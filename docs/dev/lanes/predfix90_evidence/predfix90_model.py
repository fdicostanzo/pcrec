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
    return X10[0] and not s10("q1x")


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
    return t[c_:e_].strip() == t[p:e].strip() or t[c_:e_].strip() == "(%s)" % t[p:e].strip()


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
        labelled = _directly(t, br, enc, p, e) or (not enc and lab_above)
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
        if steps[0] in ("rx",) or steps[0] in PROV or steps[0] in MACROS:
            continue
        new = rd
        bad = next((s_ for s_ in steps[1:] if s_.startswith("_")), None)
        if bad:
            raise CompileError("`%s`: the path %s `%s`, not the start (a compile error, path-rules rule 2)" %
                               (rd, RULE2_10, bad))
        try:
            tt, lo, hi, outside, env, sk = _start10(steps[0], t, bd, heads, {})
            res = walk10(tt, lo, hi, steps[1:-1], steps[-1], outside, env, bd, heads, [steps[0]])
        except Und:
            res = None
        if res:
            oks = sorted(set(tuple(x[1]) for x in res if x[0] == "ok"))
            walls = [x for x in res if x[0] == "wall"]
            if not oks and walls:
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


def wrap10(t):
    """every part label whose content is a stack or an expression, handed over parenthesised (the nested form)."""
    for _ in range(20):
        changed = False
        for nm, s_, c_, e_ in sorted(_brackets(t), key=lambda b: -b[1]):
            body = t[c_:e_]
            b0 = body.strip()
            if not b0 or (b0.startswith("(") and close_paren(b0, 0) == len(b0) - 1):
                continue
            stk = b0.startswith("[") and _close_br(b0, 0) == len(b0) - 1
            ops = re.search(r"\bSEQ\b|[&|]", _mask_conds(b0)) is not None and not (
                re.fullmatch(r"[\w.]+\(.*\)", b0, re.S) and close_paren(b0, b0.index("(")) == len(b0) - 1)
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
    return P10F["prog"](wrap10(expr), b2, **opts)
