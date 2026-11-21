# jcfold2: evidence for docs/design/joint_condition.md after the owner's zero-pass-record ruling (CF 2026-11-16
# 12:45). Tests THE MANAGER'S WORDING of the ruled answer (CF 12:45 record):
#   "a reached loop that runs zero times gives ONE tuple whose looped parts are EMPTY; empty satisfies any set (for a
#    joint set R: the outside labels' values must be possible under R for some value of the looped parts); a default
#    is NOT read there; a plain single-label condition still HOLDS on zero passes; 'unset' (never reached) keeps its
#    meaning."
# Method COPIED from jcfold_check.py (engine helpers unedited): every regex verdict is computed by libpcre2-8 (ctypes)
# AND Python `re`, and the two must agree. Each rule is evaluated in Python from the subject split by plain string
# code (the RULE's verdict, M), and separately unfolded into a regex (the rule's automaton reading) that is
# engine-run against M. Other readings (the `&` reading, the old vacuous per-pass reading, a hand expansion) are
# computed in Python and COUNTED against M; they are comparisons, not expectations.
#
# Tables:
# (RZ) re-run of jcfold's population: `/(?<k>\d)(?:;(?<h>\d))*/ & (h: <5, k: 3..7)`; M vs the `&` reading (expect 0
#      differ of 1,110) and vs jcfold's reading B (vacuous on zero passes; expect 5).
# (ZN) NESTED: `/(?<c>\d)(?:;(?<h>\d)(?::(?<k>\d))*)*/ & (c: 3..7, h: 0..4, k: 2..6)`: c outside every loop, h in the
#      outer item, k in an inner loop; zero-pass OUTER loop and zero-pass INNER loops. M vs `&`. Then jcfold's (NL)
#      population (non-product `((h, k): >= (5, 3))`) re-run under M: how many answers move.
# (ZJ) NON-PRODUCT joint sets on (RZ)'s pattern: the "possible for some value" clause; M vs the hand expansion into a
#      `|` of records (each record by the `&` reading) on zero-pass subjects; the domain of "some value"; an EMPTY set
#      spelled as a product and as a non-product.
# (ZD) DEFAULTS: a looped label with a default on zero passes (not read), the same loop never reached (read), an
#      all-looped list with a default (the empty list holds).
# (Z1) SINGLE LABEL: a plain condition on zero passes HOLDS; a never-reached loop FAILS (CF:997-1000).
# Sabotage: JCFOLD2_SABOTAGE=1 unfolds M's regexes with zero passes VACUOUS (jcfold's reading B); the check must
# then differ.
import ctypes, re, itertools, os, sys

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
SAB = os.environ.get("JCFOLD2_SABOTAGE") == "1"
if SAB:
    print("SABOTAGE ON")


def _code(p):
    if p not in _cache:
        e, o = ctypes.c_int(), ctypes.c_size_t()
        c = L.pcre2_compile_8(p.encode(), len(p.encode()), 0, ctypes.byref(e), ctypes.byref(o), None)
        assert c, (p[:80], e.value)
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
        print("  ENGINE DISAGREEMENT", repr(p[:60]), repr(t), a, b)
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


def alt(strings):
    strings = sorted(set(strings), key=lambda s: (-len(s), s))
    return "(?:" + "|".join(re.escape(s) for s in strings) + ")" if strings else "(?!)"


D = list(range(10))          # the capture language of `\d`, as integers
# the "zero passes" piece of an unfold: M keeps it guarded; the sabotage makes it unconditional (vacuous)
def zp(guard_ok):
    return True if SAB else guard_ok


# ---------------------------------------------------------------------------------------------------------------
# (RZ) P := /(?<k>\d)(?:;(?<h>\d))*/ & (h: S, k: T), S = 0..4, T = 3..7: jcfold's population, re-run under M.
print("\n(RZ) re-run: P & (h: <5, k: 3..7), k outside h's loop, under the manager's wording (M)")
SUBJ_RZ = []
for k in range(10):
    for n in range(0, 3):
        for hs in itertools.product(range(10), repeat=n):
            SUBJ_RZ.append(str(k) + "".join(";" + str(h) for h in hs))


def split_rz(s):
    parts = s.split(";")
    return int(parts[0]), [int(x) for x in parts[1:]]


S_set, T_set = set(range(5)), set(range(3, 8))
S_rx, T_rx = alt([str(x) for x in S_set]), alt([str(x) for x in T_set])
# M unfolded: per pass (h, k) in S x T; zero passes: one tuple (EMPTY, k), empty satisfies S, so k in T
m_rz = "(?:" + T_rx + "(?:;" + S_rx + ")+" + ("|" + (T_rx if not SAB else "\\d")) + ")"
rz_mA = rz_mB = rz_before = 0
rz_before = T["cases"]
for s in SUBJ_RZ:
    k, hs = split_rz(s)
    wantM = (k in T_set and all(h in S_set for h in hs)) if hs else (k in T_set)
    wantA = k in T_set and all(h in S_set for h in hs)                # (h: S) & (k: T)
    wantB = all(h in S_set and k in T_set for h in hs)                # jcfold's B: zero passes vacuous
    check("RZ M", m_rz, s, wantM)
    rz_mA += wantM != wantA
    rz_mB += wantM != wantB
print("(RZ) subjects %d; M vs the & reading differ on %d; M vs jcfold's reading B (vacuous) differ on %d" %
      (len(SUBJ_RZ), rz_mA, rz_mB))
print("     '9': M %s, & reading %s" % (whole(m_rz, "9"), 9 in T_set))

# ---------------------------------------------------------------------------------------------------------------
# (ZN) NESTED. P := /(?<c>\d)(?:;(?<h>\d)(?::(?<k>\d))*)*/ & (c: C, h: H, k: K)
print("\n(ZN) nested: P & (c: 3..7, h: 0..4, k: 2..6); c outside every loop, h in the outer item, k in an inner loop")
C_set, H_set, K_set = set(range(3, 8)), set(range(5)), set(range(2, 7))
C_rx, H_rx, K_rx = (alt([str(x) for x in s_]) for s_ in (C_set, H_set, K_set))
ITEMS = [(h, ks) for h in (0, 4, 5, 9) for ks in [(), (2,), (9,), (3, 6), (6, 0)]]
SUBJ_ZN = []
for c in (0, 2, 3, 5, 7, 8):
    for n in range(0, 3):
        for its in itertools.product(ITEMS, repeat=n):
            SUBJ_ZN.append(str(c) + "".join(";%d%s" % (h, "".join(":%d" % k for k in ks)) for h, ks in its))


def split_zn(s):
    parts = s.split(";")
    c = int(parts[0])
    its = []
    for p in parts[1:]:
        q = p.split(":")
        its.append((int(q[0]), [int(x) for x in q[1:]]))
    return c, its


def zn_M(c, its):
    if not its:                                  # the OUTER loop ran zero times: one tuple (c, EMPTY, EMPTY)
        return c in C_set
    ok = True
    for h, ks in its:
        if not ks:                               # the INNER loop, reached in this outer pass, ran zero times
            ok = ok and c in C_set and h in H_set
        for k in ks:
            ok = ok and c in C_set and h in H_set and k in K_set
    return ok


def zn_amp(c, its):                              # (c: C) & (h: H) & (k: K), each by the sequence rule
    return c in C_set and all(h in H_set for h, _ in its) and all(k in K_set for _, ks in its for k in ks)


def zn_vac(c, its):                              # jcfold's reading: per pass of the deepest loop; no pass, no tuple
    return all(c in C_set and h in H_set and k in K_set for h, ks in its for k in ks)


if SAB:
    m_zn = "\\d(?:;\\d(?::\\d)*)*"
else:
    m_zn = C_rx + "(?:;" + H_rx + "(?::" + K_rx + ")*)*"
zn_amp_d = zn_vac_d = zn_outer0 = zn_inner0 = 0
zn_before = T["cases"]
for s in SUBJ_ZN:
    c, its = split_zn(s)
    want = zn_M(c, its)
    check("ZN M", m_zn, s, want)
    zn_amp_d += want != zn_amp(c, its)
    if want != zn_vac(c, its):
        zn_vac_d += 1
    zn_outer0 += (not its)
    zn_inner0 += any(not ks for _, ks in its)
print("(ZN) subjects %d (outer zero passes %d; with at least one inner zero-pass reach %d); M vs & differ %d; "
      "M vs vacuous per-pass differ %d" % (len(SUBJ_ZN), zn_outer0, zn_inner0, zn_amp_d, zn_vac_d))
print("     '5' (outer zero): M %s; '5;9' (inner zero, h=9 not in H): M %s, vacuous %s" %
      (whole(m_zn, "5"), whole(m_zn, "5;9"), zn_vac(5, [(9, [])])))

# jcfold's (NL) re-run under M. P := /(?:(?<h>\d):(?:(?<k>\d),)*;)*/ ; ((h, k): >= (5, 3)), a non-product.
print("(ZN-NL) jcfold's (NL) population under M: ((h, k): >= (5, 3)), h in the outer item, k in the inner loop")
R_NL = lambda h, k: (h, k) >= (5, 3)
possible_h = lambda h: any(R_NL(h, k) for k in D)           # an inner zero-pass reach: h possible for some k
items = []
for a in range(10):
    sl = alt([str(k) for k in D if R_NL(a, k)])
    q = "*" if zp(possible_h(a)) else "+"
    items.append(str(a) + ":(?:" + sl + "," + ")" + q + ";")
nl_rx = "(?:" + "|".join(items) + ")*"
SUBJ_NL = []
for n in range(0, 3):
    for its in itertools.product([(4, ()), (4, (9,)), (5, ()), (5, (3,)), (5, (2,)), (5, (3, 4)), (6, (0, 1)),
                                  (5, (4, 2))], repeat=n):
        SUBJ_NL.append("".join("%d:%s;" % (a, "".join("%d," % k for k in ks)) for a, ks in its))
nl_moved, nl_moved_ex = 0, None
for s in SUBJ_NL:
    wantM, wantOld = True, True
    for item in [x for x in s.split(";") if x]:
        a, _, rest = item.partition(":")
        ks = [int(x) for x in rest.split(",") if x]
        if not ks:
            wantM = wantM and possible_h(int(a))
        for k in ks:
            wantM = wantM and R_NL(int(a), k)
            wantOld = wantOld and R_NL(int(a), k)
    check("ZN-NL M", nl_rx, s, wantM)
    if wantM != wantOld:
        nl_moved += 1
        nl_moved_ex = nl_moved_ex or s
print("(ZN-NL) subjects %d; answers that MOVE from jcfold's (NL) (an outer item with no k: held, now tests h) %d; "
      "e.g. %r" % (len(SUBJ_NL), nl_moved, nl_moved_ex))

# ---------------------------------------------------------------------------------------------------------------
# (ZJ) NON-PRODUCT joint sets on (RZ)'s pattern P := /(?<k>\d)(?:;(?<h>\d))*/
print("\n(ZJ) non-product joint sets on P := /(?<k>\\d)(?:;(?<h>\\d))*/")
DOM_ANY = D + ["x"]          # "some value" over ALL strings, represented by the digits plus one non-digit string
ZJ = [
    # name, R as a predicate over (h, k), the hand expansion as rows [(Hset or None=any, Kset or None=any)]
    ("((h, k): >= (5, 3))", lambda h, k: h != "x" and (h, k) >= (5, 3),
     [(set(range(6, 10)), None), ({5}, set(range(3, 10)))]),
    ("((k, h): >= (5, 3))", lambda h, k: h != "x" and (k, h) >= (5, 3),
     [(None, set(range(6, 10))), (set(range(3, 10)), {5})]),
    ("((h, k): (0|1|2, 3|4) | (5, 5))", lambda h, k: (h in (0, 1, 2) and k in (3, 4)) or (h == 5 and k == 5),
     [({0, 1, 2}, {3, 4}), ({5}, {5})]),
    ("((h, k): (\"x\", 3) | (0, 5))", lambda h, k: (h == "x" and k == 3) or (h == 0 and k == 5),
     [({"x"}, {3}), ({0}, {5})]),
    # dictionary order whose literal expansion has an EMPTY row: `(h: <0) | (h: 0, k: <3)`
    ("((h, k): < (0, 3))", lambda h, k: h != "x" and (h, k) < (0, 3),
     [(set(), None), ({0}, {0, 1, 2})]),
]


def rows_amp(rows, k, hs):   # a `|` of records, each record by the `&` reading over the whole match
    for Hs, Ks in rows:
        if (Ks is None or k in Ks) and all(Hs is None or h in Hs for h in hs):
            return True
    return False


for name, R, rows in ZJ:
    poss_any = {k for k in D if any(R(h, k) for h in DOM_ANY)}
    poss_cap = {k for k in D if any(R(h, k) for h in D)}
    # M unfolded (domain: ALL strings): per k, the slice of h; zero passes allowed when k is possible
    br = []
    for k in D:
        sl = alt([str(h) for h in D if R(h, k)])
        q = "*" if zp(k in poss_any) else "+"
        br.append(str(k) + "(?:;" + sl + ")" + q)
    rx = "(?:" + "|".join(br) + ")"
    z_vs_exp = nz_vs_exp = 0
    for s in SUBJ_RZ:
        k, hs = split_rz(s)
        want = all(R(h, k) for h in hs) if hs else (k in poss_any)
        check("ZJ " + name, rx, s, want)
        e = rows_amp(rows, k, hs)
        if hs:
            nz_vs_exp += want != e
        else:
            z_vs_exp += want != e
    print("(ZJ) %-34s possible k (any string) %s; (capture language of \\d) %s; zero-pass vs hand expansion differ "
          "%d of 10; with passes differ %d of %d" % (name, sorted(poss_any), sorted(poss_cap), z_vs_exp,
                                                     nz_vs_exp, len(SUBJ_RZ) - 10))

# THE EMPTY SET spelled three ways, zero passes, subject `3`
print("(ZJ-E) the EMPTY set of pairs, zero passes, subject '3':")
emp = [("(h: <0, k: 3)  [product clause: empty h satisfies <0]", 3 in {3}),
       ("((h, k): (<0, 3))  [the same, as a tuple set: product clause]", 3 in {3}),
       ("((h, k): < (0, 0))  [non-product clause: no h possible]", any((h, 3) < (0, 0) for h in D))]
for txt, v in emp:
    print("       %-58s %s" % (txt, "HOLDS" if v else "FAILS"))
print("       single label (h: <0) on '3': HOLDS (CF:997-1000)")

# ---------------------------------------------------------------------------------------------------------------
# (ZD) DEFAULTS
print("\n(ZD) defaults on zero passes")
# (a) P as (RZ), (h = 9: <5, k: T): zero passes: default NOT read -> k in T. Reading it would give 9 <5: fails.
m_zd = "(?:" + T_rx + "(?:;" + S_rx + ")+|" + (T_rx if not SAB else "(?!)") + ")"
zd_read = zd_amp = 0
for s in SUBJ_RZ:
    k, hs = split_rz(s)
    want = (k in T_set and all(h in S_set for h in hs)) if hs else (k in T_set)
    check("ZD a", m_zd, s, want)
    readdef = (k in T_set and all(h in S_set for h in hs)) if hs else (k in T_set and 9 in S_set)
    zd_read += want != readdef
    zd_amp += want != (k in T_set and all(h in S_set for h in hs))   # (h = 9: <5) & (k: T), default unread
print("(ZD a) P & (h = 9: <5, k: 3..7): %d subjects; M vs 'default read on zero passes' differ %d "
      "(the zero-pass subjects with k in T); M vs & (default unread) differ %d" % (len(SUBJ_RZ), zd_read, zd_amp))
# (b) the loop NEVER REACHED: P2 := /(?<k>\d)(?:-(?:;(?<h>\d))*)?/ ; `9` never reaches h's loop, `9-` runs it zero times
SUBJ_P2 = [str(k) for k in D] + [str(k) + "-" + "".join(";%d" % h for h in hs)
                                  for k in D for n in range(3) for hs in itertools.product(D, repeat=n)]
for dflt in (None, 9, 2):
    zero = T_rx + "-"
    unr = (T_rx if dflt is not None and dflt in S_set else "(?!)")
    rx = "(?:" + T_rx + "-(?:;" + S_rx + ")+|" + zero + "|" + unr + ")"
    for s in SUBJ_P2:
        k = int(s[0])
        if "-" not in s:                         # never reached: h UNSET; the default (if any) read
            want = k in T_set and dflt is not None and dflt in S_set
        else:
            hs = [int(x) for x in s.split("-")[1].split(";") if x]
            want = (k in T_set and all(h in S_set for h in hs)) if hs else (k in T_set)
        check("ZD b", rx, s, want)
    print("(ZD b) P2 & (h%s: <5, k: 3..7): '5' (never reached) %s, '5-' (zero passes) %s" %
          ("" if dflt is None else " = %d" % dflt, whole(rx, "5"), whole(rx, "5-")))
# (c) an all-looped list with a default: L := /(?:(?<h>\d)(?::(?<m>\d))?,)*/ & ((h, m = 0): >= (5, 3))
R_L = lambda h, m: (h, m) >= (5, 3)
itm = []
for h in D:
    sl = alt([str(m) for m in D if R_L(h, m)])
    itm.append(str(h) + "(?::" + sl + ")" + ("?" if R_L(h, 0) else "") + ",")
l_rx = "(?:" + "|".join(itm) + ")*"
SUBJ_L = [""] + ["".join("%d%s," % (h, "" if m is None else ":%d" % m) for h, m in its)
                 for n in (1, 2) for its in itertools.product([(h, m) for h in (4, 5, 6) for m in (None, 0, 3)],
                                                              repeat=n)]
for s in SUBJ_L:
    want = True
    for it in [x for x in s.split(",") if x]:
        h, _, m = it.partition(":")
        want = want and R_L(int(h), int(m) if m else 0)
    check("ZD c", l_rx, s, want)
print("(ZD c) L & ((h, m = 0): >= (5, 3)): %d subjects; the empty list %s" %
      (len(SUBJ_L), "HOLDS" if whole(l_rx, "") else "FAILS"))

# ---------------------------------------------------------------------------------------------------------------
# (Z1) single label: a plain condition on zero passes HOLDS; never reached FAILS
print("\n(Z1) single label")
z1 = [("/(?<k>\\d)(?:;(?<h>\\d))*/ & (h: <5)", "\\d(?:;" + S_rx + ")*", [(s, all(h in S_set for h in split_rz(s)[1]))
                                                                         for s in SUBJ_RZ]),
      ("/(?:(?<n>\\d),)*/ & (n: <5)", "(?:" + S_rx + ",)*", [("", True), ("3,", True), ("7,", False), ("3,7,", False)]),
      ("/x|(?<n>\\d)+/ & (n: <5)", "(?:" + S_rx + ")+", [("x", False), ("3", True), ("37", False)])]
for name, rx, cases in z1:
    for s, want in cases:
        check("Z1", rx, s, want)
    print("(Z1) %-38s %d subjects (zero passes hold; never reached fails)" % (name, len(cases)))

print("\nTOTAL cases %d differ %d engine-disagreements %d" % (T["cases"], T["differ"], DISAGREE[0]))
