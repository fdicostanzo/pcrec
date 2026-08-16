#!/usr/bin/env python3
"""Generate tests/rungselect/patterns.txt — the reverse-deterministic rung's
differential population (eng_brep_design.md §5.1).

Committed and re-runnable, and the population is DERIVED rather than hand-listed
so that adding a body or a follow is one edit rather than a hundred. Run:

    python3 docs/design/rungselect_impl/gen_patterns.py \
        > tests/rungselect/patterns.txt

WHAT THE AXES ARE FOR. Each one exists because it discriminates something the
others cannot:

  BODIES split three ways on purpose. The rung-TAKING ones cover single-byte
  branches (the motivating cell), multi-byte branches (where an iteration's
  LENGTH varies and the backward walk has to decide it), a group inside a branch
  (§3.4's "the last iteration that ENTERED it" rule, the clause the plan row got
  wrong), and a three-way alternation (where the backward byte dispatch has more
  than two arms to get wrong). The DECLINING ones are controls: they must stay
  on the frames rung, and the differential over them is then a check that
  denying a rung nothing took changes nothing.

  COUNTS walk m and n through the shapes §5.1 names: m == 0, m > 0, m == n
  (one exit, no retreat at all), and the unbounded forms, which take the same
  code path with no ceiling. Every bounded count stays at or under
  PCREC_MAX_VM_REPEAT_COPIES, because the DENIED build is the one that
  replicates and it is the ground truth this differential is measured against.

  FOLLOWS decide whether the loop can RETREAT at all. A follow disjoint from the
  body's first set makes the quantifier possessifiable, and a possessified revdet
  loop owes no resume frame — a different emitted shape. A follow that OVERLAPS
  (`a` after a body that can consume `a`) is what forces the real retreat path,
  and it is the one that would be missing from a family built only out of
  "sensible" patterns. The EMPTY follow puts the loop at the end of the pattern,
  which is where a lazy quantifier's nullable-remainder conjunct lives.

  PREFERENCES: both, always. R24 S-F1 — an all-greedy sweep is structurally
  blind to the lazy conjunct, and this rung emits a genuinely different shape
  for lazy (it commits at the minimum and extends forward) rather than a mirror
  of the greedy one.
"""

# Bodies the rung is expected to TAKE: forward AND reverse unique-iteration.
TAKE = [
    "((a)|b)",        # the motivating cell's body: a group inside a branch
    "(a|b)",          # the same without the inner group
    "(?:a|bc)",       # branches of different LENGTH, so the walk decides one
    "((x)y|z)",       # a group inside the LONGER branch
    "(?:a|b|cd)",     # three-way dispatch backward
    "(?:(p)q|(r))",   # two groups, only one entered per iteration
]

# Bodies the rung must DECLINE, each for a different measured reason. They ride
# the same differential as controls: denying a rung nothing took must change
# nothing at all.
DECLINE = [
    "(?:ab|b)",       # forward-deterministic, REVERSE-ambiguous
    "(a|ab)",         # forward-ambiguous (U1)
    "(?:aa?)",        # forward-ambiguous (U2, not prefix-free)
    "(?:a|)",         # nullable
]

# The default cross product is deliberately narrower than the axes it is drawn
# from: this file rides `make test`, and a section that costs three gcc runs per
# pattern has to justify each one. `--full` widens every axis for a deeper sweep
# run by hand (or by a merge battery), the same quick/full split
# tests/vm/run_vm_tests.sh already uses. The narrow set keeps at least one
# member of every DISTINCT EMITTED SHAPE — m == 0, m > 0, m == n, unbounded,
# greedy, lazy, possessified, not — which is the property that matters; `--full`
# adds redundancy within those shapes, not new ones.
COUNTS = ["{0,2}", "{1,3}", "{2,2}", "*"]
COUNTS_FULL = ["{0,2}", "{1,3}", "{2,2}", "{0,8}", "{2,}", "*", "+", "?"]

# Kept small on purpose: the follow's job here is to decide RETREAT vs
# POSSESSIFY vs end-of-pattern, and three cases cover all three.
FOLLOWS = [
    "c",   # disjoint from most bodies -> possessifiable -> no retreat frame
    "a",   # overlaps -> the retreat path, which is the rung's hard half
    "",    # end of pattern -> the lazy conjunct's territory
]


def emit(pat, seen, out):
    if pat not in seen:
        seen.add(pat)
        out.append(pat)


def main():
    import sys
    full = "--full" in sys.argv[1:]
    bodies = TAKE + DECLINE
    counts = COUNTS_FULL if full else COUNTS
    if not full:
        # One body per distinct backward SHAPE, plus every decline reason.
        bodies = ["((a)|b)", "(?:a|bc)", "((x)y|z)", "(?:(p)q|(r))"] + DECLINE
    seen, out = set(), []
    for body in bodies:
        for count in counts:
            for follow in FOLLOWS:
                for lazy in ("", "?"):
                    # `?` and `*` and `+` take a preference suffix the same way
                    # a braced count does; `{2,2}?` is legal and is a no-op,
                    # which is itself worth sweeping since the emitter must not
                    # take a different path for it.
                    emit(body + count + lazy + follow, seen, out)
    # A handful of shapes the cross product does not reach.
    extra = [
        # a leading literal, so the search entry has to advance the start
        "z((a)|b){0,4}c",
        "z((a)|b){0,4}?c",
        # the rung INSIDE a group, and the group's own span across a retreat
        "(((a)|b){0,4})c",
        # two rung loops in one pattern, so the per-loop slot triples and the
        # shared recovery locals are both exercised at once
        "((a)|b){0,3}c(?:(p)q|(r)){0,3}d",
        # a rung loop next to a CURSOR loop, so the ladder mixes in one artifact
        "a*((a)|b){0,4}c",
        # a rung loop next to a FRAMES loop (the body is reverse-ambiguous)
        "(?:ab|b){0,3}((a)|b){0,3}c",
        # nested: the INNER quantifier must decline (single-level scope bound)
        "(?:((a)|b){0,2}c){0,3}d",
        # exact count with a group, where there is one exit and no retreat
        "((a)|b){3}c",
        # the body's own alphabet is the follow's, so every retreat is live
        "((a)|b){0,6}ab",
        # A NESTED FIXED-COUNT quantifier, which is the only nested quantifier
        # the rung admits and the only thing that exercises the backward
        # emitter's own replication arm. It has to sit in the MIDDLE of the
        # body: the Glushkov construction models `{2}` as a loop, so a fixed
        # repeat at either END of a body makes that end's positions carry a back
        # edge and prefix-freeness fails in that direction. Measured, and the
        # reason this shape is spelled with an `x` and a `y` around it.
        "(?:x((a)|b){2}y){0,3}z",
        "(?:x((a)|b){2}y){0,3}?z",
        "(?:x(?:a|b){2}y){0,3}z",
        # a group in EVERY branch, so the walk publishes two groups per step
        "(?:(x)(?:y|z)){0,3}w",
    ]
    for p in extra:
        emit(p, seen, out)

    print("# tests/rungselect/patterns.txt -- GENERATED, do not hand-edit.")
    print("# Source: docs/design/rungselect_impl/gen_patterns.py (committed);")
    print("# regenerate with `python3 docs/design/rungselect_impl/gen_patterns.py`.")
    print("# The axes and why each one is here are documented in that file.")
    for p in out:
        print(p)


if __name__ == "__main__":
    main()
