# s1fix report — review r1-s1 FIX-NOW items on the landed S1 code

## STATE AT HANDOFF
- Branch lane/s1fix, worktree worktrees/s1fix, committed. Last rulings applied: R1 (CONTRACT-2 spec fix, stamp unchanged), R2 (NMSOUND-2 plan note).
- DONE locally: `make strict` clean (rc 0); `tests/codegen/run_prechecks.sh` 399 passed, 0 failed (incl. the four new [1.3b] rows); the four new sabotage rows' SAB_REACH probes each print their marker on the built tree.
- OWED (box was held by queue job 300-main-oracle49-maketest; my jobs wait on the box lock, nohup, niced): (1) the zero-mover proof, `python3 scripts/emit_sweep.py --ref main --tree <worktree> --out $PCREC_TMPDIR/scratch/s1fix/sweep`, log `$PCREC_TMPDIR/scratch/s1fix/sweep.log` (verdict: 0 movers); (2) `make test-codegen`, log `.../codegen.log`; (3) the matrix `REACH_ONLY=1 ... S3070-S3073` (was queued, bounded by a 900 s timeout, expect it dead; the probes were run by hand instead, see above); (4) cloud: `scripts/cloudrun --owner main --kind test --name s1fix` and `--kind mechrows --rows S3070,S3071,S3072,S3073`.
- Every edit is comment/doc/test/diagnostic text or a behaviour-free helper (`vm_general_min_width`); abi stays 103 (no stamp or emitted line touched). The dead ATTEMPT branch in `attempt_entry` also dropped its `cand_front_min_width` call, which moves a WIDTH trace record (not an artifact byte); if a trace pin reddens in test-codegen, that is the cause.
- ID NOTE: the brief's block S1965-S1974 is ALREADY TAKEN on main (the lookbehind rows S1960-S1988 exist). I used S3070-S3073 (highest id anywhere in the worktrees was S3064; nothing in the docs names S3065+). Four rows, not ten: one per new site.

## CHANGES
- Review record: docs/dev/reviews/2026-11-12-r1-s1.md plus its critic texts in the same-named directory; index line in docs/dev/reviews/CLAUDE.md.
- CONTRACT-1: match_api.md §6.3.4 `"empty"` row says the anchored entries of a switched pattern answer -1 and never give up; abi_changelog.md entry for 102 carries a review note.
- CONTRACT-2 (R1): match_api.md §6.3.3 `"selected"` row says the switch keeps its rung's value (a retry rung reads `"collapsed-prefilter"` on the empty artifact). No stamp change.
- CONTRACT-3: src/core/compile.c: the `--emit-ir` refusal names its cause (`pcrec_fact_never_matches`): "because it matches nothing" vs the unset-capture-slot text with its "or" gone.
- DFAMINW-1: src/gen/emit_dfa.c `pf_close` comment states the real argument (start-state block, shortest accepting path of the forward machine = `width.bmin`, `a*bcd` example); tuning.md §2.55¶1 carries the same sentence.
- NMSOUND-1: facts_listing.md §4.1.2¶12 says the island row (`"char-step"`) can win before `empty` while the fact still reads `empty-machine`.
- NMSOUND-3: src/ir/dfa.c cite now src/facts/kset.c.
- CHECKS-2: tests/codegen/run_prechecks.sh §1.3b: the four emitted sites (VM entry check, VM `attempt_max`, DFA front check, `pf_close` check) present by default and absent under `--harness=no-min-width` (replaces what [1.1b]/[1.2] gave up). Sabotage rows S3070 (VM entry), S3071 (VM bound), S3072 (`pf_close`), S3073 (DFA front), each SAB_SUITES=prechecks with a REACH probe.
- CHECKS-3: `vm_general_min_width()` in src/gen/emit_vm.c replaces the two spellings of `check && !ceiling` (byte-identical by construction).
- CHECKS-4: the unreachable `if (minw)` branch in `attempt_entry` removed; a comment names the trigger (a width fact sealed on the attempt machine).
- CHECKS-5: emit_vm.c's [DD-14.EMPTY] title retitled as the ceiling's stamped spelling.
- NMSOUND-2 (R2) plan NOTE on [NEVER-MATCH] (machine-final epoch beside PfEpoch, the `(*ACCEPT)` trigger note for `pcrec_minw`, the unlock list).

## OWED
See STATE AT HANDOFF: emit_sweep 0-mover proof, test-codegen, cloud test + mechrows S3070-S3073.

## Follow-up (s1fix2)
Cloud test run 43331915793 went red on test-codegen's K37 lint: run_prechecks.sh `HBIN=` line named `"$PCREC"` with no bound token. Fixed: HBIN derives from `$ROOT_DIR/build/pcrec-harness`; the grep of the K37 site regex over the file finds no unguarded line; prechecks 399/0. REACH_ONLY matrix S3070-S3073 later finished: 4 of 4 REACHED. Re-dispatched cloud test as s1fix2.
