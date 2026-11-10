# s30amrg report

## Summary

Lane s30amrg (2026-11-09, opus) brought lane/memfn-s30a (span_pick stage 3 unit 3.0a plus its review
fixes s30arev) up to main after the U2+U3 landing (main 7e8408214, which carries the landing merge
cf578177e: per-CPU SIMD targets, abi 98, MF_SITE_ABI 26).

- Merge commit: ba3933ba4.
- Ledger switch (review r1 s30a F14): 01a1bbc7c.
- Zero bytes against main: shown on the G2 window family and the finder hashes. The emit_sweep sample
  was not run: it waited on the box lock, and the kit manager ruled it covered by the full identity
  gates 501-503, which run the same arms (default and every `-fmemfn-simd` target) over the whole corpus.
- Gate jobs 500-509 refreshed for the new base. Every job passes its own `--dry-run`. None is queued.


## The merge

`git merge main` ran alone. It stopped on 7 conflicted files: 2 code files and 5 docs. Everything
else auto-merged. That includes kit.h, finder.c, formhash.c, arm_fixtures.c, memfn/src/CLAUDE.md and
memfn/tests/CLAUDE.md.

Checks before the merge commit:

- `nice make -j2 strict` is clean.
- The pre-commit hook refused the first commit attempt: memfn/tests/CLAUDE.md came to 12,334 bytes
  with both sides' lines in it, over the 12,288 limit.
  - The fix: run_g2_win.sh's later-population and plant history moved VERBATIM into a new
    memfn/tests/NOTES.md.
  - CLAUDE.md now points to that NOTES.md section. It is 11,182 bytes.

U2's API changes needed no edit beyond the conflicts:

- Every `mf_art_begin` caller in the tree already passes 5 arguments.
- No 3.0a code reads `art->policy`.
- The window family's shared contract macro carries `[FLD_target]`.

## Conflicts resolved

| file | HEAD (3.0a) | main (U2+U3) | resolution |
|---|---|---|---|
| memfn/src/compose.c `define_sel` | the E-stmt stream refusal (`WF_STREAM_REFUSAL`) before the gate description; positional `gate_in` | designated `gate_in` (U2 house fix HOUSE-6, the new `.art` field) | both: 3.0a's refusal kept, main's `{ .s = s, .h = def }` |
| memfn/src/window.c `wf_prepare` | the body moved into `wf_plan_site` (3.0a) | the old inline body with a designated `gate_in` | 3.0a's `wf_plan_site` call kept. Main changed only the initializer in that body, so the same change is applied inside `wf_plan_site` (`{ .s = s, .h = def, .wf = &f }`). A grep then shows no positional `gate_in` left in memfn/src or the tests |
| docs/dev/history/claude_md/docs__dev__lanes.md | u30d*, s30a, s30afix, s30arev lines | kitfile ... s2977fix lines | union, HEAD's lines first |
| docs/dev/history/claude_md/docs__dev__reviews.md | older review lines moved out (r13) | spanarms review lines | union |
| docs/dev/reviews/CLAUDE.md | r12, r13 planframe lines | r1 spanarms line | union |
| tests/memfn/CLAUDE.md | run_wreply.sh shortened, its history moved to NOTES.md | the same move, a shorter line | main's line (both sides made the same move) |
| tests/memfn/NOTES.md | the "run_wreply.sh's history" section | the targets, simdfloor and run_wreply.sh sections | main's. Its run_wreply.sh section moved the whole line verbatim, so it already holds HEAD's history sentence |

## Ledger switch

The kit manager ruled on review r1 s30a F14. Commit 01a1bbc7c applies the ruling.

- tests/memfn/stream_support.tsv: the LIBC and LIBC_BACK rows' basis read
  `"libc memchr supplies only one-shot" @ memfn/docs/responses.md 067aca4df`. They now read
  `@ docs/dev/decisions.md D190`.
- The pin's header comment says the rows now name D190 as their ledger.
- rows_check.py is unchanged. A D-number already narrows the read to that entry (`^## D190` up to
  the next `## D`).
- The sentence is in D190 on main ("- libc memchr supplies only one-shot. vrun becomes ...").

Checks:

- `make test-memfn-rows` is green. It printed `support pin: 6 lines, 6 rows in the kit's table, 1
  ruling ledger(s) read`, then `checks passed: 239`, `checks failed: 0`, and the census reported
  90/0.
- Hand plant through `rows_check.support_faults` on a scratch root:
  - The plant takes the sentence out of the D190 entry and puts it in another entry of the same file.
  - Both LIBC rows go red: "the ruling's sentence ... is absent from docs/dev/decisions.md".
  - So the check reads the entry, not the file.

## Zero bytes at the new base

BASE is main cf578177e. It was built plain, with `nice make -j2`, from `git archive` into
/var/tmp/pcrec-pcrec/scratch/memfn/s30amrg/base-src. TIP is this branch after the merge.

| witness | result |
|---|---|
| G2 window family: `g2_win_gen` seed 20261022, 1500 sites (2600 rendered), each side's generator against its own libpcrec.a | g2w_sites.c IDENTICAL (20,787,703 bytes); generator logs IDENTICAL |
| the same against each side's libpcrec_mftrace.a | sites and logs IDENTICAL; MFTRACE stderr (164,135 lines, 3,106 FDROUTE) is IDENTICAL once the FDROUTE ` frame=` field is set aside. That field is 3.0a's documented trace hunk (memfn/docs/trace_format.md, s30arev F6); it is not an emitted byte |
| finder form hashes: tests/memfn/run_finder.sh at tip | 3321 passed, 0 failed (policy 4/0, proof 882/0) |
| emit_sweep, REF = base build vs tip, `--streams c-default,c-vm --every 20 --jobs 2`, arms default and `-fmemfn-simd=` generic, x86-64, x86-64-v3, armv8-a | NOT RUN. It waited 10 min on the box lock behind queue job 208-main-sae2-maketest-5 and never started. The kit manager ruled it covered by jobs 501-503 (the default arm plus `tgt-generic`, `tgt-x86-64`, `tgt-x86-64-v3` and `tgt-armv8-a` at full corpus). The waiter and its loop were stopped with scripts/safekill (pids 3441875, 3441943 group). |

No header, layout or abi number moved, and there is no abi event. The full identity check is jobs
501-503. They compare against main on 67 declared arms plus 4 per-target arms.

## Gates refreshed

Jobs are in /var/tmp/pcrec-pcrec/scratch/memfn/s30a/jobs/. The previous set is backed up in
/var/tmp/pcrec-pcrec/scratch/memfn/s30amrg/jobs-prev/.

- common.sh:
  - BASE is now cf578177e. REF is s30amrg's plain build of it.
  - REFTR moved to `ref-mftrace-cf578177e`, so the reach job rebuilds the traced base.
  - check_inputs also requires the merge ba3933ba4.
- ident.sh (501-503):
  - The 67 declared arms of `--list-ident-arms cf578177e`, plus `tgt-generic`, `tgt-x86-64`,
    `tgt-x86-64-v3` and `tgt-armv8-a` (`-fmemfn-simd=T`, c-default and c-vm, no differ floor). That
    makes 71 arms, sharded 24/23/24.
  - The dry run checks the kit's target list against the job's. It also checks that REF accepts
    each target.
  - Arms naming `-fmemfn-simd` set the target text aside through emit_sweep (lane u3aside's
    `same_but_target`, merged from main).
- 504 reach:
  - 21 arms: the old 18 plus `-fmemfn-simd=` generic, x86-64 and armv8-a.
  - The traced base is built from cf578177e in the new BUILD_DIR.
  - Cap 4800, est 1900.
- mech.sh (507-509): 64 rows, sharded 22/21/21, cap 7200 (the U2 gates' lesson).
  - Derived by `tests/mech/rows_for.sh` over the code and test files the branch changes against
    main. That gives 48 rows, all among the old 62 except S2998 and S3000 (U2 rows planting in
    compose.c/kit.h). Both are added.
  - The memfnfinder arm adds nothing beyond S3000.
  - Every one of the old 62 still has its row file.
- 500, 505, 506 and basis.py are unchanged. 506's 26 plants are still 26.
- `--dry-run`: rc=0 for each of 500, 501, 502, 503, 504, 505, 506, 507, 508 and 509. Nothing is
  queued.

## Checks run

| check | file/command | result |
|---|---|---|
| warnings as errors | `nice make -j2 strict` (after the merge resolution) | clean |
| rows + census | `make test-memfn-rows` (tests/memfn/run_rows.sh -> rows_check.py; decider_census.py) | 239/0; census 90/0; §S 1 ledger read |
| sabotage anchors | `python3 -I scripts/m6read_check_sab_anchors.py` | 1202 sabotages, 1245 anchor sites, all resolve |
| arch-blind | `bash tests/memfn/run_arch_blind.sh` | 17/0 |
| codegen | `PROCS=2 nice make test-codegen` | 21/21 scripts passed, no `*** [test-` line |
| finder | `bash tests/memfn/run_finder.sh` | 3321/0 |
| G2 window family | the generator by hand at both commits (above) | identical |

Logs are in /var/tmp/pcrec-pcrec/scratch/memfn/s30amrg/: strict.log, rows.log, anchors.log,
archblind.log, codegen.log, finder.log, g2w/.

docs/dev/artifact_size_log.tsv is modified in the worktree by test-codegen. It is not committed.

## STATE AT HANDOFF

OWED: none

Delivered. The landing gates (jobs 500-509, refreshed and dry-run
clean) are the manager's to queue. The worktree's docs/dev/artifact_size_log.tsv is dirty from
test-codegen and not committed.

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| 1. merge main alone, resolve with both intents, read the U2 and s30a reports, make strict, commit | yes (ba3933ba4) |
| 2. the support pin's RULING ledger -> docs/dev/decisions.md D190; §S green | yes (01a1bbc7c; §S green, plant red) |
| 3. zero bytes vs main cf578177e: G2 window, finder hashes, emit_sweep --every 20 at default and each -fmemfn-simd target | G2 window and finder hashes yes; the emit_sweep sample is covered by jobs 501-503 per the kit manager's ruling (not run here) |
| 4. sabotage anchors, run_arch_blind.sh, make test-codegen, rows check | yes (all green) |
| 5. jobs 500-509 refreshed (BASE/REF, identity vs main, added/moved rows, u3aside, mech cap 7200), each --dry-run passes, not queued | yes |
| report + history index line | yes |
