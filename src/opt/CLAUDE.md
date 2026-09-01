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

- **callgraph.c** — [DD-14] wave B+C: THE CALL GRAPH. Which groups are
  called, what each callee region can reach, and the two things no walker in
  this tree can answer for itself.

  **IT EXISTS BECAUSE `Ast.u.call.body` IS THE AST'S FIRST BACK EDGE.** Every
  walker in `src/` was written for a TREE — `pcrec_minw`, `pcrec_has_atomic`
  and `pcrec_has_bref` are bare `const Ast *` descents with no context, no
  memo and no visited set — so a question whose answer for a call genuinely
  IS the callee's ("how wide is this?", "can it match empty?") is not
  expressible at the walker at all. A WHOLE-TREE PREDICATE needs none of this
  and MUST NOT follow the edge: it already visits the callee at the callee's
  own lexical position, so following it is redundant AND non-terminating
  (`(a(?1))` hangs the COMPILER, in predicates asked of every pattern).

  **THE PASS ORDER IS THE DESIGN AND IT IS WAVE A2's FINDING**, not the
  design document's — `subroutines_design.md` does not address it anywhere.
  `.body` is a CACHE of "which subtree is that group's, IN THE TREE THE
  EMITTER WILL WALK", and two passes above this one REBUILD nodes rather
  than mutating them: `pcrec_altcls` allocates a fresh `A_CAP` over a merged
  class (`*r = *a; r->l = body;`), and `pcrec_discharge_atomic` splices an
  `A_ATOMIC` out. A `.body` captured at END OF PARSE — where design §4.2 and
  wave A2's `PendingRef` comment both put it — therefore names a subtree that
  is no longer in the tree, and under `CALL_LINKAGE` the callee REGION is
  emitted from the stale one while the LEXICAL occurrence comes from the new
  one. **So this pass runs after `pcrec_select_engine` and before emission,
  and it is the only writer of `.body` anywhere.**

  **MEASURED, AND THE MEASUREMENT NARROWED THE CLAIM.** With the bind moved
  above `pcrec_altcls`, `((?:a|b))(?1)` emits TWO DIFFERENT PROGRAMS FOR ONE
  GROUP — a merged class test lexically, the un-merged two-branch alternation
  with its own `RX_PUSH` in the region — and `RX_RESUME_FRAMES` moves 2 -> 3
  with it. **The ANSWERS do not change**, because `altcls` is answer-preserving
  in both directions, which is exactly why no corpus cell can see this and the
  detector is `[DD-14-RECURSION rule 3]` in `tests/codegen`. **And the
  DISCHARGE witness is NOT a hazard**: `((?>a)b)(?1)` compiles BYTE-IDENTICALLY
  under the same sabotage, because the discharge splices by rewriting the
  PARENT's `->l` in place and the `A_CAP` a callee is rooted at keeps its
  identity. Wave A2 named both passes; only the one that REBUILDS the node
  matters. Sabotage row S166.

  **IT COMPUTES `minw` AND NOT `nullable` OR `W`, WHICH IS A DEVIATION FROM
  §4.4b's "one mechanism"** and is the wave's largest amendment to the design.
  Both exceptions are the same reason — the RECURRENCE lives in the emitter
  and cannot be moved. `vm_nullable` is `static` to `src/gen/emit_vm.c` and is
  the emitter's own definition of the property the empty-iteration guard is
  emitted on; a copy here would be a second answer for the two to disagree
  about, which is the failure mode `vm_marked`, `vm_cuts` and
  `vm_cursor_fits` are each ONE predicate to avoid. And `W` is a set of SLOT
  INDICES, which are assigned by `vm_count_slots`' walk over the emitter's own
  rung decisions and exist nowhere else. What this file owns is the GRAPH both
  fixpoints iterate over, exported so the emitter does not re-derive "which
  groups are called and what does each reach".

  **THE MEMO LIVES ON THE NODE, NOT IN THIS FILE.** `u.call.minw` and
  `u.call.nonnullable` are cached on the `A_CALL` because the walkers that
  READ them have no `Ctx` to reach a memo through, and the only other spelling
  is a file-static — a mutable global, which [TS-3]'s concurrent-compile test
  exists to forbid. Every one is written so **the arena's zero is the SOUND
  answer**, since `pcrec_minw` is legitimately called from `possessify.c`
  before this pass runs: `minw` 0 under-estimates (its safe direction), and
  `nonnullable` is INVERTED so a zero reads NULLABLE, the direction that EMITS
  the guard.

  **AND IT RE-ASKED MODULE `lookaround`'s §2.7 `\K` REFUSAL THROUGH THE
  GRAPH, THEN DELETED THE CHECK.** `la_has_kreset` runs in the PARSE HOOK,
  where it must (the only place with a pattern OFFSET), and at that instant
  `.body` is NULL and a forward call's target is unparsed — so wave A2 left
  three answers: re-check after resolution, refuse the combination, or MEASURE
  what 10.46 does. This lane built the first, then measured: **PCRE2's rule is
  LEXICAL.** `(?=(a\Kb))x` is error 199 and `(?=(?1))(a\Kb)` COMPILES and
  matches (1,2) on "ab", so the first two answers are OVER-REJECTIONS. The
  check was deleted and pcrec re-measured: **7 of 7 cells agree with libpcre2,
  including the isolating `^(?:((?:a)\Kb)){0}(?=(?1))ab$`** where the `\K` is
  reachable only through the call inside the lookahead. Structural reason:
  design §5.3a excludes slots 0 and 1 from `W` so the `\K` survives the
  RETURN, and `vm_look` restores the CURSOR from `SLOT_LOOK_POS` rather than
  slot 0 so it survives the ASSERTION. The file's own `\K` note carries the
  measurement; cells in `tests/recursion/kreset.rxt`.

  **[DD-14.LB] IT ALSO RUNS THE `maxw` FIXPOINT**, `minw`'s mirror, descending
  from `PCREC_W_UNBOUNDED` because over-estimating is `pcrec_maxw`'s free
  direction and under-estimating is its miscompile. **It uses NO CYCLE TEST**,
  and the `reach` closure sitting right there is why that is worth stating:
  `reaches(i, i)` would answer "is target i in a cycle" directly, and it is the
  WRONG question. `mrl_sat_add` saturates, so a target in a cycle reads its own
  published `PCREC_W_UNBOUNDED`, computes `k + UNBOUNDED == UNBOUNDED` and
  never leaves the top — and the same absorption gives the right answer for a
  target that merely REACHES a cycle without being in one (`g = (?&h)x` with
  `h` recursive is genuinely unbounded), which a cycle test gets wrong unless
  it is widened into exactly this propagation. One mechanism instead of two,
  with a cell for each half in `tests/recursion/inlookaround.rxt`.

- **postresolve.c** — [DD-14.LB] THE POST-RESOLUTION CHECKS: the pass for every
  rule that must refuse a pattern AT A PATTERN OFFSET and cannot be decided
  until the call graph exists. Run from `pcrec_compile` immediately after
  `pcrec_callgraph_build`.

  **IT EXISTS BECAUSE TWO FACTS COLLIDE AND NEITHER WILL MOVE.** A module's
  parse hook is the only place in this compiler that holds a pattern offset
  (`Ast` carries no position of any kind — PARSE-1, and `AltInfo.last_bar`
  exists because of it), and the call graph does not exist until after parse
  and after every rewriting pass (`callgraph.c` above, wave A2's finding). So a
  rule whose answer depends on a callee is DECIDED where it cannot be RAISED
  and raised where it cannot be decided.

  **THE RESOLUTION IS THREE MOVES AND THEY ARE A SHAPE, NOT A CASE:** the hook
  RECORDS (the offset, on the node, in the module's own `u.*` payload), the
  graph is BUILT, this pass RE-ASKS the module's own rule at the recorded
  offset. Today's one customer is module `lookaround`'s §2.5 fixed-width rule
  for a lookbehind whose body carries a call; the shape recurs (§6.3's splice
  eligibility, a variable-length lookbehind follow-on, the next module that
  meets a call), so a second occurrence extends a list rather than inventing a
  second post-graph timing.

  **THE SPLIT OF OWNERSHIP IS THE DESIGN.** This file owns the WALK and the
  ORDER and knows nothing about lookbehind widths;
  `src/parse/mod_lookaround.c` owns the RULE and its three refusal sentences
  and knows nothing about the call graph. Inlining the rule here would be a
  second derivation of "is this branch fixed-width" for the hook's own to
  disagree with — the failure `Ast.u.look.widths` is stored to prevent, one
  level down.

  **ORDER IS PART OF THE CONTRACT**: recorded constructs are visited in
  ASCENDING PATTERN OFFSET, so a pattern with two offending lookbehinds refuses
  at the FIRST, which is what the hook would have done. Walk order is not that
  order and is not close to it — a flat concatenation is LEFT-NESTED, so a
  spine walk reaches the RIGHTMOST element first and would report the LAST
  offender.

  **A SKIPPED PASS IS LOUD BY CONSTRUCTION.** The pending state is encoded as
  `u.look.widths == NULL`, which `vm_look_behind` already `ctx_fail`s on by
  name — so losing this pass is an internal error on the first call-bearing
  lookbehind rather than a back-step of width zero. Encoding "pending" in a new
  boolean instead would have made the same loss a WRONG SPAN, and on a negative
  lookbehind a FALSE MATCH. Its walk is its own (the house style — `revdet.c`,
  `possessify.c`, `select_engine.c`, `altcls.c` and `callgraph.c` each carry
  one, because what varies is which edges they follow) and it does not follow
  `u.call.body`, which is both design §4.4's non-terminating compile and
  redundant, since a lookbehind inside a called group is visited at its own
  lexical position anyway. Sabotage: S169 (never called; DETECTED,
  14fail/23pass, every failure a pattern-compile failure) and S170 (resolves
  but never refuses; DETECTED, 4fail/33pass, the opposite half of the same
  file). Tests: `tests/recursion/inlookaround.rxt`.

- **prefix_k.c** — [OPT-K] THE OFFSET-k PREFIX ANALYSIS: which bytes every
  match must carry, at which offsets from its own start, and which of those
  offsets are worth testing before the DFA's transition loop is entered
  (`docs/design/offset_k_skip.md`). Like `select_engine.c` and `mrl.c` it is
  an ANALYSIS rather than a transformation — it mutates nothing and returns a
  `PrefixKSets` the emitter reads.

  **IT WALKS THE NFA, AND THAT IS THE ONE FACT THAT DECIDES EVERYTHING ELSE
  ABOUT THE FILE.** The candidate-start filter pcrec shipped before this row
  derives its byte set from the forward DFA's START STATE
  (`cand_from_escapes`, src/gen/emit_dfa.c): the bytes on which the start
  state does not stay put. That is exact at offset 0 and USELESS past it,
  because an ENG_UNANCH DFA state is the merge of the threads from EVERY
  subject position — four bytes into `\d{4}-`, the state carries threads at 4,
  3, 2, 1 and 0 digits, so "a byte that does not return the machine to the
  start state" at offset 4 is `[0-9-]`, not `-` (MEASURED: 11 bytes). The
  thread whose bytes the analysis wants to constrain is the one from the
  candidate start ALONE, and the only place it exists on its own is the
  pattern's own NFA, walked from `Nfa.anch_start` — a FIELD published by
  `pcrec_build_nfa` and deliberately left alone by `nfa_wrap_unanchored`,
  rather than a shape test on the wrap's SPLIT. **Offset 0 keeps coming from
  the DFA derivation that already owns it**, so no fact has two sources, and
  §2.1 of the note is why that offset-0 set is CORRECT to be as wide as it is
  (a `\b` machine's start state escapes on every word character because it
  must REMEMBER the left-hand context, not because a match can begin there).

  **SOUND IN ONE DIRECTION ONLY, and the closure is where that lives.** The
  walk passes every assertion node as though it held, so a set can only ever
  be WIDER than the truth, the cost model then declines it, and the artifact
  keeps the filter it had. There is no direction in which this file can refuse
  a start the scan would have accepted. Its `NKind` switch has NO `default:`
  arm for `mrl.c`'s stated reason (R26 V7) and one of its own: a new
  CONSUMING kind silently treated as an assertion is the file's single unsound
  direction, so the compiler is made to say so. **That switch is the SECOND
  hand-maintained exhaustive `NKind` walk in the tree** — `src/ir/dfa.c`'s
  closure is the first — and the two are paired by nothing but this sentence
  and `-Wswitch`.

  **THE SELECTION IS A COST MODEL, AND THE MODEL WAS MEASURED WRONG ONCE.**
  Five constants, four of them measured off this box
  (`docs/dev/opt3_dfa_scan_measurement.md`), over a static byte-frequency
  prior that is D83's FALLBACK — the findings-file hook is `pcrec_byte_freq_ppm`
  and is named, not built (D77). The prior is deliberately NOT derived from
  the comparative bench's own log text: that would be a control sharing a
  source with what it controls (learnings.md §3), and every measurement in the
  note would then be a measurement of a table fitted to its own subjects.
  What the model got wrong is recorded at the constant it produced: it
  predicted 13x for `\b[0-9]{10,19}\b` and the box measured 0.96x-1.02x three
  times, because a VERIFY removes loop ENTRIES while a SCAN removes BYTES.
  The selection therefore requires the scan offset to MOVE off 0 — a MEASURED
  rule, stated as such beside the model rather than folded into it.

  Tests: `tests/offsetskip/` (answers), `tests/codegen/run_offset_skip.sh`
  (the artifact, the population, and the prior's own sum), sabotage rows
  S185/S186/S187.

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

  **[M6.5.2] AND IT IS WHERE THE PREFILTER IS REFUSED.** A backref-bearing
  pattern gets `fit.prefilter = false`, and `-fprefilter` on one is a REFUSAL
  rather than a silent override — D46's do-or-die posture, applied to a request
  the pattern cannot honour. The reason is §7.1's and it is measured twice
  over: the capture-erased approximation a prefilter would be built from is not
  even a SUPERSET once the referenced group's transitive closure holds an
  assertion or an atomic/possessive operator (12 of 18 positive-control cells
  are false negatives across those two reasons, plus 3 of 5 for the transitive
  case), and where it IS a superset its leftmost SPAN differs from the true one
  on up to 389 subjects in one family — so the EXACT anchored window
  `engine_m4.md` §6.1's hybrid needs cannot be had either way. That line is
  also what makes `src/ir/nfa.c`'s missing `A_BREF` arm unreachable rather than
  lucky: nothing builds a machine for a language a backreference is not in.

  **[DD-14] AND A CALL-BEARING PATTERN GETS NO PREFILTER EITHER — WAVE E's
  LINE, LANDED IN WAVE B+C.** Erasing a call is not a superset, it is a
  DIFFERENT language, and the counterexample is one line (§8.2): `a(?1)b` with
  group 1 = `x` matches "axb"; erase the call and `ab` is left, which does
  not. So the prefilter's REJECTION would be a false negative — the one thing
  a prefilter may never be — which is unlike `lookaround`'s erasure (a
  one-line superset proof) and exactly like `backrefs`' above.

  **IT COULD NOT WAIT FOR WAVE E, and that is measured rather than argued.**
  `src/ir/nfa.c`'s `compile_ast` has an `A_CALL` arm that `ctx_fail`s by name,
  annotated "unreachable: VM_ONLY, no prefilter" — and "unreachable" was true
  only while nothing PRODUCED an `A_CALL`. MEASURED on the wave's own branch
  before the predicate existed: `(a)(?1)`, `(?R)` and `(?<n>a)(?&n)` each
  answered `pcrec: internal error: bad AST node`, because a capture-bearing
  pattern routes to the VM, the VM asks for its prefilter, and the prefilter
  build walks a node it refuses. The choice was not "ship the optimisation
  early" but "ship a compiler that cannot compile the module's own corpus".
  S165 is the row, and its own header records that the SILENT-SKIP prediction
  §9.3 makes becomes reachable only at wave G, which builds §8.3's sound
  approximation and makes an erased machine constructible at all. The cost is
  measured and stated: 21x-350x on the sparse-candidate shape a prefilter
  exists for, over the non-recursive half of the population.

  **[M6.4.2/D67] SR-8 IS BUILT HERE, AND `forces_kreset` RETIRED INTO IT.**
  `\K` was the first VM_ONLY producer and got a bespoke analysis at [M6.2]
  wave E; `(?>` is the second, and `tests/registry/registry_check.c`'s tripwire
  said in advance what to do about it — *"If a SECOND construct arrives here, do
  not add a second exception: two is when the generic consultation has earned
  its axis and SR-8 is the right build."* So `forces_registry` replaces
  `forces_kreset`: producers stamp each node with the registry ROW they were
  dispatched on (`Ast.reg`, via the ONE `pcrec_ast_stamp` call), and this
  analysis ANDs `pcrec_ast_engines()` over the POST-DISCHARGE tree with `why`
  taken from the first DFA-excluding node's row. Backrefs' twelve rows ([M6.5])
  will need no line here at all.

  The DELETIONS are the point: `has_kreset`, `forces_kreset`,
  `Ctx.first_kreset_pos` and the tripwire's `\K` exception are all GONE, and
  `Ctx.first_vmonly_pos` is the one generic offset field where two
  per-construct ones would have been. `\K`'s shipped diagnostic is reproduced
  BYTE FOR BYTE by the generic path, which is D67's "same verdict, same
  position" made checkable.

  **`forces_captures` does NOT retire** (D67 contract note 1): it is
  REQUEST-derived, a property of the generation request with no registry row
  behind it. Two kinds of forcing therefore remain, and the `--engine=dfa`
  override has to tell them apart — `EngineAnalysis` gains a `node_derived`
  bit and the branch takes the captures arm ONLY when no node-derived analysis
  contributed a why. **That closed a defect live on the shipped compiler**:
  `--engine=dfa '(a)\Kb'` answered "pass --no-captures", advice that cannot
  help, because `\K` still forces the VM after the captures are gone.
  `RX_ENGINE_WHY`'s first-row rule is untouched — the second why exists only
  for the override.

  **The FREE DISCHARGE runs from the top of `pcrec_select_engine`**, before the
  analysis loop and unconditionally, which is what makes a per-ROW column
  produce a per-PATTERN answer: `--engine=dfa '[^"]*+"'` succeeds because the
  node is GONE by the time `forces_registry` looks, while `--engine=dfa
  '(?>a|ab)c'` refuses by name. See atomic.c's own entry for why it is not
  registered in the `discharge` socket.

  `forces_captures` triggers on the requested OUTPUT rather than the presence
  of a `(`: `a(b|c)+d` under `--no-captures` is capture-free WORK and stays on
  the DFA forever.

  **THE PARAGRAPH THAT USED TO STAND HERE EXPIRED RATHER THAN BEING WRONG.** It
  ran: every `VM_ONLY` registry row is gated by a module with no producer, so
  the parser refuses those patterns long before selection runs — which is also
  why SR-8's flip is smaller than its row implies (§9.1: zero currently-refused
  constructs become compilable when the VM exists). Module `assertions` now HAS
  a producer and `\K` is its `VM_ONLY` row, so SR-8's flip has its first member
  and the override's second branch (below) stops being empty by population.

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
  the thing to build BEFORE the producer lands, not after. **It FIRED on `\K`
  (2026-08-19), which is the day it was written for, and the answer was still
  not SR-8**: `\K`'s verdict is not "some registry column says VM", it is "this
  AST carries a node whose write is path-dependent" — a fact about the tree, not
  about the table — so a construct-specific row is the honest shape, and a
  generic column lookup designed around one customer is what D18/OS-0/D53
  forbid. The tripwire keeps its demand for the other 47 rows and gains a NAMED
  exception that PAYS: it asserts live that `--engine=dfa` on `a\Kb` refuses by
  the construct's own name AND that the same pattern compiles on the default
  engine. A SECOND construct arriving there is when the generic consultation has
  earned its axis.

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
  not passing it; a `VM_ONLY`-construct conflict names the construct.

  **[M6.2 wave E] the second branch HAS a population now — `\K` — and it ran
  for the first time without a line of it changing**, which is the whole value
  of having written it at [M4.5b] against no customer. `pcrec --features
  assertions --engine=dfa 'a\Kb'` refuses with "\K at pattern offset 1
  requires the VM engine, which --engine=dfa excludes", where the captures
  branch's `--no-captures` advice would have been a lie: no flag makes a `\K`
  pattern DFA-compilable.

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

  **[SEL-1] (2026-08-28) `auto`'s DFA-CAP-OVERFLOW CONTRACT IS A FOURTH ROW
  IN THE FIXPOINT, `forces_dfa_overflow`** — plan row [SEL-1], K40's fix:
  a DFA build that overflows a cap (state count, table entries, K7's
  element budget; src/ir/dfa.c's two "pattern too complex" sites) is a
  SELECTION OUTCOME under `auto`, not a refusal, and the general mechanism
  is that the build reports "over budget" as a RESULT this file's existing
  fixpoint consumes, exactly like `forces_captures`/`forces_registry` — no
  try/catch at the `ctx_fail` site, no second selector. It CANNOT fire on
  the pass that discovers the overflow (selection runs before the DFA is
  built), so it only ever returns non-trivially on `src/core/compile.c`'s
  ONE-SHOT RETRY of the whole pipeline (`Ctx.dfa_disabled`, set only there)
  — the only mechanism this compiler has for "abandon everything below this
  point" is its one `setjmp`, so feeding the result back means running the
  pass again with one more input bit, not adding a second recovery point.
  `cx->dfa_disabled` ALSO folds into the prefilter derivation just above
  (`has_bref || has_call || cx->dfa_disabled`, all three silently drop it)
  in the SAME step that excludes `ENGM_DFA` — a retry's own DFA build would
  be the identical construction that just overflowed, so the fallback must
  not attempt it a second time (the plan row's cost bound: at most one
  refused build dearer than `--engine=vm`). `--engine=dfa` and
  `-fprefilter` are UNTOUCHED — `compile.c`'s retry never fires under
  either, so this row never fires under `--engine=dfa`'s override branch
  either, which is also why `node_derived` is `false` and effectively moot
  for it. `RX_ENGINE_WHY` carries `cx->dfa_overflow_why`'s text
  (e.g. `"dfa overflowed: >32000 states"`) when this row is the one that
  won `why` on the ordinary first-wins rule; when a request-derived reason
  (captures) wins instead, the prefilter is STILL dropped, through
  `dfa_disabled` rather than through `why` — the two effects are
  independent by construction. `src/gen/emit_vm.c`'s `--emit-ir` listing
  needs its own arm for the identical reason `has_bref`/`has_call` did
  ([M6.5.2]/[DD-14 wave E]'s precedent: without one, the line falsely
  claims the `--engine=vm` side effect). Tests: tests/vm/run_vm_tests.sh
  §3b, tests/prefilter/ (see its own CLAUDE.md's "[SEL-1]" section).

- **atomic.c** — [M6.4.2] module `atomic-groups`' AST-level pass and its two
  walks (docs/design/atomic_groups_design.md §5.3/§5.4, panel-approved R31),
  plus [M6.5.2]'s two BACKREFERENCE tree predicates, [M6.6.2]'s
  `pcrec_has_lookaround` and [DD-14]'s `pcrec_has_call`, which live here for
  this file's own stated reason:
  SEVEN switches over `AKind` with NO `default:` arm, so a node kind added later
  is a compile error at each of them rather than a silent inheritance. That is
  seven of the tree's twenty-SEVEN such sites in one file — its densest
  concentration of the alarm, and the reason each new whole-tree predicate
  keeps landing here rather than beside its own module.

  **[DD-14] EVERY WALK IN THIS FILE IS A WHOLE-TREE WALK, AND THAT NOW HAS A
  SECOND CONSEQUENCE.** `Ast.u.call.body` is the AST's first `Ast*` -> `Ast*`
  back edge, and `subroutines_design.md` §4.4's rule is that a whole-tree
  predicate MUST NOT follow it: the callee is visited at its own lexical
  position anyway, and following the edge is a non-terminating compile on
  `(a(?1))` — in predicates asked of every pattern. Six of the seven switches
  therefore DECLINE `A_CALL` outright. The seventh is `pcrec_bref_mark`, whose
  arm is `mark[u.call.target] = true` and no descent (§4.3): a call names a
  group exactly as a reference does, so without it `--no-captures` deletes
  group 1's `A_CAP` out from under `(a)(?1)`. The mark is NOT transitive and
  needs no fixpoint — a call from inside group 1 to group 3 is an `A_CALL`
  node in the tree, so the whole-tree walk reaches it wherever it sits.

  **`pcrec_has_call`** ([DD-14], `subroutines_design.md` §4.3) is
  `pcrec_has_bref`'s sibling, and **AT WAVE B+C IT IS WIRED**. Its consumer is
  the `fit.prefilter` line in `select_engine.c`, which design §11 schedules for
  wave E and which landed here because without it `src/ir/nfa.c`'s `A_CALL`
  arm is REACHABLE: every capture-bearing call pattern answered "internal
  error: bad AST node", measured on the wave's own branch. Wave A2 placed the
  predicate and deliberately left the call site absent, on the ground that a
  fake one would pre-satisfy the row that owns the real one; the real one now
  exists and S165 is that row.

  **`pcrec_has_lookaround`** ([M6.6.2], `lookaround_design.md` §5.6) is
  `pcrec_has_atomic`'s TWIN and is placed beside it because the two are read in
  ONE expression, at one site, at one point in the pipeline — `Vm.mrl_win` in
  src/gen/emit_vm.c, post-discharge. Same hazard through a different door: the
  prefilter is built from the lookaround-ERASED pattern (src/ir/nfa.c lowers an
  `A_LOOK` to an epsilon), so its window END is not an upper bound on the real
  match's end, while its rejection and its span START stay sound. FLAT rather
  than shaped — §5.6 names the narrower "a lookaround inside an alternation"
  predicate and rejects it as a second analysis with no independent check.
  **AT WAVE A2 THE PREDICATE IS PLACED AND ITS CONJUNCT IS NOT YET IN
  `v.mrl_win`**: wave E adds `&& !pcrec_has_lookaround(root)` and sabotage row
  S-LA12 deletes it. Nothing produces an `A_LOOK` before wave B+C, so the
  conjunct could not be exercised and would pre-satisfy its own detector.

  **`pcrec_has_bref`** is §7.1's predicate — does anything here compare subject
  text to subject text — and its ONE reader is `select_engine.c`, which forces
  `EngineFit.prefilter` OFF for such a pattern. **`pcrec_bref_mark`** computes
  §3.2.4's MARKED SET: the union of every `A_BREF`'s `refs`, which for a
  by-name reference over a duplicated name is EVERY member of the run and not
  merely the member some analysis thinks it resolves to. R32's re-check E13 is
  why: §8.3's chain reads them all at MATCH time, so an unmarked member is read
  under write-on-traverse and E1 returns through it — and the measured cell
  shows there is no member to pick, because
  `(?J)^(?:(?<a>q))?(?:(?<a>a|b\k<a>))+$` on "aba" resolves to the SECOND
  member, which is the one being re-entered. Both are asked of the
  POST-DISCHARGE tree, exactly as `pcrec_has_atomic` is.

  **`pcrec_discharge_atomic` — THE FREE DISCHARGE.** Deletes every `A_ATOMIC`
  whose cut is PROVABLY a no-op and splices its body back in. The condition is
  possessify's §2.2 verdict asked TRANSPARENTLY (with the group's own follow),
  because the verdict's entire content is *"no retreat into this loop can
  produce a match the preferred path does not"*, which is precisely *"the cut
  deletes nothing"* about the ERASED tree. MEASURED at 0 violations over 532
  positive-verdict patterns (`out/free_discharge.txt`). It ships for the
  `A_ATOMIC(A_REP(X))` arm ONLY; the plain-group `(?>X)` arm is DEFERRED at
  ZERO measured cells (R31 E7) and needs a callable (U1)/(U2) predicate over an
  arbitrary subtree, which possessify.c does not expose.

  **THE VERDICT ALONE IS NOT THE CONDITION, AND THE DESIGN SAID IT WAS.** Two
  narrowings were forced by measurement during [M6.4.2], both of the shape §14
  item 9 predicts (a §2.2 CONSEQUENCE an emitted shape depended on):

  - **GREEDY ONLY.** For a greedy body the loop's FIRST exit IS the maximal
    exit, so the cut fires where §2.2 says the loop lands. For a LAZY one the
    first exit is the MINIMAL exit, while §2.2's positive verdict rests on the
    PREFERENCE COLLAPSE — licensed by the FOLLOW forcing the loop to the
    maximal exit — and the cut fires BEFORE the follow is ever consulted.
    Measured: `(?>a*?)b` on "aaab" is (3,4) and `a*?b` is (0,4), on a positive
    verdict. §5.3's own measurement could not have found it: it drives the
    possessive SUFFIX spellings, and there is no lazy one (`a*?+` is an error),
    so all 532 positive-verdict patterns are greedy.
  - **KEYED ON THE GROUP, NOT THE QUANTIFIER.** The verdict is about a GROUP,
    with that group's follow, and two nested groups over one quantifier ask two
    different questions. Measured: `(?>a*+)a` parses to
    A_ATOMIC(A_ATOMIC(A_REP(a))); the inner group's verdict (empty follow,
    positive) discharged the inner correctly, and the OUTER then found its
    now-spliced `A_REP` child already in the set and discharged itself on a
    verdict computed for a different follow — `a*a` on "aaa" is (0,3) where
    `(?>a*+)a` is NOMATCH.

  **WHY IT IS NOT REGISTERED IN `EngineAnalysis.discharge`**, which is the
  socket engine_m4.md §5.2 designed with this module named as its customer.
  Three reasons, the third measured: the socket only runs when the pattern is
  already VM-FORCED, so a capture-free `a*+` would be discharged differently
  under `--engine=vm` than by default; `discharge`'s contract is "rewrite so
  the ENGINE FORCING no longer applies", which a PARTIALLY dischargeable
  pattern cannot honour; and the fixpoint in select_engine.c NEVER CALLS a
  registered hook — it sets `rewrote = true` for any non-NULL one and loops, so
  registering today would run the analysis 8 times and rewrite nothing. It is
  therefore an ordinary AST pass driven from the top of `pcrec_select_engine`,
  the same call `run_possessify` already makes for the same reason.

  **NOT gated by `-fno-possessify`.** The discharge is semantics-preserving by
  its own verdict, and gating it would make an OPTIMISATION flag change which
  ENGINE a pattern gets. The consequence is that emission-neutrality (a
  discharged possessive emits byte-identical VM code, because possessify
  re-derives the same verdict on the same quantifier) holds only in that flag's
  ABSENCE — under it the discharge runs and `run_possessify` does not.

  **`pcrec_has_atomic`** is H3's predicate, read at EMISSION and therefore
  POST-discharge: `[^"]*+"` compiles to a pure DFA with the MRL ceiling intact,
  `(?>a|ab)c` is VM-forced with the ceiling off. **`pcrec_ast_stamped_by`** is
  D65's built-status signal for a row that reaches no doorway (RK_QUANTSUFFIX),
  reading the SR-8 stamp rather than a second fact.

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

  **[M6.4.2] `pcrec_poss_survey` — the SAME verdict, as a QUERY.** The free
  discharge (atomic.c) needs §2.2's answer on one `A_REP` without marking
  anything, and a SECOND implementation of §2.2 is the one thing this file must
  never grow: every conjunct in it is a measured refutation of a simpler rule
  somebody believed. So the survey runs the same `pss_walk` — same FOLLOW
  accumulation, same enclosing-loop term, the same lines — and reports positive
  verdicts through a callback instead of writing `Ast.u.rep.possessive`. One pass is
  exact rather than an approximation of the fixpoint: the verdict reads no
  `possessive` field anywhere, so a second round marks nothing new.

  **A_ATOMIC IS TRANSPARENT AT TWO OF THIS FILE'S THREE SWITCHES AND NOT AT
  THE THIRD, and the design said all three.** `first_of` and `gk_build` read
  through the cut, which is right: FIRST is the bytes a node can BEGIN with and
  a cut removes whole MATCHES, and the position automaton read through the cut
  has MORE positions and MORE follow edges than a cut-aware one, so the verdict
  can only become more conservative. `pss_walk` is different, and the
  difference is that it threads FOLLOW — **and FOLLOW is exactly what the cut
  cuts.**

  MEASURED, on both engines, before the arm was corrected: with the group's own
  follow passed through, `(?>(?:a|bc)*?)d` on "abcd" answers **(0,4) where
  libpcre2 answers (3,4)**. The lazy loop's verdict came out POSITIVE because
  its follow looked like `{d}` and `may_end` looked false, so the lazy conjunct
  did not fire — but `d` is not that loop's follow: the group COMMITS at the
  loop's first exit, which for a lazy loop is the MINIMAL one, and `d` runs
  only after that commitment. §2.2's collapse argument assumes the loop can be
  RE-ENTERED, which is precisely what the cut deletes. So an atomic body is
  walked as a SELF-CONTAINED PATTERN: empty follow, `may_end` true. A
  quantifier that is not last in the body still gets its real within-body
  follow from the A_CAT arm.

  §6.4a's 776,160-cell sweep (10,504 REFUTABLE, 0 violations) could not have
  found this: its generator is `PRE (?>QB q|QB xy) tail`-shaped, so a
  quantifier inside the group is always followed by something INSIDE it, and
  the cell where the quantifier ENDS the atomic body is not in its population.

  **THE SURVEY ASKS A DIFFERENT QUESTION AND GETS THE OTHER FOLLOW.** The free
  discharge asks "would DELETING this group change the answer", whose answer
  for the erased tree is the TRANSPARENT verdict. The two genuinely differ:
  `(?>a*)a` is NOMATCH on "aaa" while `a*a` is (0,3), and only the transparent
  reading refuses to discharge it, while only the cut-aware reading is right
  about the MARK the emitter needs. Same node, two questions, two follows —
  which is why `pss_verdict` is factored out and both come from the same lines.

  **STILL SOUND BUT MEASURABLY INCOMPLETE where it IS transparent.** An atomic
  group IS a unique-match guarantee, so a §2.2 that understood `A_ATOMIC` in
  `gk_build` would accept all 8,820 patterns in the "quantifier WRAPPING the
  atomic group" position where transparency accepts 0. Declining is always
  safe, so that is an opportunity deliberately not taken in [M6.4.2].

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

  **[M6.2 wave A] the `$`-follow exemption's gate is live AND SCOPE-CORRECT
  (D47.5 + its 2026-08-18 addendum; D62; assertions_design.md §8).** "Live"
  turned out to be necessary and NOT sufficient, and this file is where that
  was found out. The live read was `P.multiline = cx->mods.multiline`, taken
  once AFTER the parse — i.e. the parser's end-of-pattern option state — while
  `(?m)` in PCRE2 is SCOPED. Two of the four reachable shapes disagree in the
  unsound direction: `(?m:a{0,4}$)` and `(?m)a{0,4}$(?-m)` both end the parse
  with multiline=false and both contain a genuinely multiline `$`, so both
  would have possessified a quantifier whose retreat is the only route to the
  match — measured as lost-match cells, correct answer `(0,1)`, possessified
  answer NO MATCH. D47.5's own recorded obligation names the leading-`(?m)`
  shape, the one the old code got right, so discharging it would have left
  both defects live. The cure: `first_of` reads `a->u.anch.multiline` off the NODE,
  the parser resolves it at the `$` itself, `ParseMods` is now incomplete
  outside `src/parse/` so no later pass can repeat the mistake, and `\z`
  (A_END) takes the same exemption with no gate at all — its satisfying set is
  the singleton {n}, so the upward-closure argument is strictly sharper than
  `$`'s and nothing can make it false. The exemption FIRING is checked through
  the artifact's `<PREFIX>_VM_STRATS` stamp in both directions
  (tests/assertions/run_assertions_tests.sh); the historical account of the
  verdict-time read follows.

  Before wave A: the analysis read
  `cx->mods.multiline` at verdict time rather than carrying a comment about
  what pcrec does not support yet. `$` in a quantifier's follow is measured
  safe at 0 diverging cells without `(?m)` and unsafe under it (re-measured
  2026-08-18: 0/168 vs 12/168 on the greedy population — the 0/720 vs
  180/720 previously cited here came from a since-changed probe population;
  qualitative claim unchanged), so the exemption is conditional on a fact
  that stops being true without anyone revisiting the analysis. Module
  `assertions` inherits the test obligation — AND the R30 panel found this
  gate's verdict-time read is SCOPE-BLIND (end-of-pattern state, while (?m)
  is scoped): the miscompile cells and the parse-time-resolution cure are
  assertions_design.md §8 / decisions.md D47.5's addendum.

  **[M6.2 wave D] `\G` DECLINES, and it takes `\A`'s arm rather than `\z`'s —
  a THIRD reason for the same verdict, which is why it has its own row in the
  STRATS check rather than riding either neighbour's.** The exemption rests on
  UPWARD CLOSURE, not on the satisfying set being a singleton: `\z`'s singleton
  is `{n}`, ABOVE every retreat position, and `\G`'s is `{startpos}`, BELOW
  every one. So `\G` is DOWNWARD-closed exactly like `\A` — every retreat moves
  TOWARD the one position that satisfies it — and possessifying deletes the
  retreat that is the only route to the match. Witness, measured:
  `(x)?a{0,4}\G` on `"aaaa"` answers `(0,0)` shipped and NO MATCH under `\z`'s
  arm (sabotage S84), which is D47.5's own failure mode one construct over.

  **[M6.2 wave E] `\K` is TRANSPARENT, and it is the one arm in `first_of`
  that needs no closure argument at all.** Every other zero-width kind here had
  to be classified by WHICH WAY its satisfying set is closed, because each can
  FAIL and the whole question is whether a retreat turns a failure into a
  success. `\K` cannot fail — it is an epsilon in the NFA — so "modelled as
  absent" is the fact rather than an approximation, and it takes A_EMPTY's arm.
  The tempting wrong worry runs the other way: possessifying a loop that
  CONTAINS a `\K` is also safe, because the cut discards retreat frames only
  after the loop has exited at its chosen count, and a trial iteration that
  failed has already had its `\K` write rewound by the fail label's trail
  rewind — so the writes surviving a cut are exactly the winning path's.

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

  **The verdict and the material for it are ONE FIELD.** `Ast.u.rep.revbody` holds the
  body's REVERSED AST and is non-NULL exactly when the rung applies, so the
  three emitter sites that must agree about the rung (`vm_cost_rep`,
  `vm_count_slots`, `vm_rep`) read one field rather than each re-deciding — and
  the site that selects the rung cannot select it without having the thing the
  rung needs. `Ast.u.rep.possessive`'s precedent, one rung down.

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

  **[M6.2 wave E] `\K` DECLINES, and it is the only decline in this file that
  is a CORRECTNESS requirement rather than a missed rung.** This rung suppresses
  the per-iteration capture writes and RECOVERS them afterwards by walking
  backwards over ITERATION BOUNDARIES (§3.4's derivation). A `\K` position is
  not on that lattice — it is wherever the winning path crossed it — so a
  suppressed `\K` write is one nothing ever recovers, and the artifact would
  report the wrong start silently. `rd_shape` declines the body, which makes
  `rd_reverse` and `rd_alt_disjoint` unreachable for it; `rd_reverse`'s arm
  ctx_fails LOUDLY rather than copying the node, because reversal is NOT
  identity for `\K` — the seven kinds it sits beside survive reversal because
  each is a PREDICATE, and `\K` is not one.

  Same two inheritances as possessify.c and for the same reasons. Every decision
  is in the SOUND direction, so anything unmodellable DECLINES and a declined
  quantifier matches exactly what it matches today — which is also what makes
  `-fno-revdet` byte-identity-safe. And A_CAT/A_ALT spines are walked
  ITERATIVELY (D10/DD-10/R1 R-2, K20): the REVERSAL is the harder half of that
  obligation, because reversing a spine means REBUILDING one, and a quantifier
  body is allowed to be a 20,000-element concatenation.

  Tests: tests/rungselect/ (its own CLAUDE.md explains why three separate checks
  are needed); failing-direction controls tests/mech/sabotages/S50-S52.

- **mrl.c** — [M4.6d] MINIMUM-REMAINING-LENGTH pruning's analysis half, and
  since [M6.6.2] wave A the WIDTH analysis in both directions

  **[M6.6.2 wave A] `pcrec_maxw` JOINED `pcrec_minw` IN THIS FILE, AND ITS
  SOUND DIRECTION IS THE OPPOSITE ONE.** Everything below about
  under-estimating being safe describes `pcrec_minw` alone. `pcrec_maxw` — the
  greatest number of subject bytes any match of a node can consume — may
  OVER-estimate for free, and an UNDER-estimate is its silent miscompile,
  because its consumer is the lookaround module's fixed-width rule
  (`lookaround_design.md` §2.5: a lookbehind branch is admitted only when
  `minw == maxw`, and the artifact then back-steps exactly that many bytes).
  Two functions, one arithmetic, opposite obligations — which is why each
  carries its own header saying which way it rounds. `PCREC_W_UNBOUNDED`
  (core/internal.h) is where rounding up runs out, and it is deliberately the
  SAME VALUE as `PCREC_MINW_MAX` so that unbounded ABSORBS through
  `mrl_sat_add` and, at `mrl_sat_mul(UNBOUNDED, 0)`, correctly collapses to 0
  for an unbounded repeat of a zero-width body.

  **[DD-14 wave B+C] `pcrec_minw`'s `A_CALL` ARM READS A VALUE OFF THE NODE**
  (`u.call.minw`), filled by `src/opt/callgraph.c`'s Kleene fixpoint from
  INFINITY DOWNWARD over the call graph. It is on the NODE rather than in a
  memo because this function's signature has no `Ctx` to reach one through and
  the only alternative is a file-static, i.e. a mutable global [TS-3] forbids.
  `minw == PCREC_MINW_MAX` means THE CALLEE MATCHES NOTHING, which is a LEGAL
  compile (`^(a(?1)b)$` compiles on 10.46 and matches nothing at any length) —
  read through this arm it makes the enclosing pattern's `minw` infinite, and
  the MRL prune reads that as "no position can match", so pcrec answers NOMATCH
  in constant time where 10.46 spends its own guard finding out. The pair that
  pins both directions is `tests/recursion/mrl.rxt`: infinity must be
  REACHABLE and must not be reached by an APPROXIMATION.

  **[DD-14.LB] `pcrec_maxw`'s ARM NOW READS A MEMO TOO, AND THE ASYMMETRY IS
  IN HOW IT READS IT.** The arm was `PCREC_W_UNBOUNDED` unconditionally through
  wave B+C — EXACT for a recursive callee (design §3.4(d) measured libpcre2
  refusing exactly that inside a lookbehind, error 125) and a sound
  OVER-estimate for every other, which is this function's safe direction. It
  now answers `u.call.maxw` when `u.call.maxw_known`, filled by a SECOND Kleene
  fixpoint in `callgraph.c`, `minw`'s mirror descending from
  `PCREC_W_UNBOUNDED`.

  **THE SECOND FIELD IS THE WHOLE ASYMMETRY.** `minw`'s memo needs no validity
  flag because the arena's zero (0) is its SOUND direction — an under-estimate
  prunes less and can never delete a live position — which is what lets
  `possessify.c` call `pcrec_minw` before the graph exists. `maxw`'s safe
  direction is the opposite one, so a bare `long long maxw` whose arena zero is
  0 would be a silent MISCOMPILE (an under-estimated maximum lets a
  variable-width branch through the lookbehind rule as fixed, and on a NEGATIVE
  lookbehind that is a false match). `maxw_known` is the arena-zero-safe half,
  exactly as `u.call.nonnullable`'s inverted polarity is: false means "answer
  `PCREC_W_UNBOUNDED`", which is what the arm answered before the memo existed.

  **AND WHAT MOVED WAS THE CONSUMER, NOT THE WRITER.** Wave B+C's objection to
  tightening this arm was a TIMING one and it was correct: the consumer, module
  `lookaround`'s fixed-width rule, runs in the PARSE HOOK — where it must, to
  refuse with a pattern offset — and the graph does not exist until every call
  is resolved. [DD-14.LB] answered it by re-asking the rule after the graph
  exists (`postresolve.c` below) rather than by trying to make the hook see
  through a call. The two cells the objection was written about are no longer
  parked: one compiles, and the other turned out to be a §2.5 capability limit
  the timing gap was masking (`tests/recursion/inlookaround.rxt`).

  **`pcrec_maxw`'s ONLY CALLER IS module `lookaround`'s width rule**, at BOTH
  of its timings now, so its own instrument is still `tests/mrl/maxw_check.c` —
  see that directory's CLAUDE.md for why the three existing instruments
  structurally cannot see it. Sabotage: S171 (the `maxw` fixpoint stopped after
  one round; DETECTED, 2fail/35pass, on the two-hop chain cell alone).

  **THE ONE THING A UTF-8 BACKEND MUST REVISIT.** `A_CLASS` answers 1 byte in
  both functions. For `minw` that is a deliberate LOOSE under-estimate and
  stays sound under any encoding; for `maxw` it is EXACT only because
  `PCREC_ENC_UTF8` has no backend and `src/core/compile.c:196` refuses it by
  name. When that refusal goes, `maxw`'s arm must become the encoding's
  maximum code-unit length or the fixed-width rule silently accepts
  variable-width branches. The two arms look identical and are not.

  **[M6.5.2] `A_BREF` CONTRIBUTES 0, and it is EXACT rather than
  conservative** — this file said so before the kind existed ("Lookaround,
  backreferences and `(*ATOMIC)` have no producers today; when they gain one,
  each contributes 0 here until someone measures otherwise"), and the measured
  answer is that 0 is right for a reason the other zero-width members do not
  share. They consume nothing EVER; a backreference consumes `ref_end -
  ref_start` bytes, a match-time quantity with no compile-time lower bound
  above zero — a group can publish an EMPTY capture, so 0 is genuinely
  attainable. Any positive value would be an OVER-estimate, this file's unsound
  direction.

  MEASURED on the emitted artifact rather than argued: `(a)\1{3}c` emits
  `RX_PRUNE_TOO_SHORT(scan_position, 1)` before the reference chain — the `c`
  alone, with all three references contributing nothing to the follow-min. That
  is the under-estimate, and it prunes less rather than deleting a live
  position. **The [M6.4] failure mode has no analogue here**: what crossed a
  cut there was a follow-BOUND carried into a loop past a construct that
  changes where the loop can end, and a backreference brackets nothing and
  bounds nothing — it contributes a term, and the term is the safe one.
  `EngineFit.prefilter` is false for these patterns, so `Vm.mrl_win` is false
  too and the ceiling stamps `subject-end` or `none` rather than a
  prefilter window.
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

- **scanedge.c** — [OPT-5] THE DFA SCAN EDGE: a counted class run stops
  being *m* table steps. Runs on every machine immediately after
  `pcrec_minimize_dfa` (it needs the canonical state set, and nothing after
  it rebuilds a `DState`), and it is the one pass in this directory that
  DELETES states rather than annotating or rewriting nodes.

  **THE MEASURED NEED** is `docs/dev/opt5_step0_profile.md`: the DFA's
  per-byte step is `state = next_state[state + class]`, whose load ADDRESS is
  the value the previous iteration's load RETURNED — pointer-chasing, 3.62
  ns/byte on an in-class letter run against 0.60 for pcrec's OWN VM on the
  identical language, flat across a 64x count range. The VM wins because its
  loop-carried register is a CURSOR. This pass gives the DFA that loop where
  a region of its state graph is doing nothing but counting; §7 of the
  profile is explicit that address-independence is the first-order fix and a
  SIMD run-extension stacks on top ([OPT-SIMD]), never instead.

  **THE CRITERION IS A PROPERTY OF THE TRANSITION TABLE, not of `{m,n}`.**
  Nothing here reads the AST or knows what construct produced the states: a
  SCAN-SHAPED state advances on one class and leaves by the SAME door on
  every other, and a chain is a maximal run of them sharing (class, exit,
  accept bit). `[a-z]{0,n}` is the simplest instance rather than a special
  case of one; `[a-z]*`/`[a-z]+` are the unbounded one-state form;
  `[a-z]{3,10}` is TWO chains because the exit target changes when the
  machine starts accepting; `[0-9]{4}-[0-9]{2}` has one per run. The
  two-class control `([a-z]|[0-9]X){0,8}` is left exactly as it is.

  **SEVEN PRECONDITIONS, EVERY ONE A DECLINE, and two of them were
  MEASURED rather than reasoned.** The file's header carries all seven; the
  two worth knowing before editing anything are (6) a chain head may not be
  any state's `eolvar`/`endvar` target — the emitted loop steps from the
  VIEW-SELECTED state, not from the state variable, so a view pointing at a
  head reaches the killed table cell with the edge never having run
  (`a{0,4}$`, 87 cells of tests/possessify/possessify.rxt, the right match
  END and the wrong START) — and (7) when one chain's fall-through is
  another's head the source must have the smaller state index, because the
  emitted blocks are plain `if`s in state order.

  **THE DELETION IS WHAT BUYS THE SIZE AND IT RESTS ON ONE CLAIM about the
  EMITTED loop**: when the ordinary step runs, the state variable never holds
  a chain head together with a byte of that head's scan class. The header
  spells out the four things that make it true (where the edge sits in the
  loop body, that it is its own `if`, that a head is excluded from
  `pick_skip_states`, and that the scan consumes what the bound allows).
  MEASURED: `[a-z]{0,16384}`'s forward machine goes from 16,385 states to 2,
  its artifact from 725,729 to 17,776 source bytes and 212,800 to 16,192
  `.so` bytes.

  `-fno-scan-edge` (`PCREC_NO_SCAN_EDGE`) gates the pass ITSELF, which is
  where the soundness half has to live: an emitter filter cannot put back
  states this pass removed. `src/gen/emit_dfa.c`'s axis H carries the same
  bit so `--list-axes` can name the flag that addresses the axis; one bit,
  two readers. Tests: the answer corpora it reaches (counterk, classes,
  bounded_repeats, possessify, k18_*), `docs/spec/tuning.md` §2.18;
  sabotage rows S213 (the criterion's exit-uniformity clause) and S214 (the
  emitted loop's count bound), with DISJOINT detectors.

- **minimize.c** — DFA minimization by Moore-style partition refinement with
  signature hashing. The EOL-view edge (`eolvar`) participates as an extra
  alphabet symbol so `$`-machines minimize correctly, and since [M6.2] wave A
  the END-view edge (`endvar`, `\z`'s) as a second one. **The two are not
  symmetric**: `eolvar == -1` means "self" while `endvar == -1` means "same as
  the EOL view", so both edges are RESOLVED through that chain before entering
  a signature and re-canonicalized against the resolved target on rebuild.
  **[M6.2 wave B]**: the INITIAL PARTITION splits on BOTH accept bits
  (`accept*2 + waccept`), because a state has two independent accept outputs
  once `\b` exists — the bit for "the next byte is a word character" and the
  bit for "it is not" — and merging states that agree on one and differ on the
  other would answer a `\b` with the wrong bit at every position of the right
  kind. The TRANSITION axis needed nothing added, which is the payoff of
  baking the word view into `tr[]` rather than interning it (src/ir/CLAUDE.md).
  `Dfa.s1w` remaps alongside `s0`/`s1`; forgetting it would leave mechanism
  4's seed pointing into the PRE-merge numbering — a wrong start state rather
  than a missing one, on every pattern that minimizes, which is most of them.
  **[M6.2 wave D]** `Dfa.s1g[]` — `\G`'s own start family — remaps in a SECOND
  loop for the identical reason. The two loops are written out rather than
  merged over a pointer array because they are independent arrays each holding
  its own pre-merge id, so each is translated exactly once even on a `\G`-free
  machine where every `s1g[u]` happens to equal the `s1u[u]` beside it.
  Byte-identity survives because the key is handed out in first-occurrence
  order and only two of its four values occur without a word context.
  Byte-identity on `\z`-free patterns holds by construction rather than by a
  conditional — with every `endvar` at -1 the appended signature column is a
  duplicate of the one before it, and a duplicated column cannot change a
  partition. Behavior-preserving:
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

## [DD-14 wave G] The splice linkage, and the two predicates it added

**`callgraph.c` DECIDES THE LINKAGE.** `cg_eligibility` sets
`Ast.u.call.link = CALL_SPLICE` iff the target is not in a cycle
(`reaches(i, i)`) AND the spliced expansion fits `PCREC_MAX_SPLICE_NODES`, with
the expansion COMPOSING over nested splices (`exp(i) = nodes(body[i]) + SUM_j
site[i][j] * (splice(j) ? exp(j) - 1 : 0)`), evaluated cycles-first then over
the DAG and saturating so that "too big to count" declines like "cannot be
counted". A second budget bounds the SUM. The decision is per TARGET, not per
site, and the function says why that is a choice rather than a necessity.
`-fno-splice-calls` (`PCREC_NO_SPLICE_CALLS`) returns before any of it, so the
denied build is EXACTLY the artifact wave B+C shipped — which is what makes it
design §9.2's control rather than a fourth variant.

**AND THE PASS ORDER MOVED, ONCE.** `pcrec_discharge_atomic` is hoisted out of
`pcrec_select_engine` into `src/core/compile.c`, right after `pcrec_altcls`.
That is what makes two constraints satisfiable together: the call graph must run
AFTER every pass that REBUILDS a node (callgraph.c's own header argument), and
ENGINE SELECTION must now run AFTER the call graph, because the linkage is what
selection reads. The hoist also fixed a latent drop — `select_engine` assigned
the discharged root to a LOCAL, so a discharge at the very root was thrown away.

**`atomic.c` GAINS TWO TREE PREDICATES**, both beside `pcrec_has_call` for this
file's standing reason:

- `pcrec_has_linked_call` — `pcrec_has_call`'s NARROWING. §8.1's "not regular"
  and §8.2's "erasure is a different language" are both arguments about a call
  with NO FINITE INLINING; a spliced call has one and it is exact. Reads
  `u.call.link`, so it is meaningful only AFTER `pcrec_callgraph_build` — which
  is why that pass moved ahead of selection.
- `pcrec_has_live_capture` — the DEAD-CAPTURE ELISION. A group is dead when no
  emitted code can WRITE it: its only occurrence sits under an `A_REP{0,0}`
  (which emits nothing) and a call to it is capture-transparent (design §3.1,
  MEASURED through the live ovector). **NOT a `DEFINE` rule** —
  `(?(DEFINE)...)`, `(?:...){0}` and `(a){0}b` are one structural situation, and
  a DEFINE-shaped special case would have been a parallel mechanism for two
  thirds of its own population. Its polarity is named for the safe answer:
  over-reporting liveness costs an engine, under-reporting loses a capture.

**`select_engine.c` READS BOTH.** `forces_captures` consults the second (so an
all-dead pattern is DFA-eligible), the prefilter predicate consults the first,
and `first_dfa_excluding` exempts a `CALL_SPLICE` node BEFORE the generic SR-8
row test — which is `(?>`'s per-row-conservative/per-pattern-true gap closed by
the LINKAGE instead of by a deletion, because deleting a call means copying its
callee's `A_CAP` nodes into the tree.

Maintenance: update this file when passes are added/removed.

## [OPT-4.1] the nullability predicate — ONE derivation, THREE readers

`select_engine.c`'s fit site writes `EngineFit.prefilter_lang_nullable` as
`pcrec_minw(root) == 0` and nothing else in the tree computes that fact. Three
sites read it: the `fit.prefilter` clause in this file (a collapse RUNG's
rescue is DECLINED, and what stands in its place is no prefilter at all — on a
rung the alternative to the collapsed machine is not the exact one, because
the exact machine is what failed), `src/core/compile.c`'s build gate (under
`-fprefilter-collapse` the collapse is declined and the EXACT prefilter is
kept), and the `--emit-ir` listing's `; prefilter` line, which would otherwise
name a FLAG the caller did not pass as the reason an artifact has none.

**IT IS `src/opt/mrl.c`'s EXISTING WIDTH ANALYSIS AND NOT A SECOND WALK.**
`pcrec_minw` already answers for the PREFILTER's lowering rather than for the
pattern's semantics — `A_CAP`/`A_ATOMIC` transparent as `src/ir/nfa.c` lowers
them, `A_LOOK` 0 as the prefilter lowers it (to epsilon), `A_CALL` off the
callgraph fixpoint, which `compile.c` has already run by the time selection
asks. Its documented direction is UNDER-estimation, so `minw == 0` may claim
nullable where the true language is not, and that direction is the safe one
here: declining a rescue costs a filter, never an answer.

**AND THE COLLAPSED LANGUAGE'S NULLABILITY IS THE EXACT PATTERN'S**, which is
why the field is not called `collapsed_lang_nullable`. The collapse rewrites
`X{m,n}` as `X{min(m,1),}`, and `min(m,1) == 0` iff `m == 0`, so an `A_REP` is
nullable on exactly the same condition before and after; concatenation and
alternation combine 0-ness identically. One walk answers for both languages.

**THE MEASURED NEED** is pcrec-bench O-10 item 3 at pin 96e44c2: where
structure survives the collapse the rescue wins 2.2-4.6x, and where the
collapsed language is nullable it LOSES 1.2-9.9x, because the filter admits a
zero-length match at every position and can dismiss nothing. `-fprefilter`
is do-or-die and is never silently dropped, and what that means differs by
RUNG: on the SIZE rung it OVERRIDES the decline (its alternative there is no
prefilter, which that flag forbids), while on the [SEL-1] rung it makes the
rung ineligible so the decline is never reached and the compile REFUSES.
`-fprefilter-collapse` overrides on neither, because it chooses a LANGUAGE and
not whether a filter exists. `docs/spec/tuning.md` §2.17 is the
contract.

## [OPT-4.2] the decline generalizes off the rung — ONE PREDICATE, TWO SCOPES

[OPT-4.1]'s decline above is scoped to a ladder ATTEMPT
(`cx->collapse_reason != CR_NONE`): it only ever fires while a RUNG is
offering the count-collapsed rescue. The ORDINARY hybrid — `auto` (or forced
`--engine=vm` plus `-fprefilter`) with no cap ever hit — still built its
pattern's own EXACT prefilter unconditionally, nullable or not, which is
exactly the same defect one door over: `(a)*`'s own language matches the
empty string (no collapse involved at all — this is not a repeat the
collapse touches), and its prefilter could never dismiss a position either.
The population that reaches this path GREW when [OPT-5]'s scan edge landed:
`(a|b){0,30000}`-family patterns that used to be SIZE-REFUSED (and so took
the [OPT-4] size rung's own decline above) now compile inside every cap and
never reach a rung at all.

`select_engine.c`'s fit site derives ONE shared local,
`lang_nullable_declinable` (`prefilter_lang_nullable && !has_bref &&
!has_call && !force_on` — the exact conjuncts [OPT-4.1]'s field above
already had, minus `prefilter_has_collapsible_rep`, which is meaningless off
a rung: the ordinary path never collapses anything, so there is always a
concrete prefilter to decline), and reads it into BOTH declines:

- `prefilter_declined_nullable` (unchanged) additionally needs
  `collapse_reason != CR_NONE` and `prefilter_has_collapsible_rep` — a rung
  ran and there was a distinct rescue to refuse.
- `prefilter_declined_nullable_default` (new) additionally needs
  `collapse_reason == CR_NONE` and `would_prefilter` — a LOCAL answering "is
  `fit.chosen == ENGM_VM` and would this compile actually have built a
  prefilter, absent the decline" (the same condition the final `fit.prefilter`
  ternary falls through to), further guarded by `!cx->dfa_disabled` so the
  decline cannot fire on a retry whose OWN prefilter construction overflowed
  with no rung offered (`ESEL_OVERFLOWED_DFA`/`_PREFILTER`'s own population —
  the r47sel-1 false-stamp shape one level over: without the guard, a DFA
  build that genuinely had nothing to offer would stamp "a rescue was
  refused" instead of "nothing survived").

The two fields are MUTUALLY EXCLUSIVE by construction (one requires
`collapse_reason != CR_NONE`, the other its negation) and get their own
`ESEL_DECLINED_NULLABLE_DEFAULT` value (internal.h) rather than sharing
`ESEL_DECLINED_NULLABLE` — the K35 "closed value set silently losing a
member" shape: a rung OFFERED and REFUSED a rescue is a different population
from an ordinary compile that never had a rung to begin with, and the bench
buckets on `RX_ENGINE_SEL` precisely because it cannot bucket on prose.
`internal.h`'s own enum comment carries the placement argument (why the new
value sits adjacent to `ESEL_SELECTED` rather than appended after
`ESEL_SIZE_CAP_RETRY`); `docs/spec/tuning.md` §2.17 and `match_api.md` §6.3
are the caller-facing contract. `tests/resource`'s `(a|b){0,30000}` cell and
`tests/prefilter`'s `(a)*` witness are the two populations
(size-cap-rescued-then-declined-anyway vs. never-capped-at-all).
