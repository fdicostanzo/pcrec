# tests/harness — test execution engine

Test runner and driver template. The runner (run.sh) orchestrates compilation and execution; the driver (driver.c) template is linked against generated code and exercises the matcher.

The full previous text of this file (per-file design history, wave and lane notes, [DD-13b], [TT-4M], [UTF-VALID], [RXT-READERS] entries) is kept verbatim in `docs/dev/history/claude_md/tests__harness.md`; grep it there when you need the story behind a rule. Specs: `docs/spec/rxt_format.md` (format and driver protocol), `docs/testing.md` (process record).

## Files

- **run.sh** — bash harness. Parses `.rxt`, compiles each pattern block with `build/pcrec`, links the generated C with `driver.c`, runs it per `m`/`n` line and diffs against the expectation. Owns the `.rxt` head/directive grammar readers (including `oracle`, `var`, `gu`, `callout`), a directory's `harness.manifest` (`link FILE`; `allow-code LANGS`, granted to the directory's ENTRY files only, plus `-I` of the .rxt dir and `code-header` head lines), batching eligibility (`HARNESS_BATCH`, via `flush_block`), the target build path cross-check (DD-13b H11) and the `RXTFLAGS`/axes hooks. Pure bash + gcc (no python3 dependency). Do not add HEAD arms: format semantics live in the spec.
- **dispatch_gen.sh** — [TT-4M] `HARNESS_BATCH`'s `dispatch.c` generator (`gen_dispatch_c PREFIX...`): a `main()` that includes each member's `PREFIX.h` and dispatches by index in `argv[1]`. Default route only. Excludes shapes it cannot model (var-bearing blocks, `mc`/`@file:`) rather than growing a second escape vocabulary. Give-up words come from `outcome_word.h`.
- **outcome_word.h** — [axtri] the ONE printer of a negative `<prefix>_search` return (`rxt_print_negative`: `steps`/`frames`/`work`/`recurse`/`internal`/`unset-var`, `utf <offset>`, else `giveup <n>`), included by `driver.c` and by the generated `dispatch.c` (`-I tests/harness`). A new code's word goes HERE.
- **driver.c** — test driver template: calls the generated matcher (`rx_search`), decodes escape sequences in subjects (`\" \\ \n \t \r \f \v \xHH`), prints one line per case, handles find-all (`mc`) and the target-build path; prints `utf <offset>` and exits 3 on `PCREC_ERR_UTF` ([UTF-VALID], reached only under `RXTFLAGS=-futf-check`).
- **verify_rxt.py** — python-re oracle: cross-checks every corpus expectation (D4); shares the `oracle`/`var` grammar with run.sh ([RXT-READERS]); needs the oracle-skip rules of the spec.
- **giveup.rxt** — [DD-14 wave A] the `gu` directive's own positive and negative cases.

## Conventions

run.sh accepts file/directory arguments or scans tests/ recursively. Each .rxt pattern block is compiled to C, linked with driver.c (which includes the generated code), and executed for each m/n line. Output is one line per case; see `docs/spec/rxt_format.md` for the exact protocol.

Maintenance: update this file when files are added/removed or their roles change.
- **`mg`** ([FINDALL-NEXT] I0): the global-count line in all three legs, driver mode `global`; detail in NOTES.md.
