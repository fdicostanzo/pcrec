"""sweep.py -- independent cross-checks of the oracle over generated patterns.

  python3 -B sweep.py cross N L SEED   # N patterns x every {a,b} string of length <= L
  python3 -B sweep.py laws  N L SEED   # N (X,Y,Z) triples, same subjects

cross, per (pattern, subject, start i), the oracle's end list against:
  re     -- the end SET from python `re.fullmatch` on s[i:j] (context-free subset)
  ref    -- the end ORDER from refmatch.py's own backtracker (no PCRE2)
  la     -- the end ORDER rebuilt by PCRE2 WITHOUT callouts (lookahead_order)
  spans  -- the callout exact-span check, and the callout-free lookahead check,
            for every j, against membership in the end list
  opt    -- the end list compiled WITHOUT the NO_OPT options
laws, per triple and subject:
  XX     -- X & X  == PCRE2's own unanchored search of X (no callout)
  ALL    -- X & (?s:.*) == the same search
  COMM   -- X & Y vs Y & X: same leftmost START (asserted: the span sets are
            symmetric) and same REPORTED match (counted: the leaning rule is not)
  DIST   -- ends(Y|Z) == ends(Y) U ends(Z) as sets, and X & (Y|Z) == the
            leaning rule over that union
  AB     -- implementation A (and_sets) == implementation B (and_inline)
"""
import itertools
import os
import random
import re
import sys
import time

import p2cb as p
import refmatch
import spanoracle as so


def subjects(L, alphabet="ab"):
    for n in range(L + 1):
        for t in itertools.product(alphabet, repeat=n):
            yield "".join(t)


def plain_search(x, s):
    rc, ov = p.Code("(?:" + x + ")", 0).match(s.encode(), 0, 0)
    return ov[0] if rc > 0 else None


def cross(N, L, seed):
    rng = random.Random(seed)
    o, oo = so.Oracle(), so.Oracle(no_opt=False)
    cnt = {k: [0, 0] for k in ("re", "ref", "la", "spans", "laspans", "opt")}
    bad = []
    subs = list(subjects(L))
    slow = []
    for _ in range(N):
        x = refmatch.gen_pattern(rng, depth=2, caps=rng.random() < 0.5)
        t0 = time.time()
        pyre = re.compile(x, re.S)
        for s in subs:
            for i in range(len(s) + 1):
                got = o.ends(x, s, i)
                assert got["status"] == "ok", (x, s, i, got)
                e = got["ends"]
                res = {
                    "re": set(e) == {j for j in range(i, len(s) + 1) if pyre.fullmatch(s, i, j)},
                    "ref": e == refmatch.ends(x, s, i),
                    "la": e == o.lookahead_order(x, s, i),
                    "spans": all(o.spans(x, s, i, j) == (j in e) for j in range(i, len(s) + 1)),
                    "laspans": all(o.lookahead_spans(x, s, i, j) == (j in e) for j in range(i, len(s) + 1)),
                    "opt": e == oo.ends(x, s, i)["ends"],
                }
                for k, ok in res.items():
                    cnt[k][0 if ok else 1] += 1
                    if not ok and len(bad) < 10:
                        bad.append((k, x, s, i, e))
        dt = time.time() - t0
        if os.environ.get("ANDSPIKE_PROGRESS"):
            print("  %.2fs %s" % (dt, x), file=sys.stderr, flush=True)
        slow.append((dt, x))
    for dt, x in sorted(slow)[-3:]:
        bad.append(("slowest %.2fs" % dt, x))
    return cnt, bad


def lean(order, accept):
    for j in order:
        if j in accept:
            return j
    return None


def laws(N, L, seed):
    rng = random.Random(seed)
    o = so.Oracle()
    cnt = {k: [0, 0] for k in ("XX", "ALL", "COMMstart", "COMMreport", "DISTset", "DISTreport", "AB")}
    bad = []
    subs = list(subjects(L))

    def tally(k, ok, *info):
        cnt[k][0 if ok else 1] += 1
        if not ok and len(bad) < 10:
            bad.append((k,) + info)

    for _ in range(N):
        x, y, z = (refmatch.gen_pattern(rng, depth=2) for _ in range(3))
        yz = "(?:%s)|(?:%s)" % (y, z)
        for s in subs:
            ps = plain_search(x, s)
            ps = tuple(ps) if ps else None
            tally("XX", o.and_sets(x, x, s) == ps, x, s)
            tally("ALL", o.and_sets(x, "(?s:.*)", s) == ps, x, s)
            xy, yx = o.and_sets(x, y, s), o.and_sets(y, x, s)
            tally("COMMstart", (xy is None) == (yx is None) and (xy is None or xy[0] == yx[0]), x, y, s, xy, yx)
            tally("COMMreport", xy == yx, x, y, s, xy, yx)
            first = None
            for i in range(len(s) + 1):
                ey, ez = o.ends(y, s, i)["ends"], o.ends(z, s, i)["ends"]
                eyz = o.ends(yz, s, i)["ends"]
                tally("DISTset", set(eyz) == set(ey) | set(ez), y, z, s, i)
                if first is None:
                    j = lean(o.ends(x, s, i)["ends"], set(ey) | set(ez))
                    if j is not None:
                        first = (i, j)
            tally("DISTreport", o.and_sets(x, yz, s) == first, x, yz, s)
            tally("AB", o.and_sets(x, y, s) == o.and_inline(x, y, s), x, y, s)
    return cnt, bad


if __name__ == "__main__":
    part, N, L, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    t0 = time.time()
    cnt, bad = (cross if part == "cross" else laws)(N, L, seed)
    dt = time.time() - t0
    print("sweep %s N=%d L=%d seed=%d pcre2=%s  %.1fs" % (part, N, L, seed, p.version(), dt))
    for k, (ok, ng) in cnt.items():
        print("  %-11s agree %7d  differ %5d" % (k, ok, ng))
    for b in bad:
        print("  DIFF", b)
