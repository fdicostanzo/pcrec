# predspec20: evidence for docs/design/predicates_draft.md rev 20 and docs/dev/lanes/predspec20_report.md
# (lane predspec20, 2026-11-16; design only).
#
# PART A (RE-RUN): every table rev 20 quotes comes from an earlier lane's evidence script. Each is run again here, by
#   absolute path, with `python3 -I`, and its stdout compared BYTE FOR BYTE with that lane's committed `.out`. A table
#   rev 20 quotes is "re-run" exactly when its script's line here says SAME.
# PART B (NEW): the worked examples of the manager's readings rev 20 states for the items the absent-label lock left
#   undefined (joint_condition.md §9 row 72; the predspec20 brief's (a)-(f)), and the lane's three proposals for the
#   UNDEFINED items (e1)-(e3), each over a small population:
#   (RA)  DOM(h) not computable exactly (a backreference): the under-/over-approximation procedure; it never answers
#         differently from the exact DOM, and where the two approximations disagree the program is refused.
#   (RB)  the CONTEXT reading: "some match of the pattern" vs "some match agreeing with this match's other labels",
#         on a branch-reset pattern (PCRE2 only: Python `re` has no `(?|`); both answers printed.
#   (RC)  a DEFAULTED label inside `all`: the default stands (`all` marks only the labels without a default).
#   (RD)  zero-pass-empty under F1 (one subject; the full table is absfix's (DOM-ZE), re-run in PART A).
#   (E1)  a computed label reading an absent label: absent itself (ruled point (1)); its controls are its own.
#   (E2)  `$a`, a bound `>$a` and a hole `${$a}` on an absent a: the condition FAILS (the general form's D = {});
#         where a default written for a would reach `$a`: NOT decided (both answers printed).
#   (E3)  the mark through a macro: no label parameter exists in rev 20's language; `all(c)` marks every label of a
#         passed condition; a per-label mark on a passed condition has no spelling (open).
#   (F)   the merged warning: "the label's candidate set is never consulted" (a mark or a default on a label that can
#         never be absent where the condition reads it).
# KINDS: RUN (each subject a whole match in PCRE2, and in Python `re` where it has the construct); COMPUTED (the
#   general form evaluated on the subject's own captures); ENGINE-RUN (the answer built as a regex from the set the
#   proposal states, never from the computed answer, and run in both engines against it).
# REUSE: absfold_check.py's prefix (which execs absimpact_check.py's engines: groups(), check(), alt(), canon, D;
#   absfold's cond(), Z/U/P, AR) is exec'd verbatim, as absfix_check.py does.
# Run from the scratch dir: `timeout 300 python3 -I /abs/path/docs/dev/lanes/predspec20_check.py`.
# Sabotage: `PREDSPEC20_SABOTAGE=1` makes (RA) answer from the over-approximation alone and (E1) treat an absent
#   computed label as satisfied; the (RA) silent-change count and the (E1) engine-run differ count must then be > 0.
import os, re, itertools, sys, subprocess, hashlib, ctypes

HERE = os.path.dirname(os.path.abspath(__file__))
PRIOR = ["jointexp", "tupleval", "tupleval2", "unsetdef", "jcfold", "jcfold2", "jcfix", "absent", "absimpact",
         "absfold", "absfix", "predspec19"]

print("PART A: the earlier lanes' scripts re-run, stdout vs the committed .out (byte for byte)")
_same = 0
for n in PRIOR:
    py_ = os.path.join(HERE, n + "_check.py")
    want = open(os.path.join(HERE, n + "_check.out"), "rb").read()
    env = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE")}
    r = subprocess.run([sys.executable, "-I", py_], capture_output=True, timeout=280, env=env)
    got = r.stdout + r.stderr
    ok = (r.returncode == 0 and got == want)
    _same += ok
    print("   %-11s rc %d  %s  sha256 %s  (%d bytes)" % (n, r.returncode, "SAME" if ok else "DIFFERS", hashlib.sha256(
        got).hexdigest()[:16], len(got)))
print("   %d of %d SAME" % (_same, len(PRIOR)))

# ---------------------------------------------------------------------------------------------------------------
_src = open(os.path.join(HERE, "absfold_check.py")).read()
exec(_src[:_src.index('print("\\n(AR) THE RULE')], globals())     # absfold's prefix (+ absimpact's), verbatim
SAB20 = os.environ.get("PREDSPEC20_SABOTAGE") == "1"
if SAB20:
    print("SABOTAGE ON (PREDSPEC20_SABOTAGE=1)")
TOT20 = {"cases": 0, "differ": 0}


def pgroups(p, t, names):
    """PCRE2 only (for constructs Python `re` lacks): whole-match t; None or {name: text or None}"""
    c = _code(p)
    md = L.pcre2_match_data_create_from_pattern_8(c, None)
    rc = L.pcre2_match_8(c, t.encode(), len(t.encode()), 0, ANCH | ENDANCH, md, None)
    out = None
    if rc >= 0:
        ov = L.pcre2_get_ovector_pointer_8(md)
        out = {}
        for nm in names:
            k = L.pcre2_substring_number_from_name_8(c, nm.encode())
            out[nm] = None if ov[2 * k] == UNSET else t.encode()[ov[2 * k]:ov[2 * k + 1]].decode()
    L.pcre2_match_data_free_8(md)
    return out


def echeck(tag, rx, subj, want, pcre_only=False):
    """ENGINE-RUN: rx built from the stated set; run whole in PCRE2 (and Python `re`) against the computed answer"""
    TOT20["cases"] += 1
    got = (pgroups(rx, subj, []) is not None) if pcre_only else whole(rx, subj)
    if got != want:
        TOT20["differ"] += 1
        if TOT20["differ"] < 10:
            print("  DIFFER", tag, repr(subj), "engine", got, "computed", want)


def gen(D_, Rf):
    """THE GENERAL FORM for one label: absent -> some choice from D_ in Rf (D_ = [] fails); present -> Rf(text)"""
    return lambda x: any(Rf(v) for v in D_) if x is None else Rf(x)


# =================================================================================================================
print("\n(RA) reading (a): DOM(h) not computable exactly. P = /(?<h>(?<a>a+)b\\k<a>)?x/ (a backreference), h absent "
      "on `x`")
P_RA = r"(?<h>(?<a>a+)b\k<a>)?x"
cands = ["a" * i + "b" + "a" * j for i in range(1, 7) for j in range(1, 7)]
VALS = sorted({g["h"] for s in cands for g in [pgroups(P_RA, s + "x", ["h"])] if g and g["h"]}, key=len)
print("   VALUES run in PCRE2 over %d candidates a^i b a^j (i, j <= 6): %s" % (len(cands), VALS))
assert all(re.fullmatch(r"(a+)b\1", v) for v in VALS) and len(VALS) == 6
UNDER = VALS                                   # the values met up to a length: a SUBSET of the true DOM
OVER = lambda s: re.fullmatch(r"a+ba+", s) is not None     # the group with \k<a> read as a's own language: a SUPERSET
TRUE = lambda s: re.fullmatch(r"(a+)b\1", s) is not None   # the exact DOM (a^n b a^n), known here by construction
# the set S of each marked condition (h?: S), as a finite list of its members up to length 13 plus a regex for OVER
SETS = [("(h?: /a+ba+/)", r"a+ba+"), ('(h?: "aaba")', r"aaba"), ('(h?: "aabaa")', r"aabaa"), ("(h?: /a+b/)", r"a+b"),
        ("(h?: /a{3}ba*/)", r"a{3}ba*"), ("(h?: !/a+ba+/)", None)]
ALLS = ["a" * i + "b" + "a" * j for i in range(0, 8) for j in range(0, 8)] + ["", "x", "ab", "ba", "abb"]
silent = 0
for name, rx in SETS:
    mem = (lambda s, rx=rx: re.fullmatch(rx, s) is not None) if rx else (lambda s: re.fullmatch(r"a+ba+", s) is None)
    truth = any(mem(v) for v in ALLS if TRUE(v))
    under_yes = any(mem(v) for v in UNDER)
    over_yes = any(mem(v) for v in ALLS if OVER(v)) if rx or True else True
    if SAB20:
        ans = "HOLDS" if over_yes else "FAILS"
    elif under_yes:
        ans = "HOLDS"
    elif not over_yes:
        ans = "FAILS"
    else:
        ans = "COMPILE ERROR"
    wrong = ans in ("HOLDS", "FAILS") and (ans == "HOLDS") != truth
    silent += wrong
    print("   %-18s under %-5s over %-5s exact %-5s -> %-13s%s" % (name, under_yes, over_yes, truth, ans,
                                                                      "  WRONG (silent change)" if wrong else ""))
print("   answers that differ from the exact DOM without a diagnostic: %d (must be 0; > 0 under sabotage)" % silent)
# the same procedure where DOM IS exact (h's group regular): the two approximations coincide, never an error
P_RA2 = r"(?<h>a+ba+)?x"
V2 = sorted({g["h"] for s in cands for g in [groups(P_RA2, s + "x", ["h"])] if g and g["h"]}, key=len)
print("   control, P2 = /(?<h>a+ba+)?x/ (regular): DOM computable; under (run) = %d values, over = a+ba+; "
      "every SETS row answers without an error: %s" % (len(V2), all(
          any(re.fullmatch(rx or "(?!)", v) for v in V2) == any(re.fullmatch(rx or "(?!)", v) for v in ALLS if OVER(v))
          for _, rx in SETS if rx)))

# =================================================================================================================
print("\n(RB) reading (b): the CONTEXT of \"some match\". P = /(?|(?<k>a)(?:;(?<h>\\d))*|(?<k>b)(?:;(?<h>[5-9]))*)/ "
      "(branch reset; PCRE2 only)")
P_RB = r"(?|(?<k>a)(?:;(?<h>\d))*|(?<k>b)(?:;(?<h>[5-9]))*)"
SUBJ_RB = [k + "".join(";" + h for h in hs) for k in "ab" for n in range(3) for hs in itertools.product(D, repeat=n)]
RB = {s: pgroups(P_RB, s, ["k", "h"]) for s in SUBJ_RB}
SUBJ_RB = [s for s in SUBJ_RB if RB[s] is not None]
VAL_PAT = sorted({v for s in SUBJ_RB for v in s.split(";")[1:]})
VAL_CTX = {k: sorted({v for s in SUBJ_RB if s[0] == k for v in s.split(";")[1:]}) for k in "ab"}
print("   %d subjects match; DOM(h) over the pattern %s; given k = a %s; given k = b %s" %
      (len(SUBJ_RB), VAL_PAT, VAL_CTX["a"], VAL_CTX["b"]))
lt5 = lambda x: canon(x) and int(x) < 5
diffs = []
for s in SUBJ_RB:
    hs = s.split(";")[1:]
    passes = hs if hs else [None]
    a1 = all(gen(VAL_PAT, lt5)(x) for x in passes)                  # some match of the pattern (the manager's)
    a2 = all(gen(VAL_CTX[s[0]], lt5)(x) for x in passes)             # some match agreeing with this match's k
    if a1 != a2:
        diffs.append(s)
print("   (h?: <5): 'some match of the pattern' vs 'some match agreeing with k' differ on %d of %d: %s" %
      (len(diffs), len(SUBJ_RB), diffs))
print("   on `b`: pattern reading HOLDS (h = 0 is a value of SOME match, never of one with k = b); context reading "
      "FAILS")
# ENGINE-RUN of the manager's reading (pattern context): a zero-pass subject holds iff some DOM value is < 5
rx_pat = r"(?|a(?:;[0-4])*|b(?:;[5-9])*(?<=b)|b(?:;[0-4])+)"   # zero passes: holds for a and b; with passes: every h < 5
for s in SUBJ_RB:
    hs = s.split(";")[1:]
    want = all(gen(VAL_PAT, lt5)(x) for x in (hs if hs else [None]))
    echeck("RB pattern reading", rx_pat, s, want, pcre_only=True)
print("   ENGINE-RUN (pattern reading, regex from the set) over %d subjects" % len(SUBJ_RB))

# =================================================================================================================
print("\n(RC) reading (c): a DEFAULTED label inside `all`. P = /(?:(?<h>\\d+)(?::(?<m>\\d\\d))?,)*/, 259 lists")
P_OP = r"(?:(?<h>\d+)(?::(?<m>\d\d))?,)*"
OP_ITEMS = [(h, m) for h in ("3", "12") for m in (None, "15", "45")]
SUBJ_OP = ["".join("%s%s," % (h, "" if m is None else ":" + m) for h, m in its)
           for n in range(4) for its in itertools.product(OP_ITEMS, repeat=n)]
for s in SUBJ_OP:
    assert whole(P_OP, s)
spl = lambda s: [(it.split(":")[0], it.split(":")[1] if ":" in it else None) for it in s.split(",")[:-1]]
H100 = [str(i) for i in range(100)] + ["0" + str(i) for i in range(10)]
M2 = ["%02d" % i for i in range(100)]
Rhm = lambda t: canon(t[0]) and int(t[0]) < 10 and canon(t[1]) and int(t[1]) < 30


def op(s, marks, defaults):
    its = spl(s)
    tuples = [(Z, Z)] if not its else [(h, m if m is not None else P) for h, m in its]
    return cond(AR, tuples, Rhm, [H100, M2], marks, defaults)


A_ALL = {s: op(s, (0,), {1: "0"}) for s in SUBJ_OP}        # all((h: <10, m = 0: <30)) = (h?: <10, m = 0: <30)
A_PLAIN = {s: op(s, (), {1: "0"}) for s in SUBJ_OP}        # (h: <10, m = 0: <30)
for s in ("", "3,", "3:15,", "3:45,", "12,"):
    print("   %-8r all((h: <10, m = 0: <30)) %s   (h: <10, m = 0: <30) %s" % (s, hfx(A_ALL[s]), hfx(A_PLAIN[s])))
count("all((h, m = 0)) vs the plain (h, m = 0) record", SUBJ_OP, A_ALL, A_PLAIN, "all", "plain")
rx_all = r"(?:[0-9](?::(?:1[0-9]|2[0-9]))?,)*"            # from the set: h a canonical < 10, m absent (0) or < 30
for s in SUBJ_OP:
    echeck("RC all with default", rx_all, s, A_ALL[s])
print("   ENGINE-RUN: all((h: <10, m = 0: <30)) over the 259 (regex from the set)")
try:
    cond(AR, [(Z, Z)], Rhm, [H100, M2], (0, 1), {1: "0"})
    print("   the not-both reading of all (m marked AND defaulted): NOT refused (unexpected)")
except (NotBoth, ValueError):
    print("   the other reading (all marks m too: `m? = 0`) is the not-both compile error: REFUSED by the engine, "
          "as written")

# =================================================================================================================
print("\n(RD) reading (d): zero-pass-empty under F1. /(?<a>\\d)-(?<k>\\d)(?:;(?<h>\\d))*/ on `0-3`")
C1 = lambda t: canon(t[0]) and int(t[0]) < 0 and t[1] == "3"
C2 = lambda t: canon(t[0]) and canon(t[1]) and (int(t[0]), int(t[1])) < (0, 0)
print("   (h?: <$a, k: 3) %s   ((h?, k): < ($a, 0)) %s   (F1: no value of h would do; both FAIL)" %
      (hfx(cond(AR, [(Z, "3")], C1, [D, D], (0,))), hfx(cond(AR, [(Z, "3")], C2, [D, D], (0,)))))

# =================================================================================================================
print("\n(E1) proposal (e1): a computed label reading an absent label. P = /(?<mname>Jan|Feb|Mar)?-(?<d>\\d)/, "
      "mnum := $mname.index")
P_E1 = r"(?<mname>Jan|Feb|Mar)?-(?<d>\d)"
SUBJ_E1 = [mn + "-" + d for mn in ("", "Jan", "Feb", "Mar") for d in D]
IDX = {"Jan": "1", "Feb": "2", "Mar": "3"}
MNUM = {}
for s in SUBJ_E1:
    g = groups(P_E1, s, ["mname", "d"])
    assert g is not None
    MNUM[s] = IDX[g["mname"]] if g["mname"] is not None else None   # absent where its input is absent
DOM_MNUM = sorted({v for v in MNUM.values() if v is not None})
print("   %d subjects RUN; DOM(mnum) = the values mnum takes in some match: %s (the map's image of DOM(mname))" %
      (len(SUBJ_E1), DOM_MNUM))
lt3 = lambda x: canon(x) and int(x) < 3
gt5 = lambda x: canon(x) and int(x) > 5
E1F = [("(mnum: <3)", lambda x: (x is not None or SAB20) and (x is None or lt3(x)),
        r"(?:Jan|Feb)-\d"),
       ("(mnum?: <3)", gen(DOM_MNUM, lt3), r"(?:Jan|Feb)?-\d"),
       ("(mnum = 9: <3)", lambda x: lt3(x if x is not None else "9"), r"(?:Jan|Feb)-\d"),
       ("(mnum = 1: <3)", lambda x: lt3(x if x is not None else "1"), r"(?:Jan|Feb)?-\d"),
       ("(mnum?: >5)", gen(DOM_MNUM, gt5), r"(?!)")]
for name, f, rx in E1F:
    ans = {s: f(MNUM[s]) for s in SUBJ_E1}
    for s in SUBJ_E1:
        echeck("E1 " + name, rx, s, ans[s])
    print("   %-16s on `-5` %s; holds on %2d of %d" % (name, hfx(ans["-5"]), sum(ans.values()), len(SUBJ_E1)))
print("   the compile-error alternative would refuse all five programs (mname can be absent); the proposal answers "
      "them by ruled point (1) and the general form, with no new rule")

# =================================================================================================================
print("\n(E2) proposal (e2): `$a` on an absent a. P = /(?<a>\\d)?-(?<b>\\d)/")
P_E2 = r"(?<a>\d)?-(?<b>\d)"
SUBJ_E2 = [a + "-" + b for a in [""] + D for b in D]
E2 = {s: groups(P_E2, s, ["a", "b"]) for s in SUBJ_E2}
gtv = lambda b, a: a is not None and int(b) > int(a)               # D = {} for a: no choice exists -> fails
eqv = lambda b, a: a is not None and b == a
for name, f, rx in (("(b: >$a)", gtv, "(?:" + "|".join("%s-%s" % (a, alt([b for b in D if int(b) > int(a)]))
                                                        for a in D) + ")"),
                    ("(b: /${$a}/)", eqv, "(?:" + "|".join("%s-%s" % (a, a) for a in D) + ")")):
    ans = {s: f(E2[s]["b"], E2[s]["a"]) for s in SUBJ_E2}
    for s in SUBJ_E2:
        echeck("E2 " + name, rx, s, ans[s])
    ab = [s for s in SUBJ_E2 if E2[s]["a"] is None]
    print("   %-14s holds on %2d of %d; on the %d subjects with a absent: %d hold (D = {}: FAILS)" %
          (name, sum(ans.values()), len(SUBJ_E2), len(ab), sum(ans[s] for s in ab)))
print("   NOT DECIDED by the general form: whether a default written for a in the same condition, "
      "`(a = 0: <10, b: >$a)`, also reaches `$a`. On `-5`: if it reaches, %s; if not, %s" %
      (hfx(gtv("5", "0")), hfx(gtv("5", None))))

# =================================================================================================================
print("\n(E3) proposal (e3): the mark through a macro. office_c := ((h, m): padded(between((9, 0), (17, 0)))); "
      "t2 & all(office_c)")
H = [str(i) for i in range(10)] + ["%02d" % i for i in range(100)]
M = ["%02d" % i for i in range(100)]
P_T2 = r"(?<h>\d{1,2})(?::(?<m>\d\d))?"
SUBJ_T2 = H + [h + ":" + m for h in H for m in M]
num = lambda x: x.isdigit()
OFFICE = lambda t: num(t[0]) and num(t[1]) and (9, 0) <= (int(t[0]), int(t[1])) <= (17, 0)
T2 = {}
for s in SUBJ_T2:
    g = groups(P_T2, s, ["h", "m"])
    T2[s] = (g["h"], g["m"] if g["m"] is not None else U)
DOM_M = sorted({T2[s][1] for s in SUBJ_T2 if not isinstance(T2[s][1], Abs)})
a_all = {s: cond(AR, [T2[s]], OFFICE, [H, DOM_M], (0, 1)) for s in SUBJ_T2}   # all(c): every label marked
a_m = {s: cond(AR, [T2[s]], OFFICE, [H, DOM_M], (1,)) for s in SUBJ_T2}        # ((h, m?): office)
count("t2 & all(office_c) vs t2 & ((h, m?): office)", SUBJ_T2, a_all, a_m, "all", "m?")
h_absent = sum(1 for s in SUBJ_T2 if isinstance(T2[s][0], Abs))
print("   h is absent in %d of %d t2 matches: the mark `all` puts on h is never consulted (the merged warning, (F))" %
      (h_absent, len(SUBJ_T2)))
print("   a per-label mark on a PASSED condition (mark m but not h inside office_c from outside): no spelling in rev "
      "20's language (no label parameter, the field reference paused): OPEN, not decided by the general form")

# =================================================================================================================
print("\n(F) proposal (f): ONE warning, \"the candidate set of label x is never consulted\" (a mark or a default on a "
      "label that is never absent where the condition reads it)")
PROGS = [("t := /(?<h>\\d{1,2}):(?<m>\\d\\d)/", r"(?<h>\d{1,2}):(?<m>\d\d)", "m"),
         ("t2 (m optional)", P_T2, "m"),
         ("list (?:(?<h>\\d+)(?::(?<m>\\d\\d))?,)*", P_OP, "m"),
         ("list, h", P_OP, "h")]
POP = {"m": [h + ":" + m for h in ("9", "10") for m in ("00", "45")] + ["9", "10"]}
for name, p, lab in PROGS:
    subs = [s for s in SUBJ_T2 if whole(p, s)] if "list" not in name else SUBJ_OP
    absent = 0
    for s in subs:
        if "list" in name:
            its = spl(s)
            absent += (not its) or (lab == "m" and any(m is None for _, m in its))
        else:
            absent += groups(p, s, [lab])[lab] is None
    print("   %-40s label %s absent in %4d of %5d matches -> `%s?` / `%s = v`: %s" %
          (name, lab, absent, len(subs), lab, lab, "WARN (never consulted)" if absent == 0 else "no warning"))

print("\nTOTAL PART B: %d ENGINE-RUN cases, %d differ; %d engine disagreements (PCRE2 vs Python `re`); "
      "%d whole-match probes" % (TOT20["cases"], TOT20["differ"], DIS[0], TOT["probes"]))
