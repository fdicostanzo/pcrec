# src/opt — algorithmic optimization passes

Transformations pcrec must do because gcc cannot (APPROACH §5): they change
the algorithm, not the instruction selection. Passes run between DFA
construction (src/ir) and emission (src/gen).

## Files

- **minimize.c** — DFA minimization by Moore-style partition refinement with
  signature hashing. The EOL-view edge (`eolvar`) participates as an extra
  alphabet symbol so `$`-machines minimize correctly. Behavior-preserving:
  priority/leftmost-first semantics are already baked into the transition
  structure before this runs. Shrinks emitted tables (code size + cache).

## Conventions

A pass takes (Ctx *, Dfa *) or (Ctx *, Nfa *), mutates in place, and must be
behavior-preserving — every pass needs corpus coverage that would catch a
semantic change (the full suite runs against post-pass output). Scan-avoidance
analyses that only inform codegen (prefilters, skip states) live in the
emitter instead; move one here if it grows its own IR transformation.

Maintenance: update this file when passes are added/removed.
