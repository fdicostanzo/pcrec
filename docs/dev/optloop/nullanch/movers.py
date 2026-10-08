#!/usr/bin/env python3
"""docs/dev/optloop/nullanch/movers.py -- [NULLABLE-ANCH] BUILD's mover manifest
(lane nullanch1). Compiles census.py's population (every corpus `pattern`/
`pattern-esc` line plus every bench pattern, byte encoding, --features all,
`-p rx`) with a REFERENCE and a WORKING pcrec and prints every pattern whose
emitted `.c` differs, with its ENGINE_SEL / VM_PREFILTER on both sides, plus
the `declined-nullable-default` count on each side.

Usage: movers.py REF_PCREC NEW_PCREC BENCH_DIR [JOBS]
Both binaries must stamp the same abi (run it before an abi bump, or point
REF at a build of the bumped tree with the change reverted)."""
import os, sys, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census as c


def run(pcrec, pat):
    import subprocess
    r = subprocess.run([pcrec, "-p", "rx", "--features", "all", "-o", "-",
                        "--pattern", pat], capture_output=True, timeout=120)
    return r.stdout if r.returncode == 0 else None


def main():
    ref, new, bench = sys.argv[1:4]
    jobs = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    pats = c.population(bench)
    order = sorted(pats)

    def job(p):
        return p, run(ref, p), run(new, p)

    esel = {"ref": 0, "new": 0}
    movers, asym, ok = [], 0, 0
    with cf.ThreadPoolExecutor(jobs) as ex:
        for p, a, b in ex.map(job, order):
            if (a is None) != (b is None):
                asym += 1
                print("ASYMMETRIC\t" + c.es.encode_escape(p))
                continue
            if a is None:
                continue
            ok += 1
            sa, sb = c.stamps(a), c.stamps(b)
            esel["ref"] += sa.get("RX_ENGINE_SEL") == "declined-nullable-default"
            esel["new"] += sb.get("RX_ENGINE_SEL") == "declined-nullable-default"
            if a != b:
                movers.append((p, sa, sb))
    print(f"population {len(order)} distinct; both compile {ok}; asymmetric {asym}")
    print(f"declined-nullable-default: ref {esel['ref']} -> new {esel['new']}")
    print(f"movers {len(movers)}:")
    for p, sa, sb in movers:
        origin = ";".join(sorted({o + ":" + n for o, n in pats[p]}))
        print("\t".join([c.es.encode_escape(p), origin,
                         sa.get("RX_ENGINE_SEL", "") + " -> " + sb.get("RX_ENGINE_SEL", ""),
                         sa.get("RX_VM_PREFILTER", "") + " -> " + sb.get("RX_VM_PREFILTER", "")]))


if __name__ == "__main__":
    main()
