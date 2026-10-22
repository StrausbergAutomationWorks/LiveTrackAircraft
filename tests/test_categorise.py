"""The operator categoriser, by word (2026-10-21). Law enforcement draws police
lights on the map, so a false hit is visible. Cases are real owner names from
the government table (bin\\lta_categorise_compare.txt)."""
import unittest

from _load import load

reg = load("registrations")
FED, LAW, FIRE, MIL, NAT, GOV, RES = ("Federal law enforcement", "Law enforcement", "Fire / EMS",
                                      "Military", "Natural resources", "Government", "Research / academic")
CASES = [
    ("DEPARTMENT OF HOMELAND SECURITY", FED), ("US DEPARTMENT OF HOMELAND SECURITY", FED),
    ("DEPT OF HOMELAND SECURITY", FED), ("DEPARMENT OF HOMELAND SECURITY", FED),
    ("UNITED STATES CUSTOMS AND BORDER PROTECTION", FED), ("US CUSTOMS & BORDER PROTECTION", FED),
    ("CBP AIR LOGISTICS LLC", FED), ("HOMELAND AVIATION LLC", FED),
    ("U S MARSHALS SERVICE", FED), ("U S MARSHALL SERV JUSTICE & ALIEN TRANS SYS(JPATS)", FED),
    ("US DEPARTMENT OF JUSTICE", FED), ("UNITED STATES COAST GUARD", "Coast Guard"),
    ("CALIFORNIA HIGHWAY PATROL", LAW), ("ORANGE COUNTY SHERIFFS OFFICE", LAW),
    ("MIAMI-DADE SHERIFF'S OFFICE", LAW), ("CHARLOTTE COUNTY SHERRIFS DEPARTMENT", LAW),
    ("SAN DIEGO COUNTY SHERRIFFS DEPARTMENT", LAW), ("LAPD AIR SUPPORT DIVISION", LAW),
    ("TEXAS DEPARTMENT OF PUBLIC SAFETY", LAW), ("ILLINOIS STATE POLICE", LAW),
    ("TENNESSEE DEPARTMENT OF SAFETY & HOMELAND SECURITY", LAW),
    ("STATE OF NEW HAMPSHIRE DEPT OF SAFETY", LAW), ("LEHIGH UNIVERSITY POLICE DEPARTMENT", LAW),
    # the false positives the substring keys produced
    ("USDA FOREST SERVICE FEPP", NAT), ("MINNESOTA CULTIVATED WILD RICE COUNCIL", GOV),
    ("SULLIVAN COUNTY OFFICE OF EMERGENCY MANAGEMENT", GOV), ("OFFICE OF AVIATION SERVICES", GOV),
    ("MARSHALL UNIVERSITY", RES), ("CITY OF MARSHALL", GOV),
    ("OFFICE OF LOUISIANA STATE FIRE MARSHAL", FIRE), ("OFFICE OF LOUISIANA STATE FIRE MARSHALL", FIRE),
    ("CALCASIEU PARISH POLICE JURY", GOV), ("COLUMBUS OFFICE OF HOMELAND SECURITY", GOV),
    ("NAVAL AIR SYSTEMS COMMAND", MIL), ("UNITED STATES NAVY", MIL), ("UNITED STATESAIR FORCE", MIL),
    ("BIOSYSTEMS ENGINEERING", GOV), ("GEORGIA FORESTRY COMMISSION", NAT),
    ("STATE OF ALASKA DEPT OF FISH & GAME", NAT), ("CLEMSON UNIVERSITY", RES),
]


class Categorise(unittest.TestCase):
    def test_real_owner_names(self):
        for owner, want in CASES:
            with self.subTest(owner=owner):
                self.assertEqual(reg.categorise(owner), want)

    def test_ice_is_never_a_substring(self):
        for owner in ("ICE MAN HOLDINGS", "TWO BAG ICE", "PRICE AVIATION", "OFFICE OF THE GOVERNOR"):
            self.assertNotIn("law enforcement", reg.categorise(owner).lower(), owner)

    def test_law_enforcement_set(self):
        self.assertEqual(reg.LAW_ENFORCEMENT, frozenset((LAW, FED, "Coast Guard")))


if __name__ == "__main__":
    unittest.main()
