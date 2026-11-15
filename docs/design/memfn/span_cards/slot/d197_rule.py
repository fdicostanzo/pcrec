# span_cards/slot/d197_rule.py — D197's decision for the mfcard window, ONE VERDICT PER ISA LEVEL, by the DECLARED
# table d197_rule.tsv (review 2026-11-15 r5 FIDELITY-4 + the kit manager's R1; written before any number exists;
# the table is the rule, this file its reader).
#   python3 -I d197_rule.py rule RUNDIR AVX2RUNDIR [--second]
#                       the per-level verdicts from the two finalized records: RUNDIR timed with glibc's memchr
#                       as shipped, AVX2RUNDIR under the AVX2 tunable (each its own record; record.py's `libc`
#                       names the variant bound); --second: this is the ONE allowed re-run
#   python3 -I d197_rule.py drill [SCRATCH]
#                       the rule on CONSTRUCTED outcomes (no rundir): each case's expected per-level verdicts,
#                       `== d197 DRILL ok` iff all agree; SCRATCH: also end to end on est.py's synthetic window
# Prints one line per deciding cell and arm (the scan cost beside it), then `d197_verdict LEVEL FORM RESULT (when)
# -> trigger` per level. Exit 0 on verdicts, 2 on a refused input.
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
    "memchr-variant-not-the-arms": lambda a: a["variant"] is None
                                             or a["want_variant"] != "any" and a["variant"] != a["want_variant"],
    "any-cell-loss": lambda a: a["n"]["loss"] > 0,
    "wins-over-half-of-deciding-cells": lambda a: 2 * a["n"]["win"] > a["n_cells"],
    "shipped-arm-no-verdict": lambda v: v["shipped"] == "no-verdict",
    "shipped-arm-loss": lambda v: v["shipped"] == "LOSS",
    "avx2-arm-loss": lambda v: v["avx2"] == "LOSS",
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

def arm(t, form, out, drift, outcome, run, want_variant):
    """(arm result, lines): one level's form against libc in one finalized record, through the cell and arm tables"""
    libc = t["deciding"]["libc_form"]
    var = next((w.split("=", 1)[1] for w in (run.get("libc") or "").split() if w.startswith("memchr=")), None)
    n, lines = {"win": 0, "loss": 0, "tie": 0, "unresolved": 0}, []
    for g, r in cells(t):
        a, b = row_x(out, drift, key(t, libc, g, r)), row_x(out, drift, key(t, form, g, r))
        c = {"a": a, "b": b}
        if a and b:
            c["gain_l"] = [a["x"][i] - b["x"][i] for i in range(len(a["x"]))]
            c.update(gain=med(c["gain_l"]), floor=a["aa"] + b["aa"])
        res, why = first(t, "cell", c)[:2]
        n[res] += 1
        lines.append("cell\tgap %d reject %d\t%s vs %s\t%s\tgain %s floor %s\t(%s)" % (
            g, r, form, libc, res, c.get("gain", "-"), c.get("floor", "-"), why))
    scan = []
    for f in (form, libc):                     # the scan cost, REPORTED beside, never deciding
        s = row_x(out, drift, "kit.%s.%s" % (t["deciding"]["scan"], f))
        scan.append("%s %s" % (f, s["value"] if s and "value" in s else "-"))
    av = {"outcome": outcome, "variant": var, "want_variant": want_variant, "n": n, "n_cells": len(cells(t))}
    res, why = first(t, "arm", av)[:2]
    lines.append("arm\t%s vs %s (memchr=%s)\t%s\t%s\t(%s)\tscan (%s, not deciding): %s" % (
        form, libc, var, res, " ".join("%s %d" % kv for kv in sorted(n.items())), why, t["deciding"]["scan"],
        ", ".join(scan)))
    return res, lines

def verdict(t, shipped, avx2, second=False):
    """the verdict row (result, when, trigger) of one level from its two arms"""
    return first(t, "verdict", {"shipped": shipped, "avx2": avx2, "second": second})

def levels(t, arms_of, second=False):
    """{level: (result, when, trigger, lines)}; arms_of(form, "shipped"|"avx2") -> (arm result, lines)"""
    out = {}
    for lvl, _build, form, _axes in t["levels"]:
        r1, l1 = arms_of(form, "shipped")
        r2, l2 = arms_of(form, "avx2")
        out[lvl] = tuple(verdict(t, r1, r2, second)) + (["shipped\t" + x for x in l1] + ["avx2\t" + x for x in l2],)
    return out

def rule(rundir, avx2dir, second=False):
    t = load()
    recs = {}
    for name, d in (("shipped", rundir), ("avx2", avx2dir)):
        o, drift, _ub, outcome, _w, _p = compute(d)
        recs[name] = (o, drift, outcome[0], read_record(d)["run"])
    def arms_of(form, which):
        o, drift, outcome, run = recs[which]
        return arm(t, form, o, drift, outcome, run, "any" if which == "shipped" else "avx2")
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
    W, Lo, T = "WIN", "LOSS", "INCONCLUSIVE"
    mixed = {"mfind-swar": L7(1500), "mfind-w16": L7(990), "mfind-w32": L7(500)}
    CASES = (   # (name, shipped (out, outcome, variant), avx2 (out, outcome, variant), second, {level: expected})
        ("clean win at every level, both libc rows", (_rec(t, L7(1000), allf(500)), "FULL", "evex"),
         (_rec(t, L7(1000), allf(500)), "FULL", "avx2"), False, each(W)),
        ("clean loss at every level", (_rec(t, L7(1000), allf(1500)), "FULL", "evex"),
         (_rec(t, L7(1000), allf(1500)), "FULL", "avx2"), False, each(Lo)),
        ("per level: swar loses, w16 ties, w32 wins: three verdicts, never one",
         (_rec(t, L7(1000), mixed), "FULL", "evex"), (_rec(t, L7(1000), mixed), "FULL", "avx2"), False,
         dict(zip(lv, (Lo, T, W)))),
        ("within-floor tie (gain 30, floor 40): INCONCLUSIVE, the one re-run",
         (_rec(t, L7(1000), allf(970)), "FULL", "evex"), (_rec(t, L7(1000), allf(970)), "FULL", "avx2"), False, each(T)),
        ("the same tie on the re-run (--second): LOSS",
         (_rec(t, L7(1000), allf(970)), "FULL", "evex"), (_rec(t, L7(1000), allf(970)), "FULL", "avx2"), True, each(Lo)),
        ("a clean win on the re-run stays WIN",
         (_rec(t, L7(1000), allf(500)), "FULL", "evex"), (_rec(t, L7(1000), allf(500)), "FULL", "avx2"), True, each(W)),
        ("clean win, one outlier launch (launch 3's cost x10) trimmed away",
         (_rec(t, L7(1000), {f: [500, 500, 5000, 500, 500, 500, 500] for f in F}), "FULL", "evex"),
         (_rec(t, L7(1000), allf(500)), "FULL", "avx2"), False, each(W)),
        ("two outlier launches: a trimmed launch negative, no cell wins: INCONCLUSIVE",
         (_rec(t, L7(1000), {f: [500, 500, 5000, 5000, 500, 500, 500] for f in F}), "FULL", "evex"),
         (_rec(t, L7(1000), allf(500)), "FULL", "avx2"), False, each(T)),
        ("wins vs the shipped evex memchr, loses to the AVX2 memchr: LOSS",
         (_rec(t, L7(1000), allf(500)), "FULL", "evex"), (_rec(t, L7(400), allf(500)), "FULL", "avx2"), False, each(Lo)),
        ("loses to the shipped memchr, wins vs AVX2: LOSS",
         (_rec(t, L7(500), allf(1000)), "FULL", "evex"), (_rec(t, L7(1000), allf(500)), "FULL", "avx2"), False, each(Lo)),
        ("wins vs shipped, ties the AVX2 memchr: INCONCLUSIVE",
         (_rec(t, L7(1000), allf(500)), "FULL", "evex"), (_rec(t, L7(510), allf(500)), "FULL", "avx2"), False, each(T)),
        ("the AVX2 record bound the EVEX memchr (the tunable did nothing): INCONCLUSIVE",
         (_rec(t, L7(1000), allf(500)), "FULL", "evex"), (_rec(t, L7(1000), allf(500)), "FULL", "evex"), False, each(T)),
        ("wins on the hit-dense gaps (<= 64: 12 of 18 cells), ties above: WIN",
         (_rec(t, L7(1000), allf(990), per_cell=dense(64)), "FULL", "evex"),
         (_rec(t, L7(1000), allf(990), per_cell=dense(64)), "FULL", "avx2"), False, each(W)),
        ("all win on the dense gaps, w32 one clean loss at gap 65536: v3 LOSS, the others WIN",
         (_rec(t, L7(1000), allf(990), per_cell={**dense(64), ("mfind-w32", 65536, 0): L7(1500)}), "FULL", "evex"),
         (_rec(t, L7(1000), allf(500)), "FULL", "avx2"), False, dict(zip(lv, (W, W, Lo)))),
        ("wins on 6 of 18 cells only (gaps <= 8), ties elsewhere: INCONCLUSIVE",
         (_rec(t, L7(1000), allf(990), per_cell=dense(8)), "FULL", "evex"), (_rec(t, L7(1000), allf(500)), "FULL", "avx2"),
         False, each(T)),
        ("the shipped record's run REFUSED: INCONCLUSIVE", ({}, "REFUSED", "evex"),
         (_rec(t, L7(1000), allf(500)), "FULL", "avx2"), False, each(T)),
        ("deciding rows absent on 10 of 18 cells (gaps >= 32), the rest wins: INCONCLUSIVE",
         ({k: v for k, v in _rec(t, L7(1000), allf(500)).items() if int(k.split(".")[-2]) < 32}, "PARTIAL", "evex"),
         (_rec(t, L7(1000), allf(500)), "FULL", "avx2"), False, each(T)),
    )
    bad = 0
    for name, sa, aa, second, want in CASES:
        recs = {"shipped": sa, "avx2": aa}
        def arms_of(form, which, recs=recs):
            o, outcome, var = recs[which]
            return arm(t, form, o, {}, outcome, run(var), "any" if which == "shipped" else "avx2")
        got = {l: v[0] for l, v in levels(t, arms_of, second).items()}
        ok = got == want
        bad += not ok
        print("drill\t%s\t%s\t%s" % (name, "ok" if ok else "WRONG", ", ".join("%s %s" % (l, got[l]) for l in lv)))
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
        ok = list(v) == lv and nc == want_n
        bad += not ok
        n += 1
        print("drill\tend to end on est's synthetic window\t%s\t%d of %d cells read, %s" % (
            "ok" if ok else "WRONG", nc, want_n, ", ".join("%s %s" % (l, v[l][0]) for l in lv)))
    print("== d197 DRILL %s: %d cases, %d wrong" % ("ok" if not bad else "FAILED", n, bad))
    return 1 if bad else 0

def main():
    if sys.argv[1] == "drill":
        return drill(sys.argv[2] if len(sys.argv) > 2 else None)
    try:
        v = rule(sys.argv[2], sys.argv[3], "--second" in sys.argv[4:])
    except InputError as e:
        print("d197: REFUSED input: %s" % e)
        return 2
    for lvl, _b, form, _axes in load()["levels"]:
        res, when, trig, lines = v[lvl]
        for ln in lines:
            print("%s\t%s" % (lvl, ln))
        print("d197_verdict\t%s\t%s\t%s\t(%s) -> %s" % (lvl, form, res, when, trig))
    return 0

if __name__ == "__main__":
    sys.exit(main())
