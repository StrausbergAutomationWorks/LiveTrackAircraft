"""The release-download session (2026-10-23): header limits above GitHub's
9,242-byte Content-Security-Policy line, not auto-closed by HA, and both
downloaders use it and close it."""
import sys
import types
import unittest

from _load import load, source

rs = load("release_session")


class Session(unittest.TestCase):
    def test_limits_and_cleanup(self):
        seen = {}
        fake = types.ModuleType("homeassistant.helpers.aiohttp_client")

        def create(hass, **kw):
            seen.update(kw, hass=hass)
            return "session"
        fake.async_create_clientsession = create
        mods = {"homeassistant": types.ModuleType("homeassistant"),
                "homeassistant.helpers": types.ModuleType("homeassistant.helpers"),
                "homeassistant.helpers.aiohttp_client": fake}
        saved = {k: sys.modules.get(k) for k in mods}
        sys.modules.update(mods)
        try:
            self.assertEqual(rs.release_session("H"), "session")
        finally:
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
        self.assertEqual(seen["hass"], "H")
        self.assertIs(seen["auto_cleanup"], False)
        for k in ("max_line_size", "max_field_size"):
            self.assertGreater(seen[k], 9242, k)

    def test_downloaders_use_it_and_close_it(self):
        for name in ("route_download.py", "airport_download.py"):
            with self.subTest(name=name):
                src = source(name)
                self.assertNotIn("async_get_clientsession", src)
                self.assertIn("session = release_session(hass)", src)
                self.assertIn("await session.close()", src)


if __name__ == "__main__":
    unittest.main()
