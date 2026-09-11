"""Live Track Aircraft - real-time ADS-B positions as geo_location entities."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import AircraftCoordinator

PLATFORMS: list[Platform] = [Platform.GEO_LOCATION, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    coordinator = AircraftCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_reload))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded


async def _reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options change.

    ! A config-entry reload does NOT re-import a Python module (D6a-0c).
    Changing code, or adding a platform, needs a FULL Home Assistant restart.
    This only re-reads the options.
    """
    await hass.config_entries.async_reload(entry.entry_id)
