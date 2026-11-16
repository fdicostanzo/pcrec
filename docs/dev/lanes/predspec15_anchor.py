# predspec15: evidence for predicates_draft.md rev 15 (review r16 fixes). Three tables, each computed by libpcre2-8
# (public API, ctypes) AND Python `re`; every row asserts the two engines agree (0 disagreements expected).
#
# (W) THE WARNING'S ONE CRITERION (review r16 W1/W2/W4, SIMULATE-1/5): `anchor.whole` fires exactly on an explicit
#     anchor that provably sits at the EDGE of a filter role's stretch after macros are expanded (text in a hole is
#     not the role's text: a hole is no role). The message claims the anchor "always holds here and adds nothing".
#     For every place it fires, a COUNTER-CASE for that claim is planted: a NON-edge anchor in the same place, which
#     must change the answer (so it must NOT warn), beside the edge anchor, which must not change it (so the claim
#     is true where it fires). Filter role = PCRE2_ANCHORED|PCRE2_ENDANCHORED on the stretch as the subject; a final
#     program is searched (leftmost start, then the longest end both sides accept); a hole's text is spliced raw
#     inside `(?:...)` (§3.3: a hole is ONE entry).
# (T) review r16 FIXIND-1: the O69 tuple compare, 2 fields as written and 3 fields with EVERY comparison padded, against
#     integer lexicographic order.
# (A) the brief's any_case test: is `any_case(rx) := /(?i:${rx})/` a plain body? Meaning of any_case(S) (L66, §2.7):
#     s is accepted iff some t in S equals s up to letter case (simple case folding). Evaluated over a finite
#     universe for five argument kinds, under two readings of the hole: the document's (§11 "NO INHERITED FLAGS: a
#     hole's pattern keeps its own flags", emulated `(?i:(?-i:S))`) and a raw textual paste (PCRE's own reading of
#     the pasted text, every hole pasted raw, `(?i:(?:S))`; a filter role's literal stays its own scope, since a
#     filter role is a separate whole match, not text of the body).
import ctypes, itertools, re

L = ctypes.CDLL("libpcre2-8.so.0")
L.pcre2_compile_8.restype = ctypes.c_void_p
L.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int),
                              ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
L.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
L.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint32,
                            ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_match_data_free_8.argtypes = [ctypes.c_void_p]
ANCH, ENDANCH = 0x80000000, 0x20000000
_cache = {}
DISAGREE = [0]


def _code(p):
    if p not in _cache:
        e, o = ctypes.c_int(), ctypes.c_size_t()
        c = L.pcre2_compile_8(p.encode(), len(p.encode()), 0, ctypes.byref(e), ctypes.byref(o), None)
        assert c, (p, e.value)
        _cache[p] = c
    return _cache[p]


def py(p):
    p = p.replace(r"\z", r"\Z").replace("(?<", "(?P<").replace("(?P<=", "(?<=").replace("(?P<!", "(?<!")
    # Python refuses a global flag group not at the start: spell (?m)/(?s) prefixes as scoped groups
    return re.sub(r"^\(\?([a-z]+)\)(.*)$", r"(?\1:\2)", p, flags=re.S)


def whole(p, t):
    """p matches all of t (a filter role on the stretch t), both engines."""
    c = _code(p)
    md = L.pcre2_match_data_create_from_pattern_8(c, None)
    rc = L.pcre2_match_8(c, t.encode(), len(t.encode()), 0, ANCH | ENDANCH, md, None)
    L.pcre2_match_data_free_8(md)
    a = rc >= 0
    b = re.fullmatch(py(p), t) is not None
    if a != b:
        DISAGREE[0] += 1
        print("  ENGINE DISAGREEMENT", repr(p), repr(t), a, b)
    return a


def search_amp(sides, s):
    """a final program `A & B & ...`, searched: leftmost start, longest end at which every side matches whole."""
    for i in range(len(s) + 1):
        for j in range(len(s), i - 1, -1):
            if all(whole(p, s[i:j]) for p in sides):
                return (i, j)
    return None


def show(x):
    return "no match" if x is None else ("%d-%d" % x if isinstance(x, tuple) else str(x))


# ---------------------------------------------------------------------------------------------------- table (W)
print("(W) anchor.whole: the edge criterion, with a counter-case for the message's claim in every place it fires")
print("    columns: place | program | subject | with the anchor | without | edge? | warns (rule) | claim holds")
ROWS = []


def row(place, prog, subj, with_, without, edge, hole=False):
    same = with_ == without
    warns = edge
    # the claim "always holds here, adds nothing" must be TRUE wherever it warns; a non-edge anchor must change
    # the answer in the counter-cases (they are chosen to), so it is right that it does not warn
    ok = (same if warns else True)
    ROWS.append(ok)
    print("  %-26s | %-44s | %-9r | %-8s | %-8s | %-4s | %-5s | %s" % (
        place, prog, subj, show(with_), show(without), "yes" if edge else "no", "yes" if warns else "no",
        ("yes" if same else "NO") if warns else ("(silent: a hole is no role, ruled)" if hole else
                                                  "(differs: the anchor means something)" if not same else
                                                  "BAD COUNTER-CASE (non-edge but no difference)")))


# 1. a side of `&` in a final program
row("side of & (final)", "/\\d+/ & /^5/  vs  /\\d+/ & /5/", "x55", search_amp([r"\d+", r"^5"], "x55"),
    search_amp([r"\d+", r"5"], "x55"), True)
row("side of & (final)", "/\\d+/ & /0*^5/  vs  /\\d+/ & /0*5/", "x005", search_amp([r"\d+", r"0*^5"], "x005"),
    search_amp([r"\d+", r"0*5"], "x005"), False)
row("side of & (final)", "/\\w+/ & /a?^b/  vs  /\\w+/ & /a?b/", "ab", search_amp([r"\w+", r"a?^b"], "ab"),
    search_amp([r"\w+", r"a?b"], "ab"), False)
row("side of & (final)", "/\\w+/ & /foo$(?s:.*)/ vs no $", "foobar", search_amp([r"\w+", r"foo$(?s:.*)"], "foobar"),
    search_amp([r"\w+", r"foo(?s:.*)"], "foobar"), False)
row("side of & (final)", "/[\\w\\n]+/ & /(?m)^foo/ vs /foo/", "xfoo", search_amp([r"[\w\n]+", r"(?m)^foo"], "xfoo"),
    search_amp([r"[\w\n]+", r"foo"], "xfoo"), True)
row("side of & (final)", "/[\\w\\n]+/ & /(?ms).*^foo.*/ vs no ^", "xfoo",
    search_amp([r"[\w\n]+", r"(?ms).*^foo.*"], "xfoo"), search_amp([r"[\w\n]+", r"(?ms).*foo.*"], "xfoo"), False)
# 2. a `label:` condition: x's text t matched whole
for t in ("S-1", "Sab"):
    row("label: condition", "(x: /^S\\w*/)  vs  (x: /S\\w*/)", t, whole(r"^S\w*", t), whole(r"S\w*", t), True)
row("label: condition", "(x: /.*^err.*/)  vs  (x: /.*err.*/)", "x err", whole(r".*^err.*", "x err"),
    whole(r".*err.*", "x err"), False)
# 3. a compile-time set (a warning-name set over whole names)
NAMES = ["dead.", "dead.x", "xdead.", "ab", "b"]
row("compile-time set", "@warn.off(/^dead\\./) vs /dead\\./", "names",
    [n for n in NAMES if whole(r"^dead\.", n)], [n for n in NAMES if whole(r"dead\.", n)], True)
row("compile-time set", "@warn.off(/a?^b/)  vs  /a?b/", "names",
    [n for n in NAMES if whole(r"a?^b", n)], [n for n in NAMES if whole(r"a?b", n)], False)


# 4. a side of `&` inside a hole: /port=${ P & <256 }/ searched; the hole's stretch is what both sides match whole
def port(P, s):
    LT256 = "(?:" + "|".join(str(v) for v in range(256)) + ")"
    for i in range(len(s) + 1):
        if not s.startswith("port=", i):
            continue
        for j in range(len(s), i + 4, -1):
            st = s[i + 5:j]
            if whole(P, st) and whole(LT256, st):
                return (i, j)
    return None


row("side of & in a hole", "/port=${ /^\\d+$/ & <256 }/ vs no ^$", "port=80", port(r"^\d+$", "port=80"),
    port(r"\d+", "port=80"), True)
row("side of & in a hole", "/port=${ /\\d*^5\\d*/ & <256 }/ vs no ^", "port=15", port(r"\d*^5\d*", "port=15"),
    port(r"\d*5\d*", "port=15"), False)


# 5. a macro body standing in a filter role (W3 LEAN (b): no authorship exemption): x & anchored(r), and a user
#    macro with the same body; and a hole parameter (silent by the hole ruling, W4)
row("macro body (anchored)", "/\\w+/ & anchored(/foo/) vs & /foo/", "xfoo",
    search_amp([r"\w+", r"\A(?:foo)\z"], "xfoo"), search_amp([r"\w+", r"foo"], "xfoo"), True)
row("macro body (user, same)", "/\\w+/ & my_anch(/foo/) vs & /foo/", "xfoo",
    search_amp([r"\w+", r"\A(?:foo)\z"], "xfoo"), search_amp([r"\w+", r"foo"], "xfoo"), True)
row("hole param (padded)", "/\\d+/ & padded(/^5/) vs padded(/5/)", "x005",
    search_amp([r"\d+", r"0*(?:^5)"], "x005"), search_amp([r"\d+", r"0*(?:5)"], "x005"), False, hole=True)
row("written hole = macro", "/\\d+/ & /0*${/^5/}/ vs /0*${/5/}/", "x005",
    search_amp([r"\d+", r"0*(?:^5)"], "x005"), search_amp([r"\d+", r"0*(?:5)"], "x005"), False, hole=True)
row("hand expansion = macro", "/\\d+/ & /0*^5/ vs /0*5/", "x005",
    search_amp([r"\d+", r"0*^5"], "x005"), search_amp([r"\d+", r"0*5"], "x005"), False)
row("hole param at body edge", "/\\w+/ & startsWith(/^foo/) vs (/foo/)", "xfoobar",
    search_amp([r"\w+", r"(?:^foo)(?s:.*)"], "xfoobar"), search_amp([r"\w+", r"(?:foo)(?s:.*)"], "xfoobar"), False,
    hole=True)
print("  claim true at every place the rule warns: %s (%d rows)" % (all(ROWS), len(ROWS)))

# ---------------------------------------------------------------------------------------------------- table (T)
print()
print("(T) O69 tuple compare (review r16 FIXIND-1): conditions (l: padded(cmp)) = whole match of /0*(?:SET)/")


def canon(pred, top=120):
    vs = [str(v) for v in range(top) if pred(v)]
    return "(?:" + "|".join(vs) + ")" if vs else "(?!)"


def padded(pred):
    return "0*(?:%s)" % canon(pred)


def fields(n, s):
    m = re.fullmatch(r"(\d{1,2}):(\d\d)" + (r":(\d\d)" if n == 3 else ""), s)
    pat = r"(\d{1,2}):(\d\d)" + (r":(\d\d)" if n == 3 else "")
    assert (m is not None) == whole(pat, s)
    return None if m is None else list(m.groups())


def lex(t, b, strict, last):
    ents = []
    for k in range(len(b)):
        e = [(i, padded(lambda v, i=i: v == b[i])) for i in range(k)]
        e.append((k, padded(lambda v, k=k: (last if k == len(b) - 1 else strict)(v, b[k]))))
        ents.append(e)
    return any(all(whole(rx, t[i]) for i, rx in e) for e in ents)


def tup(s, lo, hi):
    t = fields(len(lo), s)
    if t is None:
        return False
    return lex(t, lo, lambda a, b: a > b, lambda a, b: a >= b) and lex(t, hi, lambda a, b: a < b, lambda a, b: a <= b)


def truth(s, lo, hi):
    return lo <= tuple(int(x) for x in s.split(":")) <= hi


subs2 = ["%s:%s" % (a, b) for a in [str(i) for i in range(13)] + ["%02d" % i for i in range(10)]
         for b in ["%02d" % j for j in (0, 1, 29, 30, 31, 59)]]
n = bad = 0
for lo in [(9, 0), (9, 30), (0, 0), (5, 1)]:
    for hi in [(10, 0), (9, 30), (12, 59), (5, 1)]:
        for s in subs2:
            n += 1
            bad += tup(s, lo, hi) != truth(s, lo, hi)
print("  2 fields (as written): %d cases, %d differ" % (n, bad))
subs3 = ["%s:%s:%s" % (a, b, c) for a in ["9", "09", "10", "8", "08", "0", "00"] for b in ["29", "30", "31", "00"]
         for c in ["00", "05", "06", "59"]]
n = bad = 0
for lo in [(9, 30, 5), (0, 0, 0)]:
    for hi in [(10, 0, 0), (9, 30, 5)]:
        for s in subs3:
            n += 1
            bad += tup(s, lo, hi) != truth(s, lo, hi)
print("  3 fields (every comparison padded, rev 15): %d cases, %d differ" % (n, bad))

# ---------------------------------------------------------------------------------------------------- table (A)
print()
print("(A) is any_case(rx) := /(?i:${rx})/ a plain body?  meaning: s accepted iff s equals some member of S up to case")
U = ["".join(p) for k in range(0, 5) for p in itertools.product("hHoO1", repeat=k)]


def members(accept):
    return {u for u in U if accept(u)}


def meaning(S):
    f = {t.lower() for t in S}
    return {u for u in U if u.lower() in f}


# argument kinds: (name, the argument as a set over U, document-reading body, raw-paste-reading body)
KINDS = [
    ("one literal /ho/",
     lambda u: whole(r"ho", u), lambda u: whole(r"(?i:(?-i:ho))", u), lambda u: whole(r"(?i:(?:ho))", u)),
    ("number filter <12",
     lambda u: whole(r"(?:" + "|".join(str(v) for v in range(12)) + ")", u),
     lambda u: whole(r"(?i:(?-i:(?:" + "|".join(str(v) for v in range(12)) + ")))", u),
     lambda u: whole(r"(?i:(?:(?:" + "|".join(str(v) for v in range(12)) + ")))", u)),
    # a set with an `&` inside: /[a-z]+/ & /h\w*/ ; each side is its own literal in a filter role (own flags)
    ("a set with & /[a-z]+/ & /h\\w*/",
     lambda u: whole(r"[a-z]+", u) and whole(r"h\w*", u),
     lambda u: whole(r"[a-z]+", u) and whole(r"h\w*", u),
     lambda u: whole(r"[a-z]+", u) and whole(r"h\w*", u)),
    # a label condition: /(?<w>\w+)/ & (w: "ho") ; the condition's set is its own literal in a filter role
    ("a label condition (w: \"ho\")",
     lambda u: whole(r"(?<w>\w+)", u) and whole(r"ho", u),
     lambda u: whole(r"(?i:(?-i:\w+))", u) and whole(r"ho", u),
     lambda u: whole(r"(?i:\w+)", u) and whole(r"ho", u)),
    # a nested transform: startsWith("h") := /(?:${"h"})(?s:.*)/ ; its own parameter sits in a hole of its body
    ("a nested transform startsWith(\"h\")",
     lambda u: whole(r"(?:h)(?s:.*)", u),
     lambda u: whole(r"(?i:(?-i:(?:(?-i:h))(?s:.*)))", u),
     lambda u: whole(r"(?i:(?:(?:h)(?s:.*)))", u)),
]
for name, arg, doc, paste in KINDS:
    S = members(arg)
    want = meaning(S)
    d = members(doc)
    p = members(paste)
    print("  %-38s | %3d strings | document reading: %3d differ | raw paste: %3d differ" % (
        name, len(U), len(want ^ d), len(want ^ p)))
print()
print("engine disagreements (libpcre2-8 vs Python re): %d" % DISAGREE[0])
