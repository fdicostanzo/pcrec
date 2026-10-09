#!/usr/bin/env python3
"""walk_survey: classify the measured excess walks.

    analyze.py work/res_bench.tsv work/res_corpus.tsv work/bench_times.tsv OUTDIR

Every number in docs/dev/walk_survey.md comes from this script's outputs.

A ROW is one (pattern, config, regime, subject) run of the instrument
(wsdrv.c). Each CLASS is a predicate on the row's stamps/facts plus a
GRATUITOUS-BYTE count G read off the row's per-phase columns:

  K1  end-pinned locator   view 1/2 (every alternative ends in $/\\Z/\\z, not
                           (?m)), not start-anchored, search/find-all: G = T - (span + 1) on a
                           match, T - 1 on none (the reverse-from-end walk
                           reads the match and one byte; D156's locator)
  K2  start-pinned reverse start_anchor=anchored and the reverse pass ran:
                           G = T_rev (the start IS search_from)
  K3  fixed-width reverse  cwmax == minw > 0 (byte encoding) and the reverse
                           pass ran: G = T_rev (start = end - width)
  K4  landing-start reverse per call (wsdrv's landing test): the match
                           starts at the first byte the forward machine
                           stepped in that call, and the reverse pass ran:
                           G = that call's reverse bytes (land_rev) -- the
                           start was the landing; removing the pass needs a
                           compile-time fact (every start-set byte begins a
                           match) or an anchored attempt at the landing
  K5  find-all re-scan     find-all: bytes each call read PAST its match end
                           (re-read by the next call), by phase: G = A_pre +
                           A_skip (scans); K5m = A_fwd + A_anc + A_vm + A_rev
                           (machine lookahead) reported apart
  K6  repeated pre-check   one call's pre-check reading bytes more than once
                           (k-variant memchr passes, candidate re-checks):
                           G = T_pre - U_pre (search rows)
  K7  pre-check then engine the engine re-reads bytes the pre-check
                           already scanned: G = overlap(pre, skip|fwd|vm|anc)
                           (search rows; the K82 hand-off's territory)
  K8  match-regime overread the anchored question (match regime) reads more
                           than the anchored reference \\A(?:P) needs:
                           G = U - U_machine(anch) on the same subject
  K9  hybrid span re-walk  VM_PREFILTER=hybrid: the VM re-reads the span the
                           DFA proved: G = max(ovl(fwd,vm), ovl(rev,vm))
                           (the capture finisher; required when the pattern
                           delivers captures)
  K10 VM re-reads          T_vm - U_vm on VM artifacts (backtracking and
                           per-start re-attempts; algorithmic)
  K11 DFA attempt-scan     DFA_SCAN=attempt: G = T_fwd - U_fwd
  RES residual             T - LB - (the classes above), LB = e - search_from
                           on a match (span+1 under K1; e under K2), n on
                           none; the unexplained excess, ranked to find NEW
                           classes
"""
import csv, collections, math, os, sys

PH = ["pre", "skip", "fwd", "rev", "anc", "vm", "endw", "misc", "unk"]
csv.field_size_limit(1 << 30)


def I(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return 0


def load(path):
    rows = []
    if not os.path.exists(path):
        return rows
    for r in csv.DictReader(open(path), delimiter="\t"):
        if r["rc"] in ("REFUSED", "BUILDFAIL", "TIMEOUT", ""):
            r["_bad"] = r["rc"] or "?"
        rows.append(r)
    return rows


def ovl(r):
    d = {}
    o = r.get("ovl", "") or "-"
    if o != "-":
        for kv in o.split(";"):
            k, v = kv.split("=")
            d[tuple(k.split("."))] = int(v)
    return d


def pair(d, a, b):
    return d.get((a, b), d.get((b, a), 0))


def classify(r, anch):
    """-> dict class -> G bytes (only classes that fire)."""
    if r.get("_bad"):
        return {}
    g = {}
    reg = r["regime"]
    search = reg in ("search", "search_short")
    fa = reg in ("findall", "throughput")
    n, s, e, T, U = I(r["n"]), I(r["s"]), I(r["e"]), I(r["T"]), I(r["U"])
    rc = I(r["rc"])
    t = {p: I(r.get("T_" + p)) for p in PH}
    u = {p: I(r.get("U_" + p)) for p in PH}
    a = {p: I(r.get("A_" + p)) for p in PH}
    ov = ovl(r)
    view = r["view"]
    byte = r["enc"] == "byte"
    if reg == "match":
        k = (r["pid"], r["subject"])
        if k in anch:
            g["K8"] = max(0, U - anch[k])
        return g
    if view in ("1", "2") and (search or fa) and r.get("start_anchor") != "anchored":
        lb = (e - s + 1) if rc == 1 else 1
        g["K1"] = max(0, T - lb)
    if t["rev"] > 0 and r.get("start_anchor") == "anchored":
        g["K2"] = t["rev"]
    elif t["rev"] > 0 and byte and r["cwmax"] == r["minw"] and I(r["minw"]) > 0:
        g["K3"] = t["rev"]
    elif I(r.get("land_rev")) > 0:
        g["K4"] = I(r["land_rev"])
    if fa:
        if a["pre"] + a["skip"]:
            g["K5"] = a["pre"] + a["skip"]
        m = a["fwd"] + a["anc"] + a["vm"] + a["rev"] + a["endw"]
        if m:
            g["K5m"] = m
    if search:
        if t["pre"] > u["pre"]:
            g["K6"] = t["pre"] - u["pre"]
        o = max(pair(ov, "pre", x) for x in ("skip", "fwd", "vm", "anc", "endw"))
        if o:
            g["K7"] = o
    if r.get("VM_PREFILTER") == "hybrid":
        o = max(pair(ov, "fwd", "vm"), pair(ov, "rev", "vm"))
        if o:
            g["K9"] = o
    if r.get("ENGINE") == "vm" and t["vm"] > u["vm"]:
        g["K10"] = t["vm"] - u["vm"]
    if r.get("DFA_SCAN") == "attempt" and t["fwd"] > u["fwd"]:
        g["K11"] = t["fwd"] - u["fwd"]
    return g


def lower_bound(r):
    n, s, e, rc = I(r["n"]), I(r["s"]), I(r["e"]), I(r["rc"])
    reg = r["regime"]
    if reg in ("findall", "throughput"):
        return n
    if r["view"] in ("1", "2"):
        return (e - s + 1) if rc == 1 else 1
    if r.get("start_anchor") == "anchored":
        return e if rc == 1 else 1
    return e if rc == 1 else n


CLASSES = ["K1", "K2", "K3", "K4", "K5", "K5m", "K6", "K7", "K8", "K9", "K10", "K11"]
# K9 (the capture finisher's span walk) and K10 (VM backtracking/re-attempts)
# are REPORTED but not summed as gratuitous: the first is required wherever
# captures are delivered, the second is the VM's algorithm, not a pass a
# compile-time fact removes. K0: at -O0 the skip loop's last test and the
# forward machine's first step load the SAME landing byte (gcc -O2 keeps it in
# a register); ovl(skip, fwd) is subtracted from the residual, not a class.
SUMMED = ["K1", "K2", "K3", "K4", "K5", "K5m", "K6", "K7", "K8", "K11"]
LOCFIN = {"K1": "locator", "K2": "finisher", "K3": "finisher", "K4": "finisher", "K5": "locator (gate)",
          "K5m": "locator", "K6": "locator (gate)", "K7": "locator (gate)", "K8": "locator",
          "K9": "finisher", "K10": "both", "K11": "locator"}


def gsum(gs):
    """K1 counts every byte past the span, so it subsumes the reverse and
    pre-check classes on the same cell."""
    if gs.get("K1"):
        return gs["K1"] + gs.get("K11", 0)
    return sum(gs.get(k, 0) for k in SUMMED)


def main():
    rb, rcorp, times, out = sys.argv[1:5]
    os.makedirs(out, exist_ok=True)
    pops = {"bench": load(rb), "corpus": load(rcorp)}
    tm = {}
    for x in csv.DictReader(open(times), delimiter="\t"):
        tm[(x["set"] + "/" + x["pattern"], x["regime"])] = x
    rep = open(os.path.join(out, "summary.txt"), "w")

    def P(*a):
        print(*a, file=rep)
    allcells = {}
    for pop, rows in pops.items():
        anch = {}
        for r in rows:
            if r["config"] == "anch" and not r.get("_bad"):
                anch[(r["pid"], r["subject"])] = sum(I(r.get("U_" + p)) for p in ("fwd", "anc", "vm", "endw", "rev"))
        bad = collections.Counter((r["config"], r["_bad"]) for r in rows if r.get("_bad"))
        live = [r for r in rows if not r.get("_bad") and r["config"] != "anch"]
        P("== population %s: %d rows, %d live (config default/nocaps), %d patterns; not run: %s" % (
            pop, len(rows), len(live), len({r["pid"] for r in rows}), dict(bad)))
        unk = sum(I(r.get("T_unk")) for r in live); tot = sum(I(r["T"]) for r in live)
        P("   loads through an UNCLASSIFIED site: %d of %d (%.5f%%)" % (unk, tot, 100.0 * unk / max(1, tot)))
        per = collections.defaultdict(lambda: collections.Counter())
        meta = {}
        for r in live:
            k = (r["pid"], r["config"], r["regime"])
            g = classify(r, anch)
            c = per[k]
            c["T"] += I(r["T"]); c["U"] += I(r["U"]); c["n"] += I(r["n"]); c["rows"] += 1
            c["LB"] += lower_bound(r)
            c["K0"] += pair(ovl(r), "skip", "fwd")
            c["T_scan"] += I(r.get("T_scan"))
            for kk, v in g.items():
                c["G_" + kk] += v
            for p in PH:
                c["T_" + p] += I(r.get("T_" + p))
            meta[k] = r
        cells = []
        for k, c in sorted(per.items()):
            r = meta[k]
            gs = {cl: c["G_" + cl] for cl in CLASSES}
            gg = gsum(gs)
            res = max(0, c["T"] - c["LB"] - gg - c["K0"] - gs["K9"] - gs["K10"])
            bn = bo = ""
            if pop == "bench":
                x = tm.get((k[0], k[2]))
                if x:
                    v = x["pcrec_caps_ns" if k[1] == "default" else "pcrec_nocaps_ns"]
                    if v:
                        bn = float(v); bo = x["best_other_ns"]
            cells.append(dict(pid=k[0], config=k[1], regime=k[2], c=c, gs=gs, gsum=gg, res=res, bn=bn, bo=bo, r=r))
        allcells[pop] = cells
        fo = open(os.path.join(out, "cells_%s.tsv" % pop), "w")
        hdr = ["pid", "config", "regime", "subjects", "n", "T", "U", "LB", "T_over_LB", "T_scan"] + \
              ["G_" + c for c in CLASSES] + ["G_sum", "G_res", "ENGINE", "DFA_SCAN", "DFA_PREFILTER", "DFA_START",
              "DFA_MATCH", "REQ_RUN", "REQ_HANDOFF", "VM_PREFILTER", "view", "start_anchor", "cwmax", "minw",
              "bench_ns", "best_other_ns"] + ["est_ns_" + c for c in CLASSES]
        fo.write("\t".join(hdr) + "\n")
        for x in cells:
            c, r, gs = x["c"], x["r"], x["gs"]
            est = ["%.1f" % (x["bn"] * gs[cl] / max(1, c["T"])) if x["bn"] != "" else "" for cl in CLASSES]
            fo.write("\t".join(str(v) for v in [x["pid"], x["config"], x["regime"], c["rows"], c["n"], c["T"], c["U"],
                     c["LB"], "%.3f" % (c["T"] / max(1, c["LB"])), c["T_scan"]] + [gs[cl] for cl in CLASSES] +
                     [x["gsum"], x["res"], r.get("ENGINE"), r.get("DFA_SCAN"), r.get("DFA_PREFILTER"), r.get("DFA_START"),
                      r.get("DFA_MATCH"), r.get("REQ_RUN"), r.get("REQ_HANDOFF"), r.get("VM_PREFILTER"),
                      r["view"], r.get("start_anchor"), r["cwmax"], r["minw"], x["bn"], x["bo"]] + est) + "\n")
        fo.close()
        P("-- %s: per class. cells = (pattern, config, regime) cells where G > 0; G/n = gratuitous bytes per"
          " subject byte over the cell's subjects; est_ms = sum over bench cells of pcrec median_ns x G/T"
          " (assumes a uniform per-byte cost across phases; scan phases are cheaper, so an upper estimate"
          " for K5/K6/K7)" % pop)
        P("class\tlocfin\tcells\tpatterns\tG_bytes\tG/T_of_cells\tmedian_G/n\tmax_G/n\test_ms(bench)\ttop cells (G/n)")
        for cl in CLASSES:
            hit = [x for x in cells if x["gs"][cl] > 0]
            if not hit:
                P("%s\t%s\t0" % (cl, LOCFIN[cl])); continue
            G = sum(x["gs"][cl] for x in hit); TT = sum(x["c"]["T"] for x in hit)
            gn = sorted(x["gs"][cl] / max(1, x["c"]["n"]) for x in hit)
            est = sum(x["bn"] * x["gs"][cl] / max(1, x["c"]["T"]) for x in hit if x["bn"] != "") / 1e6
            top = sorted(hit, key=lambda x: -(x["bn"] * x["gs"][cl] / max(1, x["c"]["T"]) if x["bn"] != "" else x["gs"][cl] / max(1, x["c"]["n"])))[:6]
            P("%s\t%s\t%d\t%d\t%d\t%.3f\t%.3f\t%.2f\t%.3f\t%s" % (
                cl, LOCFIN[cl], len(hit), len({x["pid"] for x in hit}), G, G / max(1, TT), gn[len(gn) // 2], gn[-1], est,
                "; ".join("%s[%s,%s]=%.2f" % (x["pid"], x["config"][:2], x["regime"][:6], x["gs"][cl] / max(1, x["c"]["n"])) for x in top)))
        P("-- %s: top RESIDUAL cells (T - LB - classes - K0, per subject byte): excess no class explains" % pop)
        for x in sorted(cells, key=lambda x: -x["res"] / max(1, x["c"]["n"]))[:25]:
            c = x["c"]
            P("  %-48s %-7s %-12s res/n=%.2f T/LB=%.2f %s | %s %s %s %s" % (x["pid"][:48], x["config"], x["regime"],
              x["res"] / max(1, c["n"]), c["T"] / max(1, c["LB"]),
              " ".join("%s=%.2f" % (p, c["T_" + p] / max(1, c["n"])) for p in PH if c["T_" + p]),
              x["r"].get("ENGINE"), x["r"].get("DFA_SCAN"), x["r"].get("DFA_START"), x["r"].get("VM_PREFILTER")))
    rep.close()
    print(open(os.path.join(out, "summary.txt")).read())


if __name__ == "__main__":
    main()
