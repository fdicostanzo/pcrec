# Lane substext: module subst-extended (BUILD)

Lane substext (opus), 2026-10-22. Branch `lane/substext`, from lane/subst at
85dbd5f17, main merged in at 081734fba. BUILD GO: Frank, 2026-10-22 ("Subst is
a go"). Design of record: `docs/design/replace_design.md` through §R4c and
`docs/design/subst_api_r4_draft.md`; the contract is `docs/spec/subst_api.md`.

## STATE AT HANDOFF

- Commits on lane/substext: 081734fba (merge main), a5402ff80 (the build and
  its cells), dd7038b96 (the spec hunks, the compliance row, rows
  S1530-S1539, CLAUDE.md rows), and the commit carrying this report.
- Light checks, run by the lane on the final tree, each under gnutimeout:
  `make strict`, `test-subst` (7,841 passed, 0 failed, ASan pass included),
  `test-subst-d27` (23/0, every family FAIL=0), `test-casemap`,
  `test-registry` (limits manifest 78 rows), `test-spec-history`,
  `test-plan-lint`, `test-claudemd-size` and `test-ci-shards`, all green.
- Queued through the box queue (owner substext; `build/STAGES` in the
  worktree): `340-343-substext-b202610221444001401697.{build,strict,test,mech}`. The test
  stage is a full `make test` through `scripts/perfrun`. The mech stage runs
  54 rows: every row on `emit_subst.c`, `subst_template.c`, `cli/main.c` and
  `definitions.c`, plus S1381. Their verdicts are OWED.
- Rulings file: `docs/dev/lanes/substext_rulings.md`. It was empty at every
  checkpoint, so no ruling was applied.
- Nothing stopped the lane. libpcre2 and the declared case table agreed on
  every cell. The rx artifact did not move. No case region exceeded the
  sizing bound.

## What was built

- **Parser** (`src/parse/subst_template.c`). Under `extended`, the template
  is parsed recursively, one sequence at a time:
  - Conditionals become SUBST_COND items, with their two texts' items after
    them and the piece count of each text.
  - Case escapes become SUBST_CASE events. A `\E` before the first case
    escape is a no-op and makes no item.
  - Escapes follow the measured table.
  - The digit-run and `\cX` values come from the definitions layer's
    decoders. They were refactored into two Ctx-free functions,
    `pcrec_esc_digits_value` and `pcrec_esc_ctrl_value`, so there is one
    decode for both the pattern side and the template side.
  - Every `\` + `1`-`9` + another digit is refused, with a diagnostic
    pointing at `${NN}`, `\o{NN}` and `\0NN`.
  - Nesting is limited by a new limits row, `PCREC_MAX_TEMPLATE_NESTING` = 10
    (libpcre2: 10 levels work, the 11th is -35).
- **Emitter** (`src/gen/emit_subst.c`).
  - **Conditionals:** one slot test, then the chosen text's pieces, padded to
    the larger text's count.
  - **The case region:** one piece per match.
    - `<p>_region` is straight-line code. The case state moves through
      `<p>_case_next` and `<p>_case_mode`, two tables the compiler computes
      from the DECLARED first-match rule table `case_rules`, which is
      §2¶13's table row for row.
    - `<p>_match` renders one match. The element calls it twice: a sizing
      pass that validates, counts and stops before the first failing match,
      then a NOSPACE test with `sneed`, then the writing pass.
    - Under byte, the case step is ASCII and inline. Under utf8 it is the
      support unit's new `rx_subst_case_utf8`. Its tables are written into
      the unit from `src/core/case_tables.inc`. An ill-formed byte is copied
      unchanged, counts as one byte, and consumes a pending one-shot.
  - **The record:** `uses = RX_SUBST_USES_SCRATCH`. A utf8 case template
    also gets the support id and pointer. A case template binds its
    encoding (§2¶5).
  - **The stamp:** `_SUBST_MODULES` gains `,subst-extended`.
  - **Core templates:** the emitted bytes are unchanged; only the shared
    types block gains one declaration.
- **CLI.** `--features subst-extended` is accepted with `--subst`. Any other
  `--features` value is refused.
- **OWED 5** (the substb2 witness). The `composed` cell runs on
  `tests/subst/composed.rxtin`, a composed rx (`ngroups` 0, `ncaps` 2). With no
  map, the check and the context setup refuse it with MISMATCH. Row S1538
  covers it.

## Oracle comparison (libpcre2-8 10.46, `pcre2_substitute` + EXTENDED)

`tests/subst-extended/cells.tsv` has 83 cells.

- **Compared with pcre2:** 79 cells, with 0 disagreements.
  - 77 are `same`.
  - 2 are the STRICT-unset class (pcre2 gives -55; §9 row 5).
- **Kept out of the differential:** 4 cells.
  - 3 ill-formed-UTF-8 case cells. libpcre2 crashes on these (§9 row 19,
    upstream U23).
  - 1 encoding-bind refusal.
- **Whole-map cells:** 4 of the 79 cover every code point the oracle
  store's case map lists (2,851 code points), all agreeing with pcre2.
  - `\U$0` and `\L$0` over the whole set.
  - `\u$0\l$0` per character.
  - `\L\u$0|\U\l$0` per pair.
- **The 1.5x bound** holds for the whole set in both directions (the
  `bound` cells).
- **What a passing cell covers:** every generic arm also runs on these cells
  (batch, RX_FOREACH, replace-all fits/size/exact/short/dirty, a hand map,
  room, mis, unk, blen, nogap against REPLACEMENT_ONLY). So does the new
  `scr` arm: render into exactly the `sneed` reported, and get NOSPACE at
  one byte less. All of this runs again under ASan+UBSan.
- **Expected values:** the cells were written by `gen_cells.py`. It is
  committed, and it reproduces `cells.tsv` byte for byte.

## Decisions taken here (for review)

- `\b` (BS) and `\v` (VT) are accepted. Both were measured, and they are
  added to §2¶10's table.
- For `\x{}` and `\o{}`, blanks and tabs may surround the digits, as
  measured.
- An unterminated conditional is refused at the template's end offset.
- An ill-formed byte consumes a pending one-shot. This cell is pcrec's own,
  spec'd in §2¶14a.
- A backslash in a core template (no module) stays an ordinary byte, as in
  PCRE2's non-extended dialect. Only the `$`-forms of the module refuse
  without it. §2¶4 and §2¶7 now say so.
- The compliance page's replacement row was stale ("no substitution API"
  since substb2). It is split into OK, OK-GATED and REJECTED rows, and the
  annotation is rewritten. The compliance_section checks are green.

## ABI

No rx abi event. The `.c` and `.h` of 44 rx compiles, over 11 patterns and 4
flag sets, are byte-identical to the merge base. Two things did change, and
neither is ever in an rx artifact:

- **The subst types block** gains the `rx_subst_case_utf8` declaration and
  its name macro.
- **The support unit** gains the function and the case-map tables, so its
  content id changes. That id is the mechanism that refuses a mix.

This follows substb2's position. But `subst_api.md` §10¶3 still says "a
change to [the unit's text] is an abi event", so the spec and the practice
disagree. This needs a manager ruling (see below).

## Needs (no numbers taken)

- **A D-number:** "no abi event for subst-block or support-unit text", with
  §10¶3 reconciled either way. substb2 asked for the same.
- **A K-number,** if the manager wants one: the mech rows on `compile.c`
  (63) and `internal.h` (5) were only anchor-checked, not re-run. Their
  sites did not change; only one subst line in `compile.c` moved, and that
  line is S1381's.

## OWED

- The verdicts of 340-343-substext-b202610221444001401697 (build, strict, test, mech).
- D27: no blinded author tested the extended forms. The design's witnesses
  and pcre2 are the controls here.
