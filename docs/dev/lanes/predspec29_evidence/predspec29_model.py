#!/usr/bin/env python3
# Lane predspec29 (2026-11-19): the evidence of docs/design/predicates_draft.md REVISION 29 (the owner's six rulings of
# 2026-11-19 folded: padded-order, flags-scope, class-order, dollar-diagnostic, number-edges, same-name-count; the
# manager's readings 1-16 of those record entries tested; tasks T-a, T-b, T-c).  DESIGN EVIDENCE ONLY; rules nothing.
# Standalone: the helpers are COPIED from ../predspec281_evidence/predspec281_model.py (not imported; that directory
# stays as committed).
#
# PARTS (the reading or task each feeds; the draft passage):
#   PO  padded-order RULED any-length-first: readings 1 (length-ordered arguments), 2 (the unbounded lazy `\d+?`, the
#       ruling's CONDITION), the mixed-order argument and the prefix pair (§2.7, R.1.16).
#   FF  flags-scope RULED (`i m s` inherited; `U x xx n` not; a written flag wins): readings 3, 4 (an `&`, a condition's
#       set, a filter-role argument inside a hole), 5 (transitive), 6 (a binding alone), 7 (not-inherited at any depth),
#       12 (`J`), 13 (numbered references); every PCRE inline flag, `#` under `x`, an `&` inside the place (R.1.14,
#       R.1.15).
#   CO  class-order RULED longest: readings 8 (no tie rule), 9 (nesting), 10 (two classes; a class under a quantifier),
#       11 (equal strings one result); the array index (§5.5).
#   NE  number-edges RULED nothing; reading 14 (the "can never match" wording).
#   DD  dollar-diagnostic RULED (a warning keyed on the FORM `$x & S`): reading 16.
#   SC  same-name-count RULED scoped; reading 15 (`$h` the last mention beside `\k<h>` the outer group).
#   TA  task T-a: his isodate example under the label rules AS DEFINED (export-rule (2)-(4)).
#   TB  task T-b: private labels doing real work.
#   AC  task T-c: `any_case` against `/(?i:${rx})/` under the flags rulings, filtered arguments included.
#
# CONTROLS: libpcre2-8 through ../rxmodel_evidence/pcre2h.py (run, never read: D181); python `re`; direct python
# semantic functions.  RULE-AS-CODE is named as such where it is used (the hole spellings, the visibility classifier,
# the class-order sorts, the warning's trigger).
#
# Run (W = the worktree; from $PCREC_TMPDIR/scratch/predspec29; one process, seconds):
#   timeout 900 python3 -I -B W/docs/dev/lanes/predspec29_evidence/predspec29_model.py > fwd.out
#   PREDSPEC29_SABOTAGE=t1,.. (or =1 for all): deliberately wrong rules; each must fail its check (ONE per check):
#     t1  PO: the body EXACT-WIDTH FIRST (the dropped body);
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
#     t19 FF: the inserted literal's `\k<h>` spelt as PCRE's text paste under `(?J)` (rev 28.1's reading).
import os, sys, re, itertools, random
import re._parser as SRE
import re._constants as SC

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rxmodel_evidence"))
import pcre2h as P                                           # noqa: E402

_sv = os.environ.get("PREDSPEC29_SABOTAGE", "")
SABS = set("t%d" % i for i in range(1, 20)) if _sv == "1" else set(x for x in _sv.split(",") if x)
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


print("predspec29 evidence; libpcre2-8 %s%s" % (P.version(), " ; SABOTAGE %s" % ",".join(sorted(SABS, key=lambda x: int(x[1:]))) if SABS else ""))
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
def body(rx, n, lazy_reduced=False):
    """the RULED macro body, RUN as written: each `&` in the hole a capture plus a callout judging the stretch WHOLE by
    the other operand (libpcre2 itself judges `(?s:.){n,}` / `(?s:.){n}`); the branches in the ruled order"""
    ge, eq = P.Pcre(r"(?s:.){%d,}" % n), P.Pcre(r"(?s:.){%d}" % n)
    A = r'(?<a>%s)(?C"A")' % (rx if not lazy_reduced else re.sub(r"\+\?$", "+", rx))
    B = r'(?<b>0*(?:%s))(?C"B")' % rx
    br = [B, A] if sab("t1") else [A, B]
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
print("\n== PART DD: dollar-diagnostic RULED (\"the form $x & .. should just get a warning\"); reading 16")
def warns(prog):
    """RULE-AS-CODE: the warning is keyed on the FORM `$x & S` (a read filtered by a set), wherever it is written"""
    if sab("t14"):
        return prog in ("/(?<x>\\d+)-/ & ($x & <5)",)        # keyed on emptiness instead: only the never-holding one
    return re.search(r"\$\w+\s*&", prog) is not None
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
print("AC %s" % check("AC T-c: equal for plain and filter-role arguments under REACH in every mode; not for a written `(?-i)`",
      all(v == [0, 0, 0] for v in ac.values()) and da == [0, 0, 0] and dq == [0, 0, 0] and dwr[0] > 0 and do_[0] > 0))

print("\n== CHECKS: %d of %d OK" % (sum(ok for _, ok in CHECKS), len(CHECKS)))
for n, ok in CHECKS:
    if not ok:
        print("FAILED CHECK: %s" % n)
