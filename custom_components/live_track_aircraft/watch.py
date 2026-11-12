"""The worldwide watch: the aircraft this integration shows WHEREVER THEY ARE, not only in the circle.

Who is on it (Lee, 2026-10-21 02:59 and 22:09; 2026-10-24):
  * the presidential airframes, by Mode S hex, never by callsign (a callsign proves nothing about
    who is aboard): adfdf8 and adfdf9, the VC-25As, and af83f3, the VC-25B "Bridge". The 747-8
    trainer stays off until its hex is measured;
  * the 89th Airlift Wing (its SAM and VENUS callsigns) and military escorts near a presidential
    airframe, from the military list;
  * every military-flagged aircraft inside the circles an entry names (Lee 2026-11-02 22:59; areas.py,
    in_areas), past the cap, from the same request;
  * the user's own list (backlog 332, follow.py), per entry: hexes in the shared hex round, at no request of
    their own; call signs in one comma-list request a minute for the instance (_callsign_round).

! THE NATIONWIDE ENFORCEMENT WATCH MOVED TO LIVE TRACK ENFORCEMENT AIRCRAFT (backlog 297, Lee
2026-10-23 23:01 and 2026-10-24 01:29): the EnforcementAircraft list's sourced and detected entries
and every federal law-enforcement registrant. This integration publishes the registrants it finds in
its FAA table for it (enforcement.publish_federal), and with it installed alone shows listed aircraft
only inside its circle (decision G). It read: the list, the federal registrants and the presidential
airframes, 305 hexes, one request a minute (62064b6).

! ONE SHARED POLL (saw_livetrack.adsb_poll): the presidential hexes join the instance's union hex
round, once a minute, with whatever Live Track Enforcement Aircraft asks; the military list goes
through the same pacing and the same backoff, because a feed limits per address. One WatchList per
instance (hass.data).
! THE MILITARY LIST ASKS adsb.fi, AND adsb.lol ONLY AFTER adsb.fi HAS FAILED OR WHILE IT IS IN A SKIP WINDOW (Lee
2026-11-02 22:59, replacing 05_SHARED_LESSONS.md B16's rule for this list too). Measured that night from the box:
adsb.fi hung 25 s, adsb.lol answered /v2/mil in 0.66 s, 132 aircraft; airplanes.live refused the IP with a 403.
"""
from __future__ import annotations

import re
import time
from collections.abc import Callable

from saw_livetrack import adsb_poll as ap

from .areas import Area
from .const import DOMAIN
from .sources.base import Observation

CONSUMER = DOMAIN
SOURCE = ap.FI
MIL_URL = "https://opendata.adsb.fi/api/v2/mil"
MIL_SOURCES = ((ap.FI, MIL_URL), (ap.LOL, "https://api.adsb.lol/v2/mil"))
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
WHY_MILITARY_AREA = "military area"
# A user's own list (follow.py, backlog 332): hexes through the shared hex round, call signs through the round below.
WHY_FOLLOWED = "followed"

# ! THE CALL-SIGN ROUND (backlog 332): every entry's followed call signs in ONE comma-list request a minute, adsb.fi
# then adsb.lol as the military list, through the shared poll's pacing and backoff. Measured 2026-11-11: both
# endpoints take a comma list (bin\lta332_callsign_probe.txt). Chunked so a long union stays a short URL.
CALLSIGN_SOURCES = ((ap.FI, "https://opendata.adsb.fi/api/v2/callsign/"),
                    (ap.LOL, "https://api.adsb.lol/v2/callsign/"))
CALLSIGNS_PER_REQUEST = 100

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
        # Every aircraft on the last military list, for the watch areas (in_areas).
        self._mil_all: dict[str, Observation] = {}
        self._why: dict[str, str] = {}
        self.status = "idle"
        # Followed call signs (backlog 332): per consumer (one per entry), asked as one union.
        self._callsigns: dict[str, frozenset[str]] = {}
        self._cs_at: float | None = None
        self._cs_obs: dict[str, list[Observation]] = {}
        self.callsign_status = "idle"
        poll.set_hexes(CONSUMER, PRESIDENTIAL)

    def set_callsigns(self, consumer: str, callsigns) -> None:
        """The call signs this consumer follows. An empty list removes it."""
        cs = frozenset((c or "").strip().upper() for c in callsigns or () if (c or "").strip())
        if cs:
            self._callsigns[consumer] = cs
        else:
            self._callsigns.pop(consumer, None)

    def release(self, consumer: str) -> None:
        """An entry unloading: its call signs go (its hexes go with the poll's release)."""
        self._callsigns.pop(consumer, None)

    def callsign_union(self) -> list[str]:
        out: set[str] = set()
        for cs in self._callsigns.values():
            out |= cs
        return sorted(out)

    def callsign_observations(self, callsigns) -> list[Observation]:
        """The aircraft broadcasting these call signs on the last answer, or nothing once it is STALE_S old."""
        if self._cs_at is None or self._clock() - self._cs_at > STALE_S:
            return []
        found: dict[str, Observation] = {}
        for c in callsigns:
            for o in self._cs_obs.get((c or "").strip().upper(), ()):
                found.setdefault(o.identity, o)
        return list(found.values())

    async def _callsign_round(self, session, now: float) -> None:
        """One request a minute (a chunk per CALLSIGNS_PER_REQUEST) for the union. A failure keeps the last answer
        until STALE_S, and says so; a non-200 is never "none of them is flying"."""
        union = self.callsign_union()
        if not union:
            self._cs_obs, self._cs_at, self.callsign_status = {}, None, "idle"
            return
        why = []
        for name, url in CALLSIGN_SOURCES:
            found: dict[str, list[Observation]] = {}
            try:
                for part in ap.chunks(union, CALLSIGNS_PER_REQUEST):
                    payload = await self._poll.get_json(session, name, url + ",".join(part))
                    for o in ap.parse_payload(payload if isinstance(payload, dict) else {}, now).values():
                        cs = (o.callsign or "").strip().upper()
                        if cs in part:
                            found.setdefault(cs, []).append(o)
            except ap.SourceError as err:
                why.append(str(err))
                continue
            self._cs_obs, self._cs_at = found, self._clock()
            self.callsign_status = "ok" if name == SOURCE else "ok from %s: %s" % (name, why[0])
            return
        self.callsign_status = "failed: " + "; ".join(why)

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

    def in_areas(self, areas: list[Area]) -> tuple[list[Observation], list[int]]:
        """(each military aircraft inside any of these circles, once; how many in each circle).

        ! An entry's own circles, not the instance's: WatchList is one per instance and each entry names its own.
        ! Nothing once the answer is STALE_S old, as observations(): a failing list does not freeze aircraft on the map.
        """
        counts = [0] * len(areas)
        if self._mil_at is None or self._clock() - self._mil_at > STALE_S:
            return [], counts
        found = []
        for o in self._mil_all.values():
            inside = [i for i, a in enumerate(areas)
                      if ap.km_between(a.latitude, a.longitude, o.latitude, o.longitude) <= a.radius_km]
            for i in inside:
                counts[i] += 1
            if inside:
                found.append(o)
        return found, counts

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
        await self._military_round(session, now, hex_status)
        # Followed call signs (backlog 332), in the same minute, whatever the military list did.
        await self._callsign_round(session, now)

    async def _military_round(self, session, now: float, hex_status: str) -> None:
        payload = source = None
        why = []
        for name, url in MIL_SOURCES:
            try:
                payload = await self._poll.get_json(session, name, url)
            except ap.SourceError as err:
                why.append(str(err))
                continue
            source = name
            break
        if source is None:
            self.status = "military list: %s" % "; ".join(why) if hex_status == "ok" else hex_status
            return
        mil = ap.parse_payload(payload if isinstance(payload, dict) else {}, now)
        self._mil_all = mil
        hexed = {o.identity: o for o in self._poll.hex_observations(CONSUMER)}
        pres = [o for h, o in {**mil, **hexed}.items() if h in PRESIDENTIAL]
        reasons = from_military(mil, pres)
        # A presidential airframe the hex round missed is still one.
        keep = [mil[h] for h in list(reasons) + [h for h in PRESIDENTIAL if h in mil]]
        self._mil, self._why, self._mil_at = keep, reasons, self._clock()
        if hex_status != "ok":
            self.status = hex_status
        else:
            self.status = "ok" if source == SOURCE else "ok, military list from %s" % source


def parse(payload, now: float) -> dict[str, Observation]:
    """The answer's records, on the feed's own clock (saw_livetrack.adsb_poll)."""
    return ap.parse_payload(payload, now)


__all__ = ["PRESIDENTIAL", "WHY_FOLLOWED", "WatchList", "from_military"]
