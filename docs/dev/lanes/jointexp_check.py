# jointexp: evidence for docs/design/joint_condition.md (the joint condition `(a, b, ...): R`).
# Engine helpers COPIED from predspec19_check.py (that file is not edited). Every regex verdict is computed by
# libpcre2-8 (ctypes) AND Python `re`, and the two must agree. Expectations are computed in Python from the
# subject's digits as INTEGER tuples (Python's own tuple order), never from the expansion under test.
#
# Claims checked:
# (X) EXPANSION: `(f1..fk): >= (b1..bk)` in dictionary order equals a union of k+0 "rectangles":
#        rect j = f1==b1 & ... & f(j-1)==b(j-1) & fj > bj        (j = 1..k-1)
#        rect k = f1==b1 & ... & f(k-1)==b(k-1) & fk >= bk
#     each rectangle a RECORD of single-label comparison sets (§4 conditions, no new set kind). Strict `>` swaps
#     the last rect's >= for >. `between(lo, hi)` = the intersection of the two halves.  Populations: time h:m,
#     version a.b.c, IPv4 a.b.c.d (sampled), with leading-zero numerals.
# (U) UNSET / OPTIONAL: a tuple with an unset member does not exist; the joint condition is false; its `!` is true
#     (the complement over the match, not over the tuple domain) -- shows the two readings differ.
# (L) LOOPED: `(h, m)` inside a loop pairs per ITERATION; "every item's tuple in R" vs the old per-label
#     sequence rule (each label over all iterations separately) -- shows where they differ.
# (C) CALENDAR: `(y, mo, d): valid_date` as a finite table of rectangles; the expansion vs datetime.
import ctypes, re, itertools, datetime, random, sys

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
L.pcre2_config_8(11, _vb)
print("libpcre2-8", _vb.value.decode(), "| Python", sys.version.split()[0])


def _code(p):
    if p not in _cache:
        e, o = ctypes.c_int(), ctypes.c_size_t()
        c = L.pcre2_compile_8(p.encode(), len(p.encode()), 0, ctypes.byref(e), ctypes.byref(o), None)
        assert c, (p, e.value)
        _cache[p] = c
    return _cache[p]


def py(p):
    return p.replace("(?<", "(?P<").replace("(?P<=", "(?<=").replace("(?P<!", "(?<!")


def whole(p, t):
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


OPS = {">": lambda a, b: a > b, ">=": lambda a, b: a >= b, "<": lambda a, b: a < b, "<=": lambda a, b: a <= b,
       "==": lambda a, b: a == b}


def cset(op, v, top):
    """the single-label comparison set `OP v` over values 0..top-1, leading zeros allowed (padded reading)"""
    vs = [str(x) for x in range(top) if OPS[op](x, v)]
    return "0*(?:" + "|".join(vs) + ")" if vs else "(?!)"


def rects(op, b, tops):
    """dictionary-order `OP b` over a k-tuple as a list of rectangles; each rectangle = list of per-field sets"""
    k = len(b)
    out = []
    lt = op in ("<", "<=")
    for j in range(k):
        last = j == k - 1
        if last:
            fop = op if op != "==" else "=="
        else:
            fop = "<" if lt else ">"
            if op == "==":
                continue
        out.append([cset("==", b[i], tops[i]) for i in range(j)] + [cset(fop, b[j], tops[j])] +
                   [cset(">=", 0, tops[i]) for i in range(j + 1, k)])
    return out


def rect_regex(rs, seps):
    """a union of rectangles laid over the author's field layout f1 sep1 f2 sep2 ... fk"""
    alts = []
    for r in rs:
        s = ""
        for i, fs in enumerate(r):
            s += fs + (re.escape(seps[i]) if i < len(seps) else "")
        alts.append(s)
    return "(?:" + "|".join(alts) + ")"


def inter(p, q):
    return "(?=%s$)%s" % (p, q)          # whole-stretch intersection by lookahead (both engines)


T = {"cases": 0, "differ": 0}


def check(tag, rx, subj, want):
    got = whole(rx, subj)
    T["cases"] += 1
    if got != want:
        T["differ"] += 1
        if T["differ"] < 15:
            print("  DIFFER", tag, repr(subj), "got", got, "want", want)


def nums(s):
    return tuple(int(x) for x in re.split(r"[.:]", s))


# (X) time h:m, all ops, several bounds, every subject h in 0..29 (1-2 digits, with leading zero), m 00..69
seps_t = [":"]
subjects_t = ["%d:%02d" % (h, m) for h in range(30) for m in range(0, 70, 3)] + \
             ["%02d:%02d" % (h, m) for h in range(0, 30, 4) for m in range(0, 70, 7)] + ["009:05", "9:5", "9:005"]
before = T["cases"]
for b in [(9, 0), (9, 30), (0, 0), (23, 59), (10, 5)]:
    for op in OPS:
        rx = rect_regex(rects(op, b, (100, 100)), seps_t)
        nr = len(rects(op, b, (100, 100)))
        assert nr == (1 if op == "==" else 2)
        for s in subjects_t:
            check("time%s%s" % (op, b), rx, s, OPS[op](nums(s), b))
for lo, hi in [((9, 0), (10, 0)), ((9, 30), (17, 15)), ((12, 0), (12, 0))]:
    rx = inter(rect_regex(rects(">=", lo, (100, 100)), seps_t), rect_regex(rects("<=", hi, (100, 100)), seps_t))
    for s in subjects_t:
        check("between", rx, s, lo <= nums(s) <= hi)
print("(X) time h:m  cases %d" % (T["cases"] - before))

# version a.b.c >= 1.4.0 and > 1.4.0, IPv4 inside a range
before = T["cases"]
vsub = ["%d.%d.%d" % t for t in itertools.product(range(0, 4), range(0, 12), range(0, 12))] + ["1.04.0", "01.4.00"]
for op in (">=", ">", "<"):
    rx = rect_regex(rects(op, (1, 4, 0), (20, 20, 20)), [".", "."])
    assert len(rects(op, (1, 4, 0), (20, 20, 20))) == 3
    for s in vsub:
        check("ver" + op, rx, s, OPS[op](nums(s), (1, 4, 0)))
print("(X) version   cases %d" % (T["cases"] - before))
before = T["cases"]
random.seed(7)
lo, hi = (10, 1, 128, 0), (10, 1, 131, 255)
ipsub = ["%d.%d.%d.%d" % (10, 1, c, d) for c in range(126, 134) for d in (0, 1, 7, 99, 200, 255)] + \
        ["%d.%d.%d.%d" % tuple(random.randrange(256) for _ in range(4)) for _ in range(150)] + \
        ["10.0.255.255", "10.2.0.0", "11.1.130.5", "9.1.130.5"]
rx = inter(rect_regex(rects(">=", lo, (256,) * 4), [".", ".", "."]),
           rect_regex(rects("<=", hi, (256,) * 4), [".", ".", "."]))
for s in ipsub:
    check("ipv4", rx, s, lo <= nums(s) <= hi)
print("(X) ipv4      cases %d" % (T["cases"] - before))

# (U) optional seconds: pattern h:m(:s)?  joint (h, m, s): >= (9, 0, 30). s unset -> no tuple -> false.
before = T["cases"]
P = r"(?<h>\d{1,2}):(?<m>\d\d)(?::(?<s>\d\d))?"
usub = ["9:00", "9:00:29", "9:00:30", "10:00", "10:00:00", "8:59:59", "9:01"]
expect_joint = {}
for s in usub:
    mm = re.fullmatch(py(P), s)
    t = mm.group("h", "m", "s")
    exists = all(x is not None for x in t)
    want = exists and tuple(map(int, t)) >= (9, 0, 30)
    # the rectangle expansion read with s OPTIONAL in the author's pattern: rectangles require the field present
    rx = rect_regex(rects(">=", (9, 0, 30), (100, 100, 100)), [":", ":"])
    check("optional", rx, s, want)
    expect_joint[s] = (want, not want)
print("(U) optional  cases %d   joint / its ! per subject:" % (T["cases"] - before))
for s, (j, n) in expect_joint.items():
    print("     %-9s joint=%-5s !joint=%-5s" % (s, j, n))

# (L) looped: (?:(?<h>\d{1,2}):(?<m>\d\d),)*  "every item's (h,m) >= (9,30)"
before = T["cases"]
item = r"(?<h>\d{1,2}):(?<m>\d\d),"
item_rx = rect_regex(rects(">=", (9, 30), (100, 100)), [":"]) + ","
loop_rx = "(?:" + item_rx + ")*"
lsub = ["", "9:30,", "9:45,", "10:00,9:30,", "9:29,", "10:00,9:29,", "10:15,9:45,", "10:45,9:35,", "11:00,10:00,", "8:30,10:00,"]
ndiff_seq = 0
for s in lsub:
    its = [tuple(map(int, (m.group("h"), m.group("m")))) for m in re.finditer(py(item), s)]
    want = all(t >= (9, 30) for t in its)
    check("looped", loop_rx, s, want)
    # the OLD reading by the per-label sequence rule: every h >= 9 AND every m >= 0 is NOT the tuple compare;
    # the negation-built per-label form of rev 17-19 reads over all iterations of each label separately:
    hs = [t[0] for t in its]; ms = [t[1] for t in its]
    seq = all(x > 9 for x in hs) or (all(x == 9 for x in hs) and all(x >= 30 for x in ms))
    if seq != want:
        ndiff_seq += 1
        print("     looped %-14r per-item=%s  per-label-sequence=%s" % (s, want, seq))
print("(L) looped    cases %d   per-label sequence reading differs on %d" % (T["cases"] - before, ndiff_seq))

# (C) calendar: (y, mo, d) valid date, y 1900..2099 represented by a leap table; rectangles counted.
before = T["cases"]
def dim(y, m):
    return (datetime.date(y + (m == 12), m % 12 + 1, 1) - datetime.timedelta(days=1)).day
leap4 = "(?:[02468][048]|[13579][26])"
yleap = "(?:19|20)" + leap4 + "|2000"           # 1900 is not leap: 19 + 00 excluded since 00 matches [02468][048]
yleap = "(?:19(?!00)%s|20%s)" % (leap4, leap4)
yany = r"(?:19|20)\d\d"
def drange(n):
    return r"(?:0?[1-9]|[12]\d|3[01])" if n == 31 else "(?:" + "|".join(["0?%d" % i for i in range(1, 10)] + [str(i) for i in range(10, n + 1)]) + ")"
rows = []
for mo in range(1, 13):
    mos = "0?%d" % mo if mo < 10 else str(mo)
    if mo == 2:
        rows.append(yany + "-" + mos + "-" + drange(28))
        rows.append(yleap + "-" + mos + "-29")
    else:
        rows.append(yany + "-" + mos + "-" + drange(dim(2001, mo)))
cal = "(?:" + "|".join(rows) + ")"
print("(C) calendar rectangles:", len(rows))
csub = ["%d-%02d-%02d" % (y, m, d) for y in (1900, 1996, 2000, 2023, 2024, 2100 - 1) for m in range(1, 13)
        for d in (1, 28, 29, 30, 31, 32)]
for s in csub:
    y, m, d = map(int, s.split("-"))
    try:
        datetime.date(y, m, d); want = True
    except ValueError:
        want = False
    check("calendar", cal, s, want)
print("(C) calendar  cases %d" % (T["cases"] - before))

print("TOTAL cases %d differ %d engine-disagreements %d" % (T["cases"], T["differ"], DISAGREE[0]))
