# tests/compound — the [COMPOUND] tool's unit checks

`docs/design/compound.md` is the design (§F the build plan); D163 and its
addenda the rulings. `make test-compound` runs `run_compound_unit.sh`, one
block per build step that has landed. Nothing here is an answer corpus yet:
the split client's `.rxt` corpus (G1) arrives with B4.

- **compound_drive.c** — the INTERNAL driver: links `build/libpcrec.a`,
  includes `src/core/internal.h` and asks `pcrec_compile_driver` with a
  `PcrecEmitIn`, the driver-tier input no `pcrec_options` field or CLI flag
  carries. Subcommand `entries` (B0) writes each pattern's plain artifact and
  one artifact per entry request, and prints the REQUEST's own name lists, so
  the check never reads the closure the compiler computed; `parts` (B1)
  compiles a witness's plain artifact and the split client's two parts
  through `pcrec_compile_part`; `selfcheck` (B1) runs the table-build
  self-check over stated and unstated parts. Built by `tests/lib/unit_cc.sh`.
- **check_entries.py** — B0 ([EMIT-ENTRIES] internal, compound.md §A.4):
  every request's artifact compiles under the harness's warnings with
  `-Werror` (an over-kept entry is an unused static, an under-kept one an
  implicit declaration, so a clean build is the closure's exactness read by
  gcc, which shares nothing with `src/gen/entries.c`); its `nm -g` set is the
  PLAIN artifact's restricted to the request's exported names (§E.3 G4's
  rule); a kept entry is a local symbol; the reduced text is not the plain
  text (positive control). Three arms (byte, utf8 + `-futf-check`, utf8) and
  per-arm floors on the rows and on each edge-bearing shape, read off the
  artifact's own stamps. MEASURED both failing directions while it was being
  built: a missing edge (the `rev-end` tie's call of `<p>_match`) read as an
  implicit declaration, an over-wide one (a byte artifact's variables) as an
  unused static `<p>_valid_upto`.
- **check_parts.py** — B1 (part mode and `CompPart`, compound.md §A.1,
  §A.5): the split client's F (P bounded to one attempt) and Q (written by
  hand until B2 derives it) of six pin-only witnesses, five parent arms
  (byte; utf8 with each startpos guard; `-futf-check`) and two prefixes
  (`kz` and a legal 60-byte one), built into ONE translation unit with the
  plain artifact (which brings the ABI block no part carries) and a HAND
  CONTROLLER (§B.2's combinator, the prologue from P), `-Werror`, then RUN
  against the plain artifact at every startpos. Asserts no part symbol is
  global, no part carries a shared block, F's loop is bounded at
  `search_from` (an unbounded F answers the same, so only its text shows
  it), K79 (the 60-byte text is the short one respelled), and the
  self-check (`compound_drive selfcheck`) refusing every unstated field
  (since B4, `groups` too). B4 (soft item, compound.md §A.5): the bound is
  a general EMISSION option — P compiled as an ORDINARY artifact (prefix
  `nb`, no part mode) under a one-attempt request answers the plain
  artifact's match-here at every character start; MEASURED: re-coupling the
  bound to part mode fails it (25 failures).
  MEASURED: a controller with no prologue goes red on every utf8 arm (the
  answers lose the startpos refusal, and under `-futf-check` F's kept
  validator becomes an unused static).
- **check_derive.py** — B2 (compound.md §B.1, §E.3 G5): the build's split
  derivation (an AST rewrite at the tree-hook, `compound_drive derive`,
  through `pcrec_compile_part`) against the twin's (`docs/design/compound/
  twin/twin2.py`'s `derive`, a text rewrite over its own parser), over the
  twin's case list, compared by LANGUAGE: both Qs answer the same at every
  startpos (verdict, caps[0]) on the twin's own subject generator. Cells:
  both-q, both-never, both-decline (same reason), refused-p (P's plain
  compile refuses too; a part that refuses where P compiles is a FAILURE),
  twin-limit, and `wider` — the build reads each `^`'s own `(?m)` scope and
  `\A` as never multiline, so it kills anchors the twin's "`(?m)` anywhere"
  rule cannot (`(?:(?m:^a)|^b)`, `^x|\n(?m:^)a$`, a `(?m)` pattern's `\A`).
  G5's tree property is asserted inside the derivation by an independent
  walk (an internal error fails the case). MEASURED: a kill that also kills
  `(?m)^` fails two cases (never disagrees); a kill that skips `\G` fails 29
  (G5's walk). `compound_drive selfcheck` also asserts the registry's
  attempt-scope column and `pcrec_ast_crosses_attempts` reading it.
- **run_compound_unit.sh** — the section script. `EVERY` (default 1 here,
  8 from the Makefile), `JOBS`, `KEEP=1`.

Maintenance: update this file when a build step adds its check.
