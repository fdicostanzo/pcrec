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

## Files

- **emit_dfa.c** — both engine emitters (emit_unanchored, emit_attempt), shared table/label helpers, header/comment/prologue emission

## Conventions

The emitter produces a self-contained .c file (or paired .c/.h if options.header_name is set). Symbols are prefixed with the user's chosen identifier (default "rx"). Emitted code must stay warning-clean under -Wall -Wextra -Werror (the harness enforces this). Future encoding backends (UTF-8) and the VM engine emitter will coexist here as separate files.

Maintenance: update this file when files are added/removed or their roles change.
