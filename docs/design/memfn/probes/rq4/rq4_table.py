#!/usr/bin/env python3
"""docs/design/memfn/probes/rq4/rq4_table.py -- renders an rq4.py run (raw.tsv
+ meta.tsv + header.txt + arms.tsv) as the RQ-4 tier-U reading (lane rq4h;
arm list and prior re-read by lane s21prep).

    python3 rq4_table.py RUNDIR [--sib-max 5] [--out FILE] [--prior RUNDIR]

The run's arms come from arms.tsv (a slot20 run has none: they are read off
meta.tsv's `forms_<ARM>` columns, which is the same list). Per (cell, regime,
level): every arm's median over launches (ns), the largest launch spread
among them, then one delta per PAIR (rq4_arms.PAIRS, those whose two arms
were run), each against its own null band, each with a sign verdict. Slot20's
D-K (DEFAULT - KBDENY, "KB verdict": + = KB costs) and ON-OFF (DEFAULT - OFF,
"SIMD verdict": + = SIMD costs) keep their names; slot21 adds D-F (R-14 verify
vs R-13's), N-F (trim vs R-13's), D-N (pad vs trim), F-K, and with slot21x
F-FK. Verdict: LOSS if delta > +floor, WIN if delta < -floor, NULL otherwise;
NO-BAND where the regime has no null cell. A row whose arms disagree on the
answer (hits, subject hash, position sum) reads ANSWER-MISMATCH and gets no
verdict.

THE NULL BAND (integration.md §R4.9.5 item 5). For a pair (X, Y) the null
population is every cell whose X and Y artifacts are BYTE-IDENTICAL (meta.tsv
`id_*` columns, set by rq4.py's facts stage, not by the cells.tsv class): the
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

--prior RUNDIR (slot21's re-read of slot20): RUNDIR is a finished earlier run
(slot20's `run/`). Its D-K LOSS comparisons are listed, each next to this
run's D-K, F-K and F-FK on the same (cell, regime, level), with the count that
remain. This run's DEFAULT differs from the prior's (R-14's trim and pad), so
the prior's D-K is a different question from this run's D-K; the comparison
that restates it is F-FK (slot21x) -- FULL is R-13's verify and FULLKB is
slot20's KBDENY -- and F-K (slot21) approximates it with KBDENY's trim and pad
still on.
"""
import argparse
import os
import statistics
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rq4_arms  # noqa: E402

PRIOR_SIB_MAX = 5.0   # the prior run is read as its own table read it (slot20: the default 5), whatever --sib-max says
CLASS_ORDER = ("THROUGHPUT", "DENSITY", "PER-CALL", "BENCH")
LEGACY_VERDICT = {"D-K": "KB verdict", "ON-OFF": "SIMD verdict"}   # slot20's column headers


def rows(path):
    with open(path, encoding="utf-8") as f:
        head = f.readline().rstrip("\n").split("\t")
        for ln in f:
            yield dict(zip(head, ln.rstrip("\n").split("\t")))


def delta(rclass, x, y):
    return (x - y) if rclass == "PER-CALL" else 100.0 * (x - y) / y


def unit(rclass):
    return "ns" if rclass == "PER-CALL" else "%"


class Run:
    """one rq4.py run: medians, answers, null bands and the per-pair verdicts"""

    def __init__(self, path, sib_max):
        self.path = path
        mpath = os.path.join(path, "meta.tsv")
        self.meta = {m["cell"]: m for m in rows(mpath)}
        with open(mpath, encoding="utf-8") as f:
            self.mcols = f.readline().rstrip("\n").split("\t")
        apath = os.path.join(path, "arms.tsv")
        if os.path.exists(apath):
            self.arms = [r["arm"] for r in rows(apath)]
        else:
            self.arms = [c[len("forms_"):] for c in self.mcols if c.startswith("forms_")]
        self.pairs = [p for p in rq4_arms.PAIRS if p[0] in self.arms and p[1] in self.arms]
        self.ns = defaultdict(list)     # (cell, rlabel, level, arm) -> [ns]
        self.ans = defaultdict(set)     # (cell, rlabel, level) -> {(hits, fnv, possum)}
        self.rcls, self.order = {}, []
        self.dropped, self.kept = defaultdict(int), defaultdict(int)
        for r in rows(os.path.join(path, "raw.tsv")):
            key = (r["cell"], r["rlabel"], r["level"])
            if key not in self.rcls:
                self.rcls[key] = r["rclass"]
                self.order.append(key)
            self.ans[key].add((r["hits"], r["fnv"], r["possum"]))
            if float(r["sib_busy"]) > sib_max:
                self.dropped[r["arm"]] += 1
                continue
            self.kept[r["arm"]] += 1
            self.ns[key + (r["arm"],)].append(float(r["ns"]))
        self.band = {}                  # (pair short, rlabel, level) -> (floor, n)
        for x, y, pname, _ in self.pairs:
            acc = defaultdict(list)
            for key in self.order:
                cell, rl, lv = key
                if self.is_null(cell, x, y) is not True or len(self.ans[key]) != 1:
                    continue
                mx, my = self.med(key, x), self.med(key, y)
                if mx is not None and my is not None:
                    acc[(rl, lv)].append(abs(delta(self.rcls[key], mx, my)))
            for k, v in acc.items():
                self.band[(pname,) + k] = (max(v), len(v))

    def is_null(self, cell, x, y):
        """True if the cell's x and y artifacts are byte-identical, False if not, None if meta lacks the column"""
        for col in (rq4_arms.id_col(x, y), rq4_arms.id_col(y, x)):
            if col in self.meta[cell]:
                return self.meta[cell][col] == "1"
        return None

    def med(self, key, arm):
        v = self.ns.get(key + (arm,))
        return statistics.median(v) if v else None

    def spread(self, key):
        s = 0.0
        for arm in self.arms:
            v = self.ns.get(key + (arm,))
            if v and len(v) > 1:
                s = max(s, 100.0 * (max(v) - min(v)) / statistics.median(v))
        return s

    def cmp(self, pair, key):
        """(delta or None, floor or None, verdict) of one pair at one (cell, regime, level)"""
        x, y, pname, _ = pair
        if len(self.ans[key]) != 1:
            return None, None, "ANSWER-MISMATCH"
        mx, my = self.med(key, x), self.med(key, y)
        if mx is None or my is None:
            return None, None, "NO-DATA"
        rc = self.rcls[key]
        d = delta(rc, mx, my)
        b = self.band.get((pname, key[1], key[2]))
        fl = b[0] if b else None
        if self.is_null(key[0], x, y):
            return d, fl, "null-cell"
        if not b:
            return d, None, "NO-BAND"
        return d, fl, "LOSS" if d > fl else "WIN" if d < -fl else "NULL"


def short_names(arms):
    ini = [a[0] for a in arms]
    return ini if len(set(ini)) == len(ini) else list(arms)


def render(run, a):
    out = []
    w = out.append
    hdr = os.path.join(run.path, "header.txt")
    if os.path.exists(hdr):
        w("```")
        w(open(hdr).read().rstrip())
        w("```")
        w("")
    if any(p[2] not in LEGACY_VERDICT for p in run.pairs):
        w("Pairs (delta = first - second; + = the first costs):")
        w("")
        for x, y, pname, desc in run.pairs:
            w("- %s = %s - %s: %s" % (pname, x, y, desc))
        w("")
    w("Readings kept / dropped (sibling busy > %.1f%%): %s" %
      (a.sib_max, ", ".join("%s %d/%d" % (arm, run.kept[arm], run.dropped[arm]) for arm in run.arms)))
    w("")
    w("## Null bands (floor = max |delta| over byte-identical cells; n = null cells)")
    w("")
    w("| regime | level | %s |" % " | ".join("%s floor | n" % p[2] for p in run.pairs))
    w("|---|---|" + "---|---|" * len(run.pairs))
    seen = []
    for cell, rl, lv in run.order:
        if (rl, lv) not in seen:
            seen.append((rl, lv))
    cls_of = {(rl, lv): run.rcls[(c, rl, lv)] for c, rl, lv in run.order}
    for rl, lv in seen:
        u = unit(cls_of[(rl, lv)])
        cells = []
        for p in run.pairs:
            b = run.band.get((p[2], rl, lv))
            cells += ["%.2f %s" % (b[0], u), str(b[1])] if b else ["-", "0"]
        w("| %s | %s | %s |" % (rl, lv, " | ".join(cells)))
    w("")

    tally = defaultdict(lambda: defaultdict(int))
    losses = defaultdict(list)
    tested = defaultdict(int)
    w("## Per cell (medians over launches, ns; spread = largest launch spread among the arms)")
    by_cell = defaultdict(list)
    for key in run.order:
        by_cell[key[0]].append(key)
    sn = dict(zip(run.arms, short_names(run.arms)))
    for cell, keys in by_cell.items():
        m = run.meta[cell]
        w("")
        w("### %s (%s, engine %s) `%s`" % (cell, m["class"], m["engine"], m["pattern"]))
        w("FORMS %s = %s; identical %s; KA %s, KB %s; live v1 %s; v3 %s" %
          ("/".join(sn[x] for x in run.arms), " / ".join(m["forms_" + x] for x in run.arms),
           ", ".join("%s=%s %s" % (sn[p[0]], sn[p[1]], "?" if run.is_null(cell, p[0], p[1]) is None
                                    else int(run.is_null(cell, p[0], p[1]))) for p in run.pairs),
           m["ka"], m["kb"], m["live_v1"], m["live_v3"]))
        w("")
        w("| regime | lvl | %s | spread%% | %s |" %
          (" | ".join(run.arms), " | ".join("%s | band | %s" % (p[2], LEGACY_VERDICT.get(p[2], p[2] + " verdict"))
                                            for p in run.pairs)))
        w("|---|---|%s---|%s" % ("---|" * len(run.arms), "---|---|---|" * len(run.pairs)))
        for key in keys:
            _, rl, lv = key
            rc = run.rcls[key]
            u = unit(rc)
            line = [rl, lv] + ["%.1f" % run.med(key, arm) if run.med(key, arm) is not None else "-"
                               for arm in run.arms]
            line.append("%.1f" % run.spread(key))
            for p in run.pairs:
                d, fl, v = run.cmp(p, key)
                if d is None:
                    line += ["-", "-", v]
                    continue
                if v in ("LOSS", "WIN", "NULL"):
                    tally[p[2]][(rc, lv, v)] += 1
                    tested[p[2]] += 1
                    if v == "LOSS":
                        losses[p[2]].append("%s %s %s %+.2f%s (floor %.2f)" % (cell, rl, lv, d, u, fl))
                line += ["%+.2f %s" % (d, u), "%.2f" % fl if fl is not None else "-", v]
            w("| " + " | ".join(line) + " |")
    w("")
    w("## Summary (comparisons tested per pair, so the multiple-comparison exposure is visible)")
    for x, y, pname, _ in run.pairs:
        w("")
        w("### %s (%s - %s): %d comparisons" % (pname, x, y, tested[pname]))
        w("")
        w("| class | level | WIN | NULL | LOSS |")
        w("|---|---|---|---|---|")
        for rc in CLASS_ORDER:
            for lv in ("v1", "v3"):
                t = tally[pname]
                if any(t[(rc, lv, v)] for v in ("WIN", "NULL", "LOSS")):
                    w("| %s | %s | %d | %d | %d |" % (rc, lv, t[(rc, lv, "WIN")], t[(rc, lv, "NULL")],
                                                     t[(rc, lv, "LOSS")]))
        w("")
        w("LOSS past the floor (%d):" % len(losses[pname]))
        for s in losses[pname]:
            w("- " + s)
    return out


def fmt(run, pair, key):
    """'+0.26ns LOSS' style cell of one comparison, or '-' where the pair was not run"""
    if pair is None:
        return "-"
    d, fl, v = run.cmp(pair, key)
    if d is None:
        return v
    return "%+.2f%s %s" % (d, unit(run.rcls[key]), v)


def reread(run, prior, w):
    """slot21's re-read of slot20's D-K LOSS comparisons"""
    pk = next((p for p in prior.pairs if p[2] == "D-K"), None)
    if pk is None:
        w("(the prior run has no D-K pair: nothing to re-read)")
        return
    pick = lambda r, n: next((p for p in r.pairs if p[2] == n), None)
    dk, fk, ffk = pick(run, "D-K"), pick(run, "F-K"), pick(run, "F-FK")
    lost = [k for k in prior.order if prior.cmp(pk, k)[2] == "LOSS"]
    w("## Re-read of the prior run's KB losses (%s)" % prior.path)
    w("")
    w("The prior run's D-K = DEFAULT - KBDENY on R-13's whole-run verify (trim and pad did not exist). This run's "
      "D-K is the same arms on R-14's verify (trim + pad ON in both). F-K = FULL - KBDENY (FULL is R-13's verify with "
      "KA and KB; this run's KBDENY keeps trim and pad, so F-K approximates the prior D-K but is not text-identical "
      "to it). F-FK = FULL - FULLKB (slot21x only; FULLKB is the prior KBDENY's text): the prior D-K restated.")
    w("")
    w("Prior D-K LOSS comparisons: %d. Present in this run (same cell, regime, level): %d." %
      (len(lost), sum(1 for k in lost if k in run.rcls)))
    w("")
    cnt = defaultdict(lambda: defaultdict(int))
    for name, pair in (("D-K", dk), ("F-K", fk), ("F-FK", ffk)):
        if pair is None:
            continue
        for k in lost:
            if k in run.rcls:
                d, _, v = run.cmp(pair, k)
                cnt[name][v] += 1
                if d is not None and d > 0:
                    cnt[name]["+"] += 1   # same sign as the prior's (every prior LOSS has delta > 0), past the floor or not
    w("| this run's comparison on those %d | LOSS (persists) | NULL | WIN | other | delta > 0 (the prior's sign) |" % len(lost))
    w("|---|---|---|---|---|---|")
    for name, pair in (("D-K", dk), ("F-K", fk), ("F-FK", ffk)):
        if pair is None:
            w("| %s | not run | | | | |" % name)
            continue
        c = cnt[name]
        oth = sum(v for k2, v in c.items() if k2 not in ("LOSS", "NULL", "WIN", "+"))
        w("| %s | %d | %d | %d | %d | %d |" % (name, c["LOSS"], c["NULL"], c["WIN"], oth, c["+"]))
    w("")
    if dk:
        new = [k for k in run.order if k not in set(lost) and run.cmp(dk, k)[2] == "LOSS"]
        w("D-K LOSS in this run that were NOT among the prior's: %d" % len(new))
        w("")
    w("| cell | regime | lvl | prior D-K | this D-K | this F-K | this F-FK |")
    w("|---|---|---|---|---|---|---|")
    for k in lost:
        if k not in run.rcls:
            w("| %s | %s | %s | %s | (cell/regime not run) | | |" % (k[0], k[1], k[2], fmt(prior, pk, k)))
            continue
        w("| %s | %s | %s | %s | %s | %s | %s |" %
          (k[0], k[1], k[2], fmt(prior, pk, k), fmt(run, dk, k), fmt(run, fk, k), fmt(run, ffk, k)))
    w("")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--sib-max", type=float, default=5.0)
    ap.add_argument("--out", default="")
    ap.add_argument("--prior", default="", help="a finished earlier run (slot20's run/) whose D-K losses to re-read")
    a = ap.parse_args()
    run = Run(a.run, a.sib_max)
    out = render(run, a)
    if a.prior:
        reread(run, Run(a.prior, PRIOR_SIB_MAX), out.append)
    text = "\n".join(out) + "\n"
    if a.out:
        open(a.out, "w").write(text)
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
