# Live Track Aircraft

Live aircraft tracking for Home Assistant. Real-time ADS-B flight positions
overhead, published as `geo_location` entities so they appear on a map without
any glue.

## Status

**No code yet.** This repository holds its identity and licence while the
integration is written.

## Why it exists

`geo_location` is what Home Assistant's map actually consumes. An integration
that publishes ordinary sensors needs a translation layer to reach the map —
one extra template sensor per aircraft. Emitting the map vocabulary natively
removes that layer.

## Design

| | |
|---|---|
| Domain | `live_track_aircraft` — settled and permanent |
| Entities | one `geo_location` entity per aircraft, created and removed as aircraft come and go |
| State | distance from the configured centre |
| Source | ADS-B, via a source seam so a second feed can be added without touching entity code |
| Identity | ICAO hex. Never derived from a callsign, which changes |

Part of the Live Track family, which shares one map vocabulary so several
integrations can render on a single map.

## Not a fork

Written from scratch. An earlier tracking fork of another project exists
separately and is unaffected by this repository; no code is shared between
them.

## Icons

The aircraft marker icons are by [ADS-B Radar](https://adsb-radar.com),
from its [SVG aircraft icon set](https://adsb-radar.com/help/icons.html).
They are used under the author's terms, which ask for a backlink to
ADS-B Radar, and are not covered by this repository's MIT licence. See
[`ATTRIBUTION.md`](ATTRIBUTION.md).

## Licence

MIT. See `LICENSE`.
