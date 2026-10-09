# memfn/src/ — the kit's sources

Built into `libpcrec.a` by pcrec's Makefile (`KITSRCS`, compiled with
`KITFLAGS`: no `-Ilib`/`-Isrc`, so nothing here can include pcrec). Every
file includes its headers by relative path. From R4c pcrec's emitters render
two sites through the kit (src/gen/memfn_sites.c, DELEG_SITES): the
offset-skip block and the pre-check composite, by the scalar arms below;
from M1b, a third, the VM's literal-run compare (VMRUN, runcmp.c); from
R4g (M2), a fourth, the prefilter find (PF, pffind.c).

- **kit.h** — the INTERNAL header: `kb` (growable text over the caller's
  `mf_arena`), the `mf_art` struct and its per-site records, the arm
  interface K2 selects over (an arm writes STRAIGHT TO THE SINK, in order,
  so a hook that writes and the sink's comment gate act at the point the arm
  reaches them), the sink writers (`kit_out`, `kit_flush`) and the
  offset-skip function's shared renderer (`ofs_fn_*`; since R4e'.0
  `ofs_fn_define` takes the calling site's handle), the shared walk's table
  descriptor `kit_table` and `kit_walk` (R4e'.0), and the row
  contracts' types (`gate_contract`: `uses` per site kind and phase,
  `serves` per field; `CL_*`/`FLD_*` from fields.def) and the MF_TRACE
  record calls. Never included outside this directory.
- **compose.c** — K2, the composer: THE KIT'S ONE SELECTION WALK,
  `kit_walk` (R4e'.0, integration.md §R4.9.2.3: per row of the asked slot,
  in table order, the deny, the gate, the row's predicate; first match; a
  slot holding no row is no selection and records nothing), which the arms
  (`select_arm`), the run compare (`rc_row_of`) and `fn_rows[]`
  (`fn_select`) all call; `mf_art`, the define/use split
  (`mf_define`/`mf_use`/`mf_emit`/`mf_call`; handles checked at use and at
  `mf_art_end`), the vocabulary rules every site must pass (`site_check`,
  `pred_kinds`: out-of-enum fields and every shape integration.md §R4.7
  rules outside the vocabulary are REFUSED loudly) and their table
  (`mf_vocab_has`), the FIRST-MATCH arm table (`ofsskip`, `precheck`,
  `precheck_assign` (one renderer, two rows: N3's split by handoff),
  `runcmp`, the five PF rows (`pf_memchr`, `pf_memchr_bounded`, `pf_walk`,
  `pf_walk_bounded`: R4g; `pf_memchr_back`: M4 prep), `mismatch_inplace`
  (M7 prep), then the generic row; each arm's `ct` is its contract, which
  the gate reads before the arm's predicate and, since [MEMFN-ROWCON] N3,
  ENFORCES: a failing row is declined and the walk moves on, a site no row
  serves is refused naming the fields, and `mf_use` re-checks the chosen
  arm against the use hooks and refuses a use it does not serve), the
  art's one `denies` value (a site
  whose `denies` differ is refused, Q-M1b-1), the `mf_includes` query, and
  the stamps: `mf_art_note_libc` (the libc record's writer, a sorted
  distinct name list on the art; every arm that renders a libc call notes
  it at the render, beside its `includes` bit: `memchr` in `ofs_fn_define`,
  `precheck_use` and `pf_memchr_use`, `memcmp` in `run_cmp_render`; the word-load helper's
  constant `memcpy` is the record's exclusion and is not noted) and `mf_stamps` (M1b: `RUN_WORDS`, the run
  compare's words count, through `sink->stamp_int`; R4a′: `MEMFN_FORMS
  "none"`, constant until R4f, then `MEMFN_LIBC`, the noted names
  comma-joined or `none`, through `sink->stamp`).
- **generic.c** — THE GENERIC SCALAR ROW (integration.md §14.6): the last
  row of every selection table, rendering every site the vocabulary
  describes as a plain byte loop (GNU C statement expressions for EXPR; a
  `static inline` definition plus calls for FUNC; STMT ASSIGN, ON_MISS,
  ON_CAND and ADVANCE). It tests every term, honours `floor`, `n`,
  `end_back` and the empty outcome on every op (VERIFY tests its range
  too; an empty range, `lo > n` included, reads nothing: §R4.7 F1), and
  uses pcrec's `member` hook for a set when one is given. No tuning constant (D149).
  **Since [MEMFN] R4h (M3, lane r4h, 2026-10-08) its `stmt_advance` is
  pcrec's in-loop skip text**: DELEG_SITES rows STAY (`dir_fwd_skip`/
  `dir_rev_skip`), EDGE (`emit_scan_edge`, both loops) and VMSPAN
  (`vm_emit_span_scan` at stride 1) render through it at zero movers (the
  frozen target, tests/memfn/pins/r4h_target/). pcrec passes every hook as
  text (`more`/`peek`/`step`/`cursor`, its own opaque `member`, and the
  caller-owned `count` with `count_by_caller` 1 on the counted edge and the
  VM's `it_`). Sabotage rows S214 (the scan edge's cap, `count_start` 1)
  and S616 (the VM span's `it_` cap, `count_start` 0) are anchored on its
  cap line, each scoped by that site fact.
- **ofsskip.c** — a SCALAR ARM, born at R4c (integration.md §15.1;
  transcribed from pcrec's `ofs_test_emit_fn` and friends): THE OFFSET-SKIP
  FUNCTION, a `static inline size_t` returning the leftmost position whose
  every term holds (one `memchr` stream on the scanned term, or the PAIR
  leapfrog on a two-member cube), its offset legend comment and its call.
  `ofsskip_arm` is the offset-skip site (FIND/FUNC/RETURN); `ofs_fn_*` also
  render the pre-check's run blocks. **Since R4e'.0 (lane r4e0,
  2026-10-09; integration.md §R4.9.2.1, the seam) the function's body is a
  first-match table, `fn_rows[]`**, with a SLOT column: BODY (`fn-pair`, the
  pair leapfrog where the scanned position is a two-member cube, above
  `fn-memchr`, the slot's floor) and PREFIX (born EMPTY: the guarded
  per-level helpers SIMD rows will add, D155; an empty slot renders zero
  bytes). `ofs_fn_define` is the seam: the BODY walk, then the PREFIX walk
  handed the BODY row, then the text (the PREFIX row's helpers, the head,
  the BODY loop). Both BODY rows are today's inline `b >= 0` branch moved
  text-for-text, scalar and undeniable (no options.def row); each carries
  a contract (`fn_pair_ct`/`fn_memchr_ct`, the body's own fields: `denies`,
  `table_ref`, no `floor`). Trace table `fn`. Its `miss` (stated as `n`) and `floor`
  (none) edge is its CONTRACT's since N3: the ad hoc define and call tests
  (lane m1bfix's K96 fix) are deleted, the gate does both.
- **precheck.c** — a SCALAR ARM, born at R4c (§15.3-§15.5; transcribed from
  pcrec's `emit_req_*`): THE PRE-CHECK COMPOSITE (ALL_PRESENT, ON_MISS or
  ASSIGN): the one-byte gate, each run's call (its offset-skip function and
  run-search comment at file scope), the set rest's table loop; pcrec's
  notes at pcrec's places. ONE renderer as TWO rows since N3,
  `precheck_arm` (ON_MISS) and `precheck_assign_arm` (ASSIGN), both form id
  `precheck`: an ON_MISS site never reads `miss`, an ASSIGN site tests the
  run call's result against `n`, so the rows serve different `miss` classes
  (and each predicate tests its own handoff).
- **runcmp.c** — a SCALAR ARM, born at M1b (integration.md §15.6, §R4.8;
  transcribed from pcrec's `src/gen/runcmp.c`): THE RUN COMPARE, one
  first-match row table (`words`, `overlap`, `bytes`, `memcmp`; the first
  two denied by `MF_D_RUN_OVERLAP`, read through the table's `deny`
  accessor by `kit_walk` since R4e'.0) and its writers. `run_cmp_render` is the
  RUN term of the offset-skip function's verify chain and the body of
  `runcmp_arm` (VERIFY/EXPR/BOOL behind the caller's guard: pcrec's VM
  literal runs); `run_cmp_prepare` declares a FUNC definition's word-load
  helpers ahead of it; `mf_flush_helpers` writes the pending ones (the art
  records the widths used/declared and the words count `mf_stamps` writes
  as `RUN_WORDS`); `mf_run_rows` is the rows' accessor (`--list-axes`).
  The overlap lengths and the width rule are DERIVED (D149).
- **pffind.c** — a SCALAR ARM, born at R4g (M2; integration.md §15.7;
  transcribed from pcrec's `pcrec_emit_find` and the memchr forms' NULL
  test and store): THE PREFILTER FIND, one FIND / STMT / ASSIGN statement
  over one SET term at offset 0 moving a scan position to the next byte a
  match can begin with. TWO renderers as FOUR rows (N3's split, by
  `end_back`): `pf_memchr_arm` / `pf_memchr_bounded_arm` (a one-byte set:
  `memchr`, then on the unbounded row pcrec's `on_miss` on a NULL hit, which
  must leave, and the store; on the bounded row one store of the hit or
  pcrec's `miss`, `n - 1`), form id `pf_memchr`; `pf_walk_arm` /
  `pf_walk_bounded_arm` (a set pcrec names by table: the in-place walk
  `while (lo < n && !T[s[lo]]) lo++;`, `result` IS `lo`, miss the range's
  end), form id `pf_walk`. The guards around the statement stay pcrec's
  (the memchr rows' empty range is EXCLUDED; the walk's NOP). M4 prep (R-7)
  added a FIFTH row, `pf_memchr_back_arm` (form id `pf_memchr`, the same
  renderer): MLINE's `(?m)^` skip, its one-byte term at offset -1 (the
  candidate's predecessor), `floor` the text of `lo`, `empty` AT_N
  (Q-R7-2), `on_miss` JUMP/BRACED or LOOP_EXIT (`break;`, Q-R7-3), and the
  store adds the 1 back; its range is read-bounded (Q-R7-1). No tuning
  constant (D149).
- **mismatch.c** — F8, THE MISMATCH, born at M7 prep (R-8, MF_VOCAB 3;
  integration.md §15.8; transcribed from pcrec's encoding seam,
  `src/enc/enc_byte.c`/`enc_utf8.c`'s span-compare loops): the compare
  LOOP of the subject from `lo` against a run-time reference span, a STMT
  site inside pcrec's own residual function (RULED Q-R8-2: the signature,
  the full-match return and the meaning of a difference stay pcrec's).
  ONE renderer (`mm_render`) as TWO rows (RULED Q-R8-9): the generic row
  renders the exact and FOLD_EXPR shapes (one `if` per byte, the fold text
  pasted around each operand), `mismatch_inplace_arm` the FOLD_STMT shape
  (two byte temps, `x`/`y` unless a hook names one, the fold statements
  pasted per temp, the subject-end test and the compare as two exits).
  ON_DIFF: the loop index IS `result`, so k is written before `on_miss`
  runs. Operands are pasted raw when identifiers, parenthesized otherwise;
  `on_miss` raw when JUMP/BRACED, braced otherwise, never LOOP_EXIT (its
  own loop encloses it). No tuning constant (D149).
- **k1_ref.c** — K1's REFERENCE functions (`mf_ref_*`): one obviously-
  correct byte loop per primitive (F1 find_byte, F2 find_any2/3, F4
  find_in_set, F5 skip_in_set, F9 find_literal, F7 run_verify, F8
  mismatch since M7 prep). G2's
  oracle side; never artifact text.
- **fields.def** — THE FIELD TABLE of the row contracts ([MEMFN-ROWCON]
  N1, docs/design/memfn/row_contracts.md §2), two X-macros: `MF_CLASS(name,
  doc)` (the value classes, OTHER in every set) and `MF_FIELD(name, phase,
  absent, classify, classes, doc)` (every site/hook/run-term field a row
  reads: where the gate reads it, what an absent value is, including the
  written per-kind OBLIGATION exemptions, its classify function and its
  closed class set, with the text-shape classes IDENT / JUMP / BRACED and,
  since R4h prep, the ADVANCE hooks' CONJ (`more`), POSTFIX (`peek`) and
  EXPR_STMT (`step`); and `count_by_caller`, the caller-owned counter
  (MF_SITE_ABI 5, OBLIG); since M4 prep (MF_SITE_ABI 6) `empty`'s E_AT_N
  (Q-R7-2) and `on_miss`'s LOOP_EXIT (`break;`, Q-R7-3); since M7 prep
  (MF_SITE_ABI 7) the MISMATCH's `fold_kind` (F_NONE/F_ASCII/F_UCP, read on
  a MISMATCH site only) and `fold`'s FOLD_EXPR/FOLD_STMT (a lexical check
  that reads through quoted literals; OTHER where fold_kind is NONE), and
  the `ref`/`reflen` hooks;
  `miss`'s MISS_N is the `MF_MISS_N` token or the text of `n`). Since N3
  `fn_ref` is a hook ID (0 UNSTATED, so a FUNC site stating 0 is refused,
  K-1) rather than an OBLIG exemption, and `s`/`n`/`lo` are read at define
  as well as use (ruling F1).
- **gate.c** — THE ROW-CONTRACT GATE (`stmt_shape` classes `break;` as
  LOOP_EXIT since M4 prep) (its `uses` entries may be CONDITIONAL
  since R4h prep: `GATE_WHEN(cls, field)` applies an entry only where a site
  field has that class, so `count_by_caller` YES makes `count` a use; kit.h
  `gate_use`): also DEFINES the exported `MF_MISS_N`
  sentinel (`mf_miss_n`, memfn.h; `kit.h`'s `kit_miss(h)` resolves it to the
  `n` hook's text, and every reader of `miss` goes through that). fields.def's classify functions
  (`kit_is_ident`, the one lexical identifier check, lives here, beside
  the ADVANCE hooks' `conj_shape`/`postfix_shape`/`expr_stmt_shape` and the
  MISMATCH fold's `fold_shape`; `kit_stmt_shape`/`kit_fold_shape` export
  two of them to a renderer that pastes the text), the
  per-field rules (R1 used-and-unstated, R2 stated-and-not-served) as
  `gate_check`, ENFORCED since N3 at define, use and the run walk (the
  callers decline a failing row, or refuse), `gate_describe` (the text
  every gate refusal names its fields with: backquoted name, rule, class),
  and under the compile-time switch `MF_TRACE` (off by default) the
  `MFTRACE` stderr records and reach counters (format:
  `../docs/trace_format.md`; since N4 the exit lines end with
  `REACH_DROPPED n=N`, the selections a full counter registry could not
  hold (32 rows since R4e'.0, over the three tables), so an undercount is visible rather than silent; a trace build also asks a declined row's
  predicate, so `would_decline` still means "the gate moved this
  selection"). Each
  row's `uses`/`serves`, with a citation per declaration, sits at the end of
  that row's own file (ofsskip.c, precheck.c, runcmp.c, pffind.c, mismatch.c,
  generic.c).
- **options.def** — the kit's option registry, an X-macro
  `MF_OPT(name, kind, budget, layer, doc)` (D147 addendum 9). BORN EMPTY:
  each byte-moving kit change adds its own deny row (`--memfn=no-NAME`) in
  the same commit and raises the floor in `docs/spec/registry.md` §6. See
  `../CLAUDE.md` "The kit's option namespace".
- **options.c** — `mf_options()` and `mf_opts_check()` over options.def:
  what `--list-axes` prints and what `--memfn=` accepts are one table.

The scalar arms are the LIVE scalar layer (D147): improvable kit code, each
change with its own `--memfn=no-NAME` row and, where it moves a byte,
pcrec's abi event and `tests/memfn/pins/arms.tsv` re-pin in the same commit.
Their provenance lines read `pcrec <commit> (relicensed 0BSD by its author, D145 addendum 1)`
(R-4 Q1, ruled by Frank 2026-10-06). Planned, not here yet: the other migrated
sites' arms (M1b on), SIMD forms (R4e′, rendered only under
`-fmemfn-simd`), K3 support. Rules: external symbols through `MF_NS`
(`pcrec_mf_*`; C15), everything else `static`; an SPDX line and a
provenance header on every file, with its row in `../PROVENANCE.md` (C16);
nothing included from pcrec's `src/`/`cli/`/`lib/`.
