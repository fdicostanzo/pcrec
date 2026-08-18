# src — internal compiler implementation

The compilation pipeline: pattern → parser (parse/) → AST → NFA → priority DFA (ir/) → optimization passes (opt/) → C codegen (gen/). Core utilities and shared data structures in core/; pipeline driver is pcrec_compile() in core/compile.c.

## Files

- **core/** — pipeline driver, arena allocator, string buffer, shared type definitions
- **parse/** — base-tier PCRE parser with module lookup hooks
- **ir/** — NFA construction and priority subset construction (DFA)
- **opt/** — IR/DFA optimization passes (APPROACH §5): minimization
- **gen/** — DFA to gcc-dialect C code emission
- **gen/enc/** — [M5-SEAM] the ENCODING BACKENDS (D58, DD-12): the
  per-encoding residual block each artifact embeds, one file per encoding
  behind one registry. The compiler and the emitter carry NO encoding
  conditionals; the only switch is which backend's text was embedded. See
  gen/enc/CLAUDE.md for the third-encoding recipe

## Conventions

All AST and IR memory is allocated from an Arena in the Job and freed wholesale on error or completion. The StrBuf (string buffer) accumulates generated C code. Error handling uses longjmp to ctx.jb. The pipeline is single-pass: each stage hands off computed IR to the next.

Maintenance: update this file when subdirectories are added/removed or roles change.
