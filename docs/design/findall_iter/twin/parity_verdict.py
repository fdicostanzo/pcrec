#!/usr/bin/env python3
# docs/design/findall_iter/twin/parity_verdict.py — the parity gate's TABLE and VERDICT
# (lane parity, 2026-10-21; findall_iter.md §5.3 revision 3, "Verdict").
#
# Reads parity.sh's results.tsv (one row per launch x subcell x regime x arm: the arm's
# median ns per find-all over its samples in that launch). Per (subcell, regime, arm): the
# MEDIAN and IQR over the launches. Then §5.3's rule:
#   floor = the A/A arm's max(|median(A)/median(L_new) - 1|, IQR(A)/median(A))
#   I     : I / L_old <= 1 + floor                        PASS, else FINDING   (every cell)
#   L_new : L_new / L_old within the floor                "_search unharmed" (an A/A pair
#                                                         in the pre-build run: same build)
#   B64   : B64 / L_old <= 1 + floor on cells 1-6         PASS, else FINDING
#           cell 7 is batching's stated cost, reported
#   batch cell: `fill` iff B64 / I < 1 - floor on EVERY subcell of cells 1 and 3 in BOTH
#           regimes, else `off` (the reading of "must beat I beyond the floor on the dense
#           cells 1 and 3" taken here: every dense subcell, every regime; the per-row
#           answers are printed so another reading can be taken from the table)
#   N64, I_shared, L_tw, I_fill: reported, not gated (I_shared within I's floor is §2.2's
#           trigger, printed per row)
# Prints the table, one VERDICT line per (subcell, regime), the batch line, then
# `parity: DONE rc=0` and `== parity COMPLETE <verdict rows>`.
#
# POST-BUILD ([FINDALL-NEXT] I1, parity.sh under PARITY_POST=1): the arms are L_old (the
# parent's artifact), L_new, A and I (the built iterator); the B64/N64/I_shared rows and
# the batch line are absent, and I is GATED on cells 1, 3 and 4 (D171: cells 2, 5, 6 and 7
# are reported), printed as `GATE` / `REPORT`.
#
# usage: python3 -I parity_verdict.py RESULTS.tsv
import sys
from collections import defaultdict

ARMS = ["L_old", "L_new", "A", "L_tw", "I", "N64", "I_shared", "B64", "I_fill"]
DENSE = ("c1-", "c3-")
GATED = ("c1-", "c3-", "c4")   # D171: the post-build gate's cells


def median(v):
    v = sorted(v)
    m = len(v) // 2
    return v[m] if len(v) % 2 else (v[m - 1] + v[m]) / 2


def quantile(v, q):
    v = sorted(v)
    if len(v) == 1:
        return v[0]
    x = q * (len(v) - 1)
    i = int(x)
    f = x - i
    return v[i] if i + 1 >= len(v) else v[i] * (1 - f) + v[i + 1] * f


rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1], encoding="ascii")]
hdr, rows = rows[0], rows[1:]
col = {h: i for i, h in enumerate(hdr)}
data = defaultdict(list)
cells, launches, loads, sib = [], set(), [], []
for r in rows:
    key = (r[col["cell"]], r[col["regime"]], r[col["arm"]])
    data[key].append(float(r[col["ns"]]))
    if r[col["cell"]] not in cells:
        cells.append(r[col["cell"]])
    launches.add(r[col["launch"]])
    loads.append(float(r[col["load1"]]))
    sib.append(float(r[col["sib_busy_pct"]]))

print(f"== parity TABLE: {len(launches)} launches, {len(rows)} rows; ns per whole find-all, "
      f"median over launches [IQR as % of median]; ratio = arm / L_old")
print(f"   load1 during the run: min {min(loads):.2f} median {median(loads):.2f} max {max(loads):.2f}; "
      f"SMT sibling busy %: median {median(sib):.1f} max {max(sib):.1f}")
nverd, batch_ok, batch_rows = 0, True, []
for cid in cells:
    for reg in ("R1", "R2"):
        st = {}
        for a in ARMS:
            v = data.get((cid, reg, a))
            if not v:
                continue
            m = median(v)
            st[a] = (m, (quantile(v, 0.75) - quantile(v, 0.25)) / m if m else 0.0)
        if "L_old" not in st or "A" not in st or "L_new" not in st:
            print(f"   {cid} {reg}: MISSING arms {sorted(set(ARMS) - set(st))}")
            continue
        base = st["L_old"][0]
        floor = max(abs(st["A"][0] / st["L_new"][0] - 1), st["A"][1])
        print(f"-- {cid} {reg}  floor {floor * 100:.2f}%")
        for a in ARMS:
            if a in st:
                m, iqr = st[a]
                print(f"   {a:<9}{m:>14.2f} ns  [{iqr * 100:5.2f}%]  ratio {m / base:.4f}")
        out = []
        ri = st["I"][0] / base
        post = "B64" not in st
        tag = ("GATE " if cid.startswith(GATED) else "REPORT ") if post else ""
        out.append(f"{tag}I {'PASS' if ri <= 1 + floor else 'FINDING'} {ri:.4f}")
        rn = st["L_new"][0] / base
        out.append(f"L_new {'unharmed' if abs(rn - 1) <= floor else 'OUTSIDE-FLOOR'} {rn:.4f}")
        if post:
            print(f"VERDICT {cid} {reg} floor {floor * 100:.2f}%: " + "; ".join(out))
            nverd += 1
            continue
        rb = st["B64"][0] / base
        if cid.startswith("c7"):
            out.append(f"B64 cost-reported {rb:.4f} (B64/I {st['B64'][0] / st['I'][0]:.4f})")
        else:
            out.append(f"B64 {'PASS' if rb <= 1 + floor else 'FINDING'} {rb:.4f}")
        if cid.startswith(DENSE):
            bi = st["B64"][0] / st["I"][0]
            beats = bi < 1 - floor
            batch_ok = batch_ok and beats
            batch_rows.append(f"{cid}/{reg} B64/I {bi:.4f} {'beats' if beats else 'does-not-beat'}")
        rs = st["I_shared"][0] / st["I"][0]
        out.append(f"I_shared/I {rs:.4f} {'within' if abs(rs - 1) <= floor else 'outside'}")
        out.append(f"N64 {st['N64'][0] / base:.4f}")
        print(f"VERDICT {cid} {reg} floor {floor * 100:.2f}%: " + "; ".join(out))
        nverd += 1
if batch_rows:
    print("BATCH dense rows: " + "; ".join(batch_rows))
    print(f"BATCH CELL: {'fill' if batch_ok else 'off'}")
print("parity: DONE rc=0")
print(f"== parity COMPLETE {nverd} verdict rows")
