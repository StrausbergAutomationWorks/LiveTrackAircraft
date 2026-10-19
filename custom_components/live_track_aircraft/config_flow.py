"""Config flow for Live Track Aircraft."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import LocationSelector, LocationSelectorConfig

from .centre import from_form, to_form
from .const import (
    CONF_LATITUDE,
    CONF_LOCATION,
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


def _title(cfg: dict[str, Any]) -> str:
    """What the integration card shows: where, and how far.

    e.g. "39.817, -84.050 - 56 km". Four decimal places is about 11 m, which
    is more than a radius of kilometres needs; three is about 110 m and reads
    without clutter.
    """
    return "%.3f, %.3f - %.0f km" % (
        float(cfg[CONF_LATITUDE]), float(cfg[CONF_LONGITUDE]),
        float(cfg[CONF_RADIUS_KM]))


def _schema(defaults: dict[str, Any], hass) -> vol.Schema:
    # ! THE CENTRE IS THE USER'S CHOICE, NOT THE INSTANCE'S LOCATION.
    # It defaults to Home Assistant's own coordinates because that is what
    # most people want, but it is a FIELD, not an assumption. Somebody in
    # Germany may well want to watch O'Hare, and an integration that reads
    # hass.config and never asks makes that impossible. Added 2026-09-11
    # after exactly that was pointed out.
    #
    # ! A MAP MARKER, NOT TWO NUMBER FIELDS (backlog 192, option A, Lee
    # 2026-10-18). No radius circle: the radius stays a number in km below,
    # so it is exact and its limits are visible. The marker is converted back
    # to CONF_LATITUDE and CONF_LONGITUDE by centre.from_form before anything
    # is stored, and the range check lives there (the selector has none).
    return vol.Schema(
        {
            vol.Required(
                CONF_LOCATION,
                default=to_form(defaults, hass.config.latitude,
                                hass.config.longitude),
            ): LocationSelector(
                LocationSelectorConfig(radius=False, icon="mdi:airplane")),
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
            # ! NO ICON OPTIONS since 2026-09-25 (Lee): the icon is always
            # unrotated and disc-less, and the card turns it (icons.py).
        }
    )


class LiveTrackAircraftConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the initial setup."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            values, error = from_form(user_input)
            if error is None:
                # One entry per centre and radius.
                await self.async_set_unique_id(
                    "%.4f_%.4f_%s" % (values[CONF_LATITUDE],
                                      values[CONF_LONGITUDE],
                                      values[CONF_RADIUS_KM])
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    # ! The title IS the integration card. It carries the three
                    # things that distinguish one entry from another - where,
                    # how far, and therefore what you are watching. "Aircraft
                    # within 56 km" said nothing about WHERE, which matters now
                    # that the centre is a free choice anywhere on earth.
                    title=_title(values),
                    data=values,
                )
            errors[CONF_LOCATION] = error
        return self.async_show_form(
            step_id="user", data_schema=_schema({}, self.hass), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        return LiveTrackAircraftOptionsFlow(entry)


class LiveTrackAircraftOptionsFlow(OptionsFlow):
    """Allow the centre, radius, interval and cap to be changed after setup."""

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            values, error = from_form(user_input)
            if error is not None:
                errors[CONF_LOCATION] = error
                user_input = None
        if user_input is not None:
            # ! Keep the card honest. Changing the centre or the radius
            # changes what this entry IS, so the title has to follow - a card
            # reading "39.817, -84.050 - 56 km" while pointed at Frankfurt
            # would be worse than no coordinates at all.
            #
            # ! Only on an explicit save. Home Assistant lets a user rename an
            # entry by hand, and doing this at setup would stomp that name on
            # every restart.
            #
            # ! TITLE AND OPTIONS IN ONE CALL. async_update_entry fires the
            # update listeners on ANY change, a title alone included, and our
            # listener reloads the entry. A title-only update here reloaded it
            # BEFORE Home Assistant stored the new options, and the entry kept
            # observing the old radius: measured 2026-09-19, options 156 km,
            # coordinator 155 km. Setting both together fires the listener once
            # with the new options in place; the options write Home Assistant
            # makes when this flow finishes then changes nothing and fires
            # nothing.
            #
            # ! STORED AS BEFORE: latitude and longitude as two keys (centre.py).
            self.hass.config_entries.async_update_entry(
                self._entry, title=_title(values), options=values)
            return self.async_create_entry(title="", data=values)
        return self.async_show_form(
            step_id="init",
            data_schema=_schema({**self._entry.data, **self._entry.options},
                                self.hass),
            errors=errors,
        )
