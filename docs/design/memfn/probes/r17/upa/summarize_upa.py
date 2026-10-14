#!/usr/bin/env python3
"""summarize_upa.py -- roll upa.py's counts.tsv into the reading's tables.

    summarize_upa.py OUTDIR [--config auto|nocaps] [--cells cells_r17.txt]
        [--compact | --rollup | --corner PPM | --dense] [--members 30-39] [--hybrid]

OUTDIR holds counts.tsv (or counts.tsv.gz, the committed form) and sites.tsv.

Per cell (one config): the search-short regime POOLED over the set's short
subjects (one activation per subject: the distribution is across subjects),
and the find-all regime per throughput subject at the STATE-LIFETIME level
(`fn:*`, one call of the function holding the site = one rx_search call for a
DFA or a prefilter-less VM site) plus the whole pass. Band: the kit's
break-even bracket B_EVEN in (1, 4) (setfind.md rev 2.3 §9.2): BELOW when the
median activation has 1 use (the kit loses at 1), ABOVE when it has >= 4 (the
kit wins at 4), IN-BRACKET for 2-3 (nothing between was timed).
"""
import argparse
import collections
import os
import sys


def _census():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "census", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "census.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_CENSUS = None


def terms(memstr):
    """An UPPER BOUND on the terms a set needs: the fewest of its maximal
    ranges, its complement's ranges (the complement form) and its greedy
    prime-cube cover (census.py's, where computed). The kit's mf_set_terms
    decides admission (K = 4); this only flags the likely population."""
    global _CENSUS
    if _CENSUS is None:
        _CENSUS = _census()
    mem = sorted(int(x, 16) for x in memstr.split(",") if x)
    if not mem:
        return 0
    inset = set(mem)
    runs = lambda xs: sum(1 for i, x in enumerate(xs) if i == 0 or xs[i - 1] != x - 1)
    comp = [x for x in range(256) if x not in inset]
    best = min(runs(mem), runs(comp) if comp else 0)
    cc = _CENSUS.cube_cover(mem)
    if cc is not None and cc >= 0:
        best = min(best, cc)
    return best


def band(med):
    if med <= 1:
        return "BELOW"
    if med >= 4:
        return "ABOVE"
    return "IN-BRACKET"


def stats(hist):
    tot = sum(hist.values())
    if not tot:
        return None
    items = sorted(hist.items())

    def q(p):
        rank = min(tot, max(1, -(-p * tot // 1)))
        acc = 0
        for u, c in items:
            acc += c
            if acc >= rank:
                return u
    ge = lambda k: sum(c for u, c in items if u >= k) / tot
    return dict(nact=tot, uses=sum(u * c for u, c in items), p10=q(.1), med=q(.5), p90=q(.9),
                max=items[-1][0], ge2=ge(2), ge4=ge(4), ge16=ge(16),
                zero=hist.get(0, 0) / tot)


def addhist(h, s):
    if s != "-":
        for p in s.split(","):
            u, c = p.split(":")
            h[int(u)] += int(c)


def pooled(mine, ix, regime):
    h = collections.Counter()
    per = []
    for r in mine:
        if r[ix["regime"]] == regime and r[ix["level"]].startswith("fn:"):
            hh = collections.Counter()
            addhist(hh, r[ix["hist"]])
            h.update(hh)
            st = stats(hh)
            per.append((r[ix["subject"]], st["med"] if st else 0, r[ix["density_ppm"]],
                        r[ix["matches"]], r[ix["hits_per_match"]]))
    return stats(h), per


def compact(a, cells, kit, siteinfo, rows, ix):
    bands = collections.Counter()
    if not a.rollup:
        print("| cell | kit | site (role, fn, \\|S\\|, terms<=) | search-short: act, median [p10, p90] max, >=2 | "
              "find-all: act, median [p10, p90] max, >=2 / >=4 / >=16 | find-all medians per subject "
              "(density ppm) | band short / find-all |")
        print("|---|---|---|---|---|---|---|")
    for c in cells:
        si = sorted(set(siteinfo.get(c, [])))
        if not si:
            continue
        mine = [r for r in rows if r[ix["cell"]] == c and r[ix["config"]] == a.config]
        ss, _ = pooled(mine, ix, "short")
        fs, per = pooled(mine, ix, "findall")
        bs = band(ss["med"]) if ss else "-"
        bf = band(fs["med"]) if fs else "-"
        k4 = "terms<=4" if min(terms(m) for _, _, _, m, _ in si) <= 4 else "terms>4"
        bands[("short", k4, bs)] += 1
        bands[("findall", k4, bf)] += 1
        if a.rollup:
            continue
        sdesc = "; ".join("%s%s, %s, %s, %d" % (r, " bounded" if b == "1" else "", fn, n, terms(m))
                          for r, fn, n, m, b in si)
        sss = ("%d, %d [%d, %d] %d, %.2f" % (ss["nact"], ss["med"], ss["p10"], ss["p90"], ss["max"], ss["ge2"])
               if ss else "-")
        fss = ("%d, %d [%d, %d] %d, %.2f / %.2f / %.2f" % (fs["nact"], fs["med"], fs["p10"], fs["p90"],
                                                          fs["max"], fs["ge2"], fs["ge4"], fs["ge16"])
               if fs else "-")
        pers = ", ".join("%s %d (%s)" % (sid, med, dens) for sid, med, dens, _, _ in per)
        print("| %s | %s | %s | %s | %s | %s | %s / %s |" % (c, kit.get(c, ""), sdesc, sss, fss, pers, bs, bf))
    if a.rollup:
        for k in sorted(bands):
            print("%s\t%s\t%s\t%d" % (k[0], k[1], k[2], bands[k]))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--config", default="auto")
    ap.add_argument("--cells")
    ap.add_argument("--dense", action="store_true", help="list dense-control candidates instead")
    ap.add_argument("--compact", action="store_true",
                    help="one row per cell x regime (find-all pooled over the throughput subjects)")
    ap.add_argument("--members", help="keep only cells whose site set is exactly this hex range, e.g. 30-39")
    ap.add_argument("--rollup", action="store_true", help="band counts over every site-bearing cell")
    ap.add_argument("--corner", type=float, metavar="PPM",
                    help="§9.2's decline corner: find-all subjects with density >= PPM and median uses < 4")
    ap.add_argument("--hybrid", action="store_true", help="keep only cells whose site is in rx_prefilter")
    a = ap.parse_args()
    cp = os.path.join(a.out, "counts.tsv")
    if not os.path.exists(cp):
        import gzip
        fh = gzip.open(cp + ".gz", "rt")
    else:
        fh = open(cp)
    rows = [l.rstrip("\n").split("\t") for l in fh]
    hdr, rows = rows[0], rows[1:]
    ix = {k: i for i, k in enumerate(hdr)}
    sites = [l.rstrip("\n").split("\t") for l in open(os.path.join(a.out, "sites.tsv"))][1:]
    siteinfo = collections.defaultdict(list)
    for s in sites:
        if s[1] == a.config and s[4] == "ok":
            siteinfo[s[0]].append((s[6], s[5], s[8], s[9], s[7]))
    order = None
    if a.cells:
        order = [l.split() for l in open(a.cells) if l.strip() and not l.startswith("#")]
    cells = [c[0] for c in order] if order else sorted(siteinfo)
    kit = {c[0]: c[1] for c in order} if order else {}
    if a.members:
        lo, hi = (int(x, 16) for x in a.members.split("-"))
        exact = ",".join("%02X" % x for x in range(lo, hi + 1))
        cells = [c for c in cells if any(m == exact for _, _, _, m, _ in siteinfo.get(c, []))]
    if a.hybrid:
        cells = [c for c in cells if any(fn == "rx_prefilter" for _, fn, _, _, _ in siteinfo.get(c, []))]
    if a.corner is not None:
        print("| cell | site (role, \\|S\\|, terms<=) | subject | density (ppm) | matches | activations | median [p10, p90] | >=2 | band |")
        print("|---|---|---|---|---|---|---|---|---|")
        for c in cells:
            si = sorted(set(siteinfo.get(c, [])))
            for r in rows:
                if (r[ix["cell"]] != c or r[ix["config"]] != a.config or r[ix["regime"]] != "findall"
                        or not r[ix["level"]].startswith("fn:")):
                    continue
                hh = collections.Counter()
                addhist(hh, r[ix["hist"]])
                st = stats(hh)
                if st and float(r[ix["density_ppm"]]) >= a.corner and st["med"] < 4:
                    print("| %s | %s | %s | %s | %s | %d | %d [%d, %d] | %.2f | %s |" % (
                        c, "; ".join("%s, %s, %d" % (x[0], x[2], terms(x[3])) for x in si), r[ix["subject"]],
                        r[ix["density_ppm"]], r[ix["matches"]], st["nact"], st["med"], st["p10"],
                        st["p90"], st["ge2"], band(st["med"])))
        return 0
    if a.compact or a.rollup:
        return compact(a, cells, kit, siteinfo, rows, ix)
    if a.dense:
        print("cell\troles\t|S|\tmembers\tengine")
        for c in sorted(siteinfo):
            for role, fn, n, mem, bnd in sorted(set(siteinfo[c])):
                if int(n) >= 10:
                    print("%s\t%s\t%s\t%s\t%s" % (c, role, n, mem[:47], fn))
        return 0
    print("| cell | kit | site | S | regime | subject | density (ppm) | matches | activations "
          "| uses/act p10 / median / p90 (max) | >=2 / >=4 / >=16 | zero | hits/match | band |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in cells:
        si = sorted(set(siteinfo.get(c, [])))
        if not si:
            print("| %s | %s | (no site in this config) |" % (c, kit.get(c, "")))
            continue
        sdesc = "; ".join("%s%s in %s" % (r, " bounded" if b == "1" else "", fn) for r, fn, n, m, b in si)
        sset = "; ".join("{%s}" % (m if int(n) <= 4 else "%s..%s (%s)" % (m[:2], m[-2:], n))
                         for r, fn, n, m, b in si)
        mine = [r for r in rows if r[ix["cell"]] == c and r[ix["config"]] == a.config]
        # search-short pooled at the fn level (one activation per subject)
        h = collections.Counter()
        nsub = 0
        for r in mine:
            if r[ix["regime"]] == "short" and r[ix["level"]].startswith("fn:"):
                addhist(h, r[ix["hist"]])
                nsub += 1
        st = stats(h)
        if st:
            print("| %s | %s | %s | %s | search-short | %d short subjects (pooled) | - | - | %d | %d / %d / %d (%d) "
                  "| %.2f / %.2f / %.2f | %.2f | - | %s |" % (
                      c, kit.get(c, ""), sdesc, sset, nsub, st["nact"], st["p10"], st["med"], st["p90"],
                      st["max"], st["ge2"], st["ge4"], st["ge16"], st["zero"], band(st["med"])))
        for r in mine:
            if r[ix["regime"]] != "findall" or not r[ix["level"]].startswith("fn:"):
                continue
            h = collections.Counter()
            addhist(h, r[ix["hist"]])
            st = stats(h)
            passuses = r[ix["uses"]]
            print("| %s | %s | | | find-all | %s (%s B) | %s | %s | %d | %d / %d / %d (%d) | %.2f / %.2f / %.2f "
                  "| %.2f | %s | %s; pass = %s uses |" % (
                      c, kit.get(c, ""), r[ix["subject"]], r[ix["bytes"]], r[ix["density_ppm"]],
                      r[ix["matches"]], st["nact"], st["p10"], st["med"], st["p90"], st["max"],
                      st["ge2"], st["ge4"], st["ge16"], st["zero"], r[ix["hits_per_match"]],
                      band(st["med"]), passuses))
    return 0


if __name__ == "__main__":
    sys.exit(main())
