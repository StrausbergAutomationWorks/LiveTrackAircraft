"""Load the component's PURE modules without Home Assistant.

A package shell stands in for custom_components.live_track_aircraft so the
relative imports resolve without running __init__.py, which needs HA. Only
modules that import nothing from homeassistant can be loaded this way:
const, icons, airframe, map_keys, aircraft, sources.base, sources.adsb.
The coordinator, the platform and the config flow are checked on the box
after a deploy, not here.
"""
import importlib
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
COMP = os.path.join(REPO, "custom_components", "live_track_aircraft")

for _pkg, _path in (("lta", COMP), ("lta.sources", os.path.join(COMP, "sources"))):
    if _pkg not in sys.modules:
        _m = types.ModuleType(_pkg)
        _m.__path__ = [_path]
        sys.modules[_pkg] = _m


def load(name: str):
    """lta.<name>, e.g. load("icons") or load("sources.adsb")."""
    return importlib.import_module("lta." + name)


def source(relpath: str) -> str:
    with open(os.path.join(COMP, relpath), encoding="utf-8") as fh:
        return fh.read()
