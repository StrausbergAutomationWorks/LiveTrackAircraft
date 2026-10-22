"""Coordinator: poll a source, hold two DISTINCT fixes per aircraft.

Contract: 10_SEED/05_SHARED_LESSONS.md section D.
"""

from __future__ import annotations

import logging
import re
import time
from datetime import UTC, datetime, timedelta
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
    SLOW_GROUND_SPEED_KMH,
)
from .sources.adsb import BACKOFF, fetch, short_floor
from .sources.base import Observation, SourceError
from . import icons
from .aircraft import classify, describe_aircraft, lookup_manufacturer
from .pictures import DIR_NAME as PICTURES_DIR, Overrides, apply as apply_picture
from .airframe import map_layer
from .map_keys import object_ids, registry_registration
from .airlines import lookup_operator
from .registrations import from_feed_flags, lookup_government, lookup_owner, prettify_owner
from .routes import RouteStore
from .airports import AirportStore
from .route_check import FILED, choose_leg
from .adsbdb import choose as adsbdb_choose
from .airport_display import shown_code, shown_name
from .eta import estimated_arrival
from .watch import PRESIDENTIAL

_LOGGER = logging.getLogger(__name__)

Fix = tuple[float, float, int]  # lat, lon, observed_at


def _iso(epoch_s: int) -> str:
    """Epoch seconds -> ISO 8601 UTC, the D0 form for an instant.

    ! Fixes stay integer epoch seconds INTERNALLY - the new/duplicate test
    and segment_duration_s are integer arithmetic on them. Only the emitted
    attribute is converted, here, at the boundary.
    """
    return datetime.fromtimestamp(epoch_s, UTC).isoformat()


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
        # Last bearing actually used for a marker, per aircraft. A slow
        # aircraft's course is noise, and this is what is held instead.
        self._angle: dict[str, float] = {}
        # The last record actually published, per aircraft. An observation
        # OLDER than the retained fix re-publishes this unchanged - see
        # _record. SSOT "2026-09-22 EVENING - THE STALE BOUNCE".
        self._last_rec: dict[str, dict[str, Any]] = {}

        self._consecutive_failures = 0
        self._last_good: dict[str, Any] | None = None
        # How many aircraft the last good poll carried, before any filter:
        # what the short-answer guard in sources/adsb.py compares against.
        self._last_obs_count: int | None = None
        # Tiltrotor picture per aircraft (cruise or hover), for the speed gap.
        self._tilt_forward: dict[str, bool] = {}

        # The shared route artifact. Absent or stale means no route fields
        # and nothing else changes - see routes.py.
        self.routes = RouteStore(hass)
        # The instance's RouteDownloader (route_download.py), set by
        # __init__.py; read only for the count sensor's status attribute.
        self.route_download = None
        # The instance's AirportDownloader (airport_download.py), set by
        # __init__.py; only its status is read here.
        self.airport_download = None
        # The instance's adsbdb client (adsbdb.py, backlog 292), set by
        # __init__.py: routes for callsigns FiledRoutesDB does not hold.
        # None means filed routes only.
        self.adsbdb = None
        # The shared airport table: coordinates and time zones per airport.
        # Absent means every route reports route_check "unchecked" and
        # nothing else changes - see airports.py.
        self.airports = AirportStore(hass)
        # The user's own pictures, by hex (pictures.py, Lee 2026-10-21).
        self.pictures = Overrides(hass.config.path(PICTURES_DIR))
        # The worldwide watch list (watch.py), set by __init__.py; None
        # means the circle only.
        self.watch = None

    async def _async_update_data(self) -> dict[str, Any]:
        now = time.time()
        try:
            # ! A 200 carrying under half the last good count is a SHORT
            # answer, not an empty sky (measured 2026-09-25, sources/adsb.py).
            source_name, observations = await fetch(
                self._session, self.latitude, self.longitude, self.radius_km, now,
                min_expected=short_floor(self._last_obs_count),
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
                # The aircraft are the last good ones; the backoff is NOW.
                return {**self._last_good, "source_backoff": BACKOFF.status()}
            raise UpdateFailed(
                f"all sources failed ({self._consecutive_failures} consecutive): {err}"
            ) from err
        self._consecutive_failures = 0
        self._last_obs_count = len(observations)

        # The pictures folder, listed at most once a minute, off the loop.
        if self.pictures.due(now):
            await self.hass.async_add_executor_job(self.pictures.scan)

        aircraft: dict[str, dict[str, Any]] = {}
        for obs in observations:
            rec = self._record(obs)
            if rec is not None:
                aircraft[obs.identity] = rec

        # adsbdb lookups queued by _record for FiledRoutesDB misses (backlog
        # 292) are worked in the BACKGROUND, so a slow answer never holds a
        # poll up; the next poll reads them from the cache. One drain at a
        # time: a second start returns at once.
        if self.adsbdb is not None and self.adsbdb.pending:
            self.hass.async_create_background_task(
                self.adsbdb.async_drain(self._session), "live_track_aircraft_adsbdb")

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

        # ! THE WATCH LIST, ADDED AFTER THE CAP (watch.py, Lee 2026-10-21):
        # the presidential airframes and every law-enforcement aircraft in
        # the government table, wherever they are. One adsb.fi request a
        # minute, shared by every entry. An aircraft already in the circle is
        # only tagged, never built twice; the cap never drops a watched one.
        watched = 0
        if self.watch is not None:
            if self.watch.due():
                await self.watch.async_fetch(self._session, now)
            for obs in self.watch.observations():
                why = self.watch.why(obs.identity)
                if obs.identity in aircraft:
                    aircraft[obs.identity]["watch"] = why
                    continue
                rec = self._record(obs)
                if rec is None:
                    continue
                rec["watch"] = why
                rec["outside_radius"] = True
                aircraft[obs.identity] = rec
                watched += 1

        # Forget fixes for aircraft no longer in the feed, so one returning
        # tomorrow starts a fresh segment rather than interpolating across a
        # gap of hours.
        for gone in [k for k in self._fix if k not in aircraft]:
            del self._fix[gone]
            self._prev_fix.pop(gone, None)
            self._angle.pop(gone, None)
            self._last_rec.pop(gone, None)
            self._tilt_forward.pop(gone, None)

        result = {
            "aircraft": aircraft,
            "in_range": in_range,
            "published": len(aircraft),
            "capped": capped,
            "source": source_name,
            # {source: resume time} for sources skipped after HTTP 429;
            # empty when none is. Backlog item 244.
            "source_backoff": BACKOFF.status(),
            "radius_km": self.radius_km,
            # Watched aircraft outside the circle (watch.py), and the watch
            # list's last round: idle, ok, waiting, or the failure.
            "watched": watched,
            "watch_status": getattr(self.watch, "status", None),
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

        # ! DROP A STALE OBSERVATION ENTIRELY. An observation OLDER than the
        # fix already held is not news; it is the other feed not having caught
        # up on this aircraft yet. Until 2026-09-22 the fix correctly refused
        # to advance, but the record was still built from THIS observation -
        # its position, course, speed and altitude, under the NEWER
        # observed_at - so the marker was thrown back along its own track and
        # forward again on the next poll: an exact A-B-A. Measured: 15 of 27
        # reversals in a 10-minute capture, while adsb.lol and adsb.fi
        # alternated on every poll. Every field of a stale observation is
        # stale, so none of it is used - not even for the held bearing.
        # Re-publish what was already published instead. Dropping the
        # aircraft from the result would be worse: the forget loop would
        # discard both fixes and it would return as a fresh segment.
        #
        # ! EQUAL IS NOT NEWER EITHER. The same capture found 10 events where
        # the two feeds reported the SAME whole second at positions 1-67 m
        # apart (0.0-1.9 s of travel) - two decodes of one second. Treated as
        # new, each one made a zero-length segment, dropped previous_* and
        # flicked the marker back and forth. Within ONE feed, the same second
        # at a different position cannot occur 15 s apart: observed_at is
        # feed now minus seen_pos, so a repeat second is a repeat fix.
        # SSOT "2026-09-22 EVENING - THE STALE BOUNCE".
        if cur is not None and obs.observed_at <= cur[2]:
            held = self._last_rec.get(obs.identity)
            if held is not None:
                return held

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
            "observed_at": _iso(latest[2]),
            "last_seen": _iso(latest[2]),
            "distance_km": metres / 1000,
        }

        # Absent values are OMITTED, never sentinels (D0): a wrong value is
        # worse than a missing one because the consumer cannot tell.
        for key, value in (
            ("callsign", obs.callsign),
            ("registration", obs.registration),
            ("emitter_category", obs.emitter_category),
            ("squawk", obs.squawk),
            ("altitude_m", obs.altitude_m),
            ("speed_kmh", obs.speed_kmh),
            ("vertical_rate_ms", obs.vertical_rate_ms),
            # ! Two different fields. heading_deg is where it POINTS and is
            # measured at roughly 1% of AIRBORNE aircraft - it is a ground
            # field. course_deg is where it is GOING.
            ("heading_deg", obs.heading_deg),
            ("course_deg", obs.course_deg),
        ):
            if value is not None:
                rec[key] = value

        rec.update(self._describe(obs))
        # The presidential airframes are named by hex (watch.PRESIDENTIAL),
        # never by callsign: a callsign proves nothing about who is aboard.
        if obs.identity in PRESIDENTIAL:
            rec["presidential_airframe"] = PRESIDENTIAL[obs.identity]

        # ! THE MARKER LABEL IS DECIDED LAST, because it depends on what the
        # lookups returned. The map renders this attribute and nothing else.
        rec["marker_label"] = _marker_label(obs, rec)

        # --- route ------------------------------------------------------
        # ! Read from the shared artifact, never resolved live. No artifact
        # means no route keys at all - the aircraft is still tracked.
        #
        # ! EVERY LEG IS TESTED, since 2026-09-22. The artifact holds every
        # leg a callsign has been seen on; choose_leg tests each against this
        # aircraft's position (route_check.py) using airport coordinates from
        # the shared airport table, and prefers a plausible leg whose
        # destination lies AHEAD on the course - which is what separates A-B
        # from B-A. Before this, the most-observed leg was published unchecked.
        #
        # ! AN IMPLAUSIBLE ROUTE IS FLAGGED, NOT HIDDEN - Lee, 2026-09-22, to
        # work on problems. route_check says which: plausible | unchecked |
        # implausible. Whether to suppress implausible routes is a later call.
        #
        # ! FILED routes are judged with the FILED profile (Lee, 2026-09-22):
        # filed flight plans are current, so they carry more weight than a
        # schedule snapshot like adsbdb. See route_check.PROFILES. Every
        # rejecting threshold there is relative, so it holds worldwide.
        #
        # ! WHICH LEG uses TIMES and FLIGHT PHASE, since 2026-09-23 (Lee):
        # the leg whose typical departure-to-arrival window holds the time of
        # this fix outranks history, and a low aircraft's climb or descent
        # says which END of the leg is near. See route_check "WHICH LEG".
        # Times are optional; without them the ranking falls back.
        leg, verdict, considered = choose_leg(
            self.routes.legs(obs.callsign), self.airports.lookup,
            here[0], here[1],
            None if obs.altitude_m is None else obs.altitude_m * 3.28084,
            obs.course_deg, profile=FILED,
            vertical_rate_ms=obs.vertical_rate_ms,
            now=latest[2],
            times=self.routes.leg_times(obs.callsign))
        source = "saw_filed_routes"
        # ! ADSBDB ONLY WHEN FiledRoutesDB HAS NO ROUTE AT ALL (backlog 292).
        # FiledRoutesDB is US-filed flights only, so abroad it is always a
        # miss. Lee 2026-10-19: every miss falls through, in the US too. A
        # filed leg judged implausible does NOT fall through: filed carries
        # more weight. The answer comes from the in-memory cache; a callsign
        # not asked yet is queued and gets its route on a later poll. Judged
        # with the strict SCHEDULE profile and published only when PLAUSIBLE
        # (adsbdb.choose) - unlike a filed route, which is flagged.
        if not leg and self.adsbdb is not None:
            leg, verdict, considered = adsbdb_choose(
                self.adsbdb.route(obs.callsign, latest[2]), self.airports.lookup,
                here[0], here[1],
                None if obs.altitude_m is None else obs.altitude_m * 3.28084,
                obs.course_deg, vertical_rate_ms=obs.vertical_rate_ms, now=latest[2])
            source = "adsbdb"
        if leg:
            # ! The codes and names are what is SHOWN (airport_display.py,
            # Lee 2026-10-19: KDJT/DJT published as KPBI/PBI, named Palm Beach
            # International Airport). Everything above used the codes as
            # reported; this changes only what is published.
            for end in ("origin", "destination"):
                reported = leg[end + "_icao"]
                rec[end + "_icao"] = shown_code(reported)
                found = self.airports.lookup(reported)
                name = shown_name(reported, (found or {}).get("ident"), (found or {}).get("name"))
                if name:
                    rec[end + "_name"] = name
            # How often FiledRoutesDB saw the leg; adsbdb has no such count,
            # and an absent value is omitted, never a sentinel (D0).
            if leg.get("route_observations") is not None:
                rec["route_observations"] = leg["route_observations"]
            rec["route_source"] = source
            rec["route_check"] = verdict
            rec["route_check_rule"] = leg["route_check_rule"]
            rec["route_time_check"] = leg["route_time_check"]
            rec["route_candidates"] = considered
            for key in ("origin_tz", "destination_tz"):
                if leg.get(key):
                    rec[key] = leg[key]
            # Lee 2026-10-03: an ETA by Flights Above's method (eta.py),
            # published for every chosen leg, implausible ones included: the
            # card marks those "?" rather than hiding them.
            eta = estimated_arrival(leg, here[0], here[1], obs.speed_kmh,
                                    obs.emitter_category, latest[2])
            if eta is not None:
                rec["arrival_estimated_at"] = _iso(round(eta))

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
                rec["previous_observed_at"] = _iso(prev[2])
                rec["segment_duration_s"] = segment

        self._last_rec[obs.identity] = rec
        return rec

    # ------------------------------------------------------------------
    # Enrichment. Nothing in the ADS-B feed names an aircraft or an
    # operator: `r` is an N-number and `t` is a four-letter designator.
    # ! A watcher gets nothing from "N746SK". These lookups are the whole
    # difference between a dot and "SkyWest CRJ-700".
    #
    # ! ALL FOUR MODULES ARE LIFTED VERBATIM and every one degrades to None
    # on any failure path, so enrichment can never break tracking.
    # ------------------------------------------------------------------
    # ! NO LONGER A STATICMETHOD, deliberately. It was pure while every
    # enrichment was a lookup. It now needs two pieces of instance state: the
    # last bearing used for this aircraft, so a slow one can hold it, and
    # whether the map card is doing the rotating.
    def _describe(self, obs: Observation) -> dict[str, Any]:
        out: dict[str, Any] = {}

        # --- type -------------------------------------------------------
        if obs.type_code:
            out["aircraft_type"] = obs.type_code
            name = describe_aircraft(obs.type_code)
            if name:
                out["aircraft_name"] = name
            maker = lookup_manufacturer(obs.type_code)
            if maker:
                out["aircraft_manufacturer"] = maker

        # --- what KIND of aircraft, and what to draw --------------------
        # ! From emitter_category, which the feed supplies on effectively
        # every aircraft. A7 is rotorcraft, and this integration is called
        # Aircraft precisely because rotorcraft are not an edge case here.
        icon_category, category_label, icon = classify(
            obs.emitter_category, obs.type_code)
        out["icon_category"] = icon_category
        out["category_label"] = category_label
        out["icon"] = icon
        # ! THE LAYER, from the same decider as the silhouette and the tone
        # (airframe.is_rotorcraft), so they cannot disagree: air_low for a
        # rotorcraft, air otherwise. The card owns the offsets (D10).
        out["map_layer"] = map_layer(obs.emitter_category, obs.type_code)

        # --- the marker silhouette, pointing where it is going ----------
        # ! ROTATE BY HEADING, FALL BACK TO COURSE - 05_SHARED_LESSONS D2.
        # heading_deg is where the aircraft POINTS and course_deg is where it
        # is GOING; in still air they agree and in a crosswind they do not.
        # Measured 2026-09-11, heading is a GROUND field here: present on
        # roughly 1% of AIRBORNE aircraft, so course does nearly all the work
        # - which is exactly what D2 calls the documented fallback.
        key = icons.pick(obs.emitter_category, obs.type_code, icon_category,
                         out.get("aircraft_name"))
        # One airframe's own icon, by hex (icons.HEX_KEYS: the VC-25As).
        key = icons.HEX_KEYS.get(obs.identity, key)
        if key == "tiltrotor":
            fwd = icons.tiltrotor_forward(
                self._tilt_forward.get(obs.identity), obs.speed_kmh)
            self._tilt_forward[obs.identity] = fwd
            if fwd:
                key = "tiltrotorfwd"
        bearing = obs.heading_deg if obs.heading_deg is not None else obs.course_deg
        basis = "heading" if obs.heading_deg is not None else "course"

        # ! A SLOW AIRCRAFT HAS NO USEFUL COURSE. Course over ground is the
        # direction of TRAVEL, so it is undefined when there is no travel. A
        # hovering or pedal-turning helicopter reports a different value every
        # cycle and the marker spins on the spot while the aircraft sits
        # still. Rotorcraft are not an edge case in this integration.
        #
        # Below the floor the LAST GOOD BEARING IS HELD rather than followed,
        # and the basis says so. Heading is different: it is where the
        # airframe POINTS, it stays meaningful at zero groundspeed, and it is
        # therefore never held.
        if (basis == "course" and obs.speed_kmh is not None
                and obs.speed_kmh < SLOW_GROUND_SPEED_KMH):
            held = self._angle.get(obs.identity)
            if held is not None:
                bearing = held
                basis = "held"

        rotatable = icons.is_rotatable(key)
        angle = icons.quantise(bearing) if rotatable else None
        if bearing is not None and basis != "held":
            self._angle[obs.identity] = bearing

        out["icon_rotatable"] = rotatable
        if angle is not None:
            out["icon_rotation_deg"] = angle
            out["icon_rotation_basis"] = basis

        # ! COLOUR AND SIZE ARE DECIDED HERE, and both carry meaning. The
        # silhouette used to be black on a near-black disc - ha-map-card
        # fills every picture marker with var(--card-background-color), and
        # .marker.dark hardcodes #1c1c1c. We now paint the badge ourselves,
        # so the fill is free to say something instead of merely being
        # visible. Weight comes from emitter_category because the artwork
        # does not carry size - measured 2026-09-12.
        #
        # ! is_government is resolved BELOW this point in the original
        # order, so it is looked up here rather than read from `out`.
        gov_row = lookup_government(obs.identity)
        gov_now = gov_row is not None
        # The feed's flags (dbFlags): military, and PIA. registrations.py.
        military, gov_cat, feed_extra = from_feed_flags(
            obs.db_flags, obs.own_op, gov_row)
        # ! THE PICTURE IS NEVER ROTATED AND NEVER ON A DISC (Lee,
        # 2026-09-25): the card turns the marker from icon_rotation_deg, and
        # an angle in the image as well would double the turn.
        out["entity_picture"] = icons.picture_url(
            key, icons.tone_for(gov_now, icon_category, gov_cat, military),
            icons.weight_for(obs.emitter_category),
            lights=icons.lights_for(gov_cat))
        # ! The user's own picture for this hex wins, drawn upright.
        own = getattr(self, "pictures", None)
        apply_picture(out, own.url(obs.identity) if own is not None else None)

        # --- operator ---------------------------------------------------
        # ("UAL", "United Airlines") a known airline
        # ("ZZZ", None)              looks like a designator, not in the table
        # (None,  "Private")         flying under a US registration
        # (None,  None)              no usable callsign
        operator_code, operator = lookup_operator(obs.callsign)
        if operator_code:
            out["operator_code"] = operator_code
        if operator:
            out["operator"] = operator

        # --- government -------------------------------------------------
        # ! The single strongest reason the table exists: police, fire and
        # air-ambulance rotorcraft read "Private" without it.
        #
        # ! The returned keys are registration / operator / operator_category
        # / operator_state, and `operator` is ALREADY prettified by the
        # registry. Written first against owner/name/category, which exist
        # nowhere in this module - it would have produced no government names
        # at all, silently, because every miss degrades to None.
        gov = lookup_government(obs.identity)
        if gov:
            out["is_government"] = True
            if gov.get("operator"):
                # A real airline designator still wins; this beats a
                # registry title holder.
                out["operator"] = out.get("operator") or gov["operator"]
                out["operator_name_source"] = "government"
            if gov.get("operator_category"):
                out["operator_category"] = gov["operator_category"]
            if gov.get("operator_state"):
                out["operator_state"] = gov["operator_state"]
            for k in ("operator_short", "identified_by"):
                if gov.get(k):
                    out[k] = gov[k]
            if gov.get("registration") and not out.get("registration"):
                out["registration"] = gov["registration"]
        else:
            out["is_government"] = False

        # --- the feed's own flags (dbFlags) -----------------------------
        # A real airline designator still wins over the feed's owner text.
        for k, v in feed_extra.items():
            if k in ("operator", "operator_name_source") and out.get("operator") not in (None, "Private"):
                continue
            out[k] = v

        # --- identifiers for the shared map (D11) -----------------------
        # ! icao24 is our identity; registration ONLY as the FAA registry
        # states it for this Mode S code, never the feed's `r` (map_keys.py).
        owner_row = lookup_owner(obs.identity)
        ids = object_ids(obs.identity, registry_registration(owner_row, gov))
        if ids:
            out["object_ids"] = ids

        # --- registered owner -------------------------------------------
        # ! THE TITLE HOLDER, NOT THE OPERATOR. N964AV is "Avianca" to
        # adsbdb and "Bank of Utah Trustee" to the FAA, so this must never
        # displace a real operator name - it is the fallback that always
        # works. Order: airline designator -> government table -> registry.
        if not out.get("operator") or out.get("operator") == "Private":
            owner = owner_row
            if owner:
                name = owner.get("owner") if isinstance(owner, dict) else owner
                if name:
                    out["operator"] = prettify_owner(name)
                    out["operator_name_source"] = "registry"
                if isinstance(owner, dict) and owner.get("category"):
                    out.setdefault("operator_category", owner["category"])

        # --- climb ------------------------------------------------------
        # Derived, not measured: a label for a rate we already publish.
        if obs.vertical_rate_ms is not None:
            if obs.vertical_rate_ms > 0.5:
                out["climb_status"] = "climbing"
            elif obs.vertical_rate_ms < -0.5:
                out["climb_status"] = "descending"
            else:
                out["climb_status"] = "level"

        return out


# --------------------------------------------------------------------------
# The marker label.
#
# ! THIS ATTRIBUTE IS THE ENTIRE MAP DISPLAY. auto-entities renders
# marker_label beside each marker at size 28 and nothing else, so it is a
# short answer to "what is that", not a description.
#
# ! THE RULE CHANGED 2026-09-11, and the reason is worth keeping. It was
# callsign -> type code -> hex, decided when phase 1 had no operator lookup at
# all. With enrichment in, the callsign is the BEST label for an airliner and
# the WORST for general aviation: measured on 68 live aircraft, 25 markers -
# 36.8% - read as a bare N-number while ALL 25 held an operator name, 21 of
# them from the registry. The map was showing tail numbers while "Lewis
# University" sat one tap away.
#
# ! An airline callsign IS the identity. AAL1782 is exactly what belongs on
# that marker. A registration is not an identity to a watcher - nobody
# recognises N674MA, and everybody recognises the flight school.
# --------------------------------------------------------------------------

# A callsign that is really a registration: US N-numbers, and the common
# foreign hyphenated forms (C-GEPW, G-ABCD, D-EFGH).
_LOOKS_LIKE_REGISTRATION = re.compile(
    r"^(N\d[A-Z0-9]*|[A-Z]{1,2}-[A-Z0-9]{3,5})$")

# Long enough to be useful, short enough for a busy map.
MAX_LABEL_CHARS = 22


def _marker_label(obs: Observation, rec: dict[str, Any]) -> str:
    """Never blank. Measured 2026-09-10: 9.5% of aircraft carry no callsign."""
    callsign = (obs.callsign or "").strip()

    if callsign and not _LOOKS_LIKE_REGISTRATION.match(callsign.upper()):
        # An airline or military callsign. This is the identity.
        return callsign

    if rec.get("presidential_airframe"):
        return rec["presidential_airframe"]

    # ! A PRIVACY ICAO ADDRESS (PIA) is a temporary hex; the operator chose
    # not to be identified (Lee 2026-10-21: shown as "identity hidden").
    if rec.get("identity_hidden"):
        return "Identity hidden"

    # ! LAW ENFORCEMENT BY AGENCY (Lee 2026-10-21): DHS, CBP, FBI, USMS, ICE
    # rather than a truncated name; a state or local force by its shortened
    # name (registrations.operator_short).
    short = rec.get("operator_short")
    if short:
        return _shorten(short)

    # A registration, or nothing at all. Say something a watcher can use.
    operator = rec.get("operator")
    if operator and operator != "Private":
        return _shorten(operator)

    name = rec.get("aircraft_name")
    if name:
        return _shorten(name)

    # ! The tail number is the LAST resort, not the first - and the hex
    # behind it, so a marker is never unlabelled.
    return callsign or obs.type_code or obs.identity.upper()


def _shorten(text: str) -> str:
    """Trim a company name to something a 28px label can carry."""
    out = text.strip()
    if len(out) <= MAX_LABEL_CHARS:
        return out
    # Drop a trailing corporate form before truncating mid-word.
    for tail in (" Llc", " Inc", " Corp", " Co", " Ltd", " Trustee", " Trust"):
        if out.endswith(tail):
            out = out[: -len(tail)].rstrip()
            break
    if len(out) <= MAX_LABEL_CHARS:
        return out
    return out[: MAX_LABEL_CHARS - 1].rstrip() + "\u2026"
