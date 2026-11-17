# covs2fix: review r32 (round covs2code) FIX-NOW and DOC items on the cover-cap stage-2 branch

Lane covs2fix (opus), 2026-11-16, branch lane/covs2fix cut from lane/covs2b @ ad6f4cb56. Inputs:
/var/tmp/pcrec-pcrec/scratch/crit-covs2code/review.md and dispositions.md (the manager's, final).
Build go: "Cover-build-go: go" (Frank, 2026-11-16 ~17:30), limited to the ruled rows.

## STATE AT HANDOFF

STATE: done. Every FIX-NOW/DOC row the brief names is applied (F2 doc, F3, F4 comment, F5, F9, F10,
F11, F12, F14, F16, F17, F18, F19, F20); every PLAN row is filed (seven under [COVER-CAP], F21 under
[IFACE-PUSH]). No abi event; no emitted byte moves (0 of 268 artifacts, below). Nothing under memfn/
edited. F1 untouched (the owner's question cover-size-cap; limits.md §3.12¶4 and tuning.md §2.56¶2's
refusal wording unchanged). Rulings file docs/dev/lanes/covs2fix_rulings.md: empty at every read
(before each commit and before this report); no R-n applied.
OWED: none

## FIX TABLE

| finding | what changed | commit | how checked |
|---|---|---|---|
| F2 (doc) | tuning.md §2.56¶1: one sentence, answers identical but cost not: O(n*k) per search at width k on a dense near miss vs the engine's O(n), measured ~200x at k=1000; the same sentence in lib/pcrec.h's `window_search_width` comment. ¶2's refusal wording untouched (F1). | ded8ef0f2 | spec-history check green (11/0); comment only in pcrec.h (0 movers) |
| F2 (plan) | [COVER-NEARMISS-SKIP] under [COVER-CAP] | 90ae009e8 | plan lint |
| F3 | src/gen/memfn_sites.h: `_Static_assert(PCREC_WSTMT_POS <= MF_RANK_MAX && PCREC_WSTMT_POS <= MF_MAX_TERM)` beside the existing one; src/gen/known.c: the kit derivation pinned, `_Static_assert(MF_MAX_FWD == MF_WREACH && MF_WSPAN_POS == MF_WREACH - 1)` after the seam assertion, its comment naming it S3266's real control; cover_cap.md §11.6.3 (the S3266 row) now names that pin, not `window_bounds_check`, as the control. memfn.h's sentence left to the kit. | d7543ed3e (memfn_sites.h; its subject also names the known.c pin, which landed in the next commit), 52579571b (known.c), 3f7bdb460 (design) | builds; `gcc -Wshadow -Werror` on both TUs; sab anchor check 1321/1378 resolve |
| F4 (comment) | known.c: the C15 comment above cc_fits and the cover_conj[] table comment no longer say "until the seam carries a counted span"; both say the kit-bound conjuncts cannot be false at a legal build and name the plan row. Conjuncts NOT removed. | 52579571b | 0 movers |
| F4 (plan) | [COVER-C15-CONJ] under [COVER-CAP] | 90ae009e8 | plan lint |
| F5 | run_cover.sh: per-arm counters and floors W verdict >= 11, W facts >= 2, W answers >= 32, N verdict >= 1; the K35 comment's arithmetic corrected (48 default + 1 N + 11 W; 108 + 32 answers, 29 W + 3 Wu); the summary line prints the arm counts; tests/kitproof/CLAUDE.md says so | ef7c760cc | run_cover.sh alone: `kitproof: 60 verdicts (11 W, 1 N), 21 facts (2 W), 140 answers (32 W; 4362 cells)`, 255 passed / 0 failed |
| F6, F7, F8, F13, F22 (plan) | [COVER-PLANT-PIN], [SAB-REFUSE-TEXT], [COVER-S1418-REACH], [COVER-AXES-REACH], [COVER-ANSWERS-SYNC], all under [COVER-CAP] (F7's row is general to every BUILD-REFUSED row but its witnesses are S3261/S3262, so it sits beside them) | 90ae009e8 | `make test-plan-lint`: lints clean, selftest 45 plants 0 failures |
| F9 | loader.sh kp_row_check refuses W with N and `width=N` on a W or N row (judged against the default only); self-test: `W:width=24`, `N:width=24`, `uW:width=40`, `WN:`, `WN:cover` must be refused; `iuRWN:width=24` dropped from the legal list (now `iuR:width=24`, `iuRW:cover`, `N:decline`) | ef7c760cc | run_cover.sh alone, green (self-test rows all pass) |
| F10 | width_opt.c: `[0-9a-f]{40}` at width 40 is a cover, `[0-9a-f]{41}` at 40 is not; run_cover.sh's width_opt floor 8 -> 10 | ef7c760cc | run_cover.sh alone, green |
| F11 | limits.def row PCREC_DEFAULT_WINDOW_SEARCH_WIDTH unit `positions` -> `bytes`, limits.md §3.12¶1 `(positions,` -> `(bytes,` in the same commit; cover_cap.md's quoted design-time row keeps its text with a one-line note | fe5ab4022 | `--list-limits` reads `bytes`; tests/registry/limits_check.sh alone: 44 passed / 0 failed |
| F12 | match_api.md §8.2¶1: "twenty-eight" -> "thirty-three" members (counted from lib/pcrec.h: 33), `memfn_simd` added to the block before `window_search_width` (header order, offsets 224/232/240 checked with offsetof), new ¶7e for `window_search_width` (BYTES, 0 = default, legal range, -1 with `invalid window_search_width`, never clamped, both ways, compound parts, not a flag bit) | 069b6887c | spec-history check green |
| F14 | S3223 header: flipped by S3223 AND S3260, `N [0-9a-f]{@D}` tells them apart; S3260 header: not unique, the N row is S3223's discriminator and its control; cases.tsv WHY of `[0-9a-f]{@D1}` and of the N row say the same | 59ac0a470 | comments/WHY only; run_cover.sh green |
| F16 | memfn_sites.c routed_kind_name: `[MF_SK_REPORT] = "REPORT"` (inside `#ifdef PCREC_CAND_TRACE`) | 52579571b | `gcc -DPCREC_CAND_TRACE -Werror` on memfn_sites.c clean; trace build only |
| F17 | cover_cap.md §11.3: the parenthesis now attributes the quote to D198's Consequences, verbatim with "(D157)"; the decisions.md records stay the manager's | 3f7bdb460 | read against review/SEAM.md SEAM-5 |
| F18 | memfn_sites.c pcrec_memfn_rows: `switch (part)` with no default; known.c: the function-local `static const uint8_t ones[32]` hoisted to file scope as `kn_all_ones` | 52579571b | 0 movers (below); anchor check |
| F19 | run_cli_tests.sh: the ceiling read from `--list-limits` (through pcrec_run, bounded), refusals 0/-1/ceiling/x/empty each also grep `--window-search-width wants an integer`, accepts 1, ceiling/2, ceiling-1 | ceb59c52a | run_cli_tests.sh alone: cases failed 0; the eight width rows PASS (4096 refused, 4095 accepted) |
| F20 | S3263's REACH comment: the facts grep does NOT show the after side unstated (`\b[0-9a-f]{32}\b` prints the same row); why the gap cannot hide a miss | 59ac0a470 | comment only |
| F21 (plan) | [SETTABLE-LIMITS] as a child of [IFACE-PUSH] (Backlog): its subject is the CLI option surface, which is that umbrella's; trigger the third settable range-checked lever | 90ae009e8 | plan lint |

## VALIDATION

- Premise: HEAD ad6f4cb56 at start; after `make`, `build/pcrec --window-search-width=4095 -p rx --pattern '[0-9a-f]{40}'` compiled and read `#define RX_DFA_SCAN "cover"`.
- 0-MOVER PROOF (F18 and every src/lib change): the baseline compiler (ad6f4cb56) and the final one each emitted 67 patterns (every distinct cases.tsv pattern with @D forms expanded at D=32, plus 15 extras incl. `[0-9a-f]{40}`, `{1000}`, `{3000}`, `a{4095}`, `\b[0-9a-f]{64}\b`) x {default width, `--window-search-width=4095`} x {byte, `-e utf8`}, `--features all`: 268 compiles, all rc 0, `diff -r` over artifacts and stderr: **0 differ**; 147 of them are cover routes (92 at width 4095). Scripts and outputs: /var/tmp/pcrec-pcrec/scratch/covs2fix/zm/ (emit.sh, pats.txt, base/, final/).
- `python3 -I scripts/m6read_check_sab_anchors.py`: 1321 sabotages, 1378 anchor sites, all resolve (after the src commits and again at the tip).
- Single test scripts, each run once, alone, under `scripts/watchdog -s 900 -m 8g -c 1800 -S covs2fix -- nice -n 19 env PROCS=4`: tests/kitproof/run_cover.sh (255/0, PASS), tests/cli/run_cli_tests.sh (cases failed 0), tests/registry/limits_check.sh (44/0). Logs: /var/tmp/pcrec-pcrec/scratch/covs2fix/{kitproof1,cli1,limits1}.log.
- Light text checks: tests/spec_history/run_spec_history.sh (11/0), `make test-plan-lint` (clean, selftest 0 failures), the pre-commit staged checks on every commit.
- Compile hygiene: `gcc ... -Wshadow -Werror` on src/gen/known.c and src/gen/memfn_sites.c, and memfn_sites.c with `-DPCREC_CAND_TRACE`. The full `make strict` was NOT run (the box's evening hold; brief allows plain make and single scripts). No `make test`, mech, axes or sanitizer battery was run locally (box rule): the cloud runs below carry them.

## CLOUD RUNS DISPATCHED

Filled in after dispatch (the next commit); see the lines below.

## LEFT OPEN

- F1 (code-size cap at wide widths): NOT this lane's; owner question cover-size-cap, plan row [COVER-SIZE-LADDER] on main. limits.md §3.12¶4 and tuning.md §2.56¶2 still state the fallback F1 says is false.
- F15 (the ask's answer depends on the caller's storage capacity): the manager's kit request, not filed here.
- memfn.h's sentence "pcrec asserts MF_RANK_MAX >= that bound" is now true (F3's assert); any rewording is the kit's.
- The process changes in the round's process.md are the filing lane's, not this lane's.
- Commit d7543ed3e's subject names the known.c derivation pin, which landed in 52579571b (subject wording only).
