"""The release-download session (2026-10-23, corrected 2026-10-24): header
limits above GitHub's 9,242-byte Content-Security-Policy line, made ONCE per
HA instance and closed by HA (never by us), used by both downloaders."""
import sys
import types
import unittest

from _load import load, source

rs = load("release_session")


class Session(unittest.TestCase):
    def test_limits_and_cleanup(self):
        seen = {}
        fake = types.ModuleType("homeassistant.helpers.aiohttp_client")

        class _S:
            closed = False

        def create(hass, **kw):
            seen.update(kw)
            seen["calls"] = seen.get("calls", 0) + 1
            return _S()
        fake.async_create_clientsession = create

        class _Hass:
            data = {}
        hass = _Hass()
        mods = {"homeassistant": types.ModuleType("homeassistant"),
                "homeassistant.helpers": types.ModuleType("homeassistant.helpers"),
                "homeassistant.helpers.aiohttp_client": fake}
        saved = {k: sys.modules.get(k) for k in mods}
        sys.modules.update(mods)
        try:
            first = rs.release_session(hass)
            self.assertIs(rs.release_session(hass), first)       # made once
            first.closed = True
            self.assertIsNot(rs.release_session(hass), first)    # remade if HA closed it
        finally:
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
        self.assertEqual(seen["calls"], 2)
        self.assertNotIn("auto_cleanup", seen)               # HA closes it at shutdown
        for k in ("max_line_size", "max_field_size"):
            self.assertGreater(seen[k], 9242, k)

    def test_downloaders_use_it_and_never_close_it(self):
        for name in ("route_download.py", "airport_download.py"):
            with self.subTest(name=name):
                src = source(name)
                self.assertNotIn("async_get_clientsession", src)
                self.assertIn("session = release_session(hass)", src)
                self.assertNotIn("session.close()", src)


if __name__ == "__main__":
    unittest.main()
