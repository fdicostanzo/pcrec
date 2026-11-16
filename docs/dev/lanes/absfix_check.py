# absfix: evidence for docs/design/joint_condition.md §4H and docs/dev/lanes/absfix_report.md (review r28's rulings,
# /var/tmp scratch dispositions.md, applied by lane absfix 2026-11-16).
#
# What it runs (each block names its population; every count the note quotes is printed here):
#   (DOM-*)  the DOMAIN of "some value" for the optional mark, an OPEN PARAMETER (owner question mark-domain), under
#            three candidates, over the same populations:
#              ANY     any text at all (the manager's withdrawn 14:50 (c));
#              GROUP   the texts the label's GROUP can match, read from the group's own text (syntactic);
#              VALUES  the values the label can take in some match of the pattern (its value language in context),
#                      computed by RUNNING the pattern (PCRE2 + Python `re`) over the population, never from its text.
#   (LOOP)   is `?` (an upper bound of 1) a LOOP for the pairing rule? both readings (owner question optional-as-loop).
#   (ALL)    `all(c)` := c with every label marked, read F1 (ruling C); the corrected (LI) / L36 / (OP) counts.
#   (NONE)   the mark COUNTED inside some/count/occurs (ruling E): `occurs.none(((h, m?): !R))` on (OP), per domain.
#   (GF)     the general form (ruling K): an absent label reads as a candidate set D (unmarked {}, `m = v` {v}, `m?` the
#            domain); the condition holds when some choice from D puts the tuple in the set. Written WITHOUT part()/tup()
#            and compared with the ruled engine (absfold's cond()) on (AR), (TM2), (ZJ), (ZE) under each domain.
#
# REUSE: absfold_check.py's prefix (which itself execs absimpact_check.py's engines, part(), tup(), plain(), groups(),
# check(), alt()) is exec'd verbatim; absfold's tables are NOT re-run here (absfold_check.out stands).
# Run (worktree root): `timeout 300 python3 -I docs/dev/lanes/absfix_check.py`.
# Sabotage: `ABSFIX_SABOTAGE=1 ...` makes VALUES read the group's text (= GROUP); the (DOM-2SP) VALUES line must then
# split the two spellings, so the check can fail.
#
# ANY is a set no program can enumerate. It is represented by the group's strings plus EXTRA (the empty string, a
# non-numeral "x", "-1", "1.5", every numeral 0..199, every 2-digit padded numeral, "000".."009"). Every set used below
# is a numeric comparison over canonical (or padded) numerals or a literal set of such strings, so any text outside
# EXTRA answers as "x" (non-numeral) or as a numeral EXTRA already covers: the representative set decides each
# existential exactly as all texts would.
import os, re, itertools, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "absfold_check.py")).read()
exec(_src[:_src.index('print("\\n(AR) THE RULE')], globals())     # absfold's prefix (+ absimpact's), verbatim
SABX = os.environ.get("ABSFIX_SABOTAGE") == "1"
if SABX:
    print("SABOTAGE ON (ABSFIX_SABOTAGE=1): VALUES reads the group's text")

EXTRA = ["", "x", "-1", "1.5"] + [str(i) for i in range(200)] + ["%02d" % i for i in range(100)] + \
        ["%03d" % i for i in range(10)]


def anyd(group):
    return sorted(set(group) | set(EXTRA), key=lambda s: (len(s), s))


def values(p, label, subjects, group):
    """VALUES: the texts `label` holds in some whole match of p over `subjects` (PCRE2 and Python `re` agree, checked
    by groups()). For the looped labels here every value occurs as the LAST pass of a one-pass subject in the
    population, so the last-iteration capture reaches every value."""
    if SABX:
        return list(group)
    out = set()
    for s in subjects:
        g = groups(p, s, [label])
        if g is not None and g[label] is not None:
            out.add(g[label])
    return sorted(out, key=lambda s: (len(s), s))


CANDS = ("ANY", "GROUP", "VALUES")
REC = lambda t: S5(t[0]) and T37(t[1])
HM = lambda t: canon(t[0]) and int(t[0]) < 10 and canon(t[1]) and int(t[1]) < 30
NOT = lambda f: (lambda t: not f(t))
NOTLT10 = lambda x: not (canon(x) and int(x) < 10)          # !(<10): every text that is not a numeral below 10
S59 = lambda x: canon(x) and 5 <= int(x) <= 9
WIT = {c: [] for c in CANDS}          # (i): answers witnessed only by a value outside VALUES, per candidate
SPL2 = {c: 0 for c in CANDS}          # (ii): two spellings of one pattern split
SET1 = {c: 0 for c in CANDS}          # (iii): two spellings of one set split
SETV = {c: 0 for c in CANDS}          # (iii'): two different sets that agree on every value the label can hold
RAMP = {c: 0 for c in CANDS}          # (iv): record vs & split


def pair_counts(title, subjects, ans, cands=CANDS):
    for a, b in itertools.combinations(cands, 2):
        count("%s: %s vs %s" % (title, a, b), subjects, ans[a], ans[b], a, b)


def witness(title, subjects, ans):
    """(i): subjects where a candidate HOLDS but the same evaluation over VALUES FAILS (a never-holdable witness)"""
    for c in CANDS:
        w = [s for s in subjects if ans[c][s] and not ans["VALUES"][s]]
        if w:
            WIT[c].append((title, len(w), len(subjects), min(w, key=lambda s: (len(s), s))))


# =================================================================================================================
print("\n(DOM-AR) table (AR)'s marked cells per domain: h absent (one kind), h's group \\d, VALUES of a \\d group = 0..9")
DOM_AR = {"ANY": anyd(D), "GROUP": D, "VALUES": D}
for title, shape in (("one (h?: <5)", lambda d: cond(AR, [(Z,)], lambda t: S5(t[0]), [d], (0,))),
                     ("one (h?: !(<10))", lambda d: cond(AR, [(Z,)], lambda t: NOTLT10(t[0]), [d], (0,))),
                     ("record (h?: <5, k: 3..7), k = 6",
                      lambda d: cond(AR, [(Z, "6")], lambda t: S5(t[0]) and T37(t[1]), [d, D], (0,))),
                     ("record (h?: !(<10), k: 3..7), k = 6",
                      lambda d: cond(AR, [(Z, "6")], lambda t: NOTLT10(t[0]) and T37(t[1]), [d, D], (0,))),
                     ("joint ((h?, k): >= (5, 3)), k = 6",
                      lambda d: cond(AR, [(Z, "6")], lambda t: canon(t[0]) and (int(t[0]), int(t[1])) >= (5, 3),
                                     [d, D], (0,)))):
    r = {c: shape(DOM_AR[c]) for c in CANDS}
    print("   %-40s " % title + "  ".join("%s %s" % (c, hfx(r[c])) for c in CANDS))
    witness("AR " + title, ["-"], {c: {"-": r[c]} for c in CANDS})

# =================================================================================================================
print("\n(DOM-TM2) t2 := /(?<h>\\d{1,2})(?::(?<m>\\d\\d))?/, 11,110 subjects; R = padded(>= (9, 30)), "
      "office = padded(between((9, 0), (17, 0)))")
H = [str(i) for i in range(10)] + ["%02d" % i for i in range(100)]
M = ["%02d" % i for i in range(100)]
P_T2 = r"(?<h>\d{1,2})(?::(?<m>\d\d))?"
SUBJ_T2 = H + [h + ":" + m for h in H for m in M]
GE930 = lambda t: num(t[0]) and num(t[1]) and (int(t[0]), int(t[1])) >= (9, 30)
OFFICE = lambda t: num(t[0]) and num(t[1]) and (9, 0) <= (int(t[0]), int(t[1])) <= (17, 0)
DOM_M = {"ANY": anyd(M), "GROUP": M, "VALUES": values(P_T2, "m", SUBJ_T2, M)}
print("   m: GROUP %d texts (\\d\\d), VALUES %d (run), ANY %d (represented)" %
      (len(DOM_M["GROUP"]), len(DOM_M["VALUES"]), len(DOM_M["ANY"])))
T2T = {}
for s in SUBJ_T2:
    g = groups(P_T2, s, ["h", "m"])
    T2T[s] = (g["h"], g["m"] if g["m"] is not None else U)
TM = {}
for form, Rf in (("((h, m?): R)", GE930), ("((h, m?): !R)", NOT(GE930)), ("((h, m?): !office)", NOT(OFFICE))):
    TM[form] = {c: {s: cond(AR, [T2T[s]], Rf, [H, DOM_M[c]], (1,)) for s in SUBJ_T2} for c in CANDS}
    print("   %-20s on '10': %s" % (form, "  ".join("%s %s" % (c, hfx(TM[form][c]["10"])) for c in CANDS)))
    pair_counts("   t2 " + form, SUBJ_T2, TM[form])
    witness("TM2 " + form, SUBJ_T2, TM[form])
for c in CANDS:
    both = [s for s in SUBJ_T2 if TM["((h, m?): R)"][c][s] and TM["((h, m?): !R)"][c][s]]
    print("   %-6s ((h, m?): R) and ((h, m?): !R) BOTH hold on %3d of 11110  e.g. %s" %
          (c, len(both), sorted(both, key=lambda s: (len(s), s))[:3]))
# ENGINE-RUN: GROUP/VALUES `((h, m?): !office)` built from the SET (rows outside office; an m-less h when some \d\d m
# takes (h, m) outside office), never from part()
hs_out = [h for h in H if any(not OFFICE((h, m)) for m in M)]
_ro = {h: [m for m in M if not OFFICE((h, m))] for h in H}
rows_out = "|".join(re.escape(h) + ":" + ("\\d\\d" if len(ms) == len(M) else alt(ms)) for h, ms in _ro.items() if ms)
for s in SUBJ_T2:
    check("TM2 !office GROUP", "(?:" + rows_out + "|" + alt(hs_out) + ")", s, TM["((h, m?): !office)"]["GROUP"][s])
print("   ENGINE-RUN: ((h, m?): !office) under GROUP over 11,110 (regex from the set)")

# =================================================================================================================
print("\n(DOM-RZ) /(?<k>\\d)(?:;(?<h>\\d))*/, 1,110 subjects: marked h per domain; record vs & per domain")
P_RZ = r"(?<k>\d)(?:;(?<h>\d))*"
SUBJ_RZ = [k + "".join(";" + h for h in hs) for k in D for n in range(3) for hs in itertools.product(D, repeat=n)]
DOM_H = {"ANY": anyd(D), "GROUP": D, "VALUES": values(P_RZ, "h", SUBJ_RZ, D)}
RZT = {}
for s in SUBJ_RZ:
    k, *hs = s.split(";")
    RZT[s] = (k, hs, [(h, k) for h in hs] if hs else [(Z, k)])
for sname, S in (("<5", S5), ("5..9", S59), ("!(<10)", NOTLT10)):
    rec = {c: {s: cond(AR, RZT[s][2], lambda t: S(t[0]) and T37(t[1]), [DOM_H[c], D], (0,)) for s in SUBJ_RZ}
           for c in CANDS}
    amp = {c: {s: plain(AR, RZT[s][1], S, DOM_H[c], mark=True) and T37(RZT[s][0]) for s in SUBJ_RZ} for c in CANDS}
    for c in CANDS:
        RAMP[c] += count("(h?: %s, k: 3..7) vs (h?: %s) & (k: 3..7) [%s]" % (sname, sname, c), SUBJ_RZ, rec[c],
                         amp[c], "rec", "&")
    pair_counts("   (h?: %s, k: 3..7)" % sname, SUBJ_RZ, rec)
    witness("RZ (h?: %s, k: 3..7)" % sname, SUBJ_RZ, rec)

# =================================================================================================================
print("\n(DOM-ZJ) jcfold2's non-product sets on (RZ)'s pattern, zero passes, h MARKED: the subjects that HOLD")
ZJS = [
    ("((h?, k): >= (5, 3))", lambda t: canon(t[0]) and (int(t[0]), int(t[1])) >= (5, 3)),
    ("((h?, k): (0|1|2, 3|4) | (5, 5))", lambda t: (t[0] in ("0", "1", "2") and t[1] in "34") or t == ("5", "5")),
    ("((h?, k): (\"x\", 3) | (0, 5))", lambda t: t == ("x", "3") or t == ("0", "5")),
    ("((h?, k): < (0, 3))", lambda t: canon(t[0]) and (int(t[0]), int(t[1])) < (0, 3)),
]
ZS = [s for s in SUBJ_RZ if ";" not in s]
for name, Rf in ZJS:
    a = {c: {s: cond(AR, RZT[s][2], Rf, [DOM_H[c], D], (0,)) for s in ZS} for c in CANDS}
    print("   %-36s " % name + "  ".join("%s %s" % (c, sorted(s for s in ZS if a[c][s])) for c in CANDS))
    pair_counts("      " + name, ZS, a)
    witness("ZJ " + name, ZS, a)

# =================================================================================================================
print("\n(DOM-ZE) /(?<a>\\d)-(?<k>\\d)(?:;(?<h>\\d))*/, 11,100 subjects, the set empty through $a; h MARKED (F1)")
P_ZE = r"(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*"
SUBJ_ZE = ["%s-%s" % (a, k) + "".join(";" + h for h in hs) for a in D for k in D for n in range(3)
           for hs in itertools.product(D, repeat=n)]
DOM_HE = {"ANY": anyd(D), "GROUP": D, "VALUES": values(P_ZE, "h", SUBJ_ZE, D)}
ZET = {}
for s in SUBJ_ZE:
    head, *hs = s.split(";")
    a, k = head.split("-")
    ZET[s] = (a, k, hs, [(h, k) for h in hs] if hs else [(Z, k)])
C1 = lambda a: (lambda t: canon(t[0]) and int(t[0]) < int(a) and t[1] == "3")
C2 = lambda a: (lambda t: canon(t[0]) and canon(t[1]) and (int(t[0]), int(t[1])) < (int(a), 0))
ZEA = {}
for nm, mk in (("C1 (h?: <$a, k: 3)", C1), ("C2 ((h?, k): < ($a, 0))", C2)):
    ZEA[nm] = {c: {s: cond(AR, ZET[s][3], mk(ZET[s][0]), [DOM_HE[c], D], (0,)) for s in SUBJ_ZE} for c in CANDS}
    pair_counts("   " + nm, SUBJ_ZE, ZEA[nm])
    witness("ZE " + nm, SUBJ_ZE, ZEA[nm])
A0 = [s for s in SUBJ_ZE if s.startswith("0-")]
for c in CANDS:
    amp = {s: plain(AR, ZET[s][2], lambda x, a=ZET[s][0]: canon(x) and int(x) < int(a), DOM_HE[c], mark=True) and
           ZET[s][1] == "3" for s in SUBJ_ZE}
    RAMP[c] += count("C1 marked vs (h?: <$a) & (k: 3) [%s]" % c, SUBJ_ZE, ZEA["C1 (h?: <$a, k: 3)"][c], amp,
                     "rec", "&")
    SET1[c] += count("a = 0, both spellings EMPTY: C1 vs C2 marked [%s]" % c, A0, ZEA["C1 (h?: <$a, k: 3)"][c],
                     ZEA["C2 ((h?, k): < ($a, 0))"][c], "C1", "C2")

# =================================================================================================================
print("\n(DOM-2SP) two spellings of one pattern: h's group text differs, the matches and captures do not")
SP2 = {
    "P1 /(?<k>\\d)(?:;(?<h>\\d)(?<=[0-4]))*/": (r"(?<k>\d)(?:;(?<h>\d)(?<=[0-4]))*", D),
    "P2 /(?<k>\\d)(?:;(?<h>[0-4]))*/": (r"(?<k>\d)(?:;(?<h>[0-4]))*", [str(i) for i in range(5)]),
    "P3 /(?<k>\\d)(?:;(?=[0-4])(?<h>\\d))*/": (r"(?<k>\d)(?:;(?=[0-4])(?<h>\d))*", D),
}
same = 0
SUBJ_2 = []
for s in SUBJ_RZ:
    gs = [groups(p, s, ["k", "h"]) for p, _ in SP2.values()]
    same += all(g == gs[0] for g in gs)
    if gs[0] is not None:
        SUBJ_2.append(s)
print("   P1, P2, P3 give the same match and captures on %d of %d (RZ) subjects; %d match" %
      (same, len(SUBJ_RZ), len(SUBJ_2)))
SP2A = {}
for nm, (p, grp) in SP2.items():
    dom = {"ANY": anyd(grp), "GROUP": grp, "VALUES": values(p, "h", SUBJ_RZ, grp)}
    print("   %-40s h: GROUP %s, VALUES %s" % (nm, "".join(dom["GROUP"]), "".join(dom["VALUES"])))
    SP2A[nm] = {c: {} for c in CANDS}
    for s in SUBJ_2:
        k, *hs = s.split(";")
        tu = [(h, k) for h in hs] if hs else [(Z, k)]
        for c in CANDS:
            SP2A[nm][c][s] = cond(AR, tu, lambda t: S59(t[0]) and T37(t[1]), [dom[c], D], (0,))
names2 = list(SP2)
for c in CANDS:
    zs = [s for s in SUBJ_2 if ";" not in s]
    print("   (h?: 5..9, k: 3..7) %-6s zero-pass subjects HOLDING: P1 %d of 10, P2 %d of 10, P3 %d of 10" %
          ((c,) + tuple(sum(SP2A[n][c][s] for s in zs) for n in names2)))
    for n in (names2[0], names2[2]):
        SPL2[c] += count("%s vs P2 [%s]" % (n[:2], c), SUBJ_2, SP2A[n][c], SP2A[names2[1]][c], n[:2], "P2")
witness("2SP P1 (h?: 5..9, k: 3..7)", SUBJ_2, {cc: SP2A[names2[0]][cc] for cc in CANDS})

# =================================================================================================================
print("\n(DOM-SET) two spellings of one set, and two different sets that agree on every value h can hold; (RZ)")
L04 = lambda x: x in ("0", "1", "2", "3", "4")
LT0 = lambda x: canon(x) and int(x) < 0
for c in CANDS:
    a = {s: plain(AR, RZT[s][1], S5, DOM_H[c], mark=True) for s in SUBJ_RZ}
    b = {s: plain(AR, RZT[s][1], L04, DOM_H[c], mark=True) for s in SUBJ_RZ}
    SET1[c] += count("(h?: <5) vs (h?: 0|1|2|3|4)  [one set, two spellings; %s]" % c, SUBJ_RZ, a, b, "<5", "0|..|4")
    e = {s: plain(AR, RZT[s][1], LT0, DOM_H[c], mark=True) for s in SUBJ_RZ}
    d = {s: plain(AR, RZT[s][1], NOTLT10, DOM_H[c], mark=True) for s in SUBJ_RZ}
    SETV[c] += count("(h?: <0) vs (h?: !(<10))  [both hold no \\d; %s]" % c, SUBJ_RZ, e, d, "<0", "!(<10)")

# =================================================================================================================
print("\n(DOM-COMP) ruling R2 (4): where VALUES (the values h takes in some match) is NOT read off the group's text; "
      "each RUN by enumeration, PCRE2 only (Python `re` lacks branch reset and recursion)")


def pc(p, t, names):
    """PCRE2-only whole match: None or {name: text or None} (the probes groups() cross-checks cannot take)"""
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
    TOT["probes"] += 1
    return out


def vals(p, subjects, label="h", given=None):
    out = set()
    for s in subjects:
        g = pc(p, s, [label] + ([given[0]] if given else []))
        if g is not None and g[label] is not None and (given is None or g[given[0]] == given[1]):
            out.add(g[label])
    return sorted(out, key=lambda s: (len(s), s))


def strs(alpha, n):
    return [""] + ["".join(c) for k in range(1, n + 1) for c in itertools.product(alpha, repeat=k)]


COMP = [
    ("LOOKAROUND (regular; a product with the lookaround's language)", r"(?<h>\d)(?<=[0-4])",
     strs("0123456789", 1), "\\d"),
    ("ATOMIC / POSSESSIVE (the group can match, the match never keeps it)", r"(?<h>\d++)5|x", strs("0159x", 3),
     "\\d++"),
    ("CONDITIONAL on another label (the branch read depends on the match)", r"(?<a>x)?(?<h>(?(a)[0-4]|[5-9]))",
     strs("0459x", 2), "(?(a)[0-4]|[5-9])"),
    ("BACKREFERENCE (the value set is not regular: a^n b a^n)", r"(?<h>(?<a>a+)b\k<a>)", strs("ab", 7),
     "(?<a>a+)b\\k<a>"),
    ("RECURSION (the value set is context-free: balanced parentheses)", r"(?<h>\((?:x|(?&h))*\))", strs("()x", 6),
     "\\((?:x|(?&h))*\\)"),
]
for title, p, subj, gtext in COMP:
    v = vals(p, subj)
    print("   %s\n      %-34s group text %-22s VALUES (subjects to length %d): %s" %
          (title, "/" + p + "/", gtext, max(len(s) for s in subj), " ".join(repr(x) for x in v[:12]) +
           (" ..." if len(v) > 12 else "") + ("  (EMPTY)" if not v else "")))
bv = vals(r"(?<h>(?<a>a+)b\k<a>)", strs("ab", 7))
print("      BACKREFERENCE check: every value is a^n b a^n: %s; RECURSION check: every value balanced: %s" %
      (all(re.fullmatch(r"(a+)b\1", x) for x in bv),
       all(x.count("(") == x.count(")") for x in vals(r"(?<h>\((?:x|(?&h))*\))", strs("()x", 6)))))
print("   CONTEXT (R2's \"some match of the pattern\": any match, or a match agreeing with this one's other labels?)")
PBR = r"(?|(?<k>a)(?:;(?<h>\d))*|(?<k>b)(?:;(?<h>[5-9]))*)"
SUBJ_BR = [k + "".join(";" + h for h in hs) for k in "ab" for n in range(2) for hs in itertools.product(D, repeat=n)]
v_all = vals(PBR, SUBJ_BR)
v_b = vals(PBR, SUBJ_BR, given=("k", "b"))
print("      /%s/ (branch reset): VALUES of h over the pattern %s; given k = b: %s" % (PBR, "".join(v_all), "".join(v_b)))
print("      (h?: <5) on 'b' (zero passes): over the pattern's VALUES %s (h = 0 is a value of SOME match); given k = b "
      "%s" % (hfx(any(S5(x) for x in v_all)), hfx(any(S5(x) for x in v_b))))

# =================================================================================================================
print("\n(DOM-SUMMARY) per candidate: (i) a never-holdable value witnesses an answer; (ii) two spellings of one "
      "pattern split; (iii) two spellings of one set split [(iii') sets equal on every holdable value split]; "
      "(iv) record = &")
for c in CANDS:
    wn = sum(w[1] for w in WIT[c])
    print("   %-6s (i) %-3s (%d answers in %d tables%s)  (ii) %-3s (%d)  (iii) %-3s (%d) [(iii') %d]  (iv) %s (%d split)"
          % (c, "YES" if wn else "no", wn, len(WIT[c]),
             "" if not WIT[c] else "; e.g. %s on %r" % (WIT[c][0][0], WIT[c][0][3]),
             "YES" if SPL2[c] else "no", SPL2[c], "YES" if SET1[c] else "no", SET1[c], SETV[c],
             "KEPT" if RAMP[c] == 0 else "BROKEN", RAMP[c]))
    for w in WIT[c]:
        print("          (i) %-44s %5d of %6d  smallest %r" % w)

# =================================================================================================================
print("\n(LOOP) optional-as-loop: is `?` (upper bound 1) a loop for the pairing rule?")
print("   (OP) /(?:(?<h>\\d+)(?::(?<m>\\d\\d))?,)*/ & (h: <10, m: <30), 259 lists; WANTED = the answers before 14:31")
P_OP = r"(?:(?<h>\d+)(?::(?<m>\d\d))?,)*"
OP_ITEMS = [(h, m) for h in ("3", "12") for m in (None, "15", "45")]
SUBJ_OP = ["".join("%s%s," % (h, "" if m is None else ":" + m) for h, m in its)
           for n in range(4) for its in itertools.product(OP_ITEMS, repeat=n)]
DH = [str(i) for i in range(13)]
DM2 = ["%02d" % i for i in range(100)]
DOM_OPM = {"ANY": anyd(DM2), "GROUP": DM2, "VALUES": values(P_OP, "m", SUBJ_OP + [h + ":" + m + "," for h in ("3",)
                                                                                  for m in DM2], DM2)}
OPI = {}
for s in SUBJ_OP:
    assert whole(P_OP, s)
    OPI[s] = [(i.split(":")[0], i.split(":")[1] if ":" in i else None) for i in s.split(",")[:-1]]


def op_tuples(s, loop):
    """not a loop: a pass without m is 'missing in a pass' (P); `?` a loop: m's pairing loop is the `?`, which ran
    ZERO passes in that reach (Z). No item: the `*` ran zero passes (and the `?` was never reached)."""
    its = OPI[s]
    if not its:
        return [(Z, Z)]
    return [(h, m if m is not None else (Z if loop else P)) for h, m in its]


def all_def(tuples, Rf, doms, defaults=None):
    """ruling C: all(c) := c with every label marked, read F1 (a defaulted label: see LEFT OPEN; not used here)"""
    return cond(AR, tuples, Rf, doms, tuple(range(len(doms))), defaults)


def a2v(tuples, loop, s):
    # withdrawn reading A2v: a tuple whose pairing loop ran no pass HOLDS outright (outside label untested)
    if not OPI[s]:
        return True
    return all(True if (loop and t[1] is Z) else cond(AR, [t], HM, [DH, DM2]) for t in tuples)


def a2z(tuples):
    # withdrawn reading A2z: zero-pass (Z) absences read as before 14:31 (projected), any other absence fails
    return cond(TD, tuples, HM, [DH, DM2])


WANT = {s: cond(TD, op_tuples(s, False), HM, [DH, DM2]) for s in SUBJ_OP}
LP = {}
for loop in (False, True):
    t = {s: op_tuples(s, loop) for s in SUBJ_OP}
    LP[loop] = {
        "(h: <10, m: <30)": {s: cond(AR, t[s], HM, [DH, DM2]) for s in SUBJ_OP},
        "(h?, m?)": {s: cond(AR, t[s], HM, [DH, DM2], (0, 1)) for s in SUBJ_OP},
        "(h?, m = 0)": {s: cond(AR, t[s], HM, [DH, DM2], (0,), {1: "0"}) for s in SUBJ_OP},
        "(h, m = 0)": {s: cond(AR, t[s], HM, [DH, DM2], (), {1: "0"}) for s in SUBJ_OP},
        "all(...) [C]": {s: all_def(t[s], HM, [DH, DM2]) for s in SUBJ_OP},
        "occurs.none(((h, m?): !R)) [E]": {s: not any(cond(AR, [tt], NOT(HM), [DH, DM2], (1,)) for tt in t[s]
                                                      if OPI[s]) for s in SUBJ_OP},
        "all A2v (withdrawn)": {s: a2v(t[s], loop, s) for s in SUBJ_OP},
        "all A2z (withdrawn)": {s: a2z(t[s]) for s in SUBJ_OP},
    }
for f in LP[False]:
    count("%-34s vs WANTED, `?` NOT a loop" % f, SUBJ_OP, WANT, LP[False][f], "want", "notloop")
    count("%-34s vs WANTED, `?` a loop" % f, SUBJ_OP, WANT, LP[True][f], "want", "loop")
    count("%-34s `?` a loop vs not" % f, SUBJ_OP, LP[False][f], LP[True][f], "notloop", "loop")

print("   SIBLING drill: A = /(?<k>\\d)?-(?<h>\\d)?/, B = /(?:(?<k>\\d)|)-(?:(?<h>\\d)|)/ (x? = (?:x|), CF 13:38), "
      "condition (h: <5, k?: 3..7) and its & spelling")
PA, PB = r"(?<k>\d)?-(?<h>\d)?", r"(?:(?<k>\d)|)-(?:(?<h>\d)|)"
SUBJ_AB = [k + "-" + h for k in [""] + D for h in [""] + D]
ab = {"A": {}, "B": {}, "&A": {}, "&B": {}}
for s in SUBJ_AB:
    for nm, p in (("A", PA), ("B", PB)):
        g = groups(p, s, ["k", "h"])
        k = g["k"] if g["k"] is not None else U
        h = g["h"] if g["h"] is not None else U
        ab[nm][s] = cond(AR, [(h, k)], lambda t: S5(t[0]) and T37(t[1]), [D, D], (1,))
        ab["&" + nm][s] = cond(AR, [(h,)], lambda t: S5(t[0]), [D]) and cond(AR, [(k,)], lambda t: T37(t[0]), [D], (0,))
    check("SIB B", "(?:" + T37rx + "|)-" + S5rx, s, ab["B"][s])
count("NOT a loop: A vs B (record)", SUBJ_AB, ab["A"], ab["B"], "A", "B")
count("NOT a loop: A record vs A &", SUBJ_AB, ab["A"], ab["&A"], "rec", "&")
print("   `?` a loop: A's record is the SIBLING-LOOP COMPILE ERROR (k's loop and h's loop do not nest), decided from "
      "the text: A ERROR vs B an answer on %d of %d; A's & spelling answers (= B's on %d of %d)" %
      (len(SUBJ_AB), len(SUBJ_AB), sum(ab["&A"][s] == ab["B"][s] for s in SUBJ_AB), len(SUBJ_AB)))
print("   A list of items with two optional fields, /(?:(?<a>\\d)?-(?<b>\\d)?,)*/ & (a?: <5, b?: 3..7):")
PL2 = r"(?:(?<a>\d)?-(?<b>\d)?,)*"
L2_ITEMS = ["-", "1-", "-7", "3-6", "7-2", "-1"]
SUBJ_L2 = ["".join(i + "," for i in its) for n in range(3) for its in itertools.product(L2_ITEMS, repeat=n)]
l2 = {}
for s in SUBJ_L2:
    assert whole(PL2, s)
    its = [i.split("-") for i in s.split(",")[:-1]]
    tu = [(a if a else P, b if b else P) for a, b in its] if its else [(Z, Z)]
    l2[s] = cond(AR, tu, lambda t: S5(t[0]) and T37(t[1]), [D, D], (0, 1))
    check("L2", "(?:(?:" + S5rx + ")?-(?:" + T37rx + ")?,)*", s, l2[s])
print("      NOT a loop: answers on all %d lists (ENGINE-RUN), e.g. '3-6,' %s, '7-2,' %s, '' %s; `?` a loop: the "
      "SIBLING-LOOP ERROR on all %d" % (len(SUBJ_L2), hfx(l2["3-6,"]), hfx(l2["7-2,"]), hfx(l2[""]), len(SUBJ_L2)))

# =================================================================================================================
print("\n(ALL) ruling C: all(c) := c with every label marked, read F1")
LI_ = [list(c) for k in range(4) for c in itertools.product(D, repeat=k)]
LIk = ["".join(x + "," for x in l) for l in LI_]
F0 = lambda x: False
pl = {s: plain(AR, l, S5, D) for s, l in zip(LIk, LI_)}
mk5 = {s: plain(AR, l, S5, D, mark=True) for s, l in zip(LIk, LI_)}
al5 = {s: all_def([(x,) for x in l] or [(Z,)], lambda t: S5(t[0]), [D]) for s, l in zip(LIk, LI_)}
al0 = {s: all_def([(x,) for x in l] or [(Z,)], lambda t: F0(t[0]), [D]) for s, l in zip(LIk, LI_)}
mk0 = {s: plain(AR, l, F0, D, mark=True) for s, l in zip(LIk, LI_)}
vac0 = {s: (True if not l else plain(AR, l, F0, D)) for s, l in zip(LIk, LI_)}
for s in LIk:
    check("LI all <5", "(?:" + S5rx + ",)*", s, al5[s])
    check("LI all <0", "(?:(?!),)+", s, al0[s])          # S meets no value of the domain: ',' never accepted
count("(LI) (n: <5) vs all((n: <5))", LIk, pl, al5, "plain", "all")
count("(LI) all((n: <5)) vs (n?: <5)", LIk, al5, mk5, "all", "n?")
count("(LI) all((n: <0)) vs (n?: <0)  [the empty-set corner, corrected]", LIk, al0, mk0, "all", "n?")
count("(LI) all((n: <0)) vs the vacuous 'holds over none' absfold computed", LIk, al0, vac0, "all", "vacuous")
# L36: lane absent's spelling rows
src2 = open(os.path.join(HERE, "absent_check.py")).read()
a0 = src2.index("SP = [")
ns = {}
exec(src2[a0:src2.index("\n]\n", a0) + 3], ns)
spres = {}
for g_, pat, probe, pg, subj, k_set, k_unset, scope in ns["SP"]:
    if probe is None:
        prev = [r for r in ns["SP"] if r[1] == pat and r[2] is not None and subj.endswith(r[4]) and r[4] != subj][0]
        st = groups(prev[2], prev[4], [prev[3]])[prev[3]] is not None
    else:
        st = groups(probe, subj, [pg])[pg] is not None
    kind = k_set if st else k_unset
    k = "Z" if kind == "Z" else ("P" if scope != "match" else "U")
    x = {"Z": Z, "U": U, "P": P}[k]
    for sname, S in (("<5", S5), ("<0", F0)):
        spres.setdefault(sname, {})[(g_, pat, subj)] = all_def([(x,)], lambda t: S(t[0]), [D])
for sname in spres:
    gs = sorted({kk[0] for kk in spres[sname]})
    split = sum(len({spres[sname][kk] for kk in spres[sname] if kk[0] == g}) > 1 for g in gs)
    print("   L36: all((n: %s)) [C] over lane absent's %d spelling rows: groups of equal spellings that SPLIT: %d of %d"
          % (sname, len(spres[sname]), split, len(gs)))
# (RZ): record = & under all
for c in ("GROUP",):
    r1 = {s: all_def(RZT[s][2], REC, [D, D]) for s in SUBJ_RZ}
    r2 = {s: all_def([(h,) for h in RZT[s][1]] or [(Z,)], lambda t: S5(t[0]), [D]) and T37(RZT[s][0])
          for s in SUBJ_RZ}
    rt = {s: cond(TD, RZT[s][2], REC, [D, D]) for s in SUBJ_RZ}
    count("(RZ) all((h: <5, k: 3..7)) vs all((h: <5)) & all((k: 3..7))  [record = & under all]", SUBJ_RZ, r1, r2,
          "all(rec)", "all&all")
    count("(RZ) all(record) vs the answers before 14:31", SUBJ_RZ, rt, r1, "before", "all")
    print("   (RZ) '9': all(record) %s (k = 9 tested); '3': %s" % (hfx(r1["9"]), hfx(r1["3"])))
oa = LP[False]["all(...) [C]"]
for s in SUBJ_OP:
    check("OP all C", "(?:" + alt([str(i) for i in range(10)]) + "(?::" + alt(["%02d" % i for i in range(30)]) +
          ")?,)*", s, oa[s])
count("(OP) all((h: <10, m: <30)) vs WANTED (before 14:31)", SUBJ_OP, WANT, oa, "want", "all")
mpl = {s: plain(AR, [m for _, m in OPI[s]], lambda x: canon(x) and int(x) < 30, DM2) for s in SUBJ_OP}
mal = {s: all_def([(m if m is not None else P,) for _, m in OPI[s]] or [(Z,)], lambda t: canon(t[0]) and int(t[0]) < 30,
                  [DM2]) for s in SUBJ_OP}
withval = [s for s in SUBJ_OP if any(m is not None for _, m in OPI[s])]
count("(OP) (m: <30) vs all((m: <30)), every list", SUBJ_OP, mpl, mal, "plain", "all")
count("(OP) the same, lists where m HAS a value", withval, mpl, mal, "plain", "all")

# =================================================================================================================
print("\n(NONE) ruling E: the mark COUNTED (F1) inside occurs.*/some/count; (OP), per domain")
for c in CANDS:
    cnt = {s: not any(cond(AR, [t], NOT(HM), [DH, DOM_OPM[c]], (1,)) for t in op_tuples(s, False)) if OPI[s] else True
           for s in SUBJ_OP}
    count("occurs.none(((h, m?): !R)) mark COUNTED vs WANTED [%s]" % c, SUBJ_OP, WANT, cnt, "want", "none")
    if c == "GROUP":
        for s in SUBJ_OP:
            check("NONE", "(?:" + alt([str(i) for i in range(10)]) + ":" + alt(["%02d" % i for i in range(30)]) + ",)*",
                  s, cnt[s])
nc = {s: not any(t[1] is not P and not HM(t) for t in op_tuples(s, False)) if OPI[s] else True for s in SUBJ_OP}
count("occurs.none(((h, m?): !R)) mark NOT counted (14:31) vs WANTED", SUBJ_OP, WANT, nc, "want", "notcounted")
un = {s: not any(cond(AR, [t], NOT(HM), [DH, DM2]) for t in op_tuples(s, False)) if OPI[s] else True for s in SUBJ_OP}
count("occurs.none(((h, m): !R)) unmarked vs WANTED", SUBJ_OP, WANT, un, "want", "unmarked")
HM100 = lambda t: canon(t[0]) and int(t[0]) < 10 and num(t[1]) and int(t[1]) < 100     # m: PADDED (num)
print("   the domain decides it in general: R' = (h: <10, m: padded(<100)), occurs.none(((h, m?): !R')) on '3,': " +
      "  ".join("%s %s" % (c, hfx(not cond(AR, [("3", P)], NOT(HM100), [DH, DOM_OPM[c]], (1,)))) for c in CANDS))
g_dom = {"ANY": anyd(["x", "y"]), "GROUP": ["x", "y"], "VALUES": values(r"ab(?<g>[xy])?", "g", ["ab", "abx", "aby"],
                                                                         ["x", "y"])}
print("   4G.6 (4)'s pair, occurrences(/ab(?<g>[xy])?/) on 'ab': (g?: \"x\") / some((g?: \"x\")) with the mark counted: " +
      "  ".join("%s %s/%s" % (c, hfx(cond(AR, [(P,)], lambda t: t[0] == "x", [g_dom[c]], (0,))),
                              hfx(any(cond(AR, [(P,)], lambda t: t[0] == "x", [g_dom[c]], (0,)) for _ in [1])))
                for c in CANDS))

# =================================================================================================================
print("\n(GF) ruling K: the general form (a candidate set D per absent label), written without part()/tup(), "
      "vs the ruled engine")


def gf(tuples, Rf, doms, marks=(), defaults=None):
    defaults = defaults or {}
    for t in tuples:
        cand = []
        for i, x in enumerate(t):
            if not isinstance(x, Abs):
                cand.append([x])
            elif i in defaults:
                cand.append([defaults[i]])
            elif i in marks:
                cand.append(list(doms[i]))
            else:
                cand.append([])
        if not any(Rf(c) for c in itertools.product(*cand)):
            return False
    return True


GFN = {"cases": 0, "differ": 0}


def gfc(tag, tuples, Rf, doms, marks=(), defaults=None):
    GFN["cases"] += 1
    if gf(tuples, Rf, doms, marks, defaults) != cond(AR, tuples, Rf, doms, marks, defaults):
        GFN["differ"] += 1
        if GFN["differ"] < 8:
            print("   GF DIFFER", tag, tuples)


for c in CANDS:
    for x in ("3", Z, U, P):                                                     # (AR)
        for mk, dv in (((), {}), ((0,), {}), ((), {0: "9"}), ((), {0: "2"})):
            gfc("AR one", [(x,)], lambda t: S5(t[0]), [DOM_AR[c]], mk, dv)
            gfc("AR rec", [(x, "6")], REC, [DOM_AR[c], D], mk, dv)
            gfc("AR jnt", [(x, "6")], lambda t: canon(t[0]) and (int(t[0]), int(t[1])) >= (5, 3), [DOM_AR[c], D], mk, dv)
    for s in SUBJ_T2:                                                            # (TM2)
        for mk, dv in (((), {}), ((1,), {}), ((), {1: "0"})):
            gfc("TM2", [T2T[s]], GE930, [H, DOM_M[c]], mk, dv)
    for s in ZS:                                                                 # (ZJ)
        for name, Rf in ZJS:
            for mk in ((), (0,)):
                gfc("ZJ", RZT[s][2], Rf, [DOM_H[c], D], mk)
    for s in SUBJ_ZE:                                                            # (ZE)
        for mkf in (C1, C2):
            for mk in ((), (0,)):
                gfc("ZE", ZET[s][3], mkf(ZET[s][0]), [DOM_HE[c], D], mk)
print("   (AR) 4 kinds x 4 controls x 3 shapes, (TM2) 11,110 x 3, (ZJ) 10 x 4 sets x 2, (ZE) 11,100 x 2 x 2; each "
      "under ANY, GROUP, VALUES: %d cases, differ %d" % (GFN["cases"], GFN["differ"]))

print("\nTOTAL engine-run cases %d differ %d engine-disagreements %d probes %d" % (TOT["cases"], TOT["differ"], DIS[0],
                                                                                TOT["probes"]))
