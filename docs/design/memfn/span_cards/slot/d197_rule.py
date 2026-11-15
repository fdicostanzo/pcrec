# span_cards/slot/d197_rule.py — D197's decision for the mfcard window, ONE VERDICT PER ISA LEVEL, by the DECLARED
# table d197_rule.tsv (review 2026-11-15 r5 FIDELITY-4 + the kit manager's R1; written before any number exists;
# the table is the rule, this file its reader).
#   python3 -I d197_rule.py rule RUNDIR AVX2RUNDIR [--second] [--confirm CRUNDIR CAVX2RUNDIR]
#                       the per-level verdicts from the two finalized records: RUNDIR timed with glibc's memchr
#                       as shipped, AVX2RUNDIR under the AVX2 tunable (each its own record; record.py's `libc`
#                       names the variant bound); --second: this is the ONE allowed re-run; --confirm: the
#                       confirming re-run's two records (window mfconfirm) for a loss on one or two cells
#   python3 -I d197_rule.py drill [SCRATCH]
#                       the rule on CONSTRUCTED outcomes (no rundir): each case's expected per-level verdicts,
#                       `== d197 DRILL ok` iff all agree; SCRATCH: also end to end on est.py's synthetic window
# Prints one line per deciding cell and arm, then per level `d197_scan` (find_byte@6 form/libc, never deciding) and
# `d197_verdict LEVEL FORM RESULT (when) -> trigger`; a CONFIRM names its cells (`d197_confirm_cells GAP.REJECT..`,
# the SLOT_CONFIRM_CELLS value of job 610). Exit 0 on verdicts, 2 on a refused input.
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
    "loss-not-reproduced": lambda c: c["gain"] < -c["floor"] and c["conf"] is not None
                                     and not c["conf"]["gain"] < -c["conf"]["floor"],
    "run-refused": lambda a: a["outcome"] == "REFUSED",
    "memchr-variant-not-the-arms": lambda a: a["variant"] is None
                                             or a["want_variant"] != "any" and a["variant"] != a["want_variant"],
    "no-loss-and-wins-over-half-of-deciding-cells": lambda a: a["n"]["loss"] == 0 and 2 * a["n"]["win"] > a["n_cells"],
    "shipped-arm-no-verdict": lambda v: v["shipped"] == "no-verdict",
    "three-or-more-loss-cells": lambda v: len(v["losses"]) >= 3,
    "loss-cells-awaiting-confirmation": lambda v: any(not confirmed for _c, confirmed in v["losses"]),
    "reproduced-loss-cells": lambda v: len(v["losses"]) > 0,
    "both-arms-win": lambda v: v["shipped"] == "WIN" and v["avx2"] == "WIN",
    "second-run": lambda v: v["second"],
    "always": lambda _x: True,
}

def first(t, table, x):
    for row in t[table]:
        if WHEN[row[1]](x):
            return row
    raise InputError("d197_rule.tsv: table %s has no row for %r" % (table, x))

def row_x(out, drift, k):
    """the row's per-launch x and A/A, or None (absent, drifted, or no W)"""
    r = out.get(k)
    if not r or "absent" in r or "x" not in r or drift.get(r["job"], (0, 0, False))[2]:
        return None
    return r

def variant_of(run):
    return next((w.split("=", 1)[1] for w in (run.get("libc") or "").split() if w.startswith("memchr=")), None)

def gain(t, form, out, drift, g, r):
    """{gain_l, gain, floor} of one cell (form vs libc) in one record, or None (a row unpriced)"""
    a, b = row_x(out, drift, key(t, t["deciding"]["libc_form"], g, r)), row_x(out, drift, key(t, form, g, r))
    if not (a and b):
        return None
    gl = [a["x"][i] - b["x"][i] for i in range(len(a["x"]))]
    return {"gain_l": gl, "gain": med(gl), "floor": a["aa"] + b["aa"]}

def arm(t, form, out, drift, outcome, run, want_variant, conf=None):
    """(arm result, loss cells [((gap, reject), confirmed)], scan, lines): one level's form against libc in one
    finalized record, through the cell and arm tables; conf (out, drift) is the confirming record of this arm"""
    libc = t["deciding"]["libc_form"]
    var = variant_of(run)
    n, losses, lines = {"win": 0, "loss": 0, "tie": 0, "unresolved": 0}, [], []
    for g, r in cells(t):
        gc = gain(t, form, out, drift, g, r)
        c = dict(gc or {}, a=gc, b=gc, conf=gain(t, form, conf[0], conf[1], g, r) if conf else None)
        res, why = first(t, "cell", c)[:2]
        n[res] += 1
        if res == "loss":
            losses.append(((g, r), c["conf"] is not None))
        lines.append("cell\tgap %d reject %d\t%s vs %s\t%s\tgain %s floor %s%s\t(%s)" % (
            g, r, form, libc, res, c.get("gain", "-"), c.get("floor", "-"),
            "" if c["conf"] is None else " confirming gain %s floor %s" % (c["conf"]["gain"], c["conf"]["floor"]), why))
    sc = [row_x(out, drift, "kit.%s.%s" % (t["deciding"]["scan"], f)) for f in (form, libc)]
    sv = [s["value"] if s and "value" in s else None for s in sc]
    scan = "%s %s, %s %s, ratio %s" % (form, "-" if sv[0] is None else sv[0], libc, "-" if sv[1] is None else sv[1],
                                       "%.2f" % (sv[0] / sv[1]) if sv[0] is not None and sv[1] else "-")
    av = {"outcome": outcome, "variant": var, "want_variant": want_variant, "n": n, "n_cells": len(cells(t))}
    res, why = first(t, "arm", av)[:2]
    lines.append("arm\t%s vs %s (memchr=%s)\t%s\t%s\t(%s)" % (
        form, libc, var, res, " ".join("%s %d" % kv for kv in sorted(n.items())), why))
    return res, ([] if res == "no-verdict" else losses), scan, lines

def levels(t, arms_of, second=False):
    """{level: (result, when, trigger, lines, scan, confirm cells)}; arms_of(form, "shipped"|"avx2") -> arm()'s
    tuple. The losses count over BOTH libc rows (the level's 36 comparisons); an arm without a verdict counts none"""
    out = {}
    for lvl, _build, form, _axes in t["levels"]:
        r1, x1, s1, l1 = arms_of(form, "shipped")
        r2, x2, s2, l2 = arms_of(form, "avx2")
        v = {"shipped": r1, "avx2": r2, "second": second, "losses": x1 + x2}
        res, when, trig = first(t, "verdict", v)
        cc = sorted({c for c, confirmed in x1 + x2 if not confirmed}) if res == "CONFIRM" else []
        out[lvl] = (res, when, trig, ["shipped\t" + x for x in l1] + ["avx2\t" + x for x in l2],
                    "shipped: %s; avx2: %s" % (s1, s2), cc)
    return out

def rule(rundir, avx2dir, second=False, confirm=None):
    t = load()
    recs, conf = {}, {}
    for name, d in (("shipped", rundir), ("avx2", avx2dir)):
        o, drift, _ub, outcome, _w, _p = compute(d)
        recs[name] = (o, drift, outcome[0], read_record(d)["run"])
    for name, d in zip(("shipped", "avx2"), confirm or ()):
        o, drift, _ub, outcome, _w, _p = compute(d)
        var = variant_of(read_record(d)["run"])
        if outcome[0] != "REFUSED" and var is not None and (name == "shipped" or var == "avx2"):
            conf[name] = (o, drift)      # a refused or mis-bound confirming record confirms nothing
    def arms_of(form, which):
        o, drift, outcome, run = recs[which]
        return arm(t, form, o, drift, outcome, run, "any" if which == "shipped" else "avx2", conf.get(which))
    return levels(t, arms_of, second)

# ---- the drill: CONSTRUCTED outcomes, each with the per-level verdicts the rule must give -----------------------
def _forms(t):
    return [form for _l, _b, form, _a in t["levels"]]

def _rec(t, libc_x, form_x, aa=20, per_cell=None):
    """a constructed est `out` for one record: every deciding cell's libc row and each level form's row, 7 launch
    values; form_x {form: x list} (default libc_x), per_cell {(form, gap, reject): x list}"""
    out = {}
    for g, r in cells(t):
        out[key(t, t["deciding"]["libc_form"], g, r)] = {"job": "JMH", "x": list(libc_x), "aa": aa}
        for f in _forms(t):
            x = (per_cell or {}).get((f, g, r), form_x.get(f, libc_x))
            out[key(t, f, g, r)] = {"job": "JMH", "x": list(x), "aa": aa}
    return out

def drill(scratch=None):
    t = load()
    F = _forms(t)
    lv = [l for l, _b, _f, _a in t["levels"]]
    L7 = lambda v: [v] * 7
    run = lambda var: {"isa": "x86-64-v4 avx512f avx2", "libc": "glibc 2.43 memchr=%s" % var}
    allf = lambda v: {f: L7(v) for f in F}
    each = lambda v: dict.fromkeys(lv, v)
    dense = lambda gmax: {(f, g, r): L7(500) for f in F for g, r in cells(t) if g <= gmax}
    W, Lo, T, C, NW = "WIN", "LOSS", "INCONCLUSIVE", "CONFIRM", "NOT-WIN"
    mixed = {"mfind-swar": L7(1500), "mfind-w16": L7(990), "mfind-w32": L7(500)}
    one_loss = {**dense(64), ("mfind-w32", 65536, 0): L7(1500)}          # w32: 12 wins, one loss (gap 65536)
    three = {**dense(64), **{("mfind-w32", g, r): L7(1500) for g, r in ((65536, 0), (65536, 100), (1024, 0))}}
    v3 = lambda x: dict(zip(lv, (W, W, x)))
    good = lambda: (_rec(t, L7(1000), allf(500)), "FULL", "avx2")
    CASES = (   # (name, shipped (out, outcome, variant), avx2 (out, outcome, variant), second, {level: expected},
                #  confirming outs {arm: out} or None)
        ("clean win at every level, both libc rows", (_rec(t, L7(1000), allf(500)), "FULL", "evex"), good(), False,
         each(W), None),
        ("clean loss at every level (18 cells: at once)", (_rec(t, L7(1000), allf(1500)), "FULL", "evex"),
         (_rec(t, L7(1000), allf(1500)), "FULL", "avx2"), False, each(Lo), None),
        ("per level: swar loses, w16 ties, w32 wins: three verdicts, never one",
         (_rec(t, L7(1000), mixed), "FULL", "evex"), (_rec(t, L7(1000), mixed), "FULL", "avx2"), False,
         dict(zip(lv, (Lo, T, W))), None),
        ("within-floor tie (gain 30, floor 40): INCONCLUSIVE, the one re-run",
         (_rec(t, L7(1000), allf(970)), "FULL", "evex"), (_rec(t, L7(1000), allf(970)), "FULL", "avx2"), False,
         each(T), None),
        ("the same tie on the re-run (--second): NOT-WIN, never LOSS",
         (_rec(t, L7(1000), allf(970)), "FULL", "evex"), (_rec(t, L7(1000), allf(970)), "FULL", "avx2"), True,
         each(NW), None),
        ("a clean win on the re-run stays WIN", (_rec(t, L7(1000), allf(500)), "FULL", "evex"), good(), True,
         each(W), None),
        ("clean win, one outlier launch (launch 3's cost x10) trimmed away",
         (_rec(t, L7(1000), {f: [500, 500, 5000, 500, 500, 500, 500] for f in F}), "FULL", "evex"), good(), False,
         each(W), None),
        ("two outlier launches: a trimmed launch negative, no cell wins: INCONCLUSIVE",
         (_rec(t, L7(1000), {f: [500, 500, 5000, 5000, 500, 500, 500] for f in F}), "FULL", "evex"), good(), False,
         each(T), None),
        ("wins vs the shipped evex memchr, loses to the AVX2 memchr on every cell: LOSS",
         (_rec(t, L7(1000), allf(500)), "FULL", "evex"), (_rec(t, L7(400), allf(500)), "FULL", "avx2"), False,
         each(Lo), None),
        ("loses to the shipped memchr on every cell, wins vs AVX2: LOSS",
         (_rec(t, L7(500), allf(1000)), "FULL", "evex"), good(), False, each(Lo), None),
        ("wins vs shipped, ties the AVX2 memchr: INCONCLUSIVE",
         (_rec(t, L7(1000), allf(500)), "FULL", "evex"), (_rec(t, L7(510), allf(500)), "FULL", "avx2"), False,
         each(T), None),
        ("the AVX2 record bound the EVEX memchr (the tunable did nothing): INCONCLUSIVE",
         (_rec(t, L7(1000), allf(500)), "FULL", "evex"), (_rec(t, L7(1000), allf(500)), "FULL", "evex"), False,
         each(T), None),
        ("wins on the hit-dense gaps (<= 64: 12 of 18 cells), ties above: WIN",
         (_rec(t, L7(1000), allf(990), per_cell=dense(64)), "FULL", "evex"),
         (_rec(t, L7(1000), allf(990), per_cell=dense(64)), "FULL", "avx2"), False, each(W), None),
        ("[R3] w32 loses ONE cell (gap 65536), no confirming run yet: v3 CONFIRM",
         (_rec(t, L7(1000), allf(990), per_cell=one_loss), "FULL", "evex"), good(), False, v3(C), None),
        ("[R3] that one-cell loss REPRODUCES in the confirming run: v3 LOSS",
         (_rec(t, L7(1000), allf(990), per_cell=one_loss), "FULL", "evex"), good(), False, v3(Lo),
         {"shipped": _rec(t, L7(1000), allf(990), per_cell=one_loss), "avx2": _rec(t, L7(1000), allf(500))}),
        ("[R3] that one-cell loss does NOT reproduce (the confirming cell ties): scored tie, v3 WIN",
         (_rec(t, L7(1000), allf(990), per_cell=one_loss), "FULL", "evex"), good(), False, v3(W),
         {"shipped": _rec(t, L7(1000), allf(990)), "avx2": _rec(t, L7(1000), allf(500))}),
        ("[R3] w32 loses THREE cells: v3 LOSS at once, no confirming run",
         (_rec(t, L7(1000), allf(990), per_cell=three), "FULL", "evex"), good(), False, v3(Lo), None),
        ("[R3] one loss vs each libc row (two of the 36 comparisons): v3 CONFIRM",
         (_rec(t, L7(1000), allf(990), per_cell=one_loss), "FULL", "evex"),
         (_rec(t, L7(1000), allf(500), per_cell={("mfind-w32", 2, 100): L7(1500)}), "FULL", "avx2"), False, v3(C),
         None),
        ("wins on 6 of 18 cells only (gaps <= 8), ties elsewhere: INCONCLUSIVE",
         (_rec(t, L7(1000), allf(990), per_cell=dense(8)), "FULL", "evex"), good(), False, each(T), None),
        ("the shipped record's run REFUSED: INCONCLUSIVE", ({}, "REFUSED", "evex"), good(), False, each(T), None),
        ("deciding rows absent on 10 of 18 cells (gaps >= 32), the rest wins: INCONCLUSIVE",
         ({k: v for k, v in _rec(t, L7(1000), allf(500)).items() if int(k.split(".")[-2]) < 32}, "PARTIAL", "evex"),
         good(), False, each(T), None),
    )
    bad = 0
    for name, sa, aa, second, want, conf in CASES:
        recs = {"shipped": sa, "avx2": aa}
        def arms_of(form, which, recs=recs, conf=conf):
            o, outcome, var = recs[which]
            return arm(t, form, o, {}, outcome, run(var), "any" if which == "shipped" else "avx2",
                       (conf[which], {}) if conf else None)
        v = levels(t, arms_of, second)
        got = {l: x[0] for l, x in v.items()}
        ok = got == want
        bad += not ok
        print("drill\t%s\t%s\t%s" % (name, "ok" if ok else "WRONG", ", ".join(
            "%s %s%s" % (l, got[l], " (%s)" % " ".join("%d.%d" % c for c in v[l][5]) if v[l][5] else "") for l in lv)))
    n = len(CASES)
    if scratch:
        # END TO END: the reader on est.py's own synthetic finalized mfcard window (compute's real row keys and
        # fields), both records: a verdict per level, every deciding cell read (none unresolved), no refusal
        import est
        for var, sub in (("evex", "shipped"), ("avx2", "avx2")):
            d = est._synth(os.path.join(scratch, "d197_" + sub), window="mfcard")
            rr = os.path.join(d, "run_record.tsv")
            txt = open(rr).read().replace("run_id\tselftest\n", "run_id\tselftest\nisa\tx86-64-v4 avx2\n"
                                          "libc\tglibc 2.43 memchr=%s\n" % var, 1)
            open(rr, "w").write(txt)
        v = rule(os.path.join(scratch, "d197_shipped"), os.path.join(scratch, "d197_avx2"))
        want_n = 2 * len(lv) * len(cells(t))
        nc = sum(1 for x in v.values() for ln in x[3] if "\tcell\t" in ln and "unresolved" not in ln)
        ok = list(v) == lv and nc == want_n and all("ratio" in x[4] for x in v.values())
        bad += not ok
        n += 1
        print("drill\tend to end on est's synthetic window\t%s\t%d of %d cells read, %s" % (
            "ok" if ok else "WRONG", nc, want_n, ", ".join("%s %s" % (l, v[l][0]) for l in lv)))
    print("== d197 DRILL %s: %d cases, %d wrong" % ("ok" if not bad else "FAILED", n, bad))
    return 1 if bad else 0

def main():
    if sys.argv[1] == "drill":
        return drill(sys.argv[2] if len(sys.argv) > 2 else None)
    a = sys.argv[4:]
    try:
        conf = a[a.index("--confirm") + 1:a.index("--confirm") + 3] if "--confirm" in a else None
        if conf is not None and len(conf) != 2:
            raise InputError("--confirm takes two rundirs (shipped, avx2)")
        v = rule(sys.argv[2], sys.argv[3], "--second" in a, conf)
    except InputError as e:
        print("d197: REFUSED input: %s" % e)
        return 2
    cc = set()
    for lvl, _b, form, _axes in load()["levels"]:
        res, when, trig, lines, scan, cells_ = v[lvl]
        for ln in lines:
            print("%s\t%s" % (lvl, ln))
        print("d197_scan\t%s\tfind_byte@6 (miss-only per byte, NOT deciding): %s" % (lvl, scan))
        print("d197_verdict\t%s\t%s\t%s\t(%s) -> %s" % (lvl, form, res, when, trig))
        cc.update(cells_)
    if cc:
        print("d197_confirm_cells\t%s" % " ".join("%d.%d" % c for c in sorted(cc)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
