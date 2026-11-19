#!/usr/bin/env python3
# Lane preddoc1 (2026-11-19): the evidence of the PILOT of the reorganized predicate documents: every example line
# of the FULL section core/holes (docs/design/predicates.md), and the manager's readings 1-12 of the lane's brief.
# DESIGN EVIDENCE ONLY; rules nothing.
#
# CONTROLS: libpcre2-8 through ../rxmodel_evidence/pcre2h.py (run, never read: D181); python `re`.  A hole is
# EXPANDED by the small RULE-AS-CODE functions below (named so) into a PCRE pattern; every example is then run on BOTH
# engines and the two answers must agree (python `re` cannot run callouts: those rows are libpcre2 only, said so).
#
# PARTS (the piece or reading each feeds):
#   EX   one example per full holes piece, WHOLE / SEARCHED / FIND-ALL.
#   R1   class-hole alternation = one class (non-negated), capture before it, every mode; the COPY reading differs.
#   R2   two holes in one class: the alternation over every combination; order unobservable (non-negated).
#   R3   zero values / every member removed in a class hole: the never-matching rx (the draft's `[x]` differs).
#   R4   a range WRITTEN out of order: libpcre2 refuses it (the removal is for alternation members only).
#   R5   one value of several characters; class-special characters literal (the text paste differs).
#   R6   `[${join(c)}]` = `[${c}]` non-negated; `[^${c}]`, two different values, accepts every character.
#   R7   the option hole: the inline option letters libpcre2 accepts; `(?)`.
#   R8   zero-in-sequence and number-names one rule: a condition LAST in a sequence = `A & (0: S)`.
#   R9   in a loop the match so far includes the earlier passes (callout start vs the pass's start).
#   R10  a bare condition in a hole: the surrounding labels vs the inserted part's own namespace.
#   R11  a binding whose body is a bare condition, used in a hole, against the record's printed answers.
#   R12  `A & (0: digit & (b: blah))` = `A & (0: digit) & (b: blah)`, every mode.
#   LT   R1 of the rulings file: every `rulings:` title the lint cannot find is a two-line bold opener.
#
# Run (W = the worktree; any cwd; seconds):
#   timeout 600 python3 -I -B W/docs/dev/lanes/preddoc1_evidence/preddoc1_model.py > fwd.out
#   PREDDOC1_SABOTAGE=sN (or =all): one deliberately wrong rule per check; each must make its check FAIL.
#     s1 R1:   the class hole lowered as COPIES of the literal (not an alternation of the class)
#     s2 R2:   the two-hole class lowered with the union class of the FIRST hole only
#     s3 R3:   zero values in a class hole read as the draft's `[x]`
#     s4 R4:   a written out-of-order range accepted (reversed silently)
#     s5 R5:   a value pasted as class TEXT (not escaped)
#     s6 R6:   `[^${c}]` lowered as ONE negated class
#     s7 R7:   the empty option value written as `(?)` text and compared with the no-group pattern by TEXT
#     s8 R8:   the sequenced condition reads the match so far from the condition's own start (empty)
#     s9 R9:   the match so far restarted at the pass's start
#     s10 R10: the bare condition reads the inserted part's namespace (h unset there)
#     s11 R12: the inner `(b: ..)` judged on a re-match of `digit` (its own world)
#     s12 EX:  the flags hole lowered WITHOUT inheritance (`(?-i:...)`)
#     s13 EX:  a count copy that is illegal kept as PCRE text instead of removed
#     s14 LT:  a typo planted in one cited title (the class check must then fail)
#     s15 R11: the binding judged as its own rx (an empty match so far)
#     x<EX-tag>: the example's RIVAL reading (the candidate not taken) run in place; its EX check must fail
import os, sys, re, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rxmodel_evidence"))
import pcre2h as P                                           # noqa: E402

SAB = set(x for x in os.environ.get("PREDDOC1_SABOTAGE", "").split(",") if x)
def sab(n): return "all" in SAB or n in SAB

RESULTS = []
def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print("  CHECK %-6s %s%s" % (name, "PASS" if ok else "FAIL", ("  " + detail) if detail else ""))

# ------------------------------------------------------------------ the three modes, both engines
def to_py(pat):
    """The same pattern in python `re` spelling: `\\k<n>` -> `(?P=n)`; a branch reset `(?|` holding no group -> `(?:`."""
    p = re.sub(r"\\k<(\w+)>", r"(?P=\1)", pat).replace("(?|", "(?:")
    p = re.sub(r"\(\?<(\w)", r"(?P<\1", p)
    # python has no `U`; a `-U` (turning off what is off) is dropped. A pattern that turns `U` ON is libpcre2-only.
    if re.search(r"\(\?[a-z]*U", p): raise ValueError("U on: libpcre2 only")
    return re.sub(r"\(\?([ims]*)-([ims]*)U:", lambda m: "(?%s%s:" % (m.group(1), ("-" + m.group(2)) if m.group(2) else ""), p)

def py_modes(pat, whole, srch, fa, flags=0):
    r = re.compile(to_py(pat), flags)
    w = [(s, bool(r.fullmatch(s))) for s in whole]
    m = r.search(srch)
    se = (m.group(0), m.start()) if m else None
    out, pos = [], 0
    while pos <= len(fa):
        m = r.search(fa, pos)
        if not m: break
        out.append((m.group(0), m.start()))
        pos = m.end() if m.end() > m.start() else m.end() + 1
    return w, se, out

def pc_modes(pat, whole, srch, fa, callouts=None):
    r = P.Pcre(pat, callouts)
    w = [(s, r.whole(s)) for s in whole]
    m = r.search(srch)
    se = (srch[m[0]:m[1]], m[0]) if m else None
    out = [(fa[a:b], a) for a, b, _ in r.findall(fa)]
    return w, se, out

def fmt(res, srch, fa):
    w, se, out = res
    ws = ", ".join("`%s` %s" % (s, "HOLDS" if h else "FAILS") for s, h in w)
    ss = ("`%s`@%d" % se) if se else "nothing"
    fs = "[" + ", ".join("`%s`@%d" % x for x in out) + "]"
    return "WHOLE %s / SEARCHED `%s` %s / FIND-ALL `%s` %s" % (ws, srch, ss, fa, fs)

def example(tag, program, pat, whole, srch, fa, callouts=None, py=True, rival=None):
    """rival = (pattern, callouts) of the reading NOT taken; PREDDOC1_SABOTAGE=x<tag> runs it in place (must FAIL)."""
    if rival is not None and sab("x" + tag):
        pat, callouts = rival[0], (rival[1] if len(rival) > 1 else callouts)
    pc = pc_modes(pat, whole, srch, fa, callouts)
    line = fmt(pc, srch, fa)
    agree = True
    if py:
        agree = py_modes(pat, whole, srch, fa) == pc
    print("%s  %s  ==  %s\n    %s%s" % (tag, program, pat, line, "" if py else "   (libpcre2 only)"))
    return pc, agree

def texts(alpha, n):
    for L in range(n + 1):
        for t in itertools.product(alpha, repeat=L):
            yield "".join(t)

def diff3(a, b, ts, labels=()):
    """WHOLE / SEARCHED / FIND-ALL differences of two python patterns over texts (span + named groups)."""
    ra, rb = re.compile(to_py(a)), re.compile(to_py(b))
    def key(m): return None if m is None else (m.span(),) + tuple(m.group(g) for g in labels)
    def fa(r, s): return [key(m) for m in r.finditer(s)]
    d = [0, 0, 0]; n = 0; first = None
    for s in ts:
        n += 1
        x = (bool(ra.fullmatch(s)) != bool(rb.fullmatch(s)),
             key(ra.search(s)) != key(rb.search(s)), fa(ra, s) != fa(rb, s))
        for i in range(3): d[i] += x[i]
        if any(x) and first is None: first = s
    return d, n, first

# ------------------------------------------------------------------ RULE-AS-CODE: the hole positions
def cls_esc(v):
    """A hole VALUE in a class is TEXT: every character a literal member (reading 5)."""
    if sab("s5"): return v
    return "".join("\\" + c if c in "\\]^-[" else c for c in v)

def class_hole(before, values, after, neg=False):
    """`[before${c}after]`, c := values: an ALTERNATION OF THE CLASS, one class per value (other-holes (1))."""
    if not values: return "(?!)" if not sab("s3") else "[%s%s%s]" % ("^" if neg else "", before, after)
    if neg and sab("s6"): return "[^%s%s%s]" % (before, "".join(cls_esc(v) for v in values), after)
    return "(?:" + "|".join("[%s%s%s%s]" % ("^" if neg else "", before, cls_esc(v), after) for v in values) + ")"

def range_hole(los, his):
    """`[${lo}-${hi}]`: the alternation over every combination, first hole slowest; an out-of-order member REMOVED."""
    mem = ["[%s-%s]" % (cls_esc(a), cls_esc(b)) for a in los for b in his if a <= b]
    return "(?:" + "|".join(mem) + ")" if mem else "(?!)"

def count_copies(lit, holes):
    """A COUNT hole: one copy of the literal per combination (first hole slowest), an illegal copy REMOVED; copies in a
    branch-reset group `(?|...)` so they share group numbers (the draft's reading)."""
    names = list(holes)
    out = []
    for combo in itertools.product(*[holes[k] for k in names]):
        env = dict(zip(names, combo))
        mn, mx = env.get("min"), env.get("max")
        if mn is not None and mx is not None and mn > mx and not sab("s13"): continue
        out.append(lit.format(**env))
    return "(?|" + "|".join(out) + ")" if out else "(?!)"

LEGAL_OPTIONS = ["i", "m", "s", "x", "xx", "n", "U", "J", "r", "a", "aD", "aS", "aW", "aP", "aT"]
def option_hole(values, body):
    """The OPTION hole: exactly one value, from the legal set, or the empty string (no option group)."""
    if len(values) != 1: raise ValueError("option hole: not exactly one value (a compile error)")
    v = values[0]
    if v == "": return body if not sab("s7") else "(?)" + body
    if v not in LEGAL_OPTIONS: raise ValueError("option hole: %r outside the legal set (a compile error)" % v)
    return "(?%s)%s" % (v, body)

def flags_hole(outer_flags, inner):
    """A hole inherits i, m, s from the flags in force at it (flags-scope); not U, x, xx, n; written flags win."""
    inh = "".join(f for f in outer_flags if f in "ims")
    if sab("s12"): inh = ""
    off = "".join(f for f in "ims" if f not in inh) + "U"
    return "(?%s-%s:%s)" % (inh, off, inner)

# ------------------------------------------------------------------ PART EX
print("== PART EX: one example per full core/holes piece (libpcre2 answers; python `re` must agree)")

pc, ok = example("EX-pattern", "/${/ab/}?c/", r"(?:ab)?c", ["ac", "abc"], "bc", "c abc ac", rival=("ab?c",))
check("EXpat", ok and pc == ([("ac", False), ("abc", True)], ("c", 1), [("c", 0), ("abc", 2), ("c", 7)]))
pc, ok = example("EX-pattern-array", "/x${[/a/, /ab/]}y/", r"x(?:a|ab)y", ["xay", "xaby"], "-xaby", "xay xaby", rival=("xay",))
check("EXarr", ok and pc[0] == [("xay", True), ("xaby", True)])

p = count_copies(r"\d{{{min},{max}}}", {"min": [2, 4], "max": [2, 4]})
pc, ok = example("EX-count", "rx.repeat(rx.digit, min = n, max = n), n := [2, 4]", p, ["123", "1"], "12345", "12345 6")
check("EXcnt", ok and p == r"(?|\d{2,2}|\d{2,4}|\d{4,4})" and pc[2] == [("12", 0), ("34", 2)])
pc, ok = example("EX-count-zero", "/xa{${n}}y/, n := 0", r"xa{0}y", ["xy", "xay"], "-xy xaby", "xy xay xy", rival=("x(?!)y",))
check("EXcz", ok and pc[0] == [("xy", True), ("xay", False)])

def name_hole(values):
    """A GROUP-NAME hole: exactly one name; an array is a compile error (name-hole)."""
    if len(values) != 1 and not sab("xEX-name"): raise ValueError("name hole: an array of names (a compile error)")
    return values[0]
pc, ok = example("EX-name", "/(?<${n}>\\d)x/, n := \"d\"", r"(?<%s>\d)x" % name_hole(["d"]), ["7x", "x"], "a7x", "7x 8x")
try: name_hole(["a", "b"]); nerr = False
except ValueError as e: nerr = True; print("    name hole [a, b]: %s" % e)
check("EXname", ok and pc[0] == [("7x", True), ("x", False)] and nerr)

p = "a" + class_hole("", ["x", "y"], "q")
pc, ok = example("EX-class", "/a[${c}q]/, c := [x, y]", p, ["ax", "ay", "aq", "ab"], "-ab ay", "ax ab aq", rival=("a[xq]",))
check("EXcls", ok and pc == ([("ax", True), ("ay", True), ("aq", True), ("ab", False)], ("ay", 4), [("ax", 0), ("aq", 6)]))

p = "a(?:" + "|".join("[%s%s]" % (x, y) for x in "xy" for y in "pq") + ")"
pc, ok = example("EX-two-holes", "/a[${a}${b}]/, a := [x, y], b := [p, q]", p, ["ap", "ab"], "-ab aq", "ax ab ap",
                 rival=("a(?:[xp]|[xq])",))
check("EX2h", ok and pc == ([("ap", True), ("ab", False)], ("aq", 4), [("ax", 0), ("ap", 6)]))
p = "a" + class_hole("", [], "x") + "|b"
pc, ok = example("EX-zero-values", "/a[${[]}x]|b/", p, ["ax", "b"], "axb", "ax b")
check("EX0v", ok and pc == ([("ax", False), ("b", True)], ("b", 2), [("b", 3)]))

p1, p2 = "a" + class_hole("", ["xy"], "", neg=True), "a" + class_hole("", ["x", "y"], "", neg=True)
pc, ok = example("EX-negated-join", "/a[^${join(c)}]/, c := [x, y]", p1, ["ax", "ay", "ab"], "ax ab", "ax ay ab")
pc2, ok2 = example("EX-negated-array", "/a[^${c}]/, c := [x, y]", p2, ["ax", "ay", "ab"], "ax ab", "ax ay ab")
check("EXneg", ok and ok2 and pc[2] == [("ab", 6)] and pc2[2] == [("ax", 0), ("ay", 3), ("ab", 6)])

p = range_hole(["a", "x"], ["m"])
pc, ok = example("EX-range", "/[${lo}-m]/, lo := [a, x] (x-m removed)", p, ["b", "x", "n"], "-xb", "b x n a", rival=("(?:[a-m]|[m-x])",))
check("EXrng", ok and p == "(?:[a-m])" and pc[2] == [("b", 0), ("a", 6)])

pc, ok = example("EX-option", "/(?${o})ab/, o := \"i\"", option_hole(["i"], "ab"), ["AB", "ab"], "x AB", "ab AB Ab")
pc2, ok2 = example("EX-option-empty", "/(?${o})ab/, o := \"\"", option_hole([""], "ab"), ["AB", "ab"], "x AB ab", "ab AB")
errs = []
for vals in (["i", "s"], [], ["q"]):
    try: option_hole(vals, "ab"); errs.append(False)
    except ValueError as e: errs.append(True); print("    option hole %r: %s" % (vals, e))
check("EXopt", ok and ok2 and pc[2] == [("ab", 0), ("AB", 3), ("Ab", 6)] and pc2[1] == ("ab", 5) and all(errs)
      and option_hole([""], "ab") == "ab")

pc, ok = example("EX-value", "/(?<y>\\d)-${$y | \"x\"}/", r"(?<y>\d)-(?:\k<y>|x)", ["3-x", "3-3", "3-4"], "7-3 3-3",
                 "3-3 4-x 5-6 7-7", rival=(r"(?<y>\d)-(?:x)",))
check("EXval", ok and pc[2] == [("3-3", 0), ("4-x", 4), ("7-7", 12)])
pc, ok = example("EX-value-unset", "/(?<y>\\d)?-${$y | \"x\"}/ (unset read: the never-matching rx)",
                 r"(?<y>\d)?-(?:(?(y)\k<y>|(?!))|x)", ["-x", "-", "3-3"], "a-x", "-x 3-3 -", rival=(r"(?<y>\d)?-(?:(?(y)\k<y>|)|x)",))
check("EXuns", ok and pc[0] == [("-x", True), ("-", False), ("3-3", True)])

def at_stretch(S):
    rx = re.compile(S)
    return lambda c: bool(rx.fullmatch(c.stretch()))
pc, ok = example("EX-bare-condition", "/\\d${(0: digit)}x/", r'\d(?C"z")x', ["7x", "77x"], "a7x", "7x 12x 8x",
                 {"z": at_stretch(r"\d")}, py=False, rival=(r'\dx(?C"z")',))
check("EXbare", pc == ([("7x", True), ("77x", False)], ("7x", 1), [("7x", 0), ("2x", 4), ("8x", 7)]))
pc, ok = example("EX-bare-and", "/x${A & (0: digit)}y/, A := /\\d+/  (0 = A only)", r'x(?<A>\d+)(?C"a")y',
                 ["x3y", "x37y"], "x37y x3y", "x3y x37y x5y",
                 {"a": lambda c: bool(re.fullmatch(r"\d", c.get("A") or "x"))}, py=False,
                 rival=(r'x(?<A>\d+)(?C"a")y', {"a": lambda c: bool(re.fullmatch(r"\d", c.stretch()))}))
check("EXand", pc == ([("x3y", True), ("x37y", False)], ("x3y", 5), [("x3y", 0), ("x5y", 9)]))

p = "(?i)id-" + flags_hole("i", "blah")
pc, ok = example("EX-flags", "/(?i)id-${/blah/}/", p, ["id-BLAH", "ID-blah"], "x ID-BLAH", "id-blah ID-BLAH Id-blah")
check("EXflg", ok and pc[0] == [("id-BLAH", True), ("ID-blah", True)])
p = "(?i)id-" + flags_hole("i", "(?-i:blah)")  # the literal's leading (?-i) spelt scoped, for python
pc, ok = example("EX-flags-written", "/(?i)id-${/(?-i)blah/}/", p, ["id-BLAH", "ID-blah"], "x ID-BLAH id-blah",
                 "id-blah ID-BLAH", rival=("(?i)id-(?:blah)",))
check("EXflw", ok and pc[0] == [("id-BLAH", False), ("ID-blah", True)])
p = "(?U)x" + flags_hole("U", "a+")
pc, ok = example("EX-flags-U", "/(?U)x${/a+/}/  (U not inherited)", p, ["xaaa"], "xaaa", "xaa xa", py=False, rival=("(?U)x(?:a+)",))
pcu = pc_modes("(?U)x(?:a+)", ["xaaa"], "xaaa", "xaa xa")
print("    the text paste `(?U)x(?:a+)` (U reaching the hole): %s" % fmt(pcu, "xaaa", "xaa xa"))
check("EXflU", pc[1] == ("xaaa", 0) and pcu[1] == ("xa", 0))

pc, ok = example("EX-labels", "/${year}-x/ & (v: >= 2000), year := /(?<v>\\d{4})/", r'(?<v>\d{4})-x(?C"v")',
                 ["2025-x", "1999-x"], "1999-x 2025-x", "2025-x 1999-x 2001-x",
                 {"v": lambda c: int(c.get("v")) >= 2000}, py=False,
                 rival=(r'(?<v>\d{4})-x(?C"v")', {"v": lambda c: False}))
check("EXlab", pc == ([("2025-x", True), ("1999-x", False)], ("2025-x", 7), [("2025-x", 0), ("2001-x", 14)]))

pc, ok = example("EX-same-name", "/(?<h>a)-${q}\\k<h>/, q := /(?<h>b)/  (the inner group renamed: scoped)",
                 r"(?<h>a)-(?:(?<h_q>b))\k<h>", ["a-ba", "a-bb"], "x a-bb a-ba", "a-ba a-bb a-ba",
                 rival=(r"(?<h1>a)-(?:(?<h>b))\k<h>",))
check("EXsnm", ok and pc == ([("a-ba", True), ("a-bb", False)], ("a-ba", 7), [("a-ba", 0), ("a-ba", 10)]))

pc, ok = example("EX-in-filter", "/\\d+/ & /${/[1-5]+/}/  (holes filled, then the operand judged)", r'\d+(?C"q")',
                 ["123", "1239"], "x9 34", "12 9 45 7", {"q": at_stretch(r"[1-5]+")}, py=False,
                 rival=(r'\d+(?C"q")', {"q": lambda c: bool(re.match(r"[1-5]+", c.stretch()))}))
check("EXflt", pc == ([("123", True), ("1239", False)], ("34", 3), [("12", 0), ("45", 5)]))

r = P.Pcre(r"a\Q${x}\Eb" if not sab("xEX-quoted") else r"a(?:x)b")
nq = [r.whole("a${x}b"), r.whole("ab")]
print("EX-quoted  /a\\Q${x}\\Eb/ (no hole inside \\Q..\\E: literal text)\n    WHOLE `a${x}b` %s, `ab` %s / SEARCHED `-a${x}b` %s / FIND-ALL `a${x}b a${x}b` %s"
      % ("HOLDS" if nq[0] else "FAILS", "HOLDS" if nq[1] else "FAILS", r.search("-a${x}b")[:2],
         [x[:2] for x in r.findall("a${x}b a${x}b")]))
check("EXq", nq == [True, False])

# ------------------------------------------------------------------ R1
print("\n== PART R1: a class-hole alternation is of the CLASS (no copies); non-negated it collapses to one class")
T = list(texts("xya-", 4))
alt = r"(?<g>\w*)" + class_hole("", ["x", "y"], "")
uni = r"(?<g>\w*)[xy]"
d, n, f = diff3(alt, uni, T, ("g",))
print("  alternation %s vs one class %s: %s of %d (WHOLE / SEARCHED / FIND-ALL, span + g)" % (alt, uni, d, n))
cp = r"(?:(?<g>\w*)[x]|(?<h>\w*)[y])"
d2, n2, f2 = diff3(cp, uni, T)
print("  the COPY reading (one copy of the literal per value) %s vs one class: %s of %d, first `%s`" % (cp, d2, n2, f2))
tq = list(texts("xyq-", 4))
d3, n3, _ = diff3(class_hole("", ["x", "y"], "q"), "[xyq]", tq)
print("  `[${c}q]` vs `[xyq]`: %s of %d" % (d3, n3))
if sab("s1"): d = d2
check("R1", d == [0, 0, 0] and d3 == [0, 0, 0] and d2 != [0, 0, 0])

# ------------------------------------------------------------------ R2
print("\n== PART R2: two holes in one class: the alternation over every combination (first hole slowest)")
def two_hole(a, b, order="slow"):
    combos = [(x, y) for x in a for y in b] if order == "slow" else [(x, y) for y in b for x in a]
    if sab("s2"): return "[" + "".join(a) + "]"
    return "(?:" + "|".join("[%s%s]" % (cls_esc(x), cls_esc(y)) for x, y in combos) + ")"
TT = list(texts("xypq-", 4))
pa = r"(?<g>\w*)" + two_hole(["x", "y"], ["p", "q"])
d, n, f = diff3(pa, r"(?<g>\w*)[xypq]", TT, ("g",))
db, _, _ = diff3(pa, r"(?<g>\w*)" + two_hole(["x", "y"], ["p", "q"], "fast"), TT, ("g",))
print("  `[${a}${b}]`, a := [x, y], b := [p, q]: %s vs `[xypq]` %s of %d; first-slowest vs first-fastest %s" % (pa, d, n, db))
pr = r"(?<g>\w*)" + range_hole(["a", "c"], ["e", "b"])
dr, nr, _ = diff3(pr, r"(?<g>\w*)[a-e]", list(texts("abcdef-", 3)), ("g",))
print("  `[${lo}-${hi}]`, lo := [a, c], hi := [e, b]: %s (c-b removed) vs `[a-e]` %s of %d" % (pr, dr, nr))
check("R2", d == [0, 0, 0] and db == [0, 0, 0] and dr == [0, 0, 0])

# ------------------------------------------------------------------ R3
print("\n== PART R3: zero values (or every member removed) in a class hole: the never-matching rx")
z = class_hole("", [], "x")
d, n, f = diff3("a" + z + "|b", "a(?!)|b", list(texts("axb", 3)))
dd, _, ff = diff3("a" + z + "|b", "a[x]|b", list(texts("axb", 3)))
allrem = range_hole(["x", "z"], ["a"])
print("  `/a[${[]}x]|b/` = %s: vs `a(?!)|b` %s of %d; vs the draft's `[x]` reading %s (first `%s`); `[${lo}-a]`, lo := [x, z]: %s"
      % ("a" + z + "|b", d, n, dd, ff, allrem))
check("R3", d == [0, 0, 0] and dd != [0, 0, 0] and allrem == "(?!)")

# ------------------------------------------------------------------ R4
print("\n== PART R4: a range WRITTEN with single values out of order is a compile error (libpcre2)")
try:
    P.Pcre("[z-a]" if not sab("s4") else "[a-z]"); r4 = "compiles"
except ValueError as e:
    r4 = "ERROR: %s" % e
print("  `[z-a]`: %s;  the alternation member `[x-m]` of `[${lo}-m]`, lo := [a, x]: removed -> %s" % (r4, range_hole(["a", "x"], ["m"])))
check("R4", r4.startswith("ERROR"))

# ------------------------------------------------------------------ R5
print("\n== PART R5: one value may hold several characters; class-special characters in a value are literal members")
rows = []
for v, probe in (("xy", "y"), ("^a", "^"), ("a-c", "b"), ("]", "]"), ("\\d", "7")):
    esc = "[" + cls_esc(v) + "]"; paste = "[" + v + "]"
    try:
        pe = P.Pcre(esc); e_ok = [pe.whole(ch) for ch in sorted(set(v))]; e_probe = pe.whole(probe)
    except ValueError as e:
        e_ok, e_probe = ["ERR"], str(e)
    try:
        pp = P.Pcre(paste); p_probe = pp.whole(probe)
    except ValueError as e:
        p_probe = "compile error"
    rows.append((v, esc, all(x is True for x in e_ok), e_probe, p_probe))
    print("  value %-5r -> %-9s every character of the value a member: %s; `%s` %s (the text paste %-9s: %s)"
          % (v, esc, all(x is True for x in e_ok), probe, "HOLDS" if e_probe is True else "FAILS" if e_probe is False else e_probe,
             paste, "HOLDS" if p_probe is True else "FAILS" if p_probe is False else p_probe))
want = {"xy": True, "^a": True, "a-c": False, "]": True, "\\d": False}
check("R5", all(r[2] for r in rows) and all((r[3] is True) == want[r[0]] for r in rows if r[0] != "xy")
      and any(r[3] != r[4] for r in rows))

# ------------------------------------------------------------------ R6
print("\n== PART R6: `[${join(c)}]` = `[${c}]` (non-negated); `[^${c}]`, two different values, accepts every character")
d, n, _ = diff3("a" + class_hole("", ["xy"], ""), "a" + class_hole("", ["x", "y"], ""), list(texts("axyb", 4)))
neg = re.compile("a" + class_hole("", ["x", "y"], "", neg=True))
acc = sum(1 for o in range(0, 0x250) if neg.fullmatch("a" + chr(o)))
print("  `a[${join(c)}]` vs `a[${c}]`, c := [x, y]: %s of %d;  `a[^${c}]` accepts %d of %d characters U+0000..U+024F"
      % (d, n, acc, 0x250))
check("R6", d == [0, 0, 0] and acc == 0x250)

# ------------------------------------------------------------------ R7
print("\n== PART R7: the option hole's legal set (the letters the draft admits), each through libpcre2; and `(?)`")
print("  libpcre2 version %s" % P.version())
legal = []
for o in LEGAL_OPTIONS + ["", "^"]:
    try: P.Pcre("(?%s)ab" % o); legal.append((o, True))
    except ValueError as e: legal.append((o, False))
for o in ("B", "u", "X", "q"):
    try: P.Pcre("(?%s)ab" % o); legal.append((o, True))
    except ValueError: legal.append((o, False))
print("  " + "  ".join("(?%s)%s" % (o, "ok" if k else "ERR") for o, k in legal))
e = P.Pcre("(?)ab"); ne = P.Pcre(option_hole([""], "ab"))
T7 = ["ab", "AB", "xab", "aB"]
same = all((e.whole(s), e.search(s) and e.search(s)[:2]) == (ne.whole(s), ne.search(s) and ne.search(s)[:2]) for s in T7)
txt_same = option_hole([""], "ab") == "ab"
print("  PCRE accepts a written `(?)`: %s; the empty value gives `%s`; `(?)ab` and `ab` answer alike on %s: %s"
      % (dict(legal)[""], option_hole([""], "ab"), T7, same))
check("R7", all(k for o, k in legal if o in LEGAL_OPTIONS) and not any(k for o, k in legal if o in ("B", "u", "X", "q"))
      and same and txt_same)

# ------------------------------------------------------------------ R8
print("\n== PART R8: `0` in a condition LAST in a sequence (the match so far) = `A & (0: S)` (the entire match)")
def seq_last(A, S):
    rx = re.compile(S)
    if sab("s8"): return P.Pcre(A + '(?C"z")', {"z": lambda c: bool(rx.fullmatch(c.subject[c.pos:c.pos]))})
    return P.Pcre(A + '(?C"z")', {"z": lambda c: bool(rx.fullmatch(c.stretch()))})
def amp_filter_py(A, S):
    """An independent FILTER model: every path of A's pattern tried from each start in PCRE order (python `re` with
    the end pinned), the first whose whole stretch S matches."""
    ra, rs = re.compile(A), re.compile(S)
    def at(s, i, end=None):
        ends = [end] if end is not None else range(len(s), i - 1, -1)
        for e in ends:
            m = ra.fullmatch(s, i, e)
            if m and rs.fullmatch(s[i:e]): return (i, e)
        return None
    return at
tot = [0, 0, 0]; n = 0
for A, S in ((r"\d+", r"7\d?"), (r"\d\d?", r"[0-4]+"), (r"[37]*", r"3*")):
    pc = seq_last(A, S); at = amp_filter_py(A, S)
    for s in texts("37x", 4):
        n += 1
        w = pc.whole(s) != (at(s, 0, len(s)) is not None)
        m = pc.search(s); mm = None
        for i in range(len(s) + 1):
            mm = at(s, i)
            if mm: break
        se = (m[:2] if m else None) != mm
        tot[0] += w; tot[1] += se
print("  three (A, S) pairs (greedy A, so a filter's first path is its longest that passes): %s WHOLE/SEARCHED of %d" % (tot[:2], n))
print("  NOTE the filter model is greedy-longest-first only for these A; the callout (match so far at the end) is PCRE's path order.")
mid = P.Pcre(r'\d(?C"z")\d', {"z": lambda c: bool(re.fullmatch("7", c.stretch()))})
print("  mid-sequence `digit SEQ (0: /7/) SEQ digit`: WHOLE `73` %s, `37` %s / SEARCHED `373` %s / FIND-ALL `73 77 37` %s"
      % (mid.whole("73"), mid.whole("37"), mid.search("373")[:2], [x[:2] for x in mid.findall("73 77 37")]))
check("R8", tot[:2] == [0, 0] and mid.whole("73") and not mid.whole("37"))

# ------------------------------------------------------------------ R9
print("\n== PART R9: inside a loop the match so far includes the earlier passes")
def loop_prog(from_pass):
    def z(c):
        st = c.stretch()
        if from_pass or (sab("s9") and not from_pass): st = st.split(";")[-1]
        return bool(re.fullmatch(r"\d", st))
    return P.Pcre(r'(?:\d(?C"z");)*', {"z": z})
a, b = loop_prog(False), loop_prog(True)
dd = [0, 0, 0]; n = 0; first = None
for s in texts("37;", 5):
    n += 1
    x = (a.whole(s) != b.whole(s), (a.search(s) or (0, 0))[:2] != (b.search(s) or (0, 0))[:2],
         [y[:2] for y in a.findall(s)] != [y[:2] for y in b.findall(s)])
    for i in range(3): dd[i] += x[i]
    if any(x) and first is None: first = s
print("  `(digit SEQ (0: digit) SEQ \";\")*` (digit one character, so a match so far longer than one pass fails):")
print("  from the rx's start (the callout's start) vs from the pass's start: %s of %d; first `%s`: %s vs %s"
      % (dd, n, first, a.whole(first), b.whole(first)))
check("R9", dd[0] > 0 and a.whole("3;") and not a.whole("3;7;") and b.whole("3;7;"))

# ------------------------------------------------------------------ R10
print("\n== PART R10: a bare condition in a hole: the SURROUNDING labels at the hole, or the inserted part's own namespace")
def bare_labels(own_ns):
    def t(c):
        h = None if (own_ns or sab("s10")) else c.get("h")
        if h is None: raise ValueError("compile error: `h` is not a name of the inserted part (free-name)")
        return int(h) < 5
    return t
sur = P.Pcre(r'(?<h>\d)(?C"t")x', {"t": bare_labels(False)})
res = (sur.whole("3x"), sur.whole("7x"), sur.search("7x 3x")[:2], [y[:2] for y in sur.findall("3x 7x 4x")])
print("  `/(?<h>\\d)${(h: <5)}x/` SURROUNDING reading: WHOLE `3x` %s, `7x` %s / SEARCHED `7x 3x` %s / FIND-ALL `3x 7x 4x` %s" % res)
try:
    own = P.Pcre(r'(?<h>\d)(?C"t")x', {"t": bare_labels(True)}); own.whole("3x"); own_res = "answers"
except ValueError as e:
    own_res = str(e)
print("  OWN-NAMESPACE reading (the place table's hole row, \"inside X, X's own namespace\"): %s" % own_res)
print("  the two readings PART (an answer against a compile error): an OWNER QUESTION, bare-condition-labels")
check("R10", res[0] is True and res[1] is False and own_res.startswith("compile error"))

# ------------------------------------------------------------------ R11
print("\n== PART R11: c := (0: digit) used as `/\\d${c}x/` against the record's printed answers for `/\\d${(0: digit)}x/`")
bind = P.Pcre(r'\d(?C"c")x', {"c": at_stretch(r"\d") if not sab("s15") else (lambda c: bool(re.fullmatch(r"\d", "")))})
got = (bind.whole("7x"), bind.whole("77x"), bind.search("a7x")[:2], [y[:2] for y in bind.findall("7x 12x 8x")])
rec = (True, False, (1, 3), [(0, 2), (4, 6), (7, 9)])
alone = P.Pcre(r'(?C"c")', {"c": at_stretch(r"\d")})
print("  binding-in-hole: %s ; the record's (zero-in-sequence entry `0` inside an inserted part): %s ; equal: %s" % (got, rec, got == rec))
print("  the rival (the binding judged as its own rx, an empty match so far): `7x` %s" % (P.Pcre(r'\d(?C"c")x', {"c": lambda c: bool(re.fullmatch(r"\d", ""))}).whole("7x")))
check("R11", got == rec)

# ------------------------------------------------------------------ R12
print("\n== PART R12: `A & (0: digit & (b: blah))` = `A & (0: digit) & (b: blah)`, A := /(?<b>\\d)\\d*x?/, digit := /\\d+/, blah := /[0-4]/")
A = r"(?<b>\d)\d*x?"
def one(c):
    st = c.stretch()
    if sab("s11"):
        m = re.match(r"(?<b>\d)", st); b = m.group("b") if m else None; b = "9" if b else None
    else:
        b = c.get("b")
    return bool(re.fullmatch(r"\d+", st)) and b is not None and bool(re.fullmatch(r"[0-4]", b))
X = P.Pcre(A + '(?C"one")', {"one": one})
Y = P.Pcre(A + '(?C"d")(?C"b")', {"d": lambda c: bool(re.fullmatch(r"\d+", c.stretch())),
                                   "b": lambda c: bool(re.fullmatch(r"[0-4]", c.get("b") or "z"))})
dd = [0, 0, 0]; n = 0
for s in texts("27x", 5):
    n += 1
    dd[0] += X.whole(s) != Y.whole(s)
    dd[1] += (X.search(s) or (0, 0, {}))[:3] != (Y.search(s) or (0, 0, {}))[:3]
    dd[2] += [y for y in X.findall(s)] != [y for y in Y.findall(s)]
print("  the nested set vs the chain: %s of %d (span + b); e.g. WHOLE `27` %s, `72` %s / SEARCHED `x72 23` %s / FIND-ALL `2x 27 7 3` %s"
      % (dd, n, X.whole("27"), X.whole("72"), X.search("x72 23")[:2], [y[:2] for y in X.findall("2x 27 7 3")]))
print("  after a NAMED label (`A & (h: digit & (b: blah))`): b is not a label of h's world: the draft's existing error (not runnable)")
check("R12", dd == [0, 0, 0])

# ------------------------------------------------------------------ LT
print("\n== PART LT: the lint's L4 failures are exactly two lint limits, every title true (rulings file R1)")
# Two classes, predicted here line by line, then compared with the lint's own output:
#  Q  a title holding a `"`: the lint's (record: "[^"]+") cannot hold it -> 'rulings item without (record: ...)';
#  T  a title whose bold opener spans two lines: the lint's record_titles cannot see it -> 'record title ... not found'.
# Every cited title, read up to its closing `")`, must be a TRUE record title (a heading or opener, joined across lines).
import subprocess
W = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
rec_lines = open(os.path.join(W, "docs/design/plan_row_bodies/COND-FAMILY.md"), encoding="utf-8").read().split("\n")
def norm(t): return " ".join(t.split()).rstrip(".")
lint_titles, joined, heads = set(), {}, {}
for i, ln in enumerate(rec_lines):
    full = None
    if ln.startswith("### "): full = ln[4:]
    else:
        m = re.match(r"^\*\*(.+?)\*\*", ln)
        if m: full = m.group(1)
        elif ln.startswith("**20"):
            t, k = ln[2:], i
            while "**" not in t and k + 1 < len(rec_lines): k += 1; t += " " + rec_lines[k]
            j = norm(t.split("**")[0]); joined[j] = i + 1; joined[j.split(" (")[0]] = i + 1
    if full is not None:
        f = norm(full); lint_titles.add(f); lint_titles.add(f.split(" (")[0])
        heads.setdefault(f, i + 1); heads.setdefault(f.split(" (")[0], i + 1)
LINT_RE = re.compile(r'\(record:\s*"([^"]+)"\)')
OUR_RE = re.compile(r'\(record:\s*"(.*?)"\)')
pred, faults, ncited, shown = set(), [], 0, {}
for fn in ("predicates_details.md", "predicates_library_details.md", "predicates_parked_details.md"):
    p = os.path.join(W, "docs/design", fn)
    if not os.path.isfile(p): continue
    inrul = False
    for n, ln in enumerate(open(p, encoding="utf-8"), 1):
        ln = ln.rstrip("\n")
        if ln.startswith("rulings:"): inrul = True; continue
        if not ln.startswith("- "): inrul = False if ln and not ln.startswith(" ") else inrul; continue
        if not inrul: continue
        m = OUR_RE.search(ln)
        if not m: faults.append("%s:%d no (record: ...) at all" % (fn, n)); continue
        t = norm(m.group(1)); ncited += 1
        if sab("s14") and ncited == 1: t += "x"
        if t not in lint_titles and t not in joined: faults.append("%s:%d NOT A RECORD TITLE: %s" % (fn, n, t)); continue
        lm = LINT_RE.search(ln)
        if not lm:
            if '"' not in t: faults.append("%s:%d lint misses a quote-free title: %s" % (fn, n, t)); continue
            pred.add(("Q", fn, n)); shown[t] = ("Q", joined.get(t) or heads.get(t))
        elif norm(lm.group(1)) not in lint_titles:
            if t not in joined: faults.append("%s:%d unseen but not two-line: %s" % (fn, n, t)); continue
            pred.add(("T", fn, n)); shown[t] = ("T", joined[t])
out = subprocess.run([sys.executable, "-I", os.path.join(W, "scripts/pred_doc_lint.py")], cwd=W,
                     capture_output=True, text=True).stdout
got, other = set(), []
for ln in out.splitlines():
    m = re.match(r"^(L\d+) docs/design/(\S+?):(\d+): (.*)$", ln)
    if not m: continue
    rule, fn, n, msg = m.group(1), m.group(2), int(m.group(3)), m.group(4)
    if rule == "L4" and msg.startswith("rulings item without"): got.add(("Q", fn, n))
    elif rule == "L4" and msg.startswith("record title") and "not found" in msg: got.add(("T", fn, n))
    else: other.append(ln)
nq, nt = sum(1 for x in got if x[0] == "Q"), sum(1 for x in got if x[0] == "T")
print("  cited title items %d; lint L4 failures: %d 'not found' (two-line), %d 'without (record:' (a quote in the title)"
      % (ncited, nt, nq))
print("  distinct titles in the two classes: %d" % len(shown))
for t in sorted(shown, key=lambda x: (shown[x][1] or 0)):
    k, ln = shown[t]; print("    %s record line %s: %s" % ("two-line" if k == "T" else "quote   ", ln, t))
print("  quote titles that are also two-line openers: %s" % ", ".join(t for t in shown if shown[t][0] == "Q" and t in joined) )
for f in faults: print("    FAULT: " + f)
for ln in other: print("    OTHER LINT FAILURE: " + ln)
if got != pred:
    print("    predicted, not reported: %s" % sorted(pred - got)); print("    reported, not predicted: %s" % sorted(got - pred))
check("LT", ncited > 0 and not faults and not other and got == pred)

print("\nSUMMARY: %d checks, %d failed: %s" % (len(RESULTS), sum(1 for _, k in RESULTS if not k),
      ", ".join(n for n, k in RESULTS if not k) or "none"))
