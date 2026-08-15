#!/usr/bin/env python3
"""Emitted-source diff between N binaries over a pattern list."""
import subprocess, sys, os, hashlib
from concurrent.futures import ThreadPoolExecutor
patfile = sys.argv[1]
bins = sys.argv[2:]
pats = [l.rstrip("\n") for l in open(patfile) if l.strip() and not l.startswith("#")]
def emit(b, p):
    r = subprocess.run([b, "-p", "rx", "-o", "-", "--", p], capture_output=True, timeout=120)
    if r.returncode != 0:
        return "REFUSE:" + r.stderr.decode(errors="replace").strip()[:80]
    return hashlib.sha256(r.stdout).hexdigest()
def one(p):
    return p, [emit(b, p) for b in bins]
with ThreadPoolExecutor(max_workers=12) as ex:
    res = list(ex.map(one, pats))
ndiff = 0
for p, hs in res:
    if len(set(hs)) > 1:
        ndiff += 1
        print("DIFF\t%s\t%s" % (p, " ".join(h[:8] for h in hs)))
print("== %d patterns, %d differ across %d binaries" % (len(res), ndiff, len(bins)))
