# Live Track Aircraft

Live aircraft tracking for Home Assistant. Real-time ADS-B flight positions
overhead, published as `geo_location` entities so they appear on a map without
any glue.

## Status

**Pre-release.** The integration runs live on its development instance:
positions, enrichment, routes and icons turned to each aircraft's track. It
has not been released yet, and installation and setup are not documented
here yet.

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

## Map card

Aircraft are drawn by [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
(`custom:live-track-map-card`), the one map every Live Track integration
renders on. It turns each aircraft's icon to its track, labels it with
its `marker_label`, and moves it between real fixes.

**The card is installed with the integration.** This integration carries a
released copy of the card, serves it, and registers it as a dashboard resource
when Home Assistant starts; there is nothing to download or copy into `www`.
Every Live Track integration does the same, and they keep exactly one resource
row between them: the highest card version any of them carries, never a
downgrade. A card you installed through HACS is left alone. Removing the last
area of this integration hands the row to another Live Track integration,
or removes it if none is left. See the card's README, section
[Live Track](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).

If your dashboards' resources are set in YAML (`lovelace: resource_mode: yaml`),
nothing can be registered for you. A Repairs issue then gives the exact line to
add; it looks like this, with the integration's own address in place of the
placeholders:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_aircraft/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

If the integration's files are removed (through HACS, say) while its areas
are still set up, and no other Live Track integration is installed, nothing is
left to tidy the row: remove it in Settings > Dashboards > Resources. To
install the card by hand instead, follow the card's README; the resource row
of a hand-installed copy under `/local/` is pointed at an integration's copy
only when that copy is a newer release.

Give it the aircraft with
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities),
filtering on `domain: geo_location` and
`attributes: {source: live_track_aircraft}`.

Any other map card that shows `geo_location` entities shows the aircraft too,
as plain markers.

## Live Track Enforcement Aircraft

Its companion, [Live Track Enforcement Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackEnforcementAircraft)
(in development), draws immigration and federal law-enforcement aircraft from a
public, sourced list wherever they fly, not only around your home, and every
aircraft in a focus area of your own. Install both and each keeps to what it
does best: this integration draws every aircraft inside its own area, the
listed ones included, and the companion draws the listed aircraft everywhere
else. One shared poll serves both, and no aircraft is drawn twice.

## Not a fork

Written from scratch. An earlier tracking fork of another project exists
separately and is unaffected by this repository; no code is shared between
them.

## Data sources

Aircraft positions come from two free community networks, tried in order:

- **[adsb.lol](https://adsb.lol)** - data under the
  [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/).
- **[adsb.fi](https://adsb.fi)** - open data for **personal, non-commercial
  use only**, under the terms in its
  [open data README](https://github.com/adsbfi/opendata).

By installing this integration you use both services, and their terms apply to
you. Both are volunteer-run; if you can, support them by feeding a receiver.
Each configured area polls at most once every 15 seconds, and the integration
backs off when a service answers HTTP 429. See [`ATTRIBUTION.md`](ATTRIBUTION.md).

Routes come from FiledRoutesDB, which holds US-filed flight plans only. When it
has no route for a callsign, the integration asks
**[adsbdb](https://www.adsbdb.com)**, once per callsign, and shows the answer
only if it fits where the aircraft actually is. adsbdb's route data is credited
to David Taylor and Jim Mason and may not be copied or republished without
permission, so answers are kept in memory only and never written to a file. A
route's source is in each aircraft's `route_source` attribute.

## Icons

The aircraft marker icons are by [ADS-B Radar](https://adsb-radar.com),
from its [SVG aircraft icon set](https://adsb-radar.com/help/icons.html).
They are used under the author's terms, which ask for a backlink to
ADS-B Radar, and are not covered by this repository's MIT licence. See
[`ATTRIBUTION.md`](ATTRIBUTION.md). Some marker icons were by StrausbergAutomationWorks, 
but have been donated to ADS-B Radar and are therefore subject to its license. 

## Licence

MIT. See `LICENSE`.
