# predspec22: evidence for docs/design/predicates_draft.md rev 22 and docs/dev/lanes/predspec22_report.md
# (lane predspec22, 2026-11-16; design only).
#
# THE QUESTIONS. The owner ruled **not-is-complement** (COND-FAMILY, 17:29): `!` applies to a PATTERN (a regex, or a
# program = a regex with its conditions) and gives the complement of its string set, or to a SET (the value side),
# never to a CONDITION. A `!` on a condition becomes a compile ERROR naming two rewrites: the complement on the set
# (`(h: !S)`), or name the pattern and complement it (`q := P & c; P & !q`). THE MANAGER'S READINGS (his, checked
# here): a complemented pattern is a COMPLETE program with its own value sets (DOM); conditions outside it never
# narrow them, its own never narrow the outside's; the complement carries no labels; in a chain it is a label-free
# filter on subjects. And **mark-in-none** (17:42): LEFT AS IS (a mark inside `none` or a count is legal; documented).
#
# PARTS: (A) every `!`-on-a-condition site of rev 21 with a worked answer, against its rewrites (L30, L95, "every hit,
#   possibly none", `when`); (B) the mark inside a group question (the `6,` example) and the two spellings that avoid
#   the dependence; (C) the closing example's candidates over the 1,111 lists against the stated intents, with an
#   ENGINE-RUN regex per intent; (D) one-witness: two marked conditions vs the one-condition spelling; (E) predspec21's
#   moving pairs re-run after the rewrites, then every (program, added condition) pair of the rev 22 pools; (F) the
#   well-foundedness, commutativity and record = `&` checks with complemented patterns in the chain.
# KINDS: RUN / COMPUTED / ENGINE-RUN as in predspec21_check.py. REUSE: predspec21_check.py is exec'd VERBATIM with its
#   output suppressed (its engines groups()/whole()/check(), Fac, doms() with THE RULE as "MANAGER", answers(), the
#   (SEARCH)/(NEGPOL) pools and populations); this script adds the complemented pattern and the rev 22 spellings.
# Run from the scratch dir: `timeout 300 python3 -I /abs/path/docs/dev/lanes/predspec22_check.py`.
# Sabotage: `PREDSPEC22_SABOTAGE=1` makes a complemented pattern read the OUTSIDE program's DOM (the rev 21 `!` on a
#   condition, N1); the (E) mapped compound pairs must then move (> 0), and (A) L30's marked complemented answer flips.
import contextlib, io, itertools, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_buf = io.StringIO()
with contextlib.redirect_stdout(_buf):
    exec(open(os.path.join(HERE, "predspec21_check.py")).read(), globals())
_p21 = _buf.getvalue()
SAB22 = os.environ.get("PREDSPEC22_SABOTAGE") == "1"
print("predspec22_check: predspec21_check.py exec'd verbatim (%d lines of its output suppressed; its TOTAL line: %s)"
      % (_p21.count("\n"), [l for l in _p21.splitlines() if l.startswith("TOTAL")][0]))
if SAB22:
    print("SABOTAGE ON (PREDSPEC22_SABOTAGE=1): a complemented pattern reads the OUTSIDE program's DOM")
T0 = dict(TOT)
RULE = "MANAGER"            # THE RULE (mark-narrows, the variant); N1 for a negated mark (rev 21's lean)


def compl(pop, labels, vals, inner):
    """`!q`, q := (the pattern) & inner: a COMPLETE program; its DOMs are its own (THE RULE over q's conditions only);
    the result is a label-free filter on subjects. SABOTAGE: the rev 21 `!` on a condition (reads the outside DOM)."""
    if SAB22:
        return Fac(frozenset().union(*[f.names for f in inner]),
                   lambda s, Dm: not all(f.fn(s, Dm) for f in inner),
                   marks=frozenset().union(*[f.marks for f in inner]), negmark=True)
    qa = answers(pop, labels, vals, inner, RULE)[0]
    return Fac("", lambda s, Dm: not qa[s], marks="")


def run(pop, labels, vals, facs):
    return answers(pop, labels, vals, facs, RULE)


def ndiff(A, B, pop):
    d = [s for s in pop if A[s] != B[s]]
    return len(d), sm(d)


# =================================================================================================================
print("\nPART A: EVERY `!` ON A CONDITION WITH A WORKED ANSWER, AGAINST ITS REWRITES (THE RULE)")
print("\n(A1) L30, one label: /(?<h>\\d)?x/, 11 subjects, S = <5")
NOT5 = lambda x: not S5(x)
fU = Fac("h", lambda s, Dm: GN[s]["h"] is not None and S5(GN[s]["h"]), marks="")
fM = Fac("h", lambda s, Dm: mk(GN[s]["h"], S5, Dm["h"]))
rows = [
    ("rev 21 `!(h: <5)` (unmarked; the plain complement)", [Fac("h", lambda s, Dm: not fU.fn(s, Dm), marks="")]),
    ("`(h: !(<5))` (the complement on the set)", [Fac("h", lambda s, Dm: GN[s]["h"] is not None and NOT5(GN[s]["h"]),
                                                      marks="")]),
    ("`P & !q`, q := P & (h: <5)", [compl(POP_N, ["h"], v_n, [fU])]),
    ("rev 21 `!(h?: <5)` (marked; N1)", [Fac("h", lambda s, Dm: not fM.fn(s, Dm), negmark=True)]),
    ("`(h?: !(<5))` (the complement on the set)", [Fac("h", lambda s, Dm: mk(GN[s]["h"], NOT5, Dm["h"]))]),
    ("`P & !q`, q := P & (h?: <5)", [compl(POP_N, ["h"], v_n, [fM])]),
]
A1 = {}
for name, facs in rows:
    a, dm = run(POP_N, ["h"], v_n, facs)
    A1[name] = a
    print("   %-52s DOM(h)={%s} on `x` %s; holds on %d of %d" % (name, dstr(dm["h"]), hfx(a["x"]), sum(a.values()),
                                                                 len(POP_N)))
ks = list(A1)
for i, j in ((0, 1), (0, 2), (3, 4), (3, 5)):
    n, ex = ndiff(A1[ks[i]], A1[ks[j]], POP_N)
    print("   %s vs %s: differ %d of %d%s" % (ks[i].split(" (")[0], ks[j].split(" (")[0], n, len(POP_N),
                                            "" if ex is None else " (smallest %r)" % ex))

print("\n(A2) L95, the joint pair on t2 (11,110 subjects), R = padded(>= (9, 30)); then `& (m?: padded(<30))` added")
fR = jm(GE930)[0]
m30 = Fac("m", lambda s, Dm: mk(G_T2[s]["m"], lambda x: num(x) and int(x) < 30, Dm["m"]))
A2 = {}
for name, facs in (("rev 21 `!((h, m?): R)` (N1)", [Fac("m", lambda s, Dm: not fR.fn(s, Dm), negmark=True)]),
                   ("`((h, m?): !R)`", jm(lambda t: not GE930(t))),
                   ("`t2 & !q`, q := t2 & ((h, m?): R)", [compl(POP_T2, ["m"], v_t2, [fR])])):
    a1, d1 = run(POP_T2, ["m"], v_t2, facs)
    a2, d2 = run(POP_T2, ["m"], v_t2, facs + [m30])
    A2[name] = a1
    mv = [s for s in POP_T2 if not a1[s] and a2[s]]
    print("   %-36s on `9` %s (DOM(m) %s); + (m?: padded(<30)): %s (DOM(m) %s); FAIL -> HOLD on %d subjects%s" % (
        name, hfx(a1["9"]), dstr(d1["m"]), hfx(a2["9"]), dstr(d2["m"]), len(mv), "" if not mv else
        " (smallest %r)" % sm(mv)))
k2 = list(A2)
n, ex = ndiff(A2[k2[0]], A2[k2[2]], POP_T2)
print("   rev 21 `!` vs `t2 & !q`: differ %d of %d%s" % (n, len(POP_T2), "" if ex is None else " (smallest %r)" % ex))

print("\n(A3) \"every hit's g is `a`, possibly none\" over occurrences(/(?<g>a)?b/), %d spans over {a,b} to length 6"
      % len(SUB))
CANDS3 = {
    "rev 21 `occurs.none(!(g: \"a\"))`": lambda hs: not any((v != "a") if v is not None else True for v in hs),
    "`occurs.none((g: !\"a\"))` (set complement)": lambda hs: not any(v is not None and v != "a" for v in hs),
    "`occurs.none((g = \"\": !\"a\"))` (a default outside S)": lambda hs: not any((v if v is not None else "") != "a"
                                                                                  for v in hs),
    "`(g: \"a\")` (the plain condition)": lambda hs: bool(hs) and all(v == "a" for v in hs),
}
RX3 = {"natural": r"(?!b)(?![ab]*bb)[ab]*", "all": r"[ab]*"}
for name, f in CANDS3.items():
    d = [s for s in SUB if f(hits(s)) != all(v == "a" for v in hits(s))]
    for s in SUB:
        check("A3 " + name, RX3["natural"] if "default" in name or "rev 21" in name else
              (RX3["all"] if "set complement" in name else r"(?=[ab]*b)(?!b)(?![ab]*bb)[ab]*"), s, f(hits(s)))
    print("   %-58s vs the intent: differ %3d of %d%s" % (name, len(d), len(SUB), "" if not d else
                                                          " (smallest %r)" % sm(d)))

print("\n(A4) `when(c, p)`: rev 21 body `(x & c & p) | (x & !c)` vs rev 22 body `(x & c & p) | (x & !q)`, q := x & c;"
      " x = /(?<k>\\d)(?:;(?<h>\\d))*/ (1,110 subjects), p = (k: 3..7)")
for cname, cf in (("(h: <5)", Fac("h", lambda s, Dm: bool(RZ[s][1]) and all(S5(x) for x in RZ[s][1]), marks="")),
                  ("(h?: <5)", hpass(S5))):
    old_f = Fac("h", lambda s, Dm, cf=cf: (cf.fn(s, Dm) and T37(RZ[s][0])) or not cf.fn(s, Dm),
                marks=cf.marks, negmark=bool(cf.marks))
    old, dmo = run(POP_RZ, ["h"], v_rz, [old_f])
    left = run(POP_RZ, ["h"], v_rz, [cf, KF])[0]
    qn = compl(POP_RZ, ["h"], v_rz, [cf])
    new = {s: left[s] or qn.fn(s, dmo) for s in POP_RZ}
    n, ex = ndiff(old, new, POP_RZ)
    print("   c = %-9s rev 21 vs rev 22 body: differ %d of %d%s; on `0`: %s / %s; on `9`: %s / %s" % (
        cname, n, len(POP_RZ), "" if ex is None else " (smallest %r)" % ex, hfx(old["0"]), hfx(new["0"]),
        hfx(old["9"]), hfx(new["9"])))

# =================================================================================================================
print("\nPART B: A MARK INSIDE A GROUP QUESTION (mark-in-none, LEFT AS IS); the lists of 0-2 items, %d lists" % len(POPL))
PS = {s: [(g["h"], g["m"]) for g in (groups(ITM, x + ",", ["h", "m"]) for x in s.split(",")[:-1])] for s in POPL}
GE_ = lambda h, m: int(m) >= int(h)


def gnone(R, mode, dflt="0"):
    """occurs.none over the passes: mode 'mark' (m? F1), 'plain' (an item lacking m is not counted), 'dflt' (m = v)"""
    if mode == "mark":
        return Fac("hm", lambda s, Dm: not any(pv(PS[s], jt(R), Dm)), marks="m", negmark=True)
    if mode == "plain":
        return Fac("hm", lambda s, Dm: not any(m is not None and R(h, m) for h, m in PS[s]), marks="")
    return Fac("hm", lambda s, Dm: not any(R(h, m if m is not None else dflt) for h, m in PS[s]), marks="")


addm = dict(poolL)["(m?: >5)"]
SPB = [("`occurs.none(((h, m?): m < h))` (marked)", gnone(MLTH, "mark")),
       ("`occurs.none(((h, m): m < h))` (unmarked, same set)", gnone(MLTH, "plain")),
       ("`occurs.none(((h, m): m >= h))` (unmarked, the complement on the set)", gnone(GE_, "plain")),
       ("`occurs.none(((h, m = 0): m < h))` (default 0)", gnone(MLTH, "dflt")),
       ("`occurs.none(((h, m = 0): m >= h))` (default 0, the complement on the set)", gnone(GE_, "dflt"))]
BANS = {}
for name, f in SPB:
    a1, d1 = run(POPL, ["m"], vL, [f])
    a2, d2 = run(POPL, ["m"], vL, [f, addm])
    BANS[name] = a1
    mv = [s for s in POPL if not a1[s] and a2[s]]
    print("   %-74s on `6,` %s (DOM(m) {%s}); + (m?: >5): %s (DOM(m) {%s}); FAIL -> HOLD on %d lists%s" % (
        name, hfx(a1["6,"]), dstr(d1["m"]), hfx(a2["6,"]), dstr(d2["m"]), len(mv), "" if not mv else
        " (smallest %r)" % sm(mv)))
base = BANS[SPB[0][0]]
for name, _ in SPB[1:]:
    n, ex = ndiff(base, BANS[name], POPL)
    print("   marked vs %-66s differ %2d of %d%s" % (name, n, len(POPL), "" if ex is None else
                                                     " (smallest %r: marked %s, this %s)" % (ex, hfx(base[ex]),
                                                                                            hfx(BANS[name][ex]))))
# the stated meaning of each DOM-free spelling, checked against a direct per-item reading (and ENGINE-RUN regexes)
MEAN = {SPB[1][0]: (lambda h, m: m is None or int(m) >= int(h), r"(?:1,|6,|1:[1-9],|6:[6-9],)*"),
        SPB[2][0]: (lambda h, m: m is None or int(m) < int(h), r"(?:1,|6,|1:0,|6:[0-5],)*"),
        SPB[3][0]: (lambda h, m: m is not None and int(m) >= int(h), r"(?:1:[1-9],|6:[6-9],)*"),
        SPB[4][0]: (lambda h, m: m is None or int(m) < int(h), r"(?:1,|6,|1:0,|6:[0-5],)*")}
for name, (per, rx) in MEAN.items():
    want = {s: all(per(h, m) for h, m in PS[s]) for s in POPL}
    for s in POPL:
        check("B " + name, rx, s, want[s])
    n, _ = ndiff(want, BANS[name], POPL)
    print("   %-74s = its per-item reading on %d of %d (ENGINE-RUN)" % (name, len(POPL) - n, len(POPL)))

# (B2) the owner's question "m is absent or if present, it is m < h" and his default `m = 0`, over lists whose hours
# include 0 (the list pool above has hours 1 and 6 only, where 0 < h always): items h in {0, 1, 6}, m in {absent, 2, 7}
its0 = [h + ("" if m is None else ":" + m) + "," for h in ("0", "1", "6") for m in (None, "2", "7")]
POPL0 = ["".join(c) for k in range(3) for c in itertools.product(its0, repeat=k)]
PS0 = {}
for s in POPL0:
    assert whole(LST, s)
    PS0[s] = [(g["h"], g["m"]) for g in (groups(ITM, x + ",", ["h", "m"]) for x in s.split(",")[:-1])]
WANT0 = {s: all(m is None or int(m) < int(h) for h, m in PS0[s]) for s in POPL0}
B2 = {"`occurs.none(((h, m): m >= h))` (unmarked, the complement on the set)":
      lambda ps: not any(m is not None and int(m) >= int(h) for h, m in ps),
      "`occurs.none(((h, m = 0): m >= h))` (default 0, inside none)":
      lambda ps: not any(int(m if m is not None else "0") >= int(h) for h, m in ps),
      "`((h, m = 0): m < h)` (default 0, the plain per-pass condition)":
      lambda ps: bool(ps) and all(int(m if m is not None else "0") < int(h) for h, m in ps)}
for s in POPL0:
    check("B2 intent", r"(?:\d,|1:0,|6:[0-5],)*", s, WANT0[s])
print("   (B2) \"m is absent, or if present m < h\" over %d lists with hours 0, 1, 6 (ENGINE-RUN intent: holds on %d):"
      % (len(POPL0), sum(WANT0.values())))
for name, f in B2.items():
    d = [s for s in POPL0 if f(PS0[s]) != WANT0[s]]
    print("      %-68s differ %2d%s" % (name, len(d), "   EXACT" if not d else "   (smallest %r)" % sm(d)))

# =================================================================================================================
print("\nPART C: THE CLOSING EXAMPLE over /(?:(?<h>\\d+)(?::(?<m>\\d\\d))?,)*/, %d lists, R = (<10, <30)" % len(SUBO))
inR = lambda h, m: int(h) < 10 and int(m) < 30
DOMv = {d for d in DOMm if int(d) < 30}      # THE RULE: the condition narrows DOM(m) where m is present (PART 4 (D5))
INT = {"I1 every item complete and in R (the empty list passes)": lambda ps: all(m is not None and inR(h, m)
                                                                                 for h, m in ps),
       "I2a every item with minutes in R; an item without minutes acceptable, unchecked": lambda ps: all(
           m is None or inR(h, m) for h, m in ps),
       "I2b every item in R; an item without minutes acceptable when its hour fits": lambda ps: all(
           (int(h) < 10) if m is None else inR(h, m) for h, m in ps)}
IRX = {"I1": r"(?:[0-9]:[0-2][0-9],)*", "I2a": r"(?:[0-9]:[0-2][0-9],|\d+,)*", "I2b": r"(?:[0-9](?::[0-2][0-9])?,)*"}
CANC = {
    "rev 21 `occurs.none(!((h, m): R))` (now illegal)": lambda ps: not any(m is None or not inR(h, m) for h, m in ps),
    "`((h, m): R)` (the plain per-pass condition)": lambda ps: bool(ps) and all(m is not None and inR(h, m)
                                                                                 for h, m in ps),
    "`occurs.none(((h, m): !R))` (unmarked, set complement)": lambda ps: not any(m is not None and not inR(h, m)
                                                                                  for h, m in ps),
    "`occurs.none(((h, m = 99): !R))` (a default outside R)": lambda ps: not any(not inR(h, m if m is not None else "99")
                                                                                  for h, m in ps),
    "`occurs.none(((h, m = 00): !R))` (a default inside R)": lambda ps: not any(not inR(h, m if m is not None else "00")
                                                                                 for h, m in ps),
    "`((h, m = 99): R)` (plain, default outside R)": lambda ps: bool(ps) and all(inR(h, m if m is not None else "99")
                                                                                  for h, m in ps),
    "`((h, m?): R)` (the marked plain condition, THE RULE)": lambda ps: bool(ps) and all(
        inR(h, m) if m is not None else any(inR(h, d) for d in DOMv) for h, m in ps),
    "`occurs.none(((h, m?): !R))` (marked, THE RULE)": lambda ps: not any(
        (not inR(h, m)) if m is not None else any(not inR(h, d) for d in DOMv) for h, m in ps),
}
PSO = {s: [(x.split(":")[0], x.split(":")[1] if ":" in x else None) for x in s.split(",") if x] for s in SUBO}
for iname, ifn in INT.items():
    tag = iname.split()[0]
    want = {s: ifn(PSO[s]) for s in SUBO}
    for s in SUBO:
        check("C " + tag, IRX[tag], s, want[s])
    print("   %s (ENGINE-RUN /%s/): holds on %d" % (iname, IRX[tag], sum(want.values())))
    for cname, cfn in CANC.items():
        d = [s for s in SUBO if cfn(PSO[s]) != want[s]]
        print("      %-62s differ %4d%s" % (cname, len(d), "   EXACT" if not d else "   (smallest %r)" % sm(d)))

# =================================================================================================================
print("\nPART D: ONE WITNESS: /(?<j>\\d)(?<h>\\d)?(?<k>\\d)/, 1,100 subjects")
PJ = r"(?<j>\d)(?<h>\d)?(?<k>\d)"
POPJ = [j + h + k for j in D for h in [""] + D for k in D]
GJ = {s: groups(PJ, s, ["j", "h", "k"]) for s in POPJ}
vJ = lambda s, lab: [GJ[s][lab]] if GJ[s][lab] is not None else []
c1 = Fac("hk", lambda s, Dm: mk(GJ[s]["h"], lambda x: int(x) < int(GJ[s]["k"]), Dm["h"]), marks="h")
c2 = Fac("hj", lambda s, Dm: mk(GJ[s]["h"], lambda x: int(x) > int(GJ[s]["j"]), Dm["h"]), marks="h")
c12 = Fac("hjk", lambda s, Dm: mk(GJ[s]["h"], lambda x: int(GJ[s]["j"]) < int(x) < int(GJ[s]["k"]), Dm["h"]),
          marks="h")
two, dt = run(POPJ, ["h"], vJ, [c1, c2])
one, do = run(POPJ, ["h"], vJ, [c12])
n, ex = ndiff(two, one, POPJ)
print("   `(h?: <$k) & (h?: >$j)` (two conditions, two stand-in values): DOM(h)={%s}, on `12` %s, holds on %d" %
      (dstr(dt["h"]), hfx(two["12"]), sum(two.values())))
print("   `(h?: >$j & <$k)` (one condition, one stand-in value):        DOM(h)={%s}, on `12` %s, holds on %d" %
      (dstr(do["h"]), hfx(one["12"]), sum(one.values())))
print("   differ %d of %d (smallest %r); every differing subject has h ABSENT: %s" % (
    n, len(POPJ), ex, all(GJ[s]["h"] is None for s in POPJ if two[s] != one[s])))

# =================================================================================================================
print("\nPART E: THE MOVING PAIRS RE-RUN (THE RULE; N1/N2 are moot: no `!` on a condition remains)")
# the rev 21 pools, as predspec21's (NEGPOL) built them, with the categories of the program's negative-polarity marks
OLDP = [(pn, pop, recs, pool, labs) for pn, pop, recs, pool, labs in NEGPOOLS]


def vw(recs):
    if recs is None:
        return vL, (lambda f: f)
    return ((lambda s, lab: [recs[s][lab]] if recs[s][lab] is not None else []),
            (lambda f: Fac(f.names, (lambda s, Dm: f.fn(recs[s], Dm)), marks=f.marks, negmark=f.negmark)))


def inner_of(name, recs):
    """the condition under a rev 21 `!` (unwrapped), its set-complement rewrite, by name"""
    if name.startswith("!((h?, k)"):
        def fin(rec, Dm):
            if rec["k"] is None:
                return False
            hs = [rec["h"]] if rec["h"] is not None else sorted(Dm["h"])
            return any(canon(x) and int(x) < int(rec["k"]) for x in hs)

        def fset(rec, Dm):
            if rec["k"] is None:
                return False
            hs = [rec["h"]] if rec["h"] is not None else sorted(Dm["h"])
            return any(canon(x) and not int(x) < int(rec["k"]) for x in hs)
        return (Fac("hk", fin, marks="h"), "((h?, k): h >= k)", Fac("hk", fset, marks="h"))
    if name.startswith("!((h, m?)"):
        return (Fac("hm", lplain(jt(MLTH)), marks="m"), "((h, m?): m >= h)",
                Fac("hm", lplain(jt(lambda h, m: int(m) >= int(h))), marks="m"))
    lab = name[2]
    return (pool_one(lab, LT5, "<5", True, False)[1], "(%s?: !(<5))" % lab,
            pool_one(lab, lambda x: not LT5(x), "!(<5)", True, False)[1])


def rewrite(pool, recs, pop, labs, how):
    """the rev 22 pool: every `!` on a condition replaced by its complemented pattern ('pat') or its set complement
    ('set'); names keep their index so a rev 21 pair maps one to one"""
    vv, wrap = vw(recs)
    out = []
    for name, f in pool:
        if name.startswith("!(") and f.marks:
            fin, sname, fset = inner_of(name, recs)
            if how == "pat":
                out.append(("!q[%s]" % name[1:], compl(pop, labs, vv, [wrap(fin)])))
            else:
                out.append((sname, wrap(fset)))
        else:
            out.append((name, wrap(f)))
    return out


MAPPED = {}         # (old category, how) -> [pairs, still moving, smallest]
OLDN = {}
for pn, pop, recs, pool, labs in OLDP:
    vv, wrap = vw(recs)
    P0 = [(nm, wrap(f)) for nm, f in pool]
    PR = {how: rewrite(pool, recs, pop, labs, how) for how in ("pat", "set")}
    cache = {}

    def A_(pl, key, combo):
        k = (key, combo)
        if k not in cache:
            cache[k] = run(pop, labs, vv, [pl[i][1] for i in combo])[0]
        return cache[k]
    for n_ in (1, 2):
        for combo in itertools.combinations(range(len(pool)), n_):
            cats = {CAT(pool[i][0]) for i in combo} - {None}
            if not cats:
                continue
            for j in range(len(pool)):
                if j in combo:
                    continue
                c2 = tuple(sorted(combo + (j,)))
                a, b = A_(P0, "old", combo), A_(P0, "old", c2)
                if not any(not a[s] and b[s] for s in pop):
                    continue
                cat = "+".join(sorted(cats))
                OLDN[cat] = OLDN.get(cat, 0) + 1
                for how in ("pat", "set"):
                    a2, b2 = A_(PR[how], how, combo), A_(PR[how], how, c2)
                    d = [s for s in pop if not a2[s] and b2[s]]
                    e = MAPPED.setdefault((cat, how), [0, 0, None])
                    e[0] += 1
                    if d:
                        e[1] += 1
                        cand = (pn, " & ".join(PR[how][i][0] for i in combo), PR[how][j][0], sm(d))
                        e[2] = e[2] or cand
print("   (E1) predspec21's FAIL -> HOLD pairs under N1 (THE RULE), each re-run with every `!` on a condition rewritten:")
for cat in sorted(OLDN):
    print("      rev 21 kind %-15s %2d pairs: as complemented patterns still moving %2d%s; as set complements %2d%s" % (
        cat, OLDN[cat], MAPPED[(cat, "pat")][1], "" if not MAPPED[(cat, "pat")][2] else
        " (e.g. %s `%s` + `%s` on %r)" % MAPPED[(cat, "pat")][2], MAPPED[(cat, "set")][1],
        "" if not MAPPED[(cat, "set")][2] else " (e.g. %s `%s` + `%s` on %r)" % MAPPED[(cat, "set")][2]))
print("      total %d pairs (the brief's 22 = compound 19 + group 3; the mixed kinds compound+direct %d, compound+group %d"
      " also listed)" % (sum(OLDN.values()), OLDN.get("compound+direct", 0), OLDN.get("compound+group", 0)))

# (E2) every (program of 1-2 conditions, added condition) pair of the rev 22 pools: both rewrites side by side, the
# unmarked and defaulted group spellings added to the list pool; kinds read off the LARGER program
CAT22 = lambda nm: ("pattern" if nm.startswith("!q[") else "group-marked" if nm.startswith(("occurs.", "count")) and
                    "?" in nm else "group-unmarked" if nm.startswith(("occurs.", "count")) else None)
F22 = {}
TOTP = 0
for pn, pop, recs, pool, labs in OLDP:
    vv, wrap = vw(recs)
    pl = rewrite(pool, recs, pop, labs, "pat")
    seen = {nm for nm, _ in pl}
    for nm, f in rewrite(pool, recs, pop, labs, "set"):
        if nm not in seen:
            pl.append((nm, f))
            seen.add(nm)
    if recs is None:
        pl += [("occurs.none(((h, m): m >= h))", gnone(GE_, "plain")), ("occurs.none(((h, m = 0): m < h))",
                                                                         gnone(MLTH, "dflt"))]
    cache = {}

    def B_(combo):
        if combo not in cache:
            cache[combo] = run(pop, labs, vv, [pl[i][1] for i in combo])[0]
        return cache[combo]
    for n_ in (1, 2):
        for combo in itertools.combinations(range(len(pl)), n_):
            a = B_(combo)
            for j in range(len(pl)):
                if j in combo:
                    continue
                c2 = tuple(sorted(combo + (j,)))
                b = B_(c2)
                TOTP += 1
                kinds = {CAT22(pl[i][0]) for i in c2} - {None}
                key = "+".join(sorted(kinds)) or "none of these"
                e = F22.setdefault(key, [0, 0, None])
                e[0] += 1
                d = [s for s in pop if not a[s] and b[s]]
                if d:
                    e[1] += 1
                    cand = (pn, " & ".join(pl[i][0] for i in combo), pl[j][0], sm(d))
                    e[2] = e[2] or cand
print("   (E2) every (program, added condition) pair of the rev 22 pools: %d pairs over %d patterns" % (TOTP, len(OLDP)))
for key in sorted(F22):
    n_, mv, ex = F22[key]
    print("      kinds in the program %-36s %5d pairs, FAIL -> HOLD %3d%s" % (key, n_, mv, "" if not ex else
                                                                             "; smallest %s `%s` + `%s` on %r" % ex))

# =================================================================================================================
print("\nPART F: COMPLEMENTED PATTERNS IN THE CHAIN: well-founded, commutative, record = `&`")
# (F1) a complemented pattern consults no DOM of the outside: evaluate every one with the POISON DOM (raises on read)
nconsult = nq = 0
for pn, pop, recs, pool, labs in OLDP:
    for nm, f in rewrite(pool, recs, pop, labs, "pat"):
        if nm.startswith("!q["):
            nq += 1
            for s in pop:
                try:
                    f.fn(s, POISON)
                except Consult:
                    nconsult += 1
print("   (F1) %d complemented patterns x their subjects: an outside DOM consulted %d times (0 = no circularity: q's "
      "DOMs are computed from q alone, before the outside's)" % (nq, nconsult))
# (F2) orders: every program of 3 conditions holding a complemented pattern, all 6 orders, pattern A; and a NESTED one
pn, pop, recs, pool, labs = OLDP[0]
vv, wrap = vw(recs)
plA = rewrite(pool, recs, pop, labs, "pat")
ordn = progs = 0
for combo in itertools.combinations(range(len(plA)), 3):
    if not any(plA[i][0].startswith("!q[") for i in combo):
        continue
    progs += 1
    base_ = run(pop, labs, vv, [plA[i][1] for i in combo])[0]
    for perm in itertools.permutations(combo):
        a_ = run(pop, labs, vv, [plA[i][1] for i in perm])[0]
        ordn += sum(a_[s] != base_[s] for s in pop)
pA2 = dict(plA)
q1 = compl(pop, labs, vv, [wrap(inner_of("!((h?, k): h < k)", recs)[0])])
q2 = compl(pop, labs, vv, [q1, pA2["(h?: >7)"]])       # q2 := A & !q1 & (h?: >7)
nest = [q2, pA2["(k?: <5)"], pA2["(h?: <5)"]]
nb = run(pop, labs, vv, nest)[0]
nd = sum(run(pop, labs, vv, list(p))[0][s] != nb[s] for p in itertools.permutations(nest) for s in pop)
print("   (F2) pattern A: %d programs of 3 conditions holding a complemented pattern x 6 orders: %d answers differ; "
      "nested `A & !q2 & (k?: <5) & (h?: <5)`, q2 := A & !q1 & (h?: >7), q1 := A & ((h?, k): h < k): 6 orders, %d "
      "differ; on `b1`: %s" % (progs, ordn, nd, hfx(nb["b1"])))
# (F3) record = `&` with a complemented pattern in the chain: (RZ) `(h?: S, k: 3..7)` as ONE record condition vs two
# `&`-ed conditions, beside `!q`, q := RZ & (h: <5) (unmarked) and q := RZ & (h?: >7) (marked)
recf = lambda S: Fac("hk", lambda s, Dm: T37(RZ[s][0]) and (all(S(x) for x in RZ[s][1]) if RZ[s][1] else
                                                            any(S(d) for d in Dm["h"])), marks="h")
rsp = 0
for qn_, qin in (("(h: <5)", Fac("h", lambda s, Dm: bool(RZ[s][1]) and all(S5(x) for x in RZ[s][1]), marks="")),
                 ("(h?: >7)", hpass(GT7))):
    qq = compl(POP_RZ, ["h"], v_rz, [qin])
    for S in (S5, S59, GT7):
        r1_ = run(POP_RZ, ["h"], v_rz, [recf(S), qq])[0]
        r2_ = run(POP_RZ, ["h"], v_rz, [hpass(S), KF, qq])[0]
        rsp += sum(r1_[s] != r2_[s] for s in POP_RZ)
print("   (F3) (RZ), 1,110 subjects, three sets x two complemented patterns: record vs `&` split %d" % rsp)

# =================================================================================================================
print("\nPART G: THE CENSUS of every `!` written in a code span of the draft, rev 21 (03a2ce715) and this tree's rev 22")
import subprocess
CONDRX = re.compile(r"!(?:\(\(|\([a-z_.\[\]0-9]+\??(?: = [^:)]*)?:|some\(|c\b)")


def census(text):
    out = {"on a CONDITION": 0, "retired lex_ (record)": 0, "rx literal or withdrawn `!~`": 0, "on a SET or PATTERN": 0}
    spans = {}
    for sp in re.findall(r"`([^`\n]*)`", text):
        for m in re.finditer(r"!(?!=)", sp):
            rest = sp[m.start():]
            inlit = any(a.start() < m.start() < a.end() for a in re.finditer(r"/(?:\\.|[^/])+/", sp))
            if inlit or rest.startswith("!~"):
                k = "rx literal or withdrawn `!~`"
            elif rest.startswith("!lex_"):
                k = "retired lex_ (record)"
            elif CONDRX.match(rest):
                k = "on a CONDITION"
                spans[sp] = spans.get(sp, 0) + 1
            else:
                k = "on a SET or PATTERN"
            out[k] += 1
    return out, spans


r21 = subprocess.run(["git", "-C", HERE, "show", "03a2ce715:docs/design/predicates_draft.md"], capture_output=True,
                     text=True).stdout
r22 = open(os.path.join(HERE, "..", "..", "design", "predicates_draft.md")).read()
for tag, text in (("rev 21", r21), ("rev 22", r22)):
    c, sp = census(text)
    print("   %s: %s; %d distinct condition spans" % (tag, ", ".join("%s %d" % kv for kv in c.items()), len(sp)))
    if tag == "rev 21":
        for k, v in sorted(sp.items(), key=lambda kv: (-kv[1], kv[0])):
            print("      %2d  %s" % (v, k[:100]))

print("\nTOTAL (this script's own) engine-run cases %d differ %d; engine disagreements (cumulative) %d; probes %d" %
      (TOT["cases"] - T0["cases"], TOT["differ"] - T0["differ"], DIS[0], TOT["probes"] - T0["probes"]))
