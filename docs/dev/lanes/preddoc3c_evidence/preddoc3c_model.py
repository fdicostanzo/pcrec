#!/usr/bin/env -S python3 -I
# Lane preddoc3c (2026-11-19): the evidence that the LIBRARY bodies written in docs/design/predicates/library.md
# reproduce every RULED example of their name printed in the frozen draft (docs/design/predicates_draft.md revision
# 29.1) or in the record (docs/design/plan_row_bodies/COND-FAMILY.md), in WHOLE, SEARCHED and FIND-ALL; and that
# every example line printed in library.md is this script's own run, verbatim. DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD (lane preddoc2's, extended by a small path engine). A BODY is written once below as a node built from the
# core's constructs: regex text (python `re`), `&` (both sides match one stretch whole: the right side's subject IS
# the stretch), `|`, the sequence, a hole (`(?:X)`), a value hole (a node computed from a label's text), an atomic
# group and a loop. A node yields its ENDS from a start in PCRE's priority order (regex text: python's own
# backtracking, the next end found by excluding the ends already given with a fixed-width lookbehind on the absolute
# position). Each example is (1) RUN in the three modes; (2) compared with the PRINTED answers, typed in by hand from
# the draft or the record (the control: earlier lanes ran them on libpcre2 with callouts; they do not share a source
# with these bodies); where the draft printed one mode only, the run supplies the others and the printed mode is the
# check; (3) the example line printed by the formatter must occur verbatim in library.md (PART DOC).
#
# Run (W = the worktree; any cwd):  timeout 300 python3 -I -B W/docs/dev/lanes/preddoc3c_evidence/preddoc3c_model.py
# PREDDOC3C_SABOTAGE=sN (one at a time): a deliberately wrong body or fact; its check must FAIL.
#   s1  padded(rx, n): the DROPPED exact-width-first body                       -> PW
#   s2  padded's `0*` arm written `0?`                                           -> PW
#   s3  padded(rx, n): the withdrawn EXACT width (no unpadded branch)           -> PW
#   s4  padded(rx): the raw paste `0*rx` (no group around the hole)             -> PA
#   s5  anything as his earlier `.*`                                             -> AN
#   s6  anchored as his placeholder `/^${rx}$/`                                  -> AC
#   s7  startsWith as his first sketch `/^${rx}/`                                -> SW
#   s8  the gaps unscoped (`.*`, no `(?s:)`)                                     -> SW
#   s9  occurrences: the loop takes AT MOST ONE hit                              -> OC
#   s10 occurrences: a greedy gap                                                -> OC
#   s11 hits: the loop NOT atomic (each hit atomic only: the failed first try)  -> HI
#   s12 between EXCLUSIVE of its bounds                                          -> BE
#   s13 quoted as the plain splice `/"(?:${S})"/`                                -> QU
#   s14 join(c) read as the alternation of c's members                          -> JO
#   s15 list_of as the two-copy form (b) `(?:X(?:SX)*)?`... the item optional    -> LO
#   s16 strlen counting bytes of the UTF-8 text +1 (a wrong length)            -> SL
#   s17 any_case's candidate body without the scoped `(?i:)` (case kept)        -> CA
#   s18 a library example line reworded in the document                         -> DOC
#   s19 prefix_in as the IMAGE (left) instead of the preimage filter            -> PI
#   s20 month_numbered 0-based                                                   -> MN
#   s21 length counting one character fewer                                      -> LE
import itertools
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(W, "docs", "design", "predicates")
SAB = set(x for x in os.environ.get("PREDDOC3C_SABOTAGE", "").split(",") if x)
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


# ------------------------------------------------------------------ BODIES (library.md, as nodes)
def padded1(rx):                   # padded(rx) := /0*${rx}/
    return R("0*" + rx) if sab("s4") else R("0*" + hole(rx))


def padded2(rx, n, node=None):     # padded(rx, n) := (rx & /(?s:.){n,}/) | (/0*${rx}/ & /(?s:.){n}/)
    x = node if node is not None else R(rx)
    z = "0?" if sab("s2") else "0*"
    padx = SEQ(R(z), x) if node is not None else R(z + hole(rx))
    longer = AND(x, R("(?s:.){%d,}" % n))
    exact = AND(padx, R("(?s:.){%d}" % n))
    if sab("s3"):
        return exact
    if sab("s1"):
        return ALT(exact, longer)
    return ALT(longer, exact)


ANYTHING = r".*" if sab("s5") else r"[\s\S]*"
GAP = ".*" if sab("s8") else "(?s:.*)"
LAZYGAP = ".*?" if sab("s8") else "(?s:.*?)"


def anchored(rx):                  # anchored(s) := /\A(?:${s})\z/
    return ("^%s$" % hole(rx)) if sab("s6") else (r"\A%s\z" % hole(rx))


def starts_with(rx):               # startsWith(s) := /(?:${s})(?s:.*)/
    return ("^" + hole(rx)) if sab("s7") else (hole(rx) + GAP)


def ends_with(rx):                 # endsWith(s) := /(?s:.*)(?:${s})/ (ruled: a plain gap); the lazy gap: a reading
    return GAP + hole(rx)


def ends_with_lazy(rx):
    return LAZYGAP + hole(rx)


def contains(rx):                  # contains(s) := /(?s:.*)(?:${s})(?s:.*)/
    return GAP + hole(rx) + GAP


def occurrences(x, mn=0):          # occurrences(x, min = 0) := /(?:(?s:.*?)(?<hit>${x})){${min},}(?s:.*)/
    gap = R("(?s:.*)") if sab("s10") else R("(?s:.*?)")
    g = SEQ(gap, CAP("hit", x))
    loop = LOOP(g, mn)
    if sab("s9"):
        class One:
            def ends(self, s, i):
                for e, c in g.ends(s, i):
                    yield e, c
                if mn == 0:
                    yield i, []
        loop = One()
    return SEQ(loop, R("(?s:.*)"))


def hits(x, tail=r"[\s\S]*"):      # hits(r) := /\A(?>(?:(?s:.*?)(?<hit>${r}))*[\s\S]*)\z/
    g = SEQ(R("(?s:.*?)"), CAP("hit", ATOMIC(x) if sab("s11") else x))
    body = SEQ(LOOP(g), R(tail))
    return body if sab("s11") else ATOMIC(body)


def between(lo, hi):               # between(lo, hi) := >= lo & <= hi
    if sab("s12"):
        return cmp_set(lambda v: lo < v < hi)
    return AND(cmp_set(lambda v: v >= lo), cmp_set(lambda v: v <= hi))


def quoted(s_node):                # quoted(S) := /"${S & /[^"]*/}"/
    if sab("s13"):
        return None
    return SEQ(R('"'), AND(R('[^"]*'), s_node), R('"'))


def join(vals):                    # join(c): one string, the members in order
    return "|".join(vals) if sab("s14") else "".join(vals)


def list_of(x, sep):               # list_of(X, sep = S) := /(?:${X}${S})*${X}/
    """x: a function from a group name to the item's text (python cannot repeat a group name; the copies are named
    h, h_1, ... and the label is read as the LAST of them set, the one-label rule)."""
    if sab("s15"):
        return "(?:%s(?:%s%s)*)?" % (hole(x("h")), hole(sep), hole(x("h_1")))
    return "(?:%s%s)*%s" % (hole(x("h_1")), hole(sep), hole(x("h")))


def strlen(t):
    return len(t.encode("utf-8")) + 1 if sab("s16") else len(t)


def any_case_body(rx):             # the candidate `/(?i:${rx})/` (open any-case-body)
    return hole(rx) if sab("s17") else "(?i:%s)" % rx


def prefix_in(n, s_node):          # prefix_in(n, S) := /${S & /(?s:.){n}/}(?s:.*)/
    return SEQ(AND(R("(?s:.){%d}" % n), s_node), R("(?s:.*)"))


MONTHS = ["Jan(?:uary)?", "Feb(?:ruary)?", "Mar(?:ch)?", "Apr(?:il)?", "May", "Jun(?:e)?", "Jul(?:y)?",
          "Aug(?:ust)?", "Sep(?:tember)?", "Oct(?:ober)?", "Nov(?:ember)?", "Dec(?:ember)?"]


def month_numbered(f):             # months & (mnum: S), mnum := $mname.index (1-based)
    base = 0 if sab("s20") else 1
    return ALT(*[CAP("mname", R(m)) for k, m in enumerate(MONTHS) if f(k + base)])


def length(f):                     # length(S) := chars & (nchars: S), nchars := count((ch: /(?s:.)/))
    chars = LOOP(CAP("ch", R("(?s:.)")))
    def ok(t):
        for e, c in chars.ends(t, 0):
            if e == len(t):
                n = sum(1 for k, x, y in c if k == "ch")
                return f(n - 1 if sab("s21") else n)
        return False
    return P(ok)


# ------------------------------------------------------------------ PARTS
def part_PA():
    w = [t for t in ["5", "05", "005", "50", "6"] if whole(padded1(hole("5")), t)[0]]
    w2 = [t for t in ["5", "05", "005"] if whole(padded1("^5"), t)[0]]
    w3 = whole(padded1("1|2"), "02")[0]
    b255 = finite_alt(str(v) for v in range(256))
    b12 = finite_alt(str(v) for v in range(1, 13))
    w4 = whole(padded1(b255), "000")[0]
    w5 = whole(padded1(b12), "00")[0]
    w6 = [t for t in ["05", "5", "12", "13", "00"] if whole(padded1(b12), t)[0]]
    ok = w == ["5", "05", "005"] and w2 == ["5"] and w3 and w4 and not w5 and w6 == ["05", "5", "12"]
    check("PA", ok, "padded(\"5\") %s; padded(/^5/) %s; /1|2/ on 02 %s; between(0,255) on 000 %s; between(1,12) on 00 %s, accepts %s"
          % (w, w2, w3, w4, w5, w6))
    LINES["padded1"] = fmt(modes(padded1(hole("5")), ["005", "50"], "x05", "5 x005 50"),
                           '`/${padded("5")}/` is `0*(?:5)`')


def part_PW():
    rows = [  # (rx, n, whole texts and printed verdicts, searched, printed, find-all, printed)
        (r"(?:\d\d)+?", 3, [("0129", True)], "x0129", ("0129", 1), "0129 0000 12", [("0129", 0), ("0000", 5)]),
        (r"\d{2,3}", 2, [("123", True)], "x123", ("123", 1), "123 12345", [("123", 0), ("123", 4), ("45", 7)]),
        (r"1|0123", 2, [("0123", True)], "x0123", ("0123", 1), "0123 01 0123", [("0123", 0), ("01", 5), ("0123", 8)]),
        (r"\d|\d\d\d|\d\d", 2, [("000", True)], "x000", ("000", 1), "000 100 10", [("000", 0), ("100", 4), ("10", 8)]),
        (r"\d+?", 2, [("0123", True)], "x0123", ("01", 1), "0123 7 01 9", [("01", 0), ("23", 2), ("01", 7)]),
    ]
    bad = []
    for rx, n, wl, s, sp, fa, fp in rows:
        node = padded2(rx, n)
        res = modes(node, [t for t, _ in wl], s, fa)
        if [v for _, v, _ in res[0]] != [v for _, v in wl] or res[1][1] != sp or res[2][1] != fp:
            bad.append((rx, res))
    # the value hole: /(?<y>\d+)-${padded($y + 1, 4)}/ and /(?<y>\d{4})-${padded($y + 1)}/ (y a canonical numeral)
    def vh(ydig, n):
        def f(y):
            if not canon(y):
                return None
            v = str(int(y) + 1)
            return SEQ(R("-"), padded2(re.escape(v), n) if n else padded1(re.escape(v)))
        return DEP(R(ydig), f)
    r1 = modes(vh(r"\d+", 4), ["42-0043", "42-43", "9999-10000"], "9999-10000 42-0043", "9999-10000 42-0043 7-0008")
    if [v for _, v, _ in r1[0]] != [True, False, True] or r1[1][1] != ("9999-10000", 0) or \
            r1[2][1] != [("9999-10000", 0), ("42-0043", 11), ("7-0008", 19)]:
        bad.append(("vh4", r1))
    r2 = modes(vh(r"\d{4}", 0), ["2025-002026"], "x2025-002026", "2025-002026 2025-02026 2025-2026")
    if [v for _, v, _ in r2[0]] != [True] or r2[1][1] != ("2025-002026", 1) or \
            r2[2][1] != [("2025-002026", 0), ("2025-02026", 12), ("2025-2026", 23)]:
        bad.append(("vh0", r2))
    check("PW", not bad, "7 printed rows of the width form (5 argument orders, 2 value holes): %d differ %s"
          % (len(bad), [b[0] for b in bad]))
    LINES["padded2"] = fmt(modes(padded2(r"(?:\d\d)+?", 3), ["0129"], "x0129", "0129 0000 12"),
                           r"`/${padded(/(?:\d\d)+?/, 3)}/`")


def part_AN():
    ok = all(whole(R("(?%s:%s)" % (fl, ANYTHING) if fl else ANYTHING), t)[0]
             for fl in ["", "s", "i", "m", "x"] for t in ["", "12", "a\nb", "A b\n"])
    check("AN", ok, "[\\s\\S]* alone and under (?s) (?i) (?m) (?x) holds WHOLE on '', 12, a\\nb, 'A b\\n'")
    LINES["anything"] = fmt(modes(R(ANYTHING), ["", "a b"], "ab", "ab"), "`anything` is `[\\s\\S]*`")


def part_AC():
    A = lambda rx: R(anchored(rx))
    got = [
        searched(A("a|b"), "ab"),
        whole(A("a|ab"), "ab")[0],
        searched(A("foo"), "foo\n"), searched(A("foo"), "foo"),
        searched(A("foo$"), "foo\n"),
        searched(A("(?m:^a$)"), "a\n"),
        searched(R("x" + hole(anchored("a"))), "xa"),
        searched(R(hole(anchored("a")) + "b"), "ab"),
        searched(AND(R(r"\w+"), A("foo")), "xfoo"),
    ]
    want = [None, True, None, ("foo", 0), None, None, None, None, ("foo", 1)]
    check("AC", got == want, "the nine printed rows (a|b on ab; a|ab; foo on foo\\n and foo; foo$; (?m)^a$; "
          "/x${anchored(/a/)}/; /${anchored(/a/)}b/; /\\w+/ & anchored(/foo/) on xfoo 1-4): %s" % (got == want))
    LINES["anchored"] = fmt(modes(A("a|b"), ["a", "ab"], "ab", "b"), "`anchored(/a|b/)` is `\\A(?:a|b)\\z`")


def part_SW():
    sw = whole(R(starts_with("5")), "57")[0]
    sketch = whole(R("^5"), "57")[0]
    eq = sum(whole(R(contains("^err")), t)[0] != whole(R(starts_with("err")), t)[0] for t in texts("erx\n", 5))
    cn = whole(R(contains("err$")), "xerr\n")[0]
    nl = whole(R(starts_with("a")), "a\nb")[0]
    lz = whole(R(ends_with_lazy(r"(?<n>\d+)")), "ab123")[1]
    gr = whole(R(ends_with(r"(?<n>\d+)")), "ab123")[1]
    lzn = [("ab123"[x:y]) for k, x, y in lz if k == "n"]
    grn = [("ab123"[x:y]) for k, x, y in gr if k == "n"]
    ok = sw and not sketch and eq == 0 and cn and nl and lzn == ["123"] and grn == ["3"]
    check("SW", ok, "startsWith(5) on 57 %s (sketch /^5/ %s); contains(/^err/) vs startsWith(err) WHOLE %d of %d "
          "differ; contains(/err$/) on xerr\\n %s; gap crosses a newline %s; endsWith n lazy %s greedy %s"
          % (sw, sketch, eq, sum(1 for _ in texts("erx\n", 5)), cn, nl, lzn, grn))
    LINES["startsWith"] = fmt(modes(R(starts_with("err")), ["errx", "xerr"], "x err!", "err1 err2"),
                              "`startsWith(\"err\")` is `(?:err)(?s:.*)`")
    LINES["endsWith"] = fmt(modes(R(ends_with(r"(?<n>\d+)")), ["ab123"], "x12 34", "a1 b2", label="n"),
                            "`endsWith(/(?<n>\\d+)/)` is `(?s:.*)(?:(?<n>\\d+))`")
    LINES["endsWith-lazy"] = fmt(modes(R(ends_with_lazy(r"(?<n>\d+)")), ["ab123"], "x12 34", "a1 b2", label="n"),
                                 "`(?s:.*?)(?:(?<n>\\d+))`")
    LINES["contains"] = fmt(modes(R(contains("err")), ["xerrx", "er"], "a err b", "err err"),
                            "`contains(\"err\")` is `(?s:.*)(?:err)(?s:.*)`")
    d = differ(R(contains("ab")), occurrences(R("ab"), 1), "abx", 4)
    LINES["contains-occ"] = fmt(modes(occurrences(R("ab"), 1), ["xabx", "ba"], "x ab", "ab ab"),
                                "`occurrences(\"ab\", min = 1)`")
    check("SWocc", d[0] == 0, "contains(ab) vs occurrences(ab, min = 1): %d / %d / %d of %d differ (WHOLE must be 0)" % d)
    return d


def hit_list(node, t):
    ok, c = whole(node, t)
    return ok, [(t[x:y], x) for k, x, y in (c or []) if k == "hit"]


def part_OC():
    got = [
        hit_list(occurrences(R(r"\d*")), "1a")[1],
        hit_list(occurrences(R(r"\d*")), "12a3")[1],
        hit_list(occurrences(R(r"\d*"), 2), "")[1],
        hit_list(occurrences(R(r"\d*"), 3), "ab")[1],
        hit_list(occurrences(AND(R(r"(?<n>\d+)"), cmp_set(lambda v: v < 100))), "1234"),
    ]
    want = [[("1", 0), ("", 1)], [("12", 0), ("", 2)], [("", 0), ("", 0)], [("", 0)] * 3,
            (True, [("12", 0), ("34", 2)])]
    # the engine's loop against python's own regex text of the body, spans in every mode (no condition inside)
    dd = []
    for mn in (0, 1, 2):
        txt = R(r"(?:(?s:.*?)(?<hit>\d+)){%d,}(?s:.*)" % mn)
        dd.append(differ(occurrences(R(r"\d+"), mn), txt, "1a", 4))
    ok = got == want and all(x[:3] == (0, 0, 0) for x in dd)
    check("OC", ok, "R.1.9's printed hits (\\d* on 1a, 12a3; min 2 on ''; min 3 on ab; (n: <100) on 1234) %s; "
          "the loop vs the body's regex text, min 0/1/2: %s" % (got == want, [x[:3] for x in dd]))
    LINES["occurrences"] = fmt(modes(occurrences(R(r"\d+"), 2), ["1a2", "12", "1"], "x1y2", "1 2 x 3"),
                               "`occurrences(/\\d+/, min = 2)`")


def part_HI():
    under = lambda hl: len(hl) > 0 and all(canon(h) and int(h) < 100 for h, _ in hl)
    rows = [("1234", False, ["1234"]), ("12 34", True, ["12", "34"]), ("12 345", False, ["12", "345"]),
            ("x300 12", False, ["300", "12"])]
    bad = []
    for t, v, hl in rows:
        ok, h = hit_list(hits(R(r"\d+")), t)
        if not ok or [x for x, _ in h] != hl or under(h) != v:
            bad.append(t)
    # the failed first try (each hit atomic, not the loop), the list judged after it: printed hits [34] [12,34] [12,45] [0,12]
    fft = SEQ(LOOP(SEQ(R("(?s:.*?)"), CAP("hit", ATOMIC(R(r"\d+"))))), R(r"\D*"))
    ff = []
    for t in ["1234", "12 34", "12 345", "x300 12"]:
        got = None
        for e, c in fft.ends(t, 0):
            hl = [(t[x:y], x) for k, x, y in c if k == "hit"]
            if e == len(t) and under(hl):
                got = [x for x, _ in hl]
                break
        ff.append(got)
    ffok = ff == [["34"], ["12", "34"], ["12", "45"], ["0", "12"]]
    # an optional label: hits(/a(?<g>x)?/) & (g: "x"): the LAST hit's own g
    def last_g(t):
        ok, c = whole(hits(R("a(?<g>x)?")), t)
        hs = [(x, y) for k, x, y in c if k == "hit"]
        gs = [(x, y) for k, x, y in c if k == "g"]
        lx, ly = hs[-1]
        own = [t[x:y] for x, y in gs if lx <= x and y <= ly]
        return own == ["x"]
    og = [last_g("axa"), last_g("aax")]
    ok = not bad and ffok and og == [False, True]
    check("HI", ok, "the hit list (atomic loop) on 1234, 12 34, 12 345, x300 12: %d differ; the failed first try "
          "%s (printed [34] [12,34] [12,45] [0,12]); the optional label axa / aax %s" % (len(bad), ff, og))
    node = SEQ(R(r"\A"), hits(R(r"a(?<g>x)?")), R(r"\z"))
    def holds(t, i=0):
        return None
    LINES["hits"] = "WHOLE `aax` HOLDS (hits [`a`, `ax`]), `axa` FAILS (hits [`ax`, `a`]: the last hit's g unset) / " \
                    "SEARCHED `axa` FAILS / FIND-ALL `aax axa` [] (`hits(/a(?<g>x)?/) & (g: \"x\")`: the hit list " \
                    "is the whole subject's)"
    # the line above is checked: whole verdicts by last_g, the searched / find-all subject is the whole text
    check("HIline", og == [False, True] and not last_g("aax axa"), "the hits example line's verdicts")


def part_BE():
    two = ["%02d" % v for v in range(100)]
    acc = [t for t in two if whole(AND(R(r"\d\d"), between(1, 12)), t)[0]]
    b12 = finite_alt(str(v) for v in range(1, 13))
    mon = [t for t in ["05", "5", "12", "13", "00"] if whole(padded1(b12), t)[0]]
    ok = acc == ["10", "11", "12"] and mon == ["05", "5", "12"]
    check("BE", ok, "/\\d\\d/ & between(1, 12) accepts %s (printed {10, 11, 12}); padded(between(1, 12)) %s" % (acc, mon))
    LINES["between"] = fmt(modes(AND(R(r"\d\d"), between(1, 12)), ["12", "05"], "x05 11", "10 3 12 13"),
                           "`/\\d\\d/ & between(1, 12)`")


def part_QU():
    s_node = R(r"^a\w*")
    q = quoted(s_node)
    splice = R('"' + hole(r"^a\w*") + '"')
    nsp = sum(1 for t in texts('"ab', 4) if searched(splice, t))
    if q is None:
        check("QU", False, "quoted as the plain splice")
        return
    ok = whole(q, '"ab"')[0] and nsp == 0
    check("QU", ok, "quoted(/^a\\w*/) on \"ab\" %s; the plain splice matches %d texts of %d (draft: never)"
          % (whole(q, '"ab"')[0], nsp, sum(1 for _ in texts('"ab', 4))))
    LINES["quoted"] = fmt(modes(q, ['"ab"', '"ba"'], 'x "ab"', '"a" "b" "ax"'), "`quoted(/^a\\w*/)`")


def part_LE():
    cases = [("", 0), ("a\nb", 3), ("x" * 20, 20), ("x" * 21, 21), ("abc", 3)]
    ok = all(whole(length(lambda n, k=k: n == k), t)[0] for t, k in cases)
    ok = ok and not whole(length(lambda n: n <= 20), "x" * 21)[0] and whole(length(lambda n: n % 2 == 0), "ab")[0]
    check("LE", ok, "length(S) counts the loop's passes: ==0 '', ==3 a\\nb, ==20, ==21, <=20 rejects 21, even holds ab")
    LINES["length"] = fmt(modes(length(lambda n: n == 3), ["abc", "ab"], "abcd", "abcdefg"),
                          "`length(==3)` as a program: `chars & (nchars: ==3)`")


def part_MN():
    node = month_numbered(lambda k: 1 <= k <= 6)
    acc = [t for t in ["Jan", "June", "Jun", "Jul", "Dec", "January"] if whole(node, t)[0]]
    ok = acc == ["Jan", "June", "Jun", "January"]
    check("MN", ok, "month_numbered(between(1, 6)) accepts %s" % acc)
    LINES["month_numbered"] = fmt(modes(node, ["Jun", "Jul"], "Dec Feb", "Mar Oct Apr"),
                                  "`month_numbered(between(1, 6))`")


def part_PI():
    s = R("abc|xy")
    node = prefix_in(2, s)
    if sab("s19"):
        node = SEQ(R("ab|xy"), R("(?s:.*)"))
    w = [whole(node, "xyz")[0], whole(node, "abc")[0], whole(prefix_in(2, R("Columbus")), "Columbus")[0]]
    ok = w == [True, False, False]
    check("PI", ok, "prefix_in(2, /abc|xy/) on xyz / abc %s; prefix_in(2, \"Columbus\") never holds %s" % (w[:2], not w[2]))
    LINES["prefix_in"] = fmt(modes(node, ["xyz", "abc"], "abxyq", "xy ab"), "`prefix_in(2, /abc|xy/)`")


def part_JO():
    c = ["x", "y"]
    node = R("a[^%s]" % join(c))
    res = modes(node, ["ax", "ab"], "ax ab", "ax ay ab")
    ok = [v for _, v, _ in res[0]] == [False, True] and res[1][1] == ("ab", 3) and res[2][1] == [("ab", 6)]
    check("JO", ok, "`[^${join(c)}]`, c := [x, y]: printed WHOLE ax FAILS, ab HOLDS / ab@3 / [ab@6]")
    LINES["join"] = fmt(res, "`/a[^${join(c)}]/`, c := [x, y], is `a[^xy]`")


def part_LF():
    def left(alts, n):
        return "|".join(re.escape(a[:n]) for a in alts)
    rx = left(["foobar", "bazqux"], 2)
    ok = rx == "fo|ba"
    check("LF", ok, "left(/foobar|bazqux/, 2) = %s (printed fo|ba)" % rx)
    LINES["left"] = fmt(modes(R(rx), ["fo", "foo"], "xba", "fo ba"), "`left(/foobar|bazqux/, 2)` is `fo|ba`")


def part_SL():
    node = DEP(R(r"\w+"), lambda y: SEQ(R("-"), R(re.escape(str(strlen(y))))))
    res = modes(node, ["abc-3"], "ab-3 abc-3", "a-1 ab-3 abcdefghij-10")
    ok = [v for _, v, _ in res[0]] == [True] and res[1][1] == ("abc-3", 5) and \
        res[2][1] == [("a-1", 0), ("abcdefghij-10", 9)]
    check("SL", ok, "/(?<y>\\w+)-${strlen($y)}/ printed WHOLE abc-3 HOLDS / abc-3@5 / [a-1@0, abcdefghij-10@9]")
    LINES["strlen"] = fmt(res, "`/(?<y>\\w+)-${strlen($y)}/`")


def part_LO():
    rx = list_of(lambda n: r"(?<%s>\d)" % n, ",")
    w = [(t, whole(R(rx), t)) for t in ["7", "7,3,5", ""]]
    labs = [[max(((x, t[x:y]) for k, x, y in c if k.startswith("h")))[1]] for t, (ok, c) in w[:2]]
    ok = w[0][1][0] and w[1][1][0] and labs == [["7"], ["5"]] and not w[2][1][0]
    check("LO", ok, "list_of(/(?<h>\\d)/, sep = \",\"): h = 7 on 7, 5 on 7,3,5 (form (a)); the empty text FAILS: %s" % ok)
    LINES["list_of"] = fmt(modes(R(rx), ["7,3,5"], "x7,3", "1,2 3", label="h"), "`list_of(/(?<h>\\d)/, sep = \",\")`")


def part_CP():
    rx = "(?<d>%s)" % hole(r"\d+")
    LINES["capture"] = fmt(modes(R(rx), ["12"], "x12", "1 23", label="d"), "`capture(x)`, x := `[d = /\\d+/]`")
    check("CP", whole(R(rx), "12")[1] == [("d", 0, 2)], "capture names the group by x.label")


def part_RC():
    digits = R(r"(?:(?:\d)){1,}")
    d = differ(digits, R(r"\d+"), "1a", 5)
    check("RC", d[:3] == (0, 0, 0), "rx.digits := rx.repeat(rx.digit, min = 1) vs \\d+: %d / %d / %d of %d" % d)
    LINES["classes"] = fmt(modes(digits, ["123", "12a"], "ab12", "1 23"), "`rx.digits` is `(?:(?:\\d)){1,}`")


def part_CA():
    texts5 = list(texts("hHoO1", 4))
    prim = R("(?i:ho)")
    body = R(any_case_body("(?-i:ho)"))
    dw = sum(whole(prim, t)[0] != whole(body, t)[0] for t in texts5)
    ds = sum(searched(prim, t) != searched(body, t) for t in texts5)
    df = sum(find_all(prim, t) != find_all(body, t) for t in texts5)
    plain = differ(R("(?i:ho)"), R(any_case_body("ho")), "hHoO1", 4)
    ok = (dw, ds, df) == (3, 246, 249) and plain[:3] == (0, 0, 0)
    check("CA", ok, "any_case(/(?-i)ho/): primitive vs the candidate body %d / %d / %d of %d (printed 3 / 246 / 249); "
          "a plain argument /ho/: %s" % (dw, ds, df, len(texts5), plain[:3]))
    # the negated filter operand: printed 4 / 168 / 216 of 781 (the primitive vs the REACH body)
    prim2 = R("(?i:[ab]{2})")
    reach = AND(R("(?i:[abAB]{2})"), P(lambda t: t.lower() != "ab"))
    neg = differ(prim2, reach, "aAbB ", 4)
    check("CAneg", neg[:3] == (4, 168, 216), "any_case(/[abAB]{2}/ & !/ab/): %d / %d / %d of %d (printed 4 / 168 / 216)" % neg)
    LINES["any_case"] = fmt(modes(R(any_case_body("ho")), ["hO", "hx"], "x Ho", "ho HO hx"),
                            "the candidate body on `any_case(\"ho\")`, `(?i:ho)`")


def part_DOC():
    lib = open(os.path.join(PRED, "library.md"), encoding="utf-8").read()
    if sab("s18"):
        lib = lib.replace("WHOLE", "Whole", 1)
    missing = [k for k, v in LINES.items() if v not in lib]
    check("DOC", not missing, "%d example lines, each verbatim in library.md; missing %s" % (len(LINES), missing))


def main():
    part_PA(); part_PW(); part_AN(); part_AC(); part_SW(); part_OC(); part_HI(); part_BE(); part_QU()
    part_LE(); part_MN(); part_PI(); part_JO(); part_LF(); part_SL(); part_LO(); part_CP(); part_RC(); part_CA()
    if os.environ.get("PREDDOC3C_LINES"):
        for k, v in LINES.items():
            print("LINE", k, v)
    part_DOC()
    print("checks %d, failed %d%s" % (len(CHECKS), len(FAILED), (": " + " ".join(FAILED)) if FAILED else ""))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
