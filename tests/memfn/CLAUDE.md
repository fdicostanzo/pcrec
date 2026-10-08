# tests/memfn — pcrec's side of the memfn kit's checks ([MEMFN])

pcrec's checks on the search-code kit (`memfn/`, D146/D147;
`docs/design/memfn/integration.md`). The kit's OWN tests (G2) live under
`memfn/tests/`, not here. Born at R4a (lane memfnmanifest, 2026-10-05) with
C17. R4c's lane r4cchecks (2026-10-06) added C4, C12, C13, C14, C17's
re-keyed dynamic half and the VM hybrid handoff reach floor (below). Later
pcrec-side kit checks and pins (`pins/`, C5/C10, §17.4) land here too.

## Files

- **site_manifest.tsv** — THE CHECKED SITE MANIFEST (integration.md
  §R4.3.4, D147 addendum 5): one row per search or span-compare site pcrec
  emits (13 at R4a: PF, PRE, OFS, SETREST, VERIFY, VMRUN, STAY, EDGE,
  VMSPAN, MLINE, N6, VMSTRIDE, N7). Each row has its emitters (the functions
  that SPELL the form), op/handoff, D91 budget, migration step and status,
  plus companions (moved with the site, spell nothing). Status is exactly
  `pending` or `delegated`. At R4a every row is `pending`, and each
  migration step's REPLACE commit flips its rows. The header documents the
  columns. R4h (M3) flipped STAY, EDGE and VMSPAN (9 delegated / 4 pending);
  VMSTRIDE stays pending on `vm_stride_loop`, the strided loop split out of
  `vm_emit_span_scan`.
- **search_vocab.tsv** — THE SEARCH-FORM VOCABULARY: the text shapes that
  count as a search form when an emitter spells them. There are four
  classes: libc search calls, table-walk loops, runcmp row texts and the
  encoding seam's span compare. Python regexes are matched against
  string literals. It names no site and no function. C12 (the emitted-form
  ratchet, born at R4c) reads THIS file rather than keep a second list.
- **c17_lex.py** — the emitter reader. It returns every C string literal
  in a file, with adjacent pieces joined and the emitter's own comments
  dropped, attributed to its file-scope definition (a function, or an
  initializer such as `enc_byte.c`'s `defs_bref`).
- **site_manifest_check.py** — C17 itself. It enforces the manifest's
  shape (two-state status, unique ids, every emitter/companion defined,
  and the K35 row floor) and the four rules:
  1. static half: a form in a function no pending row names → FAIL;
  2. dynamic half (R4c, Q3): keyed on `\bmf_(define|emit)\s*\(` (the
     rev-3 key `mf_emit_site(` named nothing). Every function under
     `src/` that calls the kit must be named (emitter or companion) by a
     `delegated` row, and every `delegated` row must be rendered at least
     once over a corpus compile pass through a TRACED build
     (`site_census.py`). LIVE since R4c (lane r4cfix): PRE/OFS/SETREST are
     delegated and their builders `req_site_define`/`ofs_site_define` reach
     the kit through pcrec's DOOR `pcrec_memfn_define` (`site_census.DOORS`):
     a door is shared plumbing, so the SITE is the door's caller; a stale door
     is red, and per compile the kit calls inside doors must equal the door
     calls traced at their callers (door accounting). Since M1b (lane m1b)
     VERIFY and VMRUN are delegated too: VERIFY is the OFS/PRE run term
     (named by its builders), VMRUN reaches the kit through the second door,
     `pcrec_memfn_emit`, from `vm_run_compare` (`emit_vm.c`). It was UNREACHED,
     loudly, while no pcrec source called the kit; a delegated row with no
     caller is a FAIL. The machinery also runs on a SYNTHETIC caller every
     time (the `selftest:` lines);
  3. a delegated emitter that still spells a form → FAIL. It is VACUOUS,
     and says so, at 0 delegated rows;
  4. a pending emitter that spells nothing → FAIL (the row is stale).

  It prints `checks passed:`/`checks failed:`.
- **site_census.py** — C17 rule 2's mechanism: `find_callers` (calls to
  `mf_define`/`mf_emit` under `src/`, attributed to the enclosing function,
  comments and strings ignored), `build_traced` (recompiles the caller
  files with a test-owned shim that logs kind/file/function before
  forwarding to the kit, relinks over a copy of `build/libpcrec.a`; pcrec
  grows no tracing hook), `corpus_patterns`/`run_corpus` (a deterministic
  sample of the `.rxt` `pattern` lines, K35 floor 100 compiles), `verdict`
  and `selftest`. Proven end to end on a scratch tree with a planted caller
  (report §2); live on pcrec's own callers since R4c (r4cfix: the door
  shim, `door_shim`/`DOORS`, traces the builders behind `pcrec_memfn_define`;
  M1b added the door `pcrec_memfn_emit`).
- **run_site_manifest.sh** — the entry point (`make test-memfn-manifest`,
  in TEST_SECTIONS; mech arm `memfnmanifest`). It holds `C17_ROW_FLOOR`,
  the K35 floor as a literal that shares no source with the TSV. A change
  that adds a manifest row raises it in the same commit. The static half
  needs no build and takes about a second; the dynamic half needs
  `build/libpcrec.a` once a caller exists, hence the section's `all`.

### C4, C12, C13, C14 and the reach floor (lane r4cchecks, R4c)

- **arch_blind_check.py**, **run_arch_blind.sh**, **c4_allowlist.tsv** — C4,
  the arch-blindness detector (`make test-memfn-arch`; mech arm
  `memfnarch`). Nine classes (ISA names, arch macros, intrinsics, intrinsic
  headers, targeting, arch nouns, kit-identity compares, reading kit output,
  the include graph) over `src/`+`cli/`+`lib/` code, the `.md` files inside
  them, and `tests/` (this directory exempt). The allowlist is COUNTED AT
  BIRTH (15 hits, 11 rows) and only descends (a stale row is red). Controls:
  positive plants per class derived from the compiler's own installation
  (`cc -dM -E` ISA-flag diffs, resource headers, `-dumpmachine`; classes 7-9
  are structural and take synthetic plants, said so), a zero-plant class is
  RED, a hex-escape negative control. `C4_ALLOW_FLOOR` (15) is a literal in
  the script. The plants are box-dependent: a Linux run may widen a class.
  Classes 1-2 plant the WHOLE derived population (not a sample) since lane
  r4clx (2026-10-06: ubuntubudu's sample missed `ABM`/`__LAHF_SAHF__`); the
  vocabulary was widened from gcc-16's and clang-x86_64's full ISA-flag
  macro sets; English words, two-letter acronyms and hash names (`sha`) are
  class-2 (macro-form) only, and `__GCC_HAVE_SYNC_COMPARE_AND_SWAP_16` is a
  class-2 plant, never a class-1 stem (the header says why).
- **form_checks.py**, **run_form_checks.sh**, **c12_ceilings.tsv** — C12,
  C13, C14 (`make test-memfn-forms`; arm `memfnforms`). C12 counts search
  forms per (emitter file, vocabulary line, libc call) against ceilings that
  only descend (12 rows, 26 forms at birth: memchr 8 in `emit_dfa.c`,
  memcmp 1 in `runcmp.c`, ...; 20 forms since M1's REPLACE lowered memchr
  8 -> 2; 9 rows / 13 forms since M1b's REPLACE deleted `runcmp.c`'s three
  rows, `C12_CEIL_ROWS_FLOOR` 12 -> 9; 8 rows / 12 forms since M2's REPLACE
  (R4g) lowered memchr 2 -> 1 and deleted the walk-fmt row, floor 9 -> 8;
  6 rows / 8 forms since M3's REPLACE (R4h) deleted `emit_dfa.c`'s
  walk-open and walk-stmt rows, 2 -> 0 each, floor 8 -> 6);
  REPLACE edits the one number on the row.
  Higher is red (a replaced form came back) AND lower is red (stale ceiling
  or a blind lexer). C13 is declared UNREACHED while no `on_cand` producer
  exists and FAILs the day one does. C14 compiles `_Static_assert(MF_MAX_TERM
  >= PCREC_OFSK_MAX_SET + 1)` and friends against the tree's own
  `core/internal.h` (limits.def's current value) and `memfn.h`, with a
  control that lowers MF_MAX_TERM and requires the assert to fire.
- **run_handoff_reach.sh** — the VM hybrid handoff route's reach floor
  (`make test-memfn-reach`; arm `memfnreach`): three witness patterns whose
  artifacts must carry `RX_VM_PREFILTER "hybrid"`, their `RX_REQ_HANDOFF`
  value and `handoff_position = rx_reqrun(` feeding the first `rx_prefilter(`,
  AND be patterns of `tests/litscan/handoff.rxt` (oracle-verified rows added
  to `gen_handoff.py`). `HANDOFF_REACH_FLOOR` (3) is a literal.

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

- **arm_fixtures.c** — C5's fixture renderer: fourteen FIXED site
  descriptions (four offset-skip shapes: a table and a byte around a scan
  at 3, a run-pinned run, a scan at 0, the pair arm; four pre-check shapes:
  the one-byte gate with a set rest, a lead before a handoff window, a
  masked window with a whole run and a set rest, a lone handoff window; and
  since M1b six run-compare shapes, one per row and the deny: overlap at
  L 3 and L 13, `memcmp` at L 8, masked `words`, masked under
  `MF_D_RUN_OVERLAP` (`bytes`), exact under it (`memcmp`); and since R4g
  five PF-find shapes through `render_pf`, pcrec's `find_site` hooks: the
  four pffind rows and a walk whose result is not its lo, the generic
  row's) rendered through
  the kit's public entry points with its OWN hooks and sink (a marker
  comment per note, pcrec_sb_cstr's string escape), so a pin moves only
  with an ARM, never with pcrec's scaffolding. Each fixture's art flushes
  its pending word-load helpers into the `def` part. `--perturb` moves one
  byte of one fixture (the witness). Every fixture STATES its `miss`
  (`MF_MISS_N` unless it says otherwise): since [MEMFN-ROWCON] N3 a row
  that uses an unstated one declines. `--gate` (N3) runs twenty GATE CASES
  instead, writing nothing: sites built to be DECLINED at define (the form
  that renders them is printed) or REFUSED (the refusal text is printed),
  covering the ad hoc K96 tests N3 deleted from memfn/src/ofsskip.c (a floor
  or a non-`n` miss at define and at the call) and the rulings it made real
  (F1 non-identifier hooks, an unstated miss, K-1's `fn_ref` 0, the
  pre-check's split by handoff). Their expected outcomes live in
  run_arm_pins.sh, not here. R4h prep added two pinned ADVANCE fixtures
  through `render_adv` (`adv-kit-count`, `adv-caller-count`: the scan
  edge's counted loop with the counter owned by the kit and by the caller,
  MF_SITE_ABI 5's `count_by_caller`) and nineteen gate cases (39 in all):
  the caller-owned counter's rules (its name required, the fact 0/1 and
  ADVANCE-only) and thirteen `adv-cls-*` cases whose hook texts classify
  as the ADVANCE shape classes or as OTHER. `--gate --gate-only CASE` runs
  one case alone (for rows_check.py's check E). Lane advtarget
  (2026-10-08) added eight more through `render_adv_x` (R4h's FROZEN
  TARGET, one per in-loop shape: `adv-stay-fwd`/`-rev`/`-view`,
  `adv-edge-unbounded`, `adv-edge-counted-fwd`/`-rev`, `adv-vmspan-it`,
  `adv-vmspan`), each with the hook texts pcrec writes today at that site
  plus its own member text (opaque, through the `AdvFx` member hook),
  cursor and indent. M4 prep (R-7, MF_SITE_ABI 6) added two READS-BELOW
  FIND fixtures through `render_emit` (one hook set, mf_emit):
  `pf-memchr-back` (MLINE's `(?m)^` site through row `pf_memchr_back`: a
  `\n` term at -1, floor = lo, empty AT_N, on_miss `break;`) and
  `find-back-reaches-n` (a G2-style reads-below FIND the generic row
  renders, its loop read-bounded to `<= n`, Q-R7-1); and nine gate cases
  (48 in all): `back-at-n-*` (the row's positive cases), `back-excluded-`/
  `back-floor-not-lo-`/`back-table-generic` (the row declines: AT_N only,
  floor must be lo's text, one byte only), `back-excluded-break-refused`
  and `pf-memchr-break-refused` (LOOP_EXIT that no row serves is REFUSED
  naming `on_miss`, Q-R7-3) and `adv-at-n-refused` (AT_N on ADVANCE has no
  miss).
- **pins/arms.tsv** — C5's pins: arm (the kit's form id), fixture, part
  (`def`/`use`), bytes, sha256. Recorded at R4c's IMPLEMENT commit, whose
  I1 shadow comparator proved the kit's rendering equal to pcrec's
  pre-migration text over the corpus sweep; re-pinned for the run-bearing
  fixtures and extended by the `runcmp` rows at M1b's REPLACE (28 rows);
  R4g added the PF rows (`pf_memchr`, `pf_walk`, one `generic` edge; 48
  rows, `ARMS_ROW_FLOOR` 38 -> 48);
  lane missn added `ofs-miss-token` and `pre-lead-handoff-miss-token`, whose
  digests equal their text-stated twins' (`MF_MISS_N` renders as `n`'s text);
  R4h prep added the two `generic` ADVANCE fixtures' four rows (58 rows,
  `ARMS_ROW_FLOOR` 58), none re-pinned; advtarget added the eight
  R4h-target fixtures' sixteen rows (74 rows, `ARMS_ROW_FLOOR` 74); M4 prep
  the two reads-below FIND fixtures' four rows (78, `ARMS_ROW_FLOOR` 78). A
  CHANGE DETECTOR: a kit change
  that moves an arm re-pins its rows in its own commit (D94's grep finds
  this file).
- **run_arm_pins.sh** — C5 (`make test-memfn-arms`, in TEST_SECTIONS):
  builds the driver against `build/libpcrec.a`, checks each fixture renders
  through its pinned arm, each part's digest, a K35 floor
  (`ARMS_ROW_FLOOR`, a literal) and an arm list (`ARMS_EXPECTED`), and that
  the `--perturb` witness moves exactly its one part. Since lane libcnote
  (kit F2) it also checks the libc record: the driver prints each
  fixture's stand-alone `MEMFN_LIBC` (no pcrec scan), and the script
  compares it with its own scan of the rendered text, with floors for
  `memchr` and `memcmp`. Check 6 ([MEMFN-ROWCON] N3) runs the driver's
  `--gate` cases against `GATE_EXPECT` (a RENDER case's form id, a REFUSE
  case's field named in backquotes), with a K35 floor
  (`GATE_CASE_FLOOR`) and an exact case count. Validated by a plant that
  turned the gate off (both walks and the use re-check): 19 of the 20
  cases changed outcome (the 20th, `allp-func-fn_ref-7`, is the positive
  control and must not). Check 7 (R4h prep) reads the counter's owner off
  the two ADVANCE fixtures' text: the kit-owned one declares
  `unsigned long scan_run_length = 1;`, the caller-owned one declares no
  counter, and both advance and cap it (`GATE_CASE_FLOOR` 39). Check 8
  (advtarget) compares each `pins/r4h_target/*.c` body byte for byte with
  its fixture's fresh `.use` (empty `.def`), with a K35 shape list
  (`R4H_TARGETS`) and floor (`R4H_TARGET_FLOOR` 8) and a planted-byte
  control that must compare unequal. Check 9 (M4 prep, R-7) compiles
  `pf-memchr-back`'s and `find-back-reaches-n`'s bodies into one program
  and runs `BACK_CASES` (10) subjects against a byte loop written from
  memfn.h's MF_OP_FIND (the first c in [lo, n] whose predecessor, at or
  above lo, is `\n`): the candidate n (Q-R7-1) and lo == n (Q-R7-2) both
  answer right (`GATE_CASE_FLOOR` 48). Seconds.
- **pins/r4h_target/** — R4h's FROZEN TARGET (lane advtarget, 2026-10-08;
  its own CLAUDE.md): one `<fixture>.c` per in-loop ADVANCE shape, a
  3-line header, the kit's text byte for byte, then a `/* pcrec today:`
  block quoting the same site's current pcrec text. pcrec's layout
  normalization diffs its emitted lines against these before R4h.
- **run_deleg_sites.sh** — C10's static half (`make test-memfn-deleg`, in
  TEST_SECTIONS): DELEG_SITES (`src/gen/memfn_sites.def`) against D91's
  budgets (this file's literal), every row's (op, handoff, kinds) through
  `mf_vocab_has` (a probe linked against `build/libpcrec.a`), `MF_P_INLOOP`
  in code only in `src/gen/memfn_sites.c`, and no by-value `mf_site`/
  `mf_pred`/`mf_result` under `src/`, with two planted controls. Its
  per-instance half is pcrec's own, at compile time
  (`pcrec_memfn_check_use`, `deleg_check` in `src/gen/memfn_sites.c`).

### The row manifest, signatures and floors (lane n4, [MEMFN-ROWCON] N4)

- **rows.tsv** — THE KIT'S ROW MANIFEST (row_contracts.md rev 4.1 §4),
  HAND-maintained: one line per row of the kit's two selection tables
  (13 at N4: the composer's 9 arms, `precheck`/`precheck_assign` and the
  four `pf_*` rows included, and runcmp's 4 rows; 14 since M4 prep added
  `pf_memchr_back`, ROWS_FLOOR 14). Each line gives the
  row's reach reason from a CLOSED set (`pcrec`, `total-fallback`,
  `pending-site:<trigger>`, `contract-reach:<G2 family>`; anything else is
  red, D77), its witness (a pcrec pattern + flags for `pcrec`, an
  `arm_fixtures.c` fixture otherwise), its text SIGNATURE and its CONTROL.
  Not derived from fields.def. The header documents the columns.
- **row_floors.tsv** — per-row CHOSEN floors: `pcrec_floor` over the full
  N2 census (`-` for a non-`pcrec` row), `g2_floor` over G2's quick tier.
  Both columns are pinned (2026-10-07/08): the pcrec column from the full
  census (the command is in the header), the G2 column from G2's per-row
  count (`run_g2.sh --rows`), checked by G2 itself at `make test-memfn-g2`.
- **rows_check.py**, **run_rows.sh** — `make test-memfn-rows` (in
  TEST_SECTIONS; about 1.5 s). Builds the kit with `-DMF_TRACE` (its own
  objects, `find`-listed), the fixture driver against them and a traced
  pcrec (build/libpcrec.a with its kit members swapped), then:
  A. the kit's row set, from the trace's exit REACH lines, against
     rows.tsv in both directions (plus `REACH_DROPPED` 0 and the
     ROWS_FLOOR literal), and runcmp's rows against `--list-axes`'s
     `run-overlap` rows and `docs/spec/tuning.md` §2.38's table;
  B. each reason from the closed set (G2 families read from
     `memfn/tests/run_g2.sh`'s `FAM_FLOORS`), its witness kind;
  C. each signature IN its witness's artifact with the trace choosing the
     row, and ABSENT from its control's with the trace not choosing it;
     then every signature against every artifact and fixture of the run
     (wherever it appears, its row was chosen); every pcrec artifact is
     made by the traced pcrec and build/pcrec, byte-identical;
  D. row_floors.tsv's shape (rows, values); PLACEHOLDER cells print as
     UNREACHED, never as a pass;
  E. (R4h prep) the ADVANCE hooks' shape classes: each `adv-cls-*` gate
     case (and the two counter cases) runs alone under the traced kit and
     its `MFTRACE REACH ... field=F class=C` lines must equal
     `CLASS_EXPECT`, a hand table in rows_check.py (CONJ / POSTFIX /
     EXPR_STMT or OTHER; `count` a used field of the caller-owned site only),
     with `CLASS_CASE_FLOOR` (run_rows.sh) and two cases per class.
  The floors themselves are the census's: `n2_report.py --floors`
  (docs/design/memfn/probes/rowcon/). Hand plants:
  `docs/dev/lanes/n4_report.md`.
- **mk_mftrace_lib.sh** — builds `build/libpcrec_mftrace.a` (make rule of the
  same name): build/libpcrec.a with its kit members swapped for `-DMF_TRACE`
  builds, the library G2's rows half links (`make test-memfn-g2` depends on
  it and passes `G2_ROW_FLOORS=tests/memfn/row_floors.tsv`, so G2's check (e)
  holds each row to its `g2_floor`). Same recipe as rows_check.py's own swap.
- `arm_fixtures.c --only FIXTURE` (N4) renders one fixture alone, so a
  traced run's rows are that fixture's.

## Sabotage rows

- S510: a `memchr(` text planted in an unlisted function trips rule 1.
- S511: a pending row goes stale and trips rule 4 (re-aimed at R4c from PRE,
  now delegated, to MLINE's `emit_attempt`).
- S512: deleting a row trips the floor.

All three are on arm `memfnmanifest`. See
`docs/dev/lanes/memfnmanifest_report.md` §4 for the transcripts.

R4c (lane r4cchecks) adds S518-S529: S518/S519/S520/S521 (C4 classes 1, 3,
9, 7), S522 (a stale allowlist row), S523 (the hex-escape exclusion removed),
S524 (a `memchr(` returns, C12), S525 (the vocabulary stops seeing it, C12),
S526 (`MF_MAX_TERM` lowered, C14), S527 (an `on_cand` token with C13
unbuilt), S528 (a kit call from an unlisted function, C17 rule 2), S529 (the
VM hybrid loses its handoff, the reach floor). Arms `memfnarch`,
`memfnforms`, `memfnreach`. Transcripts: `docs/dev/lanes/r4cchecks_report.md`.

## Maintaining it

- **A new search form in an emitter:** add a row, or name the function on
  its site's existing row, and raise the floor if you added a row.
- **A respelled form the vocabulary no longer sees:** rule 4 says so. Teach
  `search_vocab.tsv` the new shape; never delete the row to get green.
  Worked example (lane advtri, 2026-10-08, abi 67): [MEMFN] R4h's layout
  normalization respelled the five ADVANCE loops in the kit's layout
  (parenthesised `more` and member, braced body, step on its own line), and
  `walk-stmt`/`walk-open` stopped seeing them (4 rule-4 FAILs, 3 C12 STALE
  ceilings). Both regexes were widened to the new shape, not the rows or
  ceilings touched: C12 reads the same 12 forms in the same ceilings.
- **A migration step's REPLACE commit:** flip its rows to `delegated`.
  From then on, rule 3 holds pcrec to spelling none of them.
- `c4_populations/` — C4's COMMITTED compiler populations (`gcc -dM -E` dumps
  per ISA flag set, one directory per compiler/target/box). arch_blind_check.py's
  `population_controls()` plants classes 1-2 from every one, on every run, so
  the Mac checks ubuntubudu's gcc x86 vocabulary (R4c, 2026-10-07). An empty
  dump fails its population, with a scratch control on every run (R4c′).
  Own CLAUDE.md.
