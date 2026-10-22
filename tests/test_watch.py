"""The worldwide watch list (watch.py), 2026-10-22. Offline: a fake session
stands in for aiohttp; no hex here is a real aircraft except the three
presidential airframes, which are published facts."""
import asyncio
import unittest

from _load import load

watch = load("watch")
adsb = load("sources.adsb")


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


def wl(law, clock=None, backoff=None):
    c = clock or Clock()
    return watch.WatchList(lambda: law, backoff=backoff or adsb.Backoff(clock=c, wall=c), clock=c), c


class Lists(unittest.TestCase):
    def test_presidential_first_no_duplicates(self):
        w, _ = wl(["A00002", "a00001", "AF83F3"])
        self.assertEqual(w.hexes(), ["adfdf8", "adfdf9", "af83f3", "a00001", "a00002"])
        self.assertEqual(watch.WatchList.why("af83f3"), "presidential")
        self.assertEqual(watch.WatchList.why("a00001"), "law_enforcement")

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
        s = Session([Resp(200, answer("a00001", "adfdf8"))])
        self.assertTrue(w.due())
        self.run_(w, s)
        self.assertEqual(len(s.urls), 1)
        self.assertTrue(s.urls[0].startswith("https://opendata.adsb.fi/api/v2/icao/ADFDF8,ADFDF9,AF83F3,A00001"))
        self.assertEqual(sorted(o.identity for o in w.observations()), ["a00001", "adfdf8"])
        self.assertEqual(w.status, "ok")
        self.assertFalse(w.due())
        c.t += watch.INTERVAL_S
        self.assertTrue(w.due())

    def test_two_chunks_both_read(self):
        law = ["a%05x" % i for i in range(1000)]
        w, _ = wl(law)
        s = Session([Resp(200, answer("a00001")), Resp(200, answer("a003e7"))])
        orig = watch._sleep

        async def nosleep(_s):
            return None
        watch._sleep = nosleep
        try:
            self.run_(w, s)
        finally:
            watch._sleep = orig
        self.assertEqual(len(s.urls), 2)
        self.assertEqual(sorted(o.identity for o in w.observations()), ["a00001", "a003e7"])

    def test_failure_keeps_the_last_answer_until_stale(self):
        w, c = wl(["a00001"])
        self.run_(w, Session([Resp(200, answer("a00001"))]))
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


if __name__ == "__main__":
    unittest.main()
