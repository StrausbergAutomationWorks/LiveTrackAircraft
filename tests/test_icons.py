"""Pictures: always unrotated, never a disc, and the helicopter's rotor spins.

Lee, 2026-09-25: always serve unrotated, always drop the disc, remove both
options from the flow; port the animated rotor Live Track Ships uses on its SAR
helicopter. The card turns the marker from icon_rotation_deg.
"""
import os
import re
import unittest
import xml.etree.ElementTree as ET

from _load import COMP, load

icons = load("icons")
SVG = "{http://www.w3.org/2000/svg}"


def rendered(key, tone="default", weight=0.8):
    return icons.render(icons.icon_path(key), None, 64, tone, weight, False)


class Rotor(unittest.TestCase):
    def test_a7_rotor_spins_about_its_hub(self):
        root = ET.fromstring(rendered("a7", "rotor", 0.78))
        anims = root.findall(".//%sanimateTransform" % SVG)
        self.assertEqual(len(anims), 1)
        a = anims[0]
        self.assertEqual(a.get("type"), "rotate")
        self.assertEqual(a.get("repeatCount"), "indefinite")
        f = [float(x) for x in a.get("from").split()]
        t = [float(x) for x in a.get("to").split()]
        self.assertEqual((f[0], t[0]), (0.0, 360.0))
        # the hub: where the two blades of the source art cross
        self.assertAlmostEqual(f[1], icons.ROTOR_HUB[0], places=1)
        self.assertAlmostEqual(f[2], icons.ROTOR_HUB[1], places=1)
        self.assertEqual(f[1:], t[1:])
        self.assertAlmostEqual(icons.ROTOR_HUB[0], 100.8, delta=0.5)
        self.assertAlmostEqual(icons.ROTOR_HUB[1], 84.1, delta=0.5)

    def test_rotor_group_holds_the_two_blades_and_nothing_else(self):
        root = ET.fromstring(rendered("a7"))
        groups = [g for g in root.iter("%sg" % SVG)
                  if g.find("%sanimateTransform" % SVG) is not None]
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0].findall("%spath" % SVG)), 2)
        # the animated group must carry no transform of its own: the
        # animation REPLACES it, so one would be lost the moment it runs
        self.assertIsNone(groups[0].get("transform"))

    def test_nothing_else_animates(self):
        for f in sorted(os.listdir(os.path.join(COMP, "icons"))):
            key = f[:-4]
            if key == "a7" or not f.endswith(".svg"):
                continue
            with self.subTest(key=key):
                self.assertNotIn("animate", rendered(key))


class Pictures(unittest.TestCase):
    def test_every_icon_renders_as_strict_xml(self):
        keys = [f[:-4] for f in os.listdir(os.path.join(COMP, "icons")) if f.endswith(".svg")]
        self.assertGreaterEqual(len(keys), 38)
        for key in keys:
            with self.subTest(key=key):
                ET.fromstring(rendered(key))

    def test_no_disc_in_a_rendered_picture(self):
        self.assertNotIn("<circle", rendered("a320"))
        self.assertNotIn("<circle", rendered("a7", "rotor"))

    def test_picture_url_is_unrotated_and_discless(self):
        url = icons.picture_url("a7", "rotor", 0.78)
        self.assertRegex(url, r"^/api/live_track_aircraft/icon/a7/fixed\.svg\?")
        q = dict(p.split("=") for p in url.split("?", 1)[1].split("&"))
        self.assertEqual(q.get("b"), "0")
        self.assertEqual(q.get("t"), "rotor")
        self.assertEqual(q.get("w"), "0.78")
        # the art revision busts browsers' day-long cache of the static a7
        self.assertEqual(q.get("a"), str(icons.ART_REV))
        self.assertGreaterEqual(icons.ART_REV, 2)

    def test_picture_url_takes_no_angle_and_no_badge(self):
        import inspect
        params = inspect.signature(icons.picture_url).parameters
        self.assertEqual(list(params), ["key", "tone", "weight"])

    def test_default_tone_is_not_written(self):
        self.assertNotIn("t=", icons.picture_url("a320", "default", 0.85))


if __name__ == "__main__":
    unittest.main()
