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

### C15 and C16 (lane memfnskel)

- **run_link_checks.sh** — [MEMFN] R4a: `make test-memfn-link`, a `make
  test` section. Two checks born with the kit's link into libpcrec:
  - **C15**: every global defined symbol of `build/libpcrec.a` (`LIB=`
    overrides) begins `pcrec_` — the kit's are `pcrec_mf_*` through
    `MF_NS` — save `c15_allowlist.txt`. Controls: a probe archive compiled
    in the run with one planted unprefixed symbol must yield exactly it
    (and teaches the run the platform's `_` decoration); a population
    floor (200; 457 measured at R4a); reach (`pcrec_mf_options` present);
    every allowlist entry still exported.
  - **C16**: every file under `memfn/include` and `memfn/src` (`KITDIR=`
    overrides; a CLAUDE.md excepted) carries an `SPDX-License-Identifier`
    from D145's list (0BSD, Unlicense, CC0-1.0, spelled in the script) in
    its first 5 lines and a `Provenance:` line in its first 10, and
    `memfn/PROVENANCE.md` has exactly one row per file with the same
    licence. Control: a synthetic kit with six planted defects must be
    flagged for exactly those.
  The header names what neither sees. Sabotage runs against the real tree
  are recorded in `docs/dev/lanes/memfnskel_report.md`.
- **c15_allowlist.txt** — C15's exceptions, one undecorated symbol per
  line, each with its reason. Born EMPTY at R4a (0 measured).

### C5 and C10 (lane r4ccore, R4c)

- **arm_fixtures.c** — C5's fixture renderer: eight FIXED site descriptions
  (four offset-skip shapes: a table and a byte around a scan at 3, a
  run-pinned run, a scan at 0, the pair arm; four pre-check shapes: the
  one-byte gate with a set rest, a lead before a handoff window, a masked
  window with a whole run and a set rest, a lone handoff window) rendered
  through the kit's public entry points with its OWN hooks and sink (a
  marker comment per note, the `memcmp` spelling for a run compare), so a
  pin moves only with an ARM, never with pcrec's scaffolding. `--perturb`
  moves one byte of one fixture (the witness).
- **pins/arms.tsv** — C5's pins: arm (the kit's form id), fixture, part
  (`def`/`use`), bytes, sha256. Recorded at R4c's IMPLEMENT commit, whose
  I1 shadow comparator proved the kit's rendering equal to pcrec's
  pre-migration text over the corpus sweep. A CHANGE DETECTOR: a kit change
  that moves an arm re-pins its rows in its own commit (D94's grep finds
  this file).
- **run_arm_pins.sh** — C5 (`make test-memfn-arms`, in TEST_SECTIONS):
  builds the driver against `build/libpcrec.a`, checks each fixture renders
  through its pinned arm, each part's digest, a K35 floor
  (`ARMS_ROW_FLOOR`, a literal) and an arm list (`ARMS_EXPECTED`), and that
  the `--perturb` witness moves exactly its one part. Seconds.
- **run_deleg_sites.sh** — C10's static half (`make test-memfn-deleg`, in
  TEST_SECTIONS): DELEG_SITES (`src/gen/memfn_sites.def`) against D91's
  budgets (this file's literal), every row's (op, handoff, kinds) through
  `mf_vocab_has` (a probe linked against `build/libpcrec.a`), `MF_P_INLOOP`
  in code only in `src/gen/memfn_sites.c`, and no by-value `mf_site`/
  `mf_pred`/`mf_result` under `src/`, with two planted controls. Its
  per-instance half is pcrec's own, at compile time
  (`pcrec_memfn_check_use`, `deleg_check` in `src/gen/memfn_sites.c`).

## Sabotage rows

- S510: a `memchr(` text planted in an unlisted function trips rule 1.
- S511: a pending row goes stale and trips rule 4 (re-aimed at R4c from PRE,
  now delegated, to MLINE's `emit_attempt`).
- S512: deleting a row trips the floor.

All three are on arm `memfnmanifest`. See
`docs/dev/lanes/memfnmanifest_report.md` §4 for the transcripts.

## Maintaining it

- **A new search form in an emitter:** add a row, or name the function on
  its site's existing row, and raise the floor if you added a row.
- **A respelled form the vocabulary no longer sees:** rule 4 says so. Teach
  `search_vocab.tsv` the new shape; never delete the row to get green.
- **A migration step's REPLACE commit:** flip its rows to `delegated`.
  From then on, rule 3 holds pcrec to spelling none of them.
