"""Sliced state writes. No Home Assistant import.

! A TEST KNOB FOR THE MAP CARD'S BURST (2026-10-26; Aircraft
30_Correspondence/BRIEF_burst_from_map_card_20261025.md). Every poll writes
every aircraft's state, and with a full circle that is up to max_aircraft states
in one hass change; Home Assistant's websocket handler then runs 76-159 ms. With
a slice size set, the platform writes the first slice at once and the rest
spread across the poll interval, so no one change carries more than a slice.

! THE DEFAULT IS ALL, which is the old behaviour exactly: one write of every
aircraft, in the poll's own callback.

! A write carries the aircraft's record as it stands when the write happens, and
the record is THE FIX: observed_at and previous_* come from the feed, never from
the write time. A slice written 9 s after the poll shows the fix it would have
shown at once; it only reaches the frontend later.

! Runtime only, never stored: fire the event live_track_aircraft_write_slice
with {"size": 25 | 50 | 100 | "all"}, and "entry_id" to set one entry. A
restart returns every entry to ALL.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

EVENT = "live_track_aircraft_write_slice"
SIZES = (25, 50, 100)
ALL = None


def parse_size(value: Any) -> int | None:
    """None or "all" -> ALL; 25, 50 or 100 (an int, or digits) -> that int.

    Anything else raises ValueError, so a mistyped event changes nothing.
    """
    if value is None:
        return ALL
    if isinstance(value, str):
        text = value.strip().lower()
        if text == "all":
            return ALL
        if not text.isdigit():
            raise ValueError(f"write slice must be 25, 50, 100 or 'all', not {value!r}")
        value = int(text)
    if isinstance(value, bool) or not isinstance(value, int) or value not in SIZES:
        raise ValueError(f"write slice must be 25, 50, 100 or 'all', not {value!r}")
    return value


def plan(identities: Sequence[str], size: int | None,
         interval_s: float | None) -> list[tuple[float, list[str]]]:
    """-> [(delay_s, [identity, ...]), ...]: every identity once, in the order given.

    ALL, no usable interval, or no more than one slice: one write now. Otherwise
    ceil(n / size) slices, slice k at k * interval_s / slices, so the first is
    written now and the last a full step before the next poll.
    """
    ids = list(identities)
    if not ids:
        return []
    if size is ALL or interval_s is None or interval_s <= 0 or len(ids) <= size:
        return [(0.0, ids)]
    count = math.ceil(len(ids) / size)
    step = interval_s / count
    return [(k * step, ids[k * size:(k + 1) * size]) for k in range(count)]
