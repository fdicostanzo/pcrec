#!/usr/bin/env python3
"""e8min/readslot.py -- E8's reader: the window's raw launches -> one row per timed cell.

  readslot.py cells  SLOT_DIR CENSUS_TSV [--raw NAME] > e8_cells.tsv
  readslot.py losers SLOT_DIR CELLS_TSV   > SLOT_DIR/groups2.tsv     (f2perf's input: J1 cells that read R)

`cells` cuts $SLOT/time/raw_E8.tsv into visits with grid2read's own loader (grload2.visits: a requeue is a
second visit, the last clean one is chosen) and applies grid2read's floor verdict (its `floor`,
`paired_sign` and `verdict` functions, which cannot be imported: grid2read.py runs its whole analysis on
import): floor = max(|walk#b - walk|, |walk#c - walk|); V1 reads N when |V1 - walk| <= floor or the launches
disagree in sign, else R (slower) or W (faster). The NULL CONTROL is walk#b read as a policy against walk with
the HELD-OUT copy's floor alone (|walk#c - walk|): with the two-sided floor it would read N by construction.
Columns of e8_cells.tsv (ns are ns per pass, the driver's median of medians; misses_pass is the walk's
branch-misses:u per pass from f2/raw.tsv, `-` when f2perf did not run that cell):
  set cell id subject nbytes shape walk_ns v1_ns floor_ns aac_ns delta_pct verdict nullb matches misses_pass suspect
"""
import collections
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../grid2read"))
import grload2 as gl  # noqa: E402

COLS = ("set cell id subject nbytes shape walk_ns v1_ns floor_ns aac_ns delta_pct verdict nullb matches "
        "misses_pass suspect").split()


def sign_ok(v, arm, ref):
    """True iff arm - ref has the sign of the median delta in every launch."""
    rs = sorted(set(v.arm_vals[arm]) & set(v.arm_vals[ref]))
    d = [v.arm_vals[arm][r] - v.arm_vals[ref][r] for r in rs]
    md = v.med(arm) - v.med(ref)
    return bool(d) and (all(x > 0 for x in d) if md > 0 else all(x < 0 for x in d))


def read_verdict(d, floor):
    """W / R / N for a delta d against a floor and the launch-sign test result (None = no test)."""
    return "N" if abs(d) <= floor else ("W" if d < 0 else "R")


def subject_bytes(slot, subj):
    p = os.path.join(slot, "subj", subj.split("@")[0])
    if os.path.isdir(p):
        fs = sorted(f for f in os.listdir(p) if not f.startswith("."))
        return os.path.getsize(os.path.join(p, fs[0]))      # a streamed subject: one pass = one buffer
    return os.path.getsize(p)


def census_shapes(path):
    sh = collections.defaultdict(list)
    for ln in open(path, encoding="utf-8"):
        if ln.startswith("#") or not ln.strip():
            continue
        f = ln.rstrip("\n").split("\t")
        if f[7] == "1":
            sh[f[12]].append(f[4])
    return {q: ",".join(sorted(set(s))) for q, s in sh.items()}


def misses(slot):
    """(cell, subject) -> walk branch-misses:u per pass (median over launches), from f2perf's raw file."""
    p = os.path.join(slot, "f2", "raw.tsv")
    m = collections.defaultdict(list)
    if os.path.exists(p):
        for ln in list(open(p))[1:]:
            c, s, a, _l, _k, ev, _ck, _c0, pp = ln.rstrip("\n").split("\t")
            if a == "walk" and ev == "branch-misses:u":
                m[(c, s)].append(float(pp))
    return {k: statistics.median(v) for k, v in m.items()}


def cells(slot, census, tag="E8", want="all"):
    vis = gl.visits(os.path.join(slot, "time", "raw_%s.tsv" % tag), "EXT")
    chosen = {}
    for v in vis:
        if not v.overlap:
            chosen[v.key] = v                    # the last clean visit of a key wins
    shapes, miss = census_shapes(census), misses(slot)
    rows = []
    for (cell, subj, mode), v in sorted(chosen.items()):
        b = "walk"
        if mode != want or "V1" not in v.arm_vals:
            continue
        wn, vn = v.med(b), v.med("V1")
        fl = max(abs(v.med(b + "#b") - wn), abs(v.med(b + "#c") - wn))
        aac = abs(v.med(b + "#c") - wn)
        d = vn - wn
        ver = read_verdict(d, fl) if sign_ok(v, "V1", b) else "N"
        db = v.med(b + "#b") - wn
        nb = read_verdict(db, aac) if sign_ok(v, b + "#b", b) else "N"
        m = [r["ans"] for r in v.rows if r["arm"] == "V1"][0]
        mt = int(dict(x.split("=") for x in m.split() if "=" in x).get("matches", 0))
        qid = cell[3:] if cell.startswith("j1-") else subj
        rows.append(dict(set="J1" if cell.startswith("j1-") else "AN", cell=cell, id=qid, subject=subj,
                         nbytes=subject_bytes(slot, subj), shape=shapes.get(qid, "-") if cell.startswith("j1-") else "-",
                         walk_ns="%.2f" % wn, v1_ns="%.2f" % vn, floor_ns="%.2f" % fl, aac_ns="%.2f" % aac,
                         delta_pct="%+.2f" % (100.0 * d / wn), verdict=ver, nullb=nb, matches=mt,
                         misses_pass="%.2f" % miss[(cell, subj)] if (cell, subj) in miss else "-",
                         suspect=int(v.n_load_hi > 0)))
    return rows


def main():
    cmd, slot, src = sys.argv[1], sys.argv[2], sys.argv[3]
    if cmd == "cells":
        opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d  # noqa: E731
        print("\t".join(COLS))
        for r in cells(slot, src, opt("--raw", "E8"), opt("--mode", "all")):
            print("\t".join(str(r[c]) for c in COLS))
    elif cmd == "losers":      # f2perf item 6's groups2.tsv: item cell subject mode arms
        print("item\tcell\tsubject\tmode\tarms")
        for ln in list(open(src))[1:]:
            f = dict(zip(COLS, ln.rstrip("\n").split("\t")))
            if f["set"] == "J1" and f["verdict"] == "R":
                print("1\t%s\t%s\tall\twalk" % (f["cell"], f["subject"]))
    else:
        sys.exit("usage: readslot.py cells|losers SLOT SRC")


if __name__ == "__main__":
    main()
