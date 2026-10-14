"""Live Track Aircraft - real-time ADS-B positions as geo_location entities."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import CONF_LATITUDE, CONF_LONGITUDE, DOMAIN
from .coordinator import AircraftCoordinator
from .registrations import async_load_registry, async_refresh_registry
from .route_download import TICK as ROUTE_TICK, RouteDownloader
from .web import register as register_views

PLATFORMS: list[Platform] = [Platform.GEO_LOCATION, Platform.SENSOR]
_DL_KEY = f"{DOMAIN}_route_download"


def _routes_reopen(hass: HomeAssistant) -> None:
    """After a new route file is installed: every coordinator opens it now."""
    for coordinator in hass.data.get(DOMAIN, {}).values():
        routes = getattr(coordinator, "routes", None)
        if routes is not None:
            routes.reopen()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    # Serves the rotated marker silhouettes. Registered once; a second entry
    # re-registering the same view is harmless.
    register_views(hass)

    coordinator = AircraftCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    # The government-aircraft table and the owner database. Load whatever
    # exists, then refresh in the background if it is stale.
    #
    # ! THE CACHE IS SHARED WITH flights_above, DELIBERATELY.
    # registrations.py is lifted VERBATIM and its paths are
    # .storage/flights_above_gov_rotorcraft.json and
    # .storage/flights_above_owners.sqlite. Measured 2026-09-11: both already
    # exist, 322 KB and 10.9 MB, built 2026-09-07. Sharing them costs nothing
    # and saves a second 73 MB download plus a second 10.9 MB database of
    # identical public data on the same machine. Renaming the paths would
    # fork a module we want to keep byte-identical to its origin.
    #
    # ! Dormant outside the US, and every failure path leaves tracking
    # untouched - the module degrades to None rather than raising.
    opts = {**entry.data, **entry.options}
    lat = opts.get(CONF_LATITUDE)
    lon = opts.get(CONF_LONGITUDE)
    await async_load_registry(hass, lat, lon)

    async def _refresh_registry(_now=None) -> None:
        await async_refresh_registry(hass, lat, lon)

    # Fire-and-forget at startup so a stale table is replaced without holding
    # setup up, then a daily tick that only checks the cache age - the real
    # cadence is REFRESH_DAYS.
    hass.async_create_background_task(
        _refresh_registry(), "live_track_aircraft_registry")
    entry.async_on_unload(
        async_track_time_interval(hass, _refresh_registry, timedelta(days=1))
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # The route artifact, downloaded from FiledRoutesDB's public release
    # (route_download.py). ONE downloader per instance, kept outside
    # hass.data[DOMAIN], which holds coordinators only; every entry's timer
    # asks it, and its own due() and lock keep that to one download.
    # Startup check in the background so setup is not held up by 4.6 MB.
    downloader = hass.data.get(_DL_KEY)
    if downloader is None:
        downloader = hass.data[_DL_KEY] = RouteDownloader(
            hass, lambda: _routes_reopen(hass))
    coordinator.route_download = downloader
    hass.async_create_background_task(
        downloader.async_check(startup=True), "live_track_aircraft_route_download")

    async def _check_routes(_now=None) -> None:
        await downloader.async_check()

    entry.async_on_unload(
        async_track_time_interval(hass, _check_routes, ROUTE_TICK))

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
