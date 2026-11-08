# u3tgt — [XARCH-DEV] target seam unit U3 (pcrec half)

STATE: stopped (premise test failed before any edit).

## Summary

The brief's PREMISE TEST failed: `git show 6418080b2:memfn/include/memfn.h | grep -n mf_art_target`
finds nothing. 6418080b2 is "u2: WIP report, the U3 interface sheet (before any code)" and is still
lane/memfn-u2's tip; the kit's U2 lane (worktrees/u2) has UNCOMMITTED edits to memfn.h and
levels.def, and its memfn.h mentions `mf_art_target` only in a comment. With no `mf_art_target`
entry, no guard/region text from the kit and no admission rule, U3 cannot be built or tested
(nothing to call, no bytes to place, no mover to prove). No code was written; nothing merged.
Relaunch when lane/memfn-u2 has committed its code (the premise test then passes on its tip).

## What crosses the seam

Not built. The sheet (u2_report.md "The U3 interface sheet", items 1-10, at 6418080b2) was read
and is sufficient to code against once U2's code exists: `mf_art_target(art, t)` after
`mf_art_begin`, the guard from `mf_family_c_of(t->family)->guard`, the region from
`mf_target_c_of(t)->region_open/_close`, TARGETS from `t->name` / `t->family->name`.

## Emitted text

Not built; no bytes moved.

## Retired readers

Not built. Inventory for the relaunch (grep `MF_P_PORTABLE_ONLY`, pcrec side, this tree at
9161402da): lib/pcrec.h, src/core/internal.h, src/gen/memfn_sites.h, src/gen/memfn_targets.c (3),
tests/memfn/{arm_fixtures.c (12), proof_check.c (2), proven_check.c (2), run_proof.sh},
tests/mech/sabotages S722, S1224, S2930 AND S1864_policy_not_portable.sh (3 hits; not in the
brief's list; the relaunch should re-aim or retire it too).

## Pins and abi

Not touched; no abi bump taken.

## Checks

None run (no change to check). Premise test output: empty grep at 6418080b2.

## STATE AT HANDOFF

stopped; rulings file u3tgt_rulings.md empty (no entry applied); no jobs queued; owed: nothing
(U3 not started). Next: relaunch U3 against lane/memfn-u2 once its code is committed.
