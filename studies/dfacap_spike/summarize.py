#!/usr/bin/env python3
"""summarize.py -- the population summary behind the report's FINDINGS.
Usage: python3 summarize.py results/population.tsv > results/population_summary.txt"""
import collections
import csv
import re
import statistics
import sys

rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
C = collections.Counter


def reason(w):
    w = re.sub(r"\(\d+\)", "", w)
    w = re.sub(r" at \d+", "", w)
    w = re.sub(r"posix class .*", "posix class", w)
    return w


print("rows", len(rows))
st = C(r["status"] for r in rows)
print("status", dict(st))
for scope in ("corpus", "bench"):
    R = [r for r in rows if (r["src"] == "corpus") == (scope == "corpus")]
    print("  %s: %d rows, in %d" % (scope, len(R), sum(r["status"] == "in" for r in R)))
print("\nOUT reasons:")
for w, n in C(reason(r["why"]) for r in rows if r["status"] != "in").most_common():
    print("  %4d  %s" % (n, w))

IN = [r for r in rows if r["status"] == "in"]
print("\nDIFFERENTIAL over %d admitted patterns" % len(IN))
tot = sum(int(r["nsubs"]) for r in IN)
print("  subjects: %d (corpus subjects %d), pcre2 errors (invalid UTF-8 subjects) %d"
      % (tot, sum(int(r["corpus_subs"]) for r in IN), sum(int(r["pcre2_err"]) for r in IN)))
for k in ("mism_tdfa", "mism_pike", "mism_anch", "mism_vm", "mism_real"):
    bad = [r for r in IN if r[k] not in ("0", "", "n/a")]
    na = sum(r[k] == "n/a" for r in IN)
    print("  %-10s patterns with a mismatch: %d (subjects %d)%s" % (
        k, len(bad), sum(int(r[k]) for r in bad), ("  n/a %d" % na) if na else ""))
    for r in bad[:10]:
        print("      row %s %s  %s" % (r["n"], r[k], r["pattern_esc"]))
print("  exhaustive length distribution:", sorted(C(r["exh_len"] for r in IN).items()))


def num(r, k):
    return int(r[k])


def dist(xs):
    xs = sorted(xs)
    if not xs:
        return "-"
    q = lambda f: xs[min(len(xs) - 1, int(f * len(xs)))]
    return "median %s  p90 %s  p99 %s  max %s  mean %.2f" % (q(0.5), q(0.9), q(0.99), xs[-1], statistics.mean(xs))


for pre, label in (("a_", "ANCHORED (Stage 1 shape: inside the hybrid window)"),
                   ("u_", "UNANCHORED (start tag in the machine: Stage 4 shape)")):
    print("\nCOSTS, %s, %d patterns" % (label, len(IN)))
    print("  tagged states          ", dist([num(r, pre + "states") for r in IN]))
    print("  untagged states        ", dist([num(r, pre + "ustates") for r in IN]))
    ratio = [num(r, pre + "states") / max(1, num(r, pre + "ustates")) for r in IN]
    print("  tagged/untagged ratio   median %.2f  p90 %.2f  max %.2f  (== 1.0: %d)" % (
        statistics.median(ratio), sorted(ratio)[int(0.9 * len(ratio))], max(ratio),
        sum(1 for x in ratio if x == 1.0)))
    print("  registers (as built)   ", dist([num(r, pre + "regs") for r in IN]))
    print("  registers after fixed  ", dist([num(r, pre + "regs_nf") for r in IN]))
    print("  sets per transition     total sets %d over %d transitions" % (
        sum(num(r, pre + "sets") for r in IN), sum(num(r, pre + "trans") for r in IN)))
    print("  copies (as built)      ", dist([num(r, pre + "copies") for r in IN]))
    print("  max ops on one trans   ", dist([num(r, pre + "maxops") for r in IN]))
    cf_built = sum(1 for r in IN if num(r, pre + "copies") == 0)
    cf = sum(1 for r in IN if r[pre + "copyfree"] == "1")
    cfn = sum(1 for r in IN if r[pre + "copyfree_nf"] == "1")
    af = sum(1 for r in IN if r[pre + "allfixed"] == "1")
    print("  copy-free as built (this allocator)   %d (%.0f%%)" % (cf_built, 100.0 * cf_built / len(IN)))
    print("  copy-free under SOME allocation       %d (%.0f%%)" % (cf, 100.0 * cf / len(IN)))
    print("  copy-free once fixed classes dropped  %d (%.0f%%)" % (cfn, 100.0 * cfn / len(IN)))
    print("  ALL classes fixed (no registers)      %d (%.0f%%)" % (af, 100.0 * af / len(IN)))
    rz = [r for r in IN if num(r, pre + "rregs") >= 0]
    print("  REALIZED copy-free machine (fixed classes + coloured unions): %d built" % len(rz))
    print("    registers           ", dist([num(r, pre + "rregs") for r in rz]))
    print("    set ops (whole DFA) ", dist([num(r, pre + "rsets") for r in rz]))
    print("    zero registers      ", sum(1 for r in rz if num(r, pre + "rregs") == 0))
    for split, f in (("prefilter none", lambda r: r["prefilter"] == "none"),
                     ("bench", lambda r: r["src"] != "corpus")):
        S = [r for r in IN if f(r)]
        if S:
            print("    %s: %d admitted; copy-free(nf) %d, all-fixed %d" % (
                split, len(S), sum(r[pre + "copyfree_nf"] == "1" for r in S), sum(r[pre + "allfixed"] == "1" for r in S)))
    worst = sorted(IN, key=lambda r: -num(r, pre + "states") / max(1, num(r, pre + "ustates")))[:8]
    print("  worst tagged/untagged state ratio:")
    for r in worst:
        print("      %4s/%-4s regs %-3s copies %-5s %s" % (r[pre + "states"], r[pre + "ustates"], r[pre + "regs"],
                                                       r[pre + "copies"], r["pattern_esc"]))
    worst = sorted(IN, key=lambda r: -num(r, pre + "copies"))[:8]
    print("  most copies:")
    for r in worst:
        print("      copies %-5s states %-4s regs %-3s %s" % (r[pre + "copies"], r[pre + "states"], r[pre + "regs"],
                                                          r["pattern_esc"]))

print("\nFIXED-OFFSET CONTROL (verify_fixed over every subject, both machines): patterns with a violation %d"
      % sum(1 for r in IN if r.get("fixed_viol") not in ("0", "", None)))
print("\nBENCH rows:")
for r in rows:
    if r["src"] != "corpus":
        print("  %-4s %-8s a:states %-4s/%-4s regs_nf %-2s allfixed %-2s cf_nf %-2s  %s" % (
            r["status"], r["prefilter"], r["a_states"], r["a_ustates"], r["a_regs_nf"], r["a_allfixed"],
            r["a_copyfree_nf"], r["pattern_esc"][:70] if r["status"] == "in" else r["why"]))
