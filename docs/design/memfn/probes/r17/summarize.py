#!/usr/bin/env python3
"""R-17 (lane r17s): roll census.py's sites.tsv up by the FORM FAMILY a row
would key on. One row per distinct (stream, role) walk statement (`dup` 0:
the VM hat's entry and retry statements are one site).

    summarize.py OUTDIR/sites.tsv

Columns: sites | |S|=1 | pair: cube / adjacent (a 2-range) / other |
3..8 members by greedy prime-cube cover (<=2, 3, 4+) | one range n>2 |
one cube n>2 | wide (n>8, not one range/cube) by run count (2, 3-4, 5+) and
by cube cover <= 4. Read with the report's §1.3: the k-cube and r-range
columns are the populations a parameterized "small set" row would reach.
"""
import collections
import csv
import sys


def main():
    rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
    agg = collections.defaultdict(collections.Counter)
    for r in rows:
        if r["dup"] != "0":
            continue
        k = (r["stream"], r["role"])
        a = agg[k]
        n, cubes, runs = int(r["n"]), int(r["cubes"]), int(r["runs"])
        cube, rng = r["cube"] == "1", r["range"] == "1"
        a["sites"] += 1
        a["bounded"] += int(r["bounded"])
        if n == 1:
            a["byte"] += 1
        elif n == 2:
            a["pair-cube" if cube else "pair-adj" if rng else "pair-other"] += 1
        elif cube:
            a["cube>2"] += 1
        elif rng:
            a["range>2"] += 1
        elif n <= 8:
            a["small-k<=2" if cubes <= 2 else "small-k3" if cubes == 3 else "small-k4+"] += 1
        else:
            a["wide-r2" if runs == 2 else "wide-r3-4" if runs <= 4 else "wide-r5+"] += 1
            if 0 < cubes <= 4:
                a["wide-k<=4"] += 1
        if 0 < cubes <= 4 or n <= 4:
            a["ANY k<=4 cubes"] += 1
        if runs <= 2:
            a["ANY <=2 ranges"] += 1
    cols = ["sites", "bounded", "byte", "pair-cube", "pair-adj", "pair-other", "small-k<=2",
            "small-k3", "small-k4+", "range>2", "cube>2", "wide-r2", "wide-r3-4", "wide-r5+",
            "wide-k<=4", "ANY k<=4 cubes", "ANY <=2 ranges"]
    print("| stream | role | " + " | ".join(cols) + " |")
    print("|" + "---|" * (len(cols) + 2))
    for k in sorted(agg):
        print("| %s | %s | " % k + " | ".join(str(agg[k][c]) for c in cols) + " |")


if __name__ == "__main__":
    main()
