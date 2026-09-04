#!/usr/bin/env python3
"""Build the ladder's cell list. wp-K is the first K branches of w-64's own
alternation, constructed here and LABELLED as constructed -- it is not a bench
or corpus pattern. The w-K rungs are the bench's own files, read-only."""
import os, sys

BENCH = "/home/duxevents/pcrec-bench/bench/altwide/patterns"
OUT = sys.argv[1]

def readpat(name):
    with open(os.path.join(BENCH, name + ".rx")) as f:
        return f.read().strip()

w64 = readpat("w-64")
assert w64.startswith("(?:") and w64.endswith(")"), w64[:20]
words = w64[3:-1].split("|")
assert len(words) == 64, len(words)

def wp(k):
    return "(?:" + "|".join(words[:k]) + ")"

# label, pattern, priority (1 = decisive, run first)
cells = [
    ("w-8",        readpat("w-8"),                 1),
    ("w-64",       readpat("w-64"),                1),
    ("w-256",      readpat("w-256"),               1),
    ("dig-upto-16", r"\d{1,16}",                   1),
    ("wp-4",       wp(4),                          1),
    ("wp-6",       wp(6),                          1),
    ("lower-0-8",  r"[a-z]{0,8}",                  2),
    ("hex32",      r"[0-9a-f]{32}",                2),
    ("year4",      r"[12][0-9]{3}",                2),
    ("lit16",      r"abcdefghijklmnop",            2),
    ("ipv4",       r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}", 2),
    ("wp-2",       wp(2),                          2),
    ("wp-3",       wp(3),                          2),
    ("wp-5",       wp(5),                          2),
    ("wp-12",      wp(12),                         3),
    ("wp-16",      wp(16),                         3),
    ("wp-24",      wp(24),                         3),
    ("wp-32",      wp(32),                         3),
    ("wp-48",      wp(48),                         3),
    ("w-96",       readpat("w-96"),                3),
]

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "cells.tsv"), "w") as f:
    for label, pat, prio in cells:
        with open(os.path.join(OUT, label + ".rx"), "w") as p:
            p.write(pat)
        f.write("%s\t%d\n" % (label, prio))
print("%d cells" % len(cells))
