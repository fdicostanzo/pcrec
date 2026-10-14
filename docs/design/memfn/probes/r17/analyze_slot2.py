#!/usr/bin/env python3
"""R-17 follow-up reading (lane r17rd): independent recomputation of the
slot2 tables from times.tsv. Analysis only; no compiles, no timing.

    python3 -I analyze_slot2.py <slot2 dir> <section>

sections: verdict reset mask_ring adapt k percall losers perf all
Every ratio is form/table, min of 7 (ns_per_call_min), per matched row key.
"""
import csv, os, statistics as st, sys
from collections import defaultdict

REAL = "adl qdm alt2 alt2r bkn bpr sig tki kel hbr hbrc u8l dig lc".split()
DENSE = ["dig", "lc", "bkn", "bpr"]
OFF = ["swar", "mask8_swar", "mask64_swar", "mask64i_swar", "ring_swar", "adapt_swar", "adapt_mask"]
ON = ["sse2", "avx2", "mask64_sse2", "mask64_avx2", "ring_avx2", "adapt_avx2"]
SYN = {"syn4": 4, "syn5": 5, "syn6": 6, "syn8": 8}


def load(d):
    R = list(csv.DictReader(open(os.path.join(d, "times.tsv")), delimiter="\t"))
    by = defaultdict(dict)
    for r in R:
        k = (r["cell"], r["regime"], int(r["n"]), int(r["ppm"]), int(r["span"]),
             int(r["reset"]), float(r["g"]), int(r["align"]))
        by[k][r["form"]] = r
    rat = sorted(float(r["ns_per_call_med"]) / float(r["ns_per_call_min"])
                 for r in R if float(r["ns_per_call_min"]) > 0)
    return R, by, rat[int(0.95 * (len(rat) - 1))]


def ratio(by, k, f, base="table", col="ns_per_call_min"):
    fs = by[k]
    if f not in fs or base not in fs:
        return None
    b = float(fs[base][col])
    return float(fs[f][col]) / b if b > 0 else None


def sel(by, cells=None, **kw):
    """keys matching: regime n ppm span reset g align (each a value or a set/callable)."""
    out = []
    names = ["cell", "regime", "n", "ppm", "span", "reset", "g", "align"]
    for k in by:
        if cells is not None and k[0] not in cells:
            continue
        ok = True
        for nm, v in kw.items():
            x = k[names.index(nm)]
            if callable(v):
                ok = ok and v(x)
            elif isinstance(v, (set, list, tuple)):
                ok = ok and x in v
            else:
                ok = ok and x == v
        if ok:
            out.append(k)
    return out


def cellstat(by, keys, f, col="ns_per_call_min"):
    v = [ratio(by, k, f, col=col) for k in keys]
    v = [x for x in v if x is not None]
    if not v:
        return None
    return st.median(v), max(v), min(v), len(v)


def fmt(s):
    return "  -  " if s is None else "%.2f/%.2f" % (s[0], s[1])


def table(by, forms, cols, cells, col="ns_per_call_min"):
    print("| form | " + " | ".join(c[0] for c in cols) + " |")
    print("|---|" + "---|" * len(cols))
    for f in forms:
        print("| %s | " % f + " | ".join(fmt(cellstat(by, sel(by, cells, **c[1]), f, col)) for c in cols) + " |")


F64 = dict(regime="findall", n=65536, g=0.0, align=0)
INF = dict(F64, reset=0)


def sec_verdict(by, band):
    for title, forms in (("SIMD-off", OFF), ("SIMD-on", ON)):
        print("\n### %s, findall reset=inf, 64K, 14 real cells, median/worst of form/table" % title)
        cols = [("%dk" % (p // 1000), dict(INF, ppm=p)) for p in (0, 1000, 20000, 70000, 100000, 150000, 200000, 300000, 400000, 600000, 800000, 1000000)]
        table(by, forms, cols, REAL)
        print("\n### %s, dense controls only (dig lc bkn bpr)" % title)
        table(by, forms, cols, DENSE)
    print("\n### 1M, 14 real cells")
    cols = [("%s" % (("%dk" % (p // 1000)) if p < 1000000 else "1M"), dict(regime="findall", n=1048576, ppm=p, reset=0)) for p in (0, 70000, 300000, 600000, 1000000)]
    table(by, OFF + ON, cols, REAL)


def sec_reset(by, band):
    forms = ["swar", "mask8_swar", "mask64_swar", "mask64i_swar", "ring_swar", "adapt_swar", "adapt_mask",
             "avx2", "mask64_sse2", "mask64_avx2", "ring_avx2", "adapt_avx2"]
    for ppm in (300000,):
        print("\n### reset axis at %dk ppm, 64K, 14 real cells, median/worst form/table (table at the same reset)" % (ppm // 1000))
        cols = [(nm, dict(F64, ppm=ppm, reset=r)) for nm, r in (("inf", 0), ("k16", 16), ("k4", 4), ("call", 1))]
        table(by, forms, cols, REAL)
    print("\n### reset=call (1) at 20k/70k/300k/800k, median/worst")
    cols = [("%dk" % (p // 1000), dict(F64, ppm=p, reset=1)) for p in (20000, 70000, 300000, 800000)]
    table(by, forms, cols, REAL)
    print("\n### same, absolute ns per call, median over cells, reset inf vs call at 300k (table, swar, mask64_swar, ring_swar)")
    for f in ("table", "swar", "mask8_swar", "mask64_swar", "ring_swar", "mask64_avx2", "ring_avx2", "adapt_swar"):
        row = []
        for r in (0, 16, 4, 1):
            v = [float(by[k][f]["ns_per_call_min"]) for k in sel(by, REAL, **dict(F64, ppm=300000, reset=r)) if f in by[k]]
            row.append("%.1f" % st.median(v))
        print("  %-12s inf/k16/k4/call ns: %s" % (f, " ".join(row)))
    print("\n### calls_per_iter shows work per sample differs by reset (adl, 300k):")
    for r in (0, 16, 4, 1):
        for k in sel(by, ["adl"], **dict(F64, ppm=300000, reset=r)):
            print("   reset", r, "calls_per_iter", by[k]["table"]["calls_per_iter"])


def sec_mask_ring(by, band):
    forms = ["mask64_swar", "ring_swar", "mask64_avx2", "ring_avx2", "mask8_swar"]
    print("\n### ring/mask ratio, per ppm, 64K inf, median/worst over 14 cells")
    for a, b in (("ring_swar", "mask64_swar"), ("ring_avx2", "mask64_avx2"), ("mask8_swar", "mask64_swar")):
        row = []
        for p in (0, 1000, 20000, 70000, 100000, 200000, 300000, 600000, 800000, 1000000):
            v = []
            for k in sel(by, REAL, **dict(INF, ppm=p)):
                if a in by[k] and b in by[k]:
                    v.append(float(by[k][a]["ns_per_call_min"]) / float(by[k][b]["ns_per_call_min"]))
            row.append("%.2f/%.2f" % (st.median(v), max(v)))
        print("  %s/%s : %s" % (a, b, " ".join(row)))
    print("  (ppm columns: 0 1k 20k 70k 100k 200k 300k 600k 800k 1M)")
    for a, b in (("ring_swar", "mask64_swar"), ("ring_avx2", "mask64_avx2")):
        print("\n  %s/%s other regimes" % (a, b))
        for nm, kw in (("1M 70k", dict(regime="findall", n=1048576, ppm=70000, reset=0)),
                       ("1M 300k", dict(regime="findall", n=1048576, ppm=300000, reset=0)),
                       ("1M 0", dict(regime="findall", n=1048576, ppm=0, reset=0)),
                       ("k16 300k", dict(F64, ppm=300000, reset=16)), ("k4 300k", dict(F64, ppm=300000, reset=4)),
                       ("call 20k", dict(F64, ppm=20000, reset=1)), ("call 300k", dict(F64, ppm=300000, reset=1)),
                       ("clus g2", dict(regime="findall", g=2.0)), ("clus g32", dict(regime="findall", g=32.0)),
                       ("percall L16", dict(regime="percall", span=16, align=0)),
                       ("percall L64", dict(regime="percall", span=64, align=0))):
            v = []
            for k in sel(by, REAL, **kw):
                if a in by[k] and b in by[k]:
                    v.append(float(by[k][a]["ns_per_call_min"]) / float(by[k][b]["ns_per_call_min"]))
            print("    %-12s %.2f/%.2f (%d)" % (nm, st.median(v), max(v), len(v)))


def sec_adapt(by, band):
    pairs = [("adapt_swar", "swar"), ("adapt_swar", "table"), ("adapt_avx2", "avx2"), ("adapt_avx2", "table"),
             ("adapt_mask", "mask64_swar"), ("adapt_mask", "table")]
    regs = [("inf 0", dict(INF, ppm=0)), ("inf 20k", dict(INF, ppm=20000)), ("inf 70k", dict(INF, ppm=70000)),
            ("inf 150k", dict(INF, ppm=150000)), ("inf 300k", dict(INF, ppm=300000)), ("inf 800k", dict(INF, ppm=800000)),
            ("k4 300k", dict(F64, ppm=300000, reset=4)), ("call 20k", dict(F64, ppm=20000, reset=1)),
            ("call 300k", dict(F64, ppm=300000, reset=1)), ("clus g8", dict(regime="findall", g=8.0)),
            ("pc L16", dict(regime="percall", span=16, align=0)), ("pc L64", dict(regime="percall", span=64, align=0))]
    print("| a/b | " + " | ".join(r[0] for r in regs) + " |")
    print("|---|" + "---|" * len(regs))
    for a, b in pairs:
        row = []
        for nm, kw in regs:
            v = [float(by[k][a]["ns_per_call_min"]) / float(by[k][b]["ns_per_call_min"]) for k in sel(by, REAL, **kw) if a in by[k] and b in by[k]]
            row.append("%.2f/%.2f" % (st.median(v), max(v)))
        print("| %s/%s | %s |" % (a, b, " | ".join(row)))


def sec_k(by, band):
    for cell, kk in sorted(SYN.items(), key=lambda x: x[1]):
        print("\n## %s (K=%d): form/table per regime (single cell, so value = raw ratio)" % (cell, kk))
        keys = sorted(sel(by, [cell]), key=lambda k: (k[1], k[2], k[4], k[3], k[5]))
        forms = ["swar", "mask8_swar", "mask64_swar", "mask64i_swar", "ring_swar", "adapt_swar", "adapt_mask"]
        print("| regime | table ns | " + " | ".join(forms) + " | best off |")
        print("|---|---|" + "---|" * (len(forms) + 1))
        for k in keys:
            lab = "%s p%s%s" % (("fa" if k[1] == "findall" else "pc"), k[3] // 1000 if k[1] == "findall" else k[4], "k" if k[1] == "findall" else "")
            if k[1] == "percall":
                lab = "pc L%d %dk" % (k[4], k[3] // 1000)
            rs = [ratio(by, k, f) for f in forms]
            ok = [x for x in rs if x]
            print("| %s | %.1f | %s | %.2f |" % (lab, float(by[k]["table"]["ns_per_call_min"]), " | ".join("%.2f" % x for x in rs), min(ok)))


def sec_percall(by, band):
    forms = OFF + ON
    cols = [("L16 0", dict(regime="percall", span=16, align=0, ppm=0)), ("L16 20k", dict(regime="percall", span=16, align=0, ppm=20000)),
            ("L16 300k", dict(regime="percall", span=16, align=0, ppm=300000)), ("L16 800k", dict(regime="percall", span=16, align=0, ppm=800000)),
            ("L64 0", dict(regime="percall", span=64, align=0, ppm=0)), ("L64 20k", dict(regime="percall", span=64, align=0, ppm=20000)),
            ("L64 300k", dict(regime="percall", span=64, align=0, ppm=300000)), ("L64 800k", dict(regime="percall", span=64, align=0, ppm=800000)),
            ("L64odd 0", dict(regime="percall", span=64, align=1, ppm=0)), ("L64odd 300k", dict(regime="percall", span=64, align=1, ppm=300000))]
    table(by, forms, cols, REAL)
    print("\nabsolute ns per call, median over cells (L16 ppm 0):")
    for f in ["floor", "table"] + forms:
        v = [float(by[k][f]["ns_per_call_min"]) for k in sel(by, REAL, regime="percall", span=16, align=0, ppm=0) if f in by[k]]
        w = [float(by[k][f]["ns_per_call_min"]) for k in sel(by, REAL, regime="percall", span=64, align=0, ppm=0) if f in by[k]]
        print("  %-13s L16 %.2f  L64 %.2f" % (f, st.median(v), st.median(w)))


def sec_losers(by, band):
    """every (form, cell, regime) beyond the band, counted per form; and which regimes."""
    forms = OFF + ON
    for f in forms:
        loss = defaultdict(list)
        for k in sel(by, REAL):
            r = ratio(by, k, f)
            if r is not None and r > band:
                g = ("pc L%d%s" % (k[4], "odd" if k[7] else "")) if k[1] == "percall" else \
                    ("clus" if k[6] > 0 else ("%s n%s" % ({0: "inf", 1: "call"}.get(k[5], "k%d" % k[5]), "64K" if k[2] == 65536 else "1M")))
                loss[g].append((k[0], k[3], round(r, 2)))
        tot = len(sel(by, REAL))
        print("%-13s losing rows %d of %d" % (f, sum(len(v) for v in loss.values()), tot))
        for g, v in sorted(loss.items()):
            print("    %-14s %3d  worst %s" % (g, len(v), max(v, key=lambda x: x[2])))


def sec_perf(by, d):
    pdir = os.path.join(d, "perf")
    data = {}
    for f in sorted(os.listdir(pdir)):
        if not f.endswith(".csv"):
            continue
        cell, rest = f[:-4].split("_", 1)
        form, ppm = rest.rsplit("_", 1)
        ev = {}
        for line in open(os.path.join(pdir, f)):
            p = line.strip().split(",")
            if len(p) > 2 and p[0].replace(".", "").isdigit():
                ev[p[2].split(":")[0]] = float(p[0])
        out = open(os.path.join(pdir, f[:-4] + ".out")).read().split("\t")
        data[(cell, form, ppm)] = (ev, float(out[7]) * float(out[6]))
    forms = ["table", "swar", "mask64_swar", "ring_swar", "adapt_swar", "mask64_avx2"]
    for ppm in ("70000", "300000", "800000"):
        print("\nbranch-miss/call (form - floor), ppm", ppm)
        print("| cell | " + " | ".join(forms) + " |")
        print("|---|" + "---|" * len(forms))
        agg = defaultdict(list)
        for cell in sorted({c for c, _, _ in data}):
            fl = data.get((cell, "floor", ppm))
            if not fl:
                continue
            row = []
            for f in forms:
                x = data.get((cell, f, ppm))
                if not x:
                    row.append("-")
                    continue
                bm = (x[0].get("branch-misses", 0) - fl[0].get("branch-misses", 0)) / x[1]
                agg[f].append(bm)
                row.append("%.3f" % bm)
            print("| %s | %s |" % (cell, " | ".join(row)))
        print("| median | " + " | ".join("%.3f" % st.median(agg[f]) if agg[f] else "-" for f in forms) + " |")
        print("branches/call:")
        for cell in sorted({c for c, _, _ in data}):
            fl = data.get((cell, "floor", ppm))
            if not fl:
                continue
            print("  %-4s " % cell + " ".join("%s=%.1f" % (f, (data[(cell, f, ppm)][0].get("branches", 0) - fl[0].get("branches", 0)) / data[(cell, f, ppm)][1]) for f in forms if (cell, f, ppm) in data))


def main():
    d, sec = sys.argv[1], sys.argv[2]
    R, by, band = load(d)
    print("rows %d, band %.3f" % (len(R), band))
    fn = {"verdict": sec_verdict, "reset": sec_reset, "mask_ring": sec_mask_ring, "adapt": sec_adapt,
          "k": sec_k, "percall": sec_percall, "losers": sec_losers}
    if sec == "perf":
        sec_perf(by, d)
    elif sec == "all":
        for s in fn:
            print("\n======", s)
            fn[s](by, band)
        sec_perf(by, d)
    else:
        fn[sec](by, band)


if __name__ == "__main__":
    main()
