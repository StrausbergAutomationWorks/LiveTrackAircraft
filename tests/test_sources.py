"""adsb.fi first, and a short answer is not a negative result.

MEASURED 2026-09-25: adsb.lol answered HTTP 200 with 38 aircraft, then 0,
where ~200 were overhead, on the edges of its 429 cycle. fetch() took each as
the truth, the platform removed every aircraft missing from it, and the next
poll put them all back - the map stopped, then jumped. Lee: adsb.fi first,
plus the short-answer guard.
"""
import asyncio
import time
import unittest

from _load import load

const = load("const")
adsb = load("sources.adsb")
base = load("sources.base")


def payload(n):
    return {"now": time.time() * 1000, "ac": [
        {"hex": "%06x" % (0xA00000 + i), "lat": 41.9, "lon": -87.9,
         "alt_baro": 10000, "seen_pos": 0.5} for i in range(n)]}


class Resp:
    def __init__(self, status, body):
        self.status, self.body, self.headers = status, body, {}

    async def json(self, content_type=None):
        return self.body

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False


class Session:
    """Scripted per source: (status, aircraft count)."""

    def __init__(self, **script):
        self.script = {"adsb.fi": script.get("fi", (200, 200)),
                       "adsb.lol": script.get("lol", (200, 200))}
        self.asked = []

    def get(self, url, headers=None, timeout=None):
        name = "adsb.lol" if "adsb.lol" in url else "adsb.fi"
        self.asked.append(name)
        status, n = self.script[name]
        return Resp(status, payload(n) if status == 200 else {})


def fetch(sess, min_expected=None):
    bo = adsb.Backoff()
    return asyncio.run(adsb.fetch(sess, 41.9, -87.9, 156, time.time(),
                                  backoff=bo, min_expected=min_expected))


class Order(unittest.TestCase):
    def test_adsb_fi_is_asked_first(self):
        self.assertEqual([n for n, _ in const.SOURCE_URLS], ["adsb.fi", "adsb.lol"])

    def test_the_shared_poll_asks_the_same_urls(self):
        # backlog 297: the circle goes through saw_livetrack.adsb_poll, which holds the URLs
        from saw_livetrack import adsb_poll as ap
        self.assertEqual(dict(const.SOURCE_URLS), {n: ap.CIRCLE_URLS[n] for n, _ in const.SOURCE_URLS})
        self.assertEqual(adsb.SOURCES, ("adsb.fi", "adsb.lol"))
        self.assertIs(base.SourceError, ap.SourceError)
        self.assertIs(base.Observation, ap.Observation)

    def test_a_full_first_answer_asks_nobody_else(self):
        s = Session()
        name, obs = fetch(s, min_expected=100)
        self.assertEqual((name, len(obs), s.asked), ("adsb.fi", 200, ["adsb.fi"]))


class ShortFloor(unittest.TestCase):
    def test_small_skies_are_never_guarded(self):
        for prev in (None, 0, 1, 19):
            self.assertIsNone(adsb.short_floor(prev))

    def test_half_of_the_last_good(self):
        self.assertEqual(adsb.short_floor(200), 100)
        self.assertEqual(adsb.short_floor(20), 10)


class Guard(unittest.TestCase):
    def test_short_answer_falls_through_to_the_next_source(self):
        s = Session(fi=(200, 38), lol=(200, 190))
        name, obs = fetch(s, min_expected=100)
        self.assertEqual((name, len(obs)), ("adsb.lol", 190))
        self.assertEqual(s.asked, ["adsb.fi", "adsb.lol"])

    def test_empty_200_is_short(self):
        s = Session(fi=(200, 0), lol=(200, 150))
        self.assertEqual(fetch(s, min_expected=100)[0], "adsb.lol")

    def test_both_short_takes_the_larger(self):
        # both sources agreeing the sky emptied is believed, the larger first
        s = Session(fi=(200, 60), lol=(200, 0))
        name, obs = fetch(s, min_expected=100)
        self.assertEqual((name, len(obs)), ("adsb.fi", 60))

    def test_short_and_a_refusal_is_a_failure_not_an_empty_sky(self):
        # one source short, the other unable to say: no answer, so the
        # coordinator serves its last good result instead of wiping the map
        for lol in ((429, 0), (503, 0)):
            with self.subTest(lol=lol):
                s = Session(fi=(200, 5), lol=lol)
                with self.assertRaises(base.SourceError) as cm:
                    fetch(s, min_expected=100)
                self.assertIn("short", str(cm.exception))

    def test_no_floor_means_any_count_is_accepted(self):
        s = Session(fi=(200, 0))
        self.assertEqual(fetch(s, min_expected=None), ("adsb.fi", []))

    def test_first_source_failing_still_falls_through(self):
        s = Session(fi=(429, 0), lol=(200, 180))
        self.assertEqual(fetch(s, min_expected=100)[0], "adsb.lol")


class Attribution(unittest.TestCase):
    def test_both_feeds_still_credited(self):
        self.assertIn("adsb.fi", const.ATTRIBUTION)
        self.assertIn("adsb.lol", const.ATTRIBUTION)


if __name__ == "__main__":
    unittest.main()
