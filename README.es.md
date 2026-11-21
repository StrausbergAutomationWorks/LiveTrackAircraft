# Live Track Aircraft

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · **Español** · [Italiano](README.it.md) · [Dansk](README.da.md) · [Todos los idiomas](#idiomas)

**Aviones para Home Assistant, en un solo mapa.** Live Track Aircraft pone en
tu mapa de Home Assistant los aviones que vuelan sobre tu casa, o sobre
cualquier lugar del mundo que elijas: cada uno dibujado como su propio tipo,
girado hacia donde vuela, con quién lo opera y, cuando se sabe, adónde va.
También puede seguir aviones y vuelos elegidos dondequiera que estén, y vigilar
aviones militares en zonas que tú indiques.

> **Live Track Aircraft es un módulo de Live Track**, una familia de
> integraciones de Home Assistant que dibujan todo lo que se mueve, y el tiempo
> que atraviesa, en un mapa compartido: aviones, barcos, trenes y tiempo.
> Instálalo solo, o junto a los demás módulos
> ([lista abajo](#parte-de-live-track-los-demás-módulos)).

> **Sigue creciendo, y las ideas son bienvenidas.** Live Track Aircraft cubre
> hoy todo el mundo donde voluntarios mantienen receptores, con rutas y
> propietarios con más detalle para los Estados Unidos, y estamos añadiendo más
> fuentes de rutas y datos de aviones. ¿Falta el tuyo?
> [Sugiérelo](#ayúdanos-a-hacerlo-crecer), o añádelo tú mismo: te ayudaremos a
> hacerlo.

**Estado: 0.1.5, publicado.** Añadido al Marketplace por su enlace
([abajo](#instalarlo-paso-a-paso)); todavía no está en el catálogo del
Marketplace.

Obra original de StrausbergAutomationWorks. Sin relación con adsb.fi,
adsb.lol, adsbdb, la Federal Aviation Administration (Estados Unidos),
OurAirports, ADS-B Radar, Planespotters.net, ninguna aerolínea ni ningún
operador de aviones, ni respaldado por ellos.

> ⚠ **No es un sistema de seguridad.** Muestra datos públicos, normalmente de
> hace unos segundos y a veces de un minuto o más, y solo los aviones que los
> receptores de los voluntarios llegan a oír. No sirve para navegar, ni para
> separar aviones, ni para ningún otro fin operativo.

---

## Contenido

1. [Todo lo que hace](#todo-lo-que-hace)
2. [Dónde funciona](#dónde-funciona)
3. [Parte de Live Track: los demás módulos](#parte-de-live-track-los-demás-módulos)
4. [Antes de empezar](#antes-de-empezar)
5. [Instalarlo, paso a paso](#instalarlo-paso-a-paso)
6. [Configurarlo, paso a paso](#configurarlo-paso-a-paso)
7. [Claves gratuitas que activan más, paso a paso](#claves-gratuitas-que-activan-más-paso-a-paso)
8. [Poner el mapa en un panel de control](#poner-el-mapa-en-un-panel-de-control)
9. [Usarlo en automatizaciones](#usarlo-en-automatizaciones)
10. [Todo lo del mapa, en detalle](#todo-lo-del-mapa-en-detalle)
11. [Todas las entidades que crea](#todas-las-entidades-que-crea)
12. [Qué envía y qué descarga](#qué-envía-y-qué-descarga)
13. [Ayúdanos a hacerlo crecer](#ayúdanos-a-hacerlo-crecer)
14. [Idiomas](#idiomas)
15. [Créditos y licencias](#créditos-y-licencias)
16. [Palabras clave](#palabras-clave)

---

## Todo lo que hace

### En el mapa, sin configurar nada

Añades una **zona**: un centro en el mapa y un radio alrededor. Empieza en tu
casa. Todo lo que sigue aparece entonces en esa zona o, donde la tabla lo
dice, en cualquier parte del mundo.

| Qué | Dónde | De dónde |
|---|---|---|
| **Aviones**: aviones de línea, avionetas, helicópteros, planeadores, globos y drones, cada uno dibujado como su propio tipo y girado hacia donde vuela | en cada zona | adsb.fi, o adsb.lol cuando adsb.fi no responde |
| **Quién lo opera**: la aerolínea, el propietario, o el tipo cuando no se sabe nada más, en la etiqueta del marcador | cada avión | el indicativo de la aerolínea; el registro de aeronaves de la FAA (Estados Unidos) para los propietarios |
| **Colores que dicen quién vuela**: gobierno, policía, fuerzas federales del orden, el ejército, ambulancias aéreas y helicópteros, cada uno en su color | cada avión, cuando se sabe | el registro de aeronaves de la FAA (Estados Unidos) y la marca militar de la fuente |
| **Rutas**: de dónde despegó el avión y adónde va, con los nombres de los aeropuertos y una hora de llegada estimada | vuelos con un plan de vuelo presentado a la FAA (Estados Unidos); en otros lugares, cuando adsbdb conoce el vuelo | FiledRoutesDB, luego adsbdb |
| **Los aviones del presidente de los Estados Unidos**, con los aviones del 89th Airlift Wing y los aviones militares que los escoltan | en cualquier parte del mundo | adsb.fi y su lista militar |
| **Los aviones de la lista pública EnforcementAircraft** (inmigración y fuerzas federales del orden), con luces intermitentes | en cada zona | la lista EnforcementAircraft |
| **Los aviones militares en tus zonas de vigilancia**: cada avión que la fuente marca como militar, dentro de hasta diez círculos que tú indicas, aunque tu zona esté llena. Opcional: escribes los círculos en el diálogo de configuración | en cualquier parte del mundo | la lista militar de adsb.fi |
| **Los aviones y vuelos que sigues**: tu propio avión, la flota de un club, o el vuelo de un familiar. Opcional: escribes sus códigos en el diálogo de configuración | en cualquier parte del mundo | adsb.fi |
| **Fotos**: una foto del avión, con el nombre del fotógrafo, cuando lo señalas | cada avión del que Planespotters.net tiene una foto | Planespotters.net ([más](#fotos)) |
| **Tu propia imagen para un avión**, en lugar de su icono | dondequiera que se muestre ese avión | una imagen que pones en una carpeta ([cómo](#tu-propia-imagen-para-un-avión)) |

### Activado con tu propia clave o cuenta gratuita

| Clave o cuenta gratuita | Qué añade |
|---|---|
| clave de **adsb.lol** | más peticiones al día a adsb.lol, la segunda fuente, para que el mapa siga funcionando durante una caída larga de adsb.fi |

Cada una se consigue en unos minutos: [paso a paso abajo](#claves-gratuitas-que-activan-más-paso-a-paso).

---

## Dónde funciona

| Región | Qué obtienes | De dónde | Necesita |
|---|---|---|---|
| **Todo el mundo** | posiciones de aviones donde voluntarios mantienen receptores: densas sobre Europa y Norteamérica, más escasas en otros lugares, y pocas o ninguna lejos en el mar | adsb.fi, adsb.lol | nada |
| **Todo el mundo** | los nombres de los aeropuertos en las rutas, y sus husos horarios para la hora de llegada | OurAirports, a través de la tabla AirportZones | nada |
| **Todo el mundo** | rutas de muchos vuelos de línea, comprobadas con el lugar donde está realmente el avión | adsbdb | nada |
| **Norteamérica**: Estados Unidos | nombres de propietarios y operadores de aviones matriculados en los Estados Unidos, y los colores de los aviones del gobierno y de la policía | el registro de aeronaves de la FAA | nada |
| **Norteamérica**: Estados Unidos | rutas de los vuelos presentados a la FAA, incluidos los vuelos internacionales desde y hacia los Estados Unidos | FiledRoutesDB | nada |

¿No está en la lista? [Dínoslo](#ayúdanos-a-hacerlo-crecer). Donde alguien
publique los datos abiertamente, estudiaremos añadirlos.

⚠ **La cobertura es buena donde hay receptores, y no existe donde no los
hay.** Un avión solo aparece si el receptor de un voluntario lo oye, o si
varios receptores juntos pueden localizarlo. Ningún ajuste puede crear una
cobertura que no existe. **Un cielo vacío en el mapa puede significar que no
hay receptores cerca de ti, no que no haya aviones.**

⚠ **Las rutas son sobre todo para los Estados Unidos.** FiledRoutesDB solo
contiene planes de vuelo presentados a la FAA. En otros lugares, una ruta
viene de adsbdb, que conoce muchos vuelos de línea y pocos más, así que fuera
de los Estados Unidos muchos aviones no muestran ruta.

⚠ **Los nombres de los propietarios son solo para aviones matriculados en los
Estados Unidos.** Un avión matriculado en otro país muestra su aerolínea a
partir de su indicativo, o su tipo.

---

## Parte de Live Track: los demás módulos

Live Track es un conjunto de integraciones de Home Assistant, una por cada
tipo de cosa que se mueve, todas dibujadas en la misma tarjeta de mapa. Cada
una funciona sola; juntas forman una sola imagen en vivo. Comparten la tarjeta
de mapa y una biblioteca de Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
así que instalar otra no añade peticiones a una fuente que otra ya lee.

| Módulo | Qué pone en el mapa | Estado |
|---|---|---|
| **Live Track Aircraft** | aviones sobre ti por ADS-B, con rutas e iconos por tipo (este módulo) | publicado |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | buques y barcos por AIS, cerca de ti o en cualquier lugar | publicado |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | trenes de cercanías en Norteamérica, Europa y Australia | publicado |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | trenes interurbanos y de larga distancia en Norteamérica, Europa y Australia | publicado |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | aviones y buques de inmigración y de las fuerzas federales del orden, a partir de listas públicas | publicado |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | tiempo, tormentas y riesgos naturales | publicado |
| Live Track Stations | paneles de salidas y avisos de "hora de salir" para cada estación | previsto |
| Live Track Satellites | satélites que pasan sobre ti | previsto |
| Live Track Freight Trains | trenes de mercancías y de obras donde los ferrocarriles los publican | previsto |
| Live Track Transit | autobuses urbanos, tranvías, ferris y metro | previsto |
| Live Track Intercity Buses | autocares interurbanos y regionales | previsto |
| Live Track Commuter Buses | autobuses de cercanías | previsto |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | la tarjeta de mapa compartida en la que dibuja cada módulo | publicada, instalada con cada módulo |

Todo es gratuito y de código abierto. Nada se reserva para patrocinadores.

---

## Antes de empezar

* **Home Assistant** 2026.11 o posterior.
* **El Marketplace** (HACS) en tu Home Assistant, para instalarlo y
  actualizarlo de la forma fácil. Sin él puedes copiar los archivos a mano.
* **Acceso a Internet** para Home Assistant: todo viene de fuentes públicas.
* **Opcional: auto-entities** desde el Marketplace, para poner los marcadores
  en el mapa (ver
  [Poner el mapa en un panel de control](#poner-el-mapa-en-un-panel-de-control)).
* Nada que pagar y ninguna cuenta necesaria. La clave de adsb.lol de arriba es
  opcional.
* Home Assistant instala por sí mismo los dos paquetes de Python que necesita
  (`saw-livetrack` y `tzfpy`) la primera vez que se carga la integración.

---

## Instalarlo, paso a paso

### Desde el Marketplace (recomendado)

Live Track Aircraft todavía no está en el catálogo del Marketplace. Añádelo
por su enlace:

1. En Home Assistant, abre **Configuración → Marketplace** (HACS).
2. Elige **Añadir desde enlace** (o el menú de tres puntos → **Repositorios
   personalizados**).
3. Escribe `StrausbergAutomationWorks/LiveTrackAircraft`. Si te pregunta el
   tipo, elige **Integration**.
4. Busca **Live Track Aircraft** en la lista y elige **Descargar** o
   **Instalar**.
5. **Reinicia Home Assistant**: **Configuración → Sistema → Reparaciones**
   ofrece el reinicio, o usa **Configuración → Sistema → Reiniciar**.

Después, el Marketplace ofrece cada versión nueva como actualización.

### A mano

1. Descarga el código fuente de la
   [última versión](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/releases/latest).
2. Copia su carpeta `custom_components/live_track_aircraft` en la carpeta
   `custom_components` de la carpeta de configuración de tu Home Assistant
   (crea `custom_components` si no existe).
3. Reinicia Home Assistant.

Para actualizar a mano, sustituye la carpeta por la de la nueva versión y
reinicia.

---

## Configurarlo, paso a paso

El diálogo de configuración está en inglés. Sus campos se nombran aquí tal
como los muestra.

1. Abre **Configuración → Dispositivos y servicios**.
2. Elige **Añadir integración** (abajo a la derecha) y busca **Live Track
   Aircraft**.
3. **Centre** (centro): arrastra el marcador al centro del cielo que quieres
   vigilar. Empieza en tu casa.
4. **Radius (km)** (radio): hasta qué distancia del centro se muestran los
   aviones, de 1 a 463 km (0,6 a 288 millas). Si dudas, deja 56 km
   (35 millas).
5. **Update interval (seconds)** (intervalo de actualización): deja 15. Las
   fuentes rechazan peticiones más frecuentes.
6. **Maximum aircraft published** (máximo de aviones publicados): deja 250.
   Es un límite de seguridad, no una forma de mostrar menos aviones.
7. Deja vacíos por ahora los cuatro campos opcionales. Cada uno se explica más
   abajo.
8. Elige **Enviar**.

Eso es todo. Los aviones aparecen en menos de un minuto. Cada zona es una
entrada, titulada con su centro y su radio, por ejemplo
`39.817, -84.050 - 56 km`. Para vigilar una segunda zona, añade de nuevo la
integración con otro centro u otro radio. El mismo centro y el mismo radio dos
veces se rechazan.

Las rutas, los nombres de los aeropuertos y los propietarios se completan
durante los primeros minutos, a medida que se descargan los archivos de los
que vienen ([Qué envía y qué descarga](#qué-envía-y-qué-descarga)).

### Cambiar lo que muestra: las opciones

Abre **Configuración → Dispositivos y servicios → Live Track Aircraft →
Configurar** (el engranaje) en la zona que quieres cambiar. Cada opción, en
palabras sencillas:

| Opción | Qué hace | Por defecto |
|---|---|---|
| **Centre** | mueve la zona; su título la sigue | tu casa |
| **Radius (km)** | hasta qué distancia del centro se muestran los aviones, de 1 a 463 km (0,6 a 288 millas) | 56 km (35 millas) |
| **Update interval (seconds)** | cada cuánto se piden las posiciones, de 15 a 3600 segundos | 15 |
| **Maximum aircraft published** | un límite de seguridad, de 1 a 1000; cuando hay más aviones en el círculo, se conservan los más cercanos. Los aviones que sigues, los de tus zonas de vigilancia militar y los de la lista EnforcementAircraft se conservan siempre | 250 |
| **Military watch areas** | círculos donde se muestra cada avión militar ([cómo](#zonas-de-vigilancia-militar)) | vacío |
| **Aircraft to follow (hex codes)** | aviones seguidos en cualquier lugar, por su código hexadecimal ([cómo](#aviones-y-vuelos-que-sigues)) | vacío |
| **Flights to follow (call signs)** | vuelos seguidos en cualquier lugar, por su indicativo (la misma sección) | vacío |
| **adsb.lol API key** | tu propia clave para adsb.lol ([cómo conseguir una](#claves-gratuitas-que-activan-más-paso-a-paso)) | vacío |

Vacía uno de los cuatro campos opcionales para desactivar esa parte.

---

## Claves gratuitas que activan más, paso a paso

Todas son gratuitas y personales: cada persona que instala Live Track
Aircraft obtiene la suya. Pega cada una en **Configuración → Dispositivos y
servicios → Live Track Aircraft → Configurar**.

### adsb.lol (más peticiones a la segunda fuente, todo el mundo)

Live Track Aircraft pregunta primero a adsb.fi, y pregunta a adsb.lol solo
mientras adsb.fi no responde. Sin clave, adsb.lol permite 500 peticiones al
día desde una dirección de Internet, que una caída de adsb.fi puede agotar en
unas dos horas. Una clave sube ese límite. No necesitas una para empezar.

1. Abre <https://www.adsb.lol/request> y pide una clave gratuita con el
   formulario de esa página. La documentación de adsb.lol da a esta clave
   1000 peticiones al día.
2. Si alimentas adsb.lol con un receptor propio, usa en su lugar tu clave de
   colaborador (feeder): la documentación de adsb.lol le da 7200 peticiones al
   día. Tus claves están en **My keys** en adsb.lol
   (<https://www.adsb.lol/mmb>).
3. Pega la clave en **adsb.lol API key**, y elige **Enviar**.

La clave solo se envía a adsb.lol. Si adsb.lol la rechaza (incorrecta o
caducada), Live Track Aircraft sigue sin ella, y el `sensor.aircraft_in_range`
de la zona muestra `refused` en su atributo `adsblol_key` hasta que cambies la
clave. Si no, muestra `set`, o `none` sin clave. No hace falta ninguna
contraseña ni ningún secreto.

---

## Poner el mapa en un panel de control

El mapa es [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
la tarjeta en la que dibuja cada módulo de Live Track. **Se instala con Live
Track Aircraft**: nada que descargar, nada que copiar, ningún recurso que
añadir.

1. Abre un panel de control, elige el lápiz (**Editar panel de control**) y
   luego **Añadir tarjeta**.
2. Baja hasta el final y elige **Manual**.
3. Pega esto, y elige **Guardar**:

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

Esta forma necesita
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities) desde
el Marketplace. Con otros módulos de Live Track instalados, añade un filtro
`- domain: geo_location` más por cada una de sus fuentes
(`live_track_ships`, `live_track_weather` y así sucesivamente).

**Sin auto-entities:** LiveTrackMapCard puede elegir por sí misma qué muestra,
con `entity_filter`. Pega esto en su lugar; no hace falta instalar nada más:

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

Los otros módulos de Live Track van en `entity_filter` del mismo modo: una
regla `- domain: geo_location` más por cada fuente.

**En el mapa:**

* Cada avión se dibuja como su propio tipo, girado hacia donde vuela, y se
  mueve con suavidad entre las posiciones que comunica.
* Su etiqueta es el indicativo del vuelo (`UAL308`), si no quién lo opera
  (`Lewis University`), si no su tipo (`Cessna 172 Skyhawk`).
* **Señala** un avión para ver su aerolínea u operador, su foto si la hay y,
  cuando se conoce una ruta, la ruta y cuántos minutos faltan para que llegue.
  **Haz clic** en él para ver todos sus detalles y una foto más grande,
  enlazada a su página en Planespotters.net ([Fotos](#fotos)).

Si los recursos de tus paneles de control están definidos en YAML
(`lovelace: resource_mode: yaml`), no se puede registrar nada por ti: un aviso
en **Reparaciones** da entonces la línea exacta que hay que añadir. Una
tarjeta que hayas instalado tú desde el Marketplace no se toca. Si se borran
los archivos de la integración mientras sus zonas siguen configuradas, y no
hay instalado ningún otro módulo de Live Track, quita tú mismo la fila de la
tarjeta en **Configuración → Paneles de control → Recursos**. Cualquier otra
tarjeta de mapa que muestre entidades `geo_location` muestra también los
aviones, como marcadores simples.

---

## Usarlo en automatizaciones

Todo es una entidad normal de Home Assistant, así que el editor de
automatizaciones funciona con ello, sin código.

**Una notificación en el teléfono cuando un avión militar está en una de tus
zonas de vigilancia militar:**

1. **Configuración → Automatizaciones y escenas → Crear automatización →
   Crear nueva automatización**.
2. **Cuando**: **Añadir disparador** → **Entidad** → **Estado numérico**.
   Elige la entidad **Aircraft in range**, el **Atributo** **Military in
   areas** (`military_in_areas`), y **Por encima de** `0`.
3. **Entonces hacer**: **Añadir acción**, busca la acción de notificación de
   tu teléfono (lleva el nombre de tu teléfono), y escribe un mensaje, por
   ejemplo:

   ```text
   Hay un avión militar en tu zona de vigilancia
   ```

4. **Guardar**.

Para esto necesitas al menos una zona de vigilancia militar
([cómo](#zonas-de-vigilancia-militar)).

**Otras ideas:** una notificación cuando el vuelo de un familiar está en el
aire, cuando el atributo `followed_found` sube por encima de 0; una luz que se
enciende cuando hay más de 20 aviones sobre tu casa en Fráncfort (Alemania);
un contador en el panel de control de los aviones sobre tu aeródromo en
Queensland (Australia), a partir de `sensor.aircraft_in_range`; un mensaje
cuando despega el avión de tu club, cuando aparece su propia entidad
(`geo_location.aircraft_` y su código hexadecimal).

---

## Todo lo del mapa, en detalle

### Aviones

Los aviones transmiten su posición por radio, con un sistema llamado ADS-B.
Voluntarios de todo el mundo mantienen receptores y comparten lo que oyen a
través de redes comunitarias. Live Track Aircraft pide a una de ellas,
adsb.fi, cada avión dentro de tu círculo, cada 15 segundos por defecto. Cuando
adsb.fi no responde, o responde con muchos menos aviones que un momento antes,
pregunta a adsb.lol. Donde varios receptores oyen un avión que no transmite su
propia posición, las redes pueden localizarlo igualmente (multilateración,
MLAT).

Cada avión es un marcador, con el nombre de su código hexadecimal: la
dirección de seis caracteres que transmite su transpondedor, que pertenece al
avión y no cambia. El marcador aparece cuando el avión entra en tu círculo y
se quita cuando sale.

La etiqueta es el nombre más útil que se conoce, en este orden:

| El avión tiene | La etiqueta muestra | Ejemplo |
|---|---|---|
| el indicativo de un vuelo | el indicativo | `UAL308` |
| si no, un operador conocido | el operador | `Lewis University` |
| si no, un tipo conocido | el tipo | `Cessna 172 Skyhawk` |
| nada de esto | la matrícula, el código de tipo o el código hexadecimal | `N12345` |

⚠ No se muestran: aviones en tierra, vehículos de aeropuerto, y trazas solo de
radar sin identidad. Un avión que no transmite, o que vuela donde ningún
receptor lo oye, no se puede mostrar.

En cada avión: `identity` (el código hexadecimal), `callsign`,
`registration`, `aircraft_type`, `aircraft_name`, `operator`, `altitude_m`,
`speed_kmh`, `vertical_rate_ms`, `course_deg`, `squawk`, `emitter_category`,
`is_military`, `is_government`, `last_seen`.

### Colores e iconos

Cada avión se dibuja como su propio tipo: un avión de línea, un reactor
ejecutivo, una avioneta monomotor, un bimotor, un helicóptero, un
convertiplano, un planeador, un globo, un dron y muchos más, con el tamaño de
su clase. Las hélices y los rotores giran. El icono está girado hacia donde
vuela el avión; un avión lento conserva su última dirección en lugar de girar
sobre sí mismo.

El color dice quién vuela, cuando se sabe:

| Color | Quién |
|---|---|
| gris claro | la mayoría de los aviones |
| verde menta | helicópteros y otros giroaviones |
| ámbar | aviones del gobierno y ambulancias aéreas |
| azul | fuerzas federales del orden |
| verde militar | el ejército y la guardia costera |
| blanco, con luces azules intermitentes | policía |
| luces rojas y azules intermitentes | aviones de la lista EnforcementAircraft ([abajo](#la-lista-enforcementaircraft-y-live-track-salt)) |
| un brillo fijo | un avión de línea que hace vuelos chárter para ICE Air, entre otros trabajos |

⚠ De quién es un avión se sabe sobre todo para los aviones matriculados en
los Estados Unidos, por el registro de la FAA. En otros lugares, el color
viene solo de la marca militar de la fuente y del tipo de avión.

### Rutas y horas de llegada

Una ruta muestra de dónde despegó el avión y adónde va, con los nombres de
ambos aeropuertos, y una hora de llegada estimada. Viene de dos sitios:

1. **FiledRoutesDB**, un archivo público de planes de vuelo presentados a la
   FAA (Estados Unidos), creado y publicado por StrausbergAutomationWorks y
   descargado una vez al día. Cada ruta se comprueba con el lugar donde está
   el avión y la dirección en la que vuela. Una ruta que no encaja se muestra
   igualmente, y se marca como que no encaja en `route_check`.
2. **adsbdb**, al que solo se pregunta cuando FiledRoutesDB no tiene ruta para
   el indicativo, una vez por indicativo. Su respuesta solo se muestra si
   encaja con el lugar donde está realmente el avión.

Los aviones cuyos propietarios pidieron a la FAA que no mostrara sus vuelos al
público (la lista LADD de la FAA, Limiting Aircraft Data Displayed) se quitan
de FiledRoutesDB antes de publicarlo. Live Track Aircraft borra su copia
cuando el archivo caduca, o cuando la lista LADD con la que se creó tiene más
de 14 días, para no mostrar nunca rutas filtradas con una lista antigua.

La hora de llegada es una estimación, no un horario: la distancia que falta
en línea recta, a la velocidad del avión cuando va en crucero, y si no a una
velocidad típica de su clase. No se cuentan las esperas, la aproximación ni el
rodaje.

En cada avión con ruta: `origin_icao`, `destination_icao`, `origin_name`,
`destination_name`, `route_source`, `route_check`, `arrival_estimated_at`.

### Zonas de vigilancia militar

Cada avión que la fuente marca como militar, dentro de círculos que eliges, en
cualquier parte del mundo, aunque tu zona esté llena.

1. Abre **Configuración → Dispositivos y servicios → Live Track Aircraft →
   Configurar** en una zona.
2. En **Military watch areas**, escribe cada círculo como
   `latitude,longitude,km` (latitud, longitud, kilómetros), y separa los
   círculos con punto y coma, por ejemplo `39.81,-84.04,150; 34.0,-117.8,463`.
   Hasta diez círculos, cada uno de 1 a 2000 km (0,6 a 1243 millas). Escribe
   los decimales con punto.
3. Elige **Enviar**.

Los aviones militares que haya dentro aparecen en menos de un minuto y se
mueven una vez por minuto. Cada uno lleva `watch: military area`. El
`sensor.aircraft_in_range` de la zona los cuenta en `military_in_areas`, y por
círculo en `military_by_area`. Vacía el campo para dejarlo.

⚠ Solo muestra lo que transmite y está marcado como militar. Los vuelos
militares pueden volar con el transpondedor apagado, y un avión militar con
matrícula civil no está marcado.

### Aviones y vuelos que sigues

Live Track Aircraft puede seguir aviones que eliges dondequiera que estén en
el mundo, no solo en tu círculo: tu propio avión, la flota de un club o de una
empresa, o el vuelo de un familiar.

1. Abre **Configuración → Dispositivos y servicios → Live Track Aircraft →
   Configurar** en la zona con la que quieres verlos.
2. Rellena **Aircraft to follow (hex codes)**, **Flights to follow (call
   signs)**, o los dos.
3. Elige **Enviar**. Aparecen en un minuto, más o menos.

**Basta un código por avión.** Elige según lo que quieras seguir:

| Para seguir | Usa | Ejemplo |
|---|---|---|
| un avión, haga el vuelo que haga (tu propio avión, una flota) | su **código hexadecimal** | `a1b2c3` |
| un vuelo, lo haga el avión que lo haga (el viaje de un familiar) | su **indicativo** | `UAL1234` |

Poner los dos códigos del mismo avión no hace daño (se dibuja una vez), pero
no añade nada.

**Cómo escribir los códigos:**

* Separa los códigos con comas: `a1b2c3, a4b5c6, a7b8c9`. Los espacios o los
  puntos y coma entre códigos también sirven.
* Un código hexadecimal tiene exactamente seis caracteres: los dígitos del 0
  al 9 y las letras de la a a la f, en mayúsculas o minúsculas.
* Un indicativo tiene de 2 a 8 letras y dígitos, escritos tal como los
  transmite el avión, sin espacios ni guiones: `UAL1234`, no `UA 1234` ni
  `UAL-1234`.
* Hasta 100 códigos hexadecimales y 100 indicativos. Un código escrito dos
  veces cuenta una vez.
* Si un código está mal, el diálogo rechaza ese campo, dice cómo es un código
  correcto, y no guarda nada hasta que se corrija.

**Cómo encontrar los códigos.** Cada avión del mapa lleva su código
hexadecimal en su atributo `identity` y su indicativo en su atributo
`callsign`. Para un avión matriculado en los Estados Unidos, la búsqueda por
número N del registro de la FAA muestra el código hexadecimal como "Mode S
Code (Base 16 / Hex)". En un vuelo de línea, el indicativo suele ser el código
de tres letras de la aerolínea seguido del número de vuelo, que no es lo que
pone el billete:

| Billete | Indicativo |
|---|---|
| United UA 1234 | `UAL1234` |
| Delta DL 89 | `DAL89` |
| American AA 100 | `AAL100` |

Algunas aerolíneas transmiten un indicativo que no es el número de vuelo. Si
un vuelo no aparece, búscalo en un mapa de vuelos en directo y copia el
indicativo que muestra. Un indicativo se reutiliza: el mismo indicativo
mañana es otro viaje, y puede ser otro avión. Sigue en seguimiento hasta que
lo quites.

**Lo que ves.** Cada avión seguido se dibuja con su icono y su etiqueta de
siempre dondequiera que esté, aunque tu zona esté llena. Su atributo `watch`
dice `followed`, y `outside_radius` dice si está fuera de tu círculo. Fuera de
tu círculo se mueve una vez por minuto; dentro, tan a menudo como todo lo
demás. El `sensor.aircraft_in_range` de la zona muestra `followed_asked`
(cuántos códigos sigues), `followed_found` (cuántos están en el aire ahora) y
`follow_status` (la última petición de indicativos: `ok`, o qué falló).

**Para dejar de seguir**, quita el código, o vacía el campo, y elige
**Enviar**.

⚠ Solo se pueden encontrar los aviones que transmiten ADS-B, o que la MLAT
puede localizar. Un avión en tierra o fuera de la cobertura de los receptores
no se muestra, y `followed_found` no lo cuenta. Los horarios y los retrasos
por número de vuelo no forman parte de esto.

### Tu propia imagen para un avión

Pon una imagen que elijas en lugar del icono de un avión, por ejemplo el tuyo.

1. En la carpeta de configuración de tu Home Assistant (la que contiene
   `configuration.yaml`), crea una carpeta llamada
   `live_track_aircraft_pictures`.
2. Pon dentro la imagen, con el nombre del código hexadecimal del avión:
   `a1b2c3.png`. Sirven archivos PNG, JPG, WebP, GIF y SVG, de hasta 2 MB cada
   uno.

La imagen aparece en menos de un minuto, igual que un cambio o un borrado. Se
dibuja derecha, sin girar, porque una foto no está dibujada con el morro hacia
arriba. El atributo `picture_source` del avión dice entonces `override`.

Estas imágenes requieren iniciar sesión en tu Home Assistant, como todo lo
demás. El mapa recibe cada una por un enlace que firma Home Assistant y que
deja de funcionar al cabo de un día; antes se crea uno nuevo.

### Fotos

Cuando señalas un avión, el mapa muestra una foto suya de
[Planespotters.net](https://www.planespotters.net), si la hay, con el nombre
del fotógrafo al lado. Haz clic en el avión para ver la foto más grande; la
foto enlaza a su página en Planespotters.net. No hay nada que configurar.

La foto solo se busca cuando alguien señala ese avión, no para cada avión de
tu zona. Tu Home Assistant pregunta a Planespotters.net por el código
hexadecimal del avión. Guarda la respuesta, una foto o ninguna, durante 12
horas, solo en memoria, así que un reinicio la olvida. El navegador que
muestra el mapa carga la imagen directamente desde Planespotters.net. Home
Assistant no descarga, ni guarda, ni reenvía ninguna imagen.

⚠ Una foto muestra el avión tal como lo vio el fotógrafo, quizá con una librea
anterior o con un operador anterior. No todos los aviones tienen foto en
Planespotters.net.

⚠ No se busca foto para un avión que vuela con una dirección temporal por
privacidad (el programa Privacy ICAO Address de la FAA, Estados Unidos),
porque ese código hexadecimal no identifica el avión, ni para una traza sin un
código hexadecimal real.

⚠ Todavía no hay ninguna opción para desactivar las fotos.

Cada avión con código hexadecimal lleva `marker_photo_lookup`: la dirección en
tu Home Assistant donde el mapa pide la foto. Solo alguien que haya iniciado
sesión en tu Home Assistant puede usarla. Las fotos son obra de sus
fotógrafos: consulta [Créditos y licencias](#créditos-y-licencias).

### Los aviones del presidente

Los aviones que usa el presidente de los Estados Unidos se muestran en
cualquier parte del mundo, por sus códigos hexadecimales, nunca por su
indicativo, junto con los aviones del 89th Airlift Wing (indicativos SAM y
VENUS) y los aviones militares que escoltan a un avión presidencial. Vienen de
una petición por minuto que Live Track Aircraft hace de todos modos. Cada uno
lleva un atributo `watch` que dice por qué se muestra, y un avión presidencial
su nombre en `presidential_airframe`.

⚠ Un avión presidencial en el mapa no dice nada de quién va a bordo.

### La lista EnforcementAircraft y Live Track SALT

[EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)
es una lista pública de aviones usados por inmigración y por las fuerzas
federales del orden, cada entrada con sus fuentes, publicada por
StrausbergAutomationWorks. En tu zona, un avión que la lista confirma con sus
fuentes parpadea en rojo y azul, y un avión de línea que hace vuelos chárter
para ICE Air, entre otros trabajos, tiene un brillo fijo. Se conservan
siempre, aunque tu zona esté llena.

Su compañero, [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
dibuja los aviones de la lista dondequiera que vuelen, no solo en tu zona.
Instala los dos y cada uno se ocupa de su parte: Live Track Aircraft dibuja
cada avión dentro de su propia zona, incluidos los de la lista, y Live Track
SALT dibuja los aviones de la lista en todos los demás lugares. Comparten una
sola petición a las fuentes, y ningún avión se dibuja dos veces.

---

## Todas las entidades que crea

Para cada zona:

| Entidad | Qué es |
|---|---|
| `sensor.aircraft_in_range` | **Aircraft in range**: cuántos aviones hay ahora en el círculo, todos, aunque sean más que el máximo. El de una segunda zona es `sensor.aircraft_in_range_2`, y así sucesivamente |
| `geo_location.aircraft_…` | una por avión, con el nombre de su código hexadecimal (`geo_location.aircraft_a1b2c3`); viene y se va con el avión. Cada una lleva `source: live_track_aircraft`, y su estado es su distancia al centro en kilómetros |

Los atributos del sensor dicen lo que pasa: `published_count` (cuántos hay en
el mapa), `capped` (verdadero cuando el máximo cortó la lista), `source` (qué
red respondió la última vez), `source_backoff`, `route_artifact`,
`route_download`, `airport_table`, `airport_download`, `route_lookup`,
`watched_count`, `military_in_areas`, `military_by_area`, `followed_asked`,
`followed_found`, `follow_status`, `adsblol_key` y `enforcement_list`.

⚠ **Los marcadores de los aviones no tienen identificador único, a
propósito.** Una zona ve miles de aviones distintos al año, y una fila del
registro para cada uno haría que Home Assistant arrancara más despacio sin
ningún beneficio. Por eso no se pueden renombrar, ocultar ni asignar a un área
en la interfaz. Sus identificadores de entidad vienen igualmente del código
hexadecimal, así que el mismo avión recibe siempre el mismo identificador. El
sensor tiene identificador único y se puede renombrar.

⚠ **Tu base de datos.** El registrador de Home Assistant guarda una fila nueva
cada vez que cambia una entidad, y un avión en vuelo cambia en cada
actualización, cada 15 segundos por defecto. En nuestro sistema de pruebas, en
septiembre de 2026, una entidad como estas actualizada cada 15 segundos
costaba unos 9,6 MB al día; con 50 aviones son unos 480 MB al día. Si no
quieres el historial de cada avión, déjalos fuera del registrador. Añade esto
a `configuration.yaml` y reinicia:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.aircraft_*
```

Si tu `configuration.yaml` ya tiene una sección `recorder:`, añade solo el
patrón `geo_location.aircraft_*`, bajo `exclude:` y `entity_globs:`. Una
tarjeta de mapa configurada para dibujar el historial no tendrá entonces
rastro que dibujar. `sensor.aircraft_in_range` cuesta poco: sus atributos
toman pocos valores, así que el registrador los guarda una vez.

---

## Qué envía y qué descarga

**Sobre tu ubicación.** El centro y el radio de cada zona se envían a adsb.fi
en cada actualización, cada 15 segundos por defecto, y a adsb.lol cuando
adsb.fi no responde. El centro se envía tal como lo has puesto, y empieza en
tu casa: para dejar de enviar tu casa, aleja el centro de ella
(**Configurar** → **Centre**) o borra la zona. Los códigos hexadecimales y los
indicativos que sigues se envían a adsb.fi (o a adsb.lol) una vez por minuto,
y tu clave de adsb.lol solo a adsb.lol. Los indicativos de los vuelos de línea
en tu zona se envían a adsbdb cuando FiledRoutesDB no tiene ruta para ellos.
Cuando alguien señala un avión en el mapa, su código hexadecimal se envía a
Planespotters.net, como mucho una vez cada 12 horas por avión, y el navegador
que muestra el mapa carga la foto desde allí. Todavía no hay ninguna opción
para detenerlo. No se envía nada más sobre ti a ninguna parte. Cada servicio
ve tu dirección de Internet, como cualquier sitio web.

**Cuánto.**

| Fuente | Qué y cada cuánto | Tras un error |
|---|---|---|
| adsb.fi | cada avión de tu círculo, en cada actualización (cada 15 segundos por defecto); una petición por minuto para los aviones seguidos por código hexadecimal y los aviones del presidente; una para la lista militar; una para todos los indicativos seguidos juntos, solo si sigues alguno | pregunta a adsb.lol en su lugar. Una fuente que rechaza con HTTP 429 se salta durante el tiempo que pide, o durante 1 minuto, que se dobla hasta 10 minutos |
| adsb.lol | las mismas peticiones, solo mientras adsb.fi no responde | lo mismo |
| adsbdb | una petición por cada indicativo nuevo de aerolínea para el que FiledRoutesDB no tiene ruta, con al menos 1 segundo entre peticiones; una respuesta se guarda 30 días, un "sin ruta" 24 horas. Las respuestas se guardan solo en memoria | no se vuelve a preguntar durante 15 minutos; todas las peticiones se detienen 15 minutos tras un HTTP 429 |
| Planespotters.net | una petición por la foto de un avión la primera vez que alguien lo señala, y ninguna más para ese avión durante 12 horas. Las respuestas se guardan solo en memoria. La foto en sí la carga el navegador que muestra el mapa | tras un HTTP 429, no se pide ninguna foto durante el tiempo que pide Planespotters.net, o durante 10 minutos; tras un HTTP 403, durante un día |
| FiledRoutesDB, desde GitHub | un pequeño archivo de sumas de comprobación una vez al día, después de las 14:00 hora de Chicago (Estados Unidos); el archivo en sí, unos 4,6 MB, solo si ha cambiado | se reintenta una hora después; tu copia sigue en uso hasta que caduca |
| AirportZones, desde GitHub | un pequeño archivo de sumas de comprobación una vez al día; la tabla en sí, unos 4,8 MB, solo si ha cambiado | se reintenta una hora después; tu copia sigue en uso |
| EnforcementAircraft, desde GitHub | un pequeño archivo de sumas de comprobación una vez por hora; la lista en sí, pequeña, solo si ha cambiado | tu copia sigue en uso |
| Registro de aeronaves de la FAA (Estados Unidos) | el registro, unos 73 MB, una vez cada 7 días, desde `registry.faa.gov` | se reintenta al día siguiente; tu copia sigue en uso |

Los archivos descargados se comparten con otros módulos de Live Track, así que
cada uno se descarga una sola vez, instales los módulos que instales. Se
guardan en la carpeta `.storage` de Home Assistant con nombres que empiezan
por `saw_`. Si quitas Live Track Aircraft y ningún otro módulo de Live Track
los usa, puedes borrarlos a mano.

---

## Ayúdanos a hacerlo crecer

Live Track Aircraft sigue creciendo. Añadimos fuentes de rutas, fuentes de
datos y datos de aviones a medida que los encontramos, y queremos saber qué
te gustaría a continuación.

### Sugerir algo

¿Falta tu país, tu aeropuerto o tu tipo de avión? ¿Hay algo mal, o difícil de
entender? Cuéntanoslo de la forma que te resulte más fácil:

* [**Rellena un formulario corto**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=es.yml)
  en español. Necesitas una cuenta gratuita de GitHub.
* **Escribe un correo** a
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  No hace falta cuenta.

En cualquier caso, ayuda que nos digas:

* qué te gustaría ver, y en qué parte del mundo;
* un enlace a donde se publican los datos, si conoces uno (una página de
  datos abiertos, un canal público, la web de un servicio): no es necesario,
  pero ayuda;
* el idioma de tu Home Assistant, si el problema es la redacción o una
  traducción.

Escribe en inglés o en tu propio idioma, lo que te resulte más fácil.

### Añadirlo tú mismo, con nuestra ayuda

Si quieres añadir algo tú mismo, te ayudaremos a hacerlo, desde la primera
pregunta hasta la versión terminada. No necesitas ser desarrollador para
empezar:

* **Una traducción.** Los textos del diálogo de configuración son una lista
  corta de frases en un archivo de texto. Te mostraremos qué archivo y qué
  líneas.
* **Una nueva fuente de datos.** Dinos dónde se publican los datos. Podemos
  escribir el código juntos, o revisar el tuyo.
* **Probarlo donde vives.** Instálalo, mira tu parte del mapa y dinos qué está
  bien y qué no.
* **Una corrección de este README.** Si un paso no coincidía con lo que
  viste, dinos lo que viste.

[**Cuéntanos qué tienes en mente**](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues/new?template=es.yml)
o escribe a
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
y te responderemos con los siguientes pasos.

---

## Idiomas

Este README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), [Nederlands](README.nl.md),
[简体中文](README.zh-Hans.md), **Español**, [Italiano](README.it.md),
[Dansk](README.da.md). Cada README traducido está completo.

El diálogo de configuración y las opciones están por ahora solo en inglés, sea
cual sea el idioma de tu Home Assistant. Si hablas otro idioma, puedes
traducirlos tú mismo: es una lista corta de frases en un solo archivo, y [te
ayudaremos a hacerlo](#añadirlo-tú-mismo-con-nuestra-ayuda).

¿Has encontrado un error en una traducción, o necesitas otro idioma?
Dínoslo en <https://github.com/StrausbergAutomationWorks/LiveTrackAircraft/issues>,
o [tradúcelo con nuestra ayuda](#añadirlo-tú-mismo-con-nuestra-ayuda).

---

## Créditos y licencias

* **adsb.fi** (<https://adsb.fi>): posiciones de aviones, datos abiertos solo
  para uso personal y no comercial, según las condiciones de su
  [README de datos abiertos](https://github.com/adsbfi/opendata), que piden
  citar a adsb.fi y enlazar a su página principal. Al instalar esta
  integración usas adsb.fi, y sus condiciones se aplican a ti.
* **adsb.lol** (<https://adsb.lol>): posiciones de aviones, bajo la
  [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/).
  Al instalar esta integración usas adsb.lol, y sus condiciones se aplican a
  ti. Las dos redes las mantienen voluntarios: si puedes, apóyalas aportando
  los datos de un receptor.
* **FiledRoutesDB** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/FiledRoutesDB)):
  rutas de planes de vuelo presentados a la FAA (Estados Unidos), datos bajo
  CC BY 4.0, con la lista LADD de la FAA aplicada antes de publicarlos.
* **adsbdb** (<https://www.adsbdb.com>): rutas fuera de FiledRoutesDB. Sus
  datos de rutas son obra de David Taylor (Edimburgo) y Jim Mason (Glasgow), y
  no se pueden copiar ni volver a publicar sin permiso; por eso las respuestas
  se guardan solo en memoria, nunca en un archivo, y cada avión que muestra una
  ruta de adsbdb los cita.
* **El registro de aeronaves de la FAA** (Federal Aviation Administration,
  Estados Unidos): nombres de propietarios y operadores de aviones matriculados
  en los Estados Unidos, datos públicos del gobierno de los Estados Unidos. La
  propia FAA quita los nombres que se le pide no publicar antes de publicar el
  archivo.
* **OurAirports** (<https://ourairports.com>), a través de
  [AirportZones](https://github.com/StrausbergAutomationWorks/AirportZones):
  nombres y posiciones de aeropuertos, bajo la ODbL 1.0; husos horarios
  añadidos por StrausbergAutomationWorks.
* **EnforcementAircraft** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)):
  la lista de aviones de inmigración y de las fuerzas federales del orden, bajo
  la ODbL 1.0.
* **ADS-B Radar** (<https://adsb-radar.com>): los iconos de aviones, de su
  [conjunto de iconos SVG de aviones](https://adsb-radar.com/help/icons.html)
  de Jos Nutbroek, usados según sus condiciones, que piden este enlace. Los
  iconos no están cubiertos por la licencia MIT de este repositorio. Algunos
  iconos los dibujó StrausbergAutomationWorks al estilo del conjunto y los donó
  a ADS-B Radar, así que también se rigen por sus condiciones. Esta integración
  sirve los iconos con un relleno y un contorno nuevos, a escala según la clase
  de avión, y anima algunas hélices y rotores. Cada cambio está en
  [ATTRIBUTION.md](ATTRIBUTION.md).
* **Planespotters.net** (<https://www.planespotters.net>): las fotos de
  aviones, a través de su [API de
  fotos](https://www.planespotters.net/photo/api) y según sus condiciones.
  Cada foto es obra de su fotógrafo, que se nombra a su lado, y enlaza a su
  página en Planespotters.net. No se copia ninguna foto en este repositorio, y
  Home Assistant no descarga, ni guarda, ni reenvía ninguna imagen. Al
  instalar esta integración usas Planespotters.net, y sus condiciones se
  aplican a ti.
* **La tarjeta de mapa** es [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, una copia de [ha-map-card](https://github.com/nathan-gs/ha-map-card) de
  nathan-gs, MIT. Sus teselas de mapa y sus créditos están en su README.

Ninguna de estas organizaciones ha creado ni respaldado esta integración.

**Código**: MIT, en [LICENSE](LICENSE).

**Para desarrolladores:** las entidades siguen el contrato de mapa común de
Live Track, así que cada módulo aparece en un solo mapa sin sensores de
plantilla; las posiciones llegan por una interfaz de fuentes en
`custom_components/live_track_aircraft/sources/`, así que se puede añadir otra
fuente sin tocar las entidades. Las pruebas se ejecutan con
`python -m unittest discover -s tests`.

---

## Palabras clave

Home Assistant aviones · Home Assistant seguimiento de vuelos · ADS-B ·
mapa ADS-B · seguimiento de vuelos · radar de aviones · aviones sobre mí ·
MLAT · Mode S · rutas de vuelo · aviones militares · Air Force One ·
helicópteros · aircraft · flight tracker · Flugzeuge · Flugverfolgung ·
avions · suivi des vols · vliegtuigen · vluchten volgen · 飞机 · 航班跟踪 ·
aerei · tracciamento voli · fly · flysporing · adsb.fi · adsb.lol · adsbdb ·
FiledRoutesDB · registro de la FAA · OurAirports · ADS-B Radar ·
Planespotters.net · fotos de aviones · geo_location · tarjeta de mapa ·
Lovelace · HACS · Marketplace · Live Track · LiveTrack ·
StrausbergAutomationWorks

---

**Reconocimiento.** StrausbergAutomationWorks reconoce a los pueblos indígenas
de todas las tierras y aguas de este mapa, en todo el mundo, y presenta sus
respetos a sus Mayores del pasado y del presente.
