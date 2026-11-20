"""hacs/default#14501 (Frenck, 2026-11-19): the five review items, version 0.1.3.

1. The user's pictures: the view keeps authentication; the entity's URL is signed, cached per file, re-signed
   only near expiry.
2. No SQLite or stat on the event loop per aircraft: one executor job per poll (lookups.resolve), _record reads
   only its PollLookups.
3. No first ZoneInfo on the loop: route_check builds zones only in warm_zones once loop-safe; route_download's
   Chicago zone is a module constant.
4. The icon view's file lookup runs in the executor job with the render.
5. saw-livetrack 0.2.42 or later (the map card writes only its own resource rows): test_adsblol_key.py and
   test_enforcement.py pin the manifest line.
The coordinator and the views import Home Assistant, so what connects them is checked in their source (ast), as
the rest of this suite does; the behaviour is checked on the box after a deploy.
"""
import ast
import datetime as dt
import json
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _load import load, source  # noqa: E402

lookups = load("lookups")
route_check = load("route_check")
pictures = load("pictures")
adsbdb = load("adsbdb")
rd = load("route_download")


def _func(src, cls, name):
    """The ast node of a method (cls) or a module function (cls None)."""
    tree = ast.parse(src)
    body = tree.body
    if cls is not None:
        body = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls).body
    return next(n for n in body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)


def _calls(node):
    return [ast.unparse(n.func) for n in ast.walk(node) if isinstance(n, ast.Call)]


# ------------------------------------------------------------------ item 2

class FakeRoutes:
    def __init__(self, legs, times=None, boom=()):
        self._legs, self._times, self._boom = legs, times or {}, set(boom)
        self.asked = []

    def legs(self, cs):
        self.asked.append(("legs", cs))
        if cs in self._boom:
            raise RuntimeError("disk")
        return self._legs.get(cs, [])

    def leg_times(self, cs):
        self.asked.append(("times", cs))
        return self._times.get(cs, {})


class FakeAirports:
    def __init__(self, table):
        self.table, self.asked = table, []

    def lookup(self, code):
        self.asked.append(code)
        if code == "BOOM":
            raise RuntimeError("disk")
        return self.table.get(code)


def obs(callsign, hexid):
    return SimpleNamespace(callsign=callsign, identity=hexid)


class Lookups(unittest.TestCase):
    def setUp(self):
        self.routes = FakeRoutes({"AAL1": [("KORD", "KLAX", 9), ("KLAX", "KORD", 3)], "UAL2": [("KORD", "BOOM", 1)]},
                                 {"AAL1": {("KORD", "KLAX"): {"d": [600, 30, "f", 5]}}}, boom={"BAD1"})
        self.airports = FakeAirports({"KORD": {"tz": "America/Chicago", "lat": 41.98, "lon": -87.9},
                                      "KLAX": {"tz": "America/Los_Angeles", "lat": 33.94, "lon": -118.4},
                                      "EGLL": {"tz": "Europe/London", "lat": 51.47, "lon": -0.45}})
        self.owners = {"a00001": {"registration": "N1", "owner": "X"}}
        self.asked_owners = []

    def owner(self, h):
        self.asked_owners.append(h)
        if h == "bad":
            raise RuntimeError("disk")
        return self.owners.get(h)

    def resolve(self, observations, extra=()):
        return lookups.resolve(self.routes, self.airports, self.owner, observations, extra)

    def test_everything_record_reads_is_resolved(self):
        lk = self.resolve([obs("AAL1", "a00001"), obs("AAL1", "a00002"), obs(None, "a00003")], extra=["EGLL", None])
        self.assertEqual(lk.legs("AAL1"), [("KORD", "KLAX", 9), ("KLAX", "KORD", 3)])
        self.assertEqual(lk.leg_times("AAL1"), {("KORD", "KLAX"): {"d": [600, 30, "f", 5]}})
        self.assertEqual(lk.airport("KORD")["tz"], "America/Chicago")
        self.assertEqual(lk.airport("EGLL")["tz"], "Europe/London")      # adsbdb's codes
        self.assertEqual(lk.owner("a00001"), {"registration": "N1", "owner": "X"})
        self.assertIsNone(lk.owner("a00002"))
        # once per call sign, once per hex, once per code
        self.assertEqual(self.routes.asked.count(("legs", "AAL1")), 1)
        self.assertEqual(sorted(self.asked_owners), ["a00001", "a00002", "a00003"])
        self.assertEqual(sorted(self.airports.asked), ["EGLL", "KLAX", "KORD"])

    def test_a_miss_is_nothing_on_file(self):
        lk = self.resolve([])
        self.assertEqual(lk.legs("ZZZ9"), [])
        self.assertEqual(lk.leg_times("ZZZ9"), {})
        self.assertEqual(lk.legs(None), [])
        self.assertIsNone(lk.airport("KORD"))
        self.assertIsNone(lk.owner("a00001"))

    def test_a_store_fault_is_a_miss_not_a_failed_poll(self):
        lk = self.resolve([obs("BAD1", "bad"), obs("UAL2", "a00001")])
        self.assertEqual(lk.legs("BAD1"), [])
        self.assertIsNone(lk.owner("bad"))
        self.assertIsNone(lk.airport("BOOM"))
        self.assertEqual(lk.airport("KORD")["tz"], "America/Chicago")

    def test_no_stores_no_owner_table(self):
        lk = lookups.resolve(None, None, None, [obs("AAL1", "a00001")])
        self.assertEqual(lk.legs("AAL1"), [])
        self.assertIsNone(lk.owner("a00001"))

    def test_zones_are_warmed_in_the_job(self):
        route_check._ZONES.pop("America/Los_Angeles", None)
        self.resolve([obs("AAL1", "a00001")])
        self.assertIsInstance(route_check._ZONES.get("America/Los_Angeles"), ZoneInfo)


class CoordinatorWiring(unittest.TestCase):
    src = source("coordinator.py")

    def test_record_and_describe_read_no_store(self):
        for name in ("_record", "_describe"):
            calls = _calls(_func(self.src, "AircraftCoordinator", name))
            for c in calls:
                self.assertFalse(c.startswith(("self.routes.", "self.airports.")), (name, c))
                self.assertNotEqual(c, "lookup_owner", name)
        rec = ast.unparse(_func(self.src, "AircraftCoordinator", "_record"))
        self.assertIn("lk.legs(obs.callsign), lk.airport", rec)
        self.assertIn("times=lk.leg_times(obs.callsign)", rec)
        self.assertIn("self._lk.owner(obs.identity)", ast.unparse(_func(self.src, "AircraftCoordinator", "_describe")))

    def test_one_executor_job_per_poll_before_any_record(self):
        upd = _func(self.src, "AircraftCoordinator", "_async_update_data")
        calls = _calls(upd)
        self.assertEqual(calls.count("self._async_lookups"), 1)
        text = ast.unparse(upd)
        self.assertLess(text.index("self._async_lookups("), text.index("self._record("))
        # every batch this poll draws is in the one job
        self.assertIn("[*observations, *watch_found, *military_found, *followed.values()]", text)
        job = _func(self.src, "AircraftCoordinator", "_async_lookups")
        self.assertEqual(_calls(job).count("self.hass.async_add_executor_job"), 1)
        self.assertIn("resolve_lookups, self.routes, self.airports, lookup_owner", ast.unparse(job))
        # adsbdb's cache is only PEEKED before the job; route() (which queues) stays in _record
        self.assertIn("self.adsbdb.peek", _calls(job))
        self.assertNotIn("self.adsbdb.route", _calls(job))

    def test_loop_safe_and_signed(self):
        init = ast.unparse(_func(self.src, "AircraftCoordinator", "__init__"))
        self.assertIn("set_loop_safe(True)", init)
        self.assertIn("use_content_user=True", init)
        self.assertIn("async_sign_path", init)


class RoutesOffTheLoop(unittest.TestCase):
    def test_connection_any_thread_and_reopen_only_marks(self):
        src = source("routes.py")
        self.assertIn("check_same_thread=False", src)
        reopen = _func(src, "RouteStore", "reopen")
        self.assertEqual(_calls(reopen), [])          # no close on the caller's (the loop's) thread


class AdsbdbPeek(unittest.TestCase):
    def test_peek_changes_nothing(self):
        r = adsbdb.AdsbdbRoutes(clock=lambda: 1000.0)
        self.assertIsNone(r.peek("AAL1"))
        self.assertFalse(r.pending)                    # route() would have queued it
        route = {"origin_icao": "KORD", "destination_icao": "KLAX"}
        r.cache.put(adsbdb.lookup_key("AAL1"), adsbdb.HIT, route, 1000.0)
        self.assertEqual(r.peek("AAL1"), route)
        n = len(r.cache)
        self.assertIsNone(r.peek("AAL1", now=1000.0 + adsbdb.HIT_TTL_S + 1))   # expired: None ...
        self.assertEqual(len(r.cache), n)                                    # ... and not dropped
        r.cache.put(adsbdb.lookup_key("UAL2"), adsbdb.MISS, None, 1000.0)
        self.assertIsNone(r.peek("UAL2"))
        self.assertIsNone(r.peek(None))


# ------------------------------------------------------------------ item 3

class Zones(unittest.TestCase):
    def tearDown(self):
        route_check.set_loop_safe(False)

    def test_loop_safe_builds_nothing(self):
        route_check._ZONES.pop("Asia/Kathmandu", None)
        route_check.set_loop_safe(True)
        self.assertIsNone(route_check._zone("Asia/Kathmandu"))
        self.assertNotIn("Asia/Kathmandu", route_check._ZONES)
        self.assertEqual(route_check.warm_zones(["Asia/Kathmandu", None, "Asia/Kathmandu"]), 1)
        self.assertIsInstance(route_check._zone("Asia/Kathmandu"), ZoneInfo)
        self.assertEqual(route_check.warm_zones(["Asia/Kathmandu"]), 0)

    def test_an_unknown_name_is_none_either_way(self):
        route_check.warm_zones(["Not/AZone"])
        route_check.set_loop_safe(True)
        self.assertIsNone(route_check._zone("Not/AZone"))
        self.assertIsNone(route_check._zone(None))

    def test_offline_default_still_builds(self):
        route_check._ZONES.pop("Pacific/Chatham", None)
        self.assertIsInstance(route_check._zone("Pacific/Chatham"), ZoneInfo)

    def test_leg_time_loop_safe_after_warming(self):
        leg = {"origin_tz": "America/Chicago", "destination_tz": "America/Los_Angeles",
               "origin_lat": 41.98, "origin_lon": -87.9, "destination_lat": 33.94, "destination_lon": -118.4}
        times = {"d": [600, 60, "f", 5], "a": [780, 60, "f", 5]}
        now = dt.datetime(2026, 11, 18, 17, 30, tzinfo=dt.UTC).timestamp()   # 11:30 CST
        offline = route_check.leg_time(times, leg, now)
        route_check.warm_zones(["America/Chicago", "America/Los_Angeles"])
        route_check.set_loop_safe(True)
        self.assertEqual(route_check.leg_time(times, leg, now), offline)
        self.assertEqual(offline[0], route_check.IN_WINDOW)

    def test_no_lru_and_no_zoneinfo_call_in_zone(self):
        zone = _func(source("route_check.py"), None, "_zone")
        self.assertEqual(zone.decorator_list, [])
        self.assertNotIn("ZoneInfo", _calls(zone))

    def test_publish_zone_is_a_module_constant(self):
        self.assertIsInstance(rd.PUBLISH_TZ, ZoneInfo)
        self.assertEqual(str(rd.PUBLISH_TZ), "America/Chicago")
        self.assertNotIn("ZoneInfo", _calls(_func(source("route_download.py"), None, "last_slot")))


# ------------------------------------------------------------------ item 1

class SignedPictures(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.dir = self.td.name
        self.signed = []

    def tearDown(self):
        self.td.cleanup()

    def put(self, name, mtime):
        p = os.path.join(self.dir, name)
        with open(p, "wb") as fh:
            fh.write(b"x")
        os.utime(p, (mtime, mtime))

    def signer(self, url, seconds):
        self.signed.append((url, seconds))
        return "%s&authSig=s%d" % (url, len(self.signed))

    def test_signed_cached_and_resigned_near_expiry(self):
        self.put("a1b2c3.png", 1_700_000_000)
        o = pictures.Overrides(self.dir, signer=self.signer)
        o.scan(now=0)
        raw = pictures.URL_BASE + "/a1b2c3.png?v=1700000000"
        u1 = o.url("A1B2C3", now=100)
        self.assertEqual(u1, raw + "&authSig=s1")
        self.assertEqual(self.signed, [(raw, pictures.SIGN_S)])
        self.assertEqual(o.url("a1b2c3", now=100 + pictures.SIGN_S - pictures.RESIGN_BEFORE_S - 1), u1)
        self.assertEqual(len(self.signed), 1)
        u2 = o.url("a1b2c3", now=100 + pictures.SIGN_S - pictures.RESIGN_BEFORE_S + 1)
        self.assertEqual(u2, raw + "&authSig=s2")
        self.assertIsNone(o.url("ffffff", now=100))

    def test_a_replaced_file_is_a_new_signed_url_and_the_old_goes(self):
        self.put("a1b2c3.png", 1_700_000_000)
        o = pictures.Overrides(self.dir, signer=self.signer)
        o.scan(now=0)
        o.url("a1b2c3", now=0)
        self.put("a1b2c3.png", 1_700_000_500)
        o.scan(now=61)
        u = o.url("a1b2c3", now=61)
        self.assertIn("?v=1700000500&authSig=s2", u)
        self.assertEqual(list(o._signed), [pictures.URL_BASE + "/a1b2c3.png?v=1700000500"])

    def test_without_a_signer_the_plain_url(self):
        self.put("a1b2c3.png", 1_700_000_000)
        o = pictures.Overrides(self.dir)
        o.scan(now=0)
        self.assertEqual(o.url("a1b2c3"), pictures.URL_BASE + "/a1b2c3.png?v=1700000000")

    def test_a_day_and_two_hours(self):
        self.assertEqual(pictures.SIGN_S, 86400)
        self.assertEqual(pictures.RESIGN_BEFORE_S, 7200)


class Views(unittest.TestCase):
    src = source("web.py")

    def cls(self, name):
        return next(n for n in ast.parse(self.src).body if isinstance(n, ast.ClassDef) and n.name == name)

    def assigned(self, cls):
        return {t.id for n in cls.body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}

    def test_the_picture_view_keeps_authentication(self):
        self.assertNotIn("requires_auth", self.assigned(self.cls("AircraftPictureView")))
        self.assertIn('"Cache-Control": "private, max-age=86400"', self.src)

    def test_the_icons_stay_open_they_are_our_artwork(self):
        self.assertIn("requires_auth", self.assigned(self.cls("AircraftIconView")))

    # ---------------------------------------------------------- item 4
    def test_the_icon_lookup_is_in_the_executor_job(self):
        get = _func(self.src, "AircraftIconView", "get")
        calls = _calls(get)
        self.assertNotIn("icons.icon_path", calls)
        self.assertIn("icons.valid_key", calls)
        self.assertIn("_render_key, key, degrees, tone, weight, badge, lights", ast.unparse(get))
        job = _calls(_func(self.src, None, "_render_key"))
        self.assertIn("icons.icon_path", job)
        self.assertIn("icons.render", job)


# ------------------------------------------------------------------ item 5

class Manifest(unittest.TestCase):
    def test_version_and_floor(self):
        m = json.loads(source("manifest.json"))
        self.assertEqual(m["version"], "0.1.3")
        self.assertIn("saw-livetrack[zones]>=0.2.42,<0.3", m["requirements"])


if __name__ == "__main__":
    unittest.main()
