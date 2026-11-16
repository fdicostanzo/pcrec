# absfold: evidence for docs/design/joint_condition.md §4G and docs/dev/lanes/absfold_report.md.
# The owner's absent-label rule, RULED 2026-11-16 14:31 ("absent-rule: lock", COND-FAMILY's last entry):
#   (1) ONE kind of absence; (2) a condition needs a text: on an absent label it FAILS, empty lists included;
#   (3) two controls ON THE LABEL, each over every absence: the optional mark `h?` (placeholder spelling, D193 add. 4;
#       "the condition is satisfied"; in a joint condition "some value would put the tuple in the set") and the
#       default `h = v` (v read, the empty list included); NOT BOTH (a compile error); (4) a set never contains absence.
# The rule is absimpact_check.py's R (R-INTENT); its machinery is REUSED (exec'd: the engines, groups(), check(),
# alt(), part(), tup(), plain()), not re-implemented. Every table the note still quotes is re-run here under the
# ruled rule (AR), beside today's line (T, the pre-ruling line as absimpact computed it) where a move is counted.
#
# Run (worktree root): `timeout 120 python3 -I docs/dev/lanes/absfold_check.py`.
# Sabotage: `ABSFOLD_SABOTAGE=1 ...` flips AR's zero-pass entry back to today's (part("R", "Z") -> PROJ); the
# engine-run unfolds, built from the rule stated over sets (never from part()), must then differ.
#
# KINDS OF RESULT (as absimpact): RUN = the subject is a whole match of its pattern in libpcre2-8 AND Python `re`;
# COMPUTED = the answer from part()/tup() on the subject split by string code; ENGINE-RUN = AR's answer also built as
# a regex from the rule stated over sets and run against the computed answer (both engines); OLD-OUT = a computed
# column compared with the value the earlier lane's committed .out printed (an independent program's output).
import os, re, itertools, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "absimpact_check.py")).read()
exec(_src[:_src.index('print("\\n(RT)')], globals())       # absimpact's setup + rule table functions, verbatim
SAB = os.environ.get("ABSFOLD_SABOTAGE") == "1"            # part() reads this global
if SAB:
    print("SABOTAGE ON (ABSFOLD_SABOTAGE=1): AR's zero-pass entry flipped back to today's")
AR, TD = "R", "T"
NOTES = []


class Abs:
    """an absent part of a tuple; kind Z (zero passes), U (never reached), P (missing in a pass)"""
    def __init__(self, k):
        self.k = k

    def __repr__(self):
        return "<%s>" % self.k


Z, U, P = Abs("Z"), Abs("U"), Abs("P")


class NotBoth(Exception):
    pass


def resolve(rule, x, i, marks, defaults):
    if isinstance(x, Abs):
        if i in marks and i in defaults:
            raise NotBoth("label %d: marked optional AND given a default" % i)
        return part(rule, x.k, i in marks, defaults.get(i))
    return x


def cond(rule, tuples, Rf, doms, marks=(), defaults=None):
    """the condition per pass: every tuple must be in R (J7); an absent part per part() (projection = F1)"""
    defaults = defaults or {}
    for t in tuples:
        if not tup(Rf, [resolve(rule, x, i, marks, defaults) for i, x in enumerate(t)], doms):
            return False
    return True


def rec_f2(tuples, preds, doms, marks=()):
    """a PRODUCT under AR with the mark read F2 ('absence is acceptable, the condition is satisfied' outright):
    a marked absent part is satisfied; every other part is tested (unmarked absent: fails)"""
    for t in tuples:
        for i, (x, p) in enumerate(zip(t, preds)):
            if isinstance(x, Abs):
                if i in marks:
                    continue
                return False
            if not p(x):
                return False
    return True


num = lambda x: x.isdigit()
S5 = lambda x: canon(x) and int(x) < 5
T37 = lambda x: canon(x) and 3 <= int(x) <= 7
hfx = lambda b: "HOLDS" if b else "FAILS"
S5rx = alt([d for d in D if S5(d)])
T37rx = alt([d for d in D if T37(d)])


def count(name, subjects, a, b, la="A", lb="B"):
    d = [s for s in subjects if a[s] != b[s]]
    ex = min(d, key=lambda s: (len(s), s)) if d else None
    print("   %-66s differ %5d of %6d%s" % (name, len(d), len(subjects),
                                            "" if ex is None else "   smallest %r (%s %s, %s %s)" %
                                            (ex, la, hfx(a[ex]), lb, hfx(b[ex]))))
    return len(d)


def old_out(fname):
    return open(os.path.join(HERE, fname)).read()


# =================================================================================================================
print("\n(AR) THE RULE TABLE: absence x what the author wrote x condition shape -> answer (COMPUTED from part())")
print("    one label (h: <5); record (h: <5, k: 3..7) with k = 6; joint ((h, k): >= (5, 3)) with k = 6; h's group \\d")
print("    v = 9 (outside <5) and v = 2 (inside); a present h is `3`")
REC = lambda t: S5(t[0]) and T37(t[1])
JNT = lambda t: canon(t[0]) and canon(t[1]) and (int(t[0]), int(t[1])) >= (5, 3)
for kind, x in (("a value (h = 3)", "3"), ("Z zero passes", Z), ("U never reached", U), ("P missing in a pass", P)):
    for wname, mk, dv in (("nothing", (), {}), ("h?", (0,), {}), ("h = 9", (), {0: "9"}), ("h = 2", (), {0: "2"}),
                          ("h? = 9", (0,), {0: "9"})):
        row = []
        for shape, t, Rf in (("one", (x,), lambda t: S5(t[0])), ("record", (x, "6"), REC), ("joint", (x, "6"), JNT)):
            if mk and dv:                       # NOT BOTH: a compile error, whatever the match
                row.append("ERROR")
                continue
            row.append(hfx(cond(AR, [t], Rf, [D, D][:len(t)], mk, dv)))
        today = []
        for shape, t, Rf in (("one", (x,), lambda t: S5(t[0])), ("record", (x, "6"), REC), ("joint", (x, "6"), JNT)):
            if mk:
                today.append("-")
            else:
                today.append(hfx(cond(TD, [t], Rf, [D, D][:len(t)], (), dv)))
        print("   %-20s %-8s AR: one %-6s record %-6s joint %-6s | today: one %-6s record %-6s joint %s" %
              (kind, wname, row[0], row[1], row[2], today[0], today[1], today[2]))

# NOT BOTH: the compile error
try:
    cond(AR, [(U,)], lambda t: S5(t[0]), [D], (0,), {0: "0"})
    print("   NOT BOTH: NOT REFUSED (unexpected)")
except (NotBoth, ValueError):
    print("   NOT BOTH: `(m? = 0: S)` refused on every absence kind and on a present label alike (a compile error, "
          "decided from the text, not the match)")
    for x in ("3", Z, U, P):
        try:
            # a present label: the error is still a COMPILE error; the evaluator only meets it on absence, so check
            # the declaration itself
            if not isinstance(x, Abs):
                raise NotBoth("declared")
            cond(AR, [(x,)], lambda t: S5(t[0]), [D], (0,), {0: "0"})
        except (NotBoth, ValueError):
            pass
        else:
            print("   NOT BOTH: kind %r not refused" % x)

# =================================================================================================================
print("\n(TM2) THE TIME EXAMPLE: t2 := /(?<h>\\d{1,2})(?::(?<m>\\d\\d))?/ & ((h, m ...): padded(>= (9, 30)))")
H = [str(i) for i in range(10)] + ["%02d" % i for i in range(100)]
M = ["%02d" % i for i in range(100)]
P_T2 = r"(?<h>\d{1,2})(?::(?<m>\d\d))?"
GE930 = lambda t: num(t[0]) and num(t[1]) and (int(t[0]), int(t[1])) >= (9, 30)


def t2_tuple(s):
    g = groups(P_T2, s, ["h", "m"])
    assert g is not None
    return (g["h"], g["m"] if g["m"] is not None else U)


W_T2 = {"nothing": ((), {}), "m?": ((1,), {}), "m = 0": ((), {1: "0"}), "m? = 0": ((1,), {1: "0"})}
print("   subject  " + "  ".join("%-8s" % w for w in W_T2) + "  today(nothing)  today(m = 0)")
for s in ("9", "10", "11", "9:15", "9:45"):
    t = t2_tuple(s)
    out = []
    for w, (mk, dv) in W_T2.items():
        out.append("ERROR" if (mk and dv) else hfx(cond(AR, [t], GE930, [H, M], mk, dv)))
    print("   %-8s " % s + "  ".join("%-8s" % o for o in out) + "  %-14s  %s" %
          (hfx(cond(TD, [t], GE930, [H, M])), hfx(cond(TD, [t], GE930, [H, M], (), {1: "0"}))))
# ENGINE-RUN over the whole t2 population: rows of >= (9, 30) over (H, M); the mark adds h's PROJECTION, the default
# the SLICE at m = "0" (both written from the set, not from part())
SUBJ_T2 = H + [h + ":" + m for h in H for m in M]
rows = alt([h for h in H if int(h) > 9]) + ":\\d\\d|" + alt([h for h in H if int(h) == 9]) + ":" + \
    alt([m for m in M if int(m) >= 30])
rx_nothing = "(?:" + rows + ")"
rx_mark = "(?:" + rows + "|" + alt([h for h in H if int(h) >= 9]) + ")"         # some m in \d\d puts (h, m) >= (9,30)
rx_def0 = "(?:" + rows + "|" + alt([h for h in H if int(h) > 9]) + ")"          # (h, 0) >= (9, 30)
TM2 = {}
for s in SUBJ_T2:
    t = (s.split(":")[0], s.split(":")[1]) if ":" in s else (s, U)
    TM2[s] = {w: cond(AR, [t], GE930, [H, M], *W_T2[w]) for w in ("nothing", "m?", "m = 0")}
    check("TM2 nothing", rx_nothing, s, TM2[s]["nothing"])
    check("TM2 m?", rx_mark, s, TM2[s]["m?"])
    check("TM2 m = 0", rx_def0, s, TM2[s]["m = 0"])
print("   ENGINE-RUN over %d t2 subjects (nothing, m?, m = 0)" % len(SUBJ_T2))
for a_, b_ in (("nothing", "m?"), ("nothing", "m = 0"), ("m?", "m = 0")):
    count("t2: %s vs %s" % (a_, b_), SUBJ_T2, {s: TM2[s][a_] for s in SUBJ_T2}, {s: TM2[s][b_] for s in SUBJ_T2},
          a_, b_)

print("\n(TM2-L) the same in a LIST: /(?:(?<h>\\d{1,2})(?::(?<m>\\d\\d))?,)*/ & ... (both labels looped)")
P_TL = r"(?:(?<h>\d{1,2})(?::(?<m>\d\d))?,)*"
SUBJ_TL = ["".join(c + "," for c in its) for n in range(3) for its in
           itertools.product(["9", "10", "9:15", "9:45"], repeat=n)]


def tl_tuples(s):
    assert whole(P_TL, s)
    its = s.split(",")[:-1]
    if not its:
        return [(Z, Z)], True
    return [(i.split(":")[0], i.split(":")[1]) if ":" in i else (i.split(":")[0], P) for i in its], False


def a2(mode, tuples, zero, Rf, doms, marks=(), defaults=None):
    """all(c) under the three readings of the manager's 'all(...) over no values HOLDS':
    A2v: no PASS of the pairing loop -> HOLDS outright, otherwise c;  A2z: c with every Z absence projected (= today);
    A2m: c with EVERY label marked (any absence projected; 'possibly none' per label)"""
    if mode == "A2v":
        return True if zero else cond(AR, tuples, Rf, doms, marks, defaults)
    if mode == "A2z":
        if SAB:
            return cond(AR, tuples, Rf, doms, marks, defaults)
        return cond(TD, tuples, Rf, doms, (), defaults) if not marks else cond(AR, tuples, Rf, doms, marks, defaults)
    if mode == "A2m":
        allm = tuple(range(len(tuples[0])))
        return cond(AR, tuples, Rf, doms, tuple(i for i in allm if i not in (defaults or {})), defaults)


TL_FORMS = {
    "((h, m): R)": lambda tu, z: cond(AR, tu, GE930, [H, M]),
    "((h, m?): R)": lambda tu, z: cond(AR, tu, GE930, [H, M], (1,)),
    "((h, m = 0): R)": lambda tu, z: cond(AR, tu, GE930, [H, M], (), {1: "0"}),
    "((h?, m = 0): R)": lambda tu, z: cond(AR, tu, GE930, [H, M], (0,), {1: "0"}),
    "((h?, m?): R)": lambda tu, z: cond(AR, tu, GE930, [H, M], (0, 1)),
    "all(((h, m): R)) A2v": lambda tu, z: a2("A2v", tu, z, GE930, [H, M]),
    "all(((h, m): R)) A2m": lambda tu, z: a2("A2m", tu, z, GE930, [H, M]),
    "today ((h, m): R)": lambda tu, z: cond(TD, tu, GE930, [H, M]),
}
TL = {f: {} for f in TL_FORMS}
for s in SUBJ_TL:
    tu, z = tl_tuples(s)
    for f, fn in TL_FORMS.items():
        TL[f][s] = fn(tu, z)
print("   %-22s" % "form" + "".join("%-10r" % s for s in ("", "10,", "9,", "9:45,", "10,9:15,")))
for f in TL_FORMS:
    print("   %-22s" % f + "".join("%-10s" % hfx(TL[f][s]) for s in ("", "10,", "9,", "9:45,", "10,9:15,")))
# ENGINE-RUN: AR's ((h, m): R) = (row,)+ ; ((h?, m = 0): R) = (row | slice-at-0,)*
for s in SUBJ_TL:
    check("TL nothing", "(?:(?:" + rows + "),)+", s, TL["((h, m): R)"][s])
    check("TL h?,m=0", "(?:(?:" + rows + "|" + alt([h for h in H if int(h) > 9]) + "),)*", s,
          TL["((h?, m = 0): R)"][s])
print("   %d lists (0-2 items) RUN; two forms ENGINE-RUN" % len(SUBJ_TL))

# =================================================================================================================
print("\n(U) jointexp's optional seconds, /(?<h>\\d{1,2}):(?<m>\\d\\d)(?::(?<s>\\d\\d))?/ & ((h, m, s): padded(>= (9, 0, 30)))")
P_U = r"(?<h>\d{1,2}):(?<m>\d\d)(?::(?<s>\d\d))?"
GE9030 = lambda t: all(num(x) for x in t) and tuple(int(x) for x in t) >= (9, 0, 30)
old = old_out("jointexp_check.out")
u_ctl = 0
for s in ["9:00", "9:00:29", "9:00:30", "10:00", "10:00:00", "8:59:59", "9:01"]:
    g = groups(P_U, s, ["h", "m", "s"])
    t = (g["h"], g["m"], g["s"] if g["s"] is not None else U)
    r = [cond(AR, [t], GE9030, [H, M, M]), cond(AR, [t], GE9030, [H, M, M], (2,)),
         cond(AR, [t], GE9030, [H, M, M], (), {2: "0"}), cond(TD, [t], GE9030, [H, M, M])]
    o = re.search(r"\n\s+%s\s+joint=(\w+)" % re.escape(s), old).group(1) == "True"
    u_ctl += o != r[0]
    print("   %-9s AR nothing %s  s? %s  s = 0 %s  | today %s  | jointexp's .out %s" %
          (s, hfx(r[0]), hfx(r[1]), hfx(r[2]), hfx(r[3]), hfx(o)))
print("   OLD-OUT control: AR nothing vs jointexp's printed joint column differ %d of 7 (set-once: no move)" % u_ctl)

print("\n(S) jointexp's strict compare, minutes optional: t2 & ((h, m ...): > (9, 30))")
GT930 = lambda t: num(t[0]) and num(t[1]) and (int(t[0]), int(t[1])) > (9, 30)
blk = old[old.index("(S) strict"):]
s_ctl = 0
for s in ["9", "10", "8", "9:31", "9:30", "10:00"]:
    t = t2_tuple(s)
    r = [cond(AR, [t], GT930, [H, M]), cond(AR, [t], GT930, [H, M], (1,)), cond(AR, [t], GT930, [H, M], (), {1: "0"})]
    o = re.search(r"\n\s+%s\s+(\w+)" % re.escape(s), blk).group(1) == "True"
    s_ctl += o != r[0]
    print("   %-6s AR nothing %s  m? %s  m = 0 %s  | jointexp's .out joint %s" % (s, hfx(r[0]), hfx(r[1]), hfx(r[2]),
                                                                              hfx(o)))
print("   OLD-OUT control: AR nothing vs jointexp's printed joint column differ %d of 6" % s_ctl)

# =================================================================================================================
print("\n(RZ) /(?<k>\\d)(?:;(?<h>\\d))*/ & (h: <5, k: 3..7): k outside h's loop")
P_RZ = r"(?<k>\d)(?:;(?<h>\d))*"
SUBJ_RZ = [k + "".join(";" + h for h in hs) for k in D for n in range(3) for hs in itertools.product(D, repeat=n)]
RZ = {}
for s in SUBJ_RZ:
    assert whole(P_RZ, s)
    parts = s.split(";")
    k, hs = parts[0], parts[1:]
    tu = [(h, k) for h in hs] if hs else [(Z, k)]
    zero = not hs
    RZ[s] = {
        "AR": cond(AR, tu, REC, [D, D]),
        "today": cond(TD, tu, REC, [D, D]),
        "AR &": plain(AR, hs, S5, D) and T37(k),
        "AR h?": cond(AR, tu, REC, [D, D], (0,)),
        "AR h? &": plain(AR, hs, S5, D, mark=True) and T37(k),
        "AR h = 9": cond(AR, tu, REC, [D, D], (), {0: "9"}),
        "AR h = 9 &": plain(AR, hs, S5, D, default="9") and T37(k),
        "AR h = 0": cond(AR, tu, REC, [D, D], (), {0: "0"}),
        "all A2v": a2("A2v", tu, zero, REC, [D, D]),
        "all A2z": a2("A2z", tu, zero, REC, [D, D]),
        "all A2m": a2("A2m", tu, zero, REC, [D, D]),
        "all(h) & all(k) A2v": (True if zero else plain(AR, hs, S5, D)) and T37(k),
        "(h: <5) single": plain(AR, hs, S5, D),
        "(h: <5) single today": plain(TD, hs, S5, D),
    }
    check("RZ AR", T37rx + "(?:;" + S5rx + ")+", s, RZ[s]["AR"])
    check("RZ AR h?", T37rx + "(?:;" + S5rx + ")*", s, RZ[s]["AR h?"])
    check("RZ AR h=9", T37rx + "(?:;" + S5rx + ")+", s, RZ[s]["AR h = 9"])
    check("Z1 AR (h: <5)", "\\d(?:;" + S5rx + ")+", s, RZ[s]["(h: <5) single"])
V = lambda key: {s: RZ[s][key] for s in SUBJ_RZ}
count("AR vs today (the zero-pass subjects with k in 3..7)", SUBJ_RZ, V("today"), V("AR"), "today", "AR")
count("AR record vs AR (h: <5) & (k: 3..7)  [record = &]", SUBJ_RZ, V("AR"), V("AR &"), "record", "&")
count("AR (h?: <5, k: 3..7) vs today", SUBJ_RZ, V("today"), V("AR h?"), "today", "h?")
count("AR (h?: <5, k: ..) vs (h?: <5) & (k: ..)  [record = &, marked]", SUBJ_RZ, V("AR h?"), V("AR h? &"), "rec", "&")
count("AR (h = 9: <5, k: ..) vs today's (ZD a) (default unread on zero)", SUBJ_RZ, V("today"), V("AR h = 9"),
      "today", "AR")
count("AR (h = 9: <5, k: ..) vs (h = 9: <5) & (k: ..)", SUBJ_RZ, V("AR h = 9"), V("AR h = 9 &"), "rec", "&")
count("AR (h = 0: <5, k: ..) vs today", SUBJ_RZ, V("today"), V("AR h = 0"), "today", "h=0")
count("all(record) A2v vs today", SUBJ_RZ, V("today"), V("all A2v"), "today", "A2v")
count("all(record) A2v vs all((h: <5)) & all((k: 3..7)) A2v  [record = & under all]", SUBJ_RZ, V("all A2v"),
      V("all(h) & all(k) A2v"), "all(rec)", "all&all")
count("all(record) A2z vs today", SUBJ_RZ, V("today"), V("all A2z"), "today", "A2z")
count("all(record) A2m vs today", SUBJ_RZ, V("today"), V("all A2m"), "today", "A2m")
print("   '9': AR %s, today %s, h? %s, all A2v %s, all A2z %s, all A2m %s" % tuple(
    hfx(RZ["9"][k]) for k in ("AR", "today", "AR h?", "all A2v", "all A2z", "all A2m")))
print("\n(Z1) single label on the same population: (h: <5)")
count("AR (h: <5) vs today (zero passes now FAIL)", SUBJ_RZ, V("(h: <5) single today"), V("(h: <5) single"),
      "today", "AR")
for p_, rx_, cases in ((r"(?:(?<n>\d),)*", "(?:" + S5rx + ",)+", [("", False), ("3,", True), ("7,", False),
                                                                    ("3,7,", False)]),
                       (r"x|(?<n>\d)+", "(?:" + S5rx + ")+", [("x", False), ("3", True), ("37", False)])):
    res = []
    for s, _ in cases:
        g = groups(p_, s, ["n"])
        ns = [] if g["n"] is None else (list(s.replace(",", "")) if "," in s or s.isdigit() else [])
        kind = "Z" if p_.startswith("(?:") else "U"
        want = plain(AR, ns, S5, D, zkind=kind)
        check("Z1 " + p_, rx_, s, want)
        res.append("%r %s" % (s, hfx(want)))
    print("   /%s/ & (n: <5): %s" % (p_, ", ".join(res)))

# =================================================================================================================
print("\n(ZN) nested: /(?<c>\\d)(?:;(?<h>\\d)(?::(?<k>\\d))*)*/ & (c: 3..7, h: 0..4, k: 2..6)")
P_ZN = r"(?<c>\d)(?:;(?<h>\d)(?::(?<k>\d))*)*"
Cs, Hs_, Ks = (lambda x: 3 <= int(x) <= 7), (lambda x: int(x) <= 4), (lambda x: 2 <= int(x) <= 6)
ITEMS = [(h, ks) for h in "0459" for ks in [(), ("2",), ("9",), ("3", "6"), ("6", "0")]]
SUBJ_ZN = [c + "".join(";%s%s" % (h, "".join(":" + k for k in ks)) for h, ks in its)
           for c in "023578" for n in range(3) for its in itertools.product(ITEMS, repeat=n)]
PZN = lambda t: Cs(t[0]) and Hs_(t[1]) and Ks(t[2])
ZNR = {}
for s in SUBJ_ZN:
    assert whole(P_ZN, s)
    c, *its = s.split(";")
    its = [(i.split(":")[0], i.split(":")[1:]) for i in its]
    tu = [(c, Z, Z)] if not its else [t for h, ks in its for t in ([(c, h, Z)] if not ks else [(c, h, k) for k in ks])]
    k_reach = [ks for _, ks in its]
    ZNR[s] = {
        "AR": cond(AR, tu, PZN, [D, D, D]),
        "today": cond(TD, tu, PZN, [D, D, D]),
        # & with each single-label condition per pass of ITS pairing loop; k per REACH (a reach with no k = absent)
        "& reach": Cs(c) and plain(AR, [h for h, _ in its], Hs_, D) and
                   (bool(its) and all(plain(AR, ks, Ks, D) for ks in k_reach)),
        # & with k's values pooled over the match (at least one; per-match single-label reading)
        "& pooled": Cs(c) and plain(AR, [h for h, _ in its], Hs_, D) and
                    plain(AR, [k for ks in k_reach for k in ks], Ks, D),
    }
    Crx, Hrx, Krx = (alt([d for d in D if f(d)]) for f in (Cs, Hs_, Ks))
    check("ZN AR", Crx + "(?:;" + Hrx + "(?::" + Krx + ")+)+", s, ZNR[s]["AR"])
W_ = lambda key: {s: ZNR[s][key] for s in SUBJ_ZN}
print("   %d subjects RUN; AR ENGINE-RUN" % len(SUBJ_ZN))
count("AR vs today", SUBJ_ZN, W_("today"), W_("AR"), "today", "AR")
count("AR record vs & (k read PER REACH)  [record = &]", SUBJ_ZN, W_("AR"), W_("& reach"), "record", "&")
count("AR record vs & (k's values POOLED over the match)", SUBJ_ZN, W_("AR"), W_("& pooled"), "record", "&pool")

print("\n(NL) jcfold's nested non-product: /(?:(?<h>\\d):(?:(?<k>\\d),)*;)*/ & ((h, k): >= (5, 3))")
P_NL = r"(?:(?<h>\d):(?:(?<k>\d),)*;)*"
SUBJ_NL = ["".join("%s:%s;" % (a, "".join(k + "," for k in ks)) for a, ks in its) for n in range(3)
           for its in itertools.product([("4", ()), ("4", ("9",)), ("5", ()), ("5", ("3",)), ("5", ("2",)),
                                         ("5", ("3", "4")), ("6", ("0", "1")), ("5", ("4", "2"))], repeat=n)]
NLR = {}
for s in SUBJ_NL:
    assert whole(P_NL, s)
    its = [(i.split(":")[0], [k for k in i.split(":")[1].split(",") if k]) for i in s.split(";")[:-1]]
    tu = [(Z, Z)] if not its else [t for a, ks in its for t in ([(a, Z)] if not ks else [(a, k) for k in ks])]
    old_nl = all(JNT((a, k)) for a, ks in its for k in ks)                                  # jcfold: vacuous
    m_nl = all(all(JNT((a, k)) for k in ks) if ks else any(JNT((a, k)) for k in D) for a, ks in its)  # jcfold2 M
    NLR[s] = {"AR": cond(AR, tu, JNT, [D, D]), "jcfold": old_nl, "jcfold2 M": m_nl,
              "AR k?": cond(AR, tu, JNT, [D, D], (1,)), "AR h?, k?": cond(AR, tu, JNT, [D, D], (0, 1))}
    items = "(?:" + "|".join(a + ":(?:" + alt([k for k in D if JNT((a, k))]) + ",)+;" for a in D) + ")"
    check("NL AR", items + "+", s, NLR[s]["AR"])
X_ = lambda key: {s: NLR[s][key] for s in SUBJ_NL}
print("   %d subjects RUN; AR ENGINE-RUN" % len(SUBJ_NL))
count("AR vs jcfold's (NL) answers", SUBJ_NL, X_("jcfold"), X_("AR"), "NL", "AR")
count("AR vs jcfold2's (ZN-NL) answers (M)", SUBJ_NL, X_("jcfold2 M"), X_("AR"), "M", "AR")
count("AR ((h, k?): ..) vs jcfold2's M", SUBJ_NL, X_("jcfold2 M"), X_("AR k?"), "M", "k?")
count("AR ((h?, k?): ..) vs jcfold2's M", SUBJ_NL, X_("jcfold2 M"), X_("AR h?, k?"), "M", "h?,k?")

# =================================================================================================================
print("\n(ZJ) jcfold2's non-product sets on (RZ)'s pattern, zero passes (10 subjects per set)")
DOM_ANY = D + ["x"]
ZJ = [
    ("((h, k): >= (5, 3))", lambda t: t[0] != "x" and (int(t[0]), int(t[1])) >= (5, 3),
     [(set("6789"), None), ({"5"}, set("3456789"))]),
    ("((k, h): >= (5, 3))", lambda t: t[0] != "x" and (int(t[1]), int(t[0])) >= (5, 3),
     [(None, set("6789")), (set("3456789"), {"5"})]),
    ("((h, k): (0|1|2, 3|4) | (5, 5))", lambda t: (t[0] in "012" and t[1] in "34") or (t[0] == "5" and t[1] == "5"),
     [(set("012"), set("34")), ({"5"}, {"5"})]),
    ("((h, k): (\"x\", 3) | (0, 5))", lambda t: (t[0] == "x" and t[1] == "3") or (t[0] == "0" and t[1] == "5"),
     [({"x"}, {"3"}), ({"0"}, {"5"})]),
    ("((h, k): < (0, 3))", lambda t: t[0] != "x" and (int(t[0]), int(t[1])) < (0, 3),
     [(set(), None), ({"0"}, set("012"))]),
]
ZEROS = [k for k in D]
for name, Rf, rws in ZJ:
    a_ar, a_md, a_ma, e_md, e_ma = {}, {}, {}, {}, {}
    rx_ar = "(?:" + "|".join(kk + "(?:;" + alt([h for h in D if Rf((h, kk))]) + ")+" for kk in D) + ")"
    rx_md = "(?:" + "|".join(kk + "(?:;" + alt([h for h in D if Rf((h, kk))]) + ")" +
                             ("*" if any(Rf((h, kk)) for h in D) else "+") for kk in D) + ")"
    for s in SUBJ_RZ:
        k, *hs = s.split(";")
        tu = [(h, k) for h in hs] if hs else [(Z, k)]
        a_ar[s] = cond(AR, tu, Rf, [D, D])
        a_md[s] = cond(AR, tu, Rf, [D, D], (0,))
        a_ma[s] = cond(AR, tu, Rf, [DOM_ANY, D], (0,))
        # the hand expansion into a `|` of records, each record with h MARKED (projection per row's own part)
        for store, dom in ((e_md, D), (e_ma, DOM_ANY)):
            store[s] = any((Ks is None or k in Ks) and (all(Hs is None or h in Hs for h in hs) if hs else
                                                        (Hs is None or any(v in Hs for v in dom))) for Hs, Ks in rws)
        check("ZJ AR", rx_ar, s, a_ar[s])
        check("ZJ AR h?", rx_md, s, a_md[s])
    zs = [s for s in SUBJ_RZ if ";" not in s]
    print("   %-34s AR zero-pass HOLDS on %d of 10; h? (\\d) %s; h? (every string) %s" %
          (name, sum(a_ar[s] for s in zs), sorted(s for s in zs if a_md[s]), sorted(s for s in zs if a_ma[s])))
    count("   zero passes: h? joint vs h? hand expansion, \\d domain", zs, a_md, e_md, "joint", "expansion")
    count("   zero passes: h? joint vs h? hand expansion, every-string domain", zs, a_ma, e_ma, "joint", "expansion")
print("(ZJ-E) the EMPTY set of pairs, zero passes, subject '3':")
for txt, tuples_, Rf, preds, product in (
        ("(h: <0, k: 3)", [(Z, "3")], lambda t: False, [lambda x: False, lambda x: x == "3"], True),
        ("((h, k): (<0, 3))", [(Z, "3")], lambda t: False, [lambda x: False, lambda x: x == "3"], True),
        ("((h, k): < (0, 0))", [(Z, "3")], lambda t: (int(t[0]), int(t[1])) < (0, 0), None, False)):
    f1 = cond(AR, tuples_, Rf, [D, D], (0,))
    f2 = rec_f2(tuples_, preds, [D, D], (0,)) if product else f1
    print("   %-22s unmarked %s   h? read F1 (some value) %s   h? read F2 (satisfied outright) %s" %
          (txt, hfx(cond(AR, tuples_, Rf, [D, D])), hfx(f1), hfx(f2)))

# =================================================================================================================
print("\n(ZE) jcfix's zero-pass-empty: /(?<a>\\d)-(?<k>\\d)(?:;(?<h>\\d))*/, the set empty only through $a")
P_ZE = r"(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*"
SUBJ_ZE = ["%s-%s" % (a, k) + "".join(";" + h for h in hs) for a in D for k in D for n in range(3)
           for hs in itertools.product(D, repeat=n)]
ZER = {}
RX_ZE = "(?:" + "|".join("%s-%s(?:;%s)+" % (aa, kk, alt([h for h in D if int(h) < int(aa) and kk == "3"]))
                         for aa in D for kk in D) + ")"
for s in SUBJ_ZE:
    assert whole(P_ZE, s)
    head, *hs = s.split(";")
    a, k = head.split("-")
    tu = [(h, k) for h in hs] if hs else [(Z, k)]
    C1 = lambda t, a=a: canon(t[0]) and int(t[0]) < int(a) and t[1] == "3"
    C2 = lambda t, a=a: (int(t[0]), int(t[1])) < (int(a), 0)
    ZER[s] = {
        "C1 AR": cond(AR, tu, C1, [D, D]), "C2 AR": cond(AR, tu, C2, [D, D]),
        "C1 &": plain(AR, hs, lambda x, a=a: int(x) < int(a), D) and k == "3",
        "C2 rows": plain(AR, hs, lambda x, a=a: int(x) < int(a), D) or
                   (plain(AR, hs, lambda x, a=a: x == a, D) and int(k) < 0),
        "C1 h? F1": cond(AR, tu, C1, [D, D], (0,)), "C2 h? F1": cond(AR, tu, C2, [D, D], (0,)),
        "C1 h? F2": rec_f2(tu, [lambda x, a=a: int(x) < int(a), lambda x: x == "3"], [D, D], (0,)),
    }
    ZER[s]["C2 h? F2"] = ZER[s]["C2 h? F1"]           # a non-product: the ruling's joint sentence (some value)
    check("ZE C1 AR", RX_ZE, s, ZER[s]["C1 AR"])
Y_ = lambda key: {s: ZER[s][key] for s in SUBJ_ZE}
print("   %d subjects; C1 = (h: <$a, k: 3), C2 = ((h, k): < ($a, 0)); C1 AR ENGINE-RUN" % len(SUBJ_ZE))
count("C1 AR record vs (h: <$a) & (k: 3)  [record = &]", SUBJ_ZE, Y_("C1 AR"), Y_("C1 &"), "record", "&")
count("C2 AR joint vs its hand expansion into records", SUBJ_ZE, Y_("C2 AR"), Y_("C2 rows"), "joint", "rows")
A0 = [s for s in SUBJ_ZE if s.startswith("0-")]
count("a = 0 (both spellings EMPTY): C1 vs C2, unmarked", A0, Y_("C1 AR"), Y_("C2 AR"), "C1", "C2")
count("a = 0: C1 vs C2, h? read F1 (some value would do)", A0, Y_("C1 h? F1"), Y_("C2 h? F1"), "C1", "C2")
count("a = 0: C1 vs C2, h? read F2 (satisfied outright; joint keeps F1)", A0, Y_("C1 h? F2"), Y_("C2 h? F2"),
      "C1", "C2")
count("C1: h? F1 vs F2", SUBJ_ZE, Y_("C1 h? F1"), Y_("C1 h? F2"), "F1", "F2")
for s in ("0-3", "3-3", "0-5"):
    print("   %-5s " % s + "  ".join("%s %s" % (k, hfx(ZER[s][k])) for k in ("C1 AR", "C2 AR", "C1 h? F1", "C2 h? F1",
                                                                         "C1 h? F2")))
print("   one label: (h?: <0) on the empty list of /(?:(?<h>\\d),)*/: F1 %s, F2 HOLDS (the same corner, k = 1)" %
      hfx(plain(AR, [], lambda x: False, D, mark=True)))

# =================================================================================================================
print("\n(ZD) jcfold2's defaults")
P2 = r"(?<k>\d)(?:-(?:;(?<h>\d))*)?"
SUBJ_P2 = list(D) + [k + "-" + "".join(";" + h for h in hs) for k in D for n in range(3)
                     for hs in itertools.product(D, repeat=n)]
for dflt in (None, "9", "2"):
    res = {}
    for s in SUBJ_P2:
        g = groups(P2, s, ["k"])
        assert g is not None
        k = s[0]
        if "-" not in s:
            tu = [(U, k)]
        else:
            hs = [h for h in s.split("-")[1].split(";") if h]
            tu = [(h, k) for h in hs] if hs else [(Z, k)]
        res[s] = cond(AR, tu, REC, [D, D], (), {} if dflt is None else {0: dflt})
        unr = T37rx + "-?" if (dflt is not None and S5(dflt)) else "(?!)"   # absent (never reached / zero): v
        check("ZD b", "(?:" + T37rx + "-(?:;" + S5rx + ")+|" + unr + ")", s, res[s])
    print("   (ZD b) P2 & (h%s: <5, k: 3..7): '5' (never reached) %s, '5-' (zero passes) %s  [jcfold2: %s]" %
          ("" if dflt is None else " = " + dflt, hfx(res["5"]), hfx(res["5-"]),
           {None: "FAILS, HOLDS", "9": "FAILS, HOLDS", "2": "HOLDS, HOLDS"}[dflt]))
P_L = r"(?:(?<h>\d)(?::(?<m>\d))?,)*"
GE53 = lambda t: num(t[0]) and num(t[1]) and (int(t[0]), int(t[1])) >= (5, 3)
SUBJ_L = [""] + ["".join("%s%s," % (h, "" if m is None else ":" + m) for h, m in its) for n in (1, 2)
                 for its in itertools.product([(h, m) for h in "456" for m in (None, "0", "3")], repeat=n)]
ZDc = {"AR": {}, "AR h?": {}, "today": {}}
for s in SUBJ_L:
    assert whole(P_L, s)
    its = s.split(",")[:-1]
    tu = [(Z, Z)] if not its else [(i.split(":")[0], i.split(":")[1] if ":" in i else P) for i in its]
    ZDc["AR"][s] = cond(AR, tu, GE53, [D, D], (), {1: "0"})
    ZDc["AR h?"][s] = cond(AR, tu, GE53, [D, D], (0,), {1: "0"})
    ZDc["today"][s] = cond(TD, tu, GE53, [D, D], (), {1: "0"})
    item = "(?:(?:" + "|".join(h + "(?::" + alt([m for m in D if GE53((h, m))]) + ")" + ("?" if GE53((h, "0")) else "")
                              for h in D) + "),)"
    check("ZD c AR", item + "+", s, ZDc["AR"][s])
    check("ZD c AR h?", item + "*", s, ZDc["AR h?"][s])
print("   (ZD c) %d lists, /(?:(?<h>\\d)(?::(?<m>\\d))?,)*/ & ((h, m = 0): >= (5, 3)): the empty list AR %s, "
      "(h?, m = 0) %s" % (len(SUBJ_L), hfx(ZDc["AR"][""]), hfx(ZDc["AR h?"][""])))
count("(ZD c) AR vs today", SUBJ_L, ZDc["today"], ZDc["AR"], "today", "AR")
count("(ZD c) AR ((h?, m = 0): ..) vs today", SUBJ_L, ZDc["today"], ZDc["AR h?"], "today", "h?")

# =================================================================================================================
print("\n(OP) jcfix's optional-in-a-pass: /(?:(?<h>\\d+)(?::(?<m>\\d\\d))?,)*/ & (h: <10, m: <30)")
P_OP = r"(?:(?<h>\d+)(?::(?<m>\d\d))?,)*"
OP_ITEMS = [(h, m) for h in ("3", "12") for m in (None, "15", "45")]
SUBJ_OP = ["".join("%s%s," % (h, "" if m is None else ":" + m) for h, m in its)
           for n in range(4) for its in itertools.product(OP_ITEMS, repeat=n)]
Sh = lambda x: canon(x) and int(x) < 10
Tm = lambda x: canon(x) and int(x) < 30
HM = lambda t: Sh(t[0]) and Tm(t[1])
DH = [str(i) for i in range(13)]
DM2 = ["%02d" % i for i in range(100)]
OPR = {}
for s in SUBJ_OP:
    assert whole(P_OP, s)
    its = [(i.split(":")[0], i.split(":")[1] if ":" in i else None) for i in s.split(",")[:-1]]
    tu = [(Z, Z)] if not its else [(h, m if m is not None else P) for h, m in its]
    zero = not its
    ms = [m for _, m in its]
    OPR[s] = {
        "AR": cond(AR, tu, HM, [DH, DM2]),
        "today": cond(TD, tu, HM, [DH, DM2]),
        "& per pass": plain(AR, [h for h, _ in its], Sh, DH) and plain(AR, ms, Tm, DM2),
        "& pooled": plain(AR, [h for h, _ in its], Sh, DH) and plain(AR, [m for m in ms if m is not None], Tm, DM2),
        "(h?, m?)": cond(AR, tu, HM, [DH, DM2], (0, 1)),
        "(h?, m = 0)": cond(AR, tu, HM, [DH, DM2], (0,), {1: "0"}),
        "(h, m = 0)": cond(AR, tu, HM, [DH, DM2], (), {1: "0"}),
        "all A2v": a2("A2v", tu, zero, HM, [DH, DM2]),
        "all A2z": a2("A2z", tu, zero, HM, [DH, DM2]),
        "all A2m": a2("A2m", tu, zero, HM, [DH, DM2]),
    }
    H10, M30 = alt([str(i) for i in range(10)]), alt(["%02d" % i for i in range(10, 30)])
    check("OP AR", "(?:" + H10 + ":" + M30 + ",)+", s, OPR[s]["AR"])
    check("OP all A2v", "(?:" + H10 + ":" + M30 + ",)*", s, OPR[s]["all A2v"])
O_ = lambda key: {s: OPR[s][key] for s in SUBJ_OP}
print("   %d lists RUN; AR and all A2v ENGINE-RUN" % len(SUBJ_OP))
count("AR record vs today", SUBJ_OP, O_("today"), O_("AR"), "today", "AR")
count("AR record vs & (each label per pass of its loop)  [record = &]", SUBJ_OP, O_("AR"), O_("& per pass"),
      "record", "&")
count("AR record vs & (m's values pooled over the match)", SUBJ_OP, O_("AR"), O_("& pooled"), "record", "&pool")
for f in ("(h?, m?)", "(h?, m = 0)", "(h, m = 0)", "all A2v", "all A2z", "all A2m"):
    count("today's answer kept by %s?" % f, SUBJ_OP, O_("today"), O_(f), "today", f)

# =================================================================================================================
print("\n(UP) jcfix's unreached pairing: /(?:(?<h>\\d)(?:-(?:(?<k>\\d),)*)?;)*/ & (h: <5, k: <5)")
P_UP = r"(?:(?<h>\d)(?:-(?:(?<k>\d),)*)?;)*"
UP_ITEMS = [(h, ks) for h in "349" for ks in [None, (), ("2",), ("7",), ("2", "7")]]
SUBJ_UP = ["".join("%s%s;" % (h, "" if ks is None else "-" + "".join(k + "," for k in ks)) for h, ks in its)
           for n in range(3) for its in itertools.product(UP_ITEMS, repeat=n)]
S55 = lambda t: S5(t[0]) and S5(t[1])
UPR = {}
for s in SUBJ_UP:
    assert whole(P_UP, s)
    its = []
    for it in s.split(";")[:-1]:
        h, _, rest = it.partition("-")
        its.append((h, None if "-" not in it else [k for k in rest.split(",") if k]))
    if not its:
        tu = [(Z, Z)]
    else:
        tu = []
        for h, ks in its:
            tu += [(h, P)] if ks is None else ([(h, Z)] if not ks else [(h, k) for k in ks])
    # & : (h: <5) per outer pass; (k: <5) per pass of k's loop: a pass that does not reach it, or a reach with no
    # pass, is an absence (one kind); no outer pass: both absent
    k_amp = bool(its) and all(ks is not None and plain(AR, ks, S5, D) for _, ks in its)
    k_amp_m = all(ks is None or plain(AR, ks, S5, D, mark=True) for _, ks in its)
    UPR[s] = {"AR": cond(AR, tu, S55, [D, D]), "today": cond(TD, tu, S55, [D, D]),
              "&": plain(AR, [h for h, _ in its], S5, D) and k_amp,
              "AR k?": cond(AR, tu, S55, [D, D], (1,)),
              "& k?": plain(AR, [h for h, _ in its], S5, D) and k_amp_m}
    check("UP AR", "(?:" + S5rx + "-(?:" + S5rx + ",)+;)+", s, UPR[s]["AR"])
    check("UP AR k?", "(?:" + S5rx + "(?:-(?:" + S5rx + ",)*)?;)+", s, UPR[s]["AR k?"])
Q_ = lambda key: {s: UPR[s][key] for s in SUBJ_UP}
print("   %d subjects RUN; AR and k? ENGINE-RUN" % len(SUBJ_UP))
count("AR vs today", SUBJ_UP, Q_("today"), Q_("AR"), "today", "AR")
count("AR record vs (h: <5) & (k: <5)  [record = &]", SUBJ_UP, Q_("AR"), Q_("&"), "record", "&")
count("AR (h: <5, k?: <5) vs (h: <5) & (k?: <5)", SUBJ_UP, Q_("AR k?"), Q_("& k?"), "record", "&")
for s in ("3-2,;9;", "3-2,;4;", "3-;4;", "3;", ""):
    print("   %-9r AR %s  k? %s  today %s" % (s, hfx(UPR[s]["AR"]), hfx(UPR[s]["AR k?"]), hfx(UPR[s]["today"])))

# =================================================================================================================
print("\n(D1) unsetdef's single-label defaults on t2 (set-once m) and default.unused")
d1 = {}
for v in ("0", "45", "00"):
    same = 0
    for s in SUBJ_T2:
        t = (s.split(":")[1],) if ":" in s else (U,)
        same += cond(AR, [t], lambda t: Tm(t[0]), [M], (), {0: v}) == cond(AR, [t], lambda t: Tm(t[0]), [M])
    d1[v] = same
    print("   t2 & (m = %-2s: <30): same answers as no default on %d of %d" % (v, same, len(SUBJ_T2)))
old_d1 = old_out("unsetdef_check.out")
ctl = [int(x) for x in re.findall(r"same answers as no default on (\d+) of 11110", old_d1)]
print("   OLD-OUT control: unsetdef printed %s; AR %s" % (ctl, [d1[v] for v in ("0", "45", "00")]))
print("   default.unused (a) on a LOOPED label (absimpact's (LI) list): `(n = 0: <5)` vs `(n: <5)` differ %d of 1111 "
      "under AR (used: the empty list); `(n = 9: <5)` differ %d (unused: clause (b))" % tuple(
          sum(plain(AR, L_, S5, D, default=v) != plain(AR, L_, S5, D) for L_ in
              [list(c) for k in range(4) for c in itertools.product(D, repeat=k)]) for v in ("0", "9")))

print("\n(DL) unsetdef's looped list: /(?:(?<h>\\d{1,2})(?::(?<m>\\d\\d))?,)*/ & ((h, m = 0): padded(between((9, 30), "
      "(11, 0))))")
BTW = lambda t: num(t[0]) and num(t[1]) and (9, 30) <= (int(t[0]), int(t[1])) <= (11, 0)
DL = {"AR": {}, "today": {}, "AR h?": {}}
SUBJ_DL = []
for n in range(4):
    for combo in itertools.product(["9", "10", "11", "12", "9:45", "9:15", "10:30", "11:30"], repeat=n):
        s = "".join(c + "," for c in combo)
        SUBJ_DL.append(s)
        tu = [(Z, Z)] if not combo else [(c.split(":")[0], c.split(":")[1] if ":" in c else P) for c in combo]
        DL["AR"][s] = cond(AR, tu, BTW, [H, M], (), {1: "0"})
        DL["today"][s] = cond(TD, tu, BTW, [H, M], (), {1: "0"})
        DL["AR h?"][s] = cond(AR, tu, BTW, [H, M], (0,), {1: "0"})
rows_b = "(?:" + "|".join(alt([h for h in H if (9, 30) <= (int(h), int(m)) <= (11, 0)]) + ":" + m for m in M
                          if any((9, 30) <= (int(h), int(m)) <= (11, 0) for h in H)) + ")"
it_b = "(?:" + rows_b + "|" + alt([h for h in H if BTW((h, "0"))]) + "),"
for s in SUBJ_DL:
    check("DL AR", "(?:" + it_b + ")+", s, DL["AR"][s])
    check("DL AR h?", "(?:" + it_b + ")*", s, DL["AR h?"][s])
print("   %d lists; the empty list: AR %s, today %s, ((h?, m = 0): R) %s; '10,9:15,' AR %s" %
      (len(SUBJ_DL), hfx(DL["AR"][""]), hfx(DL["today"][""]), hfx(DL["AR h?"][""]), hfx(DL["AR"]["10,9:15,"])))
count("AR vs today", SUBJ_DL, DL["today"], DL["AR"], "today", "AR")
count("AR ((h?, m = 0): R) vs today", SUBJ_DL, DL["today"], DL["AR h?"], "today", "h?")

print("\n(DD) unsetdef's date without a day, now with the mark: ym := /(?<y>\\d{4})-(?<mo>\\d\\d)(?:-(?<d>\\d\\d))?/ & "
      "((y, mo, d?): padded(between((2024, 2, 15), (2024, 4, 1))))")
DD_ = ["%02d" % i for i in range(100)]
BD = lambda t: all(num(x) for x in t) and (2024, 2, 15) <= tuple(int(x) for x in t) <= (2024, 4, 1)
adm = [mo for mo in ["%02d" % i for i in range(1, 13)] if cond(AR, [("2024", mo, U)], BD, [D, D, DD_], (2,))]
print("   months admitted with no day: %s (unsetdef's 'does not matter' answer: 02, 03, 04; no default day gives it)"
      % ", ".join(adm))

# =================================================================================================================
print("\n(L36) `all` beside the plain condition, over lane absent's 28 spelling rows (11 groups), `(n: <5)`, n absent")
src2 = open(os.path.join(HERE, "absent_check.py")).read()
a0 = src2.index("SP = [")
ns = {}
exec(src2[a0:src2.index("\n]\n", a0) + 3], ns)
SPL = ns["SP"]
spres = {m_: {} for m_ in ("plain", "A2v", "A2z", "A2m", "mark")}
for g_, pat, probe, pg, subj, k_set, k_unset, scope in SPL:
    if probe is None:
        prev = [r for r in SPL if r[1] == pat and r[2] is not None and subj.endswith(r[4]) and r[4] != subj][0]
        st = groups(prev[2], prev[4], [prev[3]])[prev[3]] is not None
    else:
        st = groups(probe, subj, [pg])[pg] is not None
    kind = k_set if st else k_unset
    k = "Z" if kind == "Z" else ("P" if scope != "match" else "U")
    key = (g_, pat, subj)
    x = {"Z": Z, "U": U, "P": P}[k]
    tu = [(x,)]
    spres["plain"][key] = cond(AR, tu, lambda t: S5(t[0]), [D])
    spres["A2v"][key] = True if k == "Z" else spres["plain"][key]
    spres["A2z"][key] = cond(TD, tu, lambda t: S5(t[0]), [D]) if not SAB else spres["plain"][key]
    spres["A2m"][key] = cond(AR, tu, lambda t: S5(t[0]), [D], (0,))
    spres["mark"][key] = spres["A2m"][key]
groups_ = sorted({k[0] for k in spres["plain"]})
for m_ in ("plain", "A2v", "A2z", "A2m"):
    split = sum(len({spres[m_][k] for k in spres[m_] if k[0] == g}) > 1 for g in groups_)
    print("   %-28s groups of equal spellings that SPLIT: %d of %d" %
          ({"plain": "(n: <5)", "A2v": "all((n: <5)) A2v (no pass)", "A2z": "all((n: <5)) A2z (zero only)",
            "A2m": "all((n: <5)) A2m (any absence)"}[m_], split, len(groups_)))
LI_ = [list(c) for k in range(4) for c in itertools.product(D, repeat=k)]
LIk = ["".join(x + "," for x in l) for l in LI_]
pl = {s: plain(AR, l, S5, D) for s, l in zip(LIk, LI_)}
al = {s: (True if not l else plain(AR, l, S5, D)) for s, l in zip(LIk, LI_)}
mk = {s: plain(AR, l, S5, D, mark=True) for s, l in zip(LIk, LI_)}
count("(LI) (n: <5) vs all((n: <5)) [A2 any reading]", LIk, pl, al, "plain", "all")
count("(LI) all((n: <5)) vs (n?: <5)", LIk, al, mk, "all", "n?")
for s in LIk:
    check("LI all", "(?:" + S5rx + ",)*", s, al[s])
al0 = {s: (True if not l else plain(AR, l, lambda x: False, D)) for s, l in zip(LIk, LI_)}
mk0 = {s: plain(AR, l, lambda x: False, D, mark=True) for s, l in zip(LIk, LI_)}
count("(LI) all((n: <0)) vs (n?: <0)  [the empty-set corner]", LIk, al0, mk0, "all", "n?")

print("\nTOTAL cases %d differ %d engine-disagreements %d probes %d" % (TOT["cases"], TOT["differ"], DIS[0],
                                                                        TOT["probes"]))
