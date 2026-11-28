#!/usr/bin/env python3
"""predfix112_model.py: lane predfix112's evidence, the successor of predfold1127_model.py.

The fix after review r112 (docs/dev/reviews/2026-11-27-r112-predfold1127.md) and the fold of two owner rulings,
array-gate and body-own-name (record docs/design/plan_row_bodies/COND-FAMILY.md, 2026-11-27). DESIGN evidence
only: nothing here rules; no check under `make` reads it.

It LOADS predfold1127's model unchanged up to its checks (`# ==== CHECKS`; the older models load through it), then
patches its walker WALK1127 in one place, switched by X112[0] (off: predfold1127's walker as merged, the control):
  BODY112  body-own-name, from the statement as asked: "a path that skips nothing is always legal and reads the
           label directly under its last step; one-path limits only reads that skip a step." At each step, when
           some target of the name lies directly under the step (no node between), the targets reached by a skip
           are not counted; the direct ones keep the label flow (the last mention). Applied BEFORE the gate check,
           so a gate beside a direct target is not counted either (the statement's "always").
  array-gate is predfold1127's printed side (READ1127["array"] = "error"), now RULED.
  GROUND112 (a switch, never the printed rule) models the owner's own ground for the call case ("the d from A is
           outside and would have to gate through rx but rx as an arg cant be directly on a path"): BODY112 off,
           and a target reached across an argument's place is not counted when another target is.
Every legal printed line is also answered by MECH111 (python `re` on a regex built mechanically from the program
text and its bindings' bodies). The verdict is the last line, `predfix112_model: N checks, F failed`; it exits
non-zero iff that line reports a failure.
PINNED COMMITS (review r112 COORD-1): this model reads git ONLY by commit id (START112 below). The older models it
re-runs still read by branch NAME in one place: predfold1123_model.py reads `lane/pred-rev28:` (a clone without
that local branch turns predfold1123 QUOTES and predfix111 SUCCESSOR111 red); those lane files are historical and
are not edited.
`PREDFIX112_LIGHT=1` skips SUCCESSOR112; `PREDFIX112_SUCCDIR=DIR` an existing scratch directory for the successor
outputs; `PREDFIX112_READDUMP=1` reads DIR instead of re-running; `PREDFIX112_SABOTAGE=sN` plants one wrong rule,
fact or text per check (PLANTS112); `=all` runs each plant in its own LIGHT subprocess.
Run: `timeout 6000 python3 -I -B <this dir>/predfix112_model.py`.
"""
import builtins
import os
import re
import subprocess
import sys

MY112 = os.path.abspath(__file__)
HERE112 = os.path.dirname(MY112)
LANES112 = os.path.normpath(os.path.join(HERE112, ".."))
P1127 = os.path.join(LANES112, "predfold1127_evidence", "predfold1127_model.py")
START112 = "2d7718d4e"                                       # this lane's starting commit (lane/predfix112), PINNED
SAB112 = os.environ.get("PREDFIX112_SABOTAGE", "")
LIGHT112 = os.environ.get("PREDFIX112_LIGHT") == "1"
_src1127 = builtins.open(P1127, encoding="utf-8").read()
_a112 = _src1127.index("\n# ==== CHECKS (a probe loads the model up to this line)") + 1
_sav112 = {k: os.environ.pop(k) for k in list(os.environ)
           if k.startswith(("PREDFOLD1127_", "PREDFIX111_", "PREDFOLD1125_", "PREDFIX90_"))}
__file__ = P1127
exec(compile(_src1127[:_a112], P1127, "exec"), globals())    # noqa: S102  predfold1127's engines, unchanged
__file__ = MY112
os.environ.update(_sav112)
X112 = [True]
GROUND112 = [False]


def s112(q):
    return SAB112 == q


# ================================================================== BODY112: the one patch to WALK1127
_W_OLD = _src1127[_src1127.index("def walk1127(P, path"):_src1127.index("class Prog1127(Prog111):")]
_HOOK = ("                uniq.append(c)\n")
_BODY = _HOOK + (
    "        uniq = _body112(uniq)                            # body-own-name (predfix112)\n")
assert _W_OLD.count(_HOOK) == 1, "WALK1127's hook moved"
exec(compile(_W_OLD.replace(_HOOK, _BODY), P1127 + " (patched by predfix112)", "exec"), globals())   # noqa: S102


def _body112(uniq):
    """body-own-name: a target directly under the step (nothing between: c[2] empty) is read; targets reached by a
    skip beside it are not counted. GROUND112: instead, a target across an argument's place is not counted when
    another target is."""
    if GROUND112[0]:
        own = [c for c in uniq if not any(n.k == "arg" for n in c[2])]
        return own if own and len(own) < len(uniq) else uniq
    if not X112[0] or s112("s1"):
        return uniq
    direct = [c for c in uniq if not c[2]]
    return direct if direct and len(direct) < len(uniq) else uniq


READ1127["array"] = "error"                                  # array-gate, RULED: "error. Agree with lean"
READ1127["direct"] = "error"                                 # predfold1127's switch stays as merged; BODY112 decides
