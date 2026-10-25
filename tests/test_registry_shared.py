"""registrations.py over saw_livetrack.faa_registry (backlog 300, saw-livetrack 0.2.15): one registry per instance,
shared with Live Track Enforcement Aircraft; REGISTRY and OWNERS follow it; the old names still answer."""
import asyncio
import json
import os
import tempfile
import unittest

from _load import load

reg = load("registrations")
from saw_livetrack import faa_registry as fr  # noqa: E402


class Hass:
    def __init__(self, folder):
        self.data = {}
        self.folder = folder
        self.config = self

    def path(self, *parts):
        return os.path.join(self.folder, *parts)

    async def async_add_executor_job(self, func, *args):
        return func(*args)


class Shared(unittest.TestCase):
    def setUp(self):
        self.before = reg._current

    def tearDown(self):
        reg._current.owners.close()
        reg._current = self.before

    def test_before_setup_every_lookup_is_none(self):
        reg._current = fr.FaaRegistry("")
        self.assertIsNone(reg.lookup_government("A00001"))
        self.assertIsNone(reg.lookup_owner("A00001"))
        self.assertEqual(reg.REGISTRY.federal_law_enforcement_hexes(), [])

    def test_load_binds_the_instances_registry(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".storage"))
            with open(os.path.join(d, ".storage", fr.CACHE_NAME), "w", encoding="utf-8") as fh:
                json.dump({"schema": fr.SCHEMA, "aircraft": {"A00004": ["N809EM", "DEPARTMENT OF HOMELAND SECURITY", "DC"]}}, fh)
            hass = Hass(d)
            self.assertEqual(asyncio.run(reg.async_load_registry(hass)), 1)
            shared = hass.data[fr.STORE_KEY]
            self.assertIs(reg.current(), shared)
            self.assertEqual(reg.lookup_government("a00004")["operator_short"], "DHS")
            self.assertEqual(reg.REGISTRY.federal_law_enforcement_hexes(), ["a00004"])
            self.assertIs(reg.REGISTRY.size, shared.gov.size)
            self.assertEqual(reg.OWNERS.count, 0)
            # the companion finds the same registry, and what it loads is what this integration sees
            self.assertIs(fr.shared(hass.data, "elsewhere"), shared)
            shared.owners.close()

    def test_paths_and_names(self):
        h = Hass("/cfg")
        self.assertEqual(reg.owner_db_path(h), os.path.join("/cfg", ".storage", "saw_faa_owners.sqlite"))
        self.assertIs(reg.GovRegistry, fr.GovRegistry)
        self.assertIs(reg.operator_short, fr.operator_short)
        self.assertIs(reg.categorise, fr.categorise)


if __name__ == "__main__":
    unittest.main()
