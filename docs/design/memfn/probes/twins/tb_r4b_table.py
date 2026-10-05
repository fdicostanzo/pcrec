#!/usr/bin/env python3
"""memfn R4b: render tb_r4b transcripts as the R-1 readings (markdown).

    python3 tb_r4b_table.py LABEL=FILE[,FILE...] [LABEL=FILE[,FILE...] ...]

Each group is one BUILD; its files are LAUNCHES of the same binary (each
value is the median across launches). The FIRST group is the SIMD-off build
(x86: gcc -march=x86-64; Mac: the one build): its `emit` and `swar` give the
SIMD-off reading, and its `swar` is the scalar every group's `ffl` is read
against (the SIMD-on reading: D147, never against emit).

FLOOR (D144 addendum 1): `emit2` is the same gate timed as a second instance
in the same binary; per row the floor is the largest |emit - emit2| over the
launches of the groups being compared. A delta whose magnitude is <= the
floor reads NULL; otherwise WIN (negative: faster) or LOSS. Absolute ns,
never a ratio.

userpass and cls-n-uc (the lead cells) add `swlf` (the emitted lead test
first, then swar over the run alone: pcrec's order kept) against emit, and
`ffllf` (the same with ffl) from the last group.

cls-n-uc (cn) adds K85's columns: `nosl` is the -fno-req-set-lead gate
(K85's off arm); emit - nosl is the set-leads pre-check's own cost, and
swar - nosl / ffl - nosl say what a fused form leaves of it.
"""
import statistics
import sys

ORDER = ["gate", "sweep", "short", "pc16", "pc64", "pc256", "pc1024"]
CELLS = [("us", "union-select"), ("up", "userpass"), ("mi", "mod-i"), ("cn", "cls-n-uc (K85)")]


def read(files):
    """{(cell, var, regime, subject): [ns per launch]}, {(cell, regime, subject): [|emit-emit2|]}"""
    vals, floors = {}, {}
    for f in files:
        one = {}
        for ln in open(f, encoding="utf-8"):
            p = ln.rstrip("\n").split("\t")
            if p[0] != "R":
                continue
            one[(p[1], p[2], p[3], p[4])] = (float(p[5]), p[7])
        for k, (v, _h) in one.items():
            vals.setdefault(k, []).append(v)
        for (c, var, r, s), (v, _h) in one.items():
            if var == "emit" and (c, "emit2", r, s) in one:
                floors.setdefault((c, r, s), []).append(abs(v - one[(c, "emit2", r, s)][0]))
        hits = {(c, r, s): h for (c, var, r, s), (_v, h) in one.items() if var == "emit"}
    return vals, floors, hits


def med(xs):
    return statistics.median(xs) if xs else None


def fmt(x):
    if x is None:
        return "-"
    return "%.2f" % x if abs(x) < 100 else "{:,.0f}".format(x)


def verdict(d, fl):
    if d is None or fl is None:
        return "-"
    if abs(d) <= fl:
        return "NULL"
    return "**WIN**" if d < 0 else "**LOSS**"


def main():
    groups = []
    for a in sys.argv[1:]:
        label, files = a.split("=", 1)
        groups.append((label, read(files.split(","))))
    if not groups:
        print(__doc__)
        return 2
    base_label, (bv, bf, bh) = groups[0]
    print("ns (median of %s launches); floor = max |emit - emit2|; "
          "SIMD-off = swar - emit (%s); SIMD-on = ffl - swar(%s)\n"
          % ("/".join(str(max((len(v) for v in g[1][0].values()), default=0)) for g in groups),
             base_label, base_label))
    keys = sorted({(c, r, s) for (c, _v, r, s) in bv}, key=lambda k: (k[0], ORDER.index(k[1]), k[2]))
    for cell, title in CELLS:
        rows = [k for k in keys if k[0] == cell]
        if not rows:
            continue
        hdr = ["regime", "subject", "hits", "emit", "floor", "swar", "swar-emit", "SIMD-off"]
        for label, _ in groups:
            hdr += ["ffl " + label, "ffl-swar", "SIMD-on"]
        hdr += ["byte"]
        if cell in ("up", "cn"):
            hdr += ["swlf", "swlf-emit", "SIMD-off", "ffllf " + groups[-1][0]]
        if cell == "cn":
            hdr += ["nosl", "emit-nosl", "swar-nosl", "ffl(%s)-nosl" % groups[-1][0]]
        print("### %s\n" % title)
        print("| " + " | ".join(hdr) + " |")
        print("|" + "---|" * len(hdr))
        for (c, r, s) in rows:
            e, sw = med(bv.get((c, "emit", r, s), [])), med(bv.get((c, "swar", r, s), []))
            fl0 = max(bf.get((c, r, s), [0]))
            d = sw - e if e is not None and sw is not None else None
            out = [r, s, bh.get((c, r, s), "-"), fmt(e), fmt(fl0), fmt(sw), fmt(d), verdict(d, fl0)]
            for _label, (gv, gf, _gh) in groups:
                ff = med(gv.get((c, "ffl", r, s), []))
                fl = max(fl0, max(gf.get((c, r, s), [0])))
                dd = ff - sw if ff is not None and sw is not None else None
                out += [fmt(ff), fmt(dd), verdict(dd, fl)]
            out.append(fmt(med(bv.get((c, "byte", r, s), []))))
            if cell in ("up", "cn"):
                lf = med(bv.get((c, "swlf", r, s), []))
                dl = lf - e if lf is not None and e is not None else None
                out += [fmt(lf), fmt(dl), verdict(dl, fl0),
                        fmt(med(groups[-1][1][0].get((c, "ffllf", r, s), [])))]
            if cell == "cn":
                ns = med(bv.get((c, "nosl", r, s), []))
                lv = groups[-1][1][0]
                fl_ = med(lv.get((c, "ffl", r, s), []))
                out += [fmt(ns)] + [fmt(x - ns) if x is not None and ns is not None else "-"
                                    for x in (e, sw, fl_)]
            print("| " + " | ".join(str(x) for x in out) + " |")
        print()
    print("hits: gate = the position returned on the whole subject (n = none); "
          "sweep = gate passes over the find-all; short/pc* = subjects whose gate passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
