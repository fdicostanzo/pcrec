#!/usr/bin/env python3
"""B-M3's COMMITTED work-budget subject: N distinct lowercase words (the
base-26 spelling of 1000+i, so every word is distinct and none repeats its
neighbour), single-space separated, then " last last".  Deterministic: no
randomness, no environment.  `wb_subject.py [N]` (default 200) prints the
subject with no trailing newline; its length and sha1 are recorded with every
measurement that uses it (wb_runs.tsv)."""
import sys
def word(k):
    s = ""
    while True:
        s = chr(ord("a") + k % 26) + s
        k //= 26
        if k == 0: return s
n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
sys.stdout.write(" ".join(word(1000 + i) for i in range(n)) + " last last")
