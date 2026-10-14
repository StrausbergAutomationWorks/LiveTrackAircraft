"""The route artifact: a shared, LADD-filtered lookup this integration READS.

! THIS INTEGRATION NEVER BUILDS THE LIST AND NEVER TOUCHES TFMS.
02_REPOS_AND_BRANCHES.md draws that boundary hard: the route service holds
the SCDS credentials and does the filtering; an integration receives data
already filtered and treats `ladd_applied` as its contract. This module is
the consumer half and nothing more.

! ONE FILE, ONE NAME, SHARED BY EVERY SAW INTEGRATION. The path is
.storage/saw_routes_and_owners.sqlite - not named after any integration,
because a module may not assume a particular sibling is installed. Whichever
of our integrations installs it first, the others find it; install one and
there is one copy, install three and there is still one.

! EVERY MODULE MUST FUNCTION ON ITS OWN. No artifact means no route fields
and nothing else changes. Tracking, labelling and the map are untouched.

! FAILS CLOSED, AND DELETES RATHER THAN REFUSING. Three independent checks -
expiry, a null `ladd_applied`, and the age of the LADD list the artifact was
built against - and any one of them removes the file. Refusing would leave it
on disk where a later change could start reading it again. The cost is that
routes disappear entirely, and that is the intended behaviour: a stale route
may name an aircraft that has since asked not to be tracked.
"""

from __future__ import annotations

import datetime as dt
import logging
import os
import sqlite3
from typing import Any

_LOGGER = logging.getLogger(__name__)

ARTIFACT_FILENAME = "saw_routes_and_owners.sqlite"

# ! COUPLED TO THE PUBLICATION CADENCE, and not arbitrary. The LADD list
# publishes weekly with five business days to apply it, so a list 8 days old
# means a publication was missed, and ~14 days is the outer compliance
# boundary. If the cadence changes, both move together.
WARN_LADD_AGE_DAYS = 8
MAX_LADD_AGE_DAYS = 14


def artifact_path(hass) -> str:
    return hass.config.path(".storage", ARTIFACT_FILENAME)


def _parse(ts: str | None) -> dt.datetime | None:
    if not ts:
        return None
    try:
        d = dt.datetime.fromisoformat(ts)
        return d if d.tzinfo else d.replace(tzinfo=dt.UTC)
    except ValueError:
        return None


def _reject(meta: dict, now: dt.datetime) -> str | None:
    """Why this artifact must not be used, or None if it may be."""
    applied = meta.get("ladd_applied")
    # ! ABSENCE OF THE FLAG IS NOT PERMISSION.
    if not applied or applied == "None":
        return "ladd_applied is null - not filtered, or does not say it was"

    expires = _parse(meta.get("expires"))
    if expires is None:
        return "no expires field"
    if now > expires:
        return "expired %s" % meta.get("expires")

    listed = _parse(applied)
    if listed is None:
        return "ladd_applied is not a date: %r" % applied
    age = (now - listed).days
    if age > MAX_LADD_AGE_DAYS:
        return "built against a LADD list %d days old (limit %d)" % (
            age, MAX_LADD_AGE_DAYS)
    if age >= WARN_LADD_AGE_DAYS:
        _LOGGER.warning(
            "Route artifact's LADD list is %d days old; a weekly publication "
            "has been missed. It will be refused at %d days.",
            age, MAX_LADD_AGE_DAYS)
    return None


def _delete(path: str, reason: str) -> None:
    for suffix in ("", "-wal", "-shm"):
        try:
            os.unlink(path + suffix)
        except OSError:
            pass
    _LOGGER.warning("Route artifact DELETED: %s", reason)


class RouteStore:
    """A resolver over the shared artifact. Absent or stale resolves to None.

    ! The seam that makes the source swappable. Everything above asks for a
    route by callsign and never learns whether a local file, a future
    published artifact or an HTTP service answered.
    """

    def __init__(self, hass) -> None:
        self._path = artifact_path(hass)
        self._con: sqlite3.Connection | None = None
        self._meta: dict[str, Any] = {}
        self._checked: dt.datetime | None = None
        self._has_times: tuple[sqlite3.Connection, bool] | None = None
        self.status = "not loaded"

    def close(self) -> None:
        if self._con is not None:
            self._con.close()
            self._con = None

    def reopen(self) -> None:
        """Forget the open file so the next lookup opens THE PATH again.

        ! Called after route_download.py moves a new file over the old one.
        On Linux an open connection keeps reading the replaced file until it
        is closed; without this the switch would wait up to an hour."""
        self.close()
        self._checked = None
        self._has_times = None

    def _ensure(self) -> sqlite3.Connection | None:
        now = dt.datetime.now(dt.UTC)

        # ! Re-validated periodically, NOT once at startup. Home Assistant
        # runs for weeks; a check that only fired at boot would sail past the
        # expiry indefinitely.
        if self._con is not None and self._checked is not None:
            if (now - self._checked).total_seconds() < 3600:
                return self._con
            self.close()

        if not os.path.exists(self._path):
            self.status = "absent"
            return None

        try:
            con = sqlite3.connect(
                "file:%s?mode=ro" % self._path.replace("\\", "/"), uri=True)
            meta = dict(con.execute("SELECT k, v FROM meta").fetchall())
        except sqlite3.Error as err:
            _delete(self._path, "unreadable: %s" % err)
            self.status = "unreadable - deleted"
            return None

        reason = _reject(meta, now)
        if reason:
            con.close()
            _delete(self._path, reason)
            self.status = "rejected - deleted (%s)" % reason
            return None

        self._con, self._meta, self._checked = con, meta, now
        # "public" = installed by route_download.py from the published file
        # (it writes source_sha256); anything else is a locally built file.
        self.status = "ok (%s, ladd %s, expires %s)" % (
            "public" if meta.get("source_sha256") else "local",
            meta.get("ladd_applied"), (meta.get("expires") or "")[:10])
        return con

    def lookup(self, callsign: str | None) -> dict[str, Any] | None:
        """The most-observed route for a callsign, or None.

        ! 48.7% of callsigns fly more than one route, and most of those are
        ONE city pair flown both ways. Returning the most-observed leg is a
        deliberate simplification of a ranked list the artifact already
        carries - direction is not resolved here.
        """
        if not callsign:
            return None
        con = self._ensure()
        if con is None:
            return None
        try:
            row = con.execute(
                "SELECT dep, arr, n FROM routes WHERE acid=? "
                "ORDER BY n DESC LIMIT 1", (callsign.strip().upper(),)
            ).fetchone()
        except sqlite3.Error:
            return None
        if not row or not row[0] or not row[1]:
            return None
        return {"origin_icao": row[0], "destination_icao": row[1],
                "route_observations": row[2]}

    def legs(self, callsign: str | None) -> list[tuple[str, str, int]]:
        """EVERY leg on file for a callsign, most-observed first.

        Added 2026-09-22 so route_check.choose_leg can test each leg against
        the aircraft's position instead of trusting the most-observed one.
        Same fail-closed store: no valid artifact means no legs.
        """
        if not callsign:
            return []
        con = self._ensure()
        if con is None:
            return []
        try:
            rows = con.execute(
                "SELECT dep, arr, n FROM routes WHERE acid=? ORDER BY n DESC",
                (callsign.strip().upper(),)).fetchall()
        except sqlite3.Error:
            return []
        return [(d, a, n) for d, a, n in rows if d and a]

    def leg_times(self, callsign: str | None) -> dict[tuple[str, str], dict[str, Any]]:
        """Published time windows per leg, {(dep, arr): {k: [start, len, src, n]}},
        or {} when there are none.

        Since 2026-10-13 the windows are FiledRoutesDB's own, as published
        (field `t`, installed by route_download.py into table leg_windows):
        k is d (departure, ORIGIN's local clock), a (arrival, DESTINATION's),
        dw / aw (weekend, Saturday-Sunday at the origin, present only where
        the weekend differs; d / a are then weekdays only). start is minutes
        after local midnight and already includes the lead; len is minutes.
        COMMERCIAL and CARGO legs only.

        ! The stand-in table `leg_times` of 2026-09-23 is NOT read any more.
        A locally built file that has only that table gives no times, and
        route_check treats that as no time evidence.
        ! OPTIONAL: a file without leg_windows, or a leg without a window, is
        normal - route_check then ranks on position alone.
        """
        if not callsign:
            return {}
        con = self._ensure()
        if con is None:
            return {}
        if self._has_times is None or self._has_times[0] is not con:
            try:
                ok = con.execute("SELECT 1 FROM sqlite_master WHERE type='table' "
                                 "AND name='leg_windows'").fetchone() is not None
            except sqlite3.Error:
                ok = False
            self._has_times = (con, ok)
        if not self._has_times[1]:
            return {}
        try:
            rows = con.execute(
                "SELECT dep, arr, k, start, len, src, n FROM leg_windows WHERE acid=?",
                (callsign.strip().upper(),)).fetchall()
        except sqlite3.Error:
            return {}
        out: dict[tuple[str, str], dict[str, Any]] = {}
        for d, a, k, start, length, src, n in rows:
            if d and a and k and start is not None and length is not None:
                out.setdefault((d, a), {})[k] = [start, length, src, n]
        return out
