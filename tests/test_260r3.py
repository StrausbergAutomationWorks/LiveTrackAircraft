"""Backlog 260 round 3 (Lee, 2026-09-26): ten new icons, the unsure codes placed,
and Jos's cessna and beechcraft propellers cut out and spinning."""
import hashlib
import math
import re
import unittest
import xml.etree.ElementTree as ET

from _load import load

icons = load("icons")
airframe = load("airframe")
SVG = "{http://www.w3.org/2000/svg}"
NEW = ("tandem", "coaxial", "kmax", "gyro", "flyingwing", "fighter", "biplane", "canard", "p180", "cheyenne")
ROTORS = ("tandem", "coaxial", "kmax", "gyro")


def src(key):
    return open(icons.icon_path(key), encoding="utf-8").read()


class Placement(unittest.TestCase):
    CASES = {
        "lowwing": ("AS02", "B209", "BT36", "CRES", "D250", "EUPA", "SUBA", "TOUR", "V252"),
        "cessna": ("ALSL", "C82S", "GLST", "JFOX", "JUNR", "MC01", "NNJA", "RS21", "VR7", "WILT"),
        "beechcraft": ("C421", "C425", "C340", "VTOR"),
        "cheyenne": ("PAY4",),
        "learjet": ("PC24",),
        "canard": ("VEZE", "LGEZ", "COZY", "VELO"),
        "biplane": ("SA75", "ST75", "PTS2", "BU31", "EAGL", "WACF"),
        "fighter": ("T38", "F16", "F15", "F5", "F18H", "EUFI", "MG29"),
        "tandem": ("H47",),
        "coaxial": ("KA27", "KA32", "KA52"),
        "kmax": ("KMAX",),
        "gyro": ("GYRO", "MT", "MM16", "MM24"),
        "flyingwing": ("B2",),
        "p180": ("P180",),
    }

    def test_each_code_draws_its_icon(self):
        for key, codes in self.CASES.items():
            for code in codes:
                with self.subTest(code=code):
                    self.assertEqual(icons.pick("A1", code), key)

    def test_every_new_icon_ships(self):
        for key in NEW:
            with self.subTest(key=key):
                self.assertIsNotNone(icons.icon_path(key))

    def test_new_rotorcraft_stay_rotorcraft(self):
        for key in ROTORS:
            self.assertIn(key, icons.ROTOR_KEYS)
        for code in ("H47", "KA27", "KMAX", "MT", "MM24"):
            with self.subTest(code=code):
                self.assertTrue(airframe.is_rotorcraft("A1", code))
                self.assertEqual(airframe.map_layer("A1", code), "air_low")

    def test_fixed_wing_are_not(self):
        for code in ("B2", "P180", "PAY4", "T38", "VEZE", "ST75"):
            with self.subTest(code=code):
                self.assertFalse(airframe.is_rotorcraft("A1", code))

    def test_art_rev_bumped(self):
        self.assertGreaterEqual(icons.ART_REV, 5)


class NewIcons(unittest.TestCase):
    def test_rotors_stay_inside_the_round_marker(self):
        for key in ROTORS:
            for g in re.findall(r'<g id="rotor\d*">(.*?)</g>', src(key)):
                with self.subTest(key=key):
                    cx, cy = [float(x) for x in re.search(r'from="\d+ ([\d.]+) ([\d.]+)"', g).groups()]
                    pts = [float(x) for x in re.findall(r"-?\d+\.?\d*", re.search(r' d="([^"]+)"', g).group(1))]
                    r = max(math.hypot(x - cx, y - cy) for x, y in zip(pts[0::2], pts[1::2]))
                    self.assertLess(math.hypot(cx - 256, cy - 256) + r, 256)

    def test_every_rotor_gets_its_edge(self):
        for key, n in (("tandem", 2), ("coaxial", 2), ("kmax", 2), ("gyro", 1)):
            with self.subTest(key=key):
                root = ET.fromstring(icons.render(icons.icon_path(key), None, 64, "rotor", 0.78, False))
                groups = [g for g in root.iter("%sg" % SVG) if (g.get("id") or "").startswith("rotor")]
                self.assertEqual(len(groups), n)
                self.assertTrue(all(g.get("filter") == "url(#r)" for g in groups))

    def test_props_shrink_and_grow(self):
        for key, n in (("gyro", 1), ("biplane", 1), ("canard", 1), ("p180", 2), ("cheyenne", 2)):
            with self.subTest(key=key):
                root = ET.fromstring(icons.render(icons.icon_path(key), None, 64, "default", 0.7, False))
                an = [a for a in root.iter("%sanimateTransform" % SVG) if a.get("type") == "scale"]
                self.assertEqual(len(an), n)


class HisPropsCut(unittest.TestCase):
    # sha256 of his outline's d attribute, taken from the files as he sent them
    ORIGINAL = {"cessna": "6c8fe959a7882a0bc137677f32a0565de2786861bc415e39886e6de65cfc4142", "beechcraft": "002c98232b1a62f4a36a1925b0fce383777b06ebccdc336e0ae06d92e2b42de3"}
    PROPS = {"cessna": (1, 96.0), "beechcraft": (2, 74.1)}   # count, span of his prop bar

    def test_his_outline_is_unchanged(self):
        for key, sha in self.ORIGINAL.items():
            with self.subTest(key=key):
                d = re.search(r'<path clip-path="url\(#cut_%s\)"[^>]*\sd="([^"]+)"' % key, src(key)).group(1)
                self.assertEqual(hashlib.sha256(d.encode()).hexdigest(), sha)
                self.assertIn("Jos Nutbroek", src(key))

    def test_props_redrawn_to_his_span_and_spinning(self):
        for key, (n, span) in self.PROPS.items():
            with self.subTest(key=key):
                t = src(key)
                groups = re.findall(r'<g id="prop\d" transform="translate\([^)]+\)"><g><path d="([^"]+)"/>', t)
                self.assertEqual(len(groups), n)
                for d in groups:
                    xs = [float(x) for x in re.findall(r"-?\d+\.?\d*", d)][0::2]
                    self.assertAlmostEqual(max(xs) - min(xs), span, delta=0.6)
                root = ET.fromstring(icons.render(icons.icon_path(key), None, 64, "default", 0.7, False))
                an = [a for a in root.iter("%sanimateTransform" % SVG) if a.get("type") == "scale"]
                self.assertEqual(len(an), n)

    def test_the_clip_survives_render(self):
        for key in self.ORIGINAL:
            with self.subTest(key=key):
                out = icons.render(icons.icon_path(key), None, 64, "default", 0.7, False)
                self.assertIn('<clipPath id="cut_%s">' % key, out)
                self.assertIn('clip-rule="evenodd"', out)


if __name__ == "__main__":
    unittest.main()
