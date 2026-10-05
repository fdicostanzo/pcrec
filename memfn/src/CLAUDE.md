# memfn/src/ — the kit's sources

Built into `libpcrec.a` by pcrec's Makefile (`KITSRCS`, compiled with
`KITFLAGS`: no `-Ilib`/`-Isrc`, so nothing here can include pcrec). Every
file includes its headers by relative path. At R4a pcrec CALLS NOTHING here
except `mf_options()` (the `--list-axes` `memfn` section): the code links,
and no emitter renders through it.

- **kit.h** — the INTERNAL header: `kb` (growable text over the caller's
  `mf_arena`), the `mf_art` struct and its per-site records, and the arm
  interface K2 selects over. Never included outside this directory.
- **compose.c** — K2, the composer: `mf_art`, the define/use split
  (`mf_define`/`mf_use`/`mf_emit`/`mf_call`; handles checked at use and at
  `mf_art_end`), the vocabulary rules every site must pass (`site_check`)
  and their table (`mf_vocab_has`), the FIRST-MATCH arm table (one row at
  R4a: the generic row), and the artifact queries (`mf_flush_helpers`,
  `mf_includes`, `mf_stamps`: nothing to flush, include or stamp yet; the
  stamps are born at R4a′).
- **generic.c** — THE GENERIC SCALAR ROW (integration.md §14.6): the last
  row of every selection table, rendering every site the vocabulary
  describes as a plain byte loop (GNU C statement expressions for EXPR; a
  `static inline` definition plus calls for FUNC; STMT ASSIGN, ON_MISS,
  ON_CAND and ADVANCE). It tests every term, honours `floor`, `n`,
  `end_back` and the empty outcome, and uses pcrec's `member` hook for a
  set when one is given. No tuning constant (D149).
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

Planned, not here yet: the scalar arms migrated from pcrec (M1 on; the live
scalar layer, D147), SIMD forms (R4e′, rendered only under
`-fmemfn-simd`), K3 support. Rules: external symbols through `MF_NS`
(`pcrec_mf_*`; C15), everything else `static`; an SPDX line and a
provenance header on every file, with its row in `../PROVENANCE.md` (C16);
nothing included from pcrec's `src/`/`cli/`/`lib/`.
