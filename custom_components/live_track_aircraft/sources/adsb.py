"""ADS-B sources: adsb.fi, then adsb.lol (adsb.fi first since 2026-09-25).

! THE CIRCLE GOES THROUGH THE INSTANCE'S SHARED POLL since backlog 297 (saw-livetrack 0.2.13,
saw_livetrack.adsb_poll), where the parser, the backoff, the short-answer guard and fetch() moved
verbatim from this file at 62064b6. Shared means one 429 backoff for the house's IP across Live Track
Aircraft and Live Track Enforcement Aircraft, requests to one source paced a second apart, and an
identical circle asked once (05_SHARED_LESSONS.md B16). This integration keeps its source order and
its User-Agent; the names below are re-exported so the coordinator and the tests read them as before.

! MEASURED 2026-09-09. 196 of 360 requests at a 5-second poll returned HTTP 429 and nothing else. A
rate-limited source that falls through to the next one is INVISIBLE unless something says which
source answered, so fetch returns the source name and the count sensor publishes it.
! A SHORT ANSWER IS NOT A NEGATIVE RESULT (measured 2026-09-25): a 200 carrying under half the last
good count is tried against the next source (short_floor).
"""

from __future__ import annotations

from saw_livetrack import adsb_poll as _ap

from ..const import SOURCE_URLS, USER_AGENT
from .base import Observation, SourceError

_f = _ap._f
_parse = _ap.parse_record
_retry_after_s = _ap.retry_after_s
Backoff = _ap.Backoff
short_floor = _ap.short_floor
SHORT_GUARD_MIN = _ap.SHORT_GUARD_MIN
SHORT_FRACTION = _ap.SHORT_FRACTION
KT_TO_KMH = _ap.KT_TO_KMH
FT_TO_M = _ap.FT_TO_M
FPM_TO_MS = _ap.FPM_TO_MS

# The order this integration asks in (const.SOURCE_URLS); the URLs are the shared poll's, and
# tests/test_sources.py holds the two level.
SOURCES: tuple[str, ...] = tuple(name for name, _ in SOURCE_URLS)


async def fetch(session, latitude: float, longitude: float, radius_km: float, now: float,
                backoff: Backoff | None = None, min_expected: int | None = None,
                poll: _ap.Poll | None = None) -> tuple[str, list[Observation]]:
    """Every aircraft in the circle from the first source that answers fully and is not backing off.

    Returns the source name and its observations; raises SourceError when every source failed or is
    backing off. poll: the instance's shared poll (the coordinator passes it); without one, a poll of
    its own around `backoff` (the tests).
    """
    if poll is None:
        poll = _ap.Poll(backoff=backoff) if backoff is not None else _ap.Poll()
    return await poll.circle(session, latitude, longitude, radius_km, now, sources=SOURCES,
                             min_expected=min_expected, user_agent=USER_AGENT)


__all__ = ["Backoff", "Observation", "SourceError", "SOURCES", "fetch", "short_floor"]
