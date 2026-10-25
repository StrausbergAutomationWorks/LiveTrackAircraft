"""The FAA registry in Live Track Aircraft.

! SINCE 2026-10-25 THE CODE IS saw_livetrack.faa_registry (saw-livetrack 0.2.15, backlog 300; Lee 01:42, decision
C: "Use option1"), ONE registry per instance, shared with Live Track Enforcement Aircraft: one table, one 73 MB
download however many aircraft integrations are installed. The pure code was moved there verbatim from this file
at 2aa4823 (its history, the government table's rules and every measurement behind them, is in that commit and in
the library); its tests are the library's, and this integration's own tests still run against these names.

This module keeps the names the rest of the integration and its tests use:
  * the library's functions, classes and constants, re-exported;
  * REGISTRY and OWNERS: stable handles on the INSTANCE's tables. They exist from import, so a module that bound
    `from .registrations import REGISTRY` keeps working; before setup they answer from an empty registry (every
    lookup None), after it from the shared one;
  * lookup_government / lookup_owner, async_load_registry / async_refresh_registry, and the .storage paths.

! The caches keep their SAW-neutral names (.storage/saw_faa_gov_aircraft.json, saw_faa_owners.sqlite): the tables
already on an instance are read as they are.
"""

from __future__ import annotations

import logging

from saw_livetrack import faa_registry as _fr
from saw_livetrack.faa_registry import (  # noqa: F401 - re-exported for this integration and its tests
    CACHE_NAME,
    DBF_INTERESTING,
    DBF_LADD,
    DBF_MILITARY,
    DBF_PIA,
    EXCLUDES,
    FAA_URL,
    LAW_ENFORCEMENT,
    LEGACY_CACHE_NAME,
    OWNER_DB_NAME,
    REFRESH_DAYS,
    SCHEMA,
    US_HEX_MAX,
    US_HEX_MIN,
    GovRegistry,
    OwnerRegistry,
    _FEDERAL_OPERATOR_ALLOWLIST,
    build_owner_db,
    categorise,
    from_feed_flags,
    is_us_hex,
    location_is_us,
    needs_refresh,
    operator_short,
    parse_faa_archive,
    prettify_owner,
)

_LOGGER = logging.getLogger(__name__)


def cache_path(hass) -> str:
    return hass.config.path(".storage", CACHE_NAME)


def legacy_cache_path(hass) -> str:
    return hass.config.path(".storage", LEGACY_CACHE_NAME)


def owner_db_path(hass) -> str:
    return hass.config.path(".storage", OWNER_DB_NAME)


# The instance's registry once setup has run; until then an empty one, so every lookup says None.
_current: _fr.FaaRegistry = _fr.FaaRegistry("")


class _Current:
    """A stable handle on one part of the instance's registry ("gov" or "owners")."""

    __slots__ = ("_part",)

    def __init__(self, part: str) -> None:
        object.__setattr__(self, "_part", part)

    def __getattr__(self, name):
        return getattr(getattr(_current, self._part), name)


REGISTRY = _Current("gov")
OWNERS = _Current("owners")


def current() -> _fr.FaaRegistry:
    return _current


def lookup_government(hex_code):
    """A government registrant by Mode S hex, or None. Never touches disk."""
    return _current.lookup_government(hex_code)


def lookup_owner(hex_code):
    """Registered owner for a Mode S address, or None.

    ! This is the TITLE HOLDER, which is often not the operator (N964AV is "Avianca" to adsbdb and "Bank of
    Utah Trustee" to the FAA): prefer an operator name from any source that has one.
    """
    return _current.lookup_owner(hex_code)


def _bind(hass) -> _fr.FaaRegistry:
    global _current
    _current = _fr.shared(hass.data, hass.config.path(".storage"))
    return _current


async def async_load_registry(hass, latitude=None, longitude=None) -> int:
    """Load the cached tables into the instance's registry (once per instance). Returns the government count."""
    return await _bind(hass).load(hass.async_add_executor_job)


async def async_refresh_registry(hass, latitude=None, longitude=None, force: bool = False) -> bool:
    """Refresh from the FAA when the cache is stale. True only when a new table was installed.

    Best-effort: a failure keeps the tables in use. A second integration asking at the same time waits on the
    registry's lock and then finds the cache fresh.
    """
    from homeassistant.helpers.aiohttp_client import async_get_clientsession  # noqa: PLC0415

    result = await _bind(hass).refresh(async_get_clientsession(hass), hass.async_add_executor_job, force)
    if result.startswith("failed"):
        _LOGGER.debug("FAA registry refresh: %s", result)
    return result.startswith("updated")
