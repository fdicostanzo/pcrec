# wirechk — D136 wiring (2026-09-30, sonnet)

Branch `lane/wirechk` from main `8999ecc8`. No `src/`, no abi event, no caller-observable change (no spec hunk).

## Sites changed
- `Makefile`: `test-encoding-checks` appended to `TEST_SECTIONS` (46 -> 47 sections; measured `$(words $(TEST_SECTIONS))` = 47). Its recipe gained the trailer marker line (`touch $(TEST_TRAILER_DIR)/test-encoding-checks.ran`) as its first line, which the opt-in target lacked; without it the trailer would have reported the section MISSING. Header comment rewritten (no longer "opt-in"); `test-recursion-identity`'s comment names the battery stage. The `.PHONY` entry already existed.
- `scripts/battery.sh`: new stage `recidentity` (`make test-recursion-identity > recidentity.log`), LAST (after `mech`) so its ~35 min never delays earlier verdicts; default `BATTERY_STAGES` gains it; header + stage comment; trailer START/END/rc lines come from the shared loop, verdict = make's rc like every other stage.
- `docs/testing.md`: CI section (D136 paragraph with the run-time estimate), encoding-seam section note, recursion gate section, battery-integration section (chain now `... mech -> recidentity`).
- `tests/codegen/CLAUDE.md` (encoding-checks entry, staleness lesson, recursion-identity entry), `scripts/CLAUDE.md` (battery.sh entry + stage list). Root CLAUDE.md untouched, as ordered.

## Pins looked for and not moved
Grepped the tree (excluding dated lane reports/journal/reviews) for section-count pins (`4[0-9]/4[0-9]`, `sections ran`, `TEST_SECTIONS`, `.ran`). The count is not spelled anywhere live: `tests/lib/test_trailer.sh` counts against the argv `$(TEST_SECTIONS)` the recipe passes (one list, two uses), and docs/testing.md's "33 sections" sentence already defers to `TEST_SECTIONS` as the list of record. No registry/CI count pin exists. `.github/workflows/ci.yml`: step `timeout-minutes: 90` and job 120 unchanged (39m17s run 1 + ~10 min estimated ~47-49 min, well inside); its comment "the suite has since grown to 40" is historical and left.

## CI run-time estimate
+~10 min (ENC_MAX_BLOCKS=250 default; measured ~10 min at PROCS=1 on a loaded Mac by silentred, NOT measured on the runner). Documented as an estimate; the first CI run after landing gives the real number.

## Validation (Mac, gcc-16)
- `make -j4 CC=gcc-16`: built. `make strict CC=gcc-16`: clean, `STRICT_RC=0` (`build/wc_strict.log`).
- `make -n test` lists `test-encoding-checks` (3 occurrences: the section, the `-k` invocation, the trailer argv).
- `bash -n scripts/battery.sh`: ok. Battery has no dry mode, so it was driven with a stub `make` first on PATH and `BATTERY_STAGES=recidentity` (stub removed): trailer showed `stage recidentity START ... rc=0 END ... BATTERY DONE rc=0` and the stage log held `STUB make test-recursion-identity`, i.e. the stage dispatches to exactly that target. The real ~35 min gate was not run.
- `make test-encoding-checks CC=gcc-16` alone: launched detached at hand-off; **OWED**. Log `worktrees/wirechk/build/wc_enc.log`; completion line `ENC_RC=<n>` appended after make exits; verdict = `*** [test-encoding-checks] Error` lines (silentred left it green at its branch; `checks failed:` line is in the log).
- Full `make test` not run (manager, Linux). Note it will now print `sections ran: 47/47`.
