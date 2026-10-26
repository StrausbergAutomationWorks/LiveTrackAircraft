"""Sliced state writes (slices.py, geo_location.py; 2026-10-26, from
30_Correspondence/BRIEF_burst_from_map_card_20261025.md). The default is ALL, one write of every
aircraft per poll, as before. A slice size of 25, 50 or 100 writes the first slice at once and
the rest spread across the poll interval, every aircraft once, the last before the next poll.
The size is a runtime knob, set by an event; a write carries the aircraft's record, the fix."""
import unittest

from _load import load, source

slices = load("slices")


def ids(n):
    return ["h%03d" % i for i in range(n)]


class ParseSize(unittest.TestCase):
    def test_all_forms(self):
        for v in (None, "all", "ALL", " all "):
            self.assertIs(slices.parse_size(v), slices.ALL, v)

    def test_sizes(self):
        for v, want in ((25, 25), (50, 50), (100, 100), ("25", 25), (" 50 ", 50), ("100", 100)):
            self.assertEqual(slices.parse_size(v), want, v)

    def test_rejects(self):
        for v in (0, 10, 24, 26, 99, 101, 250, -25, True, 25.0, "", "x", "25x", [25], {}):
            with self.assertRaises(ValueError, msg=repr(v)):
                slices.parse_size(v)

    def test_constants(self):
        self.assertIsNone(slices.ALL)
        self.assertEqual(slices.SIZES, (25, 50, 100))
        self.assertEqual(slices.EVENT, "live_track_aircraft_write_slice")


class Plan(unittest.TestCase):
    def check_cover(self, p, every):
        got = [i for _, part in p for i in part]
        self.assertEqual(got, every)  # every aircraft once, in the order given

    def test_all_is_one_write_now(self):
        every = ids(250)
        p = slices.plan(every, slices.ALL, 15.0)
        self.assertEqual(p, [(0.0, every)])

    def test_empty(self):
        for size in (slices.ALL, 25):
            self.assertEqual(slices.plan([], size, 15.0), [])

    def test_fits_in_one_slice(self):
        for n in (1, 24, 25):
            p = slices.plan(ids(n), 25, 15.0)
            self.assertEqual(p, [(0.0, ids(n))], n)

    def test_250_by_25(self):
        p = slices.plan(ids(250), 25, 15.0)
        self.assertEqual(len(p), 10)
        self.assertEqual([round(d, 6) for d, _ in p], [round(1.5 * k, 6) for k in range(10)])
        self.assertTrue(all(len(part) == 25 for _, part in p))
        self.check_cover(p, ids(250))

    def test_uneven_last_slice(self):
        p = slices.plan(ids(251), 25, 15.0)
        self.assertEqual(len(p), 11)
        self.assertEqual(len(p[-1][1]), 1)
        self.assertAlmostEqual(p[1][0], 15.0 / 11)
        self.check_cover(p, ids(251))

    def test_first_now_last_before_next_poll(self):
        for n in (26, 60, 199, 250, 251, 500):
            for size in slices.SIZES:
                for interval in (5.0, 10.0, 15.0, 60.0):
                    p = slices.plan(ids(n), size, interval)
                    self.assertEqual(p[0][0], 0.0)
                    self.assertLess(p[-1][0], interval, (n, size, interval))
                    self.assertEqual(sorted(d for d, _ in p), [d for d, _ in p])
                    self.check_cover(p, ids(n))
                    self.assertTrue(all(len(part) <= size for _, part in p))

    def test_no_interval_means_one_write_now(self):
        for interval in (0, 0.0, -1.0, None):
            self.assertEqual(slices.plan(ids(100), 25, interval), [(0.0, ids(100))], interval)

    def test_input_not_held(self):
        for size in (slices.ALL, 25):
            every = ids(60)
            p = slices.plan(every, size, 15.0)
            every.append("late")
            self.check_cover(p, ids(60))


class Wiring(unittest.TestCase):
    """geo_location.py: the platform writes, not each entity; ALL stays one callback."""
    src = source("geo_location.py")

    def test_entity_no_longer_writes_on_its_own(self):
        self.assertNotIn("async_add_listener(self.async_write_ha_state)", self.src)

    def test_platform_plans_the_writes(self):
        self.assertIn('for delay, part in plan(due, slicing["size"], interval):', self.src)
        self.assertIn("due = [i for i in live if i not in fresh]", self.src)

    def test_first_slice_in_the_same_callback(self):
        self.assertIn("            if delay <= 0:\n                _write(part)\n", self.src)

    def test_pending_cancelled_each_poll_and_on_unload(self):
        self.assertIn("    def _sync() -> None:\n        _cancel_pending()\n", self.src)
        self.assertIn("entry.async_on_unload(_cancel_pending)", self.src)

    def test_write_skips_gone_and_unadded(self):
        self.assertIn("entity = live.get(identity)", self.src)
        self.assertIn("if entity is not None and entity.hass is not None:", self.src)

    def test_knob_is_an_event_for_this_entry(self):
        self.assertIn("hass.bus.async_listen(SLICE_EVENT, _set_slice)", self.src)
        self.assertIn('if target is not None and target != entry.entry_id:', self.src)
        self.assertIn('slicing["size"] = size', self.src)
        self.assertIn('slicing: dict[str, int | None] = {"size": ALL}', self.src)

    def test_write_time_never_published(self):
        # observed_at and previous_* are the fix's, passed through from the record.
        self.assertNotIn("utcnow", self.src)
        self.assertNotIn("time.time", self.src)
        self.assertEqual(self.src.count('"observed_at"'), 1)
        self.assertEqual(self.src.count('"previous_observed_at"'), 1)


if __name__ == "__main__":
    unittest.main()
