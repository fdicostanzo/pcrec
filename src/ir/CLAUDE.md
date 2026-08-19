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
  Mechanism 4 (§3.8) adds the interior start states — one per class-axis
  context of the byte the walk has already passed (`Dfa.s1u[]`, `Dfa.s1w` in
  wave B's spelling) — while `s0` covers "no context byte exists", which is
  neither a word character nor a newline and needs no twins.
  `-DPCREC_NO_WORDCTX` pins `has_word` false for
  `tests/codegen/run_wordctx_identity.sh`, the same shape as the two knobs
  above; under it a `\b` pattern compiles to something WRONG, which is what
  makes that script's positive control non-vacuous.
  **[M6.2 wave C] `(?m)` ADDS NO NEW MACHINERY — it adds a second PROPERTY to
  the two axes wave B built**, which is why this file's diff for it is small
  and its *structure* changed anyway. `(?m)$` reads whether the byte to the
  RIGHT is a newline (the axis `\b`'s right-hand side uses) and `(?m)^`
  whether the byte to the LEFT is one (the axis `\b`'s left-hand side uses),
  so the class axis stops being a BOOL and becomes the three-valued `UPC_*`
  partition (`UPC_PLAIN`/`UPC_WORD`/`UPC_NL`, disjoint and exhaustive because
  a newline is not a word character). Consequences, each of which is a thing
  to know before editing:
  (a) `DState` carries `up[UPC_N]` — a `DView` per class context — where wave
  B carried `list`/`accept` plus `wlist`/`waccept`, and `Dfa.s1u[UPC_N]`
  where it carried `s1`/`s1w`. `make_state` interns from an array and shares
  storage between views whose closures coincide, so a machine with no class
  axis still allocates ONE list per state and charges K7's budget once.
  (b) **DIRECTION APPEARS IN EXACTLY ONE PLACE**, and wave B genuinely did not
  need it: `\b` is SYMMETRIC in its two operands, so a machine reading them
  backwards gets the same answer. `(?m)$` reads ONE side — forward it is the
  byte about to be consumed, reverse it is the one already consumed — so the
  closure names its operands by SIDE (`left_*`/`right_*`, i.e. `s[pos-1]` and
  `s[pos]`) and `make_state`'s `sides_of` is the single function that knows a
  machine has a direction. `pcrec_build_dfa` takes `reverse` explicitly rather
  than deriving it from `prune`; the two coincide today (D7) and a coincidence
  load-bearing for correctness is what this project keeps recording.
  (c) `(?m)$` MAKES `end_ok` LIVE — its "or end of subject" half is wave A's
  `pos == n` view — so a pure-`(?m)$` machine has `endvar >= 0` and
  `eolvar == -1` everywhere and reaches `emit_view_select`'s
  `has_end && !has_eol` arm, the branch wave A wrote for `\z`. A construct the
  design calls `$`'s sibling shares its emitted selector with `\z` and none
  with `$`.
  (d) **`(?m)^` IS NOT THE MIRROR OF `(?m)$`.** PCRE2's multiline `^` does not
  match after a newline that ENDS the string, so `N_BOT_M`'s newline half is
  guarded by `!end_ok`. The design (§3.7, §9.3) states it without that guard
  and python3 `re` implements it without it (U11b); pcrec shipped the design's
  rule in this lane and `tests/assertions/run_mline_diff.sh` caught it at
  `startpos > 0`.
  `-DPCREC_NO_MLINECTX` pins `has_nl` false for
  `tests/codegen/run_mlinectx_identity.sh`, the same shape as the three knobs
  above; under it a `(?m)$` pattern compiles to `\z`'s semantics, which is
  what makes that script's positive control non-vacuous.
  **[M6.2 wave C ends here; WAVE D adds a THIRD POSITION BIT and a SECOND
  START FAMILY, and NOTHING to the alphabet.** `\G` (N_GSTART) is an absolute
  position test like N_BOT — it reads no byte, refines no class, asks for no
  view — but against a value that is not known until the match call:
  `pos == startpos` where N_BOT is `pos == 0`. So `Clo` gains `gst_ok` beside
  `bot_ok`/`eol_ok`/`end_ok`, and `Dfa` gains `s1g[UPC_N]`, the SAME class-axis
  family as `s1u[]` closed with that bit SET. Three things to know:
  (a) **`s0` is closed with the bit TRUE and that is a derivation, not a
  convention**: an attempt loop runs `start` from `startpos` upward, so
  `start == 0` implies `startpos == 0` implies `start == startpos`. Clearing it
  there compiles and silently deletes every `\A\G`-shaped match at offset 0.
  (b) **Every WORKLIST successor is closed with the bit FALSE, unconditionally**
  — one transition means one byte consumed, so `pos > startpos` — and that
  single `false` is why mid-pattern `\G` (`a\Gb`) is unsatisfiable with no
  special case anywhere.
  (c) **NO INVARIANT ties `gst_ok` to any other bit**, unlike `end_ok => eol_ok`:
  all four combinations describe reachable positions, so it rides through
  `make_state` as a caller's parameter rather than becoming a fourth view.
  `has_gst` gates the extra closures for the same pay-only-when-it-differs
  reason `has_end` and `upc_live[]` do.
  **THIS WAVE'S REFERENCE KNOB IS NOT IN THIS FILE, and the absence is the
  finding**: `-DPCREC_NO_GSTART` lives at `src/gen/emit_dfa.c`'s three EMITTER
  decision points instead. A knob that shares a source with the code a sabotage
  edits CANCELS that sabotage in both builds — measured on wave B's own row,
  where `run_wordctx_identity.sh` stays 1135/1135 identical under S71. See
  `pcrec_build_dfa`'s comment and tests/mech/sabotages/S83.

  **[M6.2] WAVE E ADDS NOTHING TO THIS DIRECTORY, and that is a fact worth
  recording rather than an absence.** `\K` is the module's last construct and
  the only one with no DFA path: it reports a position that is a property of
  the winning PATH, and a subset state is a priority-ordered SET, which does
  not carry one (assertions_design.md §6.1 — closed by CHOICE rather than by
  mathematics; a tagged DFA would recover it and pcrec's is not one).
  `src/ir/nfa.c` lowers `A_KRESET` to **N_EPS**, so nothing here sees it at
  all — no bit, no view, no start family, no alphabet refinement.
  **The consequence is load-bearing and is why the arm is an epsilon rather
  than a refusal**: `\K` changes no LANGUAGE, so the capture-erased prefilter
  built for `a\Kb` is the machine `ab` builds, and its span start is the
  PRE-`\K` start by construction — exactly the quantity the hybrid may bound
  the VM's search with, and exactly the one §6.3 rule 1 forbids writing out.
  Closure visit marks are generation-stamped rather than memset per call (D10). PCRE's empty-iteration rule lives in the closure walk: an ε re-arrival at a loop entry means the iteration consumed nothing, so the closure follows the loop's EXIT edge at that priority position, and it is **not** a one-shot (K17, 2026-08-14). **The closure is PATH-SENSITIVE as of K18's fix (2026-08-15): the memo is keyed on (state, OPEN-LOOP CONTEXT) and the redirect fires on "this loop is OPEN on my path", not on "this state has been seen somewhere in this closure" — the two are the same predicate only when a closure's walk is a single path, and it is a DFS over a branching ε graph.** A context is an interned IMMUTABLE chain (ctx 0 = the empty open-loop stack; every other ctx is (parent, loop entry)), which is the open-loop stack's only representation — carrying it costs one int, and the design's hardest prototype bug (a frame restoring the stack's depth but not its entries, silently losing redirects) is not expressible in it. Three things to know before editing `clo_walk`: the ctx-0 FAST PATH (the pre-K18 per-state stamp array) carries nearly all traffic and removing it costs 7x on a real pattern for byte-identical work; the walk has **no recursion at all** — a split pushes its deferred branch onto an explicit LIFO, because keying on the context makes a recursive descent Θ(d²) deep (31,377 frames at the parser's 250-paren cap, an asan stack overflow at depth 210); and both of the design's invariants ship as live `DFA_INVARIANT` aborts, neither covering the other. Read `docs/design/k18_memo_design.md` §2a/§3 and known_issues.md K17+K18 together before touching this function; the guards are `tests/base/k18_*.rxt`

## Conventions

NFA states are indexed in a flat array; split edges are encoded as `state*2 + slot` (slot 0 = preferred branch, 1 = alternate). Epsilon closure respects split order and prunes lower-priority threads on first ACCEPT. Byte equivalence classes are computed first so DFA transition tables are ncls-wide instead of 256-wide.

Maintenance: update this file when files are added/removed or their roles change.
