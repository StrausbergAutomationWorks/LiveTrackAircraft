"""Leg selection by FiledRoutesDB's PUBLISHED time windows (route_check.py),
since 2026-10-13. The windows are used as published, with no padding; a leg
outside its window is NOT ranked below a leg with no times (Lee: "We
shouldn't miss a flight because it left on-time."); weekend windows are
chosen by the origin's local day."""
import datetime as dt
import unittest
from zoneinfo import ZoneInfo

from _load import load

rc = load("route_check")

CHI, LA, SYD = ZoneInfo("America/Chicago"), ZoneInfo("America/Los_Angeles"), ZoneInfo("Australia/Sydney")
AIRPORTS = {
    "KORD": {"lat": 41.9786, "lon": -87.9048, "tz": "America/Chicago"},
    "KMDW": {"lat": 41.7868, "lon": -87.7522, "tz": "America/Chicago"},
    "KLAX": {"lat": 33.9425, "lon": -118.4081, "tz": "America/Los_Angeles"},
    "YSSY": {"lat": -33.9461, "lon": 151.1772, "tz": "Australia/Sydney"},
}


def leg(dep, arr):
    o, d = AIRPORTS[dep], AIRPORTS[arr]
    return {"origin_lat": o["lat"], "origin_lon": o["lon"], "origin_tz": o["tz"],
            "destination_lat": d["lat"], "destination_lon": d["lon"], "destination_tz": d["tz"]}


def at(zone, y, m, d, hh, mm):
    return dt.datetime(y, m, d, hh, mm, tzinfo=zone).timestamp()


# Tuesday 2026-10-13. Departure window 10:00-10:45 Chicago (earliest scheduled
# 10:30), arrival window 13:00-13:50 Los Angeles (earliest scheduled 13:40).
ORD_LAX = {"d": [600, 45, "s", 7], "a": [780, 50, "s", 7]}


class Window(unittest.TestCase):
    def test_in_the_air_is_in_window_with_progress(self):
        state, prog = rc.leg_time(ORD_LAX, leg("KORD", "KLAX"), at(CHI, 2026, 10, 13, 12, 0))
        self.assertEqual(state, rc.IN_WINDOW)
        # 10:30 CDT -> 13:40 PDT is 310 min; 12:00 CDT is 90 min in.
        self.assertAlmostEqual(prog, 90 / 310, places=6)

    def test_edges_are_inclusive_and_unpadded(self):
        L = leg("KORD", "KLAX")
        self.assertEqual(rc.leg_time(ORD_LAX, L, at(CHI, 2026, 10, 13, 10, 0))[0], rc.IN_WINDOW)
        self.assertEqual(rc.leg_time(ORD_LAX, L, at(LA, 2026, 10, 13, 13, 50))[0], rc.IN_WINDOW)
        # One minute either side: no padding any more.
        self.assertEqual(rc.leg_time(ORD_LAX, L, at(CHI, 2026, 10, 13, 9, 59))[0], rc.OUTSIDE_WINDOW)
        self.assertEqual(rc.leg_time(ORD_LAX, L, at(LA, 2026, 10, 13, 13, 51))[0], rc.OUTSIDE_WINDOW)

    def test_outside_ranks_like_no_times(self):
        self.assertEqual(rc._TIME_RANK[rc.OUTSIDE_WINDOW], rc._TIME_RANK[rc.NO_TIMES])
        self.assertLess(rc._TIME_RANK[rc.IN_WINDOW], rc._TIME_RANK[rc.NO_TIMES])

    def test_no_times(self):
        L = leg("KORD", "KLAX")
        now = at(CHI, 2026, 10, 13, 12, 0)
        self.assertEqual(rc.leg_time(None, L, now), (rc.NO_TIMES, None))
        self.assertEqual(rc.leg_time({}, L, now), (rc.NO_TIMES, None))
        self.assertEqual(rc.leg_time(ORD_LAX, L, None), (rc.NO_TIMES, None))
        self.assertEqual(rc.leg_time(ORD_LAX, {**L, "origin_tz": None}, now), (rc.NO_TIMES, None))
        self.assertEqual(rc.leg_time({"d": [9999, 5, "s", 1]}, L, now), (rc.NO_TIMES, None))

    def test_yesterdays_flight_still_counts(self):
        # Departs 22:00 Chicago, arrives 00:30 Los Angeles the next day.
        t = {"d": [1320, 30, "s", 5], "a": [1430, 40, "s", 5]}   # 23:50 LA + 40 lead = 00:30
        self.assertEqual(rc.leg_time(t, leg("KORD", "KLAX"), at(LA, 2026, 10, 14, 0, 20))[0], rc.IN_WINDOW)

    def test_window_crossing_midnight(self):
        # Start 23:40, 50 min long: to 00:30 the next day.
        t = {"d": [1420, 50, "s", 3], "a": [90, 60, "s", 3]}     # arrives ~02:10 LA
        L = leg("KORD", "KLAX")
        self.assertEqual(rc.leg_time(t, L, at(CHI, 2026, 10, 14, 0, 25))[0], rc.IN_WINDOW)

    def test_departure_only_estimates_arrival(self):
        L = leg("KORD", "KLAX")
        t = {"d": [600, 45, "s", 7]}
        self.assertEqual(rc.leg_time(t, L, at(CHI, 2026, 10, 13, 12, 0))[0], rc.IN_WINDOW)
        # ~2,800 km: block = 15 + 2800/780*60 ~ 230 min after 10:45 -> ~14:35 CDT.
        self.assertEqual(rc.leg_time(t, L, at(CHI, 2026, 10, 13, 15, 0))[0], rc.OUTSIDE_WINDOW)

    def test_arrival_only_estimates_departure(self):
        L = leg("KORD", "KLAX")
        t = {"a": [780, 50, "s", 7]}
        self.assertEqual(rc.leg_time(t, L, at(CHI, 2026, 10, 13, 12, 0))[0], rc.IN_WINDOW)
        self.assertEqual(rc.leg_time(t, L, at(CHI, 2026, 10, 13, 6, 0))[0], rc.OUTSIDE_WINDOW)


class Weekend(unittest.TestCase):
    # Weekday 10:00 departure; weekend 07:00. Weekday arrival 13:00 LA, weekend 10:00.
    T = {"d": [600, 45, "s", 5], "dw": [420, 45, "s", 2],
         "a": [780, 50, "s", 5], "aw": [600, 50, "s", 2]}

    def test_saturday_uses_the_weekend_windows(self):
        L = leg("KORD", "KLAX")
        self.assertEqual(rc.leg_time(self.T, L, at(CHI, 2026, 10, 17, 8, 30))[0], rc.IN_WINDOW)
        self.assertEqual(rc.leg_time(self.T, L, at(CHI, 2026, 10, 17, 13, 30))[0], rc.OUTSIDE_WINDOW)

    def test_weekday_ignores_them(self):
        L = leg("KORD", "KLAX")
        self.assertEqual(rc.leg_time(self.T, L, at(CHI, 2026, 10, 16, 8, 30))[0], rc.OUTSIDE_WINDOW)
        self.assertEqual(rc.leg_time(self.T, L, at(CHI, 2026, 10, 16, 12, 30))[0], rc.IN_WINDOW)

    def test_the_origins_day_decides_not_utc(self):
        # Friday 23:30 in Los Angeles is Saturday in UTC; LAX is the origin, so weekday.
        t = {"d": [1395, 30, "s", 5], "dw": [600, 30, "s", 2], "a": [440, 60, "s", 5], "aw": [1000, 60, "s", 2]}
        L = leg("KLAX", "KORD")
        now = at(LA, 2026, 10, 16, 23, 50)
        self.assertEqual(dt.datetime.fromtimestamp(now, dt.UTC).weekday(), 5)
        self.assertEqual(rc.leg_time(t, L, now)[0], rc.IN_WINDOW)

    def test_without_weekend_windows_d_and_a_are_every_day(self):
        L = leg("KORD", "KLAX")
        self.assertEqual(rc.leg_time(ORD_LAX, L, at(CHI, 2026, 10, 18, 12, 0))[0], rc.IN_WINDOW)


class Clocks(unittest.TestCase):
    def test_daylight_saving_end(self):
        # Sunday 2026-11-01, Chicago falls back at 02:00. 10:00 CST is 16:00Z.
        L = leg("KORD", "KLAX")
        start = dt.datetime(2026, 11, 1, 16, 0, tzinfo=dt.UTC).timestamp()
        self.assertEqual(rc.leg_time(ORD_LAX, L, start)[0], rc.IN_WINDOW)
        self.assertEqual(rc.leg_time(ORD_LAX, L, start - 60)[0], rc.OUTSIDE_WINDOW)

    def test_across_the_date_line(self):
        # Sydney 10:00 (AEDT) -> Los Angeles 06:00 the SAME calendar date.
        t = {"d": [600, 45, "s", 7], "a": [360, 50, "s", 7]}
        L = leg("YSSY", "KLAX")
        mid = dt.datetime(2026, 10, 14, 5, 0, tzinfo=dt.UTC).timestamp()   # 16:00 AEDT
        state, prog = rc.leg_time(t, L, mid)
        self.assertEqual(state, rc.IN_WINDOW)
        self.assertTrue(0.3 < prog < 0.7, prog)


class Choosing(unittest.TestCase):
    # Over Nebraska, westbound at cruise: ORD-LAX and MDW-LAX are both plausible,
    # both ahead, both high - geometry cannot choose.
    LAT, LON, ALT, COURSE = 41.0, -100.0, 36000.0, 255.0

    def choose(self, times, now, legs=(("KORD", "KLAX", 10), ("KMDW", "KLAX", 5))):
        got, verdict, _ = rc.choose_leg(list(legs), AIRPORTS.get, self.LAT, self.LON, self.ALT,
                                        self.COURSE, profile=rc.FILED, now=now, times=times)
        return got["origin_icao"], got["route_time_check"], verdict

    def test_in_window_beats_history(self):
        now = at(CHI, 2026, 10, 13, 12, 0)
        times = {("KMDW", "KLAX"): ORD_LAX}
        self.assertEqual(self.choose(times, now), ("KMDW", rc.IN_WINDOW, rc.PLAUSIBLE))

    def test_outside_is_not_held_against_a_leg(self):
        # ORD-LAX is outside its window, MDW-LAX has no times: history decides.
        # Before 2026-10-13 OUT_OF_WINDOW ranked below no times and MDW won.
        now = at(CHI, 2026, 10, 13, 20, 0)
        times = {("KORD", "KLAX"): ORD_LAX}
        self.assertEqual(self.choose(times, now), ("KORD", rc.OUTSIDE_WINDOW, rc.PLAUSIBLE))

    def test_published_attribute_values(self):
        now = at(CHI, 2026, 10, 13, 20, 0)
        _, state, _ = self.choose({}, now)
        self.assertEqual(state, rc.NO_TIMES)
        self.assertEqual((rc.IN_WINDOW, rc.NO_TIMES, rc.OUTSIDE_WINDOW),
                         ("in_window", "no_times", "outside_window"))


if __name__ == "__main__":
    unittest.main()
