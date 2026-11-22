"""Photos (backlog 361): a Planespotters.net photo looked up when a viewer hovers an aircraft. Since saw-livetrack 0.2.43
(backlog 362) the lookup, the kept answers, the 429/403 pause and their tests are the library's
(saw_livetrack.aircraft_photos, tests/test_aircraft_photos.py there). This file checks this integration's address and
how it is wired. No real Planespotters answer is in this file.
"""
import json
import unittest

from _load import load, source
from saw_livetrack import aircraft_photos as AP

ph = load("photos")


class Paths(unittest.TestCase):
    def test_hex_only(self):
        self.assertEqual(ph.lookup_path("abc123"), "/api/live_track_aircraft/photo/abc123")
        self.assertEqual(ph.lookup_path("ABC123"), "/api/live_track_aircraft/photo/abc123")
        for v in ("~abc123", "abc12", "abc1234", "abg123", "", None, 12):
            self.assertIsNone(ph.lookup_path(v), v)

    def test_no_lookup_for_a_privacy_address(self):
        self.assertIsNone(ph.lookup_path("abc123", True))
        self.assertEqual(ph.lookup_path("abc123", False), "/api/live_track_aircraft/photo/abc123")

    def test_the_card_takes_the_path(self):
        # LiveTrackMapCard's D4h/D4i rule: /api/ then letters, digits, _ - / only, no empty segment, <= 200
        p = ph.lookup_path("abc123")
        self.assertRegex(p, r"^/api/[A-Za-z0-9_\-/]+$")
        self.assertNotIn("//", p)
        self.assertLessEqual(len(p), 200)


class Wiring(unittest.TestCase):
    def test_the_lookup_is_the_librarys(self):
        src = source("photos.py")
        self.assertIn("from saw_livetrack import aircraft_photos as _lib", src)
        for gone in ("class PhotoLookups", "api.planespotters.net", "session.get("):
            self.assertNotIn(gone, src)
        self.assertEqual(AP.STORE_KEY, "saw_aircraft_photos")

    def test_the_view_is_signed_in_only_answers_from_the_library_and_is_registered_once(self):
        src = source("web.py")
        start = src.index("class AircraftPhotoView")
        view = src[start:src.index("\ndef ", start)]
        self.assertNotIn("requires_auth =", view)        # Home Assistant's default: True
        self.assertIn("photos_lib.answer(hass.data, async_get_clientsession(hass), hexid)", view)
        self.assertIn('"Cache-Control"] = "no-store"', view)
        self.assertIn("status_code=400", view)
        self.assertIn("status_code=503", view)
        self.assertIn("hass.http.register_view(AircraftPhotoView())", src)
        self.assertIn("if hass.data.get(_VIEWS_KEY):", src)
        self.assertNotIn("live_track_aircraft_photos", src)   # the old per-integration store key

    def test_the_entity_carries_the_path_unrecorded(self):
        g = source("geo_location.py")
        self.assertIn('_unrecorded_attributes = frozenset({"marker_photo_lookup"})', g)
        self.assertIn('lookup_path(self._identity, rec.get("identity_hidden"))', g)

    def test_library_floor(self):
        self.assertIn("saw-livetrack[zones]>=0.2.43,<0.3", json.loads(source("manifest.json"))["requirements"])


if __name__ == "__main__":
    unittest.main()
