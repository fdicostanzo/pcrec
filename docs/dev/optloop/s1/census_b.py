#!/usr/bin/env python3
"""Option-B census (lane s1b, 2026-09-25; docs/design/litscan_s1.md §6.1).

Re-runs census.py's populations against a probe_b_patch.py build and
CROSS-TABULATES the option-B run row's predicate (`rowb`, evaluated on every
artifact) against census.py's classify() (the panelled classes, unchanged)
and class_c_split.py's C1/C2/C0 rule. The question it answers is the one
option B's placement raises: does the dfa_pfs[] row select EXACTLY the
panelled population, and on which artifacts (if any) does it not?

Also counts, on the rowb population: the D11 twin (`views` -> bounded row),
today's selected row, and the seeded class-B artifacts whose reseeds bit
flips false -> true (memchr row -> run row), which scanedge.c's precondition
(8) reads.

Env: PROBE (probe_b_patch.py build), PCREC, BENCH, CORPUS, OUT.
Outputs census_b.tsv (one row per artifact-config) and census_b_summary.txt.
"""
import os, sys, collections
sys.dont_write_bytecode = True
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
sys.path.insert(0, os.path.join(here, "..", "c2"))
from census import probe, classify  # noqa: E402
from reqpos_census import bench_pop, corpus_pop  # noqa: E402
E = os.environ


def split_c(d, cls):
    """C -> C1/C2/C0 (class_c_split.py's rule), and A -> A/A2: G1's identity
    conjunct (litscan_s1.md §1.2, `p == q`) read off the probe's own walk --
    the offset-set scan byte against the run's pick. A2 verifies the run but
    scans a different byte, so G1 keeps its pre-check (C2's reason)."""
    if cls == "A":
        walk = [None if t.startswith("*") else int(t, 16) for t in d["walk"].split(".") if t]
        idx = int(d["idx"])
        q = int(d["run"][2 * idx:2 * idx + 2], 16)
        return "A" if walk[int(d["scank"])] == q else "A2"
    if cls != "C":
        return cls
    pin, idx = int(d["pin"]), int(d["idx"])
    star = [int(t[:-1]) for t in d["sel"].split(",") if t.endswith("*")]
    if not d["sel"]:
        return "C0"
    return "C1" if star and star[0] == pin + idx else "C2"


def main():
    out = open(os.path.join(E["OUT"], "census_b.tsv"), "w")
    out.write("# option-B census (docs/design/litscan_s1.md §6.1); census_b.py over a "
              "probe_b_patch.py build\n")
    out.write("pop\tid\tcfg\tclass\trowb\twhy\tpf\tkind\tcbyte\tviews\tseeded\tse\timplm\timplies\trun\tidx\tpin\tsel\n")
    t = collections.Counter()
    pops = [("bench", bench_pop(), [("caps", []), ("nocaps", ["--no-captures"])]),
            ("corpus", corpus_pop(), [("caps", [])])]
    for pname, rows, cfgs in pops:
        for rid, pat in rows:
            for cname, extra in cfgs:
                d = probe(pat, extra)
                if d is None:
                    t[(pname, cname, "refused")] += 1
                    continue
                cls = split_c(d, classify(d)[0])
                rb = d["rowb"]
                t[(pname, cname, "class=" + cls + " rowb=" + rb)] += 1
                if rb == "1":
                    t[(pname, cname, "rowb pf=" + d["pf"] + " views=" + d["views"])] += 1
                    t[(pname, cname, "rowb why=" + d["why"])] += 1
                    if d["se"] == "0" and d["seeded"] == "1":
                        t[(pname, cname, "rowb reseeds-flip (seeded, se 0->1)")] += 1
                if d["implm"] != d["implies"]:
                    t[(pname, cname, "implm!=implies")] += 1
                out.write("\t".join([pname, rid, cname, cls, rb, d["why"], d["pf"], d["kind"],
                                     d["cbyte"], d["views"], d["seeded"], d["se"], d["implm"],
                                     d["implies"], d["run"], d["idx"], d["pin"], d["sel"]]) + "\n")
    # PROGRAM CHANGES under option B, with no hand arithmetic (S1 review C2's
    # lesson): elided pre-checks (A, E) plus the run row's population (rowb).
    for pname, cname in sorted({(k[0], k[1]) for k in t}):
        n = lambda tag: t[(pname, cname, tag)]
        rowb = sum(v for k, v in t.items() if k[:2] == (pname, cname)
                   and k[2].startswith("class=") and k[2].endswith("rowb=1"))
        pc = n("class=A rowb=0") + n("class=E rowb=0") + rowb
        t[(pname, cname, "# program changes (A + E + rowb)")] = pc
    with open(os.path.join(E["OUT"], "census_b_summary.txt"), "w") as s:
        for k in sorted(t):
            line = "\t".join(k) + "\t" + str(t[k])
            print(line)
            s.write(line + "\n")


if __name__ == "__main__":
    main()
