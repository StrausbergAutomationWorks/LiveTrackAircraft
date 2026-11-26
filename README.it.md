# Live Track Aircraft

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · **Italiano** · [Dansk](README.da.md) · [Tutte le lingue](#lingue)

**Aerei per Home Assistant, su una sola mappa.** Live Track Aircraft mette
sulla mappa del tuo Home Assistant gli aerei che volano sopra casa tua, o
sopra qualsiasi luogo del mondo tu scelga: ognuno disegnato come il suo tipo,
girato nella direzione in cui vola, con chi lo opera e, quando si sa, dove
sta andando. Può anche seguire aerei e voli scelti ovunque si trovino, e
sorvegliare gli aerei militari nelle zone che indichi.

> **Live Track Aircraft è un modulo di Live Track**, una famiglia di
> integrazioni di Home Assistant che disegnano tutto ciò che si muove, e il
> meteo in cui si muove, su una sola mappa condivisa: aerei, navi, treni e
> meteo. Installalo da solo o accanto agli altri moduli
> ([elenco più sotto](#parte-di-live-track-gli-altri-moduli)).

> **Sta crescendo, e le idee sono benvenute.** Live Track Aircraft copre oggi
> tutto il mondo dove i volontari gestiscono ricevitori, con rotte e nomi dei
> proprietari più dettagliati per gli Stati Uniti, e stiamo aggiungendo altre
> fonti di rotte e altri dati sugli aerei. Manca il tuo?
> [Suggeriscilo](#aiutaci-a-farlo-crescere), o aggiungilo tu: ti aiuteremo a
> farlo.

**Stato: 0.1.6, pubblicato.** Nel catalogo del Marketplace ([installalo più
sotto](#installazione-passo-dopo-passo)).

Opera originale di StrausbergAutomationWorks. Non affiliato a, né approvato
da, adsb.fi, adsb.lol, adsbdb, la Federal Aviation Administration (Stati
Uniti), OurAirports, ADS-B Radar, Planespotters.net, alcuna compagnia aerea o
alcun operatore di aeromobili.

> ⚠ **Non è un sistema di sicurezza.** Mostra dati pubblici, di solito vecchi
> di qualche secondo e a volte di un minuto o più, e solo gli aerei che i
> ricevitori dei volontari riescono a sentire. Non serve per la navigazione,
> per separare gli aerei, né per alcun altro uso operativo.

---

## Indice

1. [Tutto quello che fa](#tutto-quello-che-fa)
2. [Dove funziona](#dove-funziona)
3. [Parte di Live Track: gli altri moduli](#parte-di-live-track-gli-altri-moduli)
4. [Prima di iniziare](#prima-di-iniziare)
5. [Installazione, passo dopo passo](#installazione-passo-dopo-passo)
6. [Configurazione, passo dopo passo](#configurazione-passo-dopo-passo)
7. [Chiavi gratuite che attivano di più, passo dopo passo](#chiavi-gratuite-che-attivano-di-più-passo-dopo-passo)
8. [Mettere la mappa su una plancia](#mettere-la-mappa-su-una-plancia)
9. [Usarlo nelle automazioni](#usarlo-nelle-automazioni)
10. [Tutto sulla mappa, nel dettaglio](#tutto-sulla-mappa-nel-dettaglio)
11. [Tutte le entità che crea](#tutte-le-entità-che-crea)
12. [Cosa invia e scarica](#cosa-invia-e-scarica)
13. [Aiutaci a farlo crescere](#aiutaci-a-farlo-crescere)
14. [Lingue](#lingue)
15. [Riconoscimenti e licenze](#riconoscimenti-e-licenze)
16. [Parole chiave](#parole-chiave)

---

## Tutto quello che fa

### Sulla mappa, senza configurare nulla

Aggiungi una **zona**: un centro sulla mappa e un raggio attorno. Parte da
casa tua. Tutto ciò che segue appare poi in quella zona o, dove la tabella lo
dice, in qualsiasi parte del mondo.

| Cosa | Dove | Da dove |
|---|---|---|
| **Aerei**: aerei di linea, aerei leggeri, elicotteri, alianti, mongolfiere e droni, ognuno disegnato come il suo tipo e girato nella direzione in cui vola | in ogni zona | adsb.fi, o adsb.lol quando adsb.fi non risponde |
| **Chi lo opera**: la compagnia aerea, il proprietario, o il tipo quando non si sa altro, nell'etichetta del segnaposto | ogni aereo | il nominativo della compagnia aerea; il registro degli aeromobili della FAA (Stati Uniti) per i proprietari |
| **Colori che dicono chi lo fa volare**: governo, polizia, forze dell'ordine federali, militari, eliambulanze ed elicotteri, ognuno con il suo colore | ogni aereo, dove si sa | il registro degli aeromobili della FAA (Stati Uniti) e il contrassegno militare del flusso di dati |
| **Rotte**: da dove è decollato l'aereo e dove sta andando, con i nomi degli aeroporti e un orario di arrivo stimato | voli che presentano un piano di volo alla FAA (Stati Uniti); altrove quando adsbdb conosce il volo | FiledRoutesDB, poi adsbdb |
| **Gli aerei del Presidente degli Stati Uniti**, con gli aerei dell'89th Airlift Wing e gli aerei militari che li scortano | in tutto il mondo | adsb.fi e il suo elenco militare |
| **Aerei dell'elenco pubblico EnforcementAircraft** (immigrazione e forze dell'ordine federali), con luci lampeggianti | in ogni zona | l'elenco EnforcementAircraft |
| **Aerei militari nelle tue zone di sorveglianza**: ogni aereo che il flusso di dati segna come militare, dentro un massimo di dieci cerchi che indichi tu, anche quando la tua zona è piena. Facoltativo: scrivi i cerchi nella finestra di configurazione | in tutto il mondo | l'elenco militare di adsb.fi |
| **Aerei e voli che segui**: il tuo aereo, la flotta di un club, o il volo su cui si trova un familiare. Facoltativo: scrivi i loro codici nella finestra di configurazione | in tutto il mondo | adsb.fi |
| **Foto**: una foto dell'aereo, con il nome del fotografo, quando lo punti | ogni aereo di cui Planespotters.net ha una foto | Planespotters.net ([altro](#foto)) |
| **La tua immagine per un aereo**, al posto della sua icona | ovunque quell'aereo sia mostrato | un'immagine che metti in una cartella ([come](#la-tua-immagine-per-un-aereo)) |

### Con la tua chiave o il tuo account gratuito

| Chiave o account gratuito | Cosa aggiunge |
|---|---|
| Chiave **adsb.lol** | più richieste al giorno ad adsb.lol, la seconda fonte, così la mappa continua durante un lungo guasto di adsb.fi |

Ognuna si ottiene in pochi minuti: [passo dopo passo più sotto](#chiavi-gratuite-che-attivano-di-più-passo-dopo-passo).

---

## Dove funziona

| Regione | Cosa ottieni | Da dove | Serve |
|---|---|---|---|
| **Tutto il mondo** | posizioni degli aerei ovunque i volontari gestiscano ricevitori: fitte sopra l'Europa e il Nord America, più rade altrove, e poche o nessuna in alto mare | adsb.fi, adsb.lol | niente |
| **Tutto il mondo** | nomi degli aeroporti sulle rotte, e i fusi orari degli aeroporti per l'orario di arrivo | OurAirports, tramite la tabella AirportZones | niente |
| **Tutto il mondo** | rotte di molti voli di linea, verificate rispetto a dove si trova davvero l'aereo | adsbdb | niente |
| **Nord America**: Stati Uniti | nomi dei proprietari e degli operatori degli aerei immatricolati negli Stati Uniti, e i colori per gli aerei governativi e della polizia | il registro degli aeromobili della FAA | niente |
| **Nord America**: Stati Uniti | rotte dei voli presentati alla FAA, compresi i voli internazionali da e per gli Stati Uniti | FiledRoutesDB | niente |

Non è nell'elenco? [Diccelo](#aiutaci-a-farlo-crescere). Dove qualcuno
pubblica i dati apertamente, valuteremo di aggiungerli.

⚠ **La copertura è buona dove ci sono ricevitori, e assente dove non ci
sono.** Un aereo appare solo quando il ricevitore di un volontario lo sente, o
quando più ricevitori insieme riescono a localizzarlo. Nessuna impostazione
può creare una copertura che non esiste. **Un cielo vuoto sulla mappa può
voler dire nessun ricevitore vicino a te, non nessun aereo.**

⚠ **Le rotte sono soprattutto per gli Stati Uniti.** FiledRoutesDB contiene
solo piani di volo presentati alla FAA. Altrove una rotta viene da adsbdb, che
conosce molti voli di linea e pochi altri, quindi fuori dagli Stati Uniti
molti aerei non mostrano una rotta.

⚠ **I nomi dei proprietari ci sono solo per gli aerei immatricolati negli
Stati Uniti.** Un aereo immatricolato in un altro paese mostra la sua
compagnia aerea, ricavata dal nominativo, o il suo tipo.

---

## Parte di Live Track: gli altri moduli

Live Track è un insieme di integrazioni di Home Assistant, una per ogni tipo
di cosa che si muove, tutte disegnate sulla stessa scheda mappa. Ognuna
funziona da sola; insieme formano un'unica immagine dal vivo. Condividono la
scheda mappa e una libreria Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
quindi installarne un'altra non aggiunge richieste a una fonte che un'altra
legge già.

| Modulo | Cosa mette sulla mappa | Stato |
|---|---|---|
| **Live Track Aircraft** | aerei sopra di te tramite ADS-B, con rotte e icone per tipo (questo modulo) | pubblicato |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | navi e barche tramite AIS, vicino a te o ovunque | pubblicato |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | treni suburbani in Nord America, Europa e Australia | pubblicato |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | treni intercity e a lunga percorrenza in Nord America, Europa e Australia | pubblicato |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | aerei e navi dell'immigrazione e delle forze dell'ordine federali, da elenchi pubblici | pubblicato |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | meteo, tempeste e rischi naturali | pubblicato |
| Live Track Stations | tabelloni delle partenze e avvisi "è ora di andare" per ogni stazione | previsto |
| Live Track Satellites | satelliti che passano sopra di te | previsto |
| Live Track Freight Trains | treni merci e di servizio dove le ferrovie li pubblicano | previsto |
| Live Track Transit | autobus urbani, tram, traghetti e metropolitane | previsto |
| Live Track Intercity Buses | autobus interurbani e regionali | previsto |
| Live Track Commuter Buses | autobus per pendolari | previsto |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | la scheda mappa condivisa su cui disegna ogni modulo | pubblicata, installata con ogni modulo |

Tutto è gratuito e open source. Niente è riservato agli sponsor.

---

## Prima di iniziare

* **Home Assistant** 2026.11 o successivo.
* **Il Marketplace** (HACS) nel tuo Home Assistant, per installarlo e
  aggiornarlo nel modo più semplice. Senza, puoi copiare i file a mano.
* **Accesso a internet** per Home Assistant: tutto arriva da fonti pubbliche.
* Niente da pagare e nessun account necessario. La chiave adsb.lol qui sopra è
  facoltativa.
* Home Assistant installa da solo i due pacchetti Python di cui ha bisogno
  (`saw-livetrack` e `tzfpy`) la prima volta che l'integrazione si carica.

---

## Installazione, passo dopo passo

### Dal Marketplace (consigliato)

1. In Home Assistant, apri **Impostazioni → Marketplace** (HACS).
2. Cerca **Live Track Aircraft** e aprilo.
3. Scegli **Scarica** (o **Installa**).
4. **Riavvia Home Assistant**: **Impostazioni → Sistema → Riparazioni** offre
   il riavvio, oppure usa **Impostazioni → Sistema → Riavvia**.

Se la ricerca non lo trova, aggiungilo tramite il suo link: scegli **Aggiungi
dal collegamento** (o il menu a tre puntini → **Repository personalizzate**),
inserisci `StrausbergAutomationWorks/LiveTrackAircraft`, scegli **Integrazione**
se viene chiesto il tipo, poi prosegui dal passo 3.

Il Marketplace offre poi ogni nuova versione come aggiornamento.

### A mano

1. Scarica il codice sorgente della
   [versione più recente](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/releases/latest).
2. Copia la sua cartella `custom_components/live_track_aircraft` nella
   cartella `custom_components` della cartella di configurazione del tuo Home
   Assistant (crea `custom_components` se non c'è).
3. Riavvia Home Assistant.

Per aggiornare a mano, sostituisci la cartella con quella della nuova versione
e riavvia.

---

## Configurazione, passo dopo passo

La finestra di configurazione è in inglese. I suoi campi sono chiamati qui
come li mostra lei.

1. Apri **Impostazioni → Dispositivi e servizi**.
2. Scegli **Aggiungi integrazione** (in basso a destra) e cerca **Live Track
   Aircraft**.
3. **Centre** (centro): trascina il segnaposto al centro del cielo che vuoi
   sorvegliare. Parte da casa tua.
4. **Radius (km)** (raggio): fino a che distanza dal centro sono mostrati gli
   aerei, da 1 a 463 km (da 0,6 a 288 miglia). Se non sei sicuro, lascia
   56 km (35 miglia).
5. **Update interval (seconds)** (intervallo di aggiornamento): lascia 15. Le
   fonti rifiutano richieste più frequenti.
6. **Maximum aircraft published** (numero massimo di aerei pubblicati):
   lascia 250. È un limite di sicurezza, non un modo per mostrare meno aerei.
7. Per ora lascia vuoti i quattro campi facoltativi. Ognuno è spiegato più
   sotto.
8. Scegli **Invia**.

Tutto qui. Gli aerei appaiono entro un minuto. Ogni zona è una voce, con il
titolo del suo centro e del suo raggio, per esempio `39.817, -84.050 - 56 km`.
Per sorvegliare una seconda zona, aggiungi di nuovo l'integrazione con un
altro centro o un altro raggio. Lo stesso centro e lo stesso raggio due volte
vengono rifiutati.

Rotte, nomi degli aeroporti e nomi dei proprietari si riempiono nei primi
minuti, man mano che si scaricano i file da cui vengono
([Cosa invia e scarica](#cosa-invia-e-scarica)).

### Cambiare ciò che mostra: le opzioni

Apri **Impostazioni → Dispositivi e servizi → Live Track Aircraft → Configura**
(l'ingranaggio) sulla zona che vuoi cambiare. Ogni opzione, in parole
semplici:

| Opzione | Cosa fa | Predefinito |
|---|---|---|
| **Centre** | sposta la zona; il suo titolo la segue | casa tua |
| **Radius (km)** | fino a che distanza dal centro sono mostrati gli aerei, da 1 a 463 km (da 0,6 a 288 miglia) | 56 km (35 miglia) |
| **Update interval (seconds)** | ogni quanto si chiedono le posizioni, da 15 a 3.600 secondi | 15 |
| **Maximum aircraft published** | un limite di sicurezza, da 1 a 1.000; quando nel cerchio ci sono più aerei, si tengono i più vicini. Gli aerei che segui, gli aerei nelle tue zone di sorveglianza militare e gli aerei dell'elenco EnforcementAircraft si tengono sempre | 250 |
| **Military watch areas** | cerchi in cui è mostrato ogni aereo militare ([come](#zone-di-sorveglianza-militare)) | vuoto |
| **Aircraft to follow (hex codes)** | aerei seguiti ovunque, per il loro codice esadecimale ([come](#aerei-e-voli-che-segui)) | vuoto |
| **Flights to follow (call signs)** | voli seguiti ovunque, per il loro nominativo (la stessa sezione) | vuoto |
| **adsb.lol API key** | la tua chiave per adsb.lol ([come ottenerla](#chiavi-gratuite-che-attivano-di-più-passo-dopo-passo)) | vuoto |

Svuota uno dei quattro campi facoltativi per disattivare quella parte.

---

## Chiavi gratuite che attivano di più, passo dopo passo

Sono tutte gratuite e personali: ogni persona che installa Live Track Aircraft
ottiene la sua. Incolla ognuna in **Impostazioni → Dispositivi e servizi →
Live Track Aircraft → Configura**.

### adsb.lol (più richieste alla seconda fonte, tutto il mondo)

Live Track Aircraft chiede prima ad adsb.fi, e chiede ad adsb.lol solo finché
adsb.fi non risponde. Senza chiave, adsb.lol permette 500 richieste al giorno
da un indirizzo internet, che un guasto di adsb.fi può esaurire in circa due
ore. Una chiave alza quel limite. Per iniziare non ti serve.

1. Apri <https://www.adsb.lol/request> e chiedi una chiave gratuita con il
   modulo che trovi lì. La documentazione di adsb.lol dà a questa chiave
   1.000 richieste al giorno.
2. Se fornisci dati ad adsb.lol con un tuo ricevitore, usa invece la tua
   chiave di feeder: la documentazione di adsb.lol le dà 7.200 richieste al
   giorno. Le tue chiavi sono sotto **My keys** su adsb.lol
   (<https://www.adsb.lol/mmb>).
3. Incolla la chiave in **adsb.lol API key** e scegli **Invia**.

La chiave è inviata solo ad adsb.lol. Se adsb.lol la rifiuta (sbagliata o
scaduta), Live Track Aircraft continua senza, e `sensor.aircraft_in_range`
della zona mostra `refused` nel suo attributo `adsblol_key` finché non cambi
la chiave. Altrimenti mostra `set`, oppure `none` senza chiave. Non servono né
password né segreti.

---

## Mettere la mappa su una plancia

La mappa è [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
la scheda su cui disegna ogni modulo di Live Track. **Si installa con Live
Track Aircraft**: niente da scaricare, niente da copiare, nessuna risorsa da
aggiungere.

1. Apri una plancia, scegli la matita (**Modifica la plancia**), poi
   **Aggiungi scheda**.
2. Scorri fino in fondo e scegli **Manuale**.
3. Incolla questo e scegli **Salva**:

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

Gli altri moduli di Live Track vanno in `entity_filter` allo stesso modo: una
regola `- domain: geo_location` in più per ogni fonte.

**Sulla mappa:**

* Ogni aereo è disegnato come il suo tipo, girato nella direzione in cui vola,
  e si muove in modo fluido tra le posizioni che comunica.
* La sua etichetta è il nominativo del volo (`UAL308`), altrimenti chi lo
  opera (`Lewis University`), altrimenti il suo tipo (`Cessna 172 Skyhawk`).
* **Punta** un aereo per vedere la sua compagnia aerea o il suo operatore, la
  sua foto se c'è e, quando si conosce una rotta, la rotta e quanti minuti
  mancano all'arrivo. **Fai clic** su di esso per tutti i dettagli e una foto
  più grande, collegata alla sua pagina su Planespotters.net ([Foto](#foto)).

Se le risorse delle tue plance sono impostate in YAML
(`lovelace: resource_mode: yaml`), non si può registrare nulla per te: un
avviso in **Riparazioni** ti dà allora la riga esatta da aggiungere. Una
scheda che hai installato tu dal Marketplace non viene toccata. Se i file
dell'integrazione vengono rimossi mentre le sue zone sono ancora configurate,
e non è installato nessun altro modulo di Live Track, rimuovi tu la riga della
scheda in **Impostazioni → Plance → Risorse**. Qualsiasi altra scheda mappa
che mostra entità `geo_location` mostra anche gli aerei, come segnaposto
semplici.

---

## Usarlo nelle automazioni

Tutto è una normale entità di Home Assistant, quindi l'editor delle
automazioni funziona con essa, senza codice.

**Una notifica sul telefono quando un aereo militare è in una delle tue zone
di sorveglianza militare:**

1. **Impostazioni → Automazioni e scenari → Crea automazione → Crea una nuova
   automazione**.
2. **Quando**: **Aggiungi attivazione** → **Entità** → **Stato numerico**.
   Scegli l'entità **Aircraft in range**, l'**Attributo** **Military in
   areas** (`military_in_areas`) e **Maggiore di** `0`.
3. **Allora**: **Aggiungi azione**, cerca l'azione di notifica del tuo
   telefono (porta il nome del tuo telefono) e scrivi un messaggio, per
   esempio:

   ```text
   Un aereo militare è nella tua zona di sorveglianza
   ```

4. **Salva**.

Per questo serve almeno una zona di sorveglianza militare
([come](#zone-di-sorveglianza-militare)).

**Altre idee:** una notifica quando il volo di un familiare è in aria, quando
l'attributo `followed_found` sale sopra 0; una luce che si accende quando più
di 20 aerei sono sopra casa tua a Francoforte (Germania); su una plancia, il
numero di aerei sopra il tuo campo di volo nel Queensland (Australia), da
`sensor.aircraft_in_range`; un messaggio quando decolla l'aereo del tuo club,
quando appare la sua entità (`geo_location.aircraft_` e il suo codice
esadecimale).

---

## Tutto sulla mappa, nel dettaglio

### Aerei

Gli aerei trasmettono la loro posizione via radio, con un sistema chiamato
ADS-B. Volontari in tutto il mondo gestiscono ricevitori e condividono ciò che
sentono attraverso reti comunitarie. Live Track Aircraft chiede a una di
queste, adsb.fi, ogni aereo dentro il tuo cerchio, ogni 15 secondi per
impostazione predefinita. Quando adsb.fi non risponde, o risponde con molti
meno aerei di un momento prima, chiede ad adsb.lol. Dove più ricevitori
sentono un aereo che non trasmette la propria posizione, le reti possono
comunque localizzarlo (multilaterazione, MLAT).

Ogni aereo è un segnaposto, con il nome del suo codice esadecimale: l'indirizzo
di sei caratteri che il suo transponder trasmette, che appartiene all'aereo e
non cambia. Il segnaposto appare quando l'aereo entra nel tuo cerchio e viene
rimosso quando ne esce.

L'etichetta è il nome più utile che si conosce, in quest'ordine:

| L'aereo ha | L'etichetta mostra | Esempio |
|---|---|---|
| il nominativo di un volo | il nominativo | `UAL308` |
| altrimenti un operatore noto | l'operatore | `Lewis University` |
| altrimenti un tipo noto | il tipo | `Cessna 172 Skyhawk` |
| niente di tutto questo | l'immatricolazione, il codice del tipo o il codice esadecimale | `N12345` |

⚠ Non sono mostrati: gli aerei a terra, i veicoli aeroportuali e le tracce
solo radar senza identità. Un aereo che non trasmette, o che vola dove nessun
ricevitore lo sente, non può essere mostrato.

Su ogni aereo: `identity` (il codice esadecimale), `callsign`,
`registration`, `aircraft_type`, `aircraft_name`, `operator`, `altitude_m`,
`speed_kmh`, `vertical_rate_ms`, `course_deg`, `squawk`, `emitter_category`,
`is_military`, `is_government`, `last_seen`.

### Colori e icone

Ogni aereo è disegnato come il suo tipo: un aereo di linea, un jet
d'affari, un monomotore leggero, un bimotore, un elicottero, un convertiplano,
un aliante, una mongolfiera, un drone e molti altri, in scala secondo la sua
classe. Eliche e rotori girano. L'icona è girata nella direzione in cui vola
l'aereo; un aereo lento mantiene la sua ultima direzione invece di girare su
sé stesso.

Il colore dice chi lo fa volare, dove si sa:

| Colore | Chi |
|---|---|
| grigio chiaro | la maggior parte degli aerei |
| verde menta | elicotteri e altri aeromobili ad ala rotante |
| ambra | aerei governativi ed eliambulanze |
| blu | forze dell'ordine federali |
| verde militare | le forze armate e la guardia costiera |
| bianco, con luci blu lampeggianti | polizia |
| luci rosse e blu lampeggianti | aerei dell'elenco EnforcementAircraft ([più sotto](#lelenco-enforcementaircraft-e-live-track-salt)) |
| un alone fisso | un aereo di linea che effettua voli charter ICE Air, tra gli altri lavori |

⚠ Chi possiede un aereo si sa soprattutto per gli aerei immatricolati negli
Stati Uniti, dal registro della FAA. Altrove il colore viene solo dal
contrassegno militare del flusso di dati e dal tipo dell'aereo.

### Rotte e orari di arrivo

Una rotta mostra da dove è decollato l'aereo e dove sta andando, con i nomi
dei due aeroporti, e un orario di arrivo stimato. Viene da due posti:

1. **FiledRoutesDB**, un file pubblico dei piani di volo presentati alla FAA
   (Stati Uniti), costruito e pubblicato da StrausbergAutomationWorks e
   scaricato una volta al giorno. Ogni rotta è verificata rispetto a dove si
   trova l'aereo e alla direzione in cui vola. Una rotta che non torna è
   comunque mostrata, e segnata come non corrispondente in `route_check`.
2. **adsbdb**, interpellato solo quando FiledRoutesDB non ha una rotta per il
   nominativo, una volta per nominativo. La sua risposta è mostrata solo
   quando corrisponde a dove si trova davvero l'aereo.

Gli aerei i cui proprietari hanno chiesto alla FAA di non mostrare
pubblicamente i loro voli (l'elenco LADD della FAA, Limiting Aircraft Data
Displayed) sono tolti da FiledRoutesDB prima della pubblicazione. Live Track
Aircraft cancella la sua copia quando il file scade, o quando l'elenco LADD
con cui è stato costruito ha più di 14 giorni, così non mostra mai rotte
filtrate con un elenco vecchio.

L'orario di arrivo è una stima, non un orario ufficiale: la distanza in linea
retta che resta, alla velocità dell'aereo quando è in crociera e a una
velocità tipica della sua classe quando non lo è. Attese, avvicinamento e
rullaggio non sono contati.

Su ogni aereo con una rotta: `origin_icao`, `destination_icao`,
`origin_name`, `destination_name`, `route_source`, `route_check`,
`arrival_estimated_at`.

### Zone di sorveglianza militare

Ogni aereo che il flusso di dati segna come militare, dentro cerchi che
scegli tu, in qualsiasi parte del mondo, anche quando la tua zona è piena.

1. Apri **Impostazioni → Dispositivi e servizi → Live Track Aircraft →
   Configura** su una zona.
2. In **Military watch areas**, scrivi ogni cerchio come
   `latitude,longitude,km` (latitudine, longitudine, chilometri), e separa i
   cerchi con il punto e virgola, per esempio
   `39.81,-84.04,150; 34.0,-117.8,463`. Fino a dieci cerchi, ognuno da 1 a
   2.000 km (da 0,6 a 1.243 miglia). Scrivi i decimali con il punto.
3. Scegli **Invia**.

Gli aerei militari che ci sono dentro appaiono entro un minuto e si muovono
una volta al minuto. Ognuno porta `watch: military area`.
`sensor.aircraft_in_range` della zona li conta in `military_in_areas`, e per
cerchio in `military_by_area`. Svuota il campo per smettere.

⚠ Mostra solo ciò che trasmette ed è segnato come militare. I voli militari
possono volare con il transponder spento, e un aereo militare con
un'immatricolazione civile non è segnato.

### Aerei e voli che segui

Live Track Aircraft può seguire aerei che scegli ovunque si trovino nel mondo,
non solo dentro il tuo cerchio: il tuo aereo, la flotta di un club o di
un'azienda, o il volo su cui si trova un familiare.

1. Apri **Impostazioni → Dispositivi e servizi → Live Track Aircraft →
   Configura** sulla zona con cui vuoi che siano mostrati.
2. Compila **Aircraft to follow (hex codes)** (aerei da seguire, codici
   esadecimali), **Flights to follow (call signs)** (voli da seguire,
   nominativi), o entrambi.
3. Scegli **Invia**. Appaiono entro circa un minuto.

**Basta un codice per aereo.** Scegli in base a cosa vuoi seguire:

| Per seguire | Usa | Esempio |
|---|---|---|
| un aereo, qualunque volo faccia (il tuo aereo, una flotta) | il suo **codice esadecimale** | `a1b2c3` |
| un volo, qualunque aereo lo faccia (il viaggio di un familiare) | il suo **nominativo** | `UAL1234` |

Inserire entrambi i codici per lo stesso aereo non fa danni (è disegnato una
volta sola) ma non aggiunge nulla.

**Come scrivere i codici:**

* Separa i codici con virgole: `a1b2c3, a4b5c6, a7b8c9`. Vanno bene anche
  spazi o punti e virgola tra i codici.
* Un codice esadecimale ha esattamente sei caratteri: le cifre da 0 a 9 e le
  lettere da a a f, maiuscole o minuscole.
* Un nominativo ha da 2 a 8 lettere e cifre, scritte come l'aereo le
  trasmette, senza spazi né trattini: `UAL1234`, non `UA 1234` o `UAL-1234`.
* Fino a 100 codici esadecimali e 100 nominativi. Un codice scritto due volte
  conta una volta.
* Se un codice è sbagliato, la finestra rifiuta quel campo, dice come deve
  essere un codice valido, e non salva nulla finché non è corretto.

**Trovare i codici.** Ogni aereo sulla mappa porta il suo codice esadecimale
nell'attributo `identity` e il suo nominativo nell'attributo `callsign`. Per
un aereo immatricolato negli Stati Uniti, la ricerca per N-number del registro
della FAA mostra il codice esadecimale come "Mode S Code (Base 16 / Hex)". Per
un volo di linea, il nominativo è di solito il codice di tre lettere della
compagnia aerea più il numero del volo, che non è quello mostrato sul
biglietto:

| Biglietto | Nominativo |
|---|---|
| United UA 1234 | `UAL1234` |
| Delta DL 89 | `DAL89` |
| American AA 100 | `AAL100` |

Alcune compagnie aeree trasmettono un nominativo che non è il numero del volo.
Se un volo non appare, cercalo su una mappa dei voli in tempo reale e copia il
nominativo mostrato lì. Un nominativo viene riusato: lo stesso nominativo
domani è un altro viaggio, e può essere un altro aereo. Resta seguito finché
non lo togli.

**Cosa vedi.** Ogni aereo seguito è disegnato con la sua icona e la sua
etichetta abituali ovunque si trovi, anche quando la tua zona è piena. Il suo
attributo `watch` dice `followed`, e `outside_radius` dice se è fuori dal tuo
cerchio. Fuori dal tuo cerchio si muove una volta al minuto; dentro, con la
stessa frequenza di tutto il resto. `sensor.aircraft_in_range` della zona
mostra `followed_asked` (quanti codici segui), `followed_found` (quanti di
loro sono in volo adesso) e `follow_status` (l'ultima richiesta per
nominativo: `ok`, o cosa è andato storto).

**Per smettere**, togli il codice, o svuota il campo, e scegli **Invia**.

⚠ Si possono trovare solo gli aerei che trasmettono ADS-B, o che la MLAT
riesce a localizzare. Un aereo a terra o fuori dalla copertura dei ricevitori
non è mostrato, e `followed_found` non lo conta. Orari e ritardi per numero di
volo non fanno parte di questa funzione.

### La tua immagine per un aereo

Metti un'immagine a tua scelta al posto dell'icona di un aereo, per esempio il
tuo aereo.

1. Nella cartella di configurazione del tuo Home Assistant (la cartella che
   contiene `configuration.yaml`), crea una cartella chiamata
   `live_track_aircraft_pictures`.
2. Metti dentro l'immagine, con il nome del codice esadecimale dell'aereo:
   `a1b2c3.png`. Funzionano file PNG, JPG, WebP, GIF e SVG, fino a 2 MB
   ciascuno.

L'immagine appare entro un minuto, e così una modifica o una rimozione. È
disegnata dritta, non girata, perché una fotografia non è disegnata con il
muso in alto. L'attributo `picture_source` dell'aereo dice allora `override`.

Queste immagini richiedono l'accesso al tuo Home Assistant, come tutto il
resto. La mappa riceve ciascuna tramite un link firmato da Home Assistant,
che smette di funzionare dopo un giorno; prima ne viene creato uno nuovo.

### Foto

Quando punti un aereo, la mappa mostra una sua foto da
[Planespotters.net](https://www.planespotters.net), se ce n'è una, con il nome
del fotografo accanto. Fai clic sull'aereo per vedere la foto più grande; la
foto rimanda alla sua pagina su Planespotters.net. Non c'è nulla da
configurare.

La foto si cerca solo quando qualcuno punta quell'aereo, non per ogni aereo
della tua zona. Il tuo Home Assistant chiede a Planespotters.net in base al
codice esadecimale dell'aereo. Tiene la risposta, una foto o nessuna foto, per
12 ore, solo in memoria, quindi un riavvio la dimentica. Il browser che mostra
la mappa carica l'immagine direttamente da Planespotters.net. Home Assistant
non scarica, non conserva e non inoltra nessuna immagine.

⚠ Una foto mostra l'aereo come lo ha visto il fotografo, forse con una livrea
precedente o con un operatore precedente. Non tutti gli aerei hanno una foto
su Planespotters.net.

⚠ Non si cerca nessuna foto per un aereo che vola con un indirizzo temporaneo
per la privacy (il programma Privacy ICAO Address della FAA, Stati Uniti),
perché quel codice esadecimale non identifica l'aereo, né per una traccia
senza un vero codice esadecimale.

⚠ Non c'è ancora un'opzione per disattivare le foto.

Ogni aereo con un codice esadecimale porta `marker_photo_lookup`: l'indirizzo
sul tuo Home Assistant a cui la mappa chiede la foto. Solo chi ha effettuato
l'accesso al tuo Home Assistant può usarlo. Le foto sono opera dei loro
fotografi: vedi [Riconoscimenti e licenze](#riconoscimenti-e-licenze).

### Gli aerei presidenziali

Gli aerei usati dal Presidente degli Stati Uniti sono mostrati ovunque si
trovino nel mondo, per i loro codici esadecimali, mai per nominativo, insieme
agli aerei dell'89th Airlift Wing (nominativi SAM e VENUS) e agli aerei
militari che scortano un aereo presidenziale. Arrivano da una richiesta al
minuto che Live Track Aircraft fa comunque. Ognuno porta un attributo `watch`
che dice perché è mostrato, e un aereo presidenziale il suo nome in
`presidential_airframe`.

⚠ Un aereo presidenziale sulla mappa non dice nulla su chi c'è a bordo.

### L'elenco EnforcementAircraft, e Live Track SALT

[EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)
è un elenco pubblico di aerei usati dall'immigrazione e dalle forze
dell'ordine federali, ogni voce con le sue fonti, pubblicato da
StrausbergAutomationWorks. Dentro la tua zona, un aereo che l'elenco conferma
dalle sue fonti lampeggia in rosso e blu, e un aereo di linea che effettua
voli charter ICE Air tra gli altri lavori ha un alone fisso. Si tengono
sempre, anche quando la tua zona è piena.

Il suo compagno, [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
disegna gli aerei dell'elenco ovunque volino, non solo nella tua zona.
Installali entrambi e ognuno si tiene la sua parte: Live Track Aircraft
disegna ogni aereo dentro la propria zona, compresi quelli dell'elenco, e Live
Track SALT disegna gli aerei dell'elenco ovunque altrove. Condividono una sola
richiesta alle fonti, e nessun aereo è disegnato due volte.

---

## Tutte le entità che crea

Per ogni zona:

| Entità | Cos'è |
|---|---|
| `sensor.aircraft_in_range` | **Aircraft in range**: quanti aerei ci sono adesso dentro il cerchio, tutti, anche quando sono più del massimo. Quello di una seconda zona è `sensor.aircraft_in_range_2`, e così via |
| `geo_location.aircraft_…` | una per aereo, con il nome del suo codice esadecimale (`geo_location.aircraft_a1b2c3`); va e viene con l'aereo. Ognuna porta `source: live_track_aircraft`, e il suo stato è la sua distanza dal centro in chilometri |

Gli attributi del sensore dicono cosa succede: `published_count` (quanti sono
sulla mappa), `capped` (vero quando il massimo ha tagliato l'elenco), `source`
(quale rete ha risposto per ultima), `source_backoff`, `route_artifact`,
`route_download`, `airport_table`, `airport_download`, `route_lookup`,
`watched_count`, `military_in_areas`, `military_by_area`, `followed_asked`,
`followed_found`, `follow_status`, `adsblol_key` e `enforcement_list`.

⚠ **I segnaposto degli aerei non hanno un ID univoco, di proposito.** Una zona
vede migliaia di aerei diversi in un anno, e una riga di registro per ognuno
renderebbe Home Assistant più lento ad avviarsi per niente. Quindi non si
possono rinominare, nascondere o assegnare a un'area nell'interfaccia. I loro
ID entità vengono comunque dal codice esadecimale, quindi lo stesso aereo
riceve sempre lo stesso ID. Il sensore ha un ID univoco e si può rinominare.

⚠ **Il tuo database.** Il recorder di Home Assistant salva una nuova riga ogni
volta che un'entità cambia, e un aereo in volo cambia a ogni aggiornamento,
ogni 15 secondi per impostazione predefinita. Sul nostro sistema di prova, a
settembre 2026, un'entità come queste aggiornata ogni 15 secondi costava circa
9,6 MB al giorno; con 50 aerei sono circa 480 MB al giorno. A meno che tu non
voglia la cronologia di ogni aereo, tienili fuori dal recorder. Aggiungi
questo a `configuration.yaml`, poi riavvia:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.aircraft_*
```

Se il tuo `configuration.yaml` ha già una sezione `recorder:`, aggiungi solo
lo schema `geo_location.aircraft_*`, sotto `exclude:` e `entity_globs:`. Una
scheda mappa impostata per disegnare la cronologia non ha allora nessuna
traccia da disegnare. `sensor.aircraft_in_range` costa poco da tenere: i suoi
attributi assumono pochi valori, quindi il recorder li salva una volta sola.

---

## Cosa invia e scarica

**Sulla tua posizione.** Il centro e il raggio di ogni zona sono inviati ad
adsb.fi a ogni aggiornamento, ogni 15 secondi per impostazione predefinita, e
ad adsb.lol quando adsb.fi non risponde. Il centro è inviato come lo hai
impostato, e parte da casa tua: per smettere di inviare la tua casa, sposta il
centro lontano da essa (**Configura** → **Centre**) o elimina la zona. I codici
esadecimali e i nominativi che segui sono inviati ad adsb.fi (o adsb.lol) una
volta al minuto, e la tua chiave adsb.lol solo ad adsb.lol. I nominativi dei
voli di linea nella tua zona sono inviati ad adsbdb quando FiledRoutesDB non
ha una rotta per loro. Quando qualcuno punta un aereo sulla mappa, il suo
codice esadecimale è inviato a Planespotters.net, al massimo una volta ogni 12
ore per ciascun aereo, e il browser che mostra la mappa carica la foto da lì.
Non c'è ancora un'opzione per fermarlo. Nient'altro su di te è inviato da
nessuna parte. Ogni servizio vede il tuo indirizzo internet, come qualsiasi
sito web.

**Quanto.**

| Fonte | Cosa e ogni quanto | Dopo un errore |
|---|---|---|
| adsb.fi | ogni aereo nel tuo cerchio, a ogni aggiornamento (ogni 15 secondi per impostazione predefinita); una richiesta al minuto per gli aerei seguiti per codice esadecimale e gli aerei presidenziali; una per l'elenco militare; una per tutti i nominativi seguiti insieme, solo se ne segui qualcuno | chiede invece ad adsb.lol. Una fonte che rifiuta con HTTP 429 viene saltata per il tempo che chiede, o per 1 minuto, che raddoppia fino a 10 minuti |
| adsb.lol | le stesse richieste, solo finché adsb.fi non risponde | lo stesso |
| adsbdb | una richiesta per ogni nuovo nominativo di linea per cui FiledRoutesDB non ha una rotta, ad almeno 1 secondo l'una dall'altra; una risposta si tiene 30 giorni, un "nessuna rotta" 24 ore. Le risposte si tengono solo in memoria | non viene richiesto di nuovo per 15 minuti; tutte le richieste si fermano 15 minuti dopo un HTTP 429 |
| Planespotters.net | una richiesta per la foto di un aereo la prima volta che qualcuno lo punta, poi nessuna per quell'aereo per 12 ore. Le risposte si tengono solo in memoria. La foto stessa la carica il browser che mostra la mappa | dopo un HTTP 429 non si chiede nessuna foto per il tempo che chiede Planespotters.net, o per 10 minuti; dopo un HTTP 403, per un giorno |
| FiledRoutesDB, da GitHub | un piccolo file di checksum una volta al giorno, dopo le 14:00 ora di Chicago (Stati Uniti); il file stesso, circa 4,6 MB, solo quando è cambiato | si riprova un'ora dopo; la copia che hai resta in uso finché non scade |
| AirportZones, da GitHub | un piccolo file di checksum una volta al giorno; la tabella stessa, circa 4,8 MB, solo quando è cambiata | si riprova un'ora dopo; la copia che hai resta in uso |
| EnforcementAircraft, da GitHub | un piccolo file di checksum una volta all'ora; l'elenco stesso, piccolo, solo quando è cambiato | la copia che hai resta in uso |
| Registro degli aeromobili della FAA (Stati Uniti) | il registro, circa 73 MB, una volta ogni 7 giorni, da `registry.faa.gov` | si riprova il giorno dopo; la copia che hai resta in uso |

I file scaricati sono condivisi con gli altri moduli di Live Track, quindi
ognuno si scarica una volta sola, qualunque sia il numero di moduli che
installi. Sono tenuti nella cartella `.storage` di Home Assistant, con nomi che
iniziano con `saw_`. Se rimuovi Live Track Aircraft e nessun altro modulo di
Live Track li usa, puoi cancellarli a mano.

---

## Aiutaci a farlo crescere

Live Track Aircraft sta ancora crescendo. Aggiungiamo fonti di rotte, fonti di
dati e dati sugli aerei man mano che li troviamo, e vogliamo sapere cosa ti
piacerebbe in seguito.

### Suggerire qualcosa

Manca il tuo paese, il tuo aeroporto o il tuo tipo di aereo? Qualcosa è
sbagliato, o difficile da capire? Diccelo nel modo più facile per te:

* [**Compila un breve modulo**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=it.yml)
  in italiano. Ti serve un account GitHub gratuito.
* **Scrivi un'email** a
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Non serve un account.

In entrambi i casi, ci aiuta se ci dici:

* cosa ti piacerebbe vedere, e in quale parte del mondo;
* un link a dove sono pubblicati i dati, se ne conosci uno (una pagina di
  dati aperti, un feed pubblico, il sito di un servizio): non è necessario,
  ma aiuta;
* la lingua del tuo Home Assistant, se il problema è la formulazione o una
  traduzione.

Scrivi in inglese o nella tua lingua, come ti è più facile.

### Aggiungerlo tu, con il nostro aiuto

Se vuoi aggiungere qualcosa tu, ti aiuteremo a farlo, dalla prima domanda
alla versione finita. Non serve essere sviluppatori per iniziare:

* **Una traduzione.** I testi della finestra di configurazione sono un breve
  elenco di frasi in un solo file di testo. Ti mostreremo quale file e quali
  righe.
* **Una nuova fonte di dati.** Dicci dove sono pubblicati i dati. Possiamo
  scrivere il codice insieme, o rivedere il tuo.
* **Provarlo dove vivi.** Installalo, guarda la tua parte della mappa e
  dicci cosa va bene e cosa no.
* **Una correzione di questo README.** Se un passo non corrispondeva a ciò
  che hai visto, dicci cosa hai visto.

[**Dicci cosa hai in mente**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=it.yml)
o scrivi a
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
e ti risponderemo con i passi successivi.

---

## Lingue

Questo README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), [Nederlands](README.nl.md),
[简体中文](README.zh-Hans.md), [Español](README.es.md), **Italiano**,
[Dansk](README.da.md). Ogni README tradotto è completo.

La finestra di configurazione e le opzioni sono per ora solo in inglese,
qualunque sia la lingua del tuo Home Assistant. Se parli un'altra lingua, puoi
tradurle tu: è un breve elenco di frasi in un solo file, e [ti aiuteremo a
farlo](#aggiungerlo-tu-con-il-nostro-aiuto).

Hai trovato un errore in una traduzione, o ti serve un'altra lingua? Diccelo
su <https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues>, o
[traducila con il nostro aiuto](#aggiungerlo-tu-con-il-nostro-aiuto).

---

## Riconoscimenti e licenze

* **adsb.fi** (<https://adsb.fi>): posizioni degli aerei, dati aperti solo per
  uso personale e non commerciale, alle condizioni del suo
  [README dei dati aperti](https://github.com/adsbfi/opendata), che chiedono
  di citare adsb.fi e di mettere un link alla sua pagina principale.
  Installando questa integrazione usi adsb.fi, e le sue condizioni si
  applicano a te.
* **adsb.lol** (<https://adsb.lol>): posizioni degli aerei, sotto la
  [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/).
  Installando questa integrazione usi adsb.lol, e le sue condizioni si
  applicano a te. Entrambe le reti sono gestite da volontari: se puoi,
  sostienile fornendo i dati di un ricevitore.
* **FiledRoutesDB** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/FiledRoutesDB)):
  rotte dai piani di volo presentati alla FAA (Stati Uniti), dati sotto
  CC BY 4.0, con l'elenco LADD della FAA applicato prima della pubblicazione.
* **adsbdb** (<https://www.adsbdb.com>): rotte al di fuori di FiledRoutesDB. I
  suoi dati sulle rotte sono opera di David Taylor (Edimburgo) e Jim Mason
  (Glasgow), e non si possono copiare né ripubblicare senza permesso; per
  questo le risposte si tengono solo in memoria, mai scritte in un file, e
  ogni aereo che mostra una rotta di adsbdb li cita.
* **Il registro degli aeromobili della FAA** (Federal Aviation
  Administration, Stati Uniti): nomi dei proprietari e degli operatori degli
  aerei immatricolati negli Stati Uniti, dati pubblici del governo degli Stati
  Uniti. La FAA stessa toglie i nomi che le viene chiesto di non pubblicare
  prima di pubblicare il file.
* **OurAirports** (<https://ourairports.com>), tramite
  [AirportZones](https://github.com/StrausbergAutomationWorks/AirportZones):
  nomi e posizioni degli aeroporti, sotto la ODbL 1.0; fusi orari aggiunti da
  StrausbergAutomationWorks.
* **EnforcementAircraft** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)):
  l'elenco degli aerei dell'immigrazione e delle forze dell'ordine federali,
  sotto la ODbL 1.0.
* **ADS-B Radar** (<https://adsb-radar.com>): le icone degli aerei, dal suo
  [set di icone SVG di aerei](https://adsb-radar.com/help/icons.html) di Jos
  Nutbroek, usate alle sue condizioni, che chiedono questo link. Le icone non
  sono coperte dalla licenza MIT di questo repository. Alcune icone sono state
  disegnate da StrausbergAutomationWorks nello stile del set e donate ad ADS-B
  Radar, quindi sono anch'esse soggette alle sue condizioni. Questa
  integrazione serve le icone con un nuovo riempimento e un nuovo contorno, in
  scala secondo la classe dell'aereo, e anima alcune eliche e alcuni rotori.
  Ogni modifica è elencata in [ATTRIBUTION.md](ATTRIBUTION.md).
* **Planespotters.net** (<https://www.planespotters.net>): le foto degli
  aerei, tramite la sua [API delle
  foto](https://www.planespotters.net/photo/api) e alle sue condizioni. Ogni
  foto è opera del suo fotografo, nominato accanto, e rimanda alla sua pagina
  su Planespotters.net. Nessuna foto è copiata in questo repository, e Home
  Assistant non scarica, non conserva e non inoltra nessuna immagine.
  Installando questa integrazione usi Planespotters.net, e le sue condizioni
  si applicano a te.
* **La scheda mappa** è [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, una copia di [ha-map-card](https://github.com/nathan-gs/ha-map-card) di
  nathan-gs, MIT. Le sue tessere di mappa e i loro riconoscimenti sono nel suo
  README.

Nessuna di queste organizzazioni ha realizzato o approvato questa
integrazione.

**Codice**: MIT, in [LICENSE](LICENSE).

**Per gli sviluppatori:** le entità seguono il contratto di mappa comune di
Live Track, così ogni modulo appare su una sola mappa senza sensori template;
le posizioni arrivano da un'interfaccia delle fonti in
`custom_components/live_track_aircraft/sources/`, così si può aggiungere un
altro flusso di dati senza toccare le entità. I test si eseguono con
`python -m unittest discover -s tests`.

---

## Parole chiave

Home Assistant aerei · Home Assistant tracciamento voli · ADS-B · mappa ADS-B ·
tracciamento voli · radar aerei · aerei sopra di me · MLAT · Mode S ·
rotte dei voli · aerei militari · Air Force One · elicotteri · aircraft ·
flight tracker · Flugzeuge · Flugverfolgung · avions · suivi des vols ·
vliegtuigen · vluchten volgen · 飞机 · 航班跟踪 · aviones ·
seguimiento de vuelos · fly · flysporing · adsb.fi · adsb.lol · adsbdb ·
FiledRoutesDB · registro della FAA · OurAirports · ADS-B Radar ·
Planespotters.net · foto di aerei · geo_location · scheda mappa · Lovelace ·
HACS · Marketplace · Live Track · LiveTrack · StrausbergAutomationWorks

---

**Riconoscimento.** StrausbergAutomationWorks riconosce i popoli indigeni di
tutte le terre e le acque di questa mappa, in tutto il mondo, e rende omaggio ai
loro Anziani del passato e del presente.
