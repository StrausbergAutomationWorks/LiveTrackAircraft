"""Military watch areas, as typed in the options dialog: "lat,lon,km; lat,lon,km". No Home Assistant import, so the tests load it.

Lee 2026-11-02 22:59. Stored as the text the user typed, so the dialog shows it back as written. An empty field is no areas.
"""
from __future__ import annotations

from typing import NamedTuple

ERROR_INVALID_AREAS = "invalid_military_areas"
MAX_AREAS = 10
MIN_AREA_KM = 1.0
MAX_AREA_KM = 2000.0


class Area(NamedTuple):
    latitude: float
    longitude: float
    radius_km: float


def parse_areas(text: str | None) -> tuple[list[Area], str | None]:
    """(areas, None), or ([], the error key). Nothing half-read: one bad circle refuses the whole field."""
    areas: list[Area] = []
    for part in (text or "").split(";"):
        part = part.strip()
        if not part:
            continue
        try:
            lat, lon, km = (float(b) for b in part.split(","))
        except ValueError:    # not a number, or not exactly three
            return [], ERROR_INVALID_AREAS
        # These comparisons are false for NaN, so NaN is refused too.
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0 and MIN_AREA_KM <= km <= MAX_AREA_KM):
            return [], ERROR_INVALID_AREAS
        areas.append(Area(lat, lon, km))
    if len(areas) > MAX_AREAS:
        return [], ERROR_INVALID_AREAS
    return areas, None


def label(area: Area) -> str:
    """The sensor's key for one circle: as short as the numbers allow."""
    return "%g,%g,%g" % area
