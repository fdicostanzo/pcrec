#!/usr/bin/env python3
"""analyze.py JOINT_TSV [POP_TSV] -- summarise joint.py's output: population
accounting, per-subject rejection distribution, model-vs-measured gap, the
bench-derived rows, and the absolute-density figures the D77 verdict reads."""
import csv
import math
import os
import statistics as st
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def q(xs, p):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    k = (len(xs) - 1) * p
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def population():
    import joint as J
    tot = pos = sized = 0
    global REASONS
    REASONS = defaultdict(int)
    for line in open(os.path.join(HERE, "population.tsv"), encoding="utf-8"):
        rid, enc, pat = line.rstrip("\n").split("\t")
        pb = pat.encode("utf-8", "surrogateescape")
        occs = J.sc.classify_pattern(pb) or []
        tot += 1
        if any(o["polarity"] == "+" and o["shape"] in ("b", "c", "d") for o in occs):
            pos += 1
            try:
                pl = J.plan(pb)
                if pl[3]:
                    sized += 1
                else:
                    REASONS[",".join(sorted(set(pl[4]))) or "none"] += 1
            except J.Refused:
                REASONS["refused"] += 1
    return tot, pos, sized


def main():
    path = sys.argv[1]
    rows = list(csv.DictReader(open(path), delimiter="\t"))
    tot, pos, sized = population()
    print("POPULATION: %d still-VM rows; %d carry a positive multi-char lookaround "
          "(census: 143); %d of those have >=1 applicable one-char condition\n"
          % (tot, pos, sized))
    print("patterns with NO applicable condition, by note:", dict(REASONS), "\n")
    by = defaultdict(list)
    for r in rows:
        by[r["subject"]].append(r)
    print("%-20s %5s %6s %5s | %6s %6s %6s %6s %6s | pooled  unsound nested-viol"
          % ("subject", "cells", "dormnt", "live", "min", "p25", "med", "p75", "max"))
    for sj, rs in sorted(by.items()):
        live = [r for r in rs if r["c0"] not in ("", "0")]
        rej = [float(r["rej"]) for r in live]
        pooled = (sum(int(r["c0"]) - int(r["c1"]) for r in live)
                  / max(1, sum(int(r["c0"]) for r in live)))
        print("%-20s %5d %6d %5d | %6.3f %6.3f %6.3f %6.3f %6.3f | %.3f   %d       %d"
              % (sj, len(rs), len(rs) - len(live), len(live), min(rej), q(rej, .25),
                 st.median(rej), q(rej, .75), max(rej), pooled,
                 sum(1 for r in rs if r["sound"] == "0"),
                 sum(1 for r in rs if r["nested"] == "0")))
    print()

    # rejection buckets among live cells, byte rows, per subject
    print("REJECTION BUCKETS (live byte-encoding cells; share of cells)")
    def bucket(x):
        return (0 if x == 0 else 1 if x < .25 else 2 if x < .5 else 3 if x < .75
                else 5 if x == 1 else 4)
    names = ["0 (no effect)", "(0,25%)", "[25,50%)", "[50,75%)", "[75,100%)", "100% (all)"]
    print("%-20s " % "subject" + " ".join("%13s" % n for n in names))
    for sj, rs in sorted(by.items()):
        live = [float(r["rej"]) for r in rs if r["enc"] == "byte" and r["c0"] not in ("", "0")]
        cnt = [sum(1 for x in live if bucket(x) == b) for b in range(6)]
        print("%-20s " % sj + " ".join("%13s" % ("%d (%.0f%%)" % (c, 100.0 * c / len(live))) for c in cnt))
    print()

    # NARROW subset vs rest, byte rows
    print("NARROW-111 SUBSET (step-0 narrow==y on every condition), live byte cells")
    for sj, rs in sorted(by.items()):
        for label, sel in (("narrow", "y"), ("wide", "n")):
            live = [float(r["rej"]) for r in rs if r["enc"] == "byte" and r["narrow"] == sel
                    and r["c0"] not in ("", "0")]
            if live:
                print("  %-20s %-6s n=%3d median %.3f mean %.3f" % (sj, label, len(live), st.median(live), st.mean(live)))
    print()

    # FALSE-CANDIDATE removal
    print("FALSE-CANDIDATE REMOVAL (share of candidates that are NOT true starts which the "
          "condition removes), live byte cells with >=1 false candidate")
    for sj, rs in sorted(by.items()):
        fr = [float(r["false_rem"]) for r in rs if r["enc"] == "byte" and r["false_rem"] not in ("",)]
        if fr:
            pooled_c = sum(int(r["c0"]) - int(r["c1"]) for r in rs if r["false_rem"] not in ("",) and r["enc"] == "byte")
            pooled_f = sum(int(r["c0"]) - int(r["t"]) for r in rs if r["false_rem"] not in ("",) and r["enc"] == "byte")
            print("  %-20s n=%3d median %.3f pooled %.3f  (removed %d of %d false)"
                  % (sj, len(fr), st.median(fr), pooled_c / pooled_f, pooled_c, pooled_f))
    print()

    # MODEL vs MEASURED (survival fraction c1/c0 vs product of selectivities)
    print("MODEL vs MEASURED survival (fraction of candidates the condition PASSES), "
          "live byte cells with a model value")
    for sj, rs in sorted(by.items()):
        pairs = [(float(r["model_pass"]), float(r["meas_pass"])) for r in rs
                 if r["enc"] == "byte" and r["model_pass"] not in ("",) and r["meas_pass"] not in ("",)
                 and int(r["c0"]) > 0]
        if not pairs:
            continue
        mrej = [1 - m for m, _ in pairs]
        arej = [1 - a for _, a in pairs]
        err = [abs(x - y) for x, y in zip(mrej, arej)]
        over = sum(1 for m, a in pairs if m > a + 0.05)   # model too pessimistic (predicts more survivors)
        under = sum(1 for m, a in pairs if m < a - 0.05)  # model too optimistic (predicts fewer)
        print("  %-20s n=%3d  model rej median %.3f | measured rej median %.3f | "
              "mean|gap| %.3f | model too optimistic on %d, too pessimistic on %d, within 5pt on %d"
              % (sj, len(pairs), st.median(mrej), st.median(arej), st.mean(err),
                 under, over, len(pairs) - over - under))
    print()

    # bench-derived rows
    print("BENCH-DERIVED ROWS (id not under tests/)")
    for r in rows:
        if not r["id"].startswith("tests/") and r["subject"] in (
                "syntax-t-256k.bin", "t-256k.bin", "decisions.md"):
            kb = int(r["n_bytes"]) / 1024.0
            print("  %-10s %-38s cond=%-24s c0=%-6s c1=%-6s true=%-5s rej=%s falserem=%s removed/KB=%.2f"
                  % (r["subject"][:9], r["id"], r["conds"][:24], r["c0"], r["c1"], r["t"],
                     r["rej"] or "-", r["false_rem"] or "-",
                     (int(r["c0"]) - int(r["c1"])) / kb if r["c1"] else 0.0))
    print()

    # ABSOLUTE DENSITY: removed / false candidates per KB, byte rows
    print("ABSOLUTE DENSITY (per KB of subject), live byte cells")
    for sj, rs in sorted(by.items()):
        live = [r for r in rs if r["enc"] == "byte" and r["c0"] not in ("", "0")]
        kb = int(live[0]["n_bytes"]) / 1024.0
        rem = [(int(r["c0"]) - int(r["c1"])) / kb for r in live]
        fal = [(int(r["c0"]) - int(r["t"])) / kb for r in live]
        print("  %-20s removed/KB: median %.2f p75 %.2f max %.1f | cells >=1/KB: %d/%d  >=3/KB: %d/%d"
              " | false/KB median %.2f"
              % (sj, st.median(rem), q(rem, .75), max(rem), sum(1 for x in rem if x >= 1), len(rem),
                 sum(1 for x in rem if x >= 3), len(rem), st.median(fal)))
    print()

    # prefilter stamp mix
    mix = defaultdict(int)
    for r in by[sorted(by)[0]]:
        mix[(r["prefilter"], r["req_byte"] == "none")] += 1
    print("PREFILTER STAMPS (RX_VM_PREFILTER, req_byte none?) over the measured patterns:",
          dict(mix))


if __name__ == "__main__":
    main()
