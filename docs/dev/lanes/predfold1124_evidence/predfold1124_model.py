#!/usr/bin/env python3
# Lane predfold1124 (2026-11-23): the successor evidence model for the fold of the owner's rulings made after review
# r88's dispositions (shorthand-is-callers, capture-in-set, exact-count-unspecified, path-rules; the manager's two
# closures that stand). DESIGN EVIDENCE ONLY; rules nothing. It succeeds docs/dev/lanes/predfix88_evidence/
# predfix88_model.py.
#
# METHOD. predfix88's model is LOADED unchanged: it is executed up to its first check (`unit("CONTROL"`), so its
# engines (and, through it, every older engine) and its check helpers (pl, rl, refused, pinned, piece8, entry8) are
# defined. Then the 1124 extensions act, each switched by X9[0] (on for the documents now; off for SWEEP's control,
# predfix88's engine over the start commit's documents):
#   SHORT9  (shorthand-is-callers, ruled) the shorthand label is the caller's own: `B(A)` read through `A.` is
#           `B([A = A])`, whatever the body does with the spot (condition 1 kept; condition 4 counts only the labels
#           the caller's own text makes, which predfix88's EXPARG arm refuses before the rewrite).
#   PATH9   (path-rules, ruled) rule 2: a path crosses no underscore label, full or prefix, unless it is the start
#           (inside a definition, through a binding's text, and through a macro's body at its call, rule 5); rules 1
#           and 4: a named middle label stacked directly in the step before it is the same spot (`n.m.h` read as
#           `n.h` by the loaded engine, which refused the chain).
# Every regex the model matches with is built mechanically from the program text by the loaded engines.
#
# Run (W = the worktree; any cwd):  timeout 1800 python3 -I -B W/docs/dev/lanes/predfold1124_evidence/predfold1124_model.py
# Its verdict is its LAST LINE, `predfold1124_model: N checks, F failed`; it EXITS NON-ZERO iff that line reports one.
# PREDFOLD1124_SABOTAGE=pN: one deliberately wrong rule, fact or document text; its target check must FAIL.
# PREDFOLD1124_SABOTAGE=all: every plant in turn (a subprocess each, a per-unit timeout naming the plant).
# PREDFOLD1124_LIGHT=1 skips SUCCESSOR. PREDFOLD1124_DUMPSUCC=DIR writes each re-run model's output there.
import builtins
import os
import re
import subprocess
import sys
import time

HERE9 = os.path.dirname(os.path.abspath(__file__))
LANES9 = os.path.normpath(os.path.join(HERE9, ".."))
W9 = os.path.normpath(os.path.join(HERE9, "..", "..", "..", ".."))
P88 = os.path.join(LANES9, "predfix88_evidence", "predfix88_model.py")
UNIT_TIMEOUT9 = 180                                          # seconds per check, per plant, per re-run model
START9 = "172930848"                                         # this lane's starting commit (lane/predfold1124), PINNED
SAB9 = set(x for x in os.environ.get("PREDFOLD1124_SABOTAGE", "").split(",") if x)
LIGHT9 = os.environ.get("PREDFOLD1124_LIGHT") == "1"


def s9(n):
    return n in SAB9


PLANTS9 = [   # (plant, its target check, what it plants: each changes the ENGINE, the evidence or a document read)
    ("p1", "CONTROL", "the control's direct regex for the chain `n.m.d` written for the SECOND digit"),
    ("p2", "SHORTHAND", "the shorthand reverted to condition 4 counting the body's labels (predfix88's engine)"),
    ("p3", "PATHS", "rule 2 off: a path may cross an underscore label"),
    ("p4", "STACKCHAIN", "the chain normalisation off: `n.m.d` left to the loaded engine, which refuses it"),
    ("p5", "TABLE", "one cell of the ownership table changed to the opposite legality in core.md as read"),
    ("p6", "NAMEGRID", "one decided cell's expected verdict flipped"),
    ("p7", "LIBLINES", "the written-out form of the provided bodies' shorthand read as `[_ = A]`"),
    ("p8", "EXACTCOUNT", "the ruled sentence of exact-count-unspecified dropped from core.md as read"),
    ("p9", "CAPSET", "lib/structural/capture/in-set read with its old status `open capture-in-set`"),
    ("p10", "OPTIONS", "the position reading's sentence dropped from library.md as read"),
    ("p11", "PARKED", "the parked piece's trigger dropped from parked.md as read"),
    ("p12", "EXPAND", "argument-default's written-out form read as `B([_ = A])` (core.md altered as read)"),
    ("p13", "READINGS", "a reading's run moved: the FIRST spot's digit read in place of the last mention"),
    ("p14", "SWEEP", "one printed answer of the documents moved under an unchanged key"),
    ("p15", "ERRSWEEP", "one printed compile-error line made a legal program (core.md altered as read)"),
    ("p16", "NULLABLE", "one program with a nullable loop run (`rx.repeat(/a?/)`)"),
    ("p17", "SUCCESSOR", "one declared red's text altered"),
    ("p18", "QUOTES", "path rule 2 altered in the base piece only"),
    ("p19", "DOC", "a formatted line altered"),
    ("p20", "FLAGS", "the option hole read as weak (R-2 reversed)"),
]
HEAVY9 = {"SUCCESSOR"}
STRICT9 = re.compile(r"^predfold1124_model: (\d+) checks, (\d+) failed(?: \(([^)]*)\))?$")
if "all" in SAB9:                                            # the plant runner: each plant alone, a subprocess each
    rows, notc = [], 0
    for pn, target, what in PLANTS9:
        env = {k: v for k, v in os.environ.items()}
        env["PREDFOLD1124_SABOTAGE"] = pn
        if target not in HEAVY9:
            env["PREDFOLD1124_LIGHT"] = "1"
        t0 = time.time()
        try:
            r = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__)], capture_output=True,
                               text=True, env=env, timeout=UNIT_TIMEOUT9 * (10 if target in HEAVY9 else 2))
            out_, rc_ = r.stdout + r.stderr, r.returncode
        except subprocess.TimeoutExpired:
            out_, rc_ = "TIMEOUT: plant %s did not finish in its unit time" % pn, None
        lines = out_.rstrip("\n").split("\n")
        last = lines[-1]
        mm = STRICT9.match(last)
        fl_ = next((x for x in lines if x.startswith("FAIL %s:" % target)), "")
        tb = any(x.startswith("Traceback") or re.search(r"\bCRASH [A-Z]\w*(Error|Exception)\b", x) for x in lines)
        ok = bool(fl_) and not tb and rc_ not in (0, None) and bool(mm) and target in (mm.group(3) or "").split(", ")
        notc += not ok
        rows.append((pn, target, what, ok))
        print("%s -> %s (%s): %s (%.0f s)" % (pn, target, what, "caught" if ok else "NOT CAUGHT", time.time() - t0))
        print("   last line: %s" % last)
        print("   its FAIL line: %s" % fl_[:300], flush=True)
    if not notc:
        print("   each plant turned its target check FAIL, with no traceback and no engine crash")
    print("predfold1124_sabotage: %d plants, %d not caught" % (len(rows), notc))
    sys.exit(1 if notc else 0)


# ================================================================== the LOADER: predfix88's engines and helpers, unchanged
for v in list(os.environ):
    if v.startswith("PREDFIX88_"):
        os.environ.pop(v, None)
_src88 = builtins.open(P88, encoding="utf-8").read()
_cut88 = _src88.index('unit("CONTROL", ')
_file9 = __file__
__file__ = P88                                               # noqa: F811  (the loaded code finds its siblings by it)
exec(compile(_src88[:_cut88], P88, "exec"), globals())       # noqa: S102  (predfix88's definitions, unchanged)
__file__ = _file9
LINES.clear()
RUN.clear()
RESULTS.clear()


def _snip88(a, b):
    """predfix88's own text between two markers (definitions placed after its first check), executed verbatim."""
    i = _src88.index(a)
    exec(compile(_src88[i:_src88.index(b, i)], P88, "exec"), globals())   # noqa: S102


_snip88("WRITERS = [", "tb_bad, tb_n, tb_rows = [], 0, 0")             # the ownership table's row and cell readers
_snip88("_d0 = _src84.index(", "DECL_RULE8 = []")                     # predfix84's DECL_LINE / DECL_RULE, predfix88's DECL8
_snip88("def heads8(rec):", "DET8 = ")                               # the record's titles
X9 = [True]
P9F = dict(prog=prog, shorthand=shorthand)


def x9():
    return X9[0]


# ================================================================== the 1124 extensions (lane predfold1124)
RULE2_9 = "crosses the underscore label"


def strip_keep_holes(t):
    """strip_lits, with the text of every `${...}` hole inside a literal kept (a hole is expression text)."""
    st = list(strip_lits(t))
    i = 0
    while True:
        i = t.find("${", i)
        if i < 0:
            break
        d, j = 0, i + 1
        while j < len(t):
            d += {"{": 1, "}": -1}.get(t[j], 0)
            if d == 0:
                break
            j += 1
        st[i:j + 1] = list(t[i:j + 1])
        i = j + 1
    return "".join(st)


def _brackets(t):
    """Every part label written in t: (name, start of `[`, start of its content, its `]`); literal text skipped,
    holes read."""
    out, st = [], strip_keep_holes(t)
    for mm in re.finditer(r"\[(\w+|\([^()\[\]]*\)) = ", st):
        j = _close_br(t, mm.start())
        if j is None:
            continue
        out.append((mm.group(1), mm.start(), mm.end(), j))
    return out


def _enclosing(br, i, lo, hi):
    """The part labels whose content holds position i, inside [lo, hi), outer first."""
    return [b for b in sorted(br, key=lambda b: b[1]) if lo <= b[1] and b[3] <= hi and b[2] <= i < b[3]]


def _sites(t, lo, hi, target, leaves):
    """Where the target may sit in t[lo:hi]: its group or its part label, and every leaf (a parameter, a binding
    name, a call) whose exports might hold it (the loaded engine decides those)."""
    st = strip_keep_holes(t)
    out = [lo + mm.start() for mm in re.finditer(r"\(\?<:?%s>" % re.escape(target), t[lo:hi])]
    out += [lo + mm.start() for mm in re.finditer(r"\[%s = " % re.escape(target), st[lo:hi])]
    for lf in leaves:
        out += [lo + mm.start() for mm in re.finditer(r"(?<![\w.$])%s(?![\w])" % re.escape(lf), st[lo:hi])]
    return sorted(set(out))


def _region(start, expr, binds):
    """(text, lo, hi, leaves) the path's steps after its start walk in: the start's part label in expr (through a
    call it holds, that macro's body); else a macro's body at its call (rule 5); else a binding's text (rule 5).
    None if the start is none of them (the loaded engine decides)."""
    bd, heads = {}, {}
    for b in binds:
        h = head_of(b)
        if h:
            heads[h[0]] = h
        else:
            n_, _, body = b.partition(" := ")
            bd[n_.strip()] = body.strip()
    names = set(bd) | set(heads) | set(PROV) | set(MACROS)
    for nm, s_, c_, e_ in _brackets(expr):
        if nm == start:
            inner = expr[c_:e_].strip()
            mc = re.fullmatch(r"([A-Za-z_][\w.]*)\((.*)\)", inner, re.S)
            if mc and mc.group(1) in heads and close_paren(inner, len(mc.group(1))) == len(inner) - 1:
                h = heads[mc.group(1)]
                return h[2], 0, len(h[2]), [p for p, _, _ in h[1]] + list(names)
            return expr, c_, e_, list(names)
    if start in heads:
        h = heads[start]
        return h[2], 0, len(h[2]), [p for p, _, _ in h[1]] + list(names)
    if start in bd:
        return bd[start], 0, len(bd[start]), list(names)
    return None


def _stacked_in(t, br, outer, inner):
    """Is a part label `inner` written directly as the whole content of a part label `outer` in t?"""
    for nm, s_, c_, e_ in br:
        if nm != outer:
            continue
        body = t[c_:e_]
        k = len(body) - len(body.lstrip())
        j = _close_br(t, c_ + k) if body.lstrip().startswith("[%s = " % inner) else None
        if j is not None and t[j + 1:e_].strip() == "":
            return True
    return False


def path_rules(expr, binds):
    """PATH9: rule 2 (no underscore label on the path unless it is the start); rules 1 and 4 (a named middle label
    stacked directly in the step before it is the same spot: dropped for the loaded engine). Returns the expression
    with each legal chain normalised; raises at a crossing."""
    if not x9():
        return expr
    sl = strip_lits(expr)
    reads = [(mm.start(1), mm.group(1)) for mm in re.finditer(r"(?<![\w.$])\$?([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+)", sl)]
    out, last = [], 0
    for pos, rd in reads:
        steps = rd.split(".")
        start, mids, target = steps[0], steps[1:-1], steps[-1]
        if any(s_.startswith("_") for s_ in steps[1:]) and not s9("p3"):
            raise CompileError("`%s`: the path %s `%s`, not the start (a compile error, path-rules rule 2)" %
                               (rd, RULE2_9, next(s_ for s_ in steps[1:] if s_.startswith("_"))))
        reg = _region(start, expr, binds)
        new = rd
        if reg is not None:
            t, lo, hi, leaves = reg
            br = _brackets(t)
            ok_site, crossed = False, None
            for i in _sites(t, lo, hi, target, leaves):
                encn = [b[0] for b in _enclosing(br, i, lo, hi)]
                it = iter(encn)
                if not all(m_ in it for m_ in mids):
                    continue                                 # this site is not on the path's named steps
                bad = [n_ for n_ in encn if n_.startswith("_")]
                if bad and not s9("p3"):
                    crossed = crossed or bad[0]
                    continue
                ok_site = True
                break
            if not ok_site and crossed:
                raise CompileError("`%s`: the path %s `%s`, not the start (a compile error, path-rules rule 2)" %
                                   (rd, RULE2_9, crossed))
            kept = [start]
            for m_ in mids:
                if _stacked_in(t, br, kept[-1], m_) and not s9("p4"):
                    continue
                kept.append(m_)
            new = ".".join(kept + [target])
        out.append(expr[last:pos] + new)
        last = pos + len(rd)
    out.append(expr[last:])
    return "".join(out)


def shorthand(expr, heads, bnames):                         # noqa: F811
    """SHORT9: the shorthand label is the caller's own: `B(A)` read through `A.` is `B([A = A])`, whatever the body
    does with the spot; condition 1 kept."""
    if not x9() or s9("p2"):
        return P9F["shorthand"](expr, heads, bnames)
    sl = strip_lits(expr)
    reads = set(re.findall(r"(?<![\w.$])\$?([A-Za-z_]\w*)\.[A-Za-z_]", sl))
    for N in sorted(reads & bnames):
        calls = []
        for mm in re.finditer(r"(?<![\w.])([A-Za-z_][\w.]*)\(", expr):
            if mm.group(1) not in heads:
                continue
            j = close_paren(expr, mm.end() - 1)
            args = [a.strip() for a in split_top(expr[mm.end():j], ",")]
            for k, a in enumerate(args):
                av = a.split(" = ", 1)[1].strip() if re.fullmatch(r"\w+ = .*", a, re.S) else a
                if av == N:
                    calls.append((mm, j, k, args))
        if not calls:
            continue
        uses = len(re.findall(r"(?<![\w.$])%s(?![\w.])" % re.escape(N), sl))
        if uses != 1:
            raise CompileError("`%s.`: the binding `%s` is used %d times in this definition, so its name is no "
                               "shorthand for a label (a compile error, binding-as-label condition 1)" % (N, N, uses))
        mm, j, k, args = calls[0]
        a = args[k]
        lab = "_" if s9("p7x") else N
        new_args = list(args)
        new_args[k] = ("%s = [%s = %s]" % (a.split(" = ", 1)[0], lab, N)) if a != N else "[%s = %s]" % (lab, N)
        expr = expr[:mm.start()] + "%s(%s)" % (mm.group(1), ", ".join(new_args)) + expr[j + 1:]
    return expr


def prog(expr, binds=(), **opts):                            # noqa: F811
    if not x9():
        return P9F["prog"](expr, binds, **opts)
    binds = list(binds)
    expr = path_rules(expr, binds)
    b2 = []
    for b in binds:                                          # the rules inside each plain binding's own text
        if head_of(b):
            b2.append(b)
        else:
            n_, _, body = b.partition(" := ")
            b2.append(n_ + " := " + path_rules(body, binds))
    return P9F["prog"](expr, b2, **opts)


# ---- the unit timeout: every check is a unit; a hung unit is named on the last line
import signal  # noqa: E402


def _alarm9(sig, frm):
    print("TIMEOUT: unit %s ran over its time" % UNIT8[0], flush=True)
    print("predfold1124_model: unit %s timed out" % UNIT8[0], flush=True)
    os._exit(3)


signal.signal(signal.SIGALRM, _alarm9)


def unit9(name, what, secs=UNIT_TIMEOUT9):
    unit(name, what, secs)


# ================================================================== the checks
D9 = dict(NOWS)                                              # the documents as READ by the checks (plants alter it)
D8.clear()
D8.update(D9)                                                # piece8 / entry8 read D8: the same dict
RULE_T = "core/labels/rule"
PATHS_T = "core/labels/rule/paths"
SC_T = "core/labels/rule/stacked-chain"
REC9 = _git8("docs/design/plan_row_bodies/COND-FAMILY.md", START9)
B_MN = "B(rx) := /${[n = [m = rx]]}xx/"
X_MN = 'X := [n = [m = A]] SEQ "!"'
X2_ = 'X2 := A SEQ "!"'
Q3B = (["3!", "7!"], "7! 3!", "3! 7! 4!")
QDD = (["7-3", "3-7", "3-3"], "7-3 3-7", "7-3 3-7 1-2 9-9")
Q1 = (["3", "7"], "7 3", "3 7 4")
IDN = "identity(x) := /${[(=) = x]}/"
if s9("p8"):
    D8["core.md"] = D8["core.md"].replace("where a body writes an exact count", "where a body writes a count", 1)
if s9("p9"):
    D8["library.md"] = D8["library.md"].replace("[lib/structural/capture/in-set]   ruled",
                                                "[lib/structural/capture/in-set]   open capture-in-set", 1)
if s9("p10"):
    D8["library.md"] = D8["library.md"].replace("may stand mid-file and applies from the statement on", "", 1)
if s9("p11"):
    D8["parked.md"] = D8["parked.md"].replace("a second kind of effect is built", "", 1)
if s9("p12"):
    D8["core.md"] = D8["core.md"].replace("Written out, `B(A)` is `B([A = A])`", "Written out, `B(A)` is `B([_ = A])`", 1)
if s9("p15"):
    D8["core.md"] = D8["core.md"].replace("(`[l = [_ = P]] & (l.d: <5)`", "(`[l = P] & (l.d: <5)`", 1)
if s9("p18"):
    D8["core.md"] = D8["core.md"].replace("2. the path may not contain any underscore labels full or prefix unless the "
                                          "underscore prefix label is the start", "2. the path may contain any label", 1)

unit9("CONTROL", "the extended engine's new answers against python `re` (each program's meaning written directly)")
QC9 = pop("37x!", 4)
ctl9 = []
for e, b, rx in (("[n = [m = P]] & (n.m.d: <5)", [P_XX], r"[0-4]xx" if not s9("p1") else r"\dxx(?<=[0-4]xx)x"),
                 ("[n = [_x = P]] & (_x.d: <5)", [P_], r"[0-4]\d"),
                 ("X & (X.n.m.h: <5)", [A_H, X_MN], r"[0-4]!"),
                 ("B(A) & (A.h: <5)", [A_H, B_CL], r"[0-4]xx"),
                 ("B(A) & (A.h: <5)", [A_H, B_ST], r"[0-4]xx"),
                 ("B(A) & (A.d: <5)", [A_D, B_AF], r"\d-[0-4]")):
    Pg, err = run(e, b)
    ctl9.append((e, ndiff(answers(Pg, QC9), answers(Re(rx), QC9)) if Pg is not None else err))
check("CONTROL", all(v == (0, 0, 0) for _, v in ctl9), "differing (WHOLE, SEARCHED, FIND-ALL) against python `re` "
      "over %d texts: %s" % (len(QC9), ctl9))

unit9("SHORTHAND", "shorthand-is-callers (ruled): `B(A)` read through `A.d` is `B([A = A])` whatever the body does "
      "with the spot; condition 1 kept; condition 4 counts only the caller's own labels")
sh_pin = pinned("SHORTHAND", [
    (RULE_T, "The shorthand label is the caller's own: `B(A)` read through `A.d` means `B([A = A])`, whatever B's "
             "body does with the spot. Condition 4 counts only labels made in the text that writes the shorthand."),
    (RULE_T, "Setting a label closes a path (through the shorthand in that binding) but doesn't block out the target."),
    (AD_T, "Written out, `B(A)` is `B([A = A])` for every body"),
    (CA_T, "the caller's `A.d` reads the argument through its own shorthand label")])
SH_BODIES = [("alone", B_AL, QDD), ("labelled", B_P, QDD), ("listed", B_LS, Q3), ("closed", B_CL, Q3),
             ("`_p`", B_CP, Q3), ("stacked", "B(rx) := /${[n = [_x = rx]]}xx/", Q3), ("two public stacked", B_MN, Q3)]
sh_bad = []
for nm_, body_, q_ in SH_BODIES:
    Ps, es = run("B(A) & (A.d: <5)", [A_D, body_])
    Pw, ew = run("B([A = A]) & (A.d: <5)", [A_D, body_])
    same = Ps is not None and Pw is not None and answers(Ps, pop("37x-", 3)) == answers(Pw, pop("37x-", 3))
    print("   %s: the shorthand %s, the written-out form %s, %s" % (nm_, "legal" if Ps else "refused: " + es[:80],
                                                                  "legal" if Pw else "refused", "alike" if same else
                                                                  "DIFFER"))
    if not same:
        sh_bad.append(nm_)
P_s1 = pl("The body labelling the spot", "B(A) & (A.d: <5)", [A_D, B_P], *QDD, tag=CA_T)
pl("A's own d, the body labelling the spot (case 2)", "B(A) & (A.d: <5)", [A_D, B_P], *QDD, tag=CP_T)
P_s2 = pl("The body listing the spot", "B(A) & (A.d: <5)", [A_D, B_LS], *Q3, tag=CA_T)
P_s3 = pl("Closed by the macro", "B(A) & (A.d: <5)", [A_D, B_CL], *Q3, tag=CA_T)
P_s3r = pl("The caller's own shorthand, under a closing body", "B(A) & (A.d: <5)", [A_D, B_CL], *Q3, tag=RULE_T)
ok_s4, r_s4 = rl("Through the call, closed", "[c = B(A)] & (c.d: <5)", [A_D, B_CL], RULE2_9,
                 "the path crosses the blank label (core/labels/rule/paths rule 2); `B(A) & (B.d: <5)` alike", CA_T)
ok_s4b = refused("B(A) & (B.d: <5)", [A_D, B_CL], RULE2_9)
P_s5 = pl("Closed by a `_` part label", "B(A) & (A.d: <5)", [A_D, B_CP], *Q3, tag=CA_T)
ok_s5b = refused("B(A) & (B.d: <5)", [A_D, B_CP], RULE2_9)
pl("The body using the argument alone", "B(A) & (A.d: <5)", [A_D, B_AL], *QDD, tag=CA_T)
pl("Through the body's path", "B(A) & (B.p.d: <5)", [A_D, B_P], *QDD, tag=CA_T)
pl("Through the call, the list", "B(A) & (B.d: <5)", [A_D, B_LS], *Q3, tag=CA_T)
pl("The caller's own label, under a closing body", "B([a = A]) & (a.h: <5)", [A_H, B_CL], *Q3, tag=CA_T)
ok_s6, r_s6 = rl("The caller's label, then the binding's name", "B([a = A]) & (A.h: <5)", [A_H, B_XX], "condition 4",
                 "the caller's label `a` is made on the spot (condition 4); the read is `a.h`", OWN_T)
ok_s7, r_s7 = rl("Used twice in the caller's text", "B(A) SEQ A & (A.d: <5)", [A_D, B_XX], "condition 1",
                 "the binding is not referenced unambiguously (condition 1); label the uses", AD_T)
P_s8 = pl("The caller's read through the shorthand", "B(A) & (A.d: <5)", [A_D, B_XX], *Q3, tag=AD_T)
P_s8w = pl("Written out", "B([A = A]) & (A.d: <5)", [A_D, B_XX], *Q3, tag=AD_T)
pl("The body using its argument alone", "B(A) & (A.d: <5)", [A_D, B_XX], *Q3, tag=ARGT)
P_s9 = pl("Both uses", "B(A) & (A.d: <5)", [B_BOTH, A_D], ["7-3", "3-7"], "7-3 3-7", "7-3 3-7 1-2 9-9", AD_T)
P_s10 = pl("Alone first", "B(A) & (A.d: <5)", [B_AF, A_D], ["3-7", "7-3"], "7-3 3-7", "7-3 3-7 1-2 9-9", AD_T,
           tail=": the last mention, the labelled spot")
P_s10w = pl("Alone first, written out", "B([A = A]) & (A.d: <5)", [B_AF, A_D], ["3-7", "7-3"], "7-3 3-7",
            "7-3 3-7 1-2 9-9", AD_T)
ok_s11, r_s11 = rl("From outside", '[pub = B(A)] & (pub.A.h: <5)', [A_H, B_XX], "not visible",
                   "the shorthand label is protected: it adds no export (the manager's reading (b))", AD_T)
P_s12 = pl("Used twice alone, the last mention", "pair(A) & (A.d: <5)", [A_D, PAIR], ["7,3", "3,7"], "3,7 7,3",
           "7,3 3,7 1,2", CP_T)
P_s13 = pl("Example 1, the spot labelled, by the argument's name", "B(A) & (A.d: <100)", [ADIG,
           "B(rx) := /${[dd = rx]}xx/"], ["42xx", "100xx", "042xx"], "x100xx 42xx", "100xx 42xx 7xx 300xx", NS_T,
           )
sh_arms = {"pins": sh_pin, "every body: the shorthand and `B([A = A])` alike": not sh_bad,
           "labelled `A.d`": wh_(P_s1, QDD[0]) == [False, True, True], "listed": wh_(P_s2, Q3[0]) == [True, False],
           "closed": wh_(P_s3, Q3[0]) == [True, False], "`c.d` closed refused (rule 2)": ok_s4,
           "`B.d` closed refused (rule 2)": ok_s4b, "`_p`": wh_(P_s5, Q3[0]) == [True, False],
           "`B.d` under `_p` refused": ok_s5b, "the caller's label then `A.h` refused": ok_s6,
           "used twice refused": ok_s7, "shorthand = written out": P_s8 is not None and P_s8w is not None and
           answers(P_s8, pop("37x", 3)) == answers(P_s8w, pop("37x", 3)),
           "both uses: the last mention, the alone spot": wh_(P_s9, ["7-3", "3-7"]) == [True, False],
           "alone first: the last mention, the labelled spot": wh_(P_s10, ["3-7", "7-3"]) == [False, True],
           "alone first written out alike": P_s10w is not None and answers(P_s10, pop("37-", 3)) ==
           answers(P_s10w, pop("37-", 3)), "from outside refused": ok_s11,
           "pair alone twice": wh_(P_s12, ["7,3", "3,7"]) == [True, False],
           "example 1 labelled": wh_(P_s13, ["42xx", "100xx"]) == [True, False]}
check("SHORTHAND", all(sh_arms.values()), "arms failing: %s (bodies differing: %s)"
      % ([k for k, v in sh_arms.items() if not v] or "none", sh_bad or "none"))

unit9("PATHS", "path-rules (ruled): rule 2 (no underscore label crossed unless it is the start), rule 3 (any label a "
      "start), rule 4 (skip), rules 5 and 6 (from outside)")
pa_pin = pinned("PATHS", [
    (PATHS_T, "1. in the label DAG there is a target label and a starting label. The starting label has at least one "
              "path to the target label"),
    (PATHS_T, "2. the path may not contain any underscore labels full or prefix unless the underscore prefix label is "
              "the start"),
    (PATHS_T, "3. within a binding, any label on the path may be used as a start label"),
    (PATHS_T, "4. if a legal path exists a.b.c and c can be unambiguously referenced from a, then b can be skipped a.c"),
    (PATHS_T, "5. From outside, the start is the binding's name, a macro's name at its call, or a label written on the "
              "use. The path then continues into that binding's tree by rules 1, 2 and 4."),
    (PATHS_T, "6. A part used alone inside a binding is crossed from outside as an underscore label is, and is a start "
              "inside its own binding."),
    (RULE_T, "stands for which label may START a path")])
ok_p1, r_p1 = rl("Outer the caller's, inner private", "[n = [_x = P]] & (n.d: <5)", [P_], RULE2_9,
                 "the path crosses `_x`, not its start (rule 2); the read is `_x.d`", PATHS_T)
P_p2 = pl("The private label as the start", "[n = [_x = P]] & (_x.d: <5)", [P_], ["37", "73", "3"], "73 37",
          "37 73 14", PATHS_T)
P_p3 = pl("Outer private, inner the caller's", "[_x = [n = P]] & (n.d: <5)", [P_], ["37", "73", "3"], "73 37",
          "37 73 14", PATHS_T)
ok_p4, r_p4 = rl("A blank label in the stack", "[l = [_ = P]] & (l.d: <5)", [P_], RULE2_9,
                 "the path crosses the blank label (rule 2); no label reads `d` there", PATHS_T)
ok_p5, r_p5 = rl("Something between the two labels", '[n = [_x = P] SEQ "!"] & (n.d: <5)', [P_], RULE2_9,
                 "the path crosses `_x` (rule 2)", PATHS_T)
ok_p6, r_p6 = rl("Through a call, a private label in the body", "B(A) & (B.n.h: <5)", [A_H, B_ST], RULE2_9,
                 "the path crosses the body's `_x` (rules 5 and 2); `B(A) & (B.h: <5)` alike", PATHS_T)
ok_p6b = refused("B(A) & (B.h: <5)", [A_H, B_ST], RULE2_9)
ok_p6c = refused("B(A) & (B._x.h: <5)", [A_H, B_ST], RULE2_9)
P_p7 = pl("Through a call, the middle label skipped", "B(A) & (B.h: <5)", [A_H, B_PH], *Q3, tag=PATHS_T,
          tail=": rule 4 (the manager's reading (f))")
P_p7b = run("B(A) & (B.p.h: <5)", [A_H, B_PH])[0]
P_p8 = pl("The caller's label, a start whatever the body stacks", "B([a = A]) & (a.h: <5)", [A_H, B_ST], *Q3,
          tag=PATHS_T, tail=": the manager's reading (e)")
ok_p9, r_p9 = rl("From outside, a part used alone", "X2 & (X2.h: <5)", [A_H, X2_], "not visible",
                 "A is used alone in X2 (rule 6); `X2 & (X2.A.h: <5)` alike; inside X2 `A.h` is legal", PATHS_T)
ok_p9b = refused("X2 & (X2.A.h: <5)", [A_H, X2_], "not visible")
P_p9c = run('A SEQ "!" & (A.h: <5)', [A_H])[0]
P_p10 = pl("His body, the owner's private label read bare", "A(n:, /\\d/)", [OWNB], ["5", "7", "55"], "7 5", "5 7 5 3",
           LO_T, tail="") if False else None
pa_arms = {"pins": pa_pin, "a private label inside the start refused": ok_p1, "`_x` a start": wh_(P_p2, ["37", "73",
           "3"]) == [True, False, False], "a private label outside the start": wh_(P_p3, ["37", "73", "3"]) ==
           [True, False, False], "a blank label refused": ok_p4, "something between refused": ok_p5,
           "through a call, `_x` in the body": ok_p6 and ok_p6b and ok_p6c,
           "rule 4 through a call = the full path": P_p7 is not None and P_p7b is not None and
           answers(P_p7, pop("37x", 3)) == answers(P_p7b, pop("37x", 3)),
           "the caller's label a start": wh_(P_p8, Q3[0]) == [True, False],
           "rule 6 from outside": ok_p9 and ok_p9b, "rule 6, a start inside": P_p9c is not None}
check("PATHS", all(pa_arms.values()), "arms failing: %s (refusals: %s; %s)" %
      ([k for k, v in pa_arms.items() if not v] or "none", r_p1, r_p4))

unit9("STACKCHAIN", "stacked-chain ANSWERED by path-rules: two public stacked labels chain (rule 1); `n.d` by rule 4, "
      "`m.d` by rule 3; from outside, rule 5")
P_c1 = pl("The chain", "[n = [m = P]] & (n.m.d: <5)", [P_XX], *Q3, tag=SC_T, tail=": rule 1")
P_c2 = pl("The first name", "[n = [m = P]] & (n.d: <5)", [P_XX], *Q3, tag=SC_T, tail=": rule 4")
P_c3 = pl("The second name", "[n = [m = P]] & (m.d: <5)", [P_XX], *Q3, tag=SC_T, tail=": rule 3")
P_c4 = pl("Two spots, the nested form", "[n = ([m = P])] & (n.m.d: <5)", [P_XX], *Q3, tag=SC_T)
P_c5 = pl("From outside, the chain", "X & (X.n.m.h: <5)", [A_H, X_MN], *Q3B, tag=SC_T)
P_c6 = pl("From outside, by name", "X & (X.h: <5)", [A_H, X_MN], *Q3B, tag=SC_T, tail=": rule 4")
P_c7 = run("X & (X.n.h: <5)", [A_H, X_MN])[0]
P_c8 = run("X & (X.m.h: <5)", [A_H, X_MN])[0]
QK9 = pop("37x!", 3)
sc_ans = [answers(p_, QK9) if p_ is not None else None for p_ in (P_c1, P_c2, P_c3, P_c4)]
sc_out = [answers(p_, QK9) if p_ is not None else None for p_ in (P_c5, P_c6, P_c7, P_c8)]
check("STACKCHAIN", None not in sc_ans and len(set(map(str, sc_ans))) == 1 and None not in sc_out and
      len(set(map(str, sc_out))) == 1 and wh_(P_c1, Q3[0]) == [True, False] and wh_(P_c5, Q3B[0]) == [True, False]
      and " ruled " in piece8(SC_T).split("\n")[0],
      "inside: `n.m.d`, `n.d`, `m.d`, the nested form %s; from outside `X.n.m.h`, `X.h`, `X.n.h`, `X.m.h` %s; the piece "
      "ruled %s" % ("alike" if None not in sc_ans and len(set(map(str, sc_ans))) == 1 else sc_ans and "DIFFER",
                    "alike" if None not in sc_out and len(set(map(str, sc_out))) == 1 else "DIFFER/REFUSED",
                    " ruled " in piece8(SC_T).split("\n")[0]))

unit9("TABLE", "the ownership table READ from core.md (header, column sentence, rows, cells), every read run")
_own = piece8(OWN_T)
if s9("p5"):
    _own = _own.replace("| `h` bare (line 1) |", "| `h` a compile error (line 1) |", 1)
_ow = ws(_own)
COLB = dict(re.findall(r"(alone|labelled|listed|closed|stacked) `(/[^`]*/)`", _ow.split("the column says:", 1)[1]
                       .split("The first row", 1)[0])) if "the column says:" in _ow else {}
_mm = re.search(r"the three modes: (WHOLE .*?\])\.", _ow)
T_EXP = _mm.group(1) if _mm else ""
T_WH, T_SR, T_FA = modes_of(T_EXP) if T_EXP else ([], "", "")
_rows = [l_ for l_ in _own.split("\n") if l_.startswith("|")]
_hdr = [c.strip() for c in _rows[0].strip("|").split("|")] if _rows else []
_cols = []
for h_ in _hdr[1:]:
    k_ = [k for k in ("alone", "labelled", "listed", "closed", "stacked") if k in h_]
    _cols.append(k_[0] if len(k_) == 1 else None)
tb_bad, tb_n, tb_rows = [], 0, 0
if len(_cols) != 5 or None in _cols or sorted(_cols) != sorted(COLB) or not T_EXP:
    tb_bad.append(("the header or the column sentence unread", _hdr, sorted(COLB), T_EXP))
for l_ in _rows[2:]:
    cs = [c.strip() for c in l_.strip("|").split("|")]
    row = next((r_ for k_, r_ in WRITERS if k_ in cs[0]), None)
    if row is None:
        tb_bad.append(("a row of an unknown writer", cs[0]))
        continue
    tb_rows += 1
    for col, cell in zip(_cols, cs[1:]):
        if col not in COLB:
            continue
        for rd, legal in cell_reads(cell) + cell_reads(cs[0], header=True):
            e, b = cell_prog(row, COLB[col], rd)
            Pg, err = run(e, b)
            tb_n += 1
            got = fmt(Pg, T_WH, T_SR, T_FA) if Pg is not None else None
            ok = (got == T_EXP) if legal else (Pg is None and not err.startswith("CRASH"))
            print("   %s %-8s `%s`: %s%s" % (row, col, rd, ("legal" if Pg else "refused: " + err[:90]),
                                             "" if ok else "   <-- DISAGREES (the cell says %s)" %
                                             ("legal" if legal else "a compile error")))
            if not ok:
                tb_bad.append((row, col, rd, e, "legal" if Pg else err[:120]))
check("TABLE", not tb_bad and tb_rows == 5, "%d rows read (5 writers), %d columns from the header and the column "
      "sentence, %d reads run against the cells' legality and the piece's three-mode answer; disagreeing: %s"
      % (tb_rows, len(_cols), tb_n, tb_bad or "none"))
pl("A blank label in the stack", "", [], [], "", "", OWN_T) if False else None
rl("A blank label in the stack", "[l = [_ = P]] & (l.d: <5)", [P_], RULE2_9,
   "the path crosses the blank label (core/labels/rule/paths rule 2)", OWN_T)
rl("The caller's label, then the binding's name", "B([a = A]) & (A.h: <5)", [A_H, B_XX], "condition 4",
   "the caller's label `a` is made on the spot (condition 4); the read is `a.h`", OWN_T)
pl("The caller's list", "[(=) = A] SEQ /xx/ & (h: <5)", [A_H], *Q3, tag=OWN_T)

unit9("NAMEGRID", "the name grid over the six path rules and the shorthand: spelling x occurrences x read kind; each "
      "cell its deciding sentence READ from its piece and a run; an undecided cell printed")
SXL9 = "S(l:) := /(?<:${l}>\\d)/"
G9 = [   # (spelling, occurrences, read kind, program, binds, expected, deciding piece, its sentence)
    ("A.h", "once, alone", "plain", "B(A) & (A.h: <5)", [A_H, B_XX], "legal", AD_T, "whatever B's body does with the spot"),
    ("A.h", "once, labelled", "plain", "B(A) & (A.h: <5)", [A_H, B_PH], "legal", AD_T, "whatever B's body does with the spot"),
    ("A.h", "once, listed", "plain", "B(A) & (A.h: <5)", [A_H, B_LS], "legal", AD_T, "whatever B's body does with the spot"),
    ("A.h", "once, closed", "plain", "B(A) & (A.h: <5)", [A_H, B_CL], "legal", AD_T, "whatever B's body does with the spot"),
    ("A.h", "once, `_p`", "plain", "B(A) & (A.h: <5)", [A_H, B_CP], "legal", AD_T, "whatever B's body does with the spot"),
    ("A.h", "once, stacked", "plain", "B(A) & (A.h: <5)", [A_H, B_ST], "legal", AD_T, "whatever B's body does with the spot"),
    ("A.h", "once, two public stacked", "plain", "B(A) & (A.h: <5)", [A_H, B_MN], "legal", AD_T,
     "whatever B's body does with the spot"),
    ("A.h", "twice, alone", "plain", "pair(A) & (A.h: <5)", [A_H, PAIR], "legal", AD_T, "the same-label-twice rules"),
    ("A.h", "twice, alone", "group", 'pair(A) & some((A.h: "3"))', [A_H, PAIR], "legal", AD_T,
     "the same-label-twice rules"),
    ("A.h", "labelled, then alone", "plain", "B(A) & (A.h: <5)", [A_H, "B(rx) := /${[p = rx]}${rx}xx/"], "legal", AD_T,
     "the same-label-twice rules"),
    ("A.h", "alone, then labelled", "plain", "B(A) & (A.h: <5)", [A_H, "B(rx) := /${rx}${[p = rx]}xx/"], "legal", AD_T,
     "the same-label-twice rules"),
    ("A.h", "never placed", "plain", "B(A) & (A.h: <5)", [A_H, "B(rx) := /xx/"], "notmod", AD_T, "never placed, the "
     "never-pass warning"),
    ("A.h", "the caller's own label too", "plain", "B([a = A]) & (A.h: <5)", [A_H, B_XX], "refused", AD_T,
     "the caller's own `B([a = A])` makes `A.d` a compile error"),
    ("A.h", "used twice by the caller", "plain", "B(A) SEQ A & (A.h: <5)", [A_H, B_XX], "refused", AD_T,
     "Condition 1"),
    ("A.h", "from outside, through the caller's label", "plain", "[pub = B(A)] & (pub.A.h: <5)", [A_H, B_XX],
     "refused", AD_T, "it adds no export"),
    ("B.h", "alone", "plain", "B(A) & (B.h: <5)", [A_H, B_XX], "refused", OWN_T, "no label: `B.h` a compile error"),
    ("B.p.h", "labelled", "plain", "B(A) & (B.p.h: <5)", [A_H, B_PH], "legal", OWN_T, "`B.p.h` (rule 5)"),
    ("B.h", "labelled", "plain", "B(A) & (B.h: <5)", [A_H, B_PH], "legal", PATHS_T, "`B.d` by rule 4 where unambiguous"),
    ("B.h", "listed", "plain", "B(A) & (B.h: <5)", [A_H, B_LS], "legal", OWN_T, "`B.h` (transform-export)"),
    ("B.h", "closed", "plain", "B(A) & (B.h: <5)", [A_H, B_CL], "refused", OWN_T, "none: `B.h` a compile error (rule 2)"),
    ("B.n.h", "stacked", "plain", "B(A) & (B.n.h: <5)", [A_H, B_ST], "refused", PATHS_T,
     "the path crosses the body's `_x`"),
    ("B._x.h", "stacked", "plain", "B(A) & (B._x.h: <5)", [A_H, B_ST], "refused", OWN_T, "`B._x.h` a compile error"),
    ("B.n.m.h", "two public stacked", "plain", "B(A) & (B.n.m.h: <5)", [A_H, B_MN], "legal", SC_T, "rule 1"),
    ("B.m.h", "two public stacked", "plain", "B(A) & (B.m.h: <5)", [A_H, B_MN], "legal", SC_T, "rule 1"),
    ("B.p.h", "called twice", "plain", "B(A) SEQ B(A) & (B.p.h: <5)", [A_H, B_PH], "refused", CP_T,
     "called more than once, a plain read is the compile error"),
    ("B.p.h", "called twice", "group", 'B(A) SEQ B(A) & some((B.p.h: "3"))', [A_H, B_PH], "legal", CP_T,
     "a group question reads every call's settings"),
    ("a.h", "closed", "plain", "B([a = A]) & (a.h: <5)", [A_H, B_CL], "legal", OWN_T, "`a.h`: another door"),
    ("a.h", "stacked", "plain", "B([a = A]) & (a.h: <5)", [A_H, B_ST], "legal", PATHS_T, "whatever the body stacks around them"),
    ("x", "a sent label, stacked", "plain", "B(S(x:)) & (x: <5)", [SXL9, B_ST], "legal", OWN_T, "`x` bare"),
    ("n.d", "inside, outer public, inner private", "plain", "[n = [_x = P]] & (n.d: <5)", [P_], "refused", PATHS_T,
     "2. the path may not contain any underscore labels"),
    ("_x.d", "inside, the private label the start", "plain", "[n = [_x = P]] & (_x.d: <5)", [P_], "legal", PATHS_T,
     "unless the underscore prefix label is the start"),
    ("n.d", "inside, outer private", "plain", "[_x = [n = P]] & (n.d: <5)", [P_], "legal", PATHS_T,
     "3. within a binding, any label on the path may be used as a start label"),
    ("l.d", "inside, a blank layer", "plain", "[l = [_ = P]] & (l.d: <5)", [P_], "refused", PATHS_T,
     "underscore labels full or prefix"),
    ("l.d", "inside, a blank layer", "group", 'NOT [l = [_ = P]] & some((l.d: "3"))', [P_], "refused", PATHS_T,
     "underscore labels full or prefix"),
    ("n.m.d", "inside, two public", "plain", "[n = [m = P]] & (n.m.d: <5)", [P_XX], "legal", SC_T, "rule 1"),
    ("X.n.m.h", "from outside", "plain", "X & (X.n.m.h: <5)", [A_H, X_MN], "legal", SC_T, "rule 5"),
    ("X.h", "from outside", "plain", "X & (X.h: <5)", [A_H, X_MN], "legal", SC_T, "rule 4"),
    ("X2.h", "from outside, a part used alone", "plain", "X2 & (X2.h: <5)", [A_H, X2_], "refused", PATHS_T,
     "6. A part used alone inside a binding is crossed from outside"),
    ("A.h", "inside X2, a part used alone", "plain", 'A SEQ "!" & (A.h: <5)', [A_H], "legal", PATHS_T,
     "is a start inside its own binding"),
]
if s9("p6"):
    G9[0] = G9[0][:5] + ("refused",) + G9[0][6:]
g9_bad, g9_und = [], []
for sp_, occ_, kind_, e, b, want, where, sent in G9:
    Pg, err = run(e, b)
    got = "legal" if Pg is not None else ("CRASH" if err.startswith("CRASH") else "refused")
    if want == "notmod":
        has = ws(sent) in ws(piece8(where))
        print("   NOT MODELLED `%s` %s (%s): decided by [%s] \"%s\" %s; the engine runs it %s" % (
            sp_, occ_, kind_, where, sent, "(found)" if has else "(MISSING)", got))
        g9_und.append((sp_, occ_, where))
        if not has:
            g9_bad.append((sp_, occ_, "sentence missing"))
        continue
    has = ws(sent) in ws(piece8(where))
    ok = got == want and has
    print("   DECIDED `%s` %s (%s): %s [%s \"%s\"%s]" % (sp_, occ_, kind_, got, where, sent[:60],
                                                       "" if has else " MISSING"))
    if not ok:
        g9_bad.append((sp_, occ_, kind_, want, got, has, (err or "")[:100]))
check("NAMEGRID", not g9_bad, "%d cells: decided %d, not modelled %d (%s); disagreeing: %s" % (
    len(G9), len(G9) - len(g9_und), len(g9_und), g9_und, g9_bad or "none"))

unit9("LIBLINES", "the library's provided bodies under the caller's shorthand (shorthand-is-callers): each "
      "`A.d` through a provided call against its written-out `[A = A]`")
LB9 = [("identity", "identity(A) & (A.d: <5)", [A_D, IDN], Q1, "lib/convention/argument-labels",
        "The same read through the argument's name"),
       ("peek", "peek(A) SEQ /\\d/ & (A.d: <5)", [A_D], Q1, "lib/control/peek",
        "Through the argument's name"),
       ("when", "W(A, (A.h: <5))", [W_AB, A_H], Q1, "lib/control/when", "Through the argument's name"),
       ("atomic", "atomic(A) & (A.d: <5)", [A_D], Q1, "lib/control/atomic", "Through the argument's name"),
       ("hits", "hits(A) & (A.d: <5)", [A_D], (["a1b3", "a3b9", "ab"], "x9 3", "a9b3 c7"), "lib/search/hits",
        "Through the argument's name")]
lb_bad = []
for nm_, e, b, q_, tag_, lab_ in LB9:
    Pg = pl(lab_, e, b, *q_, tag=tag_)
    wo = e.replace("(A,", "([%s = A]," % ("_" if s9("p7") else "A")).replace("(A)", "([%s = A])" %
                                                                            ("_" if s9("p7") else "A"), 1)
    X9[0] = True
    Pw = run(wo, b)[0]
    same = Pg is not None and Pw is not None and answers(Pg, pop("37x", 3)) == answers(Pw, pop("37x", 3))
    print("   %s: `%s` against `%s`: %s" % (nm_, e, wo, "alike" if same else "DIFFER or refused"))
    if not same:
        lb_bad.append(nm_)
P_li1 = pl("A labelled call, through the macro's name", "", [], [], "", "", CP_T) if False else None
ok_li2, r_li2 = rl("A labelled call, through the macro's name", "[h = hits(/\\d+/)] & (hits.hit: 3)", [], "condition 4",
                   "a label is made on that use (condition 4, a reading); the read is `h.hit`", CP_T)
check("LIBLINES", not lb_bad and ok_li2, "%d provided bodies read by the argument's name, each against its "
      "written-out form over the texts of `37x`: differing %s; the labelled call's name refused %s" %
      (len(LB9), lb_bad or "none", ok_li2))

unit9("EXACTCOUNT", "exact-count-unspecified (ruled, \"agree error\"): `_` into a whole count is the compile error; "
      "the three explicit spellings run")
EC_T = UN_T
ec_pin = pinned("EXACTCOUNT", [(EC_T, "The underscore where a body writes an exact count (`{${n}}`) is a compile "
                                      "error (his ruling"),
                               (EC_T, "`0`, the count left out of the body, or `rx.repeat(x, _, _)`"),
                               (CNT_T, "where a body writes an exact count")])
ok_e1, r_e1 = rl("An exact count", "E(rx.digit, _)", ["E(x, n) := /(?:${x}){${n}}/"], "no form without the part",
                 "his ruling, exact-count-unspecified", EC_T)
P_e2 = pl("The count 0", "E(rx.digit, 0)", ["E(x, n) := /(?:${x}){${n}}/"], QR, "x1234567", "1234567 12", EC_T,
          tail=": the section removed")
P_e3 = pl("The count left out of the body", "E0(rx.digit)", ["E0(x) := /(?:${x})/"], QR, "x1234567", "1234567 12",
          EC_T)
P_e4 = pl("Both bounds unspecified", "rx.repeat(rx.digit, _, _)", [], QR, "x1234567", "1234567 12", EC_T)
ok_e5, r_e5 = rl("The width unspecified", "padded_to(rx.digit, _)", [], "no form without the part",
                 "the body writes the width as an exact count (exact-count-unspecified)", "lib/modifiers/padded-to")
ec_rej = "rejected" in entry8(EC_T) and ws("how about it matches 0 meaning the section is removed") in ws(entry8(EC_T))
check("EXACTCOUNT", ec_pin and ok_e1 and ok_e5 and wh_(P_e2, QR) == [True, False, False, False] and
      wh_(P_e3, QR) == [False, False, False, False] and wh_(P_e4, QR) == [True] * 4 and ec_rej,
      "`E(rx.digit, _)` refused %s (%s); `0` %s; left out %s; `_, _` %s; his count-0 proposal in the details as not "
      "taken %s" % (ok_e1, r_e1, wh_(P_e2, QR), wh_(P_e3, QR), wh_(P_e4, QR), ec_rej))

unit9("CAPSET", "capture-in-set (ruled: error) for `|` and `&`; the two other cases the manager's readings")
CS_T = "lib/structural/capture/in-set"
cs_head = piece8(CS_T).split("\n")[0]
cs_pin = pinned("CAPSET", [(CS_T, "His words: \"capture-in-set: error.\""),
                           (CS_T, "a value left of `:` and inside a group question: compile errors for now (the "
                                  "manager's conservative readings")])
ok_cs1, r_cs1 = rl("Inside a union", '/(?<h>\\d)?x/ & (h: "3" | capture("h"))', [], "inside a set operator",
                   "his ruling; `(h: <5 & capture(\"h\"))` alike", CS_T)
ok_cs2, r_cs2 = rl("Inside an intersection", '/(?<h>\\d)?x/ & (h: <5 & capture("h"))', [], "inside a set operator",
                   "his ruling", CS_T)
ok_cs3 = refused('/(?<h>\\d)?x/ & ($a: capture("h"))', [], "capture")
ok_cs4 = refused('/(?<h>\\d)?x/ & some((h: capture("h")))', [], "capture")
P_cs5 = pl("The plain request", '/(?<h>\\d)?x/ & (h: capture("h"))', [], ["3x", "5x", "x"], "5x 3x", "3x 5x x", CS_T)
cs_r1 = run('/(?<h>\\d)?x/ & (h: "3" | capture("h"))')
cs_r2 = run('/(?<h>\\d)?x/ & (h: <5 & capture("h"))')
cs_r3 = run('/(?<h>\\d)?x/ & (h: capture("h"))')[0]
check("CAPSET", cs_pin and " ruled " in cs_head and ok_cs1 and ok_cs2 and ok_cs3 and ok_cs4 and cs_r1[0] is None and cs_r2[0] is None and
      not cs_r1[1].startswith("CRASH") and not cs_r2[1].startswith("CRASH") and cs_r3 is not None,
      "status line `%s`; `|` refused %s (%s), `&` refused %s; the plain request legal %s" % (
          cs_head[:90], cs_r1[0] is None, (cs_r1[1] or "")[:80], cs_r2[0] is None, cs_r3 is not None))

unit9("OPTIONS", "the manager's two closures that stand, marked readings following from ruled words; the constant "
      "half ruled (R-1)")
OP_T = "lib/builtin/options"
op_pin = pinned("OPTIONS", [(OP_T, "may stand mid-file and applies from the statement on"),
                            (OP_T, "A literal the caller writes as an argument takes the caller's file's options"),
                            (OP_T, "options-reach-constants: yes")])
op_open = "open options-" in piece8(OP_T)
check("OPTIONS", op_pin and not op_open, "the position reading, the argument reading and the ruled constant half "
      "found in %s: %s; an open options line left: %s" % (OP_T, op_pin, op_open))

unit9("FLAGS", "R-1 options-reach-constants (ruled: yes) and R-2 option-hole-explicit (ruled: explicit), on predfix84's "
      "flag engine, and the manager's readings each names")
FL_T = "core/patterns/flags"
fl_pin = pinned("FLAGS", [(OP_T, "Program options reach a string constant written after the statement in that file"),
                          (OP_T, "`x` never applies to a string"),
                          (FL_T, "or put into it by an option hole"),
                          ("core/holes/option", "An `i` or `-i` it puts into the literal is explicit"),
                          ("core/holes/flags", "An `i` or `-i` an option hole puts into a literal is explicit")])
FCAND.update(opthole="explicit", const="reach", position="anywhere")
if s9("p20"):
    FCAND["opthole"] = "weak"
OFT1 = ", o := `\"i\"`, w := `/ab/` in a library file that sets nothing"
P_f1 = fr("/(?${o})${w}/", OFT1)
fl("Through an option hole", "/(?${o})${w}/", OFT1, P_f1, ["ab", "AB"], "x AB ab", "ab AB Ab", FL_T)
P_f2 = fr('"ab"', " in a program file opening `@options(i)`")
fl("A string constant", '"ab"', " in a program file opening `@options(i)`", P_f2, ["ab", "AB"], "x AB ab", "ab AB",
   OP_T)
OFT3 = " in a program file opening `@options(i)`, c := `\"ab\"` in a library file that sets nothing"
P_f3 = fr("/x${c}/", OFT3)
fl("A string from a library file", "/x${c}/", OFT3, P_f3, ["xab", "XAB", "Xab"], "xAB Xab", "xab xAB Xab", OP_T)
FMACROS["K"] = (["k"], "/${k}=1/", "library")
P_f4 = fprog({"program": [("opt", {"i": True})], "library": []}, 'K("msg")')
FMACROS.clear()
OFT6 = ", o := `\"s\"`, w := `/a.b/` in a library file that sets nothing"
P_f6 = fr("/(?${o})${w}/", OFT6)
fl("Another letter through an option hole", "/(?${o})${w}/", OFT6, P_f6, ["a\nb", "axb"], "a\nb axb", "a\nb axb", FL_T)
FCAND.update(opthole="explicit", const="reach", position="anywhere")
for t_, L_ in LINES[-4:]:
    print("   LINE [%s] %s" % (t_, L_))
FR9 = [
    ("R-2 the ruling: an `i` through an option hole passes into `w`", P_f1.whole("AB")),
    ("R-1 the ruling: `\"ab\"` under `@options(i)` matches `AB`", P_f2.whole("AB") and P_f2.whole("ab")),
    ("R-1 (a): the weak value on a string does not propagate across an import (a library string in a weakly "
     "insensitive program's hole: `xAB` FAILS, `Xab` HOLDS)", not P_f3.whole("xAB") and P_f3.whole("Xab")),
    ("R-1 (c): a matched key the caller writes follows the caller's file's `i` (`K(\"msg\")`, K(k) := `/${k}=1/` in a "
     "library file: `MSG=1` HOLDS)", P_f4.whole("MSG=1") and P_f4.whole("msg=1")),
    ("R-2 (b): another letter through an option hole (`s`) is not inherited at the hole: `a\\nb` FAILS",
     not P_f6.whole("a\nb") and P_f6.whole("axb")),
]
for a, v in FR9:
    print("   %s: %s" % ("SUPPORTED" if v else "NOT SUPPORTED", a))
print("   NOT MODELLED: R-2 (a) for a macro's parameter: the flag engine resolves an option hole's name as a binding "
      "only; the binding route is the ruled line itself (o := `\"i\"`)")
print("   UNTESTABLE: R-1 (b), a string used as a name not matched against the subject (`capture(\"name\")`, a warning "
      "selector's names) is unaffected: the flag engine runs no capture request or selector")
check("FLAGS", fl_pin and all(v for _, v in FR9), "pins %s; %d runs: %s" % (
    fl_pin, len(FR9), [a[:40] for a, v in FR9 if not v] or "all as ruled and read"))

unit9("PARKED","the parked piece (his discussion on capture-in-set): a form of its own for effects, a condition "
      "operator; trigger and source")
PK_T = "parked/ideas/effect-form"
pk = piece8(PK_T)
pk_ok = " parked " in pk.split("\n")[0] and "a second kind of effect is built" in pk and ws(
    "it's a tool not a logical proofs language") in ws(entry8(PK_T)) and ws("we could for total logical consistency "
                                                                             "create a new operator for conditions to "
                                                                             "reflect its different relationship with "
                                                                             "patterns.") in ws(entry8(PK_T))
check("PARKED", pk_ok, "%s present, parked, its trigger and his words in the details: %s" % (PK_T, pk_ok))

unit9("EXPAND", "the expansion drill: each sugar form against its written-out form READ from the documents")
_ad = ws(piece8(AD_T))
_wo = re.search(r"Written out, `(\w+)\((\w+)\)` is `([^`]*)` for every body", _ad)
QX9 = ['3xx', '7xx', '7-3', '3-7', '37', '73', '3', '7', 'x', '3!', '7!', '']
DRILL9 = [(body_, (_wo.group(3) if _wo else "?") + " & (A.d: <5)") for _, body_, _ in SH_BODIES + [
    ("both", B_BOTH, None), ("alone first", B_AF, None), ("pair", "B(rx) := /${rx},${rx}/", None)]]
xd9 = []
for body_, wo_ in DRILL9:
    Pa, ea = run("B(A) & (A.d: <5)", [A_D, body_])
    Pb, eb = run(wo_, [A_D, body_])
    same = Pa is not None and Pb is not None and answers(Pa, QX9) == answers(Pb, QX9)
    print("   %s `%s` / `%s`" % ("AGREE" if same else "DIFFER", body_, wo_))
    if not same:
        xd9.append((body_, wo_, ea, eb))
Pn1, Pn2 = run("[n = [m = P]] & (n.m.d: <5)", [P_XX])[0], run("[n = [m = P]] & (m.d: <5)", [P_XX])[0]
chain_same = Pn1 is not None and Pn2 is not None and answers(Pn1, QX9) == answers(Pn2, QX9)
check("EXPAND", not xd9 and _wo is not None and chain_same, "%d bodies: `B(A)` against the written-out form read from "
      "the documents (%s), every mode over %d texts; differing: %s; the chain against its skip: %s" %
      (len(DRILL9), _wo.group(3) if _wo else "UNREAD", len(QX9), xd9 or "none", "alike" if chain_same else "DIFFER"))

unit9("READINGS", "the manager's readings a run can decide (shorthand-is-callers (a)-(d); path-rules (d)-(g))")
P_ra = run("B(A) & (A.d: <5)", [A_D, B_AF])[0]
if s9("p13"):
    P_ra = run('/(?<d>\\d)/ SEQ "-" SEQ /\\d/ & (d: <5)')[0]          # the FIRST spot's digit read
P_rb = run("[pub = B(A)] & (pub.A.d: <5)", [A_D, B_XX])[0]
P_rc = [run("B(A) & (A.h: <5)", [A_H, bb])[0] for bb in (B_XX, B_PH, B_LS, B_CL, B_ST)]
P_rd = run("[a = A] SEQ \"!\" & (A.h: <5)", [A_H])[0]
P_re = run("B([a = A]) & (a.h: <5)", [A_H, B_ST])[0]
P_rf = run("B(A) & (B.h: <5)", [A_H, B_PH])[0]
P_rf2 = run("B(A) & (B.d: <5)", [A_D, B_P])[0]
RD9 = [
    ("shorthand-is-callers (a): placed twice, the caller's label at every spot, the last mention (alone first: the "
     "labelled spot)", P_ra is not None and P_ra.whole("7-3") and not P_ra.whole("3-7")),
    ("shorthand-is-callers (b): the shorthand label protected (no export through the caller's label)", P_rb is None),
    ("shorthand-is-callers (c): the row \"an argument's binding\" reads `A.h` in every spot column",
     all(p_ is not None for p_ in P_rc)),
    ("shorthand-is-callers (d): inside the definition that makes the label, the labelled use is read by its label "
     "only", P_rd is None),
    ("path-rules (e): a caller's label is a start whatever the body stacks", P_re is not None),
    ("path-rules (f): through a call `B.h` by rule 4 where unambiguous", P_rf is not None),
    ("path-rules (f): `B.d` with two `d` in a sequence: the last mention, the body's own", P_rf2 is not None and
     P_rf2.whole("7-3") and not P_rf2.whole("3-7")),
]
for a, v in RD9:
    print("   %s: %s" % ("SUPPORTED" if v else "NOT SUPPORTED", a))
print("   UNTESTABLE: path-rules (d), the blank label is never a start: `_` has no name a path can begin with, so no "
      "program writes it (the reading follows from the spelling)")
print("   UNTESTABLE: path-rules (g), the equivalence is a picture, not a spelling: nothing runs `t` as a label")
print("   NOT MODELLED: shorthand-is-callers (a), never placed: the never-pass warning (the engine models no warning)")
check("READINGS", all(v for _, v in RD9), "%d readings run: %s" % (len(RD9), [a for a, v in RD9 if not v] or
                                                                   "all SUPPORTED"))

unit9("SWEEP", "every printed three-mode line (`rejected:` and history skipped): predfix88's engine (the 1124 "
      "extensions off) over the starting commit's documents against this one over these; every non-same status and "
      "every moved or gone answer DECLARED", 900)
OLD9 = {f: _git8("docs/design/predicates/" + f, START9) for f in DOCF}
DECL9 = dict(DECL8)                                          # predfix88's still-standing declarations
DECL9_USED_BY_88 = set(DECL8)
MOVED9 = {
    "[n = [_x = P]] & (n.d: <5)": "path-rules rule 2 (ruled): the path crosses `_x`; now the compile error line "
                                  "\"Outer the caller's, inner private\" (core/labels/rule/paths)",
    "[l = [_ = P]] & (l.d: <5)": "path-rules rule 2 (ruled): the path crosses the blank label; now a compile error line",
    "B(A) & (A.d: <5)": "shorthand-is-callers (ruled) with reading (a): a body placing the argument alone first and "
                        "labelled second reads the last mention, the labelled spot (the line \"Alone first\")",
    "B(A) & (A.h: <5)": "the line \"A label over a wider spot\" retired: the reading it showed (a label ON the spot, "
                        "for condition 4) has no use once condition 4 counts only the caller's own labels",
    "EB(rx.digit, _)": "exact-count-unspecified ruled \"agree error\": its candidate (a) line retired from the base "
                       "(to `rejected:` in the details)",
    '/(?<h>\\d)?x/ & (h: "3" | capture("h"))': "capture-in-set ruled \"error\": candidate (b)'s union line retired (to "
                                             "`rejected:`)",
    '/(?<h>\\d)?x/ & (h: <5 & capture("h"))': "capture-in-set ruled \"error\": candidate (b)'s intersection line "
                                             "retired (to `rejected:`)",
}
NOWS9 = dict(NOWS)
if s9("p14"):
    NOWS9["core.md"] = NOWS9["core.md"].replace("WHOLE `37` HOLDS, `73` FAILS, `3` FAILS / SEARCHED `73 37`",
                                                "WHOLE `37` FAILS, `73` FAILS, `3` FAILS / SEARCHED `73 37`", 1)
X9[0] = False
OLD_T9 = sw_table84(OLD9)
X9[0] = True
NEW_T9 = sw_table84(NOWS9)
sw_bad, sw_moved, sw_new, sw_gone, used9 = [], [], [], [], set()
cnt9, why9 = {}, {}
for k, vs in NEW_T9.items():
    ov = OLD_T9.get(k, [])
    for i_, (f_, ln_, st_, got_) in enumerate(vs):
        cnt9[st_] = cnt9.get(st_, 0) + 1
        if st_ != "same":
            d_ = DECL9.get((f_, k[0])) or DECL_LINE.get((f_, k[0]))
            if d_ and d_[0] == st_:
                used9.add((f_, k[0]))
                why9[d_[1][:70]] = why9.get(d_[1][:70], 0) + 1
            else:
                r_ = next((x for x in DECL_RULE if x[0] == st_ and re.search(x[1], got_)), None)
                if r_ is None:
                    sw_bad.append(("UNDECLARED", f_, ln_, st_, k[0], got_[:160]))
                else:
                    used9.add(r_[1])
                    why9[r_[2][:70]] = why9.get(r_[2][:70], 0) + 1
        o_ = ov[i_] if i_ < len(ov) else None
        if o_ and (o_[3] != got_ or o_[2] != st_):
            if k[0] in MOVED9:
                used9.add(("moved", k[0]))
            else:
                sw_moved.append((f_, ln_, k[0], o_[2], st_, o_[3][:160], got_[:160]))
    if not ov:
        sw_new.append((vs[0][0], vs[0][1], k[0]))
for k, vs in OLD_T9.items():
    if k not in NEW_T9:
        if k[0] in MOVED9:
            used9.add(("moved", k[0]))
        else:
            sw_gone.append((vs[0][0], vs[0][1], k[0], vs[0][2]))
stale9 = sorted(k for k in list(DECL9) + list(DECL_LINE) if k not in used9) + sorted(k for k in MOVED9 if ("moved", k) not in used9)
for k_, n_ in sorted(why9.items()):
    print("   DECLARED x%d: %s" % (n_, k_))
for x in sw_gone:
    print("   GONE %s:%d `%s` (was %s)" % x)
for x in sw_new:
    print("   ADDED %s:%d `%s`" % x)
for x in sw_moved:
    print("   MOVED %s:%d `%s` (old %s, now %s)\n      old: %s\n      now: %s" % x)
for x in sw_bad:
    print("   BAD %s" % (x,))
for x in stale9:
    print("   STALE DECLARATION %s" % (x,))
for k_, why in sorted(MOVED9.items()):
    print("   ANSWER MOVED OR LINE GONE (declared): `%s`: %s" % (k_, why))
check("SWEEP", OLD_T9 and not sw_bad and not sw_moved and not sw_gone and not stale9,
      "%d printed lines now (%s), %d at the starting commit under predfix88's engine; undeclared %d; moved or gone and "
      "not declared %d; declared moves %d; added %d; stale declarations %d" % (
          len(NEW_T9), ", ".join("%s %d" % kv for kv in sorted(cnt9.items())), len(OLD_T9), len(sw_bad),
          len(sw_moved) + len(sw_gone), len(MOVED9), len(sw_new), len(stale9)))

unit9("ERRSWEEP", "every printed compile-error line of the base files whose program and bindings parse: refused "
      "under this engine, no crash; each line whose legality CHANGED against predfix88's engine over the starting "
      "commit listed")


def err_lines(docs, base_only=True):
    out = []
    for f in DOCF:
        if base_only and f.endswith("_details.md"):
            continue
        for ln, L in enumerate(docs[f].split("\n"), 1):
            for mm in re.finditer(r"modes: a compile error \(`([^`]*)`((?:, [\w.]+(?:\([^()]*\))? := `[^`]*`)*)", L):
                b = ["%s := %s" % (x.group(1), x.group(2)) for x in
                     re.finditer(r", ([\w.]+(?:\([^()]*\))?) := `([^`]*)`", mm.group(2))]
                out.append((f, ln, mm.group(1), b))
    return out


es_now = err_lines(D8)
es_old = err_lines(OLD9)
es_bad, es_chg = [], []
for f_, ln_, e, b in es_now:
    Pg, err = run(e, b)
    if Pg is not None or err.startswith("CRASH"):
        es_bad.append((f_, ln_, e, "legal" if Pg is not None else err[:100]))
for f_, ln_, e, b in es_old:
    X9[0] = False
    Po, eo = run(e, b)
    X9[0] = True
    Pn, en = run(e, b)
    if (Po is None) != (Pn is None):
        es_chg.append((f_, ln_, e, "refused" if Po is None else "legal", "refused" if Pn is None else "legal"))
for x in es_chg:
    print("   LEGALITY CHANGED (a line of the starting commit) %s:%d `%s`: %s -> %s" % x)
for x in es_bad:
    print("   BAD (printed a compile error, runs legal or crashes) %s" % (x,))
check("ERRSWEEP", es_now and not es_bad, "%d compile-error lines now, each refused with no crash: bad %d; of the "
      "starting commit's %d, %d changed legality under the ruled rules (listed)" % (len(es_now), len(es_bad),
                                                                                   len(es_old), len(es_chg)))

unit9("NULLABLE", "EVID-4's known limit: no program the extended engine ran has a loop whose body can match empty")
exec(compile(_src84[_src84.index("def nullable(n):"):_src84.index("checked = list(RUN)")], P84, "exec"),
     globals())                                              # noqa: S102  predfix84's walker, verbatim
_nullable84b = nullable


def nullable(n):                                             # noqa: F811
    return False if n[0] == "ncls" else _nullable84b(n)


if s9("p16"):
    run("rx.repeat(/a?/)")
checked9 = list(RUN)
nl9 = [(e, b) for e, b, nd in checked9 if loops_nullable(nd, [])]
check("NULLABLE", not nl9, "%d programs run by the checks above (SWEEP's included), walked node by node: %d with a "
      "loop whose body can match empty%s" % (len(checked9), len(nl9), (": %s" % nl9[:4]) if nl9 else ""))

unit9("SUCCESSOR", "every earlier in-force model re-run with library.md served from its PINNED delivery commit "
      "(predfix88's runner, unchanged; nested runs routed to their own pins); each red declared by its FAIL line "
      "VERBATIM with a reason; a traceback is never declared", 3600)
PINS9 = dict(PINS8)
PINS9["predfix88"] = "50a39f8e4"                             # predfix88's delivery commit (its .out committed there)
DECLF9 = os.path.join(HERE9, "predfold1124_succ_decl.tsv")
SDECL9 = {}
if os.path.exists(DECLF9):
    for l_ in builtins.open(DECLF9, encoding="utf-8").read().split("\n"):
        if l_ and not l_.startswith("#"):
            m_, r_, why_, fl_ = l_.split("\t", 3)
            SDECL9.setdefault(m_, {})[r_] = (fl_, why_)
if s9("p17") and SDECL9:
    _k = sorted(SDECL9)[0]
    _r = sorted(SDECL9[_k])[0]
    SDECL9[_k][_r] = (SDECL9[_k][_r][0].replace("FAIL", "FAIL ", 1), SDECL9[_k][_r][1])
succ_bad, succ_n, succ_t = [], 0, {}
ORDER9 = ["predfix88"] + list(PINS8)
if not LIGHT9:
    for mname in ORDER9:
        env = {k: v for k, v in os.environ.items() if not k.endswith(("_SABOTAGE", "_ENGINE", "_PROBE", "_LIGHT",
                                                                       "_DUMPSUCC"))}
        for v_ in list(LIGHTENV8.values()) + ["PREDFIX88_LIGHT"]:
            env[v_] = "1"                                    # their own SUCCESSOR re-runs the same list: run once, here
        t0 = time.time()
        try:
            out = subprocess.run([sys.executable, "-I", "-B", P88, "--succ",
                                  os.path.join(LANES9, mname + "_evidence", mname + "_model.py"), PINS9[mname]],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env,
                                 timeout=600).stdout
        except subprocess.TimeoutExpired:
            out = "TIMEOUT: model %s did not finish in 600 s" % mname
        succ_t[mname] = time.time() - t0
        if os.environ.get("PREDFOLD1124_DUMPSUCC"):         # the declarations' source run (the lane's scratch)
            builtins.open(os.path.join(os.environ["PREDFOLD1124_DUMPSUCC"], mname + ".out"), "w").write(out)
        succ_n += 1
        lines_ = out.rstrip("\n").split("\n")
        last = lines_[-1]
        mm = re.match(r"%s_model: (\d+) checks, (\d+) failed(?: \(([^)]*)\))?$" % mname, last)
        reds = {}
        if mm and not any(x.startswith("Traceback") for x in lines_):
            for r in [x.strip() for x in (mm.group(3) or "").split(",") if x.strip()]:
                reds[r] = next((l_ for l_ in lines_ if l_.startswith("FAIL %s:" % r) or
                                re.match(r"%s\s+FAIL\b" % re.escape(r), l_)), "")
        else:
            reds["TRACEBACK"] = last
        decl = SDECL9.get(mname, {})
        print("   %-13s (library at %s, %.1f s) last line: %s" % (mname, PINS9[mname], succ_t[mname], last[:150]))
        for r, fline in sorted(reds.items()):
            d = decl.get(r)
            if r == "TRACEBACK":
                succ_bad.append((mname, "TRACEBACK"))
                print("      TRACEBACK (never declarable): %s" % fline[:300])
            elif d is None:
                succ_bad.append((mname, r, "UNDECLARED"))
                print("      %s UNDECLARED: %s" % (r, fline[:400]))
            elif d[0] != fline:
                succ_bad.append((mname, r, "TEXT CHANGED"))
                print("      %s TEXT CHANGED:\n         declared: %s\n         now:      %s" % (r, d[0][:300], fline[:300]))
            else:
                print("      %s declared: %s\n         its FAIL line: %s" % (r, d[1], fline[:240]))
        gone = sorted(set(decl) - set(reds))
        if gone:
            succ_bad.append((mname, "GREEN NOW", gone))
            print("      declared but green now: %s" % gone)
check("SUCCESSOR", LIGHT9 or (succ_n == len(ORDER9) == 15 and not succ_bad),
      "%d earlier models re-run (%.0f s in all), each red against its declared FAIL line verbatim (%d declared): %s"
      % (succ_n, sum(succ_t.values()), sum(len(v) for v in SDECL9.values()), succ_bad or "every red declared, "
         "its text unchanged; no traceback"))

unit9("QUOTES", "the owner's sentences, each PINNED to the piece (or details entry) that quotes it, and in the "
      "record at the pinned start commit; the rulings' titles cited whole")
QQ9 = [   # (his sentence, word for word; the piece that must hold it: a base tag, or "details:" + tag)
    ("shorthand-is-callers: yes thats it exactly. Setting a label closes a path (through the shorthand in that "
     "binding) but doesn't block out the target.", AD_T),
    ("Setting a label closes a path (through the shorthand in that binding) but doesn't block out the target.", RULE_T),
    ("This has been a good trajectory. We started out all open, then moved to mostly all closed. Now we are seeing "
     "the balance. Very Buddha", "details:" + RULE_T),
    ("capture-in-set: error.", CS_T),
    ("we could for total logical consistency create a new operator for conditions to reflect its different "
     "relationship with patterns.", "details:" + PK_T),
    ("it's a tool not a logical proofs language", "details:" + PK_T),
    ("exact-count-unspecified: agree error", EC_T),
    ("exact-count-unspecified: how about it matches 0 meaning the section is removed. There may be programmatic "
     "reasons someone doesn't want a stretch to exist. Although, theres probably better ways to express it.",
     "details:" + EC_T),
    ("path-rules: yes", PATHS_T),
    ("1. in the label DAG there is a target label and a starting label. The starting label has at least one path to "
     "the target label", PATHS_T),
    ("2. the path may not contain any underscore labels full or prefix unless the underscore prefix label is the "
     "start", PATHS_T),
    ("3. within a binding, any label on the path may be used as a start label", PATHS_T),
    ("4. if a legal path exists a.b.c and c can be unambiguously referenced from a, then b can be skipped a.c",
     PATHS_T),
    ("[_t = A ] is equivalent to [_ = [t = A ]]", PATHS_T),
    ("My intention of the rule was that if rx was labeled in B, you couldn't access rx directly shorthand through, "
     "or in,  B. But the read is that you can't access it at al, even through A.", "details:" + AD_T),
    ("label-doors: agree. Yes", RULE_T),
    ("5. Labels stacked on one spot are equal names of it; their order does not matter.", RULE_T),
    ("binding-as-label: yes", RULE_T),
]
TT9 = [
    '2026-11-23 OWNER RULING — shorthand-is-callers: "yes thats it exactly. Setting a label closes a path (through the '
    'shorthand in that binding) but doesn\'t block out the target."',
    '2026-11-23 OWNER RULING — capture-in-set: error; and a DISCUSSION: "we are already pushing it by using the '
    'operators that we are ... it\'s a tool not a logical proofs language"',
    '2026-11-23 OWNER RULING — exact-count-unspecified: "agree error"',
    "2026-11-23 OWNER RULING — path-rules: yes (his four rules for paths within a binding, the manager's two readings "
    "of them, and rules 5 and 6 across bindings)",
]
if s9("p18"):
    pass                                                     # the plant altered core.md as read, above
RW9 = ws(REC9)
q9_miss = []
for q, where in QQ9:
    home = entry8(where[8:]) if where.startswith("details:") else piece8(where)
    if ws(q) not in RW9 or ws(q) not in ws(home):
        q9_miss.append((q[:60], where, ws(q) in RW9))
REVR9 = "db8382c63"                                         # lane/pred-rev28 with R-1/R-2's record entries, PINNED
RWR9 = ws(_git8("docs/design/plan_row_bodies/COND-FAMILY.md", REVR9))
for q, where in (("options-reach-constants: yes", OP_T), ("option-hole-explicit: explicit", FL_T)):
    if ws(q) not in RWR9 or ws(q) not in ws(piece8(where)):
        q9_miss.append((q, where, ws(q) in RWR9))
TTR9 = ["2026-11-23 OWNER RULING — options-reach-constants: yes (a file's weak `i` reaches a string constant)",
        "2026-11-23 OWNER RULING — option-hole-explicit: explicit (an `i` given through an option hole is explicit)"]
DET9 = D8["core_details.md"] + D8["library_details.md"] + D8["parked_details.md"]
t9_miss = [t_ for t_ in TT9 if ws(t_) not in heads8(REC9) or ws('(record: "%s")' % t_) not in ws(DET9)]
t9_miss += [t_ for t_ in TTR9 if ws(t_) not in heads8(_git8("docs/design/plan_row_bodies/COND-FAMILY.md", REVR9))
            or ws('(record "%s")' % t_) not in ws(DET9)]                # cited in history only: after this lane's cut
check("QUOTES", not q9_miss and not t9_miss,
      "%d quoted sentences, each in the record at %s AND in its own piece, missing: %s; %d record titles cited whole "
      "as a `rulings:` item's record, not a title or not cited: %s" % (len(QQ9), START9, q9_miss or "none", len(TT9),
                                                                   t9_miss or "none"))

unit9("DOC", "every line this model formats occurs verbatim in the piece its tag names")
DLN9 = list(LINES)
if s9("p19") and DLN9:
    DLN9[0] = (DLN9[0][0], DLN9[0][1].replace("WHOLE `", "WHOLE `x", 1))
D8.clear()
D8.update(NOWS)
d9_miss = [(t_, L) for t_, L in DLN9 if ws(L) not in ws(piece8(t_))]
for t_, L in d9_miss:
    print("   MISSING [%s] %s" % (t_, L))
check("DOC", DLN9 and not d9_miss, "%d lines, each in its own piece; missing: %d" % (len(DLN9), len(d9_miss)))

failed9 = [n for n, ok in RESULTS if not ok]
print("predfold1124_model: %d checks, %d failed%s" % (len(RESULTS), len(failed9),
                                                     (" (%s)" % ", ".join(failed9)) if failed9 else ""))
sys.exit(1 if failed9 else 0)
