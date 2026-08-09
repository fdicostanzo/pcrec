# src/gen — C code generation

Emits DFA as self-contained gcc-dialect C using computed goto, per-state jump tables over byte equivalence classes. The generated code has zero dependency on pcrec at build or run time; ASCII/byte encoding is implemented here; future backends (UTF-8, VM engine) will be siblings in this directory.

## Files

- **emit_dfa.c** — DFA → C: computed-goto labels, per-state jump tables, pattern comment, function prologue/epilogue

## Conventions

Generated code uses computed goto for state dispatch and inline jump tables indexed by equivalence class. The emitter produces a self-contained .c file (or paired .c/.h if options.header_name is set). Symbols are prefixed with the user's chosen identifier (default "rx"). Future encoding backends will coexist here as separate emitters (e.g., emit_utf8.c).

Maintenance: update this file when files are added/removed or their roles change.
