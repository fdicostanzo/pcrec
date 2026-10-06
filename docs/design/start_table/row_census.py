#!/usr/bin/env python3
"""docs/design/start_table/row_census.py -- per-ROW population of every start
mechanism today, read off the EMITTED STAMPS (never off src/), over the same
corpus population scripts/emit_sweep.py sweeps (its own enumerate_corpus, so
the two cannot disagree about which patterns exist).

Why: a 0-mover emit_sweep proves nothing about a row the corpus never selects
(K35 / [MECH-REACH]). This prints, per arm (engine x encoding), how many
corpus artifacts land on each value of each start-family stamp, so the
no-mover refactor's plan can name the rows whose identity rests on a
constructed witness rather than on the sweep.

Usage: row_census.py PCREC_BIN TREE OUT_TSV [--jobs N] [--deny FLAG|all ...]
Read-only on TREE. Writes OUT_TSV (arm, stamp, value, count) and a summary
on stdout.
"""
import collections, concurrent.futures, os, re, subprocess, sys
sys.path.insert(0, os.path.join(sys.argv[2], "scripts"))
import emit_sweep as es  # noqa: E402

STAMPS = ["DFA_SCAN", "DFA_PREFILTER", "DFA_START", "VM_PREFILTER",
          "VM_PREFILTER_LANG", "VM_START", "VM_START_SCAN", "VM_RESEED",
          "REQ_WHY", "REQ_HANDOFF", "END_WINDOW", "ENGINE"]
ARMS = [("auto", "byte", []), ("vm", "byte", ["--engine=vm"]),
        ("auto", "utf8", ["-e", "utf8"]), ("vm", "utf8", ["--engine=vm", "-e", "utf8"])]
RX = re.compile(rb'^#define RX_([A-Z_]+) (.*)$', re.M)


# The DFA-shaped body's ROUTE is a function of the PREFILTER's engine
# (job->engine: ENG_UNANCH / ENG_ATTEMPT / empty), never of fit.chosen
# ([r2 sound-M1]): a VM hybrid whose prefilter machine is ENG_ATTEMPT is an
# ATTEMPT-route customer. ROUTE classes, disjoint by construction:
#   DFA-UNANCH  DFA-ATTEMPT  DFA-EMPTY     (ENGINE "dfa", by DFA_SCAN)
#   HYB-UNANCH  HYB-ATTEMPT  HYB-EMPTY     (ENGINE "vm", VM_PREFILTER "hybrid")
#   VM-ONLY                                (ENGINE "vm", VM_PREFILTER "none")
ROUTE_KEYED = ["DFA_PREFILTER", "DFA_START", "REQ_WHY", "REQ_HANDOFF",
               "VM_START", "VM_START_SCAN", "VM_RESEED", "END_WINDOW"]
SCAN_ROUTE = {'"unanchored"': "UNANCH", '"attempt"': "ATTEMPT", '"empty"': "EMPTY"}


def route_of(d):
    eng = d.get("ENGINE")
    if eng == '"dfa"':
        return "DFA-" + SCAN_ROUTE.get(d.get("DFA_SCAN"), "?")
    if eng == '"vm"':
        if d.get("VM_PREFILTER") == '"hybrid"':
            return "HYB-" + SCAN_ROUTE.get(d.get("DFA_SCAN"), "?")
        return "VM-ONLY"
    return "?"


def stamps_of(stdout):
    """The start-family stamps of one emitted artifact, plus ROUTE-keyed
    joint keys (one artifact, one route class: no double count)."""
    d = {}
    for k, v in RX.findall(stdout):
        k = k.decode()
        if k in STAMPS:
            v = v.decode().strip()
            if k == "REQ_HANDOFF" and v != '"none"':
                v = '"<K>"'
            if k == "END_WINDOW" and v != '"none"':
                v = '"<W>"'
            d[k] = v
    route = route_of(d)
    d["ROUTE"] = route
    for k in ROUTE_KEYED:
        if k in d:
            d[route + ":" + k] = d[k]
    # The start bound literals, read off the text (B1/B2/B5 have no stamp):
    m = re.search(rb"const size_t start_max = ([^;]*);", stdout)
    if m:
        d[route + ":start_max"] = ("0" if m.group(1).startswith(b"0") else
                                   "search_from" if m.group(1).startswith(b"search_from")
                                   else "n")
    if re.search(rb"const size_t attempt_max = search_from;", stdout):
        d[route + ":attempt_max"] = "search_from"
    # H1 (root-minimum-width ceiling) is read TWO ways ([r2 checks-M4 H1]):
    #  - the stamp's VALUE against the constant's printed spelling (shares
    #    PCREC_MINW_MAX with the code, so alone it is not a control);
    #  - the EMITTED TEST itself (the row's body text), which shares nothing
    #    with the constant. The census prints both; they must agree.
    m = re.search(rb'^#define RX_VM_ROOT_MINW (\S+)', stdout, re.M)
    if m:
        d["VM_ROOT_MINW_CEIL"] = "yes" if m.group(1) == b"1099511627776ULL" else "no"
        d["H1_TEST_EMITTED"] = "yes" if b"_VM_ROOT_MINW) return 0;" in stdout else "no"
    return d


def one(binp, pat, extra, want_bytes=False):
    argv = [binp.encode(), b"-p", b"rx", b"--features", b"all"] + [e.encode() for e in extra] \
        + [b"-o", b"-", b"--pattern", pat]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=30)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    d = stamps_of(r.stdout)
    return (d, r.stdout) if want_bytes else d


# [r2 checks-M4] the deny arm: every start-family deny/force flag as its own
# arm, so a row whose population is 0 at default (R6 `fixed`) is COUNTED under
# the arm that reaches it rather than asserted. The flag list is the one
# deny_census.py sweeps (one list, imported by both).
START_FLAGS = ["-fno-offset-skip", "-fno-run-prefilter", "-fno-start-set",
               "-fno-start-pinned", "-fno-req-set-lead", "-fno-req-handoff",
               "-fno-hyb-reseed", "-fno-vm-anchor-bound", "-fno-end-window",
               "-fno-req-byte", "-fno-req-run", "-fno-req-run-fold",
               "-fprefilter-collapse"]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("pcrec"); ap.add_argument("tree"); ap.add_argument("out")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--deny", action="append", default=[],
                    help="add the four base arms again under FLAG ('all' = START_FLAGS)")
    a = ap.parse_args()
    binp, tree, out, jobs = a.pcrec, a.tree, a.out, a.jobs
    flags = START_FLAGS if a.deny == ["all"] else a.deny
    arms = [(f"{e}/{c}", x) for e, c, x in ARMS]
    for fl in flags:
        arms += [(f"{e}/{c}{fl}", x + [fl]) for e, c, x in ARMS]
    pats = es.enumerate_corpus(binp, tree, 30)
    pats = sorted(set(p[2].encode("utf-8", "surrogateescape") if isinstance(p[2], str)
                      else p[2] for p in pats))
    rows = []
    print(f"corpus patterns (distinct): {len(pats)}")
    for arm, extra in arms:
        cnt = collections.Counter()
        ok = 0
        with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
            for d in ex.map(lambda p: one(binp, p, extra), pats):
                if d is None:
                    continue
                ok += 1
                for k, v in d.items():
                    cnt[(k, v)] += 1
        print(f"== {arm}: compiled {ok}")
        for (k, v), n in sorted(cnt.items()):
            rows.append((arm, k, v, n))
            print(f"   {k:28s} {v:28s} {n}")
    with open(out, "w") as f:
        f.write("arm\tstamp\tvalue\tcount\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")


if __name__ == "__main__":
    main()
