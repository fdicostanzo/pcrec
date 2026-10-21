# src/enc — the ENCODING BACKENDS

The DD-12 residual seam ([M5-SEAM], D58). Everything an artifact carries that
depends on which ENCODING it was compiled for lives here, in exactly one file
per encoding. Layer position: `lib -> core -> enc -> parse -> ir -> opt -> gen
-> driver/dump -> cli` (a layer BETWEEN `core` and `parse`; [REVW.3] moved it
from `src/gen/enc/` because `max_cp`/`fold`/`advance`/`start_cls`/`start_guard`
are data fields lower layers read). This directory includes no gen or kit
header and calls nothing above `core`.

## Standing rules

- Maintenance: update this file when files are added/removed or their roles
  change.
- DD-12 (7): NO encoding conditionals anywhere (compiler, emitter, artifact).
  Encodings are SEALED BACKENDS; the only "switch" is WHICH backend's text an
  artifact embedded. No `if (enc == UTF8)`; adding one is the design-stop
  signal. Ask the TABLE (`pcrec_enc_has_entry`, `engine_callable`, a field),
  never the encoding or its fold object.
- The seam is for the enumerable runtime-identity RESIDUE, NOT the HOT PATH.
  Enforced by `tests/codegen/run_codegen_tests.sh` `[M5-SEAM/DD-12(7)]`
  (every emitted engine body checked for a residual reference), sabotage
  `tests/mech/sabotages/S68_residual_in_hot_loop.sh` (changes no answer, so only a
  structural check sees it).
- Every interface change the seam forces is RECORDED against D58 (revisit
  clause), even "nothing changed". Growth by CONSTRUCT is a ROW in the entries
  table, never a new `PcrecEncEntry` field; per-backend data goes in `PcrecEnc`
  scalars/text and each such addition grows the recipe below by one line.
- Adding a backend (third-encoding recipe): one `enc_<name>.c` here, an
  `extern` in `enc.h`, a row in `enc.c`'s table (the Makefile globs
  `src/enc/*.c`). The row carries: residual ENTRIES, `max_cp`, `onebyte_max`,
  `fold` (NEVER NULL: an empty relation, so no encoding opts out of case
  questions), `restrict_ok`, `advance` text, `start_cls` + `start_guard`
  (NULL both if no position is restricted), and a `sites` table if its span
  compare is byte-wise. NOTHING in `src/core`, `parse`, `ir`, `opt`, `gen`,
  `cli/`, `lib/` is touched; if a shared file outside this directory must
  change, stop: take it to a design decision (the derailment DD-12 names).
- Residual text: `$` is the prefix placeholder and `@` begins the one site
  token (`PCREC_ENC_SITE`); no other `$` or `@` (`pcrec_enc_emit_text`
  refuses a stray `@`; a site-data fold text's `@` is the kit operand).
  Text is ASCII-only, including comments (src/gen/CLAUDE.md standing rule).
- Each text blob is a PAIR since [EMIT-VERB] (D112): `decls`/`decls_doc`,
  `defs`/`defs_doc`; a backend states which half is prose (either `_doc` may
  be NULL), no renderer parses C to find out.
- `enc_byte.c` carries no comment into the artifact (D76 identity gate pins
  that path); `advance` there is the bare `@P++;`.
- `max_cp` answers "what does `[^x]` mean" (contiguous repertoire only; a
  codepage backend would not fit it, D77-recorded, not built). A pending row
  still carries its true `max_cp` (no wrong value waiting for a reader).
- `fold` is per-encoding because the folds disagree: `byte` folds exactly the
  52 ASCII letters (never 0xE9), `utf8` folds Unicode simple. The fold is
  spelled ARITHMETICALLY in residual text (never `tolower()`: locale-dependent).
  Tied to the compiler-side fold by `tests/backrefs/fold_agreement_check.c`
  (byte), `fold_agreement_utf8_check.c` (`run_backref_diff.sh` 9b),
  `fold_agreement_ucp_check.c` (UCP).
- Compare protocol: the span compares RETURN A LENGTH; on failure negative,
  `-(r)-1` = prefix that compared equal (work the budget must be told about).
  One protocol across encodings (do not "optimize" byte into a second one).
  Two entries (exact / caseless), not one with a flag (D18/D23: options
  compile away). The pair takes `(const unsigned char *ref, size_t reflen)`
  ([VAR]), serving backreferences and `${name}` variables alike (no sibling
  pair; memory `pcrec-general-mechanisms-not-special-cases`).
- `back_step` returns the sentinel `<prefix>_BACK_STEP_NONE` (`(size_t)-1`),
  not a signed length; `s`/`n` parameters stay (adding one later is an ABI
  break). Engine-callable.
- `engine_callable` is a fact about the ENTRY, consumed on the compile path
  (`emit_vm.c` `A_BREF` via `pcrec_enc_entry_engine_callable`). `next_pos` is
  `false` (the engine advances via the inline `advance` text); compares and
  `back_step` are `true` (no automaton representation).
- `advance` is spelled again as `next_pos`, `start_cls`, `start_guard`: drift
  hazard, tied by `tests/codegen/run_encoding_checks.sh` (K49 advance-
  agreement, extracted from an emitted artifact, non-vacuous both ways) and
  `tests/utf8/run_startbnd_diff.sh` (INDEPENDENT boundary predicate).
- `start_cls` must be disjoint from word/newline bytes (class-axis partition
  `UPC_NOSTART`); a backend failing it is refused at `pcrec_enc_start_cls_ok()`
  (silent failure otherwise). `start_guard` opens `@P == 0 ||` (ASK 1: no
  validation pass, `utf8_design.md` 2.6). Under `byte` both are NULL: no gate,
  no guard, `PCREC_NO_STARTPOS_GUARD` masked out of `rx_info.flags`.
- The entry MASK is DISCOVERED BY EMITTING, not predicted: `Job.enc_mask`
  starts at `PCREC_ENCE_NEXT_POS`; emitters OR in what they call; the
  prologue is written AFTER the body. Never emit dead residual text.
- `pcrec_enc_ready` = "has a non-empty entries array" (a third site any
  seam change touches, besides the two emit functions).
- A name pcrec knows but cannot compile (`utf8` row, no backend) must be
  refused BY ITS OWN NAME ([SR-10] single namespace); no site maps encoding
  names of its own.
- Kit site token (D58 addendum 2, [MEMFN] M7): byte-wise compares write
  `PCREC_ENC_SITE` (whole line `@site@`) plus a keyed side table
  (`PcrecEncSite`, `PcrecEnc.sites`: fold kind, fold text, failure statement);
  `emit_dfa.c` `emit_residual_defs` describes the site to the kit (DELEG row
  N7, `pcrec_memfn_span_site`) and passes rendered loops back as strings;
  `pcrec_enc_emit_text` checks the token rules. A walk whose unit is the
  encoding's character (utf8 caseless) keeps its body, no row (D147 add. 14).
  Operand spellings are one set (`PCREC_ENC_SPAN_*`); changing kit-rendered
  bytes is a pcrec abi event (D76/D94 ritual).
- Entry columns: `requires` (entries a body calls; both emit functions close
  the mask via `pcrec_enc_mask_close`) and `inline_def` (`static inline`, empty
  `decls`, emitted by `pcrec_enc_emit_inline_defs` in table order ahead of the
  engine bodies; `pcrec_enc_emit_defs` skips it; its `decls_doc` rides the
  inline half, never the `.h`). Span compares and `BACK_STEP` are `inline_def`
  ([LOSS-REVIEW] cand. 1, abi 76).
- `PCREC_ENCE_DECODE` (`$_decode`, one decoder shared by utf8 caseless
  compare, [CLS-TREE] S4); `entries_byte[]` has no row, so the VM keeps a
  class's byte child. `$_var_valid` is present only where validity is a
  question (`pcrec_enc_has_entry(e, PCREC_ENCE_VAR_VALID)`), is NOT
  `engine_callable`, and is re-spelled on `$_valid_upto` (one validator, D133
  Q7).
- [UTF-VALID] (D133) `PCREC_ENCE_VALID_UPTO`: ALWAYS in the mask, every
  backend has a row (`byte`: `return n;`), not engine_callable. Step-back is
  PCRE2's raw walk (utf_valid_design.md 1.3), NOT `$_back_step`. `$_VALID_LB`
  is defined by `emit_residual_defs` from `Ctx.lb_max` on every artifact.
  ASCII fast path via `__builtin_memcpy` (no `<string.h>`).
  `pcrec_utf_check_on` (gen/emit_dfa.c) is the predicate (table row + flag).
- `restrict_ok` ([K70]): `byte` true, `utf8` false; `mod_modifiers.c` `(?r)`
  port reads it and REFUSES by name when false (never silent miscompile).
- [UCP] U2 `onebyte_max` (byte 0xFF, utf8 0x7F): `pcrec_enc_set_bytes`
  returns a set's byte image only if all members <= it; every A_CTX
  set-to-bytes site asks it (`\b` port, `src/parse/ctxnode.c`, NFA lowering,
  VM `vm_ctx`).
- K94: byte-only UCP caseless row `PCREC_ENCE_SPAN_CASELESS_UCP` replaces the
  plain one in the mask; `vm_caseless_entry` (emit_vm.c) picks it when
  `Ast.u.bref.ucp`/`u.var.ucp` and the table carries it; its Latin-1 fold
  table comes from `enc_emit_latin1_fold_table` (enc.c) over
  `pcrec_fold_latin1_rep` (core/fold.c).
- `pcrec_enc_names` over-long policy is an ordered PREFIX (same as
  `src/parse/enabled.c` `render_modules`).

## Files

- `enc.h` — whole seam interface: `PcrecEnc` row, `PcrecEncEntry`, entry ids =
  mask bits, `PcrecEncSite`, registry accessors, `pcrec_enc_emit_text`,
  `pcrec_enc_advance`; its header comment holds the third-encoding recipe.
- `enc.c` — registry table (encoding namespace's one definition), by-id/by-name
  lookups, name menu, `$`-to-prefix substitution, `pcrec_enc_set_bytes`,
  `enc_emit_latin1_fold_table`.
- `enc_byte.c` — `PCREC_ENC_BYTE` backend (identity-shaped entries: next_pos,
  span_match, span_match_caseless, span_match_caseless UCP, back_step,
  valid_upto), each with its contract comment emitted beside its declaration.
- `enc_utf8.c` — `PCREC_ENC_UTF8` backend (next_pos, back_step with
  declared-length repair, span compares, decode, valid_upto, advance).
- `utf8_fold_pairs.inc` — GENERATED sorted `{from,to}` map of the 1,484
  non-identity simple folds, `#include`d into utf8's residual text.

## Pointers

D58 (+ addenda), DD-12, D76/D94, D112, D133, D147; `docs/design/utf8_design.md`;
`docs/design/lookaround_design.md` 3.7, 4.3; `docs/design/ucp_design.md` 2.3;
`docs/design/cls_tree_design.md`; `docs/design/utf_valid_design.md`;
`docs/design/variables_pattern.md`; `docs/spec/match_api.md` 3.1;
`docs/design/encoding_data_layout.md`; `src/CLAUDE.md`; `src/gen/CLAUDE.md`.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/src__enc.md
