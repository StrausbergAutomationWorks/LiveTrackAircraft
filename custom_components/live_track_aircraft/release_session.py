"""A download session for GitHub release assets (route and airport files).

! WHY NOT HA'S SHARED SESSION (measured 2026-10-23): GitHub answers a release
download with a 302 whose Content-Security-Policy header is 9,242 bytes, and
aiohttp refuses any header line over 8,190 by default ("Got more than 8190
bytes when reading"). HA's shared session cannot be given other limits, so
every route and airport download failed from that afternoon, leaving the
installed files in place until they expired. This session raises both limits
to 32,768 and shares HA's connector.
! ONE SESSION, NEVER CLOSED BY US (2026-10-24): a session from
async_create_clientsession is HA's to close - HA replaces its close() with a
warning ("closes the Home Assistant aiohttp session"), so closing it after
each check did nothing and left one behind per check (442f4ae). It is made
once per HA instance, kept in hass.data, and HA closes it at shutdown.
"""
from __future__ import annotations

MAX_HEADER_BYTES = 32768
DATA_KEY = "live_track_aircraft_release_session"


def release_session(hass):
    session = hass.data.get(DATA_KEY)
    if session is None or session.closed:
        from homeassistant.helpers.aiohttp_client import async_create_clientsession  # noqa: PLC0415

        session = async_create_clientsession(hass, max_line_size=MAX_HEADER_BYTES,
                                             max_field_size=MAX_HEADER_BYTES)
        hass.data[DATA_KEY] = session
    return session
