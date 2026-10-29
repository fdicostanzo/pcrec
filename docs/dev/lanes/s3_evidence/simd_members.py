#!/usr/bin/env python3
"""docs/dev/lanes/s3_evidence/simd_members.py -- WHICH corpus patterns make up scripts/emit_sweep.py's
`-fmemfn-simd` c-default DIFFER cell at two compilers (code review r2 R2-3: the cell's pin, lowered
20 -> 9 at job 600, is a judged trade, so its members are named, not only counted).

    python3 -I simd_members.py --ref BIN --new BIN --tree DIR [--jobs N]

Population: every distinct corpus pattern (census.py's enumeration with the block options
dropped, as the sweep compiles a pattern), byte and utf8 bases. A pattern is a MEMBER at a compiler iff its
`-p rx --features all` artifact differs under `-fmemfn-simd` (the sweep's DIFFER). Prints each
base's member counts, the patterns that LEFT (members at REF only) and JOINED (at NEW only).
Trailer: `== simd_members COMPLETE: ref=R new=N left=L joined=J`.
"""
import argparse
import concurrent.futures
import os
import subprocess
import sys


def art(binary, pat, extra):
    r = subprocess.run([binary, "-p", "rx", "--features", "all"] + extra + ["-o", "-", "--pattern", pat],
                       capture_output=True, timeout=60)
    return r.returncode, r.stdout


def member(binary, pat, enc):
    a = art(binary, pat, enc)
    b = art(binary, pat, enc + ["-fmemfn-simd"])
    return a[0] == 0 and b[0] == 0 and a[1] != b[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--jobs", type=int, default=16)
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.tree, "scripts"))
    import emit_sweep  # noqa: E402
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import census  # noqa: E402  (census.py's corpus enumeration; block options dropped)
    _, tasks, _ = census.corpus_tasks(emit_sweep, a.new, a.tree)
    pats = sorted({p for p, _ in tasks})
    tot = {}
    for enc_name, enc in (("byte", []), ("utf8", ["-e", "utf8"])):
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
            ref = list(ex.map(lambda p: member(a.ref, p, enc), pats))
            new = list(ex.map(lambda p: member(a.new, p, enc), pats))
        left = [p for p, r, n in zip(pats, ref, new) if r and not n]
        joined = [p for p, r, n in zip(pats, ref, new) if n and not r]
        print("%s: patterns %d, members ref %d new %d" % (enc_name, len(pats), sum(ref), sum(new)))
        for p in left:
            print("  LEFT   %s %s" % (enc_name, emit_sweep.encode_escape(p)))
        for p in joined:
            print("  JOINED %s %s" % (enc_name, emit_sweep.encode_escape(p)))
        tot[enc_name] = (sum(ref), sum(new), len(left), len(joined))
    print("== simd_members COMPLETE: ref=%s new=%s left=%d joined=%d" % (
        "/".join(str(v[0]) for v in tot.values()), "/".join(str(v[1]) for v in tot.values()),
        sum(v[2] for v in tot.values()), sum(v[3] for v in tot.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
