#!/usr/bin/env python3
"""docs/design/memfn/r17b_prime/b4prep/summarize_manifest.py -- the counts b4prep's item 4 reports
from a regenerated predicted-mover manifest (lane b4prep).

    python3 -I summarize_manifest.py NEW.tsv OLD.tsv KEYS.tsv

Reads NEW (the rev 4.1 term-count manifest), OLD (fdb2's, the interim-set manifest, left as is) and
grid2read's keys.tsv. Prints, for each of NEW and OLD: sites, (arm, pattern) movers, sites by
(shape, pick); then for NEW the split of the sites on shapes that have NO `kit.saving.V1.WALK.<shape>`
key in keys.tsv between V1 (term count <= 2) and the walk (>= 3), by arm; then the movers-by-ID
difference NEW vs OLD. A term count is range + eq + cube of the shape name `r<R>e<E>c<C>`.
"""
import re
import sys
from collections import Counter


def load(path):
    rows = []
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("#") or not ln.strip():
                continue
            f = ln.rstrip("\n").split("\t")
            arm, pat, site, mem, shape, row, pick, mv = f
            rows.append((arm, pat, site, int(mem), shape, row, pick, int(mv)))
    return rows


def terms(shape):
    m = re.fullmatch(r"r(\d+)e(\d+)c(\d+)", shape)
    return None if not m else sum(int(x) for x in m.groups())


def movers(rows):
    return {(r[0], r[1]) for r in rows if r[7]}


def report(name, rows):
    mv = movers(rows)
    print("== %s: %d set sites, %d (arm, pattern) movers" % (name, len(rows), len(mv)))
    by = Counter((r[4], r[5], r[6]) for r in rows)
    for k in sorted(by):
        print("   shape %-8s row %-4s pick %-5s sites %d" % (k + (by[k],)))
    arms = Counter(a for a, _ in mv)
    print("   movers by arm: %s" % dict(arms))


def main():
    new, old, keys = sys.argv[1:4]
    keyed = set()
    with open(keys) as fh:
        for ln in fh:
            m = re.match(r"kit\.saving\.V1\.WALK\.(r\d+e\d+c\d+)\t", ln)
            if m:
                keyed.add(m.group(1))
    N, O = load(new), load(old)
    report("NEW (" + new.split("/")[-1] + ")", N)
    report("OLD (" + old.split("/")[-1] + ")", O)
    print("== keyed shapes in keys.tsv:", ",".join(sorted(keyed)))
    print("== NEW sites on shapes with NO saving key (the 'no-key sites'), by arm, term count, pick")
    c = Counter()
    for r in N:
        if r[4] not in keyed:
            c[(r[0], terms(r[4]), r[6])] += 1
    for k in sorted(c, key=lambda k: (k[0], -1 if k[1] is None else k[1], k[2])):
        print("   arm %-7s terms %-4s pick %-5s sites %d" % (k[0], k[1], k[2], c[k]))
    tot = Counter()
    for (arm, t, pick), n in c.items():
        tot[(arm, pick)] += n
    for k in sorted(tot):
        print("   TOTAL arm %-7s pick %-5s sites %d" % (k + (tot[k],)))
    # the rule's own consistency: pick V1 iff terms <= 2 (members >= 2 sites only)
    bad = [r for r in N if terms(r[4]) is not None and ((terms(r[4]) <= 2) != (r[6] == "V1"))]
    print("== rule check: sites whose pick disagrees with 'V1 iff terms <= 2': %d" % len(bad))
    for r in bad[:10]:
        print("   ", r[:7])
    mn, mo = movers(N), movers(O)
    print("== movers by ID: NEW %d, OLD %d, in both %d, only NEW %d, only OLD %d"
          % (len(mn), len(mo), len(mn & mo), len(mn - mo), len(mo - mn)))
    print("   only NEW by arm:", dict(Counter(a for a, _ in mn - mo)))
    print("   only OLD by arm:", dict(Counter(a for a, _ in mo - mn)))


if __name__ == "__main__":
    main()
