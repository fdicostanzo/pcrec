# src/core — pipeline driver and memory management

Home of the compilation pipeline driver and shared utilities: arena allocator for AST/IR, growable string buffer for codegen output, shared type definitions, and longjmp error handling.

## Files

- **compile.c** — pcrec_compile() pipeline driver (parse → SELECT ENGINE →
  NFA → DFA → emit);
  ctx_fail error handler; pcrec_default_options defaults; and
  pcrec_count_groups(), the parse-only entry behind the CLI's
  `--count-groups` (MOD-0.1/§18.1 — reports Ctx.ncap's end-of-parse value
  with pcrec_compile's exact refusal behaviour; it lives here because this
  file holds the tree's ONLY setjmp)
  **[M4.5b]** the pipeline gained two things. Engine selection moved OUT of
  this file's inline `if` into a pass (src/opt/select_engine.c) that runs
  after parse and BEFORE machine construction, so a `--engine` request pcrec
  cannot honour is diagnosed without paying for an automaton first; and the
  DFA pair is now built CONDITIONALLY — when the DFA is the engine, or when
  the VM wants it as its prefilter, but NOT for `--engine=vm`, where
  engine_m4.md §5.6/D44/R21 E-6 turns the prefilter off. That last case is
  why the build is skipped rather than merely ignored: `--engine=vm` is meant
  to be an INDEPENDENT second derivation of the match span, and an
  independence you get by not consulting an answer you did compute is weaker
  than one you get by never computing it. `Ctx.want_caps` (seeded from
  PCREC_NO_CAPTURES) and `Ctx.first_cap_pos` are seeded here too, and cleared
  for pcrec_count_groups, which emits nothing.

  **[M4.5c]** `pcrec_compile` and DD-8's `pcrec_emit_ir` are now two thin
  callers of ONE driver, `compile_driver`, differing in a single bool. The
  fork is the thing to avoid on principle (M2.12's `$`-engine fork is the
  standing example) and here it would also break engine_m4.md §10's constraint
  at the pipeline level: a listing produced by a second driver would describe
  a compile that never happened. `--emit-ir` therefore runs a REAL compile and
  throws the C away — the cost of the guarantee, on a debug tool.

- **arena.c** — zeroing arena allocator; 16-byte aligned blocks, minimum 64KB per block
- **sb.c** — growable string buffer for C code emission; sb_putc, sb_puts, sb_printf
- **limits.h** — every number that decides what pcrec ACCEPTS, REJECTS or
  PROMISES, in three sections that ARE D26's tiers: ours (free to tune), PCRE2
  syntax (exact, and measured — the 65535 repeat ceiling, the 250 nesting cap),
  and PCRE2 internals (minimums we honour, not contracts we owe). The
  provenance is the point: a bare `250` and a bare `60` look alike and are not.
  Structural constants (256 byte values, block sizes, growth factors) and local
  algorithmic bounds with proofs beside them stay where they are, deliberately —
  see the file's own inclusion rule before adding to it
- **internal.h** — shared data structures: Arena, StrBuf, Ctx, Nfa, Dfa,
  **[M4.5b]'s `A_CAP` AST node and `EngineFit`**, the
  syntax construct registry types (RegRow and its FEAT_/FLAV_/ENGM_/RS_/RD_
  vocabulary, D24), the `(*` doorway's NAME tables (VerbName/VerbTable and the
  VF_* form bits, D25/Q1 — a SECOND schema on purpose, because a verb name
  answers one externally-measured question while a RegRow carries a module, a
  feature bit and an engine mask it would have to invent), the POSIX
  class-bracket NAME table (PosixName, MOD-0.3a — a third schema, per-name
  module attribution), the doorway vocabulary (ExtWhat/ExtWant/ExtResult,
  moved above RegRow at MOD-0.3b when ports embedded it) with the ExtPort
  producing-port types, and module-level declarations.

  **`A_CAP` and D31 ([M4.5b]).** D31 ruled the group erasure STAYS, on a
  MEASURED compile-time cost; engine_m4.md §11.3 records that the VM
  nonetheless needs SOME node to know where to emit a capture write. Both
  hold at once, and the reason is worth reading before touching either: the
  node is BORN ONLY WHEN CAPTURES ARE REQUESTED (`Ctx.want_caps`), and it is
  TRANSPARENT to every consumer but the VM emitter (`ast_bare` in
  src/ir/nfa.c). So a capture-free pattern's AST is byte-identical to D31's
  always, `--no-captures` reproduces D31's AST for any pattern, and the
  prefilter machine built for a capture pattern is STATE-FOR-STATE the
  machine the capture-erased pattern builds — which is §6.1's STRUCTURAL
  erasure half and §11.3's "two lowerings from one parse" mitigation,
  obtained without a second tree. That is also what makes §5.4's
  byte-identity gate hold by construction rather than by audit

  **[ENG-BREP]** `Ast` gains `possessive` (A_REP only, set by
  src/opt/possessify.c), `revbody` (A_REP only, set by src/opt/revdet.c to the
  body's REVERSED AST when engine_m4.md §2.5's reverse-deterministic rung
  applies, and NULL otherwise — so one field is both the verdict and the
  material the emitter's backward walk is built from, which is what stops the
  emitter's three rung-reading sites from each re-deciding), and `ModState`
  gains `multiline`. The second has NO
  WRITER today and exists as a field rather than as a comment because D47.5
  rules the `$`-follow exemption's gate a LIVE CHECK: `$` in a quantifier's
  follow is measured safe at 0/720 diverging cells and UNSAFE at 180/720 under
  `(?m)`, so the exemption is conditional on a fact that would otherwise stop
  being true without anyone revisiting the analysis. Module `assertions` is its
  writer and inherits the test obligation.

## Conventions

All dynamic allocations for AST/IR go through arena_alloc() and are freed together. StrBuf accumulates generated code; sb_* functions append. Error paths longjmp to cx.jb. internal.h is NOT installed; it is internal to src/.

Maintenance: update this file when files are added/removed or their roles change.
