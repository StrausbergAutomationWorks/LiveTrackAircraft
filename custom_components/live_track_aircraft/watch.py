"""The worldwide watch: the aircraft this integration shows WHEREVER THEY ARE, not only in the circle.

Who is on it (Lee, 2026-10-21 02:59 and 22:09; 2026-10-24):
  * the presidential airframes, by Mode S hex, never by callsign (a callsign proves nothing about
    who is aboard): adfdf8 and adfdf9, the VC-25As, and af83f3, the VC-25B "Bridge". The 747-8
    trainer stays off until its hex is measured;
  * the 89th Airlift Wing (its SAM and VENUS callsigns) and military escorts near a presidential
    airframe, from adsb.fi's military list.

! THE NATIONWIDE ENFORCEMENT WATCH MOVED TO LIVE TRACK ENFORCEMENT AIRCRAFT (backlog 297, Lee
2026-10-23 23:01 and 2026-10-24 01:29): the EnforcementAircraft list's sourced and detected entries
and every federal law-enforcement registrant. This integration publishes the registrants it finds in
its FAA table for it (enforcement.publish_federal), and with it installed alone shows listed aircraft
only inside its circle (decision G). It read: the list, the federal registrants and the presidential
airframes, 305 hexes, one request a minute (62064b6).

! ONE SHARED POLL (saw_livetrack.adsb_poll): the presidential hexes join the instance's union hex
round, once a minute, with whatever Live Track Enforcement Aircraft asks; the military list goes
through the same pacing and the same 429 backoff, because adsb.fi limits per address. One WatchList
per instance (hass.data). Never adsb.lol for this (05_SHARED_LESSONS.md B16).
"""
from __future__ import annotations

import re
import time
from collections.abc import Callable

from saw_livetrack import adsb_poll as ap

from .const import DOMAIN
from .sources.base import Observation

CONSUMER = DOMAIN
SOURCE = ap.FI
MIL_URL = "https://opendata.adsb.fi/api/v2/mil"
INTERVAL_S = ap.HEX_INTERVAL_S
# The military answer is dropped after this long without a fresh one, as the hex answer is.
STALE_S = ap.HEX_STALE_S

PRESIDENTIAL = {
    "adfdf8": "VC-25A 82-8000",
    "adfdf9": "VC-25A 92-9000",
    "af83f3": "VC-25B 25-3300",
}
WHY_PRESIDENTIAL = "presidential"
WHY_89AW = "89aw"
WHY_ESCORT = "escort"

# ! THE 89th AIRLIFT WING, ALWAYS (Lee 2026-10-22 01:27): SAM or VENUS plus digits AND a hex in the US
# military block (ADF7C8-AFFFFF). Measured 2026-10-21: "SAMB2" on /v2/mil was a RAAF PC-21 (7cf9e7).
_WING_CALLSIGN = re.compile(r"^(?:SAM|VENUS)\d{1,5}$")
US_MIL_MIN, US_MIL_MAX = 0xADF7C8, 0xAFFFFF

# ! ESCORTS: any military-flagged aircraft within ESCORT_KM of a presidential airframe while one is in
# view (Lee 2026-10-21, option b; 10 nm on 2026-10-22): a judgement, not a measurement.
ESCORT_KM = 18.52


def _is_us_mil(hex_id: str) -> bool:
    try:
        return US_MIL_MIN <= int(hex_id, 16) <= US_MIL_MAX
    except (TypeError, ValueError):
        return False


def _km(a: Observation, b: Observation) -> float:
    return ap.km_between(a.latitude, a.longitude, b.latitude, b.longitude)


def from_military(mil: dict[str, Observation], presidential: list[Observation]) -> dict[str, str]:
    """{hex: why} for the wing's callsigns and escorts in /v2/mil's answer."""
    out: dict[str, str] = {}
    for hx, o in mil.items():
        if hx in PRESIDENTIAL:
            continue
        if _is_us_mil(hx) and _WING_CALLSIGN.match((o.callsign or "").upper()):
            out[hx] = WHY_89AW
        elif any(_km(o, p) <= ESCORT_KM for p in presidential):
            out[hx] = WHY_ESCORT
    return out


class WatchList:
    """The presidential airframes through the shared hex round, and the military list once a minute."""

    def __init__(self, poll: ap.Poll, clock: Callable[[], float] = time.monotonic) -> None:
        self._poll = poll
        self._clock = clock
        self._next = 0.0
        self._mil_at: float | None = None
        self._mil: list[Observation] = []
        self._why: dict[str, str] = {}
        self.status = "idle"
        poll.set_hexes(CONSUMER, PRESIDENTIAL)

    def hexes(self) -> list[str]:
        return list(PRESIDENTIAL)

    def why(self, hex_id: str) -> str:
        if hex_id in PRESIDENTIAL:
            return WHY_PRESIDENTIAL
        return self._why.get(hex_id, "watched")

    def due(self) -> bool:
        return self._clock() >= self._next or self._poll.hex_due()

    def observations(self) -> list[Observation]:
        """The presidential airframes from the shared round, plus the wing and escorts while fresh."""
        found = {o.identity: o for o in self._poll.hex_observations(CONSUMER)}
        if self._mil_at is not None and self._clock() - self._mil_at <= STALE_S:
            for o in self._mil:
                found.setdefault(o.identity, o)
        return list(found.values())

    async def async_fetch(self, session, now: float) -> None:
        """The shared hex round (when due), then the military list (once a minute).

        ! A failed military list keeps what the hex round found and says so; a non-200 is never
        "none of them is flying".
        """
        self._poll.set_hexes(CONSUMER, PRESIDENTIAL)
        hex_status = await self._poll.hex_round(session, now)
        if self._clock() < self._next:
            if hex_status != "ok":
                self.status = hex_status
            return
        self._next = self._clock() + INTERVAL_S
        try:
            payload = await self._poll.get_json(session, SOURCE, MIL_URL)
        except ap.SourceError as err:
            self.status = "military list: %s" % err if hex_status == "ok" else hex_status
            return
        mil = ap.parse_payload(payload if isinstance(payload, dict) else {}, now)
        hexed = {o.identity: o for o in self._poll.hex_observations(CONSUMER)}
        pres = [o for h, o in {**mil, **hexed}.items() if h in PRESIDENTIAL]
        why = from_military(mil, pres)
        # A presidential airframe the hex round missed is still one.
        keep = [mil[h] for h in list(why) + [h for h in PRESIDENTIAL if h in mil]]
        self._mil, self._why, self._mil_at = keep, why, self._clock()
        self.status = hex_status if hex_status != "ok" else "ok"


def parse(payload, now: float) -> dict[str, Observation]:
    """The answer's records, on the feed's own clock (saw_livetrack.adsb_poll)."""
    return ap.parse_payload(payload, now)


__all__ = ["PRESIDENTIAL", "WatchList", "from_military"]
