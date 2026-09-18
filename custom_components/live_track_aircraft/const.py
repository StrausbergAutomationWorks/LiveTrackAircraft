"""Constants for Live Track Aircraft.

Identity is PERMANENT. The domain is fixed at first install and no rename
recovers it - 00_START_HERE.md damage item 2.
"""

from __future__ import annotations

DOMAIN = "live_track_aircraft"
ATTRIBUTION = "Data from adsb.lol and adsb.fi"

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
# Tried in order; any non-200 is that source failing and the next is tried.
# ! A rate-limited adsb.lol falls through to adsb.fi SILENTLY, which is why
# the count sensor publishes which source answered.
SOURCE_URLS: tuple[tuple[str, str], ...] = (
    ("adsb.lol", "https://api.adsb.lol/v2/point/{lat}/{lon}/{nm}"),
    ("adsb.fi", "https://opendata.adsb.fi/api/v2/lat/{lat}/lon/{lon}/dist/{nm}"),
)

REQUEST_TIMEOUT = 20
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

# ! WHO ROTATES THE ICON. Off, the integration serves an
# already-rotated silhouette and the marker is correct on any map
# card - that is the shipped behaviour and it depends on nothing.
# On, the icon is served unrotated and the card is expected to turn
# it from icon_rotation_deg, which is the only way the rotation can
# SLIDE rather than snap: two images cannot be interpolated, one
# CSS transform can.
#
# ! DEFAULT OFF ON PURPOSE. On, every marker points north wherever
# the card cannot rotate.
CONF_CARD_ROTATION = "card_rotation"
DEFAULT_CARD_ROTATION = False

# Below this the aircraft is not meaningfully moving and a bearing between
# two fixes is noise. Also the threshold that keeps ground clutter honest.
STATIONARY_KT = 40.0

# --- display ------------------------------------------------------------
# Stacking on the shared map: ships 20, South Shore trains 25, aircraft
# above both so something overhead is not hidden under something on water.
Z_INDEX_OFFSET = 30
