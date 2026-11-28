#!/usr/bin/env python3
"""predfold1128_model.py: lane predfold1128's evidence, the successor of predfix112_model.py.

The fold of five owner rulings (gate-beside-direct, carve-out-reading, caller-label-export, named-list-use,
param-reference) and of the owner's STRONG LEAN no-path-through-argument, applied and marked (record
docs/design/plan_row_bodies/COND-FAMILY.md, 2026-11-27). DESIGN evidence only: nothing here rules; no check under
`make` reads it.

It LOADS predfix112's model unchanged up to its checks (`# ==== CHECKS112`; the older models load through it), then
puts, switched by X128[0] (off: predfix112's walker and engine as merged, the control):
  PLACE128  the strong lean in the walker's spot finder `_between`, from the statement as put: a spot whose chain
            from the step's start crosses an argument's place is dropped unless the place is LISTED (its nearest
            ancestor that is not itself a place is an export list: the door of carve-out-reading, mode "A"), or the
            spot is a label the SENDER writes in that argument and the step's start is neither the call nor a label
            directly on it (caller-label-export: `Y.a.h` legal, `Y.c.a.h` refused). The list's alias and the place
            stay nodes between, so a read through the list skips them and one-path counts (the door, not "own").
            MODE128[0] switches the two unasked readings: "A0" (only the place's own parent list counts:
            forwarded-place's other reading), "A2" (any list above the place in its body: list-over-label's).
  MSG128    a refusal with no candidate left because a place was crossed names the rule and the ways in.
  NAMED128  the engine's front end for a named list on a parameter's place (named-list-use): the demand is checked
            at the call (and through a forwarding body), a never-satisfiable body refused at its definition, and
            the call inlined as the list over the argument (`[(=h) = A]`, the export list the engine runs).
  REF128    the front end for a declared reference parameter (param-reference): the head's list, line 2's and
            line 4's definition errors, line 3's call errors, and the expansion (each listed name read through the
            caller's name); a body calling `weekday_of` is run by WDPG128, python's datetime standing in for the
            planned native, on a regex built mechanically from the bindings' text (MINI128).
  SENT128   a switch (never the printed rule): sent-over-body-label's other reading, refused.
Every legal read new in this lane is ALSO answered by MECH111 (python `re` on a regex built mechanically from the
program text), never from the engine. The verdict is the last line, `predfold1128_model: N checks, F failed`; it
exits non-zero iff that line reports a failure.
PINNED COMMITS: this model reads git ONLY by commit id (START128). The older models it re-runs still read by branch
NAME in one place (predfold1123_model.py, `lane/pred-rev28:`); those lane files are historical and not edited.
`PREDFOLD1128_LIGHT=1` skips SUCCESSOR128; `PREDFOLD1128_SUCCDIR=DIR` an existing EMPTY scratch directory for the
successor outputs; `PREDFOLD1128_READDUMP=1` reads DIR instead of re-running; `PREDFOLD1128_WRITEDECL=F` writes the
seen reds as a declaration draft; `PREDFOLD1128_SABOTAGE=sN` plants one wrong rule, fact or text per check
(PLANTS128); `=all` runs each plant in its own LIGHT subprocess.
Run: `timeout 6000 python3 -I -B <this dir>/predfold1128_model.py` from the worktree root.
"""
import builtins
import datetime
import os
import re
import subprocess
import sys

MY128 = os.path.abspath(__file__)
HERE128 = os.path.dirname(MY128)
LANES128 = os.path.normpath(os.path.join(HERE128, ".."))
P112 = os.path.join(LANES128, "predfix112_evidence", "predfix112_model.py")
START128 = "8e7cca4a9"                                       # this lane's starting commit (lane/predfold1128), PINNED
SAB128 = os.environ.get("PREDFOLD1128_SABOTAGE", "")
LIGHT128 = os.environ.get("PREDFOLD1128_LIGHT") == "1"
_src112 = builtins.open(P112, encoding="utf-8").read()
_a128 = _src112.index("\n# ==== CHECKS112 (a probe loads the model up to this line)") + 1
_sav128 = {k: os.environ.pop(k) for k in list(os.environ)
           if k.startswith(("PREDFIX112_", "PREDFOLD1127_", "PREDFIX111_", "PREDFOLD1125_", "PREDFIX90_"))}
__file__ = P112
exec(compile(_src112[:_a128], P112, "exec"), globals())      # noqa: S102  predfix112's engines, unchanged
__file__ = MY128
os.environ.update(_sav128)
X128 = [True]
MODE128 = ["A"]
SENT128 = [False]
MARK128 = "(the owner's strong lean, entailed by carve-out-reading and caller-label-export; to be confirmed)"


def s128(q):
    return SAB128 == q


# ================================================================== PLACE128: no path through an argument's place
_BETWEEN112 = _between                                       # noqa: F821  predfold1127's spot finder, as loaded
DROP128 = [[]]                                               # per walk: the places a dropped spot crossed
CROSS128 = []                                                # per MECHROUTE128 walk: a kept spot crossed a place


def _listed128(arg):
    if MODE128[0] == "A0":
        return arg.parent is not None and arg.parent.k == "list"
    x = arg.parent
    while x is not None and x.k == "arg":                    # a parameter passed on sits in the inner body's place
        x = x.parent
    if x is None:
        return False
    if x.k == "list":
        return not s128("s1")
    if MODE128[0] == "A2":
        while x is not None and x.k != "call":
            if x.k == "list":
                return True
            x = x.parent
    return False


def _call_of128(arg):
    x = arg.parent
    while x is not None and x.k != "call":
        x = x.parent
    return x


def _between(start, x, P):                                   # noqa: F811
    out = _BETWEEN112(start, x, P)
    if not X128[0]:
        return out
    res = []
    for node, betw, gates, walls, chain in out:
        bad = [n for n in chain[1:] if n.k == "arg" and not _listed128(n)]
        if bad:
            last = bad[-1]
            below = chain[chain.index(last) + 1:]
            sender = (len(bad) == 1 and node.k == "label" and not node.name.startswith("_")
                      and not any(n.k in ("call", "arg") for n in below[:-1]))
            c = _call_of128(last)
            j = next((i for i, n in enumerate(chain) if n is c), -1)
            on_call = j < 0 or not any(_named(n) for n in chain[1:j])   # noqa: F821  the call or a label right on it
            if not (sender and not on_call):
                DROP128[-1].append((last, c))
                continue
        if CROSS128 and any(n.k == "arg" for n in chain[1:]):
            CROSS128[-1] = True
        res.append((node, betw, gates, walls, chain))
    return res


_WALK112 = walk1127                                          # noqa: F821  predfix112's patched walker


_PREP112 = prep1127                                          # noqa: F821
_DIGITS128 = re.search(r"`rx\.digits := rx\.repeat\(rx\.digit, min = 1, max = _\)` is `([^`]+)`", NOWS["library.md"])   # noqa: F821
assert _DIGITS128 and _DIGITS128.group(1) == "\\d+", "lib/rx/classes: rx.digits is not printed as \\d+"


def prep1127(expr, binds):                                   # noqa: F811
    """the walker's front end, `rx.digits` read as the library's printed `\\d+` (lib/rx/classes) so a read over it
    is judged (X128 on; the older walker left it unparsed)."""
    if X128[0]:
        sub = "/" + _DIGITS128.group(1) + "/"
        expr = re.sub(r"(?<![\w.])rx\.digits(?![\w(])", lambda _m: sub, expr)
        binds = [re.sub(r"(?<![\w.])rx\.digits(?![\w(])", lambda _m: sub, b_) for b_ in binds]
    return _PREP112(expr, binds)


def walk1127(P, path, reading=None, array=False):            # noqa: F811
    """the walker, its refusal re-worded where a place was crossed and no candidate is left (MSG128)."""
    DROP128.append([])
    try:
        return _WALK112(P, path, reading, array)
    except Refused as x:                                     # noqa: F821
        msg = str(x)
        if X128[0] and DROP128[-1] and "not visible through" in msg and not s128("s2"):
            c = DROP128[-1][0][1]
            nm = c.name if c is not None else "the macro"
            raise Refused("`%s`: the path passes %s's argument place, which no list opens (a compile error, "   # noqa: F821
                          "core/labels/rule/argument-place): read it by the sender's own name (`A.h` for `%s(A)`), "
                          "label the argument, or list it in the body (`[(=) = rx]`)" % (".".join(path), nm, nm))
        raise
    finally:
        DROP128.pop()


# ================================================================== the front ends: named lists, references
_PROG112 = prog                                              # noqa: F821  the loaded engine's entry


def _defs128(binds):
    out = {}
    for b in binds:
        m = re.match(r"\s*([A-Za-z_]\w*)(\((.*)\))?\s*:=\s*(.*)$", b, re.S)
        if m:
            out[m.group(1)] = (m.group(3), m.group(4).strip(), b)
    return out


def _params128(head):
    """a head's parameters: [(name or None, list or None)], a list `(=a, =b)`, `(y1 = year)` a reference."""
    ps, depth, cur = [], 0, ""
    for ch in head or "":
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            ps.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        ps.append(cur.strip())
    out = []
    for p in ps:
        if p.startswith("("):
            labs = []
            for it in p[1:-1].split(","):
                a, _, b = it.strip().partition("=")
                labs.append((a.strip() or b.strip(), b.strip()))   # (the body's name, the argument's label)
            out.append((None, labs))
        else:
            out.append((p.split("=")[0].strip().rstrip(":"), None))
    return out


def _exports128(name, defs, seen=()):
    """the public labels a binding's text exports (its groups and part labels, not under `_`); a binding it uses
    alone exports nothing; a part label passes its part's."""
    if name not in defs or name in seen:
        return set()
    body = defs[name][1]
    out = set()
    for m in re.finditer(r"\(\?<(\w+)>", body):
        out.add(m.group(1))
    for m in re.finditer(r"\[\s*(\w+)\s*=\s*([A-Za-z_]\w*)\s*\]", body):
        if not m.group(1).startswith("_"):
            out.add(m.group(1))
            out |= _exports128(m.group(2), defs, seen + (name,))
    for m in re.finditer(r"\[\s*(\w+)\s*=", body):
        if not m.group(1).startswith("_"):
            out.add(m.group(1))
    hidden = set()
    for m in re.finditer(r"\[\s*_\w*\s*=\s*/\(\?<(\w+)>", body):
        hidden.add(m.group(1))
    return out - hidden


def _calls128(e, name):
    """each call `name(...)` in e: (start, end, [argument texts])."""
    out = []
    for m in re.finditer(r"(?<![\w.$])%s\(" % re.escape(name), e):
        i = m.end()
        depth, j = 1, i
        while j < len(e) and depth:
            depth += {"(": 1, ")": -1}.get(e[j], 0)
            j += 1
        inner = e[i:j - 1]
        out.append((m.start(), j, [inner[x:y] for x, y in split_top_commas(inner, 0, len(inner))] if inner.strip() else []))   # noqa: F821
    return out


def _demands128(defs, macro, k, path=()):
    """what the k-th parameter of `macro` must export, by a named list in its body (or one it forwards to):
    [(label, demanding macro, list text)]; 'NEVER' where a label written on the parameter shuts it from the list."""
    if macro not in defs or macro in path:
        return []
    ps = _params128(defs[macro][0])
    if k >= len(ps) or ps[k][0] is None:
        return []
    p, body = ps[k][0], defs[macro][1]
    out = []
    for m in re.finditer(r"\[\s*\(=(\w+(?:\s*,\s*=\w+)*)\)\s*=\s*%s\s*\]" % re.escape(p), body):
        for lab in re.findall(r"\w+", m.group(1)):
            out.append((lab, macro, "(=%s)" % m.group(1)))
    for g in defs:
        for a, b, args in _calls128(body, g):
            for kk, arg in enumerate(args):
                if arg == p:
                    out += _demands128(defs, g, kk, path + (macro,))
                elif re.fullmatch(r"\[\s*\w+\s*=\s*%s\s*\]" % re.escape(p), arg):
                    for d in _demands128(defs, g, kk, path + (macro,)):
                        out.append(("NEVER",) + d)
    return out


def _named_list128(e, binds):
    """named-list-use: the demand at the call; the never-satisfiable body at its definition; the call inlined."""
    defs = _defs128(binds)
    nl = {n: v for n, v in defs.items() if v[0] and re.search(r"\[\s*\(=\w", v[1])}
    if not nl:
        return e, binds
    for g, (head, body, _) in defs.items():                  # a definition that can never be satisfied
        if not head:
            continue
        for k in range(len(_params128(head))):
            for d in _demands128(defs, g, k):
                if d[0] == "NEVER":
                    raise CompileError("at %s's definition: `%s` passes no `%s` to %s's list `%s`" % (   # noqa: F821
                        g, "[q = r]", d[1], d[2], d[3]))
    for g in defs:
        if not defs[g][0]:
            continue
        for a, b, args in _calls128(e, g):
            for k, arg in enumerate(args):
                for lab, by, lst in _demands128(defs, g, k):
                    if lab not in _exports128(arg, defs) and not s128("s3"):
                        raise CompileError("at `%s`: the argument exports no `%s`, which %s's list `%s` demands%s" % (   # noqa: F821
                            e[a:b], lab, by, lst, "" if by == g else ", through %s's place" % g))
    for n, (head, body, _) in nl.items():                    # inline `N(A)` as the list over the argument
        m = re.fullmatch(r"/\$\{\[\s*(\(=[^)]*\))\s*=\s*(\w+)\s*\]\}(.*)/", body)
        if not m:
            continue
        for a, b, args in reversed(_calls128(e, n)):
            new = "[%s = %s]" % (m.group(1), args[0]) + (" SEQ /%s/" % m.group(3) if m.group(3) else "")
            e = e[:a] + "(" + new + ")" + e[b:]
        e = re.sub(r"(?<![\w.])%s\.(\w+)" % re.escape(n), r"\1", e)
    return e, [b for b in binds if _defs128([b]).keys().isdisjoint(nl)]


def _ref128(e, binds):
    """param-reference: the four lines; returns (expr, binds, weekday or None)."""
    defs = _defs128(binds)
    refs = {n: v for n, v in defs.items() if v[0] and any(p[1] for p in _params128(v[0]))}
    for n, (head, body, _) in defs.items():                  # line 4: nothing inferred
        if not head or n in refs:
            continue
        for p, labs in _params128(head):
            if p and re.search(r"(?<![\w.$])%s\.\w" % re.escape(p), body) and not re.search(
                    r"\$\{\s*%s\s*\}|(?<![\w.$])%s(?![\w.])" % (re.escape(p), re.escape(p)), body.replace("(" + p + ".", "")):
                raise CompileError("at %s's definition: the body reads `%s` and never places it: declare the "   # noqa: F821
                                   "reference in the head, `%s((=%s))`" % (n, p, n, body.split(p + ".")[1].split(":")[0].strip()))
    if not refs:
        return e, binds, None
    for n, (head, body, _) in refs.items():                  # line 2: the body reads only what the head lists
        names = [lab for p, labs in _params128(head) if labs for lab, _ in labs]
        for m in re.finditer(r"\(\s*\$?(\w+)\s*:|\$(\w+)", body):
            r_ = m.group(1) or m.group(2)
            if r_ not in names and not s128("s4"):
                raise CompileError("at %s's definition: `%s` is not in the head's list `(%s)`" % (   # noqa: F821
                    n, r_, ", ".join("=" + x for x in names)))
    wd = None
    for n, (head, body, _) in refs.items():
        ps = _params128(head)
        for a, b, args in reversed(_calls128(e, n)):
            out = body
            rest = e[:a] + e[b:]
            for (p, labs), arg in zip(ps, args):
                if not re.fullmatch(r"[A-Za-z_]\w*", arg):
                    raise CompileError("at `%s`: a reference argument names something the caller placed, not a "   # noqa: F821
                                       "pattern" % e[a:b])
                placed = len(re.findall(r"(?<![\w.$(@])%s(?![\w.(])" % re.escape(arg), _pattern_part128(rest)))
                labelled = re.search(r"\[\s*%s\s*=" % re.escape(arg), rest)
                if placed > 1 and not labelled:
                    raise CompileError("at `%s`: `%s` is placed twice: label the uses" % (e[a:b], arg))   # noqa: F821
                src = labelled and re.search(r"\[\s*%s\s*=\s*(\w+)\s*\]" % re.escape(arg), rest)
                ex = _exports128(src.group(1) if src else arg, defs)
                for lab, alab in labs or []:
                    if alab not in ex:
                        raise CompileError("at `%s`: `%s` exports no `%s`, which the head's list needs" % (   # noqa: F821
                            e[a:b], arg, alab))
                    out = re.sub(r"(?<![\w.$])(\$?)%s(?!\w)" % re.escape(lab), r"\g<1>%s.%s" % (arg, alab), out)
                pos = rest.find(arg, a) if not s128("s5") else -1
                if _inside_seq128(e, a) and pos >= a:        # line 3: "at the point of the call"
                    raise CompileError("at `%s`: a read before the match: `%s` is matched after the call" % (   # noqa: F821
                        e[a:b], arg))
            if "weekday_of(" in out:
                wd = out
            e = e[:a] + out + e[b:]
    return e, [x for x in binds if _defs128([x]).keys().isdisjoint(refs)], wd


def _pattern_part128(e):
    """the expression with its conditions and reference calls removed (what is placed)."""
    return re.sub(r"\([^()]*:[^()]*\)", "", e)


def _inside_seq128(e, a):
    """the call stands inside a parenthesised operand of a sequence, not as a top-level `&` operand."""
    depth = 0
    for ch in e[:a]:
        depth += {"(": 1, ")": -1}.get(ch, 0)
    return depth > 0 and " SEQ " in e


# ------------------------------------------------------------------ MINI128 and WDPG128: the weekday run
def mini128(e, binds):
    """a regex built mechanically from a pattern's text: `[x = /rx/]` a named group, `"lit"` escaped, a binding's
    name its body, `SEQ` concatenation; nothing else (the programs it is used on)."""
    defs = _defs128(binds)

    def low(s):
        s = s.strip()
        ps = split111(s, 0, len(s), "SEQ")                   # noqa: F821
        if len(ps) > 1:
            return "".join(low(s[x:y]) for x, y in ps)
        m = re.fullmatch(r"\[\s*(\w+)\s*=\s*(.*)\]", s, re.S)
        if m:
            return "(?P<%s>%s)" % (m.group(1), low(m.group(2)))
        if s.startswith("/") and s.endswith("/"):
            return "(?:%s)" % s[1:-1]
        if s.startswith('"'):
            return re.escape(s[1:-1])
        if s in defs:
            return "(?:%s)" % low(defs[s][1])
        raise ValueError("mini128: " + s)
    return low(e)


MON128 = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def weekday_of128(y, m, d):
    """the STAND-IN for the planned native weekday_of: python's datetime, the month by name."""
    try:
        return datetime.date(int(y), MON128.index(m) + 1, int(d)).strftime("%A")
    except (ValueError, TypeError):
        return None


class WdPg(RePg):                                            # noqa: F821
    """a program whose condition is `(L: == weekday_of($y, $m, $d))`: the regex from MINI128, the test by the
    stand-in on the named groups."""
    def __init__(self, rx, cond):
        super().__init__(rx)
        m = re.fullmatch(r"\(\s*(\w+)\.(\w+)\s*:\s*==\s*weekday_of\(\s*\$(\w+)\.(\w+),\s*\$\w+\.(\w+),\s*\$\w+\.(\w+)\s*\)\s*\)", cond)
        self.l, self.y, self.mo, self.d = m.group(2), m.group(4), m.group(5), m.group(6)

    def _ok(self, m):
        if m is None:
            return False
        w = weekday_of128(m.group(self.y), m.group(self.mo), m.group(self.d))
        return (w != m.group(self.l)) if s128("s6") else (w == m.group(self.l))


def prog(expr, binds=(), **opts):                            # noqa: F811
    if not X128[0]:
        return _PROG112(expr, binds, **opts)
    binds = [re.sub(r"__ref__(\w+)", lambda m: "(%s)" % ", ".join("=" + x for x in m.group(1).split("__")), b_)
             for b_ in binds]                                # a sweep's encoded head read back (_enc_ref128)
    if SENT128[0]:
        defs = _defs128(binds)
        for n, (head, body, _) in defs.items():
            if head and re.search(r"\[\s*(\w+)\s*=\s*\[\s*\w+\s*=\s*\w+\s*\]\s*\]", body) and ":" in head:
                raise CompileError("the path from the sent label passes the body's label and the argument's place "   # noqa: F821
                                   "(sent-over-body-label's other reading)")
    e, binds = _named_list128(expr, binds)
    e, binds, wd = _ref128(e, binds)
    if wd is not None:
        parts = [e[x:y].strip() for x, y in split111(e, 0, len(e), "&")]   # noqa: F821
        return WdPg(mini128(parts[0], binds), parts[1])
    R = _with_new_hits128(_mech_route128, e, binds)
    if R is not None:
        return R
    return _PROG112(e, binds, **opts)


MECHLOG128 = []                                              # (program, read, target) of every read MECHROUTE128 answered


def _mech_route128(e, binds):
    """MECHROUTE128: a read whose walk crosses an argument's place (the reads this lane's rule decides) is answered
    by MECH111, the regex built mechanically from the program text with the walker's target group named, never by
    the loaded engine (whose own path rules predate the place rule: it refuses `Y.a.h` and reads the argument's `d`
    for `Bo.d`). One such read with a digit-range condition `(path: <N)`; anything else stays the engine's."""
    reads = [r for r in reads_of(e) if len(r[0]) >= 2]      # noqa: F821
    if len(reads) != 1:
        return None
    try:
        ew, bw, _ = prep1127(e, binds)                       # noqa: F821
        P = Prog1127(ew, bw)                                 # noqa: F821
    except Exception:                                        # noqa: BLE001
        return None
    path, a, b = reads[0]
    CROSS128.append(False)
    try:
        r = walk1127(P, path)
    except Exception:                                        # noqa: BLE001  a refusal is the engine's to give (FE111)
        return None
    finally:
        crossed = CROSS128.pop()
    if not crossed or r[2] is None:
        return None
    m = re.match(r"\s*:\s*<\s*(\d+)\s*\)", e[b:])
    if not m:
        return None
    tgt = (r[2].tid.split(":")[-1], 1, r[2].name)
    if s128("s10"):
        tgt = (tgt[0], 1, "zz")
    try:
        _PROG112(e, binds)
    except CompileError as x:                                # noqa: F821
        if not re.search(r"is not visible through|not modelled \(predfix88", str(x)):   # the engine's other refusals stand
            raise
    try:
        R = mech(e, binds, target=tgt, cond=(0, int(m.group(1)) - 1))   # noqa: F821
    except Exception:                                        # noqa: BLE001
        return None
    MECHLOG128.append((e, ".".join(path), tgt))
    return R


_HITS128 = re.search(r"`hits\(r\) := (/.*?/)`", NOWS["library.md"])   # noqa: F821  hits-through-hit: the body as printed now
assert "${[(=) = r]}" in _HITS128.group(1), "hits' body carries no list under `hit`"
HITS_OLD128 = _HITS128.group(1).replace("${[(=) = r]}", "${r}")   # the body at START128, answer-identical (MECH128)


HITS_NEW128 = _HITS128.group(1)
LIBMACROS["hits"] = ([("r", None)], HITS_OLD128)           # noqa: F821  the loaded engines answer with the old body
_FE112, _WV112 = fe111, walk_v27                             # noqa: F821  (their own path checks predate a list
#                                                             inside a label-only group); the walker reads the new one


def _with_new_hits128(fn, *a, **k):
    if not X128[0]:
        return fn(*a, **k)
    LIBMACROS["hits"] = ([("r", None)], HITS_NEW128)         # noqa: F821
    try:
        return fn(*a, **k)
    finally:
        LIBMACROS["hits"] = ([("r", None)], HITS_OLD128)     # noqa: F821


def fe111(expr, binds):                                      # noqa: F811
    return _with_new_hits128(_FE112, expr, binds)


def walk_v27(expr, binds, read, reading=None, array=False, old=False):   # noqa: F811
    return _with_new_hits128(_WV112, expr, binds, read, reading, array, old)


# ==== CHECKS128 (a probe loads the model up to this line)
RESULTS.clear()                                              # noqa: F821
AH = "A := /(?<h>\\d)/"
AD = "A := /(?<d>\\d)/"
BP = "B(rx) := /${[p = rx]}xx/"
YB = 'Y := [c = B([a = A])] SEQ "!"'
ISO = 'isodate := [year = /\\d{4}/] SEQ "-" SEQ [month = /\\d\\d/] SEQ "-" SEQ [day = /\\d\\d/]'
B21 = "before2100((=year)) := (year: < 2100)"
NB = "N(rx) := /${[(=h) = rx]}/"
WDN = "wdname := [wd = /[A-Z][a-z]+day/]"
MDY = 'mdy := [month = /[A-Z][a-z]+/] SEQ " " SEQ [day = /\\d{1,2}/] SEQ ", " SEQ [year = /\\d{4}/]'
DN = "day_named((=wd), (=year, =month, =day)) := (wd: == weekday_of($year, $month, $day))"
TX = ["3xx", "7xx", "4xx", "x3xx", "3xxx"]
TXB = ["3xx!", "7xx!", "4xx!", "x3xx!"]
TD = ["7-3", "3-7", "1-2", "7-7", "x3-1", "3-3"]
TW = ["3;7", "7;3", "1;2", "x3;7"]


def unit128(name, what):
    print("== %s: %s" % (name, what))


def same_as(P, rx_, texts):
    """the program's answers (whole, searched, find-all) against a regex written by hand from the ruled sentence."""
    return P is not None and ans11(P, texts) == ans11(RePg(rx_), texts)   # noqa: F821


unit128("CANARY128", "X128 off is predfix112's walker as merged (the control): `B.h` through a label the body writes "
        "on the place legal; X128 on refused, the message naming the rule and the ways in (MSG128)")
X128[0] = False
c0 = run11("B(A) & (B.h: <5)", [AH, BP])                     # noqa: F821
X128[0] = True
c1 = run11("B(A) & (B.h: <5)", [AH, BP])                     # noqa: F821
check("CANARY128", c0[0] is not None and same_as(c0[0], r"[0-4]xx", TX) and c1[0] is None    # noqa: F821
      and "core/labels/rule/argument-place" in (c1[1] or "") and "`A.h`" in (c1[1] or ""),
      "off: %s; on: %s" % ("legal" if c0[0] else c0[1], (c1[1] or "LEGAL")[:150]))

unit128("RULE128", "reads judged by the model's full program builder against hand-filled verdicts, each citing the ruled "
        "line (or the marked lean) it rests on; every legal read's answers against a regex written by hand")
RULE128 = [
    ("B(A) & (B.h: <5)", [AH, BP], ("refused", "argument place"), "the strong lean: a label the body writes passes nothing"),
    ("B(A) & (A.h: <5)", [AH, BP], r"[0-4]xx", "the sender's name, the shorthand (argument-default)"),
    ("B(A) & (B.p: <5)", [AH, BP], r"[0-4]xx", "the body's label itself"),
    ("B(A) & (B.p.h: <5)", [AH, BP], ("refused", "argument place"), "the strong lean"),
    ("B([a = A]) & (B.a.h: <5)", [AH, BP], ("refused", "argument place"), "caller-label-export: the macro's name is the call"),
    ("Y & (Y.a.h: <5)", [AH, BP, YB], r"[0-4]xx!", "caller-label-export: `Y.a.h` legal"),
    ("Y & (Y.c.a.h: <5)", [AH, BP, YB], ("refused", "argument place"), "caller-label-export: `Y.c.a.h` an error"),
    ("Y & (Y.c.h: <5)", [AH, BP, YB], ("refused", "argument place"), "caller-label-export: the call's label"),
    ("Y & (Y.a.h: <5)", [AH, BP, 'Y := [c = B([_a = A])] SEQ "!"'], ("refused", "not visible"), "caller-label-export: `_a` keeps it in"),
    ("X & (X.c.h: <5)", [AH, BP, 'Y := [c = B(A)] SEQ "!"', 'X := [y = Y] SEQ ";"'], ("refused", "argument place"), "stacked-chain moved"),
    ("X & (X.a.h: <5)", [AH, BP, YB, 'X := [y = Y] SEQ ";"'], r"[0-4]xx!;", "caller-label-export: the re-spelling of `X.c.h`"),
    ("[pub = B([A = A])] & (pub.A.h: <5)", [AH, BP], ("refused", "argument place"), "caller-label-export: the call's label"),
    ("[pub = B([A = A])] & (A.h: <5)", [AH, BP], r"[0-4]xx", "the sender's own label"),
    ("X & (X.A.h: <5)", [AH, BP, 'X := [pub = B([A = A])] SEQ "!"'], r"[0-4]xx!", "caller-label-export: written, from a binding that uses the caller"),
    ("X & (X.A.h: <5)", [AH, BP, 'X := [pub = B(A)] SEQ "!"'], ("refused", ""), "shorthand-outside: the shorthand adds no export"),
    ("[n = (P SEQ B(Q))] & (n.B.p.d: <5)", ["P := /(?<d>\\d)/", "Q := /,(?<d>\\d)/", BP], ("refused", "argument place"), "alone-as-middle moved"),
    ("[n = (P SEQ B(Q))] & (Q.d: <5)", ["P := /(?<d>\\d)/", "Q := /,(?<d>\\d)/", BP], r"\d,[0-4]xx", "the sender's name"),
    ("B(A) & (B.p.d: <5)", [AD, "B(rx) := /${[p = rx]}-(?<d>\\d)/"], ("refused", "argument place"), "closed-argument moved"),
    ("B(A) & (B.d: <5)", [AD, "B(rx) := /${[p = rx]}-(?<d>\\d)/"], r"\d-[0-4]", "body-own-name: the body's own beside the place"),
    ("identity(A) & (identity.h: <5)", [AH, "identity(x) := /${[(=) = x]}/"], r"[0-4]", "carve-out-reading: the door"),
    ("identity([a = A]) & (identity.a.h: <5)", [AH, "identity(x) := /${[(=) = x]}/"], r"[0-4]", "the door, a path through it"),
    ('W(/(?<h>\\d)/, /;(?<e>\\d)/) & (W.h: <5)', ["W(a, b) := [(=) = a] SEQ [(=) = b]"], r"[0-4];\d", "the door: one argument sets it"),
    ('W(/(?<h>\\d)/, /;(?<h>\\d)/) & (W.h: "3")', ["W(a, b) := [(=) = a] SEQ [(=) = b]"], ("refused", "2 labels `h`"), "the door: one-path counts (not \"own\")"),
    ("Bo(Ad) & (Bo.d: <5)", ["Ad := /(?<d>\\d)/", "Bo(rx) := /(?<d>\\d)-${[(=) = rx]}/"], r"[0-4]-\d", "the door with body-own-name: the body's own"),
    ("B2(A) & (B2.p.h: <5)", [AH, "B2(rx) := /${[p = [(=) = rx]]}xx/"], r"[0-4]xx", "the list under the body's label"),
    ("B2(A) & (B2.h: <5)", [AH, "B2(rx) := /${[p = [(=) = rx]]}xx/"], r"[0-4]xx", "the list under the body's label, skipped"),
    ('hits(/a(?<g>x)?/) & (hits.hit.g: "x")', [], None, "hits-through-hit: legal with the list under `hit`"),
    ("[n = (P SEQ /,(?<d>\\d)/)] & (n.d: <5)", ["P := /(?<d>\\d)/"], r"\d,[0-4]", "gate-beside-direct: legal"),
]
if s128("s7"):
    RULE128[1] = (RULE128[1][0], RULE128[1][1], ("refused", "argument place"), RULE128[1][3])
TEXTS128 = {"Y & ": TXB, "X & (X.a.h": [t_ + ";" for t_ in TXB], "X & (X.A.h": TXB, "[n = (P SEQ B(Q))]": ["7,3xx", "3,7xx", "4,1xx"],
            "B(A) & (B.d": TD, "B(A) & (B.p.d": TD, "identity": ["3", "7", "4"], "W(": TW, "Bo(": TD,
            "[n = (P SEQ /,": ["7,3", "3,7", "1,2"]}
r_bad, r_leg = [], 0
for e_, b_, want, why in RULE128:
    P_, err_ = run11(e_, b_)                                 # noqa: F821
    texts = next((v for k, v in TEXTS128.items() if e_.startswith(k)), None) or TX
    if isinstance(want, tuple):
        ok_ = P_ is None and want[1] in (err_ or "") and not (err_ or "").startswith("CRASH")
        got = (err_ or "LEGAL")[:150]
    elif want is None:
        ok_ = P_ is not None
        got = "legal" if P_ else err_
    else:
        ok_ = same_as(P_, want, texts)
        r_leg += 1
        got = "legal, %s the hand regex `%s`" % ("equal to" if ok_ else "NOT equal to", want) if P_ else err_
    if not ok_:
        r_bad.append((e_, got))
    print("   %-58s %s | %s" % (e_[:58], why, got[:130]))
check("RULE128", not r_bad and r_leg >= 15, "%d reads (%d legal against hand regexes); not as the ruling says: %s" % (   # noqa: F821
    len(RULE128), r_leg, r_bad or "none"))

unit128("READINGS128", "the manager's readings in the record entries this lane folds, each RUN")
rdg = {}
X128[0] = False
old_xc = run11("X & (X.c.h: <5)", [AH, BP, 'Y := [c = B(A)] SEQ "!"', 'X := [y = Y] SEQ ";"'])[0]   # noqa: F821
X128[0] = True
new_xa = run11("X & (X.a.h: <5)", [AH, BP, YB, 'X := [y = Y] SEQ ";"'])[0]   # noqa: F821
T3 = [t_ + ";" for t_ in TXB]
rdg["stacked-chain's `X.c.h` re-spelled by Y labelling the argument, `X.a.h`, the old answers"] = (
    old_xc is not None and new_xa is not None and ans11(old_xc, T3) == ans11(new_xa, T3), "control `X.c.h` vs `X.a.h`")   # noqa: F821
pw = run11("[pub = B([A = A])] & (pub.A.h: <5)", [AH, BP])   # noqa: F821
xw = run11("X & (X.A.h: <5)", [AH, BP, 'X := [pub = B([A = A])] SEQ "!"'])   # noqa: F821
xi = run11("X & (X.A.h: <5)", [AH, BP, 'X := [pub = B(A)] SEQ "!"'])   # noqa: F821
rdg["shorthand-outside's contrast in its old form, `pub.A.h` written out, is REFUSED by caller-label-export's asked words (so the manager's reading holds only in the moved form below)"] = (
    pw[0] is None, "`pub.A.h` written out: %s" % ("refused" if pw[0] is None else "legal"))
rdg["the contrast, moved: from a binding that uses the caller, written legal, the shorthand refused"] = (
    xw[0] is not None and xi[0] is None, "written %s / shorthand %s" % ("legal" if xw[0] else xw[1], (xi[1] or "LEGAL")[:60]))
b1 = run11("Bo(Ad) & (Bo.d: <5)", ["Ad := /(?<d>\\d)/", "Bo(rx) := /(?<d>\\d)-${[(=) = rx]}/"])[0]   # noqa: F821
b2 = run11("Bo(Ad) & (Bo.d: <5)", ["Ad := /(?<d>\\d)/", "Bo(rx) := /(?<d>\\d)-${[(=, _ = d) = rx]}/"])[0]   # noqa: F821
rdg["carve-out-reading's observation: the remedy `[(=, _ = d) = rx]` is available today, the same answers (the door reads the body's own anyway)"] = (
    b1 is not None and b2 is not None and ans11(b1, TD) == ans11(b2, TD), "with and without the remedy")   # noqa: F821
X128[0] = False
h_old = run11('hits(/a(?<g>x)?/) & (hits.hit.g: "x")', [])[0]   # noqa: F821
X128[0] = True
h_new = run11('hits(/a(?<g>x)?/) & (hits.hit.g: "x")', [])[0]   # noqa: F821
HITS_NEW128, _hn = HITS_OLD128, HITS_NEW128
h_nolist = walk_v27('hits(/a(?<g>x)?/) & (hits.hit.g: "x")', [], "hits.hit.g")
HITS_NEW128 = _hn
TH = ["aax", "axa", "ax", "a"]
rdg["hits-through-hit (the manager's call): the list under `hit` keeps `hits.hit.g` legal, its answers; without it refused"] = (
    h_old is not None and h_new is not None and ans11(h_old, TH) == ans11(h_new, TH) and h_nolist[0] == "refused",   # noqa: F821
    "without the list: %s" % (h_nolist[1][:80] if h_nolist[0] == "refused" else h_nolist[0]))
wf = run11('wdname SEQ " " SEQ mdy & day_named(wdname, mdy)', [WDN, MDY, DN])   # noqa: F821
ws_ = run11('(wdname & day_named(wdname, mdy)) SEQ " " SEQ mdy', [WDN, MDY, DN])   # noqa: F821
rdg["param-reference: \"at the point of the call\": a filter over the whole legal, the call at the weekday's own spot \"a read before the match\""] = (
    wf[0] is not None and ws_[0] is None and "a read before the match" in (ws_[1] or ""), "filter %s / own spot %s" % (
        "legal" if wf[0] else wf[1], (ws_[1] or "LEGAL")[:70]))
ck = run11("checked(isodate)", ["checked(B) := B & (B.year: < 2100)", ISO])   # noqa: F821
iso = run11("isodate & (isodate.year: < 2100)", [ISO])[0]   # noqa: F821
TI = ["2024-02-29", "2150-01-01", "1999-12-31"]
print("   param-reference example 3, `checked(B) := B & (B.year: < 2100)`, as the model reads it: %s; the reading 'legal' "
      "answers as `isodate & (isodate.year: < 2100)`: %s" % ((ck[1] or "LEGAL")[:100], fmt(iso, TI, " ".join(TI), " ".join(TI))))   # noqa: F821
rdg["param-reference example 3 (`checked`) NOT FOLDED: both readings run (the line above), listed for him"] = (iso is not None, "run")
for k_, (ok_, why_) in rdg.items():
    print("   %s: %s (%s)" % (k_, "SUPPORTED" if ok_ else "NOT SUPPORTED", why_))
check("READINGS128", all(v[0] for v in rdg.values()) and not s128("s8"), "%d readings run, %d as stated" % (   # noqa: F821
    len(rdg), sum(1 for v in rdg.values() if v[0])))

unit128("OPEN128", "the three unasked questions, each reading RUN: the printed one (the study's lean) and the other")
op = []
B1 = "B1(rx) := /${[(=) = [p = rx]]}xx/"
MX = ["Mx(r) := /<${[(=) = L2(r)]}>/", "L2(x) := /${[(=) = x]}/"]
RS = "Rs(l:, v) := /${[l = [p = v]]}xx/"
for nm_, e_, b_, mode_, want_, texts in [
        ("list-over-label, printed (A)", "B1(A) & (B1.h: <5)", [AH, B1], "A", None, TX),
        ("list-over-label, the other (A2)", "B1(A) & (B1.h: <5)", [AH, B1], "A2", r"[0-4]xx", TX),
        ("list-over-label, `B1.p` in both", "B1(A) & (B1.p: <5)", [AH, B1], "A", r"[0-4]xx", TX),
        ("forwarded-place, printed (A)", "Mx(A) & (Mx.h: <5)", [AH] + MX, "A", r"<[0-4]>", ["<3>", "<7>", "<4>"]),
        ("forwarded-place, the other (A0)", "Mx(A) & (Mx.h: <5)", [AH] + MX, "A0", None, ["<3>"]),
        ("sent-over-body-label, printed", "Rs(x:, A) & (x.h: <5)", [AH, RS], "A", r"[0-4]xx", TX),
        ("sent-over-body-label, the other (SENT128)", "Rs(x:, A) & (x.h: <5)", [AH, RS], "SENT", None, TX)]:
    MODE128[0] = "A" if mode_ == "SENT" else mode_
    SENT128[0] = mode_ == "SENT"
    P_, err_ = run11(e_, b_)                                 # noqa: F821
    MODE128[0], SENT128[0] = "A", False
    ok_ = (P_ is None) if want_ is None else same_as(P_, want_, texts)
    if s128("s9") and nm_.startswith("forwarded-place, printed"):
        ok_ = P_ is None
    print("   %-44s %s%s" % (nm_, "refused: " + (err_ or "")[:90] if P_ is None else "legal ", "" if P_ is None else
                              fmt(P_, texts[:2], " ".join(texts[1::-1]), " ".join(texts[:3]))))   # noqa: F821
    op.append((nm_, ok_))
check("OPEN128", all(o[1] for o in op), "%d runs, as each reading says: %s" % (len(op), [o[0] for o in op if not o[1]] or "all"))   # noqa: F821

unit128("NAMED128", "named-list-use: the use error at the call (and through a forwarding body), the twice-set argument "
        "legal (the last), the never-satisfiable body at its definition; each message names the label and the list")
nm_bad = []
for e_, b_, want_, texts in [
        ("N(A) & (N.h: <5)", [AH, NB], r"[0-4]", ["3", "7", "4"]),
        ("N(Ae) & (N.h: <5)", ["Ae := /(?<e>\\d)/", NB], ("at `N(Ae)`", "`h`", "(=h)"), None),
        ("N(A2) & (N.h: <5)", ["A2 := /(?<h>\\d)(?<h>\\d)/", NB], r"\d[0-4]", ["37", "73", "44"]),
        ("N(Aw) & (N.h: <5)", ["Aw := [_w = /(?<h>\\d)/]", NB], ("at `N(Aw)`", "`h`", "(=h)"), None),
        ("M(Ae) & (M.h: <5)", ["Ae := /(?<e>\\d)/", "M(r) := /<${[(=) = N(r)]}>/", NB], ("at `M(Ae)`", "through M's place", "(=h)"), None),
        ("M2(A)", [AH, "M2(r) := /<${N([q = r])}>/", NB], ("at M2's definition", "`h`", "(=h)"), None)]:
    P_, err_ = run11(e_, b_)                                 # noqa: F821
    ok_ = same_as(P_, want_, texts) if isinstance(want_, str) else (P_ is None and all(w in (err_ or "") for w in want_))
    print("   %-24s %s" % (e_, "legal, %s the hand regex" % ("equal to" if ok_ else "NOT equal to") if P_ else (err_ or "")[:120]))
    if not ok_:
        nm_bad.append(e_)
check("NAMED128", not nm_bad, "6 programs; not as ruled: %s" % (nm_bad or "none"))   # noqa: F821

unit128("REF128", "param-reference: declared heads, the definition errors (lines 2, 4), the call errors (line 3), the "
        "expansion's answers against hand regexes; the weekday by the stand-in (WEEKDAY128 below)")
rf_bad = []
ISORX = r"(?P<y>\d{4})-\d\d-\d\d"
for e_, b_, want_ in [
        ("isodate & before2100(isodate)", [B21, ISO], ("rx", r"(?:20\d\d|1\d\d\d|0\d\d\d)-\d\d-\d\d")),
        ("isodate & jan(isodate)", ['jan((=year)) := (month: "01")', ISO], ("err", "not in the head's list")),
        ("isodate & A(isodate)", ["A(B) := (B.year: < 2100)", ISO], ("err", "declare the reference in the head")),
        ("/(?<year>\\d{4})/ & before2100(/(?<year>\\d{4})/)", [B21], ("err", "not a pattern")),
        ("yr & before2100(yr)", ["yr := /(?<y>\\d{4})/", B21], ("err", "exports no `year`")),
        ('isodate SEQ " " SEQ isodate & before2100(isodate)', [B21, ISO], ("err", "placed twice")),
        ('(wdname & day_named(wdname, mdy)) SEQ " " SEQ mdy', [WDN, MDY, DN], ("err", "a read before the match"))]:
    P_, err_ = run11(e_, b_)                                 # noqa: F821
    if want_[0] == "rx":
        ok_ = same_as(P_, want_[1], ["2024-02-29", "2150-01-01", "1999-12-31", "x 2150-01-01 1999-12-31"])
    else:
        ok_ = P_ is None and want_[1] in (err_ or "")
    print("   %-52s %s" % (e_[:52], "legal, %s the hand regex" % ("equal to" if ok_ else "NOT equal to") if P_ else (err_ or "")[:110]))
    if not ok_:
        rf_bad.append(e_)
check("REF128", not rf_bad, "7 programs; not as ruled: %s" % (rf_bad or "none"))   # noqa: F821

unit128("WEEKDAY128", "his question \"Wednesday June 12, 1994\": the filter over the whole, by the stand-in, against "
        "weekday.py's committed answers (the manager's run: a different program text and regex; both use python's "
        "datetime, the stand-in by design) and the calendar fact June 12, 1994 was a Sunday")
WDT = ["Wednesday June 12, 1994", "Sunday June 12, 1994", "Wednesday June 15, 1994"]
WDS = "Wednesday June 12, 1994; Sunday June 12, 1994; Wednesday June 15, 1994"
Pw = run11('wdname SEQ " " SEQ mdy & day_named(wdname, mdy)', [WDN, MDY, DN])[0]   # noqa: F821
wout = builtins.open(os.path.join(LANES128, "predbang_evidence", "weekday.out"), encoding="utf-8").read()
got_w = [Pw.whole(t_) for t_ in WDT] if Pw else []
fa_w = Pw.findall(WDS) if Pw else []
ok_w = (Pw is not None and got_w == [False, True, True] and [f"{a}@{b}" for a, b in fa_w] ==
        ["Sunday June 12, 1994@25", "Wednesday June 15, 1994@47"] and "June 12, 1994 was a Sunday" in wout
        and "Sunday June 12, 1994@25" in wout and "Wednesday June 15, 1994@47" in wout)
if Pw:
    print("   " + fmt(Pw, WDT, WDS, WDS))                    # noqa: F821
check("WEEKDAY128", ok_w, "whole %s, find-all %s (weekday.out agrees: %s)" % (got_w, fa_w, "June 12, 1994 was a Sunday" in wout))   # noqa: F821

unit128("TABLE128", "the kinds table's three rows this lane writes (an argument's place, the shorthand, a label the "
        "caller writes), their cells read as text, against the walker's runs (two sources: the table's words, the walker)")
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
if s128("s11"):
    D8["core.md"] = D8["core.md"].replace("| passed only through a list on it, a node between", "| always passed, a node between", 1)   # noqa: F821
kp128 = piece8("core/labels/rule/kinds")                     # noqa: F821
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
rows128 = {}
for L_ in kp128.split("\n"):
    L_ = L_.strip()
    if L_.startswith("| ") and not L_.startswith(("| the kind", "|---")):
        cells = [c.strip() for c in L_.strip("|").split(" | ")]
        rows128[re.sub(r"\s*\(.*$|\s*`.*$", "", cells[0]).strip()] = cells


def _legal128(e, b, r):
    return walk_v27(e, b, r)[0] == "legal"


tb_bad = []
pl = rows128.get("an argument's place", [""] * 6)
tb = [("place, skippable: only through a list", pl[3].startswith("passed only through a list"),
       not _legal128("B(A) & (B.h: <5)", [AH, BP], "B.h") and _legal128("identity(A) & (identity.h: <5)", [AH, "identity(x) := /${[(=) = x]}/"], "identity.h")),
      ("place, outside: a wall but the sender's names", pl[4].startswith("no: a wall"),
       not _legal128("Y & (Y.c.h: <5)", [AH, BP, YB], "Y.c.h") and _legal128("Y & (Y.a.h: <5)", [AH, BP, YB], "Y.a.h")),
      ("place, exported: a label the body writes passes nothing", "passes nothing" in pl[5],
       not _legal128("B(A) & (B.p.h: <5)", [AH, BP], "B.p.h"))]
sh = rows128.get("an argument's shorthand label", [""] * 6)
tb.append(("shorthand, skippable: no", sh[3].startswith("no"),
           not _legal128('X & (X.A.h: <5)', [AH, BP, 'X := [pub = B(A)] SEQ "!"'], "X.A.h")))
cl = rows128.get("a label the caller writes in an argument", [""] * 6)
tb.append(("caller's label, outside: by its own name, never through the call", cl[4].startswith("yes, by its own name"),
           _legal128("Y & (Y.a.h: <5)", [AH, BP, YB], "Y.a.h") and not _legal128("Y & (Y.c.a.h: <5)", [AH, BP, YB], "Y.c.a.h")))
tb.append(("caller's label, exported: an underscore label keeps it in", "underscore label keeps it in" in cl[5],
           not _legal128("Y & (Y.a.h: <5)", [AH, BP, 'Y := [c = B([_a = A])] SEQ "!"'], "Y.a.h")))
for nm_, doc_, run_ in tb:
    print("   %-62s the table says %s, the walker %s" % (nm_, doc_, run_))
    if doc_ is not True or run_ is not True:
        tb_bad.append(nm_)
check("TABLE128", len(rows128) >= 12 and not tb_bad, "%d rows read, %d cells against runs; differing: %s" % (   # noqa: F821
    len(rows128), len(tb), tb_bad or "none"))

unit128("SWEEP128", "every printed three-mode line RUN under this model; the starting commit %s's lines under the "
        "control (X128 off: predfix112's walker and engine) against these, keyed by the program; every key gone or "
        "moved DECLARED" % START128)
exec(compile(_src11[_src11.index("def sw11(docs):"):_src11.index("def key11(k):")], P1125, "exec"), globals())   # noqa: S102,F821
exec(compile(_src111[_src111.index("_sweep_one11, _modes_of11, _fmt11 = "):_src111.index("OLD111 = {")], P111, "exec"),   # noqa: S102,F821
     globals())
exec(compile(_src9[_src9.index("def err_lines(docs"):_src9.index("es_now = err_lines(D8)")], P1124, "exec"),   # noqa: S102,F821
     globals())
exec(compile(_src111[_src111.index("MSG111 = {"):_src111.index("}\n", _src111.index("MSG111 = {")) + 2], P111, "exec"),   # noqa: S102,F821
     globals())
exec(compile(_src1127[_src1127.index("MSG1127 = dict(MSG111)"):_src1127.index("es_bad, es_msg = [], []", _src1127.index("MSG1127 = dict(MSG111)"))], P1127, "exec"),   # noqa: S102,F821
     globals())
exec(compile(_src112[_src112.index("MSG112 = dict(MSG1127)"):_src112.index("es_bad, es_msg = [], []", _src112.index("MSG112 = dict(MSG1127)"))], P112, "exec"),   # noqa: S102
     globals())
_SWEEP_ONE112 = sweep_one                                    # noqa: F821


def _enc_ref128(tail):
    """a printed head with a declared reference, `before2100((=year))`, in a spelling the inherited sweep's binding
    reader takes (one level of parentheses): `before2100(__ref__year)`; prog reads it back (REF128)."""
    def one(m):
        inner = m.group(2)
        out, depth, cur = [], 0, ""
        for ch in inner:
            depth += {"(": 1, ")": -1}.get(ch, 0)
            if ch == "," and depth == 0:
                out.append(cur.strip())
                cur = ""
            else:
                cur += ch
        out.append(cur.strip())
        return "%s(%s) :=" % (m.group(1), ", ".join(
            "__ref__" + "__".join(x.strip().lstrip("=") for x in p[1:-1].split(",")) if p.startswith("(") else p for p in out))
    return re.sub(r"(\w+)\(((?:[^()]|\([^()]*\))*\([^()]*\)(?:[^()]|\([^()]*\))*)\) :=", one, tail)


def sweep_one(line_, a, pt, tail):                           # noqa: F811
    return _SWEEP_ONE112(line_, a, pt, _enc_ref128(tail))


OLD128 = {f_: _git8("docs/design/predicates/" + f_, START128) for f_ in DOCF}   # noqa: F821
X128[0] = False
OLD_T128 = sw11(OLD128)                                      # noqa: F821
X128[0] = True
NOWS128 = dict(NOWS)                                         # noqa: F821
if s128("s12"):
    NOWS["core.md"] = NOWS["core.md"].replace("Through a call, the sender's name: WHOLE `3xx` HOLDS", "Through a call, the sender's name: WHOLE `3xx` FAILS", 1)   # noqa: F821
NEW_T128 = sw11(NOWS)                                        # noqa: F821
NOWS.update(NOWS128)                                         # noqa: F821
LEAN128 = "the strong lean no-path-through-argument (marked), "
GONE128 = {                                                  # a printed line whose program this fold moved: key -> why
    "B(A) & (B.h: <5)": LEAN128 + "core/labels/rule/paths: a compile error now; the read `A.h`, the same answers "
                        "(core/labels/rule/argument-place, the line \"Through a call, the sender's name\")",
    "X & (X.c.h: <5)": LEAN128 + "and caller-label-export: a compile error now; re-spelled by Y labelling the argument, "
                       "`X.a.h`, the same answers (READINGS128)",
    "[n = (P SEQ B(Q))] & (n.B.p.d: <5)": LEAN128 + "a compile error now; the read `Q.d`, the same answers",
    "B(A) & (B.p.d: <5)": LEAN128 + "a compile error now; the read `A.d`",
    "[pub = B([A = A])] & (pub.A.h: <5)": LEAN128 + "and caller-label-export (\"only the path through the call's own "
                                          "label\" is an error): a compile error now; `A.h`, or `X.A.h` from a binding "
                                          "that uses the caller",
    "B(A) & (B.dd.d: <100)": LEAN128 + "a compile error now (argument-default and nested-scope); the read `A.d`",
    "C := B(A) & (B.dd.d: <100)": LEAN128 + "nested-scope's example 1, a compile error now (missed by the study's census)",
}
MOVED128 = {}
inh = set((k_, f_, st_) for k_, vs in OLD_T128.items() for f_, _, st_, _, _ in vs if st_ != "same")
sw_bad, sw_moved, sw_gone, sw_new, sw_inh, cnt, used = [], [], [], [], [], {}, set()
for k_, vs in NEW_T128.items():
    for f_, ln_, st_, got_, pr_ in vs:
        cnt[st_] = cnt.get(st_, 0) + 1
        if st_ != "same":
            (sw_inh if (k_, f_, st_) in inh else sw_bad).append((f_, ln_, st_, k_[0], got_[:160]))
for k_, vs0 in OLD_T128.items():
    for f0 in sorted(set(v_[0] for v_ in vs0)):
        vs = [v_ for v_ in vs0 if v_[0] == f0]
        nk = [v_ for v_ in NEW_T128.get(k_, []) if v_[0] == f0]
        if nk:
            po, pn = sorted(set(v_[4] for v_ in vs)), sorted(set(v_[4] for v_ in nk))
            if po != pn:
                if k_[0] in MOVED128:
                    used.add(k_[0])
                    print("   MOVED BY A RULING %s `%s`: %s" % (f0, k_[0], MOVED128[k_[0]]))
                else:
                    sw_moved.append((f0, k_[0], " || ".join(po)[:200], " || ".join(pn)[:200]))
            continue
        if k_[0] in GONE128:
            used.add(k_[0])
            print("   DROPPED OR MOVED BY A RULING %s:%d `%s`: %s" % (vs[0][0], vs[0][1], k_[0], GONE128[k_[0]]))
            continue
        sw_gone.append((vs[0][0], vs[0][1], k_[0], vs[0][2]))
stale = sorted(k_ for k_ in list(GONE128) + list(MOVED128) if k_ not in used)
for k_, vs in NEW_T128.items():
    if k_ not in OLD_T128:
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
check("SWEEP128", OLD_T128 and not sw_bad and not sw_moved and not sw_gone and not stale,   # noqa: F821
      "%d printed lines now (%s), %d keys at the starting commit; not same and not inherited %d (inherited %d); "
      "moved %d; gone %d; declared %d; added %d; stale %d" % (
          sum(len(v) for v in NEW_T128.values()), ", ".join("%s %d" % kv for kv in sorted(cnt.items())),
          len(OLD_T128), len(sw_bad), len(sw_inh), len(sw_moved), len(sw_gone), len(GONE128) + len(MOVED128),
          len(sw_new), len(stale)))

unit128("ERRSWEEP128", "every printed compile-error line of the base files refused under this model, no crash; each "
        "named form in the refusal's message (MSG112's rows less the reads now legal, and this lane's)")
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
if s128("s13"):
    D8["core.md"] = D8["core.md"].replace("Through a call, past the body's label: modes: a compile error (`B(A) & (B.p.h: <5)`",
                                          "Through a call, past the body's label: modes: a compile error (`B(A) & (B.p: <5)`", 1)   # noqa: F821
es_now = [x_ for x_ in err_lines({f_: _enc_ref128(v_) for f_, v_ in D8.items()}) if not x_[0].endswith("_details.md")]   # noqa: F821
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
MSG128 = dict(MSG112)                                        # noqa: F821
MSG128.pop("[n = (P SEQ B(Q))] & (n.d: <5)")                 # `n.B.d` passes B's place now: the message names `n.P.d`
MSG128.update({
    "B(A) & (B.p.h: <5)": "argument-place",
    "B([a = A]) & (B.a.h: <5)": "argument-place",
    "isodate & jan(isodate)": "`month`",
    "isodate & A(isodate)": "`A((=year))`",
    "yr & before2100(yr)": "`year`",
    "isodate SEQ \" \" SEQ isodate & before2100(isodate)": "placed twice",
    "(wdname & day_named(wdname, mdy)) SEQ \" \" SEQ mdy": "a read before the match",
})
es_bad, es_msg = [], []
for f_, ln_, e_, b_ in es_now:
    Pg, err = run11(e_, b_)                                  # noqa: F821
    if Pg is not None or (err or "").startswith("CRASH"):
        es_bad.append((f_, ln_, e_, "legal" if Pg is not None else err[:100]))
    elif e_ in MSG128 and MSG128[e_] not in err:
        es_msg.append((f_, ln_, e_, MSG128[e_], err[:140]))
for x_ in es_bad:
    print("   BAD (printed a compile error, runs legal or crashes) %s" % (x_,))
for x_ in es_msg:
    print("   MESSAGE %s:%d `%s` lacks %s: %s" % x_)
msg_unseen = sorted(set(MSG128) - set(e_ for _, _, e_, _ in es_now))
check("ERRSWEEP128", es_now and not es_bad and not es_msg and not msg_unseen,   # noqa: F821
      "%d compile-error lines read, each refused with no crash: bad %s; named form missing %s; message rows with no "
      "line %s" % (len(es_now), es_bad or "none", es_msg or "none", msg_unseen or "none"))

unit128("SPECLINES128", "every printed line new in this lane (not in its file at the starting commit) is RUN: a "
        "three-mode line SAME as run, a compile-error line refused")
newset = {f_: set(NOWS[f_].split("\n")) - set(OLD128[f_].split("\n")) for f_ in BASES11}   # noqa: F821
nl3, nle, nl_bad = 0, 0, []
for k_, vs in NEW_T128.items():
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
nl_lines = [(f_, L_) for f_ in BASES11 for L_ in newset[f_] if re.search(r"WHOLE `|modes: a compile error", L_)]   # noqa: F821
nl_all = len(nl_lines)
if s128("s14"):
    nl_all += 1
check("SPECLINES128", not nl_bad and nl3 + nle == nl_all, "%d new printed lines: three-mode %d, compile-error %d, "   # noqa: F821
      "unread %d; not as printed: %s" % (nl_all, nl3, nle, nl_all - nl3 - nle, nl_bad or "none"))

unit128("STALE128", "the base files, continuation lines joined, hold none of the texts this fold retires; the "
        "withdrawn clause printed nowhere in the six files")
STALE128 = [
    (r"in which case they count as the body's own labels", "the withdrawn clause (carve-out-reading)"),
    (r"count as the body's own labels", "the withdrawn clause (carve-out-reading)"),
    (r"\(\?<:hit>\$\{r\}\)", "hits-through-hit: the body carries the list"),
    (r"\(\?<:hit>\$\{x\}\)", "hits-through-hit: occurrences' body carries the list"),
    (r"A named list on a spot: modes: a compile error", "named-list-use: legal"),
    (r"open gate-beside-direct|owner question gate-beside-direct", "gate-beside-direct ruled"),
    (r"open caller-label-export|open carve-out-reading|open named-list-use|open param-reference", "ruled"),
]
if s128("s15"):
    STALE128.append((r"Through a call, the sender's name", "planted"))
joined = {f_: re.sub(r"\n  +", " ", NOWS[f_]) for f_ in DOCF}   # noqa: F821
st_hits = [(f_, rx_, why) for rx_, why in STALE128 for f_ in (DOCF if "count as" in rx_ else BASES11)   # noqa: F821
           if re.search(rx_, joined[f_], re.M)]
for x_ in st_hits:
    print("   STALE %s `%s` (%s)" % x_)
check("STALE128", not st_hits, "%d retired texts searched; found %s" % (len(STALE128), st_hits or "none"))   # noqa: F821

unit128("MARK128", "the strong lean's mark: its exact phrase at every site, counted; the home piece open under its "
        "slug; every line this lane moved to a compile error by the lean carries it")
mk = {f_: NOWS[f_].count(MARK128) for f_ in BASES11}         # noqa: F821
home = piece8("core/labels/rule/argument-place")             # noqa: F821
home_ok = "open no-path-through-argument" in home.split("\n")[0] and MARK128 in home
LEANERR128 = ["`B(A) & (B.h: <5)`", "`[n = (P SEQ B(Q))] & (n.B.p.d: <5)`", "`X & (X.c.h: <5)`", "`B(A) & (B.p.d: <5)`",
              "`[pub = B([A = A])] & (pub.A.h: <5)`", "`B(A) & (B.dd.d: <100)`", "`C := B(A) & (B.dd.d: <100)`"]
if s128("s16"):
    LEANERR128.append("`B(A) & (B.zz: <5)`")
unmarked = []
for p_ in LEANERR128:
    ls_ = [L_ for f_ in BASES11 for L_ in NOWS[f_].split("\n") if "modes: a compile error (" + p_ in L_]   # noqa: F821
    if not ls_ or any(MARK128 not in L_ for L_ in ls_):
        unmarked.append(p_)
bad_phr = [f_ for f_ in BASES11 if re.search(r"the owner's strong lean(?!, entailed by carve-out-reading and caller-label-export; to be confirmed)", NOWS[f_])]   # noqa: F821
check("MARK128", home_ok and not unmarked and not bad_phr and sum(mk.values()) >= len(LEANERR128),   # noqa: F821
      "%d marked sites (%s); home piece open and marked: %s; moved lines unmarked or missing: %s; a variant phrase: %s" % (
          sum(mk.values()), ", ".join("%s %d" % kv for kv in sorted(mk.items())), home_ok, unmarked or "none", bad_phr or "none"))

unit128("MECH128", "every read MECHROUTE128 answered (MECH111 with the walker's target), where the control engine "
        "(X128 off, predfix112 as merged) also reads it legal and to the same group, answers equal: a second source")
mlog = sorted(set(MECHLOG128))
mc_bad, mc_n = [], 0
CTRL128 = [("identity(A) & (identity.h: <5)", [AH, "identity(x) := /${[(=) = x]}/"], ["3", "7", "4"]),
           ("B2(A) & (B2.h: <5)", [AH, "B2(rx) := /${[p = [(=) = rx]]}xx/"], TX),
           ('W(/(?<h>\\d)/, /;(?<e>\\d)/) & (W.h: <5)', ["W(a, b) := [(=) = a] SEQ [(=) = b]"], TW)]
for e_, b_, texts in CTRL128:
    del MECHLOG128[:]
    P_, err_ = run11(e_, b_)                                 # noqa: F821
    routed = bool(MECHLOG128)
    X128[0] = False
    Q_, qerr_ = run11(e_, b_)                                # noqa: F821
    X128[0] = True
    same = P_ is not None and Q_ is not None and ans11(P_, texts) == ans11(Q_, texts)   # noqa: F821
    mc_n += routed
    print("   %-46s routed %s; MECH111 %s the control engine" % (e_[:46], routed, "equal to" if same else "NOT equal to"))
    if not routed or not same:
        mc_bad.append(e_)
for x_ in mlog:
    print("   ROUTED %s  read %s  target %s" % x_)
check("MECH128", not mc_bad and len(mlog) >= 5, "%d distinct reads routed over the run so far; %d controls routed and "   # noqa: F821
      "equal; not: %s" % (len(mlog), mc_n, mc_bad or "none"))

unit128("QUOTES128", "the owner's words this lane quotes, each in the record at the PINNED starting commit and in its "
        "piece; every record title a predfold1128 item cites is a title of that record")
REC128 = _git8("docs/design/plan_row_bodies/COND-FAMILY.md", START128)   # noqa: F821
QQ128 = [
    ("carve-out-reading: agree with lean", "core/labels/rule/argument-door"),
    ("a body's export list opens a door through the argument's place.", "core/labels/rule/argument-door"),
    ("caller-label-export: agree first read. If they didn't want to export use _a label.", "core/labels/rule/caller-label"),
    ("named-list-use: agree use it.", "core/labels/export/named-list"),
    ("param-reference: yes all four", "core/operators/bindings/reference"),
    ("I dislike the secret change from pattern to reference.", "core/operators/bindings/reference"),
    ("let's do a strong lean yes with your carve out for exported labels.", "core/labels/rule/argument-place"),
    ("Could you use it to match the Wednesday via day of the week.", "core/operators/bindings/reference-call"),
]
if s128("s17"):
    QQ128.append(("carve-out-reading: disagree", "core/labels/rule/argument-door"))
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
q_miss = [(q_[:50], t_) for q_, t_ in QQ128 if ws(q_) not in ws(REC128) or ws(q_) not in ws(piece8(t_))]   # noqa: F821
DET128 = NOWS["core_details.md"] + NOWS["library_details.md"] + NOWS["parked_details.md"]   # noqa: F821
DOLD128 = set((OLD128["core_details.md"] + OLD128["library_details.md"] + OLD128["parked_details.md"]).split("\n"))
cited = sorted(set(m_.group(1) for l_ in DET128.split("\n") if l_ not in DOLD128
                   for m_ in re.finditer(r'\(record:\s*"(.+?)"\)(?=[;,.:\s]|$)', l_)))
heads = [ws(h_) for h_ in re.findall(r"^#{2,3} (.*)$", REC128, re.M)]   # noqa: F821
t_miss = [t_[:80] for t_ in cited if not any(h_.rstrip(".") == ws(t_) or h_.startswith(ws(t_) + " (") for h_ in heads)]   # noqa: F821
check("QUOTES128", not q_miss and not t_miss and cited, "%d quoted sentences (missing: %s); %d record titles cited "   # noqa: F821
      "(not a title at %s: %s)" % (len(QQ128), q_miss or "none", len(cited), START128, t_miss or "none"))

unit128("SUCCESSOR128", "every in-force model re-run: predfix112 in full, and the twenty its SUCCESSOR112 re-runs "
        "(their outputs dumped through it); each red DECLARED in predfold1128_succ_decl.tsv by predfix90's `red_key10` "
        "key, which carries the red's own FAIL line and no document line numbers; a traceback never")
P90_128 = os.path.join(LANES128, "predfix90_evidence", "predfix90_model.py")
_src90_128 = builtins.open(P90_128, encoding="utf-8").read()
exec(compile(_src90_128[_src90_128.index("CRASH10 = re.compile("):_src90_128.index("succ_bad, succ_n, succ_t, succ_seen = ")],   # noqa: S102
             P90_128, "exec"), globals())                    # predfix90's red key, verbatim
DECLF128 = os.path.join(HERE128, "predfold1128_succ_decl.tsv")
SD128 = {}
if os.path.exists(DECLF128):
    for l_ in builtins.open(DECLF128, encoding="utf-8").read().split("\n"):
        if l_ and not l_.startswith("#"):
            m_, r_, cls_, why_, key_ = l_.split("\t", 4)
            SD128.setdefault(m_, {})[r_] = (cls_, key_, why_)
if s128("s18") and SD128:
    _m = sorted(SD128)[0]
    _r = sorted(SD128[_m])[0]
    SD128[_m][_r] = (SD128[_m][_r][0], SD128[_m][_r][1] + " planted", SD128[_m][_r][2])
SCR128 = os.environ.get("PREDFOLD1128_SUCCDIR", "")
RD128 = os.environ.get("PREDFOLD1128_READDUMP") == "1"
sc_bad, sc_seen, sc_outs = [], [], {}
if not LIGHT128 or RD128:
    if not SCR128 or not os.path.isdir(SCR128):
        sc_bad.append(("PREDFOLD1128_SUCCDIR", SCR128, "NOT A DIRECTORY"))
    elif not RD128 and os.listdir(SCR128):                   # the older models read EVERY .out in the directory
        sc_bad.append(("PREDFOLD1128_SUCCDIR", SCR128, "NOT EMPTY (a stale dump is read as a model)"))
    elif not RD128:
        env = {k: v for k, v in os.environ.items() if not k.startswith(("PREDFIX111_", "PREDFOLD1125_", "PREDFOLD1127_",
                                                                        "PREDFIX90_", "PREDFIX112_", "PREDFOLD1128_"))}
        env["PREDFIX112_SUCCDIR"] = SCR128
        o_ = subprocess.run([sys.executable, "-I", "-B", P112], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, env=env, timeout=5900).stdout
        builtins.open(os.path.join(SCR128, "predfix112.out"), "w", encoding="utf-8").write(o_)
    if SCR128 and os.path.isdir(SCR128):
        for f_ in sorted(os.listdir(SCR128)):
            if f_.endswith(".out"):
                sc_outs[f_[:-4]] = builtins.open(os.path.join(SCR128, f_), encoding="utf-8").read()
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
        decl = SD128.get(mname, {})
        print("   %-13s last line: %s" % (mname, last[:150]))
        for r, (cls_, key_) in sorted(reds.items()):
            sc_seen.append((mname, r, cls_, key_))
            d_ = decl.get(r)
            if cls_ == "TRACEBACK" or d_ is None or d_[1] != key_:
                sc_bad.append((mname, r, "UNDECLARED" if d_ is None else ("KEY CHANGED" if cls_ != "TRACEBACK" else cls_)))
        for r in sorted(set(decl) - set(reds)):
            sc_bad.append((mname, r, "DECLARED, NOW GREEN"))
    WD = os.environ.get("PREDFOLD1128_WRITEDECL", "")
    if WD:
        with builtins.open(WD, "w", encoding="utf-8") as fh:
            fh.write("# model\tred\tclass\twhy\tkey (red_key10: the red's own FAIL line text, no document line numbers)\n")
            for mname, r, cls_, key_ in sc_seen:
                fh.write("%s\t%s\t%s\t%s\t%s\n" % (mname, r, cls_, SD128.get(mname, {}).get(r, ("", "", "WHY?"))[2], key_))
    for x_ in sc_bad:
        print("   NOT AS DECLARED %s %s: %s" % x_)
    check("SUCCESSOR128", len(sc_outs) >= 21 and not sc_bad, "%d models read, %d reds, each against its declared "   # noqa: F821
          "key (%d declared): %s" % (len(sc_outs), len(sc_seen), sum(len(v) for v in SD128.values()),
                                     sc_bad or "all as declared"))
else:
    print("   LIGHT: SUCCESSOR128 not run")

PLANTS128 = {"s1": "RULE128", "s2": "CANARY128", "s3": "NAMED128", "s4": "REF128", "s5": "REF128", "s6": "WEEKDAY128",
             "s7": "RULE128", "s8": "READINGS128", "s9": "OPEN128", "s10": "MECH128", "s11": "TABLE128",
             "s12": "SWEEP128", "s13": "ERRSWEEP128", "s14": "SPECLINES128", "s15": "STALE128", "s16": "MARK128",
             "s17": "QUOTES128", "s18": "SUCCESSOR128"}
if SAB128 == "all":
    caught = []
    for q_, tgt in sorted(PLANTS128.items(), key=lambda kv: int(kv[0][1:])):
        env = dict(os.environ, PREDFOLD1128_SABOTAGE=q_, PREDFOLD1128_LIGHT="1")
        if q_ == "s18":
            env["PREDFOLD1128_READDUMP"] = "1"
        o_ = subprocess.run([sys.executable, "-I", "-B", MY128], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, env=env, timeout=3000)
        fl = [l_ for l_ in o_.stdout.split("\n") if l_.startswith("FAIL ")]
        ok_ = o_.returncode != 0 and any(l_.startswith("FAIL %s:" % tgt) for l_ in fl) and "Traceback" not in o_.stdout
        caught.append((q_, tgt, ok_))
        print("   PLANT %s -> %s: %s; FAIL lines: %s" % (q_, tgt, "CAUGHT" if ok_ else "NOT CAUGHT",
                                                       [l_[:90] for l_ in fl]))
    check("PLANTS128", all(c_[2] for c_ in caught), "%d plants, caught %d" % (len(caught), sum(c_[2] for c_ in caught)))   # noqa: F821

failed128 = [n_ for n_, ok_ in RESULTS if not ok_]           # noqa: F821
print("predfold1128_model: %d checks, %d failed%s" % (len(RESULTS), len(failed128),   # noqa: F821
                                                     (" (%s)" % ", ".join(failed128)) if failed128 else ""))
sys.exit(1 if failed128 else 0)
