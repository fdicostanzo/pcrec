#!/usr/bin/env python3
"""[OPT-LITSCAN] S1 census: which artifacts the S1 design would move, and how.

Drives a PROBE compiler (probe_patch.py applied to a scratch `git archive` of
the design's base; it prints one `S1\t...` line per compile on stderr at the
`<PREFIX>_REQ_WHY` stamp site, read off the SAME derivations the emitter
uses: req_admit, unanch_start, dfa_pf_of, the offset-k walk). Nothing here
times anything; every column is a compile-time fact.

Populations (the reqpos census's own, ../c2/reqpos_census.py):
  bench   every pcrec-bench bench/*/patterns/*.rx, under `--features all`
          and `--features all --no-captures` (the bench's two auto testees)
  corpus  every pattern/pattern-esc row of every shipped .rxt, `--features
          all`, default options (a row's own flags are NOT applied -- the
          reqpos census's convention; a prediction, not the gate)

Classes (docs/design/litscan_s1.md §6):
  A  run pre-check; the DFA scan's CURRENT offset-set selection already
     verifies the run at its pinned offsets          -> pre-check ELIDED
  B  run pre-check; run pinned at a fixed offset; no k-set selected
                                                     -> run-pinned k-set + ELIDED
  C  run pinned; a k-set selected that does not verify it -> unchanged
  D  run pre-check; run NOT at a fixed offset (floating)  -> unchanged
  E  one-byte pre-check; offset-set prefilter scanning the same byte
                                                     -> ELIDED (G1 widened)
  V  pre-check emitted on an artifact with no DFA scan (VM) -> unchanged
  P  no pre-check change; the offset-set verify holds >=2 contiguous
     singleton verify offsets                        -> verify re-spelled (P4)
  -  none of the above                               -> unchanged
The `p4` column flags the verify re-spelling on ANY class.

Env: PROBE (probe build/pcrec), PCREC (any build, for --list-source),
BENCH, CORPUS, OUT.
"""
import os, sys, subprocess, tempfile, collections
sys.dont_write_bytecode = True
E = os.environ
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "c2"))
from reqpos_census import bench_pop, corpus_pop  # noqa: E402


def probe(pat, extra):
    fd, tmp = tempfile.mkstemp(suffix=".c")
    os.close(fd)
    try:
        r = subprocess.run([E["PROBE"], "-p", "rx", "--features", "all"] + extra +
                           ["-o", tmp, "--pattern", pat],   # BYTES: a str argv is re-encoded UTF-8
                           capture_output=True, timeout=120, env=dict(E, S1PROBE="x"))
    finally:
        for f in (tmp, tmp[:-2] + ".h"):
            if os.path.exists(f):
                os.unlink(f)
    for ln in r.stderr.decode("latin-1").split("\n"):
        if ln.startswith("S1\t"):
            return dict(kv.split("=", 1) for kv in ln.split("\t")[2:])
    return None


def chains(sel, scank, walk):
    """maximal contiguous runs (length >= 2) of singleton VERIFY offsets"""
    offs = sorted(o for o in sel if o != scank and o < len(walk) and walk[o] is not None)
    out, cur = [], []
    for o in offs:
        if cur and o == cur[-1] + 1:
            cur.append(o)
        else:
            if cur:
                out.append(cur)
            cur = [o]
    if cur:
        out.append(cur)
    return [c for c in out if len(c) >= 2]


def run_bytes(d):
    """decoded req_run.bytes, or None if there is no run"""
    if d["run"] == "-":
        return None
    return [int(d["run"][2 * i:2 * i + 2], 16) for i in range(len(d["run"]) // 2)]


def clause3b(d, pin, idx):
    """litscan_s1.md Section 1.1 clause 3's SECOND disjunct: the model
    selected nothing (no k-set), the pick's offset s = pin + idx is 0, and
    the offset-0 filter is the plain `memchr` form on exactly
    req_run.bytes[idx] -- i.e. the SAME scan req-byte already runs, at the
    SAME offset the run needs it at. Checked explicitly (not inferred from
    idx/pin alone) per S1 review C2: the memchr byte must equal run[idx]."""
    rb = int(d["rb"])
    rbytes = run_bytes(d)
    return pin + idx == 0 and d["pf"] == "memchr" and rbytes is not None and rb == rbytes[idx]


def classify(d):
    walk = [None if t.startswith("*") else int(t, 16) for t in d["walk"].split(".") if t]
    sel = [int(x.rstrip("*")) for x in d["sel"].split(",") if x]
    scank, rb = int(d["scank"]), int(d["rb"])
    pofs = d["pf"].startswith("offset-set")
    p4 = bool(pofs and chains(sel, scank, walk))
    if d["why"] == "emitted":
        if d["dscan"] == "0":
            return "V", p4
        if d["run"] != "-":
            pin, idx = int(d["pin"]), int(d["idx"])
            if pin < 0:
                return "D", p4
            if d["implies"] == "1":
                return "A", p4
            if not sel and clause3b(d, pin, idx):
                return "B", p4
            return "C", p4
        if pofs and 0 <= scank < len(walk) and walk[scank] == rb:
            return "E", p4
        return "-", p4
    return ("P" if p4 else "-"), p4


def main():
    out = open(os.path.join(E["OUT"], "census.tsv"), "w")
    out.write("# [OPT-LITSCAN] S1 census (docs/design/litscan_s1.md §6); "
              "produced by census.py over a probe_patch.py build of b5c1423b\n")
    out.write("pop\tid\tcfg\tclass\tp4\twhy\tpf\trb\trun\tidx\twalk\tsel\tpin\n")
    tally = collections.Counter()
    pops = [("bench", bench_pop(), [("caps", []), ("nocaps", ["--no-captures"])]),
            ("corpus", corpus_pop(), [("caps", [])])]
    for pname, rows, cfgs in pops:
        for rid, pat in rows:
            for cname, extra in cfgs:
                d = probe(pat, extra)
                if d is None:
                    tally[(pname, cname, "refused")] += 1
                    continue
                cls, p4 = classify(d)
                tally[(pname, cname, cls)] += 1
                if p4 and cls != "P":
                    tally[(pname, cname, cls + "+p4")] += 1
                out.write("\t".join([pname, rid, cname, cls, str(int(p4)), d["why"], d["pf"],
                                     d["rb"], d["run"], d["idx"], d["walk"], d["sel"],
                                     d["pin"]]) + "\n")
    with open(os.path.join(E["OUT"], "census_summary.txt"), "w") as s:
        for k in sorted(tally):
            line = "\t".join(k) + "\t" + str(tally[k])
            print(line)
            s.write(line + "\n")


if __name__ == "__main__":
    main()
