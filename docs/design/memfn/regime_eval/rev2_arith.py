#!/usr/bin/env python3
"""rev2_arith.py -- the arithmetic regime_eval.md rev 2 / rev 2.1 quotes.

Lane regeval3, 2026-10-14 (rev 2); lane regeval4 (rev 2.1: parts 1b and 2 with
and without the OPTIONAL perf passes, D166 addendum 1). No clock, no build, no
new measurement: it reads one finished file and prints arithmetic.

  1. [r1 T7] the consumer-bound condition-2 spread over the FIXED arm set
     K = {walk, V1, A1} (walk plus the arms every gated cell times at both
     layers), from F2's counts (docs/dev/lanes/gridread/f2_counts.txt, the
     B-7-corrected source), beside rev 1's all-arms spread; and the
     condition-3b reading on the cycles column (pick under SIMD-off S0 is R7's
     V1; under SIMD-on S0 it is R7's A1).
  1b. [D166a1] the TIMING-ONLY consumer-bound rule: spread of cycles/pass over K
     in NULL units, the CB reading at k = 2, 3, 4, and its agreement with the
     (now optional) perf-misses reading.
  2. [r1 T12] the judge wall estimate, as a formula with every input named,
     and the five-slot split.

Usage: python3 -I -B rev2_arith.py [F2_COUNTS]   (prints to stdout)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
F2 = os.path.join(HERE, "..", "..", "..", "dev", "lanes", "gridread", "f2_counts.txt")

K = ("walk", "V1", "A1")
NULL_RATIO = 0.0309          # gridread's 3.09% (Zen 4 grid1), the cycles proxy for NULL_cell


def load(path):
    rows = {}
    with open(path) as f:
        for line in f:
            if line.startswith("#") or line.startswith("cell") or line.startswith("f2perf"):
                continue
            p = line.split()
            if len(p) != 8:
                continue
            cell, subj, arm = p[0], p[1], p[2]
            rows.setdefault((cell, subj), {})[arm] = {
                "cycles": float(p[3]), "misses_kib": float(p[7])}
    return rows


def spread(arms, names):
    v = [arms[a]["misses_kib"] for a in names]
    return (max(v) - min(v)) / arms["walk"]["misses_kib"]


def part1(path):
    rows = load(path)
    print("== 1. consumer-bound condition 2 (misses/KiB spread / walk misses/KiB)")
    print("%-8s %-9s %9s %10s %10s  %-26s %-26s" % (
        "cell", "subject", "walk m/K", "spread K", "spread all",
        "SIMD-off: V1 pick vs best", "SIMD-on: A1 pick vs best"))
    for (cell, subj), arms in sorted(rows.items()):
        sk = spread(arms, K)
        sa = spread(arms, tuple(arms))
        w = arms["walk"]["cycles"]
        # SIMD-off layer arms {walk, V1}; S0 pick there is R7 = V1.
        best_off = min(arms[a]["cycles"] for a in ("walk", "V1"))
        d_off = (arms["V1"]["cycles"] - best_off) / w
        # SIMD-on layer arms {walk, V1, A1}; S0 pick there is R7 = A1.
        best_on = min(arms[a]["cycles"] for a in ("walk", "V1", "A1"))
        d_on = (arms["A1"]["cycles"] - best_on) / w
        c3_off = (w - best_off) / w
        c3_on = (w - best_on) / w

        def tag(c3, d3b):
            return "c3 %+5.1f%% 3b %+5.1f%% %s" % (
                100 * c3, 100 * d3b,
                "ok" if (c3 <= NULL_RATIO and d3b <= NULL_RATIO) else "--")
        print("%-8s %-9s %9.1f %9.1f%% %9.1f%%  %-26s %-26s" % (
            cell, subj, arms["walk"]["misses_kib"], 100 * sk, 100 * sa,
            tag(c3_off, d_off), tag(c3_on, d_on)))
    print("  cond 1: walk misses/KiB >= 50; cond 2: spread K <= 20%; "
          "cond 3/3b: (walk-best)/walk and (pick-best)/walk <= NULL (3.09% of walk, cycles proxy)")
    print("  'ok' = conditions 3 and 3b hold for that layer; CB needs all four.")
    print()


def part1b(path):
    """Timing-only CB (D166 add. 1): c3, spread over K <= k*NULL, 3b; vs perf."""
    rows = load(path)
    print("== 1b. timing-only consumer-bound rule, cycles/pass as the ns proxy")
    print("   NULL proxy = %.2f%% of walk (gridread's grid p90 A/A; a cell's NULL_c is >= this)" %
          (100 * NULL_RATIO))
    ks = (2, 3, 4)
    print("%-8s %-9s %9s %8s | %s | %s" % (
        "cell", "subject", "tspread", "in NULL",
        "layer: timing-CB at k=2,3,4", "perf-CB (misses>=50/KiB, spread K<=20%)"))
    tally = {k: [0, 0] for k in ks}          # [CB count, disagreements with perf]
    n = 0
    for (cell, subj), arms in sorted(rows.items()):
        w = arms["walk"]["cycles"]
        cy = [arms[a]["cycles"] for a in K]
        ts = (max(cy) - min(cy)) / w
        for layer, names, pick in (("off", ("walk", "V1"), "V1"),
                                   ("on", ("walk", "V1", "A1"), "A1")):
            best = min(arms[a]["cycles"] for a in names)
            c3 = (w - best) / w <= NULL_RATIO
            c3b = (arms[pick]["cycles"] - best) / w <= NULL_RATIO
            perf = (arms["walk"]["misses_kib"] >= 50 and spread(arms, K) <= 0.20
                    and c3 and c3b)
            out = []
            n += 1
            for k in ks:
                t = c3 and c3b and ts <= k * NULL_RATIO
                tally[k][0] += t
                tally[k][1] += (t != perf)
                out.append("CB" if t else "--")
            print("%-8s %-9s %8.1f%% %7.1f  %-3s %s  perf %s" % (
                cell, subj, 100 * ts, ts / NULL_RATIO, layer, " ".join(out),
                "CB" if perf else "--"))
    for k in ks:
        print("  k=%d: timing-CB on %d of %d (cell, layer) rows; disagrees with perf-CB on %d" %
              (k, tally[k][0], n, tally[k][1]))
    print()


# ---------------------------------------------------------------- part 2
# Inputs (regime_eval.md rev 2 §2.4; every one is a stated assumption):
SEC_STREAM = 0.95      # s per launch, streamed or >= 1 MiB subject (grid1 §3)
SEC_REP = 0.65         # s per launch, repeated 64 KiB subject (grid1 §3)
L = 3                  # LAUNCHES per judge group (Q-REVAL-8)
L_WIT = 5              # LAUNCHES per WITNESS group (Q-REVAL-8)
F_RERUN = 0.20         # pre-registered budget share of groups that get +2 launches (M-9); an estimate
PERF_ROW = 0.6         # s per perf arm row, 3 launches (F2: 72 rows in 43 s)
PERF_ARMS = 3          # perf only on K = {walk, V1, A1}
CHECK_PER_GROUP = 36 * 60 / 540   # s; rev 1's 3 x 12 min over its 540 groups, scaled per group
SLOT_FIXED = 13 * 60   # s per slot: anchor replay ~10 min (M-8) + end-of-slot drift re-time ~3 min
N_PAT = 70             # J1 RT patterns (20 per class x ~3.5 classes, rev 1)
N_J2A = 40             # J2a patterns, 3 groups each (rev 1)
ARMS_ALL = 8           # all/iter groups: rev 1's 7 + walk#c
ARMS_FIRST = 6         # first/lines groups: rev 1's 5 + walk#c
BUCKETS = 4            # lines buckets: N-edges of the active set {32, 64} U C1's swapped {14, 32}
N_WIT = 35             # WITNESS groups: 7 replay-scorable rows (R0 R1 R2 RD2 R5 R6 R7) x 5
ARMS_WIT = 6


def launches(groups, arms, l, rerun=True):
    eff = l + (2 * F_RERUN if rerun else 0)
    return groups * arms * eff


def unit(name, groups, arms, sec, l=L, rerun=True, with_perf=True):
    timed = launches(groups, arms, l, rerun) * sec
    perf = groups * PERF_ARMS * PERF_ROW if with_perf else 0
    check = groups * CHECK_PER_GROUP
    return (name, groups, timed / 60, perf / 60, check / 60, (timed + perf + check) / 60)


def part2(with_perf=True):
    unit_ = lambda *a, **k: unit(*a, with_perf=with_perf, **k)
    units = [
        unit_("J1 first/S", N_PAT, ARMS_FIRST, SEC_STREAM),
        unit_("J1 all/S", N_PAT, ARMS_ALL, SEC_STREAM),
        unit_("J1 all/W", N_PAT, ARMS_ALL, SEC_STREAM),
        unit_("J1 iter/S", N_PAT, ARMS_ALL, SEC_STREAM),
    ] + [unit_("J1 lines/S b%d" % (b + 1), N_PAT, ARMS_FIRST, SEC_STREAM)
         for b in range(BUCKETS)] + [
        unit_("J2a", N_J2A * 3, ARMS_ALL, SEC_STREAM),
        unit_("rep64k column", N_PAT, ARMS_ALL, SEC_REP, rerun=False),
        unit_("WITNESS", N_WIT, ARMS_WIT, SEC_STREAM, l=L_WIT, rerun=False),
    ]
    print("== 2. judge wall estimate (minutes), %s" % (
        "WITH the optional perf pass" if with_perf else "WITHOUT the optional perf pass (the required path)"))
    print("%-16s %6s %8s %6s %6s %8s" % ("unit", "groups", "timed", "perf", "check", "total"))
    tot = [0, 0, 0, 0, 0]
    by = {}
    for name, g, t, p, c, s in units:
        print("%-16s %6d %8.1f %6.1f %6.1f %8.1f" % (name, g, t, p, c, s))
        for i, v in enumerate((g, t, p, c, s)):
            tot[i] += v
        by[name] = s
    print("%-16s %6d %8.1f %6.1f %6.1f %8.1f" % ("SUM", *tot))
    slots = {
        "J-a1": ("J1 all/S", "J1 all/W"),
        "J-a2": ("J1 iter/S", "J1 first/S"),
        "J-a3": ("J1 lines/S b1", "J1 lines/S b2", "WITNESS"),
        "J-a4": ("J1 lines/S b3", "J1 lines/S b4", "rep64k column/2"),
        "J-b": ("J2a", "rep64k column/2"),
    }
    print("five slots (unit totals + %d min fixed per slot):" % (SLOT_FIXED // 60))
    grand = 0
    for s, us in slots.items():
        v = 0
        for u in us:
            v += by[u[:-2]] / 2 if u.endswith("/2") else by[u]
        v += SLOT_FIXED / 60
        grand += v
        print("  %-5s %6.1f  %s" % (s, v, " + ".join(us)))
    print("  total %6.1f min (%.1f h)" % (grand, grand / 60))


if __name__ == "__main__":
    f2 = sys.argv[1] if len(sys.argv) > 1 else F2
    part1(f2)                 # OPTIONAL corroboration (needs perf counters)
    part1b(f2)                # the rule (timing only)
    part2(with_perf=False)    # the required path
    print()
    part2(with_perf=True)     # with the optional perf passes
