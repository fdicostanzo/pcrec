#!/usr/bin/env python3
"""e8min/pickcheck.py CENSUS_TSV -- the independent check on the PICK column: the census's pick
comes from the table code, the term count from the cover shape (rNeNcN, r+e+c); V1 iff r+e+c <= 2
(rev 4.1 §1.3a). Prints the exceptions (any row where they disagree, with its row and lookup
columns, which say why: R7w is "no set" / no cover shape) and the totals; exit 1 on an exception
that is not an R7w/NOMS row."""
import re
import sys

n = bad = unexpl = 0
for ln in open(sys.argv[1], encoding="utf-8"):
    if ln.startswith("#") or not ln.strip():
        continue
    f = ln.rstrip("\n").split("\t")
    arm, shape, row, pick, lookup = f[0], f[4], f[5], f[6], f[8]
    m = re.fullmatch(r"r(\d+)e(\d+)c(\d+)", shape)
    if not m:                       # no cover shape ('-'): the walk by construction
        want = "WALK"
    else:
        want = "V1" if sum(map(int, m.groups())) <= 2 else "WALK"
    n += 1
    if pick != want:
        bad += 1
        why = row == "R7w" or lookup == "NOMS"
        unexpl += not why
        print("EXCEPTION %s site=%s shape=%s row=%s pick=%s want=%s lookup=%s%s"
              % (arm, f[2], shape, row, pick, want, lookup, "" if why else "  UNEXPLAINED"))
print("pickcheck: %d sites, %d exceptions, %d unexplained" % (n, bad, unexpl))
sys.exit(1 if unexpl else 0)
