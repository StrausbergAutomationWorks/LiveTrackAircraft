"""The public route file's downloader and installer (route_download.py) and
the reader of its time windows (routes.RouteStore.leg_times), 2026-10-13.
Offline: synthetic files, a temporary .storage, no network, no HA."""
import datetime as dt
import gzip
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
import types
import unittest

from _load import load

# ! THE LADD DATE IS RELATIVE TO TODAY (2026-10-29). routes.py refuses an artifact whose LADD list is over
# MAX_LADD_AGE_DAYS old by the REAL clock; a fixed 2026-10-13 began failing three Reader tests on 2026-10-28. The
# list is applied every Tuesday and the old file replaced (Lee 2026-10-29), so a real one is at most a week old.
# ! Only the Reader tests read by the real clock; install() judges by the fixed NOW below, where a FRESH_LADD after
# NOW is accepted (measured: those tests pass) and the refusal case keeps a date 16 days before NOW.
_TODAY = dt.datetime.now(dt.UTC).date()
FRESH_LADD = (_TODAY - dt.timedelta(days=2)).isoformat()

rd = load("route_download")
routes = load("routes")

NOW = dt.datetime(2026, 10, 14, 2, 0, tzinfo=dt.UTC)        # 21:00 CDT on the 13th


def payload(**over):
    p = {
        "format": "filedroutesdb/1",
        "built": "2026-10-14T01:13:02+00:00",
        "expires": "2036-10-24T01:13:02+00:00",   # far out: a real date expires
        "ladd_applied": FRESH_LADD,
        "ladd_entries": 74022,
        "attribution": "Derived from data obtained through the FAA SWIM Cloud Distribution Service.",
        "licence": "CC-BY-4.0",
        "times": {"shape": "times-1", "as_of": "2026-10-14T01:13:02+00:00",
                  "zones": "saw_livetrack.zones.zone_at", "tbb_data": "2026d"},
        "routes": {
            "AAL1": {"u": "COMMERCIAL", "a": "JET", "s": 1791940000, "l": [
                {"r": "KORD-KLAX", "n": 12, "t": {"d": [600, 45, "s", 7], "a": [780, 50, "s", 7],
                                                 "dw": [420, 45, "f", 2]}},
                {"r": "KLAX-KORD", "n": 11}]},
            "N123AB": {"u": "GA", "a": "PISTON", "s": 1791940000, "l": [{"r": "KDPA-KDPA", "n": 3}]},
        },
    }
    p.update(over)
    return p


def blob(p):
    return gzip.compress(json.dumps(p).encode())


class Storage(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.dir, ".storage"))
        self.hass = types.SimpleNamespace(config=types.SimpleNamespace(
            path=lambda *p: os.path.join(self.dir, *p)))
        self.path = os.path.join(self.dir, ".storage", routes.ARTIFACT_FILENAME)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def install(self, p, sha=None, current=None, now=NOW):
        b = blob(p)
        return rd.build_artifact(b, sha or hashlib.sha256(b).hexdigest(), self.path, now, current)

    def tables(self):
        con = sqlite3.connect(self.path)
        try:
            return {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        finally:
            con.close()

    def refused(self, p, sha=None, current=None):
        with open(self.path, "wb") as fh:
            fh.write(b"OLD FILE")
        with self.assertRaises(rd.InstallRefused):
            self.install(p, sha, current)
        with open(self.path, "rb") as fh:
            self.assertEqual(fh.read(), b"OLD FILE")       # untouched
        self.assertFalse(os.path.exists(self.path + rd.TMP_SUFFIX))


class Install(Storage):
    def test_good_file_installs(self):
        s = self.install(payload())
        self.assertEqual((s["routes"], s["windows"], s["malformed_windows"], s["callsigns"]), (3, 3, 0, 2))
        self.assertEqual(self.tables(), {"meta", "routes", "leg_windows"})   # no owners
        meta = rd.installed_meta(self.path)
        self.assertEqual(meta["format"], "filedroutesdb/1")
        self.assertEqual(meta["ladd_applied"], FRESH_LADD)
        self.assertEqual(meta["source_sha256"], s["sha256"])
        self.assertFalse(os.path.exists(self.path + rd.TMP_SUFFIX))

    def test_replaces_an_existing_file(self):
        with open(self.path, "wb") as fh:
            fh.write(b"stopgap")
        self.install(payload())
        self.assertEqual(rd.installed_meta(self.path)["format"], "filedroutesdb/1")

    def test_hash_mismatch_refused(self):
        self.refused(payload(), sha="0" * 64)

    def test_wrong_format_refused(self):
        self.refused(payload(format="filedroutesdb/2"))

    def test_null_ladd_refused(self):
        self.refused(payload(ladd_applied=None))

    def test_expired_refused(self):
        self.refused(payload(expires="2026-10-14T01:00:00+00:00"))

    def test_old_ladd_list_refused(self):
        self.refused(payload(ladd_applied="2026-09-28"))           # 16 days before NOW: install() judges by NOW

    def test_no_routes_refused(self):
        self.refused(payload(routes={}))

    def test_not_gzip_refused(self):
        with self.assertRaises(rd.InstallRefused):
            rd.build_artifact(b"not gzip", hashlib.sha256(b"not gzip").hexdigest(), self.path, NOW)

    def test_older_than_the_installed_public_file_refused(self):
        cur = {"source_sha256": "a" * 64, "built": "2026-10-14T02:00:00+00:00"}
        self.refused(payload(), current=cur)

    def test_older_than_a_local_file_installs(self):
        cur = {"built": "2026-10-14T02:00:00+00:00"}                # stopgap: no source_sha256
        self.install(payload(), current=cur)

    def test_malformed_windows_skipped_and_counted(self):
        p = payload()
        p["routes"]["AAL1"]["l"][0]["t"] = {"d": [600, 0, "s", 7], "a": [780, 50, "x", 7],
                                            "dw": [420, 45, "s", 2], "aw": [True, 5, "s", 1]}
        s = self.install(p)
        self.assertEqual((s["windows"], s["malformed_windows"]), (1, 3))


class Reader(Storage):
    def test_leg_times_reads_the_windows(self):
        self.install(payload())
        store = routes.RouteStore(self.hass)
        got = store.leg_times("aal1 ")
        self.assertEqual(got, {("KORD", "KLAX"): {"d": [600, 45, "s", 7], "a": [780, 50, "s", 7],
                                                  "dw": [420, 45, "f", 2]}})
        self.assertEqual([l[:2] for l in store.legs("AAL1")], [("KORD", "KLAX"), ("KLAX", "KORD")])
        self.assertTrue(store.status.startswith("ok (public"))
        store.close()

    def test_standin_only_file_gives_no_times(self):
        con = sqlite3.connect(self.path)
        con.execute("CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT)")
        con.executemany("INSERT INTO meta VALUES (?,?)", [("built", "2026-10-13T18:33:27+00:00"),
                        ("expires", "2036-10-23T18:33:27+00:00"), ("ladd_applied", FRESH_LADD)])
        con.execute("CREATE TABLE routes (acid TEXT, dep TEXT, arr TEXT, n INTEGER, user_cat TEXT, "
                    "ac_cat TEXT, last_seen INTEGER)")
        con.execute("INSERT INTO routes VALUES ('AAL1','KORD','KLAX',3,'COMMERCIAL','JET',1)")
        con.execute("CREATE TABLE leg_times (acid TEXT, dep TEXT, arr TEXT, dep_min INTEGER, "
                    "dep_spread_min INTEGER, arr_min INTEGER, arr_basis TEXT, flights INTEGER)")
        con.execute("INSERT INTO leg_times VALUES ('AAL1','KORD','KLAX',600,5,780,'x',3)")
        con.commit()
        con.close()
        store = routes.RouteStore(self.hass)
        self.assertEqual(store.leg_times("AAL1"), {})
        self.assertEqual(len(store.legs("AAL1")), 1)
        self.assertTrue(store.status.startswith("ok (local"))
        store.close()

    def test_reopen_sees_a_replaced_file(self):
        self.install(payload())
        store = routes.RouteStore(self.hass)
        self.assertEqual(len(store.legs("AAL1")), 2)
        p = payload(built="2026-10-14T01:30:00+00:00")
        p["routes"]["AAL1"]["l"] = p["routes"]["AAL1"]["l"][:1]
        # reopen() must let go of the open file: on HA's Linux the old one
        # would otherwise be read for up to an hour (and Windows, where this
        # test runs, cannot replace an open file at all).
        store.reopen()
        self.assertIsNone(store._con)
        self.install(p)
        self.assertEqual(len(store.legs("AAL1")), 1)
        store.close()


class Zones(Storage):
    def test_zone_comes_from_the_coordinates_not_the_table(self):
        # The builder calls saw_livetrack.zones.zone_at; so does the client.
        airports = load("airports")
        con = sqlite3.connect(os.path.join(self.dir, ".storage", airports.AIRPORTS_FILENAME))
        con.execute("CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT)")
        con.execute("CREATE TABLE zones (ident TEXT PRIMARY KEY, tz TEXT, lat REAL, lon REAL, cross_check TEXT)")
        con.execute("INSERT INTO zones VALUES ('KORD', 'Europe/Paris', 41.9786, -87.9048, NULL)")
        con.commit()
        con.close()
        store = airports.AirportStore(self.hass)
        self.assertEqual(store.lookup("KORD")["tz"], "America/Chicago")
        store.close()


class Schedule(unittest.TestCase):
    def test_parse_sums(self):
        h = "1e24d8a083cd0802cc7a42b651c55be53ac298612cd607a82ed6b43138a458e3"
        self.assertEqual(rd.parse_sums(h + "  filedroutesdb.json.gz\r\n"), h)
        self.assertEqual(rd.parse_sums(h.upper() + " *filedroutesdb.json.gz"), h)
        self.assertIsNone(rd.parse_sums(h + "  other.gz"))
        self.assertIsNone(rd.parse_sums("abc  filedroutesdb.json.gz"))
        self.assertIsNone(rd.parse_sums(""))

    def test_slot_is_14_00_chicago_through_daylight_saving(self):
        U = dt.UTC
        self.assertEqual(rd.last_slot(dt.datetime(2026, 10, 13, 20, 0, tzinfo=U)),
                         dt.datetime(2026, 10, 13, 19, 0, tzinfo=U))          # CDT
        self.assertEqual(rd.last_slot(dt.datetime(2026, 10, 13, 18, 59, tzinfo=U)),
                         dt.datetime(2026, 10, 12, 19, 0, tzinfo=U))
        self.assertEqual(rd.last_slot(dt.datetime(2026, 12, 1, 21, 0, tzinfo=U)),
                         dt.datetime(2026, 12, 1, 20, 0, tzinfo=U))           # CST
        self.assertEqual(rd.last_slot(dt.datetime(2026, 11, 1, 20, 0, tzinfo=U)),
                         dt.datetime(2026, 11, 1, 20, 0, tzinfo=U))           # change day

    def test_due(self):
        built_recent = {"built": "2026-10-13T18:33:27+00:00"}
        built_old = {"built": "2026-10-12T18:33:27+00:00"}
        slot = rd.last_slot(NOW)
        self.assertTrue(rd.due(NOW, None, None, None, False))                   # absent
        self.assertFalse(rd.due(NOW, None, None, NOW - dt.timedelta(minutes=30), False))  # retry wait
        self.assertTrue(rd.due(NOW, built_old, slot + dt.timedelta(minutes=5), None, True))   # startup, old
        self.assertFalse(rd.due(NOW, built_recent, slot + dt.timedelta(minutes=5), None, True))
        self.assertTrue(rd.due(NOW, built_recent, None, None, False))           # never checked
        self.assertTrue(rd.due(NOW, built_recent, slot - dt.timedelta(minutes=1), None, False))
        self.assertFalse(rd.due(NOW, built_recent, slot, None, False))          # checked this slot
        self.assertFalse(rd.due(NOW, built_old, slot, None, False))             # age only at startup


class Wiring(unittest.TestCase):
    def test_manifest_requires_tzfpy_by_name(self):
        # Home Assistant's is_installed() ignores extras (measured 2026-10-13):
        # saw-livetrack is already present for the rail integrations, so
        # "saw-livetrack[zones]" alone would never install tzfpy.
        from _load import source
        req = json.loads(source("manifest.json"))["requirements"]
        self.assertIn("tzfpy==2.1.0", req)
        self.assertTrue(any(r.startswith("saw-livetrack[zones]") for r in req))

    def test_release_url(self):
        self.assertEqual(rd.RELEASE_URL + rd.ASSET,
                         "https://github.com/StrausbergAutomationWorks/FiledRoutesDB/releases/download/data/filedroutesdb.json.gz")


if __name__ == "__main__":
    unittest.main()
