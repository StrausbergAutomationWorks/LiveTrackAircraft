"""Round 4 (Lee, 2026-10-06): Jos's lines and icons of 2026-09-28, and our be12, be200, us2."""
import hashlib
import re
import unittest
import xml.etree.ElementTree as ET

from _load import load

icons = load("icons")
airframe = load("airframe")
SVG = "{http://www.w3.org/2000/svg}"
CASES = {
    "heavytransport": ("A124", "A225", "IL76", "C5M", "C17", "A400", "AN22", "A50"),
    "amphibian": ("CL2P", "CL2T", "DHC2", "DHC3", "CAT", "DH2T", "DH3T",
                  "G21", "G21T", "G21M", "G73", "G73T", "U16"),
    "be12": ("BE12",), "be200": ("BER2", "BER4"), "us2": ("US2",),
}
# sha256 of his files as he sent them (newicons.zip, 2026-09-28)
HIS = {"amphibian": "5bcce8936c6cf6716ab8ac91ad6727d38c8850b229a4b28a9ebf50c1419f4620",
       "heavytransport": "cb3d948500de0bcf26b69e7592535d3d1457245c3f23662f3c502e40cf1dc308"}
PROPS = {"be12": 2, "be200": 0, "us2": 4}


class Round4(unittest.TestCase):
    def test_each_code_draws_its_icon(self):
        for key, codes in CASES.items():
            for code in codes:
                with self.subTest(code=code):
                    self.assertEqual(icons.pick("A3", code), key)
                    self.assertFalse(airframe.is_rotorcraft("A3", code))
                    self.assertEqual(airframe.map_layer("A3", code), "air")

    def test_his_lines_are_verbatim(self):
        self.assertEqual(icons._AUTHOR_LISTS["heavytransport"], "a124,a225,il76,c5m,c17,a400,an22")
        self.assertEqual(icons._AUTHOR_LISTS["amphibian"], "cl2p,cl2t,cl4t,cl215,cl415,dhc2,dhc3,canso,pby")

    def test_his_files_ship_unchanged(self):
        for key, sha in HIS.items():
            with self.subTest(key=key):
                self.assertEqual(hashlib.sha256(open(icons.icon_path(key), "rb").read()).hexdigest(), sha)

    def test_props(self):
        for key, n in PROPS.items():
            with self.subTest(key=key):
                root = ET.fromstring(icons.render(icons.icon_path(key), None, 64, "default", 0.85, False))
                an = [a for a in root.iter("%sanimateTransform" % SVG) if a.get("type") == "scale"]
                self.assertEqual(len(an), n)

    def test_ours_drawn_inside_the_box(self):
        for key in PROPS:
            with self.subTest(key=key):
                t = open(icons.icon_path(key), encoding="utf-8").read()
                d = re.search(r'<path fill-rule="evenodd" d="([^"]+)"', t).group(1)
                v = [float(x) for x in re.findall(r"-?\d+\.?\d*", d)]
                self.assertGreaterEqual(min(v), 10)
                self.assertLessEqual(max(v), 502)

    def test_art_rev(self):
        self.assertGreaterEqual(icons.ART_REV, 7)


if __name__ == "__main__":
    unittest.main()
