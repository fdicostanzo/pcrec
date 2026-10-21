#!/usr/bin/env python3
"""docs/design/memfn/r17b_prime/b4prep/summarize_manifest.py -- the counts b4prep's item 4 reports
from a regenerated predicted-mover manifest (lane b4prep).

    python3 -I summarize_manifest.py NEW.tsv OLD.tsv KEYS.tsv

Reads NEW (the rev 4.1 term-count manifest), OLD (fdb2's, the interim-set manifest, left as is) and
grid2read's keys.tsv. Prints, for each of NEW and OLD: sites, (arm, pattern) movers, sites by
(shape, pick); then for NEW the split of the sites on shapes that have NO `kit.saving.V1.WALK.<shape>`
key in keys.tsv between V1 (term count <= 2) and the walk (>= 3), by arm; then the movers-by-ID
difference NEW vs OLD. A term count is range + eq + cube of the shape name `r<R>e<E>c<C>`.

[b4close2] The manifest now carries four more columns (lookup, poscov, hull, walk0; the OLD
manifest has none, read as `ok` and `-`). The rule check skips NOMS rows (a site whose art held no
measures: a discarded compound part, shadow_census.py's header) and lists them apart. The POSCOST
section counts the WALK-ROUTED set-FIND sites (pick WALK, >= 3 terms at the scanned position, shape
`-` counted as >= 3: no cover within MF_SET_K): how many have a <= 2-term position anywhere in their
span (the k-set walk's offsets, `poscov`), how many have a <= 2-term superset hull with <= 8 and
<= 16 extra members (`hull`), and how many have both, by arm, as sites and as (arm, pattern).
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
            arm, pat, site, mem, shape, row, pick, mv = f[:8]
            ext = f[8:12] if len(f) >= 12 else ["ok", "-", "-", "-"]
            rows.append((arm, pat, site, int(mem), shape, row, pick, int(mv)) + tuple(ext))
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


def poscost(rows):
    """The POSCOST counts over the walk-routed set-FIND sites (>= 3 terms at the scanned position)."""
    walk = [r for r in rows if r[8] != "NOMS" and r[6] == "WALK"
            and (r[4] == "-" or (terms(r[4]) or 0) >= 3)]
    print("== POSCOST: walk-routed set-FIND sites (pick WALK, >= 3 terms or no cover within K): %d"
          % len(walk))

    def le2(pc):                      # a <= 2-term position in the span; None: no walk handed
        if pc == "-":
            return None
        return any(x != "x" and int(x) <= 2 for x in pc.split(","))

    def hullx(h):                     # extra members of the <= 2-term hull; None: none within 16
        if h == "-" or h == ">16":
            return None
        if h == "exact":
            return 0
        return int(h.split("/")[0])

    for scope, sel in (("ALL", lambda r: True), ("byte", lambda r: r[0] == "byte"),
                       ("byte-vm", lambda r: r[0] == "byte-vm")):
        W = [r for r in walk if sel(r)]
        nwalk = sum(1 for r in W if le2(r[9]) is None)
        c_pos = [r for r in W if le2(r[9])]
        h8 = [r for r in W if hullx(r[10]) is not None and hullx(r[10]) <= 8]
        h16 = [r for r in W if hullx(r[10]) is not None and hullx(r[10]) <= 16]
        both8 = [r for r in c_pos if r in h8]
        both16 = [r for r in c_pos if r in h16]
        ids = lambda L: len({(r[0], r[1]) for r in L})
        print("   %-8s sites %d ((arm,pattern) %d); no walk handed (poscov '-') %d; walk0 differs %d"
              % (scope, len(W), ids(W), nwalk, sum(1 for r in W if r[11] == "diff")))
        print("            <=2-term position within span: sites %d ((arm,pattern) %d)"
              % (len(c_pos), ids(c_pos)))
        later = [r for r in c_pos if any(x != "x" and int(x) <= 2 for x in r[9].split(",")[1:])]
        print("            of those: a <=2-term position at offset >= 1: sites %d ((arm,pattern) %d);"
              " only the walk's offset 0 (which differs from the scanned set): sites %d"
              % (len(later), ids(later), len(c_pos) - len(later)))
        print("            <=2-term superset hull, extras <=8: sites %d (%d); <=16: sites %d (%d)"
              % (len(h8), ids(h8), len(h16), ids(h16)))
        print("            both (position and hull): <=8 sites %d (%d); <=16 sites %d (%d)"
              % (len(both8), ids(both8), len(both16), ids(both16)))
    ext = Counter()
    for r in walk:
        x = hullx(r[10])
        ext["none<=16" if x is None else str(x)] += 1
    print("   hull extras histogram (ALL): %s" % dict(sorted(ext.items(), key=lambda kv: (len(kv[0]), kv[0]))))
    firstle2 = Counter()
    for r in walk:
        if r[9] == "-":
            continue
        for i, x in enumerate(r[9].split(",")):
            if x != "x" and int(x) <= 2:
                firstle2[i] += 1
                break
    print("   offset of the first <=2-term position (ALL): %s" % dict(sorted(firstle2.items())))


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
    noms = [r for r in N if r[8] == "NOMS"]
    bad = [r for r in N if r[8] != "NOMS" and terms(r[4]) is not None
           and ((terms(r[4]) <= 2) != (r[6] == "V1"))]
    print("== rule check: sites whose pick disagrees with 'V1 iff terms <= 2' (NOMS rows apart): %d"
          % len(bad))
    for r in bad[:10]:
        print("   ", r[:7])
    print("== NOMS rows (key lookups answered ABSENT for keys the set holds; the site's art held"
          " no measures): %d" % len(noms))
    for r in noms:
        print("    %s %s site %s %d members shape %s pick %s" % (r[0], r[1], r[2], r[3], r[4], r[6]))
    poscost(N)
    mn, mo = movers(N), movers(O)
    print("== movers by ID: NEW %d, OLD %d, in both %d, only NEW %d, only OLD %d"
          % (len(mn), len(mo), len(mn & mo), len(mn - mo), len(mo - mn)))
    print("   only NEW by arm:", dict(Counter(a for a, _ in mn - mo)))
    print("   only OLD by arm:", dict(Counter(a for a, _ in mo - mn)))


if __name__ == "__main__":
    main()
