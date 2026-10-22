"""The worldwide watch list (watch.py), 2026-10-22. Offline: a fake session
stands in for aiohttp; no hex here is a real aircraft except the three
presidential airframes, which are published facts."""
import asyncio
import unittest

from _load import load

watch = load("watch")
adsb = load("sources.adsb")


async def _nosleep(_s):
    return None


watch._sleep = _nosleep


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


NOMIL = Resp(200, mil())


def wl(law, clock=None, backoff=None):
    c = clock or Clock()
    return watch.WatchList(lambda: law, backoff=backoff or adsb.Backoff(clock=c, wall=c), clock=c), c


class Lists(unittest.TestCase):
    def test_presidential_first_no_duplicates(self):
        w, _ = wl(["A00002", "a00001", "AF83F3"])
        self.assertEqual(w.hexes(), ["adfdf8", "adfdf9", "af83f3", "a00001", "a00002"])
        self.assertEqual(w.why("af83f3"), "presidential")
        self.assertEqual(w.why("a00001"), "law_enforcement")

    def test_chunks_at_the_measured_size(self):
        self.assertEqual(watch.MAX_PER_REQUEST, 994)
        parts = watch.chunks([str(i) for i in range(2000)])
        self.assertEqual([len(p) for p in parts], [994, 994, 12])

    def test_trainer_and_bridge(self):
        self.assertEqual(set(watch.PRESIDENTIAL), {"adfdf8", "adfdf9", "af83f3"})


class Fetch(unittest.TestCase):
    def run_(self, w, session):
        asyncio.run(w.async_fetch(session, 1789000000.0))

    def test_one_round(self):
        w, c = wl(["a00001"])
        s = Session([Resp(200, answer("a00001", "adfdf8")), Resp(200, mil())])
        self.assertTrue(w.due())
        self.run_(w, s)
        self.assertEqual(len(s.urls), 2)
        self.assertEqual(s.urls[1], "https://opendata.adsb.fi/api/v2/mil")
        self.assertTrue(s.urls[0].startswith("https://opendata.adsb.fi/api/v2/icao/ADFDF8,ADFDF9,AF83F3,A00001"))
        self.assertEqual(sorted(o.identity for o in w.observations()), ["a00001", "adfdf8"])
        self.assertEqual(w.status, "ok")
        self.assertFalse(w.due())
        c.t += watch.INTERVAL_S
        self.assertTrue(w.due())

    def test_two_chunks_both_read(self):
        law = ["a%05x" % i for i in range(1000)]
        w, _ = wl(law)
        s = Session([Resp(200, answer("a00001")), Resp(200, answer("a003e7")), Resp(200, mil())])
        self.run_(w, s)
        self.assertEqual(len(s.urls), 3)
        self.assertEqual(sorted(o.identity for o in w.observations()), ["a00001", "a003e7"])

    def test_failure_keeps_the_last_answer_until_stale(self):
        w, c = wl(["a00001"])
        self.run_(w, Session([Resp(200, answer("a00001")), Resp(200, mil())]))
        c.t += watch.INTERVAL_S
        self.run_(w, Session([Resp(503)]))
        self.assertEqual(w.status, "HTTP 503")
        self.assertEqual(len(w.observations()), 1)
        c.t += watch.STALE_S
        self.assertEqual(w.observations(), [])

    def test_429_backs_the_circle_off_too(self):
        c = Clock()
        b = adsb.Backoff(clock=c, wall=c)
        w, _ = wl(["a00001"], clock=c, backoff=b)
        self.run_(w, Session([Resp(429, headers={"Retry-After": "300"})]))
        self.assertIsNotNone(b.remaining("adsb.fi"))
        c.t += watch.INTERVAL_S
        s = Session([])
        self.run_(w, s)                      # still backing off: not asked
        self.assertEqual(s.urls, [])
        self.assertTrue(w.status.startswith("waiting"))


class Military(unittest.TestCase):
    AF1 = rec("adfdf8", lat=38.80, lon=-76.90, flight="AF1")

    def round_(self, mil_payload, icao=("a00001",), status=200):
        w, _ = wl(["a00001"])
        s = Session([Resp(200, answer(*icao)), Resp(status, mil_payload)])
        asyncio.run(w.async_fetch(s, 1789000000.0))
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
        w, _ = wl(["a00001"])
        s = Session([Resp(200, {"ac": [self.AF1], "now": 1789000000000}), Resp(200, mil(near))])
        asyncio.run(w.async_fetch(s, 1789000000.0))
        self.assertEqual(w.why("ae1111"), "escort")

    def test_distance(self):
        self.assertAlmostEqual(watch.ESCORT_KM, 10 * 1.852, places=2)

    def test_military_list_failure_keeps_the_hexes(self):
        w, got = self.round_(None, status=503)
        self.assertEqual(list(got), ["a00001"])
        self.assertEqual(w.status, "military list HTTP 503")


if __name__ == "__main__":
    unittest.main()
