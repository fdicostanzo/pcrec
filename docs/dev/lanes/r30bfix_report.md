# r30bfix — merge main into lane/memfn-r30b, fix job 697's four reds, stage the re-run

Lane r30bfix, 2026-10-31 (opus). Tree `worktrees/r30b`, branch `lane/memfn-r30b`. Inputs:
`r30btri_report.md` (the triage of job 697-kit-r30b-heavy: no R-30 defect, four stale
expectations, merge main first) and `r30b_rulings.md` (2026-10-29 entry: pcrec-side edits
allowed if listed; none were made here). No heavy run: no make test, no mech, no sweep, no timing.

## Summary

- The merge of main 5c60e118c is `975ed3a9c`. Seven files conflicted, all of them abi readers
  or index lines. `make strict` is clean.
- R-30 is renumbered abi 93 -> 94 (PROVISIONAL; main assigns the number at landing). Every
  reader of the number now says 94, on top of main's 93 entry. The identity gate's (B) FILEPIN
  is self-pinned to the merge, `975ed3a9c`.
- Fix 1 (`reqcube_check.py` k66): the check now decides from the FACTS whether a whole part is
  present. It passes on the merged tree (93 passed, 0 failed). Run through
  `build/pcrec-harness --harness=pres-window` (R-30's old form), the k66 row fails, as it should.
- Fix 2 (simd-form floor): measured once on the merged tree, `make test-memfn-guarded`, 12
  passed / 0 failed. `simd-form` = 8 and `simd-form-named` = 4 of 4. Floor re-pinned 6 -> 8.
- Fix 3 (G7 lever fence): S1548 added to the allowlist. `run_lever_fence.sh` passes (3 checks,
  4 controls).
- Fix 4 (S678): a plant defect that predates R-30. The row is re-planted warning-clean and
  hand-checked in scratch. Its mech figure is owed.
- The census BASE now points at 5c60e118c (its abi map is 94 -> 93). Eleven one-stage jobs are
  staged under `r30b2_jobs/`, and every `--dry-run` passes. NOT queued.

## Merge

`git -C worktrees/r30b merge main` (main at 5c60e118c) ran on its own, and I read its result
before going on. Seven files conflicted:

| file | resolution |
|---|---|
| `src/gen/emit_dfa.c` | `PCREC_ARTIFACT_ABI 94` (main 93, branch 94) |
| `docs/spec/match_api.md` (3 hunks) | 94 in §1¶7's guard block, §6¶1's `rx_info` table and §6¶17 |
| `tests/codegen/run_codegen_tests.sh` | main's ABI_EXPECT line and message (with `92->93: [K134]`) at 94, `93->94: [MEMFN] R-30` appended |
| `tests/codegen/run_recursion_identity.sh` | main's K134 self-pin comment kept; R-30's self-pin comment rewritten as 93 -> 94 over 5c60e118c; FILEPIN history = main's chain prefixed with the r30b pin |
| `tests/mech/sabotages/S693_abi_not_bumped.sh` | BEFORE 94, AFTER 93 (the parent's number, the row's convention) |
| `docs/dev/history/abi_changelog.md` | R-30's entry on top (renumbered 93 -> 94, provisional), then main's 93 entry in the past tense ("was `93`"), then the 92 entry |
| `docs/dev/history/claude_md/docs__dev__lanes.md` | both sides kept (main's index lines, then r30b's) |

Kit code under `memfn/` merged with no conflicts; R-30's hunks sit on top of main's changes.

pcrec-side hunks the merge keeps from R-30 (`git diff main 975ed3a9c -- src cli lib`, 16
insertions, 2 deletions, all of them R-30's own):
- `cli/main.c` (the `--harness=` option chain under `#ifdef PCREC_HARNESS`): parses
  `--harness=pres-window` into `st->harness.pres_window`. This is the test-only lever.
- `src/core/internal.h` (`PcrecHarnessOptions`): the `pres_window : 1` bit and its comment.
- `src/gen/memfn_sites.c` (`pcrec_memfn_art`): hands the lever to the kit
  (`mf_lever(job->mf, "pres-window")`) on a harness compile only.
- `src/gen/emit_dfa.c`: the abi constant (93 -> 94).
- `cli/CLAUDE.md`: harness option (5) recorded.

No `req_site_define` edit was made (the ruling allowed it; none was needed). `make -j16` rc=0
and `make strict` rc=0 ("whole tree compiles clean with -Werror -Wshadow") on the merge, before
it was committed.

## Abi readers

I found every reader of the number by grep (`git grep` for the number next to
`abi`/`ABI`/`PCREC_RX_ABI_H`/`ABI_EXPECT`/backticked numbers, across `docs/spec`, `src`, `lib`,
`cli`, `tests`, `scripts`, `memfn` and `docs/guide`). I also cross-checked the files main's own
92 -> 93 bump touched (ebcc10aa1, 79d766fc1, 86356a960). At 94 now:

| reader | form |
|---|---|
| `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI` | the one constant; every emitted `.abi = N`, the PROVENANCE `(abi N)` and the `PCREC_RX_ABI_H` fence derive from it |
| `docs/spec/match_api.md` §1¶7 | the guard block's `#error` text and `#define PCREC_RX_ABI_H 94` |
| `docs/spec/match_api.md` §6¶1 | the `rx_info` table's `abi` row value `94` |
| `docs/spec/match_api.md` §6¶17 | "It is `94` on every artifact pcrec emits today" |
| `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT=94` | [DD-14.FB] check plus its bump-history message (93->94 appended) |
| `tests/codegen/run_recursion_identity.sh` FILEPIN | (B)'s whole-file pin: `975ed3a9c`, the merge (src unchanged after it) |
| `tests/mech/sabotages/S693_abi_not_bumped.sh` | `SAB_BEFORE ... 94` / `SAB_AFTER ... 93` |
| `docs/dev/history/abi_changelog.md` | the top entry "is `94`" (record, renumbered) |
| `docs/dev/lanes/r30b_evidence/census.py` `ABI` | the census's abi digit map, now 94 -> 93 (BASE 5c60e118c) |
| `docs/dev/lanes/r30b2_jobs/common.sh` `r30b2_dry` | each job's dry-run checks for `PCREC_ARTIFACT_ABI 94` |

The branch's old 92 -> 94 wording is gone wherever a reader states the current number. It
stays only in history text: the S693 RE-AIMED comment ("93 -> 94 in landing order") and
r30b_report.md §4, which §12 of that report now marks superseded. Mentions of
`abi 93`/`abi 92` that remain are dated history (K134's comments in run_cpset_structure.sh,
run_size_term.sh and run_recursion_identity.sh; S283's figure), not readers. If main lands
R-30 under another number, these same rows move.

## Fixes

1. **`tests/codegen/reqcube_check.py`, k66.**
   - Condition (from the FACTS, never the checked text): an emitted run pre-check with a whole
     run longer than its window, on a VM route with `VM_PREFILTER "none"`. This is
     tuning.md §2.29¶4's own condition. It reads the run lengths from the record and
     `RX_ENGINE`/`RX_VM_PREFILTER` from the listing's decisions section. `facts()` now compiles
     under the same `COVER_DENY` as `emit()`, so the route is the same compile's.
   - Where the condition holds: `rx_reqrun` must be ABSENT and `rx_reqrun_whole` PRESENT.
     Elsewhere the old requirement (`rx_reqrun` present) is unchanged. The whole-block checks
     and the S448 k66 check still run.
   - Both populations are counted, and each must be >= 1. Today: 1 with a whole part (k66),
     10 without.
   - It can fail. Through `build/pcrec-harness --harness=pres-window` (a scratch wrapper, the
     old form), the run reads `FAIL ... a 12-byte whole run on a VM route with no prefilter,
     yet the 8-byte window's rx_reqrun block is still emitted`, 92 passed / 1 failed. On the
     merged tree: 93 passed, 0 failed.
   - The file I validated is `tests/codegen/reqcube_check.py` itself, run directly. The suite
     that chains it, `run_codegen_tests.sh` (`make test-codegen`), is job 3: OWED.
2. **`tests/memfn/simd_guarded_check.py` `FLOORS['simd-form']` 6 -> 8.**
   - I checked the box first (`scripts/boxlock status`): queue job 762-p1mech-ident, an
     identity job, not timing; no bench window.
   - Then ran `nice -n 19 make test-memfn-guarded` once (it drives
     `tests/memfn/run_simd_guarded.sh`): checks passed 12, failed 0. Populations: compiled 4095,
     vm 2175, dfa 1878, two-blocks 2217, ladder-moved 7, refused 350, simd-form 8,
     simd-form-named 4 (floor 4), scaffold-copy 304.
   - Main's three named vrun witnesses (`(?i)foobarbaz`, `(?i)select.*from`,
     `(?i)abcdefghijklmnop`) and `(?i)union.*?select` all still render a SIMD row (named 4 of
     4), so R-30 moved none of them.
   - Re-pinned AT the measure, with a comment naming job 697's 5 and the merged tree's 8.
3. **`tests/compound/run_lever_fence.sh` ALLOW += `tests/mech/sabotages/S1548_`**, with the
   comment extended (the plant's reach probe must name the lever). Run directly:
   `PASS: G7 lever fence (3 checks, 4 controls)`. The suite that chains it
   (`make test-compound`) is job 5: OWED.
4. **S678 is a PLANT DEFECT that predates R-30.** From the source:
   - The plant (`adv_member` returns `member[0]` for every term) is unchanged since lane m6
     (962fcc4c9). Its own `SAB_DOC_FIGURE` (m6, 2026-10-08) already records
     "`(?:a[a.])+\b` fails to compile, its position-1 class bitmap unused". That is job 697's
     anomaly (`rx_class_bitmap1 defined but not used`, -Werror).
   - R-30's only `memfn_sites.c` hunk is in `pcrec_memfn_art` (the lever hookup), not in
     `adv_member`.
   - Re-planted: each term keeps its OWN class test but reads it at position 0's byte (`+ T]`
     rewritten to `+ 0]` in an arena copy, T < 10). Every bitmap is still referenced. The hook
     still forgets its term. At W = 1 it is unchanged.
   - A permuting plant (`member[(term+1) % W]`) was tried first and rejected. The members carry
     their own offsets, so the planted conjunction was only reordered (same answers, verified).
   - Hand check in scratch (`git archive` of the tip, plant applied, build with
     `-Wall -Wextra -Werror -Wshadow`, rc 0): `(?:a[a.])+\b` compiles clean under
     `-Wall -Wextra -Werror`. `(?:ab)+c` on `xabababc` reads nomatch (clean: 1 8), and
     `(?:a\.)+\b` on `aa.a.` reads nomatch (clean: 1 3).
   - The row's matrix figure is OWED (job 9, half A).

Census BASE (task 4): `r30b_evidence/census.py` now maps 94 -> 93 and documents BASE
5c60e118c. The new jobs' `common.sh` sets `BASE=5c60e118c`. Job 697's script is re-pointed and
marked SUPERSEDED, and its `--dry-run` still passes. The census's declared population is read
from BASE's own artifacts, so no hand-written mover declaration needed re-deriving.

## Staged jobs

The jobs are in `docs/dev/lanes/r30b2_jobs/`; the order, the KEYs and the `boxqueue add`
commands are in its `README.md`. Shared settings are in `common.sh`. There is one stage per
job, each about an hour or less, chained by `--ready` = `boxqueue after KEY`:

| # | KEY | after | stage | cap |
|---|---|---|---|---|
| 1 | kit-r30b2-build | - | make -j16, make strict, mechval (77 ids); records the tip | 900 |
| 2 | kit-r30b2-census | 1 | refbuild 5c60e118c + census.py | 1800 |
| 3 | kit-r30b2-codegen | 1 | make test-codegen | 1200 |
| 4 | kit-r30b2-memfn | 1 | the 15 memfn sections | 1800 |
| 5 | kit-r30b2-compound | 1 | make test-compound | 1800 |
| 6 | kit-r30b2-regrx | 1 | make test-registry, make test-rxtsource | 900 |
| 7 | kit-r30b2-axes | 1 | `AXES=--harness=pres-window` run_axes.sh | 2400 |
| 8 | kit-r30b2-test | 1,3,4,5,6 | perfrun make test | 3600 |
| 9 | kit-r30b2-mech-a | 8 | mech 38 rows (S1543-S1548, S278, S693, S449, S678 first) | 3600 |
| 10 | kit-r30b2-mech-b | 9 | mech 39 rows | 3600 |
| 11 | kit-r30b2-reach | 1 | REACH_ONLY matrix, `MECH_SCRATCH` + `KEEP=1` under build/r30b2/reach_scratch | 1200 |

- Every `bash <job> --dry-run` passed on the tip: rc 0, and each printed its cap, patience and
  `expect steps=N lines=^== r30b2 step ... rc=0$` declarations. `--ready` answers 75 ("waiting
  on kit-r30b2-build") until the keys exist and are green; job 1 answers 0.
- Job 1 writes `build/r30b2/TIP` only when all three of its steps pass. Every later job refuses
  to run on a different tip.
- The mech id list is job 697's 76 plus S526. `tests/mech/rows_for.sh` over the R-30 kit files
  and `memfn_sites.c` on the merged tree names S526 (`memfn/include/memfn.h`). Job 697 had
  omitted it.

## Not done

- No queueing: the kit manager queues after agreeing the slot with main.
- No heavy run. These are OWED to the jobs: `make test-codegen` with fix 1 inside its suite;
  the memfn group; `make test-compound`; registry/rxtsource at abi 94; the axes lever; the full
  make test; mech for all 77 rows (S678's re-plant included); reach (S1760/S1761 still
  unexplained; job 11 keeps its scratch).
- The full `rows_for.sh` over every touched path (including `emit_dfa.c`, `internal.h` and
  `cli/main.c`) names 259 rows. Like r30b, I kept the cut list (rows on R-30's kit files plus
  the abi, lever and cli rows). The manager may widen it.
- I did not run `make test-memfn-guarded` a second time after the re-pin. The floor is a
  literal, and the measured 8 meets it.
- `docs/dev/artifact_size_log.tsv` (modified) and `r30b_rulings.md` (untracked) are left
  untouched, as the brief says. lanecheck reports the dirty tree for those two.

### Charter checklist

| brief item | done |
|---|---|
| 1. merge main alone, resolve, kit keeps R-30 on top, pcrec takes main's side, list pcrec hunks, make strict, commit | yes: 975ed3a9c; hunks listed under Merge; strict rc 0 |
| 2. abi 93 -> 94 provisional, every reader by grep, consistent with main's 93, readers listed | yes: Abi readers; FILEPIN self-pinned 8cabaf824 |
| 3.1 reqcube k66 from the facts, able to fail | yes: 99ffc170b; failing run through the old form |
| 3.2 simd-form floor measured once under nice (box checked) | yes: d75beecba; 8 / named 4 |
| 3.3 fence ALLOW S1548 + comment | yes: e2b5c2e52 |
| 3.4 S678: predates R-30? fix only if a plant defect, say which | yes: plant defect, predates R-30; re-planted f4db1701d |
| 4. census BASE -> merged main tip | yes: 7f0b460d6, d96e96d40 |
| 5. stage one-stage jobs, after-chains, README + add commands, dry-runs pass | yes: r30b2_jobs/, 11 jobs, all dry-runs rc 0 |
| 6. r30b_report.md names sections not run; this report with the DELIVER sections | yes: r30b_report.md §12; this file |
| WIP commit after each task; no heavy runs; lanecheck | yes; lanecheck below |

## STATE AT HANDOFF

- Branch `lane/memfn-r30b`, every task committed (the last WIP commit plus this report's
  commit). Rulings file: last entry applied is 2026-10-29 "pcrec-side edits allowed" (no new
  pcrec-side edit was made).
- OWED: the eleven staged jobs (`r30b2_jobs/README.md`), queued by the kit manager. The mech
  figure of the re-planted S678. The S1760/S1761 reach cause, which job 11 will explain if it
  happens again. A landing renumber of abi 94 if main assigns another number (the Abi readers
  table is the site list).
- Scratch: `/var/tmp/pcrec-pcrec/scratch/r30bfix/` (merge resolver, reqcube runs, the guarded
  log, the S678 planted tree, the job generator `genjobs.py`). Nothing under /tmp.
- Dirty, as instructed: `docs/dev/artifact_size_log.tsv`, `r30b_rulings.md`.
