# Attribution

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
