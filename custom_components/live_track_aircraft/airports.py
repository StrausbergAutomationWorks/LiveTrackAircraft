"""Airport lookup over the shared precomputed table.

! ONE FILE, ONE NAME, SHARED BY EVERY SAW INTEGRATION:
.storage/saw_airport_zones.sqlite. Not named after any integration (shared-
file rule); whichever integration needs it first reads it, the others find it.

What it holds, per OurAirports airport: coordinates and an IANA time zone.
  zones(ident PK, tz, lat, lon, cross_check)
  aliases(code PK, ident, field)   - our code matched a column other than ident
  meta(k, v)                       - source, build date, licence, ATTRIBUTION
Built outside Home Assistant (bin\\build_airport_zones.py). Decided by Lee
2026-09-22: PRECOMPUTE and ship, rather than carry a 32 MB boundary library
into HA. Measurements: 25_FiledRoutesDB/SSOT.md, "CITIES ARE NOT IN THE DATA".

! THE TABLE STORES ZONE NAMES, NOT OFFSETS. Daylight-saving changes need
nothing from us: zoneinfo computes the offset for any instant from HA's own tz
database. Measured 2026-09-22 inside HA's Python (3.14.6, tzdata 2026.4):
America/Chicago goes CDT -> CST at 2026-11-01 07:00Z and back at 2027-03-14
08:00Z unaided. So there is NO clock-scheduled refresh here. The file is
re-read when it CHANGES ON DISK, checked hourly - that catches a new build
whenever it lands, without a restart.

! EVERY FAILURE DEGRADES TO "NO AIRPORT DATA". Absent, unreadable or
malformed: lookups return None and route verification reports "unchecked".
Tracking, labelling and the map are untouched.

! LICENCE. The zone column is derived from Timezone Boundary Builder data
(ODbL v1.0). The attribution travels in the file's own meta table.
"""
from __future__ import annotations

import datetime as dt
import logging
import os
import sqlite3
from typing import Any

_LOGGER = logging.getLogger(__name__)

AIRPORTS_FILENAME = "saw_airport_zones.sqlite"
RECHECK_S = 3600


class AirportStore:
    """Code -> {lat, lon, tz}. A code is resolved as an OurAirports ident
    first, then through the aliases table - the same order the coverage was
    measured in."""

    def __init__(self, hass) -> None:
        self._path = hass.config.path(".storage", AIRPORTS_FILENAME)
        self._con: sqlite3.Connection | None = None
        self._stamp: tuple[float, int] | None = None     # (mtime, size) of the open file
        self._checked: dt.datetime | None = None
        self._cache: dict[str, dict[str, Any] | None] = {}
        self._aliases = False
        self.meta: dict[str, str] = {}
        self.status = "not loaded"

    def close(self) -> None:
        if self._con is not None:
            try:
                self._con.close()
            except sqlite3.Error:
                pass
        self._con = None

    def _ensure(self) -> sqlite3.Connection | None:
        now = dt.datetime.now(dt.UTC)
        if self._checked is not None and (now - self._checked).total_seconds() < RECHECK_S:
            return self._con
        self._checked = now
        try:
            st = os.stat(self._path)
        except OSError:
            if self._con is not None:
                self.close()
                self._cache.clear()
            self.status = "absent"
            return None
        stamp = (st.st_mtime, st.st_size)
        if self._con is not None and stamp == self._stamp:
            return self._con                              # unchanged on disk
        # New or changed file: reopen, and forget everything cached from the old one.
        self.close()
        self._cache.clear()
        try:
            con = sqlite3.connect("file:%s?mode=ro" % self._path.replace("\\", "/"),
                                  uri=True, check_same_thread=False)
            meta = dict(con.execute("SELECT k, v FROM meta").fetchall())
            con.execute("SELECT ident, tz, lat, lon FROM zones LIMIT 1").fetchall()
        except sqlite3.Error as err:
            self.status = "unreadable: %s" % err
            _LOGGER.warning("Airport table %s unreadable: %s", self._path, err)
            return None
        has_aliases = bool(con.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='aliases'").fetchone())
        self._con, self._stamp, self.meta = con, stamp, meta
        self._aliases = has_aliases
        self.status = "ok (built %s, %s airports%s)" % (
            (meta.get("built") or "")[:10], meta.get("rows", "?"), "" if has_aliases else ", no aliases")
        _LOGGER.debug("Airport table loaded: %s", self.status)
        return con

    def lookup(self, code: str | None) -> dict[str, Any] | None:
        """{'lat', 'lon', 'tz', 'ident'} for one of our airport codes, or None."""
        if not code:
            return None
        con = self._ensure()
        if con is None:
            return None
        code = code.strip().upper()
        if code in self._cache:
            return self._cache[code]
        out = None
        try:
            row = con.execute("SELECT ident, tz, lat, lon FROM zones WHERE ident=?", (code,)).fetchone()
            if row is None and self._aliases:
                row = con.execute(
                    "SELECT z.ident, z.tz, z.lat, z.lon FROM aliases a JOIN zones z ON z.ident=a.ident "
                    "WHERE a.code=?", (code,)).fetchone()
            if row is not None:
                out = {"ident": row[0], "tz": row[1], "lat": row[2], "lon": row[3]}
        except sqlite3.Error:
            return None                                   # do not cache a failure
        self._cache[code] = out
        return out
