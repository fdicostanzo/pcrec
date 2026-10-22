#!/usr/bin/env python3
# docs/dev/lanes/r27b_evidence/diff_581.py — job 581: the differential stage's case generator.
#
# usage: python3 -I diff_581.py CELLS.TSV OUTDIR [CELL ...]
#   writes OUTDIR/<cell>.cases (ddrv.c's format) and OUTDIR/<cell>.tile
#
# Per cell: 2000 deterministic subjects (random.Random seeded from the cell id), length 0..40, over
# the alphabet of the cell's stop, set and ctx bytes plus a few others (' ', 'x', '\n', 0xE9).
# Half are pure random strings over that alphabet; half PLANT an instance of the cell's match
# (or a near-miss: one byte replaced / dropped, or cut short) in random filler, so the matches,
# the near-misses, matches ending EXACTLY at the subject's end and starting exactly at 0, and
# ctx edges (the bound before 0 / after the end) are all common. The expected answers are python
# `re` on bytes (the independent control, no pcrec source), search(subject, lo) for every lo.
import importlib.util
import os
import random
import re
import struct
import sys

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("pb", os.path.join(here, "proto_bodies_581.py"))
pb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pb)

NCASES = 2000
EXTRA = b" x\n\xe9"
# per cell: instances (text a match is planted as) and the sentinel tile (a text satisfying the terms,
# including the ctx bytes: a straddling over-read completes a match)
INST = {
    "lit-l8": [b"abcdefgh"], "foobar": [b"foobar"], "file-ext-order": [b".tar", b".tar.gz"],
    "cat-bounded": [b"cat", b" cat ", b"(cat)", b"cat_", b"_cat", b"cat1"],
    "done-eol": [b"done\n", b"done", b"done\ndone\n", b"donex"],
    "year4": [b"2024", b"1999 ", b"12345", b"123"],
    "word-digit": [b"a1", b"_9", b"ab1", b"z", b"-1", b"1"],
    "hex8-bounded": [b"deadbeef", b" 0123abcd ", b"deadbeefa", b"abcdef0", b"x12345678", b"12345678g"],
}
TILE = {
    "lit-l8": "abcdefgh", "foobar": "foobar", "file-ext-order": ".tar", "cat-bounded": "cat ",
    "done-eol": "done\n", "year4": "0123456789", "word-digit": "a1", "hex8-bounded": "abcdef01 ",
}


def alphabet(cell):
    k, stop, tests = pb.CELLS[cell]
    a = set(EXTRA)
    for ss in pb.span_sets(cell):
        a |= set(sorted(ss)[:6])
    for _off, ss in pb.ctx_items(cell):
        a |= set(sorted(ss)[:3])
    for t in INST[cell]:
        a |= set(t)
    return bytes(sorted(a))


def subject(rng, cell, alpha):
    n = rng.randint(0, 40)
    if rng.random() < 0.5:
        return bytes(rng.choice(alpha) for _ in range(n))
    out = b""
    for _ in range(rng.randint(1, 2)):
        out += bytes(rng.choice(alpha) for _ in range(rng.randint(0, 12)))
        inst = bytearray(rng.choice(INST[cell]))
        r = rng.random()
        if r < 0.35 and inst:
            inst[rng.randrange(len(inst))] = rng.choice(alpha)
        elif r < 0.5 and inst:
            del inst[rng.randrange(len(inst))]
        elif r < 0.6 and inst:
            inst = inst[:rng.randrange(len(inst))]
        out += bytes(inst)
    out += bytes(rng.choice(alpha) for _ in range(rng.choice([0, 0, 0, 1, 2, 5])))
    if rng.random() < 0.5:                         # cut so the planted text may end the subject
        out = out[:rng.randint(0, 40)]
    return out[:40]


def main():
    cells_tsv, outd = sys.argv[1], sys.argv[2]
    want = sys.argv[3:]
    pats = dict(l.rstrip("\n").split("\t", 1) for l in open(cells_tsv) if l.strip() and not l.startswith("#"))
    os.makedirs(outd, exist_ok=True)
    for cell, pat in pats.items():
        if want and cell not in want:
            continue
        rx = re.compile(pat.encode())
        rng = random.Random("diff581/" + cell)
        alpha = alphabet(cell)
        nmatch = nlen = 0
        with open(os.path.join(outd, cell + ".cases"), "wb") as f:
            for i in range(NCASES):
                s = subject(rng, cell, alpha)
                assert len(s) <= 40
                f.write(struct.pack("<I", len(s)) + s)
                for lo in range(len(s) + 1):
                    m = rx.search(s, lo)
                    f.write(struct.pack("<ii", *(m.span() if m else (-1, -1))))
                    nmatch += m is not None and lo == 0
                nlen += len(s)
        open(os.path.join(outd, cell + ".tile"), "w").write(TILE[cell])
        print("diff cases: %-15s %d subjects, %d bytes, %d with a match from 0, alphabet %d bytes" %
              (cell, NCASES, nlen, nmatch, len(alpha)))


main()
