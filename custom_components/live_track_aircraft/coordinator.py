"""Coordinator: poll a source, hold two DISTINCT fixes per aircraft.

Contract: 10_SEED/05_SHARED_LESSONS.md section D.
"""

from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.location import distance as _distance

from .const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MAX_AIRCRAFT,
    CONF_RADIUS_KM,
    CONF_SCAN_INTERVAL,
    DEFAULT_MAX_AIRCRAFT,
    DEFAULT_RADIUS_KM,
    DEFAULT_SCAN_INTERVAL,
    MAX_SEGMENT_S,
    MAX_TRANSIENT_FAILURES,
)
from .sources.adsb import fetch
from .sources.base import Observation, SourceError

_LOGGER = logging.getLogger(__name__)

Fix = tuple[float, float, int]  # lat, lon, observed_at


class AircraftCoordinator(DataUpdateCoordinator):
    """Poll an ADS-B source and expose one record per aircraft."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        opts = {**entry.data, **entry.options}
        self.latitude = float(opts.get(CONF_LATITUDE, hass.config.latitude))
        self.longitude = float(opts.get(CONF_LONGITUDE, hass.config.longitude))
        self.radius_km = float(opts.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM))
        self.max_aircraft = int(opts.get(CONF_MAX_AIRCRAFT, DEFAULT_MAX_AIRCRAFT))

        super().__init__(
            hass,
            _LOGGER,
            name="Live Track Aircraft",
            update_interval=timedelta(
                seconds=int(opts.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
            ),
        )
        self._session = async_get_clientsession(hass)

        # TWO fixes per aircraft, keyed on the ICAO hex.
        #
        # ! They must be DISTINCT observations, not merely consecutive ones.
        # Measured on Live Track South Shore 2026-09-11: when the poll
        # interval and the publish interval are close, they ALIAS and roughly
        # one poll in three returns an observation identical to the last.
        # Storing those duplicates collapses the segment to zero length, so
        # course_deg and the previous_* fields appear and vanish on alternate
        # updates - which the map renders as a stutter. Every individual
        # omission is correct, which is what makes it hard to see; only the
        # sequence is wrong.
        #
        # ! This integration is exposed to it. The scan floor is 15 s and the
        # measured p50 update gap is 10 s, but slow and stationary aircraft
        # sit at p50 15 s and p95 80 s - so duplicates are certain for part
        # of the population.
        self._fix: dict[str, Fix] = {}
        self._prev_fix: dict[str, Fix] = {}

        self._consecutive_failures = 0
        self._last_good: dict[str, Any] | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        now = time.time()
        try:
            source_name, observations = await fetch(
                self._session, self.latitude, self.longitude, self.radius_km, now
            )
        except SourceError as err:
            self._consecutive_failures += 1
            if (self._consecutive_failures <= MAX_TRANSIENT_FAILURES
                    and self._last_good is not None):
                # ! Serve the previous result rather than blanking the map.
                # A rate-limited coordinator that returns nothing looks
                # EXACTLY like an empty sky - no error, no log line, aircraft
                # simply gone. The count sensor's source attribute and the
                # entity ages are what make this visible as stale rather than
                # absent.
                _LOGGER.debug(
                    "All sources failed (%s consecutive): %s; serving the "
                    "previous result", self._consecutive_failures, err)
                return self._last_good
            raise UpdateFailed(
                f"all sources failed ({self._consecutive_failures} consecutive): {err}"
            ) from err
        self._consecutive_failures = 0

        aircraft: dict[str, dict[str, Any]] = {}
        for obs in observations:
            rec = self._record(obs)
            if rec is not None:
                aircraft[obs.identity] = rec

        # The TRUE number in radius, before any cap. A capped count cannot
        # distinguish a quiet sky from a clipped list.
        in_range = len(aircraft)

        # ! The cap is a GUARD RAIL, not a display control, and if it ever
        # bites it says so. Silent truncation is indistinguishable from a
        # dead feed - measured on Live Track Ships, a cap of 50 truncated 36%
        # of samples. Nearest first, so what survives is what is overhead.
        capped = False
        if in_range > self.max_aircraft:
            capped = True
            _LOGGER.warning(
                "Live Track Aircraft: %s aircraft in radius, publishing the "
                "nearest %s. Raise max_aircraft if this is not what you want.",
                in_range, self.max_aircraft)
            nearest = sorted(aircraft.values(), key=lambda r: r["distance_km"])
            aircraft = {r["identity"]: r for r in nearest[: self.max_aircraft]}

        # Forget fixes for aircraft no longer in the feed, so one returning
        # tomorrow starts a fresh segment rather than interpolating across a
        # gap of hours.
        for gone in [k for k in self._fix if k not in aircraft]:
            del self._fix[gone]
            self._prev_fix.pop(gone, None)

        result = {
            "aircraft": aircraft,
            "in_range": in_range,
            "published": len(aircraft),
            "capped": capped,
            "source": source_name,
            "radius_km": self.radius_km,
        }
        self._last_good = result
        return result

    def _record(self, obs: Observation) -> dict[str, Any] | None:
        """One Observation to the record the entities read."""
        here = (round(obs.latitude, 6), round(obs.longitude, 6))

        # Advance only on a genuinely NEW observation - see the note on
        # _fix above. A duplicate poll re-emits the same segment instead of
        # destroying it.
        #
        # ! AND NEVER GO BACKWARDS. A regressing observed_at produces a
        # negative segment, which fails the 0 < seg guard below and drops the
        # previous_* fields - the same visible stutter as a duplicate.
        # Measured 2026-09-11 before the source was moved onto the feed's own
        # clock; belt and braces now that it is, because a source that
        # reorders records must not be able to reintroduce it.
        cur = self._fix.get(obs.identity)
        is_new = cur is None or (
            obs.observed_at > cur[2] or
            (obs.observed_at == cur[2] and (cur[0], cur[1]) != here)
        )
        if is_new:
            if cur is not None:
                self._prev_fix[obs.identity] = cur
            self._fix[obs.identity] = (here[0], here[1], obs.observed_at)

        latest = self._fix[obs.identity]
        prev = self._prev_fix.get(obs.identity)

        metres = _distance(self.latitude, self.longitude, here[0], here[1])
        if metres is None:
            return None

        rec: dict[str, Any] = {
            "identity": obs.identity,
            "latitude": here[0],
            "longitude": here[1],
            "observed_at": latest[2],
            "last_seen": latest[2],
            "distance_km": metres / 1000,
            # ! callsign -> type code -> hex, and NEVER blank. Measured
            # 2026-09-10: 9.5% of aircraft in a poll carried no callsign, and
            # that was ordinary ADS-B traffic between transmissions. One
            # marker in ten would otherwise be an unlabelled dot.
            "marker_label": obs.callsign or obs.type_code or obs.identity.upper(),
        }

        # Absent values are OMITTED, never sentinels (D0): a wrong value is
        # worse than a missing one because the consumer cannot tell.
        for key, value in (
            ("callsign", obs.callsign),
            ("type_code", obs.type_code),
            ("registration", obs.registration),
            ("emitter_category", obs.emitter_category),
            ("squawk", obs.squawk),
            ("altitude_m", obs.altitude_m),
            ("speed_kmh", obs.speed_kmh),
            ("vertical_rate_ms", obs.vertical_rate_ms),
            # ! Two different fields. heading_deg is where it POINTS and is
            # present on about a quarter of records; course_deg is where it
            # is GOING. This is the first integration here with both.
            ("heading_deg", obs.heading_deg),
            ("course_deg", obs.course_deg),
        ):
            if value is not None:
                rec[key] = value

        # ! previous_* let the map INTERPOLATE between two MEASURED fixes.
        # There is no max_extrapolation_s here and that is deliberate: this
        # integration PASSES the D3b eligibility test and declines. 73.5% of
        # update events carry course and motion together, so extrapolation is
        # permitted - but interpolation covers 100% of aircraft, animates
        # only between observed points, and cannot be wrong during a turn, a
        # hold or an approach. "No extrapolation" is NOT "no motion".
        if prev is not None:
            segment = latest[2] - prev[2]
            if 0 < segment <= MAX_SEGMENT_S:
                rec["previous_latitude"] = prev[0]
                rec["previous_longitude"] = prev[1]
                rec["previous_observed_at"] = prev[2]
                rec["segment_duration_s"] = segment

        return rec
