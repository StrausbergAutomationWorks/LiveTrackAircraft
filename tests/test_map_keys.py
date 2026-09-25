"""object_ids (D11) in the exact form the card accepts, or not at all.

D11 rule 7: the card drops a malformed value SILENTLY - a number, an
upper-case icao24, a lower-case registration all do nothing. So the form is
tested exactly, and a value that is not already right is left out, never
repaired. registration comes only from the FAA registry (stated AS the
registration for that Mode S code), never from the feed's `r`.
"""
import unittest

from _load import load

mk = load("map_keys")


class ObjectIds(unittest.TestCase):
    def test_both(self):
        self.assertEqual(mk.object_ids("a046e7", "N4174L"),
                         {"icao24": "a046e7", "registration": "N4174L"})

    def test_values_are_strings(self):
        for v in mk.object_ids("a046e7", "N100").values():
            self.assertIsInstance(v, str)

    def test_icao24_only(self):
        self.assertEqual(mk.object_ids("ace3b9", None), {"icao24": "ace3b9"})

    def test_our_identity_is_lowered(self):
        # identity is ours, not a stated value from elsewhere
        self.assertEqual(mk.object_ids("ACE3B9", None), {"icao24": "ace3b9"})

    def test_malformed_icao24_left_out(self):
        for bad in ("~a1b2c3", "a046e", "a046e7f", "g046e7", "", None, 10545127):
            with self.subTest(bad=bad):
                self.assertNotIn("icao24", mk.object_ids(bad, None) or {})

    def test_registration_never_repaired(self):
        for bad in ("n4174l", " N4174L", "N4174L ", "N", "", None, 4174, "N 4174L"):
            with self.subTest(bad=bad):
                self.assertNotIn("registration",
                                 mk.object_ids("a046e7", bad) or {})

    def test_foreign_forms_accepted(self):
        self.assertEqual(mk.object_ids("4aaa4b", "SE-JRK")["registration"], "SE-JRK")

    def test_nothing_to_say_is_none(self):
        self.assertIsNone(mk.object_ids(None, None))
        self.assertIsNone(mk.object_ids("zz", "lower"))


class RegistryRegistration(unittest.TestCase):
    """Which registry answer counts as the registration."""

    def test_owner_dict(self):
        self.assertEqual(mk.registry_registration({"registration": "N4174L", "owner": "X"}, None), "N4174L")

    def test_government_used_when_owner_absent(self):
        self.assertEqual(mk.registry_registration(None, {"registration": "N911VH"}), "N911VH")

    def test_owner_wins_over_government(self):
        self.assertEqual(mk.registry_registration({"registration": "N1"}, {"registration": "N2"}), "N1")

    def test_nothing(self):
        self.assertIsNone(mk.registry_registration(None, None))
        self.assertIsNone(mk.registry_registration("a plain owner string", None))
        self.assertIsNone(mk.registry_registration({"owner": "X"}, {}))


if __name__ == "__main__":
    unittest.main()
