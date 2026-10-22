# tests/registry — the syntax construct registry, checked against the parser

Guards the SR-1 table in `src/parse/registry.c` (design: docs/dev/decisions.md
D24). The table describes every non-base PCRE construct declaratively; this
directory asserts that the description and the shipped parser actually agree.

## Files

- **definitions_check.c** / **run_definitions_tests.sh** — [DD-11.1]'s required checks (docs/design/definitions_table.md §3 items 1-2), now over FIVE `DefKind`s: the ...
- **definitions_oracle_gen.c / definitions_oracle_driver.c / definitions_oracle_check.c / definitions_oracle_subjects.h / run_definitions_oracle.sh** — [DD-11.3]'s ...
- **registry_check.c** — links `build/libpcrec.a` and includes `src/core/internal.h`, so it compares the table with the parser inside one process rather than re-deriving ...
- **pcre2_check.c** — the same table against **libpcre2** (PC-3): the first check in this project that is not pcrec reading pcrec.
- **run_registry_tests.sh** — builds and runs both, plus compliance_section.py, PC-4 and (since [CHK-2] piece 1) axes_registry_check.sh; part of `make test`.
- **run_pc4.sh / pc4_check.c / pc4_driver.c / pc4_subjects.h** — PC-4 (MOD-0.3e), the SEMANTIC differential R8/C4-2 asked for and PC-3 deliberately is not: what a PRODUCED ...
- **axes_registry_check.sh** — [CHK-2] piece 1(a): the OPTIMIZATION-AXIS registry's own check, a DIFFERENT registry from the SR-1 syntax table above.
- **limits_check.sh** — [LIM-1] (D90, 2026-08-30): the numeric-limits table's own check, the SIXTH registry-family TSV surface's independent side.
- **syntax_index_check.py** — [SPEC-LANG]: `docs/spec/pattern_language.md` §10 (the language spec's hand-written construct index) against `pcrec --list-syntax`: missing/extra rows, module disagreements, sections the doc lacks; plants three mutations of the real doc first and fails if one goes unreported. Run by run_registry_tests.sh. A population FLOOR (`ROWS_FLOOR`, 142 rows): raise it in any change that adds a construct.
- `tests/lib/spec_extract.sh` — section "[decfbB0b] the extractors moved to `tests/lib/spec_extract.sh`" (history file)

## Two hand-written assertions that must not be tidied away (R5 N-1)

`check_table_to_parser` ends with two hand-written `expect_msg` calls for the
class-open entry to the collating rows, added because the doorway model does not
describe that position so nothing derives them.

After SR-2 they are **the only non-circular assertion about message TEXT left in
this file.** Every other message check now reads the expected string from the
row that the parser also renders from. An R5 critic predicted SR-2 had made the
documented "reword the collating message → 2 failures" sabotage stale, measured
it, and found those two calls still catch it.

If they are ever folded into the derived loop as a tidy-up, `registry` loses the
ability to see any message change at all and tests/reject/ becomes the sole
guard. That would look like a simplification. It is not one.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__registry.md`.
