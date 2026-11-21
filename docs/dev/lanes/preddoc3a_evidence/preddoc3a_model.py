#!/usr/bin/env -S python3 -I
# Lane preddoc3a (2026-11-19): the evidence for the conversion of the core sections `core/model`, `core/patterns`,
# `core/labels`, `core/conditions`, `core/filters` (docs/design/predicates/core.md): every example line of those
# sections in WHOLE, SEARCHED and FIND-ALL, the manager's readings 1-3 of the lane's brief, the slug census.
# DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD. Three sources per example, none sharing its construction with another:
#  (1) THE PATH MODEL below (`run`): a small backtracking matcher written from the RULED WORDS (a condition is one more
#      piece of the pattern, tried where it stands; a rejecting piece sends the pattern to its next path in PCRE's
#      order; a branching resets the labels inside it on entry, the last mention wins; `P & Q` keeps a path of P whose
#      stretch Q matches WHOLE as its own text, P's paths outer; a complement holds when no path of B matches the
#      stretch whole; a lookahead and an atomic part offer their first path only; a backreference reads PCRE's capture).
#      It reports WHOLE (a path from 0 to the end), SEARCHED (the first path at the leftmost start) and FIND-ALL
#      (PCRE2's global loop: after an empty match, a non-empty retry at the same place, else one step).
#  (2) A LOWERING to plain regex run in python `re` (a condition on a one-character label written as a lookbehind on
#      the text that label holds; exact for these examples only, never a general lowering), where one exists; it
#      must give the same spans in every mode. Where no lowering exists the example says so.
#  (3) THE DRAFT'S PRINTED ANSWERS (docs/design/predicates_draft.md revision 29.1, or the record where it printed the
#      run), typed in by hand from the source named beside each example: the run must reproduce every printed answer
#      (the manager's reading 3).
#  Each example LINE printed by the formatter must occur verbatim in core.md.
#
# Run (W = the worktree; any cwd):  timeout 300 python3 -I -B W/docs/dev/lanes/preddoc3a_evidence/preddoc3a_model.py
# PREDDOC3A_SABOTAGE=sN (one at a time): a deliberately wrong rule; its named check must FAIL.
#   s1  a condition does not backtrack: the first path of the pattern is judged, no other     -> MATCH, ALT, TV
#   s2  a branching does NOT reset the labels inside it on entry (PCRE's capture carry)        -> ONE, FLOW, CAPT
#   s3  `&` with the RIGHT operand outer (join order reversed)                                 -> AND, AND2
#   s4  the right operand of `&` SEARCHED in the stretch (not matched whole)                   -> AND3
#   s5  a test on an ABSENT label holds (absence as a pass)                                    -> TV, TV2, ONE
#   s6  a lookahead re-entered (every inner path offered)                                      -> LOOK2
#   s7  an atomic part re-entered (every path offered)                                         -> ATOM
#   s8  the postfix quantifier applied to the last character, not the operand (a text paste)  -> QUANT
#   s9  a backreference reads the LABEL (reset on entry), not PCRE's capture                   -> CAPT2
#   s10 a sequence operand's backreference reads the WHOLE composition's last group            -> BREF
#   s11 `0` in a sequenced condition read from the condition's own point (empty)               -> ZERO
#   s12 a pass resets its body's labels at its start (no previous-pass value)                  -> PSR, PSR2
#   s13 a default reaches past its own test (the default applied to the label everywhere)      -> DEF
#   s14 the complement holds when SOME path of B fails (not when no path of B matches)         -> COMP, KINDS
#   s15 a sequenced condition tested once, after the loop                                      -> INSEQ
#   s16 a literal read with implicit extended mode (spaces dropped)                            -> LIT
#   s17 a flag written mid-literal applied to the whole literal                                -> FLAGS
#   s18 a part label's path read from the FIRST mention                                        -> PATH2
#   s19 a slug dropped from the details file                                                   -> SL
#   s20 a `needs:` into a later section planted                                                -> R2
#   s21 a ruled piece's rulings item pointed at a title the record does not hold               -> R1
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(W, "docs", "design", "predicates")
RECORD = os.path.join(W, "docs", "design", "plan_row_bodies", "COND-FAMILY.md")
SAB = set(x for x in os.environ.get("PREDDOC3A_SABOTAGE", "").split(",") if x)
FAILED, CHECKS = [], []


def sab(n):
    return n in SAB


def check(name, ok, detail=""):
    CHECKS.append(name)
    print("%-6s %s %s" % (name, "ok  " if ok else "FAIL", detail))
    if not ok:
        FAILED.append(name)


def doc(name):
    with open(os.path.join(PRED, name), encoding="utf-8") as f:
        return f.read()


# ================================================================== THE PATH MODEL
# A node is a tuple. A matcher is a generator of (end, state) in PCRE's preference order; state = (labels, caps, start)
# with labels and caps dicts (None = unset), start = where the rx being matched began (for `0`).
def names(n):
    k = n[0]
    if k == "grp":
        return {n[1]} | names(n[2])
    if k in ("seq", "alt"):
        out = set()
        for x in n[1]:
            out |= names(x)
        return out
    if k in ("rep", "look", "atomic", "not"):
        return names(n[1])
    if k == "amp":
        return names(n[1]) | names(n[2])
    return set()


def reset(st, n):
    if sab("s2"):
        return st
    lab = dict(st[0])
    for x in names(n):
        lab[x] = None
    return (lab, st[1], st[2])


def m(n, s, i, st):
    k = n[0]
    if k == "chr":                                   # one character of a class (python syntax), flags
        if i < len(s) and re.fullmatch(n[1], s[i], n[2] if len(n) > 2 else 0):
            yield i + 1, st
    elif k == "lit":
        if s.startswith(n[1], i):
            yield i + len(n[1]), st
    elif k == "seq":
        yield from mseq(n[1], 0, s, i, st)
    elif k == "alt":
        st = reset(st, n)
        for x in n[1]:
            yield from m(x, s, i, st)
    elif k == "rep":
        node, mn, mx, mode = n[1], n[2], n[3], n[4]
        if mode == "p":
            for r in mrep(node, mn, mx, "g", s, i, reset(st, n), 0):
                yield r
                return
        else:
            yield from mrep(node, mn, mx, mode, s, i, reset(st, n), 0)
    elif k == "grp":
        for j, st2 in m(n[2], s, i, st):
            lab, cap = dict(st2[0]), dict(st2[1])
            lab[n[1]] = s[i:j]
            cap[n[1]] = s[i:j]
            yield j, (lab, cap, st2[2])
    elif k == "cond":
        if n[1](st, s, i):
            yield i, st
    elif k == "look":                                # positive or negative lookahead
        paths = m(n[1], s, i, st)
        if n[2]:                                     # negative
            if next(paths, None) is None:
                yield i, st
        elif sab("s6"):
            for _j, st2 in paths:
                yield i, st2
        else:
            r = next(paths, None)
            if r is not None:
                yield i, r[1]
    elif k == "atomic":
        if sab("s7"):
            yield from m(n[1], s, i, st)
        else:
            r = next(m(n[1], s, i, st), None)
            if r is not None:
                yield r
    elif k == "amp":                                 # P & Q: Q matched WHOLE on the stretch's own text
        P, Q = n[1], n[2]
        if sab("s3") and Q[0] != "not":
            P, Q = Q, P
        for j, st2 in m(P, s, i, st):
            sub = s[i:j]
            for st3 in whole_paths(Q, sub, st2):
                yield j, st3
    elif k == "bref":
        v = st[0].get(n[1]) if sab("s9") else st[1].get(n[1])
        if v is not None and s.startswith(v, i):
            yield i + len(v), st
    elif k == "bol":
        if i == 0:
            yield i, st
    elif k == "eol":
        if i == len(s):
            yield i, st
    elif k == "wb":
        a = i > 0 and (s[i - 1].isalnum() or s[i - 1] == "_")
        b = i < len(s) and (s[i].isalnum() or s[i] == "_")
        if a != b:
            yield i, st
    else:
        raise ValueError(k)


def whole_paths(Q, sub, st):
    """Q judged on `sub` as the whole text (the filter sentence): its paths from 0 to the end, labels joined."""
    if Q[0] == "not":                                # a complement: no path of B matches the stretch whole
        B = Q[1]
        pathsB = [e for e, _ in m(B, sub, 0, (dict(st[0]), dict(st[1]), 0)) if e == len(sub)]
        if sab("s14"):
            allB = [e for e, _ in m(B, sub, 0, (dict(st[0]), dict(st[1]), 0))]
            if any(e != len(sub) for e in allB) or not allB:
                yield st
            return
        if not pathsB:
            yield st
        return
    inner = (dict(st[0]), dict(st[1]), 0)
    if sab("s4"):                                    # searched in the stretch instead of whole
        for a in range(len(sub) + 1):
            for e, st3 in m(Q, sub, a, inner):
                yield (st3[0], st3[1], st[2])
                return
        return
    for e, st3 in m(Q, sub, 0, inner):
        if e == len(sub):
            yield (st3[0], st3[1], st[2])


def mseq(nodes, k, s, i, st):
    if k == len(nodes):
        yield i, st
        return
    for j, st2 in m(nodes[k], s, i, st):
        yield from mseq(nodes, k + 1, s, j, st2)


def mrep(node, mn, mx, mode, s, i, st, count):
    def more():
        for j, st2 in m(node, s, i, st):
            if j == i:                               # an empty pass: it counts, the loop then stops
                if count + 1 >= mn:
                    yield j, st2
            else:
                yield from mrep(node, mn, mx, mode, s, j, st2, count + 1)
    can_more = mx is None or count < mx
    if mode == "l":
        if count >= mn:
            yield i, st
        if can_more:
            yield from more()
    else:
        if can_more:
            yield from more()
        if count >= mn:
            yield i, st


def paths(n, s, i):
    st = ({}, {}, i)
    if sab("s1"):                                    # the first path of the pattern only (conditions stripped first)
        yield from first_then_judge(n, s, i)
        return
    yield from m(n, s, i, st)


def first_then_judge(n, s, i):
    """s1: judge only the first path of the condition-free pattern (no backtracking into the pattern)."""
    def strip(x):
        k = x[0]
        if k == "cond":
            return ("seq", [])
        if k in ("seq", "alt"):
            return (k, [strip(y) for y in x[1]])
        if k == "rep":
            return ("rep", strip(x[1])) + x[2:]
        if k == "grp":
            return ("grp", x[1], strip(x[2]))
        if k in ("look", "atomic"):
            return (k, strip(x[1])) + x[2:]
        if k == "amp":
            return ("amp", strip(x[1]), x[2])
        return x
    r = next(m(strip(n), s, i, ({}, {}, i)), None)
    if r is None:
        return
    for j, st in m(n, s, i, ({}, {}, i)):
        if j == r[0] and st[0] == r[1][0]:
            yield j, st
            return


def whole(n, t):
    for j, st in paths(n, t, 0):
        if j == len(t):
            return True, st[0]
    return False, None


def searched(n, t):
    for a in range(len(t) + 1):
        for j, st in paths(n, t, a):
            return (t[a:j], a, st[0])
    return None


def findall(n, t):
    out, pos, retry = [], 0, False
    while pos <= len(t):
        if retry:
            retry = False
            hit = None
            for j, st in paths(n, t, pos):
                if j > pos:
                    hit = (j, st)
                    break
            if hit:
                out.append((t[pos:hit[0]], pos))
                pos = hit[0]
                continue
            pos += 1
            if pos > len(t):
                break
        found = None
        for a in range(pos, len(t) + 1):
            for j, st in paths(n, t, a):
                found = (a, j)
                break
            if found:
                break
        if not found:
            break
        a, j = found
        out.append((t[a:j], a))
        if j == a:
            retry = True
        pos = j
    return out


# ------------------------------------------------------------------ node builders
def C(cls, fl=0):
    return ("chr", cls, fl)


def L(t):
    return ("lit", t)


def S(*xs):
    return ("seq", list(xs))


def A(*xs):
    return ("alt", list(xs))


def R(x, mn, mx, mode="g"):
    return ("rep", x, mn, mx, mode)


def G(name, x):
    return ("grp", name, x)


def Q(pred):
    return ("cond", pred)


def AMP(p, q):
    return ("amp", p, q)


def NOT(b):
    return ("not", b)


D = C(r"\d")
DPLUS = R(D, 1, None)


def num(v):                                          # the canonical decimal numeral (core/values/number-domain)
    return int(v) if v is not None and re.fullmatch(r"0|[1-9]\d*", v) else None


def lab(name, test):                                 # (name: S): the label's text in S; absent fails (two-valued)
    def p(st, s, i):
        v = st[0].get(name)
        if v is None:
            return sab("s5")
        return test(v)
    return Q(p)


def lt(k):
    return lambda v: num(v) is not None and num(v) < k


def ge(k):
    return lambda v: num(v) is not None and num(v) >= k


# ------------------------------------------------------------------ the three modes, formatted
def run3(node, wt, srch, fa, show=()):
    wv = []
    for t in wt:
        ok, labs = whole(node, t)
        wv.append((t, ok, labs))
    return wv, searched(node, srch), (fa, findall(node, fa)), show


def labtxt(labs, show):
    if not show or labs is None:
        return ""
    return " (%s)" % ", ".join(("%s unset" % x) if labs.get(x) is None else ("%s = `%s`" % (x, labs[x])) for x in show)


def fmt(res, prog, srch_text):
    wv, sv, fv, show = res
    w = ", ".join("`%s` %s%s" % (t, "HOLDS" if ok else "FAILS", labtxt(labs, show) if ok else "") for t, ok, labs in wv)
    s = "`%s` %s" % (srch_text, ("`%s`@%d%s" % (sv[0], sv[1], labtxt(sv[2], show))) if sv else "FAILS")
    f = "`%s` [%s]" % (fv[0], ", ".join("`%s`@%d" % x for x in fv[1]))
    return "WHOLE %s / SEARCHED %s / FIND-ALL %s (%s)" % (w, s, f, prog)


def re3(rx, wt, srch, fa, flags=0):
    c = re.compile(rx, flags)
    wv = [(t, c.fullmatch(t) is not None) for t in wt]
    mm = c.search(srch)
    sv = (mm.group(0), mm.start()) if mm else None
    fv = [(x.group(0), x.start()) for x in c.finditer(fa)]
    return wv, sv, fv


def same_as_re(res, rx, wt, srch, fa, flags=0):
    wv, sv, fv, _ = res
    rw, rs, rf = re3(rx, wt, srch, fa, flags)
    return [(t, o) for t, o, _ in wv] == rw and ((sv[0], sv[1]) if sv else None) == rs and fv[1] == rf


def printed(res, whole_p=None, srch_p=False, fa_p=None, labels_p=None):
    """The draft's printed answers: whole_p {text: bool}; srch_p (text, start) or None; fa_p [(text, start)];
    labels_p {text: {label: value}} for WHOLE."""
    wv, sv, fv, _ = res
    d = dict((t, (o, l)) for t, o, l in wv)
    ok = True
    for t, v in (whole_p or {}).items():
        ok = ok and d[t][0] == v
    for t, want in (labels_p or {}).items():
        got = d[t][1] or {}
        ok = ok and all(got.get(k) == v for k, v in want.items())
    if srch_p is not False:
        ok = ok and ((sv[0], sv[1]) if sv else None) == srch_p
    if fa_p is not None:
        ok = ok and fv[1] == fa_p
    return ok


CORE = None


def in_core(line):
    global CORE
    if CORE is None:
        CORE = doc("core.md")
    return line in CORE


def example(tag, node, prog, wt, srch, fa, show=(), rx=None, rxflags=0, pr=None):
    """Run one example; compare with the lowering `rx` (python `re`) and the printed answers `pr` (kwargs of
    printed()); its line must be in core.md. -> (ok, line)."""
    res = run3(node, wt, srch, fa, show)
    line = fmt(res, prog, srch)
    ok_re = True if rx is None else same_as_re(res, rx, wt, srch, fa, rxflags)
    ok_pr = True if pr is None else printed(res, **pr)
    ok_doc = in_core(line)
    check(tag, ok_re and ok_pr and ok_doc, "%s | re %s | printed %s | doc %s" % (
        line, "n/a" if rx is None else ("same" if ok_re else "DIFFERS"), "n/a" if pr is None else
        ("reproduced" if ok_pr else "DIFFERS"), "found" if ok_doc else "NOT FOUND"))
    return ok_re and ok_pr and ok_doc


# ================================================================== THE EXAMPLES, one per piece
def ex_match():
    # core/model/match. The record (branch-scope, 11:35): `/(?<a>\d+)(?<b>\d+)/ & (a: 1)` on `123` holds a = 1, b = 23.
    node = S(G("a", DPLUS), G("b", DPLUS), lab("a", lambda v: v == "1"))
    example("MATCH", node, '`/(?<a>\\d+)(?<b>\\d+)/ & (a: "1")`', ["123", "23"], "x23 123", "123 213 1",
            show=("a", "b"), rx=r"1\d+", pr=dict(whole_p={"123": True}, labels_p={"123": {"a": "1", "b": "23"}}))


def ex_table():
    # core/model/table (a reading): the second branch reached when the first one's label is rejected.
    node = S(A(S(G("l", D), D), S(D, G("l", D))), lab("l", lambda v: v == "3"))
    example("TABLE", node, '`/(?<l>\\d)\\d|\\d(?<l>\\d)/ & (l: "3")`', ["73", "77"], "x737", "37 73 77",
            show=("l",), rx=r"3\d|\d3")


def ex_nest():
    # core/model/places/outermost-view: the record (nested-pass): `/(?:(?:(?<h>\d)?;)*,)*/ & (h: <5)`: `3;,,` and
    # `3;;,` FAIL from outside.
    inner = R(S(R(G("h", D), 0, 1), L(";")), 0, None)
    node = S(R(S(inner, L(",")), 0, None), lab("h", lt(5)))
    example("NEST", node, "`/(?:(?:(?<h>\\d)?;)*,)*/ & (h: <5)`", ["3;,", "3;,,", "3;;,"], "3;,,", "3;, 3;;, 4;,",
            pr=dict(whole_p={"3;,,": False, "3;;,": False}))


def ex_literal():
    # core/patterns/literals: a literal means what PCRE means; no implicit extended mode (`/a b|c/` keeps its space).
    node = A(S(L("a"), C(" "), L("b")), L("c")) if not sab("s16") else A(L("ab"), L("c"))
    example("LIT", node, "`/a b|c/`", ["a b", "ab"], "xa b", "c a b ab", rx=r"a b|c")


def ex_flags():
    # core/patterns/flags: a flag written mid-literal applies from where it is written.
    fl = re.I
    node = S(L("a"), C("b", fl)) if not sab("s17") else S(C("a", fl), C("b", fl))
    example("FLAGS", node, "`/a(?i)b/`", ["aB", "AB"], "AB aB", "ab aB Ab", rx=r"a(?i:b)")


def ex_sequence():
    # core/patterns/sequence: rev 25's PART RX1 (the draft R.1.14): `wb SEQ digits SEQ wb`.
    node = S(("wb",), DPLUS, ("wb",))
    example("SEQ", node, "`wb SEQ digits SEQ wb`, wb := `/\\b/`, digits := `/\\d+/`", ["12", "x12"], "x12 34",
            "12 x34 56", rx=r"\b\d+\b", pr=dict(whole_p={"12": True}, srch_p=("34", 4), fa_p=[("12", 0), ("56", 7)]))


def ex_alternation():
    # core/patterns/alternation: the draft R.1.4 (PART A B1): `(B | A) & (l: <20)` on `25` HOLDS l = 2 / `25`@0 /
    # on `25 13` [`25`@0, `13`@3]; A := `/(?<l>\d)\d/`, B := `/(?<l>\d\d)/`.
    node = S(A(G("l", S(D, D)), S(G("l", D), D)), lab("l", lt(20)))
    example("ALT", node, "`(B | A) & (l: <20)`, A := `/(?<l>\\d)\\d/`, B := `/(?<l>\\d\\d)/`", ["25", "7"], "25",
            "25 13", show=("l",), rx=r"\d\d",
            pr=dict(whole_p={"25": True}, labels_p={"25": {"l": "2"}}, srch_p=("25", 0), fa_p=[("25", 0), ("13", 3)]))


def ex_quant():
    # core/patterns/quantifiers: the draft R.1.14 (PART RX8): `("a" SEQ "b")+` is `(?:ab)+`: WHOLE `abb` FAILS,
    # SEARCHED `abbab` `ab`@0.
    node = R(S(L("a"), L("b")), 1, None) if not sab("s8") else S(L("a"), R(L("b"), 1, None))
    example("QUANT", node, '`("a" SEQ "b")+` is `(?:ab)+`', ["abab", "abb"], "abbab", "abab x ab",
            rx=r"(?:ab)+", pr=dict(whole_p={"abb": False}, srch_p=("ab", 0)))


def ex_atomic():
    # core/patterns/atomic: the draft R.1.4 (B8; V17): `atomic(B | A) & (l: <20)` on `25` FAILS / FAILS / [`13`@3]
    # (texts `25`, `25`, `25 13`).
    node = S(("atomic", A(G("l", S(D, D)), S(G("l", D), D))), lab("l", lt(20)))
    example("ATOM", node, "`atomic(B | A) & (l: <20)`, A := `/(?<l>\\d)\\d/`, B := `/(?<l>\\d\\d)/`", ["25", "13"],
            "25", "25 13", rx=r"1\d", pr=dict(whole_p={"25": False}, srch_p=None, fa_p=[("13", 3)]))


def ex_look():
    # core/patterns/lookaround: the draft R.1.4 (rev 26's PART LA): `/(?=\d*(?<l>\d)\b)(?<f>\d)\d*/` with
    # `(l: > $f)`: WHOLE `1234` HOLDS, SEARCHED `4321 1234` `1234`@5, FIND-ALL `1234 4321 77` [`1234`@0].
    look = ("look", S(R(D, 0, None), G("l", D), ("wb",)), False)
    cond = Q(lambda st, s, i: st[0].get("l") is not None and st[0].get("f") is not None
             and int(st[0]["l"]) > int(st[0]["f"]))
    node = S(look, G("f", D), R(D, 0, None), cond)
    example("LOOK", node, "`/(?=\\d*(?<l>\\d)\\b)(?<f>\\d)\\d*/ & (l: > $f)`", ["1234", "4321"], "4321 1234",
            "1234 4321 77", show=("l", "f"),
            pr=dict(whole_p={"1234": True}, labels_p={"1234": {"l": "4", "f": "1"}}, srch_p=("1234", 5),
                    fa_p=[("1234", 0)]))


def ex_look2():
    # core/patterns/lookaround: an outer condition never re-enters a lookahead (regex-settles (3), LA1):
    # `/(?=\d*(?<l>\d))\d+/ & (l: <5)` WHOLE `35`: the lookahead's first path sets l = `5`; re-entered, l = `3` would hold.
    node = S(("look", S(R(D, 0, None), G("l", D)), False), DPLUS, lab("l", lt(5)))
    ok35, ok53 = whole(node, "35")[0], whole(node, "53")[0]
    check("LOOK2", (not ok35) and ok53, "`/(?=\\d*(?<l>\\d))\\d+/ & (l: <5)` WHOLE `35` %s, `53` %s (PCRE: FAILS, HOLDS)"
          % ("HOLDS" if ok35 else "FAILS", "HOLDS" if ok53 else "FAILS"))


def ex_capt():
    # core/labels/labels-vs-captures: the draft R.1.7 (PART L): `/(?:(?<h>\d+)(?::(?<m>\d\d))?,)*\k<m>/` MATCHES
    # `9:45,10,45` WHOLE (`\k<m>` reads the capture `45`), `... & (m: "45")` FAILS there (the label m is unset) and
    # HOLDS on `9:45,10:45,45`.
    body = S(G("h", DPLUS), R(S(L(":"), G("m", S(D, D))), 0, 1), L(","))
    node = S(R(body, 0, None), ("bref", "m"), lab("m", lambda v: v == "45"))
    example("CAPT", node, '`/(?:(?<h>\\d+)(?::(?<m>\\d\\d))?,)*\\k<m>/ & (m: "45")`',
            ["9:45,10:45,45", "9:45,10,45"], "9:45,10,45 1:45,45", "9:45,10,45 1:45,45",
            pr=dict(whole_p={"9:45,10:45,45": True, "9:45,10,45": False}))
    # the regex half alone (no condition) is python `re`: it MATCHES `9:45,10,45` (the capture carries)
    node2 = S(R(body, 0, None), ("bref", "m"))
    ok, _ = whole(node2, "9:45,10,45")
    rr = re.fullmatch(r"(?:(?P<h>\d+)(?::(?P<m>\d\d))?,)*(?P=m)", "9:45,10,45") is not None
    check("CAPT2", ok and rr, "the backreference reads PCRE's capture: path model %s, python re %s (printed: MATCHES)"
          % (ok, rr))


def ex_onerule():
    # core/labels/one-rule: the draft R.1.7 (PART S S1, the table he was shown): `/(?:(?<a>\d)|(?<b>[a-z]))*xx/ &
    # (a: <5)`: `3qxx` FAILS, `q3xx` HOLDS a = 3, `7q3xx` HOLDS a = 3; SEARCHED on `3qxx` FAILS; FIND-ALL on
    # `3qxx q3xx 7q3xx` [`q3xx`@5, `7q3xx`@10].
    node = S(R(A(G("a", D), G("b", C("[a-z]"))), 0, None), L("xx"), lab("a", lt(5)))
    example("ONE", node, "`/(?:(?<a>\\d)|(?<b>[a-z]))*xx/ & (a: <5)`", ["3qxx", "q3xx", "7q3xx"], "3qxx",
            "3qxx q3xx 7q3xx", show=("a",),
            pr=dict(whole_p={"3qxx": False, "q3xx": True, "7q3xx": True},
                    labels_p={"q3xx": {"a": "3"}, "7q3xx": {"a": "3"}}, srch_p=None,
                    fa_p=[("q3xx", 5), ("7q3xx", 10)]))


def ex_flow():
    # core/labels/flow: the draft R.1.13 label-flow (3)(i): A := `/(?<h>\d)/`, B := `/(?:,(?<h>\d))?/`, `A SEQ B` on
    # `7` WHOLE HOLDS h UNSET, on `7,3` h = `3`; SEARCHED `x7 7,3` `7`@1 h unset; FIND-ALL `7 7,3` [`7`@0, `7,3`@2].
    node = S(G("h", D), R(S(L(","), G("h", D)), 0, 1))
    example("FLOW", node, "`A SEQ B`, A := `/(?<h>\\d)/`, B := `/(?:,(?<h>\\d))?/`", ["7", "7,3"], "x7 7,3",
            "7 7,3", show=("h",), rx=r"\d(?:,\d)?",
            pr=dict(whole_p={"7": True, "7,3": True}, labels_p={"7": {"h": None}, "7,3": {"h": "3"}},
                    srch_p=("7", 1), fa_p=[("7", 0), ("7,3", 2)]))


def ex_export():
    # core/labels/export: the draft R.1.13 (rev 29's PART TB (2)): `year := /(?<_v>\d{4})/ & (_v: >= 2000)`: WHOLE
    # `2025` HOLDS, `1999` FAILS / SEARCHED `x1999 2001` `2001`@6 / FIND-ALL `1999 2001 2025` [`2001`@5, `2025`@10].
    node = S(G("_v", S(D, D, D, D)), lab("_v", ge(2000)))
    example("EXP", node, "`year := /(?<_v>\\d{4})/ & (_v: >= 2000)`", ["2025", "1999"], "x1999 2001",
            "1999 2001 2025", rx=r"(?:[2-9]\d{3})",
            pr=dict(whole_p={"2025": True, "1999": False}, srch_p=("2001", 6), fa_p=[("2001", 5), ("2025", 10)]))


def ex_caller():
    # core/labels/export/caller-ambiguous (open): the match is the same under every candidate; h is what parts.
    node = AMP(S(G("h", D), D), S(D, G("h", D)))
    example("CALL", node, "`A & B`, A := `/(?<h>\\d)\\d/`, B := `/\\d(?<h>\\d)/`", ["12", "1"], "x12", "12 34",
            rx=r"\d\d", pr=dict(whole_p={"12": True}, srch_p=("12", 1), fa_p=[("12", 0), ("34", 3)]))


def ex_paths():
    # core/labels/paths: the draft R.1.13 label-flow (4) (rev 25's PART LF): `[aa = /(?<h>\d)\d/] & /\d(?<h>\d)/ &
    # (aa.h: <2)`: WHOLE `12` HOLDS, `21` FAILS; SEARCHED `21 12` `12`@3; FIND-ALL `12 21 10` [`12`@0, `10`@6].
    node = S(AMP(G("aa", S(G("aa.h", D), D)), S(D, G("h", D))), lab("aa.h", lt(2)))
    example("PATH", node, "`[aa = /(?<h>\\d)\\d/] & /\\d(?<h>\\d)/ & (aa.h: <2)`", ["12", "21"], "21 12",
            "12 21 10", rx=r"[01]\d",
            pr=dict(whole_p={"12": True, "21": False}, srch_p=("12", 3), fa_p=[("12", 0), ("10", 6)]))
    # path-and-ambiguity (ruled): a part label mentioned twice: the path reads the LAST mention.
    two = S(G("aa", G("aa.h", D)), L(","), G("aa", G("aa.h", D)))
    if sab("s18"):
        two = S(G("aa", G("aa.h", D)), L(","), G("aa", D))
    node2 = S(two, lab("aa.h", lt(5)))
    res = run3(node2, ["7,3", "3,7"], "3,7 7,3", "7,3 3,7 1,2")
    line = fmt(res, '`[aa = /(?<h>\\d)/] SEQ "," SEQ [aa = /(?<h>\\d)/] & (aa.h: <5)`', "3,7 7,3")
    check("PATH2", printed(res, whole_p={"7,3": True, "3,7": False}) and same_as_re(
        res, r"\d,[0-4]", ["7,3", "3,7"], "3,7 7,3", "7,3 3,7 1,2") and in_core(line),
          "%s | doc %s" % (line, "found" if in_core(line) else "NOT FOUND"))


def ex_bref():
    # core/labels/backreferences: the draft R.1.13 REFERENCES (1) (rev 26's PART REF REF2): A := `/(?<h>\d)/`,
    # B := `/(?<h>\d)\k<h>/`, `A SEQ B`: WHOLE `733` HOLDS, `737` FAILS (the written-out regex under (?J) gives the
    # reverse). The part's own group: modelled by renaming B's group apart (h2).
    if sab("s10"):
        node = S(G("h", D), G("h", D), ("bref", "h"), ("bref_first",)) if False else S(G("h", D), G("h2", D),
                                                                                       ("bref", "h"))
    else:
        node = S(G("h", D), G("h2", D), ("bref", "h2"))
    example("BREF", node, "`A SEQ B`, A := `/(?<h>\\d)/`, B := `/(?<h>\\d)\\k<h>/`", ["733", "737"], "x737 733",
            "733 737 455", rx=r"\d(\d)\1", pr=dict(whole_p={"733": True, "737": False}))


def ex_numbers():
    # core/labels/numbers: the draft R.1.13 (rev 25's PART NUM (2)): `/(\d):(\d)/ & (2: > $1)`: WHOLE `3:5` HOLDS,
    # `5:3` FAILS; SEARCHED `5:3 3:5` `3:5`@4; FIND-ALL `5:3 3:5 4:9` [`3:5`@4, `4:9`@8].
    cond = Q(lambda st, s, i: int(st[0]["2"]) > int(st[0]["1"]))
    node = S(G("1", D), L(":"), G("2", D), cond)
    example("NUM", node, "`/(\\d):(\\d)/ & (2: > $1)`", ["3:5", "5:3"], "5:3 3:5", "5:3 3:5 4:9",
            pr=dict(whole_p={"3:5": True, "5:3": False}, srch_p=("3:5", 4), fa_p=[("3:5", 4), ("4:9", 8)]))


def ex_numloop():
    # core/labels/numbers/in-loop (open number-in-loop): the draft R.1.13 (rev 26.1's PART R47 A3): `/(?:(\d)?;)*/ &
    # (1: <5)` WHOLE `3;;`: regex's capture HOLDS, the label FAILS.
    body = S(R(G("1", D), 0, 1), L(";"))
    node = S(R(body, 0, None), lab("1", lt(5)))
    res_label = whole(node, "3;;")[0]
    cap = re.fullmatch(r"(?:(\d)?;)*", "3;;")
    res_cap = cap is not None and cap.group(1) is not None and int(cap.group(1)) < 5
    example("NUML", node, "`/(?:(\\d)?;)*/ & (1: <5)`, the label reading", ["3;;", "3;"], "3;;", "3;; 7;3;",
            pr=dict(whole_p={"3;;": False}, srch_p=("3;", 0), fa_p=[("3;", 0), ("7;3;", 4)]))
    check("NUML2", (not res_label) and res_cap,
          "WHOLE `3;;`: the label reading %s, regex's capture %s (printed: the label FAILS, the capture HOLDS)"
          % ("HOLDS" if res_label else "FAILS", "HOLDS" if res_cap else "FAILS"))


def ex_form():
    # core/conditions/form: a record is the `&` of its entries.
    t = S(G("h", R(D, 1, 2)), L(":"), G("m", S(D, D)))
    node = S(t, lab("h", ge(10)), lab("m", lt(30)))
    example("FORM", node, "`/(?<h>\\d{1,2}):(?<m>\\d\\d)/ & (h: >= 10, m: <30)`", ["10:15", "9:15", "10:45"],
            "9:15 10:15", "10:15 9:15 11:20", rx=r"(?:[1-9]\d):(?:[1-2]\d)")


def ex_twovalued():
    # core/conditions/two-valued: the draft R.1.5 (PART A U1; V4): `/(?<b>\d+)(?<a>\d)?/ & (a: <5)` on `12` HOLDS
    # a = 2, b = 1 / `12`@0 / on `12 1 19 3` [`12`@0].
    node = S(G("b", DPLUS), R(G("a", D), 0, 1), lab("a", lt(5)))
    example("TV", node, "`/(?<b>\\d+)(?<a>\\d)?/ & (a: <5)`", ["12", "1"], "12", "12 1 19 3", show=("a", "b"),
            rx=r"\d+(?<=[0-4])(?<=\d\d)",
            pr=dict(whole_p={"12": True}, labels_p={"12": {"a": "2", "b": "1"}}, srch_p=("12", 0), fa_p=[("12", 0)]))
    # NOT on an absent label holds (U2): `/(?<b>\d+)(?<a>\d)?/ & NOT (a: <5)` on `1` HOLDS.
    notc = Q(lambda st, s, i: not (st[0].get("a") is not None and num(st[0]["a"]) is not None and num(st[0]["a"]) < 5)
             if not sab("s5") else (st[0].get("a") is not None and not num(st[0]["a"]) < 5))
    node2 = S(G("b", DPLUS), R(G("a", D), 0, 1), notc)
    ok, _ = whole(node2, "1")
    check("TV2", ok, "`NOT (a: <5)` on `1` (a absent): %s (printed U2: HOLDS)" % ("HOLDS" if ok else "FAILS"))


def ex_inseq():
    # core/conditions/in-sequence: the draft R.1.14 (rev 26's PART CS CS1): the condition tested each pass.
    item = S(G("h", D), lab("h", lt(5)), L(";")) if not sab("s15") else S(G("h", D), L(";"))
    node = R(item, 1, None)
    if sab("s15"):
        node = S(node, lab("h", lt(5)))
    example("INSEQ", node, '`(/(?<h>\\d)/ SEQ (h: <5) SEQ ";")+`', ["3;4;", "7;3;"], "7;3;", "3;7;4; 2;",
            rx=r"(?:[0-4];)+", pr=dict(whole_p={"7;3;": False}))


def ex_zero():
    # core/conditions/match-so-far: the record (zero-in-sequence, zeroseq.py): digit, `(0: /7/)`, digit: WHOLE `73`
    # HOLDS, `37` FAILS / SEARCHED `373` `73`@1 / FIND-ALL `73 77 37` [`73`@0, `77`@3].
    def p(st, s, i):
        so_far = s[st[2]:i] if not sab("s11") else ""
        return so_far == "7"
    node = S(D, Q(p), D)
    example("ZERO", node, "`/\\d/ SEQ (0: /7/) SEQ /\\d/`", ["73", "37"], "373", "73 77 37", rx=r"7\d",
            pr=dict(whole_p={"73": True, "37": False}, srch_p=("73", 1), fa_p=[("73", 0), ("77", 3)]))


def ex_psr():
    # core/conditions/pass-start-read: the draft R.1.7 (rev 25's PART PS): `/(?:(?=(?<n>\d))${c}(?<h>\d);)*/`,
    # c := 'h unset, or n >= h': WHOLE `3;4;7;` HOLDS, `3;3;9;` HOLDS, `3;7;4;` FAILS (SEARCHED `3;7;`@0).
    def c(st, s, i):
        h = st[0].get("h") if not sab("s12") else None
        n = st[0].get("n")
        return h is None or int(n) >= int(h)
    body = S(("look", G("n", D), False), Q(c), G("h", D), L(";"))
    node = R(body, 0, None)
    example("PSR", node, "`/(?:(?=(?<n>\\d))${c}(?<h>\\d);)*/`, c := `NOT (h: /\\d/) | (n: >= $h)`",
            ["3;4;7;", "3;7;4;"], "3;7;4;", "3;7;4; 9;1;",
            pr=dict(whole_p={"3;4;7;": True, "3;7;4;": False}, srch_p=("3;7;", 0)))
    # the control the draft names: WHOLE equals "the items are in non-decreasing order" over every text of `139;`
    import itertools
    ts = ["".join(p) for k in range(0, 6) for p in itertools.product("139;", repeat=k)]
    bad = 0
    for t in ts:
        intent = re.fullmatch(r"(?:\d;)*", t) is not None and all(
            a <= b for a, b in zip(re.findall(r"\d", t), re.findall(r"\d", t)[1:]))
        if whole(node, t)[0] != intent:
            bad += 1
    check("PSR2", bad == 0, "WHOLE vs the intent 'items non-decreasing' (python) on %d texts over `139;`: %d differ"
          % (len(ts), bad))


def ex_defaults():
    # core/conditions/defaults: the draft §R.3 (PART A N4): `(h = "x": !<5)` on `/(?<h>\d)?x/`: `x` HOLDS /
    # `3x` FAILS / `7x` HOLDS (WHOLE).
    def p(st, s, i):
        v = st[0].get("h")
        if v is None:
            v = "x"
        return not (num(v) is not None and num(v) < 5)
    node = S(R(G("h", D), 0, 1), L("x"), Q(p))
    if sab("s13"):                                  # the default leaks: an absent h reads `0` everywhere
        node = S(R(G("h", D), 0, 1), L("x"), Q(lambda st, s, i: not (num(st[0].get("h") or "0") < 5)))
    example("DEF", node, '`/(?<h>\\d)?x/ & (h = "x": !<5)`', ["x", "3x", "7x"], "3x x", "7x 3x x",
            rx=r"[5-9]?x", pr=dict(whole_p={"x": True, "3x": False, "7x": True}))


def ex_and():
    # core/filters/and: the draft R.1.4 (rev 24.4's PART F): `/\d+/ & /^\d$/` SEARCHED `a12 1` -> `1`@1.
    node = AMP(DPLUS, S(("bol",), D, ("eol",)))
    example("AND", node, "`/\\d+/ & /^\\d$/`", ["1", "12"], "a12 1", "12 3", rx=r"\d",
            pr=dict(srch_p=("1", 1)))
    # join order (left decides): `G & L` vs `L & G`, G := `/(?<a>\d+)/`, L := `/(?<c>\d+?)/`: on `11` `11`@0 vs `1`@0.
    Gn, Ln = G("a", DPLUS), G("c", R(D, 1, None, "l"))
    s1 = searched(AMP(Gn, Ln), "11")
    s2 = searched(AMP(Ln, Gn), "11")
    check("AND2", s1[:2] == ("11", 0) and s2[:2] == ("1", 0),
          "join order: `G & L` SEARCHED `11` %r, `L & G` %r (printed: `11`@0, `1`@0)" % (s1[:2], s2[:2]))
    # the right side matched WHOLE on the stretch, never searched in it: `/\d+/ & /1/` WHOLE `11` FAILS, `1` HOLDS.
    w11, w1 = whole(AMP(DPLUS, L("1")), "11")[0], whole(AMP(DPLUS, L("1")), "1")[0]
    check("AND3", (not w11) and w1, "`/\\d+/ & /1/` WHOLE `11` %s, `1` %s (the sentence: FAILS, HOLDS)"
          % ("HOLDS" if w11 else "FAILS", "HOLDS" if w1 else "FAILS"))


def ex_complement():
    # core/filters/complement: `/\d+/ & !/7\d*/`.
    node = AMP(DPLUS, NOT(S(L("7"), R(D, 0, None))))
    example("COMP", node, "`/\\d+/ & !/7\\d*/`", ["123", "712"], "a7 12", "7 12 77 37", rx=r"(?!7)\d+",
            pr=dict(whole_p={"123": True, "712": False}))


def ex_kinds():
    # core/filters/kinds: two complements combined, used beside a positive pattern (the ruled table's `neither`).
    seven = S(L("7"), R(D, 0, None))
    eight = S(L("8"), R(D, 0, None))
    node = AMP(AMP(DPLUS, NOT(seven)), NOT(eight))
    example("KINDS", node, "`/\\d+/ & neither`, neither := `not /7\\d*/ & not /8\\d*/`", ["123", "812"], "7 8 12",
            "12 7 8 93", rx=r"(?![78])\d+")


# ================================================================== THE MANAGER'S READINGS AND THE CENSUS
MINE = ("core/model", "core/patterns", "core/labels", "core/conditions", "core/filters")


def pieces():
    """-> list of (tag, status, needs) for core.md, in order; and section order."""
    out, sec_order = [], []
    tag = None
    for ln in doc("core.md").split("\n"):
        h = re.match(r"^## .*\[(core/[a-z0-9-]+)\]", ln)
        if h:
            sec_order.append(h.group(1))
        p = re.match(r"^### .*?\[(core/[a-z0-9/-]+)\]\s+(\S+)", ln)
        if p:
            tag = p.group(1)
            out.append([tag, p.group(2), []])
        elif tag and ln.startswith("needs:"):
            out[-1][2] += [x for x in re.split(r"[\s,]+", ln[6:]) if x]
    return out, sec_order


def r1():
    """Reading 1: every ruled piece of the five sections cites at least one record title that exists."""
    rec = open(RECORD, encoding="utf-8").read()
    det = doc("core_details.md")
    if sab("s21"):
        det = det.replace('(record: "2026-11-17 OWNER RULING — branchings reset',
                          '(record: "2026-11-17 OWNER RULING — branchings DO NOT reset')
    ps, _ = pieces()
    bad = []
    for tag, status, _n in ps:
        if not tag.startswith(MINE) or status != "ruled":
            continue
        m_ = re.search(r"^## %s — .*?(?=^## )" % re.escape(tag), det, re.S | re.M)
        titles = re.findall(r'\(record: "(.*?)"\)', m_.group(0), re.S) if m_ else []
        quotes = re.findall(r'^- \d{4}-\d\d-\d\d "(.*)" \(record: ', m_.group(0), re.M) if m_ else []
        nrec = " ".join(rec.split())
        badq = [q for q in quotes if " ".join(q.split()) not in nrec]
        if badq:
            print("       quote not verbatim in the record (%s): %s" % (tag, badq))
        found = [t for t in titles if " ".join(t.split()) in " ".join(rec.split())]
        if not found or len(found) != len(titles) or badq:
            bad.append(tag)
    n = sum(1 for t, s, _ in ps if t.startswith(MINE) and s == "ruled")
    check("R1", not bad, "%d ruled pieces; each rulings item's title found in the record: %s"
          % (n, "all" if not bad else "NOT for " + " ".join(bad)))


def r2():
    """Reading 2: no piece of the five sections needs a piece of a LATER section."""
    ps, order = pieces()
    sec = lambda t: "/".join(t.split("/")[:2])
    idx = dict((s, k) for k, s in enumerate(order))
    bad = []
    for tag, _s, needs in ps:
        if not tag.startswith(MINE):
            continue
        nd = list(needs)
        if sab("s20") and tag == "core/model/match":
            nd.append("core/holes/pattern")
        for x in nd:
            if idx.get(sec(x), -1) > idx[sec(tag)]:
                bad.append("%s -> %s" % (tag, x))
    check("R2", not bad, "needs: into a later section: %s" % (bad or "none"))


def census():
    ps, _ = pieces()
    mine = [(t, s) for t, s, _ in ps if t.startswith(MINE)]
    q = [t for t, s in mine if s == "?"]
    core = doc("core.md")
    skel = []
    tag = None
    for ln in core.split("\n"):
        p = re.match(r"^### .*?\[(core/[a-z0-9/-]+)\]", ln)
        if p:
            tag = p.group(1)
        elif tag and tag.startswith(MINE) and ln.strip() == "skeleton: yes":
            skel.append(tag)
    by = {}
    for t, s in mine:
        by[s if not s.startswith("open") else "open"] = by.get(s if not s.startswith("open") else "open", 0) + 1
    check("DONE", not q and not skel, "%d pieces in the five sections, by status %s; `?` left: %d; skeleton left: %d"
          % (len(mine), dict(sorted(by.items())), len(q), len(skel)))


def part_sl():
    draft = open(os.path.join(W, "docs", "design", "predicates_draft.md"), encoding="utf-8").read().split("\n")
    a = next(i for i, ln in enumerate(draft) if ln.startswith("### R.8 "))
    b = next(i for i, ln in enumerate(draft) if ln.startswith("### R.9 "))
    bold = set(re.findall(r"\*\*([a-z0-9]+(?:-[a-z0-9]+)+)\*\*", "\n".join(draft[a:b])))
    want = bold | {"group-truth", "negated-class-hole", "inner-label-read", "bare-condition-labels"}
    homed, mine = set(), set()
    det = doc("core_details.md")
    cur = None
    for ln in det.split("\n"):
        h = re.match(r"^## (core/[a-z0-9/-]+) — ", ln)
        if h:
            cur = h.group(1)
        if ln.startswith("slugs:"):
            ws = set(x for x in re.split(r"[\s,]+", ln[6:]) if x and x not in ("none", "-"))
            if sab("s19") and "caller-ambiguous" in ws:
                ws.discard("caller-ambiguous")
            homed |= ws
            if cur and cur.startswith(MINE):
                mine |= ws
    for f in ("library_details.md", "parked_details.md"):
        for ln in doc(f).split("\n"):
            if ln.startswith("slugs:"):
                homed.update(x for x in re.split(r"[\s,]+", ln[6:]) if x)
    miss = sorted(want - homed)
    check("SL", len(want) == 124 and not miss,
          "%d of %d slugs homed (R.8's %d bold kebab slugs + 4), %d of them on the five sections' entries "
          "(%d of those in the 124); missing: %s"
          % (len(want) - len(miss), len(want), len(bold), len(mine), len(mine & want), miss or "none"))
    print("       the five sections' slugs: %s" % " ".join(sorted(mine)))


for fn in [ex_match, ex_table, ex_nest, ex_literal, ex_flags, ex_sequence, ex_alternation, ex_quant, ex_atomic, ex_look, ex_look2,
           ex_capt, ex_onerule, ex_flow, ex_export, ex_caller, ex_paths, ex_bref, ex_numbers, ex_numloop, ex_form,
           ex_twovalued, ex_inseq, ex_zero, ex_psr, ex_defaults, ex_and, ex_complement, ex_kinds,
           r1, r2, census, part_sl]:
    try:
        fn()
    except Exception as ex:  # a part that raises is its own FAILED check
        import traceback
        traceback.print_exc()
        check("X" + fn.__name__, False, "raised %r" % ex)
print("preddoc3a_model: %d checks, %d failed%s" % (len(CHECKS), len(FAILED), (": " + " ".join(FAILED)) if FAILED else ""))
sys.exit(1 if FAILED else 0)
