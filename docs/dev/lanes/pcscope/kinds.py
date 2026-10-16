#!/usr/bin/env python3
"""docs/dev/lanes/pcscope/kinds.py -- folds census.py's rows.tsv into one
PRESENCE/HANDOFF kind per artifact and prints the per-arm tallies (and, for
the rwquest arm, the kind x mode table).

Usage: python3 -I kinds.py OUT_DIR/rows.tsv

Kinds (first match):
  compound       REQ_WHY "compound": the compound route owns the entry
  none           no necessary byte and no necessary run
  decl-one       declined, G2 one-attempt
  decl-dom       declined, G1 dominated (the find already tests it)
  H-reentry      handoff kept AND re-entered by the forward scan (L1)
  H-entry        handoff kept at the entry only
  P-k65+k66      presence is the only linear proof: set rest AND whole run
  P-k65          presence is the only linear proof: set rest
  P-k66          presence is the only linear proof: whole run
  P-lead         set-leads lead + run (discard)
  P-run          run window (discard)
  P-byte         one-byte gate (discard)
"""
import sys
from collections import Counter, defaultdict


def kind(r):
    a = r["admit"]
    if a == "compound":
        return "compound"
    if a == "none":
        return "none"
    if a == "one-attempt":
        return "decl-one"
    if a == "dominated":
        return "decl-dom"
    if r["use"] == "handoff":
        return "H-reentry" if r["reentry"] == "yes" else "H-entry"
    k65 = r["setrest"] == "set-rest"
    k66 = r["runtests"] == "whole-run"
    if k65 and k66:
        return "P-k65+k66"
    if k65:
        return "P-k65"
    if k66:
        return "P-k66"
    if a == "set-leads":
        return "P-lead"
    if r["runtests"] == "window":
        return "P-run"
    return "P-byte"


def main():
    rows = []
    with open(sys.argv[1], encoding="utf-8", errors="surrogateescape") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            rows.append(dict(zip(hdr, line.rstrip("\n").split("\t"))))
    per = defaultdict(Counter)
    proof = defaultdict(Counter)
    modes = defaultdict(Counter)
    for r in rows:
        k = kind(r)
        per[r["arm"]][k] += 1
        proof[r["arm"]][(k, r["giveup"])] += 1
        if r["arm"] == "rwquest":
            modes[k][r["mode"]] += 1
    order = ["compound", "none", "decl-one", "decl-dom", "H-reentry", "H-entry",
             "P-k65+k66", "P-k65", "P-k66", "P-lead", "P-run", "P-byte"]
    arms = sorted(per)
    print("kind\t" + "\t".join(arms))
    for k in order:
        print(k + "\t" + "\t".join(str(per[a][k]) for a in arms))
    print("total\t" + "\t".join(str(sum(per[a].values())) for a in arms))
    print("\nkind x give-up class (proof-only = presence is the call's only "
          "linear no-match proof)")
    for a in arms:
        for (k, g), n in sorted(proof[a].items()):
            if g == "proof-only" or g == "superset-front":
                print("%s\t%s\t%s\t%d" % (a, k, g, n))
    print("\nrwquest kind x mode")
    ms = sorted({m for c in modes.values() for m in c})
    print("kind\t" + "\t".join(ms))
    for k in order:
        if k in modes:
            print(k + "\t" + "\t".join(str(modes[k][m]) for m in ms))


if __name__ == "__main__":
    main()
