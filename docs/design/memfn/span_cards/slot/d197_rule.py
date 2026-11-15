# span_cards/slot/d197_rule.py — D197's decision for the mfcard window, by the DECLARED table d197_rule.tsv (review
# 2026-11-15 r5 FIDELITY-4; written before any number exists; the table is the rule, this file its reader).
#   python3 -I d197_rule.py rule RUNDIR AVX2RUNDIR   the verdict from the two finalized records: RUNDIR timed with
#                                                    glibc's memchr as shipped, AVX2RUNDIR under the AVX2 tunable
#                                                    (each its own record, record.py's `libc` names the variant)
#   python3 -I d197_rule.py drill [SCRATCH]          the rule on CONSTRUCTED outcomes (no rundir): each case's
#                                                    expected verdict, `== d197 DRILL ok` iff all agree; SCRATCH:
#                                                    also end to end on est.py's synthetic mfcard window
# One line per deciding cell and arm, then `d197_verdict WIN|LOSS|NO-VERDICT`. Exit 0 on a verdict, 2 on input.
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from est import med, trim, compute, read_record, InputError  # noqa: E402  (the estimator's primitives, ONE home)

def load(path=os.path.join(HERE, "d197_rule.tsv")):
    sec, t = None, {}
    for ln in open(path):
        ln = ln.rstrip("\n")
        if ln.startswith("#section "):
            sec = ln.split()[1]
            t[sec] = []
        elif ln and not ln.startswith("#"):
            t[sec].append(tuple(ln.split("\t")))
    t["deciding"] = dict(t["deciding"])
    return t

def cells(t):
    d = t["deciding"]
    return [(int(g), int(r)) for g in d["gaps"].split(",") for r in d["rejects"].split(",")]

def key(t, form, g, r):
    d = t["deciding"]
    return "kit.%s.%s.%s.%s.%d.%d" % (d["quantity"], form, d["landing"], d["split"], g, r)

# THE NAMED PREDICATES (the table's `when` words), one line each
WHEN = {
    "either-row-unpriced": lambda c: c["a"] is None or c["b"] is None,
    "gain-beyond-floor-and-every-trimmed-launch-positive":
        lambda c: c["gain"] > c["floor"] and all(x > 0 for x in trim(c["gain_l"])),
    "gain-below-minus-floor": lambda c: c["gain"] < -c["floor"],
    "run-refused": lambda a: a["outcome"] == "REFUSED",
    "memchr-variant-not-the-arms": lambda a: a["variant"] != a["want_variant"] and a["want_variant"] != "any"
                                             or a["variant"] is None,
    "any-cell-loss": lambda a: a["n"]["loss"] > 0,
    "wins-over-half-of-deciding-cells": lambda a: 2 * a["n"]["win"] > a["n_cells"],
    "shipped-arm-no-verdict": lambda v: v["shipped"] == "no-verdict",
    "shipped-arm-loss": lambda v: v["shipped"] == "LOSS",
    "avx2-arm-no-verdict": lambda v: v["avx2"] == "no-verdict",
    "avx2-arm-not-win": lambda v: v["avx2"] != "WIN",
    "always": lambda _x: True,
}

def first(t, table, x):
    for res, when in t[table]:
        if WHEN[when](x):
            return res, when
    raise InputError("d197_rule.tsv: table %s has no row for %r" % (table, x))

def row_x(out, drift, k):
    """the row's per-launch x and A/A, or None (absent, drifted, or no W)"""
    r = out.get(k)
    if not r or "absent" in r or "x" not in r or drift.get(r["job"], (0, 0, False))[2]:
        return None
    return r

def arm(t, out, drift, outcome, run, want_variant):
    """(arm verdict, lines): one arm (a finalized record) through the cell and arm tables"""
    lvl = (run.get("isa") or "?").split()[0]
    fused = dict(t["fused"]).get(lvl)
    if fused is None:
        raise InputError("box level %s names no fused form in d197_rule.tsv's `fused` table" % lvl)
    libc = t["deciding"]["libc_form"]
    var = next((w.split("=", 1)[1] for w in (run.get("libc") or "").split() if w.startswith("memchr=")), None)
    n, lines = {"win": 0, "loss": 0, "tie": 0, "unresolved": 0}, []
    for g, r in cells(t):
        a, b = row_x(out, drift, key(t, libc, g, r)), row_x(out, drift, key(t, fused, g, r))
        c = {"a": a, "b": b}
        if a and b:
            c["gain_l"] = [a["x"][i] - b["x"][i] for i in range(len(a["x"]))]
            c.update(gain=med(c["gain_l"]), floor=a["aa"] + b["aa"])
        res, why = first(t, "cell", c)
        n[res] += 1
        lines.append("cell\tgap %d reject %d\t%s vs %s\t%s\tgain %s floor %s\t(%s)" % (
            g, r, fused, libc, res, c.get("gain", "-"), c.get("floor", "-"), why))
    av = {"outcome": outcome, "variant": var, "want_variant": want_variant, "n": n, "n_cells": len(cells(t))}
    res, why = first(t, "arm", av)
    lines.append("arm\t%s vs %s (memchr=%s, box %s)\t%s\t%s\t(%s)" % (fused, libc, var, lvl, res,
                 " ".join("%s %d" % kv for kv in sorted(n.items())), why))
    return res, lines

def verdict(t, shipped, avx2):
    return first(t, "verdict", {"shipped": shipped, "avx2": avx2})

def rule(rundir, avx2dir):
    t = load()
    out = []
    got = {}
    for name, d, want in (("shipped", rundir, "any"), ("avx2", avx2dir, "avx2")):
        o, drift, _ub, outcome, _w, _p = compute(d)
        res, lines = arm(t, o, drift, outcome[0], read_record(d)["run"], want)
        got[name] = res
        out += ["%s\t%s" % (name, ln) for ln in lines]
    v, why = verdict(t, got["shipped"], got["avx2"])
    return v, why, out

# ---- the drill: CONSTRUCTED outcomes, each with the verdict the rule must give ---------------------------------
def _arm_out(t, fused, libc_x, fused_x, aa=20, per_cell=None):
    """a constructed est `out` for one arm: every deciding cell's two rows with 7 launch values (libc_x, fused_x
    lists or a per-cell override {(gap, reject): (libc_x, fused_x)})"""
    out = {}
    for g, r in cells(t):
        lx, fx = (per_cell or {}).get((g, r), (libc_x, fused_x))
        out[key(t, t["deciding"]["libc_form"], g, r)] = {"job": "JMH", "x": list(lx), "aa": aa}
        out[key(t, fused, g, r)] = {"job": "JMH", "x": list(fx), "aa": aa}
    return out

def drill(scratch=None):
    t = load()
    run = lambda var: {"isa": "x86-64-v4 avx512f avx2", "libc": "glibc 2.43 memchr=%s" % var}
    L7 = lambda v: [v] * 7
    small = {(g, r) for g, r in cells(t) if g <= 64}
    win_small = {c: (L7(1000), L7(500)) for c in small}
    CASES = (   # (name, shipped arm (out, outcome, variant), avx2 arm, expected verdict)
        ("clean win on every cell, both libc variants", (_arm_out(t, "mfind-w32", L7(1000), L7(500)), "FULL", "evex"),
         (_arm_out(t, "mfind-w32", L7(1000), L7(500)), "FULL", "avx2"), "WIN"),
        ("clean loss", (_arm_out(t, "mfind-w32", L7(1000), L7(1500)), "FULL", "evex"),
         (_arm_out(t, "mfind-w32", L7(1000), L7(1500)), "FULL", "avx2"), "LOSS"),
        ("within-floor tie on every cell (gain 30, floor 40): LOSS", (_arm_out(t, "mfind-w32", L7(1000), L7(970)), "FULL",
         "evex"), (_arm_out(t, "mfind-w32", L7(1000), L7(970)), "FULL", "avx2"), "LOSS"),
        ("clean win, one outlier launch (launch 3's fused cost x10) trimmed away",
         (_arm_out(t, "mfind-w32", L7(1000), [500, 500, 5000, 500, 500, 500, 500]), "FULL", "evex"),
         (_arm_out(t, "mfind-w32", L7(1000), L7(500)), "FULL", "avx2"), "WIN"),
        ("two outlier launches: a trimmed launch negative, no cell wins: LOSS",
         (_arm_out(t, "mfind-w32", L7(1000), [500, 500, 5000, 5000, 500, 500, 500]), "FULL", "evex"),
         (_arm_out(t, "mfind-w32", L7(1000), L7(500)), "FULL", "avx2"), "LOSS"),
        ("the libc variants disagree (wins vs the shipped evex memchr, ties the AVX2 one): LOSS",
         (_arm_out(t, "mfind-w32", L7(1000), L7(500)), "FULL", "evex"),
         (_arm_out(t, "mfind-w32", L7(500), L7(490)), "FULL", "avx2"), "LOSS"),
        ("the libc variants disagree (loses to the shipped memchr, wins vs AVX2): LOSS",
         (_arm_out(t, "mfind-w32", L7(500), L7(1000)), "FULL", "evex"),
         (_arm_out(t, "mfind-w32", L7(1000), L7(500)), "FULL", "avx2"), "LOSS"),
        ("the AVX2 arm's process bound the EVEX memchr (the tunable did nothing): NO-VERDICT",
         (_arm_out(t, "mfind-w32", L7(1000), L7(500)), "FULL", "evex"),
         (_arm_out(t, "mfind-w32", L7(1000), L7(500)), "FULL", "evex"), "NO-VERDICT"),
        ("wins on the hit-dense gaps (<= 64: 12 of 18 cells), ties above: WIN",
         (_arm_out(t, "mfind-w32", L7(1000), L7(990), per_cell=win_small), "FULL", "evex"),
         (_arm_out(t, "mfind-w32", L7(1000), L7(990), per_cell=win_small), "FULL", "avx2"), "WIN"),
        ("wins on the hit-dense gaps, one clean loss at gap 65536: LOSS",
         (_arm_out(t, "mfind-w32", L7(1000), L7(990), per_cell={**win_small, (65536, 0): (L7(1000), L7(1500))}),
          "FULL", "evex"),
         (_arm_out(t, "mfind-w32", L7(1000), L7(500)), "FULL", "avx2"), "LOSS"),
        ("wins on 6 of 18 cells only (gaps <= 8), ties elsewhere: LOSS",
         (_arm_out(t, "mfind-w32", L7(1000), L7(990), per_cell={c: (L7(1000), L7(500)) for c in cells(t) if c[0] <= 8}),
          "FULL", "evex"),
         (_arm_out(t, "mfind-w32", L7(1000), L7(500)), "FULL", "avx2"), "LOSS"),
        ("the shipped arm's run REFUSED: NO-VERDICT", ({}, "REFUSED", "evex"),
         (_arm_out(t, "mfind-w32", L7(1000), L7(500)), "FULL", "avx2"), "NO-VERDICT"),
        ("deciding rows absent on 10 of 18 cells (gaps >= 32), the rest wins: unresolved cells, LOSS",
         ({k: v for k, v in _arm_out(t, "mfind-w32", L7(1000), L7(500)).items() if ".256." not in k and ".1024." not in k
           and ".65536." not in k and ".64." not in k and ".32." not in k}, "PARTIAL", "evex"),
         (_arm_out(t, "mfind-w32", L7(1000), L7(500)), "FULL", "avx2"), "LOSS"),
    )
    bad = 0
    for name, sa, aa, want in CASES:
        r1, _l1 = arm(t, sa[0], {}, sa[1], run(sa[2]), "any")
        r2, _l2 = arm(t, aa[0], {}, aa[1], run(aa[2]), "avx2")
        got, why = verdict(t, r1, r2)
        ok = got == want
        bad += not ok
        print("drill\t%s\t%s\tshipped %s, avx2 %s -> %s (%s)" % (name, "ok" if ok else "WRONG", r1, r2, got, why))
    n = len(CASES)
    if scratch:
        # END TO END: the reader on est.py's own synthetic finalized mfcard window (compute's real row keys and
        # fields), both arms: a verdict, every deciding cell read (none unresolved), no refusal
        import est
        lines = []
        for var, sub in (("evex", "shipped"), ("avx2", "avx2")):
            d = est._synth(os.path.join(scratch, "d197_" + sub), window="mfcard")
            rr = os.path.join(d, "run_record.tsv")
            txt = open(rr).read().replace("run_id\tselftest\n", "run_id\tselftest\nisa\tx86-64-v4 avx2\n"
                                          "libc\tglibc 2.43 memchr=%s\n" % var, 1)
            open(rr, "w").write(txt)
        v, why, lines = rule(os.path.join(scratch, "d197_shipped"), os.path.join(scratch, "d197_avx2"))
        nc = sum(1 for ln in lines if "\tcell\t" in ln and "unresolved" not in ln)
        ok = v in ("WIN", "LOSS") and nc == 2 * len(cells(t))
        bad += not ok
        n += 1
        print("drill\tend to end on est's synthetic window\t%s\t%d of %d cells read, verdict %s (%s)" % (
            "ok" if ok else "WRONG", nc, 2 * len(cells(t)), v, why))
    print("== d197 DRILL %s: %d cases, %d wrong" % ("ok" if not bad else "FAILED", n, bad))
    return 1 if bad else 0

def main():
    if sys.argv[1] == "drill":
        return drill(sys.argv[2] if len(sys.argv) > 2 else None)
    try:
        v, why, lines = rule(sys.argv[2], sys.argv[3])
    except InputError as e:
        print("d197: REFUSED input: %s" % e)
        return 2
    for ln in lines:
        print(ln)
    print("d197_verdict\t%s\t(%s)" % (v, why))
    return 0

if __name__ == "__main__":
    sys.exit(main())
