"""The tracking centre in the dialogs: a map marker, stored as two numbers.

Backlog 192, option A (Lee, 2026-10-18): the setup and options dialogs show the
centre as ONE map marker (Home Assistant's location selector, no radius
circle) and keep the radius as a number in kilometres.

The entry still stores CONF_LATITUDE and CONF_LONGITUDE as separate keys, so
existing entries, the coordinator, the title and the unique_id read exactly
what they read before. This module converts between the two shapes and does
nothing else. It imports nothing from Home Assistant, so the tests load it.

! THE SELECTOR DOES NOT RANGE-CHECK. Measured on HA 2026.10.2: its data schema
coerces both values to float and requires both keys, and a latitude of 141.9
passed. The range check is here.

! A ``radius`` key inside the location is IGNORED. The selector is configured
without one, but its data schema still accepts it, and the radius is
CONF_RADIUS_KM, a field of its own with its own limits.
"""

from __future__ import annotations

from typing import Any

from .const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE

# The error key shown under the map when the point is not on the globe.
ERROR_INVALID_LOCATION = "invalid_location"


def to_form(cfg: dict[str, Any], home_latitude: float,
            home_longitude: float) -> dict[str, float]:
    """The marker's starting point: the stored centre, else HA's home.

    ``cfg`` is the merged ``{**entry.data, **entry.options}``, or ``{}`` at
    setup. Submitting the dialog without moving the marker stores the same
    two numbers back.
    """
    return {
        "latitude": float(cfg.get(CONF_LATITUDE, home_latitude)),
        "longitude": float(cfg.get(CONF_LONGITUDE, home_longitude)),
    }


def from_form(user_input: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    """The submitted dialog as the entry stores it, or an error key.

    Returns ``(values, None)`` with CONF_LOCATION replaced by CONF_LATITUDE and
    CONF_LONGITUDE and every other field passed through unchanged, or
    ``(None, ERROR_INVALID_LOCATION)``.
    """
    loc = user_input.get(CONF_LOCATION)
    if not isinstance(loc, dict):
        return None, ERROR_INVALID_LOCATION
    try:
        lat = float(loc["latitude"])
        lon = float(loc["longitude"])
    except (KeyError, TypeError, ValueError):
        return None, ERROR_INVALID_LOCATION
    if lat != lat or lon != lon:  # NaN
        return None, ERROR_INVALID_LOCATION
    if not -90.0 <= lat <= 90.0:
        return None, ERROR_INVALID_LOCATION
    # A map can be panned round the world more than once, and a marker
    # dropped on a second copy reads, say, 190 for -170. Fold it back.
    # Inferred from how web maps wrap, not measured on this dialog.
    if not -180.0 <= lon <= 180.0:
        if abs(lon) > 1e6:
            return None, ERROR_INVALID_LOCATION
        lon = ((lon + 180.0) % 360.0) - 180.0
    values = {k: v for k, v in user_input.items() if k != CONF_LOCATION}
    values[CONF_LATITUDE] = lat
    values[CONF_LONGITUDE] = lon
    return values, None
