# tests/cli — CLI surface and library-API tests

Covers what the .rxt corpus cannot: argument parsing, output-file behavior,
error text and exit codes, and library-level properties such as stack usage.
Part of `make test` since M2.

## Files

- **run_cli_tests.sh** — the cases (count deliberately not hand-copied here — this line has drifted twice; `grep -c '^case[0-9]*()' run_cli_tests.sh` is the source): (1) ...
- **case 11 (MOD-0.7)** — `--explain`, the CROSS-SOURCE query surface, and the first case in this file written under a stated assertion rule.
- **case 12 (R20/MOD07-1)** — A PRODUCING PORT THAT FAILS, on both query surfaces.
- **case 13 (MOD-0.8c slice 3)** — THE ENCODING GATE (`-e`), which nothing in this repository covered before: `grep -rn '\-e utf8' tests/` found nothing, so the CLI's only ...
- **case 14 ([STD1] phase A, D37, 2026-08-13)** — the frozen named set `std1` = {classes, modifiers}, artifact stamping, and the bare-default mapping point, WITHOUT the ...
- **case 15 (K21 fix, 2026-08-15)** — the third leg of `--emit-main`'s contract, which case2 could not reach: `<prefix>_search`'s return is THREE-valued ...
- **case 16 ([M4.7c], K9's API half)** — the K9 embedded-NUL repro itself (docs/dev/known_issues.md K9), the one surface in this file that has to be a direct library-API C ...
- **case 17 (K38 fix)** — the SPEC-FIRST witness case3 could not be: case3's 60-char-prefix cell proves the prefix is ACCEPTED and its artifact COMPILES, but only for the ...
- **K98** (2026-10-09): `--pattern-esc` is decoded once in `main`, above every mode, so `--emit-ir`, `--emit-facts` and `--count-groups` read the DECODED pattern.

## Conventions

Case 8 is a BUDGET, not a functional check: a 9000-duplicate-branch alternation
compiled under `ulimit -s 512`. It exists because M2.8's trie recursed once per
branch and segfaulted at a 1 MB stack — a regression against hardening this
project had already done once (R3 critic F3). pcrec is a library and musl's
default thread stack is 128 KB, so "it works on the main thread" is not the bar.
Keep the limit low enough that the recursive form fails it.

`--list-verbs` (Q1/D25) is a SECOND dump rather than new columns on the first,
and the reason is `--list-syntax`'s consumers: SR-4 generates a section of
docs/pcre2_compliance.md from it, so widening it churns a document for a table
that has nothing to do with RegRows. Its own assertions are a floor plus named
rows from BOTH tables plus the four-field count — a bare count would be
satisfied by any fifty rows, and a dump of one table would silently lose the
case distinction that is the whole point of there being two.

**[SR-11] (2026-08-21): case10's field-count pin is now the contract's own
HEADER TRUTHFULNESS check.** `table_check_truthfulness` (tests/lib/table.sh)
replaces the `NF != 16` literal: every data row's field count is compared
against the HEADER's own declared count, never a hardcoded number, so the
next appended column changes nothing here — this is the "correct final
form of case10" docs/spec/table_contract.md names it as. Sabotage-validated
against a real `pcrec` wrapper that injects an extra tab into one data row:
the assertion fails naming the exact count mismatch, not a silent pass.

Case 10's load-bearing assertion is the FIELD COUNT, not the content. SR-4 makes
tests/reject/ iterate `--list-syntax` and renders docs/pcre2_compliance.md from
it, so the TSV is an interface with consumers. The dump forbids tabs and
newlines inside a field rather than escaping them, and a `note` that acquired
one would hand every consumer a silently shifted column — nothing else in the
suite would notice. The other cases there are ordinary surface checks: a query
takes no pattern and no `-o`, an unknown flavour is an error rather than a
silently-unfiltered dump, and both flags appear in `--help`.

(Rest of this section: see the history file.)

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__cli.md`.
