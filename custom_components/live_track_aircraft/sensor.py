"""The companion count sensor.

! The integration does not NEED this. Nothing in the map, the entity model or
the retirement path depends on it - it exists so a human can see what is
happening, and so some history survives once geo_location.* is excluded from
the recorder.

! THE STATE IS THE TRUE COUNT, UNCAPPED. A capped count cannot distinguish a
quiet sky from a clipped list. Publishing the true number beside the
published one makes truncation visible instead of invisible.

! THIS entity DOES get a unique_id, as the deliberate exception to the
integration's no-unique_id decision. That decision was forced by arithmetic -
917 bytes times tens of thousands of airframes. A singleton multiplies by
one, and this is the entity a user is most likely to rename or put on a
dashboard, which is exactly what a registry row is for.

! NO TIMESTAMP ATTRIBUTES. The recorder keys attribute blobs by CONTENT, so
an attribute unique on every write can never be shared and mints a new blob
each time. Measured on this instance: 69,418 distinct blobs holding 79.8 MB,
and one rich sensor on the same pattern cost 377 MB/week. `last_updated` on
the state already carries when this was written. The attributes below are
deliberately low-cardinality - radius never changes, source takes two values,
capped takes two, published_count perhaps fifty - so they de-duplicate to a
few hundred blobs shared across thousands of rows.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTRIBUTION, DOMAIN
from .coordinator import AircraftCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AircraftCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AircraftInRange(coordinator, entry)])


class AircraftInRange(SensorEntity):
    """How many aircraft are within the configured radius."""

    _attr_attribution = ATTRIBUTION
    _attr_should_poll = False
    _attr_icon = "mdi:airplane-search"
    _attr_name = "Aircraft in range"
    _attr_native_unit_of_measurement = "aircraft"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: AircraftCoordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_aircraft_in_range"

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success

    @property
    def native_value(self) -> int | None:
        data = self._coordinator.data
        return None if data is None else data["in_range"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self._coordinator.data
        if not data:
            return {}
        return {
            "radius_km": data["radius_km"],
            "published_count": data["published"],
            # True when the cap bit and markers are missing from the map.
            "capped": data["capped"],
            # ! Which source answered. A rate-limited adsb.lol falls through
            # to adsb.fi silently, and without this there is no way to notice
            # you have been running on the backup feed for a week.
            "source": data["source"],
            # Sources skipped after HTTP 429, with the time each resumes.
            # One value per episode, not a countdown (backlog item 244).
            "source_backoff": data.get("source_backoff", {}),
            # Whether the shared route artifact is installed and current.
            # Low cardinality: a handful of distinct strings, so it
            # de-duplicates in the recorder like the rest.
            "route_artifact": self._coordinator.routes.status,
            # Same, for the shared airport table (airports.py).
            "airport_table": self._coordinator.airports.status,
        }

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )
