#!/usr/bin/env -S python3 -I
# Lane preddoc6 (2026-11-19): the evidence for the predicate documents' example lines added or changed by lane
# preddoc6 (review r60's FIX-NOW batch): each is RUN here in WHOLE, SEARCHED and FIND-ALL (a WHOLE-only table in
# WHOLE), the program built MECHANICALLY from the text printed in the documents where the text is a body or a
# pattern; the manager's readings 2 and 3 are tested over the base files. DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD. The path engine and body builder of lane preddoc4 (docs/dev/lanes/preddoc4_evidence/preddoc4_model.py),
# copied unchanged below, extended by PART TV's path expander (every path of a pattern of optional atoms, in PCRE's
# priority order, as one plain regex per path). The control for every example line: the line the run prints must
# occur VERBATIM in core.md or library.md (PART DOC); the document's line was written from the record's, the draft's
# or the piece's own words before this run. Conditions are lowered by hand per example (a python predicate on the
# text a labelled part took), exact for these examples only.
#
# Run (W = the worktree; any cwd):  timeout 600 python3 -I -B W/docs/dev/lanes/preddoc6_evidence/preddoc6_model.py
# PREDDOC6_SABOTAGE=sN (one at a time): a deliberately wrong reading; its check must FAIL.
#   s1  NOT c read as the complement (NOT drops a path only if every path meets c)            -> TV
#   s2  repeat(x, n) built as the unbounded body                                              -> CF
#   s3  capture's name hole filled with the wrong name (the group renamed)                    -> CP
#   s4  the twelve month names out of calendar order (Jun and Jul swapped)                    -> MN
#   s5  the private label `_v` unreadable outside its literal (its condition dropped)          -> EX
#   s6  the bare condition's `0` read as the inserted part's own (empty: never a digit)       -> DG
#   s7  condition-group (b): the quantified test kept (read as the unquantified one)          -> CG
#   s8  reading 3 with `join` dropped from the library's names                                -> R3
#   s9  a document example line reworded                                                      -> DOC
import itertools
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(W, "docs", "design", "predicates")
SAB = set(x for x in os.environ.get("PREDDOC6_SABOTAGE", "").split(",") if x)
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


# ------------------------------------------------------------------ PARTS (lane preddoc6)
def line(key, node, whole_texts, srch, fa, prog, label=None):
    LINES[key] = fmt(modes(node, whole_texts, srch, fa, label), prog)
    return LINES[key]


def paths(pat):
    """Every path of a pattern made of atoms each optionally followed by `?` (greedy), in priority order: one plain
    regex per path (the atom kept or dropped). Atoms: a named group `(?<n>...)`, an escape `\\x`, one character."""
    toks = re.findall(r"(\(\?<\w+>[^()]*\)|\\.|[^\\(])(\??)", pat)
    assert "".join(a + q for a, q in toks) == pat, (toks, pat)
    choices = [[a, ""] if q else [a] for a, q in toks]
    return ["".join(c) for c in itertools.product(*choices)]


def part_TV():
    """core/conditions/two-valued: the three meanings over both columns of the printed table (WHOLE)."""
    s = doc("core.md")
    i = s.index("[core/conditions/two-valued]")
    tab = s[i:s.index("\n- A test that can never pass", i)]
    hdr = re.search(r"\| spelling \| P = `(.*?)`: (.*?) \(WHOLE\) \| P = `(.*?)`: (.*?) \(WHOLE\) \|", tab)
    cols = [(hdr.group(1).strip("/"), re.findall(r"`([^`]*)`", hdr.group(2))), (hdr.group(3).strip("/"), re.findall(r"`([^`]*)`", hdr.group(4)))]
    rows = re.findall(r"^  \| `(NOT \(h: <5\)|\(h: !<5\)|P & !\(P & \(h: <5\)\))` \| (.*?) \| (.*?) \|$", tab, re.M)
    lt5 = lambda h: h is not None and canon(h) and int(h) < 5

    def hs(pat, t):              # h on every path of P that matches t whole, in priority order
        out = []
        for p in paths(pat):
            m = re.fullmatch(R(p).rx, t)
            if m:
                out.append(m.groupdict().get("h"))
        return out

    def meaning(sp, pat, t):
        h = hs(pat, t)
        if sp == "NOT (h: <5)":
            if sab("s1"):
                return bool(h) and not any(lt5(x) for x in h)
            return any(not lt5(x) for x in h)
        if sp == "(h: !<5)":
            return any(x is not None and canon(x) and not lt5(x) for x in h)
        return bool(h) and not any(lt5(x) for x in h)
    bad = []
    for sp, c1, c2 in rows:
        for (pat, ts), printed in zip(cols, (c1, c2)):
            got = " / ".join("HOLDS" if meaning(sp, pat, t) else "FAILS" for t in ts)
            if got != printed.strip():
                bad.append((sp, pat, got, printed))
    check("TV", len(rows) == 3 and not bad, "3 spellings x 2 columns (paths of `%s` on `3x`: h = %s); differ %s"
          % (cols[1][0], hs(cols[1][0], "3x"), bad))


def part_CF():
    """core/operators/bindings/call-forms: `rx.repeat(rx.digit, 3)` by each of the two bodies it fits."""
    bn = body_text("library.md", "repeat(x, n)")
    bm = body_text("library.md", "repeat(x, min)")
    if sab("s2"):
        bn = bm.replace("min", "n")
    a = line("CF1", build(bn, {"x": r"\d", "n": 3}), ["1234"], "12345", "1234567",
             "`rx.repeat(rx.digit, 3)` by `repeat(x, n)`, `(?:\\d){3}`")
    b = line("CF2", build(bm, {"x": r"\d", "min": 3}), ["1234"], "12345", "1234567",
             "`rx.repeat(rx.digit, 3)` by `repeat(x, min)`, `(?:\\d){3,}`")
    check("CF", a != b, "bodies %s / %s; the two lines differ" % (bn, bm))


def part_CP():
    """lib/structural/capture: the body built from its text, the name hole filled raw, x a pattern hole."""
    s = doc("library.md")
    body = re.search(r"`capture\(name, x\) := (/.*?/)`", s).group(1)
    name = "e" if sab("s3") else "d"
    rx = body[1:-1].replace("${name}", name).replace("${x}", hole(r"\d+"))
    ok = rx == "(?<d>(?:\\d+))"
    line("CP", R(rx), ["12"], "x12", "1 23", '`capture("d", /\\d+/)` is `(?<d>(?:\\d+))`', label="d")
    LINES["CP"] = LINES["CP"].replace("HOLDS (12)", "HOLDS (d = `12`)")
    check("CP", ok, "built %s" % rx)


def part_MN():
    """lib/modifiers/month-numbered: the twelve names read from the body; `between(1, 6)` on the 1-based index."""
    s = doc("library.md").replace("\n  ", " ")
    arr = re.search(r"`months := \[mname = \[(.*?)\]\]`", s).group(1)
    names = re.findall(r"/([^/]*)/", arr)
    if sab("s4"):
        names[5], names[6] = names[6], names[5]
    node = ALT(*[R(n) for k, n in enumerate(names, 1) if 1 <= k <= 6])
    line("MN", node, ["Jun", "Jul"], "Dec Feb", "Mar Oct Apr", "`month_numbered(between(1, 6))`")
    check("MN", len(names) == 12, "%d names" % len(names))


def part_EX():
    """core/labels/export: the program `year` (the private label read by its own condition)."""
    f = (lambda v: True) if sab("s5") else (lambda v: v >= 2000)
    node = DEP(R(r"\d{4}"), lambda t: R("") if canon(t) and f(int(t)) else None)
    line("EX", node, ["2025", "1999"], "x1999 2001", "1999 2001 2025",
         "the program `year`, year := `/(?<_v>\\d{4})/ & (_v: >= 2000)`")
    check("EX", True, "lowered: the condition on the 4 digits `_v` took")


def part_DG():
    """core/holes/bare-condition: `/\\d${(0: rx.digit)}x/`, the `0` the surrounding match so far."""
    class ZERO:
        def ends(self, s, i):
            for e, c in R(r"\d").ends(s, i):
                so_far = "" if sab("s6") else s[i:e]
                if re.fullmatch(r"\d", so_far):
                    for e2, c2 in R("x").ends(s, e):
                        yield e2, c + c2
    line("DG", ZERO(), ["7x", "77x"], "a7x", "7x 12x 8x", "`/\\d${(0: rx.digit)}x/`")
    check("DG", True, "lowered: the match so far at the hole is the `\\d` before it")


def part_CG():
    """core/conditions/quantified/group: candidate (b) (the test vanishes) and the unquantified control."""
    cond = lambda t: R("") if int(t) < 5 else None
    if sab("s7"):
        qb = DEP(R(r"\d"), cond)
    else:
        qb = DEP(R(r"\d"), lambda t: ALT(R(""), R("")) if cond(t) else R(""))   # `(...)?`: the group, else empty
    line("CG1", qb, ["7"], "x7", "7 3", "(b), `[h = rx.digit] SEQ ((h: <5))?`; under (a) a compile error")
    line("CG2", DEP(R(r"\d"), cond), ["7", "3"], "x7", "7 3", "unquantified, `[h = rx.digit] SEQ (h: <5)`")
    check("CG", True, "lowered: h the digit; the condition zero-width after it")


def part_EV():
    """lib/counting/count's bullet: `/\\d*[02468]/` is the even counts (numerals 0..999)."""
    bad = [n for n in range(1000) if (re.fullmatch(r"\d*[02468]", str(n)) is not None) != (n % 2 == 0)]
    check("EV", not bad, "0..999: %d disagree" % len(bad))


def part_R3():
    """Reading 3: every name CALLED in a base example or body has a library piece (exceptions listed); a bare
    `digit` in a base code span is reported (the R2 scan of lane preddoc4 does not see a name used without a call)."""
    lib = doc("library.md")
    names = set()
    for p in re.split(r"^(?=### )", lib, flags=re.M)[1:]:
        h = p.split("\n", 1)[0]
        for tok in h.split("[")[0].replace("###", "").split(","):
            tok = tok.strip().strip("`")
            if re.fullmatch(r"[A-Za-z_][\w.@]*", tok):
                names.add(tok.lstrip("@"))
        st = p.split("\n")[1] if "\n" in p else ""
        m = re.match(r"`@?([A-Za-z_][\w.]*)\(", st)
        if m:
            names.add(m.group(1))
    names |= {"occurs.exactly", "occurs.at_least", "occurs.at_most", "occurs.none", "rx.digit", "rx.digits",
              "rx.letter", "rx.any_of", "rx.range", "rx.none_of", "rx.repeat", "each_group", "where_group",
              "suffix_in", "slice_in", "assert.some", "assert.none", "assert.same", "warn.off", "warn.error"}
    if sab("s8"):
        names.discard("join")
    called = {}
    bare_digit = []
    for f in ("core.md", "library.md", "parked.md"):
        for k, ln in enumerate(doc(f).split("\n"), 1):
            for code in re.findall(r"`([^`]*)`", ln):
                for n in re.findall(r"(?<![\w.$\\/])@?([a-z_][a-z0-9_.]*)\((?!\?)", code):
                    called.setdefault(n, set()).add(f)
                if code != "digit" and re.search(r"(?<![\w.$\\])digit\b(?!s)", code):   # `digit` alone: prose
                    bare_digit.append("%s:%d" % (f, k))
    BINDINGS = {"pair", "m", "f", "repeat", "capture", "x", "date_in", "m.x", "year", "padded"}   # bound in the line
    PARKED = {"cartesian", "example", "options"}    # parked.md placeholders: `@options(...)`, `example(g & ..)`
    CALLED_EXAMPLE_ONLY = {"days", "weekday_of", "days_in", "luhn", "lex_ge", "all_matches", "concat", "unpad",
                           "check", "search"}
    def known(n):
        return n in names or n.split(".")[-1] in names or any(x.endswith("." + n) for x in names)
    missing = sorted(n for n in called if not known(n) and n not in BINDINGS | PARKED | CALLED_EXAMPLE_ONLY)
    listed = sorted(n for n in called if n in CALLED_EXAMPLE_ONLY | PARKED and not known(n))
    check("R3", not missing and "join" in called and not bare_digit,
          "%d names called in the base files; without a library piece: %s; the listed exceptions found: %s; "
          "bare `digit` in a code span at %s" % (len(called), missing, listed, bare_digit))


def part_DOC():
    text = doc("core.md") + doc("library.md")
    if sab("s9"):
        text = text.replace("WHOLE `1234` FAILS", "WHOLE `1234` fails", 1)
    missing = [(k, v) for k, v in LINES.items() if v not in text]
    check("DOC", not missing, "%d example lines, each verbatim in core.md or library.md; missing %s"
          % (len(LINES), missing))


def main():
    part_TV(); part_CF(); part_CP(); part_MN(); part_EX(); part_DG(); part_CG(); part_EV(); part_R3()
    if os.environ.get("PREDDOC6_LINES"):
        for k, v in LINES.items():
            print("LINE", k, v)
    part_DOC()
    print("checks %d, failed %d%s" % (len(CHECKS), len(FAILED), (": " + " ".join(FAILED)) if FAILED else ""))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
