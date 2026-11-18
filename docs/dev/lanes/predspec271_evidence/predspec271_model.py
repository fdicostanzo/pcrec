#!/usr/bin/env python3
# Lane predspec271 (2026-11-18): the evidence of docs/design/predicates_draft.md REVISION 27.1 (review r48's fixes as
# the manager ruled them).  DESIGN EVIDENCE ONLY; rules nothing.  Standalone: the helpers are COPIED from
# predspec27_model.py (not imported; predspec27_evidence/ stays as committed).
#
# PARTS (review r48 finding in brackets):
#   B   [B] unset-in-hole re-cut: four candidates ALGEBRA / WHOLE-HOLE / EMPTY-READ / EMPTY-HOLE on the bare `${$y}`,
#       on `${$y | "x"}` (against PCRE's `(?:\k<y>|x)`) and on `${$y + 1}`; R.1.15 (5)'s hit-carry program under the
#       draft's FAIL reading (vacuous) and a witness with the edge second.
#   C   [C] a FINITE label of variable width: the run-time form vs its compile-time copies in PATH order and in the
#       values' (width-ascending) order.
#   D   [D] T1's run-time order: an overlapping-strings witness, written order vs read-first.
#   K   [K] the narrowed control per place: inside an `occurrences` argument (a hit is a pass).
#   J   [J] hole-flags: a compile-time one-string rx with its own flags vs a read under the options at the hole.
#   H   [H] the one number domain: `0099` under §2.4's canonical rule vs `+` parsing digits; a non-numeral read.
#   A   [A] construction-line (a): the finite-lifting fact (`(?|\d{3}|\d{5})`, `\d + 1`), every mode.
#   I   [I] under-construction-class: the meaning of an infinite operand's image (`\d+ + 1`), every mode.
#   TT  [V] the TYPE TABLE (rev 27.1) as RULE-AS-CODE: EVERY stated cell; unstated cells return NOT-MODELLED.
#
# CONTROLS: libpcre2-8 through ../rxmodel_evidence/pcre2h.py (run, never read: D181); python `re` (J); direct python
# semantic functions.  The label is predspec261's marker model (an empty marker group at each pass / hit start; a
# label counts only from its pass).
#
# Run (W = the worktree; from $PCREC_TMPDIR/scratch/predspec271; one process, seconds):
#   timeout 900 python3 -I -B W/docs/dev/lanes/predspec271_evidence/predspec271_model.py > fwd.out
#   PREDSPEC271_SABOTAGE=1 (all) or a comma list of s1..s9: deliberately wrong rules; the checks must fail:
#     s1 the unset read under `|` read as WHOLE-HOLE (the hole fails), not ALGEBRA;
#     s2 R.1.15 (5) under FAIL modelled with the unset read as EMPTY (the vacuity hidden);
#     s3 T1's run-time form READ-FIRST (not written order);
#     s4 a finite label's compile-time copies in the VALUES' order (not path order);
#     s5 the label inside an `occurrences` argument WITHOUT the hit marker (a hit not counted as a pass);
#     s6 a read in a hole under the GROUP's options (not the hole's);
#     s7 the number domain: `+` parses any digit string (not §2.4's canonical numerals);
#     s8 TT: an array the user writes under arithmetic classed UNDER CONSTRUCTION (the withdrawn m1 consequence);
#     s9 TT: a read in a COUNT hole on a FINITE label classed UNDER CONSTRUCTION (rev 26.1's finite clause dropped).
import os, sys, re, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rxmodel_evidence"))
import pcre2h as P                                           # noqa: E402

_sv = os.environ.get("PREDSPEC271_SABOTAGE", "")
SABS = set("s%d" % i for i in range(1, 10)) if _sv == "1" else set(x for x in _sv.split(",") if x)
def sab(k): return k in SABS

CHECKS = []
def check(name, ok):
    CHECKS.append((name, bool(ok)))
    return "OK" if ok else "FAILED"

NOTEMPTY_ATSTART = 0x00000008
CASELESS = 0x00000008          # PCRE2_CASELESS (compile option; same bit value as NOTEMPTY_ATSTART, a match option)


def pool(alpha, n=5):
    out = [""]
    for k in range(1, n + 1):
        out += ["".join(t) for t in itertools.product(alpha, repeat=k)]
    return out


def W(rx, s):
    return rx.match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)


def S(rx, s):
    return rx.match(s, 0)


def F(rx, s):
    """PCRE2's global loop (R.1.2)"""
    out, pos, ne = [], 0, False
    while pos <= len(s):
        r = rx.match(s, pos, (NOTEMPTY_ATSTART | P.PCRE2_ANCHORED) if ne else 0)
        if r is None:
            if ne:
                ne = False
                pos += 1
                continue
            break
        out.append(r)
        ne = r[1] == r[0]
        pos = r[1]
    return out


def lab(r, keys):
    return "" if not keys else " " + ", ".join("%s = %s" % (k, "unset" if r[2].get(k) is None else "`%s`" % r[2][k]) for k in keys)


def fW(rx, s, keys=()):
    r = W(rx, s)
    return "FAILS" if r is None else "HOLDS" + lab(r, keys)


def fS(rx, s, keys=()):
    r = S(rx, s)
    return "FAILS" if r is None else "`%s`@%d%s" % (s[r[0]:r[1]], r[0], lab(r, keys))


def fF(rx, s, keys=()):
    return "[" + ", ".join("`%s`@%d%s" % (s[a:b], a, lab((a, b, l), keys)) for a, b, l in F(rx, s)) + "]"


def row(rx, s, mode, keys=()):
    if mode == "W":
        r = W(rx, s)
        return None if r is None else tuple(r[2].get(k) for k in keys)
    if mode == "S":
        r = S(rx, s)
        return None if r is None else (r[0], r[1]) + tuple(r[2].get(k) for k in keys)
    return tuple((a, b) + tuple(l.get(k) for k in keys) for a, b, l in F(rx, s))


def diff3(r1, r2, texts, keys1=(), keys2=None):
    keys2 = keys1 if keys2 is None else keys2
    out, first = [], None
    for m in "WSF":
        n = 0
        for s in texts:
            if row(r1, s, m, keys1) != row(r2, s, m, keys2):
                n += 1
                first = first or (m, s)
        out.append(n)
    return out, first


def show(rx, w, s_, f_, keys=()):
    return "WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % (w, fW(rx, w, keys), s_, fS(rx, s_, keys), f_, fF(rx, f_, keys))


def num(v):
    return v is not None and re.fullmatch(r"0|[1-9]\d*", v) is not None


def label_of(c, g):
    """the one label rule's marker model: a label counts only if its group starts at or after the pass marker"""
    sp, ps = c.span(g), c.span("ps")
    if sab("s2"):
        return c.get(g)
    return c.get(g) if (sp is not None and ps is not None and sp[0] >= ps[0]) else None


VQ = r'(?<v>[\s\S]*?)(?C"eq")'      # a one-string value hole: a lazy capture accepted only when it equals the value


def slots(n):
    """a hole holding an ORDERED list of up to n literal strings: one callout slot per member, tried in list order"""
    return "(?:" + "|".join(r'(?<v%d>[\s\S]*?)(?C"e%d")' % (i, i) for i in range(n)) + ")"


def holerx(pre, post, vals, n=2):
    """vals(c) -> the hole's strings in order (a list), or None for 'the hole fails'"""
    def mk(i):
        def eq(c):
            L = vals(c)
            return L is not None and len(L) > i and c.get("v%d" % i) == L[i]
        return eq
    return P.Pcre(pre + slots(n) + post, {"e%d" % i: mk(i) for i in range(n)})


def F2(rx, s, after):
    """PCRE2's global loop with a hook after each hit (hit-carry: the next hit's hole reads the previous hit's y)"""
    out, pos, ne = [], 0, False
    while pos <= len(s):
        r = rx.match(s, pos, (NOTEMPTY_ATSTART | P.PCRE2_ANCHORED) if ne else 0)
        if r is None:
            if ne:
                ne = False
                pos += 1
                continue
            break
        out.append(r)
        after(r)
        ne = r[1] == r[0]
        pos = r[1]
    return out


def hits_txt(s, hs):
    return "[" + ", ".join("`%s`@%d" % (s[a:b], a) for a, b, _ in hs) + "]"


def canon(v):
    return v is not None and re.fullmatch(r"0|[1-9]\d*", v) is not None


def plus1(y):
    """`$y + 1` on one string under THE DRAFT'S READING of the number domain (rev 27.1, review r48 H): ONE domain for
    every number operation, §2.4's canonical numerals; a string outside it yields NOTHING at run time"""
    if y is None:
        return None
    if sab("s7"):                                    # s7: `+` parses any digit string (the two-domain draft)
        return str(int(y) + 1) if re.fullmatch(r"\d+", y) else None
    return str(int(y) + 1) if canon(y) else None


print("predspec271 evidence; libpcre2-8 %s%s" % (P.version(), " ; SABOTAGE %s" % ",".join(sorted(SABS, key=lambda x: int(x[1:]))) if SABS else ""))
for line, ok in P.selfcheck():
    print("selfcheck: %s ; %s" % (line, check("selfcheck " + line[:30], ok)))

# =====================================================================================================================
print("\n== PART B: unset-in-hole re-cut (review r48 B): four candidates for an UNSET read inside a hole's expression")
# ALGEBRA     the unset read is the rx of NO strings; the expression is evaluated on it ({} | "x" = {x}; {} + 1 = {})
# WHOLE-HOLE  an unset read anywhere in the expression makes the whole hole fail
# EMPTY-READ  the unset read is the one-string rx "" (MATCH_UNSET_BACKREF applied to the READ); "" + 1 is no numeral
# EMPTY-HOLE  an unset read makes the whole hole the empty string (rev 26's VH4/VH6 and rev 27's PART Q `qe` EMPTY)
CANDS = ("ALGEBRA", "WHOLE-HOLE", "EMPTY-READ", "EMPTY-HOLE")
def ev(expr, y, cand):
    """the hole's ordered strings for an expression over one read y (None = unset); None = the hole fails"""
    if y is None:
        if cand == "WHOLE-HOLE" or (cand == "ALGEBRA" and sab("s1")):
            return None
        if cand == "EMPTY-HOLE":
            return [""]
        rd = [] if cand == "ALGEBRA" else [""]
    else:
        rd = [y]
    if expr == "bare":
        out = rd
    elif expr == "or-x":
        out = rd + ["x"]
    elif expr == "plus1":
        out = [v for v in (plus1(r) for r in rd) if v is not None]
    return out if out else None                     # an expression that yields nothing FAILS (the ruled form)
progs = {}
for cand in CANDS:
    progs[("bare", cand)] = holerx(r'(?<y>\d)?-', '', lambda c, cand=cand: ev("bare", c.get("y"), cand), 1)
    progs[("or-x", cand)] = holerx(r'(?<y>\d)?-', '', lambda c, cand=cand: ev("or-x", c.get("y"), cand), 2)
    progs[("plus1", cand)] = holerx(r'(?:(?<y>\d{4}))?-', '', lambda c, cand=cand: ev("plus1", c.get("y"), cand), 1)
for cand in CANDS:
    print("B bare `/(?<y>\\d)?-${$y}/` %-10s %s" % (cand, show(progs[("bare", cand)], "-", "x- 3-3", "- 3-3 -")))
for cand in CANDS:
    print("B `/(?<y>\\d)?-${$y | \"x\"}/` %-10s %s" % (cand, show(progs[("or-x", cand)], "-x", "-x", "3-3 -x")))
for cand in CANDS:
    print("B `/(?<y>\\d{4})?-${$y + 1}/` %-10s %s" % (cand, show(progs[("plus1", cand)], "-", "x-1 2025-2026", "- 2025-2026 -")))
BP = pool("37x-", 5)
pc_or = P.Pcre(r'(?<y>\d)?-(?:\k<y>|x)')
pc_bare = P.Pcre(r'(?<y>\d)?-\k<y>')
dor = {}
for cand in CANDS:
    dor[cand], fo = diff3(progs[("or-x", cand)], pc_or, BP)
    db, fb = diff3(progs[("bare", cand)], pc_bare, BP)
    print("B vs PCRE over %d texts (`37x-`, length <= 5): `${$y | \"x\"}` %-10s vs `(?:\\k<y>|x)` %d / %d / %d (first %s) ; bare `${$y}` vs `\\k<y>` %d / %d / %d"
          % (len(BP), cand, dor[cand][0], dor[cand][1], dor[cand][2], fo, db[0], db[1], db[2]))
UP = pool("12-", 5)
dpl = {c: diff3(progs[("plus1", c)], progs[("plus1", "ALGEBRA")], UP)[0] for c in CANDS}
print("B `${$y + 1}` over %d texts (`12-`, length <= 5) against ALGEBRA: %s" % (len(UP), " ; ".join("%s %d / %d / %d" % (c, d[0], d[1], d[2]) for c, d in dpl.items())))
print("B only ALGEBRA keeps PCRE's answer for `(?:\\k<y>|x)` ; on `$y + 1` ALGEBRA = WHOLE-HOLE = EMPTY-READ, EMPTY-HOLE parts ; %s"
      % check("B unset-in-hole candidates", dor["ALGEBRA"] == [0, 0, 0] and dor["WHOLE-HOLE"][1] > 0 and dor["EMPTY-READ"][1] > 0
              and dpl["WHOLE-HOLE"] == [0, 0, 0] and dpl["EMPTY-READ"] == [0, 0, 0] and dpl["EMPTY-HOLE"][1] > 0))
# R.1.15 (5): `occurrences(/${$y + 1}-(?<y>\d{4})/, min = 2)`: the hole stands BEFORE its group, so by hit-carry a hit
# reads the PREVIOUS hit's y; the first hit has none.  Hits by PCRE2's global loop, the hole reading the previous hit.
def carry_hits(pre, post, t, unset_reading):
    st = {"prev": None}
    def vals(c):
        p = st["prev"]
        if p is None:
            return [""] if unset_reading == "EMPTY-HOLE" else None
        v = plus1(p)
        return None if v is None else [v]
    rx = holerx(pre, post, vals, 1)
    return F2(rx, t, lambda r: st.__setitem__("prev", r[2].get("y")))
for rd in ("FAIL", "EMPTY-HOLE"):
    eff = "EMPTY-HOLE" if (rd == "FAIL" and sab("s2")) else rd
    for t in ("-2025 2026-2030", "-2025 2027-2030"):
        hs = carry_hits('', r'-(?<y>\d{4})', t, eff)
        print("B R.1.15 (5) `occurrences(/${$y + 1}-(?<y>\\d{4})/, min = 2)` unset read as %-10s `%s`: hits %s -> %s" % (rd, t, hits_txt(t, hs), "HOLDS" if len(hs) >= 2 else "FAILS"))
HP = pool("12- ", 6)
nfail = sum(1 for t in HP if carry_hits('', r'-(?<y>\d)', t, "EMPTY-HOLE" if sab("s2") else "FAIL"))
nemp = sum(1 for t in HP if carry_hits('', r'-(?<y>\d)', t, "EMPTY-HOLE"))
print("B `/${$y + 1}-(?<y>\\d)/` as a hit-list argument over %d texts (`12- `, length <= 6): texts with ANY hit: FAIL %d, EMPTY-HOLE %d ; %s"
      % (len(HP), nfail, nemp, check("B R.1.15 (5) is vacuous under FAIL", nfail == 0 and nemp > 0)))
for t in ("2025 2026-2030", "2025 2027-2030"):
    hs = carry_hits(r'(?:', r'-)?(?<y>\d{4})', t, "FAIL")
    print("B the edge second, under FAIL: `/(?:${$y + 1}-)?(?<y>\\d{4})/` as a hit-list argument `%s`: hits %s" % (t, hits_txt(t, hs)))

# =====================================================================================================================
print("\n== PART C: a FINITE label of variable width: run time vs the compile-time copies (review r48 C)")
rtC = P.Pcre(r'(?<y>\d{1,2})' + VQ, {"eq": lambda c: (lambda L: L is not None and c.get("v") == L)(plus1(c.get("y")))})
two = ["%02d" % i for i in range(100)]; one = [str(i) for i in range(10)]
path = two + one                                        # PCRE's path order for `\d{1,2}`: the greedy width first
values = one + two                                      # the values' order, width ascending (lift-order's candidate)
def copies(order):
    return P.Pcre("(?:" + "|".join(y + plus1(y) for y in order if plus1(y) is not None) + ")")
cp_path = copies(values if sab("s4") else path)
cp_vals = copies(values)
CP = pool("0123", 5)
dpth, _ = diff3(rtC, cp_path, CP); dval, fval = diff3(rtC, cp_vals, CP)
print("C `/(?<y>\\d{1,2})${$y + 1}/` (domain: canonical numerals) run-time vs copies in PATH order %d / %d / %d ; in the values' order %d / %d / %d (first %s) of %d texts (`0123`, length <= 5)"
      % (dpth[0], dpth[1], dpth[2], dval[0], dval[1], dval[2], fval, len(CP)))
print("C run time: %s" % show(rtC, "1213", "1213", "1213 45 910"))
print("C values' order copies: %s" % show(cp_vals, "1213", "1213", "1213 45 910"))
print("C %s" % check("C copies keep the answers only in path order", dpth == [0, 0, 0] and dval[1] > 0))

# =====================================================================================================================
print("\n== PART D: T1's run-time order (review r48 D): the operands' strings in WRITTEN order")
m33 = holerx(r'(?<y>\d)-', '', lambda c: None if c.get("y") is None else (["33", c.get("y")] if not sab("s3") else [c.get("y"), "33"]), 2)
rf33 = holerx(r'(?<y>\d)-', '', lambda c: None if c.get("y") is None else [c.get("y"), "33"], 2)
p33 = P.Pcre(r'(?<y>\d)-(?:33|\k<y>)')
mx = holerx(r'(?<y>\d)-', '', lambda c: None if c.get("y") is None else ([c.get("y"), c.get("y") + "x"] if not sab("s3") else [c.get("y") + "x", c.get("y")]), 2)
px = P.Pcre(r'(?<y>\d)-(?:\k<y>|\k<y>x)')
print("D `/(?<y>\\d)-${\"33\" | $y}/` written order: %s" % show(m33, "3-33", "3-33", "3-33 7-7 3-3"))
print("D the same, READ FIRST:         %s" % show(rf33, "3-33", "3-33", "3-33 7-7 3-3"))
d1, f1 = diff3(m33, p33, pool("37-", 5)); d2, f2 = diff3(rf33, p33, pool("37-", 5)); d3_, _ = diff3(mx, px, pool("37x-", 5))
print("D vs PCRE `(?:33|\\k<y>)` over 364 texts (`37-`): written order %d / %d / %d ; read first %d / %d / %d (first %s) ; `${$y | ($y . \"x\")}` vs `(?:\\k<y>|\\k<y>x)` %d / %d / %d of 1,365"
      % (d1[0], d1[1], d1[2], d2[0], d2[1], d2[2], f2, d3_[0], d3_[1], d3_[2]))
print("D %s" % check("D written order = PCRE's alternation, read-first parts", d1 == [0, 0, 0] and d3_ == [0, 0, 0] and d2[1] > 0))

# =====================================================================================================================
print("\n== PART K: the narrowed control per place (review r48 K): an `occurrences` argument (a hit is a pass)")
def occ(R, mn):
    return r'(?:[\s\S]*?(?:' + R + r')){%d,}' % mn
def labhit(c):
    if sab("s5"):
        return c.get("y") is not None and c.get("v") == c.get("y")
    sp, ps = c.span("y"), c.span("ps")
    L = c.get("y") if (sp is not None and ps is not None and sp[0] >= ps[0]) else None
    return L is not None and c.get("v") == L
def narrowhit(c):
    return c.get("y") is not None and c.get("v") == c.get("y")
k1 = P.Pcre(occ(r'(?<y>\d)?-\k<y>;', 2)); l1 = P.Pcre(occ(r'(?<ps>)(?<y>\d)?-' + VQ + ';', 2), {"eq": labhit})
n1 = P.Pcre(occ(r'(?<ps>)(?<y>\d)?-' + VQ + ';', 2), {"eq": narrowhit})
k2 = P.Pcre(occ(r'(?:(?<y>\d);)*=\k<y>', 2)); l2 = P.Pcre(occ(r'(?<ps>)(?:(?<y>\d);)*=' + VQ, 2), {"eq": labhit})
kt = P.Pcre(r'(?<y>\d)?-\k<y>;'); lt = P.Pcre(r'(?<ps>)(?<y>\d)?-' + VQ + ';', {"eq": labhit})
KP1 = pool("37-;", 7); KP2 = pool("3;=", 6); KPT = pool("37-;", 6)
dk1, fk1 = diff3(l1, k1, KP1); dk2, fk2 = diff3(l2, k2, KP2); dkt, _ = diff3(lt, kt, KPT); dn1, _ = diff3(n1, k1, KP1)
print("K `occurrences(/(?<y>\\d)?-${$y};/, min = 2)` vs the `\\k<y>` spelling %d / %d / %d of %d (first %s) ; the same literal at top level %d / %d / %d of %d"
      % (dk1[0], dk1[1], dk1[2], len(KP1), fk1, dkt[0], dkt[1], dkt[2], len(KPT)))
print("K `occurrences(/(?:(?<y>\\d);)*=${$y}/, min = 2)` (no optional, one written depth) vs `\\k<y>` %d / %d / %d of %d (first %s)" % (dk2[0], dk2[1], dk2[2], len(KP2), fk2))
print("K label: %s" % show(l1, "3-3;-3;", "3-3;-3;", "3-3;-3; 7-7;"))
print("K `\\k`:   %s" % show(k1, "3-3;-3;", "3-3;-3;", "3-3;-3; 7-7;"))
print("K the model \"label where set, else the capture\" vs `\\k<y>` in the argument %d / %d / %d ; %s"
      % (dn1[0], dn1[1], dn1[2], check("K in an argument the hit is a pass", dk1[0] > 0 and dk2[0] > 0 and dkt == [0, 0, 0] and dn1 == [0, 0, 0])))

# =====================================================================================================================
print("\n== PART J: hole-flags (review r48 J): one string known at compile time vs at run time, same position")
own = P.Pcre(r'(?i)(?<y>a)-(?-i:a)')                    # q := /a/ with its own flags (hole-reading; §11 O32)
kref = P.Pcre(r'(?i)(?<y>a)-\k<y>')                     # PCRE's backreference: the options at the reference
hm = P.Pcre(r'(?i)(?<y>a)-' + VQ, {"eq": lambda c: c.get("y") is not None and (
    c.get("v") == c.get("y") if sab("s6") else c.get("v").casefold() == c.get("y").casefold())})
print("J own flags  `/(?i)(?<y>a)-${q}/`, q := /a/: %s" % show(own, "a-A", "x a-A", "a-A a-a A-a"))
print("J options at the hole `/(?i)(?<y>a)-${$y}/`:   %s" % show(hm, "a-A", "x a-A", "a-A a-a A-a"))
pyown = re.compile(r'(?i)(?P<y>a)-(?-i:a)'); pyref = re.compile(r'(?i)(?P<y>a)-(?P=y)')
okpy = (pyown.fullmatch("a-A") is None) and (pyref.fullmatch("a-A") is not None)
dj, fj = diff3(hm, kref, pool("aA-x", 5))
print("J python `re` agrees (own flags FAILS, reference HOLDS on `a-A`): %s ; the hole model vs `\\k<y>` %d / %d / %d of 1,365 (`aA-x`) ; %s"
      % (okpy, dj[0], dj[1], dj[2], check("J same string, two answers by when it is known", okpy and W(own, "a-A") is None and W(hm, "a-A") is not None and dj == [0, 0, 0])))

# =====================================================================================================================
print("\n== PART H: the one number domain (review r48 H)")
qh = P.Pcre(r'(?<y>\d{4})-' + VQ, {"eq": lambda c: (lambda L: L is not None and c.get("v") == L)(plus1(c.get("y")))})
print("H `/(?<y>\\d{4})-${$y + 1}/` under the one domain: %s" % show(qh, "0099-100", "0099-100 2025-2026", "0099-100 2025-2026 0100-101"))
qw = P.Pcre(r'(?<y>\w+)-' + VQ, {"eq": lambda c: (lambda L: L is not None and c.get("v") == L)(plus1(c.get("y")))})
print("H a non-numeral read `/(?<y>\\w+)-${$y + 1}/`: %s" % show(qw, "ab-ab1", "ab-ab1 9-10", "ab-ab1 9-10 b-c"))
lt100 = lambda y: canon(y) and int(y) < 100            # §2.4: `y: <100` holds on canonical numerals below 100 only
agree = all((plus1(y) is not None) == canon(y) for y in ("0099", "0100", "0", "00", "99", "2025", "ab"))
print("H `0099`: `y: <100` %s ; `$y + 1` %s ; `+` and `<` agree on the domain for 7 strings: %s ; %s"
      % (lt100("0099"), plus1("0099"), agree, check("H one domain for + and <", agree)))

# =====================================================================================================================
print("\n== PART A: construction-line (a): the finite-lifting fact (review r48 A; the RULED array-lift answers)")
al2 = P.Pcre(r'(?|\d{3}|\d{5})')
print("A AL2 `rx.repeat(rx.digit, n + 1)`, n := [2, 4] = `(?|\\d{3}|\\d{5})`: %s" % show(al2, "123", "123456", "12345 678"))
print("A AL1 `[2, 4] + 1` = %s ; `[2, 4] + [1, 10]` = %s" % ([n + 1 for n in (2, 4)], [a + b for a in (2, 4) for b in (1, 10)]))
lift = P.Pcre("(?:" + "|".join(v for v in (plus1(str(d)) for d in range(10))) + ")")
print("A `\\d + 1` lifted in the values' order `(?:1|...|10)`: %s" % show(lift, "10", "x10", "10 3 11"))
NP = pool("0123456789", 3)
bad = sum(1 for t in NP if (W(lift, t) is not None) != (canon(t) and 1 <= int(t) <= 10))
print("A WHOLE over %d digit texts (length <= 3) vs \"a canonical numeral 1..10\": %d differ ; %s" % (len(NP), bad, check("A lifting a finite operand = its image", bad == 0)))

# =====================================================================================================================
print("\n== PART I: under-construction-class (review r48 I): an image whose meaning is defined, the build not there")
img = P.Pcre(r'[1-9]\d*')   # HAND-WORKED: `\d+ + 1` under the one domain = the canonical numerals >= 1, longest first
print("I the meaning of `${\\d+ + 1}` (HAND-WORKED spelling `[1-9]\\d*`, its answers RUN): %s" % show(img, "10", "x07 12", "0 10 007"))
print("I today, under either error class (\"under construction\" or \"requires module\"): a compile error, in every mode")

# =====================================================================================================================
print("\n== PART TT: the TYPE TABLE of rev 27.1 as RULE-AS-CODE (every stated cell; unstated -> NOT-MODELLED)")
# operand kinds: const (one string, compile time); read (a read, at most one string, run time, of an infinite
# label); readfin (a read of a FINITE label); array (an array the user writes); finite (a finite rx); rx (an infinite
# rx that CAN FILTER); matchonly (an rx that can match but not filter, `\b\d+\b`).
KINDS = ("const", "read", "readfin", "array", "finite", "rx", "matchonly")
REGEX_OPS = {"|", "&", "!", "SEQ", "postfix", "pattern-hole", "when", "condition"}
SINGLE_FNS = {"+", "-", "*", "%", "left", "upperStart"}
def status(op, kind):
    if op in REGEX_OPS:
        return "BUILT"
    if op in SINGLE_FNS or op == ".":
        if kind == "matchonly":
            return "ERROR"
        if op == ".":
            return "OPEN" if kind in ("const", "read", "readfin") else "NOT-MODELLED"
        if kind in ("const", "read", "readfin"):
            return "BUILT"
        if kind == "array":
            return "UNDER CONSTRUCTION" if sab("s8") else "OPEN"
        return "UNDER CONSTRUCTION"
    if op == "compare":
        return "BUILT" if kind in ("const", "read", "readfin") else "NOT-MODELLED"
    if op == "count-hole":
        return {"const": "BUILT", "array": "BUILT", "finite": "BUILT", "readfin": "UNDER CONSTRUCTION" if sab("s9") else "OPEN",
                "read": "UNDER CONSTRUCTION"}.get(kind, "NOT-MODELLED")
    if op == "name-hole":
        return {"const": "BUILT", "read": "ERROR", "readfin": "ERROR"}.get(kind, "NOT-MODELLED")
    if op in ("class-hole", "option-hole"):
        return "OPEN"
    if op in ("backref-hole", "Q-hole"):
        return "ERROR"
    if op == "occurrences":
        return "NOT-MODELLED" if kind in ("read", "readfin") else "BUILT"
    return "NOT-MODELLED"
RANK = {"BUILT": 0, "OPEN": 1, "NOT-MODELLED": 1, "UNDER CONSTRUCTION": 2, "ERROR": 3}
def compose(op, kind, pos, rkind):
    """THE COMPOSITION RULE (rev 27.1, review r48 I): an operation inside a position: both rows apply; the stricter wins"""
    a, b = status(op, kind), status(pos, rkind)
    return a if RANK[a] >= RANK[b] else b
# the cells as the draft's TYPE TABLE states them (rev 27.1), transcribed
TT = {}
for op in ("|", "&", "!", "SEQ", "postfix", "pattern-hole", "when", "condition"):
    for k in KINDS:
        TT[(op, k)] = "BUILT"
for op in ("+", "-", "*", "%", "left", "upperStart"):
    for k in KINDS:
        TT[(op, k)] = {"const": "BUILT", "read": "BUILT", "readfin": "BUILT", "array": "OPEN", "finite": "UNDER CONSTRUCTION",
                       "rx": "UNDER CONSTRUCTION", "matchonly": "ERROR"}[k]
for k in KINDS:
    TT[(".", k)] = {"const": "OPEN", "read": "OPEN", "readfin": "OPEN", "matchonly": "ERROR"}.get(k, "NOT-MODELLED")
    TT[("compare", k)] = "BUILT" if k in ("const", "read", "readfin") else "NOT-MODELLED"
    TT[("count-hole", k)] = {"const": "BUILT", "array": "BUILT", "finite": "BUILT", "readfin": "OPEN", "read": "UNDER CONSTRUCTION"}.get(k, "NOT-MODELLED")
    TT[("name-hole", k)] = {"const": "BUILT", "read": "ERROR", "readfin": "ERROR"}.get(k, "NOT-MODELLED")
    for op in ("class-hole", "option-hole"):
        TT[(op, k)] = "OPEN"
    for op in ("backref-hole", "Q-hole"):
        TT[(op, k)] = "ERROR"
    TT[("occurrences", k)] = "NOT-MODELLED" if k in ("read", "readfin") else "BUILT"
okt = all(status(o, k) == e for (o, k), e in TT.items())
nm = sum(1 for e in TT.values() if e == "NOT-MODELLED")
for op in ("+", "count-hole", "name-hole", ".", "compare"):
    print("TT %-10s %s" % (op, " ; ".join("%s %s" % (k, status(op, k)) for k in KINDS)))
cmp = compose("+", "array", "count-hole", "array")
print("TT composition `\\d{${n + 1}}`, n := [2, 4]: T8 on an array %s, T13 on its finite result %s -> %s"
      % (status("+", "array"), status("count-hole", "array"), cmp))
print("TT %d cells (%d operations x %d kinds), %d NOT-MODELLED (no cell stated) ; %s"
      % (len(TT), len(TT) // len(KINDS), len(KINDS), nm, check("TT every stated cell", okt and cmp == "OPEN")))

print("\n== CHECKS: %d of %d OK" % (sum(ok for _, ok in CHECKS), len(CHECKS)))
