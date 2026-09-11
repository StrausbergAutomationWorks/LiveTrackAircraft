"""Config flow for Live Track Aircraft."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MAX_AIRCRAFT,
    CONF_RADIUS_KM,
    CONF_SCAN_INTERVAL,
    DEFAULT_MAX_AIRCRAFT,
    DEFAULT_RADIUS_KM,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_MAX_AIRCRAFT,
    MAX_RADIUS_KM,
    MAX_SCAN_INTERVAL,
    MIN_MAX_AIRCRAFT,
    MIN_RADIUS_KM,
    MIN_SCAN_INTERVAL,
)


def _schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_RADIUS_KM, default=defaults.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM)
            ): vol.All(vol.Coerce(float), vol.Range(min=MIN_RADIUS_KM, max=MAX_RADIUS_KM)),
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): vol.All(
                vol.Coerce(int),
                # ! The 15 s floor is MEASURED, not chosen. At 5 s, 196 of
                # 360 requests returned HTTP 429.
                vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
            ),
            vol.Required(
                CONF_MAX_AIRCRAFT,
                default=defaults.get(CONF_MAX_AIRCRAFT, DEFAULT_MAX_AIRCRAFT),
            ): vol.All(
                vol.Coerce(int),
                # ! A guard rail, not a display control. Thinning belongs to
                # the card. A ceiling is not a count (A2).
                vol.Range(min=MIN_MAX_AIRCRAFT, max=MAX_MAX_AIRCRAFT),
            ),
        }
    )


class LiveTrackAircraftConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the initial setup."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            latitude = self.hass.config.latitude
            longitude = self.hass.config.longitude
            # One entry per centre and radius, matching the fork's shape.
            await self.async_set_unique_id(
                f"{latitude:.4f}_{longitude:.4f}_{user_input[CONF_RADIUS_KM]}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"Aircraft within {user_input[CONF_RADIUS_KM]:.0f} km",
                data={
                    CONF_LATITUDE: latitude,
                    CONF_LONGITUDE: longitude,
                    **user_input,
                },
            )
        return self.async_show_form(step_id="user", data_schema=_schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        return LiveTrackAircraftOptionsFlow(entry)


class LiveTrackAircraftOptionsFlow(OptionsFlow):
    """Allow radius, interval and cap to be changed after setup."""

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=_schema({**self._entry.data, **self._entry.options}),
        )
