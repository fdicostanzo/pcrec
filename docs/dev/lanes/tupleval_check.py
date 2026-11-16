# tupleval: evidence for docs/design/joint_condition.md §4A (the tuple as a value: the full account).
# Engine helpers COPIED from jointexp_check.py (that file is not edited). Every regex verdict is computed by
# libpcre2-8 (ctypes) AND Python `re`, and the two must agree. Expectations are computed INDEPENDENTLY of the
# regex under test: Python integer tuples, datetime.date, the ipaddress module, plain string equality.
#
# Claims checked (tables cited in the note as (D), (R), (Q), (E), (O)):
# (D) DESTRUCTURING / PROJECTION LOSES THE PAIRING: for a table that is NOT a product (month_days), the record of
#     its projections (month: pi1, day: pi2) admits more than the joint condition ((month, day): month_days);
#     for a PRODUCT the projections give it back exactly.
# (R) A CIDR LIST IS AN ARRAY OF TUPLE RANGES: each block = between(network, broadcast) over (a, b, c, d) in
#     dictionary order; expectation by `ipaddress`, prefixes not on octet boundaries included.
# (Q) A TUPLE OF `$` VALUES OVER REPEATED LABELS IS UNPAIRED: ($h, $m) read as the product of every h with every m
#     differs from the per-iteration pairs (Python only for the product reading; the per-item answer engine-run).
# (E) A LITERAL TUPLE IS STRING EQUALITY PER COMPONENT: t & ((h, m): (9, 0)) is empty on t's whole population
#     (m is two digits), while padded(== (9, 0)) admits 9:00 and 09:00.
# (O) THE TWO ORDERS ARE DIFFERENT SETS: `>= (9, 30)` (dictionary) vs `(>= 9, >= 30)` (product), counted.
import ctypes, re, itertools, datetime, random, sys, ipaddress

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


def cset(op, v, top, pad=True):
    """single-label comparison set `OP v` over 0..top-1; pad=True: leading zeros allowed (padded); else canonical"""
    vs = [str(x) for x in range(top) if OPS[op](x, v)]
    if not vs:
        return "(?!)"
    return ("0*" if pad else "") + "(?:" + "|".join(vs) + ")"


def rects(op, b, tops, pad=True):
    """dictionary-order `OP b` over a k-tuple as a list of products (rows), each a list of per-field sets"""
    k = len(b)
    out = []
    lt = op in ("<", "<=")
    for j in range(k):
        if j == k - 1:
            fop = op
        else:
            if op == "==":
                continue
            fop = "<" if lt else ">"
        out.append([cset("==", b[i], tops[i], pad) for i in range(j)] + [cset(fop, b[j], tops[j], pad)] +
                   [cset(">=", 0, tops[i], pad) for i in range(j + 1, k)])
    return out


def rect_regex(rs, seps):
    alts = []
    for r in rs:
        s = ""
        for i, fs in enumerate(r):
            s += fs + (re.escape(seps[i]) if i < len(seps) else "")
        alts.append(s)
    return "(?:" + "|".join(alts) + ")"


def inter(p, q):
    return "(?=%s$)%s" % (p, q)


T = {"cases": 0, "differ": 0}


def check(tag, rx, subj, want):
    got = whole(rx, subj)
    T["cases"] += 1
    if got != want:
        T["differ"] += 1
        if T["differ"] < 15:
            print("  DIFFER", tag, repr(subj), "got", got, "want", want)
    return got


def pset(vals):
    return "0*(?:" + "|".join(str(v) for v in vals) + ")"


# ---------------------------------------------------------------------------------------------------------------
# (D) projection of a non-product table loses the pairing; of a product it does not.
before = T["cases"]
month_days = [([1, 3, 5, 7, 8, 10, 12], range(1, 32)), ([4, 6, 9, 11], range(1, 31)), ([2], range(1, 29))]
tuples = {(m, d) for ms, ds in month_days for m in ms for d in ds}
pi1 = sorted({m for m, _ in tuples}); pi2 = sorted({d for _, d in tuples})
print("(D) month_days: %d tuples; pi1 x pi2 = %d tuples (%d extra)" %
      (len(tuples), len(pi1) * len(pi2), len(pi1) * len(pi2) - len(tuples)))
joint_rx = "(?:" + "|".join(pset(ms) + "-" + pset(ds) for ms, ds in month_days) + ")"
proj_rx = pset(pi1) + "-" + pset(pi2)
dsub = ["%02d-%02d" % (m, d) for m in range(0, 14) for d in range(0, 33)]
proj_extra = 0
for s in dsub:
    m, d = map(int, s.split("-"))
    want_joint = (m, d) in tuples
    check("D-joint", joint_rx, s, want_joint)
    got_proj = check("D-proj", proj_rx, s, m in pi1 and d in pi2)     # the projection's own expectation
    if got_proj and not want_joint:
        proj_extra += 1
# independent cross-check of the table itself against datetime (a non-leap year)
cal_ok = sum(1 for (m, d) in tuples if datetime.date(2023, m, d))
print("(D) month_days rows checked against datetime(2023): %d of %d valid" % (cal_ok, len(tuples)))
print("(D) subjects %d: joint differs 0 expected; projection admits %d subjects the table does not (e.g. 04-31, 02-30)"
      % (len(dsub), proj_extra))
# a PRODUCT: (padded(between(1, 12)), padded(between(1, 28))): projections give it back
prod = {(m, d) for m in range(1, 13) for d in range(1, 29)}
q1 = {m for m, _ in prod}; q2 = {d for _, d in prod}
assert {(a, b) for a in q1 for b in q2} == prod
print("(D) product (1..12) x (1..28): pi1 x pi2 == the set: True")
small = {(9, 0), (17, 30)}
sp = {(a, b) for a in {x for x, _ in small} for b in {y for _, y in small}}
print("(D) [(9, 0), (17, 30)]: pi1 x pi2 =", sorted(sp), "(%d tuples, the set has %d)" % (len(sp), len(small)))
print("(D) cases %d" % (T["cases"] - before))

# ---------------------------------------------------------------------------------------------------------------
# (R) CIDR blocks as dictionary-order ranges over four canonical octets; an array of them = their union.
before = T["cases"]
nets = ["10.1.128.0/22", "10.1.128.0/17", "172.16.0.0/12", "192.168.4.0/23", "100.64.0.0/10", "8.8.8.8/32"]
blocks = []
for n in nets:
    net = ipaddress.ip_network(n)
    lo = tuple(int(x) for x in str(net.network_address).split("."))
    hi = tuple(int(x) for x in str(net.broadcast_address).split("."))
    rx = inter(rect_regex(rects(">=", lo, (256,) * 4, pad=False), [".", ".", "."]),
               rect_regex(rects("<=", hi, (256,) * 4, pad=False), [".", ".", "."]))
    blocks.append((net, rx))
octet = "(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)"
ipv4 = "\\.".join([octet] * 4)
random.seed(11)
rsub = []
for net, _ in blocks:
    a = int(net.network_address); b = int(net.broadcast_address)
    for x in (a - 1, a, a + 1, (a + b) // 2, b - 1, b, b + 1):
        if 0 <= x < 2 ** 32:
            rsub.append(str(ipaddress.ip_address(x)))
rsub += [str(ipaddress.ip_address(random.randrange(2 ** 32))) for _ in range(300)]
rsub += ["10.1.130.5", "172.32.0.0", "172.15.255.255", "01.1.130.5"]
# the array's union as ONE regex exceeds PCRE2's pattern size here, so the array answer is the OR of the
# engine-run per-block answers (alternation itself is not under test); it is checked against `ipaddress` too.
narr = 0
for s in rsub:
    try:
        addr = ipaddress.ip_address(s)
    except ValueError:
        addr = None
    got = [check("R-block", inter(ipv4, rx), s, addr is not None and addr in net) for net, rx in blocks]
    want_any = addr is not None and any(addr in net for net, _ in blocks)
    T["cases"] += 1
    if any(got) != want_any:
        T["differ"] += 1
        print("  DIFFER R-array", repr(s))
    narr += any(got)
print("(R) %d CIDR blocks (1 on an octet boundary, 5 not), %d subjects, %d in the array; cases %d"
      % (len(blocks), len(rsub), narr, T["cases"] - before))

# ---------------------------------------------------------------------------------------------------------------
# (Q) ($h, $m) over a repeated label: the product of every h with every m vs the per-iteration pairs; R = >= (9, 30).
before = T["cases"]
item = r"(?<h>\d{1,2}):(?<m>\d\d),"
loop_rx = "(?:" + rect_regex(rects(">=", (9, 30), (100, 100)), [":"]) + ",)*"
qsub = ["", "9:30,", "10:00,9:30,", "10:00,9:45,", "10:15,9:45,", "9:45,10:00,", "11:00,10:00,", "9:31,9:59,",
        "10:05,9:40,12:00,", "9:29,", "10:00,9:29,"]
qdiff = 0
for s in qsub:
    its = [(int(m.group("h")), int(m.group("m"))) for m in re.finditer(py(item), s)]
    per_item = all(t >= (9, 30) for t in its)
    check("Q-per-item", loop_rx, s, per_item)
    unpaired = all((h, m) >= (9, 30) for h, _ in its for _, m in its)
    if unpaired != per_item:
        qdiff += 1
        print("     %-18r per-iteration pairs=%-5s product of $h x $m=%s" % (s, per_item, unpaired))
print("(Q) subjects %d: the unpaired product differs on %d; cases %d" % (len(qsub), qdiff, T["cases"] - before))

# ---------------------------------------------------------------------------------------------------------------
# (E) a literal tuple compares TEXT per component.
before = T["cases"]
tpop = ["%d:%02d" % (h, m) for h in range(100) for m in range(100)] + \
       ["%02d:%02d" % (h, m) for h in range(10) for m in range(100)]
lit_rx = "9:0"                    # ((h, m): (9, 0)): h text "9", m text "0"
pad_rx = "0*9:0*0"                # ((h, m): padded(== (9, 0)))
t_rx = r"\d{1,2}:\d\d"
nlit = npad = 0
for s in tpop:
    h, m = s.split(":")
    nlit += check("E-literal", inter(t_rx, lit_rx), s, (h, m) == ("9", "0"))
    npad += check("E-padded", inter(t_rx, pad_rx), s, (int(h), int(m)) == (9, 0))
print("(E) t population %d: literal (9, 0) admits %d, padded(== (9, 0)) admits %d; cases %d"
      % (len(tpop), nlit, npad, T["cases"] - before))

# ---------------------------------------------------------------------------------------------------------------
# (O) dictionary order vs product order: two sets, counted on the time population.
before = T["cases"]
dict_rx = rect_regex(rects(">=", (9, 30), (100, 100)), [":"])
prod_rx = cset(">=", 9, 100) + ":" + cset(">=", 30, 100)
nd = 0
for s in tpop:
    h, m = map(int, s.split(":"))
    a = check("O-dict", dict_rx, s, (h, m) >= (9, 30))
    b = check("O-prod", prod_rx, s, h >= 9 and m >= 30)
    nd += a != b
print("(O) subjects %d: `>= (9, 30)` and `(>= 9, >= 30)` differ on %d (e.g. 10:00); cases %d"
      % (len(tpop), nd, T["cases"] - before))

print("TOTAL cases %d differ %d engine-disagreements %d" % (T["cases"], T["differ"], DISAGREE[0]))
