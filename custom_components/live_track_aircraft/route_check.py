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

import math

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


def choose_leg(legs, resolve, lat, lon, altitude_ft=None, course_deg=None, profile=SCHEDULE):
    """Pick the leg this aircraft can be flying.

    legs     : [(dep, arr, n), ...] - every leg on file for the callsign
    resolve  : code -> {'lat', 'lon', 'tz', ...} or None
    profile  : how much the route SOURCE is trusted - FILED for FiledRoutesDB,
               SCHEDULE (the strict original rules) for adsbdb-like sources
    Returns (leg dict or None, verdict, number of legs considered). The leg
    dict carries the endpoint coordinates and zones when known, and
    'route_check_rule' - the test that decided the verdict.
    """
    if not legs:
        return None, None, 0
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
        scored.append((_RANK[verdict], behind, -(n or 0), verdict, leg))
    scored.sort(key=lambda s: s[:3])
    best = scored[0]
    return best[4], best[3], len(legs)
