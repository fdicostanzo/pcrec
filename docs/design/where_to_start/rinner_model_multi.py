#!/usr/bin/env python3
"""rincensus lane (2026-10-11): the soundness model's second half -- what rinmodel's single-split
`R = (?:P)L(?:S)` generator could not express (critic review r1, F1/F2/F3/F4/F6).

Imports rinner_model.py (libpcre2 as the oracle AND as the tactic's two components, exactly as there) and adds

  --fixed        the planted rows, every startpos + find-all, against libpcre2 10.46:
                   F4  (?i)(?:xb*a|b)aA / xbaaa     caseless L: the arm must DECLINE (L's fold variants are bordered)
                       (?:xb*a|b)aa     / xbaaa     the same shape, case-sensitive: border-freeness is necessary
                   F3  b[ax]+ab         / abxab     floor at the previous occurrence's END is unsound (floor_end); the START + 1 is right
                       (?:dog|cat)ing   / doging    floor at a scan BYTE hit is unsound (floor_bytehit); the START + 1 is right
                   F1  (?:[ab]+:x|b:y)  / ab:y      verify the whole R at the UNION minimum is wrong (unionmin); per-branch verify in
                                                    increasing start order, first success wins, is right
                   F2  yab|[xy]*abc     / xyabc     DISTINCT landmarks per branch: one scan over {yab, abc} is wrong
                       x[a-y]*z|cq      / xcqz      (both must be DECLINED by the common-L rule)
                   C   (?:aq|[abq]{5}q) / bbaqbq    two FIXED widths: pair-admitted, composition-unsafe
  --multi N      N random cases R = (?:P1 L S1 | P2 L S2 | ...) with ONE common L and different P_i, S_i, gated by
                 the per-branch G2 arms (`pair`, the ruled text), the COMPOSITION rule (`comp`: every branch strong -- cannot-contain-L,
                 factor-free+border-free, or empty -- or every branch fixed at the SAME width) and `strong` (no fixed branch, where the
                 floor is also sound).  Variants: the form (ii) tactic, the floored tactic, and the mutants unionmin / floor_end /
                 floor_bytehit; negative controls pair_not_comp and gate_off.
  --distinct N   N random cases with a DIFFERENT landmark per branch; the single-scan tactic over all landmarks is the model of "distinct
                 landmarks" and must be wrong somewhere (so the common-L rule is shown necessary).
  --selftest     asserts the above (gated rows 0 wrong, every mutant and control detected).

Env PCRE2_LIB as in rinner_model.py (10.46 on the Linux dev box: /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0).
"""
import argparse, collections, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rinner_model as RM  # noqa: E402

CASELESS = 0x00000008


# ---- arms, per (P, L) -------------------------------------------------------

def variants(L, ci):
    out = [""]
    for ch in L:
        opts = {ch, ch.lower(), ch.upper()} if ci else {ch}
        out = [v + o for v in out for o in sorted(opts)]
    return sorted(set(out))


def fold_alph(al, ci):
    return al | {c.lower() for c in al} | {c.upper() for c in al} if ci else set(al)


def border_free_ci(L, ci):
    """no two occurrences (fold variants, possibly different) overlap"""
    vs = variants(L, ci)
    n = len(L)
    for k in range(1, n):
        for a in vs:
            for b in vs:
                if a[-k:] == b[:k]:
                    return False
    return True


def factor_free_ci(P, L, ci):
    return all(RM.factor_witness(P, v) is None for v in variants(L, ci))


def branch_arms(P, pw, palph, L, ci=False):
    """-> dict(fixed, disj, ffree, empty, strong); decided by THIS module's own code (parse_p NFA x KMP, per fold variant)."""
    empty = pw == (0, 0)
    fixed = pw[0] == pw[1]
    disj = not {c.lower() if ci else c for c in L} <= {c.lower() if ci else c for c in palph}
    ff = border_free_ci(L, ci) and factor_free_ci(P, L, ci)
    return dict(fixed=fixed, w=pw[0], disj=disj, ffree=ff, empty=empty, strong=(disj or ff or empty))


def gates(branches, L, ci=False):
    """pair / comp / strong for a multi-branch case (see the module docstring)."""
    ar = [branch_arms(b["P"], b["pw"], b["palph"], L, ci) for b in branches]
    g1 = all(not (b["pf"]["atomic"] or b["pf"]["look"]) for b in branches)
    pair = g1 and all(a["fixed"] or a["strong"] for a in ar)
    strong = pair and all(a["strong"] for a in ar)
    samew = pair and all(a["fixed"] for a in ar) and len({a["w"] for a in ar}) == 1
    comp = strong or samew
    return dict(g1=g1, pair=pair, comp=comp, strong=strong, samew=samew, arms=ar)


# ---- the tactics ------------------------------------------------------------

def find_L(base, L, j, ci):
    return (base.lower().find(L.lower(), j)) if ci else base.find(L, j)


def tactic_multi(R, branches, L, subj, frm, mut, opts, ci=False):
    """Form (ii): per occurrence j of the common L, each branch's own minimum start s*_i(j); verify the WHOLE R at them in increasing
    order; the first success is the answer.  Mutants: unionmin (verify only at the union minimum), floor (stop at the previous
    occurrence's first byte + 1), floor_end (its END), floor_bytehit (the previous hit of L's last byte), lo0."""
    cR = RM.comp(R.encode(), opts)
    Lb = L.encode()
    j, prev_j, prev_byte = frm, None, None
    sb = Lb[-1:]
    while True:
        j = find_L(subj, Lb, j, ci)
        if j < 0:
            return None
        lo = 0 if "lo0" in mut else frm
        if "floor" in mut and prev_j is not None:
            lo = max(lo, prev_j + 1)
        if "floor_end" in mut and prev_j is not None:
            lo = max(lo, prev_j + len(Lb))
        if "floor_bytehit" in mut:
            # the previous hit of the scan byte (L's last byte) anywhere in [frm, j): the cheapest "hit" a scan loop has
            k = subj.rfind(sb.lower() if ci else sb, frm, j + len(Lb) - 1) if not ci else max(
                subj.lower().rfind(sb.lower(), frm, j + len(Lb) - 1), -1)
            if k >= 0:
                lo = max(lo, k + 1)
        starts = []
        for b in branches:
            st = [s for s in range(lo, j + 1) if RM.p_ends_at(b["P"], opts, subj, s, j)]
            if st:
                starts.append(min(st))
        cand = sorted(set(starts))
        if "unionmin" in mut and cand:
            cand = cand[:1]
        for s in cand:
            r = RM.match(cR, subj, s, RM.ANCHORED)
            if r is not None:
                return r
        prev_j = j
        j += 1


def tactic_distinct(R, branches, subj, frm, opts):
    """DISTINCT landmarks: one scan over every branch's own L_i, in position order; at an occurrence of L_i the candidates are
    branch i's starts; verify the whole R at them in increasing order; first success wins."""
    cR = RM.comp(R.encode(), opts)
    for j in range(frm, len(subj) + 1):
        for b in branches:
            Lb = b["L"].encode()
            if subj[j:j + len(Lb)] != Lb:
                continue
            st = [s for s in range(frm, j + 1) if RM.p_ends_at(b["P"], opts, subj, s, j)]
            for s in sorted(st[:1]):
                r = RM.match(cR, subj, s, RM.ANCHORED)
                if r is not None:
                    return r
    return None


# ---- generators -------------------------------------------------------------

def gen_branch(rnd, L):
    g = RM.G(rnd, "P", 0); g.ncap0 = 0
    P, pw, pa = g.alt(0)
    h = RM.G(rnd, "S", 0); h.ncap0 = 0
    S, _w, _a = h.alt(0)
    return dict(P=P, S=S, pw=tuple(pw), palph=set(pa), pf=dict(g.f), L=L)


def gen_multi(rnd, distinct=False):
    nb = rnd.choice([2, 2, 3])
    L = rnd.choice(RM.LITS)
    if distinct:
        Ls = rnd.sample(sorted(set(RM.LITS)), nb)
    else:
        Ls = [L] * nb
    br = [gen_branch(rnd, Ls[i]) for i in range(nb)]
    R = "(?:%s)" % "|".join("(?:%s)%s(?:%s)" % (b["P"], b["L"], b["S"]) for b in br)
    return dict(L=L, branches=br, R=R, multi=rnd.random() < 0.2)


# ---- the random populations -------------------------------------------------

def run_multi(n, seed):
    rnd = random.Random(seed)
    tot, bad, wit = collections.Counter(), collections.Counter(), {}
    for _ in range(n):
        c = gen_multi(rnd)
        opts = (RM.MULTILINE if c["multi"] else 0) | (RM.UTF if RM.UTFMODE else 0)
        cR = RM.comp(c["R"].encode(), opts)
        if not cR or any(not RM.comp(("(?:%s)" % b["P"]).encode(), opts) for b in c["branches"]):
            tot["uncompilable"] += 1
            continue
        gt = gates(c["branches"], c["L"])
        tot["cases"] += 1
        for k in ("g1", "pair", "comp", "strong", "samew"):
            tot["gate:" + k] += gt[k]
        tot["gate:pair-not-comp"] += gt["pair"] and not gt["comp"]
        tot["gate:comp-needs-strong-arm"] += gt["comp"] and not gt["samew"]
        tot["gate:mixed-P (not all P_i equal text)"] += len({b["P"] for b in c["branches"]}) > 1 and gt["comp"]
        plan = []                                    # (key, mutation tuple, population predicate)
        if gt["comp"]:
            plan += [("tactic[comp]", ()), ("unionmin[comp]", ("unionmin",))]
        if gt["pair"] and not gt["comp"]:
            plan += [("pair_not_comp", ())]
        if gt["strong"]:
            plan += [("floor[strong]", ("floor",)), ("floor_end[strong]", ("floor_end",)),
                     ("floor_bytehit[strong]", ("floor_bytehit",))]
        if gt["g1"] and not gt["pair"]:
            plan += [("gate_off[split-ambiguous]", ())]
        if not plan:
            continue
        for subj in RM.subjects(rnd, 12):
            orc = lambda f: RM.match(cR, subj, f)
            truth_all = RM.find_all(orc, subj)
            for key, mut in plan:
                fn = lambda f: tactic_multi(c["R"], c["branches"], c["L"], subj, f, mut, opts)
                for frm in range(len(subj) + 1):
                    if RM.UTFMODE and frm < len(subj) and 0x80 <= subj[frm] < 0xC0:
                        continue
                    t, m = orc(frm), fn(frm)
                    tot[key] += 1
                    if t != m:
                        bad[key] += 1
                        wit.setdefault(key, (c["R"], subj, frm, t, m))
                got = RM.find_all(fn, subj)
                tot[key + "/findall"] += 1
                if got != truth_all:
                    bad[key + "/findall"] += 1
                    wit.setdefault(key + "/findall", (c["R"], subj, 0, truth_all, got))
    return tot, bad, wit


def run_distinct(n, seed):
    rnd = random.Random(seed)
    tot, bad, wit = collections.Counter(), collections.Counter(), {}
    for _ in range(n):
        c = gen_multi(rnd, distinct=True)
        if len({b["L"] for b in c["branches"]}) < 2:
            continue
        opts = RM.UTF if RM.UTFMODE else 0
        cR = RM.comp(c["R"].encode(), opts)
        if not cR or any(not RM.comp(("(?:%s)" % b["P"]).encode(), opts) for b in c["branches"]):
            continue
        # each branch is admitted BY ITSELF (a single split passing G1 and a G2 arm); the question is the combination
        ok = all(gates([b], b["L"])["pair"] for b in c["branches"])
        tot["cases"] += 1
        tot["each-branch-admitted"] += ok
        if not ok:
            continue
        for subj in RM.subjects(rnd, 12):
            orc = lambda f: RM.match(cR, subj, f)
            for frm in range(len(subj) + 1):
                if RM.UTFMODE and frm < len(subj) and 0x80 <= subj[frm] < 0xC0:
                    continue
                t, m = orc(frm), tactic_distinct(c["R"], c["branches"], subj, frm, opts)
                tot["distinct-landmark scan"] += 1
                if t != m:
                    bad["distinct-landmark scan"] += 1
                    wit.setdefault("distinct-landmark scan", (c["R"], subj, frm, t, m))
    return tot, bad, wit


def run_shaped(n, seed, nsubj=40):
    """SHAPED composition population (the random generator's 3-letter alphabet almost never lets two fixed widths collide):
    branches over {a,b,q}, L = q.  Branch kinds: FIXED (a literal or [abq]{w}, w 1..5), STRONG ([ab]+, [ab]{0,3}, empty), AMBIG
    ([abq]+, a P that can consume L).  Classes: comp (0 wrong required), pair_not_comp (must be wrong somewhere), gate_off."""
    global RM
    rnd = random.Random(seed)
    tot, bad, wit = collections.Counter(), collections.Counter(), {}
    kinds = {"fixed": ["a", "b", "ab", "[abq]{2}", "[abq]{3}", "[abq]{4}", "[abq]{5}", "aab", "[ab]{3}"],
             "strong": ["[ab]+", "[ab]{0,3}", "[ab]*", "b+", ""],
             "ambig": ["[abq]+", "[abq]{1,4}", "a[abq]*"]}
    alph = "abq"
    for _ in range(n):
        nb = rnd.choice([2, 2, 3])
        spec, names = [], []
        for _i in range(nb):
            kd = rnd.choice(["fixed", "fixed", "strong", "strong", "ambig"] if rnd.random() < 0.9 else ["ambig"])
            spec.append((rnd.choice(kinds[kd]), rnd.choice(["", "", "a", "b"])))
            names.append(kd)
        br = parse_branches([(P if P else "", S) for P, S in spec], False)
        for b, (P, S) in zip(br, spec):
            if P == "":
                b["pw"], b["palph"] = (0, 0), set()
        L = "q"
        R = "(?:%s)" % "|".join("(?:%s)%s(?:%s)" % (b["P"], L, b["S"]) for b in br)
        cR = RM.comp(R.encode(), 0)
        if not cR:
            continue
        gt = gates(br, L)
        key = "comp" if gt["comp"] else ("pair_not_comp" if gt["pair"] else "gate_off")
        sub = "+".join(sorted(set(names))) if key == "pair_not_comp" else ""
        tot["cases:" + key] += 1
        subs = set()
        while len(subs) < nsubj:
            subs.add("".join(rnd.choice(alph) for _ in range(rnd.randint(2, 9))).encode())
        for subj in sorted(subs):
            orc = lambda f: RM.match(cR, subj, f)
            fn = lambda f: tactic_multi(R, br, L, subj, f, (), 0)
            for frm in range(len(subj) + 1):
                t, m = orc(frm), fn(frm)
                tot[key] += 1
                if sub: tot[key + "[" + sub + "]"] += 1
                if t != m:
                    bad[key] += 1
                    if sub: bad[key + "[" + sub + "]"] += 1
                    wit.setdefault(key, (R, subj, frm, t, m))
                    if sub: wit.setdefault(key + "[" + sub + "]", (R, subj, frm, t, m))
    return tot, bad, wit


# ---- the planted rows -------------------------------------------------------

def parse_branches(spec, ci):
    """spec: list of (P, S); P text parsed by rinner_model's parse_p for width/alphabet (its own bookkeeping)."""
    out = []
    for P, S in spec:
        lo, hi, al = RM.ast_info(RM.parse_p(P))
        out.append(dict(P=P, S=S, pw=(lo, hi), palph=al, pf=dict(atomic=0, look=0, view=0, bref=0)))
    return out


ROWS = [
    # name, regex R (as libpcre2 sees it), branches [(P, S)], L, subject, caseless, which variants must be wrong
    ("F4 (?i)(?:xb*a|b)aA", "(?i)(?:xb*a|b)aA", [("(?:xb*a|b)", "")], "aA", b"xbaaa", True, ["plain"]),
    ("F4' (?:xb*a|b)aa", "(?:xb*a|b)aa", [("(?:xb*a|b)", "")], "aa", b"xbaaa", False, ["plain"]),
    ("F3 b[ax]+ab", "b[ax]+ab", [("b[ax]+", "")], "ab", b"abxab", False, ["floor_end"]),
    ("F3' (?:dog|cat)ing", "(?:dog|cat)ing", [("(?:dog|cat)", "")], "ing", b"doging", False, ["floor_bytehit"]),
    ("F1 (?:[ab]+:x|b:y)", "(?:[ab]+:x|b:y)", [("[ab]+", "x"), ("b", "y")], ":", b"ab:y", False, ["unionmin"]),
    ("C  (?:aq|[abq]{5}q)", "(?:aq|[abq]{5}q)", [("a", ""), ("[abq]{5}", "")], "q", b"bbaqbq", False, ["plain"]),
]
DISTINCT_ROWS = [
    ("F2 yab|[xy]*abc", "yab|[xy]*abc", [("", "", "yab"), ("[xy]*", "", "abc")], b"xyabc"),
    ("F2 x[a-y]*z|cq", "x[a-y]*z|cq", [("x[a-y]*", "", "z"), ("", "", "cq")], b"xcqz"),
]
# (P, S, L_i): a branch's landmark is its WHOLE maximal literal run (yab / abc / z / cq), P what precedes it

VARS = [("plain", ()), ("floor", ("floor",)), ("floor_end", ("floor_end",)), ("floor_bytehit", ("floor_bytehit",)),
        ("unionmin", ("unionmin",))]


def run_fixed(show=True):
    out, fails = [], []
    for name, R, spec, L, subj, ci, must_wrong in ROWS:
        opts = CASELESS if ci else 0
        cR = RM.comp(R.encode(), opts)
        assert cR, name
        br = parse_branches(spec, ci)
        gt = gates(br, L, ci)
        orc = lambda f: RM.match(cR, subj, f)
        truth0 = orc(0)
        print("== %s   subject %r   libpcre2 truth from 0: %s" % (name, subj, truth0))
        print("   gate: pair=%s comp=%s strong=%s samew=%s; arms per branch: %s%s"
              % (gt["pair"], gt["comp"], gt["strong"], gt["samew"],
                 [{k: v for k, v in a.items() if k in ("fixed", "disj", "ffree", "empty")} for a in gt["arms"]],
                 "  (fold variants of L: %s)" % variants(L, ci) if ci else ""))
        for vname, mut in VARS:
            if vname == "unionmin" and len(br) < 2:
                continue
            got0 = tactic_multi(R, br, L, subj, 0, mut, opts, ci)
            wrong = 0
            for frm in range(len(subj) + 1):
                t = orc(frm)
                m = tactic_multi(R, br, L, subj, frm, mut, opts, ci)
                wrong += t != m
            fa_t = RM.find_all(orc, subj)
            fa_m = RM.find_all(lambda f: tactic_multi(R, br, L, subj, f, mut, opts, ci), subj)
            print("   %-14s from 0: %-10s startpos mismatches %d, find-all %s" % (vname, got0, wrong, "ok" if fa_t == fa_m else "WRONG"))
            if vname in must_wrong and not (wrong or fa_t != fa_m):
                fails.append("%s: %s was NOT wrong (the plant does not bite)" % (name, vname))
            if vname not in must_wrong and (wrong or fa_t != fa_m) and vname in ("floor", "unionmin") and vname != "unionmin":
                pass
        # the gate must DECLINE the rows where the plain tactic is the planted failure
        if name.startswith(("F4", "C ")):
            if gt["comp"] and not name.startswith("F4"):
                fails.append("%s: the composition gate admitted it" % name)
            if name.startswith("F4") and gt["pair"] and gt["comp"]:
                fails.append("%s: the arm admitted a bordered L" % name)
            print("   -> declined by the gate: %s" % (not gt["comp"]))
        else:
            if not gt["comp"]:
                fails.append("%s: the correct form's gate declined it (%s)" % (name, gt))
            for vname in ("plain",) + (("floor",) if gt["strong"] else ()):
                wrong = sum(orc(f) != tactic_multi(R, br, L, subj, f, dict(VARS)[vname], opts, ci) for f in range(len(subj) + 1))
                if wrong:
                    fails.append("%s: the correct %s form is WRONG (%d)" % (name, vname, wrong))
    for name, R, spec, subj in DISTINCT_ROWS:
        cR = RM.comp(R.encode(), 0)
        br = []
        for P, S, L in spec:
            lo, hi, al = RM.ast_info(RM.parse_p(P)) if P else (0, 0, set())
            br.append(dict(P=P, S=S, L=L, pw=(lo, hi), palph=al, pf=dict(atomic=0, look=0, view=0, bref=0)))
        truth = RM.match(cR, subj, 0)
        got = tactic_distinct(R, br, subj, 0, 0)
        print("== %s   subject %r   truth %s   one scan over the distinct landmarks %s -> %s"
              % (name, subj, truth, [b["L"] for b in br], got))
        if truth == got:
            fails.append("%s: the distinct-landmark scan was RIGHT (the plant does not bite)" % name)
        print("   -> each branch alone is admitted: %s; common L across the branches: none -> DECLINED by the common-L rule"
              % [gates([b], b["L"])["pair"] for b in br])
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixed", action="store_true")
    ap.add_argument("--multi", type=int)
    ap.add_argument("--distinct", type=int)
    ap.add_argument("--shaped", type=int, help="N shaped composition cases (fixed-width / strong / ambiguous branches over {a,b,q})")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--utf8", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.utf8:
        RM.ALPH, RM.SUBJ, RM.UTFMODE = "abXé", "aabXXéé\n", True
        RM.LITS = ["X", "é", "Xé", "éa", "aa", "a"]
    print("# rinner_model_multi.py: libpcre2 %s%s, seed %d" % (RM.version(), "" if RM.version().startswith("10.46") else " (NOT the 10.46 reference)", a.seed))
    fails = []
    if a.fixed:
        fails += run_fixed()
    if a.multi:
        tot, bad, wit = run_multi(a.multi, a.seed)
        print("multi: %d cases compiled (uncompilable %d), seed %d%s" % (tot["cases"], tot["uncompilable"], a.seed, ", UTF" if a.utf8 else ""))
        for k in sorted(k for k in tot if k.startswith("gate:")):
            print("  %-45s %6d" % (k, tot[k]))
        print("%-32s %10s %10s  %s" % ("variant", "checks", "mismatch", "first witness (R, subject, startpos, truth, model)"))
        for k in sorted(k for k in tot if not k.startswith("gate:") and k not in ("cases", "uncompilable")):
            print("%-32s %10d %10d  %s" % (k, tot[k], bad[k], wit.get(k, "") if bad[k] else ""))
        for k in ("tactic[comp]", "floor[strong]"):
            for sf in ("", "/findall"):
                if bad[k + sf]:
                    fails.append("%s%s: the gated form disagrees with libpcre2" % (k, sf))
        for k in ("unionmin[comp]", "floor_end[strong]", "floor_bytehit[strong]"):
            if bad[k] + bad[k + "/findall"] == 0:
                fails.append("%s: never wrong (mutant / negative control undetected)" % k)
        if tot["tactic[comp]"] == 0 or tot["floor[strong]"] == 0:
            fails.append("a gated population is empty")
    if a.shaped:
        tot, bad, wit = run_shaped(a.shaped, a.seed)
        print("shaped composition: seed %d, %d cases" % (a.seed, a.shaped))
        print("%-52s %10s %10s  %s" % ("class", "checks", "mismatch", "first witness (R, subject, startpos, truth, model)"))
        for k in sorted(k for k in tot if not k.startswith("cases:")):
            print("%-52s %10d %10d  %s" % (k, tot[k], bad[k], wit.get(k, "") if bad[k] else ""))
        print("cases: " + ", ".join("%s %d" % (k[6:], tot[k]) for k in sorted(tot) if k.startswith("cases:")))
        if bad["comp"]:
            fails.append("shaped comp-gated: the composition rule is WRONG (%d)" % bad["comp"])
        for k in ("pair_not_comp", "gate_off"):
            if bad[k] == 0:
                fails.append("shaped %s: never wrong (the control cannot fail)" % k)
        if tot["comp"] == 0:
            fails.append("shaped comp population empty")
    if a.distinct:
        tot, bad, wit = run_distinct(a.distinct, a.seed)
        print("distinct: %d cases, each branch admitted alone in %d" % (tot["cases"], tot["each-branch-admitted"]))
        k = "distinct-landmark scan"
        print("%-32s %10d %10d  %s" % (k, tot[k], bad[k], wit.get(k, "") if bad[k] else ""))
        if bad[k] == 0:
            fails.append("the distinct-landmark scan was never wrong: the common-L rule is not shown necessary")
    if a.selftest:
        print("selftest: " + ("PASS" if not fails else "FAIL: " + "; ".join(fails)))
        sys.exit(1 if fails else 0)
    elif fails:
        print("NOTE: " + "; ".join(fails))


if __name__ == "__main__":
    main()
