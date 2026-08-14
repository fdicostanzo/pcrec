# lib — public library API

The only header file installed for embedding pcrec as a library. Declares the three public functions and the options/output/error structs.

## Files

- **pcrec.h** — public API: pcrec_compile(), pcrec_output_free(), pcrec_default_options(); encoding enum and option/output/error types. **[M4.4] (docs/design/match_api_m4.md, the MATCH-API FREEZE, D43.2/D44.8, 2026-08-14)** broke `pcrec_options`: the separate `caseless`/`emit_main` `int` fields are GONE, replaced by one `uint64_t flags` word and the `PCREC_CASELESS`/`PCREC_EMIT_MAIN`/`PCREC_NO_CAPTURES` bit constants (the last RESERVED — no code sets or reads it yet; M4.5-era `--no-captures`) — one representation of each boolean fact end to end, from CLI parse (cli/main.c) through this struct through the generated `rx_info.flags` (src/gen/emit_dfa.c). Also added: `pcrec_err_input`/`pcrec_error.input` (subst note §9 Q8, D42.4 — which input string `pos` indexes into; `pcrec_compile()` always sets `PCREC_ERR_INPUT_PATTERN` today). The `<prefix>_search` doc comment is REWRITTEN for the caps-array signature (D44.2) — see docs/design/match_api_m4.md §1.0/§11 for the full generated-ABI surface this header does NOT declare (the fixed types `rx_ctx`/`rx_matchfn`/`rx_group_entry`/`rx_info`/etc. and the `<prefix>_match`/`<prefix>_match_caps`/`<prefix>_info` entries live in the GENERATED .c/.h, per-artifact, never in this file — this remains the compiler's own library surface only).

## Conventions

This is the sole public interface; everything under src/ is internal. The library works in two modes: -o out.c writes a self-contained .c file (no header), or -o out.c with options.header_name='out.h' writes paired .c/.h files. Generated code has no dependency on pcrec at runtime.

Maintenance: update this file when files are added/removed or their roles change.
