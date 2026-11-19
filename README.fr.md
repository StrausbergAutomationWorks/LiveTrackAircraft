# Live Track Aircraft

[English](README.md) · [Deutsch](README.de.md) · **Français** · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Toutes les langues](#langues)

**Les avions pour Home Assistant, sur une seule carte.** Live Track Aircraft
place sur votre carte Home Assistant les avions qui volent au-dessus de chez
vous, ou au-dessus de tout endroit du monde que vous choisissez : chacun
dessiné selon son type, tourné dans la direction où il vole, avec qui
l'exploite et, quand on le sait, où il va. Il peut aussi suivre des avions et
des vols choisis où qu'ils soient, et surveiller les avions militaires dans
des zones que vous nommez.

> **Live Track Aircraft est un module de Live Track**, une famille
> d'intégrations Home Assistant qui dessinent tout ce qui bouge, et la météo
> qu'il traverse, sur une seule carte partagée : avions, navires, trains et
> météo. Installez-le seul, ou à côté des autres modules
> ([liste ci-dessous](#les-autres-modules-de-live-track)).

> **Il grandit, et vos idées sont les bienvenues.** Live Track Aircraft
> couvre aujourd'hui le monde entier là où des bénévoles font fonctionner des
> récepteurs, avec les routes et les propriétaires les plus détaillés pour les
> États-Unis, et nous ajoutons d'autres sources de routes et d'informations
> sur les avions. Le vôtre manque ? [Proposez-le](#aidez-le-à-grandir), ou
> ajoutez-le vous-même : nous vous aiderons à le faire.

**État : 0.1.1, publié.** Ajouté au Marketplace par son lien
([ci-dessous](#linstaller-étape-par-étape)) ; il n'est pas encore dans le
catalogue du Marketplace.

Travail original de StrausbergAutomationWorks. Sans lien avec adsb.fi,
adsb.lol, adsbdb, la Federal Aviation Administration (États-Unis),
OurAirports, ADS-B Radar, une compagnie aérienne ou un exploitant d'avions,
et sans leur approbation.

> ⚠ **Pas un système de sécurité.** Il montre des données publiques,
> généralement vieilles de quelques secondes et parfois d'une minute ou plus,
> et seulement les avions que les récepteurs des bénévoles entendent. Il ne
> sert ni à la navigation, ni à la séparation des avions, ni à aucun autre
> usage opérationnel.

---

## Sommaire

1. [Tout ce qu'il fait](#tout-ce-quil-fait)
2. [Où il fonctionne](#où-il-fonctionne)
3. [Les autres modules de Live Track](#les-autres-modules-de-live-track)
4. [Avant de commencer](#avant-de-commencer)
5. [L'installer, étape par étape](#linstaller-étape-par-étape)
6. [Le configurer, étape par étape](#le-configurer-étape-par-étape)
7. [Clés gratuites qui activent plus, étape par étape](#clés-gratuites-qui-activent-plus-étape-par-étape)
8. [Mettre la carte sur un tableau de bord](#mettre-la-carte-sur-un-tableau-de-bord)
9. [L'utiliser dans des automatisations](#lutiliser-dans-des-automatisations)
10. [Tout ce qui est sur la carte, en détail](#tout-ce-qui-est-sur-la-carte-en-détail)
11. [Toutes les entités qu'il crée](#toutes-les-entités-quil-crée)
12. [Ce qu'il envoie et télécharge](#ce-quil-envoie-et-télécharge)
13. [Aidez-le à grandir](#aidez-le-à-grandir)
14. [Langues](#langues)
15. [Crédits et licences](#crédits-et-licences)
16. [Mots-clés](#mots-clés)

---

## Tout ce qu'il fait

### Sur la carte, sans rien configurer

Vous ajoutez une **zone** : un centre sur la carte et un rayon autour. Elle
commence chez vous. Tout ce qui suit apparaît alors dans cette zone ou, là où
le tableau le dit, partout dans le monde.

| Quoi | Où | Source |
|---|---|---|
| **Avions** : avions de ligne, avions légers, hélicoptères, planeurs, ballons et drones, chacun dessiné selon son type et tourné dans la direction où il vole | dans chaque zone | adsb.fi, ou adsb.lol quand adsb.fi ne répond pas |
| **Qui l'exploite** : la compagnie, le propriétaire, ou le type quand rien d'autre n'est connu, sur l'étiquette du marqueur | chaque avion | l'indicatif d'appel de la compagnie ; le registre des aéronefs de la FAA (États-Unis) pour les propriétaires |
| **Des couleurs qui disent qui vole** : gouvernement, police, forces de l'ordre fédérales, armée, ambulances aériennes et hélicoptères, chacun dans sa couleur | chaque avion, quand on le sait | le registre des aéronefs de la FAA (États-Unis) et le marquage militaire du flux |
| **Routes** : d'où l'avion a décollé et où il va, avec les noms des aéroports et une heure d'arrivée estimée | les vols dont le plan de vol est déposé auprès de la FAA (États-Unis) ; ailleurs quand adsbdb connaît le vol | FiledRoutesDB, puis adsbdb |
| **Les avions du président des États-Unis**, avec les avions du 89th Airlift Wing et les avions militaires qui les escortent | partout dans le monde | adsb.fi et sa liste militaire |
| **Les avions de la liste publique EnforcementAircraft** (immigration et forces de l'ordre fédérales), avec des feux clignotants | dans chaque zone | la liste EnforcementAircraft |
| **Les avions militaires dans vos zones de surveillance** : chaque avion que le flux marque comme militaire, dans jusqu'à dix cercles que vous nommez, même quand votre zone est pleine. Facultatif : vous saisissez les cercles dans la boîte de dialogue de configuration | partout dans le monde | la liste militaire d'adsb.fi |
| **Les avions et les vols que vous suivez** : votre propre avion, la flotte d'un club, ou le vol d'un membre de la famille. Facultatif : vous saisissez leurs codes dans la boîte de dialogue de configuration | partout dans le monde | adsb.fi |
| **Votre propre image pour un avion**, à la place de son icône | partout où cet avion est montré | une image que vous mettez dans un dossier ([comment](#votre-propre-image-pour-un-avion)) |

### Activé par votre propre clé ou compte gratuit

| Clé ou compte gratuit | Ce qu'il ajoute |
|---|---|
| clé **adsb.lol** | plus de requêtes par jour vers adsb.lol, la deuxième source, pour que la carte continue pendant une longue panne d'adsb.fi |

Chacune s'obtient en quelques minutes : [étape par étape ci-dessous](#clés-gratuites-qui-activent-plus-étape-par-étape).

---

## Où il fonctionne

| Région | Ce que vous obtenez | Source | Il faut |
|---|---|---|---|
| **Le monde entier** | les positions des avions là où des bénévoles font fonctionner des récepteurs : dense au-dessus de l'Europe et de l'Amérique du Nord, plus clairsemé ailleurs, et peu ou rien loin en mer | adsb.fi, adsb.lol | rien |
| **Le monde entier** | les noms des aéroports sur les routes, et leurs fuseaux horaires pour l'heure d'arrivée | OurAirports, par la table AirportZones | rien |
| **Le monde entier** | les routes de nombreux vols de ligne, vérifiées par rapport à l'endroit où l'avion se trouve vraiment | adsbdb | rien |
| **Amérique du Nord** : États-Unis | les noms des propriétaires et exploitants des avions immatriculés aux États-Unis, et les couleurs des avions du gouvernement et de la police | le registre des aéronefs de la FAA | rien |
| **Amérique du Nord** : États-Unis | les routes des vols déposés auprès de la FAA, y compris les vols internationaux vers et depuis les États-Unis | FiledRoutesDB | rien |

Pas dans la liste ? [Dites-le-nous](#aidez-le-à-grandir). Là où quelqu'un
publie les données ouvertement, nous étudierons leur ajout.

⚠ **La couverture est bonne là où il y a des récepteurs, et absente là où il
n'y en a pas.** Un avion n'apparaît que si le récepteur d'un bénévole
l'entend, ou si plusieurs récepteurs ensemble peuvent le localiser. Aucun
réglage ne peut créer une couverture qui n'existe pas. **Un ciel vide sur la
carte peut vouloir dire qu'il n'y a pas de récepteur près de chez vous, pas
qu'il n'y a pas d'avion.**

⚠ **Les routes concernent surtout les États-Unis.** FiledRoutesDB ne contient
que des plans de vol déposés auprès de la FAA. Ailleurs, une route vient
d'adsbdb, qui connaît beaucoup de vols de ligne et peu d'autres, donc hors des
États-Unis beaucoup d'avions n'affichent pas de route.

⚠ **Les noms des propriétaires ne concernent que les avions immatriculés aux
États-Unis.** Un avion immatriculé dans un autre pays affiche sa compagnie
d'après son indicatif d'appel, ou son type.

---

## Les autres modules de Live Track

Live Track est un ensemble d'intégrations Home Assistant, une par type d'objet
en mouvement, toutes dessinées sur la même carte. Chacune fonctionne seule ;
ensemble, elles forment une seule image en direct. Elles partagent la carte et
une bibliothèque Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
donc en installer une autre n'ajoute aucune requête à une source qu'une autre
lit déjà.

| Module | Ce qu'il met sur la carte | État |
|---|---|---|
| **Live Track Aircraft** | les avions au-dessus de vous via l'ADS-B, avec routes et icônes par type (ce module) | publié |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | navires et bateaux via l'AIS, près de chez vous ou n'importe où | publié |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | trains de banlieue en Amérique du Nord, en Europe et en Australie | publié |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | trains intercités et grandes lignes en Amérique du Nord, en Europe et en Australie | publié |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | avions et navires des services d'immigration et des forces de l'ordre fédérales, d'après des listes publiques | publié |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | météo, tempêtes et risques naturels | publié |
| Live Track Stations | tableaux des départs et rappels « il est temps de partir » pour chaque gare | prévu |
| Live Track Satellites | les satellites qui passent au-dessus de vous | prévu |
| Live Track Freight Trains | trains de marchandises et de travaux là où les chemins de fer les publient | prévu |
| Live Track Transit | bus urbains, tramways, ferries et métros | prévu |
| Live Track Intercity Buses | autocars interurbains et régionaux | prévu |
| Live Track Commuter Buses | bus de banlieue | prévu |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | la carte partagée sur laquelle dessine chaque module | publiée, installée avec chaque module |

Tout est gratuit et libre. Rien n'est réservé aux sponsors.

---

## Avant de commencer

* **Home Assistant** 2026.11 ou plus récent.
* **Le Marketplace** (HACS) dans votre Home Assistant, pour l'installer et le
  mettre à jour facilement. Sans lui, vous pouvez copier les fichiers à la
  main.
* **Un accès à Internet** pour Home Assistant : tout vient de sources
  publiques.
* **Facultatif : auto-entities** depuis le Marketplace, pour mettre les
  marqueurs sur la carte (voir
  [Mettre la carte sur un tableau de bord](#mettre-la-carte-sur-un-tableau-de-bord)).
* Rien à payer et aucun compte nécessaire. La clé adsb.lol ci-dessus est
  facultative.
* Home Assistant installe lui-même les deux paquets Python dont il a besoin
  (`saw-livetrack` et `tzfpy`) la première fois que l'intégration se charge.

---

## L'installer, étape par étape

### Depuis le Marketplace (recommandé)

Live Track Aircraft n'est pas encore dans le catalogue du Marketplace.
Ajoutez-le par son lien :

1. Dans Home Assistant, ouvrez **Paramètres → Marketplace** (HACS).
2. Choisissez **Ajouter grâce à un lien** (ou le menu à trois points →
   **Dépôts personnalisés**).
3. Saisissez `StrausbergAutomationWorks/LiveTrackAircraft`. Si le type est
   demandé, choisissez **Integration**.
4. Trouvez **Live Track Aircraft** dans la liste et choisissez
   **Télécharger** ou **Installer**.
5. **Redémarrez Home Assistant** : **Paramètres → Système → Corrections**
   propose le redémarrage, ou utilisez **Paramètres → Système → Redémarrer**.

Le Marketplace propose ensuite chaque nouvelle version comme mise à jour.

### À la main

1. Téléchargez le code source de la
   [dernière version](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/releases/latest).
2. Copiez son dossier `custom_components/live_track_aircraft` dans le dossier
   `custom_components` du dossier de configuration de votre Home Assistant
   (créez `custom_components` s'il n'existe pas).
3. Redémarrez Home Assistant.

Pour mettre à jour à la main, remplacez le dossier par celui de la nouvelle
version et redémarrez.

---

## Le configurer, étape par étape

La boîte de dialogue de configuration est en anglais. Ses champs sont nommés
ici comme elle les affiche.

1. Ouvrez **Paramètres → Appareils et services**.
2. Choisissez **Ajouter une intégration** (en bas à droite) et cherchez
   **Live Track Aircraft**.
3. **Centre** (le centre) : faites glisser le marqueur au milieu du ciel que
   vous voulez surveiller. Il commence chez vous.
4. **Radius (km)** (le rayon) : jusqu'où autour du centre les avions sont
   montrés, de 1 à 463 km (0,6 à 288 milles). Dans le doute, gardez 56 km
   (35 milles).
5. **Update interval (seconds)** (l'intervalle de mise à jour) : gardez 15.
   Les sources refusent les requêtes plus fréquentes.
6. **Maximum aircraft published** (le nombre maximal d'avions publiés) :
   gardez 250. C'est une limite de sécurité, pas un moyen de montrer moins
   d'avions.
7. Laissez vides pour l'instant les quatre champs facultatifs. Chacun est
   expliqué plus bas.
8. Choisissez **Valider**.

C'est tout. Les avions apparaissent en moins d'une minute. Chaque zone est une
entrée, intitulée d'après son centre et son rayon, par exemple
`39.817, -84.050 - 56 km`. Pour surveiller une deuxième zone, ajoutez de
nouveau l'intégration avec un autre centre ou un autre rayon. Le même centre
et le même rayon deux fois sont refusés.

Les routes, les noms des aéroports et les propriétaires se remplissent pendant
les premières minutes, à mesure que les fichiers d'où ils viennent se
téléchargent ([Ce qu'il envoie et télécharge](#ce-quil-envoie-et-télécharge)).

### Changer ce qu'il montre : les options

Ouvrez **Paramètres → Appareils et services → Live Track Aircraft →
Configurer** (la roue dentée) sur la zone à modifier. Chaque option, en mots
simples :

| Option | Ce qu'elle fait | Par défaut |
|---|---|---|
| **Centre** | déplace la zone ; son titre suit | chez vous |
| **Radius (km)** | jusqu'où autour du centre les avions sont montrés, de 1 à 463 km (0,6 à 288 milles) | 56 km (35 milles) |
| **Update interval (seconds)** | la fréquence à laquelle les positions sont demandées, de 15 à 3 600 secondes | 15 |
| **Maximum aircraft published** | une limite de sécurité, de 1 à 1 000 ; quand il y a plus d'avions dans le cercle, les plus proches sont gardés. Les avions que vous suivez, ceux de vos zones de surveillance militaire et ceux de la liste EnforcementAircraft sont toujours gardés | 250 |
| **Military watch areas** | des cercles où chaque avion militaire est montré ([comment](#zones-de-surveillance-militaire)) | vide |
| **Aircraft to follow (hex codes)** | des avions suivis partout, d'après leur code hexadécimal ([comment](#les-avions-et-les-vols-que-vous-suivez)) | vide |
| **Flights to follow (call signs)** | des vols suivis partout, d'après leur indicatif d'appel (même section) | vide |
| **adsb.lol API key** | votre propre clé pour adsb.lol ([comment en obtenir une](#clés-gratuites-qui-activent-plus-étape-par-étape)) | vide |

Videz l'un des quatre champs facultatifs pour désactiver cette partie.

---

## Clés gratuites qui activent plus, étape par étape

Elles sont toutes gratuites et personnelles : chaque personne qui installe
Live Track Aircraft obtient la sienne. Collez chacune dans **Paramètres →
Appareils et services → Live Track Aircraft → Configurer**.

### adsb.lol (plus de requêtes vers la deuxième source, le monde entier)

Live Track Aircraft interroge d'abord adsb.fi, et n'interroge adsb.lol que
tant qu'adsb.fi ne répond pas. Sans clé, adsb.lol autorise 500 requêtes par
jour depuis une même adresse Internet, qu'une panne d'adsb.fi peut épuiser en
environ deux heures. Une clé relève cette limite. Vous n'en avez pas besoin
pour commencer.

1. Ouvrez <https://www.adsb.lol/request> et demandez une clé gratuite avec le
   formulaire de cette page. La documentation d'adsb.lol donne à cette clé
   1 000 requêtes par jour.
2. Si vous alimentez adsb.lol avec votre propre récepteur, utilisez plutôt
   votre clé de contributeur (feeder) : la documentation d'adsb.lol lui donne
   7 200 requêtes par jour. Vos clés sont sous **My keys** sur adsb.lol
   (<https://www.adsb.lol/mmb>).
3. Collez la clé dans **adsb.lol API key**, et choisissez **Valider**.

La clé n'est envoyée qu'à adsb.lol. Si adsb.lol la refuse (fausse ou
expirée), Live Track Aircraft continue sans elle, et le
`sensor.aircraft_in_range` de la zone affiche `refused` dans son attribut
`adsblol_key` jusqu'à ce que vous changiez la clé. Sinon il affiche `set`, ou
`none` sans clé. Aucun mot de passe ni secret n'est nécessaire.

---

## Mettre la carte sur un tableau de bord

La carte est [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
la carte sur laquelle dessine chaque module Live Track. **Elle est installée
avec Live Track Aircraft** : rien à télécharger, rien à copier, aucune
ressource à ajouter.

1. Ouvrez un tableau de bord, choisissez le crayon (**Modifier le tableau de
   bord**), puis **Ajouter une carte**.
2. Faites défiler jusqu'en bas et choisissez **Manuel**.
3. Collez ceci, et choisissez **Enregistrer** :

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

Les marqueurs ont besoin
d'[auto-entities](https://github.com/thomasloven/lovelace-auto-entities)
depuis le Marketplace. Avec d'autres modules Live Track installés, ajoutez un
filtre `- domain: geo_location` de plus pour chacune de leurs sources
(`live_track_ships`, `live_track_weather` et ainsi de suite).

**Sur la carte :**

* Chaque avion est dessiné selon son type, tourné dans la direction où il
  vole, et se déplace en douceur entre les positions qu'il transmet.
* Son étiquette est l'indicatif d'appel du vol (`UAL308`), sinon qui
  l'exploite (`Lewis University`), sinon son type (`Cessna 172 Skyhawk`).
* **Pointez** un avion pour voir sa compagnie ou son exploitant et, quand une
  route est connue, sa route et le nombre de minutes avant son arrivée.
  **Cliquez** dessus pour tous ses détails.

Si les ressources de vos tableaux de bord sont définies en YAML
(`lovelace: resource_mode: yaml`), rien ne peut être enregistré pour vous : un
problème sous **Corrections** donne alors la ligne exacte à ajouter. Une carte
que vous avez installée vous-même par le Marketplace n'est pas touchée. Si les
fichiers de l'intégration sont supprimés alors que ses zones sont encore
configurées, et qu'aucun autre module Live Track n'est installé, supprimez
vous-même la ligne de la carte dans **Paramètres → Tableaux de bord →
Ressources**. Toute autre carte qui affiche les entités `geo_location` affiche
aussi les avions, comme de simples marqueurs.

---

## L'utiliser dans des automatisations

Tout est une entité Home Assistant ordinaire, donc l'éditeur d'automatisations
fonctionne avec, sans code.

**Une notification sur le téléphone quand un avion militaire est dans l'une de
vos zones de surveillance militaire :**

1. **Paramètres → Automatisations et scènes → Créer une automatisation →
   Créer une nouvelle automatisation**.
2. **Quand** : **Ajouter un déclencheur** → **Entité** → **État numérique**.
   Choisissez l'entité **Aircraft in range**, l'**Attribut** **Military in
   areas** (`military_in_areas`), et **Au-dessus de** `0`.
3. **Alors faire** : **Ajouter une action**, cherchez l'action de notification
   de votre téléphone (elle porte le nom de votre téléphone), et saisissez un
   message, par exemple :

   ```text
   Un avion militaire est dans votre zone de surveillance
   ```

4. **Enregistrer**.

Il faut pour cela au moins une zone de surveillance militaire
([comment](#zones-de-surveillance-militaire)).

**Autres idées :** une notification quand le vol d'un membre de la famille est
en l'air, quand l'attribut `followed_found` dépasse 0 ; une lampe qui
s'allume quand plus de 20 avions survolent votre maison à Francfort
(Allemagne) ; un compteur sur le tableau de bord des avions au-dessus de
votre aérodrome dans le Queensland (Australie), d'après
`sensor.aircraft_in_range` ; un message quand l'avion de votre club décolle,
quand sa propre entité (`geo_location.aircraft_` et son code hexadécimal)
apparaît.

---

## Tout ce qui est sur la carte, en détail

### Avions

Les avions transmettent leur position par radio, un système appelé ADS-B. Des
bénévoles du monde entier font fonctionner des récepteurs et partagent ce
qu'ils entendent par des réseaux communautaires. Live Track Aircraft demande à
l'un d'eux, adsb.fi, chaque avion dans votre cercle, toutes les 15 secondes
par défaut. Quand adsb.fi ne répond pas, ou répond avec bien moins d'avions
qu'un instant plus tôt, il interroge adsb.lol. Là où plusieurs récepteurs
entendent un avion qui ne transmet pas sa propre position, les réseaux peuvent
quand même le localiser (multilatération, MLAT).

Chaque avion est un marqueur, nommé d'après son code hexadécimal : l'adresse
de six caractères que son transpondeur transmet, qui appartient à l'avion et
ne change pas. Le marqueur apparaît quand l'avion entre dans votre cercle et
disparaît quand il en sort.

L'étiquette est le nom le plus utile connu, dans cet ordre :

| L'avion a | L'étiquette montre | Exemple |
|---|---|---|
| l'indicatif d'appel d'un vol | l'indicatif | `UAL308` |
| sinon un exploitant connu | l'exploitant | `Lewis University` |
| sinon un type connu | le type | `Cessna 172 Skyhawk` |
| rien de tout cela | l'immatriculation, le code de type ou le code hexadécimal | `N12345` |

⚠ Non montrés : les avions au sol, les véhicules d'aéroport, et les pistes
radar seules sans identité. Un avion qui ne transmet pas, ou qui vole là où
aucun récepteur ne l'entend, ne peut pas être montré.

Sur chaque avion : `identity` (le code hexadécimal), `callsign`,
`registration`, `aircraft_type`, `aircraft_name`, `operator`, `altitude_m`,
`speed_kmh`, `vertical_rate_ms`, `course_deg`, `squawk`, `emitter_category`,
`is_military`, `is_government`, `last_seen`.

### Couleurs et icônes

Chaque avion est dessiné selon son type : un avion de ligne, un avion
d'affaires, un monomoteur léger, un bimoteur, un hélicoptère, un convertible
à rotors basculants, un planeur, un ballon, un drone et bien d'autres, à la
taille de sa catégorie. Les hélices et les rotors tournent. L'icône est
tournée dans la direction où vole l'avion ; un avion lent garde sa dernière
direction au lieu de tourner sur lui-même.

La couleur dit qui vole, quand on le sait :

| Couleur | Qui |
|---|---|
| gris clair | la plupart des avions |
| vert menthe | les hélicoptères et autres giravions |
| ambre | les avions du gouvernement et les ambulances aériennes |
| bleu | les forces de l'ordre fédérales |
| vert armée | l'armée et la garde côtière |
| blanc, avec des feux bleus clignotants | la police |
| des feux rouges et bleus clignotants | les avions de la liste EnforcementAircraft ([plus bas](#la-liste-enforcementaircraft-et-live-track-salt)) |
| une lueur fixe | un avion de ligne qui effectue des vols charter pour ICE Air, entre autres travaux |

⚠ À qui appartient un avion n'est connu surtout que pour les avions
immatriculés aux États-Unis, d'après le registre de la FAA. Ailleurs, la
couleur vient seulement du marquage militaire du flux et du type de l'avion.

### Routes et heures d'arrivée

Une route montre d'où l'avion a décollé et où il va, avec les noms des deux
aéroports, et une heure d'arrivée estimée. Elle vient de deux sources :

1. **FiledRoutesDB**, un fichier public de plans de vol déposés auprès de la
   FAA (États-Unis), construit et publié par StrausbergAutomationWorks et
   téléchargé une fois par jour. Chaque route est vérifiée par rapport à
   l'endroit où se trouve l'avion et à la direction dans laquelle il vole.
   Une route qui ne correspond pas est quand même montrée, et marquée comme
   ne correspondant pas dans `route_check`.
2. **adsbdb**, interrogé seulement quand FiledRoutesDB n'a pas de route pour
   l'indicatif, une fois par indicatif. Sa réponse n'est montrée que si elle
   correspond à l'endroit où se trouve vraiment l'avion.

Les avions dont les propriétaires ont demandé à la FAA de ne pas montrer leurs
vols au public (la liste LADD de la FAA, Limiting Aircraft Data Displayed) sont
retirés de FiledRoutesDB avant sa publication. Live Track Aircraft supprime sa
copie quand le fichier expire, ou quand la liste LADD avec laquelle il a été
construit a plus de 14 jours, pour ne jamais montrer de routes filtrées avec
une ancienne liste.

L'heure d'arrivée est une estimation, pas un horaire : la distance restante en
ligne droite, à la vitesse de l'avion quand il est en croisière, et à une
vitesse typique de sa catégorie sinon. L'attente, l'approche et le roulage ne
sont pas comptés.

Sur chaque avion qui a une route : `origin_icao`, `destination_icao`,
`origin_name`, `destination_name`, `route_source`, `route_check`,
`arrival_estimated_at`.

### Zones de surveillance militaire

Chaque avion que le flux marque comme militaire, dans des cercles que vous
choisissez, partout dans le monde, même quand votre zone est pleine.

1. Ouvrez **Paramètres → Appareils et services → Live Track Aircraft →
   Configurer** sur une zone.
2. Dans **Military watch areas**, saisissez chaque cercle sous la forme
   `latitude,longitude,km`, et séparez les cercles par des points-virgules,
   par exemple `39.81,-84.04,150; 34.0,-117.8,463`. Jusqu'à dix cercles,
   chacun de 1 à 2 000 km (0,6 à 1 243 milles). Écrivez les décimales avec un
   point.
3. Choisissez **Valider**.

Les avions militaires qui s'y trouvent apparaissent en moins d'une minute et
bougent une fois par minute. Chacun porte `watch: military area`. Le
`sensor.aircraft_in_range` de la zone les compte dans `military_in_areas`, et
par cercle dans `military_by_area`. Videz le champ pour arrêter.

⚠ Il ne montre que ce qui transmet et est marqué comme militaire. Les vols
militaires peuvent voler transpondeur éteint, et un avion militaire sous une
immatriculation civile n'est pas marqué.

### Les avions et les vols que vous suivez

Live Track Aircraft peut suivre des avions que vous choisissez où qu'ils
soient dans le monde, pas seulement dans votre cercle : votre propre avion, la
flotte d'un club ou d'une entreprise, ou le vol d'un membre de la famille.

1. Ouvrez **Paramètres → Appareils et services → Live Track Aircraft →
   Configurer** sur la zone avec laquelle vous voulez les voir.
2. Remplissez **Aircraft to follow (hex codes)**, **Flights to follow (call
   signs)**, ou les deux.
3. Choisissez **Valider**. Ils apparaissent en une minute environ.

**Un seul code par avion suffit.** Choisissez selon ce que vous voulez
suivre :

| Pour suivre | Utilisez | Exemple |
|---|---|---|
| un avion, quel que soit le vol qu'il effectue (votre propre avion, une flotte) | son **code hexadécimal** | `a1b2c3` |
| un vol, quel que soit l'avion qui l'effectue (le voyage d'un proche) | son **indicatif d'appel** | `UAL1234` |

Saisir les deux codes pour le même avion ne fait pas de mal (il est dessiné
une fois) mais n'ajoute rien.

**Saisir les codes :**

* Séparez les codes par des virgules : `a1b2c3, a4b5c6, a7b8c9`. Des espaces
  ou des points-virgules entre les codes marchent aussi.
* Un code hexadécimal fait exactement six caractères : les chiffres 0 à 9 et
  les lettres a à f, en majuscules ou en minuscules.
* Un indicatif d'appel fait 2 à 8 lettres et chiffres, saisis comme l'avion
  les transmet, sans espace ni tiret : `UAL1234`, et non `UA 1234` ou
  `UAL-1234`.
* Jusqu'à 100 codes hexadécimaux et 100 indicatifs. Un code saisi deux fois
  compte une fois.
* Si un code est faux, la boîte de dialogue refuse ce champ, dit à quoi
  ressemble un bon code, et n'enregistre rien tant qu'il n'est pas corrigé.

**Trouver les codes.** Chaque avion sur la carte porte son code hexadécimal
dans son attribut `identity` et son indicatif dans son attribut `callsign`.
Pour un avion immatriculé aux États-Unis, la recherche par numéro N du
registre de la FAA affiche le code hexadécimal comme « Mode S Code (Base 16 /
Hex) ». Pour un vol de ligne, l'indicatif est en général le code à trois
lettres de la compagnie suivi du numéro de vol, ce qui n'est pas ce
qu'indique le billet :

| Billet | Indicatif |
|---|---|
| United UA 1234 | `UAL1234` |
| Delta DL 89 | `DAL89` |
| American AA 100 | `AAL100` |

Certaines compagnies transmettent un indicatif qui n'est pas le numéro de vol.
Si un vol n'apparaît pas, cherchez-le sur une carte des vols en direct et
copiez l'indicatif qui y est affiché. Un indicatif est réutilisé : le même
indicatif demain est un autre voyage, et peut-être un autre avion. Il reste
suivi jusqu'à ce que vous le retiriez.

**Ce que vous voyez.** Chaque avion suivi est dessiné avec son icône et son
étiquette habituelles où qu'il soit, même quand votre zone est pleine. Son
attribut `watch` vaut `followed`, et `outside_radius` dit s'il est hors de
votre cercle. Hors de votre cercle, il bouge une fois par minute ; dedans,
aussi souvent que tout le reste. Le `sensor.aircraft_in_range` de la zone
affiche `followed_asked` (combien de codes vous suivez), `followed_found`
(combien sont en l'air maintenant) et `follow_status` (la dernière requête
d'indicatifs : `ok`, ou ce qui n'a pas marché).

**Pour arrêter**, retirez le code, ou videz le champ, et choisissez
**Valider**.

⚠ Seuls les avions qui transmettent l'ADS-B, ou que la MLAT peut localiser,
peuvent être trouvés. Un avion au sol ou hors de la couverture des récepteurs
n'est pas montré, et `followed_found` ne le compte pas. Les horaires et les
retards par numéro de vol n'en font pas partie.

### Votre propre image pour un avion

Mettez une image de votre choix à la place de l'icône d'un avion, par exemple
votre propre avion.

1. Dans le dossier de configuration de votre Home Assistant (celui qui
   contient `configuration.yaml`), créez un dossier nommé
   `live_track_aircraft_pictures`.
2. Mettez-y l'image, nommée d'après le code hexadécimal de l'avion :
   `a1b2c3.png`. Les fichiers PNG, JPG, WebP, GIF et SVG fonctionnent,
   jusqu'à 2 Mo chacun.

L'image apparaît en moins d'une minute, de même qu'un changement ou une
suppression. Elle est dessinée droite, sans rotation, parce qu'une photo n'est
pas dessinée le nez vers le haut. L'attribut `picture_source` de l'avion vaut
alors `override`.

⚠ Ces images sont servies sans connexion, comme les icônes : quiconque peut
joindre votre Home Assistant par son adresse peut les ouvrir. N'y mettez pas
d'image privée.

### Les avions du président

Les avions qu'utilise le président des États-Unis sont montrés partout dans le
monde, d'après leurs codes hexadécimaux, jamais d'après leur indicatif, avec
les avions du 89th Airlift Wing (indicatifs SAM et VENUS) et les avions
militaires qui escortent un avion présidentiel. Ils viennent d'une requête par
minute que Live Track Aircraft fait de toute façon. Chacun porte un attribut
`watch` qui dit pourquoi il est montré, et un avion présidentiel son nom dans
`presidential_airframe`.

⚠ Un avion présidentiel sur la carte ne dit rien de qui est à bord.

### La liste EnforcementAircraft et Live Track SALT

[EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)
est une liste publique d'avions utilisés par les services d'immigration et les
forces de l'ordre fédérales, chaque entrée avec ses sources, publiée par
StrausbergAutomationWorks. Dans votre zone, un avion que la liste confirme
d'après ses sources clignote en rouge et bleu, et un avion de ligne qui
effectue des vols charter pour ICE Air, entre autres travaux, a une lueur
fixe. Ils sont toujours gardés, même quand votre zone est pleine.

Son compagnon, [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
dessine les avions de la liste où qu'ils volent, pas seulement dans votre
zone. Installez les deux et chacun s'en tient à sa partie : Live Track
Aircraft dessine chaque avion dans sa propre zone, ceux de la liste compris,
et Live Track SALT dessine les avions de la liste partout ailleurs. Ils
partagent une seule requête aux sources, et aucun avion n'est dessiné deux
fois.

---

## Toutes les entités qu'il crée

Pour chaque zone :

| Entité | Ce que c'est |
|---|---|
| `sensor.aircraft_in_range` | **Aircraft in range** : combien d'avions sont dans le cercle maintenant, tous, même au-delà du maximum. Celui d'une deuxième zone est `sensor.aircraft_in_range_2`, et ainsi de suite |
| `geo_location.aircraft_…` | une par avion, nommée d'après son code hexadécimal (`geo_location.aircraft_a1b2c3`) ; elle va et vient avec l'avion. Chacune porte `source: live_track_aircraft`, et son état est sa distance au centre en kilomètres |

Les attributs du capteur disent ce qui se passe : `published_count` (combien
sont sur la carte), `capped` (vrai quand le maximum a coupé la liste),
`source` (quel réseau a répondu en dernier), `source_backoff`,
`route_artifact`, `route_download`, `airport_table`, `airport_download`,
`route_lookup`, `watched_count`, `military_in_areas`, `military_by_area`,
`followed_asked`, `followed_found`, `follow_status`, `adsblol_key` et
`enforcement_list`.

⚠ **Les marqueurs des avions n'ont pas d'identifiant unique, volontairement.**
Une zone voit des milliers d'avions différents en un an, et une ligne de
registre pour chacun ralentirait le démarrage de Home Assistant pour rien. Ils
ne peuvent donc pas être renommés, masqués ou attribués à une pièce dans
l'interface. Leurs identifiants d'entité viennent quand même du code
hexadécimal, donc le même avion reçoit toujours le même identifiant. Le
capteur a un identifiant unique et peut être renommé.

⚠ **Votre base de données.** L'enregistreur de Home Assistant stocke une
nouvelle ligne chaque fois qu'une entité change, et un avion en vol change à
chaque mise à jour, toutes les 15 secondes par défaut. Sur notre système de
test, en septembre 2026, une entité comme celles-ci mise à jour toutes les 15
secondes coûtait environ 9,6 Mo par jour ; pour 50 avions, cela fait environ
480 Mo par jour. Sauf si vous voulez l'historique de chaque avion, tenez-les
hors de l'enregistreur. Ajoutez ceci à `configuration.yaml`, puis
redémarrez :

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.aircraft_*
```

Si votre `configuration.yaml` a déjà une section `recorder:`, ajoutez-y
seulement le motif `geo_location.aircraft_*`, sous `exclude:` et
`entity_globs:`. Une carte réglée pour dessiner l'historique n'a alors plus de
trace à dessiner. `sensor.aircraft_in_range` coûte peu : ses attributs
prennent peu de valeurs, donc l'enregistreur les stocke une fois.

---

## Ce qu'il envoie et télécharge

**À propos de votre position.** Le centre et le rayon de chaque zone sont
envoyés à adsb.fi à chaque mise à jour, toutes les 15 secondes par défaut, et
à adsb.lol quand adsb.fi ne répond pas. Le centre est envoyé tel que vous
l'avez réglé, et il commence chez vous : pour ne plus envoyer votre domicile,
éloignez-en le centre (**Configurer** → **Centre**) ou supprimez la zone. Les
codes hexadécimaux et les indicatifs que vous suivez sont envoyés à adsb.fi
(ou adsb.lol) une fois par minute, et votre clé adsb.lol seulement à adsb.lol.
Les indicatifs des vols de ligne dans votre zone sont envoyés à adsbdb quand
FiledRoutesDB n'a pas de route pour eux. Rien d'autre vous concernant n'est
envoyé nulle part. Chaque service voit votre adresse Internet, comme tout site
web.

**Combien.**

| Source | Quoi et à quelle fréquence | Après une erreur |
|---|---|---|
| adsb.fi | chaque avion dans votre cercle, à chaque mise à jour (toutes les 15 secondes par défaut) ; une requête par minute pour les avions suivis par code hexadécimal et les avions du président ; une pour la liste militaire ; une pour tous les indicatifs suivis ensemble, seulement si vous en suivez | interroge adsb.lol à la place. Une source qui refuse avec HTTP 429 est sautée pendant le temps qu'elle demande, ou pendant 1 minute, doublée jusqu'à 10 minutes |
| adsb.lol | les mêmes requêtes, seulement tant qu'adsb.fi ne répond pas | pareil |
| adsbdb | une requête par nouvel indicatif de compagnie pour lequel FiledRoutesDB n'a pas de route, à au moins 1 seconde d'intervalle ; une réponse est gardée 30 jours, une « pas de route » 24 heures. Les réponses sont gardées en mémoire seulement | pas interrogé de nouveau pendant 15 minutes ; toutes les requêtes s'arrêtent 15 minutes après HTTP 429 |
| FiledRoutesDB, depuis GitHub | un petit fichier de sommes de contrôle une fois par jour, après 14:00 heure de Chicago (États-Unis) ; le fichier lui-même, environ 4,6 Mo, seulement s'il a changé | réessayé une heure plus tard ; votre copie reste utilisée jusqu'à son expiration |
| AirportZones, depuis GitHub | un petit fichier de sommes de contrôle une fois par jour ; la table elle-même, environ 4,8 Mo, seulement si elle a changé | réessayé une heure plus tard ; votre copie reste utilisée |
| EnforcementAircraft, depuis GitHub | un petit fichier de sommes de contrôle une fois par heure ; la liste elle-même, petite, seulement si elle a changé | votre copie reste utilisée |
| Registre des aéronefs de la FAA (États-Unis) | le registre, environ 73 Mo, une fois tous les 7 jours, depuis `registry.faa.gov` | réessayé le lendemain ; votre copie reste utilisée |

Les fichiers téléchargés sont partagés avec les autres modules Live Track,
donc chacun n'est téléchargé qu'une fois, quel que soit le nombre de modules
installés. Ils sont gardés dans le dossier `.storage` de Home Assistant sous
des noms commençant par `saw_`. Si vous retirez Live Track Aircraft et
qu'aucun autre module Live Track ne les utilise, vous pouvez les supprimer à
la main.

---

## Aidez-le à grandir

Live Track Aircraft continue de grandir. Nous ajoutons des sources de routes,
des sources de données et des informations sur les avions à mesure que nous
les trouvons, et nous voulons savoir ce que vous aimeriez ensuite.

### Proposer quelque chose

Votre pays, votre aéroport ou votre type d'avion manque ? Quelque chose est
faux, ou difficile à comprendre ? Dites-le-nous de la façon la plus simple
pour vous :

* [**Remplissez un court formulaire**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=fr.yml)
  en français. Il vous faut un compte GitHub gratuit.
* **Écrivez un e-mail** à
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Aucun compte n'est nécessaire.

Dans les deux cas, il nous aide que vous nous disiez :

* ce que vous aimeriez voir, et où dans le monde ;
* un lien vers l'endroit où les données sont publiées, si vous en connaissez
  un (une page de données ouvertes, un flux public, le site d'un service) : ce
  n'est pas nécessaire, mais cela aide ;
* la langue de votre Home Assistant, si le problème concerne la formulation ou
  une traduction.

Écrivez en anglais ou dans votre propre langue, ce qui est le plus simple pour
vous.

### L'ajouter vous-même, avec notre aide

Si vous souhaitez ajouter quelque chose vous-même, nous vous aiderons à le
faire, de la première question jusqu'à la version terminée. Vous n'avez pas
besoin d'être développeur pour commencer :

* **Une traduction.** Les textes de la boîte de dialogue de configuration sont
  une courte liste de phrases dans un seul fichier texte. Nous vous montrerons
  quel fichier et quelles lignes.
* **Une nouvelle source de données.** Dites-nous où les données sont publiées.
  Nous pouvons écrire le code ensemble, ou relire le vôtre.
* **Le tester là où vous habitez.** Installez-le, regardez votre partie de la
  carte, et dites-nous ce qui est juste et ce qui ne l'est pas.
* **Une correction de ce README.** Si une étape ne correspondait pas à ce que
  vous avez vu, dites-nous ce que vous avez vu.

[**Dites-nous ce que vous avez en tête**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=fr.yml)
ou écrivez à
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
et nous vous répondrons avec les prochaines étapes.

---

## Langues

Ce README : [English](README.md), [Deutsch](README.de.md), **Français**,
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md).
Chaque README traduit est complet.

La boîte de dialogue de configuration et les options sont pour l'instant en
anglais seulement, quelle que soit la langue de votre Home Assistant. Si vous
parlez une autre langue, vous pouvez les traduire vous-même : c'est une courte
liste de phrases dans un seul fichier, et [nous vous aiderons à le
faire](#lajouter-vous-même-avec-notre-aide).

Vous avez trouvé une erreur dans une traduction, ou il vous faut une autre
langue ? Dites-le-nous sur
<https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues>, ou
[traduisez-le avec notre aide](#lajouter-vous-même-avec-notre-aide).

---

## Crédits et licences

* **adsb.fi** (<https://adsb.fi>) : les positions des avions, données ouvertes
  pour un usage personnel et non commercial seulement, selon les conditions de
  son [README de données ouvertes](https://github.com/adsbfi/opendata), qui
  demandent de citer adsb.fi et de mettre un lien vers sa page d'accueil. En
  installant cette intégration, vous utilisez adsb.fi, et ses conditions
  s'appliquent à vous.
* **adsb.lol** (<https://adsb.lol>) : les positions des avions, sous
  l'[Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/).
  En installant cette intégration, vous utilisez adsb.lol, et ses conditions
  s'appliquent à vous. Les deux réseaux sont gérés par des bénévoles : si vous
  le pouvez, soutenez-les en leur fournissant les données d'un récepteur.
* **FiledRoutesDB** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/FiledRoutesDB)) :
  routes tirées des plans de vol déposés auprès de la FAA (États-Unis),
  données sous CC BY 4.0, avec la liste LADD de la FAA appliquée avant la
  publication.
* **adsbdb** (<https://www.adsbdb.com>) : routes hors de FiledRoutesDB. Ses
  données de routes sont l'œuvre de David Taylor (Édimbourg) et Jim Mason
  (Glasgow), et ne peuvent pas être copiées ni republiées sans autorisation ;
  les réponses sont donc gardées en mémoire seulement, jamais écrites dans un
  fichier, et chaque avion qui montre une route d'adsbdb les cite.
* **Le registre des aéronefs de la FAA** (Federal Aviation Administration,
  États-Unis) : les noms des propriétaires et exploitants des avions
  immatriculés aux États-Unis, données publiques du gouvernement des
  États-Unis. La FAA retire elle-même les noms qu'on lui demande de ne pas
  publier avant de publier le fichier.
* **OurAirports** (<https://ourairports.com>), par
  [AirportZones](https://github.com/StrausbergAutomationWorks/AirportZones) :
  noms et positions des aéroports, sous l'ODbL 1.0 ; fuseaux horaires ajoutés
  par StrausbergAutomationWorks.
* **EnforcementAircraft** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)) :
  la liste des avions des services d'immigration et des forces de l'ordre
  fédérales, sous l'ODbL 1.0.
* **ADS-B Radar** (<https://adsb-radar.com>) : les icônes des avions, tirées
  de son [jeu d'icônes SVG d'avions](https://adsb-radar.com/help/icons.html)
  par Jos Nutbroek, utilisées selon ses conditions, qui demandent ce lien. Les
  icônes ne sont pas couvertes par la licence MIT de ce dépôt. Certaines
  icônes ont été dessinées par StrausbergAutomationWorks dans le style du jeu
  et données à ADS-B Radar, donc ses conditions s'appliquent aussi à elles.
  Cette intégration sert les icônes avec un nouveau remplissage et un contour,
  à l'échelle de la catégorie de l'avion, et anime certaines hélices et
  certains rotors. Chaque changement est listé dans
  [ATTRIBUTION.md](ATTRIBUTION.md).
* **La carte** est [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, une copie de [ha-map-card](https://github.com/nathan-gs/ha-map-card)
  de nathan-gs, MIT. Ses fonds de carte et leurs crédits sont dans son README.

Aucune de ces organisations n'a créé ni approuvé cette intégration.

**Code** : MIT, dans [LICENSE](LICENSE).

**Pour les développeurs :** les entités suivent le contrat de carte commun de
Live Track, donc chaque module s'affiche sur une seule carte sans capteurs de
modèle ; les positions passent par une interface de sources dans
`custom_components/live_track_aircraft/sources/`, donc un autre flux peut être
ajouté sans toucher aux entités. Les tests se lancent avec
`python -m unittest discover -s tests`.

---

## Mots-clés

Home Assistant avions · Home Assistant suivi des vols · ADS-B · carte ADS-B ·
suivi des vols · radar d'avions · avions au-dessus de moi · MLAT · Mode S ·
routes aériennes · avions militaires · Air Force One · hélicoptères ·
aircraft · flight tracker · Flugzeuge · Flugverfolgung · vliegtuigen ·
vluchten volgen · 飞机 · 航班跟踪 · aviones · seguimiento de vuelos ·
aerei · tracciamento voli · fly · flysporing · adsb.fi · adsb.lol · adsbdb ·
FiledRoutesDB · registre de la FAA · OurAirports · ADS-B Radar ·
geo_location · carte · Lovelace · HACS · Marketplace · Live Track ·
LiveTrack · StrausbergAutomationWorks

---

**Reconnaissance.** StrausbergAutomationWorks reconnaît les peuples autochtones
de toutes les terres et de toutes les eaux de cette carte, partout dans le
monde, et rend hommage à leurs Aînés d'hier et d'aujourd'hui.
