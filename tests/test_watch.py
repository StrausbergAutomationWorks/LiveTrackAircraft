"""The worldwide watch (watch.py) on the shared poll, backlog 297. Offline: a fake session stands in
for aiohttp; no hex here is a real aircraft except the three presidential airframes, which are
published facts."""
import asyncio
import unittest

from _load import load, source

watch = load("watch")
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
        self.assertNotIn("api.adsb.lol", source("watch.py"))

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
        s = Session([Resp(200, answer("adfdf8"))])
        run(w, s)                      # still backing off: adsb.fi not asked; saw-livetrack 0.2.24: adsb.lol answers the round
        self.assertEqual(s.urls, ["https://api.adsb.lol/v2/hex/ADFDF8,ADFDF9,AF83F3"])
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


if __name__ == "__main__":
    unittest.main()
