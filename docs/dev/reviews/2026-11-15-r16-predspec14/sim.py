# SIMULATE lens: the rule implemented from the rev 14 TEXT. A filter role = PCRE2 whole match
# (ANCHORED|ENDANCHORED) with the stretch as the subject; a hole = the argument spliced as (?:...) into the body
# text (anchors in it read the enclosing filter role's stretch = plain PCRE on that stretch). A final program is
# searched: leftmost start, ends longest first (the greedy left operands used here prefer the longest).
# Second engine: Python re.fullmatch; any disagreement aborts.
import ctypes, re
L = ctypes.CDLL("libpcre2-8.so.0")
L.pcre2_compile_8.restype = ctypes.c_void_p
L.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int),
                              ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
L.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
L.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint32,
                            ctypes.c_void_p, ctypes.c_void_p]
ANCH, ENDANCH = 0x80000000, 0x20000000
C = {}


def whole_pcre(p, t):
    if p not in C:
        e, o = ctypes.c_int(), ctypes.c_size_t()
        C[p] = L.pcre2_compile_8(p.encode(), len(p.encode()), 0, ctypes.byref(e), ctypes.byref(o), None)
        assert C[p], p
    md = L.pcre2_match_data_create_from_pattern_8(C[p], None)
    return L.pcre2_match_8(C[p], t.encode(), len(t), 0, ANCH | ENDANCH, md, None) >= 0


def whole_py(p, t):
    q = re.sub(r"^\(\?([a-z]+)\)(.*)$", r"(?\1:\2)", p, flags=re.S)
    return re.fullmatch(q.replace(r"\z", r"\Z"), t) is not None


def whole(p, t):
    a, b = whole_pcre(p, t), whole_py(p, t)
    assert a == b, ("engines disagree", p, t)
    return a


def amp(*ps):          # an & chain as a filter on stretch t (every side matched whole on t)
    return lambda t: all(whole(p, t) for p in ps)


def search(f, s):      # a final program, searched
    for i in range(len(s) + 1):
        for j in range(len(s), i - 1, -1):
            if f(s[i:j]):
                return (i, j)
    return None


def final(p, s):     # a lone final pattern: plain PCRE search, anchors read the subject (Python re as the engine)
    m = re.search(p.replace(r"\z", r"\Z"), s)
    return (m.start(), m.end()) if m else None


def hole(body, arg):   # splice arg into the body's hole, grouped
    return body.replace("${}", "(?:%s)" % arg)


PAD, SW, EW, ANC, CONT = "0*${}", "${}(?s:.*)", "(?s:.*?)${}", r"\A${}\z", "(?s:.*?)${}(?s:.*)"
LT256 = r"(?:0|[1-9]\d?|1\d\d|2[0-4]\d|25[0-5])"
rows = []


def row(tag, name, f, s):
    rows.append((tag, name, s, search(f, s)))


# S1: an anchor NOT at the edge of a filter role's own text: the warning fires by the text, the anchor means something
row("S1", r"/\d+/ & padded(/^5/)  [hole: no warning]", amp(r"\d+", hole(PAD, "^5")), "x005")
row("S1", r"/\d+/ & /0*^5/  [hand expansion, own text: fires]", amp(r"\d+", "0*^5"), "x005")
row("S1", r"/\d+/ & /0*5/  [the anchor removed]", amp(r"\d+", "0*5"), "x005")
row("S1b", r"/[\w ]+/ & /.*^err.*/  [L17's spelled body: fires]", amp(r"[\w ]+", ".*^err.*"), "x err")
row("S1b", r"/[\w ]+/ & /.*err.*/  [anchor removed]", amp(r"[\w ]+", ".*err.*"), "x err")
row("S1c", r"/[\w\n]+/ & /(?ms).*^foo.*/  [(?m) mid: fires]", amp(r"[\w\n]+", r"(?ms).*^foo.*"), "x\nfoo")
row("S1c", r"/[\w\n]+/ & /(?s).*foo.*/  [anchor removed]", amp(r"[\w\n]+", r"(?s).*foo.*"), "x\nfoo")
row("S1c", r"/[\w\n]+/ & /(?ms).*^foo.*/  [(?m) mid: fires]", amp(r"[\w\n]+", r"(?ms).*^foo.*"), "xfoo")
row("S1c", r"/[\w\n]+/ & /(?s).*foo.*/  [anchor removed]", amp(r"[\w\n]+", r"(?s).*foo.*"), "xfoo")
row("S1d", r"/\w+/ & /a?^b/  [fires]", amp(r"\w+", "a?^b"), "ab")
row("S1d", r"/\w+/ & /a?b/  [removed]", amp(r"\w+", "a?b"), "ab")
row("S1e", r"/\w+/ & /foo$(?s:.*)/  [fires]", amp(r"\w+", r"foo$(?s:.*)"), "foobar")
row("S1e", r"/\w+/ & /foo(?s:.*)/  [removed]", amp(r"\w+", r"foo(?s:.*)"), "foobar")
# S2: a hole parameter at the body's edge: the anchor adds nothing, no warning
for nm, body, a, b, s in [("startsWith", SW, "^foo", "foo", "xfoobar"), ("endsWith", EW, "bar$", "bar", "foobarx"),
                          ("anchored", ANC, "^foo$", "foo", "xfoo"), ("padded", PAD, "5$", "5", "x0057")]:
    row("S2", r"/\w+/ & %s(/%s/)" % (nm, a), amp(r"\w+", hole(body, a)), s)
    row("S2", r"/\w+/ & %s(/%s/)" % (nm, b), amp(r"\w+", hole(body, b)), s)
# S3: anchored(r) in a filter role = r (L69); a user macro with anchored's body
row("S3", r"/\w+/ & anchored(/foo/)  (= my_anchored(/foo/), same body)", amp(r"\w+", hole(ANC, "foo")), "xfoo")
row("S3", r"/\w+/ & /foo/", amp(r"\w+", "foo"), "xfoo")
# S4: nesting
row("S4", r"/\d+/ & padded(anchored(/5/))", amp(r"\d+", hole(PAD, hole(ANC, "5"))), "x005")
row("S4", r"/\d+/ & anchored(padded(/5/))", amp(r"\d+", hole(ANC, hole(PAD, "5"))), "x005")
rows.append(("S4", r"final padded(anchored(/5/)) [plain PCRE search]", "005", final(hole(PAD, hole(ANC, "5")), "005")))
rows.append(("S4", r"final anchored(padded(/5/)) [plain PCRE search]", "005", final(hole(ANC, hole(PAD, "5")), "005")))
rows.append(("S4", r"final padded(anchored(/5/)) [plain PCRE search]", "5", final(hole(PAD, hole(ANC, "5")), "5")))
row("S4", r"/\d+/ & contains(padded(/^5/))", amp(r"\d+", hole(CONT, hole(PAD, "^5"))), "x0057")
row("S4", r"/\d+/ & contains(padded(/5/))", amp(r"\d+", hole(CONT, hole(PAD, "5"))), "x0057")
row("S4", r'/\d+/ & startsWith("5")', amp(r"\d+", hole(SW, "5")), "x0057")
# S5: L13 / E-CTX-5 sets (whole match on each string)
for w in ["5", "05", "005", "57", "057"]:
    rows.append(("S5", 'padded(/^5/) %s | padded("5") %s | padded(startsWith("5")) %s' % (
        whole(hole(PAD, "^5"), w), whole(hole(PAD, "5"), w), whole(hole(PAD, hole(SW, "5")), w)), w, "-"))
# S6: quoted answers of L41, L70, L13
row("S6", r"/\w+/ & /^foo/ (L41: foo 0-3)", amp(r"\w+", "^foo"), "foobar")
row("S6", r'/\w+/ & startsWith("foo") (L41: foobar)', amp(r"\w+", hole(SW, "foo")), "foobar")
row("S6", r"/^\d+$/ & <256 (L70: 1-3)", amp(r"^\d+$", LT256), "x300 12")
row("S6", r"/^foo/ & /(?s).*/ (L70: 1-4)", amp("^foo", "(?s).*"), "xfoo")
row("S6", r"/foo$/ & /(?s).*/ (L70: 0-3)", amp("foo$", "(?s).*"), "foox")
row("S6", r"/\d+/ & padded(/^5/) (L13: 3-4)", amp(r"\d+", hole(PAD, "^5")), "x005")
# S7: a parameter in BOTH roles: tagged(S) := /<(?<t>${S})>/ & (t: S); S's hole copy reads the & side's stretch
def tagged(S):
    body = hole("<(?P<t>${})>", S)
    def f(t):
        m = re.fullmatch(body.replace("(?<t>", "(?P<t>"), t)
        return m is not None and whole(body, t) and whole(S, m.group("t"))
    return f
row("S7", r"tagged(/^a/) on '<a>' [hole copy: ^ at '<' never holds]", tagged("^a"), "<a>")
row("S7", r"tagged(/a/) on '<a>'", tagged("a"), "<a>")
for tag, name, s, r in rows:
    print("%-4s %-66s on %-10r -> %s" % (tag, name, s, r))
print("engines disagree on 0 rows (any disagreement asserts)")
