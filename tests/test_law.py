"""Law enforcement on the map (2026-10-22): the fill by owner class, police
lights, Coast Guard green with lights, and what the marker says."""
import unittest
import xml.etree.ElementTree as ET

from _load import load

icons = load("icons")
reg = load("registrations")
SVG = "{http://www.w3.org/2000/svg}"
LAW, FED, CG, MIL = "Law enforcement", "Federal law enforcement", "Coast Guard", "Military"


class Fill(unittest.TestCase):
    def test_owner_class(self):
        self.assertEqual(icons.tone_for(True, None, MIL), "mil")
        self.assertEqual(icons.tone_for(True, None, CG), "mil")
        self.assertEqual(icons.tone_for(True, "rotorcraft", LAW), "police")
        self.assertEqual(icons.tone_for(True, None, FED), "law")
        self.assertEqual(icons.tone_for(True, "rotorcraft", "Fire / EMS"), "gov")
        self.assertEqual(icons.tone_for(False, "rotorcraft"), "rotor")
        self.assertEqual(icons.tone_for(False, None, None, military=True), "mil")

    def test_colours(self):
        self.assertEqual(icons._TONES["mil"], "#5C6B32")
        self.assertEqual(icons._TONES["law"], "#2F5DB8")
        self.assertEqual(icons._TONES["police"], "#FFFFFF")

    def test_lights(self):
        for cat in (LAW, FED, CG):
            self.assertTrue(icons.lights_for(cat), cat)
        for cat in (MIL, "Government", None):
            self.assertFalse(icons.lights_for(cat), cat)

    def test_level_with_registrations(self):
        self.assertEqual(icons.LIGHT_CATEGORIES, reg.LAW_ENFORCEMENT)
        self.assertEqual(reg.categorise("UNITED STATES COAST GUARD"), CG)


def rendered(key="a7", lights=True, degrees=None, badge=False):
    return icons.render(icons.icon_path(key), degrees, 64, "law", 0.66, badge, lights)


class Lights(unittest.TestCase):
    def test_two_glows_that_alternate(self):
        root = ET.fromstring(rendered())
        floods = {f.get("id"): f.find("%sfeFlood" % SVG).get("flood-color")
                  for f in root.iter("%sfilter" % SVG) if f.get("id") in ("lr", "lb")}
        self.assertEqual(floods, {"lr": icons.LIGHT_RED, "lb": icons.LIGHT_BLUE})
        groups = [g for g in root if g.tag == "%sg" % SVG]
        self.assertEqual(len(groups), 3)                     # red, blue, the art
        self.assertEqual(groups[2].get("filter"), "url(#e)")  # the art on top
        for g, want, fid in ((groups[0], "1;0", "lr"), (groups[1], "0;1", "lb")):
            a = g.find("%sanimate" % SVG)
            self.assertEqual(a.get("values"), want)
            self.assertEqual(a.get("calcMode"), "discrete")
            self.assertEqual(a.get("dur"), "1.2s")
            self.assertEqual(g.get("opacity"), want[0])
            self.assertEqual([u.get("filter") for u in g.iter("%suse" % SVG)], ["url(#%s)" % fid] * 2)

    def test_under_three_flashes_a_second(self):
        self.assertGreaterEqual(icons.LIGHT_PERIOD_S / 2, 1 / 3.0)

    def test_none_unless_asked(self):
        self.assertNotIn('id="lr"', rendered(lights=False))
        self.assertEqual(rendered(lights=False),
                         icons.render(icons.icon_path("a7"), None, 64, "law", 0.66, False))

    def test_not_on_the_old_paths(self):
        self.assertNotIn('id="lr"', rendered(degrees=90))
        self.assertNotIn('id="lr"', rendered(badge=True))

    def test_url(self):
        self.assertIn("l=1", icons.picture_url("a7", "law", 0.66, lights=True))
        self.assertNotIn("l=", icons.picture_url("a7", "law", 0.66))


class PoliceFlash(unittest.TestCase):
    """State and local police: white, Ships' blue wig-wag (2026-10-22)."""

    def test_blue_wig_wag_on_top(self):
        out = icons.render(icons.icon_path("a7"), None, 64, "police", 0.66, False, True)
        root = ET.fromstring(out)
        self.assertNotIn('id="lr"', out)
        ells = list(root.iter("%sellipse" % SVG))
        self.assertEqual(len(ells), 2)
        begins = [e.find("%sanimate" % SVG).get("begin") for e in ells]
        self.assertEqual(begins, ["0s", "-0.4s"])
        for e in ells:
            self.assertEqual(e.find("%sanimate" % SVG).get("dur"), "0.8s")
        stops = {s.get("stop-color") for s in root.iter("%sstop" % SVG)}
        self.assertTrue({icons.POLICE_BLUE, icons.POLICE_HOT} <= stops)
        self.assertNotIn(icons.LIGHT_RED, stops)
        top = [c for c in root][-1]
        self.assertNotEqual(top.get("filter"), "url(#e)")      # outside the edge filter

    def test_the_flash_stays_inside_the_image(self):
        for k in (0.30, 0.44, 0.60, 0.71):
            self.assertLessEqual(k * icons._flash_reach(icons.police_flash_r(k)), icons.REACH_LIMIT + 1e-6)

    def test_federal_keeps_the_red_and_blue_glow(self):
        self.assertEqual(icons.tone_for(True, None, FED), "law")
        out = icons.render(icons.icon_path("a7"), None, 64, "law", 0.66, False, True)
        self.assertIn('id="lr"', out)
        self.assertNotIn("<ellipse", out)


class Label(unittest.TestCase):
    CASES = [
        ("DEPARTMENT OF HOMELAND SECURITY", FED, "DHS"),
        ("DEPARTMENT OF HOMELAND SECURITY US CUSTOMS &", FED, "CBP"),
        ("U S IMMIGRATION AND CUSTOMS ENFORCEMENT", FED, "ICE"),
        ("FEDERAL BUREAU OF INVESTIGATION", FED, "FBI"),
        ("U S MARSHALS SERVICE", FED, "USMS"),
        ("CBP AIR LOGISTICS LLC", FED, "CBP"),
        ("UNITED STATES COAST GUARD", CG, "USCG"),
        ("TEXAS DEPARTMENT OF PUBLIC SAFETY", LAW, "TX DPS"),
        ("CALIFORNIA HIGHWAY PATROL", LAW, "CA Hwy Patrol"),
        ("NEW YORK CITY POLICE DEPARTMENT", LAW, "NYPD"),
        ("LOS ANGELES POLICE DEPT AIR SUPPORT DIVISION", LAW, "LAPD"),
        ("UTAH COUNTY SHERIFF", LAW, "Utah Co Sheriff"),
        ("MISSISSIPPI COUNTY SHERIFFS DEPARTMENT", LAW, "Mississippi Co Sheriff"),
        ("MIAMI-DADE SHERIFFS OFFICE", LAW, "Miami-Dade Sheriff"),
        ("MARYLAND STATE POLICE AVIATION COMMAND", LAW, "MD State Police"),
        ("SAN BERNARDINO COUNTY SHERIFFS DEPT", LAW, "San Bernardino Sheriff"),
        ("TENNESSEE DEPARTMENT OF SAFETY & HOMELAND SECURITY", LAW, "TN DOS"),
        ("COUNTY OF MERCED SHERIFF'S DEPT", LAW, "Merced Co Sheriff"),
    ]

    def test_cases(self):
        for owner, cat, want in self.CASES:
            with self.subTest(owner=owner):
                self.assertEqual(reg.operator_short(owner, cat), want)

    def test_only_law_enforcement(self):
        self.assertIsNone(reg.operator_short("NAVAL AIR SYSTEMS COMMAND", MIL))
        self.assertIsNone(reg.operator_short("CITY OF CHICAGO", "Government"))

    def test_lookup(self):
        r = reg.GovRegistry()
        r._table = {"A00001": ["N1", "CBP AIR LOGISTICS LLC", "TX"],
                    "A00002": ["N2", "ILLINOIS STATE POLICE", "IL"],
                    "A00003": ["N3", "NASA", "CA"]}
        r._loaded = True
        a, b, c = (r.lookup(h) for h in ("A00001", "A00002", "A00003"))
        self.assertEqual((a["identified_by"], a["operator_short"]), ("faa_federal_list", "CBP"))
        self.assertEqual((b["identified_by"], b["operator_short"]), ("faa_government", "IL State Police"))
        self.assertEqual(c["identified_by"], "faa_government")
        self.assertNotIn("operator_short", c)

    def test_watch_list_hexes(self):
        r = reg.GovRegistry()
        r._table = {"A00002": ["N2", "ILLINOIS STATE POLICE", "IL"],
                    "A00001": ["N1", "UNITED STATES COAST GUARD", ""],
                    "A00003": ["N3", "NASA", "CA"]}
        r._loaded = True
        self.assertEqual(r.law_enforcement_hexes(), ["a00001", "a00002"])
        r._table = {}
        self.assertEqual(r.law_enforcement_hexes(), ["a00001", "a00002"])   # cached per table
        r._law = None
        self.assertEqual(r.law_enforcement_hexes(), [])


if __name__ == "__main__":
    unittest.main()
