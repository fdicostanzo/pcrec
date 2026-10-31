#!/usr/bin/env python3
"""Lane p1dsg3 (2026-10-29), review r5 SLOT-1: L6/L8's NEXT read, rev 1 (a live read through the
LOCATE -> NEXT -> FIRST -> PRESENCE -> LOCATE cycle) against rev 2 (a COUNTERFACTUAL read: NEXT's
selection in this compile with the walk's deny bit set, so no row reads the walk).

For every bench row that reaches L6 on stage 1 (the DFA-routed rows of rev 1's bench_stamps.txt,
whose census row is next-landmark / excl-cand / excl-lower; VM-routed rows decline at L1 and never
read NEXT), two compiles at this tree's HEAD:
  W0 = the default compile. No row carries PCREC_NO_LANDMARK_WALK today, so W0 IS the counterfactual
       world: its RX_DFA_PREFILTER is exactly the value rev 2's memo holds (NEXT_cf).
  W1 = `-fno-req-handoff`, the proxy the r5 verifier used for the walk-selected world (PRESENCE
       `dominated` removes FIRST's handoff and so NEXT's `handoff-reentry`; NEXT's other rows read no
       slot that reaches LOCATE). The proxy keeps RX_REQ_WHY "emitted", so it stands in for the
       dominated state only through the NEXT rows, which is all L6 reads.
Rev 1 has TWO fixed points on a row iff NEXT(W0) is in L6's decline set and NEXT(W1) is not.
Rev 2 reads NEXT(W0) in both worlds: one value by construction. The LEMMA rev 2 states (when the walk
is admitted, the walk world's NEXT equals NEXT_cf) is checked as: NEXT(W0) outside the decline set
=> NEXT(W1) == NEXT(W0).
Usage: PCREC=build/pcrec CORPUS=<tree> python3 -I cf_next.py  (50 compiles, one process at a time)."""
import os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
DECLINE = re.compile(r"^(offset-set|run-pinned|handoff)")
ABOVE = ("empty", "rev-end", "cover")   # LOCATE rows ahead of `landmark-walk` in cand_rows[]
STAMPS = ("ENGINE", "VM_PREFILTER", "DFA_PREFILTER", "REQ_WHY", "DFA_SCAN")


def bench_rows():
    """census.tsv's bench rows by id, plus rev 0's 5b approximation (tiers.py's bench_pop)."""
    rows = {}
    hdr = None
    for ln in open(os.path.join(os.environ["CORPUS"], "docs/design/startset/census.tsv"), encoding="utf-8"):
        if ln.startswith("#"):
            continue
        fl = ln.rstrip("\n").split("\t")
        if hdr is None:
            hdr = fl
            continue
        d = dict(zip(hdr, fl))
        if d["kind"] == "bench":
            rows["%s/%s" % (d["set"], d["name"])] = (bytes.fromhex(d["pat_hex"]), d["set"] == "utf8")
    rows["subtri/5b-mask-email~"] = (rb"[%+\-.0-9A-Za-z_]+@[0-9A-Za-z\-]+(?:\.[0-9A-Za-z\-]+)*\.[A-Za-z]{2,}", False)
    return rows


def stamps(pat, utf8, extra):
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        out = os.path.join(td, "a.c")
        cmd = [os.environ["PCREC"], "-p", "rx", "--features", "all"] + (["-e", "utf8"] if utf8 else []) + \
              extra + ["-o", out, "--pattern", pat.decode("latin-1")]
        rc = subprocess.run(cmd, capture_output=True, timeout=120).returncode
        src = open(out).read() if rc == 0 and os.path.exists(out) else ""
    return {k: (re.search(r'#define RX_%s "([^"]*)"' % k, src) or [None, "-"])[1] for k in STAMPS}, rc


def main():
    ids = []
    for ln in open(os.path.join(HERE, "..", "p1dsg2_evidence", "bench_stamps.txt")):
        if ln.startswith("#"):
            continue
        f = [x.strip() for x in ln.split("|")]
        if f[3] == "dfa":
            ids.append(f[0])
    rows = bench_rows()
    print("# id | W0 engine/vm-prefilter | W0 RX_DFA_SCAN (LOCATE) | W0 RX_DFA_PREFILTER | W0 REQ_WHY | "
          "W1 (-fno-req-handoff) RX_DFA_PREFILTER | rev 1 L6 | rev 2 L6 | lemma")
    n2 = nlem = nbad = nabove = 0
    for i in ids:
        pat, utf8 = rows[i]
        w0, rc0 = stamps(pat, utf8, [])
        w1, rc1 = stamps(pat, utf8, ["-fno-req-handoff"])
        if w0["DFA_SCAN"] in ABOVE:
            # a LOCATE row ABOVE the walk is selected (first match): the walk's predicate never runs,
            # so L6 is never read; RX_DFA_PREFILTER is NEXT's absence column ("none"), not a selection
            nabove += 1
            print("%s | %s/%s | %s | %s | %s | %s | not evaluated (%s outranks) | not evaluated | -" % (
                i, w0["ENGINE"], w0["VM_PREFILTER"], w0["DFA_SCAN"], w0["DFA_PREFILTER"], w0["REQ_WHY"],
                w1["DFA_PREFILTER"], w0["DFA_SCAN"]))
            continue
        d0 = bool(DECLINE.match(w0["DFA_PREFILTER"]))
        d1 = bool(DECLINE.match(w1["DFA_PREFILTER"]))
        rev1 = "TWO fixed points (declines walk-off, passes walk-on)" if d0 and not d1 else \
               ("declines" if d0 else "passes")
        rev2 = "declines" if d0 else "passes"
        lem = "-" if d0 else ("holds" if w1["DFA_PREFILTER"] == w0["DFA_PREFILTER"] else "FAILS")
        n2 += d0 and not d1
        nlem += lem == "holds"
        nbad += lem == "FAILS"
        print("%s | %s/%s | %s | %s | %s | %s | %s | %s | %s" % (i, w0["ENGINE"], w0["VM_PREFILTER"], w0["DFA_SCAN"],
                                                              w0["DFA_PREFILTER"], w0["REQ_WHY"], w1["DFA_PREFILTER"],
                                                              rev1, rev2, lem))
    print("# rows %d; outranked by a LOCATE row above the walk %d; rev 1 two-fixed-point rows %d; "
          "rev 2 two-fixed-point rows 0 (one read); lemma holds %d, FAILS %d" % (len(ids), nabove, n2, nlem, nbad))
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main())
