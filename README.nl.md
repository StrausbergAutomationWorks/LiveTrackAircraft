# Live Track Aircraft

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · **Nederlands** · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Alle talen](#talen)

**Vliegtuigen voor Home Assistant, op één kaart.** Live Track Aircraft zet de
vliegtuigen boven je huis, of boven elke plek op de wereld die je kiest, op je
Home Assistant-kaart: elk getekend als zijn eigen type, gedraaid in de
richting waarin het vliegt, met wie het gebruikt en, als het bekend is, waar
het naartoe gaat. Het kan ook gekozen vliegtuigen en vluchten volgen, waar ze
ook zijn, en uitkijken naar militaire vliegtuigen in gebieden die je opgeeft.

> **Live Track Aircraft is één module van Live Track**, een familie Home
> Assistant-integraties die alles wat beweegt, en het weer waar het doorheen
> beweegt, op één gedeelde kaart tekenen: vliegtuigen, schepen, treinen en
> weer. Installeer het alleen, of naast de andere modules
> ([lijst hieronder](#onderdeel-van-live-track-de-andere-modules)).

> **Het groeit, en ideeën zijn welkom.** Live Track Aircraft dekt vandaag de
> hele wereld waar vrijwilligers ontvangers draaien, met routes en eigenaren
> het meest gedetailleerd voor de Verenigde Staten, en we voegen meer
> routebronnen en vliegtuiggegevens toe. Ontbreekt de jouwe?
> [Stel het voor](#help-het-groeien), of voeg het zelf toe: we helpen je
> daarbij.

**Status: 0.1.6, uitgebracht.** In de catalogus van de Marktplaats ([installeer
het hieronder](#installeren-stap-voor-stap)).

Eigen werk van StrausbergAutomationWorks. Niet verbonden met, en niet
gesteund door, adsb.fi, adsb.lol, adsbdb, de Federal Aviation Administration
(Verenigde Staten), OurAirports, ADS-B Radar, Planespotters.net, een
luchtvaartmaatschappij of een gebruiker van vliegtuigen.

> ⚠ **Geen veiligheidssysteem.** Het toont openbare gegevens, meestal
> seconden oud en soms een minuut of langer, en alleen vliegtuigen die de
> ontvangers van vrijwilligers toevallig horen. Het is niet bedoeld voor
> navigatie, voor het gescheiden houden van vliegtuigen, of voor enig ander
> operationeel doel.

---

## Inhoud

1. [Alles wat het doet](#alles-wat-het-doet)
2. [Waar het werkt](#waar-het-werkt)
3. [Onderdeel van Live Track: de andere modules](#onderdeel-van-live-track-de-andere-modules)
4. [Voordat je begint](#voordat-je-begint)
5. [Installeren, stap voor stap](#installeren-stap-voor-stap)
6. [Instellen, stap voor stap](#instellen-stap-voor-stap)
7. [Gratis sleutels die meer inschakelen, stap voor stap](#gratis-sleutels-die-meer-inschakelen-stap-voor-stap)
8. [De kaart op een dashboard zetten](#de-kaart-op-een-dashboard-zetten)
9. [Gebruiken in automatiseringen](#gebruiken-in-automatiseringen)
10. [Alles op de kaart, in detail](#alles-op-de-kaart-in-detail)
11. [Alle entiteiten die het aanmaakt](#alle-entiteiten-die-het-aanmaakt)
12. [Wat het verstuurt en downloadt](#wat-het-verstuurt-en-downloadt)
13. [Help het groeien](#help-het-groeien)
14. [Talen](#talen)
15. [Bronvermelding en licenties](#bronvermelding-en-licenties)
16. [Trefwoorden](#trefwoorden)

---

## Alles wat het doet

### Op de kaart, zonder iets in te stellen

Je voegt een **gebied** toe: een middelpunt op de kaart en een straal
eromheen. Het begint bij je huis. Alles hieronder verschijnt dan in dat
gebied, of, waar de tabel het zegt, overal ter wereld.

| Wat | Waar | Bron |
|---|---|---|
| **Vliegtuigen**: verkeersvliegtuigen, kleine vliegtuigen, helikopters, zweefvliegtuigen, ballonnen en drones, elk getekend als zijn eigen type en gedraaid in de richting waarin het vliegt | in elk gebied | adsb.fi, of adsb.lol als adsb.fi niet antwoordt |
| **Wie het gebruikt**: de luchtvaartmaatschappij, de eigenaar, of het type als er niets anders bekend is, op het label van de markering | elk vliegtuig | de roepnaam van de luchtvaartmaatschappij; het luchtvaartuigregister van de FAA (Verenigde Staten) voor eigenaren |
| **Kleuren die zeggen wie er vliegt**: overheid, politie, federale ordediensten, het leger, ambulancevliegtuigen en helikopters, elk in een eigen kleur | elk vliegtuig waar het bekend is | het luchtvaartuigregister van de FAA (Verenigde Staten) en de militaire markering van de feed |
| **Routes**: waar het vliegtuig is opgestegen en waar het naartoe gaat, met de namen van de luchthavens en een geschatte aankomsttijd | vluchten met een vliegplan ingediend bij de FAA (Verenigde Staten); elders als adsbdb de vlucht kent | FiledRoutesDB, dan adsbdb |
| **De vliegtuigen van de president van de Verenigde Staten**, met de vliegtuigen van de 89th Airlift Wing en de militaire vliegtuigen die ze begeleiden | overal ter wereld | adsb.fi en zijn militaire lijst |
| **Vliegtuigen op de openbare EnforcementAircraft-lijst** (immigratie en federale ordediensten), met knipperende lichten | in elk gebied | de EnforcementAircraft-lijst |
| **Militaire vliegtuigen in je bewakingsgebieden**: elk vliegtuig dat de feed als militair markeert, binnen tot tien cirkels die je opgeeft, ook als je gebied vol is. Optioneel: je typt de cirkels in de instellingsdialoog | overal ter wereld | de militaire lijst van adsb.fi |
| **Vliegtuigen en vluchten die je volgt**: je eigen vliegtuig, de vloot van een club, of de vlucht van een familielid. Optioneel: je typt hun codes in de instellingsdialoog | overal ter wereld | adsb.fi |
| **Foto's**: een foto van het vliegtuig, met de naam van de fotograaf, als je het aanwijst | elk vliegtuig waarvan Planespotters.net een foto heeft | Planespotters.net ([meer](#fotos)) |
| **Je eigen afbeelding voor één vliegtuig**, in plaats van zijn symbool | overal waar dat vliegtuig getoond wordt | een afbeelding die je in een map zet ([hoe](#je-eigen-afbeelding-voor-één-vliegtuig)) |

### Ingeschakeld met je eigen gratis sleutel of account

| Gratis sleutel of account | Wat het toevoegt |
|---|---|
| **adsb.lol**-sleutel | meer verzoeken per dag aan adsb.lol, de tweede bron, zodat de kaart blijft werken tijdens een lange storing van adsb.fi |

Elk ervan heb je in een paar minuten: [stap voor stap hieronder](#gratis-sleutels-die-meer-inschakelen-stap-voor-stap).

---

## Waar het werkt

| Regio | Wat je krijgt | Bron | Nodig |
|---|---|---|---|
| **De hele wereld** | posities van vliegtuigen waar vrijwilligers ontvangers draaien: dicht boven Europa en Noord-Amerika, dunner elders, en weinig of niets ver op zee | adsb.fi, adsb.lol | niets |
| **De hele wereld** | de namen van luchthavens op routes, en hun tijdzones voor de aankomsttijd | OurAirports, via de tabel AirportZones | niets |
| **De hele wereld** | routes van veel lijnvluchten, gecontroleerd tegen waar het vliegtuig werkelijk is | adsbdb | niets |
| **Noord-Amerika**: Verenigde Staten | namen van eigenaren en gebruikers van in de Verenigde Staten geregistreerde vliegtuigen, en de kleuren voor overheids- en politievliegtuigen | het luchtvaartuigregister van de FAA | niets |
| **Noord-Amerika**: Verenigde Staten | routes van vluchten die bij de FAA zijn ingediend, ook internationale vluchten van en naar de Verenigde Staten | FiledRoutesDB | niets |

Niet op de lijst? [Laat het ons weten](#help-het-groeien). Waar iemand de
gegevens openlijk publiceert, kijken we of we ze kunnen toevoegen.

⚠ **De dekking is goed waar ontvangers zijn, en afwezig waar ze niet zijn.**
Een vliegtuig verschijnt alleen als de ontvanger van een vrijwilliger het
hoort, of als meerdere ontvangers samen het kunnen lokaliseren. Geen enkele
instelling kan dekking maken die er niet is. **Een lege lucht op de kaart kan
betekenen dat er geen ontvangers bij je in de buurt zijn, niet dat er geen
vliegtuigen zijn.**

⚠ **Routes zijn er vooral voor de Verenigde Staten.** FiledRoutesDB bevat
alleen vliegplannen die bij de FAA zijn ingediend. Elders komt een route van
adsbdb, dat veel lijnvluchten kent en weinig andere, dus buiten de Verenigde
Staten tonen veel vliegtuigen geen route.

⚠ **Namen van eigenaren zijn er alleen voor in de Verenigde Staten
geregistreerde vliegtuigen.** Een vliegtuig dat in een ander land is
geregistreerd, toont zijn luchtvaartmaatschappij uit zijn roepnaam, of zijn
type.

---

## Onderdeel van Live Track: de andere modules

Live Track is een reeks Home Assistant-integraties, één per soort bewegend
ding, allemaal getekend op dezelfde kaart. Elke werkt op zichzelf; samen
vormen ze één live beeld. Ze delen de kaart en een Python-bibliotheek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
dus een extra module installeren voegt geen verzoeken toe aan een bron die een
andere al leest.

| Module | Wat het op de kaart zet | Status |
|---|---|---|
| **Live Track Aircraft** | vliegtuigen boven je via ADS-B, met routes en typesymbolen (deze module) | uitgebracht |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | schepen en boten via AIS, bij jou in de buurt of overal | uitgebracht |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | forensentreinen in Noord-Amerika, Europa en Australië | uitgebracht |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | intercity- en langeafstandstreinen in Noord-Amerika, Europa en Australië | uitgebracht |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | vliegtuigen en schepen van immigratie- en federale ordediensten, uit openbare lijsten | uitgebracht |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | weer, stormen en natuurgevaren | uitgebracht |
| Live Track Stations | vertrekborden en "tijd om te gaan"-meldingen voor elk station | gepland |
| Live Track Satellites | satellieten die over je heen trekken | gepland |
| Live Track Freight Trains | goederen- en werktreinen waar spoorwegen ze publiceren | gepland |
| Live Track Transit | stadsbussen, trams, veerboten en metro | gepland |
| Live Track Intercity Buses | intercity- en streekbussen | gepland |
| Live Track Commuter Buses | forensenbussen | gepland |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | de gedeelde kaart waarop elke module tekent | uitgebracht, met elke module geïnstalleerd |

Alles is gratis en open source. Niets wordt achtergehouden voor sponsors.

---

## Voordat je begint

* **Home Assistant** 2026.11 of nieuwer.
* **De Marktplaats** (HACS) in je Home Assistant, om het op de makkelijke
  manier te installeren en bij te werken. Zonder kun je de bestanden met de
  hand kopiëren.
* **Internettoegang** voor Home Assistant: alles komt uit openbare bronnen.
* Niets te betalen en geen account nodig. De adsb.lol-sleutel hierboven is
  optioneel.
* Home Assistant installeert zelf de twee Python-pakketten die het nodig heeft
  (`saw-livetrack` en `tzfpy`) wanneer de integratie de eerste keer laadt.

---

## Installeren, stap voor stap

### Via de Marktplaats (aanbevolen)

1. Open in Home Assistant **Instellingen → Marktplaats** (HACS).
2. Zoek **Live Track Aircraft** en open het.
3. Kies **Download** (of **Installeren**).
4. **Herstart Home Assistant**: **Instellingen → Systeem → Reparaties** biedt
   de herstart aan, of gebruik **Instellingen → Systeem → Herstart**.

Vindt de zoekfunctie het niet, voeg het dan toe via de koppeling: kies **Via
koppeling toevoegen** (of het menu met drie puntjes → **Aangepaste
repositories**), voer `StrausbergAutomationWorks/LiveTrackAircraft` in, kies
**Integration** als om het type wordt gevraagd en ga daarna verder bij stap 3.

De Marktplaats biedt daarna elke nieuwe release als update aan.

### Met de hand

1. Download de broncode van de
   [nieuwste release](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/releases/latest).
2. Kopieer de map `custom_components/live_track_aircraft` daaruit naar de map
   `custom_components` van je Home Assistant-configuratiemap (maak
   `custom_components` aan als die er niet is).
3. Herstart Home Assistant.

Om met de hand bij te werken, vervang je de map door die van de nieuwe release
en herstart je.

---

## Instellen, stap voor stap

De instellingsdialoog is in het Engels. Zijn velden staan hier zoals hij ze
toont.

1. Open **Instellingen → Apparaten en diensten**.
2. Kies **Voeg integratie toe** (rechtsonder) en zoek naar **Live Track
   Aircraft**.
3. **Centre** (middelpunt): sleep de markering naar het midden van de lucht
   die je wilt bekijken. Hij begint bij je huis.
4. **Radius (km)** (straal): hoe ver van het middelpunt vliegtuigen getoond
   worden, van 1 tot 463 km (0,6 tot 288 mijl). Twijfel je, houd dan 56 km
   (35 mijl).
5. **Update interval (seconds)** (bijwerkinterval): houd 15. De bronnen
   weigeren vaker gedane verzoeken.
6. **Maximum aircraft published** (maximaal aantal gepubliceerde vliegtuigen):
   houd 250. Het is een veiligheidsgrens, geen manier om minder vliegtuigen te
   tonen.
7. Laat de vier optionele velden voorlopig leeg. Elk wordt hieronder
   uitgelegd.
8. Kies **Verzend**.

Dat is alles. Vliegtuigen verschijnen binnen een minuut. Elk gebied is één
item, met als titel zijn middelpunt en straal, bijvoorbeeld
`39.817, -84.050 - 56 km`. Om een tweede gebied te bekijken, voeg je de
integratie opnieuw toe met een ander middelpunt of een andere straal. Hetzelfde
middelpunt en dezelfde straal twee keer wordt geweigerd.

Routes, luchthavennamen en eigenaren vullen zich in de eerste minuten, terwijl
de bestanden waar ze vandaan komen worden gedownload
([Wat het verstuurt en downloadt](#wat-het-verstuurt-en-downloadt)).

### Wijzigen wat het toont: de opties

Open **Instellingen → Apparaten en diensten → Live Track Aircraft →
Configureer** (het tandwiel) bij het gebied dat je wilt wijzigen. Elke optie,
in gewone woorden:

| Optie | Wat het doet | Standaard |
|---|---|---|
| **Centre** | verplaatst het gebied; zijn titel volgt | je huis |
| **Radius (km)** | hoe ver van het middelpunt vliegtuigen getoond worden, 1 tot 463 km (0,6 tot 288 mijl) | 56 km (35 mijl) |
| **Update interval (seconds)** | hoe vaak posities worden opgevraagd, 15 tot 3.600 seconden | 15 |
| **Maximum aircraft published** | een veiligheidsgrens, 1 tot 1.000; zijn er meer vliegtuigen in de cirkel, dan worden de dichtstbijzijnde gehouden. Vliegtuigen die je volgt, vliegtuigen in je militaire bewakingsgebieden en vliegtuigen op de EnforcementAircraft-lijst worden altijd gehouden | 250 |
| **Military watch areas** | cirkels waarin elk militair vliegtuig getoond wordt ([hoe](#militaire-bewakingsgebieden)) | leeg |
| **Aircraft to follow (hex codes)** | vliegtuigen die overal gevolgd worden, op hun hexcode ([hoe](#vliegtuigen-en-vluchten-die-je-volgt)) | leeg |
| **Flights to follow (call signs)** | vluchten die overal gevolgd worden, op hun roepnaam (dezelfde sectie) | leeg |
| **adsb.lol API key** | je eigen sleutel voor adsb.lol ([hoe je er een krijgt](#gratis-sleutels-die-meer-inschakelen-stap-voor-stap)) | leeg |

Maak een van de vier optionele velden leeg om dat deel uit te schakelen.

---

## Gratis sleutels die meer inschakelen, stap voor stap

Ze zijn allemaal gratis en persoonlijk: elke persoon die Live Track Aircraft
installeert, krijgt een eigen sleutel. Plak elke sleutel in **Instellingen →
Apparaten en diensten → Live Track Aircraft → Configureer**.

### adsb.lol (meer verzoeken aan de tweede bron, de hele wereld)

Live Track Aircraft vraagt eerst adsb.fi, en vraagt adsb.lol alleen zolang
adsb.fi niet antwoordt. Zonder sleutel staat adsb.lol 500 verzoeken per dag
toe vanaf één internetadres, die een storing van adsb.fi in ongeveer twee uur
kan opmaken. Een sleutel verhoogt die grens. Om te beginnen heb je er geen
nodig.

1. Open <https://www.adsb.lol/request> en vraag met het formulier daar een
   gratis sleutel aan. De documentatie van adsb.lol geeft deze sleutel 1.000
   verzoeken per dag.
2. Voed je adsb.lol met een eigen ontvanger, gebruik dan je feedersleutel: de
   documentatie van adsb.lol geeft die 7.200 verzoeken per dag. Je sleutels
   staan onder **My keys** op adsb.lol (<https://www.adsb.lol/mmb>).
3. Plak de sleutel in **adsb.lol API key**, en kies **Verzend**.

De sleutel wordt alleen naar adsb.lol gestuurd. Weigert adsb.lol hem (fout of
verlopen), dan werkt Live Track Aircraft zonder hem verder, en toont
`sensor.aircraft_in_range` van het gebied `refused` in zijn attribuut
`adsblol_key` tot je de sleutel wijzigt. Anders toont het `set`, of `none`
zonder sleutel. Geen wachtwoord en geen geheim nodig.

---

## De kaart op een dashboard zetten

De kaart is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
de kaart waarop elke Live Track-module tekent. **Hij wordt met Live Track
Aircraft geïnstalleerd**: niets te downloaden, niets te kopiëren, geen bron
toe te voegen.

1. Open een dashboard, kies het potlood (**Wijzig dashboard**), dan **Voeg
   kaart toe**.
2. Scrol naar beneden en kies **Handmatig**.
3. Plak dit, en kies **Bewaar**:

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

Andere Live Track-modules gaan op dezelfde manier in `entity_filter`: nog een
regel `- domain: geo_location` voor elke bron.

**Op de kaart:**

* Elk vliegtuig is getekend als zijn eigen type, gedraaid in de richting
  waarin het vliegt, en beweegt soepel tussen de posities die het doorgeeft.
* Het label is de roepnaam van de vlucht (`UAL308`), anders wie het gebruikt
  (`Lewis University`), anders het type (`Cessna 172 Skyhawk`).
* **Wijs** een vliegtuig aan om zijn luchtvaartmaatschappij of gebruiker te
  zien, zijn foto als die er is en, als een route bekend is, de route en over
  hoeveel minuten het aankomt. **Klik** erop voor alle details en een grotere
  foto, gekoppeld aan zijn pagina op Planespotters.net ([Foto's](#fotos)).

Zijn de bronnen van je dashboards in YAML ingesteld
(`lovelace: resource_mode: yaml`), dan kan er niets voor je worden
geregistreerd: een melding onder **Reparaties** geeft dan de precieze regel om
toe te voegen. Een kaart die je zelf via de Marktplaats hebt geïnstalleerd,
blijft ongemoeid. Worden de bestanden van de integratie verwijderd terwijl de
gebieden nog zijn ingesteld, en is er geen andere Live Track-module
geïnstalleerd, verwijder dan zelf de regel van de kaart in **Instellingen →
Dashboards → Bronnen**. Elke andere kaart die `geo_location`-entiteiten
toont, toont de vliegtuigen ook, als gewone markeringen.

---

## Gebruiken in automatiseringen

Alles is een gewone Home Assistant-entiteit, dus de automatiseringseditor
werkt ermee, zonder code.

**Een melding op je telefoon als er een militair vliegtuig in een van je
militaire bewakingsgebieden is:**

1. **Instellingen → Automatiseringen en scènes → Maak automatisering aan →
   Voeg automatisering toe**.
2. **Wanneer**: **Voeg trigger toe** → **Entiteit** → **Numerieke status**.
   Kies de entiteit **Aircraft in range**, het **Attribuut** **Military in
   areas** (`military_in_areas`), en **Boven** `0`.
3. **Doe dan**: **Voeg actie toe**, zoek de meldingsactie van je telefoon (die
   draagt de naam van je telefoon), en voer een bericht in, bijvoorbeeld:

   ```text
   Er is een militair vliegtuig in je bewakingsgebied
   ```

4. **Bewaar**.

Hiervoor heb je minstens één militair bewakingsgebied nodig
([hoe](#militaire-bewakingsgebieden)).

**Andere ideeën:** een melding als de vlucht van een familielid in de lucht
is, als het attribuut `followed_found` boven 0 komt; een lamp die aangaat als
er meer dan 20 vliegtuigen boven je huis in Frankfurt (Duitsland) zijn; een
teller op het dashboard van de vliegtuigen boven je vliegveld in Queensland
(Australië), uit `sensor.aircraft_in_range`; een bericht als het vliegtuig
van je club opstijgt, als zijn eigen entiteit (`geo_location.aircraft_` en
zijn hexcode) verschijnt.

---

## Alles op de kaart, in detail

### Vliegtuigen

Vliegtuigen zenden hun positie per radio uit, een systeem dat ADS-B heet.
Vrijwilligers over de hele wereld draaien ontvangers en delen wat ze horen via
gemeenschapsnetwerken. Live Track Aircraft vraagt een daarvan, adsb.fi, om
elk vliegtuig in je cirkel, standaard elke 15 seconden. Als adsb.fi niet
antwoordt, of met veel minder vliegtuigen dan een moment eerder, vraagt het
adsb.lol. Waar meerdere ontvangers een vliegtuig horen dat zijn eigen positie
niet uitzendt, kunnen de netwerken het toch lokaliseren (multilateratie,
MLAT).

Elk vliegtuig is één markering, genoemd naar zijn hexcode: het adres van zes
tekens dat zijn transponder uitzendt, dat bij het vliegtuig hoort en niet
verandert. De markering verschijnt als het vliegtuig je cirkel binnenkomt en
wordt verwijderd als het die verlaat.

Het label is de nuttigste naam die bekend is, in deze volgorde:

| Het vliegtuig heeft | Het label toont | Voorbeeld |
|---|---|---|
| de roepnaam van een vlucht | de roepnaam | `UAL308` |
| anders een bekende gebruiker | de gebruiker | `Lewis University` |
| anders een bekend type | het type | `Cessna 172 Skyhawk` |
| geen van deze | de registratie, de typecode of de hexcode | `N12345` |

⚠ Niet getoond: vliegtuigen op de grond, voertuigen op luchthavens, en alleen
radarsporen zonder identiteit. Een vliegtuig dat niet uitzendt, of vliegt waar
geen ontvanger het hoort, kan niet getoond worden.

Op elk vliegtuig: `identity` (de hexcode), `callsign`, `registration`,
`aircraft_type`, `aircraft_name`, `operator`, `altitude_m`, `speed_kmh`,
`vertical_rate_ms`, `course_deg`, `squawk`, `emitter_category`,
`is_military`, `is_government`, `last_seen`.

### Kleuren en symbolen

Elk vliegtuig is getekend als zijn eigen type: een verkeersvliegtuig, een
zakenjet, een kleine eenmotorige, een tweemotorige, een helikopter, een
kantelrotorvliegtuig, een zweefvliegtuig, een ballon, een drone en nog veel
meer, op grootte naar zijn klasse. Propellers en rotoren draaien. Het symbool
is gedraaid in de richting waarin het vliegtuig vliegt; een langzaam
vliegtuig houdt zijn laatste richting in plaats van rond te draaien.

De kleur zegt wie er vliegt, waar dat bekend is:

| Kleur | Wie |
|---|---|
| lichtgrijs | de meeste vliegtuigen |
| mintgroen | helikopters en andere wentelwiekvliegtuigen |
| amber | overheidsvliegtuigen en ambulancevliegtuigen |
| blauw | federale ordediensten |
| legergroen | het leger en de kustwacht |
| wit, met knipperende blauwe lichten | politie |
| knipperende rode en blauwe lichten | vliegtuigen op de EnforcementAircraft-lijst ([hieronder](#de-enforcementaircraft-lijst-en-live-track-salt)) |
| een constante gloed | een verkeersvliegtuig dat onder meer chartervluchten voor ICE Air vliegt |

⚠ Van wie een vliegtuig is, is vooral bekend voor in de Verenigde Staten
geregistreerde vliegtuigen, uit het register van de FAA. Elders komt de kleur
alleen uit de militaire markering van de feed en het type van het vliegtuig.

### Routes en aankomsttijden

Een route toont waar het vliegtuig is opgestegen en waar het naartoe gaat,
met de namen van beide luchthavens, en een geschatte aankomsttijd. Hij komt
van twee plaatsen:

1. **FiledRoutesDB**, een openbaar bestand van vliegplannen die bij de FAA
   (Verenigde Staten) zijn ingediend, gemaakt en gepubliceerd door
   StrausbergAutomationWorks en één keer per dag gedownload. Elke route wordt
   gecontroleerd tegen waar het vliegtuig is en de richting waarin het vliegt.
   Een route die niet past, wordt toch getoond, en in `route_check` als niet
   passend gemarkeerd.
2. **adsbdb**, alleen gevraagd als FiledRoutesDB geen route voor de roepnaam
   heeft, één keer per roepnaam. Zijn antwoord wordt alleen getoond als het
   past bij waar het vliegtuig werkelijk is.

Vliegtuigen waarvan de eigenaren de FAA hebben gevraagd hun vluchten niet
openbaar te tonen (de LADD-lijst van de FAA, Limiting Aircraft Data
Displayed), worden uit FiledRoutesDB verwijderd voordat het wordt
gepubliceerd. Live Track Aircraft verwijdert zijn kopie als het bestand
verloopt, of als de LADD-lijst waarmee het is gemaakt ouder is dan 14 dagen,
zodat het nooit routes toont die met een oude lijst zijn gefilterd.

De aankomsttijd is een schatting, geen dienstregeling: de resterende afstand
in een rechte lijn, bij de snelheid van het vliegtuig als het op kruissnelheid
is, en anders bij een typische snelheid voor zijn klasse. Wachtpatronen, de
nadering en het taxiën worden niet meegeteld.

Op elk vliegtuig met een route: `origin_icao`, `destination_icao`,
`origin_name`, `destination_name`, `route_source`, `route_check`,
`arrival_estimated_at`.

### Militaire bewakingsgebieden

Elk vliegtuig dat de feed als militair markeert, binnen cirkels die je kiest,
overal ter wereld, ook als je gebied vol is.

1. Open **Instellingen → Apparaten en diensten → Live Track Aircraft →
   Configureer** bij een gebied.
2. Typ in **Military watch areas** elke cirkel als `latitude,longitude,km`
   (breedte, lengte, kilometers), en scheid cirkels met puntkomma's,
   bijvoorbeeld `39.81,-84.04,150; 34.0,-117.8,463`. Tot tien cirkels, elk
   van 1 tot 2.000 km (0,6 tot 1.243 mijl). Schrijf decimalen met een punt.
3. Kies **Verzend**.

De militaire vliegtuigen erin verschijnen binnen een minuut en bewegen één
keer per minuut. Elk draagt `watch: military area`.
`sensor.aircraft_in_range` van het gebied telt ze in `military_in_areas`, en
per cirkel in `military_by_area`. Maak het veld leeg om te stoppen.

⚠ Het toont alleen wat uitzendt en als militair gemarkeerd is. Militaire
vluchten kunnen met de transponder uit vliegen, en een militair vliegtuig met
een burgerregistratie is niet gemarkeerd.

### Vliegtuigen en vluchten die je volgt

Live Track Aircraft kan vliegtuigen die je kiest volgen, waar ze ook zijn op
de wereld, niet alleen in je cirkel: je eigen vliegtuig, de vloot van een club
of een bedrijf, of de vlucht van een familielid.

1. Open **Instellingen → Apparaten en diensten → Live Track Aircraft →
   Configureer** bij het gebied waarbij je ze wilt zien.
2. Vul **Aircraft to follow (hex codes)**, **Flights to follow (call signs)**
   of beide in.
3. Kies **Verzend**. Ze verschijnen binnen ongeveer een minuut.

**Eén code per vliegtuig is genoeg.** Kies op basis van wat je wilt volgen:

| Om te volgen | Gebruik | Voorbeeld |
|---|---|---|
| één vliegtuig, welke vlucht het ook vliegt (je eigen vliegtuig, een vloot) | zijn **hexcode** | `a1b2c3` |
| één vlucht, welk vliegtuig hem ook vliegt (de reis van een familielid) | zijn **roepnaam** | `UAL1234` |

Beide codes voor hetzelfde vliegtuig invoeren kan geen kwaad (het wordt één
keer getekend) maar voegt niets toe.

**De codes typen:**

* Scheid codes met komma's: `a1b2c3, a4b5c6, a7b8c9`. Spaties of puntkomma's
  tussen codes werken ook.
* Een hexcode is precies zes tekens: de cijfers 0 tot 9 en de letters a tot
  f, in hoofd- of kleine letters.
* Een roepnaam is 2 tot 8 letters en cijfers, getypt zoals het vliegtuig hem
  uitzendt, zonder spatie of streepje: `UAL1234`, niet `UA 1234` of
  `UAL-1234`.
* Tot 100 hexcodes en 100 roepnamen. Een code die twee keer is getypt, telt
  één keer.
* Is één code fout, dan weigert de dialoog dat veld, zegt hoe een goede code
  eruitziet, en bewaart niets tot hij verbeterd is.

**De codes vinden.** Elk vliegtuig op de kaart draagt zijn hexcode in het
attribuut `identity` en zijn roepnaam in het attribuut `callsign`. Voor een in
de Verenigde Staten geregistreerd vliegtuig toont de N-nummerzoekfunctie van
het FAA-register de hexcode als "Mode S Code (Base 16 / Hex)". Voor een
lijnvlucht is de roepnaam meestal de code van drie letters van de
luchtvaartmaatschappij en het vluchtnummer, wat niet op het ticket staat:

| Ticket | Roepnaam |
|---|---|
| United UA 1234 | `UAL1234` |
| Delta DL 89 | `DAL89` |
| American AA 100 | `AAL100` |

Sommige luchtvaartmaatschappijen zenden een roepnaam uit die niet het
vluchtnummer is. Verschijnt een vlucht niet, zoek hem dan op een live
vluchtkaart op en kopieer de roepnaam die daar staat. Een roepnaam wordt
hergebruikt: dezelfde roepnaam morgen is een andere reis, en misschien een
ander vliegtuig. Hij blijft gevolgd tot je hem verwijdert.

**Wat je ziet.** Elk gevolgd vliegtuig wordt getekend met zijn gewone symbool
en label, waar het ook is, ook als je gebied vol is. Zijn attribuut `watch`
is `followed`, en `outside_radius` zegt of het buiten je cirkel is. Buiten je
cirkel beweegt het één keer per minuut; erbinnen zo vaak als al het andere.
`sensor.aircraft_in_range` van het gebied toont `followed_asked` (hoeveel
codes je volgt), `followed_found` (hoeveel daarvan nu in de lucht zijn) en
`follow_status` (het laatste roepnaamverzoek: `ok`, of wat er misging).

**Om te stoppen** verwijder je de code, of maak je het veld leeg, en kies je
**Verzend**.

⚠ Alleen vliegtuigen die ADS-B uitzenden, of die MLAT kan lokaliseren, kunnen
gevonden worden. Een vliegtuig op de grond of buiten het bereik van ontvangers
wordt niet getoond, en `followed_found` telt het niet. Dienstregelingen en
vertragingen per vluchtnummer horen hier niet bij.

### Je eigen afbeelding voor één vliegtuig

Zet een afbeelding naar keuze in plaats van het symbool van één vliegtuig,
bijvoorbeeld je eigen vliegtuig.

1. Maak in je Home Assistant-configuratiemap (de map met
   `configuration.yaml`) een map met de naam `live_track_aircraft_pictures`.
2. Zet de afbeelding erin, genoemd naar de hexcode van het vliegtuig:
   `a1b2c3.png`. PNG-, JPG-, WebP-, GIF- en SVG-bestanden werken, tot 2 MB
   per stuk.

De afbeelding verschijnt binnen een minuut, net als een wijziging of een
verwijdering. Hij wordt rechtop getekend, niet gedraaid, omdat een foto niet
met de neus omhoog getekend is. Het attribuut `picture_source` van het
vliegtuig is dan `override`.

Voor deze afbeeldingen moet je aangemeld zijn bij je Home Assistant, net als
voor de rest. De kaart krijgt elke afbeelding via een link die Home Assistant
ondertekent en die na een dag niet meer werkt; daarvoor wordt een nieuwe
gemaakt.

### Foto's

Als je een vliegtuig aanwijst, toont de kaart een foto ervan van
[Planespotters.net](https://www.planespotters.net), als die er is, met de naam
van de fotograaf ernaast. Klik op het vliegtuig om de foto groter te zien; de
foto linkt naar zijn pagina op Planespotters.net. Je hoeft niets in te
stellen.

De foto wordt alleen opgezocht als iemand dat vliegtuig aanwijst, niet voor
elk vliegtuig in je gebied. Je Home Assistant vraagt Planespotters.net op de
hexcode van het vliegtuig. Home Assistant bewaart het antwoord, een foto of
geen foto, 12 uur, alleen in het geheugen, dus een herstart vergeet het. De
browser die de kaart toont, laadt de afbeelding rechtstreeks van
Planespotters.net. Home Assistant downloadt, bewaart of verstuurt geen enkele
afbeelding.

⚠ Een foto toont het vliegtuig zoals de fotograaf het zag, misschien in een
eerdere beschildering of bij een eerdere gebruiker. Niet elk vliegtuig heeft
een foto op Planespotters.net.

⚠ Er wordt geen foto opgezocht voor een vliegtuig dat met een tijdelijk adres
voor privacy vliegt (het programma Privacy ICAO Address van de FAA, Verenigde
Staten), omdat die hexcode het vliegtuig niet identificeert, en ook niet voor
een spoor zonder echte hexcode.

⚠ Foto's kunnen nog niet worden uitgezet.

Elk vliegtuig met een hexcode draagt `marker_photo_lookup`: het adres op je
Home Assistant waar de kaart om de foto vraagt. Alleen wie op je Home
Assistant is aangemeld, kan het gebruiken. De foto's zijn het werk van hun
fotografen: zie [Bronvermelding en licenties](#bronvermelding-en-licenties).

### De vliegtuigen van de president

De vliegtuigen die de president van de Verenigde Staten gebruikt, worden
overal ter wereld getoond, op hun hexcodes, nooit op roepnaam, samen met de
vliegtuigen van de 89th Airlift Wing (roepnamen SAM en VENUS) en de militaire
vliegtuigen die een presidentieel vliegtuig begeleiden. Ze komen uit één
verzoek per minuut dat Live Track Aircraft toch al doet. Elk draagt een
attribuut `watch` dat zegt waarom het getoond wordt, en een presidentieel
vliegtuig zijn naam in `presidential_airframe`.

⚠ Een presidentieel vliegtuig op de kaart zegt niets over wie er aan boord
is.

### De EnforcementAircraft-lijst en Live Track SALT

[EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)
is een openbare lijst van vliegtuigen die door immigratie- en federale
ordediensten worden gebruikt, elk item met zijn bronnen, gepubliceerd door
StrausbergAutomationWorks. In je gebied knippert een vliegtuig dat de lijst uit
haar bronnen bevestigt rood en blauw, en een verkeersvliegtuig dat onder meer
chartervluchten voor ICE Air vliegt, heeft een constante gloed. Ze worden
altijd gehouden, ook als je gebied vol is.

Zijn metgezel, [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
tekent de vliegtuigen op de lijst waar ze ook vliegen, niet alleen in je
gebied. Installeer beide en elk houdt zich aan zijn eigen deel: Live Track
Aircraft tekent elk vliegtuig in zijn eigen gebied, die op de lijst
inbegrepen, en Live Track SALT tekent de vliegtuigen op de lijst overal
elders. Ze delen één verzoek aan de bronnen, en geen vliegtuig wordt twee keer
getekend.

---

## Alle entiteiten die het aanmaakt

Voor elk gebied:

| Entiteit | Wat het is |
|---|---|
| `sensor.aircraft_in_range` | **Aircraft in range**: hoeveel vliegtuigen nu in de cirkel zijn, allemaal, ook als het er meer zijn dan het maximum. Die van een tweede gebied is `sensor.aircraft_in_range_2`, enzovoort |
| `geo_location.aircraft_…` | één per vliegtuig, genoemd naar zijn hexcode (`geo_location.aircraft_a1b2c3`); hij komt en gaat met het vliegtuig. Elk draagt `source: live_track_aircraft`, en zijn status is zijn afstand tot het middelpunt in kilometers |

De attributen van de sensor zeggen wat er gebeurt: `published_count` (hoeveel
er op de kaart staan), `capped` (waar als het maximum de lijst heeft
ingekort), `source` (welk netwerk het laatst antwoordde), `source_backoff`,
`route_artifact`, `route_download`, `airport_table`, `airport_download`,
`route_lookup`, `watched_count`, `military_in_areas`, `military_by_area`,
`followed_asked`, `followed_found`, `follow_status`, `adsblol_key` en
`enforcement_list`.

⚠ **De markeringen van vliegtuigen hebben bewust geen unieke ID.** Een gebied
ziet in een jaar duizenden verschillende vliegtuigen, en een registerregel
voor elk zou Home Assistant zonder nut trager laten opstarten. Daarom kunnen
ze in de interface niet hernoemd, verborgen of aan een ruimte toegewezen
worden. Hun entiteits-ID's komen toch uit de hexcode, dus hetzelfde vliegtuig
krijgt altijd dezelfde ID. De sensor heeft een unieke ID en kan hernoemd
worden.

⚠ **Je database.** De recorder van Home Assistant slaat een nieuwe regel op
telkens als een entiteit verandert, en een vliegend vliegtuig verandert bij
elke update, standaard elke 15 seconden. Op ons testsysteem kostte in
september 2026 een entiteit zoals deze, elke 15 seconden bijgewerkt, ongeveer
9,6 MB per dag; bij 50 vliegtuigen is dat ongeveer 480 MB per dag. Wil je de
geschiedenis van elk vliegtuig niet, houd ze dan buiten de recorder. Voeg dit
toe aan `configuration.yaml` en herstart daarna:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.aircraft_*
```

Heeft je `configuration.yaml` al een sectie `recorder:`, voeg dan alleen het
patroon `geo_location.aircraft_*` toe, onder `exclude:` en `entity_globs:`.
Een kaart die ingesteld is om geschiedenis te tekenen, heeft dan geen spoor om
te tekenen. `sensor.aircraft_in_range` kost weinig: zijn attributen hebben
weinig waarden, dus de recorder slaat ze één keer op.

---

## Wat het verstuurt en downloadt

**Over je locatie.** Het middelpunt en de straal van elk gebied worden bij
elke update naar adsb.fi gestuurd, standaard elke 15 seconden, en naar
adsb.lol als adsb.fi niet antwoordt. Het middelpunt wordt gestuurd zoals je
het hebt ingesteld, en het begint bij je huis: om je huis niet meer te sturen,
verplaats je het middelpunt ervandaan (**Configureer** → **Centre**) of
verwijder je het gebied. De hexcodes en roepnamen die je volgt, worden één
keer per minuut naar adsb.fi (of adsb.lol) gestuurd, en je adsb.lol-sleutel
alleen naar adsb.lol. De roepnamen van lijnvluchten in je gebied worden naar
adsbdb gestuurd als FiledRoutesDB er geen route voor heeft. Als iemand op de
kaart een vliegtuig aanwijst, wordt de hexcode ervan naar Planespotters.net
gestuurd, hoogstens één keer per 12 uur per vliegtuig, en de browser die de
kaart toont, laadt de foto daarvandaan. Dit kan nog niet worden uitgezet.
Verder wordt er niets over jou ergens naartoe gestuurd. Elke dienst ziet je
internetadres, zoals elke website.

**Hoeveel.**

| Bron | Wat en hoe vaak | Na een fout |
|---|---|---|
| adsb.fi | elk vliegtuig in je cirkel, bij elke update (standaard elke 15 seconden); één verzoek per minuut voor de op hexcode gevolgde vliegtuigen en de vliegtuigen van de president; één voor de militaire lijst; één voor alle gevolgde roepnamen samen, alleen als je er volgt | vraagt in plaats daarvan adsb.lol. Een bron die weigert met HTTP 429, wordt overgeslagen voor de tijd die hij vraagt, of voor 1 minuut, verdubbeld tot 10 minuten |
| adsb.lol | dezelfde verzoeken, alleen zolang adsb.fi niet antwoordt | hetzelfde |
| adsbdb | één verzoek per nieuwe roepnaam van een luchtvaartmaatschappij waarvoor FiledRoutesDB geen route heeft, minstens 1 seconde ertussen; een antwoord wordt 30 dagen bewaard, een "geen route" 24 uur. Antwoorden worden alleen in het geheugen bewaard | 15 minuten niet opnieuw gevraagd; alle verzoeken pauzeren 15 minuten na HTTP 429 |
| Planespotters.net | één verzoek om de foto van een vliegtuig de eerste keer dat iemand het aanwijst, daarna 12 uur geen voor dat vliegtuig. Antwoorden worden alleen in het geheugen bewaard. De foto zelf laadt de browser die de kaart toont | na HTTP 429 wordt geen foto gevraagd voor de tijd die Planespotters.net vraagt, of 10 minuten; na HTTP 403 een dag lang |
| FiledRoutesDB, van GitHub | een klein controlesombestand één keer per dag, na 14:00 uur Chicago-tijd (Verenigde Staten); het bestand zelf, ongeveer 4,6 MB, alleen als het veranderd is | een uur later opnieuw geprobeerd; je kopie blijft in gebruik tot hij verloopt |
| AirportZones, van GitHub | een klein controlesombestand één keer per dag; de tabel zelf, ongeveer 4,8 MB, alleen als hij veranderd is | een uur later opnieuw geprobeerd; je kopie blijft in gebruik |
| EnforcementAircraft, van GitHub | een klein controlesombestand één keer per uur; de lijst zelf, klein, alleen als hij veranderd is | je kopie blijft in gebruik |
| Luchtvaartuigregister van de FAA (Verenigde Staten) | het register, ongeveer 73 MB, één keer per 7 dagen, van `registry.faa.gov` | de volgende dag opnieuw geprobeerd; je kopie blijft in gebruik |

De gedownloade bestanden worden gedeeld met andere Live Track-modules, dus elk
wordt maar één keer gedownload, hoeveel modules je ook installeert. Ze staan
in de map `.storage` van Home Assistant onder namen die met `saw_` beginnen.
Verwijder je Live Track Aircraft en gebruikt geen andere Live Track-module ze,
dan kun je ze met de hand verwijderen.

---

## Help het groeien

Live Track Aircraft groeit nog. We voegen routebronnen, gegevensbronnen en
vliegtuiggegevens toe zodra we ze vinden, en we willen weten wat je hierna
zou willen.

### Iets voorstellen

Ontbreekt je land, je luchthaven of je vliegtuigtype? Klopt er iets niet, of
is iets moeilijk te begrijpen? Laat het ons weten op de manier die voor jou
het makkelijkst is:

* [**Vul een kort formulier in**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=nl.yml)
  in het Nederlands. Je hebt een gratis GitHub-account nodig.
* **Stuur een e-mail** naar
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Geen account nodig.

Hoe dan ook, het helpt als je ons vertelt:

* wat je graag zou zien, en waar ter wereld;
* een link naar waar de gegevens worden gepubliceerd, als je die kent (een
  open-datapagina, een openbare feed, de website van een dienst): niet nodig,
  maar het helpt;
* de taal van je Home Assistant, als het probleem de formulering of een
  vertaling is.

Schrijf in het Engels of in je eigen taal, wat voor jou het makkelijkst is.

### Zelf iets toevoegen, met onze hulp

Wil je zelf iets toevoegen, dan helpen we je daarbij, van de eerste vraag tot
de afgeronde release. Je hoeft geen ontwikkelaar te zijn om te beginnen:

* **Een vertaling.** De teksten in de instellingsdialoog zijn een korte lijst
  zinnen in één tekstbestand. We laten je zien welk bestand en welke regels.
* **Een nieuwe gegevensbron.** Vertel ons waar de gegevens worden
  gepubliceerd. We kunnen de code samen schrijven, of de jouwe nakijken.
* **Testen waar je woont.** Installeer het, bekijk jouw deel van de kaart, en
  vertel ons wat klopt en wat niet.
* **Een verbetering van deze README.** Als een stap niet overeenkwam met wat
  je zag, vertel ons wat je zag.

[**Vertel ons wat je in gedachten hebt**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=nl.yml)
of schrijf naar
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
en we antwoorden met de volgende stappen.

---

## Talen

Deze README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), **Nederlands**, [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md).
Elke vertaalde README is volledig.

De instellingsdialoog en de opties zijn voorlopig alleen in het Engels, in welke
taal je Home Assistant ook staat. Spreek je een andere taal, dan kun je ze zelf
vertalen: het is een korte lijst zinnen in één bestand, en [we helpen je
daarbij](#zelf-iets-toevoegen-met-onze-hulp).

Een fout in een vertaling gevonden, of een andere taal nodig? Laat het ons
weten op <https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues>,
of [vertaal het met onze hulp](#zelf-iets-toevoegen-met-onze-hulp).

---

## Bronvermelding en licenties

* **adsb.fi** (<https://adsb.fi>): posities van vliegtuigen, open gegevens
  alleen voor persoonlijk, niet-commercieel gebruik, onder de voorwaarden in
  zijn [open-data-README](https://github.com/adsbfi/opendata), die vragen
  adsb.fi te vermelden en naar zijn startpagina te linken. Door deze
  integratie te installeren gebruik je adsb.fi, en gelden zijn voorwaarden
  voor jou.
* **adsb.lol** (<https://adsb.lol>): posities van vliegtuigen, onder de
  [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/).
  Door deze integratie te installeren gebruik je adsb.lol, en gelden zijn
  voorwaarden voor jou. Beide netwerken worden door vrijwilligers gedraaid: als
  je kunt, steun ze door ze met een ontvanger te voeden.
* **FiledRoutesDB** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/FiledRoutesDB)):
  routes uit vliegplannen die bij de FAA (Verenigde Staten) zijn ingediend,
  gegevens onder CC BY 4.0, met de LADD-lijst van de FAA toegepast vóór
  publicatie.
* **adsbdb** (<https://www.adsbdb.com>): routes buiten FiledRoutesDB. Zijn
  routegegevens zijn het werk van David Taylor (Edinburgh) en Jim Mason
  (Glasgow), en mogen zonder toestemming niet gekopieerd of opnieuw
  gepubliceerd worden, dus antwoorden worden alleen in het geheugen bewaard,
  nooit in een bestand geschreven, en elk vliegtuig met een route van adsbdb
  vermeldt hen.
* **Het luchtvaartuigregister van de FAA** (Federal Aviation Administration,
  Verenigde Staten): namen van eigenaren en gebruikers van in de Verenigde
  Staten geregistreerde vliegtuigen, openbare gegevens van de regering van de
  Verenigde Staten. De FAA laat zelf de namen weg die ze moet achterhouden,
  voordat ze het bestand publiceert.
* **OurAirports** (<https://ourairports.com>), via
  [AirportZones](https://github.com/StrausbergAutomationWorks/AirportZones):
  namen en posities van luchthavens, onder de ODbL 1.0; tijdzones toegevoegd
  door StrausbergAutomationWorks.
* **EnforcementAircraft** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)):
  de lijst van vliegtuigen van immigratie- en federale ordediensten, onder de
  ODbL 1.0.
* **ADS-B Radar** (<https://adsb-radar.com>): de vliegtuigsymbolen, uit zijn
  [SVG-symbolenset voor vliegtuigen](https://adsb-radar.com/help/icons.html)
  door Jos Nutbroek, gebruikt onder zijn voorwaarden, die om deze
  terugverwijzing vragen. De symbolen vallen niet onder de MIT-licentie van
  deze repository. Sommige symbolen zijn door StrausbergAutomationWorks in de
  stijl van de set getekend en aan ADS-B Radar geschonken, dus ook voor hen
  gelden zijn voorwaarden. Deze integratie levert de symbolen met een nieuwe
  vulling en omtrek, geschaald naar de klasse van het vliegtuig, en laat
  sommige propellers en rotoren draaien. Elke wijziging staat in
  [ATTRIBUTION.md](ATTRIBUTION.md).
* **Planespotters.net** (<https://www.planespotters.net>): de foto's van
  vliegtuigen, via zijn [foto-API](https://www.planespotters.net/photo/api) en
  onder zijn voorwaarden. Elke foto is het werk van zijn fotograaf, die
  ernaast wordt genoemd, en linkt naar zijn pagina op Planespotters.net. Er is
  geen foto in deze repository gekopieerd, en Home Assistant downloadt,
  bewaart of verstuurt geen enkele afbeelding. Door deze integratie te
  installeren gebruik je Planespotters.net, en zijn voorwaarden gelden voor
  jou.
* **De kaart** is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, een kopie van [ha-map-card](https://github.com/nathan-gs/ha-map-card)
  door nathan-gs, MIT. De kaarttegels en hun vermeldingen staan in de README
  ervan.

Geen van deze organisaties heeft deze integratie gemaakt of gesteund.

**Code**: MIT, in [LICENSE](LICENSE).

**Voor ontwikkelaars:** de entiteiten volgen het gedeelde kaartcontract van
Live Track, zodat elke module zonder sjabloonsensoren op één kaart verschijnt;
posities komen via een broninterface in
`custom_components/live_track_aircraft/sources/`, zodat een andere feed kan
worden toegevoegd zonder de entiteiten aan te raken. De tests draaien met
`python -m unittest discover -s tests`.

---

## Trefwoorden

Home Assistant vliegtuigen · Home Assistant vluchten volgen · ADS-B ·
ADS-B-kaart · vluchten volgen · vliegtuigradar · vliegtuigen boven mij ·
MLAT · Mode S · vliegroutes · militaire vliegtuigen · Air Force One ·
helikopters · aircraft · flight tracker · Flugzeuge · Flugverfolgung ·
avions · suivi des vols · 飞机 · 航班跟踪 · aviones · seguimiento de vuelos ·
aerei · tracciamento voli · fly · flysporing · adsb.fi · adsb.lol · adsbdb ·
FiledRoutesDB · FAA-register · OurAirports · ADS-B Radar · Planespotters.net ·
vliegtuigfoto's · geo_location · kaart · Lovelace · HACS · Marktplaats · Live
Track · LiveTrack · StrausbergAutomationWorks

---

**Erkenning.** StrausbergAutomationWorks erkent de inheemse volken van alle
landen en wateren op deze kaart, overal ter wereld, en betuigt zijn respect aan
hun Elders, van vroeger en nu.
