#!/usr/bin/env python3
# docs/design/findall_iter/twin/parity_expect.py — the parity slot's INDEPENDENT answer
# control (lane parity, 2026-10-21; findall_iter.md §5.3).
#
# For each subcell of the parity gate, python's `re` over the same subject BYTES gives the
# expected find-all: the match count and the FNV-1a 64 hash over every span's (start, end),
# the function tdrv.c's `check` mode computes. No pcrec code is read: the expectation and
# the subject (a pcrec artifact's answers) share no source. The four patterns have no empty
# match and no construct where python's `re` and PCRE2 differ in byte mode (`\w` is ASCII
# [0-9A-Za-z_] for a bytes pattern, as it is for PCRE2 without UCP), so `re.finditer` is
# the base-tier oracle the house rule names.
#
# usage: python3 -I parity_expect.py CELLS.tsv SUBJDIR   (CELLS: id pattern-key subject stop)
import re
import sys

PATTERNS = {"pa": rb"a", "pw": rb"\w+", "pc": rb"(a)", "pd": rb"^a|b"}
M = (1 << 64) - 1
PRIME = 1099511628211

cells, subjdir = sys.argv[1], sys.argv[2]
for line in open(cells, encoding="ascii"):
    if not line.strip() or line.startswith("#"):
        continue
    cid, pk, subj, stop = line.split("\t")[:4]
    stop = int(stop)
    data = open(f"{subjdir}/{subj}", "rb").read()
    h, k = 14695981039346656037, 0
    for m in re.finditer(PATTERNS[pk], data):
        a, b = m.span()
        h = ((h ^ a) * PRIME) & M
        h = ((h ^ b) * PRIME) & M
        k += 1
        if k == stop:
            break
    print(f"{cid}\tcount {k} hash {h:016x} code 0")
