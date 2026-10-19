"""Downloading the public airport table (airport_download.py, backlog 245, Lee 2026-10-18):
what is installed, what is refused, and that a refusal leaves the installed file untouched."""
import datetime as dt
import gzip
import hashlib
import os
import sqlite3
import tempfile
import unittest

from _load import load

ad = load("airport_download")
NOW = dt.datetime(2026, 10, 19, 12, 0, tzinfo=dt.UTC)
N = ad.MIN_ROWS


def table(path, *, fmt=ad.FORMAT, rows=N, meta_rows=None, built="2026-10-19T04:03:20+00:00",
          drop_meta=(), zones_cols=None, aliases=True):
    """A table in the published shape, broken in exactly one way when asked."""
    cols = zones_cols or ["ident", "tz", "lat", "lon", "cross_check",
                          "name", "municipality", "iata_code", "iso_country", "type"]
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT)")
    con.execute("CREATE TABLE zones (%s)" % ", ".join(cols))
    if aliases:
        con.execute("CREATE TABLE aliases (code, ident, field)")
        con.execute("INSERT INTO aliases VALUES ('ORD', 'KORD', 'iata_code')")
    con.executemany("INSERT INTO zones VALUES (%s)" % ",".join("?" * len(cols)),
                    [tuple(("K%05d" % i) if c == "ident" else "x" for c in cols) for i in range(rows)])
    meta = {"format": fmt, "built": built, "rows": str(rows if meta_rows is None else meta_rows),
            "license": "ODbL v1.0", "attribution": "Timezone Boundary Builder ... OurAirports"}
    for k in drop_meta:
        meta.pop(k)
    con.executemany("INSERT INTO meta VALUES (?,?)", meta.items())
    con.commit()
    con.close()


def packed(**kw):
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "t.sqlite")
        table(p, **kw)
        blob = gzip.compress(open(p, "rb").read())
    return blob, hashlib.sha256(blob).hexdigest()


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good, cls.good_sha = packed()

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.td.name, "saw_airport_zones.sqlite")

    def tearDown(self):
        self.td.cleanup()

    def put_old(self, **meta):
        """An installed file to protect: the hand-placed stopgap shape by default."""
        con = sqlite3.connect(self.path)
        con.execute("CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT)")
        con.executemany("INSERT INTO meta VALUES (?,?)", (meta or {"built": "2026-09-23T02:26:40+00:00"}).items())
        con.commit()
        con.close()
        return open(self.path, "rb").read()

    def refused(self, blob, sha, current=None, **kw):
        before = open(self.path, "rb").read() if os.path.exists(self.path) else None
        with self.assertRaises(ad.InstallRefused):
            ad.install_table(blob, sha, self.path, NOW, current, **kw)
        after = open(self.path, "rb").read() if os.path.exists(self.path) else None
        self.assertEqual(after, before, "a refusal changed the installed file")
        self.assertFalse(os.path.exists(self.path + ad.TMP_SUFFIX), "temporary file left behind")


class Installs(Base):
    def test_good_table_is_installed_over_the_stopgap(self):
        self.put_old()
        s = ad.install_table(self.good, self.good_sha, self.path, NOW, ad.installed_meta(self.path))
        self.assertEqual(s["rows"], N)
        m = ad.installed_meta(self.path)
        self.assertEqual(m["source_sha256"], self.good_sha)
        self.assertEqual(m["format"], ad.FORMAT)
        self.assertEqual(m["source_url"], ad.RELEASE_URL + ad.ASSET)
        self.assertEqual(m["installed_at"], "2026-10-19T12:00:00+00:00")
        self.assertFalse(os.path.exists(self.path + ad.TMP_SUFFIX))

    def test_installed_table_is_readable_by_the_reader_query(self):
        ad.install_table(self.good, self.good_sha, self.path, NOW)
        con = sqlite3.connect(self.path)
        self.assertEqual(con.execute("SELECT ident, tz, lat, lon FROM zones WHERE ident='K00001'").fetchone()[0], "K00001")
        con.close()

    def test_newer_build_replaces_an_older_published_one(self):
        old, old_sha = packed(built="2026-10-12T04:00:00+00:00")
        ad.install_table(old, old_sha, self.path, NOW)
        ad.install_table(self.good, self.good_sha, self.path, NOW, ad.installed_meta(self.path))
        self.assertEqual(ad.installed_meta(self.path)["source_sha256"], self.good_sha)

    def test_sha_is_compared_case_insensitively(self):
        ad.install_table(self.good, self.good_sha.upper(), self.path, NOW)


class Refuses(Base):
    def test_hash_mismatch(self):
        self.put_old()
        self.refused(self.good, "0" * 64)

    def test_not_gzip(self):
        self.put_old()
        blob = b"not gzip at all"
        self.refused(blob, hashlib.sha256(blob).hexdigest())

    def test_gzip_but_not_sqlite(self):
        blob = gzip.compress(b"x" * 1000)
        self.refused(blob, hashlib.sha256(blob).hexdigest())

    def test_unpacks_past_the_cap(self):
        self.refused(self.good, self.good_sha, unpacked_cap=4096)

    def test_wrong_format(self):
        self.refused(*packed(fmt="saw_airport_zones/2"))

    def test_missing_meta_keys(self):
        for k in ("attribution", "license", "built", "rows"):
            with self.subTest(k=k):
                self.refused(*packed(drop_meta=(k,)))

    def test_missing_name_column(self):
        cols = ["ident", "tz", "lat", "lon", "cross_check", "municipality", "iata_code", "iso_country", "type"]
        self.refused(*packed(zones_cols=cols))

    def test_missing_aliases_table(self):
        self.refused(*packed(aliases=False))

    def test_too_few_rows(self):
        self.refused(*packed(rows=N - 1))

    def test_row_count_disagrees_with_meta(self):
        self.refused(*packed(meta_rows=N + 5))

    def test_built_is_not_a_time(self):
        self.refused(*packed(built="last tuesday"))

    def test_older_than_the_installed_published_file(self):
        ad.install_table(self.good, self.good_sha, self.path, NOW)
        older, osha = packed(built="2026-10-12T04:00:00+00:00")
        self.refused(older, osha, current=ad.installed_meta(self.path))

    def test_stopgap_is_not_protected_by_its_build_date(self):
        # The hand-placed file has no source_sha256, so an older-looking date does not block it.
        self.put_old(built="2027-01-01T00:00:00+00:00")
        ad.install_table(self.good, self.good_sha, self.path, NOW, ad.installed_meta(self.path))


class Due(unittest.TestCase):
    PUB = {"source_sha256": "a" * 64, "built": "2026-10-19T04:03:20+00:00"}

    def test_absent_is_due(self):
        self.assertTrue(ad.due(NOW, None, None, None))

    def test_hand_placed_file_is_due(self):
        self.assertTrue(ad.due(NOW, {"built": "2026-09-23T02:26:40+00:00"}, NOW, None))

    def test_published_file_checked_today_is_not_due(self):
        self.assertFalse(ad.due(NOW, self.PUB, NOW - dt.timedelta(hours=23), None))

    def test_published_file_checked_a_day_ago_is_due(self):
        self.assertTrue(ad.due(NOW, self.PUB, NOW - dt.timedelta(days=1), None))

    def test_never_checked_is_due(self):
        self.assertTrue(ad.due(NOW, self.PUB, None, None))

    def test_retry_waits_an_hour(self):
        self.assertFalse(ad.due(NOW, None, None, NOW - dt.timedelta(minutes=59)))
        self.assertTrue(ad.due(NOW, None, None, NOW - dt.timedelta(minutes=61)))


class Constants(unittest.TestCase):
    def test_points_at_the_public_release(self):
        self.assertEqual(ad.RELEASE_URL + ad.ASSET,
                         "https://github.com/StrausbergAutomationWorks/AirportZones/releases/download/data/saw_airport_zones.sqlite.gz")
        self.assertEqual(ad.FORMAT, "saw_airport_zones/1")

    def test_same_shared_filename_as_the_reader(self):
        self.assertEqual(load("airports").AIRPORTS_FILENAME, "saw_airport_zones.sqlite")

    def test_sums_line_parses(self):
        line = "%s  %s\n" % ("3e3d2d98" + "0" * 56, ad.ASSET)
        self.assertEqual(ad.parse_sums(line, ad.ASSET), "3e3d2d98" + "0" * 56)
        self.assertIsNone(ad.parse_sums(line, "filedroutesdb.json.gz"))


if __name__ == "__main__":
    unittest.main()
