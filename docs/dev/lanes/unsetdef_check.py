# unsetdef: evidence for docs/design/joint_condition.md §4B (a default for an absent label, `(h, m = 0): R`).
# Engine helpers COPIED from tupleval2_check.py (that file is not edited). Every regex verdict is computed by
# libpcre2-8 (ctypes) AND Python `re`, and the two must agree. Expectations are computed INDEPENDENTLY of the regex
# under test: the subject is split by Python string code into its fields, an absent field takes the default's TEXT,
# and the tuple is tested by Python integer tuple order (plus the canonical-numeral rule for unpadded sets). The
# regex under test is built from the UNFOLD (rows of products, the slice of the rows at the default, the unset branch
# of the pattern), never from that expectation.
#
# Tables (cited in the note as (DF), (DG), (D1), (DN), (DS), (DV), (DD), (DL), (DA), (DC), (DK)):
# (DF)  the default on optional minutes, the owner's example: unfold == expectation; the sketch's s3 points.
# (DG)  the GUARD: the hand unfold WITHOUT "m unset" differs from the default (counted), so the guard is needed.
# (D1)  the single-label default `(m = v: <30)`; a default outside the set; a default on a never-unset label.
# (DN)  the default vs no default vs the "don't care" alternative `| (h: 10)`: counts of differing subjects.
# (DS)  several defaults (optional minutes AND seconds), vs §5 problem 7's two-alternative form.
# (DV)  a version without a patch number, `1.4` as `1.4.0`.
# (DD)  a date without a day: NO default value reproduces "don't care" (counted over every day 1..31).
# (DL)  a looped label with an optional field per item; zero iterations hold.
# (DA)  a label unset because another ALTERNATIVE was taken.
# (DC)  a computed label (`mnum := $mname.index`) with a default.
# (DK)  look-alikes: `t2 & [m = 0]` (legal, different): counted.
# Sabotage: UNSETDEF_SABOTAGE=1 builds the slice at the wrong default (30 instead of 0) in (DF); it must go red.
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
SAB = os.environ.get("UNSETDEF_SABOTAGE") == "1"
if SAB:
    print("*** SABOTAGE ON: (DF) slice built at m = 30 instead of the default 0")


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


# ---------------------------------------------------------------------------------------------------------------
# Sets of k-tuples as FINITE UNIONS OF PRODUCTS: a row is a tuple of integer intervals (lo, hi), one per component.
TOP = 10 ** 9


def ge(b, strict=False):
    k = len(b)
    rows = []
    for j in range(k):
        last = j == k - 1
        lo = b[j] + 1 if (not last or strict) else b[j]
        rows.append(tuple((b[i], b[i]) for i in range(j)) + ((lo, TOP),) + ((0, TOP),) * (k - j - 1))
    return rows


def le(b, strict=False):
    k = len(b)
    rows = []
    for j in range(k):
        last = j == k - 1
        hi = b[j] - 1 if (not last or strict) else b[j]
        if hi < 0:
            continue
        rows.append(tuple((b[i], b[i]) for i in range(j)) + ((0, hi),) + ((0, TOP),) * (k - j - 1))
    return rows


def inter(r1, r2):
    out = []
    for a in r1:
        for b in r2:
            row = tuple((max(x[0], y[0]), min(x[1], y[1])) for x, y in zip(a, b))
            if all(lo <= hi for lo, hi in row):
                out.append(row)
    return out


def between(lo, hi):
    return inter(ge(lo), le(hi))


def canon(s):
    return s.isdigit() and str(int(s)) == s


def comp_ok(text, iv, padded):
    """is the TEXT in the component set: a numeral (canonical unless padded) whose value is in the interval"""
    if not text.isdigit():
        return False
    if not padded and not canon(text):
        return False
    return iv[0] <= int(text) <= iv[1]


def slice_rows(rows, i, vtext, padded):
    """the slice of a union of products at component i = the default's TEXT: the rows whose i-th component holds the
    text, with that component dropped. Again a finite union of products (the lane's claim s2)."""
    return [r[:i] + r[i + 1:] for r in rows if comp_ok(vtext, r[i], padded)]


def alt(strings):
    return "(?:" + "|".join(re.escape(s) for s in sorted(strings, key=lambda s: (-len(s), s))) + ")" if strings \
        else "(?!)"


def comp_rx(domain, iv, padded):
    return alt([s for s in domain if comp_ok(s, iv, padded)])


def rows_rx(rows, domains, seps, padded):
    """a union of products laid over fields with the given string domains and separators"""
    parts = []
    for r in rows:
        x = comp_rx(domains[0], r[0], padded)
        for d, sep, iv in zip(domains[1:], seps, r[1:]):
            x += re.escape(sep) + comp_rx(d, iv, padded)
        parts.append(x)
    return "(?:" + "|".join(parts) + ")" if parts else "(?!)"


# The independent expectation: Python integer tuple order on the fields' texts.
def in_range(texts, lo, hi, padded, lo_strict=False):
    if not all(t.isdigit() and (padded or canon(t)) for t in texts):
        return False
    v = tuple(int(t) for t in texts)
    return (v > lo if lo_strict else v >= lo) and (hi is None or v <= hi)


H = [str(i) for i in range(10)] + ["%02d" % i for i in range(100)]   # h := \d{1,2}
M = ["%02d" % i for i in range(100)]                                  # m := \d\d


def split_t2(s):
    r"""t2 := /(?<h>\d{1,2})(?::(?<m>\d\d))?/, parsed by string code: (h, m or None)"""
    if ":" in s:
        h, m = s.split(":")
        return h, m
    return s, None


SUBJ_T2 = H + [h + ":" + m for h in H for m in M]
LO, HI = (9, 30), (11, 0)
R = between(LO, HI)

# (DF) ----------------------------------------------------------------------------------------------------------
# t2 & ((h, m = 0): padded(between((9, 30), (11, 0))))
# UNFOLD: m set -> the rows over (h, m); m unset (the optional skipped) -> h in the slice of R at m = "0".
dflt = "30" if SAB else "0"
sl = slice_rows(R, 1, dflt, True)
rx_default = "(?:" + rows_rx(R, [H, M], [":"], True) + "|" + rows_rx(sl, [H], [], True) + ")"
n0 = T["differ"]
for s in SUBJ_T2:
    h, m = split_t2(s)
    check("DF", rx_default, s, in_range((h, m if m is not None else "0"), LO, HI, True))
print("(DF) t2 & ((h, m = 0): padded(between((9, 30), (11, 0)))): %d subjects, rows %d, slice rows %d, differ %d"
      % (len(SUBJ_T2), len(R), len(sl), T["differ"] - n0))
pts = {s: whole(rx_default, s) for s in ["9", "09", "10", "11", "12", "9:29", "9:30", "11:00", "11:01", "10:59"]}
print("(DF) the sketch's s3 points:", ", ".join("%s %s" % (k, "IN" if v else "out") for k, v in pts.items()))

# (DG) the hand unfold WITHOUT the guard: ((h, m): R) | (h: slice) -- the slice also admits SET minutes.
rx_noguard = "(?:" + rows_rx(R, [H, M], [":"], True) + "|" + rows_rx(sl, [H], [], True) + "(?::\\d\\d)?)"
slice_h = {h for h in H if in_range((h, "0"), LO, HI, True)}
cnt = 0
for s in SUBJ_T2:
    h, m = split_t2(s)
    own = (m is not None and in_range((h, m), LO, HI, True)) or h in slice_h
    got = check("DG", rx_noguard, s, own)
    if got != in_range((h, m if m is not None else "0"), LO, HI, True):
        cnt += 1
print("(DG) unguarded hand unfold ((h, m): R) | (h: slice): engine == its own meaning; differs from the default on "
      "%d of %d subjects (e.g. 11:45 %s)" % (cnt, len(SUBJ_T2), "IN" if whole(rx_noguard, "11:45") else "out"))

# (DN) no default, and the "don't care" alternative `| (h: 10)` (text 10), against the default.
rx_nodef = rows_rx(R, [H, M], [":"], True)
rx_dontcare = "(?:" + rx_nodef + "|10(?::\\d\\d)?)"
c_nd = c_dc = 0
for s in SUBJ_T2:
    h, m = split_t2(s)
    want_def = in_range((h, m if m is not None else "0"), LO, HI, True)
    a = check("DN-nodef", rx_nodef, s, m is not None and in_range((h, m), LO, HI, True))
    b = check("DN-dontcare", rx_dontcare, s, (m is not None and in_range((h, m), LO, HI, True)) or h == "10")
    c_nd += a != want_def
    c_dc += b != want_def
diff_dc = [s for s in SUBJ_T2 if whole(rx_dontcare, s) != whole(rx_default, s)]
print("(DN) vs the default: no default differs on %d; `| (h: 10)` differs on %d (%s)"
      % (c_nd, c_dc, ", ".join(diff_dc[:6])))

# (D1) single-label defaults on t2: (m = 0: <30), (m = 45: <30), and a default on a never-unset label.
LT30 = le((29,))
for v in ["0", "45", "00"]:
    sl1 = slice_rows(LT30, 0, v, False)          # arity 1: the slice is the empty tuple: holds or not, by v
    unset_rx = H_rx = alt(H)
    rx = "(?:" + alt(H) + ":" + rows_rx(LT30, [M], [], False) + ("|" + unset_rx if sl1 else "") + ")"
    same_as_nodef = 0
    rx_nd1 = alt(H) + ":" + rows_rx(LT30, [M], [], False)
    for s in SUBJ_T2:
        h, m = split_t2(s)
        want = in_range((m if m is not None else v,), (0,), (29,), False)
        check("D1", rx, s, want)
        same_as_nodef += whole(rx_nd1, s) == want
    print("(D1) t2 & (m = %s: <30): unset branch %s; same answers as no default on %d of %d"
          % (v, "HOLDS" if sl1 else "FAILS (the default is outside the set)", same_as_nodef, len(SUBJ_T2)))
T_SUBJ = [h + ":" + m for h in H for m in M]                         # t: minutes required
rx_t_def = rows_rx(R, [H, M], [":"], True)                            # the unset branch does not exist in t
same = sum(whole(rx_t_def, s) == in_range(tuple(s.split(":")), LO, HI, True) for s in T_SUBJ)
T["cases"] += len(T_SUBJ)
T["differ"] += len(T_SUBJ) - same
print("(D1) t (m never unset) & ((h, m = 0): R): identical to no default on %d of %d: the default is never used"
      % (same, len(T_SUBJ)))

# (DS) several defaults: t3 := /(?<h>\d{1,2})(?::(?<m>\d\d)(?::(?<s>\d\d))?)?/
#      ((h, m = 0, s = 0): padded(>= (9, 0, 30)))  vs §5 problem 7: ((h, m): padded(> (9, 0))) | ((h, m, s): ...)
HS = ["8", "08", "9", "09", "10", "11"]
SS = ["00", "05", "29", "30", "31", "59"]
SUBJ_T3 = HS + [h + ":" + m for h in HS for m in M] + [h + ":" + m + ":" + s for h in HS for m in M for s in SS]
B3 = (9, 0, 30)
R3 = ge(B3)
sl_s = slice_rows(R3, 2, "0", True)
sl_ms = slice_rows(sl_s, 1, "0", True)
rx3 = "(?:" + rows_rx(R3, [HS, M, SS], [":", ":"], True) + "|" + rows_rx(sl_s, [HS, M], [":"], True) + "|" + \
      rows_rx(sl_ms, [HS], [], True) + ")"
rx_p7 = "(?:" + rows_rx(ge((9, 0), strict=True), [HS, M], [":"], True) + "(?::" + alt(SS) + ")?|" + \
        rows_rx(R3, [HS, M, SS], [":", ":"], True) + ")"
d37 = []
for s in SUBJ_T3:
    f = s.split(":")
    full = tuple(f + ["0"] * (3 - len(f)))
    want = in_range(full, B3, None, True)
    check("DS", rx3, s, want)
    own7 = (len(f) >= 2 and in_range(tuple(f[:2]), (9, 0), None, True, lo_strict=True)) or \
           (len(f) == 3 and in_range(tuple(f), B3, None, True))
    got7 = check("DS-p7", rx_p7, s, own7)
    if got7 != want:
        d37.append(s)
print("(DS) t3 & ((h, m = 0, s = 0): padded(>= (9, 0, 30))): %d subjects, branches 3 (rows %d/%d/%d); "
      "§5 problem 7's form differs on %d (all minutes-absent: %s; e.g. %s)"
      % (len(SUBJ_T3), len(R3), len(sl_s), len(sl_ms), len(d37), all(":" not in s for s in d37), ", ".join(d37[:4])))

# (DV) semver2 := /(?<major>\d+)\.(?<minor>\d+)(?:\.(?<patch>\d+))?/, canonical, patch = 0
MJ = [str(i) for i in range(4)]
MN = [str(i) for i in range(13)]
SUBJ_V = [a + "." + b for a in MJ for b in MN] + [a + "." + b + "." + c for a in MJ for b in MN for c in MN]
for name, rows, lo, hi in [(">= (1, 4, 2)", ge((1, 4, 2)), (1, 4, 2), None),
                           (">= (1, 4, 0)", ge((1, 4, 0)), (1, 4, 0), None),
                           ("between((1, 4, 0), (1, 9, 9))", between((1, 4, 0), (1, 9, 9)), (1, 4, 0), (1, 9, 9))]:
    slv = slice_rows(rows, 2, "0", False)
    rxv = "(?:" + rows_rx(rows, [MJ, MN, MN], [".", "."], False) + "|" + rows_rx(slv, [MJ, MN], ["."], False) + ")"
    rxu = "(?:" + rows_rx(rows, [MJ, MN, MN], [".", "."], False) + "|" + rows_rx(slv, [MJ, MN], ["."], False) + \
          "(?:\\." + alt(MN) + ")?)"
    du = 0
    for s in SUBJ_V:
        f = s.split(".")
        want = in_range(tuple(f + ["0"] * (3 - len(f))), lo, hi, False)
        check("DV", rxv, s, want)
        du += whole(rxu, s) != want
    print("(DV) semver2 & ((major, minor, patch = 0): %s): %d subjects; slice rows %d; the UNGUARDED hand form "
          "differs on %d" % (name, len(SUBJ_V), len(slv), du))

# (DD) a date without a day: ym := /(?<y>\d{4})-(?<mo>\d\d)(?:-(?<d>\d\d))?/, R = padded(between((2024, 2, 15),
#      (2024, 4, 1))). "Don't care" (the month overlaps R) vs a default day = v, for every v in 1..31.
DLO, DHI = (2024, 2, 15), (2024, 4, 1)
months = ["%02d" % i for i in range(1, 13)]
overlap = {mo for mo in months if any(in_range(("2024", mo, "%02d" % d), DLO, DHI, True) for d in range(1, 32))}
best = None
for v in range(1, 32):
    rd = between(DLO, DHI)
    sld = slice_rows(rd, 2, str(v), True)
    rxd = rows_rx(sld, [["2024"], months], ["-"], True)
    dif = 0
    for mo in months:
        s = "2024-" + mo
        got = check("DD", rxd, s, in_range(("2024", mo, str(v)), DLO, DHI, True))
        dif += got != (mo in overlap)
    best = dif if best is None else min(best, dif)
print("(DD) 2024-MM with no day: the 'don't care' months %s; the best default day differs on %d of 12 months "
      "(no default reproduces it)" % (sorted(overlap), best))

# (DL) looped: list := /(?:(?<h>\d{1,2})(?::(?<m>\d\d))?,)*/ & ((h, m = 0): padded(between((9, 30), (11, 0))))
ITEMS = ["9", "10", "11", "12", "9:45", "9:15", "10:30", "11:30"]
item_rx = "(?:" + rows_rx(R, [H, M], [":"], True) + "|" + rows_rx(sl if not SAB else slice_rows(R, 1, "0", True),
                                                                   [H], [], True) + ")"
rx_list = "(?:" + item_rx + ",)*"
nl = 0
for n in range(4):
    for combo in itertools.product(ITEMS, repeat=n):
        s = "".join(c + "," for c in combo)
        want = all(in_range((split_t2(c)[0], split_t2(c)[1] or "0"), LO, HI, True) for c in combo)
        check("DL", rx_list, s, want)
        nl += 1
print("(DL) looped, per item: %d lists of 0..3 items; empty list (zero iterations) %s; '10,9:15,' %s"
      % (nl, "HOLDS" if whole(rx_list, "") else "fails", "IN" if whole(rx_list, "10,9:15,") else "out"))

# (DA) unset because another ALTERNATIVE was taken: /(?<h>\d{1,2})(?::(?<m>\d\d)| o'clock)/
SUBJ_A = [h + " o'clock" for h in H] + [h + ":" + m for h in H for m in M]
rx_a = "(?:" + rows_rx(R, [H, M], [":"], True) + "|" + rows_rx(sl, [H], [], True) + " o'clock)"
for s in SUBJ_A:
    if s.endswith(" o'clock"):
        h, m = s[:-8], "0"
    else:
        h, m = s.split(":")
    check("DA", rx_a, s, in_range((h, m), LO, HI, True))
print("(DA) the other alternative taken (` o'clock`): %d subjects" % len(SUBJ_A))

# (DC) computed label: ym2 := /(?<year>\d{4})(?:-(?<mname>Jan|...|Dec))?/, mnum := $mname.index,
#      ((year, mnum = 1): >= (2024, 3))  (mnum unset when mname is: the lane's reading of §4.4)
NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
YR = [str(y) for y in range(2022, 2027)]
RC = ge((2024, 3))
slc = slice_rows(RC, 1, "1", False)
parts = []
for r in RC:
    names = [n for i, n in enumerate(NAMES, 1) if r[1][0] <= i <= r[1][1]]
    parts.append(comp_rx(YR, r[0], False) + "-" + alt(names))
rx_c = "(?:" + "|".join(parts) + "|" + rows_rx(slc, [YR], [], False) + ")"
SUBJ_C = YR + [y + "-" + n for y in YR for n in NAMES]
for s in SUBJ_C:
    y, _, n = s.partition("-")
    mn = NAMES.index(n) + 1 if n else 1
    check("DC", rx_c, s, (int(y), mn) >= (2024, 3))
print("(DC) computed label, (year, mnum = 1): >= (2024, 3): %d subjects; '2024' %s, '2025' %s"
      % (len(SUBJ_C), "IN" if whole(rx_c, "2024") else "out", "IN" if whole(rx_c, "2025") else "out"))

# (DK) look-alike `t2 & [m = 0]`: an array whose one entry is "0" labelled m, intersected with t2: legal.
rx_arr = "(?=(?:\\d{1,2})(?::\\d\\d)?$)0"
adm = [s for s in SUBJ_T2 if check("DK", rx_arr, s, s == "0")]
dk = sum(whole(rx_arr, s) != whole(rx_default, s) for s in SUBJ_T2)
print("(DK) t2 & [m = 0] admits %s; differs from t2 & ((h, m = 0): R) on %d of %d" % (adm, dk, len(SUBJ_T2)))

# (DE) R-1 (owner question 10:40): a default that is a SET of several strings. Two readings, each an unfold:
#      EVERY: holds when every member would fit (the intersection of the slices); SOME: when any member would (the
#      union). D = m's own pattern's strings (\d\d). Compared on the minutes-absent subjects with rev 18's
#      DECIDED-PREFIX order (§8 caveat (5): a field is read only when the earlier ones equal the bound; an unset field
#      read makes the match incomparable: rejected), modelled here in Python.
def decided_prefix(h, rng):
    """the decided-prefix answer for minutes UNSET: each bound's compare decides on h alone or reads m (reject)"""
    if not (h.isdigit()):
        return False
    hv = int(h)
    for kind, b in rng:
        if kind in (">=", ">"):
            if hv < b[0]:
                return False
            if hv == b[0]:
                return False          # reaches the unset m: incomparable
        else:
            if hv > b[0]:
                return False
            if hv == b[0]:
                return False
    return True


RANGES = [("between((9, 30), (11, 0))", [(">=", (9, 30)), ("<=", (11, 0))], LO, HI, False),
          ("between((9, 0), (10, 0))", [(">=", (9, 0)), ("<=", (10, 0))], (9, 0), (10, 0), False),
          (">= (9, 30)", [(">=", (9, 30))], (9, 30), None, False),
          ("> (9, 0)", [(">", (9, 0))], (9, 0), None, True),
          ("between((9, 0), (11, 59))", [(">=", (9, 0)), ("<=", (11, 59))], (9, 0), (11, 59), False)]
DSET = M
for name, rng, lo, hi, strict in RANGES:
    if hi is None:
        rows = ge(lo, strict=strict)
    else:
        rows = between(lo, hi)
    every = None
    some = []
    for v in DSET:
        s1 = slice_rows(rows, 1, v, True)
        every = s1 if every is None else inter(every, s1)
        some = sorted(set(some + s1))
    rx_e = "(?:" + rows_rx(rows, [H, M], [":"], True) + "|" + rows_rx(every, [H], [], True) + ")"
    rx_s = "(?:" + rows_rx(rows, [H, M], [":"], True) + "|" + rows_rx(some, [H], [], True) + ")"
    rx_eu = "(?:" + rows_rx(rows, [H, M], [":"], True) + "|" + rows_rx(every, [H], [], True) + "(?::\\d\\d)?)"
    rx_su = "(?:" + rows_rx(rows, [H, M], [":"], True) + "|" + rows_rx(some, [H], [], True) + "(?::\\d\\d)?)"
    ed = sd = e_vs_dp = s_vs_dp = eu = su = 0
    for s in SUBJ_T2:
        h, m = split_t2(s)
        inr = lambda mm: in_range((h, mm), lo, hi, True, lo_strict=strict)
        if m is None:
            we, ws = all(inr(v) for v in DSET), any(inr(v) for v in DSET)
        else:
            we = ws = inr(m)
        check("DE-every", rx_e, s, we)
        check("DE-some", rx_s, s, ws)
        eu += whole(rx_eu, s) != we
        su += whole(rx_su, s) != ws
        if m is None:
            dp = decided_prefix(h, rng)
            e_vs_dp += we != dp
            s_vs_dp += ws != dp
    ein = [h for h in ["8", "9", "10", "11", "12"] if whole(rx_e, h)]
    sin = [h for h in ["8", "9", "10", "11", "12"] if whole(rx_s, h)]
    print("(DE) %-27s m = any \\d\\d: EVERY admits %-12s SOME admits %-12s | vs decided-prefix on the 110 "
          "minutes-absent subjects: EVERY differs %d, SOME %d | unguarded hand form: EVERY %d, SOME %d differ"
          % (name, ",".join(ein) or "-", ",".join(sin) or "-", e_vs_dp, s_vs_dp, eu, su))
# the date: SOME over every day = the 'don't care' (overlap) months
rd = between(DLO, DHI)
some_d = []
for d in range(1, 32):
    some_d = sorted(set(some_d + slice_rows(rd, 2, "%02d" % d, True)))
rxsd = rows_rx(some_d, [["2024"], months], ["-"], True)
for mo in months:
    check("DE-date", rxsd, "2024-" + mo, mo in overlap)
print("(DE) 2024-MM, d = any day, SOME: admits %s (= the 'don't care' months)"
      % [mo for mo in months if whole(rxsd, "2024-" + mo)])

print("TOTAL cases %d differ %d engine-disagreements %d" % (T["cases"], T["differ"], DISAGREE[0]))
