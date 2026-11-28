#!/usr/bin/env python3
"""predfix114_model.py: lane predfix114's evidence, the successor of predfold1129_model.py.

Review r114's ruled dispositions applied to the predicate documents (record docs/design/plan_row_bodies/
COND-FAMILY.md, the 2026-11-28 entries to the end; the owner's CORRECTION on stacked labels and his answer on one
list-over-label row). DESIGN evidence only: nothing here rules; no check under `make` reads it.

It LOADS predfold1129's model unchanged up to its checks (`# ==== CHECKS129`; the older models load through it),
then changes its walker GATE129 in five places, switched by X114[0] (off: predfold1129 as merged, the control):
  ORDER114  stacked labels are ORDERED steps (the owner's correction: "\"stacked\" are not the same but ordered as
            usual. Sometimes you can skip the upper stack label per usual skip rules. Here however you can't because
            p is a gate."): the label written DIRECTLY on a crossing is the gate, never skipped; a label above it
            sits over text written in place (a label expression) and is skipped by the usual rules; a place and the
            argument's own label are two steps (the body's `p`, then the sender's `a`).
  INCALL114 a path that NAMES a call's gate (the label directly on the call, or the call by its own name) is inside
            the call: it reaches an argument's text only through the body's place (`Y.c.a.h` skips the gate `p`;
            `Y.a.h`, the sender's own text reached without naming the call, stays legal).
  TWIN114   a text that reads through a name it places more than once, or reads before its only placement, is
            answered as its EXPLICIT-LABEL TWIN (last-placement 2: "exactly as an explicit label mentioned twice
            does"): every bare placement of the name rewritten `[twN = N]`, every read `N.x` as `twN.x`, built
            mechanically from the text; the twin is then judged and run as any program.
  SENTINL114 a macro with a sent label parameter (`Rs(l:, v) := /${[l = [p = v]]}xx/`) called with a sent label is
            inlined at the call (the sent label written for `l`, the argument for `v`): the sent label becomes the
            upper label over the body's own, so `x.p.h` is the full path and `x.h` skips the gate `p`.
  LOUD114   a crash is never a refusal (an exception the reader did not raise is reported `CRASH`, r114 F24); a
            program GATE129 cannot read that the in-force engine REFUSES is refused `FALLBACK114: ...` (loud, never
            an answer of the ruled rules, r114 F5); a legal fallback answer is logged.
The verdict is the last line, `predfix114_model: N checks, F failed`; it exits non-zero iff that line reports a
failure. PINNED COMMITS: this model reads git ONLY by commit id (START114).
`PREDFIX114_LIGHT=1` skips SUCCESSOR114; `PREDFIX114_SUCCDIR=DIR` an existing EMPTY scratch directory for the
successor outputs; `PREDFIX114_READDUMP=1` reads DIR instead of re-running; `PREDFIX114_WRITEDECL=F` writes the
seen reds as a declaration draft; `PREDFIX114_SABOTAGE=sN` plants one wrong rule, fact or text per check (PLANTS114);
`=all` runs each plant in its own LIGHT subprocess.
Run: `timeout 6000 python3 -I -B <this dir>/predfix114_model.py` from the worktree root.
"""
import builtins
import os
import re
import subprocess
import sys

MY114 = os.path.abspath(__file__)
HERE114 = os.path.dirname(MY114)
LANES114 = os.path.normpath(os.path.join(HERE114, ".."))
P129 = os.path.join(LANES114, "predfold1129_evidence", "predfold1129_model.py")
START114 = "b935b91b6"                                       # this lane's starting commit (lane/predfix114), PINNED
SAB114 = os.environ.get("PREDFIX114_SABOTAGE", "")
LIGHT114 = os.environ.get("PREDFIX114_LIGHT") == "1"
_src129 = builtins.open(P129, encoding="utf-8").read()
_a114 = _src129.index("\n# ==== CHECKS129 (a probe loads the model up to this line)") + 1
_sav114 = {k: os.environ.pop(k) for k in list(os.environ)
           if k.startswith(("PREDFOLD1129_", "PREDFIX113_", "PREDFOLD1128_", "PREDFIX112_", "PREDFOLD1127_",
                            "PREDFIX111_", "PREDFOLD1125_", "PREDFIX90_"))}
__file__ = P129
exec(compile(_src129[:_a114], P129, "exec"), globals())      # noqa: S102  predfold1129's engines, unchanged
__file__ = MY114
os.environ.update(_sav114)
X114 = [True]


def s114(q):
    return SAB114 == q


# ================================================================== ORDER114 and INCALL114: GATE129's walker, amended
_NOSTACK129 = _nostack129                                    # noqa: F821
_CLASSIFY129 = _classify129                                  # noqa: F821
_GNAME129 = _gname129                                        # noqa: F821


def _nostack129():                                           # noqa: F811
    return True if X114[0] else _NOSTACK129()


def _call_gate114(call):
    """the node that is a call's gate: the label written directly on it, else the call itself."""
    if call.parent is not None and call.parent.k == "label" and call.parent.kids[0] is call:
        return call.parent
    return call


def _classify129(P, chain, rtid, named):                     # noqa: F811
    """ORDER114: every label its own step; the label directly on a crossing is the gate (never skipped), a label
    above it skippable by the usual rules. INCALL114: an argument's own text reached from a call whose gate the path
    named is behind the body's place."""
    if not X114[0]:
        return _CLASSIFY129(P, chain, rtid, named)
    walls, gates, skips, full = [], [], [], []
    named_ids = set(id(n) for n in named)
    for i, n in enumerate(chain[1:-1], 1):
        p = chain[i - 1]
        if isinstance(n, R2129):                             # noqa: F821
            g = _call_gate114(n.call)
            if (id(g) in named_ids or id(n.call) in named_ids or g is chain[0]) and not s114("s2"):
                lab = n.argn.parent
                if lab is not None and lab.k == "label" and lab.kids[0] is n.argn and not lab.name.startswith("_"):
                    gates.append(lab)                        # the body's label on the place: a gate skipped
                    full.append((lab.name,))
                else:
                    walls.append(n)                          # an unlabelled place, from outside the body (rule 6)
            continue
        if n.k == "label":
            if n.name == "_" or n.name.startswith("_"):
                walls.append(n)
                continue
            if id(n) in named_ids or n is chain[-1]:
                continue
            bottom = n.kids[0]
            gate = _is_crossing129(bottom) and _crossed129(bottom, chain) and not s114("s1")   # noqa: F821
            (gates if gate else skips).append(n)
            full.append((n.name,))
            continue
        if n.k == "grp":
            if n.name.startswith("_"):
                walls.append(n)
                continue
            skips.append(n)
            full.append((n.name,))
            continue
        if n.k in ("use", "call"):
            if not isinstance(p, R2129) and p.k in ("label", "list"):   # noqa: F821
                continue                                     # labelled or listed: the label is the gate
            if not isinstance(p, R2129) and p.k == "arg" and _bare_arg129(P, n, chain):   # noqa: F821
                continue                                     # the argument's own use, bare under its place: one spot
            if n.tid != rtid:
                walls.append(n)
                continue
            if _crossed129(n, chain):                        # noqa: F821
                gates.append(n)
            else:
                skips.append(n)
            full.append((n.name,))
            continue
        if n.k == "list":
            skips.append(n)
            continue
        if n.k == "arg":
            if n.parent is not None and n.parent.k in ("label", "list"):
                continue
            if not isinstance(p, R2129) and p.k == "arg":    # noqa: F821
                continue
            if n.tid != rtid:
                walls.append(n)
                continue
            if id(n) in named_ids:
                continue
            gates.append(n)
            full.append((_pname129(P, n),))                  # noqa: F821
            continue
    return walls, gates, skips, full


def _gname129(P, g, rtid):                                   # noqa: F811
    if X114[0] and g.k == "label":
        return g.name                                        # ORDER114: the gate is the label itself
    return _GNAME129(P, g, rtid)


# ================================================================== BRANCH114 and NAMEBOTH114: walk129, two lines changed
# walk129's source, re-compiled with two mechanical replacements (asserted present):
#  - BRANCH114[0] == "error" (gate-beside-direct-branch's other reading, a switch): a direct target does not hide a
#    gated one in another branch of `|` (a gate is never skipped, label-names-gate 1);
#  - the refusal names every way in (label-names-gate 4: "A bare `a.g` is an error naming both"): the full path AND,
#    where the gate is a label the reader's own text writes, the read that starts at it.
BRANCH114 = [""]
CURRT114 = ["P"]
_w_a = _src129.index("def walk129(")
_w_b = _src129.index("def _gname129(")
_w_src = _src129[_w_a:_w_b]
_w_old = "        if direct:\n            pool = direct"
_w_new = ("        if direct and BRANCH114[0] == \"error\" and X114[0] and any(_rel129(pre, d[6], g[6]) == \"alt\" "
          "for d in direct for g in gated):\n"
          "            raise Refused129(\"`%s`: a `%s` sits behind a gate in another branch, which is never skipped: %s "
          "(a compile error, gate-beside-direct-branch's other reading)\" % (\".\".join(path), x, "
          "_gatesay129(path, i, gated)))\n" + _w_old)
assert _w_src.count(_w_old) == 1
_w_src = _w_src.replace(_w_old, _w_new)
_w_src = _w_src.replace('    P = pre.P\n', '    P = pre.P\n    CURRT114[0] = rtid\n', 1)
exec(compile(_w_src, P129 + " (walk129, BRANCH114)", "exec"), globals())   # noqa: S102
_GATESAY129 = _gatesay129                                    # noqa: F821


def _gatesay129(path, i, cs):                                # noqa: F811
    if not X114[0]:
        return _GATESAY129(path, i, cs)
    fps = []
    for c in cs:
        f_ = ".".join(list(path[:i]) + [g for g in c[7]] + list(path[i:]))
        if f_ not in fps:
            fps.append(f_)
    for c in cs:
        for g in c[2]:
            if g.k == "label" and g.tid == CURRT114[0] and not s114("s6"):
                f_ = ".".join([g.name] + list(path[i:]))
                if f_ not in fps:
                    fps.append(f_)
    return "write " + " or ".join("`%s`" % f_ for f_ in fps)


# ================================================================== TWIN114: the explicit-label twin
TWINLOG114 = []


def _placements114(t, n):
    """the bare placements of the name n in the text t, pattern position only: [(start, end, form)], form 'bare'
    or 'hole' (`${n}`); None when n is placed under a label or as a path (the twin does not apply)."""
    out = []
    for m in re.finditer(r"(?<![\w.$@])%s(?![\w.(])" % re.escape(n), t):
        a, b = m.start(), m.end()
        before = t[:a]
        if _in_cond129(t, a):                                # noqa: F821  a read, not a placement
            continue
        if before.endswith("${"):
            if not t[b:].startswith("}"):
                return None
            out.append((a, b, "hole"))
            continue
        if before.count("/") % 2 or before.count('"') % 2 or before.count("`") % 2:
            continue                                         # inside a literal
        if re.search(r"=\s*$", before) and re.search(r"\[\s*\w+\s*=\s*$", before):
            return None                                      # labelled already: the label is the name
        if re.match(r"\s*\.", t[b:]):
            return None
        out.append((a, b, "bare"))
    return out


def _reads114(t, n):
    """the reads through n written in t's conditions: [start of the name]."""
    return [m.start(1) for m in re.finditer(r"(?<![\w.$])@?(%s)\.[A-Za-z_]" % re.escape(n), t)
            if _in_cond129(t, m.start(1))]                   # noqa: F821


def _twin_text114(t, n):
    """the explicit-label twin of t for the name n, or None when TWIN114 does not apply."""
    if "$" + n in t.replace("${" + n + "}", ""):
        return None                                          # a value read: not a placement (F23)
    pl = _placements114(t, n)
    rd = _reads114(t, n)
    if not pl or not rd:
        return None
    if len(pl) < 2 and not any(r < pl[0][0] for r in rd):
        return None
    tw = "tw" + n
    out, i = [], 0
    for a, b, form in pl:
        out.append(t[i:a])
        out.append("[%s = %s]" % (tw, n))
        i = b
    out.append(t[i:])
    t2 = "".join(out)
    t2 = re.sub(r"(?<![\w.$])(@?)%s\.(?=[A-Za-z_])" % re.escape(n),
                lambda m: m.group(1) + tw + ".", t2)
    return t2


def twin114(expr, binds):
    """TWIN114 over a program: the top-level text for each binding name it reads through, each macro body for each
    of its parameters; (expr, binds, [what was twinned])."""
    did = []
    if s114("s3"):
        return expr, binds, did
    defs = _defs128(binds)                                   # noqa: F821
    for n in sorted(defs):
        t2 = _twin_text114(expr, n)
        if t2 is not None:
            did.append(("top", n))
            expr = t2
    nb = []
    for b in binds:
        if ":=" not in b:
            nb.append(b)
            continue
        h, body = b.split(":=", 1)
        m = re.match(r"\s*([A-Za-z_]\w*)\s*\(([^)]*)\)\s*$", h)
        if m:
            for prm in [x.strip() for x in m.group(2).split(",")]:
                if re.fullmatch(r"[A-Za-z_]\w*", prm):
                    t2 = _twin_text114(body, prm)
                    if t2 is not None:
                        did.append((m.group(1), prm))
                        body = t2
        nb.append(h + ":=" + body)
    tw = set(x[0] for x in did if x[0] != "top")
    for n in sorted(tw):                                     # a twinned body inlined at its calls (the in-force
        if re.search(r"(?<![\w.])%s\." % re.escape(n), expr):   # engine reads a body's own label over a place
            continue                                         # in `|` and before it wrongly: the twin runs as the
        d = _defs128(nb)[n]                                  # noqa: F821  caller's text); never with a read B.x
        ps = [x.strip() for x in d[0].split(",")]
        for a_, b_, args in reversed(_calls128(expr, n)):    # noqa: F821
            if len(args) != len(ps):
                continue
            body = d[1].strip()
            for p_, v_ in zip(ps, args):
                body = re.sub(r"(?<![\w.$])%s(?![\w(])" % re.escape(p_), lambda m, v_=v_: v_.strip(), body)
            expr = expr[:a_] + "(" + body + ")" + expr[b_:]
            did.append(("inlined", n))
        nb = [x for x in nb if n not in _defs128([x])]       # noqa: F821
    return expr, nb, did


LISTLEAN114 = [""]                                           # OTHER114's switch: "one-step" = his lean, list-opens-one-step


def listrows114(expr, binds):
    """his answer on list-over-label ("${[p=[(=) = rx]]} as if just [p=rx]"): a list directly under a label on a
    place is no door; and, switched, his lean on the other order (the list opens exactly the one step it is written
    on: from outside the list's export, the inner label hidden; a body's own read of it kept)."""
    def fix(t):
        if not s114("s5"):
            t = re.sub(r"\[\s*([A-Za-z]\w*)\s*=\s*\[\s*\(=\)\s*=\s*([A-Za-z_]\w*)\s*\]\s*\]", r"[\1 = \2]", t)
        if LISTLEAN114[0] == "one-step":
            for m in re.finditer(r"\[\s*\(=\)\s*=\s*\[\s*([A-Za-z]\w*)\s*=\s*([A-Za-z_]\w*)\s*\]\s*\]", t):
                if not re.search(r"(?<![\w.])%s\." % re.escape(m.group(1)), t):
                    t = t[:m.start()] + "[(=) = %s]" % m.group(2) + t[m.end():]
                    break
        return t
    return fix(expr), [b.split(":=", 1)[0] + ":=" + fix(b.split(":=", 1)[1]) if ":=" in b else b for b in binds]


# ================================================================== SENTINL114: a sent label inlined at the call
def sentinl114(expr, binds):
    defs = _defs128(binds)                                   # noqa: F821
    for n, (head, body, _) in defs.items():
        if not head:
            continue
        m = re.match(r"\s*([A-Za-z_]\w*)\s*:\s*,\s*([A-Za-z_]\w*)\s*$", head)
        if not m:
            continue
        lp, vp = m.group(1), m.group(2)
        if not re.search(r"\[\s*%s\s*=\s*\[\s*[A-Za-z]\w*\s*=\s*%s\s*\]\s*\]" % (re.escape(lp), re.escape(vp)), body):
            continue                                         # only a sent label stacked over a body's label on v
        cm = re.search(r"(?<![\w.])%s\(\s*([A-Za-z_]\w*)\s*:\s*,\s*([^()]*?)\s*\)" % re.escape(n), expr)
        if not cm or cm.group(1).startswith("_"):
            continue
        b2 = re.sub(r"(?<![\w.])%s(?![\w(])" % re.escape(lp), lambda _m: cm.group(1), body.strip())
        b2 = re.sub(r"(?<![\w.])%s(?![\w(])" % re.escape(vp), lambda _m: cm.group(2), b2)
        expr = expr[:cm.start()] + "(" + b2 + ")" + expr[cm.end():]
        binds = [x for x in binds if n not in _defs128([x])]   # noqa: F821
    return expr, binds


# ================================================================== LOUD114 and the entry: prog with the five in front
_PROG129 = prog                                              # noqa: F821  predfold1129's entry
FALLLOG114 = []


class Crash114(Exception):
    pass


def _prog114(expr, binds, **opts):
    """predfold1129's prog with LOUD114: no exception class that marks a crash is read as 'beyond the reader'."""
    binds = list(binds)
    ROW1_113[0], CHECKED113[0] = "legal", "new"              # noqa: F821
    try:
        if PATHATOM129.search(" ".join(t for t in [expr] + [b.split(":=", 1)[1] for b in binds if ":=" in b])):   # noqa: F821
            expr, binds = _part129(expr, binds)              # noqa: F821
        try:
            if re.search(r"@\d", " ".join([expr] + binds)):
                raise Unparsed("a group question over a number")   # noqa: F821  predfold1127's prep crashes on it
            pre, vs = verdict129(expr, binds)                # noqa: F821
        except (Unparsed, Mech129Error, Refused129, TR11.TrError) as x:   # noqa: F821  beyond the reader
            if expr in RESPELL129:                           # noqa: F821
                MECHLOG129.append(expr)                      # noqa: F821
                return _PROG113(RESPELL129[expr], binds, **opts)   # noqa: F821
            try:
                P_ = _PROG113(expr, binds, **opts)           # noqa: F821
            except CompileError as e:                        # noqa: F821
                if s114("s4"):
                    raise
                raise CompileError("FALLBACK114: GATE129 cannot read it (%s); the in-force engine refuses: %s" % (   # noqa: F821
                    str(x)[:60], str(e)[:160]))
            FALLLOG114.append(expr)
            return P_
        except CompileError:                                 # noqa: F821  the front end's own refusal
            raise
        except Exception as x:                               # noqa: BLE001
            raise Crash114("%s in GATE129: %s" % (type(x).__name__, str(x)[:80]))
        for rd, rtid, v, r in vs:
            if v[0] == "refused":
                raise CompileError(v[1])                     # noqa: F821
        try:
            return _PROG113(expr, binds, **opts)             # noqa: F821
        except CompileError as e:                            # noqa: F821
            try:
                P_ = mech129(expr, binds)                    # noqa: F821
            except (Mech129Error, Unparsed, Refused129) as x:   # noqa: F821
                if expr in RESPELL129:                       # noqa: F821
                    MECHLOG129.append(expr)                  # noqa: F821
                    return _PROG113(RESPELL129[expr], binds, **opts)   # noqa: F821
                raise CompileError("legal by GATE129 but MECH129 cannot build it (%s); the in-force engine: %s" % (   # noqa: F821
                    str(x)[:60], str(e)[:80]))
            MECHLOG129.append(expr)                          # noqa: F821
            return P_
    finally:
        ROW1_113[0], CHECKED113[0] = "error", "error"        # noqa: F821


def prog(expr, binds=(), **opts):                            # noqa: F811
    if not X114[0]:
        return _PROG129(expr, binds, **opts)
    binds = list(binds)
    expr, binds = sentinl114(expr, binds)
    expr, binds = listrows114(expr, binds)
    e2, b2, did = twin114(expr, binds)
    if did:
        TWINLOG114.append((expr, did))
    return _prog114(e2, b2, **opts)


def run11(expr, binds=()):                                   # noqa: F811  LOUD114: a crash is never a refusal
    try:
        return prog(expr, list(binds)), None
    except CompileError as e:                                # noqa: F821
        return None, str(e)
    except Exception as e:                                   # noqa: BLE001
        return None, "CRASH %s: %s" % (type(e).__name__, str(e)[:100])


# ==== CHECKS114 (a probe loads the model up to this line)
