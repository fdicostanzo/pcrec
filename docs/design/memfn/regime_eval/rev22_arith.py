#!/usr/bin/env python3
"""rev22_arith.py -- regime_eval.md rev 2.2's slot wall and POWER arithmetic.

Lane regeval5, 2026-10-14. No clock, no build: it reads rev22_population.tsv
(the ESTIMATED placement of the 177 real J1 questions, rev22_population.py)
and prints

  1. the cut ladder: the rev 2.1 plan on the REAL population, then each cut
     lever applied in turn, with groups, wall minutes and what each cut
     removes (cells per layer x regime, patterns, gates, controls);
  2. the power table per plan: for each gate population (layer x shipped
     filter, J1-open only, J2a not counted because its regime is unknown
     before E6), G0 per regime, G1 per fixed policy (|D(P)|), G2 per regime
     against its §3.0 power floor, G3's non-CB cell count, G4's scorable
     controls; each under the LOWER and UPPER regime readings;
  3. the two-window split of the lean plan.

Every input is a stated assumption (constants below). Usage:
  python3 -I -B rev22_arith.py [rev22_population.tsv]
"""
import hashlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TSV = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "rev22_population.tsv")

# ---- timing inputs (rev 2.1 §2.4, unchanged)
SEC = 0.95            # s per launch, streamed or >= 1 MiB
SEC_REP = 0.65        # s per launch, repeated 64 KiB
L = 3                 # LAUNCHES per judge group (Q-REVAL-8, ruled)
L_WIT = 5             # LAUNCHES per WITNESS group
F_RERUN = 0.20        # rerun budget share (+2 launches)
CHECK = 4.0           # s per group, check.sh + counting, no clock
B = 65536
SUBJ_BYTES = 64 * B   # one streamed subject (4 MiB)
SALT = b"rev2.2-estimate"

# ---- power inputs (all CHOSEN or proxies; printed with the table)
G0_CELLS, G0_PATS = 20, 5          # §3.1 G0
G1_D_MIN = 10                      # §3.0 power floor for G1
G3_MIN = 40                        # §3.0 power floor for G3
CB_SHARE = 6 / 36                  # F2: 6 of 36 (cell, layer) rows tie at k = 3 (rev2_arith_out part 1b)
NEFF = 0.5                         # n_eff / n: unequal walk weights (assumed)
R_NOISE = (0.010, 0.015, 0.0309)   # per-group NULL / walk, RMS: low, central, the p90 3.09%
# R_in proxies: regime_eval.md §8, PICKABLE, fit-repeated (grid2's streamed R_in replaces them at E4b)
R_IN = {("off", "S0"): (20.2, 16.2, 0.1), ("on", "S0"): (13.7, 1.3, 0.0),
        ("off", "S1"): (6.3, 2.0, 0.1), ("on", "S1"): (8.9, 0.1, 0.0)}
GSTAR = {"on": 4.5, "off": 11.0}   # R5 / R6 g* (regime_tables rev 0.4 §3, PF one-term / dig lower end)
REGS = ("DINGHY", "TUG", "LINER")


def load():
    rows = []
    with open(TSV) as f:
        head = None
        for line in f:
            if line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            if head is None:
                head = p
                continue
            rows.append(dict(zip(head, p)))
    for r in rows:
        for k in ("g", "bpm"):
            r[k] = float(r[k])
        for k in ("S", "pool", "runs", "b0", "b1", "b2", "b3", "medlong"):
            r[k] = int(r[k])
    return rows


def regime(Lv, g):
    if Lv < 64:
        return "DINGHY"
    return "TUG" if g < 18.5 else "LINER"


def sealed_ids(rt):
    """§2.8: rank RT patterns by sha256(salt || id); the bottom 30% (rounded up) are sealed."""
    k = math.ceil(0.3 * len(rt))
    ranked = sorted(rt, key=lambda r: hashlib.sha256(SALT + r["id"].encode()).hexdigest())
    return {r["id"] for r in ranked[:k]}


# ------------------------------------------------------------ groups per plan
def groups_for(r, plan):
    """-> list of (shape, bucket, regime_lower, regime_upper) for one RT pattern"""
    out = []
    g, bpm = r["g"], r["bpm"]
    whole = (regime(g, g), regime(max(g, bpm), g))
    for sh in plan["shapes"]:
        if sh == "all/W" and r["w"] != "y":
            continue
        if sh == "first/S" and plan.get("first_own_only") and r["mode"] != "first":
            continue
        if sh == "lines":
            if plan.get("lines_subset") and not plan["lines_subset"](r):
                continue
            tot = r["b0"] + r["b1"] + r["b2"] + r["b3"]
            shares = [r["b0"], r["b1"], r["b2"], r["b3"]]
            if plan["buckets"] == 3:              # {<32, 32-63, >=64}: C1's 14 edge dropped
                shares = [shares[0] + shares[1], shares[2], shares[3]]
            nb = len(shares)
            for k, sh_bytes in enumerate(shares):
                if tot == 0 or sh_bytes / tot * SUBJ_BYTES < B:
                    continue                      # under one buffer of such lines: no group
                if k < nb - 1:
                    out.append(("lines", k, "DINGHY", "DINGHY"))
                else:
                    ml = max(64, r["medlong"])
                    out.append(("lines", k, regime(min(g, ml), g),
                                regime(min(max(g, bpm), ml), g)))
            continue
        out.append((sh, None) + whole)
    return out


def pick(layer, filt, r, shape, bucket, nb):
    """regime_tables rev 0.4 §3, first match, S0/S1 (R3/R4/R8 not replayed)."""
    short = shape == "lines" and bucket is not None and bucket < nb - 2      # n < 32
    mid = shape == "lines" and bucket is not None and bucket == nb - 2       # 32 <= n < 64
    if layer == "off" and r["runs"] >= 2:
        return "walk"                                                         # R0
    if short:
        return "walk"                                                         # R1
    if mid:
        return "V1"                                                           # R2 (V1 if emitted)
    if filt == "S1" and r["g"] < GSTAR[layer]:
        return "walk"                                                         # R5 / R6
    return "A1" if layer == "on" else "V1"                                    # R7


LINER_C = 1                        # §3.1: cap(LINER) = R_in + 1 point; rev 2.2 proposes 2 (Q-REVAL-16)


def power(rt_open, plan, reading):
    """-> dict of statuses per (layer, filter)"""
    res = {}
    nb = plan["buckets"] if "lines" in plan["shapes"] else 4
    cells = []
    for r in rt_open:
        for sh, bk, rlo, rup in groups_for(r, plan):
            cells.append((r, sh, bk, rlo if reading == "lower" else rup))
    for layer in ("off", "on"):
        for filt in ("S0", "S1"):
            st = {}
            for i, reg in enumerate(REGS):
                sub = [c for c in cells if c[3] == reg]
                n, pats = len(sub), len({c[0]["id"] for c in sub})
                g0 = n >= G0_CELLS and pats >= G0_PATS
                st["G0 " + reg] = (n, pats, "ok" if g0 else "UNREACHED")
                cap = (R_IN[(layer, filt)][i] + LINER_C) if reg == "LINER" else \
                      (1.25 * R_IN[(layer, filt)][i] + 2)
                need = [2 * (4 * 100 * rn / cap) ** 2 for rn in R_NOISE]   # n >= need (n_eff = n/2)
                if not g0:
                    s2 = "UNREACHED"
                else:
                    s2 = "/".join("ok" if n >= nd else "UNDER" for nd in need)
                st["G2 " + reg] = (n, [round(x) for x in need], s2)
            pols = ["walk", "V1"] + (["A1"] if layer == "on" else [])
            for p in pols:
                d = sum(pick(layer, filt, c[0], c[1], c[2], nb) != p for c in cells)
                st["G1 " + p] = (d, "ok" if d >= G1_D_MIN else "UNDERPOWERED")
            ncb = round(len(cells) * (1 - CB_SHARE))
            st["G3"] = (ncb, "ok" if ncb >= G3_MIN else "UNDERPOWERED")
            res[(layer, filt)] = st
    return res, len(cells)


# ------------------------------------------------------------ wall
def wall(rt, plan):
    rows = []
    per = []
    for r in rt:
        per += groups_for(r, plan)
    by = {}
    for sh, *_ in per:
        by[sh] = by.get(sh, 0) + 1
    tot_s = 0
    for sh, n in sorted(by.items()):
        arms = plan["arms"][sh]
        t = n * arms * (L + 2 * F_RERUN) * SEC + n * CHECK
        rows.append((sh, n, arms, t / 60))
        tot_s += t
    j2 = plan["j2a"]
    t = j2 * plan["arms"]["all/S"] * (L + 2 * F_RERUN) * SEC + j2 * CHECK
    rows.append(("J2a (W)", j2, plan["arms"]["all/S"], t / 60))
    tot_s += t
    w = plan["witness"]
    t = w * plan["arms"]["witness"] * L_WIT * SEC + w * CHECK
    rows.append(("WITNESS", w, plan["arms"]["witness"], t / 60))
    tot_s += t
    rp = plan["rep64k"]
    t = rp * plan["arms"]["all/S"] * L * SEC_REP + rp * CHECK
    rows.append(("rep64k (ungated)", rp, plan["arms"]["all/S"], t / 60))
    tot_s += t
    fixed = plan["fixed_min"]
    return rows, tot_s / 60, fixed, len(per)


FULL = dict(name="FULL (rev 2.1 shapes, real population)",
            shapes=("first/S", "all/S", "all/W", "iter/S", "lines"), buckets=4,
            arms={"first/S": 6, "all/S": 8, "all/W": 8, "iter/S": 8, "lines": 6, "witness": 6},
            j2a=120, witness=35, rep64k=None, fixed_min=5 * 13)

LADDER = [
    ("cut 1: J1 iter/S out (emulated; S2/S3 never gate)",
     dict(shapes=("first/S", "all/S", "all/W", "lines"))),
    ("cut 2: J1 all/W out (S is the gating condition; W stays for J2a)",
     dict(shapes=("first/S", "all/S", "lines"))),
    ("cut 3: arms per layer 8/6 -> 5 (drop S1 = LV_X86_W16 and the kept V3/A3)",
     dict(arms={"first/S": 5, "all/S": 5, "lines": 5, "witness": 5})),
    ("cut 4: J2a 40 x 3 -> 20 patterns x 1 (W, the transferred bench subjects)",
     dict(j2a=20)),
    ("cut 5: rep64k on a 2-per-class subsample (ungated)",
     dict(rep64k=14)),
    ("cut 6: two windows; full anchor replay in window 1, drift anchors in window 2",
     dict(fixed_min=13 + 6)),
]
NOT_TAKEN = [
    ("lever: lines buckets 4 -> 3 (drop C1's 14 edge)", dict(buckets=3)),
    ("lever: first/S only where the question's own mode is `first`", dict(first_own_only=True)),
    ("lever: LAUNCHES 3 -> 2", None),
]


def fmt_power(res):
    out = []
    for (layer, filt), st in res.items():
        g0 = " ".join("%s %d/%dp %s" % (k[3:4], v[0], v[1], v[2][:3] if v[2] == "ok" else "UNR")
                      for k, v in st.items() if k.startswith("G0"))
        g1 = " ".join("%s:%d%s" % (k[3:], v[0], "" if v[1] == "ok" else "!UND")
                      for k, v in st.items() if k.startswith("G1"))
        g2 = " ".join("%s %s" % (k[3:4], v[2]) for k, v in st.items() if k.startswith("G2"))
        out.append("    %-3s %s | G0 %s | G1 |D| %s | G2 [r=1.0/1.5/3.09%%] %s | G3 %d%s" % (
            layer, filt, g0, g1, g2, st["G3"][0], "" if st["G3"][1] == "ok" else " UNDERPOWERED"))
    return "\n".join(out)


def main():
    rows = load()
    rt = [r for r in rows if r["est"] == "RT"]
    sealed = sealed_ids(rt)
    rt_open = [r for r in rt if r["id"] not in sealed]
    print("== 0. population (ESTIMATE, rev22_population.tsv): %d questions, %d RT, "
          "%d J1-open, %d J1-sealed" % (len(rows), len(rt), len(rt_open), len(sealed)))
    print("   sealed (stand-in salt; the prereg's salt re-draws it): %s" % " ".join(sorted(sealed)))
    print()

    plan = dict(FULL)
    plan["rep64k"] = len(rt)
    plans = [(plan["name"], dict(plan))]
    for label, ch in LADDER:
        plan = dict(plan)
        plan.update(ch)
        plan["name"] = label
        plans.append((label, plan))
    lean = plans[-1][1]

    print("== 1. the cut ladder (cumulative; minutes; J1 = all RT patterns, open + sealed)")
    print("   per group: arms x (L + 2 f_rerun) x %.2f s + %.1f s check; WITNESS L = %d; rep64k %.2f s, no reruns"
          % (SEC, CHECK, L_WIT, SEC_REP))
    prev = None
    for label, p in plans:
        units, tmin, fixed, ng = wall(rt, p)
        total = tmin + fixed
        print("  %-78s %4d J1 groups  %6.1f + %4.1f fixed = %6.1f min%s" % (
            label, ng, tmin, fixed, total,
            "" if prev is None else "  (%+.1f)" % (total - prev)))
        prev = total
    print()
    for label, p in (plans[0], plans[-1]):
        units, tmin, fixed, ng = wall(rt, p)
        print("  units, %s:" % label)
        for sh, n, arms, m in units:
            print("    %-18s %4d groups x %d arms  %6.1f min" % (sh, n, arms, m))
        print("    %-18s %21s %6.1f min" % ("fixed (anchors)", "", fixed))
        print("    %-18s %21s %6.1f min" % ("TOTAL", "", tmin + fixed))
    print()
    for label, ch in NOT_TAKEN:
        if ch is None:
            p = dict(lean)
            units, tmin, fixed, ng = wall(rt, p)
            t2 = sum(m for sh, n, a, m in units)   # rescale timed part by (2 + 0.4)/(3 + 0.4)
            print("  %-60s saves ~%.1f min of timing (not taken: Q-REVAL-8 ruled 3; cross-fit on one launch per fold)"
                  % (label, (1 - 2.4 / 3.4) * t2))
            continue
        p = dict(lean)
        p.update(ch)
        units, tmin, fixed, ng = wall(rt, p)
        u0, t0, f0, n0 = wall(rt, lean)
        print("  %-60s %+.1f min, %d -> %d J1 groups (not taken)" % (label, tmin - t0, n0, ng))
    print()

    print("== 1b. gated J1 cells per corpus class x regime (one layer x filter; open + sealed), lower / upper reading")
    classes = ["logs", "code", "prose", "structured", "markup", "nonenglish", "binary"]
    for label, p in (plans[0], ("LEAN", lean)):
        print("  %s" % label)
        print("    %-11s %5s  %-11s %-11s %-11s" % ("class", "cells", "DINGHY", "TUG", "LINER"))
        tots = [0, [0, 0], [0, 0], [0, 0]]
        for c in classes + ["ALL"]:
            cells = [gr for r in rt if c == "ALL" or r["cls"] == c for gr in groups_for(r, p)]
            line = "    %-11s %5d  " % (c, len(cells))
            for reg in REGS:
                line += "%4d / %-4d " % (sum(x[2] == reg for x in cells), sum(x[3] == reg for x in cells))
            print(line)
    print()

    print("== 2. power per plan (J1-open only; J2a adds cells of unknown regime)")
    print("   G0: cells/patterns per regime (D T L), floor %d cells from %d patterns" % (G0_CELLS, G0_PATS))
    print("   G1: |D(P)| = cells where the table's S0/S1 pick differs from always-P; floor %d" % G1_D_MIN)
    print("   G2: n >= 2 (4 r / cap)^2 at r = 1.0 / 1.5 / 3.09%% of walk; cap from §8 PICKABLE as the R_in proxy")
    print("   G3: non-CB cells = cells x (1 - %.2f); floor %d" % (CB_SHARE, G3_MIN))
    show = [plans[0], ("LEAN = " + plans[-1][0], plans[-1][1])]
    for label, ch in NOT_TAKEN[:2]:
        p3 = dict(lean)
        p3.update(ch)
        show.append(("LEAN + " + label + " (not taken)", p3))
    pl = dict(lean)
    pl["shapes"] = ("all/S",)
    show.append(("LEAN without lines (illustration: what lines buys)", pl))
    global LINER_C
    for label, p in show:
        for reading in ("lower", "upper"):
            res, n = power(rt_open, p, reading)
            print("  %s -- %s reading, %d gated cells per layer x filter" % (label, reading, n))
            print(fmt_power(res))
        print()
    LINER_C = 2
    for reading in ("lower", "upper"):
        res, n = power(rt_open, lean, reading)
        print("  LEAN with cap(LINER) = R_in + 2 (proposed) -- %s reading: G2 L %s" % (
            reading, " ".join("%s %s:%s" % (k[0], k[1], v["G2 LINER"][2] + " need " +
                                            "/".join(map(str, v["G2 LINER"][1])))
                               for k, v in res.items())))
    LINER_C = 1
    print()
    rt_sealed = [r for r in rt if r["id"] in sealed]
    for label, p in (plans[0], ("LEAN", lean)):
        for reading in ("lower", "upper"):
            res, n = power(rt_sealed, p, reading)
            st = res[("on", "S0")]
            print("  J1-sealed alone (final reading), %s, %s: %d cells; G0 %s; G3 %d %s" % (
                label[:28], reading, n,
                " ".join("%s %d/%dp %s" % (k[3:4], v[0], v[1], v[2]) for k, v in st.items()
                         if k.startswith("G0")), st["G3"][0], st["G3"][1]))
    print()

    print("== 3. LEAN split into two quiet-box windows")
    units, tmin, fixed, ng = wall(rt, lean)
    by = {u[0]: u[3] for u in units}
    w1 = by.get("all/S", 0) + by.get("first/S", 0) + by.get("WITNESS", 0) + \
        by.get("rep64k (ungated)", 0) + 13
    w2 = by.get("lines", 0) + by.get("J2a (W)", 0) + 6
    print("  window 1: anchors (full) 10 + J1 all/S %.1f + J1 first/S %.1f + WITNESS %.1f + rep64k %.1f"
          " + drift 3 = %.1f min" % (by.get("all/S", 0), by.get("first/S", 0), by.get("WITNESS", 0),
                                     by.get("rep64k (ungated)", 0), w1))
    print("  window 2: drift anchors 3 + J1 lines %.1f + J2a %.1f + drift 3 = %.1f min"
          % (by.get("lines", 0), by.get("J2a (W)", 0), w2))
    print("  total %.1f min; plus zen4-grid2's required ~56 min, separately (rev 2.1 §2.1)" % (w1 + w2))


if __name__ == "__main__":
    main()
