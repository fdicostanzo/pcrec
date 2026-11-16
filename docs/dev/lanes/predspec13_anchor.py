# predspec13: THE AMPERSAND RULE TESTED BY POSITION (predicates_draft.md rev 13, §11), and the `anchored` wording check.
# The ruled rule (COND-FAMILY.md on main, CF:1054-1062): BOTH operands of `&` are FILTER ROLES; a filter role matches
# its span WHOLE and opens a SCOPED MATCH over it; a hole opens none; an anchor (^ $ \A \z \Z) reads the INNERMOST
# scoped match ("plain PCRE with the span as the subject", CF:1013-1014). This script EMULATES that rule on top of
# libpcre2-8 (public API, ctypes) and, as a second engine, Python's `re`; it is not pcrec.
#
# Nodes (evaluated on a candidate span [k, m) of the subject s, inside a scope [I, J)):
#   Frag(p)      rx text that is NOT a filter role: PCRE matches p from k, its anchors reading the scope [I, J);
#                emulated by matching `(?:p)(?=(?s:.){J-m}\z)` on s[I:J] at offset k-I, PCRE2_ANCHORED (the lookahead
#                pins the end at m without moving the scope's end).
#   Amp(a, b)    `a & b`: a filter role, so a NEW scope [k, m); both operands evaluated whole on it.
#   Filt(x)      any one filter role (an rx operand alone, an `anchored` read as "a filter role"): new scope [k, m).
#   Seq(parts)   concatenation (rx text around holes): some split k = p0 <= ... <= pn = m, each part on its piece.
#   Cond(P, l, C) `P & (l: C)`: P whole on [k, m) (PCRE's parse), then C a filter role on label l's span.
# A FINAL program is searched: leftmost start i, then every end j at i that qualifies (listed, longest first; D196
# reports the left operand's preferred one, which for the greedy operands used here is the longest).
import ctypes, re, sys

L = ctypes.CDLL("libpcre2-8.so.0")
L.pcre2_compile_8.restype = ctypes.c_void_p
L.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int),
                              ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
L.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
L.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint32,
                            ctypes.c_void_p, ctypes.c_void_p]
L.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
L.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
L.pcre2_pattern_info_8.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
L.pcre2_substring_number_from_name_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
ANCH, ENDANCH = 0x80000000, 0x20000000
_cache = {}

def _code(p):
    if p not in _cache:
        e, o = ctypes.c_int(), ctypes.c_size_t()
        c = L.pcre2_compile_8(p.encode(), len(p.encode()), 0, ctypes.byref(e), ctypes.byref(o), None)
        assert c, (p, e.value)
        _cache[p] = c
    return _cache[p]

def pcre(p, s, off=0, flags=0):
    """-> None or (ovector list of (start, end))"""
    c = _code(p)
    md = L.pcre2_match_data_create_from_pattern_8(c, None)
    rc = L.pcre2_match_8(c, s.encode(), len(s), off, flags, md, None)
    if rc < 0:
        return None
    ov = L.pcre2_get_ovector_pointer_8(md)
    return [(ov[2 * g], ov[2 * g + 1]) for g in range(rc)]

def py(p):
    return p.replace(r"\z", r"\Z").replace("(?<", "(?P<").replace("(?P<=", "(?<=").replace("(?P<!", "(?<!")

ENGINE = "pcre2"

def frag(p, s, k, m, I, J):
    q = "(?:%s)(?=(?s:.){%d}\\z)" % (p, J - m)
    T = s[I:J]
    if ENGINE == "pcre2":
        r = pcre(q, T, k - I, ANCH)
        return r is not None and r[0][1] == m - I
    # Python refuses a flag group not at the pattern's start: spell a leading (?s)/(?m) of p as a scoped group
    pp = re.sub(r"^\(\?([a-z]+)\)(.*)$", r"(?\1:\2)", p, flags=re.S)
    r = re.compile(py("(?:%s)(?=(?s:.){%d}\\z)" % (pp, J - m))).match(T, k - I)
    return r is not None and r.end() == m - I

def whole_groups(p, t, name):
    if ENGINE == "pcre2":
        r = pcre(p, t, 0, ANCH | ENDANCH)
        if r is None:
            return None
        g = L.pcre2_substring_number_from_name_8(_code(p), name.encode())
        return r[g] if g < len(r) else (None, None)
    r = re.fullmatch(py(p), t)
    return None if r is None else r.span(name)

class Frag:
    def __init__(s, p): s.p = p
    def ev(s, sub, k, m, I, J): return frag(s.p, sub, k, m, I, J)
class Filt:
    def __init__(s, x): s.x = x
    def ev(s, sub, k, m, I, J): return s.x.ev(sub, k, m, k, m)
class Amp:
    def __init__(s, a, b): s.a, s.b = a, b
    def ev(s, sub, k, m, I, J): return s.a.ev(sub, k, m, k, m) and s.b.ev(sub, k, m, k, m)
class Seq:
    def __init__(s, *parts): s.parts = parts
    def ev(s, sub, k, m, I, J):
        def go(t, pos):
            if t == len(s.parts):
                return pos == m
            return any(s.parts[t].ev(sub, pos, q, I, J) and go(t + 1, q) for q in range(pos, m + 1))
        return go(0, k)
class Cond:
    def __init__(s, P, l, C): s.P, s.l, s.C = P, l, C
    def ev(s, sub, k, m, I, J):
        sp = whole_groups(s.P, sub[k:m], s.l)
        if sp is None or sp[0] is None or sp[0] < 0 or sp[0] > len(sub):
            return False
        a, b = k + sp[0], k + sp[1]
        return s.C.ev(sub, a, b, a, b)

def searched(node, sub):
    n = len(sub)
    for i in range(n + 1):
        ends = [j for j in range(n, i - 1, -1) if node.ev(sub, i, j, 0, n)]
        if ends:
            return "match (%d,%d)%s" % (i, ends[0], "" if len(ends) == 1 else
                                         " [ends at %d qualifying: %s]" % (i, ",".join(map(str, ends))))
    return "no match"

LT256 = "(?:0|[1-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-5])"   # the comparison set <256: canonical numerals 0..255 (C9)
num = lambda: Frag(LT256)

ROWS = [
 # position, program (draft spelling), node, subject
 ("(i) final, searched", "/^\\d+$/  (no &: the subject's ends)", Frag(r"^\d+$"), "x300 12"),
 ("(i) final, searched", "/^\\d+$/ & <256", Amp(Frag(r"^\d+$"), num()), "x300 12"),
 ("(i) final, searched", "/\\d+/ & <256  (the same answer: the anchors add nothing)", Amp(Frag(r"\d+"), num()), "x300 12"),
 ("(i) look-alike P vs P & /(?s).*/", "/^foo/", Frag(r"^foo"), "xfoo"),
 ("(i) look-alike P vs P & /(?s).*/", "/^foo/ & /(?s).*/", Amp(Frag(r"^foo"), Frag(r"(?s).*")), "xfoo"),
 ("(i) look-alike P vs P & /(?s).*/", "/foo$/", Frag(r"foo$"), "foox"),
 ("(i) look-alike P vs P & /(?s).*/", "/foo$/ & /(?s).*/", Amp(Frag(r"foo$"), Frag(r"(?s).*")), "foox"),
 ("(ii) final under anchored", "anchored(/^\\d+$/ & <256) = /\\A${...}\\z/", Seq(Frag(r"\A"), Amp(Frag(r"^\d+$"), num()), Frag(r"\z")), "x300 12"),
 ("(ii) final under anchored", "anchored(/^\\d+$/ & <256)", Seq(Frag(r"\A"), Amp(Frag(r"^\d+$"), num()), Frag(r"\z")), "200"),
 ("(ii) final under anchored", "anchored(/^\\d+$/ & <256)", Seq(Frag(r"\A"), Amp(Frag(r"^\d+$"), num()), Frag(r"\z")), "200\n"),
 ("(ii) final under anchored", "anchored(/\\d+/ & <256)  (same answers without the operand anchors)", Seq(Frag(r"\A"), Amp(Frag(r"\d+"), num()), Frag(r"\z")), "200\n"),
 ("(iii) & in a hole", "/port=${ /^\\d+$/ & <256 }/", Seq(Frag("port="), Amp(Frag(r"^\d+$"), num())), "port=80"),
 ("(iii) & in a hole", "/port=${ /^\\d+$/ & <256 }/", Seq(Frag("port="), Amp(Frag(r"^\d+$"), num())), "port=300"),
 ("(iii) & in a hole", "/port=${ /\\d+/ & <256 }\\b/  (author's fix for 'the whole number')", Seq(Frag("port="), Amp(Frag(r"\d+"), num()), Frag(r"\b")), "port=300"),
 ("(iii) the owner's acceptance row (CF:1078-1079 on main)", "/999${ /\\d+/ & <100 }999/", Seq(Frag("999"), Amp(Frag(r"\d+"), Frag("(?:0|[1-9]\\d?)")), Frag("999")), "99945999"),
 ("(iii) its near row", "/999${ /\\d+/ & <100 }999/", Seq(Frag("999"), Amp(Frag(r"\d+"), Frag("(?:0|[1-9]\\d?)")), Frag("999")), "99912345999"),
 ("(iii) alt. reading: anchors read the SUBJECT", "/port=${/^\\d+$/}/ spliced (= /port=^\\d+$/)", Frag(r"port=^\d+$"), "port=80"),
 ("(iii) hole look-alike, no &", "/x${/^a/}/  (a hole opens no scope: ^ = the subject's start)", Seq(Frag("x"), Frag("^a")), "xa"),
 ("(iii) hole look-alike, with &", "/x${/^a/ & /(?s).*/}/", Seq(Frag("x"), Amp(Frag("^a"), Frag(r"(?s).*"))), "xa"),
 ("(iv) & nested in a hole of an & operand", "/\\w+/ & /a${ /^\\d$/ & <5 }b/", Amp(Frag(r"\w+"), Seq(Frag("a"), Amp(Frag(r"^\d$"), Frag("[0-4]")), Frag("b"))), "a3b"),
 ("(iv) alt. reading: inner ^ reads the OUTER operand's span", "/\\w+/ & /a^\\d$b/", Amp(Frag(r"\w+"), Frag(r"a^\d$b")), "a3b"),
 ("(iv) condition inside a hole", "P := /(?<w>\\w)-(?<v>\\w+)/; /k=${ P & (v: /^a\\w*/) }/", Seq(Frag("k="), Cond(r"(?<w>\w)-(?<v>\w+)", "v", Frag(r"^a\w*"))), "k=x-ab"),
 ("(iv) condition inside a hole", "P := /(?<w>\\w)-(?<v>\\w+)/; /k=${ P & (v: /^a\\w*/) }/", Seq(Frag("k="), Cond(r"(?<w>\w)-(?<v>\w+)", "v", Frag(r"^a\w*"))), "k=x-ba"),
 ("(v) label: condition", "P := /(?<w>\\w) (?<x>\\w+)/; P & (x: /^S\\w*/)", Cond(r"(?<w>\w) (?<x>\w+)", "x", Frag(r"^S\w*")), "a Sab"),
 ("(v) label: condition", "P & (x: /^S\\w*/)", Cond(r"(?<w>\w) (?<x>\w+)", "x", Frag(r"^S\w*")), "a xSab"),
 ("(vi) operand is an & chain", "(/^\\d+/ & /\\d+$/) & <256", Amp(Amp(Frag(r"^\d+"), Frag(r"\d+$")), num()), "x300 12"),
 ("(vi) operand is an & chain", "/^\\d+/ & (/\\d+$/ & <256)", Amp(Frag(r"^\d+"), Amp(Frag(r"\d+$"), num())), "x300 12"),
 ("(vii) edge assertion: why it is an ERROR", "/\\w+/ & /\\bfoo/ read as plain PCRE on the span", Amp(Frag(r"\w+"), Frag(r"\bfoo")), "xfoo"),
 ("(vii) edge assertion: the pasted text", "/\\w*\\bfoo/  (\\b reads the real context)", Frag(r"\w*\bfoo"), "xfoo"),
 ("(vii) (?m) in an operand", "/\\w+/ & /(?m)^foo/", Amp(Frag(r"\w+"), Frag(r"(?m)^foo")), "xfoo"),
 ("(viii) rx-text & (switch ON)", "/^\\d+&${<256}$/  (operands ^\\d+ and ${<256}$)", Amp(Frag(r"^\d+"), Seq(num(), Frag("$"))), "x300 12"),
 ("(viii) rx-text & (switch ON)", "/^(?:\\d+&${<256})$/  (anchors outside the group read the subject)", Seq(Frag("^"), Amp(Frag(r"\d+"), num()), Frag("$")), "x300 12"),
 ("(viii) rx-text & (switch ON)", "/^(?:\\d+&${<256})$/", Seq(Frag("^"), Amp(Frag(r"\d+"), num()), Frag("$")), "200"),
 ("(viii) rx-text & (switch ON)", "/a|^b&\\w+/  (| outside: ^b is an & operand)", None, "xb"),
]
# `/a|^b&\w+/`: D196 precedence, the top-level alternation is a | ( ^b & \w+ ).
class Alt:
    def __init__(s, *xs): s.xs = xs
    def ev(s, sub, k, m, I, J): return any(x.ev(sub, k, m, I, J) for x in s.xs)
ROWS[-1] = ROWS[-1][:2] + (Alt(Frag("a"), Amp(Frag("^b"), Frag(r"\w+"))), ROWS[-1][3])

# The `anchored` wording check (CF:1048-1053: the "P in filter role on the enclosing scope" wording may be used only if
# no case differs from \A(?:P)\z). FILTER-ROLE reading = Filt(P) where it stands; TEXT reading = \A(?:P)\z spliced.
class ScopeFilt:
    """P matched WHOLE on the INNERMOST SCOPED MATCH [I, J) (a hole opens none, so in a hole that is the scope around)"""
    def __init__(s, x): s.x = x
    def ev(s, sub, k, m, I, J): return k == I and m == J and s.x.ev(sub, k, m, k, m)
def A_text(p): return Seq(Frag(r"\A"), Frag(p), Frag(r"\z"))
def A_scope(p): return ScopeFilt(Frag(p))     # wording 1: "P in filter role on the enclosing scope" = the innermost scope
def A_here(p): return Filt(Frag(p))           # wording 2: "P in filter role where it stands" = on the span it takes
ANCH_ROWS = [
 ("a final pattern", lambda A: A("foo"), "foo\n"),
 ("a final pattern", lambda A: A("foo"), "foo"),
 ("a final pattern, $ in P", lambda A: A("foo$"), "foo\n"),
 ("a final pattern, alternation at P's top", lambda A: A("a|b"), "ab"),
 ("a final pattern, alternation at P's top", lambda A: A("a|ab"), "ab"),
 ("a final pattern, (?m) inside P", lambda A: A("(?m)^a$"), "a\n"),
 ("a final pattern, (?m) inside P", lambda A: A("(?m)a$\\n^b"), "a\nb"),
 ("inside a filter: x & anchored(P), x := /\\w+/", lambda A: Amp(Frag(r"\w+"), A("foo")), "xfoo"),
 ("inside a filter, (?m) and alternation", lambda A: Amp(Frag(r"(?s).*"), A("(?m)^a$|b")), "a\n"),
 ("a label: condition", lambda A: Cond(r"(?<w>\w) (?<x>\w+)", "x", A("ab|b")), "z ab"),
 ("in a HOLE: /x${anchored(/a/)}/", lambda A: Seq(Frag("x"), A("a")), "xa"),
 ("in a HOLE at the scope's start: /${anchored(/a/)}b/", lambda A: Seq(A("a"), Frag("b")), "ab"),
 ("in a hole of an & operand: /\\w+/ & /x${anchored(/a/)}/", lambda A: Amp(Frag(r"\w+"), Seq(Frag("x"), A("a"))), "xa"),
]

def main():
    global ENGINE
    print("# THE AMPERSAND RULE BY POSITION (searched final programs unless the row says otherwise)")
    bad = 0
    for pos, prog, node, sub in ROWS:
        ENGINE = "pcre2"; a = searched(node, sub)
        ENGINE = "re"; b = searched(node, sub)
        bad += a != b
        print("%-46s %-72s on %-10r pcre2: %s%s" % (pos, prog, sub, a, "" if a == b else "  | re DIFFERS: " + b))
    print()
    print("# anchored(P): the ruled text \\A(?:P)\\z vs two readings of 'P in filter role on the enclosing scope':")
    print("#   scope = P whole on the innermost scoped match; where-it-stands = P whole on the span it takes")
    for where, mk, sub in ANCH_ROWS:
        res = {}
        for ENGINE in ("pcre2", "re"):
            res[ENGINE] = [searched(mk(A), sub) for A in (A_text, A_scope, A_here)]
        bad += res["pcre2"] != res["re"]
        t, f1, f2 = res["pcre2"]
        print("%-56s on %-7r \\A..\\z: %-12s | scope: %-12s %-4s | where-it-stands: %-12s %s" % (where, sub, t, f1,
              "SAME" if t == f1 else "DIFF", f2, "SAME" if t == f2 else "DIFF"))
    print()
    print("engines disagree on %d rows" % bad)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
