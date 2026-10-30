"""airlines.airline_short: the hover's first line for a commercial flight (Lee 2026-10-29 14:14, 14:24).

"United 1678", not "UAL1678": the integration publishes `airline_short`, the card composes it with the flight number
(06_MAP_CONTRACT.md D4b). A single-brand regional is its brand, a multi-brand regional (SkyWest, Republic) its
operator; RCH and CAP are not commercial and keep their callsign.
"""
import os
import unittest

from _load import COMP, load

airlines = load("airlines")


class Tables(unittest.TestCase):
    def test_every_designator_has_a_short_name_but_the_non_commercial(self):
        self.assertEqual(set(airlines._OPERATORS) - set(airlines._SHORT), {"RCH", "CAP"})

    def test_no_short_name_without_an_operator(self):
        self.assertEqual(set(airlines._SHORT) - set(airlines._OPERATORS), set())

    def test_short_names_fit(self):
        for code, short in airlines._SHORT.items():
            self.assertTrue(0 < len(short) <= 22 and short == short.strip(), (code, short))


class Lookup(unittest.TestCase):
    def test_mainline(self):
        self.assertEqual(airlines.airline_short("UAL1678"), "United")
        self.assertEqual(airlines.airline_short("AAL861"), "American")
        self.assertEqual(airlines.airline_short("DAL1519"), "Delta")

    def test_single_brand_regionals_are_their_brand(self):
        for cs, brand in (("ENY3548", "American Eagle"), ("JIA5123", "American Eagle"), ("PDT4400", "American Eagle"),
                          ("EDV5335", "Delta Connection"), ("GJS4513", "United Express"), ("ASH6012", "United Express"),
                          ("UCA4801", "United Express"), ("QXE2201", "Alaska Horizon")):
            self.assertEqual(airlines.airline_short(cs), brand, cs)

    def test_multi_brand_regionals_are_the_operator(self):
        self.assertEqual(airlines.airline_short("SKW5500"), "SkyWest")
        self.assertEqual(airlines.airline_short("SKW476L"), "SkyWest")
        self.assertEqual(airlines.airline_short("RPA3406"), "Republic")

    def test_letters_after_the_number(self):
        self.assertEqual(airlines.airline_short("BAW2PD"), "British Airways")
        self.assertEqual(airlines.airline_short(" ual1678 "), "United")

    def test_not_an_airline_flight(self):
        for cs in (None, "", "UAL", "UALX", "UAL12345", "N123AB", "N959BP", "COL120", "TROY329", "VELUX55",
                   "TYSON51", "RCH123", "CAP2541", "IDT84A"):
            self.assertIsNone(airlines.airline_short(cs), cs)


class Wiring(unittest.TestCase):
    def src(self, name):
        with open(os.path.join(COMP, name), encoding="utf-8") as fh:
            return fh.read()

    def test_published(self):
        coord = self.src("coordinator.py")
        self.assertIn('short_name = airline_short(obs.callsign)', coord)
        self.assertIn('out["airline_short"] = short_name', coord)
        self.assertIn('"airline_short",', self.src("geo_location.py"))

    def test_a_charter_says_so_in_the_hover(self):
        coord = self.src("coordinator.py")
        start = coord.index("elif listed_status == CHARTER:")
        block = coord[start:coord.index('out["entity_picture"]', start)]
        self.assertIn('out["operator_short"] = CHARTER_FLIGHT_LABEL if flight is not None else CHARTER_LABEL', block)


if __name__ == "__main__":
    unittest.main()
