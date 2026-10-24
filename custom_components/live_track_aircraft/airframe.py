"""Is it a rotorcraft? ONE answer, decided in saw_livetrack.aircraft_icons.airframe.

Moved to the shared library with the icon table it reads (backlog 298, saw-livetrack
0.2.11), verbatim from this file at ac45b2e. Lee's order of 2026-09-25 is in its
docstring: the type code when the icon table knows it, then the rotor type table,
then ADS-B emitter category A7. aircraft.py, the coordinator and the tests import
from here as before.
"""

from __future__ import annotations

from saw_livetrack.aircraft_icons.airframe import (  # noqa: F401
    _ROTOR_PREFIXES,
    _ROTOR_TYPES,
    _norm,
    is_rotorcraft,
    map_layer,
)
