"""The source seam.

Everything above this package sees Observations and never learns which feed
produced them. That seam is what let Live Track Ships add a second source
without touching entity code.

! Units are fixed once - 05_SHARED_LESSONS.md D0. A source converts to the
canonical unit or omits the field. It never passes a foreign unit upward and
it never substitutes a sentinel: a wrong value is worse than a missing one,
because the consumer cannot tell.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Observation:
    """One aircraft, as one source saw it, in canonical units.

    ! Every optional field defaults to None and is OMITTED downstream rather
    than emitted as a sentinel (D0).
    """

    # --- identity -------------------------------------------------------
    # The ICAO 24-bit address, lower case. This is the whole of identity:
    # entity naming, the previous-fix store and every lookup key on it.
    # ! Never a callsign - callsigns change mid-flight and are reassigned
    # daily.
    identity: str

    # --- position -------------------------------------------------------
    latitude: float
    longitude: float
    # When the POSITION was true, not when we fetched it (D2).
    observed_at: int

    # --- kinematics -----------------------------------------------------
    # ! heading_deg and course_deg are NOT the same field (D2). Heading is
    # where the aircraft is POINTED; course is where it is actually GOING.
    # Rotate an icon by heading, fall back to course. Extrapolate by course
    # only - and this integration does not extrapolate at all.
    heading_deg: float | None = None
    course_deg: float | None = None
    speed_kmh: float | None = None
    altitude_m: float | None = None
    vertical_rate_ms: float | None = None

    # --- description ----------------------------------------------------
    callsign: str | None = None
    type_code: str | None = None
    emitter_category: str | None = None
    squawk: str | None = None
    registration: str | None = None

    # How stale the source itself says this position is, in seconds.
    seen_pos_s: float | None = None
    # The feed's own database flags (readsb dbFlags: military 1, interesting
    # 2, PIA 4, LADD 8) and its owner/operator text, both from the
    # aggregator's aircraft database, not from the aircraft. Absent = None.
    db_flags: int | None = None
    own_op: str | None = None

    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def is_moving(self) -> bool:
        """Whether the aircraft is moving enough for a bearing to mean anything."""
        from ..const import STATIONARY_KT

        if self.speed_kmh is None:
            return False
        return self.speed_kmh > STATIONARY_KT * 1.852


class SourceError(Exception):
    """A source could not answer. The next source should be tried."""
