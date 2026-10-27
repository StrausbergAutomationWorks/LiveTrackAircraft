"""The shipped LiveTrackMapCard (backlog 291): offered at setup, untouched by an
unload, withdrawn only by the domain's LAST entry.

__init__.py needs Home Assistant, which the suite does not have, so its three
entry functions are compiled out of the source on their own and run against
stand-ins for every name they use. What is checked is the integration's own
wiring; shared_map_card.py and saw_livetrack.map_card carry their own tests in
LiveTrackCore, and the row on the box is measured after a deploy.
"""
import __future__
import ast
import asyncio
import builtins
import json
import os
import re
import unittest
from pathlib import Path
from unittest import mock

from _load import COMP, source

DOMAIN = "live_track_aircraft"
HERE = Path(COMP)
FUNCS = ("async_setup_entry", "async_unload_entry", "async_remove_entry")


def _compile_entry_functions():
    """The three functions, compiled from __init__.py, and the free names they read."""
    tree = ast.parse(source("__init__.py"))
    defs = [n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name in FUNCS]
    assert sorted(d.name for d in defs) == sorted(FUNCS), [d.name for d in defs]
    mod = ast.Module(body=defs, type_ignores=[])
    code = compile(mod, "__init__.py", "exec",
                   flags=__future__.annotations.compiler_flag, dont_inherit=True)
    free = set()
    for d in defs:
        local = {a.arg for a in d.args.args}
        for n in ast.walk(d):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n is not d:
                local.add(n.name)
                local.update(a.arg for a in n.args.args)
            elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                local.add(n.id)
        for n in ast.walk(d):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id not in local:
                free.add(n.id)
    return code, free


CODE, FREE = _compile_entry_functions()
AWAITED = {"async_offer_map_card", "async_withdraw_map_card", "async_setup_list",
           "async_load_registry"}


def _close(coro, *_a, **_k):
    """Background tasks are not run: close any coroutine so none is left unawaited."""
    if asyncio.iscoroutine(coro):
        coro.close()


class _World:
    """Stand-ins for hass, an entry and every module-level name the functions read."""

    def __init__(self, entries=("e1",)):
        self.calls = []
        ns = {"__builtins__": builtins}
        for name in FREE:
            if hasattr(builtins, name):
                continue
            ns[name] = mock.AsyncMock() if name in AWAITED else mock.MagicMock()
        ns["DOMAIN"] = DOMAIN
        ns["HERE"] = HERE
        ns["PLATFORMS"] = ["geo_location", "sensor"]
        ns["async_offer_map_card"].side_effect = lambda *a: self.calls.append("offer")
        ns["async_withdraw_map_card"].side_effect = lambda *a: self.calls.append("withdraw")
        coord = mock.MagicMock()
        coord.async_config_entry_first_refresh = mock.AsyncMock(
            side_effect=lambda: self.calls.append("first_refresh"))
        ns["AircraftCoordinator"] = mock.MagicMock(return_value=coord)
        self.coordinator = coord
        exec(CODE, ns)
        self.ns = ns

        hass = mock.MagicMock()
        hass.data = {}
        hass.async_create_background_task = mock.MagicMock(side_effect=_close)
        hass.config_entries.async_forward_entry_setups = mock.AsyncMock(return_value=True)
        hass.config_entries.async_unload_platforms = mock.AsyncMock(return_value=True)
        self.entries = [self._entry(eid) for eid in entries]
        hass.config_entries.async_entries = mock.MagicMock(
            side_effect=lambda d=None: list(self.entries) if d == DOMAIN else [])
        self.hass = hass

    @staticmethod
    def _entry(eid):
        e = mock.MagicMock()
        e.entry_id = eid
        e.data = {"latitude": 41.9, "longitude": -87.9}
        e.options = {}
        return e

    def run(self, name, *args):
        return asyncio.run(self.ns[name](*args))


class MapCardAdoption(unittest.TestCase):

    def test_setup_offers_the_card_before_the_first_refresh(self):
        w = _World()
        self.assertTrue(w.run("async_setup_entry", w.hass, w.entries[0]))
        offer = w.ns["async_offer_map_card"]
        offer.assert_awaited_once_with(w.hass, DOMAIN, HERE / "frontend")
        self.assertEqual(w.calls, ["offer", "first_refresh"])
        w.ns["async_withdraw_map_card"].assert_not_called()

    def test_unload_neither_offers_nor_withdraws(self):
        w = _World()
        w.hass.data[DOMAIN] = {"e1": w.coordinator}
        self.assertTrue(w.run("async_unload_entry", w.hass, w.entries[0]))
        w.ns["async_offer_map_card"].assert_not_called()
        w.ns["async_withdraw_map_card"].assert_not_called()
        self.assertEqual(w.calls, [])

    def test_removing_the_last_entry_withdraws(self):
        w = _World(entries=("e1",))
        w.run("async_remove_entry", w.hass, w.entries[0])
        w.ns["async_withdraw_map_card"].assert_awaited_once_with(w.hass, DOMAIN)

    def test_removing_one_of_two_entries_does_not_withdraw(self):
        w = _World(entries=("e1", "e2"))
        w.run("async_remove_entry", w.hass, w.entries[0])
        w.ns["async_withdraw_map_card"].assert_not_called()
        w.run("async_remove_entry", w.hass, w.entries[1])
        w.ns["async_withdraw_map_card"].assert_not_called()

    def test_removing_the_last_after_the_other_went_withdraws(self):
        w = _World(entries=("e1", "e2"))
        w.entries.pop(0)            # e1 was removed earlier
        w.run("async_remove_entry", w.hass, w.entries[0])
        w.ns["async_withdraw_map_card"].assert_awaited_once_with(w.hass, DOMAIN)


class ShippedFiles(unittest.TestCase):

    def test_the_bundle_is_a_stamped_release_alone_in_its_folder(self):
        folder = HERE / "frontend"
        self.assertEqual(sorted(os.listdir(folder)), ["live-track-map-card.js"])
        with open(folder / "live-track-map-card.js", "rb") as fh:
            first = fh.readline().decode("utf-8")
        m = re.match(r"^/\*! live-track-map-card (\S+) \*/", first)
        self.assertIsNotNone(m, first[:80])
        self.assertRegex(m.group(1), r"^\d+\.\d+\.\d+\+[0-9a-f]+$")   # no prerelease

    def test_manifest_waits_for_http_and_lovelace(self):
        m = json.loads(source("manifest.json"))
        self.assertIn("http", m["dependencies"])
        self.assertIn("lovelace", m["after_dependencies"])

    def test_both_repairs_texts_in_strings_and_translations(self):
        s = json.loads(source("strings.json"))
        t = json.loads(source(os.path.join("translations", "en.json")))
        for j in (s, t):
            for key, ph in (("map_card_yaml_resource", "{url}"),
                            ("map_card_duplicate_resources", "{urls}")):
                self.assertIn(ph, j["issues"][key]["description"])
                self.assertTrue(j["issues"][key]["title"])
        self.assertEqual(s, t)


if __name__ == "__main__":
    unittest.main()
