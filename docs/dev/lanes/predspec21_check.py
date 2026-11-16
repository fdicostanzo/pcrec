# predspec21: evidence for docs/design/predicates_draft.md rev 21 and docs/dev/lanes/predspec21_report.md
# (lane predspec21, 2026-11-16; design only).
#
# THE QUESTION. The owner ruled domain-scope (COND-FAMILY, 16:31): DOM(h), the values a marked absent label "could have
# had", is read from the PROGRAM the condition meets (the regex with the conditions on it), not from the bare regex.
# The ruling leaves open whether another condition on the SAME label narrows h's DOM. So three domains are computed
# side by side, each over the same populations:
#   REGEX       the values h takes in some whole match of the REGEX (rev 20's VALUES; the defining operand's matches)
#   PROG-OTHER  the values h takes in some match of the PROGRAM where h is present, every condition that does NOT name
#               h applied (a record's entries are separate `&`-ed conditions; a PRODUCT tuple set splits into its
#               entries, record-is-product; a non-product joint set, or an entry reading `$h`, names h): open
#               reading (i)-NO ("another condition on the same label does not narrow")
#   PROG-ALL    the same, EVERY condition of the flattened chain applied, the ones naming h included (over matches
#               where h is present, so no mark on h is ever consulted): open reading (i)-YES
# Marks on OTHER labels inside the program are consulted while a DOM is computed; the DOMs are therefore a FIXED
# POINT. Each is computed twice, descending from the regex's values (TOP) and ascending from the empty set (BOTTOM);
# every table prints whether the two agree. Answers use TOP.
#
# PARTS: (1) THE PROGRAM DOMAIN: rev 20's tables (AR), (TM2), (RZ), (ZJ), (ZE), the two-spellings tables (2SP, SET),
#   review r29's equal-behaviour pairs (EB1 the branch-reset `q := P & (k: "b")` vs the narrowed regex; EB2 t2m vs t2x;
#   EB3 the extra `&` operand), then the four tests per domain. (2) ONE WITNESS: FIXIND-3's and FIXIND-6's populations
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
# Sabotage: `PREDSPEC21_SABOTAGE=1` makes PROG-ALL skip the conditions naming h (= PROG-OTHER) and makes the record
#   read `$a` with its own witness; the EB2 PROG-ALL split count and the record-vs-joint differ count must then be > 0.
import os, re, itertools, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "absfold_check.py")).read()
exec(_src[:_src.index('print("\\n(AR) THE RULE')], globals())     # absfold's prefix (+ absimpact's), verbatim
SAB21 = os.environ.get("PREDSPEC21_SABOTAGE") == "1"
if SAB21:
    print("SABOTAGE ON (PREDSPEC21_SABOTAGE=1)")
VARS = ("REGEX", "PROG-OTHER", "PROG-ALL")
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
    """one `&`-ed condition of the flattened chain: the labels it names, and fn(s, DOM) -> bool"""
    def __init__(self, names, fn):
        self.names = frozenset(names)
        self.fn = fn


def mk(v, S, dom):
    """one label's test: a present text is tested; an absent marked label holds when some value of DOM is in S (F1)"""
    return S(v) if v is not None else any(S(d) for d in dom)


def doms(pop, labels, vals, facs, var):
    """DOM per label under one domain; returns (TOP, BOTTOM) fixed points (dicts label -> set)"""
    regex = {h: {v for s in pop for v in vals(s, h)} for h in labels}
    if var == "REGEX":
        return regex, regex

    def step(cur):
        new = {}
        for h in labels:
            narrow_same = var == "PROG-ALL" and not SAB21
            keep = [f for f in facs if narrow_same or h not in f.names]
            new[h] = {v for s in pop if vals(s, h) and all(f.fn(s, cur) for f in keep) for v in vals(s, h)}
        return new

    def fix(cur):
        for _ in range(60):
            nxt = step(cur)
            if nxt == cur:
                return cur
            cur = nxt
        raise RuntimeError("no fixed point")
    return fix({h: set(regex[h]) for h in labels}), fix({h: set() for h in labels})


def answers(pop, labels, vals, facs, var):
    top, bot = doms(pop, labels, vals, facs, var)
    a = {s: all(f.fn(s, top) for f in facs) for s in pop}
    b = {s: all(f.fn(s, bot) for f in facs) for s in pop}
    return a, top, sum(a[s] != b[s] for s in pop)


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


MOVES = []          # (table, variant, n, smallest)
FPRES = {v: 0 for v in VARS}     # TOP vs BOTTOM disagreements per variant over PART 1
WIT = {v: 0 for v in VARS}       # (i)
SPL = {v: 0 for v in VARS}       # (ii)
SETS = {v: 0 for v in VARS}      # (iii)
RAMP = {v: 0 for v in VARS}      # (iv)
HELD = {}                        # the values each label holds in the program (PROG-ALL TOP), per table, for (i)


def run_table(title, pop, labels, vals, facs, show=None, tally=True):
    """answers per variant; the moves against REGEX; the witnesses (i) against PROG-ALL's held values"""
    res = {}
    for v in VARS:
        a, top, fp = answers(pop, labels, vals, facs, v)
        res[v] = (a, top, fp)
        FPRES[v] += fp
    print("   %s: DOM %s; TOP vs BOTTOM fixed point differ: %s" % (
        title, "; ".join("%s %s" % (v, " ".join("%s={%s}" % (h, dstr(res[v][1][h])) for h in labels)) for v in VARS),
        "/".join(str(res[v][2]) for v in VARS)))
    for v in VARS[1:]:
        d = [s for s in pop if res[v][0][s] != res["REGEX"][0][s]]
        if tally:
            MOVES.append((title, v, len(d), len(pop), sm(d), res["REGEX"][0].get(sm(d)) if d else None))
        print("      %-10s vs REGEX: %d of %d move%s" % (v, len(d), len(pop), "" if not d else ", smallest %r (REGEX %s, %s %s)"
                                                    % (sm(d), hfx(res["REGEX"][0][sm(d)]), v, hfx(res[v][0][sm(d)]))))
    held = res["PROG-ALL"][1]
    for v in VARS:
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
    ("record (h?: <5, k: 3..7)", [Fac("h", lambda s, Dm: mk(hv(s), S5, Dm["h"])), Fac("k", lambda s, Dm: T37(kv(s)))]),
    ("record (h?: !(<10), k: 3..7)", [Fac("h", lambda s, Dm: mk(hv(s), NOTLT10, Dm["h"])),
                                      Fac("k", lambda s, Dm: T37(kv(s)))]),
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


KF = Fac("k", lambda s, Dm: T37(RZ[s][0]))
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
C1k = Fac("k", lambda s, Dm: ZE[s][1] == "3")
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
kb = Fac("k", lambda s, Dm: BRK[s][0] == "b")
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
                                                                     mk(GI[s]["h"], ZZ, Dm["h"]))], v)[0]["h"]
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
print("\n(MOVES) the answers that move from REGEX, per table and domain (the smallest witness each)")
for t, v, n, tot, ex, regans in MOVES:
    if n:
        print("   %-62s %-10s %5d of %6d  smallest %r (REGEX %s)" % (t[:62], v, n, tot, ex, hfx(regans)))
print("   every other table: 0 move under both program domains")

print("\n(SUMMARY) per domain: (i) an answer witnessed only by a value the label never holds in a match of the program "
      "(measured against PROG-ALL's set, so PROG-ALL's 0 is by construction); (ii) two spellings of one program split "
      "(2SP, EB1 A/B, EB2, EB3); (iii) two spellings of one set split (SET <5, ZE a = 0); (iv) record = & (RZ, ZE, EB1 "
      "C/A); the fixed point (TOP vs BOTTOM) over PART 1")
for v in VARS:
    print("   %-10s (i) %-4s %4d   (ii) %-4s %4d   (iii) %-4s %d   (iv) %s (%d split)   fixed point: %s" %
          (v, "YES" if WIT[v] else "no", WIT[v], "YES" if SPL[v] else "no", SPL[v], "YES" if SETS[v] else "no", SETS[v],
           "KEPT" if RAMP[v] == 0 else "BROKEN", RAMP[v], "unique" if FPRES[v] == 0 else "%d differ" % FPRES[v]))

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
        top = doms(pop, ["h"], vv, [fA, fB], v)[0]
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
        top = doms(POP_E, ["a"], v_e, [fa, fb], v)[0]["a"]
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
        top = doms(pop, ["h"], vv, [f1, f2], v)[0]
        per = {s: f1.fn(s, top) and f2.fn(s, top) for s in pop}
        sha = {s: (conds[0][1](G[s]["h"], G[s]) and conds[1][1](G[s]["h"], G[s])) if G[s]["h"] is not None else
               any(conds[0][1](d, G[s]) and conds[1][1](d, G[s]) for d in top["h"]) for s in pop}
        cmp("/%s/ %s & %s DOM(h)={%s} PER-CONDITION vs SHARED [%s]" % (P, conds[0][0], conds[1][0], dstr(top["h"]), v),
            pop, per, sha, "per", "shared")

print("\n(FP) the fixed-point residue: /a(?<h>\\d)|b(?<k>\\d)/ & (h?: <5) & (k?: <5); each mark's DOM is read over "
      "matches where the OTHER mark is consulted")
P_FP = r"a(?<h>\d)|b(?<k>\d)"
POP_FP = ["a" + d for d in D] + ["b" + d for d in D]
GF_ = {s: groups(P_FP, s, ["h", "k"]) for s in POP_FP}
v_fp = lambda s, lab: [GF_[s][lab]] if GF_[s][lab] is not None else []
ffh = Fac("h", lambda s, Dm: mk(GF_[s]["h"], S5, Dm["h"]))
ffk = Fac("k", lambda s, Dm: mk(GF_[s]["k"], S5, Dm["k"]))
for v in VARS:
    top, bot = doms(POP_FP, ["h", "k"], v_fp, [ffh, ffk], v)
    at = {s: ffh.fn(s, top) and ffk.fn(s, top) for s in POP_FP}
    ab = {s: ffh.fn(s, bot) and ffk.fn(s, bot) for s in POP_FP}
    print("   [%-10s] TOP DOM h={%s} k={%s}; BOTTOM h={%s} k={%s}" % (v, dstr(top["h"]), dstr(top["k"]), dstr(bot["h"]),
                                                                    dstr(bot["k"])))
    cmp("      answers TOP vs BOTTOM [%s]" % v, POP_FP, at, ab, "top", "bottom")

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
            fac = Fac("ab", lambda s, Dm, vals_=vals_: rec_slot(vals_(s), Sa, Tb, dflt, marked, Dm["a"]))
            vv = lambda s, lab, vals_=vals_: [a for a, _ in vals_(s) if a is not None]
            dom_ = doms(pop, ["a"], vv, [fac], v)[0]["a"]
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
