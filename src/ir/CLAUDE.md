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
  failure rather than a wrong answer. **[M4.7b/K7]: the `X{m,n}` tail loop INHERITS its
  accumulated out-patch array rather than copying it** (`Frag w = { s,
  cat.out };`) — the copy made NFA construction Theta((n-m)^2) in arena
  traffic while the state count stayed linear, which is exactly why
  `PCREC_MAX_NFA_STATES` never had anything to object to and `a{0,65535}` was
  SIGKILLed instead of refused. It is safe because a Patch is an unordered SET
  (`patch_to` writes one target into every entry and reads nothing about
  order) and `nst` is called in the same places, so the NFA is bit-identical —
  verified byte-for-byte on 572 corpus artifacts. `frag_cat2` already used
  this idiom; that loop was the one site that had not. Otherwise: split edge order encodes choice preference (D3). Can compile the pattern REVERSED (concat order flipped) for the D7 reverse machine; nfa_wrap_unanchored() adds the lowest-priority start self-loop for one-pass unanchored search; iterative CAT/ALT spine flattening (R1 R-2). M2.8 adds a priority-preserving prefix TRIE for flat alternations (trie_build/trie_key), with two soundness guards documented in D9 — index-range partitioning around a branch that ends mid-trie, and a pairwise-disjointness test before reordering groups. In reverse mode the per-branch key is reversed, so it factors common SUFFIXES. The whole factoring path has a compile-time off switch, `-DPCREC_NO_TRIE` (TRIE_ENABLED), which exists solely so tests/codegen/run_trie_identity.sh can build a reference compiler and diff emitted C against it — the trie must be output-preserving, and that diff is a far stronger soundness net than subject sampling. It is never defined in a shipped build, and the shipped object's code sections are byte-identical with the switch present
- **dfa.c** — priority subset construction with byte equivalence classes; `prune` on for forward machines (leftmost-first accept-pruning), off for the reverse machine (must keep all threads to find the earliest match start); EOL-variant states for `$` (R1 S-C1/S-C2); per-engine state caps grounded in emitter cost (R1 A-3), **plus [M4.7b]'s
  `PCREC_MAX_SUBSET_ELEMS` charged in `intern()` as each state's list is
  interned** — the state caps bound how many states exist, this bounds what
  they COST, and on the exact-repeat family those are different numbers by a
  factor of n. `tab_grow` and the two reallocs here now fail through
  `ctx_nomem` rather than `abort`. **[M6.2 wave A] A THIRD CLOSURE VIEW**, `end_ok`, for `\z` (N_END): true
  only at `pos == n`, where `eol_ok` is true at `n` AND before a final
  newline. `make_state` computes three closures and interns up to two
  variants, and the CANONICALIZATION REFERENCE is the one thing to get right —
  `endvar` is interned iff it differs from the **EOL view**, not from the
  base. Against the base instead, every eol-differing state of every
  `$`-bearing pattern interns a redundant live `endvar`, the emitted artifact
  stops being byte-identical, and no answer changes anywhere (that was the
  design's own first draft, R30 E3). `-DPCREC_NO_ENDVAR` compiles the
  interning out and exists for one consumer,
  `tests/codegen/run_endvar_identity.sh`, exactly as `-DPCREC_NO_TRIE` exists
  for `run_trie_identity.sh`; never defined in a shipped build.
  **[M6.2 wave B] A FOURTH AXIS, and it is NOT a position view.** `\b`/`\B`
  (N_WORDB/N_NWORDB) read the two BYTES around a position rather than the
  position itself, so the closure takes two more bits — `cons_word` (the byte
  already consumed, fixed per state, read off the class of the transition that
  built it) and `up_word` (the byte about to be consumed, a per-class
  PARAMETER). The test is SYMMETRIC in them, which is the whole reason one
  closure serves the forward and the reverse machine with no notion of
  direction anywhere in this file. Three consequences, each of which is the
  thing to understand before editing:
  (a) **`eqclasses` refines the alphabet by `pcrec_cls_word_esc`** when the
  machine carries a word assertion, so both bits are constant inside a class.
  ONE SPELLING of the word set, shared with `\w` (assertions_design.md §7.2
  item 3); there is no second copy anywhere and a structural check says so.
  (b) **The word view is a SECOND LIST on the state (`DState.wlist`), not a
  second interned state.** `eolvar`/`endvar` are POSITION views — two
  positions out of n, so a per-state indirection costs nothing. The word view
  is a CLASS view, decided at every position by a class the transition lookup
  already has in a register, so it is BAKED INTO `tr[]`: the row for class `c`
  is built from the closure `cls_is_word(c)` selects. What is left over is the
  accept bit alone, which is why §3.6's class-indexed accept table exists and
  nothing else does.
  (c) **The "previous byte was a word character" bit is NOT a field.** Two
  pre-sets reached under different contexts close differently wherever the
  context is live, so they intern APART; where it is not live they intern
  TOGETHER, and that merge is why §3.5's measured ratio is 1.10x median rather
  than the theoretical 2x. A field would have to forbid it.
  Mechanism 4 (§3.8) adds `Dfa.s1w`, the interior start state for a WORD
  context — `s1` is the non-word one and `s0` covers "no context byte exists",
  which is a non-word context and needs no twin.
  `-DPCREC_NO_WORDCTX` pins `has_word` false for
  `tests/codegen/run_wordctx_identity.sh`, the same shape as the two knobs
  above; under it a `\b` pattern compiles to something WRONG, which is what
  makes that script's positive control non-vacuous.
  Closure visit marks are generation-stamped rather than memset per call (D10). PCRE's empty-iteration rule lives in the closure walk: an ε re-arrival at a loop entry means the iteration consumed nothing, so the closure follows the loop's EXIT edge at that priority position, and it is **not** a one-shot (K17, 2026-08-14). **The closure is PATH-SENSITIVE as of K18's fix (2026-08-15): the memo is keyed on (state, OPEN-LOOP CONTEXT) and the redirect fires on "this loop is OPEN on my path", not on "this state has been seen somewhere in this closure" — the two are the same predicate only when a closure's walk is a single path, and it is a DFS over a branching ε graph.** A context is an interned IMMUTABLE chain (ctx 0 = the empty open-loop stack; every other ctx is (parent, loop entry)), which is the open-loop stack's only representation — carrying it costs one int, and the design's hardest prototype bug (a frame restoring the stack's depth but not its entries, silently losing redirects) is not expressible in it. Three things to know before editing `clo_walk`: the ctx-0 FAST PATH (the pre-K18 per-state stamp array) carries nearly all traffic and removing it costs 7x on a real pattern for byte-identical work; the walk has **no recursion at all** — a split pushes its deferred branch onto an explicit LIFO, because keying on the context makes a recursive descent Θ(d²) deep (31,377 frames at the parser's 250-paren cap, an asan stack overflow at depth 210); and both of the design's invariants ship as live `DFA_INVARIANT` aborts, neither covering the other. Read `docs/design/k18_memo_design.md` §2a/§3 and known_issues.md K17+K18 together before touching this function; the guards are `tests/base/k18_*.rxt`

## Conventions

NFA states are indexed in a flat array; split edges are encoded as `state*2 + slot` (slot 0 = preferred branch, 1 = alternate). Epsilon closure respects split order and prunes lower-priority threads on first ACCEPT. Byte equivalence classes are computed first so DFA transition tables are ncls-wide instead of 256-wide.

Maintenance: update this file when files are added/removed or their roles change.
