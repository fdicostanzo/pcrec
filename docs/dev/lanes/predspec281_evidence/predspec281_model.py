#!/usr/bin/env python3
# Lane predspec281 (2026-11-18): the evidence of docs/design/predicates_draft.md REVISION 28.1 (review r52's fixes, as
# the predicate manager ruled them).  DESIGN EVIDENCE ONLY; rules nothing.  Standalone: the helpers are COPIED from
# predspec28_model.py (not imported; predspec28_evidence/ stays as committed).
#
# PARTS (review r52 item; the draft passage each one feeds):
#   PR  a PRIORITY-ORDER enumerator (re._parser's tree walked in PCRE priority order; class members in codepoint
#       order, §5.5's LEAN), checked against libpcre2 itself on separating witnesses (`(?:a|ab){1,2}`); rev 28's
#       "more copies first" order shown to part; the array product through it; the refusals (§5.5's sentences) (D).
#   CO  class-order: `\d + 1` and `[90] + 1` under codepoint order (the LEAN) and the other orders (D).
#   PO  padded-order: `padded(rx, n)`'s ORDER: the two-case body against the per-member fill in the argument's own
#       order (T5), the prefix pair `/${padded(/\d{2,3}/, 2)}/`; an infinite argument (greedy and lazy) (A).
#   FF  flags-in-filter and flags-scope: an `&` inside a hole; `x` and `#`; `n`, `U`, `xx`, `J`; branch carry; the
#       caseful hole; `any_case` with a written flag (E).
#   NW  numeral-width at full scope (`- 1`, `- 10`, `* 0`, `% 7`, `+ 1`, `* 3`); two reads; an intermediate result;
#       WIDTH KEPT as the composition `padded(r, strlen($y))`; number-edges (`% 0`, a negative result) (F).
#   SN  same-name-twice at the LANGUAGE level (where the error fires); `\2` without `(?J)`; the corrected §R.7 witness;
#       same-name-count's hole case under the record's "inserted patterns' groups stay scoped" (G).
#   DD  dollar-diagnostic: a read standing for ITS GROUP'S rx in the emptiness diagnostic (I).
#   RC  read COMPOUNDS lifted per member (`($y | "9") + 1`, `($y & <5) + 1`, `$y . "E"` + 1) (K, FIXIND-7).
#   TT  T8/T9 as ONE class per operand by an ORDERED clause list (B); its expected table written by hand.
#   UN  the never-matching rx `(?!)` as a PCRE spelling of the unset read; a value hole in a lookbehind (J).
#   PW  padded's `0*` arm (FIXIND-14): a witness that separates `0*` from `0?`.
#
# CONTROLS: libpcre2-8 through ../rxmodel_evidence/pcre2h.py (run, never read: D181); python `re`; direct python
# semantic functions.  Rule-as-code is named as such where it is used.
#
# Run (W = the worktree; from $PCREC_TMPDIR/scratch/predspec281; one process, seconds):
#   timeout 900 python3 -I -B W/docs/dev/lanes/predspec281_evidence/predspec281_model.py > fwd.out
#   PREDSPEC281_SABOTAGE=t1,.. : deliberately wrong rules; each must fail its check (ONE sabotage per check):
#     t1  PR: the enumerator in rev 28's order (more copies first across choices);
#     t2  PR: the array product with the SECOND operand slowest;
#     t3  PR: an edge assertion accepted by enumerate (no refusal);
#     t4  CO: class members in DESCENDING codepoint order;
#     t5  PO: the per-member fill built in LENGTH order (shortest first) instead of the argument's order;
#     t6  PO: the infinite argument's members taken greedy when it is written lazy;
#     t7  FF: under flags-in-filter (b) the `&` operand checked caseful (the hole's flags not reaching it);
#     t8  FF: `x` at a hole spelt as text with the literal's comment not ended at the literal's end;
#     t9  FF: `(?J)` at a hole treated as scoped for the TEXT reading too;
#     t10 FF: the caseful hole spelt caseless (the "always caseless" reading);
#     t11 FF: `any_case`'s body dropping the argument's written `(?-i)`;
#     t12 NW: WIDTH KEPT never pads (equal to CANONICAL);
#     t13 NW: WIDTH KEPT on intermediate results modelled as canonical;
#     t14 NW: `padded`'s width EXACT in the composition (a value longer than the width yields nothing);
#     t15 NW: a negative result read as a signed numeral under THE DRAFT'S READING;
#     t16 SN: the error at the LITERAL (two groups of one name refused without a backreference);
#     t17 DD: the read treated as match-dependent (no diagnostic);
#     t18 RC: a compound's members tried in REVERSE order;
#     t19 TT: the clause order reversed (UNDER CONSTRUCTION before the assertion error);
#     t20 UN: the never-matching rx spelled `(?:)` in the PCRE spelling of the unset read;
#     t21 PW: padded's arm `0?` instead of `0*`.
import os, sys, re, itertools
import re._parser as SRE
import re._constants as SC

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rxmodel_evidence"))
import pcre2h as P                                           # noqa: E402

_sv = os.environ.get("PREDSPEC281_SABOTAGE", "")
SABS = set("t%d" % i for i in range(1, 22)) if _sv == "1" else set(x for x in _sv.split(",") if x)
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


def fW(rx, s): return "FAILS" if W(rx, s) is None else "HOLDS"
def fS(rx, s):
    r = S(rx, s)
    return "FAILS" if r is None else "`%s`@%d" % (s[r[0]:r[1]], r[0])
def fF(rx, s): return "[" + ", ".join("`%s`@%d" % (s[a:b], a) for a, b, _ in F(rx, s)) + "]"


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
    return "WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % (w.replace("\n", "\\n"), fW(rx, w), s_, fS(rx, s_), f_, fF(rx, f_))


def trip(rx, w, s_, f_):
    return (fW(rx, w), fS(rx, s_), fF(rx, f_))


def compiles(p):
    try:
        return P.Pcre(p), None
    except ValueError as e:
        return None, str(e).split(": ", 1)[-1]


def canon(v):
    return v is not None and re.fullmatch(r"0|[1-9]\d*", v) is not None


def arith(y, op, k):
    """`$y op k` on one string under THE NUMBER DOMAIN (RULED canonical); None = yields nothing (outside the domain:
    a non-canonical operand, `% 0`, a negative result: the last two THE DRAFT'S READING, number-edges)"""
    if not canon(y):
        return None
    a = int(y)
    if op == "%" and k == 0:
        return None
    r = {"+": a + k, "-": a - k, "*": a * k, "%": a % k if k else None}[op]
    if r < 0:
        return ("-" + str(-r)) if sab("t15") else None
    return str(r)


VQ = r'(?<v>[\s\S]*?)(?C"eq")'      # a value hole: a lazy capture accepted only when the predicate holds on it


def hole(pre, pred, post=''):
    """pred(c, v) -> True when the hole's set holds v (the label read where the hole stands)"""
    return P.Pcre(pre + VQ + post, {"eq": lambda c: pred(c, c.get("v")) is True})


def hole_seq(pre, fns, post=''):
    """a hole whose expression yields its members IN ORDER: one branch per member, fns[i](c) -> the member or None"""
    br, cb = [], {}
    for i, f in enumerate(fns):
        br.append(r'(?<v%d>[\s\S]*?)(?C"m%d")' % (i, i))
        cb["m%d" % i] = (lambda c, i=i, f=f: f(c) is not None and c.get("v%d" % i) == f(c))
    return P.Pcre(pre + "(?:" + "|".join(br) + ")" + post, cb)


def zfill_min(v, n):
    """padded-width RULED minimum: zeros reach out to n characters; a value n or longer is matched unpadded"""
    return "0" * max(0, n - len(v)) + v


def alt_rx(strs, pre="", post=""):
    seen, out = set(), []
    for s in strs:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return P.Pcre(pre + "(?:" + "|".join(re.escape(s) for s in out) + ")" + post)


print("predspec281 evidence; libpcre2-8 %s%s" % (P.version(), " ; SABOTAGE %s" % ",".join(sorted(SABS, key=lambda x: int(x[1:]))) if SABS else ""))
for line, ok in P.selfcheck():
    print("selfcheck: %s ; %s" % (line, check("selfcheck " + line[:30], ok)))

# =====================================================================================================================
print("\n== PART PR: enumerate in PCRE PRIORITY order (§5.5), checked against libpcre2 itself")
BUDGET = 20000      # §5.5: "A BUDGET bounds it" names no number; this number is the MODEL's, not the draft's


class Refused(Exception):
    pass


DIG = "0123456789"


def cls_members(items):
    out = set()
    for op, av in items:
        if op == SC.LITERAL:
            out.add(chr(av))
        elif op == SC.RANGE:
            out |= {chr(c) for c in range(av[0], av[1] + 1)}
        elif op == SC.CATEGORY and av == SC.CATEGORY_DIGIT:
            out |= set(DIG)
        else:
            raise Refused("class item not modelled: %s" % op)
    return sorted(out, reverse=sab("t4"))


def seq_strs(seq):
    """the strings of a node sequence, in PCRE priority order (first element slowest; greedy = one more copy first)"""
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
        if sab("t1"):                                    # rev 28's order: more copies first across choices
            out = []
            rng = range(hi, lo - 1, -1) if op == SC.MAX_REPEAT else range(lo, hi + 1)
            for m in rng:
                out += seq_strs(list(body) * m + rest)
            return out
        if lo > 0:
            return seq_strs(list(body) + [(op, (lo - 1, hi - 1, body))] + rest)
        if hi == 0:
            return seq_strs(rest)
        more = seq_strs(list(body) + [(op, (0, hi - 1, body))] + rest)
        none = seq_strs(rest)
        out = more + none if op == SC.MAX_REPEAT else none + more
        if len(out) > BUDGET:
            raise Refused("over budget")
        return out
    if op in (SC.ASSERT, SC.ASSERT_NOT, SC.AT):
        raise Refused("NOT STATED: an assertion inside the rx (§5.5 names only edge assertions); the model refuses it")
    if op == SC.GROUPREF:
        raise Refused("NOT STATED: a backreference (non-regular); the model refuses it")
    raise Refused("not modelled: %s" % op)


def enum(rx):
    """§5.5 enumerate: a FINITE rx's strings in PCRE PRIORITY order; an edge assertion is the edge-assertion error
    (§5.5's sentence); an infinite or over-budget rx refused (§5.5's sentence; the budget's number is the model's)"""
    tree = list(SRE.parse(rx, re.ASCII))
    if tree and not sab("t3"):
        for (op, av) in (tree[0], tree[-1]):
            if op in (SC.ASSERT, SC.ASSERT_NOT, SC.AT):
                raise Refused("an edge assertion: the edge-assertion error (§5.5)")
    elif tree and sab("t3"):
        tree = [n for n in tree if n[0] not in (SC.ASSERT, SC.ASSERT_NOT, SC.AT)]
    out = seq_strs(tree)
    if len(out) > BUDGET:
        raise Refused("over budget")
    return out


def old_enum_copies_first(rx):
    """rev 28's enumerator order for one counted repeat of an alternation (more copies first), for the record"""
    m = re.fullmatch(r"\(\?:(.*)\)\{(\d),(\d)\}", rx)
    alts, lo, hi = m.group(1).split("|"), int(m.group(2)), int(m.group(3))
    out = []
    for k in range(hi, lo - 1, -1):
        out += ["".join(t) for t in itertools.product(alts, repeat=k)]
    return out


WIT = [(r"(?:a|ab){1,2}", "ab", 5), (r"\d{1,2}", "0123", 4), (r"(?:ab|a)(?:c|bc)?", "abc", 4), (r"a{0,2}?b", "ab", 4),
       (r"(?:x|xy)(?:yz|y)?", "xyz", 4), (r"[ba]x|b", "abx", 4)]
pr_ok = True
for rx, al, n in WIT:
    st = enum(rx)
    sal = "".join(sorted(set("".join(st)))) if st else al          # every character a member uses
    setok = sorted(set(st)) == sorted(s for s in pool(sal, max(map(len, st)) + 1) if re.fullmatch(rx, s, re.ASCII))
    d, first = diff3(alt_rx(st), P.Pcre(rx), pool(al, n))
    pr_ok &= setok and d == [0, 0, 0]
    print("PR `%s`: %d strings, first %s ; SET = python `re`'s by brute force over the members' characters, one longer than the longest: %s ; the alternation in enumerate's order vs libpcre2's own `%s` over %d texts (`%s`, length <= %d): %d / %d / %d"
          % (rx, len(st), " | ".join(st[:6]), setok, rx, len(pool(al, n)), al, n, d[0], d[1], d[2]))
old = old_enum_copies_first(r"(?:a|ab){1,2}")
dold, fold = diff3(alt_rx(old), P.Pcre(r"(?:a|ab){1,2}"), pool("ab", 5))
po_rx = alt_rx(enum(r"(?:a|ab){1,2}"))
print("PR rev 28's model order (more copies first) for `(?:a|ab){1,2}`: %s ; vs libpcre2 %d / %d / %d of %d (first %s)"
      % (" | ".join(old), dold[0], dold[1], dold[2], len(pool("ab", 5)), fold))
print("PR `(?:a|ab){1,2}` in PRIORITY order: %s ; rev 28's order: %s" % (show(po_rx, "aba", "aba", "aba ab"), show(alt_rx(old), "aba", "aba", "aba ab")))
print("PR %s" % check("PR enumerator = libpcre2's priority order; rev 28's order parts", pr_ok and dold[1] > 0))
# the array product through the enumerator (array-lift: "first operand slowest")
A_, B_ = enum(r"1|2"), enum(r"10|20")
prod = [arith(a, "+", int(b)) for a in A_ for b in B_] if not sab("t2") else [arith(a, "+", int(b)) for b in B_ for a in A_]
cat = enum(r"(?:1|2)(?:10|20)")
pairs = [a + b for a in A_ for b in B_] if not sab("t2") else [a + b for b in B_ for a in A_]
dcat, _ = diff3(alt_rx(pairs), P.Pcre(r"(?:1|2)(?:10|20)"), pool("012", 5))
print("PR `[1, 2] + [10, 20]` through the enumerator: %s ; the pair order %s = enumerate(`(?:1|2)(?:10|20)`) %s ; the pair alternation vs libpcre2's concatenation %d / %d / %d of %d (`012`, length <= 5)"
      % ("|".join(prod), "|".join(pairs), "|".join(cat), dcat[0], dcat[1], dcat[2], len(pool("012", 5))))
print("PR %s" % check("PR product first slowest = PCRE's concatenation order", prod == ["11", "21", "12", "22"] and pairs == cat and dcat == [0, 0, 0]))
ref = {}
for rx in (r"(?<=x)ab", r"ab\b", r"a(?=b)b", r"\d+", r"(\d)\1", r"[0-9]{5}"):
    try:
        ref[rx] = "%d strings" % len(enum(rx))
    except Refused as e:
        ref[rx] = "REFUSED (%s)" % e
    print("PR enumerate(`%s`): %s" % (rx, ref[rx]))
print("PR %s" % check("PR refusals as §5.5 states them (edge assertion; infinite; budget) and the model's own (NOT STATED)",
      ref[r"(?<=x)ab"].startswith("REFUSED (an edge") and ref[r"ab\b"].startswith("REFUSED (an edge")
      and "NOT STATED" in ref[r"a(?=b)b"] and ref[r"\d+"] == "REFUSED (infinite)" and "NOT STATED" in ref[r"(\d)\1"]
      and ref[r"[0-9]{5}"] == "REFUSED (over budget)"))

# =====================================================================================================================
print("\n== PART CO: class-order (§5.5's LEAN: class members in codepoint order) decides lifted answers")
def lifted(rx, f):
    return [r for r in (f(s) for s in enum(rx)) if r is not None]
d1 = lifted(r"\d", lambda s: arith(s, "+", 1))
d1r = list(reversed([arith(s, "+", 1) for s in DIG]))
w90 = lifted(r"[90]", lambda s: arith(s, "+", 1))
w90w = [arith(s, "+", 1) for s in "90"]                               # the members in WRITTEN order
co = {}
for nm, strs in (("`\\d + 1` CODEPOINT (the LEAN)", d1), ("`\\d + 1` DESCENDING", d1r),
                 ("`[90] + 1` CODEPOINT (the LEAN)", w90), ("`[90] + 1` WRITTEN order", w90w)):
    rx = alt_rx(strs)
    co[nm] = trip(rx, "10", "x10", "10 3 11")
    print("CO %s = %s: %s" % (nm, "|".join(strs), show(rx, "10", "x10", "10 3 11")))
dco, _ = diff3(alt_rx(d1), alt_rx(d1r), pool("0123x", 4))
print("CO `\\d + 1` codepoint vs descending over %d texts (`0123x`, length <= 4): %d / %d / %d" % (len(pool("0123x", 4)), dco[0], dco[1], dco[2]))
print("CO %s" % check("CO codepoint order's answers", co["`\\d + 1` CODEPOINT (the LEAN)"] == ("HOLDS", "`1`@1", "[`1`@0, `3`@3, `1`@5, `1`@6]")
      and co["`\\d + 1` DESCENDING"] == ("HOLDS", "`10`@1", "[`10`@0, `3`@3, `1`@5, `1`@6]")
      and co["`[90] + 1` CODEPOINT (the LEAN)"][1] == "`1`@1" and co["`[90] + 1` WRITTEN order"][1] == "`10`@1"))

# =====================================================================================================================
print("\n== PART PO: padded-order: `padded(rx, n)`'s ORDER (padded-width RULED minimum; the order NOT ruled)")
def per_member(rx, n):
    ms = enum(rx)
    fills = [zfill_min(m, n) for m in ms]
    if sab("t5"):
        fills = sorted(fills, key=len)
    return fills
def setdef(rx, n, al, k):
    ms = set(enum(rx))
    return sorted({zfill_min(m, n) for m in ms})
# the two-case body `(/0*${rx}/ & /(?s:.){${n}}/) | (rx & /(?s:.){${n},}/)`, its `&`s reduced BY HAND for these
# arguments (HAND-WORKED; the reductions' SETS are checked against the definition below)
TWO = {(r"\d{2,3}", 2): r"(?:\d{2}|\d{2,3})", (r"\d{1,3}", 2): r"(?:\d{2}|\d{2,3})"}
po = {}
for (rx, n), body in TWO.items():
    pm = alt_rx(per_member(rx, n))
    tw = P.Pcre(body)
    bset = sorted(s for s in pool(DIG, 3) if W(tw, s) is not None)
    setok = bset == setdef(rx, n, DIG, 3)
    d, first = diff3(tw, pm, pool("0123x ", 5))
    po[(rx, n)] = (trip(tw, "123", "x123", "123 12345"), trip(pm, "123", "x123", "123 12345"), d, setok)
    print("PO `/${padded(/%s/, %d)}/` TWO-CASE body (as `%s`): %s" % (rx, n, body, show(tw, "123", "x123", "123 12345")))
    print("PO the same, PER-MEMBER fill in the argument's order (T5): %s" % show(pm, "123", "x123", "123 12345"))
    print("PO   SETS equal (the body's WHOLE set over digits up to 3 = the fills of enumerate's members): %s ; the two ORDERS over %d texts (`0123x `, length <= 5): %d / %d / %d (first %s)"
          % (setok, len(pool("0123x ", 5)), d[0], d[1], d[2], first))
pmid = alt_rx(per_member(r"\d{2,3}", 2)); dself, _ = diff3(pmid, P.Pcre(r"\d{2,3}"), pool("0123x ", 5))
print("PO per-member `padded(/\\d{2,3}/, 2)` vs the argument `\\d{2,3}` itself (no member is padded at n = 2): %d / %d / %d" % tuple(dself))
# an INFINITE argument: members longer than the subject cannot match, so `[01]+` on texts up to 5 is `[01]{1,5}`
# (HAND-WORKED truncation); two candidate bodies over ruled pieces
L5 = 5
inf = {}
for nm, arg, tr in (("greedy `[01]+`", r"[01]+", r"[01]{1,5}"), ("lazy `[01]+?`", r"[01]+?", r"[01]{1,5}?")):
    trr = tr if not (sab("t6") and tr.endswith("?")) else tr[:-1]
    ref_ = alt_rx(per_member(trr, 2))
    two = P.Pcre(r"(?:[01]{2}|[01]{2,})")          # two-case: the exactly-n case first
    rev = P.Pcre(r"(?:[01]{2,}|[01]{2})")          # reversed: the unpadded case first
    a, _ = diff3(two, ref_, pool("01x", L5)); b, _ = diff3(rev, ref_, pool("01x", L5))
    inf[nm] = (a, b)
    print("PO infinite argument %s at n = 2, against its per-member fill (argument order) over %d texts (`01x`, length <= 5): TWO-CASE body %d / %d / %d ; REVERSED body (unpadded case first) %d / %d / %d ; per-member %s"
          % (nm, len(pool("01x", L5)), a[0], a[1], a[2], b[0], b[1], b[2], show(ref_, "011", "x011", "011 0110")))
print("PO %s" % check("PO two-case body = definition in WHOLE, parts in SEARCHED/FIND-ALL; per-member = argument order",
      all(v[3] for v in po.values()) and po[(r"\d{2,3}", 2)][0] == ("HOLDS", "`12`@1", "[`12`@0, `12`@4, `34`@6]")
      and po[(r"\d{2,3}", 2)][1] == ("HOLDS", "`123`@1", "[`123`@0, `123`@4, `45`@7]") and dself == [0, 0, 0]
      and po[(r"\d{2,3}", 2)][2][0] == 0 and po[(r"\d{2,3}", 2)][2][1] > 0))
print("PO %s" % check("PO no one body keeps the argument's order for an infinite argument",
      inf["greedy `[01]+`"][1] == [0, 0, 0] and inf["greedy `[01]+`"][0][1] > 0
      and inf["lazy `[01]+?`"][0] == [0, 0, 0] and inf["lazy `[01]+?`"][1][1] > 0))

# =====================================================================================================================
print("\n== PART FF: flags in a hole: an `&` inside the hole; x and #; n, U, xx, J; branch carry; the caseful hole")
def amp(xrx, yrx, ycase, pre, post=""):
    """X & Y in a hole: the stretch matched by X (in X's order) and accepted whole by Y"""
    fl = 0 if ycase else re.I
    return P.Pcre(pre + "(?:(?<s>%s)(?C\"y\"))" % xrx + post, {"y": lambda c: re.fullmatch(yrx, c.get("s") or "", fl) is not None})
fa = amp(r"(?-i:ab)", r"a.", True, r"(?i)x")                      # (a) the `&` operands keep their own (caseful) flags
fb = amp(r"ab", r"a.", sab("t7"), r"(?i)x")                        # (b) the hole's flags reach the `&` operands
fn_ = P.Pcre(r"(?i)x(?:ab)")                                       # the hole with no filter, `/(?i)x${/ab/}/`
FP = pool("xXaAbB", 4)
dab, _ = diff3(fa, fn_, FP); dbb, _ = diff3(fb, fn_, FP)
print("FF flags-in-filter `/(?i)x${/ab/ & /a./}/` (a) operands own flags: %s" % show(fa, "XAB", "x XAB xab", "xab XAB xAb"))
print("FF flags-in-filter (b) the hole's flags reach the operands: %s" % show(fb, "XAB", "x XAB xab", "xab XAB xAb"))
print("FF against `/(?i)x${/ab/}/` (the filter admits every member) over %d texts (`xXaAbB`, length <= 4): (a) %d / %d / %d ; (b) %d / %d / %d"
      % (len(FP), dab[0], dab[1], dab[2], dbb[0], dbb[1], dbb[2]))
print("FF %s" % check("FF flags-in-filter: (a) parts from the plain hole, (b) equals it", dab[0] > 0 and dbb == [0, 0, 0]))
# x: a space and a `#` in an inserted literal
xs = {"PROPAGATE (text)": r"(?x)a(?:b c)d", "NOT PROPAGATED": r"(?x)a(?-x:b c)d"}
for k, p in xs.items():
    print("FF x `/(?x)a${/b c/}d/` %s: %s" % (k, show(P.Pcre(p), "abcd", "x ab cd abcd", "abcd ab cd")))
hx = {"TEXT PASTE `(?x)a(?:b#c)d`": r"(?x)a(?:b#c)d",
      "x REACHES THE LITERAL, its comment ends at the literal's end `(?x)a(?:b)d`": r"(?x)a(?:b)d" if not sab("t8") else r"(?x)a(?:b#c)d",
      "NOT PROPAGATED `(?x)a(?-x:b#c)d`": r"(?x)a(?-x:b#c)d"}
hxr = {}
for k, p in hx.items():
    rx, err = compiles(p)
    hxr[k] = "REJECTED (%s)" % err if rx is None else trip(rx, "abd", "x ab#cd abd", "abd ab#cd")
    print("FF # `/(?x)a${/b#c/}d/` %s: %s" % (k, hxr[k] if rx is None else show(rx, "abd", "x ab#cd abd", "abd ab#cd")))
print("FF %s" % check("FF x and #: three readings, the text paste a compile error",
      hxr["TEXT PASTE `(?x)a(?:b#c)d`"].startswith("REJECTED (missing closing parenthesis")
      and hxr["x REACHES THE LITERAL, its comment ends at the literal's end `(?x)a(?:b)d`"][0] == "HOLDS"
      and hxr["NOT PROPAGATED `(?x)a(?-x:b#c)d`"][0] == "FAILS"))
other = {}
for nm, prop, notp, w, s_, f_ in (
        ("n `/(?n)x${/(a)\\1/}/`", r"(?n)x(?:(a)\1)", r"(?n)x(?-n:(a)\1)", "xaa", "x xaa", "xaa xa xaa"),
        ("U `/(?U)x${/a+/}/`", r"(?U)x(?:a+)", r"(?U)x(?-U:a+)", "xaaa", "xaaa", "xaa xa"),
        ("xx `/(?xx)${/[a b]/}/`", r"(?xx)(?:[a b])", r"(?xx)(?^:[a b])", " ", "x a", "a b"),
        ("J `/(?J)(?<h>a)-${/(?<h>b)\\k<h>/}/`", r"(?J)(?'h'a)-(?:(?'h'b)\k<h>)", r"(?'h'a)-(?:(?'g'b)\k<g>)", "a-ba", "a-bb a-ba", "a-ba a-bb"),
        ("branch carry `/(?:a(?i)b|${/c/})/`", r"(?:a(?i)b|(?:c))", r"(?:a(?i)b|(?-i:c))", "C", "xC", "c C aB")):
    if sab("t9") and nm.startswith("J"):
        prop = notp
    a, ea = compiles(prop); b, eb = compiles(notp)
    other[nm] = (("REJECTED (%s)" % ea) if a is None else trip(a, w, s_, f_), trip(b, w, s_, f_))
    print("FF %s PROPAGATE / PCRE's own: %s" % (nm, ("REJECTED (%s)" % ea) if a is None else show(a, w, s_, f_)))
    print("FF %s %s: %s" % (nm, "OUTER BINDING NOT REACHED (own namespace)" if nm.startswith("J") else "NOT PROPAGATED / no carry", show(b, w, s_, f_)))
print("FF %s" % check("FF n, U, xx, J, branch carry", other["n `/(?n)x${/(a)\\1/}/`"][0].startswith("REJECTED")
      and other["U `/(?U)x${/a+/}/`"][0][1] == "`xa`@0" and other["U `/(?U)x${/a+/}/`"][1][1] == "`xaaa`@0"
      and other["xx `/(?xx)${/[a b]/}/`"][0][0] == "FAILS" and other["xx `/(?xx)${/[a b]/}/`"][1][0] == "HOLDS"
      and other["J `/(?J)(?<h>a)-${/(?<h>b)\\k<h>/}/`"][0][0] == "HOLDS" and other["J `/(?J)(?<h>a)-${/(?<h>b)\\k<h>/}/`"][1][0] == "FAILS"
      and other["branch carry `/(?:a(?i)b|${/c/})/`"][0][0] == "HOLDS" and other["branch carry `/(?:a(?i)b|${/c/})/`"][1][0] == "FAILS"))
cf = P.Pcre(r"x(?:ab)" if not sab("t10") else r"(?i)x(?:ab)")
print("FF the CASEFUL hole `/x${/ab/}/` (no flag anywhere): %s" % show(cf, "xAB", "xAB xab", "xab xAB XAB"))
print("FF %s" % check("FF caseful hole stays caseful", W(cf, "xAB") is None and W(cf, "xab") is not None))
AQ = pool("hHoO", 3)
body = P.Pcre(r"(?i:(?:(?-i)ho))" if not sab("t11") else r"(?i:(?:ho))")
def prim_ci(t):
    return any(W(P.Pcre(r"(?-i)ho"), u) is not None for u in {"".join(p) for p in itertools.product(*[(ch.lower(), ch.upper()) for ch in t])})
dac = [t for t in AQ if (W(body, t) is not None) != prim_ci(t)]
print("FF `any_case(/(?-i)ho/)`: the body `/(?i:${rx})/` vs the primitive over %d texts (`hHoO`, length <= 3): %d differ %s"
      % (len(AQ), len(dac), dac))
print("FF %s" % check("FF any_case with a written flag differs", len(dac) == 3))

# =====================================================================================================================
print("\n== PART NW: numeral-width at its full scope (number-domain RULED canonical; WIDTH KEPT = zero-padded to the operand's width)")
def width_kept(y, op, k):
    r = arith(y, op, k)
    if r is None:
        return None
    return r if sab("t12") else r.zfill(len(y))
ops = [("-", 1), ("-", 10), ("*", 0), ("%", 7), ("+", 1), ("*", 3)]
nw, narrower = {}, {}
Y = [str(i) for i in range(10000)]
for op, k in ops:
    dif = [y for y in Y if arith(y, op, k) != width_kept(y, op, k)]
    nar = [y for y in Y if arith(y, op, k) is not None and len(arith(y, op, k)) < len(y)]
    nw[(op, k)], narrower[(op, k)] = len(dif), len(nar)
    print("NW `$y %s %d` over the canonical y 0..9999 (10,000 operands): CANONICAL vs WIDTH KEPT differ on %d ; results narrower than the operand %d (first %s)"
          % (op, k, len(dif), len(nar), dif[:3]))
lines = {}
for op, k, w1, w2, s_, f_ in (("-", 1, "10-9", "10-09", "10-09 10-9", "10-9 100-99 100-099"), ("%", 7, "10-3", "10-03", "10-03 10-3", "10-3 100-2 100-002")):
    hc = hole(r'(?<y>\d+)-', lambda c, v, op=op, k=k: v == arith(c.get("y"), op, k))
    hw = hole(r'(?<y>\d+)-', lambda c, v, op=op, k=k: v == width_kept(c.get("y"), op, k))
    lines[(op, "C")] = (fW(hc, w1), fW(hc, w2), fS(hc, s_), fF(hc, f_))
    lines[(op, "W")] = (fW(hw, w1), fW(hw, w2), fS(hw, s_), fF(hw, f_))
    print("NW `/(?<y>\\d+)-${$y %s %d}/` CANONICAL: WHOLE %s %s, %s %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % ((op, k, w1) + lines[(op, "C")][:1] + (w2,) + lines[(op, "C")][1:2] + (s_,) + lines[(op, "C")][2:3] + (f_,) + lines[(op, "C")][3:]))
    print("NW the same, WIDTH KEPT: WHOLE %s %s, %s %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % ((w1,) + lines[(op, "W")][:1] + (w2,) + lines[(op, "W")][1:2] + (s_,) + lines[(op, "W")][2:3] + (f_,) + lines[(op, "W")][3:]))
print("NW %s" % check("NW differ = narrower, every op; the every-mode lines",
      all(nw[x] == narrower[x] for x in nw) and nw[("-", 1)] == 3 and nw[("+", 1)] == 0 and nw[("*", 3)] == 0 and nw[("%", 7)] > 9000
      and lines[("-", "C")] == ("HOLDS", "FAILS", "`10-9`@6", "[`10-9`@0, `100-99`@5]")
      and lines[("-", "W")] == ("FAILS", "HOLDS", "`10-09`@0", "[`100-099`@12]")))
# two reads: whose width?
pairs2 = [(str(a), str(b)) for a in range(0, 300) for b in range(0, 300) if a >= b]
def two(a, b, who):
    r = arith(a, "-", int(b)) if canon(b) else None
    if r is None:
        return None
    return r if who == "C" else r.zfill(len(a) if who == "A" else len(b))
cAB = {k: sum(1 for a, b in pairs2 if two(a, b, k[0]) != two(a, b, k[1])) for k in ("CA", "CB", "AB")}
print("NW two reads `$a - $b` over a >= b in 0..299 (%d pairs): CANONICAL vs a's width %d ; vs b's width %d ; a's vs b's %d"
      % (len(pairs2), cAB["CA"], cAB["CB"], cAB["AB"]))
tw = {}
for who in "CAB":
    h = hole(r'(?<a>\d+)-(?<b>\d+)=', lambda c, v, who=who: v is not None and v == two(c.get("a"), c.get("b"), who))
    tw[who] = (fW(h, "100-1=99"), fW(h, "100-1=099"), fS(h, "100-1=099 100-1=99"), fF(h, "100-1=99 100-1=099 5-5=0"))
    print("NW `/(?<a>\\d+)-(?<b>\\d+)=${$a - $b}/` %s: WHOLE 100-1=99 %s, 100-1=099 %s ; SEARCHED `100-1=099 100-1=99` %s ; FIND-ALL `100-1=99 100-1=099 5-5=0` %s"
          % (({"C": "CANONICAL", "A": "WIDTH KEPT (a's)", "B": "WIDTH KEPT (b's)"}[who],) + tw[who]))
# an intermediate result
def inter(y, mode):
    r1 = arith(y, "-", 1)
    if r1 is None:
        return None
    if mode == "each" and not sab("t13"):
        r1 = r1.zfill(len(y))
    r2 = arith(r1, "+", 1)
    if r2 is None:
        return None
    return r2.zfill(len(y)) if mode in ("each", "end") else r2
cint = {m: sum(1 for y in Y if inter(y, m) != inter(y, "C")) for m in ("each", "end")}
print("NW `${($y - 1) + 1}` over 0..9999: WIDTH KEPT on EVERY result vs CANONICAL %d differ ; WIDTH KEPT on the hole's result only %d" % (cint["each"], cint["end"]))
ti = {}
for m in ("C", "each", "end"):
    h = hole(r'(?<y>\d+)-', lambda c, v, m=m: v is not None and v == inter(c.get("y"), m))
    ti[m] = trip(h, "10-10", "x10-10", "10-10 9-9 100-100")
    print("NW `/(?<y>\\d+)-${($y - 1) + 1}/` %s: %s" % ({"C": "CANONICAL", "each": "WIDTH KEPT on every result", "end": "WIDTH KEPT on the hole's result"}[m], show(h, "10-10", "x10-10", "10-10 9-9 100-100")))
print("NW %s" % check("NW two reads part; intermediate width parts", cAB["AB"] > 0 and tw["A"][1] == "HOLDS" and tw["B"][1] == "FAILS"
      and cint["each"] > 0 and cint["end"] == 0 and ti["each"][0] == "FAILS" and ti["C"][0] == "HOLDS"))
# GENFORM-5: WIDTH KEPT as the composition `padded($y op k, strlen($y))`
def padded_w(v, n):
    if v is None:
        return None
    if sab("t14"):
        return v.zfill(n) if len(v) <= n else None
    return zfill_min(v, n)
gn = {(op, k): sum(1 for y in Y if padded_w(arith(y, op, k), len(y)) != width_kept(y, op, k)) for op, k in ops}
print("NW WIDTH KEPT vs the composition `padded($y op k, strlen($y))` (padded-width RULED minimum): %s ; total %d of %d"
      % (" ; ".join("`%s %d` %d" % (op, k, n) for (op, k), n in gn.items()), sum(gn.values()), len(Y) * len(ops)))
print("NW %s" % check("NW WIDTH KEPT = padded(r, strlen($y))", all(n == 0 for n in gn.values())))
# number-edges: `% 0` and a negative result
ne = {}
for nm, op, k, w1, w2, s_, f_ in (("`% 0`", "%", 0, "5-0", "5-5", "x5-0 5-5", "5-0 7-7 0-0"), ("`- 10`", "-", 10, "15-5", "5--5", "5--5 15-5", "15-5 5--5 10-0")):
    h = hole(r'(?<y>\d+)-', lambda c, v, op=op, k=k: v is not None and v == arith(c.get("y"), op, k))
    ne[nm] = (fW(h, w1), fW(h, w2), fS(h, s_), fF(h, f_))
    print("NE `/(?<y>\\d+)-${$y %s %d}/` THE DRAFT'S READING (outside the domain: nothing): WHOLE %s %s, %s %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s"
          % ((op, k, w1, ne[nm][0], w2, ne[nm][1], s_, ne[nm][2], f_, ne[nm][3])))
hs = hole(r'(?<y>\d+)-', lambda c, v: canon(c.get("y")) and v == str(int(c.get("y")) - 10))
print("NE the same `- 10`, a SIGNED result (the other candidate): %s" % show(hs, "5--5", "5--5 15-5", "15-5 5--5 10-0"))
print("NE `$y % 0` the other candidate: a COMPILE ERROR (the divisor is a compile-time constant): every mode refused (HAND-WORKED; no model needed)")
print("NE %s" % check("NE `% 0` never holds; a negative result yields nothing", ne["`% 0`"] == ("FAILS", "FAILS", "FAILS", "[]")
      and ne["`- 10`"][0] == "HOLDS" and ne["`- 10`"][1] == "FAILS" and ne["`- 10`"][2] == "`15-5`@5" and W(hs, "5--5") is not None))

# =====================================================================================================================
print("\n== PART SN: same-name-twice at the LANGUAGE level (RULED: the literal LEGAL; `\\k<h>` to a name two groups carry a COMPILE ERROR at the backreference unless `(?J)`)")
def lang(lit):
    """the language's compile of one literal (rule-as-code): (None, where, offset) for the error, else (Pcre, None, None)"""
    names = re.findall(r"\(\?(?:<|')([A-Za-z_]\w*)(?:>|')", lit)
    dup = {n for n in names if names.count(n) > 1}
    J = "(?J)" in lit
    if sab("t16") and dup and not J:
        return None, "at the second group (the literal)", lit.index("(?<%s>" % sorted(dup)[0], lit.index("(?<") + 1)
    for m in re.finditer(r"\\k<([A-Za-z_]\w*)>", lit):
        if m.group(1) in dup and not J:
            return None, "at the backreference", m.start()
    pcre = re.sub(r"\(\?<([A-Za-z_]\w*)>", r"(?'\1'", lit)
    if dup and not J:
        pcre = "(?J)" + pcre          # dup names are legal in the language; PCRE needs J to accept them (no `\k` to them here)
    return P.Pcre(pcre), None, None
sn = {}
for lit, w, s_, f_ in ((r"(?<h>a)(?<h>b)", "ab", "xab", "ab ab"), (r"(?<h>\d)(?<h>\d)-\k<h>", "12-1", "x12-1", "12-1"),
                       (r"(?<h>\d)(?<h>\d)-\2", "12-2", "x12-1 34-4", "12-2 34-3 56-6"),
                       (r"(?J)(?<h>\d);(?:(?<h>\d)|x)\k<h>", "3;x3", "3;x3 3;77", "3;x3 3;77 3;73"),
                       (r"(?<h>\d);(?:(?<h>\d)|x)\k<h>", "3;x3", "3;x3", "3;x3")):
    rx, where, off = lang(lit)
    _, perr = compiles(re.sub(r"\(\?<([A-Za-z_]\w*)>", r"(?'\1'", lit))
    sn[lit] = ("ERROR %s (offset %d)" % (where, off)) if rx is None else trip(rx, w, s_, f_)
    print("SN `%s`: the LANGUAGE %s ; libpcre2 on the literal as written: %s"
          % (lit, sn[lit] if rx is None else "LEGAL: " + show(rx, w, s_, f_), "COMPILES" if perr is None else "REJECTED (%s)" % perr))
# same-name-count, the hole case: q := /(?<h>b)/ in `/(?<h>a)-${q}\k<h>/`
scoped = P.Pcre(r"(?<h>a)-(?:(?<g>b))\k<h>")
print("SN same-name-count `/(?<h>a)-${q}\\k<h>/`, q := /(?<h>b)/: SCOPED (the record's \"inserted patterns' groups stay scoped\": q's group is not a second h): %s ; COUNTED: a COMPILE ERROR at the backreference, every mode"
      % show(scoped, "a-ba", "x a-bb a-ba", "a-ba a-bb a-ba"))
print("SN %s" % check("SN the error at the backreference, the literal legal, `\\2` legal, the corrected witness",
      sn[r"(?<h>a)(?<h>b)"][0] == "HOLDS" and sn[r"(?<h>\d)(?<h>\d)-\k<h>"].startswith("ERROR at the backreference")
      and sn[r"(?<h>\d)(?<h>\d)-\2"][0] == "HOLDS" and sn[r"(?J)(?<h>\d);(?:(?<h>\d)|x)\k<h>"][2] == "[`3;x3`@0, `3;73`@10]"
      and sn[r"(?<h>\d);(?:(?<h>\d)|x)\k<h>"].startswith("ERROR at the backreference") and W(scoped, "a-ba") is not None))

# =====================================================================================================================
print("\n== PART DD: dollar-diagnostic: for the emptiness diagnostics a read stands for ITS GROUP'S rx (the manager's call 4, THE DRAFT'S READING)")
DPOOL = pool("0123456789-", 4)
def lang_of(rx, cond):
    return {t for t in DPOOL if re.fullmatch(rx, t) and cond(t)}
def fires(prog_rx, grp_rx, cond):
    """the empty-intersection diagnostic under the reading: L(prog) & (L(group) & cond) empty over the pool"""
    if sab("t17"):
        return False                                  # the read as match-dependent: silent (rev 28's text)
    return not ({t for t in DPOOL if re.fullmatch(prog_rx, t)} & lang_of(grp_rx, cond))
lt5 = lambda t: canon(t) and int(t) < 5
gt100 = lambda t: canon(t) and int(t) > 100
progs = [(r"(?<x>\d+)-", r"\d+-", r"\d+", lt5), (r"(?<x>\d+)", r"\d+", r"\d+", lt5), (r"(?<x>\d)", r"\d", r"\d", gt100),
         (r"(?<x>\d\d)-?", r"\d\d-?", r"\d\d", lt5), (r"(?<x>\d+)-?", r"\d+-?", r"\d+", lt5)]
DP = pool("37-", 5) + pool("109", 4)
sound = True
for pre, prog_rx, grp, cond in progs:
    h = P.Pcre(pre + r'(?C"f")', {"f": lambda c, cond=cond: c.stretch() == c.get("x") and cond(c.get("x"))})
    hits = [sum(1 for t in DP if row(h, t, m) not in (False, None, ())) for m in "WSF"]
    fz = fires(prog_rx, grp, cond)
    sound &= (not fz) or hits == [0, 0, 0]
    print("DD `/%s/ & ($x & %s)`: the diagnostic %s ; texts with a hit over %d: %d / %d / %d"
          % (pre, "<5" if cond is lt5 else ">100", "FIRES" if fz else "silent", len(DP), hits[0], hits[1], hits[2]))
print("DD %s" % check("DD fires on the never-holding program, not on the holding one; never on a program that holds",
      fires(r"\d+-", r"\d+", lt5) and not fires(r"\d+", r"\d+", lt5) and sound))

# =====================================================================================================================
print("\n== PART RC: read COMPOUNDS lifted per member (THE DRAFT'S READING: each member a constant or a read, in the compound's order)")
def mem_y1(c):
    return arith(c.get("y"), "+", 1)
fns = [mem_y1, lambda c: arith("9", "+", 1)]
if sab("t18"):
    fns = list(reversed(fns))
rc1 = hole_seq(r'(?<y>\d)-', fns)
copies = P.Pcre("(?:" + "|".join("%d-(?:%s|10)" % (d, d + 1) for d in range(10)) + ")")
drc, _ = diff3(rc1, copies, pool("01389x-", 4) + ["x0-10", "3-10 9-10"])
print("RC `/(?<y>\\d)-${($y | \"9\") + 1}/`: %s ; vs the compile-time copies `(?:0-(?:1|10)|...|9-(?:10|10))` in libpcre2 %d / %d / %d"
      % (show(rc1, "3-10", "x0-10", "3-4 3-10 0-10"), drc[0], drc[1], drc[2]))
rc2 = hole_seq(r'(?<y>\d)-', [lambda c: arith(c.get("y"), "+", 1) if lt5(c.get("y")) else None])
print("RC `/(?<y>\\d)-${($y & <5) + 1}/`: %s" % show(rc2, "3-4", "7-8 3-4", "3-4 7-8 4-5"))
rc3 = hole_seq(r'(?<y>\d)-', [lambda c: arith(c.get("y") + "E", "+", 1)])
print("RC `/(?<y>\\d)-${($y . \"E\") + 1}/` (`3E` is no numeral: nothing): %s" % show(rc3, "3-4", "3-4", "3-4 3-3E"))
print("RC %s" % check("RC per-member lift", drc == [0, 0, 0] and fS(rc1, "x0-10") == "`0-1`@1" and fS(rc1, "x3-10") == "`3-10`@1"
      and W(rc2, "3-4") is not None and W(rc2, "7-8") is None and F(rc3, "3-4 3-3E") == []))

# =====================================================================================================================
print("\n== PART TT: T8/T9 as ONE class per operand, by an ORDERED clause list (the manager's call 1)")
CLAUSES = [("an assertion looking outside", "COMPILE ERROR (enumerate's edge-assertion error)"),
           ("infinite or over budget", "UNDER CONSTRUCTION"),
           ("a constant, a read, an array, a finite rx enumerate accepts", "BUILT NOW")]
if sab("t19"):
    CLAUSES = [CLAUSES[1], CLAUSES[0], CLAUSES[2]]
def props(rx):
    p = set()
    try:
        enum(rx)
    except Refused as e:
        s = str(e)
        p.add("an assertion looking outside" if "edge" in s else "infinite or over budget" if s in ("infinite", "over budget") else "other")
        if "edge" in s:                                 # an edge assertion AND infinite: both properties
            try:
                list(SRE.parse(rx))
                if re.search(r"\+|\*|\{\d+,\}", rx):
                    p.add("infinite or over budget")
            except Exception:
                pass
        return p
    p.add("a constant, a read, an array, a finite rx enumerate accepts")
    return p
def status(rx):
    pr = props(rx)
    for cond, st in CLAUSES:
        if cond in pr:
            return st
    return "NOT-MODELLED"
EXPECT = {r"(?<=x)ab": "COMPILE ERROR (enumerate's edge-assertion error)", r"(?<=x)\d+": "COMPILE ERROR (enumerate's edge-assertion error)",
          r"\b\d+\b": "COMPILE ERROR (enumerate's edge-assertion error)", r"\d+": "UNDER CONSTRUCTION",
          r"[0-9]{5}": "UNDER CONSTRUCTION", r"foobar|bazqux": "BUILT NOW", r"\d": "BUILT NOW"}
tt = {rx: status(rx) for rx in EXPECT}
for rx, st in tt.items():
    print("TT `left(/%s/, 2)` / `/%s/ + 1`: %s" % (rx, rx, st))
print("TT %s" % check("TT one class per operand, the hand-written table", tt == EXPECT))

# =====================================================================================================================
print("\n== PART UN: the never-matching rx as a PCRE spelling of the unset read; a value hole in a lookbehind")
NEVER = r"(?!)" if not sab("t20") else r"(?:)"
alg = hole(r'(?<y>\d)?-', lambda c, v: v in ([c.get("y")] if c.get("y") is not None else []) + ["x"])
spel = P.Pcre(r'(?<y>\d)?-(?:(?(y)\k<y>|%s)|x)' % NEVER)
du, fu = diff3(alg, spel, pool("37x-", 5))
print("UN `/(?<y>\\d)?-${$y | \"x\"}/` (callout model) vs the PCRE spelling `(?<y>\\d)?-(?:(?(y)\\k<y>|%s)|x)` over %d texts: %d / %d / %d (first %s)"
      % (NEVER, len(pool("37x-", 5)), du[0], du[1], du[2], fu))
lb = {}
for p in (r"(?<y>\d+)-(?<=\k<y>-)x", r"(?<y>\d)-(?<=\k<y>-)x"):
    rx, err = compiles(p)
    lb[p] = "REJECTED (%s)" % err if rx is None else show(rx, "3-x", "x3-x", "3-x 7-x")
    print("UN libpcre2 `%s` (the PCRE analogue of a value hole in a lookbehind): %s" % (p, lb[p]))
print("UN %s" % check("UN never-matching spelling; the lookbehind facts", du == [0, 0, 0]
      and lb[r"(?<y>\d+)-(?<=\k<y>-)x"].startswith("REJECTED (length of lookbehind") and not lb[r"(?<y>\d)-(?<=\k<y>-)x"].startswith("REJECTED")))

# =====================================================================================================================
print("\n== PART PW: padded's `0*` arm (FIXIND-14: a witness that separates `0*` from `0?`)")
def padset(L, v):
    return L is not None and v is not None and re.fullmatch((r"0?" if sab("t21") else r"0*") + re.escape(L), v) is not None
pwh = hole(r'(?<y>\d{4})-', lambda c, v: padset(arith(c.get("y"), "+", 1), v))
print("PW `/(?<y>\\d{4})-${padded($y + 1)}/`: %s" % show(pwh, "2025-002026", "x2025-002026", "2025-002026 2025-02026 2025-2026"))
print("PW %s" % check("PW `0*` admits two zeros", W(pwh, "2025-002026") is not None))

print("\n== CHECKS: %d of %d OK" % (sum(ok for _, ok in CHECKS), len(CHECKS)))
for n, ok in CHECKS:
    if not ok:
        print("FAILED CHECK: %s" % n)
