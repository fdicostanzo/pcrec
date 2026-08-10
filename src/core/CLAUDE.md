# src/core — pipeline driver and memory management

Home of the compilation pipeline driver and shared utilities: arena allocator for AST/IR, growable string buffer for codegen output, shared type definitions, and longjmp error handling.

## Files

- **compile.c** — pcrec_compile() pipeline driver (parse → NFA → DFA → emit); ctx_fail error handler; pcrec_default_options defaults
- **arena.c** — zeroing arena allocator; 16-byte aligned blocks, minimum 64KB per block
- **sb.c** — growable string buffer for C code emission; sb_putc, sb_puts, sb_printf
- **internal.h** — shared data structures: Arena, StrBuf, Ctx, Nfa, Dfa, the
  syntax construct registry types (RegRow and its FEAT_/FLAV_/ENGM_/RS_/RD_
  vocabulary, D24), the `(*` doorway's NAME tables (VerbName/VerbTable and the
  VF_* form bits, D25/Q1 — a SECOND schema on purpose, because a verb name
  answers one externally-measured question while a RegRow carries a module, a
  feature bit and an engine mask it would have to invent), and module-level
  declarations

## Conventions

All dynamic allocations for AST/IR go through arena_alloc() and are freed together. StrBuf accumulates generated code; sb_* functions append. Error paths longjmp to cx.jb. internal.h is NOT installed; it is internal to src/.

Maintenance: update this file when files are added/removed or their roles change.
