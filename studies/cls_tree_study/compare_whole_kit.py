#!/usr/bin/env python3
"""compare_whole_kit.py -- [CLS-TREE] S0, a1's OWED byte-tier half
(docs/design/cls_tree_design.md sect. 7(a), a1): "the same [whole-set check]
for the 41 byte classes (expected: the DP never picks a whole-set table
there, since MASK64/CUBES carry no load)".

verify_whole.py already answers the EXHAUSTIVE-CORRECTNESS half for any
population, `byteclasses` included (clsets.population dispatches on the
name). What was missing is the COMPARISON that turns "here are two more
sizes" into "confirmed/refuted": per byte class, is either whole-set form
(`page2w`/`page3w`) ever smaller than the kit's own size-minimal sectioned
answer (`sweep.py`'s lam=0 "size" policy row, already swept and committed at
`results/sweep_byteclasses.tsv`)? If never, the DP offering whole-set
sections at the byte tier would be pure surface area for zero wins there --
confirming the design note's expectation rather than assuming it.

Usage:
    python3 compare_whole_kit.py [whole_tsv] [sweep_tsv]
        (defaults: results/whole_byteclasses.tsv, results/sweep_byteclasses.tsv;
        run `python3 verify_whole.py byteclasses > results/whole_byteclasses.tsv`
        and `make byteclasses` first if those are missing)

Writes results/whole_vs_kit_byteclasses.tsv and prints the verdict line.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _read_tsv(path):
    rows = []
    header = None
    for line in open(path, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        if header is None:
            header = f
            continue
        if f[0] == "TOTAL mismatches:" or f[0].startswith("TOTAL"):
            continue
        rows.append(dict(zip(header, f)))
    return rows


def kit_size_minimal(sweep_rows):
    """One row per set: the lam=0 ("size") policy's total object bytes --
    the kit's own smallest answer, the thing a whole-set candidate would
    have to BEAT to ever be chosen at that end of the dial."""
    out = {}
    for r in sweep_rows:
        if r.get("lam") == "0" and r.get("policy") == "size":
            out[r["set"]] = int(r["total"])
    return out


def main():
    whole_path = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.join(HERE, "results", "whole_byteclasses.tsv")
    sweep_path = sys.argv[2] if len(sys.argv) > 2 else \
        os.path.join(HERE, "results", "sweep_byteclasses.tsv")
    out_path = os.path.join(HERE, "results", "whole_vs_kit_byteclasses.tsv")

    whole = _read_tsv(whole_path)
    kit_min = kit_size_minimal(_read_tsv(sweep_path))

    missing = [r["set"] for r in whole if r["set"] not in kit_min]
    if missing:
        raise SystemExit("compare_whole_kit: no size-minimal kit row for: %s"
                          % ", ".join(missing))

    wins = ties = losses = 0
    lines = ["set\tkit_size_total\tpage2w_obj\tpage3w_obj\tbest_whole\tverdict"]
    for r in whole:
        name = r["set"]
        kt = kit_min[name]
        p2, p3 = int(r["page2w_obj"]), int(r["page3w_obj"])
        best = min(p2, p3)
        if best < kt:
            verdict = "WHOLE-WINS"
            wins += 1
        elif best == kt:
            verdict = "TIE"
            ties += 1
        else:
            verdict = "kit-wins"
            losses += 1
        lines.append("%s\t%d\t%d\t%d\t%d\t%s" % (name, kt, p2, p3, best, verdict))

    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    n = len(whole)
    print("\n".join(lines))
    print("# sets=%d WHOLE-WINS=%d TIE=%d kit-wins=%d" % (n, wins, ties, losses))
    if wins == 0:
        print("VERDICT: CONFIRMED -- no byte class in the 41-set corpus "
              "population has a whole-set (page2w/page3w) object size "
              "strictly smaller than the kit's own size-minimal sectioned "
              "answer (%d ties, %d kit-wins, 0 whole-wins). The DP offering "
              "whole-set sections at the byte tier would win nothing on "
              "size there; MASK64/CUBES/BITMAP already cover a <=256-code-"
              "point domain at kit prices with no per-page index overhead."
              % (ties, losses))
        return 0
    print("VERDICT: REFUTED -- %d byte class(es) have a smaller whole-set "
          "object than the kit's size-minimal answer; see %s"
          % (wins, out_path))
    return 1


if __name__ == "__main__":
    sys.exit(main())
