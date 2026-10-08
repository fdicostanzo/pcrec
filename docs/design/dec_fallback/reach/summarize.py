#!/usr/bin/env python3
"""[DEC-FALLBACK] rev 2: reach.tsv (analyse.py) -> reach.md, the row x
variant table the note's §4.3a cites: per row/cell, the count at the `base`
arm in each variant, the total over every arm, the arms that reach it, and
one witness (the first, corpus before constructed). usage:
summarize.py OUT_DIR > reach.md"""
import collections, csv, sys

out = sys.argv[1]
rows = list(csv.DictReader(open(out + "/reach.tsv"), delimiter="\t"))
VARS = ["plain", "lowsize", "lowdfa", "lowboth", "lowthr"]
ORDER = {
 "T1": ["forcing", "nomem", "size-term-trial", "sel1-collapse", "sel1-drop", "unroll-rescue",
        "prefilter-collapse", "drop-anchored", "drop-premul", "drop-prefilter", "refuse"],
 "T2": ["backref", "linked-call", "var-nullable", "nullable-exact", "nullable-collapsed",
        "overflow-drop", "forced-on", "forced-off", "var", "default-on", "default-off"],
 "T3": ["rung-sizecap", "rung-sel1", "forced", "nullable", "exact", "no-rep"],
 "T4": ["option", "denied", "default", "cap-rescue", "size-model", "capacity-declined",
        "size-model-declined"],
}
base = collections.Counter(); tot = collections.Counter(); arms = collections.defaultdict(set)
wit = {}
for r in rows:
    k = (r["table"], r["row"], r["scope"])
    n = int(r["n"])
    tot[k] += n
    arms[k].add(r["arm"])
    if r["arm"] == "base":
        base[k + (r["variant"],)] += n
    w = (r["witness_src"], r["witness_pattern"], r["flags"], r["encoding"], r["variant"], r["arm"])
    if k not in wit or (wit[k][0] != "corpus" and w[0] == "corpus"):
        wit[k] = w
print("# Row reach (prototype, `reach/`), per table row and cell\n")
print("Counts are ATTEMPTS (T1: arrivals; T2/T3: admissions/gates; T4: compiles)"
      " at the `base` arm per variant; `all arms` sums every variant x arm;"
      " `arms` lists the arms that reach the cell. One witness each.\n")
for t, names in ORDER.items():
    print("## %s\n" % t)
    print("| row | cell | " + " | ".join(VARS) + " | all arms | arms | witness |")
    print("|---|---|" + "---:|" * len(VARS) + "---:|---|---|")
    cells = sorted({k for k in tot if k[0] == t}, key=lambda k: (names.index(k[1]) if k[1] in names else 99, k[2]))
    seen = {k[1] for k in cells}
    for nm in names:
        if nm not in seen:
            print("| %s | - | " % nm + " | ".join("0" for _ in VARS) + " | **0** | - | - |")
    for k in cells:
        w = wit[k]
        ws = "`%s` %s%s%s (%s/%s)" % (w[1].replace("|", "\\|")[:60], ("-" + w[2] + " ") if w[2] else "",
                                       ("-e " + w[3] + " ") if w[3] else "", w[0] if w[0] != "corpus" else "",
                                       w[4], w[5])
        print("| %s | %s | " % (k[1], k[2]) + " | ".join(str(base[k + (v,)]) for v in VARS) +
              " | %d | %s | %s |" % (tot[k], ",".join(sorted(arms[k])), ws))
    print()
