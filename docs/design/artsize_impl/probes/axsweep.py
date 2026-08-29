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
    out.write("axis\tmaxN\tmaxcode\tmaxcode_pat\tmaxtotal\tmaxtotal_pat\tover_code_cap\tover_total_cap\tcompiled\trefused\n")
    CODECAP, TOTALCAP = 500000, 1000000
    for name, flags in AXES:
        st = {"maxN": -1, "maxcode": -1, "maxcodep": "", "maxtotal": -1, "maxtotalp": "", "nc": 0, "bc": 0, "ok": 0, "ref": 0}
        def work(p):
            t, err, _ = emit(p, extra=flags, timeout=300)
            if err: return ("ref", p, 0, 0, 0)
            r = scan(t)
            # [r40 R4] CODE bytes = comment-excluded bytes OUTSIDE table
            # initializers. Exact, emitter-countable, no coefficients.
            code = r["bytes"] - r["tables"]
            return ("ok", p, r["labels"], code, r["bytes"])
        with ThreadPoolExecutor(max_workers=4) as ex:
            for kind, p, N, code, total in ex.map(work, pats):
                if kind == "ref": st["ref"] += 1; continue
                st["ok"] += 1
                if N > st["maxN"]: st["maxN"] = N
                if code > st["maxcode"]: st["maxcode"], st["maxcodep"] = code, p
                if total > st["maxtotal"]: st["maxtotal"], st["maxtotalp"] = total, p
                if code > CODECAP: st["nc"] += 1
                if total > TOTALCAP: st["bc"] += 1
        out.write("%s\t%d\t%.0f\t%s\t%d\t%s\t%d\t%d\t%d\t%d\n" % (
            name, st["maxN"], st["maxcode"], st["maxcodep"][:50].replace("\t"," "),
            st["maxtotal"], st["maxtotalp"][:50].replace("\t"," "),
            st["nc"], st["bc"], st["ok"], st["ref"]))
        out.flush()
        print("%-18s maxN=%-6d maxcode=%-9.0f maxtotal=%-9d over-code-cap=%d over-total-cap=%d (ok %d / ref %d)" % (
            name, st["maxN"], st["maxcode"], st["maxtotal"], st["nc"], st["bc"], st["ok"], st["ref"]), flush=True)
    out.close()

if __name__ == "__main__":
    main()
