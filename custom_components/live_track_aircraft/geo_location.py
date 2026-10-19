"""geo_location entities for Live Track Aircraft.

One entity per AIRCRAFT, keyed on the ICAO 24-bit address.

Contract: 10_SEED/05_SHARED_LESSONS.md section D.

  * `state` is @final and IS the distance. Do not add a distance attribute.
  * `state_attributes` is @final and returns only source/latitude/longitude.
    Everything else goes in extra_state_attributes or it is silently dropped.
  * `_attr_source` is mandatory - it is what the shared map filters on.

! NO unique_id, and that is deliberate - a departure from D1 recorded in this
integration's SSOT. A session reading D1 alone will think it is a bug.

D6a-0b says to KEEP the registry row for anything that recurs, and aircraft
recur. But that rule was derived from earthquakes, from vessels at 30-37 a
day and from trains. Measured 2026-09-10: a geo_location registry row is 917
bytes and a 30 nm radius produced 125 DISTINCT AIRFRAMES IN 30 MINUTES. At a
plausible annual union of 20,000-50,000 that is 17.5-43.7 MB of registry JSON
loaded into memory at every start. The rule breaks on arithmetic, not taste.

! Its PURPOSE survives. The entity_id derives from _attr_name, NOT from
unique_id (D6b), so naming from the hex gives the same stable id on every
return - which is the whole of what D6a-0b was protecting. With no row,
nothing reserves the base id either, so the vessel_367152790_4 drift mode
cannot occur here at all.

What is given up: renaming, hiding, area assignment and voice exposure, on
markers that exist for as long as an aircraft is overhead.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .adsbdb import ATTRIBUTION as ADSBDB_ATTRIBUTION
from .const import ATTRIBUTION, DOMAIN
from .coordinator import AircraftCoordinator

# Attributes copied straight through when present. Absent keys are OMITTED.
_PASSTHROUGH = (
    # --- the shared map (06_MAP_CONTRACT.md D10, D11) ---
    # map_layer: air, or air_low for a rotorcraft; the CARD owns the offsets.
    # object_ids: icao24, and registration where the FAA registry states it.
    "map_layer",
    "object_ids",
    "identity",
    "marker_label",
    "callsign",
    # --- description: what the feed cannot tell a watcher on its own ---
    "aircraft_type",
    "aircraft_name",
    "aircraft_manufacturer",
    "registration",
    "operator",
    "operator_code",
    "operator_category",
    "operator_state",
    "operator_name_source",
    "is_government",
    "emitter_category",
    # D4 display helpers: a consumer MAY use these and MUST NOT require them.
    "icon_category",
    "category_label",
    "icon_rotatable",
    "icon_rotation_deg",
    "icon_rotation_basis",
    "squawk",
    # --- kinematics, in contract units (D0) ---
    "altitude_m",
    "speed_kmh",
    "vertical_rate_ms",
    "climb_status",
    "heading_deg",
    "course_deg",
    # --- route, from the shared artifact; absent when it is not installed ---
    "origin_icao",
    "destination_icao",
    # airport names from the airport table (airports.py), as shown
    # (airport_display.py); absent when the table has none
    "origin_name",
    "destination_name",
    "route_observations",
    "route_source",
    # route verification (route_check.choose_leg) and the airport table's zones
    "route_check",
    "route_check_rule",
    "route_time_check",
    "route_candidates",
    "origin_tz",
    "destination_tz",
    # estimated arrival at the leg's destination (eta.py), D0 instant, D4b
    "arrival_estimated_at",
    # --- freshness and motion ---
    "last_seen",
    "observed_at",
    "previous_latitude",
    "previous_longitude",
    "previous_observed_at",
    "segment_duration_s",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create entities as aircraft appear and remove them as they depart."""
    coordinator: AircraftCoordinator = hass.data[DOMAIN][entry.entry_id]
    live: dict[str, Aircraft] = {}

    @callback
    def _sync() -> None:
        current = set((coordinator.data or {}).get("aircraft") or {})

        new = [i for i in current if i not in live]
        if new:
            entities = [Aircraft(coordinator, i) for i in new]
            live.update(zip(new, entities))
            async_add_entities(entities)

        # ! Departed aircraft are REMOVED, unlike vessels and railcars.
        # With no registry row there is nothing to keep, and leaving the
        # entity behind would fill the state machine with thousands of
        # unavailable markers - the very cost this design avoids.
        for gone in [i for i in live if i not in current]:
            entity = live.pop(gone)
            entity.hass.async_create_task(entity.async_remove(force_remove=True))

    _sync()
    entry.async_on_unload(coordinator.async_add_listener(_sync))


class Aircraft(GeolocationEvent):
    """One aircraft on the shared map."""

    _attr_should_poll = False
    _attr_unit_of_measurement = "km"

    # ! adsbdb's route data is David Taylor's and Jim Mason's (adsbdb.py,
    # backlog 292), so an aircraft showing an adsbdb route credits them and
    # adsbdb. Two values only, so the attribute stays low-cardinality.
    @property
    def attribution(self) -> str:
        rec = self._rec()
        if (rec or {}).get("route_source") == "adsbdb":
            return ATTRIBUTION + "; " + ADSBDB_ATTRIBUTION
        return ATTRIBUTION

    # The discriminator the shared map's auto-entities card filters on.
    _attr_source = DOMAIN

    # ! NOT a class constant. It was `_attr_icon = "mdi:airplane"`, which
    # drew every rotorcraft as an aeroplane - measured 2026-09-11, five A7
    # rotorcraft including two City of Chicago Bells, all rendering as
    # aircraft. The feed says what kind it is on effectively every aircraft
    # and the integration was ignoring it.
    @property
    def icon(self) -> str:
        rec = self._rec()
        return (rec or {}).get("icon") or "mdi:airplane"

    # ! The silhouette, already rotated. ha-map-card's get picture() falls
    # back to attributes.entity_picture, so this is what puts a turning
    # aeroplane on the map rather than a dot.
    @property
    def entity_picture(self) -> str | None:
        rec = self._rec()
        return (rec or {}).get("entity_picture")

    def __init__(self, coordinator: AircraftCoordinator, identity: str) -> None:
        self._coordinator = coordinator
        self._identity = identity
        # ! From the hex, never from the callsign. A callsign changes mid
        # flight and is reassigned daily; the entity_id is forever (D6b).
        self._attr_name = f"Aircraft {identity.upper()}"

    def _rec(self) -> dict[str, Any] | None:
        return ((self._coordinator.data or {}).get("aircraft") or {}).get(
            self._identity
        )

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success and self._rec() is not None

    @property
    def latitude(self) -> float | None:
        rec = self._rec()
        return rec["latitude"] if rec else None

    @property
    def longitude(self) -> float | None:
        rec = self._rec()
        return rec["longitude"] if rec else None

    @property
    def distance(self) -> float | None:
        """Kilometres from the configured centre.

        state is @final and returns round(self.distance, 1), so this IS the
        state. Nothing else should publish a distance.
        """
        rec = self._rec()
        return rec["distance_km"] if rec else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        rec = self._rec()
        if not rec:
            return {}
        # ! No stacking number any more: map_layer names the layer and the
        # card maps it to an offset (D10). The old attribute was read by
        # nothing - LiveTrackMapCard reads that key from its dashboard config.
        attrs: dict[str, Any] = {}
        for key in _PASSTHROUGH:
            if key in rec:
                attrs[key] = rec[key]
        return attrs

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )
