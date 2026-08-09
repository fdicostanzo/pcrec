# src/ir — NFA construction and DFA compilation

Intermediate representation: AST → priority Thompson NFA (nfa.c) → DFA via priority subset construction (dfa.c). Priority ordering on NFA split edges encodes greedy/lazy and alternation preference; subset construction yields a leftmost-first DFA with accept-pruning giving PCRE leftmost-first semantics.

## Files

- **nfa.c** — Thompson NFA construction from AST; split edge order encodes choice preference (see docs/decisions.md D3)
- **dfa.c** — priority subset construction with byte equivalence classes; leftmost-first semantics and EOL assertions ($ accept flag)

## Conventions

NFA states are indexed in a flat array; split edges are encoded as `state*2 + slot` (slot 0 = preferred branch, 1 = alternate). Epsilon closure respects split order and prunes lower-priority threads on first ACCEPT. Byte equivalence classes are computed first so DFA transition tables are ncls-wide instead of 256-wide.

Maintenance: update this file when files are added/removed or their roles change.
