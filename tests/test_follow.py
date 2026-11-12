"""A user's own watch list (follow.py, watch.py's call-sign round; backlog 332). Offline: a fake session stands in
for aiohttp, as in test_watch.py. No hex or call sign here is a real aircraft or flight being followed."""
import asyncio
import json
import unittest

from _load import load, source

follow = load("follow")
watch = load("watch")
from saw_livetrack import adsb_poll as ap  # noqa: E402

from test_watch import Clock, Resp, Session, mil, rec  # noqa: E402

E1, E2 = "live_track_aircraft/entry1", "live_track_aircraft/entry2"


def wl():
    c = Clock()

    async def nosleep(s):
        c.t += s

    poll = ap.Poll(clock=c, sleep=nosleep)
    return watch.WatchList(poll, clock=c), poll, c


def run(w, session):
    asyncio.run(w.async_fetch(session, 1789000000.0))


def ac(*recs):
    return {"ac": list(recs), "now": 1789000000000}


class ParseHexes(unittest.TestCase):
    def test_lower_case_each_once_in_order(self):
        self.assertEqual(follow.parse_hexes(" A00808, a1b2c3;A00808\n0d0e0f "),
                         (["a00808", "a1b2c3", "0d0e0f"], None))

    def test_nothing_is_none(self):
        for text in (None, "", "  ", ",", " ; , "):
            self.assertEqual(follow.parse_hexes(text), ([], None), repr(text))

    def test_refused(self):
        for text in ("a0080", "a008088", "g00808", "~a00808", "a00808, UAL1234", "a0-808", "0xa00808"):
            self.assertEqual(follow.parse_hexes(text), ([], follow.ERROR_INVALID_HEXES), text)

    def test_at_most_100(self):
        ok = ",".join("%06x" % i for i in range(100))
        self.assertEqual(len(follow.parse_hexes(ok)[0]), 100)
        self.assertEqual(follow.parse_hexes(",".join("%06x" % i for i in range(101))),
                         ([], follow.ERROR_INVALID_HEXES))

    def test_repeats_do_not_count_against_the_limit(self):
        self.assertEqual(follow.parse_hexes(",".join(["a00808"] * 150)), (["a00808"], None))


class ParseCallsigns(unittest.TestCase):
    def test_upper_case_each_once_in_order(self):
        self.assertEqual(follow.parse_callsigns("ual1234, DAL89 ual1234;n1"), (["UAL1234", "DAL89", "N1"], None))

    def test_a_hex_looking_call_sign_is_a_call_sign_here(self):
        self.assertEqual(follow.parse_callsigns("ACA123"), (["ACA123"], None))

    def test_nothing_is_none(self):
        for text in (None, "", " , "):
            self.assertEqual(follow.parse_callsigns(text), ([], None), repr(text))

    def test_refused(self):
        for text in ("U", "UAL123456", "UAL-123", "UAL_1", "18-21015", "ÜAL1"):
            self.assertEqual(follow.parse_callsigns(text), ([], follow.ERROR_INVALID_CALLSIGNS), text)

    def test_the_limits_are_inside(self):
        self.assertEqual(follow.parse_callsigns("AB, ABCDEFGH")[1], None)
        self.assertEqual(len(follow.parse_callsigns(",".join("X%d" % i for i in range(100)))[0]), 100)
        self.assertEqual(follow.parse_callsigns(",".join("X%d" % i for i in range(101))),
                         ([], follow.ERROR_INVALID_CALLSIGNS))


class HexesJoinTheUnionRound(unittest.TestCase):
    """Followed hexes cost no request: they go in the same /v2/icao/ request as the presidential airframes."""

    def test_one_request_for_the_presidents_and_the_entry(self):
        w, poll, _ = wl()
        poll.set_hexes(E1, ["a00808"])
        s = Session([Resp(200, ac(rec("a00808"), rec("adfdf8"))), Resp(200, mil())])
        run(w, s)
        self.assertEqual(len(s.urls), 2)                                  # the hex round and the military list only
        self.assertTrue(s.urls[0].endswith("/v2/icao/A00808,ADFDF8,ADFDF9,AF83F3"))
        self.assertEqual([o.identity for o in poll.hex_observations(E1)], ["a00808"])
        self.assertEqual([o.identity for o in w.observations()], ["adfdf8"])   # the watch's own stay its own

    def test_released_on_unload(self):
        w, poll, _ = wl()
        poll.set_hexes(E1, ["a00808"])
        poll.release(E1)
        self.assertEqual(poll.union(), ["adfdf8", "adfdf9", "af83f3"])


class CallsignRound(unittest.TestCase):
    def test_none_followed_no_request(self):
        w, _, _ = wl()
        s = Session([Resp(200, ac()), Resp(200, mil())])
        run(w, s)
        self.assertEqual(len(s.urls), 2)
        self.assertEqual(w.callsign_status, "idle")

    def test_one_request_for_every_entrys_call_signs(self):
        w, _, _ = wl()
        w.set_callsigns(E1, ["UAL1234", "DAL89"])
        w.set_callsigns(E2, ["DAL89", "BAW21"])
        s = Session([Resp(200, ac()), Resp(200, mil()),
                     Resp(200, ac(rec("a00001", flight="UAL1234 "), rec("a00002", flight="BAW21"),
                                  rec("a00003", flight="SWA1")))])
        run(w, s)
        self.assertEqual(s.urls[2], "https://opendata.adsb.fi/api/v2/callsign/BAW21,DAL89,UAL1234")
        self.assertEqual(len(s.urls), 3)
        self.assertEqual(w.callsign_status, "ok")
        self.assertEqual([o.identity for o in w.callsign_observations(["UAL1234", "DAL89"])], ["a00001"])
        self.assertEqual([o.identity for o in w.callsign_observations(["baw21"])], ["a00002"])
        self.assertEqual(w.callsign_observations(["SWA1"]), [])        # in the answer, but nobody asked

    def test_two_aircraft_on_one_call_sign_both(self):
        w, _, _ = wl()
        w.set_callsigns(E1, ["UAL1234"])
        run(w, Session([Resp(200, ac()), Resp(200, mil()),
                        Resp(200, ac(rec("a00001", flight="UAL1234"), rec("a00009", flight="UAL1234")))]))
        self.assertEqual(sorted(o.identity for o in w.callsign_observations(["UAL1234"])), ["a00001", "a00009"])

    def test_chunked(self):
        w, _, _ = wl()
        w.set_callsigns(E1, ["X%03d" % i for i in range(watch.CALLSIGNS_PER_REQUEST + 1)])
        s = Session([Resp(200, ac()), Resp(200, mil()), Resp(200, ac()), Resp(200, ac())])
        run(w, s)
        self.assertEqual(len(s.urls), 4)
        self.assertEqual(s.urls[3], "https://opendata.adsb.fi/api/v2/callsign/X100")

    def test_adsb_lol_when_adsb_fi_fails(self):
        w, _, _ = wl()
        w.set_callsigns(E1, ["UAL1234"])
        s = Session([Resp(200, ac()), Resp(200, mil()), Resp(503),
                     Resp(200, ac(rec("a00001", flight="UAL1234")))])
        run(w, s)
        self.assertEqual(s.urls[3], "https://api.adsb.lol/v2/callsign/UAL1234")
        self.assertEqual(len(w.callsign_observations(["UAL1234"])), 1)
        self.assertTrue(w.callsign_status.startswith("ok from adsb.lol: "), w.callsign_status)

    def test_runs_when_the_military_list_failed(self):
        w, _, _ = wl()
        w.set_callsigns(E1, ["UAL1234"])
        s = Session([Resp(200, ac()), Resp(503), Resp(503), Resp(200, ac(rec("a00001", flight="UAL1234")))])
        run(w, s)
        self.assertEqual(len(w.callsign_observations(["UAL1234"])), 1)
        self.assertTrue(w.status.startswith("military list: "))           # the watch's status is unchanged by it

    def test_both_failing_keeps_the_last_answer_until_stale_and_says_so(self):
        w, _, c = wl()
        w.set_callsigns(E1, ["UAL1234"])
        run(w, Session([Resp(200, ac()), Resp(200, mil()), Resp(200, ac(rec("a00001", flight="UAL1234")))]))
        c.t += watch.INTERVAL_S
        run(w, Session([Resp(200, ac()), Resp(200, mil()), Resp(503), Resp(502)]))
        self.assertTrue(w.callsign_status.startswith("failed: "))
        self.assertIn("adsb.fi returned HTTP 503", w.callsign_status)
        self.assertIn("adsb.lol returned HTTP 502", w.callsign_status)
        self.assertEqual(len(w.callsign_observations(["UAL1234"])), 1)
        w._cs_at = c.t - watch.STALE_S
        self.assertEqual(len(w.callsign_observations(["UAL1234"])), 1)    # at the limit, still drawn
        w._cs_at -= 1
        self.assertEqual(w.callsign_observations(["UAL1234"]), [])

    def test_once_a_minute(self):
        w, _, c = wl()
        w.set_callsigns(E1, ["UAL1234"])
        run(w, Session([Resp(200, ac()), Resp(200, mil()), Resp(200, ac())]))
        s = Session([])
        run(w, s)                                                          # not due: nothing asked
        self.assertEqual(s.urls, [])

    def test_release_and_an_empty_list_remove_the_entry(self):
        w, _, _ = wl()
        w.set_callsigns(E1, ["UAL1234"])
        w.set_callsigns(E2, ["DAL89"])
        w.release(E1)
        self.assertEqual(w.callsign_union(), ["DAL89"])
        w.set_callsigns(E2, [])
        self.assertEqual(w.callsign_union(), [])

    def test_nobody_left_forgets_the_answer(self):
        w, _, c = wl()
        w.set_callsigns(E1, ["UAL1234"])
        run(w, Session([Resp(200, ac()), Resp(200, mil()), Resp(200, ac(rec("a00001", flight="UAL1234")))]))
        w.release(E1)
        c.t += watch.INTERVAL_S
        run(w, Session([Resp(200, ac()), Resp(200, mil())]))
        self.assertEqual(w.callsign_status, "idle")
        self.assertEqual(w.callsign_observations(["UAL1234"]), [])


class Wiring(unittest.TestCase):
    """The coordinator and the dialog need Home Assistant, so what connects them is pinned in source; the live check
    does the rest."""

    def test_the_coordinator(self):
        c = source("coordinator.py")
        self.assertIn("self.follow_hexes = parse_hexes(opts.get(CONF_FOLLOW_HEXES))[0]", c)
        self.assertIn("self.follow_callsigns = parse_callsigns(opts.get(CONF_FOLLOW_CALLSIGNS))[0]", c)
        # named before the round, so they are in it
        self.assertLess(c.index("self.poll.set_hexes(self.claim_key, self.follow_hexes)"),
                        c.index("await self.watch.async_fetch("))
        self.assertLess(c.index("self.watch.set_callsigns(self.claim_key, self.follow_callsigns)"),
                        c.index("await self.watch.async_fetch("))
        # drawn after the cap, so past it, and before the forgetting and the claim
        self.assertLess(c.index("apply_cap("), c.index("self.poll.hex_observations(self.claim_key)"))
        self.assertLess(c.index("self.watch.callsign_observations(self.follow_callsigns)"),
                        c.index("for gone in [k for k in self._fix"))
        self.assertLess(c.index("for gone in [k for k in self._fix"), c.index("self.poll.claim(self.claim_key"))
        self.assertIn('aircraft[obs.identity].setdefault("watch", WHY_FOLLOWED)', c)
        self.assertIn('rec["watch"] = WHY_FOLLOWED', c)
        self.assertIn('"followed_found": len(followed)', c)
        self.assertEqual(watch.WHY_FOLLOWED, "followed")

    def test_unload_releases_the_call_signs(self):
        self.assertIn("watch.release(coordinator.claim_key)", source("__init__.py"))

    def test_the_entity_publishes_why(self):
        g = source("geo_location.py")
        self.assertIn('"watch",', g)
        self.assertIn('"outside_radius",', g)

    def test_the_sensor(self):
        s = source("sensor.py")
        for key in ("followed_asked", "followed_found", "follow_status"):
            self.assertIn('"%s": data.get("%s"' % (key, key), s)

    def test_the_dialog(self):
        f = source("config_flow.py")
        for key in ("CONF_FOLLOW_HEXES", "CONF_FOLLOW_CALLSIGNS"):
            self.assertIn('description={"suggested_value": defaults.get(%s, "")}' % key, f)
        self.assertIn("(CONF_FOLLOW_HEXES, parse_hexes), (CONF_FOLLOW_CALLSIGNS, parse_callsigns)", f)
        self.assertIn("return None, {key: error}", f)

    def test_the_words_on_both_forms(self):
        self.assertEqual(source("strings.json"), source("translations/en.json"))
        d = json.loads(source("strings.json"))
        for block in (d["config"]["step"]["user"], d["options"]["step"]["init"]):
            for key in ("follow_hexes", "follow_callsigns"):
                self.assertIn(key, block["data"])
                self.assertIn(key, block["data_description"])
        for part in ("config", "options"):
            for err in (follow.ERROR_INVALID_HEXES, follow.ERROR_INVALID_CALLSIGNS):
                self.assertIn(err, d[part]["error"])


if __name__ == "__main__":
    unittest.main()
