# landcf — lane/corefix prepared for landing (2026-10-22, sonnet; no new behaviour)

Merged main (a623ced02) into lane/corefix and renumbered its abi 87 -> 83.

## Merge
- Merge commit 9a7ec9643. Six conflicts, all resolved: lanes/CLAUDE.md, the
  lanes history file and known_issues.md (additions kept, main's short
  CLAUDE.md form taken), rxtsource pins (main's values plus the branch's own
  delta: +1 file, +44 blocks, +1070 lines; C3 PASS +316, SKIP +754,
  PCRE2ONLY +754, VERIFIABLE +316), and the two start-set VM mover manifests
  (both sides' rows kept).

## abi 87 -> 83 (D94)
Readers changed (5 files): `src/gen/emit_dfa.c` (PCREC_ARTIFACT_ABI),
`tests/codegen/run_codegen_tests.sh` (ABI_EXPECT),
`tests/mech/sabotages/S693_abi_not_bumped.sh` (BEFORE 83, AFTER stays 82),
`docs/spec/match_api.md` (§1¶7 block, which also still said `!= 82` for the
guard, plus the rx_info table row and §6¶17), `docs/dev/history/abi_changelog.md`.
No other file cites the number as a value (greps of src, lib, cli, tests,
scripts, docs/spec, docs/testing.md, Makefile; FILEPIN stays 813f43ec8, abi 82,
and the branch was already green against it). Lane evidence scripts
(`cfcount/census.py`, `corefix/census.py`) and the older reports keep the
number 87 as written: they are historical records.

## Light checks (own tree, after the renumber)
test-codegen, test-registry, test-rxtsource (292 files / 5976 blocks / 72572
lines), make strict, test-plan-lint, test-spec-history, test-claudemd-size:
all green, no make `*** [test-` lines.

## STATE AT HANDOFF
Queued (jobs in worktrees/.boxqueue, `--ready` unconditional):
- `720-landcf-test`: make, strict, perfrun `make test`, red-line grep. Expect
  four lines `== 720 step build OK`, `strict OK`, `test OK`, `verdict OK`.
- `720-landcf-mech`: S38 S53-S57 S191 S192 S193 S693 S696 S701 S1470-S1476
  (19 rows; S1477-S1479 do not exist). Expect `== mech run COMPLETE: 19 rows`.
Validation OWED: both jobs. The manager lands the branch when both are green.
