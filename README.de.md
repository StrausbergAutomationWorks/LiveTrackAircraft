# Live Track Aircraft

[English](README.md) · **Deutsch** · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Alle Sprachen](#sprachen)

**Flugzeuge für Home Assistant, auf einer Karte.** Live Track Aircraft bringt
die Flugzeuge über Ihrem Zuhause, oder über jedem Ort der Welt, den Sie
wählen, auf Ihre Home-Assistant-Karte: jedes als sein eigener Typ gezeichnet,
in seine Flugrichtung gedreht, mit seinem Betreiber und, wenn bekannt, seinem
Ziel. Es kann auch gewählten Flugzeugen und Flügen folgen, wo immer sie sind,
und in Gebieten, die Sie nennen, nach Militärflugzeugen Ausschau halten.

> **Live Track Aircraft ist ein Modul von Live Track**, einer Familie von
> Home-Assistant-Integrationen, die alles, was sich bewegt, und das Wetter,
> durch das es sich bewegt, auf einer gemeinsamen Karte zeichnen: Flugzeuge,
> Schiffe, Züge und Wetter. Installieren Sie es allein oder neben den anderen
> Modulen ([Liste unten](#teil-von-live-track-die-anderen-module)).

> **Es wächst, und wir freuen uns über Ideen.** Live Track Aircraft deckt
> heute die ganze Welt ab, wo Freiwillige Empfänger betreiben, mit Routen und
> Haltern am ausführlichsten für die Vereinigten Staaten, und wir fügen weitere
> Routenquellen und Flugzeugdaten hinzu. Fehlt Ihres?
> [Schlagen Sie es vor](#helfen-sie-mit-es-zu-erweitern), oder fügen Sie es
> selbst hinzu: Wir helfen Ihnen dabei.

**Status: 0.1.1, veröffentlicht.** Per Link zum Marketplace hinzugefügt
([unten](#installation-schritt-für-schritt)); es ist noch nicht im Katalog
des Marketplace.

Eigene Arbeit von StrausbergAutomationWorks. Nicht verbunden mit und nicht
unterstützt von adsb.fi, adsb.lol, adsbdb, der Federal Aviation
Administration (Vereinigte Staaten), OurAirports, ADS-B Radar, einer
Fluggesellschaft oder einem Betreiber von Flugzeugen.

> ⚠ **Kein Sicherheitssystem.** Es zeigt öffentliche Daten, meist Sekunden
> alt und manchmal eine Minute oder mehr, und nur Flugzeuge, die die
> Empfänger von Freiwilligen gerade hören. Es ist nicht für die Navigation,
> nicht für die Staffelung von Flugzeugen und für keinen anderen betrieblichen
> Zweck gedacht.

---

## Inhalt

1. [Alles, was es kann](#alles-was-es-kann)
2. [Wo es funktioniert](#wo-es-funktioniert)
3. [Teil von Live Track: die anderen Module](#teil-von-live-track-die-anderen-module)
4. [Bevor Sie beginnen](#bevor-sie-beginnen)
5. [Installation, Schritt für Schritt](#installation-schritt-für-schritt)
6. [Einrichtung, Schritt für Schritt](#einrichtung-schritt-für-schritt)
7. [Kostenlose Schlüssel, die mehr freischalten, Schritt für Schritt](#kostenlose-schlüssel-die-mehr-freischalten-schritt-für-schritt)
8. [Die Karte auf ein Dashboard bringen](#die-karte-auf-ein-dashboard-bringen)
9. [In Automationen verwenden](#in-automationen-verwenden)
10. [Alles auf der Karte im Detail](#alles-auf-der-karte-im-detail)
11. [Alle Entitäten, die es anlegt](#alle-entitäten-die-es-anlegt)
12. [Was es sendet und herunterlädt](#was-es-sendet-und-herunterlädt)
13. [Helfen Sie mit, es zu erweitern](#helfen-sie-mit-es-zu-erweitern)
14. [Sprachen](#sprachen)
15. [Danksagungen und Lizenzen](#danksagungen-und-lizenzen)
16. [Stichwörter](#stichwörter)

---

## Alles, was es kann

### Auf der Karte, ohne Einrichtung

Sie legen ein **Gebiet** an: einen Mittelpunkt auf der Karte und einen Radius
darum. Es beginnt bei Ihrem Zuhause. Alles Folgende erscheint dann in diesem
Gebiet oder, wo die Tabelle es sagt, überall auf der Welt.

| Was | Wo | Woher |
|---|---|---|
| **Flugzeuge**: Verkehrsflugzeuge, Kleinflugzeuge, Hubschrauber, Segelflugzeuge, Ballone und Drohnen, jedes als sein eigener Typ gezeichnet und in seine Flugrichtung gedreht | in jedem Gebiet | adsb.fi, oder adsb.lol, wenn adsb.fi nicht antwortet |
| **Wer es betreibt**: die Fluggesellschaft, der Halter, oder der Typ, wenn sonst nichts bekannt ist, als Beschriftung der Markierung | jedes Flugzeug | das Rufzeichen der Fluggesellschaft; das FAA-Luftfahrzeugregister (Vereinigte Staaten) für Halter |
| **Farben, die sagen, wer fliegt**: Regierung, Polizei, Bundespolizeibehörden, Militär, Luftrettung und Hubschrauber, jeweils in eigener Farbe | jedes Flugzeug, wo es bekannt ist | das FAA-Luftfahrzeugregister (Vereinigte Staaten) und die Militärkennung des Datenstroms |
| **Routen**: wo das Flugzeug gestartet ist und wohin es fliegt, mit den Namen der Flughäfen und einer geschätzten Ankunftszeit | Flüge mit einem bei der FAA (Vereinigte Staaten) aufgegebenen Flugplan; anderswo, wenn adsbdb den Flug kennt | FiledRoutesDB, dann adsbdb |
| **Die Flugzeuge des Präsidenten der Vereinigten Staaten**, mit den Flugzeugen des 89th Airlift Wing und den Militärflugzeugen, die sie begleiten | überall auf der Welt | adsb.fi und seine Militärliste |
| **Flugzeuge auf der öffentlichen EnforcementAircraft-Liste** (Einwanderungs- und Bundespolizeibehörden), mit blinkenden Lichtern | in jedem Gebiet | die EnforcementAircraft-Liste |
| **Militärflugzeuge in Ihren Beobachtungsgebieten**: jedes Flugzeug, das der Datenstrom als militärisch kennzeichnet, in bis zu zehn Kreisen, die Sie nennen, auch wenn Ihr Gebiet voll ist. Freiwillig: Sie tippen die Kreise in den Einrichtungsdialog | überall auf der Welt | die Militärliste von adsb.fi |
| **Flugzeuge und Flüge, denen Sie folgen**: Ihr eigenes Flugzeug, die Flotte eines Vereins oder der Flug eines Familienmitglieds. Freiwillig: Sie tippen ihre Codes in den Einrichtungsdialog | überall auf der Welt | adsb.fi |
| **Ihr eigenes Bild für ein Flugzeug**, anstelle seines Symbols | überall, wo dieses Flugzeug gezeigt wird | ein Bild, das Sie in einen Ordner legen ([wie](#ihr-eigenes-bild-für-ein-flugzeug)) |

### Mit Ihrem eigenen kostenlosen Schlüssel oder Konto freigeschaltet

| Kostenloser Schlüssel oder Konto | Was es hinzufügt |
|---|---|
| **adsb.lol**-Schlüssel | mehr Anfragen am Tag an adsb.lol, die zweite Quelle, damit die Karte auch bei einem langen Ausfall von adsb.fi weiterläuft |

Jeder ist in wenigen Minuten beschafft: [Schritt für Schritt unten](#kostenlose-schlüssel-die-mehr-freischalten-schritt-für-schritt).

---

## Wo es funktioniert

| Region | Was Sie bekommen | Woher | Benötigt |
|---|---|---|---|
| **Die ganze Welt** | Positionen von Flugzeugen, wo Freiwillige Empfänger betreiben: dicht über Europa und Nordamerika, dünner anderswo, und wenig oder nichts weit draußen auf See | adsb.fi, adsb.lol | nichts |
| **Die ganze Welt** | Namen der Flughäfen auf Routen und ihre Zeitzonen für die Ankunftszeit | OurAirports, über die Tabelle AirportZones | nichts |
| **Die ganze Welt** | Routen vieler Linienflüge, geprüft daran, wo das Flugzeug tatsächlich ist | adsbdb | nichts |
| **Nordamerika**: Vereinigte Staaten | Namen von Haltern und Betreibern der in den Vereinigten Staaten registrierten Flugzeuge, und die Farben für Regierungs- und Polizeiflugzeuge | das FAA-Luftfahrzeugregister | nichts |
| **Nordamerika**: Vereinigte Staaten | Routen der bei der FAA aufgegebenen Flüge, auch internationaler Flüge von und nach den Vereinigten Staaten | FiledRoutesDB | nichts |

Nicht auf der Liste? [Sagen Sie es uns](#helfen-sie-mit-es-zu-erweitern). Wo
jemand die Daten offen veröffentlicht, sehen wir uns an, sie hinzuzufügen.

⚠ **Die Abdeckung ist gut, wo Empfänger sind, und fehlt, wo keine sind.** Ein
Flugzeug erscheint nur, wenn der Empfänger eines Freiwilligen es hört, oder
wenn mehrere Empfänger zusammen es orten können. Keine Einstellung kann eine
Abdeckung schaffen, die es nicht gibt. **Ein leerer Himmel auf der Karte kann
heißen, dass keine Empfänger in Ihrer Nähe sind, nicht, dass keine Flugzeuge
fliegen.**

⚠ **Routen gibt es vor allem für die Vereinigten Staaten.** FiledRoutesDB
enthält nur bei der FAA aufgegebene Flugpläne. Anderswo kommt eine Route von
adsbdb, das viele Linienflüge und wenige andere kennt, deshalb zeigen
außerhalb der Vereinigten Staaten viele Flugzeuge keine Route.

⚠ **Namen von Haltern gibt es nur für in den Vereinigten Staaten registrierte
Flugzeuge.** Ein in einem anderen Land registriertes Flugzeug zeigt seine
Fluggesellschaft aus dem Rufzeichen, oder seinen Typ.

---

## Teil von Live Track: die anderen Module

Live Track ist eine Reihe von Home-Assistant-Integrationen, eine für jede Art
von beweglichem Ding, alle auf derselben Kartenkarte gezeichnet. Jede
funktioniert allein; zusammen ergeben sie ein lebendiges Bild. Sie teilen sich
die Kartenkarte und eine Python-Bibliothek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
sodass eine weitere installierte Integration keine zusätzlichen Anfragen an
eine Quelle stellt, die eine andere bereits liest.

| Modul | Was es auf die Karte bringt | Status |
|---|---|---|
| **Live Track Aircraft** | Flugzeuge über Ihnen per ADS-B, mit Routen und Typsymbolen (dieses Modul) | veröffentlicht |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | Schiffe und Boote per AIS, in Ihrer Nähe oder irgendwo | veröffentlicht |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | Nahverkehrszüge in Nordamerika, Europa und Australien | veröffentlicht |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | Intercity- und Fernzüge in Nordamerika, Europa und Australien | veröffentlicht |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | Flugzeuge und Schiffe der Einwanderungs- und Bundespolizeibehörden, aus öffentlichen Listen | veröffentlicht |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | Wetter, Stürme und Naturgefahren | veröffentlicht |
| Live Track Stations | Abfahrtstafeln und „Zeit zu gehen“-Hinweise für jeden Bahnhof | geplant |
| Live Track Satellites | Satelliten, die über Sie hinwegziehen | geplant |
| Live Track Freight Trains | Güter- und Arbeitszüge, wo Bahnen sie veröffentlichen | geplant |
| Live Track Transit | Stadtbusse, Straßenbahnen, Fähren und U-Bahnen | geplant |
| Live Track Intercity Buses | Fernbusse und Regionalbusse | geplant |
| Live Track Commuter Buses | Pendlerbusse | geplant |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | die gemeinsame Kartenkarte, auf der jedes Modul zeichnet | veröffentlicht, mit jedem Modul installiert |

Alles ist kostenlos und quelloffen. Nichts wird für Sponsoren zurückgehalten.

---

## Bevor Sie beginnen

* **Home Assistant** 2026.11 oder neuer.
* **Der Marketplace** (HACS) in Ihrem Home Assistant, um es auf dem einfachen
  Weg zu installieren und zu aktualisieren. Ohne ihn können Sie die Dateien
  von Hand kopieren.
* **Internetzugang** für Home Assistant: Alles kommt aus öffentlichen Quellen.
* **Freiwillig: auto-entities** aus dem Marketplace, um die Markierungen auf
  die Karte zu bringen (siehe
  [Die Karte auf ein Dashboard bringen](#die-karte-auf-ein-dashboard-bringen)).
* Nichts zu bezahlen und kein Konto nötig. Der adsb.lol-Schlüssel oben ist
  freiwillig.
* Home Assistant installiert die zwei Python-Pakete, die es braucht
  (`saw-livetrack` und `tzfpy`), selbst, wenn die Integration zum ersten Mal
  lädt.

---

## Installation, Schritt für Schritt

### Über den Marketplace (empfohlen)

Live Track Aircraft ist noch nicht im Katalog des Marketplace. Fügen Sie es
per Link hinzu:

1. Öffnen Sie in Home Assistant **Einstellungen → Marketplace** (HACS).
2. Wählen Sie **Über Link hinzufügen** (oder das Dreipunktmenü →
   **Benutzerdefinierte Repositorys**).
3. Geben Sie `StrausbergAutomationWorks/LiveTrackAircraft` ein. Wenn nach dem
   Typ gefragt wird, wählen Sie **Integration**.
4. Suchen Sie **Live Track Aircraft** in der Liste und wählen Sie
   **Herunterladen** oder **Installieren**.
5. **Starten Sie Home Assistant neu**: **Einstellungen → System → Reparaturen**
   bietet den Neustart an, oder nutzen Sie **Einstellungen → System → Neu
   starten**.

Der Marketplace bietet dann jede neue Veröffentlichung als Aktualisierung an.

### Von Hand

1. Laden Sie den Quellcode der
   [neuesten Veröffentlichung](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/releases/latest)
   herunter.
2. Kopieren Sie dessen Ordner `custom_components/live_track_aircraft` in den
   Ordner `custom_components` Ihres Home-Assistant-Konfigurationsordners
   (legen Sie `custom_components` an, falls es ihn nicht gibt).
3. Starten Sie Home Assistant neu.

Zum Aktualisieren von Hand ersetzen Sie den Ordner durch den der neuen
Veröffentlichung und starten neu.

---

## Einrichtung, Schritt für Schritt

Der Einrichtungsdialog ist auf Englisch. Seine Felder sind hier so genannt,
wie er sie zeigt.

1. Öffnen Sie **Einstellungen → Geräte & Dienste**.
2. Wählen Sie **Integration hinzufügen** (unten rechts) und suchen Sie nach
   **Live Track Aircraft**.
3. **Centre** (Mittelpunkt): Ziehen Sie die Markierung in die Mitte des
   Himmels, den Sie beobachten möchten. Sie beginnt bei Ihrem Zuhause.
4. **Radius (km)**: wie weit vom Mittelpunkt Flugzeuge gezeigt werden, von 1
   bis 463 km (0,6 bis 288 Meilen). Im Zweifel lassen Sie 56 km (35 Meilen).
5. **Update interval (seconds)** (Aktualisierungsabstand): Lassen Sie 15. Die
   Quellen lehnen häufigere Anfragen ab.
6. **Maximum aircraft published** (höchstens veröffentlichte Flugzeuge):
   Lassen Sie 250. Es ist eine Sicherheitsgrenze, kein Weg, weniger Flugzeuge
   zu zeigen.
7. Lassen Sie die vier freiwilligen Felder vorerst leer. Jedes ist unten
   erklärt.
8. Wählen Sie **OK**.

Das ist alles. Flugzeuge erscheinen innerhalb einer Minute. Jedes Gebiet ist
ein Eintrag, betitelt mit seinem Mittelpunkt und Radius, zum Beispiel
`39.817, -84.050 - 56 km`. Um ein zweites Gebiet zu beobachten, fügen Sie die
Integration noch einmal mit einem anderen Mittelpunkt oder Radius hinzu.
Derselbe Mittelpunkt und Radius zweimal wird abgelehnt.

Routen, Flughafennamen und Halter füllen sich in den ersten Minuten, während
die Dateien, aus denen sie kommen, heruntergeladen werden
([Was es sendet und herunterlädt](#was-es-sendet-und-herunterlädt)).

### Ändern, was es zeigt: die Optionen

Öffnen Sie **Einstellungen → Geräte & Dienste → Live Track Aircraft →
Konfigurieren** (das Zahnrad) bei dem Gebiet, das Sie ändern möchten. Jede
Option in einfachen Worten:

| Option | Was sie bewirkt | Standard |
|---|---|---|
| **Centre** | verschiebt das Gebiet; sein Titel folgt | Ihr Zuhause |
| **Radius (km)** | wie weit vom Mittelpunkt Flugzeuge gezeigt werden, 1 bis 463 km (0,6 bis 288 Meilen) | 56 km (35 Meilen) |
| **Update interval (seconds)** | wie oft Positionen abgefragt werden, 15 bis 3.600 Sekunden | 15 |
| **Maximum aircraft published** | eine Sicherheitsgrenze, 1 bis 1.000; sind mehr Flugzeuge im Kreis, werden die nächsten behalten. Flugzeuge, denen Sie folgen, Flugzeuge in Ihren militärischen Beobachtungsgebieten und Flugzeuge auf der EnforcementAircraft-Liste werden immer behalten | 250 |
| **Military watch areas** | Kreise, in denen jedes Militärflugzeug gezeigt wird ([wie](#militärische-beobachtungsgebiete)) | leer |
| **Aircraft to follow (hex codes)** | Flugzeuge, denen überall gefolgt wird, nach ihrem Hex-Code ([wie](#flugzeuge-und-flüge-denen-sie-folgen)) | leer |
| **Flights to follow (call signs)** | Flüge, denen überall gefolgt wird, nach ihrem Rufzeichen (derselbe Abschnitt) | leer |
| **adsb.lol API key** | Ihr eigener Schlüssel für adsb.lol ([wie Sie einen bekommen](#kostenlose-schlüssel-die-mehr-freischalten-schritt-für-schritt)) | leer |

Leeren Sie eines der vier freiwilligen Felder, um diesen Teil abzuschalten.

---

## Kostenlose Schlüssel, die mehr freischalten, Schritt für Schritt

All diese sind kostenlos und persönlich: Jede Person, die Live Track Aircraft
installiert, bekommt ihren eigenen. Fügen Sie jeden unter **Einstellungen →
Geräte & Dienste → Live Track Aircraft → Konfigurieren** ein.

### adsb.lol (mehr Anfragen an die zweite Quelle, die ganze Welt)

Live Track Aircraft fragt zuerst adsb.fi und fragt adsb.lol nur, solange
adsb.fi nicht antwortet. Ohne Schlüssel erlaubt adsb.lol 500 Anfragen am Tag
von einer Internetadresse, die ein Ausfall von adsb.fi in etwa zwei Stunden
aufbrauchen kann. Ein Schlüssel hebt diese Grenze an. Zum Anfangen brauchen
Sie keinen.

1. Öffnen Sie <https://www.adsb.lol/request> und beantragen Sie mit dem
   Formular dort einen kostenlosen Schlüssel. Die Dokumentation von adsb.lol
   gibt diesem Schlüssel 1.000 Anfragen am Tag.
2. Wenn Sie adsb.lol mit einem eigenen Empfänger beliefern, nehmen Sie
   stattdessen Ihren Feeder-Schlüssel: Die Dokumentation von adsb.lol gibt
   ihm 7.200 Anfragen am Tag. Ihre Schlüssel finden Sie unter **My keys** bei
   adsb.lol (<https://www.adsb.lol/mmb>).
3. Fügen Sie den Schlüssel in **adsb.lol API key** ein und wählen Sie **OK**.

Der Schlüssel wird nur an adsb.lol gesendet. Lehnt adsb.lol ihn ab (falsch
oder abgelaufen), arbeitet Live Track Aircraft ohne ihn weiter, und
`sensor.aircraft_in_range` des Gebiets zeigt `refused` im Attribut
`adsblol_key`, bis Sie den Schlüssel ändern. Sonst zeigt es `set`, oder
`none` ohne Schlüssel. Kein Passwort und kein Geheimnis ist nötig.

---

## Die Karte auf ein Dashboard bringen

Die Karte ist [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
die Karte, auf der jedes Live-Track-Modul zeichnet. **Sie wird mit Live Track
Aircraft installiert**: nichts herunterzuladen, nichts zu kopieren, keine
Ressource hinzuzufügen.

1. Öffnen Sie ein Dashboard, wählen Sie den Stift (**Dashboard bearbeiten**),
   dann **Karte hinzufügen**.
2. Scrollen Sie ganz nach unten und wählen Sie **Manuell**.
3. Fügen Sie dies ein und wählen Sie **Speichern**:

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

Die Markierungen brauchen
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities) aus dem
Marketplace. Sind andere Live-Track-Module installiert, fügen Sie für jede
ihrer Quellen einen weiteren Filter `- domain: geo_location` hinzu
(`live_track_ships`, `live_track_weather` und so weiter).

**Auf der Karte:**

* Jedes Flugzeug ist als sein eigener Typ gezeichnet, in seine Flugrichtung
  gedreht, und bewegt sich gleichmäßig zwischen den Positionen, die es meldet.
* Seine Beschriftung ist das Rufzeichen des Flugs (`UAL308`), sonst sein
  Betreiber (`Lewis University`), sonst sein Typ (`Cessna 172 Skyhawk`).
* **Zeigen** Sie auf ein Flugzeug, um seine Fluggesellschaft oder seinen
  Betreiber zu sehen und, wenn eine Route bekannt ist, die Route und wie viele
  Minuten es bis zur Ankunft braucht. **Klicken** Sie darauf für alle Details.

Sind die Ressourcen Ihrer Dashboards in YAML festgelegt
(`lovelace: resource_mode: yaml`), kann nichts für Sie registriert werden:
Ein Eintrag unter **Reparaturen** nennt dann die genaue Zeile, die Sie
hinzufügen. Eine Karte, die Sie selbst über den Marketplace installiert
haben, bleibt unberührt. Werden die Dateien der Integration entfernt, während
ihre Gebiete noch eingerichtet sind, und ist kein anderes Live-Track-Modul
installiert, entfernen Sie die Zeile der Karte selbst unter **Einstellungen →
Dashboards → Ressourcen**. Jede andere Kartenkarte, die
`geo_location`-Entitäten zeigt, zeigt die Flugzeuge auch, als einfache
Markierungen.

---

## In Automationen verwenden

Alles ist eine gewöhnliche Home-Assistant-Entität, daher funktioniert der
Automationseditor damit, ganz ohne Code.

**Eine Benachrichtigung auf dem Telefon, wenn ein Militärflugzeug in einem
Ihrer militärischen Beobachtungsgebiete ist:**

1. **Einstellungen → Automationen & Szenen → Automation erstellen → Neue
   Automation erstellen**.
2. **Sobald**: **Auslöser hinzufügen** → **Entität** → **Numerischer
   Zustand**. Wählen Sie die Entität **Aircraft in range**, das **Attribut**
   **Military in areas** (`military_in_areas`) und **Über** `0`.
3. **Dann**: **Aktion hinzufügen**, suchen Sie die Benachrichtigungsaktion
   Ihres Telefons (sie trägt den Namen Ihres Telefons), und geben Sie eine
   Nachricht ein, zum Beispiel:

   ```text
   Ein Militärflugzeug ist in Ihrem Beobachtungsgebiet
   ```

4. **Speichern**.

Dafür brauchen Sie mindestens ein militärisches Beobachtungsgebiet
([wie](#militärische-beobachtungsgebiete)).

**Weitere Ideen:** eine Benachrichtigung, wenn der Flug eines
Familienmitglieds in der Luft ist, wenn das Attribut `followed_found` über 0
steigt; ein Licht, das angeht, wenn mehr als 20 Flugzeuge über Ihrem Zuhause
in Frankfurt (Deutschland) sind; eine Anzeige auf dem Dashboard, wie viele
Flugzeuge über Ihrem Flugplatz in Queensland (Australien) sind, aus
`sensor.aircraft_in_range`; eine Nachricht, wenn das Flugzeug Ihres Vereins
startet, wenn seine eigene Entität (`geo_location.aircraft_` und sein
Hex-Code) erscheint.

---

## Alles auf der Karte im Detail

### Flugzeuge

Flugzeuge senden ihre Position per Funk, ein System namens ADS-B. Freiwillige
auf der ganzen Welt betreiben Empfänger und teilen, was sie hören, über
Gemeinschaftsnetze. Live Track Aircraft fragt eines davon, adsb.fi, nach
jedem Flugzeug in Ihrem Kreis, standardmäßig alle 15 Sekunden. Wenn adsb.fi
nicht antwortet, oder mit weit weniger Flugzeugen als einen Moment zuvor,
fragt es adsb.lol. Wo mehrere Empfänger ein Flugzeug hören, das seine eigene
Position nicht sendet, können die Netze es trotzdem orten (Multilateration,
MLAT).

Jedes Flugzeug ist eine Markierung, benannt nach seinem Hex-Code: der
sechsstelligen Adresse, die sein Transponder sendet, die zum Flugzeug gehört
und sich nicht ändert. Die Markierung erscheint, wenn das Flugzeug in Ihren
Kreis kommt, und wird entfernt, wenn es ihn verlässt.

Die Beschriftung ist der nützlichste bekannte Name, in dieser Reihenfolge:

| Das Flugzeug hat | Die Beschriftung zeigt | Beispiel |
|---|---|---|
| das Rufzeichen eines Flugs | das Rufzeichen | `UAL308` |
| sonst einen bekannten Betreiber | den Betreiber | `Lewis University` |
| sonst einen bekannten Typ | den Typ | `Cessna 172 Skyhawk` |
| nichts davon | das Kennzeichen, den Typcode oder den Hex-Code | `N12345` |

⚠ Nicht gezeigt: Flugzeuge am Boden, Fahrzeuge auf Flughäfen, und reine
Radarspuren ohne Kennung. Ein Flugzeug, das nicht sendet oder wo kein
Empfänger es hört, kann nicht gezeigt werden.

An jedem Flugzeug: `identity` (der Hex-Code), `callsign`, `registration`,
`aircraft_type`, `aircraft_name`, `operator`, `altitude_m`, `speed_kmh`,
`vertical_rate_ms`, `course_deg`, `squawk`, `emitter_category`,
`is_military`, `is_government`, `last_seen`.

### Farben und Symbole

Jedes Flugzeug ist als sein eigener Typ gezeichnet: ein Verkehrsflugzeug, ein
Geschäftsreiseflugzeug, ein einmotoriges Kleinflugzeug, ein zweimotoriges, ein
Hubschrauber, ein Kipprotorflugzeug, ein Segelflugzeug, ein Ballon, eine Drohne
und viele mehr, in der Größe nach seiner Klasse. Propeller und Rotoren drehen
sich. Das Symbol ist in die Flugrichtung gedreht; ein langsames Flugzeug
behält seine letzte Richtung, statt sich zu drehen.

Die Farbe sagt, wer fliegt, wo das bekannt ist:

| Farbe | Wer |
|---|---|
| hellgrau | die meisten Flugzeuge |
| mintgrün | Hubschrauber und andere Drehflügler |
| bernsteinfarben | Regierungsflugzeuge und Luftrettung |
| blau | Bundespolizeibehörden |
| armeegrün | das Militär und die Küstenwache |
| weiß, mit blinkenden blauen Lichtern | Polizei |
| blinkende rote und blaue Lichter | Flugzeuge auf der EnforcementAircraft-Liste ([unten](#die-enforcementaircraft-liste-und-live-track-salt)) |
| ein gleichmäßiges Leuchten | ein Verkehrsflugzeug, das unter anderem Charterflüge für ICE Air fliegt |

⚠ Wem ein Flugzeug gehört, ist vor allem für in den Vereinigten Staaten
registrierte Flugzeuge bekannt, aus dem FAA-Register. Anderswo kommt die Farbe
nur aus der Militärkennung des Datenstroms und dem Typ des Flugzeugs.

### Routen und Ankunftszeiten

Eine Route zeigt, wo das Flugzeug gestartet ist und wohin es fliegt, mit den
Namen beider Flughäfen, und eine geschätzte Ankunftszeit. Sie kommt aus zwei
Quellen:

1. **FiledRoutesDB**, eine öffentliche Datei mit bei der FAA (Vereinigte
   Staaten) aufgegebenen Flugplänen, erstellt und veröffentlicht von
   StrausbergAutomationWorks und einmal am Tag heruntergeladen. Jede Route
   wird daran geprüft, wo das Flugzeug ist und in welche Richtung es fliegt.
   Eine Route, die nicht passt, wird trotzdem gezeigt und in `route_check`
   als nicht passend markiert.
2. **adsbdb**, nur gefragt, wenn FiledRoutesDB für das Rufzeichen keine Route
   hat, einmal pro Rufzeichen. Seine Antwort wird nur gezeigt, wenn sie dazu
   passt, wo das Flugzeug tatsächlich ist.

Flugzeuge, deren Halter die FAA gebeten haben, ihre Flüge nicht öffentlich zu
zeigen (die LADD-Liste der FAA, Limiting Aircraft Data Displayed), werden aus
FiledRoutesDB entfernt, bevor die Datei veröffentlicht wird. Live Track
Aircraft löscht seine Kopie, wenn die Datei abläuft oder wenn die LADD-Liste,
mit der sie erstellt wurde, älter als 14 Tage ist, damit es nie Routen zeigt,
die mit einer alten Liste gefiltert wurden.

Die Ankunftszeit ist eine Schätzung, kein Flugplan: die verbleibende
Entfernung in gerader Linie, bei der Geschwindigkeit des Flugzeugs, wenn es im
Reiseflug ist, und sonst bei einer typischen Geschwindigkeit seiner Klasse.
Warteschleifen, Anflug und Rollen werden nicht mitgerechnet.

An jedem Flugzeug mit Route: `origin_icao`, `destination_icao`,
`origin_name`, `destination_name`, `route_source`, `route_check`,
`arrival_estimated_at`.

### Militärische Beobachtungsgebiete

Jedes Flugzeug, das der Datenstrom als militärisch kennzeichnet, in Kreisen,
die Sie wählen, überall auf der Welt, auch wenn Ihr Gebiet voll ist.

1. Öffnen Sie **Einstellungen → Geräte & Dienste → Live Track Aircraft →
   Konfigurieren** bei einem Gebiet.
2. Tippen Sie in **Military watch areas** jeden Kreis als
   `latitude,longitude,km` (Breite, Länge, Kilometer) und trennen Sie Kreise
   mit Semikolons, zum Beispiel `39.81,-84.04,150; 34.0,-117.8,463`. Bis zu
   zehn Kreise, jeder von 1 bis 2.000 km (0,6 bis 1.243 Meilen). Schreiben Sie
   Dezimalzahlen mit Punkt.
3. Wählen Sie **OK**.

Die Militärflugzeuge darin erscheinen innerhalb einer Minute und bewegen sich
einmal pro Minute. Jedes trägt `watch: military area`.
`sensor.aircraft_in_range` des Gebiets zählt sie in `military_in_areas` und
pro Kreis in `military_by_area`. Leeren Sie das Feld, um aufzuhören.

⚠ Es zeigt nur, was sendet und als militärisch gekennzeichnet ist.
Militärflüge können mit ausgeschaltetem Transponder fliegen, und ein
Militärflugzeug mit ziviler Registrierung ist nicht gekennzeichnet.

### Flugzeuge und Flüge, denen Sie folgen

Live Track Aircraft kann Flugzeugen, die Sie wählen, überall auf der Welt
folgen, nicht nur in Ihrem Kreis: Ihrem eigenen Flugzeug, der Flotte eines
Vereins oder einer Firma, oder dem Flug eines Familienmitglieds.

1. Öffnen Sie **Einstellungen → Geräte & Dienste → Live Track Aircraft →
   Konfigurieren** bei dem Gebiet, bei dem sie gezeigt werden sollen.
2. Füllen Sie **Aircraft to follow (hex codes)**, **Flights to follow (call
   signs)** oder beide aus.
3. Wählen Sie **OK**. Sie erscheinen innerhalb etwa einer Minute.

**Ein Code pro Flugzeug genügt.** Wählen Sie danach, was Sie verfolgen
möchten:

| Um zu folgen | Nehmen Sie | Beispiel |
|---|---|---|
| einem Flugzeug, welchen Flug es auch fliegt (Ihr eigenes Flugzeug, eine Flotte) | seinen **Hex-Code** | `a1b2c3` |
| einem Flug, welches Flugzeug ihn auch fliegt (die Reise eines Familienmitglieds) | sein **Rufzeichen** | `UAL1234` |

Beide Codes für dasselbe Flugzeug einzugeben schadet nicht (es wird einmal
gezeichnet), bringt aber nichts.

**Die Codes eingeben:**

* Trennen Sie Codes mit Kommas: `a1b2c3, a4b5c6, a7b8c9`. Leerzeichen oder
  Semikolons zwischen Codes funktionieren auch.
* Ein Hex-Code hat genau sechs Zeichen: die Ziffern 0 bis 9 und die Buchstaben
  a bis f, groß oder klein geschrieben.
* Ein Rufzeichen hat 2 bis 8 Buchstaben und Ziffern, so eingegeben, wie das
  Flugzeug es sendet, ohne Leerzeichen oder Bindestrich: `UAL1234`, nicht
  `UA 1234` oder `UAL-1234`.
* Bis zu 100 Hex-Codes und 100 Rufzeichen. Ein doppelt eingegebener Code zählt
  einmal.
* Ist ein Code falsch, lehnt der Dialog dieses Feld ab, sagt, wie ein
  richtiger Code aussieht, und speichert nichts, bis er korrigiert ist.

**Die Codes finden.** Jedes Flugzeug auf der Karte trägt seinen Hex-Code im
Attribut `identity` und sein Rufzeichen im Attribut `callsign`. Für ein in den
Vereinigten Staaten registriertes Flugzeug zeigt die N-Nummer-Suche des
FAA-Registers den Hex-Code als „Mode S Code (Base 16 / Hex)“. Bei einem
Linienflug ist das Rufzeichen meist der dreibuchstabige Code der
Fluggesellschaft und die Flugnummer, nicht das, was auf dem Ticket steht:

| Ticket | Rufzeichen |
|---|---|
| United UA 1234 | `UAL1234` |
| Delta DL 89 | `DAL89` |
| American AA 100 | `AAL100` |

Manche Fluggesellschaften senden ein Rufzeichen, das nicht die Flugnummer ist.
Erscheint ein Flug nicht, suchen Sie ihn auf einer Live-Flugkarte und kopieren
Sie das dort gezeigte Rufzeichen. Ein Rufzeichen wird wiederverwendet: Dasselbe
Rufzeichen morgen ist eine andere Reise und vielleicht ein anderes Flugzeug.
Es bleibt verfolgt, bis Sie es entfernen.

**Was Sie sehen.** Jedes verfolgte Flugzeug wird mit seinem üblichen Symbol und
seiner Beschriftung gezeichnet, wo immer es ist, auch wenn Ihr Gebiet voll
ist. Sein Attribut `watch` lautet `followed`, und `outside_radius` sagt, ob es
außerhalb Ihres Kreises ist. Außerhalb Ihres Kreises bewegt es sich einmal pro
Minute; innerhalb so oft wie alles andere. `sensor.aircraft_in_range` des
Gebiets zeigt `followed_asked` (wie vielen Codes Sie folgen),
`followed_found` (wie viele davon jetzt in der Luft sind) und `follow_status`
(die letzte Rufzeichen-Anfrage: `ok`, oder was schiefging).

**Um aufzuhören**, entfernen Sie den Code oder leeren das Feld und wählen
**OK**.

⚠ Nur Flugzeuge, die ADS-B senden oder die MLAT orten kann, können gefunden
werden. Ein Flugzeug am Boden oder außerhalb der Empfängerabdeckung wird nicht
gezeigt, und `followed_found` zählt es nicht. Flugpläne und Verspätungen nach
Flugnummer gehören nicht dazu.

### Ihr eigenes Bild für ein Flugzeug

Setzen Sie ein Bild Ihrer Wahl anstelle des Symbols eines Flugzeugs, zum
Beispiel Ihres eigenen.

1. Legen Sie in Ihrem Home-Assistant-Konfigurationsordner (dem Ordner mit
   `configuration.yaml`) einen Ordner namens `live_track_aircraft_pictures`
   an.
2. Legen Sie das Bild hinein, benannt nach dem Hex-Code des Flugzeugs:
   `a1b2c3.png`. PNG-, JPG-, WebP-, GIF- und SVG-Dateien funktionieren, bis
   2 MB je Datei.

Das Bild erscheint innerhalb einer Minute, ebenso eine Änderung oder ein
Entfernen. Es wird aufrecht gezeichnet, nicht gedreht, weil ein Foto nicht mit
der Nase nach oben gezeichnet ist. Das Attribut `picture_source` des Flugzeugs
lautet dann `override`.

⚠ Diese Bilder werden ohne Anmeldung ausgeliefert, wie die Symbole: Jeder, der
Ihr Home Assistant über seine Adresse erreichen kann, kann sie öffnen. Legen
Sie dort kein privates Bild ab.

### Die Flugzeuge des Präsidenten

Die Flugzeuge, die der Präsident der Vereinigten Staaten nutzt, werden
überall auf der Welt gezeigt, nach ihren Hex-Codes, nie nach Rufzeichen,
zusammen mit den Flugzeugen des 89th Airlift Wing (Rufzeichen SAM und VENUS)
und den Militärflugzeugen, die ein Flugzeug des Präsidenten begleiten. Sie
kommen aus einer Anfrage pro Minute, die Live Track Aircraft ohnehin stellt.
Jedes trägt ein Attribut `watch`, das sagt, warum es gezeigt wird, und ein
Flugzeug des Präsidenten seinen Namen in `presidential_airframe`.

⚠ Ein Flugzeug des Präsidenten auf der Karte sagt nichts darüber, wer an Bord
ist.

### Die EnforcementAircraft-Liste und Live Track SALT

[EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)
ist eine öffentliche Liste von Flugzeugen, die von Einwanderungs- und
Bundespolizeibehörden genutzt werden, jeder Eintrag mit seinen Quellen,
veröffentlicht von StrausbergAutomationWorks. In Ihrem Gebiet blinkt ein
Flugzeug, das die Liste aus ihren Quellen bestätigt, rot und blau, und ein
Verkehrsflugzeug, das unter anderem Charterflüge für ICE Air fliegt, leuchtet
gleichmäßig. Sie werden immer behalten, auch wenn Ihr Gebiet voll ist.

Sein Begleiter, [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
zeichnet die gelisteten Flugzeuge, wo immer sie fliegen, nicht nur in Ihrem
Gebiet. Installieren Sie beide, und jedes bleibt bei seinem Teil: Live Track
Aircraft zeichnet jedes Flugzeug in seinem eigenen Gebiet, die gelisteten
eingeschlossen, und Live Track SALT zeichnet die gelisteten Flugzeuge überall
sonst. Sie teilen sich eine Anfrage an die Quellen, und kein Flugzeug wird
zweimal gezeichnet.

---

## Alle Entitäten, die es anlegt

Für jedes Gebiet:

| Entität | Was sie ist |
|---|---|
| `sensor.aircraft_in_range` | **Aircraft in range**: wie viele Flugzeuge jetzt im Kreis sind, alle, auch wenn es mehr als das Maximum sind. Der eines zweiten Gebiets ist `sensor.aircraft_in_range_2` und so weiter |
| `geo_location.aircraft_…` | eine pro Flugzeug, benannt nach seinem Hex-Code (`geo_location.aircraft_a1b2c3`); sie kommt und geht mit dem Flugzeug. Jede trägt `source: live_track_aircraft`, und ihr Zustand ist ihre Entfernung vom Mittelpunkt in Kilometern |

Die Attribute des Sensors sagen, was geschieht: `published_count` (wie viele
auf der Karte sind), `capped` (wahr, wenn das Maximum die Liste gekürzt hat),
`source` (welches Netz zuletzt geantwortet hat), `source_backoff`,
`route_artifact`, `route_download`, `airport_table`, `airport_download`,
`route_lookup`, `watched_count`, `military_in_areas`, `military_by_area`,
`followed_asked`, `followed_found`, `follow_status`, `adsblol_key` und
`enforcement_list`.

⚠ **Die Markierungen der Flugzeuge haben absichtlich keine eindeutige ID.**
Ein Gebiet sieht im Jahr Tausende verschiedener Flugzeuge, und ein
Registereintrag für jedes würde Home Assistant ohne Nutzen langsamer starten
lassen. Daher können sie in der Oberfläche nicht umbenannt, ausgeblendet oder
einem Bereich zugewiesen werden. Ihre Entitäts-IDs kommen trotzdem aus dem
Hex-Code, sodass dasselbe Flugzeug immer dieselbe ID bekommt. Der Sensor hat
eine eindeutige ID und kann umbenannt werden.

⚠ **Ihre Datenbank.** Der Recorder von Home Assistant speichert eine neue
Zeile, wann immer sich eine Entität ändert, und ein fliegendes Flugzeug ändert
sich bei jeder Aktualisierung, standardmäßig alle 15 Sekunden. Auf unserem
Testsystem kostete im September 2026 eine solche Entität, alle 15 Sekunden
aktualisiert, etwa 9,6 MB am Tag; bei 50 Flugzeugen sind das etwa 480 MB am
Tag. Wenn Sie nicht den Verlauf jedes Flugzeugs möchten, halten Sie sie aus
dem Recorder heraus. Fügen Sie dies in `configuration.yaml` ein und starten
Sie dann neu:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.aircraft_*
```

Hat Ihre `configuration.yaml` schon einen Abschnitt `recorder:`, fügen Sie nur
das Muster `geo_location.aircraft_*` hinzu, unter `exclude:` und
`entity_globs:`. Eine Kartenkarte, die einen Verlauf zeichnen soll, hat dann
keine Spur zu zeichnen. `sensor.aircraft_in_range` kostet wenig: Seine
Attribute nehmen nur wenige Werte an, daher speichert der Recorder sie einmal.

---

## Was es sendet und herunterlädt

**Über Ihren Standort.** Mittelpunkt und Radius jedes Gebiets werden bei jeder
Aktualisierung an adsb.fi gesendet, standardmäßig alle 15 Sekunden, und an
adsb.lol, wenn adsb.fi nicht antwortet. Der Mittelpunkt wird so gesendet, wie
Sie ihn festgelegt haben, und er beginnt bei Ihrem Zuhause: Um Ihr Zuhause
nicht mehr zu senden, verschieben Sie den Mittelpunkt davon weg
(**Konfigurieren** → **Centre**) oder löschen Sie das Gebiet. Die Hex-Codes
und Rufzeichen, denen Sie folgen, werden einmal pro Minute an adsb.fi (oder
adsb.lol) gesendet, und Ihr adsb.lol-Schlüssel nur an adsb.lol. Die
Rufzeichen von Linienflügen in Ihrem Gebiet werden an adsbdb gesendet, wenn
FiledRoutesDB für sie keine Route hat. Sonst wird nichts über Sie irgendwohin
gesendet. Jeder Dienst sieht Ihre Internetadresse, wie jede Website.

**Wie viel.**

| Quelle | Was und wie oft | Nach einem Fehler |
|---|---|---|
| adsb.fi | jedes Flugzeug in Ihrem Kreis, bei jeder Aktualisierung (standardmäßig alle 15 Sekunden); eine Anfrage pro Minute für die per Hex-Code verfolgten Flugzeuge und die Flugzeuge des Präsidenten; eine für die Militärliste; eine für alle verfolgten Rufzeichen zusammen, nur wenn Sie welchen folgen | fragt stattdessen adsb.lol. Eine Quelle, die mit HTTP 429 ablehnt, wird für die Zeit übersprungen, die sie verlangt, oder für 1 Minute, verdoppelt bis zu 10 Minuten |
| adsb.lol | dieselben Anfragen, nur solange adsb.fi nicht antwortet | dasselbe |
| adsbdb | eine Anfrage pro neuem Rufzeichen einer Fluggesellschaft, für das FiledRoutesDB keine Route hat, mindestens 1 Sekunde Abstand; eine Antwort wird 30 Tage behalten, ein „keine Route“ 24 Stunden. Antworten werden nur im Arbeitsspeicher gehalten | 15 Minuten nicht erneut gefragt; alle Anfragen pausieren 15 Minuten nach HTTP 429 |
| FiledRoutesDB, von GitHub | eine kleine Prüfsummendatei einmal am Tag, nach 14:00 Uhr Chicagoer Zeit (Vereinigte Staaten); die Datei selbst, etwa 4,6 MB, nur wenn sie sich geändert hat | eine Stunde später erneut versucht; Ihre Kopie bleibt in Gebrauch, bis sie abläuft |
| AirportZones, von GitHub | eine kleine Prüfsummendatei einmal am Tag; die Tabelle selbst, etwa 4,8 MB, nur wenn sie sich geändert hat | eine Stunde später erneut versucht; Ihre Kopie bleibt in Gebrauch |
| EnforcementAircraft, von GitHub | eine kleine Prüfsummendatei einmal pro Stunde; die Liste selbst, klein, nur wenn sie sich geändert hat | Ihre Kopie bleibt in Gebrauch |
| FAA-Luftfahrzeugregister (Vereinigte Staaten) | das Register, etwa 73 MB, einmal alle 7 Tage, von `registry.faa.gov` | am nächsten Tag erneut versucht; Ihre Kopie bleibt in Gebrauch |

Die heruntergeladenen Dateien werden mit anderen Live-Track-Modulen geteilt,
daher wird jede nur einmal heruntergeladen, wie viele Module Sie auch
installieren. Sie liegen im Ordner `.storage` von Home Assistant unter Namen,
die mit `saw_` beginnen. Entfernen Sie Live Track Aircraft und nutzt kein
anderes Live-Track-Modul sie, können Sie sie von Hand löschen.

---

## Helfen Sie mit, es zu erweitern

Live Track Aircraft wächst noch. Wir fügen Routenquellen, Datenquellen und
Flugzeugdaten hinzu, sobald wir sie finden, und wir möchten wissen, was Sie
sich als Nächstes wünschen.

### Etwas vorschlagen

Fehlt Ihr Land, Ihr Flughafen oder Ihr Flugzeugtyp? Ist etwas falsch oder
schwer zu verstehen? Sagen Sie es uns auf dem Weg, der für Sie einfacher ist:

* [**Füllen Sie ein kurzes Formular aus**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=de.yml)
  auf Deutsch. Sie brauchen ein kostenloses GitHub-Konto.
* **Schreiben Sie eine E-Mail** an
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Kein Konto nötig.

In beiden Fällen hilft es, wenn Sie uns sagen:

* was Sie gern sehen würden, und wo auf der Welt;
* einen Link, wo die Daten veröffentlicht werden, falls Sie einen kennen (eine
  Open-Data-Seite, ein öffentlicher Feed, die Website eines Dienstes): nicht
  nötig, aber hilfreich;
* die Sprache Ihres Home Assistant, wenn es um die Formulierung oder eine
  Übersetzung geht.

Schreiben Sie auf Englisch oder in Ihrer eigenen Sprache, was für Sie
einfacher ist.

### Selbst etwas hinzufügen, mit unserer Hilfe

Wenn Sie selbst etwas hinzufügen möchten, helfen wir Ihnen dabei, von der
ersten Frage bis zur fertigen Veröffentlichung. Sie müssen kein Entwickler
sein, um anzufangen:

* **Eine Übersetzung.** Die Texte im Einrichtungsdialog sind eine kurze Liste
  von Sätzen in einer Textdatei. Wir zeigen Ihnen, welche Datei und welche
  Zeilen.
* **Eine neue Datenquelle.** Sagen Sie uns, wo die Daten veröffentlicht
  werden. Wir können den Code gemeinsam schreiben oder Ihren durchsehen.
* **Testen, wo Sie wohnen.** Installieren Sie es, sehen Sie sich Ihren Teil
  der Karte an, und sagen Sie uns, was stimmt und was nicht.
* **Eine Korrektur dieser README.** Wenn ein Schritt nicht zu dem passte, was
  Sie gesehen haben, sagen Sie uns, was Sie gesehen haben.

[**Sagen Sie uns, was Sie vorhaben**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=de.yml)
oder schreiben Sie an
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
und wir antworten mit den nächsten Schritten.

---

## Sprachen

Diese README: [English](README.md), **Deutsch**, [Français](README.fr.md),
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md).
Jede übersetzte README ist vollständig.

Der Einrichtungsdialog und die Optionen sind vorerst nur auf Englisch, gleich
welche Sprache Ihr Home Assistant hat. Wenn Sie eine andere Sprache sprechen,
können Sie sie selbst übersetzen: Es ist eine kurze Liste von Sätzen in einer
Datei, und [wir helfen Ihnen dabei](#selbst-etwas-hinzufügen-mit-unserer-hilfe).

Einen Fehler in einer Übersetzung gefunden, oder eine andere Sprache nötig?
Sagen Sie es uns unter
<https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues>, oder
[übersetzen Sie mit unserer Hilfe](#selbst-etwas-hinzufügen-mit-unserer-hilfe).

---

## Danksagungen und Lizenzen

* **adsb.fi** (<https://adsb.fi>): Positionen von Flugzeugen, offene Daten nur
  für den persönlichen, nicht kommerziellen Gebrauch, nach den Bedingungen in
  seiner [Open-Data-README](https://github.com/adsbfi/opendata), die
  verlangen, adsb.fi zu nennen und auf seine Startseite zu verlinken. Wenn Sie
  diese Integration installieren, nutzen Sie adsb.fi, und seine Bedingungen
  gelten für Sie.
* **adsb.lol** (<https://adsb.lol>): Positionen von Flugzeugen, unter der
  [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/).
  Wenn Sie diese Integration installieren, nutzen Sie adsb.lol, und seine
  Bedingungen gelten für Sie. Beide Netze werden von Freiwilligen betrieben:
  Wenn Sie können, unterstützen Sie sie, indem Sie einen Empfänger beisteuern.
* **FiledRoutesDB** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/FiledRoutesDB)):
  Routen aus bei der FAA (Vereinigte Staaten) aufgegebenen Flugplänen, Daten
  unter CC BY 4.0, mit der LADD-Liste der FAA vor der Veröffentlichung
  angewandt.
* **adsbdb** (<https://www.adsbdb.com>): Routen außerhalb von FiledRoutesDB.
  Seine Routendaten sind das Werk von David Taylor (Edinburgh) und Jim Mason
  (Glasgow) und dürfen ohne Erlaubnis nicht kopiert oder neu veröffentlicht
  werden, daher werden Antworten nur im Arbeitsspeicher gehalten, nie in eine
  Datei geschrieben, und jedes Flugzeug mit einer Route von adsbdb nennt sie.
* **Das FAA-Luftfahrzeugregister** (Federal Aviation Administration,
  Vereinigte Staaten): Namen von Haltern und Betreibern der in den Vereinigten
  Staaten registrierten Flugzeuge, öffentliche Daten der Regierung der
  Vereinigten Staaten. Die FAA lässt die Namen, die sie zurückhalten soll,
  selbst weg, bevor sie die Datei veröffentlicht.
* **OurAirports** (<https://ourairports.com>), über
  [AirportZones](https://github.com/StrausbergAutomationWorks/AirportZones):
  Namen und Positionen von Flughäfen, unter der ODbL 1.0; Zeitzonen von
  StrausbergAutomationWorks hinzugefügt.
* **EnforcementAircraft** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)):
  die Liste der Flugzeuge von Einwanderungs- und Bundespolizeibehörden, unter
  der ODbL 1.0.
* **ADS-B Radar** (<https://adsb-radar.com>): die Flugzeugsymbole, aus seinem
  [SVG-Symbolsatz für Flugzeuge](https://adsb-radar.com/help/icons.html) von
  Jos Nutbroek, genutzt nach seinen Bedingungen, die diesen Rückverweis
  verlangen. Die Symbole fallen nicht unter die MIT-Lizenz dieses Repositorys.
  Einige Symbole wurden von StrausbergAutomationWorks im Stil des Satzes
  gezeichnet und ADS-B Radar geschenkt, daher gelten auch für sie dessen
  Bedingungen. Diese Integration liefert die Symbole mit neuer Füllung und
  Umrisslinie, nach Flugzeugklasse skaliert, und lässt einige Propeller und
  Rotoren drehen. Jede Änderung steht in [ATTRIBUTION.md](ATTRIBUTION.md).
* **Die Kartenkarte** ist [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, eine Kopie von [ha-map-card](https://github.com/nathan-gs/ha-map-card)
  von nathan-gs, MIT. Ihre Kartenkacheln und deren Nachweise stehen in ihrer
  README.

Keine dieser Organisationen hat diese Integration erstellt oder unterstützt.

**Code**: MIT, in [LICENSE](LICENSE).

**Für Entwickler:** Die Entitäten folgen dem gemeinsamen Kartenvertrag von
Live Track, sodass jedes Modul ohne Vorlagensensoren auf einer Karte
erscheint; Positionen kommen über eine Quellenschnittstelle in
`custom_components/live_track_aircraft/sources/`, sodass ein weiterer
Datenstrom hinzugefügt werden kann, ohne die Entitäten anzufassen. Die Tests
laufen mit `python -m unittest discover -s tests`.

---

## Stichwörter

Home Assistant Flugzeuge · Home Assistant Flugverfolgung · ADS-B ·
ADS-B-Karte · Flugverfolgung · Flugzeugradar · Flugzeuge über mir · MLAT ·
Mode S · Flugrouten · Militärflugzeuge · Air Force One · Hubschrauber ·
aircraft · flight tracker · avions · suivi des vols · vliegtuigen ·
vluchten volgen · 飞机 · 航班跟踪 · aviones · seguimiento de vuelos ·
aerei · tracciamento voli · fly · flysporing · adsb.fi · adsb.lol · adsbdb ·
FiledRoutesDB · FAA-Register · OurAirports · ADS-B Radar · geo_location ·
Kartenkarte · Lovelace · HACS · Marketplace · Live Track · LiveTrack ·
StrausbergAutomationWorks

---

**Würdigung.** StrausbergAutomationWorks würdigt die indigenen Völker aller
Länder und Gewässer auf dieser Karte, überall auf der Welt, und erweist ihren
Ältesten, in Vergangenheit und Gegenwart, seinen Respekt.
