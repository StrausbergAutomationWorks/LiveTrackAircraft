"""The worldwide watch (watch.py) on the shared poll, backlog 297. Offline: a fake session stands in
for aiohttp; no hex here is a real aircraft except the three presidential airframes, which are
published facts."""
import asyncio
import unittest

import json

from _load import load, source

watch = load("watch")
areas_mod = load("areas")
from saw_livetrack import adsb_poll as ap  # noqa: E402


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


class Resp:
    def __init__(self, status, payload=None, headers=None):
        self.status, self._p, self.headers = status, payload, headers or {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def json(self, content_type=None):
        return self._p


class Session:
    def __init__(self, answers):
        self.answers, self.urls = list(answers), []

    def get(self, url, **kw):
        self.urls.append(url)
        return self.answers.pop(0)


def rec(h, **kw):
    r = {"hex": h, "lat": 30.0, "lon": -97.0, "alt_baro": 1200, "seen_pos": 1.0, "flight": "N1TX "}
    r.update(kw)
    return r


def answer(*hexes):
    return {"ac": [rec(h) for h in hexes], "now": 1789000000000}


def mil(*recs):
    return {"ac": list(recs), "now": 1789000000000}


def wl():
    c = Clock()

    async def nosleep(s):
        c.t += s

    poll = ap.Poll(clock=c, sleep=nosleep)
    return watch.WatchList(poll, clock=c), poll, c


def run(w, session):
    asyncio.run(w.async_fetch(session, 1789000000.0))


class Lists(unittest.TestCase):
    def test_presidential_only(self):
        w, poll, _ = wl()
        self.assertEqual(w.hexes(), ["adfdf8", "adfdf9", "af83f3"])
        self.assertEqual(poll.union(), ["adfdf8", "adfdf9", "af83f3"])
        self.assertEqual(w.why("af83f3"), "presidential")
        self.assertEqual(set(watch.PRESIDENTIAL), {"adfdf8", "adfdf9", "af83f3"})

    def test_the_nationwide_enforcement_watch_moved_out(self):
        self.assertNotIn("law_enforcement", source("watch.py").split('"""', 2)[2])
        # Lee 2026-11-02 22:59: adsb.lol only for the military list, after adsb.fi (the hex round's is the library's)
        self.assertEqual([n for n, _ in watch.MIL_SOURCES], [ap.FI, ap.LOL])
        # backlog 332: the call-sign round is the second, also after adsb.fi
        self.assertEqual([n for n, _ in watch.CALLSIGN_SOURCES], [ap.FI, ap.LOL])
        self.assertEqual(source("watch.py").count("api.adsb.lol"), 2)

    def test_the_companions_hexes_join_one_union_round(self):
        w, poll, _ = wl()
        poll.set_hexes("live_track_enforcement_aircraft", ["a00808", "adfdf8"])
        s = Session([Resp(200, answer("a00808", "adfdf8")), Resp(200, mil())])
        run(w, s)
        self.assertEqual(len(s.urls), 2)
        self.assertTrue(s.urls[0].endswith("/v2/icao/A00808,ADFDF8,ADFDF9,AF83F3"))
        self.assertEqual([o.identity for o in w.observations()], ["adfdf8"])   # its own hexes only
        self.assertEqual([o.identity for o in poll.hex_observations("live_track_enforcement_aircraft")],
                         ["a00808", "adfdf8"])


class Fetch(unittest.TestCase):
    def test_one_round(self):
        w, poll, c = wl()
        s = Session([Resp(200, answer("adfdf8")), Resp(200, mil())])
        self.assertTrue(w.due())
        run(w, s)
        self.assertEqual(s.urls[1], "https://opendata.adsb.fi/api/v2/mil")
        self.assertEqual([o.identity for o in w.observations()], ["adfdf8"])
        self.assertEqual(w.status, "ok")
        self.assertFalse(w.due())
        c.t += watch.INTERVAL_S
        self.assertTrue(w.due())

    def test_failure_keeps_the_last_answer_until_stale(self):
        w, poll, c = wl()
        run(w, Session([Resp(200, answer("adfdf8")), Resp(200, mil())]))
        c.t += watch.INTERVAL_S
        run(w, Session([Resp(503)]))
        self.assertTrue(w.status.startswith("failed"))
        self.assertEqual(len(w.observations()), 1)
        c.t += watch.STALE_S
        self.assertEqual(w.observations(), [])

    def test_429_backs_the_circle_off_too(self):
        w, poll, c = wl()
        run(w, Session([Resp(429, headers={"Retry-After": "300"}), Resp(200, answer())]))
        self.assertIsNotNone(poll.backoff.remaining("adsb.fi"))
        c.t += watch.INTERVAL_S
        s = Session([Resp(200, answer("adfdf8")), Resp(200, mil())])
        run(w, s)                      # still backing off: adsb.fi not asked; adsb.lol answers the round and the list
        self.assertEqual(s.urls, ["https://api.adsb.lol/v2/hex/ADFDF8,ADFDF9,AF83F3", "https://api.adsb.lol/v2/mil"])
        self.assertEqual([o.identity for o in w.observations()], ["adfdf8"])
        self.assertEqual(w.status, "ok from adsb.lol: adsb.fi backing off")


class Military(unittest.TestCase):
    AF1 = rec("adfdf8", lat=38.80, lon=-76.90, flight="AF1")

    def round_(self, mil_payload, icao=(), status=200):
        w, _, _ = wl()
        s = Session([Resp(200, answer(*icao)), Resp(status, mil_payload)])
        run(w, s)
        return w, {o.identity: w.why(o.identity) for o in w.observations()}

    def test_the_wing_always(self):
        w, got = self.round_(mil(rec("ae0123", flight="SAM44"), rec("ae0456", flight="VENUS02"),
                                 rec("7cf9e7", flight="SAMB2"),          # RAAF PC-21, 2026-10-21
                                 rec("4b7001", flight="SAM12"),          # not a US military hex
                                 rec("ae0789", flight="RCH123"),
                                 rec("ae0999", flight="SAMX7")))          # US hex, not SAM + digits
        self.assertEqual(got["ae0123"], "89aw")
        self.assertEqual(got["ae0456"], "89aw")
        for h in ("7cf9e7", "4b7001", "ae0789", "ae0999"):
            self.assertNotIn(h, got)

    def test_escorts_only_near_a_presidential_airframe(self):
        near = rec("ae1111", lat=38.80, lon=-76.80, flight="BOLT1")    # 8.7 km
        far = rec("ae2222", lat=38.80, lon=-76.60, flight="BOLT2")     # 26 km
        _, got = self.round_(mil(self.AF1, near, far))
        self.assertEqual(got.get("adfdf8"), "presidential")
        self.assertEqual(got.get("ae1111"), "escort")
        self.assertNotIn("ae2222", got)
        _, got = self.round_(mil(near))                                # no AF1 in view
        self.assertNotIn("ae1111", got)

    def test_escort_of_af1_found_by_hex_request(self):
        near = rec("ae1111", lat=38.80, lon=-76.80, flight="BOLT1")
        w, _, _ = wl()
        s = Session([Resp(200, {"ac": [self.AF1], "now": 1789000000000}), Resp(200, mil(near))])
        run(w, s)
        self.assertEqual(w.why("ae1111"), "escort")

    def test_distance(self):
        self.assertAlmostEqual(watch.ESCORT_KM, 10 * 1.852, places=2)

    def test_military_list_failure_keeps_the_hexes(self):
        w, got = self.round_(None, icao=("adfdf8",), status=503)
        self.assertEqual(list(got), ["adfdf8"])
        self.assertTrue(w.status.startswith("military list"))


class MilitaryFallback(unittest.TestCase):
    """Lee 2026-11-02 22:59: adsb.fi then adsb.lol, as the hex round."""
    WING = rec("ae0123", flight="SAM44")

    def test_adsb_lol_answers_when_adsb_fi_fails(self):
        w, _, _ = wl()
        s = Session([Resp(200, answer()), Resp(503), Resp(200, mil(self.WING))])
        run(w, s)
        self.assertEqual(s.urls[1:], ["https://opendata.adsb.fi/api/v2/mil", "https://api.adsb.lol/v2/mil"])
        self.assertEqual(w.why("ae0123"), "89aw")
        self.assertEqual(w.status, "ok, military list from adsb.lol")

    def test_adsb_lol_is_not_asked_while_adsb_fi_answers(self):
        w, _, c = wl()
        for _ in range(3):
            s = Session([Resp(200, answer()), Resp(200, mil(self.WING))])
            run(w, s)
            self.assertFalse(any("adsb.lol" in u for u in s.urls))
            self.assertEqual(w.status, "ok")
            c.t += watch.INTERVAL_S

    def test_inside_adsb_fis_window_it_is_not_asked(self):
        w, poll, _ = wl()
        poll.backoff.refused(ap.FI, 300.0)
        s = Session([Resp(200, answer()), Resp(200, mil(self.WING))])
        run(w, s)
        self.assertEqual(s.urls[1], "https://api.adsb.lol/v2/mil")
        self.assertFalse(any("adsb.fi" in u for u in s.urls))
        self.assertEqual(w.why("ae0123"), "89aw")
        self.assertEqual(w.status, "ok from adsb.lol: adsb.fi backing off")   # the hex round's status, the more telling

    def test_both_failing_says_both_and_keeps_the_last_answer(self):
        w, _, c = wl()
        run(w, Session([Resp(200, answer()), Resp(200, mil(self.WING))]))
        c.t += watch.INTERVAL_S
        run(w, Session([Resp(200, answer()), Resp(503), Resp(502)]))
        self.assertIn("adsb.fi returned HTTP 503", w.status)
        self.assertIn("adsb.lol returned HTTP 502", w.status)
        self.assertTrue(w.status.startswith("military list: "))
        self.assertEqual([o.identity for o in w.observations()], ["ae0123"])


class Areas(unittest.TestCase):
    """Lee 2026-11-02 22:59: every military-flagged aircraft inside the named circles, from the same request."""
    HOME = areas_mod.Area(39.81, -84.04, 150.0)
    SOCAL = areas_mod.Area(34.0, -117.8, 463.0)
    NEAR = rec("ae0001", lat=39.82, lon=-84.06, flight="RCH1")
    FAR = rec("ae0002", lat=42.92, lon=-84.06, flight="RCH2")          # 346 km north of HOME
    SD = rec("ae0003", lat=32.70, lon=-117.40, flight="SHWK425")       # 149 km from SOCAL's centre

    def fetched(self, *recs):
        w, _, c = wl()
        run(w, Session([Resp(200, answer()), Resp(200, mil(*recs))]))
        return w, c

    def test_any_military_aircraft_inside_each_counted(self):
        w, _ = self.fetched(self.NEAR, self.FAR, self.SD)
        found, counts = w.in_areas([self.HOME, self.SOCAL])
        self.assertEqual(sorted(o.identity for o in found), ["ae0001", "ae0003"])
        self.assertEqual(counts, [1, 1])

    def test_not_only_the_wing(self):
        w, _ = self.fetched(self.NEAR)
        self.assertEqual(w.why("ae0001"), "watched")
        self.assertEqual(w.observations(), [])                  # not watched worldwide: only inside an area
        self.assertEqual(len(w.in_areas([self.HOME])[0]), 1)

    def test_in_two_circles_listed_once_counted_in_each(self):
        w, _ = self.fetched(self.NEAR)
        wide = areas_mod.Area(38.92, -84.06, 300.0)
        found, counts = w.in_areas([self.HOME, wide])
        self.assertEqual(len(found), 1)
        self.assertEqual(counts, [1, 1])

    def test_the_edge_is_inside(self):
        w, _ = self.fetched(self.NEAR)
        km = ap.km_between(39.81, -84.04, 39.82, -84.06)
        self.assertEqual(w.in_areas([areas_mod.Area(39.81, -84.04, km)])[1], [1])
        self.assertEqual(w.in_areas([areas_mod.Area(39.81, -84.04, km - 0.001)])[1], [0])

    def test_no_areas_nothing(self):
        w, _ = self.fetched(self.NEAR)
        self.assertEqual(w.in_areas([]), ([], []))

    def test_a_ground_or_positionless_record_is_not_counted(self):
        w, _ = self.fetched(rec("ae0004", lat=39.82, lon=-84.06, alt_baro="ground"), {"hex": "ae0005", "flight": "X"})
        self.assertEqual(w.in_areas([self.HOME]), ([], [0]))

    def test_nothing_before_a_list_and_nothing_once_stale(self):
        w, _, c = wl()
        self.assertEqual(w.in_areas([self.HOME]), ([], [0]))
        run(w, Session([Resp(200, answer()), Resp(200, mil(self.NEAR))]))
        w._mil_at = 2000.0
        c.t = 2000.0 + watch.STALE_S
        self.assertEqual(len(w.in_areas([self.HOME])[0]), 1)     # at the limit, still drawn
        c.t += 1
        self.assertEqual(w.in_areas([self.HOME]), ([], [0]))

    def test_a_failed_list_keeps_the_last_until_stale(self):
        w, _, c = wl()
        run(w, Session([Resp(200, answer()), Resp(200, mil(self.NEAR))]))
        c.t += watch.INTERVAL_S
        run(w, Session([Resp(200, answer()), Resp(503), Resp(503)]))
        self.assertEqual(len(w.in_areas([self.HOME])[0]), 1)

    def test_the_fallback_feeds_the_areas(self):
        w, _, _ = wl()
        run(w, Session([Resp(200, answer()), Resp(503), Resp(200, mil(self.NEAR))]))
        self.assertEqual(len(w.in_areas([self.HOME])[0]), 1)

    def test_a_new_list_replaces_the_old(self):
        w, _, c = wl()
        run(w, Session([Resp(200, answer()), Resp(200, mil(self.NEAR))]))
        c.t += watch.INTERVAL_S
        run(w, Session([Resp(200, answer()), Resp(200, mil(self.FAR))]))
        self.assertEqual(w.in_areas([self.HOME]), ([], [0]))


class Wiring(unittest.TestCase):
    """The coordinator and the dialog need Home Assistant, so what connects them is pinned in their source; the live check does the rest."""

    def test_the_coordinator(self):
        c = source("coordinator.py")
        self.assertIn("self.military_areas = parse_areas(opts.get(CONF_MILITARY_AREAS))[0]", c)
        self.assertIn("self.watch.in_areas(self.military_areas)", c)
        self.assertLess(c.index("apply_cap("), c.index("self.watch.in_areas("))     # after the cap, so past it
        self.assertLess(c.index("self.watch.in_areas("), c.index("for gone in [k for k in self._fix"))
        self.assertIn('aircraft[obs.identity].setdefault("watch", WHY_MILITARY_AREA)', c)
        self.assertIn('rec["watch"] = WHY_MILITARY_AREA', c)
        self.assertIn('"military_in_areas": len(military_found)', c)
        self.assertIn('"military_by_area": {area_label(a): n for a, n in zip(self.military_areas, military_counts)}', c)

    def test_the_sensor(self):
        s = source("sensor.py")
        self.assertIn('"military_in_areas": data.get("military_in_areas", 0)', s)
        self.assertIn('"military_by_area": data.get("military_by_area", {})', s)

    def test_the_dialog(self):
        f = source("config_flow.py")
        self.assertIn('description={"suggested_value": defaults.get(CONF_MILITARY_AREAS, "")}', f)
        self.assertEqual(f.count("_from_dialog(user_input)"), 2)
        self.assertIn("return None, {CONF_MILITARY_AREAS: error}", f)
        self.assertIn("values[CONF_MILITARY_AREAS] = text", f)

    def test_the_words_on_both_forms(self):
        for name in ("strings.json", "translations/en.json"):
            d = json.loads(source(name))
            for block in (d["config"]["step"]["user"], d["options"]["step"]["init"]):
                self.assertIn("military_areas", block["data"], name)
                self.assertIn("military_areas", block["data_description"], name)
            for part in ("config", "options"):
                self.assertIn("invalid_military_areas", d[part]["error"], name)


if __name__ == "__main__":
    unittest.main()
