"""adsbdb.py offline (backlog 292).

! NO REAL adsbdb ANSWER IS IN THIS FILE. Their route data may not be copied
or published, and this repository goes public at first release. Every
callsign and pairing below is invented ("TST123" Helsinki-Stockholm); only
the airports' codes and rounded coordinates are real, and those are public.
The response SHAPE is the one measured on 2026-10-19 (bin\\lta292_adsbdb_probe.py).
"""
import asyncio
import json
import unittest

from _load import load

ab = load("adsbdb")
rc = load("route_check")

EFHK = {"lat": 60.317, "lon": 24.963, "tz": "Europe/Helsinki", "ident": "EFHK"}
ESSA = {"lat": 59.652, "lon": 17.919, "tz": "Europe/Stockholm", "ident": "ESSA"}
TABLE = {"EFHK": EFHK, "ESSA": ESSA}


def answer(origin="ESSA", dest="EFHK", o=(59.652, 17.919), d=(60.317, 24.963)):
    end = lambda code, ll: {"icao_code": code, "iata_code": "XXX", "latitude": ll[0],
                            "longitude": ll[1], "name": "n", "country_name": "c"}
    return json.dumps({"response": {"flightroute": {
        "callsign": "TST123", "callsign_icao": "TST123", "callsign_iata": None,
        "airline": None, "origin": end(origin, o), "destination": end(dest, d)}}}).encode()


MISS_BODY = b'{"response":"unknown callsign"}'
JSON = "application/json"


class LookupKey(unittest.TestCase):
    def test_airline_shapes(self):
        for cs, want in (("FIN1G", "FIN1G"), (" fin1g ", "FIN1G"), ("TST123", "TST123"),
                         ("ABC1234", "ABC1234")):
            self.assertEqual(ab.lookup_key(cs), want, cs)

    def test_not_asked(self):
        for cs in (None, "", "N123AB", "OHLVA", "ABC12345", "AB1", "ABCD12", "ABC"):
            self.assertIsNone(ab.lookup_key(cs), cs)


class Parse(unittest.TestCase):
    def test_hit(self):
        state, route = ab.parse(200, JSON, answer())
        self.assertEqual(state, ab.HIT)
        self.assertEqual(route, {"origin_icao": "ESSA", "origin_lat": 59.652, "origin_lon": 17.919,
                                 "destination_icao": "EFHK", "destination_lat": 60.317,
                                 "destination_lon": 24.963})

    def test_miss_is_404_unknown(self):
        self.assertEqual(ab.parse(404, JSON, MISS_BODY), (ab.MISS, None))

    def test_v1_html_is_a_failure_not_a_miss(self):
        # Measured: /v1/ answers 200 with the website for ANY callsign.
        state, why = ab.parse(200, "text/html; charset=utf-8", b"<!DOCTYPE html><html></html>")
        self.assertEqual(state, ab.ERROR)
        self.assertIn("not JSON", why)

    def test_json_header_with_html_body(self):
        self.assertEqual(ab.parse(200, JSON, b"<!DOCTYPE html>")[0], ab.ERROR)

    def test_429(self):
        self.assertEqual(ab.parse(429, "text/plain", b"slow down"), (ab.LIMITED, None))

    def test_other_status(self):
        self.assertEqual(ab.parse(500, JSON, b'{"response":"x"}')[0], ab.ERROR)
        self.assertEqual(ab.parse(503, JSON, answer())[0], ab.ERROR)   # a route, but not a 200
        self.assertEqual(ab.parse(404, JSON, b'{"response":"unknown aircraft"}')[0], ab.ERROR)

    def test_bad_shapes(self):
        self.assertEqual(ab.parse(200, JSON, b'{"response":{}}')[0], ab.ERROR)
        self.assertEqual(ab.parse(200, JSON, b'[]')[0], ab.ERROR)
        self.assertEqual(ab.parse(200, JSON, answer(origin="XX"))[0], ab.ERROR)
        self.assertEqual(ab.parse(200, JSON, answer(dest=None))[0], ab.ERROR)

    def test_bad_coordinates_dropped_not_fatal(self):
        state, route = ab.parse(200, JSON, answer(o=(999, 17.9)))
        self.assertEqual(state, ab.HIT)
        self.assertIsNone(route["origin_lat"])
        self.assertIsNone(route["origin_lon"])
        self.assertEqual(route["destination_lat"], 60.317)


class CacheTest(unittest.TestCase):
    def test_lifetimes(self):
        c = ab.Cache()
        c.put("A", ab.HIT, {"x": 1}, 0)
        c.put("B", ab.MISS, {"x": 1}, 0)
        c.put("C", ab.ERROR, "why", 0)
        self.assertEqual(c.get("A", 30 * 86400 - 1), (ab.HIT, {"x": 1}))
        self.assertIsNone(c.get("A", 30 * 86400))
        self.assertEqual(c.get("B", 86399), (ab.MISS, None))
        self.assertIsNone(c.get("B", 86400))
        self.assertEqual(c.get("C", 899), (ab.ERROR, None))
        self.assertIsNone(c.get("C", 900))
        self.assertEqual(len(c), 0)

    def test_cap_drops_oldest(self):
        c = ab.Cache(cap=2)
        for k in "ABC":
            c.put(k, ab.MISS, None, 0)
        self.assertIsNone(c.get("A", 1))
        self.assertIsNotNone(c.get("C", 1))


class BudgetTest(unittest.TestCase):
    def test_rolling_hour(self):
        b = ab.Budget(limit=3)
        for t in (0, 10, 20):
            self.assertTrue(b.allow(t))
            b.record(t)
        self.assertFalse(b.allow(30))
        self.assertFalse(b.allow(100))           # an hour, not a minute
        self.assertEqual(b.free_at(30), 3600)
        self.assertTrue(b.allow(3600))

    def test_default_under_adsbdb_threshold(self):
        self.assertLess(ab.HOURLY_BUDGET, 512)
        self.assertGreater(ab.PAUSE_429_S, 300)
        self.assertIn("/v0/", ab.API_URL)


class Choose(unittest.TestCase):
    def test_plausible_published_with_schedule(self):
        state, route = ab.parse(200, JSON, answer())
        # Over the Baltic between the two, at cruise, heading east.
        leg, verdict, n = ab.choose(route, TABLE.get, 60.0, 21.5, 35000, 80)
        self.assertEqual(verdict, rc.PLAUSIBLE)
        self.assertEqual((leg["origin_icao"], leg["destination_icao"]), ("ESSA", "EFHK"))
        self.assertEqual(leg["destination_tz"], "Europe/Helsinki")   # the table, not adsbdb
        self.assertIsNone(leg["route_observations"])
        self.assertEqual(n, 1)

    def test_implausible_dropped(self):
        route = ab.parse(200, JSON, answer())[1]
        # 3,000 ft over Oslo: low and far from both ends -> schedule rejects.
        self.assertEqual(ab.choose(route, TABLE.get, 59.9, 10.7, 3000, 80), (None, None, 0))

    def test_schedule_not_filed(self):
        # 8,000 ft mid-leg, ~195 km from each end: the low-far-from-ends rule
        # rejects it, and only the schedule profile has that rule.
        route = ab.parse(200, JSON, answer())[1]
        self.assertEqual(ab.choose(route, TABLE.get, 60.1, 21.4, 8000, 80), (None, None, 0))
        ok, _, _ = rc.evaluate({"origin_lat": 59.652, "origin_lon": 17.919,
                                "destination_lat": 60.317, "destination_lon": 24.963},
                               60.1, 21.4, 8000, 80, profile=rc.FILED)
        self.assertTrue(ok)

    def test_adsbdb_coordinates_when_table_lacks_an_end(self):
        route = ab.parse(200, JSON, answer())[1]
        leg, verdict, _ = ab.choose(route, {"EFHK": EFHK}.get, 60.0, 21.5, 35000, 80)
        self.assertEqual(verdict, rc.PLAUSIBLE)
        self.assertEqual(leg["origin_lat"], 59.652)
        self.assertIsNone(leg["origin_tz"])

    def test_no_coordinates_anywhere_is_not_published(self):
        route = ab.parse(200, JSON, answer(o=(999, 999)))[1]
        self.assertEqual(ab.choose(route, {"EFHK": EFHK}.get, 60.0, 21.5, 35000, 80), (None, None, 0))

    def test_nothing(self):
        self.assertEqual(ab.choose(None, TABLE.get, 60.0, 21.5), (None, None, 0))


class Clock:
    def __init__(self):
        self.t = 1_000_000.0
        self.slept = []

    def __call__(self):
        return self.t

    async def sleep(self, s):
        self.slept.append(s)
        self.t += s


def client(answers, clock=None):
    clock = clock or Clock()
    asked = []

    async def fetch(_session, key):
        asked.append(key)
        clock.t += 0.7
        a = answers.pop(0)
        if isinstance(a, Exception):
            raise a
        return a

    return ab.AdsbdbRoutes(clock=clock, sleep=clock.sleep, fetch=fetch), asked, clock


def drain(c):
    asyncio.run(c.async_drain(None))


class Lookup(unittest.TestCase):
    def test_one_request_per_callsign_not_per_poll(self):
        c, asked, clock = client([(200, JSON, answer()), (404, JSON, MISS_BODY)])
        for _ in range(3):                       # three polls before the drain
            self.assertIsNone(c.route("TST123"))
            self.assertIsNone(c.route("TST9"))
            self.assertIsNone(c.route("N123AB"))  # never queued
        drain(c)
        self.assertEqual(asked, ["TST123", "TST9"])
        self.assertEqual(clock.slept, [ab.MIN_GAP_S])
        for _ in range(3):                       # three polls after it
            self.assertEqual(c.route("TST123")["destination_icao"], "EFHK")
            self.assertIsNone(c.route("TST9"))
        drain(c)
        self.assertEqual(asked, ["TST123", "TST9"])
        self.assertEqual(c.status, "ok")
        self.assertFalse(c.pending)

    def test_miss_asked_again_after_a_day(self):
        c, asked, clock = client([(404, JSON, MISS_BODY), (404, JSON, MISS_BODY)])
        c.route("TST9")
        drain(c)
        clock.t += 86400
        c.route("TST9")
        drain(c)
        self.assertEqual(asked, ["TST9", "TST9"])

    def test_429_pauses_everything_and_keeps_the_callsign(self):
        c, asked, clock = client([(429, "text/plain", b""), (200, JSON, answer()),
                                  (404, JSON, MISS_BODY)])
        c.route("TST123")
        c.route("TST9")
        drain(c)
        self.assertEqual(asked, ["TST123"])
        self.assertTrue(c.pending)
        self.assertIn("429", c.status)
        self.assertIsNone(c.route("TST123"))         # not cached as anything
        clock.t += ab.PAUSE_429_S - 5
        drain(c)
        self.assertEqual(asked, ["TST123"])          # nothing during the pause
        clock.t += 10
        drain(c)
        self.assertEqual(asked, ["TST123", "TST123", "TST9"])
        self.assertEqual(c.route("TST123")["origin_icao"], "ESSA")

    def test_failures_cached_briefly_then_pause(self):
        c, asked, clock = client([OSError("down"), (200, "text/html", b"<html>"),
                                  (500, JSON, b"{}"), (200, JSON, answer())])
        for cs in ("AAA1", "BBB1", "CCC1", "TST123"):
            c.route(cs)
        drain(c)
        self.assertEqual(asked, ["AAA1", "BBB1", "CCC1"])
        self.assertIn("paused after 3 failures", c.status)
        self.assertIsNone(c.route("AAA1"))           # an error, not a route
        clock.t += ab.PAUSE_ERRORS_S
        drain(c)
        self.assertEqual(asked[-1], "TST123")
        self.assertEqual(c.status, "ok")
        # The failed ones come back after ERROR_TTL_S, not before.
        self.assertIsNone(c.route("AAA1"))
        self.assertFalse(c.pending)

    def test_an_answer_resets_the_failure_count(self):
        c, asked, clock = client([OSError("x"), (404, JSON, MISS_BODY), OSError("x"),
                                  OSError("x"), (404, JSON, MISS_BODY)])
        for cs in ("AAA1", "BBB1", "CCC1", "DDD1", "EEE1"):
            c.route(cs)
        drain(c)
        self.assertEqual(asked, ["AAA1", "BBB1", "CCC1", "DDD1", "EEE1"])
        self.assertEqual(c.status, "ok")

    def test_hourly_budget(self):
        c, asked, clock = client([(404, JSON, MISS_BODY)] * 5)
        c.budget = ab.Budget(limit=2)
        for cs in ("AAA1", "BBB1", "CCC1"):
            c.route(cs)
        drain(c)
        self.assertEqual(asked, ["AAA1", "BBB1"])
        self.assertIn("budget", c.status)
        clock.t += 3600
        drain(c)
        self.assertEqual(asked, ["AAA1", "BBB1", "CCC1"])

    def test_queue_cap(self):
        c, asked, clock = client([])
        for i in range(ab.MAX_QUEUE + 20):
            c.route("TST%d" % i)
        self.assertEqual(len(c._queue), ab.MAX_QUEUE)

    def test_one_drain_at_a_time(self):
        c, asked, clock = client([(404, JSON, MISS_BODY)])
        c.route("TST9")
        c._draining = True
        drain(c)
        self.assertEqual(asked, [])


if __name__ == "__main__":
    unittest.main()
