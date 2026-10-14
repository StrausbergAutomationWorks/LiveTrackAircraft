"""Reject geometrically impossible routes.

adsbdb maps a callsign to a route from a schedule snapshot that is not kept
current. Airlines reassign flight numbers between schedule seasons, so the
stored answer is often a route that number genuinely served at some point -
just not now. Measured near ORD on 2026-08-25: 16 of 34 answers, 47%, were for
city pairs whose great circle passes hundreds of km away.

Examples from that sample:
    SWA4822  HOU-LAS  1373 km off track, at 700 ft over Chicago
    GTI532   ANC-LAX  2442 km off track
    SWA1563  BNA-LGA   688 km off track, heading error only 3 degrees

SWA1563 was traced to the end. adsbdb says BNA-LGA. OpenSky, which derives
departure airports from observed tracks rather than a schedule, saw the
aircraft leave KDEN. Airportia and Plane Finder both show WN1563 operating
DEN-MDW six days a week, and Plane Finder has the specific airframe N8510E
flying it that evening. So the flight number does identify its route reliably
- adsbdb's copy is simply out of date. These are stale-data errors rather than
inherent ambiguity, and they persist until the upstream snapshot refreshes.

No free current source exists. adsb.lol's feed carries no route fields and its
/api/0/routeset endpoint returns 201 with an empty body for every payload
shape tried. hexdb.io is a thinner version of the same historical mapping.
Airportia, Plane Finder and AirNav Radar are all correct but are display sites
over licensed commercial feeds. OpenSky is free and correct for ORIGIN, but
rate-limits after a handful of anonymous requests.

So the fix is to check the answer against the aircraft's own position and
discard it when it cannot be true. Showing nothing beats showing MEM-DCA for
an aircraft on approach to O'Hare.

WORLDWIDE BEHAVIOUR

The maths is spherical throughout, with no flat-earth approximation and no
hemisphere or meridian assumption. Verified against great-circle waypoints
computed by spherical interpolation:

  * antimeridian - ANC-NRT waypoints at 179W, 165E and 153E all give a
    cross-track of 0; longitude wraparound is handled by the trig itself
  * polar        - LHR-HND crosses 69N and validates correctly
  * southern     - JNB-CPT, GRU-JNB, AKL-SCL (to 52S) and SYD-LAX (crossing
    the equator at 163W) all validate
  * dense Europe - AMS-BRU is a 158 km leg; an aircraft over Frankfurt is
    still rejected because rules 2 and 3 fire even where rule 1's floor is
    generous relative to the leg

TWO KNOWN WEAKNESSES, both worse outside the US:

  1. Short legs are only weakly validated. On a 158 km route the 150 km floor
     is nearly the whole leg, so rule 1 contributes little and rules 2 and 3
     carry the check. A wrong route that happens to be nearby will pass.

  2. The 150 km radius in rule 0 is scaled to US airport spacing. In Europe,
     150 km of one airport frequently means several airports, so a wrong route
     that shares an endpoint region is accepted. This is the UAL1424 failure
     mode - near the claimed origin is not evidence of having departed it -
     and it will be more common where airports are dense.

Both would be addressed by a position source rather than a schedule lookup:
OpenSky's flights/aircraft endpoint gives the observed departure airport,
cacheable per aircraft since origin does not change mid-flight. Left out here
because it needs user-supplied credentials.
"""

import datetime as dt
import functools
import math
from zoneinfo import ZoneInfo

# Cross-track allowance. Aircraft do deviate for weather and airways, and long
# international legs wander more, so the limit scales with leg length - but
# never below 150 km. Calibrated against the sample above: the widest correct
# answer was 189 km on a ~4,000 km leg (YYZ-SAL); the tightest wrong one was
# 216 km on a ~600 km leg (RFD-SDF).
MIN_CROSS_TRACK_KM = 150.0
CROSS_TRACK_FRACTION = 0.06

# Below this the aircraft is manoeuvring near an airport, so one of its
# endpoints must be close by.
TERMINAL_ALT_FT = 10000
TERMINAL_RANGE_KM = 150.0

_EARTH_KM = 6371.0


def _hav_km(lat1, lon1, lat2, lon2):
    p1, l1, p2, l2 = map(math.radians, (lat1, lon1, lat2, lon2))
    dp, dl = p2 - p1, l2 - l1
    return 2 * _EARTH_KM * math.asin(math.sqrt(
        math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2))


def _bearing(lat1, lon1, lat2, lon2):
    p1, l1, p2, l2 = map(math.radians, (lat1, lon1, lat2, lon2))
    dl = l2 - l1
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def _cross_track_km(o_lat, o_lon, d_lat, d_lon, lat, lon):
    """Perpendicular distance from the aircraft to the great circle."""
    d13 = _hav_km(o_lat, o_lon, lat, lon) / _EARTH_KM
    t13 = math.radians(_bearing(o_lat, o_lon, lat, lon))
    t12 = math.radians(_bearing(o_lat, o_lon, d_lat, d_lon))
    return abs(math.asin(math.sin(d13) * math.sin(t13 - t12)) * _EARTH_KM)


# --------------------------------------------------------------------------
# TRUST PROFILES - added 2026-09-22, Lee's decision.
#
# The rules below were written against adsbdb: a schedule snapshot that is
# often STALE (47% wrong near ORD, 2026-08-25). That is the "schedule" profile
# and it is unchanged - same rules, same order, same thresholds.
#
# FiledRoutesDB routes are FILED FLIGHT PLANS, current to the week, so they
# carry more weight ("filed" profile). A filed route is rejected only on
# evidence that holds anywhere in the world:
#   * past an end of the leg                    - relative to the leg's length
#   * far off the great circle                  - 25% of the leg, not 6%
#   * flying AWAY from its destination          - course vs bearing, > 120 deg
# and NOT for being low far from both ends: that rule assumes airline traffic;
# a general-aviation or air-taxi plan at 6,000 ft between two fields is normal.
#
# Forced by measurement, 2026-09-22 21:34-22:00, 177 legs: 7 rejected, ALL for
# cross-track, all long legs, six of them airline flights almost certainly on
# the route - AAL458 KMIA-KMSP 215 km off a 150 km allowance at FL380 heading
# for MSP; BAW21ML KDEN-EGLL 811/450; TAP23SL KSFO-LPPT 1094/547; DAL685,
# DAL392, UAL1792. Eastbound and westbound traffic follows jet streams and
# flow routes well off the great circle.
#
# ! WORLDWIDE. Every threshold that can REJECT is relative - a fraction of
# the leg, or an angle. The two absolute distances (TERMINAL_RANGE_KM and the
# cross-track floor) only ever ACCEPT more. So dense Europe, the Pacific and
# the southern hemisphere are judged by the same geometry as the US.
# --------------------------------------------------------------------------

SCHEDULE, FILED = "schedule", "filed"
PROFILES = {
    SCHEDULE: {"xt_fraction": CROSS_TRACK_FRACTION, "xt_floor_km": MIN_CROSS_TRACK_KM,
               "low_far": True, "direction": False},
    FILED:    {"xt_fraction": 0.25, "xt_floor_km": MIN_CROSS_TRACK_KM,
               "low_far": False, "direction": True},
}
PAST_END_FACTOR = 1.25
AWAY_DEG = 120.0


def evaluate(route, lat, lon, altitude_ft=None, course_deg=None, profile=SCHEDULE):
    """(plausible, rule, numbers) for a route at an aircraft's position.

    rule names the test that DECIDED: no_position | no_coordinates |
    same_airport | near_an_end | off_great_circle | past_end | flying_away |
    low_far_from_ends | on_route. Accepts when there is nothing to test -
    the point is to reject demonstrable nonsense.
    """
    p = PROFILES[profile]
    if not route or lat is None or lon is None:
        return True, "no_position", {}
    o_lat, o_lon = route.get("origin_lat"), route.get("origin_lon")
    d_lat, d_lon = route.get("destination_lat"), route.get("destination_lon")
    if None in (o_lat, o_lon, d_lat, d_lon):
        return True, "no_coordinates", {}

    leg_km = _hav_km(o_lat, o_lon, d_lat, d_lon)
    info = {"leg_km": round(leg_km)}
    if leg_km < 1.0:                      # origin == destination; nothing to test
        return True, "same_airport", info
    to_origin = _hav_km(lat, lon, o_lat, o_lon)
    to_dest = _hav_km(lat, lon, d_lat, d_lon)
    info.update(to_origin_km=round(to_origin), to_dest_km=round(to_dest))

    # 0. Close to either endpoint, accept without further question. Arrivals
    #    get vectored and held, departures turn out before turning on course,
    #    so nothing below means anything within about 150 km of an airport.
    if min(to_origin, to_dest) <= TERMINAL_RANGE_KM:
        return True, "near_an_end", info

    # 1. Anywhere near the great circle between the two?
    xt = _cross_track_km(o_lat, o_lon, d_lat, d_lon, lat, lon)
    limit = max(p["xt_floor_km"], leg_km * p["xt_fraction"])
    info.update(xt_km=round(xt), limit_km=round(limit))
    if xt > limit:
        return False, "off_great_circle", info

    # 2. Past either end? The great circle's extension runs round the planet.
    if to_origin > leg_km * PAST_END_FACTOR or to_dest > leg_km * PAST_END_FACTOR:
        return False, "past_end", info

    # 3. (filed) Flying away from the destination. Outside both terminal
    #    areas an aircraft on this leg is heading for its destination; a
    #    reroute bends the course, it does not reverse it. Also what rejects
    #    a filed A-B when the aircraft is flying the unfiled B-A.
    if p["direction"] and course_deg is not None:
        off = _angle_diff(course_deg, _bearing(lat, lon, d_lat, d_lon))
        info["course_off_deg"] = round(off)
        if off > AWAY_DEG:
            return False, "flying_away", info

    # 4. (schedule) Low means near an airport, but rule 0 found no endpoint
    #    close - so a low aircraft here is nowhere near either end. Catches a
    #    700 ft aircraft over Chicago claiming HOU-LAS. Not applied to filed
    #    routes: low cross-country general aviation is ordinary.
    if p["low_far"] and altitude_ft is not None and altitude_ft < TERMINAL_ALT_FT:
        return False, "low_far_from_ends", info

    return True, "on_route", info


def route_is_plausible(route, lat, lon, altitude_ft=None, course_deg=None, profile=SCHEDULE):
    """Whether a looked-up route can be true for an aircraft at (lat, lon).
    Default profile is the original adsbdb behaviour, unchanged."""
    return evaluate(route, lat, lon, altitude_ft, course_deg, profile)[0]


def describe_rejection(route, lat, lon, altitude_ft=None):
    """Why a route was rejected. For debug logging only."""
    o_lat, o_lon = route.get("origin_lat"), route.get("origin_lon")
    d_lat, d_lon = route.get("destination_lat"), route.get("destination_lon")
    if None in (o_lat, o_lon, d_lat, d_lon):
        return "no coordinates"
    leg = _hav_km(o_lat, o_lon, d_lat, d_lon)
    xt = _cross_track_km(o_lat, o_lon, d_lat, d_lon, lat, lon)
    return (f"{route.get('origin_iata')}-{route.get('destination_iata')} "
            f"leg={leg:.0f}km cross_track={xt:.0f}km "
            f"limit={max(MIN_CROSS_TRACK_KM, leg * CROSS_TRACK_FRACTION):.0f}km "
            f"alt={altitude_ft}")


# --------------------------------------------------------------------------
# Choosing among a callsign's legs. Added 2026-09-22, when airport coordinates
# became available (airports.py). Until then this module was INERT.
#
# ! 48.7% of callsigns fly more than one route, and most of those are ONE city
# pair flown both ways. The artifact carries every leg with its observation
# count; the old lookup returned only the most-observed one, unchecked. Here
# every leg is tested against the aircraft's own position:
#
#   1. geometrically plausible legs beat unchecked ones, which beat implausible
#   2. among those, a leg whose DESTINATION lies ahead on the aircraft's course
#      beats one whose destination is behind it - this is what separates A-B
#      from B-A, which geometry alone cannot (both lie on the same great circle)
#   3. then observation count, as before
#
# Unchecked means an endpoint has no coordinates; it is not evidence either way.
# --------------------------------------------------------------------------

PLAUSIBLE, UNCHECKED, IMPLAUSIBLE = "plausible", "unchecked", "implausible"
_RANK = {PLAUSIBLE: 0, UNCHECKED: 1, IMPLAUSIBLE: 2}
AHEAD_DEG = 90.0


def _angle_diff(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


# --------------------------------------------------------------------------
# WHICH LEG, BY TIME AND BY FLIGHT PHASE - added 2026-09-23, Lee's decision.
#
# Measured the night before (Live Track Aircraft SSOT, "THE VERDICT CAPTURE,
# READ AGAINST WHAT WAS ACTUALLY FLYING"): the route shown was a leg OTHER than
# the one in the air for 60 of 296 checkable verdicts, and for 43 of them the
# right leg WAS on file - near Chicago several legs rank plausible, "destination
# ahead" often ties, and the tiebreak fell to how often each leg had been seen.
# Loosening or tightening thresholds cannot fix that; choosing the leg can.
#
# Two new keys, both between the geometry verdict and "ahead":
#
#   PHASE - a LOW aircraft (below TERMINAL_ALT_FT) is near one of the ends of
#     the leg it is flying. Climbing -> that end is the ORIGIN; descending ->
#     the DESTINATION; level or no rate -> either end. Tested against the
#     LEG'S OWN ENDS within TERMINAL_RANGE_KM, never "the nearest airport": an
#     aircraft climbing out of O'Hare can be closer to Midway, and a leg from
#     either of them passes. Very low (< VERY_LOW_FT) with neither end near is
#     counted against the leg; between the two altitudes with no rate, nothing.
#     ! A RANK, NOT A REJECTION: it only orders legs against each other. A GA
#     flight cruising low between two distant fields has every leg ranked the
#     same, so nothing changes for it.
#
#   TIME - a leg whose departure-to-arrival window contains "now" beats a leg
#     with no times. ! SINCE 2026-10-13 the windows are the PUBLISHED ones,
#     used without padding, and a leg OUTSIDE its window ranks the same as one
#     with no times - see THE PUBLISHED WINDOWS below; the 2026-09-23 slack
#     and the OUT_OF_WINDOW penalty are gone. With one end's window only, the
#     other is estimated from distance; with no times at all this key ties
#     and the ranking is the one used before. Among legs in their
#     window, the one whose expected PROGRESS (fraction of the time window
#     elapsed) best matches the aircraft's actual progress along the leg wins.
#
# Observation count is now the LAST tiebreak, not the one that decides.
# Times are clock minutes after local midnight in each end's own zone, so a
# daylight-saving change moves them with the schedule (see routes.leg_times).
# --------------------------------------------------------------------------

VERY_LOW_FT = 5000.0
CLIMB_MS = 2.5                  # ~500 ft/min; below this "level" (turbulence, GA)

# --------------------------------------------------------------------------
# THE PUBLISHED WINDOWS - since 2026-10-13 (Lee: the box uses the public file).
#
# FiledRoutesDB publishes, per COMMERCIAL or CARGO leg, a departure window on
# the ORIGIN's clock and an arrival window on the DESTINATION's:
# [start, length, source, flights]. start ALREADY includes the lead - the
# earliest scheduled time less 30 min (departure) or 40 min (arrival) - and
# the end is the time by which 90% of the flights are scheduled. So:
#
#   ! NO PADDING HERE. The 2026-09-23 slack (30 min early + spread, 90 min
#     late + spread) was for the stand-in's single typical time. The windows
#     are used as published.
#   ! LATE OR OUTSIDE IS NOT EVIDENCE AGAINST A LEG. Lee: "We shouldn't miss a
#     flight because it left on-time." A flight later than its window falls
#     back to the position rule: OUTSIDE_WINDOW ranks exactly like NO_TIMES.
#     (Until 2026-10-13, OUT_OF_WINDOW ranked BELOW no times.)
#   ! WEEKEND by the ORIGIN's local day of the departure: dw / aw where
#     published, else d / a (which are then all days).
#
# The aircraft can be in the air on the leg from the start of the departure
# window to the end of the arrival window: that is the test. Measured by the
# route service (hold-out, 2026-10-13): 90.5% of on-time-or-early departures
# and 89.3% of arrivals fall inside their windows; late departures 31%, by
# design.
#
# Zones come from each airport's COORDINATES (airports.py, saw_livetrack.zones
# .zone_at) - the call the builder makes, so the two cannot disagree.
# --------------------------------------------------------------------------
DEP_LEAD_MIN, ARR_LEAD_MIN = 30, 40     # the builder's leads (the file's keys.t)
EST_FIXED_MIN, EST_KMH = 15.0, 780.0    # one end missing: block = this
MIN_BLOCK = dt.timedelta(minutes=5)
MAX_BLOCK = dt.timedelta(hours=20)
IN_WINDOW, NO_TIMES, OUTSIDE_WINDOW = "in_window", "no_times", "outside_window"
_TIME_RANK = {IN_WINDOW: 0, NO_TIMES: 1, OUTSIDE_WINDOW: 1}
# The sort order. Named so an offline replay can test alternatives with the
# same code; the integration never changes it.
ORDER = ("verdict", "phase", "time", "behind", "progress", "history")


@functools.lru_cache(maxsize=512)
def _zone(name):
    if not name:
        return None
    try:
        return ZoneInfo(name)
    except Exception:           # unknown key, missing tzdata
        return None


def _local(day, minute, zone):
    return dt.datetime(day.year, day.month, day.day, minute // 60, minute % 60, tzinfo=zone)


def _win(times, key, weekend):
    """(start, length) of the d or a window for this day, or None.
    Weekend: the weekend window where one is published, else the plain one."""
    w = (times.get(key + "w") if weekend else None) or times.get(key)
    if not w or len(w) < 2:
        return None
    try:
        start, length = int(w[0]), int(w[1])
    except (TypeError, ValueError):
        return None
    if not (0 <= start <= 1439 and 1 <= length <= 1440):
        return None
    return start, length


def _block(leg):
    """Estimated block time from distance, for a leg with one end's window."""
    if None in (leg.get("origin_lat"), leg.get("origin_lon"),
                leg.get("destination_lat"), leg.get("destination_lon")):
        return None
    km = _hav_km(leg["origin_lat"], leg["origin_lon"], leg["destination_lat"], leg["destination_lon"])
    return dt.timedelta(minutes=EST_FIXED_MIN + km / EST_KMH * 60.0)


def _flights(times, leg, now_dt):
    """The leg's possible flights near now: (lo, hi, dep_ref, arr_ref).

    lo = start of the departure window, hi = end of the arrival window,
    dep_ref / arr_ref = the earliest scheduled times (window start + lead),
    used only for expected progress. One flight per ORIGIN day, yesterday and
    today; a flight leaving tomorrow cannot be in the air now.
    """
    oz, dz = _zone(leg.get("origin_tz")), _zone(leg.get("destination_tz"))
    if oz is None:
        return
    base = now_dt.astimezone(oz).date()
    for off in (-1, 0):
        day = base + dt.timedelta(days=off)
        weekend = day.weekday() >= 5
        dwin, awin = _win(times, "d", weekend), _win(times, "a", weekend)
        if dwin is None and awin is None:
            continue
        d_lo = d_ref = d_hi = None
        if dwin is not None:
            d_lo = _local(day, dwin[0], oz)
            d_ref = d_lo + dt.timedelta(minutes=min(DEP_LEAD_MIN, dwin[1]))
            d_hi = d_lo + dt.timedelta(minutes=dwin[1])
        block = None
        if awin is not None and dz is not None:
            a_lo = a_ref = None
            if d_ref is None:
                block = _block(leg)
                if block is None:
                    continue
            # Arrival instances around this departure day on the destination's
            # clock; the first one a plausible block time after departure.
            anchor = (d_ref or _local(day, 720, oz)).astimezone(dz).date()
            for k in (-2, -1, 0, 1, 2):
                lo = _local(anchor + dt.timedelta(days=k), awin[0], dz)
                ref = lo + dt.timedelta(minutes=min(ARR_LEAD_MIN, awin[1]))
                if d_ref is not None:
                    ok = MIN_BLOCK < ref - d_ref <= MAX_BLOCK
                else:
                    ok = (ref - block).astimezone(oz).date() == day
                if ok and (a_ref is None or ref < a_ref):
                    a_lo, a_ref = lo, ref
            if a_ref is None:
                continue
            a_hi = a_lo + dt.timedelta(minutes=awin[1])
            if d_ref is None:                       # arrival only: departure estimated
                d_ref = a_ref - block
                d_lo = d_ref - dt.timedelta(minutes=DEP_LEAD_MIN)
        else:
            if d_ref is None:
                continue
            block = _block(leg)
            if block is None:
                continue
            a_ref, a_hi = d_ref + block, d_hi + block   # departure only: arrival estimated
        yield d_lo, a_hi, d_ref, a_ref


def leg_time(times, leg, now):
    """(IN_WINDOW | NO_TIMES | OUTSIDE_WINDOW, expected progress 0..1 or None).

    times : {'d': [start, len, src, n], 'a': [...], 'dw': ..., 'aw': ...} or None
            - the published windows, routes.RouteStore.leg_times
    leg   : the leg dict, with origin/destination tz and coordinates
    now   : epoch seconds
    In the window = between the start of a departure window and the end of
    the arrival window that follows it. Outside is NOT evidence against the
    leg (see THE PUBLISHED WINDOWS above).
    """
    if not times or now is None:
        return NO_TIMES, None
    now_dt = dt.datetime.fromtimestamp(now, dt.UTC)
    seen = False
    for lo, hi, d_ref, a_ref in _flights(times, leg, now_dt):
        seen = True
        if lo <= now_dt <= hi:
            span = (a_ref - d_ref).total_seconds()
            prog = min(1.0, max(0.0, (now_dt - d_ref).total_seconds() / span)) if span > 0 else None
            return IN_WINDOW, prog
    return (OUTSIDE_WINDOW if seen else NO_TIMES), None


def leg_phase(leg, lat, lon, altitude_ft, vertical_rate_ms):
    """0 consistent, 1 no evidence, 2 inconsistent - see PHASE above."""
    if altitude_ft is None or altitude_ft >= TERMINAL_ALT_FT or lat is None or lon is None:
        return 1
    if None in (leg.get("origin_lat"), leg.get("destination_lat")):
        return 1
    near_o = _hav_km(lat, lon, leg["origin_lat"], leg["origin_lon"]) <= TERMINAL_RANGE_KM
    near_d = _hav_km(lat, lon, leg["destination_lat"], leg["destination_lon"]) <= TERMINAL_RANGE_KM
    if vertical_rate_ms is not None and vertical_rate_ms > CLIMB_MS:
        return 0 if near_o else 2
    if vertical_rate_ms is not None and vertical_rate_ms < -CLIMB_MS:
        return 0 if near_d else 2
    if near_o or near_d:
        return 0
    return 2 if altitude_ft < VERY_LOW_FT else 1


def choose_leg(legs, resolve, lat, lon, altitude_ft=None, course_deg=None, profile=SCHEDULE,
               vertical_rate_ms=None, now=None, times=None):
    """Pick the leg this aircraft can be flying.

    legs     : [(dep, arr, n), ...] - every leg on file for the callsign
    resolve  : code -> {'lat', 'lon', 'tz', ...} or None
    profile  : how much the route SOURCE is trusted - FILED for FiledRoutesDB,
               SCHEDULE (the strict original rules) for adsbdb-like sources
    vertical_rate_ms, now (epoch s), times ({(dep, arr): {...}}) - all
               optional; absent, the ranking is the one used before 2026-09-23
               apart from the phase key, which then needs only altitude.
    Returns (leg dict or None, verdict, number of legs considered). The leg
    dict carries the endpoint coordinates and zones when known,
    'route_check_rule' - the test that decided the verdict - and
    'route_time_check' - in_window | no_times | outside_window.
    """
    if not legs:
        return None, None, 0
    times = times or {}
    scored = []
    for dep, arr, n in legs:
        o, d = resolve(dep), resolve(arr)
        leg = {"origin_icao": dep, "destination_icao": arr, "route_observations": n}
        if o:
            leg.update(origin_lat=o["lat"], origin_lon=o["lon"], origin_tz=o["tz"])
        if d:
            leg.update(destination_lat=d["lat"], destination_lon=d["lon"], destination_tz=d["tz"])
        if o is None or d is None or lat is None or lon is None:
            verdict, rule = UNCHECKED, ("no_position" if lat is None or lon is None else "no_coordinates")
        else:
            ok, rule, _ = evaluate(leg, lat, lon, altitude_ft, course_deg, profile)
            verdict = PLAUSIBLE if ok else IMPLAUSIBLE
        leg["route_check_rule"] = rule
        behind = 1                                    # unknown direction sorts after "ahead"
        if d and course_deg is not None and lat is not None and lon is not None:
            behind = 0 if _angle_diff(course_deg, _bearing(lat, lon, d["lat"], d["lon"])) <= AHEAD_DEG else 2
        tstate, expected = leg_time(times.get((dep, arr)), leg, now)
        leg["route_time_check"] = tstate
        progress = 0.0
        if expected is not None and o and d and lat is not None and lon is not None:
            a, b = _hav_km(lat, lon, o["lat"], o["lon"]), _hav_km(lat, lon, d["lat"], d["lon"])
            if a + b > 0:
                progress = abs(expected - a / (a + b))
        keys = {"verdict": _RANK[verdict],
                "phase": leg_phase(leg, lat, lon, altitude_ft, vertical_rate_ms),
                "time": _TIME_RANK[tstate], "behind": behind,
                "progress": progress, "history": -(n or 0)}
        scored.append((tuple(keys[k] for k in ORDER), verdict, leg))
    scored.sort(key=lambda s: s[0])
    best = scored[0]
    return best[2], best[1], len(legs)
