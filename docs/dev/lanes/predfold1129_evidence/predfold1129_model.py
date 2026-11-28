#!/usr/bin/env python3
"""predfold1129_model.py: lane predfold1129's evidence, the successor of predfix113_model.py.

The fold of seven owner rulings of 2026-11-28 (record docs/design/plan_row_bodies/COND-FAMILY.md, from
"2026-11-28 OWNER RULING — reference-example-checked" to the end): reference-example-checked, named-list-body-read,
label-names-gate, argument-is-gate, part-of-argument, last-placement, same-path-last. DESIGN evidence only: nothing
here rules; no check under `make` reads it.

It LOADS predfix113's model unchanged up to its checks (`# ==== CHECKS113`; the older models load through it), then
puts its own walker GATE129 in front, switched by X129[0] (off: predfix113 as merged, the control):
  GATE129  the ONE gate rule, written from the ruled statements as asked:
           - every crossing from one definition's text into another (a binding used, a macro called, a parameter
             placed) is a gate, one step, never skipped (label-names-gate 1); its name is the label written directly
             on it, else the thing's own name (2): a binding's or a macro's name, the parameter's name (that name
             only inside the body, argument-is-gate 3); labels stacked on one spot are equal names of it
             (label-doors 5); only a label over text written right there may be skipped (3); an export list on a
             place flattens (5; argument-is-gate 5): the place under it is no step;
           - a placed parameter is a gate like any other (argument-is-gate 1): named by the body's label a step
             anyone may take (2); unlabelled, from outside the body, a wall (3); the argument's own text written
             in the caller is the caller's text (caller-label-export), reached from the call without the body;
           - a read from outside through an unlabelled gate is a wall (path-rules rule 6, unchanged);
           - a plain read through a name placed twice or more reaches the last placement written before the read
             (last-placement 2, 3; line 1 "but local implicit");
           - a skip is legal when every label it could reach has the same full path, and reads the last mention;
             two different full paths are an error naming both (same-path-last 1, 2); within one match (one-path
             line 1: branches of `|` part); a path that skips nothing reads the label directly under its last step
             (body-own-name); the array form exempt from one-path, never from a gate (array-gate).
  MECH129  python `re` built MECHANICALLY from the parsed program text: the walker's target spot is the one named
           group, the condition narrows it (the digits it allows, enumerated); never the engine.
The verdict is the last line, `predfold1129_model: N checks, F failed`; it exits non-zero iff that line reports a
failure. PINNED COMMITS: this model reads git ONLY by commit id (START129).
`PREDFOLD1129_CENSUS=1` prints the census (every printed read of the six documents at START129, the in-force walker
against GATE129) and exits 0. `PREDFOLD1129_LIGHT=1` skips SUCCESSOR129; `PREDFOLD1129_SUCCDIR=DIR` an existing EMPTY
scratch directory for the successor outputs; `PREDFOLD1129_READDUMP=1` reads DIR instead of re-running;
`PREDFOLD1129_SABOTAGE=sN` plants one wrong rule, fact or text per check (PLANTS129); `=all` runs each plant in its
own LIGHT subprocess.
Run: `timeout 6000 python3 -I -B <this dir>/predfold1129_model.py` from the worktree root.
"""
import builtins
import os
import re
import subprocess
import sys

MY129 = os.path.abspath(__file__)
HERE129 = os.path.dirname(MY129)
LANES129 = os.path.normpath(os.path.join(HERE129, ".."))
P113 = os.path.join(LANES129, "predfix113_evidence", "predfix113_model.py")
START129 = "43bbce01f"                                       # this lane's starting commit (lane/predfold1129), PINNED
SAB129 = os.environ.get("PREDFOLD1129_SABOTAGE", "")
LIGHT129 = os.environ.get("PREDFOLD1129_LIGHT") == "1"
CENSUS129 = os.environ.get("PREDFOLD1129_CENSUS") == "1"
_src113 = builtins.open(P113, encoding="utf-8").read()
_a129 = _src113.index("\n# ==== CHECKS113 (a probe loads the model up to this line)") + 1
_sav129 = {k: os.environ.pop(k) for k in list(os.environ)
           if k.startswith(("PREDFIX113_", "PREDFOLD1128_", "PREDFIX112_", "PREDFOLD1127_", "PREDFIX111_",
                            "PREDFOLD1125_", "PREDFIX90_"))}
__file__ = P113
exec(compile(_src113[:_a129], P113, "exec"), globals())      # noqa: S102  predfix113's engines, unchanged
__file__ = MY129
os.environ.update(_sav129)
X129 = [True]
MARK129 = "(the owner's strong lean, entailed by carve-out-reading and caller-label-export; to be confirmed)"


def s129(q):
    return SAB129 == q


# ================================================================== GATE129: the one gate rule
class R2129:
    """a marker in a chain: the walk went from a call straight into the caller's own text of an argument."""
    k = "r2"
    name = None
    kids = ()

    def __init__(self, call, argn=None):
        self.call = call
        self.argn = argn


def _pname129(P, n):
    return P.texts[n.tid][n.a:n.b].strip()


def _stack129(n):
    """the label stack a label node belongs to: (top, [labels top to bottom], the node under the bottom)."""
    top = n
    while top.parent is not None and top.parent.k == "label" and len(top.parent.kids) == 1 \
            and top.parent.kids[0] is top:
        top = top.parent
    labs, x = [], top
    while x.k == "label":
        labs.append(x)
        x = x.kids[0]
    return top, labs, x


def _is_crossing129(n):
    return n.k in ("use", "call", "arg")


def _names129(P, n, rtid):
    """the names a node answers to as a step or a start, read from the text rtid ([] = none)."""
    if n.k == "label":
        return [] if n.name == "_" else [n.name]
    if n.k == "grp":
        return [n.name]
    if n.k in ("use", "call"):
        if n.parent is not None and n.parent.k in ("label", "list"):
            return []                                        # a label written on it is its name (gate 2)
        return [n.name] if n.tid == rtid else []             # from outside an unlabelled gate is a wall (rule 6)
    if n.k == "arg":
        if n.parent is not None and n.parent.k in ("label", "list"):
            return []
        return [_pname129(P, n)] if n.tid == rtid else []    # the parameter's name only inside the body (3)
    return []


def _arg_contents129(call):
    """the caller's own text of each argument of a call: [(content, the arg node of its LAST placement)]."""
    btid = call.kids[0].tid
    seen = {}

    def go(n):
        for k in n.kids:
            if k.k == "arg" and k.tid == btid:
                c = k.kids[0]
                if id(c) not in seen or seen[id(c)][1].a < k.a:
                    seen[id(c)] = (c, k)
                continue
            go(k)
    go(call.kids[0])
    return sorted(seen.values(), key=lambda v: v[0].a)


def _walled_place129(call, argn):
    x = argn.parent
    while x is not None and x is not call:
        if x.k == "label" and x.name.startswith("_"):
            return True
        x = x.parent
    return False


def _norm129(pre, chain):
    """a chain from the root with each jump into an argument's own text (R2) replaced by that text's placement."""
    out = []
    for n in chain:
        if isinstance(n, R2129):
            out = list(pre.rootpath.get(id(n.argn), [n.argn])) if n.argn is not None else None
            continue
        if out is None:
            out = list(pre.rootpath.get(id(n), [n]))
            continue
        out.append(n)
    return out


def _walk_down129(start):
    """every (node, chain) below start: through bodies, and from a call into its arguments' own text (R2)."""
    out = []

    def go(n, chain, depth):
        if depth > 40:
            raise Unparsed("depth")                          # noqa: F821
        for k in n.kids:
            ch = chain + [k]
            out.append((k, ch))
            go(k, ch, depth + 1)
        if n.k == "call":
            for c, argn in _arg_contents129(n):
                if _walled_place129(n, argn):
                    continue                                 # the body walls the place: no way in from the call
                m = R2129(n, argn)
                ch = chain + [m, c]
                out.append((c, ch))
                go(c, ch, depth + 1)
    go(start, [start], 0)
    return out


def _crossed129(X, chain):
    """a crossing X on a chain is crossed when the chain goes on into what X enters (a call: not by R2)."""
    if X not in chain:
        return False
    i = chain.index(X)
    if i + 1 >= len(chain):
        return False
    return not isinstance(chain[i + 1], R2129)


def _classify129(P, chain, rtid, named):
    """the nodes between a start and a target on a chain: (walls, gates skipped, labels skipped, full path).
    `named` = the nodes the path names (start included), so a stack-mate of a named label is no skip."""
    walls, gates, skips, full = [], [], [], []
    between = [n for n in chain[1:-1] if not isinstance(n, R2129)]
    named_ids = set(id(n) for n in named)
    prev = chain[0]
    for i, n in enumerate(chain[1:-1], 1):
        if isinstance(n, R2129):
            prev = n
            continue
        p = chain[i - 1]
        if n.k == "label":
            top, labs, bottom = _stack129(n)
            mates = any(id(m) in named_ids or m is chain[-1] for m in labs)
            if n.name == "_" or n.name.startswith("_"):
                walls.append(n)
                continue
            if mates:
                prev = n
                continue
            if labs[0] is n:                                 # one entry per stack
                gate = _is_crossing129(bottom) and _crossed129(bottom, chain)
                (gates if gate else skips).append(n)
                full.append(tuple([labs[0].name] + sorted(m.name for m in labs[1:])))
            continue
        if n.k == "grp":
            if n.name.startswith("_"):
                walls.append(n)
                continue
            skips.append(n)
            full.append((n.name,))
            continue
        if n.k in ("use", "call"):
            if not isinstance(p, R2129) and p.k in ("label", "list"):
                continue                                     # labelled or listed: the label is the gate
            if not isinstance(p, R2129) and p.k == "arg":
                continue                                     # the argument's own use under its place: one spot
            if n.tid != rtid:
                walls.append(n)                              # from outside through an unlabelled gate (rule 6)
                continue
            if _crossed129(n, chain):
                gates.append(n)
                full.append((n.name,))
            else:
                skips.append(n)
                full.append((n.name,))
            continue
        if n.k == "list":
            skips.append(n)                                  # the door: passed, a node between, no name
            continue
        if n.k == "arg":
            if n.parent is not None and n.parent.k in ("label", "list"):
                continue
            if not isinstance(p, R2129) and p.k == "arg":
                continue                                     # a parameter passed on as a place's content: one spot
            if n.tid != rtid:
                walls.append(n)                              # an unlabelled place from outside (argument-is-gate 3)
                continue
            if id(n) in named_ids:
                continue
            gates.append(n)
            full.append((_pname129(P, n),))
            continue
        # alt seq and rx hole leaf cond list: structure, no step
    return walls, gates, skips, full


class Pre129:
    """the walker's view of one program: the parse (Prog1127 over prep1127's text), its root paths and order."""

    def __init__(self, expr, binds):
        e = _lookaround_not(expr)                            # noqa: F821  fe111's text rewrites, in its order
        e = re.sub(r"\[(\s*_?\w+\s*=\s*)\(\s*([A-Za-z_]\w*)\s*\)\]", r"[\1\2]", e)
        if "when(" in e:
            e = _when_cond(e)                                # noqa: F821
        e = _caret_cond(e)                                   # noqa: F821
        e, binds = _name_hole_mark(e, list(binds))           # noqa: F821
        e = _index_const(e, binds)                           # noqa: F821
        self.e0 = e
        keep = LIBMACROS.get("hits")                         # noqa: F821
        if keep is not None:
            LIBMACROS["hits"] = (keep[0], HITS_NEW128)       # noqa: F821  the walker reads the body as printed
        try:
            ew, bw, _ = prep1127(e, binds)                   # noqa: F821
        finally:
            if keep is not None:
                LIBMACROS["hits"] = keep                     # noqa: F821
        self.ew, self.bw = ew, bw
        self.P = Prog1127(ew, bw)                            # noqa: F821
        self.order, self.rootpath = {}, {}
        k = [0]

        def go(n, path):                                     # the LAST visit wins: an argument placed twice
            self.order[id(n)] = k[0]                         # is read at its last placement (last-placement 2)
            self.rootpath[id(n)] = path
            k[0] += 1
            for c in n.kids:
                go(c, path + [c])
        go(self.P.root, [self.P.root])


def _key129(pre, full_chain):
    return tuple(pre.order.get(id(n), -1) for n in _norm129(pre, full_chain))


def _rel129(pre, ca, cb):
    """how two spots relate in one match, by their chains from the root: 'alt' | 'and' | 'seq'."""
    a = _norm129(pre, ca)
    b = _norm129(pre, cb)
    i = 0
    while i < min(len(a), len(b)) and a[i] is b[i]:
        i += 1
    lca = a[i - 1] if i else pre.P.root
    if lca.k == "rx" and lca.name == "|":
        raise Unparsed("an alternation inside an rx literal")   # noqa: F821
    if lca.k == "alt":
        return "alt"
    if lca.k == "and":
        return "and"
    return "seq"


class Refused129(Exception):
    pass


def _fullname129(before, full, rest):
    """the full path: the names before the step, the skipped spots' names (a stack by its top name), the rest."""
    return ".".join(list(before) + [x[0] for x in full] + list(rest))


def walk129(pre, path, rtid="P", scope=None, rpos=None, array=False):
    """judge the read `path` written in the text rtid (scope: the node whose tree it reads; rpos: where in rtid it is
    written): ("legal", target, full chain, how) | Refused129 | Unparsed."""
    P = pre.P
    root = scope if scope is not None else P.root
    nodes = [n for n, _ in _walk_down129(root)] + [root]
    starts, seen = [], set()
    for n in nodes:
        if id(n) in seen:
            continue
        if n.tid == rtid and path[0] in _names129(P, n, rtid):
            seen.add(id(n))
            starts.append(n)
    if not starts:
        raise Refused129("`%s`: no label `%s` is written in this text (a compile error: a bare read is a read of the "
                         "text's own labels; the start of a path is a label it writes, a binding's or a macro's name, "
                         "or, inside a body, a parameter)" % (".".join(path), path[0]))
    def fchain(n):
        return pre.rootpath.get(id(n), [n])
    how = "one"
    if len(starts) > 1:                                      # last-placement: the last placement before the read
        rels = set()
        for i, a in enumerate(starts):
            for b in starts[i + 1:]:
                rels.add(_rel129(pre, fchain(a), fchain(b)))
        if "and" in rels:
            raise Refused129("`%s`: both sides of `&` place `%s`, an ambiguous reference (a compile error, "
                             "core/labels/flow)" % (".".join(path), path[0]))
        if rels == {"alt"}:
            how = "branch taken"
        else:
            before = [s for s in starts if rpos is None or s.a < rpos]
            if s129("s1"):
                before = starts[:1]
            if not before:
                raise Refused129("`%s`: no placement of `%s` is written before the read" % (".".join(path), path[0]))
            starts = [max(before, key=lambda s: pre.order.get(id(s), 0))]
            how = "last placement"
    routes = [(s, [s], fchain(s)) for s in starts]           # (current node, named nodes, full chain from the root)
    for i, x in enumerate(path[1:], 1):
        last = i == len(path) - 1
        cands = []
        for cur, named, fc in routes:
            for node, chain in _walk_down129(cur):
                if x not in _names129(P, node, rtid):
                    continue
                if node.k in ("use", "call") and node.parent is not None and node.parent.k == "arg" \
                        and not s129("s4"):
                    continue                                 # the shorthand: a start only (shorthand-outside)
                if last and node.k not in ("label", "grp"):
                    continue
                walls, gates, skips, full = _classify129(P, chain, rtid, named + [node])
                if walls:
                    continue
                gn = [_gname129(P, g, rtid) for g in gates]
                cands.append((node, chain, gates, skips, full, named, fc + chain[1:], gn))
        if not cands:
            raise Refused129("`%s`: no label `%s` is reached from `%s` (a compile error: it is not there, or behind a "
                             "wall)" % (".".join(path), x, ".".join(path[:i])))
        uniq = []                                            # one per spot: the best route to it
        rank = lambda c: (2 if c[2] else (1 if c[3] else 0), len(c[4]))   # noqa: E731
        for c in sorted(cands, key=rank):
            if not any(u[0] is c[0] and _same_place129(u[1], c[1]) for u in uniq):
                uniq.append(c)
        gated = [c for c in uniq if c[2]]
        direct = [c for c in uniq if not c[2] and not c[3]]
        if s129("s2"):
            gated = []
        if array and last:
            if gated and not direct:
                raise Refused129("`@%s`: a `%s` sits behind a gate, %s; array or not, a gate is never skipped (a "
                                 "compile error, array-gate)" % (".".join(path), x, _gatesay129(path, i, gated)))
            return ("legal", None, None, "array")
        if direct:
            pool = direct                                    # body-own-name: nothing skipped is read
        elif gated:
            raise Refused129("`%s`: a `%s` sits behind a gate, which is never skipped: %s (a compile error, "
                             "label-names-gate)" % (".".join(path), x, _gatesay129(path, i, uniq)))
        else:
            pool = uniq
        if len(pool) > 1:
            fulls = set(tuple(c[4]) for c in pool)
            rel = set()
            for j, a in enumerate(pool):
                for b in pool[j + 1:]:
                    r = _rel129(pre, a[6], b[6])
                    rel.add(r)
                    if r == "and":
                        raise Refused129("`%s`: both sides of `&` set `%s`, an ambiguous reference (a compile "
                                         "error, core/labels/flow)" % (".".join(path), x))
                    if r == "seq" and _fp129(a[4]) != _fp129(b[4]) and not s129("s3"):
                        raise Refused129("`%s`: two labels `%s` with different full paths are visible from `%s`: "
                                         "write %s (a compile error, same-path-last 2)" % (
                                             ".".join(path), x, path[i - 1], " or ".join(
                                                 "`%s`" % _fullname129(path[:i], c[4], path[i:]) for c in pool)))
            if rel == {"alt"}:
                how = "branch taken"
                routes = [(c[0], c[5] + [c[0]], c[6]) for c in pool]
                continue
            pick = max(pool, key=lambda c: _key129(pre, c[6]))
            pool = [pick]
            how = "last mention" if how == "one" else how
        routes = [(c[0], c[5] + [c[0]], c[6]) for c in pool]
    if how == "branch taken" or len(routes) > 1:
        return ("legal", [r[0] for r in routes], [r[2] for r in routes], "branch taken")
    return ("legal", routes[0][0], routes[0][2], how)


def _gname129(P, g, rtid):
    if g.k == "label":
        return _stack129(g)[1][0].name
    if g.k == "arg":
        return _pname129(P, g)
    return g.name


def _fp129(full):
    return tuple(frozenset(x) for x in full)


def _same_place129(c1, c2):
    a1 = [n for n in c1 if getattr(n, "k", None) == "arg"]
    a2 = [n for n in c2 if getattr(n, "k", None) == "arg"]
    return not a1 or not a2 or a1[-1] is a2[-1] or True


def _gatesay129(path, i, cs):
    fps = sorted(set(".".join(list(path[:i]) + [g for g in c[7]] + list(path[i:])) for c in cs))
    return "write " + " or ".join("`%s`" % f for f in fps)


# ================================================================== reads of a program: its own and its bodies'
READC129 = re.compile(r"\(\s*(@?)([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*:\s*(.*)\)$", re.S)


def reads129(pre):
    """every read the program writes: (path, rtid, scope node, read position, array, condition text)."""
    P = pre.P
    out = []
    for x, y in P.conds:
        t = P.texts["P"][x:y]
        for path, a, b in reads_of(t):                       # noqa: F821
            arr = a > 0 and t[a - 1] == "@"
            out.append((path, "P", None, x + a, arr, t))
    seen = set()
    for n, chain in _walk_down129(P.root):
        if n.k != "cond" or (id(n), n.tid) in seen:
            continue
        seen.add((id(n), n.tid))
        scope = next((c for c in reversed(chain[:-1]) if getattr(c, "k", None) in ("use", "call")
                      and c.kids and c.kids[0].tid == n.tid), None)
        if scope is None and n.tid != "P":
            continue
        t = P.texts[n.tid][n.a:n.b]
        for path, a, b in reads_of(t):                       # noqa: F821
            arr = a > 0 and t[a - 1] == "@"
            out.append((path, n.tid, scope, n.a + a, arr, t))
    return out


def verdict129(expr, binds):
    """GATE129 on every read of a program: [(read, rtid, verdict)], verdict ('legal', how) | ('refused', msg)."""
    pre = Pre129(expr, binds)
    out = []
    for path, rtid, scope, pos, arr, ct in reads129(pre):
        if rtid == "P" and len(path) == 1:
            continue                                         # a bare read of the program's own label: label flow
        try:
            r = walk129(pre, path, rtid, scope, pos, arr)
            out.append((".".join(path), rtid, ("legal", r[3]), r))
        except Refused129 as e:
            out.append((".".join(path), rtid, ("refused", str(e)), None))
    return pre, out


# ================================================================== MECH129: python `re` from the parsed text
class Mech129Error(Exception):
    pass


class RePg129(RePg):                                         # noqa: F821
    """RePg with several needs: each a set of group names of which one must be set."""

    def __init__(self, rx, needs):
        RePg.__init__(self, rx)                              # noqa: F821
        self.needs = needs

    def _ok(self, m):
        return m is not None and all(any(m.group(g) is not None for g in gs) for gs in self.needs)


CONDRX129 = re.compile(r"\(\s*@?[A-Za-z_][\w.]*\s*:\s*(?:(==|<=|>=|<|>)\s*)?(-?\d+|\"[^\"]*\")\s*\)$")


def _cond129(ct):
    m = CONDRX129.match(ct.strip())
    if not m:
        raise Mech129Error("condition " + ct[:40])
    op, v = m.group(1) or "==", m.group(2)
    if v.startswith('"'):
        if op != "==":
            raise Mech129Error("an ordered string test")
        lit = v[1:-1]
        return lambda t: t == lit, [lit]
    n = int(v)
    f = {"==": lambda t: int(t) == n, "<": lambda t: int(t) < n, "<=": lambda t: int(t) <= n,
         ">": lambda t: int(t) > n, ">=": lambda t: int(t) >= n}[op]
    return f, None


DIGITSUB129 = re.compile(r"^(?:\\d(?:\{\d\})?|\[0-9\](?:\{\d\})?)+$")


def _narrow129(sub, test, lits):
    """the strings of a fixed-length digit pattern that pass the test, as an alternation (enumerated)."""
    import itertools
    if lits is not None:
        ok = [x for x in lits if re.fullmatch(sub, x)]
        return "(?:%s)" % "|".join(re.escape(x) for x in ok) if ok else "(?!)"
    if not DIGITSUB129.match(sub):
        raise Mech129Error("a target that is no fixed run of digits: " + sub[:30])
    n = len(re.sub(r"\\d|\[0-9\]", "0", re.sub(r"(\\d|\[0-9\])\{(\d)\}", lambda m: "0" * int(m.group(2)), sub)))
    ok = ["".join(t) for t in itertools.product("0123456789", repeat=n) if test("".join(t))]
    return "(?:%s)" % "|".join(ok) if ok else "(?!)"


def _plain129(rx_):
    """refuse a regex whose narrowed targets would not mean the condition: a hole left as text, an atomic group, a
    lookaround, a backreference, a possessive quantifier, or a quantified group holding a target (the label of a
    loop is the last pass's own; python's capture is the last pass that set it)."""
    for bad in ("${", "(?>", "\\k", "(?=", "(?!", "(?<=", "(?<!", "*+", "++", "?+", "}+", "(?(", "(?J"):
        if bad in rx_:
            raise Mech129Error("a construct the narrowing cannot carry: " + bad)
    st, i = [], 0
    while i < len(rx_):
        c = rx_[i]
        if c == "\\":
            i += 2
            continue
        if c == "[":
            j = i + 1
            if j < len(rx_) and rx_[j] == "^":
                j += 1
            if j < len(rx_) and rx_[j] == "]":
                j += 1
            while j < len(rx_) and rx_[j] != "]":
                j += 2 if rx_[j] == "\\" else 1
            i = j + 1
            continue
        if c == "(":
            st.append(i)
        elif c == ")":
            a = st.pop()
            if i + 1 < len(rx_) and rx_[i + 1] in "*+?{" and "(?P<T" in rx_[a:i]:
                raise Mech129Error("a target under a quantifier")
        i += 1


def mech129(expr, binds):
    """the program's regex, built from its parsed text: each read's target spot(s) a named group narrowed by its
    condition. Raises Mech129Error where the text is beyond it, Refused129 where GATE129 refuses a read."""
    pre = Pre129(expr, binds)
    P = pre.P
    spots = []                                               # (normalized chain ids, group name)
    needs = []
    k = [0]
    for path, rtid, scope, pos, arr, ct in reads129(pre):
        if arr:
            raise Mech129Error("a group question")
        r = walk129(pre, path, rtid, scope, pos, arr)
        test, lits = _cond129(ct)
        chains = r[2] if isinstance(r[1], list) else [r[2]]
        gs = []
        for ch in chains:
            k[0] += 1
            g = "T%d" % k[0]
            spots.append(([id(x) for x in _norm129(pre, ch)], g, test, lits))
            gs.append(g)
        needs.append(gs)
    stack = []

    def mark(n):
        ids = [id(x) for x in stack]
        for ch, g, test, lits in spots:
            if ch == ids:
                return g, test, lits
        return None

    def wrap(n, inner):
        m = mark(n)
        if not m:
            return "(?:%s)" % inner
        g, test, lits = m
        return "(?P<%s>%s)" % (g, _narrow129(inner, test, lits))

    def r_(n):
        stack.append(n)
        try:
            return r1(n)
        finally:
            stack.pop()

    def r1(n):
        if n.k == "alt":
            return wrap(n, "|".join(r_(c) for c in n.kids)) if mark(n) else "(?:%s)" % "|".join(r_(c) for c in n.kids)
        if n.k == "and":
            pats = [c for c in n.kids if c.k != "cond"]
            if len(pats) != 1:
                raise Mech129Error("& between patterns")
            return r_(pats[0])
        if n.k == "seq":
            return "".join(r_(c) for c in n.kids)
        if n.k in ("label", "list", "use", "call", "arg", "hole"):
            return wrap(n, r_(n.kids[0]))
        if n.k == "leaf":
            if "\\" in P.texts[n.tid][n.a:n.b]:
                raise Mech129Error("an escape in a string")
            return re.escape(TR11._unstring(P.texts[n.tid][n.a:n.b]))   # noqa: F821
        if n.k == "rx":
            return rxt(n)
        if n.k == "grp":
            return wrap(n, r_(n.kids[0]))
        raise Mech129Error("a node " + n.k)

    def rxt(n):
        t = P.texts[n.tid]
        out, i = [], n.a
        for c in sorted(n.kids, key=lambda c: c.a):
            seg = t[i:c.a]
            if "(?<" in re.sub(r"\(\?<[=!]", "", seg):
                raise Mech129Error("a group the parser kept as text")
            out.append(seg)
            if c.k == "hole":
                out.append(r_(c))
                i = c.b
            else:                                            # a named group: its own rx node inside
                stack.append(c)
                try:
                    m = mark(c)
                    inner = r_(c.kids[0])
                    out.append("(?P<%s>%s)" % (m[0], _narrow129(inner, m[1], m[2])) if m else "(?:%s)" % inner)
                finally:
                    stack.pop()
                i = c.b
        out.append(t[i:n.b])
        return "".join(out)
    for x, y in P.conds:
        if len(reads_of(P.texts["P"][x:y])) != 1:           # noqa: F821
            raise Mech129Error("a condition that is not one read")
    for n, _ in _walk_down129(P.root):
        if n.k == "cond" and len(reads_of(P.texts[n.tid][n.a:n.b])) != 1:   # noqa: F821
            raise Mech129Error("a body's condition that is not one read")
    rx_ = r_(P.root)
    _plain129(rx_)
    for ch, g, test, lits in spots:
        if "(?P<%s>" % g not in rx_:
            raise Mech129Error("a target spot not rendered (%s)" % g)
    try:
        return RePg129(rx_, needs)
    except re.error as e:
        raise Mech129Error("re: " + str(e))


# ================================================================== the census: every printed read, old walker against GATE129
BIND129 = re.compile(r"([\w.]+(?:\([\w, =:]*\))?) := `([^`]*)`")
GQ129 = ("some", "every", "count", "none", "all", "occurs")


FIELDS129 = ("slugs:", "rulings:", "rejected:", "readings:", "evidence:", "history:", "was:", "formerly:")


def field129(lines, i, f):
    """the field a line sits in: 'base' in a base file; in a details file the last field opened above it."""
    if not f.endswith("_details.md"):
        return "base"
    for j in range(i, -1, -1):
        t = lines[j]
        if t.startswith("## "):
            return "entry head"
        for fl in FIELDS129:
            if t.startswith(fl):
                return fl.rstrip(":")
    return "?"


def _piece_binds129(lines, i, line, binds):
    """a name the line's program uses but does not bind: its binding from the same piece (the nearest line above,
    then below, inside the piece's heading bounds), as the piece's reader reads it."""
    have = set(re.match(r"\s*([A-Za-z_]\w*)", b).group(1) for b in binds)
    a = i
    while a > 0 and not lines[a].startswith(("### ", "## ")):
        a -= 1
    b = i + 1
    while b < len(lines) and not lines[b].startswith(("### ", "## ")):
        b += 1
    names = set(re.findall(r"(?<![\w.$@])([A-Z][A-Za-z0-9_]*|[a-z][a-z0-9_]*)(?=[^\w]|$)", " ".join(
        re.findall(r"`([^`]*)`", line))))
    out = list(binds)
    for _ in range(3):                                       # the bindings' own names, two levels down
        need = sorted(n for n in names if n not in have)
        if not need:
            break
        for n in need:
            for j in list(range(i - 1, a - 1, -1)) + list(range(i + 1, b)):
                m = re.search(r"(?<![\w.])(%s(?:\([\w, =:]*\))?) := `([^`]*)`" % re.escape(n), lines[j])
                if m:
                    out.append("%s := %s" % (m.group(1), m.group(2)))
                    have.add(n)
                    names |= set(re.findall(r"(?<![\w.$@])([A-Za-z_][A-Za-z0-9_]*)", m.group(2)))
                    break
    return out


def printed129(docs):
    """(file, line no, kind, program, binds) of every program printed on a three-mode or compile-error line of the
    six documents (each backticked program with a read; a binding, a bare condition and a body skipped)."""
    out = []
    for f in DOCF:                                           # noqa: F821
        lines_ = docs[f].split("\n")
        for ln, line in enumerate(lines_, 1):
            three = "WHOLE " in line and " / FIND-ALL " in line
            err = "modes: a compile error (`" in line
            if not (three or err):
                continue
            binds = ["%s := %s" % b for b in BIND129.findall(line)]
            binds = _piece_binds129(lines_, ln - 1, line, binds)
            tail = line
            if three:
                a = answer_part(line)                        # noqa: F821
                tail = line[line.index(a) + len(a):] if a else line
            else:
                tail = line[line.index("modes: a compile error (`") + len("modes: a compile error ("):]
            first = True
            for s in re.findall(r"`([^`]*)`", tail):
                if ":=" in s:
                    continue
                try:
                    if s.startswith("(") and TR11._group_end(s, 0) == len(s):   # noqa: F821
                        continue
                except Exception:                            # noqa: BLE001  an unbalanced fragment, no program
                    continue
                if any(s == b.split(" := ", 1)[1] for b in binds):
                    continue
                has_read = re.search(r"\(\s*[@A-Za-z_][\w.]*\s*:|\b(%s)\(\s*@" % "|".join(GQ129), s)
                has_body_read = any(re.search(r"\(\s*[@A-Za-z_][\w.]*\s*:", b.split(" := ", 1)[1]) for b in binds)
                if not (has_read or has_body_read):
                    continue
                if not re.match(r"[\[\(/A-Za-z!^\"]", s):
                    continue
                kind = ("three-mode" if first else "three-mode, a further program") if three else "compile error"
                first = False
                out.append((f, ln, kind, s, binds, field129(lines_, ln - 1, f)))
    return out


def old_verdict129(pre, path, rtid, arr):
    """the in-force walker (predfix113's: walk1127 over its spot finder) on the same parse: ('legal', target) |
    ('refused', msg) | ('n/a', why)."""
    if rtid != "P":
        return ("n/a", "a body's read: the in-force walker judges only the program's own")
    try:
        r = walk1127(pre.P, path, None, arr)                 # noqa: F821
    except Refused as e:                                     # noqa: F821
        return ("refused", str(e))
    except Unparsed as e:                                    # noqa: F821
        return ("n/a", "unparsed: " + str(e))
    return ("legal", r[2], r[3])


def _pattern_only129(pre, e):
    """the program with its own top-level conditions removed (for the in-force engine on a body's reads)."""
    out, last = [], 0
    for x, y in sorted(pre.P.conds):
        out.append(e[last:x])
        last = y
    out.append(e[last:])
    t = "".join(out)
    t = re.sub(r"(\s*&\s*)+$", "", re.sub(r"^(\s*&\s*)+", "", t))
    return re.sub(r"&\s*&", "&", t)


def program_verdict129(e, binds):
    """GATE129 on a whole program: (pre, reads, new verdict, why): legal | error (a refused read, or the in-force
    engine refusing it for a reason no moved path rule gives)."""
    pre, vs = verdict129(e, binds)
    eng = run11(e, binds)                                    # noqa: F821
    olds = []
    for rd, rtid, v, r in vs:
        olds.append(old_verdict129(pre, rd.split("."), rtid, "@" + rd in e) if rtid == "P" else ("n/a", ""))
    bad = [(rd, v[1]) for rd, rtid, v, r in vs if v[0] == "refused"]
    if bad:
        return pre, vs, olds, "error", bad[0][1]
    if eng[0] is not None:
        return pre, vs, olds, "legal", ""
    moved = any(o[0] == "refused" for o in olds)
    body = any(rtid != "P" for _, rtid, _, _ in vs)
    if moved or (body and "does not hold" in (eng[1] or "")):
        return pre, vs, olds, "legal", "the in-force engine's refusal is a path rule that moved: %s" % (eng[1] or "")[:120]
    return pre, vs, olds, "error", "the in-force engine, for a reason no moved rule gives: %s" % (eng[1] or "")[:140]


def census129(docs):
    rows, spots, unparsed, kinds, total = [], [], [], [], 0
    progs = printed129(docs)
    for f, ln, kind, e, binds, fld in progs:
        eng = run11(e, binds)                                # noqa: F821  the in-force engine: the baseline
        ov = "legal" if eng[0] is not None else "error"
        pv = "error" if kind == "compile error" else "legal"
        try:
            pre, vs, olds, nv, why = program_verdict129(e, binds)
        except Exception as x:                               # noqa: BLE001
            unparsed.append((f, ln, fld, e, "%s: %s" % (type(x).__name__, str(x)[:70])))
            continue
        total += len(vs)
        if ov != pv and kind != "three-mode, a further program":
            kinds.append((f, ln, fld, kind, e, ov, eng[1] or ""))
        if ov != nv:
            rows.append(("legal to error" if ov == "legal" else "error to legal", f, ln, fld, kind, e, binds, vs, olds,
                         why, eng[1] or ""))
        for (rd, rtid, v, r), o in zip(vs, olds):
            if v[0] == "legal" and o[0] == "legal" and r is not None and not isinstance(r[1], list) and r[3] != "array" \
                    and o[1] is not None and o[1] is not r[1]:
                spots.append((f, ln, fld, kind, e, binds, rd, o, r))
    return progs, rows, spots, unparsed, kinds, total


if CENSUS129:
    progs_, rows_, spots_, unp_, kinds_, tot_ = census129(NOWS)   # noqa: F821
    by_ = {}
    for r_ in rows_:
        by_.setdefault((r_[0], r_[3] in ("base",)), []).append(r_)
    nbase = sum(1 for p_ in progs_ if p_[5] == "base")
    print("predfold1129 census at %s: %d printed programs on three-mode and compile-error lines of the six documents "
          "(%d in base files); the reader could not parse %d of them (%d in base files); %d reads judged in the rest. "
          "Against the in-force engine (predfix113), programs whose legality moves: %s; legal reads whose spot moves: %d" % (
              START129, len(progs_), nbase, len(unp_), sum(1 for u_ in unp_ if u_[2] == "base"), tot_,
              ", ".join("%s%s %d" % (k_[0], " (base)" if k_[1] else " (details)", len(v_)) for k_, v_ in sorted(by_.items())) or "none",
              len(spots_)))
    for k_ in sorted(by_, key=lambda k: (not k[1], k[0])):
        print("\n== %s, %s (%d)" % (k_[0], "base files" if k_[1] else "details files", len(by_[k_])))
        for cls, f, ln, fld, kind, e, binds, vs, olds, why, ew in by_[k_]:
            print("%s:%d [%s%s] `%s`   %s" % (f, ln, kind, "" if fld == "base" else ", field " + fld, e, "; ".join(binds)))
            for (rd, rtid, v, r), o in zip(vs, olds):
                print("      %s%s: GATE129 %s" % (rd, "" if rtid == "P" else " (in %s)" % rtid,
                                                 v[0] + " (" + v[1] + ")" if v[0] == "legal" else "refused: " + v[1][:230]))
            print("      in-force engine: %s" % ("legal" if cls == "legal to error" else "refused: " + ew[:200]))
    print("\n== legal reads whose spot moves (%d)" % len(spots_))
    for f, ln, fld, kind, e, binds, rd, o, r in spots_:
        print("%s:%d [%s] %s in `%s`   %s: GATE129 %s" % (f, ln, kind, rd, e, "; ".join(binds), r[3]))
    print("\n== the line's kind is not the in-force engine's verdict (prose, a joined line, or a history record) (%d)" % len(kinds_))
    for f, ln, fld, kind, e, ov, ew in kinds_:
        print("%s:%d [%s, %s] `%s`: the engine %s" % (f, ln, kind, fld, e[:100], ov if ov == "legal" else "refuses: " + ew[:90]))
    print("\n== not parsed (%d)" % len(unp_))
    for f, ln, fld, e, why in unp_:
        print("%s:%d [%s] `%s`: %s" % (f, ln, fld, e[:120], why))
    sys.exit(0)
