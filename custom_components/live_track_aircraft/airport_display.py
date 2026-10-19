"""What this integration SHOWS for an airport, where it differs from the data.

Lee, 2026-10-19, for every install: wherever a route reports DJT or KDJT, the
published code is PBI or KPBI and the published name is "Palm Beach
International Airport".

Background, as measured that night: the FAA changed the airport's
identifiers from PBI / KPBI to DJT / KDJT on 2026-07-09 (IATA followed on
2026-08-18), and it was named Palm Beach International Airport until then.
FiledRoutesDB still carried KPBI only (1,852 departure and 1,804 arrival
rows, none on KDJT); OurAirports keeps the ident KPBI with KDJT and DJT as
aliases, and its name column carries the new name. adsbdb is the source most
likely to send KDJT.

! DISPLAY ONLY. Applied when the attributes are published, after the leg is
chosen: coordinates, zones and the plausibility check use the code as the
route reported it, so nothing about which leg is shown changes.

No Home Assistant import: tested offline (tests/test_airport_display.py).
"""
from __future__ import annotations

SHOWN_CODE = {"KDJT": "KPBI", "DJT": "PBI"}
# Keyed on the SHOWN code, which every spelling of the airport maps to:
# shown_name tries the shown form of the table's ident, then of the reported
# code, so the name holds if the table ever moves its ident to KDJT.
SHOWN_NAME = {"KPBI": "Palm Beach International Airport",
              "PBI": "Palm Beach International Airport"}


def shown_code(code: str | None) -> str | None:
    """The code to publish for a code as a route reported it."""
    if not code:
        return code
    return SHOWN_CODE.get(code.strip().upper(), code)


def shown_name(reported: str | None, ident: str | None, table_name: str | None) -> str | None:
    """The airport name to publish, or None when there is none to show.

    reported   : the code as the route reported it
    ident      : the airport table's ident it resolved to (airports.py)
    table_name : the table's name for that ident
    """
    for key in (shown_code(ident), shown_code(reported)):
        if key and key.strip().upper() in SHOWN_NAME:
            return SHOWN_NAME[key.strip().upper()]
    name = (table_name or "").strip()
    return name or None
