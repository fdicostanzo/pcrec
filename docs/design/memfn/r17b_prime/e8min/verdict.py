#!/usr/bin/env python3
"""e8min/verdict.py -- B4's kit-tier verdict (E8), plan.md section 2 "verdict script" items (a)-(g).

  verdict.py CELLS_TSV EXPECTED_LOSSES_MD CENSUS_TSV      (CELLS_TSV: readslot.py cells' output)

Prints one block per item and ends with `E8 VERDICT: PASS | REFUTED | INVALID | UNDERPOWERED`; exit 0 only on PASS.
Precedence: INVALID (the window cannot see a loss) > REFUTED > UNDERPOWERED > PASS (FINDINGS are reported, not gating).
Constants are regime_eval section 3.0a's rows, copied; each is CHOSEN or UNMEASURED as labelled there.
"""
import collections
import math
import re
import sys

EP01, EP05, EP07, EP08 = 2.0, 40, 20, 5          # G1's 2 (x N), G3 min cells, G0 min cells, G0 min patterns
EP15, EP17, EP18, EP19 = 3.0, 0.25, 0.05, 0.25   # G3: floor in w_call units, walk fraction, rate, budget fraction
W_CALL = 16.0                                    # EP16, ns per DINGHY call, "about 16 on Zen 4" (UNMEASURED here)
REG_MISS, REG_GAP = 0.1, 8                       # r17b_prime 9.2a: walk misses per landing < 0.1, mean gap <= 8 B
NULLCTL_MIN = 0.8                                # share of cells where walk#b must read N (UNMEASURED DEFAULT)
LOSER_CONTROLS = [("LC1", "word-eq", "g2-f3-word-eq-n1m-ginf-Lnone-S", 13.7),    # b4prep/f3rr.md, (2,0,1)
                  ("LC2", "quad", "g2-f3-quad-n1m-ginf-Lnone-S", 41.3)]          # (3,1,0)


def read_cells(path):
    rows = [ln.rstrip("\n").split("\t") for ln in open(path)]
    return [dict(zip(rows[0], r)) for r in rows[1:]]


def expected_list(path):
    """{(family, subject): (id, grid2 pct, 2x line pct)} from expected_losses.md's EL and SS rows (the one source)."""
    out = {}
    for ln in open(path, encoding="utf-8"):
        c = [x.strip() for x in ln.split("|")]
        if len(c) < 7 or not re.fullmatch(r"(EL[0-9]+|SS[0-9]+[a-e]?)", c[1].split()[0] if c[1] else ""):
            continue
        if "B5" in c[1]:
            continue                                   # EL11 is scored at B5, not B4
        i = c[1].split()[0]
        fam = re.match(r"(dig|dfa-hat|bounded)", c[2])
        g = re.search(r"g = ([0-9]+|inf)", c[2])
        L = re.search(r"L = ([0-9]+k?)", c[2])
        pct = re.search(r"\+([0-9.]+)%", c[4])
        if not (fam and g and L and pct):
            raise SystemExit("verdict: cannot parse expected-loss row: " + ln.strip())
        gg = g.group(1)
        tail = "-reg" if "`reg`" in c[2] or " reg" in c[2] else ("-u" if gg not in ("2", "inf") else "")
        subj = "g2-%s-n64k-g%s-L%s%s-S" % (fam.group(1), gg, L.group(1), tail)
        if (fam.group(1), subj) in out:                # SS1 is EL5's cell: one cell, scored once
            continue
        out[(fam.group(1), subj)] = (i, float(pct.group(1)), 2 * float(pct.group(1)))
    return out


def main():
    cells = read_cells(sys.argv[1])
    exp = expected_list(sys.argv[2])
    for c in ("nbytes", "matches"):
        for r in cells:
            r[c] = int(r[c])
    for r in cells:
        for c in ("walk_ns", "v1_ns", "floor_ns", "aac_ns", "delta_pct"):
            r[c] = float(r[c])
    movers = {ln.rstrip("\n").split("\t")[12] for ln in open(sys.argv[3], encoding="utf-8")
              if not ln.startswith("#") and ln.split("\t")[7] == "1"}
    j1 = [r for r in cells if r["set"] == "J1"]
    an = {r["subject"]: r for r in cells if r["set"] == "AN"}
    invalid, refute, under, findings = [], [], [], []

    print("== anchors and positive controls (INVALID if one does not read R)")
    for (fam, subj), (i, pct, line) in sorted(exp.items(), key=lambda kv: kv[1][0]):
        r = an.get(subj)
        if r is None:
            invalid.append("%s: cell %s was not timed" % (i, subj)); print("  %-6s MISSING %s" % (i, subj)); continue
        d = r["delta_pct"]
        tag = "R" if r["verdict"] == "R" else r["verdict"]
        print("  %-6s %-32s V1 %+6.1f%% %s (grid2 +%.1f%%, 2x line +%.1f%%)" % (i, subj, d, tag, pct, line))
        if tag != "R":
            invalid.append("%s reads %s, not R" % (i, tag))
        elif d > line:
            findings.append("%s beyond its 2x line: %+.1f%% > %.1f%%" % (i, d, line))
    for i, fam, subj, pct in LOSER_CONTROLS:
        r = an.get(subj)
        if r is None:
            invalid.append("%s: cell %s was not timed" % (i, subj)); print("  %-6s MISSING %s" % (i, subj)); continue
        tag = r["verdict"]
        print("  %-6s %-32s V1 %+6.1f%% %s (f3rr +%.1f%%, 2x line +%.1f%%)" % (i, subj, r["delta_pct"], tag, pct, 2 * pct))
        if tag != "R":
            invalid.append("%s reads %s, not R" % (i, tag))
        elif r["delta_pct"] > 2 * pct:
            findings.append("%s beyond its 2x line: %+.1f%% > %.1f%%" % (i, r["delta_pct"], 2 * pct))

    print("== null control (walk#b against walk, held-out floor)")
    nulls = [r for r in cells if r["nullb"] == "N"]
    share = len(nulls) / len(cells) if cells else 0.0
    print("  walk#b reads N on %d of %d cells (%.2f; bar %.2f, UNMEASURED DEFAULT)" % (len(nulls), len(cells), share, NULLCTL_MIN))
    if share < NULLCTL_MIN:
        invalid.append("null control: walk#b reads N on only %.2f of cells" % share)

    print("== (e) G0 counts")
    npat = len({r["id"] for r in j1})
    print("  J1 cells %d (floor EP07 %d), patterns %d (floor EP08 %d), movers in the census %d" % (len(j1), EP07, npat, EP08, len(movers)))
    if len(j1) < EP07 or npat < EP08:
        under.append("G0: %d cells / %d patterns below %d / %d" % (len(j1), npat, EP07, EP08))

    print("== (a) per mover cell: a loss outside the expected-loss classes refutes (9.4)")
    nlose = 0
    expected_j1 = []
    for r in j1:
        if r["verdict"] != "R":
            continue
        nlose += 1
        gap = r["nbytes"] / r["matches"] if r["matches"] else math.inf
        mpl = (float(r["misses_pass"]) / r["matches"]) if r["misses_pass"] != "-" and r["matches"] else None
        # misses per MATCH bounds misses per landing from above (landings >= matches), and size/matches bounds
        # the mean gap from above, so passing both is sufficient for the rule; failing is read as unlisted
        regular = gap <= REG_GAP and (mpl is None or mpl < REG_MISS)
        how = "selected-without-counters" if mpl is None else "misses/match %.3f" % mpl
        if regular:
            expected_j1.append(r)
            print("  LISTED(rule) %s %s %+.1f%% gap<=%.1f B (%s)" % (r["cell"], r["subject"], r["delta_pct"], gap, how))
        else:
            refute.append("%s on %s: V1 loses %+.1f%% beyond floor, unlisted (gap %.1f B, %s)" % (r["cell"], r["subject"], r["delta_pct"], gap, how))
            print("  UNLISTED LOSS %s %s %+.1f%% (gap %.1f B, %s)" % (r["cell"], r["subject"], r["delta_pct"], gap, how))
    print("  %d of %d J1 cells read R; %d listed by the rule, %d unlisted" % (nlose, len(j1), len(expected_j1), nlose - len(expected_j1)))
    nosuspect = [r for r in j1 if r["verdict"] == "R" and r["suspect"] == "1"]
    if nosuspect:
        print("  note: %d R cells ran with load1 above the harness limit (LOAD-SUSPECT)" % len(nosuspect))

    print("== (c) G1 vs always-walk: sum(V1 - walk) over moved cells <= 2*N")
    tot = sum(r["v1_ns"] - r["walk_ns"] for r in j1)
    N = math.sqrt(sum(r["floor_ns"] ** 2 for r in j1))
    print("  sum %+.0f ns, N (quadrature of the floors) %.0f ns, bar %.0f ns" % (tot, N, EP01 * N))
    if tot > EP01 * N:
        refute.append("G1: sum(V1 - walk) %+.0f ns > 2N = %.0f ns" % (tot, EP01 * N))

    print("== (d) G3 outlier budget (EP15-EP19; w_call %.0f ns UNMEASURED)" % W_CALL)
    F = EP15 * W_CALL
    out = [r for r in j1 if r["v1_ns"] - r["walk_ns"] > max(F, EP17 * r["walk_ns"])]
    excess = sum(r["v1_ns"] - r["walk_ns"] for r in out)
    saving = sum(r["walk_ns"] - r["v1_ns"] for r in j1)
    budget = EP19 * max(0.0, saving)
    print("  outliers %d of %d cells (bar %.0f%% = %.1f), excess %.0f ns, budget %.0f ns, summed saving %+.0f ns"
          % (len(out), len(j1), 100 * EP18, EP18 * len(j1), excess, budget, saving))
    if len(j1) < EP05:
        under.append("G3: %d cells below EP05 = %d" % (len(j1), EP05))
    if len(out) > EP18 * len(j1) or excess > budget:
        refute.append("G3: %d outliers (allowed %.1f), excess %.0f ns (budget %.0f)" % (len(out), EP18 * len(j1), excess, budget))
    for r in out:
        print("    outlier %s %s %+.0f ns" % (r["cell"], r["subject"], r["v1_ns"] - r["walk_ns"]))

    print("== (f) per moved shape: the term-count rule confirmed (a W and no R) or a FINDING")
    by = collections.defaultdict(collections.Counter)
    for r in j1:
        by[r["shape"]][r["verdict"]] += 1
    for sh in sorted(by):
        c = by[sh]
        ok = c["W"] > 0 and c["R"] == 0
        print("  %-10s W %d N %d R %d  %s" % (sh, c["W"], c["N"], c["R"], "confirmed" if ok else "FINDING"))
        if not ok:
            findings.append("shape %s: V1 does not save against the walk (W %d N %d R %d)" % (sh, c["W"], c["N"], c["R"]))

    print("== (g) D169's revisit line: a listed cell on a real subject >= 64 KiB")
    big = [r for r in expected_j1 if r["nbytes"] >= 65536]
    for r in big:
        print("  REVISIT %s %s (%d B)" % (r["cell"], r["subject"], r["nbytes"]))
    if big:
        findings.append("D169 revisit: %d listed J1 cells on subjects >= 64 KiB" % len(big))
    else:
        print("  none")

    print("== FINDINGS (%d)" % len(findings))
    for f in findings:
        print("  " + f)
    for tag, lst in (("INVALID", invalid), ("REFUTED", refute), ("UNDERPOWERED", under)):
        for x in lst:
            print("  %s: %s" % (tag, x))
    v = "INVALID" if invalid else "REFUTED" if refute else "UNDERPOWERED" if under else "PASS"
    print("E8 VERDICT: " + v)
    return 0 if v == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
