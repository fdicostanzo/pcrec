#!/usr/bin/env python3
"""docs/design/memfn/probes/rq4/rq4_table.py -- renders an rq4.py run (raw.tsv
+ meta.tsv + header.txt) as the RQ-4 tier-U reading (lane rq4h).

    python3 rq4_table.py RUNDIR [--sib-max 5] [--out FILE]

Per (cell, regime, level): the three arms' medians over launches (ns), the
largest launch spread among them, then two deltas, each against its own null
band, each with a sign verdict:
  DEFAULT - KBDENY   the KB question (rankuse_report.md §6); + = KB costs
  DEFAULT - OFF      SIMD-on against SIMD-off (D147: both layers);  + = SIMD costs
Verdict: LOSS if delta > +floor, WIN if delta < -floor, NULL otherwise;
NO-BAND where the regime has no null cell. A row whose arms disagree on the
answer (hits, subject hash, position sum) reads ANSWER-MISMATCH and gets no
verdict.

THE NULL BAND (integration.md §R4.9.5 item 5). For a pair (X, Y) the null
population is every cell whose X and Y artifacts are BYTE-IDENTICAL (meta.tsv
id_DK / id_DO, set by rq4.py's facts stage, not by the cells.tsv class): the
same text timed as two arms in the same run, same binaries set, same
interleave. Per (regime, level) its delta is computed exactly as a mover's,
and the FLOOR is the maximum |delta| over those cells (`UNMEASURED DEFAULT:`
the maximum, until the null distribution supports a quantile). Unit by regime
class: THROUGHPUT, DENSITY and BENCH deltas are RELATIVE (% of Y's median);
PER-CALL deltas are ABSOLUTE ns (D144 addendum 1: absolute deltas against a
floor; a ratio only well above the timer floor).

Readings whose SMT siblings were busier than --sib-max % (`UNMEASURED
DEFAULT:` 5, §R4.9.5 item 2) are discarded before the median; the count is
reported per arm.
"""
import argparse
import os
import statistics
import sys
from collections import defaultdict

PAIRS = [("DEFAULT", "KBDENY", "id_DK", "D-K"), ("DEFAULT", "OFF", "id_DO", "ON-OFF")]
ARMS = ("DEFAULT", "KBDENY", "OFF")


def rows(path):
    with open(path, encoding="utf-8") as f:
        head = f.readline().rstrip("\n").split("\t")
        for ln in f:
            yield dict(zip(head, ln.rstrip("\n").split("\t")))


def delta(rclass, x, y):
    return (x - y) if rclass == "PER-CALL" else 100.0 * (x - y) / y


def unit(rclass):
    return "ns" if rclass == "PER-CALL" else "%"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--sib-max", type=float, default=5.0)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    meta = {m["cell"]: m for m in rows(os.path.join(a.run, "meta.tsv"))}
    ns = defaultdict(list)          # (cell, rlabel, level, arm) -> [ns]
    ans = defaultdict(set)          # (cell, rlabel, level) -> {(hits, fnv, possum)}
    rcls, order, dropped, kept = {}, [], defaultdict(int), defaultdict(int)
    for r in rows(os.path.join(a.run, "raw.tsv")):
        key = (r["cell"], r["rlabel"], r["level"])
        if key not in rcls:
            rcls[key] = r["rclass"]
            order.append(key)
        ans[key].add((r["hits"], r["fnv"], r["possum"]))
        if float(r["sib_busy"]) > a.sib_max:
            dropped[r["arm"]] += 1
            continue
        kept[r["arm"]] += 1
        ns[key + (r["arm"],)].append(float(r["ns"]))

    def med(key, arm):
        v = ns.get(key + (arm,))
        return statistics.median(v) if v else None

    def spread(key):
        s = 0.0
        for arm in ARMS:
            v = ns.get(key + (arm,))
            if v and len(v) > 1:
                s = max(s, 100.0 * (max(v) - min(v)) / statistics.median(v))
        return s

    # null bands: (pair, rlabel, level) -> (floor, n)
    band = {}
    for x, y, idk, pname in PAIRS:
        acc = defaultdict(list)
        for key in order:
            cell, rl, lv = key
            if meta[cell][idk] != "1" or len(ans[key]) != 1:
                continue
            mx, my = med(key, x), med(key, y)
            if mx is not None and my is not None:
                acc[(rl, lv)].append(abs(delta(rcls[key], mx, my)))
        for k, v in acc.items():
            band[(pname,) + k] = (max(v), len(v))

    out = []
    w = out.append
    hdr = os.path.join(a.run, "header.txt")
    if os.path.exists(hdr):
        w("```")
        w(open(hdr).read().rstrip())
        w("```")
        w("")
    w("Readings kept / dropped (sibling busy > %.1f%%): %s" %
      (a.sib_max, ", ".join("%s %d/%d" % (arm, kept[arm], dropped[arm]) for arm in ARMS)))
    w("")
    w("## Null bands (floor = max |delta| over byte-identical cells; n = null cells)")
    w("")
    w("| regime | level | D-K floor | n | ON-OFF floor | n |")
    w("|---|---|---|---|---|---|")
    seen = []
    for cell, rl, lv in order:
        if (rl, lv) not in seen:
            seen.append((rl, lv))
    cls_of = {(rl, lv): rcls[(c, rl, lv)] for c, rl, lv in order}
    for rl, lv in seen:
        u = unit(cls_of[(rl, lv)])
        cells = []
        for pname in ("D-K", "ON-OFF"):
            b = band.get((pname, rl, lv))
            cells += ["%.2f %s" % (b[0], u), str(b[1])] if b else ["-", "0"]
        w("| %s | %s | %s |" % (rl, lv, " | ".join(cells)))
    w("")

    tally = defaultdict(lambda: defaultdict(int))
    losses = defaultdict(list)
    tested = defaultdict(int)
    w("## Per cell (medians over launches, ns; spread = largest launch spread among the arms)")
    by_cell = defaultdict(list)
    for key in order:
        by_cell[key[0]].append(key)
    for cell, keys in by_cell.items():
        m = meta[cell]
        w("")
        w("### %s (%s, engine %s) `%s`" % (cell, m["class"], m["engine"], m["pattern"]))
        w("FORMS D/K/O = %s / %s / %s; identical D=K %s, D=O %s; KA %s, KB %s; live v1 %s; v3 %s" %
          (m["forms_DEFAULT"], m["forms_KBDENY"], m["forms_OFF"], m["id_DK"], m["id_DO"], m["ka"], m["kb"],
           m["live_v1"], m["live_v3"]))
        w("")
        w("| regime | lvl | DEFAULT | KBDENY | OFF | spread% | D-K | band | KB verdict | ON-OFF | band | SIMD verdict |")
        w("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for key in keys:
            _, rl, lv = key
            rc = rcls[key]
            u = unit(rc)
            md = {arm: med(key, arm) for arm in ARMS}
            line = [rl, lv] + ["%.1f" % md[arm] if md[arm] is not None else "-" for arm in ARMS]
            line.append("%.1f" % spread(key))
            for x, y, idk, pname in PAIRS:
                if len(ans[key]) != 1:
                    line += ["-", "-", "ANSWER-MISMATCH"]
                    continue
                if md[x] is None or md[y] is None:
                    line += ["-", "-", "NO-DATA"]
                    continue
                d = delta(rc, md[x], md[y])
                b = band.get((pname, rl, lv))
                if m[idk] == "1":
                    v = "null-cell"
                elif not b:
                    v = "NO-BAND"
                else:
                    v = "LOSS" if d > b[0] else "WIN" if d < -b[0] else "NULL"
                    tally[pname][(rc, lv, v)] += 1
                    tested[pname] += 1
                    if v == "LOSS":
                        losses[pname].append("%s %s %s %+.2f%s (floor %.2f)" % (cell, rl, lv, d, u, b[0]))
                line += ["%+.2f %s" % (d, u), "%.2f" % b[0] if b else "-", v]
            w("| " + " | ".join(line) + " |")
    w("")
    w("## Summary (comparisons tested per pair, so the multiple-comparison exposure is visible)")
    for x, y, idk, pname in PAIRS:
        w("")
        w("### %s (%s - %s): %d comparisons" % (pname, x, y, tested[pname]))
        w("")
        w("| class | level | WIN | NULL | LOSS |")
        w("|---|---|---|---|---|")
        for rc in ("THROUGHPUT", "DENSITY", "PER-CALL", "BENCH"):
            for lv in ("v1", "v3"):
                t = tally[pname]
                if any(t[(rc, lv, v)] for v in ("WIN", "NULL", "LOSS")):
                    w("| %s | %s | %d | %d | %d |" % (rc, lv, t[(rc, lv, "WIN")], t[(rc, lv, "NULL")],
                                                     t[(rc, lv, "LOSS")]))
        w("")
        w("LOSS past the floor (%d):" % len(losses[pname]))
        for s in losses[pname]:
            w("- " + s)
    text = "\n".join(out) + "\n"
    if a.out:
        open(a.out, "w").write(text)
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
