"""The feed's database flags (dbFlags), 2026-10-22: military army green, PIA
"identity hidden"."""
import unittest

from _load import load

reg = load("registrations")
icons = load("icons")
adsb = load("sources.adsb")


def rec(**kw):
    r = {"hex": "ae1463", "lat": 38.8, "lon": -76.9, "alt_baro": 9000, "seen_pos": 1.0}
    r.update(kw)
    return r


class Parse(unittest.TestCase):
    def test_flags_and_owner(self):
        o = adsb._parse(rec(dbFlags=5, ownOp="United States Coast Guard"), 1e9)
        self.assertEqual((o.db_flags, o.own_op), (5, "United States Coast Guard"))

    def test_absent_or_not_an_int(self):
        for bad in (None, "1", True, 1.0):
            r = rec() if bad is None else rec(dbFlags=bad)
            self.assertIsNone(adsb._parse(r, 1e9).db_flags, bad)
        self.assertIsNone(adsb._parse(rec(ownOp="  "), 1e9).own_op)


class Flags(unittest.TestCase):
    def test_military_no_table_row(self):
        mil, cat, x = reg.from_feed_flags(1, None, None)
        self.assertTrue(mil)
        self.assertEqual(cat, "Military")
        self.assertEqual(x, {"is_military": True, "operator_category": "Military",
                             "identified_by": "feed_military"})
        self.assertEqual(icons.tone_for(False, "rotorcraft", cat, mil), "mil")
        self.assertFalse(icons.lights_for(cat))

    def test_military_coast_guard_keeps_lights(self):
        mil, cat, x = reg.from_feed_flags(1, "UNITED STATES COAST GUARD", None)
        self.assertEqual(cat, "Coast Guard")
        self.assertEqual(x["operator_short"], "USCG")
        self.assertEqual(x["operator_name_source"], "feed")
        self.assertEqual(icons.tone_for(False, None, cat, mil), "mil")
        self.assertTrue(icons.lights_for(cat))

    def test_military_owner_not_law_is_military(self):
        _, cat, _ = reg.from_feed_flags(1, "UNIVERSITY OF NOWHERE", None)
        self.assertEqual(cat, "Military")

    def test_table_row_keeps_its_category(self):
        gov = {"operator_category": "Federal law enforcement"}
        mil, cat, x = reg.from_feed_flags(1, "SOMETHING ELSE", gov)
        self.assertEqual(cat, "Federal law enforcement")
        self.assertEqual(x, {"is_military": True})
        self.assertEqual(icons.tone_for(True, None, cat, mil), "mil")   # green, with lights
        self.assertTrue(icons.lights_for(cat))

    def test_pia_and_others(self):
        self.assertEqual(reg.from_feed_flags(4, None, None), (False, None, {"identity_hidden": True}))
        for f in (0, 2, 8, None, -1, True):
            self.assertEqual(reg.from_feed_flags(f, "X", None), (False, None, {}), f)
        mil, _, x = reg.from_feed_flags(13, None, None)   # 1 + 4 + 8
        self.assertTrue(mil and x["identity_hidden"])


if __name__ == "__main__":
    unittest.main()
