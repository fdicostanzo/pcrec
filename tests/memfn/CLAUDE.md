# tests/memfn — pcrec's side of the memfn kit's checks ([MEMFN])

pcrec's checks on the search-code kit (`memfn/`, D146/D147;
`docs/design/memfn/integration.md`). The kit's OWN tests (G2) live under
`memfn/tests/`, not here. Born at R4a (lane memfnmanifest, 2026-10-05) with
C17. Later pcrec-side kit checks and pins (`pins/`, C5/C10/C11/C12, §17.4)
land here too.

## Files

- **site_manifest.tsv** — THE CHECKED SITE MANIFEST (integration.md
  §R4.3.4, D147 addendum 5): one row per search or span-compare site pcrec
  emits (13 at R4a: PF, PRE, OFS, SETREST, VERIFY, VMRUN, STAY, EDGE,
  VMSPAN, MLINE, N6, VMSTRIDE, N7). Each row has its emitters (the functions
  that SPELL the form), op/handoff, D91 budget, migration step and status,
  plus companions (moved with the site, spell nothing). Status is exactly
  `pending` or `delegated`. At R4a every row is `pending`, and each
  migration step's REPLACE commit flips its rows. The header documents the
  columns.
- **search_vocab.tsv** — THE SEARCH-FORM VOCABULARY: the text shapes that
  count as a search form when an emitter spells them. There are four
  classes: libc search calls, table-walk loops, runcmp row texts and the
  encoding seam's span compare. Python regexes are matched against
  string literals. It names no site and no function. C12 (the emitted-form
  ratchet, born at R4c) is meant to read THIS file rather than keep a
  second list.
- **c17_lex.py** — the emitter reader. It returns every C string literal
  in a file, with adjacent pieces joined and the emitter's own comments
  dropped, attributed to its file-scope definition (a function, or an
  initializer such as `enc_byte.c`'s `defs_bref`).
- **site_manifest_check.py** — C17 itself. It enforces the manifest's
  shape (two-state status, unique ids, every emitter/companion defined,
  and the K35 row floor) and the four rules:
  1. static half: a form in a function no pending row names → FAIL;
  2. dynamic half: UNREACHED while no `src/` code calls `mf_emit_site`,
     and FAIL once one does and this half is still unbuilt;
  3. a delegated emitter that still spells a form → FAIL. It is VACUOUS,
     and says so, at 0 delegated rows;
  4. a pending emitter that spells nothing → FAIL (the row is stale).

  It prints `checks passed:`/`checks failed:`.
- **run_site_manifest.sh** — the entry point (`make test-memfn-manifest`,
  in TEST_SECTIONS; mech arm `memfnmanifest`). It holds `C17_ROW_FLOOR`,
  the K35 floor as a literal that shares no source with the TSV. A change
  that adds a manifest row raises it in the same commit. The check is
  static: no build and no binary, and it takes about a second.

## Sabotage rows

- S478: a `memchr(` text planted in an unlisted function trips rule 1.
- S479: the PRE row goes stale and trips rule 4.
- S480: deleting a row trips the floor.

All three are on arm `memfnmanifest`. See
`docs/dev/lanes/memfnmanifest_report.md` §4 for the transcripts.

## Maintaining it

- **A new search form in an emitter:** add a row, or name the function on
  its site's existing row, and raise the floor if you added a row.
- **A respelled form the vocabulary no longer sees:** rule 4 says so. Teach
  `search_vocab.tsv` the new shape; never delete the row to get green.
- **A migration step's REPLACE commit:** flip its rows to `delegated`.
  From then on, rule 3 holds pcrec to spelling none of them.
