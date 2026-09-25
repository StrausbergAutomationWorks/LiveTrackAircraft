"""Constants for Live Track Aircraft.

Identity is PERMANENT. The domain is fixed at first install and no rename
recovers it - 00_START_HERE.md damage item 2.
"""

from __future__ import annotations

DOMAIN = "live_track_aircraft"
# ! THE FEEDS' TERMS REQUIRE THIS (read 2026-09-22). adsb.fi: "You must cite
# adsb.fi and include a link to our home page." adsb.lol: its API and data are
# ODbL 1.0, whose notice is required when the data is used publicly - not for a
# private map, but a user may share theirs, so it rides along. HA shows this
# string on every entity's attribution, so it carries both. README.md and
# ATTRIBUTION.md carry the same, with links.
ATTRIBUTION = (
    "Data from adsb.lol (https://adsb.lol, ODbL 1.0) "
    "and adsb.fi (https://adsb.fi)"
)

# --- configuration keys ---
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_RADIUS_KM = "radius_km"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_MAX_AIRCRAFT = "max_aircraft"

# --- radius -------------------------------------------------------------
# 56 km matches the flights_above entry already running, so the first
# deployment is comparable with what is on the map today.
DEFAULT_RADIUS_KM = 56.0
MIN_RADIUS_KM = 1.0
# The feed's own hard ceiling is 250 nautical miles.
MAX_RADIUS_KM = 463.0

# --- scan interval ------------------------------------------------------
# ! MEASURED 2026-09-09, not chosen. At a 5-second poll, 196 of 360 requests
# returned HTTP 429 - a 45.6% success rate. flights_above runs at 15 s in
# production with no throttling, and upstream's MIN_SCAN_INTERVAL is 15.
DEFAULT_SCAN_INTERVAL = 15
MIN_SCAN_INTERVAL = 15
MAX_SCAN_INTERVAL = 3600

# --- entity cap ---------------------------------------------------------
# ! A GUARD RAIL, NOT A DISPLAY CONTROL. Thinning belongs to the card:
# auto-entities filters on domain and attributes without a restart. An
# integration-side cap set too low loses data that was never published and
# looks like poor coverage rather than a setting.
#
# ! A ceiling is not a count - 05_SHARED_LESSONS.md A2. The live value is on
# the config entry, not here.
#
# Measured 2026-09-10 at 30 nm: 74 aircraft in one poll at 20:00, 21 at
# 22:40. Two samples across a diurnal swing is not a distribution and the
# busy hour is UNMEASURED, so this sits well above anything observed.
DEFAULT_MAX_AIRCRAFT = 250
MIN_MAX_AIRCRAFT = 1
MAX_MAX_AIRCRAFT = 1000

# --- sources ------------------------------------------------------------
# Tried in order; any non-200, or a short 200 (sources/adsb.py), is that
# source failing and the next is tried.
# ! A source that falls through to the next does so SILENTLY, which is why
# the count sensor publishes which source answered.
# ! adsb.fi FIRST since 2026-09-25 (Lee). Measured that evening: adsb.lol
# took about four requests a minute and then refused with 429 and no
# Retry-After, on a ~135 s cycle, and on the edges of it answered 200 with a
# SHORT list (38, then 0, against ~200 overhead) - the map stopped and
# jumped. adsb.fi answered 12 of 12 reads of the same circle in full.
SOURCE_URLS: tuple[tuple[str, str], ...] = (
    # ! v3, NOT v2: adsb.fi's README (updated 2026-05-17) calls v2/lat/lon/dist
    # DEPRECATED and asks new integrations to use v3. Measured 2026-09-22: v3
    # answers in adsb.lol's shape ("ac", `now` in MILLISECONDS) where v2 used
    # "aircraft" and seconds. The parser reads both; see the `now` sniff.
    ("adsb.fi", "https://opendata.adsb.fi/api/v3/lat/{lat}/lon/{lon}/dist/{nm}"),
    ("adsb.lol", "https://api.adsb.lol/v2/point/{lat}/{lon}/{nm}"),
)

REQUEST_TIMEOUT = 20

# ! BACK OFF ON HTTP 429 (backlog item 244). Measured 2026-09-22: adsb.lol
# refused 1 poll in 2 with Flights Above polling the same endpoint from the
# same IP, ~1 in 8 without it. Retrying a refusing source every 15 s spends
# the budget it is asking us to spare. A refused source is skipped for its
# Retry-After when it sends one, else BACKOFF_FIRST_S doubling per
# consecutive refusal up to BACKOFF_MAX_S; one 200 resets it. Retry-After is
# clamped to RETRY_AFTER_MAX_S so a malformed header cannot park a source
# for a day.
BACKOFF_FIRST_S = 60.0
BACKOFF_MAX_S = 600.0
RETRY_AFTER_MAX_S = 900.0
USER_AGENT = "LiveTrackAircraft/0.1 (+https://github.com/StrausbergAutomationWorks/LiveTrackAircraft)"

# A single failed fetch must not blank every marker.
MAX_TRANSIENT_FAILURES = 3

# --- motion -------------------------------------------------------------
# The longest segment we will offer a consumer to interpolate across. Beyond
# this the two fixes are not a segment, they are two sightings with a gap.
# Measured 2026-09-09: p95 update gap 35 s, p99 150 s, max 1,250 s.
MAX_SEGMENT_S = 300

# ! Below this groundspeed, course over ground is noise rather than a
# direction: a hovering helicopter reports a different course every
# cycle. A judgement, not a measurement - 30 km/h is about 16 kt,
# below any approach speed and above hover jitter.
SLOW_GROUND_SPEED_KMH = 30.0

# ! NO ICON OPTIONS since 2026-09-25 (Lee). The icon is always served
# unrotated, the card turns it, and it never carries a disc - see icons.py.
# The two options that chose otherwise are gone from the flow; values a
# user saved before are ignored, and the next save of the form drops them.

# Below this the aircraft is not meaningfully moving and a bearing between
# two fixes is noise. Also the threshold that keeps ground clutter honest.
STATIONARY_KT = 40.0

# --- display ------------------------------------------------------------
# Stacking on the shared map is the CARD's job since 2026-09-25: each entity
# names its map_layer (air, or air_low for a rotorcraft - airframe.py) and
# LiveTrackMapCard owns the offsets. 06_MAP_CONTRACT.md D10.
