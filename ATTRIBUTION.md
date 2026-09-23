# Attribution

## Aircraft position data

Live positions are fetched at runtime from two services. Nothing from either is
shipped in this repository.

**adsb.lol** - https://adsb.lol. The API and all data adsb.lol makes public are
licensed under the Open Database License (ODbL) 1.0,
https://opendatacommons.org/licenses/odbl/ (stated in the API's own
description at https://api.adsb.lol/docs, read 2026-09-22).

**adsb.fi** - https://adsb.fi. Terms, as stated in
https://github.com/adsbfi/opendata (read 2026-09-22; that README last changed
2026-05-17): the open data is for personal, non-commercial use only; it may
not be licensed, sold, rented or leased; it is provided as-is; users must cite
adsb.fi and link to its home page. This file, the Data sources section of
`README.md`, and the attribution shown on every entity are that citation.

## Aircraft marker icons

The 37 SVG files in `custom_components/live_track_aircraft/icons/` are by
**ADS-B Radar** — https://adsb-radar.com

Source: https://adsb-radar.com/help/icons.html

Terms, as stated on that page (read 2026-09-21): the icons are free to use
for personal and commercial projects, and the only requirement is a
backlink to ADS-B Radar in the project, website or documentation. This
file, and the Icons section of `README.md`, are that backlink.

The icons belong to their author. They are not covered by the MIT licence
in `LICENSE`, which applies to the code in this repository.

### Changes made by this integration

The files ship as downloaded. At runtime the integration serves altered
copies: editor metadata is removed so browsers parse them strictly, the
hardcoded fill is replaced, a circular background is added, and each icon
is scaled by aircraft category and, by default, rotated to the direction
of travel.
