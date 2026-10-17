#!/usr/bin/env python3
"""clsmask_candidates: population-wide census of the instrument's sites and
dynamic tests (the memo's section 2 numbers).

    census.py WORK ANADIR > results/census.txt

Static: program sites by form x kind, classes by size band, run sites and
their IR possessify verdict, per config. Dynamic (PANEL subjects, summed over
every artifact of the config): program tests by form and by kind, start-skip
tests, and the share of tests at classes of each size band.
"""
import collections, gzip, os, sys

WORK, ANA = sys.argv[1], sys.argv[2]
arts = {}
for i, ln in enumerate(gzip.open(os.path.join(ANA, "artifacts.tsv.gz"), "rt").read().split("\n")):
    f = ln.split("\t")
    if i == 0:
        hdr = f; continue
    if len(f) > 3:
        r = dict(zip(hdr, f)); arts[(r["h"], r["config"])] = r
site = {}
for ln in open(os.path.join(WORK, "static.tsv"), errors="replace").read().split("\n")[1:]:
    f = ln.split("\t")
    if len(f) > 11 and f[3] == "site":
        site[(f[0], f[1], int(f[4]))] = (f[5], f[6], int(f[10]), f[7])


def band(form, n):
    if form == "ucls": return "utf8-cp"
    if n == 1: return "1"
    if n == 2: return "2"
    if n <= 16: return "3-16"
    if n <= 64: return "17-64"
    if n <= 192: return "65-192"
    return "193-255"


for cfg in ("vm", "auto"):
    keys = {k for k in arts if k[1] == cfg}
    print("== config %s: %d VM-routed artifacts with rows" % (cfg, len(keys)))
    fk = collections.Counter(); bands = collections.Counter(); runs = collections.Counter()
    for (h, c, s), (kind, form, n, lab) in site.items():
        if c != cfg or kind == "start":
            continue
        fk[(form, kind)] += 1; bands[band(form, n)] += 1
    print("static program sites by form x kind:")
    for (form, kind), n in sorted(fk.items(), key=lambda x: -x[1]):
        print("  %-7s %-7s %6d" % (form, kind, n))
    print("static program sites by class-size band: " + ", ".join("%s %d" % kv for kv in sorted(bands.items())))
    nr = sum(int(arts[k]["nrun"]) for k in keys); npo = sum(int(arts[k]["nrun_poss"]) for k in keys)
    print("run sites: %d, of them POSSESSIFIED per the IR strategies table: %d (%.1f%%)" % (nr, npo, 100.0 * npo / max(nr, 1)))
    st = collections.Counter(arts[k]["strats"] for k in keys)
    print("RX_VM_STRATS stamps: " + ", ".join("%s %d" % kv for kv in st.most_common()))
    # dynamic, panel, over three slices (the quadratic RESCAN artifacts --
    # panel re-visit >= 8 -- dominate a plain sum)
    def resc(k):
        return float(arts[k].get("panel_rev") or 0) >= 8

    def realp(k):
        return any(x in arts[k]["sources"].split(",") for x in ("bench", "rw", "ref"))
    slices = [("all", lambda k: True), ("non-RESCAN", lambda k: not resc(k)),
              ("REAL non-RESCAN", lambda k: realp(k) and not resc(k))]
    rows = [ln.split("\t") for ln in open(os.path.join(WORK, "runs.tsv"), errors="replace").read().split("\n")[1:]]
    for name, keep in slices:
        T_form = collections.Counter(); T_kind = collections.Counter(); T_band = collections.Counter(); n_tot = 0
        arts_in = set()
        for f in rows:
            if len(f) < 16 or f[1] != cfg or f[3] != "panel" or f[5] == "-" or (f[0], f[1]) not in arts or not keep((f[0], f[1])):
                continue
            arts_in.add(f[0])
            n_tot += int(f[5])
            if f[15] == "-":
                continue
            for x in f[15].split(";"):
                s2, t = (int(y) for y in x.split(":"))
                kind, form, n, lab = site.get((f[0], f[1], s2), ("?", "?", 0, ""))
                T_kind[kind] += t
                if kind != "start":
                    T_form[form] += t; T_band[band(form, n)] += t
        tp = sum(T_form.values())
        print("PANEL dynamic, slice %s (%d artifacts): %d subject bytes, %d program tests (%.3f per byte), %d start-skip tests (%.3f per byte)"
              % (name, len(arts_in), n_tot, tp, tp / max(n_tot, 1), T_kind["start"], T_kind["start"] / max(n_tot, 1)))
        print("  program tests by form: " + ", ".join("%s %.1f%%" % (k, 100.0 * v / max(tp, 1)) for k, v in T_form.most_common()))
        print("  program tests by kind: " + ", ".join("%s %.1f%%" % (k, 100.0 * v / max(tp, 1)) for k, v in T_kind.most_common() if k != "start"))
        print("  program tests by class-size band: " + ", ".join("%s %.1f%%" % (k, 100.0 * v / max(tp, 1)) for k, v in sorted(T_band.items())))
    print()
