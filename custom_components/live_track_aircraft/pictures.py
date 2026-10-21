"""Picture overrides: the user's own image for one aircraft, by Mode S hex.

Lee, 2026-10-21: a picture of his choosing for one airframe. A file named for
the aircraft's hex in the config folder ``live_track_aircraft_pictures`` -
``af83f3.png`` - replaces that aircraft's icon on the map. Any hex, any
aircraft; the integration ships no pictures of its own here.

* Kinds: png, jpg / jpeg, webp, gif, svg. Up to MAX_BYTES each.
* The folder is listed once a minute, off the event loop (coordinator.py), so
  adding, replacing or removing a file shows within a minute and a poll never
  touches the disk.
* The picture is drawn UPRIGHT: a photograph or a drawing is not nose-up art,
  so the rotation fields are dropped for that aircraft.
* ! The view serves these WITHOUT authentication, as it does the icons: an
  <img> or a CSS background cannot send a token. Anything put in the folder
  can be fetched by anyone who can reach this Home Assistant by URL.
* ! A user's SVG could carry script. As a CSS background it never runs; the
  view also sends a Content-Security-Policy that blocks script if the URL is
  opened directly.

Nothing here imports Home Assistant, so it tests without it.
"""

from __future__ import annotations

import os
import re
import time
from typing import Any

DIR_NAME = "live_track_aircraft_pictures"
URL_BASE = "/api/live_track_aircraft/picture"
TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "gif": "image/gif",
    "svg": "image/svg+xml",
}
MAX_BYTES = 2_000_000
RESCAN_S = 60.0
_HEX = re.compile(r"^[0-9a-f]{6}$")
# Dropped for an aircraft drawn with its own picture: it is not nose-up art.
_ROTATION_KEYS = ("icon_rotation_deg", "icon_rotation_basis")


def _split(name: str) -> tuple[str, str] | None:
    """(hex, ext) for a valid file name, lower case; None otherwise."""
    stem, dot, ext = name.rpartition(".")
    stem, ext = stem.lower(), ext.lower()
    if not dot or not _HEX.match(stem) or ext not in TYPES:
        return None
    return stem, ext


def _listing(folder: str) -> list[str]:
    try:
        return sorted(os.listdir(folder))
    except (OSError, TypeError, ValueError):
        return []


class Overrides:
    """The pictures in the folder, by hex. scan() blocks; call it off the loop."""

    def __init__(self, folder: str) -> None:
        self.folder = folder
        self._found: dict[str, tuple[str, str, int]] = {}
        self._scanned_at: float | None = None

    def due(self, now: float) -> bool:
        return self._scanned_at is None or now - self._scanned_at >= RESCAN_S

    def scan(self, now: float | None = None) -> int:
        found: dict[str, tuple[str, str, int]] = {}
        for name in _listing(self.folder):
            key = _split(name)
            if key is None or key[0] in found:
                continue          # one picture per hex: the first by name
            path = os.path.join(self.folder, name)
            try:
                st = os.stat(path)
            except OSError:
                continue
            if not os.path.isfile(path) or not 0 < st.st_size <= MAX_BYTES:
                continue
            found[key[0]] = (name, key[1], int(st.st_mtime))
        self._found = found
        self._scanned_at = time.time() if now is None else now
        return len(found)

    @property
    def count(self) -> int:
        return len(self._found)

    def url(self, hex_id: str | None) -> str | None:
        """The picture URL for this aircraft, or None. ?v= changes with the file."""
        hit = self._found.get((hex_id or "").lower())
        if hit is None:
            return None
        return "%s/%s.%s?v=%d" % (URL_BASE, (hex_id or "").lower(), hit[1], hit[2])


def apply(out: dict[str, Any], url: str | None) -> dict[str, Any]:
    """Put the user's picture on a described aircraft, upright."""
    if not url:
        return out
    out["entity_picture"] = url
    out["picture_source"] = "override"
    out["icon_rotatable"] = False
    for key in _ROTATION_KEYS:
        out.pop(key, None)
    return out


def resolve(folder: str, name: str) -> tuple[str, str] | None:
    """(path, content type) for a requested ``<hex>.<ext>``, or None.

    ! The request is untrusted. Only a name that passes _split is looked for,
    and only among the folder's own entries, so nothing outside the folder
    can be reached.
    """
    want = _split(name)
    if want is None:
        return None
    for entry in _listing(folder):
        if _split(entry) == want:
            path = os.path.join(folder, entry)
            try:
                size = os.path.getsize(path)
            except OSError:
                return None
            if os.path.isfile(path) and 0 < size <= MAX_BYTES:
                return path, TYPES[want[1]]
            return None
    return None
