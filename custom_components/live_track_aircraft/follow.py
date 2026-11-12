"""A user's own watch list (backlog 332): aircraft followed by Mode S hex, and flights by call sign, anywhere.
No Home Assistant import, so the tests load it.

Lee 2026-11-10 (recorded) and 2026-11-11 (go). Two fields, never one: a call sign such as ACA123 is also six hex
digits, so one mixed field could not tell which was meant. Stored as the text the user typed, so the dialog shows
it back as written; an empty field follows nothing. One bad entry refuses the whole field, as areas.py does.

! A HEX IS AN AIRFRAME; A CALL SIGN IS A FLIGHT. A call sign follows whatever aircraft broadcasts it, which is
the point for a family member's flight (UAL1234 tomorrow may be another aircraft) and the reason a fleet is
followed by hex. Identity on the map is the hex either way (entity id from the hex, as every aircraft here).

! THE COST, MEASURED 2026-11-11 (bin\\lta332_callsign_probe.txt): hexes join the shared poll's union hex round
(saw_livetrack.adsb_poll, up to 994 hexes in one request), so they cost nothing; call signs go in ONE comma-list
request a minute for the whole instance (watch.py). adsb.fi's /v2/callsign/ and adsb.lol's both answered four
call signs in one request, HTTP 200, all four found; an absent call sign answers 200 with an empty list.
"""
from __future__ import annotations

import re

ERROR_INVALID_HEXES = "invalid_follow_hexes"
ERROR_INVALID_CALLSIGNS = "invalid_follow_callsigns"
# A judgement, not a measurement: well under the 994 hexes one request carries, and a short URL for call signs.
MAX_HEXES = 100
MAX_CALLSIGNS = 100

_SPLIT = re.compile(r"[\s,;]+")
# The ICAO 24-bit address as the feeds print it. "~" (TIS-B, not an airframe) is refused: the parser skips them.
_HEX = re.compile(r"^[0-9a-f]{6}$")
# ADS-B's flight field: up to eight letters and digits, as broadcast (no dash, no space).
_CALLSIGN = re.compile(r"^[A-Z0-9]{2,8}$")


def _parse(text: str | None, pattern: re.Pattern, case, limit: int, error: str) -> tuple[list[str], str | None]:
    out: list[str] = []
    for token in _SPLIT.split((text or "").strip()):
        if not token:
            continue
        token = case(token)
        if not pattern.match(token):
            return [], error
        if token not in out:
            out.append(token)
    if len(out) > limit:
        return [], error
    return out, None


def parse_hexes(text: str | None) -> tuple[list[str], str | None]:
    """(hexes in lower case, in the order typed, each once; None), or ([], the error key)."""
    return _parse(text, _HEX, str.lower, MAX_HEXES, ERROR_INVALID_HEXES)


def parse_callsigns(text: str | None) -> tuple[list[str], str | None]:
    """(call signs in upper case, in the order typed, each once; None), or ([], the error key)."""
    return _parse(text, _CALLSIGN, str.upper, MAX_CALLSIGNS, ERROR_INVALID_CALLSIGNS)
