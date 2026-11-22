"""A photo of an aircraft from Planespotters.net, looked up when a viewer hovers it (backlog 361).

! THE LOOKUP IS THE LIBRARY'S since saw-livetrack 0.2.43 (backlog 362, 2026-11-21): saw_livetrack.aircraft_photos, which
began as this file and moved to the library when Live Track SALT became its second consumer (05_SHARED_LESSONS.md
rule 2). The terms' rules (the User-Agent, answers kept 12 h, nothing downloaded or proxied, 429 pausing every lookup,
403 stopping them for a day) and their tests are the library's. One store and one pause per Home Assistant, under the
library's SAW-neutral key, so with Live Track SALT installed too both share them.

What stays here is this integration's own address: the map card asks it (06_MAP_CONTRACT.md D4i,
`marker_photo_lookup`), and web.AircraftPhotoView answers it from the library.
"""

from __future__ import annotations

from typing import Any

from saw_livetrack import aircraft_photos as _lib

URL_BASE = "/api/live_track_aircraft/photo"


def lookup_path(identity: Any, identity_hidden: Any = False) -> str | None:
    """The entity's `marker_photo_lookup`, or None: not for a TIS-B track or anything that is not an ICAO
    address, and not for a Privacy ICAO Address (the feed's `identity_hidden`), whose hex names no airframe."""
    return _lib.lookup_path(URL_BASE, identity, identity_hidden)
