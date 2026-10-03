"""Estimated arrival at the destination of the chosen leg. No HA imports.

Lee 2026-10-03: the map's hover box shows "<origin>-<destination> in <n> min"
under the callsign, and the estimate is made the way Flights Above makes it
(its coordinator.py, `_compute_progress`): remaining great-circle distance to
the destination over a speed. The live ground speed is used only when it
looks like cruise (>= CRUISE_FLOOR_KMH); below that - climb, descent, a slow
aircraft - a typical cruise speed for the aircraft's class, so a plane
climbing out does not read hours late.

Flights Above keys its cruise speed on a class it derives from the type
designator. This integration already emits the ADS-B emitter category on
effectively every aircraft (aircraft.py, "Emitter category"), so the class
is that: the same speeds, mapped to the categories they describe.

The integration publishes the INSTANT (arrival_estimated_at, D0); the card
writes the words (06_MAP_CONTRACT.md D4b).

! An estimate, not a schedule. Straight line, no holding, no approach, no
taxi. Measured against nothing yet.
"""

from __future__ import annotations

import math

# Flights Above's CRUISE_KMH, by the emitter category each class falls in.
CRUISE_KMH = {
    "A1": 240,   # light (< 15,500 lb): Flights Above "piston"
    "A2": 700,   # small (15,500-75,000 lb): "regional" - CRJ, Q400, bizjets
    "A3": 830,   # large (75,000-300,000 lb): "narrowbody"
    "A4": 830,   # high-vortex large (B757): "narrowbody"
    "A5": 900,   # heavy (> 300,000 lb): "widebody"
    "A6": 900,   # high performance (> 5 g, > 400 kt)
    "A7": 220,   # rotorcraft; Flights Above has no class for it
}
CRUISE_UNKNOWN_KMH = 820     # Flights Above "unknown"
CRUISE_FLOOR_KMH = 500       # live ground speed trusted from here up

_EARTH_KM = 6371.0088


def _hav_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * _EARTH_KM * math.asin(math.sqrt(min(1.0, h)))


def cruise_kmh(emitter_category: str | None) -> int:
    """The class's typical cruise speed; the unknown one for anything else."""
    return CRUISE_KMH.get((emitter_category or "").strip().upper(), CRUISE_UNKNOWN_KMH)


def estimated_arrival(leg: dict | None, lat: float | None, lon: float | None,
                      speed_kmh: float | None, emitter_category: str | None,
                      fix_epoch: float | None) -> float | None:
    """Epoch seconds the aircraft should reach the leg's destination, or None.

    From the FIX's time, not the poll's: the distance left is measured from
    where the aircraft was at fix_epoch. None when the destination has no
    coordinates, the position or its time is missing, or any value is not
    finite.
    """
    if not leg or lat is None or lon is None or fix_epoch is None:
        return None
    d_lat, d_lon = leg.get("destination_lat"), leg.get("destination_lon")
    if d_lat is None or d_lon is None:
        return None
    try:
        remaining = _hav_km(float(lat), float(lon), float(d_lat), float(d_lon))
        speed = float(speed_kmh) if speed_kmh is not None else 0.0
    except (TypeError, ValueError):
        return None
    if not (math.isfinite(remaining) and math.isfinite(speed)):
        return None
    effective = speed if speed >= CRUISE_FLOOR_KMH else cruise_kmh(emitter_category)
    return float(fix_epoch) + remaining / effective * 3600.0
