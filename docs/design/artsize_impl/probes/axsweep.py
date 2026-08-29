#!/usr/bin/env python3
"""[r40 S11] Re-measure the "0 of 2,487 refused" claim off the default axis.

N depends on more than (AST, K) -- critic-sem measured -fno-length-prune moving
N 121 -> 117 on one pattern -- so the caps' zero-refusal claim, taken on the
default axis only, is not yet a claim about the axes make test-axes sweeps.
Emit only; no gcc.
"""
import sys, os
sys.path.insert(0,'/tmp/claude-1001/-home-duxevents-pcrec/2118fa38-0a1c-4bbd-ba29-87aee486bb5b/scratchpad/artsize3')
from measure import emit, scan, corpus_patterns
from concurrent.futures import ThreadPoolExecutor

AXES = [("default", []), ("engine-vm", ["--engine=vm"]),
        ("no-counter", ["-fno-counter"]), ("no-possessify", ["-fno-possessify"]),
        ("no-revdet", ["-fno-revdet"]), ("no-length-prune", ["-fno-length-prune"]),
        ("no-splice-calls", ["-fno-splice-calls"]), ("no-tiered-entry", ["-fno-tiered-entry"]),
        ("no-premul-table", ["-fno-premul-table"]), ("no-offset-skip", ["-fno-offset-skip"])]

def main():
    pats = corpus_patterns()
    out = open(sys.argv[1], "w")
    out.write("axis\tmaxN\tmaxN_pat\tmaxraw\tmaxraw_pat\tover_node_cap\tover_byte_cap\tcompiled\trefused\n")
    NODECAP, BYTECAP = 2000, 1000000
    for name, flags in AXES:
        st = {"maxN": -1, "maxNp": "", "maxraw": -1, "maxrawp": "", "nc": 0, "bc": 0, "ok": 0, "ref": 0}
        def work(p):
            t, err, _ = emit(p, extra=flags, timeout=300)
            if err: return ("ref", p, 0, 0)
            r = scan(t); return ("ok", p, r["labels"], r["total"])
        with ThreadPoolExecutor(max_workers=4) as ex:
            for kind, p, N, raw in ex.map(work, pats):
                if kind == "ref": st["ref"] += 1; continue
                st["ok"] += 1
                if N > st["maxN"]: st["maxN"], st["maxNp"] = N, p
                if raw > st["maxraw"]: st["maxraw"], st["maxrawp"] = raw, p
                if N > NODECAP: st["nc"] += 1
                if raw > BYTECAP: st["bc"] += 1
        out.write("%s\t%d\t%s\t%d\t%s\t%d\t%d\t%d\t%d\n" % (
            name, st["maxN"], st["maxNp"][:50].replace("\t"," "), st["maxraw"],
            st["maxrawp"][:50].replace("\t"," "), st["nc"], st["bc"], st["ok"], st["ref"]))
        out.flush()
        print("%-18s maxN=%-6d maxraw=%-9d over-node-cap=%d over-byte-cap=%d (ok %d / ref %d)" % (
            name, st["maxN"], st["maxraw"], st["nc"], st["bc"], st["ok"], st["ref"]), flush=True)
    out.close()

if __name__ == "__main__":
    main()
