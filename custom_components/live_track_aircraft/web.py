"""Serves the rotated marker icons.

! WHY AN HTTP VIEW AND NOT A FILE IN www/. The icons ship INSIDE the
component, so a user installs the integration and gets them - nothing to copy
into www/, nothing to configure, and the integration stays self-contained for
anyone anywhere. It also means rotation can be computed per request instead of
pre-generating 72 variants of 37 icons on disk.

! WHY entity_picture AND NOT THE CARD. ha-map-card has no rotation support -
checked its source, the only "rotat" in it is a CSS hue-rotate - but its
`get picture()` already falls back to `attributes.entity_picture`. So the
integration hands it a picture that is already pointing the right way and the
card needs to know nothing about headings.
"""

from __future__ import annotations

import logging

from aiohttp import web

from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from . import icons, photos, pictures

_LOGGER = logging.getLogger(__name__)

# The URL shape and the picture URL live in icons.py, testable without HA.
# ! The view still answers every URL ever issued - angles and the disc
# included - so an older cached URL resolves; the integration now issues
# only unrotated, disc-less ones (icons.picture_url).
URL_BASE = icons.URL_BASE
picture_url = icons.picture_url


class AircraftIconView(HomeAssistantView):
    """Return one aircraft silhouette, rotated."""

    url = URL_BASE + "/{key}/{angle}.svg"
    name = "api:live_track_aircraft:icon"

    # ! An <img> tag cannot send an Authorization header, so a picture URL
    # has to be reachable without one. These are 37 public-domain-ish
    # silhouettes with no user data in them - the URL reveals only that an
    # aircraft of some shape is somewhere. Nothing here is sensitive.
    requires_auth = False

    async def get(self, request: web.Request, key: str, angle: str) -> web.Response:
        # ! valid_key() rejects anything but [a-z0-9], so a path segment
        # cannot climb out of the icons folder. It is pure; the lookup that
        # touches the disk (icon_path, os.path.exists) runs in the executor
        # job with the render (hacs/default#14501 item 4).
        if not icons.valid_key(key):
            return web.Response(status=404, text="unknown icon")

        if angle == "fixed":
            degrees: int | None = None
        else:
            try:
                degrees = int(angle) % 360
            except ValueError:
                return web.Response(status=400, text="bad angle")

        # ! Both are UNTRUSTED input off a URL. tone resolves through a
        # lookup that falls back to default, and weight is clamped in
        # render(), so neither can reach the filesystem or the output.
        tone = request.query.get("t", "default")
        try:
            weight = float(request.query.get("w", icons.DEFAULT_WEIGHT))
        except (TypeError, ValueError):
            weight = icons.DEFAULT_WEIGHT
        # Anything but "0" keeps the badge, so a mangled value fails safe.
        badge = request.query.get("b") != "0"
        # l=g glow, l=w wig-wag, the old l=1 paired with the tone; anything
        # else is unlit, so a mangled value fails safe (lights_from_query).
        lights = icons.lights_from_query(request.query.get("l"))

        try:
            svg = await request.app["hass"].async_add_executor_job(
                _render_key, key, degrees, tone, weight, badge, lights)
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Could not render %s at %s", key, angle)
            return web.Response(status=500, text="render failed")
        if svg is None:
            return web.Response(status=404, text="unknown icon")

        return web.Response(
            body=svg.encode("utf-8"),
            content_type="image/svg+xml",
            headers={
                # 72 angles per icon, and the artwork never changes, so this
                # is fetched once per aircraft shape per day and then cached.
                "Cache-Control": "public, max-age=86400, immutable",
            },
        )


class AircraftPictureView(HomeAssistantView):
    """Return the user's own picture for one aircraft (pictures.py)."""

    url = pictures.URL_BASE + "/{name}"
    name = "api:live_track_aircraft:picture"
    # ! AUTHENTICATED, since 0.1.3 (hacs/default#14501 item 1, Frenck
    # 2026-11-19: these are the user's own files, and the hex in the URL is
    # public). requires_auth stays at Home Assistant's default, True. The
    # entity's URL is signed (pictures.Overrides, async_sign_path), which the
    # auth middleware accepts in place of a token on a GET; measured on Home
    # Assistant 2026.11.2 on 2026-11-20, before this change.

    async def get(self, request: web.Request, name: str) -> web.Response:
        hass = request.app["hass"]
        folder = hass.config.path(pictures.DIR_NAME)
        found = await hass.async_add_executor_job(pictures.resolve, folder, name)
        if found is None:
            return web.Response(status=404, text="no picture")
        path, content_type = found
        body = await hass.async_add_executor_job(_read, path)
        return web.Response(
            body=body,
            content_type=content_type,
            headers={
                # ?v= is the file's mtime, so a replaced file is a new URL.
                # private: the user's own file, behind a sign-in, is kept by
                # the browser only, never by a shared cache on the way.
                "Cache-Control": "private, max-age=86400",
                "X-Content-Type-Options": "nosniff",
                # A user's SVG must not run script if opened directly.
                "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; img-src data:",
            },
        )


class AircraftPhotoView(HomeAssistantView):
    """A photo of one aircraft from Planespotters.net, asked by the map card when its hover box first opens
    (photos.py; 06_MAP_CONTRACT.md D4i; backlog 361). Signed in only: requires_auth stays True, and the card
    asks with the viewer's own sign-in (hass.callApi). Answers `{"photo": <D4g marker_photo> | null}`; 503
    while lookups are paused or one failed, so the card asks again later."""

    url = photos.URL_BASE + "/{hexid}"
    name = "api:live_track_aircraft:photo"

    def __init__(self, lookups: photos.PhotoLookups) -> None:
        self._lookups = lookups

    async def get(self, request: web.Request, hexid: str) -> web.Response:
        from homeassistant.helpers.aiohttp_client import async_get_clientsession  # noqa: PLC0415

        h = photos.valid_hex(hexid)
        if h is None:
            return self.json_message("not an ICAO address", status_code=400)
        state, photo = await self._lookups.get(async_get_clientsession(request.app["hass"]), h)
        if state in (photos.PHOTO, photos.NONE):
            resp = self.json({"photo": photo})
        else:
            resp = self.json_message(f"photo lookup {state}", status_code=503)
        # The card keeps the answer itself (at most 12 h, PhotoLookup.js); no browser or proxy copy.
        resp.headers["Cache-Control"] = "no-store"
        return resp


def _render_key(key: str, degrees, tone, weight, badge, lights) -> str | None:
    """BLOCKS: the icon's file (icon_path stats it) and its render, in one
    executor job. None when no picture has that key."""
    path = icons.icon_path(key)
    if path is None:
        return None
    return icons.render(path, degrees, 64, tone, weight, badge, lights)


def _read(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read(pictures.MAX_BYTES + 1)[: pictures.MAX_BYTES]


_PHOTOS_KEY = "live_track_aircraft_photos"


def register(hass: HomeAssistant) -> None:
    """Register the views ONCE per run. Every config entry's setup calls this; a second registration of the same
    URL would add a second route to the same view (the photo view holds state, so it must be one object)."""
    if hass.data.get(_PHOTOS_KEY) is not None:
        return
    lookups = hass.data[_PHOTOS_KEY] = photos.PhotoLookups()
    hass.http.register_view(AircraftIconView())
    hass.http.register_view(AircraftPictureView())
    hass.http.register_view(AircraftPhotoView(lookups))
