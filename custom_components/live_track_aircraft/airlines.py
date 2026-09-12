"""Operator lookup for Flights Above.

The ADS-B feed gives a callsign but never the airline behind it. For airline
traffic the first three characters are the operator's ICAO designator
(``UAL308`` -> United Airlines), so a simple prefix lookup turns a callsign
into something a human recognises.

General-aviation aircraft usually fly under their own registration rather than
an airline callsign, which is why an N-number is reported as private traffic
instead of being matched against the table.
"""

from __future__ import annotations

import re

# ICAO three-letter operator designators -> operator name.
# Not exhaustive: covers the carriers most likely to appear over Europe and
# North America, plus the major cargo operators.
_OPERATORS: dict[str, str] = {
    # --- North America, mainline ---
    "AAL": "American Airlines",
    "UAL": "United Airlines",
    "DAL": "Delta Air Lines",
    "SWA": "Southwest Airlines",
    "JBU": "JetBlue Airways",
    "ASA": "Alaska Airlines",
    "NKS": "Spirit Airlines",
    "FFT": "Frontier Airlines",
    "HAL": "Hawaiian Airlines",
    "AAY": "Allegiant Air",
    "SCX": "Sun Country Airlines",
    "MXY": "Breeze Airways",
    # --- North America, regional ---
    "RPA": "Republic Airways as American Eagle, Delta Connection or United Express",
    "SKW": "SkyWest Airlines as American Eagle, Delta Connection, United Express or Alaska SkyWest",
    "ENY": "American Eagle by Envoy Air",
    "EDV": "Delta Connection by Endeavor Air",
    # Mesa merged into Republic Airways Holdings 2025-11-25 but retains its
    # own AOC and callsign. United Express is a 10-year contract, not
    # ownership — recheck periodically.
    "ASH": "United Express by Mesa Airlines",
    "JIA": "American Eagle by PSA Airlines",
    "PDT": "American Eagle by Piedmont Airlines",
    "GJS": "United Express by GoJet Airlines",
    "QXE": "Alaska Horizon by Horizon Air",
    # --- Canada / Mexico / Latin America ---
    "ACA": "Air Canada",
    "ROU": "Air Canada Rouge",
    "JZA": "Jazz Aviation",
    "WJA": "WestJet",
    "POE": "Porter Airlines",
    "AMX": "Aeromexico",
    "VOI": "Volaris",
    "CMP": "Copa Airlines",
    "AVA": "Avianca",
    "ARG": "Aerolineas Argentinas",
    "TAM": "LATAM Brasil",
    "LAN": "LATAM Airlines",
    # --- Europe ---
    "BAW": "British Airways",
    "VIR": "Virgin Atlantic",
    "DLH": "Lufthansa",
    "AFR": "Air France",
    "KLM": "KLM",
    "IBE": "Iberia",
    "SWR": "Swiss",
    "AUA": "Austrian Airlines",
    "SAS": "Scandinavian Airlines",
    "FIN": "Finnair",
    "ICE": "Icelandair",
    "NAX": "Norwegian",
    "EIN": "Aer Lingus",
    "BEL": "Brussels Airlines",
    "TAP": "TAP Air Portugal",
    "ITY": "ITA Airways",
    "LOT": "LOT Polish Airlines",
    "AEE": "Aegean Airlines",
    "RYR": "Ryanair",
    "EZY": "easyJet",
    "WZZ": "Wizz Air",
    "VLG": "Vueling",
    "EWG": "Eurowings",
    "TVF": "Transavia France",
    "CFG": "Condor",
    # --- Middle East / Africa / South Asia ---
    "THY": "Turkish Airlines",
    "ELY": "El Al",
    "RJA": "Royal Jordanian",
    "MSR": "EgyptAir",
    "ETH": "Ethiopian Airlines",
    "KQA": "Kenya Airways",
    "SAA": "South African Airways",
    "QTR": "Qatar Airways",
    "UAE": "Emirates",
    "ETD": "Etihad Airways",
    "AIC": "Air India",
    "IGO": "IndiGo",
    "PIA": "Pakistan International",
    # --- Asia / Pacific ---
    "JAL": "Japan Airlines",
    "ANA": "All Nippon Airways",
    "KAL": "Korean Air",
    "AAR": "Asiana Airlines",
    "CPA": "Cathay Pacific",
    "CCA": "Air China",
    "CES": "China Eastern",
    "CSN": "China Southern",
    "EVA": "EVA Air",
    "CAL": "China Airlines",
    "SIA": "Singapore Airlines",
    "THA": "Thai Airways",
    "MAS": "Malaysia Airlines",
    "GIA": "Garuda Indonesia",
    "PAL": "Philippine Airlines",
    "QFA": "Qantas",
    "ANZ": "Air New Zealand",
    # --- Cargo ---
    "FDX": "FedEx Express",
    "UPS": "U.P.S. Airlines",
    "ABX": "ABX Air - Cargo",
    "ATN": "Air Transport International - Cargo",
    "GTI": "Atlas Air - Cargo",
    "CKS": "Kalitta Air - Cargo",
    "KFS": "Kalitta Charters - Cargo",
    "PAC": "Polar Air Cargo",
    "CLX": "Cargolux",
    "GEC": "Lufthansa Cargo",
    "NCA": "Nippon Cargo Airlines",
    "CKK": "China Cargo Airlines",
    "CAO": "Air China Cargo",
    "BOX": "AeroLogic - Cargo",
    "MPH": "Martinair Cargo",
    "SQC": "Singapore Airlines Cargo",
    "GSS": "Atlas Air (Global Supply)",
    # --- Business / fractional / state ---
    "EJA": "NetJets",
    "LXJ": "Flexjet",
    "RCH": "USAF Air Mobility Command",
    "ABY": "Air Arabia",
    "AIQ": "Thai AirAsia",
    "AMF": "Ameriflight",
    "AWI": "Air Wisconsin",
    "AXB": "Air India Express",
    "AXM": "AirAsia",
    "AZU": "Azul",
    "BCS": "European Air Transport (DHL)",
    "CAP": "Civil Air Patrol",
    "CBJ": "Beijing Capital Airlines",
    "CDG": "Shandong Airlines",
    "CFG": "Condor",
    "CHH": "Hainan Airlines",
    "CJT": "Cargojet",
    "CQH": "Spring Airlines",
    "CSC": "Sichuan Airlines",
    "CSZ": "Shenzhen Airlines",
    "CXA": "Xiamen Airlines",
    "CYO": "ATI Jet",
    "DAT": "DAT (Danish Air Transport)",
    "EJM": "Executive Jet Management",
    "EJU": "easyJet Europe",
    "EXS": "Jet2",
    "FDB": "flydubai",
    "FLE": "Flair Airlines",
    "GLO": "GOL",
    "IGO": "IndiGo",
    "JAF": "TUI fly Belgium",
    "JJP": "Jetstar Japan",
    "JST": "Jetstar",
    "JSX": "JSX",
    "JUS": "USA Jet Airlines",
    "MRA": "Martinaire",
    "MSC": "Air Cairo",
    "NSZ": "Norwegian Air Sweden",
    "PGT": "Pegasus Airlines",
    "QLK": "QantasLink",
    "RAX": "Royal Air Freight",
    "SAS": "SAS",
    "SEJ": "SpiceJet",
    "SKY": "Skymark Airlines",
    "SVA": "Saudia",
    "SXS": "SunExpress",
    "TOM": "TUI Airways",
    "TRA": "Transavia",
    "TSC": "Air Transat",
    "UCA": "CommutAir",
    "VIV": "Viva Aerobus",
    "VOZ": "Virgin Australia",
    "VTE": "Contour Aviation",
    "VTI": "Vistara",
    "WUK": "Wizz Air UK",
}

# An aircraft flying under a US registration (N followed by a digit) is
# general aviation rather than a scheduled operator.
_US_REGISTRATION = re.compile(r"^N[0-9]")

# Callsign placeholders used when the feed reports no callsign at all.
_PLACEHOLDERS = frozenset({"", "?", "UNKNOWN", "NONE", "NULL"})


def lookup_operator(callsign: str | None) -> tuple[str | None, str | None]:
    """Return ``(operator_code, operator_name)`` for a callsign.

    Both values are ``None`` when nothing sensible can be derived, so callers
    can pass the result straight through to entity attributes.

    ``("UAL", "United Airlines")``  a known airline
    ``("ZZZ", None)``               looks like a designator, not in the table
    ``(None, "Private")``  flying under a US registration
    ``(None, None)``                no usable callsign
    """
    if not callsign:
        return None, None

    text = str(callsign).strip().upper()
    if text in _PLACEHOLDERS:
        return None, None

    if _US_REGISTRATION.match(text):
        return None, "Private"

    prefix = text[:3]
    if len(prefix) < 3 or not prefix.isalpha():
        return None, None

    return prefix, _OPERATORS.get(prefix)
