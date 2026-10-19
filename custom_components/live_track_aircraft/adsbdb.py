"""Routes outside FiledRoutesDB: adsbdb, one callsign at a time (backlog 292).

FiledRoutesDB holds US-FILED flights only (FAA flight plans), so abroad it can
never supply a route: measured 2026-10-18 with the centre on Helsinki, 12
aircraft published and not one with a route. This module is the second
source. Lee's study (adsb-route-accuracy) measured adsbdb 27% correct in the
US, 79% elsewhere and 87% in the Nordics, so it is asked only when FiledRoutesDB
has NO route for the callsign, and every answer is judged with route_check's
strict `schedule` profile. Only a PLAUSIBLE answer is published; an
implausible one is dropped, not flagged (filed routes are flagged instead).

! REWRITTEN, NOT COPIED, from Flights Above's lookup (the 2026-09-08 design
rule). No hexdb: measured 9% correct in exactly the population a fallback
serves (backlog 30).

! THE TERMS. adsbdb's README: the flight route data is the work of David
Taylor, Edinburgh and Jim Mason, Glasgow, and may not be copied, published,
or incorporated into other databases without David Taylor's permission. So:
each install looks up for itself, the answers live in MEMORY ONLY (Lee,
2026-10-19), never in a file, never in anything published. A restart forgets
them and costs one request per callsign in view.

! MEASURED 2026-10-19 (bin\\lta292_adsbdb_probe.py, lta292_adsbdb_v1.py):
  * /v0/callsign/<cs> is the API: 200 with response.flightroute, or 404 with
    {"response": "unknown callsign"}. ~0.7 s, ~640 bytes.
  * /v1/ is NOT: it answers 200 with the website's HTML for any callsign,
    known or not, while the server header says "v1.0.0". So anything that is
    not JSON in the expected shape is a FAILURE here, never a miss and never
    a route. Do not "upgrade" API_URL to v1.
  * No rate-limit headers. The README: 512+ requests -> blocked 60 s; 1024+
    -> blocked 300 s, reset on EACH request made during the block. The window
    is not documented. HOURLY_BUDGET keeps this client under 512 for any
    window up to an hour; a longer window is not ruled out by anything
    measured. A 429 stops every request for PAUSE_429_S, longer than the
    longest block, because retrying inside a block extends it.

How often: one request per NEW callsign, never per poll. route() answers from
the cache and queues anything it has not seen; drain() works the queue one
request at a time, MIN_GAP_S apart, in the background. A hit is kept 30 days,
a miss 24 hours, a failed request 15 minutes, so nothing is asked every poll.

Only airline-shaped callsigns are asked (three letters, a digit, up to three
more): a registration used as a callsign has no route in any source (01
ENVIRONMENT, "Filter the population"), and asking would only spend budget.

No Home Assistant import: tested offline (tests/test_adsbdb.py).
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from collections import OrderedDict, deque
from typing import Any

from .route_check import PLAUSIBLE, SCHEDULE, choose_leg

_LOGGER = logging.getLogger(__name__)

API_URL = "https://api.adsbdb.com/v0/callsign/"
USER_AGENT = "LiveTrackAircraft (StrausbergAutomationWorks)"
TIMEOUT_S = 25
MAX_BODY = 64 * 1024                  # an answer is ~640 bytes; a cap, not a size

HIT_TTL_S = 30 * 86400                # Lee, 2026-10-19
MISS_TTL_S = 86400                    # Lee, 2026-10-19
ERROR_TTL_S = 15 * 60                 # a failed request is not asked again for this long
MAX_CACHE = 5000
MAX_QUEUE = 200

MIN_GAP_S = 1.0
HOURLY_BUDGET = 200
PAUSE_429_S = 15 * 60                 # longer than the 300 s block, which a request resets
ERRORS_BEFORE_PAUSE = 3
PAUSE_ERRORS_S = 10 * 60

HIT, MISS, LIMITED, ERROR = "hit", "miss", "limited", "error"

ATTRIBUTION = ("Route from adsbdb.com (https://www.adsbdb.com); route data by "
               "David Taylor, Edinburgh and Jim Mason, Glasgow")

_CALLSIGN = re.compile(r"^[A-Z]{3}[0-9][A-Z0-9]{0,3}$")
_AIRPORT = re.compile(r"^[A-Z0-9]{4}$")


# ---------------------------------------------------------------- pure parts

def lookup_key(callsign: str | None) -> str | None:
    """The callsign as asked, or None when it is not airline-shaped."""
    if not callsign:
        return None
    cs = str(callsign).strip().upper()
    return cs if _CALLSIGN.match(cs) else None


def _coord(value, limit: float) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if -limit <= value <= limit else None


def _airport(end) -> tuple[str, float | None, float | None] | None:
    if not isinstance(end, dict):
        return None
    code = end.get("icao_code")
    if not isinstance(code, str) or not _AIRPORT.match(code.strip().upper()):
        return None
    lat, lon = _coord(end.get("latitude"), 90.0), _coord(end.get("longitude"), 180.0)
    if lat is None or lon is None:
        lat = lon = None
    return code.strip().upper(), lat, lon


def parse(status: int, content_type: str | None, body: bytes) -> tuple[str, Any]:
    """(HIT, route) | (MISS, None) | (LIMITED, None) | (ERROR, reason).

    route: origin_icao, destination_icao, and the coordinates adsbdb gives
    for each end (None when absent or out of range).
    """
    if status == 429:
        return LIMITED, None
    if "json" not in (content_type or "").lower():
        return ERROR, "HTTP %d, not JSON (%s)" % (status, (content_type or "no content-type")[:40])
    try:
        payload = json.loads(body)
    except ValueError:
        return ERROR, "HTTP %d, unreadable JSON" % status
    response = payload.get("response") if isinstance(payload, dict) else None
    if status in (200, 404) and response == "unknown callsign":
        return MISS, None
    if status != 200:
        return ERROR, "HTTP %d" % status
    route = response.get("flightroute") if isinstance(response, dict) else None
    if not isinstance(route, dict):
        return ERROR, "no flightroute"
    origin, destination = _airport(route.get("origin")), _airport(route.get("destination"))
    if origin is None or destination is None:
        return ERROR, "no ICAO code for an end"
    return HIT, {
        "origin_icao": origin[0], "origin_lat": origin[1], "origin_lon": origin[2],
        "destination_icao": destination[0],
        "destination_lat": destination[1], "destination_lon": destination[2],
    }


class Cache:
    """Answers by callsign, in memory only, each with its own expiry."""

    TTL = {HIT: HIT_TTL_S, MISS: MISS_TTL_S, ERROR: ERROR_TTL_S}

    def __init__(self, cap: int = MAX_CACHE) -> None:
        self._cap = cap
        self._d: OrderedDict[str, tuple[str, Any, float]] = OrderedDict()

    def __len__(self) -> int:
        return len(self._d)

    def get(self, key: str, now: float) -> tuple[str, Any] | None:
        got = self._d.get(key)
        if got is None:
            return None
        if now >= got[2]:
            del self._d[key]
            return None
        return got[0], got[1]

    def put(self, key: str, state: str, route: Any, now: float) -> None:
        self._d.pop(key, None)
        self._d[key] = (state, route if state == HIT else None, now + self.TTL[state])
        while len(self._d) > self._cap:
            self._d.popitem(last=False)


class Budget:
    """At most `limit` requests in any rolling hour."""

    def __init__(self, limit: int = HOURLY_BUDGET) -> None:
        self._limit = limit
        self._sent: deque[float] = deque()

    def _trim(self, now: float) -> None:
        while self._sent and now - self._sent[0] >= 3600:
            self._sent.popleft()

    def allow(self, now: float) -> bool:
        self._trim(now)
        return len(self._sent) < self._limit

    def free_at(self, now: float) -> float:
        self._trim(now)
        return now if len(self._sent) < self._limit else self._sent[0] + 3600

    def record(self, now: float) -> None:
        self._sent.append(now)


def choose(route: dict | None, lookup, lat, lon, altitude_ft=None, course_deg=None,
           vertical_rate_ms=None, now=None) -> tuple[dict | None, str | None, int]:
    """The adsbdb leg to publish, or (None, None, 0).

    The ends are placed from our airport table first (`lookup`, airports.py:
    OurAirports coordinates and a zone); an end the table does not know uses
    the coordinates adsbdb sent, for this check only. Judged with SCHEDULE,
    and returned only when PLAUSIBLE.
    """
    if not route:
        return None, None, 0

    def resolve(code):
        got = lookup(code)
        if got:
            return got
        for end in ("origin", "destination"):
            if route.get(end + "_icao") == code and route.get(end + "_lat") is not None:
                return {"lat": route[end + "_lat"], "lon": route[end + "_lon"], "tz": None}
        return None

    leg, verdict, considered = choose_leg(
        [(route["origin_icao"], route["destination_icao"], None)], resolve, lat, lon,
        altitude_ft, course_deg, profile=SCHEDULE, vertical_rate_ms=vertical_rate_ms,
        now=now, times=None)
    if verdict != PLAUSIBLE:
        return None, None, 0
    return leg, verdict, considered


# ------------------------------------------------------- the lookup client

class AdsbdbRoutes:
    """One per Home Assistant instance: every entry shares the cache and the
    budget, because adsbdb counts requests per address, not per entry."""

    def __init__(self, clock=time.time, sleep=asyncio.sleep, fetch=None) -> None:
        # clock, sleep and fetch are replaced only by the offline tests.
        self._clock, self._sleep = clock, sleep
        self._fetch_fn = fetch or self._fetch
        self.cache = Cache()
        self.budget = Budget()
        self._queue: OrderedDict[str, None] = OrderedDict()
        self._draining = False
        self._errors = 0
        self.paused_until = 0.0
        self.status = "idle"

    @property
    def pending(self) -> bool:
        return bool(self._queue)

    def route(self, callsign: str | None, now: float | None = None) -> dict | None:
        """The cached route for this callsign; queues it when not yet asked."""
        key = lookup_key(callsign)
        if key is None:
            return None
        now = self._clock() if now is None else now
        got = self.cache.get(key, now)
        if got is None:
            if key not in self._queue and len(self._queue) < MAX_QUEUE:
                self._queue[key] = None
            return None
        return got[1] if got[0] == HIT else None

    def _set(self, status: str) -> None:
        if status != self.status:
            self.status = status
            _LOGGER.debug("adsbdb: %s", status)

    async def _fetch(self, session, key: str) -> tuple[int, str | None, bytes]:
        import aiohttp  # noqa: PLC0415 - HA's own dependency; kept out of the pure part

        async with session.get(API_URL + key, timeout=aiohttp.ClientTimeout(total=TIMEOUT_S),
                               headers={"User-Agent": USER_AGENT, "Accept": "application/json"}) as resp:
            body = bytearray()
            async for chunk in resp.content.iter_chunked(1 << 14):
                body += chunk
                if len(body) > MAX_BODY:
                    return resp.status, "too large", b""
            return resp.status, resp.headers.get("Content-Type"), bytes(body)

    async def async_drain(self, session) -> None:
        """Work the queue, one request at a time. Returns when it is empty,
        paused, or the hourly budget is spent; the next poll starts it again."""
        if self._draining:
            return
        self._draining = True
        try:
            first = True
            while self._queue:
                now = self._clock()
                if now < self.paused_until:
                    return
                if not self.budget.allow(now):
                    self._set("hourly budget of %d spent until %s" % (
                        HOURLY_BUDGET, _utc(self.budget.free_at(now))))
                    return
                if not first:
                    await self._sleep(MIN_GAP_S)
                first = False
                key = next(iter(self._queue))
                now = self._clock()
                self.budget.record(now)
                try:
                    status, ctype, body = await self._fetch_fn(session, key)
                    state, value = parse(status, ctype, body)
                except Exception as err:  # noqa: BLE001 - network, timeouts
                    state, value = ERROR, err.__class__.__name__
                now = self._clock()
                if state == LIMITED:
                    # The callsign stays queued; nothing is sent during the pause.
                    self.paused_until = now + PAUSE_429_S
                    self._set("paused after HTTP 429 until %s" % _utc(self.paused_until))
                    _LOGGER.warning("adsbdb answered 429; no requests until %s", _utc(self.paused_until))
                    return
                del self._queue[key]
                self.cache.put(key, state, value, now)
                if state == ERROR:
                    self._errors += 1
                    if self._errors >= ERRORS_BEFORE_PAUSE:
                        self.paused_until = now + PAUSE_ERRORS_S
                        self._set("paused after %d failures (%s) until %s" % (
                            self._errors, value, _utc(self.paused_until)))
                        self._errors = 0
                        return
                    self._set("failed: %s" % value)
                else:
                    self._errors = 0
                    self._set("ok")
        finally:
            self._draining = False


def _utc(epoch: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime(epoch))
