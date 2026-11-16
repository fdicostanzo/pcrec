# absent: evidence for docs/dev/lanes/absent_report.md (a condition on an ABSENT label: options side by side).
# Run: `timeout 120 python3 -I docs/dev/lanes/absent_check.py`. Sabotage: `ABSENT_SABOTAGE=1 ...` (the H unfolds
# lose their absent branch, the F unfolds gain one; the check must then differ).
#
# Method (copied from jcfix_check.py, engine helpers unedited in substance): every regex verdict is computed by
# libpcre2-8 (ctypes) AND Python `re`; the two must agree. Every subject is first checked to be a whole match of its
# operand pattern by both engines.
#
# WHAT IS RUN AND WHAT IS COMPUTED.
# - RUN: (SP) every spelling pair is checked to accept the SAME language (all strings over the row's alphabet up to
#   length 5, both engines), and the PARSE FACT each row's kind rests on (which construct the match entered) is read
#   from PCRE2's capture state through probe groups (`(?<o>...)` around the optional, `(?<e>)` in the empty branch).
# - COMPUTED: each option's answer, from the option's declared table (RESOLVE below: absence kind x option ->
#   a value, EMPTY or FAIL) evaluated on the subject split by plain string code. These are comparisons, not engine
#   verdicts.
# - ENGINE-RUN (the "unfold" checks): for (OP), (RZ), (TM), (DL) the H, F and T answers are also built as a regex from
#   the option's rule stated over intervals/sets (not from the answers) and run against the computed answer.
# - CONTROL: the T columns are compared with the earlier lanes' own functions for the ruled answers (jcfix's op_rec,
#   up_joint X/W/W'/Y; jcfold2's M on (RZ)/(ZN); unsetdef's (DL), (DA), (D1) expectations), copied here; any differ is
#   printed as a CONTROL DIFFER.
#
# Tables: (SP) spelling test; (MV) what moves, per population; (TM) the time example; (EQ) record vs `&`;
#         (DU) default.unused under each base.
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
L.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
L.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
L.pcre2_substring_number_from_name_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
ANCH, ENDANCH = 0x80000000, 0x20000000
UNSET = ctypes.c_size_t(-1).value
_cache = {}
DISAGREE = [0]
L.pcre2_config_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
_vb = ctypes.create_string_buffer(64)
L.pcre2_config_8(11, _vb)
print("libpcre2-8", _vb.value.decode(), "| Python", sys.version.split()[0])
SAB = os.environ.get("ABSENT_SABOTAGE") == "1"
if SAB:
    print("SABOTAGE ON")


def _code(p):
    if p not in _cache:
        e, o = ctypes.c_int(), ctypes.c_size_t()
        c = L.pcre2_compile_8(p.encode(), len(p.encode()), 0, ctypes.byref(e), ctypes.byref(o), None)
        assert c, (p[:80], e.value)
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
        print("  ENGINE DISAGREEMENT", repr(p[:60]), repr(t), a, b)
    return a


def is_set(p, t, name):
    """is the named group SET in PCRE2's whole match of t (and in Python's): the probe for which construct ran"""
    c = _code(p)
    md = L.pcre2_match_data_create_from_pattern_8(c, None)
    rc = L.pcre2_match_8(c, t.encode(), len(t.encode()), 0, ANCH | ENDANCH, md, None)
    assert rc >= 0, (p, t)
    n = L.pcre2_substring_number_from_name_8(c, name.encode())
    ov = L.pcre2_get_ovector_pointer_8(md)
    a = ov[2 * n] != UNSET
    L.pcre2_match_data_free_8(md)
    b = re.fullmatch(py(p), t).group(name) is not None
    if a != b:
        DISAGREE[0] += 1
        print("  PROBE DISAGREEMENT", repr(p), repr(t), name, a, b)
    return a


T = {"cases": 0, "differ": 0, "control": 0, "control_differ": 0}


def check(tag, rx, subj, want):
    got = whole(rx, subj)
    T["cases"] += 1
    if got != want:
        T["differ"] += 1
        if T["differ"] < 15:
            print("  DIFFER", tag, repr(subj), "got", got, "want", want)
    return got


def control(tag, subj, got, want):
    T["control"] += 1
    if got != want:
        T["control_differ"] += 1
        if T["control_differ"] < 15:
            print("  CONTROL DIFFER", tag, repr(subj), "got", got, "want", want)


def in_pattern(pat, subjects):
    bad = [s for s in subjects if not whole(pat, s)]
    assert not bad, (pat, bad[:3])


def alt(strings):
    strings = sorted(set(strings), key=lambda s: (-len(s), s))
    return "(?:" + "|".join(re.escape(s) for s in strings) + ")" if strings else "(?!)"


def hf(s):
    return "HOLDS" if s else "FAILS"


# =================================================================================================================
# THE OPTIONS, as ONE declared table each: (absence kind, scope) -> what the absent label contributes to its tuple.
# Kinds (where the match stopped short of the label, predicates_draft.md §4.2's "deepest construct entered"):
#   O   an optional / {0,1} around the label skipped           A   an alternative not taken
#   Z   a loop (upper bound >= 2) reached and run zero times     EO  an optional around the label's loop skipped
#   EA  an alternative around the label's loop not taken
# Scope flags: inpass (absent in one pass of an enclosing loop), elsewhere (the label has a value in another pass of
# the same match).  Results: ("val", text) the default read; EMPTY (the part ranges over its group's strings: the
# projection; for a product, the other parts tested on their own); FAIL (the tuple fails).
EMPTY, FAIL = "EMPTY", "FAIL"
OPTIONS = ["T-pass", "T-match", "X1", "H", "H-d2", "F"]


def resolve(opt, kind, default=None, inpass=False, elsewhere=False):
    dv = ("val", default) if default is not None else None
    if opt == "T-pass":         # today's line, J6 read per pass (draft :1694, §4B.1 LOOPED row)
        if kind == "Z":
            return EMPTY        # zero passes: empty, default NOT read (J7, CF 12:45; §4B.1)
        return dv or FAIL       # unset: fails unless a default (J6, CF 11:05)
    if opt == "T-match":        # today's line, J6 read per match (§4.2's per-match boundary; jcfix's W')
        if kind == "Z":
            return EMPTY
        if inpass and elsewhere:
            return EMPTY        # the label is not unset in the match: the pass reads like a zero-pass reach
        return dv or FAIL
    if opt == "X1":             # the owner's remark taken literally: every quantifier with min 0 is a loop
        if kind in ("O", "Z", "EO"):
            return dv or EMPTY  # default read on every absence (else `m = 0` on optional minutes is never read)
        return dv or FAIL       # an alternative not taken: the one "complete no set"
    if opt == "H":              # absent holds; one absence state; a default read on EVERY absence (item 7 automatic)
        return dv or EMPTY
    if opt == "H-d2":           # absent holds; a default read on a missing field, never on a zero-pass loop
        if kind == "Z":
            return EMPTY
        return dv or EMPTY
    if opt == "F":              # absent fails, the empty list included; a default read on every absence
        return dv or FAIL
    raise KeyError(opt)


def tuple_ok(R, parts, doms):
    """parts: list of text | EMPTY | FAIL | ("val", text). R: predicate over a tuple of texts. doms: the group strings
    each EMPTY part ranges over (the projection's domain: the label's group strings, jcfix's lean)"""
    if any(p == FAIL for p in parts):
        return False
    parts = [p[1] if isinstance(p, tuple) else p for p in parts]
    idx = [i for i, p in enumerate(parts) if p == EMPTY]
    if not idx:
        return R(tuple(parts))
    for combo in itertools.product(*[doms[i] for i in idx]):
        t = list(parts)
        for i, v in zip(idx, combo):
            t[i] = v
        if R(tuple(t)):
            return True
    return False


canon = lambda x: re.fullmatch(r"0|[1-9][0-9]*", x) is not None
D = [str(i) for i in range(10)]                 # \d's strings
H12 = [str(i) for i in range(10)] + ["%02d" % i for i in range(100)]    # \d{1,2}
M2 = ["%02d" % i for i in range(100)]          # \d\d

# =================================================================================================================
# (SP) THE SPELLING TEST
print("\n(SP) spelling test: `(n: <5)` on a subject where n has no value; rows grouped by EQUAL patterns")
# each row: (group id, pattern, probe pattern, probe group, subject, kind-if-probe-set, kind-if-probe-unset, scope)
# scope: "match" (set once / whole match) or (inpass, elsewhere) for a label inside a loop item.
SP = [
    # x? family: ? = (?:x|) = {0,1}
    ("q", r"(?<n>\d)?x", r"(?<n>\d)?x", "n", "x", None, "O", "match"),
    ("q", r"(?:(?<n>\d)|)x", r"(?:(?<n>\d)|(?<e>))x", "e", "x", "A", None, "match"),
    ("q", r"(?<n>\d){0,1}x", r"(?<n>\d){0,1}x", "n", "x", None, "O", "match"),
    ("q", r"(?<n>\d)??x", r"(?<n>\d)??x", "n", "x", None, "O", "match"),
    # x* family: * = (?:x+)? = (?:x+|) = (?:x*)? (greedy) = (?:x*)?? (lazy)
    ("s", r"(?<n>\d)*x", r"(?<n>\d)*x", "n", "x", None, "Z", "match"),
    ("s", r"(?:(?<n>\d)+)?x", r"(?<o>(?:(?<n>\d)+))?x", "o", "x", "?", "EO", "match"),
    ("s", r"(?:(?<n>\d)+|)x", r"(?:(?<n>\d)+|(?<e>))x", "e", "x", "EA", None, "match"),
    ("s", r"(?:(?<n>\d)*)?x", r"(?<o>(?:(?<n>\d)*))?x", "o", "x", "Z", "EO", "match"),
    ("s", r"(?:(?<n>\d)*)??x", r"(?<o>(?:(?<n>\d)*))??x", "o", "x", "Z", "EO", "match"),
    # x{0,2} family: {0,2} = (?:x{1,2})?
    ("b", r"(?<n>\d){0,2}x", r"(?<n>\d){0,2}x", "n", "x", None, "Z", "match"),
    ("b", r"(?:(?<n>\d){1,2})?x", r"(?<o>(?:(?<n>\d){1,2}))?x", "o", "x", "?", "EO", "match"),
    # x|y with the label in one branch (no equal twin among these; the alternative is the "complete no set")
    ("a", r"(?:(?<n>\d)|y)", r"(?:(?<n>\d)|(?<e>y))", "e", "y", "A", None, "match"),
    # NESTED 1: an optional inside a loop item; subjects: absent in every pass / in one pass
    ("n1", r"(?:a(?<n>\d)?,)*", r"(?:a(?<n>\d)?,)*", "n", "a,", None, "O", (True, False)),
    ("n1", r"(?:a(?:(?<n>\d)|),)*", r"(?:a(?:(?<n>\d)|(?<e>)),)*", "e", "a,", "A", None, (True, False)),
    ("n1'", r"(?:a(?<n>\d)?,)*", None, None, "a3,a,", None, "O", (True, True)),
    ("n1'", r"(?:a(?:(?<n>\d)|),)*", None, None, "a3,a,", "A", None, (True, True)),
    # NESTED 2: a loop inside a loop item, its equal spellings; subjects as above
    ("n2", r"(?:a(?<n>\d)*,)*", r"(?:a(?<n>\d)*,)*", "n", "a,", None, "Z", (True, False)),
    ("n2", r"(?:a(?:(?<n>\d)+)?,)*", r"(?:a(?<o>(?:(?<n>\d)+))?,)*", "o", "a,", "?", "EO", (True, False)),
    ("n2", r"(?:a(?:(?<n>\d)+|),)*", r"(?:a(?:(?<n>\d)+|(?<e>)),)*", "e", "a,", "EA", None, (True, False)),
    ("n2'", r"(?:a(?<n>\d)*,)*", None, None, "a3,a,", None, "Z", (True, True)),
    ("n2'", r"(?:a(?:(?<n>\d)+)?,)*", None, None, "a3,a,", "?", "EO", (True, True)),
    ("n2'", r"(?:a(?:(?<n>\d)+|),)*", None, None, "a3,a,", "EA", None, (True, True)),
    # NESTED 3: a loop inside an optional inside a loop item (lane jcfix's (UP) shape)
    ("n3", r"(?:a(?:-(?:(?<n>\d),)*)?;)*", r"(?:a(?<o>-(?:(?<n>\d),)*)?;)*", "o", "a-;", "Z", "EO", (True, False)),
    ("n3", r"(?:a(?:-|-(?:(?<n>\d),)+)?;)*", r"(?:a(?:(?<e>-)|-(?:(?<n>\d),)+)?;)*", "e", "a-;", "EA", None,
     (True, False)),
    ("n3o", r"(?:a(?:-(?:(?<n>\d),)*)?;)*", r"(?:a(?<o>-(?:(?<n>\d),)*)?;)*", "o", "a;", "Z", "EO", (True, False)),
    ("n3o", r"(?:a(?:-(?:(?<n>\d),)*|);)*", r"(?:a(?:-(?:(?<n>\d),)*|(?<e>));)*", "e", "a;", "EA", None,
     (True, False)),
    ("n3'", r"(?:a(?:-(?:(?<n>\d),)*)?;)*", None, None, "a-3,;a;", "Z", "EO", (True, True)),
    ("n3'", r"(?:a(?:-(?:(?<n>\d),)*|);)*", None, None, "a-3,;a;", "EA", None, (True, True)),
]


def lang(p, alphabet, n):
    return {"".join(w) for k in range(n + 1) for w in itertools.product(alphabet, repeat=k) if whole(p, "".join(w))}


# RUN: equal spellings accept the same language
groups = {}
for g, pat, *_ in SP:
    groups.setdefault(g.rstrip("'o"), []).append(pat)
eq_fail = 0
for g, pats in groups.items():
    pats = sorted(set(pats), key=pats.index)
    alpha = ["1", "x", "y"] if g in ("q", "s", "b", "a") else (["a", "1", ","] if g in ("n1", "n2") else
                                                               ["a", "-", "1", ",", ";"])
    n = 5 if len(alpha) <= 3 else 6
    base = lang(pats[0], alpha, n)
    for p in pats[1:]:
        same = lang(p, alpha, n) == base
        eq_fail += not same
        print("     same language as %-30s: %-32s %s (all strings over %s up to length %d)" %
              (pats[0], p, "YES" if same else "NO", "".join(alpha), n))
print("(SP) spelling pairs that are NOT the same language: %d" % eq_fail)

SP_ANS = {}
print("     %-32s %-9s %-4s %s" % ("spelling", "subject", "kind", "  ".join("%-7s" % o for o in OPTIONS)))
for g, pat, probe, pg, subj, k_set, k_unset, scope in SP:
    assert whole(pat, subj), (pat, subj)
    st = is_set(probe, subj, pg) if probe is not None else None
    if probe is None:     # PCRE keeps an earlier pass's capture, so the absent (LAST) pass is probed on its own:
        prev = [r for r in SP if r[1] == pat and r[2] is not None and subj.endswith(r[4]) and r[4] != subj][0]
        st = is_set(prev[2], prev[4], prev[3])
    kind = k_set if st else k_unset
    if kind == "?":       # the probe says the optional was ENTERED: then n's loop ran; cannot be (n absent)
        raise AssertionError((pat, subj))
    if scope == "match":
        res = {o: tuple_ok(lambda t: canon(t[0]) and int(t[0]) < 5, [resolve(o, kind)], [D]) for o in OPTIONS}
    else:
        inpass, elsewhere = scope
        # every pass is checked; the passes with n present have n = 3 (< 5): the answer is the absent pass's
        res = {o: tuple_ok(lambda t: canon(t[0]) and int(t[0]) < 5, [resolve(o, kind, inpass=inpass,
                                                                              elsewhere=elsewhere)], [D])
               for o in OPTIONS}
    SP_ANS[(g, pat, subj)] = (kind, res)
    print("     %-32s %-9r %-4s %s" % (pat, subj, kind, "  ".join("%-7s" % hf(res[o]) for o in OPTIONS)))
print("(SP) per option: number of equal-spelling groups (same pattern, same subject) whose rows DISAGREE:")
for o in OPTIONS:
    bad = []
    for g in sorted({r[0] for r in SP}):
        rows = [(p, s, SP_ANS[(gg, p, s)][1][o]) for gg, p, *_r in SP if gg == g for s in [_r[2]]]
        if len({x[2] for x in rows}) > 1:
            bad.append(g)
    print("     %-7s %d of %d groups: %s" % (o, len(bad), len({r[0] for r in SP}), " ".join(bad) or "-"))

# =================================================================================================================
# (MV) WHAT MOVES. Each population: today's answer (T-pass, T-match), each option, the count that moves.
print("\n(MV) what moves, per population (moved = differs from T-pass; 'vs T-match' where the ruled text is undecided)")
MV = {}


ADDED = set()        # populations this lane added (not one of the brief's ruled populations)


def report(name, subjects, ans, note="", added=False):
    """ans: option -> {subject: bool}"""
    MV[name] = ans
    if added:
        ADDED.add(name)
        note = (note + " [ADDED by this lane]").strip()
    base = ans["T-pass"]
    cells = []
    for o in OPTIONS:
        d = sorted([s for s in subjects if ans[o][s] != base[s]], key=lambda s: (len(s), s))
        dm = [s for s in subjects if ans[o][s] != ans["T-match"][s]]
        cells.append((o, len(d), d[:2], len(dm)))
    print("(MV) %-44s %5d subjects %s" % (name, len(subjects), note))
    for o, n, ex, nm in cells:
        print("       %-7s moves %5d vs T-pass (e.g. %-24s) %5d vs T-match" % (o, n, ", ".join(repr(x) for x in ex)
                                                                              or "-", nm))


# ---- (U) optional seconds, ((h, m, s): padded(>= (9, 0, 30))) : set-once O
U_SUBJ = ["9:00", "9:00:29", "9:00:30", "10:00", "10:00:00", "8:59:59", "9:01"]
P_U = r"(?<h>\d{1,2}):(?<m>\d\d)(?::(?<s>\d\d))?"
in_pattern(P_U, U_SUBJ)
RU = lambda t: all(x.isdigit() for x in t) and tuple(int(x) for x in t) >= (9, 0, 30)
ans = {o: {} for o in OPTIONS}
for sbj in U_SUBJ:
    p = sbj.split(":")
    for o in OPTIONS:
        parts = p[:2] + ([p[2]] if len(p) == 3 else [resolve(o, "O")])
        ans[o][sbj] = tuple_ok(RU, parts, [None, None, M2])
    control("U", sbj, ans["T-pass"][sbj], len(p) == 3 and RU(tuple(p)))     # jointexp's (U): no tuple, false
report("(U) ((h, m, s): padded(>= (9, 0, 30)))", U_SUBJ, ans)

# ---- (S) strict, minutes optional, ((h, m): padded(> (9, 30)))
S_SUBJ = ["9", "10", "8", "9:31", "9:30", "10:00"]
RS = lambda t: all(x.isdigit() for x in t) and tuple(int(x) for x in t) > (9, 30)
ans = {o: {} for o in OPTIONS}
for sbj in S_SUBJ:
    p = sbj.split(":")
    for o in OPTIONS:
        ans[o][sbj] = tuple_ok(RS, [p[0], p[1] if len(p) == 2 else resolve(o, "O")], [None, M2])
    control("S", sbj, ans["T-pass"][sbj], len(p) == 2 and RS(tuple(p)))
report("(S) ((h, m): padded(> (9, 30))), m optional", S_SUBJ, ans)

# ---- (TM) the time example: t2 & ((h, m [= 0]): >= (9, 30)), the DOM reading (canonical numerals)
print("\n(TM) the time example: t2 := /(?<h>\\d{1,2})(?::(?<m>\\d\\d))?/ & ((h, m): >= (9, 30)), with and without m = 0")
P_T2 = r"(?<h>\d{1,2})(?::(?<m>\d\d))?"
RT = lambda t: canon(t[0]) and canon(t[1]) and (int(t[0]), int(t[1])) >= (9, 30)
TM = {}
for dflt in (None, "0"):
    for sbj in ("9", "10", "9:15", "9:45"):
        p = sbj.split(":")
        TM[(dflt, sbj)] = {o: tuple_ok(RT, [p[0], p[1] if len(p) == 2 else resolve(o, "O", dflt)], [None, M2])
                           for o in OPTIONS}
    print("     %-12s %s" % ("no default" if dflt is None else "m = 0", "  ".join(
        "%s: %s" % (s, "/".join("%s=%s" % (o, "H" if TM[(dflt, s)][o] else "F") for o in OPTIONS))
        for s in ("9", "10", "9:15", "9:45"))))
# ENGINE-RUN over the whole t2 population (11,110): each option's rule built as a regex from intervals:
#   present part: h canonical, m canonical, (h, m) >= (9, 30); absent part: T/F: the default's slice (h with (h, 0)
#   >= (9, 30)) or nothing; H: the projection (h canonical with SOME m in \d\d canonical making it >= (9, 30)).
SUBJ_T2 = H12 + [h + ":" + m for h in H12 for m in M2]
in_pattern(P_T2, SUBJ_T2[::37])
present = "(?:" + alt([h for h in H12 if canon(h) and int(h) > 9]) + ":" + alt([m for m in M2 if canon(m)]) + "|9:" + \
    alt([m for m in M2 if canon(m) and int(m) >= 30]) + ")"
proj = alt([h for h in H12 if canon(h) and int(h) >= 9])        # some canonical m: m = 30 .. 99 for h = 9
slice0 = alt([h for h in H12 if canon(h) and int(h) >= 10])     # (h, 0) >= (9, 30)
for o, dflt, absent in (("T-pass", None, None), ("F", None, None), ("H", None, proj), ("T-pass", "0", slice0),
                        ("F", "0", slice0), ("H", "0", slice0)):
    if SAB and o == "H" and dflt is None:
        absent = None
    if SAB and o == "F" and dflt is None:
        absent = proj
    rx = "(?:" + present + ("|" + absent if absent else "") + ")"
    for sbj in SUBJ_T2:
        p = sbj.split(":")
        want = tuple_ok(RT, [p[0], p[1] if len(p) == 2 else resolve(o, "O", dflt)], [None, M2])
        check("TM %s %s" % (o, dflt), rx, sbj, want)
    acc = sum(1 for sbj in SUBJ_T2 if ":" not in sbj and whole(rx, sbj))
    print("     engine-run %-7s %-10s over %d subjects: minutes-absent subjects accepted %d" %
          (o, "m = 0" if dflt else "no default", len(SUBJ_T2), acc))

# ---- (D1) single-label defaults on t2, (m = v: <30) for v in none, 0, 45, 00 (canonical numerals)
print()
LT30 = lambda t: canon(t[0]) and int(t[0]) < 30
DU = {}
for v in (None, "0", "45", "00"):
    ans = {o: {} for o in OPTIONS}
    for sbj in SUBJ_T2:
        p = sbj.split(":")
        for o in OPTIONS:
            ans[o][sbj] = tuple_ok(LT30, [p[1] if len(p) == 2 else resolve(o, "O", v)], [M2])
        if v is not None:
            control("D1", sbj, ans["T-pass"][sbj], LT30((p[1] if len(p) == 2 else v,)))
    DU[v] = ans
    report("(D1) t2 & (m%s: <30)" % ("" if v is None else " = " + v), SUBJ_T2, ans, added=v is None)
print("(DU) default.unused: is `(m = v: <30)` answer-identical to `(m: <30)` (no default) under each base?")
for v in ("0", "45", "00"):
    print("     m = %-3s %s" % (v, "  ".join("%s=%s" % (o, "UNUSED" if all(DU[v][o][s] == DU[None][o][s] for s in SUBJ_T2)
                                                    else "used") for o in OPTIONS)))

# ---- (DA) the other alternative taken: /(?<h>\d{1,2})(?::(?<m>\d\d)| o'clock)/ & ((h, m [= 0]): padded(between))
P_DA = r"(?<h>\d{1,2})(?::(?<m>\d\d)| o'clock)"
SUBJ_DA = [h + " o'clock" for h in H12] + [h + ":" + m for h in H12 for m in M2]
in_pattern(P_DA, SUBJ_DA[::41] + SUBJ_DA[:110])
RB = lambda t: all(x.isdigit() for x in t) and (9, 30) <= (int(t[0]), int(t[1])) <= (11, 0)
for dflt in (None, "0"):
    ans = {o: {} for o in OPTIONS}
    for sbj in SUBJ_DA:
        if sbj.endswith(" o'clock"):
            h, m = sbj[:-8], None
        else:
            h, m = sbj.split(":")
        for o in OPTIONS:
            ans[o][sbj] = tuple_ok(RB, [h, m if m is not None else resolve(o, "A", dflt)], [None, M2])
        if dflt is not None:
            control("DA", sbj, ans["T-pass"][sbj], RB((h, m if m is not None else "0")))
    report("(DA) o'clock & ((h, m%s): padded(between((9,30),(11,0))))" % ("" if dflt is None else " = 0"),
           SUBJ_DA, ans, added=True)

# ---- L56 / L65 witnesses (predicates_draft.md §4.2, §0.1)
print()
WIT = [(r"x|(?<n>\d)+", "x", "EA", "match"), (r"(?:(?<n>\d),)*", "", "Z", "match"),
       (r"(?:(?<n>\d)+)?x", "x", "EO", "match"), (r"(?<n>\d)?x", "x", "O", "match"), (r"(?<n>\d)*x", "x", "Z", "match")]
ans = {o: {} for o in OPTIONS}
for pat, sbj, kind, _ in WIT:
    assert whole(pat, sbj)
    for o in OPTIONS:
        ans[o][pat] = tuple_ok(lambda t: canon(t[0]) and int(t[0]) < 5, [resolve(o, kind)], [D])
report("(L56/L65) the draft's witnesses, (n: <5)", [w[0] for w in WIT], ans)
for pat, sbj, kind, _ in WIT:
    print("       /%s/ on %-4r %s" % (pat, sbj, " ".join("%s=%s" % (o, hf(ans[o][pat])) for o in OPTIONS)))

# ---- (RZ) /(?<k>\d)(?:;(?<h>\d))*/ & (h: <5, k: 3..7): zero passes Z; the record and the `&`
SUBJ_RZ = [k + "".join(";" + h for h in hs) for k in D for n in range(3) for hs in itertools.product(D, repeat=n)]
P_RZ = r"(?<k>\d)(?:;(?<h>\d))*"
in_pattern(P_RZ, SUBJ_RZ)
S5 = lambda x: canon(x) and int(x) < 5
T37 = lambda x: canon(x) and 3 <= int(x) <= 7


def rz_rec(o, sbj, Rf=lambda t: S5(t[0]) and T37(t[1]), dflt=None):
    k, *hs = sbj.split(";")
    if not hs:
        return tuple_ok(Rf, [resolve(o, "Z", dflt), k], [D, None])
    return all(tuple_ok(Rf, [h, k], [None, None]) for h in hs)


def rz_amp(o, sbj):
    k, *hs = sbj.split(";")
    hpart = tuple_ok(lambda t: S5(t[0]), [resolve(o, "Z")], [D]) if not hs else all(S5(h) for h in hs)
    return hpart and T37(k)


EQ = {}
ans = {o: {s: rz_rec(o, s) for s in SUBJ_RZ} for o in OPTIONS}
for s in SUBJ_RZ:   # control: jcfold2's M on (RZ) = the `&` reading (0 of 1,110 differ there)
    k, *hs = s.split(";")
    control("RZ", s, ans["T-pass"][s], T37(k) and all(S5(h) for h in hs))
report("(RZ) (h: <5, k: 3..7), h looped", SUBJ_RZ, ans)
EQ["RZ"] = {o: sum(rz_rec(o, s) != rz_amp(o, s) for s in SUBJ_RZ) for o in OPTIONS}
# ENGINE-RUN: T/H `k(?:;h)*` vs F `k(?:;h)+`
Trx, Srx = alt([x for x in D if T37(x)]), alt([x for x in D if S5(x)])
for o, q in (("T-pass", "*"), ("H", "*"), ("F", "+")):
    qq = q if not SAB else {"*": "+", "+": "*"}[q]
    rx = Trx + "(?:;" + Srx + ")" + qq
    for s in SUBJ_RZ:
        check("RZ " + o, rx, s, ans[o][s])
# (ZD a) the same with a default on the looped label: (h = 9: <5, k: 3..7)
ans = {o: {s: rz_rec(o, s, dflt="9") for s in SUBJ_RZ} for o in OPTIONS}
report("(ZD a) (h = 9: <5, k: 3..7)", SUBJ_RZ, ans)

# ---- (ZJ) non-product joint sets on (RZ)'s pattern, zero passes; per option
ZJ = [("((h, k): >= (5, 3))", lambda t: canon(t[0]) and (int(t[0]), int(t[1])) >= (5, 3)),
      ("((k, h): >= (5, 3))", lambda t: canon(t[0]) and (int(t[1]), int(t[0])) >= (5, 3)),
      ("((h, k): (0|1|2, 3|4) | (5, 5))", lambda t: (t[0] in "012" and t[1] in "34") or (t[0] == "5" and t[1] == "5")),
      ("((h, k): (\"x\", 3) | (0, 5))", lambda t: (t[0] == "x" and t[1] == "3") or (t[0] == "0" and t[1] == "5")),
      ("((h, k): < (0, 3))", lambda t: canon(t[0]) and (int(t[0]), int(t[1])) < (0, 3))]
zj_all = {o: {} for o in OPTIONS}
for name, Rf in ZJ:
    for o in OPTIONS:
        for s in SUBJ_RZ:
            zj_all[o][name + " " + s] = rz_rec(o, s, Rf=Rf)
report("(ZJ) five non-product sets on (RZ)'s pattern", list(zj_all["T-pass"]), zj_all)

# ---- (ZN) nested: /(?<c>\d)(?:;(?<h>\d)(?::(?<k>\d))*)*/ & (c: 3..7, h: 0..4, k: 2..6)
ITEMS = [(h, ks) for h in ("0", "4", "5", "9") for ks in [(), ("2",), ("9",), ("3", "6"), ("6", "0")]]
SUBJ_ZN = [c + "".join(";%s%s" % (h, "".join(":" + k for k in ks)) for h, ks in its)
           for c in ("0", "2", "3", "5", "7", "8") for n in range(3) for its in itertools.product(ITEMS, repeat=n)]
in_pattern(r"(?<c>\d)(?:;(?<h>\d)(?::(?<k>\d))*)*", SUBJ_ZN)
C37, H04, K26 = T37, S5, (lambda x: canon(x) and 2 <= int(x) <= 6)


def split_zn(s):
    p = s.split(";")
    return p[0], [(q.split(":")[0], q.split(":")[1:]) for q in p[1:]]


def zn_rec(o, s):
    c, its = split_zn(s)
    Rf = lambda t: C37(t[0]) and H04(t[1]) and K26(t[2])
    if not its:
        return tuple_ok(Rf, [c, resolve(o, "Z"), resolve(o, "Z")], [None, D, D])
    for h, ks in its:
        if not ks:
            if not tuple_ok(Rf, [c, h, resolve(o, "Z")], [None, None, D]):
                return False
        elif not all(Rf((c, h, k)) for k in ks):
            return False
    return True


def zn_amp(o, s):
    c, its = split_zn(s)
    ok = C37(c)
    hs = [h for h, _ in its]
    ok = ok and (all(H04(h) for h in hs) if its else tuple_ok(lambda t: H04(t[0]), [resolve(o, "Z")], [D]))
    for h, ks in its:          # k: per reach of its loop (each outer pass reaches it)
        ok = ok and (all(K26(k) for k in ks) if ks else tuple_ok(lambda t: K26(t[0]), [resolve(o, "Z")], [D]))
    if not its:
        ok = ok and tuple_ok(lambda t: K26(t[0]), [resolve(o, "Z")], [D])
    return ok


ans = {o: {s: zn_rec(o, s) for s in SUBJ_ZN} for o in OPTIONS}
for s in SUBJ_ZN:  # control: (ZN) M = the `&` reading (jcfold2: 0 of 2,526)
    c, its = split_zn(s)
    control("ZN", s, ans["T-pass"][s], C37(c) and all(H04(h) for h, _ in its) and all(K26(k) for _, ks in its
                                                                                       for k in ks))
report("(ZN) (c: 3..7, h: 0..4, k: 2..6), nested", SUBJ_ZN, ans)
EQ["ZN"] = {o: sum(zn_rec(o, s) != zn_amp(o, s) for s in SUBJ_ZN) for o in OPTIONS}

# ---- (OP) /(?:(?<h>\d+)(?::(?<m>\d\d))?,)*/ & (h: <10, m: <30): an optional inside a pass
P_OP = r"(?:(?<h>\d+)(?::(?<m>\d\d))?,)*"
OP_ITEMS = [(h, m) for h in ("3", "12") for m in (None, "15", "45")]
SUBJ_OP = ["".join("%s%s," % (h, "" if m is None else ":" + m) for h, m in its)
           for n in range(4) for its in itertools.product(OP_ITEMS, repeat=n)]
in_pattern(P_OP, SUBJ_OP)
Sh = lambda x: canon(x) and int(x) < 10
Tm = lambda x: canon(x) and int(x) < 30


def split_op(s):
    return [(it.split(":")[0], it.split(":")[1] if ":" in it else None) for it in s.split(",")[:-1]]


def op_rec(o, s, Rf=lambda t: Sh(t[0]) and Tm(t[1]), dflt=None, mdom=M2):
    its = split_op(s)
    if not its:
        return tuple_ok(Rf, [resolve(o, "Z"), resolve(o, "Z", dflt)], [H12, mdom])
    any_m = any(m is not None for _, m in its)
    return all(tuple_ok(Rf, [h, m if m is not None else resolve(o, "O", dflt, inpass=True, elsewhere=any_m)],
                        [None, mdom]) for h, m in its)


def op_amp(o, s):
    its = split_op(s)
    if not its:
        return tuple_ok(lambda t: Sh(t[0]), [resolve(o, "Z")], [H12]) and \
            tuple_ok(lambda t: Tm(t[0]), [resolve(o, "Z")], [M2])
    any_m = any(m is not None for _, m in its)
    return all(Sh(h) for h, _ in its) and all(
        tuple_ok(lambda t: Tm(t[0]), [m if m is not None else resolve(o, "O", inpass=True, elsewhere=any_m)], [M2])
        for _, m in its)


ans = {o: {s: op_rec(o, s) for s in SUBJ_OP} for o in OPTIONS}
for s in SUBJ_OP:  # control: jcfix's op_rec (the record: a pass whose m is unset FAILS) = T-pass
    control("OP", s, ans["T-pass"][s], all(m is not None and Sh(h) and Tm(m) for h, m in split_op(s)))
    its = split_op(s)   # jcfix's (B) per-match single-label reading + h = T-match's `&`
    ms = [m for _, m in its if m is not None]
    control("OP&B", s, op_amp("T-match", s), (not its or bool(ms)) and all(Sh(h) for h, _ in its) and
            all(Tm(m) for m in ms))
report("(OP) (h: <10, m: <30), m optional in each item", SUBJ_OP, ans)
EQ["OP"] = {o: sum(op_rec(o, s) != op_amp(o, s) for s in SUBJ_OP) for o in OPTIONS}
# ENGINE-RUN: H `(?:h(?::m)?,)*`; F `(?:h:m,)+`; T-pass `(?:h:m,)*`; T-match `|(?:h,)*h:m,(?:h(?::m)?,)*`
H10 = alt([x for x in ("3", "12") if Sh(x)] + [str(i) for i in range(10)])
M30 = alt([str(i) for i in range(10, 30)])
OPRX = {"H": "(?:" + H10 + ("(?::" + M30 + ")?" if not SAB else ":" + M30) + ",)*",
        "F": "(?:" + H10 + ":" + M30 + ",)" + ("+" if not SAB else "*"),
        "T-pass": "(?:" + H10 + ":" + M30 + ",)*",
        "T-match": "(?:|(?:" + H10 + ",)*" + H10 + ":" + M30 + ",(?:" + H10 + "(?::" + M30 + ")?,)*)"}
for o, rx in OPRX.items():
    for s in SUBJ_OP:
        check("OP " + o, rx, s, ans[o][s])
for s in ("", "3,", "3:15,", "3:15,3,", "3:45,3,"):
    print("       %-10r %s" % (s, " ".join("%s=%s" % (o, hf(ans[o][s])) for o in OPTIONS)))

# ---- (UP) /(?:(?<h>\d)(?:-(?:(?<k>\d),)*)?;)*/ & (h: <5, k: <5): a loop inside an optional inside a pass
P_UP = r"(?:(?<h>\d)(?:-(?:(?<k>\d),)*)?;)*"
UP_ITEMS = [(h, ks) for h in ("3", "4", "9") for ks in [None, (), ("2",), ("7",), ("2", "7")]]
SUBJ_UP = ["".join("%s%s;" % (h, "" if ks is None else "-" + "".join(k + "," for k in ks)) for h, ks in its)
           for n in range(3) for its in itertools.product(UP_ITEMS, repeat=n)]
in_pattern(P_UP, SUBJ_UP)


def split_up(s):
    out = []
    for it in s.split(";")[:-1]:
        if "-" in it:
            h, rest = it.split("-")
            out.append((h, [x for x in rest.split(",") if x]))
        else:
            out.append((it, None))
    return out


def up_rec(o, s, Rf=lambda t: S5(t[0]) and S5(t[1])):
    its = split_up(s)
    if not its:
        return tuple_ok(Rf, [resolve(o, "Z"), resolve(o, "Z")], [D, D])
    any_reach = any(ks is not None for _, ks in its)
    for h, ks in its:
        if ks is None:
            part = resolve(o, "EO", inpass=True, elsewhere=any_reach)
        elif not ks:
            part = resolve(o, "Z")
        else:
            if not all(Rf((h, k)) for k in ks):
                return False
            continue
        if not tuple_ok(Rf, [h, part], [None, D]):
            return False
    return True


def up_amp(o, s):
    its = split_up(s)
    if not its:
        return tuple_ok(lambda t: S5(t[0]), [resolve(o, "Z")], [D]) and tuple_ok(lambda t: S5(t[0]), [resolve(o, "Z")],
                                                                                [D])
    any_reach = any(ks is not None for _, ks in its)
    ok = all(S5(h) for h, _ in its)
    for _, ks in its:
        if ks is None:
            part = resolve(o, "EO", inpass=True, elsewhere=any_reach)
            ok = ok and tuple_ok(lambda t: S5(t[0]), [part], [D])
        elif not ks:
            ok = ok and tuple_ok(lambda t: S5(t[0]), [resolve(o, "Z")], [D])
        else:
            ok = ok and all(S5(k) for k in ks)
    return ok


def jcfix_up_joint(its, reading):      # COPIED from jcfix_check.py (control), texts mapped to ints
    its = [(int(h), None if ks is None else [int(k) for k in ks]) for h, ks in its]
    R = lambda h, k: h < 5 and k < 5
    poss = lambda h: h < 5
    if not its:
        return True
    never = all(ks is None for _, ks in its)
    for h, ks in its:
        if ks is None:
            if reading == "Y":
                return False
            if reading == "W'" and never:
                return False
            if not poss(h):
                return False
            continue
        if not ks and not poss(h):
            return False
        if any(not R(h, k) for k in ks):
            return False
    return True


ans = {o: {s: up_rec(o, s) for s in SUBJ_UP} for o in OPTIONS}
for s in SUBJ_UP:
    control("UP Y", s, ans["T-pass"][s], jcfix_up_joint(split_up(s), "Y"))
    control("UP W'", s, ans["T-match"][s], jcfix_up_joint(split_up(s), "W'"))
    control("UP W", s, ans["H"][s], jcfix_up_joint(split_up(s), "W"))
report("(UP) (h: <5, k: <5), k's loop in an optional", SUBJ_UP, ans)
EQ["UP"] = {o: sum(up_rec(o, s) != up_amp(o, s) for s in SUBJ_UP) for o in OPTIONS}
for s in ("", "3;", "3-;", "3-2,;9;", "3-2,;4;", "3-2,;3;"):
    print("       %-10r %s" % (s, " ".join("%s=%s" % (o, hf(ans[o][s])) for o in OPTIONS)))

# ---- (DL) /(?:(?<h>\d{1,2})(?::(?<m>\d\d))?,)*/ & ((h, m = 0): padded(between((9, 30), (11, 0))))
DL_ITEMS = ["9", "10", "11", "12", "9:45", "9:15", "10:30", "11:30"]
SUBJ_DL = ["".join(c + "," for c in combo) for n in range(4) for combo in itertools.product(DL_ITEMS, repeat=n)]
in_pattern(r"(?:(?<h>\d{1,2})(?::(?<m>\d\d))?,)*", SUBJ_DL)
for dflt in ("0", None):
    ans = {o: {s: op_rec(o, s, Rf=RB, dflt=dflt, mdom=M2) for s in SUBJ_DL} for o in OPTIONS}
    if dflt == "0":
        for s in SUBJ_DL:  # control: unsetdef's (DL) expectation (per item, the default read; empty list holds)
            want = all(RB((c.split(":")[0], c.split(":")[1] if ":" in c else "0")) for c in s.split(",")[:-1])
            control("DL", s, ans["T-pass"][s], want)
        # ENGINE-RUN: H (= T-pass here, item: present in range | h in the slice at 0) and F (non-empty list)
        pres = "(?:" + alt(["9", "09"]) + ":" + alt([m for m in M2 if int(m) >= 30]) + "|" + alt(["10"]) + ":" + \
            alt(M2) + "|11:00)"
        item = "(?:" + pres + "|" + alt(["10", "11"]) + "),"
        for o, rx in (("H", "(?:" + item + ")*"), ("F", "(?:" + item + ")" + ("+" if not SAB else "*"))):
            for s in SUBJ_DL:
                check("DL " + o, rx, s, ans[o][s])
    report("(DL) list & ((h, m%s): padded(between((9,30),(11,0))))" % (" = 0" if dflt else ""), SUBJ_DL, ans,
           added=dflt is None)
    for s in ("", "9,", "10,", "10,9:45,", "11,9:45,", "9,10:30,"):
        print("       %-10r %s" % (s, " ".join("%s=%s" % (o, hf(ans[o][s])) for o in OPTIONS)))

# ---- (ZD b) the loop NEVER REACHED: /(?<k>\d)(?:-(?:;(?<h>\d))*)?/ & (h [= v]: <5, k: 3..7)
SUBJ_P2 = D + [k + "-" + "".join(";" + h for h in hs) for k in D for n in range(3) for hs in itertools.product(D, repeat=n)]
in_pattern(r"(?<k>\d)(?:-(?:;(?<h>\d))*)?", SUBJ_P2)
for dflt in (None, "9", "2"):
    ans = {o: {} for o in OPTIONS}
    for s in SUBJ_P2:
        k = s[0]
        for o in OPTIONS:
            if "-" not in s:
                part = resolve(o, "EO", dflt)
                ans[o][s] = tuple_ok(lambda t: S5(t[0]) and T37(t[1]), [part, k], [D, None])
            else:
                hs = [x for x in s.split("-")[1].split(";") if x]
                ans[o][s] = all(S5(h) and T37(k) for h in hs) if hs else \
                    tuple_ok(lambda t: S5(t[0]) and T37(t[1]), [resolve(o, "Z", dflt), k], [D, None])
        want = (T37(k) and dflt is not None and S5(dflt)) if "-" not in s else \
            (T37(k) and all(S5(h) for h in [x for x in s.split("-")[1].split(";") if x]))
        control("ZD b", s, ans["T-pass"][s], want)
    report("(ZD b) never reached, (h%s: <5, k: 3..7)" % ("" if dflt is None else " = " + dflt), SUBJ_P2, ans)

# ---- (ZD c) /(?:(?<h>\d)(?::(?<m>\d))?,)*/ & ((h, m = 0): >= (5, 3))
SUBJ_L = [""] + ["".join("%s%s," % (h, "" if m is None else ":" + m) for h, m in its)
                 for n in (1, 2) for its in itertools.product([(h, m) for h in "456" for m in (None, "0", "3")],
                                                              repeat=n)]
R53 = lambda t: canon(t[0]) and canon(t[1]) and (int(t[0]), int(t[1])) >= (5, 3)
ans = {o: {s: op_rec(o, s, Rf=R53, dflt="0", mdom=D) for s in SUBJ_L} for o in OPTIONS}
for s in SUBJ_L:
    want = all(R53((it.partition(":")[0], it.partition(":")[2] or "0")) for it in s.split(",") if it)
    control("ZD c", s, ans["T-pass"][s], want)
report("(ZD c) ((h, m = 0): >= (5, 3)), looped", SUBJ_L, ans)

# =================================================================================================================
print("\n(EQ) record vs `&` of its one-label conditions, each under the SAME option: subjects that differ")
for pop, d in EQ.items():
    print("     %-3s %s" % (pop, "  ".join("%s=%d" % (o, d[o]) for o in OPTIONS)))
# crossing T's sub-readings: the record under one, the `&` under the other
print("     crossed: OP record T-pass vs & T-match: %d; UP record T-pass vs & T-match: %d; UP record T-match vs & "
      "T-pass: %d" % (sum(op_rec("T-pass", s) != op_amp("T-match", s) for s in SUBJ_OP),
                      sum(up_rec("T-pass", s) != up_amp("T-match", s) for s in SUBJ_UP),
                      sum(up_rec("T-match", s) != up_amp("T-pass", s) for s in SUBJ_UP)))

# =================================================================================================================
for which, keep in (("the RULED populations (the brief's list)", lambda n: n not in ADDED),
                    ("the populations ADDED by this lane", lambda n: n in ADDED)):
    print("\n(MV) TOTAL moved answers per option over %s (vs T-pass / vs T-match)" % which)
    tot = {o: [0, 0, 0] for o in OPTIONS}
    for name, a in MV.items():
        if not keep(name):
            continue
        for o in OPTIONS:
            subs = list(a["T-pass"])
            tot[o][0] += sum(a[o][s] != a["T-pass"][s] for s in subs)
            tot[o][1] += sum(a[o][s] != a["T-match"][s] for s in subs)
            tot[o][2] += len(subs)
    for o in OPTIONS:
        print("     %-7s %6d / %6d of %d" % (o, tot[o][0], tot[o][1], tot[o][2]))

# =================================================================================================================
# (AU) AUTHOR-WRITTEN FORMS: can an author reach another option's answers with today's tools (a default)?
print("\n(AU) author forms on (OP) and (DL, no default): a default written to reproduce another option's answers")


def rec_defaults(o, s, Rf, dh, dm, mdom, hdom):
    its = split_op(s)
    if not its:
        return tuple_ok(Rf, [resolve(o, "Z", dh), resolve(o, "Z", dm)], [hdom, mdom])
    any_m = any(m is not None for _, m in its)
    return all(tuple_ok(Rf, [h, m if m is not None else resolve(o, "O", dm, inpass=True, elsewhere=any_m)],
                        [None, mdom]) for h, m in its)


OPR = lambda t: Sh(t[0]) and Tm(t[1])
for label, pop, Rf, mdom, tgt, form in (
        ("(OP)", SUBJ_OP, OPR, M2, "T-pass", ("H", None, "x")),     # H + a sentinel default outside the set
        ("(OP)", SUBJ_OP, OPR, M2, "H", ("F", None, "0")),          # F + a default inside the set (m only)
        ("(OP)", SUBJ_OP, OPR, M2, "H", ("F", "0", "0")),           # F + defaults on every label
        ("(DL)", SUBJ_DL, RB, M2, "T-pass", ("H", None, "x")),
        ("(DL)", SUBJ_DL, RB, M2, "H", ("F", "10", "0"))):
    o, dh, dm = form
    target = {s: rec_defaults(tgt, s, Rf, None, None, mdom, H12) for s in pop}
    got = {s: rec_defaults(o, s, Rf, dh, dm, mdom, H12) for s in pop}
    d = sorted([s for s in pop if target[s] != got[s]], key=lambda s: (len(s), s))
    print("     %s %s with h%s, m = %s vs %s with no default: differ %d of %d  e.g. %s" %
          (label, o, "" if dh is None else " = " + dh, dm, tgt, len(d), len(pop), d[:3]))

# =================================================================================================================
# (ZE) jcfix's zero-pass-empty corner under each option: /(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*/, a = 0 makes both sets
# EMPTY: C1 `(h: <$a, k: 3)` (a record), C2 `((h, k): < ($a, 0))`, and C1's `&` form `(h: <$a) & (k: 3)`.
# NOTE: every option here reads a one-label condition's absent part by the SAME projection as a joint one (EMPTY ranges
# over the group's strings); today's ruled single-label zero-pass rule is "holds" (vacuous). The two agree except on a
# set that is empty for this match; the row "T (vacuous)" shows today's ruled `&` there.
print("\n(ZE) zero-pass-empty under each option (a = 0: both sets empty); 11,100 subjects, a, k in 0..9, 0-2 passes")
SUBJ_ZE = ["%d-%d" % (a, k) + "".join(";%d" % h for h in hs) for a in range(10) for k in range(10) for n in range(3)
           for hs in itertools.product(range(10), repeat=n)]
in_pattern(r"(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*", SUBJ_ZE[::7])
A0 = [x for x in SUBJ_ZE if x.startswith("0-")]


def ze(o, x, which):
    head, *hs = x.split(";")
    a, k = head.split("-")
    lt = lambda h: canon(h) and int(h) < int(a)
    if which == "C1":
        Rf = lambda t: lt(t[0]) and t[1] == "3"
    elif which == "C2":
        Rf = lambda t: canon(t[0]) and (int(t[0]), int(t[1])) < (int(a), 0)
    else:  # the `&` of C1's one-label conditions
        hpart = all(lt(h) for h in hs) if hs else tuple_ok(lambda t: lt(t[0]), [resolve(o, "Z")], [D])
        return hpart and k == "3"
    if not hs:
        return tuple_ok(Rf, [resolve(o, "Z"), k], [D, None])
    return all(Rf((h, k)) for h in hs)


for o in OPTIONS:
    c1c2 = [x for x in A0 if ze(o, x, "C1") != ze(o, x, "C2")]
    c1amp = [x for x in SUBJ_ZE if ze(o, x, "C1") != ze(o, x, "AMP")]
    print("     %-7s C1 vs C2 at a = 0: %d of %d differ %s; C1 vs its & form: %d of %d differ; '0-3': C1 %s, C2 %s"
          % (o, len(c1c2), len(A0), c1c2[:2], len(c1amp), len(SUBJ_ZE), hf(ze(o, "0-3", "C1")), hf(ze(o, "0-3", "C2"))))
vac = lambda x: (x.split(";")[0].split("-")[1] == "3") and all(int(h) < int(x[0]) for h in x.split(";")[1:])
print("     T (vacuous one-label rule, today's ruled `&`) on '0-3': %s; C1 under T's projection vs it: %d of %d differ"
      % (hf(vac("0-3")), sum(ze("T-pass", x, "C1") != vac(x) for x in SUBJ_ZE), len(SUBJ_ZE)))

# =================================================================================================================
# (R2) the owner's optional mark (rulings R2): base "a condition needs a text" (absent FAILS); the author marks
# absence acceptable. Placeholders: on the FILTER `(h: S?)` / `((h, m): R?)`, on the LABEL `(h?: S)` / `((h, m?): R)`.
# A marked absent part is read by the CONDITION (R1: no set holds absence): SOME reading = the condition holds if
# some text of the label's group would satisfy it (the projection); VACUOUS reading of a whole-filter mark = the
# condition holds outright when a marked label is absent. Compared with the hand alternative `| (h: 10)` (unsetdef's
# "does not matter", the EVERY reading of §4B.6) and with H. COMPUTED; t2 population as (TM), plus `8`, `11`.
print("\n(R2) optional mark on t2 & ((h, m): padded(between((9, 30), (11, 0)))) and on ((h, m): >= (9, 30)), DOM")
GE930 = RT
BTW = RB
forms = {}
for rname, Rf in (("between((9,30),(11,0)) padded", BTW), (">= (9, 30)", GE930)):
    res = {}
    for sbj in SUBJ_T2:
        p = sbj.split(":")
        h, m = p[0], (p[1] if len(p) == 2 else None)
        if m is not None:
            v = Rf((h, m))
            res[sbj] = dict(neither=v, dflt0=v, mark_label=v, mark_filter_vacuous=v, hand=v, H=v)
            continue
        res[sbj] = dict(
            neither=False,                                                   # base: absent FAILS
            dflt0=Rf((h, "0")),                                              # m = 0
            mark_label=tuple_ok(Rf, [h, EMPTY], [None, M2]),                 # (h, m?): R, the SOME reading
            mark_filter_vacuous=True,                                        # ((h, m): R?) read as "holds outright"
            hand=(h.isdigit() and int(h) == 10),                             # ... | (h: 10), unsetdef's spelling
            H=tuple_ok(Rf, [h, resolve("H", "O")], [None, M2]))
    forms[rname] = res
    keys = ["neither", "dflt0", "mark_label", "mark_filter_vacuous", "hand", "H"]
    print("     R = %s" % rname)
    for sbj in ("8", "9", "10", "11", "9:15", "9:45"):
        print("       %-5s %s" % (sbj, " ".join("%s=%s" % (k, "H" if res[sbj][k] else "F") for k in keys)))
    for a_, b_ in (("mark_label", "H"), ("mark_label", "hand"), ("mark_label", "mark_filter_vacuous"),
                   ("mark_label", "dflt0"), ("neither", "hand")):
        d = sorted([x for x in SUBJ_T2 if res[x][a_] != res[x][b_]], key=lambda x: (len(x), x))
        print("       %-20s vs %-20s differ %4d of %d  e.g. %s" % (a_, b_, len(d), len(SUBJ_T2), d[:4]))
# the record (a product) with a marked label: (h: <10, m?: <30) vs (h: <10) & (m?: <30) on (OP)'s population, the
# mark read by SOME; base F; and the EVERY reading for comparison (every text of m's group must satisfy)
eq_some = eq_every = 0
for x in SUBJ_OP:
    its = split_op(x)
    rec = (all(tuple_ok(lambda t: Sh(t[0]) and Tm(t[1]), [h, m if m is not None else EMPTY], [None, M2])
               for h, m in its)) if its else False                      # base F: the empty list fails (unmarked h)
    amp = (all(Sh(h) for h, _ in its) and all(Tm(m) if m is not None else any(Tm(z) for z in M2) for _, m in its)) \
        if its else False
    every = all(Sh(h) and (Tm(m) if m is not None else all(Tm(z) for z in M2)) for h, m in its) if its else False
    eq_some += rec != amp
    eq_every += rec != every
print("     (OP) (h: <10, m?: <30) vs (h: <10) & (m?: <30), base F: differ %d of %d; the EVERY reading of m? vs SOME: "
      "differ %d (e.g. '3,': SOME %s, EVERY %s)" % (eq_some, len(SUBJ_OP), eq_every,
                                                   hf(tuple_ok(lambda t: Sh(t[0]) and Tm(t[1]), ["3", EMPTY], [None, M2])),
                                                   hf(all(Tm(z) for z in M2))))

print("\nCONTROL comparisons %d differ %d" % (T["control"], T["control_differ"]))
print("TOTAL engine cases %d differ %d engine-disagreements %d" % (T["cases"], T["differ"], DISAGREE[0]))
