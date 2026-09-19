# src — internal compiler implementation

The compilation pipeline: pattern → parser (parse/) → AST → NFA → priority DFA (ir/) → optimization passes (opt/) → C codegen (gen/). Core utilities and shared data structures in core/; pipeline driver is pcrec_compile() in core/compile.c.

## The layer order

```
lib → core(base) → enc → parse → ir → opt → gen → driver → dump → cli
```

A file may depend on anything to its LEFT. `tools/review/include_graph.py`
is the instrument, and this is the order it tests
(`tools/review/out/include_backedges.tsv`, 0 rows).

**`core/` is two layers wearing one name, and the order above says so.**
The BASE tier is `arena.c`, `sb.c`, `cpset.c`, `fold.c`, `tune.c` and the
type definitions in `internal.h`: everything depends on it and it depends
on nothing. `compile.c` is the DRIVER, and a driver by definition sits
above every stage it drives — its calls into `gen/` are the pipeline
working, not a layering breach, and reading them as breaches is what the
old six-layer model did. [REVW.3] wave 3 fixed the MODEL and deliberately
did not move the file (ruling M4, D77): `include_graph.py` carries a
per-file tier override table for it, with its reasoning at the table.

**The driver tier's own residue, measured and named** (an `nm -g`/`nm -u`
join over the built objects, 2026-09-19): `compile.c` also defines
`ctx_fail`, `ctx_nomem` and `pcrec_default_options`, which every layer
calls — 22 call edges that the `driver` classification turns into
back-edges pointing the other way. They are base-tier primitives living
in a driver's file. Nothing is proposed for them here; the number is
recorded so a later wave knows the residue is a FILE that is two layers,
not a model that is still wrong.

**What the include graph cannot see.** It measures includes, and
`core/internal.h` declares nearly everything while 52 of ~55 `.c` files
include it, so a cross-layer CALL usually generates no cross-layer
INCLUDE. The call-level census is 30 back-edges where the include graph
reads 0. A clean `include_backedges.tsv` is a statement about includes.

## Files

- **core/** — pipeline driver, arena allocator, string buffer, shared type definitions
- **enc/** — [M5-SEAM] the ENCODING BACKENDS (D58, DD-12): the
  per-encoding residual block each artifact embeds, one file per encoding
  behind one registry. The compiler and the emitter carry NO encoding
  conditionals; the only switch is which backend's text was embedded.
  `src/gen/enc/` until [REVW.3] wave 3 moved it to its derived position, a
  layer between `core` and `parse`: the seam was chartered emission-only
  and four later seam events gave `PcrecEnc` DATA fields that parse and ir
  read, so every include back-edge in the tree was a lower layer reaching
  up into `gen` for something that is not emission. See enc/CLAUDE.md for
  the third-encoding recipe
- **parse/** — base-tier PCRE parser with module lookup hooks
- **ir/** — NFA construction and priority subset construction (DFA)
- **opt/** — IR/DFA optimization passes (APPROACH §5): minimization; and,
  since [M6.4.2], `atomic.c` — the free discharge, which is not an
  optimisation at all: it deletes cuts a proof shows are no-ops, which changes
  which ENGINE a pattern gets and never which strings it matches
- **gen/** — DFA to gcc-dialect C code emission
- **dump/** — [REVW.3] wave 3: the REGISTRY DUMP TIER, the CLI's read-only
  table surfaces (`--list-syntax`/`--list-families`/`--list-definitions`/
  `--list-axes`/`--list-limits`/`--list-schema` and their query siblings).
  Moved out of `parse/`, where four files that RENDER the parse, core and
  gen tiers' own tables were filed as parser code. `cli/` is their only
  caller and no `src/` object names their symbols. See dump/CLAUDE.md

## Conventions

All AST and IR memory is allocated from an Arena in the Job and freed wholesale on error or completion. The StrBuf (string buffer) accumulates generated C code. Error handling uses longjmp to ctx.jb. The pipeline is single-pass: each stage hands off computed IR to the next.

Maintenance: update this file when subdirectories are added/removed or roles change.
