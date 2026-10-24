"""Download the PUBLIC FiledRoutesDB file and install it as the route artifact.

Lee, 2026-10-13: the box uses the PUBLIC artifact. This module is how any
install of Live Track Aircraft gets its routes - this machine included. It
replaces the laptop's daily SSH push of a stopgap file.

! THIS INTEGRATION STILL NEVER BUILDS THE LIST AND NEVER TOUCHES TFMS. It
downloads what the route service published (release `data` of
StrausbergAutomationWorks/FiledRoutesDB), already LADD-filtered, and treats
`ladd_applied` as its contract, exactly as routes.py does.

! ONE FILE, ONE NAME, SHARED: .storage/saw_routes_and_owners.sqlite. The name
says "owners" for history; the public file carries NO owners (owner data comes
from each install's own FAA registry download, registrations.py). The name
stays so every reader finds it where it always was.

! FAILS CLOSED, AT EVERY STEP. Nothing reaches the shared path unless the
download's SHA-256 matches the published SHA256SUMS, the format is the one
this code reads, and the same three checks routes.py applies - expiry, a null
`ladd_applied`, a LADD list more than 14 days old (warn at 8) - pass. A
refused download leaves the installed file as it was; routes.py goes on
judging that file by itself and DELETES it when it goes stale. Built under a
temporary name, read back, then moved over the old file in one rename.

! HOW OFTEN. The file is about 4.6 MB and is rebuilt once a day, at about
13:34 America/Chicago. So: at startup when the installed file is absent or
more than a day old, and once per publication after 14:00 America/Chicago.
A check first reads SHA256SUMS (89 bytes); the 4.6 MB file is fetched only
when its hash differs from the installed one. A failure is retried an hour
later, and at most MAX_DOWNLOADS_PER_SLOT large downloads are made for one
publication, so a broken publication cannot turn this into a loop.

No Home Assistant import at module level: the pure functions below are tested
offline (tests/test_download.py).
"""
from __future__ import annotations

import asyncio
import datetime as dt
import gzip
import hashlib
import json
import logging
import os
import sqlite3
from typing import Any
from zoneinfo import ZoneInfo

from .routes import ARTIFACT_FILENAME, _parse, _reject

_LOGGER = logging.getLogger(__name__)

RELEASE_URL = ("https://github.com/StrausbergAutomationWorks/FiledRoutesDB"
               "/releases/download/data/")
ASSET = "filedroutesdb.json.gz"
SUMS = "SHA256SUMS"
FORMAT = "filedroutesdb/1"

# The publication clock. The route service rebuilds at 13:30 America/Chicago
# and ships about four minutes later; checking from 14:00 leaves room.
PUBLISH_ZONE = "America/Chicago"
PUBLISH_AFTER = dt.time(14, 0)
STARTUP_MAX_AGE = dt.timedelta(days=1)
RETRY_AFTER = dt.timedelta(hours=1)
MAX_DOWNLOADS_PER_SLOT = 3
MAX_BYTES = 64 * 1024 * 1024          # the file is ~4.6 MB; a cap, not a size
MAX_SUMS_BYTES = 64 * 1024
TICK = dt.timedelta(minutes=10)       # how often due() is asked; it gates the network
TMP_SUFFIX = ".lta-new"               # not ".new": the stopgap job uses that name
WINDOW_KEYS = ("d", "a", "dw", "aw")


class InstallRefused(Exception):
    """The download must not be installed. The installed file is untouched."""


# ---------------------------------------------------------------- pure parts

def parse_sums(text: str, name: str = ASSET) -> str | None:
    """The SHA-256 SHA256SUMS gives for `name`, lower-case, or None."""
    for line in (text or "").splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[-1].lstrip("*") == name:
            h = parts[0].lower()
            if len(h) == 64 and all(c in "0123456789abcdef" for c in h):
                return h
    return None


def last_slot(now: dt.datetime) -> dt.datetime:
    """The most recent PUBLISH_AFTER on the publication clock at or before
    `now` (aware). Daylight saving moves it in UTC; it does not move locally."""
    zone = ZoneInfo(PUBLISH_ZONE)
    local = now.astimezone(zone)
    slot = dt.datetime.combine(local.date(), PUBLISH_AFTER, tzinfo=zone)
    if slot > local:
        slot = dt.datetime.combine(local.date() - dt.timedelta(days=1),
                                   PUBLISH_AFTER, tzinfo=zone)
    return slot.astimezone(dt.UTC)


def due(now: dt.datetime, meta: dict | None, checked_at: dt.datetime | None,
        attempted_at: dt.datetime | None, startup: bool) -> bool:
    """Whether to look for a new file now.

    meta         : the installed file's meta table, or None when absent
    checked_at   : last time the published hash was read successfully
    attempted_at : last time a check started, successful or not
    """
    if attempted_at is not None and now - attempted_at < RETRY_AFTER:
        return False
    if meta is None:
        return True
    if startup:
        built = _parse(meta.get("built"))
        if built is None or now - built > STARTUP_MAX_AGE:
            return True
    return checked_at is None or checked_at < last_slot(now)


def installed_meta(path: str) -> dict | None:
    """The installed file's meta table, or None when absent or unreadable.
    Read-only; judging the file is routes.py's job, not this one's."""
    if not os.path.exists(path):
        return None
    try:
        con = sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)
        try:
            return dict(con.execute("SELECT k, v FROM meta").fetchall())
        finally:
            con.close()
    except sqlite3.Error:
        return None


def _window(w) -> tuple[int, int, str, int] | None:
    """One published window, or None when it is not well-formed."""
    if not isinstance(w, (list, tuple)) or len(w) != 4:
        return None
    start, length, src, n = w
    if isinstance(start, bool) or isinstance(length, bool) or isinstance(n, bool):
        return None
    if not (isinstance(start, int) and isinstance(length, int) and isinstance(n, int)):
        return None
    if not (0 <= start <= 1439 and 1 <= length <= 1440 and src in ("s", "f") and n >= 1):
        return None
    return start, length, src, n


def _unlink(path: str) -> None:
    for suffix in ("", "-wal", "-shm", "-journal"):
        try:
            os.unlink(path + suffix)
        except OSError:
            pass


def build_artifact(blob: bytes, expected_sha: str, path: str,
                   now: dt.datetime | None = None,
                   current: dict | None = None) -> dict[str, Any]:
    """Verify a downloaded file and install it at `path`. Returns a summary.

    Raises InstallRefused, leaving whatever is at `path` untouched, when the
    hash does not match, the format is not FORMAT, the header fails a
    routes.py check, or the file is OLDER than the public one installed
    (`current`, its meta) - a CDN can serve the previous pair for a moment.
    """
    now = now or dt.datetime.now(dt.UTC)
    sha = hashlib.sha256(blob).hexdigest()
    if sha != (expected_sha or "").lower():
        raise InstallRefused("sha256 %s does not match SHA256SUMS %s" % (sha[:12], (expected_sha or "")[:12]))
    try:
        payload = json.loads(gzip.decompress(blob))
    except (OSError, ValueError) as err:
        raise InstallRefused("not gzip JSON: %s" % err) from err
    if not isinstance(payload, dict) or payload.get("format") != FORMAT:
        raise InstallRefused("format %r, expected %r" % (
            payload.get("format") if isinstance(payload, dict) else type(payload).__name__, FORMAT))
    routes = payload.get("routes")
    if not isinstance(routes, dict) or not routes:
        raise InstallRefused("no routes")
    header = {k: (None if payload.get(k) is None else str(payload.get(k)))
              for k in ("built", "expires", "ladd_applied")}
    reason = _reject(header, now)
    if reason:
        raise InstallRefused(reason)
    if current and current.get("source_sha256"):
        new_b, old_b = _parse(header["built"]), _parse(current.get("built"))
        if new_b is not None and old_b is not None and new_b < old_b:
            raise InstallRefused("older (built %s) than the installed file (built %s)"
                                 % (header["built"], current.get("built")))

    tmp = path + TMP_SUFFIX
    _unlink(tmp)
    route_rows = window_rows = malformed = 0
    times = payload.get("times") if isinstance(payload.get("times"), dict) else {}
    meta = {
        "built": header["built"], "expires": header["expires"],
        "ladd_applied": header["ladd_applied"],
        "ladd_entries": payload.get("ladd_entries"),
        "format": FORMAT,
        "attribution": payload.get("attribution"),
        "licence": payload.get("licence"),
        "source_url": RELEASE_URL + ASSET,
        "source_sha256": sha,
        "installed_at": now.replace(microsecond=0).isoformat(),
        "times_shape": times.get("shape"),
        "times_as_of": times.get("as_of"),
        "times_zones": times.get("zones"),
        "times_tbb_data": times.get("tbb_data"),
        "leg_windows": ("published windows per leg: k d|a|dw|aw, start minutes after "
                        "local midnight (d origin, a destination), len minutes, "
                        "src s|f, n flights. See the file's keys.t."),
    }
    try:
        con = sqlite3.connect(tmp)
        try:
            con.execute("CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT)")
            con.execute("CREATE TABLE routes (acid TEXT, dep TEXT, arr TEXT, n INTEGER, "
                        "user_cat TEXT, ac_cat TEXT, last_seen INTEGER)")
            con.execute("CREATE TABLE leg_windows (acid TEXT, dep TEXT, arr TEXT, k TEXT, "
                        "start INTEGER, len INTEGER, src TEXT, n INTEGER)")
            con.executemany("INSERT INTO meta VALUES (?,?)",
                            [(k, None if v is None else str(v)) for k, v in meta.items()])
            rrows, wrows = [], []
            for acid, e in routes.items():
                if not isinstance(e, dict):
                    continue
                for leg in e.get("l") or []:
                    if not isinstance(leg, dict):
                        continue
                    dep, _, arr = str(leg.get("r") or "").partition("-")
                    if not dep or not arr:
                        continue
                    rrows.append((acid, dep, arr, leg.get("n", 0), e.get("u"), e.get("a"), e.get("s")))
                    t = leg.get("t")
                    if isinstance(t, dict):
                        for k in WINDOW_KEYS:
                            if k not in t:
                                continue
                            w = _window(t[k])
                            if w is None:
                                malformed += 1
                                continue
                            wrows.append((acid, dep, arr, k) + w)
            con.executemany("INSERT INTO routes VALUES (?,?,?,?,?,?,?)", rrows)
            con.executemany("INSERT INTO leg_windows VALUES (?,?,?,?,?,?,?,?)", wrows)
            con.execute("CREATE INDEX ix_acid ON routes(acid)")
            con.execute("CREATE INDEX ix_lw_acid ON leg_windows(acid)")
            con.commit()
            route_rows, window_rows = len(rrows), len(wrows)
            # Read back before anything replaces the installed file.
            if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise InstallRefused("integrity_check failed on the new database")
            got_r = con.execute("SELECT count(*) FROM routes").fetchone()[0]
            got_w = con.execute("SELECT count(*) FROM leg_windows").fetchone()[0]
            if got_r != route_rows or got_w != window_rows or route_rows == 0:
                raise InstallRefused("read back %d/%d rows, wrote %d/%d" % (got_r, got_w, route_rows, window_rows))
            back = dict(con.execute("SELECT k, v FROM meta").fetchall())
            reason = _reject(back, now)
            if reason:
                raise InstallRefused("read back: " + reason)
        finally:
            con.close()
        os.replace(tmp, path)                     # atomic on one filesystem
    except InstallRefused:
        _unlink(tmp)
        raise
    except (sqlite3.Error, OSError) as err:
        _unlink(tmp)
        raise InstallRefused("writing the database: %s" % err) from err
    for suffix in ("-wal", "-shm", "-journal"):
        try:
            os.unlink(path + suffix)              # leftovers belong to the old file
        except OSError:
            pass
    return {"built": header["built"], "expires": header["expires"],
            "ladd_applied": header["ladd_applied"], "sha256": sha,
            "routes": route_rows, "windows": window_rows, "malformed_windows": malformed,
            "callsigns": len(routes)}


# ------------------------------------------------------- Home Assistant side

class RouteDownloader:
    """One per Home Assistant instance; every config entry's timer asks it."""

    def __init__(self, hass, on_installed) -> None:
        self._hass = hass
        self._path = hass.config.path(".storage", ARTIFACT_FILENAME)
        self._on_installed = on_installed
        self._lock = asyncio.Lock()
        self._checked_at: dt.datetime | None = None
        self._attempted_at: dt.datetime | None = None
        self._slot: dt.datetime | None = None
        self._slot_downloads = 0
        self.status = "not run"

    async def _get(self, session, name: str, cap: int) -> bytes:
        import aiohttp  # noqa: PLC0415 - HA's own dependency; kept out of the pure part

        async with session.get(RELEASE_URL + name, timeout=aiohttp.ClientTimeout(total=300),
                               headers={"User-Agent": "LiveTrackAircraft (StrausbergAutomationWorks)"}) as resp:
            if resp.status != 200:
                raise InstallRefused("%s: HTTP %d" % (name, resp.status))
            body = bytearray()
            async for chunk in resp.content.iter_chunked(1 << 16):
                body += chunk
                if len(body) > cap:
                    raise InstallRefused("%s larger than %d bytes" % (name, cap))
            return bytes(body)

    async def async_check(self, startup: bool = False) -> None:
        from .release_session import release_session  # noqa: PLC0415 - see release_session.py

        if self._lock.locked():
            return
        async with self._lock:
            hass = self._hass
            meta = await hass.async_add_executor_job(installed_meta, self._path)
            now = dt.datetime.now(dt.UTC)
            if not due(now, meta, self._checked_at, self._attempted_at, startup):
                return
            self._attempted_at = now
            session = None
            try:
                session = release_session(hass)
                sums = await self._get(session, SUMS, MAX_SUMS_BYTES)
                sha = parse_sums(sums.decode("utf-8", "replace"))
                if sha is None:
                    raise InstallRefused("SHA256SUMS names no %s" % ASSET)
                if meta and meta.get("source_sha256") == sha:
                    self._checked_at = now
                    self.status = "current (built %s, sha %s)" % ((meta.get("built") or "")[:16], sha[:8])
                    return
                slot = last_slot(now)
                if self._slot != slot:
                    self._slot, self._slot_downloads = slot, 0
                if self._slot_downloads >= MAX_DOWNLOADS_PER_SLOT:
                    self.status = "waiting: %d downloads failed for this publication" % self._slot_downloads
                    return
                self._slot_downloads += 1
                blob = await self._get(session, ASSET, MAX_BYTES)
                summary = await hass.async_add_executor_job(
                    build_artifact, blob, sha, self._path, None, meta)
            except InstallRefused as err:
                self.status = "failed: %s" % err
                _LOGGER.warning("Route download refused, installed file unchanged: %s", err)
                return
            except Exception as err:  # noqa: BLE001 - network, timeouts, disk
                self.status = "failed: %s" % (err.__class__.__name__)
                _LOGGER.warning("Route download failed, installed file unchanged: %r", err)
                return
            finally:
                if session is not None:
                    await session.close()
            self._checked_at = now
            self.status = "installed (built %s, sha %s)" % (summary["built"][:16], summary["sha256"][:8])
            _LOGGER.info("Route artifact installed from %s: %s", ASSET, summary)
            self._on_installed()
