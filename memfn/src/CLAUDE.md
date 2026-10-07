# memfn/src/ — the kit's sources

Built into `libpcrec.a` by pcrec's Makefile (`KITSRCS`, compiled with
`KITFLAGS`: no `-Ilib`/`-Isrc`, so nothing here can include pcrec). Every
file includes its headers by relative path. From R4c pcrec's emitters render
two sites through the kit (src/gen/memfn_sites.c, DELEG_SITES): the
offset-skip block and the pre-check composite, by the scalar arms below;
from M1b, a third, the VM's literal-run compare (VMRUN, runcmp.c).

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
  `runcmp`, then the generic row; each arm's `ct` is its contract, which
  the WARN gate reads before the arm's predicate and re-checks against the
  use hooks in `mf_use`), the art's one `denies` value (a site
  whose `denies` differ is refused, Q-M1b-1), the `mf_includes` query, and
  the stamps: `mf_art_note_libc` (the libc record's writer, a sorted
  distinct name list on the art; every arm that renders a libc call notes
  it at the render, beside its `includes` bit: `memchr` in `ofs_fn_define`
  and `precheck_use`, `memcmp` in `run_cmp_render`; the word-load helper's
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
  render the pre-check's run blocks.
- **precheck.c** — a SCALAR ARM, born at R4c (§15.3-§15.5; transcribed from
  pcrec's `emit_req_*`): THE PRE-CHECK COMPOSITE (ALL_PRESENT, ON_MISS or
  ASSIGN): the one-byte gate, each run's call (its offset-skip function and
  run-search comment at file scope), the set rest's table loop; pcrec's
  notes at pcrec's places.
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
  closed class set, with the text-shape classes IDENT / JUMP / BRACED).
- **gate.c** — THE ROW-CONTRACT GATE: fields.def's classify functions
  (`kit_is_ident`, the one lexical identifier check, lives here), the
  per-field rules (R1 used-and-unstated, R2 stated-and-not-served) as
  `gate_check`, run in WARN mode at define, use and the run walk (verdicts
  recorded on `site_rec`/`mf_art`, no selection changed), and under the
  compile-time switch `MF_TRACE` (off by default) the `MFTRACE` stderr
  records and reach counters (format: `../docs/trace_format.md`). Each
  row's `uses`/`serves`, with a citation per declaration, sits at the end of
  that row's own file (ofsskip.c, precheck.c, runcmp.c, generic.c).
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
