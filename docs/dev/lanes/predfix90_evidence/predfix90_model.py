#!/usr/bin/env python3
# Lane predfix90 (2026-11-25): the successor evidence model for review r90's fix of the predfold1124 fold
# (record "2026-11-25 MANAGER — review r90 (predfold1124): the dispositions; no owner words"). DESIGN EVIDENCE ONLY;
# rules nothing. It succeeds docs/dev/lanes/predfold1124_evidence/predfold1124_model.py.
#
# METHOD. predfold1124's model is LOADED unchanged up to its first check (`unit9("CONTROL"`), so its engines (and,
# through it, every older engine) and its helpers are defined. Then the r90 extension PATH10 (switched by X10[0]; off
# is predfold1124's engine, the control of SWEEP and ERRSWEEP):
#   PATH10  the path rules over the label tree of the program TEXT, across binding and call boundaries: rule 2 (no
#           underscore label on the path unless it is the start) at every level (A3, A5 (ii)); rule 6 (a part used
#           alone, crossed from outside as an underscore label is) below a label over an expression or a hole (A4);
#           rules 1 and 4 at any depth and any number of skipped labels (A1, A2, "rule 4 applies repeatedly", a
#           reading); a sent label is a start in the caller's binding whose path still obeys rule 2 below it
#           (sent-label-wall, the manager's reading until asked, A5 (i)). A legal read with one target is handed to
#           the loaded engine as its FULL path, and every part label whose content is a stack or an expression is
#           handed over parenthesised (core/labels/rule/stacked-chain: "The nested form ... reads the same"), the two
#           spellings the loaded engine walks.
# Then the 1124 checks are run AGAIN, from its own text, with DECLARED PATCHES (each must apply exactly once; a
# predecessor that drifted fails loudly): the fixes C4-C9 of review r90. Then this lane's checks: CANARY, PATHS10,
# GRID (the path rules as a SEPARATE small evaluator over a generated grid), READINGS10, and SUCCESSOR10 (C1-C3).
#
# Run (W = the worktree; any cwd):  timeout 3600 python3 -I -B W/docs/dev/lanes/predfix90_evidence/predfix90_model.py
# Its verdict is its LAST LINE, `predfix90_model: N checks, F failed`; it EXITS NON-ZERO iff that line reports one.
# PREDFIX90_SABOTAGE=pN: one deliberately wrong rule, fact or document text; its target check must FAIL, for the
# reason the plant's expected FAIL-line fragment names. PREDFIX90_SABOTAGE=all: every plant, one subprocess each.
# PREDFIX90_LIGHT=1 skips SUCCESSOR10. PREDFIX90_DUMPSUCC=DIR writes each re-run model's output there.
import builtins
import os
import re
import subprocess
import sys
import time

HERE10 = os.path.dirname(os.path.abspath(__file__))
LANES10 = os.path.normpath(os.path.join(HERE10, ".."))
W10 = os.path.normpath(os.path.join(HERE10, "..", "..", "..", ".."))
P1124 = os.path.join(LANES10, "predfold1124_evidence", "predfold1124_model.py")
UNIT_TIMEOUT10 = 240
START10 = "33abd6926"                                        # this lane's starting commit (lane/predfix90), PINNED
SAB10 = set(x for x in os.environ.get("PREDFIX90_SABOTAGE", "").split(",") if x)
LIGHT10 = os.environ.get("PREDFIX90_LIGHT") == "1"


def s10(n):
    return n in SAB10


# (plant, its target check, what it plants, the FAIL-line fragment that must name it: C9's per-plant expected arm)
PLANTS10 = [
    ("q1", "CANARY", "the PATH10 switch made a no-op (X10 forced on for the control)", "the control is not"),
    ("q2", "PATHS10", "rule 2 off below a used binding (the two-level wall lost again)", "two-level wall"),
    ("q3", "GRID", "the evaluator's rule 4 limited to ONE skipped label", "disagreeing"),
    ("q4", "GRID", "the engine's rule 6 off below a label over an expression", "disagreeing"),
    ("q5", "READINGS10", "the sent label crosses the body's blank below it (reading A5 (i) reversed)", "sent-label-wall"),
    ("q6", "PATHS10", "the reading clause \"rule 4 applies repeatedly\" dropped from core.md as read", "MISSING"),
    ("q7", "CONTROL", "a provided body's direct regex written for the wrong digit", "differing"),
    ("q8", "TABLE", "a table cell's ground changed (rule 2 -> rule 6) in core.md as read", "ground"),
    ("q9", "STACKCHAIN", "the stacked-chain lede's `m.d` sentence reversed in core.md as read", "MISSING"),
    ("q10", "READINGS", "the engine crashes on a reading's program (a CRASH is no support)", "NOT SUPPORTED"),
    ("q11", "SWEEP", "one printed answer moved in BOTH the engine's run and the document (status stays same)",
     "moved or gone and not declared 1"),
    ("q12", "ERRSWEEP", "one printed compile-error line respelled so the parser skips it", "skipped 1"),
    ("q13", "SUCCESSOR10", "a declared red's missing-line set altered", "MISSING SET CHANGED"),
    ("q14", "QUOTES", "path rule 4 altered in the base piece only", "missing: [("),
    ("q15", "DOC", "a formatted line altered", "missing: 1"),
    ("q16", "GRID", "one undecided cell given an expected answer it lacks", "undecided"),
    ("q17", "NAMEGRID", "a cell's deciding sentence dropped from its piece as read", "sentence missing"),
    ("q18", "ERRSWEEP", "a legality change of the start commit left out of the declared list", "undeclared change"),
]
HEAVY10 = {"SUCCESSOR10"}
STRICT10 = re.compile(r"^predfix90_model: (\d+) checks, (\d+) failed(?: \(([^)]*)\))?$")
if "all" in SAB10:                                           # the plant runner: each plant alone, a subprocess each
    rows, notc = [], 0
    for pn, target, what, frag in PLANTS10:
        env = {k: v for k, v in os.environ.items()}
        env["PREDFIX90_SABOTAGE"] = pn
        if target not in HEAVY10:
            env["PREDFIX90_LIGHT"] = "1"
        t0 = time.time()
        try:
            r = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__)], capture_output=True,
                               text=True, env=env, timeout=UNIT_TIMEOUT10 * (12 if target in HEAVY10 else 4))
            out_, rc_ = r.stdout + r.stderr, r.returncode
        except subprocess.TimeoutExpired:
            out_, rc_ = "TIMEOUT: plant %s did not finish in its unit time" % pn, None
        lines = out_.rstrip("\n").split("\n")
        last = lines[-1]
        mm = STRICT10.match(last)
        fl_ = next((x for x in lines if x.startswith("FAIL %s:" % target)), "")
        tb = any(x.startswith("Traceback") or re.search(r"\bCRASH [A-Z]\w*(Error|Exception)\b", x) for x in lines
                 if not x.startswith("   "))
        ok = bool(fl_) and frag in fl_ and not tb and rc_ not in (0, None) and bool(mm) and \
            target in (mm.group(3) or "").split(", ")
        notc += not ok
        rows.append((pn, target, what, ok))
        print("%s -> %s (%s): %s (%.0f s)" % (pn, target, what, "caught" if ok else "NOT CAUGHT", time.time() - t0))
        print("   last line: %s" % last)
        print("   its FAIL line (must name `%s`): %s" % (frag, fl_[:400]), flush=True)
    if not notc:
        print("   each plant turned its target check FAIL, its FAIL line naming the planted fact, with no traceback")
    print("predfix90_sabotage: %d plants, %d not caught" % (len(rows), notc))
    sys.exit(1 if notc else 0)


# ================================================================== the LOADER: predfold1124's engines, unchanged
for v in list(os.environ):
    if v.startswith(("PREDFOLD1124_", "PREDFIX88_")):
        os.environ.pop(v, None)
_src9 = builtins.open(P1124, encoding="utf-8").read()
_cut9 = _src9.index('unit9("CONTROL", ')
_file10 = __file__
__file__ = P1124                                             # noqa: F811  (the loaded code finds its siblings by it)
exec(compile(_src9[:_cut9], P1124, "exec"), globals())       # noqa: S102  (predfold1124's definitions, unchanged)
__file__ = _file10
LINES.clear()
RUN.clear()
RESULTS.clear()
X10 = [True]
P10F = dict(prog=prog, path_rules=path_rules)


def x10():
    return X10[0] or s10("q1")


# ================================================================== PATH10: the path rules over the label tree
RULE2_10 = "crosses the underscore label"
RULE6_10 = "a part used alone in it"
SENT10 = "sent-label-wall"


def _mask_conds(t):
    """t with literals blanked (holes kept) and every condition `(read: ...)` blanked: what is left is pattern text."""
    st = list(strip_keep_holes(t))
    for mm in re.finditer(r"\((?=\$?[A-Za-z_][\w.]*: )", "".join(st)):
        j = close_paren(t, mm.start())
        if j is not None and j > mm.start():
            st[mm.start():j + 1] = " " * (j + 1 - mm.start())
    return "".join(st)


class Und(Exception):
    """the walker cannot decide this read: it is handed to the loaded engine as written."""


def _env_of(binds):
    bd, heads = {}, {}
    for b in binds:
        h = head_of(b)
        if h:
            heads[h[0]] = h
        else:
            n_, _, body = b.partition(" := ")
            bd[n_.strip()] = body.strip()
    return bd, heads


def _leaves(t, lo, hi, params, bd, heads):
    """the leaves written in t[lo:hi] (pattern text only): (position, end, kind, name, call args)."""
    st = _mask_conds(t)
    out = []
    lab_at = set(mm.start(1) for mm in re.finditer(r"\[(\w+) = ", st))
    for mm in re.finditer(r"(?<![\w.$])([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)(?![\w])", st[lo:hi]):
        p, nm = lo + mm.start(1), mm.group(1)
        if p in lab_at or st[lo + mm.end():lo + mm.end() + 1] == ":":
            continue
        nxt = st[lo + mm.end():lo + mm.end() + 1]
        if nxt == "(":
            j = close_paren(t, lo + mm.end())
            args = [(a, ) for a in split_top(t[lo + mm.end() + 1:j], ",")]
            if nm in heads:
                out.append((p, j + 1, "call", nm, t[lo + mm.end() + 1:j]))
            elif nm not in ("NOT", "some", "count", "all", "none"):
                out.append((p, j + 1, "opaque", nm, args))
        elif nm in params:
            out.append((p, lo + mm.end(), "param", nm, None))
        elif nm in bd:
            out.append((p, lo + mm.end(), "bind", nm, None))
    return out


def _directly(t, br, enc, p, e):
    """is the leaf at t[p:e] the whole content of the innermost label enclosing it?"""
    if not enc:
        return False
    nm, s_, c_, e_ = enc[-1]
    return t[c_:e_].strip() == t[p:e].strip()


def _match(steps, names):
    """rule 4 (applied repeatedly, a reading): the steps a subsequence of the route's public labels; (consumed, the
    labels the full path names)."""
    k = 0
    for n_ in names:
        if k < len(steps) and n_ == steps[k]:
            k += 1
    return k


def walk10(t, lo, hi, steps, target, outside, env, bd, heads, route, depth=0, lab_above=False):
    """every site of `target` under t[lo:hi] reached by the steps: ("ok", full path) | ("wall", rule, name)."""
    if depth > 8:
        raise Und("too deep")
    params = env
    br = [b for b in _brackets(t) if lo <= b[1] and b[3] <= hi]
    out = []
    raw = t[lo:hi]
    sites = [("group", lo + mm.start(), lo + mm.end()) for mm in re.finditer(r"\(\?<:?%s>" % re.escape(target), raw)]
    sites += [("label", b[1], b[3] + 1) for b in br if b[0] == target]
    for p, e, kind, nm, args in _leaves(t, lo, hi, params, bd, heads):
        sites.append((kind, p, e, nm, args))
    for s in sites:
        kind, p, e = s[0], s[1], s[2]
        enc = [b for b in _enclosing(br, p, lo, hi)]
        names = [b[0] for b in enc]
        priv = [n_ for n_ in names if n_.startswith("_")]
        pub = [n_ for n_ in names if not n_.startswith("_") and not n_.startswith("(")]
        k = _match(steps, pub)
        rest = steps[k:]
        if kind in ("group", "label"):
            if rest:
                continue
            if priv and not s10("q2x"):
                out.append(("wall", "rule 2", priv[0]))
                continue
            out.append(("ok", route + pub))
            continue
        if kind == "opaque":
            if rest or target:
                raise Und("a provided call %s holds a part" % nm)
            continue
        nm = s[3]
        labelled = _directly(t, br, enc, p, e) or (not enc and lab_above and raw.strip() == t[p:e].strip())
        sub = []
        if kind == "bind":
            if rest and rest[0] == nm:
                raise Und("an implicit label as a middle")
            sub = walk10(bd[nm], 0, len(bd[nm]), rest, target, True, {}, bd, heads, route + pub, depth + 1)
        elif kind == "call":
            h = heads[nm]
            if rest and rest[0] == nm:
                raise Und("a macro's name as a middle")
            avals = [a.strip() for a in split_top(s[4], ",")] if s[4].strip() else []
            penv = {}
            for (pn, _, pk), av in zip(h[1], avals):
                if pk == "plain":
                    off = t.index(av, p) if av in t[p:e] else None
                    penv[pn] = (t, off, (off + len(av)) if off is not None else None, outside, env)
            sub = walk10(h[2], 0, len(h[2]), rest, target, True, penv, bd, heads, route + pub, depth + 1)
        elif kind == "param":
            at, ao, ae, aout, aenv = params[nm]
            if ao is None:
                raise Und("an argument not found")
            sub = walk10(at, ao, ae, rest, target, aout, aenv, bd, heads, route + pub, depth + 1,
                         lab_above=labelled)
        if not sub:
            continue
        reach = [x for x in sub if x[0] == "ok"]
        if priv and reach and not (s10("q2") and depth > 0) and not s10("q2x"):
            out.append(("wall", "rule 2", priv[0]))
            continue
        if outside and not labelled and reach and kind in ("bind", "param", "call") and not s10("q4"):
            out.append(("wall", "rule 6", nm))
            continue
        out += sub
    return out


def _start10(start, t, bd, heads, env):
    """(text, lo, hi, outside, env, kind) of the start, or raise Und."""
    br = _brackets(t)
    st = _mask_conds(t)
    mine = [b for b in br if b[0] == start]
    if len(mine) > 1:
        raise Und("two labels %s" % start)
    if mine:
        return t, mine[0][2], mine[0][3], False, env, "label"
    for mm in re.finditer(r"(?<![\w.])([A-Za-z_][\w.]*)\(", st):
        nm = mm.group(1)
        if nm not in heads:
            continue
        j = close_paren(t, mm.end() - 1)
        avals = [a.strip() for a in split_top(t[mm.end():j], ",")]
        h = heads[nm]
        for (pn, _, pk), av in zip(h[1], avals):
            if pk == "label" and av == start + ":":
                hb = h[2]
                penv = {}
                for (pn2, _, pk2), av2 in zip(h[1], avals):
                    if pk2 == "plain":
                        off = t.index(av2, mm.end()) if av2 in t[mm.end():j] else None
                        penv[pn2] = (t, off, (off + len(av2)) if off is not None else None, False, env)
                lb = [b for b in _brackets(hb) if b[0] == pn]
                if len(lb) != 1:
                    raise Und("a sent label not on a part label")
                return hb, lb[0][2], lb[0][3], True, penv, "sent"
    uses = [x for x in _leaves(t, 0, len(t), env, bd, heads) if x[3] == start]
    if start in bd and len(uses) >= 1:
        return bd[start], 0, len(bd[start]), True, {}, "bind"
    calls = [x for x in uses if x[2] == "call"]
    if len(calls) == 1:
        h = heads[start]
        p, e, _, _, a = calls[0]
        avals = [x.strip() for x in split_top(a, ",")] if a.strip() else []
        penv = {}
        for (pn, _, pk), av in zip(h[1], avals):
            if pk == "plain":
                off = t.index(av, p) if av in t[p:e] else None
                penv[pn] = (t, off, (off + len(av)) if off is not None else None, False, env)
        return h[2], 0, len(h[2]), True, penv, "call"
    raise Und("no start")


def path10(t, binds):
    """PATH10 over the reading text t: every dotted read decided by the rules; returns t with each decided legal
    read written as its full path; raises at a wall."""
    bd, heads = _env_of(binds)
    sl = strip_lits(t)
    reads = [(mm.start(1), mm.group(1)) for mm in re.finditer(r"(?<![\w.$])\$?([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+)", sl)]
    out, last = [], 0
    for pos, rd in reads:
        steps = rd.split(".")
        if steps[0] == "rx" or (steps[0] not in bd and steps[0] not in heads and (steps[0] in PROV or
                                                                                  steps[0] in MACROS)):
            continue
        new = rd
        bad = next((s_ for s_ in steps[1:] if s_.startswith("_")), None)
        if bad:
            raise CompileError("`%s`: the path %s `%s`, not the start (a compile error, path-rules rule 2)" %
                               (rd, RULE2_10, bad))
        try:
            tt, lo, hi, outside, env, sk = _start10(steps[0], t, bd, heads, {})
            res = walk10(tt, lo, hi, steps[1:-1], steps[-1], outside, env, bd, heads, [steps[0]],
                         lab_above=sk in ("label", "sent"))
        except Und:
            res = None
        if res:
            oks = sorted(set(tuple(x[1]) for x in res if x[0] == "ok"))
            walls = [x for x in res if x[0] == "wall"]
            if not oks and walls and not (sk == "sent" and s10("q5")):
                w = walls[0]
                if w[1] == "rule 2":
                    raise CompileError("`%s`: the path %s `%s`, not the start (a compile error, path-rules rule 2%s)"
                                       % (rd, RULE2_10, w[2], "; the sent label is a start, the body's wall below "
                                          "it is crossed: %s, the manager's reading" % SENT10 if sk == "sent" else ""))
                raise CompileError("`%s`: `%s` is not visible through `%s`: the path crosses `%s`, %s (a compile "
                                   "error, path-rules rule 6)" % (rd, ".".join(steps[1:]), steps[0], w[2], RULE6_10))
            if len(oks) == 1 and sk != "sent":
                new = ".".join(list(oks[0]) + [steps[-1]])
        out.append(t[last:pos] + new)
        last = pos + len(rd)
    out.append(t[last:])
    return "".join(out)


def _toplevel10(t):
    """t's text outside every (), [], {}, literal and string: the operators that join t's top-level parts."""
    m = _mask_conds(t)
    out, d = [], 0
    for c in m:
        if c in "([{":
            d += 1
        elif c in ")]}":
            d -= 1
        elif d == 0:
            out.append(c)
    return "".join(out)


def wrap10(t):
    """every part label (the blank's excepted) whose content is a stack or an expression joined by `SEQ` or `&` (a
    top-level `|` or `,` makes entries of the label set: "Inside `[ ]` the label set binds looser than `&`, tighter
    than `|`"), handed over parenthesised."""
    for _ in range(20):
        changed = False
        for nm, s_, c_, e_ in sorted(_brackets(t), key=lambda b: -b[1]):
            body = t[c_:e_]
            b0 = body.strip()
            if nm == "_" or not b0 or (b0.startswith("(") and close_paren(b0, 0) == len(b0) - 1):
                continue
            stk = re.match(r"\[(?:\w+|\([^()]*\)) = ", b0) is not None and _close_br(b0, 0) == len(b0) - 1
            top = _toplevel10(b0)
            ops = bool(re.search(r"\bSEQ\b|&", top)) and not re.search(r"[|,]", top)
            if stk or ops:
                t = t[:c_] + body.replace(b0, "(" + b0 + ")", 1) + t[e_:]
                changed = True
                break
        if not changed:
            break
    return t


def path_rules(expr, binds):                                 # noqa: F811
    """PATH10 first (the reading text's reads decided), then predfold1124's PATH9 as it was."""
    if x10():
        expr = path10(expr, binds)
    return P10F["path_rules"](expr, binds)


def prog(expr, binds=(), **opts):                            # noqa: F811
    """PATH10 on: every text handed over with its stacks and expressions parenthesised; predfold1124's prog then
    runs the path rules (PATH10, then PATH9) over the expression and each binding's text, as it did."""
    if not x10():
        return P10F["prog"](expr, binds, **opts)
    b2 = []
    for b in binds:
        h = head_of(b)
        n_, _, body = b.partition(" := ")
        b2.append(n_ + " := " + wrap10(body))
    e2 = wrap10(expr)
    for mm in re.finditer(r"(?<![\w.$])(_[A-Za-z]\w*)\.", strip_lits(e2)):
        priv = mm.group(1)
        if re.search(r"\[%s = " % re.escape(priv), e2) and not s10("q2x"):
            path10(e2, list(binds))                          # decided first: a wall below the start still refuses
            e2 = re.sub(r"(?<![\w.$])%s(?![\w])" % re.escape(priv), "p" + priv + "_start", e2)
    return P10F["prog"](e2, b2, **opts)


# ================================================================== the GRID's evaluator: the path rules, SEPARATE
# It reads no program text: a cell is an abstract stack of layers between the start and the target `h` (the group
# of A := /(?<h>\d)/), and the rules are applied to that stack as the documents word them. The program text the
# engine runs and the regex the answers are checked against are both BUILT from the stack, mechanically.
#   layer: ("P", name) a public part label | ("_x",) a private one | ("_",) the blank label | ("E",) the part is
#   one operand of an expression (`(.. SEQ ",")`) | ("H",) the part is in a hole of a literal (`/${..},/`) |
#   ("Bd", name) a binding boundary (the part below is the text of a binding `name`, used here).
GRULE = {   # the deciding sentences, each READ from its piece (pinned by GRID)
    1: ("core/labels/rule/paths", "1. in the label DAG there is a target label and a starting label. The starting "
                                  "label has at least one path to the target label"),
    2: ("core/labels/rule/paths", "2. the path may not contain any underscore labels full or prefix unless the "
                                  "underscore prefix label is the start"),
    3: ("core/labels/rule/paths", "3. within a binding, any label on the path may be used as a start label"),
    4: ("core/labels/rule/paths", "4. if a legal path exists a.b.c and c can be unambiguously referenced from a, then "
                                  "b can be skipped a.c"),
    "4r": ("core/labels/rule/paths", "rule 4 applies repeatedly"),
    5: ("core/labels/rule/paths", "5. From outside, the start is the binding's name, a macro's name at its call, or a "
                                  "label written on the use. The path then continues into that binding's tree by "
                                  "rules 1, 2 and 4."),
    6: ("core/labels/rule/paths", "6. A part used alone inside a binding is crossed from outside as an underscore "
                                  "label is, and is a start inside its own binding."),
    "e": ("core/labels/rule/paths", "never a licence to cross a wall below it"),
    "sent": ("core/labels/rule/sent-label-wall", "a compile error by rule 2 for now"),
    "short": ("core/labels/rule", "whatever B's body does with the spot"),
}
START_KINDS = ("in", "in_", "inwx", "inwb", "bind", "use", "call", "arg", "sent", "short")
WALLS10 = ("_x", "_")


def g_eval(kind, layers, steps):
    """(verdict, [rule keys]) by the rules alone, on the abstract stack: "legal" | "refused"."""
    if kind == "arg":
        return "legal", ["e"]                                # the caller's label: a start, the body's walls above it
    if kind == "short":
        return "legal", ["short"]                            # shorthand-is-callers, whatever the body does
    segs, cur, und = [], [], False
    for ly in layers:
        if ly[0] == "Bd":
            segs.append(cur)
            cur = []
        else:
            cur.append(ly)
    segs.append(cur)
    for j, sg in enumerate(segs):
        for ly in sg:
            if ly[0] in WALLS10:
                return "refused", ["sent" if kind == "sent" else 2] + ([5] if j else [])
        outside = j > 0 or kind in ("bind", "call", "use")
        labelled = bool(sg) and sg[-1][0] in ("P",) + WALLS10 or (j == 0 and not sg and kind in (
            "in", "in_", "inwx", "inwb", "sent"))
        if outside and not labelled:
            return "refused", [6] + ([5] if j else [])
        if not outside and not labelled and j + 1 < len(segs):
            und = True
    pubs = [ly[1] for ly in layers if ly[0] == "P"]
    k = 0
    for p in pubs:
        if k < len(steps) and steps[k] == p:
            k += 1
    if k < len(steps):
        return "refused", [1]
    if und and not s10("q16"):
        return "undecided", ["alone-as-middle"]
    skipped = len(pubs) - len(steps)
    if s10("q3") and skipped >= 2:
        return "refused", [4]
    return "legal", [1] + ([5] if kind in ("bind", "use", "call") or len(segs) > 1 else []) + \
        ([3] if kind in ("in", "in_", "inwx", "inwb") else []) + ([4] if skipped >= 1 else []) + (["4r"] if skipped >= 2 else []) + \
        ([2] if kind == "in_" else [])


def g_build(kind, layers, steps):
    """(expression, bindings, the expected regex) built from the stack, mechanically."""
    leaf = {"call": "rx", "arg": "rx", "short": "rx", "sent": "v"}.get(kind, "A")
    frag, rx, binds = leaf, "(?P<h>[0-4])", []
    for ly in reversed(layers):
        if ly[0] == "P" or ly[0] in WALLS10:
            frag = "[%s = %s]" % (ly[1] if ly[0] == "P" else ly[0], frag)
        elif ly[0] == "E":
            frag, rx = '(%s SEQ ",")' % frag, rx + ","
        elif ly[0] == "H":
            frag, rx = "/${%s},/" % frag, rx + ","
        elif ly[0] == "Bd":
            binds.append("%s := %s" % (ly[1], frag))
            frag = ly[1]
    path = ".".join(list(steps) + ["h"])
    if kind in ("in", "in_", "inwx", "inwb"):
        s_ = "_s" if kind == "in_" else "s"
        top = "[%s = %s]" % (s_, frag)
        if kind in ("inwx", "inwb"):                         # a wall ABOVE the start
            top = "[%s = %s]" % ("_x" if kind == "inwx" else "_", top)
        return '%s SEQ "!" & (%s.%s: <5)' % (top, s_, path), [A_H] + binds, rx + "!"
    if kind == "bind":
        return "X & (X.%s: <5)" % path, [A_H] + binds + ['X := %s SEQ "!"' % frag], rx + "!"
    if kind == "use":
        return "[c = X] & (c.%s: <5)" % path, [A_H] + binds + ['X := %s SEQ "!"' % frag], rx + "!"
    if kind == "sent":
        return "R(x:, A) & (x.%s: <5)" % path, [A_H, "R(l:, v) := /${[l = %s]}xx/" % frag], rx + "xx"
    body = "B(rx) := /${%s}xx/" % frag
    if kind == "call":
        return "B(A) & (B.%s: <5)" % path, [A_H, body], rx + "xx"
    if kind == "arg":
        return "B([a = A]) & (a.h: <5)", [A_H, body], rx + "xx"
    return "B(A) & (A.h: <5)", [A_H, body], rx + "xx"


def g_cells():
    """the grid: start kind x stack (depth 0-3: labels, walls, an expression, a hole, up to two binding levels) x
    every subsequence of the stack's public labels as the path's middle steps."""
    import itertools
    toks = ("P", "_x", "_", "E", "H", "Bd")
    out = []
    for kind in START_KINDS:
        for n in range(0, 4):
            for combo in itertools.product(toks, repeat=n):
                if kind in ("call", "arg", "short", "sent") and "Bd" in combo:
                    continue
                if kind == "sent" and ("E" in combo or "H" in combo):
                    continue
                if combo.count("Bd") > 2:
                    continue
                layers, pn, bn = [], iter("nmk"), iter(("Y1", "Y2"))
                for t_ in combo:
                    layers.append(("P", next(pn)) if t_ == "P" else ("Bd", next(bn)) if t_ == "Bd" else (t_, t_))
                pubs = [ly[1] for ly in layers if ly[0] == "P"]
                subs = [s for r in range(len(pubs) + 1) for s in itertools.combinations(pubs, r)]
                if kind in ("arg", "short"):
                    subs = [()]
                for st in subs:
                    out.append((kind, tuple(layers), st))
    return out


def g_texts(rx):
    """WHOLE / SEARCHED / FIND-ALL subjects made from the expected regex itself (its one digit 3 or 7)."""
    lit = rx.replace("(?P<h>[0-4])", "\0")
    hold, fail = lit.replace("\0", "3"), lit.replace("\0", "7")
    return [hold, fail], fail + " " + hold, hold + " " + fail + " " + lit.replace("\0", "4")


def g_run(cells):
    """each cell: the evaluator's verdict, the engine's run, and (legal) the answers against the built regex."""
    res = []
    for kind, layers, steps in cells:
        want, why = g_eval(kind, layers, steps)
        e, b, rx = g_build(kind, layers, steps)
        Pg, err = run(e, b)
        got = "legal" if Pg is not None else ("CRASH" if err.startswith("CRASH") else "refused")
        diff = None
        if Pg is not None and want == "legal":
            wh, sr, fa = g_texts(rx)
            q = wh + [sr, fa]
            diff = ndiff(answers(Pg, q), answers(Re(rx), q))
        res.append((kind, layers, steps, want, why, e, b, rx, got, err, diff))
    return res


# ================================================================== the checks10
def unit10(name, what, secs=UNIT_TIMEOUT10):
    unit(name, what, secs)


SC10_T = "core/labels/rule/stacked-chain"
EXP_T = "core/labels/export"
LP_T = "core/labels/paths"
SLW_T = "core/labels/rule/sent-label-wall"
SPW_T = "core/labels/rule/skip-past-wall"
EQI_T = "core/labels/rule/equivalence-inside"
AAM_T = "core/labels/rule/alone-as-middle"
GRN_T = "core/labels/rule/group-node"
SHO_T = "core/labels/paths/shorthand-outside"
P1_ = "P := /(?<d>\\d)/"
Q1_ = "Q := /,(?<d>\\d)/"
QE_ = "Q := /,(?<e>\\d)/"
P2_ = "P := /(?<d>\\d)\\d/"
Q2_ = "Q := /\\d(?<d>\\d)/"
Q2E = "Q := /\\d(?<e>\\d)/"
Q3_ = "Q := /a(?<d>\\d)/"
Q3E = "Q := /a(?<e>\\d)/"
XW_ = 'X := [_x = [n = A]] SEQ "!"'
YW_ = 'Y := [c = X] SEQ ";"'
Y2_ = 'Y := [c = B(A)] SEQ "!"'
X2L = 'X := [y = Y] SEQ ";"'
RSB = "R(l:, v) := /${[l = [_ = v]]}xx/"
RSA = "R(l:, v) := /${[_ = [l = v]]}xx/"
QS10 = (["3,7", "7,3"], "7,3 3,7", "3,7 7,3 4,1")
QA10 = (["7,3", "3,7"], "3,7 7,3", "7,3 3,7 4,1")
Q2D = (["37", "73"], "73 37", "37 73 14")
QOR = (["3", "a3", "a7"], "a7 a3", "3 a7 a4")
Q2L = (["3xx!;", "7xx!;"], "7xx!; 3xx!;", "3xx!; 7xx!; 4xx!;")
QX1 = (["37!", "73!"], "73! 37!", "37! 73! 14!")
QM10 = (["3,7!", "7,3!"], "7,3! 3,7!", "3,7! 7,3! 4,1!")
D10 = dict(NOWS)                                             # the documents as READ by the checks (plants alter it)
if s10("q6"):
    D10["core.md"] = D10["core.md"].replace("rule 4 applies repeatedly", "rule 4 applies once", 1)
if s10("q8"):
    D10["core.md"] = D10["core.md"].replace("none: `B.h` a compile error (rule 2)", "none: `B.h` a compile error (rule 6)", 1)
if s10("q9"):
    D10["core.md"] = D10["core.md"].replace("`m.d` starts at `m` (rule 3)", "`m.d` is a compile error", 1)
if s10("q14"):
    D10["core.md"] = D10["core.md"].replace("4. if a legal path exists a.b.c and c can be unambiguously referenced from a, "
                                            "then b can be skipped a.c", "4. a middle label may be skipped", 1)
if s10("q17"):
    D10["core.md"] = D10["core.md"].replace("the same-label-twice rules", "the rules", 1)
D8.clear()
D8.update(D10)


def flat_call(body, param, arg, target, wrong=False):
    """CONTROL's direct regex of `B(A)` read through A's `target`, BUILT from the texts: the body's literal with
    every hole's labels dropped and the parameter replaced by the argument's literal, A's group the restricted
    digit, the body's own groups unnamed."""
    a = arg.strip()[1:-1]
    a = re.sub(r"\(\?<%s>\\d\)" % re.escape(target), "([5-9])" if wrong else "([0-4])", a)
    a = re.sub(r"\(\?<\w+>", "(?:", a)
    b = re.sub(r"\(\?<\w+>", "(?:", body.strip()[1:-1])

    def hole(mm):
        x = mm.group(1).strip()
        while True:
            m2 = re.fullmatch(r"\[(?:\w+|\([^()]*\)) = (.*)\]", x, re.S)
            if not m2:
                break
            x = m2.group(1).strip()
        assert x == param, (x, param)
        return a
    return re.sub(r"\$\{([^{}]*)\}", hole, b)


CTL10 = []
for e_, b_ in (("identity(A) & (A.d: <5)", [A_D, IDN]), ("B(A) & (A.d: <5)", [A_D, B_CL]),
               ("B(A) & (A.d: <5)", [A_D, B_LS]), ("B(A) & (A.d: <5)", [A_D, B_CP]),
               ("B(A) & (A.d: <5)", [A_D, B_P]), ("B([A = A]) & (A.d: <5)", [A_D, B_ST])):
    h_ = head_of(b_[1])
    CTL10.append((e_, b_, flat_call(h_[2], h_[1][0][0], b_[0].split(" := ", 1)[1], "d",
                                    wrong=s10("q7") and e_.startswith("identity"))))

# ---- predfold1124's checks CONTROL .. READINGS, run again from its own text with the DECLARED PATCHES of r90
PATCH10 = [   # (why, its text in predfold1124, the patched text): each must apply exactly once
    ("C4: CONTROL runs the provided bodies against regexes built from their texts",
     '("B(A) & (A.d: <5)", [A_D, B_AF], r"\\d-[0-4]")):',
     '("B(A) & (A.d: <5)", [A_D, B_AF], r"\\d-[0-4]")) + tuple(CTL10):'),
    ("C4: CONTROL's FAIL line names the differing rows only",
     '"over %d texts: %s" % (len(QC9), ctl9))',
     '"over %d texts: %s" % (len(QC9), [x_ for x_ in ctl9 if x_[1] != (0, 0, 0)] or "none"))'),
    ("A8: \"From outside\" re-witnessed on a labelling body",
     'ok_s11, r_s11 = rl("From outside", \'[pub = B(A)] & (pub.A.h: <5)\', [A_H, B_XX], "not visible",\n'
     '                   "the shorthand label is protected: it adds no export (the manager\'s reading (b))", AD_T)',
     'ok_s11, r_s11 = rl("From outside", \'[pub = B(A)] & (pub.A.h: <5)\', [A_H, B_PH], "not visible",\n'
     '                   "the shorthand label is protected: it adds no export (the manager\'s reading (b); open "\n'
     '                   "shorthand-outside)", AD_T)'),
    ("the line \"A blank label in the stack\" printed once, in core/labels/ownership",
     'ok_p4, r_p4 = rl("A blank label in the stack", "[l = [_ = P]] & (l.d: <5)", [P_], RULE2_9,\n'
     '                 "the path crosses the blank label (rule 2); no label reads `d` there", PATHS_T)',
     'ok_p4, r_p4 = refused("[l = [_ = P]] & (l.d: <5)", [P_], RULE2_9), ""'),
    ("the line \"Through a call, a private label in the body\" moved to core/labels/ownership",
     '"the path crosses the body\'s `_x` (rules 5 and 2); `B(A) & (B.h: <5)` alike", PATHS_T)',
     '"the path crosses the body\'s `_x` (rules 5 and 2); `B(A) & (B.h: <5)` alike", OWN_T)'),
    ("A5: reading (e) restricted: the line's label",
     'pl("The caller\'s label, a start whatever the body stacks",',
     'pl("The caller\'s label, a start under the body\'s wall",'),
    ("C7: READINGS (b) by a refusal with its key, never a crash",
     '("shorthand-is-callers (b): the shorthand label protected (no export through the caller\'s label)", P_rb is None),',
     '("shorthand-is-callers (b): the shorthand label protected (no export through the caller\'s label)",\n'
     '     refused("[pub = B(A)] & (pub.A.d: <5)", [A_D, B_XX], "not visible")),'),
    ("C7: READINGS (d) by a refusal with its key, never a crash",
     '"only", P_rd is None),',
     '"only", refused("[a = A] SEQ \\"!\\" & (A.h: <5)", [A_H], "neither written")),'),
    ("A5: reading (e) restricted: the arm's name",
     '("path-rules (e): a caller\'s label is a start whatever the body stacks", P_re is not None),',
     '("path-rules (e): a caller\'s label is a start, the body\'s wall above it", P_re is not None),'),
    ("A7: (g) is tested (READINGS10), no longer printed UNTESTABLE",
     'print("   UNTESTABLE: path-rules (g), the equivalence is a picture, not a spelling: nothing runs `t` as a label")',
     'print("   (g) of path-rules: run by READINGS10 (inside and outside)")'),
    ("C6: NAMEGRID's deciding sentence the ruled clause, not a rule number (n.m.d)",
     '("n.m.d", "inside, two public", "plain", "[n = [m = P]] & (n.m.d: <5)", [P_XX], "legal", SC_T, "rule 1"),',
     '("n.m.d", "inside, two public", "plain", "[n = [m = P]] & (n.m.d: <5)", [P_XX], "legal", SC_T,\n'
     '     "rule 1 makes `n.m.d` a path"),'),
    ("C6: NAMEGRID (B.n.m.h)",
     '("B.n.m.h", "two public stacked", "plain", "B(A) & (B.n.m.h: <5)", [A_H, B_MN], "legal", SC_T, "rule 1"),',
     '("B.n.m.h", "two public stacked", "plain", "B(A) & (B.n.m.h: <5)", [A_H, B_MN], "legal", SC_T,\n'
     '     "From outside (rule 5) the binding\'s name starts the same tree"),'),
    ("C6: NAMEGRID (B.m.h)",
     '("B.m.h", "two public stacked", "plain", "B(A) & (B.m.h: <5)", [A_H, B_MN], "legal", SC_T, "rule 1"),',
     '("B.m.h", "two public stacked", "plain", "B(A) & (B.m.h: <5)", [A_H, B_MN], "legal", SC_T,\n'
     '     "rule 3 lets `m` start one"),'),
    ("C6: NAMEGRID (X.n.m.h)",
     '[A_H, X_MN], "legal", SC_T, "rule 5"),',
     '[A_H, X_MN], "legal", SC_T,\n     "From outside (rule 5) the binding\'s name starts the same tree"),'),
    ("C6: NAMEGRID (X.h)",
     '("X.h", "from outside", "plain", "X & (X.h: <5)", [A_H, X_MN], "legal", SC_T, "rule 4"),',
     '("X.h", "from outside", "plain", "X & (X.h: <5)", [A_H, X_MN], "legal", SC_T,\n'
     '     "and `X.h` (rule 4) read A\'s `h`"),'),
    ("A5: NAMEGRID's sentence for the caller's label under a stack",
     '"legal", PATHS_T, "whatever the body stacks around them"),',
     '"legal", PATHS_T, "never a licence to cross a wall below it"),'),
    ("the cell B.n.h's sentence moved with its line to core/labels/ownership",
     '("B.n.h", "stacked", "plain", "B(A) & (B.n.h: <5)", [A_H, B_ST], "refused", PATHS_T,',
     '("B.n.h", "stacked", "plain", "B(A) & (B.n.h: <5)", [A_H, B_ST], "refused", OWN_T,'),
    ("B9: FLAGS pins the narrowed options sentence (the weak `i`, the asked letter)",
     '(OP_T, "Program options reach a string constant written after the statement in that file")',
     '(OP_T, "A file\'s weak `i` reaches a string constant written after the statement in that file")'),
    ("B9: FLAGS pins the narrowed explicit sentence (an `i` put in by an option hole)",
     '(FL_T, "or put into it by an option hole")', '(FL_T, "or an `i` put into it by an option hole")'),
    ("B9: \"Inside a union\" names no intersection as its alike (the line \"Inside an intersection\" is its own)",
     '"his ruling; `(h: <5 & capture(\\"h\\"))` alike", CS_T)', '"his ruling", CS_T)'),
    ("C9: NAMEGRID's FAIL line says which arm a cell fails",
     'g9_bad.append((sp_, occ_, kind_, want, got, has, (err or "")[:100]))',
     'g9_bad.append((sp_, occ_, kind_, want, got, "sentence found" if has else "sentence missing", (err or "")[:100]))'),
]
_a10 = _src9.index('unit9("CONTROL", ')
_chk9 = _src9[_a10:_src9.index('unit9("SWEEP", ')]
_bad10 = []
for why_, old_, new_ in PATCH10:
    if _chk9.count(old_) != 1:
        _bad10.append((why_, _chk9.count(old_)))
    _chk9 = _chk9.replace(old_, new_, 1)
if _bad10:
    print("PATCH DRIFT (predfold1124's text moved): %s" % _bad10)
    print("predfix90_model: 0 checks, 1 failed (PATCHES)")
    sys.exit(1)
print("== %d declared patches applied to predfold1124's checks CONTROL .. READINGS:" % len(PATCH10))
for why_, _, _ in PATCH10:
    print("   PATCH: %s" % why_)
if s10("q10"):
    _run10 = run

    def run(expr, binds=()):                                 # noqa: F811  (q10: the engine crashes on one program)
        if expr == "[pub = B(A)] & (pub.A.d: <5)":
            return None, "CRASH ValueError: planted"
        return _run10(expr, binds)
exec(compile(_chk9, P1124, "exec"), globals())               # noqa: S102


# ---- this lane's checks
unit10("CANARY", "the control is predfold1124's engine: each canary program's legality flips with PATH10 off")
CAN10 = [("Y & (Y.c.h: <5)", [A_H, XW_, YW_]), ('[n = [m = A] SEQ "!"] & (n.h: <5)', [A_H]),
         ("X & (X.ab.l: <5)", ["B := /(?<l>\\d)/", "A := /a(?<l>\\d)/", 'X := [ab = (B | A)] SEQ "!"']),
         ("[n = [m = [k = P]]] & (n.k.d: <5)", [P_XX])]
can_rows = []
for e_, b_ in CAN10:
    X10[0] = False
    off_ = run(e_, b_)[0] is not None
    X10[0] = True
    on_ = run(e_, b_)[0] is not None
    can_rows.append((e_, "legal" if off_ else "refused", "legal" if on_ else "refused"))
    print("   CANARY `%s`: PATH10 off %s, on %s" % can_rows[-1])
can_ok = all(r_[1] != r_[2] for r_ in can_rows)
check("CANARY", can_ok, "%d canaries; the control is %s" % (len(can_rows), "predfold1124's engine: each flips" if can_ok
                                                           else "not predfold1124's engine: %s" % can_rows))

unit10("PATHS10", "review r90's cells A1-A8, A10, A11 as printed lines, each run; the readings and clauses pinned")
pa10_pins = [(PATHS_T, "rule 4 applies repeatedly"), (PATHS_T, "never a licence to cross a wall below it"),
             (PATHS_T, "count only the targets a legal path reaches"), (PATHS_T, "an implicit label is never a middle"),
             (PATHS_T, "Rule 5's start by a binding's or macro's name is line 3's shorthand"),
             (PATHS_T, "It holds from outside"), (EXP_T, "A label under an underscore label is not exported"),
             (AD_T, "for the read through `A.d`"), (SLW_T, "a compile error by rule 2 for now"),
             (SPW_T, "count only the targets a legal path reaches"), (AAM_T, "an implicit label is a start, never a middle"),
             (EQI_T, "[_t = A ] is equivalent to [_ = [t = A ]]"), (SHO_T, "the shorthand label is protected"),
             (GRN_T, "no sentence decides it")]
pa10_miss = [(t_, s_) for t_, s_ in pa10_pins if ws(s_) not in ws(piece8(t_))]
P_a1 = pl("A public label between", '[n = [m = P] SEQ "!"] & (n.d: <5)', [P2_], *QX1, tag=PATHS_T,
          tail=": rules 1 and 4")
P_a1b = run('[n = [m = P] SEQ "!"] & (n.m.d: <5)', [P2_])[0]
P_a2 = pl("Three stacked, both middles skipped", "[n = [m = [k = P]]] & (n.d: <5)", [P_XX], *Q3, tag=SC10_T,
          tail=": rule 4 applied repeatedly (a reading)")
P_a2b = run("[n = [m = [k = P]]] & (n.m.k.d: <5)", [P_XX])[0]
P_a2c = pl("Two binding levels, the middles skipped", "X & (X.c.h: <5)", [A_H, B_PH, Y2_, X2L], *Q2L, tag=SC10_T,
           tail=": rules 5 and 4, applied repeatedly (a reading)")
P_a2d = run("X & (X.y.c.p.h: <5)", [A_H, B_PH, Y2_, X2L])[0]
ok_a3, r_a3 = rl("A wall one binding level up", "Y & (Y.c.h: <5)", [A_H, XW_, YW_], RULE2_10,
                 "the path Y, c, then X's `_x`, crosses `_x` (rules 5 and 2); `Y.h` and `Y.c.n.h` alike", OWN_T)
ok_a3b = refused("Y & (Y.h: <5)", [A_H, XW_, YW_], RULE2_10) and refused("Y & (Y.c.n.h: <5)", [A_H, XW_, YW_], RULE2_10)
ok_a3c = refused("X & (X.n.h: <5)", [A_H, XW_], RULE2_10)
ok_a4, r_a4 = rl("From outside, alone in an expression", "X & (X.ab.l: <5)",
                 ["B := /(?<l>\\d)/", "A := /a(?<l>\\d)/", 'X := [ab = (B | A)] SEQ "!"'], RULE6_10,
                 "B and A are used alone in it (core/labels/rule/paths rule 6); through a hole, X := "
                 "`[n = /${Q},/] SEQ \"!\"`, alike", LP_T)
ok_a4b = refused("X & (X.n.d: <5)", [Q1_, 'X := [n = /${Q},/] SEQ "!"'], RULE6_10)
P_a4 = pl("From outside, a public part beside a part used alone", "X & (X.n.d: <5)",
          [P1_, Q1_, 'X := [n = ([m = P] SEQ Q)] SEQ "!"'], *QM10, tag=LP_T,
          tail=": m's `d` (rule 6: Q, used alone, is crossed as a wall)")
ok_a5, r_a5 = rl("Through the call, the caller's label under the body's wall", "B([a = A]) & (B.a.d: <5)", [A_D, B_ST],
                 RULE2_10, "the path crosses the body's `_x` (rules 5 and 2); `a.d` is the read", OWN_T)
P_a8w = pl("From outside, written out", "[pub = B([A = A])] & (pub.A.h: <5)", [A_H, B_PH], *Q3, tag=AD_T)
rl("From outside", "[pub = B(A)] & (pub.A.h: <5)", [A_H, B_PH], "not visible",
   "the shorthand label is protected: it adds no export (the manager's reading (b); open shorthand-outside)", SHO_T)
pl("From outside, written out", "[pub = B([A = A])] & (pub.A.h: <5)", [A_H, B_PH], *Q3, tag=SHO_T)
P_a10 = pl("Both bounds unspecified, the one hole twice", "EB(rx.digit, _)", ["EB(x, n) := /(?:${x}){${n},${n}}/"], QR,
           "x1234567", "1234567 12", UN_T, tail=": `{0,}` (count-unspecified)")
# the open pieces' runs
ok_o1, r_o1 = rl("The sent label above the body's blank", "R(x:, A) & (x.h: <5)", [A_H, RSB], SENT10,
                 "the path x, `_`, h crosses the blank (rule 2, the manager's reading)", SLW_T)
P_o1b = pl("Candidate (b)'s answers: the wall written above the sent label", "R(x:, A) & (x.h: <5)", [A_H, RSA], *Q3,
           tag=SLW_T)
P_o2s = pl("In a sequence, the private part last", "[n = ([m = P] SEQ [_x = Q])] & (n.d: <5)", [P1_, Q1_], *QS10,
           tag=SPW_T, tail=": m's `d`")
P_o2a = pl("Across `&`", "[n = ([m = P] & [_x = Q])] & (n.d: <5)", [P2_, Q2_], *Q2D, tag=SPW_T, tail=": m's `d`")
P_o2o = pl("Across `|`", "[n = ([m = P] | [_x = Q])] & (n.d: <5)", [P1_, Q3_], *QOR, tag=SPW_T,
           tail=": m's `d`, unset where the private branch is taken")
P_o2sb = pl("Candidate (b) in a sequence, the last mention read", "[n = ([m = P] SEQ [k = Q])] & (n.d: <5)",
            [P1_, Q1_], *QS10, tag=SPW_T, tail=": Q's `d`")
ok_o2ab, r_o2ab = rl("Candidate (b) across `&`", "[n = ([m = P] & [k = Q])] & (n.d: <5)", [P2_, Q2_], "ambiguous",
                     "both sides set `d`, the ambiguous reference", SPW_T)
P_o2ob = pl("Candidate (b) across `|`, the branch taken", "[n = ([m = P] | [k = Q])] & (n.d: <5)", [P1_, Q3_], *QOR,
            tag=SPW_T)
P_o2se = run("[n = ([m = P] SEQ [_x = Q])] & (n.d: <5)", [P1_, QE_])[0]      # the competitor renamed: the control
P_o2ae = run("[n = ([m = P] & [_x = Q])] & (n.d: <5)", [P2_, Q2E])[0]
P_o2oe = run("[n = ([m = P] | [_x = Q])] & (n.d: <5)", [P1_, Q3E])[0]
P_o3 = pl("Inside, the blank above `t`", '[_ = [t = A]] SEQ "!" & (t.h: <5)', [A_H], *Q3B, tag=EQI_T, tail=": rule 3")
ok_o3, r_o3 = rl("Inside, his `[_t = A]`", '[_t = A] SEQ "!" & (t.h: <5)', [A_H], "neither written",
                 "no label `t` is made (the manager's reading (g)); `_t.h` is the read", EQI_T)
ok_o3b, r_o3b = rl("From outside, both", "X & (X.t.h: <5)", [A_H, 'X := [_ = [t = A]] SEQ "!"'], RULE2_10,
                   "the path crosses the blank (rule 2); X := `[_t = A] SEQ \"!\"` with `X.h` alike, crossing `_t`",
                   EQI_T)
ok_o3c = refused("X & (X.h: <5)", [A_H, 'X := [_t = A] SEQ "!"'], RULE2_10) and \
    refused("X & (X.h: <5)", [A_H, 'X := [_ = [t = A]] SEQ "!"'], RULE2_10)
ok_o4, r_o4 = rl("A part used alone as a middle, inside", "[n = (P SEQ Q)] & (n.Q.d: <5)", [P1_, Q1_], "not visible",
                 "the read is `Q.d`; an implicit label is a start, never a middle (the manager's reading)", AAM_T)
P_o4 = pl("Through the part used alone, skipped", "[n = (P SEQ Q)] & (n.d: <5)", [P1_, Q1_], *QA10, tag=AAM_T,
          tail=": Q's `d`, the last mention")
P_o4b = pl("Candidate (b)'s answers: the read as `Q.d`", "[n = (P SEQ Q)] & (Q.d: <5)", [P1_, Q1_], *QA10, tag=AAM_T)
ok_o5, r_o5 = rl("A group inside a group", "/(?<g>(?<d>\\d))x/ & (g.d: <5)", [], "not visible",
                 "the evidence engine reads no group as a middle; no sentence decides it", GRN_T)
P_o5b = pl("Candidate (b)'s answers: the outer group written as a part label", "[g = /(?<d>\\d)/] SEQ /x/ & (g.d: <5)",
           [], ["3x", "7x"], "7x 3x", "3x 7x 4x", GRN_T)
QK10 = pop("37,a!x;", 3)
pa10_arms = {
    "pins": not pa10_miss,
    "A1 a public label between: `n.d` = `n.m.d`": P_a1 is not None and P_a1b is not None and
    answers(P_a1, QK10) == answers(P_a1b, QK10) and wh_(P_a1, QX1[0]) == [True, False],
    "A2 depth 3: `n.d` = `n.m.k.d`": P_a2 is not None and P_a2b is not None and answers(P_a2, QK10) == answers(P_a2b, QK10),
    "A2 two binding levels: `X.c.h` = `X.y.c.p.h`": P_a2c is not None and P_a2d is not None and
    answers(P_a2c, pop("37x!;", 5)[:400]) == answers(P_a2d, pop("37x!;", 5)[:400]),
    "A3 the two-level wall": ok_a3 and ok_a3b and ok_a3c,
    "A4 rule 6 below a label over an expression and a hole": ok_a4 and ok_a4b and wh_(P_a4, QM10[0]) == [True, False],
    "A5 (ii) through the call, the body's wall": ok_a5,
    "A8 from outside: the written-out half legal": wh_(P_a8w, Q3[0]) == [True, False],
    "A10 the EB line: `{0,}`": wh_(P_a10, QR) == [True] * 4,
    "sent-label-wall: (a) refused, (b) legal": ok_o1 and wh_(P_o1b, Q3[0]) == [True, False],
    "skip-past-wall: each operator = its renamed control": all(
        p_ is not None and q_ is not None and answers(p_, QK10) == answers(q_, QK10)
        for p_, q_ in ((P_o2s, P_o2se), (P_o2a, P_o2ae), (P_o2o, P_o2oe))),
    "skip-past-wall candidate (b) runs": wh_(P_o2sb, QS10[0]) == [False, True] and ok_o2ab and P_o2ob is not None,
    "equivalence-inside: legal / refused inside, both refused outside": wh_(P_o3, Q3B[0]) == [True, False] and ok_o3
    and ok_o3b and ok_o3c,
    "alone-as-middle: `n.Q.d` refused, `n.d` and `Q.d` alike": ok_o4 and P_o4 is not None and P_o4b is not None and
    answers(P_o4, QK10) == answers(P_o4b, QK10),
    "group-as-node: refused now, (b) legal": ok_o5 and wh_(P_o5b, ["3x", "7x"]) == [True, False],
}
check("PATHS10", all(pa10_arms.values()), "arms failing: %s; pins MISSING: %s" % (
    [k for k, v in pa10_arms.items() if not v] or "none", pa10_miss or "none"))

unit10("GRID", "start kind x stack (labels, walls, an expression, a hole, up to two binding levels; depth 0-3) x every "
       "skip: the SEPARATE evaluator's verdict from the rule text against the engine; each legal answer against the "
       "regex built from the stack, in all three modes; every cell printed")
g_pins = [(k, t_, s_) for k, (t_, s_) in GRULE.items()]
g_miss = [(k, t_) for k, t_, s_ in g_pins if ws(s_) not in ws(piece8(t_))]
for k, t_, s_ in g_pins:
    print("   SENTENCE %s [%s] \"%s\" %s" % (k, t_, s_, "(found)" if (k, t_) not in g_miss else "(MISSING)"))
cells10 = g_cells()
gres = g_run(cells10)
g_bad, g_und, g_cnt = [], [], {}
for kind, layers, steps, want, why, e, b, rx, got, err, diff in gres:
    stk = "/".join(l_[1] if l_[0] in ("P", "Bd") else l_[0] for l_ in layers) or "-"
    tag_ = "UNDECIDED" if want == "undecided" else "DECIDED"
    ok_ = want == "undecided" or (want == got and (diff in (None, (0, 0, 0))))
    g_cnt[(want, got)] = g_cnt.get((want, got), 0) + 1
    print("   %s %s | %s | path %s | rules %s: %s | engine %s%s%s" % (
        tag_, kind, stk, ".".join(steps) or "-", ",".join(map(str, why)), want, got,
        (" modes-diff %s" % (diff,)) if diff not in (None, (0, 0, 0)) else "", "" if ok_ else "   <-- DISAGREES"))
    if want == "undecided":
        g_und.append((kind, stk, steps))
    elif not ok_:
        g_bad.append((kind, stk, ".".join(steps), want, got, diff, (err or "")[:80]))
G_UND10 = 16                                                 # declared: the alone-as-middle cells (inside, through a
#                                                              binding used alone below a label over an expression)
check("GRID", not g_bad and not g_miss and len(g_und) == G_UND10,
      "%d cells (%s); disagreeing: %s; undecided %d (declared %d); sentences missing: %s" % (
          len(gres), ", ".join("%s->%s %d" % (a_, b_, n_) for (a_, b_), n_ in sorted(g_cnt.items())),
          g_bad[:6] or "none", len(g_und), G_UND10, g_miss or "none"))

unit10("READINGS10", "the manager's readings of review r90's dispositions, each run: SUPPORTED / NOT SUPPORTED")
r4r = [r_ for r_ in gres if "4r" in r_[4]]
RD10 = [
    ("(1) rule 4 applies repeatedly (A2): every GRID cell skipping two or more labels legal, its answers the built "
     "regex's (%d cells)" % len(r4r), bool(r4r) and all(r_[8] == "legal" and r_[10] == (0, 0, 0) for r_ in r4r)),
    ("(2) a label under an underscore label is not exported (A3): `X.n.h` and, a level up, `Y.c.h` refused",
     ok_a3c and ok_a3),
    ("(3) `n.Q.d` inside a compile error: an implicit label is a start, never a middle (A4)", ok_o4),
    ("(4) reading (e) restricted (A5): the caller's label a start under the body's wall (`a.h` legal), never a "
     "licence below it (`B([a = [_x = A]]) & (a.h: <5)` refused)",
     run("B([a = A]) & (a.h: <5)", [A_H, B_ST])[0] is not None and
     refused("B([a = [_x = A]]) & (a.h: <5)", [A_H, B_XX], RULE2_10)),
    ("(5) sent-label-wall: the sent label above the body's blank a compile error by rule 2 (A5 i)", ok_o1),
    ("(6) rule 4's candidates count only the targets a legal path reaches (A6), per operator `SEQ`, `&`, `|`: each "
     "answer that of the program with the private competitor renamed", pa10_arms[
         "skip-past-wall: each operator = its renamed control"]),
    ("(7) his equivalence holds from outside and fails inside under reading (g) (A7)",
     pa10_arms["equivalence-inside: legal / refused inside, both refused outside"]),
]
P_8in = [(run("B(A) & (A.h: <5)", [A_H, bb])[0], run("B([A = A]) & (A.h: <5)", [A_H, bb])[0]) for bb in (B_PH, B_LS)]
P_8out = [(refused("[pub = B(A)] & (pub.A.h: <5)", [A_H, bb], "not visible"),
           run("[pub = B([A = A])] & (pub.A.h: <5)", [A_H, bb])[0]) for bb in (B_PH, B_LS)]
RD10.append(("(8) the shorthand's expansion: the same READ inside the binding, parting from outside, for a labelling "
             "and a listing body (A8; the inside half compares the shorthand with the text SHORT9 rewrites it to, "
             "checks C4 names)", all(a_ is not None and b_ is not None and answers(a_, pop("37x", 3)) ==
                                     answers(b_, pop("37x", 3)) for a_, b_ in P_8in) and
             all(a_ and b_ is not None for a_, b_ in P_8out)))
for a_, v_ in RD10:
    print("   %s: %s" % ("SUPPORTED" if v_ else "NOT SUPPORTED", a_))
check("READINGS10", all(v_ for _, v_ in RD10), "%d readings run: %s" % (
    len(RD10), [a_[:60] for a_, v_ in RD10 if not v_] or "all SUPPORTED"))

unit10("TABLE10", "C5: every ownership-table cell's GROUNDS (line n, rule n, condition n, a piece, \"a reading\") "
       "against the declared list; a cell resting on a reading carries its mark")
GTOK10 = re.compile(r"\blines? \d+(?:, \d+)*|\brules? \d+(?: and \d+)?|\bcondition \d+|\ba reading\b|"
                    r"core/[\w/-]+|transform-export|another door")


def cell_grounds(cell):
    return sorted(set(GTOK10.findall(cell)))


_trows = [l_ for l_ in piece8(OWN_T).split("\n") if l_.startswith("|")][2:]
GOT10 = {}
for i_, l_ in enumerate(_trows):
    cs = [c.strip() for c in l_.strip("|").split("|")]
    for j_, c_ in enumerate(cs):
        GOT10[(i_, j_)] = cell_grounds(c_)
GROUNDS10 = {(0, 0): [], (0, 1): ['line 1'], (0, 2): ['lines 1, 2'], (0, 3): ['line 1'], (0, 4): ['a reading', 'line 4'], (0, 5): ['line 1', 'rule 2', 'rule 3'], (1, 0): [], (1, 1): ['core/labels/paths/argument-default', 'line 3'], (1, 2): ['rule 5'], (1, 3): ['transform-export'], (1, 4): ['line 3', 'rule 2'], (1, 5): ['rule 2'], (2, 0): [], (2, 1): ['core/labels/paths/call-prefix'], (2, 2): ['a reading', 'rule 4', 'rule 5'], (2, 3): ['transform-export'], (2, 4): ['rule 2'], (2, 5): ['rule 2'], (3, 0): ['condition 4'], (3, 1): ['core/labels/export/arguments'], (3, 2): [], (3, 3): [], (3, 4): ['another door', 'core/labels/paths/closed-argument', 'line 4'], (3, 5): ['a reading', 'rule 3'], (4, 0): ['core/operators/bindings/label-forward'], (4, 1): ['core/operators/bindings/label-in-argument'], (4, 2): [], (4, 3): [], (4, 4): ['another door', 'line 4'], (4, 5): ['line 1']}                                               # DECLARED: each cell's grounds, the table as fixed
tb10_bad = [(k_, GROUNDS10.get(k_), v_) for k_, v_ in sorted(GOT10.items()) if GROUNDS10.get(k_) != v_]
if not GROUNDS10:
    print("   GROUNDS10 (to declare): %r" % GOT10)
check("TABLE10", GROUNDS10 and not tb10_bad and len(GOT10) == len(GROUNDS10),
      "%d cells read, each cell's ground set against the declared one; changed ground: %s" % (
          len(GOT10), tb10_bad[:4] or "none"))

unit10("STACKCHAIN10", "C6: stacked-chain's ruled lede and bullet clauses pinned (the piece can no longer be reversed "
       "with every check green)")
sc10_pins = [(SC10_T, "`n.m.d` is the full path, `n.d` skips `m` (rule 4), `m.d` starts at `m` (rule 3)"),
             (SC10_T, "rule 1 makes `n.m.d` a path, rule 3 lets `m` start one, rule 4 lets `n.d` skip `m`"),
             (SC10_T, "The nested form `[n = ([m = P])]`, two spots, reads the same"),
             (SC10_T, "From outside (rule 5) the binding's name starts the same tree")]
sc10_miss = [(t_, s_) for t_, s_ in sc10_pins if ws(s_) not in ws(piece8(t_))]
check("STACKCHAIN10", not sc10_miss and " ruled " in piece8(SC10_T).split("\n")[0],
      "%d sentences pinned; MISSING: %s" % (len(sc10_pins), sc10_miss or "none"))

unit10("SWEEP", "C8: every printed three-mode line (`rejected:` and history skipped): predfold1124's engine (PATH10 off) "
       "over the starting commit's documents against this one over these, keyed by the FULL sweep key (program, "
       "bindings, the three texts); every non-same status and every moved or gone answer DECLARED", 900)
OLD10 = {f_: _git8("docs/design/predicates/" + f_, START10) for f_ in DOCF}
MOVED10 = {}                                                 # DECLARED: repr(full key) -> why (filled from the run)
X10[0] = False
OLD_T10 = sw_table84(OLD10)
X10[0] = True
NEW_T10 = sw_table84(NOWS)
if s10("q11"):                                               # an answer moved in the run AND the document alike
    _k = next(k_ for k_, vs in sorted(NEW_T10.items(), key=lambda kv: repr(kv[0])) if vs[0][2] == "same" and
              repr(k_) not in MOVED10 and k_ in OLD_T10)
    NEW_T10[_k] = [(a_, b_, c_, d_ + " (planted)") for a_, b_, c_, d_ in NEW_T10[_k]]
inh10 = {}                                                   # the control's own non-same rows: inherited, full key
for k_, vs in OLD_T10.items():
    for f_, ln_, st_, got_ in vs:
        if st_ != "same":
            inh10[(k_, f_, st_)] = True
sw_bad, sw_moved, sw_new, sw_gone, used10, cnt10 = [], [], [], [], set(), {}
for k_, vs in NEW_T10.items():
    ov = OLD_T10.get(k_, [])
    for i_, (f_, ln_, st_, got_) in enumerate(vs):
        cnt10[st_] = cnt10.get(st_, 0) + 1
        if st_ != "same" and (k_, f_, st_) not in inh10 and repr(k_) not in MOVED10:
            sw_bad.append(("UNDECLARED", f_, ln_, st_, k_[0], got_[:160]))
        o_ = ov[i_] if i_ < len(ov) else None
        if o_ and (o_[3] != got_ or o_[2] != st_):
            if repr(k_) in MOVED10:
                used10.add(repr(k_))
            else:
                sw_moved.append((f_, ln_, k_, o_[2], st_, o_[3][:160], got_[:160]))
        elif repr(k_) in MOVED10 and not ov:
            used10.add(repr(k_))
    if not ov:
        sw_new.append((vs[0][0], vs[0][1], k_[0]))
for k_, vs in OLD_T10.items():
    if k_ not in NEW_T10:
        if repr(k_) in MOVED10:
            used10.add(repr(k_))
        else:
            sw_gone.append((vs[0][0], vs[0][1], k_, vs[0][2]))
stale10 = sorted(k_ for k_ in MOVED10 if k_ not in used10)
for x_ in sw_gone:
    print("   GONE %s:%d %r (was %s)" % x_)
for x_ in sw_new:
    print("   ADDED %s:%d `%s`" % x_)
for x_ in sw_moved:
    print("   MOVED %s:%d %r (old %s, now %s)\n      old: %s\n      now: %s" % x_)
for x_ in sw_bad:
    print("   BAD %s" % (x_,))
for x_ in stale10:
    print("   STALE DECLARATION %s" % x_)
for k_, why_ in sorted(MOVED10.items()):
    print("   DECLARED MOVE OR GONE %s: %s" % (k_[:160], why_))
check("SWEEP", OLD_T10 and not sw_bad and not sw_moved and not sw_gone and not stale10,
      "%d printed lines now (%s), %d at the starting commit under predfold1124's engine; undeclared %d; moved or gone "
      "and not declared %d; declared %d; added %d; stale declarations %d" % (
          len(NEW_T10), ", ".join("%s %d" % kv for kv in sorted(cnt10.items())), len(OLD_T10), len(sw_bad),
          len(sw_moved) + len(sw_gone), len(MOVED10), len(sw_new), len(stale10)))

unit10("ERRSWEEP", "C9: every printed compile-error line of the base files refused, no crash; a line the parser cannot "
       "read is COUNTED (declared or a failure); each legality change of the starting commit's lines DECLARED")
exec(compile(_src9[_src9.index("def err_lines(docs"):_src9.index("es_now = err_lines(D8)")], P1124, "exec"),
     globals())                                              # noqa: S102  predfold1124's reader, verbatim
if s10("q12"):
    D8["core.md"] = D8["core.md"].replace("A wall one binding level up: modes: a compile error (`",
                                          "A wall one binding level up: modes: a compile error ( `", 1)
FN10 = ("worded \"a compile error for now (\" or \"at `lim`\", which predfold1124's reader does not parse; no path "
        "cell (r90 moves none)")
SKIP10 = {("core.md", "A joint left part"): FN10, ("core.md", "A value left part"): FN10,   # DECLARED: why unread
          ("core.md", "Inside a group question"): FN10, ("core.md", "A set that reads a label, bound alone"): FN10}
ES_CHG10 = {}                                                # DECLARED: (file, program, bindings) -> why
es_now = err_lines(D8)
es_seen = set((f_, ln_) for f_, ln_, _, _ in es_now)
es_skip = []
for f_ in DOCF:
    if f_.endswith("_details.md"):
        continue
    for ln_, L_ in enumerate(D8[f_].split("\n"), 1):
        if re.search(r"modes: a compile error", L_) and (f_, ln_) not in es_seen:
            lab_ = L_.split(": modes:", 1)[0].strip()[:80]
            es_skip.append((f_, lab_))
es_und_skip = [x_ for x_ in es_skip if x_ not in SKIP10]
es_bad, es_chg = [], []
for f_, ln_, e_, b_ in es_now:
    Pg, err = run(e_, b_)
    if Pg is not None or err.startswith("CRASH"):
        es_bad.append((f_, ln_, e_, "legal" if Pg is not None else err[:100]))
for f_, ln_, e_, b_ in err_lines(OLD10):
    X10[0] = False
    Po = run(e_, b_)[0]
    X10[0] = True
    Pn = run(e_, b_)[0]
    if (Po is None) != (Pn is None):
        es_chg.append((f_, e_, tuple(b_), "refused" if Po is None else "legal", "refused" if Pn is None else "legal"))
for f_, e_, b_ in [x_[:3] for x_ in es_chg]:
    pass
ES_DECL10 = dict(ES_CHG10)
if s10("q18") and ES_DECL10:
    ES_DECL10.pop(sorted(ES_DECL10)[0])
es_und_chg = [x_ for x_ in es_chg if x_[:3] not in ES_DECL10]
es_stale = [k_ for k_ in ES_DECL10 if k_ not in set(x_[:3] for x_ in es_chg)]
for x_ in es_chg:
    print("   LEGALITY CHANGED (a line of the starting commit) %s `%s` %s: %s -> %s; %s" % (
        x_[0], x_[1], list(x_[2]), x_[3], x_[4], ES_DECL10.get(x_[:3], "UNDECLARED")))
for x_ in es_skip:
    print("   SKIPPED (the parser cannot read it) %s `%s`: %s" % (x_[0], x_[1], SKIP10.get(x_, "UNDECLARED")))
for x_ in es_bad:
    print("   BAD (printed a compile error, runs legal or crashes) %s" % (x_,))
check("ERRSWEEP", es_now and not es_bad and not es_und_skip and not es_und_chg and not es_stale,
      "%d compile-error lines read, each refused with no crash: bad %d; skipped %d (undeclared skipped %d); of the "
      "starting commit's lines %d changed legality (undeclared change %d, stale %d)" % (
          len(es_now), len(es_bad), len(es_skip), len(es_und_skip), len(es_chg), len(es_und_chg), len(es_stale)))
D8.clear()
D8.update(D10)

exec(compile(_src9[_src9.index('unit9("NULLABLE", '):_src9.index('unit9("SUCCESSOR", ')], P1124, "exec"),
     globals())                                              # noqa: S102  predfold1124's NULLABLE, verbatim

unit10("SUCCESSOR10", "every earlier in-force model re-run (predfold1124 itself, then predfix88 and the fourteen it "
       "re-ran, library.md served from their PINNED commits by predfix88's runner); each red declared by a key with "
       "no document line numbers (C1): DOC/MARKS reds by their MISSING-line set (C2), a red whose check printed an "
       "engine CRASH row by its crash rows, class CRASH, never \"documents moved\" (C3); a raw traceback never", 3600)
PINS10 = dict(PINS8)
PINS10["predfix88"] = "50a39f8e4"
ORDER10 = ["predfold1124", "predfix88"] + list(PINS8)
DECLF10 = os.path.join(HERE10, "predfix90_succ_decl.tsv")
SDECL10 = {}
if os.path.exists(DECLF10):
    for l_ in builtins.open(DECLF10, encoding="utf-8").read().split("\n"):
        if l_ and not l_.startswith("#"):
            m_, r_, cls_, why_, key_ = l_.split("\t", 4)
            SDECL10.setdefault(m_, {})[r_] = (cls_, key_, why_)
CRASH10 = re.compile(r"\bCRASH [A-Z]\w*(Error|Exception)\b|'CRASH', ")


def norm10(t):
    """C1: a key with no document line numbers."""
    t = re.sub(r"\('(\w+\.md)', \d+", r"('\1', N", t)
    t = re.sub(r"(\w+\.md):\d+", r"\1:N", t)
    return t


def red_key10(name, out_lines, fline):
    """(class, key) of one red: its section is the lines between its `== NAME:` header and its verdict."""
    sec, on = [], False
    for x_ in out_lines:
        if x_.startswith("== %s:" % name) or re.match(r"== %s\b" % re.escape(name), x_):
            on, sec = True, []
            continue
        if on and (x_.startswith("FAIL %s:" % name) or x_.startswith("PASS %s:" % name)):
            break
        if on:
            sec.append(x_)
    crash = sorted(set(norm10(x_.strip()) for x_ in sec if CRASH10.search(x_)))
    if crash:
        return "CRASH", " || ".join(crash)
    miss = sorted(set(norm10(x_.strip()) for x_ in sec if x_.strip().startswith("MISSING")))
    if miss:
        return "MISSING", " || ".join(miss)
    return "LINE", norm10(fline)


succ_bad, succ_n, succ_t, succ_seen = [], 0, {}, []
if s10("q13") and SDECL10:
    _m = next(m_ for m_ in sorted(SDECL10) if any(v_[0] == "MISSING" for v_ in SDECL10[m_].values()))
    _r = next(r_ for r_ in sorted(SDECL10[_m]) if SDECL10[_m][r_][0] == "MISSING")
    SDECL10[_m][_r] = (SDECL10[_m][_r][0], SDECL10[_m][_r][1] + " || MISSING [x] planted", SDECL10[_m][_r][2])
if not LIGHT10:
    for mname in ORDER10:
        env = {k: v for k, v in os.environ.items() if not k.endswith(("_SABOTAGE", "_ENGINE", "_PROBE", "_LIGHT",
                                                                       "_DUMPSUCC"))}
        for v_ in list(LIGHTENV8.values()) + ["PREDFIX88_LIGHT", "PREDFOLD1124_LIGHT"]:
            env[v_] = "1"                                    # their own SUCCESSOR re-runs the same list: run once, here
        t0 = time.time()
        cmd = [sys.executable, "-I", "-B", P1124] if mname == "predfold1124" else \
            [sys.executable, "-I", "-B", P88, "--succ", os.path.join(LANES10, mname + "_evidence", mname + "_model.py"),
             PINS10[mname]]
        try:
            out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env,
                                 timeout=900).stdout
        except subprocess.TimeoutExpired:
            out = "TIMEOUT: model %s did not finish in 900 s" % mname
        succ_t[mname] = time.time() - t0
        if os.environ.get("PREDFIX90_DUMPSUCC"):
            builtins.open(os.path.join(os.environ["PREDFIX90_DUMPSUCC"], mname + ".out"), "w").write(out)
        succ_n += 1
        lines_ = out.rstrip("\n").split("\n")
        last = lines_[-1]
        mm = re.match(r"%s_model: (\d+) checks, (\d+) failed(?: \(([^)]*)\))?$" % mname, last)
        reds = {}
        if mm and not any(x_.startswith("Traceback") for x_ in lines_):
            for r in [x_.strip() for x_ in (mm.group(3) or "").split(",") if x_.strip()]:
                fl_ = next((l_ for l_ in lines_ if l_.startswith("FAIL %s:" % r) or
                            re.match(r"%s\s+FAIL\b" % re.escape(r), l_)), "")
                reds[r] = red_key10(r, lines_, fl_)
        else:
            reds["TRACEBACK"] = ("TRACEBACK", last)
        decl = SDECL10.get(mname, {})
        print("   %-13s (%s, %.1f s) last line: %s" % (mname, "its own documents" if mname == "predfold1124" else
                                                       "library at " + PINS10[mname], succ_t[mname], last[:150]))
        for r, (cls_, key_) in sorted(reds.items()):
            succ_seen.append((mname, r, cls_, key_))
            d = decl.get(r)
            if r == "TRACEBACK":
                succ_bad.append((mname, "TRACEBACK"))
                print("      TRACEBACK (never declarable): %s" % key_[:300])
            elif d is None:
                succ_bad.append((mname, r, "UNDECLARED"))
                print("      %s UNDECLARED (%s): %s" % (r, cls_, key_[:600]))
            elif d[0] != cls_ or d[1] != key_:
                succ_bad.append((mname, r, "MISSING SET CHANGED" if cls_ == "MISSING" else "KEY CHANGED"))
                print("      %s %s:\n         declared (%s): %s\n         now (%s):      %s" % (
                    r, "MISSING SET CHANGED" if cls_ == "MISSING" else "KEY CHANGED", d[0], d[1][:600], cls_,
                    key_[:600]))
            else:
                print("      %s declared (%s): %s\n         its key: %s" % (r, cls_, d[2], key_[:300]))
        gone = sorted(set(decl) - set(reds))
        if gone:
            succ_bad.append((mname, "GREEN NOW", gone))
            print("      declared but green now: %s" % gone)
    if os.environ.get("PREDFIX90_WRITEDECL"):                # the declarations' source run (the lane's scratch)
        with builtins.open(os.environ["PREDFIX90_WRITEDECL"], "w", encoding="utf-8") as fh:
            for m_, r_, c_, k_ in succ_seen:
                fh.write("%s\t%s\t%s\t%s\t%s\n" % (m_, r_, c_, SDECL10.get(m_, {}).get(r_, ("", "", "?"))[2], k_))
check("SUCCESSOR10", LIGHT10 or (succ_n == len(ORDER10) == 16 and not succ_bad),
      "%d earlier models re-run (%.0f s in all), each red against its declared key (%d declared): %s"
      % (succ_n, sum(succ_t.values()), sum(len(v) for v in SDECL10.values()), succ_bad or "every red declared, its "
         "key unchanged; no traceback"))

unit10("QUOTES", "the owner's sentences the fixed pieces quote, each PINNED to its piece and to the record at the "
       "pinned start commit; the rulings' titles cited whole")
REC10 = _git8("docs/design/plan_row_bodies/COND-FAMILY.md", START10)
RW10 = ws(REC10)
QQ10 = [
    ("path-rules: yes", PATHS_T),
    ("1. in the label DAG there is a target label and a starting label. The starting label has at least one path to "
     "the target label", PATHS_T),
    ("2. the path may not contain any underscore labels full or prefix unless the underscore prefix label is the "
     "start", PATHS_T),
    ("3. within a binding, any label on the path may be used as a start label", PATHS_T),
    ("4. if a legal path exists a.b.c and c can be unambiguously referenced from a, then b can be skipped a.c", PATHS_T),
    ("[_t = A ] is equivalent to [_ = [t = A ]]", PATHS_T),
    ("[_t = A ] is equivalent to [_ = [t = A ]]", EQI_T),
    ("Setting a label closes a path (through the shorthand in that binding) but doesn't block out the target.", RULE_T),
    ("Setting a label closes a path (through the shorthand in that binding) but doesn't block out the target.", CA_T),
    ("shorthand-is-callers: yes thats it exactly", AD_T),
    ("exact-count-unspecified: agree error", UN_T),
    ("capture-in-set: error.", "lib/structural/capture/in-set"),
    ("options-reach-constants: yes", "lib/builtin/options"),
    ("option-hole-explicit: explicit", "core/patterns/flags"),
    ("you can't go through A to get inside", EXP_T),
]
q10_miss = [(q_[:60], w_, ws(q_) in RW10) for q_, w_ in QQ10 if ws(q_) not in RW10 or ws(q_) not in ws(piece8(w_))]
TT10 = ["2026-11-23 OWNER RULING — path-rules: yes (his four rules for paths within a binding, the manager's two "
        "readings of them, and rules 5 and 6 across bindings)",
        '2026-11-23 OWNER RULING — shorthand-is-callers: "yes thats it exactly. Setting a label closes a path (through '
        'the shorthand in that binding) but doesn\'t block out the target."',
        "2026-11-23 OWNER RULING — options-reach-constants: yes (a file's weak `i` reaches a string constant)",
        "2026-11-25 MANAGER — review r90 (predfold1124): the dispositions; no owner words"]
DET10 = D8["core_details.md"] + D8["library_details.md"] + D8["parked_details.md"]
t10_miss = [t_[:60] for t_ in TT10 if ws(t_) not in heads8(REC10) or ws(t_) not in ws(DET10)]
check("QUOTES", not q10_miss and not t10_miss,
      "%d quoted sentences, each in the record at %s AND in its own piece, missing: %s; %d record titles cited, not a "
      "title or not cited: %s" % (len(QQ10), START10, q10_miss or "none", len(TT10), t10_miss or "none"))

unit10("DOC", "every line this model formats occurs verbatim in the piece its tag names")
DLN10 = list(LINES)
if s10("q15") and DLN10:
    DLN10[0] = (DLN10[0][0], DLN10[0][1].replace("WHOLE `", "WHOLE `x", 1))
D8.clear()
D8.update(NOWS)
d10_miss = [(t_, L_) for t_, L_ in DLN10 if ws(L_) not in ws(piece8(t_))]
for t_, L_ in d10_miss:
    print("   MISSING [%s] %s" % (t_, L_))
check("DOC", DLN10 and not d10_miss, "%d lines, each in its own piece; missing: %d" % (len(DLN10), len(d10_miss)))

failed10 = [n_ for n_, ok_ in RESULTS if not ok_]
print("predfix90_model: %d checks, %d failed%s" % (len(RESULTS), len(failed10),
                                                  (" (%s)" % ", ".join(failed10)) if failed10 else ""))
sys.exit(1 if failed10 else 0)
