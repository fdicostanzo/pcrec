#!/usr/bin/env python3
"""predfix111_model.py: lane predfix111's evidence, the successor of predfold1125_model.py.

Review r111's fix lane: the findings as the manager ruled them, and the owner's rulings group-node and peek-name
(record docs/design/plan_row_bodies/COND-FAMILY.md, 2026-11-27). DESIGN evidence only: nothing here rules; no check
under `make` reads it.

It LOADS predfold1125's model unchanged up to its first check (`unit11("CANARY", `; the older models load through
it), then puts its own FRONT END FE111 before the loaded program builder, switched by X111[0] (off: the starting
commit's control, predfold1125's builder alone):
  WALK111  a path walker written from the LABEL-KIND TABLE of core/labels/rule (its rows below, KINDS111), not from
           the loaded walker: every read of a parsed program is judged by it; a legal read whose route names a part
           used alone, a macro call used alone or a named group of rx text is RELABELLED before the loaded engine
           answers it (review r111 F24): each such node on the route becomes a written label with a fresh name
           (`[q__1 = Q]`; a group `(?<g>X)` at the top of its literal the part label `[g = /X/]`) and the read the
           full path to the chosen target, so the engine answers the path natively and no rule is patched.
  READINGS the owner questions left open are SWITCHES, every reading RUN: gate-twice-scope (F2: `a` the count over
           the definition, `b` under the read's prefix, printed `b`), gate-beside-label (F3: `i` a compile error,
           `ii` the gated target not counted, `iii` the gate counted, printed `ii`).
  MARKED   the marked readings the documents now print, each a rewrite of the program text: `!` on a lookaround in
           rx text (`!/(?=x)/` is `!^/x/`); `^c` on a condition is c (and `!^c` is `!c`, which `when`'s guard lays);
           a label set only inside `!^A` and read after it a compile error; a capturing group's whole name from an
           unmarked parameter the label-needs-mark error; `.index` of a label inside one alternative its constant.
Every printed line it formats is ALSO answered by MECH111, python `re` on a regex built mechanically from the
program text and its bindings' bodies (the target group named, the condition laid on it), never from the engine.
Its checks are printed by name; the verdict is its last line, `predfix111_model: N checks, F failed`, and it exits
non-zero iff that line reports a failure. `PREDFIX111_LIGHT=1` skips SUCCESSOR111. `PREDFIX111_SABOTAGE=sN`
plants one wrong rule, fact or text per check (PLANTS111); `=all` runs each plant in its own subprocess (LIGHT).
Run: `timeout 3000 python3 -I -B <this dir>/predfix111_model.py`.
"""
import builtins
import os
import re
import subprocess
import sys
import time

MY111 = os.path.abspath(__file__)
HERE111 = os.path.dirname(MY111)
LANES111 = os.path.normpath(os.path.join(HERE111, ".."))
ROOT111 = os.path.normpath(os.path.join(LANES111, "..", "..", ".."))
P1125 = os.path.join(LANES111, "predfold1125_evidence", "predfold1125_model.py")
START111 = "cec257072"                                       # this lane's starting commit (lane/predfix111), PINNED
SAB111 = os.environ.get("PREDFIX111_SABOTAGE", "")
LIGHT111 = os.environ.get("PREDFIX111_LIGHT") == "1"
_src11 = builtins.open(P1125, encoding="utf-8").read()
_a111 = _src11.index('unit11("CANARY", ')
__file__ = P1125
_sav111 = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith(("PREDFOLD1125_", "PREDFIX90_"))}
exec(compile(_src11[:_a111], P1125, "exec"), globals())      # noqa: S102  predfold1125's engines, unchanged
os.environ.update(_sav111)
__file__ = MY111
_P1125 = prog                                                # noqa: F821  the loaded chain's program builder
X111 = [True]
READ111 = {"twice": "b", "beside": "ii"}                    # the printed readings of F2 and F3 (marked)


def s111(q):
    return SAB111 == q


class Unparsed(Exception):
    """A program outside WALK111's grammar: the loaded builder judges it alone."""


# ================================================================== the label-kind table (core/labels/rule)
# One row per kind of label; the columns are the table's: a start inside, a middle step inside, skippable inside,
# crossed from outside (the path enters the binding that holds it), exports. "wall" = a path containing it is
# refused; "gate" = a path may name it but never skip it; each row's ground is in the documents' table.
KINDS111 = {  # kind: (start inside, step inside, skip inside, crossed from outside, exports)
    "label":      ("yes", "yes", "yes", "yes", "yes"),
    "ulabel":     ("yes", "wall", "wall", "wall", "no"),
    "blank":      ("no", "wall", "wall", "wall", "no"),
    "alone":      ("yes", "yes", "gate", "wall", "no"),
    "call":       ("yes", "yes", "gate", "wall", "no"),
    "argalone":   ("no", "no", "yes", "yes", "no"),      # an argument's shorthand label, past the call boundary
    "group":      ("yes", "yes", "yes", "yes", "yes"),
    "ugroup":     ("yes", "wall", "wall", "wall", "no"),
}
if s111("s2"):
    KINDS111["alone"] = ("yes", "yes", "yes", "wall", "no")   # plant: a part used alone skippable


# ================================================================== the parser (a small grammar, spans kept)
NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _skip(s, i):
    """the index past the bracketed, quoted or rx item starting at i (TR11's scanners)."""
    c = s[i]
    if c == "/" and TR11._rx_start(s, i):
        return TR11._rx_end(s, i)
    if c in "\"'":
        return TR11._str_end(s, i)
    if c in "([":
        return TR11._group_end(s, i)
    if c == "{":
        return TR11._brace_end(s, i)
    return i + 1


def split111(s, a, b, sep):
    """[(start, end)] of s[a:b] split at the top-level separator sep ('|', '&' or 'SEQ')."""
    out, i, last = [], a, a
    while i < b:
        c = s[i]
        if c in "/\"'([{" and not (c == "/" and not TR11._rx_start(s, i)):
            i = _skip(s, i)
            continue
        if sep == "SEQ" and s.startswith("SEQ", i) and (i == 0 or not s[i - 1].isalnum()) and \
                (i + 3 >= len(s) or not s[i + 3].isalnum()):
            out.append((last, i))
            last = i + 3
            i += 3
            continue
        if sep != "SEQ" and c == sep:
            out.append((last, i))
            last = i + 1
        i += 1
    out.append((last, b))
    res = []
    for x, y in out:
        while x < y and s[x] == " ":
            x += 1
        while y > x and s[y - 1] == " ":
            y -= 1
        res.append((x, y))
    return res


class N111:
    """a node: kind (alt seq and label use call arg rx grp hole leaf cond), its text id and span, children."""
    __slots__ = ("k", "name", "tid", "a", "b", "kids", "own", "depth", "parent", "use_of")

    def __init__(self, k, tid, a, b, kids=(), name=None):
        self.k, self.tid, self.a, self.b, self.kids, self.name = k, tid, a, b, list(kids), name
        self.own, self.depth, self.parent, self.use_of = True, 0, None, None


class Prog111:
    def __init__(self, expr, binds):
        self.texts = {"P": expr}
        self.defs = {}
        for b in binds:
            m = re.match(r"\s*([A-Za-z_]\w*)(\(([^)]*)\))?\s*:=\s*(.*)$", b, re.S)
            if not m:
                raise Unparsed("binding " + b)
            name, params, body = m.group(1), m.group(3), m.group(4).strip()
            tid = "B:" + name
            self.texts[tid] = body
            self.defs[name] = ([p.strip() for p in params.split(",")] if params is not None else None, tid)
        parts = split111(expr, 0, len(expr), "&")
        self.pattern = []
        self.conds = []
        for x, y in parts:
            t = expr[x:y]
            if t.startswith("(") and TR11._group_end(expr, x) == y and _is_cond(t):
                self.conds.append((x, y))
            else:
                self.pattern.append((x, y))
        if not self.pattern:
            raise Unparsed("no pattern")
        kids = [self.alt("P", x, y, {}, True, 0) for x, y in self.pattern]
        self.root = kids[0] if len(kids) == 1 else N111("and", "P", self.pattern[0][0], self.pattern[-1][1], kids)
        _link(self.root, None)

    def alt(self, tid, a, b, env, own, depth):
        s = self.texts[tid]
        if depth > 12:
            raise Unparsed("depth")
        ps = split111(s, a, b, "|")
        if len(ps) > 1:
            return N111("alt", tid, a, b, [self.andn(tid, x, y, env, own, depth) for x, y in ps])
        return self.andn(tid, a, b, env, own, depth)

    def andn(self, tid, a, b, env, own, depth):
        s = self.texts[tid]
        ps = split111(s, a, b, "&")
        if len(ps) > 1:
            return N111("and", tid, a, b, [self.seq(tid, x, y, env, own, depth) for x, y in ps])
        return self.seq(tid, a, b, env, own, depth)

    def seq(self, tid, a, b, env, own, depth):
        s = self.texts[tid]
        ps = split111(s, a, b, "SEQ")
        if len(ps) > 1:
            return N111("seq", tid, a, b, [self.atom(tid, x, y, env, own, depth) for x, y in ps])
        return self.atom(tid, a, b, env, own, depth)

    def atom(self, tid, a, b, env, own, depth):
        s = self.texts[tid]
        t = s[a:b]
        if not t:
            raise Unparsed("empty")
        if t[0] == "(" and TR11._group_end(s, a) == b:
            if _is_cond(t):
                return N111("cond", tid, a, b)
            return self.alt(tid, a + 1, b - 1, env, own, depth)      # parentheses aside: grouping is no spot
        if t[0] == "[" and TR11._group_end(s, a) == b:
            m = re.match(r"\[\s*(\(=\)|_?[A-Za-z0-9_]*)\s*=\s*", t)
            if not m or m.group(1) == "":
                raise Unparsed("label " + t)
            x = a + m.end()
            n = N111("label", tid, a, b, [self.alt(tid, x, b - 1, env, own, depth)], m.group(1))
            if m.group(1) == "(=)":
                n.k = "list"
            return n
        if t[0] == "/" and TR11._rx_start(s, a) and TR11._rx_end(s, a) == b:
            return self.rx(tid, a + 1, b - 1, env, own, depth)
        if t[0] in "\"'" and TR11._str_end(s, a) == b:
            return N111("leaf", tid, a, b)
        m = NAME.match(t)
        if m and m.end() == len(t):
            nm = t
            if nm in env:
                arg = env[nm]
                return N111("arg", tid, a, b, [arg])
            if nm in self.defs and self.defs[nm][0] is None:
                btid = self.defs[nm][1]
                bs = self.texts[btid]
                u = N111("use", tid, a, b, [self.alt(btid, 0, len(bs), {}, False, depth + 1)], nm)
                return u
            raise Unparsed("name " + nm)
        if m and t[m.end()] == "(" and TR11._group_end(s, a + m.end()) == b:
            nm = m.group(0)
            if nm not in self.defs or self.defs[nm][0] is None:
                raise Unparsed("call " + nm)
            params, btid = self.defs[nm]
            args = [(x, y) for x, y in split_top_commas(s, a + m.end() + 1, b - 1)]
            if len(args) != len(params):
                raise Unparsed("arity " + nm)
            env2 = {}
            for p, (x, y) in zip(params, args):
                if p.endswith(":"):
                    raise Unparsed("label parameter")
                env2[p] = self.alt(tid, x, y, env, own, depth)
            bs = self.texts[btid]
            return N111("call", tid, a, b, [self.alt(btid, 0, len(bs), env2, False, depth + 1)], nm)
        raise Unparsed("atom " + t[:40])

    def rx(self, tid, a, b, env, own, depth):
        """an rx literal's items: named groups (their own rx node inside) and holes; plain text between."""
        s = self.texts[tid]
        n = N111("rx", tid, a, b)
        i, d, stack = a, 0, [n]
        while i < b:
            c = s[i]
            if c == "\\":
                i += 2
                continue
            if c == "[":                                    # a class: skip to its end
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
                j = TR11._brace_end(s, i + 1)
                h = N111("hole", tid, i, j, [self.alt(tid, i + 2, j - 1, env, own, depth)])
                h.depth = d
                stack[-1].kids.append(h)
                i = j
                continue
            if c == "(":
                m = re.match(r"\(\?<(:?)(_?[A-Za-z][A-Za-z0-9_]*)>", s[i:b])
                if m:
                    g = N111("grp", tid, i, None, [], m.group(2))
                    g.depth = d
                    inner = N111("rx", tid, i + m.end(), None)
                    g.kids = [inner]
                    stack[-1].kids.append(g)
                    stack.append(g)
                    stack.append(inner)
                    d = 0
                    i += m.end()
                    continue
                if re.match(r"\(\?<\$\{", s[i:b]) or re.match(r"\(\?<:\$\{", s[i:b]):
                    raise Unparsed("a group-name hole")
                stack.append(None)                          # a plain group
                d += 1
                i += 1
                continue
            if c == "|" and d == 0 and len(stack) <= 2:
                stack[-1].name = "|"                        # a top-level alternation in this literal
            if c == ")":
                top = stack.pop()
                if top is None:
                    d -= 1
                else:
                    top.b = i                               # the inner rx ends here
                    g = stack.pop()
                    g.b = i + 1
                    d = g.depth
                    if i + 1 < b and s[i + 1] in "*+?{":
                        g.depth = 99                        # quantified: not convertible
                i += 1
                continue
            i += 1
        if len(stack) != 1:
            raise Unparsed("rx parentheses")
        return n


def split_top_commas(s, a, b):
    out, i, last = [], a, a
    while i < b:
        c = s[i]
        if c in "/\"'([{" and not (c == "/" and not TR11._rx_start(s, i)):
            i = _skip(s, i)
            continue
        if c == ",":
            out.append((last, i))
            last = i + 1
        i += 1
    out.append((last, b))
    return [(x + len(s[x:y]) - len(s[x:y].lstrip()), y - (len(s[x:y]) - len(s[x:y].rstrip()))) for x, y in out]


def _is_cond(t):
    """a parenthesised text that is a condition: a top-level `:` (an entry)."""
    inner = t[1:-1]
    i = 0
    while i < len(inner):
        c = inner[i]
        if c in "/\"'([{" and not (c == "/" and not TR11._rx_start(inner, i)):
            i = _skip(inner, i)
            continue
        if c == ":" and not inner.startswith(":=", i):
            return True
        i += 1
    return False


def _link(n, parent):
    n.parent = parent
    for k in n.kids:
        _link(k, n)


# ================================================================== WALK111: a read judged by the table
def kind_of(n):
    """the table row of a node, or None for a node that is no label (structure, text)."""
    if n.k == "label":
        return "blank" if n.name == "_" else ("ulabel" if n.name.startswith("_") else "label")
    if n.k == "grp":
        return "ugroup" if n.name.startswith("_") else "group"
    if n.k in ("use", "call"):
        if n.parent is not None and n.parent.k in ("label", "list"):
            return None                                     # a labelled use: the label is the node
        return "alone" if n.k == "use" else "call"
    return None


def context(n, top):
    """'inside' (the text of the reading definition), 'outside' (inside a used binding's or a body's tree) or
    'beyond' (an argument's text reached through a call's body)."""
    ctx, x = "inside", n.parent
    chain = []
    while x is not None:
        chain.append(x)
        x = x.parent
    for x in reversed(chain):                               # from the root down
        if x.k in ("use", "call"):
            ctx = "outside" if ctx == "inside" else ctx
        if x.k == "arg":
            ctx = "beyond"
    return ctx


class Refused(Exception):
    pass


def _named(n):
    return n.name if n.k in ("label", "grp", "use", "call") else None


def _subtree(n):
    yield n
    for k in n.kids:
        yield from _subtree(k)


def walk111(P, path, reading=None):
    """judge the read `path` (a list of names) in the program P: ("legal", route, target, how) or Refused."""
    rd = dict(READ111)
    if reading:
        rd.update(reading)
    nodes = [n for n in _subtree(P.root)]
    s1 = path[0]
    starts = [n for n in nodes if _named(n) == s1 and context(n, P.root) == "inside" and kind_of(n)]
    starts = [n for n in starts if KINDS111[kind_of(n)][0] == "yes"]
    if not starts:
        raise Unparsed("no start " + s1)
    alone_starts = [n for n in starts if kind_of(n) in ("alone", "call")]
    if len(alone_starts) > 1:
        raise Refused("`%s`: %s is used %d times here; label the part (`[left = %s]`) to read one use" % (
            ".".join(path), s1, len(alone_starts), s1))
    routes = [([s0], [], [s0]) for s0 in starts]            # (route of named nodes, gates skipped, full route)
    for i, x in enumerate(path[1:], 1):
        last = i == len(path) - 1
        nxt = []
        for route, gates, full in routes:
            for node, skipped, walls in _reach(route[-1], x, P):
                if walls:
                    continue
                k = kind_of(node)
                ctx = context(node, P.root)
                col = 1 if ctx == "inside" else 3
                if KINDS111[k][col] != "yes" and not (ctx != "inside" and KINDS111[k][3] == "yes"):
                    continue
                if not last and k in ("alone", "call"):
                    scope = P.root if rd["twice"] == "a" else route[-1]
                    same = [n for n in _subtree(scope) if _named(n) == x and kind_of(n) in ("alone", "call")
                            and context(n, P.root) == "inside"]
                    if len(same) > 1:
                        raise Refused("`%s`: `%s` is used more than once here, so it is not a step (a compile "
                                      "error, alone-as-middle)" % (".".join(path), x))
                if last and k not in ("label", "group"):
                    continue
                nxt.append((route + [node], gates + skipped, full + skipped + [node]))
        if not nxt:
            raise Refused(_why(P, routes, x, path))
        routes = nxt
    ungated = [r for r in routes if not r[1]]
    gated = [r for r in routes if r[1]]
    if rd["beside"] == "i" and gated:
        raise Refused(_gate_msg(path, gated))
    pool = ungated if (rd["beside"] == "ii" or not gated) else ungated + gated
    if not ungated:
        raise Refused(_gate_msg(path, gated))
    targets = []
    for r in pool:
        if r[0][-1] not in [t[0][-1] for t in targets]:
            targets.append(r)
    if len(targets) == 1:
        return ("legal", targets[0][2], targets[0][0][-1], "one")
    lca = _lca([t[0][-1] for t in targets])
    if lca.k == "rx" and lca.name == "|":
        raise Unparsed("an alternation inside an rx literal")
    if lca.k in ("seq", "rx"):                              # an rx literal's items are in sequence, text order
        pick = max(targets, key=lambda t: _pos_in(lca, t[0][-1]))
        return ("legal", pick[2], pick[0][-1], "last mention")
    if lca.k == "alt":
        return ("legal", None, None, "branch taken")
    raise Refused("`%s`: both sides of `&` set `%s`, an ambiguous reference (a compile error, core/labels/flow)" % (
        ".".join(path), path[-1]))


def _pos_in(lca, n):
    x = n
    while x.parent is not lca:
        x = x.parent
    return lca.kids.index(x)


def _lca(ns):
    def anc(n):
        out = []
        while n is not None:
            out.append(n)
            n = n.parent
        return out
    a0 = anc(ns[0])
    for x in a0:
        if all(x in anc(n) for n in ns[1:]):
            return x
    return a0[-1]


def _reach(start, x, P):
    """every node named x below start: (node, gates skipped on the way, walls crossed on the way)."""
    out = []

    def go(n, gates, walls):
        for k in n.kids:
            kk = kind_of(k)
            if _named(k) == x and kk:
                out.append((k, list(gates), list(walls)))
            if kk is None:
                go(k, gates, walls)
                continue
            ctx = context(k, P.root)
            if ctx == "beyond" and kk in ("alone", "call"):
                kk = "argalone"
            col = 2 if ctx == "inside" else 3
            cell = KINDS111[kk][col]
            if cell == "yes":
                go(k, gates, walls)
            elif cell == "gate":
                go(k, gates + [k], walls)
            else:
                go(k, gates, walls + [k])
    go(start, [], [])
    return out


def _gate_msg(path, gated):
    ws_ = sorted(set(".".join([path[0]] + [g.name for g in r[1]] + [path[-1]]) for r in gated))
    return ("`%s`: the path skips a part used alone, which is never skipped inside its binding: write %s (a compile "
            "error, alone-as-middle)" % (".".join(path), " or ".join("`%s`" % w for w in ws_)))


def _why(P, routes, x, path):
    for route, _, _ in routes:
        for node, sk, walls in _reach(route[-1], x, P):
            if not walls and kind_of(node) in ("alone", "call") and context(node, P.root) != "inside":
                walls = [node]
            if walls:
                w = walls[0]
                k = kind_of(w)
                if k in ("alone", "call"):
                    return ("`%s`: the path crosses `%s`, a part used alone in it (a compile error, path-rules rule 6)"
                            % (".".join(path), w.name))
                return ("`%s`: the path crosses the underscore %s `%s`, not the start (a compile error, path-rules "
                        "rule 2%s)" % (".".join(path), "group" if w.k == "grp" else "label", w.name,
                                       "; group-node" if w.k == "grp" else ""))
    return "`%s`: `%s` is not visible through `%s` (a compile error, core/labels/paths)" % (
        ".".join(path), ".".join(path[1:]), path[0])


# ================================================================== RELABEL: the route written out for the engine
def relabel(P, route, path):
    """the program text and bindings with every part used alone, call and group on the route written as a label,
    and the full read; (expr, binds, read)."""
    texts = dict(P.texts)
    wrap, conv = {}, {}
    names = []
    k = 0
    for j, n in enumerate(route):
        kk = kind_of(n)
        if j == len(route) - 1 or (j == 0 and kk in ("alone", "call", "label", "ulabel")):
            names.append(n.name)                            # the target, and a start the engine reads natively
        elif kk in ("alone", "call"):
            k += 1
            nm = "%s__%d" % (n.name.lower(), k)
            wrap[id(n)] = (n, nm)
            names.append(nm)
        elif kk in ("group", "ugroup"):
            if n.depth != 0:
                raise Unparsed("a group not at the top of its literal")
            conv[id(n)] = n
            names.append(n.name)
        else:
            names.append(n.name)
    edits = {}
    for n, nm in wrap.values():
        edits.setdefault(n.tid, []).append((n.a, n.b, "[%s = %s]" % (nm, "%s")))
    rxs = {}
    for g in conv.values():
        lit = g.parent
        while lit.parent is not None and lit.parent.k == "grp":
            lit = lit.parent.parent                         # the outermost literal holding it
        rxs[id(lit)] = lit
    out = {}
    for tid, s in texts.items():
        es = sorted(edits.get(tid, []), key=lambda e: e[0])
        lits = sorted([l_ for l_ in rxs.values() if l_.tid == tid], key=lambda l_: l_.a)
        out[tid] = _render(s, 0, len(s), es, lits, conv)
    expr = out["P"]
    binds = []
    for nm, (params, tid) in P.defs.items():
        binds.append("%s%s := %s" % (nm, "" if params is None else "(%s)" % ", ".join(params), out[tid]))
    return expr, binds, ".".join(names)


def _render(s, a, b, edits, lits, conv):
    res, i = [], a
    items = [(e[0], e[1], "edit", e) for e in edits if a <= e[0] and e[1] <= b] + \
            [(l_.a - 1, l_.b + 1, "lit", l_) for l_ in lits if a <= l_.a - 1 and l_.b + 1 <= b]
    items.sort(key=lambda t: (t[0], -t[1]))
    for x, y, kind, obj in items:
        if x < i:
            continue                                        # nested inside an item already rendered
        res.append(s[i:x])
        inner_e = [e for e in edits if x <= e[0] and e[1] <= y and e is not obj]
        if kind == "edit":
            res.append(obj[2] % _render(s, x, y, inner_e, [l_ for l_ in lits if x < l_.a and l_.b < y], conv))
        else:
            res.append(_render_lit(s, obj, inner_e, conv))
        i = y
    res.append(s[i:b])
    return "".join(res)


def _render_lit(s, lit, edits, conv):
    """an rx literal whose top-level groups in conv become part labels, the literal split into a sequence."""
    parts, i = [], lit.a
    for g in [k for k in lit.kids if k.k == "grp" and id(k) in conv]:
        if g.a > i:
            parts.append("/%s/" % _render(s, i, g.a, edits, [], conv))
        inner = g.kids[0]
        hs = [k for k in inner.kids if k.k == "hole"]
        if len(hs) == 1 and hs[0].a == inner.a and hs[0].b == inner.b:
            body = _render(s, hs[0].a + 2, hs[0].b - 1, edits, [], conv)
        elif any(k.k == "grp" and id(k) in conv for k in inner.kids):
            body = "(%s)" % _render_lit(s, inner, edits, conv)
        else:
            body = "/%s/" % _render(s, inner.a, inner.b, edits, [], conv)
        parts.append("[%s = %s]" % (g.name, body))
        i = g.b
    if i < lit.b:
        parts.append("/%s/" % _render(s, i, lit.b, edits, [], conv))
    return "(" + " SEQ ".join(parts) + ")" if len(parts) > 1 else parts[0]


# ================================================================== FE111: the marked readings, as text rewrites
COND_AT = re.compile(r"(!?)\^\(")
LOOK_RX = re.compile(r"!/\(\?(=|!|<=|<!)(.*)\)/")


def _lookaround_not(e):
    """`!/(?=x)/` is `!^/x/` and `!/(?!x)/` is `^/x/`; `!/(?<=x)/` is `/(?<!x)/` (a MARKED reading: line 1, a
    lookaround is a test)."""
    out, i = [], 0
    while i < len(e):
        if e[i] == "!" and e.startswith("/(?", i + 1) and TR11._rx_start(e, i + 1):
            j = TR11._rx_end(e, i + 1)
            lit = e[i + 1:j]
            m = LOOK_RX.match("!" + lit)
            if m and TR11._group_end(lit, 1) == len(lit) - 1:
                op, x = m.group(1), m.group(2)
                out.append({"=": "!^/%s/" % x, "!": "^/%s/" % x, "<=": "/(?<!%s)/" % x, "<!": "/(?<=%s)/" % x}[op])
                i = j
                continue
        out.append(e[i])
        i += 1
    return "".join(out)


def _caret_cond(e):
    """`^c` on a condition is c, `!^c` is `!c` (a MARKED reading: a condition is zero width already)."""
    out, i = [], 0
    while i < len(e):
        m = COND_AT.match(e, i)
        if m and not (i > 0 and e[i - 1] == "\\"):
            a = m.end() - 1
            b = TR11._group_end(e, a)
            if _is_cond(e[a:b]):
                out.append(("!" if m.group(1) else "") + e[a:b])
                i = b
                continue
        if e[i] == "/" and TR11._rx_start(e, i):
            j = TR11._rx_end(e, i)
            out.append(e[i:j])
            i = j
            continue
        out.append(e[i])
        i += 1
    return "".join(out)


def _when_cond(e):
    """a `when` whose test is a condition, laid out by its ruled body read from library.md (WHEN11), the list
    label on a condition dropped (a condition sets no label); `^c`/`!^c` then read by _caret_cond."""
    m = re.match(r"when\((.*)\) := (.*)$", WHEN11)
    params = [p.strip() for p in m.group(1).split(",")]
    body = m.group(2)
    out, i = [], 0
    while True:
        j = e.find("when(", i)
        if j < 0 or (j > 0 and (e[j - 1].isalnum() or e[j - 1] == "_")):
            out.append(e[i:])
            break
        k = TR11._group_end(e, j + 4)
        args = [e[x:y] for x, y in split_top_commas(e, j + 5, k - 1)]
        if not args or not (args[0].startswith("(") and _is_cond(args[0])):
            out.append(e[i:k])
            i = k
            continue
        vals = {}
        for p, a in zip(params, args):
            vals[p.split("=")[0].strip()] = a
        for p in params:
            if "=" in p and p.split("=")[0].strip() not in vals:
                vals[p.split("=")[0].strip()] = p.split("=", 1)[1].strip()
        b2 = body
        for nm, v in vals.items():
            b2 = re.sub(r"\[\(=\) = %s\]" % nm, lambda _m, v=v, nm=nm: "(%s)" % v if nm != "test" else v, b2)
            b2 = re.sub(r"(?<![\w$])%s(?!\w)" % nm, lambda _m, v=v: v, b2)
        t = vals["test"]
        mm = re.match(r"\((\s*[\w.]+\s*:\s*)(<=|>=|<|>)(.*)\)$", t)
        if mm:                                              # the engine lays a condition in a group as `!` of
            inv = {"<": ">=", ">=": "<", ">": "<=", "<=": ">"}[mm.group(2)]   # its complement (c is !!c)
            b2 = b2.replace("(" + t + " SEQ", "(!(%s%s%s) SEQ" % (mm.group(1), inv, mm.group(3)), 1)
        out.append(e[i:j] + "(" + b2 + ")")
        i = k
    return "".join(out)


def _bang_ahead_labels(e, reads):
    """a label set only inside a `!^A` operand and read after it: a compile error (a MARKED reading)."""
    i = 0
    while True:
        j = e.find("!^", i)
        if j < 0:
            return
        a = j + 2
        if a < len(e) and e[a] == "/" and TR11._rx_start(e, a):
            b = TR11._rx_end(e, a)
        elif a < len(e) and e[a] in "([":
            b = TR11._group_end(e, a)
        else:
            i = a
            continue
        inner = set(re.findall(r"\(\?<:?([A-Za-z]\w*)>|\[\s*([A-Za-z]\w*)\s*=", e[a:b]))
        inner = set(x or y for x, y in inner)
        rest = e[:j] + e[b:]
        outside = set(x or y for x, y in re.findall(r"\(\?<:?([A-Za-z]\w*)>|\[\s*([A-Za-z]\w*)\s*=", rest))
        for r in reads:
            if r[0] in inner and r[0] not in outside:
                raise CompileError("`%s` is set only inside `!^`, never visible after it (a compile error, "   # noqa: F821
                                   "core/labels/paths; a marked reading)" % r[0])
        i = b


def _name_hole_mark(e, binds):
    """label-needs-mark on a capturing group's whole name (a MARKED reading); `n:` there read in the engine's
    spelling (the head unmarked, `_:` the engine's `_`)."""
    b2, marked = [], []
    for b in binds:
        m = re.match(r"\s*([A-Za-z_]\w*)\(([^)]*)\)\s*:=\s*(.*)$", b, re.S)
        if not m:
            b2.append(b)
            continue
        ps = [p.strip() for p in m.group(2).split(",")]
        body = m.group(3)
        for p in ps:
            pn = p.rstrip(":")
            if re.search(r"\(\?<\$\{%s\}>" % re.escape(pn), body):
                if not p.endswith(":"):
                    raise CompileError("at the binding `%s`: the body places the parameter `%s` as a group's "   # noqa: F821
                                       "whole name, a label; a label parameter is marked `%s:` in the head "
                                       "(label-needs-mark; a marked reading)" % (b, pn, pn))
                if re.search(r"\(\?<:?\$\{%s\}" % re.escape(pn), body.replace("(?<${%s}>" % pn, "")) is None:
                    marked.append((m.group(1), ps.index(p)))
                    ps = [x.rstrip(":") if x == p else x for x in ps]
        b2.append("%s(%s) := %s" % (m.group(1), ", ".join(ps), body))
    for nm, k in marked:
        src_b = [b for b in b2 if re.match(r"\s*%s\(" % nm, b)][0]
        mm0 = re.match(r"\s*(\w+)\(([^)]*)\)\s*:=\s*(.*)$", src_b, re.S)
        ps0 = [x.strip() for x in mm0.group(2).split(",")]
        rest = [x for i, x in enumerate(ps0) if i != k]
        var = "%s__blank%d" % (nm, k)
        vbody = mm0.group(3).replace("(?<${%s}>" % ps0[k], "(")
        b2.append("%s%s := %s" % (var, "(%s)" % ", ".join(rest) if rest else "", vbody))

        def blank(mm, var=var, k=k):
            args = [mm.group(2)[x:y] for x, y in split_top_commas(mm.group(2), 0, len(mm.group(2)))]
            if k < len(args) and args[k].strip() == "_:":
                del args[k]
                return var + ("(%s)" % ", ".join(args) if args else "")
            return mm.group(0)
        e = re.sub(r"\b(%s)\(([^()]*)\)" % nm, blank, e)

        def fix(mm):
            args = [mm.group(2)[x:y] for x, y in split_top_commas(mm.group(2), 0, len(mm.group(2)))]
            if k < len(args) and args[k].strip() == "_:":
                args[k] = "_"
            return "%s(%s)" % (mm.group(1), ", ".join(args))
        e = re.sub(r"\b(%s)\(([^()]*)\)" % nm, fix, e)
    return e, b2


def _alts_of(body):
    """the alternatives of a binding's body (a map literal's elements, or the top-level `|`), as texts."""
    els = TR11.map_of(body)
    if els is not None:
        return [("[%s = %s]" % (k, v)) for k, v in els]
    return [body[x:y] for x, y in split111(body, 0, len(body), "|")]


def _index_const(e, binds):
    """`(X.l.index: S)` for a label written inside ONE alternative of X: its constant position (map-creator line
    7, "a constant for a label inside one alternative"), laid as l being set where the constant is in S."""
    bd = {b.split(":=")[0].strip(): b.split(":=", 1)[1].strip() for b in binds if ":=" in b}

    def rep(m):
        x, l_, s_ = m.group(1), m.group(2), m.group(3).strip()
        if x not in bd:
            return m.group(0)
        alts = _alts_of(bd[x])
        ks = [i + 1 for i, a in enumerate(alts) if re.search(r"\[\s*%s\s*=|\(\?<:?%s>" % (l_, l_), a)]
        if len(ks) != 1 or len(alts) < 2:                    # inside ONE of two or more alternatives
            return m.group(0)
        mm = re.match(r"(==|<=|>=|<|>)?\s*(\d+)$", s_)
        if not mm:
            return m.group(0)
        op, v = mm.group(1) or "==", int(mm.group(2))
        ok = {"==": ks[0] == v, "<": ks[0] < v, "<=": ks[0] <= v, ">": ks[0] > v, ">=": ks[0] >= v}[op]
        return "(%s.%s: %s)" % (x, l_, "/[\\s\\S]+/" if ok else "/\\b\\B/")
    return re.sub(r"\((\w+)\.(\w+)\.index:\s*([^()]*)\)", rep, e)


READ_RX = re.compile(r"\(\s*([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*\??:(?!=)")
WALKLOG111 = []                                             # (program, read, verdict) of every read WALK111 judged


def reads_of(e):
    """the label paths the conditions of e read: `(a.b.c: S)`, and `@a.b.c` in a group question."""
    out = []
    for m in READ_RX.finditer(e):
        out.append((m.group(1).split("."), m.start(1), m.end(1)))
    for m in re.finditer(r"@([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)", e):
        out.append((m.group(1).split("."), m.start(1), m.end(1)))
    return out


def fe111(expr, binds):
    """the marked readings, then WALK111 on every read; the program the loaded builder then runs."""
    e = _lookaround_not(expr)
    e = re.sub(r"\[(\s*_?\w+\s*=\s*)\(\s*([A-Za-z_]\w*)\s*\)\]", r"[\1\2]", e)   # parentheses aside (F7)
    if "when(" in e:
        e = _when_cond(e)
    e = _caret_cond(e)
    e, binds = _name_hole_mark(e, list(binds))
    e = _index_const(e, binds)
    reads = reads_of(e)
    _bang_ahead_labels(e, [r[0] for r in reads])
    todo = [r for r in reads if len(r[0]) >= 2]
    if not todo:
        return e, binds
    try:
        P = Prog111(e, binds)
    except Unparsed:
        return e, binds
    relabels = []
    for path, a, b in todo:
        try:
            r = walk111(P, path)
        except Unparsed:
            continue
        except Refused as x:
            WALKLOG111.append((expr, ".".join(path), "refused"))
            raise CompileError(str(x))                      # noqa: F821
        WALKLOG111.append((expr, ".".join(path), "legal"))
        if r[1] and any(kind_of(n) in ("alone", "call", "group", "ugroup") for n in r[1][1:-1] + r[1][:1]
                        if not (n is r[1][0] and kind_of(n) in ("alone", "call"))):
            relabels.append((path, a, b, r[1]))
    if not relabels:
        return e, binds
    if len(relabels) > 1:
        return e, binds
    path, a, b, route = relabels[0]
    e2, b2, rd = relabel(P, route, path)
    # the read moved with the relabel: find it again in the rendered text by its old spelling
    old = ".".join(path)
    if e2.count("(" + old + ":") + e2.count("(" + old + " :") + e2.count("@" + old) != 1:
        return e, binds
    e2 = e2.replace("(" + old + ":", "(" + rd + ":").replace("(" + old + " :", "(" + rd + " :").replace("@" + old, "@" + rd)
    return e2, b2


def prog(expr, binds=(), **opts):                            # noqa: F811
    """The documents as now ruled: FE111, then predfold1125's builder. X111 off: predfold1125's builder alone."""
    if not X111[0]:
        return _P1125(expr, list(binds), **opts)
    e2, b2 = fe111(expr, list(binds))
    return _P1125(e2, b2, **opts)


# ================================================================== MECH111: python `re`, built from the text
class MechError(Exception):
    pass


class RePg:
    """a python regex with the program's interface: whole, search, findall; `need` a group that must be set."""
    def __init__(self, rx, need=None):
        self.c = re.compile(rx)
        self.need = need

    def _ok(self, m):
        return m is not None and (self.need is None or m.group(self.need) is not None)

    def whole(self, t):
        return self._ok(self.c.fullmatch(t))

    def search(self, t, frm=0):
        for i in range(frm, len(t) + 1):
            m = self.c.match(t, i)
            if self._ok(m):
                return (m.start(), m.end())
        return None

    def findall(self, t):
        out, i, last_empty = [], 0, None
        while i <= len(t):
            m = self.c.match(t, i)
            if self._ok(m) and not (m.end() == m.start() == last_empty):
                out.append((m.group(0), m.start()))
                if m.end() == m.start():
                    last_empty = m.start()
                    i += 1
                else:
                    i = m.end()
                continue
            i += 1
        return out


def mech(expr, binds, target=None, need=None, cond=None):
    """the regex of a program, built from its text: target = (binding, use number, group) names one group T (the
    read's target), every other group unnamed; cond = (low, high) its digit range; need = a label that must be set."""
    bd, dflt = {}, {}
    for b in list(binds) + [WHEN11]:                        # the library's `when`, its ruled body READ
        m = re.match(r"\s*([A-Za-z_]\w*)(\(([^)]*)\))?\s*:=\s*(.*)$", b, re.S)
        if m.group(1) in bd:
            continue
        ps = None
        if m.group(3) is not None:
            ps = []
            for p in m.group(3).split(","):
                nm_, _, dv = p.partition("=")
                ps.append(nm_.strip().rstrip(":"))
                if dv:
                    dflt[(m.group(1), nm_.strip())] = dv.strip()
        bd[m.group(1)] = (ps, m.group(4).strip())
    count = {}
    st = {"T": target, "cond": cond, "need": need}

    def low(s, env, owner):
        s = s.strip()
        ps = split111(s, 0, len(s), "|")
        if len(ps) > 1:
            return "(?:%s)" % "|".join(low(s[x:y], env, owner) for x, y in ps)
        ps = split111(s, 0, len(s), "&")
        if len(ps) > 1:
            raise MechError("& inside")
        ps = split111(s, 0, len(s), "SEQ")
        if len(ps) > 1:
            return "".join(low(s[x:y], env, owner) for x, y in ps)
        return atom(s, env, owner)

    def atom(s, env, owner):
        if s.startswith("!^"):
            return "(?!%s)" % atom(s[2:], env, owner)
        if s.startswith("^"):
            return "(?=%s)" % atom(s[1:], env, owner)
        if s.startswith("!/") and TR11._rx_start(s, 1) and TR11._rx_end(s, 1) == len(s):
            return "(?!%s)" % atom(s[1:], env, owner)
        if s.startswith("!(") and TR11._group_end(s, 1) == len(s) and _is_cond(s[1:]):
            return cond_rx(s[1:], neg=True)
        if s[0] == "(" and TR11._group_end(s, 0) == len(s):
            if _is_cond(s):
                return cond_rx(s)
            return "(?:%s)" % low(s[1:-1], env, owner)
        if s[0] == "[" and TR11._group_end(s, 0) == len(s):
            m = re.match(r"\[\s*(\(=\)|_?\w*)\s*=\s*(.*)\]$", s, re.S)
            if st["need"] and m.group(1) == st["need"] and not st.get("nd"):
                st["nd"] = True
                return "(?P<N>%s)" % low(m.group(2), env, owner)
            return "(?:%s)" % low(m.group(2), env, owner)
        if s[0] == "/" and TR11._rx_end(s, 0) == len(s):
            return rx(s[1:-1], env, owner)
        if s[0] in "\"'":
            return re.escape(TR11._unstring(s))
        m = re.match(r"([A-Za-z_]\w*)(?:\[(.*)\]|\.([A-Za-z_]\w*))?$", s, re.S)
        if m and (m.group(2) or m.group(3)) and m.group(1) in bd:
            els = TR11.map_of(bd[m.group(1)][1])
            if m.group(3):
                return "(?:%s)" % low(dict(els)[m.group(3)], {}, m.group(1))
            keys = [k.strip() for k in m.group(2).split("|")]
            out = []
            for k in keys:
                if k.isdigit():
                    out.append(els[int(k) - 1][1])
                else:
                    out.append(dict(els).get(TR11._unstring(k)))
            out = [o for o in out if o is not None]
            return "(?:%s)" % "|".join(low(o, {}, m.group(1)) for o in out) if out else r"(?!)"
        if m and m.end() == len(s) and not (m.group(2) or m.group(3)):
            nm = m.group(1)
            if nm in env:
                return "(?:%s)" % env[nm]
            if nm in bd and bd[nm][0] is None:
                count[nm] = count.get(nm, 0) + 1
                body = bd[nm][1]
                els = TR11.map_of(body)
                if els is not None:
                    return "(?:%s)" % "|".join(low(v, {}, nm) for _, v in els)
                return "(?:%s)" % low(body, {}, (nm, count[nm]))
            raise MechError("name " + nm)
        m = re.match(r"([A-Za-z_]\w*)\((.*)\)$", s, re.S)
        if m and m.group(1) in bd and bd[m.group(1)][0] is not None:
            ps, body = bd[m.group(1)]
            args = [m.group(2)[x:y] for x, y in split_top_commas(m.group(2), 0, len(m.group(2)))]
            args += [dflt[(m.group(1), p)] for p in ps[len(args):]]
            env2 = {p: low(a, env, owner) if not a.strip().endswith(":") and a.strip() != "_" else None
                    for p, a in zip(ps, args)}
            body2 = body
            for p, a in zip(ps, args):
                if a.strip() in ("_", "_:"):
                    body2 = body2.replace("(?<${%s}>" % p, "(")
            count[m.group(1)] = count.get(m.group(1), 0) + 1
            return "(?:%s)" % low(body2, env2, (m.group(1), count[m.group(1)]))
        raise MechError("atom " + s[:40])

    def rx(t, env, owner):
        out, i = [], 0
        while i < len(t):
            if t.startswith("${", i):
                j = TR11._brace_end(t, i + 1)
                out.append("(?:%s)" % low(t[i + 2:j - 1], env, owner))
                i = j
                continue
            if t[i] == "\\":
                out.append(t[i:i + 2])
                i += 2
                continue
            m = re.match(r"\(\?<:?(_?[A-Za-z]\w*)>", t[i:])
            if m:
                g = m.group(1)
                if st["T"] and (owner if isinstance(owner, tuple) else (owner, 1)) == st["T"][:2] and g == st["T"][2] \
                        and not st.get("done"):
                    st["done"] = True
                    out.append("(?P<T>")
                    lo, hi = st["cond"] or (None, None)
                    k = t.find(")", i + m.end())
                    if lo is not None and t[i + m.end():k] == "\\d":
                        out.append("[%d-%d]" % (lo, hi))
                        i = k
                        continue
                else:
                    out.append("(?P<N>" if st["need"] == g and not st.get("nd") else "(?:")
                    if st["need"] == g:
                        st["nd"] = True
                i += m.end()
                continue
            if t.startswith("(?<", i) and not t.startswith(("(?<=", "(?<!"), i):
                raise MechError("group " + t[i:i + 10])
            out.append(t[i])
            i += 1
        return "".join(out)

    def cond_rx(c, neg=False):
        m = re.match(r"\(\s*(\w+)\s*:\s*(<|>=)\s*(\d)\s*\)$", c)
        if not m:
            raise MechError("condition " + c)
        lo, hi = (0, int(m.group(3)) - 1) if m.group(2) == "<" else (int(m.group(3)), 9)
        cls = "[%d-%d]" % (lo, hi)
        return "(?<!%s)" % cls if neg else "(?<=%s)" % cls      # the label is the digit just before (a limit)

    parts = split111(expr, 0, len(expr), "&")
    pat = [expr[x:y] for x, y in parts if not (expr[x:y].startswith("(") and _is_cond(expr[x:y]))]
    if len(pat) != 1:
        raise MechError("& in the program")
    r = low(pat[0], {}, "P")
    if target and not st.get("done"):
        raise MechError("target not found")
    return RePg(r, "T" if target else ("N" if need else None))


# ================================================================== CHECKS
# ==== CHECKS (a probe loads the model up to this line)
RESULTS.clear()                                              # noqa: F821  predfold1125's counters, this model's own


def unit111(name, what):
    print("== %s: %s" % (name, what))


def answers(P, texts):
    return ans11(P, texts)                                   # noqa: F821


def walk_v(expr, binds, read, reading=None):
    """WALK111's verdict on one read: ('legal', target binding/text id, target name, how) or ('refused', message)."""
    try:
        P = Prog111(expr, binds)
        r = walk111(P, read.split("."), reading)
    except Refused as e:
        return ("refused", str(e))
    except Unparsed as e:
        return ("unparsed", str(e))
    if r[2] is None:
        return ("legal", None, None, r[3])
    return ("legal", r[2].tid, r[2].name, r[3])


PB = "P := /(?<d>\\d)/"
QB = "Q := /,(?<d>\\d)/"
BB = "B(rx) := /${[p = rx]}xx/"
AB = "A := /(?<h>\\d)/"
T2 = ["7,3", "3,7", "1,2", "7,3x", "x3,1", "3,3", "7,7"]
TXX = ["7,3xx", "3,7xx", "1,2xx", "7,3x"]
TG = ["3x", "7x", "4x", "x3x", "3", "37x"]

unit111("CANARY111", "X111 off is predfold1125's builder (the control): it refuses the group step and answers the "
        "alone read of two uses by rewriting; X111 on answers both by the walker")
X111[0] = False
c0 = run11("/(?<g>(?<d>\\d))x/ & (g.d: <5)")                 # noqa: F821
c1 = run11("[n = (P SEQ Q)] SEQ \";\" SEQ [m = (P SEQ Q)] & (n.Q.d: <5)", [PB, QB])   # noqa: F821
X111[0] = True
c2 = run11("/(?<g>(?<d>\\d))x/ & (g.d: <5)")                 # noqa: F821
c3 = run11("[n = (P SEQ Q)] SEQ \";\" SEQ [m = (P SEQ Q)] & (n.Q.d: <5)", [PB, QB])   # noqa: F821
if s111("s1"):
    c2 = c0
check("CANARY111", c0[0] is None and c1[0] is None and c2[0] is not None and c3[0] is not None,   # noqa: F821
      "off: %s / %s; on: %s / %s" % (c0[1], c1[1], "legal" if c2[0] else c2[1], "legal" if c3[0] else c3[1]))

unit111("TABLE111", "the label-kind table of core/labels/rule/kinds, read cell by cell, against WALK111's KINDS111 "
        "(the rows it models)")
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
        print("   ROW not modelled by WALK111: %s" % cells[0])
        continue
    tb_seen.add(k)
    got = tuple(cell_code(i, c) for i, c in enumerate(cells[1:6]))
    want = KINDS111[k]
    want = tuple("no" if (i == 0 and w == "no") else w for i, w in enumerate(want))
    if s111("s2") and k == "alone":
        pass                                                 # the plant moved KINDS111, not the document
    if got != want:
        tb_bad.append((name, got, want))
    print("   ROW %-28s document %s, walker %s" % (name, got, want))
check("TABLE111", not tb_bad and tb_seen == set(ROWS111.values()), "%d rows modelled; differing: %s; missing: %s" % (
    len(tb_seen), tb_bad or "none", sorted(set(ROWS111.values()) - tb_seen) or "none"))

unit111("GRID111", "reads judged by WALK111 against hand-filled verdicts, each citing its ground; every legal read's "
        "answers against MECH111 (python `re` on the regex built from the program text, the target group named)")
# (program, bindings, read, expected verdict, expected target (binding, use, group) or None, ground)
GRID111 = [
    ("[n = (P SEQ Q)] & (n.Q.d: <5)", [PB, QB], "n.Q.d", "legal", ("Q", 1, "d"), "alone-as-middle: a middle step"),
    ("[n = (P SEQ Q)] & (n.d: <5)", [PB, QB], "n.d", "refused", None, "alone-as-middle: never skipped"),
    ("[n = (P SEQ Q)] & (Q.d: <5)", [PB, QB], "Q.d", "legal", ("Q", 1, "d"), "path-rules rule 6: a start inside"),
    ("[n = (P SEQ Q)] & (n.P.d: <5)", [PB, QB], "n.P.d", "legal", ("P", 1, "d"), "alone-as-middle"),
    ("[n = (Q SEQ Q)] & (n.Q.d: <5)", [QB], "n.Q.d", "refused", None, "alone-as-middle: used twice"),
    ("X & (X.Q.d: <5)", [PB, QB, "X := [n = (P SEQ Q)]"], "X.Q.d", "refused", None, "path-rules rule 6"),
    ("X & (X.n.Q.d: <5)", [PB, QB, "X := [n = (P SEQ Q)]"], "X.n.Q.d", "refused", None, "path-rules rule 6"),
    ("X & (X.d: <5)", [PB, QB, "X := [n = (P SEQ Q)]"], "X.d", "refused", None, "path-rules rule 6"),
    ("[n = (P SEQ B(Q))] & (n.B.p.d: <5)", [PB, QB, BB], "n.B.p.d", "legal", ("Q", 1, "d"), "a reading (F6)"),
    ("[n = (P SEQ B(Q))] & (n.B.d: <5)", [PB, QB, BB], "n.B.d", "legal", ("Q", 1, "d"), "a reading (F6), rule 4"),
    ("[n = (P SEQ B(Q))] & (n.d: <5)", [PB, QB, BB], "n.d", "refused", None, "a reading (F6)"),
    ("[n = (Q)] & (n.d: <5)", [QB], "n.d", "legal", ("Q", 1, "d"), "a reading (F7), parentheses aside"),
    ("[n = Q] & (n.d: <5)", [QB], "n.d", "legal", ("Q", 1, "d"), "path-rules rule 4"),
    ("[n = [m = P] SEQ \"!\"] & (n.d: <5)", [PB], "n.d", "legal", ("P", 1, "d"), "path-rules rules 1, 4"),
    ("[n = [_x = P]] & (n.d: <5)", [PB], "n.d", "refused", None, "path-rules rule 2"),
    ("[n = ([m = P] SEQ [_x = Q])] & (n.d: <5)", [PB, QB], "n.d", "legal", ("P", 1, "d"), "skip-past-wall"),
    ("[n = ([_ = P] SEQ Q)] & (n.d: <5)", [PB, QB], "n.d", "refused", None, "alone-as-middle (F25: the gate named)"),
    ("/(?<g>(?<d>\\d))x/ & (g.d: <5)", [], "g.d", "legal", ("P", 1, "d"), "group-node"),
    ("X & (X.g.d: <5)", ["X := /(?<g>(?<d>\\d))x/"], "X.g.d", "legal", ("X", 1, "d"), "group-node, rule 5"),
    ("X & (X.d: <5)", ["X := /(?<_g>(?<d>\\d))x/"], "X.d", "refused", None, "group-node, rule 2"),
    ("[n = /(?<_g>(?<d>\\d))x/] & (n.d: <5)", [], "n.d", "refused", None, "group-node, rule 2"),
    ("/(?<_g>(?<d>\\d))x/ & (_g.d: <5)", [], "_g.d", "legal", ("P", 1, "d"), "group-node, rule 2's start"),
    ("/(?<g>${A})x/ & (g.A.h: <5)", [AB], "g.A.h", "legal", ("A", 1, "h"), "group-node (c)"),
    ("/(?<g>${A})x/ & (g.h: <5)", [AB], "g.h", "refused", None, "group-node (c) with alone-as-middle"),
    ("/(?<g>${A})x/ & (A.h: <5)", [AB], "A.h", "legal", ("A", 1, "h"), "group-node (c), rule 6's start"),
    ("/(?<g>(?<d>\\d))x/ SEQ /(?<g>(?<d>\\d))y/ & (g.d: <5)", [], "g.d", "legal", None, "group-node (e), last mention"),
    ("/(?<g>(?<d>\\d))\\w/ & /\\w(?<g>(?<d>\\d))/ & (g.d: <5)", [], "g.d", "refused", None, "group-node (e), `&`"),
    ("[pub = B(A)] & (pub.A.h: <5)", [AB, BB], "pub.A.h", "refused", None, "shorthand-outside"),
]
if s111("s3"):
    GRID111[1] = GRID111[1][:3] + ("legal",) + GRID111[1][4:]
g_bad, g_mech, g_n = [], [], 0
for e_, b_, rd_, want, tgt, why in GRID111:
    v = walk_v(e_, b_, rd_)
    if v[0] != want:
        g_bad.append((e_, rd_, want, v))
    if want == "legal" and v[0] == "legal" and tgt:
        P_, err_ = run11(e_, b_)                             # noqa: F821
        texts = TXX if "B(" in e_ else (TG if "x/" in e_ else T2)
        try:
            R_ = mech(e_, b_, target=tgt, cond=(0, 4))
        except MechError as x_:
            g_mech.append((e_, "MECH " + str(x_)))
            continue
        g_n += 1
        if P_ is None or answers(P_, texts) != answers(R_, texts):
            g_mech.append((e_, err_ or "answers differ"))
    print("   %-58s %-8s %-8s %s" % (e_[:58], rd_, v[0], why))
check("GRID111", not g_bad and not g_mech and g_n >= 12,
      "%d reads; verdicts differing %s; legal reads against MECH111: %d, differing %s" % (
          len(GRID111), g_bad or "none", g_n, g_mech or "none"))

unit111("READ2", "gate-twice-scope (F2), both readings RUN: (a) uses counted over the definition, (b) under the read's "
        "prefix (printed, marked)")
E2 = "[n = (P SEQ Q)] SEQ \";\" SEQ [m = (P SEQ Q)] & (n.Q.d: <5)"
ra = walk_v(E2, [PB, QB], "n.Q.d", {"twice": "b" if s111("s11") else "a"})
rb = walk_v(E2, [PB, QB], "n.Q.d", {"twice": "b"})
P2, _ = run11(E2, [PB, QB])                                  # noqa: F821
R2 = mech(E2, [PB, QB], target=("Q", 1, "d"), cond=(0, 4))
T22 = ["7,3;7,7", "7,7;7,3", "1,2;3,4", "7,3;7,3"]
print("   (a) %s\n   (b) %s" % (ra, rb))
check("READ2", ra[0] == "refused" and rb[0] == "legal" and P2 is not None and answers(P2, T22) == answers(R2, T22),
      "(a) %s; (b) %s, its answers against MECH111 %s" % (ra[0], rb[0], "equal" if P2 and answers(P2, T22) == answers(
          R2, T22) else "DIFFER"))

unit111("READ3", "gate-beside-label (F3), the three readings RUN: (i) a compile error, (ii) a's `d` (printed, "
        "marked), (iii) Q's `d`, the last mention; each legal reading's answers against MECH111")
E3 = "[n = ([a = P] SEQ Q)] & (n.d: <5)"
r3 = {k: walk_v(E3, [PB, QB], "n.d", {"beside": ("ii" if s111("s12") and k == "iii" else k)}) for k in ("i", "ii", "iii")}
ok3 = r3["i"][0] == "refused" and r3["ii"][1:3] == ("B:P", "d") and r3["iii"][1:3] == ("B:Q", "d")
for k, (bn, u) in (("ii", ("P", 1)), ("iii", ("Q", 1))):
    READ111["beside"] = k
    P3, e3 = run11(E3, [PB, QB])                             # noqa: F821
    R3 = mech(E3, [PB, QB], target=(bn, u, "d"), cond=(0, 4))
    same = P3 is not None and answers(P3, T2) == answers(R3, T2)
    ok3 = ok3 and same
    print("   (%s) %s; answers against MECH111 %s" % (k, r3[k], "equal" if same else "DIFFER %s" % e3))
READ111["beside"] = "ii"
print("   (i) %s" % (r3["i"],))
check("READ3", ok3, "(i) %s; (ii) %s; (iii) %s" % (r3["i"][0], r3["ii"][1:3], r3["iii"][1:3]))

unit111("GROUPNODE", "the group-node ruling's readings (a)-(e) of its record entry, RUN; and every printed program "
        "naming an underscore group, found by grep, read by WALK111")
gn = {}
for e_, b_, rd_ in (("/(?<g>(?<d>\\d))x/ & (g.d: <5)", [], "g.d"), ("X & (X.d: <5)", ["X := /(?<_g>(?<d>\\d))x/"], "X.d"),
                    ("[n = /(?<_g>(?<d>\\d))x/] & (n.d: <5)", [], "n.d"), ("/(?<g>${A})x/ & (g.h: <5)", [AB], "g.h"),
                    ("/(?<g>${A})x/ & (g.A.h: <5)", [AB], "g.A.h"), ("/(?<g>${A})x/ & (A.h: <5)", [AB], "A.h")):
    gn[(e_, rd_)] = walk_v(e_, b_, rd_)
    print("   %-45s %-6s %s" % (e_, rd_, gn[(e_, rd_)][0]))
Pa, _ = run11("/(?<g>(?<d>\\d))x/ & (g.d: <5)")              # noqa: F821
Pb, _ = run11("[g = /(?<d>\\d)/] SEQ /x/ & (g.d: <5)")       # noqa: F821
okA = Pa is not None and Pb is not None and answers(Pa, TG) == answers(Pb, TG)
e1, e2 = "/(?<g>(?<d>\\d))x/ SEQ /(?<g>(?<d>\\d))y/ & (g.d: <5)", "/(?<g>(?<d>\\d))\\w/ & /\\w(?<g>(?<d>\\d))/ & (g.d: <5)"
Pe, _ = run11(e1)                                            # noqa: F821
Re1 = RePg(r"(?:\d)x(?P<T>[0-4])y", "T")                     # the last mention, written by hand from the ruled rule
TE = ["3x3y", "3x7y", "7x3y", "x3x3y"]
okE = Pe is not None and answers(Pe, TE) == answers(Re1, TE) and run11(e2)[0] is None   # noqa: F821
UG = []
for f_ in BASES11:                                           # noqa: F821
    for ln_, L_ in enumerate(NOWS[f_].split("\n"), 1):       # noqa: F821
        for m_ in re.finditer(r"\(\?<(_\w+)>", L_):
            UG.append((f_, ln_, m_.group(1), bool(re.search(r"\w\.%s\b" % m_.group(1), L_))))
for x_ in UG:
    print("   UGROUP %s:%d `%s`, read through it: %s" % x_)
okB = gn[("X & (X.d: <5)", "X.d")][0] == "refused" and gn[("[n = /(?<_g>(?<d>\\d))x/] & (n.d: <5)", "n.d")][0] == "refused"
okC = [gn[k][0] for k in list(gn)[3:]] == ["refused", "legal", "legal"]
if s111("s4"):
    okC = okC and gn[("/(?<g>${A})x/ & (g.h: <5)", "g.h")][0] == "legal"
check("GROUPNODE", okA and okB and okC and okE and not any(x_[3] for x_ in UG),
      "(a) `g.d` legal, the answers of `[g = /(?<d>\\d)/] SEQ /x/`: %s; (b) the two walls refused: %s; (c) g.h, g.A.h, "
      "A.h: %s; (e) last mention and `&`: %s; printed underscore groups %d, read through: %d" % (
          okA, okB, [gn[k][0] for k in list(gn)[3:]], okE, len(UG), sum(1 for x_ in UG if x_[3])))

unit111("MARKED111", "the marked readings the documents print, each RUN: against MECH111 where legal, refused where "
        "the reading refuses")
MK = [
    ("`!` on a lookaround in rx text is its opposite", "\"x\" SEQ !/(?=\\d)/", [], "x(?!\\d)", ["x", "x1", "1x2", "xx"]),
    ("`^c` on a condition is c", "/(?<h>\\d)/ SEQ ^(h: <5) SEQ /x/", [], "[0-4]x", ["3x", "7x", "a3x"]),
    ("`when` with a condition test", "/(?<h>\\d)/ SEQ when((h: <5), /a/, /b/)", [], "(?:[0-4]a|[5-9]b)",
     ["3a", "3b", "7a", "7b", "x7b3a"]),
    ("a group name from a marked parameter, `_:` its blank", "C(_:)", ["C(n:) := /(?<${n}>\\d)x/"], "(\\d)x",
     ["7x", "x", "77x"]),
    ("`.index` of a label inside one alternative is its constant", "F & (F.c.index: 2)",
     ["F := [a = \"99\"] SEQ [b = \"76\"] | [c = \"87\"]"], "87", ["87", "9976", "x87"]),
]
MKR = [
    ("a label set only inside `!^A`, read after it", "!^/(?<d>\\d)/ SEQ /\\w/ & (d: <5)", []),
    ("a group's whole name from an unmarked parameter", "C(x)", ["C(n) := /(?<${n}>\\d)x/"]),
    ("`.index` of the other position never holds", "F & (F.c.index: 1)",
     ["F := [a = \"99\"] SEQ [b = \"76\"] | [c = \"87\"]"]),
]
if s111("s5"):
    MK[0] = (MK[0][0], MK[0][1], [], "x(?=\\d)", MK[0][4])
mk_bad = []
for k_, e_, b_, rx_, t_ in MK:
    P_, err_ = run11(e_, b_)                                 # noqa: F821
    R_ = RePg(rx_)
    ok_ = P_ is not None and answers(P_, t_) == answers(R_, t_)
    if not ok_:
        mk_bad.append((k_, err_))
    print("   %s: %s" % (k_, "RUN, equal to `%s`" % rx_ if ok_ else "DIFFERS %s" % err_))
for k_, e_, b_ in MKR:
    P_, err_ = run11(e_, b_)                                 # noqa: F821
    never = P_ is not None and not any(P_.whole(t) or P_.search(t) for t in ["87", "9976", "3a", "7x"])
    ok_ = P_ is None or (k_.startswith("`.index`") and never)
    if not ok_:
        mk_bad.append((k_, "legal"))
    print("   %s: %s" % (k_, err_ or ("never holds" if never else "LEGAL")))
check("MARKED111", not mk_bad, "%d legal readings against regexes written from their sentences, %d refusals; "
      "differing: %s" % (len(MK), len(MKR), mk_bad or "none"))

unit111("EVERY111", "review r111 F5: `every` and the item form agree where the label is required, and part only "
        "where it is optional (the critic's count, re-run over the texts of `17,x` up to length 5)")
TV = texts11("17,x", 5)                                      # noqa: F821
pairs = [("required", "/(?:(?<d>\\d),)*x/ & every(@d, \"7\")", "/(?:(?<d>\\d)${(d: \"7\")},)*x/"),
         ("optional", "/(?:(?<d>\\d)?,)*x/ & every(@d, \"7\")", "/(?:(?<d>\\d)?${(d: \"7\")},)*x/")]
ev = {}
for k_, a_, b_ in pairs:
    Pa_, ea_ = run11(a_)                                     # noqa: F821
    Pb_, eb_ = run11(b_)                                     # noqa: F821
    ev[k_] = diff11(Pa_, Pb_, TV) if Pa_ and Pb_ else (ea_, eb_)   # noqa: F821
    print("   label %s: %d texts, every against the item form differ (whole, searched, find-all) %s" % (k_, len(TV), ev[k_]))
if s111("s14"):
    ev["required"] = (1, 0, 0)
check("EVERY111", ev["required"] == (0, 0, 0) and isinstance(ev["optional"][0], int) and sum(ev["optional"]) > 0,   # noqa: F821
      "required %s, optional %s" % (ev["required"], ev["optional"]))

unit111("SWEEP111", "every printed three-mode line RUN under this model; the starting commit %s's lines under "
        "predfold1125's builder (X111 off, the control) against these, keyed by the program; every move DECLARED" % START111)
exec(compile(_src11[_src11.index("def sw11(docs):"):_src11.index("def key11(k):")], P1125, "exec"), globals())   # noqa: S102  predfold1125's sweep, verbatim
_sweep_one11, _modes_of11, _fmt11 = sweep_one, modes_of, fmt   # noqa: F821
NL111 = [False]


def modes_of(line):                                          # noqa: F811
    wh, sr, fa = _modes_of11(line)
    if NL111[0]:
        return [t.replace("\\n", "\n") for t in wh], sr.replace("\\n", "\n"), fa.replace("\\n", "\n")
    return wh, sr, fa


def fmt(P, whole, srch, fa):                                 # noqa: F811
    r = _fmt11(P, whole, srch, fa)
    return r.replace("\n", "\\n") if NL111[0] else r


def sweep_one(line_, a, pt, tail):                           # noqa: F811
    """predfold1125's, with a text's `\\n` read as a line end, as the documents write texts (library.md's
    options lines): the texts only, never the program."""
    NL111[0] = "\\n" in a
    try:
        return _sweep_one11(line_, a, pt, tail)
    finally:
        NL111[0] = False


OLD111 = {f_: _git8("docs/design/predicates/" + f_, START111) for f_ in DOCF}   # noqa: F821
X111[0] = False
OLD_T111 = sw11(OLD111)                                      # noqa: F821
X111[0] = True
NOWS111 = dict(NOWS)                                         # noqa: F821
if s111("s6"):
    NOWS["core.md"] = NOWS["core.md"].replace("A group inside a group: WHOLE `3x` HOLDS", "A group inside a group: WHOLE `3x` FAILS", 1)   # noqa: F821
NEW_T111 = sw11(NOWS)                                        # noqa: F821
NOWS.update(NOWS111)                                         # noqa: F821
# declarations: a printed line whose program a ruling or a finding of this lane moved or dropped
GONE111 = {
    "[g = /(?<d>\\d)/] SEQ /x/ & (g.d: <5)": "group-node: candidate (b)'s line, ruled; its answers now printed on the "
                                           "group's own program (GROUPNODE (a))",
    "C(_)": "r111 F8: re-spelled `C(_:)` with `C(n:) := /(?<${n}>\\d)x/` (label-needs-mark on a group's whole name)",
    'm SEQ "!"': "r111 F14: the creator's no-deduplication line dropped; his words are of a search's results",
    'm["b" | 1] SEQ /\\w/': "r111 F15: the key-order witness re-picked (`m[\"b\" | \"a\"]` over `{a = /\\d/, b = /\\d\\d/}`)",
}
MOVED111 = {}
inh111 = set((k_, f_, st_) for k_, vs in OLD_T111.items() for f_, _, st_, _, _ in vs if st_ != "same")
sw_bad, sw_moved, sw_gone, sw_new, sw_inh, cnt = [], [], [], [], [], {}
used111 = set()
for k_, vs in NEW_T111.items():
    for f_, ln_, st_, got_, pr_ in vs:
        cnt[st_] = cnt.get(st_, 0) + 1
        if st_ != "same":
            if (k_, f_, st_) in inh111:
                sw_inh.append((f_, ln_, st_, k_[0]))
            else:
                sw_bad.append((f_, ln_, st_, k_[0], got_[:160]))
for k_, vs0 in OLD_T111.items():
    for f0 in sorted(set(v_[0] for v_ in vs0)):
        vs = [v_ for v_ in vs0 if v_[0] == f0]
        nk = [v_ for v_ in NEW_T111.get(k_, []) if v_[0] == f0]
        if nk:
            po = sorted(set(v_[4] for v_ in vs))
            pn = sorted(set(v_[4] for v_ in nk))
            if po != pn and repr(k_[0]) not in MOVED111:
                sw_moved.append((f0, k_[0], " || ".join(po)[:200], " || ".join(pn)[:200]))
            continue
        if k_[0] in GONE111:
            used111.add(k_[0])
            print("   DROPPED OR MOVED BY A RULING %s:%d `%s`: %s" % (vs[0][0], vs[0][1], k_[0], GONE111[k_[0]]))
            continue
        sw_gone.append((vs[0][0], vs[0][1], k_[0], vs[0][2]))
stale111 = sorted(k_ for k_ in GONE111 if k_ not in used111)
for k_, vs in NEW_T111.items():
    if k_ not in OLD_T111:
        sw_new.append((vs[0][0], vs[0][1], k_[0]))
for x_ in sw_new:
    print("   ADDED %s:%d `%s`" % x_)
for x_ in sw_gone:
    print("   GONE %s:%d %r (was %s)" % x_)
for x_ in sw_moved:
    print("   MOVED %s %r\n      old: %s\n      now: %s" % x_)
for x_ in sw_bad:
    print("   BAD %s:%d %s `%s`: %s" % x_)
for x_ in sw_inh:
    print("   INHERITED (the control's own, same key and status) %s:%d %s `%s`" % x_)
for x_ in stale111:
    print("   STALE DECLARATION %s" % x_)
check("SWEEP111", OLD_T111 and not sw_bad and not sw_moved and not sw_gone and not stale111,   # noqa: F821
      "%d printed lines now (%s), %d keys at the starting commit; not same and not inherited %d (inherited %d); "
      "moved %d; gone %d; declared %d; added %d; stale %d" % (
          sum(len(v) for v in NEW_T111.values()), ", ".join("%s %d" % kv for kv in sorted(cnt.items())),
          len(OLD_T111), len(sw_bad), len(sw_inh), len(sw_moved), len(sw_gone), len(GONE111), len(sw_new),
          len(stale111)))

unit111("ERRSWEEP111", "every printed compile-error line of the base files refused under this model, no crash; each "
        "named form in the refusal's message (MSG111: predfold1125's rows and this lane's)")
exec(compile(_src9[_src9.index("def err_lines(docs"):_src9.index("es_now = err_lines(D8)")], P1124, "exec"),   # noqa: F821
     globals())                                              # noqa: S102  predfold1124's reader, verbatim
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
if s111("s7"):
    D8["core.md"] = D8["core.md"].replace("An underscore group walls, from outside: modes: a compile error (`X & (X.d: <5)`",
                                          "An underscore group walls, from outside: modes: a compile error (`X & (X.g.d: <5)`", 1)   # noqa: F821
    D8["core.md"] = D8["core.md"].replace("X := `/(?<_g>(?<d>\\d))x/`: the path crosses", "X := `/(?<g>(?<d>\\d))x/`: the path crosses", 1)   # noqa: F821
es_now = [x_ for x_ in err_lines(D8) if not x_[0].endswith("_details.md")]   # noqa: F821
es_seen = set((f_, ln_) for f_, ln_, _, _ in es_now)
es_skip = []
for f_ in BASES11:                                           # noqa: F821
    for ln_, L_ in enumerate(D8[f_].split("\n"), 1):          # noqa: F821
        if "modes: a compile error" in L_ and (f_, ln_) not in es_seen:
            es_skip.append((f_, L_.split(": modes:", 1)[0].strip()[:70]))
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
MSG111 = {
    "/\\d+/ & !/7\\d*/": "`~/7\\d*/`",
    "/(?<h>\\d)/ & ~(h: <5)": "`!(h: <5)`",
    "\"a\\d\"": "`/\\d/`",
    "m": "no label",
    "m.z": "no member",
    "R(x, A)": "marked `l:`",
    "[n = (P SEQ Q)] & (n.d: <5)": "`n.Q.d`",
    "[n = (Q SEQ Q)] & (n.Q.d: <5)": "more than once",
    "X & (X.Q.d: <5)": "rule 6",
    "C(x)": "marked `n:`",
    "[n = (P SEQ B(Q))] & (n.d: <5)": "`n.B.d`",
    "X & (X.d: <5)": "rule",
    "[n = /(?<_g>(?<d>\\d))x/] & (n.d: <5)": "underscore group",
    "/(?<g>${A})x/ & (g.h: <5)": "`g.A.h`",
    "!^/(?<d>\\d)/ SEQ /\\w/ & (d: <5)": "`!^`",
}
es_bad, es_msg = [], []
for f_, ln_, e_, b_ in es_now:
    Pg, err = run11(e_, b_)                                  # noqa: F821
    if Pg is not None or (err or "").startswith("CRASH"):
        es_bad.append((f_, ln_, e_, "legal" if Pg is not None else err[:100]))
    elif e_ in MSG111 and MSG111[e_] not in err:
        es_msg.append((e_, MSG111[e_], err[:120]))
    print("   %s:%d `%s` %s: %s" % (f_, ln_, e_, b_ or "", (err or "LEGAL")[:110]))
msg_unseen = sorted(set(MSG111) - set(e_ for _, _, e_, _ in es_now))
F25 = run11("[n = ([_ = P] SEQ Q)] & (n.d: <5)", [PB, QB])   # noqa: F821
f25ok = F25[0] is None and "`n.Q.d`" in F25[1]
print("   F25: `[n = ([_ = P] SEQ Q)] & (n.d: <5)`: %s" % F25[1])
for x_ in es_skip:
    print("   SKIPPED (the reader cannot read it) %s `%s`" % x_)
check("ERRSWEEP111", es_now and not es_bad and not es_msg and not msg_unseen and f25ok,   # noqa: F821
      "%d compile-error lines read, each refused with no crash: bad %s; named form missing %s; message rows with no "
      "line %s; F25's gate named first %s; skipped (unread, counted) %d" % (
          len(es_now), es_bad or "none", es_msg or "none", msg_unseen or "none", f25ok, len(es_skip)))

unit111("SPECLINES111", "every printed line new in this lane (not in its piece's file at the starting commit) is "
        "RUN: a three-mode line SAME as run (SWEEP111), a compile-error line refused (ERRSWEEP111)")
newset = {f_: set(NOWS[f_].split("\n")) - set(OLD111[f_].split("\n")) for f_ in BASES11}   # noqa: F821
if s111("s13"):
    NOWS["core.md"] = NOWS["core.md"].replace("His F, the other position: WHOLE `87` FAILS", "His F, the other position: WHOLE `87` HOLDS", 1)   # noqa: F821
    newset["core.md"].add("His F, the other position: WHOLE `87` HOLDS" + NOWS["core.md"].split("His F, the other position: WHOLE `87` HOLDS", 1)[1].split("\n", 1)[0])
    NEW_T111 = sw11(NOWS)                                    # noqa: F821
    NOWS.update(NOWS111)                                     # noqa: F821
nl3, nle, nl_bad = 0, 0, []
for k_, vs in NEW_T111.items():
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
seen_l = set()
for k_, vs in NEW_T111.items():
    for f_, ln_, st_, got_, pr_ in vs:
        seen_l.add((f_, NOWS[f_].split("\n")[ln_ - 1]))   # noqa: F821
seen_l |= set((f_, NOWS[f_].split("\n")[ln_ - 1]) for f_, ln_, _, _ in es_now)   # noqa: F821
nl_un = [(f_, L_[:90]) for f_ in BASES11 for L_ in sorted(newset[f_])   # noqa: F821
         if re.search(r"WHOLE `|modes: a compile error", L_) and (f_, L_) not in seen_l]
for x_ in nl_un:
    print("   UNREAD by the sweeps %s: %s" % x_)
nl_all = sum(1 for f_ in BASES11 for L_ in newset[f_] if re.search(r"WHOLE `|modes: a compile error", L_))   # noqa: F821
check("SPECLINES111", not nl_bad and nl3 + nle == nl_all, "%d new printed lines: three-mode %d, compile-error %d, "   # noqa: F821
      "unread %d; not as printed: %s" % (nl_all, nl3, nle, nl_all - nl3 - nle, nl_bad or "none"))

unit111("STALE111", "the base files, continuation lines joined, hold none of the texts review r111 named stale")
STALE = [
    (r"the six escapes", "F20"),
    (r"open group-as-node", "group-node"),
    (r"open peek-name", "peek-name, F10"),
    (r"\bowed at", "F11"),
    (r"the evidence engine reads no group as a middle", "group-node"),
    (r"or the loop can make no pass", "F5"),
    (r"two elements of one text stay two", "F14"),
    (r"an alternative set twice, one never set", "F13"),
    (r"The negated test is", "F22"),
    (r"carries two fields: `\.index`", "F13"),
    (r"`X\.a\.index` is the position of the alternative", "F13"),
    (r"`!X`, X a set or pattern: a compile error", "F4"),
]
if s111("s8"):
    STALE.append((r"A group inside a group", "planted"))
joined = {f_: re.sub(r"\n  +", " ", NOWS[f_]) for f_ in BASES11}   # noqa: F821
st_hits = [(f_, rx_, why) for rx_, why in STALE for f_ in BASES11 if re.search(rx_, joined[f_])]   # noqa: F821
for x_ in st_hits:
    print("   STALE %s `%s` (%s)" % x_)
check("STALE111", not st_hits, "%d stale texts searched; found %s" % (len(STALE), st_hits or "none"))   # noqa: F821

unit111("QUOTES111", "the owner's words this lane quotes, each in the record at the PINNED starting commit and in its "
        "piece; every record title a 2026-11-27 item cites is a title of that record")
REC111 = _git8("docs/design/plan_row_bodies/COND-FAMILY.md", START111)   # noqa: F821
QQ111 = [
    ("group-node: agree group as a step. Group names should be labels almost exactly excepting the explicit capture "
     "semantics", "core/labels/rule/group-node"),
    ("a named group in rx text is a step in a path like a part label. `g.d` is legal, the flat read still works by "
     "skipping, and an underscore group walls what is inside it.", "core/labels/rule/group-node"),
    ("Peek name: keep. We can review choice later. I'm not sure either.", "lib/control/peek"),
    ("`X.a.index` is the position, among X's alternatives, of the alternative `a` was set in: a constant for a label "
     "inside one alternative (your 1, 1, 2), the matched member for a label over the whole array.",
     "core/values/metadata"),
    ("m[\"a\"|1]: I would not deduplicate", "core/modules/map/access"),
    ("alone-as-middle: yes to the gate", "core/labels/rule/alone-as-middle"),
]
if s111("s9"):
    QQ111.append(("group-node: agree group as a node", "core/labels/rule/group-node"))
q_miss = [(q_[:50], t_) for q_, t_ in QQ111 if ws(q_) not in ws(REC111) or ws(q_) not in ws(piece8(t_))]   # noqa: F821
DET111 = NOWS["core_details.md"] + NOWS["library_details.md"] + NOWS["parked_details.md"]   # noqa: F821
cited = sorted(set(m_.group(1) for l_ in DET111.split("\n") if "predfix111" in l_ or "2026-11-27" in l_
                   for m_ in re.finditer(r'\(record:\s*"(.+?)"\)(?=[;,.:\s]|$)', l_)))
heads = [ws(h_) for h_ in re.findall(r"^#{2,3} (.*)$", REC111, re.M)]   # noqa: F821
t_miss = [t_[:80] for t_ in cited if not any(h_.rstrip(".") == ws(t_) or h_.startswith(ws(t_) + " (") for h_ in heads)]   # noqa: F821
check("QUOTES111", not q_miss and not t_miss, "%d quoted sentences (missing: %s); %d record titles cited (not a title "
      "at %s: %s)" % (len(QQ111), q_miss or "none", len(cited), START111, t_miss or "none"))   # noqa: F821

unit111("SUCCESSOR111", "every in-force model re-run: predfold1125 in full, and the seventeen its SUCCESSOR11 re-runs "
        "(their outputs dumped by it); each red DECLARED in predfix111_succ_decl.tsv by predfix90's `red_key10` "
        "key, which carries the red's own FAIL line and no document line numbers; a traceback never")
exec(compile(_src10[_src10.index("CRASH10 = re.compile("):_src10.index("succ_bad, succ_n, succ_t, succ_seen = ")], P90,   # noqa: F821
             "exec"), globals())                             # noqa: S102  predfix90's red key, verbatim
DECLF111 = os.path.join(HERE111, "predfix111_succ_decl.tsv")
SDECL = {}
if os.path.exists(DECLF111):
    for l_ in builtins.open(DECLF111, encoding="utf-8").read().split("\n"):
        if l_ and not l_.startswith("#"):
            m_, r_, cls_, why_, key_ = l_.split("\t", 4)
            SDECL.setdefault(m_, {})[r_] = (cls_, key_, why_)
if s111("s10") and SDECL:
    _m = sorted(SDECL)[0]
    _r = sorted(SDECL[_m])[0]
    SDECL[_m][_r] = (SDECL[_m][_r][0], SDECL[_m][_r][1] + " planted", SDECL[_m][_r][2])
SCR111 = os.environ.get("PREDFIX111_SUCCDIR", "")
READ111D = os.environ.get("PREDFIX111_READDUMP") == "1"
succ_bad, succ_seen, succ_outs = [], [], {}
if not LIGHT111 or READ111D:
    if not READ111D:
        env = {k: v for k, v in os.environ.items() if not k.startswith(("PREDFIX111_", "PREDFOLD1125_"))}
        env["PREDFOLD1125_SUCCDUMP"] = SCR111
        o_ = subprocess.run([sys.executable, "-I", "-B", P1125], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, env=env, timeout=5400).stdout
        builtins.open(os.path.join(SCR111, "predfold1125.out"), "w", encoding="utf-8").write(o_)
    for f_ in sorted(os.listdir(SCR111)):
        if f_.endswith(".out"):
            succ_outs[f_[:-4]] = builtins.open(os.path.join(SCR111, f_), encoding="utf-8").read()
    for mname, out in sorted(succ_outs.items()):
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
        decl = SDECL.get(mname, {})
        print("   %-13s last line: %s" % (mname, last[:150]))
        for r, (cls_, key_) in sorted(reds.items()):
            succ_seen.append((mname, r, cls_, key_))
            d_ = decl.get(r)
            if cls_ == "TRACEBACK" or d_ is None or d_[1] != key_:
                succ_bad.append((mname, r, "UNDECLARED" if d_ is None else ("KEY CHANGED" if cls_ != "TRACEBACK" else cls_)))
        for r in sorted(set(decl) - set(reds)):
            succ_bad.append((mname, r, "DECLARED, NOW GREEN"))
    WD = os.environ.get("PREDFIX111_WRITEDECL", "")
    if WD:
        with builtins.open(WD, "w", encoding="utf-8") as fh:
            fh.write("# model\tred\tclass\twhy\tkey (red_key10: the red's own FAIL line text, no document line numbers)\n")
            for mname, r, cls_, key_ in succ_seen:
                fh.write("%s\t%s\t%s\t%s\t%s\n" % (mname, r, cls_, SDECL.get(mname, {}).get(r, ("", "", "WHY?"))[2], key_))
    for x_ in succ_bad:
        print("   NOT AS DECLARED %s %s: %s" % x_)
    check("SUCCESSOR111", len(succ_outs) >= 18 and not succ_bad, "%d models read, %d reds, each against its declared "   # noqa: F821
          "key (%d declared): %s" % (len(succ_outs), len(succ_seen), sum(len(v) for v in SDECL.values()),
                                     succ_bad or "all as declared"))
else:
    print("   LIGHT: SUCCESSOR111 not run")

PLANTS111 = {"s1": "CANARY111", "s2": "TABLE111", "s3": "GRID111", "s4": "GROUPNODE", "s5": "MARKED111",
             "s6": "SWEEP111", "s7": "ERRSWEEP111", "s8": "STALE111", "s9": "QUOTES111", "s10": "SUCCESSOR111",
             "s11": "READ2", "s12": "READ3", "s13": "SPECLINES111", "s14": "EVERY111"}
if SAB111 == "all":
    caught = []
    for q_, tgt in sorted(PLANTS111.items(), key=lambda kv: int(kv[0][1:])):
        env = dict(os.environ, PREDFIX111_SABOTAGE=q_, PREDFIX111_LIGHT="1")
        if q_ == "s10":
            env["PREDFIX111_READDUMP"] = "1"
        o_ = subprocess.run([sys.executable, "-I", "-B", MY111], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, env=env, timeout=3000)
        fl = [l_ for l_ in o_.stdout.split("\n") if l_.startswith("FAIL ")]
        ok_ = o_.returncode != 0 and any(l_.startswith("FAIL %s:" % tgt) for l_ in fl) and "Traceback" not in o_.stdout
        caught.append((q_, tgt, ok_))
        print("   PLANT %s -> %s: %s; FAIL lines: %s" % (q_, tgt, "CAUGHT" if ok_ else "NOT CAUGHT",
                                                       [l_[:90] for l_ in fl]))
    check("PLANTS111", all(c_[2] for c_ in caught), "%d plants, caught %d" % (len(caught), sum(c_[2] for c_ in caught)))   # noqa: F821

failed111 = [n_ for n_, ok_ in RESULTS if not ok_]          # noqa: F821
print("predfix111_model: %d checks, %d failed%s" % (len(RESULTS), len(failed111),   # noqa: F821
                                                   (" (%s)" % ", ".join(failed111)) if failed111 else ""))
sys.exit(1 if failed111 else 0)
