#!/usr/bin/env python3
"""walk_survey: classify the measured excess walks.

    analyze.py work/res_bench.tsv work/res_corpus.tsv work/bench_times.tsv OUTDIR

Every number in docs/dev/walk_survey.md comes from this script's outputs.

A ROW is one (pattern, config, regime, subject) run of the instrument
(wsdrv.c). Each CLASS is a predicate on the row's stamps/facts plus a
GRATUITOUS-BYTE count G read off the row's per-phase columns:

  K1  end-pinned locator   view 1/2 (every alternative ends in $/\\Z/\\z, not
                           (?m)), search/find-all: G = T - (span + 1) on a
                           match, T - 1 on none (the reverse-from-end walk
                           reads the match and one byte; D156's locator)
  K2  start-pinned reverse start_anchor=anchored and the reverse pass ran:
                           G = T_rev (the start IS search_from)
  K3  fixed-width reverse  cwmax == minw > 0 (byte encoding) and the reverse
                           pass ran: G = T_rev (start = end - width)
  K4  landing-start reverse (search rows only) the match starts where the
                           forward machine first stepped (s == lo_fwd) and
                           the reverse pass ran: G = T_rev -- conditional: an
                           anchored attempt at the landing would have
                           answered; it costs where that attempt fails
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
    if view in ("1", "2") and (search or fa):
        lb = (e - s + 1) if rc == 1 else 1
        g["K1"] = max(0, T - lb)
    if t["rev"] > 0 and r.get("start_anchor") == "anchored":
        g["K2"] = t["rev"]
    elif t["rev"] > 0 and byte and r["cwmax"] == r["minw"] and I(r["minw"]) > 0:
        g["K3"] = t["rev"]
    elif t["rev"] > 0 and search and rc == 1 and r.get("lo_fwd") not in ("", "-1") and I(r["lo_fwd"]) == s:
        g["K4"] = t["rev"]
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
    classes = ["K1", "K2", "K3", "K4", "K5", "K5m", "K6", "K7", "K8", "K9", "K10", "K11"]
    for pop, rows in pops.items():
        anch = {}
        for r in rows:
            if r["config"] == "anch" and not r.get("_bad"):
                anch[(r["pid"], r["subject"])] = sum(I(r.get("U_" + p)) for p in ("fwd", "anc", "vm", "endw", "rev"))
        bad = collections.Counter(r["_bad"] for r in rows if r.get("_bad"))
        live = [r for r in rows if not r.get("_bad") and r["config"] != "anch"]
        P("== population %s: %d rows (%d live, refused/failed: %s), %d patterns" % (
            pop, len(rows), len(live), dict(bad), len({r["pid"] for r in rows})))
        per = collections.defaultdict(lambda: collections.Counter())   # (pid,config,regime) -> sums
        meta = {}
        for r in live:
            k = (r["pid"], r["config"], r["regime"])
            g = classify(r, anch)
            c = per[k]
            c["T"] += I(r["T"]); c["U"] += I(r["U"]); c["n"] += I(r["n"]); c["rows"] += 1
            c["LB"] += lower_bound(r)
            c["T_scan"] += I(r.get("T_scan"))
            for kk, v in g.items():
                c["G_" + kk] += v
                c["hit_" + kk] += 1
            for p in PH:
                c["T_" + p] += I(r.get("T_" + p))
            meta[k] = r
        # class table
        P("-- class totals over (pattern, config, regime) cells, %s" % pop)
        P("class\tcells\tpatterns\tG_bytes\tT_bytes_of_those_cells\tG/T\tmax_cell_G/n")
        for cl in classes:
            ks = [k for k, c in per.items() if c["G_" + cl] > 0]
            if not ks:
                P("%s\t0" % cl); continue
            G = sum(per[k]["G_" + cl] for k in ks); TT = sum(per[k]["T"] for k in ks)
            mx = max(per[k]["G_" + cl] / max(1, per[k]["n"]) for k in ks)
            P("%s\t%d\t%d\t%d\t%d\t%.3f\t%.2f" % (cl, len(ks), len({k[0] for k in ks}), G, TT, G / max(1, TT), mx))
        # per-cell table with impact
        fo = open(os.path.join(out, "cells_%s.tsv" % pop), "w")
        hdr = ["pid", "config", "regime", "subjects", "n", "T", "U", "LB", "T_over_LB", "T_scan"] + \
              ["G_" + c for c in classes] + ["G_res", "ENGINE", "DFA_SCAN", "DFA_PREFILTER", "DFA_START",
              "DFA_MATCH", "REQ_RUN", "REQ_HANDOFF", "VM_PREFILTER", "view", "start_anchor", "cwmax", "minw",
              "bench_ns", "best_other_ns", "est_ns_lost", "dominant"]
        fo.write("\t".join(hdr) + "\n")
        for k, c in sorted(per.items()):
            r = meta[k]
            gs = {cl: c["G_" + cl] for cl in classes}
            gsum = sum(v for kk, v in gs.items() if kk not in ("K9", "K10"))
            res = max(0, c["T"] - c["LB"] - gsum)
            bn = bo = el = ""
            if pop == "bench":
                x = tm.get((k[0], k[2]))
                if x:
                    v = x["pcrec_caps_ns" if k[1] == "default" else "pcrec_nocaps_ns"]
                    if v:
                        bn = float(v)
                        bo = x["best_other_ns"]
                        el = "%.1f" % (bn * min(1.0, gsum / max(1, c["T"])))
            dom = max(gs, key=lambda z: gs[z]) if any(gs.values()) else ""
            fo.write("\t".join(str(x) for x in [k[0], k[1], k[2], c["rows"], c["n"], c["T"], c["U"], c["LB"],
                     "%.3f" % (c["T"] / max(1, c["LB"])), c["T_scan"]] + [gs[cl] for cl in classes] +
                     [res, r.get("ENGINE"), r.get("DFA_SCAN"), r.get("DFA_PREFILTER"), r.get("DFA_START"),
                      r.get("DFA_MATCH"), r.get("REQ_RUN"), r.get("REQ_HANDOFF"), r.get("VM_PREFILTER"),
                      r["view"], r.get("start_anchor"), r["cwmax"], r["minw"], bn, bo, el, dom]) + "\n")
        fo.close()
    rep.close()
    print(open(os.path.join(out, "summary.txt")).read())


if __name__ == "__main__":
    main()
