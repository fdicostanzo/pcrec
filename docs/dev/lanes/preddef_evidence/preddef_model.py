#!/usr/bin/env python3
# Lane preddef (2026-11-22): the evidence for folding the owner's ruling "default-export: protected" (record
# "2026-11-22 OWNER RULING — default-export: protected (a part used alone is available inside the binding and is not
# exported)") into the predicate documents, and the manager's readings (a)..(h) of the lane brief tested.
# DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD. Lane predfix82's model is LOADED unchanged: predfix82_model.py is executed up to its line "the checks" (it
# loads predcall's, which loads predref's, which loads predbound's lowerer and matcher). Its plants are cleared.
# The RULE below then replaces, in the loaded engine (the names resolve at call time in one namespace):
#   PROTECT  a part USED ALONE in a binding's body (a bound name or a pattern macro's call written as a sequence
#            operand, in a hole or as an `&` operand, under no part label) keeps its labels inside that body
#            (through its own name, `A.h`) and exports none of them: its groups lose every scope outside the body,
#            as under `[_A = A]` with the local name `A` (reading (a)). At the top-level program nothing is outside.
#            A part label `[x = ..]` (and everything written under it) is NOT a use alone: its part's exported
#            labels pass out through it as before (statement 3 for a labelled part).
#   ARGS     an ARGUMENT the macro body uses alone (`${rx}`) is not exported by the call: neither the call's name
#            (`B.d`) nor a label on the call (`c.d`) reaches its labels (reading (e)). The caller's own `A.d` is
#            open argument-default: ARGDEF "local" (the caller's local read of its own part, legal) or "error"
#            (not visible, a compile error). Both are run; neither is applied. An argument written in place stays
#            the caller's own text under both (a reading, call-prefix's "An argument written in place").
#   VISIBLE  a path read INSIDE a binding's body to a label not visible there is the same compile error the loaded
#            engine raised only at the top-level program (a label not visible through its source).
#   LIST     export-list (ruled, rulings file R-1): a part label whose left side is a named list, `[(=year) = A]`,
#            `[(y = year) = A]`, `[(=) = A]`, `[(=, _ = month) = A]`: the binding takes the listed EXPORTED labels of
#            the part as labels of its own (written here: exported, read bare inside) and nothing else; no path name.
#   SETAND   a fix to the loaded engine's set test: `A & A` and `A & /../` are patterns, not sets.
# The old engine (PREDDEF_ENGINE=old) restores predfix82's lower_atom, use_definition, prefix_parts and prog.
# KNOWN LIMIT (EVID-4, planned, not fixed here): a NULLABLE loop body past the minimum (PCRE's trailing empty pass)
# is not modelled: the loaded matcher refuses an empty pass once the minimum is met. The check NULLABLE greps every
# program this model's checks run for one and fails if found.
#
# Run (W = the worktree; any cwd):  timeout 900 python3 -I -B W/docs/dev/lanes/preddef_evidence/preddef_model.py
# The model EXITS NON-ZERO when any check fails; its verdict is its LAST LINE.
# PREDDEF_ENGINE=old runs the loaded engine WITHOUT the rule (SWEEP's control; prints one table and exits).
# PREDDEF_SABOTAGE=sN (one at a time): a deliberately wrong rule or fact; its target check must FAIL.
# CHECKS and PLANTS (check: its plant):
#   CONTROL s7 (python `re` oracle widened to `\d!?`)   PROTECT s1 (PROTECT off)   EXAMPLE s8 (oracle: `7` also holds)
#   ANALOGY s9 (`[_ = A]` row: local read legal)        MACRO s2 (ARGS prefix mask off: the call exports the argument)
#   AWAITS s3 (candidate "error" closes nothing)        UNMARKED s21 (one line's "(awaits argument-default)" dropped)
#   ARRAY s10 (oracle: B's h is the first)              NESTED2 s11 (oracle: the last digit 3)
#   LIBRARY s12 (oracle: two characters)                VISIBLE s4 (VISIBLE off, in a body and at the top)
#   SETAND s5 (the loaded set test back)                LIST s6 (the list also keeps the part's own labels)
#   CAPTEXP s13 (a capture `q` invented)                ATOMIC s22 (ARGS prefix mask off for this check)
#   SCAN s20 (a printed line reading `p2.h`, p2 := `/${A}!/`)   NULLABLE s14 (a nullable loop body run)
#   SUCCESSOR s15 (one of predfix82's reds undeclared)  SWEEP s16 (a printed program re-spelled to read an unexported
#   label: `pub := A SEQ "!"`, then `pub.h`)            QUOTES s17 (a quote altered)   MARKS s18   DOC s19
import os
import re
import subprocess
import sys

HERE3 = os.path.dirname(os.path.abspath(__file__))
PF = os.path.join(HERE3, "..", "predfix82_evidence", "predfix82_model.py")
SABD = set(x for x in os.environ.get("PREDDEF_SABOTAGE", "").split(",") if x)
ENGINE_D = os.environ.get("PREDDEF_ENGINE", "new")
for v in ("PREDFIX82_SABOTAGE", "PREDFIX82_ENGINE", "PREDCALL_SABOTAGE", "PREDREF_SABOTAGE", "PREDBOUND_SABOTAGE"):
    os.environ.pop(v, None)


def sd(n):
    return n in SABD


_src3 = open(PF, encoding="utf-8").read()
_cut3 = re.search(r"^# =+ the checks$", _src3, re.M).start()
exec(compile(_src3[:_cut3], PF, "exec"), globals())         # noqa: S102  (predfix82's definitions, unchanged)
SAB82.clear()
SABC.clear()
SABR.clear()
SAB.clear()

OLD82 = dict(lower_atom=lower_atom, use_definition=use_definition, prefix_parts=prefix_parts, Ctx_sub=Ctx.sub,
             prog=prog)

# ================================================================== the RULE (lane preddef)
ARGDEF = ["local"]            # open argument-default: "local" | "error"
ARG_PARTS = set()             # part strings an argument used alone in a body left; no later prefix takes them
Ctx.labelled = False          # True while lowering under a part label written in the same definition
_ctx_sub0 = Ctx.sub


def _ctx_sub(self, **kw):
    c = _ctx_sub0(self, **kw)
    c.labelled = self.labelled
    return c


_base_binds_d = base_binds


def base_binds():                                            # noqa: F811
    _base_binds_d()
    ARG_PARTS.clear()


def all_parts(text):
    out = set()
    for g in GROUP_NAME.findall(text):
        out |= set(g.split(";"))
    for n in re.findall(r"\$\{#(\d+)\}", text):
        nd = NODES.get(int(n))
        if nd and nd[0] == "setv":
            out |= set(nd[1].split(";"))
    return out


_prefix_parts_d = prefix_parts


def prefix_parts(text, prefix, at, vis, kind):               # noqa: F811
    """As predfix82's; a part an argument used alone left (ARG_PARTS) is never prefixed again (ARGS)."""
    if not ARG_PARTS or sd("s2"):
        return _prefix_parts_d(text, prefix, at, vis, kind)
    hide = {}

    def mask(mm):
        ps = mm.group(1).split(";")
        keep = [p for p in ps if p not in ARG_PARTS]
        held_ = [p for p in ps if p in ARG_PARTS]
        if not held_:
            return mm.group(0)
        k = "zz%d" % len(hide)
        hide[k] = held_
        return "(?<%s>" % ";".join(keep + ["%s@hidden" % k])
    t2 = GROUP_NAME.sub(mask, text)
    t3 = _prefix_parts_d(t2, prefix, at, vis, kind)

    def unmask(mm):
        ps = mm.group(1).split(";")
        out = []
        for p in ps:
            base, _, sc = p.partition("@")
            if sc == "hidden" and base in hide:
                out += hide[base]
            elif sc == "hidden" or base.split(".")[-1] in hide:
                continue
            else:
                out.append(p)
        return "(?<%s>" % ";".join(out)
    return GROUP_NAME.sub(unmask, t3)


_lower_atom_d = lower_atom


def is_part_label(e):
    return re.fullmatch(r"\[(\w*) = (.*)\]([+*?]?)", e, re.S) is not None


LISTPL = re.compile(r"\[\(([^()]*)\) = (.*)\]([+*?]?)", re.S)


def list_pairs(lst):
    """`=year` -> [("year", "year")]; `y = year`; `=` alone is ALL; `_ = month` leaves month out."""
    pairs, allx, out = [], False, set()
    for it in [x.strip() for x in lst.split(",")]:
        if it == "=":
            allx = True
        elif it.startswith("="):
            pairs.append((it[1:].strip(), it[1:].strip()))
        else:
            new, _, old = [x.strip() for x in it.partition("=")]
            if new == "_":
                out.add(old)
            else:
                pairs.append((new, old))
    return pairs, allx, out


def lower_list(mm, ctx):
    """LIST (export-list, ruled): `[(=year) = isodate]`: the binding takes the listed EXPORTED labels of the part as
    labels of its own (written here: exported, read bare inside) and nothing else of the part; no path name."""
    pairs, allx, out = list_pairs(mm.group(1))
    lc = ctx.sub()
    lc.labelled = True
    inner = lower(mm.group(2), lc)
    here = set(ctx.scopes)
    exported = set(b for b in surfaced(inner, ctx.cur) if "." not in b and not private(b))
    for new, old in pairs:
        if old not in exported:
            raise CompileError("`%s` is not a label the part exports (export-list: only an exported label is listed)"
                               % old)
    names = list(pairs)
    if allx:
        names += [(b, b) for b in sorted(exported) if b not in out and (b, b) not in pairs]
    ctx.held.update(n for n, _ in names)

    def fix(ps):
        keep = [(b, sc) for b, sc in ps if not (set(sc) & here)]
        if sd("s6"):
            keep += [(b, sc) for b, sc in ps if set(sc) & here and "." not in b]
        for b, sc in ps:
            if set(sc) & here and "." not in b:
                for new, old in names:
                    if old == b:
                        keep.append((new, list(ctx.scopes)))
        return keep

    def rep(m2):
        ps = fix(parts_of(m2.group(1)))
        return "(?<%s>" % join_parts(ps) if ps else "(?:"
    for n in re.findall(r"\$\{#(\d+)\}", inner):
        nd = NODES[int(n)]
        if nd[0] == "setv":
            ps = fix(parts_of(nd[1]))
            NODES[int(n)] = ("setv", join_parts(ps) if ps else "_closed@none", nd[2])
    return "(?:%s)%s" % (GROUP_NAME.sub(rep, inner), mm.group(3))


_own_labels_d = own_labels


def own_labels(text):                                        # noqa: F811
    """The labels a definition writes, the names a list on a part label takes included (export-list)."""
    out = _own_labels_d(text)
    for mm in LISTPL.finditer(text):
        pairs, allx, _ = list_pairs(mm.group(1))
        out |= set(n for n, _ in pairs)
    for mm in re.finditer(r"\[\(([^()]*)\) = ", text):
        pairs, _, _ = list_pairs(mm.group(1))
        out |= set(n for n, _ in pairs)
    return out


def lower_atom(expr, ctx):                                   # noqa: F811
    e = expr.strip()
    mm = LISTPL.fullmatch(e)
    if mm:
        return lower_list(mm, ctx)
    if is_part_label(e):                                     # a labelled part: its contents pass out through it
        lc = ctx.sub()
        lc.labelled = True
        return _lower_atom_d(e, lc)
    alone = not ctx.labelled and ctx.cur != "top"
    if e in ctx.params:                                      # ARGS: an argument used alone in the body
        text = _lower_atom_d(e, ctx)
        if not ctx.labelled:
            ARG_PARTS.update(all_parts(text))
            if ARGDEF[0] == "error" and not sd("s3"):
                caller = ctx.params[e][1]
                text = close_parts(text, caller.scopes)
        return text
    call = parse_call(e)
    pattern_use = ((e in BINDS and not is_cond(BINDS[e]) and not is_set_body(BINDS[e])) or
                   (call and call[0] in MACROS and re.fullmatch(r"[A-Za-z]\w*", call[0])
                    and not is_cond(pick_macro(*call)[1])))
    text = _lower_atom_d(e, ctx)
    if pattern_use and alone and not sd("s1"):              # PROTECT
        text = close_parts(text, ctx.scopes[:-1])
    return text


_use_definition_d = use_definition


def use_definition(body, ctx, dname, params=None, mark=True):    # noqa: F811
    """VISIBLE: a path the body reads must be visible in the body (as prog checks at the top-level program)."""
    sc = "s%d" % (COUNTER[0] + 1)
    start = len(NAMED)
    saved = ctx.labelled
    text = _use_definition_d(body, ctx, dname, params, mark)
    if not sd("s4"):
        seen = surfaced(text, sc)
        for scope, nm in NAMED[start:]:
            if scope == sc and "." in nm and nm not in seen:
                raise CompileError("`%s`: `%s` is not visible through `%s` in %s (a compile error, "
                                   "core/labels/export)" % (nm, nm.split(".", 1)[1], nm.split(".")[0], dname))
    ctx.labelled = saved
    return text


_is_set_body_d = is_set_body


def is_set_body(body, _seen=()):                             # noqa: F811
    """SETAND: an `&` chain with a pattern operand (a literal, a part label, a bound PATTERN) is a pattern, not a
    set (the loaded test read `B := A & A` and `A & /(?<b>\\d)/` as sets and dropped the binding's use)."""
    if not sd("s5"):
        for op in split_top(body.strip(), " & "):
            op = op.strip()
            if op.startswith("/") or op.startswith("[") or op.startswith('"'):
                if len(split_top(body.strip(), " & ")) > 1:
                    return False
            if op in BINDS and op not in _seen and len(split_top(body.strip(), " & ")) > 1:
                b = BINDS[op]
                if not is_cond(b) and not is_set_body(b, _seen + (op,)):
                    return False
    return _is_set_body_d(body)


_prog_d = prog


def prog(expr, binds=(), **opts):                            # noqa: F811
    """VISIBLE at the top-level program: a bare name read there must be one some group there sets (a label of an
    argument the body uses alone is not, under argument-default's candidate "error")."""
    Pg = _prog_d(expr, binds, **opts)
    if not sd("s4"):
        seen = surfaced(Pg.rx, "top")
        for sc, nm in NAMED:
            if sc == "top" and "." not in nm and not nm.isdigit() and nm not in seen:
                raise CompileError("`%s`: no group visible here sets it (a compile error, core/labels/export)" % nm)
    return Pg


if ENGINE_D == "old":
    globals().update(OLD82)
else:
    Ctx.sub = _ctx_sub

if ENGINE_D == "old":
    for f, ln, line_, a, pt, tail in sweep_lines():
        st, got = sweep_one(line_, a, pt, tail)
        print("SW\t%s\t%d\t%s\t%s" % (f, ln, st, got if st in ("same", "DIFF") else ""))
    sys.exit(0)

# ================================================================== the checks
RESULTS = []


def check(name, ok, detail=""):                              # noqa: F811
    RESULTS.append((name, bool(ok)))
    print("%s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def qref(expr, binds=()):
    try:
        prog(expr, list(binds))
        return None
    except CompileError as e:
        return str(e)


def tryp(expr, binds=()):
    try:
        return prog(expr, list(binds))
    except CompileError:
        return None


def wdiff(Pg, pred, texts):
    return sum(1 for t in texts if Pg.whole(t) != pred(t)) if Pg is not None else -1


def dline(label, expr, bt, Pg, wh, sr, fa, tag, tail=""):
    L = "%s%s (`%s`%s)%s" % ((label + ": ") if label else "", fmt(Pg, wh, sr, fa), expr, bt, tail)
    return doc_line(L, tag)


def bt_of(binds):
    out = ""
    for b in binds:
        h, _, d = b.partition(" := ")
        out += ", %s := `%s`" % (h, d)
    return out


A_H = "A := /(?<h>\\d)/"
A_D = "A := /(?<d>\\d)/"
A_A = "A := /(?<a>\\d)/"
QDIG = pop("37!", 3)

print("== CONTROL: the loaded matcher against python `re`")
c1 = ndiff(answers(prog('"ab" | "a"'), pop("ab;", 4)), answers(Re(r"ab|a"), pop("ab;", 4)))
c2 = ndiff(answers(prog("p2", ["p2 := /${A}!/", A_H]), QDIG), answers(Re(r"\d!" if not sd("s7") else r"\d!?"), QDIG))
check("CONTROL", (c1, c2) == ((0, 0, 0),) * 2, "differing (WHOLE, SEARCHED, FIND-ALL): `\"ab\" | \"a\"` %s; "
      "`/${A}!/` against `\\d!` %s over %d texts" % (c1, c2, len(QDIG)))

print("== PROTECT: readings (a), (b), (c): a part used alone is seen inside and not exported (statement 3)")
lt5 = lambda t: re.fullmatch(r"\d!", t) is not None and int(t[0]) < 5      # noqa: E731
P_in = tryp("p2", ["p2 := /${A}!/ & (A.h: <5)", A_H])
P_in2 = tryp("p2", ["p2 := A SEQ \"!\" & (A.h: <5)", A_H])
r_o1 = qref("p2 & (p2.h: <5)", ["p2 := /${A}!/", A_H])
r_o2 = qref("p2 & (p2.h: <5)", ["p2 := A SEQ \"!\"", A_H])
r_o3 = qref("p2 & (p2.A.h: <5)", ["p2 := A SEQ \"!\"", A_H])
PUB = ["pub := [a = A] SEQ \"!\"", A_H]
P_pn, P_pp = tryp("pub & (pub.h: <5)", PUB), tryp("pub & (pub.a.h: <5)", PUB)
r_6 = qref("p6 & (p6.h: <5)", ["p6 := [_a = A] SEQ \"!\"", A_H])
if P_in is not None:
    dline("Used alone, inside", "p2", ", p2 := `/${A}!/ & (A.h: <5)`, A := `/(?<h>\\d)/`", P_in, ["3!", "7!"], "7! 3!",
          "3! 7! 4!", "core/labels/export")
wp = [wdiff(x, lt5, QDIG) for x in (P_in, P_in2, P_pn, P_pp)]
check("PROTECT", wp == [0, 0, 0, 0] and all((r_o1, r_o2, r_o3, r_6)),
      "inside `/${A}!/` and `A SEQ \"!\"` with `(A.h: <5)` and a labelled part read `pub.h`, `pub.a.h`: whole answers "
      "differing from `[0-4]!` %s over %d texts; from outside refused: `p2.h` (hole) %s, `p2.h` (sequence) %s, "
      "`p2.A.h` %s, `p6.h` under `[_a = A]` %s" % (wp, len(QDIG), bool(r_o1), bool(r_o2), bool(r_o3), bool(r_6)))
print("   refusal: %s" % r_o1)

print("== EXAMPLE: his `B := A & A`, `C := B & (B.a: 9)`, \"here B.a is always an error\" (reading (g))")
BAA = ["B := A & A", A_A]
r_g1 = qref("C", ["C := B & (B.a: 9)"] + BAA)
r_g2 = qref("C", ["C := B & some((B.a: \"9\"))"] + BAA)
r_g3 = qref("B & (B.a: 9)", BAA)
r_g4 = qref("B & some((B.a: \"9\"))", BAA)
BXY = ["B := [x = A] & [y = A]", A_A]
P_x, P_y = tryp("B & (B.x.a: 9)", BXY), tryp("B & (B.y.a: 9)", BXY)
D9 = pop("97x", 3)
is9 = lambda t: t == "9"                                     # noqa: E731
if sd("s8"):
    is9 = lambda t: t in ("9", "7")                          # noqa: E731
for lab, Pg_ in (("x", P_x), ("y", P_y)):
    if Pg_ is not None:
        dline("Each use labelled, " + lab, "B & (B.%s.a: 9)" % lab, bt_of(BXY), Pg_, ["9", "7"], "x7 9", "9 7 99 9",
              "core/labels/export/flat-read-outside")
check("EXAMPLE", all((r_g1, r_g2, r_g3, r_g4)) and wdiff(P_x, is9, D9) == 0 and wdiff(P_y, is9, D9) == 0,
      "refused: at C plain %s, group question %s; at the top plain %s, group question %s; `B.x.a`, `B.y.a` whole "
      "answers differing from `9`: %d, %d over %d texts" % (bool(r_g1), bool(r_g2), bool(r_g3), bool(r_g4),
                                                           wdiff(P_x, is9, D9), wdiff(P_y, is9, D9), len(D9)))
print("   refusal at C: %s" % r_g1)

print("== ANALOGY: his four forms, each read locally and from outside (the table's rows; reading (d))")
AN = [("[a = A]", "a.h", True, "pub.h", True), ("[_a = A]", "_a.h", True, "pub.h", False),
      ("A", "A.h", True, "pub.h", False), ("[_ = A]", "A.h", False, "pub.h", False),
      ("[A = A]", "A.h", True, "pub.A.h", True)]
if sd("s9"):
    AN[3] = ("[_ = A]", "A.h", True, "pub.h", False)
an_bad = []
for form, loc, lok, out, ook in AN:
    gl = tryp("pub", ["pub := %s SEQ \"!\" & (%s: <5)" % (form, loc), A_H]) is not None
    go = tryp("pub & (%s: <5)" % out, ["pub := %s SEQ \"!\"" % form, A_H]) is not None
    print("   %-9s local `%s` %s, outside `%s` %s" % (form, loc, "legal" if gl else "refused", out,
                                                      "legal" if go else "refused"))
    if (gl, go) != (lok, ook):
        an_bad.append(form)
check("ANALOGY", not an_bad, "%d forms (the four rows and his `[=A]` read as `[A = A]`), local and outside read "
      "against the table: differing %s" % (len(AN), an_bad or "none"))

print("== MACRO: reading (e): a call exports what its body's text writes; an argument used alone is not exported")
BX = ["B(rx) := /${rx}xx/", A_D]
r_m1, r_m2 = qref("B(A) & (B.d: <5)", BX), qref("[c = B(A)] & (c.d: <5)", BX)
BO = ["B(rx) := /${rx}-(?<d>\\d)/", A_D]
P_c = tryp("[c = B(A)] & (c.d: <5)", BO)
E3 = ["B(rx) := /${[dd = rx]}xx/", "A := [d = rx.digits]"]
P_e3 = tryp("B(A) & (B.dd.d: <100)", E3)
D2 = pop("37-", 3)
q_own = lambda t: re.fullmatch(r"\d-\d", t) is not None and int(t[2]) < 5         # noqa: E731
X3 = ["42xx", "100xx", "042xx", "7xx", "x"]
e3 = lambda t: re.fullmatch(r"(0|[1-9]\d?)xx", t) is not None                   # noqa: E731
if P_c is not None:
    dline("d as the call exports it, the body's own", "[c = B(A)] & (c.d: <5)", bt_of([A_D, BO[0]]), P_c,
          ["7-3", "3-7", "3-3"], "3-7 7-3", "7-3 3-7 1-2 9-9", "core/labels/paths/call-prefix")
if P_e3 is not None:
    dline("Through a part label in the body", "B(A) & (B.dd.d: <100)", bt_of([E3[1], E3[0]]), P_e3,
          ["42xx", "100xx", "042xx"], "x100xx 42xx", "100xx 42xx 7xx 300xx", "core/labels/paths/argument-default")
check("MACRO", r_m1 and r_m2 and wdiff(P_c, q_own, D2) == 0 and wdiff(P_e3, e3, X3) == 0,
      "`/${rx}xx/`: `B.d` refused %s, `c.d` refused %s; `/${rx}-(?<d>\\d)/`: `c.d` reads the body's own d, differing "
      "%d over %d texts; his example 3 `B.dd.d` differing %d over %d" % (bool(r_m1), bool(r_m2), wdiff(P_c, q_own, D2),
                                                                         len(D2), wdiff(P_e3, e3, X3), len(X3)))
print("   refusal: %s" % r_m1)

print("== SWEEP-TABLE: every printed three-mode line under argument-default's two candidates")
ROWS = {}
for ad in ("local", "error"):
    ARGDEF[0] = ad
    for f, ln, line_, a, pt, tail in sweep_lines():
        ROWS.setdefault((f, ln), [line_, a, pt, tail, {}])[4][ad] = sweep_one(line_, a, pt, tail)
ARGDEF[0] = "local"
envo = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE")}
envo["PREDDEF_ENGINE"] = "old"
oo = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__)], capture_output=True, text=True,
                    env=envo, timeout=600).stdout
OLD_SW = {}
for l_ in oo.split("\n"):
    if l_.startswith("SW\t"):
        _, f_, ln_, st_, got_ = l_.split("\t", 4)
        OLD_SW[(f_, int(ln_))] = (st_, got_)
print("   %d printed lines; the old engine (predfix82's, without the rule) ran %d" % (len(ROWS), len(OLD_SW)))

print("== AWAITS: every line marked \"(awaits argument-default)\": the printed answers under (local), refused "
      "under (error) where its program reads the argument's label")
aw_bad, aw_n, aw_noread = [], 0, []
for k, (line_, a, pt, tail, st) in sorted(ROWS.items()):
    if "(awaits argument-default)" not in line_:
        continue
    aw_n += 1
    reads = re.search(r"\(\w[\w.]*: ", pt) is not None
    unmod = not reads and st["local"][0] == st["error"][0] == OLD_SW.get(k, ("?",))[0] != "same"
    if (st["local"][0] != "same" and not unmod) or (reads and st["error"][0] != "REFUSED"):
        aw_bad.append((k, st["local"][0], st["error"][0]))
    if not reads:
        aw_noread.append(k)
    print("   %s:%d local %s, error %s%s" % (k[0], k[1], st["local"][0], st["error"][0],
                                            "" if reads else " (no read in the program: its label annotation awaits%s)"
                                            % ("; a library body this engine does not model, the old engine alike"
                                               if unmod else "")))
P_l = tryp("B(A) & (A.d: <5)", BX)
ARGDEF[0] = "error"
r_le = qref("B(A) & (A.d: <5)", BX)
ARGDEF[0] = "local"
x3 = lambda t: re.fullmatch(r"[0-4]xx", t) is not None                          # noqa: E731
if P_l is not None:
    dline("(local)", "B(A) & (A.d: <5)", bt_of([A_D, BX[0]]), P_l, ["3xx", "7xx"], "7xx 3xx", "3xx 7xx 4xx",
          "core/labels/paths/argument-default")
check("AWAITS", aw_n and not aw_bad and wdiff(P_l, x3, pop("37x", 3)) == 0 and r_le,
      "%d marked lines; not (local same, error refused): %s; %d with no read; the piece's own line: (local) differing "
      "%d, (error) refused %s" % (aw_n, aw_bad or "none", len(aw_noread), wdiff(P_l, x3, pop("37x", 3)), bool(r_le)))

print("== UNMARKED: every unmarked printed line answers alike under both candidates (none silently awaits)")
if sd("s21"):                                    # plant: one line's mark dropped
    k_ = next(k for k, v in ROWS.items() if "(awaits argument-default)" in v[0] and v[4]["error"][0] == "REFUSED")
    ROWS[k_][0] = ROWS[k_][0].replace("(awaits argument-default)", "")
um_bad = [(k, st["local"][0], st["error"][0]) for k, (line_, a, pt, tail, st) in ROWS.items()
          if "(awaits argument-default)" not in line_ and not line_.startswith("(local): ")
          and st["local"][0] == "same" and st["error"][0] != "same"]
check("UNMARKED", not um_bad, "%d unmarked lines reproduced under (local); moved under (error): %s" %
      (sum(1 for v in ROWS.values() if "(awaits" not in v[0] and v[4]["local"][0] == "same"), um_bad or "none"))

print("== ARRAY: reading (f): inside a binding a part used alone has its settings seen (array-in-piece)")
AR_in = tryp("B2", ["B2 := A SEQ /;(?<h>\\d)/ & some((A.h: \"7\"))", A_H])
AR_out = tryp("B & some((B.h: \"7\"))", ["B := A SEQ /;(?<h>\\d)/", A_H])
r_ar = qref("B & some((B.A.h: \"7\"))", ["B := A SEQ /;(?<h>\\d)/", A_H])
DA = pop("71;", 3)
f_in = lambda t: re.fullmatch(r"\d;\d", t) is not None and t[0] == "7"          # noqa: E731
f_out = lambda t: re.fullmatch(r"\d;\d", t) is not None and t[2] == ("7" if not sd("s10") else "1")  # noqa: E731
check("ARRAY", wdiff(AR_in, f_in, DA) == 0 and wdiff(AR_out, f_out, DA) == 0 and r_ar,
      "inside `some((A.h: \"7\"))` differing %d; outside `some((B.h: \"7\"))` reads B's own h only, differing %d, over "
      "%d texts; `B.A.h` from outside refused %s" % (wdiff(AR_in, f_in, DA), wdiff(AR_out, f_out, DA), len(DA),
                                                    bool(r_ar)))

print("== NESTED2: binding-prefix's nested use: `X.d.h` through X's part label, `X.D.h` refused (D used alone in X)")
ND = ["D := /(?<h>\\d)+/", "X := [d = D] SEQ \"!\""]
P_nd = tryp("D SEQ \";\" SEQ X & (X.d.h: \"4\")", ND)
r_nd = qref("D SEQ \";\" SEQ X & (X.D.h: \"4\")", ["D := /(?<h>\\d)+/", "X := D SEQ \"!\""])
DN = pop("14;!", 5)
nd_p = lambda t: re.fullmatch(r"\d+;\d+!", t) is not None and t[-2] == ("4" if not sd("s11") else "3")  # noqa: E731
if P_nd is not None:
    dline("X's use, labelled in X", "D SEQ \";\" SEQ X & (X.d.h: \"4\")", bt_of(ND), P_nd, ["14;23!", "12;34!", "23;14!"],
          "12;34! 14;24!", "14;23! 12;34! 4;14!", "core/labels/paths/binding-prefix")
check("NESTED2", wdiff(P_nd, nd_p, DN) == 0 and r_nd, "`X.d.h` differing from `\\d+;\\d*4!` %d over %d texts; "
      "`X.D.h` refused %s" % (wdiff(P_nd, nd_p, DN), len(DN), bool(r_nd)))

print("== LIBRARY: reading (h): `length` uses `chars` alone, so a call exports no `ch`")
LB = ["length(S) := chars & (count((chars.ch: /(?s:.)/)): S)", "chars := ([ch = /(?s:.)/])*"]
P_len = tryp("length(3)", LB)
r_l1, r_l2 = qref("length(3) & (length.ch: \"a\")", LB), qref("length(3) & (length.chars.ch: \"a\")", LB)
P_ch = tryp("chars & (chars.ch: \"a\")", LB[1:])
DL3 = pop("ab", 4)
l3 = lambda t: len(t) == (3 if not sd("s12") else 2)                          # noqa: E731
ch_a = lambda t: len(t) > 0 and t[-1] == "a"                                   # noqa: E731
check("LIBRARY", wdiff(P_len, l3, DL3) == 0 and r_l1 and r_l2 and wdiff(P_ch, ch_a, DL3) == 0,
      "`length(3)` differing from three characters %d over %d texts; `length.ch` refused %s, `length.chars.ch` refused "
      "%s; `chars.ch` (chars's own part label, the last) differing %d" % (wdiff(P_len, l3, DL3), len(DL3), bool(r_l1),
                                                                           bool(r_l2), wdiff(P_ch, ch_a, DL3)))

print("== VISIBLE: a path read inside a body to a label not visible there is a compile error, as at the top")
r_v1 = qref("C", ["C := B SEQ \"!\" & (B.h: <5)", "B := A SEQ \"-\"", A_H])
r_v2 = qref("B SEQ \"!\" & (B.h: <5)", ["B := A SEQ \"-\"", A_H])
P_v3 = tryp("C", ["C := B SEQ \"!\" & (B.A.h: <5)", "B := [A = A] SEQ \"-\"", A_H])
check("VISIBLE", r_v1 and r_v2 and P_v3 is not None, "inside C `B.h` refused %s; at the top refused %s; `B.A.h` through "
      "B's part label legal %s" % (bool(r_v1), bool(r_v2), P_v3 is not None))
print("   refusal inside: %s" % r_v1)

print("== SETAND: `B := A & A` and `A & /../` are patterns, not sets (a fix to the loaded engine's set test)")
check("SETAND", not is_set_body("A & A") and not is_set_body("A & /(?<b>\\d)/") and is_set_body("<5"),
      "`A & A` a set %s, `A & /(?<b>\\d)/` a set %s, `<5` a set %s" % (is_set_body("A & A"),
                                                                      is_set_body("A & /(?<b>\\d)/"), is_set_body("<5")))

print("== LIST: export-list (R-1): `[(=year) = isodate]` takes the listed labels only")
ISO = "isodate := [year = /\\d{4}/] SEQ \"-\" SEQ [month = /\\d\\d/] SEQ \"-\" SEQ [day = /\\d\\d/]"
DT = "date := [(=year) = isodate] SEQ \"!\""
P_ly = tryp("date & (date.year: >= 2000)", [DT, ISO])
r_lm = qref("date & (date.month: \"01\")", [DT, ISO])
r_lp = qref("date & (date.isodate.month: \"01\")", [DT, ISO])
P_lr = tryp("date & (date.y: >= 2000)", ["date := [(y = year) = isodate] SEQ \"!\"", ISO])
r_lr = qref("date & (date.year: >= 2000)", ["date := [(y = year) = isodate] SEQ \"!\"", ISO])
P_la = tryp("date & (date.month: \"01\")", ["date := [(=) = isodate] SEQ \"!\"", ISO])
DB1 = "date := [(=, _ = month) = isodate] SEQ \"!\""
P_lb, r_lb = tryp("date & (date.day: \"02\")", [DB1, ISO]), qref("date & (date.month: \"01\")", [DB1, ISO])
P_li = tryp("date", ["date := [(=year) = isodate] SEQ \"!\" & (year: >= 2000)", ISO])
r_lx = qref("date", ["date := [(=hour) = isodate] SEQ \"!\"", ISO])
DTS = ["2025-01-02!", "1999-01-02!", "2001-12-31!", "1999-02-03!", "2025-02-02!", "2025-01-02", "x"]
ok_y = lambda t: re.fullmatch(r"\d{4}-\d\d-\d\d!", t) is not None and int(t[:4]) >= 2000   # noqa: E731
ok_m = lambda t: re.fullmatch(r"\d{4}-01-\d\d!", t) is not None                          # noqa: E731
ok_d = lambda t: re.fullmatch(r"\d{4}-\d\d-02!", t) is not None                          # noqa: E731
if P_ly is not None:
    dline("date.year, from outside", "date & (date.year: >= 2000)", bt_of([DT, ISO]), P_ly,
          ["2025-01-02!", "1999-01-02!"], "1999-01-02! 2025-03-04!", "2025-01-02! 1999-01-02! 2001-12-31!",
          "core/labels/export/export-list")
if P_lb is not None:
    dline("All but one", "date & (date.day: \"02\")", bt_of([DB1, ISO]), P_lb, ["2025-01-02!", "1999-02-03!"],
          "1999-02-03! 2025-01-02!", "2025-01-02! 1999-02-03! 2001-01-02!", "core/labels/export/export-list")
lw = [wdiff(x, f, DTS) for x, f in ((P_ly, ok_y), (P_lr, ok_y), (P_la, ok_m), (P_lb, ok_d), (P_li, ok_y))]
q_lr = [bool(x) for x in (r_lm, r_lp, r_lr, r_lb, r_lx)]
check("LIST", lw == [0] * 5 and all(q_lr), "one `date.year`, renamed `date.y`, all `date.month`, all but one "
      "`date.day`, read bare inside: differing %s over %d texts; refused: unlisted `date.month` %s, the part's path "
      "`date.isodate.month` %s, the renamed-away `date.year` %s, the left-out `date.month` %s, an unexported "
      "`(=hour)` %s" % (lw, len(DTS), *q_lr))
print("   refusals: %s | %s" % (r_lm, r_lx))

print("== CAPTEXP: capture-export's two candidates, the match the same under both")
P_q = tryp("q", ["q := /${A}!/", A_H])
seen_top = set(b for b in surfaced(P_q.rx, "top")) if P_q is not None else set()
groups_rx = set(re.findall(r"\(\?<([A-Za-z]\w*)@", P_q.rx)) if P_q is not None else set()
cap_a = sorted(b for b in seen_top if "." not in b and not b.startswith("_"))
cap_b = sorted(set(g for g in groups_rx if not g.startswith("_")) | ({"q"} if sd("s13") else set()))
if P_q is not None:
    dline("", "q", ", q := `/${A}!/`, A := `/(?<h>\\d)/`", P_q, ["3!", "33!"], "x3!", "3! 7! 4", "core/labels/export/capture-export",
          "; the caller's captures: (a) none, (b) `h`")
check("CAPTEXP", P_q is not None and cap_a == [] and cap_b == ["h"],
      "labels visible at the top-level program (candidate (a)'s captures): %s; groups written in rx text (candidate "
      "(b)'s): %s" % (cap_a, cap_b))

print("== ATOMIC: the re-spelled atomic line; the old program refused (reading (e))")
AT = ["A := /(?<l>\\d)\\d/", "B := /(?<l>\\d\\d)/"]
if sd("s22"):
    SABD.add("s2")
r_at = qref("[ab = atomic(B | A)] & (ab.l: <20)", AT)
SABD.discard("s2") if sd("s22") else None
check("ATOMIC", r_at is not None, "`[ab = atomic(B | A)] & (ab.l: <20)` refused %s: %s" % (bool(r_at), r_at))

print("== SCAN: a textual control on every printed line, the engine's runs aside: a read `X.y` from outside, X bound "
      "on the line, where X's text writes no `y` and has no public part label to pass one")
SCANL = [(k, v[0], v[3]) for k, v in sorted(ROWS.items())]
if sd("s20"):
    SCANL.append((("planted", 0), "", " (`p2 & (p2.h: <5)`, p2 := `/${A}!/`, A := `/(?<h>\\d)/`)"))
sc_n, sc_flag = 0, []
for k, line_, tail in SCANL:
    bd = dict((h.split("(")[0], b) for h, b in re.findall(r"([\w.]+(?:\([\w, =]*\))?) := `([^`]*)`", tail))
    mm = re.search(r"`([^`]*)`", tail)
    for X, y in re.findall(r"\b([A-Za-z]\w*)\.([A-Za-z_]\w*)\s*:", (mm.group(1) if mm else "") + " " +
                           " ".join(bd.values())):
        if X not in bd:
            continue
        sc_n += 1
        d = bd[X]
        if not re.search(r"\(\?<%s>|\[%s = |\[\([^)]*\b%s\b|\[[A-Za-z]\w* = |\[\(=[,)]" % (y, y, y), d):
            sc_flag.append((k, "%s.%s" % (X, y)))
check("SCAN", sc_n and not sc_flag, "%d printed lines, %d reads `X.y` through a binding on the line; flagged: %s" %
      (len(SCANL), sc_n, sc_flag or "none"))

print("== NULLABLE: EVID-4's known limit: no program the checks ran has a loop whose body can match empty")


def nullable(n):
    t = n[0]
    if t in ("lit", "cls", "dot"):
        return False
    if t == "seq":
        return all(nullable(x) for x in n[1])
    if t == "alt":
        return any(nullable(x) for x in n[1])
    if t == "grp":
        return nullable(n[2])
    if t == "rep":
        return n[2] == 0 or nullable(n[1])
    if t == "atomic":
        return nullable(n[1])
    return True


def loops_nullable(n, out):
    t = n[0]
    if t == "rep" and (n[3] is None or n[3] > 1) and nullable(n[1]):
        out.append(n)
    for x in (n[1] if t in ("seq", "alt") else [n[2]] if t in ("grp", "andpat2") else
              [n[1]] if t in ("rep", "atomic", "look") else []):
        if isinstance(x, tuple):
            loops_nullable(x, out)
    return out


checked = list(RUN)
if sd("s14"):
    checked.append(("/(?:(?<d>\\d)*)+/", (), prog("/(?:(?<d>\\d)*)+/").node))
nl = [(e, b) for e, b, nd in checked if loops_nullable(nd, [])]
check("NULLABLE", not nl, "%d programs run by the checks above, walked node by node: %d with a loop whose body can "
      "match empty%s" % (len(checked), len(nl), (": %s" % nl[:4]) if nl else ""))

print("== SUCCESSOR: every earlier in-force model re-run; its LAST LINE read; each red declared superseded")
LANES = os.path.normpath(os.path.join(HERE3, ".."))
P82 = "predfix82's declaration, unchanged: "
SUPERSEDED = {
    "predfix82": {"MARKS": "MARKS here: its ANS-1 text \"a name with two sources is open two-sources\" left the "
                           "call-prefix bullet reflowed for default-export (40-line cap); the pointer stands as \"two "
                           "sources: core/labels/paths/two-sources\", and two-sources gains its default-export bullet",
                  "SUCCESSOR": "SUCCESSOR here: its own re-run of predref and predcall meets their new DOC reds, "
                               "declared below"},
    "predbound": {"DOC": P82 + "REPRINT (its two missing lines re-printed)"},
    "predref": {"SCAN": P82 + "VALUEGQ, BOUNDSET, REPRINT (three fragment spans)",
                "MARKS": P82 + "predcall's MARKS (call-prefix ruled)",
                "DOC": "ATOMIC and SWEEP here: the atomic line is re-spelled `atomic([ab = B | A]) & (ab.l: <20)` "
                       "(the old program is refused under default-export, reading (e)); answers unchanged"},
    "predcall": {"SCAN": P82 + "the same three fragment spans",
                 "PREDREF": P82 + "SUCCESSOR (this check reads predref's last line itself)",
                 "DOC": "MACRO here: the line \"d as the call surfaces it, the last mention (B's)\" is renamed \"d as "
                        "the call exports it, the body's own\" (default-export), its answers unchanged and printed "
                        "by MACRO"},
    "predfix77": {"TRACEBACK": P82 + "REPRINT and predbound's checks (the `chars` body reader)"},
    "predarr": {"TRACEBACK": P82 + "REPRINT and predref's HITS (the same `chars` body reader)"},
    "predscope": {"NAMES": P82 + "predbound's bound-condition checks",
                  "CLOSEDB": P82 + "REPRINT `bare-condition/labels`",
                  "DOC": P82 + "REPRINT (lines re-spelled under label-reference and nested-scope)"},
}
if sd("s15"):
    SUPERSEDED["predfix82"].pop(next(iter(SUPERSEDED["predfix82"]), None), None)
procs = {}
for mname in SUPERSEDED:
    env = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE") and not k.endswith("_ENGINE")}
    procs[mname] = subprocess.Popen([sys.executable, "-I", "-B", os.path.join(LANES, mname + "_evidence",
                                                                               mname + "_model.py")],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
succ_ok = True
for mname, pr in procs.items():
    try:
        out, _ = pr.communicate(timeout=600)
    except subprocess.TimeoutExpired:
        pr.kill()
        out = "TIMEOUT"
    last = out.rstrip("\n").split("\n")[-1]
    mm = re.match(r"%s_model: (\d+) checks, (\d+) failed(?: \(([^)]*)\))?$" % mname, last)
    reds = set(x.strip() for x in (mm.group(3) or "").split(",") if x.strip()) if mm else {"TRACEBACK"}
    undeclared = sorted(reds - set(SUPERSEDED[mname]))
    gone = sorted(set(SUPERSEDED[mname]) - reds)
    if undeclared:
        succ_ok = False
    print("   %-10s last line: %s" % (mname, last[:120]))
    for r in sorted(reds):
        print("      %s: %s" % (r, ("superseded by " + SUPERSEDED[mname][r]) if r in SUPERSEDED[mname]
                                    else "UNDECLARED"))
    if gone:
        print("      declared but green now: %s" % gone)
check("SUCCESSOR", succ_ok, "%d earlier models re-run, each last line read; every red declared superseded: %s" %
      (len(procs), "yes" if succ_ok else "NO"))

print("== SWEEP: every printed three-mode line, old engine against the rule (argument-default (local)); no printed "
      "answer moves unless listed under ANSWERS_CHANGED")
ANSWERS_CHANGED = {}
NEW_SW = {k: v[4]["local"] for k, v in ROWS.items()}
if sd("s16"):                                    # plant: a printed program re-spelled to read an unexported label
    k_ = next(k for k, v in ROWS.items() if "(`pub & (pub.h: <5)`, pub := `[a = A] SEQ" in v[0])
    l_ = ROWS[k_][0].replace("pub := `[a = A] SEQ", "pub := `A SEQ")
    a_ = answer_part(l_)
    t_ = l_[l_.index(a_) + len(a_):]
    NEW_SW[k_] = sweep_one(l_, a_, re.search(r"`([^`]*)`", t_).group(1), t_)
moved = [k for k in NEW_SW if OLD_SW.get(k, ("?",))[0] == "same" and NEW_SW[k][0] != "same"
         and k not in ANSWERS_CHANGED]
gained = [k for k in NEW_SW if OLD_SW.get(k, ("?",))[0] != "same" and NEW_SW[k][0] == "same"]
cnt = {}
for v in NEW_SW.values():
    cnt[v[0]] = cnt.get(v[0], 0) + 1
ocnt = {}
for v in OLD_SW.values():
    ocnt[v[0]] = ocnt.get(v[0], 0) + 1
check("SWEEP", len(OLD_SW) == len(NEW_SW) and not moved,
      "%d printed lines (old engine %d: %s); the rule: %s; reproduced by the old engine and not the rule: %d %s; "
      "reproduced by the rule only: %d %s; ANSWERS_CHANGED %d" %
      (len(NEW_SW), len(OLD_SW), ", ".join("%s %d" % kv for kv in sorted(ocnt.items())),
       ", ".join("%s %d" % kv for kv in sorted(cnt.items())), len(moved), moved[:4], len(gained), sorted(gained),
       len(ANSWERS_CHANGED)))
for k in moved:
    print("   MOVED %s:%d %s %s" % (k[0], k[1], NEW_SW[k][0], NEW_SW[k][1][:160]))

print("== QUOTES: every owner sentence this lane quotes occurs in the record and the documents; every cited title is one")
QQ = ["default-export: protected",
      "[a = A ] is making the labels from A public to local and later bindings",
      "also makes the labels protected but with different access locally",
      "not accessible locally to the binding",
      "A := <label a> B := A & A   C := B & (B.a: 9) here B.a is always an error.",
      "Export list: yes. I will say that the form is the same but one is bindings and one is labels. We should clarify "
      "either they are the same thing but different targets or note their space.",
      "I meant if isodate was defined and I wanted to reexport year only. [d = isodate] exports all. How about this: "
      "[(=year) = isodate]",
      "Question, can I somehow export some labels but not others. Like year only from isodate",
      "Agree caveat bindings used to scope labels (A.a: 8)",
      "what would A.d mean if d no longer was visible?"]
TT = ["2026-11-22 OWNER RULING — default-export: protected",
      "2026-11-22 OWNER, an analogy to validate: the four ways a part is used, as C++ access levels",
      "2026-11-22 OWNER, discussing the analogy: `B := A & A`, `C := B & (B.a: 9)`: \"here B.a is always an error\"",
      "2026-11-22 OWNER RULING — export-list: yes",
      "2026-11-22 OWNER PROPOSAL — re-exporting one label of a defined part: `[(=year) = isodate]`",
      "2026-11-22 OWNER, a question after default-export: \"can I somehow export some labels but not others. Like year "
      "only from isodate\"",
      "2026-11-22 OWNER, on the two name spaces: \"Agree caveat bindings used to scope labels (A.a: 8)\""]
if sd("s17"):
    QQ[0] = "default-export: public"
DOCS_NOW = {f: read(os.path.join(PRED, f)) for f in NEW}
ALLNOW = "\n".join(DOCS_NOW.values())
q_miss = [q for q in QQ if ws(q) not in RECORD_WS or ws(q) not in ws(ALLNOW)]
heads = set(ws(re.sub(r"^(### |\*\*)", "", l_)) for l_ in RECORD.split("\n") if l_.startswith(("### ", "**")))
t_miss = [t for t in TT if not any(h.startswith(ws(t)) for h in heads) or ws(t.split(" (")[0]) not in ws(ALLNOW)]
check("QUOTES", not q_miss and not t_miss, "%d quoted sentences in the record and the documents, missing: %s; %d "
      "record titles cited, not a title or not cited: %s" % (len(QQ), q_miss or "none", len(TT), t_miss or "none"))

print("== MARKS: each piece of the fold where it landed")
C_, CD_, L_, LD_ = DOCS_NOW["core.md"], DOCS_NOW["core_details.md"], DOCS_NOW["library.md"], DOCS_NOW["library_details.md"]
MK = [("statement", C_, "a part used alone is seen inside it and not exported"),
      ("statement 3", C_, "A part used alone exports none of its labels, through a hole and the sequence operator alike"),
      ("statement 5", C_, "(awaits capture-export)"),
      ("analogy table", C_, "| `A` alone | protected, \"with different access locally\" | none (statement 3) |"),
      ("export-list row", C_, "| `[(=year) = A]` | (export-list) |"),
      ("some but not others", C_, "Some labels but not others: by part"),
      ("flat-read-outside", C_, "a label it does not export is none"),
      ("flow", C_, "a user reads what a piece exports"),
      ("holes/labels", C_, "a hole is a part used alone"),
      ("call-prefix", C_, "an argument used alone is not exported"),
      ("argument-default", C_, "[core/labels/paths/argument-default]   open argument-default 2026-11-22"),
      ("capture-export", C_, "[core/labels/export/capture-export]   open capture-export 2026-11-22"),
      ("two-sources", C_, "What default-export changes (a reading)"),
      ("export-list", C_, "[core/labels/export/export-list]   ruled 2026-11-22"),
      ("binding-list", C_, "One form, two targets, decided by where it stands"),
      ("form caveat", C_, "A path's last step is the label"),
      ("placeholders", C_, "| the EXPORT LIST on a part label"),
      ("errors row", C_, "a read from outside of a label only a part used alone holds"),
      ("length", L_, "so a call exports no `ch`"),
      ("rulings item", CD_, "- 2026-11-22 \"default-export: protected\" (record: \"2026-11-22 OWNER RULING — default-export"),
      ("library history", LD_, "lane preddef, default-export folded"),
      ("EVID-4", open(os.path.abspath(__file__), encoding="utf-8").read(), "# KNOWN LIMIT (EVID-4, planned")]
if sd("s18"):
    MK[0] = (MK[0][0], MK[0][1], MK[0][2] + " (planted)")
mk_miss = [i for i, t, sub in MK if ws(sub) not in ws(t)]
check("MARKS", not mk_miss, "%d pieces of the fold found where they landed; missing: %s" % (len(MK), mk_miss or "none"))

print("== DOC: every line this model formats occurs verbatim in the documents")
DLN = list(LINES)
if sd("s19"):
    DLN[0] = (DLN[0][0], DLN[0][1].replace("WHOLE `", "WHOLE `x", 1))
d_miss = [(t, L[:90]) for t, L in DLN if ws(L) not in ws(ALLNOW)]
check("DOC", DLN and not d_miss, "%d lines; missing: %s" % (len(DLN), d_miss or "none"))

failed = [n for n, ok in RESULTS if not ok]
print("preddef_model: %d checks, %d failed%s" % (len(RESULTS), len(failed),
                                                  (" (%s)" % ", ".join(failed)) if failed else ""))
sys.exit(1 if failed else 0)
