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


def route_is_plausible(route, lat, lon, altitude_ft=None):
    """Whether a looked-up route can be true for an aircraft at (lat, lon).

    Returns True when the route has no coordinates to check against - the
    point is to reject demonstrable nonsense, not to discard everything that
    cannot be proven.
    """
    if not route or lat is None or lon is None:
        return True

    o_lat = route.get("origin_lat")
    o_lon = route.get("origin_lon")
    d_lat = route.get("destination_lat")
    d_lon = route.get("destination_lon")
    if None in (o_lat, o_lon, d_lat, d_lon):
        return True

    leg_km = _hav_km(o_lat, o_lon, d_lat, d_lon)
    if leg_km < 1.0:                      # origin == destination; nothing to test
        return True

    to_origin = _hav_km(lat, lon, o_lat, o_lon)
    to_dest = _hav_km(lat, lon, d_lat, d_lon)

    # 0. Close to either endpoint, accept without further question. Arrivals
    #    get vectored onto downwind legs and into holds, and departures turn
    #    out before turning on course, so cross-track distance means nothing
    #    within about 150 km of an airport. Checking this FIRST prevents the
    #    geometry below from rejecting perfectly good arrivals.
    if min(to_origin, to_dest) <= TERMINAL_RANGE_KM:
        return True

    # 1. Is the aircraft anywhere near the great circle between the two?
    limit = max(MIN_CROSS_TRACK_KM, leg_km * CROSS_TRACK_FRACTION)
    if _cross_track_km(o_lat, o_lon, d_lat, d_lon, lat, lon) > limit:
        return False

    # 2. Is it past either end? Being on the great circle is not enough - the
    #    extension of the line runs right round the planet.
    if to_origin > leg_km * 1.25 or to_dest > leg_km * 1.25:
        return False

    # 3. Low means near an airport, but rule 0 already established that no
    #    endpoint is close - so a low aircraft here is nowhere near either end
    #    of its claimed route. This is what catches a 700 ft aircraft over
    #    Chicago claiming HOU-LAS.
    if altitude_ft is not None and altitude_ft < TERMINAL_ALT_FT:
        return False

    return True


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
