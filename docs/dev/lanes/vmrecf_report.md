# vmrecf — the three step-(a) `make test` reds on lane/vmrec

Source: job 745-vmrecm-test's `job.log.make` (it hit its 3600 s cap: build + strict + identity gate + full make test is
~55-60 min). Its three reds were real. All three are fixed without moving an emitted byte.

## Per red

### 1. [TT-9] `tests/codegen/run_stmt_writer.sh` in neither san manifest
- Cause: the step-(a) ST check is a static script (no compiler invocation), added to `make test-codegen` but not to the
  sanitizer manifests.
- Change: one row in `tests/lib/san_excluded.txt`, reason `NO-C-RUN` (the same reason the other file-reading codegen
  scripts carry), placed in alphabetical order after `run_start_landing.sh`.
- Evidence: queued section job 744-vmrecf-sect (OWED, see below); the entry names an existing script that is not in
  `san_scripts.txt`, the two conditions the check tests.

### 2. [C15] unprefixed exports from `src/gen/vm_stmt.c`
- Cause: the record builders and fragment/target constructors (44 `vm_*` symbols) were external with no `pcrec_` prefix.
- Change: 43 of them are used from `src/gen/emit_vm.c`, so they take the house prefix (`vm_b_label` ->
  `pcrec_vm_b_label`, likewise every `vm_b_*`, `vm_frag*`, `vm_stmt_*`, `vm_tgt_*`), by whole-word rename in
  `vm_stmt.c`, `vm_stmt.h`, `emit_vm.c` and the 16 sabotage scripts whose plants/anchors quote those names (rename
  only; each anchor and its replacement were renamed together, intent unchanged). The 44th, `vm_b_step`, was used by
  nothing (the builder for `VK_STEP` has no caller; `make strict` showed it once it was static): the dead builder is
  deleted, the `VK_STEP` renderer row is untouched.
- Evidence: `make strict` clean (`strict: whole tree compiles clean with -Werror -Wshadow`); `nm -g` on the new
  `libpcrec.a` is the C15 population check (OWED to 744-vmrecf-sect for the section itself).

### 3. memfn-manifest rule 2: `vm_piece_render` an unlisted door caller
- Cause: step (a) moved the kit door calls out of `emit_vm.c` (`vm_run_site`, `vm_emit_span_scan` built and rendered the
  kit text in place) into the one piece renderer `vm_piece_render` (`VP_KIT`), which calls `pcrec_memfn_emit`. The
  manifest's `companions` column named the old callers, not the new one.
- Change: `vm_piece_render` appended to the `companions` of the three rows whose door moved: VMRUN, VMSPAN, VMSTRIDE
  (`tests/memfn/site_manifest.tsv`). The delegation itself is unchanged; no new row, no new site. Note for the next
  reader: rule 2's reach clause (`a delegated row nothing renders`) is now satisfied for these three rows by any VM kit
  render, since all three share the one renderer; the per-row reach lives in the traced kinds column (rule 5), which is
  untouched.
- Evidence: queued (OWED) test-memfn-manifest inside 744-vmrecf-sect.

## Byte identity (STOP RULE did not fire)
- Spot check: 16 patterns x 4 arms (default, `--engine=vm`, `-fcomments`, `--no-captures`) = 64 compiles, emitted C,
  header, stderr and rc compared between a build of the pre-fix commit fe819672d (`git archive` to
  `scratch/vmrecf/base/`) and the fixed tree: 64 compiles, 0 differ. Only C identifiers inside the compiler changed.
- The identity gate (744-vmrecm-ident, 68 arms, 0 movers) was not re-run: nothing under `src/gen` moved beyond rename
  and the deletion of an uncalled function.
- `make strict` clean after the last source commit.

## Process note
`boxlock status` showed the lock HELD-ORPHAN by the dead 745 job: its `make test` tree (gnutimeout 2700 -> make -j2 ->
test-memfn-g2) was still running in this worktree 64 minutes in, competing with my rebuild. I stopped it with
`scripts/safekill 132455` (the lane's own stray). Then the box queue held the lock for long qsplit/fsfix/p1mech jobs, so
instead of waiting on `boxlock run` I queued the three sections as a job.

## Queued (all dry-run clean at `scripts/boxqueue add`, one stage per job)

| key | what | cap |
|---|---|---|
| 744-vmrecf-sect | make; `make -k test-memfn-link test-memfn-manifest test-codegen` | 1800 |
| 745-vmrecf-test | make; perfrun make test (81 sections); after vmrecf-sect | 3600 (make test alone measured ~1600 s) |
| 746-vmrecf-mech | S1840-S1849 (10 rows); after vmrecf-test | 3600 |
| 747-vmrecf-mechre | the 29 re-aimed rows; after vmrecf-mech | 18000 (LONG-JOB, per-row time unmeasured) |

Job scripts: `/var/tmp/pcrec-pcrec/scratch/vmrecf/74[4-7]-*.job`. 746/747 mirror vmrecm's; 747's S-ids are unchanged
(the rename touched anchor text only; the rows resolved at enqueue).

## STATE AT HANDOFF
Fixes committed (9f797cadf, a0dfd1ce8), `make build`/`strict` clean, 64-compile spot identity 0 differ. Validation
OWED: jobs 744-747 queued, none run. Reads: 744 `job.log.sect` ("sect: DONE rc=0", plus no `*** [(Makefile:N: )?test-`
line), 745 `job.log.make` via `scripts/verdict`, 746/747 `== mech run COMPLETE`. If 744 shows [SABANCHOR] red, a
sabotage script still quotes an old `vm_` name (grep the old names, `git grep -w`). Last rulings entry applied: none
(vmrecf_rulings.md had no entries).
