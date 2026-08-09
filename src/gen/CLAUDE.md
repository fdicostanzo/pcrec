# src/gen — C code generation

Emits self-contained gcc-dialect C from the DFA machines. Two engines (D7):
ENG_UNANCH for patterns without `^` (including `$`-bearing ones since M2.7/D8) — table-driven O(n) forward scan
(leftmost-first match end) + reverse scan (match start), with a memchr/bitmap
start-state prefilter; ENG_ATTEMPT for `^` patterns — per-start computed-goto
attempt loop with EOL-variant states. Table emission exists because gcc compile
time on huge computed-goto functions is superlinear (R1 A-3). Generated code
has zero dependency on pcrec at build or run time.

`emit_unanchored` handles EOL and non-EOL machines in ONE function on purpose
(M2.12): M2.7 forked a second copy for `$` patterns, and that fork is how the
prefilter and skip loops silently went missing from the `$` path for an entire
milestone. Under EOL every skip is bounded at n-1 and scan avoidance runs
BEFORE the accept/EOL evaluation — see D11, and note the ordering rule is the
subtle half.

## The multi-engine naming surface (OS-0b)

One output file may eventually carry several engines, one per point of the
option product, behind a generated selector (D18/D20). Of the 15 identifiers
this emitter produces, 12 are FUNCTION-LOCAL statics, so two engines in two
functions cannot collide on them. Exactly two things are file-scope and both
have their own emitter:

- `emit_span_typedef` — ONCE PER FILE, shared by every engine in it. Emitting
  it per engine is not a benign redefinition: each occurrence declares a fresh
  anonymous struct type, so gcc rejects the file with `error: conflicting
  types for 'rx_span'` (verified, -std=gnu11 and -std=c99).
- `emit_search_decl` / `emit_search_head` — ONCE PER ENGINE, under that
  engine's own entry name, kept adjacent so the declaration and the definition
  cannot drift apart.

The entry name comes from `engine_entry_name()` and is read nowhere else, so a
finder can hand each engine a distinct name without any emitter learning that
options have a product. Today there is one engine per file and the name is
`<prefix>_search`. Both properties are enforced by the multi-engine block in
tests/codegen/run_codegen_tests.sh, which compiles a two-engine file.

## Files

- **emit_dfa.c** — both engine emitters (emit_unanchored, emit_attempt), the file-scope/per-engine naming helpers, shared table/label helpers, header/comment/prologue emission

## Conventions

The emitter produces a self-contained .c file (or paired .c/.h if options.header_name is set). Symbols are prefixed with the user's chosen identifier (default "rx"). Emitted code must stay warning-clean under -Wall -Wextra -Werror (the harness enforces this). Future encoding backends (UTF-8) and the VM engine emitter will coexist here as separate files.

Maintenance: update this file when files are added/removed or their roles change.
