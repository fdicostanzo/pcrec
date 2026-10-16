#!/usr/bin/env python3
"""docs/dev/lanes/pcscope/census.py -- lane pcscope's population census of the
PRESENCE pre-check and the K82 handoff (D161 addendum 14, the merged window
request). Read-only: compiles patterns with a -DPCREC_CAND_TRACE build of main
and tallies, per artifact, what the pre-check site and the handoff decided.

Usage:
  python3 -I census.py TRACE_PCREC MAIN_TREE OUT_DIR [JOBS]

TRACE_PCREC  a pcrec built from main with CFLAGS="-O2 -g -DPCREC_CAND_TRACE"
MAIN_TREE    the main checkout whose tests/**/*.rxt and
             docs/dev/lanes/rwquest/questions.tsv are the populations
OUT_DIR      where rows.tsv (one row per artifact) and summary.txt go

Populations (arms):
  corpus/default   every distinct corpus pattern, -p rx --features all
  corpus/vm        the same, --engine=vm (no DFA scan in front: K65's route)
  corpus/utf8      the same, -e utf8 (rate NONE under the default analysis)
  rwquest          the 177 blinded questions with their own flags
                   (i/m/s inline; utf -> -e utf8; ucp -> --ucp)

Per artifact, from the trace (CANDTRACE records) and the stamps:
  admit      RX_REQ_WHY (emitted/none/one-attempt/dominated), with
             `set-leads` split out of `emitted` by the req-gate record
  site       req-site (nothing/declined/run/byte)
  gate       req-gate (none/byte/lead-optional/lead-required)
  front      run-tests' route (dfa-scan/no-dfa-scan)
  runtests   run-tests (none/window/whole-run)  -- whole-run = K66's part
  setrest    set-rest (none/set-rest)           -- set-rest  = K65's part
  use        req-from (handoff/scan-from-startpos)
  reentry    NEXT form-fwd == handoff (the [REQ-HANDOFF-L1] re-entry)
  engine, vm_prefilter, vm_lang, dfa_prefilter, frameless: stamps
"""
import os
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

STAMPS = ("ENGINE", "REQ_BYTE", "REQ_RUN", "REQ_WHY", "REQ_HANDOFF",
          "VM_PREFILTER", "VM_PREFILTER_LANG", "DFA_PREFILTER", "VM_FRAMELESS",
          "VM_START_SCAN", "DFA_SCAN")


def decode_escape(s):
    # --list-source's escapes: \\ \t \n \r \xHH (emit_sweep.py's set)
    out, i = bytearray(), 0
    b = s.encode("utf-8", "surrogateescape")
    while i < len(b):
        c = b[i]
        if c == 0x5C and i + 1 < len(b):
            n = b[i + 1]
            if n == ord("x") and i + 3 < len(b):
                out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
            out.append({ord("t"): 9, ord("n"): 10, ord("r"): 13}.get(n, n)); i += 2
            continue
        out.append(c); i += 1
    return bytes(out)


def corpus(pcrec, tree):
    pats = set()
    for d, _, fs in os.walk(os.path.join(tree, "tests")):
        for f in fs:
            if not f.endswith(".rxt"):
                continue
            r = subprocess.run([pcrec, "--list-source", os.path.join(d, f)],
                               capture_output=True, timeout=120)
            if r.returncode != 0:
                continue
            for line in r.stdout.decode("utf-8", "surrogateescape").splitlines():
                fl = line.split("\t")
                if len(fl) >= 5 and fl[0] in ("pattern", "pattern-esc"):
                    pats.add(decode_escape(fl[4]))
    return sorted(pats)


def rwquest(tree):
    rows = []
    with open(os.path.join(tree, "docs/dev/lanes/rwquest/questions.tsv"),
              encoding="utf-8", errors="surrogateescape") as fh:
        next(fh)
        for line in fh:
            f = line.rstrip("\n").split("\t")
            qid, pat, flags, mode = f[0], f[4], f[5], f[6]
            fl = [] if flags == "-" else flags.split(",")
            inline = "".join(x for x in fl if x in ("i", "m", "s", "x"))
            extra = []
            if "utf" in fl: extra += ["-e", "utf8"]
            if "ucp" in fl: extra += ["--ucp"]
            p = ("(?%s)" % inline if inline else "") + pat
            rows.append((qid, mode, p.encode("utf-8", "surrogateescape"), extra))
    return rows


def compile_one(pcrec, pat, extra):
    argv = [pcrec, "-p", "rx", "--features", "all"] + extra + [
        "-o", "-", "--pattern", pat.decode("utf-8", "surrogateescape")]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    st = {}
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        if line.startswith("#define RX_"):
            p = line.split(None, 2)
            if len(p) == 3 and p[1][3:] in STAMPS:
                st[p[1][3:]] = p[2].strip('"')
    tr = {}
    for line in r.stderr.decode("utf-8", "replace").splitlines():
        f = line.split("\t")
        if f[0] != "CANDTRACE" or len(f) < 5:
            continue
        slot, route, row, site = f[1], f[2], f[3], f[4]
        if site in ("req-site", "req-gate", "set-rest", "req-from", "req-handoff"):
            tr[site] = row
        elif site == "run-tests":
            tr["front"], tr["runtests"] = route, row
        elif slot == "NEXT" and site == "form-fwd":
            tr["form-fwd"] = row
    why = st.get("REQ_WHY", "?")
    admit = why
    if why == "emitted" and tr.get("req-gate", "").startswith("lead"):
        admit = "set-leads"
    return {
        "admit": admit,
        "site": tr.get("req-site", "-"),
        "gate": tr.get("req-gate", "-"),
        "front": tr.get("front", "-"),
        "runtests": tr.get("runtests", "-"),
        "setrest": tr.get("set-rest", "-"),
        "use": tr.get("req-from", "-"),
        "reentry": "yes" if tr.get("form-fwd") == "handoff" else "no",
        "engine": st.get("ENGINE", "?"),
        "vm_prefilter": st.get("VM_PREFILTER", "-"),
        "vm_lang": st.get("VM_PREFILTER_LANG", "-"),
        "dfa_prefilter": st.get("DFA_PREFILTER", "-"),
        "frameless": st.get("VM_FRAMELESS", "-"),
        "handoff_k": st.get("REQ_HANDOFF", "-"),
    }


def give_up_class(r):
    """Whether the presence answer is the call's ONLY linear no-match proof
    (the K64/K65/K66 obligation) on this artifact, read off the route."""
    if r["admit"] in ("none",):
        return "no-presence"
    if r["engine"] != "vm":
        return "linear-front"            # a DFA body decides the window itself
    if r["vm_prefilter"] == "hybrid" and r["vm_lang"] == "exact":
        return "linear-front"            # an exact hybrid DFA in front
    if r["vm_prefilter"] == "hybrid":
        return "superset-front"          # count-collapsed hybrid: not a proof
    return "proof-only"                  # no DFA scan in front


COLS = ("admit", "site", "gate", "front", "runtests", "setrest", "use",
        "reentry", "engine", "vm_prefilter", "vm_lang", "dfa_prefilter",
        "frameless", "handoff_k")


def main():
    pcrec, tree, out = sys.argv[1], sys.argv[2], sys.argv[3]
    jobs = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    os.makedirs(out, exist_ok=True)
    pats = corpus(pcrec, tree)
    tasks = []
    for p in pats:
        tasks.append(("corpus/default", "-", "-", p, []))
        tasks.append(("corpus/vm", "-", "-", p, ["--engine=vm"]))
        tasks.append(("corpus/utf8", "-", "-", p, ["-e", "utf8"]))
    for qid, mode, p, extra in rwquest(tree):
        tasks.append(("rwquest", qid, mode, p, extra))
    with ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(lambda t: compile_one(pcrec, t[3], t[4]), tasks))
    summ = {}
    with open(os.path.join(out, "rows.tsv"), "w", encoding="utf-8",
              errors="surrogateescape") as fh:
        fh.write("arm\tid\tmode\tgiveup\t" + "\t".join(COLS) + "\tpattern\n")
        for t, r in zip(tasks, res):
            arm = t[0]
            c = summ.setdefault(arm, {"n": 0, "refused": 0, "keys": Counter()})
            c["n"] += 1
            if r is None:
                c["refused"] += 1
                continue
            g = give_up_class(r)
            for k in ("admit", "gate", "runtests", "setrest", "use", "reentry"):
                c["keys"][(k, r[k])] += 1
            c["keys"][("giveup", g)] += 1
            c["keys"][("admit x giveup", r["admit"] + " / " + g)] += 1
            if r["use"] == "handoff":
                c["keys"][("handoff x engine", r["engine"] + "/" + r["vm_prefilter"])] += 1
            if r["admit"] == "dominated":
                c["keys"][("dominated x front", r["engine"] + "/" + r["vm_prefilter"]
                           + "/" + r["vm_lang"] + "/" + r["dfa_prefilter"])] += 1
            if r["admit"] == "one-attempt":
                c["keys"][("one-attempt x front", r["engine"] + "/" + r["vm_prefilter"]
                           + "/" + r["vm_lang"] + "/frameless=" + r["frameless"])] += 1
            fh.write("\t".join([arm, t[1], t[2], g] + [r[k] for k in COLS] +
                               [t[3].decode("utf-8", "surrogateescape")
                                .replace("\\", "\\\\").replace("\t", "\\t")
                                .replace("\n", "\\n")]) + "\n")
    with open(os.path.join(out, "summary.txt"), "w") as fh:
        fh.write("distinct corpus patterns: %d\n" % len(pats))
        for arm, c in summ.items():
            fh.write("\n== %s: %d compiles, %d refused\n" % (arm, c["n"], c["refused"]))
            for (k, v), n in sorted(c["keys"].items()):
                fh.write("  %-22s %-50s %6d\n" % (k, v, n))
    print(open(os.path.join(out, "summary.txt")).read())


if __name__ == "__main__":
    main()
