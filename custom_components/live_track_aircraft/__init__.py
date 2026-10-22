"""Live Track Aircraft - real-time ADS-B positions as geo_location entities."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .adsbdb import AdsbdbRoutes
from .airport_download import TICK as AIRPORT_TICK, AirportDownloader
from .const import CONF_LATITUDE, CONF_LONGITUDE, DOMAIN
from .coordinator import AircraftCoordinator
from .registrations import async_load_registry, async_refresh_registry
from .route_download import TICK as ROUTE_TICK, RouteDownloader
from .web import register as register_views

PLATFORMS: list[Platform] = [Platform.GEO_LOCATION, Platform.SENSOR]
_DL_KEY = f"{DOMAIN}_route_download"
_AIR_KEY = f"{DOMAIN}_airport_download"
_ADSBDB_KEY = f"{DOMAIN}_adsbdb"


def _airports_recheck(hass: HomeAssistant) -> None:
    """After a new airport table is installed: every coordinator looks at it now."""
    for coordinator in hass.data.get(DOMAIN, {}).values():
        airports = getattr(coordinator, "airports", None)
        if airports is not None:
            airports.recheck()


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
    # adsbdb routes for callsigns FiledRoutesDB does not hold (adsbdb.py,
    # backlog 292). ONE client per instance, outside hass.data[DOMAIN] like
    # the downloaders: adsbdb limits by address, so every entry shares one
    # budget and one in-memory cache. Set before the first poll.
    coordinator.adsbdb = hass.data.setdefault(_ADSBDB_KEY, AdsbdbRoutes())
    await coordinator.async_config_entry_first_refresh()

    # The government-aircraft table and the owner database. Load whatever
    # exists, then refresh in the background if it is stale.
    #
    # ! NOT SHARED WITH flights_above (corrected 2026-10-22). This read that
    # these were flights_above's own files, lifted verbatim. Since the
    # 2026-09-11 divergence the paths are SAW-neutral and ours -
    # .storage/saw_faa_gov_aircraft.json (saw_faa_gov_rotorcraft.json until
    # 2026-10-22) and .storage/saw_faa_owners.sqlite - while flights_above
    # keeps its own flights_above_gov_rotorcraft.json. Measured 2026-10-22:
    # no other component on the box names either SAW file.
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

    # The airport table, downloaded from AirportZones' public release
    # (airport_download.py, backlog 245). Same shape as the routes: one
    # downloader per instance, every entry's timer asks it, startup check in
    # the background.
    air = hass.data.get(_AIR_KEY)
    if air is None:
        air = hass.data[_AIR_KEY] = AirportDownloader(
            hass, lambda: _airports_recheck(hass))
    coordinator.airport_download = air
    hass.async_create_background_task(
        air.async_check(), "live_track_aircraft_airport_download")

    async def _check_airports(_now=None) -> None:
        await air.async_check()

    entry.async_on_unload(
        async_track_time_interval(hass, _check_airports, AIRPORT_TICK))

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
