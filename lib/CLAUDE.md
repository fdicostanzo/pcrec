# lib — public library API

The only header file installed for embedding pcrec as a library. Declares the three public functions and the options/output/error structs.

## Files

- **pcrec.h** — public API: pcrec_compile(), pcrec_output_free(), pcrec_default_options(); encoding enum and option/output/error types. **[M4.4] (docs/design/match_api_m4.md, the MATCH-API FREEZE, D43.2/D44.8, 2026-08-14)** broke `pcrec_options`: the separate `caseless`/`emit_main` `int` fields are GONE, replaced by one `uint64_t flags` word and the `PCREC_CASELESS`/`PCREC_EMIT_MAIN`/`PCREC_NO_CAPTURES` bit constants (the last RESERVED — no code sets or reads it yet; M4.5-era `--no-captures`) — one representation of each boolean fact end to end, from CLI parse (cli/main.c) through this struct through the generated `rx_info.flags` (src/gen/emit_dfa.c). Also added: `pcrec_err_input`/`pcrec_error.input` (subst note §9 Q8, D42.4 — which input string `pos` indexes into; `pcrec_compile()` always sets `PCREC_ERR_INPUT_PATTERN` today). The `<prefix>_search` doc comment is REWRITTEN for the caps-array signature (D44.2) — see docs/design/match_api_m4.md §1.0/§11 for the full generated-ABI surface this header does NOT declare (the fixed types `rx_ctx`/`rx_matchfn`/`rx_group_entry`/`rx_info`/etc. and the `<prefix>_match`/`<prefix>_match_caps`/`<prefix>_info` entries live in the GENERATED .c/.h, per-artifact, never in this file — this remains the compiler's own library surface only).

**[M4.5b] (2026-08-15)** adds three `pcrec_options` members and two enum
families, all GENERATION AXES (D18: options are compiled away): `engine`
(`PCREC_ENGINE_AUTO`/`_DFA`/`_VM` — do-or-die, and `_VM` also disables the DFA
prefilter per D44/R21 E-6), `step_budget` (`PCREC_STEP_BUDGET_DEFAULT`/`_NONE`
or a count of backtrack resumptions), and `frame_capacity`. `PCREC_NO_CAPTURES`
stops being reserved and becomes live (D42.1: captures ON by default, this bit
recovers the pre-M4.5 pure-DFA artifact). The budget is an axis rather than a
runtime parameter not merely by preference but because it is the ONLY shape
the ruled ABI leaves open: `rx_matchfn`'s signature is frozen with no slot for
one, and adding one to `rx_ctx` is a DD-3 struct revision D38 reserved for
capture export (engine_m4.md §4.6).

**[M4.5c] (2026-08-15)** adds one flag bit, `PCREC_TRACE` (DD-8): emit an
instrumented matcher that prints every resume-frame push/pop and capture write
to stderr. A generation axis like the rest (D18), never the default, and the
artifact stamps that it is traced — a traced matcher writes to stderr, which
is not something a shipped one should ever do.

## Conventions

This is the sole public interface; everything under src/ is internal. The library works in two modes: -o out.c writes a self-contained .c file (no header), or -o out.c with options.header_name='out.h' writes paired .c/.h files. Generated code has no dependency on pcrec at runtime.

Maintenance: update this file when files are added/removed or their roles change.

**[ENG-BREP] (2026-08-16):** `PCREC_NO_POSSESSIFY` (`1u << 4`) joins the flags
word as the first STRATEGY-DENIAL bit — `-fno-possessify`, D47.3's deny family.
It is unlike every other bit here in one way worth stating: it is a testing and
tuning axis, not a semantic option, so it changes no answer and
`src/gen/emit_dfa.c` deliberately MASKS it out of the emitted `rx_info.flags`.
Two artifacts differing only in this bit are byte-identical, which is what
makes the pass's own byte-identity gate expressible at all.

**[ENG-BREP counter-K] (2026-08-17):** the family reaches its third and last
v1 member and gains the rung's two value knobs.

`PCREC_NO_COUNTER` (`1u << 6`, `-fno-counter`) denies the COUNTER rung. Same
masked-out-of-`rx_info.flags` treatment as its two siblings, and the same
role — except that denying THIS one drops a bounded repeat to literal
replication, which is what ships today and is therefore the semantic ground
truth its differential compares against. `unroll_k` is its value parameter
(K, `PCREC_UNROLL_K_DEFAULT` = 0 meaning `PCREC_DEFAULT_UNROLL_K` in
src/core/limits.h): ONE value per artifact, never per quantifier (D47
ADDENDUM held §4.5 strictly; the clamp that would have varied K moved whole
to plan row [ENG-CLAMP]).

`work_budget` (`PCREC_WORK_BUDGET_DEFAULT`/`_NONE`, `--work-budget=N`) is the
THIRD DD-2 bound, ruled at the D47 SECOND ADDENDUM's settlement 4: work units
spent on forward work the fail label never sees — frames discarded at a cut,
frameless scan iterations — reported as `<PREFIX>_ERR_WORK`. It is a SEPARATE
counter from `step_budget`, which keeps its exact meaning of one backtrack
resumption; nothing is scaled into anything. ONE existence gate in v1 (D49):
`--fno-step-budget` suppresses both counters, which keeps the tests/vm
no-counter pin true as written; splitting the gate later is additive.

Note the deliberate split of homes, since the two constants look alike and are
not: K lives in `src/core/limits.h` because changing it changes what pcrec
ACCEPTS (it decides how many copies a bounded repeat emits, against the
replication caps), while the work budget's default lives beside its siblings in
`src/gen/emit_vm.c` because a runtime give-up budget changes nothing pcrec
accepts, rejects or promises — limits.h's own stated inclusion rule, applied in
both directions.
