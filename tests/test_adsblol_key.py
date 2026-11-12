"""The user's own adsb.lol API key (backlog 336): one optional, masked field in both dialogs, stored stripped
("" meaning none), handed to the shared poll before any request, shown on the sensor as none/set/refused, never the
key. The library's own tests cover what the poll does with it (saw-livetrack 0.2.36, tests/test_adsb_poll.py).
Source checks: the flow, coordinator and sensor import Home Assistant.

Run from the repo root: python -m unittest discover -s tests
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMP = os.path.join(ROOT, "custom_components", "live_track_aircraft")


def source(name):
    with open(os.path.join(COMP, name), encoding="utf-8") as fh:
        return fh.read()


class AdsbLolKey(unittest.TestCase):
    def test_the_option_key(self):
        self.assertIn('CONF_ADSBLOL_KEY = "adsblol_api_key"', source("const.py"))

    def test_one_masked_optional_field_cleared_by_emptying(self):
        f = source("config_flow.py")
        self.assertEqual(f.count("vol.Optional(\n                CONF_ADSBLOL_KEY,"), 1)
        self.assertIn('description={"suggested_value": defaults.get(CONF_ADSBLOL_KEY, "")}', f)
        self.assertIn("TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))", f)
        self.assertNotIn("vol.Required(CONF_ADSBLOL_KEY", f)

    def test_stored_stripped_and_empty_means_none(self):
        f = source("config_flow.py")
        self.assertIn('values[CONF_ADSBLOL_KEY] = (values.get(CONF_ADSBLOL_KEY) or "").strip()', f)
        # in _from_dialog, which both flows call
        self.assertLess(f.index("def _from_dialog"), f.index("values[CONF_ADSBLOL_KEY]"))
        self.assertLess(f.index("values[CONF_ADSBLOL_KEY]"), f.index("def _schema"))

    def test_the_poll_has_it_before_the_first_request(self):
        c = source("coordinator.py")
        self.assertIn('self.adsblol_key = str(opts.get(CONF_ADSBLOL_KEY) or "").strip()', c)
        body = c[c.index("async def _async_update_data"):]
        self.assertLess(body.index("self.poll.set_key(self.claim_key, self.adsblol_key)"), body.index("await fetch("))

    def test_unload_releases_it(self):
        self.assertIn("poll.release(coordinator.claim_key)", source("__init__.py"))

    def test_the_sensor_shows_the_status_never_the_key(self):
        s = source("sensor.py")
        self.assertIn('"adsblol_key": self._coordinator.poll.key_status()', s)
        self.assertNotIn("adsblol_key\": self._coordinator.adsblol_key", s)

    def test_labelled_and_described_in_both_steps_and_files(self):
        self.assertEqual(source("strings.json"), source(os.path.join("translations", "en.json")))
        d = json.loads(source("strings.json"))
        for step in (d["config"]["step"]["user"], d["options"]["step"]["init"]):
            self.assertEqual(step["data"]["adsblol_api_key"], "adsb.lol API key")
            self.assertIn("500 requests a day", step["data_description"]["adsblol_api_key"])

    def test_requires_the_library_that_sends_it(self):
        m = json.loads(source("manifest.json"))
        self.assertIn("saw-livetrack[zones]>=0.2.36,<0.3", m["requirements"])


if __name__ == "__main__":
    unittest.main()
