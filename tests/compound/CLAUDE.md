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
  self-check over stated and unstated parts; `ranks` (E0) compiles each
  case as the default build does and prints the edge relation
  `entry_rows[]` derived for its shape, with each edge's rank
  (`PcrecEmitIn.edge_rank`). Built by `tests/lib/unit_cc.sh`.
- **entry_ranks.tsv** — E0's HAND RANK FIXTURE
  (`docs/design/compound_entries.md` §3.2, §3.6; a precondition of E1):
  one witness artifact per rank R0..R3 (or an `UNWITNESSED` row), each an
  edge `from -> to`, its rank, and the call-site text in `from`'s emitted
  body with its exact count. Written from the emitted C, never from
  `src/gen/entries.c`.
- **check_entry_ranks.py** — E0: the fixture's ranks against the drive's
  `ranks` output, each witness held to its call site in the artifact; then
  every N-th corpus artifact whose `search_run` calls the hybrid's embedded
  search is R3 exactly where that body holds a second call site (the
  retry's re-seed), read from the text, with floors on the R3 and R2
  populations. MEASURED at EVERY=1: 910 R3, 449 R2, 0 failures; the S1008
  plant (R3 read as R2) fails 115 lines at EVERY=8.
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
- **B4, the driver (compound.md §E.3 G1-G7, §E.4):**
  - **split.rxt** (G1) — the split compound's answer net: 105 blocks over
    `split_cases.tsv`, every `m`/`n`/`ms`/`ns`/`g`/`mc` line libpcre2
    10.46's answer, written by **gen_split.py** (`python3 -I gen_split.py
    ORACLE PCREC SCRATCH split_cases.tsv`; a case pcrec refuses is a `perr`
    block) and re-asked by **verify_split.py**, which shares no code with
    the generator. Rides `test-corpus` (own-oracle in verify_rxt.py).
  - **split_cases.tsv** — the twin's case list (cases2) plus the owed CMP-13
    arm: `id<TAB>enc<TAB>P-hex<TAB>engine`.
  - **check_split_diff.py** + **split_diff.c** (G2 + G4) — every case under
    every option arm (byte; utf8 under each startpos guard, each with and
    without `-futf-check`), the compound against the lever's plain artifact and
    libpcre2 in ONE translation unit, every startpos, span and every group,
    `_match`/`_match_caps` too; G4: the compound's `.h` and `nm -g` equal the
    plain artifact's. Floor on admitted case-arms. MEASURED: the CMP-2 plant
    (`floor_any` false) fails 15 cells.
  - **check_linear.py** + **loads_drv.c** (G3) — counted subject loads of a
    whole find-all (kernel-address hooks, no clock) on the pin-only shapes at
    k and 4k: compound <= lever + calls (final-newline cells: <= Q compiled
    alone + calls, today's rev-end cost) and linear in k.
  - **check_admitted.py** + **admitted.tsv** — the corpus's admitted
    population BY ID (file:line, arm, row), both directions; regenerate
    with **landing_census.py** `--write-manifest` (G6: corpus and bench, the
    reference compiler against this one: every mover is the stamp, the
    stamp-sized `_WHY` figure, or an admitted compound whose lever output is
    the reference's plain artifact; 0 bench admissions).
  - **check_declines.py** + **declines.tsv** — the decline controls
    (compound.md §E.4): `compound_drive walk` runs the as-built admission and
    reports each candidate's first failing conjunct (A1..A5) or `admit`;
    §E.4's named controls assert their RE-DERIVED ids, the candidate set
    (split_cases.tsv) is held to the recorded list both ways (`--write`
    regenerates), with floors on A1, A2, A5 and `admit`.
  - **check_lever.py** — the lever's two-directional property (§A.11):
    `"none"` byte-identical where the default ships plain, `"forced-off"`
    exactly where it ships a row; a floor on the forced population. Also
    test-axes' internal arm.
  - **run_lever_fence.sh** (G7) — one global under `pcrec_harness_` in
    `libpcrec.a`, no `lib/` declaration, the spelling only in the allowlisted
    places; each check against a planted input that must fail it.
  - **run_shell_checks.sh** — the call-site rows (a DFA part's calls get rows
    1, 2, 8 only), the namespace table's two rows, and `drop-compound` under
    a cap between the compiler's own plain and compound sizes.
- **run_compound_unit.sh** — the section script (B0, E0, B1, B2, B4). `EVERY` (default 1 here,
  8 from the Makefile), `JOBS`, `KEEP=1`. The mech arm `compound` runs it
  from a sabotaged tree (rows S891-S910, S1008).

Maintenance: update this file when a build step adds its check.
