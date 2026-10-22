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

## Flight routes outside FiledRoutesDB

When FiledRoutesDB, which holds US-filed flights only, has no route for a
callsign, the integration asks **adsbdb** - https://www.adsbdb.com - for that
callsign at runtime. Nothing from adsbdb is shipped in this repository, and
nothing it returns is written to a file: answers are held in memory and
forgotten at restart.

adsbdb's README (https://github.com/mrjackwills/adsbdb, read 19 October 2026)
says its flight route data was compiled by David Taylor (Edinburgh) and Jim
Mason (Glasgow), and that copying it, publishing it or adding it to another
database needs David Taylor's explicit permission. Every aircraft showing an
adsbdb route credits adsbdb and both compilers in its attribution.

## Aircraft marker icons

40 of the 63 SVG files in `custom_components/live_track_aircraft/icons/` are by
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
AW609 three-view), and, added 26 September 2026: `tandem.svg` (CH-47 Chinook),
`coaxial.svg` (Kamov), `kmax.svg` (Kaman K-MAX), `gyro.svg` (autogyro),
`flyingwing.svg` (B-2), `fighter.svg` (F-16 planform), `biplane.svg` (Stearman),
`canard.svg` (Rutan Long-EZ), `p180.svg` (Piaggio P.180 Avanti) and `cheyenne.svg`
(Piper PA-42 Cheyenne 400), each drawn to the type's published dimensions; and
`pc6.svg`, `pc7.svg`, `pc9.svg`, `pc12.svg`, `pc21.svg` and `pc24.svg`, whose
outlines are traced from the top views in Pilatus Aircraft Ltd's model building
plans (https://www.pilatus-aircraft.com) and scaled to Pilatus's published spans.
Added 6 October 2026, drawn to each type's published dimensions: `be12.svg`
(Beriev Be-12), `be200.svg` (Beriev Be-200) and `us2.svg` (ShinMaywa US-2).
Their propellers and rotors are animated.
Added 22 October 2026: `vc25a.svg` (Boeing VC-25A, a 747-200B), drawn to the
type's published span and length in its own light blue and white; chords and
engine stations are estimated. It is the one icon drawn in its own colours
rather than a single tone, and it is used for the two VC-25As by Mode S
address.

### Which icon each aircraft type gets

The type-to-icon table in `icons.py` is the default lists from the ADS-B
Radar app, shared by its author, Jos Nutbroek, in September 2026, in the
version he sent on 25 September 2026. `beechcraft.svg` (a light twin, used
for the King Airs, Barons and their kind) is his, sent the same week; the file
he sent is named `beachcraft.svg` and ships unchanged under the name its list
key uses. Since his list files the King Airs under it, `kingair.svg` is no
longer used by the table. On 28 September 2026 he sent two more icons and
their lists: `heavytransport.svg` (his file `heavyfreighter.svg`, shipped
unchanged under the name its list key uses) and `amphibian.svg`.

### Changes made by this integration

The files ship as downloaded except three. `a7.svg` (the helicopter): its two
rotor blades are grouped and animated so the rotor spins; the shapes are
unchanged. `cessna.svg` and `beechcraft.svg`: his outline is kept byte for
byte, a clip hides the propeller band beside each spinner, and the propeller
is redrawn from his own outline in a group that animates it (26 September
2026). A note in each file says so. The type list is followed except where `icons.py` overrides it: EN28
(Enstrom 280), CH7A/CH7B (Helisport CH-7) and MM24 (Magni M24 gyrocopter)
are drawn as helicopters rather than light aircraft; V22 and B609 use the
tiltrotor; the low-wing singles on the Cessna line use `lowwing.svg`; P68,
listed under two icons, uses the twin; and the types in `_ROUND3` in `icons.py`
(twins, canards, biplanes, fighters, gyroplanes, the Chinook, the Kamovs,
the K-MAX, the B-2, the Avanti and the Cheyenne 400), in `_PILATUS` (the
Pilatus types) and in `_ROUND4` (the amphibians and the Beriev A-50) use the
icons above. At
runtime the integration serves altered copies: editor metadata is removed
so browsers parse them strictly, the hardcoded fill is replaced, a dark
outline is drawn round the silhouette, and each icon is scaled by aircraft
category. Icons are served pointing north; the map card turns them to the
direction of travel.
