#!/usr/bin/env python3
"""predfix114_model.py: lane predfix114's evidence, the successor of predfold1129_model.py.

Review r114's ruled dispositions applied to the predicate documents (record docs/design/plan_row_bodies/
COND-FAMILY.md, the 2026-11-28 entries to the end; the owner's CORRECTION on stacked labels and his answer on one
list-over-label row). DESIGN evidence only: nothing here rules; no check under `make` reads it.

It LOADS predfold1129's model unchanged up to its checks (`# ==== CHECKS129`; the older models load through it),
then changes its walker GATE129 and its entry, switched by X114[0] (off: predfold1129 as merged, the control):
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
  LIST114   his answer ("${[p=[(=) = rx]]} as if just [p=rx]"), list-opens-one-step (RULED: a list is no step of a
            path; the label under it is hidden from above, what is under that label comes up) and a list that passes
            nothing (RULED, a compile error where it is written); LISTLEAN114 "gate" = the withdrawn reading.
  LOOP114   branch-in-loop (RULED "error for now. Ambiguous"): a plain read skipping to a name two branches of an
            alternation under `rx.repeat` hold is a compile error naming both full paths and the array form;
            LOOPALT114 "last" = the parked reading, the branch of the last pass.
  BRANCH114 and NAMEBOTH114: a switch for gate-beside-direct-branch's other reading; refusals naming every way in.
The checks: RULE114, TWIN114, LOUD114, SWEEP114, ERRSWEEP114, QUOTES114, STALE114, TAGS114, OTHER114,
SUCCESSOR114, PLANTS114 (s1..s18, one per check at least).
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


LISTLEAN114 = ["one-step"]                                   # list-opens-one-step, RULED 2026-11-28 (rulings R-1);
                                                             # "gate" = the withdrawn printed reading (OTHER114's control)


def _balanced114(t, i):
    """the index after the parenthesis that closes the one opening at t[i]"""
    d = 0
    for j in range(i, len(t)):
        d += {"(": 1, ")": -1}.get(t[j], 0)
        if d == 0:
            return j + 1
    raise Unparsed("unbalanced")                             # noqa: F821


def _top_split114(t, sep):
    out, d, cur = [], 0, ""
    for ch in t:
        d += {"(": 1, "[": 1, ")": -1, "]": -1}.get(ch, 0)
        if ch == sep and d == 0:
            out.append(cur); cur = ""
        else:
            cur += ch
    return out + [cur]


def listrows114(expr, binds):
    """his answer on list-over-label ("${[p=[(=) = rx]]} as if just [p=rx]"): a list directly under a label on a
    place is no door; list-opens-one-step (RULED): a list gives the thing it is written over no path element, so
    the label under it is not reached from above, and what is under that label comes up; a body's read that STARTS
    at the label is kept. A list that passes nothing is a compile error where it is written (RULED, R-2)."""
    def fix(t):
        if not s114("s5"):
            t = re.sub(r"\[\s*([A-Za-z]\w*)\s*=\s*\[\s*\(=\)\s*=\s*([A-Za-z_]\w*)\s*\]\s*\]", r"[\1 = \2]", t)
        if not s114("s8"):
            for m in re.finditer(r"\[\s*\(=\)\s*=\s*(?:\[\s*([A-Za-z]\w*)\s*=\s*)?(/(?:[^/\\]|\\.)*/)\s*\]?\s*\]", t):
                if "(?<" not in m.group(2):
                    raise CompileError("a list that passes nothing: there is nothing inside %s to export (a compile "   # noqa: F821
                                       "error where it is written, list-opens-one-step)" % (
                                           "`%s`" % m.group(1) if m.group(1) else "the list"))
        if LISTLEAN114[0] == "one-step" and not s114("s7"):
            for m in re.finditer(r"\[\s*\(=\)\s*=\s*\[\s*([A-Za-z]\w*)\s*=\s*([A-Za-z_]\w*)\s*\]\s*\]", t):
                if not re.search(r"(?<![\w.])%s\." % re.escape(m.group(1)), t):
                    t = t[:m.start()] + "[(=) = %s]" % m.group(2) + t[m.end():]
                    break
        return t
    out = fix(expr), [b.split(":=", 1)[0] + ":=" + fix(b.split(":=", 1)[1]) if ":=" in b else b for b in binds]
    hidden = set()
    if LISTLEAN114[0] == "one-step" and not s114("s7"):
        for t in [expr] + binds:
            hidden |= set(re.findall(r"\[\s*\(=\)\s*=\s*\[\s*([A-Za-z]\w*)\s*=", t))
    for t in [expr] + [b.split(":=", 1)[1] for b in binds if ":=" in b]:
        for p_ in sorted(hidden):
            m = re.search(r"(?<![\w.@])((?:[A-Za-z_]\w*\.)+)%s\b((?:\.\w+)*)" % re.escape(p_), t)
            if m:
                raise CompileError("`%s%s%s`: no label `%s` is reached from `%s` (a compile error: a list is no step of a "   # noqa: F821
                                   "path, list-opens-one-step)" % (m.group(1), p_, m.group(2), p_, m.group(1)[:-1]))
    return out


LOOPALT114 = ["error"]                                       # branch-in-loop RULED "error for now"; "last" = the
                                                             # parked reading "the branch of the last pass" (OTHER114)


def loopalt114(expr, binds):
    """branch-in-loop (RULED 2026-11-28, R-3, "error for now. Ambiguous"): a loop around an alternation makes its
    branches' paths count together; a plain read skipping to a name two branches hold is a compile error naming
    both full paths and the array form. The array form (`@n.d`) is untouched."""
    if s114("s9") or LOOPALT114[0] == "last":
        return
    for t in [expr] + [b.split(":=", 1)[1] for b in binds if ":=" in b]:
        for m in re.finditer(r"\[\s*([A-Za-z]\w*)\s*=\s*rx\.repeat\(", t):
            n = m.group(1)
            a = m.end() - 1
            inner = t[a + 1:_balanced114(t, a) - 1]
            first = _top_split114(inner, ",")[0]
            br = _top_split114(first, "|")
            if len(br) < 2:
                continue
            held = {}
            for b in br:
                lm = re.match(r"\s*\[\s*([A-Za-z]\w*)\s*=", b)
                for g in re.findall(r"\(\?<(\w+)>", b):
                    held.setdefault(g, []).append(lm.group(1) if lm else None)
            for rm in re.finditer(r"(?<![@\w.])%s\.(\w+)\b(?!\.)" % re.escape(n), expr):
                ls = held.get(rm.group(1), [])
                if len(ls) >= 2:
                    raise CompileError("`%s.%s`: a loop around an alternation: two full paths, %s, and the "   # noqa: F821
                                       "array form `some(@%s.%s, ..)` (a compile error, branch-in-loop: ambiguous, for now)" % (
                                           n, rm.group(1), " and ".join("`%s.%s.%s`" % (n, l_, rm.group(1)) for l_ in ls if l_),
                                           n, rm.group(1)))


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
    loopalt114(expr, binds)
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
        if s114("s10"):
            return None, str(e)                              # plant: a crash read as a refusal
        return None, "CRASH %s: %s" % (type(e).__name__, str(e)[:100])


# ==== CHECKS114 (a probe loads the model up to this line)
RESULTS.clear()                                              # noqa: F821
REC114 = "4b2a952b3"                                         # the record's last entry this lane applies (rulings R-3), PINNED


def unit114(name, what):
    print("== %s: %s" % (name, what))


AH = "A := /(?<h>\\d)/"
G = "A := [g = /\\d/]"
BP = "B(rx) := /${[p = rx]}xx/"
YC = 'Y := [c = B([a = A])] SEQ "!"'
PX = "P := /(?<d>\\d)xx/"
XN = 'X := [n = [m = A]] SEQ "!"'
RS = "Rs(l:, v) := /${[l = [p = v]]}xx/"
B1B = "B1(rx) := /${[(=) = [p = rx]]}xx/"
BAB = "Ba(rx) := /${[a = [(=) = [p = rx]]]}xx/"
B3B = "B3(rx) := /${[p = [(=) = rx]]}xx/"
LOOP = "[n = rx.repeat([a = /(?<d>\\d)/] | [b = /x(?<d>\\d)/], min = 1, max = _)]"
T3 = [("3xx", "HOLDS"), ("7xx", "FAILS")]
T3b = [("3xx!", "HOLDS"), ("7xx!", "FAILS")]
# RULE114: verdicts and texts typed by hand from the RULED WORDS (his correction, his answer, list-opens-one-step,
# a list that passes nothing, branch-in-loop, the dispositions' F3-F5), never from the walker or the documents:
# (ruling and line, program, bindings, "legal"/"error", [(text, HOLDS/FAILS), ..]).
RULE114 = [
    ("correction: n.d over [n = [m = P]], the gate skipped", "[n = [m = P]] & (n.d: <5)", [PX], "error", []),
    ("correction: n.m.d, the full path", "[n = [m = P]] & (n.m.d: <5)", [PX], "legal", T3),
    ("correction: m.d, from the gate", "[n = [m = P]] & (m.d: <5)", [PX], "legal", T3),
    ("correction: the upper label skipped over text in place", "[n = [m = /(?<d>\\d)xx/]] & (n.d: <5)", [], "legal", T3),
    ("correction: X.h from outside", "X & (X.h: <5)", [AH, XN], "error", []),
    ("correction: X.n.h skips the gate m", "X & (X.n.h: <5)", [AH, XN], "error", []),
    ("correction: X.m.h", "X & (X.m.h: <5)", [AH, XN], "legal", [("3!", "HOLDS"), ("7!", "FAILS")]),
    ("correction: X.n.m.h", "X & (X.n.m.h: <5)", [AH, XN], "legal", [("3!", "HOLDS"), ("7!", "FAILS")]),
    ("correction: Y.c.a.h an error (argument-is-gate's telling wrong)", "Y & (Y.c.a.h: <5)", [AH, BP, YC], "error", []),
    ("correction: Y.c.p.a.h the full path", "Y & (Y.c.p.a.h: <5)", [AH, BP, YC], "legal", T3b),
    ("correction: Y.c.p.h skips the sender's a", "Y & (Y.c.p.h: <5)", [AH, BP, YC], "error", []),
    ("argument-is-gate, told: Y.a.h stays legal", "Y & (Y.a.h: <5)", [AH, BP, YC], "legal", T3b),
    ("correction: B.a.h skips the place's p", "B([a = A]) & (B.a.h: <5)", [AH, BP], "error", []),
    ("correction: B.p.a.h, two steps", "B([a = A]) & (B.p.a.h: <5)", [AH, BP], "legal", T3),
    ("correction: x.h over a sent label above p", "Rs(x:, A) & (x.h: <5)", [AH, RS], "error", []),
    ("correction: x.p.h", "Rs(x:, A) & (x.p.h: <5)", [AH, RS], "legal", T3),
    ("his answer: [p = [(=) = rx]] as if just [p = rx]: B3.p.h", "B3(A) & (B3.p.h: <5)", [AH, B3B], "legal", T3),
    ("his answer: B3.h", "B3(A) & (B3.h: <5)", [AH, B3B], "error", []),
    ("list-opens-one-step 2: B1.h comes up", "B1(A) & (B1.h: <5)", [AH, B1B], "legal", T3),
    ("list-opens-one-step: B1.p hidden", "B1(A) & (B1.p: <5)", [AH, B1B], "error", []),
    ("list-opens-one-step: B1.p.h hidden", "B1(A) & (B1.p.h: <5)", [AH, B1B], "error", []),
    ("list-opens-one-step 2: p.h inside", "B1i(A)", [AH, "B1i(rx) := /${[(=) = [p = rx]]}xx/ & (p.h: <5)"], "legal", T3),
    ("list-opens-one-step, his example: a.h from outside", "Ba(A) & (Ba.a.h: <5)", [AH, BAB], "legal", T3),
    ("list-opens-one-step, his example: a.p.h from outside", "Ba(A) & (Ba.a.p.h: <5)", [AH, BAB], "error", []),
    ("list-opens-one-step, his example: a.p inside", "Bi(A)", [AH, "Bi(rx) := /${[a = [(=) = [p = rx]]]}xx/ & (a.p: <5)"], "error", []),
    ("list-opens-one-step, his example: a.h inside", "Bi(A)", [AH, "Bi(rx) := /${[a = [(=) = [p = rx]]]}xx/ & (a.h: <5)"], "legal", T3),
    ("list-opens-one-step, his example: p.h inside", "Bi(A)", [AH, "Bi(rx) := /${[a = [(=) = [p = rx]]]}xx/ & (p.h: <5)"], "legal", T3),
    ("list-opens-one-step 3: a bare read under (=)", "N4(A)", [AH, "N4(rx) := /${[(=) = rx]}xx/ & (h: <5)"], "error", []),
    ("a list that passes nothing", "Y & (Y.year: <5)", ["Y := [(=) = [year = /\\d{4}/]]"], "error", []),
    ("branch-in-loop: error for now", LOOP + " & (n.d: < 5)", [], "error", []),
    ("branch-in-loop: the array form untouched", LOOP + " & some(@n.d, <5)", [], "legal",
     [("x73", "HOLDS"), ("3x7", "HOLDS"), ("x7x8", "FAILS")]),
    ("last-placement 2 with F3: placed in two branches", "B(A)", [G, 'B(rx) := (rx | (rx SEQ "!")) & (rx.g: <5)'], "legal",
     [("3", "HOLDS"), ("7", "FAILS"), ("3!", "HOLDS"), ("7!", "FAILS")]),
    ("last-placement 4 with F5: a group question reads every placement", "B(A)",
     [G, 'B(rx) := rx SEQ ";" SEQ rx & some(@rx.g, "7")'], "legal", [("3;7", "HOLDS"), ("7;3", "HOLDS"), ("3;3", "FAILS")]),
    ("last-placement 5: from outside an unlabelled placement exports nothing", "B5(A) & (B5.g: <5)",
     [G, 'B5(rx) := rx SEQ ";" SEQ rx'], "error", []),
    ("last-placement 1: local implicit", "B(A)", [G, "B(rx) := rx & (rx.g: < 5)"], "legal", [("3", "HOLDS"), ("7", "FAILS")]),
    ("same-path-last 1, an optional second placement", 'A SEQ ";" SEQ (A)? & (A.g: <5)', [G], "legal",
     [("7;3", "HOLDS"), ("3;7", "FAILS"), ("3;", "FAILS")]),
]
# the rulings of the seven that the correction did not move: predfold1129's RULE129, its entries re-run here
_r129 = _src129[_src129.index("RULE129 = ["):_src129.index("unit129(\"RULE129\"")]
_g129 = {"ISO129": 'isodate := [year = /\\d{4}/] SEQ "-" SEQ [month = /\\d\\d/] SEQ "-" SEQ [day = /\\d\\d/]', "G129": G,
         "BP129": BP, "AH129": AH, "PQ129": ["P := /(?<d>\\d)/", "Q := /,(?<d>\\d)/"]}
exec(_r129, _g129)                                           # noqa: S102
MOVED_BY_CORRECTION = {"argument-is-gate, told: Y.c.a.h"}   # its told verdict is the one the correction found wrong
for nm_, e_, b_, want, tx_ in _g129["RULE129"]:
    if nm_ not in MOVED_BY_CORRECTION:
        RULE114.append(("(RULE129) " + nm_, e_, b_, want, tx_))
unit114("RULE114", "the correction, his answer, list-opens-one-step, a list that passes nothing, branch-in-loop and "
        "F3-F5 on %d programs, plus predfold1129's RULE129 rows the correction left, each verdict typed from the ruled "
        "words" % len(RULE114))
if s114("s14"):
    RULE114[0] = RULE114[0][:3] + ("legal",) + RULE114[0][4:]
RULEMSG114 = {"a list that passes nothing": "nothing inside `year` to export",   # the reason the ruling gives
              "branch-in-loop: error for now": "`n.a.d` and `n.b.d`"}
rl_bad = []
for nm_, e_, b_, want, tx_ in RULE114:
    Pg, err = run11(e_, b_)                                  # noqa: F821
    got = "legal" if Pg is not None else "error"
    bad_tx = [(t_, w_) for t_, w_ in tx_ if Pg is not None and ("HOLDS" if Pg.whole(t_) else "FAILS") != w_]
    if got != want or bad_tx or (err or "").startswith("CRASH") or RULEMSG114.get(nm_, "") not in (err or ""):
        rl_bad.append((nm_, want, got, bad_tx, (err or "")[:120]))
for x_ in rl_bad:
    print("   NOT AS RULED %s: want %s, got %s %s %s" % x_)
check("RULE114", not rl_bad, "%d programs; not as ruled: %s" % (len(RULE114), [x_[0] for x_ in rl_bad] or "none"))   # noqa: F821

unit114("TWIN114", "last-placement 2 (\"exactly as an explicit label mentioned twice does\"), F4: a read before the "
        "only placement answered as the explicit-label twin WRITTEN BY HAND, both run, three modes equal")
TWINS114 = [   # (program, bindings, its explicit-label twin typed by hand)
    ("B(A)", [G, "B(rx) := (/\\d/ & (rx.g: <5)) SEQ rx"], "(/\\d/ & (t.g: <5)) SEQ [t = A]", [G]),
    ("B(A)", [G, 'B(rx) := rx SEQ ";" SEQ rx & (rx.g: < 5)'], '[t = A] SEQ ";" SEQ [t = A] & (t.g: < 5)', [G]),
    ("B(A)", [G, 'B(rx) := (rx | (rx SEQ "!")) & (rx.g: <5)'], '([t = A] | ([t = A] SEQ "!")) & (t.g: <5)', [G]),
]
TWTX114 = ["13", "31", "1", "3", "3!", "7!", "3;7", "7;3", "x13 31", "3;7 7;3"]
tw_bad = []
for e_, b_, te_, tb_ in TWINS114:
    P1, e1 = run11(e_, b_)                                   # noqa: F821
    P2, e2 = run11(te_, tb_)                                 # noqa: F821
    if s114("s3") and P1 is not None:
        pass                                                 # the plant is in twin114 itself
    if (P1 is None) != (P2 is None):
        tw_bad.append((e_, b_[1], "verdicts differ", e1, e2))
    elif P1 is not None and ans11(P1, TWTX114) != ans11(P2, TWTX114):   # noqa: F821
        tw_bad.append((e_, b_[1], "answers differ"))
for x_ in tw_bad:
    print("   NOT AS ITS TWIN %s" % (x_,))
check("TWIN114", not tw_bad, "%d bodies against their hand-written twins, %d texts, three modes: %s" % (   # noqa: F821
    len(TWINS114), len(TWTX114), tw_bad or "equal"))

unit114("LOUD114", "F24 and F5: a crash is reported CRASH, never a refusal; a program the reader cannot read that the "
        "in-force engine refuses carries the FALLBACK114 prefix")
ld_bad = []
_v114 = verdict129                                           # noqa: F821


def _boom114(*a, **k):
    raise ZeroDivisionError("planted crash")


verdict129 = _boom114
_c = run11("B(A)", [AH, BP])                                 # noqa: F821
verdict129 = _v114
if not (_c[1] or "").startswith("CRASH"):
    ld_bad.append(("a crash", _c[1]))
_f = run11("B(A)", [G, "B(rx) := /${[(=g) = rx]}xx/ & (g: <5)"])   # noqa: F821  the F24 program
if _f[0] is not None or not (_f[1] or "").startswith("FALLBACK114"):
    ld_bad.append(("the F24 program", _f[1]))
print("   crash -> %s\n   F24 -> %s" % ((_c[1] or "")[:100], (_f[1] or "legal")[:140]))
check("LOUD114", not ld_bad, "crash and fallback: %s" % (ld_bad or "as stated"))   # noqa: F821

unit114("SWEEP114", "every printed three-mode line RUN under this model; the starting commit %s's lines under the "
        "control (X114 off: predfold1129 as merged) against these, keyed by the program; every key gone or moved "
        "DECLARED (MOVED114/GONE114 below)" % START114)
_sw_a = _src128.index('exec(compile(_src11[_src11.index("def sw11(docs):")')   # noqa: F821
_sw_b = _src128.index("OLD128 = {f_: _git8(")             # noqa: F821
exec(compile(_src128[_sw_a:_sw_b], P128, "exec"), globals())     # noqa: S102,F821  the sweep and error-line readers, verbatim
OLD114 = {f_: _git8("docs/design/predicates/" + f_, START114) for f_ in DOCF}   # noqa: F821
X114[0] = False
OLD_T114 = sw11(OLD114)                                      # noqa: F821
X114[0] = True
NOWS114 = dict(NOWS)                                         # noqa: F821
if s114("s11"):
    NOWS["core.md"] = NOWS["core.md"].replace("The chain: WHOLE `3xx` HOLDS", "The chain: WHOLE `3xx` FAILS", 1)   # noqa: F821
NEW_T114 = sw11(NOWS)                                        # noqa: F821
NOWS.update(NOWS114)                                         # noqa: F821
COR_ = "his correction on stacked labels (ordered steps; the label directly on a crossing is the gate)"
MOVED114 = {}    # program -> why its printed answers moved
GONE114 = {      # program -> why its three-mode line is gone (now a compile-error line, or rewritten)
    "[n = [m = P]] & (n.d: <5)": COR_ + ": `n.d` skips the gate `m`",
    "X & (X.n.h: <5)": COR_ + ": `X.n.h` skips the gate `m`",
    "[n = [m = [k = P]]] & (n.d: <5)": COR_ + ": `n.d` skips the gate `k`",
    "X & (X.y.c.a.h: <5)": COR_ + ": the place's gate `p` skipped",
    "B([a = A]) & (B.a.h: <5)": COR_ + ": `B.a.h` skips the place's gate `p`",
    "Y & (Y.c.a.h: <5)": COR_ + ": argument-is-gate's telling found wrong, `p` skipped",
    "Y & (Y.c.p.h: <5)": COR_ + ": `Y.c.p.h` skips the sender's `a`",
    "[k = [c = B([a = A])]] & (c.a.h: <5)": COR_ + ": `c.a.h` skips `p`",
    "Rs(x:, A) & (x.h: <5)": COR_ + ": `x.h` skips the gate `p`",
    "[pub = B([A = A])] & (pub.A.h: <5)": COR_ + ": `pub.A.h` skips `p`; `pub.p.A.h` printed",
    "B1(A) & (B1.p.h: <5)": "list-opens-one-step (a list is no step of a path): `B1.p.h` a compile error",
    "B1(A) & (B1.p: <5)": "list-opens-one-step (a list is no step of a path): `B1.p` a compile error",
}
inh = set((k_, f_, st_) for k_, vs in OLD_T114.items() for f_, _, st_, _, _ in vs if st_ != "same")
sw_bad, sw_moved, sw_gone, sw_new, sw_inh, cnt, used = [], [], [], [], [], {}, set()
for k_, vs in NEW_T114.items():
    for f_, ln_, st_, got_, pr_ in vs:
        cnt[st_] = cnt.get(st_, 0) + 1
        if st_ != "same":
            (sw_inh if (k_, f_, st_) in inh else sw_bad).append((f_, ln_, st_, k_[0], got_[:160]))
for k_, vs0 in OLD_T114.items():
    for f0 in sorted(set(v_[0] for v_ in vs0)):
        vs = [v_ for v_ in vs0 if v_[0] == f0]
        nk = [v_ for v_ in NEW_T114.get(k_, []) if v_[0] == f0]
        if nk:
            po, pn = sorted(set(v_[4] for v_ in vs)), sorted(set(v_[4] for v_ in nk))
            if po != pn:
                if k_[0] in MOVED114:
                    used.add(k_[0])
                    print("   MOVED BY A RULING %s `%s`: %s" % (f0, k_[0], MOVED114[k_[0]]))
                else:
                    sw_moved.append((f0, k_[0], " || ".join(po)[:200], " || ".join(pn)[:200]))
            continue
        if k_[0] in GONE114:
            used.add(k_[0])
            print("   GONE BY A RULING %s:%d `%s`: %s" % (vs[0][0], vs[0][1], k_[0], GONE114[k_[0]]))
            continue
        sw_gone.append((vs[0][0], vs[0][1], k_[0], vs[0][2]))
stale = sorted(k_ for k_ in list(GONE114) + list(MOVED114) if k_ not in used)
for k_, vs in NEW_T114.items():
    if k_ not in OLD_T114:
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
check("SWEEP114", OLD_T114 and not sw_bad and not sw_moved and not sw_gone and not stale and len(sw_new) >= 10,   # noqa: F821
      "%d printed lines now (%s), %d keys at the starting commit; not same and not inherited %d (inherited %d); "
      "moved %d; gone %d; declared %d; added %d; stale %d" % (
          sum(len(v) for v in NEW_T114.values()), ", ".join("%s %d" % kv for kv in sorted(cnt.items())),
          len(OLD_T114), len(sw_bad), len(sw_inh), len(sw_moved), len(sw_gone), len(GONE114) + len(MOVED114),
          len(sw_new), len(stale)))

unit114("ERRSWEEP114", "every printed compile-error line of the base files refused under this model, no crash; the "
        "ruled forms' refusals carry the phrase the ruling gives (MSG114); FALLBACK refusals counted")
MSG114 = {
    "[n = [m = P]] & (n.d: <5)": "write `n.m.d` or `m.d`",
    "B(A)": "",                                              # several bodies: matched by body below
    "Y & (Y.c.a.h: <5)": "write `Y.c.p.a.h`",
    "Rs(x:, A) & (x.h: <5)": "write `x.p.h`",
    "B1(A) & (B1.p.h: <5)": "a list is no step of a path",
    "Y & (Y.year: <5)": "nothing inside `year` to export",
    LOOP + " & (n.d: < 5)": "`n.a.d` and `n.b.d`",
}
MSGB114 = {"B(rx) := [a = /${[dd = rx]}xx/] & (a.g: <7)": "or `dd.g`"}   # label-names-gate 4, "naming both"
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
if s114("s12"):
    D8["core.md"] = D8["core.md"].replace("modes: a compile error (`Y & (Y.c.a.h: <5)`", "modes: a compile error (`Y & (Y.c.p.a.h: <5)`", 1)   # noqa: F821
es_now = [x_ for x_ in err_lines({f_: _enc_ref128(v_) for f_, v_ in D8.items()}) if not x_[0].endswith("_details.md")]   # noqa: F821
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
es_bad, es_msg, es_fb, seen = [], [], 0, set()
for f_, ln_, e_, b_ in es_now:
    Pg, err = run11(e_, b_)                                  # noqa: F821
    if Pg is not None or (err or "").startswith("CRASH"):
        es_bad.append((f_, ln_, e_, "legal" if Pg is not None else err[:100]))
        continue
    es_fb += err.startswith("FALLBACK114")
    want = MSG114.get(e_) or next((v_ for k_, v_ in MSGB114.items() if k_ in b_), "")
    if want:
        seen.add(e_ if MSG114.get(e_) else next(k_ for k_ in MSGB114 if k_ in b_))
        if want not in err:
            es_msg.append((f_, ln_, e_, want, err[:140]))
for x_ in es_bad:
    print("   BAD (printed a compile error, runs legal or crashes) %s" % (x_,))
for x_ in es_msg:
    print("   MESSAGE %s:%d `%s` lacks %r: %s" % x_)
unseen = sorted((set(k_ for k_ in MSG114 if MSG114[k_]) | set(MSGB114)) - seen)
check("ERRSWEEP114", es_now and not es_bad and not es_msg and not unseen,   # noqa: F821
      "%d compile-error lines read, each refused with no crash (FALLBACK114 refusals %d, the in-force engine's, "
      "loud): bad %s; ruled phrase missing %s; message rows with no line %s" % (
          len(es_now), es_fb, es_bad or "none", es_msg or "none", unseen or "none"))

BASES114 = ("core.md", "library.md", "parked.md")
DETS114 = ("core_details.md", "library_details.md", "parked_details.md")
JOIN114 = {f_: re.sub(r"\n  +", " ", NOWS[f_]) for f_ in NOWS}   # noqa: F821  continuation lines joined
RECT114 = _git8("docs/design/plan_row_bodies/COND-FAMILY.md", REC114)   # noqa: F821
RECN114 = re.sub(r"\s+", " ", RECT114)
_i114 = RECT114.index("### 2026-11-28 OWNER RULING — reference-example-checked")

unit114("QUOTES114", "every \"His words\" bullet of the base files that quotes a 2026-11-28 ruling or correction: each "
        "quoted span (12 characters or more, split at an elision `...` or an inserted `[no]`) a verbatim substring "
        "of the record at the PINNED commit %s, whitespace normalised" % REC114)
SL114 = ("reference-example-checked", "named-list-body-read", "label-names-gate", "argument-is-gate", "part-of-argument",
         "last-placement", "same-path-last", "sent-over-body-label", "list-opens-one-step", "branch-in-loop",
         "Sometimes you can skip", "as if just", "let's discuss", "pass thru", "nothing inside year")
qt_n, qt_bad, qt_b = 0, [], 0
for f_ in BASES114:
    t_ = JOIN114[f_]
    if s114("s13") and f_ == "core.md":
        t_ = t_.replace('"list-opens-one-step: in terms of path', '"list-opens-one-step: in term of path', 1)
    for l_ in t_.split("\n"):
        if not re.match(r"- (His words|His answer|An unnamed list passes)", l_) or not any(s_ in l_ for s_ in SL114):
            continue
        qt_b += 1
        for seg in l_.split('"')[1::2]:
            for sub in re.split(r" ?\.\.\. ?|\[no\]", seg):
                sub = re.sub(r"\s+", " ", sub).strip()
                if len(sub) < 12 or re.search(r"(?m)^%s(?:, [^:]*)?: " % re.escape(sub), t_):
                    continue
                qt_n += 1
                if sub not in RECN114:
                    qt_bad.append((f_, sub[:80]))
for x_ in qt_bad:
    print("   NOT IN THE RECORD %s: %s" % x_)
check("QUOTES114", qt_b >= 10 and qt_n >= 20 and not qt_bad, "%d bullets, %d quoted spans; not in the record: %s" % (   # noqa: F821
    qt_b, qt_n, qt_bad or "none"))

unit114("STALE114", "F16/F17: the search strings taken MECHANICALLY from the record's own REVISES / REVERSES / "
        "WITHDRAWN / IN DOUBT sentences (the 2026-11-28 entries at %s), searched over all six documents with "
        "continuation lines joined; a base hit only in a bullet saying it is corrected; a details hit only in "
        "slugs/rejected/readings/history or a marked rulings item" % REC114)
_t114 = re.sub(r"\s+", " ", RECT114[_i114:])
ST114 = []
for m_ in re.finditer(r"\b(REVISES|REVERSES|WITHDRAWN|IN DOUBT)\b", _t114):
    seg = re.split(r"(?<=[a-z\)\"`])\. (?=[A-Z(])| ### ", _t114[m_.start():m_.start() + 400])[0]
    for qm in re.finditer(r'"([^"]{12,})"', seg):
        if "to his sentence" not in seg[max(0, qm.start() - 30):qm.start()]:
            ST114.append((m_.group(1), qm.group(1)))
    bm = re.search(r'"([^"]{8,})" is $', _t114[max(0, m_.start() - 120):m_.start()])
    if bm:
        ST114.append((m_.group(1), bm.group(1)))
STS114 = []
for k_, q_ in ST114:
    for p_ in re.split(r" \.\.\. |\.\.\.", q_):
        p_ = p_.strip(" .,")
        if len(p_) >= 12:
            STS114.append((k_, p_))
# REVERSES binding-prefix's compile error names no quoted sentence: the piece's own retired wording, from git at START
STS114.append(("REVERSES (binding-prefix, by its wording at %s)" % START114, "used more than once is a compile error"))
if s114("s15"):
    NOWS["core.md"] = NOWS["core.md"] + "\n- planted: exactly one label of that name is visible from the start.\n"   # noqa: F821
DETF114 = ("slugs:", "rulings:", "rejected:", "readings:", "evidence:", "history:")
st_hits, st_ok = [], 0
for k_, p_ in STS114:
    pn_ = re.sub(r"\s+", " ", p_)
    for f_ in BASES114 + DETS114:
        cur = None
        for l_ in re.sub(r"\n  +", " ", NOWS[f_]).split("\n"):   # noqa: F821
            if l_.startswith(DETF114):
                cur = l_.split(":")[0]
            elif l_.startswith("## "):
                cur = None
            if pn_ not in re.sub(r"\s+", " ", l_):
                continue
            if f_ in BASES114:
                ok_ = bool(re.search(r"his correction|corrected|revised by|It revises", l_))
            else:                                            # a marked item, or a 2026-11-28 item reporting the revision
                ok_ = cur in ("slugs", "rejected", "readings", "history") or (cur == "rulings" and (
                    l_.startswith("- [") or bool(re.search(r"(?i)\brevises\b|\breverses\b|\bwithdrawn\b|\bin doubt\b|was wrong", l_))))
            if ok_:
                st_ok += 1
            else:
                st_hits.append((f_, k_, pn_[:50], l_[:90]))
if s114("s15"):
    NOWS["core.md"] = NOWS["core.md"].rsplit("\n- planted:", 1)[0] + "\n"   # noqa: F821
for x_ in st_hits:
    print("   STALE %s [%s] %r: %s" % x_)
check("STALE114", len(STS114) >= 8 and not st_hits, "%d search strings from the record; hits allowed %d; stale %s" % (   # noqa: F821
    len(STS114), st_ok, [x_[:3] for x_ in st_hits] or "none"))

unit114("TAGS114", "F17: every piece in each 2026-11-28 OWNER entry's `tags:` line (record at %s) has a details "
        "entry whose rulings field cites that entry's title" % REC114)
tg_bad, tg_n = [], 0
_dets = "\n".join(NOWS[f_] for f_ in DETS114)                # noqa: F821
if s114("s16"):
    _dets = _dets.replace('(record: "2026-11-28 OWNER RULINGS — a list that passes nothing', '(record: "planted', 1)
_ents = {}
for e_ in re.split(r"\n(?=## )", _dets):
    mm = re.match(r"## (\S+) — ", e_)
    if mm:
        _ents[mm.group(1)] = e_.split("\nrejected:")[0]
for ent in re.split(r"\n(?=### )", RECT114[_i114:]):
    title = ent.split("\n", 1)[0][4:]
    if not title.startswith("2026-11-28 OWNER"):
        continue
    tm = re.search(r"^tags: (.*)$", ent, re.M)
    for tg in (tm.group(1).split() if tm else []):
        tg_n += 1
        if '(record: "%s")' % title not in _ents.get(tg, ""):
            tg_bad.append((tg, title[:60]))
for x_ in tg_bad:
    print("   NO RULINGS ITEM %s for %s" % x_)
check("TAGS114", tg_n >= 30 and not tg_bad, "%d tagged pieces; missing %s" % (tg_n, tg_bad or "none"))   # noqa: F821

unit114("OTHER114", "each open reading the lane leaves to the owner, BOTH readings run (the printed one, and the "
        "other by its switch or its own spelling), each against a verdict and texts typed from the reading's words")
OTHER114 = [   # (question, printed program, binds, printed verdict, other program, other binds, switch, other verdict, texts)
    ("gate-beside-direct-branch", "[n = (P | /a(?<d>\\d)/)] & (n.d: <5)", ["P := /(?<d>\\d)/"], "legal",
     None, None, ("BRANCH114", "error"), "error", [("3", "HOLDS"), ("a3", "HOLDS"), ("7", "FAILS"), ("a7", "FAILS")]),
    ("group-over-hole", "/(?<g>${A})x/ & (g.h: <5)", [AH], "error",
     "[g = A] SEQ /x/ & (g.h: <5)", [AH], None, "legal", [("3x", "HOLDS"), ("7x", "FAILS")]),
    ("branch-last-pass (parked)", LOOP + " & (n.d: < 5)", [], "error",
     None, None, ("LOOPALT114", "last"), "legal", [("x73", "HOLDS"), ("3x7", "FAILS")]),
    ("list-over-label, the withdrawn reading", "B1(A) & (B1.h: <5)", [AH, B1B], "legal",
     None, None, ("LISTLEAN114", "gate"), "error", [("3xx", "HOLDS"), ("7xx", "FAILS")]),
]
if s114("s17"):
    OTHER114[0] = OTHER114[0][:3] + ("error",) + OTHER114[0][4:]
ot_bad = []
for q_, e_, b_, pv, oe, ob, sw, ov, tx_ in OTHER114:
    r1 = run11(e_, b_)                                       # noqa: F821
    if sw:
        old_ = globals()[sw[0]][0]
        globals()[sw[0]][0] = sw[1]
        try:
            r2 = run11(e_, b_)                               # noqa: F821
        finally:
            globals()[sw[0]][0] = old_
    else:
        r2 = run11(oe, ob)                                   # noqa: F821
    for rd, (Pg, err), want in (("printed", r1, pv), ("other", r2, ov)):
        got = "legal" if Pg is not None else "error"
        line_ = "   %s %s reading: %s" % (q_, rd, got)
        if Pg is not None:
            ws = ["HOLDS" if Pg.whole(t_) else "FAILS" for t_, _ in tx_]
            line_ += " " + "; ".join("%s %s" % (t_, w_) for (t_, _), w_ in zip(tx_, ws))
            if want == "legal" and ws != [w_ for _, w_ in tx_]:
                ot_bad.append((q_, rd, "texts"))
        else:
            line_ += " (%s)" % (err or "")[:110]
        print(line_)
        if got != want or (err or "").startswith("CRASH"):
            ot_bad.append((q_, rd, got))
check("OTHER114", not ot_bad, "%d open readings, both run; not as stated: %s" % (len(OTHER114), ot_bad or "none"))   # noqa: F821

unit114("SUCCESSOR114", "every in-force model re-run: predfold1129 in full (its SUCCESSOR129 re-runs predfix113 and the "
        "twenty-two before it, their outputs dumped beside it); each red DECLARED in predfix114_succ_decl.tsv by "
        "predfix90's `red_key10` key (the red's own FAIL line, no document line numbers); a traceback never")
P90_114 = os.path.join(LANES114, "predfix90_evidence", "predfix90_model.py")
_src90_114 = builtins.open(P90_114, encoding="utf-8").read()
exec(compile(_src90_114[_src90_114.index("CRASH10 = re.compile("):_src90_114.index("succ_bad, succ_n, succ_t, succ_seen = ")],   # noqa: S102
             P90_114, "exec"), globals())                    # predfix90's red key, verbatim
DECLF114 = os.path.join(HERE114, "predfix114_succ_decl.tsv")
SD114 = {}
if os.path.exists(DECLF114):
    for l_ in builtins.open(DECLF114, encoding="utf-8").read().split("\n"):
        if l_ and not l_.startswith("#"):
            m_, r_, cls_, why_, key_ = l_.split("\t", 4)
            SD114.setdefault(m_, {})[r_] = (cls_, key_, why_)
if s114("s18") and SD114:
    _pm = sorted(SD114)[0]
    _pr = sorted(SD114[_pm])[0]
    SD114[_pm][_pr] = (SD114[_pm][_pr][0], SD114[_pm][_pr][1] + " planted", SD114[_pm][_pr][2])
SCR114 = os.environ.get("PREDFIX114_SUCCDIR", "")
RD114 = os.environ.get("PREDFIX114_READDUMP") == "1"
sc_bad, sc_seen, sc_outs = [], [], {}
if not LIGHT114 or RD114:
    SUB114 = os.path.join(SCR114, "p1129")
    if not SCR114 or not os.path.isdir(SCR114):
        sc_bad.append(("PREDFIX114_SUCCDIR", SCR114, "NOT A DIRECTORY"))
    elif not RD114 and os.listdir(SCR114):
        sc_bad.append(("PREDFIX114_SUCCDIR", SCR114, "NOT EMPTY (a stale dump is read as a model)"))
    elif not RD114:
        os.mkdir(SUB114)
        env = {k: v for k, v in os.environ.items() if not k.startswith((
            "PREDFIX111_", "PREDFOLD1125_", "PREDFOLD1127_", "PREDFIX90_", "PREDFIX112_", "PREDFOLD1128_", "PREDFIX113_",
            "PREDFOLD1129_", "PREDFIX114_"))}
        env["PREDFOLD1129_SUCCDIR"] = SUB114
        o_ = subprocess.run([sys.executable, "-I", "-B", P129], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, env=env, timeout=11000).stdout
        builtins.open(os.path.join(SCR114, "predfold1129.out"), "w", encoding="utf-8").write(o_)
    for d_ in (SCR114, SUB114):
        if d_ and os.path.isdir(d_):
            for f_ in sorted(os.listdir(d_)):
                if f_.endswith(".out"):
                    sc_outs[f_[:-4]] = builtins.open(os.path.join(d_, f_), encoding="utf-8").read()
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
        decl = SD114.get(mname, {})
        print("   %-13s last line: %s" % (mname, last[:150]))
        for r, (cls_, key_) in sorted(reds.items()):
            sc_seen.append((mname, r, cls_, key_))
            d_ = decl.get(r)
            if cls_ == "TRACEBACK" or d_ is None or d_[1] != key_:
                sc_bad.append((mname, r, "UNDECLARED" if d_ is None else ("KEY CHANGED" if cls_ != "TRACEBACK" else cls_)))
        for r in sorted(set(decl) - set(reds)):
            sc_bad.append((mname, r, "DECLARED, NOW GREEN"))
    WD114 = os.environ.get("PREDFIX114_WRITEDECL", "")
    if WD114:
        with builtins.open(WD114, "w", encoding="utf-8") as fh:
            fh.write("# model\tred\tclass\twhy\tkey (red_key10: the red's own FAIL line text, no document line numbers)\n")
            for mname, r, cls_, key_ in sc_seen:
                fh.write("%s\t%s\t%s\t%s\t%s\n" % (mname, r, cls_, SD114.get(mname, {}).get(r, ("", "", "WHY?"))[2], key_))
    for x_ in sc_bad:
        print("   NOT AS DECLARED %s %s: %s" % x_)
    check("SUCCESSOR114", len(sc_outs) >= 24 and not sc_bad, "%d models read, %d reds, each against its declared "   # noqa: F821
          "key (%d declared): %s" % (len(sc_outs), len(sc_seen), sum(len(v) for v in SD114.values()),
                                     sc_bad or "all as declared"))
else:
    print("   LIGHT: SUCCESSOR114 not run")

PLANTS114 = {"s1": "RULE114", "s2": "RULE114", "s3": "TWIN114", "s4": "LOUD114", "s5": "RULE114", "s6": "ERRSWEEP114",
             "s7": "RULE114", "s8": "RULE114", "s9": "RULE114", "s10": "LOUD114", "s11": "SWEEP114",
             "s12": "ERRSWEEP114", "s13": "QUOTES114", "s14": "RULE114", "s15": "STALE114", "s16": "TAGS114",
             "s17": "OTHER114", "s18": "SUCCESSOR114"}
if SAB114 == "all":
    caught = []
    for q_, tgt in sorted(PLANTS114.items(), key=lambda kv: int(kv[0][1:])):
        env = dict(os.environ, PREDFIX114_SABOTAGE=q_, PREDFIX114_LIGHT="1")
        if q_ == "s18":
            env["PREDFIX114_READDUMP"] = "1"
        o_ = subprocess.run([sys.executable, "-I", "-B", MY114], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, env=env, timeout=3000)
        fl = [l_ for l_ in o_.stdout.split("\n") if l_.startswith("FAIL ")]
        ok_ = o_.returncode != 0 and any(l_.startswith("FAIL %s:" % tgt) for l_ in fl) and "Traceback" not in o_.stdout
        caught.append((q_, tgt, ok_))
        print("   PLANT %s -> %s: %s; FAIL lines: %s" % (q_, tgt, "CAUGHT" if ok_ else "NOT CAUGHT",
                                                       [l_[:90] for l_ in fl]))
    check("PLANTS114", all(c_[2] for c_ in caught), "%d plants, caught %d" % (len(caught), sum(c_[2] for c_ in caught)))   # noqa: F821

failed114 = [n_ for n_, ok_ in RESULTS if not ok_]           # noqa: F821
print("predfix114_model: %d checks, %d failed%s" % (len(RESULTS), len(failed114),   # noqa: F821
                                                  (" (%s)" % ", ".join(failed114)) if failed114 else ""))
sys.exit(1 if failed114 else 0)
