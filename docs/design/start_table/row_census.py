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

Usage: row_census.py PCREC_BIN TREE OUT_TSV [--jobs N]
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


def one(binp, pat, extra):
    argv = [binp.encode(), b"-p", b"rx", b"--features", b"all"] + [e.encode() for e in extra] \
        + [b"-o", b"-", b"--pattern", pat]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=30)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    d = {}
    for k, v in RX.findall(r.stdout):
        k = k.decode()
        if k in STAMPS:
            v = v.decode().strip()
            if k == "REQ_HANDOFF" and v != '"none"':
                v = '"<K>"'
            if k == "END_WINDOW" and v != '"none"':
                v = '"<W>"'
            d[k] = v
    # JOINT keys: the stamp alone conflates two routes' rows.
    #  - ENG_ATTEMPT's predecessor-byte skip stamps DFA_PREFILTER "memchr",
    #    the same token as ENG_UNANCH's offset-0 memchr row;
    #  - the VM hybrid's inlined prefilter carries its own DFA_PREFILTER row.
    if d.get("DFA_SCAN") == '"attempt"':
        d["ATTEMPT:DFA_PREFILTER"] = d.get("DFA_PREFILTER", "?")
    if d.get("VM_PREFILTER") == '"hybrid"':
        d["HYBRID:DFA_PREFILTER"] = d.get("DFA_PREFILTER", "?")
        d["HYBRID:REQ_HANDOFF"] = d.get("REQ_HANDOFF", "?")
    if d.get("ENGINE") == '"vm"' and d.get("VM_PREFILTER") == '"none"':
        d["VMONLY:VM_START_SCAN"] = d.get("VM_START_SCAN", "?")
        d["VMONLY:REQ_WHY"] = d.get("REQ_WHY", "?")
    # ROOT_MINW at the ceiling is the root-minimum-width row's predicate
    m = re.search(rb'^#define RX_VM_ROOT_MINW (\S+)', r.stdout, re.M)
    if m:
        d["VM_ROOT_MINW_CEIL"] = "yes" if m.group(1) == b"1099511627776ULL" else "no"
    return d


def main():
    binp, tree, out = sys.argv[1], sys.argv[2], sys.argv[3]
    jobs = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[4] == "--jobs" else 8
    pats = es.enumerate_corpus(binp, tree, 30)
    pats = sorted(set(p[2].encode("utf-8", "surrogateescape") if isinstance(p[2], str)
                      else p[2] for p in pats))
    rows = []
    print(f"corpus patterns (distinct): {len(pats)}")
    for eng, enc, extra in ARMS:
        cnt = collections.Counter()
        ok = 0
        with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
            for d in ex.map(lambda p: one(binp, p, extra), pats):
                if d is None:
                    continue
                ok += 1
                for k, v in d.items():
                    cnt[(k, v)] += 1
        arm = f"{eng}/{enc}"
        print(f"== {arm}: compiled {ok}")
        for (k, v), n in sorted(cnt.items()):
            rows.append((arm, k, v, n))
            print(f"   {k:18s} {v:28s} {n}")
    with open(out, "w") as f:
        f.write("arm\tstamp\tvalue\tcount\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")


if __name__ == "__main__":
    main()
