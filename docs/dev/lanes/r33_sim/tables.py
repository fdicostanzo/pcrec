#!/usr/bin/env python3
"""docs/dev/lanes/r33_sim/tables.py -- R-33's report tables from sim.py's outputs.

    python3 -I tables.py SWEEPDIR OUTDIR

Writes OUTDIR/differ_<tag>.tsv (every differing decision unit of TODAY's default compile, RTE arm,
every source: the full list the report cites) for tags keyA and keyB, and prints the report's
markdown tables: counts by site kind x verdict per key, the sensitivity counts, and the
disagreement classes.
"""
import collections
import csv
import os
import sys

TAGS = ("keyA", "keyB", "A_h10", "A_h40", "B_h10", "B_h40")
COLS = ("src", "id", "kind", "verdict", "pat", "frame", "arows", "today_path", "today_off", "today_set",
        "today_method", "today_row", "today_score", "sim_entry", "sim_off", "sim_set", "sim_method",
        "sim_score", "gap", "cands")


def load(d, tag):
    return [x for x in csv.DictReader(open(os.path.join(d, "units_%s.tsv" % tag)), delimiter="\t",
                                      quoting=csv.QUOTE_NONE) if x["arm"] == "RTE"]


def klass(x):
    if x["kind"] in ("PF", "LMHIT") and x["verdict"] == "differ-method":
        return "R1 two-member stop: today walk, local rule PAIR"
    if x["kind"] in ("PF", "LMHIT") and x["verdict"] == "differ-alt":
        return "R2 PF: the RESEED alternative's stop over PARKED k0"
    if x["kind"] == "OFS":
        return "R3 OFS: a stop outside A-model's walked one-member domain"
    if x["kind"] == "COVER":
        return "R4 COVER: A-mass's stop vs the priced one (smp20's class)"
    return "R5 pre-check part"


def main():
    d, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    rows = {t: load(d, t) for t in TAGS}
    for t in ("keyA", "keyB"):
        with open(os.path.join(out, "differ_%s.tsv" % t), "w") as f:
            f.write("\t".join(COLS) + "\n")
            for x in rows[t]:
                if x["verdict"].startswith("differ"):
                    f.write("\t".join(x[c] for c in COLS) + "\n")
    kinds = sorted({x["kind"] for x in rows["keyA"]})
    verdicts = ("agree", "agree-stop(hors)", "agree-stop(unobserved)", "differ-stop", "differ-alt",
                "differ-method")
    for t in ("keyA", "keyB"):
        c = collections.Counter((x["kind"], x["verdict"]) for x in rows[t])
        print("\n%s\n\n| kind | units | %s |" % (t, " | ".join(verdicts)))
        print("|---|---|" + "---|" * len(verdicts))
        for k in kinds:
            n = sum(c[(k, v)] for v in verdicts)
            print("| %s | %d | %s |" % (k, n, " | ".join(str(c[(k, v)]) for v in verdicts)))
        n = len(rows[t])
        print("| all | %d | %s |" % (n, " | ".join(str(sum(c[(k, v)] for k in kinds)) for v in verdicts)))
    print("\n| setting | units | agree (incl. agree-stop) | differ | sim pick priced above today's own (gap < 1) |")
    print("|---|---|---|---|---|")
    for t in TAGS:
        r = rows[t]
        dif = [x for x in r if x["verdict"].startswith("differ")]
        print("| %s | %d | %d | %d | %d |" % (t, len(r), len(r) - len(dif), len(dif),
                                             sum(1 for x in dif if float(x["gap"]) < 1)))
    for t in ("keyA", "keyB"):
        dif = [x for x in rows[t] if x["verdict"].startswith("differ")]
        c = collections.Counter(klass(x) for x in dif)
        g = collections.defaultdict(list)
        for x in dif:
            g[klass(x)].append(float(x["gap"]))
        src = collections.Counter((klass(x), x["src"]) for x in dif)
        print("\n%s classes\n\n| class | units | corpus / bench / s588 | gap < 1 | gap >= 1.5 |" % t)
        print("|---|---|---|---|---|")
        for k in sorted(c):
            print("| %s | %d | %d / %d / %d | %d | %d |" % (k, c[k], src[(k, "corpus")], src[(k, "bench")],
                                                        src[(k, "s588")], sum(1 for v in g[k] if v < 1),
                                                        sum(1 for v in g[k] if v >= 1.5)))


if __name__ == "__main__":
    main()
