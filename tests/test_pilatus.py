"""The six Pilatus icons (Lee, 2026-09-26), traced from Pilatus's model building plans."""
import re
import unittest
import xml.etree.ElementTree as ET

from _load import load

icons = load("icons")
airframe = load("airframe")
SVG = "{http://www.w3.org/2000/svg}"
CODES = {"PC6P": "pc6", "PC6T": "pc6", "PC7": "pc7", "PC9": "pc9", "PC12": "pc12", "PC21": "pc21", "PC24": "pc24"}
PROPS = ("pc6", "pc7", "pc9", "pc12", "pc21")


class Pilatus(unittest.TestCase):
    def test_codes(self):
        for code, key in CODES.items():
            with self.subTest(code=code):
                self.assertEqual(icons.pick("A1", code), key)
                self.assertFalse(airframe.is_rotorcraft("A1", code))
                self.assertIsNotNone(icons.icon_path(key))

    def test_one_spinning_prop_each_and_none_on_the_jet(self):
        for key in CODES.values():
            with self.subTest(key=key):
                root = ET.fromstring(icons.render(icons.icon_path(key), None, 64, "default", 0.72, False))
                an = [a for a in root.iter("%sanimateTransform" % SVG) if a.get("type") == "scale"]
                self.assertEqual(len(an), 1 if key in PROPS else 0)

    def test_drawn_inside_the_box(self):
        for key in set(CODES.values()):
            with self.subTest(key=key):
                t = open(icons.icon_path(key), encoding="utf-8").read()
                d = re.search(r'<path fill-rule="evenodd" d="([^"]+)"', t).group(1)
                v = [float(x) for x in re.findall(r"-?\d+\.?\d*", d)]
                self.assertGreaterEqual(min(v), 10)
                self.assertLessEqual(max(v), 502)

    def test_art_rev(self):
        self.assertGreaterEqual(icons.ART_REV, 6)


if __name__ == "__main__":
    unittest.main()
