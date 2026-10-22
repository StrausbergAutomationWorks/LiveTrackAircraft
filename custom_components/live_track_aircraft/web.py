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

from . import icons, pictures

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
        path = icons.icon_path(key)
        if path is None:
            # ! valid_key() rejects anything but [a-z0-9], so a path segment
            # cannot climb out of the icons folder.
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
        # Only "1" turns the lights on, so a mangled value fails safe.
        lights = request.query.get("l") == "1"

        try:
            svg = await request.app["hass"].async_add_executor_job(
                icons.render, path, degrees, 64, tone, weight, badge, lights)
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Could not render %s at %s", key, angle)
            return web.Response(status=500, text="render failed")

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
    # ! As the icons: a picture URL cannot carry a token. What is in the
    # folder is the user's choice to show; pictures.py says so.
    requires_auth = False

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
                "Cache-Control": "public, max-age=86400",
                "X-Content-Type-Options": "nosniff",
                # A user's SVG must not run script if opened directly.
                "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; img-src data:",
            },
        )


def _read(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read(pictures.MAX_BYTES + 1)[: pictures.MAX_BYTES]


def register(hass: HomeAssistant) -> None:
    hass.http.register_view(AircraftIconView())
    hass.http.register_view(AircraftPictureView())
