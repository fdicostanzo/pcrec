#!/usr/bin/env python3
"""[START-SET] rev 2: tables for startset.md rev 2 §4.1a from sweep.py's TSVs.
    summarize.py out/witnesses.tsv out/sweep.tsv  > out/sweep_summary.txt"""
import collections, csv, sys
def load(p): return list(csv.DictReader((l for l in open(p) if not l.startswith("# ")), delimiter="\t"))
W, R = load(sys.argv[1]), load(sys.argv[2])
print("== the six sound-F1 witnesses (critic's alphabets, maxlen 7) ==")
print("pattern\troute\tcells\tmatches\tpcre2_vs_base\t|E|\t|S|\t|T| cur/a/b\tdiffs cur/a/b/dfa\tTdfa<=T cur/a/b\toracle cur/a/b")
for r in W:
    print("\t".join([r["name"].split("tests/")[-1], r["route"], r["cases"], r["matches"], r["pcre2_vs_base"], r["E"], r["S"],
        "/".join(r["T_" + k] for k in ("cur", "a", "b")), "/".join(r["diffs_" + k] for k in ("cur", "a", "b", "dfa")),
        "/".join(r["static_ok_" + k] for k in ("cur", "a", "b")), "/".join(r["oracle_ok_" + k] for k in ("cur", "a", "b"))]))
ok = [r for r in R if r["status"] == "ok"]
print("\n== the sweep: every seeded byte-class DFA/hybrid census row with a necessary S ==")
print("rows %d (not ok: %s); cells %d; matches %d; rows reaching >= 1 match %d; libpcre2-vs-base diffs %s" % (
    len(R), [(r["name"], r["status"]) for r in R if r["status"] != "ok"], sum(int(r["cases"]) for r in ok),
    sum(int(r["matches"]) for r in ok), sum(int(r["matches"]) > 0 for r in ok),
    sum(int(r["pcre2_vs_base"]) for r in ok if r["pcre2_vs_base"].isdigit())))
print("rows with |E*| == 256: %d of %d;  rows with T_a == S: %d;  rows with Tdfa == S: %d" % (
    sum(r["Estar"] == "256" for r in ok), len(ok), sum(r["T_a"] == r["S"] for r in ok), sum(r["Tdfa"] == r["S"] for r in ok)))
for k in ("cur", "a", "b", "dfa"):
    print("T=%-4s rows_with_diffs %3d  total_diffs %7d  static(Tdfa<=T)_fail %3d  oracle_fail %3d" % (k,
        sum(int(r["diffs_" + k]) > 0 for r in ok), sum(int(r["diffs_" + k]) for r in ok),
        sum(r["static_ok_" + k] == "0" for r in ok), sum(r["oracle_ok_" + k] == "0" for r in ok)))
print("\n== movers (admission) ==")
for k, what in (("mover_cur", "r3 F: T=S&E nonempty, T < E"), ("mover_a_sub", "(a) T=S&E*, admitted iff T < E"),
                ("mover_a_card", "(a) admitted iff |T| < |E|"), ("mover_b_sub", "(b) T=S, admitted iff S < E"),
                ("mover_b_card", "(b) admitted iff |S| < |E|"), ("mover_c", "(c) T=S&E, declined when S not<= E")):
    c = collections.Counter((r["kind"], r["route"]) for r in ok if r[k] == "1")
    print("%-14s %-42s total %3d  bench %2d (dfa %d, hybrid %d)  corpus %2d (dfa %d, hybrid %d)" % (k, what, sum(c.values()),
        c["bench", "dfa"] + c["bench", "hybrid"], c["bench", "dfa"], c["bench", "hybrid"],
        c["corpus", "dfa"] + c["corpus", "hybrid"], c["corpus", "dfa"], c["corpus", "hybrid"]))
print("\nr3 movers that are UNSOUND (mover_cur with diffs or a failed check):")
for r in ok:
    if r["mover_cur"] == "1" and (int(r["diffs_cur"]) or r["static_ok_cur"] == "0"): print("  ", r["name"], "diffs", r["diffs_cur"])
print("rows the cardinality admission adds over the subset admission:")
for r in ok:
    if r["mover_b_card"] == "1" and r["mover_b_sub"] == "0": print("  ", r["kind"], r["name"], r["route"], "|E|", r["E"], "|S|", r["S"])
print("rows where S \\ E != {} but the r3 F declines (T empty or not narrower) -- the r3 census counted the T-empty ones as movers:")
for r in ok:
    if int(r["S_minus_E"]) and r["mover_cur"] == "0": print("  ", r["name"], "|E|", r["E"], "|T_cur|", r["T_cur"])
