"""A download session for GitHub release assets (route and airport files).

! WHY NOT HA'S SHARED SESSION (measured 2026-10-23): GitHub answers a release
download with a 302 whose Content-Security-Policy header is 9,242 bytes, and
aiohttp refuses any header line over 8,190 by default ("Got more than 8190
bytes when reading"). HA's shared session cannot be given other limits, so
every route and airport download failed from that afternoon, leaving the
installed files in place until they expired. This session raises both limits
to 32,768 and shares HA's connector (closing it does not close the connector).
The caller closes it after each check.
"""
from __future__ import annotations

MAX_HEADER_BYTES = 32768


def release_session(hass):
    from homeassistant.helpers.aiohttp_client import async_create_clientsession  # noqa: PLC0415

    return async_create_clientsession(hass, auto_cleanup=False,
                                      max_line_size=MAX_HEADER_BYTES,
                                      max_field_size=MAX_HEADER_BYTES)
