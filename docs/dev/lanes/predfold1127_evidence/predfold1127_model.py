#!/usr/bin/env python3
"""predfold1127_model.py: lane predfold1127's evidence, the successor of predfix111_model.py.

The fold of the owner's rulings gate-beside-label and one-path (record docs/design/plan_row_bodies/COND-FAMILY.md,
2026-11-27). DESIGN evidence only: nothing here rules; no check under `make` reads it.

It LOADS predfix111's model unchanged up to its checks (`# ==== CHECKS`; the older models load through it), then
puts its own walker WALK1127 in front, switched by X1127[0] (off: predfix111's walker WALK111, the control):
  WALK1127 the one-path rule, written from the ruled statement as asked: a step in a path may be skipped only when
           exactly one label of that name is visible from the start (counted within one match: targets in two
           branches of one `|` are one each; a target behind a gate is visible and counted; a target behind a wall
           is not visible); a part used alone (a gate) is never skipped, even holding the only target (line 2);
           the array form is exempt (line 3; its reading over a gate is the switch READ1127["array"]); a name counts
           as used once or twice by what lies under the path's start (line 5). A read that skips nothing (each
           target a direct child of the start) is label flow, unchanged (the last mention in a sequence).
           "Skips" means a node lies between the start and the target: a label, a group, a part or a call used
           alone, a list's alias, or an argument's place in a body (its parameter).
  FE1127   predfix111's front end FE111, with the array flag passed to the walker (a read written `@a.b`).
Every legal printed line is ALSO answered by MECH111 (python `re` on a regex built mechanically from the program
text and its bindings' bodies), never from the engine. The verdict is the last line,
`predfold1127_model: N checks, F failed`; it exits non-zero iff that line reports a failure.
`PREDFOLD1127_LIGHT=1` skips SUCCESSOR1127; `PREDFOLD1127_SUCCDIR=DIR` an existing scratch directory for the
successor outputs; `PREDFOLD1127_READDUMP=1` reads DIR instead of re-running; `PREDFOLD1127_SABOTAGE=sN` plants one
wrong rule, fact or text per check (PLANTS1127); `=all` runs each plant in its own LIGHT subprocess.
Run: `timeout 6000 python3 -I -B <this dir>/predfold1127_model.py`.
"""
import builtins
import os
import re
import subprocess
import sys

MY1127 = os.path.abspath(__file__)
HERE1127 = os.path.dirname(MY1127)
LANES1127 = os.path.normpath(os.path.join(HERE1127, ".."))
P111 = os.path.join(LANES1127, "predfix111_evidence", "predfix111_model.py")
START1127 = "637a5e79c"                                      # this lane's starting commit (lane/predfold1127), PINNED
SAB1127 = os.environ.get("PREDFOLD1127_SABOTAGE", "")
LIGHT1127 = os.environ.get("PREDFOLD1127_LIGHT") == "1"
_src111 = builtins.open(P111, encoding="utf-8").read()
_a1127 = _src111.index("# ==== CHECKS (a probe loads the model up to this line)")
__file__ = P111
_sav1127 = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith(("PREDFIX111_", "PREDFOLD1125_", "PREDFIX90_"))}
exec(compile(_src111[:_a1127], P111, "exec"), globals())     # noqa: S102  predfix111's engines, unchanged
os.environ.update(_sav1127)
__file__ = MY1127
_WALK111, _FE111 = walk111, fe111                            # noqa: F821  the loaded walker and front end
X1127 = [True]
READ1127 = {"array": "error", "direct": "error"}             # reading (d), printed marked: `error` (conservative);
#                                                             `direct`: a target reached directly beside a skipped one
#                                                             (`c.d`): `error` (the ruled four), `wins` the other reading


def s1127(q):
    return SAB1127 == q


# ================================================================== WALK1127: the one-path rule
def _between(start, x, P):
    """every SPOT of a node named x below start: (node, nodes between, gates skipped, walls crossed, chain); the
    nodes between are the table's kinds and a list's alias or an argument's place (no name of its own); the chain
    is every node passed from start, so an argument a body places twice gives two spots."""
    out = []

    def go(n, betw, gates, walls, chain):
        for k in n.kids:
            ch = chain + [k]
            kk = kind_of(k)                                  # noqa: F821
            if _named(k) == x and kk:                        # noqa: F821
                out.append((k, list(betw), list(gates), list(walls), ch))
            if kk is None:
                go(k, betw + ([k] if k.k in ("list", "arg") else []), gates, walls, ch)
                continue
            ctx = context(k, P.root)                         # noqa: F821
            if ctx == "beyond" and kk in ("alone", "call"):
                kk = "argalone"
            cell = KINDS111[kk][2 if ctx == "inside" else 3]   # noqa: F821
            if cell == "yes":
                go(k, betw + [k], gates, walls, ch)
            elif cell == "gate":
                go(k, betw + [k], gates + [k], walls, ch)
            else:
                go(k, betw + [k], gates, walls + [k], ch)
    go(start, [], [], [], [start])
    return out


def _cooccur(a, b):
    """two spots (their chains from the start) can be set in one match unless they part in two branches of one
    `|` (an alternation of the language, or of an rx literal: handed to the loaded builder, as WALK111 does)."""
    i = 0
    while i < min(len(a), len(b)) and a[i] is b[i]:
        i += 1
    lca = a[i - 1]
    if lca.k == "rx" and lca.name == "|":
        raise Unparsed("an alternation inside an rx literal")   # noqa: F821
    return lca.k != "alt"


def _cooccur_starts(a, b):
    """two spots under two starts (two labels of the start's name): by the starts' own nodes."""
    return _cooccur(_anc(a[0][-1]) + a[5][1:], _anc(b[0][-1]) + b[5][1:])


def _anc(n):
    out = []
    while n is not None:
        out.append(n)
        n = n.parent
    return out[::-1]


NEST1127 = [0]


def _fullpaths(P, path, cands):
    """each target's shortest path that names it alone: the fewest nodes between kept for which the walker itself
    reaches that one target and no other (None: no path names it)."""
    import itertools
    out = []
    for route, node, betw in cands:
        if any(n.name is None for n in route):
            out.append(None)
            continue
        betw = [n for n in betw if n.name]                   # a nameless place (an argument's) is no written step
        opt = list(betw)                                     # the walker itself keeps what may not be skipped
        found = None
        NEST1127[0] += 1
        try:
            for k in range(len(opt) + 1):
                for keep in itertools.combinations(opt, k):
                    ws_ = [n.name for n in route[:-1]] + [n.name for n in betw if n not in opt or n in keep] + [node.name]
                    try:
                        r = walk1127(P, ws_)
                    except (Refused, Unparsed):              # noqa: F821
                        continue
                    if r[2] is node:
                        found = ".".join(ws_)
                        break
                if found:
                    break
        finally:
            NEST1127[0] -= 1
        out.append(found)
    return out


def _onepath_msg(P, path, cands, gate):
    rd_ = ".".join(path)
    why = ("a `%s` sits behind a gate (a part used alone is never skipped)" % path[-1] if gate else
           "%d labels `%s` are visible from `%s`, so no step may be skipped" % (len(cands), path[-1], path[0]))
    if NEST1127[0]:
        return "`%s`: %s" % (rd_, why)
    fps = _fullpaths(P, path, cands)
    named = sorted(set(f for f in fps if f and f != rd_))
    unnamed = sum(1 for f in fps if not f or f == rd_)
    if named:
        say = "write the full path, " + " or ".join("`%s`" % f for f in named)
        if unnamed:
            say += "; %d of them no other path from `%s` names" % (unnamed, path[0])
    else:
        say = "no path from `%s` names one of them alone" % path[0]
    return "`%s`: %s: %s (a compile error, core/labels/rule/paths rule 4, one-path)" % (rd_, why, say)


def walk1127(P, path, reading=None, array=False):
    """judge the read `path` in P by the one-path rule: ("legal", route, target, how) or Refused."""
    rd = dict(READ1127)
    if reading:
        rd.update(reading)
    nodes = list(_subtree(P.root))                           # noqa: F821
    s1 = path[0]
    starts = [n for n in nodes if _named(n) == s1 and context(n, P.root) == "inside" and kind_of(n)]   # noqa: F821
    starts = [n for n in starts if KINDS111[kind_of(n)][0] == "yes"]   # noqa: F821
    if not starts:
        raise Unparsed("no start " + s1)                     # noqa: F821
    alone_starts = [n for n in starts if kind_of(n) in ("alone", "call")]   # noqa: F821
    if len(alone_starts) > 1:
        raise Refused("`%s`: %s is used %d times here; label the part (`[left = %s]`) to read one use" % (   # noqa: F821
            ".".join(path), s1, len(alone_starts), s1))
    routes = [([s0], [s0]) for s0 in starts]                 # (route of named nodes, full route for the relabel)
    how = "one"
    gate_ok = array and rd["array"] == "exempt"              # reading (d): the array form through a gate
    for i, x in enumerate(path[1:], 1):
        last = i == len(path) - 1
        cands = []                                            # (route, node, between, gates, full)
        for route, full in routes:
            for node, betw, gates, walls, chain in _between(route[-1], x, P):
                if walls:
                    continue
                k = kind_of(node)                            # noqa: F821
                ctx = context(node, P.root)                  # noqa: F821
                col = 1 if ctx == "inside" else 3
                if KINDS111[k][col] != "yes" and not (ctx != "inside" and KINDS111[k][3] == "yes"):   # noqa: F821
                    continue
                if not last and k in ("alone", "call"):      # line 5: counted under the path's start
                    same = [n for n in _subtree(route[-1]) if _named(n) == x and kind_of(n) in ("alone", "call")   # noqa: F821
                            and context(n, P.root) == "inside"]   # noqa: F821
                    if len(same) > 1:
                        raise Refused("`%s`: `%s` is used more than once here, so it is not a step (a compile "   # noqa: F821
                                      "error, alone-as-middle)" % (".".join(path), x))
                if last and k not in ("label", "group"):
                    continue
                cands.append((route, node, betw, gates, full, chain))
        if not cands:
            raise Refused(_why(P, [(r, [], f) for r, f in routes], x, path))   # noqa: F821
        uniq = []
        for c in cands:                                      # one per spot: a start's route and its chain
            if not any(u[0] is c[0] and len(u[5]) == len(c[5]) and all(p is q for p, q in zip(u[5], c[5])) for u in uniq):
                uniq.append(c)
        gated = [c for c in uniq if c[3]] if not gate_ok else []
        if array and last and not gated:                     # line 3: the array form is exempt
            return ("legal", None, None, "array")
        skipping = [c for c in uniq if c[2]]
        if s1127("s3"):
            gated = []                                       # plant: the gate skippable
        if gated:                                            # line 2, and gate-beside-label
            raise Refused(_onepath_msg(P, path, [(c[0] + [c[1]], c[1], c[2]) for c in uniq], True))   # noqa: F821
        for j, a in enumerate(uniq):                          # `&` first: the ambiguous reference, as before
            for b in uniq[j + 1:]:
                if a[0] is b[0]:
                    ca, cb = a[0] + a[5][1:], b[0] + b[5][1:]
                    q = 0
                    while q < min(len(ca), len(cb)) and ca[q] is cb[q]:
                        q += 1
                    if ca[q - 1].k == "and":
                        raise Refused("`%s`: both sides of `&` set `%s`, an ambiguous reference (a compile error, "   # noqa: F821
                                      "core/labels/flow)" % (".".join(path), path[-1]))
        co = any(_cooccur(a[0] + a[5][1:], b[0] + b[5][1:]) if a[0] is b[0] else _cooccur_starts(a, b)
                 for j, a in enumerate(uniq) for b in uniq[j + 1:])
        if co and skipping and rd["direct"] == "wins" and len(skipping) < len(uniq):
            uniq = [c for c in uniq if not c[2]]             # the other reading: a full path to one target wins
            skipping = []
            co = len(uniq) > 1
        if co and skipping and not s1127("s2"):
            raise Refused(_onepath_msg(P, path, [(c[0] + [c[1]], c[1], c[2]) for c in uniq], False))   # noqa: F821
        if len(uniq) > 1 and not co:
            how = "branch taken"
        elif len(uniq) > 1:
            lca = _lca([c[1] for c in uniq])                 # noqa: F821
            if lca.k in ("seq", "rx") and len(set(id(c[1]) for c in uniq)) == len(uniq):
                pick = max(uniq, key=lambda c: _pos_in(lca, c[1]))   # noqa: F821
                uniq = [pick]
                how = "last mention"
            elif lca.k in ("seq", "rx", "use", "label", "grp"):
                raise Unparsed("one node at two spots, nothing skipped")   # noqa: F821
            else:
                raise Refused("`%s`: both sides of `&` set `%s`, an ambiguous reference (a compile error, "   # noqa: F821
                              "core/labels/flow)" % (".".join(path), path[-1]))
        routes = [(c[0] + [c[1]], c[4] + c[3] + [c[1]]) for c in uniq]
    if how == "branch taken":
        return ("legal", None, None, how)
    return ("legal", routes[0][1], routes[0][0][-1], how)


class Prog1127(Prog111):                                     # noqa: F821
    """predfix111's parser, its rx literal reader taking a hole or a named group inside a plain group (`(?:..)`,
    `(?>..)`, `(?=..)`): the item joins the nearest enclosing node, as a provided body writes them."""

    def rx(self, tid, a, b, env, own, depth):
        s = self.texts[tid]
        n = N111("rx", tid, a, b)                            # noqa: F821
        i, d, stack = a, 0, [n]

        def top():
            return next(x for x in reversed(stack) if x is not None)
        while i < b:
            c = s[i]
            if c == "\\":
                i += 2
                continue
            if c == "[":
                j = i + 1
                if j < b and s[j] == "^":
                    j += 1
                if j < b and s[j] == "]":
                    j += 1
                while j < b and s[j] != "]":
                    j += 2 if s[j] == "\\" else 1
                i = j + 1
                continue
            if s.startswith("${", i):
                j = TR11._brace_end(s, i + 1)                # noqa: F821
                h = N111("hole", tid, i, j, [self.alt(tid, i + 2, j - 1, env, own, depth)])   # noqa: F821
                h.depth = d
                top().kids.append(h)
                i = j
                continue
            if c == "(":
                m = re.match(r"\(\?<(:?)(_?[A-Za-z][A-Za-z0-9_]*)>", s[i:b])
                if m:
                    g = N111("grp", tid, i, None, [], m.group(2))   # noqa: F821
                    g.depth = d
                    inner = N111("rx", tid, i + m.end(), None)   # noqa: F821
                    g.kids = [inner]
                    top().kids.append(g)
                    stack.append(g)
                    stack.append(inner)
                    d = 0
                    i += m.end()
                    continue
                if re.match(r"\(\?<:?\$\{", s[i:b]):
                    raise Unparsed("a group-name hole")      # noqa: F821
                stack.append(None)
                d += 1
                i += 1
                continue
            if c == "|" and d == 0 and len(stack) <= 2:
                top().name = "|"
            if c == ")":
                t_ = stack.pop()
                if t_ is None:
                    d -= 1
                else:
                    t_.b = i
                    g = stack.pop()
                    g.b = i + 1
                    d = g.depth
                    if i + 1 < b and s[i + 1] in "*+?{":
                        g.depth = 99
                i += 1
                continue
            i += 1
        if len(stack) != 1:
            raise Unparsed("rx parentheses")                 # noqa: F821
        return n


GQ1127 = re.compile(r"\b(some|every|count|occurs\.none|occurs\.all|none|all)\(\s*@")


def prep1127(expr, binds):
    """the program as the WALKER parses it (never what the engine runs): a group question `f(@a.b, ..)` stands as a
    condition `(a.b: /x/)`; a provided name called (LIBMACROS, its body READ from library.md by predspot's reader)
    joins the bindings, its keyword arguments written by position. Returns (expr, binds, provided names added)."""
    e, out, i = expr, [], 0
    while True:
        m = GQ1127.search(e, i)
        if not m:
            break
        a = m.start()
        b = TR11._group_end(e, m.end(1))                     # noqa: F821
        pm = re.match(r"@([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)", e[m.end() - 1:])
        e = e[:a] + "(%s: /x/)" % pm.group(1) + e[b:]
        i = a + 1
    have = set(re.match(r"\s*([A-Za-z_]\w*)", x).group(1) for x in binds)
    added = []
    for nm, (ps, body) in sorted(LIBMACROS.items()):        # noqa: F821
        if nm in have or not re.search(r"(?<![\w.])%s\(" % re.escape(nm), e + " ".join(binds)):
            continue
        added.append(nm)
        binds = list(binds) + ["%s(%s) := %s" % (nm, ", ".join(p for p, _ in ps), body)]

        j = 0
        while True:
            mm = re.compile(r"(?<![\w.])%s\(" % re.escape(nm)).search(e, j)
            if not mm:
                break
            k = TR11._group_end(e, mm.end() - 1)             # noqa: F821
            args = [e[x:y] for x, y in split_top_commas(e, mm.end(), k - 1)]   # noqa: F821
            names = [p for p, _ in ps]
            posd = {}
            for q, a_ in enumerate(args):
                kw = re.match(r"\s*([A-Za-z_]\w*)\s*=(?!=)\s*(.*)$", a_, re.S)
                if kw and kw.group(1) in names:
                    posd[kw.group(1)] = kw.group(2)
                else:
                    posd[names[q]] = a_
            new = "%s(%s)" % (nm, ", ".join(posd.get(p, "//") for p in names))
            e = e[:mm.start()] + new + e[k:]
            j = mm.start() + len(new)
    return e, binds, added


def walk111(P, path, reading=None, array=False):            # noqa: F811  the walker the front end calls
    if not X1127[0]:
        return _WALK111(P, path, reading)
    return walk1127(P, path, reading, array)


def fe111(expr, binds):                                      # noqa: F811  FE111 with the array flag passed
    e = _lookaround_not(expr)                                # noqa: F821
    e = re.sub(r"\[(\s*_?\w+\s*=\s*)\(\s*([A-Za-z_]\w*)\s*\)\]", r"[\1\2]", e)
    if "when(" in e:
        e = _when_cond(e)                                    # noqa: F821
    e = _caret_cond(e)                                       # noqa: F821
    e, binds = _name_hole_mark(e, list(binds))               # noqa: F821
    e = _index_const(e, binds)                               # noqa: F821
    reads = reads_of(e)                                      # noqa: F821
    _bang_ahead_labels(e, [r[0] for r in reads])             # noqa: F821
    todo = [r for r in reads if len(r[0]) >= 2]
    if not todo:
        return e, binds
    ew, bw, added = prep1127(e, binds) if X1127[0] else (e, binds, [])
    try:
        P = (Prog1127 if X1127[0] else Prog111)(ew, bw)      # noqa: F821
    except Unparsed:                                         # noqa: F821
        return e, binds
    relabels = []
    for path, a, b in todo:
        arr = a > 0 and e[a - 1] == "@"
        try:
            r = walk111(P, path, None, arr)
        except Unparsed:                                     # noqa: F821
            continue
        except Refused as x:                                 # noqa: F821
            WALKLOG111.append((expr, ".".join(path), "refused"))   # noqa: F821
            raise CompileError(str(x))                       # noqa: F821
        WALKLOG111.append((expr, ".".join(path), "legal"))   # noqa: F821
        if r[1] and any(kind_of(n) in ("alone", "call", "group", "ugroup") for n in r[1][1:-1] + r[1][:1]   # noqa: F821
                        if not (n is r[1][0] and kind_of(n) in ("alone", "call"))):   # noqa: F821
            relabels.append((path, a, b, r[1]))
    if len(relabels) != 1 or added or ew != e:
        return e, binds
    path, a, b, route = relabels[0]
    e2, b2, rd = relabel(P, route, path)                     # noqa: F821
    old = ".".join(path)
    if e2.count("(" + old + ":") + e2.count("(" + old + " :") + e2.count("@" + old) != 1:
        return e, binds
    e2 = e2.replace("(" + old + ":", "(" + rd + ":").replace("(" + old + " :", "(" + rd + " :").replace("@" + old, "@" + rd)
    return e2, b2


def walk_v27(expr, binds, read, reading=None, array=False, old=False):
    """a verdict on one read: ('legal', text id, name, how) | ('refused', msg) | ('unparsed', why)."""
    try:
        if old:
            P = Prog111(expr, binds)                         # noqa: F821
            r = _WALK111(P, read.split("."), reading)
        else:
            ew, bw, _ = prep1127(expr, binds)
            P = Prog1127(ew, bw)
            r = walk1127(P, read.split("."), reading, array)
    except Refused as e:                                     # noqa: F821
        return ("refused", str(e))
    except Unparsed as e:                                    # noqa: F821
        return ("unparsed", str(e))
    if r[2] is None:
        return ("legal", None, None, r[3])
    return ("legal", r[2].tid, r[2].name, r[3])


# ==== CHECKS (a probe loads the model up to this line)
RESULTS.clear()                                              # noqa: F821


def unit1127(name, what):
    print("== %s: %s" % (name, what))


PB = "P := /(?<d>\\d)/"
QB = "Q := /,(?<d>\\d)/"
AB = "A := /(?<h>\\d)/"
DATE = 'date := [y = /(?<v>\\d)/] SEQ "-" SEQ [m = /(?<v>\\d)/]'
T2 = ["7,3", "3,7", "1,2", "7,7", "x3,1", "3,3", "7,3x"]
TD = ["7-3", "3-7", "1-2", "7-7", "x3-1", "3-3"]


def same_as(P, rx_, texts):
    """the program's answers (whole, searched, find-all) against a regex written by hand from the ruled sentence."""
    return P is not None and ans11(P, texts) == ans11(RePg(rx_), texts)   # noqa: F821


unit1127("CANARY1127", "X1127 off is predfix111's walker (the control): `date.v` legal (the last mention) and "
         "gate-beside's `n.d` legal (reading (ii)); X1127 on refuses both")
X1127[0] = False
c0 = run11("date & (date.v: <5)", [DATE])                    # noqa: F821
c1 = run11("[n = ([a = P] SEQ Q)] & (n.d: <5)", [PB, QB])     # noqa: F821
X1127[0] = True
c2 = run11("date & (date.v: <5)", [DATE])                    # noqa: F821
c3 = run11("[n = ([a = P] SEQ Q)] & (n.d: <5)", [PB, QB])     # noqa: F821
if s1127("s1"):
    c2 = c0
check("CANARY1127", c0[0] is not None and c1[0] is not None and c2[0] is None and c3[0] is None,   # noqa: F821
      "off: %s / %s; on: %s / %s" % ("legal" if c0[0] else c0[1], "legal" if c1[0] else c1[1], c2[1], c3[1]))

unit1127("RULE1127", "reads judged by the model's full program builder against hand-filled verdicts, each citing the "
         "ruled line it rests on; every legal read's answers against a regex written by hand from the sentence")
# (program, bindings, expected: a hand regex for a legal read, or "refused" with a fragment its message carries, ground)
RULE1127 = [
    ("date & (date.v: <5)", [DATE], ("refused", "`date.m.v`"), "one-path line 4 (his example)"),
    ("date & (date.m.v: <5)", [DATE], r"\d-[0-4]", "rule 1, the full path"),
    ("date & (date.y.v: <5)", [DATE], r"[0-4]-\d", "rule 1, the full path"),
    ("pair & (pair.x: <5)", ["pair := [b = /(?<x>\\d)/] | [c = /a(?<x>\\d)/]"], r"(?:[0-4]|a[0-4])",
     "one-path line 1 (his example): the branch taken"),
    ("[n = ([a = P] SEQ [b = Q])] & (n.d: <5)", [PB, QB], ("refused", "`n.b.d`"), "one-path line 4"),
    ("[n = ([a = P] SEQ [b = Q])] & (n.b.d: <5)", [PB, QB], r"\d,[0-4]", "rule 1"),
    ("[n = ([a = P] SEQ [b = Q])] & some(@n.d, <5)", [PB, QB], r"(?:[0-4],\d|\d,[0-4])", "one-path line 3, exempt"),
    ("[n = ([a = P] SEQ Q)] & (n.d: <5)", [PB, QB], ("refused", "`n.Q.d`"), "gate-beside-label: error"),
    ("[n = ([a = P] SEQ Q)] & (n.d: <5)", [PB, QB], ("refused", "`n.a.d`"), "gate-beside-label: `n.a.d` or `n.Q.d`"),
    ("[n = ([a = P] SEQ Q)] & (n.a.d: <5)", [PB, QB], r"[0-4],\d", "rule 1"),
    ("[n = (P SEQ Q)] & (n.d: <5)", [PB, QB], ("refused", "`n.Q.d`"), "one-path line 2 (alone-as-middle)"),
    ("/(?<g>${A})x/ & (g.h: <5)", [AB], ("refused", "`g.A.h`"), "one-path line 2: the only target, gated"),
    ("[n = ([m = P] SEQ [_x = Q])] & (n.d: <5)", [PB, QB], r"[0-4],\d", "skip-past-wall: a wall hides its labels"),
    ("[n = ([m = P] & [_x = Q])] & (n.d: <5)", ["P := /(?<d>\\d)\\d/", "Q := /\\d(?<d>\\d)/"], r"[0-4]\d",
     "skip-past-wall, across `&`"),
    ("[n = ([m = P] & [k = Q])] & (n.d: <5)", ["P := /(?<d>\\d)\\d/", "Q := /\\d(?<d>\\d)/"], ("refused", "`&`"),
     "rule 4: across `&` ambiguous (one-path keeps it)"),
    ("D2 & (D2.c: \"3\")", ["D2 := /(?<c>\\d)(?<c>\\d)/"], r"\d3", "label flow: nothing skipped (a reading)"),
    ("[aa = /(?<h>\\d)/] SEQ \",\" SEQ [aa = /(?<h>\\d)/] & (aa.h: <5)", [], r"\d,[0-4]",
     "label flow: nothing skipped (a reading)"),
    ("[n = (P SEQ Q)] SEQ \";\" SEQ [m = (P SEQ Q)] & (n.Q.d: <5)", [PB, QB], r"\d,[0-4];\d,\d",
     "one-path line 5: counted under the start"),
    ("[n = (Q SEQ Q)] & (n.Q.d: <5)", [QB], ("refused", "more than once"), "one-path line 5: twice under the start"),
    ("X & (X.h: <5)", [AB, "X := [n = [m = A]] SEQ \"!\""], r"[0-4]!", "rule 4, one target, two skipped"),
    ("B(A) & (B.h: <5)", [AB, "B(rx) := /${[p = rx]}xx/"], r"[0-4]xx", "rule 4 through a call, one target"),
    ("[c = B(A)] & (c.d: <5)", ["A := /(?<d>\\d)/", "B(rx) := /${rx}-(?<d>\\d)/"], ("refused", "2 labels `d`"),
     "one-path line 4 (`c.d`, the census)"),
    ("B(A) & (B.d: <5)", ["A := /(?<d>\\d)/", "B(rx) := /${rx}-(?<d>\\d)/"], ("refused", "2 labels `d`"),
     "one-path as worded (the line beside `c.d`)"),
    ("[c = B(A)] & (c.d: <5)", ["A := /(?<e>\\d)/", "B(rx) := /${rx}-(?<d>\\d)/"], r"\d-[0-4]",
     "one target: the body's own"),
    ("B(/(?<d>\\d)/) & (B.d: <5)", ["B(rx) := /${rx}-(?<d>\\d)/"], ("refused", "2 labels `d`"),
     "one-path line 4 (`B.d`, the census)"),
    ("W(/(?<h>\\d)/, /;(?<h>\\d)/) & (W.h: \"3\")", ["W(a, b) := [(=) = a] SEQ [(=) = b]"], ("refused", "2 labels `h`"),
     "one-path line 4 (`W.h`, the census)"),
    ("pair(A) & (pair.d: <5)", ["A := /(?<d>\\d)/", "pair(p) := /${[(=) = p]},${[(=) = p]}/"],
     ("refused", "2 labels `d`"), "one-path line 5: the argument placed twice under the start"),
    ("list_of(/(?<h>\\d)/, sep = \",\") & (list_of.h: \"5\")", [], ("refused", "2 labels `h`"),
     "one-path line 5: two spots of the argument"),
    ("[ab = ([b = B] | [a = A])] & (ab.l: <20)", ["A := /(?<l>\\d)\\d/", "B := /(?<l>\\d\\d)/"],
     r"(?:[01]\d|\d\d)", "one-path line 1: one per branch"),
]
if s1127("s2"):
    RULE1127[0] = (RULE1127[0][0], RULE1127[0][1], r"\d-[0-4]", RULE1127[0][3])
TEXTS1127 = {"date": TD, "pair & ": ["3", "a3", "a7", "7", "a", "x3"], "X & ": ["3!", "7!", "x3!", "3"],
             "B(A) & (B.h": ["3xx", "7xx", "x3xx"], "[c = B(A)]": TD, "[ab": ["25", "13", "7", "19", "20", "05"],
             "[n = ([m = P] & ": ["37", "73", "14", "3"], "D2": ["73", "37", "13", "3"]}
r_bad, r_leg = [], 0
for e_, b_, want, why in RULE1127:
    P_, err_ = run11(e_, b_)                                 # noqa: F821
    texts = next((v for k, v in TEXTS1127.items() if e_.startswith(k)), None) or (
        ["7,3;7,7", "7,7;7,3", "1,2;3,4", "7,3;7,3"] if ";" in e_ else T2)
    if isinstance(want, tuple):
        ok_ = P_ is None and want[1] in (err_ or "") and not (err_ or "").startswith("CRASH")
        got = (err_ or "LEGAL")[:150]
    else:
        ok_ = same_as(P_, want, texts)
        r_leg += 1
        got = "legal, %s the hand regex `%s`" % ("equal to" if ok_ else "NOT equal to", want) if P_ else err_
    if not ok_:
        r_bad.append((e_, got))
    print("   %-66s %s | %s" % (e_[:66], why, got[:140]))
check("RULE1127", not r_bad and r_leg >= 12, "%d reads (%d legal against hand regexes); not as the ruling says: %s" % (
    len(RULE1127), r_leg, r_bad or "none"))


def gates_written(expr, binds):
    """the program with every part or call used alone written as a label (`[q__1 = Q]`): the array form through a
    gate under reading (d)'s other side, every setting read, for the engine."""
    ew, bw, _ = prep1127(expr, binds)
    P = Prog1127(ew, bw)                                     # the pattern side stands first, unmoved by the prep
    edits, k = {}, 0
    for n in _subtree(P.root):                               # noqa: F821
        if kind_of(n) in ("alone", "call") and context(n, P.root) == "inside":   # noqa: F821
            k += 1
            edits.setdefault(n.tid, []).append((n.a, n.b, "[%s__%d = %s]" % (n.name.lower(), k, "%s")))
    assert ew[:P.root.b] == expr[:P.root.b]
    return _render(expr, 0, len(expr), sorted(edits.get("P", [])), [], {})   # noqa: F821


unit1127("READINGS1127", "the manager's readings of the two record entries, each RUN: one-path (a)-(c) and the "
         "direct/skip pair; gate-beside-label's three")
rdg = {}
v_wall = walk_v27("[n = ([m = P] SEQ [_x = Q])] & (n.d: <5)", [PB, QB], "n.d")
v_gate = walk_v27("[n = ([a = P] SEQ Q)] & (n.d: <5)", [PB, QB], "n.d")
rdg["(a) visible: a wall hides, a gate holds"] = (v_wall[0] == "legal" and v_wall[1:3] == ("B:P", "d") and
                                                   v_gate[0] == "refused", "%s / %s" % (v_wall[:3], v_gate[1][:80]))
bt = []
for e_, b_, r_ in (("D2 & (D2.c: \"3\")", ["D2 := /(?<c>\\d)(?<c>\\d)/"], "D2.c"),
                   ("[aa = /(?<h>\\d)/] SEQ \",\" SEQ [aa = /(?<h>\\d)/] & (aa.h: <5)", [], "aa.h")):
    P_ = Prog1127(*prep1127(e_, b_)[:2])
    st_ = [n for n in _subtree(P_.root) if _named(n) == r_.split(".")[0] and kind_of(n)]   # noqa: F821
    bw_ = [len(x[1]) for s0 in st_ for x in _between(s0, r_.split(".")[1], P_)]
    bt.append((r_, bw_, walk_v27(e_, b_, r_)))
if s1127("s4"):
    bt[0] = (bt[0][0], [1, 0], bt[0][2])
rdg["(b) D2.c, aa.h skip nothing: label flow"] = (all(set(x[1]) == {0} and x[2][3] == "last mention" for x in bt),
                                                   "; ".join("%s: nodes between each target %s, %s" % (x[0], x[1], x[2][3]
                                                                                                        if x[2][0] == "legal" else x[2][0]) for x in bt))
dirw = {}
for e_, b_, r_ in (("[c = B(A)] & (c.d: <5)", ["A := /(?<d>\\d)/", "B(rx) := /${rx}-(?<d>\\d)/"], "c.d"),
                   ("B(/(?<d>\\d)/) & (B.d: <5)", ["B(rx) := /${rx}-(?<d>\\d)/"], "B.d"),
                   ("date & (date.v: <5)", [DATE], "date.v")):
    dirw[r_] = (walk_v27(e_, b_, r_)[0], walk_v27(e_, b_, r_, {"direct": "wins"}))
READ1127["direct"] = "wins"
Pw_, _ = run11("[c = B(A)] & (c.d: <5)", ["A := /(?<d>\\d)/", "B(rx) := /${rx}-(?<d>\\d)/"])   # noqa: F821
READ1127["direct"] = "error"
rdg["(f) direct beside a skip: printed error; `wins` keeps c.d, B.d legal (the body's own), date.v still an error"] = (
    dirw["c.d"][0] == dirw["B.d"][0] == "refused" and dirw["c.d"][1][1:3] == ("B:B", "d") and dirw["B.d"][1][0] == "legal"
    and dirw["date.v"][1][0] == "refused" and same_as(Pw_, r"\d-[0-4]", TD),
    "; ".join("%s: %s / wins %s" % (k, v[0], v[1][:3]) for k, v in dirw.items()))
g1 = walk_v27("[n = ([a = P] SEQ Q)] & (n.d: <5)", [PB, QB], "n.d")
g2 = walk_v27("/(?<g>${A})x/ & (g.h: <5)", [AB], "g.h")
g3 = walk_v27("[n = ([m = P] SEQ [_x = Q])] & (n.d: <5)", [PB, QB], "n.d")
rdg["gate-beside (1): the error with another legal target beside the gate"] = (
    g1[0] == "refused" and "`n.a.d`" in g1[1] and "`n.Q.d`" in g1[1], g1[1][:120])
rdg["gate-beside (2): `g.h` over /(?<g>${A})x/, the same rule with no other target"] = (
    g2[0] == "refused" and "gate" in g2[1], g2[1][:120])
rdg["gate-beside (3): a private part beside a written label unchanged (skip-past-wall)"] = (
    g3[0] == "legal" and g3[1:3] == ("B:P", "d"), str(g3[:3]))
for k_, (ok_, why_) in rdg.items():
    print("   %s: %s (%s)" % (k_, "SUPPORTED" if ok_ else "NOT SUPPORTED", why_))
check("READINGS1127", all(v[0] for v in rdg.values()), "%d readings run, %d supported" % (
    len(rdg), sum(1 for v in rdg.values() if v[0])))

unit1127("READ_D1127", "reading (d), a QUESTION: the array form through a gate (`some(@n.d, <5)` over `[n = (P SEQ Q)]`), "
         "both readings RUN: `error` (printed, marked) and `exempt` (every setting read, the gated ones too)")
ED = "[n = (P SEQ Q)] & some(@n.d, <5)"
d_err = walk_v27("[n = (P SEQ Q)] & (n.d: <5)", [PB, QB], "n.d", array=True)
d_ex = walk_v27("[n = (P SEQ Q)] & (n.d: <5)", [PB, QB], "n.d", {"array": "error" if s1127("s12") else "exempt"}, array=True)
Pd_err = run11(ED, [PB, QB])                                 # noqa: F821
EDW = gates_written(ED, [PB, QB])
Pd_ex, ed_ex = run11(EDW, [PB, QB])                          # noqa: F821
okd = d_err[0] == "refused" and Pd_err[0] is None and d_ex[0] == "legal" and same_as(Pd_ex, r"(?:[0-4],\d|\d,[0-4])", T2)
print("   error: %s\n   exempt: %s; the engine on `%s`: %s the hand regex `(?:[0-4],\\d|\\d,[0-4])`" % (
    d_err[1][:120], d_ex, EDW, "equal to" if same_as(Pd_ex, r"(?:[0-4],\d|\d,[0-4])", T2) else "NOT equal to"))
if Pd_ex:
    print("   exempt answers: %s" % fmt(Pd_ex, ["7,3", "3,7", "7,7"], "7,7 3,7", "7,3 7,7 1,2"))   # noqa: F821
check("READ_D1127", okd, "error: %s (the program refused: %s); exempt: %s" % (d_err[0], Pd_err[0] is None, d_ex[0]))

unit1127("CENSUS1127", "every dotted read of every printed three-mode program at the starting commit %s: the control's "
         "walker (WALK111) against WALK1127; every read that moves DECLARED (MOVED1127); every read WALK1127 does not "
         "parse given its category and a count of the target's name written as a label in its text" % START1127)
exec(compile(_src11[_src11.index("def sw11(docs):"):_src11.index("def key11(k):")], P1125, "exec"), globals())   # noqa: S102,F821
exec(compile(_src111[_src111.index("_sweep_one11, _modes_of11, _fmt11 = "):_src111.index("OLD111 = {")], P111, "exec"),   # noqa: S102
     globals())
OLD1127 = {f_: _git8("docs/design/predicates/" + f_, START1127) for f_ in DOCF}   # noqa: F821
X1127[0] = False
OLD_T1127 = sw11(OLD1127)                                    # noqa: F821
X1127[0] = True
MOVED1127 = {
    ("date.v", "date & (date.v: <5)"): "one-path line 4 (the census; his example)",
    ("c.d", "[c = B(A)] & (c.d: <5)"): "one-path line 4 (the census)",
    ("B.d", "B(/(?<d>\\d)/) & (B.d: <5)"): "one-path line 4 (the census)",
    ("W.h", "W(/(?<h>\\d)/, /;(?<h>\\d)/) & (W.h: \"3\")"): "one-path line 4 (the census)",
    ("n.d", "[n = ([a = P] SEQ Q)] & (n.d: <5)"): "gate-beside-label: error",
    ("pair.d", "pair(A) & (pair.d: <5)"): "one-path line 5: the argument at two spots under the start (the census "
                                          "counted one)",
    ("list_of.h", "list_of(/(?<h>\\d)/, sep = \",\") & (list_of.h: \"5\")"): "one-path line 5: two spots (the census "
                                                                            "did not parse it)",
}
# `B(A) & (B.d: <5)` of call-prefix (its line wrote "the same A and B": the key carries no bindings, so this census
# cannot run it; RULE1127 runs it with them: refused) moves too; its line is re-spelled with its bindings written.
if s1127("s11"):
    MOVED1127.pop(("pair.d", "pair(A) & (pair.d: <5)"))
CAT1127 = [
    (r"^no start ", "a start the walker does not place (the caller's shorthand `A`, a label the caller writes in an "
                    "argument, a sent label, a list's name): one label of the name under it, by hand"),
    (r"^(call |atom rx\.|name chars)", "a provided name the walker does not parse (a native body, a loop, a "
                                       "list_of default): one label of the name at its spot, by hand"),
    (r"^label \[\(=", "a binding list over a part (`[(=year) = isodate]`): the list takes one label"),
    (r"^label \[/", "an array literal (`days`): one label of the name"),
    (r"^atom C := ", "a binding written in the program (his example 1): A's one `d`"),
    (r"^atom rx\.digits", "a provided pattern in a body: one label of the name"),
    (r"^atom \d", "a provided name with a value argument (`prefix_in(3, ..)`): one label of the name"),
]
cen, moved, unp = {}, [], []
for k_, vs in OLD_T1127.items():
    e_, b_ = k_[0], ["%s := %s" % x_ for x_ in k_[1]]
    for path_, a_, _ in reads_of(e_):                        # noqa: F821
        if len(path_) < 2:
            continue
        arr_ = a_ > 0 and e_[a_ - 1] == "@"
        rd_ = ".".join(path_)
        vo = walk_v27(e_, b_, rd_, old=True)
        vn = walk_v27(e_, b_, rd_, array=arr_)
        ko = vo[3] if vo[0] == "legal" else vo[0]
        kn = vn[3] if vn[0] == "legal" else vn[0]
        if kn == "unparsed":
            Pc_, ec_ = run11(e_, b_)                         # noqa: F821
            X1127[0] = False
            Pk_, ek_ = run11(e_, b_)                         # noqa: F821  the control's whole builder
            X1127[0] = True
            if Pc_ is None and Pk_ is not None:
                kn = "refused (the loaded builder)"
            elif Pc_ is None:
                kn = "refused by both (its bindings are not on the line)"
        cen[(ko, kn)] = cen.get((ko, kn), 0) + 1
        if vn[0] == "refused" and vo[0] != "refused" or kn == "refused (the loaded builder)":
            moved.append((rd_, e_, vs[0][0], vs[0][1]))
        if vn[0] == "unparsed" and kn == "unparsed":
            cat = next((c_ for rx_, c_ in CAT1127 if re.search(rx_, vn[1])), None)
            nm_ = path_[-1]
            txt = e_ + " " + " ".join(b_) + " " + " ".join(LIBMACROS[x_][1] for x_ in LIBMACROS   # noqa: F821
                                                         if re.search(r"(?<![\w.])%s\(" % re.escape(x_), e_))
            nlab = len(re.findall(r"\(\?<:?%s>|\[\s*%s\s*=|\(=\s*%s\b" % ((re.escape(nm_),) * 3), txt))
            unp.append((rd_, e_[:80], vn[1], cat, nlab))
for (ko, kn), n_ in sorted(cen.items()):
    print("   %4d  control %-13s now %s" % (n_, ko, kn))
for x_ in moved:
    print("   MOVED %-10s `%s` (%s:%d): %s" % (x_[0], x_[1], x_[2], x_[3], MOVED1127.get((x_[0], x_[1]), "UNDECLARED")))
for x_ in unp:
    print("   NOT PARSED %-12s `%s` [%s] labels of the name in its text: %d; %s" % (x_[0], x_[1], x_[2], x_[4],
                                                                               x_[3] or "NO CATEGORY"))
m_set = set((x_[0], x_[1]) for x_ in moved)
TWICE1127 = {                                               # the name written twice in the text, judged by hand
    ("ab.l", "atomic([ab = ([b = B] | [a = A])]) & (ab.l: <20)"): "two branches of one `|`: one per match (line 1)",
    ("date.year", "date & (date.year: >= 2000)"): "the list `(=year)` names isodate's one `year`: one label",
    ("A.d", "B(A) & (A.d: <5)"): "the start A placed at two spots: two settings of the start's own name, nothing "
                                  "skipped to two labels (label flow; argument-default's lines \"Both uses\", "
                                  "\"Alone first\")",
}
tw = [x_ for x_ in unp if x_[4] > 1 and (x_[0], x_[1]) not in TWICE1127]
check("CENSUS1127", m_set == set(MOVED1127) and all(x_[3] for x_ in unp) and not tw,
      "%d reads; moved %d (declared %d; undeclared %s; declared, not moved %s); not parsed %d, each categorised: %s; "
      "named twice in its text, unjudged: %s" % (sum(cen.values()), len(moved), len(MOVED1127),
                                                 sorted(m_set - set(MOVED1127)) or "none",
                                                 sorted(set(MOVED1127) - m_set) or "none", len(unp),
                                                 all(x_[3] for x_ in unp), [x_[:2] for x_ in tw] or "none"))

unit1127("TABLE1127", "the label-kind table of core/labels/rule/kinds, read cell by cell, against KINDS111 (the rows "
         "the walker models; WALK1127 reads the same table)")
ROWS111 = {"a written part label": "label", "an underscore part label": "ulabel", "the blank label": "blank",
           "a part used alone": "alone", "a macro call used alone": "call", "a named group of rx text": "group",
           "an underscore group": "ugroup"}

def cell_code(col, c):
    c = c.strip()
    if col == 2 and c.startswith("no, a gate"):
        return "gate"
    if c.startswith("yes"):
        return "yes"
    if c.startswith("no"):
        return "wall" if col in (1, 2, 3) else "no"
    return "?"


D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
if s1127("s13"):
    D8["core.md"] = D8["core.md"].replace("| no, a gate (alone-as-middle, one-path 2) |", "| yes (one-path 2) |", 1)   # noqa: F821
kp = piece8("core/labels/rule/kinds")                        # noqa: F821
tb_bad, tb_seen = [], set()
for L_ in kp.split("\n"):
    L_ = L_.strip()
    if not L_.startswith("| ") or L_.startswith("| the kind") or L_.startswith("|---"):
        continue
    cells = [c.strip() for c in L_.strip("|").split(" | ")]
    name = re.sub(r"\s*\(.*$|\s*`.*$", "", cells[0]).strip()
    k = ROWS111.get(name)
    if k is None:
        continue
    tb_seen.add(k)
    got = tuple(cell_code(i, c) for i, c in enumerate(cells[1:6]))   # noqa: F821
    want = tuple("no" if (i == 0 and w == "no") else w for i, w in enumerate(KINDS111[k]))   # noqa: F821
    if got != want:
        tb_bad.append((name, got, want))
    print("   ROW %-28s document %s, walker %s" % (name, got, want))
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
check("TABLE1127", not tb_bad and tb_seen == set(ROWS111.values()), "%d rows; differing: %s" % (   # noqa: F821
    len(tb_seen), tb_bad or "none"))

unit1127("SWEEP1127", "every printed three-mode line RUN under this model; the starting commit %s's lines under the "
         "control (X1127 off: predfix111's walker) against these, keyed by the program; every key gone DECLARED" % START1127)
NOWS1127 = dict(NOWS)                                        # noqa: F821
if s1127("s5"):
    NOWS["core.md"] = NOWS["core.md"].replace("Across a sequence, the full path: WHOLE `7-3` HOLDS", "Across a sequence, the full path: WHOLE `7-3` FAILS", 1)   # noqa: F821
NEW_T1127 = sw11(NOWS)                                       # noqa: F821
NOWS.update(NOWS1127)                                        # noqa: F821
GONE1127 = {
    "[n = ([a = P] SEQ Q)] & (n.d: <5)": "gate-beside-label: the line is the compile error; `n.a.d` printed with its "
                                         "old answers",
    "date & (date.v: <5)": "one-path line 4: the compile error; `date.m.v` printed with its old answers",
    "[c = B(A)] & (c.d: <5)": "one-path line 4: the compile error; the body's own `d` printed with an argument that "
                              "sets no `d`, its old answers",
    "B(A) & (B.d: <5)": "one-path: the compile error (beside `c.d`); `B.d` printed with an argument that sets no "
                        "`d`, its old answers",
    "pair(A) & (pair.d: <5)": "one-path line 5: the compile error; the caller's label `pair([x = A])` printed with "
                              "its old answers",
    "B(/(?<d>\\d)/) & (B.d: <5)": "one-path line 4: the compile error (two-sources' line \"Through the call, both\")",
    'W(/(?<h>\\d)/, /;(?<h>\\d)/) & (W.h: "3")': "one-path line 4: the compile error; the caller's labels printed "
                                                "with its old answers",
    'list_of(/(?<h>\\d)/, sep = ",") & (list_of.h: "5")': "one-path line 5: the compile error; the caller's label "
                                                          "printed with its old answers",
}
inh = set((k_, f_, st_) for k_, vs in OLD_T1127.items() for f_, _, st_, _, _ in vs if st_ != "same")
sw_bad, sw_moved, sw_gone, sw_new, sw_inh, cnt, used = [], [], [], [], [], {}, set()
for k_, vs in NEW_T1127.items():
    for f_, ln_, st_, got_, pr_ in vs:
        cnt[st_] = cnt.get(st_, 0) + 1
        if st_ != "same":
            (sw_inh if (k_, f_, st_) in inh else sw_bad).append((f_, ln_, st_, k_[0], got_[:160]))
for k_, vs0 in OLD_T1127.items():
    for f0 in sorted(set(v_[0] for v_ in vs0)):
        vs = [v_ for v_ in vs0 if v_[0] == f0]
        nk = [v_ for v_ in NEW_T1127.get(k_, []) if v_[0] == f0]
        if nk:
            po, pn = sorted(set(v_[4] for v_ in vs)), sorted(set(v_[4] for v_ in nk))
            if po != pn:
                sw_moved.append((f0, k_[0], " || ".join(po)[:200], " || ".join(pn)[:200]))
            continue
        if k_[0] in GONE1127:
            used.add(k_[0])
            print("   DROPPED OR MOVED BY A RULING %s:%d `%s`: %s" % (vs[0][0], vs[0][1], k_[0], GONE1127[k_[0]]))
            continue
        sw_gone.append((vs[0][0], vs[0][1], k_[0], vs[0][2]))
stale = sorted(k_ for k_ in GONE1127 if k_ not in used)
for k_, vs in NEW_T1127.items():
    if k_ not in OLD_T1127:
        sw_new.append((vs[0][0], vs[0][1], k_[0], vs[0][3][:150]))
for x_ in sw_new:
    print("   ADDED %s:%d `%s`: %s" % x_)
for x_ in sw_gone:
    print("   GONE %s:%d %r (was %s)" % x_)
for x_ in sw_moved:
    print("   MOVED %s %r\n      old: %s\n      now: %s" % x_)
for x_ in sw_bad:
    print("   BAD %s:%d %s `%s`: %s" % x_)
for x_ in stale:
    print("   STALE DECLARATION %s" % x_)
check("SWEEP1127", OLD_T1127 and not sw_bad and not sw_moved and not sw_gone and not stale,
      "%d printed lines now (%s), %d keys at the starting commit; not same and not inherited %d (inherited %d); "
      "moved %d; gone %d; declared %d; added %d; stale %d" % (
          sum(len(v) for v in NEW_T1127.values()), ", ".join("%s %d" % kv for kv in sorted(cnt.items())),
          len(OLD_T1127), len(sw_bad), len(sw_inh), len(sw_moved), len(sw_gone), len(GONE1127), len(sw_new),
          len(stale)))

unit1127("ERRSWEEP1127", "every printed compile-error line of the base files refused under this model, no crash; each "
         "named form in the refusal's message (MSG111's rows and this lane's MSG1127)")
exec(compile(_src9[_src9.index("def err_lines(docs"):_src9.index("es_now = err_lines(D8)")], P1124, "exec"),   # noqa: S102,F821
     globals())
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
if s1127("s6"):
    D8["library.md"] = D8["library.md"].replace("modes: a compile error (`list_of(/(?<h>\\d)/, sep = \",\") & (list_of.h: \"5\")`",
                                                "modes: a compile error (`list_of([x = /(?<h>\\d)/], sep = \",\") & (x.h: \"5\")`", 1)   # noqa: F821
es_now = [x_ for x_ in err_lines(D8) if not x_[0].endswith("_details.md")]   # noqa: F821
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
exec(compile(_src111[_src111.index("MSG111 = {"):_src111.index("}\n", _src111.index("MSG111 = {")) + 2], P111, "exec"),   # noqa: S102
     globals())
MSG1127 = dict(MSG111)                                       # noqa: F821
MSG1127.update({
    "[n = (P SEQ B(Q))] & (n.d: <5)": "`n.B.d`",
    "date & (date.v: <5)": "`date.m.v`",
    "[n = ([a = P] SEQ Q)] & (n.d: <5)": "`n.a.d`",
    "[n = ([a = P] SEQ [b = Q])] & (n.d: <5)": "`n.b.d`",
    "[n = (P SEQ Q)] & some(@n.d, <5)": "behind a gate",
    "B(/(?<d>\\d)/) & (B.d: <5)": "2 labels `d`",
    "pair(A) & (pair.d: <5)": "2 labels `d`",
    'W(/(?<h>\\d)/, /;(?<h>\\d)/) & (W.h: "3")': "2 labels `h`",
    'list_of(/(?<h>\\d)/, sep = ",") & (list_of.h: "5")': "2 labels `h`",
})
es_bad, es_msg = [], []
for f_, ln_, e_, b_ in es_now:
    Pg, err = run11(e_, b_)                                  # noqa: F821
    if Pg is not None or (err or "").startswith("CRASH"):
        es_bad.append((f_, ln_, e_, "legal" if Pg is not None else err[:100]))
    elif e_ in MSG1127 and MSG1127[e_] not in err:
        es_msg.append((f_, ln_, e_, MSG1127[e_], err[:140]))
for x_ in es_bad:
    print("   BAD (printed a compile error, runs legal or crashes) %s" % (x_,))
for x_ in es_msg:
    print("   MESSAGE %s:%d `%s` lacks %s: %s" % x_)
msg_unseen = sorted(set(MSG1127) - set(e_ for _, _, e_, _ in es_now))
check("ERRSWEEP1127", es_now and not es_bad and not es_msg and not msg_unseen,
      "%d compile-error lines read, each refused with no crash: bad %s; named form missing %s; message rows with no "
      "line %s" % (len(es_now), es_bad or "none", es_msg or "none", msg_unseen or "none"))

unit1127("SPECLINES1127", "every printed line new in this lane (not in its file at the starting commit) is RUN: a "
         "three-mode line SAME as run, a compile-error line refused")
newset = {f_: set(NOWS[f_].split("\n")) - set(OLD1127[f_].split("\n")) for f_ in BASES11}   # noqa: F821
nl3, nle, nl_bad = 0, 0, []
for k_, vs in NEW_T1127.items():
    for f_, ln_, st_, got_, pr_ in vs:
        if f_ in newset and NOWS[f_].split("\n")[ln_ - 1] in newset[f_]:   # noqa: F821
            nl3 += 1
            if st_ != "same":
                nl_bad.append((f_, ln_, st_))
for f_, ln_, e_, b_ in es_now:
    if NOWS[f_].split("\n")[ln_ - 1] in newset[f_]:           # noqa: F821
        nle += 1
        if run11(e_, b_)[0] is not None:                      # noqa: F821
            nl_bad.append((f_, ln_, "legal"))
nl_all = sum(1 for f_ in BASES11 for L_ in newset[f_] if re.search(r"WHOLE `|modes: a compile error", L_))   # noqa: F821
if s1127("s10"):
    nl_all += 1
check("SPECLINES1127", not nl_bad and nl3 + nle == nl_all, "%d new printed lines: three-mode %d, compile-error %d, "
      "unread %d; not as printed: %s" % (nl_all, nl3, nle, nl_all - nl3 - nle, nl_bad or "none"))

unit1127("STALE1127", "the base files, continuation lines joined, hold none of the texts this fold retires")
STALE1127 = [
    (r"a marked reading;\s+owner question gate-twice-scope", "one-path line 5"),
    (r"owner question gate-beside-label", "gate-beside-label"),
    (r"a's `d`, a marked reading", "gate-beside-label"),
    (r"'Unambiguously' is the existing rule", "one-path amends it"),
    (r"`list_of\.h`, the last item", "one-path line 5"),
    (r"list_of\.h = ", "one-path line 5"),
    (r"the caller reads `pair\.d`, the last mention", "one-path line 5"),
    (r"the body's own is `B\.d`", "one-path line 4"),
    (r"A name test and then both hold is one label", "one-path"),
    (r"a name two of them hold is one label by the same rules", "one-path"),
    (r"`B\.d` by rule 4 where unambiguous", "one-path"),
]
if s1127("s7"):
    STALE1127.append((r"Two written labels, a skip", "planted"))
joined = {f_: re.sub(r"\n  +", " ", NOWS[f_]) for f_ in BASES11}   # noqa: F821
st_hits = [(f_, rx_, why) for rx_, why in STALE1127 for f_ in BASES11 if re.search(rx_, joined[f_])]   # noqa: F821
for x_ in st_hits:
    print("   STALE %s `%s` (%s)" % x_)
check("STALE1127", not st_hits, "%d retired texts searched; found %s" % (len(STALE1127), st_hits or "none"))

unit1127("QUOTES1127", "the owner's words this lane quotes, each in the record at the PINNED starting commit and in its "
         "piece; every record title a predfold1127 item cites is a title of that record")
REC1127 = _git8("docs/design/plan_row_bodies/COND-FAMILY.md", START1127)   # noqa: F821
QQ1127 = [
    ("gate-beside-label: error. One may be writing the last line not knowing how Q is defined. So did they know Q had "
     "a d and chose to skip it? Or did they think it did have d and were intending to use it? Skipping labels is about "
     "efficiency in total clarity.", "core/labels/rule/alone-as-middle"),
    ("Skipping labels is about efficiency in total clarity.", "core/labels/rule/one-path"),
    ("one-path: yes all five", "core/labels/rule/one-path"),
    ("a step in a path may be skipped only when exactly one label of that name is visible from the start.",
     "core/labels/rule/one-path"),
    ("It is counted within one match, so a read into an alternation is legal: `pair.x` for `pair := [b = /(?<x>\\d)/] "
     "| [c = /a(?<x>\\d)/]` reads the `x` of the branch taken.", "core/labels/rule/one-path"),
    ("A part used alone is still never skipped, even when it holds the only target.", "core/labels/rule/one-path"),
    ("The array form is exempt, as you just said.", "core/labels/rule/one-path"),
    ("It replaces \"in a sequence the last mention wins\" for skipped reads. Four printed reads become errors that ask "
     "for the full path, for example `date.v` over `[y = /(?<v>\\d)/] SEQ \"-\" SEQ [m = /(?<v>\\d)/]`.",
     "core/labels/rule/one-path"),
    ("A name counts as used once or twice by what lies under the path's start, which answers gate-twice-scope.",
     "core/labels/rule/one-path"),
    ("skipping steps in a path is available when there is exactly one path possible from the start to any end label "
     "visible from that start.", "core/labels/rule/one-path"),
    ("one-path: yes all five", "core/labels/rule/paths"),
]
if s1127("s8"):
    QQ1127.append(("one-path: yes all six", "core/labels/rule/one-path"))
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
q_miss = [(q_[:50], t_) for q_, t_ in QQ1127 if ws(q_) not in ws(REC1127) or ws(q_) not in ws(piece8(t_))]   # noqa: F821
DET1127 = NOWS["core_details.md"] + NOWS["library_details.md"]   # noqa: F821
DOLD1127 = set((OLD1127["core_details.md"] + OLD1127["library_details.md"]).split("\n"))
cited = sorted(set(m_.group(1) for l_ in DET1127.split("\n") if l_ not in DOLD1127     # every line this lane wrote
                   for m_ in re.finditer(r'\(record:\s*"(.+?)"\)(?=[;,.:\s]|$)', l_)))
if s1127("s9"):
    cited.append("2026-11-27 OWNER RULING — one-path: yes all six")
heads = [ws(h_) for h_ in re.findall(r"^#{2,3} (.*)$", REC1127, re.M)]   # noqa: F821
t_miss = [t_[:80] for t_ in cited if not any(h_.rstrip(".") == ws(t_) or h_.startswith(ws(t_) + " (") for h_ in heads)]   # noqa: F821
check("QUOTES1127", not q_miss and not t_miss and cited, "%d quoted sentences (missing: %s); %d record titles cited "
      "(not a title at %s: %s)" % (len(QQ1127), q_miss or "none", len(cited), START1127, t_miss or "none"))

unit1127("MECH1127", "the legal full-path and one-target reads of RULE1127 answered by MECH111 (python `re` on the regex "
         "built mechanically from the program text and its bindings' bodies, the target group named), against the engine")
MECH1127 = [
    ("[n = ([a = P] SEQ [b = Q])] & (n.b.d: <5)", [PB, QB], ("Q", 1, "d"), T2),
    ("[n = ([a = P] SEQ Q)] & (n.a.d: <5)", [PB, QB], ("P", 1, "d"), T2),
    ("[n = ([m = P] SEQ [_x = Q])] & (n.d: <5)", [PB, QB], ("P", 1, "d"), T2),
    ("[n = (P SEQ Q)] SEQ \";\" SEQ [m = (P SEQ Q)] & (n.Q.d: <5)", [PB, QB], ("Q", 1, "d"),
     ["7,3;7,7", "7,7;7,3", "1,2;3,4", "7,3;7,3"]),
    ("X & (X.h: <5)", [AB, "X := [n = [m = A]] SEQ \"!\""], ("A", 1, "h"), ["3!", "7!", "x3!", "3"]),
    ("B(A) & (B.h: <5)", [AB, "B(rx) := /${[p = rx]}xx/"], ("A", 1, "h"), ["3xx", "7xx", "x3xx"]),
]
if s1127("s14"):
    MECH1127[0] = (MECH1127[0][0], MECH1127[0][1], ("P", 1, "d"), MECH1127[0][3])
mc_bad = []
for e_, b_, tgt, texts in MECH1127:
    P_, err_ = run11(e_, b_)                                 # noqa: F821
    try:
        R_ = mech(e_, b_, target=tgt, cond=(0, 4))           # noqa: F821
    except MechError as x_:                                  # noqa: F821
        mc_bad.append((e_, "MECH " + str(x_)))
        continue
    same = P_ is not None and answers(P_, texts) == answers(R_, texts)   # noqa: F821
    print("   %-62s MECH111 %s the engine" % (e_[:62], "equal to" if same else "NOT equal to"))
    if not same:
        mc_bad.append((e_, err_ or "answers differ"))
check("MECH1127", not mc_bad, "%d reads; not equal: %s" % (len(MECH1127), mc_bad or "none"))   # noqa: F821

unit1127("SUCCESSOR1127", "every in-force model re-run: predfix111 in full, and the eighteen its SUCCESSOR111 re-runs "
         "(their outputs dumped through it); each red DECLARED in predfold1127_succ_decl.tsv by predfix90's `red_key10` "
         "key, which carries the red's own FAIL line and no document line numbers; a traceback never")
P90_1127 = os.path.join(LANES1127, "predfix90_evidence", "predfix90_model.py")
_src90_1127 = builtins.open(P90_1127, encoding="utf-8").read()
exec(compile(_src90_1127[_src90_1127.index("CRASH10 = re.compile("):_src90_1127.index("succ_bad, succ_n, succ_t, succ_seen = ")],   # noqa: S102
             P90_1127, "exec"), globals())                   # predfix90's red key, verbatim
DECLF1127 = os.path.join(HERE1127, "predfold1127_succ_decl.tsv")
SD1127 = {}
if os.path.exists(DECLF1127):
    for l_ in builtins.open(DECLF1127, encoding="utf-8").read().split("\n"):
        if l_ and not l_.startswith("#"):
            m_, r_, cls_, why_, key_ = l_.split("\t", 4)
            SD1127.setdefault(m_, {})[r_] = (cls_, key_, why_)
if s1127("s15") and SD1127:
    _m = sorted(SD1127)[0]
    _r = sorted(SD1127[_m])[0]
    SD1127[_m][_r] = (SD1127[_m][_r][0], SD1127[_m][_r][1] + " planted", SD1127[_m][_r][2])
SCR1127 = os.environ.get("PREDFOLD1127_SUCCDIR", "")
RD1127 = os.environ.get("PREDFOLD1127_READDUMP") == "1"
sc_bad, sc_seen, sc_outs = [], [], {}
if not LIGHT1127 or RD1127:
    if not RD1127:
        env = {k: v for k, v in os.environ.items() if not k.startswith(("PREDFIX111_", "PREDFOLD1125_", "PREDFOLD1127_",
                                                                        "PREDFIX90_"))}
        env["PREDFIX111_SUCCDIR"] = SCR1127
        o_ = subprocess.run([sys.executable, "-I", "-B", P111], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, env=env, timeout=5400).stdout
        builtins.open(os.path.join(SCR1127, "predfix111.out"), "w", encoding="utf-8").write(o_)
    for f_ in sorted(os.listdir(SCR1127)):
        if f_.endswith(".out"):
            sc_outs[f_[:-4]] = builtins.open(os.path.join(SCR1127, f_), encoding="utf-8").read()
    for mname, out in sorted(sc_outs.items()):
        lines_ = out.rstrip("\n").split("\n")
        last = lines_[-1]
        mm = re.match(r"%s_model: (\d+) checks, (\d+) failed(?: \(([^)]*)\))?$" % mname, last)
        reds = {}
        if mm and not any(x_.startswith("Traceback") for x_ in lines_):
            for r in [x_.strip() for x_ in (mm.group(3) or "").split(",") if x_.strip()]:
                fl_ = next((l_ for l_ in lines_ if l_.startswith("FAIL %s:" % r) or
                            re.match(r"%s\s+FAIL\b" % re.escape(r), l_)), "")
                reds[r] = red_key10(r, lines_, fl_)          # noqa: F821
        else:
            reds["TRACEBACK"] = ("TRACEBACK", last)
        decl = SD1127.get(mname, {})
        print("   %-13s last line: %s" % (mname, last[:150]))
        for r, (cls_, key_) in sorted(reds.items()):
            sc_seen.append((mname, r, cls_, key_))
            d_ = decl.get(r)
            if cls_ == "TRACEBACK" or d_ is None or d_[1] != key_:
                sc_bad.append((mname, r, "UNDECLARED" if d_ is None else ("KEY CHANGED" if cls_ != "TRACEBACK" else cls_)))
        for r in sorted(set(decl) - set(reds)):
            sc_bad.append((mname, r, "DECLARED, NOW GREEN"))
    WD = os.environ.get("PREDFOLD1127_WRITEDECL", "")
    if WD:
        with builtins.open(WD, "w", encoding="utf-8") as fh:
            fh.write("# model\tred\tclass\twhy\tkey (red_key10: the red's own FAIL line text, no document line numbers)\n")
            for mname, r, cls_, key_ in sc_seen:
                fh.write("%s\t%s\t%s\t%s\t%s\n" % (mname, r, cls_, SD1127.get(mname, {}).get(r, ("", "", "WHY?"))[2], key_))
    for x_ in sc_bad:
        print("   NOT AS DECLARED %s %s: %s" % x_)
    check("SUCCESSOR1127", len(sc_outs) >= 19 and not sc_bad, "%d models read, %d reds, each against its declared "   # noqa: F821
          "key (%d declared): %s" % (len(sc_outs), len(sc_seen), sum(len(v) for v in SD1127.values()),
                                     sc_bad or "all as declared"))
else:
    print("   LIGHT: SUCCESSOR1127 not run")

PLANTS1127 = {"s1": "CANARY1127", "s2": "RULE1127", "s3": "READINGS1127", "s4": "READINGS1127", "s5": "SWEEP1127",
              "s6": "ERRSWEEP1127", "s7": "STALE1127", "s8": "QUOTES1127", "s9": "QUOTES1127", "s10": "SPECLINES1127",
              "s11": "CENSUS1127", "s12": "READ_D1127", "s13": "TABLE1127", "s14": "MECH1127",
              "s15": "SUCCESSOR1127"}
if SAB1127 == "all":
    caught = []
    for q_, tgt in sorted(PLANTS1127.items(), key=lambda kv: int(kv[0][1:])):
        env = dict(os.environ, PREDFOLD1127_SABOTAGE=q_, PREDFOLD1127_LIGHT="1")
        if q_ == "s15":
            env["PREDFOLD1127_READDUMP"] = "1"
        o_ = subprocess.run([sys.executable, "-I", "-B", MY1127], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, env=env, timeout=3000)
        fl = [l_ for l_ in o_.stdout.split("\n") if l_.startswith("FAIL ")]
        ok_ = o_.returncode != 0 and any(l_.startswith("FAIL %s:" % tgt) for l_ in fl) and "Traceback" not in o_.stdout
        caught.append((q_, tgt, ok_))
        print("   PLANT %s -> %s: %s; FAIL lines: %s" % (q_, tgt, "CAUGHT" if ok_ else "NOT CAUGHT",
                                                       [l_[:90] for l_ in fl]))
    check("PLANTS1127", all(c_[2] for c_ in caught), "%d plants, caught %d" % (len(caught), sum(c_[2] for c_ in caught)))   # noqa: F821

failed1127 = [n_ for n_, ok_ in RESULTS if not ok_]         # noqa: F821
print("predfold1127_model: %d checks, %d failed%s" % (len(RESULTS), len(failed1127),   # noqa: F821
                                                     (" (%s)" % ", ".join(failed1127)) if failed1127 else ""))
sys.exit(1 if failed1127 else 0)
