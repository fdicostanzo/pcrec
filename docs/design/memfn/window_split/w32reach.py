#!/usr/bin/env python3
# w32reach.py BIN TREE [--floor=byte=N,utf8=M] [--extra=FLAG] : G2 arm 3's REACH COUNTER (window_split.md rev 2.1
# §8.2, r98 R11). Over the corpus population emit_sweep's arms use (distinct pattern bytes of
# every TREE/tests .rxt, enumerated by BIN, emit_sweep.enumerate_corpus + distinct_patterns), it
# compiles each pattern ONCE per base (byte, utf8) exactly as emit_sweep's stream 1 does at arm 3
# (`-p rx --features all -fmemfn-simd=x86-64-v3 [-e utf8] -o - --pattern P`, c-default engine) and
# counts the artifacts whose text holds the V form's w32 level stamp `span-vector@w32` (the
# FORMS define's token the w32 block writes). CENSUS of that population; emits text only, so the
# count reads the same on any host ([XARCH-DEV] U3). Prints the count per base, the first three
# hits, and `w32reach: byte N, utf8 M`. With --floor, exit 1 iff a base is below its floor (the
# per-commit gate: a commit whose arm 3 stops rendering the block reads red even when emit_sweep's
# identity half holds on both sides). Reads TREE, writes nothing.
import os, sys
from concurrent.futures import ThreadPoolExecutor
args = [a for a in sys.argv[1:] if not a.startswith('--')]
binp, tree = os.path.abspath(args[0]), os.path.abspath(args[1])
floor = {}
for a in sys.argv[1:]:
    if a.startswith('--floor'):
        for kv in (a.split('=', 1)[1] if '=' in a and not a.endswith('--floor') else '').split(','):
            if kv: k, v = kv.split('='); floor[k] = int(v)
sys.path.insert(0, os.path.join(tree, 'scripts'))
import emit_sweep as es

pats = es.distinct_patterns(es.enumerate_corpus(binp, tree, 30))
ARM = ['-fmemfn-simd=x86-64-v3']
# --extra=FLAG appends one flag to every compile: the counter's DRILL (`--extra=--memfn=no-span-vector`
# denies the V form, so the count must fall below its floor and the run go red)
ARM += [a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--extra=')]
TOKEN = b'span-vector@w32'
res = {}
for base, bargs in (('byte', []), ('utf8', ['-e', 'utf8'])):
    def one(p):
        ok, c, _ = es.compile_stream_c(binp, p, 30, extra=bargs + ARM)
        return p, bool(ok and c and TOKEN in c)
    with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as ex:
        hits = [p for p, h in ex.map(one, pats) if h]
    res[base] = len(hits)
    print(f'{base}: {len(hits)} of {len(pats)} distinct patterns render {TOKEN.decode()}; first '
          + ', '.join(repr(h) for h in hits[:3]))
print(f"w32reach: byte {res['byte']}, utf8 {res['utf8']}")
bad = [b for b, f in floor.items() if res.get(b, 0) < f]
for b in bad: print(f'w32reach: {b} {res[b]} BELOW FLOOR {floor[b]}')
sys.exit(1 if bad else 0)
