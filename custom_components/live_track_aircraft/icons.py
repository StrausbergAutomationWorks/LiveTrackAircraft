"""Aircraft marker icons: drawn by saw_livetrack.aircraft_icons since backlog 298.

The type table, the artwork, render(), the tones, the lights, the police flash
and ART_REV live in the shared library (saw-livetrack 0.2.11), so Live Track
Enforcement Aircraft draws a listed aircraft exactly as this integration does
(Lee 2026-10-24). They moved verbatim from this file at ac45b2e, and every
picture was rendered before and after and compared byte for byte.
Icons by ADS-B Radar - https://adsb-radar.com - ATTRIBUTION.md, here and in
the library beside the icons, is the backlink their licence asks for.

What stays HERE, because it is this integration's own:
  * HEX_KEYS and the two pictures it names (icons/vc25a.svg, icons/af83f3.svg):
    the presidential airframes are drawn by Live Track Aircraft only.
  * URL_BASE and picture_url(): the view (web.py) is this integration's.
  * LOCAL_ART_REV, for a change to those two pictures.

Every name of the library, the private ones included, is re-exported, so the
coordinator, web.py and the tests keep reading icons.<name>. pick() calls
airframe.is_rotorcraft() in the library, the one answer this component's
airframe.py also gives.
"""

from __future__ import annotations

import os

from saw_livetrack import aircraft_icons as _lib

globals().update({k: v for k, v in vars(_lib).items() if not k.startswith("__")})

# ! ONE AIRFRAME, ITS OWN ICON, BY MODE S HEX - never by callsign.
HEX_KEYS = {
    "adfdf8": "vc25a",     # VC-25A 82-8000
    "adfdf9": "vc25a",     # VC-25A 92-9000
    "af83f3": "af83f3",    # VC-25B 25-3300
}

# Only the keys HEX_KEYS names are looked for in this component's folder, so a
# stale copy of a library icon left on a box can never shadow the library's.
_LOCAL_KEYS = frozenset(HEX_KEYS.values())


def local_icon_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "icons")


def icon_path(key: str) -> str | None:
    """This component's own picture for a HEX_KEYS key, else the library's."""
    if key in _LOCAL_KEYS and valid_key(key):
        p = os.path.join(local_icon_dir(), key + ".svg")
        return p if os.path.exists(p) else None
    return _lib.icon_path(key)


URL_BASE = "/api/live_track_aircraft/icon"

# ! THE a= REVISION IS THE LIBRARY'S PLUS OURS. The library bumps ART_REV with
# any change to its pictures; LOCAL_ART_REV bumps with a change to the two
# pictures kept here. Both only ever go up, so the sum does too, and a cached
# picture is never served under a new look. 0 today: a=10 as before the move.
LOCAL_ART_REV = 0
ART_REV = _lib.ART_REV + LOCAL_ART_REV


def picture_url(key: str, tone: str = "default",
                weight: float | None = None, lights: bool = False) -> str:
    """The entity_picture: one silhouette, UNROTATED, with no disc.

    ! NO ANGLE AND NO BADGE ARGUMENT, on purpose (Lee, 2026-09-25). The card
    turns the marker from icon_rotation_deg; a rotated picture as well would
    double the turn. b=0 keeps the view from drawing its disc.
    ! TONE AND WEIGHT RIDE AS QUERY PARAMETERS, and the query is part of the
    cache key - a government aircraft and an airliner on the same silhouette
    are two different cached images, as they should be.
    """
    return "%s/%s/fixed.svg?%s" % (URL_BASE, key, _lib.picture_query(tone, weight, lights, ART_REV))
