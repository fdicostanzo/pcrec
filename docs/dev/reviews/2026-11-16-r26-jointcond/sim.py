# simulate lens: an evaluator of the joint condition written from the NOTE'S TEXT ONLY
# (J1-J9, §4B.1, J7 zero-pass wording, item 4, item 5, item 7 expansion, LEVEL).
# Engines: libpcre2-8 (whole-span parse, ANCHORED|ENDANCHORED, as draft §4.5) and
# Python re (per-pass enumeration by matching the loop item one at a time).
import ctypes, re, itertools, sys

pc = ctypes.CDLL("libpcre2-8.so.0")
pc.pcre2_compile_8.restype = ctypes.c_void_p
pc.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
                               ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
pc.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
pc.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
pc.pcre2_match_8.restype = ctypes.c_int
pc.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t,
                             ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
pc.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
pc.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
pc.pcre2_substring_number_from_name_8.restype = ctypes.c_int
pc.pcre2_substring_number_from_name_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
ANCH, ENDANCH = 0x80000000, 0x20000000
UNSET = ctypes.c_size_t(-1).value

class PCRE:
    def __init__(self, pat):
        e = ctypes.c_int(); off = ctypes.c_size_t()
        b = pat.encode()
        self.code = pc.pcre2_compile_8(b, len(b), 0, ctypes.byref(e), ctypes.byref(off), None)
        assert self.code, (pat, e.value)
        self.md = pc.pcre2_match_data_create_from_pattern_8(self.code, None)
    def whole(self, s, names):
        b = s.encode()
        r = pc.pcre2_match_8(self.code, b, len(b), 0, ANCH | ENDANCH, self.md, None)
        if r < 0:
            return None
        ov = pc.pcre2_get_ovector_pointer_8(self.md)
        out = {}
        for n in names:
            g = pc.pcre2_substring_number_from_name_8(self.code, n.encode())
            if g < 0 or g >= r and False:
                out[n] = None; continue
            a, z = ov[2 * g], ov[2 * g + 1]
            out[n] = None if a == UNSET else s[a:z]
        return out

EMPTY = object()   # a looped part on zero passes (J7 manager's wording)

# ---------- sets of k-tuples, from the note's text ----------
CANON = re.compile(r"0|[1-9][0-9]*\Z")
def canon(x):
    return isinstance(x, str) and bool(re.fullmatch(r"0|[1-9][0-9]*", x))

class Arity1:
    """an arity-1 set given by a predicate on one string"""
    def __init__(self, pred, name): self.pred, self.name = pred, name
    def has(self, s): return self.pred(s)

def cmpset(op, b):           # §2.4: canonical numerals compared with literal b
    f = {"<": lambda v: v < b, "<=": lambda v: v <= b, ">": lambda v: v > b,
         ">=": lambda v: v >= b, "==": lambda v: v == b}[op]
    return Arity1(lambda s: canon(s) and f(int(s)), f"{op}{b}")
def lit(t): return Arity1(lambda s: s == t, repr(t))
def oneof(*ts): return Arity1(lambda s: s in ts, "|".join(ts))
ANY = Arity1(lambda s: True, "any")
def padded1(S):              # padded(rx) := /0*${rx}/
    return Arity1(lambda s: S.has(re.sub(r"\A0+(?=.)", "", s)) or S.has(s) or
                  any(S.has(s[i:]) for i in range(len(s)) if s[:i] == "0" * i), "padded")

class TupleSet:
    product = False
    def has(self, t): raise NotImplementedError

class Product(TupleSet):     # (S1, ..., Sk): J3 producer (1)
    product = True
    def __init__(self, *parts): self.parts = parts
    def has(self, t): return all(p.has(x) for p, x in zip(self.parts, t))

class Union(TupleSet):
    def __init__(self, *xs): self.xs = xs
    def has(self, t): return any(x.has(t) for x in self.xs)

class Inter(TupleSet):
    def __init__(self, *xs): self.xs = xs
    def has(self, t): return all(x.has(t) for x in self.xs)

class Dict(TupleSet):
    """op (b1..bk), dictionary order. reading EXP: item 7's expansion (row j: equal
    prefix, fj op' bj, REMAINING FIELDS UNCONSTRAINED). reading DOM: every component
    in its comparison domain (item 3: a non-numeric component 'lies outside every
    numeric comparison set'; item 4: 'the comparison set holds CANONICAL numerals per
    component')."""
    def __init__(self, op, bs, reading, pad=False):
        self.op, self.bs, self.reading, self.pad = op, bs, reading, pad
    def val(self, s):
        if self.pad and isinstance(s, str) and re.fullmatch(r"0*(0|[1-9][0-9]*)", s):
            s = re.sub(r"\A0+(?=.)", "", s)
        return int(s) if canon(s) else None
    def has(self, t):
        vs = [self.val(x) for x in t]
        if self.reading == "DOM" and any(v is None for v in vs):
            return False
        # EXP: walk the rows; a field is read only when the prefix is equal
        for j, b in enumerate(self.bs):
            v = vs[j]
            if v is None:
                return False           # the deciding field must be a numeral in both readings
            last = j == len(self.bs) - 1
            if v == b:
                if last:
                    return self.op in ("<=", ">=", "==")
                continue
            if self.op == "==":
                return False
            if v > b:
                return self.op in (">", ">=")
            return self.op in ("<", "<=")
        return False

def padded(T):               # J8: on every part
    if isinstance(T, Product): return Product(*[padded1(p) for p in T.parts])
    if isinstance(T, Dict): return Dict(T.op, T.bs, T.reading, pad=True)
    if isinstance(T, Union): return Union(*[padded(x) for x in T.xs])
    if isinstance(T, Inter): return Inter(*[padded(x) for x in T.xs])
    raise TypeError

def between(lo, hi, reading, pad=False):
    return Inter(Dict(">=", lo, reading, pad), Dict("<=", hi, reading, pad))

# ---------- the zero-pass tuple (J7, manager's wording) ----------
U = [str(i) for i in range(100)] + ["%02d" % i for i in range(10)] + ["x", "ab", "", "M"]
def holds_tuple(Rset, t, zp_clause, domain=U):
    if not any(x is EMPTY for x in t):
        return Rset.has(t)
    if zp_clause == "product-by-spelling" and isinstance(Rset, Product):
        return all(x is EMPTY or p.has(x) for p, x in zip(Rset.parts, t))
    # non-product (or projection everywhere): some value of the looped parts
    idx = [i for i, x in enumerate(t) if x is EMPTY]
    for fill in itertools.product(domain, repeat=len(idx)):
        tt = list(t)
        for i, v in zip(idx, fill): tt[i] = v
        if Rset.has(tuple(tt)):
            return True
    return False
