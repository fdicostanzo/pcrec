# memfn/src/ — the kit's sources

Built into `libpcrec.a` by pcrec's Makefile (`KITSRCS`, compiled with
`KITFLAGS`: no `-Ilib`/`-Isrc`, so nothing here can include pcrec). Every
file includes its headers by relative path. From R4c pcrec's emitters render
two sites through the kit (src/gen/memfn_sites.c, DELEG_SITES): the
offset-skip block and the pre-check composite, by the scalar arms below.

- **kit.h** — the INTERNAL header: `kb` (growable text over the caller's
  `mf_arena`), the `mf_art` struct and its per-site records, the arm
  interface K2 selects over (an arm writes STRAIGHT TO THE SINK, in order,
  so a hook that writes and the sink's comment gate act at the point the arm
  reaches them), the sink writers (`kit_out`, `kit_flush`) and the
  offset-skip function's shared renderer (`ofs_fn_*`). Never included
  outside this directory.
- **compose.c** — K2, the composer: `mf_art`, the define/use split
  (`mf_define`/`mf_use`/`mf_emit`/`mf_call`; handles checked at use and at
  `mf_art_end`), the vocabulary rules every site must pass (`site_check`,
  `pred_kinds`: out-of-enum fields and every shape integration.md §R4.7
  rules outside the vocabulary are REFUSED loudly) and their table
  (`mf_vocab_has`), the FIRST-MATCH arm table (R4c: `ofsskip`, `precheck`,
  then the generic row), and the artifact queries (`mf_flush_helpers`,
  `mf_includes`: nothing to flush or include yet), and the stamps:
  `mf_art_note_libc` (the libc record's writer, a sorted distinct name list
  on the art) and `mf_stamps` (R4a′: `MEMFN_FORMS "none"`, constant until
  R4f, then `MEMFN_LIBC`, the noted names comma-joined or `none`; two
  `sink->stamp` calls).
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
- **k1_ref.c** — K1's REFERENCE functions (`mf_ref_*`): one obviously-
  correct byte loop per primitive (F1 find_byte, F2 find_any2/3, F4
  find_in_set, F5 skip_in_set, F9 find_literal, F7 run_verify). G2's
  oracle side; never artifact text.
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
