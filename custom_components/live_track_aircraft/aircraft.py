"""Aircraft type lookup for Flights Above.

The ADS-B feed reports an ICAO aircraft type designator such as ``B753`` or
``LJ60``. Those are precise but unreadable, so this maps them to the model
name a person would recognise.

Unknown designators return ``None`` rather than a guess: the coarse
``emissions_class`` already covers "roughly what kind of aircraft is this",
and inventing a model name would be worse than admitting the gap.
"""

from __future__ import annotations

# ICAO type designator -> human-readable model name.
# Weighted toward types common over Europe and North America, plus the
# general-aviation and business types that dominate low-altitude traffic.
_AIRCRAFT_TYPES: dict[str, str] = {
    # --- Airbus, narrowbody ---
    "A318": "Airbus A318",
    "A319": "Airbus A319",
    "A320": "Airbus A320",
    "A321": "Airbus A321",
    "A19N": "Airbus A319neo",
    "A20N": "Airbus A320neo",
    "A21N": "Airbus A321neo",
    "BCS1": "Airbus A220-100",
    "BCS3": "Airbus A220-300",
    # --- Airbus, widebody ---
    "A306": "Airbus A300-600",
    "A310": "Airbus A310",
    "A332": "Airbus A330-200",
    "A333": "Airbus A330-300",
    "A338": "Airbus A330-800neo",
    "A339": "Airbus A330-900neo",
    "A342": "Airbus A340-200",
    "A343": "Airbus A340-300",
    "A345": "Airbus A340-500",
    "A346": "Airbus A340-600",
    "A359": "Airbus A350-900",
    "A35K": "Airbus A350-1000",
    "A388": "Airbus A380-800",
    "A400": "Airbus A400M Atlas",
    # --- Boeing 737 ---
    "B733": "Boeing 737-300",
    "B734": "Boeing 737-400",
    "B735": "Boeing 737-500",
    "B736": "Boeing 737-600",
    "B737": "Boeing 737-700",
    "B738": "Boeing 737-800",
    "B739": "Boeing 737-900",
    "B37M": "Boeing 737 MAX 7",
    "B38M": "Boeing 737 MAX 8",
    "B39M": "Boeing 737 MAX 9",
    "B3XM": "Boeing 737 MAX 10",
    "B712": "Boeing 717-200",
    # --- Boeing 747 / 757 / 767 ---
    "B741": "Boeing 747-100",
    "B742": "Boeing 747-200",
    "B743": "Boeing 747-300",
    "B744": "Boeing 747-400",
    "B748": "Boeing 747-8",
    "BLCF": "Boeing 747 Dreamlifter",
    "B752": "Boeing 757-200",
    "B753": "Boeing 757-300",
    "B762": "Boeing 767-200",
    "B763": "Boeing 767-300",
    "B764": "Boeing 767-400",
    # --- Boeing 777 / 787 ---
    "B772": "Boeing 777-200",
    "B77L": "Boeing 777-200LR / 777F",
    "B773": "Boeing 777-300",
    "B77W": "Boeing 777-300ER",
    "B778": "Boeing 777-8",
    "B779": "Boeing 777-9",
    "B788": "Boeing 787-8 Dreamliner",
    "B789": "Boeing 787-9 Dreamliner",
    "B78X": "Boeing 787-10 Dreamliner",
    # --- McDonnell Douglas ---
    "MD11": "McDonnell Douglas MD-11",
    "MD82": "McDonnell Douglas MD-82",
    "MD83": "McDonnell Douglas MD-83",
    "MD88": "McDonnell Douglas MD-88",
    "MD90": "McDonnell Douglas MD-90",
    "DC10": "McDonnell Douglas DC-10",
    # --- Embraer ---
    "E135": "Embraer ERJ-135",
    "E145": "Embraer ERJ-145",
    "E170": "Embraer E170",
    "E75S": "Embraer E175 (short wing)",
    "E75L": "Embraer E175 (long wing)",
    "E190": "Embraer E190",
    "E195": "Embraer E195",
    "E290": "Embraer E190-E2",
    "E295": "Embraer E195-E2",
    "E120": "Embraer EMB-120 Brasilia",
    "E50P": "Embraer Phenom 100",
    "E55P": "Embraer Phenom 300",
    "E545": "Embraer Legacy 450",
    "E550": "Embraer Legacy 500",
    # --- Bombardier regional ---
    "CRJ1": "Bombardier CRJ-100",
    "CRJ2": "Bombardier CRJ-200",
    "CRJ7": "Bombardier CRJ-700",
    "CRJ9": "Bombardier CRJ-900",
    "CRJX": "Bombardier CRJ-1000",
    "DH8A": "De Havilland Dash 8-100",
    "DH8B": "De Havilland Dash 8-200",
    "DH8C": "De Havilland Dash 8-300",
    "DH8D": "De Havilland Dash 8-400",
    # --- Bombardier business ---
    "CL30": "Bombardier Challenger 300",
    "CL35": "Bombardier Challenger 350",
    "CL60": "Bombardier Challenger 600",
    "GL5T": "Bombardier Global 5000",
    "GL7T": "Bombardier Global 7500",
    "GLEX": "Bombardier Global Express",
    "LJ31": "Learjet 31",
    "LJ35": "Learjet 35",
    "LJ40": "Learjet 40",
    "LJ45": "Learjet 45",
    "LJ60": "Learjet 60",
    "LJ75": "Learjet 75",
    # --- Cessna ---
    "C172": "Cessna 172 Skyhawk",
    "C182": "Cessna 182 Skylane",
    "C206": "Cessna 206 Stationair",
    "C208": "Cessna 208 Caravan",
    "C210": "Cessna 210 Centurion",
    "C25A": "Cessna Citation CJ2",
    "C25B": "Cessna Citation CJ3",
    "C25C": "Cessna Citation CJ4",
    "C500": "Cessna Citation I",
    "C510": "Cessna Citation Mustang",
    "C525": "Cessna CitationJet",
    "C550": "Cessna Citation II",
    "C560": "Cessna Citation V",
    "C56X": "Cessna Citation Excel",
    "C650": "Cessna Citation III",
    "C680": "Cessna Citation Sovereign",
    "C68A": "Cessna Citation Latitude",
    "C700": "Cessna Citation Longitude",
    "C750": "Cessna Citation X",
    # --- Gulfstream / Dassault ---
    "GLF4": "Gulfstream IV",
    "GLF5": "Gulfstream V",
    "GLF6": "Gulfstream G650",
    "G150": "Gulfstream G150",
    "G280": "Gulfstream G280",
    "GALX": "Gulfstream G200 Galaxy",
    "F2TH": "Dassault Falcon 2000",
    "F900": "Dassault Falcon 900",
    "FA20": "Dassault Falcon 20/200",
    "FA7X": "Dassault Falcon 7X",
    "FA8X": "Dassault Falcon 8X",
    # --- Turboprop / utility ---
    "PC12": "Pilatus PC-12",
    "PC24": "Pilatus PC-24",
    "AT43": "ATR 42-300",
    "AT45": "ATR 42-500",
    "AT72": "ATR 72",
    "AT75": "ATR 72-500",
    "AT76": "ATR 72-600",
    "SF34": "Saab 340",
    "SB20": "Saab 2000",
    "BE20": "Beechcraft King Air 200",
    "BE30": "Beechcraft King Air 350",
    "B350": "Beechcraft King Air 350",
    "BE9L": "Beechcraft King Air 90",
    "BE40": "Beechcraft Premier / Beechjet",
    "BE58": "Beechcraft Baron 58",
    "BE36": "Beechcraft Bonanza 36",
    "DHC6": "De Havilland Twin Otter",
    # --- Piston general aviation ---
    "P28A": "Piper PA-28 Cherokee",
    "P28R": "Piper PA-28R Arrow",
    "PA31": "Piper PA-31 Navajo",
    "PA34": "Piper PA-34 Seneca",
    "PA44": "Piper PA-44 Seminole",
    "PA46": "Piper PA-46 Malibu",
    "SR20": "Cirrus SR20",
    "SR22": "Cirrus SR22",
    "S22T": "Cirrus SR22T",
    "SF50": "Cirrus Vision Jet",
    "DA40": "Diamond DA40",
    "DA42": "Diamond DA42 Twin Star",
    "DA62": "Diamond DA62",
    "M20P": "Mooney M20",
    "C77R": "Cessna 177 Cardinal RG",
    # --- Helicopters ---
    "R22": "Robinson R22",
    "R44": "Robinson R44",
    "R66": "Robinson R66",
    "B06": "Bell 206 JetRanger",
    "B407": "Bell 407",
    "B429": "Bell 429",
    "EC30": "Airbus H125",
    "EC35": "Airbus H135",
    "EC45": "Airbus H145",
    "AS50": "Airbus AS350 Ecureuil",
    "A139": "Leonardo AW139",
    "S76": "Sikorsky S-76",
    # --- Other / regional manufacturers ---
    "F100": "Fokker 100",
    "F70": "Fokker 70",
    "SU95": "Sukhoi Superjet 100",
    "C919": "COMAC C919",
    "ARJ2": "COMAC ARJ21",
    "IL76": "Ilyushin Il-76",
    "AN12": "Antonov An-12",
    "A124": "Antonov An-124 Ruslan",
    # --- Military types seen in civil airspace ---
    "C130": "Lockheed C-130 Hercules",
    "C30J": "Lockheed C-130J Super Hercules",
    "C17": "Boeing C-17 Globemaster III",
    "K35R": "Boeing KC-135 Stratotanker",
    "P8": "Boeing P-8 Poseidon",
    "H60": "Sikorsky UH-60 Black Hawk",
    "AA1": "Grumman American AA-1",
    "AA5": "Grumman American AA-5 Tiger",
    "AC11": "Rockwell Commander 112/114",
    "AC90": "Rockwell Turbo Commander 690",
    "B190": "Beechcraft 1900",
    "B721": "Boeing 727-100",
    "B722": "Boeing 727-200",
    "B733": "Boeing 737-300",
    "BALL": "Balloon",
    "BE35": "Beechcraft Bonanza 35",
    "BE55": "Beechcraft Baron 55",
    "BE76": "Beechcraft Duchess",
    "BE95": "Beechcraft Travel Air",
    "BE99": "Beechcraft 99",
    "C150": "Cessna 150",
    "C152": "Cessna 152",
    "C177": "Cessna 177 Cardinal",
    "C185": "Cessna 185 Skywagon",
    "C310": "Cessna 310",
    "C340": "Cessna 340",
    "C402": "Cessna 402",
    "C414": "Cessna 414",
    "C421": "Cessna 421",
    "C72R": "Cessna 172RG Cutlass",
    "C82R": "Cessna R182 Skylane RG",
    "C82S": "Cessna T182 Turbo Skylane",
    "C82T": "Cessna TR182 Turbo Skylane RG",
    "COL4": "Cessna TTx / Corvalis",
    "DA20": "Diamond DA20 Katana",
    "DH3T": "De Havilland DHC-3 Turbo Otter",
    "DHC2": "De Havilland DHC-2 Beaver",
    "DV20": "Diamond DA20 Katana",
    "E135": "Embraer ERJ-135",
    "E45X": "Embraer ERJ-145XR",
    "EPIC": "Epic LT",
    "GLID": "Glider",
    "GYRO": "Gyrocopter",
    "H25B": "Hawker 750/850",
    "H25C": "Hawker 1000",
    "H500": "Hughes 500",
    "P32R": "Piper PA-32R Lance/Saratoga",
    "P46T": "Piper PA-46 Meridian",
    "PA18": "Piper PA-18 Super Cub",
    "PA23": "Piper PA-23 Apache/Aztec",
    "PA25": "Piper PA-25 Pawnee",
    "PA32": "Piper PA-32 Cherokee Six",
    "RV10": "Van's RV-10",
    "RV12": "Van's RV-12",
    "RV14": "Van's RV-14",
    "RV6": "Van's RV-6",
    "RV7": "Van's RV-7",
    "RV8": "Van's RV-8",
    "RV9": "Van's RV-9",
    "SLG2": "Sling 2",
    "SLG4": "Sling 4",
    "SW4": "Swearingen Metro",
    "T206": "Cessna T206 Turbo Stationair",
    "T210": "Cessna T210 Turbo Centurion",
    "T34P": "Beechcraft T-34 Mentor",
    "TBM7": "Daher TBM 700",
    "TBM8": "Daher TBM 850",
    "TBM9": "Daher TBM 900",
    "TEX2": "Beechcraft T-6 Texan II",
    "ULAC": "Ultralight",
}


# Manufacturer inferred from the designator's prefix, for types not in the
# table above. ICAO designators are manufacturer-clustered, so "B7.." is a
# Boeing and "A3.." is an Airbus even when the exact model is unrecognised.
#
# Order matters: earlier rules win. Anything that would be swallowed by a
# broader prefix has to come first -- see _EXACT_MANUFACTURER for designators
# that collide outright.
_EXACT_MANUFACTURER: dict[str, str] = {
    # "C17" would otherwise capture "C172", the Cessna Skyhawk.
    "C17": "Boeing",
    "P8": "Boeing",
    "C5M": "Lockheed",
    "A400": "Airbus",
}

_MANUFACTURER_PREFIXES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("BCS",), "Airbus"),
    (("BLCF",), "Boeing"),
    (("B350", "B190", "BE", "B35", "B36", "B58", "B60"), "Beechcraft"),
    (("B06", "B407", "B412", "B429", "B430", "B505"), "Bell"),
    (("C919", "ARJ"), "COMAC"),
    (("C130", "C30J"), "Lockheed"),
    (("K35", "KC1"), "Boeing"),
    (("CRJ", "CL3", "CL6", "GLEX", "GL5", "GL7", "BD1"), "Bombardier"),
    (("DH8", "DHC"), "De Havilland Canada"),
    (("DA2", "DA3", "DA4", "DA6"), "Diamond"),
    (("DC", "MD"), "McDonnell Douglas"),
    (("EC1", "EC2", "EC3", "EC4", "EC6", "EC7"), "Airbus Helicopter"),
    (("F70", "F100", "F28"), "Fokker"),
    (("F2", "F9", "FA"), "Dassault"),
    (("GLF", "G15", "G20", "G28", "GALX"), "Gulfstream"),
    (("LJ",), "Learjet"),
    (("P28", "P32", "P46", "P3", "P4", "PA"), "Piper"),
    (("PC",), "Pilatus"),
    (("SR2", "S22", "SF50"), "Cirrus"),
    (("SF3", "SB2"), "Saab"),
    (("AT4", "AT7"), "ATR"),
    (("A124", "A225", "AN"), "Antonov"),
    (("A109", "A119", "A139", "A169", "A189"), "Leonardo"),
    (("AS3", "AS5", "AS6", "H12", "H13", "H14", "H16"), "Airbus Helicopter"),
    (("IL",), "Ilyushin"),
    (("SU",), "Sukhoi"),
    (("R22", "R44", "R66"), "Robinson"),
    (("M20",), "Mooney"),
    (("TBM",), "Daher"),
    (("S76", "S92", "H60"), "Sikorsky"),
    # Broad family prefixes last.
    (("H25",), "Hawker"),
    (("H50", "H36", "H269"), "Hughes / MD Helicopter"),
    (("TEX", "T34", "T6"), "Beechcraft"),
    (("DH1", "DH2", "DH3", "DH4", "DH6", "DHC"), "De Havilland Canada"),
    (("SLG",), "Sling Aircraft"),
    (("RV",), "Van's Aircraft"),
    (("DV",), "Diamond"),
    (("AA1", "AA5"), "Grumman American"),
    (("SW2", "SW3", "SW4"), "Swearingen"),
    (("AC6", "AC9", "AC11", "AC50"), "Rockwell Commander"),
    (("TBM",), "Daher"),
    (("EPIC",), "Epic Aircraft"),
    (("A19", "A20", "A21", "A2", "A3"), "Airbus"),
    (("B3", "B7"), "Boeing"),
    (("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "T20", "T21", "COL"), "Cessna"),
    (("E1", "E2", "E3", "E4", "E5", "E7", "E9"), "Embraer"),
)


def lookup_aircraft(type_code: str | None) -> str | None:
    """Return the exact model name for a designator, or ``None``.

    ``"B753"`` -> ``"Boeing 757-300"``
    ``"B7XX"`` -> ``None`` (see :func:`describe_aircraft` for a fallback)
    """
    if not type_code:
        return None
    return _AIRCRAFT_TYPES.get(str(type_code).strip().upper())


def lookup_manufacturer(type_code: str | None) -> str | None:
    """Return the manufacturer for a designator, or ``None``.

    Works for designators missing from :data:`_AIRCRAFT_TYPES`, since ICAO
    designators are clustered by manufacturer.

    ``"B753"`` -> ``"Boeing"``
    ``"B7XX"`` -> ``"Boeing"``
    ``"ZZZZ"`` -> ``None``
    """
    if not type_code:
        return None
    text = str(type_code).strip().upper()
    if text in _EXACT_MANUFACTURER:
        return _EXACT_MANUFACTURER[text]
    for prefixes, name in _MANUFACTURER_PREFIXES:
        if text.startswith(prefixes):
            return name
    return None


def describe_aircraft(type_code: str | None) -> str | None:
    """Best available description of an aircraft type.

    Prefers the exact model, falls back to manufacturer plus the raw
    designator, and returns ``None`` only when neither can be determined.

    ``"B753"`` -> ``"Boeing 757-300"``
    ``"B7XX"`` -> ``"Boeing (B7XX)"``
    ``"ZZZZ"`` -> ``None``
    """
    if not type_code:
        return None
    text = str(type_code).strip().upper()

    exact = lookup_aircraft(text)
    if exact:
        return exact

    maker = lookup_manufacturer(text)
    if maker:
        return f"{maker} ({text})"

    return None
# --------------------------------------------------------------------------
# Emitter category.
#
# ! THE FEED ALREADY KNOWS WHAT KIND OF AIRCRAFT THIS IS, and the integration
# was throwing it away. Measured 2026-09-11: emitter_category was present on
# 100% of aircraft and every single marker still rendered as mdi:airplane -
# including a Bell 407 and a Bell 429 belonging to the City of Chicago.
#
# ! THIS IS WHY "Aircraft" IS THE NAME. A7 is ROTORCRAFT, and the naming
# rationale in this integration's SSOT is built on rotorcraft not being an
# edge case. Drawing them all as aeroplanes contradicted the one decision the
# name was chosen to honour.
#
# ! icon_category and category_label are D4 DISPLAY HELPERS - a consumer MAY
# use them and MUST NOT require them. They exist because ha-map-card cannot
# compute on attributes; the physics is emitter_category and that is emitted
# unchanged beside them.
# --------------------------------------------------------------------------

_CATEGORY = {
    "A0": ("airplane", "Aircraft", "mdi:airplane"),
    "A1": ("airplane", "Light aircraft", "mdi:airplane"),
    "A2": ("airplane", "Small aircraft", "mdi:airplane"),
    "A3": ("airplane", "Large aircraft", "mdi:airplane"),
    "A4": ("airplane", "Large aircraft (high vortex)", "mdi:airplane"),
    "A5": ("airplane", "Heavy aircraft", "mdi:airplane"),
    "A6": ("airplane", "High performance", "mdi:airplane"),
    "A7": ("rotorcraft", "Rotorcraft", "mdi:helicopter"),
    "B1": ("glider", "Glider", "mdi:airplane"),
    "B2": ("balloon", "Balloon or airship", "mdi:airballoon"),
    "B3": ("parachutist", "Parachutist", "mdi:parachute"),
    "B4": ("ultralight", "Ultralight", "mdi:airplane"),
    "B6": ("uav", "Unmanned", "mdi:quadcopter"),
    "B7": ("space", "Space vehicle", "mdi:rocket-launch"),
    # C1-C3 are SURFACE vehicles and obstacles. They are filtered out at the
    # source, so reaching this table would be a bug - mapped anyway so it
    # would be visible rather than silent.
    "C1": ("surface", "Surface vehicle (emergency)", "mdi:truck"),
    "C2": ("surface", "Surface vehicle (service)", "mdi:truck"),
    "C3": ("obstacle", "Point obstacle", "mdi:tower-fire"),
}

# ! A FALLBACK FOR WHEN THE FEED DOES NOT SAY. Type designators are a weaker
# signal than emitter_category and are used only when it is absent - a
# rotorcraft drawn as an aeroplane is a worse error than a missing icon.
#
# ! EXACT DESIGNATORS FIRST, PREFIXES ONLY WHERE THEY CANNOT COLLIDE.
# The first version of this was prefixes alone, and "A19" matched **A19N,
# the Airbus A319neo** - an airliner drawn as a helicopter, which is the
# worst mistake this table can make. Found by testing the rule against all
# 246 designators in _AIRCRAFT_TYPES rather than by reading it.
#
# ! THE TEST IS THE POINT, NOT THE LIST. Any addition here must be re-run
# against the table: `classify(None, t)` over every designator, and a
# fixed-wing type coming back "rotorcraft" is a defect. Two-character and
# three-character prefixes are where collisions live - prefer the full code.
_ROTOR_TYPES = frozenset((
    # Bell
    "B06", "B06T", "B204", "B205", "B206", "B210", "B212", "B214", "B222",
    "B230", "B407", "B412", "B427", "B429", "B430", "B505", "B525", "B47G",
    "B47J", "UH1", "UH1H", "UH1Y", "H1",
    # Robinson
    "R22", "R44", "R66",
    # Airbus Helicopters / Eurocopter / Aerospatiale
    "AS50", "AS55", "AS65", "AS32", "AS3B", "ASetc", "ALO2", "ALO3",
    "EC20", "EC25", "EC30", "EC35", "EC45", "EC55", "EC75", "EC20",
    "H125", "H130", "H135", "H145", "H160", "H175", "H215", "H225",
    "GAZL", "PUMA", "SUCO",
    # Leonardo / AgustaWestland
    "A109", "A119", "A139", "A169", "A189", "AW09", "AW139", "EH10", "A129",
    # Sikorsky
    "S61", "S61R", "S64", "S70", "S76", "S92", "H60", "UH60", "MH60", "S300",
    # Boeing / vertical lift
    "CH47", "H47", "V22", "V280", "CH46", "AH64", "H64",
    # MD / Hughes / Schweizer / Enstrom
    "MD50", "MD52", "MD53", "MD60", "MD62", "MD87H", "H500", "H269", "H369",
    "EN28", "EN48", "S269", "S300C",
    # Russian
    "MI8", "MI17", "MI24", "MI26", "MI2", "KA32", "KA26", "KA52",
    # Other
    "NH90", "LYNX", "EH101", "AW101", "W3", "BK17", "BO05", "SK76",
))

# Prefix families that cannot collide with a fixed-wing designator. Each is
# four characters or a three-character stem verified against the type table.
_ROTOR_PREFIXES = (
    "EC1", "EC2", "EC3", "EC4", "EC5", "EC6", "EC7",   # Eurocopter EC1xx-EC7xx
    "AS3", "AS5", "AS6",                               # AS332/350/355/365
    "MI",                                              # Mil Mi-
    "KA",                                              # Kamov Ka-
    "MD5", "MD6",                                      # MD 500/600 - NOT MD8/MD9
    "B06", "B21", "B22", "B23", "B40", "B41", "B42", "B43", "B47",
)


def classify(emitter_category: str | None, type_code: str | None):
    """(icon_category, category_label, icon) - never None."""
    cat = (emitter_category or "").strip().upper()
    if cat in _CATEGORY:
        return _CATEGORY[cat]
    t = (type_code or "").strip().upper()
    if t:
        if t in _ROTOR_TYPES or any(t.startswith(p) for p in _ROTOR_PREFIXES):
            return ("rotorcraft", "Rotorcraft", "mdi:helicopter")
    return ("airplane", "Aircraft", "mdi:airplane")
