# Lane p1land — landing P1 ([LANDWALK] stage 1) as abi 95

Lane p1land, opus, 2026-11-02, worktree `worktrees/p1build`, branch `lane/p1build` (tip 1cd8d220b at
start). Carries out p1prep_report.md's LANDING DRAFT. Scratch: `$PCREC_TMPDIR/scratch/p1land/`
(logs, the three job scripts, the parked pre-merge `artifact_size_log.tsv` and the stale
`p1build.done`/`p1prep.done`).

Premise test: `git merge-base --is-ancestor 657e23231 main` succeeded (R-30 is on main), and main's
`src/gen/emit_dfa.c` read `#define PCREC_ARTIFACT_ABI 94`. P10 is NOT on main (`docs/spec/tuning.md`
tops out at §2.53 there), so §2.54 stays P1's: **P10's landing renumbers its `-fdeferred-req-check`
section to §2.55 and every citation of it** (and re-checks run_prechecks.sh's walk deny on its
one-attempt witness, p1prep §6).

## Merge of main

`git merge --no-ff main` (main 0da7ab3bb) -> **f5de088bf**. Before it, the tree's run-dirtied
`docs/dev/artifact_size_log.tsv` was copied to scratch and restored (a test-run artifact, not lane
work). Nine conflicted files, all abi readers or docs; no conflict in any src/ logic:

| file | conflict | resolution |
|---|---|---|
| `src/gen/emit_dfa.c` | `PCREC_ARTIFACT_ABI` 95 vs 94 | 95 |
| `tests/codegen/run_codegen_tests.sh` | `ABI_EXPECT` and the transition message | 95; the message keeps main's `92->93` ([K134]) and `93->94` (R-30) and P1's entry becomes `94->95` (the "93 and 94 reserved on main" tail dropped) |
| `docs/spec/match_api.md` (3 hunks) | the §1 guard snippet, §6's `rx_info` row 1, §6¶17's sentence | 95 |
| `tests/mech/sabotages/S693_abi_not_bumped.sh` (2) | re-aim comments, `SAB_BEFORE` | both comment blocks kept plus a p1land re-aim line; BEFORE 95, AFTER 93 -> **94** (the parent's number at landing) |
| `docs/dev/history/abi_changelog.md` | the "today" entry | P1's entry "is `95` ... (94 -> 95, numbered at landing by lane p1land over main's R-30 94)", then R-30's entry as "was `94`", then [K134]'s 93 unchanged |
| `tests/codegen/run_recursion_identity.sh` | self-pin comments + `FILEPIN` | both self-pin comments kept; main's FILEPIN in the merge itself, re-pinned in the next commit (below) |
| `src/gen/NOTES.md`, `tests/codegen/NOTES.md` | both sides appended a section | both kept |
| `docs/dev/history/claude_md/docs__dev__lanes.md` | both sides appended index lines | both kept |

**`req_dominated_applies` (p1prep's named hand-merge):** merged clean, and read by hand. Main's only
change to `src/gen/emit_dfa.c` since the base is the abi line; R-30 lives in
`memfn/src/precheck.c`, `src/core/internal.h` (the `pres_window` harness bit) and
`src/gen/memfn_sites.c` (the lever call). P1's `whole` branch returns `dominated` before the kit's
PRES ask, and R-30 changes only what that ask contains, so the two compose: on a walk artifact the
pre-check is dropped whole (R-30 is moot there); elsewhere R-30 applies unchanged. No answer can
move from the merge. `make strict` green on the merge (`scratch/p1land/strict.log`: "whole tree
compiles clean with -Werror -Wshadow").

## abi 95 and its readers

Main is 94, so P1 is 95 (ruling (a)). Readers found by grep
(`(abi|ABI).{0,15}\b9[3-6]\b` over src lib cli memfn examples tests docs/spec, then `` `9[45]` `` in
docs/spec, then `abi[ =:_-]*9[45]|_a9[45]|ABI_H 9[45]` over the tree outside docs/dev): **seven
reader sites (plus the change log), every one now 95, or 94 as the parent:**

1. `src/gen/emit_dfa.c` `#define PCREC_ARTIFACT_ABI 95` (the `.abi` stamp, the banner and the
   `PCREC_RX_ABI_H` guard all come from it)
2. `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT=95` + its transition message
3. `docs/spec/match_api.md` §1 guard snippet (three lines)
4. `docs/spec/match_api.md` §6 `rx_info` table row 1
5. `docs/spec/match_api.md` §6¶17 "It is `95` on every artifact pcrec emits today"
6. `tests/mech/sabotages/S693_abi_not_bumped.sh` `SAB_BEFORE` 95 / `SAB_AFTER` 94
7. `tests/codegen/run_recursion_identity.sh` `FILEPIN` (below)

plus the change log's top entry (`docs/dev/history/abi_changelog.md`). Comments that cite a number
as history were left: `run_facts_checks.sh` "(abi 95)", `run_cpset_structure.sh` "abi 95"/"abi 93",
`run_size_term.sh` "abi 93", the older self-pin comments in run_recursion_identity.sh, and
`docs/design/memfn/vrun_bench_request.md`'s "657e23231, abi 94, or a later commit" (a request naming
a commit, not a reader). `src/gen/CLAUDE.md` names the macro, not the number.

**FILEPIN re-pin (as landr30 did):** `FILEPIN="${RECURSION_IDENTITY_FILEPIN:-f5de088bf}"`, the
landing merge, with the provenance chain prepended: re-pinned from the lane self-pin 379b84fac,
(B) 0 at 379b84fac (job 709) and e766f6b15/d6e03a594 byte-identical (job 762), before it cd4c36b92
(R-30's landing) and the rest of the chain unchanged. No src commit follows f5de088bf on the branch,
so the pin is the tree under test. The branch is meant to be taken by main as is (main is an
ancestor of f5de088bf), so the pin names a commit main will contain.

## D184

Written into `docs/dev/decisions.md` from p1prep's draft, placed immediately before D185 (the file
is not in strict numeric order: D181, D180, D183, D182, then D184, D185). Title carries "landed
2026-11-02 by lane p1land, abi 95". Added to the draft: the **Consequences** bullet (abi 94 -> 95;
the (B) re-pin; the [RECID-A] (A) list moving to 168 / 383 / 168 / 111 by POPULATION, naming the
two +1 identity movers: `(?i)[a-z]+@X` on vm and `[a-z]+@x(?:(y|\G)+){0}` on default/noprefilter,
both NEW landwalk.rxt patterns whose emitted program equals main's byte for byte, p1prep MOVER),
[LANDWALK-PRES]'s status per rulings (b) and the 2026-11-02 pricing deferral, and a **Revisit when**
bullet ([LANDWALK-PRES]'s fix, `k_hit` measured, [LANDWALK-VM] opening).

## Ledger and spec

- `docs/dev/full_suite_ledger.md`: the major line at the top of "### major" (p1prep §4, with abi
  94 -> 95 and the landing's own validation named) and the Runs note after landr30's ("major +1;
  recidentity's known (A) moves to 168/383/168/111, population, not a move"). The header's
  "major: 31" count was not edited (landr30 did not edit it either; the manager owns that count).
- Spec (D80): the only caller-observable change the landing itself makes is the abi number, in
  `docs/spec/match_api.md` §1 and §6 (above). P1's own spec hunks (`tuning.md` §2.54,
  `match_api.md` §6.3.4, `limits.md` §8.4) came with the branch and merged clean.
- `tests/mech/run_sabotage_matrix.sh`: the `landwalk` arm's row comment now names S1822 retired
  UNREACHED (re-arm tripwire `cand_rows_check.py` [cand-ma-dfa-only]) and S1855 (p1prep §5).
- `docs/dev/plan.md` [LANDWALK]: status line updated (landing prepared as abi 95, 830 queued, the
  manager merges on its verdict). STATE stays `not-started`: plan_lint refuses `started` in the
  Candidates block, and moving the row is the manager's at merge (its children stay open).
- CLAUDE.md files: none needed a change (no file added, removed or re-roled; `tests/landwalk/CLAUDE.md`
  already names S1820-S1829 and S1855). The lanes history index gains this report's line.

## Validation armed

Light suites on the merged tree, run directly, one at a time, `nice`, box free (logs in
`scratch/p1land/`):

| command | rc | reading | log |
|---|---|---|---|
| `make strict` (on the merge, before its commit) | 0 | "whole tree compiles clean with -Werror -Wshadow" | `strict.log` |
| `make -j16` | 0 | built | `build.log` |
| `make test-codegen` | 0 | no `*** [... test-X] Error` line; 19 `checks failed: 0` trailers, none non-zero | `codegen.log` |
| `make test-registry` | 0 | no error line; last PASS the [DD-11.3] option-matrix self-oracle (31 s) | `test-registry.log` |
| `make test-rxtsource` | 0 | "INV-COMPAT holds over 312 files / 6304 blocks / 75730 expectation lines" (the p1rxt pins, unchanged by the merge; 70 s) | `test-rxtsource.log` |

Queued (scripts in `scratch/p1land/jobs/`, each `--dry-run` clean, and accepted by `boxqueue add`):

| key | work | after | cap / est | expect |
|---|---|---|---|---|
| **830-p1land-test** | `make test` via perfrun on worktrees/p1build | none | 3600 / 1500 s | `sections=81 log=job.log.make last=^sections ran:` (one line per run, so it cannot double-count) |
| 831-p1land-mech | the landing's 20-row mech list (p1prep §5) | 830 | 1800 / 450 s | `rows=20 last=^== mech run COMPLETE: ` |
| 832-p1land-ident | `test-recursion-identity-locked` at FILEPIN f5de088bf (p1prep §2's landing gate) | 830 | 2700 / 1200 s | `none` (make's rc exec'd; (A) is red by design) |

What the manager reads:
- **830:** `scripts/verdict` on `job.log.make`: `sections ran: 81/81` and no
  `*** [Makefile:N: test-X] Error` line.
- **831:** the 20 rows' verdicts: S1822 UNREACHED (retired, declared), the other 19 DETECTED,
  S693 included (re-aimed here). The matrix exits 1 on the declared UNREACHED row as 713 did, so
  the job reads FAILED on rc; that is expected, the per-row lines are the verdict.
- **832:** (B) 0 differing on all four arms; (A) = 168 / 383 / 168 / 111
  (default / vm / noprefilter / nocaptures). Make's rc is red by design ([RECID-A]). Any other (A)
  number, or any (B) differing, triggers the STOP RULE.

## STATE AT HANDOFF

Branch `lane/p1build` at this report's commit, over the landing commits: f5de088bf (the merge of main
0da7ab3bb), fd6de3414 (FILEPIN re-pin, D184, ledger, plan status, landwalk arm rows), then the
report. No src change after the merge. Light suites green (above).

OWED, queued 2026-11-02 ~20:10 (pending; the box was held by another session's `t588-smoke` at
enqueue; the runner is live):
- **830-p1land-test** — completion line `sections ran: 81/81` in the run dir's `job.log.make`,
  no `*** [Makefile:N: test-X] Error` line (`scripts/verdict`).
- **831-p1land-mech** (after 830) — `== mech run COMPLETE: 20 rows`; S1822 UNREACHED, 19 DETECTED.
- **832-p1land-ident** (after 830) — the gate's (A)/(B) `differing=` lines: (B) 0 on all arms,
  (A) 168 / 383 / 168 / 111.

The manager reads the verdicts and merges lane/p1build into main (main is an ancestor of
f5de088bf, so main takes the branch and the FILEPIN names a commit main contains). Owed to P10's
landing: renumber its tuning.md §2.54 to §2.55. Rulings file: last entry applied is
"2026-11-02 19:05 (manager): brief issued. No entries yet." Nothing stopped: the merge moved no
answer and the light suites named no mover; the identity (A)/(B) reading is 832's.
