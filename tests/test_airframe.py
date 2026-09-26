"""Rotorcraft is decided ONCE (airframe.is_rotorcraft) and everything follows it.

Lee, 2026-09-25: 1. the type code, when the icon table knows it: rotorcraft
exactly when it draws a7; 2. otherwise the rotor type table, with prefixes
that cannot match gliders; 3. otherwise emitter category A7.
The silhouette, the tone, icon_category and map_layer all call it, so they
cannot disagree - measured before this, they did in 82 cases.
"""
import unittest

from _load import load

icons = load("icons")
airframe = load("airframe")
aircraft = load("aircraft")

CATS = (None, "", "A1", "A2", "A3", "A7", "B1")
# Rotor types the ICON table does not know, so rule 2 decides them. Derived:
# a fixed list went stale the day Jos's 2026-09-25 list added B06, B407, R44...
ROTOR_ONLY_IN_TABLE = tuple(sorted(
    c for c in airframe._ROTOR_TYPES if c not in icons._BY_TYPE)) + ("EC130",)
assert len(ROTOR_ONLY_IN_TABLE) >= 10, ROTOR_ONLY_IN_TABLE
GLIDERS = ("KA6", "KA6CR", "MINI-NIMBUS", "MISTRALC", "AS30", "B4208", "ASK21")


def cases():
    for code in list(icons._BY_TYPE) + list(ROTOR_ONLY_IN_TABLE) + ["ZZZZ", None, ""]:
        for cat in CATS:
            yield cat, code


class Rule1TypeTableWins(unittest.TestCase):
    def test_every_table_code_is_rotor_exactly_when_it_draws_a7(self):
        for code, key in icons._BY_TYPE.items():
            for cat in CATS:
                with self.subTest(code=code, cat=cat):
                    self.assertEqual(airframe.is_rotorcraft(cat, code), key == "a7")

    def test_category_does_not_override_a_known_type(self):
        self.assertFalse(airframe.is_rotorcraft("A7", "A320"))
        self.assertTrue(airframe.is_rotorcraft("A1", "BK117C2"))
        self.assertTrue(airframe.is_rotorcraft(None, "H145M"))

    def test_r22_is_a_helicopter_by_our_override(self):
        self.assertEqual(icons.pick(None, "R22"), "a7")
        self.assertTrue(airframe.is_rotorcraft("A1", "R22"))

    def test_overrides_beat_the_author(self):
        for code, key in icons._OVERRIDES.items():
            self.assertEqual(icons._BY_TYPE[code], key)

    def test_2026_09_25_overrides(self):
        # helicopters / a gyro on his cessna, by his own descriptions
        for code in ("EN28", "CH7A", "CH7B", "MM24"):
            with self.subTest(code=code):
                self.assertEqual(icons.pick("A1", code), "a7")
                self.assertTrue(airframe.is_rotorcraft("A1", code))
        # V22: a rotorcraft until its tiltrotor icon exists
        self.assertEqual(icons.pick(None, "V22"), "a7")
        self.assertEqual(airframe.map_layer("A2", "V22"), "air_low")
        # P68 is on two of his lines: the twin, fixed here
        self.assertEqual(icons.pick("A1", "P68"), "beechcraft")

    def test_his_2026_09_25_list_is_the_base(self):
        # a sample of what his new list decides, override-free
        for code, key in (("BE20", "beechcraft"), ("B350", "beechcraft"),
                          ("B190", "beechcraft"), ("SF34", "beechcraft"),
                          ("B727", "md11"), ("GLF6", "fa7x"), ("A19N", "a320"),
                          ("B609", "a7"), ("GYRO", "a7"), ("TOBA", "cessna")):
            with self.subTest(code=code):
                self.assertEqual(icons._BY_TYPE[code], key)
        self.assertGreaterEqual(len(icons._BY_TYPE), 909)
        self.assertIsNotNone(icons.icon_path("beechcraft"))

    def test_type_codes_are_case_insensitive(self):
        self.assertTrue(airframe.is_rotorcraft(None, " bk117 "))


class Rule2RotorTable(unittest.TestCase):
    def test_rotor_types_the_icon_table_lacks(self):
        for code in ROTOR_ONLY_IN_TABLE:
            with self.subTest(code=code):
                self.assertNotIn(code, icons._BY_TYPE)
                self.assertTrue(airframe.is_rotorcraft("A1", code))
                self.assertTrue(airframe.is_rotorcraft(None, code))

    def test_gliders_are_never_rotorcraft(self):
        for code in GLIDERS:
            for cat in (None, "B1"):
                with self.subTest(code=code, cat=cat):
                    self.assertFalse(airframe.is_rotorcraft(cat, code))

    def test_no_prefix_matches_any_non_helicopter_the_table_knows(self):
        for code, key in icons._BY_TYPE.items():
            if key == "a7":
                continue
            with self.subTest(code=code):
                self.assertFalse(code.startswith(airframe._ROTOR_PREFIXES))
                self.assertNotIn(code, airframe._ROTOR_TYPES)

    def test_the_name_table_rotorcraft_are_exactly_these(self):
        # bin\prefix_test.py's gate, pinned: every designator in the
        # 246-name table, category absent. Read by name on 2026-09-25 - all
        # helicopters, plus the autogyro. Anything new here is a defect until
        # someone looks at its name.
        got = {c for c in aircraft._AIRCRAFT_TYPES if airframe.is_rotorcraft(None, c)}
        self.assertEqual(got, {
            "A139", "AS50", "B06", "B407", "B429", "EC30", "EC35", "EC45",
            "H500", "H60", "R22", "R44", "R66", "S76", "GYRO"})


class Rule3Category(unittest.TestCase):
    def test_unknown_type_falls_to_category(self):
        self.assertTrue(airframe.is_rotorcraft("A7", "ZZZZ"))
        self.assertTrue(airframe.is_rotorcraft("a7", None))
        self.assertFalse(airframe.is_rotorcraft("A1", "ZZZZ"))
        self.assertFalse(airframe.is_rotorcraft(None, None))


class EverythingAgrees(unittest.TestCase):
    def test_icon_tone_category_and_layer_follow_one_answer(self):
        for cat, code in cases():
            with self.subTest(cat=cat, code=code):
                rotor = airframe.is_rotorcraft(cat, code)
                ic = aircraft.classify(cat, code)[0]
                self.assertEqual(ic == "rotorcraft", rotor)
                self.assertEqual(icons.pick(cat, code, ic) == "a7", rotor)
                self.assertEqual(airframe.map_layer(cat, code),
                                 "air_low" if rotor else "air")
                self.assertEqual(icons.tone_for(False, ic) == "rotor", rotor)

    def test_map_layer_is_only_air_or_air_low(self):
        self.assertEqual({airframe.map_layer(c, t) for c, t in cases()},
                         {"air", "air_low"})

    def test_non_rotor_categories_keep_their_labels(self):
        self.assertEqual(aircraft.classify("B1", "ZZZZ")[0], "glider")
        self.assertEqual(aircraft.classify("A5", "ZZZZ")[1], "Heavy aircraft")
        # A7 on a known fixed-wing type is not a rotorcraft
        self.assertEqual(aircraft.classify("A7", "A320")[0], "airplane")


if __name__ == "__main__":
    unittest.main()
