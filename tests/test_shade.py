"""A more delicate edge and gentle shading (Lee, 2026-10-21 00:19).

"Start with the ground shadow, then gentle shading, and keep the black edge,
but reduce the thickness so they look more delicate." The shadow is the
card's (LiveTrackMapCard, contract D4a-shadow); the edge and the shading are
drawn here. Values chosen by eye: 20_Research/icons_depth_20261021/.
"""
import os
import re
import unittest
import xml.etree.ElementTree as ET

from _load import load

icons = load("icons")
SVG = "{http://www.w3.org/2000/svg}"


def rendered(key, tone="default", weight=0.8, degrees=None):
    return icons.render(icons.icon_path(key), degrees, 64, tone, weight, False)


def keys():
    # ! A file named for a hex (af83f3.svg, Lee 2026-10-21, 5a26fc0) is a
    # PICTURE for one aircraft, not type artwork: it is not rendered and shaded.
    # The library's icons and this component's own (backlog 298).
    return sorted(f[:-4] for f in os.listdir(icons.icon_dir()) + os.listdir(icons.local_icon_dir())
                  if f.endswith(".svg") and not re.match(r"^[0-9a-f]{6}\.svg$", f))


class Edge(unittest.TestCase):
    def test_one_pixel(self):
        self.assertEqual(icons.OUTLINE_PX, 1.0)

    def test_the_filter_carries_it(self):
        out = rendered("b737")
        _, w, h = icons._inner(open(icons.icon_path("b737"), encoding="utf-8").read())
        r = float(re.search(r'<filter id="e"[^>]*>\s*<feMorphology [^>]*radius="([\d.]+)"', out).group(1))
        self.assertAlmostEqual(r, 1.0 * max(w, h) / 64.0, places=3)

    def test_still_black(self):
        self.assertIn('flood-color="%s"' % icons.BADGE, rendered("b737"))


class Shading(unittest.TestCase):
    def test_every_icon_is_well_formed_and_shaded(self):
        for key in keys():
            with self.subTest(key=key):
                root = ET.fromstring(rendered(key))
                ids = {e.get("id") for e in root.iter()}
                self.assertTrue({"art", "m", "sp", "fa", "e"} <= ids, ids)
                uses = [u.get("href") for u in root.iter("%suse" % SVG)]
                self.assertEqual(uses, ["#art", "#art"])

    def test_the_art_takes_its_tone_from_the_use(self):
        for tone, colour in icons._TONES.items():
            root = ET.fromstring(rendered("a330", tone))
            art = [g for g in root.iter("%sg" % SVG) if g.get("id") == "art"][0]
            self.assertIsNone(art.get("fill"))
            drawn = [u for u in root.iter("%suse" % SVG) if u.get("fill") != "#fff"]
            self.assertEqual([u.get("fill") for u in drawn], [colour])

    def test_the_mask_is_the_silhouette_in_white(self):
        root = ET.fromstring(rendered("cessna"))
        mask = [m for m in root.iter("%smask" % SVG) if m.get("id") == "m"][0]
        self.assertEqual([(u.get("href"), u.get("fill")) for u in mask.iter("%suse" % SVG)], [("#art", "#fff")])

    def test_both_gradients_are_masked_to_it_and_under_the_edge(self):
        root = ET.fromstring(rendered("b777"))
        edge = [g for g in root.iter("%sg" % SVG) if g.get("filter") == "url(#e)"][0]
        rects = [(r.get("fill"), r.get("mask")) for r in edge.iter("%srect" % SVG)]
        self.assertEqual(rects, [("url(#sp)", "url(#m)"), ("url(#fa)", "url(#m)")])

    def test_spanwise_symmetric_about_the_spine(self):
        root = ET.fromstring(rendered("b737", weight=0.85))
        g = [x for x in root.iter("%slinearGradient" % SVG) if x.get("id") == "sp"][0]
        _, w, _ = icons._inner(open(icons.icon_path("b737"), encoding="utf-8").read())
        self.assertAlmostEqual((float(g.get("x1")) + float(g.get("x2"))) / 2, w / 2, places=2)
        stops = [(float(s.get("offset")), s.get("stop-color"), float(s.get("stop-opacity")))
                 for s in g.iter("%sstop" % SVG)]
        for (o, c, a), (o2, c2, a2) in zip(stops, reversed(stops)):
            self.assertAlmostEqual(o, 1 - o2)
            self.assertEqual((c, a), (c2, a2))

    def test_gentle(self):
        self.assertEqual(icons.SHADE, 0.6)
        out = rendered("b737")
        opacities = [float(x) for x in re.findall(r'stop-opacity="([\d.]+)"', out)]
        self.assertLessEqual(max(opacities), 0.42 * 0.6 + 1e-9)
        self.assertIn('stop-color="#fff" stop-opacity="0.240"', out)

    def test_the_footprint_scales_with_weight(self):
        def span(weight):
            g = re.search(r'<linearGradient id="sp"[^>]*x1="([\d.]+)"[^>]*x2="([\d.]+)"', rendered("b737", weight=weight))
            return float(g.group(2)) - float(g.group(1))
        self.assertAlmostEqual(span(0.5) * 2, span(1.0), places=2)

    def test_animations_survive(self):
        for key, kind in (("a7", "rotate"), ("cessna", "scale"), ("lowwing", "scale")):
            with self.subTest(key=key):
                root = ET.fromstring(rendered(key))
                self.assertTrue(any(a.get("type") == kind for a in root.iter("%sanimateTransform" % SVG)))

    def test_a_turned_picture_is_not_shaded(self):
        out = rendered("b737", degrees=90)
        self.assertNotIn("<mask", out)
        self.assertIn("rotate(90 ", out)

    def test_the_badge_path_is_unchanged(self):
        out = icons.render(icons.icon_path("b737"), None, 64, "default", 0.8, True)
        self.assertNotIn("<mask", out)
        self.assertIn("<circle", out)

    def test_art_rev(self):
        self.assertGreaterEqual(icons.ART_REV, 8)


if __name__ == "__main__":
    unittest.main()
