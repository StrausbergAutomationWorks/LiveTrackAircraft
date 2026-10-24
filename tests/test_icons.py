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
        # over the CABIN (its area centroid), not the fuselage waist (84.1)
        self.assertAlmostEqual(icons.ROTOR_HUB[0], 100.8, delta=0.5)
        self.assertAlmostEqual(icons.ROTOR_HUB[1], 57.8, delta=0.5)

    def test_blades_cross_at_the_hub(self):
        # the two blade centre lines, through their own matrices, meet at the hub
        import re
        src = open(icons.icon_path("a7"), encoding="utf-8").read()
        lines = []
        for d, m in re.findall(r'<path style="[^"]*" d="([^"]+)" transform="matrix\(([^)]+)\)"/>', src):
            n = [float(x) for x in re.findall(r"-?\d+\.?\d*", d)]
            cx = (min(n[0::2]) + max(n[0::2])) / 2
            a, b, c, dd, e, f = [float(x) for x in m.split(",")]
            tr = lambda x, y: (a * x + c * y + e, b * x + dd * y + f)
            lines.append((tr(cx, min(n[1::2])), tr(cx, max(n[1::2]))))
        (x1, y1), (x2, y2) = lines[0]
        (x3, y3), (x4, y4) = lines[1]
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
        py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
        self.assertAlmostEqual(px, icons.ROTOR_HUB[0], delta=0.05)
        self.assertAlmostEqual(py, icons.ROTOR_HUB[1], delta=0.05)
        for (sx, sy), (ex, ey) in lines:
            for x, y in ((sx, sy), (ex, ey)):
                self.assertAlmostEqual(((x - px) ** 2 + (y - py) ** 2) ** 0.5,
                                       icons.ROTOR_RADIUS, delta=0.5)

    def test_every_tip_stays_inside_the_round_marker_at_any_weight(self):
        # the card clips a picture marker to a circle of the picture's own box
        import math
        for w in (0.5, 0.62, 0.78, 0.85, 1.0, 5.0):
            k = icons._FIT * max(0.1, min(1.0, min(w, icons.ROTOR_MAX_WEIGHT)))
            hx = 100 + (icons.ROTOR_HUB[0] - 100) * k
            hy = 100 + (icons.ROTOR_HUB[1] - 100) * k
            reach = math.hypot(hx - 100, hy - 100) + icons.ROTOR_RADIUS * k
            with self.subTest(weight=w):
                self.assertLess(reach, 99.0)
                self.assertGreater(hy - icons.ROTOR_RADIUS * k, 0.0)

    def test_the_rotor_has_its_own_edge(self):
        root = ET.fromstring(rendered("a7", "rotor", 0.78))
        g = [x for x in root.iter("%sg" % SVG) if x.get("id") == "rotor"][0]
        self.assertEqual(g.get("filter"), "url(#r)")
        self.assertEqual(len([f for f in root.iter("%sfilter" % SVG) if f.get("id") == "r"]), 1)
        self.assertNotIn('filter id="r"', rendered("a320"))

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
            if key in ("a7", "lowwing", "kingair", "tiltrotor", "tiltrotorfwd",
                       # backlog 260 round 3 (2026-09-26); cessna/beechcraft: his props, cut out
                       "tandem", "coaxial", "kmax", "gyro", "biplane", "canard", "p180", "cheyenne",
                       "cessna", "beechcraft", "pc6", "pc7", "pc9", "pc12", "pc21",
                       # round 4 (2026-10-06): their props
                       "be12", "us2",
                       # 2026-10-24: the King Air 350's props
                       "kingair350") or not f.endswith(".svg"):
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
        self.assertGreaterEqual(icons.ART_REV, 4)

    def test_picture_url_takes_no_angle_and_no_badge(self):
        import inspect
        params = inspect.signature(icons.picture_url).parameters
        self.assertEqual(list(params), ["key", "tone", "weight", "lights"])

    def test_default_tone_is_not_written(self):
        self.assertNotIn("t=", icons.picture_url("a320", "default", 0.85))


if __name__ == "__main__":
    unittest.main()
