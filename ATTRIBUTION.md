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

38 of the 42 SVG files in `custom_components/live_track_aircraft/icons/` are by
**ADS-B Radar** — https://adsb-radar.com

Source: https://adsb-radar.com/help/icons.html

Terms, as stated on that page (read 2026-09-21): the icons are free to use
for personal and commercial projects, and the only requirement is a
backlink to ADS-B Radar in the project, website or documentation. This
file, and the Icons section of `README.md`, are that backlink.

The icons belong to their author. They are not covered by the MIT licence
in `LICENSE`, which applies to the code in this repository.

The exceptions are drawn for this project in the style of the set and are
covered by the MIT licence with the code: `kingair.svg` (offered to the set's
author), `lowwing.svg` (a low-wing single), and `tiltrotor.svg` /
`tiltrotorfwd.svg` (a tiltrotor hovering and in cruise, after an AgustaWestland
AW609 three-view). Their propellers and rotors are animated.

### Which icon each aircraft type gets

The type-to-icon table in `icons.py` is the default lists from the ADS-B
Radar app, shared by its author, Jos Nutbroek, in September 2026, in the
version he sent on 25 September 2026. `beechcraft.svg` (a light twin, used
for the King Airs, Barons and their kind) is his, sent the same week; the file
he sent is named `beachcraft.svg` and ships unchanged under the name its list
key uses. Since his list files the King Airs under it, `kingair.svg` is no
longer used by the table.

### Changes made by this integration

The files ship as downloaded except `a7.svg` (the helicopter), whose two
rotor blades are grouped and animated so the rotor spins; the shapes are
unchanged. The type list is followed except where `icons.py` overrides it: EN28
(Enstrom 280), CH7A/CH7B (Helisport CH-7) and MM24 (Magni M24 gyrocopter)
are drawn as helicopters rather than light aircraft; V22 and B609 use the
tiltrotor; the low-wing singles on the Cessna line use `lowwing.svg`; P68,
listed under two icons, uses the twin. At
runtime the integration serves altered copies: editor metadata is removed
so browsers parse them strictly, the hardcoded fill is replaced, a dark
outline is drawn round the silhouette, and each icon is scaled by aircraft
category. Icons are served pointing north; the map card turns them to the
direction of travel.
