"""The worldwide watch list: aircraft shown WHEREVER THEY ARE, not only in
the circle (Lee, 2026-10-21 02:59 and 22:09).

Who is on it:
  * the presidential airframes, by Mode S hex, never by callsign (a callsign
    proves nothing about who is aboard): adfdf8 and adfdf9, the VC-25As, and
    af83f3, the VC-25B "Bridge". The 747-8 trainer stays off until its hex is
    measured;
  * every law-enforcement aircraft in the FAA government table
    (registrations.LAW_ENFORCEMENT: DHS, CBP, ICE, FBI, USMS, state and
    local police, the Coast Guard).

! ONE REQUEST A MINUTE ANSWERS ALL OF IT. Measured 2026-10-22 00:3x CDT:
adsb.fi's /v2/icao/<hex>,<hex>,... took all 994 hexes (3 + 991) in one
request - a 6,994-character URL, HTTP 200 in 1.3 s, 6.4 kB back, 11 aircraft
airborne at that hour - and returned only hexes it was asked for.
adsb.fi's README documents the comma-separated form and a public limit of 1
request a second; it gives no per-request hex limit, so requests are cut at
MAX_PER_REQUEST, the size measured to work. Never adsb.lol for this
(05_SHARED_LESSONS.md B16).

! THE CIRCLE IS THE SAME SOURCE. adsb.fi limits per address, so a 429 here is
recorded in the circle's own BACKOFF (sources/adsb.py) and the watch waits
while adsb.fi is backing off. One WatchList per instance (hass.data), like
the adsbdb client: a second entry reads the same answer.
"""
from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

import aiohttp

from .const import REQUEST_TIMEOUT, USER_AGENT
from .sources.adsb import BACKOFF, Backoff, _f, _parse, _retry_after_s
from .sources.base import Observation

_LOGGER = logging.getLogger(__name__)

URL = "https://opendata.adsb.fi/api/v2/icao/"
SOURCE = "adsb.fi"
INTERVAL_S = 60
# The answer is dropped after this long without a fresh one, so a failing
# watch does not freeze aircraft on the map.
STALE_S = 3 * INTERVAL_S
MAX_PER_REQUEST = 994
CHUNK_GAP_S = 1.1          # adsb.fi: 1 request a second

PRESIDENTIAL = {
    "adfdf8": "VC-25A 82-8000",
    "adfdf9": "VC-25A 92-9000",
    "af83f3": "VC-25B 25-3300",
}
WHY_PRESIDENTIAL = "presidential"
WHY_LAW = "law_enforcement"


def chunks(hexes: list[str], size: int = MAX_PER_REQUEST) -> list[list[str]]:
    return [hexes[i:i + size] for i in range(0, len(hexes), size)]


class WatchList:
    """Asks adsb.fi for every watched hex once a minute and keeps the answer."""

    def __init__(self, law_hexes: Callable[[], list[str]],
                 backoff: Backoff | None = None,
                 clock: Callable[[], float] = time.monotonic) -> None:
        self._law_hexes = law_hexes
        self._backoff = BACKOFF if backoff is None else backoff
        self._clock = clock
        self._next = 0.0
        self._at: float | None = None
        self._obs: list[Observation] = []
        self.status = "idle"

    def hexes(self) -> list[str]:
        law = [h.lower() for h in (self._law_hexes() or [])]
        return list(PRESIDENTIAL) + sorted(set(law) - set(PRESIDENTIAL))

    @staticmethod
    def why(hex_id: str) -> str:
        return WHY_PRESIDENTIAL if hex_id in PRESIDENTIAL else WHY_LAW

    def due(self) -> bool:
        return self._clock() >= self._next

    def observations(self) -> list[Observation]:
        """The last answer, or nothing once it is STALE_S old."""
        if self._at is None or self._clock() - self._at > STALE_S:
            return []
        return list(self._obs)

    def _done(self, status: str) -> None:
        self.status = status
        self._next = self._clock() + INTERVAL_S

    async def async_fetch(self, session: aiohttp.ClientSession, now: float) -> None:
        """One round: every chunk, or stop at the first failure."""
        left = self._backoff.remaining(SOURCE)
        if left is not None:
            self._done(f"waiting: {SOURCE} backing off")
            return
        found: dict[str, Observation] = {}
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        parts = chunks([h.upper() for h in self.hexes()])
        for i, part in enumerate(parts):
            if i:
                await _sleep(CHUNK_GAP_S)
            try:
                async with session.get(
                        URL + ",".join(part), headers=headers,
                        timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
                    if resp.status != 200:
                        if resp.status == 429:
                            self._backoff.refused(SOURCE, _retry_after_s(
                                resp.headers.get("Retry-After"), time.time()))
                        # ! A non-200 is never "none of them is flying":
                        # the last good answer stands until it is stale.
                        self._done(f"HTTP {resp.status}")
                        return
                    payload = await resp.json(content_type=None)
            except (aiohttp.ClientError, TimeoutError, ValueError) as err:
                self._done(f"failed: {type(err).__name__}")
                return
            found.update(parse(payload, now))
        self._obs = list(found.values())
        self._at = self._clock()
        self._done("ok")


def parse(payload: dict[str, Any], now: float) -> dict[str, Observation]:
    """The answer's records, on the feed's own clock (sources/adsb.py)."""
    feed_now = _f(payload.get("now"))
    if feed_now and feed_now > 1e11:
        feed_now = feed_now / 1000.0
    base = feed_now if feed_now else now
    out: dict[str, Observation] = {}
    for record in payload.get("ac") or payload.get("aircraft") or []:
        if isinstance(record, dict):
            obs = _parse(record, base)
            if obs is not None:
                out[obs.identity] = obs
    return out


async def _sleep(s: float) -> None:
    import asyncio
    await asyncio.sleep(s)
