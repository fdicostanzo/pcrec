#!/usr/bin/env python3
# Lane predspec27 (2026-11-18): the evidence of docs/design/predicates_draft.md REVISION 27 (the owner's 2026-11-18
# afternoon rulings: backref-label = capture; value-hole yes; match-is-rx = ONE type; read-is-constant = two forms).
# DESIGN EVIDENCE ONLY; rules nothing.  Standalone: the helpers are COPIED from predspec261_model.py (not imported;
# predspec261_evidence/ stays as committed).  Every "MANAGER'S READING" the five record entries carry is tested here
# where a run can decide it; the rest are decided by a quoted record line (the lane's report says which).
#
# PARTS:
#   BL  backref-label RULED (capture): the witness in every mode; readings m1 (which group vs which value), m2 (an
#       inserted part's group read as PCRE would), m3 (two groups of one name in one literal: PCRE refuses it).
#   VD  the value-hole DISCUSSION's answers: the case at the hole (four placements, python `re` and libpcre2); the
#       narrowing of "`${$y}` equals `\k<y>`" (where they part, counted; the "label if set, else capture" model).
#   UT  ONE TYPE: `$x & <5` legal (two programs; where it parts from `(x: <5)`); his `if(...)` under the ruled `when`
#       (three test readings); `\d + 1` at compile time (the lifted alternation, its ORDER); `$y + 1` at run time;
#       `$y | "x"`, `$y & <5`, `$y . "E"` holes; compile-time folding.
#   TT  the TYPE TABLE as RULE-AS-CODE (consistency only, never an independent control).
#
# CONTROLS: libpcre2-8 through ../rxmodel_evidence/pcre2h.py (run, never read: D181); python `re`; direct python
# semantic functions for the conditional readings.  The label (the one rule) is the marker model of predspec261
# (an empty `(?<ps>)` at each pass start; a label counts only from its pass).
#
# Run (W = the worktree; from $PCREC_TMPDIR/scratch/predspec27; one process, seconds):
#   timeout 900 python3 -I -B W/docs/dev/lanes/predspec27_evidence/predspec27_model.py > fwd.out
#   PREDSPEC27_SABOTAGE=1 (all) or a comma list of s1..s8: deliberately wrong rules; the checks must fail:
#     s1 `\k<h>` read as the LABEL (backref-label's withdrawn draft reading);
#     s2 the label model replaced by PCRE's capture (the one rule's arm removed);
#     s3 the case at the hole decided by the GROUP's options;
#     s4 `$x & <5` read as the condition `(x: <5)` (the stretch not judged);
#     s5 the conditional's bare test PEEKED (not consumed);
#     s6 the lifted `\d + 1` built LONGEST FIRST (not in the values' order);
#     s7 a value inserted as REGEX SYNTAX (not as its one string);
#     s8 TT: a single-value function on a finite rx classed BUILT NOW.
import os, sys, re, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rxmodel_evidence"))
import pcre2h as P                                           # noqa: E402

_sv = os.environ.get("PREDSPEC27_SABOTAGE", "")
SABS = set("s%d" % i for i in range(1, 9)) if _sv == "1" else set(x for x in _sv.split(",") if x)
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


VQ = r'(?<v>[\s\S]*?)(?C"eq")'      # a value hole: a lazy capture accepted only when it equals the value L


print("predspec27 evidence; libpcre2-8 %s%s" % (P.version(), " ; SABOTAGE %s" % ",".join(sorted(SABS, key=lambda x: int(x[1:]))) if SABS else ""))
for line, ok in P.selfcheck():
    print("selfcheck: %s ; %s" % (line, check("selfcheck " + line[:30], ok)))

# =====================================================================================================================
print("\n== PART BL: backref-label RULED: \"capture. Plain rx in particular should work like pcre when we can.\"")
# BL1 the ruled witness, every mode.  `\k<y>` in the literal = PCRE (the capture).  Beside it the LABEL-read form
# `${$y}` (pass-start-read; the one rule), which the ruling leaves reading the label.
k1 = P.Pcre(r'(?:(?<y>\d)?-\k<y>;)*')
def eqlab(c):
    L = label_of(c, "y")
    return L is not None and c.get("v") == L
l1 = P.Pcre(r'(?:(?<ps>)(?<y>\d)?-' + VQ + ';)*', {"eq": eqlab})
kk1 = l1 if sab("s1") else k1                         # s1: `\k` read as the label (the withdrawn draft reading)
BLPOOL = pool("37-;", 7)
print("BL1 `\\k<y>` (RULED: the capture) `/(?:(?<y>\\d)?-\\k<y>;)*/`: %s" % show(kk1, "3-3;-3;", "3-3;-3;", "3-3;-3; 7-7;", ("y",)))
print("BL1 the label read `${$y}` in the same place `/(?:(?<y>\\d)?-${$y};)*/`: %s" % show(l1, "3-3;-3;", "3-3;-3;", "3-3;-3; 7-7;"))
d, first = diff3(kk1, l1, BLPOOL)
print("BL1 the two forms part on %d / %d / %d of %d texts (`37-;`, length <= 7), first %s ; %s"
      % (d[0], d[1], d[2], len(BLPOOL), first,
         check("BL1 ruled witness: `\\k` HOLDS, `${$y}` FAILS, 2/2/2", W(kk1, "3-3;-3;") is not None and W(l1, "3-3;-3;") is None and d == [2, 2, 2])))
# BL m1: "it should be the last reference as labels" narrowed to WHICH GROUP; the VALUE is the capture's.
# A := /(?<h>\d)/, B := /(?<h>\d)?-\k<h>/, `A SEQ B`.  (i) B's own group, its capture (free-name + capture): renamed
# model `(?<h0>\d)(?<h>\d)?-\k<h>`; (ii) PCRE's written-out splice under (?J) (first SET group: A's); (iii) the label
# (one label across SEQ, the last mention; B's optional resets it on entry).
m1_cap = P.Pcre(r'(?<h0>\d)(?<h>\d)?-\k<h>')
m1_J = P.Pcre(r"(?J)(?'h'\d)(?'h'\d)?-\k<h>")
m1_lab = P.Pcre(r'(?<h0>\d)(?<ps>)(?<h>\d)?-' + VQ, {"eq": lambda c: (lambda L: L is not None and c.get("v") == L)(label_of(c, "h"))})
for t in ("7-7", "77-7", "73-3"):
    print("BL m1 `A SEQ B` on `%s`: (i) B's own group, capture %s ; (ii) the splice under (?J) %s ; (iii) the label %s"
          % (t, fW(m1_cap, t), fW(m1_J, t), fW(m1_lab, t)))
M1POOL = pool("37-", 5)
dcj, fcj = diff3(m1_cap, m1_J, M1POOL)
dcl, _ = diff3(m1_cap, m1_lab, M1POOL)
print("BL m1 over %d texts (`37-`, length <= 5): (i) vs (ii) %d / %d / %d (first %s) ; (i) vs (iii) %d / %d / %d ; %s"
      % (len(M1POOL), dcj[0], dcj[1], dcj[2], fcj, dcl[0], dcl[1], dcl[2],
         check("BL m1 which-group = B's own (differs from (?J)), its value = capture", dcj[0] > 0 and W(m1_cap, "7-7") is None and W(m1_cap, "77-7") is not None)))
# BL m2: an outer literal inserting a part X := /(?<h>\d)?/ that exports h, and `\k<h>` after it:
# `/(?:${X}-\k<h>;)*/` written out = `(?:(?:(?<h>\d)?)-\k<h>;)*`: PCRE, the same as the plain literal (BL1).
m2 = P.Pcre(r'(?:(?:(?<y>\d)?)-\k<y>;)*')
d2, _ = diff3(m2, k1, BLPOOL)
print("BL m2 `/(?:${X}-\\k<h>;)*/`, X := /(?<h>\\d)?/: %s ; vs the plain literal of BL1 %d / %d / %d of %d ; %s"
      % (show(m2, "3-3;-3;", "3-3;-3;", "3-3;-3; 7-7;"), d2[0], d2[1], d2[2], len(BLPOOL), check("BL m2 inserted part read as PCRE", d2 == [0, 0, 0])))
# BL m3: two groups of ONE name inside one literal.  PCRE refuses it without (?J); under (?J) the first SET group.
try:
    P.Pcre(r'(?<h>\d);(?:(?<h>\d)|x)\k<h>')
    refused = "compiles"
except ValueError as e:
    refused = "REFUSED (%s)" % str(e).split(": ", 1)[-1]
print("BL m3 `/(?<h>\\d);(?:(?<h>\\d)|x)\\k<h>/` without (?J): libpcre2 %s" % refused)
J3 = P.Pcre(r"(?J)(?'h'\d);(?:(?'h'\d)|x)\k<h>")
def m3(f):
    return P.Pcre(r'(?<h1>\d);(?:(?<h2>\d)|x)' + VQ, {"eq": lambda c: (lambda L: L is not None and c.get("v") == L)(f(c))})
m3_label = m3(lambda c: c.get("h2"))                                     # entering the alternation resets h
m3_last = m3(lambda c: c.get("h2") if c.get("h2") is not None else c.get("h1"))
m3_first = m3(lambda c: c.get("h1") if c.get("h1") is not None else c.get("h2"))
R3POOL = pool("37;x", 4)
dJ, _ = diff3(m3_first, J3, R3POOL)
for nm, rx in (("(?J) PCRE", J3), ("first set (model)", m3_first), ("last set", m3_last), ("label", m3_label)):
    print("BL m3 %-18s %s" % (nm, show(rx, "3;x3", "3;x3 3;77", "3;x3 3;77 3;73")))
dl, _ = diff3(m3_label, m3_last, R3POOL); dlf, _ = diff3(m3_label, m3_first, R3POOL); dfl, _ = diff3(m3_first, m3_last, R3POOL)
print("BL m3 over %d texts (`37;x`, length <= 4): first-set model vs PCRE (?J) %d / %d / %d ; label vs last set %d / %d / %d ; label vs first set %d / %d / %d ; first vs last %d / %d / %d ; %s"
      % (len(R3POOL), dJ[0], dJ[1], dJ[2], dl[0], dl[1], dl[2], dlf[0], dlf[1], dlf[2], dfl[0], dfl[1], dfl[2],
         check("BL m3 refused without (?J); three readings part", refused.startswith("REFUSED") and dJ == [0, 0, 0] and dl[0] > 0 and dlf[0] > 0 and dfl[0] > 0)))

# =====================================================================================================================
print("\n== PART VD: the value-hole discussion's answers (case at the hole; the narrowed control)")
# VD1 case: "the options in force AT THE HOLE decide".  Four placements on `a-A`, python `re` and libpcre2.
PLACES = (("plain", r'(?P<y>a)-(?P=y)', r'(?<y>a)-\k<y>'),
          ("all (?i)", r'(?i)(?P<y>a)-(?P=y)', r'(?i)(?<y>a)-\k<y>'),
          ("only the reference caseless", r'(?P<y>a)-(?i:(?P=y))', r'(?<y>a)-(?i:\k<y>)'),
          ("only the group caseless", r'(?i:(?P<y>a))-(?P=y)', r'(?i:(?<y>a))-\k<y>'))
want = {"plain": False, "all (?i)": True, "only the reference caseless": True, "only the group caseless": False}
okc = True
for nm, py, pc in PLACES:
    a, b = re.fullmatch(py, "a-A") is not None, W(P.Pcre(pc), "a-A") is not None
    okc = okc and a == b == want[nm]
    print("VD1 `a-A` %-28s python `re` %s ; libpcre2 %s" % (nm, "HOLDS" if a else "FAILS", "HOLDS" if b else "FAILS"))
print("VD1 the manager's table (plain fails; (?i) holds; only the reference caseless holds; only the group caseless fails) ; %s" % check("VD1 case table reproduced", okc))
# VD1b the value hole as a literal written at the hole, under the HOLE's options (s3: the GROUP's options), vs `\k<y>`
# with the same placement, over `aAbB-` length <= 5 (3,906 texts), every mode.
def hole_model(group_ci, hole_ci):
    ci = group_ci if sab("s3") else hole_ci
    g = r'(?i:(?<y>[a-b]))' if group_ci else r'(?<y>[a-b])'
    return P.Pcre(g + '-' + VQ, {"eq": lambda c: c.get("y") is not None and ((c.get("v").casefold() == c.get("y").casefold()) if ci else c.get("v") == c.get("y"))})
CPOOL = pool("aAbB-", 5)
okb = True
for gci, hci in ((False, False), (True, True), (False, True), (True, False)):
    kref = P.Pcre((r'(?i:(?<y>[a-b]))' if gci else r'(?<y>[a-b])') + '-' + (r'(?i:\k<y>)' if hci else r'\k<y>'))
    dd, ff = diff3(hole_model(gci, hci), kref, CPOOL, ("y",))
    okb = okb and dd == [0, 0, 0]
    print("VD1b group caseless %-5s hole caseless %-5s: the literal-at-the-hole model vs `\\k<y>` %d / %d / %d of %d, first %s" % (gci, hci, dd[0], dd[1], dd[2], len(CPOOL), ff))
check("VD1b options at the hole = backreference's", okb)
# VD2 the narrowing of "`${$y}` equals `\k<y>`": they part ONLY where the label is unset at the hole and the capture
# set; a "label if set, else capture" model equals `\k<y>` on both pools.
def narrow(c):
    L = label_of(c, "y")
    L = L if L is not None else c.get("y")
    return L is not None and c.get("v") == L
n1 = P.Pcre(r'(?:(?<ps>)(?<y>\d)?-' + VQ + ';)*', {"eq": narrow})
k2 = P.Pcre(r'(?:(?:(?<y>\d);)*,)*=\k<y>')
l2 = P.Pcre(r'(?:(?<ps>)(?:(?<y>\d);)*,)*=' + VQ, {"eq": eqlab})
n2 = P.Pcre(r'(?:(?<ps>)(?:(?<y>\d);)*,)*=' + VQ, {"eq": narrow})
P2 = pool("3;,=", 6)
dA, fA = diff3(l1, k1, BLPOOL); dB, fB = diff3(l2, k2, P2)
dnA, _ = diff3(n1, k1, BLPOOL); dnB, _ = diff3(n2, k2, P2)
kc = P.Pcre(r'(?:(?<y>\d)-\k<y>;)*'); lc = P.Pcre(r'(?:(?<ps>)(?<y>\d)-' + VQ + ';)*', {"eq": eqlab})
dC, _ = diff3(lc, kc, pool("37-;", 6))
print("VD2 `${$y}` (the label) vs `\\k<y>` (the capture): an optional in a loop %d / %d / %d of %d (first %s) ; two loops deep %d / %d / %d of %d (first %s) ; no optional, one depth %d / %d / %d of %d"
      % (dA[0], dA[1], dA[2], len(BLPOOL), fA, dB[0], dB[1], dB[2], len(P2), fB, dC[0], dC[1], dC[2], len(pool("37-;", 6))))
print("VD2 the model \"the label where it is set, else the capture\" vs `\\k<y>`: %d / %d / %d and %d / %d / %d ; %s"
      % (dnA[0], dnA[1], dnA[2], dnB[0], dnB[1], dnB[2],
         check("VD2 they part only where the label is unset and the capture set", dA[0] > 0 and dB[0] > 0 and dC == [0, 0, 0] and dnA == [0, 0, 0] and dnB == [0, 0, 0])))

# =====================================================================================================================
print("\n== PART UT: ONE TYPE (match-is-rx, read-is-constant)")
# UT1 m1: `$x & <5` is no longer an error by type: an rx, x's text when x < 5, else nothing.  As an `&` operand it is
# a FILTER on the stretch (the filter sentence): it holds where the STRETCH is x's text and x < 5.
def and_read(pre):
    if sab("s4"):
        return P.Pcre(pre + r'(?C"t")', {"t": lambda c: num(c.get("x")) and int(c.get("x")) < 5})
    return P.Pcre(pre + r'(?C"t")', {"t": lambda c: c.stretch() == c.get("x") and num(c.get("x")) and int(c.get("x")) < 5})
def cond(pre):
    return P.Pcre(pre + r'(?C"t")', {"t": lambda c: num(c.get("x")) and int(c.get("x")) < 5})
UPOOL = pool("37-", 5)
for pre, nm in ((r'(?<x>\d+)', "/(?<x>\\d+)/"), (r'(?<x>\d+)-', "/(?<x>\\d+)-/")):
    a, b = and_read(pre), cond(pre)
    dd, ff = diff3(a, b, UPOOL, ("x",))
    w_, s_, f_ = ("3", "73 3", "3 7 33") if pre.endswith(")") else ("3-", "7-3-", "3- 7- 3-")
    print("UT1 `%s & ($x & <5)`: %s" % (nm, show(a, w_, s_, f_)))
    print("UT1 `%s & (x: <5)`:    %s ; the two part on %d / %d / %d of %d (first %s)" % (nm, show(b, w_, s_, f_), dd[0], dd[1], dd[2], len(UPOOL), ff))
    if pre.endswith(")"):
        same = dd
    else:
        other = dd
        never = sum(W(a, t) is not None or S(a, t) is not None for t in UPOOL)
print("UT1 where the stretch IS x's text the two agree ; where it is not, `$x & <5` never holds (%d of %d texts hold in any mode) ; %s"
      % (never, len(UPOOL), check("UT1 legal; agrees on /(?<x>\\d+)/, parts on /(?<x>\\d+)-/", same == [0, 0, 0] and other[0] > 0 and never == 0)))

# UT2 m5: his `if($y & (0: 1492), "Columbus", $y)` as the ruled `when(A, then = B, else = C)` in a hole,
# `/(?<y>\d{4}):${when(TEST, "Columbus", else = $y)}/`, three readings of the test:
#   (a) a CONDITION `(y: 1492)` (zero width, reads the label);
#   (b) his test as a BARE PATTERN (when-peek RULED: consumed, warned): `$y & (0: 1492)` matches y's text when y is 1492;
#   (c) as `peek(...)`: tried at the point, consuming nothing; B starts where it started.
# The else guard "A cannot match here" in every case.
is1492 = {"c": lambda c: c.get("y") == "1492", "nc": lambda c: c.get("y") != "1492"}
NOTA = r'(?:(?C"nc")|(?C"c")(?!\k<y>))'
WA = P.Pcre(r'(?<y>\d{4}):(?:(?C"c")Columbus|(?C"nc")\k<y>)', is1492)
WB = P.Pcre(r'(?<y>\d{4}):(?:(?C"c")' + (r'(?=\k<y>)' if sab("s5") else r'\k<y>') + r'Columbus|' + NOTA + r'\k<y>)', is1492)
WC = P.Pcre(r'(?<y>\d{4}):(?:(?C"c")(?=\k<y>)Columbus|' + NOTA + r'\k<y>)', is1492)
def sem(reading, t):
    """direct semantic function: does the WHOLE text match the reading?"""
    m = re.fullmatch(r'(\d{4}):(.*)', t, re.S)
    if not m:
        return False
    y, rest = m.group(1), m.group(2)
    a_here = (y == "1492" and rest.startswith(y))
    if reading == "a":
        return rest == ("Columbus" if y == "1492" else y)
    if reading == "b":
        return (a_here and rest == y + "Columbus") or (not a_here and rest == y)
    return (a_here and rest == "Columbus") or (not a_here and rest == y)
TEXTS = [y + ":" + tail for y in ("1492", "2025") for tail in ("Columbus", "1492", "2025", "1492Columbus", "2025Columbus", "", "Col")]
oku = True
for nm, rx, rd in (("(a) condition", WA, "a"), ("(b) bare, consumed", WB, "b"), ("(c) peek", WC, "c")):
    bad = sum((W(rx, t) is not None) != sem(rd, t) for t in TEXTS)
    oku = oku and bad == 0
    print("UT2 %-20s WHOLE: %s ; vs the semantic function %d of %d differ"
          % (nm, ", ".join("`%s` %s" % (t, fW(rx, t)) for t in ("1492:Columbus", "2025:2025", "1492:1492", "1492:1492Columbus")), bad, len(TEXTS)))
    print("    SEARCHED `x1492:Columbus` %s ; FIND-ALL `1492:Columbus 2025:2025 1492:1492` %s" % (fS(rx, "x1492:Columbus"), fF(rx, "1492:Columbus 2025:2025 1492:1492")))
check("UT2 three readings = their semantic functions", oku)
print("UT2 his intent (Columbus for 1492, else the year) is reading (a) only ; %s"
      % check("UT2 only the condition test gives `1492:Columbus`", W(WA, "1492:Columbus") is not None and W(WB, "1492:Columbus") is None and W(WC, "1492:Columbus") is None))

# UT3 the two forms: `\d + 1` at COMPILE time (the lifted alternation) beside `$y + 1` at RUN time.
digits = [s for s in pool("0123456789", 2) if re.fullmatch(r'\d', s)]          # `\d`'s strings, in the values' order
lifted = [str(int(s) + 1) for s in digits]
order = sorted(lifted, key=lambda s: (-len(s), s)) if sab("s6") else lifted
alt = "(?:" + "|".join(order) + ")"
print("UT3 `\\d` enumerates to %d strings %s ; `\\d + 1` lifts to %s" % (len(digits), digits, alt))
NPOOL = pool("0123456789", 3)
badw = sum((re.fullmatch(alt, t) is not None) != (num(t) and 1 <= int(t) <= 10) for t in NPOOL)
ua = P.Pcre(alt)
ulong = P.Pcre("(?:" + "|".join(sorted(lifted, key=lambda s: (-len(s), s))) + ")")
print("UT3 WHOLE over %d digit texts (length <= 3): the alternation vs \"a canonical numeral 1..10\" %d differ" % (len(NPOOL), badw))
print("UT3 the values' order: %s" % show(ua, "10", "x10", "10 3 11"))
print("UT3 longest first:     %s" % show(ulong, "10", "x10", "10 3 11"))
dor, _ = diff3(ua, ulong, NPOOL)
print("UT3 the two orders part on %d / %d / %d of %d (WHOLE agrees: a set; SEARCHED and FIND-ALL do not: the ORDER is a fact of the lifted rx) ; %s"
      % (dor[0], dor[1], dor[2], len(NPOOL), check("UT3 compile-time form: WHOLE = 1..10, order decides SEARCHED", badw == 0 and dor[0] == 0 and dor[1] > 0 and S(ua, "x10")[1] - S(ua, "x10")[0] == 1)))
def plus1(c):
    y = c.get("y")
    return None if y is None else str(int(y) + 1)
rt = P.Pcre(r'(?<y>\d{4})-' + VQ, {"eq": lambda c: (lambda L: L is not None and c.get("v") == L)(plus1(c))})
print("UT3 `$y + 1` at RUN time `/(?<y>\\d{4})-${$y + 1}/`: %s ; %s"
      % (show(rt, "2025-2026", "x2025-2026", "2025-2026 2030-2032 2030-2031", ("y",)),
         check("UT3 run-time form reproduces VH1", W(rt, "2025-2026") is not None and S(rt, "x2025-2026")[0] == 1 and [(a, b) for a, b, _ in F(rt, "2025-2026 2030-2032 2030-2031")] == [(0, 9), (20, 29)])))

# UT4 the regex operations on a read, in a hole (the run-time form): `$y | "x"`, `$y & <5`, `$y . "E"`.
# Each model (callout) against a plain PCRE pattern that writes the same strings (no loop: label = capture here).
def hole(pre, post, vals):
    return P.Pcre(pre + VQ + post, {"eq": lambda c: c.get("y") is not None and c.get("v") in vals(c)})
H4 = pool("37x-E", 5)
okh = True
rows4 = []
# `$y | "x"`: the alternation in order (y's text first), modelled by two alternatives
m_or = P.Pcre(r'(?<y>\d)-(?:' + VQ + r'|x)', {"eq": lambda c: c.get("y") is not None and c.get("v") == c.get("y")})
c_or = P.Pcre(r'(?<y>\d)-(?:\k<y>|x)')
rows4.append(('`/(?<y>\\d)-${$y | "x"}/`', m_or, c_or, "3-x", "7-3 3-3", "3-3 4-x 5-6 7-7"))
m_and = P.Pcre(r'(?<y>\d)-' + VQ, {"eq": lambda c: num(c.get("y")) and int(c.get("y")) < 5 and c.get("v") == c.get("y")})
c_and = P.Pcre(r'(?<y>[0-4])-\k<y>')
rows4.append(('`/(?<y>\\d)-${$y & <5}/`', m_and, c_and, "3-3", "7-7 3-3", "3-3 7-7 4-4"))
def joined(c):
    y = c.get("y")
    if y is None:
        return None
    return y + "E" if not sab("s7") else y + "."      # s7: the join read as regex syntax `y.` (any character)
m_dot = P.Pcre(r'(?<y>\d)-' + VQ, {"eq": lambda c: (lambda L: L is not None and (re.fullmatch(L, c.get("v")) is not None if sab("s7") else c.get("v") == L))(joined(c))})
c_dot = P.Pcre(r'(?<y>\d)-\k<y>E')
rows4.append(('`/(?<y>\\d)-${$y . "E"}/` (`.` his joining placeholder)', m_dot, c_dot, "3-3E", "x7-7E", "3-3E 4-4x 7-7E"))
for nm, md, ctl, w, s_, f_ in rows4:
    dd, ff = diff3(md, ctl, H4, ("y",))
    okh = okh and dd == [0, 0, 0]
    print("UT4 %s: %s ; the run-time model vs the plain PCRE pattern of the same strings %d / %d / %d of %d" % (nm, show(md, w, s_, f_), dd[0], dd[1], dd[2], len(H4)))
check("UT4 regex operations on a read: run-time model = PCRE", okh)
# UT5 m3: a compile-time constant is FOLDED (the compile-time form on a one-string rx).
left = lambda s, n: s[:n]
print("UT5 folding: left(\"Columbus\", 2) = `%s` ; 2025 + 1 = `%s` ; a one-string rx in, a one-string rx out (RULE-AS-CODE)" % (left("Columbus", 2), str(2025 + 1)))

# =====================================================================================================================
print("\n== PART TT: the TYPE TABLE (R.1.16) as RULE-AS-CODE (consistency, never a control)")
# operand kinds: const (one string, compile time), read (one string, run time), finite (a finite rx, compile time),
# rx (any rx, compile time).  status(op, kind) -> BUILT / UNDER CONSTRUCTION / ERROR, per the table's rows.
REGEX_OPS = {"|", "&", "!", "SEQ", "postfix", "pattern-hole", "when", "peek"}
SINGLE_FNS = {"+", "-", "*", "%", "left", "upperStart", "."}
def status(op, kind):
    if op in REGEX_OPS:
        return "BUILT" if kind in ("const", "finite", "rx", "read") else "ERROR"
    if op in SINGLE_FNS:
        if kind in ("const", "read"):
            return "BUILT"
        if kind == "finite" and sab("s8"):
            return "BUILT"
        return "UNDER CONSTRUCTION"
    if op == "count-hole":
        return {"const": "BUILT", "finite": "BUILT", "read": "UNDER CONSTRUCTION", "rx": "ERROR"}[kind]
    return "ERROR"
tt = [("+", "const", "BUILT"), ("+", "read", "BUILT"), ("+", "finite", "UNDER CONSTRUCTION"), ("+", "rx", "UNDER CONSTRUCTION"),
      ("left", "read", "BUILT"), ("left", "rx", "UNDER CONSTRUCTION"), ("|", "read", "BUILT"), ("&", "read", "BUILT"),
      ("count-hole", "finite", "BUILT"), ("count-hole", "read", "UNDER CONSTRUCTION")]
okt = all(status(o, k) == e for o, k, e in tt)
for o, k, e in tt:
    print("TT %-10s on %-6s -> %s" % (o, k, status(o, k)))
print("TT %d rows ; %s" % (len(tt), check("TT the table's cells", okt)))

# =====================================================================================================================
print("\n== PART Q: the questions left (every mode, a several-match subject)")
def plus1w(c):
    y = c.get("y")
    return None if y is None else str(int(y) + 1).zfill(len(y))
qc = P.Pcre(r'(?<y>\d{4})-' + VQ, {"eq": lambda c: (lambda L: L is not None and c.get("v") == L)(plus1(c))})
qw = P.Pcre(r'(?<y>\d{4})-' + VQ, {"eq": lambda c: (lambda L: L is not None and c.get("v") == L)(plus1w(c))})
print("Q numeral-width CANONICAL  %s" % show(qc, "0099-100", "x0099-0100 0099-100", "0099-100 0099-0100 9999-10000"))
print("Q numeral-width WIDTH KEPT %s" % show(qw, "0099-100", "x0099-0100 0099-100", "0099-100 0099-0100 9999-10000"))
NWP = [a + "-" + b for a in ("0099", "0999", "9999", "0100") for b in ("100", "0100", "1000", "01000", "10000", "101", "0101")]
dnw, _ = diff3(qc, qw, NWP)
print("Q numeral-width the two part on %d / %d / %d of %d texts (four years x seven tails)" % (dnw[0], dnw[1], dnw[2], len(NWP)))
qf = P.Pcre(r'(?:(?<y>\d{4}))?-' + VQ, {"eq": lambda c: (lambda L: L is not None and c.get("v") == L)(plus1(c))})
qe = P.Pcre(r'(?:(?<y>\d{4}))?-' + VQ, {"eq": lambda c: c.get("v") == ("" if c.get("y") is None else str(int(c.get("y")) + 1))})
print("Q unset-in-hole FAIL  %s" % show(qf, "-", "x-1 2025-2026", "- 2025-2026 -"))
print("Q unset-in-hole EMPTY %s" % show(qe, "-", "x-1 2025-2026", "- 2025-2026 -"))
UP = pool("12-", 5)
due, _ = diff3(qf, qe, UP)
print("Q unset-in-hole FAIL vs EMPTY on %d texts (`12-`, length <= 5; `\\d{4}` never set there, so every text is the unset case): %d / %d / %d" % (len(UP), due[0], due[1], due[2]))
# construction-line (a): `/\d{${n + 1}}/`, n := [2, 4]: BUILT (array-lift's ruled meaning) = `(?|\d{3}|\d{5})`; or UNDER CONSTRUCTION
cl = P.Pcre(r'(?|\d{3}|\d{5})')
print("Q construction-line (a) `/\\d{${n + 1}}/`, n := [2, 4], as BUILT: %s ; as UNDER CONSTRUCTION: the error, in every mode" % show(cl, "12345", "x12345", "123 12345"))
check("Q numeral-width / unset-in-hole readings part", dnw[0] > 0 and due[0] > 0)

print("\n== CHECKS: %d of %d OK" % (sum(ok for _, ok in CHECKS), len(CHECKS)))
for n, ok in CHECKS:
    if not ok:
        print("FAILED: %s" % n)
