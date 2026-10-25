"""The source seam.

Everything above this package sees Observations and never learns which feed produced them. That seam
is what let Live Track Ships add a second source without touching entity code.

! SINCE BACKLOG 297 (saw-livetrack 0.2.13) Observation and SourceError are the shared poll's,
saw_livetrack.adsb_poll, where they moved verbatim from this file at 62064b6, so the circle the shared
poll answers and the records this integration builds are one type. Every name here is re-exported.

! Units are fixed once - 05_SHARED_LESSONS.md D0. A source converts to the canonical unit or omits the
field. It never passes a foreign unit upward and it never substitutes a sentinel.
"""

from __future__ import annotations

from saw_livetrack.adsb_poll import Observation, SourceError

__all__ = ["Observation", "SourceError"]
