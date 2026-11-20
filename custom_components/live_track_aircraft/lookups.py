"""Everything a poll reads from disk, resolved in ONE executor job per poll.

hacs/default#14501 item 2 (Frenck, 2026-11-19): _record looked up, per
aircraft, on the event loop, the legs and leg times of its call sign
(routes.py, SQLite), every airport those legs name (airports.py, a stat and
SQLite) and its registered owner (saw-livetrack's OwnerRegistry, SQLite). With
a busy sky that was hundreds of SQLite reads every poll on the loop.

Since 0.1.3 the coordinator gathers every observation the poll will draw (the
circle, the watch list, the military areas, the user's own watch list), calls
resolve() ONCE in hass.async_add_executor_job, and _record reads only the
PollLookups it returns. resolve() also builds every time zone those airports
name (route_check.warm_zones), because a first ZoneInfo reads tzdata from disk
(item 3).

! A key that is not in the PollLookups answers as "nothing on file": no legs,
no times, no airport, no owner. That is what a miss looked like before, so a
lookup the gathering did not foresee costs that aircraft its route for one
poll, never a disk read on the loop. The one known case: an adsbdb route that
arrives (async_drain, in the background) between the gathering and _record;
the next poll resolves its airports.

Nothing here imports Home Assistant, so it tests without it.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from .route_check import warm_zones


class PollLookups:
    """One poll's answers, by the exact key _record will ask with."""

    __slots__ = ("_legs", "_times", "_airports", "_owners")

    def __init__(self) -> None:
        self._legs: dict[Any, list] = {}
        self._times: dict[Any, dict] = {}
        self._airports: dict[Any, dict | None] = {}
        self._owners: dict[Any, Any] = {}

    def legs(self, callsign) -> list:
        return self._legs.get(callsign, [])

    def leg_times(self, callsign) -> dict:
        return self._times.get(callsign, {})

    def airport(self, code) -> dict | None:
        return self._airports.get(code)

    def owner(self, hex_code):
        return self._owners.get(hex_code)

    def __repr__(self) -> str:
        return "PollLookups(%d callsigns, %d airports, %d owners)" % (
            len(self._legs), len(self._airports), len(self._owners))


def resolve(routes, airports, owner_lookup: Callable[[Any], Any] | None,
            observations: Iterable, extra_codes: Iterable = ()) -> PollLookups:
    """BLOCKS: run it in the executor. One PollLookups for these observations.

    routes       : routes.RouteStore (legs, leg_times)
    airports     : airports.AirportStore (lookup)
    owner_lookup : registrations.lookup_owner, or None
    observations : anything with .callsign and .identity
    extra_codes  : airport codes from elsewhere (adsbdb's cached routes)
    Every failure of one lookup degrades to "nothing on file" for that key, as
    each store already does; nothing raises out of here.
    """
    out = PollLookups()
    codes: set = set()
    for obs in observations:
        cs = getattr(obs, "callsign", None)
        if cs and cs not in out._legs:
            try:
                legs = routes.legs(cs) if routes is not None else []
            except Exception:  # noqa: BLE001 - a store fault is a miss, never a failed poll
                legs = []
            try:
                times = routes.leg_times(cs) if routes is not None else {}
            except Exception:  # noqa: BLE001
                times = {}
            out._legs[cs], out._times[cs] = legs, times
            for dep, arr, _n in legs:
                codes.add(dep)
                codes.add(arr)
        hex_code = getattr(obs, "identity", None)
        if owner_lookup is not None and hex_code and hex_code not in out._owners:
            try:
                out._owners[hex_code] = owner_lookup(hex_code)
            except Exception:  # noqa: BLE001
                out._owners[hex_code] = None
    codes.update(c for c in extra_codes if c)
    zones = set()
    for code in codes:
        try:
            found = airports.lookup(code) if airports is not None else None
        except Exception:  # noqa: BLE001
            found = None
        out._airports[code] = found
        if found and found.get("tz"):
            zones.add(found["tz"])
    warm_zones(zones)
    return out
