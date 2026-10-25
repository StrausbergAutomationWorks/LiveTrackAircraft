"""The EnforcementAircraft list in this integration (backlog 299).

! EVERY SOURCED LISTED AIRCRAFT FLASHES RED/BLUE (Lee 2026-10-24 02:13): the
glow over its owner-class fill, so a listed state or local police aircraft
loses the blue wig-wag. Police not on the list keep it. A detected_unconfirmed
entry is left to the owner rules (Lee 17:00). The decision is the
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


def watched_hexes(hass) -> list[str]:
    """What the nationwide watch (watch.py) asks for besides the presidential airframes.

    ! POLICE NOT ON THE LIST ARE NOT WATCHED NATIONWIDE (Lee 2026-10-24 20:55;
    Enforcement SSOT section 3.5 step 2): the list's sourced and detected
    entries, plus every federal law-enforcement registrant in the FAA table.
    A state or local police aircraft not on the list is drawn only inside the
    circle. Measured that evening: 1,160 law-enforcement hexes in the box's
    table, 871 of them state and local and not on the list.
    """
    hexes = set(REGISTRY.federal_law_enforcement_hexes())
    reader = hass.data.get(el.STORE_KEY)
    if reader is not None:
        hexes |= reader.hexes(el.SOURCED, el.DETECTED)
    return sorted(hexes)
