"""The government table: every government registrant, every type, no drones."""
import csv
import io
import os
import sys
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(__file__))
from _load import load  # noqa: E402

reg = load("registrations")

REF_COLS = ["CODE", "MFR", "MODEL", "TYPE-ACFT", "NO-SEATS"]
MASTER_COLS = ["N-NUMBER", "MFR MDL CODE", "TYPE REGISTRANT", "NAME", "STATE",
               "MODE S CODE HEX", "STATUS CODE"]


def _csv(cols, rows):
    s = io.StringIO()
    w = csv.writer(s)
    w.writerow(cols)
    w.writerows(rows)
    return ("\ufeff" + s.getvalue()).encode("utf-8")


def archive(ref, master):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("ACFTREF.txt", _csv(REF_COLS, ref))
        z.writestr("MASTER.txt", _csv(MASTER_COLS, master))
    return b.getvalue()


REF = [
    ["FW4", "CESSNA", "206H", "4", "6"],
    ["HEL", "BELL", "407", "6", "7"],
    ["MQ9", "GENERAL ATOMICS", "MQ-9 BLOCK 1", "4", "0"],
    ["DJ2", "DJI", "IMAGINARY TWO-SEAT", "6", "2"],
    ["ER2", "LOCKHEED", "ER-2", "4", "1"],
    ["UNK", "ACME", "NO SEAT COUNT", "4", ""],
]
MASTER = [
    ["101PD", "FW4", "5", "CITY OF EXAMPLE POLICE DEPT", "IL", "A00001", "V"],
    ["202SO", "HEL", "5", "EXAMPLE COUNTY SHERIFF", "IL", "A00002", "V"],
    ["303CB", "MQ9", "5", "U S CUSTOMS AND BORDER PROTECTION", "AZ", "A00003", "V"],
    ["404DJ", "DJ2", "5", "EXAMPLE STATE UNIVERSITY", "OK", "A00004", "V"],
    ["505NA", "ER2", "5", "NASA", "CA", "A00005", "V"],
    ["606PV", "FW4", "1", "PRIVATE PERSON", "IL", "A00006", "V"],
    ["707CB", "HEL", "7", "CBP AIR LOGISTICS LLC", "TX", "A00007", "V"],
    ["808UK", "UNK", "5", "EXAMPLE CITY", "IL", "A00008", "V"],
]


class Table(unittest.TestCase):
    def setUp(self):
        self.t = reg.parse_faa_archive(archive(REF, MASTER))

    def test_every_type_kept(self):
        self.assertEqual(self.t["A00001"], ["N101PD", "CITY OF EXAMPLE POLICE DEPT", "IL"])
        self.assertIn("A00002", self.t)            # rotorcraft
        self.assertIn("A00005", self.t)            # one seat is an aircraft

    def test_drones_out(self):
        self.assertNotIn("A00003", self.t)         # 0 seats
        self.assertNotIn("A00004", self.t)         # a drone maker

    def test_registrant(self):
        self.assertNotIn("A00006", self.t)         # an individual
        self.assertIn("A00007", self.t)            # the federal allowlist

    def test_unknown_seats_kept(self):
        self.assertIn("A00008", self.t)

    def test_exactly(self):
        self.assertEqual(sorted(self.t), ["A00001", "A00002", "A00005", "A00007", "A00008"])


class Names(unittest.TestCase):
    class _Hass:
        class config:
            @staticmethod
            def path(*p):
                return "/".join(p)

    def test_paths(self):
        h = self._Hass()
        self.assertEqual(reg.cache_path(h), ".storage/saw_faa_gov_aircraft.json")
        self.assertEqual(reg.legacy_cache_path(h), ".storage/saw_faa_gov_rotorcraft.json")
        self.assertEqual(reg.SCHEMA, 2)


if __name__ == "__main__":
    unittest.main()
