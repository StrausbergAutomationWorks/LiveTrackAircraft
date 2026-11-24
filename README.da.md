# Live Track Aircraft

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · **Dansk** · [Alle sprog](#sprog)

**Fly til Home Assistant, på ét kort.** Live Track Aircraft sætter de fly,
der flyver over dit hjem, eller over et hvilket som helst sted i verden, du
vælger, på dit Home Assistant-kort: hvert tegnet som sin egen type, drejet i
den retning, det flyver, med hvem der opererer det og, når det vides, hvor det
skal hen. Den kan også følge udvalgte fly og flyvninger, hvor de end er, og
holde øje med militærfly i områder, du angiver.

> **Live Track Aircraft er ét modul i Live Track**, en familie af Home
> Assistant-integrationer, der tegner alt, hvad der bevæger sig, og vejret, det
> bevæger sig igennem, på ét fælles kort: fly, skibe, tog og vejr. Installer
> den alene eller ved siden af de andre moduler
> ([liste nedenfor](#en-del-af-live-track-de-andre-moduler)).

> **Den vokser, og idéer er velkomne.** Live Track Aircraft dækker i dag hele
> verden, hvor frivillige driver modtagere, med ruter og ejernavne mest
> detaljeret for USA, og vi tilføjer flere rutekilder og flere oplysninger om
> fly. Mangler dit? [Foreslå det](#hjælp-den-med-at-vokse), eller tilføj det
> selv: vi hjælper dig med det.

**Status: 0.1.6, udgivet.** I Markedspladsens katalog ([installér den
nedenfor](#installation-trin-for-trin)).

Originalt arbejde af StrausbergAutomationWorks. Ikke tilknyttet eller
godkendt af adsb.fi, adsb.lol, adsbdb, Federal Aviation Administration (USA),
OurAirports, ADS-B Radar, Planespotters.net, noget flyselskab eller nogen
operatør af fly.

> ⚠ **Ikke et sikkerhedssystem.** Den viser offentlige data, som regel få
> sekunder gamle og nogle gange et minut eller mere, og kun fly, som
> frivilliges modtagere tilfældigvis hører. Den er ikke til navigation, til at
> holde fly adskilt eller til noget andet operationelt formål.

---

## Indhold

1. [Alt, hvad den gør](#alt-hvad-den-gør)
2. [Hvor den virker](#hvor-den-virker)
3. [En del af Live Track: de andre moduler](#en-del-af-live-track-de-andre-moduler)
4. [Før du begynder](#før-du-begynder)
5. [Installation, trin for trin](#installation-trin-for-trin)
6. [Opsætning, trin for trin](#opsætning-trin-for-trin)
7. [Gratis nøgler, der slår mere til, trin for trin](#gratis-nøgler-der-slår-mere-til-trin-for-trin)
8. [Sæt kortet på et betjeningspanel](#sæt-kortet-på-et-betjeningspanel)
9. [Brug den i automatiseringer](#brug-den-i-automatiseringer)
10. [Alt på kortet i detaljer](#alt-på-kortet-i-detaljer)
11. [Alle entiteter, den opretter](#alle-entiteter-den-opretter)
12. [Hvad den sender og henter](#hvad-den-sender-og-henter)
13. [Hjælp den med at vokse](#hjælp-den-med-at-vokse)
14. [Sprog](#sprog)
15. [Tak og licenser](#tak-og-licenser)
16. [Nøgleord](#nøgleord)

---

## Alt, hvad den gør

### På kortet, uden at sætte noget op

Du tilføjer et **område**: et midtpunkt på kortet og en radius omkring det.
Det begynder ved dit hjem. Alt nedenfor vises så i det område eller, hvor
tabellen siger det, hvor som helst i verden.

| Hvad | Hvor | Fra |
|---|---|---|
| **Fly**: passagerfly, småfly, helikoptere, svævefly, balloner og droner, hvert tegnet som sin egen type og drejet i den retning, det flyver | i hvert område | adsb.fi, eller adsb.lol, når adsb.fi ikke svarer |
| **Hvem der opererer det**: flyselskabet, ejeren eller typen, når intet andet vides, i markørens etiket | hvert fly | flyselskabets kaldesignal; FAA's luftfartøjsregister (USA) for ejere |
| **Farver, der siger, hvem der flyver det**: regering, politi, føderale ordensmyndigheder, militæret, ambulancefly og helikoptere, hver i sin egen farve | hvert fly, hvor det vides | FAA's luftfartøjsregister (USA) og datastrømmens militærmærke |
| **Ruter**: hvor flyet lettede, og hvor det skal hen, med lufthavnenes navne og en anslået ankomsttid | flyvninger, der indleverer en flyveplan til FAA (USA); andre steder, når adsbdb kender flyvningen | FiledRoutesDB, derefter adsbdb |
| **USA's præsidents fly**, med flyene fra 89th Airlift Wing og de militærfly, der eskorterer dem | hvor som helst i verden | adsb.fi og dens militærliste |
| **Fly på den offentlige EnforcementAircraft-liste** (udlændinge- og føderale ordensmyndigheder), med blinkende lys | i hvert område | EnforcementAircraft-listen |
| **Militærfly i dine overvågningsområder**: hvert fly, datastrømmen markerer som militært, inden for op til ti cirkler, du angiver, også når dit område er fuldt. Valgfrit: du skriver cirklerne i opsætningsdialogen | hvor som helst i verden | adsb.fi's militærliste |
| **Fly og flyvninger, du følger**: dit eget fly, en klubs flåde eller den flyvning, et familiemedlem er med. Valgfrit: du skriver deres koder i opsætningsdialogen | hvor som helst i verden | adsb.fi |
| **Fotos**: et foto af flyet, med fotografens navn, når du peger på det | hvert fly, som Planespotters.net har et foto af | Planespotters.net ([mere](#fotos)) |
| **Dit eget billede til ét fly**, i stedet for dets ikon | overalt, hvor det fly vises | et billede, du lægger i en mappe ([sådan](#dit-eget-billede-til-et-fly)) |

### Med din egen gratis nøgle eller konto

| Gratis nøgle eller konto | Hvad den tilføjer |
|---|---|
| **adsb.lol**-nøgle | flere forespørgsler om dagen til adsb.lol, den anden kilde, så kortet bliver ved under et langt udfald hos adsb.fi |

Hver tager få minutter at få: [trin for trin nedenfor](#gratis-nøgler-der-slår-mere-til-trin-for-trin).

---

## Hvor den virker

| Område | Hvad du får | Fra | Kræver |
|---|---|---|---|
| **Hele verden** | flyenes positioner, hvor frivillige driver modtagere: tæt over Europa og Nordamerika, tyndere andre steder, og lidt eller intet langt ude på havet | adsb.fi, adsb.lol | intet |
| **Hele verden** | lufthavnenes navne på ruter, og lufthavnenes tidszoner til ankomsttiden | OurAirports, via tabellen AirportZones | intet |
| **Hele verden** | ruter for mange rutefly, kontrolleret mod, hvor flyet faktisk er | adsbdb | intet |
| **Nordamerika**: USA | ejer- og operatørnavne for fly registreret i USA, og farverne for regerings- og politifly | FAA's luftfartøjsregister | intet |
| **Nordamerika**: USA | ruter for flyvninger indleveret til FAA, også internationale flyvninger til og fra USA | FiledRoutesDB | intet |

Ikke på listen? [Fortæl os det](#hjælp-den-med-at-vokse). Hvor nogen
offentliggør dataene åbent, ser vi på at tilføje dem.

⚠ **Dækningen er god, hvor der er modtagere, og fraværende, hvor der ikke
er.** Et fly vises kun, når en frivilligs modtager hører det, eller når flere
modtagere sammen kan finde dets position. Ingen indstilling kan skabe dækning,
der ikke findes. **En tom himmel på kortet kan betyde, at der ikke er
modtagere nær dig, ikke at der ikke er fly.**

⚠ **Ruter er mest for USA.** FiledRoutesDB rummer kun flyveplaner indleveret
til FAA. Andre steder kommer en rute fra adsbdb, som kender mange rutefly og
få andre, så uden for USA viser mange fly ingen rute.

⚠ **Ejernavne findes kun for fly registreret i USA.** Et fly registreret i et
andet land viser sit flyselskab ud fra kaldesignalet, eller sin type.

---

## En del af Live Track: de andre moduler

Live Track er en række Home Assistant-integrationer, én for hver slags ting,
der bevæger sig, alle tegnet på det samme kortkort. Hver virker for sig;
sammen giver de ét levende billede. De deler kortkortet og et Python-bibliotek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
så installerer du endnu et modul, kommer der ingen ekstra forespørgsler til en
kilde, som et andet allerede læser.

| Modul | Hvad det sætter på kortet | Status |
|---|---|---|
| **Live Track Aircraft** | fly over dig via ADS-B, med ruter og typeikoner (dette modul) | udgivet |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | skibe og både via AIS, nær dig eller hvor som helst | udgivet |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | nærbanetog i Nordamerika, Europa og Australien | udgivet |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | intercity- og fjerntog i Nordamerika, Europa og Australien | udgivet |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | fly og skibe fra udlændinge- og føderale ordensmyndigheder, fra offentlige lister | udgivet |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | vejr, storme og naturfarer | udgivet |
| Live Track Stations | afgangstavler og "tid til at gå"-påmindelser for hver station | planlagt |
| Live Track Satellites | satellitter, der passerer over dig | planlagt |
| Live Track Freight Trains | gods- og arbejdstog, hvor jernbaner offentliggør dem | planlagt |
| Live Track Transit | bybusser, sporvogne, færger og metro | planlagt |
| Live Track Intercity Buses | fjern- og regionalbusser | planlagt |
| Live Track Commuter Buses | pendlerbusser | planlagt |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | det fælles kortkort, som hvert modul tegner på | udgivet, installeres med hvert modul |

Alt er gratis og open source. Intet holdes tilbage til sponsorer.

---

## Før du begynder

* **Home Assistant** 2026.11 eller nyere.
* **Markedspladsen** (HACS) i din Home Assistant, så du nemt kan installere
  og opdatere den. Uden den kan du kopiere filerne manuelt.
* **Internetadgang** for Home Assistant: alt kommer fra offentlige kilder.
* **Valgfrit: auto-entities** fra Markedspladsen, til at sætte markørerne på
  kortet (se [Sæt kortet på et betjeningspanel](#sæt-kortet-på-et-betjeningspanel)).
* Intet at betale og ingen konto nødvendig. adsb.lol-nøglen ovenfor er
  valgfri.
* Home Assistant installerer selv de to Python-pakker, den har brug for
  (`saw-livetrack` og `tzfpy`), første gang integrationen indlæses.

---

## Installation, trin for trin

### Fra Markedspladsen (anbefalet)

1. Åbn **Indstillinger → Markedsplads** (HACS) i Home Assistant.
2. Søg efter **Live Track Aircraft**, og åbn den.
3. Vælg **Download** (eller **Installér**).
4. **Genstart Home Assistant**: **Indstillinger → System → Reparationer**
   tilbyder genstarten, eller brug **Indstillinger → System → Genstart**.

Hvis søgningen ikke finder den, så tilføj den via dens link: vælg **Tilføj fra
link** (eller menuen med tre prikker → **Brugerdefinerede repositorier**), skriv
`StrausbergAutomationWorks/LiveTrackAircraft`, vælg **Integration**, hvis du
bliver spurgt om typen, og fortsæt derefter fra trin 3.

Markedspladsen tilbyder derefter hver ny udgivelse som en opdatering.

### Manuelt

1. Hent kildekoden til den
   [seneste udgivelse](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/releases/latest).
2. Kopiér mappen `custom_components/live_track_aircraft` fra den over i mappen
   `custom_components` i din Home Assistants konfigurationsmappe (opret
   `custom_components`, hvis den ikke findes).
3. Genstart Home Assistant.

For at opdatere manuelt skal du erstatte mappen med den fra den nye udgivelse
og genstarte.

---

## Opsætning, trin for trin

Opsætningsdialogen er på engelsk. Dens felter er nævnt her, som den viser dem.

1. Åbn **Indstillinger → Enheder & tjenester**.
2. Vælg **Tilføj integration** (nederst til højre), og søg efter **Live Track
   Aircraft**.
3. **Centre** (midtpunkt): træk markøren til midten af den himmel, du vil
   holde øje med. Den begynder ved dit hjem.
4. **Radius (km)** (radius): hvor langt fra midtpunktet fly vises, fra 1 til
   463 km (0,6 til 288 miles). Er du i tvivl, så behold 56 km (35 miles).
5. **Update interval (seconds)** (opdateringsinterval i sekunder): behold 15.
   Kilderne afviser hyppigere forespørgsler.
6. **Maximum aircraft published** (højeste antal viste fly): behold 250. Det
   er en sikkerhedsgrænse, ikke en måde at vise færre fly på.
7. Lad de fire valgfrie felter stå tomme indtil videre. Hvert er forklaret
   nedenfor.
8. Vælg **Indsend**.

Det er det hele. Fly vises inden for et minut. Hvert område er én post, med
sit midtpunkt og sin radius som titel, for eksempel
`39.817, -84.050 - 56 km`. For at holde øje med et andet område skal du
tilføje integrationen igen med et andet midtpunkt eller en anden radius.
Samme midtpunkt og radius to gange afvises.

Ruter, lufthavnsnavne og ejernavne fyldes ud i løbet af de første minutter,
efterhånden som de filer, de kommer fra, hentes
([Hvad den sender og henter](#hvad-den-sender-og-henter)).

### Ændr, hvad den viser: indstillingerne

Åbn **Indstillinger → Enheder & tjenester → Live Track Aircraft → Konfigurér**
(tandhjulet) på det område, du vil ændre. Hver indstilling med almindelige
ord:

| Indstilling | Hvad den gør | Standard |
|---|---|---|
| **Centre** | flytter området; dets titel følger med | dit hjem |
| **Radius (km)** | hvor langt fra midtpunktet fly vises, 1 til 463 km (0,6 til 288 miles) | 56 km (35 miles) |
| **Update interval (seconds)** | hvor ofte der spørges efter positioner, 15 til 3.600 sekunder | 15 |
| **Maximum aircraft published** | en sikkerhedsgrænse, 1 til 1.000; er der flere fly i cirklen, beholdes de nærmeste. Fly, du følger, fly i dine militære overvågningsområder og fly på EnforcementAircraft-listen beholdes altid | 250 |
| **Military watch areas** | cirkler, hvor hvert militærfly vises ([sådan](#militære-overvågningsområder)) | tom |
| **Aircraft to follow (hex codes)** | fly, der følges overalt, efter deres hex-kode ([sådan](#fly-og-flyvninger-du-følger)) | tom |
| **Flights to follow (call signs)** | flyvninger, der følges overalt, efter deres kaldesignal (samme afsnit) | tom |
| **adsb.lol API key** | din egen nøgle til adsb.lol ([sådan får du en](#gratis-nøgler-der-slår-mere-til-trin-for-trin)) | tom |

Ryd et af de fire valgfrie felter for at slå den del fra.

---

## Gratis nøgler, der slår mere til, trin for trin

De er alle gratis og personlige: hver person, der installerer Live Track
Aircraft, får sin egen. Indsæt hver i **Indstillinger → Enheder & tjenester →
Live Track Aircraft → Konfigurér**.

### adsb.lol (flere forespørgsler til den anden kilde, hele verden)

Live Track Aircraft spørger først adsb.fi og spørger kun adsb.lol, så længe
adsb.fi ikke svarer. Uden nøgle tillader adsb.lol 500 forespørgsler om dagen
fra én internetadresse, som et udfald hos adsb.fi kan bruge op på omkring to
timer. En nøgle hæver den grænse. Du behøver ikke én for at begynde.

1. Åbn <https://www.adsb.lol/request>, og bed om en gratis nøgle med
   formularen der. adsb.lol's dokumentation giver denne nøgle 1.000
   forespørgsler om dagen.
2. Hvis du leverer data til adsb.lol med din egen modtager, så brug i stedet
   din feeder-nøgle: adsb.lol's dokumentation giver den 7.200 forespørgsler om
   dagen. Dine nøgler står under **My keys** på adsb.lol
   (<https://www.adsb.lol/mmb>).
3. Indsæt nøglen i **adsb.lol API key**, og vælg **Indsend**.

Nøglen sendes kun til adsb.lol. Hvis adsb.lol afviser den (forkert eller
udløbet), fortsætter Live Track Aircraft uden den, og områdets
`sensor.aircraft_in_range` viser `refused` i sin egenskab `adsblol_key`, indtil
du ændrer nøglen. Ellers viser den `set`, eller `none` uden nøgle. Der skal
ingen adgangskode og ingen hemmelighed til.

---

## Sæt kortet på et betjeningspanel

Kortet er [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
det kort, som hvert Live Track-modul tegner på. **Det installeres med Live
Track Aircraft**: intet at hente, intet at kopiere, ingen ressource at
tilføje.

1. Åbn et betjeningspanel, vælg blyanten (**Redigér betjeningspanel**), og
   derefter **Tilføj kort**.
2. Rul helt ned, og vælg **Manuel**.
3. Indsæt dette, og vælg **Gem**:

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

Denne form kræver
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities) fra
Markedspladsen. Er andre Live Track-moduler installeret, så tilføj ét filter
`- domain: geo_location` mere for hver af deres kilder (`live_track_ships`,
`live_track_weather` og så videre).

**Uden auto-entities:** LiveTrackMapCard kan selv vælge, hvad den viser, med
`entity_filter`. Indsæt dette i stedet; der skal ikke installeres mere:

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

Andre Live Track-moduler kommer i `entity_filter` på samme måde: én regel
`- domain: geo_location` mere for hver kilde.

**På kortet:**

* Hvert fly tegnes som sin egen type, drejet i den retning, det flyver, og
  bevæger sig jævnt mellem de positioner, det melder.
* Dets etiket er flyvningens kaldesignal (`UAL308`), ellers hvem der opererer
  det (`Lewis University`), ellers dets type (`Cessna 172 Skyhawk`).
* **Peg på** et fly for at se dets flyselskab eller operatør, dets foto, når
  der er et, og, når en rute kendes, ruten og hvor mange minutter der er til
  ankomst. **Klik** på det for alle detaljer og et større foto, der linker til
  dets side på Planespotters.net ([Fotos](#fotos)).

Er dine betjeningspanelers ressourcer sat op i YAML
(`lovelace: resource_mode: yaml`), kan intet registreres for dig: en
meddelelse under **Reparationer** giver så den præcise linje, du skal tilføje.
Et kort, du selv har installeret via Markedspladsen, får lov at være. Hvis
integrationens filer fjernes, mens dens områder stadig er sat op, og intet
andet Live Track-modul er installeret, så fjern selv kortets række under
**Indstillinger → Betjeningspaneler → Ressourcer**. Ethvert andet kortkort, der
viser `geo_location`-entiteter, viser også flyene, som almindelige markører.

---

## Brug den i automatiseringer

Alt er almindelige Home Assistant-entiteter, så automatiseringseditoren virker
med dem, uden kode.

**En notifikation på telefonen, når et militærfly er i et af dine militære
overvågningsområder:**

1. **Indstillinger → Automatiseringer & scener → Tilføj automatisering →
   Opret ny automatisering**.
2. **Når**: **Tilføj udløser** → **Entitet** → **Numerisk tilstand**. Vælg
   entiteten **Aircraft in range**, **Egenskab** **Military in areas**
   (`military_in_areas`) og **Over** `0`.
3. **Så gør**: **Tilføj handling**, søg efter din telefons
   notifikationshandling (den bærer din telefons navn), og skriv en besked,
   for eksempel:

   ```text
   Et militærfly er i dit overvågningsområde
   ```

4. **Gem**.

Det kræver mindst ét militært overvågningsområde
([sådan](#militære-overvågningsområder)).

**Andre idéer:** en notifikation, når et familiemedlems flyvning er i luften,
når egenskaben `followed_found` stiger over 0; et lys, der tænder, når mere
end 20 fly er over dit hjem i Frankfurt (Tyskland); antallet af fly over din
flyveplads i Queensland (Australien) på et betjeningspanel, fra
`sensor.aircraft_in_range`; en besked, når din klubs fly letter, når dets egen
entitet (`geo_location.aircraft_` og dets hex-kode) dukker op.

---

## Alt på kortet i detaljer

### Fly

Fly sender deres position via radio, med et system, der hedder ADS-B.
Frivillige over hele verden driver modtagere og deler det, de hører, gennem
fællesskabsnetværk. Live Track Aircraft spørger et af dem, adsb.fi, om hvert
fly inden for din cirkel, som standard hvert 15. sekund. Når adsb.fi ikke
svarer, eller svarer med langt færre fly end et øjeblik før, spørger den
adsb.lol. Hvor flere modtagere hører et fly, der ikke sender sin egen
position, kan netværkene stadig finde det (multilateration, MLAT).

Hvert fly er én markør, opkaldt efter dets hex-kode: den seks tegn lange
adresse, som dets transponder sender, og som hører til flyet og ikke ændrer
sig. Markøren vises, når flyet kommer ind i din cirkel, og fjernes, når det
forlader den.

Etiketten er det mest nyttige navn, der kendes, i denne rækkefølge:

| Flyet har | Etiketten viser | Eksempel |
|---|---|---|
| en flyvnings kaldesignal | kaldesignalet | `UAL308` |
| ellers en kendt operatør | operatøren | `Lewis University` |
| ellers en kendt type | typen | `Cessna 172 Skyhawk` |
| intet af dette | registreringen, typekoden eller hex-koden | `N12345` |

⚠ Vises ikke: fly på jorden, lufthavnskøretøjer og rene radarspor uden
identitet. Et fly, der ikke sender, eller flyver, hvor ingen modtager hører
det, kan ikke vises.

På hvert fly: `identity` (hex-koden), `callsign`, `registration`,
`aircraft_type`, `aircraft_name`, `operator`, `altitude_m`, `speed_kmh`,
`vertical_rate_ms`, `course_deg`, `squawk`, `emitter_category`,
`is_military`, `is_government`, `last_seen`.

### Farver og ikoner

Hvert fly tegnes som sin egen type: et passagerfly, et forretningsjetfly, et
lille enmotorers fly, et tomotorers fly, en helikopter, et tiltrotorfly, et
svævefly, en ballon, en drone og mange flere, i størrelse efter sin klasse.
Propeller og rotorer drejer. Ikonet drejes i den retning, flyet flyver; et
langsomt fly beholder sin sidste retning i stedet for at snurre rundt.

Farven siger, hvem der flyver det, hvor det vides:

| Farve | Hvem |
|---|---|
| lysegrå | de fleste fly |
| mintgrøn | helikoptere og andre rotorfly |
| rav | regeringsfly og ambulancefly |
| blå | føderale ordensmyndigheder |
| armygrøn | militæret og kystvagten |
| hvid, med blinkende blå lys | politi |
| blinkende røde og blå lys | fly på EnforcementAircraft-listen ([nedenfor](#enforcementaircraft-listen-og-live-track-salt)) |
| et fast skær | et passagerfly, der flyver ICE Air-charterflyvninger, blandt andet arbejde |

⚠ Hvem der ejer et fly, vides mest for fly registreret i USA, fra FAA's
register. Andre steder kommer farven kun fra datastrømmens militærmærke og
flyets type.

### Ruter og ankomsttider

En rute viser, hvor flyet lettede, og hvor det skal hen, med begge
lufthavnes navne, og en anslået ankomsttid. Den kommer fra to steder:

1. **FiledRoutesDB**, en offentlig fil med flyveplaner indleveret til FAA
   (USA), bygget og udgivet af StrausbergAutomationWorks og hentet én gang om
   dagen. Hver rute kontrolleres mod, hvor flyet er, og den vej, det flyver.
   En rute, der ikke passer, vises alligevel og markeres som ikke-passende i
   `route_check`.
2. **adsbdb**, som kun spørges, når FiledRoutesDB ikke har en rute for
   kaldesignalet, én gang pr. kaldesignal. Dens svar vises kun, når det passer
   med, hvor flyet faktisk er.

Fly, hvis ejere har bedt FAA om at holde deres flyvninger ude af offentlig
visning (FAA's LADD-liste, Limiting Aircraft Data Displayed), fjernes fra
FiledRoutesDB, før den udgives. Live Track Aircraft sletter sin kopi, når
filen udløber, eller når den LADD-liste, den blev bygget efter, er mere end
14 dage gammel, så den aldrig viser ruter filtreret efter en gammel liste.

Ankomsttiden er et skøn, ikke en køreplan: den resterende afstand i lige
linje, ved flyets fart, når det er i marchhøjde, og ved en typisk fart for
dets klasse, når det ikke er. Venteløb, indflyvning og taxikørsel tælles ikke
med.

På hvert fly med en rute: `origin_icao`, `destination_icao`,
`origin_name`, `destination_name`, `route_source`, `route_check`,
`arrival_estimated_at`.

### Militære overvågningsområder

Hvert fly, datastrømmen markerer som militært, inden for cirkler, du vælger,
hvor som helst i verden, også når dit område er fuldt.

1. Åbn **Indstillinger → Enheder & tjenester → Live Track Aircraft →
   Konfigurér** på et område.
2. Skriv i **Military watch areas** hver cirkel som `latitude,longitude,km`
   (breddegrad, længdegrad, kilometer), og adskil cirklerne med semikolon,
   for eksempel `39.81,-84.04,150; 34.0,-117.8,463`. Op til ti cirkler, hver
   fra 1 til 2.000 km (0,6 til 1.243 miles). Skriv decimaler med punktum.
3. Vælg **Indsend**.

Militærflyene inden for dem vises inden for et minut og flytter sig én gang i
minuttet. Hvert bærer `watch: military area`. Områdets
`sensor.aircraft_in_range` tæller dem i `military_in_areas`, og pr. cirkel i
`military_by_area`. Ryd feltet for at stoppe.

⚠ Den viser kun det, der sender og er markeret som militært. Militære
flyvninger kan flyve med transponderen slukket, og et militærfly med en civil
registrering er ikke markeret.

### Fly og flyvninger, du følger

Live Track Aircraft kan følge fly, du vælger, hvor de end er i verden, ikke
kun inden for din cirkel: dit eget fly, en klubs eller en virksomheds flåde
eller den flyvning, et familiemedlem er med.

1. Åbn **Indstillinger → Enheder & tjenester → Live Track Aircraft →
   Konfigurér** på det område, du vil have dem vist sammen med.
2. Udfyld **Aircraft to follow (hex codes)** (fly at følge, hex-koder),
   **Flights to follow (call signs)** (flyvninger at følge, kaldesignaler)
   eller begge.
3. Vælg **Indsend**. De vises inden for cirka et minut.

**Én kode pr. fly er nok.** Vælg efter, hvad du vil følge:

| For at følge | Brug | Eksempel |
|---|---|---|
| ét fly, uanset hvilken flyvning det flyver (dit eget fly, en flåde) | dets **hex-kode** | `a1b2c3` |
| én flyvning, uanset hvilket fly der flyver den (et familiemedlems rejse) | dens **kaldesignal** | `UAL1234` |

At skrive begge koder for samme fly gør ingen skade (det tegnes én gang), men
tilføjer intet.

**Sådan skriver du koderne:**

* Adskil koderne med kommaer: `a1b2c3, a4b5c6, a7b8c9`. Mellemrum eller
  semikolon mellem koderne virker også.
* En hex-kode er præcis seks tegn: cifrene 0 til 9 og bogstaverne a til f,
  med store eller små bogstaver.
* Et kaldesignal er 2 til 8 bogstaver og cifre, skrevet som flyet sender det,
  uden mellemrum eller bindestreg: `UAL1234`, ikke `UA 1234` eller
  `UAL-1234`.
* Op til 100 hex-koder og 100 kaldesignaler. En kode skrevet to gange tæller
  én gang.
* Er én kode forkert, afviser dialogen det felt, siger, hvordan en god kode
  ser ud, og gemmer intet, før den er rettet.

**Sådan finder du koderne.** Hvert fly på kortet bærer sin hex-kode i
egenskaben `identity` og sit kaldesignal i egenskaben `callsign`. For et fly
registreret i USA viser N-nummersøgningen i FAA's register hex-koden som
"Mode S Code (Base 16 / Hex)". For et rutefly er kaldesignalet som regel
flyselskabets kode på tre bogstaver plus flynummeret, hvilket ikke er det,
billetten viser:

| Billet | Kaldesignal |
|---|---|
| United UA 1234 | `UAL1234` |
| Delta DL 89 | `DAL89` |
| American AA 100 | `AAL100` |

Nogle flyselskaber sender et kaldesignal, der ikke er flynummeret. Dukker en
flyvning ikke op, så slå den op på et live-flykort, og kopiér det kaldesignal,
der vises der. Et kaldesignal genbruges: samme kaldesignal i morgen er en
anden rejse og kan være et andet fly. Det bliver ved med at blive fulgt,
indtil du fjerner det.

**Hvad du ser.** Hvert fulgt fly tegnes med sit sædvanlige ikon og sin
sædvanlige etiket, hvor det end er, også når dit område er fuldt. Dets
egenskab `watch` lyder `followed`, og `outside_radius` siger, om det er uden
for din cirkel. Uden for din cirkel flytter det sig én gang i minuttet; inden
for den lige så ofte som alt andet. Områdets `sensor.aircraft_in_range` viser
`followed_asked` (hvor mange koder du følger), `followed_found` (hvor mange af
dem der er i luften nu) og `follow_status` (den seneste forespørgsel på
kaldesignaler: `ok`, eller hvad der gik galt).

**For at stoppe** fjerner du koden, eller rydder feltet, og vælger
**Indsend**.

⚠ Kun fly, der sender ADS-B, eller som MLAT kan finde, kan findes. Et fly på
jorden eller uden for modtagernes dækning vises ikke, og `followed_found`
tæller det ikke. Køreplaner og forsinkelser efter flynummer er ikke en del af
dette.

### Dit eget billede til et fly

Sæt et billede efter eget valg i stedet for ét flys ikon, for eksempel dit
eget fly.

1. Lav en mappe med navnet `live_track_aircraft_pictures` i din Home
   Assistants konfigurationsmappe (den mappe, der indeholder
   `configuration.yaml`).
2. Læg billedet i den, navngivet efter flyets hex-kode: `a1b2c3.png`. PNG-,
   JPG-, WebP-, GIF- og SVG-filer virker, op til 2 MB hver.

Billedet vises inden for et minut, og det samme gør en ændring eller en
fjernelse. Det tegnes opret, ikke drejet, for et fotografi tegnes ikke med
næsen opad. Flyets egenskab `picture_source` lyder så `override`.

Disse billeder kræver login på din Home Assistant, ligesom resten af den.
Kortet får hvert billede via et link, som Home Assistant signerer, og som
holder op med at virke efter et døgn; et nyt link laves inden da.

### Fotos

Når du peger på et fly, viser kortet et foto af det fra
[Planespotters.net](https://www.planespotters.net), hvis der er et, med
fotografens navn ved siden af. Klik på flyet for at se fotoet større; fotoet
linker til dets side på Planespotters.net. Der er intet at sætte op.

Fotoet slås kun op, når nogen peger på det fly, ikke for hvert fly i dit
område. Din Home Assistant spørger Planespotters.net ud fra flyets hex-kode.
Den gemmer svaret, et foto eller intet foto, i 12 timer, kun i hukommelsen, så
en genstart glemmer det. Browseren, der viser kortet, henter billedet direkte
fra Planespotters.net. Home Assistant henter, gemmer eller videresender ikke
noget billede.

⚠ Et foto viser flyet, som fotografen så det, måske i en tidligere bemaling
eller hos en tidligere operatør. Ikke alle fly har et foto på
Planespotters.net.

⚠ Der slås intet foto op for et fly, der flyver med en midlertidig adresse af
hensyn til privatlivet (FAA's program Privacy ICAO Address, USA), fordi den
hex-kode ikke identificerer flyet, og heller ikke for et spor uden en rigtig
hex-kode.

⚠ Fotos kan endnu ikke slås fra.

Hvert fly med en hex-kode har `marker_photo_lookup`: adressen på din Home
Assistant, hvor kortet beder om fotoet. Kun en, der er logget ind på din Home
Assistant, kan bruge den. Fotoene er deres fotografers værk: se [Tak og
licenser](#tak-og-licenser).

### Præsidentens fly

De fly, som USA's præsident bruger, vises, hvor de end er i verden, efter
deres hex-koder, aldrig efter kaldesignal, sammen med flyene fra 89th Airlift
Wing (kaldesignalerne SAM og VENUS) og de militærfly, der eskorterer et
præsidentfly. De kommer fra én forespørgsel i minuttet, som Live Track
Aircraft laver alligevel. Hvert bærer en egenskab `watch`, der siger, hvorfor
det vises, og et præsidentfly sit navn i `presidential_airframe`.

⚠ Et præsidentfly på kortet siger intet om, hvem der er om bord.

### EnforcementAircraft-listen og Live Track SALT

[EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)
er en offentlig liste over fly, der bruges af udlændinge- og føderale
ordensmyndigheder, hver post med sine kilder, udgivet af
StrausbergAutomationWorks. Inden for dit område blinker et fly, som listen
bekræfter ud fra sine kilder, rødt og blåt, og et passagerfly, der flyver
ICE Air-charterflyvninger blandt andet arbejde, har et fast skær. De beholdes
altid, også når dit område er fuldt.

Dens makker, [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
tegner de listede fly, hvor de end flyver, ikke kun i dit område. Installer
begge, og hver holder sig til sin del: Live Track Aircraft tegner hvert fly
inden for sit eget område, de listede medregnet, og Live Track SALT tegner de
listede fly alle andre steder. De deler én forespørgsel til kilderne, og intet
fly tegnes to gange.

---

## Alle entiteter, den opretter

For hvert område:

| Entitet | Hvad det er |
|---|---|
| `sensor.aircraft_in_range` | **Aircraft in range**: hvor mange fly der er inden for cirklen nu, alle sammen, også når der er flere end maksimum. Et andet områdes hedder `sensor.aircraft_in_range_2`, og så videre |
| `geo_location.aircraft_…` | én pr. fly, opkaldt efter dets hex-kode (`geo_location.aircraft_a1b2c3`); den kommer og går med flyet. Hver bærer `source: live_track_aircraft`, og dens tilstand er dens afstand fra midtpunktet i kilometer |

Sensorens egenskaber siger, hvad der sker: `published_count` (hvor mange der
er på kortet), `capped` (sand, når maksimum skar listen af), `source` (hvilket
netværk der svarede sidst), `source_backoff`, `route_artifact`,
`route_download`, `airport_table`, `airport_download`, `route_lookup`,
`watched_count`, `military_in_areas`, `military_by_area`, `followed_asked`,
`followed_found`, `follow_status`, `adsblol_key` og `enforcement_list`.

⚠ **Flymarkørerne har ikke noget unikt ID, med vilje.** Et område ser tusinder
af forskellige fly på et år, og en registerrække for hvert ville gøre Home
Assistant langsommere til at starte for ingenting. Derfor kan de ikke
omdøbes, skjules eller få et område i brugerfladen. Deres entitets-ID'er
kommer stadig fra hex-koden, så det samme fly altid får det samme ID. Sensoren
har et unikt ID og kan omdøbes.

⚠ **Din database.** Home Assistants recorder gemmer en ny række, hver gang en
entitet ændrer sig, og et fly i luften ændrer sig ved hver opdatering, som
standard hvert 15. sekund. På vores testsystem kostede en entitet som disse,
opdateret hvert 15. sekund, i september 2026 omkring 9,6 MB om dagen; ved 50
fly er det omkring 480 MB om dagen. Medmindre du vil have historikken for
hvert fly, så hold dem ude af recorderen. Tilføj dette til
`configuration.yaml`, og genstart så:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.aircraft_*
```

Har din `configuration.yaml` allerede et afsnit `recorder:`, så tilføj kun
mønsteret `geo_location.aircraft_*` til det, under `exclude:` og
`entity_globs:`. Et kortkort, der er sat til at tegne historik, har så intet
spor at tegne. `sensor.aircraft_in_range` er billig at beholde: dens
egenskaber antager få værdier, så recorderen gemmer dem én gang.

---

## Hvad den sender og henter

**Om din placering.** Midtpunktet og radiussen for hvert område sendes til
adsb.fi ved hver opdatering, som standard hvert 15. sekund, og til adsb.lol,
når adsb.fi ikke svarer. Midtpunktet sendes, som du har sat det, og det
begynder ved dit hjem: for at holde op med at sende dit hjem skal du flytte
midtpunktet væk fra det (**Konfigurér** → **Centre**) eller slette området.
De hex-koder og kaldesignaler, du følger, sendes til adsb.fi (eller adsb.lol)
én gang i minuttet, og din adsb.lol-nøgle kun til adsb.lol. Kaldesignalerne
for rutefly i dit område sendes til adsbdb, når FiledRoutesDB ikke har en rute
for dem. Når nogen peger på et fly på kortet, sendes dets hex-kode til
Planespotters.net, højst én gang hver 12. time for hvert fly, og browseren,
der viser kortet, henter fotoet derfra. Det kan endnu ikke slås fra. Intet
andet om dig sendes nogen steder hen. Hver tjeneste ser din internetadresse,
som enhver hjemmeside gør.

**Hvor meget.**

| Kilde | Hvad og hvor ofte | Efter en fejl |
|---|---|---|
| adsb.fi | hvert fly i din cirkel, ved hver opdatering (som standard hvert 15. sekund); én forespørgsel i minuttet for de fly, der følges efter hex-kode, og præsidentens fly; én for militærlisten; én for alle fulgte kaldesignaler samlet, kun når du følger nogen | spørger adsb.lol i stedet. En kilde, der afviser med HTTP 429, springes over i den tid, den beder om, eller i 1 minut, fordoblet op til 10 minutter |
| adsb.lol | de samme forespørgsler, kun så længe adsb.fi ikke svarer | det samme |
| adsbdb | én forespørgsel pr. nyt kaldesignal for et rutefly, som FiledRoutesDB ikke har en rute for, med mindst 1 sekunds mellemrum; et svar gemmes i 30 dage, et "ingen rute" i 24 timer. Svar gemmes kun i hukommelsen | spørges ikke igen i 15 minutter; alle forespørgsler holder pause i 15 minutter efter HTTP 429 |
| Planespotters.net | én forespørgsel efter et flys foto første gang, nogen peger på det, og derefter ingen for det fly i 12 timer. Svar gemmes kun i hukommelsen. Selve fotoet henter browseren, der viser kortet | efter HTTP 429 spørges der ikke efter fotos i den tid, Planespotters.net beder om, eller i 10 minutter; efter HTTP 403 i et døgn |
| FiledRoutesDB, fra GitHub | en lille kontrolsumfil én gang om dagen, efter kl. 14:00 Chicago-tid (USA); selve filen, omkring 4,6 MB, kun når den er ændret | prøves igen en time senere; den kopi, du har, bliver brugt, indtil den udløber |
| AirportZones, fra GitHub | en lille kontrolsumfil én gang om dagen; selve tabellen, omkring 4,8 MB, kun når den er ændret | prøves igen en time senere; den kopi, du har, bliver brugt |
| EnforcementAircraft, fra GitHub | en lille kontrolsumfil én gang i timen; selve listen, lille, kun når den er ændret | den kopi, du har, bliver brugt |
| FAA's luftfartøjsregister (USA) | registret, omkring 73 MB, én gang hver 7. dag, fra `registry.faa.gov` | prøves igen næste dag; den kopi, du har, bliver brugt |

De hentede filer deles med andre Live Track-moduler, så hver hentes én gang,
uanset hvor mange moduler du installerer. De ligger i Home Assistants mappe
`.storage` under navne, der begynder med `saw_`. Fjerner du Live Track
Aircraft, og intet andet Live Track-modul bruger dem, kan du slette dem
manuelt.

---

## Hjælp den med at vokse

Live Track Aircraft vokser stadig. Vi tilføjer rutekilder, datakilder og
oplysninger om fly, efterhånden som vi finder dem, og vi vil gerne vide, hvad
du kunne tænke dig næste gang.

### Foreslå noget

Mangler dit land, din lufthavn eller din flytype? Er noget forkert eller
svært at forstå? Fortæl os det på den måde, der er nemmest for dig:

* [**Udfyld en kort formular**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=da.yml)
  på dansk. Du skal have en gratis GitHub-konto.
* **Skriv en e-mail** til
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Ingen konto nødvendig.

Uanset hvad hjælper det, hvis du fortæller os:

* hvad du gerne vil se, og hvor i verden;
* et link til, hvor dataene offentliggøres, hvis du kender et (en side med
  åbne data, et offentligt feed, en tjenestes hjemmeside): ikke nødvendigt,
  men det hjælper;
* din Home Assistants sprog, hvis problemet er formuleringen eller en
  oversættelse.

Skriv på engelsk eller på dit eget sprog, hvad der er nemmest for dig.

### Tilføj det selv, med vores hjælp

Vil du selv tilføje noget, hjælper vi dig med det, fra det første spørgsmål
til den færdige udgivelse. Du behøver ikke være udvikler for at begynde:

* **En oversættelse.** Teksterne i opsætningsdialogen er en kort liste af
  sætninger i én tekstfil. Vi viser dig hvilken fil og hvilke linjer.
* **En ny datakilde.** Fortæl os, hvor dataene offentliggøres. Vi kan skrive
  koden sammen eller se din igennem.
* **Test, hvor du bor.** Installer den, se på din del af kortet, og fortæl os,
  hvad der er rigtigt, og hvad der ikke er.
* **En rettelse til denne README.** Hvis et trin ikke passede med det, du så,
  så fortæl os, hvad du så.

[**Fortæl os, hvad du har i tankerne**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=da.yml)
eller skriv til
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
så svarer vi med de næste skridt.

---

## Sprog

Denne README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), [Nederlands](README.nl.md),
[简体中文](README.zh-Hans.md), [Español](README.es.md),
[Italiano](README.it.md), **Dansk**. Hver oversat README er komplet.

Opsætningsdialogen og indstillingerne er indtil videre kun på engelsk, uanset
hvilket sprog din Home Assistant bruger. Taler du et andet sprog, kan du selv
oversætte dem: det er en kort liste med sætninger i én fil, og [vi hjælper dig
med det](#tilføj-det-selv-med-vores-hjælp).

Har du fundet en fejl i en oversættelse, eller har du brug for et andet sprog?
Fortæl os det på <https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues>,
eller [oversæt det med vores hjælp](#tilføj-det-selv-med-vores-hjælp).

---

## Tak og licenser

* **adsb.fi** (<https://adsb.fi>): flypositioner, åbne data kun til personlig,
  ikke-kommerciel brug, på betingelserne i dens
  [README om åbne data](https://github.com/adsbfi/opendata), som beder om at
  nævne adsb.fi og linke til dens forside. Ved at installere denne integration
  bruger du adsb.fi, og dens betingelser gælder for dig.
* **adsb.lol** (<https://adsb.lol>): flypositioner, under
  [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/).
  Ved at installere denne integration bruger du adsb.lol, og dens betingelser
  gælder for dig. Begge netværk drives af frivillige: støt dem, hvis du kan,
  ved at levere data fra en modtager.
* **FiledRoutesDB** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/FiledRoutesDB)):
  ruter fra flyveplaner indleveret til FAA (USA), data under CC BY 4.0, med
  FAA's LADD-liste anvendt før udgivelsen.
* **adsbdb** (<https://www.adsbdb.com>): ruter uden for FiledRoutesDB. Dens
  rutedata er David Taylors (Edinburgh) og Jim Masons (Glasgow) arbejde og må
  ikke kopieres eller genudgives uden tilladelse, så svar gemmes kun i
  hukommelsen, skrives aldrig til en fil, og hvert fly, der viser en rute fra
  adsbdb, nævner dem.
* **FAA's luftfartøjsregister** (Federal Aviation Administration, USA): ejer-
  og operatørnavne for fly registreret i USA, offentlige data fra USA's
  regering. FAA udelader selv de navne, den bliver bedt om at tilbageholde, før
  den udgiver filen.
* **OurAirports** (<https://ourairports.com>), via
  [AirportZones](https://github.com/StrausbergAutomationWorks/AirportZones):
  lufthavnes navne og positioner, under ODbL 1.0; tidszoner tilføjet af
  StrausbergAutomationWorks.
* **EnforcementAircraft** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)):
  listen over fly fra udlændinge- og føderale ordensmyndigheder, under ODbL
  1.0.
* **ADS-B Radar** (<https://adsb-radar.com>): flyikonerne, fra dens
  [sæt af SVG-flyikoner](https://adsb-radar.com/help/icons.html) af Jos
  Nutbroek, brugt på dens betingelser, som beder om dette link. Ikonerne er
  ikke omfattet af dette repositorys MIT-licens. Nogle ikoner er tegnet af
  StrausbergAutomationWorks i sættets stil og doneret til ADS-B Radar, så de
  er også under dens betingelser. Denne integration serverer ikonerne med en ny
  fyldfarve og kontur, skaleret efter flyklasse, og animerer nogle propeller og
  rotorer. Hver ændring står i [ATTRIBUTION.md](ATTRIBUTION.md).
* **Planespotters.net** (<https://www.planespotters.net>): flyfotoene, gennem
  dens [foto-API](https://www.planespotters.net/photo/api) og på dens
  betingelser. Hvert foto er fotografens værk, fotografen nævnes ved siden af
  det, og fotoet linker til sin side på Planespotters.net. Intet foto er
  kopieret ind i dette repository, og Home Assistant henter, gemmer eller
  videresender ikke noget billede. Ved at installere denne integration bruger
  du Planespotters.net, og dens betingelser gælder for dig.
* **Kortkortet** er [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, en kopi af [ha-map-card](https://github.com/nathan-gs/ha-map-card) af
  nathan-gs, MIT. Dets kortfliser og deres kildeangivelser står i dets README.

Ingen af disse organisationer har lavet eller godkendt denne integration.

**Kode**: MIT, i [LICENSE](LICENSE).

**For udviklere:** entiteterne følger Live Tracks fælles kortkontrakt, så hvert
modul vises på ét kort uden skabelonsensorer; positioner kommer gennem en
kildegrænseflade i `custom_components/live_track_aircraft/sources/`, så en
anden datastrøm kan tilføjes uden at røre entiteterne. Testene køres med
`python -m unittest discover -s tests`.

---

## Nøgleord

Home Assistant fly · Home Assistant flysporing · ADS-B · ADS-B-kort ·
flysporing · flyradar · fly over mig · MLAT · Mode S · flyruter ·
militærfly · Air Force One · helikoptere · aircraft · flight tracker ·
Flugzeuge · Flugverfolgung · avions · suivi des vols · vliegtuigen ·
vluchten volgen · 飞机 · 航班跟踪 · aviones · seguimiento de vuelos · aerei ·
tracciamento voli · adsb.fi · adsb.lol · adsbdb · FiledRoutesDB ·
FAA-register · OurAirports · ADS-B Radar · Planespotters.net · flyfotos ·
geo_location · kortkort · Lovelace · HACS · Marketplace · Markedsplads · Live
Track · LiveTrack · StrausbergAutomationWorks

---

**Anerkendelse.** StrausbergAutomationWorks anerkender de oprindelige folk i
alle de lande og farvande, dette kort dækker, over hele verden, og viser sin
respekt for deres ældste, fortidens og nutidens.
