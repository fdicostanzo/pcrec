# debulka report: CLAUDE.md de-bulk, src/ cli/ lib/ memfn/ scripts/ tools/ docs/ side

Each of the 30 tracked CLAUDE.md files over 200 lines in these directories is now a short index. The full former text of each is in `docs/dev/history/claude_md/<path with / as __>.md`, under a one-line header naming the source path and base commit d3d4c5834. Nothing auto-injects those files. The scaffold, the generic `claude_md/CLAUDE.md` and the line in `docs/dev/history/CLAUDE.md` are in.

## Per-file line counts (before | after)

| file | before | after |
|---|---|---|
| cli/CLAUDE.md | 546 | 39 |
| docs/design/CLAUDE.md | 3256 | 107 |
| docs/design/atomic_groups_measurements/CLAUDE.md | 262 | 83 |
| docs/design/backrefs_measurements/CLAUDE.md | 214 | 88 |
| docs/design/counterk_impl/CLAUDE.md | 315 | 35 |
| docs/design/dd13_format/CLAUDE.md | 803 | 34 |
| docs/design/eng_brep_measurements/CLAUDE.md | 267 | 83 |
| docs/design/memfn/CLAUDE.md | 642 | 73 |
| docs/design/start_table/CLAUDE.md | 255 | 94 |
| docs/design/subroutines_measurements/CLAUDE.md | 240 | 80 |
| docs/dev/CLAUDE.md | 911 | 79 |
| docs/dev/lanes/CLAUDE.md | 4024 | 62 |
| docs/dev/optloop/CLAUDE.md | 923 | 91 |
| docs/dev/reviews/CLAUDE.md | 576 | 50 |
| docs/dev/reviews/lens_reports/CLAUDE.md | 299 | 32 |
| docs/spec/CLAUDE.md | 237 | 135 |
| lib/CLAUDE.md | 463 | 35 |
| memfn/CLAUDE.md | 391 | 50 |
| memfn/src/CLAUDE.md | 450 | 46 |
| memfn/tests/CLAUDE.md | 523 | 43 |
| scripts/CLAUDE.md | 838 | 122 |
| src/core/CLAUDE.md | 1903 | 61 |
| src/dump/CLAUDE.md | 298 | 106 |
| src/enc/CLAUDE.md | 644 | 152 |
| src/facts/CLAUDE.md | 363 | 41 |
| src/gen/CLAUDE.md | 4570 | 64 |
| src/ir/CLAUDE.md | 402 | 33 |
| src/opt/CLAUDE.md | 1795 | 246 |
| src/parse/CLAUDE.md | 2209 | 101 |
| tools/review/CLAUDE.md | 217 | 90 |

Total: 37,657 lines down to about 2,100. Over the ~150 target: `src/opt` (246, many rule entries kept) and `src/enc` (152).

## Greppers found and how each was handled

- `tests/memfn/arch_blind_check.py` with `tests/memfn/c4_allowlist.tsv` counts architecture vocabulary in CLAUDE.md files under `src/`, `cli/` and `lib/`. The allowlist row `doc src/gen/CLAUDE.md 6 1` needs exactly one hit, so the index keeps the "an x86 slot" sentence once. No other index under `src/`, `cli/` or `lib/` carries ISA words. `tests/memfn/run_arch_blind.sh` ran here: 17 passed, 0 failed.
- The `tests/codegen/CLAUDE.md` and `tests/thread/CLAUDE.md` allowlist rows belong to lane debulkb (tests/). They have the same "exact count" shape, so debulkb must keep those hits.
- `scripts/plan_lint.py` only skips `CLAUDE.md` in the plan-bodies directory, so no text is read. `scripts/plan_lint.sh` ran: 183 rows, 0 violations.
- `tests/spec_history/spec_history.py` and `spec_cites.py` skip `docs/spec/CLAUDE.md`. `scripts/spec_toc.py`, `tests/spec_history/specdoc.py` and `scripts/hooks/pre-commit` cite its "Numbering" section and the no-build-history rule. The index keeps both in full.
- `tests/compound/run_lever_fence.sh` only names `cli/CLAUDE.md` in its ALLOW path list, so no text is read.
- `tests/memfn/run_link_checks.sh` excludes CLAUDE.md by name. `scripts/mk_d27_cell.sh` only lists CLAUDE.md files.
- The remaining hits are prose comments, Makefile comments and `SAB_DOC_FIGURE` strings in `tests/mech/sabotages/*` that cite a CLAUDE.md entry by tag, for example `[M4.6f]`, `[OPT-4.2]` and "STRATEGY-DENIAL mask". They are not machine-read. The briefs asked for one-line entries naming those tags in `src/opt`, `lib` and `src/gen`. I did not re-check that each entry made it into the indexes.
- `tests/registry/axes_registry_check.sh` cites the `[ENG-BREP]` rung-ladder section. The brief asked the index to keep that rule content.
- `docs/dev/lanes/CLAUDE.md`: `BOILERPLATE.md` and `BRIEF_TEMPLATE.md` are separate files and unchanged.
- Subagents did the index writing (sonnet, one per file group). The lead reviewed `src/gen` in full and spot-checked the MUST/NEVER/ALWAYS and "Maintenance:" counts in all 30. I added the `dd13_format` Maintenance line, which one agent had dropped.

## Preservation check

`build/scr/pres.py` (scratch, not committed). For every file the history body equals `git show d3d4c5834:<path>` exactly, and every original line is in (index lines plus history lines). Result: 30 of 30 files, 0 missing lines.

## OWED

- A full `make test`, because the memfn arch-blind and spec_history suites are in it. Only arch-blind and `plan_lint` ran here.
- `tests/spec_history` was not run separately.
- I did not read all indexes line by line for dropped rules beyond the count comparison. A reviewer should sample `src/opt`, `src/parse` and `src/core`.

## STATE AT HANDOFF

Branch lane/debulka, all work committed. No rulings file entries (`docs/dev/lanes/debulka_rulings.md` is empty). Nothing running.
