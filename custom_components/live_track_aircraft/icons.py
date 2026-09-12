"""Aircraft marker icons, rotated to the direction of travel.

Icons by ADS-B Radar for macOS - https://adsb-radar.com
! THE LICENCE REQUIRES A BACKLINK. "Free to use for personal and commercial
projects. The only requirement: please provide a backlink to ADS-B Radar
somewhere in your project, website, or documentation." That backlink lives in
the README and in ATTRIBUTION.md, and must survive any rewrite of either.

! EVERY ICON POINTS NORTH. Verified by rendering all 37 and looking at them,
not by reading the XML - the SVGs carry baked-in transforms that make the
source misleading. So rotation is the bearing applied directly, with no
per-icon offset table.

! ROTATION HAPPENS HERE, NOT IN THE CARD. ha-map-card has no rotation support
- checked, the only "rotat" in its source is a CSS hue-rotate - but it does
honour entity_picture. So the integration serves an already-rotated SVG and
the card simply draws a picture.
"""

from __future__ import annotations

import re

# --- emitter category -> icon -------------------------------------------
# a0-a7 and b1-b4 map onto the ADS-B categories exactly.
#
# ! TWO DELIBERATE EXCEPTIONS, because the file names do not match the
# standard: b0.svg is a QUADCOPTER, but category B0 means "no category
# information" while B6 means UAV and has no file of its own. A drone drawn
# on every aircraft whose category is merely unreported would be actively
# misleading, so B6 takes the drone and B0 takes the generic airliner.
_BY_CATEGORY = {
    "A0": "a0", "A1": "a1", "A2": "a2", "A3": "a3",
    "A4": "a4", "A5": "a5", "A6": "a6", "A7": "a7",
    "B0": "a0",     # no information - NOT the drone
    "B1": "b1",     # glider
    "B2": "b2",     # lighter-than-air: airship or balloon, seen from above
    "B3": "b3",     # parachutist - a canopy from above
    "B4": "b4",     # ultralight, hang-glider, paraglider
    "B6": "b0",     # UAV - the quadcopter
    "C0": "c0", "C1": "c0", "C2": "c0",   # surface, filtered at the source
}

# --- ICAO type designator -> a specific silhouette ------------------------
# Checked before the category, because "a Boeing 737" beats "a large aircraft".
_BY_TYPE = {
    "A318": "a320", "A319": "a320", "A320": "a320", "A321": "a320",
    "A19N": "a320", "A20N": "a320", "A21N": "a320",
    "A306": "a330", "A310": "a330", "A332": "a330", "A333": "a330",
    "A338": "a330", "A339": "a330", "A35K": "a330", "A359": "a330",
    "A342": "a340", "A343": "a340", "A345": "a340", "A346": "a340",
    "A388": "a380",
    "B731": "b737", "B732": "b737", "B733": "b737", "B734": "b737",
    "B735": "b737", "B736": "b737", "B737": "b737", "B738": "b737",
    "B739": "b737", "B37M": "b737", "B38M": "b737", "B39M": "b737",
    "B741": "b747", "B742": "b747", "B743": "b747", "B744": "b747",
    "B748": "b747", "B74S": "b747",
    "B762": "b767", "B763": "b767", "B764": "b767",
    "B752": "b767", "B753": "b767",
    "B772": "b777", "B773": "b777", "B77L": "b777", "B77W": "b777",
    "B778": "b777", "B779": "b777",
    "B788": "b787", "B789": "b787", "B78X": "b787",
    "C130": "c130", "C30J": "c130", "L100": "c130",
    "C172": "cessna", "C152": "cessna", "C162": "cessna", "C177": "cessna",
    "C182": "cessna", "C206": "cessna", "C210": "cessna", "C72R": "cessna",
    "P28A": "cessna", "P28B": "cessna", "PA28": "cessna", "SR20": "cessna",
    "SR22": "cessna", "DA40": "cessna", "BE36": "cessna", "M20P": "cessna",
    "CRJ1": "crjx", "CRJ2": "crjx", "CRJ7": "crjx", "CRJ9": "crjx",
    "CRJX": "crjx",
    "DH8A": "dh8a", "DH8B": "dh8a", "DH8C": "dh8a", "DH8D": "dh8a",
    "AT43": "dh8a", "AT45": "dh8a", "AT72": "dh8a", "AT75": "dh8a",
    "AT76": "dh8a", "SF34": "dh8a", "B190": "dh8a",
    "E190": "e195", "E195": "e195", "E290": "e195", "E295": "e195",
    "E170": "erj", "E175": "erj", "E75L": "erj", "E75S": "erj",
    "E135": "erj", "E145": "erj", "E45X": "erj",
    "F100": "f100", "F70": "f100",
    "FA7X": "fa7x", "FA8X": "fa7x", "FA50": "fa7x", "F2TH": "fa7x",
    "GLF5": "glf5", "GLF4": "glf5", "GLF6": "glf5", "GL5T": "glf5",
    "G280": "glf5", "GALX": "glf5", "CL60": "glf5", "CL35": "glf5",
    "LJ35": "learjet", "LJ45": "learjet", "LJ60": "learjet",
    "LJ75": "learjet", "LJ31": "learjet", "C25A": "learjet",
    "C25B": "learjet", "C25C": "learjet", "C56X": "learjet",
    "C68A": "learjet", "E55P": "learjet", "PC12": "learjet",
    "MD11": "md11", "MD82": "md11", "MD83": "md11", "MD88": "md11",
    "MD90": "md11", "B712": "md11", "DC10": "md11",
}

# --- what must NOT be turned ---------------------------------------------
# ! An icon is unrotatable when turning it says nothing or breaks the
# picture. Decided by LOOKING at the rendered icons.
#
#   b3   a parachute canopy from above - radially symmetric, and a
#        parachutist has no heading
#   f11  a hot-air balloon in SIDE view - the only side-on icon in the set,
#        and rotating it tips the balloon over
#   f15  a three-bladed propeller - rotationally symmetric
#
# ! B2 IS NOT IN THIS SET. Lighter-than-air covers AIRSHIPS, which are
# powered and point where they are going, and b2 is a top-down ellipse that
# rotates correctly. An earlier draft put B2 here and swapped it to the f11
# balloon; both were wrong.
_NOT_ROTATABLE = frozenset(("b3", "f11", "f15", "c0"))

# Rotation is quantised so the browser can cache. 5 degrees is finer than
# the eye reads on a 28px marker and gives 72 cacheable variants per icon.
ROTATION_STEP = 5

_SAFE = re.compile(r"^[a-z0-9]+$")


def pick(emitter_category: str | None, type_code: str | None,
         icon_category: str | None = None) -> str:
    """Which silhouette to draw. Type beats category; never returns None."""
    t = (type_code or "").strip().upper()
    if t in _BY_TYPE:
        return _BY_TYPE[t]
    cat = (emitter_category or "").strip().upper()
    if cat in _BY_CATEGORY:
        return _BY_CATEGORY[cat]
    # No category and an unknown type: fall back to the shape family the
    # type-prefix rule worked out.
    if icon_category == "rotorcraft":
        return "a7"
    if icon_category == "balloon":
        return "b2"
    if icon_category == "uav":
        return "b0"
    return "a0"


def is_rotatable(key: str) -> bool:
    return key not in _NOT_ROTATABLE


def quantise(bearing: float | None) -> int | None:
    if bearing is None:
        return None
    return int(round((bearing % 360) / ROTATION_STEP) * ROTATION_STEP) % 360


def valid_key(key: str) -> bool:
    """Guard for the HTTP view: a path segment must not escape the folder."""
    return bool(_SAFE.match(key or ""))


# --------------------------------------------------------------------------
# Rendering
#
# ! A SQUARE ROTATED 45 DEGREES DOES NOT FIT IN ITS OWN BOX. The corners need
# sqrt(2) more room, so wrapping the artwork in a plain rotate() clips the
# wingtips at every angle that is not a multiple of 90. The group is scaled
# to 1/sqrt(2) about the centre first, which costs a little size and keeps
# every angle whole.
# --------------------------------------------------------------------------

import math
import os

_SVG_OPEN = re.compile(r"<svg\b[^>]*>", re.I)
_VIEWBOX = re.compile(r'viewBox\s*=\s*"([^"]+)"', re.I)

# Fitting a rotated square inside the original box.
_FIT = 1.0 / math.sqrt(2.0)


def _inner(svg: str) -> tuple[str, float, float]:
    """The artwork inside the root <svg>, plus the box it is drawn in."""
    m = _SVG_OPEN.search(svg)
    if not m:
        raise ValueError("no <svg> element")
    body = svg[m.end():]
    end = body.rfind("</svg>")
    if end >= 0:
        body = body[:end]
    vb = _VIEWBOX.search(m.group(0))
    if vb:
        parts = [float(x) for x in vb.group(1).replace(",", " ").split()]
        if len(parts) == 4:
            return body, parts[2], parts[3]
    return body, 512.0, 512.0


def render(path: str, degrees: int | None, size: int = 64) -> str:
    """One icon, rotated. `degrees` of None means do not rotate."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    body, w, h = _inner(src)
    cx, cy = w / 2.0, h / 2.0

    if degrees:
        # Scale about the centre, THEN rotate about the centre, so nothing
        # reaches a corner it cannot fit into.
        transform = (
            'transform="translate(%.4f %.4f) scale(%.6f) translate(%.4f %.4f) '
            'rotate(%d %.4f %.4f)"'
            % (cx - cx * _FIT, cy - cy * _FIT, _FIT, 0.0, 0.0,
               degrees, cx, cy))
    else:
        transform = ""

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %s %s">'
        '<g %s>%s</g></svg>'
        % (size, size, _fmt(w), _fmt(h), transform, body)
    )


def _fmt(v: float) -> str:
    return ("%f" % v).rstrip("0").rstrip(".") if v % 1 else "%d" % int(v)


def icon_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "icons")


def icon_path(key: str) -> str | None:
    if not valid_key(key):
        return None
    p = os.path.join(icon_dir(), key + ".svg")
    return p if os.path.exists(p) else None
