#!/usr/bin/env python3
"""Harvest every `pattern ...` line from the .rxt corpora into a flat list.

Usage: harvest_patterns.py <repo-root> > patterns.txt
One pattern per line, deduplicated, in first-seen order. `pattern` lines that
carry harness flags after the pattern are taken verbatim from the first token
onward, which is how the harness itself reads them.
"""
import os
import sys

root = sys.argv[1]
seen = set()
out = []
for dirpath, dirnames, filenames in os.walk(os.path.join(root, "tests")):
    for fn in sorted(filenames):
        if not fn.endswith(".rxt"):
            continue
        with open(os.path.join(dirpath, fn), errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line.startswith("pattern "):
                    continue
                p = line[len("pattern "):]
                if p and p not in seen:
                    seen.add(p)
                    out.append(p)
print("\n".join(out))
