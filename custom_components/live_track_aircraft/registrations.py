"""Resolve US government aircraft from their Mode S address.

The ADS-B feeds give a callsign and a type designator. For airline traffic the
callsign resolves to an operator via airlines.py. For an aircraft squawking its
registration - N911VH, say - there is nothing to resolve against, and the
honest fallback is "Private / General Aviation".

That fallback is wrong for a large and locally visible class of aircraft:
police, sheriff, fire and air-ambulance helicopters, which orbit at low level
and are exactly what a person looking up wants identified. They transmit an
N-number as their callsign and appear in no commercial aircraft database -
adsbdb.com and hexdb.io both 404 on them.

The FAA Releasable Aircraft Database does list them, keyed by the Mode S hex
that ADS-B transmits. This module builds a table of EVERY government-
registered aircraft from it - every aircraft type, drones excluded - and
refreshes it periodically. (Until 2026-10-22 this docstring said "crewed
rotorcraft"; the table had held every type since the fork's local change.)

SCOPE - this is deliberately inert outside the US:
  * The table only loads when the configured location is in US territory.
  * Lookups only run for hex addresses in the US ICAO block A00000-AFFFFF.
A user in Europe downloads nothing, parses nothing, and sees no change.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

_LOGGER = logging.getLogger(__name__)

# ⚠ NO TABLE IS SHIPPED. This path is where a bundled snapshot WOULD live;
# it is deliberately absent, and every load path handles that - load() returns
# 0 on a missing file and lookup_government() returns None on an empty table.
#
# Two reasons not to ship one:
#
#   * The integration refreshes itself at setup. __init__.py fires
#     async_refresh_registry as a background task immediately, then daily, and
#     _needs_refresh() is True when no cache exists - so a fresh install has a
#     current table within minutes, not after REFRESH_DAYS.
#   * A snapshot cannot be kept current. Measured: 456 of 5,730 government
#     aircraft are on the FAA LADD list, and 8% of that table would go stale
#     the moment an operator enrolled. Shipping the FAA's own download instead
#     of a copy of it means every install has data as fresh as its last
#     refresh, obtained directly from the source under no agreement.
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "gov_aircraft.json")

# US ICAO 24-bit allocation. Exact, not heuristic.
US_HEX_MIN = 0xA00000
US_HEX_MAX = 0xAFFFFF

# Coarse boxes covering the US and its territories. The point is to avoid a
# 73 MB download for someone nowhere near the US, not to police borders - the
# CONUS box does catch southern Canada, which is harmless because Canadian
# aircraft are C0xxxx and fail the hex gate anyway.
_US_BOXES = (
    (24.4, 49.4, -125.0, -66.9),    # CONUS
    (51.0, 71.5, -168.0, -129.0),   # Alaska
    (51.0, 56.0, 172.0, 180.0),     # Aleutians beyond the antimeridian
    (18.9, 22.3, -160.3, -154.8),   # Hawaii
    (17.6, 18.6, -67.3, -64.5),     # Puerto Rico / USVI
    (13.2, 13.7, 144.6, 145.0),     # Guam
    (14.1, 15.3, 145.1, 146.1),     # Northern Marianas
)


def location_is_us(latitude: float | None, longitude: float | None,
                   country: str | None = None) -> bool:
    """Whether this install should bother with the US registry at all.

    ``country`` is Home Assistant's own configured country when available,
    which is the user's declaration and beats any bounding box. The boxes are
    the fallback for installs where it was never set.
    """
    if country:
        return country.upper() == "US"
    if latitude is None or longitude is None:
        return False
    return any(a <= latitude <= b and c <= longitude <= d
               for a, b, c, d in _US_BOXES)


def is_us_hex(hex_code: str | None) -> bool:
    """Whether a Mode S address falls in the US ICAO allocation."""
    if not hex_code:
        return False
    try:
        return US_HEX_MIN <= int(str(hex_code), 16) <= US_HEX_MAX
    except (TypeError, ValueError):
        return False


_SMALL_WORDS = {"of", "and", "the", "for", "at", "in", "on"}
_KEEP_UPPER = {"US", "USA", "USDA", "NASA", "DHS", "FBI", "DEA", "CBP", "ICE",
               "EMS", "LAPD", "NYPD", "CHP", "DPS", "ATF", "TSA", "NOAA"}


def prettify_owner(owner: str) -> str:
    """The registry stores owners in caps; make them readable."""
    words = []
    for i, w in enumerate(owner.split()):
        core = w.strip(".,")
        if core in _KEEP_UPPER:
            words.append(core)
        elif core.lower() in _SMALL_WORDS and i > 0:
            words.append(core.lower())
        elif "'" in w:                       # SHERIFF'S -> Sheriff's
            head, tail = w.split("'", 1)
            words.append(head.capitalize() + "'" + tail.lower())
        else:
            words.append(w.capitalize())
    out = " ".join(words)
    for abbr, full in (("Dept", "Department"), ("Cnty", "County")):
        out = out.replace(f" {abbr} ", f" {full} ")
        if out.endswith(f" {abbr}"):
            out = out[: -len(abbr)] + full
    return out


# ! BY WORD, NOT BY SUBSTRING (2026-10-21). The keys were substrings, and
# measured on the 5,725-row table that put 108 USDA Forest Service and a
# Minnesota wild-rice council under "Federal law enforcement" ("ICE " inside
# servICE, offICE, rICE), Marshall University under "Law enforcement", a
# Louisiana POLICE JURY (parish government) as police and a state FIRE
# MARSHAL as police. Law enforcement now draws police lights on the map
# (Lee, 2026-10-21), so a false hit is visible. Rules are tried in order;
# the first that matches wins. bin\lta_categorise_compare.py has the before
# and after.
_CATEGORY_RULES = (
    # Not police, though they carry the words.
    ("Fire / EMS", r"\bFIRE MARSHALL?S?\b"),
    ("Government", r"\bPOLICE JURY\b"),
    # ! COAST GUARD IS ITS OWN CATEGORY (Lee 2026-10-21: "army green with
    # police lights"): military fill, law-enforcement lights.
    ("Coast Guard", r"\bCOAST GUARD\b"),
    # Federal first, so the US Marshals are federal, not local.
    ("Federal law enforcement",
     r"\b(?:DEPT|DEPARTMENT|DEPARMENT) OF HOMELAND SECURITY\b"
     r"|\bCUSTOMS\b|\bBORDER (?:PROTECTION|PATROL)\b|\bCBP\b"
     r"|\bIMMIGRATION\b|\bDRUG ENFORCEMENT\b|\bDEA\b"
     r"|\bBUREAU OF INVESTIGATION\b|\bFBI\b|\bATF\b|\bSECRET SERVICE\b"
     r"|\bU ?S MARSHALL?S?\b|\bMARSHALS? SERVICE\b|\bJPATS\b"
     r"|\bDEPARTMENT OF JUSTICE\b"),
    ("Law enforcement",
     r"\bSHER+IF+'?S?\b|\bPOLICE\b|\bMARSHALS?\b|\bCONSTABLES?\b"
     r"|\bPUBLIC SAFETY\b|\b(?:DEPT|DEPARTMENT) OF SAFETY\b"
     r"|\bSTATE PATROL\b|\bHIGHWAY PATROL\b|\bDEPARTMENT OF CORRECTIONS?\b"
     r"|\bLAPD\b|\bNYPD\b|\bCHP\b|\bDPS\b|\bTROOPERS?\b"),
    ("Fire / EMS",
     r"\bFIRE\b|\bRESCUE\b|\bEMS\b|\bMEDICAL\b|\bAMBULANCE\b|\bMEDEVAC\b"
     r"|\bLIFE FLIGHT\b|\bAIR CARE\b"),
    ("Military",
     r"\bNAVAL\b|\bNAVY\b|\bARMY\b|AIR FORCE\b|\bMARINE CORPS\b"
     r"|\bNATIONAL GUARD\b|\bDEFENSE\b|\bDOD\b"),
    ("Natural resources",
     r"\bFOREST(?:RY|S)?\b|\bAPHIS\b|\bWILDLIFE\b|\bNATURAL RESOURCES?\b|\bPARKS?\b"
     r"|\bFISH AND GAME\b|\bCONSERVATION\b"),
    ("Research / academic",
     r"\bUNIVERSITY\b|\bCOLLEGE\b|\bINSTITUTE\b|\bNASA\b|\bRESEARCH\b|\bNOAA\b"),
)
_CATEGORY_RES = tuple((label, re.compile(rx)) for label, rx in _CATEGORY_RULES)

# The categories that draw police lights (icons.py). Coast Guard since
# 2026-10-22: its fill is military green (icons.MILITARY_CATEGORIES).
LAW_ENFORCEMENT = frozenset(("Law enforcement", "Federal law enforcement",
                             "Coast Guard"))
_FEDERAL_LABELLED = frozenset(("Federal law enforcement", "Coast Guard"))

# ! SHORT AGENCY CODES ON THE MARKER (Lee 2026-10-21): "DHS, CBP, FBI, USMS,
# ICE" instead of a truncated name. Tried in order, on the raw owner, and
# only for the federal categories: ICE before CBP because its name carries
# CUSTOMS; DHS last, for a DHS registration that names no component.
_AGENCY_CODES = tuple((code, re.compile(rx)) for code, rx in (
    ("ICE", r"\bIMMIGRATION\b"),
    ("CBP", r"\bCUSTOMS\b|\bBORDER (?:PROTECTION|PATROL)\b|\bCBP\b"),
    ("USCG", r"\bCOAST GUARD\b"),
    ("FBI", r"\bBUREAU OF INVESTIGATION\b|\bFBI\b"),
    ("USMS", r"\bMARSHALS? SERV|\bU ?S MARSHALL?S?\b|\bJPATS\b"),
    ("DEA", r"\bDRUG ENFORCEMENT\b|\bDEA\b"),
    ("ATF", r"\bATF\b|\bALCOHOL,? TOBACCO\b"),
    ("USSS", r"\bSECRET SERVICE\b"),
    ("DHS", r"\b(?:DEPT|DEPARTMENT|DEPARMENT) OF HOMELAND SECURITY\b"),
    ("DOJ", r"\bDEPARTMENT OF JUSTICE\b"),
))

_STATES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    "Puerto Rico": "PR",
}
_STATE_CODES = frozenset(_STATES.values())
# A state's name is shortened to its code only as the FORCE's name: "Utah
# County", "Mississippi County", "New York City" and "Washington DC" are
# places inside a state, and keep their names.
_STATE_RES = tuple((re.compile(r"^(?:State of |Commonwealth of )?%s\b(?! (?:County|Co|City|Parish|Dc)\b)"
                               % re.escape(n)), c)
                   for n, c in sorted(_STATES.items(), key=lambda kv: -len(kv[0])))
_STATE_TAIL = re.compile(r"\s+(?:%s)$" % "|".join(re.escape(n) for n in _STATES))
# Tried in order. Before the state codes: whole names with a known short form.
_FIRST = tuple((re.compile(rx), to) for rx, to in (
    (r"^(?:City of New York|New York City) Police\b.*$", "NYPD"),
    (r"^(?:City of )?Los Angeles Police\b.*$", "LAPD"),
    (r"^Washington DC\b", "DC"),
    (r"^(?:Department|Dept) of Public Safety of the State of (.+)$", r"\1 Department of Public Safety"),
    (r"^County of (.+?) (Sher+if+|Police)", r"\1 County \2"),
    (r"\s*\([^)]*\)", ""),
))
_WORDS = (
    (r"\b(?:Department|Dept) of Public Safety\b", "DPS"),
    (r"\b(?:Department|Dept) of State Police\b", "State Police"),
    (r"\b(Patrol) (?:Department|Dept) of Safety$", r"\1"),
    (r"\b(?:Department|Dept) of Safety(?: (?:&|and) Homeland Security)?\b", "DOS"),
    (r"\bHighway Patrol\b", "Hwy Patrol"),
    (r"\bSher+if+'?s? (?:Of+f?ice|Department|Dept|Depart)\b", "Sheriff"),
    (r"\bSher+if+'?s?\b", "Sheriff"),
    (r"\bPolice (?:Department|Dept)\b", "Police"),
    (r"\bMetropolitan\b", "Metro"),
    (r"\bCounty\b", "Co"),
    (r"\bDepartment\b", "Dept"),
    (r"\s+(?:Field Supp(?:ort)? )?(?:Office of )?(?:Aviation|Air Support|Air Operations|Air|Aerial|Aircraft|Headquarters)"
     r"(?: (?:Command|Unit|Section|Division|Div|Operations|Bureau))?$", ""),
)
_WORD_RES = tuple((re.compile(rx), to) for rx, to in _WORDS)


# The feed's database flags (readsb dbFlags). Lee 2026-10-21, step 2.
DBF_MILITARY, DBF_INTERESTING, DBF_PIA, DBF_LADD = 1, 2, 4, 8


def from_feed_flags(db_flags, own_op: str | None, gov: dict | None):
    """What the feed's flags add: (military, category, attributes).

    ! Every aircraft the feed flags military is drawn army green on its own
    type icon (icons.tone_for's military argument). A military aircraft is
    in no FAA table, so its category comes from the feed's owner text: a
    Coast Guard or law-enforcement owner keeps its lights, anything else is
    "Military". A government-table row keeps its own category.
    ! PIA (a Privacy ICAO Address) is a temporary hex: nothing can be looked
    up and the marker says so.
    """
    flags = db_flags if isinstance(db_flags, int) and not isinstance(db_flags, bool) and db_flags > 0 else 0
    military = bool(flags & DBF_MILITARY)
    category = (gov or {}).get("operator_category")
    extra: dict = {}
    if military:
        extra["is_military"] = True
        if gov is None:
            found = categorise(own_op) if own_op else None
            category = found if found in LAW_ENFORCEMENT else "Military"
            extra["operator_category"] = category
            extra["identified_by"] = "feed_military"
            if own_op:
                extra["operator"] = prettify_owner(own_op)
                extra["operator_name_source"] = "feed"
            short = operator_short(own_op or "", category)
            if short:
                extra["operator_short"] = short
    if flags & DBF_PIA:
        extra["identity_hidden"] = True
    return military, category, extra


def operator_short(owner: str, category: str | None) -> str | None:
    """What a law-enforcement marker says: an agency code for a federal
    agency, else the operator's name with its state and stock words
    shortened. None for any other category. Rules read against every
    law-enforcement owner in the table (bin/lta_le_labels.txt)."""
    if category not in LAW_ENFORCEMENT or not owner:
        return None
    up = " ".join(owner.upper().replace("&", " AND ").split())
    if category in _FEDERAL_LABELLED:
        for code, rx in _AGENCY_CODES:
            if rx.search(up):
                return code
    name = prettify_owner(owner)
    name = re.sub(r"-([a-z])", lambda m: "-" + m.group(1).upper(), name)
    name = re.sub(r"^City of ", "", name)
    words = name.split()
    if words and words[0].upper() in _STATE_CODES:
        words[0] = words[0].upper()
    name = " ".join("DNR" if w == "Dnr" else "DC" if w == "Dc" else w for w in words)
    for rx, to in _FIRST:
        name = rx.sub(to, name)
    for rx, code in _STATE_RES:
        if rx.search(name):
            name = rx.sub(code, name, count=1)
            break
    name = _STATE_TAIL.sub("", name)
    for rx, to in _WORD_RES:
        name = rx.sub(to, name)
    name = " ".join(name.split())
    # The label is 22 characters (coordinator.MAX_LABEL_CHARS); "San
    # Bernardino Sheriff" fits where "San Bernardino Co Sheriff" would not.
    if len(name) > 22:
        name = name.replace(" Co ", " ")
    return name or None


def categorise(owner: str) -> str:
    up = " ".join(owner.upper().replace("&", " AND ").split())
    for label, rx in _CATEGORY_RES:
        if rx.search(up):
            return label
    return "Government"


class GovRegistry:
    """The lookup table. Loaded lazily, and only for US installs."""

    def __init__(self) -> None:
        self._table: dict[str, list[str]] = {}
        self._loaded = False
        self._warned_unloaded = False
        self._law: list[str] | None = None
        self._fed: list[str] | None = None
        self.schema = 0

    def load(self, path: str | None = None) -> int:
        """Load the table from disk. Returns how many entries were read.

        Never raises: a missing or corrupt file leaves the registry empty and
        every lookup simply returns None, which is the same behaviour as not
        having the feature at all.
        """
        target = path or DATA_FILE
        try:
            with open(target, encoding="utf-8") as fh:
                payload = json.load(fh)
            table = payload.get("aircraft") if isinstance(payload, dict) else None
            if not isinstance(table, dict):
                raise ValueError("no 'aircraft' mapping in payload")
            self._table = table
            self._law = None
            self._fed = None
            self.schema = payload.get("schema", 0) if isinstance(payload.get("schema"), int) else 0
            self._loaded = True
            _LOGGER.debug("Loaded %s government aircraft from %s",
                          len(table), target)
        except Exception:  # noqa: BLE001
            self._table = {}
            self._loaded = True
            _LOGGER.debug("Could not load %s; government lookups disabled",
                          target, exc_info=True)
        return len(self._table)

    def lookup(self, hex_code: str | None) -> dict[str, Any] | None:
        """Resolve a Mode S address, or None.

        Returns None for anything outside the US ICAO block without touching
        the table, so non-US traffic costs a single integer comparison.

        ⚠ This runs in the event loop, so it must NEVER touch disk. The table
        is loaded once during setup via async_load_registry, which uses an
        executor. An earlier version lazily called self.load() from here and
        Home Assistant correctly flagged it:

            Detected blocking call to open ... inside the event loop by
            custom integration 'flights_above'

        If the table was never loaded, return None rather than loading it -
        that is the same behaviour as not having the feature.
        """
        if not is_us_hex(hex_code):
            return None
        if not self._loaded:
            if not self._warned_unloaded:
                self._warned_unloaded = True
                _LOGGER.debug(
                    "Government registry not loaded; lookups return None. "
                    "async_load_registry should have run during setup."
                )
            return None
        row = self._table.get(str(hex_code).upper())
        if not row:
            return None
        registration, owner, state = (row + ["", "", ""])[:3]
        category = categorise(owner) if owner else None
        out = {
            "registration": registration or None,
            "operator": prettify_owner(owner) if owner else None,
            "operator_category": category,
            "operator_state": state or None,
            # HOW it was identified (Lee 2026-10-21: the hover box says so).
            # A code; the words are the card's (06 D4b).
            "identified_by": ("faa_federal_list"
                              if owner.strip().upper() in _FEDERAL_OPERATOR_ALLOWLIST
                              else "faa_government"),
        }
        short = operator_short(owner, category)
        if short:
            out["operator_short"] = short
        return out

    @property
    def size(self) -> int:
        return len(self._table)

    def law_enforcement_hexes(self) -> list[str]:
        """Every hex whose owner is law enforcement (watch.py's list).
        Worked out once per table, not per poll."""
        if self._law is None:
            self._law = sorted(h.lower() for h, row in self._table.items()
                               if row and len(row) > 1
                               and categorise(row[1]) in LAW_ENFORCEMENT)
        return self._law

    def federal_law_enforcement_hexes(self) -> list[str]:
        """Every hex whose owner is FEDERAL law enforcement (watch.py, 2026-10-24).

        The EnforcementAircraft list's federal rule names the same registrants;
        asking the table as well keeps a registration newer than the list's
        build watched. Worked out once per table."""
        if self._fed is None:
            self._fed = sorted(h.lower() for h, row in self._table.items()
                               if row and len(row) > 1
                               and categorise(row[1]) == "Federal law enforcement")
        return self._fed


REGISTRY = GovRegistry()


def lookup_government(hex_code: str | None) -> dict[str, Any] | None:
    """Module-level convenience wrapper around the shared registry."""
    return REGISTRY.lookup(hex_code)



# --------------------------------------------------------------------------
# Owner lookup
#
# The government table names 5,726 aircraft. Everything else - private jets,
# flight school Cessnas, air ambulances, corporate turboprops - falls through
# to lookup_operator, which can only match airline designators, and therefore
# shows "Private". Measured: 28 of 52 occupied slots.
#
# ⚠ SQLITE, NOT A DICT, and the reason is measured. 181,538 entries are 2.32 MB
# gzipped and 7.63 MB as JSON, but 51.6 MB as a Python dict - twenty-two times
# the file size. parse_faa_archive's docstring promises "peak memory is a few
# MB, so this is safe on a Pi" and that promise is load-bearing. On disk the
# same table is 10.7 MB and a lookup costs about 51 microseconds.
#
# ⚠ NOTHING IS SHIPPED. This is built from the archive the integration ALREADY
# downloads every REFRESH_DAYS for the government table.
#
# ⚠ INDIVIDUAL REGISTRANTS ARE EXCLUDED. Section 803 of the FAA
# Reauthorization Act of 2024 (49 USC 44114, effective 2025-03-28) defines
# personally identifiable information to include the name of the owner where
# the owner is an individual. TYPE REGISTRANT = 1 is dropped: 126,404 of
# 316,483 rows. That sounds fatal to the feature and is not - measured against
# 28 unnamed aircraft overhead, 26 would still be named, because light aircraft
# near a city are overwhelmingly flight school and rental fleets registered to
# companies.
#
# ! SUPERSEDED 2026-09-12 - THIS FILTER NO LONGER EXISTS. The paragraph
# above describes what the FORK still does, and is kept for that reason.
# The withholding is applied by the FAA BEFORE the archive is published,
# so TYPE REGISTRANT = 1 was never the Section 803 population. See the
# DIVERGENCE comment inside build_owner_db below, and
# 30_Integrations/Live_Track_Aircraft/SSOT.md.
# --------------------------------------------------------------------------

_TYPE_REGISTRANT_INDIVIDUAL = "1"


def owner_db_path(hass) -> str:
    # ! DIVERGENCE FROM THE FORK'S COPY, and the only one. This read
    # "flights_above_owners.sqlite".
    #
    # EVERY MODULE MUST FUNCTION ON ITS OWN. They are modules so a user can
    # install only what they want, and a path named after another
    # integration assumes that integration is present. On a clean machine it
    # names something that does not exist.
    #
    # The name is SAW-neutral rather than live_track_aircraft-specific on
    # purpose: this is a cache of a PUBLIC dataset, not integration state.
    # Whichever of our integrations needs it first builds it; the others
    # find it. Install one, one download; install three, still one.
    # Nothing depends on another integration having run.
    return hass.config.path(".storage", "saw_faa_owners.sqlite")


def build_owner_db(raw: bytes, db_path: str) -> int:
    """Extract owners from the FAA archive into SQLite. Returns the row count.

    ⚠ Runs on an executor thread alongside parse_faa_archive. CPU-bound.
    ⚠ Writes to a temporary file and renames, so a failure part-way through
    leaves the previous database intact rather than a half-built one.
    """
    import csv
    import io as _io
    import sqlite3
    import zipfile

    tmp = db_path + ".new"
    for p in (tmp, tmp + "-wal", tmp + "-shm"):
        try:
            os.unlink(p)
        except OSError:
            pass

    zf = zipfile.ZipFile(_io.BytesIO(raw))
    con = sqlite3.connect(tmp)
    n = 0
    try:
        con.execute("PRAGMA journal_mode=OFF")
        con.execute("PRAGMA synchronous=OFF")
        con.execute("CREATE TABLE owners (hex TEXT PRIMARY KEY, reg TEXT, "
                    "owner TEXT)")
        with zf.open("MASTER.txt") as fh:
            reader = csv.DictReader(_io.TextIOWrapper(fh, "utf-8-sig",
                                                      errors="replace"))
            batch = []
            for row in reader:
                r = {(k or "").strip(): (v or "").strip()
                     for k, v in row.items()}
                if r.get("STATUS CODE") != "V":
                    continue
                # ! DIVERGENCE FROM THE FORK'S COPY, 2026-09-11. This skipped
                # every TYPE REGISTRANT = 1 row - 126,404 of 310,098 valid
                # registrations, 40.8% - believing it implemented 49 U.S.C.
                # 44114 (Section 803).
                #
                # ! IT DID NOT. The statute binds the FAA, not us, and the
                # withholding is ALREADY APPLIED TO THE FILE WE DOWNLOAD.
                # From ardata.pdf inside this very archive: "The FAA has
                # established a procedure in accordance with 49 U.S.C. §
                # 44114(b) by which private aircraft owners can request
                # certain personally identifiable information, such as names
                # and addresses, be withheld ... Some records previously
                # found on this page are not available at this time due to
                # the implementation of these changes."
                #
                # So a name still present in the Releasable Aircraft Database
                # is a name the FAA has decided to release. Dropping type 1
                # discarded 126,404 of them and left the map showing bare
                # tail numbers instead.
                #
                # ! IT ALSO CAUGHT THE WRONG PEOPLE ANYWAY. Type 4 Co-Owned
                # (25,822) and type 2 Partnership (3,085) are usually private
                # individuals too, and both were kept - measured: N5116J,
                # "CARLL ELIZABETH M", type 4, on the map.
                #
                # ! WHAT STILL MATTERS: the snapshot AGES. A withholding
                # granted after our download stays in our copy until the next
                # refresh, which is why REFRESH_DAYS is not decoration.
                hx = (r.get("MODE S CODE HEX") or "").upper()
                name = r.get("NAME") or ""
                if not hx or not name:
                    continue
                batch.append((hx, "N" + (r.get("N-NUMBER") or ""), name[:48]))
                if len(batch) >= 5000:
                    con.executemany("INSERT OR REPLACE INTO owners "
                                    "VALUES (?,?,?)", batch)
                    n += len(batch)
                    batch = []
            if batch:
                con.executemany("INSERT OR REPLACE INTO owners VALUES (?,?,?)",
                                batch)
                n += len(batch)
        con.commit()
    finally:
        con.close()
    os.replace(tmp, db_path)
    return n


class OwnerRegistry:
    """Read-only owner lookups, held open for the life of the process."""

    def __init__(self) -> None:
        self._con = None
        self.count = 0

    def open(self, db_path: str) -> int:
        import sqlite3
        self.close()
        if not os.path.exists(db_path):
            return 0
        try:
            self._con = sqlite3.connect(
                "file:%s?mode=ro" % db_path.replace("\\", "/"),
                uri=True, check_same_thread=False)
            self.count = self._con.execute(
                "SELECT COUNT(*) FROM owners").fetchone()[0]
        except Exception:  # noqa: BLE001
            # ⚠ Degrade, never raise. A missing or corrupt database must not
            # affect setup or flight tracking - the same contract GovRegistry
            # already honours.
            _LOGGER.debug("Owner database unavailable", exc_info=True)
            self._con = None
            self.count = 0
        return self.count

    def close(self) -> None:
        if self._con is not None:
            try:
                self._con.close()
            except Exception:  # noqa: BLE001
                pass
        self._con = None
        self.count = 0

    def lookup(self, hex_code):
        if self._con is None or not hex_code:
            return None
        try:
            row = self._con.execute(
                "SELECT reg, owner FROM owners WHERE hex=?",
                (hex_code.strip().upper(),)).fetchone()
        except Exception:  # noqa: BLE001
            return None
        return {"registration": row[0], "owner": row[1]} if row else None


OWNERS = OwnerRegistry()


def lookup_owner(hex_code):
    """Registered owner for a Mode S address, or None.

    ⚠ This is the TITLE HOLDER, which is often not the operator. Measured:
    N964AV is "Avianca" to adsbdb and "Bank of Utah Trustee" to the FAA;
    N553FX is "Flexjet" and "Citation X Parts LLC". Prefer an operator name
    from any source that has one; this is the fallback that always works.
    """
    return OWNERS.lookup(hex_code)

# --------------------------------------------------------------------------
# Self-refresh
#
# The bundled snapshot ages. Rather than requiring a release for every FAA
# update, the integration refreshes itself and writes the result beside Home
# Assistant's own storage, which then takes precedence over the bundle.
#
# Everything here is best-effort. A failure leaves the previous table in place
# and is logged at debug level; it never affects setup or flight tracking.
# --------------------------------------------------------------------------

# ! DIVERGENCE FROM THE FORK'S COPY, 2026-09-11. This was 30, chosen on the
# belief that the FAA refreshed the registry monthly. NOBODY HAD MEASURED IT.
#
# ! MEASURED: the archive is rebuilt EVERY BUSINESS NIGHT, around 23:22 US
# Central. Three MASTER.txt build stamps - 2026-08-28 23:23, 2026-09-04 23:23
# and 2026-09-10 23:22 - and every member of the zip carries the same
# timestamp within twelve minutes, which is one nightly batch. The two Friday
# files are an artefact of WHEN WE DOWNLOADED: 30 August was a Sunday and
# 5 September a Saturday, so each got the previous Friday's build.
#
# ! WEEKLY IS A DELIBERATE CEILING, NOT THE SOURCE'S CADENCE. Daily would be
# a 73 MB download every night for a handful of changed rows - a nuisance for
# almost no benefit. Weekly costs four downloads a month instead of one and
# buys a worst-case staleness of 7 days instead of 30.
#
# ! THIS IS THE ONLY THING ABOUT 44114 THAT STILL BINDS US. The withholding
# itself is applied by the FAA before the file is published, so there is
# nothing to filter - but a withholding granted the day after a download sits
# in our copy until the next refresh. Freshness is the obligation; filtering
# never was.
REFRESH_DAYS = 7
FAA_URL = "https://registry.faa.gov/database/ReleasableAircraft.zip"

# A bare urllib/aiohttp UA is rejected with 403; the registry wants something
# browser-shaped.
_FAA_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"),
    "Accept": "application/zip,*/*",
}

_TYPE_ACFT_ROTORCRAFT = "6"
_TYPE_REGISTRANT_GOVERNMENT = "5"

# LOCAL CHANGE. Federal operators registered as an LLC rather than as
# government, so a registrant-code filter alone misses them. EXACT names only -
# keyword matching was measured and rejected: "MARSHAL" gives 248 hits and 4
# real ones (people surnamed Marshall, Marshall University, Marshall Soaring
# Club); "ICE" gives 14 and ZERO real ones (Ice Man Holdings, Two Bag Ice).
# ! EMPTY SINCE 2026-10-23 (Lee): both names it held were PRIVATE owners.
# HOMELAND AVIATION LLC is a Shreveport, LA owner of light piston aircraft
# (N462WC, an Aviat Husky, FAA registry); CBP AIR LOGISTICS LLC is "managed
# and wholly owned by" a private individual by its own court filing (D. Kan.
# 2:25-cv-02514). A private registrant gets an agency label only when a cited
# document backs it or Lee has reviewed it (an EnforcementAircraft entry),
# never from its name.
_FEDERAL_OPERATOR_ALLOWLIST: frozenset[str] = frozenset()
# ACFTREF TYPE-ENG: 2 turbo-prop, 3 turbo-shaft, 4 turbo-jet, 5 turbo-fan.
_TURBINE_ENGINES = frozenset(("2", "3", "4", "5"))
_DRONE_MFR_PREFIXES = (
    "DJI", "AUTEL", "YUNEEC", "3D ROBOTICS", "PARROT", "SKYDIO", "FREEFLY",
    "AGEAGLE", "INSPIRED FLIGHT", "WINGTRA", "QUANTUM SYSTEMS", "ENYU LUO",
    "SENSEFLY", "EHANG", "XIAOMI", "POWERVISION",
)


def parse_faa_archive(raw: bytes) -> dict[str, list[str]]:
    """Extract every government-registered aircraft, drones excluded.

    Streams row by row: MASTER.txt is 194 MB uncompressed and must never be
    materialised. Peak memory is a few MB, so this is safe on a Pi.

    NOTE: runs on an executor thread. It is CPU-bound for roughly 10-60 s
    depending on hardware and must not touch the event loop.
    """
    import csv
    import io as _io
    import zipfile

    zf = zipfile.ZipFile(_io.BytesIO(raw))

    def rows(name: str):
        # utf-8-sig: these files carry a BOM which would otherwise leave the
        # first column named '\ufeffCODE'.
        with zf.open(name) as fh:
            reader = csv.DictReader(_io.TextIOWrapper(fh, "utf-8-sig", errors="replace"))
            for row in reader:
                yield {(k or "").strip(): (v or "").strip() for k, v in row.items()}

    types: dict[str, tuple[str, int]] = {}
    for r in rows("ACFTREF.txt"):
        # LOCAL CHANGE: no rotorcraft filter. It excluded every government
        # FIXED-WING aircraft, so a government Gulfstream fell through to
        # lookup_operator and displayed as "Private". Measured: rotorcraft
        # only 1,595 entries; all government aircraft 5,730.
        # ! A blank or unreadable seat count is UNKNOWN, not zero: only a
        # stated 0 marks a drone below.
        try:
            seats = int(r.get("NO-SEATS") or "")
        except ValueError:
            seats = None
        types[r.get("CODE", "")] = ((r.get("MFR") or "").upper(), seats,
                                    (r.get("TYPE-ENG") or "").strip(),
                                    (r.get("AC-WEIGHT") or "").strip().upper())

    table: dict[str, list[str]] = {}
    for r in rows("MASTER.txt"):
        if (r.get("TYPE REGISTRANT") != _TYPE_REGISTRANT_GOVERNMENT
                and (r.get("NAME") or "").strip().upper()
                not in _FEDERAL_OPERATOR_ALLOWLIST):
            continue
        t = types.get(r.get("MFR MDL CODE", ""))
        if not t:
            continue
        mfr, seats, engine, weight = t
        # ! DRONES OUT (Lee, 2026-10-22). This read "drones kept", and
        # _DRONE_MFR_PREFIXES was defined and never used. Measured on the
        # FAA archive of 2026-10-21: 1,136 of 5,743 government rows had
        # ACFTREF NO-SEATS 0, every one an unmanned aircraft by make and model
        # (DJI, Skydio, Autel, Hylio, ScanEagle, MQ-9...); all 700 drone-maker
        # rows have 0 seats too, and a word search of make and model found
        # none the seat count missed. ONE seat is a real aircraft (ER-2,
        # F-16A, Air Tractor, gliders) and is kept: the fork's PR branch
        # dropped seats < 2, which was right for rotorcraft only.
        # ! The cost, measured: 10 GENERAL ATOMICS MQ-9 BLOCK 1 go with them,
        # and a large UAS can transmit ADS-B. One that does still gets its
        # owner from the owner table; it is just not drawn as government.
        # ! MQ-9 CLASS KEPT (Lee 2026-10-22 01:27): an unmanned airframe that
        # is turbine-powered (TYPE-ENG 2-5) and not weight class 4 (UAS under
        # 55 lb). Measured: 18 rows - 12 MQ-9, 4 Global Hawk, 2 Scion Weasel;
        # a turbine model jet (class 4) and a DJI coded turbofan stay out.
        # ! DRONES ARE IN THE TABLE (Lee 2026-10-22 02:31: leaving them out
        # was "the opposite of what I want"). From ed51866 to this commit
        # they were left out (0 seats or a drone maker), MQ-9 class kept
        # from 9fd867b; measured, that dropped 1,118 of 5,743 rows. A
        # government drone that broadcasts is drawn as government, with
        # lights if police. _DRONE_MFR_PREFIXES and _TURBINE_ENGINES are no
        # longer used here.
        del mfr, seats, engine, weight
        hx = (r.get("MODE S CODE HEX") or "").strip().upper()
        if hx:
            table[hx] = [
                "N" + (r.get("N-NUMBER") or "").strip(),
                (r.get("NAME") or "").strip(),
                (r.get("STATE") or "").strip(),
            ]
    return table


def cache_path(hass) -> str:
    """Where the refreshed table lives - beside HA's own storage.

    ! SAW-neutral name. See owner_db_path for why: every module must work
    on its own, so a path may not assume another integration is installed.
    ! RENAMED 2026-10-22 from saw_faa_gov_rotorcraft.json: the table had held
    every aircraft type for weeks and the name made the project's own record
    say "rotorcraft only". Measured that day: no other component on the box,
    and no branch of any SAW clone, names the old file.
    """
    return hass.config.path(".storage", CACHE_NAME)


CACHE_NAME = "saw_faa_gov_aircraft.json"
# Read only while the new file does not exist yet, so the first start after
# the rename keeps its government tones until the refresh lands; deleted after
# the first successful write.
LEGACY_CACHE_NAME = "saw_faa_gov_rotorcraft.json"
# 3 since 2026-10-22 02:3x: drones back in. A cache of an older schema is
# rebuilt at the next start (needs_refresh), not after REFRESH_DAYS.
# 4 since 2026-10-23: the two private LLCs out of the allowlist.
SCHEMA = 4
EXCLUDES = "nothing: every government registrant, drones included"


def legacy_cache_path(hass) -> str:
    return hass.config.path(".storage", LEGACY_CACHE_NAME)


def needs_refresh(path: str, loaded_schema: int) -> bool:
    """Stale by age, or built by an older rule (SCHEMA)."""
    return _needs_refresh(path) or loaded_schema < SCHEMA


def _needs_refresh(path: str) -> bool:
    import time
    try:
        age_days = (time.time() - os.path.getmtime(path)) / 86400
    except OSError:
        return True                      # no cache yet
    return age_days >= REFRESH_DAYS


async def async_load_registry(hass, latitude=None, longitude=None) -> int:
    """Load the best available table for this install.

    Prefers a refreshed cache over the bundled snapshot. Returns the number of
    entries loaded.
    """
    # ! DIVERGENCE FROM THE FORK'S COPY, 2026-09-11. A location_is_us() gate
    # stood here and returned 0 for any install outside the United States.
    #
    # ! THE GATE ASKED THE WRONG QUESTION. It tested where the INSTALL is,
    # not what the user is WATCHING - and the two are unrelated. This
    # integration lets a user set the centre to anywhere on earth, so someone
    # in Germany may quite reasonably be watching O'Hare. The gate answered
    # "not a US location" and gave them nothing.
    #
    # ! IT WAS ALSO WRONG NEAR BORDERS AND OCEANS. Dublin sits under the
    # North Atlantic tracks, Vancouver and Tijuana are minutes from US
    # traffic. All three see N-registered aircraft constantly and all three
    # were refused.
    #
    # The remaining cost is a 73 MB download for a user who never sees a US
    # aircraft. That is worth revisiting as a deferral keyed on OBSERVED
    # TRAFFIC - is_us_hex() over what is actually in radius - which is the
    # question the gate should have been asking. It is not worth another
    # geographic guess.
    cache = cache_path(hass)
    legacy = legacy_cache_path(hass)
    target = (cache if os.path.exists(cache)
              else legacy if os.path.exists(legacy) else DATA_FILE)
    n = await hass.async_add_executor_job(REGISTRY.load, target)
    # Opened here so a restart picks up an existing database without waiting
    # for the next refresh.
    await hass.async_add_executor_job(OWNERS.open, owner_db_path(hass))
    return n


async def async_refresh_registry(hass, latitude=None, longitude=None,
                                 force: bool = False) -> bool:
    """Refresh from the FAA registry if the cache is older than REFRESH_DAYS.

    Returns True only when a new table was fetched, parsed and loaded.

    Best-effort throughout: any failure leaves the existing table untouched.
    The download is ~73 MB for ~87 KB of useful data, which is unavoidable -
    the archive is one zip and DEREG.txt alone is 278 MB uncompressed.
    """
    # ! The location_is_us() gate that stood here is gone - see
    # async_load_registry above for why. The function itself is kept: it is
    # still a correct answer to "is this point in the US", which a future
    # traffic-based deferral may want.
    cache = cache_path(hass)
    if not force and not needs_refresh(cache, REGISTRY.schema):
        return False
    import aiohttp
    from homeassistant.helpers.aiohttp_client import async_get_clientsession

    _LOGGER.debug("Refreshing government aircraft registry from %s", FAA_URL)
    try:
        session = async_get_clientsession(hass)
        async with session.get(
            FAA_URL, headers=_FAA_HEADERS,
            timeout=aiohttp.ClientTimeout(total=600),
        ) as resp:
            if resp.status != 200:
                _LOGGER.debug("FAA registry returned HTTP %s", resp.status)
                return False
            raw = await resp.read()
    except Exception:  # noqa: BLE001
        _LOGGER.debug("Could not download the FAA registry", exc_info=True)
        return False

    try:
        # Parsing is CPU-bound for tens of seconds - never on the event loop.
        table = await hass.async_add_executor_job(parse_faa_archive, raw)
        # ⚠ Same archive, same executor pass. The 73 MB download is already
        # paid for; extracting owners from it costs only CPU.
        try:
            rows = await hass.async_add_executor_job(
                build_owner_db, raw, owner_db_path(hass))
            OWNERS.open(owner_db_path(hass))
            _LOGGER.debug("Owner database rebuilt: %d aircraft", rows)
        except Exception:  # noqa: BLE001
            # Never let the owner half break the government half.
            _LOGGER.debug("Owner database rebuild failed", exc_info=True)
    except Exception:  # noqa: BLE001
        _LOGGER.debug("Could not parse the FAA registry", exc_info=True)
        return False

    if not table:
        _LOGGER.debug("FAA registry parsed to an empty table; keeping the old one")
        return False

    payload = {"schema": SCHEMA, "source": "FAA Releasable Aircraft Database",
               "excludes": EXCLUDES, "count": len(table), "aircraft": table}

    def _write() -> None:
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        tmp = cache + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, separators=(",", ":"))
        os.replace(tmp, cache)           # atomic; never a half-written cache
        try:
            os.unlink(legacy_cache_path(hass))   # the pre-rename name
        except OSError:
            pass

    try:
        await hass.async_add_executor_job(_write)
    except Exception:  # noqa: BLE001
        _LOGGER.debug("Could not write the registry cache", exc_info=True)
        return False

    await hass.async_add_executor_job(REGISTRY.load, cache)
    _LOGGER.info("Government aircraft registry refreshed: %s entries", len(table))
    return True
