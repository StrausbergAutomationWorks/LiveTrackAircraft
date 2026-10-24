"""Download the PUBLIC airport table and install it where airports.py reads it.

Backlog 245 (Lee, 2026-10-18): the table is published as release `data` of
StrausbergAutomationWorks/AirportZones, rebuilt weekly, ODbL v1.0. This module
is how any install gets it - this machine included. It replaces the copy placed
on the box by hand on 2026-09-22, which had no names.

! ONE FILE, ONE NAME, SHARED: .storage/saw_airport_zones.sqlite (airports.py,
AIRPORTS_FILENAME). Not named after any integration; whichever integration
needs it first fetches it, the others find it.

! FAILS CLOSED, AT EVERY STEP. Nothing reaches the shared path unless the
download's SHA-256 matches the published SHA256SUMS, it unpacks within a size
cap, SQLite's integrity check passes, `meta.format` is the one this code reads,
every column airports.py and the names need is present, the row count is at
least MIN_ROWS and equals `meta.rows`, the licence and attribution are present,
and it is not OLDER than a published file already installed. A refused download
leaves the installed file as it was. Written under a temporary name, read back,
then moved over the old file in one rename.

! HOW OFTEN. About 4.8 MB, rebuilt weekly at no fixed hour from a client's point
of view. So: at startup when absent or not a published file, then the 94-byte
SHA256SUMS once a day; the large file only when its hash differs. A failure is
retried an hour later, at most MAX_DOWNLOADS_PER_DAY large downloads a day.

No Home Assistant import at module level: the pure parts are tested offline
(tests/test_airport_download.py).
"""
from __future__ import annotations

import asyncio
import datetime as dt
import hashlib
import logging
import os
import sqlite3
import zlib
from typing import Any

from .airports import AIRPORTS_FILENAME
from .route_download import installed_meta, parse_sums

_LOGGER = logging.getLogger(__name__)

RELEASE_URL = ("https://github.com/StrausbergAutomationWorks/AirportZones"
               "/releases/download/data/")
ASSET = "saw_airport_zones.sqlite.gz"
SUMS = "SHA256SUMS"
FORMAT = "saw_airport_zones/1"

CHECK_EVERY = dt.timedelta(days=1)
RETRY_AFTER = dt.timedelta(hours=1)
MAX_DOWNLOADS_PER_DAY = 3
MAX_BYTES = 64 * 1024 * 1024          # the download is ~4.8 MB; a cap, not a size
MAX_UNPACKED = 256 * 1024 * 1024      # ~12 MB unpacked
MAX_SUMS_BYTES = 64 * 1024
MIN_ROWS = 80000                      # OurAirports held 86,258 on 2026-10-18
TICK = dt.timedelta(minutes=30)       # how often due() is asked; it gates the network
TMP_SUFFIX = ".lta-new"

ZONES_COLUMNS = {"ident", "tz", "lat", "lon", "cross_check",
                 "name", "municipality", "iata_code", "iso_country", "type"}
ALIASES_COLUMNS = {"code", "ident", "field"}
META_REQUIRED = ("format", "built", "rows", "license", "attribution")


class InstallRefused(Exception):
    """The download must not be installed. The installed file is untouched."""


def _parse(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        t = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=dt.UTC)


def due(now: dt.datetime, meta: dict | None, checked_at: dt.datetime | None,
        attempted_at: dt.datetime | None) -> bool:
    """Whether to look for a new file now.

    meta         : the installed file's meta table, or None when absent
    checked_at   : last time the published hash was read successfully
    attempted_at : last time a check started, successful or not
    """
    if attempted_at is not None and now - attempted_at < RETRY_AFTER:
        return False
    if meta is None or not meta.get("source_sha256"):
        return True                    # absent, or placed by hand rather than downloaded
    return checked_at is None or now - checked_at >= CHECK_EVERY


def _unlink(path: str) -> None:
    for suffix in ("", "-wal", "-shm", "-journal"):
        try:
            os.unlink(path + suffix)
        except OSError:
            pass


def _gunzip(blob: bytes, cap: int) -> bytes:
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        out = d.decompress(blob, cap + 1)
    except zlib.error as err:
        raise InstallRefused("not gzip: %s" % err) from err
    if len(out) > cap or d.unconsumed_tail:
        raise InstallRefused("unpacks to more than %d bytes" % cap)
    if not d.eof:
        raise InstallRefused("gzip stream truncated")
    return out


def install_table(blob: bytes, expected_sha: str, path: str,
                  now: dt.datetime | None = None, current: dict | None = None,
                  unpacked_cap: int = MAX_UNPACKED) -> dict[str, Any]:
    """Verify a downloaded table and install it at `path`. Returns a summary.

    Raises InstallRefused, leaving whatever is at `path` untouched.
    `current` is the installed file's meta (installed_meta), or None.
    """
    now = now or dt.datetime.now(dt.UTC)
    sha = hashlib.sha256(blob).hexdigest()
    if sha != (expected_sha or "").lower():
        raise InstallRefused("sha256 %s does not match SHA256SUMS %s" % (sha[:12], (expected_sha or "")[:12]))
    raw = _gunzip(blob, unpacked_cap)
    if not raw.startswith(b"SQLite format 3\x00"):
        raise InstallRefused("not an SQLite database")
    tmp = path + TMP_SUFFIX
    _unlink(tmp)
    try:
        with open(tmp, "wb") as fh:
            fh.write(raw)
        con = sqlite3.connect(tmp)
        try:
            if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise InstallRefused("integrity_check failed")
            try:
                meta = dict(con.execute("SELECT k, v FROM meta").fetchall())
            except sqlite3.Error as err:
                raise InstallRefused("no meta table: %s" % err) from err
            if meta.get("format") != FORMAT:
                raise InstallRefused("format %r, expected %r" % (meta.get("format"), FORMAT))
            missing = [k for k in META_REQUIRED if not meta.get(k)]
            if missing:
                raise InstallRefused("meta lacks %s" % ", ".join(missing))
            for table, need in (("zones", ZONES_COLUMNS), ("aliases", ALIASES_COLUMNS)):
                have = {r[1] for r in con.execute("PRAGMA table_info(%s)" % table)}
                if not need <= have:
                    raise InstallRefused("%s lacks %s" % (table, sorted(need - have)))
            rows = con.execute("SELECT COUNT(*) FROM zones").fetchone()[0]
            if rows < MIN_ROWS or str(rows) != str(meta.get("rows")):
                raise InstallRefused("zones has %d rows, meta says %s, minimum %d"
                                     % (rows, meta.get("rows"), MIN_ROWS))
            built = _parse(meta.get("built"))
            if built is None:
                raise InstallRefused("meta built %r is not a time" % meta.get("built"))
            if current and current.get("source_sha256"):
                old = _parse(current.get("built"))
                if old is not None and built < old:
                    raise InstallRefused("older (built %s) than the installed file (built %s)"
                                         % (meta.get("built"), current.get("built")))
            stamp = {"source_url": RELEASE_URL + ASSET, "source_sha256": sha,
                     "installed_at": now.replace(microsecond=0).isoformat()}
            con.executemany("INSERT OR REPLACE INTO meta VALUES (?,?)", list(stamp.items()))
            con.commit()
            back = dict(con.execute("SELECT k, v FROM meta").fetchall())
            if back.get("source_sha256") != sha or back.get("format") != FORMAT:
                raise InstallRefused("read back the meta wrong")
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
    return {"built": meta.get("built"), "rows": rows, "sha256": sha}


# ------------------------------------------------------- Home Assistant side

class AirportDownloader:
    """One per Home Assistant instance; every config entry's timer asks it."""

    def __init__(self, hass, on_installed) -> None:
        self._hass = hass
        self._path = hass.config.path(".storage", AIRPORTS_FILENAME)
        self._on_installed = on_installed
        self._lock = asyncio.Lock()
        self._checked_at: dt.datetime | None = None
        self._attempted_at: dt.datetime | None = None
        self._day: dt.date | None = None
        self._day_downloads = 0
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

    async def async_check(self) -> None:
        from .release_session import release_session  # noqa: PLC0415 - see release_session.py

        if self._lock.locked():
            return
        async with self._lock:
            hass = self._hass
            meta = await hass.async_add_executor_job(installed_meta, self._path)
            now = dt.datetime.now(dt.UTC)
            if not due(now, meta, self._checked_at, self._attempted_at):
                return
            self._attempted_at = now
            session = None
            try:
                session = release_session(hass)
                sums = await self._get(session, SUMS, MAX_SUMS_BYTES)
                sha = parse_sums(sums.decode("utf-8", "replace"), ASSET)
                if sha is None:
                    raise InstallRefused("SHA256SUMS names no %s" % ASSET)
                if meta and meta.get("source_sha256") == sha:
                    self._checked_at = now
                    self.status = "current (built %s, sha %s)" % ((meta.get("built") or "")[:16], sha[:8])
                    return
                if self._day != now.date():
                    self._day, self._day_downloads = now.date(), 0
                if self._day_downloads >= MAX_DOWNLOADS_PER_DAY:
                    self.status = "waiting: %d downloads failed today" % self._day_downloads
                    return
                self._day_downloads += 1
                blob = await self._get(session, ASSET, MAX_BYTES)
                summary = await hass.async_add_executor_job(
                    install_table, blob, sha, self._path, None, meta)
            except InstallRefused as err:
                self.status = "failed: %s" % err
                _LOGGER.warning("Airport table download refused, installed file unchanged: %s", err)
                return
            except Exception as err:  # noqa: BLE001 - network, timeouts, disk
                self.status = "failed: %s" % (err.__class__.__name__)
                _LOGGER.warning("Airport table download failed, installed file unchanged: %r", err)
                return
            finally:
                if session is not None:
                    await session.close()
            self._checked_at = now
            self.status = "installed (built %s, sha %s)" % ((summary["built"] or "")[:16], summary["sha256"][:8])
            _LOGGER.info("Airport table installed from %s: %s", ASSET, summary)
            self._on_installed()
