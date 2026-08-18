# src/opt — algorithmic optimization passes

Transformations pcrec must do because gcc cannot (APPROACH §5): they change
the algorithm, not the instruction selection. Passes run between DFA
construction (src/ir) and emission (src/gen).

## Files

- **altcls.c** — [OPT-ALTCLS] ALTERNATION -> CLASS NORMALIZATION
  (docs/dev/plan.md's [OPT-ALTCLS] row). The FIRST pass in the pipeline —
  `pcrec_altcls` runs immediately after parse, before `pcrec_select_engine`
  and everything it drives (possessify/revdet/mrl, both machine builds, both
  emitters), which is why this pass is declared in internal.h ahead of
  `pcrec_select_engine` rather than grouped with the ENG-BREP passes below.

  TWO STAGES, both AST-to-AST REWRITES (unlike possessify.c/revdet.c's
  in-place annotation, this pass changes tree SHAPE and returns a possibly-
  new root, the same shape select_engine.c's `discharge` hook uses). Stage 1
  merges a maximal ADJACENT run of A_ALT branches that are each a bare
  A_CLASS (parse.c already normalizes every literal to a singleton class)
  into ONE class holding the union — `b|c` -> `[bc]`. Stage 2 runs on stage
  1's output and factors a maximal ADJACENT run of branches sharing a
  literal first byte into `byte + (?:remainder)` — `frank|fred` ->
  `fr(?:ank|ed)` — recursively, via an ITERATIVE prefix-extension loop
  (D10/DD-10/K20: prefix LENGTH is pattern-shaped) plus recursion bounded by
  SPLIT depth only (`PCREC_MAX_ALTCLS_FACTOR_DEPTH`, core/limits.h;
  branch-count-shaped, always safe to decline past the cap). NO CAPTURING
  GROUPS are ever introduced — the file allocates A_CLASS/A_CAT/A_ALT/A_EMPTY
  nodes only — which is what discharges the plan row's "must emit
  non-capturing groups or it changes the group count" obligation BY
  CONSTRUCTION rather than by a runtime check.

  D46: both stages are independently gated (`PCREC_NO_ALTCLS_MERGE`/
  `PCREC_NO_ALTCLS_FACTOR`, lib/pcrec.h — DENY-only, the original
  per-selection-point family's shape, not the prefilter's force pair) and
  independently stamped (`<PREFIX>_ALTCLS_MERGES`/`<PREFIX>_ALTCLS_FACTORED`,
  src/gen/emit_dfa.c's shared `pcrec_emit_prologue` — this pass runs before
  either engine exists, so unlike possessify/revdet/prefilter's VM-only
  stamps this one is common to both emitters).

  Full soundness argument, the generalization-ladder boundary (why stage 2
  is prefix factoring rather than a wider multi-char class merge — that is
  UNSOUND, `frank|fred` -> `fr[ae][nd]k?` accepts cross-products it must
  not), and the recursion-discipline reasoning are all in the file's own
  header. Tests: tests/altcls/. Sabotage: tests/mech/sabotages/ (S66/S67).

- **select_engine.c** — per-pattern ENGINE selection ([M4.5b],
  docs/design/engine_m4.md §5.1). Not a transformation like the pass below:
  it answers which engine compiles this pattern, and it exists as a pass
  rather than as compile.c's old inline `if` because of what its future
  customers are. The backrefs-finite expansion and the atomic/possessive cut
  are not analyses that RETURN a verdict, they are REWRITES that DISCHARGE
  one — `(abc)\1` is VM-forced until the expansion turns it into `abcabc`, at
  which point it is DFA-compilable. So the socket carries an optional
  `discharge` hook and the pass is a FIXPOINT with a bound, shipped with zero
  hooks registered (§5.2's own instruction: the bound exists from day one so a
  later rewrite pair cannot loop).

  The one analysis registered, `forces_captures`, triggers on the requested
  OUTPUT rather than the presence of a `(`: `a(b|c)+d` under `--no-captures`
  is capture-free WORK and stays on the DFA forever. Every `VM_ONLY` registry
  row is gated by a module with no producer, so the parser refuses those
  patterns long before selection runs — which is also why SR-8's flip is
  smaller than its row implies (§9.1: zero currently-refused constructs become
  compilable when the VM exists).

  **[M4.7a] SR-8 ITSELF: the consuming socket is deliberately NOT built
  here.** Zero producers means zero customers (D18/OS-0/D53's standing
  discipline against unpopulated machinery), and a hand-built `Ctx` proving
  a socket works is a control sharing a source with what it controls — it
  proves plumbing, not that a real producer's contract would look like the
  one guessed at sample size zero. Instead,
  `tests/registry/registry_check.c`'s `check_engine_capability_tripwire`
  asserts every `VM_ONLY`-masked `RS_MODULE` row has NO wired producer —
  the fact that makes engine-capability refusal unreachable today — so the
  day a module wires the first one, that check fails and names this file as
  the thing to build BEFORE the producer lands, not after.

  It also DRIVES possessify.c, and the placement is a reported deviation from
  §2.8's literal reading rather than a silent choice. §2.8 proposes
  possessification as an `EngineAnalysis` row whose `discharge` hook does the
  rewrite; the SHAPE claim is right and possessify.c keeps it, but the
  registration is not available. `discharge`'s contract is "rewrite so the
  ENGINE FORCING no longer applies", which possessification cannot do and must
  not claim to — a capture-bearing pattern still needs the VM afterwards — and
  the fixpoint only reaches `discharge` when the pattern is VM-FORCED, so
  registering there would possessify a capture-bearing pattern and SKIP a
  capture-free one built with `--engine=vm`: the same artifact kind, the same
  emitter, optimised differently for a reason invisible from outside. The
  driver is therefore the CHOSEN engine, which is the honest condition — see
  `run_possessify` and its comment.

  This file also owns the §5.6 override's REFUSALS, and it runs before machine
  construction so a caller who asked for an impossible combination pays no
  automaton for the diagnostic. The two refusal triggers are spelled
  differently on purpose (§9.2 item 2): a captures conflict names
  `--no-captures` as the way out, since the caller asked for captures merely by
  not passing it; a `VM_ONLY`-construct conflict names the construct. Only the
  first has a population today, and the second is empty BY POPULATION, not by
  omission.

  **[M4.6f] (2026-08-17):** the PREFILTER FORCE PAIR (D46's controllability
  half for `fit.prefilter`, §6.1/§4.7) is applied here, immediately after the
  derived value's own computation and in the same do-or-die posture the
  `--engine` switch above uses. `-fprefilter`/`-fno-prefilter`
  (`PCREC_FORCE_PREFILTER`/`PCREC_NO_PREFILTER`) override the derived
  boolean in EITHER direction — unlike the ladder's DENY-only family, because
  `fit.prefilter` is one verdict for the whole artifact rather than a
  per-quantifier step, so there is no addressing problem FORCE would create.
  Both flags together refuse (ambiguous request); `-fprefilter` additionally
  refuses whenever `fit.chosen != ENGM_VM` (no VM artifact exists to attach a
  prefilter to — reachable via explicit `--engine=dfa` or auto routing to the
  DFA because the pattern requests no captures). `-fno-prefilter` never
  refuses: `--engine=vm` already ships a pure, prefilter-free VM artifact
  today, so denying the hybrid is always buildable. The axis's D46
  observability half — `RX_VM_PREFILTER` — lives in src/gen/emit_vm.c, read
  from `job->fit.prefilter` directly rather than recomputed. Tests:
  tests/prefilter/.

- **possessify.c** — [ENG-BREP] POSSESSIFICATION
  (docs/design/eng_brep_design.md §2, D47.1: possessify-first in both the
  application order and the build order). Marks every `A_REP` for which no
  retreat into the loop can produce a match the PREFERRED path does not, so
  src/gen/emit_vm.c can emit it with no resume frames and no giveback.

  A REWRITE, not an analysis that returns a verdict (§2.8's shape claim): it
  does not observe that the loop needs no frames, it MAKES the quantifier one
  that needs none. It is monotone — it returns how many quantifiers it NEWLY
  marked, a marked quantifier is never unmarked — which is what lets
  select_engine.c drive it to a fixpoint in two rounds.

  **The rule is REPAIRED, and the obvious version of it is measured WRONG.**
  "FIRST(body) disjoint from FOLLOW(quantifier), body non-nullable" is the
  analysis as [ENG-BREP]'s own plan row stated it and it is UNSOUND: 117
  counterexamples, every one a body like `(a|ab)` whose iterations can end in
  two places. The body must ALSO admit a unique iteration — (U1)
  one-unambiguous and (U2) prefix-free on its position (Glushkov) automaton —
  and the disjointness arm carries a LAZY-ONLY conjunct (a lazy `Q` needs a
  non-nullable remainder, 316 measured cells) that the R24 panel added after
  the design lane's own probe structurally could not see the question. Read
  the file's header before touching the verdict ladder; every conjunct in it
  is a refutation somebody paid for.

  Two things it inherits that are easy to lose. Every set is computed in the
  SOUND direction, so anything unmodellable widens to all bytes and DECLINES —
  declining is always available and always safe. And A_CAT/A_ALT spines are
  walked ITERATIVELY (D10/DD-10/R1 R-2, and K20 the third time): a
  20,000-character pattern segfaulted pcrec once already for want of that, and
  three of this file's walks descend those spines.

  The `$`-follow exemption's gate is LIVE (D47.5): the analysis reads
  `cx->mods.multiline` at verdict time rather than carrying a comment about
  what pcrec does not support yet. `$` in a quantifier's follow is measured
  safe at 0/720 diverging cells and unsafe at 180/720 under `(?m)`, so the
  exemption is conditional on a fact that stops being true without anyone
  revisiting the analysis. Module `assertions` inherits the test obligation.

  Tests: tests/possessify/ (its own CLAUDE.md explains why three separate
  checks are needed and what each is blind to); failing-direction controls
  tests/mech/sabotages/S45-S49.

  It also EXPORTS its unique-iteration predicate (`pcrec_uniq_scratch` /
  `pcrec_uniq_iteration`, declared in core/internal.h) for revdet.c below, which
  asks the identical question of the REVERSED body. The export exists so that
  there is one implementation of a rule carrying three measured refutations,
  not two that could drift.

- **revdet.c** — [ENG-BREP] the REVERSE-DETERMINISTIC RUNG's analysis
  (docs/design/engine_m4.md §2.5, docs/design/eng_brep_design.md §3, and the
  lane's emitted-shape sketch at
  docs/design/rungselect_impl/rungselect_design.md). Marks every `A_REP` whose
  consumed run decomposes into iterations UNIQUELY and RECOVERABLY FROM THE
  RIGHT, so src/gen/emit_vm.c can emit ONE body copy instead of `rmax` of them.

  **The verdict and the material for it are ONE FIELD.** `Ast.revbody` holds the
  body's REVERSED AST and is non-NULL exactly when the rung applies, so the
  three emitter sites that must agree about the rung (`vm_cost_rep`,
  `vm_count_slots`, `vm_rep`) read one field rather than each re-deciding — and
  the site that selects the rung cannot select it without having the thing the
  rung needs. `Ast.possessive`'s precedent, one rung down.

  **The rule is TWO unique-iteration checks and each has a witness.** FORWARD
  (on the body) is what makes the emitted scan deterministic and licenses the
  per-iteration cut; its witness is `(aa?)`, which fails (U2). REVERSE (on the
  reversed body, the identical predicate on the identical construction) is what
  makes the retreat computable locally; its witness is `(?:ab|b)`, which PASSES
  forward and fails reversed, because reversed it is `(?:ba|b)` whose two
  initial positions are both `b`. That second class is exactly the residual
  engine_m4.md §2.5 predicts the boundary-record rung shrinks to.

  The forward predicate is IMPORTED from possessify.c (`pcrec_uniq_iteration`,
  with `pcrec_uniq_scratch` for the reusable position workspace) rather than
  reimplemented. Every conjunct in it is a refutation somebody measured, and a
  second copy of that rule is the worst place in this tree to keep two sources
  of truth.

  **`rd_alt_disjoint` checks a property that is already implied**, and that is
  deliberate. The emitted backward walk has no choice points — at an alternation
  it reads the next byte and jumps to the one branch that can begin with it —
  which is a strictly stronger thing to depend on than "the walk lands in the
  right place". (U1) implies it, but "implied by" is how a dependency quietly
  survives a change to what it depends on, so the check is re-derived directly
  on the reversed tree the emitter will walk. `pcrec_revdet_first` is exported
  so the check and the emitted dispatch read one computation.

  Same two inheritances as possessify.c and for the same reasons. Every decision
  is in the SOUND direction, so anything unmodellable DECLINES and a declined
  quantifier matches exactly what it matches today — which is also what makes
  `-fno-revdet` byte-identity-safe. And A_CAT/A_ALT spines are walked
  ITERATIVELY (D10/DD-10/R1 R-2, K20): the REVERSAL is the harder half of that
  obligation, because reversing a spine means REBUILDING one, and a quantifier
  body is allowed to be a 20,000-element concatenation.

  Tests: tests/rungselect/ (its own CLAUDE.md explains why three separate checks
  are needed); failing-direction controls tests/mech/sabotages/S50-S52.

- **mrl.c** — [M4.6d] MINIMUM-REMAINING-LENGTH pruning's analysis half
  (`pcrec_minw`; docs/design/k23_impl/k23_design.md §4.3, adopted by D51
  ruling 1 as K23's fix of record). The least number of subject bytes any
  match of a node can consume, over the eight AST kinds. That is the whole
  file: where the numbers are USED, and the lattice rule that makes a clamp
  sound at stride > 1, live at the emission sites in src/gen/emit_vm.c, which
  threads `minw` down its own walk as a FOLLOW-MIN accumulator rather than
  computing it per program point.

  It is NOT a transformation and mutates nothing, which makes it the odd file
  in this directory — it sits here rather than in the emitter because an error
  in it is SILENT in the same way possessify.c's and revdet.c's are, and for
  the same reason deserves its own file, its own tests and its own stated
  direction of safety. Under-estimating always prunes less; OVER-estimating
  deletes real matches with no compile error, no warning and no failing test
  unless the corpus happens to contain the shape.

  **The switch is EXHAUSTIVE with no live default arm, and that is a design
  obligation rather than a style preference** (§4.2's failure mode 1, sharpened
  by R26 V7). A node kind added after this file was written must be a COMPILE
  ERROR here — under `-Wswitch`, which `make strict` promotes — rather than a
  silent inheritance of whatever a default returned. The unreachable trailing
  `return 0` is the safe value, and says so.

  Two things it walks ITERATIVELY for src/ir/nfa.c's R-2 reason (D10/DD-10,
  K20): a left-leaning `A_CAT` spine and an `A_CAP` chain are as long as the
  PATTERN, not as deep as its nesting. What stays recursive descends one paren
  level per frame, i.e. Θ(d) — which is what K18 actually teaches, and is the
  correction to this design note's own refuted prediction 2 (`pss_walk`
  recurses on pattern structure today and compiles a 249-paren pattern fine;
  `clo_visit` was a problem because it recursed Θ(d²), not because it
  recursed).

  Arithmetic saturates at `PCREC_MINW_MAX` (core/internal.h, shared with the
  emitter's accumulator so a long concatenation of saturated subtrees cannot
  overflow past the ceiling that exists to prevent it). A wrapped product is
  not merely wrong, it is wrong in the UNSOUND direction whenever it lands on
  a small positive value; saturation is an under-estimate, which is safe
  twice over.

  Tests: tests/mrl/ (its own CLAUDE.md; the `.rxt` corpus there is
  D27-BLINDED and found a real gap in the first implementation).

- **minimize.c** — DFA minimization by Moore-style partition refinement with
  signature hashing. The EOL-view edge (`eolvar`) participates as an extra
  alphabet symbol so `$`-machines minimize correctly. Behavior-preserving:
  priority/leftmost-first semantics are already baked into the transition
  structure before this runs. Shrinks emitted tables (code size + cache).
  **[M4.7b/K7]:** its five local tables are the ONLY allocations on the compile
  path the Job does not own, so this is the one file where failing cleanly
  means freeing by hand before `ctx_nomem`; the header note claiming "no
  ctx_fail paths" is updated accordingly. **K25 is filed against this pass**,
  not against K7's accounting: Moore refinement needs O(n) rounds on an
  n-state chain, so `a{0,25000}` spends a measured 15.3 s here against 0.03 s
  for parse, NFA build and both subset constructions combined. Bounded memory,
  terminates, behaviour-preserving — a cost, not a failure — but it is what
  currently sets tests/resource/'s CPU budget.

## Conventions

A TRANSFORMATION pass takes (Ctx *, Dfa *) or (Ctx *, Nfa *), mutates in
place, and must be behavior-preserving — every pass needs corpus coverage that would catch a
semantic change (the full suite runs against post-pass output). Scan-avoidance
analyses that only inform codegen (prefilters, skip states) live in the
emitter instead; move one here if it grows its own IR transformation.

altcls.c is the one AST-LEVEL exception to the "mutates in place" half: it
runs before NFA/DFA construction exists to mutate, so it takes (Ctx *, Ast *)
and RETURNS the (possibly new) root instead — select_engine.c's `discharge`
hook shape, for the same reason (the rewrite can change tree SHAPE, which an
in-place field mutation cannot express). Still behavior-preserving, still
corpus-covered, still deny-only + D46-stamped like every pass in this
directory.

Maintenance: update this file when passes are added/removed.
