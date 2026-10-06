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
  0BSD; Frank's ruling is PENDING, R-4 Q1), `Unlicense`
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
| `src/ofsskip.c` | pcrec 691a8b7c `src/gen/emit_dfa.c` (`ofs_test_emit_fn`, `ofs_test_emit_pair`, `ofsk_emit_verify`, `ofsk_emit_params`, `pf_block_ofs`'s comment), transcribed at R4c (relicensed 0BSD by its author; ruling pending) | 0BSD | THE OFFSET-SKIP FUNCTION: every artifact's `<p>_ofsskip` block, its comment and its calls, and the pre-check's `<p>_reqrun`/`<p>_reqrun_whole` functions |
| `src/precheck.c` | pcrec 691a8b7c `src/gen/emit_dfa.c` (`emit_req_one_byte`, `emit_req_run_check`'s call lines, `emit_req_handoff`'s declaration and miss test, `emit_req_set_rest`'s block, `pcrec_emit_req_run_blocks`' comment), transcribed at R4c (relicensed 0BSD by its author; ruling pending) | 0BSD | THE PRE-CHECK COMPOSITE: every artifact's necessary-byte/run pre-check statements and its run blocks' comments |
| `src/k1_ref.c` | original | 0BSD | K1's reference functions (G2's oracle); never artifact text |
| `src/options.c` | original | 0BSD | `mf_options()` / `mf_opts_check()`; the `--list-axes` `memfn` section's rows |
| `src/options.def` | original | 0BSD | the kit's option registry (empty at R4a) |
