# DRILL S7: §12.5 E-CAL's two spellings, whole subject (its real mode: isodate is fixed-width, so searched = whole on
# these 10-character subjects), from rev 20's TEXT; labels by both engines.
import os, sys, itertools, calendar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eng import groups, VER, DIS, PROBES
print(VER)
ISO = r"(?<year>\d{4})-(?<month>\d\d)-(?<day>\d\d)"
pb = lambda t, lo, hi: lo <= int(t) <= hi                       # padded(between(lo, hi)) on \d\d text
leap = lambda y: calendar.isleap(int(y))
SUB = ["%s-%02d-%02d" % (y, m, d) for y in ("1900", "2000", "2023", "2024") for m in range(0, 14) for d in range(0, 33)]
n = differ = 0
for s in SUB:
    g = groups(ISO, s, ["year", "month", "day"])
    y, mo, d = g["year"], g["month"], g["day"]
    isodate = pb(mo, 1, 12) and pb(d, 1, 31)                    # E-WEEKDAY's isodate
    dim = calendar.monthrange(int(y), int(mo))[1] if isodate else None
    valid = isodate and int(d) <= dim                           # (day: padded(<=$dim))
    md = (pb(mo, 1, 1) or int(mo) in (3, 5, 7, 8, 10, 12)) and pb(d, 1, 31) or \
         int(mo) in (4, 6, 9, 11) and pb(d, 1, 30) or int(mo) == 2 and pb(d, 1, 28)
    valid2 = isodate and (md or (leap(y) and int(mo) == 2 and int(d) == 29))
    n += 1
    differ += valid != valid2
print("E-CAL valid vs valid2: %d of %d differ" % (differ, n))
for s in ("2024-02-29", "2023-02-29", "2024-04-31", "2024-13-01", "1900-02-29", "2000-02-29"):
    print("  ", s, [s in {x for x in SUB} and None])
print("engine disagreements:", DIS[0], "probes:", PROBES[0])
