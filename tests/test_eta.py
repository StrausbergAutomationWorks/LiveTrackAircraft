"""Estimated arrival (eta.py): Flights Above's method, keyed on the ADS-B
emitter category, and its wiring into the record (Lee, 2026-10-03)."""
import ast
import math
import unittest

from _load import load, source

eta = load("eta")

ORD = {"destination_lat": 41.9786, "destination_lon": -87.9048}
T0 = 1_791_000_000


def km_east(lat, km):
    """A longitude offset that puts a point `km` east along a parallel."""
    return km / (111.32 * math.cos(math.radians(lat)))


class Estimate(unittest.TestCase):
    def at_distance(self, km):
        return ORD["destination_lat"], ORD["destination_lon"] + km_east(ORD["destination_lat"], km)

    def test_cruise_speed_is_used_live(self):
        lat, lon = self.at_distance(830)
        got = eta.estimated_arrival(ORD, lat, lon, 830.0, "A3", T0)
        self.assertAlmostEqual(got - T0, 3600, delta=15)

    def test_below_the_floor_the_class_cruise_is_used(self):
        # Descending at 300 km/h, 100 km out, an A3: 100 / 830 h, not 100 / 300.
        lat, lon = self.at_distance(100)
        got = eta.estimated_arrival(ORD, lat, lon, 300.0, "A3", T0)
        self.assertAlmostEqual(got - T0, 100 / 830 * 3600, delta=5)

    def test_floor_is_inclusive(self):
        lat, lon = self.at_distance(500)
        self.assertAlmostEqual(eta.estimated_arrival(ORD, lat, lon, 500.0, "A3", T0) - T0,
                               3600, delta=10)

    def test_each_class_and_unknown(self):
        for cat, kmh in (("A1", 240), ("A2", 700), ("A3", 830), ("A4", 830),
                         ("A5", 900), ("A6", 900), ("A7", 220)):
            self.assertEqual(eta.cruise_kmh(cat), kmh, cat)
        self.assertEqual(eta.cruise_kmh(" a5 "), 900)
        for cat in (None, "", "B1", "C3"):
            self.assertEqual(eta.cruise_kmh(cat), 820, cat)

    def test_no_speed_uses_the_class(self):
        lat, lon = self.at_distance(240)
        self.assertAlmostEqual(eta.estimated_arrival(ORD, lat, lon, None, "A1", T0) - T0,
                               3600, delta=10)

    def test_from_the_fix_time(self):
        lat, lon = self.at_distance(83)
        a = eta.estimated_arrival(ORD, lat, lon, 830.0, "A3", T0)
        b = eta.estimated_arrival(ORD, lat, lon, 830.0, "A3", T0 + 60)
        self.assertAlmostEqual(b - a, 60, delta=0.001)

    def test_at_the_destination_is_now(self):
        self.assertAlmostEqual(
            eta.estimated_arrival(ORD, ORD["destination_lat"], ORD["destination_lon"], 0.0, "A3", T0),
            T0, delta=0.001)

    def test_none_without_what_it_needs(self):
        lat, lon = self.at_distance(50)
        self.assertIsNone(eta.estimated_arrival(None, lat, lon, 800.0, "A3", T0))
        self.assertIsNone(eta.estimated_arrival({}, lat, lon, 800.0, "A3", T0))
        self.assertIsNone(eta.estimated_arrival({"destination_lat": 41.9}, lat, lon, 800.0, "A3", T0))
        self.assertIsNone(eta.estimated_arrival(ORD, None, lon, 800.0, "A3", T0))
        self.assertIsNone(eta.estimated_arrival(ORD, lat, None, 800.0, "A3", T0))
        self.assertIsNone(eta.estimated_arrival(ORD, lat, lon, 800.0, "A3", None))
        self.assertIsNone(eta.estimated_arrival(ORD, lat, lon, float("nan"), "A3", T0))
        self.assertIsNone(eta.estimated_arrival(ORD, lat, lon, "fast", "A3", T0))


class Wiring(unittest.TestCase):
    def test_published_by_the_platform(self):
        tree = ast.parse(source("geo_location.py"))
        keys = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and any(
                    getattr(t, "id", None) == "_PASSTHROUGH" for t in node.targets):
                keys = [e.value for e in node.value.elts]
        self.assertIn("arrival_estimated_at", keys)

    def test_coordinator_uses_the_fix_time_and_iso(self):
        src = source("coordinator.py")
        self.assertIn("from .eta import estimated_arrival", src)
        self.assertIn("estimated_arrival(leg, here[0], here[1], obs.speed_kmh,\n"
                      "                                    obs.emitter_category, latest[2])", src)
        self.assertIn('rec["arrival_estimated_at"] = _iso(round(eta))', src)


if __name__ == "__main__":
    unittest.main()
