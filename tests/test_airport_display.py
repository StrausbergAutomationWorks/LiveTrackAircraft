"""airport_display.py, and airports.py's name column (2026-10-19)."""
import os
import sqlite3
import tempfile
import unittest

from _load import load

disp = load("airport_display")
airports = load("airports")

PBI_NAME = "Palm Beach International Airport"
TABLE_NAME = "President Donald J. Trump International Airport"


class ShownCode(unittest.TestCase):
    def test_substituted(self):
        self.assertEqual(disp.shown_code("KDJT"), "KPBI")
        self.assertEqual(disp.shown_code("DJT"), "PBI")
        self.assertEqual(disp.shown_code(" kdjt "), "KPBI")

    def test_others_unchanged(self):
        for code in ("KPBI", "PBI", "KORD", "EFHK", "KDJ", "DJTX"):
            self.assertEqual(disp.shown_code(code), code)
        self.assertIsNone(disp.shown_code(None))
        self.assertEqual(disp.shown_code(""), "")


class ShownName(unittest.TestCase):
    def test_by_ident_and_by_code(self):
        self.assertEqual(disp.shown_name("KDJT", "KPBI", TABLE_NAME), PBI_NAME)
        self.assertEqual(disp.shown_name("KPBI", "KPBI", TABLE_NAME), PBI_NAME)
        self.assertEqual(disp.shown_name("DJT", "KPBI", TABLE_NAME), PBI_NAME)
        self.assertEqual(disp.shown_name("KDJT", "KDJT", TABLE_NAME), PBI_NAME)   # table moves its ident
        self.assertEqual(disp.shown_name("KDJT", None, None), PBI_NAME)           # table lacks it
        self.assertEqual(disp.shown_name("DJT", None, None), PBI_NAME)            # FAA three-letter form
        self.assertEqual(disp.shown_name("PBI", None, None), PBI_NAME)

    def test_others_from_the_table(self):
        self.assertEqual(disp.shown_name("KORD", "KORD", "Chicago O'Hare International Airport"),
                         "Chicago O'Hare International Airport")
        self.assertIsNone(disp.shown_name("KORD", "KORD", None))
        self.assertIsNone(disp.shown_name("KORD", "KORD", "  "))
        self.assertIsNone(disp.shown_name("XXXX", None, None))


class FakeHass:
    def __init__(self, root):
        self.config = self

        def path(*parts):
            return os.path.join(root, *parts)
        self.path = path


def make_table(root, names=True):
    os.makedirs(os.path.join(root, ".storage"), exist_ok=True)
    con = sqlite3.connect(os.path.join(root, ".storage", airports.AIRPORTS_FILENAME))
    con.execute("CREATE TABLE meta (k TEXT, v TEXT)")
    con.execute("INSERT INTO meta VALUES ('built', '2026-10-19T04:03:20Z'), ('rows', '2')")
    if names:
        con.execute("CREATE TABLE zones (ident TEXT, tz TEXT, lat REAL, lon REAL, cross_check TEXT, name TEXT)")
        con.executemany("INSERT INTO zones VALUES (?,?,?,?,?,?)",
                        [("KPBI", "America/New_York", 26.683, -80.096, "same_name", TABLE_NAME),
                         ("KORD", "America/Chicago", 41.977, -87.905, "same_name", "Chicago O'Hare International Airport")])
    else:
        con.execute("CREATE TABLE zones (ident TEXT, tz TEXT, lat REAL, lon REAL, cross_check TEXT)")
        con.executemany("INSERT INTO zones VALUES (?,?,?,?,?)",
                        [("KPBI", "America/New_York", 26.683, -80.096, "same_name"),
                         ("KORD", "America/Chicago", 41.977, -87.905, "same_name")])
    con.execute("CREATE TABLE aliases (code TEXT, ident TEXT, field TEXT)")
    con.executemany("INSERT INTO aliases VALUES (?,?,?)",
                    [("KDJT", "KPBI", "icao_code"), ("DJT", "KPBI", "local_code")])
    con.commit()
    con.close()


class StoreNames(unittest.TestCase):
    def store(self, names):
        tmp = tempfile.mkdtemp()
        make_table(tmp, names)
        s = airports.AirportStore(FakeHass(tmp))
        self.addCleanup(s.close)
        return s

    def test_name_and_alias(self):
        s = self.store(True)
        got = s.lookup("KDJT")
        self.assertEqual((got["ident"], got["name"]), ("KPBI", TABLE_NAME))
        self.assertAlmostEqual(got["lat"], 26.683)
        self.assertEqual(s.lookup("KORD")["name"], "Chicago O'Hare International Airport")
        self.assertEqual(disp.shown_name("KDJT", got["ident"], got["name"]), PBI_NAME)

    def test_table_without_names_still_resolves(self):
        s = self.store(False)
        got = s.lookup("KDJT")
        self.assertEqual(got["ident"], "KPBI")
        self.assertIsNone(got["name"])
        self.assertAlmostEqual(got["lon"], -80.096)
        self.assertIsNone(disp.shown_name("KORD", "KORD", s.lookup("KORD")["name"]))


if __name__ == "__main__":
    unittest.main()
