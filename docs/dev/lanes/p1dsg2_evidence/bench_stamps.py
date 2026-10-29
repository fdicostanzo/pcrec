#!/usr/bin/env python3
"""Lane p1dsg2: correct the parse-only census's `next-landmark` approximation on the BENCH with the
artifacts' own stamps (review r1 D3/S2). For every bench row the census puts in next-landmark,
excl-cand or excl-lower (37 compiles, under the 50 cap), compile it and read RX_ENGINE,
RX_DFA_PREFILTER (NEXT's selection on the DFA route) and RX_VM_START_SCAN, then apply the rev-1
conjuncts the census cannot: L1 `route` (stage 1 is CR_DFA) and L7 `next-landmark` as the build reads
it (NEXT selected one of offset-set*, run-pinned*, handoff). Usage: PCREC=build/pcrec CORPUS=.
python3 -I bench_stamps.py"""
import importlib.util, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("population2", os.path.join(HERE, "population2.py"))
P2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(P2)
LANDMARK_NEXT = re.compile(r"^(offset-set|run-pinned|handoff)")
pcrec = os.environ["PCREC"]
print("# id | census row | L | RX_ENGINE | RX_DFA_PREFILTER | RX_VM_START_SCAN | rev-1 stage-1 verdict")
for r in P2.T.bench_pop():
    row, d = P2.classify(r)
    if row not in ("next-landmark", "excl-cand", "excl-lower"):
        continue
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        out = os.path.join(td, "a.c")
        cmd = [pcrec, "-p", "rx", "--features", "all"] + (["-e", "utf8"] if r["enc"] == "utf8" else []) + \
              ["-o", out, "--pattern", r["pat"].decode("latin-1")]
        rc = subprocess.run(cmd, capture_output=True, timeout=120).returncode
        src = open(out).read() if rc == 0 and os.path.exists(out) else ""
    st = {k: (re.search(r'#define RX_%s "([^"]*)"' % k, src) or [None, "-"])[1]
          for k in ("ENGINE", "DFA_PREFILTER", "VM_START_SCAN")}
    if not src:
        v = "compile failed rc=%d" % rc
    elif st["ENGINE"] != "dfa":
        v = "decline: route (%s; stage 2)" % st["ENGINE"]
    elif LANDMARK_NEXT.match(st["DFA_PREFILTER"]):
        v = "decline: next-landmark (%s)" % st["DFA_PREFILTER"]
    elif row == "next-landmark":
        v = "census approximation WRONG: NEXT is %s, row continues past L7" % st["DFA_PREFILTER"]
    else:
        v = "ADMITTED (stage 1, %s), pending rarity + POST rows" % row
    print("%s | %s | %s | %s | %s | %s | %s" % (r["id"], row, d.get("L", ""), st["ENGINE"], st["DFA_PREFILTER"],
                                              st["VM_START_SCAN"], v))
