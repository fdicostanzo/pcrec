# tupleval2: evidence for docs/design/joint_condition.md §4A.3 (taking a tuple apart) and §4A.11 (first/rest
# binding with recursion). Engine helpers COPIED from tupleval_check.py (that file is not edited). Every regex verdict
# is computed by libpcre2-8 (ctypes) AND Python `re`, and the two must agree. Expectations are computed
# INDEPENDENTLY of the regex under test: Python integer tuples (Python's own tuple order) and plain set arithmetic.
#
# Claims checked (tables cited in the note as (F), (FS), (A)):
# (F)  DICTIONARY ORDER AS A LIBRARY DEFINITION BY FIRST/REST: the clauses of §4A.11, run by a small interpreter
#      that follows them as written (first-match clause selection by head shape; `(b, r...)` takes a tuple apart
#      into its first entry and the rest, the rest of a pair being the plain second entry; `(x, y...)` on the value
#      side builds the product of x and y's components), expand to sets of k-tuples whose regex, laid over a
#      dotted-numeral operand, answers EXACTLY Python's integer tuple order, for k = 2, 3, 4 and the operators
#      at-least, strictly-greater, at-most, strictly-less and between. Row counts printed (k rows per order).
# (FS) THE SLIPS: the three ways to write the library wrong (the plain clause first; the rest used without
#      spreading; a recursive call on the whole instead of the rest) are each REFUSED at compile time by an
#      existing or proposed rule (a tuple atom in a one-value comparison; a nested tuple entry; the termination
#      check), never a silent different answer. Counted per k.
# (A)  TAKING A SET APART: `(a, b) := T` gives back T on a round trip `(a, b)` exactly when T is the product of its
#      parts; the test is on the SET, not its spelling (`[(1, 2), (1, 3)]` IS a product; `month_days` is not).
import ctypes, re, itertools, sys

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


def whole(p, t):
    c = _code(p)
    md = L.pcre2_match_data_create_from_pattern_8(c, None)
    rc = L.pcre2_match_8(c, t.encode(), len(t.encode()), 0, ANCH | ENDANCH, md, None)
    L.pcre2_match_data_free_8(md)
    a = rc >= 0
    b = re.fullmatch(p, t) is not None
    if a != b:
        DISAGREE[0] += 1
        print("  ENGINE DISAGREEMENT", repr(p), repr(t), a, b)
    return a


T = {"cases": 0, "differ": 0}


def check(tag, rx, subj, want):
    got = whole(rx, subj)
    T["cases"] += 1
    if got != want:
        T["differ"] += 1
        if T["differ"] < 15:
            print("  DIFFER", tag, repr(subj), "got", got, "want", want)
    return got


# ---------------------------------------------------------------------------------------------------------------
# The interpreter for §4A.11's clauses. A VALUE is either a plain bound (an int: arity 1) or a Python tuple of
# plain bounds (arity k >= 2). A SET of k-tuples is a list of ROWS (a finite union of products); a row is a tuple of
# k COMPONENT sets; a component is ("cmp", op, n) (the existing single-value comparison set `op n`) or ("any",).
class CompileError(Exception):
    pass


def arity(v):
    return len(v) if isinstance(v, tuple) else 1


def take_apart(v):
    """the head `(b, r...)`: first entry and the rest; the rest of a pair is its plain second entry (4A.2: (x) is x)"""
    assert isinstance(v, tuple) and len(v) >= 2
    rest = v[1:]
    return v[0], (rest[0] if len(rest) == 1 else rest)


def as_rows(s):
    """an arity-1 component set used where a set is expected: one row of one component"""
    return s if isinstance(s, list) else [(s,)]


def build(first, rest_rows, spread=True):
    """the value side `(first, rest...)`: the product of the arity-1 set `first` and every row of `rest`.
    Without the spread mark, `(first, rest)` with a rest of arity >= 2 is a NESTED tuple entry: an error (4A.2)."""
    rows = as_rows(rest_rows)
    if not spread and any(len(r) >= 2 for r in rows):
        raise CompileError("a tuple entry is one field (nested tuple)")
    return [(first,) + r for r in rows]


def cmp_one(op, b):
    """the existing comparison set `op b`: ONE atom, one value (§2.4). A tuple atom is refused under §4A.11."""
    if isinstance(b, tuple):
        raise CompileError("a comparison takes one value; for a tuple use the library order")
    return ("cmp", op, b)


DEPTH = {"calls": 0}


def call(name, v, caller_arity=None):
    """run a library definition by first-match clause selection; the termination rule: a recursive call's argument
    has a strictly smaller arity than its caller's"""
    if caller_arity is not None and arity(v) >= caller_arity:
        raise CompileError("recursion does not take a rest: %s" % name)
    DEPTH["calls"] += 1
    for shape, body in LIB[name]:
        if shape == "tuple" and arity(v) >= 2:
            return body(v)
        if shape == "plain":
            return body(v)
    raise CompileError("no clause")


def any_rows(v):
    return call("all", v)


def mk_order(strict_op, last_op, name):
    """ge/gt/le/lt as written in §4A.11:
         name(b)         := last_op b
         name((b, r...)) := (strict_op b, all(r)...) | (== b, name(r)...)"""
    def tuple_clause(v):
        b, r = take_apart(v)
        return build(cmp_one(strict_op, b), call("all", r, arity(v))) + \
            build(cmp_one("==", b), call(name, r, arity(v)))
    return [("tuple", tuple_clause), ("plain", lambda v: [(cmp_one(last_op, v),)])]


LIB = {
    "all": [("tuple", lambda v: build(("any",), call("all", take_apart(v)[1], arity(v)))),
            ("plain", lambda v: [(("any",),)])],
    "ge": mk_order(">", ">=", "ge"),
    "gt": mk_order(">", ">", "gt"),
    "le": mk_order("<", "<=", "le"),
    "lt": mk_order("<", "<", "lt"),
}

OPS = {">": lambda a, b: a > b, ">=": lambda a, b: a >= b, "<": lambda a, b: a < b, "<=": lambda a, b: a <= b,
       "==": lambda a, b: a == b}


def comp_rx(c, top, pad):
    """a component's regex over the canonical numerals 0..top-1 (pad: leading zeros allowed, the `padded` reading)"""
    if c[0] == "any":
        return r"\d+"
    _, op, n = c
    vs = [str(x) for x in range(top) if OPS[op](x, n)]
    if not vs:
        return "(?!)"
    return ("0*" if pad else "") + "(?:" + "|".join(vs) + ")"


def rows_rx(rows, top, pad):
    return "(?:" + "|".join(r"\.".join(comp_rx(c, top, pad) for c in r) for r in rows) + ")"


def inter(p, q):
    return "(?=%s$)%s" % (p, q)


PYORD = {"ge": lambda t, b: t >= b, "gt": lambda t, b: t > b, "le": lambda t, b: t <= b, "lt": lambda t, b: t < b}

# ---------------------------------------------------------------------------------------------------------------
# (F) the library order against Python's integer tuple order.
CONF = {2: (15, [(0, 0), (3, 7), (14, 14), (7, 0), (0, 14)], [((3, 7), (9, 2)), ((0, 0), (0, 0)), ((5, 5), (4, 4))]),
        3: (8, [(0, 0, 0), (3, 7, 1), (7, 7, 7), (4, 0, 6), (1, 6, 0)], [((2, 3, 4), (5, 1, 0)), ((3, 3, 3), (3, 3, 5)),
                                                                       ((6, 0, 0), (2, 0, 0))]),
        4: (6, [(0, 0, 0, 0), (2, 5, 1, 3), (5, 5, 5, 5), (3, 0, 4, 0)], [((1, 2, 3, 4), (4, 3, 2, 1)),
                                                                        ((2, 2, 2, 2), (2, 2, 3, 0))])}
for k, (top, bounds, ranges) in sorted(CONF.items()):
    before = T["cases"]
    subj = [".".join(map(str, t)) for t in itertools.product(range(top), repeat=k)]
    operand = r"\.".join([r"\d+"] * k)
    nrows = set()
    for b in bounds:
        for name in ("ge", "gt", "le", "lt"):
            rows = call(name, b)
            nrows.add(len(rows))
            rx = inter(operand, rows_rx(rows, top, False))
            for s in subj:
                t = tuple(map(int, s.split(".")))
                check("F-%s-%d" % (name, k), rx, s, PYORD[name](t, b))
    for lo, hi in ranges:                                    # between(lo, hi) := ge(lo) & le(hi), the macro unchanged
        rx = inter(operand, inter(rows_rx(call("ge", lo), top, False), rows_rx(call("le", hi), top, False)))
        for s in subj:
            t = tuple(map(int, s.split(".")))
            check("F-between-%d" % k, rx, s, lo <= t <= hi)
    print("(F) k=%d: %d subjects, %d bounds x 4 orders + %d betweens; rows per order %s; cases %d"
          % (k, len(subj), len(bounds), len(ranges), sorted(nrows), T["cases"] - before))

# padded components (leading zeros in the subject), k = 2: the library writes `padded` into each component it builds
before = T["cases"]
psubj = ["%d.%d" % t for t in itertools.product(range(15), repeat=2)] + \
        ["%02d.%02d" % t for t in itertools.product(range(15), repeat=2)]
for b in [(3, 7), (9, 0)]:
    for name in ("ge", "gt"):
        rx = inter(r"\d+\.\d+", rows_rx(call(name, b), 15, True))
        for s in psubj:
            t = tuple(map(int, s.split(".")))
            check("F-padded", rx, s, PYORD[name](t, b))
print("(F) k=2 padded components: %d subjects (canonical and two-digit), cases %d" % (len(psubj), T["cases"] - before))

# ---------------------------------------------------------------------------------------------------------------
# (FS) the three slips, each refused at compile time (counted per k), never a silent different answer.
SAVED = dict(LIB)


def slip_plain_first():
    for n in ("ge",):
        LIB[n] = list(reversed(SAVED[n]))


def slip_no_spread():
    def tuple_clause(v):
        b, r = take_apart(v)
        return build(cmp_one(">", b), call("all", r, arity(v)), spread=False) + \
            build(cmp_one("==", b), call("ge", r, arity(v)), spread=False)
    LIB["ge"] = [("tuple", tuple_clause), SAVED["ge"][1]]


def slip_whole():
    def tuple_clause(v):
        b, r = take_apart(v)
        return build(cmp_one(">", b), call("all", r, arity(v))) + build(cmp_one("==", b), call("ge", v, arity(v)))
    LIB["ge"] = [("tuple", tuple_clause), SAVED["ge"][1]]


for label, slip in (("plain clause first", slip_plain_first), ("rest without spread", slip_no_spread),
                    ("recursion on the whole", slip_whole)):
    slip()
    out = []
    for k in (2, 3, 4):
        try:
            call("ge", tuple(range(1, k + 1)))
            out.append("k=%d ACCEPTED" % k)
        except CompileError as e:
            out.append("k=%d refused (%s)" % (k, e))
    LIB.update(SAVED)
    print("(FS) %-24s %s" % (label + ":", "; ".join(out)))

# ---------------------------------------------------------------------------------------------------------------
# (A) taking a SET apart: the round trip is exact iff the set is the product of its parts (Python set arithmetic).
def parts_round_trip(S):
    p1 = {a for a, _ in S}
    p2 = {b for _, b in S}
    back = {(a, b) for a in p1 for b in p2}
    return back == S, len(S), len(back)


month_days = {(m, d) for ms, ds in [([1, 3, 5, 7, 8, 10, 12], range(1, 32)), ([4, 6, 9, 11], range(1, 31)),
                                    ([2], range(1, 29))] for m in ms for d in ds}
CASES_A = [
    ("(9, 0)", {(9, 0)}),
    ("(padded(between(1, 12)), padded(between(1, 28)))", {(m, d) for m in range(1, 13) for d in range(1, 29)}),
    ("[(1, 2), (1, 3)]  (spelled as an array, a product)", {(1, 2), (1, 3)}),
    ("[(9, 0), (17, 30)]", {(9, 0), (17, 30)}),
    ("month_days", month_days),
    (">= (9, 30) over hours 0..23, minutes 0..59", {(h, m) for h in range(24) for m in range(60) if (h, m) >= (9, 30)}),
]
for label, S in CASES_A:
    ok, n, nb = parts_round_trip(S)
    print("(A) %-52s %-5s set %4d pairs, parts give back %4d" % (label, "EXACT" if ok else "LOSES", n, nb))

print("TOTAL cases %d differ %d engine-disagreements %d" % (T["cases"], T["differ"], DISAGREE[0]))
