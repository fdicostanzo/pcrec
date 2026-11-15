# span_cards/slot/d197_rule.py — D197's decision for the mfcard window, ONE VERDICT PER ISA LEVEL, by the DECLARED
# table d197_rule.tsv (review 2026-11-15 r5 FIDELITY-4 + the kit manager's R1; written before any number exists;
# the table is the rule, this file its reader).
#   python3 -I d197_rule.py rule RUNDIR AVX2RUNDIR [--second FIRST FIRSTAVX2] [--confirm CRUNDIR CAVX2RUNDIR]
#                       the per-level verdicts from the two finalized records: RUNDIR timed with glibc's memchr
#                       as shipped, AVX2RUNDIR under the AVX2 tunable (each its own record; record.py's `libc`
#                       names the variant bound); --second: this is the ONE allowed re-run, FIRST/FIRSTAVX2 the
#                       first run's two records (review r6 RULE-6: second-ness is derived from them); --confirm:
#                       the confirming re-run's two records (window mfconfirm) for a loss on one or two comparisons.
#                       Every record must pin this file and the table (record.py `window`, r6 RULE-3) and the
#                       records must be one experiment (`provenance`, r6 RULE-2), else REFUSED
#   python3 -I d197_rule.py drill [SCRATCH]
#                       the rule on CONSTRUCTED outcomes (no rundir): each case's expected per-level verdicts,
#                       `== d197 DRILL ok` iff all agree; SCRATCH: also end to end on est.py's synthetic window
# Prints one line per deciding cell and arm, then per level `d197_scan` (find_byte@6 form/libc, never deciding) and
# `d197_verdict LEVEL FORM RESULT (when) -> trigger`; a CONFIRM names its cells (`d197_confirm_cells GAP.REJECT..`,
# the SLOT_CONFIRM_CELLS value of job 610). Exit 0 on verdicts, 2 on a refused input.
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from est import med, trim, compute, read_record, cell_texts, InputError  # noqa: E402  (the estimator's primitives, ONE home)
import record  # noqa: E402  (rule_pins: the record's pin of this rule, ONE home)

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
    t["libc_variant"] = dict(t["libc_variant"])
    return t

def cells(t):
    d = t["deciding"]
    return [(int(g), int(r)) for g in d["gaps"].split(",") for r in d["rejects"].split(",")]

def key(t, form, g, r):
    d = t["deciding"]
    return "kit.%s.%s.%s.%s.%d.%d" % (d["quantity"], form, d["landing"], d["split"], g, r)

# THE NAMED PREDICATES (the table's `when` words), one line each
WHEN = {
    "either-row-unpriced": lambda c: c["priced"] is None,      # gain(): None when either row is (the TSV's UNPRICED)
    "gain-beyond-floor-and-every-trimmed-launch-positive":
        lambda c: c["gain"] > c["floor"] and all(x > 0 for x in trim(c["gain_l"])),
    "gain-below-minus-floor": lambda c: c["gain"] < -c["floor"],
    "loss-not-reproduced": lambda c: c["gain"] < -c["floor"] and c["conf"] is not None
                                     and not c["conf"]["gain"] < -c["conf"]["floor"],
    "run-refused": lambda a: a["outcome"] == "REFUSED",
    # the AVX2 arm bound memchr's avx2 variant; [r6 FIDELITY-2] the shipped arm ran WITHOUT a tunable and bound
    # something other than the AVX2 arm's variant
    "memchr-variant-not-the-arms": lambda a: a["variant"] is None
                                             or a["which"] == "avx2" and a["variant"] != AVX2_VARIANT
                                             or a["which"] == "shipped" and (a["tunables"] or a["variant"] == AVX2_VARIANT),
    "no-loss-and-wins-over-half-of-deciding-comparisons":
        lambda a: a["n"]["loss"] == 0 and 2 * a["n"]["win"] > a["n_cells"],
    "second-run-without-a-verdict": lambda v: v["second"] and (WHEN["shipped-arm-no-verdict"](v)
                                                                 or WHEN["confirmation-refused-or-absent"](v)),
    "shipped-arm-no-verdict": lambda v: v["shipped"] == "no-verdict",
    "three-or-more-loss-comparisons": lambda v: len(v["losses"]) >= 3,
    "confirmation-refused-or-absent": lambda v: v["confirming"] and len(v["losses"]) < 3
                                                and any(not confirmed for _c, confirmed in v["losses"]),
    "loss-comparisons-awaiting-confirmation": lambda v: any(not confirmed for _c, confirmed in v["losses"]),
    "reproduced-loss-comparisons": lambda v: len(v["losses"]) > 0,
    "both-arms-win": lambda v: v["shipped"] == "WIN" and v["avx2"] == "WIN",
    "second-run": lambda v: v["second"],
    "always": lambda _x: True,
}

AVX2_VARIANT = "avx2"      # the AVX2 arm's variant (record.py memchr_variant's word for a VEX memchr)

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

def tunables_of(run):
    return any(w.startswith("GLIBC_TUNABLES=") for w in (run.get("libc") or "").split())

def gain(t, form, out, drift, g, r):
    """{gain_l, gain, floor} of one cell (form vs libc) in one record, or None (a row unpriced)"""
    a, b = row_x(out, drift, key(t, t["deciding"]["libc_form"], g, r)), row_x(out, drift, key(t, form, g, r))
    if not (a and b):
        return None
    gl = [a["x"][i] - b["x"][i] for i in range(len(a["x"]))]
    return {"gain_l": gl, "gain": med(gl), "floor": a["aa"] + b["aa"]}

def arm(t, form, out, drift, outcome, run, which, conf=None):
    """(arm result, loss comparisons [((gap, reject), confirmed)], scan, lines): one level's form against libc in
    one finalized record (`which`: shipped or avx2), through the cell and arm tables; conf (out, drift) is the
    confirming record of this arm"""
    libc = t["deciding"]["libc_form"]
    var = variant_of(run)
    n, losses, lines = {"win": 0, "loss": 0, "tie": 0, "unresolved": 0}, [], []
    for g, r in cells(t):
        gc = gain(t, form, out, drift, g, r)
        c = dict(gc or {}, priced=gc, conf=gain(t, form, conf[0], conf[1], g, r) if conf else None)
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
    av = {"outcome": outcome, "variant": var, "which": which, "tunables": tunables_of(run), "n": n,
          "n_cells": len(cells(t))}
    res, why = first(t, "arm", av)[:2]
    # [r6 RULE-8(b)] libc's vector printed from the variant the RECORD names, never asserted by the levels' axes
    lines.append("arm\t%s vs %s (memchr=%s: %s)\t%s\t%s\t(%s)" % (
        form, libc, var, t["libc_variant"].get(var, "a variant the table does not name"), res,
        " ".join("%s %d" % kv for kv in sorted(n.items())), why))
    return res, ([] if res == "no-verdict" else losses), scan, lines

def levels(t, arms_of, second=False, confirming=False):
    """{level: (result, when, trigger, lines, scan, confirm cells)}; arms_of(form, "shipped"|"avx2") -> arm()'s
    tuple. The losses count over BOTH libc rows (the level's 36 comparisons); an arm without a verdict counts none.
    confirming: a confirming run's records were given (--confirm), usable or not"""
    out = {}
    for lvl, _build, form, _axes in t["levels"]:
        r1, x1, s1, l1 = arms_of(form, "shipped")
        r2, x2, s2, l2 = arms_of(form, "avx2")
        v = {"shipped": r1, "avx2": r2, "second": second, "confirming": confirming, "losses": x1 + x2}
        res, when, trig = first(t, "verdict", v)
        cc = sorted({c for c, confirmed in x1 + x2 if not confirmed}) if res == "CONFIRM" else []
        out[lvl] = (res, when, trig, ["shipped\t" + x for x in l1] + ["avx2\t" + x for x in l2],
                    "shipped: %s; avx2: %s" % (s1, s2), cc)
    return out

def bound_right(which, run):
    """the arm table's variant row, asked of a record alone (a confirming record's arm)"""
    return not WHEN["memchr-variant-not-the-arms"]({"variant": variant_of(run), "which": which,
                                                     "tunables": tunables_of(run)})

def meta(t, d):
    """[r6 RULE-2] one finalized record's scores and PROVENANCE facts: run keys, plan, the deciding forms' kit fold
    hashes (est.cell_texts: the texts link.py timed), and the find_hit cells its plan moved to JMHC"""
    o, drift, _ub, outcome, _w, _p = compute(d)
    rec = read_record(d)
    forms = {t["deciding"]["libc_form"]} | set(_forms(t))
    folds = {x[0]: x[1] for x in cell_texts(d, rec).values() if x[0] in forms}   # one fold per form: est refuses two
    q = "kit.%s." % t["deciding"]["quantity"]
    return {"dir": d, "out": o, "drift": drift, "outcome": outcome[0], "run": rec["run"], "plan": sorted(rec["plan"]),
            "folds": folds,
            "confirm_cells": {tuple(int(v) for v in k.split(".")[-2:]) for k, _g, j in rec["plan"]
                              if j == "JMHC" and k.startswith(q)}}

# [r6 RULE-2, RULE-3, RULE-6] THE RECORDS ARE ONE EXPERIMENT. roles: shipped, avx2 (this run), first.shipped,
# first.avx2 (--second: the first run's), confirm.shipped, confirm.avx2 (--confirm). Each line: what every role's
# record must hold; a failure REFUSES the input (no verdict, exit 2), never scores a row
WINDOW_OF = {"shipped": "mfcard", "avx2": "mfcard", "first": "mfcard", "confirm": "mfconfirm"}

def plan_of(m, role):
    """the plan facts compared across records: the whole frozen plan, except that a confirming run's plan moved its
    cells to JMHC (plan.py CONFIRM_CELLS): its kit keys and the cards and policy it was planned under"""
    if role.startswith("confirm"):
        return (sorted(k for k, _g, _j in m["plan"] if k.startswith("kit.")),
                m["run"].get("cards_sha256"), m["run"].get("policy_sha256"))
    return (m["plan"], m["run"].get("cards_sha256"), m["run"].get("policy_sha256"))

def provenance(pins, recs):
    base = recs["shipped"]
    for role, m in sorted(recs.items()):
        r = m["run"]
        for k, v in sorted(pins.items()):
            if r.get(k) != v:
                raise InputError("RULE PIN %s (%s): the record pins %s %s, the rule run is %s: the rule read is not "
                                 "the one declared before this record's numbers (review r6 RULE-3)"
                                 % (role, m["dir"], k, r.get(k), v))
        if r.get("window") != WINDOW_OF[role.split(".")[0]]:
            raise InputError("RECORD ROLE %s (%s): window %s, a %s record must be window %s (review r6 RULE-2)"
                             % (role, m["dir"], r.get("window"), role, WINDOW_OF[role.split(".")[0]]))
        if r.get("code_commit") != base["run"].get("code_commit"):
            raise InputError("ONE EXPERIMENT %s: code_commit %s, the shipped arm's %s (review r6 RULE-2)"
                             % (role, r.get("code_commit"), base["run"].get("code_commit")))
        if plan_of(m, role) != plan_of(base, role):
            raise InputError("ONE EXPERIMENT %s: its plan differs from the shipped arm's (review r6 RULE-2)" % role)
        moved = sorted(f for f in set(m["folds"]) & set(base["folds"]) if m["folds"][f] != base["folds"][f])
        if moved:
            raise InputError("ONE EXPERIMENT %s: the kit fold of %s differs from the shipped arm's (the kit moved "
                             "between the records; review r6 RULE-2)" % (role, ", ".join(moved)))
    this = {recs[n]["run"].get("run_id") for n in ("shipped", "avx2")}
    first = {m["run"].get("run_id") for role, m in recs.items() if role.startswith("first.")}
    if this & first:
        raise InputError("--second names the run's own run id %s as the first run's: a second run is another run "
                         "(review r6 RULE-2)" % ", ".join(sorted(this & first)))
    for role, m in sorted(recs.items()):
        if role.startswith("confirm.") and m["run"].get("run_id") in this | first:
            raise InputError("RECORD ROLE %s: run id %s is the confirmed run's own: a confirmation is another run "
                             "(review r6 RULE-2)" % (role, m["run"].get("run_id")))

def confirm_cells_check(want, recs):
    """[r6 RULE-2] each confirming record re-ran EXACTLY the CONFIRM verdict's cells (d197_confirm_cells)"""
    if not want:
        raise InputError("--confirm given, but no level's verdict without it is CONFIRM: nothing to confirm")
    for role, m in sorted(recs.items()):
        if role.startswith("confirm.") and sorted(m["confirm_cells"]) != sorted(want):
            raise InputError("RECORD ROLE %s: its JMHC cells %s, the CONFIRM's %s (review r6 RULE-2)" % (
                role, " ".join("%d.%d" % c for c in sorted(m["confirm_cells"])) or "none",
                " ".join("%d.%d" % c for c in sorted(want))))

def rule(rundir, avx2dir, second=None, confirm=None):
    """second: the first run's (shipped, avx2) rundirs; confirm: the confirming run's (shipped, avx2) rundirs"""
    t = load()
    roles = [("shipped", rundir), ("avx2", avx2dir)]
    roles += [("first." + n, d) for n, d in zip(("shipped", "avx2"), second or ())]
    roles += [("confirm." + n, d) for n, d in zip(("shipped", "avx2"), confirm or ())]
    recs = {role: meta(t, d) for role, d in roles}
    provenance(record.rule_pins(), recs)
    is_second = second is not None          # [r6 RULE-6] derived: the first run's records passed provenance
    def arms_of(conf):
        def f(form, which):
            m = recs[which]
            return arm(t, form, m["out"], m["drift"], m["outcome"], m["run"], which, conf.get(which))
        return f
    v = levels(t, arms_of({}), is_second)
    if confirm is None:
        return v
    confirm_cells_check({c for x in v.values() for c in x[5]}, recs)
    conf = {}
    for n in ("shipped", "avx2"):
        m = recs["confirm." + n]
        if m["outcome"] != "REFUSED" and bound_right(n, m["run"]):
            conf[n] = (m["out"], m["drift"])     # a refused or mis-bound confirming record confirms nothing
    return levels(t, arms_of(conf), is_second, confirming=True)

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
    TUN = "avx2 GLIBC_TUNABLES=glibc.cpu.hwcaps=-AVX512VL"
    CASES = (   # (name, shipped (out, outcome, variant), avx2 (out, outcome, variant), second, {level: expected},
                #  confirming outs {arm: out, or None for a confirming record refused or mis-bound} or None)
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
        ("[R3] that one-cell loss REPRODUCES in the confirming run (its own values): v3 LOSS",
         (_rec(t, L7(1000), allf(990), per_cell=one_loss), "FULL", "evex"), good(), False, v3(Lo),
         {"shipped": _rec(t, L7(1010), allf(990), per_cell={("mfind-w32", 65536, 0): L7(1400)}),
          "avx2": _rec(t, L7(1000), allf(500))}),
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
        ("[r6 RULE-1] the shipped record REFUSED on the second run: NOT-WIN, never a third run",
         ({}, "REFUSED", "evex"), good(), True, each(NW), None),
        ("[r6 RULE-1] the shipped record's variant unknown on the second run: NOT-WIN",
         (_rec(t, L7(1000), allf(500)), "FULL", None), good(), True, each(NW), None),
        ("[r6 RULE-5] the one-cell loss, its confirming shipped record REFUSED or mis-bound: v3 INCONCLUSIVE, never "
         "CONFIRM again", (_rec(t, L7(1000), allf(990), per_cell=one_loss), "FULL", "evex"), good(), False, v3(T),
         {"shipped": None, "avx2": _rec(t, L7(1000), allf(500))}),
        ("[r6 RULE-5] the one-cell loss, the confirming record lacks that cell's rows: v3 INCONCLUSIVE",
         (_rec(t, L7(1000), allf(990), per_cell=one_loss), "FULL", "evex"), good(), False, v3(T),
         {"shipped": {k: v for k, v in _rec(t, L7(1000), allf(990)).items() if not k.endswith(".65536.0")},
          "avx2": _rec(t, L7(1000), allf(500))}),
        ("[r6 RULE-5] the same absent confirmation on the second run: v3 NOT-WIN",
         (_rec(t, L7(1000), allf(990), per_cell=one_loss), "FULL", "evex"), good(), True, v3(NW),
         {"shipped": None, "avx2": _rec(t, L7(1000), allf(500))}),
        ("[r6 RULE-5] three losses with a confirmation given for another level: v3 LOSS at once (no confirmation needed)",
         (_rec(t, L7(1000), allf(990), per_cell=three), "FULL", "evex"), good(), False, v3(Lo),
         {"shipped": None, "avx2": None}),
        ("[r6 FIDELITY-2] both records under the AVX2 tunable (EVEX never timed): the shipped arm no verdict, "
         "INCONCLUSIVE", (_rec(t, L7(1000), allf(500)), "FULL", TUN), (_rec(t, L7(1000), allf(500)), "FULL", TUN),
         False, each(T), None),
        ("[r6 FIDELITY-2] the shipped record bound the avx2 memchr with no tunable: INCONCLUSIVE",
         (_rec(t, L7(1000), allf(500)), "FULL", "avx2"), good(), False, each(T), None),
        ("deciding rows absent on 10 of 18 cells (gaps >= 32), the rest wins: INCONCLUSIVE",
         ({k: v for k, v in _rec(t, L7(1000), allf(500)).items() if int(k.split(".")[-2]) < 32}, "PARTIAL", "evex"),
         good(), False, each(T), None),
    )
    bad = 0
    for name, sa, aa, second, want, conf in CASES:
        recs = {"shipped": sa, "avx2": aa}
        def arms_of(form, which, recs=recs, conf=conf):
            o, outcome, var = recs[which]
            return arm(t, form, o, {}, outcome, run(var) if var else {}, which,
                       (conf[which], {}) if conf and conf.get(which) is not None else None)
        v = levels(t, arms_of, second, confirming=conf is not None)
        got = {l: x[0] for l, x in v.items()}
        ok = got == want
        bad += not ok
        print("drill\t%s\t%s\t%s" % (name, "ok" if ok else "WRONG", ", ".join(
            "%s %s%s" % (l, got[l], " (%s)" % " ".join("%d.%d" % c for c in v[l][5]) if v[l][5] else "") for l in lv)))
    n = len(CASES)
    # [r6 RULE-2, RULE-3, RULE-6] PROVENANCE on constructed records: (name, {role: record facts}, confirm cells the
    # first verdict named or None, the refusal's words or None for a pass)
    pins = record.rule_pins()
    PL = [("kit.find_hit.mfind-w32.periodic.one.65536.0", "JMH.g", "JMH")]
    PLC = [("kit.find_hit.mfind-w32.periodic.one.65536.0", "JMHC.g", "JMHC")]
    def M(run_id="r1", window="mfcard", commit="c0", plan_rows=PL, folds=None, pin=pins):
        r = dict(pin, run_id=run_id, window=window, code_commit=commit, cards_sha256="a", policy_sha256="b")
        return {"dir": run_id, "run": r, "plan": sorted(plan_rows), "folds": folds or {"mfind-w32": "f0"},
                "confirm_cells": {(65536, 0)} if window == "mfconfirm" else set()}
    run1 = {"shipped": M(), "avx2": M()}
    conf1 = {"confirm.shipped": M("r1.c", "mfconfirm", plan_rows=PLC), "confirm.avx2": M("r1.c", "mfconfirm", plan_rows=PLC)}
    first1 = {"first.shipped": M("r0"), "first.avx2": M("r0")}
    PCASES = (
        ("the control: a run, its confirmation and its first run, one experiment", dict(run1, **conf1, **first1),
         {(65536, 0)}, None),
        ("the SAME record passed as its own confirmation: REFUSED", dict(run1, **{"confirm.shipped": M(),
                                                                                 "confirm.avx2": M()}),
         {(65536, 0)}, "window mfcard"),
        ("a confirming record (window mfconfirm) carrying the first run's run id: REFUSED",
         dict(run1, **{"confirm.shipped": M("r1", "mfconfirm", plan_rows=PLC), "confirm.avx2": conf1["confirm.avx2"]}),
         {(65536, 0)}, "is the confirmed run's own"),
        ("a confirming record whose JMHC cells are not the CONFIRM's: REFUSED", dict(run1, **conf1), {(1024, 0)},
         "its JMHC cells 65536.0, the CONFIRM's 1024.0"),
        ("--confirm with no CONFIRM verdict: REFUSED", dict(run1, **conf1), set(), "nothing to confirm"),
        ("--second naming the run's own records: REFUSED", dict(run1, **{"first.shipped": M(), "first.avx2": M()}),
         None, "names the run's own run id"),
        ("--second naming a confirming record as the first run: REFUSED",
         dict(run1, **{"first.shipped": M("r0", "mfconfirm"), "first.avx2": M("r0")}), None, "window mfconfirm"),
        ("the two libc arms on different code commits: REFUSED", {"shipped": M(), "avx2": M(commit="c1")}, None,
         "code_commit c1"),
        ("the two libc arms on different plans: REFUSED", {"shipped": M(), "avx2": M(plan_rows=PL + PLC)}, None,
         "plan differs"),
        ("the confirming run on another kit fold: REFUSED",
         dict(run1, **{"confirm.shipped": M("r1.c", "mfconfirm", plan_rows=PLC, folds={"mfind-w32": "f1"}),
                       "confirm.avx2": conf1["confirm.avx2"]}), {(65536, 0)}, "kit fold of mfind-w32"),
        ("the second run on another code commit than the first: REFUSED",
         dict(run1, **{"first.shipped": M("r0", commit="c9"), "first.avx2": M("r0", commit="c9")}), None,
         "code_commit c9"),
        ("a record pinning another rule table: REFUSED",
         {"shipped": M(), "avx2": M(pin=dict(pins, d197_rule_tsv_sha256="0" * 64))}, None, "RULE PIN avx2"),
        ("a record pinning no rule (finalized before r6): REFUSED", {"shipped": M(pin={}), "avx2": M()}, None,
         "RULE PIN shipped"),
    )
    for name, recs, want_cells, refusal in PCASES:
        try:
            provenance(pins, recs)
            if want_cells is not None:
                confirm_cells_check(want_cells, recs)
            got = None
        except InputError as e:
            got = str(e)
        ok = got is None if refusal is None else got is not None and refusal in got
        bad += not ok
        n += 1
        print("drill\t[r6 provenance] %s\t%s\t%s" % (name, "ok" if ok else "WRONG", (got or "passes")[:160]))
    if scratch:
        # END TO END: the reader on est.py's own synthetic finalized mfcard window (compute's real row keys and
        # fields), both records: a verdict per level, every deciding cell read (none unresolved), no refusal
        import est
        for var, sub in (("evex", "shipped"), ("avx2", "avx2")):
            d = est._synth(os.path.join(scratch, "d197_" + sub), window="mfcard")
            rr = os.path.join(d, "run_record.tsv")
            txt = open(rr).read().replace("run_id\tselftest\n", "run_id\tselftest\nisa\tx86-64-v4 avx2\n"
                                          "libc\tglibc 2.43 memchr=%s%s\n" % (var, " GLIBC_TUNABLES=x" if var == "avx2" else "")
                                          + "".join("%s\t%s\n" % kv for kv in sorted(record.rule_pins().items())), 1)
            open(rr, "w").write(txt)
        sd, ad = os.path.join(scratch, "d197_shipped"), os.path.join(scratch, "d197_avx2")
        v = rule(sd, ad)
        want_n = 2 * len(lv) * len(cells(t))
        nc = sum(1 for x in v.values() for ln in x[3] if "\tcell\t" in ln and "unresolved" not in ln)
        # [r6 RULE-7] the scan ratio is a NUMBER for both libc rows at every level (est's synth prices find_byte@6)
        ok = (list(v) == lv and nc == want_n
              and all(len(re.findall(r"ratio [0-9]+\.[0-9]{2}\b", x[4])) == 2 for x in v.values()))
        bad += not ok
        n += 1
        print("drill\tend to end on est's synthetic window\t%s\t%d of %d cells read, %s; scan %s" % (
            "ok" if ok else "WRONG", nc, want_n, ", ".join("%s %s" % (l, v[l][0]) for l in lv), v[lv[0]][4]))
        # [r6 RULE-2] the critic's repro end to end: the run's own two records passed as their confirmation
        try:
            rule(sd, ad, confirm=(sd, ad))
            got = "passes"
        except InputError as e:
            got = str(e)
        ok = "window mfcard" in got
        bad += not ok
        n += 1
        print("drill\t[r6 RULE-2] end to end: the run's own records as their confirmation REFUSED\t%s\t%s" % (
            "ok" if ok else "WRONG", got[:160]))
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
