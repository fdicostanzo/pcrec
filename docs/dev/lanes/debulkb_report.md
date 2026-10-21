# debulkb report (lane debulkb, sonnet): tests/ and studies/ CLAUDE.md de-bulk

All 30 tracked CLAUDE.md files over 200 lines under tests/ and studies/ are now short indexes (largest 134 lines, most 25-90). Total 21,267 -> 1,981 lines. Docs only; no box time.

## Per file (before | after lines)

| file | before | after |
|---|---:|---:|
| studies/CLAUDE.md | 324 | 44 |
| tests/CLAUDE.md | 821 | 75 |
| tests/assertions/CLAUDE.md | 545 | 118 |
| tests/axes/CLAUDE.md | 667 | 53 |
| tests/backrefs/CLAUDE.md | 257 | 84 |
| tests/bench/compare/CLAUDE.md | 241 | 54 |
| tests/cli/CLAUDE.md | 375 | 56 |
| tests/codegen/CLAUDE.md | 4149 | 102 |
| tests/core/CLAUDE.md | 383 | 52 |
| tests/fuzz/CLAUDE.md | 243 | 68 |
| tests/known_fail/CLAUDE.md | 277 | 36 |
| tests/lib/CLAUDE.md | 492 | 60 |
| tests/lookaround/CLAUDE.md | 431 | 58 |
| tests/mech/CLAUDE.md | 4108 | 90 |
| tests/mech/sabotages/CLAUDE.md | 436 | 134 |
| tests/memfn/CLAUDE.md | 832 | 82 |
| tests/mrl/CLAUDE.md | 226 | 78 |
| tests/possessify/CLAUDE.md | 343 | 52 |
| tests/probes/CLAUDE.md | 221 | 59 |
| tests/recursion/CLAUDE.md | 735 | 110 |
| tests/registry/CLAUDE.md | 1522 | 35 |
| tests/reject/CLAUDE.md | 502 | 33 |
| tests/resource/CLAUDE.md | 274 | 25 |
| tests/rxtsource/CLAUDE.md | 1049 | 38 |
| tests/size/CLAUDE.md | 237 | 75 |
| tests/spec_mod0/CLAUDE.md | 525 | 86 |
| tests/thread/CLAUDE.md | 223 | 60 |
| tests/uprops/CLAUDE.md | 201 | 48 |
| tests/utf8/CLAUDE.md | 350 | 92 |
| tests/vm/CLAUDE.md | 278 | 24 |
## Method
- One scratchpad generator (not committed): intro (capped), `## Files` one-liners (first sentence, ~170 chars) for every file bullet, file-documenting section headings listed as one-liners, the Conventions/Maintenance/Traps-type sections kept (capped at a paragraph boundary), file-specific rule sections kept per a hand-picked list, and an "Also" line for any directory file the original mentioned but the index did not.
- History file per directory: docs/dev/history/claude_md/<path with / as __>.md = one header line (source path + commit d3d4c5834) + the FULL original text, byte-for-byte. The index rules/one-liners therefore appear in both places (duplication is deliberate: preservation check is trivial and exact).

## Greppers found (whole-tree grep for CLAUDE.md, claude case-insensitive, *.sh/*.py/Makefile)
- REAL READER: tests/memfn/arch_blind_check.py (C4, `make test-memfn-arch`) scans every tests/*/CLAUDE.md (except tests/memfn/) for ISA/arch vocabulary against tests/memfn/c4_allowlist.tsv, counting hits per file and failing on FEWER hits ("stale row"). Allowlist rows: tests/codegen/CLAUDE.md class 6 x1 (x86_64 measurement note) and tests/thread/CLAUDE.md class 6 x2 (ARM64 note). Handling: kept one line in each index carrying the same hit(s) (codegen: the run_prechecks.sh section 5 line; thread: two "Platform note" lines, the scan counts per line). VERIFIED: `TMPDIR=<scratch> bash tests/memfn/run_arch_blind.sh <worktree>` -> checks passed 17, failed 0 (a first index version failed 2 stale rows, as expected). Moved text under docs/dev/history/ is outside the scanner's scopes (src/cli/lib/tests). No allowlist edit was needed.
- scripts/plan_lint.py: reads docs/dev/plan.md bodies and treats `CLAUDE.md` only as an exempt body name; PL14 (plan.md:<line> citations in the tracked tree) ran clean after the commits (183 rows, 0 violations).
- All the other hits the brief listed (tests/codegen/run_*.sh, run_cli_tests.sh, run_bench.sh, tier_escalation.sh, run_lever_fence.sh, run_altcls_tests.sh, run_assertions_tests.sh, battery.sh, hooks/pre-commit, mk_d27_cell.sh) are COMMENTS or messages, or (mk_d27_cell.sh) a find of CLAUDE.md names; none reads CLAUDE.md text. run_lever_fence.sh ALLOWs cli/CLAUDE.md edits (not mine). SAB_DOC_FIGURE fields in ~15 sabotage rows cite "tests/codegen|reject|registry|mrl/CLAUDE.md" figures; the matrix does not read them (sabotages/CLAUDE.md: "The matrix does not read it"), so these are now human pointers to the history file (not edited: outside my scope).
- No check requires a file to be LISTED in its directory's CLAUDE.md; the index nevertheless lists every file the original mentioned.

## Preservation
verify.py (scratchpad): for each of the 30, every original line is in (index lines U history lines): lost = 0 for all 30. Every directory entry the original text mentioned appears in the index (0 unlisted-but-mentioned after the "Also" lines).

## Caveats / honest limits
- Standing rules are kept where they live in Conventions/Maintenance/Traps-style sections and in hand-picked rule sections (oracle rules, generated-corpus notes, mech Standing rules). Rules buried inside long per-file or per-lane narrative sections (e.g. tests/codegen's ~50 lane sections, tests/mech's ~100 row sections) were NOT individually harvested; they live in the history file. The mech index carries three rules lifted by hand (commit-before-run, missing log scores anomaly, ids without suffix).
- A few kept Conventions sections are capped at ~30 lines at a paragraph boundary (bench/compare, sabotages Maintenance at 10, etc.) with a "rest in the history file" note; the first lines hold the rules.
- One-liners are mechanical first-sentence cuts ("..." marks a truncation); some read roughly.

## OWED (not run; heavier or outside my lane)
- `make test` sections that run codegen/mech/registry scripts are unaffected by this change (no script reads these files except C4, run and green), but the manager's normal main `make test` after merge is the formal gate. `make test-memfn-arch` is cheap: I ran its script directly (green).

## STATE AT HANDOFF
Branch lane/debulkb, worktree worktrees/debulkb, clean; 31 commits on top of d3d4c5834 (one per file plus the rulings file, which is gitignored/untracked and empty). Rulings file read: no entries. No merge done.
