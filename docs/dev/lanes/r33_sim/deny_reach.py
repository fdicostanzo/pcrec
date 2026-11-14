#!/usr/bin/env python3
"""docs/dev/lanes/r33_sim/deny_reach.py -- R-43 (2): which corpus patterns a kit deny MOVES, per emit_sweep cell.

    python3 -I deny_reach.py --tree TREE --bin PCREC --deny=--memfn=no-run-verify-wide --flags '-e utf8 --engine=vm'
                             --out MOVERS.tsv [--jobs N] [--limit N]

A measurement, not a check. Every distinct corpus pattern (collect.py's src_corpus: emit_sweep's enumeration, the
same `c%05d` ids as the census sweep) is compiled twice by the PLAIN pcrec with emit_sweep's own argv builder
(`compile_stream_c`, `-o -`): the cell's flags alone (the base) and the cell's flags plus the deny. A pattern MOVES
when both compile and the two artifacts differ (emit_sweep's DIFFER); a pattern one side refuses is counted apart.
MOVERS.tsv: one line per pattern, `id ok_base ok_arm differ pat_hex`; the last stdout line is the cell's summary,
`REACH flags=.. deny=.. patterns=N ok_base=N ok_arm=N differ=N refused=N`.
"""
import argparse
import concurrent.futures
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import collect  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--deny", required=True)
    ap.add_argument("--flags", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    es = collect.load_emit_sweep(a.tree)
    items = collect.src_corpus(a.tree, es, os.path.join(a.tree, "build/pcrec"))
    if a.limit:
        items = items[:a.limit]
    cell = a.flags.split()

    def one(it):
        _, pid, pat, _ = it
        okb, b, _ = es.compile_stream_c(a.bin, pat, 60, extra=cell)
        oka, d, _ = es.compile_stream_c(a.bin, pat, 60, extra=cell + [a.deny])
        return pid, okb, oka, int(okb and oka and b != d), pat.hex()

    n = okb = oka = differ = refused = 0
    with open(a.out, "w") as out, concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for pid, b, d, x, h in ex.map(one, items):
            n += 1
            okb += b
            oka += d
            differ += x
            refused += b != d
            out.write("%s\t%d\t%d\t%d\t%s\n" % (pid, b, d, x, h))
    print("REACH flags=%s deny=%s patterns=%d ok_base=%d ok_arm=%d differ=%d refused=%d"
          % (a.flags or "-", a.deny, n, okb, oka, differ, refused), flush=True)


if __name__ == "__main__":
    main()
