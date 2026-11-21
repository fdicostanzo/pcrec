# predspec17: evidence for predicates_draft.md rev 17 (the owner's direction of 2026-11-15 23:07/23:10: the tuple
# compare DECOMPOSED into a projection and an array compare; names ruled `lex_` + size, 23:06). Engine helpers copied
# verbatim from predspec16_anchor.py. Every regex verdict is computed by libpcre2-8 (public API, ctypes) AND Python `re`;
# every call asserts the two engines agree (0 disagreements expected).
#
# THE DECOMPOSED FORM, emulated as written. The AUTHOR's pattern (with the author's labels) is matched WHOLE on the
# stretch; the projection is the array of the compared labels, written in the order the compare reads them (a label
# section `(h:)` per entry, or today's accessor macro `h_is(S) := (h: S)`); the array compare's body is the usual
# prefix expansion, each bound one `[ ]` of entries (any one), an entry `s[1](padded(==lo[1])) & s[2](padded(>=lo[2]))`
# = all its conditions; a condition `(h: padded(cmp))` = the label's text matched whole by `0*(?:SET)`, SET the
# comparison set's canonical numerals. Truth = integer lexicographic order of the labels' values in PROJECTION order.
#
# (D) the family over author patterns, against integer lexicographic order: 2 and 3 fields, between / at_least /
#     at_most and the derived strict / equal forms; one population whose author pattern holds the labels in the
#     OTHER group order than the projection (`/(?<m>\d\d) past (?<h>\d{1,2})/`, projection [h, m]).
# (R) rev 16's bundled bodies vs the decomposed form on the same populations (the expansion is the same conditions
#     with the author's labels for t1..t3): 0 differ expected.
# (W) the worked rows of §8 in the decomposed form.
import ctypes, itertools, json, re

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
L.pcre2_config_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
_vb = ctypes.create_string_buffer(64)
L.pcre2_config_8(11, _vb)                       # PCRE2_CONFIG_VERSION
print("libpcre2-8", _vb.value.decode(), "| Python", __import__("sys").version.split()[0])


def _code(p):
    if p not in _cache:
        e, o = ctypes.c_int(), ctypes.c_size_t()
        c = L.pcre2_compile_8(p.encode(), len(p.encode()), 0, ctypes.byref(e), ctypes.byref(o), None)
        assert c, (p, e.value)
        _cache[p] = c
    return _cache[p]


def py(p):
    p = p.replace(r"\z", r"\Z").replace("(?<", "(?P<").replace("(?P<=", "(?<=").replace("(?P<!", "(?<!")
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


def yn(b):
    return "accept" if b else "reject"



def canon(pred, top=130):
    vs = [str(v) for v in range(top) if pred(v)]
    return "(?:" + "|".join(vs) + ")" if vs else "(?!)"


def padded(pred):
    return "0*(?:%s)" % canon(pred)


def author(p, s):
    """the author's pattern matched WHOLE on s; its labels (a dict), or None"""
    ok = whole(p, s)
    m = re.fullmatch(py(p), s)
    assert (m is not None) == ok
    return m.groupdict() if ok else None


def bound(vals, proj, b, strict, last):
    """one bound's `[ ]`: s[1](padded(strict b1)) | s[1](padded(==b1)) & s[2](padded(strict b2)) | ...
    vals: the author's labels; proj: the projection (label names in compare order)"""
    if len(proj) != len(b):
        raise ValueError("wrong-length array: %d vs %d (a compile error)" % (len(proj), len(b)))
    for k in range(len(b)):
        conds = [(proj[i], padded(lambda v, i=i: v == b[i])) for i in range(k)]
        conds.append((proj[k], padded(lambda v, k=k: (last if k == len(b) - 1 else strict)(v, b[k]))))
        if all(vals[lab] is not None and whole(rx, vals[lab]) for lab, rx in conds):
            return True
    return False


GE = (lambda a, b: a > b, lambda a, b: a >= b)
LE = (lambda a, b: a < b, lambda a, b: a <= b)


def lex_ge(P, proj, lo, s):
    v = author(P, s)
    return v is not None and bound(v, proj, lo, *GE)


def lex_le(P, proj, hi, s):
    v = author(P, s)
    return v is not None and bound(v, proj, hi, *LE)


def lex_between(P, proj, lo, hi, s):
    v = author(P, s)
    return v is not None and bound(v, proj, lo, *GE) and bound(v, proj, hi, *LE)


# rev 16's bundled body, for (R): fields /(?<t1>${f[1]})${sep}(?<t2>${f[2]})/ then the same bounds over t1..tn
def rev16_between(pats, sep, lo, hi, s):
    p = re.escape(sep).join("(?<t%d>(?:%s))" % (i + 1, a) for i, a in enumerate(pats))
    proj = ["t%d" % (i + 1) for i in range(len(pats))]
    return lex_between(p, proj, lo, hi, s)


def truth(P, proj, s):
    v = author(P, s)
    return None if v is None else tuple(int(v[l]) for l in proj)


tot = {}


def tally(key, got, want):
    n, bad = tot.get(key, (0, 0))
    tot[key] = (n + 1, bad + (got != want))


# ---------------------------------------------------------------------------------------------------- table (D)
print()
print("(D) the decomposed family over AUTHOR patterns vs integer lexicographic order (projection order)")
HM = r"(?<h>\d{1,2}):(?<m>\d\d)"
HMS = r"(?<h>\d{1,2}):(?<m>\d\d):(?<sec>\d\d)"
PAST = r"(?<m>\d\d) past (?<h>\d{1,2})"          # labels in the OTHER group order; the projection says [h, m]
subs2 = ["%s:%s" % (a, b) for a in [str(i) for i in range(13)] + ["%02d" % i for i in range(10)]
         for b in ["%02d" % j for j in (0, 1, 29, 30, 31, 59)]]
subsp = ["%s past %s" % (b, a) for a in [str(i) for i in range(13)] + ["%02d" % i for i in range(10)]
         for b in ["%02d" % j for j in (0, 1, 29, 30, 31, 59)]]
subs3 = ["%s:%s:%s" % (a, b, c) for a in ["9", "09", "10", "8", "08", "0", "00", "11"] for b in ["29", "30", "31", "00"]
         for c in ["00", "04", "05", "06", "59"]]
B2 = [(9, 0), (9, 30), (0, 0), (5, 1), (10, 0), (12, 59)]
B3 = [(9, 30, 5), (0, 0, 0), (10, 0, 0), (9, 30, 6)]


def family(tag, P, proj, subs, bounds):
    for s in subs:
        v = truth(P, proj, s)
        f = v is not None
        for lo in bounds:
            tally(tag + "  lex_ge", lex_ge(P, proj, lo, s), f and v >= lo)
            tally(tag + "  lex_le", lex_le(P, proj, lo, s), f and v <= lo)
            tally(tag + "  above = P & !lex_le", f and not lex_le(P, proj, lo, s), f and v > lo)
            tally(tag + "  below = P & !lex_ge", f and not lex_ge(P, proj, lo, s), f and v < lo)
            tally(tag + "  equal = lex_between(lo, lo)", lex_between(P, proj, lo, lo, s), f and v == lo)
            for hi in bounds:
                tally(tag + "  lex_between", lex_between(P, proj, lo, hi, s), f and lo <= v <= hi)


family("2 h:m      [h, m]", HM, ["h", "m"], subs2, B2)
family("2 m past h [h, m]", PAST, ["h", "m"], subsp, B2)
family("3 h:m:s    [h, m, sec]", HMS, ["h", "m", "sec"], subs3, B3)
VERS = r"(?<major>0|[1-9]\d*)\.(?<minor>0|[1-9]\d*)"
subsv = ["%d.%d" % (a, b) for a in range(0, 4) for b in range(0, 13)]
family("2 versions [major, minor]", VERS, ["major", "minor"], subsv, [(1, 4), (0, 9), (1, 10), (2, 0)])
for k in sorted(tot):
    print("  %-46s %5d cases, %d differ" % (k, tot[k][0], tot[k][1]))
print("  total: %d cases, %d differ" % (sum(n for n, _ in tot.values()), sum(b for _, b in tot.values())))

# ---------------------------------------------------------------------------------------------------- table (R)
print()
print("(R) rev 16's bundled body vs the decomposed form (author pattern = the same field patterns and separator)")
n = bad = 0
for pats, sep, subs, bounds, P, proj in [
        ([r"\d{1,2}", r"\d\d"], ":", subs2, B2, HM, ["h", "m"]),
        ([r"\d{1,2}", r"\d\d", r"\d\d"], ":", subs3, B3, HMS, ["h", "m", "sec"])]:
    for s in subs:
        for lo in bounds:
            for hi in bounds:
                n += 1
                bad += rev16_between(pats, sep, lo, hi, s) != lex_between(P, proj, lo, hi, s)
print("  %d cases, %d differ" % (n, bad))

# ---------------------------------------------------------------------------------------------------- table (W)
print()
print("(W) the worked rows of §8 (rev 17), each subject matched WHOLE by the filter")


def ex(title, f, rows):
    print("  " + title)
    b = 0
    for s, want in rows:
        got = f(s)
        b += got != want
        print("    %-14r -> %-6s %s" % (s, yn(got), "" if got == want else "  UNEXPECTED (stated %s)" % yn(want)))
    return b


bad = 0
bad += ex('/(?<h>\\d{1,2}):(?<m>\\d\\d)/ & lex_between2([(h:), (m:)], [9, 0], [10, 0])',
          lambda s: lex_between(HM, ["h", "m"], (9, 0), (10, 0), s),
          [("9:00", True), ("09:30", True), ("9:59", True), ("10:00", True),
           ("10:01", False), ("8:59", False), ("11:00", False), ("9:5", False)])
bad += ex('/(?<m>\\d\\d) past (?<h>\\d{1,2})/ & lex_between2([(h:), (m:)], [9, 0], [10, 0])  (labels in the other order)',
          lambda s: lex_between(PAST, ["h", "m"], (9, 0), (10, 0), s),
          [("30 past 9", True), ("00 past 10", True), ("01 past 10", False), ("59 past 8", False)])
bad += ex('/(?<h>\\d{1,2}):(?<m>\\d\\d):(?<sec>\\d\\d)/ & lex_between3([(h:), (m:), (sec:)], [9, 30, 5], [10, 0, 0])',
          lambda s: lex_between(HMS, ["h", "m", "sec"], (9, 30, 5), (10, 0, 0), s),
          [("9:30:05", True), ("09:30:05", True), ("9:59:59", True), ("10:00:00", True),
           ("9:30:04", False), ("10:00:01", False), ("8:59:59", False), ("9:30", False)])
bad += ex('/(?<major>0|[1-9]\\d*)\\.(?<minor>0|[1-9]\\d*)/ & lex_between2([(major:), (minor:)], [1, 4], [1, 10])',
          lambda s: lex_between(VERS, ["major", "minor"], (1, 4), (1, 10), s),
          [("1.4", True), ("1.9", True), ("1.10", True),
           ("1.3", False), ("1.11", False), ("2.0", False), ("0.9", False), ("1.04", False), ("1x4", False)])
SEMVER = r"(?<major>0|[1-9]\d*)\.(?<minor>0|[1-9]\d*)\.(?<patch>0|[1-9]\d*)"
bad += ex('semver & lex_ge3([(major:), (minor:), (patch:)], [1, 4, 0])  (the 2026-11-14 record\'s shape)',
          lambda s: lex_ge(SEMVER, ["major", "minor", "patch"], (1, 4, 0), s),
          [("1.4.0", True), ("1.10.2", True), ("2.0.0", True), ("1.3.99", False), ("0.9.9", False),
           ("1.04.0", False)])
try:
    lex_ge(HM, ["h", "m"], (9, 0, 0), "9:00")
    print("    wrong-length call: NOT refused")
    bad += 1
except ValueError as e:
    print("    wrong-length call lex_ge3([(h:), (m:)], [9, 0, 0]) -> refused:", e)
print("  worked rows not as stated: %d" % bad)
print()
print("engine disagreements: %d" % DISAGREE[0])
