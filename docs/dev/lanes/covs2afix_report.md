# covs2afix report — [COVER-CAP] stage 2 unit A, review r18 fixes (lane/covs2afix, from lane/covs2a 1d6b0502d)

## STATE AT HANDOFF
- Rulings file (docs/dev/lanes/covs2afix_rulings.md): empty at every re-read; no entry applied.
- All FIX-NOW findings applied and committed; the review is filed; every local section named below is green; the box was not used after 00:06 box clock (deadline 00:45).
- Local validation (each under `timeout`, run in this worktree after the last code change): `make` rc 0; `make strict` rc 0; `make test-kitproof` PASS (50 verdicts / 19 facts / 105 answers, 195 checks, 0 failed); `make test-cli` cases failed 0 (includes the new window-search-width refusal/accept cells); `make test-registry`, `test-endmark`, `test-doc-lint`, `test-spec-history` rc 0. `cloud_mech_check.sh` on the regenerated table PASS (1308 ids, 90 shards) and its `--selftest` rc 0.
- NOT validated here: the full `make test`, the mech rows, the identity gate (the cloud runs below); A6's prediction-tooling copy (docs/dev/lanes/covs2a_evidence/) was NOT reviewed by r18 (it sat in the round's denied directory) and is left untouched.
- No abi bump on this branch (the joint landing's one event). No emitted byte moved (ROUTE IDENTITY).

## FINDINGS APPLIED
| id | disposition | files | the check that shows it |
|---|---|---|---|
| CONTRACT-1 | NOTED | none | ask kept in the review's ruling: the joint gate MUST have a `W` row at n >= 33 that reads `cover` (B7) |
| CONTRACT-2 | applied (doc) | docs/spec/limits.md §3.12¶1, docs/spec/tuning.md §2.56¶1 (the tuning.md hunk rode the CONFORM-4 commit: same file) | text states bytes, `é{4}` = 8; unit token in limits.def left `positions` (a `--list-limits` text change was not asked: ruling said no behaviour change); test-spec-history rc 0 |
| CONTRACT-3 | NOTED | none | trigger = a W compound row once a compound kind can yield a cover part |
| CHECKS-1 | PLAN | none | see PLAN FOR THE COMBINED BRANCH |
| CHECKS-2 | applied | tests/kitproof/{loader.sh,cases.tsv,run_cover.sh,CLAUDE.md}, tests/cli/run_cli_tests.sh | new FLAGS letter `N` (`--window-search-width=<D-1>`) + row `verdict N [0-9a-f]{@D} decline` (floor 49 -> 50); plant: loader's N arm emptied -> `checks failed: 1` (red). CLI: cells for 0 / -1 / 4096 / x / empty refused (nonzero, no artifact) and 1 / 2047 accepted; test-cli failed 0 |
| CHECKS-3 | applied | tests/kitproof/{loader.sh,run_cover.sh,reach.sh} | `kp_row_check` (FLAGS must be `-` or letters of iuRWN; `width=` must be a bare decimal) called for every verdict/facts row, every answer row and reach.sh; a bad row prints FAIL + `test-kitproof: FAIL` and exits 1. Self-test rows in run_cover.sh (6 refusals, 3 acceptances; no mech sabotage id taken). Planted bad rows, by hand in a scratch copy: FLAGS `w` -> `FAIL: cases.tsv: FLAGS 'w' ...` red; `width=4O` -> `FAIL: ... not width=<decimal>` red |
| CHECKS-4 | PLAN | none | see PLAN |
| CONFORM-1 | applied | tests/kitproof/run_cover.sh | width_opt.c built by `unit_build` (sources tests/lib/unit_cc.sh: SANFLAGS, LIBPCREC, -Werror); test-kitproof green with -Werror |
| CONFORM-2 | applied by REGENERATION (no hand patch) | tests/ci/cloud_mech_shards.tsv | see SHARD TABLE below |
| CONFORM-3 | applied (doc) | docs/spec/CLAUDE.md | "(3.1-3.12 and 8)" |
| CONFORM-4 | applied | lib/pcrec.h, docs/spec/match_api.md §8.2, docs/spec/tuning.md §4 table | `window_search_width` is now the LAST member of `pcrec_options` (header, §8.2 listing after `allow_code`, §4 table row after `tune`); no positional initializer of `pcrec_options` exists (grep); width_opt.c and the CLI set it by name; emitted bytes identical (ROUTE IDENTITY); `vm_entry_shape` is an earlier breach of the same append rule, left as is: NOTED follow-up for the interface push |
| CONFORM-5 | applied (doc) | src/gen/known.h (a), tests/registry/limits_check.sh (b), src/core/limits.h (c), tests/endmark/CLAUDE.md (d) | comments only; (b) "five of those six" -> "five of those"; (c) change log removed; (d) names the width -D; make strict + test-registry green |
| CONFORM-6 | applied (doc) | docs/design/kit_proof.md | MkEnd sketch marked superseded by cover_cap.md rev 5.2 §11 A1 |
| CONFORM-7 | applied (doc) | tests/registry/limits_check.sh file header | "the named bespoke flag sites (two today)", "the eight BUILD_D/FLAG_D rows" |
| CONFORM-8 | PLAN | none | see PLAN |
| EMITTED-1 | PLAN | none | see PLAN |
| EMITTED-2 | merged into CONFORM-5(a) | | |

### SHARD TABLE (CONFORM-2)
- tests/ci/CLAUDE.md and the generator's header say the table is built from the COMMITTED `tests/ci/measured_mech.tsv` (file reads; no timing run). Regenerated with
  `python3 -I tests/ci/cloud_units_plan.py mech --slots 30 --waves 3 --measured tests/ci/measured_mech.tsv --write`
  (the shape the CLAUDE.md names; without `--measured` the check refuses an all-ESTIMATE table). Result: 90 shards, 1308 ids, 70 ESTIMATE rows, header counts and `# unmeasured` list now true; `cloud_mech_check.sh tests/ci/cloud_mech_shards.tsv` PASS and `--selftest` rc 0. The LPT balance re-deals ~915 rows between shards: the diff is large by construction (generated file).
- Does main's tree at 4456e9127 fail `cloud_mech_check.sh`? YES: run against `git archive 4456e9127 tests/ci tests/mech/sabotages` it prints `DROPPED (in no shard): S3170` and `S3198` (both row files exist on main, the table lacks them). The same regeneration on main fixes it (PLAN item below). The regenerated table here also holds S3234 (this branch's row).

## REVIEW FILED
- docs/dev/reviews/2026-11-15-r18-covs2a.md + directory docs/dev/reviews/2026-11-15-r18-covs2a/ (r17 is on main for predspec17; main's tree has no r18 at `git ls-tree main`). PROPOSED column replaced by the manager's RULINGS; the "notes for committing" section removed; the match_api.md line cite in conform.md replaced by its section; grep for `plan.md:<n>` over the review and directory finds nothing; the pre-commit hook accepted the commit.
- Index line in docs/dev/reviews/CLAUDE.md. The two accepted process changes applied: .claude/skills/pcrec-critic/SKILL.md (§3 item 2 plants carry `build/pcrec-harness`; §5 COMMON quotes interim wrongness for a staged subject; only those two places edited), a dated lessons paragraph in docs/dev/guide/critics.md "Lessons from review rounds", the Framework notes appended to docs/dev/meta/coordinator_framework.md. The proposed conformance lens-table row was NOT in the manager's accepted list and was not applied.

## ROUTE IDENTITY
- Not the 7,000-compile sweep (left to the cloud gate). Bounded sample: 16 patterns (fixed widths 4..40 incl. 24/32/33, multibyte `é{4}`, `\z`, `$`, alternations, `\w+@\w+\.com`, a 36-letter literal) x 5 configs (default, `-e utf8`, `-i`, `--window-search-width=40`, `--window-search-width=1`) = 80 compiles of `--features all -p rx`, each by the lane/covs2a binary (built from 1d6b0502d, saved before any edit) and by this branch's build/pcrec, compared byte for byte under the SAME output basename in two directories (and exit status): 0 differences. The struct move and the test/doc edits cannot move emitted C (the options struct is the compiler's input), and none did.

## PLAN FOR THE COMBINED BRANCH (lift these into its brief; no code written now)
1. CHECKS-1: the default's fallback in `cover_width_limit` is unwitnessed above 32 at A (width conjunct and kit bounds coincide at 32); B7's raised bounds make the `@D1` row discriminate. Optional cheap witness before then: a `-DPCREC_DEFAULT_WINDOW_SEARCH_WIDTH=24` reference build.
2. CHECKS-4 (pre-existing): deleting the `R`/`i`/`W` FLAGS-map line is silent in make test (only `u` reddens) and no row uses `i`; make the R witness exact (a facts R row or the stamp value) and give `i` a row or drop it. Partly closed here for W (the N row and the CLI cells), not for R/i.
3. CONFORM-8: §11.1's first reader grep also hits S1083 and S1224 plants (`proven[]`), tests/memfn/run_proof.sh, run_form_checks.sh, two memfn pins; add them to B6's reader list so B does not meet them as red mech rows.
4. EMITTED-1: `PcrecCover` holds two pointer/length pairs for one fact (`sets`/`exact_len` and `end.set`/`end.k`); at B drop `MkEnd.set` and pass `cv->sets` to its three readers, or document the alias.
5. CONTRACT-1 ask: the joint gate has a `W` row at n >= 33 reading `cover`.
6. Main repair: regenerate `tests/ci/cloud_mech_shards.tsv` on main with the command above (S3170/S3198 dropped at 4456e9127), unless the joint landing reaches main first.
7. NOTED for the interface push: `vm_entry_shape` sits mid-struct against lib/CLAUDE.md's append rule.

## OWED RUNS
Dispatched to the cloud as this lane's last act (names `covs2afix-test`, `covs2afix-recidentity`, `covs2afix-mech`, ref lane/covs2afix, owner main); see the list line filled in below after dispatch.
