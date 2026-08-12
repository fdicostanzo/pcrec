# src/core — pipeline driver and memory management

Home of the compilation pipeline driver and shared utilities: arena allocator for AST/IR, growable string buffer for codegen output, shared type definitions, and longjmp error handling.

## Files

- **compile.c** — pcrec_compile() pipeline driver (parse → NFA → DFA → emit);
  ctx_fail error handler; pcrec_default_options defaults; and
  pcrec_count_groups(), the parse-only entry behind the CLI's
  `--count-groups` (MOD-0.1/§18.1 — reports Ctx.ncap's end-of-parse value
  with pcrec_compile's exact refusal behaviour; it lives here because this
  file holds the tree's ONLY setjmp)
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
- **internal.h** — shared data structures: Arena, StrBuf, Ctx, Nfa, Dfa, the
  syntax construct registry types (RegRow and its FEAT_/FLAV_/ENGM_/RS_/RD_
  vocabulary, D24), the `(*` doorway's NAME tables (VerbName/VerbTable and the
  VF_* form bits, D25/Q1 — a SECOND schema on purpose, because a verb name
  answers one externally-measured question while a RegRow carries a module, a
  feature bit and an engine mask it would have to invent), the POSIX
  class-bracket NAME table (PosixName, MOD-0.3a — a third schema, per-name
  module attribution), the doorway vocabulary (ExtWhat/ExtWant/ExtResult,
  moved above RegRow at MOD-0.3b when ports embedded it) with the ExtPort
  producing-port types, and module-level declarations

## Conventions

All dynamic allocations for AST/IR go through arena_alloc() and are freed together. StrBuf accumulates generated code; sb_* functions append. Error paths longjmp to cx.jb. internal.h is NOT installed; it is internal to src/.

Maintenance: update this file when files are added/removed or their roles change.
