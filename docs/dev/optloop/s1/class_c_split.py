#!/usr/bin/env python3
"""S1 review C2 (2026-09-25): splits census.tsv's single "C" tag into the
note's own C1/C2/C0 sub-populations, downstream of classify() by design
(census.py's own header: "C1/C2 and B's sub-split are computed from the
TSV in the note"). classify() cannot do this itself -- the SELECTED scan
offset (`scank`) the probe computes is never written to the TSV, only the
raw `sel` string, which still carries it as the one offset with a trailing
`*` (probe_patch.py's own format).

  C1  sel non-empty AND the starred offset equals the pick's offset
      s = pin + idx           -- clause 3(a): "the selection scans offset s"
  C2  sel non-empty AND it does not                -- clause 3 fails, k-set present
  C0  sel EMPTY                                     -- clause 3(b) failed too
      (S1-2's B-branch fix moves these OUT of B; neither C1 nor C2 as the
      note's own §6 table defines them, since both assume a k-set exists --
      a genuinely new subtype the fix surfaces, not a hand-adjustment)

Usage: class_c_split.py census.tsv
"""
import sys, collections


def parse_sel_star(selstr):
    offs, star = [], None
    for tok in selstr.split(","):
        if not tok:
            continue
        if tok.endswith("*"):
            v = int(tok[:-1])
            star = v
        else:
            v = int(tok)
        offs.append(v)
    return offs, star


def main():
    rows = []
    with open(sys.argv[1]) as f:
        header = None
        for line in f:
            if line.startswith("#"):
                continue
            line = line.rstrip("\n")
            parts = line.split("\t")
            if header is None:
                header = parts
                continue
            rows.append(dict(zip(header, parts)))

    tally = collections.Counter()
    for r in rows:
        if r["class"] != "C":
            tally[(r["pop"], r["cfg"], r["class"])] += 1
            continue
        pin, idx = int(r["pin"]), int(r["idx"])
        s = pin + idx
        offs, star = parse_sel_star(r["sel"])
        if not offs:
            cls = "C0"
        elif star == s:
            cls = "C1"
        else:
            cls = "C2"
        tally[(r["pop"], r["cfg"], cls)] += 1

    for k in sorted(tally):
        print("\t".join(k) + "\t" + str(tally[k]))

    for pop, cfg in sorted({(k[0], k[1]) for k in tally}):
        def n(c):
            return tally[(pop, cfg, c)]
        pc = n("A") + n("B") + n("C1") + n("E")
        print("# %s/%s program changes (A+B+C1+E) = %d" % (pop, cfg, pc))


if __name__ == "__main__":
    main()
