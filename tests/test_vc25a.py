"""The VC-25A's painted icon (2026-10-22, draft A): render() keeps the paint
of an icon marked data-paint="keep", and the two VC-25As get it by hex."""
import hashlib
import unittest
import xml.etree.ElementTree as ET

from _load import load

icons = load("icons")
SVG = "{http://www.w3.org/2000/svg}"
LIVERY = {"#8EC3E6", "#24508F", "#F6F6F2"}


def fills(svg):
    return {e.get("fill") for e in ET.fromstring(svg).iter("%spath" % SVG) if e.get("fill")}


class Paint(unittest.TestCase):
    def test_the_file(self):
        path = icons.icon_path("vc25a")
        with open(path, "rb") as fh:
            raw = fh.read()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(hashlib.sha256(raw).hexdigest()[:16], "c85b33e37b70fcd9")
        self.assertIn(b'data-paint="keep"', raw)

    def test_paint_kept(self):
        out = icons.render(icons.icon_path("vc25a"), None, 64, "mil", 1.0, False)
        self.assertTrue(LIVERY <= fills(out), fills(out))
        self.assertIn('style="mask-type:alpha"', out)

    def test_others_still_one_tone(self):
        out = icons.render(icons.icon_path("b747"), None, 64, "mil", 1.0, False)
        self.assertEqual(fills(out) - {"none"}, set())
        self.assertNotIn("mask-type", out)

    def test_by_hex(self):
        self.assertEqual(icons.HEX_KEYS, {"adfdf8": "vc25a", "adfdf9": "vc25a"})
        self.assertNotIn("af83f3", icons.HEX_KEYS)      # the Bridge: not drawn yet

    def test_lights_and_edge_still_apply(self):
        out = icons.render(icons.icon_path("vc25a"), None, 64, "mil", 1.0, False, True)
        self.assertIn('id="lr"', out)
        self.assertIn('filter="url(#e)"', out)


if __name__ == "__main__":
    unittest.main()
