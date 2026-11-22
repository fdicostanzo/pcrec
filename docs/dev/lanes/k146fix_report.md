# k146fix — K146: the compile-thread stack overflow on nested quantified lookarounds

## Summary

K146 is fixed by the tree's existing depth mechanism. The nesting cap
(`PCREC_MAX_GROUP_DEPTH` = 250) bounds recursion depth. The stack budget
(`PCREC_COMPILE_STACK_BUDGET`, limits.md §3.10) is measured per nesting
family by `tests/thread/run_compile_stack.sh`. The fix shrinks frames with
the house primitive `PCREC_OWN_FRAME`, the same rule l1ttri 2e9e86126
applied. K146's shape now has its own `DEPTH_FAMILIES` row, `lookrep`, so
the bound is checked. There is no private guard, no new limit and no new
diagnostic: depth 251 is refused by the parser exactly as for every
sibling. The siblings do not use an explicit stack, so neither does this
fix.

- Witness `(?=a|b`×N `c` `)*+`×N on the 442,368-byte thread: main SIGSEGVs
  from N=180. The branch compiles N=250 in 297,536 B, and N=251 is refused
  by name.
- Identity: emit_sweep, base main f8789cd2e against the branch, over the
  branch tree's population. ZERO movers and ZERO asymmetric rows on every
  stream. ident_check.py with an empty census reports 0 unexplained.
- No family got worse. optnest@250 fell from 372,296 to 257,168,
  altnest@250 from 295,224 to 136,392, optnest-vm@250 from 293,984 to
  241,064, grp/callouter/callinner from about 160 K to 120,552. Every other
  family is unchanged.
- Spec hunk: yes, limits.md §3.10¶2-¶5 (re-measured figures and the new
  worst family). The budget VALUE and its `limits.def` row are unchanged.

## Reproduction

At main f8789cd2e, the driver `tests/thread/compile_stack_driver.c` ran on
a 442,368-byte thread with the same CFLAGS as the Makefile:

| N | main | branch |
|---|---|---|
| 50 | hw 140,568 | hw 92,464 |
| 100 | hw 257,368 | hw 143,664 |
| 179 | hw 441,912 | hw 224,560 |
| 180 | SIGSEGV (139) | ok |
| 250 | SIGSEGV (139) | hw 297,536 |
| 251 | refused, "too deeply nested" | refused, same |

On main the smallest crashing N is 180, which matches K146. The growth was
2,336 B per nesting level.

## Cause

The r58 hypothesis named only part of the cause. A gdb backtrace at the
N=200 crash puts it in the VM EMITTER, not in `vm_cost`. Each paren level
of this shape is about five AST levels (ALT, CAT, LOOK, ATOMIC from `*+`,
REP). The emitter's dispatcher `vm_emit_node` had every recursive arm
inlined into it (`vm_alt`, `vm_cat`/`vm_emit_f`, `vm_look` with
`vm_look_behind`, `vm_atomic`, `vm_cap`, ...). Its frame was therefore the
union of all their locals, 544 B (from -fstack-usage and per-frame SP
deltas). It was paid four times per level, plus `vm_star` (152) and
`vm_rep` (8), for 2,336 B per level.

Once the emitter was fixed, `vm_cost` became the deepest walk, as the r58
note had said. Its dispatcher had the same inlined-arm union (304 B ×4 per
level). `vm_cost_rep` carried 480 B, of which 256 is the revdet arm's
`int grp[PCREC_MAX_REVDET_BODY_GROUPS]`, used only for its count. The two
`vm_isl_build` call sites (`vm_alt`, `vm_cost_alt`) held a `VmIsl` trie by
value in the recursing frame.

## Fix

All changes are in `src/gen/emit_vm.c`. Each moves locals that are dead
before the recursion into a callee marked `PCREC_OWN_FRAME`, or marks a
recursive arm out of line:

- Emitter arms: `vm_emit_f`, `vm_alt`, `vm_rep`, `vm_atomic`, `vm_look`,
  `vm_look_behind`, `vm_ctx`, `vm_cap`, `vm_bref`, `vm_var` and `vm_cat`
  are marked `PCREC_OWN_FRAME`. At -O2 the dispatcher now tail-calls them
  (checked in the objdump: `jmp vm_cat`, `jmp vm_alt`, ...), so a level
  pays only the frames on its own path.
- `vm_alt_island`: a new own-frame helper. It holds the `VmIsl` trie and
  emits the island. `vm_alt` calls it first, so the order is unchanged.
- Cost arms: `vm_cost_cap`, `_cat`, `_alt`, `_rep`, `_atomic`, `_look` and
  `_call` are marked `PCREC_OWN_FRAME`. `vm_cost_alt_island` is a new
  own-frame helper that returns the island's frame charge, or -1.
- `vm_rev_ncaps(body)`: a new own-frame helper that returns the revdet group
  COUNT. It replaces the 64-int scratch array in `vm_cost_rep` and
  `vm_count_slots_rep`, which only read `ng`. `vm_revdet_rep` (the
  emitter) still has its array, because it uses the numbers. No measured
  family reaches it, so it was left alone and is listed as residual.
- Comments: `vm_emit_node`'s header states the rule (every recursive arm is
  its own frame; a new recursive arm is marked the same way). The stale
  "this function is inlined into vm_emit_node" note in `vm_look_behind` is
  corrected.

The result is 1,027 B per level for `lookrep` (was 2,336). Its deepest walk
is now `vm_cost`. A further cut is possible (`vm_cursor_applies`'s 1.8 KB
leaf, the `Cost` returns), but nothing measured needs it.

Tests:
- `tests/thread/run_compile_stack.sh`: new `DEPTH_FAMILIES` row
  `lookrep;;(?=a|b;c;)*+;;all;0`. The control is the base library: against
  main's libpcrec the row FAILS ("lookrep nested 250 deep KILLED
  pcrec_compile (killed, exit 139)", 40/41). Against the branch the script
  passes 41/41.
- `tests/lookaround/quantified.rxt`, through its generator
  `tests/lookaround/gen_corpus.py`: two blocks with K146's shape eight
  deep. The first is the bare witness. The second is the witness followed
  by a consumer, `^(?:…)b`. The cells are 6 in total, and libpcre2 10.46
  and python `re` agree on all of them (the generator marks no
  `# pcre2-only`). Regenerating changes only quantified.rxt; the other
  files come out byte-identical. The corpus uses depth 8, not 250, for two
  reasons. A harness compile runs on the main thread, so a corpus block
  could not reproduce the crash at any depth; the depth-250 regression
  check is the `lookrep` row. And at depth 250 the artifact is 790 KB, with
  gcc taking 8.5 s and 420 MB per compile, which every corpus sweep would
  pay. Harness: 32 passed, 0 failed. verify_rxt.py: ALL CHECKS PASSED.

Spec (D80): `docs/spec/limits.md` §3.10.
- ¶3 names the new worst family, `lookrep`, at 297,536 B and about 1.0 KB
  per level. optnest is 257,168 B and about 0.95 KB per level. The
  lookaround/atomic/named/inline-option families are at most 212,696 B.
  Plain groups are 120,552 B. The compound route is 225,496 B, about 13 KB
  over its plain nest. The depth-251 refusal is at most 214,152 B.
- ¶4 gives the depths at 128 KB, measured by bisection: lookrep 87, optnest
  118, the lookaround family 145-159, plain groups 250.
- ¶2 and ¶5 say "at least 20%" headroom instead of "about 20%".

Several of the old ¶3 and ¶4 figures had already drifted on main before
this change: optnest@250 was 372,296 against a stated 362,736, and plain
groups at 128 KB reached 197 against a stated 250. The new figures are
today's measurements. MANAGER'S CALL, not made here: the budget is now
about 1.49× the worst family. Lowering it (297,536 × 1.22, rounded up to
16 KB, is 376,832) would tighten a caller promise and move the
`--list-limits` dump and the `limits.def` text. It is left at 442,368.

`docs/dev/plan.md` [K146-VMCOST-DEPTH] gains a status line naming this
branch. Its STATE stays not-started, because plan_lint PL13 refuses a
started row outside Active. Closing it, and K146 in known_issues.md, is
for landing.

## Identity

`scripts/emit_sweep.py --ref-bin <git archive f8789cd2e>/build/pcrec --bin
worktrees/k146fix/build/pcrec --tree worktrees/k146fix --movers-out …`. It
ran under `boxlock run --label k146fix-identity`, ending
`emit_sweep: DONE rc=0`. The self-check passed at full reach. Real run:
c-default, c-vm, emit-ir-vm, facts, the four emit-ir-auto arms and stderr
each have population 7,224 with movers=0 and asymmetric=0. Composition has
466 files and 88 artifacts with movers=0, and dumps have 7 with movers=0.
The verdict was taken from `docs/dev/lanes/sae1_evidence/ident_check.py`
with an EMPTY census, not from emit_sweep's rc: `census movers: 0`,
`== ident_check COMPLETE: 0 unexplained`, rc 0.

The binary swept was built before the last two edits. Those edits are
comments only in emit_vm.c (the `vm_emit_node` header and the
`vm_look_behind` arena note), and they change no code.

Log: `/var/tmp/pcrec-pcrec/scratch/k146fix/sweep.log`, with the movers file
next to it in `sweep/movers.tsv`. These are scratch files, not committed.

## Depth check

Every family at 250 and 251 on the 442,368-byte thread (high-water bytes),
main → branch:

| family@250 | main | branch |
|---|---|---|
| lookrep (new) | SIGSEGV | 297,536 |
| optnest | 372,296 | 257,168 |
| optnest-vm | 293,984 | 241,064 |
| compound | 225,496 | 225,496 |
| inlineopt | 212,696 | 212,696 |
| look / lookbehind | 204,552 | 204,552 |
| named | 200,552 | 200,552 |
| atomic | 196,552 | 196,552 |
| starnest | 144,504 | 144,504 |
| altnest | 295,224 | 136,392 |
| callouter / callinner | 160,856 / 160,312 | 120,552 |
| grp / ncgrp | 159,768 / 120,552 | 120,552 |

The depth-251 refusals are unchanged, at most 214,152. The WIDTH cases are
unchanged. The control dies by signal as before. Full run on the final
build: `checks passed: 41, checks failed: 0`, file
`tests/thread/run_compile_stack.sh` run directly with the worktree's
build/.

At a 128 KB thread (bisection, main → branch): optnest 74 → 118, lookrep
45 → 87, grp 197 → 250. look 152, atomic 159, named 155 and inlineopt 145
are unchanged.

## Validation queued

- Done in the lane: `make` and `make strict` in the worktree are green
  ("strict: whole tree compiles clean with -Werror -Wshadow").
  `run_compile_stack.sh` passes 41/41. The harness on quantified.rxt has 32
  passed and 0 failed, and verify_rxt.py on it passes 100%. The identity
  sweep is above.
- Queued: `make test` on lane/k146fix through `scripts/boxqueue batch`,
  owner k146fix. Its job keys are in STATE AT HANDOFF. A new .rxt block
  moves population pins (rxtsource census, start-set manifests, size
  tripwire), and this run is what reports them. Those re-pins are OWED to
  a follow-up if it goes red on them.

## STATE AT HANDOFF

STATE: delivered. The branch lane/k146fix is committed, and this report is
committed. The rulings file `k146fix_rulings.md` was empty at every check,
so no ruling was applied.

OWED: none in the lane. The `make test` is QUEUED, not owed: it is batch
b20261120104514388223, jobs `400-k146fix-b20261120104514388223.build`,
`401-k146fix-b20261120104514388223.strict` and
`402-k146fix-b20261120104514388223.test` (perfrun label
k146fix-maketest). They wait behind `200-dhremeas-timing`, which held the
box at handoff. Read the verdict with `scripts/boxqueue state KEY` and
`scripts/verdict`. If it is red on a population pin moved by the two new quantified.rxt
blocks, a follow-up re-pins it. The manager runs the code critic round
before landing. Not done here, by brief: merge, closing the plan row and
the K146 entry, any change to the budget value.

Residual: `vm_revdet_rep` still keeps `grp[64]` on a recursing frame, but no
family reaches it. `vm_cursor_applies` is a 1.8 KB leaf paid once.
