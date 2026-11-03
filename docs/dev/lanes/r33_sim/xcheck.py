#!/usr/bin/env python3
"""docs/dev/lanes/r33_sim/xcheck.py -- R-33's cross-check of the simulation against timings ON FILE.

    python3 -I xcheck.py SWEEPDIR RPDIR BAR588_MD RULEPILOT_DATASET BENCH_REPORTS OUTDIR

No new timing. Three readings, each written as a TSV under OUTDIR and summarized on stdout:

 1. JOB 588 (bar588's re-read, new_bar.md: the §6 cells' and the mover sample's RTE/DEF, the
    two-stream sample's RTE/BASE). Per pattern: TODAY's routed answer (RTE), the DEF arm's
    (`--memfn=no-window-search,no-window-skip`: the legacy OFS/PRE/PF route), and the simulation's
    pick on RTE's facts (keys A and B). The sim SIDES WITH DEF where its (set, method) is DEF's and not
    RTE's; then RTE/DEF > 1 supports it and RTE/DEF < 1 is the sim picking something measured
    slower. Confounded: DEF changes the whole route (frame, verify, entry), not only the stop.
 2. THE RULE-LIST PILOT (rulepilot slot dataset.json, per-site arms timed): per site, each census arm's
    kit answers (RPDIR, the probe over each arm's deny set) and its median time against the default
    arm a0, per cell (miss/dense x 64/8192/1048576). Where the sim (on a0's facts) differs from a0, the
    arm whose rendered (set, method) multiset EQUALS the sim's is looked up: its measured ratio to a0
    is the evidence. Floor: the site's own A/A spread (a0, a0#b, a0#c).
 3. THE BENCH LEDGERS (pcrec-bench reports/*.matrix.tsv, READ-ONLY; the latest ryzen7700x matrix per
    subbench): for each bench pattern with a differing unit, pcrec's best ratio to the row's best
    engine (1.000: pcrec is the best measured). Context only: no ledger times pcrec against itself
    with another stop.
"""
import collections
import csv
import glob
import json
import math
import os
import statistics
import sys

SEARCH_KINDS = ("COVER", "OFS", "PF", "LMHIT", "MLINE", "PRE:part")


def units(path):
    rows = list(csv.DictReader(open(path), delimiter="\t", quoting=csv.QUOTE_NONE))
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["src"], r["id"], r["arm"])].append(r)
    return by


def norm(m):
    return "memchr" if m == "memchr-back" else m      # the context stop's back search is memchr's


def sig_today(us):
    return sorted((u["today_set"], norm(u["today_method"])) for u in us if u["kind"] in SEARCH_KINDS)


def sig_sim(us):
    return sorted((u["sim_set"], u["sim_method"]) for u in us if u["kind"] in SEARCH_KINDS)


def gmean(xs):
    xs = [x for x in xs if x and x > 0]
    return math.exp(sum(math.log(x) for x in xs) / len(xs)) if xs else None


def parse_bar(md):
    """{id: [(table, regime, class, ratio)]} from new_bar.md's three per-pattern tables."""
    out = collections.defaultdict(list)
    table, cols = None, None
    for line in open(md, encoding="utf-8"):
        if line.startswith("## "):
            table = line[3:].strip()
            cols = None
            continue
        if not line.startswith("| "):
            continue
        f = [x.strip() for x in line.strip().strip("|").split("|")]
        if f[0] in ("cell", "row"):
            cols = f
            continue
        if not cols or f[0].startswith("---") or len(f) != len(cols):
            continue
        d = dict(zip(cols, f))
        rk = "RTE/DEF" if "RTE/DEF" in d else "RTE/BASE" if "RTE/BASE" in d else None
        if rk is None:
            continue
        try:
            out[f[0]].append((table.split("(")[0].strip(), d["regime"], d["class"], float(d[rk]), rk))
        except (KeyError, ValueError):
            pass
    return out


def x588(sweep, bar_md, outdir):
    lines, rep = [], []
    ua, ub = units(os.path.join(sweep, "units_keyA.tsv")), units(os.path.join(sweep, "units_keyB.tsv"))
    bar = parse_bar(bar_md)
    ids = sorted({k[1] for k in ua if k[0] == "s588"})
    for pid in ids:
        rte_a, rte_b = ua.get(("s588", pid, "RTE"), []), ub.get(("s588", pid, "RTE"), [])
        dfa = ua.get(("s588", pid, "DEF"), [])
        if not rte_a:
            continue
        pat = rte_a[0]["pat"]
        t, d = sig_today(rte_a), sig_today(dfa)
        sa, sb = sig_sim(rte_a), sig_sim(rte_b)
        cells = bar.get(pid, [])
        rk = cells[0][4] if cells else "-"
        ratios = [c[3] for c in cells]
        g = gmean(ratios)
        for key, s in (("A", sa), ("B", sb)):
            if s == t:
                side = "agrees with RTE"
            elif s == d:
                side = "differs; = DEF"
            else:
                side = "differs; neither"
            ev = "-"
            if side == "differs; = DEF" and rk == "RTE/DEF" and ratios:
                ev = "supports (RTE slower)" if g > 1.0 else "AGAINST (sim's pick measured slower)"
            elif side == "agrees with RTE" and t != d and rk == "RTE/DEF" and ratios:
                ev = "supports (RTE faster)" if g < 1.0 else "AGAINST (RTE measured slower; sim keeps it)"
            lines.append([pid, pat, key, t, d, s, side, rk, "%.3f" % g if g else "-",
                          "%.3f" % max(ratios) if ratios else "-",
                          " ".join("%s/%s=%.3f" % (c[1], c[2], c[3]) for c in cells), ev])
    with open(os.path.join(outdir, "xcheck_588.tsv"), "w") as f:
        f.write("id\tpattern\tkey\tRTE today\tDEF today\tsim\tsim side\tratio\tgmean\tmax\tcells\tevidence\n")
        for l in lines:
            f.write("\t".join(str(x) for x in l) + "\n")
    return lines


def site_floor(cells):
    fl = []
    for c, arms in cells.items():
        base = [statistics.median(arms[k]) for k in ("a0", "a0#b", "a0#c") if k in arms]
        if len(base) > 1:
            fl.append(max(abs(b / base[0] - 1) for b in base))
    return max(fl) if fl else 0.0


def xrp(rpdir, dataset, outdir):
    ua, ub = units(os.path.join(rpdir, "units_keyA.tsv")), units(os.path.join(rpdir, "units_keyB.tsv"))
    ds = json.load(open(dataset))
    lines = []
    for site in ds["sites"]:
        sid = site["id"]
        cells = site["cells"]
        fl = site_floor(cells)
        arms = sorted({a for c in cells.values() for a in c if "#" not in a})
        ratio = {}
        for a in arms:
            rs = [statistics.median(c[a]) / statistics.median(c["a0"]) for c in cells.values()
                  if a in c and "a0" in c]
            ratio[a] = gmean(rs)
        best = min(ratio, key=lambda a: ratio[a]) if ratio else None
        for key, U in (("A", ua), ("B", ub)):
            a0 = U.get(("rp", sid + ":a0", "RTE"), [])
            if not a0:
                continue
            t, s = sig_today(a0), sig_sim(a0)
            if s == t:
                # agrees with the default: is some arm with a DIFFERENT search measured faster?
                faster = [a for a in arms if a != "a0" and ratio.get(a) and ratio[a] < 1 - fl
                          and sig_today(U.get(("rp", sid + ":" + a, "RTE"), [])) != t]
                lines.append([sid, a0[0]["pat"], key, "agree", t, s, "-", "-", "%.4f" % fl,
                              ",".join("%s=%.3f" % (a, ratio[a]) for a in faster) or "-",
                              "%s=%.3f" % (best, ratio[best]) if best else "-"])
                continue
            match = [a for a in arms if a != "a0" and sig_today(U.get(("rp", sid + ":" + a, "RTE"), [])) == s]
            mr = ",".join("%s=%.3f" % (a, ratio[a]) for a in match if ratio.get(a)) or "no arm renders it"
            verdict = "-"
            if match and all(ratio.get(a) for a in match):
                m = min(ratio[a] for a in match)
                verdict = ("supports" if m < 1 - fl else "AGAINST (measured slower)" if m > 1 + fl
                           else "within floor")
            lines.append([sid, a0[0]["pat"], key, "differ", t, s, mr, verdict, "%.4f" % fl, "-",
                          "%s=%.3f" % (best, ratio[best]) if best else "-"])
    with open(os.path.join(outdir, "xcheck_rulepilot.tsv"), "w") as f:
        f.write("site\tpattern\tkey\tsim vs a0\ta0 today\tsim\tarm rendering the sim (ratio to a0)\t"
                "evidence\tA/A floor\tfaster arms with another search (sim agrees with a0)\tbest arm\n")
        for l in lines:
            f.write("\t".join(str(x) for x in l) + "\n")
    return lines


def xbench(sweep, reports, outdir):
    latest = {}
    for m in sorted(glob.glob(os.path.join(reports, "*-ryzen7700x-*.matrix.tsv"))):
        sb = os.path.basename(m)[11:].split("-0.")[0]
        latest[sb] = m          # sorted by date prefix: the last is the newest
    ratio = {}
    for sb, m in latest.items():
        cols = None
        for line in open(m, encoding="utf-8"):
            if line.startswith("#"):
                continue
            f = line.rstrip("\n").split("\t")
            if cols is None:
                cols = f
                continue
            d = dict(zip(cols, f))
            pc = [c for c in cols if c.startswith("pcrec_")]
            vals = []
            for c in pc:
                try:
                    vals.append(float(d[c]))
                except ValueError:
                    pass
            if vals:
                ratio.setdefault((sb, d["pattern"]), []).append((d["regime_or_na"], min(vals)))
    ub = units(os.path.join(sweep, "units_keyB.tsv"))
    ua = units(os.path.join(sweep, "units_keyA.tsv"))
    lines = []
    for (src, pid, arm), us in sorted(ua.items()):
        if src != "bench":
            continue
        for key, U in (("A", ua), ("B", ub)):
            for u in U[(src, pid, arm)]:
                if u["verdict"].startswith("agree"):
                    continue
                sb, name = pid.split("/", 1)
                rs = ratio.get((sb, name), [])
                lines.append([pid, u["pat"], key, u["kind"], u["verdict"],
                              "%s %s" % (u["today_set"], u["today_method"]),
                              "%s %s" % (u["sim_set"], u["sim_method"]), u["gap"],
                              " ".join("%s=%.3f" % r for r in rs) or "not in a ryzen7700x ledger",
                              os.path.basename(latest.get(sb, "-"))])
    with open(os.path.join(outdir, "xcheck_bench.tsv"), "w") as f:
        f.write("pattern id\tpattern\tkey\tkind\tverdict\ttoday\tsim\tgap\tpcrec ratio to row best "
                "(by regime)\tledger\n")
        for l in lines:
            f.write("\t".join(str(x) for x in l) + "\n")
    return lines


def main():
    sweep, rpdir, bar_md, dataset, reports, outdir = sys.argv[1:7]
    os.makedirs(outdir, exist_ok=True)
    a = x588(sweep, bar_md, outdir)
    b = xrp(rpdir, dataset, outdir)
    c = xbench(sweep, reports, outdir)
    print("== r33 xcheck: 588 rows %d, rule-pilot rows %d, bench rows %d" % (len(a), len(b), len(c)))


if __name__ == "__main__":
    main()
