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


class Federal(unittest.TestCase):
    """The nationwide watch moved to the companion (backlog 297): the federal registrants are published
    for it under the library's SAW-neutral key, and nothing here watches the list nationwide."""

    def test_published_under_the_neutral_key(self):
        class Reg:
            def federal_law_enforcement_hexes(self):
                return ["a00004", "a1b2c3"]

            def lookup(self, h):
                return {"a00004": {"registration": "N809EM", "operator": "Department of Homeland Security",
                                   "operator_short": "DHS", "operator_category": "Federal law enforcement"},
                        }.get(h)
        old, enf.REGISTRY = enf.REGISTRY, Reg()
        try:
            hass = Hass(tempfile.gettempdir())
            self.assertEqual(enf.publish_federal(hass), 2)
            self.assertEqual(el.FEDERAL_KEY, "saw_federal_law_enforcement")
            self.assertEqual(hass.data[el.FEDERAL_KEY], {
                "a00004": {"registration": "N809EM", "operator": "Department of Homeland Security",
                           "operator_short": "DHS"},
                "a1b2c3": {}})
        finally:
            enf.REGISTRY = old

    def test_wired(self):
        src = source("__init__.py")
        self.assertIn("WatchList(coordinator.poll)", src)
        self.assertIn("publish_federal(hass)", src)
        self.assertNotIn("watched_hexes", src)
        self.assertNotIn("watched_hexes", source("enforcement.py"))


class Lights(unittest.TestCase):
    def test_picture_of_a_listed_police_aircraft(self):
        url = icons.picture_url("a7", "police", 0.78, lights=icons.LIGHTS_GLOW)
        self.assertIn("t=police", url)
        self.assertIn("l=g", url)
        self.assertIn("a=%d" % icons.ART_REV, url)
        self.assertGreaterEqual(icons.ART_REV, 11)

    def test_view_reads_every_mode(self):
        self.assertIn("icons.lights_from_query(request.query.get(\"l\"))", source("web.py"))
        self.assertEqual([icons.lights_from_query(v) for v in ("1", "g", "w", "c", "x", None)],
                         [True, "glow", "wigwag", "charter", False, False])

    def test_picture_of_a_charter(self):
        url = icons.picture_url("a320", "default", 0.85, lights=icons.LIGHTS_CHARTER)
        self.assertIn("l=c", url)
        self.assertNotIn("l=g", url)


class Wiring(unittest.TestCase):
    def test_coordinator_decides(self):
        src = source("coordinator.py")
        self.assertIn("lights = icons.lights_for(gov_cat)", src)
        self.assertIn("if elist is not None and elist.is_sourced(obs.identity):", src)
        self.assertIn("lights = icons.LIGHTS_GLOW", src)
        # sourced only: no detected status turns lights on or off here (Lee 2026-10-24 17:00).
        # Scoped to the lights block since 2026-10-25: the cap (cap.py) exempts detected
        # hexes from being DROPPED, which is not a lights decision.
        start = src.index("lights = icons.lights_for(gov_cat)")
        block = src[start:src.index('out["entity_picture"]', start)]
        self.assertNotIn("DETECTED", block)
        self.assertNotIn("elist.hexes(", block)
        # ! backlog 313 (Lee 2026-10-29): the ONE list status read in the lights block is the charter's.
        self.assertEqual(block.count("elist.status("), 1)
        self.assertIn("elif elist is not None and elist.status(obs.identity) == CHARTER:", block)
        self.assertIn("lights = icons.LIGHTS_CHARTER", block)
        self.assertLess(block.index("lights = icons.LIGHTS_GLOW"), block.index("lights = icons.LIGHTS_CHARTER"))
        # and the only other use of a list status is the cap's exemption
        self.assertEqual(src.count("elist.status("), 2)
        self.assertIn("elist.status(h) in WATCHED", src)

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

    def test_charter_label_comes_first(self):
        # backlog 313 (Lee 2026-10-29 01:18): _marker_label and its helpers, compiled from the source and called.
        import ast
        import re as _re
        from types import SimpleNamespace
        from saw_livetrack import enforcement_list as el
        src = source("coordinator.py")
        tree = ast.parse(src)
        keep = [n for n in tree.body if (isinstance(n, ast.FunctionDef) and n.name in ("_marker_label", "_shorten"))
                or (isinstance(n, ast.Assign) and any(getattr(t, "id", "") in ("_LOOKS_LIKE_REGISTRATION", "MAX_LABEL_CHARS")
                                                       for t in n.targets))]
        ns = {"re": _re, "CHARTER": el.CHARTER, "CHARTER_LABEL": el.CHARTER_LABEL, "Any": object, "Observation": object}
        exec(compile(ast.Module(body=keep, type_ignores=[]), "coordinator.py", "exec"), ns)
        obs = SimpleNamespace(callsign="GXA301", identity="a2c4e0")
        self.assertEqual(ns["_marker_label"](obs, {"enforcement_status": "ice_air_charter"}), "ICE Air Charter?")
        self.assertEqual(ns["_marker_label"](obs, {}), "GXA301")
        self.assertEqual(ns["_marker_label"](obs, {"enforcement_status": "sourced"}), "GXA301")
        start = src.index("elif elist is not None and elist.status(obs.identity) == CHARTER:")
        self.assertIn('out["enforcement_status"] = CHARTER', src[start:src.index('out["entity_picture"]', start)])

    def test_manifest_pin(self):
        req = json.loads(source("manifest.json"))["requirements"]
        self.assertIn("saw-livetrack[zones]>=0.2.17,<0.3", req)   # the airline table and airline_short, 0.2.17

    def test_the_lists_agency_when_the_registry_gives_none(self):
        # backlog 300: the registry's short name first, the list's agency for a sourced aircraft without one
        src = source("coordinator.py")
        i = src.index('if not out.get("operator_short") and elist is not None and elist.is_sourced(obs.identity):')
        self.assertGreater(i, src.index('for k in ("operator_short", "identified_by"):'))
        self.assertGreater(i, src.index("for k, v in feed_extra.items():"))
        self.assertIn('out["operator_short"] = listed.agency', src)

    def test_the_circle_is_asked_as_this_entry(self):
        # 0.2.14: the answer is kept under this entry's name so a circle inside it costs no request
        self.assertIn("consumer=self.claim_key", source("coordinator.py"))
        self.assertIn("consumer=consumer)", source("sources/adsb.py"))


if __name__ == "__main__":
    unittest.main()
