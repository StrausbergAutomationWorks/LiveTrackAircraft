"""The EnforcementAircraft list in this integration (backlog 299).

! EVERY SOURCED LISTED AIRCRAFT FLASHES RED/BLUE (Lee 2026-10-24 02:13): the
glow over its owner-class fill, so a listed state or local police aircraft
loses the blue wig-wag. Police not on the list keep it. A detected_unconfirmed
entry is left to the owner rules (Lee 17:00). An ice_air_charter entry
(backlog 313, Lee 2026-10-29) takes the library's steady charter glow, not
the flash: the airframe flies other work too. The decision is the
coordinator's; this module only holds the reader and its session.

! THE READER IS saw_livetrack.enforcement_list, ONE PER INSTANCE, shared with
Live Track Enforcement Aircraft under its SAW-neutral key, so whichever starts
first builds it and the other finds it. Its cache is
.storage/saw_enforcementaircraft.json.

! ITS OWN SESSION, under the library's SESSION_KEY with the raised header
limits (05_SHARED_LESSONS.md B17). ! NEVER release_session.py, the route
downloader, its cache or any token of FiledRoutesDB (Lee, 2026-10-23): the
list is not linked to that service in any way. As with the release session,
the session is HA's to close at shutdown.
"""
from __future__ import annotations

from datetime import timedelta

from saw_livetrack import enforcement_list as el

from .registrations import REGISTRY

# Asked every hour; the reader itself holds a good check for 6 h, a failed one for 15 min.
TICK = timedelta(hours=1)


def list_session(hass):
    session = hass.data.get(el.SESSION_KEY)
    if session is None or session.closed:
        from homeassistant.helpers.aiohttp_client import async_create_clientsession  # noqa: PLC0415

        session = async_create_clientsession(hass, **el.SESSION_KWARGS)
        hass.data[el.SESSION_KEY] = session
    return session


async def async_setup_list(hass) -> el.EnforcementList:
    """The instance's reader; the cached list loaded the first time it is made."""
    first = el.STORE_KEY not in hass.data
    reader = el.shared(hass.data, hass.config.path(".storage", el.CACHE_NAME))
    if first:
        await hass.async_add_executor_job(reader.load_cache)
    return reader


async def async_refresh_list(hass, reader: el.EnforcementList) -> str:
    return await reader.refresh(list_session(hass), hass.async_add_executor_job)


def federal_registrants() -> dict[str, dict[str, str]]:
    """{hex: {registration, operator, operator_short}} for every FEDERAL law-enforcement registrant.

    ! THE NATIONWIDE WATCH MOVED TO LIVE TRACK ENFORCEMENT AIRCRAFT (backlog 297). It watched the list's
    sourced and detected entries plus these registrants (Lee 2026-10-24 20:55, 305 hexes with the
    presidential airframes), so a registration newer than the list's build stayed watched (measured
    that evening: 15 DHS registrations on the box's table and not on the list). This integration holds
    the FAA table and the companion does not, so the registrants are PUBLISHED in hass.data under the
    library's SAW-neutral key (enforcement_list.FEDERAL_KEY) for whoever draws the list: found, not
    built. Police not on the list stay inside the circle.
    """
    out: dict[str, dict[str, str]] = {}
    for h in REGISTRY.federal_law_enforcement_hexes():
        row = REGISTRY.lookup(h) or {}
        out[h] = {k: row[k] for k in ("registration", "operator", "operator_short") if row.get(k)}
    return out


def publish_federal(hass) -> int:
    """Put the registrants in hass.data for the companion; called after each load of the table."""
    found = federal_registrants()
    hass.data[el.FEDERAL_KEY] = found
    return len(found)
