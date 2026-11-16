# jcfix: evidence for docs/design/joint_condition.md §4F (round jointcond's fixes) and for the two owner-question
# drafts in docs/dev/lanes/jcfix_report.md. Run: `timeout 120 python3 -I docs/dev/lanes/jcfix_check.py`.
#
# Method COPIED from jcfold2_check.py (engine helpers unedited in substance): every regex verdict is computed by
# libpcre2-8 (ctypes) AND Python `re`, and the two must agree. A rule's verdict is computed in Python from the subject
# split by plain string code; where a table says ENGINE-RUN, the rule is also unfolded into a regex (its automaton
# reading) and that regex is run against the Python verdict (a differ would be printed). Other readings are COMPUTED
# in Python and COUNTED against each other: comparisons, not expectations. Every subject is first checked to be a
# whole match of the operand pattern (both engines).
#
# Tables:
# (ZE) zero-pass-empty: a joint set EMPTY only through a match value, `/(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*/` with
#      `(h: <$a, k: 3)` and `((h, k): < ($a, 0))`; four rules: the `&` reading, jcfold2's split rule, the record's
#      unsplit wording, the manager's lean (one rule, looped values drawn from their groups' strings). Then the
#      lean on the (RZ), (ZN), (ZJ) populations against the `&` reading (hand expansion for (ZJ)) and the split rule.
# (UP) unreached pairing: `/(?:(?<h>\d)(?:-(?:(?<k>\d),)*)?;)*/`, an outer pass whose optional skips the pairing
#      loop; joint candidates X (text as written), W (as a zero-pass reach), Y (unset in that pass); single-label k
#      readings W1, Y1, M0; does `(h: <5, k: <5)` = `(h: <5) & (k: <5)` survive under each.
# (OP) optional in a pass: `/(?:(?<h>\d+)(?::(?<m>\d\d))?,)*/ & (h: <10, m: <30)`, an item without minutes.
# (DM) dictionary domain (the brief's letter (DD) is taken: unsetdef's date-without-a-day table in §4B.4): EXP vs
#      DOM on the `t` population; table (O) padded and unpadded.
# Sabotage: JCFIX_SABOTAGE=1 unfolds every engine-run rule with its zero-pass / unreached piece made vacuous; the
# check must then differ.
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
SAB = os.environ.get("JCFIX_SABOTAGE") == "1"
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
    b = re.fullmatch(p.replace("(?<", "(?P<"), t) is not None    # Python spells a named group (?P<..>)
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


def in_pattern(pat, subjects):
    bad = [s for s in subjects if not whole(pat, s)]
    assert not bad, (pat, bad[:3])


def alt(strings):
    strings = sorted(set(strings), key=lambda s: (-len(s), s))
    return "(?:" + "|".join(re.escape(s) for s in strings) + ")" if strings else "(?!)"


def vac(ok):                 # the zero-pass / unreached piece of an unfold; the sabotage makes it unconditional
    return True if SAB else ok


D = list(range(10))          # the capture language of `\d`, as integers
ANYS = D + ["x"]             # "every string", represented by the digits plus one non-digit string (as jcfold2)


def num_lt(h, b):            # a comparison set over canonical numerals (§2.4): "x" is in no numeric set
    return h != "x" and h < b


# =================================================================================================================
# (ZE) zero-pass-empty
print("\n(ZE) zero-pass-empty: P := /(?<a>\\d)-(?<k>\\d)(?:;(?<h>\\d))*/, a set EMPTY only through the match value $a")
P_ZE = r"(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*"
SUBJ_ZE = []
for a in D:
    for k in D:
        for n in range(3):
            for hs in itertools.product(D, repeat=n):
                SUBJ_ZE.append("%d-%d" % (a, k) + "".join(";%d" % h for h in hs))
in_pattern(P_ZE, SUBJ_ZE)


def split_ze(s):
    head, *hs = s.split(";")
    a, k = head.split("-")
    return int(a), int(k), [int(h) for h in hs]


# the two spellings. R(a) as a predicate over (h, k); PRODUCT tells which clause the split rule uses.
CONDS = {
    "C1 (h: <$a, k: 3)": dict(R=lambda a, h, k: num_lt(h, a) and k == 3, product=True,
                             amp=lambda a, k, hs: all(h < a for h in hs) and k == 3),
    # no `&` form exists for a non-product; its hand expansion `(h: <$a) | (h: ==$a, k: <0)` as records:
    "C2 ((h, k): < ($a, 0))": dict(R=lambda a, h, k: h != "x" and (h, k) < (a, 0), product=False,
                                   amp=lambda a, k, hs: all(h < a for h in hs) or (all(h == a for h in hs) and k < 0)),
}


def possible(R, a, k, dom):
    return any(R(a, h, k) for h in dom)


RULES = {
    # the `&` reading (C1) / the hand expansion into a `|` of records (C2): COMPUTED only
    "AMP": None,
    # jcfold2's split: a product: empty satisfies each part (the other parts tested); not a product: projection,
    # "some value" over every string (jcfold2's corner 2 reading)
    # (the only product here is C1, whose outside part is `k: 3`)
    "SPLIT": lambda c, a, k: k == 3 if c["product"] else possible(c["R"], a, k, ANYS),
    # the record's wording verbatim, for ANY joint set: projection; its domain is not stated: every string
    "UNSPLIT-any": lambda c, a, k: possible(c["R"], a, k, ANYS),
    # the manager's lean: ONE rule, projection with the looped values drawn from their groups' strings (`\d`)
    "LEAN": lambda c, a, k: possible(c["R"], a, k, D),
    # RULING-2's fourth clause, for comparison: R empty (for this match, over the groups' strings): HOLDS; else LEAN
    "EMPTY-HOLDS": lambda c, a, k: (not any(c["R"](a, h, kk) for h in D for kk in D)) or possible(c["R"], a, k, D),
}
ZE_RES = {}
for cname, c in CONDS.items():
    for rname, zero in RULES.items():
        res = {}
        for s in SUBJ_ZE:
            a, k, hs = split_ze(s)
            if rname == "AMP":
                res[s] = c["amp"](a, k, hs)
            elif hs:
                res[s] = all(c["R"](a, h, k) for h in hs)
            else:
                res[s] = zero(c, a, k)
        ZE_RES[(cname, rname)] = res
        if rname != "AMP":    # ENGINE-RUN: unfold per class of (a, k): the slice of h; zero passes iff `zero`
            br = []
            for a in D:
                for k in D:
                    sl = alt([str(h) for h in D if c["R"](a, h, k)])
                    br.append("%d-%d(?:;%s)%s" % (a, k, sl, "*" if vac(zero(c, a, k)) else "+"))
            rx = "(?:" + "|".join(br) + ")"
            for s in SUBJ_ZE:
                check("ZE %s %s" % (cname, rname), rx, s, res[s])
print("(ZE) subjects %d per condition (a, k in 0..9; 0-2 passes; zero-pass subjects 100)" % len(SUBJ_ZE))
for s in ("0-3", "3-3", "0-3;0", "3-3;1"):
    print("     %-7s" % s, "; ".join("%s: %s" % (cn.split()[0], " ".join("%s=%s" % (rn, "HOLDS" if ZE_RES[(cn, rn)][s]
                                                                              else "FAILS") for rn in RULES))
                                    for cn in CONDS))
names = list(RULES)
for cname in CONDS:
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            d = [s for s in SUBJ_ZE if ZE_RES[(cname, names[i])][s] != ZE_RES[(cname, names[j])][s]]
            print("     %-24s %-11s vs %-11s differ %4d  e.g. %s" % (cname, names[i], names[j], len(d), d[:3]))
# C1 and C2 are the SAME set only when a = 0 (both EMPTY); compare the two spellings there
A0 = [s for s in SUBJ_ZE if s.startswith("0-")]
for rname in names:
    d = [s for s in A0 if ZE_RES[("C1 (h: <$a, k: 3)", rname)][s] != ZE_RES[("C2 ((h, k): < ($a, 0))", rname)][s]]
    print("     a = 0 (both spellings the EMPTY set, %d subjects): C1 vs C2 under %-11s differ %3d  e.g. %s" %
          (len(A0), rname, len(d), d[:3]))
# the CONSTANT spellings: predicates_draft.md:1941-1942 (§5.2, LEAN): an empty intersection from pure parts at a
# narrowing site is an ERROR. The intersection here: R against the labels' group strings (`\d` x `\d`).
for txt, R in (("(h: <0, k: 3)", lambda h, k: h < 0 and k == 3), ("((h, k): < (0, 0))", lambda h, k: (h, k) < (0, 0)),
               ("(h: <3, k: 3)", lambda h, k: h < 3 and k == 3)):
    empty = not any(R(h, k) for h in D for k in D)
    print("     constant %-20s R x (\\d, \\d) %s -> %s" % (txt, "EMPTY" if empty else "non-empty",
                                                         "compile ERROR (:1941, LEAN)" if empty else "compiles"))

# --- the lean on (RZ), (ZN), (ZJ) --------------------------------------------------------------------------------
print("\n(ZE-L) the lean's ONE rule on jcfold2's populations (projection, looped values from their groups' strings)")
SUBJ_RZ = [str(k) + "".join(";" + str(h) for h in hs) for k in D for n in range(3) for hs in itertools.product(D, repeat=n)]
in_pattern(r"(?<k>\d)(?:;(?<h>\d))*", SUBJ_RZ)


def split_rz(s):
    p = s.split(";")
    return int(p[0]), [int(x) for x in p[1:]]


S_set, T_set = set(range(5)), set(range(3, 8))
lean_amp = lean_m = 0
br = []
for k in D:
    sl = alt([str(h) for h in D if h in S_set and k in T_set])
    br.append("%d(?:;%s)%s" % (k, sl, "*" if vac(any(h in S_set and k in T_set for h in D)) else "+"))
rx_rz = "(?:" + "|".join(br) + ")"
for s in SUBJ_RZ:
    k, hs = split_rz(s)
    lean = all(h in S_set and k in T_set for h in hs) if hs else any(h in S_set and k in T_set for h in D)
    amp = k in T_set and all(h in S_set for h in hs)
    m = amp if not hs else all(h in S_set and k in T_set for h in hs)      # jcfold2's M: the product clause
    if not hs:
        m = k in T_set
    check("ZE-L RZ", rx_rz, s, lean)
    lean_amp += lean != amp
    lean_m += lean != m
print("(RZ) %d subjects: lean vs the & reading differ %d; lean vs jcfold2's split rule differ %d" %
      (len(SUBJ_RZ), lean_amp, lean_m))

C_set, H_set, K_set = set(range(3, 8)), set(range(5)), set(range(2, 7))
ITEMS = [(h, ks) for h in (0, 4, 5, 9) for ks in [(), (2,), (9,), (3, 6), (6, 0)]]
SUBJ_ZN = [str(c) + "".join(";%d%s" % (h, "".join(":%d" % k for k in ks)) for h, ks in its)
           for c in (0, 2, 3, 5, 7, 8) for n in range(3) for its in itertools.product(ITEMS, repeat=n)]
in_pattern(r"(?<c>\d)(?:;(?<h>\d)(?::(?<k>\d))*)*", SUBJ_ZN)


def split_zn(s):
    p = s.split(";")
    return int(p[0]), [(int(q.split(":")[0]), [int(x) for x in q.split(":")[1:]]) for q in p[1:]]


def zn_lean(c, its):
    R = lambda c_, h, k: c_ in C_set and h in H_set and k in K_set
    if not its:                                   # outer zero passes: (c, EMPTY, EMPTY): c possible for some h, k
        return any(R(c, h, k) for h in D for k in D)
    for h, ks in its:
        if not ks and not any(R(c, h, k) for k in D):
            return False
        if any(not R(c, h, k) for k in ks):
            return False
    return True


def zn_M(c, its):                                 # jcfold2's M (the product clause), as in jcfold2_check.py
    if not its:
        return c in C_set
    return all((c in C_set and h in H_set) if not ks else all(c in C_set and h in H_set and k in K_set for k in ks)
               for h, ks in its)


def zn_amp(c, its):
    return c in C_set and all(h in H_set for h, _ in its) and all(k in K_set for _, ks in its for k in ks)


rx_zn = alt([str(c) for c in D if vac(c in C_set)]) + "(?:;" + alt([str(h) for h in H_set]) + "(?::" + \
    alt([str(k) for k in K_set]) + ")*)*"
zl_amp = zl_m = 0
for s in SUBJ_ZN:
    c, its = split_zn(s)
    v = zn_lean(c, its)
    check("ZE-L ZN", rx_zn, s, v)
    zl_amp += v != zn_amp(c, its)
    zl_m += v != zn_M(c, its)
print("(ZN) %d subjects: lean vs the & reading differ %d; lean vs jcfold2's split rule differ %d" %
      (len(SUBJ_ZN), zl_amp, zl_m))

ZJ = [
    ("((h, k): >= (5, 3))", lambda h, k: h != "x" and (h, k) >= (5, 3),
     [(set(range(6, 10)), None), ({5}, set(range(3, 10)))]),
    ("((k, h): >= (5, 3))", lambda h, k: h != "x" and (k, h) >= (5, 3),
     [(None, set(range(6, 10))), (set(range(3, 10)), {5})]),
    ("((h, k): (0|1|2, 3|4) | (5, 5))", lambda h, k: (h in (0, 1, 2) and k in (3, 4)) or (h == 5 and k == 5),
     [({0, 1, 2}, {3, 4}), ({5}, {5})]),
    ("((h, k): (\"x\", 3) | (0, 5))", lambda h, k: (h == "x" and k == 3) or (h == 0 and k == 5),
     [({"x"}, {3}), ({0}, {5})]),
    ("((h, k): < (0, 3))", lambda h, k: h != "x" and (h, k) < (0, 3), [(set(), None), ({0}, {0, 1, 2})]),
]


def rows_amp(rows, k, hs):
    return any((Ks is None or k in Ks) and all(Hs is None or h in Hs for h in hs) for Hs, Ks in rows)


tot = {"z_amp": 0, "z_m": 0, "p_amp": 0, "p_m": 0, "z": 0, "p": 0}
for name, R, rows in ZJ:
    br = []
    for k in D:
        sl = alt([str(h) for h in D if R(h, k)])
        br.append("%d(?:;%s)%s" % (k, sl, "*" if vac(any(R(h, k) for h in D)) else "+"))
    rx = "(?:" + "|".join(br) + ")"
    z_amp = z_m = p_amp = p_m = 0
    for s in SUBJ_RZ:
        k, hs = split_rz(s)
        lean = all(R(h, k) for h in hs) if hs else any(R(h, k) for h in D)
        m = all(R(h, k) for h in hs) if hs else any(R(h, k) for h in ANYS)     # jcfold2's M: "every string"
        e = rows_amp(rows, k, hs)
        check("ZE-L ZJ " + name, rx, s, lean)
        if hs:
            p_amp += lean != e; p_m += lean != m
        else:
            z_amp += lean != e; z_m += lean != m
    for key, v in (("z_amp", z_amp), ("z_m", z_m), ("p_amp", p_amp), ("p_m", p_m)):
        tot[key] += v
    tot["z"] += 10; tot["p"] += len(SUBJ_RZ) - 10
    print("(ZJ) %-34s zero passes: lean vs hand expansion %d of 10, vs split %d of 10; with passes: vs hand %d, "
          "vs split %d of %d" % (name, z_amp, z_m, p_amp, p_m, len(SUBJ_RZ) - 10))
print("(ZJ) total: zero passes lean vs hand expansion %d of %d, vs split %d of %d; with passes vs hand %d of %d, "
      "vs split %d of %d" % (tot["z_amp"], tot["z"], tot["z_m"], tot["z"], tot["p_amp"], tot["p"], tot["p_m"], tot["p"]))

# =================================================================================================================
# (UP) unreached pairing
print("\n(UP) P := /(?:(?<h>\\d)(?:-(?:(?<k>\\d),)*)?;)*/: an outer pass may skip the optional, so k's loop (the "
      "pairing loop) is never reached in that pass")
P_UP = r"(?:(?<h>\d)(?:-(?:(?<k>\d),)*)?;)*"
UP_ITEMS = [(h, ks) for h in (3, 4, 9) for ks in [None, (), (2,), (7,), (2, 7)]]
SUBJ_UP = ["".join("%d%s;" % (h, "" if ks is None else "-" + "".join("%d," % k for k in ks)) for h, ks in its)
           for n in range(3) for its in itertools.product(UP_ITEMS, repeat=n)]
in_pattern(P_UP, SUBJ_UP)


def split_up(s):
    out = []
    for it in s.split(";")[:-1]:
        if "-" in it:
            h, rest = it.split("-")
            out.append((int(h), [int(x) for x in rest.split(",") if x]))
        else:
            out.append((int(it), None))
    return out


def up_joint(its, reading, R, poss):
    """the record/joint condition per pass of the pairing loop (k's loop); R over (h, k); poss(h): h possible"""
    if not its:
        return True                                   # outer zero passes: (EMPTY, EMPTY)
    never = all(ks is None for _, ks in its)          # k's loop reached in NO pass: k unset in the match (§4.2)
    for h, ks in its:
        if ks is None:
            if reading == "X":                        # J7 as written: no reach, no pass, no tuple; J6 only per match
                if never:
                    return False
                continue
            if reading == "Y":                        # k unset in that pass: J6 fails it
                return False
            if reading in ("W", "W'"):                # as a zero-pass reach: (h, EMPTY); h must be possible
                if reading == "W'" and never:         # W': k's loop reached in NO pass: k unset in the match (§4.2), J6
                    return False
                if not poss(h):
                    return False
                continue
        if not ks and not poss(h):                    # reached, zero passes: (h, EMPTY) (J7, CF 12:45)
            return False
        if any(not R(h, k) for k in ks):
            return False
    return True


def up_single_k(its, reading, Tk):
    ks_all = [k for _, ks in its if ks for k in ks]
    if reading == "W1":       # a pass that does not reach k's loop gives k zero iterations in it
        return all(Tk(k) for k in ks_all)
    if reading == "Y1":       # k unset in that pass: (k: T) fails (every outer pass must have k)
        return all(ks is not None for _, ks in its) and all(Tk(k) for k in ks_all)
    if reading == "M0":       # §4.2 per MATCH: unset only if no pass reached k's loop; else k's iterations
        if its and all(ks is None for _, ks in its):
            return False
        return all(Tk(k) for k in ks_all)


S5 = lambda x: x < 5
UPR = {}
for r in ("X", "W", "W'", "Y"):
    UPR[r] = {s: up_joint(split_up(s), r, lambda h, k: S5(h) and S5(k), lambda h: S5(h) and any(S5(k) for k in D))
              for s in SUBJ_UP}
for r in ("W1", "Y1", "M0"):
    UPR["&" + r] = {s: all(S5(h) for h, _ in split_up(s)) and up_single_k(split_up(s), r, S5) for s in SUBJ_UP}
# ENGINE-RUN: W and Y unfold to regexes (product (<5, <5)); W: the optional's skip allowed when h is possible
S5rx = alt([str(x) for x in D if S5(x)])
rx_W = "(?:" + S5rx + "(?:-(?:" + S5rx + ",)*)?;)*"
rx_Y = "(?:" + S5rx + "-(?:" + S5rx + ",)*;)*" if not SAB else rx_W
for s in SUBJ_UP:
    check("UP W", rx_W, s, UPR["W"][s])
    check("UP Y", rx_Y, s, UPR["Y"][s])
print("(UP) %d subjects (0-2 outer passes; h in 3, 4, 9; k's optional skipped, empty, or 1-2 values); W and Y "
      "engine-run, X, W' and the & readings computed" % len(SUBJ_UP))
keys = list(UPR)
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        d = [s for s in SUBJ_UP if UPR[keys[i]][s] != UPR[keys[j]][s]]
        print("     %-4s vs %-4s differ %3d  e.g. %s" % (keys[i], keys[j], len(d), d[:3]))
for s in ("3-2,;9;", "3-2,;4;", "3-2,;3;", "3-;9;", "9;", "3;", ""):
    print("     %-9r" % s, " ".join("%s=%s" % (k, "HOLDS" if UPR[k][s] else "FAILS") for k in keys))
# the same corner on a NON-product set, ((h, k): >= (5, 3)): W tests h's possibility, Y fails the pass
R53 = lambda h, k: (h, k) >= (5, 3)
for s in ("3-2,;9;", "3-2,;4;", "9-;9;", "9-5,;9;", "9-5,;4;"):
    its = split_up(s)
    print("     ((h, k): >= (5, 3)) on %-9r" % s, " ".join(
        "%s=%s" % (r, "HOLDS" if up_joint(its, r, R53, lambda h: any(R53(h, k) for k in D)) else "FAILS")
        for r in ("X", "W", "W'", "Y")))

# =================================================================================================================
# (OP) optional label inside a pass
print("\n(OP) P := /(?:(?<h>\\d+)(?::(?<m>\\d\\d))?,)*/ & (h: <10, m: <30); an item may have no minutes")
P_OP = r"(?:(?<h>\d+)(?::(?<m>\d\d))?,)*"
OP_ITEMS = [(h, m) for h in ("3", "12") for m in (None, "15", "45")]
SUBJ_OP = ["".join("%s%s," % (h, "" if m is None else ":" + m) for h, m in its)
           for n in range(4) for its in itertools.product(OP_ITEMS, repeat=n)]
in_pattern(P_OP, SUBJ_OP)
canon = lambda x: re.fullmatch(r"0|[1-9][0-9]*", x) is not None
Sh = lambda x: canon(x) and int(x) < 10
Tm = lambda x: canon(x) and int(x) < 30


def split_op(s):
    return [(it.split(":")[0], it.split(":")[1] if ":" in it else None) for it in s.split(",")[:-1]]


def op_rec(its):          # J9 + J6 per pass (J7): a pass whose m is unset has no tuple: FAILS (no default)
    return all(m is not None and Sh(h) and Tm(m) for h, m in its)


def op_ampA(its):         # (h: S) & (m: T), m's iterations = the passes; a pass without m: m unset in it, fails
    return all(Sh(h) for h, _ in its) and all(m is not None and Tm(m) for _, m in its)


def op_ampB(its):         # (h: S) & (m: T), m's iterations = the values m took; unset only if never set (§4.2)
    ms = [m for _, m in its if m is not None]
    if its and not ms:
        return False
    return all(Sh(h) for h, _ in its) and all(Tm(m) for m in ms)


H10 = alt([str(i) for i in range(10)])
M30 = alt([str(i) for i in range(10, 30)])
rx_rec = "(?:" + H10 + ":" + M30 + ",)*" if not SAB else "(?:" + H10 + "(?::" + M30 + ")?,)*"
OPR = {"REC": {}, "&A": {}, "&B": {}}
for s in SUBJ_OP:
    its = split_op(s)
    OPR["REC"][s], OPR["&A"][s], OPR["&B"][s] = op_rec(its), op_ampA(its), op_ampB(its)
    check("OP REC", rx_rec, s, OPR["REC"][s])
print("(OP) %d subjects (0-3 items; h 3 or 12; minutes absent, 15 or 45); REC engine-run, the & readings computed"
      % len(SUBJ_OP))
for a_, b_ in (("REC", "&A"), ("REC", "&B"), ("&A", "&B")):
    d = [s for s in SUBJ_OP if OPR[a_][s] != OPR[b_][s]]
    print("     %-3s vs %-3s differ %3d  e.g. %s" % (a_, b_, len(d), sorted(d, key=len)[:3]))
for s in ("3,", "3:15,", "3:15,3,", "3,3:15,", "12:15,3,"):
    print("     %-10r" % s, " ".join("%s=%s" % (k, "HOLDS" if OPR[k][s] else "FAILS") for k in OPR))

# =================================================================================================================
# (DM) dictionary domain
print("\n(DM) dictionary domain on t := /(?<h>\\d{1,2}):(?<m>\\d\\d)/, 11,000 subjects")
H_T = [str(i) for i in range(10)] + ["%02d" % i for i in range(100)]
SUBJ_T = ["%s:%02d" % (h, m) for h in H_T for m in range(100)]
in_pattern(r"(?<h>\d{1,2}):(?<m>\d\d)", SUBJ_T[::97])


def val(x, pad):
    if pad and re.fullmatch(r"\d+", x):
        x = re.sub(r"\A0+(?=.)", "", x)
    return int(x) if canon(x) else None


def dict_has(op, bs, t, reading, pad):
    vs = [val(x, pad) for x in t]
    if reading == "DOM" and any(v is None for v in vs):
        return False
    for j, b in enumerate(bs):
        v = vs[j]
        if v is None:
            return False
        if v == b:
            if j == len(bs) - 1:
                return op in ("<=", ">=", "==")
            continue
        return op in ((">", ">=") if v > b else ("<", "<="))


def part_has(ops_bs, t, pad):
    return all(v is not None and {"<": v < b, "<=": v <= b, ">": v > b, ">=": v >= b}[op]
               for (op, b), v in zip(ops_bs, [val(x, pad) for x in t]))


for op, bs in ((">=", (9, 0)), (">", (9, 30))):
    for pad in (False, True):
        acc = {}
        for rd in ("EXP", "DOM"):
            acc[rd] = {s for s in SUBJ_T if dict_has(op, bs, s.split(":"), rd, pad)}
            # ENGINE-RUN: the set unfolded as a `|` of rows over the subject's text, one alternation per component
            hs = {s.split(":")[0] for s in SUBJ_T}
            ms = ["%02d" % i for i in range(100)]
            rows = []
            for h in sorted(hs):
                okm = [m for m in ms if dict_has(op, bs, (h, m), rd, pad)]
                if okm:
                    rows.append(re.escape(h) + ":" + alt(okm))
            rx = "(?:" + "|".join(rows) + ")"
            for s in SUBJ_T:
                check("DM %s %s" % (op, rd), rx, s, s in acc[rd])
        d = acc["EXP"] ^ acc["DOM"]
        print("     %-11s %s: EXP %d, DOM %d, differ %d  e.g. %s" % ("%s %s" % (op, bs), "padded  " if pad else
                                                                    "unpadded", len(acc["EXP"]), len(acc["DOM"]),
                                                                    len(d), sorted(d)[:3]))
for pad in (False, True):
    for rd in ("EXP", "DOM"):
        n = sum(1 for s in SUBJ_T if dict_has(">=", (9, 30), s.split(":"), rd, pad) !=
                part_has(((">=", 9), (">=", 30)), s.split(":"), pad))
        w = "10:00"
        print("     (O) %s %s: >= (9, 30) vs (>= 9, >= 30) differ %d of %d; '10:00' in the first: %s" %
              ("padded  " if pad else "unpadded", rd, n, len(SUBJ_T), dict_has(">=", (9, 30), w.split(":"), rd, pad)))
for rd in ("EXP", "DOM"):
    sl = [h for h in H_T if dict_has(">=", (9, 0), (h, "00"), rd, False)]
    print("     ((h, m = 00): >= (9, 0)) %s: the slice at m = '00' holds %d h texts -> %s" %
          (rd, len(sl), "default.unused (b) fires (slice EMPTY)" if not sl else "no warning"))

# the look-alike round jointcond found unlisted (CENSUS-4): a union of tuples vs a tuple of unions, both padded;
# COMPUTED (integer pairs from the subject's text), not engine-run
U = {(9, 0), (10, 30)}
in_u = lambda s: tuple(val(x, True) for x in s.split(":")) in U
in_p = lambda s: val(s.split(":")[0], True) in (9, 10) and val(s.split(":")[1], True) in (0, 30)
for name, f in (("padded([(9, 0), (10, 30)])", in_u), ("(padded(9 | 10), padded(0 | 30))", in_p)):
    acc = [s for s in SUBJ_T if f(s)]
    print("     look-alike %-34s admits %d of %d: %s" % (name, len(acc), len(SUBJ_T), acc))
d = [s for s in SUBJ_T if in_u(s) != in_p(s)]
print("     look-alike union of tuples vs tuple of unions: differ %d  %s" % (len(d), d))

print("\nTOTAL cases %d differ %d engine-disagreements %d" % (T["cases"], T["differ"], DISAGREE[0]))
