# Live Track Aircraft

**English** · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [All languages](#languages)

**Aircraft for Home Assistant, on one map.** Live Track Aircraft puts the
aircraft flying over your home, or over any place in the world you choose, on
your Home Assistant map: each one drawn as its own type, turned to the
direction it flies, with who operates it and, when known, where it is going.
It can also follow chosen aircraft and flights wherever they are, and watch
for military aircraft in areas you name.

> **Live Track Aircraft is one module of Live Track**, a family of Home
> Assistant integrations that draw everything that moves, and the weather it
> moves through, on one shared map: aircraft, ships, trains and weather.
> Install it on its own, or beside the other modules
> ([list below](#part-of-live-track-the-other-modules)).

> **Growing, and open to ideas.** Live Track Aircraft covers the whole world
> where volunteers run receivers today, with routes and owner names in most
> detail for the United States, and we are adding more route sources and
> aircraft information. Is yours missing? [Suggest it](#help-it-grow), or add
> it yourself: we will help you do it.

**Status: 0.1.6, released.** Added to the Marketplace by link
([below](#install-it-step-by-step)); it is not in the Marketplace's catalog
yet.

Original work by StrausbergAutomationWorks. Not affiliated with, or endorsed
by, adsb.fi, adsb.lol, adsbdb, the Federal Aviation Administration (United
States), OurAirports, ADS-B Radar, Planespotters.net, any airline or any
aircraft operator.

> ⚠ **Not a safety system.** It shows public data, usually seconds old and
> sometimes a minute or more, and only aircraft that volunteers' receivers
> happen to hear. It is not for navigation, for separating aircraft, or for
> any other operational purpose.

---

## Contents

1. [Everything it does](#everything-it-does)
2. [Where it works](#where-it-works)
3. [Part of Live Track: the other modules](#part-of-live-track-the-other-modules)
4. [Before you start](#before-you-start)
5. [Install it, step by step](#install-it-step-by-step)
6. [Set it up, step by step](#set-it-up-step-by-step)
7. [Free keys that switch on more, step by step](#free-keys-that-switch-on-more-step-by-step)
8. [Put the map on a dashboard](#put-the-map-on-a-dashboard)
9. [Use it in automations](#use-it-in-automations)
10. [Everything on the map, in detail](#everything-on-the-map-in-detail)
11. [All the entities it creates](#all-the-entities-it-creates)
12. [What it sends and downloads](#what-it-sends-and-downloads)
13. [Help it grow](#help-it-grow)
14. [Languages](#languages)
15. [Credits and licences](#credits-and-licences)
16. [Keywords](#keywords)

---

## Everything it does

### On the map, with nothing to set up

You add an **area**: a centre on the map and a radius around it. It starts at
your home. Everything below then appears in that area, or, where the table
says so, anywhere in the world.

| What | Where | From |
|---|---|---|
| **Aircraft**: airliners, light aircraft, helicopters, gliders, balloons and drones, each drawn as its own type and turned to the direction it flies | in each area | adsb.fi, or adsb.lol when adsb.fi does not answer |
| **Who operates it**: the airline, the owner, or the type when nothing else is known, on the marker's label | every aircraft | the airline's call sign; the FAA aircraft registry (United States) for owners |
| **Colours that say who flies it**: government, police, federal law enforcement, the military, air ambulances and helicopters each in their own colour | every aircraft where it is known | the FAA aircraft registry (United States) and the feed's military flag |
| **Routes**: where the aircraft took off and where it is going, with the airports' names and an estimated arrival time | flights that file a flight plan with the FAA (United States); elsewhere when adsbdb knows the flight | FiledRoutesDB, then adsbdb |
| **The presidential aircraft of the United States**, with the aircraft of the 89th Airlift Wing and the military aircraft escorting them | anywhere in the world | adsb.fi and its military list |
| **Aircraft on the public EnforcementAircraft list** (immigration and federal law enforcement), with flashing lights | in each area | the EnforcementAircraft list |
| **Military aircraft in your watch areas**: every aircraft the feed marks as military, inside up to ten circles you name, even when your area is full. Optional: you type the circles into the setup dialog | anywhere in the world | adsb.fi's military list |
| **Aircraft and flights you follow**: your own plane, a club's fleet, or the flight a family member is on. Optional: you type their codes into the setup dialog | anywhere in the world | adsb.fi |
| **Photos**: a photo of the aircraft, with the photographer's name, when you point at it | every aircraft Planespotters.net has a photo of | Planespotters.net ([more](#photos)) |
| **Your own picture for one aircraft**, in place of its icon | wherever that aircraft is shown | a picture you put in a folder ([how](#your-own-picture-for-one-aircraft)) |

### Switched on by your own free key or account

| Free key or account | What it adds |
|---|---|
| **adsb.lol** key | more requests a day to adsb.lol, the second source, so the map keeps going during a long adsb.fi outage |

Each takes a few minutes to get: [step by step below](#free-keys-that-switch-on-more-step-by-step).

---

## Where it works

| Region | What you get | From | Needs |
|---|---|---|---|
| **The whole world** | aircraft positions wherever volunteers run receivers: dense over Europe and North America, thinner elsewhere, and little or nothing far out at sea | adsb.fi, adsb.lol | nothing |
| **The whole world** | airport names on routes, and the airports' time zones for the arrival time | OurAirports, by way of the AirportZones table | nothing |
| **The whole world** | routes for many airline flights, checked against where the aircraft actually is | adsbdb | nothing |
| **North America**: United States | owner and operator names for aircraft registered in the United States, and the colours for government and police aircraft | the FAA aircraft registry | nothing |
| **North America**: United States | routes for flights filed with the FAA, including international flights to and from the United States | FiledRoutesDB | nothing |

Not on the list? [Tell us](#help-it-grow). Where someone publishes the data
openly, we will look at adding it.

⚠ **Coverage is good where receivers are, and absent where they are not.** An
aircraft appears only when a volunteer's receiver hears it, or when several
receivers together can locate it. No setting can create coverage that does not
exist. **An empty sky on the map may mean no receivers near you, not no
aircraft.**

⚠ **Routes are mostly for the United States.** FiledRoutesDB holds only flight
plans filed with the FAA. Elsewhere a route comes from adsbdb, which knows many
airline flights and few others, so outside the United States many aircraft
show no route.

⚠ **Owner names are for aircraft registered in the United States only.** An
aircraft registered in another country shows its airline from its call sign,
or its type.

---

## Part of Live Track: the other modules

Live Track is a set of Home Assistant integrations, one per kind of moving
thing, all drawn on the same map card. Each works on its own; together they
make one live picture. They share the map card and a Python library
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
so installing another one adds no requests to a source another already reads.

| Module | What it puts on the map | Status |
|---|---|---|
| **Live Track Aircraft** | aircraft overhead from ADS-B, with routes and type icons (this module) | released |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | ships and boats from AIS, near you or anywhere | released |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | commuter trains in North America, Europe and Australia | released |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | intercity and long-distance trains in North America, Europe and Australia | released |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | immigration and federal law-enforcement aircraft and vessels, from public lists | released |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | weather, storms and natural hazards | released |
| Live Track Stations | departure boards and "time to leave" alerts for every station | planned |
| Live Track Satellites | satellites passing overhead | planned |
| Live Track Freight Trains | freight and work trains where railways publish them | planned |
| Live Track Transit | city buses, trams, ferries and metro | planned |
| Live Track Intercity Buses | intercity and regional coaches | planned |
| Live Track Commuter Buses | commuter buses | planned |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | the shared map card every module draws on | released, installed with each module |

Everything is free and open source. Nothing is held back for sponsors.

---

## Before you start

* **Home Assistant** 2026.11 or later.
* **The Marketplace** (HACS) in your Home Assistant, to install and update it
  the easy way. Without it you can copy the files by hand.
* **Internet access** for Home Assistant: everything comes from public
  sources.
* **Optional: auto-entities** from the Marketplace, to put the markers on the
  map (see [Put the map on a dashboard](#put-the-map-on-a-dashboard)).
* Nothing to pay and no account needed. The adsb.lol key above is optional.
* Home Assistant installs the two Python packages it needs (`saw-livetrack`
  and `tzfpy`) by itself the first time the integration loads.

---

## Install it, step by step

### From the Marketplace (recommended)

Live Track Aircraft is not in the Marketplace's catalog yet. Add it by its
link:

1. In Home Assistant, open **Settings → Marketplace** (HACS).
2. Choose **Add from link** (or the three-dot menu → **Custom repositories**).
3. Enter `StrausbergAutomationWorks/LiveTrackAircraft`. If asked for the
   type, choose **Integration**.
4. Find **Live Track Aircraft** in the list and choose **Download** or
   **Install**.
5. **Restart Home Assistant**: **Settings → System → Repairs** offers the
   restart, or use **Settings → System → Restart**.

The Marketplace then offers each new release as an update.

### By hand

1. Download the source code of the
   [latest release](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/releases/latest).
2. Copy its `custom_components/live_track_aircraft` folder into the
   `custom_components` folder of your Home Assistant configuration folder
   (create `custom_components` if it is not there).
3. Restart Home Assistant.

To update by hand, replace the folder with the new release's and restart.

---

## Set it up, step by step

The setup dialog is in English.

1. Open **Settings → Devices & services**.
2. Choose **Add integration** (bottom right) and search for **Live Track
   Aircraft**.
3. **Centre**: drag the marker to the middle of the sky you want to watch. It
   starts at your home.
4. **Radius (km)**: how far from the centre aircraft are shown, from 1 to
   463 km (0.6 to 288 miles). If unsure, keep 56 km (35 miles).
5. **Update interval (seconds)**: keep 15. The sources refuse requests made
   more often than that.
6. **Maximum aircraft published**: keep 250. It is a safety limit, not a way
   to show fewer aircraft.
7. Leave the four optional fields empty for now. Each is explained below.
8. Choose **Submit**.

That is all. Aircraft appear within a minute. Each area is one entry, titled
with its centre and radius, for example `39.817, -84.050 - 56 km`. To watch a
second area, add the integration again with another centre or radius. The
same centre and radius twice is refused.

Routes, airport names and owner names fill in over the first minutes, as the
files they come from download ([What it sends and downloads](#what-it-sends-and-downloads)).

### Change what it shows: the options

Open **Settings → Devices & services → Live Track Aircraft → Configure** (the
cog) on the area you want to change. Every option, in plain words:

| Option | What it does | Default |
|---|---|---|
| **Centre** | moves the area; its title follows | your home |
| **Radius (km)** | how far from the centre aircraft are shown, 1 to 463 km (0.6 to 288 miles) | 56 km (35 miles) |
| **Update interval (seconds)** | how often positions are asked for, 15 to 3,600 seconds | 15 |
| **Maximum aircraft published** | a safety limit, 1 to 1,000; when more aircraft are in the circle, the nearest are kept. Aircraft you follow, aircraft in your military watch areas and aircraft on the EnforcementAircraft list are always kept | 250 |
| **Military watch areas** | circles where every military aircraft is shown ([how](#military-watch-areas)) | empty |
| **Aircraft to follow (hex codes)** | aircraft followed anywhere, by their hex code ([how](#aircraft-and-flights-you-follow)) | empty |
| **Flights to follow (call signs)** | flights followed anywhere, by their call sign (the same section) | empty |
| **adsb.lol API key** | your own key for adsb.lol ([how to get one](#free-keys-that-switch-on-more-step-by-step)) | empty |

Clear one of the four optional fields to switch that part off.

---

## Free keys that switch on more, step by step

All of these are free and personal: each person who installs Live Track
Aircraft gets their own. Paste each into **Settings → Devices & services →
Live Track Aircraft → Configure**.

### adsb.lol (more requests to the second source, the whole world)

Live Track Aircraft asks adsb.fi first, and asks adsb.lol only while adsb.fi
does not answer. Without a key, adsb.lol allows 500 requests a day from one
internet address, which an adsb.fi outage can use up in about two hours. A key
raises that limit. You do not need one to start.

1. Open <https://www.adsb.lol/request> and ask for a free key with the form
   there. adsb.lol's documentation gives this key 1,000 requests a day.
2. If you feed adsb.lol with a receiver of your own, use your feeder key
   instead: adsb.lol's documentation gives it 7,200 requests a day. Your keys
   are under **My keys** on adsb.lol (<https://www.adsb.lol/mmb>).
3. Paste the key into **adsb.lol API key**, and choose **Submit**.

The key is sent only to adsb.lol. If adsb.lol refuses it (wrong or expired),
Live Track Aircraft carries on without it, and the area's
`sensor.aircraft_in_range` shows `refused` in its `adsblol_key` attribute
until you change the key. Otherwise it shows `set`, or `none` with no key. No
password and no secret is needed.

---

## Put the map on a dashboard

The map is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
the card every Live Track module draws on. **It is installed with Live Track
Aircraft**: nothing to download, nothing to copy, no resource to add.

1. Open a dashboard, choose the pencil (**Edit dashboard**), then **Add card**.
2. Scroll to the bottom and choose **Manual**.
3. Paste this, and choose **Save**:

```yaml
type: custom:auto-entities
card:
  type: custom:live-track-map-card
filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_aircraft
      options:
        display: attribute
        attribute: marker_label
        position_transition: auto
  exclude:
    - state: unavailable
```

This form needs [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)
from the Marketplace. With other Live Track modules installed, add one more
`- domain: geo_location` filter for each of their sources
(`live_track_ships`, `live_track_weather` and so on).

**Without auto-entities:** LiveTrackMapCard can choose what it shows by
itself, with `entity_filter`. Paste this instead; nothing more to install:

```yaml
type: custom:live-track-map-card
entity_filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_aircraft
      options:
        display: attribute
        attribute: marker_label
        position_transition: auto
  exclude:
    - state: unavailable
```

Other Live Track modules go in `entity_filter` the same way: one more
`- domain: geo_location` rule for each source.

**On the map:**

* Each aircraft is drawn as its own type, turned to the direction it flies,
  and moves smoothly between the positions it reports.
* Its label is the flight's call sign (`UAL308`), or else who operates it
  (`Lewis University`), or else its type (`Cessna 172 Skyhawk`).
* **Point at** an aircraft to see its airline or operator, its photo when
  there is one and, when a route is known, its route and how many minutes
  until it arrives. **Click** it for all its details and a larger photo,
  linked to its page on Planespotters.net ([Photos](#photos)).

If your dashboards' resources are set in YAML (`lovelace: resource_mode: yaml`),
nothing can be registered for you: a **Repairs** issue then gives the exact
line to add. A card you installed yourself through the Marketplace is left
alone. If the integration's files are removed while its areas are still set
up, and no other Live Track module is installed, remove the card's row
yourself in **Settings → Dashboards → Resources**. Any other map card that
shows `geo_location` entities shows the aircraft too, as plain markers.

---

## Use it in automations

Everything is an ordinary Home Assistant entity, so the automation editor
works with it, no code needed.

**A phone notification when a military aircraft is in one of your military
watch areas:**

1. **Settings → Automations & scenes → Create automation → Create new
   automation**.
2. **When**: **Add trigger** → **Entity** → **Numeric state**. Choose the
   entity **Aircraft in range**, the **Attribute** **Military in areas**
   (`military_in_areas`), and **Above** `0`.
3. **Then do**: **Add action**, search for your phone's notification action
   (it carries your phone's name), and enter a message, for example:

   ```text
   A military aircraft is in your watch area
   ```

4. **Save**.

This needs at least one military watch area ([how](#military-watch-areas)).

**Other ideas:** a notification when a family member's flight is in the air,
from the `followed_found` attribute rising above 0; a light that turns on when
more than 20 aircraft are over your home in Frankfurt (Germany); a dashboard
count of aircraft over your airfield in Queensland (Australia) from
`sensor.aircraft_in_range`; a message when your club's aircraft takes off,
from its own entity (`geo_location.aircraft_` and its hex code) appearing.

---

## Everything on the map, in detail

### Aircraft

Aircraft send their position by radio, a system called ADS-B. Volunteers
around the world run receivers and share what they hear through community
networks. Live Track Aircraft asks one of them, adsb.fi, for every aircraft
inside your circle, every 15 seconds by default. When adsb.fi does not answer,
or answers with far fewer aircraft than a moment before, it asks adsb.lol.
Where several receivers hear an aircraft that does not send its own position,
the networks can still locate it (multilateration, MLAT).

Each aircraft is one marker, named from its hex code: the six-character
address its transponder sends, which belongs to the aircraft and does not
change. The marker appears when the aircraft comes into your circle and is
removed when it leaves.

The label is the most useful name known, in this order:

| The aircraft has | The label shows | Example |
|---|---|---|
| a flight's call sign | the call sign | `UAL308` |
| otherwise a known operator | the operator | `Lewis University` |
| otherwise a known type | the type | `Cessna 172 Skyhawk` |
| none of these | the registration, the type code or the hex code | `N12345` |

⚠ Not shown: aircraft on the ground, airport vehicles, and radar-only tracks
that carry no identity. An aircraft that does not broadcast, or flies where no
receiver hears it, cannot be shown.

On each aircraft: `identity` (the hex code), `callsign`, `registration`,
`aircraft_type`, `aircraft_name`, `operator`, `altitude_m`, `speed_kmh`,
`vertical_rate_ms`, `course_deg`, `squawk`, `emitter_category`,
`is_military`, `is_government`, `last_seen`.

### Colours and icons

Each aircraft is drawn as its own type: an airliner, a business jet, a light
single, a twin, a helicopter, a tiltrotor, a glider, a balloon, a drone and
many more, sized by its class. Propellers and rotors turn. The icon is turned
to the direction the aircraft flies; a slow aircraft keeps its last direction
rather than spinning.

Colour says who flies it, where that is known:

| Colour | Who |
|---|---|
| light grey | most aircraft |
| mint green | helicopters and other rotorcraft |
| amber | government aircraft and air ambulances |
| blue | federal law enforcement |
| army green | the military and the Coast Guard |
| white, with flashing blue lights | police |
| flashing red and blue lights | aircraft on the EnforcementAircraft list ([below](#the-enforcementaircraft-list-and-live-track-salt)) |
| a steady glow | an airliner that flies ICE Air charters, among other work |

⚠ Who owns an aircraft is known mostly for aircraft registered in the United
States, from the FAA registry. Elsewhere the colour comes only from the
feed's military flag and the aircraft's type.

### Routes and arrival times

A route shows where the aircraft took off and where it is going, with both
airports' names, and an estimated arrival time. It comes from two places:

1. **FiledRoutesDB**, a public file of flight plans filed with the FAA
   (United States), built and published by StrausbergAutomationWorks and
   downloaded once a day. Every route is checked against where the aircraft
   is and the way it is flying. A route that does not fit is still shown, and
   marked as not fitting in `route_check`.
2. **adsbdb**, asked only when FiledRoutesDB has no route for the call sign,
   once per call sign. Its answer is shown only when it fits where the
   aircraft actually is.

Aircraft whose owners asked the FAA to keep their flights from public display
(the FAA's LADD list, Limiting Aircraft Data Displayed) are removed from
FiledRoutesDB before it is published. Live Track Aircraft deletes its copy
when the file expires, or when the LADD list it was built against is more than
14 days old, so it never shows routes filtered against an old list.

The arrival time is an estimate, not a schedule: the straight-line distance
left, at the aircraft's speed when it is cruising and at a typical speed for
its class when it is not. Holding, the approach and taxiing are not counted.

On each aircraft with a route: `origin_icao`, `destination_icao`,
`origin_name`, `destination_name`, `route_source`, `route_check`,
`arrival_estimated_at`.

### Military watch areas

Every aircraft the feed marks as military, inside circles you choose,
anywhere in the world, even when your area is full.

1. Open **Settings → Devices & services → Live Track Aircraft → Configure**
   on an area.
2. In **Military watch areas**, type each circle as `latitude,longitude,km`,
   and separate circles with semicolons, for example
   `39.81,-84.04,150; 34.0,-117.8,463`. Up to ten circles, each from 1 to
   2,000 km (0.6 to 1,243 miles).
3. Choose **Submit**.

The military aircraft inside them appear within a minute and move once a
minute. Each carries `watch: military area`. The area's
`sensor.aircraft_in_range` counts them in `military_in_areas`, and per circle
in `military_by_area`. Clear the field to stop.

⚠ It shows only what broadcasts and is marked as military. Military flights
can fly with their transponder off, and a military aircraft on a civil
registration is not marked.

### Aircraft and flights you follow

Live Track Aircraft can follow aircraft you choose wherever they are in the
world, not only inside your circle: your own plane, a club's or a company's
fleet, or the flight a family member is on.

1. Open **Settings → Devices & services → Live Track Aircraft → Configure**
   on the area you want them shown with.
2. Fill in **Aircraft to follow (hex codes)**, **Flights to follow (call
   signs)**, or both.
3. Choose **Submit**. They appear within about a minute.

**One code per aircraft is enough.** Choose by what you want to follow:

| To follow | Use | Example |
|---|---|---|
| one aircraft, whatever flight it flies (your own plane, a fleet) | its **hex code** | `a1b2c3` |
| one flight, whatever aircraft flies it (a family member's trip) | its **call sign** | `UAL1234` |

Entering both codes for the same aircraft does no harm (it is drawn once) but
adds nothing.

**Typing the codes:**

* Separate codes with commas: `a1b2c3, a4b5c6, a7b8c9`. Spaces or semicolons
  between codes work too.
* A hex code is exactly six characters: the digits 0 to 9 and the letters a
  to f, in upper or lower case.
* A call sign is 2 to 8 letters and digits, typed as the aircraft broadcasts
  it, with no space or dash: `UAL1234`, not `UA 1234` or `UAL-1234`.
* Up to 100 hex codes and 100 call signs. A code typed twice counts once.
* If one code is wrong, the dialog refuses that field, says what a good code
  looks like, and saves nothing until it is fixed.

**Finding the codes.** Every aircraft on the map carries its hex code in its
`identity` attribute and its call sign in its `callsign` attribute. For an
aircraft registered in the United States, the FAA registry's N-number search
shows the hex code as "Mode S Code (Base 16 / Hex)". For an airline flight,
the call sign is usually the airline's three-letter code and the flight
number, which is not what the ticket shows:

| Ticket | Call sign |
|---|---|
| United UA 1234 | `UAL1234` |
| Delta DL 89 | `DAL89` |
| American AA 100 | `AAL100` |

Some airlines broadcast a call sign that is not the flight number. If a flight
does not appear, look it up on a live flight map and copy the call sign shown
there. A call sign is reused: the same call sign tomorrow is a different trip,
and may be a different aircraft. It stays followed until you remove it.

**What you see.** Each followed aircraft is drawn with its usual icon and
label wherever it is, even when your area is full. Its `watch` attribute reads
`followed`, and `outside_radius` says whether it is outside your circle.
Outside your circle it moves once a minute; inside it, as often as everything
else. The area's `sensor.aircraft_in_range` shows `followed_asked` (how many
codes you follow), `followed_found` (how many of them are in the air now) and
`follow_status` (the last call-sign request: `ok`, or what went wrong).

**To stop**, remove the code, or clear the field, and choose **Submit**.

⚠ Only aircraft that broadcast ADS-B, or that MLAT can locate, can be found.
An aircraft on the ground or out of receiver coverage is not shown, and
`followed_found` does not count it. Schedules and delays by flight number are
not part of this.

### Your own picture for one aircraft

Put a picture of your choosing in place of one aircraft's icon, for example
your own plane.

1. In your Home Assistant configuration folder (the folder that holds
   `configuration.yaml`), make a folder named `live_track_aircraft_pictures`.
2. Put the picture in it, named with the aircraft's hex code: `a1b2c3.png`.
   PNG, JPG, WebP, GIF and SVG files work, up to 2 MB each.

The picture appears within a minute, and so does a change or a removal. It is
drawn upright, not turned, because a photograph is not drawn nose up. The
aircraft's `picture_source` attribute then reads `override`.

These pictures need a sign-in to your Home Assistant, like the rest of it.
The map gets each one by a link that Home Assistant signs, which stops
working after a day; a new link is made before then.

### Photos

When you point at an aircraft, the map shows a photo of it from
[Planespotters.net](https://www.planespotters.net), if there is one, with the
photographer's name beside it. Click the aircraft to see the photo larger; the
photo links to its page on Planespotters.net. There is nothing to set up.

The photo is looked up only when someone points at that aircraft, not for
every aircraft in your area. Your Home Assistant asks Planespotters.net by the
aircraft's hex code. It keeps the answer, a photo or no photo, for 12 hours,
in memory only, so a restart forgets it. The browser that shows the map loads
the picture straight from Planespotters.net. Home Assistant does not download,
store or pass on any picture.

⚠ A photo shows the aircraft as the photographer saw it, perhaps in an earlier
livery or with an earlier operator. Not every aircraft has a photo on
Planespotters.net.

⚠ No photo is looked up for an aircraft that flies with a temporary address
for privacy (the Privacy ICAO Address program of the FAA, United States),
because that hex code does not identify the aircraft, or for a track without a
real hex code.

⚠ There is no option to turn photos off yet.

Each aircraft with a hex code carries `marker_photo_lookup`: the address on
your Home Assistant where the map asks for the photo. Only someone signed in
to your Home Assistant can use it. The photos are the work of their
photographers: see [Credits and licences](#credits-and-licences).

### The presidential aircraft

The aircraft used by the President of the United States are shown wherever
they are in the world, by their hex codes, never by call sign, together with
the aircraft of the 89th Airlift Wing (call signs SAM and VENUS) and the
military aircraft escorting a presidential aircraft. They come from one
request a minute that Live Track Aircraft makes anyway. Each carries a
`watch` attribute saying why it is shown, and a presidential aircraft its
name in `presidential_airframe`.

⚠ A presidential aircraft on the map says nothing about who is aboard.

### The EnforcementAircraft list, and Live Track SALT

[EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)
is a public list of aircraft used in immigration and federal law enforcement,
each entry with its sources, published by StrausbergAutomationWorks. Inside
your area, an aircraft the list confirms from its sources flashes red and
blue, and an airliner that flies ICE Air charters among other work has a
steady glow. They are always kept, even when your area is full.

Its companion, [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
draws the listed aircraft wherever they fly, not only in your area. Install
both and each keeps to its own part: Live Track Aircraft draws every aircraft
inside its own area, the listed ones included, and Live Track SALT draws the
listed aircraft everywhere else. They share one request to the sources, and no
aircraft is drawn twice.

---

## All the entities it creates

For each area:

| Entity | What it is |
|---|---|
| `sensor.aircraft_in_range` | **Aircraft in range**: how many aircraft are inside the circle now, all of them, even when more than the maximum. A second area's is `sensor.aircraft_in_range_2`, and so on |
| `geo_location.aircraft_…` | one per aircraft, named from its hex code (`geo_location.aircraft_a1b2c3`); it comes and goes with the aircraft. Each carries `source: live_track_aircraft`, and its state is its distance from the centre in kilometres |

The sensor's attributes say what is happening: `published_count` (how many are
on the map), `capped` (true when the maximum cut the list), `source` (which
network answered last), `source_backoff`, `route_artifact`, `route_download`,
`airport_table`, `airport_download`, `route_lookup`, `watched_count`,
`military_in_areas`, `military_by_area`, `followed_asked`, `followed_found`,
`follow_status`, `adsblol_key` and `enforcement_list`.

⚠ **The aircraft markers have no unique ID, on purpose.** An area sees
thousands of different aircraft in a year, and a registry row for each would
make Home Assistant slower to start for nothing. So they cannot be renamed,
hidden or given an area in the interface. Their entity IDs still come from
the hex code, so the same aircraft always gets the same ID. The sensor has a
unique ID and can be renamed.

⚠ **Your database.** Home Assistant's recorder stores a new row each time an
entity changes, and a flying aircraft changes with every update, every 15
seconds by default. On our test system, in September 2026, an entity like
these updated every 15 seconds cost about 9.6 MB a day; at 50 aircraft that
is about 480 MB a day. Unless you want the history of every aircraft, keep
them out of the recorder. Add this to `configuration.yaml`, then restart:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.aircraft_*
```

If your `configuration.yaml` already has a `recorder:` section, add only the
pattern `geo_location.aircraft_*` to it, under `exclude:` and
`entity_globs:`. A map card set to draw
history then has no trail to draw. `sensor.aircraft_in_range` is cheap to
keep: its attributes take few values, so the recorder stores them once.

---

## What it sends and downloads

**About your location.** The centre and radius of each area are sent to
adsb.fi with every update, every 15 seconds by default, and to adsb.lol when
adsb.fi does not answer. The centre is sent as you set it, and it starts at
your home: to stop sending your home, move the centre away from it
(**Configure** → **Centre**) or delete the area. The hex codes and call signs
you follow are sent to adsb.fi (or adsb.lol) once a minute, and your adsb.lol
key only to adsb.lol. The call signs of airline flights in your area are sent
to adsbdb when FiledRoutesDB has no route for them. When someone points at an
aircraft on the map, its hex code is sent to Planespotters.net, at most once
every 12 hours for each aircraft, and the browser showing the map loads the
photo from there. There is no option to stop this yet. Nothing else about you
is sent anywhere. Each service sees your internet address, as any website
does.

**How much.**

| Source | What and how often | After an error |
|---|---|---|
| adsb.fi | every aircraft in your circle, at each update (every 15 seconds by default); one request a minute for the aircraft followed by hex code and the presidential aircraft; one for the military list; one for all followed call signs together, only when you follow any | asks adsb.lol instead. A source that refuses with HTTP 429 is skipped for the time it asks, or for 1 minute doubling up to 10 minutes |
| adsb.lol | the same requests, only while adsb.fi does not answer | the same |
| adsbdb | one request per new airline call sign that FiledRoutesDB has no route for, at least 1 second apart; an answer is kept 30 days, a "no route" 24 hours. Answers are kept in memory only | not asked again for 15 minutes; all requests pause 15 minutes after HTTP 429 |
| Planespotters.net | one request for an aircraft's photo the first time someone points at it, then none for that aircraft for 12 hours. Answers are kept in memory only. The browser showing the map loads the photo itself | after HTTP 429, no photo is asked for during the time Planespotters.net asks, or for 10 minutes; after HTTP 403, for a day |
| FiledRoutesDB, from GitHub | a small checksum file once a day, after 14:00 Chicago time (United States); the file itself, about 4.6 MB, only when it has changed | tried again an hour later; the copy you have stays in use until it expires |
| AirportZones, from GitHub | a small checksum file once a day; the table itself, about 4.8 MB, only when it has changed | tried again an hour later; the copy you have stays in use |
| EnforcementAircraft, from GitHub | a small checksum file once an hour; the list itself, small, only when it has changed | the copy you have stays in use |
| FAA aircraft registry (United States) | the registry, about 73 MB, once every 7 days, from `registry.faa.gov` | tried again the next day; the copy you have stays in use |

The downloaded files are shared with other Live Track modules, so each is
downloaded once however many modules you install. They are kept in Home
Assistant's `.storage` folder under names beginning `saw_`. If you remove Live
Track Aircraft and no other Live Track module uses them, you can delete them
by hand.

---

## Help it grow

Live Track Aircraft is still growing. We add route sources, data sources and
aircraft information as we find them, and we want to know what you would like
next.

### Suggest something

Is your country, airport or aircraft type missing? Is something wrong, or
hard to understand? Tell us whichever way is easier for you:

* [**Fill in a short form**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=en.yml)
  in English. You need a free GitHub account.
* **Write an email** to
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  No account needed.

Either way, it helps to tell us:

* what you would like to see, and where in the world;
* a link to where the data is published, if you know one (an open-data page,
  a public feed, a service's website): not needed, but it helps;
* your Home Assistant language, if the problem is the wording or a
  translation.

Write in English or in your own language, whichever is easier for you.

### Add it yourself, with our help

If you would like to add something yourself, we will help you do it, from
the first question to the finished release. You do not need to be a
developer to start:

* **A translation.** The words in the setup dialog are a short list of
  phrases in one text file. We will show you which file and which lines.
* **A new source.** Tell us where the data is published. We can write the
  code together, or look over yours.
* **Testing where you live.** Install it, look at your part of the map, and
  tell us what is right and what is not.
* **A fix to this README.** If a step did not match what you saw, tell us
  what you saw.

[**Tell us what you have in mind**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=en.yml)
or write to
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
and we will reply with the next steps.

---

## Languages

This README: **English**, [Deutsch](README.de.md), [Français](README.fr.md),
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md).
Each translated README is complete.

The setup dialog and the options are in English only for now, whatever your Home
Assistant language. If you speak another language, you can translate them
yourself: it is a short list of phrases in one file, and [we will help you do
it](#add-it-yourself-with-our-help).

Found a mistake in a translation, or need another language? Tell us at
<https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues>, or
[translate it with our help](#add-it-yourself-with-our-help).

---

## Credits and licences

* **adsb.fi** (<https://adsb.fi>): aircraft positions, open data for personal,
  non-commercial use only, under the terms in its
  [open data README](https://github.com/adsbfi/opendata), which ask to cite
  adsb.fi and link to its home page. By installing this integration you use
  adsb.fi, and its terms apply to you.
* **adsb.lol** (<https://adsb.lol>): aircraft positions, under the
  [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/).
  By installing this integration you use adsb.lol, and its terms apply to you.
  Both networks are run by volunteers: if you can, support them by feeding a
  receiver.
* **FiledRoutesDB** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/FiledRoutesDB)):
  routes from flight plans filed with the FAA (United States), data under
  CC BY 4.0, with the FAA's LADD list applied before publication.
* **adsbdb** (<https://www.adsbdb.com>): routes outside FiledRoutesDB. Its
  route data is the work of David Taylor (Edinburgh) and Jim Mason (Glasgow),
  and may not be copied or republished without permission, so answers are
  kept in memory only, never written to a file, and every aircraft showing an
  adsbdb route credits them.
* **The FAA aircraft registry** (Federal Aviation Administration, United
  States): owner and operator names of aircraft registered in the United
  States, public data of the United States government. The FAA itself leaves
  out the names it is asked to withhold before it publishes the file.
* **OurAirports** (<https://ourairports.com>), by way of
  [AirportZones](https://github.com/StrausbergAutomationWorks/AirportZones):
  airport names and positions, under the ODbL 1.0; time zones added by
  StrausbergAutomationWorks.
* **EnforcementAircraft** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)):
  the list of immigration and federal law-enforcement aircraft, under the
  ODbL 1.0.
* **ADS-B Radar** (<https://adsb-radar.com>): the aircraft icons, from its
  [SVG aircraft icon set](https://adsb-radar.com/help/icons.html) by Jos
  Nutbroek, used under its terms, which ask for this backlink. The icons are
  not covered by this repository's MIT licence. Some icons were drawn by
  StrausbergAutomationWorks in the style of the set and donated to ADS-B
  Radar, so they are under its terms too. This integration serves the icons
  with a new fill and outline, scaled by aircraft class, and animates some
  propellers and rotors. Every change is listed in
  [ATTRIBUTION.md](ATTRIBUTION.md).
* **Planespotters.net** (<https://www.planespotters.net>): the aircraft
  photos, through its [photo API](https://www.planespotters.net/photo/api) and
  under its terms. Each photo is the work of its photographer, who is named
  beside it, and links to its page on Planespotters.net. No photo is copied
  into this repository, and Home Assistant does not download, store or pass on
  any picture. By installing this integration you use Planespotters.net, and
  its terms apply to you.
* **The map card** is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, a copy of [ha-map-card](https://github.com/nathan-gs/ha-map-card) by
  nathan-gs, MIT. Its map tiles and their credits are in its README.

None of these organisations made or endorsed this integration.

**Code**: MIT, in [LICENSE](LICENSE).

**For developers:** the entities follow the shared Live Track map contract,
so every module renders on one map without template sensors; positions come
through a source seam in `custom_components/live_track_aircraft/sources/`, so
another feed can be added without touching the entities. The tests run with
`python -m unittest discover -s tests`.

---

## Keywords

Home Assistant aircraft · Home Assistant flight tracker · ADS-B · ADS-B map ·
flight tracking · aircraft tracker · planes overhead · MLAT · Mode S ·
flight routes · military aircraft · Air Force One · helicopters ·
Flugzeuge · Flugverfolgung · avions · suivi des vols · vliegtuigen ·
vluchten volgen · 飞机 · 航班跟踪 · aviones · seguimiento de vuelos ·
aerei · tracciamento voli · fly · flysporing · adsb.fi · adsb.lol · adsbdb ·
FiledRoutesDB · FAA registry · OurAirports · ADS-B Radar · Planespotters.net ·
aircraft photos · geo_location · map card · Lovelace · HACS · Marketplace ·
Live Track · LiveTrack · StrausbergAutomationWorks

---

**Acknowledgement.** StrausbergAutomationWorks acknowledges the Indigenous
peoples of every land and water on this map, all over the world, and pays its
respect to their Elders, past and present.
