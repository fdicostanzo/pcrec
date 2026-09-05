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
  this idiom; that loop was the one site that had not. **[LIM-2] N1 (2026-09-04):
`nst`'s state-count check reads a raise-only per-compile override**
(`b->cx->opt->max_nfa_states`, 0 = `PCREC_MAX_NFA_STATES`) — the same
`cli/main.c` `raise_only_limits[]` table also raises `PCREC_MAX_DFA_STATES_
GOTO` and `PCREC_MAX_SUBSET_ELEMS`; see `lib/pcrec.h`'s comment on the four
new `pcrec_options` fields. Otherwise: split edge order encodes choice preference (D3). Can compile the pattern REVERSED (concat order flipped) for the D7 reverse machine; nfa_wrap_unanchored() adds the lowest-priority start self-loop for one-pass unanchored search; iterative CAT/ALT spine flattening (R1 R-2). M2.8 adds a priority-preserving prefix TRIE for flat alternations (trie_build/trie_key), with two soundness guards documented in D9 — index-range partitioning around a branch that ends mid-trie, and a pairwise-disjointness test before reordering groups. In reverse mode the per-branch key is reversed, so it factors common SUFFIXES. The whole factoring path has a compile-time off switch, `-DPCREC_NO_TRIE` (TRIE_ENABLED), which exists solely so tests/codegen/run_trie_identity.sh can build a reference compiler and diff emitted C against it — the trie must be output-preserving, and that diff is a far stronger soundness net than subject sampling. It is never defined in a shipped build, and the shipped object's code sections are byte-identical with the switch present
- **dfa.c** — priority subset construction with byte equivalence classes; `prune` on for forward machines (leftmost-first accept-pruning), off for the reverse machine (must keep all threads to find the earliest match start);
  **[ENG-ABS] (2026-08-29) `pcrec_build_dfa` TAKES ITS ROOT AND ITS
  OPTIONALITY AS PARAMETERS, and neither is a special case.** `root` used to be
  `nfa->start` implicitly — the state `nfa_wrap_unanchored` installs. The
  anchored MATCH-HERE machine
  (`docs/design/anchored_match_unwrapped.md`) is this SAME construction rooted
  at `nfa->anch_start` instead, i.e. the pattern's own first state, which the
  wrap deliberately leaves addressable; every call site now STATES its root, and
  nothing in this file knows the difference. `optional` is read at exactly one
  place — `intern`'s two "pattern too complex" sites, where an optional machine
  RECORDS the overflow on `Dfa.overflowed` and returns `PCREC_DFA_DEAD` instead
  of `ctx_fail`ing, leaving `[SEL-1]`'s record and both diagnostics
  character-for-character unchanged. That one line is what makes an optional
  machine's cap overflow a SELECTION OUTCOME rather than a refusal, and it is
  why a pattern that compiles today cannot start failing because a machine
  nothing needs did not fit. The worklist loop returns on `d->overflowed`; EOL-variant states for `$` (R1 S-C1/S-C2); per-engine state caps grounded in emitter cost (R1 A-3), **plus [M4.7b]'s
  `PCREC_MAX_SUBSET_ELEMS` charged in `intern()` as each state's list is
  interned** — the state caps bound how many states exist, this bounds what
  they COST, and on the exact-repeat family those are different numbers by a
  factor of n. `tab_grow` and the two reallocs here now fail through
  `ctx_nomem` rather than `abort`. **[SEL-1] (2026-08-28) THE TWO "pattern
  too complex" `ctx_fail` SITES** (the state-count check in `intern()`, the
  `PCREC_MAX_SUBSET_ELEMS` check beside it) **ALSO RECORD THE OVERFLOW ON
  `Ctx`** (`dfa_overflowed`/`dfa_overflow_why`, plain fields, set
  unconditionally right before the unchanged `ctx_fail` call) — the general
  mechanism `auto`'s DFA-cap-overflow contract needs (plan row [SEL-1],
  `src/opt/select_engine.c`'s `forces_dfa_overflow`, `src/core/compile.c`'s
  retry): the build reports "over budget" as a RESULT a later pass consumes,
  never a special case at this site itself — the diagnostic text and the
  `ctx_fail` call are byte-for-byte what they were before this row.
  **[LIM-2] N1 (2026-09-04) A THIRD SITE, checking a SMALLER threshold
  FIRST.** Right before the `PCREC_MAX_SUBSET_ELEMS` check, `intern()` now
  asks whether `!d->optional && cx->opt->engine == PCREC_ENGINE_AUTO &&
  cx->subset_elems > PCREC_MAX_AUTO_DFA_ELEMS` — the SAME counter, a
  SMALLER auto-only budget, joining the identical `dfa_overflowed`/
  `dfa_overflow_why` recording shape (a fourth field, `Ctx.dfa_overflow_
  is_budget`, marks WHICH site fired, read only by `compile_driver`'s
  stderr note). `!d->optional` excludes [ENG-ABS]'s anchored third
  machine (its overflow never refuses regardless); the AUTO conjunct
  excludes an explicit `--engine=dfa` request, which pays the full cap
  below in full. The default (30,000,000) is derived, not chosen —
  docs/dev/lanes/n1budget_report.md's corpus+bench sweep found the worst
  currently-compiling artifact's spend at 24,050,003 elements
  (`tests/counterk/counterk.rxt:1845`). Gate: `tests/codegen/
  run_n1_budget.sh`, a `-DPCREC_MAX_AUTO_DFA_ELEMS`-lowered reference
  compiler (this row's OWN raise-only default is BUILD_D, `[ART-SIZE]`'s
  own two-lever shape, since the natural population at the shipped
  default is zero and the CLI override can only raise it).
  **[M6.2
  wave A] A THIRD CLOSURE VIEW**, `end_ok`, for `\z` (N_END): true
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
  `-DPCREC_NO_WORDCTX` compiles the axis out for
  `tests/codegen/run_wordctx_identity.sh`, the same shape as the two knobs
  above; under it a `\b` pattern compiles to something WRONG, which is what
  makes that script's positive control non-vacuous. **[M6.2 repair slice,
  2026-08-19] IT NO LONGER PINS THE FLAG** — see `eqclasses` and the file
  header for why the placement is the whole point.
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
  `-DPCREC_NO_MLINECTX` compiles the newline half out for
  `tests/codegen/run_mlinectx_identity.sh`, the same shape as the three knobs
  above; under it a `(?m)$` pattern compiles to `\z`'s semantics, which is
  what makes that script's positive control non-vacuous. **[M6.2 repair
  slice, 2026-08-19] IT NO LONGER PINS THE FLAG**, for S71's reason one wave
  over.
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
  where `run_wordctx_identity.sh` stayed 1135/1135 identical under S71. See
  `pcrec_build_dfa`'s comment and tests/mech/sabotages/S83.
  **[M6.2 REPAIR SLICE, 2026-08-19] THE OTHER THREE KNOBS WERE RE-PLACED ON
  THAT FINDING, and the re-placement is NOT simply "move them to the
  emitter".** `\G` could live wholly at the emitter because it refines no
  alphabet and interns no state the emitter cannot neutralize. `\b` and
  `(?m)` refine the ALPHABET and `\z` interns a STATE, so an emitter branch
  cannot undo either and an emitter-only knob was MEASURED to leave S71 at
  1186/1186 identical — the same blindness in a new place. What each knob
  gets instead is a `#ifndef` around the ANALYSIS'S ACTION (the refinement in
  `eqclasses`, the interning in `make_state`) plus a pin in front of the
  flag's consumers, AND an emitter half for the sites where the emitted text
  is what the construct decides. Measured after, all three red on their own
  gates through BYTES: S71 1178 of 1186 differing, S76 1117 of 1201, S69
  failing `endvaridentity` — each with its corpus arm green.
  `-DPCREC_NO_ENDVAR` was already at its action and did not move.

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
  **[M6.5.2] ADDS ONE ARM AND IT IS THE OPPOSITE OF `\K`'s.** `A_BREF` has
  NO MACHINE — a backreference is not regular — and `compile_ast` falls into
  its internal error DELIBERATELY rather than approximating. Two
  approximations exist and both are refused HERE rather than in a comment:
  erasing the reference to epsilon is a SUBSET (it deletes real matches, the
  one failure class D26 refuses outright), and replacing it with a copy of the
  referenced group's machine is APPROACH §2's erasure, which is not even a
  SUPERSET once that group's transitive closure holds an assertion or an
  atomic/possessive operator — MEASURED at 12 of 18 positive-control cells
  across the two reasons, plus 3 of 5 for the transitive one. Even where it IS
  a superset its leftmost SPAN differs from the true one on a large fraction
  of subjects, so it cannot serve as `engine_m4.md` §6.1's exact anchored
  window either.

  **Nothing builds that machine, and that is ENFORCED UPSTREAM rather than
  assumed**: `src/opt/select_engine.c` forces `EngineFit.prefilter` OFF for a
  backref-bearing pattern and REFUSES `-fprefilter` on one by name, and the
  pattern is VM-forced by its rows' stamps, so `src/core/compile.c`'s build
  condition (`chosen == ENGM_DFA || fit.prefilter`) is false. Reaching the arm
  means one of those two facts stopped being true — which is exactly when a
  loud internal error is worth more than a machine that answers for a
  different language. Contrast `\K` above: an epsilon there is right BECAUSE
  the construct changes no language; a backreference changes it, so there is
  no honest epsilon.

  **[M6.6.2] `A_LOOK` IS A THIRD ANSWER, AND IT IS NEITHER OF THOSE TWO.**
  `compile_ast` lowers a lookaround to `N_EPS`, body and all — and unlike
  `\K`'s epsilon that is NOT exact. Erasing a lookaround throws away a filter,
  so the machine built here recognises a strict SUPERSET of the pattern's
  language. That is the design (`lookaround_design.md` §5.2/§5.3) and it rests
  on a one-line proof: a lookaround consumes nothing, so every position where P
  matches is a position where erase(P) matches, i.e. L(P) is a subset of
  L(erase(P)) EVERYWHERE. A superset prefilter is sound for REJECTION and for
  the span START and NOT for the span END — the identical hazard an atomic
  group has, measured for that construct at 114 cells of silent match loss —
  which is why `pcrec_has_lookaround` exists to switch the MRL window ceiling
  off (§5.6). So the three arms are three different claims: `\K` erases
  EXACTLY, a backreference cannot be erased at all, and a lookaround erases to
  a SOUND SUPERSET whose looseness is paid for elsewhere. The general DFA
  construction — product construction with each body's recognizer — is
  chartered as `[ENG-LOOK]` and §5.7 records Frank's ruling that no
  one-character fold ships in the meantime.

  **[DD-14] `A_CALL` IS A FOURTH ANSWER, AND IT IS `A_BREF`'s WITH A REASON
  THAT WILL EXPIRE.** `compile_ast` falls to the loud `ctx_fail` for a
  subroutine call, exactly as it does for a backreference — but NOT because a
  call is as hopeless. A call to a NON-RECURSIVE callee has an exact finite
  lowering (splice the callee's machine in); a call in a CYCLE does not, since
  that is a context-free language and this is a finite automaton, and
  `subroutines_design.md` §8.2 measured that the two available approximations
  are the two `A_BREF`'s arm already refuses — erasure to epsilon is a SUBSET
  (it deletes real matches, D26's one outright-refused failure class) and a
  depth-bounded unrolling is neither subset nor superset. Nothing builds the
  machine: every `recursion` row is VM_ONLY and wave E forces
  `EngineFit.prefilter` off, so `src/core/compile.c`'s build condition is
  false. **WAVE G IS WHERE THIS ARM CHANGES** and it is the one site in the
  module where following the call graph is the POINT rather than a hang:
  §8.3's approximation, restored only for SPLICEABLE (acyclic) calls, against
  the 21x-350x prefilter loss §8.3 measured.

  Closure visit marks are generation-stamped rather than memset per call (D10). PCRE's empty-iteration rule lives in the closure walk: an ε re-arrival at a loop entry means the iteration consumed nothing, so the closure follows the loop's EXIT edge at that priority position, and it is **not** a one-shot (K17, 2026-08-14). **The closure is PATH-SENSITIVE as of K18's fix (2026-08-15): the memo is keyed on (state, OPEN-LOOP CONTEXT) and the redirect fires on "this loop is OPEN on my path", not on "this state has been seen somewhere in this closure" — the two are the same predicate only when a closure's walk is a single path, and it is a DFS over a branching ε graph.** A context is an interned IMMUTABLE chain (ctx 0 = the empty open-loop stack; every other ctx is (parent, loop entry)), which is the open-loop stack's only representation — carrying it costs one int, and the design's hardest prototype bug (a frame restoring the stack's depth but not its entries, silently losing redirects) is not expressible in it. Three things to know before editing `clo_walk`: the ctx-0 FAST PATH (the pre-K18 per-state stamp array) carries nearly all traffic and removing it costs 7x on a real pattern for byte-identical work; the walk has **no recursion at all** — a split pushes its deferred branch onto an explicit LIFO, because keying on the context makes a recursive descent Θ(d²) deep (31,377 frames at the parser's 250-paren cap, an asan stack overflow at depth 210); and both of the design's invariants ship as live `DFA_INVARIANT` aborts, neither covering the other. Read `docs/design/k18_memo_design.md` §2a/§3 and known_issues.md K17+K18 together before touching this function; the guards are `tests/base/k18_*.rxt`

## Conventions

NFA states are indexed in a flat array; split edges are encoded as `state*2 + slot` (slot 0 = preferred branch, 1 = alternate). Epsilon closure respects split order and prunes lower-priority threads on first ACCEPT. Byte equivalence classes are computed first so DFA transition tables are ncls-wide instead of 256-wide.

## [DD-14 wave G] `compile_ast`'s `A_CALL` arm, and the one back edge it follows

`nfa.c`'s `A_CALL` arm INLINES a `CALL_SPLICE` callee's fragment. It is EXACT,
not design §8.3's "sound approximation": the only thing lost is the CAPTURE, and
`ast_bare` already erases every `A_CAP` in the tree — so `(?&atom)` and the body
it names build the IDENTICAL machine, which is what makes the RFC 5322
specimen's factored artifact the hand-inlined one's.

**IT FOLLOWS `Ast.u.call.body`, WHICH IS THE AST'S ONE BACK EDGE**, and it is
safe to follow ONLY because a `CALL_SPLICE` callee is not in a cycle (design
§6.3 condition 1), making the descent a DAG bounded by the call-target count.
This file's header says "remaining recursion depth is bounded by the parser's
group-nesting cap"; **wave G is what made that sentence stop being true on its
own**, because a call edge is not a nesting edge. `NB.splice_depth` is the
counter that restores it, and it is load-bearing rather than defensive: sabotage
row S175 (eligibility admits a cycle) SEGFAULTED here, in `compile_ast` and not
in the emitter, before the counter existed — and a stack overflow is the one
failure a sabotage matrix cannot tell from an infrastructure fault.

**§8.3's `Sigma*` ARM IS DELIBERATELY NOT BUILT.** `src/opt/select_engine.c`
narrows both consumers to `pcrec_has_linked_call`, so a pattern with a LINKED
call gets neither engine's machine and nothing would consume the superset. A
LINKED call reaching this builder is a hard internal error. The consequence is
measured rather than argued: the spliced prefilter has NO superset window-end
exposure at all, and
`docs/design/subroutines_measurements/probes/probe_call_prefilter_hazard.py`
reports H1/H2/H3 all zero over 280 cells beside a control column that violates
22 times on the same cells.

Maintenance: update this file when files are added/removed or their roles change.
