"""variants.py -- [ARTREV] a DENSE and a SPARSE variant of a cell subject (charter S4: "the cell's
subject plus one dense and one sparse variant").

The pinned original finds the subject's matches; then
  dense   the matches, each with CTX bytes of its own surroundings, concatenated (cycled) up to
          the subject's length: nearly every byte sits inside or beside a match;
  sparse  the subject's own bytes with every match destroyed except one in KEEP (one byte inside
          a match flipped to 0x01), so matches are rare and the scan/prefilter paths dominate.
Deterministic (no randomness); the sha256 of both files goes in the output.  The variants are
TIMING subjects only: all arms see the same bytes, and the harness already refuses an answer
mismatch between arms.
"""
import hashlib
import os

import common as C


def spans_exe(meta, od):
    bdir = os.path.join(od, "build")
    os.makedirs(bdir, exist_ok=True)
    exe = os.path.join(bdir, "spans")
    cmd = C.arm_compile_cmd(meta, od, exe, main_src=os.path.join(C.HERE, "driver_spans.c"))
    r = C.run(cmd)
    if r.returncode != 0:
        C.die("spans driver compile failed:\n%s" % r.stderr[-1200:])
    return exe


def cmd_variants(a):
    meta = C.load_meta(a.name)
    od = os.path.join(C.art_dir(a.name), "arms", "orig")
    exe = spans_exe(meta, od)
    data = open(a.subject, "rb").read()
    r = C.run([exe, a.subject])
    if r.returncode != 0:
        C.die("spans driver failed: %s" % r.stderr[-300:])
    spans = [tuple(int(x) for x in ln.split("\t")) for ln in r.stdout.split("\n") if ln.strip()]
    n = len(data)
    if not spans:
        C.die("the original finds NO match in %s: a dense variant cannot be built from it" % a.subject)
    pieces = [data[max(0, s - a.ctx):min(n, e + a.ctx)] for s, e in spans if e - s <= 4096]
    if not pieces:
        C.die("no usable match spans")
    dense = bytearray()
    k = 0
    while len(dense) < n:
        dense += pieces[k % len(pieces)]
        k += 1
    dense = bytes(dense[:n])
    sparse = bytearray(data)
    kept = 0
    for i, (s, e) in enumerate(spans):
        if i % a.keep == 0:
            kept += 1
            continue
        if e > s:
            sparse[s + (e - s) // 2] = 0x01
    open(a.out_dense, "wb").write(dense)
    open(a.out_sparse, "wb").write(bytes(sparse))
    for label, p, b in (("dense", a.out_dense, dense), ("sparse", a.out_sparse, bytes(sparse))):
        print("%-6s %s  %d bytes  sha256 %s" % (label, p, len(b), hashlib.sha256(b).hexdigest()))
    print("original matches in %s: %d (dense uses %d pieces; sparse keeps %d of them intact)" % (a.subject, len(spans), len(pieces), kept))
    return 0
