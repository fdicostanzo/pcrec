# vmrecg — five anomalous sabotage plants and the S684 miss on lane/vmrec

Tooling: a scratch helper in `scratch/vmrecg/` applied each row through `tests/mech/lib/replace.py` (the matrix's own
applier), rebuilt, ran the row's arm under the harness flags (`-O1 -std=gnu11 -Wall -Wextra -Werror`), and reverted `src/`.
No `src/` or `tests/memfn` file is changed by this lane; only the five sabotage scripts. No emitted byte moved (the plants
only exist inside the matrix's sabotaged builds), no kit change: the STOP RULE did not fire.

## Per row

### S105 (vm_stmt.c) — "expected expression before ']'"
- Cause: the re-aimed AFTER added a third `%s` to the bref printf's format but not an argument, shifting every later
  argument (`slot_values[\n]`).
- Change: the AFTER rewrites the format and the argument list together: the test is `slot_values[ns] != slot_values[ne]`
  (START != END), args `else, ns, ne, ns, ne`.
- Evidence: `tests/backrefs/numeric.rxt`: 78 passed / 10 failed, 0 compiler errors or warnings in the log.

### S106 (emit_vm.c) — implicit declaration of rx_span_match
- Cause: only the record's operand was zeroed; the `seam_entry` that decides which entry the artifact declares
  (`enc_mask`) still followed the caseless field, so the sensitive entry was called and never emitted.
- Change: second hunk in `vm_bref` makes `seam_entry = PCREC_ENCE_SPAN` (field ignored at both places).
- Evidence: `tests/backrefs/caseless.rxt`: 39 passed / 14 failed, 0 errors or warnings. The row's codegen and brefdiff
  arms are scored by the queued job.

### S135 (emit_vm.c) — unused parameter rx_search_from
- Cause: the `ngst++` (forces the `<p>_search_from` parameter) sat before `if (k > 0)`, so a zero-width body
  (`(?<=)z`, `z(?<=)`) got the parameter with no reader: `-Werror=unused-parameter` on `rx_match_anchored`.
  Measured before the fix on `tests/lookaround`: 116 failures, 50 error lines, all from this.
- Change: the bump rides each guard that READS the parameter (`k > 0`), at both arms (last branch and non-last branch).
- Evidence: whole `tests/lookaround` after: 2409 passed / 20 failed, 0 errors or warnings (the 20 are the startpos cells).

### S36 (vm_stmt.c) — 'w' undeclared
- Cause: the AFTER still used the pre-record spelling (`w->trn`, `w->bt[b_].mark`).
- Change: the AFTER guards the CURRENT emitted line with `0 &&`:
  `while (0 && run->trail_depth > run->resume_stack[frame_index].trail_mark)`.
- Evidence: `tests/vm/run_vm_tests.sh` (the row's `vm` arm): 56 passed / 2 failed, 0 warnings; the failures are the
  oracle sweep's wrong group spans (`(a)|(b)` on "a\nb" reports group 1 as (2,-1) instead of unset).

### S1845 (vm_stmt.c) — label+1 names a label that does not exist
- Cause: `lbl++` renders `goto rx_L<n+1>`, undefined.
- Change: a non-checkpoint label branch renders the FAIL target instead (a target that exists and is wrong); checkpointed
  branches are left alone, because redirecting them left `rx_trail_gc_at` / `rx_trail_compact` unused
  (`-Werror=unused-variable/function`, observed on the first attempt). SAB_DESC updated.
- Evidence: `tests/backrefs`: 520 passed / 368 failed, 0 errors or warnings.

## S684 (UNDETECTED, zero checks failed): the plant, not the check
- Pop line from the 747 log: `reach:ok(1/1)`, `memfnmanifest:0fail/14pass`, `memfnforms:0fail/5pass`.
- Why: C17 rule 1 and rule 3 and C12 all key on the FUNCTION a vocabulary-matching string literal sits in, and the
  vocabulary line that matters (`walk-open`, `search_vocab.tsv`) matches a `while (` whose condition the literal LEAVES
  OPEN. The original m6 plant split the literal (`"while ((%s_span_cursor + %d <= %s)"` then `") {\n ..."`) for exactly
  that reason (commit 962fcc4c9). The vmrec re-aim (45971212a) rewrote it as ONE closed literal
  `"while ((... <= %s)) {\n..."`, which no vocabulary line recognises, so nothing fires. Run on the planted tree:
  `site_manifest_check.py` 14 passed / 0 failed.
- The shared renderer is NOT the cause. A hand experiment (not committed) with the original split spelling placed in
  `vm_r_span`: `site_manifest_check.py` 13/1 (`rule 1 (static half): src/gen/vm_stmt.c:429 in vm_r_span spells a
  walk-open form ... no pending row names it`) and `run_form_checks.sh` 4/1 (`C12: src/gen/vm_stmt.c walk-open -: 1
  form(s) spelled, ceiling 0`). The caller `vm_r_span` is in no delegated row, and a respelling anywhere in
  `vm_stmt.c` is a function the manifest does not list, so rule 1 stands in for rule 3. The check still tells a
  respelled loop from a delegation; the vmrecf note that rule 2's reach is shared by the three rows does not weaken rules
  1/3/C12.
- Conclusion: the ROW should be re-aimed (restore the split literal in the AFTER: two `pcrec_sb_printf` calls, the first
  ending in `)`), not the check. Per the brief I did NOT re-aim it; S684 is in the queued job and will read UNDETECTED
  again until the manager rules. If the manager rules the re-aim, it is a two-line AFTER edit (text in the experiment
  above) and S684 alone re-runs in ~100 s.
- S511 (manifest plant, VMSTRIDE -> pending): hand-verified, `site_manifest_check.py` 14 passed / 2 failed (rule 4 on
  `vm_span_advance` and `vm_emit_span_scan`), so it should score DETECTED.

## Validation
- `make strict` clean; `python3 scripts/m6read_check_sab_anchors.py`: 1086 sabotages, 1121 anchor sites, all resolve (0 stale).
- Commit bec866e8a (pre-commit staged checks 52 passed / 0 failed).
- No check changed, so no section job.

## Queued (OWED)
| key | what | cap |
|---|---|---|
| 748-vmrecg-mech | `run_sabotage_matrix.sh S105 S106 S135 S36 S1845 S684 S511` (7 rows; dry-run clean, size rows=7) | 2400 (747 measured ~99 s/row) |

Completion line: `== mech run COMPLETE: 7 rows`. Expected: 6 DETECTED, S684 UNDETECTED (UNEXPECTED) until re-aimed.

## STATE AT HANDOFF
State: DONE for the five plants; S684 awaits a manager ruling (re-aim). Rulings file `vmrecg_rulings.md`: polled, last
entry "(none yet)", none applied. Branch lane/vmrec at the report commit; worktree clean apart from the untracked
manager files (deliver.txt, vmrec.done) and `docs/dev/artifact_size_log.tsv` (pre-existing, not mine).
