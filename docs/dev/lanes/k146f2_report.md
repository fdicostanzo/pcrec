# k146f2 report: review r62's FIX-NOW rulings applied to the K146 fix

## Summary

Branch lane/k146f2, cut from lane/k146fix at 7e93da96b. Every finding ruled
FIX-NOW in docs/dev/reviews/2026-11-20-r62-k146fix.md is fixed, one commit
each with its id in the subject line. K147 is filed, [K147-POSSESSIFY-DEPTH]
is a plan row, and [LINT-FRAME] is ready. The only code edits are comments
in src/gen/emit_vm.c, src/core/internal.h and the text of one limits.def
row; no emitted byte should move (identity sweep queued, see Validation).
The rulings file k146f2_rulings.md was empty at every check.

## Fix by finding

- DEPTH-1 (91e19bd22): `altrep;;(a|b;c;)*;;all;0` added to DEPTH_FAMILIES.
  Measured at depth 250 on the 442,368-byte thread: 353,512 B (1,344 B per
  level), rc 0; depth 251 refused by name. The musl 131,072-byte depth was
  bisected: 84 for altrep, 87 for lookrep, 118 for optnest. limits.md §3.10¶3
  now names `(a|b(a|b…c)*)*` as the worst (lookrep and optnest follow) and
  ¶4 gives 84/87/118. The other figures re-read from the run
  (run_compile_stack.sh 43 passed, 0 failed) are unchanged.
- DEPTH-2 (67b29e35e): limits.def's PCREC_COMPILE_STACK_BUDGET text now says
  "at least 1.2x the worst measured family (1.25x today)". The value is
  unchanged. This moves `--list-limits` text, so a dumps mover for that
  row is expected in the sweep below.
- DEPTH-3/DEPTH-4 (3e5a1c37e): one sentence in §3.10¶1 names the exception
  (`(a|b(a|b…\1)*)*` from depth 174, 26 with a backreference per group) and
  K147, and says ¶2-¶4 do not hold for that shape. Both witnesses re-run:
  depth 173 hw 441,096 and 174 rc 139; depth 25 hw 420,744 and 26 rc 139.
- EMITTED-1/CHECK-3 (2506fd696): the two answer-blind cells in gen_corpus.py
  are replaced by the emitted critic's seven capture-bearing patterns
  (k146caps.rxt: depth 3, depth 40, plain star, `(?:` wrappers, a consumer,
  negative lookahead, multi-literal first branches), and quantified.rxt is
  regenerated from libpcre2 by the generator (byte-identical regeneration of
  all 14 files was checked first). The expectations equal the critic's
  oracle-derived ones line for line. harness run.sh on the file: 264 cases
  passed, 0 failed; verify_rxt.py 100%.
- HOUSE-1 (52ec788a8): internal.h's PCREC_OWN_FRAME comment states both uses
  (scratch dead before the walk recurses; a recursive arm kept out of its
  dispatcher's frame, K146, precedent rb_look_item); coding.md §2.4 gets
  one line pointing at it.
- HOUSE-2 (010391dc8): the vm_emit_node header no longer says "every
  recursive arm"; it says which arms are marked (those that carry locals),
  names vm_splice, vm_call and vm_callout as recursive and unmarked, and
  vm_ctx, vm_bref and vm_var as marked without recursing. The reword was
  chosen over marking vm_splice (r62: marking them moved no family).
- HOUSE-3 (38d4255f2): vm_cost's arms are calls, not tail calls.
- HOUSE-4 (a4f8353d5): one sentence names vm_count_slots' A_ALT arm (the
  third vm_isl_build reader, frame 0x70) as exempt and says what to do if
  it ever matters.
- HOUSE-5 (5c9ba308b): vm_cost_alt_island moved above vm_cost_alt's header;
  vm_alt's header trimmed so the [ENG-ISL] statement lives once, in
  vm_alt_island's.
- HOUSE-6 (c94a3cf6a): the K146 entry is retitled FIXED ON lane/k146f2
  (awaiting landing) with the cause confirmed and the fix stated; the plan
  row [K146-VMCOST-DEPTH] says what the code now does. Its STATE stays
  not-started because it sits in Boonies (plan_lint PL13).

## K147 and LINT-FRAME records

- known_issues.md K147 (above K146): witness, the one-backreference and
  per-group-backreference depths, cause (per r62's gdb, not re-run: first_of
  and text_first in src/opt/possessify.c), fix by the same general depth
  mechanism, and UNLOCK-2's family survey as its notes.
- plan.md: [K147-POSSESSIFY-DEPTH] STATE:not-started, trigger: the next
  lane of K146's family, right after K146 lands.
- plan.md: [LINT-FRAME] is STATE:ready with a `ready:` line and a status
  note that K146 fired its trigger (r62 UNLOCK-1), scheduled after K147. The
  row moved from Backlog into Active, because plan_lint PL13 wants ready
  rows there.
- `make -s test-plan-lint` passes (PL13/PL10 fixed on the way).

## Checks run

- `make -j8` green on the worktree (before the last comment edits; the queued
  build/strict redo it).
- tests/thread/run_stackdepth_tests.sh: 5 passed, 0 failed, 1 known pinned.
- tests/thread/run_compile_stack.sh: 43 passed, 0 failed (with altrep).
- tests/harness/run.sh and verify_rxt.py on tests/lookaround/quantified.rxt:
  green (above).
- `make -s test-plan-lint`: green. The commit hooks' staged checks passed.

## Validation queued

Batch b20261120112322125373, owner k146f2, prio 400, stages in
/var/tmp/pcrec-pcrec/scratch/k146f2/stages.txt:
`400-k146f2-b20261120112322125373.build`, `.strict`, `.ident`, `.test`
(perfrun label k146f2-maketest).

- `.ident` runs emit_sweep (reference: the archived base f8789cd2e build in
  scratch/k146fix/base; subject: this worktree's build; movers in
  scratch/k146f2/sweep/movers.tsv) and then ident_check.py with an EMPTY
  census. It deliberately exits 0 so `.test` still runs; read the verdict
  from the `IDENT-VERDICT ident_check rc=N` line at the end of
  /var/tmp/pcrec-pcrec/scratch/k146f2/ident.log. Expected: 0 unexplained on
  every emitted stream; ONE dumps mover, `--list-limits`' text for
  PCREC_COMPILE_STACK_BUDGET (DEPTH-2), is the declared exception. Anything
  else is a real mover.
- `.test` is `make test`. The larger quantified.rxt (7 blocks, not 2) moves
  population pins (rxtsource census, start-set manifests, size tripwire)
  further than k146fix's own run did; a red there on a pin is a re-pin
  follow-up, not a regression.
- Read verdicts with `scripts/boxqueue state KEY` and `scripts/verdict`.

## STATE AT HANDOFF

STATE: delivered; branch lane/k146f2 committed with this report. Last
rulings entry applied: none (file empty).

OWED: none (the queued jobs above are the validation, not owed lane work).

The identity
verdict is NOT yet taken (queued), so no 0-movers claim is made here. Not
done, by brief: merge, closing K146/its plan row, K147's fix, [LINT-FRAME].
