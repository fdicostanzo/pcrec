# predspec21: evidence for docs/design/predicates_draft.md rev 21 and docs/dev/lanes/predspec21_report.md
# (lane predspec21, 2026-11-16; design only).
#
# THE QUESTION. The owner ruled domain-scope (COND-FAMILY, 16:31): DOM(h), the values a marked absent label "could have
# had", is read from the PROGRAM the condition meets (the regex with the conditions on it), not from the bare regex.
# Which conditions narrow a DOM, and how, is OPEN (the brief's item (i); the manager's rulings R1, R2 in the lane's
# rulings file). Six domains are computed side by side over the same populations; every program domain reads matches
# where h is PRESENT:
#   REGEX    the values h takes in some whole match of the REGEX (rev 20's VALUES; for `&` of rx, the defining operand)
#   SAME-NO  the brief's reading (i)-NO: every condition NOT naming h narrows; a greatest fixed point (marks on other
#            labels are consulted while a DOM is computed)
#   OWNER    R2 (i), the owner's question read literally: the regex narrowed by the UNMARKED conditions only
#   MANAGER  R2 (ii), the manager's lean: every condition narrows; where a mark would be consulted (its label absent)
#            the condition is TRANSPARENT; no DOM is read while a DOM is computed
#   LFP/GFP  R2 (iii)/(iv): every condition narrows, marks consulted; the least / greatest fixed point (iterated from
#            the empty set / from the regex's values; "no fixed point" = the iteration oscillates)
# A record's entries are separate `&`-ed conditions; a PRODUCT tuple set splits into its entries (record-is-product);
# a non-product joint set, or an entry reading `$h`, names h.
#
# PARTS: (1) THE PROGRAM DOMAIN: rev 20's tables (AR), (TM2), (RZ), (ZJ), (ZE), the two-spellings tables (2SP, SET),
#   review r29's equal-behaviour pairs (EB1 the branch-reset `q := P & (k: "b")` vs the narrowed regex; EB2 t2m vs t2x;
#   EB3 the extra `&` operand), R2's `(k?: "b")` pair (EBK), the mark under `!` (NEG), R1's independence and order
#   (INDEP), a search over small programs (SEARCH), then the four tests per domain. (2) ONE WITNESS: FIXIND-3's and FIXIND-6's populations
#   and a match-dependent pair, per domain; the fixed-point residue. (3) RECORD VERSUS JOINT WITH DOLLAR: every record
#   with an own-label `$` against its joint spelling, defaulted and marked, plus an ENGINE-RUN regex built from the
#   joint set. (4) the other counts rev 21 quotes (review r29's drills, recomputed here so the draft can cite one command).
# KINDS: RUN (whole match in libpcre2-8 AND Python `re`, which must agree; PCRE2 only where marked: branch reset);
#   COMPUTED (an answer from the stated rule over the run captures); ENGINE-RUN (an answer also built as a regex from the
#   stated set and run in both engines against the computed one).
# REUSE: absfold_check.py's prefix (which execs absimpact_check.py's engines groups()/whole()/check()/alt(), part(),
#   tup(), plain(); absfold's cond(), Z/U/P, count(), hfx()) is exec'd verbatim, as predspec20_check.py does. The
#   drills of PART 4 are review r29's critics' (fixind D2/D5/D6, ruling DRILL 1-4, simulate S1/S2), re-coded on these
#   engines with their populations unchanged.
# Run from the scratch dir: `timeout 300 python3 -I /abs/path/docs/dev/lanes/predspec21_check.py`.
# Sabotage: `PREDSPEC21_SABOTAGE=1` makes MANAGER skip the conditions naming h and makes the record read `$a` with its
#   own witness; the EB2 MANAGER split count and the record-vs-joint differ count must then be > 0.
import os, re, itertools, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "absfold_check.py")).read()
exec(_src[:_src.index('print("\\n(AR) THE RULE')], globals())     # absfold's prefix (+ absimpact's), verbatim
SAB21 = os.environ.get("PREDSPEC21_SABOTAGE") == "1"
if SAB21:
    print("SABOTAGE ON (PREDSPEC21_SABOTAGE=1)")
VARS = ("REGEX", "SAME-NO", "OWNER", "MANAGER", "LFP", "GFP")
NOTLT10 = lambda x: not (canon(x) and int(x) < 10)
S59 = lambda x: canon(x) and 5 <= int(x) <= 9


def pgroups(p, t, names):
    """PCRE2 only (branch reset): whole-match t; None or {name: text or None}"""
    c = _code(p)
    md = L.pcre2_match_data_create_from_pattern_8(c, None)
    rc = L.pcre2_match_8(c, t.encode(), len(t.encode()), 0, ANCH | ENDANCH, md, None)
    out = None
    if rc >= 0:
        ov = L.pcre2_get_ovector_pointer_8(md)
        out = {}
        for nm in names:
            k = L.pcre2_substring_number_from_name_8(c, nm.encode())
            out[nm] = None if ov[2 * k] == UNSET else t.encode()[ov[2 * k]:ov[2 * k + 1]].decode()
    L.pcre2_match_data_free_8(md)
    TOT["probes"] += 1
    return out


class Fac:
    """one `&`-ed condition of the flattened chain: the labels it names, the labels it MARKS (a `$x` reading a marked
    label of its own record counts: it reads the mark's witness), and fn(s, DOM) -> bool"""
    def __init__(self, names, fn, marks=None, negmark=False):
        self.names = frozenset(names)
        self.marks = frozenset(names[:1] if marks is None else marks)   # convention: the marked label is named first
        self.fn = fn
        self.negmark = negmark      # a mark under NEGATIVE polarity (`!`, occurs.none, an upper bound): rulings R4


class Consult(Exception):
    pass


class _Poison:
    def __iter__(self):
        raise Consult()


class _PoisonDom(dict):
    def __getitem__(self, k):
        return _Poison()


POISON = _PoisonDom()


def no_dom(f, s, transparent):
    """evaluate f on s without any DOM: a mark that would be consulted is TRANSPARENT (True) or a bug (raises)"""
    try:
        return f.fn(s, POISON)
    except Consult:
        if transparent:
            return True
        raise


def mk(v, S, dom):
    """one label's test: a present text is tested; an absent marked label holds when some value of DOM is in S (F1)"""
    return S(v) if v is not None else any(S(d) for d in dom)


class NoFixedPoint(Exception):
    pass


def doms(pop, labels, vals, facs, var):
    """DOM per label under one domain (dict label -> set); every program domain reads matches where h is PRESENT.
    REGEX    the regex's values (rev 20)
    SAME-NO  the brief's open reading (i)-NO: every condition NOT naming h applied; greatest fixed point
    OWNER    the owner's question, literal (R2 (i)): the regex narrowed by the UNMARKED conditions only; computed once
    MANAGER  R2 (ii), the manager's lean: every condition applied; a mark that would be consulted is transparent;
             computed once, no DOM read while a DOM is computed
    LFP/GFP  every condition applied, the least / greatest fixed point (R2 (iii), (iv))"""
    regex = {h: {v for s in pop for v in vals(s, h)} for h in labels}
    if var == "REGEX":
        return regex
    if var == "MGR-N2":
        # rulings R4 candidate N2: THE RULE (MANAGER) except that a condition holding a mark under NEGATIVE polarity is
        # TRANSPARENT while a DOM is computed, wherever its label stands (MANAGER itself is N1: it narrows where present)
        return {h: {v for s in pop if vals(s, h) and all(no_dom(f, s, True) for f in facs if not f.negmark)
                    for v in vals(s, h)} for h in labels}
    if var in ("OWNER", "MANAGER"):
        out = {}
        for h in labels:
            if var == "OWNER":
                keep = [f for f in facs if not f.marks]
            else:
                keep = [f for f in facs if not (SAB21 and h in f.names)]
            out[h] = {v for s in pop if vals(s, h) and all(no_dom(f, s, var == "MANAGER") for f in keep)
                      for v in vals(s, h)}
        return out

    def step(cur):
        new = {}
        for h in labels:
            keep = [f for f in facs if var != "SAME-NO" or h not in f.names]
            new[h] = {v for s in pop if vals(s, h) and all(f.fn(s, cur) for f in keep) for v in vals(s, h)}
        return new
    cur = {h: set() for h in labels} if var == "LFP" else {h: set(regex[h]) for h in labels}
    for _ in range(60):
        nxt = step(cur)
        if nxt == cur:
            return cur
        cur = nxt
    raise NoFixedPoint()


def answers(pop, labels, vals, facs, var):
    dm = doms(pop, labels, vals, facs, var)
    return {s: all(f.fn(s, dm) for f in facs) for s in pop}, dm


def sm(xs):
    return min(xs, key=lambda s: (len(s), s)) if xs else None


def cmp(title, pop, A, B, la, lb):
    d = [s for s in pop if A[s] != B[s]]
    ex = sm(d)
    print("   %-70s differ %5d of %6d%s" % (title, len(d), len(pop), "" if ex is None else "   smallest %r (%s %s, %s %s)"
                                          % (ex, la, hfx(A[ex]), lb, hfx(B[ex]))))
    return len(d)


def dstr(d):
    return "".join(sorted(d, key=lambda s: (len(s), s))) if all(len(x) == 1 for x in d) else \
        "%d values" % len(d)


MOVES = []          # (table, variant, n, total, smallest, REGEX answer there)
WIT = {v: 0 for v in VARS}       # (i)
SPL = {v: 0 for v in VARS}       # (ii)
SETS = {v: 0 for v in VARS}      # (iii)
RAMP = {v: 0 for v in VARS}      # (iv)


def run_table(title, pop, labels, vals, facs, show=None, tally=True):
    """answers per domain; the moves against REGEX; (i) SELF-CONSISTENCY: a subject HOLDS but FAILS when every DOM is
    replaced by the values the label holds in the matches this same domain ACCEPTS (a value never held witnessed it)"""
    res = {}
    for v in VARS:
        res[v] = answers(pop, labels, vals, facs, v)
    print("   %s: DOM %s" % (title, "; ".join("%s %s" % (v, " ".join("%s={%s}" % (h, dstr(res[v][1][h])) for h in labels))
                                            for v in VARS)))
    mv = []
    for v in VARS[1:]:
        d = [s for s in pop if res[v][0][s] != res["REGEX"][0][s]]
        if tally:
            MOVES.append((title, v, len(d), len(pop), sm(d), res["REGEX"][0].get(sm(d)) if d else None))
        if d:
            mv.append("%s %d (smallest %r: REGEX %s, %s %s)" % (v, len(d), sm(d), hfx(res["REGEX"][0][sm(d)]), v,
                                                                 hfx(res[v][0][sm(d)])))
    print("      vs REGEX over %d subjects: %s" % (len(pop), "; ".join(mv) if mv else "0 move under every program domain"))
    for v in VARS:
        held = {h: {x for s in pop if res[v][0][s] for x in vals(s, h)} for h in labels}
        w = [s for s in pop if res[v][0][s] and not all(f.fn(s, held) for f in facs)]
        WIT[v] += len(w) if tally else 0
    if show:
        for s in show:
            print("      on %-8r %s" % (s, "  ".join("%s %s" % (v, hfx(res[v][0][s])) for v in VARS)))
    return res


# =================================================================================================================
print("PART 1: THE PROGRAM DOMAIN")
print("\n(AR) table (AR)'s marked cells on a concrete pattern /(?<h>\\d)?-(?<k>\\d)/ (110 subjects; h absent on `-k`)")
P_AR = r"(?<h>\d)?-(?<k>\d)"
POP_AR = [h + "-" + k for h in [""] + D for k in D]
G_AR = {s: groups(P_AR, s, ["h", "k"]) for s in POP_AR}
v_ar = lambda s, lab: [G_AR[s][lab]] if G_AR[s][lab] is not None else []
hv = lambda s: G_AR[s]["h"]
kv = lambda s: G_AR[s]["k"]
AR_SHAPES = [
    ("one (h?: <5)", [Fac("h", lambda s, Dm: mk(hv(s), S5, Dm["h"]))]),
    ("one (h?: !(<10))", [Fac("h", lambda s, Dm: mk(hv(s), NOTLT10, Dm["h"]))]),
    ("record (h?: <5, k: 3..7)", [Fac("h", lambda s, Dm: mk(hv(s), S5, Dm["h"])), Fac("k", lambda s, Dm: T37(kv(s)), marks="")]),
    ("record (h?: !(<10), k: 3..7)", [Fac("h", lambda s, Dm: mk(hv(s), NOTLT10, Dm["h"])),
                                      Fac("k", lambda s, Dm: T37(kv(s)), marks="")]),
    ("joint ((h?, k): >= (5, 3))", [Fac("hk", lambda s, Dm: any(canon(x) and (int(x), int(kv(s))) >= (5, 3) for x in
                                                               ([hv(s)] if hv(s) is not None else Dm["h"])))]),
]
for title, facs in AR_SHAPES:
    run_table(title, POP_AR, ["h"], v_ar, facs, show=["-6"])

# -----------------------------------------------------------------------------------------------------------------
print("\n(TM2) t2 := /(?<h>\\d{1,2})(?::(?<m>\\d\\d))?/, 11,110 subjects; R = padded(>= (9, 30)), office = padded(between("
      "(9, 0), (17, 0)))")
H = [str(i) for i in range(10)] + ["%02d" % i for i in range(100)]
M = ["%02d" % i for i in range(100)]
P_T2 = r"(?<h>\d{1,2})(?::(?<m>\d\d))?"
POP_T2 = H + [h + ":" + m for h in H for m in M]
G_T2 = {s: groups(P_T2, s, ["h", "m"]) for s in POP_T2}
v_t2 = lambda s, lab: [G_T2[s][lab]] if G_T2[s][lab] is not None else []
GE930 = lambda t: num(t[0]) and num(t[1]) and (int(t[0]), int(t[1])) >= (9, 30)
OFFICE = lambda t: num(t[0]) and num(t[1]) and (9, 0) <= (int(t[0]), int(t[1])) <= (17, 0)


def jm(Rf):
    return [Fac("hm", lambda s, Dm: any(Rf((G_T2[s]["h"], x)) for x in
                                        ([G_T2[s]["m"]] if G_T2[s]["m"] is not None else Dm["m"])))]


for title, Rf in (("((h, m?): R)", GE930), ("((h, m?): !R)", lambda t: not GE930(t)),
                  ("((h, m?): !office)", lambda t: not OFFICE(t))):
    run_table(title, POP_T2, ["m"], v_t2, jm(Rf), show=["9", "10"])

# -----------------------------------------------------------------------------------------------------------------
print("\n(RZ) /(?<k>\\d)(?:;(?<h>\\d))*/, 1,110 subjects: (h?: S, k: 3..7) as the record (tuples, cond()) and as `&`")
P_RZ = r"(?<k>\d)(?:;(?<h>\d))*"
POP_RZ = [k + "".join(";" + h for h in hs) for k in D for n in range(3) for hs in itertools.product(D, repeat=n)]
for s in POP_RZ:
    assert whole(P_RZ, s)
RZ = {s: (s.split(";")[0], s.split(";")[1:]) for s in POP_RZ}
v_rz = lambda s, lab: RZ[s][1] if lab == "h" else [RZ[s][0]]


def hpass(S):
    return Fac("h", lambda s, Dm: all(S(x) for x in RZ[s][1]) if RZ[s][1] else any(S(d) for d in Dm["h"]))


KF = Fac("k", lambda s, Dm: T37(RZ[s][0]), marks="")
for sname, S in (("<5", S5), ("5..9", S59), ("!(<10)", NOTLT10)):
    facs = [hpass(S), KF]
    res = run_table("(h?: %s, k: 3..7)" % sname, POP_RZ, ["h"], v_rz, facs, show=["3", "9"])
    for v in VARS:
        dh = sorted(res[v][1]["h"])
        rec = {s: cond(AR, [(h, RZ[s][0]) for h in RZ[s][1]] or [(Z, RZ[s][0])], lambda t, S=S: S(t[0]) and T37(t[1]),
                       [dh, D], (0,)) for s in POP_RZ}
        amp = {s: plain(AR, RZ[s][1], S, dh, mark=True) and T37(RZ[s][0]) for s in POP_RZ}
        RAMP[v] += cmp("record (tuples) vs & [%s]" % v, POP_RZ, rec, amp, "rec", "&")

# -----------------------------------------------------------------------------------------------------------------
print("\n(ZJ) jcfold2's non-product sets on (RZ)'s pattern, h MARKED (one joint condition naming h and k); answers on "
      "the 10 zero-pass subjects")
ZJS = [
    ("((h?, k): >= (5, 3))", lambda t: canon(t[0]) and (int(t[0]), int(t[1])) >= (5, 3)),
    ("((h?, k): (0|1|2, 3|4) | (5, 5))", lambda t: (t[0] in ("0", "1", "2") and t[1] in "34") or t == ("5", "5")),
    ("((h?, k): (\"x\", 3) | (0, 5))", lambda t: t == ("x", "3") or t == ("0", "5")),
    ("((h?, k): < (0, 3))", lambda t: canon(t[0]) and (int(t[0]), int(t[1])) < (0, 3)),
]
ZS = [s for s in POP_RZ if ";" not in s]
for name, Rf in ZJS:
    f = Fac("hk", lambda s, Dm, Rf=Rf: all(Rf((h, RZ[s][0])) for h in RZ[s][1]) if RZ[s][1] else
            any(Rf((d, RZ[s][0])) for d in Dm["h"]))
    res = run_table(name, POP_RZ, ["h"], v_rz, [f])
    print("      zero-pass subjects HOLDING: " + "  ".join("%s %s" % (v, "".join(s for s in ZS if res[v][0][s]))
                                                       for v in VARS))

# -----------------------------------------------------------------------------------------------------------------
print("\n(ZE) /(?<a>\\d)-(?<k>\\d)(?:;(?<h>\\d))*/, 11,100 subjects, the set empty through $a; h MARKED")
P_ZE = r"(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*"
POP_ZE = ["%s-%s" % (a, k) + "".join(";" + h for h in hs) for a in D for k in D for n in range(3)
          for hs in itertools.product(D, repeat=n)]
ZE = {}
for s in POP_ZE:
    head, *hs = s.split(";")
    a, k = head.split("-")
    ZE[s] = (a, k, hs)
v_ze = lambda s, lab: ZE[s][2] if lab == "h" else [ZE[s][0 if lab == "a" else 1]]
C1h = Fac("ha", lambda s, Dm: all(canon(x) and int(x) < int(ZE[s][0]) for x in ZE[s][2]) if ZE[s][2] else
          any(canon(d) and int(d) < int(ZE[s][0]) for d in Dm["h"]))
C1k = Fac("k", lambda s, Dm: ZE[s][1] == "3", marks="")
C2f = lambda t, a: canon(t[0]) and canon(t[1]) and (int(t[0]), int(t[1])) < (int(a), 0)
C2 = Fac("hka", lambda s, Dm: all(C2f((x, ZE[s][1]), ZE[s][0]) for x in ZE[s][2]) if ZE[s][2] else
         any(C2f((d, ZE[s][1]), ZE[s][0]) for d in Dm["h"]))
r1 = run_table("C1 (h?: <$a, k: 3)", POP_ZE, ["h"], v_ze, [C1h, C1k], show=["0-3", "5-3"])
r2 = run_table("C2 ((h?, k): < ($a, 0))", POP_ZE, ["h"], v_ze, [C2], show=["0-3", "5-3"])
A0 = [s for s in POP_ZE if s.startswith("0-")]
for v in VARS:
    SETS[v] += cmp("a = 0, both spellings EMPTY: C1 vs C2 [%s]" % v, A0, r1[v][0], r2[v][0], "C1", "C2")
    dh = sorted(r1[v][1]["h"])
    rec = {s: cond(AR, [(x, ZE[s][1]) for x in ZE[s][2]] or [(Z, ZE[s][1])],
                   lambda t, a=ZE[s][0]: canon(t[0]) and int(t[0]) < int(a) and t[1] == "3", [dh, D], (0,))
           for s in POP_ZE}
    amp = {s: plain(AR, ZE[s][2], lambda x, a=ZE[s][0]: canon(x) and int(x) < int(a), dh, mark=True) and ZE[s][1] == "3"
           for s in POP_ZE}
    RAMP[v] += cmp("C1 record (tuples) vs (h?: <$a) & (k: 3) [%s]" % v, POP_ZE, rec, amp, "rec", "&")

# -----------------------------------------------------------------------------------------------------------------
print("\n(2SP) two spellings of one pattern (absfix's P1-P3), (h?: 5..9, k: 3..7), the 310 matching (RZ) subjects")
SP2 = [("P1", r"(?<k>\d)(?:;(?<h>\d)(?<=[0-4]))*"), ("P2", r"(?<k>\d)(?:;(?<h>[0-4]))*"),
       ("P3", r"(?<k>\d)(?:;(?=[0-4])(?<h>\d))*")]
POP_2 = [s for s in POP_RZ if whole(SP2[0][1], s)]
assert all(whole(p, s) for _, p in SP2 for s in POP_2) and len(POP_2) == 310
r2sp = {n: run_table(n + " " + p, POP_2, ["h"], v_rz, [hpass(S59), KF]) for n, p in SP2}
for v in VARS:
    for n in ("P1", "P3"):
        SPL[v] += cmp("%s vs P2 [%s]" % (n, v), POP_2, r2sp[n][v][0], r2sp["P2"][v][0], n, "P2")
print("   (the three spellings' REGEX DOMs are equal here: h's VALUES, not its group text; rev 20's GROUP split is absfix's)")

# -----------------------------------------------------------------------------------------------------------------
print("\n(SET) two spellings of one set, and two sets equal on every holdable value; (RZ)")
L04 = lambda x: x in ("0", "1", "2", "3", "4")
LT0 = lambda x: canon(x) and int(x) < 0
for a_, b_, la, lb, tgt in ((S5, L04, "<5", "0|1|2|3|4", SETS), (LT0, NOTLT10, "<0", "!(<10)", None)):
    ra = run_table("(h?: %s)" % la, POP_RZ, ["h"], v_rz, [hpass(a_)])
    rb = run_table("(h?: %s)" % lb, POP_RZ, ["h"], v_rz, [hpass(b_)])
    for v in VARS:
        n = cmp("(h?: %s) vs (h?: %s) [%s]" % (la, lb, v), POP_RZ, ra[v][0], rb[v][0], la, lb)
        if tgt is not None:
            tgt[v] += n
print("   (both `(h?: <0)` and `(h?: !(<10))` are a constant set disjoint from \\d: by §5.2 a compile ERROR, not FAILS)")

# -----------------------------------------------------------------------------------------------------------------
print("\n(EB1) review r29's branch-reset pair: P = /(?|(?<k>a)(?:;(?<h>\\d))*|(?<k>b)(?:;(?<h>[5-9]))*)/ (PCRE2 only), "
      "Q2 = /(?<k>b)(?:;(?<h>[5-9]))*/; 222 subjects")
P_BR = r"(?|(?<k>a)(?:;(?<h>\d))*|(?<k>b)(?:;(?<h>[5-9]))*)"
Q2 = r"(?<k>b)(?:;(?<h>[5-9]))*"
POP_BR = [k + "".join(";" + h for h in hs) for k in "ab" for n in range(3) for hs in itertools.product(D, repeat=n)]
GP = {s: pgroups(P_BR, s, ["k"]) for s in POP_BR}
GQ = {s: groups(Q2, s, ["k"]) for s in POP_BR}
same_q = sum(((GP[s] is not None and GP[s]["k"] == "b") == (GQ[s] is not None)) for s in POP_BR)
print("   `P & (k: \"b\")` and Q2 accept the same subjects (h's passes read off the subject) on %d of %d" %
      (same_q, len(POP_BR)))
BRK = {s: (s[0], s.split(";")[1:]) for s in POP_BR}


def br_vals(G):
    return lambda s, lab: ([] if G[s] is None else (BRK[s][1] if lab == "h" else [BRK[s][0]]))


hb = lambda S: Fac("h", lambda s, Dm: all(S(x) for x in BRK[s][1]) if BRK[s][1] else any(S(d) for d in Dm["h"]))
kb = Fac("k", lambda s, Dm: BRK[s][0] == "b", marks="")
mP = Fac("", lambda s, Dm: GP[s] is not None)
mQ = Fac("", lambda s, Dm: GQ[s] is not None)
eb = {}
eb["A  P & (k: \"b\") & (h?: <5)"] = run_table("A  P & (k: \"b\") & (h?: <5)", POP_BR, ["h"], br_vals(GP),
                                                [mP, kb, hb(S5)], show=["b"])
eb["B  Q2 & (h?: <5)"] = run_table("B  Q2 & (h?: <5)", POP_BR, ["h"], br_vals(GQ), [mQ, hb(S5)], show=["b"])
for v in VARS:
    SPL[v] += cmp("A vs B (Bq = A by binding, L2) [%s]" % v, POP_BR, eb["A  P & (k: \"b\") & (h?: <5)"][v][0],
                  eb["B  Q2 & (h?: <5)"][v][0], "A", "B")
# the record, its joint product spelling (split, record-is-product), and the joint left UNSPLIT (a condition naming h)
jprod_unsplit = Fac("hk", lambda s, Dm: all(BRK[s][0] == "b" and S5(x) for x in BRK[s][1]) if BRK[s][1] else
                    any(BRK[s][0] == "b" and S5(d) for d in Dm["h"]))
rC = run_table("C  P & (h?: <5, k: \"b\")  [= ((k, h?): (\"b\", <5)), the product split]", POP_BR, ["h"], br_vals(GP),
               [mP, hb(S5), kb], show=["b"])
rJ = run_table("J  P & ((k, h?): (\"b\", <5)) left UNSPLIT (a control, not a reading; not tallied)", POP_BR, ["h"],
               br_vals(GP), [mP, jprod_unsplit], show=["b"], tally=False)
for v in VARS:
    RAMP[v] += cmp("C record vs A `&` [%s]" % v, POP_BR, rC[v][0], eb["A  P & (k: \"b\") & (h?: <5)"][v][0], "C", "A")
    cmp("C record vs J the joint product UNSPLIT [%s] (record-is-product needs the split)" % v, POP_BR, rC[v][0],
        rJ[v][0], "C", "J")
run_table("P & (h?: <5)  (anywhere, 16:13)", POP_BR, ["h"], br_vals(GP), [mP, hb(S5)], show=["b"])
o1 = Fac("hk", lambda s, Dm: all((BRK[s][0] == "a" and S5(x)) or (BRK[s][0] == "b" and not S5(x)) for x in BRK[s][1])
         if BRK[s][1] else any((BRK[s][0] == "a" and S5(d)) or (BRK[s][0] == "b" and not S5(d)) for d in Dm["h"]))
run_table("P & ((k, h?): (\"a\", <5) | (\"b\", >=5))  (the 16:13 example)", POP_BR, ["h"], br_vals(GP), [mP, o1],
          show=["b"])
o2 = Fac("hk", lambda s, Dm: all(BRK[s][0] == "a" and S5(x) for x in BRK[s][1]) if BRK[s][1] else
         any(BRK[s][0] == "a" and S5(d) for d in Dm["h"]))
run_table("P & ((k, h?): (\"a\", <5))  (the 16:13 example)", POP_BR, ["h"], br_vals(GP), [mP, o2], show=["b"])

# -----------------------------------------------------------------------------------------------------------------
print("\n(EB2) review r29's t2m := t2 & (m?: padded(<60)) vs t2x := /(?<h>\\d{1,2})(?::(?<m>[0-5]\\d))?/, then "
      "& (m?: padded(>=60)); 11,110 subjects")
T2X = r"(?<h>\d{1,2})(?::(?<m>[0-5]\d))?"
G_TX = {s: groups(T2X, s, ["h", "m"]) for s in POP_T2}
pl60 = lambda v: re.fullmatch(r"0*(?:[0-9]|[1-5][0-9])", v) is not None
pg60 = lambda v: re.fullmatch(r"0*(?:[6-9][0-9]|[1-9][0-9]{2,})", v) is not None
mT2 = lambda S: Fac("m", lambda s, Dm: mk(G_T2[s]["m"], S, Dm["m"]))
mTX = lambda S: Fac("m", lambda s, Dm: G_TX[s] is not None and mk(G_TX[s]["m"], S, Dm["m"]))
v_tx = lambda s, lab: [] if G_TX[s] is None or G_TX[s][lab] is None else [G_TX[s][lab]]
t2m = run_table("t2m = t2 & (m?: padded(<60))", POP_T2, ["m"], v_t2, [mT2(pl60)], show=["9"])
t2x = run_table("t2x", POP_T2, ["m"], v_tx, [Fac("", lambda s, Dm: G_TX[s] is not None)], show=["9"])
for v in VARS:
    cmp("t2m vs t2x as programs (same subjects, same labels expected) [%s]" % v, POP_T2, t2m[v][0], t2x[v][0], "t2m",
        "t2x")
eA = run_table("t2m & (m?: padded(>=60))", POP_T2, ["m"], v_t2, [mT2(pl60), mT2(pg60)], show=["9"])
eB = run_table("t2x & (m?: padded(>=60))", POP_T2, ["m"], v_tx, [mTX(pg60)], show=["9"])
EB2N = {}
for v in VARS:
    EB2N[v] = cmp("t2m & (m?: padded(>=60)) vs t2x & (m?: padded(>=60)) [%s]" % v, POP_T2, eA[v][0], eB[v][0], "t2m",
                  "t2x")
    SPL[v] += EB2N[v]

# -----------------------------------------------------------------------------------------------------------------
print("\n(EB3) review r29's AND-DEAD: /(?:(?<h>\\d|zz))?x/ & /[^z]*/ vs /(?:(?<h>\\d))?x/, then & (h?: \"zz\"); "
      "subjects over {1,z,x} to length 4")
PZ = r"(?:(?<h>\d|zz))?x"
PI = r"(?=[^z]*\z)(?:(?<h>\d|zz))?x"      # the intersection, run as one pattern (the label-free operand as a lookahead)
P3 = r"(?:(?<h>\d))?x"
POP_Z = ["".join(c) for n in range(5) for c in itertools.product("1zx", repeat=n)]
GZ = {s: groups(PZ, s, ["h"]) for s in POP_Z}
GI = {s: groups(PI, s, ["h"]) for s in POP_Z}
G3 = {s: groups(P3, s, ["h"]) for s in POP_Z}
print("   the chain and P3: same subjects and labels on %d of %d" % (sum(GI[s] == G3[s] for s in POP_Z), len(POP_Z)))
ZZ = lambda x: x == "zz"
# REGEX for the chain = the DEFINING operand's values (PZ); the program domains read the chain's matches (PI)
v_pz = lambda s, lab: [] if GZ[s] is None or GZ[s]["h"] is None else [GZ[s]["h"]]
v_pi = lambda s, lab: [] if GI[s] is None or GI[s]["h"] is None else [GI[s]["h"]]
v_p3 = lambda s, lab: [] if G3[s] is None or G3[s]["h"] is None else [G3[s]["h"]]
regdom = {v for s in POP_Z for v in v_pz(s, "h")}
chainA = {}
for v in VARS:
    dom_ = regdom if v == "REGEX" else doms(POP_Z, ["h"], v_pi, [Fac("h", lambda s, Dm: GI[s] is not None and
                                                                     mk(GI[s]["h"], ZZ, Dm["h"]))], v)["h"]
    chainA[v] = {s: GI[s] is not None and mk(GI[s]["h"], ZZ, dom_) for s in POP_Z}
r3 = run_table("P3 & (h?: \"zz\")", POP_Z, ["h"], v_p3, [Fac("h", lambda s, Dm: G3[s] is not None and
                                                              mk(G3[s]["h"], ZZ, Dm["h"]))], show=["x"])
print("   chain & (h?: \"zz\") on `x`: " + "  ".join("%s %s" % (v, hfx(chainA[v]["x"])) for v in VARS) +
      "   (REGEX = the defining operand's values {%s})" % ",".join(sorted(regdom)))
for v in VARS:
    n = cmp("chain vs P3 under (h?: \"zz\") [%s]" % v, POP_Z, chainA[v], r3[v][0], "chain", "P3")
    SPL[v] += n
    if v == "REGEX":
        WIT[v] += sum(1 for s in POP_Z if chainA[v][s] and not r3[v][0][s])

# -----------------------------------------------------------------------------------------------------------------
print("\n(EBK) rulings R2: `P & (k?: \"b\") & (h?: <5)` vs `P & (k: \"b\") & (h?: <5)` (k is never absent in P, so the two "
      "programs behave alike); the branch-reset P of EB1")
kbm = Fac("k", lambda s, Dm: BRK[s][0] == "b")          # (k?: "b"): k is never absent in P, so no DOM is consulted
rKM = run_table("K? P & (k?: \"b\") & (h?: <5)", POP_BR, ["h"], br_vals(GP), [mP, kbm, hb(S5)], show=["b"])
for v in VARS:
    SPL[v] += cmp("K? vs A  P & (k: \"b\") & (h?: <5) [%s]" % v, POP_BR, rKM[v][0],
                  eb["A  P & (k: \"b\") & (h?: <5)"][v][0], "k?", "k")

# -----------------------------------------------------------------------------------------------------------------
print("\n(NEG) a mark under `!` (rev 20 §0.1 L30, L95): the condition's own complement is one of the program's "
      "conditions, so the domains that narrow by it read DOM(h) without S")
P_N = r"(?<h>\d)?x"
POP_N = ["x"] + [d + "x" for d in D]
GN = {s: groups(P_N, s, ["h"]) for s in POP_N}
v_n = lambda s, lab: [GN[s]["h"]] if GN[s]["h"] is not None else []
run_table("L30 !(h?: <5) on /(?<h>\\d)?x/", POP_N, ["h"], v_n, [Fac("h", lambda s, Dm: not mk(GN[s]["h"], S5, Dm["h"]))],
          show=["x"], tally=False)
run_table("L30 (h?: !(<5)) on /(?<h>\\d)?x/", POP_N, ["h"], v_n, [Fac("h", lambda s, Dm: mk(GN[s]["h"], lambda x: not
                                                                                            S5(x), Dm["h"]))],
          show=["x"], tally=False)
run_table("L95 !((h, m?): R) on t2", POP_T2, ["m"], v_t2, [Fac("m", lambda s, Dm: not jm(GE930)[0].fn(s, Dm))],
          show=["9"], tally=False)
run_table("L95 ((h, m?): !R) on t2", POP_T2, ["m"], v_t2, jm(lambda t: not GE930(t)), show=["9"], tally=False)

# -----------------------------------------------------------------------------------------------------------------
print("\n(INDEP) rulings R1 (a): `b` against P & (k: \"b\"), P & (h?: <5) and P & (k: \"b\") & (h?: <5), per domain")
for v in VARS:
    a1 = answers(POP_BR, ["h"], br_vals(GP), [mP, kb], v)[0]["b"]
    a2 = answers(POP_BR, ["h"], br_vals(GP), [mP, hb(S5)], v)[0]["b"]
    a3 = answers(POP_BR, ["h"], br_vals(GP), [mP, kb, hb(S5)], v)[0]["b"]
    print("   [%-7s] P & (k: \"b\") %s   P & (h?: <5) %s   P & (k: \"b\") & (h?: <5) %s   -> the intersection of the "
          "first two %s" % (v, hfx(a1), hfx(a2), hfx(a3), "= the third" if (a1 and a2) == a3 else "!= the third"))
# order and grouping: DOM reads the SET of conditions of the flattened chain, so neither can enter; the run checks the
# six orders of EB1's three conditions and the binding `q := P & (k: "b"); q & (h?: <5)` (the same set, L2)
ordn = 0
for v in VARS:
    base = answers(POP_BR, ["h"], br_vals(GP), [mP, kb, hb(S5)], v)[0]
    for perm in itertools.permutations([mP, kb, hb(S5)]):
        a_ = answers(POP_BR, ["h"], br_vals(GP), list(perm), v)[0]
        ordn += sum(a_[s] != base[s] for s in POP_BR)
print("   order: the 6 orders of EB1's three conditions x %d domains x %d subjects: %d differ (by construction: DOM reads "
      "the chain's SET of conditions)" % (len(VARS), len(POP_BR), ordn))

# -----------------------------------------------------------------------------------------------------------------
print("\n(SEARCH) every program of 1-3 conditions from a small pool, on three patterns: where the candidate domains "
      "answer differently (the smallest program and subject each), where ADDING a condition turns a FAIL into a HOLD, "
      "and where the fixed-point iteration finds no fixed point")
LT5 = lambda x: canon(x) and int(x) < 5
GT7 = lambda x: canon(x) and int(x) > 7


def pool_one(lab, S, sname, marked, neg):
    nm = ("!" if neg else "") + "(%s%s: %s)" % (lab, "?" if marked else "", sname)

    def fn(rec, Dm):
        v = rec[lab]
        r = S(v) if v is not None else (any(S(d) for d in Dm[lab]) if marked else False)
        return (not r) if neg else r
    return nm, Fac(lab, fn, marks=lab if marked else "", negmark=bool(neg and marked))


def pool_joint():
    def fn(rec, Dm):
        hs = [rec["h"]] if rec["h"] is not None else sorted(Dm["h"])
        ks = [rec["k"]] if rec["k"] is not None else sorted(Dm["k"])
        return any(canon(x) and canon(y) and int(x) < int(y) for x in hs for y in ks)
    return "((h?, k?): h < k)", Fac("hk", fn, marks="hk")


def pool_njoint():
    def fn(rec, Dm):
        if rec["k"] is None:
            return True                       # k unmarked: the inner condition fails, so `!` holds
        hs = [rec["h"]] if rec["h"] is not None else sorted(Dm["h"])
        return not any(canon(x) and int(x) < int(rec["k"]) for x in hs)
    return "!((h?, k): h < k)", Fac("hk", fn, marks="h", negmark=True)


POOLS = []
for pname, pat, pop, kvals in (("A", r"a(?<h>\d)|b(?<k>\d)|c", ["a" + d for d in D] + ["b" + d for d in D] + ["c"], None),
                               ("B", r"(?<h>\d)?-(?<k>\d)?", [h + "-" + k for h in [""] + D for k in [""] + D], None)):
    recs = {s: groups(pat, s, ["h", "k"]) for s in pop}
    pool = [pool_one(lab, S, sn, mkd, False) for lab in "hk" for S, sn in ((LT5, "<5"), (GT7, ">7")) for mkd in
            (False, True)] + [pool_one(lab, LT5, "<5", True, True) for lab in "hk"] + [pool_joint(), pool_njoint()]
    POOLS.append((pname, pat, pop, recs, pool))
recs_br = {s: {"k": BRK[s][0], "h": (BRK[s][1][0] if BRK[s][1] else None)} for s in POP_BR
           if GP[s] is not None and len(BRK[s][1]) <= 1}
pool_br = [("(k: \"b\")", Fac("k", lambda rec, Dm: rec["k"] == "b", marks="")),
           ("(k?: \"b\")", Fac("k", lambda rec, Dm: mk(rec["k"], lambda x: x == "b", Dm["k"]), marks="k")),
           pool_one("h", LT5, "<5", False, False), pool_one("h", LT5, "<5", True, False),
           pool_one("h", GT7, ">7", True, False), pool_one("h", LT5, "<5", True, True)]
POOLS.append(("P", P_BR + " (0-1 passes)", sorted(recs_br), recs_br, pool_br))
DIFF = {}          # (v1, v2) -> (count of programs, smallest (size, pattern, program, subject, a1, a2))
F2H = {v: [0, None] for v in VARS}
F2HPOS = {v: [0, 0] for v in VARS}     # pairs with no mark under `!`: [pairs checked, FAIL -> HOLD]
NOFP = {v: [0, None] for v in VARS}
NPROG = 0
for pname, pat, pop, recs, pool in POOLS:
    vrec = lambda s, lab, recs=recs: [recs[s][lab]] if recs[s][lab] is not None else []
    ans = {}
    for n in (1, 2, 3):
        for combo in itertools.combinations(range(len(pool)), n):
            NPROG += 1
            facs = [Fac(pool[i][1].names, (lambda f: (lambda s, Dm: f.fn(recs[s], Dm)))(pool[i][1]),
                        marks=pool[i][1].marks, negmark=pool[i][1].negmark) for i in combo]
            for v in VARS:
                try:
                    ans[(combo, v)] = answers(pop, ["h", "k"], vrec, facs, v)[0]
                except NoFixedPoint:
                    ans[(combo, v)] = None
                    NOFP[v][0] += 1
                    NOFP[v][1] = NOFP[v][1] or (pname, " & ".join(pool[i][0] for i in combo))
    for (combo, v), a in ans.items():
        if a is None:
            continue
        for v2 in VARS:
            if VARS.index(v2) <= VARS.index(v) or ans.get((combo, v2)) is None:
                continue
            b = ans[(combo, v2)]
            d = [s for s in pop if a[s] != b[s]]
            if d:
                key = (v, v2)
                cnt, best = DIFF.get(key, (0, None))
                cand = (len(combo), pname, " & ".join(pool[i][0] for i in combo), sm(d), hfx(a[sm(d)]), hfx(b[sm(d)]))
                DIFF[key] = (cnt + 1, cand if best is None or cand[:1] + (len(cand[3]),) < best[:1] + (len(best[3]),)
                             else best)
        if len(combo) <= 2:
            for j in range(len(pool)):
                if j in combo:
                    continue
                c2 = tuple(sorted(combo + (j,)))
                b = ans.get((c2, v))
                if b is None:
                    continue
                d = [s for s in pop if not a[s] and b[s]]
                if not any(pool[i][0].startswith("!") and pool[i][1].marks for i in c2):
                    F2HPOS[v][0] += 1
                    F2HPOS[v][1] += bool(d)
                if d:
                    F2H[v][0] += 1
                    cand = (len(c2), pname, " & ".join(pool[i][0] for i in combo), pool[j][0], sm(d))
                    if F2H[v][1] is None or (cand[0], len(cand[4])) < (F2H[v][1][0], len(F2H[v][1][4])):
                        F2H[v][1] = cand
print("   %d programs over %d patterns (A = /%s/, B = /%s/, P = %s)" % (NPROG, len(POOLS), POOLS[0][1], POOLS[1][1],
                                                                       POOLS[2][1]))
for v1, v2 in itertools.combinations(VARS, 2):
    cnt, best = DIFF.get((v1, v2), (0, None))
    print("   %-7s vs %-7s: %4d programs answer differently%s" % (v1, v2, cnt, "" if best is None else
                                                                  "; smallest: pattern %s, `%s` on %r (%s %s, %s %s)" %
                                                                  (best[1], best[2], best[3], v1, best[4], v2, best[5])))
for v in VARS:
    print("   [%-7s] no mark under `!`: adding a condition turns a FAIL into a HOLD in %d of %d (program, added "
          "condition) pairs" % (v, F2HPOS[v][1], F2HPOS[v][0]))
for v in VARS:
    print("   [%-7s] adding a condition turns a FAIL into a HOLD in %d (program, added condition) pairs%s; no fixed point "
          "in %d programs%s" % (v, F2H[v][0], "" if F2H[v][1] is None else "; smallest: pattern %s, `%s` + `%s` on %r" %
                                F2H[v][1][1:], NOFP[v][0], "" if NOFP[v][1] is None else "; e.g. %s `%s`" % NOFP[v][1]))

# -----------------------------------------------------------------------------------------------------------------
print("\n(NEGPOL) rulings R4: a mark under NEGATIVE polarity (`!` on a marked condition, `!` over a compound holding "
      "one, a group question that counts a mark downward). Two candidates for what THE RULE does with such a condition "
      "while a DOM is computed: N1 it narrows where its marked label is PRESENT, as the filter it is (= MANAGER above); "
      "N2 it is TRANSPARENT (no narrowing at all). Unmarked negated conditions narrow as filters under both.")
NEGV = (("N1", "MANAGER"), ("N2", "MGR-N2"))


def prog_ans(pop, labels, vals, facs, var):
    return answers(pop, labels, vals, facs, var)


# (1a) `!` directly on a marked condition: the manager's R4 witness on the branch-reset P
pb = dict(pool_br)
vbr = lambda s, lab: [recs_br[s][lab]] if recs_br[s][lab] is not None else []
wrapb = lambda f: Fac(f.names, (lambda s, Dm: f.fn(recs_br[s], Dm)), marks=f.marks, negmark=f.negmark)
popb = sorted(recs_br)
for v in ("REGEX",) + tuple(x[1] for x in NEGV):
    a1, d1 = prog_ans(popb, ["h", "k"], vbr, [wrapb(pb["!(h?: <5)"])], v)
    a2, d2 = prog_ans(popb, ["h", "k"], vbr, [wrapb(pb["(k: \"b\")"]), wrapb(pb["!(h?: <5)"])], v)
    print("   [%-7s] P & !(h?: <5) on `b`: DOM(h)={%s} %s;   P & (k: \"b\") & !(h?: <5) on `b`: DOM(h)={%s} %s%s" %
          (v, dstr(d1["h"]), hfx(a1["b"]), dstr(d2["h"]), hfx(a2["b"]),
           "   -> FAIL to HOLD by adding (k: \"b\")" if not a1["b"] and a2["b"] else ""))

# (1b) `!` over a compound: pattern A, `!((h?, k): h < k)` then + `(h?: >7)`, on `b1`
pA = dict(POOLS[0][4])
recA = POOLS[0][3]
vA = lambda s, lab: [recA[s][lab]] if recA[s][lab] is not None else []
wrapA = lambda f: Fac(f.names, (lambda s, Dm: f.fn(recA[s], Dm)), marks=f.marks, negmark=f.negmark)
for v in ("REGEX",) + tuple(x[1] for x in NEGV):
    a1, d1 = prog_ans(POOLS[0][2], ["h", "k"], vA, [wrapA(pA["!((h?, k): h < k)"])], v)
    a2, d2 = prog_ans(POOLS[0][2], ["h", "k"], vA, [wrapA(pA["!((h?, k): h < k)"]), wrapA(pA["(h?: >7)"])], v)
    print("   [%-7s] A & !((h?, k): h < k) on `b1`: DOM(h)={%s} %s;   + (h?: >7): DOM(h)={%s} %s%s" %
          (v, dstr(d1["h"]), hfx(a1["b1"]), dstr(d2["h"]), hfx(a2["b1"]),
           "   -> FAIL to HOLD" if not a1["b1"] and a2["b1"] else ""))

# (1c) group questions with a mark inside, over a looped label: LST := /(?:(?<h>\d)(?::(?<m>\d))?,)*/, the lists of
# 0-2 items from h in {1, 6}, m in {absent, 2, 7}; each list's passes read item by item from the engine
LST = r"(?:(?<h>\d)(?::(?<m>\d))?,)*"
ITM = r"(?<h>\d)(?::(?<m>\d))?,"
its = [h + ("" if m is None else ":" + m) + "," for h in ("1", "6") for m in (None, "2", "7")]
POPL = ["".join(c) for k in range(3) for c in itertools.product(its, repeat=k)]
PS = {}
for s in POPL:
    assert whole(LST, s)
    PS[s] = [(g["h"], g["m"]) for g in (groups(ITM, x + ",", ["h", "m"]) for x in s.split(",")[:-1])]
vL = lambda s, lab: [m for h, m in PS[s] if m is not None] if lab == "m" else [h for h, m in PS[s]]


def pv(ps, f, Dm):
    """per pass, F1 on an absent marked m; a pass whose test would consult a DOM is SKIPPED while a DOM is computed"""
    out = []
    for h, m in ps:
        try:
            out.append(f(h, m, Dm))
        except Consult:
            pass
    return out


def jt(R):
    return lambda h, m, Dm: R(h, m) if m is not None else any(R(h, d) for d in Dm["m"])


MLTH = lambda h, m: int(m) < int(h)
LT5m = lambda h, m: int(m) < 5
GT5m = lambda h, m: int(m) > 5


def lplain(f):
    def fn(s, Dm):
        ps = PS[s]
        if not ps:
            return False            # h unmarked: absent on zero passes
        r = pv(ps, f, Dm)
        return all(r)
    return fn


def lmark1(S):
    def fn(s, Dm):
        ps = PS[s]
        if not ps:
            return any(S("0", d) for d in Dm["m"])     # zero passes: m absent once, F1
        return all(pv(ps, jt(S), Dm))
    return fn


poolL = [
    ("occurs.none(((h, m?): m < h))", Fac("hm", lambda s, Dm: not any(pv(PS[s], jt(MLTH), Dm)), marks="m", negmark=True)),
    ("occurs.at_most(1, ((h, m?): m < h))", Fac("hm", lambda s, Dm: sum(pv(PS[s], jt(MLTH), Dm)) <= 1, marks="m",
                                                 negmark=True)),
    ("!((h, m?): m < h)", Fac("hm", (lambda f: lambda s, Dm: not f(s, Dm))(lplain(jt(MLTH))), marks="m", negmark=True)),
    ("some(((h, m?): m < h))", Fac("hm", lambda s, Dm: any(pv(PS[s], jt(MLTH), Dm)), marks="m")),
    ("((h, m?): m < h)", Fac("hm", lplain(jt(MLTH)), marks="m")),
    ("(m?: <5)", Fac("m", lmark1(LT5m), marks="m")),
    ("(m?: >5)", Fac("m", lmark1(GT5m), marks="m")),
    ("(h: <5)", Fac("h", lambda s, Dm: bool(PS[s]) and all(int(h) < 5 for h, m in PS[s]), marks="")),
]
CAT = lambda name: ("group" if name.startswith(("occurs.", "count")) else "compound" if name.startswith("!((") else
                    "direct" if name.startswith("!(") else None)
NEGPOOLS = [("A", POOLS[0][2], POOLS[0][3], POOLS[0][4], ["h", "k"]),
            ("B", POOLS[1][2], POOLS[1][3], POOLS[1][4], ["h", "k"]),
            ("P", POOLS[2][2], POOLS[2][3], POOLS[2][4], ["h", "k"]),
            ("LST", POPL, None, poolL, ["m"])]
F2HN = {}          # (the negative-polarity kinds the program holds, candidate) -> [pairs, smallest]
for pname, pop, recs, pool, labs in NEGPOOLS:
    if recs is None:
        vv, wrap = vL, (lambda f: f)
    else:
        vv = (lambda recs: lambda s, lab: [recs[s][lab]] if recs[s][lab] is not None else [])(recs)
        wrap = (lambda recs: lambda f: Fac(f.names, (lambda s, Dm: f.fn(recs[s], Dm)), marks=f.marks,
                                          negmark=f.negmark))(recs)
    for _, v in NEGV:
        cache = {}

        def A_(combo):
            if combo not in cache:
                cache[combo] = prog_ans(pop, labs, vv, [wrap(pool[i][1]) for i in combo], v)[0]
            return cache[combo]
        for n in (1, 2):
            for combo in itertools.combinations(range(len(pool)), n):
                cats = {CAT(pool[i][0]) for i in combo} - {None}
                if not cats:
                    continue
                a = A_(combo)
                for j in range(len(pool)):
                    if j in combo:
                        continue
                    b = A_(tuple(sorted(combo + (j,))))
                    d = [s for s in pop if not a[s] and b[s]]
                    if d:
                        for c in ("+".join(sorted(cats)),):
                            e = F2HN.setdefault((c, v), [0, None])
                            e[0] += 1
                            cand = (n, len(sm(d)), pname, " & ".join(pool[i][0] for i in combo), pool[j][0], sm(d))
                            if e[1] is None or cand[:2] < e[1][:2]:
                                e[1] = cand
for c in ("direct", "compound", "group"):
    for _, v in NEGV:
        F2HN.setdefault((c, v), [0, None])
for (c, v), (n, best) in sorted(F2HN.items()):
    print("   [%-7s] FAIL to HOLD by adding a condition, the program's negative-polarity marks only %-15s: %3d pairs%s" %
          (v, c, n, "" if best is None else "; smallest: pattern %s, `%s` + `%s` on %r" % best[2:]))
# the R4 witness under N2 also covers the positive-polarity question: does a program with NO negative-polarity mark ever
# move FAIL -> HOLD under N2? (under N1 = MANAGER: 0 of 698, (SEARCH))
n2pos = [0, 0]
for pname, pop, recs, pool, labs in NEGPOOLS[:3]:
    vv = (lambda recs: lambda s, lab: [recs[s][lab]] if recs[s][lab] is not None else [])(recs)
    wrap = (lambda recs: lambda f: Fac(f.names, (lambda s, Dm: f.fn(recs[s], Dm)), marks=f.marks,
                                      negmark=f.negmark))(recs)
    posi = [i for i in range(len(pool)) if not pool[i][1].negmark]
    for n in (1, 2):
        for combo in itertools.combinations(posi, n):
            a = prog_ans(pop, labs, vv, [wrap(pool[i][1]) for i in combo], "MGR-N2")[0]
            for j in posi:
                if j in combo:
                    continue
                b = prog_ans(pop, labs, vv, [wrap(pool[i][1]) for i in sorted(combo + (j,))], "MGR-N2")[0]
                n2pos[0] += 1
                n2pos[1] += any(not a[s] and b[s] for s in pop)
print("   [MGR-N2 ] no negative-polarity mark: FAIL to HOLD in %d of %d (program, added condition) pairs" %
      (n2pos[1], n2pos[0]))
# (1d) the draft's own compound example, L95: t2 & !((h, m?): R) on `9`, then + (m?: padded(<30))
l95 = Fac("m", lambda s, Dm: not jm(GE930)[0].fn(s, Dm), negmark=True)
m30 = Fac("m", lambda s, Dm: mk(G_T2[s]["m"], lambda x: num(x) and int(x) < 30, Dm["m"]))
for v in ("REGEX",) + tuple(x[1] for x in NEGV):
    a1, d1 = prog_ans(POP_T2, ["m"], v_t2, [l95], v)
    a2, d2 = prog_ans(POP_T2, ["m"], v_t2, [l95, m30], v)
    print("   [%-7s] L95 t2 & !((h, m?): R) on `9`: DOM(m)={%s} %s;   + (m?: padded(<30)): DOM(m)={%s} %s" %
          (v, dstr(d1["m"]), hfx(a1["9"]), dstr(d2["m"]), hfx(a2["9"])))
# (2) the list witnesses, both candidates, on the smallest subject each
for nm_ in ("occurs.none(((h, m?): m < h))",):
    f0 = dict(poolL)[nm_]
    for v in ("REGEX",) + tuple(x[1] for x in NEGV):
        a1, d1 = prog_ans(POPL, ["m"], vL, [f0], v)
        a2, d2 = prog_ans(POPL, ["m"], vL, [f0, dict(poolL)["(m?: >5)"]], v)
        print("   [%-7s] LST & %s on `6,`: DOM(m)={%s} %s;   + (m?: >5): DOM(m)={%s} %s" %
              (v, nm_, dstr(d1["m"]), hfx(a1["6,"]), dstr(d2["m"]), hfx(a2["6,"])))

# -----------------------------------------------------------------------------------------------------------------
print("\n(MOVES) the answers that move from REGEX, per table and domain (the smallest witness each)")
for t, v, n, tot, ex, regans in MOVES:
    if n:
        print("   %-62s %-10s %5d of %6d  smallest %r (REGEX %s)" % (t[:62], v, n, tot, ex, hfx(regans)))
print("   every other table: 0 move under every program domain")

print("\n(SUMMARY) per domain: (i) an answer witnessed only by a value the label never holds in a match the same domain "
      "accepts (self-consistency); (ii) two spellings of one program split (2SP, EB1 A/B, EKB k?/k, EB2, EB3); (iii) two "
      "spellings of one set split (SET <5, ZE a = 0); (iv) record = & (RZ, ZE, EB1 C/A); WELL-FOUNDED = computed once, no "
      "DOM read while a DOM is computed")
for v in VARS:
    print("   %-7s (i) %-3s %4d   (ii) %-3s %4d   (iii) %-3s %d   (iv) %s (%d split)   well-founded: %s" %
          (v, "YES" if WIT[v] else "no", WIT[v], "YES" if SPL[v] else "no", SPL[v], "YES" if SETS[v] else "no", SETS[v],
           "KEPT" if RAMP[v] == 0 else "BROKEN", RAMP[v],
           {"REGEX": "yes (no program read)", "SAME-NO": "no (a fixed point)", "OWNER": "yes", "MANAGER": "yes",
            "LFP": "no (a fixed point)", "GFP": "no (a fixed point)"}[v]))

# =================================================================================================================
print("\nPART 2: ONE WITNESS")
print("\n(W3) FIXIND-3: `(h?: <5) & (h?: >5)` as two conditions, each its own witness (PER-CONDITION), vs one witness "
      "for both (SHARED, = the joined `(h?: <5 & >5)`'s answer; the joined spelling with constant sets is a §5.2 ERROR)")
A5 = lambda x: canon(x) and int(x) < 5
B5 = lambda x: canon(x) and int(x) > 5
for P, pop, loop in ((r"(?<h>\d)?x", ["x"] + [d + "x" for d in D], False),
                     (r"(?:(?<h>\d),)*", ["".join(d + "," for d in c) for k in range(3) for c in
                                          itertools.product(D, repeat=k)], True)):
    if loop:
        PS = {s: [x for x in s.split(",") if x] for s in pop}
        for s in pop:
            assert whole(P, s)
    else:
        PS = {s: [x for x in [groups(P, s, ["h"])["h"]] if x is not None] for s in pop}
    vv = lambda s, lab: PS[s]
    fA = Fac("h", lambda s, Dm, A=A5: all(A(x) for x in PS[s]) if PS[s] else any(A(d) for d in Dm["h"]))
    fB = Fac("h", lambda s, Dm, B=B5: all(B(x) for x in PS[s]) if PS[s] else any(B(d) for d in Dm["h"]))
    for v in VARS:
        top = doms(pop, ["h"], vv, [fA, fB], v)
        per = {s: fA.fn(s, top) and fB.fn(s, top) for s in pop}
        sha = {s: all(A5(x) and B5(x) for x in PS[s]) if PS[s] else any(A5(d) and B5(d) for d in top["h"])
               for s in pop}
        cmp("%-18s DOM(h)={%s} PER-CONDITION vs SHARED [%s]" % (P, dstr(top["h"]), v), pop, per, sha, "per", "shared")

print("\n(W6) FIXIND-6: /(?<a>\\d)?-(?<b>\\d)/, 110 subjects: `$a` reads the tuple's own a (SHARED, the "
      "default-reaches-dollar derivation) vs its own witness (INDEPENDENT) vs no reach (`$a` empty)")
POP_E = [a + "-" + b for a in [""] + D for b in D]
GE = {s: groups(r"(?<a>\d)?-(?<b>\d)", s, ["a", "b"]) for s in POP_E}
v_e = lambda s, lab: [GE[s][lab]] if GE[s][lab] is not None else []
for name, Sa in (("(a?: <3, b: >$a)", lambda x: int(x) < 3), ("(a?: >7, b: >$a)", lambda x: int(x) > 7)):
    fa = Fac("a", lambda s, Dm, Sa=Sa: mk(GE[s]["a"], Sa, Dm["a"]))
    fb = Fac("ab", lambda s, Dm: any(int(GE[s]["b"]) > int(x) for x in ([GE[s]["a"]] if GE[s]["a"] is not None else
                                                                       Dm["a"])))
    for v in VARS:
        top = doms(POP_E, ["a"], v_e, [fa, fb], v)["a"]
        sh, ind, nr = {}, {}, {}
        for s in POP_E:
            a, b = GE[s]["a"], int(GE[s]["b"])
            if a is not None:
                sh[s] = ind[s] = nr[s] = Sa(a) and b > int(a)
            else:
                sh[s] = any(Sa(d) and b > int(d) for d in top)
                ind[s] = any(Sa(d) for d in top) and any(b > int(d) for d in top)
                nr[s] = False
        print("   %-18s [%-10s] DOM(a)={%s} holds: shared %d, independent %d, no-reach %d of %d" %
              (name, v, dstr(top), sum(sh.values()), sum(ind.values()), sum(nr.values()), len(POP_E)))
        cmp("      shared vs independent [%s]" % v, POP_E, sh, ind, "shared", "indep")

print("\n(WX) a MATCH-DEPENDENT pair on one label: two conditions whose sets read other labels")
for P, pop, conds in (
        (r"(?<h>\d)?-(?<k>\d)", [h + "-" + k for h in [""] + D for k in D],
         (("(h?: <$k)", lambda x, g: int(x) < int(g["k"]), "hk"), ("(h?: >$k)", lambda x, g: int(x) > int(g["k"]), "hk"))),
        (r"(?<j>\d)(?<h>\d)?(?<k>\d)", [j + h + k for j in D for h in [""] + D for k in D],
         (("(h?: <$k)", lambda x, g: int(x) < int(g["k"]), "hk"), ("(h?: >$j)", lambda x, g: int(x) > int(g["j"]), "hj")))):
    names = ["h", "k"] + (["j"] if "<j>" in P else [])
    G = {s: groups(P, s, names) for s in pop}
    vv = lambda s, lab, G=G: [G[s][lab]] if G[s][lab] is not None else []
    f1 = Fac(conds[0][2], lambda s, Dm, G=G, c=conds[0][1]: (lambda h: c(h, G[s]) if h is not None else
                                                                 any(c(d, G[s]) for d in Dm["h"]))(G[s]["h"]))
    f2 = Fac(conds[1][2], lambda s, Dm, G=G, c=conds[1][1]: (lambda h: c(h, G[s]) if h is not None else
                                                                 any(c(d, G[s]) for d in Dm["h"]))(G[s]["h"]))
    for v in VARS:
        top = doms(pop, ["h"], vv, [f1, f2], v)
        per = {s: f1.fn(s, top) and f2.fn(s, top) for s in pop}
        sha = {s: (conds[0][1](G[s]["h"], G[s]) and conds[1][1](G[s]["h"], G[s])) if G[s]["h"] is not None else
               any(conds[0][1](d, G[s]) and conds[1][1](d, G[s]) for d in top["h"]) for s in pop}
        cmp("/%s/ %s & %s DOM(h)={%s} PER-CONDITION vs SHARED [%s]" % (P, conds[0][0], conds[1][0], dstr(top["h"]), v),
            pop, per, sha, "per", "shared")

print("\n(FP) the well-foundedness witness: /a(?<h>\\d)|b(?<k>\\d)/ & (h?: <5) & (k?: <5); each mark's DOM is read over "
      "matches where the OTHER mark is consulted")
P_FP = r"a(?<h>\d)|b(?<k>\d)"
POP_FP = ["a" + d for d in D] + ["b" + d for d in D]
GF_ = {s: groups(P_FP, s, ["h", "k"]) for s in POP_FP}
v_fp = lambda s, lab: [GF_[s][lab]] if GF_[s][lab] is not None else []
ffh = Fac("h", lambda s, Dm: mk(GF_[s]["h"], S5, Dm["h"]))
ffk = Fac("k", lambda s, Dm: mk(GF_[s]["k"], S5, Dm["k"]))
rfp = run_table("(h?: <5) & (k?: <5)", POP_FP, ["h", "k"], v_fp, [ffh, ffk], show=["a0", "b9"], tally=False)
cmp("LFP vs GFP", POP_FP, rfp["LFP"][0], rfp["GFP"][0], "LFP", "GFP")

# =================================================================================================================
print("\nPART 3: RECORD VERSUS JOINT WITH DOLLAR (own-label `$a`; defaulted and marked), per domain")
LIT = [a + "-" + b for a in [""] + D for b in ("0", "3", "5", "9")]
POP_L = ["".join(i + "," for i in its) for n in range(3) for its in itertools.product(LIT, repeat=n)]
P_L = r"(?:(?<a>\d)?-(?<b>\d),)*"
for s in POP_L:
    assert whole(P_L, s)
PASSES = {}
for s in POP_E:
    PASSES[("E", s)] = [(GE[s]["a"], GE[s]["b"])]
for s in POP_L:
    PASSES[("L", s)] = [((it.split("-")[0] or None), it.split("-")[1]) for it in s.split(",")[:-1]]
RECS = [
    ("(a = 0: <10, b: >$a)", lambda x: int(x) < 10, lambda y, x: int(y) > int(x), "0", False),
    ("(a = 5: <3, b: >$a)", lambda x: int(x) < 3, lambda y, x: int(y) > int(x), "5", False),
    ("(a = 7: <10, b: ==$a)", lambda x: int(x) < 10, lambda y, x: y == x, "7", False),
    ("(a?: <3, b: >$a)", lambda x: int(x) < 3, lambda y, x: int(y) > int(x), None, True),
    ("(a?: >7, b: >$a)", lambda x: int(x) > 7, lambda y, x: int(y) > int(x), None, True),
    ("(a?: <10, b: ==$a)", lambda x: int(x) < 10, lambda y, x: y == x, None, True),
]


def rec_slot(passes, Sa, Tb, dflt, marked, dom):
    """THE RECORD, the derivation: the default fills a's ONE slot and `$a` reads the slot; the mark: some slot value
    from DOM(a) passes both entries (sabotage: `$a` takes its own witness)"""
    for a, b in passes:
        if a is not None:
            ok = Sa(a) and Tb(b, a)
        elif dflt is not None:
            ok = Sa(dflt) and Tb(b, dflt)
        elif marked:
            ok = (any(Sa(d) for d in dom) and any(Tb(b, d) for d in dom)) if SAB21 else \
                any(Sa(d) and Tb(b, d) for d in dom)
        else:
            ok = False
        if not ok:
            return False
    return True


def joint_gf(passes, Rset, dflt, marked, dom):
    """THE JOINT `((a, b): {(x, y): ...})`: the general form, a candidate set per absent label, some choice in R"""
    for a, b in passes:
        cand = [a] if a is not None else ([dflt] if dflt is not None else (sorted(dom) if marked else []))
        if not any((x, b) in Rset for x in cand):
            return False
    return True


RJN = {v: [0, 0] for v in VARS}
for name, Sa, Tb, dflt, marked in RECS:
    Rset = {(x, y) for x in D for y in D if Sa(x) and Tb(y, x)}       # the tuple set, enumerated over a's and b's digits
    for v in VARS:
        out = []
        for tag, pop, vals_ in (("E", POP_E, lambda s: PASSES[("E", s)]), ("L", POP_L, lambda s: PASSES[("L", s)])):
            fac = Fac("ab", lambda s, Dm, vals_=vals_: rec_slot(vals_(s), Sa, Tb, dflt, marked, Dm["a"]),
                      marks="a" if marked else "")
            vv = lambda s, lab, vals_=vals_: [a for a, _ in vals_(s) if a is not None]
            dom_ = doms(pop, ["a"], vv, [fac], v)["a"]
            ra = {s: rec_slot(vals_(s), Sa, Tb, dflt, marked, dom_) for s in pop}
            ja = {s: joint_gf(vals_(s), Rset, dflt, marked, dom_) for s in pop}
            n = sum(ra[s] != ja[s] for s in pop)
            RJN[v][0] += len(pop)
            RJN[v][1] += n
            # ENGINE-RUN: a regex built from the JOINT set (each pass an alternative), run against the record's answer
            item = []
            for x in D:
                ys = [y for y in D if (x, y) in Rset]
                if ys:
                    item.append(x + "-" + alt(ys))
            absent_ys = [y for y in D if any((c, y) in Rset for c in
                                             ([dflt] if dflt is not None else (sorted(dom_) if marked else [])))]
            if absent_ys:
                item.append("-" + alt(absent_ys))
            body = "(?:" + "|".join(item) + ")" if item else "(?!)"
            rx = body if tag == "E" else "(?:" + body + ",)*"
            for s in pop:
                check("record vs joint %s %s %s" % (name, tag, v), rx, s, ra[s])
            ex = sm([s for s in pop if ra[s] != ja[s]])
            out.append("%s %d/%d%s DOM(a)={%s}" % (tag, n, len(pop), "" if ex is None else " e.g. %r" % ex, dstr(dom_)))
        print("   %-22s [%-10s] record vs joint differ: %s" % (name, v, "; ".join(out)))
print("   on `-5`: (a = 0: <10, b: >$a) %s (the default fills $a: 5 > 0); (a?: <3, b: >$a) %s; (a?: >7, b: >$a) %s" % (
    hfx(rec_slot([(None, "5")], RECS[0][1], RECS[0][2], "0", False, [])),
    hfx(rec_slot([(None, "5")], RECS[3][1], RECS[3][2], None, True, D)),
    hfx(rec_slot([(None, "5")], RECS[4][1], RECS[4][2], None, True, D))))
for v in VARS:
    print("   TOTAL [%-10s] record vs joint: %d of %d differ" % (v, RJN[v][1], RJN[v][0]))

# =================================================================================================================
print("\nPART 4: the other counts rev 21 quotes (review r29's drills, recomputed)")
# fixind D2: "every hit, possibly none" vs (g?: "a") over occurrences(/(?<g>a)?b/)
SUB = ["".join(c) for k in range(7) for c in itertools.product("ab", repeat=k)]
hc = re.compile(py(r"(?<g>a)?b"))
hits = lambda s: [m.group("g") for m in hc.finditer(s)]
DOMg = {v for s in SUB for v in hits(s) if v is not None}
nm_, nn_ = 0, 0
for s in SUB:
    hs = hits(s)
    natural = all(v == "a" for v in hs)
    mark = all((v == "a") if v is not None else ("a" in DOMg) for v in hs) if hs else ("a" in DOMg)
    none_ = not any((v != "a") if v is not None else True for v in hs)
    nm_ += natural != mark
    nn_ += none_ != natural
    check("D2 natural", r"(?!b)(?![ab]*bb)[ab]*", s, natural)
    check("D2 mark", r"[ab]*", s, mark)
print("   (D2) occurrences(/(?<g>a)?b/), %d spans over {a,b} to length 6, DOM(g) = %s: 'every hit\\'s g is a, possibly "
      "none' vs (g?: \"a\") differ %d (e.g. 'b', 'abb'); vs occurs.none(!(g: \"a\")) differ %d" % (len(SUB), sorted(DOMg),
                                                                                                 nm_, nn_))
# fixind D5: the closing example over 1,111 lists
POPO = r"(?:(?<h>\d+)(?::(?<m>\d\d))?,)*"
ITEMS = [(h, m) for h in ("3", "12") for m in (None, "15", "45", "05", "99")]
SUBO = ["".join("%s%s," % (h, "" if m is None else ":" + m) for h, m in its) for k in range(4)
        for its in itertools.product(ITEMS, repeat=k)]
DOMm = {"%02d" % i for i in range(100)}
for rname, Rm in (("R = (<10, <30)", lambda v: int(v) < 30), ("R' = (<10, padded(<100))", lambda v: int(v) < 100)):
    cm, cp, ex = 0, 0, []
    for s in SUBO:
        ps = [(x.split(":")[0], x.split(":")[1] if ":" in x else None) for x in s.split(",") if x]
        inR = lambda h, m: int(h) < 10 and Rm(m)
        want = all(m is not None and inR(h, m) for h, m in ps)
        marked = not any((not inR(h, m)) if m is not None else any(not inR(h, d) for d in DOMm) for h, m in ps)
        plainnot = not any((m is None) or not inR(h, m) for h, m in ps)
        cm += marked != want
        cp += plainnot != want
        if marked != want and len(ex) < 2:
            ex.append(s)
    print("   (D5) %-26s over %d lists: occurs.none(((h, m?): !R)) vs wanted %d %s; occurs.none(!((h, m): R)) %d" %
          (rname, len(SUBO), cm, ex, cp))
    # the same marked form under THE RULE (mark-narrows, the variant): the condition narrows DOM(m) through the
    # passes where m is PRESENT (an ordinary filter there: no such pass has its tuple outside R), so DOM(m) = the
    # minutes some h < 10 pairs with inside R; the passes with m absent are transparent while DOM is computed
    DOMv = {d for d in DOMm if Rm(d)}
    cv, exv = 0, []
    for s in SUBO:
        ps = [(x.split(":")[0], x.split(":")[1] if ":" in x else None) for x in s.split(",") if x]
        inR = lambda h, m: int(h) < 10 and Rm(m)
        want = all(m is not None and inR(h, m) for h, m in ps)
        markedv = not any((not inR(h, m)) if m is not None else any(not inR(h, d) for d in DOMv) for h, m in ps)
        cv += markedv != want
        if markedv != want and len(exv) < 2:
            exv.append(s)
    print("   (D5) %-26s under the RULE (program DOM, DOM(m) = %d values): occurs.none(((h, m?): !R)) vs wanted %d %s" %
          (rname, len(DOMv), cv, exv))
# fixind D6: an array alternative lacking the label
PX = r"(?<x>\d)|(?<y>[a-z])"
SUBX = D + [chr(c) for c in range(97, 123)]
DOMx6 = {groups(PX, s, ["x"])["x"] for s in SUBX if groups(PX, s, ["x"])["x"] is not None}
inS = lambda t: re.fullmatch("[0-5]", t) is not None
unm = sum(1 for s in SUBX if groups(PX, s, ["x"])["x"] is not None and inS(groups(PX, s, ["x"])["x"]))
keep = sum(1 for s in SUBX if mk(groups(PX, s, ["x"])["x"], inS, DOMx6))
print("   (D6) [x = /\\d/, y = /[a-z]/] & (x?: /[0-5]/) as /%s/, %d subjects: unmarked %d, marked (absent x) %d, the "
      "entry DROPPED %d" % (PX, len(SUBX), unm, keep, unm))
# ruling DRILL 1: a `*` loop that can run at most once by meaning vs the `?` spelling
P1, P2 = r"(?<k>\d)?-(?<h>\d)?", r"(?:(?<k>\d)(?=-))*-(?:(?<h>\d)(?!\d))*"
n = dm = dc = 0
for L_ in range(0, 5):
    for tp in itertools.product("059-a", repeat=L_):
        t = "".join(tp)
        n += 1
        a, b = groups(P1, t, ["k", "h"]), groups(P2, t, ["k", "h"])
        dm += (a is None) != (b is None)
        dc += a is not None and b is not None and a != b
print("   (LOOP) /%s/ vs /%s/: %d subjects, match differ %d, capture differ %d" % (P1, P2, n, dm, dc))
# ruling DRILL 2: same captures, different pass sequences
n = da = dc = 0
ex = None
for L_ in range(1, 4):
    for tp in itertools.product("0379", repeat=L_):
        t = "".join(tp)
        n += 1
        a, b = groups(r"(?<n>\d)+", t, ["n"]), groups(r"\d*(?<n>\d)", t, ["n"])
        dc += a != b
        if all(int(x) < 5 for x in t) != (int(t[-1]) < 5):
            da += 1
            ex = ex or t
print("   (SEQ) /(?<n>\\d)+/ vs /\\d*(?<n>\\d)/: %d subjects, PCRE-reported captures differ %d; (n: <5) by the sequence "
      "rule differs on %d (first %r; '993': %s)" % (n, dc, da, ex, all(int(x) < 5 for x in "993") != (int("3") < 5)))
# ruling DRILL 3: `50;`
P5 = r"(?<k>\d+);(?:(?<n>\d),)*"
DOMn = [d for d in D if whole(P5, "0;%s," % d)]
print("   (50;) /%s/ on '50;': n absent, k = %s; DOM(n) = %s; values > 50: %s -> (n?: >$k) / all((n: >$k)) FAILS" %
      (P5, groups(P5, "50;", ["k"])["k"], "".join(DOMn), [d for d in DOMn if int(d) > 50]))
# ruling DRILL 4 + V4: a finite S against a backreference DOM; DEFINE never sets its group
print("   (BREF) 'aaba' in DOM(h) of /(?<h>(?<a>a+)b\\k<a>)?x/: %s (run on the group); so (h?: \"aaba\") FAILS exactly" %
      whole(r"(?<a>a+)b(?P=a)", "aaba"))
gd = [pgroups(r"(?(DEFINE)(?<o>\d{1,3}))(?&o)\.(?&o)", t, ["o"]) for t in ("1.2", "192.168")]
print("   (DEFINE) /(?(DEFINE)(?<o>\\d{1,3}))(?&o)\\.(?&o)/ on '1.2', '192.168': o = %s, %s (PCRE2 only): DOM(o) = {}" %
      (gd[0]["o"], gd[1]["o"]))
# simulate S1: whole vs searched for the t2 controls
DOMM = sorted({G_T2[s]["m"] for s in POP_T2 if G_T2[s]["m"]})
late = lambda h, m: (int(h), int(m)) >= (9, 30)


def c_s1(g, mode):
    h, m = g["h"], g["m"]
    if m is not None:
        return late(h, m)
    return False if mode == "plain" else (any(late(h, v) for v in DOMM) if mode == "mark" else late(h, "0"))


def searched(s, mode):
    for st in range(len(s)):
        for e in range(len(s), st, -1):
            g = pgroups(P_T2, s[st:e], ["h", "m"])
            if g is not None and c_s1(g, mode):
                return s[st:e], st
    return None


for mode in ("plain", "mark", "def0"):
    d = [s for s in POP_T2 if c_s1(G_T2[s], mode) != (searched(s, mode) is not None)]
    print("   (S1) t2 & ((h, m%s): padded(>= (9, 30))) whole vs SEARCHED differ on %d of %d%s" % (
        {"plain": "", "mark": "?", "def0": " = 0"}[mode], len(d), len(POP_T2), "" if not d else ", e.g. %r -> %r" %
        (d[0], searched(d[0], mode))))
print("   (S1) on '9:15': " + "  ".join("%s %s" % (m, searched("9:15", m)) for m in ("plain", "mark", "def0")))
# simulate S2 PRIORITY-DEAD
SUBP = ["".join(c) for k in range(8) for c in itertools.product("abx", repeat=k)]
dpd = sum(groups(r"(?:(?<h>a|ab)(?<k>b*))?x", s, ["h", "k"]) != groups(r"(?:(?<h>a)(?<k>b*))?x", s, ["h", "k"])
          for s in SUBP)
print("   (PRIO) /(?:(?<h>a|ab)(?<k>b*))?x/ vs /(?:(?<h>a)(?<k>b*))?x/: %d subjects, differ %d; `ab` is never h's value in "
      "PCRE's parse" % (len(SUBP), dpd))

print("\nTOTAL engine-run cases %d differ %d; engine disagreements (PCRE2 vs Python `re`) %d; probes %d" %
      (TOT["cases"], TOT["differ"], DIS[0], TOT["probes"]))
