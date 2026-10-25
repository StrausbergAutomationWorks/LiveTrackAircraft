"""The entity cap, with listed aircraft exempt. No Home Assistant import.

! A GUARD RAIL, NOT A DISPLAY CONTROL (const.py). When more aircraft are in
the circle than max_aircraft, the nearest are kept, so what survives is what
is overhead.

! LISTED AIRCRAFT ARE NEVER DROPPED (Lee 2026-10-25 14:14: "LTA should not
drop a listed aircraft"). A hex on the EnforcementAircraft list as sourced or
detected_unconfirmed survives the cap wherever it is in the circle, the way the
watch list survives it. A cleared entry was found not involved and is capped
like any other aircraft. Measured that day: 691 aircraft in a 463 km circle
against a cap of 250, so the cap reached 212 km and a listed aircraft beyond
that was gone from the map with Live Track Aircraft alone.
"""

from __future__ import annotations

from typing import Any, Callable


def apply_cap(aircraft: dict[str, dict[str, Any]], max_aircraft: int,
              exempt: Callable[[str], bool]) -> tuple[dict[str, dict[str, Any]], bool, int]:
    """-> (kept, capped, exempted).

    kept: the nearest max_aircraft by distance_km, then every further one for
    which exempt(identity) is true, nearest first. capped: whether the cap bit.
    exempted: how many were kept only because they are exempt.
    """
    if len(aircraft) <= max_aircraft:
        return aircraft, False, 0
    nearest = sorted(aircraft.values(), key=lambda r: r["distance_km"])
    kept = {r["identity"]: r for r in nearest[:max_aircraft]}
    exempted = 0
    for r in nearest[max_aircraft:]:
        if exempt(r["identity"]):
            kept[r["identity"]] = r
            exempted += 1
    return kept, True, exempted
