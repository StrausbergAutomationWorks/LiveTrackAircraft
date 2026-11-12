"""The tracking centre as a map marker (centre.py, backlog 192, option A, Lee 2026-10-18):
the dialog shows one `location` field, the entry stores latitude and longitude
as before, and the flow, the strings and the translations agree on it."""
import json
import os
import re
import unittest

from _load import COMP, load, source

centre = load("centre")
const = load("const")

STORED = {
    const.CONF_LATITUDE: 39.816990066207804,
    const.CONF_LONGITUDE: -84.0496410145588,
    const.CONF_RADIUS_KM: 56.0,
    const.CONF_SCAN_INTERVAL: 15,
    const.CONF_MAX_AIRCRAFT: 250,
}
HOME = (51.5, -0.12)


def form(lat, lon, **extra):
    d = {k: v for k, v in STORED.items()
         if k not in (const.CONF_LATITUDE, const.CONF_LONGITUDE)}
    d[const.CONF_LOCATION] = {"latitude": lat, "longitude": lon}
    d.update(extra)
    return d


class ToForm(unittest.TestCase):
    def test_marker_starts_at_the_stored_centre(self):
        self.assertEqual(centre.to_form(STORED, *HOME),
                         {"latitude": STORED["latitude"], "longitude": STORED["longitude"]})

    def test_marker_starts_at_home_when_nothing_is_stored(self):
        self.assertEqual(centre.to_form({}, *HOME), {"latitude": 51.5, "longitude": -0.12})

    def test_no_radius_in_the_marker(self):
        self.assertNotIn("radius", centre.to_form(STORED, *HOME))


class FromForm(unittest.TestCase):
    def test_unmoved_marker_stores_exactly_what_was_stored(self):
        # 05 A8: submitting the dialog untouched must not move anything.
        m = centre.to_form(STORED, *HOME)
        sub = form(m["latitude"], m["longitude"])
        values, err = centre.from_form(sub)
        self.assertIsNone(err)
        self.assertEqual(values, STORED)

    def test_location_key_is_never_stored(self):
        values, _ = centre.from_form(form(10.0, 20.0))
        self.assertNotIn(const.CONF_LOCATION, values)
        self.assertEqual((values["latitude"], values["longitude"]), (10.0, 20.0))

    def test_other_fields_pass_through_unchanged(self):
        values, _ = centre.from_form(form(10.0, 20.0))
        for k in (const.CONF_RADIUS_KM, const.CONF_SCAN_INTERVAL, const.CONF_MAX_AIRCRAFT):
            self.assertEqual(values[k], STORED[k])

    def test_strings_are_coerced(self):
        values, err = centre.from_form(form("41.9", "-88"))
        self.assertIsNone(err)
        self.assertEqual((values["latitude"], values["longitude"]), (41.9, -88.0))

    def test_a_radius_inside_the_location_is_ignored(self):
        sub = form(10.0, 20.0)
        sub[const.CONF_LOCATION]["radius"] = 5000.0
        values, _ = centre.from_form(sub)
        self.assertEqual(values[const.CONF_RADIUS_KM], 56.0)
        self.assertNotIn("radius", values)

    def test_latitude_out_of_range_is_refused(self):
        # Measured on HA 2026.10.2: the selector itself accepts 141.9.
        for lat in (90.0001, -90.0001, 141.9):
            self.assertEqual(centre.from_form(form(lat, 0.0)), (None, centre.ERROR_INVALID_LOCATION))

    def test_latitude_at_the_poles_is_accepted(self):
        for lat in (90.0, -90.0):
            self.assertIsNone(centre.from_form(form(lat, 0.0))[1])

    def test_longitude_edges_are_kept(self):
        for lon in (180.0, -180.0):
            self.assertEqual(centre.from_form(form(0.0, lon))[0]["longitude"], lon)

    def test_wrapped_longitude_is_folded_back(self):
        for lon, want in ((190.0, -170.0), (-190.0, 170.0), (360.0 - 87.99, -87.99), (540.0, -180.0)):
            got = centre.from_form(form(0.0, lon))[0]["longitude"]
            self.assertAlmostEqual(got, want, places=9)
            self.assertTrue(-180.0 <= got <= 180.0)

    def test_nonsense_is_refused(self):
        for loc in (None, "41,-88", {}, {"latitude": 1.0}, {"longitude": 1.0},
                    {"latitude": "north", "longitude": 1.0},
                    {"latitude": float("nan"), "longitude": 1.0},
                    {"latitude": 1.0, "longitude": float("nan")},
                    {"latitude": 1.0, "longitude": float("inf")}):
            sub = form(0.0, 0.0)
            sub[const.CONF_LOCATION] = loc
            self.assertEqual(centre.from_form(sub), (None, centre.ERROR_INVALID_LOCATION), loc)

    def test_missing_location_is_refused(self):
        sub = form(0.0, 0.0)
        del sub[const.CONF_LOCATION]
        self.assertEqual(centre.from_form(sub), (None, centre.ERROR_INVALID_LOCATION))

    def test_input_is_not_mutated(self):
        sub = form(10.0, 20.0)
        before = json.dumps(sub, sort_keys=True)
        centre.from_form(sub)
        self.assertEqual(json.dumps(sub, sort_keys=True), before)


class Wiring(unittest.TestCase):
    """The flow uses the marker and converts both ways; checked in the source,
    because config_flow imports Home Assistant and cannot be loaded here."""

    def setUp(self):
        self.src = source("config_flow.py")

    def test_one_marker_no_radius_circle(self):
        self.assertEqual(self.src.count("LocationSelectorConfig(radius=False"), 1)

    def test_no_separate_latitude_or_longitude_field(self):
        self.assertIsNone(re.search(r"vol\.Required\(\s*CONF_LATITUDE", self.src))
        self.assertIsNone(re.search(r"vol\.Required\(\s*CONF_LONGITUDE", self.src))

    def test_both_steps_convert_before_storing(self):
        self.assertEqual(self.src.count("_from_dialog(user_input)"), 2)
        self.assertEqual(self.src.count("from_form(user_input)"), 1)
        self.assertNotIn("data=user_input", self.src)
        self.assertNotIn("options=user_input", self.src)
        self.assertNotIn("_title(user_input)", self.src)

    def test_both_steps_show_errors(self):
        self.assertEqual(self.src.count("errors=errors"), 2)
        self.assertEqual(self.src.count("return None, {CONF_LOCATION: error}"), 1)


class Labels(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(COMP, "strings.json"), "rb") as fh:
            self.raw = fh.read()
        self.s = json.loads(self.raw.decode("utf-8"))

    def test_translations_file_matches_strings(self):
        # HA reads translations/en.json for a custom integration, not strings.json.
        with open(os.path.join(COMP, "translations", "en.json"), "rb") as fh:
            self.assertEqual(fh.read(), self.raw)

    def test_location_is_labelled_and_lat_lon_are_gone(self):
        for step in (self.s["config"]["step"]["user"], self.s["options"]["step"]["init"]):
            self.assertIn("location", step["data"])
            self.assertIn("location", step["data_description"])
            self.assertNotIn("latitude", step["data"])
            self.assertNotIn("longitude", step["data"])

    def test_error_text_exists_for_both_flows(self):
        for flow in ("config", "options"):
            self.assertIn(centre.ERROR_INVALID_LOCATION, self.s[flow]["error"])

    def test_every_form_field_is_labelled(self):
        for step in (self.s["config"]["step"]["user"], self.s["options"]["step"]["init"]):
            self.assertEqual(set(step["data"]),
                             {"location", "radius_km", "scan_interval", "max_aircraft", "military_areas",
                          "follow_hexes", "follow_callsigns",    # backlog 332
                          "adsblol_api_key"})                    # backlog 336

    def test_no_bom(self):
        self.assertFalse(self.raw.startswith(b"\xef\xbb\xbf"))


if __name__ == "__main__":
    unittest.main()
