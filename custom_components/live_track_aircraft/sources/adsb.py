"""ADS-B sources: adsb.lol, then adsb.fi.

Both serve the readsb JSON shape, so one parser covers them; only the URL
path differs. They are tried in order and any non-200 is that source
failing.

! MEASURED 2026-09-09. 196 of 360 requests at a 5-second poll returned HTTP
429 and nothing else - a 45.6% success rate. At 15 s there is no throttling.
A rate-limited source that falls through to the next one is INVISIBLE unless
something says which source answered, so `fetch` returns the source name and
the count sensor publishes it.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import aiohttp

from ..const import (
    BACKOFF_FIRST_S,
    BACKOFF_MAX_S,
    REQUEST_TIMEOUT,
    RETRY_AFTER_MAX_S,
    SOURCE_URLS,
    USER_AGENT,
)
from .base import Observation, SourceError

_LOGGER = logging.getLogger(__name__)

KT_TO_KMH = 1.852
FT_TO_M = 0.3048
FPM_TO_MS = 0.00508


def _f(value: Any) -> float | None:
    """A finite float, or None. Strings and sentinels become None."""
    if value is None or isinstance(value, bool):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if out == out and abs(out) != float("inf") else None


def _parse(record: dict[str, Any], now: float) -> Observation | None:
    """One feed record to an Observation, or None if it is not for us."""
    hex_id = (record.get("hex") or "").strip().lower()
    if not hex_id:
        return None

    # ! SKIP TIS-B. A '~' prefix marks a non-ICAO address - a ground station
    # rebroadcasting a radar target. Measured 2026-09-10: 1.1% of records,
    # carrying no callsign, no category and a seen_pos of 34-50 s against a
    # p50 of 0.30 s for ADS-B. It can never be route-joined either, because
    # the TFMS join is call-sign only. Nothing to label and nothing to add.
    if hex_id.startswith("~"):
        return None

    lat, lon = _f(record.get("lat")), _f(record.get("lon"))
    if lat is None or lon is None:
        return None

    # ! SKIP GROUND OBJECTS. alt_baro is the STRING "ground" for anything on
    # the surface, which includes the C1/C2 emitter categories - airport
    # vehicles, which are not aircraft. Without this the ramp at O'Hare owns
    # the map.
    alt_raw = record.get("alt_baro")
    if isinstance(alt_raw, str):
        if alt_raw.strip().lower() == "ground":
            return None
        alt_raw = None

    # How stale the source says this position already is. `now` is the
    # SERVER's clock, so this lands on the server's timeline and not ours.
    seen_pos = _f(record.get("seen_pos"))
    observed_at = round(now - seen_pos) if seen_pos is not None else round(now)

    callsign = (record.get("flight") or "").strip() or None

    # ! track is COURSE over ground, not heading (D2). The fork publishes it
    # under the name `heading`, which is the mislabel this integration exists
    # not to inherit. true_heading is the real heading and is separately
    # populated on about a quarter of records.
    return Observation(
        identity=hex_id,
        latitude=lat,
        longitude=lon,
        observed_at=observed_at,
        course_deg=_f(record.get("track")),
        heading_deg=_f(record.get("true_heading")),
        speed_kmh=(None if _f(record.get("gs")) is None
                   else round(_f(record.get("gs")) * KT_TO_KMH, 1)),
        altitude_m=(None if _f(alt_raw) is None
                    else round(_f(alt_raw) * FT_TO_M, 1)),
        vertical_rate_ms=(None if _f(record.get("baro_rate")) is None
                          else round(_f(record.get("baro_rate")) * FPM_TO_MS, 2)),
        callsign=callsign,
        type_code=(record.get("t") or "").strip() or None,
        emitter_category=(record.get("category") or "").strip() or None,
        squawk=(record.get("squawk") or "").strip() or None,
        registration=(record.get("r") or "").strip() or None,
        seen_pos_s=seen_pos,
    )


def _retry_after_s(value: str | None, wall_now: float) -> float | None:
    """Retry-After as seconds from now, clamped; None if absent or unreadable.

    RFC 9110 allows delay-seconds or an HTTP-date. Both are accepted.
    """
    if not value:
        return None
    value = value.strip()
    try:
        secs = float(value)
    except ValueError:
        try:
            when = parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError):
            return None
        if when is None:
            return None
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        secs = when.timestamp() - wall_now
    if secs != secs or abs(secs) == float("inf"):
        return None
    return max(1.0, min(RETRY_AFTER_MAX_S, secs))


class Backoff:
    """Per-source skip windows after HTTP 429.

    ! MODULE-LEVEL, SHARED BY EVERY CONFIG ENTRY, ON PURPOSE: the limit is
    per IP, not per entry. Decisions use the monotonic clock; the wall-clock
    deadline exists only to be displayed.
    """

    def __init__(
        self,
        clock: Callable[[], float] = time.monotonic,
        wall: Callable[[], float] = time.time,
    ) -> None:
        self._clock = clock
        self._wall = wall
        self._until: dict[str, float] = {}
        self._until_wall: dict[str, float] = {}
        self._strikes: dict[str, int] = {}

    def remaining(self, name: str) -> float | None:
        """Seconds left in this source's skip window, or None."""
        until = self._until.get(name)
        if until is None:
            return None
        left = until - self._clock()
        return left if left > 0 else None

    def refused(self, name: str, retry_after: float | None) -> tuple[float, int]:
        """Record a 429. Returns (skip seconds, consecutive refusals)."""
        strikes = self._strikes.get(name, 0) + 1
        self._strikes[name] = strikes
        if retry_after is not None:
            delay = retry_after
        else:
            delay = min(BACKOFF_MAX_S, BACKOFF_FIRST_S * 2 ** (strikes - 1))
        self._until[name] = self._clock() + delay
        self._until_wall[name] = self._wall() + delay
        return delay, strikes

    def answered(self, name: str) -> int:
        """Record a 200. Returns the refusals it ended (0 if none)."""
        self._until.pop(name, None)
        self._until_wall.pop(name, None)
        return self._strikes.pop(name, 0)

    def status(self) -> dict[str, str]:
        """{source: resume time, UTC ISO} for every source now skipped.

        One fixed value per episode, not a countdown, so the attribute does
        not change on every poll and the recorder de-duplicates it.
        """
        return {
            name: datetime.fromtimestamp(self._until_wall[name], timezone.utc)
            .replace(microsecond=0).isoformat().replace("+00:00", "Z")
            for name in self._until
            if self.remaining(name) is not None
        }


BACKOFF = Backoff()


async def fetch(
    session: aiohttp.ClientSession,
    latitude: float,
    longitude: float,
    radius_km: float,
    now: float,
    backoff: Backoff | None = None,
) -> tuple[str, list[Observation]]:
    """Fetch from the first source that answers and is not backing off.

    Returns the source name and its observations. Raises SourceError when
    every source failed or is backing off - the caller decides whether to
    serve its last good result or fail.
    """
    backoff = BACKOFF if backoff is None else backoff
    nm = max(1, min(250, round(radius_km / 1.852)))
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    last_error = "no sources configured"
    failures: list[str] = []

    for name, template in SOURCE_URLS:
        left = backoff.remaining(name)
        if left is not None:
            # Not requested at all: that is the point.
            last_error = f"{name} backing off, {left:.0f} s left"
            failures.append(last_error)
            _LOGGER.debug("%s", last_error)
            continue
        url = template.format(lat=round(latitude, 6), lon=round(longitude, 6), nm=nm)
        try:
            async with session.get(
                url, headers=headers,
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            ) as resp:
                if resp.status != 200:
                    # ! A non-200 is never a negative RESULT. 429 in
                    # particular means slow down, not "no aircraft".
                    last_error = f"{name} returned HTTP {resp.status}"
                    if resp.status == 429:
                        header = resp.headers.get("Retry-After")
                        delay, strikes = backoff.refused(
                            name, _retry_after_s(header, time.time()))
                        # First refusal of an episode at INFO; a repeat
                        # means the backoff is not enough, so WARNING.
                        _LOGGER.log(
                            logging.WARNING if strikes > 1 else logging.INFO,
                            "%s rate-limited (HTTP 429, %s in a row); skipping "
                            "it for %.0f s (%s)",
                            name, strikes, delay,
                            f"Retry-After {header!r}" if header
                            else "no Retry-After")
                    else:
                        _LOGGER.info("%s; trying the next source", last_error)
                    failures.append(last_error)
                    continue
                payload = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            last_error = f"{name} unreachable: {err!r}"
            failures.append(last_error)
            _LOGGER.info("%s; trying the next source", last_error)
            _LOGGER.debug("%s", last_error, exc_info=True)
            continue

        ended = backoff.answered(name)
        if ended:
            _LOGGER.info("%s answering again after %s refusal(s)", name, ended)

        # ! USE THE SERVER'S CLOCK, NOT OURS. The payload carries `now` in
        # MILLISECONDS, and every record's seen_pos is an age measured
        # against it. Deriving observed_at from local time.time() instead
        # mixes in our own poll jitter, and measured 2026-09-11 that made
        # observed_at go BACKWARDS between polls - 1789163459 then
        # 1789163447. A negative segment then fails the 0 < seg guard, the
        # previous_* fields drop out, and the marker stutters. Same visible
        # symptom as the duplicate-fix aliasing in D3c-iii, different cause.
        #
        # It also makes a genuinely unchanged observation produce an
        # IDENTICAL observed_at - server now and seen_pos advance together -
        # which is exactly what the coordinator's duplicate guard needs.
        # ! THE TWO SOURCES USE DIFFERENT UNITS FOR THE SAME FIELD.
        # Measured 2026-09-11, seconds apart:
        #     adsb.lol   now = 1789164099000      MILLISECONDS
        #     adsb.fi    now = 1789164098.001     SECONDS
        # Dividing by 1000 unconditionally turned every adsb.fi timestamp
        # into a 1970 date, the coordinator's monotonic guard then refused
        # all of them as regressions, and the fixes FROZE at their last
        # adsb.lol values - stale positions served confidently for minutes.
        # Sniff the magnitude; do not trust a shared field name to mean a
        # shared unit.
        feed_now = _f(payload.get("now"))
        if feed_now and feed_now > 1e11:
            feed_now = feed_now / 1000.0
        base = feed_now if feed_now else now

        records = payload.get("ac") or payload.get("aircraft") or []
        seen: dict[str, Observation] = {}
        for record in records:
            if not isinstance(record, dict):
                continue
            obs = _parse(record, base)
            if obs is not None:
                # A feed can carry the same hex twice; the later record wins.
                seen[obs.identity] = obs
        return name, list(seen.values())

    # Every source, not only the last: "adsb.fi returned 503" alone hides
    # that adsb.lol was skipped for a backoff.
    raise SourceError("; ".join(failures) or last_error)
