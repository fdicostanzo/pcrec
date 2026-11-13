"""cost.py -- what exhaustive end enumeration costs on catastrophic patterns.

The enumeration forces PCRE2 through EVERY path (each end callout fails), so
its cost is the full backtracking tree, not the first-match cost. Per pattern
and subject length n: raw callouts, distinct ends, PCRE2 status, wall time,
next to a plain first-match run. Bounded by the oracle's callout cap and match
limit (both reported when they fire).
  python3 -B cost.py [MAXN]
"""
import sys
import time

import p2cb as p
import spanoracle as so

PATS = [("(a|a)*", "a"), ("(a*)*", "a"), ("(a|aa)*", "a"), ("(?:a+)+b", "a"), ("a*a*a*", "a"),
        ("(?:a|b)*", "ab")]


def main(maxn):
    o = so.Oracle(callout_cap=2_000_000, match_limit=50_000_000)
    print("%-10s %3s %10s %6s %-7s %9s %9s" % ("pattern", "n", "callouts", "ends", "status", "enum_ms", "first_ms"))
    for x, unit in PATS:
        for n in range(4, maxn + 1, 4):
            s = (unit * n)[:n]
            t0 = time.perf_counter()
            r = o.ends(x, s, 0)
            t1 = time.perf_counter()
            c = p.Code("(?:" + x + ")", 0)
            c.match(s.encode(), 0, p.ANCHORED)
            t2 = time.perf_counter()
            print("%-10s %3d %10d %6d %-7s %9.2f %9.3f" % (x, n, r["raw"], len(r["ends"]), r["status"],
                                                          1e3 * (t1 - t0), 1e3 * (t2 - t1)))
            if r["status"] != "ok":
                break
    s = "a" * 20
    small = so.Oracle(callout_cap=10_000, match_limit=1_000_000)
    r = small.ends("(a|a)*", s, 0)
    print("bounded: (a|a)* n=20 with callout_cap=10k -> status %s after %d callouts, ends so far %r"
          % (r["status"], r["raw"], r["ends"]))
    # the exact-span check on an UNREACHABLE end is the same full search:
    t0 = time.perf_counter()
    try:
        small.spans("(a|a)*b", s, 0, 20)
        print("spans unexpectedly finished")
    except p.Pcre2Error as e:
        print("bounded: spans('(a|a)*b', a^20, 0, 20) -> %s in %.1f ms" % (e, 1e3 * (time.perf_counter() - t0)))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 16)
