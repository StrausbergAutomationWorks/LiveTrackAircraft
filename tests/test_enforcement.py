"""The EnforcementAircraft list here (backlog 299): every sourced listed aircraft glows red/blue,
police not on the list keep the wig-wag, a detection is left to the owner rules, and the reader
never touches anything of FiledRoutesDB."""
import asyncio
import json
import os
import tempfile
import unittest

from _load import load, source

icons = load("icons")
enf = load("enforcement")
el = enf.el


class Hass:
    def __init__(self, folder):
        self.data = {}
        self.folder = folder
        self.config = self

    def path(self, *parts):
        return os.path.join(self.folder, *parts)

    async def async_add_executor_job(self, func, *args):
        return func(*args)


def listing():
    return json.dumps({"name": "EnforcementAircraft", "schema": 1, "built": "2026-10-24T04:04:22Z",
                       "aircraft": [{"hex": "a1b2c3", "status": "sourced", "agency": "TX DPS"},
                                    {"hex": "abc123", "status": "detected_unconfirmed"}]}).encode()


class Reader(unittest.TestCase):
    def test_one_reader_loaded_from_the_cache(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".storage"))
            with open(os.path.join(d, ".storage", el.CACHE_NAME), "wb") as fh:
                fh.write(listing())
            hass = Hass(d)
            a = asyncio.run(enf.async_setup_list(hass))
            self.assertTrue(a.is_sourced("A1B2C3"))
            self.assertFalse(a.is_sourced("abc123"))
            self.assertEqual(a.cache_path, os.path.join(d, ".storage", "saw_enforcementaircraft.json"))
            self.assertIs(asyncio.run(enf.async_setup_list(hass)), a)
            self.assertIs(hass.data[el.STORE_KEY], a)


class Watched(unittest.TestCase):
    """Police not on the list are not watched nationwide (Lee 2026-10-24 20:55)."""

    def test_list_plus_federal_registrants(self):
        class Reg:
            def federal_law_enforcement_hexes(self):
                return ["a00004", "a1b2c3"]
        old, enf.REGISTRY = enf.REGISTRY, Reg()
        try:
            hass = Hass(tempfile.gettempdir())
            self.assertEqual(enf.watched_hexes(hass), ["a00004", "a1b2c3"])          # no list yet
            reader = el.EnforcementList(os.path.join(tempfile.gettempdir(), "x.json"))
            reader._install(json.dumps({"name": "EnforcementAircraft", "schema": 1, "aircraft": [
                {"hex": "a1b2c3", "status": "sourced"}, {"hex": "abc123", "status": "detected_unconfirmed"},
                {"hex": "def456", "status": "cleared"}]}).encode())
            hass.data[el.STORE_KEY] = reader
            self.assertEqual(enf.watched_hexes(hass), ["a00004", "a1b2c3", "abc123"])  # cleared stays out
        finally:
            enf.REGISTRY = old

    def test_wired(self):
        self.assertIn("WatchList(lambda: watched_hexes(hass))", source("__init__.py"))
        self.assertNotIn("WatchList(REGISTRY.law_enforcement_hexes)", source("__init__.py"))


class Lights(unittest.TestCase):
    def test_picture_of_a_listed_police_aircraft(self):
        url = icons.picture_url("a7", "police", 0.78, lights=icons.LIGHTS_GLOW)
        self.assertIn("t=police", url)
        self.assertIn("l=g", url)
        self.assertIn("a=%d" % icons.ART_REV, url)
        self.assertGreaterEqual(icons.ART_REV, 11)

    def test_view_reads_every_mode(self):
        self.assertIn("icons.lights_from_query(request.query.get(\"l\"))", source("web.py"))
        self.assertEqual([icons.lights_from_query(v) for v in ("1", "g", "w", "x", None)],
                         [True, "glow", "wigwag", False, False])


class Wiring(unittest.TestCase):
    def test_coordinator_decides(self):
        src = source("coordinator.py")
        self.assertIn("lights = icons.lights_for(gov_cat)", src)
        self.assertIn("if elist is not None and elist.is_sourced(obs.identity):", src)
        self.assertIn("lights = icons.LIGHTS_GLOW", src)
        # sourced only: no detected status turns lights on or off here (Lee 2026-10-24 17:00)
        self.assertNotIn("DETECTED", src)
        self.assertNotIn("elist.status(", src)
        self.assertNotIn("elist.hexes(", src)

    def test_set_before_the_first_poll(self):
        src = source("__init__.py")
        self.assertLess(src.index("await async_setup_list(hass)"),
                        src.index("await coordinator.async_config_entry_first_refresh()"))
        self.assertIn("async_track_time_interval(hass, _check_list, LIST_TICK)", src)

    def test_own_session_never_filedroutesdb(self):
        src = source("enforcement.py")
        code = src.split('"""', 2)[2]
        for word in ("release_session", "route_download", "routes", "FiledRoutesDB", "frdb"):
            self.assertNotIn(word, code, word)
        self.assertIn("hass.data.get(el.SESSION_KEY)", code)
        self.assertIn("async_create_clientsession(hass, **el.SESSION_KWARGS)", code)
        self.assertNotIn("enforcement", source("release_session.py").lower())

    def test_sensor_line(self):
        self.assertIn('"enforcement_list": getattr(self._coordinator.enforcement_list, "summary", None)',
                      source("sensor.py"))

    def test_manifest_pin(self):
        req = json.loads(source("manifest.json"))["requirements"]
        self.assertIn("saw-livetrack[zones]>=0.2.12,<0.3", req)


if __name__ == "__main__":
    unittest.main()
