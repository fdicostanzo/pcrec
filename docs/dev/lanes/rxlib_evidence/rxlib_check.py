#!/usr/bin/env python3
# Lane rxlib (2026-11-17): checks for docs/design/rx_module.md. DESIGN EVIDENCE ONLY; rules nothing.
#
# What it checks:
#   PART A  the libpcre2 harness's own selfcheck (lane rxmodel's pcre2h.py, imported, never edited).
#   PART B  the three before/after examples of the note's section 1. BEFORE = today's spelling (a literal with holes)
#           written out BY HAND as its regex model (a hole is one atom `(?:...)`, a condition a callout at the place it
#           is written, the 2026-11-17 branch-scope ruling); AFTER = the literal-free spelling EXPANDED BY CODE from the
#           construct definitions of the note's section 2 (class Rx below, one function per construct). Both run on
#           libpcre2-8 (callouts serve the conditions) in WHOLE, SEARCHED and FIND-ALL over a text set, and both are
#           compared with an INDEPENDENT INTENT ORACLE: a plain regex with no labels and no callouts, run on Python `re`
#           (which shares no code with libpcre2 or with the expander), plus a Python-computed label where one is
#           reported.
#   PART C  the separator loop's definition (section 5) against a split-based oracle (Python `re`, plain constructs).
#   PART D  where a condition is written in a sequence (section 3): `(A & c) € B` against `(A € B) & c`.
#   PART E  the same label twice (section 4): what PCRE reads for a duplicate name, by backreference (no callout).
# RXLIB_SABOTAGE=1 breaks two construct definitions on purpose (the loop moves its item's conditions AFTER the loop,
# the regex reading of a bare label; `optional` becomes lazy): PART B and PART C must then report differences.
import itertools, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "rxmodel_evidence"))
import pcre2h  # noqa: E402

SAB = os.environ.get("RXLIB_SABOTAGE") == "1"
INF = None


# ---------------------------------------------------------------- the constructs (note section 2), as regex text
class Rx:
    """An rx under construction: its regex TEXT, its callouts {id: test}, its labels (in written order)."""
    n = 0

    def __init__(self, text, conds=None, labels=()):
        self.text, self.conds, self.labels = text, dict(conds or {}), list(labels)

    def atom(self):                       # the hole rule: a hole is ONE atom
        return "(?:%s)" % self.text


def merge(*parts):
    c, l = {}, []
    for p in parts:
        c.update(p.conds); l += p.labels
    return c, l


def text(s):                              # literal text: every character literal
    return Rx("".join("\\" + ch if not ch.isalnum() else ch for ch in s))


def digit():
    return Rx(r"\d")


def digits(lo=1, hi=INF):
    return Rx(r"\d{%d,%s}" % (lo, "" if hi is INF else hi))


def label(name, p):                       # `[name = p]`: a one-entry labelled array IS `(?<name>p)` (draft §3.1)
    c, l = merge(p)
    return Rx("(?<%s>%s)" % (name, p.text), c, [name] + l)


def seq(a, b):                            # A € B := /${A}${B}/
    c, l = merge(a, b)
    return Rx(a.atom() + b.atom(), c, l)


def alt(*ps):                             # [A, B] / A | B: PCRE's alternation; a label shared by branches -> (?|...)
    c, l = merge(*ps)
    shared = len(l) != len(set(l))
    return Rx(("(?|%s)" if shared else "(?:%s)") % "|".join(p.text for p in ps), c, sorted(set(l), key=l.index))


def optional(p, mode="greedy"):
    q = {"greedy": "?", "lazy": "??", "possessive": "?+"}["lazy" if SAB else mode]
    c, l = merge(p)
    return Rx(p.atom() + q, c, l)


def loop(p, lo=0, hi=INF, sep=None, mode="greedy"):
    """rx.loop(item, min, max, sep): item repeated; with sep, sep BETWEEN items (the item written twice)."""
    q = {"greedy": "", "lazy": "?", "possessive": "+"}[mode]
    body, conds = p, dict(p.conds)
    if SAB and p.conds:                   # sabotage: the item's conditions move AFTER the loop (last pass only)
        body = Rx(re.sub(r'\(\?C"[^"]*"\)', "", p.text), {}, p.labels)
    def rep(a, b):
        return "{%d,%s}" % (a, "" if b is INF else b)
    if sep is None:
        t = body.atom() + rep(lo, hi) + q
    else:
        tail = "(?:%s%s)%s%s" % (sep.atom(), body.atom(), rep(max(lo - 1, 0), INF if hi is INF else hi - 1), q)
        t = body.atom() + tail
        if lo == 0:
            t = "(?:%s)?%s" % (t, q)
    out = Rx(t, conds, p.labels)
    if SAB and p.conds:
        out.text += "".join('(?C"%s")' % k for k in p.conds)
    return out


def cond(p, lab, test, tag=None):         # p & (lab: S): a callout at the place the condition is written
    Rx.n += 1
    k = tag or "c%d" % Rx.n
    c, l = merge(p)
    c[k] = (lab, test)
    return Rx(p.text + '(?C"%s")' % k, c, l)


# ---------------------------------------------------------------- tests on numerals (canonical, draft §2.4)
def canon(s):
    return s is not None and re.fullmatch(r"0|[1-9]\d*", s) is not None


def lt(n):
    return lambda v: canon(v) and int(v) < n


# ---------------------------------------------------------------- running
def compile_model(pattern, conds):
    fns = {k: (lambda ctx, lab=lab, t=t: t(ctx.get(lab))) for k, (lab, t) in conds.items()}
    return pcre2h.Pcre(pattern, fns)


def run3(p, s, labs):
    w = p.whole(s)
    r = p.search(s)
    srch = None if r is None else (r[0], r[1], tuple(r[2].get(x) for x in labs))
    fa = tuple((a, b, tuple(d.get(x) for x in labs)) for a, b, d in p.findall(s))
    return w, srch, fa


def texts(alpha, n):
    for k in range(n + 1):
        for t in itertools.product(alpha, repeat=k):
            yield "".join(t)


def oracle3(plain, s, labfn):
    """Python `re` on a plain regex (no labels, no callouts); labels computed in Python from the matched text."""
    r = re.compile(plain)
    w = r.fullmatch(s) is not None
    m = r.search(s)
    srch = None if m is None else (m.start(), m.end(), labfn(m.group()))
    fa, pos = [], 0
    while pos <= len(s):
        m = r.search(s, pos)
        if m is None: break
        fa.append((m.start(), m.end(), labfn(m.group())))
        pos = m.end() if m.end() > m.start() else m.end() + 1
    return w, srch, tuple(fa)


def compare(name, before, after, plain, labfn, labs, alpha, n, show):
    pb, pa = compile_model(before.text, before.conds), compile_model(after.text, after.conds)
    print("  BEFORE regex model: %s" % before.text)
    print("  AFTER  expansion:   %s" % after.text)
    print("  INTENT (Python re): %s" % plain)
    for s in show:
        print("    on %-10r BEFORE %s" % (s, run3(pb, s, labs)))
        print("    on %-10r AFTER  %s" % (s, run3(pa, s, labs)))
    nb = [0, 0, 0]; no = [0, 0, 0]; first = [None, None]; tot = 0
    for s in texts(alpha, n):
        tot += 1
        b, a, o = run3(pb, s, labs), run3(pa, s, labs), oracle3(plain, s, labfn)
        for i in range(3):
            if b[i] != a[i]:
                nb[i] += 1; first[0] = first[0] or s
            if a[i] != o[i]:
                no[i] += 1; first[1] = first[1] or s
    print("  over %d texts: BEFORE vs AFTER differ WHOLE %d; SEARCHED %d; FIND-ALL %d (first %r)" % (tot, nb[0], nb[1], nb[2], first[0]))
    print("  over %d texts: AFTER vs INTENT differ WHOLE %d; SEARCHED %d; FIND-ALL %d (first %r)" % (tot, no[0], no[1], no[2], first[1]))
    return sum(nb) + sum(no)


def main():
    print("rxlib_check.py  libpcre2-8 %s  python %s  sabotage=%s" % (pcre2h.version(), sys.version.split()[0], SAB))
    bad = 0
    print("\nPART A  harness selfcheck")
    for line, ok in pcre2h.selfcheck():
        print("  %s %s" % ("OK " if ok else "BAD", line)); bad += (not ok)

    print("\nPART B  the three before/after examples (note section 1)")
    print("\nB1  every item of a list under 5")
    print("  BEFORE: item := /(?<h>\\d)/ & (h: <5)   then   /(?:${item};)*/")
    print("  AFTER : item := [h = rx.digit] & (h: <5)   then   rx.loop(item € \";\")")
    before = Rx('(?:(?:(?<h>\\d)(?C"b1"));)*', {"b1": ("h", lt(5))}, ["h"])
    after = loop(seq(cond(label("h", digit()), "h", lt(5)), text(";")))
    bad += compare("B1", before, after, r"(?:[0-4];)*", lambda g: (g[-2] if g else None,), ["h"],
                   "37;", 5, ["3;7;", "3;3;", "7;3;", "3;;"])

    print("\nB2  a time of day, labelled parts, a condition on the hour")
    print("  BEFORE: t2 := /(?<h>\\d{1,2})(?::(?<m>\\d\\d))?/   then   t2 & (h: <13)")
    print("  AFTER : t2 := [h = rx.digits(1, 2)] € rx.optional(\":\" € [m = rx.digits(2, 2)])   then   t2 & (h: <13)")
    before = Rx('(?<h>\\d{1,2})(?::(?<m>\\d\\d))?(?C"b2")', {"b2": ("h", lt(13))}, ["h", "m"])
    t2 = seq(label("h", digits(1, 2)), optional(seq(text(":"), label("m", digits(2, 2)))))
    after = cond(t2, "h", lt(13))
    def lab2(g):
        h, _, m = g.partition(":")
        return (h, m or None)
    bad += compare("B2", before, after, r"(?:1[0-2]|\d)(?::\d\d)?", lab2, ["h", "m"],
                   "1490:", 5, ["14:30", "9:30", "12:45", "00:30", "9:30 14:00"])

    print("\nB3  an alternation, a label in both branches, a condition outside it")
    print("  BEFORE: A := /(?<l>\\d)\\d/, B := /(?<l>\\d\\d)/   then   (B | A) & (l: <20)")
    print("  AFTER : A := [l = rx.digit] € rx.digit, B := [l = rx.digits(2, 2)]   then   (B | A) & (l: <20)")
    before = Rx('(?|(?<l>\\d\\d)|(?<l>\\d)\\d)(?C"b3")', {"b3": ("l", lt(20))}, ["l"])
    A = seq(label("l", digit()), digit()); B = label("l", digits(2, 2))
    after = cond(alt(B, A), "l", lt(20))
    bad += compare("B3", before, after, r"\d\d", lambda g: (g if lt(20)(g) else g[0],), ["l"],
                   "125 ", 4, ["25", "15", "25 13", "05"])

    print("\nPART C  the separator loop's definition (plain; Python re against a split oracle)")
    item, sep = Rx("[ab]"), text(",")
    nd = 0
    for lo, hi in [(0, INF), (1, INF), (0, 1), (0, 2), (2, 3), (3, 3)]:
        rxt = loop(item, lo, hi, sep).text
        r = re.compile(rxt); d = 0; firstd = None
        for s in texts("ab,", 6):
            parts = [] if s == "" else s.split(",")
            ok = all(p in ("a", "b") for p in parts) and lo <= len(parts) and (hi is INF or len(parts) <= hi)
            if (r.fullmatch(s) is not None) != ok:
                d += 1; firstd = firstd or s
        print("  loop([ab], min=%d, max=%s, sep=\",\") = %-48s differ %d of 1093 (first %r)" % (lo, "inf" if hi is INF else hi, rxt, d, firstd))
        nd += d
        one = "(?:(?(<s>)%s)%s(?<s>)){%d,%s}" % (sep.atom(), item.atom(), lo, "" if hi is INF else hi)
        r1 = pcre2h.Pcre(one); d1 = 0; f1 = None    # PCRE2, not Python re: Python refuses a forward (?(s)...)
        for s in texts("ab,", 6):
            parts = [] if s == "" else s.split(",")
            ok = all(p in ("a", "b") for p in parts) and lo <= len(parts) and (hi is INF or len(parts) <= hi)
            if r1.whole(s) != ok:
                d1 += 1; f1 = f1 or s
        print("    the ONE-COPY form (conditional group) %-40s differ %d of 1093 (first %r)" % (one, d1, f1))
    bad += nd

    print("\nPART D  where a condition stands in a sequence (note section 3)")
    A = label("h", digit()); Bp = optional(seq(text(";"), label("m", digit())))
    first = seq(cond(A, "h", lt(5), "dA"), Bp)          # (A & (h: <5)) € B
    second = cond(seq(A, Bp), "h", lt(5), "dB")         # (A € B) & (h: <5)
    pf, ps = compile_model(first.text, first.conds), compile_model(second.text, second.conds)
    print("  (A & (h: <5)) € B  =  %s" % first.text)
    print("  (A € B) & (h: <5)  =  %s" % second.text)
    d = [0, 0, 0]
    for s in texts("37;", 5):
        a, b = run3(pf, s, ["h", "m"]), run3(ps, s, ["h", "m"])
        for i in range(3): d[i] += a[i] != b[i]
    print("  c reads only A's label: differ WHOLE %d; SEARCHED %d; FIND-ALL %d of 364" % tuple(d))
    for s in ["3;7", "7;3"]:
        print("    on %r first %s | second %s" % (s, run3(pf, s, ["h", "m"]), run3(ps, s, ["h", "m"])))
    early = seq(cond(A, "m", lt(5), "dE"), Bp)          # (A & (m: <5)) € B: m is not set yet where c stands
    late = cond(seq(A, Bp), "m", lt(5), "dL")
    pe, pl = compile_model(early.text, early.conds), compile_model(late.text, late.conds)
    d = [0, 0, 0]
    for s in texts("37;", 5):
        a, b = run3(pe, s, ["h", "m"]), run3(pl, s, ["h", "m"])
        for i in range(3): d[i] += a[i] != b[i]
    print("  c reads B's label m:  differ WHOLE %d; SEARCHED %d; FIND-ALL %d of 364" % tuple(d))
    for s in ["3;3", "3;7"]:
        print("    on %r early %s | late %s" % (s, run3(pe, s, ["h", "m"]), run3(pl, s, ["h", "m"])))

    print("\nPART E  the same label twice: what PCRE reads for a duplicate name (backreference, no callout)")
    cases = [
        (r"(?J)(?'h'\d)(?:;(?'h'\d))?=\k<h>", ["3;7=3", "3;7=7", "3=3"], "two groups named h, both set: \\k<h> reads"),
        (r"(?J)(?'h'\d)(?:;(?'h'\d))*=\k<h>", ["1;2;3=1", "1;2;3=3"], "separator loop with the item written twice"),
        (r"(?:(?'h'\d);)*=\k<h>", ["1;2;3;=1", "1;2;3;=3"], "one group in a loop (the last-pass control)"),
        (r"(?:(?(<s>);)(?'h'\d)(?<s>))*=\k<h>", ["1;2;3=1", "1;2;3=3"], "the one-copy separator loop (conditional group)"),
    ]
    for pat, ss, what in cases:
        p = pcre2h.Pcre(pat)
        print("  %-44s %s: %s" % (pat, what, ", ".join("%s %s" % (s, "HOLDS" if p.whole(s) else "fails") for s in ss)))

    print("\nPART F  quantifier operators (rulings R2): `X ?` := /(?:${X})?/; the ends PCRE tries, in order, on `123`")
    print("  (a callout after the quantified part records the position and says \"fail here\"; the match is anchored at 0)")
    for pat in [r"(?:\d+)?", r"\d*", r"(?:\d+)??", r"\d*?", r"(?:\d+?)?", r"(?:\d+?)??", r"(?:\d+)?+", r"\d*+", r"(?:\d+)*", r"(?:\d+)+"]:
        seen = []
        q = pcre2h.Pcre(pat + '(?C"t")', {"t": lambda c, seen=seen: seen.append(c.pos)})
        q.match("123", 0, pcre2h.PCRE2_ANCHORED)
        same = "same strings as \\d*" if all((re.fullmatch(pat.replace("?+", "?").replace("*+", "*"), t) is not None) == (re.fullmatch(r"\d*", t) is not None) for t in texts("1x", 4)) else "other strings"
        print("  %-14s ends tried %-28s %s" % (pat, seen, same))
    print("\nPART G  the note's section 7 examples, each candidate run (WHOLE / SEARCHED / FIND-ALL)")
    def show(tag, pat, conds, labs, whole, srch, fa):
        q = compile_model(pat, conds) if conds else pcre2h.Pcre(pat)
        print("  %-34s %-46s WHOLE %r %s | SEARCHED %r %s | FIND-ALL %r %s" % (tag, pat, whole, q.whole(whole),
              srch, run3(q, srch, labs)[1], fa, run3(q, fa, labs)[2]))
    print("  sequence-reading: wb € rx.digits € wb (wb = \\b); the HOLE reading is the edge-assertion error (no run)")
    show("  splice reading", r"\b\d+\b", None, [], "12", "x12 34", "12 x34 56")
    print("  sequence-precedence: \"x\" € \"1\" | \"2\"")
    show("  P1 (€ tighter than |)", r"x1|2", None, [], "2", "y2", "x1 2 x2")
    show("  P3 (| tighter than €)", r"x(?:1|2)", None, [], "2", "y2", "x1 2 x2")
    print("  label-twice: [h = rx.digit] € rx.optional(\";\" € [h = rx.digit]) & (h: <5)")
    first = lambda c: lt(5)(c.get("h1"))
    last = lambda c: lt(5)(c.get("h2") if c.get("h2") is not None else c.get("h1"))
    show("  D2 PCRE (first set group)", r'(?<h1>\d)(?:;(?<h2>\d))?(?C"t")', {"t": ("h1", lt(5))}, ["h1", "h2"], "3;7", "3;7", "3;7 8;2")
    q = pcre2h.Pcre(r'(?<h1>\d)(?:;(?<h2>\d))?(?C"t")', {"t": last})
    print("  %-34s %-46s WHOLE '3;7' %s | SEARCHED '3;7' %s | FIND-ALL '3;7 8;2' %s" % ("  D3 last set", q.pattern, q.whole("3;7"), q.search("3;7"), q.findall("3;7 8;2")))
    print("  separator-label: rx.loop([h = rx.digit], sep = \",\") & (h: <5)")
    show("  two-copy (PCRE: first item)", r'(?:(?<h1>\d)(?:,(?<h2>\d))*)?(?C"t")', {"t": ("h1", lt(5))}, ["h1"], "7,3", "7,3", "7,3 1,9")
    show("  one-copy (last pass)", r'(?:(?(<s>),)(?<h>\d)(?<s>))*(?C"t")', {"t": ("h", lt(5))}, ["h"], "7,3", "7,3", "7,3 1,9")
    print("  count-argument: rx.digits(n, n) with n := [2, 4] (an enumeration of two members)")
    show("  C1 union, enumeration order", r"\d{2}|\d{4}", None, [], "1234", "12345", "12345")
    show("  C1 whole on 123", r"\d{2}|\d{4}", None, [], "123", "x", "x")
    show("  C3 hull", r"\d{2,4}", None, [], "123", "12345", "12345")
    print("  quantifier-operators: [a = rx.digits] ? lazy, then [b = rx.digits(0)] € \"x\", & (b: <30)")
    show("  (X ?) lazy on the outside", r'(?:(?<a>\d+))??(?<b>\d*)x(?C"t")', {"t": ("b", lt(30))}, ["a", "b"], "123x", "123x", "123x 45x")
    show("  X * lazy (the plain-regex twin)", r'(?<a>\d*?)(?<b>\d*)x(?C"t")', {"t": ("b", lt(30))}, ["a", "b"], "123x", "123x", "123x 45x")
    print("  quantifier-grammar: \"1\" + \"2\" if a sequence were juxtaposition")
    show("  quantifier reading 1+2", r"1+2", None, [], "112", "x1112", "12 112 3")
    show("  arithmetic reading (the rx 3)", r"3", None, [], "112", "x3", "12 112 3")
    print("\nSUMMARY: PART A failures + PART B and PART C (two-copy form) differences = %d (forward run expects 0; RXLIB_SABOTAGE=1 must move it)" % bad)


if __name__ == "__main__":
    main()
