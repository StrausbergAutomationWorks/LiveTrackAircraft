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
* ! SIGNED, since 0.1.3 (hacs/default#14501 item 1, Frenck 2026-11-19). The
  view keeps Home Assistant's authentication; an <img> or a CSS background
  cannot send a token, so the URL handed to the entity carries Home
  Assistant's own signature (async_sign_path, authSig): good for SIGN_S,
  bound to the path and the ?v=, and refused once it expires, is altered or
  is stripped (measured on Home Assistant 2026.11.2, 2026-11-20). Until
  0.1.2 these were served WITHOUT authentication, to anyone who could reach
  the instance and guess a hex.
* The signed URL is cached per file (hex, kind, mtime) and re-signed only
  when under RESIGN_BEFORE_S of it is left, so the URL changes about once a
  day and the map card's picture cache (keyed by URL) is not churned. The
  signing secret lives for one Home Assistant run; a restart rebuilds every
  entity with a new signature anyway.
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
SIGN_S = 24 * 3600            # how long a signed picture URL is good for
RESIGN_BEFORE_S = 2 * 3600    # re-signed when less than this is left
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

    def __init__(self, folder: str, signer=None) -> None:
        """signer(url, seconds) -> signed url, called on the event loop (Home
        Assistant's async_sign_path is a callback); None hands out the plain
        URL, which the view now refuses without a sign-in."""
        self.folder = folder
        self._signer = signer
        self._found: dict[str, tuple[str, str, int]] = {}
        self._signed: dict[str, tuple[str, float]] = {}
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
        # Signatures for files no longer there (or replaced: a new mtime is a
        # new URL) go with them. Reassigned, not edited in place.
        current = {self._raw(h, v) for h, v in found.items()}
        self._signed = {k: v for k, v in self._signed.items() if k in current}
        self._scanned_at = time.time() if now is None else now
        return len(found)

    @property
    def count(self) -> int:
        return len(self._found)

    @staticmethod
    def _raw(hex_id: str, hit: tuple[str, str, int]) -> str:
        return "%s/%s.%s?v=%d" % (URL_BASE, hex_id, hit[1], hit[2])

    def url(self, hex_id: str | None, now: float | None = None) -> str | None:
        """The picture URL for this aircraft, signed, or None. ?v= changes with the file."""
        key = (hex_id or "").lower()
        hit = self._found.get(key)
        if hit is None:
            return None
        raw = self._raw(key, hit)
        if self._signer is None:
            return raw
        now = time.time() if now is None else now
        held = self._signed.get(raw)
        if held is not None and held[1] - now > RESIGN_BEFORE_S:
            return held[0]
        signed = self._signer(raw, SIGN_S)
        self._signed[raw] = (signed, now + SIGN_S)
        return signed


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
