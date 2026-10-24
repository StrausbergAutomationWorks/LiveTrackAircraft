"""The King Air 350's own icon (Lee 2026-10-24, draft D): ours, painted to keep its
black windows, two spinning props, and ART_REV moved with it."""
import os
import re
import unittest
import xml.etree.ElementTree as ET

from _load import COMP, load

icons = load("icons")


class KingAir350(unittest.TestCase):
    def test_b350_draws_kingair350(self):
        self.assertEqual(icons.pick("A1", "B350"), "kingair350")
        self.assertEqual(icons.pick(None, "b350"), "kingair350")

    def test_the_other_king_airs_stay_on_his_beechcraft(self):
        for code in ("BE20", "BE30", "BE9L"):
            with self.subTest(code=code):
                self.assertEqual(icons.pick("A1", code), "beechcraft")

    def test_file_keeps_its_paint_and_has_two_props(self):
        with open(icons.icon_path("kingair350"), "rb") as fh:  # in the library since backlog 298
            raw = fh.read()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        self.assertIn(b'data-paint="keep"', raw)
        self.assertEqual(raw.count(b"<animateTransform"), 2)
        self.assertEqual(raw.count(b'fill="#000" d='), 2)   # windscreen and band, solid

    def test_renders_in_every_tone_as_strict_xml(self):
        for tone in ("default", "gov", "law", "police", "mil"):
            with self.subTest(tone=tone):
                ET.fromstring(icons.render(icons.icon_path("kingair350"), None, 64, tone,
                                           0.62, False, tone in ("law", "police")))

    def test_windows_stay_black_after_render(self):
        svg = icons.render(icons.icon_path("kingair350"), None, 64, "law", 0.62, False)
        self.assertGreaterEqual(len(re.findall(r'fill="#000" d=', svg)), 2)

    def test_art_rev(self):
        self.assertGreaterEqual(icons.ART_REV, 10)


if __name__ == "__main__":
    unittest.main()
