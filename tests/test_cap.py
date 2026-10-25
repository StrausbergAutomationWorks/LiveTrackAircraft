"""The cap with listed aircraft exempt (cap.py; Lee 2026-10-25 14:14: "LTA should not drop a
listed aircraft"). The nearest max_aircraft are kept; a listed hex survives wherever it is; the
coordinator exempts sourced and detected_unconfirmed, never cleared."""
import unittest

from _load import load, source

cap = load("cap")


def ac(n, km):
    return {"identity": "h%03d" % n, "distance_km": km}


def sky(count):
    # Deliberately out of distance order, so the sort is tested.
    return {r["identity"]: r for r in (ac(i, float((i * 37) % count)) for i in range(count))}


NONE = lambda h: False


class Cap(unittest.TestCase):
    def test_under_the_cap_untouched(self):
        a = sky(5)
        kept, capped, ex = cap.apply_cap(a, 5, NONE)
        self.assertIs(kept, a)
        self.assertEqual((capped, ex), (False, 0))

    def test_nearest_kept_when_it_bites(self):
        kept, capped, ex = cap.apply_cap(sky(10), 3, NONE)
        self.assertTrue(capped)
        self.assertEqual(ex, 0)
        self.assertEqual(sorted(r["distance_km"] for r in kept.values()), [0.0, 1.0, 2.0])

    def test_listed_beyond_the_cap_kept(self):
        a = sky(10)
        far = max(a.values(), key=lambda r: r["distance_km"])["identity"]
        kept, capped, ex = cap.apply_cap(a, 3, lambda h: h == far)
        self.assertTrue(capped)
        self.assertEqual(ex, 1)
        self.assertEqual(len(kept), 4)
        self.assertIn(far, kept)

    def test_listed_inside_the_cap_not_counted_twice(self):
        a = sky(10)
        near = min(a.values(), key=lambda r: r["distance_km"])["identity"]
        kept, _, ex = cap.apply_cap(a, 3, lambda h: h == near)
        self.assertEqual((len(kept), ex), (3, 0))

    def test_every_listed_kept(self):
        kept, _, ex = cap.apply_cap(sky(20), 2, lambda h: True)
        self.assertEqual((len(kept), ex), (20, 18))


class CoordinatorWiring(unittest.TestCase):
    """The coordinator exempts sourced and detected, not cleared, and reports the count."""
    src = source("coordinator.py")

    def test_statuses(self):
        self.assertIn("elist.status(h) in (SOURCED, DETECTED)", self.src)
        self.assertNotIn("CLEARED", self.src)

    def test_cap_goes_through_apply_cap(self):
        self.assertIn("apply_cap(aircraft, self.max_aircraft, listed)", self.src)
        self.assertNotIn("nearest[: self.max_aircraft]", self.src)

    def test_count_published(self):
        self.assertIn('"listed_over_cap": listed_over_cap', self.src)
        self.assertIn('"listed_over_cap": data.get("listed_over_cap", 0)', source("sensor.py"))


if __name__ == "__main__":
    unittest.main()
