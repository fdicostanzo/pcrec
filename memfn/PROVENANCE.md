# PROVENANCE — where each kit source file's text comes from

`third_party/`'s PROVENANCE shape applied inside the kit (integration.md
§20.3; D145, D147 addendum 1). One row per file under `include/` and
`src/` — every kit file whose text can reach a generated artifact, and the
rest of the kit's sources with them, so the table and the tree are compared
as two whole sets.

- **source** — `original` for the kit's own text; for translated text, the
  upstream project, its version and the file translated.
- **licence** — the SPDX id the file's own header carries. It must be one
  of D145's injectable licences: `0BSD` (the kit's own text, and pcrec's
  text moved into the kit by a migration step: pcrec's author relicenses it
  0BSD, D145 addendum 1; its source reads `pcrec <commit> (relicensed
  0BSD by its author, D145 addendum 1)`), `Unlicense`
  (text translated from Rust `memchr`, taking that crate's `Unlicense` arm
  of `Unlicense OR MIT`), or `CC0-1.0`. MIT/BSD/Apache text is ideas-only
  and never appears here.
- **what derives from it** — which emitted text, or which kit function,
  the file is the origin of.

The check is C16 (`tests/memfn/run_link_checks.sh`): every file in scope
carries an SPDX line with an id from the list above and a `Provenance:`
line; every file has exactly one row here, every row names a file that
exists, and the row's licence equals the file's SPDX id. Add the row in
the change that adds the file.

| file | source | licence | what derives from it |
|---|---|---|---|
| `include/memfn.h` | original | 0BSD | the contract's types and entry points; no artifact text |
| `src/kit.h` | original | 0BSD | the kit's internal types; no artifact text |
| `src/compose.c` | original | 0BSD | K2's selection, handles and artifact queries; no artifact text of its own |
| `src/generic.c` | original | 0BSD | THE GENERIC SCALAR ROW: the text of every site it renders (no pcrec site reaches it at R4c) |
| `src/ofsskip.c` | pcrec 691a8b7c (relicensed 0BSD by its author, D145 addendum 1): `src/gen/emit_dfa.c` (`ofs_test_emit_fn`, `ofs_test_emit_pair`, `ofsk_emit_verify`, `ofsk_emit_params`, `pf_block_ofs`'s comment), transcribed at R4c | 0BSD | THE OFFSET-SKIP FUNCTION: every artifact's `<p>_ofsskip` block, its comment and its calls, and the pre-check's `<p>_reqrun`/`<p>_reqrun_whole` functions; since R4e'.0b/R-13 (original kit text) the routing (`<fn>__body`, the selector) and, at `-fmemfn-simd`, the seam's level-block directives and the selector's `#if` chain |
| `src/precheck.c` | pcrec 691a8b7c (relicensed 0BSD by its author, D145 addendum 1): `src/gen/emit_dfa.c` (`emit_req_one_byte`, `emit_req_run_check`'s call lines, `emit_req_handoff`'s declaration and miss test, `emit_req_set_rest`'s block, `pcrec_emit_req_run_blocks`' comment), transcribed at R4c | 0BSD | THE PRE-CHECK COMPOSITE: every artifact's necessary-byte/run pre-check statements and its run blocks' comments |
| `src/runcmp.c` | pcrec 993f8c1d (relicensed 0BSD by its author, D145 addendum 1): `src/gen/runcmp.c` (the row table and its walk, `rc_emit_words`, `rc_emit_bytes`, `pcrec_emit_run_compare`, `pcrec_runcmp_prepare`, `pcrec_emit_runcmp_helpers`, `pcrec_emit_runcmp_stamp`'s count), transcribed at M1b | 0BSD | THE RUN COMPARE: every artifact's literal-run compares (the VM's literal runs and island chains, the offset-skip function's run term), the `<p>_w<W>` word-load helpers and their comment, the `RUN_WORDS` count, and the `run-overlap` rows `--list-axes` prints |
| `src/pffind.c` | pcrec 5e9ec93c (relicensed 0BSD by its author, D145 addendum 1): `src/gen/emit_dfa.c` (`pcrec_emit_find`'s two forms, `pf_emit_memchr`'s NULL test and position store, `pf_emit_memchr_bounded`'s clamped store), transcribed at R4g | 0BSD | THE PREFILTER FIND: every artifact's PF statement (the DFA prefilter's `memchr`/`memchr-bounded`/`byte-class`/`byte-class-bounded` and the DFA hat's `first-*-bounded` skip statements, and the VM hat's attempt seek) |
| `src/mismatch.c` | pcrec 1adead14 (relicensed 0BSD by its author, D145 addendum 1): `src/enc/enc_byte.c` (the compare loops of `defs_bref`, `defs_bref_ci`, `defs_bref_ci_ucp`) and `src/enc/enc_utf8.c` (`u8_defs_bref`'s), transcribed at M7 | 0BSD | THE MISMATCH (F8): the compare loop of every artifact's `<p>_span_match` and byte-wise `<p>_span_match_caseless` (the generic row's exact and expression-fold shapes, the row `mismatch_inplace`'s in-place fold) |
| `src/k1_ref.c` | original | 0BSD | K1's reference functions (G2's oracle); never artifact text |
| `src/options.c` | original | 0BSD | `mf_options()` / `mf_opts_check()`; the `--list-axes` `memfn` section's rows |
| `src/options.def` | original | 0BSD | the kit's option registry (empty at R4a; R4e' batch 1's `vrun-*` deny rows since R-13) |
| `src/levels.def` | original | 0BSD | the kit's ISA levels (R4e' batch 1, R-13): every level guard, intrinsics `#include` and level token a SIMD-on artifact carries |
| `src/levels.c` | original | 0BSD | `mf_levels()` / `kit_level()` over levels.def; no artifact text of its own |
| `src/vrun.c` | pcrec 631771b7 (relicensed 0BSD by its author, D145 addendum 1): `docs/design/memfn/probes/twins/tb_r4b.c` (`f_ffl`, R-1's hand twin: the block loop, lane mask and overlapped final block), transcribed at R-13; the vector operations are the compiler's documented intrinsics, named, no third-party text | 0BSD | THE FIRST SIMD ROWS `vrun-w16`/`vrun-w32` (R4e' batch 1): the body of every guarded `<fn>__w16`/`<fn>__w32` helper a `-fmemfn-simd` artifact carries |
| `src/fields.def` | original | 0BSD | the row contracts' field and class table ([MEMFN-ROWCON] N1); no artifact text |
| `src/gate.c` | original | 0BSD | the row-contract gate and the MF_TRACE records ([MEMFN-ROWCON] N1); no artifact text |
