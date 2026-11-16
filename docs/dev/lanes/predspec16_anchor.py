# predspec16: evidence for predicates_draft.md rev 16 (the owner's three rulings of 2026-11-15 21:50/21:54: the
# tuple compare joins the first library; `json.quoted` is cut; `any_case` stays a primitive for now). The evidence
# script continued from predspec15_anchor.py (its engine helpers copied verbatim). Every regex verdict is computed by
# libpcre2-8 (public API, ctypes) AND Python `re`; every row asserts the two engines agree (0 disagreements expected).
#
# (F) THE TUPLE FAMILY of the first library (§8 TUPLE COMPARISONS): for 2 and 3 fields, `..._between`,
#     `..._at_least`, `..._at_most` with the bodies of rev 15's O69 sketch, every comparison padded. A body is
#     emulated as written: the field pattern `/(?<t1>${a})${sep}(?<t2>${b})/` matched WHOLE on the stretch (a hole of a
#     string inserts the string as literal text, so `${"."}` is `\.`), then each bound's `[ ]` of condition records
#     (any one entry; a record = all its conditions), each condition `(tk: padded(cmp))` = the label's text matched
#     whole by `0*(?:SET)` where SET is the comparison set's canonical numerals. Truth = integer lexicographic order
#     of the parsed fields. Also the strict comparisons and equality derived by `!` and `&` (the library does not
#     carry them): `fields & !at_most(lo)` = strictly above lo, `fields & !at_least(hi)` = strictly below hi,
#     `between(lo, lo)` = equal.
# (X) the worked examples of §8 with their rows: the time range 9:00..10:00, an h:m:s range 9:30:05..10:00:00, a
#     version range 1.4..1.10 (with canonical-number fields and with `\d+` fields), and the contrasts: a string
#     `between("1.4", "1.10")` (empty: "1.4" > "1.10" as strings) and a separator written as rx text `/./`.
# (J) E-JSONL rewritten without `json.quoted` (cut): `quoted(S)` (the library body, §2.7) for ts and level and
#     `json.string & contains("timeout")` for msg, against the cut transform's meaning (S tested on the DECODED
#     string), on member value texts; then the three §12.1 subject lines end to end (a flat object's members
#     extracted, `row(k, v)` = ANY member with key k whose value text v accepts, the case's stated semantics).
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


# ---------------------------------------------------------------------------------------------------- table (F)
print()
print("(F) the tuple family (2 and 3 fields; between / at_least / at_most), bodies as written, vs integer lex order")


def canon(pred, top=130):
    vs = [str(v) for v in range(top) if pred(v)]
    return "(?:" + "|".join(vs) + ")" if vs else "(?!)"


def padded(pred):
    return "0*(?:%s)" % canon(pred)


def fields(pats, sep, s, sep_is_rx=False):
    """the body's field pattern /(?<t1>${a})${sep}(?<t2>${b})[${sep}(?<t3>${c})]/ matched whole on s; the labels"""
    sp = sep if sep_is_rx else re.escape(sep)
    p = sp.join("(?<t%d>(?:%s))" % (i + 1, a) for i, a in enumerate(pats))
    ok = whole(p, s)
    m = re.fullmatch(py(p), s)
    assert (m is not None) == ok
    return [m.group("t%d" % (i + 1)) for i in range(len(pats))] if ok else None


def bound(t, b, strict, last):
    """one bound's `[ ]` of records: (t1: padded(strict b1)) | (t1: padded(==b1), t2: padded(strict b2)) | ..."""
    for k in range(len(b)):
        rec = [(i, padded(lambda v, i=i: v == b[i])) for i in range(k)]
        rec.append((k, padded(lambda v, k=k: (last if k == len(b) - 1 else strict)(v, b[k]))))
        if all(whole(rx, t[i]) for i, rx in rec):
            return True
    return False


GE = (lambda a, b: a > b, lambda a, b: a >= b)
LE = (lambda a, b: a < b, lambda a, b: a <= b)


def at_least(pats, sep, lo, s, **kw):
    t = fields(pats, sep, s, **kw)
    return t is not None and bound(t, lo, *GE)


def at_most(pats, sep, hi, s, **kw):
    t = fields(pats, sep, s, **kw)
    return t is not None and bound(t, hi, *LE)


def between(pats, sep, lo, hi, s, **kw):
    t = fields(pats, sep, s, **kw)
    return t is not None and bound(t, lo, *GE) and bound(t, hi, *LE)


def ints(s, sep):
    return tuple(int(x) for x in s.split(sep))


H2 = [r"\d{1,2}", r"\d\d"]
H3 = [r"\d{1,2}", r"\d\d", r"\d\d"]
subs2 = ["%s:%s" % (a, b) for a in [str(i) for i in range(13)] + ["%02d" % i for i in range(10)]
         for b in ["%02d" % j for j in (0, 1, 29, 30, 31, 59)]]
subs3 = ["%s:%s:%s" % (a, b, c) for a in ["9", "09", "10", "8", "08", "0", "00", "11"] for b in ["29", "30", "31", "00"]
         for c in ["00", "04", "05", "06", "59"]]
B2 = [(9, 0), (9, 30), (0, 0), (5, 1), (10, 0), (12, 59)]
B3 = [(9, 30, 5), (0, 0, 0), (10, 0, 0), (9, 30, 6)]
tot = {}


def tally(key, got, want):
    n, bad = tot.get(key, (0, 0))
    tot[key] = (n + 1, bad + (got != want))


for s in subs2:
    v = ints(s, ":")
    for lo in B2:
        tally("2 fields  at_least", at_least(H2, ":", lo, s), v >= lo)
        tally("2 fields  at_most", at_most(H2, ":", lo, s), v <= lo)
        f = fields(H2, ":", s) is not None
        tally("2 fields  above  = fields & !at_most", f and not at_most(H2, ":", lo, s), v > lo)
        tally("2 fields  below  = fields & !at_least", f and not at_least(H2, ":", lo, s), v < lo)
        tally("2 fields  equal  = between(lo, lo)", between(H2, ":", lo, lo, s), v == lo)
        for hi in B2:
            tally("2 fields  between", between(H2, ":", lo, hi, s), lo <= v <= hi)
for s in subs3:
    v = ints(s, ":")
    for lo in B3:
        tally("3 fields  at_least", at_least(H3, ":", lo, s), v >= lo)
        tally("3 fields  at_most", at_most(H3, ":", lo, s), v <= lo)
        f = fields(H3, ":", s) is not None
        tally("3 fields  above  = fields & !at_most", f and not at_most(H3, ":", lo, s), v > lo)
        tally("3 fields  below  = fields & !at_least", f and not at_least(H3, ":", lo, s), v < lo)
        tally("3 fields  equal  = between(lo, lo)", between(H3, ":", lo, lo, s), v == lo)
        for hi in B3:
            tally("3 fields  between", between(H3, ":", lo, hi, s), lo <= v <= hi)
# versions: canonical-number fields (no leading zero), 2 fields
VN = r"0|[1-9]\d*"
subsv = ["%d.%d" % (a, b) for a in range(0, 4) for b in range(0, 13)]
for s in subsv:
    v = ints(s, ".")
    for lo in [(1, 4), (0, 9), (1, 10)]:
        for hi in [(1, 10), (2, 0), (1, 4)]:
            tally("2 fields  between (versions, sep '.')", between([VN, VN], ".", lo, hi, s), lo <= v <= hi)
for k in sorted(tot):
    print("  %-42s %5d cases, %d differ" % (k, tot[k][0], tot[k][1]))
print("  total: %d cases, %d differ" % (sum(n for n, _ in tot.values()), sum(b for _, b in tot.values())))

# ---------------------------------------------------------------------------------------------------- table (X)
print()
print("(X) the worked examples (§8): each subject matched WHOLE by the filter")


def ex(title, f, rows):
    print("  " + title)
    bad = 0
    for s, want in rows:
        got = f(s)
        bad += got != want
        print("    %-12r -> %-6s %s" % (s, yn(got), "" if got == want else "  UNEXPECTED (stated %s)" % yn(want)))
    return bad


bad = 0
bad += ex('pair_between(/\\d{1,2}/, ":", /\\d\\d/, 9, 0, 10, 0)   (the time range 9:00 to 10:00)',
          lambda s: between(H2, ":", (9, 0), (10, 0), s),
          [("9:00", True), ("09:30", True), ("9:59", True), ("10:00", True),
           ("10:01", False), ("8:59", False), ("11:00", False), ("9:5", False)])
bad += ex('triple_between(/\\d{1,2}/, ":", /\\d\\d/, /\\d\\d/, 9, 30, 5, 10, 0, 0)   (h:m:s, 9:30:05 to 10:00:00)',
          lambda s: between(H3, ":", (9, 30, 5), (10, 0, 0), s),
          [("9:30:05", True), ("09:30:05", True), ("9:59:59", True), ("10:00:00", True),
           ("9:30:04", False), ("10:00:01", False), ("8:59:59", False), ("9:30", False)])
bad += ex('pair_between(/0|[1-9]\\d*/, ".", /0|[1-9]\\d*/, 1, 4, 1, 10)   (versions 1.4 to 1.10)',
          lambda s: between([VN, VN], ".", (1, 4), (1, 10), s),
          [("1.4", True), ("1.9", True), ("1.10", True),
           ("1.3", False), ("1.11", False), ("2.0", False), ("0.9", False), ("1.04", False), ("1x4", False)])
bad += ex('pair_between(/\\d+/, ".", /\\d+/, 1, 4, 1, 10)   (the same with \\d+ fields: padded reads 1.04 as 1.4)',
          lambda s: between([r"\d+", r"\d+"], ".", (1, 4), (1, 10), s),
          [("1.04", True), ("01.10", True), ("1.010", True), ("1.011", False)])
bad += ex('contrast: the separator as rx text /./ instead of the string "." (accepts 1x4)',
          lambda s: between([VN, VN], ".", (1, 4), (1, 10), s, sep_is_rx=True),
          [("1.4", True), ("1x4", True)])
print("    contrast: a STRING range between(\"1.4\", \"1.10\") (the language's string order, Python str compare):",
      "\"1.4\" <= \"1.10\" is", "1.4" <= "1.10", "-> the set is EMPTY;",
      "and between(\"1.4\", \"1.9\") accepts", [s for s in ["1.4", "1.5", "1.9", "1.10", "1.45"] if "1.4" <= s <= "1.9"])
print("  worked rows not as stated: %d" % bad)

# ---------------------------------------------------------------------------------------------------- table (J)
print()
print("(J) E-JSONL without json.quoted: the rewrite's value filters vs the cut transform's meaning (S on the DECODED string)")
JSTRING = r'"(?:[^"\\\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*"'
ISODATE = r"\d{4}-\d{2}-\d{2}"
CONTAINS_TIMEOUT = r"(?s:.*?)(?:timeout)(?s:.*)"


def ts_S(x):        # dates.isodate & between("2024-01-01", "2024-03-31"), strings compared as strings
    return whole(ISODATE, x) and "2024-01-01" <= x <= "2024-03-31"


def level_S(x):     # "error"
    return whole("error", x)


def msg_S(x):       # contains("timeout")
    return whole(CONTAINS_TIMEOUT, x)


def quoted(S, v):   # quoted(S) := /"${S & /[^"]*/}"/  (§2.7 bodies table)
    return whole(r'"[^"]*"', v) and whole(r"[^\"]*", v[1:-1]) and S(v[1:-1])


def rewrite(key, v):
    if key == "ts":
        return quoted(ts_S, v)
    if key == "level":
        return quoted(level_S, v)
    return whole(JSTRING, v) and msg_S(v)        # json.string & contains("timeout"): the RAW literal text


def cut_meaning(key, v):
    if not whole(JSTRING, v):
        return False
    d = json.loads(v)
    return {"ts": ts_S, "level": level_S, "msg": msg_S}[key](d)


U = "\\" + "u"                                  # a JSON \u escape, spelled so no tool decodes it
VALS = [("ts", r'"2024-02-10"'), ("ts", r'"2024-05-01"'), ("ts", '"2024' + U + '002d02-10"'),
        ("level", r'"error"'), ("level", '"err' + U + '006fr"'), ("level", r'"warn"'),
        ("msg", r'"db timeout"'), ("msg", r'"timeout"'), ("msg", r'"db \"pool\" timeout"'),
        ("msg", '"time' + U + '006fut"'), ("msg", r'"x\timeout"'), ("msg", r'"no news"')]
ndiff = 0
for k, v in VALS:
    a, b = rewrite(k, v), cut_meaning(k, v)
    ndiff += a != b
    print("  %-5s %-24s rewrite: %-6s cut json.quoted: %-6s %s" % (k, v, yn(a), yn(b),
          "same" if a == b else "DIFFERS (raw text vs decoded)"))
print("  value rows that differ: %d of %d (each is an escape: the rewrite reads the raw text)" % (ndiff, len(VALS)))

MEMBER = re.compile(r'\s*"((?:[^"\\]|\\.)*)"\s*:\s*("(?:[^"\\]|\\.)*"|[^,}]+?)\s*(?:,|\}$)')


def members(line):
    assert line.startswith("{") and line.endswith("}")
    return [(m.group(1), m.group(2)) for m in MEMBER.finditer(line[1:])]


def program(line, f):
    ms = members(line)
    return all(any(k == key and f(key, v) for k, v in ms) for key in ("ts", "level", "msg"))


print("  the §12.1 subject lines (row(k, v) = ANY member with key k whose value text v accepts):")
for line, want in [('{"ts":"2024-02-10","level":"error","msg":"db timeout"}', True),
                   ('{"msg":"timeout","level":"error","ts":"2024-02-10"}', True),
                   ('{"ts":"2024-05-01","level":"error","msg":"timeout"}', False),
                   ('{"ts":"2024-02-10","level":"error","msg":"db \\"pool\\" timeout"}', True)]:
    a, b = program(line, rewrite), program(line, cut_meaning)
    print("    %-62s rewrite: %-8s cut form: %-8s %s" % (line, "match" if a else "no match", "match" if b else "no match",
          "(stated: %s)" % ("match" if want else "no match") if a == want else "UNEXPECTED"))

print()
print("engine disagreements (libpcre2-8 vs Python re): %d" % DISAGREE[0])
