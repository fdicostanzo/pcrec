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
  offset-skip function's shared renderer (`ofs_fn_*`), and the row
  contracts' types (`gate_contract`: `uses` per site kind and phase,
  `serves` per field; `CL_*`/`FLD_*` from fields.def) and the MF_TRACE
  record calls. Never included outside this directory.
- **compose.c** — K2, the composer: `mf_art`, the define/use split
  (`mf_define`/`mf_use`/`mf_emit`/`mf_call`; handles checked at use and at
  `mf_art_end`), the vocabulary rules every site must pass (`site_check`,
  `pred_kinds`: out-of-enum fields and every shape integration.md §R4.7
  rules outside the vocabulary are REFUSED loudly) and their table
  (`mf_vocab_has`), the FIRST-MATCH arm table (`ofsskip`, `precheck`,
  `precheck_assign` (one renderer, two rows: N3's split by handoff),
  `runcmp`, the four PF rows (`pf_memchr`, `pf_memchr_bounded`, `pf_walk`,
  `pf_walk_bounded`: R4g), then the generic row; each arm's `ct` is its contract, which
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
- **ofsskip.c** — a SCALAR ARM, born at R4c (integration.md §15.1;
  transcribed from pcrec's `ofs_test_emit_fn` and friends): THE OFFSET-SKIP
  FUNCTION, a `static inline size_t` returning the leftmost position whose
  every term holds (one `memchr` stream on the scanned term, or the PAIR
  leapfrog on a two-member cube), its offset legend comment and its call.
  `ofsskip_arm` is the offset-skip site (FIND/FUNC/RETURN); `ofs_fn_*` also
  render the pre-check's run blocks. Its `miss` (stated as `n`) and `floor`
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
  two denied by `MF_D_RUN_OVERLAP`) and its writers. `run_cmp_render` is the
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
  (the memchr rows' empty range is EXCLUDED; the walk's NOP). No tuning
  constant (D149).
- **k1_ref.c** — K1's REFERENCE functions (`mf_ref_*`): one obviously-
  correct byte loop per primitive (F1 find_byte, F2 find_any2/3, F4
  find_in_set, F5 skip_in_set, F9 find_literal, F7 run_verify). G2's
  oracle side; never artifact text.
- **fields.def** — THE FIELD TABLE of the row contracts ([MEMFN-ROWCON]
  N1, docs/design/memfn/row_contracts.md §2), two X-macros: `MF_CLASS(name,
  doc)` (the value classes, OTHER in every set) and `MF_FIELD(name, phase,
  absent, classify, classes, doc)` (every site/hook/run-term field a row
  reads: where the gate reads it, what an absent value is, including the
  written per-kind OBLIGATION exemptions, its classify function and its
  closed class set, with the text-shape classes IDENT / JUMP / BRACED;
  `miss`'s MISS_N is the `MF_MISS_N` token or the text of `n`). Since N3
  `fn_ref` is a hook ID (0 UNSTATED, so a FUNC site stating 0 is refused,
  K-1) rather than an OBLIG exemption, and `s`/`n`/`lo` are read at define
  as well as use (ruling F1).
- **gate.c** — THE ROW-CONTRACT GATE: also DEFINES the exported `MF_MISS_N`
  sentinel (`mf_miss_n`, memfn.h; `kit.h`'s `kit_miss(h)` resolves it to the
  `n` hook's text, and every reader of `miss` goes through that). fields.def's classify functions
  (`kit_is_ident`, the one lexical identifier check, lives here), the
  per-field rules (R1 used-and-unstated, R2 stated-and-not-served) as
  `gate_check`, ENFORCED since N3 at define, use and the run walk (the
  callers decline a failing row, or refuse), `gate_describe` (the text
  every gate refusal names its fields with: backquoted name, rule, class),
  and under the compile-time switch `MF_TRACE` (off by default) the
  `MFTRACE` stderr records and reach counters (format:
  `../docs/trace_format.md`; since N4 the exit lines end with
  `REACH_DROPPED n=N`, the selections a full counter registry could not
  hold, so an undercount is visible rather than silent; a trace build also asks a declined row's
  predicate, so `would_decline` still means "the gate moved this
  selection"). Each
  row's `uses`/`serves`, with a citation per declaration, sits at the end of
  that row's own file (ofsskip.c, precheck.c, runcmp.c, pffind.c, generic.c).
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
