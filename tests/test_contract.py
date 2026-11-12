"""What the HA-bound modules must and must not say, read from their source.

The coordinator, platform and config flow import Home Assistant, so they are
checked here by reading them and on the box after a deploy by what the live
entities carry (bin\\lta_258_live.py).
"""
import ast
import json
import os
import re
import unittest

from _load import COMP, load, source

GONE = ("card_rotation", "CARD_ROTATION", "silhouette_only", "SILHOUETTE_ONLY",
        "Z_INDEX_OFFSET", "z_index_offset")


def component_files():
    for root, _dirs, files in os.walk(COMP):
        if "__pycache__" in root:
            continue
        for f in files:
            if f.endswith((".py", ".json")):
                yield os.path.relpath(os.path.join(root, f), COMP)


class OptionsAndZIndexGone(unittest.TestCase):
    def test_no_trace_in_any_component_file(self):
        for rel in component_files():
            text = source(rel)
            for word in GONE:
                with self.subTest(file=rel, word=word):
                    self.assertNotIn(word, text)

    def test_strings_offer_only_the_dialog_fields(self):
        # Five fields until 2026-10-18; latitude and longitude became one map
        # marker, `location`, with backlog 192. Still no icon option.
        s = json.loads(source("strings.json"))
        for step in (s["config"]["step"]["user"], s["options"]["step"]["init"]):
            self.assertEqual(set(step["data"]),
                             {"location", "radius_km",
                              "scan_interval", "max_aircraft", "military_areas",
                              # backlog 332, a user's own watch list
                              "follow_hexes", "follow_callsigns",
                              # backlog 336, the user's own adsb.lol key
                              "adsblol_api_key"})


def passthrough():
    tree = ast.parse(source("geo_location.py"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                getattr(t, "id", None) == "_PASSTHROUGH" for t in node.targets):
            return [e.value for e in node.value.elts]
    raise AssertionError("_PASSTHROUGH not found")


class Platform(unittest.TestCase):
    def test_map_layer_and_object_ids_are_published(self):
        keys = passthrough()
        self.assertIn("map_layer", keys)
        self.assertIn("object_ids", keys)

    def test_the_ice_air_flight_flags_are_published(self):
        # 2026-10-31 (Lee 02:06): the record held them since 7b0d259 and the entity did not.
        keys = passthrough()
        self.assertIn("ice_air_flight", keys)
        self.assertIn("ice_air_charter_flight", keys)
        written = re.findall(r'out\["(ice_air_\w+)"\]\s*=', source("coordinator.py"))
        self.assertTrue(written)
        for key in written:
            self.assertIn(key, keys, key)


class CoordinatorWiring(unittest.TestCase):
    def setUp(self):
        self.src = source("coordinator.py")

    def test_layer_and_ids_come_from_the_shared_functions(self):
        self.assertIn("map_layer(", self.src)
        self.assertIn("object_ids(", self.src)
        self.assertIn("registry_registration(", self.src)

    def test_the_guard_is_fed_the_last_good_count(self):
        self.assertIn("short_floor(", self.src)
        self.assertIn("min_expected=", self.src)

    def test_rotorcraft_is_not_decided_in_the_coordinator(self):
        # it calls classify / pick / map_layer; all three go to airframe
        self.assertNotIn('== "A7"', self.src)
        self.assertNotIn("_ROTOR_", self.src)

    def test_picture_is_never_rotated_by_us(self):
        self.assertIn("picture_url(", self.src)
        self.assertNotIn("badge=", self.src)


class OneDecider(unittest.TestCase):
    def test_classify_and_pick_both_call_is_rotorcraft(self):
        # icons.pick() is in saw_livetrack.aircraft_icons since backlog 298.
        from saw_livetrack import aircraft_icons
        lib = open(aircraft_icons.__file__, encoding="utf-8").read()
        for rel, text in (("aircraft.py", source("aircraft.py")), ("aircraft_icons", lib)):
            with self.subTest(file=rel):
                self.assertIn("is_rotorcraft(", text)


if __name__ == "__main__":
    unittest.main()
