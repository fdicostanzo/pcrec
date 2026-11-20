#!/usr/bin/env -S python3 -I
# Lane preddoc4 (2026-11-19): the evidence for the predicate documents' pieces added or changed by lane preddoc4
# (review r59's design-bearing findings, the manager's ruling R-1): every example line added or changed is RUN here
# in WHOLE, SEARCHED and FIND-ALL; every CORRECTED library body is built MECHANICALLY from its text as printed in
# docs/design/predicates/library.md (the `${p}` holes substituted, a parameter written outside a hole kept as
# literal text); and the manager's readings 1-2 are tested over the base files. DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD. The path engine of lane preddoc3c (copied whole below, unchanged): a node yields its ENDS from a start in
# PCRE's priority order over python `re`; `&` = both sides match one stretch whole. The control for each example is
# the answer typed in by hand from the record's or the draft's printed run, or, for an example new here, the plain
# regex the piece says the program equals (`re` on the written-out pattern); a check compares the run with it. PART
# DOC: every example line the formatter prints occurs verbatim in core.md or library.md.
#
# Run (W = the worktree; any cwd):  timeout 600 python3 -I -B W/docs/dev/lanes/preddoc4_evidence/preddoc4_model.py
# PREDDOC4_SABOTAGE=sN (one at a time): a deliberately wrong body or fact; its check must FAIL.
#   s1  padded's body text as it stood before the fix: `{n,}` / `{n}`, the parameter outside a hole  -> PD
#   s2  atomic(X) without the atomic group (`(?:X)`)                                             -> AT
#   s3  `!X` read as nothing-subtracted (the complement dropped)                                  -> KI
#   s4  comparisons read by VALUE (leading zeros ignored), not over canonical numerals             -> CM
#   s5  a tuple compared part by part (the per-part form) instead of in dictionary order            -> TU
#   s6  NOT peek(A) read as peek(A) (the negation dropped)                                        -> NE
#   s7  the match so far in a loop read from the rx's start in BOTH candidate lines               -> ZL
#   s8  some(c) read as "every pass"                                                              -> SO
#   s9  count(c) counting every pass, not the passes meeting c                                  -> CO
#   s10 .index 0-based                                                                            -> ME
#   s11 a computed label read as the concatenation of the reads, not their sum                    -> CL
#   s12 pattern($x) read as the backreference \k<x> (the match, not the pattern)                 -> PT
#   s13 rx.repeat's legality test read as min < max (the equal-bound copies dropped)              -> RP
#   s14 a document example line reworded                                                          -> DOC
#   s15 reading 1's table built with the R-1 moves undone (enumerate a core piece)                -> R1
#   s16 reading 2 with one called name dropped from the library's piece names                      -> R2
import itertools
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(W, "docs", "design", "predicates")
SAB = set(x for x in os.environ.get("PREDDOC4_SABOTAGE", "").split(",") if x)
FAILED, CHECKS, LINES = [], [], {}


def sab(n):
    return n in SAB


def check(name, ok, detail=""):
    CHECKS.append(name)
    print("%-6s %s %s" % (name, "ok  " if ok else "FAIL", detail))
    if not ok:
        FAILED.append(name)


# ------------------------------------------------------------------ the path engine
class R:
    """Regex text: ends in python's priority order; caps = the named groups of the path giving that end."""
    def __init__(self, rx):
        self.rx = re.sub(r"\(\?<(?=[A-Za-z_])", "(?P<", rx)     # PCRE's `(?<n>` is python's `(?P<n>`

    def ends(self, s, i):
        seen = []
        while True:
            excl = "".join(r"(?<!\A[\s\S]{%d})" % e for e in seen)
            m = re.compile("(?:%s)%s" % (self.rx, excl)).match(s, i)
            if not m:
                return
            seen.append(m.end())
            caps = [(k, m.start(k), m.end(k)) for k in m.re.groupindex if m.start(k) >= 0]
            yield m.end(), caps


class P:
    """A filter-only rx given as a predicate on the whole stretch (a comparison set, a condition on the stretch)."""
    def __init__(self, f):
        self.f = f

    def ends(self, s, i):
        for e in range(len(s), i - 1, -1):
            if self.f(s[i:e]):
                yield e, []


class AND:
    def __init__(self, a, b):
        self.a, self.b = a, b

    def ends(self, s, i):
        for e, c in self.a.ends(s, i):
            t = s[i:e]
            for e2, c2 in self.b.ends(t, 0):
                if e2 == len(t):
                    yield e, c + [(k, x + i, y + i) for k, x, y in c2]
                    break


class ALT:
    def __init__(self, *ns):
        self.ns = ns

    def ends(self, s, i):
        for n in self.ns:
            yield from n.ends(s, i)


class SEQ:
    def __init__(self, *ns):
        self.ns = ns

    def ends(self, s, i, k=0):
        if k == len(self.ns):
            yield i, []
            return
        for e, c in self.ns[k].ends(s, i):
            for e2, c2 in self.ends(s, e, k + 1):
                yield e2, c + c2


class CAP:
    def __init__(self, name, n):
        self.name, self.n = name, n

    def ends(self, s, i):
        for e, c in self.n.ends(s, i):
            yield e, c + [(self.name, i, e)]


class DEP:
    """A value hole: the node after `a` is computed from the text `a` took (None: no path)."""
    def __init__(self, a, f):
        self.a, self.f = a, f

    def ends(self, s, i):
        for e, c in self.a.ends(s, i):
            n = self.f(s[i:e])
            if n is None:
                continue
            for e2, c2 in n.ends(s, e):
                yield e2, c + c2


class ATOMIC:
    def __init__(self, n):
        self.n = n

    def ends(self, s, i):
        for x in self.n.ends(s, i):
            yield x
            return


class LOOP:
    """`(?:G){min,}` greedy, PCRE's rule as the draft's R.1.9 states it (review r47 V1): the first `min` iterations
    always run (and may be empty); after an empty iteration no further iteration is tried."""
    def __init__(self, g, mn=0):
        self.g, self.mn = g, mn

    def ends(self, s, i, k=0, had_empty=False):
        if k >= self.mn and had_empty:
            yield i, []
            return
        for e, c in self.g.ends(s, i):
            if k >= self.mn and e == i:
                yield e, c
                continue
            for e2, c2 in self.ends(s, e, k + 1, had_empty or e == i):
                yield e2, c + c2
        if k >= self.mn:
            yield i, []


def first(node, s, i):
    for x in node.ends(s, i):
        return x
    return None


def whole(node, t):
    for e, c in node.ends(t, 0):
        if e == len(t):
            return True, c
    return False, None


def searched(node, s):
    for i in range(len(s) + 1):
        x = first(node, s, i)
        if x:
            return (s[i:x[0]], i)
    return None


def find_all(node, s):
    out, pos = [], 0
    while pos <= len(s):
        hit = None
        for i in range(pos, len(s) + 1):
            x = first(node, s, i)
            if x:
                hit = (i, x[0])
                break
        if not hit:
            break
        i, e = hit
        if e == i:          # an empty match: PCRE retries here for a non-empty one, else moves on
            out.append((s[i:e], i))
            ne = None
            for e2, _ in node.ends(s, i):
                if e2 > i:
                    ne = e2
                    break
            if ne is not None and i + 1 <= len(s):
                out.append((s[i:ne], i))
                pos = ne
            else:
                pos = i + 1
            continue
        out.append((s[i:e], i))
        pos = e
    return out


def modes(node, whole_texts, srch, fa, label=None):
    wv = []
    for t in whole_texts:
        ok, c = whole(node, t)
        lab = None
        if ok and label:
            vals = sorted((x, t[x:y]) for k, x, y in c if k == label or k.startswith(label + "_"))
            lab = vals[-1][1] if vals else "unset"
        wv.append((t, ok, lab))
    return wv, (srch, searched(node, srch)), (fa, find_all(node, fa))


def fmt(res, prog):
    wv, sv, fv = res
    w = ", ".join("`%s` %s%s" % (t, "HOLDS" if ok else "FAILS", " (%s)" % lab if lab else "") for t, ok, lab in wv)
    s = "`%s` %s" % (sv[0], ("`%s`@%d" % sv[1]) if sv[1] else "FAILS")
    f = "`%s` [%s]" % (fv[0], ", ".join("`%s`@%d" % x for x in fv[1]))
    return "WHOLE %s / SEARCHED %s / FIND-ALL %s (%s)" % (w, s, f, prog)


def texts(alpha, n):
    for k in range(n + 1):
        for p in itertools.product(alpha, repeat=k):
            yield "".join(p)


def differ(a, b, alpha, n):
    """WHOLE / SEARCHED / FIND-ALL difference counts of two nodes over every text of the alphabet up to length n."""
    dw = ds = df = tot = 0
    for t in texts(alpha, n):
        tot += 1
        dw += whole(a, t)[0] != whole(b, t)[0]
        ds += searched(a, t) != searched(b, t)
        df += find_all(a, t) != find_all(b, t)
    return dw, ds, df, tot


def hole(x):
    return "(?:%s)" % x


def canon(t):
    return re.fullmatch(r"0|[1-9]\d*", t) is not None


def cmp_set(f):                    # a comparison set: canonical numerals whose value satisfies f
    return P(lambda t: canon(t) and f(int(t)))


def finite_alt(vals):              # a finite set of strings as an alternation (longest first; WHOLE checks only)
    return "|".join(re.escape(v) for v in sorted(vals, key=lambda v: (-len(v), v)))




# ------------------------------------------------------------------ the mechanical body builder (lane preddoc4)
def doc(name):
    return open(os.path.join(PRED, name), encoding="utf-8").read()


def body_text(fname, head):
    """The body printed in the document after `head :=`, as one code span (it may wrap onto the next line)."""
    s = doc(fname).replace("\n  ", " ")
    m = re.search(r"`%s := (.*?)`" % re.escape(head), s)
    if not m:
        raise SystemExit("no body for %s in %s" % (head, fname))
    return m.group(1)


def build(body, args):
    """A body's text to a node: `|`, `&`, parentheses, a parameter name (its node), `/regex/` with `${p}` holes.
    A hole whose value is a number inserts the numeral (a count position); one whose value is regex text inserts
    `(?:X)` (a pattern hole). Text outside `${...}` is kept as it is written, a parameter name included."""
    toks = re.findall(r"/(?:\\.|[^/\\])*/|\(|\)|\||&|[A-Za-z_]\w*", body)
    assert "".join(toks).replace(" ", "") == body.replace(" ", ""), (toks, body)
    pos = [0]

    def lit(t):
        def sub(m):
            v = args[m.group(1)]
            return str(v) if isinstance(v, int) else hole(v)
        return R(re.sub(r"\$\{(\w+)\}", sub, t[1:-1]))

    def atom():
        t = toks[pos[0]]
        pos[0] += 1
        if t == "(":
            n = alt()
            assert toks[pos[0]] == ")"
            pos[0] += 1
            return n
        if t.startswith("/"):
            return lit(t)
        return R(args[t])

    def conj():
        n = atom()
        while pos[0] < len(toks) and toks[pos[0]] == "&":
            pos[0] += 1
            n = AND(n, atom())
        return n

    def alt():
        ns = [conj()]
        while pos[0] < len(toks) and toks[pos[0]] == "|":
            pos[0] += 1
            ns.append(conj())
        return ns[0] if len(ns) == 1 else ALT(*ns)

    n = alt()
    assert pos[0] == len(toks)
    return n


def complement(rx):
    return P(lambda t: re.fullmatch(rx, t) is None)


# ------------------------------------------------------------------ PARTS
def part_PD():
    """padded: the corrected two-argument body and the one-argument body, built from library.md's text."""
    b2 = body_text("library.md", "padded(rx, n)")
    b1 = body_text("library.md", "padded(rx)")
    if sab("s1"):
        b2 = b2.replace("${n}", "n")
    fixed = "${n}" in b2 and not re.search(r"(?<!\$)\{n[,}]", b2)
    n2 = build(b2, {"rx": r"(?:\d\d)+?", "n": 3})
    n1 = build(b1, {"rx": "5"})
    got2 = fmt(modes(n2, ["0129"], "x0129", "0129 0000 12"), r"`/${padded(/(?:\d\d)+?/, 3)}/`")
    got1 = fmt(modes(n1, ["005", "50"], "x05", "5 x005 50"), '`/${padded("5")}/` is `0*(?:5)`')
    want2 = ("WHOLE `0129` HOLDS / SEARCHED `x0129` `0129`@1 / FIND-ALL `0129 0000 12` [`0129`@0, `0000`@5] "
             r"(`/${padded(/(?:\d\d)+?/, 3)}/`)")
    want1 = ("WHOLE `005` HOLDS, `50` FAILS / SEARCHED `x05` `05`@1 / FIND-ALL `5 x005 50` [`5`@0, `005`@3, `5`@7] "
             '(`/${padded("5")}/` is `0*(?:5)`)')
    # the other printed width answers (preddoc3c PART PW's controls): `\d{2,3}` n = 3 on 012, 0123 / `1|0123` n = 4
    n3 = build(b2, {"rx": r"\d{2,3}", "n": 3})
    n4 = build(b2, {"rx": "1|0123", "n": 4})
    extra = (whole(n3, "012")[0], whole(n3, "0123")[0], whole(n4, "0001")[0], whole(n4, "0123")[0])
    check("PD", fixed and got2 == want2 and got1 == want1 and extra == (True, False, True, True),
          "body %r built from its text: width line %s; one-argument line %s; \\d{2,3} n=3 012/0123, 1|0123 n=4 "
          "0001/0123 %s" % (b2, "as printed" if got2 == want2 else "DIFFERS: " + got2, "as printed" if got1 == want1
                             else "DIFFERS", extra))
    LINES["padded1"], LINES["padded2"] = got1, got2


def part_AT():
    b = body_text("library.md", "atomic(X)")
    if sab("s2"):
        b = b.replace("(?>", "(?:")
    x = build(b, {"X": "a|ab"})
    node = SEQ(x, R("c"))
    res = modes(node, ["ac", "abc"], "xabc ac", "ac abc ac")
    ctrl = re.compile(r"(?>(?:a|ab))c")
    ok = (res[0] == [("ac", True, None), ("abc", False, None)] and res[1][1] == ("ac", 5)
          and [(m.group(), m.start()) for m in ctrl.finditer("ac abc ac")] == res[2][1])
    check("AT", ok, "atomic(/a|ab/) SEQ \"c\" from the body %r: %s" % (b, res))
    LINES["atomic"] = fmt(res, '`atomic(/a|ab/) SEQ "c"` is `(?>(?:a|ab))c`')


def part_KI():
    def neg(rx):
        return R(".*") if sab("s3") else complement(rx)
    neither = AND(neg(r"7\d*"), neg(r"8\d*"))
    node = AND(R(r"\d+"), neither)
    res = modes(node, ["123", "812"], "7 8 12", "12 7 8 93")
    ok = res[0] == [("123", True, None), ("812", False, None)] and res[1][1] == ("12", 4) \
        and res[2][1] == [("12", 0), ("93", 7)]
    check("KI", ok, "`/\\d+/ & !/7\\d*/ & !/8\\d*/` (the printed answers): %s" % (res,))
    LINES["kinds"] = fmt(res, r"`/\d+/ & neither`, neither := `!/7\d*/ & !/8\d*/`")


def part_CM():
    def lt20(t):
        if sab("s4"):
            return t.isdigit() and int(t) < 20
        return canon(t) and int(t) < 20
    node = AND(R(r"\d+"), P(lt20))
    res = modes(node, ["19", "020", "20"], "x25", "25 7 019")
    # control: the comparison set written out as the plain regex of canonical numerals below 20
    ctrl = re.compile(r"(?:1\d|\d)")
    ok = (res[0] == [("19", True, None), ("020", False, None), ("20", False, None)]
          and all(bool(ctrl.fullmatch(t)) == ok_ for t, ok_, _ in res[0])
          and res[1][1] == ("2", 1) and res[2][1] == [("2", 0), ("5", 1), ("7", 3), ("0", 5), ("19", 6)])
    check("CM", ok, "`/\\d+/ & <20`: %s" % (res,))
    LINES["comparisons"] = fmt(res, r"`/\d+/ & <20`")


def part_TU():
    rx = re.compile(r"(\d{1,2}):(\d{2})")

    def ge(t):
        m = rx.fullmatch(t)
        if not m:
            return False
        h, mm = m.group(1), m.group(2)
        if not (canon(h) and canon(mm)):
            return False
        if sab("s5"):
            return int(h) >= 9 and int(mm) >= 30
        return (int(h), int(mm)) >= (9, 30)
    node = AND(R(r"(?<h>\d{1,2}):(?<m>\d{2})"), P(ge))
    res = modes(node, ["9:45", "9:15", "10:15"], "9:15 10:30", "9:30 9:15 12:45")
    ok = (res[0] == [("9:45", True, None), ("9:15", False, None), ("10:15", True, None)]
          and res[1][1] == ("10:30", 5) and res[2][1] == [("9:30", 0), ("12:45", 10)])
    check("TU", ok, "time & ((h, m): >= (9, 30)), dictionary order: %s" % (res,))
    LINES["tuples"] = fmt(res, r"`time & ((h, m): >= (9, 30))`, time := `/(?<h>\d{1,2}):(?<m>\d{2})/`")


def part_NE():
    pk = "(?=x)" if sab("s6") else "(?!x)"
    node = SEQ(R(r"\d"), R(pk))
    res = modes(node, ["7", "7x"], "7x 8", "1x 2 3x4")
    ctrl = re.compile(r"\d(?!x)")
    ok = (res[0] == [("7", True, None), ("7x", False, None)] and res[1][1] == ("8", 3)
          and [(m.group(), m.start()) for m in ctrl.finditer("1x 2 3x4")] == res[2][1])
    check("NE", ok, "`/\\d/ SEQ NOT peek(/x/)` is `\\d(?!x)`: %s" % (res,))
    LINES["negation"] = fmt(res, r"`/\d/ SEQ NOT peek(/x/)` is `\d(?!x)`")


class ZPASS:
    """One pass of `(/\\d/ SEQ (0: /\\d/) SEQ ";")+`: the `0` read from the pass's start or from the rx's start."""
    def __init__(self, mode):
        self.mode = mode

    def ends(self, s, i):
        for e1, c in R(r"\d").ends(s, i):
            origin = ZTOP.z0 if (self.mode == "rx" or sab("s7")) else i
            if re.fullmatch(r"\d", s[origin:e1]):
                for e2, c2 in R(";").ends(s, e1):
                    yield e2, c + c2


class ZTOP:
    z0 = 0

    def __init__(self, n):
        self.n = n

    def ends(self, s, i):
        ZTOP.z0 = i
        yield from self.n.ends(s, i)


def part_ZL():
    a = ZTOP(LOOP(ZPASS("pass"), 1))
    b = ZTOP(LOOP(ZPASS("rx"), 1))
    ra = modes(a, ["3;4;"], "3;4;", "3;4; 5;")
    rb = modes(b, ["3;4;"], "3;4;", "3;4; 5;")
    ok = (ra[0][0][1] is True and rb[0][0][1] is False and ra[2][1] == [("3;4;", 0), ("5;", 5)]
          and rb[2][1] == [("3;", 0), ("4;", 2), ("5;", 5)])
    check("ZL", ok, "the witness `(/\\d/ SEQ (0: /\\d/) SEQ \";\")+`: (a) the pass %s; (b) the rx's start %s" % (ra, rb))
    LINES["zero_a"] = fmt(ra, "(a) the pass's own match so far")
    LINES["zero_b"] = fmt(rb, "(b) the match so far from the rx's start")


def passes_node():
    return LOOP(SEQ(CAP("d", R(r"\d")), R(",")), 1)


class FILT:
    """A condition on the captures of the path (a group question): keeps the ends whose captures satisfy f."""
    def __init__(self, n, f):
        self.n, self.f = n, f

    def ends(self, s, i):
        for e, c in self.n.ends(s, i):
            if self.f([s[x:y] for k, x, y in c if k == "d"]):
                yield e, c


def part_SO():
    f = (lambda ds: ds and all(d == "7" for d in ds)) if sab("s8") else (lambda ds: any(d == "7" for d in ds))
    node = FILT(passes_node(), f)
    res = modes(node, ["1,7,", "1,2,"], "1,2, 7,", "7,1, 2, 3,7,")
    ok = (res[0] == [("1,7,", True, None), ("1,2,", False, None)] and res[1][1] == ("7,", 5)
          and res[2][1] == [("7,1,", 0), ("3,7,", 8)])
    check("SO", ok, "`/(?:(?<d>\\d),)+/ & some((d: \"7\"))`: %s" % (res,))
    LINES["some"] = fmt(res, '`/(?:(?<d>\\d),)+/ & some((d: "7"))`')


def part_CO():
    f = (lambda ds: len(ds) == 2) if sab("s9") else (lambda ds: sum(d == "7" for d in ds) == 2)
    node = FILT(passes_node(), f)
    res = modes(node, ["7,1,7,", "7,1,"], "7,7,7,", "7,7,7, 1,7,7,")
    ok = (res[0] == [("7,1,7,", True, None), ("7,1,", False, None)] and res[1][1] == ("7,7,", 0)
          and res[2][1] == [("7,7,", 0), ("1,7,7,", 7)])
    check("CO", ok, "`/(?:(?<d>\\d),)+/ & (n: ==2)`, n := count((d: \"7\")): %s" % (res,))
    LINES["count"] = fmt(res, '`/(?:(?<d>\\d),)+/ & (n: ==2)`, n := `count((d: "7"))`')


class IDX:
    """`/${days}/` with days := [w = [/Mon/, /Tue/, /Wed/]]: each branch carries `w.index`, 1-based."""
    def ends(self, s, i):
        for k, name in enumerate(["Mon", "Tue", "Wed"]):
            for e, c in R(name).ends(s, i):
                yield e, c + [("w.index", k if sab("s10") else k + 1, 0)]


def part_ME():
    node = FILT(IDX(), lambda ds: True)
    node = type("F", (), {"ends": lambda self, s, i: ((e, c) for e, c in IDX().ends(s, i)
                                                     if [x for k, x, y in c if k == "w.index"][0] >= 2)})()
    res = modes(node, ["Tue", "Mon"], "Mon Wed", "Tue Mon Wed")
    ok = (res[0] == [("Tue", True, None), ("Mon", False, None)] and res[1][1] == ("Wed", 4)
          and res[2][1] == [("Tue", 0), ("Wed", 8)])
    check("ME", ok, "`/${days}/ & (w.index: >= 2)`, 1-based: %s" % (res,))
    LINES["metadata"] = fmt(res, "`/${days}/ & (w.index: >= 2)`, days := `[w = [/Mon/, /Tue/, /Wed/]]`")


def part_CL():
    rx = re.compile(r"(\d)\+(\d)")

    def f(t):
        m = rx.fullmatch(t)
        if not m:
            return False
        v = int(m.group(1) + m.group(2)) if sab("s11") else int(m.group(1)) + int(m.group(2))
        return v < 10
    node = AND(R(r"(?<a>\d)\+(?<b>\d)"), P(f))
    res = modes(node, ["3+4", "7+8"], "7+8 2+2", "1+1 9+9 5+4")
    ok = (res[0] == [("3+4", True, None), ("7+8", False, None)] and res[1][1] == ("2+2", 4)
          and res[2][1] == [("1+1", 0), ("5+4", 8)])
    check("CL", ok, "`/(?<a>\\d)\\+(?<b>\\d)/ & (sum: <10)`, sum := $a + $b: %s" % (res,))
    LINES["computed"] = fmt(res, r"`/(?<a>\d)\+(?<b>\d)/ & (sum: <10)`, sum := `$a + $b`")


def part_PT():
    rx = r"(?<x>\d+),\k<x>" if sab("s12") else r"(?<x>\d+),(?:\d+)"
    node = R(rx.replace(r"\k<x>", "(?P=x)"))
    res = modes(node, ["12,345", "12,"], "a1,2", "1,22 3,4")
    ok = (res[0] == [("12,345", True, None), ("12,", False, None)] and res[1][1] == ("1,2", 1)
          and res[2][1] == [("1,22", 0), ("3,4", 5)])
    check("PT", ok, "`/(?<x>\\d+),${pattern($x)}/` is `(?<x>\\d+),(?:\\d+)`: %s" % (res,))
    LINES["pattern"] = fmt(res, r"`/(?<x>\d+),${pattern($x)}/` is `(?<x>\d+),(?:\d+)`")


def part_RP():
    copies = [(a, b) for a in (2, 4) for b in (2, 4) if (a < b if sab("s13") else a <= b)]
    body = "|".join(r"\d{%d,%d}" % c for c in copies)
    node = R("(?:%s)" % body)          # python has no branch reset `(?|`; no group inside, so the answers are equal
    res = modes(node, ["123", "1"], "12345", "12345 6")
    want = ("WHOLE `123` HOLDS, `1` FAILS / SEARCHED `12345` `12`@0 / FIND-ALL `12345 6` [`12`@0, `34`@2] "
            r"(`rx.repeat(rx.digit, min = n, max = n)`, n := [2, 4], is `(?|\d{2,2}|\d{2,4}|\d{4,4})`: the copy (4,2) removed)")
    got = fmt(res, r"`rx.repeat(rx.digit, min = n, max = n)`, n := [2, 4], is `(?|\d{2,2}|\d{2,4}|\d{4,4})`: the copy (4,2) removed")
    ok = got == want and body == r"\d{2,2}|\d{2,4}|\d{4,4}"
    check("RP", ok, "the count-hole copies %s; the line as printed: %s" % (body, got == want))
    LINES["repeat"] = got


def piece_tags(fname):
    return re.findall(r"^### .*?\[([a-z0-9/-]+)\]", doc(fname), re.M)


def part_R1():
    """Reading 1 (R-1's form): no core piece is a call-form name; every library piece has its defined: line."""
    core = doc("core.md")
    lib = doc("library.md")
    if sab("s15"):
        core += "\n### Enumerate   [core/arrays/enumerate]   ruled 2026-11-14\n`enumerate(rx)` lists.\n"
    heads = re.findall(r"^### (.*?)   \[(core/[a-z0-9/-]+)\]", core, re.M)
    # a call-form name piece: its heading is a name written as a call or a bare identifier the library defines
    lib_names = set(re.findall(r"`([a-z_][a-z0-9_.]*)\(", lib))
    bad = [t for h, t in heads if h.strip("`").split("(")[0].lower() in lib_names | {"enumerate", "import"}]
    pieces = re.split(r"^(?=### )", lib, flags=re.M)[1:]
    nodef = [re.search(r"\[(.*?)\]", p).group(1) for p in pieces if not re.search(r"^defined: ", p, re.M)]
    natives = []
    for p in pieces:
        m = re.search(r"^defined: native \((.*)\)$", p, re.M)
        if m:
            natives.append((re.search(r"\[(.*?)\]", p).group(1), m.group(1)))
    check("R1", not bad and not nodef, "core pieces named as a call: %s; library pieces without defined: %s; "
          "%d library pieces, %d native" % (bad, nodef, len(pieces), len(natives)))
    for t, why in natives:
        print("       native  %-36s %s" % (t, why))


def part_R2():
    """Reading 2: every name CALLED in a base example or body has a library piece (exceptions listed)."""
    lib = doc("library.md")
    names = set()
    for p in re.split(r"^(?=### )", lib, flags=re.M)[1:]:
        h = p.split("\n", 1)[0]
        for tok in h.split("[")[0].replace("###", "").split(","):
            tok = tok.strip().strip("`")
            if re.fullmatch(r"[A-Za-z_][\w.]*", tok):     # a heading that IS a name (not a phrase)
                names.add(tok)
        st = p.split("\n")[1] if "\n" in p else ""
        m = re.match(r"`([A-Za-z_][\w.]*)\(", st)
        if m:
            names.add(m.group(1))
    names |= {"occurs.exactly", "occurs.at_least", "occurs.at_most", "occurs.none", "rx.digit", "rx.digits",
              "rx.letter", "rx.any_of", "rx.range", "rx.none_of", "rx.repeat", "each_group", "where_group",
              "suffix_in", "slice_in", "assert.some", "assert.none", "assert.same"}
    if sab("s16"):
        names.discard("join")
    called = {}
    for f in ("core.md", "library.md"):
        for ln in doc(f).split("\n"):
            for code in re.findall(r"`([^`]*)`", ln):
                for n in re.findall(r"(?<![\w.$\\@/])([a-z_][a-z0-9_.]*)\((?!\?)", code):
                    called.setdefault(n, set()).add(f)
    BINDINGS = {"pair", "m", "f", "repeat", "search", "capture", "x", "date_in", "m.x"}   # bound in the example
    PARKED = {"cartesian"}                                  # a parked idea's name (parked.md), not provided
    CALLED_EXAMPLE_ONLY = {"days", "weekday", "weekday_of", "days_in", "luhn", "lex_ge", "all_matches", "concat",
                           "unpad", "even", "check"}
    def known(n):
        return n in names or n.split(".")[-1] in names or any(x.endswith("." + n) for x in names)
    missing = sorted(n for n in called if not known(n) and n not in BINDINGS | PARKED | CALLED_EXAMPLE_ONLY)
    listed = sorted(n for n in called if n in CALLED_EXAMPLE_ONLY)
    check("R2", not missing and "join" in called, "%d names called in the base files; without a library piece: %s; "
          "the listed exceptions found: %s" % (len(called), missing, listed))


def part_DOC():
    text = doc("core.md") + doc("library.md")
    if sab("s14"):
        text = text.replace("WHOLE `ac` HOLDS", "WHOLE `ac` holds", 1)
    missing = [k for k, v in LINES.items() if v not in text]
    check("DOC", not missing, "%d example lines, each verbatim in core.md or library.md; missing %s"
          % (len(LINES), missing))


def main():
    part_PD(); part_AT(); part_KI(); part_CM(); part_TU(); part_NE(); part_ZL(); part_SO(); part_CO(); part_ME()
    part_CL(); part_PT(); part_RP(); part_R1(); part_R2()
    if os.environ.get("PREDDOC4_LINES"):
        for k, v in LINES.items():
            print("LINE", k, v)
    part_DOC()
    print("checks %d, failed %d%s" % (len(CHECKS), len(FAILED), (": " + " ".join(FAILED)) if FAILED else ""))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
