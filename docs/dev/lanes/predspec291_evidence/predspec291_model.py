#!/usr/bin/env python3
# Lane predspec291 (2026-11-19): the evidence of docs/design/predicates_draft.md REVISION 29.1 (review r54's sixteen
# items P29-1..P29-16 as the predicate manager ruled them; the manager's readings 1-4 of the lane's brief tested).
# DESIGN EVIDENCE ONLY; rules nothing.  Standalone: rev 29's model (../predspec29_evidence/predspec29_model.py, copied,
# not imported; that directory stays as committed) with its PARTS kept, and the rev 29.1 additions marked "[29.1]".
#
# PARTS (the reading or item each feeds; the draft passage):
#   PO  padded-order RULED any-length-first (rev 29's readings 1, 2) [29.1: P29-6: the CONDITION's witness `\d+?` cannot
#       separate the ruled body from the DROPPED exact-first body; the SPARSE lazy `(?:\d\d)+?` (n = 3) and the finite
#       `(?:\d\d){1,2}?` can; the condition check now fails under the dropped body (t1); the question padded-lazy-sparse].
#   TX  [29.1] P29-1 and the manager's reading 2: the inserted literal PARSED ALONE (comments, `\Q`, group numbers,
#       recursion its own; it inherits only `i m s`): a MODEL spelling `(?-U:(?^ims:...))` + renumbering, never "the"
#       text; the four drills (a) `U` (b) `#` under a written `(?x)` (c) an unterminated `\Q` (d) `(?R)` / `(?1)`;
#       every printed rev 29 flags triple re-derived under it.
#   FA  [29.1] P29-2: the `r` and `a`-family flags at a hole (UTF + UCP compile), the draft's reading (inherited) vs
#       not inherited.
#   SQ  [29.1] P29-3 and the manager's reading 3: the flags of a SEQUENCE operand (each operand starts with the flags
#       inherited where the sequence stands; nothing passes sideways).
#   FF  flags-scope RULED (rev 29's readings 3-7, 12, 13).
#   CO  class-order RULED (rev 29's readings 8-11) [29.1: P29-9 the class FIRST `\d + (1|9)`; P29-10
#       `enumerate(/\d/) + 1`].
#   NE  number-edges RULED nothing.
#   DD  dollar-diagnostic RULED [29.1: P29-11 and the manager's reading 4: the warned form defined on the PARSE (a
#       small parser of the program text, the precedence table's levels 5 and 7); the parse drill; P29-12: the HINT
#       keyed on the place, and the value-hole witness re-run].
#   SC  same-name-count RULED [29.1: P29-5 the optional and looped groups: last mention vs last set].
#   TA  T-a (isodate) [29.1: P29-13 hole-export: `isodate SEQ "!"` vs `/${isodate}!/` as a caller sees them].
#   TB  T-b (private labels).
#   PL  plus-operands RULED [29.1: P29-7 and the manager's reading 1: ONE warning trigger, an arithmetic result KNOWN
#       to be nothing whatever the cause; a member list only when every member's result is nothing].
#   AC  T-c (`any_case`) [29.1: P29-4 a NEGATED filter operand; the LEAN vs the DEFINITION].
#
# CONTROLS: libpcre2-8 through ../rxmodel_evidence/pcre2h.py (run, never read: D181); python `re`; direct python
# semantic functions.  RULE-AS-CODE is named as such where it is used.
#
# Run (W = the worktree; from $PCREC_TMPDIR/scratch/predspec291; one process, seconds):
#   timeout 900 python3 -I -B W/docs/dev/lanes/predspec291_evidence/predspec291_model.py > fwd.out
#   PREDSPEC291_SABOTAGE=t1,.. (or =1 for all): deliberately wrong rules; each must fail its check (ONE per check):
#     t1  PO: the body EXACT-WIDTH FIRST (the dropped body) [29.1: now caught by the CONDITION check too];
#     t2  PO: the lazy argument's any-length branch taken GREEDY (rev 28.1's hand reduction `[01]{2,}`);
#     t3  PO: the fill reference built in LENGTH order (longest first) for the mixed-order argument;
#     t4  FF: `U` INHERITED (rev 28.1's draft reading);
#     t5  FF: an `&` inside a hole keeps its own flags (flags-in-filter candidate (a));
#     t6  FF: a filter-role argument's `&` operand inside a hole kept caseful (the manager's m2 of 2026-11-18);
#     t7  FF: inheritance stops at depth one (B in A not reached);
#     t8  FF: a binding alone read under the flags of a hole it is used at elsewhere;
#     t9  CO: class members in CODEPOINT order (the replaced lean);
#     t10 CO: `(1|9) + \d` sorted longest-first ACROSS the alternation (the user's order not kept);
#     t11 CO: the second candidate for two classes made identical to the first;
#     t12 CO: equal result strings kept as separate results (no merge);
#     t13 NE: a negative result read as a signed numeral;
#     t14 DD: the warning keyed on EMPTINESS (silent where the form is right);
#     t15 SC: `\k<h>` after the hole reads the last mention (the inserted group);
#     t16 TA: a part label HIDES its part's labels from a bare reference;
#     t17 TB: a private label exported out of its binding;
#     t18 AC: the body drops the argument's own written `(?-i)`;
#     t19 FF: the inserted literal's `\k<h>` spelt as PCRE's text paste under `(?J)` (rev 28.1's reading);
#     t20 PL: `+` JOINS a non-number member to its operand (the join candidate he closed);
#     t21 PL: the warning fires when only SOME members are outside the domain;
#     t22 PL: a non-numeral READ joined instead of yielding nothing;
#     [29.1]
#     t23 TX: the parsed-alone model does not end the literal's own comment / `\Q` at its end (the text paste);
#     t24 TX: the parsed-alone model leaves an outer `(?U)` in force (no `(?-U:...)`: the `(?^...)` spelling alone);
#     t25 FA: the `a` family NOT inherited (`(?^)` taken to reset it too);
#     t26 SQ: a sequence operand's flags pass sideways (text concatenation);
#     t27 PO: the sparse lazy witness dropped from the condition check (the dense `\d+?` alone);
#     t28 PL: the warning keyed on a non-numeral operand only (the replaced two-branch wording; `% 0` silent);
#     t29 DD: the trigger LEXICAL (rev 29's `\$\w+\s*&` over the program text);
#     t30 DD: the hint printed at every place (a value hole included);
#     t31 SC: `$h` after an optional inserted group reads the LAST SET (not the last mention);
#     t32 CO: `\d + (1|9)` reading A built with the class's results sorted across the alternation (= reading B);
#     t33 AC: the negated operand of a filter-role argument keeps its OWN flags in the REACH body;
#     t34 TA: a hole exports nothing (candidate (b) of hole-export applied to the model of the draft's reading);
#     t35 CO: `enumerate(/\d/) + 1` read as the class lift (= `\d + 1`) in the array-lift row.
import os, sys, re, itertools, random
import re._parser as SRE
import re._constants as SC

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rxmodel_evidence"))
import pcre2h as P                                           # noqa: E402

_sv = os.environ.get("PREDSPEC291_SABOTAGE", "")
SABS = set("t%d" % i for i in range(1, 36)) if _sv == "1" else set(x for x in _sv.split(",") if x)
def sab(k): return k in SABS

CHECKS = []
def check(name, ok):
    CHECKS.append((name, bool(ok)))
    return "OK" if ok else "FAILED"

NOTEMPTY_ATSTART = 0x00000008


def pool(alpha, n=5):
    out = [""]
    for k in range(1, n + 1):
        out += ["".join(t) for t in itertools.product(alpha, repeat=k)]
    return out


def W(rx, s): return rx.match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)
def S(rx, s): return rx.match(s, 0)


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


def esc(s): return s.replace("\n", "\\n")
def fW(rx, s): return "FAILS" if W(rx, s) is None else "HOLDS"
def fS(rx, s):
    r = S(rx, s)
    return "FAILS" if r is None else "`%s`@%d" % (esc(s[r[0]:r[1]]), r[0])
def fF(rx, s): return "[" + ", ".join("`%s`@%d" % (esc(s[a:b]), a) for a, b, _ in F(rx, s)) + "]"


def row(rx, s, mode):
    if mode == "W":
        return W(rx, s) is not None
    if mode == "S":
        r = S(rx, s)
        return None if r is None else (r[0], r[1])
    return tuple((a, b) for a, b, _ in F(rx, s))


def diff3(r1, r2, texts):
    out, first = [], None
    for m in "WSF":
        n = 0
        for s in texts:
            if row(r1, s, m) != row(r2, s, m):
                n += 1
                first = first or (m, s)
        out.append(n)
    return out, first


def show(rx, w, s_, f_):
    return "WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % (esc(w), fW(rx, w), esc(s_), fS(rx, s_), esc(f_), fF(rx, f_))


def trip(rx, w, s_, f_):
    return (fW(rx, w), fS(rx, s_), fF(rx, f_))


def compiles(p, cb=None):
    try:
        return P.Pcre(p, cb), None
    except ValueError as e:
        return None, str(e).split(": ", 1)[-1]


def canon(v):
    return v is not None and re.fullmatch(r"0|[1-9]\d*", v) is not None


def arith(y, op, k):
    """`$y op k` under THE NUMBER DOMAIN (RULED canonical) and number-edges (RULED 2026-11-19, "number-edge: nothing"):
    None = yields nothing (a non-canonical operand, `% 0`, a negative result)"""
    if not canon(y):
        return None
    a = int(y)
    if op == "%" and k == 0:
        return None
    r = {"+": a + k, "-": a - k, "*": a * k, "%": a % k if k else None}[op]
    if r < 0:
        return ("-" + str(-r)) if sab("t13") else None
    return str(r)


VQ = r'(?<v>[\s\S]*?)(?C"eq")'      # a value hole: a lazy capture accepted only when the predicate holds on it


def hole(pre, pred, post=''):
    return P.Pcre(pre + VQ + post, {"eq": lambda c: pred(c, c.get("v")) is True})


def zfill_min(v, n):
    """padded-width RULED minimum"""
    return "0" * max(0, n - len(v)) + v


def alt_rx(strs, pre="", post=""):
    seen, out = set(), []
    for s in strs:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return P.Pcre(pre + "(?:" + ("|".join(re.escape(s) for s in out) if out else "(?!)") + ")" + post)


print("predspec291 evidence; libpcre2-8 %s%s" % (P.version(), " ; SABOTAGE %s" % ",".join(sorted(SABS, key=lambda x: int(x[1:]))) if SABS else ""))
for line, ok in P.selfcheck():
    print("selfcheck: %s ; %s" % (line, check("selfcheck " + line[:30], ok)))

# ---------------------------------------------------------------------------------------------------------------------
# the enumerator (§5.5, PCRE priority order), copied from predspec281's PART PR; class members in codepoint order
# (equal-length members: their order is never observable in a match, reading 8, checked in PART CO by shuffles)
class Refused(Exception):
    pass


def cls_members(items):
    out = set()
    for op, av in items:
        if op == SC.LITERAL:
            out.add(chr(av))
        elif op == SC.RANGE:
            out |= {chr(c) for c in range(av[0], av[1] + 1)}
        elif op == SC.CATEGORY and av == SC.CATEGORY_DIGIT:
            out |= set("0123456789")
        else:
            raise Refused("class item not modelled: %s" % op)
    return sorted(out)


def seq_strs(seq):
    if not seq:
        return [""]
    (op, av), rest = seq[0], seq[1:]
    if op == SC.LITERAL:
        return [chr(av) + s for s in seq_strs(rest)]
    if op == SC.IN:
        tail = seq_strs(rest)
        return [c + s for c in cls_members(av) for s in tail]
    if op == SC.BRANCH:
        return [s for alt in av[1] for s in seq_strs(list(alt) + rest)]
    if op == SC.SUBPATTERN:
        return seq_strs(list(av[3]) + rest)
    if op in (SC.MAX_REPEAT, SC.MIN_REPEAT):
        lo, hi, body = av
        if hi == SC.MAXREPEAT:
            raise Refused("infinite")
        if lo > 0:
            return seq_strs(list(body) + [(op, (lo - 1, hi - 1, body))] + rest)
        if hi == 0:
            return seq_strs(rest)
        more = seq_strs(list(body) + [(op, (0, hi - 1, body))] + rest)
        none = seq_strs(rest)
        return more + none if op == SC.MAX_REPEAT else none + more
    raise Refused("not modelled: %s" % op)


def enum(rx):
    return seq_strs(list(SRE.parse(rx, re.ASCII)))


# =====================================================================================================================
print("\n== PART PO: padded-order RULED (\"i agree with your lean\"): padded(rx, n) := (rx & /(?s:.){n,}/) | (/0*${rx}/ & /(?s:.){n}/)")
def body(rx, n, lazy_reduced=False, exact_first=None):
    """the RULED macro body, RUN as written: each `&` in the hole a capture plus a callout judging the stretch WHOLE by
    the other operand (libpcre2 itself judges `(?s:.){n,}` / `(?s:.){n}`); the branches in the ruled order"""
    ge, eq = P.Pcre(r"(?s:.){%d,}" % n), P.Pcre(r"(?s:.){%d}" % n)
    A = r'(?<a>%s)(?C"A")' % (rx if not lazy_reduced else re.sub(r"\+\?$", "+", rx))
    B = r'(?<b>0*(?:%s))(?C"B")' % rx
    xf = sab("t1") if exact_first is None else exact_first
    br = [B, A] if xf else [A, B]
    return P.Pcre("(?:%s)" % "|".join(br), {"A": lambda c: W(ge, c.get("a") or "") is not None if c.get("a") is not None else False,
                                            "B": lambda c: W(eq, c.get("b") or "") is not None if c.get("b") is not None else False})


def fill(members, n):
    """"fill each string in the argument's order" (the record's comparison): each member zero-filled to at least n,
    in enumerate's order (T5's per-string application)"""
    fills = [zfill_min(m, n) for m in members]
    return fills


ALPH = "019x"
PT = pool(ALPH, 5)
POST = ["", "1"]                       # alone, and followed by a digit (a continuation that can re-split the digits)
def po_cmp(rx_body, rx_trunc, n, label):
    """rx_body: the argument as written (the body runs it); rx_trunc: the same argument over the subject's digits,
    truncated to the subject's length (HAND-WORKED truncation: a member with another digit or longer than the subject
    cannot match); the fill reference is the per-member alternation in enumerate's order"""
    tot = [0, 0, 0]
    first = None
    for post in POST:
        b = body(rx_body, n)
        bp = P.Pcre("(?:" + b.pattern + ")" + post, b.callouts)
        ref = alt_rx(fill(enum(rx_trunc), n), post=post)
        d, f = diff3(bp, ref, PT)
        tot = [x + y for x, y in zip(tot, d)]
        first = first or f
    print("PO %-34s n=%d any-length-first vs fill-each-string over %d texts x %d continuations (`%s`, length <= 5): %d / %d / %d (first %s)"
          % (label, n, len(PT), len(POST), ALPH, tot[0], tot[1], tot[2], first))
    return tot


# reading 1: arguments ordered by length (longest first; shortest first), finite and infinite
LONG = [(r"\d{1,3}", r"[019]{1,3}"), (r"\d\d\d|\d\d|\d", r"[019][019][019]|[019][019]|[019]"), (r"\d{2,4}", r"[019]{2,4}"),
        (r"\d+", r"[019]{1,5}"), (r"0123|1", r"0123|1")]
SHORT = [(r"\d{1,3}?", r"[019]{1,3}?"), (r"\d|\d\d|\d\d\d", r"[019]|[019][019]|[019][019][019]"), (r"\d+?", r"[019]{1,5}?"),
         (r"1|0119", r"1|0119"), (r"1|01|011", r"1|01|011")]
r1 = {}
for grp, args in (("LONGEST FIRST", LONG), ("SHORTEST FIRST", SHORT)):
    for rx, tr in args:
        for n in (2, 3):
            r1[(rx, n)] = po_cmp(rx, tr, n, "%s `%s`" % (grp, rx))
# the shortest-first counterexample, every mode
cx = body(r"1|0123", 2)
cxr = alt_rx(fill(enum(r"1|0123"), 2))
print("PO `/${padded(/1|0123/, 2)}/` the RULED body: %s" % show(cx, "0123", "x0123", "0123 01 0123"))
print("PO the same, fill each string in the argument's order (`01|0123`): %s" % show(cxr, "0123", "x0123", "0123 01 0123"))
long_ok = all(r1[(rx, n)] == [0, 0, 0] for rx, _ in LONG for n in (2, 3))
dense_short_ok = all(r1[(rx, n)] == [0, 0, 0] for rx in (r"\d{1,3}?", r"\d|\d\d|\d\d\d", r"\d+?") for n in (2, 3))
sparse = r1[(r"1|0119", 2)]
print("PO %s" % check("PO reading 1: longest-first arguments equal; dense shortest-first equal; the sparse shortest-first `1|0119` parts",
      long_ok and dense_short_ok and sparse[0] == 0 and sparse[1] > 0 and fS(cx, "x0123") == "`0123`@1" and fS(cxr, "x0123") == "`01`@1"))

# reading 2: the unbounded lazy argument (the ruling's CONDITION) and rev 28.1's statement
print("PO reading 2 (the CONDITION): `\\d+?` and `\\d+` under the RULED body (above): lazy %s ; greedy %s"
      % (r1[(r"\d+?", 2)], r1[(r"\d+", 2)]))
lz = body(r"\d+?", 2)
print("PO `/${padded(/\\d+?/, 2)}/` the RULED body: %s" % show(lz, "0123", "x0123", "0123 7 01 9"))
print("PO the same, fill each string (`\\d+?` members shortest first, each filled; truncated to the subjects' digits 0-3, 7, 9 and length 4: HAND-WORKED): %s"
      % show(alt_rx(fill(enum(r"[0-379]{1,4}?"), 2)), "0123", "x0123", "0123 7 01 9"))
# rev 28.1's hand reduction of the any-length-first body for a lazy argument was `(?:[01]{2,}|[01]{2})` (GREEDY)
L01 = pool("01x", 5)
ref01 = alt_rx(fill(enum(r"[01]{1,5}?"), 2))
d_true, _ = diff3(body(r"[01]+?", 2, lazy_reduced=sab("t2")), ref01, L01)
d_281, _ = diff3(P.Pcre(r"(?:[01]{2,}|[01]{2})"), ref01, L01)
d_281l, _ = diff3(P.Pcre(r"(?:[01]{2,}?|[01]{2})"), ref01, L01)
print("PO lazy `[01]+?` at n = 2 over %d texts (`01x`, length <= 5): the RULED body RUN as written %d / %d / %d ; rev 28.1's reduction `(?:[01]{2,}|[01]{2})` %d / %d / %d (its `{2,}` is GREEDY: the reduction dropped the argument's `?`) ; the reduction with the `?` kept `(?:[01]{2,}?|[01]{2})` %d / %d / %d"
      % ((len(L01),) + tuple(d_true) + tuple(d_281) + tuple(d_281l)))
print("PO %s" % check("PO reading 2: the unbounded lazy argument equals fill under any-length-first; rev 28.1's 0 / 160 / 160 is its greedy reduction",
      r1[(r"\d+?", 2)] == [0, 0, 0] and r1[(r"\d+?", 3)] == [0, 0, 0] and d_true == [0, 0, 0] and d_281 == [0, 160, 160] and d_281l == [0, 0, 0]))

# [29.1] P29-6: the CONDITION's own witness. `\d+?` cannot separate the RULED body from the DROPPED exact-first body
# (both equal fill); a SPARSE lazy argument can.  The check below fails if the ruled body is replaced by the dropped one.
SP = pool("0129x", 6)
SP5 = pool("0129x", 5)                 # the dense reference (every member filled) is too large a PCRE pattern at length 6
def po3(rx_body, rx_trunc, n, texts, by_length=False):
    """fill in enumerate's order (PCRE PRIORITY ORDER, §5.5), or (by_length) the members sorted SHORTEST FIRST (a stable
    sort of the priority order: the reference review r54's verifier used, "lazy: shortest-first")"""
    mem = enum(rx_trunc)
    if by_length:
        mem = sorted(mem, key=len)
    fl = alt_rx(fill(mem, n))
    a, fa = diff3(body(rx_body, n), fl, texts)
    x, fx = diff3(body(rx_body, n, exact_first=True), fl, texts)
    ax, fax = diff3(body(rx_body, n), body(rx_body, n, exact_first=True), texts)
    return a, x, ax, (fa, fx, fax)
cond = {}
for lab, rxb, rxt, n in (("dense `\\d+?`", r"\d+?", r"[0129]{1,5}?", 2), ("dense `\\d+?`", r"\d+?", r"[0129]{1,5}?", 3),
                         ("SPARSE `(?:\\d\\d)+?`", r"(?:\d\d)+?", r"(?:[0129][0129]){1,3}?", 3),
                         ("SPARSE finite `(?:\\d\\d){1,2}?`", r"(?:\d\d){1,2}?", r"(?:[0129][0129]){1,2}?", 3)):
    if sab("t27") and lab.startswith("SPARSE"):
        continue
    tx = SP5 if lab.startswith("dense") else SP
    for bl in (False, True):
        a, x, ax, firsts = po3(rxb, rxt, n, tx, by_length=bl)
        cond[(lab, n, bl)] = (a, x, ax)
        print("PO [29.1] CONDITION witness %s n=%d over %d texts (`0129x`, length <= %d), fill in %s: RULED any-length-first vs fill %d / %d / %d ; DROPPED exact-first vs fill %d / %d / %d ; ruled vs dropped %d / %d / %d (first differences %s)"
              % ((lab, n, len(tx), 5 if tx is SP5 else 6, "SHORTEST-FIRST order (the verifier's)" if bl else "PRIORITY order (enumerate's)") + tuple(a) + tuple(x) + tuple(ax) + (firsts,)))
for rxb, n, w, s_, f_ in ((r"(?:\d\d)+?", 3, "0129", "x0129", "0129 0000 12"), (r"(?:\d\d){1,2}?", 3, "0129", "x0129", "0129 0000 12")):
    print("PO [29.1] `/${padded(/%s/, %d)}/` RULED (any-length first): %s" % (rxb, n, show(body(rxb, n), w, s_, f_)))
    print("PO [29.1]   the same, DROPPED (exact-width first): %s" % show(body(rxb, n, exact_first=True), w, s_, f_))
    tr = rxb.replace(r"\d", "[0129]").replace("+?", "{1,3}?")
    print("PO [29.1]   the same, fill each string in PRIORITY order (enumerate's): %s" % show(alt_rx(fill(enum(tr), n)), w, s_, f_))
    print("PO [29.1]   the same, fill each string SHORTEST FIRST: %s" % show(alt_rx(fill(sorted(enum(tr), key=len), n)), w, s_, f_))
    print("PO [29.1]   the priority-order witness SEARCHED `0000`: %s (ruled) ; %s (dropped) ; %s (fill, priority order) ; %s (fill, shortest first)"
          % (fS(body(rxb, n), "0000"), fS(body(rxb, n, exact_first=True), "0000"), fS(alt_rx(fill(enum(tr), n)), "0000"), fS(alt_rx(fill(sorted(enum(tr), key=len), n)), "0000")))
dense_ns = all(cond[("dense `\\d+?`", n, bl)] == ([0, 0, 0], [0, 0, 0], [0, 0, 0]) for n in (2, 3) for bl in (False, True))
sp = cond.get(("SPARSE `(?:\\d\\d)+?`", 3, True))
spf = cond.get(("SPARSE finite `(?:\\d\\d){1,2}?`", 3, True))
spp = cond.get(("SPARSE `(?:\\d\\d)+?`", 3, False))
print("PO %s" % check("PO [29.1] the CONDITION (P29-6): the dense `\\d+?` does not separate the bodies; the SPARSE lazy arguments do (shortest-first fill: the ruled body differs, the dropped body equals it; priority-order fill: neither equals it)",
      dense_ns and sp is not None and sp[0][0] == 0 and sp[0][1] > 0 and sp[1] == [0, 0, 0]
      and spf is not None and spf[0][1] > 0 and spf[1] == [0, 0, 0] and spp is not None and spp[0][1] > 0 and spp[1][1] > 0))

# the mixed-order argument (stated behaviour) and the prefix pair
mix = r1.get(("mix", 2)) or po_cmp(r"\d|\d\d\d|\d\d", r"[019]|[019][019][019]|[019][019]", 2, "MIXED `\\d|\\d\\d\\d|\\d\\d`")
mb = body(r"\d|\d\d\d|\d\d", 2)
mf_members = enum(r"[0-9]|[0-9][0-9][0-9]|[0-9][0-9]")
if sab("t3"):
    mf_members = sorted(mf_members, key=len, reverse=True)
mf = alt_rx(fill(mf_members, 2))
print("PO MIXED `/${padded(/\\d|\\d\\d\\d|\\d\\d/, 2)}/` the RULED body: %s" % show(mb, "000", "x000", "000 100 10"))
print("PO MIXED, fill each string in the argument's order: %s" % show(mf, "000", "x000", "000 100 10"))
pp = body(r"\d{2,3}", 2)
print("PO PREFIX PAIR `/${padded(/\\d{2,3}/, 2)}/` the RULED body: %s" % show(pp, "123", "x123", "123 12345"))
print("PO PREFIX PAIR, rev 28's exact-width-first body (dropped): %s"
      % show(P.Pcre(r"(?:\d{2}|\d{2,3})"), "123", "x123", "123 12345"))
print("PO %s" % check("PO mixed order parts (`000`: body `000`, fill `00`); prefix pair `123`@1",
      mix[1] > 0 and fS(mb, "x000") == "`000`@1" and fS(mf, "x000") == "`00`@1" and fS(pp, "x123") == "`123`@1"
      and fF(pp, "123 12345") == "[`123`@0, `123`@4, `45`@7]"))

# =====================================================================================================================
print("\n== PART FF: flags-scope RULED (\"i agree with your inherit table excepting that U should also not be inherited\")")
INHERIT = set("ims") | ({"U"} if sab("t4") else set())
def spell(outer, inner):
    """RULE-AS-CODE: the PCRE spelling of `/(?OUTER)...${/INNER/}.../` at the hole: the inserted literal starts with
    the INHERITED flags in force at the hole (i, m, s) and every other flag at its default; its own written flags win
    (they are inside it). `(?^...)` resets i m n s x xx; U is reset by an outer `(?-U:...)` (both checked by run)"""
    inh = "".join(f for f in "ims" if f in outer)
    g = "(?^%s:%s)" % (inh, inner)
    if "U" in outer:
        g = "(?U:%s)" % g if "U" in INHERIT else "(?-U:%s)" % g
    return g
# the spelling's own mechanics, by run: `(?^)` resets x and n; `(?-U:)` resets U
mech = [fW(P.Pcre(r"(?x)x(?^:a b)"), "xa b"), fW(P.Pcre(r"(?n)x(?^:(a)\1)"), "xaa"), fS(P.Pcre(r"(?U)x(?-U:(?^:a+))"), "xaaa"),
        fW(P.Pcre(r"(?xx)x(?^:[a b])"), "x "), fW(P.Pcre(r"(?i)x(?^i:ab)"), "XAB")]
print("FF the spelling's mechanics (libpcre2): `(?x)x(?^:a b)` WHOLE `xa b` %s ; `(?n)x(?^:(a)\\1)` WHOLE `xaa` %s ; `(?U)x(?-U:(?^:a+))` SEARCHED `xaaa` %s ; `(?xx)x(?^:[a b])` WHOLE `x ` %s ; `(?i)x(?^i:ab)` WHOLE `XAB` %s"
      % tuple(mech))
# the plain hole, one row per inline flag: (name, outer flags, program text, the PCRE spelling's outer/pre/post, inner, WHOLE, SEARCHED, FIND-ALL texts)
CASES = [
    ("i", "i", "/(?i)x${/ab/}/", "(?i)x", "ab", "", "XAB", "x XaB", "xab XAB"),
    ("m", "m", "/(?m)x${/a$/}\\nb/", "(?m)x", "a$", r"\nb", "xa\nb", "zxa\nb", "xa\nb xa\nb"),
    ("s", "s", "/(?s)x${/a./}/", "(?s)x", "a.", "", "xa\n", "zxa\n", "xa\n xab"),
    ("x (a space)", "x", "/(?x)x${/a b/}/", "(?x)x", "a b", "", "xa b", "z xab xa b", "xa b xab"),
    ("x (a `#`)", "x", "/(?x)x${/a#b/}/", "(?x)x", "a#b", "", "xa#b", "z xa#b", "xa#b xa"),
    ("xx", "xx", "/(?xx)x${/[a b]/}/", "(?xx)x", "[a b]", "", "x ", "zx xa", "x  xb"),
    ("n", "n", "/(?n)x${/(a)\\1/}/", "(?n)x", r"(a)\1", "", "xaa", "x xaa", "xaa xa xaa"),
    ("U", "U", "/(?U)x${/a+/}/", "(?U)x", "a+", "", "xaaa", "xaaa", "xaa xa"),
    ("a written `(?-i)` wins", "i", "/(?i)x${/(?-i)ab/}/", "(?i)x", "(?-i)ab", "", "XAB", "XAB Xab", "xab XAB Xab"),
    ("a written `(?U)` wins", "", "/x${/(?U)a+/}/", "x", "(?U)a+", "", "xaaa", "xaaa", "xaa xa"),
    ("branch carry", "i", "/(?:a(?i)b|${/c/})/", "(?:a(?i)b|", "c", ")", "C", "xC", "c C aB"),
]
# the expected answers, written BY HAND from the rulings and the record's statements (flags-scope entry: "`/(?n)x${/(a)\1/}/`
# is no longer a compile error; `/(?U)x${/a+/}/` SEARCHED `xaaa` gives `xaaa`@0 ...; a binding `/a b/` in a `(?x)` hole
# keeps its space")
EXP = {"i": ("HOLDS", "`XaB`@2", "[`xab`@0, `XAB`@4]"), "m": ("HOLDS", "`xa\\nb`@1", "[`xa\\nb`@0, `xa\\nb`@5]"),
       "s": ("HOLDS", "`xa\\n`@1", "[`xa\\n`@0, `xab`@4]"), "x (a space)": ("HOLDS", "`xa b`@6", "[`xa b`@0]"),
       "x (a `#`)": ("HOLDS", "`xa#b`@2", "[`xa#b`@0]"), "xx": ("HOLDS", "`x `@1", "[`x `@0, `xb`@3]"),
       "n": ("HOLDS", "`xaa`@2", "[`xaa`@0, `xaa`@7]"), "U": ("HOLDS", "`xaaa`@0", "[`xaa`@0, `xa`@4]"),
       "a written `(?-i)` wins": ("FAILS", "`Xab`@4", "[`xab`@0, `Xab`@8]"), "a written `(?U)` wins": ("HOLDS", "`xa`@0", "[`xa`@0, `xa`@4]"),
       "branch carry": ("HOLDS", "`C`@1", "[`c`@0, `C`@2, `aB`@4]")}
ffp = {}
for nm, outer, prog, pre, inner, post, w, s_, f_ in CASES:
    rx, err = compiles(pre + spell(outer, inner) + post)
    ffp[nm] = trip(rx, w, s_, f_) if rx else ("REJECTED (%s)" % err,)
    print("FF plain hole, %-24s `%s`: %s" % (nm, prog, show(rx, w, s_, f_) if rx else ffp[nm][0]))
for k in EXP:
    if ffp.get(k) != EXP[k]:
        print("FF MISMATCH %s: got %s expected %s" % (k, ffp.get(k), EXP[k]))
print("FF %s" % check("FF the plain hole, every inline flag, against the hand-written expectations", ffp == EXP))

# reading 12 (J) and 13 (numbered references): the inserted literal's references are its own
jt = {}
for nm, prog, pat, w2, s_, f_ in (
        ("J", "/(?J)(?<h>a)-${/(?<h>b)\\k<h>/}/", r"(?J)(?'h'a)-(?:(?'h'b)\k<h>)" if sab("t19") else r"(?J)(?<h>a)-(?:(?<g>b)\k<g>)", ("a-bb", "a-ba"), "x a-ba a-bb", "a-bb a-ba a-bb"),
        ("J, PCRE's text paste (rev 28.1's draft reading)", "", r"(?J)(?'h'a)-(?:(?'h'b)\k<h>)", ("a-bb", "a-ba"), "x a-ba a-bb", "a-bb a-ba a-bb"),
        ("numbered", "/(a)-${/(b)\\1/}/", r"(a)-(?:(b)\2)", ("a-bb", "a-ba"), "x a-ba a-bb", "a-bb a-ba a-bb"),
        ("numbered, the text paste", "", r"(a)-(?:(b)\1)", ("a-bb", "a-ba"), "x a-ba a-bb", "a-bb a-ba a-bb")):
    rx = P.Pcre(pat)
    jt[nm] = (fW(rx, w2[0]), fW(rx, w2[1]), fS(rx, s_), fF(rx, f_))
    print("FF %-46s %s (spelt `%s`): WHOLE `%s` %s, `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s"
          % (nm, prog, pat, w2[0], jt[nm][0], w2[1], jt[nm][1], s_, jt[nm][2], f_, jt[nm][3]))

# readings 3 and 4: an `&` inside a hole; a condition's set; a filter-role argument; an `&` at program level
def amp_hole(pre, outer, X, Y, post="", reach=True, w_flags_of_Y=None):
    """`/(?OUTER)pre${X & Y}post/`: the stretch X offers (X under the inherited flags), judged WHOLE by Y; Y under the
    inherited flags if the hole's flags REACH it (reading 3), else under its own"""
    yfl = outer if reach else ""
    Yp = P.Pcre(spell(yfl, Y))
    return P.Pcre(pre + "(?:(?<s>%s)(?C\"y\"))" % spell(outer, X) + post, {"y": lambda c: W(Yp, c.get("s") or "") is not None})
REACH = not sab("t5")
AMPS = [("i", "i", "(?i)x", "ab", "a."), ("m", "m", "(?m)x", r"a\nb", r"a$\nb"), ("s", "s", "(?s)x", r"a[\s\S]", "a."),
        ("x", "x", "(?x)x", r"a\ b", "a b"), ("n", "n", "(?n)x", r"(a)\g{-1}", r"(a)\1"), ("U", "U", "(?U)x", "a+", "a+")]
AW = {"i": ("XAB", "z XAB", "xab XAb"), "m": ("xa\nb", "zxa\nb", "xa\nb"), "s": ("xa\n", "zxa\n", "xa\n xab"),
      "x": ("xa b", "zxa b", "xa b"), "n": ("xaa", "x xaa", "xaa xaa"), "U": ("xaaa", "xaaa", "xaa xa")}
ar = {}
for nm, outer, pre, X, Y in AMPS:
    a_reach = amp_hole(pre, outer, X, Y, reach=REACH)
    a_own = amp_hole(pre, outer, X, Y, reach=False)
    w, s_, f_ = AW[nm]
    ar[nm] = (trip(a_reach, w, s_, f_), trip(a_own, w, s_, f_))
    print("FF `&` in a hole, %s: `/%s${/%s/ & /%s/}/` REACH (reading 3): %s" % (nm, pre, X, Y, show(a_reach, w, s_, f_)))
    print("FF   the same, the operands' OWN flags: %s" % show(a_own, w, s_, f_))
FP = pool("xXaAbB", 4)
dreach, _ = diff3(amp_hole("(?i)x", "i", "ab", "a.", reach=REACH), P.Pcre(r"(?i)x(?:ab)"), FP)
down, _ = diff3(amp_hole("(?i)x", "i", "ab", "a.", reach=False), P.Pcre(r"(?i)x(?:ab)"), FP)
print("FF `/(?i)x${/ab/ & /a./}/` against the plain hole `/(?i)x${/ab/}/` over %d texts (`xXaAbB`, length <= 4): REACH %d / %d / %d ; OWN %d / %d / %d"
      % ((len(FP),) + tuple(dreach) + tuple(down)))
# an `&` at PROGRAM level: no surrounding rx, each side its own flags
pl = P.Pcre(r'(?:(?<s>(?i)ab)(?C"y"))', {"y": lambda c: W(P.Pcre("a."), c.get("s") or "") is not None})
print("FF `&` at PROGRAM level `/(?i)ab/ & /a./` (each side its own flags): %s" % show(pl, "AB", "AB ab", "ab AB aB"))
print("FF %s" % check("FF reading 3: reach changes only the inherited flags (i m s); the not-inherited agree; = the plain hole; program level own",
      ar["i"][0] == ("HOLDS", "`XAB`@2", "[`xab`@0, `XAb`@4]") and ar["i"][1][0] == "FAILS"
      and ar["m"][0][0] == "HOLDS" and ar["m"][1][0] == "FAILS" and ar["s"][0][0] == "HOLDS" and ar["s"][1][0] == "FAILS"
      and all(ar[k][0] == ar[k][1] for k in ("x", "n", "U")) and ar["x"][0][0] == "HOLDS" and ar["n"][0][0] == "HOLDS" and ar["U"][0][1] == "`xaaa`@0"
      and dreach == [0, 0, 0] and down[0] > 0 and fW(pl, "AB") == "FAILS"))
# reading 4: a condition's set inside a hole, and a filter-role argument (quoted) inside a hole
cond_reach = amp_hole("(?i)x", "i", r"(?<w>\w\w)", "ab", reach=REACH)          # `/(?i)x${/(?<w>\w\w)/ & (w: /ab/)}/`
cond_own = amp_hole("(?i)x", "i", r"(?<w>\w\w)", "ab", reach=False)
print("FF a CONDITION'S SET in a hole `/(?i)x${/(?<w>\\w\\w)/ & (w: /ab/)}/` REACH: %s" % show(cond_reach, "XAB", "z XAB", "xab XAb"))
print("FF   the same, the set its OWN flags: %s" % show(cond_own, "XAB", "z XAB", "xab XAb"))
# quoted(S) := /"${S & /[^"]*/}"/ (§2.7's body), used at `/(?i)x${quoted(/ab/)}/`: two holes deep; the `&` inside quoted's hole
def quoted_in_hole(reach):
    inner_X = spell("i", "ab") if (reach and not sab("t6")) else "(?-i:ab)"
    Yq = P.Pcre(spell("i" if reach else "", r'[^"]*'))
    return P.Pcre(r'(?i)x(?:"(?:(?<s>%s)(?C"y"))")' % inner_X, {"y": lambda c: W(Yq, c.get("s") or "") is not None})
q_reach, q_own = quoted_in_hole(True), quoted_in_hole(False)
print("FF a FILTER-ROLE argument in a hole `/(?i)x${quoted(/ab/)}/` REACH (transitive): %s" % show(q_reach, 'x"AB"', 'z x"AB"', 'x"ab" x"Ab"'))
print("FF   the same, the operand its OWN flags (the manager's m2 of 2026-11-18): %s" % show(q_own, 'x"AB"', 'z x"AB"', 'x"ab" x"Ab"'))
print("FF %s" % check("FF reading 4: a condition's set and a filter-role argument under the same sentence",
      fW(cond_reach, "XAB") == "HOLDS" and fW(cond_own, "XAB") == "FAILS" and fW(q_reach, 'x"AB"') == "HOLDS" and fW(q_own, 'x"AB"') == "FAILS"))

# reading 5: transitive; reading 7: not-inherited at any depth
def nest(outer, pre, inner_b, depth_stop=False):
    """`B := /inner_b/`, `A := /x${B}/`, used at `/(?OUTER)pre${A}/`"""
    a_body = "x" + (spell("", inner_b) if depth_stop else "(?:%s)" % inner_b)
    return P.Pcre(pre + spell(outer, a_body))
t5_ = sab("t7")
nt = {}
for nm, outer, pre, ib, w, s_, f_ in (("i", "i", "(?i)", "ab", "XAB", "z XAB", "xab XAb"),
                                     ("x (not inherited)", "x", "(?x)", "a b", "xa b", "z xa b", "xa b xab"),
                                     ("U (not inherited)", "U", "(?U)", "a+", "xaaa", "xaaa", "xaa xa")):
    rx = nest(outer, pre, ib, depth_stop=t5_ and nm == "i")
    nt[nm] = trip(rx, w, s_, f_)
    print("FF transitive (reading 5/7) %s: B := /%s/, A := /x${B}/, `/%s${A}/`: %s" % (nm, ib, pre, show(rx, w, s_, f_)))
print("FF %s" % check("FF reading 5: B gets `i` through A; reading 7: `x`, `U` stay B's defaults at depth two",
      nt["i"] == ("HOLDS", "`XAB`@2", "[`xab`@0, `XAb`@4]") and nt["x (not inherited)"][0] == "HOLDS" and nt["U (not inherited)"][1] == "`xaaa`@0"))

# reading 6: a binding has no fixed string set; computed from A alone, A reads under A's own flags
A6 = "ab"
alone = enum(A6) if not sab("t8") else sorted({"".join(p) for p in itertools.product("aA", "bB")})
at_hole = sorted(t for t in pool("aAbB", 2) if W(P.Pcre("(?i)" + spell("i", A6)), t))
print("FF reading 6: A := /ab/: enumerate(A) (A alone, its own flags) = %s ; the strings `/(?i)${A}/` matches (over `aAbB`, length <= 2) = %s"
      % (alone, at_hole))
cnt = hole(r"(?i)(?<y>[a-zA-Z]+)=", lambda c, v: v == str(len(alone)))
print("FF   `/(?i)(?<y>\\w+)=${count_of(enumerate(A))}/` (count_of a placeholder: a value computed from A ALONE): %s" % show(cnt, "ab=1", "x ab=4 ab=1", "ab=1 AB=1 ab=4"))
print("FF %s" % check("FF reading 6: A alone has one string; at the hole four", alone == ["ab"] and len(at_hole) == 4 and fW(cnt, "ab=1") == "HOLDS"))
print("FF %s" % check("FF readings 12, 13: the inserted literal's `\\k<h>` and `\\1` are its own; the text paste reads the outer",
      jt["J"][:2] == ("HOLDS", "FAILS") and jt["J, PCRE's text paste (rev 28.1's draft reading)"][:2] == ("FAILS", "HOLDS")
      and jt["numbered"][:2] == ("HOLDS", "FAILS") and jt["numbered, the text paste"][:2] == ("FAILS", "HOLDS")
      and jt["J"][2] == "`a-bb`@7" and jt["J"][3] == "[`a-bb`@0, `a-bb`@10]"))

# =====================================================================================================================
print("\n== PART TX [29.1]: P29-1, the manager's reading 2: the inserted literal PARSED ALONE (it inherits only `i m s`)")
def lex_end(lit):
    """RULE-AS-CODE (the MODEL of "parsed alone", enough for the drills): walk the literal as a PCRE lexer would and
    return (inside an unterminated `\\Q`, inside an open `#` comment) at its END.  Tracks escapes, classes, `(?#...)`,
    and the `x` flag per group level (`(?x)`, `(?-x)`, `(?^)`, `(?x:...)`), starting OFF (`x` is not inherited)."""
    i, n, x, stack, q, com, cls = 0, len(lit), False, [], False, False, False
    while i < n:
        c = lit[i]
        if q:
            if lit.startswith("\\E", i):
                q, i = False, i + 2
            else:
                i += 1
            continue
        if com:
            com, i = (c != "\n"), i + 1
            continue
        if c == "\\":
            if lit.startswith("\\Q", i):
                q, i = True, i + 2
            else:
                i += 2
            continue
        if cls:
            cls, i = (c != "]"), i + 1
            continue
        if c == "[":
            cls, i = True, i + 1
            continue
        if x and c == "#":
            com, i = True, i + 1
            continue
        if c == "(":
            if lit.startswith("(?#", i):
                j = lit.find(")", i)
                i = n if j < 0 else j + 1
                continue
            m = re.match(r"\(\?([\^a-zA-Z-]*)([:)])", lit[i:])
            if m:
                fl, end, nx = m.group(1), m.group(2), x
                if fl.startswith("^"):
                    nx, fl = False, fl[1:]
                on, _, off = fl.partition("-")
                nx = True if "x" in on else nx
                nx = False if "x" in off else nx
                if end == ")":
                    x = nx
                else:
                    stack.append(x)
                    x = nx
                i += len(m.group(0))
                continue
            stack.append(x)
            i += 1
            continue
        if c == ")":
            x = stack.pop() if stack else x
        i += 1
    return q, com


def alone(outer, inner, groups_before, tag="q"):
    """RULE-AS-CODE: a MODEL spelling (never "the" text) of the literal `inner` PARSED ALONE at a hole whose flags in
    force are `outer`: it must compile ALONE; its own `\\Q` and `#` comment end at its end; its group NAMES and NUMBERS
    are its own (renamed / renumbered past the `groups_before` groups of the outer pattern and the wrapper); `(?R)`
    recurses the inserted literal (the wrapper group); it inherits only `i m s` (`(?^ims-subset:...)`), and an outer `U`
    is reset by `(?-U:...)`.  The wrapper is a NAMED capture (so `(?R)` can call it, and it captures under an outer
    `(?n)` too): the outer's later group numbers shift by one, which the spelled outer patterns below account for."""
    inh = "".join(f for f in "ims" if f in outer)
    P.Pcre(("(?%s)" % inh if inh else "") + inner)                 # legal ALONE (raises otherwise)
    q, com = lex_end(inner)
    body_ = inner if sab("t23") else inner + ("\\E" if q else "") + ("\n" if com else "")
    body_ = re.sub(r"\(\?<([A-Za-z_]\w*)>", lambda m: "(?<%s_%s>" % (tag, m.group(1)), body_)
    body_ = re.sub(r"\\k<([A-Za-z_]\w*)>", lambda m: "\\k<%s_%s>" % (tag, m.group(1)), body_)
    off = groups_before + 1
    body_ = re.sub(r"\(\?(\d+)\)", lambda m: "(?%d)" % (int(m.group(1)) + off), body_)
    body_ = body_.replace("(?R)", "(?&%s_W)" % tag)
    body_ = re.sub(r"\\(\d)", lambda m: "\\g{%d}" % (int(m.group(1)) + off), body_)
    g = "(?<%s_W>(?^%s:%s))" % (tag, inh, body_)
    if "U" in outer and not sab("t24"):
        g = "(?-U:%s)" % g
    return g


TXPOOL = pool("xab", 6)
tx = {}
# (a) U
ua = P.Pcre("(?U)x" + alone("U", "a+", 0))
up = P.Pcre("(?U)x(?^:a+)")
tx["a"] = (fS(ua, "xaaa"), fS(up, "xaaa"))
print("TX (a) `/(?U)x${/a+/}/` parsed alone (MODEL `%s`): %s" % (ua.pattern, show(ua, "xaaa", "xaaa", "xaa xa")))
print("TX     the `(?^...)` spelling alone, `(?U)x(?^:a+)` (`(?^)` does not reset `U`): %s" % show(up, "xaaa", "xaaa", "xaa xa"))
# (b) a written `(?x)` with a `#` comment
bb = P.Pcre("x" + alone("", "(?x)a #c", 0))
bp, berr = compiles("x(?^:(?x)a #c)")
_, berr_alone = compiles("(?x)a #c")
tx["b"] = (fW(bb, "xa"), berr is not None, berr_alone is None)
print("TX (b) `/x${/(?x)a #c/}/` parsed alone: %s ; the literal alone compiles: %s ; the text paste `x(?^:(?x)a #c)`: %s"
      % (show(bb, "xa", "z xa xb", "xa xa"), berr_alone is None, "COMPILE ERROR (%s)" % berr if berr else "compiles"))
# (c) an unterminated \Q
cc = P.Pcre("x" + alone("", "a\\Qb", 0))
cp, cerr = compiles("x(?^:a\\Qb)")
tx["c"] = (fW(cc, "xab"), cerr is not None)
print("TX (c) `/x${/a\\Qb/}/` parsed alone: %s ; the text paste `x(?^:a\\Qb)`: %s"
      % (show(cc, "xab", "z xab", "xab xab"), "COMPILE ERROR (%s)" % cerr if cerr else "compiles"))
# (d) recursion: (?R) and (?1) are the inserted literal's own
dd_ = P.Pcre("x" + alone("", "a(?R)?b", 0))
dp = P.Pcre("x(?^:a(?R)?b)")
d_cnt, d_first = diff3(dd_, dp, TXPOOL)
tx["d"] = (fW(dd_, "xaabb"), fW(dp, "xaabb"), d_cnt)
print("TX (d) `/x${/a(?R)?b/}/` parsed alone: %s" % show(dd_, "xaabb", "z xaabb", "xab xaabb"))
print("TX     the text paste `x(?^:a(?R)?b)` (`(?R)` the OUTER pattern): %s ; WHOLE `xaxabb` %s" % (show(dp, "xaabb", "z xaabb", "xab xaabb"), fW(dp, "xaxabb")))
print("TX     parsed alone vs the paste over %d texts (`xab`, length <= 6): %d / %d / %d (first %s)" % ((len(TXPOOL),) + tuple(d_cnt) + (d_first,)))
n1 = P.Pcre("(z)-" + alone("", "(a)(?1)", 1))
n1p = P.Pcre("(z)-(?^:(a)(?1))")
tx["d1"] = (fW(n1, "z-aa"), fW(n1, "z-az"), fW(n1p, "z-aa"), fW(n1p, "z-az"))
print("TX     `/(z)-${/(a)(?1)/}/` parsed alone: WHOLE `z-aa` %s, `z-az` %s ; the paste (`(?1)` the OUTER group 1): `z-aa` %s, `z-az` %s ; parsed alone %s"
      % (tx["d1"] + (show(n1, "z-aa", "x z-az z-aa", "z-aa z-az z-aa"),)))
print("TX %s" % check("TX [29.1] P29-1 drills: (a) `U` needs `(?-U:...)`; (b) a written `(?x)` `#` and (c) an open `\\\\Q` compile alone, not pasted; (d) `(?R)`, `(?1)` the literal's own",
      tx["a"] == ("`xaaa`@0", "`xa`@0") and tx["b"] == ("HOLDS", True, True) and tx["c"] == ("HOLDS", True)
      and tx["d"][:2] == ("HOLDS", "FAILS") and tx["d"][2][0] > 0 and tx["d1"] == ("HOLDS", "FAILS", "FAILS", "HOLDS")))
# the manager's reading 2: every printed rev 29 flags triple stands under "parsed alone" (re-derived from this model,
# not from the text paste): the plain-hole table (EXP above) and the J / numbered rows
txp = {}
for nm, outer, prog, pre, inner, post, w, s_, f_ in CASES:
    gb = len(re.findall(r"\((?!\?)", pre))
    rx, err = compiles(pre + alone(outer, inner, gb) + post)
    txp[nm] = trip(rx, w, s_, f_) if rx else ("REJECTED (%s)" % err,)
    if txp[nm] != EXP[nm]:
        print("TX MISMATCH %s: parsed alone %s ; printed %s" % (nm, txp[nm], EXP[nm]))
jn = P.Pcre("(?J)(?<h>a)-" + alone("", "(?<h>b)\\k<h>", 1))
nn = P.Pcre("(a)-" + alone("", "(b)\\1", 1))
txj = ((fW(jn, "a-bb"), fW(jn, "a-ba"), fS(jn, "x a-ba a-bb"), fF(jn, "a-bb a-ba a-bb")), (fW(nn, "a-bb"), fW(nn, "a-ba")))
print("TX reading 2: the %d plain-hole rows of PART FF re-derived parsed alone: %d equal the printed triples ; `J` row %s ; numbered row %s"
      % (len(CASES), sum(1 for k in EXP if txp.get(k) == EXP[k]), txj[0], txj[1]))
print("TX %s" % check("TX [29.1] the manager's reading 2: every printed rev 29 flags triple stands parsed alone",
      txp == EXP and txj == (("HOLDS", "FAILS", "`a-bb`@7", "[`a-bb`@0, `a-bb`@10]"), ("HOLDS", "FAILS"))))

# =====================================================================================================================
print("\n== PART FA [29.1]: P29-2, the `r` and `a`-family flags at a hole (UTF + UCP compile options)")
UTFO = 0x00080000 | 0x00020000
def _co(s, b): return len(s.encode()[:b].decode())
def vis(t): return t.replace("\u212a", "<U+212A>").replace("\u0663", "<U+0663>")
def uW(rx, s): return "FAILS" if rx.match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED) is None else "HOLDS"
def uS(rx, s):
    r = rx.match(s, 0)
    if r is None:
        return "FAILS"
    a, b = _co(s, r[0]), _co(s, r[1])
    return "`%s`@%d" % (vis(s[a:b]), a)
def uF(rx, s):
    out, pos = [], 0
    sb = s.encode()
    while pos <= len(sb):
        r = rx.match(s, pos)
        if r is None:
            break
        a, b = _co(s, r[0]), _co(s, r[1])
        out.append("`%s`@%d" % (vis(s[a:b]), a))
        pos = r[1] if r[1] > r[0] else r[1] + 1
    return "[" + ", ".join(out) + "]"
def ushow(rx, w, s_, f_):
    return "WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % (vis(w), uW(rx, w), vis(s_), uS(rx, s_), vis(f_), uF(rx, f_))
def urow(rx, s, m):
    if m == "W":
        return rx.match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED) is not None
    if m == "S":
        r = rx.match(s, 0)
        return None if r is None else r[:2]
    return uF(rx, s)
def udiff(r1, r2, texts):
    return [sum(1 for t in texts if urow(r1, t, m) != urow(r2, t, m)) for m in "WSF"]
K, AR3 = "\u212a", "\u0663"
mechs = [uW(P.Pcre("(?i)k", opts=UTFO), K), uW(P.Pcre("(?ir)k", opts=UTFO), K), uW(P.Pcre("(?ir)x(?^i:k)", opts=UTFO), "x" + K),
         uW(P.Pcre("(?aD)x(?^:\\d)", opts=UTFO), "x" + AR3), uW(P.Pcre("(?aD)x(?-aD:(?^:\\d))", opts=UTFO), "x" + AR3)]
print("FA mechanics (libpcre2, UTF+UCP): `(?i)k` WHOLE <U+212A> %s ; `(?ir)k` %s ; `(?ir)x(?^i:k)` `x<U+212A>` %s (`(?^)` resets `r`) ; `(?aD)x(?^:\\d)` `x<U+0663>` %s (`(?^)` does NOT reset `aD`) ; `(?aD)x(?-aD:(?^:\\d))` %s"
      % tuple(mechs))
fa = {}
rin, rout = P.Pcre("(?ir)x(?^ir:k)", opts=UTFO), P.Pcre("(?ir)x(?^i:k)", opts=UTFO)
a_in = "(?aD)x(?-aD:(?^:\\d))" if sab("t25") else "(?aD)x(?^:\\d)"
ain, aout = P.Pcre(a_in, opts=UTFO), P.Pcre("(?aD)x(?-aD:(?^:\\d))", opts=UTFO)
RP, AP = pool("xk" + K, 4), pool("x3" + AR3, 4)
for nm, r1, r2, w, s_, f_, tp in (("`/(?ir)x${/k/}/`", rin, rout, "x" + K, "zx" + K + " xk", "xk x" + K + " xK", RP),
                                  ("`/(?aD)x${/\\d/}/`", ain, aout, "x" + AR3, "zx" + AR3 + " x3", "x3 x" + AR3 + " x7", AP)):
    fa[nm] = (ushow(r1, w, s_, f_), ushow(r2, w, s_, f_), udiff(r1, r2, tp), len(tp))
    print("FA %s INHERITED (THE DRAFT'S READING): %s" % (nm, fa[nm][0]))
    print("FA %s NOT inherited: %s ; inherited vs not over %d texts: %d / %d / %d" % ((nm, fa[nm][1], fa[nm][3]) + tuple(fa[nm][2])))
print("FA %s" % check("FA [29.1] P29-2: `(?^)` resets `r`, not `aD`; inherited and not inherited part on both flags",
      mechs == ["HOLDS", "FAILS", "HOLDS", "FAILS", "HOLDS"] and uW(ain, "x" + AR3) == "FAILS" and uW(aout, "x" + AR3) == "HOLDS"
      and uW(rin, "x" + K) == "FAILS" and uW(rout, "x" + K) == "HOLDS" and all(v[2][0] > 0 for v in fa.values())))

# =====================================================================================================================
print("\n== PART SQ [29.1]: P29-3, the manager's reading 3: the flags of a SEQUENCE operand")
sq_own = P.Pcre("(?i)xab" if sab("t26") else "(?:(?i)x)(?:ab)")
sq_cat = P.Pcre("(?i)xab")
sqd, sqf = diff3(sq_own, sq_cat, FP)
print("SQ `/(?i)x/ SEQ /ab/` each operand its own flags (THE DRAFT'S READING; nothing passes sideways): %s" % show(sq_own, "XAB", "z XAB Xab", "xab XAB Xab"))
print("SQ   WHOLE `Xab` %s" % fW(sq_own, "Xab"))
print("SQ   the text concatenation `(?i)xab` (the flag passes sideways): %s ; the two over %d texts (`xXaAbB`, length <= 4): %d / %d / %d (first %s)"
      % ((show(sq_cat, "XAB", "z XAB Xab", "xab XAB Xab"), len(FP)) + tuple(sqd) + (sqf,)))
sq_in = P.Pcre("(?i)z(?:%s%s)" % (spell("i", "x"), spell("i", "ab")))
print("SQ inside `(?i)` surroundings `/(?i)z${/x/ SEQ /ab/}/` (both operands inherit): %s" % show(sq_in, "ZXAB", "q ZXAB", "zxab ZXAB zXaB"))
print("SQ %s" % check("SQ [29.1] the manager's reading 3: `XAB` FAILS, `Xab` HOLDS; inside `(?i)` both operands inherit",
      fW(sq_own, "XAB") == "FAILS" and fW(sq_own, "Xab") == "HOLDS" and sqd[0] > 0 and fW(sq_in, "ZXAB") == "HOLDS"))

# =====================================================================================================================
print("\n== PART CO: class-order RULED (\"class-order: longest\"): a class position's lifted results, the LONGER first")
DIG = "0123456789"
def by_len(rs):
    """a CLASS POSITION's results: the longer first; equal lengths in any order (stable here)"""
    rs = [r for r in rs if r is not None]
    return rs if sab("t9") else sorted(rs, key=len, reverse=True)
def uniq(rs):
    if sab("t12"):
        return list(rs)
    seen, out = set(), []
    for r in rs:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out
CP = pool("0123x", 5)
d1 = uniq(by_len(arith(d, "+", 1) for d in DIG))
co1 = alt_rx(d1)
print("CO `/${\\d + 1}/` = %s: %s" % ("|".join(d1), show(co1, "10", "x10", "10 3 11")))
# reading 8: no tie rule: shuffle the equal-length results 20 ways
rng = random.Random(29)
def shuffled_eq(rs):
    out, i = [], 0
    while i < len(rs):
        j = i
        while j < len(rs) and len(rs[j]) == len(rs[i]):
            j += 1
        blk = rs[i:j]
        rng.shuffle(blk)
        out += blk
        i = j
    return out
sh = [0, 0, 0]
for _ in range(20):
    d, _f = diff3(co1, alt_rx(shuffled_eq(list(d1))), CP)
    sh = [a + b for a, b in zip(sh, d)]
nest19 = [r for a in ("1", "9") for r in by_len(arith(a, "+", int(d)) for d in DIG)]
sh2 = [0, 0, 0]
for _ in range(20):
    blocks = [by_len(arith(a, "+", int(d)) for d in DIG) for a in ("1", "9")]
    d, _f = diff3(alt_rx(nest19), alt_rx([r for b in blocks for r in shuffled_eq(b)]), CP)
    sh2 = [a + b for a, b in zip(sh2, d)]
print("CO reading 8: equal-length results shuffled 20 ways, over %d texts (`0123x`, length <= 5): `\\d + 1` %d / %d / %d ; `(1|9) + \\d` %d / %d / %d"
      % ((len(CP),) + tuple(sh) + tuple(sh2)))
cpo = alt_rx([arith(d, "+", 1) for d in DIG])
dcp, _ = diff3(co1, cpo, CP)
print("CO `\\d + 1` LONGEST against the replaced CODEPOINT lean (`1|...|10`): %d / %d / %d ; codepoint: %s" % (tuple(dcp) + (show(cpo, "10", "x10", "10 3 11"),)))
print("CO %s" % check("CO reading 8 and the ruled order on `\\d + 1`", sh == [0, 0, 0] and sh2 == [0, 0, 0]
      and trip(co1, "10", "x10", "10 3 11") == ("HOLDS", "`10`@1", "[`10`@0, `3`@3, `1`@5, `1`@6]")))
# reading 9: nesting; the user's alternation keeps its order
if sab("t10"):
    nest19 = sorted(nest19, key=len, reverse=True)
n19 = alt_rx(nest19)
glob19 = alt_rx(sorted([arith(a, "+", int(d)) for a in ("1", "9") for d in DIG], key=len, reverse=True))
dn, _ = diff3(n19, glob19, CP)
print("CO reading 9 `/${(1|9) + \\d}/` NESTED (the alternation's order kept, each choice's class results longest first) = %s: %s"
      % ("|".join(uniq(nest19)), show(n19, "11", "x11", "11 1 18")))
print("CO   the same sorted longest first ACROSS the alternation: %s ; nested vs across %d / %d / %d" % ((show(glob19, "11", "x11", "11 1 18"),) + tuple(dn)))
n39 = alt_rx([r for a in ("3", "9") for r in by_len(arith(a, "+", int(d)) for d in DIG)])
g39 = alt_rx(sorted([arith(a, "+", int(d)) for a in ("3", "9") for d in DIG], key=len, reverse=True))
d39, _ = diff3(n39, g39, CP)
print("CO   the record's `(3|9) + \\d`: nested vs across %d / %d / %d (no result of one length is a prefix of one of the other at a shared start)" % tuple(d39))
print("CO %s" % check("CO reading 9: nested parts from across on `(1|9) + \\d`", fS(n19, "x11") == "`1`@1" and fS(glob19, "x11") == "`11`@1" and dn[1] > 0))
# reading 10: two class positions in one lift; a class under a quantifier: candidates
def two_class(order_first):
    """`\\d + \\d`: candidate C1 every result of the lift longest first (the lift as ONE position); C2/C3 the first class
    position slowest (its members in ascending / descending order: a class has no order), the second's results longest
    first within each"""
    if order_first == "C1":
        return sorted([arith(a, "+", int(b)) for a in DIG for b in DIG], key=len, reverse=True)
    firsts = DIG if order_first == "C2" else DIG[::-1]
    if sab("t11") and order_first == "C2":
        return two_class("C1")
    return [r for a in firsts for r in by_len(arith(a, "+", int(b)) for b in DIG)]
tc = {k: alt_rx(two_class(k)) for k in ("C1", "C2", "C3")}
for k in tc:
    print("CO reading 10 `/${\\d + \\d}/` %s: %s" % (k, show(tc[k], "13", "x13", "13 4 18")))
d12, _ = diff3(tc["C1"], tc["C2"], CP); d13, _ = diff3(tc["C1"], tc["C3"], CP)
print("CO   C1 vs C2 %d / %d / %d ; C1 vs C3 %d / %d / %d" % (tuple(d12) + tuple(d13)))
# `\d\d + 1`: the operand has two class positions
dd_ops = [a + b for a in DIG for b in DIG]
P1 = sorted([arith(m, "+", 1) for m in dd_ops if arith(m, "+", 1)], key=len, reverse=True)
P2 = [r for a in DIG for r in by_len(arith(a + b, "+", 1) for b in DIG)]
P3 = [r for a in DIG[::-1] for r in by_len(arith(a + b, "+", 1) for b in DIG)]
ddp = {k: alt_rx(v) for k, v in (("P1", P1), ("P2", P2), ("P3", P3))}
dP12, _ = diff3(ddp["P1"], ddp["P2"], CP); dP13, _ = diff3(ddp["P1"], ddp["P3"], CP)
print("CO reading 10 `/${\\d\\d + 1}/` P1 (one position): %s ; P1 vs P2 (first class slowest, ascending) %d / %d / %d ; P1 vs P3 (descending) %d / %d / %d"
      % ((show(ddp["P1"], "100", "x100", "100 12 99"),) + tuple(dP12) + tuple(dP13)))
# a class under a quantifier: `\d{1,2} + 1` and the lazy `\d{1,2}? + 1`
def quant(lazy, cand):
    """Q1: the quantifier's order kept (greedy: two copies first; lazy: one copy first), each count's results longest
    first; Q2: every result of the quantified class longest first (the quantified class as ONE position)"""
    groups = [[a + b for a in DIG for b in DIG], list(DIG)]
    if lazy:
        groups = groups[::-1]
    if cand == "Q2":
        return sorted([arith(m, "+", 1) for g in groups for m in g if arith(m, "+", 1)], key=len, reverse=True)
    return [r for g in groups for r in by_len(arith(m, "+", 1) for m in g)]
qd = {}
for lazy in (False, True):
    q1, q2 = alt_rx(quant(lazy, "Q1")), alt_rx(quant(lazy, "Q2"))
    d, _ = diff3(q1, q2, CP)
    qd[lazy] = (d, trip(q1, "100", "x100", "100 10 9"), trip(q2, "100", "x100", "100 10 9"))
    print("CO reading 10 `/${\\d{1,2}%s + 1}/` Q1 (quantifier order kept): %s ; Q2 (one position): %s ; Q1 vs Q2 %d / %d / %d"
          % (("?" if lazy else ""), show(q1, "100", "x100", "100 10 9"), show(q2, "100", "x100", "100 10 9"), d[0], d[1], d[2]))
print("CO %s" % check("CO reading 10: the candidates part on `\\d + \\d` and the lazy quantifier; agree on `\\d\\d + 1`",
      d12[1] > 0 and d13 == [0, 0, 0] and dP12 == [0, 0, 0] and dP13 == [0, 0, 0] and qd[True][0][1] > 0 and qd[False][0] == [0, 0, 0]))
# reading 11: equal strings are one result
z = uniq(by_len(arith(d, "*", 0) for d in DIG))
dz, _ = diff3(alt_rx(z), P.Pcre("0"), CP)
print("CO reading 11 `/${\\d * 0}/`: the results %s ; vs `/0/` %d / %d / %d ; %s" % ((z,) + tuple(dz) + (show(alt_rx(z), "0", "x0", "0 00"),)))
print("CO %s" % check("CO reading 11: one result", z == ["0"] and dz == [0, 0, 0]))
# the ARRAY interface of enumerate keeps an order among equal-length members (§5.5's `.index`)
arr = enum(r"[-/.]")
print("CO enumerate(/[-\\/.]/) as an ARRAY (§5.5's example, codepoint): %s ; `.index` of `/` = %d ; in DESCENDING order it would be %d (no match answer differs: equal lengths)"
      % (arr, arr.index("/") + 1, arr[::-1].index("/") + 1))

# [29.1] P29-9: the class FIRST, `\d + (1|9)`: reading A (the user's alternation order outermost, whatever its operand
# position; each choice's class results longest first) vs reading B (the class position's results longest first
# across the whole lift; "first operand slowest" puts the class outermost); C2 / C3 (class members outermost, ascending /
# descending, the alternation's order inside each) for reference
cfA = uniq([r for alt in ("1", "9") for r in by_len(arith(d, "+", int(alt)) for d in DIG)])
if sab("t32"):
    cfA = uniq(sorted([arith(d, "+", int(alt)) for d in DIG for alt in ("1", "9")], key=len, reverse=True))
cfB = uniq(sorted([arith(d, "+", int(alt)) for d in DIG for alt in ("1", "9")], key=len, reverse=True))
cfC2 = uniq([arith(d, "+", int(alt)) for d in DIG for alt in ("1", "9")])
cfC3 = uniq([arith(d, "+", int(alt)) for d in DIG[::-1] for alt in ("1", "9")])
cfr = {k: alt_rx(v) for k, v in (("A", cfA), ("B", cfB), ("C2", cfC2), ("C3", cfC3))}
for k in ("A", "B", "C2", "C3"):
    print("CO [29.1] P29-9 `/${\\d + (1|9)}/` reading %s = %s: %s" % (k, "|".join(cfr[k].pattern[3:-1].split("|")[:12]) + "|...", show(cfr[k], "11", "x11", "11 3 18")))
cAB, _ = diff3(cfr["A"], cfr["B"], CP); cC, _ = diff3(cfr["C2"], cfr["C3"], CP)
cBC3, _ = diff3(cfr["B"], cfr["C3"], CP); cAC2, _ = diff3(cfr["A"], cfr["C2"], CP)
print("CO [29.1]   over %d texts (`0123x`, length <= 5): A vs B %d / %d / %d ; C2 vs C3 %d / %d / %d ; B vs C3 %d / %d / %d ; A vs C2 %d / %d / %d"
      % ((len(CP),) + tuple(cAB) + tuple(cC) + tuple(cBC3) + tuple(cAC2)))
print("CO %s" % check("CO [29.1] P29-9: the class first; readings A and B part (`x11`: A `1`@1, B `11`@1)",
      fS(cfr["A"], "x11") == "`1`@1" and fS(cfr["B"], "x11") == "`11`@1" and cAB[1] > 0 and cBC3 == [0, 0, 0]))
# [29.1] P29-10: `enumerate(/\d/) + 1`: (a) the ARRAY interface only keeps codepoint order, the lift follows class-order
# (= `\d + 1`); (b) the array's codepoint order everywhere, lifts included (array-lift: "values in the order given");
# (c) review r54's GENERAL-6 form: ONE order wherever a class's member order is observable, the longer result first,
# ties by codepoint (= (a) on this lift; bare `enumerate(/\d/)` stays codepoint)
earr = enum(r"\d")
ci = {"a": co1, "b": alt_rx([arith(m, "+", 1) for m in earr]), "c": alt_rx(sorted([arith(m, "+", 1) for m in earr], key=lambda r: (-len(r), r)))}
if sab("t35"):
    ci["b"] = co1
for k in "abc":
    print("CO [29.1] P29-10 `/${enumerate(/\\d/) + 1}/` candidate (%s): %s" % (k, show(ci[k], "10", "x10", "10 3 11")))
dab, _ = diff3(ci["a"], ci["b"], CP); dac, _ = diff3(ci["a"], ci["c"], CP)
print("CO [29.1]   (a) vs (b) %d / %d / %d ; (a) vs (c) %d / %d / %d of %d ; bare `enumerate(/\\d/)` as an ARRAY: %s under (a), (b) and (c)"
      % (tuple(dab) + tuple(dac) + (len(CP), earr)))
print("CO %s" % check("CO [29.1] P29-10: `enumerate(/\\d/) + 1` as an array lift (codepoint) parts from `\\d + 1` (`x10`)",
      dab[1] > 0 and dac == [0, 0, 0] and fS(ci["b"], "x10") == "`1`@1" and fS(ci["a"], "x10") == "`10`@1"))

# =====================================================================================================================
print("\n== PART NE: number-edges RULED (\"number-edge: nothing\"); reading 14")
ne = {}
for nm, op, k, w1, w2, s_, f_ in (("`% 0`", "%", 0, "5-0", "5-5", "x5-0 5-5", "5-0 7-7 0-0"), ("`- 10`", "-", 10, "15-5", "5--5", "5--5 15-5", "15-5 5--5 10-0")):
    h = hole(r'(?<y>\d+)-', lambda c, v, op=op, k=k: v is not None and v == arith(c.get("y"), op, k))
    ne[nm] = (fW(h, w1), fW(h, w2), fS(h, s_), fF(h, f_))
    print("NE `/(?<y>\\d+)-${$y %s %d}/`: WHOLE %s %s, %s %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % (op, k, w1, ne[nm][0], w2, ne[nm][1], s_, ne[nm][2], f_, ne[nm][3]))
NP = pool("0157-", 5)
never = sum(1 for t in NP for m in "WSF" if row(hole(r'(?<y>\d+)-', lambda c, v: v is not None and v == arith(c.get("y"), "%", 0)), t, m) not in (False, None, ()))
lift0 = uniq(by_len(arith(d, "%", 0) for d in DIG))
print("NE `/(?<y>\\d+)-${$y %% 0}/` hits over %d texts (`0157-`, length <= 5), every mode: %d ; the compile-time lift `\\d %% 0` keeps %d of 10 results (every one removed: the hole has ZERO values)"
      % (len(NP), never, len(lift0)))
print("NE %s" % check("NE `% 0` never holds; a negative result yields nothing; the constant lift is empty",
      ne["`% 0`"] == ("FAILS", "FAILS", "FAILS", "[]") and ne["`- 10`"] == ("HOLDS", "FAILS", "`15-5`@5", "[`15-5`@0, `10-0`@10]")
      and never == 0 and lift0 == []))

# =====================================================================================================================
print("\n== PART DD: dollar-diagnostic RULED (\"the form $x & .. should just get a warning\"); reading 16 [29.1: P29-11, P29-12]")
class Prs:
    """[29.1] RULE-AS-CODE: a small parser of the program text, enough for the drill: `&` (level 7, n-ary) over `+ -`
    (level 5) over atoms: `( e )`, a condition `(name: e)`, a regex literal `/../` whose holes `${ e }` are parsed, a
    string literal `".."` (opaque: nothing inside it is code), a read `$name(.name)*`, a comparison set `<5`, a number."""
    def __init__(self, t):
        self.t, self.i = t, 0
    def ws(self):
        while self.i < len(self.t) and self.t[self.i] == " ":
            self.i += 1
    def peek(self):
        self.ws()
        return self.t[self.i] if self.i < len(self.t) else ""
    def expr(self):
        ops = [self.sum_()]
        while self.peek() == "&":
            self.i += 1
            ops.append(self.sum_())
        return ops[0] if len(ops) == 1 else ("and", ops)
    def sum_(self):
        ops = [self.atom()]
        while self.peek() in ("+", "-"):
            self.i += 1
            ops.append(self.atom())
        return ops[0] if len(ops) == 1 else ("sum", ops)
    def atom(self):
        c, t = self.peek(), self.t
        if c == "(":
            m = re.match(r"\(\s*([A-Za-z_]\w*)\s*:", t[self.i:])
            if m:
                self.i += len(m.group(0))
                e = self.expr()
                assert self.peek() == ")"
                self.i += 1
                return ("cond", m.group(1), e)
            self.i += 1
            e = self.expr()
            assert self.peek() == ")", (t, self.i)
            self.i += 1
            return ("paren", e)
        if c == "/":
            j, holes = self.i + 1, []
            while t[j] != "/":
                if t[j] == "\\":
                    j += 2
                    continue
                if t.startswith("${", j):
                    sub = Prs(t)
                    sub.i = j + 2
                    holes.append(sub.expr())
                    assert sub.peek() == "}"
                    j = sub.i + 1
                    continue
                j += 1
            self.i = j + 1
            return ("rx", holes)
        if c == '"':
            j = t.index('"', self.i + 1)
            self.i = j + 1
            return ("str",)
        m = re.match(r"\$[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*", t[self.i:])
        if m:
            self.i += len(m.group(0))
            return ("read", m.group(0))
        m = re.match(r"(?:<=|>=|<|>)\s*\d+|\d+", t[self.i:])
        assert m, (t, self.i)
        self.i += len(m.group(0))
        return ("cmp" if m.group(0)[0] in "<>" else "num",)


def strip(e):
    while e[0] == "paren":
        e = e[1]
    return e


def dollar_sites(prog):
    """[29.1] THE MANAGER'S CALL (P29-11): the warned form is an `&` one of whose operands is a label read or a path
    read, parenthesised or not, on either side.  Returns [(the place, the hint)]: the `(x: S)` HINT only where the form
    is a drop-in, an `&` operand (P29-12, THE MANAGER'S CALL); in a hole it is omitted."""
    if sab("t29"):
        return [("lexical", True)] if re.search(r"\$\w+\s*&", prog) else []
    out = []
    def walk(e, place):
        k = e[0]
        if k == "and":
            if any(strip(o)[0] == "read" for o in e[1]):
                out.append((place, place == "and-operand" or sab("t30")))
            for o in e[1]:
                walk(o, "and-operand")
        elif k == "sum":
            for o in e[1]:
                walk(o, "sum-operand")
        elif k == "paren":
            walk(e[1], place)
        elif k == "cond":
            walk(e[2], "condition")
        elif k == "rx":
            for h in e[1]:
                walk(h, "hole")
    p = Prs(prog)
    tree = p.expr()
    assert p.i == len(prog), (prog, p.i)
    walk(tree, "top")
    return out


def warns(prog):
    """the warning fires (rev 29's PROGS keep their verdicts under the parse-defined form)"""
    if sab("t14"):
        return prog in ("/(?<x>\\d+)-/ & ($x & <5)",)        # keyed on emptiness instead: only the never-holding one
    return bool(dollar_sites(prog))
PROGS = ["/(?<x>\\d+)-/ & ($x & <5)", "/(?<x>\\d+)/ & ($x & <5)", "/(?<x>\\d+)/ & (x: <5)", "/(?<y>\\d+)-${$y & <5}/", "/(?<x>\\d+)/"]
for p in PROGS:
    print("DD %-34s the warning: %s" % (p, "FIRES (points at `(x: S)`)" if warns(p) else "silent"))
lt5 = lambda t: canon(t) and int(t) < 5
DP = pool("37-", 5)
dol = P.Pcre(r'(?<x>\d+)(?C"f")', {"f": lambda c: c.stretch() == c.get("x") and lt5(c.get("x"))})   # stretch = $x and $x < 5
cnd = P.Pcre(r'(?<x>\d+)(?C"f")', {"f": lambda c: lt5(c.get("x"))})                                # (x: <5)
ddd, _ = diff3(dol, cnd, DP)
print("DD `/(?<x>\\d+)/ & ($x & <5)` vs `/(?<x>\\d+)/ & (x: <5)` over %d texts (`37-`, length <= 5): %d / %d / %d ; %s"
      % ((len(DP),) + tuple(ddd) + (show(dol, "3", "x7 3", "3 7 33 4"),)))
print("DD %s" % check("DD reading 16: fires on every `$x & S`, including the right one; never on `(x: S)`; the right one equals its suggestion",
      [warns(p) for p in PROGS] == [True, True, False, True, False] and ddd == [0, 0, 0]))

# [29.1] P29-11 the parse drill (the manager's reading 4), and P29-12 the hint keyed on the place
DRILL = [("($x) & <5", True), ("<5 & $x", True), ("$d.year & <2000", True), ("1 + $x & <5", False), ("\"$x & <5\"", False),
         ("/(?<x>\\d+)/ & (($x) & <5)", True), ("/(?<x>\\d+)/ & (<5 & $x)", True), ("/d/ & ($d.year & <2000)", True),
         ("/(?<x>\\d+)/ & (1 + $x & <5)", False), ("/(?<x>\\d+)/ & \"$x & <5\"", False), ("/(?<x>\\d+)/ & ($x + $y & <50)", False),
         ("/(?<x>\\d+)/ & (($x + $y) & <50)", False), ("/(?<x>\\d)(?<y>\\d)/ & ($x & $y)", True)]
dr = {}
for prog, want in DRILL:
    st = dollar_sites(prog)
    dr[prog] = bool(st)
    lex = re.search(r"\$\w+\s*&", prog) is not None
    print("DD [29.1] parse drill %-36s the warning: %-6s (rev 29's lexical trigger: %s)%s"
          % (prog, "FIRES" if st else "silent", "fires" if lex else "silent", "" if dr[prog] == want else "  <- NOT the expected verdict"))
print("DD %s" % check("DD [29.1] P29-11 / the manager's reading 4: the form defined on the parse (parenthesised, mirrored, a path; not a sum; not in a string)",
      all(dr[p] == w for p, w in DRILL)))
HINTP = ["/(?<x>\\d+)/ & ($x & <5)", "/(?<x>\\d+)-/ & ($x & <5)", "/(?<y>\\d+)-${$y & <5}/", "/(?<x>\\d+)/ & (<5 & $x)"]
hp = {}
for prog in HINTP:
    hp[prog] = dollar_sites(prog)
    print("DD [29.1] P29-12 %-32s the warning at: %s" % (prog, ", ".join("%s, hint `(x: S)` %s" % (pl, "PRINTED" if h else "OMITTED") for pl, h in hp[prog])))
# the value-hole witness (R.1.15 (12)'s idiom) against the hint applied there as a zero-width condition at that point
# (the legal spelling: a sequenced condition, `/(?<y>\d+)-/ SEQ (y: <5)`)
vh = hole(r"(?<y>\d+)-", lambda c, v: v is not None and v == c.get("y") and lt5(c.get("y")))
vc = P.Pcre(r'(?<y>\d+)-(?C"f")', {"f": lambda c: lt5(c.get("y"))})
dvh, fvh = diff3(vh, vc, DP)
print("DD [29.1] `/(?<y>\\d+)-${$y & <5}/`: %s" % show(vh, "3-3", "x 7-7 3-3", "3-3 3- 7-7"))
print("DD [29.1]   the hint applied in the hole (as the condition at that point): %s ; the two over %d texts (`37-`, length <= 5): %d / %d / %d (first %s)"
      % ((show(vc, "3-3", "x 7-7 3-3", "3-3 3- 7-7"), len(DP)) + tuple(dvh) + (fvh,)))
print("DD %s" % check("DD [29.1] P29-12: the hint printed at an `&` operand, omitted in a hole; there it would change the answer",
      [h for _, h in hp["/(?<x>\\d+)/ & ($x & <5)"]] == [True] and [h for _, h in hp["/(?<y>\\d+)-${$y & <5}/"]] == [False]
      and fW(vh, "3-3") == "HOLDS" and fW(vc, "3-3") == "FAILS" and dvh[1] > 0))

# =====================================================================================================================
print("\n== PART SC: same-name-count RULED (\"same-name-count: scoped\"); reading 15 (`$h` the last mention)")
# q := /(?<h>b)/ ; `/(?<h>a)-${q};${$h}\k<h>/`: \k<h> the OUTER group (scoped); $h the LAST MENTION (q's public h,
# export-rule (2)-(3), R.1.13 label-flow (3))
kref = "qh" if sab("t15") else "h"
sc = P.Pcre(r"(?<h>a)-(?:(?<qh>b));\k<qh>\k<%s>" % kref)
sc_alt = P.Pcre(r"(?<h>a)-(?:(?<qh>b));\k<h>\k<h>")          # $h read as the OUTER group (not the rules as defined)
print("SC `/(?<h>a)-${q};${$h}\\k<h>/`, q := /(?<h>b)/: `$h` the last mention (q's), `\\k<h>` the outer: %s" % show(sc, "a-b;ba", "x a-b;aa a-b;ba", "a-b;ba a-b;bb a-b;ba"))
print("SC   the same with `$h` read as the OUTER group (not the rules as defined): %s" % show(sc_alt, "a-b;ba", "x a-b;aa a-b;ba", "a-b;ba a-b;bb a-b;ba"))
scq = P.Pcre(r"(?<h>a)-(?:(?<g>b))\k<h>")
print("SC the ruling's own example `/(?<h>a)-${q}\\k<h>/`: %s" % show(scq, "a-ba", "x a-bb a-ba", "a-ba a-bb a-ba"))
print("SC %s" % check("SC reading 15 and the ruled example", trip(sc, "a-b;ba", "x a-b;aa a-b;ba", "a-b;ba a-b;bb a-b;ba") == ("HOLDS", "`a-b;ba`@9", "[`a-b;ba`@0, `a-b;ba`@14]")
      and trip(scq, "a-ba", "x a-bb a-ba", "a-ba a-bb a-ba") == ("HOLDS", "`a-ba`@7", "[`a-ba`@0, `a-ba`@10]")))

# [29.1] P29-5: optional and looped groups separate "last mention" (the rule: R.1.7, a reset is a mention) from "last
# set": `/(?<h>a)?-${q};${$h}\k<h>/`, q := /(?<h>b)?/ (the inserted group spelt `h2`, so `\k<h>` reads the outer)
SCP = pool("ab-;", 6)
def sc_prog(loop, reading):
    o, i_ = ("(?:(?<h>a))*", "(?:(?:(?<h2>b))*)") if loop else ("(?<h>a)?", "(?:(?<h2>b)?)")
    hv = r"(?(<h2>)\k<h2>|(?!))" if (reading == "mention" and not sab("t31")) else r"(?(<h2>)\k<h2>|\k<h>)"
    return P.Pcre(o + "-" + i_ + ";" + hv + r"\k<h>")
sco = {}
for loop in (False, True):
    m_, s2 = sc_prog(loop, "mention"), sc_prog(loop, "set")
    sco[loop] = (diff3(m_, s2, SCP)[0], trip(m_, "a-;aa", "x a-;aa a-b;ba", "a-;aa a-b;ba"), trip(s2, "a-;aa", "x a-;aa a-b;ba", "a-;aa a-b;ba"))
    print("SC [29.1] P29-5 %s: LAST MENTION (the rule) %s" % ("looped `(?:(?<h>a))*` / `(?:(?<h>b))*`" if loop else "optional `/(?<h>a)?-${q};${$h}\\k<h>/`, q := /(?<h>b)?/",
                                                         show(m_, "a-;aa", "x a-;aa a-b;ba", "a-;aa a-b;ba")))
    print("SC [29.1]   LAST SET (the rival): %s ; the two over %d texts (`ab-;`, length <= 6): %d / %d / %d"
          % ((show(s2, "a-;aa", "x a-;aa a-b;ba", "a-;aa a-b;ba"), len(SCP)) + tuple(sco[loop][0])))
print("SC %s" % check("SC [29.1] P29-5: the optional witness separates last mention from last set",
      sco[False][1] == ("FAILS", "`a-b;ba`@8", "[`a-b;ba`@6]") and sco[False][2][0] == "HOLDS" and sco[False][0][0] > 0 and sco[True][0][0] > 0))

# =====================================================================================================================
print("\n== PART TA: task T-a: isodate three times, two under part labels, the label rules AS DEFINED")
ISO = r"(?<%syear>\d{4})-(?<%smonth>\d\d)-(?<%sday>\d\d)"
def iso(p): return ISO % (p, p, p)
def visible(name, parts, inside):
    """RULE-AS-CODE (export-rule (1)-(4), R.1.0's BINDING and PART LABEL rows, label-flow (3)): `parts` = the program's
    parts in sequence order, each (part label or None, its group prefix); returns the group a reference reads, or an
    ERROR.  INSIDE the binding: a bare name = the LAST MENTION among every part's public labels (a part label only
    disambiguates: its part's labels stay visible bare); a path `x.name` = the last mention of part label x.  OUTSIDE:
    the public labels written in its own literals (none here: every label is isodate's) and its public part labels'
    paths"""
    if "." in name:
        pl, nm = name.split(".")
        hits = [g for lab, g in parts if lab == pl]
        return (hits[-1] + nm) if hits else "ERROR (no part label %s)" % pl
    if not inside:
        return "ERROR (not visible outside: no literal of the binding writes it, no path)"
    hits = [g for lab, g in parts if lab is None or not sab("t16")]
    return (hits[-1] + name) if hits else "ERROR (not visible)"
ORDERS = {"his order: [start_date = isodate] SEQ \":\" SEQ [end_date = isodate] SEQ \" \" SEQ isodate":
          ([("start_date", "s"), ("end_date", "e"), (None, "t")], iso("s") + ":" + iso("e") + " " + iso("t")),
          "the unlabelled use FIRST: isodate SEQ \" \" SEQ [start_date = isodate] SEQ \":\" SEQ [end_date = isodate]":
          ([(None, "t"), ("start_date", "s"), ("end_date", "e")], iso("t") + " " + iso("s") + ":" + iso("e"))}
SUB = {"his order": ("2021-01-02:2022-03-04 2023-05-06", "x 2021-01-02:2022-03-04 2023-05-06 y",
                     "2021-01-02:2022-03-04 2023-05-06 2024-07-08:2025-09-10 2026-11-12"),
       "the unlabelled use FIRST": ("2023-05-06 2021-01-02:2022-03-04", "x 2023-05-06 2021-01-02:2022-03-04 y",
                                    "2023-05-06 2021-01-02:2022-03-04 2026-11-12 2024-07-08:2025-09-10")}
ta = {}
for title, (parts, pat) in ORDERS.items():
    rx = P.Pcre(pat)
    key = "his order" if title.startswith("his") else "the unlabelled use FIRST"
    w, s_, f_ = SUB[key]
    print("TA %s" % title)
    for ref in ("year", "start_date.year", "end_date.year"):
        for inside in (True, False):
            g = visible(ref, parts, inside)
            if g.startswith("ERROR"):
                print("TA   %-16s %s: %s" % (ref, "inside the program" if inside else "outside a binding of it", g))
                ta[(key, ref, inside)] = g
                continue
            mw = W(rx, w)
            ms = S(rx, s_)
            mf = F(rx, f_)
            vals = (mw[2][g] if mw else "FAILS", ms[2][g] if ms else "FAILS", [m[2][g] for m in mf])
            ta[(key, ref, inside)] = vals
            print("TA   %-16s %s reads group %-6s WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s"
                  % (ref, "inside the program" if inside else "outside a binding of it", g, w, vals[0], s_, vals[1], f_, vals[2]))
# a hole instead of an unlabelled SEQ part: R.1.0's PATTERN HOLE row ("only X's public (exported) names flow into the
# outer pattern"): then the unlabelled use's labels are written-in-the-literal for the binding (THE DRAFT'S READING)
print("TA   with the third use INSERTED THROUGH A HOLE (`.. SEQ /${isodate}/`): outside a binding, bare `year` = the hole's year (R.1.0 PATTERN HOLE: its public names flow into the outer pattern; THE DRAFT'S READING); as an unlabelled SEQ part: the ERROR above")
print("TA %s" % check("TA bare `year` = the last mention, paths read their parts, outside only paths",
      ta[("his order", "year", True)][2] == ["2023", "2026"] and ta[("his order", "start_date.year", True)][2] == ["2021", "2024"]
      and ta[("the unlabelled use FIRST", "year", True)][2] == ["2022", "2025"] and ta[("his order", "year", False)].startswith("ERROR")
      and ta[("his order", "end_date.year", False)][0] == "2022"))

# [29.1] P29-13 hole-export: B1 := isodate SEQ "!" and B2 := /${isodate}!/ match the same texts; the caller
# `B & (year: >2000)` is legal for B2 only under THE DRAFT'S READING (a hole re-exports its pattern's public labels)
def exports_year(kind):
    """RULE-AS-CODE: does a caller of the binding see `year`? THE DRAFT'S READING: a hole re-exports (R.1.0 PATTERN HOLE
    + T-a (ii)); an unlabelled SEQ part does not (export-rule (3))"""
    return kind == "hole" and not sab("t34")
isob = P.Pcre("(?:" + iso("") + ")!")
isoc = P.Pcre("(?:" + iso("") + r')!(?C"y")', {"y": lambda c: int(c.get("year")) > 2000})
HW, HS, HF = "2021-01-02!", "x 1999-01-02! 2021-01-02!", "2021-01-02! 1999-01-02! 2025-11-19!"
print("TA [29.1] P29-13 B1 := isodate SEQ \"!\" and B2 := /${isodate}!/ alone (one PCRE spelling): %s" % show(isob, HW, HS, HF))
for kind, nm in (("seq", "B1"), ("hole", "B2")):
    if exports_year(kind):
        print("TA [29.1]   `%s & (year: >2000)`: legal (THE DRAFT'S READING: the hole re-exports `year`): %s" % (nm, show(isoc, HW, HS, HF)))
    else:
        print("TA [29.1]   `%s & (year: >2000)`: COMPILE ERROR (a free name: `year` is not visible to the caller)" % nm)
print("TA [29.1]   candidate (b) of hole-export (only a part label re-exports): `B2 & (year: >2000)` the same COMPILE ERROR as B1")
print("TA %s" % check("TA [29.1] P29-13: the draft's reading gives the caller `year` through a hole, not through an unlabelled SEQ part",
      exports_year("hole") and not exports_year("seq") and fS(isoc, HS) == "`2021-01-02!`@14" and fS(isob, HS) == "`1999-01-02!`@2"))

# =====================================================================================================================
print("\n== PART TB: task T-b: private labels doing real work under the binding scope (export-rule (1))")
def exported(binding_labels):
    """RULE-AS-CODE: what a binding shows outside: its public labels (no `_` prefix)"""
    return [l for l in binding_labels if sab("t17") or not l.startswith("_")]
tb = {}
# (1) date with ONE separator, private: `date := /\d{4}(?<_s>[-\/])\d\d${$_s}\d\d/` used twice in one program
d1p = r"\d{4}(?<%s>[-/])\d\d\k<%s>\d\d"
prog1 = P.Pcre("(?:" + d1p % ("as", "as") + r")\.\.(?:" + d1p % ("bs", "bs") + ")")
print("TB (1) `date := /\\d{4}(?<_s>[-\\/])\\d\\d${$_s}\\d\\d/`; `range := [a = date] SEQ \"..\" SEQ [b = date]`: %s"
      % show(prog1, "2025-11-19..2025/12/01", "x 2025-11/19..2025-12-01 2025-11-19..2025/12/01", "2025-11-19..2025/12/01 2025/11-19..2025-12-01 2026/01/01..2026-02-02"))
tb[1] = (fW(prog1, "2025-11-19..2025/12/01"), fW(prog1, "2025-11/19..2025-12-01"), exported(["_s"]))
print("TB     each use's `_s` is its own; what `date` shows outside: %s (so `range` sees no `_s`: nothing to collide, nothing for the caller)" % tb[1][2])
# (2) a private label as the subject of a condition inside the binding
y4 = P.Pcre(r'(?<_v>\d{4})(?C"c")', {"c": lambda c: canon(c.get("_v")) and int(c.get("_v")) >= 2000})
print("TB (2) `year := /(?<_v>\\d{4})/ & (_v: >= 2000)`: %s ; exported: %s" % (show(y4, "2025", "x1999 2001", "1999 2001 2025"), exported(["_v"])))
tb[2] = (fW(y4, "2025"), fW(y4, "1999"), exported(["_v"]))
# (3) matched quotes, a private label read in a value hole, a key and a value each quoted
q3 = r"(?<%s>[\"'])[^\"']*\k<%s>"
prog3 = P.Pcre("(?<k>" + q3 % ("kq", "kq") + ")=(?<v>" + q3 % ("vq", "vq") + ")")
print("TB (3) `qstr := /(?<_q>[\"'])[^\"']*${$_q}/`; `[k = qstr] SEQ \"=\" SEQ [v = qstr]`: %s ; the caller's labels: k, v (and their public paths: none, qstr exports %s)"
      % (show(prog3, "'a'=\"b\"", "x 'a\"=\"b\" 'a'=\"b\"", "'a'=\"b\" \"c\"='d' 'e\"='f'"), exported(["_q"])))
tb[3] = (fW(prog3, "'a'=\"b\""), fW(prog3, "'a\"=\"b\""), exported(["_q"]))
print("TB %s" % check("TB private labels do their work inside and export nothing",
      tb[1][:2] == ("HOLDS", "FAILS") and tb[2][:2] == ("HOLDS", "FAILS") and tb[3][:2] == ("HOLDS", "FAILS")
      and tb[1][2] == tb[2][2] == tb[3][2] == []))

# =====================================================================================================================
print("\n== PART PL: plus-operands RULED (rulings file R1): arithmetic on the decimal numerals only; anything else NOTHING; a warning if known")
def op_(a, op, b):
    """RULE-AS-CODE of the ruling: `a op b` on one pair of strings; a non-numeral operand yields nothing"""
    if sab("t20") and op == "+" and not (canon(a) and canon(b)):
        return a + b
    return arith(a, op, int(b)) if canon(b) else None
W_CLS = [chr(c) for c in range(48, 58)] + [chr(c) for c in range(65, 91)] + ["_"] + [chr(c) for c in range(97, 123)]   # \w (ASCII)
wl = uniq(by_len(op_(m, "+", "1") for m in W_CLS))
dl = uniq(by_len(op_(m, "+", "1") for m in DIG))
dw, _ = diff3(alt_rx(wl), alt_rx(dl), CP)
print("PL reading 18 `/${\\w + 1}/` member by member: %d results %s ; vs `/${\\d + 1}/` %d / %d / %d of %d ; %s"
      % (len(wl), "|".join(wl), dw[0], dw[1], dw[2], len(CP), show(alt_rx(wl), "10", "xa10", "a1 10 b")))
arr = uniq(r for r in (op_(m, "+", "1") for m in ["7", "x", "41"]) if r is not None)
print("PL reading 18 the array `[\"7\", \"x\", \"41\"] + 1` = %s: %s" % (arr, show(alt_rx(arr), "8", "x42 8", "8 x 42")))
consts = {}
for a, op, b in (("a", "+", "b"), ("a", "+", "1"), ("a", "-", "1"), ("a", "*", "2"), ("a", "%", "2"), ("7", "+", "b"), ("7", "+", "1")):
    r = op_(a, op, b)
    consts["%s %s %s" % (a, op, b)] = r
    print("PL reading 18 `/${\"%s\" %s %s}/`: %s ; %s" % (a, op, b if canon(b) else '"%s"' % b, "NOTHING" if r is None else "`%s`" % r,
          show(alt_rx([] if r is None else [r]), "a", "x8 ab", "8 ab a1")))
def warns_arith(members_a, op, b):
    """RULE-AS-CODE [29.1: P29-7, THE MANAGER'S CALL]: ONE trigger: an arithmetic result KNOWN at compile time to be
    nothing, whatever the cause (a non-numeral constant operand, a written `% 0`, a constant negative result); a member
    list (array or class) warns only when EVERY member's result is nothing"""
    if sab("t28"):
        return all(not canon(m) for m in members_a) or not canon(b)
    res = [op_(m, op, b) for m in members_a]
    if sab("t21"):
        return any(r is None for r in res)
    return all(r is None for r in res)
WA = {"\"a\" + \"b\"": warns_arith(["a"], "+", "b"), "\"a\" + 1": warns_arith(["a"], "+", "1"), "\"a\" % 2": warns_arith(["a"], "%", "2"),
      "\\w + 1": warns_arith(W_CLS, "+", "1"), "[a-z] + 1": warns_arith([chr(c) for c in range(97, 123)], "+", "1"), "\\d + 1": warns_arith(DIG, "+", "1")}
for k, v in WA.items():
    print("PL reading 17 the warning on `%s`: %s" % (k, "FIRES" if v else "silent"))
print("PL %s" % check("PL reading 18: `\\w + 1` = `\\d + 1` member by member; constants outside the domain nothing; the array per member",
      dw == [0, 0, 0] and wl == dl and arr == ["8", "42"] and consts["a + b"] is None and consts["a % 2"] is None and consts["7 + 1"] == "8"))
print("PL %s" % check("PL reading 17: the warning only where the whole result is known nothing",
      [WA[k] for k in WA] == [True, True, True, False, True, False]))
# [29.1] P29-7, the manager's reading 1: the ONE trigger on the number-edge programs and a mixed member list
LOW = [chr(c) for c in range(97, 123)]
WA2 = [("\"a\" + \"b\"", ["a"], "+", "b", True), ("\"a\" + 1", ["a"], "+", "1", True), ("[a-z] + 1", LOW, "+", "1", True),
       ("${\\d % 0}", DIG, "%", "0", True), ("\"7\" % 0", ["7"], "%", "0", True), ("\"3\" - 5", ["3"], "-", "5", True),
       ("\\d - 10", DIG, "-", "10", True), ("[\"a\", \"7\"] % 0", ["a", "7"], "%", "0", True),
       ("\\w + 1", W_CLS, "+", "1", False), ("\\d + 1", DIG, "+", "1", False), ("\\d - 5", DIG, "-", "5", False)]
wa2 = {}
for nm, mem, op, b, want in WA2:
    wa2[nm] = warns_arith(mem, op, b)
    vals = uniq(by_len(op_(m, op, b) for m in mem))
    print("PL [29.1] reading 1 `%s`: the warning %s ; the values %s%s" % (nm, "FIRES" if wa2[nm] else "silent", vals if vals else "NONE (the never-matching rx)",
          "" if wa2[nm] == want else "  <- NOT the expected verdict"))
print("PL %s" % check("PL [29.1] P29-7 / the manager's reading 1: one trigger, a result known nothing whatever the cause; a member list only when every member's is",
      all(wa2[nm] == want for nm, _, _, _, want in WA2)))
# reading 19: run-time reads that are no numeral already yielded nothing under number-domain
def rd(c, v):
    y = c.get("y")
    r = (y + "1") if (sab("t22") and not canon(y)) else op_(y, "+", "1")
    return v is not None and v == r
h19 = hole(r"(?<y>\w+)-", rd)
print("PL reading 19 `/(?<y>\\w+)-${$y + 1}/` (number-domain's answer, unchanged): %s ; WHOLE `a-a1` %s"
      % (show(h19, "7-8", "x a-a1 7-8", "7-8 a-a1 41-42"), fW(h19, "a-a1")))
print("PL %s" % check("PL reading 19: a non-numeral read yields nothing (as number-domain ruled)",
      trip(h19, "7-8", "x a-a1 7-8", "7-8 a-a1 41-42") == ("HOLDS", "`7-8`@7", "[`7-8`@0, `41-42`@9]") and fW(h19, "a-a1") == "FAILS"))

# =====================================================================================================================
print("\n== PART AC: task T-c: any_case(rx) against the body /(?i:${rx})/ under flags-scope (and flags-in-filter REACH, reading 3)")
def variants(t):
    return {"".join(p) for p in itertools.product(*[(ch.lower(), ch.upper()) if ch.isalpha() else (ch,) for ch in t])}
def prim_members(members):
    """the primitive (§2.7: a string equal to some member of S up to letter case), as an alternation: S's members in S's
    order, each with its case variants (equal lengths: their order unobservable); its SEARCHED/FIND-ALL order is
    S's order (THE MODEL's reading: §2.7 defines a SET)"""
    out = []
    for m in members:
        out += sorted(variants(m))
    return alt_rx(out)
APOOL = pool("hHoO1", 4)
QPOOL = pool('hHoO"', 4)
ac = {}
# plain arguments (finite): the body is `(?i:(?:rx))`
for Srx in ("ho", "h[o1]{1,2}", "ho|1h"):
    bd = P.Pcre(r"(?i:(?:%s))" % Srx)
    d, f = diff3(bd, prim_members(enum(Srx)), APOOL)
    ac[Srx] = d
    print("AC plain `%s`: body vs primitive over %d texts (`hHoO1`, length <= 4): %d / %d / %d" % (Srx, len(APOOL), d[0], d[1], d[2]))
# an argument writing its own `(?-i)`: its own flag wins
wr = P.Pcre(r"(?i:(?:(?-i)ho))" if not sab("t18") else r"(?i:(?:ho))")
dwr, _ = diff3(wr, prim_members(["ho"]), APOOL)
print("AC `any_case(/(?-i)ho/)`: body %s ; vs primitive %d / %d / %d" % ((show(wr, "HO", "x HO ho", "ho HO Ho"),) + tuple(dwr)))
# a filter-role argument: `/[ho1]{1,3}/ & /h\w*/` (an `&` inside the hole: REACH) and `quoted("ho")`
X, Y = r"[ho1]{1,3}", r"h\w*"
mem = [m for m in enum(X) if re.fullmatch(Y, m)]
amp_body = amp_hole("", "i", X, Y, reach=True)
amp_own = amp_hole("", "i", X, Y, reach=False)
da, _ = diff3(amp_body, prim_members(mem), APOOL); do_, _ = diff3(amp_own, prim_members(mem), APOOL)
print("AC `any_case(/[ho1]{1,3}/ & /h\\w*/)`: body under REACH vs primitive %d / %d / %d ; with the operands' OWN flags %d / %d / %d" % (tuple(da) + tuple(do_)))
print("AC   REACH: %s" % show(amp_body, "HO1", "x HO1 ho", "ho1 HO 1h"))
qb = P.Pcre(r'(?i:"(?:(?<s>ho)(?C"y"))")', {"y": lambda c: W(P.Pcre(r'(?i)[^"]*'), c.get("s") or "") is not None})
dq, _ = diff3(qb, prim_members(['"ho"']), QPOOL)
print("AC `any_case(quoted(\"ho\"))` under REACH: %s ; vs primitive over %d texts (`hHoO\"`, length <= 4) %d / %d / %d"
      % ((show(qb, '"HO"', 'x "HO" "ho"', '"ho" "HO" "Ho"'), len(QPOOL)) + tuple(dq)))
# [29.1] P29-4: a NEGATED filter operand: `any_case(/[abAB]{2}/ & !/ab/)`; the primitive (§2.7's DEFINITION: a string
# equal to some member of S up to letter case), the REACH body, the operands' OWN flags, and §2.7's LEAN (the
# case-folded reading, lower case) -- each a finite set of length-2 strings (an alternation is exact in every mode)
AB16 = ["".join(p) for p in itertools.product("abAB", repeat=2)]
S15 = [t for t in AB16 if re.fullmatch("[abAB]{2}", t) and not re.fullmatch("ab", t)]
prim15 = sorted({v for m in S15 for v in variants(m)})
reach15 = [t for t in AB16 if re.fullmatch("(?i)[abAB]{2}", t) and not re.fullmatch("ab" if sab("t33") else "(?i)ab", t)]
own15 = [t for t in AB16 if re.fullmatch("[abAB]{2}", t) and not re.fullmatch("ab", t)]
fold15 = [t for t in AB16 if t.lower() in S15]
NPOOL = pool("aAbB ", 4)
neg = {k: alt_rx(v) for k, v in (("prim", prim15), ("reach", reach15), ("own", own15), ("fold", fold15))}
dneg = {k: diff3(neg[k], neg["prim"], NPOOL)[0] for k in ("reach", "own", "fold")}
print("AC [29.1] P29-4 `any_case(/[abAB]{2}/ & !/ab/)`: sizes primitive %d, REACH body %d, own flags %d, the LEAN (folded) %d"
      % (len(prim15), len(reach15), len(own15), len(fold15)))
for k in ("prim", "reach", "own", "fold"):
    print("AC [29.1]   %-6s %s" % (k, show(neg[k], "aB", "x aB ab", "ab aB AB")))
print("AC [29.1]   vs the primitive over %d texts (`aAbB `, length <= 4): REACH %d / %d / %d ; own flags %d / %d / %d ; the LEAN %d / %d / %d"
      % ((len(NPOOL),) + tuple(dneg["reach"]) + tuple(dneg["own"]) + tuple(dneg["fold"])))
print("AC %s" % check("AC [29.1] P29-4: a negated filter operand parts the body from the primitive; the LEAN gives the body's answer",
      dneg["reach"][0] > 0 and dneg["own"][0] > 0 and dneg["fold"] == dneg["reach"] and fW(neg["prim"], "aB") == "HOLDS" and fW(neg["reach"], "aB") == "FAILS"))

print("AC %s" % check("AC T-c: equal for plain and filter-role arguments under REACH in every mode; not for a written `(?-i)`",
      all(v == [0, 0, 0] for v in ac.values()) and da == [0, 0, 0] and dq == [0, 0, 0] and dwr[0] > 0 and do_[0] > 0))

print("\n== CHECKS: %d of %d OK" % (sum(ok for _, ok in CHECKS), len(CHECKS)))
for n, ok in CHECKS:
    if not ok:
        print("FAILED CHECK: %s" % n)
