#!/usr/bin/env python3
"""confirm_collect.py -- [ARTREV] S4: join the pass-1/pass-2 timing summaries and the identity logs into
the per-artifact confirmed.tsv rows (lane artconf).  Reads only files; writes confirmed.tsv on stdout.

  confirm_collect.py ROOT NAME PASS1_DIR PASS2_DIR IDLOG_DIR

A verdict is reportable ONLY from pass 2 (pad control); an arm that was not carried to pass 2 reads its
pass-1 verdict capped at NOISE ("p1-only").  Verdict text is copied from summary.txt verbatim.
"""
import os, re, sys, glob

ARM_RE = re.compile(r"^  (\S+)\s+median\s+([\d.]+)\s+IQR\s+([\d.]+)\s+vs orig\s+([+-][\d.]+)\s+\(\s*([+-][\d.]+)%\)\s+threshold\s+([\d.]+)\s+(\w+)")
LAY_RE = re.compile(r"^      layout: pad-median ([\d.]+)\s+spread across pads ([\d.]+) \(orig ([\d.]+)\)\s+pad-median delta ([+-][\d.]+) vs threshold ([\d.]+)\s+paired deltas ([^\[]*)(?:\[(.*)\])?")
SUBJ_RE = re.compile(r"^subject (\S+)\s+null-twin deviation ([\d.]+)")


def parse(path):
    out, subj, last = {}, None, None
    for ln in open(path):
        ln = ln.rstrip("\n")
        m = SUBJ_RE.match(ln)
        if m:
            subj = m.group(1)
            out[subj] = {"_null": float(m.group(2))}
            continue
        m = ARM_RE.match(ln)
        if m and subj:
            a = m.group(1)
            out[subj][a] = dict(med=float(m.group(2)), iqr=float(m.group(3)), delta=float(m.group(4)), pct=float(m.group(5)),
                                thr=float(m.group(6)), verdict=m.group(7), lay=None, note="")
            last = out[subj][a]
            continue
        m = LAY_RE.match(ln)
        if m and last is not None:
            last["lay"] = dict(pm=float(m.group(1)), spread=float(m.group(2)), ospread=float(m.group(3)), pdelta=float(m.group(4)),
                               thr=float(m.group(5)), paired=m.group(6).split())
            last["note"] = m.group(7) or ""
    return out


def repairs(idlog_dir, name, arm):
    p = os.path.join(idlog_dir, "%s__%s__plain.log" % (name, arm))
    if not os.path.exists(p):
        return "?"
    t = open(p).read()
    m = re.search(r"(\d+) give-up repair\(s\) of which (\d+) checked", t)
    st = idlog_dir and os.path.exists(os.path.join(idlog_dir, "%s__%s__strict.log" % (name, arm)))
    strict = ""
    if st:
        strict = "FAIL" if "IDENTITY FAIL" in open(os.path.join(idlog_dir, "%s__%s__strict.log" % (name, arm))).read() else "PASS"
    return "%s/%s%s" % (m.group(1), m.group(2), ("/strict=" + strict) if strict else "") if m else "?"


def main():
    root, name, p1d, p2d, idl = sys.argv[1:6]
    p1 = parse(os.path.join(p1d, "summary.txt"))
    p2 = parse(os.path.join(p2d, "summary.txt"))
    cell = p2["CELL"]
    arms = [a for a in cell if not a.startswith("_") and a not in ("orig", "orig2", "null")]
    p1arms = [a for a in p1["CELL"] if a not in ("orig", "orig2", "null", "_null") and a not in arms]
    hdr = ["arm", "lead", "cell_med_ns_B", "orig_med", "delta_ns_B", "delta_pct", "threshold", "pad_spread", "orig_pad_spread",
           "null_dev", "paired_pads_same_sign", "verdict", "pass", "layout_note", "dense", "sparse", "repairs_checked_strict"]
    print("\t".join(hdr))
    def lead(a):
        return a
    for a, src, ps in [(x, p2, "2") for x in arms] + [(x, p1, "1") for x in p1arms]:
        c = src["CELL"][a]
        o = src["CELL"]["orig"]
        L = c["lay"]
        verdict = c["verdict"]
        if ps == "1":
            verdict = "NOISE" if verdict == "NOISE" else "NOISE(p1-only:plain-" + verdict + ")"
        paired = ""
        if L:
            paired = "%d/%d" % (sum(1 for x in L["paired"] if (float(x) > 0) == (c["delta"] > 0)), len(L["paired"]))
        # sub-rows: dense / sparse verdicts from the same pass (generality rows); pad control applies only in pass 2
        d = src["dense"][a]["verdict"] if a in src.get("dense", {}) else "-"
        s = src["sparse"][a]["verdict"] if a in src.get("sparse", {}) else "-"
        print("\t".join(str(x) for x in [
            a, lead(a), "%.4f" % c["med"], "%.4f" % o["med"], "%+.4f" % c["delta"], "%+.2f" % c["pct"],
            "%.4f" % (L["thr"] if L else c["thr"]), "%.4f" % L["spread"] if L else "-", "%.4f" % L["ospread"] if L else "-",
            "%.4f" % src["CELL"]["_null"], paired, verdict, "pass" + ps, c["note"], d, s, repairs(idl, name, a)]))
    # controls: orig2 and null must read NOISE on every row
    bad = []
    for sp, per in p2.items():
        for a in ("orig2", "null"):
            if a in per and per[a]["verdict"] != "NOISE":
                bad.append("%s/%s=%s" % (sp, a, per[a]["verdict"]))
    print("# controls (orig2, null) non-NOISE rows in pass 2: %s" % (", ".join(bad) or "none"))


main()
