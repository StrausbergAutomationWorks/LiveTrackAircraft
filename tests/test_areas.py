"""Military watch areas as typed in the options dialog (areas.py; Lee 2026-11-02 22:59)."""
import unittest

from _load import load

areas = load("areas")


class Parse(unittest.TestCase):
    def test_lee_s_three_circles(self):
        got, err = areas.parse_areas("39.81,-84.04,150; 38.6,-121.8,463; 34.0,-117.8,463")
        self.assertIsNone(err)
        self.assertEqual(got, [(39.81, -84.04, 150.0), (38.6, -121.8, 463.0), (34.0, -117.8, 463.0)])

    def test_nothing_is_no_areas(self):
        for text in (None, "", "   ", ";", " ; ; "):
            self.assertEqual(areas.parse_areas(text), ([], None), repr(text))

    def test_spaces_and_a_trailing_semicolon(self):
        got, err = areas.parse_areas(" 39.81 , -84.04 , 150 ; ")
        self.assertIsNone(err)
        self.assertEqual(got, [(39.81, -84.04, 150.0)])

    def test_the_limits_are_inside(self):
        for text in ("90,180,1", "-90,-180,2000"):
            self.assertIsNone(areas.parse_areas(text)[1], text)

    def test_refused(self):
        for text in ("39.81,-84.04", "39.81,-84.04,150,9", "north,-84.04,150", "91,0,10", "-91,0,10", "0,181,10",
                     "0,-181,10", "0,0,0.5", "0,0,2001", "nan,0,10", "0,nan,10", "0,0,nan", "0,0,inf",
                     "39.81 -84.04 150", "1,2,3; bad"):
            self.assertEqual(areas.parse_areas(text), ([], areas.ERROR_INVALID_AREAS), text)

    def test_at_most_ten(self):
        self.assertEqual(len(areas.parse_areas(";".join(["1,2,3"] * 10))[0]), 10)
        self.assertEqual(areas.parse_areas(";".join(["1,2,3"] * 11)), ([], areas.ERROR_INVALID_AREAS))

    def test_the_label(self):
        self.assertEqual(areas.label(areas.Area(39.81, -84.04, 150.0)), "39.81,-84.04,150")
        self.assertEqual(areas.label(areas.Area(34.0, -117.8, 463.0)), "34,-117.8,463")


if __name__ == "__main__":
    unittest.main()
