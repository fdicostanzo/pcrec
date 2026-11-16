# absimpact: evidence for docs/dev/lanes/absimpact_report.md (the impact of the CANDIDATE absent-label rule R on every
# kind of statement of the predicate draft). R is NOT ruled; this script computes "today" (T, the ruled line read per
# pass, lane absent's T-pass) and "under R" side by side, and counts the answers that move.
# Run (worktree root): `timeout 120 python3 -I docs/dev/lanes/absimpact_check.py`.
# Sabotage: `ABSIMPACT_SABOTAGE=1 ...` (R's zero-pass entry is flipped to today's; the engine-run unfolds must differ).
#
# KINDS OF RESULT.
# - RUN: every subject is checked to be a whole match of its operand pattern by libpcre2-8 AND Python `re`; the parse
#   facts the rows rest on (a loop reached and run zero times, an alternative not taken, the hits of `occurrences`)
#   are read from PCRE2 (probe groups; the hits from an unrolled form of the `occurrences` body, compared with
#   find-all).
# - COMPUTED: each answer from ONE declared table per rule (PART below: absence kind x rule x mark/default -> what the
#   absent part contributes), evaluated on the subject split by plain string code.
# - ENGINE-RUN: for (LI), (OC), (OP), (RZ), (AL) the R answers are also built as a regex from R stated over sets (not
#   from the answers) and run against the computed answer with both engines.
# - REUSED: lane absent's (SP) rows are exec'd from absent_check.py (its list text only, not its module).
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
L.pcre2_config_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
ANCH, ENDANCH = 0x80000000, 0x20000000
UNSET = ctypes.c_size_t(-1).value
_vb = ctypes.create_string_buffer(64)
L.pcre2_config_8(11, _vb)
print("libpcre2-8", _vb.value.decode(), "| Python", sys.version.split()[0])
SAB = os.environ.get("ABSIMPACT_SABOTAGE") == "1"
if SAB:
    print("SABOTAGE ON")
_cache, DIS = {}, [0]
TOT = {"cases": 0, "differ": 0, "probes": 0}


def _code(p):
    if p not in _cache:
        e, o = ctypes.c_int(), ctypes.c_size_t()
        c = L.pcre2_compile_8(p.encode(), len(p.encode()), 0, ctypes.byref(e), ctypes.byref(o), None)
        assert c, (p[:80], e.value)
        _cache[p] = c
    return _cache[p]


def py(p):
    return p.replace("(?<", "(?P<").replace("(?P<=", "(?<=").replace("(?P<!", "(?<!")


def groups(p, t, names):
    """whole-match t against p in PCRE2; return None (no match) or {name: text or None}; Python `re` must agree"""
    c = _code(p)
    md = L.pcre2_match_data_create_from_pattern_8(c, None)
    rc = L.pcre2_match_8(c, t.encode(), len(t.encode()), 0, ANCH | ENDANCH, md, None)
    out = None
    if rc >= 0:
        ov = L.pcre2_get_ovector_pointer_8(md)
        out = {}
        for nm in names:
            n = L.pcre2_substring_number_from_name_8(c, nm.encode())
            out[nm] = None if ov[2 * n] == UNSET else t.encode()[ov[2 * n]:ov[2 * n + 1]].decode()
    L.pcre2_match_data_free_8(md)
    m = re.fullmatch(py(p), t)
    pyo = None if m is None else {nm: m.group(nm) for nm in names}
    if pyo != out:
        DIS[0] += 1
        print("  ENGINE DISAGREEMENT", repr(p[:60]), repr(t), out, pyo)
    TOT["probes"] += 1
    return out


def whole(p, t):
    return groups(p, t, []) is not None


def check(tag, rx, subj, want):
    TOT["cases"] += 1
    got = whole(rx, subj)
    if got != want:
        TOT["differ"] += 1
        if TOT["differ"] < 12:
            print("  DIFFER", tag, repr(subj), "engine", got, "computed", want)


def alt(strings):
    strings = sorted(set(strings), key=lambda s: (-len(s), s))
    return "(?:" + "|".join(re.escape(s) for s in strings) + ")" if strings else "(?!)"


hf = lambda b: "HOLDS" if b else "FAILS"
canon = lambda x: re.fullmatch(r"0|[1-9][0-9]*", x) is not None
D = [str(i) for i in range(10)]

# =================================================================================================================
# THE RULES AS ONE DECLARED TABLE (the report's table (RT)). An absent part has a KIND:
#   Z  a loop reached and run zero times (the label has no pass)      U  never reached (an optional skipped, an
#   P  missing in ONE pass of the pairing loop (the pass has no text)     alternative not taken, a loop skipped)
# It contributes: ("val", v) the default's text; PROJ (the part ranges over its group's strings: "some value would
# put the tuple in R"); FAIL. T = today's ruled line read per pass (J6, J7, §4.2, §4B.1); R = the candidate.
PROJ, FAIL = "PROJ", "FAIL"


def part(rule, kind, mark=False, default=None):
    dv = ("val", default) if default is not None else None
    if rule == "T":
        if kind == "Z":
            return PROJ                     # zero passes: nothing to test for the looped part; default NOT read
        return dv or FAIL                   # unset (U) or missing in a pass (P): fails unless a default (J6)
    if rule == "R":
        if kind == "Z" and SAB:
            return PROJ                     # SABOTAGE: today's zero-pass entry
        if dv and mark:
            raise ValueError("mark and default on one label: a SUB-CHOICE, not answered by R")
        if dv:
            return dv                       # the default: read on EVERY kind of absence, the empty list included
        if mark:
            return PROJ                     # the optional mark: some value would do
        return FAIL                         # a condition needs a text
    raise KeyError(rule)


def tup(Rf, parts, doms):
    """one tuple: parts are a text, FAIL, PROJ or ("val", v); PROJ ranges over doms[i]"""
    if any(p == FAIL for p in parts):
        return False
    parts = [p[1] if isinstance(p, tuple) else p for p in parts]
    idx = [i for i, p in enumerate(parts) if p == PROJ]
    for combo in itertools.product(*[doms[i] for i in idx]):
        t = list(parts)
        for i, v in zip(idx, combo):
            t[i] = v
        if Rf(tuple(t)):
            return True
    return False


def plain(rule, passes, S, dom, zkind="Z", mark=False, default=None, all_zero=None):
    """a one-label condition over the passes of the label's loop (a set-once label: one pass or none).
    passes: list of texts (None = missing in that pass). zkind: the kind when there is no pass.
    all_zero: for `all(...)` under R, sub-choice A2 ('every, possibly none') = True"""
    if not passes:
        if all_zero:
            return True
        return tup(lambda t: S(t[0]), [part(rule, zkind, mark, default)], [dom])
    return all(tup(lambda t: S(t[0]), [v if v is not None else part(rule, "P", mark, default)], [dom])
               for v in passes)


def per_pass(rule, v, S, dom, mark=False, default=None, ignore_absent=False):
    """one pass's value for a group question (some/count): the condition on that pass alone"""
    if v is None and ignore_absent:
        return False
    return tup(lambda t: S(t[0]), [v if v is not None else part(rule, "P", mark, default)], [dom])


MOVES = {}


def tally(tab, name, subjects, a, b, show=lambda s: repr(s), la="today", lb="R"):
    diff = [s for s in subjects if a[s] != b[s]]
    MOVES[(tab, name)] = (len(diff), len(subjects))
    ex = min(diff, key=lambda s: (len(str(s)), str(s))) if diff else None
    print("   %-58s moves %5d of %6d%s" % (name, len(diff), len(subjects),
                                          "" if ex is None else "   smallest: %s (%s %s, %s %s)" %
                                          (show(ex), la, hf(a[ex]), lb, hf(b[ex]))))
    return len(diff)


# =================================================================================================================
print("\n(RT) the rule as tested: what an absent part contributes (kind x rule x mark/default)")
for kind in ("Z", "U", "P"):
    row = []
    for rule in ("T", "R"):
        for mk, dv in ((False, None), (True, None), (False, "v")):
            if rule == "T" and mk:
                row.append("-")
                continue
            r = part(rule, kind, mk, dv)
            row.append("default" if isinstance(r, tuple) else r)
    print("   %s  T: plain %-5s default %-8s | R: plain %-5s mark %-5s default %s" %
          (kind, row[0], row[2], row[3], row[4], row[5]))

# =================================================================================================================
# (SP) lane absent's spelling rows, `(n: <5)` with n absent (exec'd list; kinds re-probed here)
print("\n(SP) lane absent's 27 spelling rows, `(n: <5)` on a subject where n has no value")
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "absent_check.py")).read()
a0 = src.index("SP = [")
ns = {}
exec(src[a0:src.index("\n]\n", a0) + 3], ns)
SP = ns["SP"]
S5 = lambda x: canon(x) and int(x) < 5
sp_t, sp_r, sp_m, keys, SP_KIND = {}, {}, {}, [], {}
for g, pat, probe, pg, subj, k_set, k_unset, scope in SP:
    assert whole(pat, subj)
    if probe is None:
        prev = [r for r in SP if r[1] == pat and r[2] is not None and subj.endswith(r[4]) and r[4] != subj][0]
        st = groups(prev[2], prev[4], [prev[3]])[prev[3]] is not None
    else:
        st = groups(probe, subj, [pg])[pg] is not None
    kind = k_set if st else k_unset
    k = "Z" if kind == "Z" else ("P" if scope != "match" else "U")
    key = (pat, subj)
    keys.append(key)
    SP_KIND[key] = kind
    # rows whose subject has n in another pass (`a3,`) carry n = 3 there (< 5): the answer is the absent pass's
    sp_t[key] = tup(lambda t: S5(t[0]), [part("T", k)], [D])
    sp_r[key] = tup(lambda t: S5(t[0]), [part("R", k)], [D])
    sp_m[key] = tup(lambda t: S5(t[0]), [part("R", k, mark=True)], [D])
    print("   %-34s %-9r kind %-3s today %s  R %s  R with n? %s" % (pat, subj, kind, hf(sp_t[key]), hf(sp_r[key]),
                                                                   hf(sp_m[key])))
tally("SP", "plain (n: <5), today vs R", keys, sp_t, sp_r, show=lambda k: "/%s/ on %r" % k)
print("   groups of equal spellings that SPLIT: today %d, R %d, R with n? %d (of %d)" % tuple(
    [sum(len({d[(p, s)] for gg, p, *_r in SP if gg == g for s in [_r[2]]}) > 1 for g in {r[0] for r in SP})
     for d in (sp_t, sp_r, sp_m)] + [len({r[0] for r in SP})]))

# =================================================================================================================
# (LI) a list: /(?:(?<n>\d),)*/ ; 1,111 subjects (0-3 items). Every statement kind over a looped label.
print("\n(LI) list /(?:(?<n>\\d),)*/, 1,111 subjects (0 to 3 items); n has zero passes on the empty list")
P_LI = r"(?:(?<n>\d),)*"
SUBJ_LI = ["".join(d + "," for d in c) for k in range(4) for c in itertools.product(D, repeat=k)]
LI = {}
for s in SUBJ_LI:
    g = groups(P_LI, s, ["n"])
    assert g is not None and (g["n"] is None) == (s == "")      # RUN: zero passes = n unset in PCRE2's state
    LI[s] = s.split(",")[:-1]
GE5 = lambda x: canon(x) and int(x) >= 5
ANY = lambda x: True
kinds_li = {
    "plain (n: <5)": lambda r, s: plain(r, LI[s], S5, D),
    "all((n: <5)), A1 (as plain)": lambda r, s: plain(r, LI[s], S5, D),
    "some((n: <5))": lambda r, s: any(per_pass(r, v, S5, D) for v in LI[s]),
    "c := count((n: <5)), (c: ==0)": lambda r, s: sum(per_pass(r, v, S5, D) for v in LI[s]) == 0,
    "occurs.exactly(1, (n: <5))": lambda r, s: sum(per_pass(r, v, S5, D) for v in LI[s]) == 1,
    "occurs.at_most(1, (n: <5))": lambda r, s: sum(per_pass(r, v, S5, D) for v in LI[s]) <= 1,
    "occurs.none((n: >=5))": lambda r, s: sum(per_pass(r, v, GE5, D) for v in LI[s]) == 0,
    "!(n: <5)": lambda r, s: not plain(r, LI[s], S5, D),
    "(n: !<5)": lambda r, s: plain(r, LI[s], lambda x: not S5(x), D),
    "guard !(n: /[\\s\\S]*/)": lambda r, s: not plain(r, LI[s], ANY, D),
    "(n = 0: <5)": lambda r, s: plain(r, LI[s], S5, D, default="0"),
    "(n = 9: <5)": lambda r, s: plain(r, LI[s], S5, D, default="9"),
}
LIA = {}
for name, f in kinds_li.items():
    a = {s: f("T", s) for s in SUBJ_LI}
    b = {s: f("R", s) for s in SUBJ_LI}
    LIA[name] = (a, b)
    tally("LI", name, SUBJ_LI, a, b)
mk = {s: plain("R", LI[s], S5, D, mark=True) for s in SUBJ_LI}
tally("LI", "(n?: <5) under R vs plain today (the mark restores it?)", SUBJ_LI, LIA["plain (n: <5)"][0], mk)
a2 = {s: plain("R", LI[s], S5, D, all_zero=True) for s in SUBJ_LI}
tally("LI", "all((n: <5)), A2 ('possibly none') vs plain today", SUBJ_LI, LIA["plain (n: <5)"][0], a2)
d0 = {s: plain("R", LI[s], S5, D, default="0") for s in SUBJ_LI}
tally("LI", "(n = 0: <5) under R vs plain today (a default in S as the fix)", SUBJ_LI,
      LIA["plain (n: <5)"][0], d0)
nsome = {s: not any(per_pass("R", v, lambda x: not S5(x), D) for v in LI[s]) for s in SUBJ_LI}
tally("LI", "!some((n: !<5)) under R vs plain today (rev 8's vacuous spelling)", SUBJ_LI,
      LIA["plain (n: <5)"][0], nsome)
# L30: !(x: S) vs (x: !S)
for rule in ("T", "R"):
    a = {s: not plain(rule, LI[s], S5, D) for s in SUBJ_LI}
    b = {s: plain(rule, LI[s], lambda x: not S5(x), D) for s in SUBJ_LI}
    tally("LI", "L30 %s: !(n: <5) vs (n: !<5)" % ("today" if rule == "T" else "R"), SUBJ_LI, a, b,
          la="!(n: <5)", lb="(n: !<5)")
# sub-choice (b): `!` of a condition on a MARKED absent label. B1: the plain complement of the marked condition
# (absent -> the marked condition holds -> `!` FALSE); B2: the mark kept outside the `!` (absent acceptable -> TRUE)
b1 = {s: not plain("R", LI[s], S5, D, mark=True) for s in SUBJ_LI}
b2 = {s: (not LI[s]) or not plain("R", LI[s], S5, D, mark=True) for s in SUBJ_LI}
tally("LI", "sub-choice B: !(n?: <5), B1 vs B2", SUBJ_LI, b1, b2, la="B1", lb="B2")
tally("LI", "B1 !(n?: <5) under R vs !(n: <5) today", SUBJ_LI, LIA["!(n: <5)"][0], b1)
# (DU) default.unused on a looped label that is never unset, only zero-pass: is the default answer-identical?
for rule in ("T", "R"):
    for v in ("0", "9"):
        x = {s: plain(rule, LI[s], S5, D) for s in SUBJ_LI}
        y = {s: plain(rule, LI[s], S5, D, default=v) for s in SUBJ_LI}
        n = sum(x[s] != y[s] for s in SUBJ_LI)
        MOVES[("DU", rule + v)] = (n, len(SUBJ_LI))
        print("   (DU) %s: (n = %s: <5) vs (n: <5): %d of %d differ -> %s" %
              ("today" if rule == "T" else "R    ", v, n, len(SUBJ_LI), "used" if n else "UNUSED (warns)"))
# ENGINE-RUN: R's plain = (?:[0-4],)+ ; today's = (?:[0-4],)* ; R's mark = today's; R's default 9 = (?:[0-4],)+
LT = "(?:[0-4],)"
for s in SUBJ_LI:
    check("LI R plain", LT + "+", s, LIA["plain (n: <5)"][1][s])
    check("LI T plain", LT + "*", s, LIA["plain (n: <5)"][0][s])
    check("LI R mark", LT + "*", s, mk[s])
    check("LI R n=0", LT + "*", s, d0[s])
    check("LI R n=9", LT + "+", s, LIA["(n = 9: <5)"][1][s])
    check("LI R !plain", "(?!" + LT + "+" + "$)(?:\\d,)*", s, LIA["!(n: <5)"][1][s])

# =================================================================================================================
# (OC) occurrences: r := /ab(?<g>[xy])/ over every span on {a,b,x,y} of length 0-6 (5,461). Hits RUN from PCRE2.
print("\n(OC) occurrences(r), r := /ab(?<g>[xy])/, 5,461 spans over {a,b,x,y} of length 0 to 6")
UNR = "(?:(?s:.*?)(?<h1>ab(?<g1>[xy]))(?:(?s:.*?)(?<h2>ab(?<g2>[xy]))(?:(?s:.*?)(?<h3>ab(?<g3>[xy])))?)?)?(?s:.*)"
SUBJ_OC = ["".join(c) for k in range(7) for c in itertools.product("abxy", repeat=k)]
OC = {}
for s in SUBJ_OC:
    g = groups(UNR, s, ["g1", "g2", "g3"])
    hits = [g[k] for k in ("g1", "g2", "g3") if g[k] is not None]
    fa = [m.group(1) for m in re.finditer(r"ab([xy])", s)]
    if hits != fa:
        DIS[0] += 1
        print("  HIT DISAGREEMENT", s, hits, fa)
    OC[s] = hits
X = lambda v: v == "x"
Y = lambda v: v == "y"
G = ["x", "y"]
kinds_oc = {
    "L52a (m: occurrences(r) & (g: \"x\"))": lambda r, s: plain(r, OC[s], X, G),
    "L52b (m: occurrences(r) & some((g: \"x\")))": lambda r, s: any(per_pass(r, v, X, G) for v in OC[s]),
    "L55b (m: occurrences(r, min = 1) & (g: \"x\"))": lambda r, s: bool(OC[s]) and plain(r, OC[s], X, G),
    "L58 contains(r) & (g: \"x\")": lambda r, s: bool(OC[s]) and plain(r, OC[s], X, G),
    "L61a contains(r & (g: \"x\"))": lambda r, s: "x" in OC[s],
    "occurs.none((g: \"y\"))": lambda r, s: not any(per_pass(r, v, Y, G) for v in OC[s]),
    "!(g: \"x\") over the hits": lambda r, s: not plain(r, OC[s], X, G),
    "(m: occurrences(r)) alone (L16)": lambda r, s: True,
}
OCA = {}
for name, f in kinds_oc.items():
    a = {s: f("T", s) for s in SUBJ_OC}
    b = {s: f("R", s) for s in SUBJ_OC}
    OCA[name] = (a, b)
    tally("OC", name, SUBJ_OC, a, b)
for rule in ("T", "R"):
    i = 0 if rule == "T" else 1
    for x, y, lab in (("L52a (m: occurrences(r) & (g: \"x\"))", "L52b (m: occurrences(r) & some((g: \"x\")))", "L52"),
                      ("L52a (m: occurrences(r) & (g: \"x\"))", "L55b (m: occurrences(r, min = 1) & (g: \"x\"))",
                       "L55"),
                      ("L61a contains(r & (g: \"x\"))", "L58 contains(r) & (g: \"x\")", "L61")):
        tally("OC", "%s %s: the two forms" % (lab, "today" if rule == "T" else "R"), SUBJ_OC,
              OCA[x][i], OCA[y][i], la="first", lb="second")
a2o = {s: plain("R", OC[s], X, G, all_zero=True) for s in SUBJ_OC}
tally("OC", "sub-choice A: all((g: \"x\")) A1 (= plain) vs A2 ('possibly none') under R", SUBJ_OC,
      OCA["L52a (m: occurrences(r) & (g: \"x\"))"][1], a2o, la="A1", lb="A2")
mko = {s: plain("R", OC[s], X, G, mark=True) for s in SUBJ_OC}
tally("OC", "(g?: \"x\") under R vs L52a today", SUBJ_OC, OCA["L52a (m: occurrences(r) & (g: \"x\"))"][0], mko)
for s in SUBJ_OC:  # ENGINE-RUN: R's L52a = has abx and no aby ; today's = no aby ; R's mark = no aby
    check("OC R L52a", "(?!(?s:.*)aby)" + "(?s:.*)abx" + "(?s:.*)", s,
          OCA["L52a (m: occurrences(r) & (g: \"x\"))"][1][s])
    check("OC T L52a", "(?!(?s:.*)aby)(?s:.*)", s, OCA["L52a (m: occurrences(r) & (g: \"x\"))"][0][s])
    check("OC R mark", "(?!(?s:.*)aby)(?s:.*)", s, mko[s])

# (OG) a hit that can lack its label: r2 := /ab(?<g>[xy])?/ (an optional INSIDE the hit; the iteration's own values)
print("\n(OG) occurrences(r2), r2 := /ab(?<g>[xy])?/: a hit may lack g (sub-choice: the mark inside some/count)")
UNR2 = ("(?:(?s:.*?)(?<h1>ab(?<g1>[xy])?)(?:(?s:.*?)(?<h2>ab(?<g2>[xy])?)(?:(?s:.*?)(?<h3>ab(?<g3>[xy])?))?)?)?"
        "(?s:.*)")
OG = {}
for s in SUBJ_OC:
    g = groups(UNR2, s, ["h1", "h2", "h3", "g1", "g2", "g3"])
    hits = [g["g%d" % i] for i in (1, 2, 3) if g["h%d" % i] is not None]
    fa = [m.group(1) for m in re.finditer(r"ab([xy])?", s)]
    if hits != fa:
        DIS[0] += 1
        print("  HIT DISAGREEMENT", s, hits, fa)
    OG[s] = hits
e1 = {s: any(per_pass("R", v, X, G, mark=True) for v in OG[s]) for s in SUBJ_OC}
e2 = {s: any(per_pass("R", v, X, G, ignore_absent=True) for v in OG[s]) for s in SUBJ_OC}
tally("OG", "some((g?: \"x\")): E1 (a hit without g counts) vs E2 (it does not)", SUBJ_OC, e2, e1, la="E2", lb="E1")
c1 = {s: sum(per_pass("R", v, X, G, mark=True) for v in OG[s]) == 1 for s in SUBJ_OC}
c2 = {s: sum(per_pass("R", v, X, G, ignore_absent=True) for v in OG[s]) == 1 for s in SUBJ_OC}
tally("OG", "occurs.exactly(1, (g?: \"x\")): E1 vs E2", SUBJ_OC, c2, c1, la="E2", lb="E1")
pa = {s: plain("T", OG[s], X, G) for s in SUBJ_OC}
pb = {s: plain("R", OG[s], X, G) for s in SUBJ_OC}
tally("OG", "(g: \"x\") over hits that may lack g", SUBJ_OC, pa, pb)

# =================================================================================================================
# (OP) records: /(?:(?<h>\d+)(?::(?<m>\d\d))?,)*/ & (h: <10, m: <30) (lane absent's population, 259)
print("\n(OP) record (h: <10, m: <30), m optional in each item, 259 lists (0-3 items)")
P_OP = r"(?:(?<h>\d+)(?::(?<m>\d\d))?,)*"
OP_ITEMS = [(h, m) for h in ("3", "12") for m in (None, "15", "45")]
SUBJ_OP = ["".join("%s%s," % (h, "" if m is None else ":" + m) for h, m in its)
           for n in range(4) for its in itertools.product(OP_ITEMS, repeat=n)]
for s in SUBJ_OP:
    assert whole(P_OP, s)
H12 = [str(i) for i in range(10)] + ["%02d" % i for i in range(100)]
M2 = ["%02d" % i for i in range(100)]
H100 = [str(i) for i in range(100)] + ["0" + str(i) for i in range(10)]   # \d+ sampled (enough for <10)
Sh = lambda x: canon(x) and int(x) < 10
Tm = lambda x: canon(x) and int(x) < 30
spl = lambda s: [(it.split(":")[0], it.split(":")[1] if ":" in it else None) for it in s.split(",")[:-1]]


def op_rec(rule, s, hm=False, mm=False, md=None, neg=False):
    its = spl(s)
    Rf = lambda t: Sh(t[0]) and Tm(t[1])
    if not its:
        r = tup(Rf, [part(rule, "Z", hm), part(rule, "Z", mm, md)], [H100, M2])
    else:
        r = all(tup(Rf, [h, m if m is not None else part(rule, "P", mm, md)], [None, M2]) for h, m in its)
    return (not r) if neg else r


def op_amp(rule, s):
    its = spl(s)
    hs = plain(rule, [h for h, _ in its], Sh, H100)
    ms = plain(rule, [m for _, m in its], Tm, M2)
    return hs and ms


OPA = {}
for name, kw in (("record (h: <10, m: <30)", {}), ("record with m? (h: <10, m?: <30)", {"mm": True}),
                 ("record with h?, m?", {"hm": True, "mm": True}), ("record with m = 0", {"md": "0"}),
                 ("!(h: <10, m: <30)", {"neg": True})):
    a = {s: op_rec("T", s, **({k: v for k, v in kw.items() if k in ("md", "neg")})) for s in SUBJ_OP}
    b = {s: op_rec("R", s, **kw) for s in SUBJ_OP}
    OPA[name] = (a, b)
    tally("OP", name + " (R) vs the unmarked form today", SUBJ_OP, a, b)
eq = sum(op_rec("R", s) != op_amp("R", s) for s in SUBJ_OP)
print("   record vs `&` of its entries under R: %d of %d differ (L3, J9)" % (eq, len(SUBJ_OP)))
MOVES[("OP", "EQ R")] = (eq, len(SUBJ_OP))
for s in SUBJ_OP:   # ENGINE-RUN
    check("OP R rec", "(?:3:15,)" + "+", s, OPA["record (h: <10, m: <30)"][1][s])
    check("OP T rec", "(?:3:15,)*", s, OPA["record (h: <10, m: <30)"][0][s])
    check("OP R m?", "(?:3(?::15)?,)" + "+", s, OPA["record with m? (h: <10, m?: <30)"][1][s])
    check("OP R h?m?", "(?:3(?::15)?,)*", s, OPA["record with h?, m?"][1][s])

# =================================================================================================================
# (RZ) zero-pass-record: /(?<k>\d)(?:;(?<h>\d))*/ & (h: <5, k: 3..7), 1,110 subjects
print("\n(RZ) /(?<k>\\d)(?:;(?<h>\\d))*/, 1,110 subjects: the zero-pass record, when(), the array of conditions")
P_RZ = r"(?<k>\d)(?:;(?<h>\d))*"
SUBJ_RZ = [k + "".join(";" + h for h in hs) for k in D for n in range(3) for hs in itertools.product(D, repeat=n)]
for s in SUBJ_RZ:
    g = groups(P_RZ, s, ["h"])
    assert (g["h"] is None) == (";" not in s)
T37 = lambda x: canon(x) and 3 <= int(x) <= 7


def rz(rule, s, hm=False, hd=None, Rf=lambda t: S5(t[0]) and T37(t[1])):
    k, *hs = s.split(";")
    if not hs:
        return tup(Rf, [part(rule, "Z", hm, hd), k], [D, None])
    return all(Rf((h, k)) for h in hs)


RZA = {}
for name, kw in (("(h: <5, k: 3..7)", {}), ("(h?: <5, k: 3..7)", {"hm": True}), ("(h = 9: <5, k: 3..7)", {"hd": "9"}),
                 ("(h = 0: <5, k: 3..7)", {"hd": "0"})):
    a = {s: rz("T", s, hd=kw.get("hd")) for s in SUBJ_RZ}
    b = {s: rz("R", s, **kw) for s in SUBJ_RZ}
    RZA[name] = (a, b)
    tally("RZ", name + " (R) vs the same today", SUBJ_RZ, a, b, show=lambda x: repr(x))
tally("RZ", "(h?: <5, k: 3..7) under R vs (h: <5, k: 3..7) today", SUBJ_RZ, RZA["(h: <5, k: 3..7)"][0],
      RZA["(h?: <5, k: 3..7)"][1])
for rule in ("T", "R"):
    hpl = {s: plain(rule, s.split(";")[1:], S5, D) for s in SUBJ_RZ}
    kpl = {s: T37(s.split(";")[0]) for s in SUBJ_RZ}
    rec = {s: rz(rule, s) for s in SUBJ_RZ}
    amp = {s: hpl[s] and kpl[s] for s in SUBJ_RZ}
    arr = {s: hpl[s] or kpl[s] for s in SUBJ_RZ}
    whn = {s: (hpl[s] and s.split(";")[0] == "3") or not hpl[s] for s in SUBJ_RZ}
    RZA["amp " + rule], RZA["arr " + rule], RZA["when " + rule] = amp, arr, whn
    MOVES[("RZ", "EQ " + rule)] = (sum(rec[s] != amp[s] for s in SUBJ_RZ), len(SUBJ_RZ))
    print("   record vs `&` (%s): %d of %d differ" % (rule, MOVES[("RZ", "EQ " + rule)][0], len(SUBJ_RZ)))
tally("RZ", "L23 array [(h: <5), (k: 3..7)] (R vs today)", SUBJ_RZ, RZA["arr T"], RZA["arr R"])
tally("RZ", "P & when((h: <5), (k: 3)) (R vs today)", SUBJ_RZ, RZA["when T"], RZA["when R"])
Trx, Srx = alt([x for x in D if T37(x)]), alt([x for x in D if S5(x)])
for s in SUBJ_RZ:   # ENGINE-RUN
    check("RZ R rec", Trx + "(?:;" + Srx + ")" + "+", s, RZA["(h: <5, k: 3..7)"][1][s])
    check("RZ R h?", Trx + "(?:;" + Srx + ")*", s, RZA["(h?: <5, k: 3..7)"][1][s])
    # R: when = (h has passes, all < 5, and k = 3) or not (that): zero passes, or some h >= 5
    check("RZ R when", "3(?:;[0-4])+|\\d(?:;\\d)*;[5-9](?:;\\d)*|" + "\\d", s, RZA["when R"][s])

# (ZE) zero-pass-empty, the corner for a MARKED label: /(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*/ & (h?: <$a, k: 3)
print("\n(ZE) /(?<a>\\d)-(?<k>\\d)(?:;(?<h>\\d))*/ & (h?: <$a, k: 3): the set for h is EMPTY when a = 0")
SUBJ_ZE = ["%d-%d" % (a, k) + "".join(";%d" % h for h in hs) for a in range(10) for k in range(10) for n in range(3)
           for hs in itertools.product(range(10), repeat=n)]
f1, f2, un = {}, {}, {}
for s in SUBJ_ZE:
    ak, *hs = s.split(";")
    a, k = ak.split("-")
    lt = lambda x: canon(x) and int(x) < int(a)
    zero = not hs
    f1[s] = (k == "3") and (tup(lambda t: lt(t[0]), [PROJ], [D]) if zero else all(lt(h) for h in hs))
    f2[s] = (k == "3") and (True if zero else all(lt(h) for h in hs))
    un[s] = (k == "3") and (False if zero else all(lt(h) for h in hs))
tally("ZE", "F1 (projection: some h would do) vs F2 (absent acceptable outright)", SUBJ_ZE, f1, f2, la="F1",
      lb="F2")
tally("ZE", "unmarked (h: <$a, k: 3) under R vs F2", SUBJ_ZE, un, f2, la="unmarked", lb="F2")

# =================================================================================================================
# (AL) the labelled alternation [x = /\d/, y = /[a-z]/] & (x: /[0-5]/)  (§4.2, "the alternative lacking x drops")
print("\n(AL) [x = /\\d/, y = /[a-z]/] & (x: /[0-5]/), 36 one-character subjects")
P_AL = r"(?<x>\d)|(?<y>[a-z])"
SUBJ_AL = D + [chr(c) for c in range(97, 123)]
AL = {s: groups(P_AL, s, ["x"])["x"] for s in SUBJ_AL}
F5 = lambda v: v in "012345"
DX = D
a = {s: plain("T", [AL[s]] if AL[s] else [], F5, DX, zkind="U") for s in SUBJ_AL}
b = {s: plain("R", [AL[s]] if AL[s] else [], F5, DX, zkind="U") for s in SUBJ_AL}
c = {s: plain("R", [AL[s]] if AL[s] else [], F5, DX, zkind="U", mark=True) for s in SUBJ_AL}
tally("AL", "(x: /[0-5]/) (R vs today)", SUBJ_AL, a, b)
tally("AL", "(x?: /[0-5]/) under R vs (x: /[0-5]/) today", SUBJ_AL, a, c)
for s in SUBJ_AL:
    check("AL R", "[0-5]", s, b[s])
    check("AL R x?", "[0-5]|[a-z]", s, c[s])

# =================================================================================================================
# (T2) set-once joint: t2 := /(?<h>\d{1,2})(?::(?<m>\d\d))?/ & ((h, m): >= (9, 30)) (DOM reading), 11,110 subjects
print("\n(T2) t2 & ((h, m): >= (9, 30)), minutes optional (set once), 11,110 subjects")
P_T2 = r"(?<h>\d{1,2})(?::(?<m>\d\d))?"
SUBJ_T2 = [h for h in H12] + [h + ":" + m for h in H12 for m in M2]
for s in SUBJ_T2[:110] + SUBJ_T2[-50:]:
    g = groups(P_T2, s, ["m"])
    assert g is not None and ((g["m"] is None) == (":" not in s))
RT2 = lambda t: canon(t[0]) and canon(t[1]) and (int(t[0]), int(t[1])) >= (9, 30)


def t2(rule, s, mm=False, md=None, hm=False):
    h, m = (s.split(":") + [None])[:2]
    return tup(RT2, [h, m if m is not None else part(rule, "U", mm, md)], [None, M2])


a = {s: t2("T", s) for s in SUBJ_T2}
b = {s: t2("R", s) for s in SUBJ_T2}
c = {s: t2("R", s, mm=True) for s in SUBJ_T2}
d = {s: t2("R", s, md="0") for s in SUBJ_T2}
e = {s: t2("T", s, md="0") for s in SUBJ_T2}
tally("T2", "((h, m): >= (9, 30)) (R vs today)", SUBJ_T2, a, b)
tally("T2", "((h, m = 0): ...) (R vs today)", SUBJ_T2, e, d)
tally("T2", "((h, m?): ...) under R vs ((h, m): ...) today", SUBJ_T2, a, c)
# sub-choice (c): a mark on a label that is never absent (h is required): answer-identical?
hmk = {s: t2("R", s) for s in SUBJ_T2}
tally("T2", "((h?, m): ...) vs ((h, m): ...) under R (h never absent)", SUBJ_T2, b, hmk, la="h", lb="h?")
# sub-choice (d): `m? = 0`: D2 the default wins (= m = 0), D3 the mark wins (= m?)
tally("T2", "(h, m? = 0): D2 (default read) vs D3 (mark read)", SUBJ_T2, d, c, la="D2", lb="D3")


# =================================================================================================================
# (RK) RULINGS R1 (14:15): R-KINDS beside R-INTENT. The manager's reading of the owner's words: two absence kinds,
# each with its own control. REACHED-EMPTY (RE: a quantifier reached and run zero times, `x*` and, by his 13:29
# remark, `x?` skipped) is accepted only by the mark `h?`; NEVER-REACHED (NR: an alternative not taken) is handled only
# by the default `h = v`; `h? = v` reads v on either kind; nothing written: FAIL. A loop never reached because an
# optional AROUND it was skipped (EO) has two readings: K1 by the optional (RE), K2 by the label's own loop (NR).
print("\n(RK) R-kinds beside R-intent (rulings R1): what each control does per absence kind")


def part_kinds(cls, mark=False, default=None):
    if mark and default is not None:
        return ("val", default)
    if cls == "RE":
        return PROJ if mark else FAIL
    if cls == "NR":
        return ("val", default) if default is not None else FAIL
    raise KeyError(cls)


def kclass(kind, reading):
    if kind in ("Z", "O"):
        return "RE"
    if kind in ("A", "EA"):
        return "NR"
    if kind == "EO":
        return "RE" if reading == "K1" else "NR"
    raise KeyError(kind)


CTRL = [("nothing", False, None), ("n?", True, None), ("n = 3", False, "3"), ("n? = 3", True, "3")]
for cls in ("RE", "NR"):
    print("   %-3s %s" % (cls, "  ".join("%s -> %s" % (nm, (lambda r: "v read" if isinstance(r, tuple) else r)(
        part_kinds(cls, mk, dv))) for nm, mk, dv in CTRL)))
SPK = {}
for g, pat, probe, pg, subj, k_set, k_unset, scope in SP:
    key = (pat, subj)
    kind = [r for r in SP if (r[1], r[4]) == key][0]
    # re-read the probed kind from the (SP) pass above (sp_kind)
    kind = SP_KIND[key]
    row = {}
    for reading in ("K1", "K2"):
        for nm, mk, dv in CTRL:
            row[(reading, nm)] = tup(lambda t: S5(t[0]), [part_kinds(kclass(kind, reading), mk, dv)], [D])
    for nm, mk, dv in CTRL:
        row[("intent", nm)] = tup(lambda t: S5(t[0]), [part("R", "P", mk, dv) if not (mk and dv) else ("val", dv)],
                                  [D])
    SPK[key] = row
    acc = lambda rd: ",".join(nm for nm, _m, _d in CTRL[1:] if row[(rd, nm)]) or "-"
    print("   %-34s %-9r %-3s accepted by: R-kinds K1 [%s]  K2 [%s]  R-intent [%s]" %
          (pat, subj, kind, acc("K1"), acc("K2"), acc("intent")))
for rd in ("K1", "K2", "intent"):
    for nm, _m, _d in CTRL:
        split = sum(len({SPK[(p, _r[2])][(rd, nm)] for gg, p, *_r in SP if gg == g}) > 1 for g in {r[0] for r in SP})
        MOVES[("RK", rd + " " + nm)] = (split, len({r[0] for r in SP}))
        print("   split groups, %-6s with %-7s written: %d of %d" % (rd, nm, split, len({r[0] for r in SP})))

# the time example: optional minutes (`?`, RE) vs the alternation spelling `(?::(?<m>\d\d)| o'clock)` (NR)
print("   time example ((h, m ...): >= (9, 30)) on `9`, `10` (minutes absent), two spellings of the optional part")
for lab, cls in (("t2 optional `(?::(?<m>\\d\\d))?`", "RE"), ("o'clock alternation", "NR")):
    for nm, mk, dv in (("nothing", False, None), ("m?", True, None), ("m = 0", False, "0"), ("m? = 0", True, "0")):
        rk = [tup(RT2, [h, part_kinds(cls, mk, dv)], [None, M2]) for h in ("9", "10")]
        ri = [tup(RT2, [h, ("val", dv) if dv is not None else (PROJ if mk else FAIL)], [None, M2]) for h in ("9", "10")]
        print("     %-34s %-8s R-kinds 9:%s 10:%s | R-intent 9:%s 10:%s" % (lab, nm, hf(rk[0]), hf(rk[1]),
                                                                          hf(ri[0]), hf(ri[1])))

# a labelled alternation with a list-valued entry: x records whose list may be empty, never y records
print("   [x = /(?:(?<n>\\d),)*/, y = /[a-z]+/] & (n?: <5): 'an x record whose list may be empty, not a y record'")
P_XY = r"(?<x>(?:(?<n>\d),)*)|(?<y>[a-z]+)"
SUBJ_XY = ["", "1,", "7,", "1,2,", "1,7,", "a", "bc"]
want = {"": True, "1,": True, "7,": False, "1,2,": True, "1,7,": False, "a": False, "bc": False}
for s in SUBJ_XY:
    g = groups(P_XY, s, ["x", "n", "y"])
    ns_ = s.split(",")[:-1] if g["x"] is not None else []
    cls = None if ns_ else ("RE" if g["x"] is not None else "NR")
    rk = all(S5(v) for v in ns_) if ns_ else tup(lambda t: S5(t[0]), [part_kinds(cls, True)], [D])
    ri = all(S5(v) for v in ns_) if ns_ else tup(lambda t: S5(t[0]), [part("R", "Z", True)], [D])
    ri2 = ri and g["x"] is not None          # R-intent: (n?: <5, x: /(?s).*/)  (x must have a text, possibly empty)
    MOVES[("RK", "xy " + s)] = (int(rk != want[s]) + int(ri2 != want[s]), 2)
    print("     %-6r x=%-6r y=%-4r intended %s | R-kinds (n?: <5) %s | R-intent (n?: <5) %s, (n?: <5, x: /(?s).*/) %s"
          % (s, g["x"], g["y"], hf(want[s]), hf(rk), hf(ri), hf(ri2)))

# =================================================================================================================
print("\nSUMMARY")
print("engine cases: %d, differ: %d; probes/whole-matches: %d; engine disagreements: %d" %
      (TOT["cases"], TOT["differ"], TOT["probes"], DIS[0]))
