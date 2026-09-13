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

from . import icons

_LOGGER = logging.getLogger(__name__)

URL_BASE = "/api/live_track_aircraft/icon"


def picture_url(key: str, degrees: int | None,
                tone: str = "default", weight: float | None = None) -> str:
    """The entity_picture for one icon at one angle, tone and size.

    ! TONE AND WEIGHT RIDE AS QUERY PARAMETERS, not path segments. The route
    shape is unchanged, so an older cached URL still resolves, and the query
    is part of the cache key - a government aircraft and an airliner on the
    same silhouette are two different cached images, as they should be.
    """
    url = "%s/%s/%s.svg" % (
        URL_BASE, key, "fixed" if degrees is None else degrees)
    extra = []
    if tone and tone != "default":
        extra.append("t=%s" % tone)
    if weight is not None:
        extra.append("w=%.2f" % weight)
    return url + ("?" + "&".join(extra) if extra else "")


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

        try:
            svg = await request.app["hass"].async_add_executor_job(
                icons.render, path, degrees, 64, tone, weight)
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


def register(hass: HomeAssistant) -> None:
    hass.http.register_view(AircraftIconView())
