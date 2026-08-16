# src/opt — algorithmic optimization passes

Transformations pcrec must do because gcc cannot (APPROACH §5): they change
the algorithm, not the instruction selection. Passes run between DFA
construction (src/ir) and emission (src/gen).

## Files

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

  Exactly ONE analysis is registered today, and its trigger is the requested
  OUTPUT rather than the presence of a `(`: `a(b|c)+d` under `--no-captures`
  is capture-free WORK and stays on the DFA forever. Every other `VM_ONLY`
  registry row is gated by a module with no producer, so the parser refuses
  those patterns long before selection runs — which is also why SR-8's flip is
  smaller than its row implies (§9.1: zero currently-refused constructs become
  compilable when the VM exists).

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

- **minimize.c** — DFA minimization by Moore-style partition refinement with
  signature hashing. The EOL-view edge (`eolvar`) participates as an extra
  alphabet symbol so `$`-machines minimize correctly. Behavior-preserving:
  priority/leftmost-first semantics are already baked into the transition
  structure before this runs. Shrinks emitted tables (code size + cache).

## Conventions

A TRANSFORMATION pass takes (Ctx *, Dfa *) or (Ctx *, Nfa *), mutates in
place, and must be behavior-preserving — every pass needs corpus coverage that would catch a
semantic change (the full suite runs against post-pass output). Scan-avoidance
analyses that only inform codegen (prefilters, skip states) live in the
emitter instead; move one here if it grows its own IR transformation.

Maintenance: update this file when passes are added/removed.
