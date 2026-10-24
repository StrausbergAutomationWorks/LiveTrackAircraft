"""The user's own picture for one aircraft, by hex (Lee, 2026-10-21 04:10)."""
import os
import shutil
import tempfile
import unittest

from _load import load

pictures = load("pictures")


class Folder(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="ltapic_")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def put(self, name, data=b"x" * 10, mtime=None):
        p = os.path.join(self.dir, name)
        with open(p, "wb") as fh:
            fh.write(data)
        if mtime is not None:
            os.utime(p, (mtime, mtime))
        return p


class Scan(Folder):
    def test_finds_a_picture_by_hex(self):
        self.put("af83f3.png", mtime=1_700_000_000)
        o = pictures.Overrides(self.dir)
        self.assertEqual(o.scan(now=0), 1)
        self.assertEqual(o.url("af83f3"), "/api/live_track_aircraft/picture/af83f3.png?v=1700000000")

    def test_case_does_not_matter(self):
        self.put("AF83F3.PNG")
        o = pictures.Overrides(self.dir); o.scan(now=0)
        self.assertTrue(o.url("AF83F3").startswith("/api/live_track_aircraft/picture/af83f3.png?v="))

    def test_every_kind(self):
        for i, ext in enumerate(("png", "jpg", "jpeg", "webp", "gif", "svg")):
            self.put("a0000%d.%s" % (i, ext))
        o = pictures.Overrides(self.dir)
        self.assertEqual(o.scan(now=0), 6)

    def test_ignores_what_is_not_a_picture_for_a_hex(self):
        for name in ("af83f3.txt", "af83f.png", "af83f3x.png", "zz83f3.png", "notes.png", "af83f3", ".png"):
            self.put(name)
        os.mkdir(os.path.join(self.dir, "adfdf8.png"))      # a folder, not a file
        self.put("adfdf9.png", data=b"")                     # empty
        self.put("a00001.png", data=b"x" * (pictures.MAX_BYTES + 1))
        o = pictures.Overrides(self.dir)
        self.assertEqual(o.scan(now=0), 0)

    def test_one_per_hex_the_first_by_name(self):
        self.put("af83f3.gif"); self.put("af83f3.png")
        o = pictures.Overrides(self.dir); o.scan(now=0)
        self.assertIn("af83f3.gif?", o.url("af83f3"))

    def test_a_replaced_file_is_a_new_url(self):
        self.put("af83f3.png", mtime=1_700_000_000)
        o = pictures.Overrides(self.dir); o.scan(now=0)
        first = o.url("af83f3")
        self.put("af83f3.png", data=b"y" * 20, mtime=1_700_000_500)
        o.scan(now=100)
        self.assertNotEqual(o.url("af83f3"), first)

    def test_a_removed_file_is_gone_after_the_next_scan(self):
        p = self.put("af83f3.png")
        o = pictures.Overrides(self.dir); o.scan(now=0)
        os.remove(p); o.scan(now=100)
        self.assertIsNone(o.url("af83f3"))

    def test_no_folder_no_pictures(self):
        o = pictures.Overrides(os.path.join(self.dir, "missing"))
        self.assertEqual(o.scan(now=0), 0)
        self.assertIsNone(o.url("af83f3"))

    def test_unknown_or_blank_hex(self):
        self.put("af83f3.png")
        o = pictures.Overrides(self.dir); o.scan(now=0)
        for h in (None, "", "adfdf8"):
            self.assertIsNone(o.url(h))

    def test_rescan_once_a_minute(self):
        o = pictures.Overrides(self.dir)
        self.assertTrue(o.due(0))
        o.scan(now=1000)
        self.assertFalse(o.due(1059))
        self.assertTrue(o.due(1060))


class Apply(unittest.TestCase):
    def test_upright_and_marked(self):
        out = {"entity_picture": "/icon", "icon_rotatable": True, "icon_rotation_deg": 35, "icon_rotation_basis": "course"}
        pictures.apply(out, "/api/live_track_aircraft/picture/af83f3.png?v=1")
        self.assertEqual(out, {"entity_picture": "/api/live_track_aircraft/picture/af83f3.png?v=1",
                               "picture_source": "override", "icon_rotatable": False})

    def test_no_picture_changes_nothing(self):
        out = {"entity_picture": "/icon", "icon_rotation_deg": 35}
        self.assertEqual(pictures.apply(dict(out), None), out)


class Resolve(Folder):
    def test_serves_the_file_with_its_type(self):
        p = self.put("AF83F3.Png")
        self.assertEqual(pictures.resolve(self.dir, "af83f3.png"), (p, "image/png"))
        self.assertEqual(pictures.resolve(self.dir, "AF83F3.PNG"), (p, "image/png"))

    def test_refuses_anything_else(self):
        self.put("af83f3.png")
        outside = os.path.join(os.path.dirname(self.dir), "a00000.png")
        for name in ("../a00000.png", "..\\a00000.png", "af83f3.svg", "af83f3.exe", "af83f3", "", "secrets.yaml",
                     "af83f3.png/../../x", "%2e%2e/a00000.png"):
            self.assertIsNone(pictures.resolve(self.dir, name), name)
        self.assertFalse(os.path.exists(outside))

    def test_empty_or_huge_is_not_served(self):
        self.put("a00001.png", data=b"")
        self.put("a00002.png", data=b"x" * (pictures.MAX_BYTES + 1))
        self.assertIsNone(pictures.resolve(self.dir, "a00001.png"))
        self.assertIsNone(pictures.resolve(self.dir, "a00002.png"))


class Wired(unittest.TestCase):
    """The coordinator, the entity and the view each carry their part."""

    def read(self, name):
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(here, "custom_components", "live_track_aircraft", name), encoding="utf-8") as fh:
            return fh.read()

    def test_coordinator_scans_off_the_loop_and_applies(self):
        src = self.read("coordinator.py")
        self.assertIn("async_add_executor_job(self.pictures.scan)", src)
        self.assertIn("apply_picture(out, own.url(obs.identity)", src)
        # after the icon picture is chosen, so the user's wins
        self.assertLess(src.index("lights=lights)"), src.index("apply_picture(out"))

    def test_entity_exposes_picture_source(self):
        self.assertIn('"picture_source",', self.read("geo_location.py"))

    def test_view_registered_and_locked_down(self):
        src = self.read("web.py")
        self.assertIn("hass.http.register_view(AircraftPictureView())", src)
        self.assertIn("Content-Security-Policy", src)
        self.assertIn("pictures.resolve, folder, name", src)


if __name__ == "__main__":
    unittest.main()
