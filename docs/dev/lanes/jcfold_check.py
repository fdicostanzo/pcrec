# jcfold: evidence for docs/design/joint_condition.md after the 2026-11-16 rulings (lane jcfold).
# Engine helpers COPIED from jointexp_check.py (not edited). Every regex verdict is computed by libpcre2-8
# (ctypes) AND Python `re`, and the two must agree. Expectations are computed in Python from the subject split by
# plain string code (integer tuples, Python's own tuple order), never from the regex under test.
#
# Tables:
# (RD) RECORD = PRODUCT WITH A DEFAULT (record-is-product, 11:35): `t2 & (h: S, m = v: T)` unfolded the RECORD's
#      way (each entry a single-label condition, the default slicing its own entry) vs the JOINT way
#      `((h, m = v): (S, T))` unfolded as §4B.2's guarded slice. Both engine-run; expectation from the split subject.
# (RZ) RECORD AT DIFFERENT DEPTHS, ZERO PASSES: `/(?<k>\d)(?:;(?<h>\d))*/ & (h: S, k: T)`. Reading A: §4.1's
#      "a record = the & of its entries" (k: T always checked). Reading B: the k-label rule specialised (joint-loops,
#      11:17: per pass of h's loop, k "having its one value on every pass"; zero passes: no tuple, holds). Counts the
#      subjects where the two readings differ (the CONTRADICTION the report names).
# (SE) `$`-BOUND START/END PAIR: `span & ((eh, em): padded(> ($sh, $sm)))`, unfolded as the §4.6 relation's finite
#      union over the classes of (sh, sm); expectation (eh, em) > (sh, sm) as integers.
# (MN) THREE-FIELD MONTH-NAME RANGE: `textdate & ((year, mnum, day): between((2024, 3, 15), (2025, 2, 1)))` with
#      `mnum := $mname.index`; text order day, name, year (the left's order is the compare's, not the text's).
# (RC) ROW COUNT: `between(lo, hi)` over k fields after merging the shared prefix: at most 2k - 1 products; the
#      maximum reached; answers equal to the integer tuple order.
# (NL) NESTED LOOPS: h in an outer loop's item, k in an inner loop inside it; pairing per pass of the DEEPEST loop
#      (k's), h one value per pass; `((h, k): >= (5, 3))`.
# Sabotage: JCFOLD_SABOTAGE=1 builds (SE) with `>=` for `>` and (RD) without the guard; the check must then differ.
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
SAB = os.environ.get("JCFOLD_SABOTAGE") == "1"
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


def padded_texts(vals, width):
    """every text of the values in vals, written with 0..width-len extra leading zeros (the `padded` reading)"""
    out = []
    for v in vals:
        s = str(v)
        for z in range(0, max(0, width - len(s)) + 1):
            out.append("0" * z + s)
    return out


def canon(s):
    return int(s)


# ---------------------------------------------------------------------------------------------------------------
# (RD) record = product, with a default. t2 := /(?<h>\d{1,2})(?::(?<m>\d\d))?/
print("\n(RD) record = product with a default: t2 & (h: S, m = v: T) vs ((h, m = v): (S, T))")
H_TXT = [str(h) for h in range(25)] + ["%02d" % h for h in range(10)]
M_TXT = ["%02d" % m for m in range(60)]
SUBJ_T2 = [h for h in H_TXT] + [h + ":" + m for h in H_TXT for m in M_TXT]
rd_before = T["cases"]
for (S_lo, S_hi), (T_op, T_b), v in itertools.product([(9, 11), (0, 23), (12, 12)], [("<", 30), (">=", 30)],
                                                      ["0", "45", "00"]):
    inS = lambda x: S_lo <= x <= S_hi
    inT = (lambda x: x < T_b) if T_op == "<" else (lambda x: x >= T_b)
    S_rx = alt(padded_texts(range(S_lo, S_hi + 1), 2))
    T_rx = alt(padded_texts([x for x in range(100) if inT(x)], 2))
    v_in_T = inT(canon(v))              # `padded` reading: the default compared as written, through padded(T)
    # RECORD route: (h: S) & (m = v: T): h in S; m present -> m in T; m absent -> v in T (a constant choice)
    rec = S_rx + "(?::" + T_rx + ")" + ("?" if v_in_T else "")
    # JOINT route: ((h, m): (S, T)) | (m unset & (h: slice of S x T at m = v)); slice = S if v in T else empty
    guard_absent = "" if SAB else "(?!:)"
    sl = S_rx if v_in_T else "(?!)"
    joint = "(?:" + S_rx + ":" + T_rx + "|" + sl + guard_absent + ("(?::\\d\\d)?" if SAB else "") + ")"
    for s in SUBJ_T2:
        h, _, m = s.partition(":")
        want = inS(int(h)) and (inT(int(m)) if m else v_in_T)
        a = check("RD rec", rec, s, want)
        b = check("RD joint", joint, s, want)
print("(RD) 18 (S, T, v) combinations x %d subjects x 2 routes: cases %d" % (len(SUBJ_T2), T["cases"] - rd_before))

# ---------------------------------------------------------------------------------------------------------------
# (RZ) labels at different depths, zero passes. P := /(?<k>\d)(?:;(?<h>\d))*/
print("\n(RZ) record at different depths: P & (h: S, k: T), k outside h's loop")
SUBJ_RZ = []
for k in range(10):
    for n in range(0, 3):
        for hs in itertools.product(range(10), repeat=n):
            SUBJ_RZ.append(str(k) + "".join(";" + str(h) for h in hs))
S_set, T_set = set(range(5)), set(range(3, 8))
S_rx, T_rx = alt([str(x) for x in S_set]), alt([str(x) for x in T_set])
# Reading A (§4.1: a record is the & of its entries): k in T, and every h in S (zero h: holds for h's entry)
readA = T_rx + "(?:;" + S_rx + ")*"
# Reading B (the k-label rule: per pass of h's loop, the pair (h_i, k) in S x T; zero passes: no pair, holds)
readB = "(?:" + T_rx + "(?:;" + S_rx + ")+|\\d)"
rz_before, rz_diff, rz_zero = T["cases"], 0, 0
for s in SUBJ_RZ:
    parts = s.split(";")
    k, hs = int(parts[0]), [int(x) for x in parts[1:]]
    wantA = k in T_set and all(h in S_set for h in hs)
    wantB = all(h in S_set and k in T_set for h in hs)
    a = check("RZ A", readA, s, wantA)
    b = check("RZ B", readB, s, wantB)
    if a != b:
        rz_diff += 1
        rz_zero += (len(hs) == 0)
print("(RZ) subjects %d; readings A and B differ on %d, all %d of them zero-pass subjects (k outside T, no h)" %
      (len(SUBJ_RZ), rz_diff, rz_zero))
print("     e.g. '9': A (record as the & of its entries) %s, B (per-pass pairing) %s" %
      (whole(readA, "9"), whole(readB, "9")))

# ---------------------------------------------------------------------------------------------------------------
# (SE) span := /(?<sh>\d{1,2}):(?<sm>\d\d)-(?<eh>\d{1,2}):(?<em>\d\d)/ & ((eh, em): padded(> ($sh, $sm)))
print("\n(SE) $-bound pair: span & ((eh, em): padded(> ($sh, $sm)))")
HRS = list(range(24))
MINS = [0, 1, 29, 30, 31, 58, 59]
H_ALL = [str(h) for h in HRS] + ["%02d" % h for h in range(10)]
branches = []
for sh in HRS:                       # one branch per CLASS of the earlier labels (§4.6): the value pair (sh, sm)
    for sm in MINS:
        # the class's end set, the dictionary expansion's two rows with this class's values as the atom:
        # eh > sh (any minute) | eh == sh, em > sm   (sabotage: em >= sm)
        row1 = alt(padded_texts([e for e in HRS if e > sh], 2)) + ":" + alt(["%02d" % m for m in MINS])
        row2 = alt(padded_texts([sh], 2)) + ":" + alt(["%02d" % m for m in MINS if (m >= sm if SAB else m > sm)])
        end = "(?:" + row1 + "|" + row2 + ")"
        branches.append(alt(padded_texts([sh], 2)) + ":" + "%02d" % sm + "-" + end)
se_rx = "(?:" + "|".join(branches) + ")"
se_before = T["cases"]
classes = len(branches)
for sh_t in H_ALL:
    for sm in MINS:
        for eh_t in ["7", "07", "9", "09", "10", "13", "23", sh_t]:
            for em in MINS:
                s = "%s:%02d-%s:%02d" % (sh_t, sm, eh_t, em)
                want = (int(eh_t), em) > (int(sh_t), sm)
                check("SE", se_rx, s, want)
print("(SE) classes %d (24 hours x %d minutes); cases %d" % (classes, len(MINS), T["cases"] - se_before))

# ---------------------------------------------------------------------------------------------------------------
# (MN) textdate := /(?<day>\d{1,2}) (?<mname>Jan|...|Dec) (?<year>\d{4})/; mnum := $mname.index
print("\n(MN) three fields with a month name: textdate & ((year, mnum, day): between((2024, 3, 15), (2025, 2, 1)))")
NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
LO, HI = (2024, 3, 15), (2025, 2, 1)


def mn_rows(lo, hi, tops):
    """between(lo, hi) as rows of per-field integer sets (dictionary order), merged on the shared prefix"""
    return between_rows(lo, hi, tops)


def between_rows(lo, hi, tops):
    """the merged expansion: shared prefix p, then the middle row, the lower branch, the upper branch"""
    k = len(lo)
    if lo > hi:
        return []
    p = 0
    while p < k and lo[p] == hi[p]:
        p += 1
    pre = [{lo[i]} for i in range(p)]
    if p == k:
        return [pre]
    rows = []
    mid = set(range(lo[p] + 1, hi[p]))
    if mid:
        rows.append(pre + [mid] + [set(range(tops[i])) for i in range(p + 1, k)])
    # lower branch: field p == lo[p], rest >= lo[p+1:] in dictionary order (j rows for j remaining fields)
    rest = k - p - 1
    if rest == 0:
        rows.append(pre + [{lo[p]}])
        rows.append(pre + [{hi[p]}])
        return rows
    for j in range(rest):
        i = p + 1 + j
        last = j == rest - 1
        rows.append(pre + [{lo[p]}] + [{lo[q]} for q in range(p + 1, i)] +
                    [set(x for x in range(tops[i]) if (x >= lo[i] if last else x > lo[i]))] +
                    [set(range(tops[q])) for q in range(i + 1, k)])
    for j in range(rest):
        i = p + 1 + j
        last = j == rest - 1
        rows.append(pre + [{hi[p]}] + [{hi[q]} for q in range(p + 1, i)] +
                    [set(x for x in range(tops[i]) if (x <= hi[i] if last else x < hi[i]))] +
                    [set(range(tops[q])) for q in range(i + 1, k)])
    return [r for r in rows if all(r)]


mn_rx_rows = []
for r in between_rows(LO, HI, (10000, 13, 32)):
    ys, ms, ds = r
    # laid over the TEXT order day, name, year; mnum's set becomes the names whose index is in it
    mn_rx_rows.append(alt([str(d) for d in ds if d >= 1]) + " " + alt([NAMES[m - 1] for m in ms if 1 <= m <= 12]) +
                      " " + alt([str(y) for y in ys if 1000 <= y <= 9999 and y in range(2022, 2028)]))
mn_rx = "(?:" + "|".join(mn_rx_rows) + ")"
mn_before = T["cases"]
for y in range(2022, 2028):
    for mi, nm in enumerate(NAMES, 1):
        for d in range(1, 32):
            s = "%d %s %d" % (d, nm, y)
            check("MN", mn_rx, s, LO <= (y, mi, d) <= HI)
print("(MN) rows %d; cases %d (years 2022-2027, 12 names, days 1-31)" % (len(mn_rx_rows), T["cases"] - mn_before))

# ---------------------------------------------------------------------------------------------------------------
# (RC) row count of between(lo, hi) over k fields, merged on the shared prefix: at most 2k - 1
print("\n(RC) rows of between(lo, hi) after merging the shared prefix, k = 2, 3, 4 (fields 0..4)")
TOP = 5
rc_before = T["cases"]
rc_engine = [0]
for k in (2, 3, 4):
    tuples = list(itertools.product(range(TOP), repeat=k))
    maxrows, over, pairs = 0, 0, 0
    for lo in tuples[::7 if k == 4 else 1]:
        for hi in tuples[::11 if k == 4 else (3 if k == 3 else 1)]:
            if lo > hi:
                continue
            pairs += 1
            rows = between_rows(lo, hi, (TOP,) * k)
            maxrows = max(maxrows, len(rows))
            over += len(rows) > 2 * k - 1
            if pairs % (1 if k == 2 else 9) == 0:      # engine-run a sample of the pairs over every subject
                rx = "(?:" + "|".join(".".join(alt([str(x) for x in f]) for f in r) for r in rows) + ")" \
                    if rows else "(?!)"
                for t in tuples:
                    check("RC k=%d" % k, rx, ".".join(map(str, t)), lo <= t <= hi)
                    rc_engine[0] += 1
            else:                                      # the rest: the rows' union checked in Python
                for t in tuples:
                    inrows = any(all(t[i] in r[i] for i in range(k)) for r in rows)
                    T["cases"] += 1
                    if inrows != (lo <= t <= hi):
                        T["differ"] += 1
    print("(RC) k=%d: bound pairs %d, max rows %d (2k - 1 = %d), pairs over the bound %d" %
          (k, pairs, maxrows, 2 * k - 1, over))
print("(RC) cases %d, of which engine-run %d (the rest: the rows' union checked in Python)" % (T["cases"] - rc_before, rc_engine[0]))

# ---------------------------------------------------------------------------------------------------------------
# (NL) nested loops. P := /(?:(?<h>\d):(?:(?<k>\d),)*;)*/ ; ((h, k): >= (5, 3))
print("\n(NL) nested loops: h in the outer item, k in an inner loop; pairing per pass of k's loop")
# per outer item: h = a, then every k in the slice {k : (a, k) >= (5, 3)}
items = []
for a in range(10):
    ks = [k for k in range(10) if (a, k) >= (5, 3)]
    items.append(str(a) + ":(?:" + alt([str(k) for k in ks]) + ",)*;")
nl_rx = "(?:" + "|".join(items) + ")*"
nl_before = T["cases"]
SUBJ_NL = []
for n in range(0, 3):
    for its in itertools.product([(4, ()), (4, (9,)), (5, ()), (5, (3,)), (5, (2,)), (5, (3, 4)), (6, (0, 1)),
                                  (5, (4, 2))], repeat=n):
        SUBJ_NL.append("".join("%d:%s;" % (a, "".join("%d," % k for k in ks)) for a, ks in its))
for s in SUBJ_NL:
    want = True
    for item in [x for x in s.split(";") if x]:
        a, _, rest = item.partition(":")
        for k in [x for x in rest.split(",") if x]:
            want = want and (int(a), int(k)) >= (5, 3)
    check("NL", nl_rx, s, want)
print("(NL) subjects %d (an outer item with no k pairs nothing: holds)" % (T["cases"] - nl_before))

print("\nTOTAL cases %d differ %d engine-disagreements %d" % (T["cases"], T["differ"], DISAGREE[0]))
