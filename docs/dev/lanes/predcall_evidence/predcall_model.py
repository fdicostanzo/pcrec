#!/usr/bin/env python3
# Lane predcall (2026-11-22): the evidence for folding the owner's call-prefix ruling (case 1: "yes use the macro
# name as shown to qualify the label"), stating his lean on case 2 and on closed-argument, his statement "[ c = B(A) ]
# does not allow c.A", his second `hits` example, and the manager's readings (a)..(e) of the lane brief.
# DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD. Lane predref's model is LOADED unchanged: predref_model.py is executed up to its line "the checks" (its
# definitions; it in turn loads lane predbound's lowerer and matcher unchanged). Its own plants are cleared, so none
# fires unless this model sets one. EXTENSIONS of this lane, after the load:
#   MACRO-PREFIX  case 1 (ruled): a call `m(..)` of a macro whose body is a pattern carries a part label of the
#                 macro's own name, as a used binding does (binding-prefix's mechanism, unchanged): every public
#                 group the call surfaces (the body's and the arguments') also sets `m.x`; the call counts as a USE
#                 of the name `m` in the definition it is written in, so binding-prefix's two rules apply to it as
#                 they do to a binding (reading (a)).
#   ARG-COUNT     an argument that is a binding counts as ONE use of its name in the caller however often the body
#                 lowers the parameter (reading (d): "used more than once" is counted in the definition the reference
#                 is written in, and the caller writes `A` once). OPT argcount = "lowered" is the other count (every
#                 lowering a use), shown for contrast.
# Every three-mode line formatted for the documents must occur VERBATIM in them (DOC). The record's pasted lines are
# read from the record, never typed by hand (RECORD, HITS2).
#
# Run (W = the worktree; any cwd):  timeout 300 python3 -I -B W/docs/dev/lanes/predcall_evidence/predcall_model.py
# PREDCALL_SABOTAGE=sN (one at a time): a deliberately wrong rule or fact; its target check must FAIL.
#   s1  the matcher tries alternatives last first (predref's plant s3)                         -> CONTROL
#   s2  a macro's name carries no prefix (case 1 off)                                          -> CASE1
#   s3  a plain read through a twice-used prefix accepted (predbound's plant s18)              -> TWICE
#   s4  a binding passed as an argument also prefixes the body's own groups                     -> RECORD
#   s5  an argument counted once per lowering, not once in the caller's text                   -> PAIR
#   s6  a path to a label the prefix does not pass accepted (predbound's plant s19)            -> CA
#   s7  `hits`'s atomic group dropped (predref's plant s6)                                     -> HITS2
#   s8  a quoted owner sentence altered (in memory)                                            -> QUOTES
#   s9  the call-prefix piece read back as still open (in memory)                              -> MARKS
#   s10 a planted printed program reading a borrowed label bare (in memory)                    -> SCAN
#   s11 predref's model run with one of its own plants (s3), so its red set differs            -> PREDREF
#   s12 one formatted line's subject altered before the document lookup                        -> DOC
#   s13 `[_ = X]` in a macro body passes X's labels on (the closure ignored)                    -> CLOSED
# R-1 of the rulings file (closed-argument RULED (a)) adds the check CLOSED: where the macro closes its argument's
# labels the caller's `A.d` is refused; where `d` is visible through the call it is legal and reads `d` as it
# reaches the caller.
import os
import re
import subprocess
import sys

HERE1 = os.path.dirname(os.path.abspath(__file__))
PR = os.path.join(HERE1, "..", "predref_evidence", "predref_model.py")
SABC = set(x for x in os.environ.get("PREDCALL_SABOTAGE", "").split(",") if x)
os.environ.pop("PREDREF_SABOTAGE", None)
os.environ.pop("PREDBOUND_SABOTAGE", None)


def sabc(n):
    return n in SABC


_src1 = open(PR, encoding="utf-8").read()
_cut1 = re.search(r"^# =+ the checks$", _src1, re.M).start()
exec(compile(_src1[:_cut1], PR, "exec"), globals())         # noqa: S102  (predref's definitions, unchanged)

SABR.clear()
SAB.clear()
if sabc("s1"):
    SABR.add("s3")
if sabc("s3"):
    SAB.add("s18")
if sabc("s6"):
    SAB.add("s19")
if sabc("s7"):
    SABR.add("s6")

RESULTS = []


def check(name, ok, detail=""):                              # noqa: F811
    RESULTS.append((name, bool(ok)))
    print("%s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


NEW = {f: read(os.path.join(PRED, f)) for f in ("core.md", "library.md", "parked.md", "core_details.md",
                                                 "library_details.md", "parked_details.md")}
ALLDOC = "\n".join(NEW.values())

# ================================================================== EXTENSIONS (lane predcall)
ARGSEEN = {}
_base_binds2 = base_binds


def base_binds():                                            # noqa: F811
    _base_binds2()
    ARGSEEN.clear()


_lower_atom2 = lower_atom


def lower_atom(expr, ctx):                                   # noqa: F811
    """MACRO-PREFIX: a call of a pattern macro is a use of the macro's name, which prefixes what the call surfaces."""
    e = expr.strip()
    if sabc("s13") and e.startswith("[_ = "):
        e = "[_closed = " + e[len("[_ = "):]                 # a `_x` part label: the model keeps its groups' keys
        return _lower_atom2(e, ctx)
    call = parse_call(e)
    if (call and call[0] in MACROS and re.fullmatch(r"[A-Za-z]\w*", call[0])
            and not is_cond(pick_macro(*call)[1]) and not sabc("s2")):
        text = _lower_atom2(e, ctx)
        if sabc("s4"):
            for a in call[1]:
                if a.strip() in BINDS:
                    text = add_prefix(text, a.strip())
        USES[(ctx.cur, call[0])] = USES.get((ctx.cur, call[0]), 0) + 1
        ctx.held.add(call[0])
        return add_prefix(text, call[0])
    return _lower_atom2(expr, ctx)


_use_param2 = use_param


def use_param(name, ctx):                                    # noqa: F811
    """ARG-COUNT: the second and later lowerings of one argument of one call add no use in the caller."""
    key = (id(ctx.params), name)
    before = dict(USES)
    out = _use_param2(name, ctx)
    if OPT.get("argcount", "text") == "text" and not sabc("s5"):
        if key in ARGSEEN:
            for k in list(USES):
                if USES[k] > before.get(k, 0):
                    USES[k] = before.get(k, 0)
        else:
            ARGSEEN[key] = ctx.params                        # kept alive, so its id is not reused
    return out


def hitlist(lab, call, t):
    """The hit list `[lab = call]` leaves on the whole text t (predref's HITS helper, restated: it sits after
    predref's checks line, which this model does not load)."""
    st = whole_state(prog("[%s = %s]" % (lab, call)), t)
    return settings(st.log, "%s.hit@top" % lab, "top") if st else None


def whole_ndiff(Pg, pred, texts):
    return sum(1 for t in texts if Pg.whole(t) != pred(t))


def fmt_rec_each(Pg, wh, sr, fa, hl=None):
    """The record's own form: `WHOLE `t` HOLDS / WHOLE ...`, hit lists as python lists."""
    parts = []
    for t in wh:
        x = "WHOLE `%s` %s" % (t, "HOLDS" if Pg.whole(t) else "FAILS")
        if hl:
            x += " (hits %r)" % (hitlist(hl[0], hl[1], t),)
        parts.append(x)
    r = Pg.search(sr)
    parts.append("SEARCHED `%s` %s" % (sr, "`%s`@%d" % (sr[r[0]:r[1]], r[0]) if r else "FAILS"))
    parts.append("FIND-ALL `%s` [%s]" % (fa, ", ".join("`%s`@%d" % x for x in Pg.findall(fa))))
    return " / ".join(parts)


def fmt_doc_hits(Pg, wh, sr, fa, hl):
    w = []
    for t in wh:
        x = "`%s` %s" % (t, "HOLDS" if Pg.whole(t) else "FAILS")
        x += " (hits [%s])" % ", ".join("`%s`" % v for v in hitlist(hl[0], hl[1], t))
        w.append(x)
    r = Pg.search(sr)
    return "WHOLE %s / SEARCHED `%s` %s / FIND-ALL `%s` [%s]" % (
        ", ".join(w), sr, "`%s`@%d" % (sr[r[0]:r[1]], r[0]) if r else "FAILS", fa,
        ", ".join("`%s`@%d" % x for x in Pg.findall(fa)))


def rec_line(prefix):
    ls = [x for x in RECORD.split("\n") if x.startswith(prefix)]
    assert len(ls) == 1, (prefix, ls)
    return ls[0]


def rec_answer(line):
    return line[line.index("WHOLE "):]


def rec_texts(line):
    a = rec_answer(line)
    wh = re.findall(r"WHOLE `([^`]*)`", a)
    sr = re.search(r"SEARCHED `([^`]*)`", a).group(1)
    fa = re.search(r"FIND-ALL `([^`]*)` \[", a).group(1)
    return wh, sr, fa


# ================================================================== the checks
print("== CONTROL: the loaded matcher, programs without conditions, against python `re`")
POPA = pop("ab;7", 4)
c1 = ndiff(answers(prog('"ab" | "a"'), POPA), answers(Re(r"ab|a"), POPA))
c2 = ndiff(answers(prog("hits(/\\d+/)"), pop("1a ", 4)),
           answers(Re(r"\A(?>(?:(?s:.*?)(?:\d+))*[\s\S]*)\Z"), pop("1a ", 4)))
c3 = ndiff(answers(prog("B(A)", ["A := /(?<d>\\d)/", "B(rx) := /${rx}-(?<d>\\d)/"]), pop("37-", 4)),
           answers(Re(r"\d-\d"), pop("37-", 4)))
check("CONTROL", (c1, c2, c3) == ((0, 0, 0),) * 3,
      "differing (WHOLE, SEARCHED, FIND-ALL): `\"ab\" | \"a\"` %s over %d texts; `hits` %s; `B(A)` (A, B of the "
      "call-prefix run) against `\\d-\\d` %s" % (c1, len(POPA), c2, c3))

print("== CASE1: the ruling, the macro's name as the prefix; his example; one call reads as a labelled call")
CW, CS, CF = ["a1b3", "a3b1", "3", "a13", "ab"], "x1 3", "a3 b1 3"
POPH = pop("13 a", 4)
P_name = safe_prog("hits(/\\d+/) & (hits.hit: 3)")
P_lab = prog("[h = hits(/\\d+/)] & (h.hit: 3)")
last3 = (lambda t: bool(re.findall(r"\d+", t)) and re.findall(r"\d+", t)[-1] == "3")
d_name = safe_ndiff(P_name, P_lab, POPH)
w_direct = whole_ndiff(P_name, last3, POPH) if P_name else -1
L_name = L_lab = None
if P_name:
    L_name = doc_line("By the macro's name, his example: %s (`hits(/\\d+/) & (hits.hit: 3)`)" % fmt(P_name, CW, CS, CF),
                      "call-prefix")
    print("   " + L_name)
L_lab = doc_line("Labelled: %s (`[h = hits(/\\d+/)] & (h.hit: 3)`)" % fmt(P_lab, CW, CS, CF), "call-prefix")
print("   " + L_lab)
# the library's printed lines, the call labelled, against the macro's name (reading (c) for one call)
lib_rows = []
for needle, byname in [("(`[h = hits(/\\d+/)] & (h.hit: <5)`", "hits(/\\d+/) & (hits.hit: <5)"),
                       ("(`[h = hits(/\\d+/)] & occurs.none((h.hit: >= 5))`", "hits(/\\d+/) & occurs.none((hits.hit: >= 5))"),
                       ("(`[hits = occurrences(/\\d+/)] & (hits.hit: <5)`", "occurrences(/\\d+/) & (occurrences.hit: <5)"),
                       ("(`[hits = occurrences(/\\d+/)] & occurs.none((hits.hit: >= 5))`",
                        "occurrences(/\\d+/) & occurs.none((occurrences.hit: >= 5))")]:
    L0 = printed(NEW["library.md"], needle)
    Pn = safe_prog(byname)
    got = fmt(Pn, *modes_of(L0)) if Pn else "REFUSED"
    same = got == strip_annot(answer_part(L0))
    lib_rows.append(same)
    print("   `%s` against the printed line %s: %s" % (byname, needle, "the same answers" if same else "DIFFERS: " + got))
check("CASE1", P_name is not None and d_name == (0, 0, 0) and w_direct == 0 and all(lib_rows),
      "his `hits(/\\d+/) & (hits.hit: 3)` %s; against `[h = hits(/\\d+/)] & (h.hit: 3)` %s differing over %d texts; "
      "WHOLE against the direct \"last number is 3\" %s differing; the four printed library lines, the call "
      "labelled, give the same answers by the macro's name: %d of 4"
      % ("legal" if P_name else "REFUSED", d_name, len(POPH), w_direct, sum(lib_rows)))

print("== TWICE: reading (a), binding-prefix's two rules carried to a macro's name")
TW = 'occurrences(/\\d/) SEQ ";" SEQ occurrences(/\\d/)'
r_plain = refused(TW + ' & (occurrences.hit: "9")')
r_dollar = refused('[x = ' + TW + '] & ($occurrences.hit: "9")')
P_gq = safe_prog(TW + ' & some((occurrences.hit: "9"))')
POP9 = pop("9;1", 4)
both = (lambda t: ";" in t and "9" in t)                     # some hit 9 in EITHER call (any digit can be a hit)
w_gq = whole_ndiff(P_gq, both, POP9) if P_gq else -1
nine_first = P_gq.whole("9;1") if P_gq else None             # the 9 only in the first call's stretch
L_gq = None
if P_gq:
    L_gq = doc_line("Called twice, a group question reads every call: %s (`%s & some((occurrences.hit: \"9\"))`)"
                    % (fmt(P_gq, ["9;1", "1;9", "1;1"], "x;1 9;", "9;1 1;1 1;9"), TW), "call-prefix")
    print("   " + L_gq)
print("   plain read: %s" % r_plain)
check("TWICE", r_plain is not None and "label the part" in r_plain and w_gq == 0 and nine_first,
      "a plain read through `occurrences` called twice %s; the group question `some((occurrences.hit: \"9\"))` "
      "against the direct \"a `;` and a 9 anywhere\" %s differing over %d texts (`9;1` %s: the first call is read)"
      % ("refused, \"label the part\"" if r_plain and "label the part" in r_plain else "ACCEPTED", w_gq, len(POP9),
         "HOLDS" if nine_first else "FAILS"))

print("== RECORD: reading (b), the call-prefix record entry's two pasted lines, from the program text")
CPB = ["A := /(?<d>\\d)/", "B(rx) := /${rx}-(?<d>\\d)/"]
RL1 = rec_line("A.d <5 (A's own d): ")
RL2 = rec_line("c.d <5 (d as B(A) surfaces it: the last mention, B's): ")
rows = []
for RL, expr, label in [(RL1, "B(A) & (A.d: <5)", "A's own d, through the argument (case 2)"),
                        (RL2, "[c = B(A)] & (c.d: <5)", "d as the call surfaces it, the last mention (B's)")]:
    wh, sr, fa = rec_texts(RL)
    Pg = safe_prog(expr, CPB)
    got = fmt_rec_each(Pg, wh, sr, fa) if Pg else "REFUSED"
    same = got == rec_answer(RL)
    rows.append(same)
    print("   record line `%s` %s" % (RL[:22], "REPRODUCED by `%s`" % expr if same else "DIFFERS: " + got))
    if Pg:
        print("   " + doc_line("%s: %s (`%s`, A := `/(?<d>\\d)/`, B(rx) := `/${rx}-(?<d>\\d)/`)"
                             % (label, fmt(Pg, wh, sr, fa), expr), "call-prefix"))
own = (lambda t: re.fullmatch(r"(\d)-(\d)", t) is not None and int(t[0]) < 5)
last = (lambda t: re.fullmatch(r"(\d)-(\d)", t) is not None and int(t[2]) < 5)
POPD = pop("37-", 3)
wA = whole_ndiff(safe_prog("B(A) & (A.d: <5)", CPB), own, POPD)
wc = whole_ndiff(safe_prog("[c = B(A)] & (c.d: <5)", CPB), last, POPD)
check("RECORD", all(rows) and wA == 0 and wc == 0,
      "the record's two lines reproduced: %d of 2; WHOLE against the direct first digit / second digit under 5: "
      "%d, %d differing over %d texts" % (sum(rows), wA, wc, len(POPD)))

print("== BDOT: reading (c), `B.d` for a single call is `c.d`")
wh, sr, fa = rec_texts(RL2)
P_B = safe_prog("B(A) & (B.d: <5)", CPB)
POPB = pop("37-", 4)
dB = safe_ndiff(P_B, prog("[c = B(A)] & (c.d: <5)", CPB), POPB)
L_B = None
if P_B:
    L_B = doc_line("By the macro's name: %s (`B(A) & (B.d: <5)`, the same A and B)" % fmt(P_B, wh, sr, fa), "call-prefix")
    print("   " + L_B)
check("BDOT", P_B is not None and dB == (0, 0, 0) and L_B and fmt(P_B, wh, sr, fa) == rec_answer(RL2).replace(
    " / WHOLE `", ", `"), "`B(A) & (B.d: <5)` %s; against `[c = B(A)] & (c.d: <5)` %s differing over %d texts; "
      "its line equals the record's c.d line" % ("legal" if P_B else "REFUSED", dB, len(POPB)))

print("== CA: his statement \"[ c = B(A) ] does not allow c.A\"; the ground, the argument is the parameter")
r_ca = refused("[c = B(A)] & (c.A.d: <5)", CPB)
print("   `[c = B(A)] & (c.A.d: <5)`: %s" % r_ca)
check("CA", r_ca is not None, "`[c = B(A)] & (c.A.d: <5)` %s (the call's label holds no part named for the argument)"
      % ("refused" if r_ca else "ACCEPTED"))

print("== PAIR: reading (d), an argument used twice by the body, `A` written once in the caller")
PB2 = ["A := /(?<d>\\d)/", "pair(p) := /${p},${p}/"]
P_pair = safe_prog("pair(A) & (A.d: <5)", PB2)
lastp = (lambda t: re.fullmatch(r"\d,\d", t) is not None and int(t[2]) < 5)
POPP = pop("37,", 3)
wp = whole_ndiff(P_pair, lastp, POPP) if P_pair else -1
dpc = safe_ndiff(P_pair, prog("[c = pair(A)] & (c.d: <5)", PB2), pop("37,", 4))
r_low = refused("pair(A) & (A.d: <5)", PB2, argcount="lowered")
gq_pair = safe_prog("pair(A) & some((A.d: \"7\"))", PB2)
L_pair = None
if P_pair:
    L_pair = doc_line("An argument used twice by the body: %s (`pair(A) & (A.d: <5)`, A := `/(?<d>\\d)/`, pair(p) := "
                      "`/${p},${p}/`)" % fmt(P_pair, ["7,3", "3,7", "3,3"], "3,7 7,3", "7,3 3,7 1,2 9,9"), "call-prefix")
    print("   " + L_pair)
print("   counted per lowering instead: %s" % r_low)
check("PAIR", P_pair is not None and wp == 0 and dpc == (0, 0, 0) and r_low is not None and gq_pair.whole("7,3"),
      "`pair(A) & (A.d: <5)` %s; WHOLE against the direct \"the second digit under 5\" %d differing over %d texts; "
      "against `[c = pair(A)] & (c.d: <5)` %s; counted per lowering it is refused (%s); a group question reads both "
      "(`7,3` HOLDS some 7)" % ("legal" if P_pair else "REFUSED", wp, len(POPP), dpc, "yes" if r_low else "NO"))

print("== HITS2: reading (e), his second hits example, the record's two pasted lines, from the program text")
H_IN = "[h = hits(/\\d+/ & (0: <5))] & (h.hit: 3) & some((h.hit: 4))"
H_EV = "[h = hits(/\\d+/)] & occurs.none((h.hit: >= 5)) & (h.hit: 3) & some((h.hit: 4))"
HR1, HR2 = rec_line("inner test: "), rec_line("every number: ")
h_rows = []
for RL, expr, call, label in [(HR1, H_IN, "hits(/\\d+/ & (0: <5))", "His second example, a test inside the argument"),
                              (HR2, H_EV, "hits(/\\d+/)", "Every number tested after the call")]:
    wh, sr, fa = rec_texts(RL)
    Pg = prog(expr)
    got = fmt_rec_each(Pg, wh, sr, fa, ("h", call))
    same = got == rec_answer(RL)
    h_rows.append(same)
    print("   record line `%s` %s" % (RL[:12], "REPRODUCED" if same else "DIFFERS: " + got))
    print("   " + doc_line("%s: %s (`%s`)" % (label, fmt_doc_hits(Pg, wh, sr, fa, ("h", call)), expr), "lib/search/hits"))
POPN = pop("49 31", 4)
inner_d = (lambda t: bool(re.findall("[0-4]", t)) and re.findall("[0-4]", t)[-1] == "3" and "4" in re.findall("[0-4]", t))
nums = (lambda t: re.findall(r"\d+", t))
every_d = (lambda t: bool(nums(t)) and all(int(x) < 5 for x in nums(t)) and nums(t)[-1] == "3" and "4" in nums(t))
wi = whole_ndiff(prog(H_IN), inner_d, POPN)
we = whole_ndiff(prog(H_EV), every_d, POPN)
check("HITS2", all(h_rows) and wi == 0 and we == 0,
      "the record's two lines reproduced with their hit lists: %d of 2; WHOLE against the direct hits (inner: every "
      "digit 0-4; after: every number) %d, %d differing over %d texts" % (sum(h_rows), wi, we, len(POPN)))

print("== CLOSED: R-1, closed-argument ruled (a): `A.d` legal exactly where `d` is visible through the call")
CLB = ["A := /(?<d>\\d)/", "B(rx) := /${[_ = rx]}xx/"]
r_cl = refused("B(A) & (A.d: <5)", CLB)
r_clc = refused("[c = B(A)] & (c.d: <5)", CLB)
P_cl = safe_prog("B(A)", CLB)
cl_ctl = safe_ndiff(P_cl, Re(r"\dxx"), pop("3x", 4))
P_op = safe_prog("B(A) & (A.d: <5)", CPB)
wh, sr, fa = rec_texts(RL1)
L_vis = None
if P_op:
    L_vis = doc_line("Visible through the call: %s (`B(A) & (A.d: <5)`, A := `/(?<d>\\d)/`, B(rx) := `/${rx}-(?<d>\\d)/`)"
                     % fmt(P_op, wh, sr, fa), "closed-argument")
    print("   " + L_vis)
print("   closed: `B(A) & (A.d: <5)` with B(rx) := `/${[_ = rx]}xx/`: %s" % r_cl)
print("   closed: `[c = B(A)] & (c.d: <5)`: %s" % r_clc)
check("CLOSED", r_cl is not None and r_clc is not None and cl_ctl == (0, 0, 0) and P_op is not None
      and "modes: a compile error (`B(A) & (A.d: <5)`, A := `/(?<d>\\d)/`, B(rx) := `/${[_ = rx]}xx/`" in NEW["core.md"],
      "where B closes its argument (`[_ = rx]`) `A.d` %s and `c.d` %s, the call itself matching as `\\dxx` (%s "
      "differing over 31 texts); through an open B `A.d` legal, its line the record's A.d line; the compile-error "
      "line printed: %s" % ("refused" if r_cl else "ACCEPTED", "refused" if r_clc else "ACCEPTED", cl_ctl,
                            "yes" if "modes: a compile error (`B(A) & (A.d: <5)`" in NEW["core.md"] else "NO"))

print("== QUOTES: every owner sentence this lane prints, word for word in the record and in the documents")
QUOTES = [
    "call-prefix. case 1. yes use the macro name as shown to qualify the label. 2. i'd say A.d is legal there. i'm "
    "trying to figure out if B(A) would ever remove the d. its possible it changes the answer to go through [ c = B(A) "
    "] as B may defined d",
    "closed-arguments: i thought you'd lean to (a). what would A.d mean if d no longer was visible? also: [ c = B(A) ] "
    "does not allow c.A",
    "nice. critical is the @assert macros to test that it does what was intended",
    "help-captures: right. [h = hits(/\\d+/ & (0: <5)) ] & (h.hit: 3) & some((h.hit: 4))<5 and last hit is 3 and some "
    "hit is 4.",
    "C cannot see rx as its a binding variable not a label.",
    "closed-arguments: a",
]
if sabc("s8"):
    QUOTES[0] = QUOTES[0].replace("qualify", "name")
qbad = [q for q in QUOTES if ws(q) not in RECORD_WS]
qdoc = [q[:40] for q in QUOTES[:3] + QUOTES[5:] if ws(q) not in ws(ALLDOC)]
check("QUOTES", not qbad and not qdoc, "%d passages found in the record; missing: %s; this lane's four in the "
      "documents: %s" % (len(QUOTES) - len(qbad), [q[:40] for q in qbad] or "none", "all" if not qdoc else qdoc))

print("== MARKS: statuses and the statements moved")
core, lib = NEW["core.md"], NEW["library.md"]
if sabc("s9"):
    core = core.replace("[core/labels/paths/call-prefix]   ruled 2026-11-22", "[core/labels/paths/call-prefix]   open call-prefix 2026-11-22")
marks = {
    "call-prefix ruled": "[core/labels/paths/call-prefix]   ruled 2026-11-22" in core,
    "closed-argument ruled (R-1)": "[core/labels/paths/closed-argument]   ruled 2026-11-22" in core,
    "no 'not a prefix' statement": not re.search(r"not a prefix|is no prefix|never by the macro", core + lib),
    "the ruled statement": "`A.d` is legal in the caller exactly where `d` is visible through the call, and "
                                   "it reads `d` as it reaches the caller." in ws(core),
    "c.A in the paths piece": "does not allow c.A" in piece(core, "core/labels/paths"),
    "standard's line": "written before bound-condition (2026-11-22), which refuses a computed value bound alone; "
                       "restated when the standard library is designed" in ws(lib),
    "macro types d.year": "`d.year`" in piece(core, "core/operators/bindings/macro-types"),
    "errors index row": "the caller's `A.d` where the macro closes its argument's labels" in piece(core, "core/diagnostics/errors"),
    "no 'lean' left for case 2": "NOT RULED; the owner's lean" not in core,
    "assert remark": "critical is the @assert macros" in piece(lib, "lib/assert/assert"),
}
check("MARKS", all(marks.values()), "; ".join("%s %s" % (k, "yes" if v else "NO") for k, v in marks.items()))

print("== SCAN: predref's textual label-reference checker over every printed program span, this lane's LEFT list")
LEFT2 = dict(LEFT)
docs = dict(NEW)
if sabc("s10"):
    docs["core.md"] += "\nPlant: WHOLE `3` HOLDS / SEARCHED `3` `3`@0 / FIND-ALL `3` [`3`@0] (`B(A) & (d: <5)`)\n"
total, flagged = scan(docs)
extra = sorted(k for k in flagged if k not in LEFT2)
gone = sorted(k for k in LEFT2 if k not in flagged)
check("SCAN", not extra and not gone, "%d program spans checked; %d distinct spans read a label bare or through an "
      "unknown head, all on LEFT; not on LEFT: %s; on LEFT but no longer flagged: %s"
      % (total, len(flagged), extra or "none", gone or "none"))

print("== PREDREF: lane predref's model on the folded documents; which of its checks go red, each covered here")
env = dict(os.environ)
env.pop("PREDCALL_SABOTAGE", None)
if sabc("s11"):
    env["PREDREF_SABOTAGE"] = "s3"
pr = subprocess.run([sys.executable, "-I", "-B", PR], capture_output=True, text=True, env=env, timeout=280)
red = sorted(set(re.findall(r"^FAIL (\w+):", pr.stdout, re.M)))
print("   " + pr.stdout.strip().split("\n")[-1])
for ln in pr.stdout.split("\n"):
    if ln.startswith("FAIL "):
        print("   " + ln[:300])
EXPECT_RED = ["MARKS"]
check("PREDREF", red == EXPECT_RED, "red: %s (expected %s: its MARKS looks for the call-prefix piece still open, "
      "covered by MARKS here, which looks for it ruled; its other 7 checks stay green on the folded documents)"
      % (red, EXPECT_RED))

print("== DOC: every formatted line verbatim in the documents")
missing = []
for i, (tag, L) in enumerate(LINES):
    if sabc("s12") and i == 0:
        L = L.replace("WHOLE `", "WHOLE `x", 1)
    if L not in ALLDOC:
        missing.append((tag, L[:90]))
check("DOC", not missing, "%d lines; missing: %s" % (len(LINES), missing or "none"))

nf = sum(1 for _, ok in RESULTS if not ok)
print("predcall_model: %d checks, %d failed%s" % (len(RESULTS), nf,
                                                 ("" if not nf else " (%s)" % ", ".join(n for n, ok in RESULTS if not ok))))
sys.exit(1 if nf else 0)
