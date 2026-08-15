# src/ir — NFA construction and DFA compilation

Intermediate representation: AST → priority Thompson NFA (nfa.c) → DFA via priority subset construction (dfa.c). Priority ordering on NFA split edges encodes greedy/lazy and alternation preference; subset construction yields a leftmost-first DFA with accept-pruning giving PCRE leftmost-first semantics.

## Files

- **nfa.c** — Thompson NFA construction from AST; **[M4.5b]: `A_CAP` is
  INVISIBLE here** (`ast_bare`, applied at compile_ast's entry, at trie_key's
  spine head and leaves, and at both spine flattenings). That is load-bearing
  twice over: it re-applies D31's erasure so the machine built for `(a|b)+c`
  is state-for-state the machine built for `(?:a|b)+c` (engine_m4.md §6.1's
  STRUCTURAL half, and the reason §5.4's byte-identity gate holds), and
  missing one call site would not miscompile — compile_ast's own entry deref
  is the backstop — but WOULD perturb trie ELIGIBILITY, surfacing as a gate
  failure rather than a wrong answer. Otherwise: split edge order encodes choice preference (D3). Can compile the pattern REVERSED (concat order flipped) for the D7 reverse machine; nfa_wrap_unanchored() adds the lowest-priority start self-loop for one-pass unanchored search; iterative CAT/ALT spine flattening (R1 R-2). M2.8 adds a priority-preserving prefix TRIE for flat alternations (trie_build/trie_key), with two soundness guards documented in D9 — index-range partitioning around a branch that ends mid-trie, and a pairwise-disjointness test before reordering groups. In reverse mode the per-branch key is reversed, so it factors common SUFFIXES. The whole factoring path has a compile-time off switch, `-DPCREC_NO_TRIE` (TRIE_ENABLED), which exists solely so tests/codegen/run_trie_identity.sh can build a reference compiler and diff emitted C against it — the trie must be output-preserving, and that diff is a far stronger soundness net than subject sampling. It is never defined in a shipped build, and the shipped object's code sections are byte-identical with the switch present
- **dfa.c** — priority subset construction with byte equivalence classes; `prune` on for forward machines (leftmost-first accept-pruning), off for the reverse machine (must keep all threads to find the earliest match start); EOL-variant states for `$` (R1 S-C1/S-C2); per-engine state caps grounded in emitter cost (R1 A-3). Closure visit marks are generation-stamped rather than memset per call, and clo_visit's tail edges are explicit loop iterations so recursion depth no longer depends on gcc's tail-call optimisation (D10). PCRE's empty-iteration rule lives in clo_visit: an ε re-arrival at a loop entry means the iteration consumed nothing, so the closure follows the loop's EXIT edge at that priority position. It is **not** a one-shot — K17 (2026-08-14) was exactly the one-shot being spent by an inner star before an outer one needed it, and removing it is safe because the redirect graph (loop entry → its continuation) points only outward and is therefore acyclic. **The `seen` memo here is global per closure while the empty-iteration rule is path-dependent, and that gap is a live bug (K18): a redirect that has to be reached THROUGH an already-seen non-loop ε state is still lost. Read known_issues.md K17 and K18 together before touching this function**

## Conventions

NFA states are indexed in a flat array; split edges are encoded as `state*2 + slot` (slot 0 = preferred branch, 1 = alternate). Epsilon closure respects split order and prunes lower-priority threads on first ACCEPT. Byte equivalence classes are computed first so DFA transition tables are ncls-wide instead of 256-wide.

Maintenance: update this file when files are added/removed or their roles change.
