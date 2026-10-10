# n7uret — R-12's N7U half: manifest row N7U RETIRED (D147 addendum 14)

Lane n7uret (sonnet, light work), 2026-10-09, branch lane/n7uret cut from
lane/memfn-vmlazy. Docs/TSV/comment only; no pcrec byte moves, no abi event.

## Deleted (counts re-derived on the branch, not taken from r12scope)
- `tests/memfn/site_manifest.tsv`: row N7U. `C17_ROW_FLOOR` 14 -> 13.
- `tests/memfn/search_vocab.tsv`: the `span-compare span-decode` line. Its
  only reader was the N7U row's rule-4 spelling plus the C12 row below
  (`git grep -n span-decode` over tests/ and src/ after the edit: only
  comments/history). The C12/C17 checks stop seeing `$_decode(s,` in
  enc_utf8.c.
- `tests/memfn/c12_ceilings.tsv`: the `src/enc/enc_utf8.c span-decode 1`
  row; header counts (1 row, 1 form) and history extended.
  `C12_CEIL_ROWS_FLOOR` 2 -> 1 (VALID's swar-hibit row stays).

## Re-pinned readers (from `git grep -n 'C17_ROW_FLOOR\|C12_CEIL_ROWS_FLOOR'`)
- `tests/memfn/run_site_manifest.sh:38`, `run_form_checks.sh:23`: the
  literals, comment histories extended.
- `tests/mech/sabotages/S512_c17_row_below_floor.sh`: POP
  `^C17_ROW_FLOOR=14` -> `=13`, history comment. S511: history note only
  (plant VMSTRIDE unaffected). No sabotage plant relied on N7U or
  span-decode (grep of tests/mech and the sabotage_anchors.tsv files; the
  anchors' line numbers for site_manifest.tsv sit above N7U's line).
  S711 not needed.
- Prose: tests/memfn/CLAUDE.md, src/enc/CLAUDE.md, integration.md
  (§R4.3.4 exclusion rule beside Q-R10-11's; status table at the
  rung-table row, the `[r9]` row, the §15 "Not migrated" bullet and the
  §22 status block marked retired; dated history kept). Other docs hits
  are dated lane reports/journals, left as history.
- `src/enc/enc_utf8.c` sites_utf8[] comment only (compiler source, not
  emitted text; `make` and the codegen-reading suites below unaffected).

## Verdicts (taskset -c 12-13, gnutimeout; read from make's Error lines)
make -j4, test-memfn-manifest (13 rows, 12 delegated / 1 pending, floor
13), test-memfn-forms (C12 1 form, 1 ceiling row), test-memfn-rows,
test-memfn-deleg, test-memfn-reach, make strict: all rc 0, no
`*** [...test-` lines. Mech, run on the committed tip: S512 DETECTED
(memfnmanifest 1fail/10pass), S511 DETECTED (2fail/11pass), clean POPs
reached. (A first S512 run before committing read UNREACHED because the
matrix works from HEAD; expected, not a defect.)

## Owed to main
- decisions.md (main's file): close D58 addendum 2's revisit clause (line
  ~9256, "or N7U ...") as "does not migrate; D147 add. 14".
