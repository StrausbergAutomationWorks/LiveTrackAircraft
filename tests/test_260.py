"""Backlog 260 (Lee, 2026-09-25): the low-wing single, the tiltrotor's two
pictures and their speed switch, spinning props on OUR icons only."""
import math
import re
import unittest
import xml.etree.ElementTree as ET

from _load import load

icons = load("icons")
airframe = load("airframe")
SVG = "{http://www.w3.org/2000/svg}"


def src(key):
    return open(icons.icon_path(key), encoding="utf-8").read()


class LowWing(unittest.TestCase):
    def test_sure_types_draw_the_low_wing(self):
        for code in ("P28A", "PA28", "SR22", "BE36", "M20P", "DA40", "TOBA", "PA46", "RV10", "PC12"):
            with self.subTest(code=code):
                self.assertEqual(icons.pick("A1", code), "lowwing")
                self.assertEqual(airframe.map_layer("A1", code), "air")

    def test_high_wings_twins_and_unsure_stay(self):
        for code in ("C172", "C182", "C208", "PA18", "J3", "C340", "PAY4", "C421", "PC24", "VEZE"):
            with self.subTest(code=code):
                self.assertNotEqual(icons.pick("A1", code), "lowwing")

    def test_only_codes_he_had_on_cessna(self):
        # nothing of his other lines was moved: a low-wing code is one he filed as cessna
        cessna = set(c.strip().upper() for c in icons._AUTHOR_LISTS["cessna"].split(","))
        self.assertTrue(set(icons._LOWWING) <= cessna)
        self.assertEqual(len(set(icons._LOWWING)), 138)  # 139 on his line; TBM7 is there twice

    def test_the_gap_is_a_hole_in_the_wing(self):
        # evenodd, one path for the body: the fuselage-over-wing gap
        self.assertIn('fill-rule="evenodd"', src("lowwing"))


class Tiltrotor(unittest.TestCase):
    def test_both_pictures_are_rotorcraft(self):
        for code in ("V22", "B609"):
            with self.subTest(code=code):
                self.assertEqual(icons.pick("A3", code), "tiltrotor")
                self.assertTrue(airframe.is_rotorcraft("A3", code))
                self.assertEqual(airframe.map_layer("A3", code), "air_low")
        self.assertIn("tiltrotorfwd", icons.ROTOR_KEYS)

    def test_speed_switch_with_a_gap(self):
        f = icons.tiltrotor_forward
        self.assertFalse(f(None, None))          # first sight, no speed: hover
        self.assertFalse(f(None, 150.0))
        self.assertTrue(f(None, 200.0))
        self.assertTrue(f(True, 185.0))          # inside the gap: keep cruise
        self.assertFalse(f(False, 185.0))        # inside the gap: keep hover
        self.assertFalse(f(True, 170.0))
        self.assertTrue(f(True, None))           # speed lost: keep
        self.assertEqual((icons.TILT_FORWARD_KMH, icons.TILT_HOVER_KMH), (200.0, 170.0))

    def test_same_scale_for_both_pictures(self):
        # the body path of both is drawn from one geometry: same nose and tail
        def ys(key):
            d = re.search(r'<path fill-rule="evenodd" d="([^"]+)"', src(key)).group(1)
            v = [float(x) for x in re.findall(r"-?\d+\.?\d*", d)]
            return round(min(v[1::2])), round(max(v[1::2]))
        self.assertEqual(ys("tiltrotor"), ys("tiltrotorfwd"))

    def test_hover_rotors_stay_inside_the_round_marker(self):
        t = src("tiltrotor")
        for g in re.findall(r'<g id="rotor\d*">(.*?)</g>', t):
            cx, cy = [float(x) for x in re.search(r'from="\d+ ([\d.]+) ([\d.]+)"', g).groups()]
            pts = [float(x) for x in re.findall(r"-?\d+\.?\d*", re.search(r' d="([^"]+)"', g).group(1))]
            r = max(math.hypot(x - cx, y - cy) for x, y in zip(pts[0::2], pts[1::2]))
            self.assertLess(math.hypot(cx - 256, cy - 256) + r, 256)

    def test_every_rotor_gets_its_edge(self):
        out = icons.render(icons.icon_path("tiltrotor"), None, 64, "rotor", 0.78, False)
        root = ET.fromstring(out)
        groups = [g for g in root.iter("%sg" % SVG) if (g.get("id") or "").startswith("rotor")]
        self.assertEqual(len(groups), 2)
        self.assertTrue(all(g.get("filter") == "url(#r)" for g in groups))


class Props(unittest.TestCase):
    def test_our_props_shrink_and_grow(self):
        for key, n in (("lowwing", 1), ("kingair", 2), ("tiltrotorfwd", 2)):
            with self.subTest(key=key):
                root = ET.fromstring(icons.render(icons.icon_path(key), None, 64, "default", 0.7, False))
                an = [a for a in root.iter("%sanimateTransform" % SVG) if a.get("type") == "scale"]
                self.assertEqual(len(an), n)
                self.assertTrue(all(a.get("values", "").startswith("1 1;") for a in an))

    def test_his_icons_are_not_animated(self):
        # his props are fused into one outline; nothing of his moves
        for key in ("cessna", "beechcraft", "dh8a", "c130"):
            with self.subTest(key=key):
                self.assertNotIn("animate", src(key))


if __name__ == "__main__":
    unittest.main()
