# src/core — pipeline driver and memory management

Home of the compilation pipeline driver and shared utilities: arena allocator for AST/IR, growable string buffer for codegen output, shared type definitions, and longjmp error handling.

## Files

- **compile.c** — pcrec_compile() pipeline driver (parse → SELECT ENGINE →
  NFA → DFA → emit);
  ctx_fail error handler; pcrec_default_options defaults; and
  pcrec_count_groups(), the parse-only entry behind the CLI's
  `--count-groups` (MOD-0.1/§18.1 — reports Ctx.ncap's end-of-parse value
  with pcrec_compile's exact refusal behaviour; it lives here because this
  file holds the tree's ONLY setjmp)
  **[OPT-ALTCLS] (2026-08-17)** the pipeline gains a THIRD thing, ahead of
  the two below: immediately after `pcrec_parse`, `root = pcrec_altcls(&cx,
  root)` runs the alternation->class normalization pass
  (`src/opt/altcls.c`) and REPLACES `root` with its (possibly rewritten)
  result, before `pcrec_select_engine` or anything it drives ever sees the
  tree. Placement is load-bearing, not incidental: possessify/revdet/mrl and
  both machine builds all analyze SHAPES the pass may have merged or
  factored, and re-analyzing the alternation spelling instead would miss
  exactly the wins the plan row measures (a merged class collapsing the VM's
  cursor rung, the DFA's byte-equivalence-class table). Self-gated on
  `PCREC_NO_ALTCLS_MERGE`/`PCREC_NO_ALTCLS_FACTOR`; `Job` gains
  `altcls_merges`/`altcls_factored`, the D46 stamp source read by BOTH
  emitters (src/gen/emit_dfa.c's shared `pcrec_emit_prologue`) since this
  pass runs before either engine exists.

  **[M5-SEAM] (2026-08-18, D58)** the ENCODING GATE is now a REGISTRY
  lookup rather than a pair of `PCREC_ENC_*` comparisons with the names
  written out in literals: `pcrec_enc_by_id` (src/gen/enc/) resolves the
  requested value, a value that is not a namespace member at all is refused
  with the table's rendered menu, and a member with no backend yet is
  refused BY ITS OWN `name`. That is [SR-10]'s single-namespace rule on the
  half this gate owns, and its motivating instance was exactly this
  diagnostic and cli/main.c's name mapping drifting apart. The K14-shaped
  wording below is unchanged and still applies — the promise names the
  MILESTONE, not a module the namespace lacks.

  **[M4.5b]** the pipeline gained two things. Engine selection moved OUT of
  this file's inline `if` into a pass (src/opt/select_engine.c) that runs
  after parse and BEFORE machine construction, so a `--engine` request pcrec
  cannot honour is diagnosed without paying for an automaton first; and the
  DFA pair is now built CONDITIONALLY — when the DFA is the engine, or when
  the VM wants it as its prefilter, but NOT for `--engine=vm`, where
  engine_m4.md §5.6/D44/R21 E-6 turns the prefilter off. That last case is
  why the build is skipped rather than merely ignored: `--engine=vm` is meant
  to be an INDEPENDENT second derivation of the match span, and an
  independence you get by not consulting an answer you did compute is weaker
  than one you get by never computing it. `Ctx.want_caps` (seeded from
  PCREC_NO_CAPTURES) and `Ctx.first_cap_pos` are seeded here too, and cleared
  for pcrec_count_groups, which emits nothing.

  **[M4.5c]** `pcrec_compile` and DD-8's `pcrec_emit_ir` are now two thin
  callers of ONE driver, `compile_driver`, differing in a single bool. The
  fork is the thing to avoid on principle (M2.12's `$`-engine fork is the
  standing example) and here it would also break engine_m4.md §10's constraint
  at the pipeline level: a listing produced by a second driver would describe
  a compile that never happened. `--emit-ir` therefore runs a REAL compile and
  throws the C away — the cost of the guarantee, on a debug tool.

- **fold.c** — THE ASCII CASE-FOLD PARTITION AS ONE OBJECT ([M6.5.2], D23,
  R32 E8). `pcrec_ascii_fold[c]` is c's case PARTNER, or c itself when it has
  none: exactly the 52 ASCII letters, each with one partner, and no byte
  >= 0x80 (MEASURED over all 256 bytes against libpcre2's 8-bit non-UTF build,
  and re-measured against pcrec's own class fold at zero disagreements).

  **It exists because the fold has to exist TWICE and cannot be made to exist
  once.** Until module `backrefs` it had one consumer: `cls_casefold` in
  src/parse/parse.c, which WIDENS a class bitmap at parse time so the emitted
  matcher has no flag, no branch and no `tolower()` (D23). A caseless
  BACKREFERENCE cannot fold at parse time — its operand is subject text nobody
  has seen — so the fold appears a second time inside the encoding residual
  `$_bref_match_caseless` (src/gen/enc/enc_byte.c), which is TEXT compiled by
  someone else's toolchain and cannot call a `static` function here. Two
  spellings of one fact with nothing between them is the shape this project
  keeps cataloguing; this table is what
  `tests/backrefs/fold_agreement_check.c` ties the two to, over all 65,536
  ordered byte pairs, with the residual side read out of an artifact pcrec
  actually emitted. `cls_casefold` derives its widening from it, so the
  parse-time fold IS this table by construction.

- **arena.c** — zeroing arena allocator; 16-byte aligned blocks, minimum 64KB per block.
  **[M4.7b/K7]** carries a `Ctx *cx` back-pointer, and a failed malloc now
  calls `ctx_nomem()` instead of `abort()`. That one pointer is K7's worst
  half: pcrec is a LIBRARY, and aborting kills the CALLER's process — the
  outcome a caller who set a memory limit was specifically trying to avoid.
  The longjmp lands in compile_driver, whose `job_cleanup` already freed
  everything wholesale, so nothing leaks and nothing half-built is read again
- **sb.c** — growable string buffer for C code emission; sb_putc, sb_puts, sb_printf.
  **[M4.7b/K7]** same back-pointer, with one real difference from Arena's:
  NULL is a legitimate state here. `src/parse/syntax_dump.c` builds
  `--features`/syntax-query text in bare `StrBuf sb = {0}` locals belonging to
  no compile, with no `pcrec_error` to report through, so those keep the
  abort. `sb_grow` also reallocs into a temporary now — assigning a failed
  realloc straight into `sb->p` would lose the only pointer to the live buffer
  the error path is about to free
- **limits.h** — every number that decides what pcrec ACCEPTS, REJECTS or
  PROMISES, in three sections that ARE D26's tiers: ours (free to tune), PCRE2
  syntax (exact, and measured — the 65535 repeat ceiling, the 250 nesting cap),
  and PCRE2 internals (minimums we honour, not contracts we owe). The
  provenance is the point: a bare `250` and a bare `60` look alike and are not.
  Structural constants (256 byte values, block sizes, growth factors) and local
  algorithmic bounds with proofs beside them stay where they are, deliberately —
  see the file's own inclusion rule before adding to it.
  **[M4.7b] adds `PCREC_MAX_SUBSET_ELEMS`**, K7's second half and the first
  bound in this file on what the COMPILER spends rather than on what it emits
  (every other one is grounded in emitter cost, R1 A-3, and those are
  structurally blind to a cost paid before emission): how many NFA-state-list
  elements the subset construction may intern across a compile. The state-COUNT
  caps cannot substitute, because the two diverge by a whole factor on the
  exact-repeat family — n+1 states whose state-SETS average n/2. Read its entry
  before touching the number: it records the corpus maximum it is derived from,
  the measured cost at the ceiling, the exact repeats it NARROWS
  (`a{9795}` compiles, `a{9796}` refuses), and the raise-to-restore lever with
  a measured price at three points.
  **[M6.3] adds `PCREC_MAX_GROUP_NAME`** (128), the PCRE2-syntax-tier cap
  on a named group's name length — measured against libpcre2 10.46
  (tests/probes/probe_named_groups.c, swept 1..2000 bytes, exact wall at
  129, PCRE2 error 148), not carried over from PCRE1's older 32-byte
  convention
- **internal.h** — shared data structures: Arena, StrBuf, Ctx, Nfa, Dfa,
  **[M4.5b]'s `A_CAP` AST node and `EngineFit`**, the
  syntax construct registry types (RegRow and its FEAT_/FLAV_/ENGM_/RS_/RD_
  vocabulary, D24), the `(*` doorway's NAME tables (VerbName/VerbTable and the
  VF_* form bits, D25/Q1 — a SECOND schema on purpose, because a verb name
  answers one externally-measured question while a RegRow carries a module, a
  feature bit and an engine mask it would have to invent), the POSIX
  class-bracket NAME table (PosixName, MOD-0.3a — a third schema, per-name
  module attribution), the doorway vocabulary (ExtWhat/ExtWant/ExtResult,
  moved above RegRow at MOD-0.3b when ports embedded it) with the ExtPort
  producing-port types, and module-level declarations.

  **[M6.6.2 wave 0, D70] `struct Ast` IS A TAGGED UNION.** The per-kind fields
  live in `union { ... } u`, keyed by the existing `AKind k`:
  `n->u.cls.bits`, `n->u.rep.{rmin,rmax,greedy,possessive,revbody}`,
  `n->u.cap.no`, `n->u.anch.multiline`, `n->u.bref.{refs,nrefs,caseless}`.
  `k`, `l`, `r`, `not_repeatable` and `reg` stay COMMON.

  **[M6.6.2 wave A2] THE FIRST MEMBER ADDED UNDER THE RULE IS `u.look`**
  (`A_LOOK`: `behind`, `neg`, `atomic`, `widths`, `nbranch`), and it is worth
  reading as the worked example the rule was written for. The design's own
  sketch (`lookaround_design.md` §3.1) proposed FIVE new TOP-LEVEL fields, one
  of them an `int look_widths[]` FLEXIBLE ARRAY MEMBER. D70 refuses both
  halves: they go in a member, and the width table is an arena `const int *`
  because a flexible array cannot live in a union, cannot be preceded by
  another member, and would make `sizeof(Ast)` a lie for the zeroing arena
  that allocates every node at one fixed size. The union member is 24 bytes
  against `u.cls.bits`'s 32, so `sizeof(Ast)` is unchanged. The rule D70 makes
  operative: **no module may add a new top-level per-kind field** — a new kind
  adds a union MEMBER, and a field joins the common block only when a survey
  MEASURES it cross-kind. The union buys reading and containment, NOT
  checking: C does not police member access, so D62's discipline (parse-
  resolved state, per-field comments, per-field sabotage rows) is unchanged.

  **[DD-14 wave A2] THE SECOND MEMBER ADDED UNDER THE RULE IS `u.call`**
  (`A_CALL`: `target`, `body`, `link`, `nsave`, `save`, plus a new `CallLink`
  enum beside `AKind`), and it is the first member holding a POINTER INTO THE
  SAME TREE. `u.call.body` is the resolved callee subtree — **SHARED, never
  owned** — which makes it the AST's first `Ast*` -> `Ast*` back edge and puts
  a second obligation on every generic helper beside D70's own:

  | generic helper | what it does with `u.call` | why |
  |---|---|---|
  | `src/opt/revdet.c` `rd_node` (the reversal copy constructor) | **never reached with one.** Its `*n = *src` shallow-copies the union, so an `A_CALL` copy would keep a valid `u.call` and a `body` pointer into the FORWARD tree — the most plausible-looking wrong node in the file. `rd_reverse`'s own `case A_CALL:` `ctx_fail` stops it before the tail fallthrough, and `rd_shape`'s decline stops `rd_reverse` being called at all. Its `n->k == A_REP` guard already keeps the `revbody`/`possessive` clear off `u.call`. | a shallow copy is right for every kind it DOES copy; a call is not one of them |
  | `src/opt/altcls.c` `altcls_walk`'s `*r = *a` (A_REP and A_CAP only) | **never runs on an `A_CALL`**: both copies are under an explicit kind arm that owns `u.rep`/`u.cap`, and the new `case A_CALL: return a;` returns the node itself. A copier that FOLLOWED `.body` would duplicate the callee and give one call site a private copy of a subtree the rest of the tree shares. | D70's kind-check rule, already satisfied |
  | `src/parse/mod_assertions.c`'s multiline pin | **cannot reach it** — guarded `k == A_BOL \|\| k == A_EOL`, and that port produces no `A_CALL`. | the guard the D70 migration added |
  | `src/opt/atomic.c` `dis_walk`, `src/parse/mod_backrefs.c` `br_strip_caps` (the two tree REWRITES) | **visit the node as itself and never follow `.body`.** Following it would discharge / strip the callee once per call that names it, rewriting `a->l` on nodes another part of the tree points at, and would not terminate on a recursive callee. | design §4.4 |
  | `--emit-ir`'s listing | **no `AKind` arm exists to write.** The listing renders the `VEvent` stream the emitter records (`emit_vm.c` switches on `VEvent.k`), so a call's listing content is whatever wave B+C's `RX_CALL`/`RX_RETURN` emission records as events — the same finding `u.look` reached. | measured, not assumed |

  **THE RULE THE MEMBER ADDS**, beside D70's own: a generic helper must not
  merely GUARD `u.call` — it must not FOLLOW `.body`. A whole-tree walk
  already visits the callee at the callee's own lexical position, so following
  the edge is redundant, and on `(a(?1))` it is a non-terminating compile in a
  predicate asked of every pattern. A genuinely subtree-relative analysis goes
  through `src/opt/callgraph.c`'s memoised SCC fixpoint (wave B+C).
  `sizeof(Ast)` is unchanged: the member is 32 bytes on LP64, which is
  `u.cls.bits`'s own 32.

### [DD-14 wave A2] The EIGHT SWITCH-LESS WALKERS, inspected

  `subroutines_design.md` §4.4a's census is `switch`-shaped, which is exactly
  the set `-Wswitch` covers **and exactly the set it covers, no more**. The
  residual it names is 72 further `->k ==` dispatch points and **eight AST
  walkers with no kind switch at all**. The design assigns their arms to wave
  B+C; wave A2 was the wave with the tree open, so each was READ and its
  behaviour on an `A_CALL` recorded. **NONE needs a guard, and none can be
  reached in wave A2 anyway (no producer).**

  | walker | what it does with an `A_CALL` today | guard needed? |
  |---|---|---|
  | `emit_vm.c` `vm_lifts` | its argument is an `A_ATOMIC`; `r->k != A_REP` DECLINES the lift for a call body. If the body is `A_REP((?1))` it declines again through `vm_nullable(r->l)`, which answers `true`. | no — but B+C must re-read it once `vm_nullable` becomes the graph fixpoint, because the lift of `(?>(?1)*)` then depends on the CALLEE's nullability |
  | `emit_vm.c` `bare` | `while (k == A_CAP)` — stops AT the call and returns it. A call is not transparent to anything. | no |
  | `emit_vm.c` `vm_alt` | flattens the `A_ALT` spine and hands each branch to `vm_emit`. A call branch reaches `vm_emit`'s arm — `ctx_fail` today, `vm_call` in B+C. Generic in the branch kind. | no |
  | `nfa.c` `trie_key` | requires every spine leaf to be `A_CLASS`; an `A_CALL` leaf makes it return false (INELIGIBLE). Dead for a call-bearing pattern anyway once wave E forces the prefilter off. | no |
  | `nfa.c` `ast_bare` | `while (k == A_CAP)` — stops at the call, `bare`'s answer. | no |
  | `altcls.c` `altcls_walk_alt` | flattens `A_ALT`, calls `altcls_walk` per branch (which now has an explicit `case A_CALL: return a;`), then merges only RUNS of `A_CLASS` branches — a call breaks the run. | no |
  | `altcls.c` `altcls_branch_peel` | requires the branch's FIRST flattened atom to be a single-byte `A_CLASS`; a leading call DECLINES. A call later in the branch is carried through `altcls_rebuild_cat` **by pointer**, never copied. | no |
  | `altcls.c` `altcls_cat_flatten` | a pure spine flattener with no kind assumption; a non-`A_CAT` node is a length-1 spine of itself. | no |

  **AND THE INSPECTION FOUND SOMETHING THE SWITCH CENSUS COULD NOT — A PASS
  ORDERING HAZARD FOR `u.call.body`, WHICH THE DESIGN DOES NOT ADDRESS.**
  `.body` is filled by the end-of-parse resolution pass (`pcrec_bref_resolve`,
  called at the END of `pcrec_parse`, parse.c). **Two later passes REBUILD
  nodes rather than mutating them**, so a pointer captured at resolution can
  be left naming a subtree that is no longer in the tree:

  - `pcrec_altcls` (`src/core/compile.c`, immediately after parse) allocates
    NEW nodes: `altcls_walk`'s `A_REP`/`A_CAP` arms do `*r = *a; r->l = body;`,
    and stages 1 and 2 rebuild spines and merge branches into a fresh
    `A_CLASS`. On `((?:a|b))(?1)` the tree's group 1 becomes a NEW `A_CAP`
    over `[ab]` while `.body` still names the OLD one over the alternation.
  - `pcrec_discharge_atomic` (via `pcrec_select_engine`) SPLICES an `A_ATOMIC`
    out, so a callee whose root was that node is reached through `.body` with
    the cut still in it.

  The consequence is not academic: under `CALL_LINKAGE` the callee REGION is
  emitted from `.body` while the lexical occurrence is emitted from the new
  node — two different programs for one group — and §4.4c computes `W` and the
  region's slot INDICES over whichever one it was handed. **WAVE B+C OWES ONE
  OF THREE ANSWERS**: resolve `.body` AFTER the rewriting passes, have every
  rewriting pass update it, or exempt callee subtrees from rewriting. Note
  `possessify` and `revdet` are NOT in this list — they annotate fields on the
  SAME nodes, so `.body` sees their results. Nothing is reachable in wave A2
  (no producer), which is why this is recorded rather than fixed here.

### The D70 ownership survey

  Every read and write of every non-`k`/`l`/`r` field of `struct Ast` across
  `src/`, `cli/`, `lib/` and `tests/**/*.c`, classified by the kind(s) the
  site is reasoning about. Recorded here because D70's "Revisit when" clause
  depends on the measurement existing. `Ast` turned out to be confined to 20
  files, all under `src/` — `cli/`, `lib/` and the test C drivers never touch
  it, so the whole migration surface was 231 lines / 249 occurrences.

  | field | kind(s) the sites reason about | Ast sites | disposition |
  |---|---|---|---|
  | `cls[32]` | A_CLASS | 25 | `u.cls.bits` |
  | `rmin` | A_REP | 61 | `u.rep.rmin` |
  | `rmax` | A_REP | 54 | `u.rep.rmax` |
  | `greedy` | A_REP | 28 | `u.rep.greedy` |
  | `possessive` | A_REP | 14 | `u.rep.possessive` |
  | `revbody` | A_REP | 5 | `u.rep.revbody` |
  | `capno` | A_CAP | 21 | `u.cap.no` |
  | `multiline` | **A_BOL + A_EOL** (closed family) | 8 | `u.anch.multiline` |
  | `refs` | A_BREF | 5 | `u.bref.refs` |
  | `nrefs` | A_BREF | 6 | `u.bref.nrefs` |
  | `caseless` | A_BREF | 4 | `u.bref.caseless` |
  | `not_repeatable` | **CROSS-KIND** | 5 | stays COMMON |
  | `reg` | **CROSS-KIND** | 5 | stays COMMON |

  - **`multiline` is a FAMILY, not one kind.** A_BOL and A_EOL share the
    meaning and the reads (`src/ir/nfa.c` `compile_ast`, `src/gen/emit_vm.c`
    `vm_emit`, `src/opt/possessify.c` `first_of`), so they share ONE payload
    named for the family rather than getting a member each.
  - **`not_repeatable` is genuinely cross-kind**, which the survey had to
    answer rather than assume. It is WRITTEN on A_EMPTY (a bare option run,
    `mod_modifiers.c`), PROPAGATED onto A_CAP and A_ATOMIC from their bodies
    (`parse.c`, `mod_named_groups.c`, `mod_atomic_groups.c` — and the `body`
    it reads is an atom of ANY kind), and READ off an atom of any kind by
    `parse.c`'s quantifier check. No union member could hold it.
  - **`reg` is cross-kind by construction** (D67): `pcrec_ast_stamp` writes it
    for any producer's node and `pcrec_ast_engines()` reads it for any node,
    regardless of `k`. It was expected to be common and the survey confirms it.

### The THIRD disposition shape: a generic helper sanitising a per-kind field

  The survey went looking for two dispositions — per-kind (a union member) and
  cross-kind (a common field) — and measured a THIRD, which is where both of
  this refactor's hazards live. A field can be per-kind in every READ and
  still be WRITTEN unconditionally by a generic copy or sanitise helper that
  runs for kinds it never enumerates. Before the union such a write is merely
  DEAD; after it, it is a write through the wrong union member onto whatever
  payload the node actually owns.

  | site | field(s) | kinds it ran for | disposition |
  |---|---|---|---|
  | `src/opt/revdet.c` `rd_node` | `revbody`, `possessive` | **every** kind `rd_reverse` copies | union member + **KIND GUARD** |
  | `src/parse/mod_assertions.c` port | `multiline` | all **eight** of the port's rows | shared `u.anch` + **KIND GUARD** |

  **`rd_node` was the live one, and the miscompile is MEASURED.** It is the
  reversal copy constructor for every kind `rd_reverse` handles — A_CLASS,
  A_EMPTY, the six position predicates, A_CAP, A_REP, A_CAT, A_ALT, plus the
  function-tail fallthrough — and it unconditionally cleared two A_REP-only
  fields on all of them. The arithmetic: the union sits at `+40` and
  `u.cls.bits` spans `+40..+71`, so through `u.rep` the clear writes
  `possessive` at `+49` (class bitmap BYTE 9, i.e. bytes `0x48`-`0x4F`, `H`-`O`)
  and `revbody` at `+56..+63` (bitmap BYTES 16-23, `0x80`-`0xBF`). On a
  reversed A_CLASS node it therefore ZEROES the body's membership for those
  ranges.

  What that costs, measured on the unguarded build: the reversed body's class
  tests compile to an all-zero `rx_class_bitmap[32]`, the backward walk can
  never take them, and **the LAST ITERATION'S CAPTURES — the thing
  `u.rep.revbody` exists to recover — come back UNSET**. `((H)|I){3}J` on
  `"HHHJ"` reports groups `(-1,-1)(-1,-1)` where both this compiler and
  python3 `re` give `(2,3)(2,3)`; `((I)|J){2}K` on `"IJK"` and
  `((H)|b){0,4}c` on `"HHc"` are the same shape. **The whole-match span is
  unchanged in every case**, which is why a span-only driver sees nothing.

  It is now guarded on `n->k == A_REP`, behaviour-preserving because those
  values are only ever read for A_REP.

  **THE CORPUS COULD NOT SEE IT, AND THAT GAP IS NOW CLOSED** — the finding
  that came out of using the real hazard as the identity gate's positive
  control. With the guard removed the gate first reported **zero differences on
  all four axes**: exactly 44 corpus patterns took the reverse-deterministic
  rung and every one was spelled in lowercase ASCII, so not one had a bit in
  either clobbered range. The population could not express the bug.

  `tests/rungselect/revdet_highbytes.rxt` closes it: 7 patterns / 127 cases
  with class bits in BOTH ranges (`H`-`O` for bitmap byte 9;
  `\x80`-`\x8f` and `\xb0`-`\xb2` for bytes 16-23), every one verified to take
  the rung via the `RX_VM_RUNGS` / `PCREC_VM_RUNG_REVDET` (0x8) stamp, every
  expectation agreed by python3 `re` AND libpcre2. **Its `g` capture lines are
  the detector** — the match span is unchanged under the bug, so an `m`-only
  file would pass and certify nothing. Measured: 61 of its 127 cases fail
  under the unguarded build, 0 under the guarded one; the identity gate now
  goes red at 7 differing on default/vm/noprefilter (`--no-captures` reports 0
  and correctly so — under that flag the `A_CAP` nodes are never born, so the
  corrupted reconstruction is not emitted). Mech row **S121** is the permanent
  detector.

  **The assertions pin was the latent one, and is guarded too** rather than
  merely recorded. It writes `u.anch.multiline = false` for all eight of the
  port's rows, i.e. also on A_END, A_WORDB, A_NWORDB, A_GSTART and A_KRESET.
  Today those five kinds have no payload, so it aliases nothing — but the day
  any of them gains one it becomes a silent clobber, and nobody will re-read
  that line then. The deliberate, forward-looking comment is kept verbatim
  above the guard.

  **THE RULE THIS YIELDS**, stated at the union in `internal.h` and repeated
  here because it is the thing a future author needs: a writer may touch
  `u.<payload>` only under a kind check that owns it, and a generic copy or
  sanitise helper MUST guard rather than write unconditionally. Those two are
  the only such sites in the tree today; the shape to grep for is a helper
  that takes a node of unconstrained kind and assigns a per-kind field.

  **`A_CAP` and D31 ([M4.5b]).** D31 ruled the group erasure STAYS, on a
  MEASURED compile-time cost; engine_m4.md §11.3 records that the VM
  nonetheless needs SOME node to know where to emit a capture write. Both
  hold at once, and the reason is worth reading before touching either: the
  node is BORN ONLY WHEN CAPTURES ARE REQUESTED (`Ctx.want_caps`), and it is
  TRANSPARENT to every consumer but the VM emitter (`ast_bare` in
  src/ir/nfa.c). So a capture-free pattern's AST is byte-identical to D31's
  always, `--no-captures` reproduces D31's AST for any pattern, and the
  prefilter machine built for a capture pattern is STATE-FOR-STATE the
  machine the capture-erased pattern builds — which is §6.1's STRUCTURAL
  erasure half and §11.3's "two lowerings from one parse" mitigation,
  obtained without a second tree. That is also what makes §5.4's
  byte-identity gate hold by construction rather than by audit

  **[ENG-BREP]** `Ast` gains `possessive` (A_REP only, set by
  src/opt/possessify.c), `revbody` (A_REP only, set by src/opt/revdet.c to the
  body's REVERSED AST when engine_m4.md §2.5's reverse-deterministic rung
  applies, and NULL otherwise — so one field is both the verdict and the
  material the emitter's backward walk is built from, which is what stops the
  emitter's three rung-reading sites from each re-deciding), and `ModState`
  gains `multiline`. The second has NO
  WRITER today and exists as a field rather than as a comment because D47.5
  rules the `$`-follow exemption's gate a LIVE CHECK: `$` in a quantifier's
  follow is measured safe at 0 diverging cells without `(?m)` and UNSAFE under
  it (re-measured 2026-08-18: 0/168 vs 12/168 greedy population; the 0/720 vs
  180/720 previously cited here is from a since-changed probe population), so
  the exemption is conditional on a fact that would otherwise stop being true
  without anyone revisiting the analysis. Module `assertions` is its writer and
  inherits the test obligation — noting the R30 finding that a verdict-time
  read of this field is scope-blind; the cure resolves multiline at PARSE time
  onto the node (assertions_design.md §8, D47.5 addendum).

  **[M6.2 wave A] `A_END`, `Ast.u.anch.multiline`, `NKind.N_END`, `DState.endvar`,
  and `Ctx.mods` becoming an OPAQUE POINTER.** Four type changes and one
  structural enforcement, all from `docs/design/assertions_design.md` §3.3 and
  §8, ruled by D62:

  - **`A_END` is a KIND and `Ast.u.anch.multiline` is a FIELD**, which is D62's
    principle applied twice in opposite directions in one change: node KINDS
    encode STRUCTURE, node FIELDS encode PARSE-RESOLVED MODIFIER STATE. `\z`
    is structure — no option turns `\Z` into it, and their position sets
    differ permanently ({n} versus {n} plus {n-1} before a final newline) — so
    it is a kind, and `src/opt/mrl.c:18-24`'s exhaustive-switch-no-default
    rule then makes every analysis that must decide about it a COMPILE ERROR
    (measured: exactly two sites had not already been handled deliberately).
    Multiline-ness of a `$` is modifier state, so it is a field, where
    `r->u.rep.greedy` (from `(?U)`) already lives.
  - **`Ast.u.anch.multiline` carries D62's control 3 as a comment obligation**, and
    it is load-bearing rather than decorative: the residual D62 accepts is
    that a FUTURE analysis pattern-matching `case A_EOL:` without reading the
    field silently reproduces the bug the field exists to fix, and no
    diagnostic will say so. Read that comment before writing an analysis that
    special-cases `$`.
  - **`DState.endvar`'s -1 does NOT mean what `eolvar`'s -1 means.** `eolvar
    == -1` is "same as this state"; `endvar == -1` is "same as the EOL VIEW",
    so a consumer walks a two-link chain. That asymmetry is the whole of R30
    E3 and the reason a `\z`-free pattern's artifact is byte-identical by
    construction; getting it wrong costs byte-identity on every `$`-bearing
    pattern while changing no answer.
  - **`Ctx.mods` is a pointer to an INCOMPLETE `ParseMods`** defined only in
    `src/parse/parse_mods.h`, so §8.2's invariant ("scoped modifier state is
    resolved at parse time, onto the node; no post-parse pass reads it") is a
    COMPILE ERROR outside `src/parse/` rather than a sentence someone has to
    remember. It was a sentence until wave A, and exactly one pass broke it —
    `src/opt/possessify.c`, reading the parser's END-OF-PATTERN multiline
    state at verdict time, a shipped scope-blind miscompile waiting for `(?m)`
    to be accepted. `compile.c` no longer builds one; `pcrec_parse_mods_init`
    (src/parse/parse.c) seeds it, and every Ctx that can reach a parser or a
    doorway port calls it.

  **[M6.2 wave D] `A_GSTART`, `NKind.N_GSTART`, `Dfa.s1g[]`, and the BARE
  ANCHOR predicate.** `\G` is a third kind on D62's principle and the cleanest
  instance of it in the module: it is not `\A` under an option, it is a test
  against a RUNTIME value (`<prefix>_search`'s `startpos`) where `\A`'s is the
  compile-time constant 0. The two coincide only when `startpos == 0`, which is
  why a pattern that confuses them passes every test written at the default
  startpos — the whole reason the module's corpus is written in `ms`/`ns`
  cells. `Dfa.s1g[]` is the SAME class-axis family as `s1u[]` closed with the
  `\G` bit set, equal to it entry for entry on every machine with no N_GSTART,
  which is what keeps every pre-wave artifact's start dispatch unmoved by
  construction rather than by a flag test. `pcrec_is_bare_anchor` /
  `pcrec_wrap_bare_anchor` are declared here because FOUR sites need the rule
  and had already drifted — see src/parse/CLAUDE.md for the over-rejection
  that found it.

  **[M6.2 wave E] `A_KRESET` and `Ctx.first_kreset_pos`, and the kind is the
  one member of the assertion family that is not an assertion.** Every other
  kind added by this module asks a QUESTION about the position and can fail;
  `\K` always succeeds, reads nothing, and WRITES — it moves the reported
  start of the match. It gets a kind rather than a flag for the usual D62
  reason and for a sharper one: there is no other node it could be a variant
  of. `src/ir/nfa.c` lowers it to N_EPS, so no IR kind exists for it — the
  first construct in the module with no `N_` counterpart, and the reason is
  that it changes no language, only what gets reported.
  `first_kreset_pos` is `first_cap_pos`'s twin, first-wins, and it exists for
  the DIAGNOSTIC only: `src/opt/select_engine.c` decides the engine by WALKING
  the AST for an A_KRESET (the honest question — the reported start is
  path-dependent exactly when such a node exists, and a rewrite that deleted
  one must flip the verdict), while the `engine_why` stamp needs a pattern
  offset that no AST node carries.

  **[M4.7a] SR-8 evaluated and declined to add a `Ctx.vmonly_*` field here**,
  unlike the `ModState.multiline` precedent above — the difference being
  that `multiline`'s writer (module `assertions`) is a scheduled, named
  future customer, while SR-8's would-be socket has none: every `VM_ONLY`
  registry row lacks a producer, so there is no near-term writer to shape
  the field's contract around. `tests/registry/registry_check.c`'s
  `check_engine_capability_tripwire` guards the gap instead — see
  src/opt/CLAUDE.md's select_engine.c entry. **[M6.3] is the tripwire's
  first trip**, and the fix is recorded on `Ctx.named_groups` below rather
  than here: no `Ctx.vmonly_*`-shaped field was needed after all.
  **[M6.2] WAVE E IS ITS SECOND TRIP AND ITS FIRST REAL ONE.** [M6.3]'s was
  a reclassification — a named group's AST is an ordinary A_CAP, so the
  pre-existing capture rule already routed it and the three rows moved to
  ANY_ENGINE, leaving the population. `\K` genuinely IS VM-only and stays in
  it, so the tripwire fires for the reason it was written. The answer was
  still not SR-8: a construct-specific `forces_*` row is the honest shape at
  sample size one, and the generic registry-column consultation would be
  machinery designed around one customer. The tripwire keeps its demand and
  gains a NAMED exception that pays for itself by asserting the
  `--engine=dfa` refusal live — see tests/registry/registry_check.c. A
  SECOND construct arriving there is when SR-8 has earned its axis, and a
  `Ctx.vmonly_*` field is still not what it needs.

  **[M6.3] `NamedGroup` and `Ctx.named_groups`/`n_named_groups`.** Module
  `named-groups`' declared-groups list: an arena-allocated singly linked
  list, in declaration order, of every `(name, group-number)` pair the
  parser's `pcrec_ngport_declare` (src/parse/mod_named_groups.c) records.
  Populated UNCONDITIONALLY — regardless of `want_caps` — because a
  group's NAME is the same lexical-fact tier `ngroups` already is, not a
  build-output fact; `src/gen/emit_dfa.c`'s `emit_info_def` reads it once,
  at emission, to build the sorted `rx_group_entry` array
  `rx_info.groups`/`nnames` promise (sort key: `strcmp` on the name,
  matching PCRE2's own measured `PCRE2_INFO_NAMETABLE` order —
  docs/dev/decisions.md D59). No new engine-selection field was added: a
  named group's AST is an ordinary `A_CAP` node, so the pre-existing
  `forces_captures` rule in src/opt/select_engine.c already covers it,
  which is also why the three declaring registry rows moved `engines`
  VM_ONLY -> ANY_ENGINE rather than SR-8 (above) finally being built — D59
  has the full argument.

  **[M6.4.2] `A_ATOMIC`, `Ast.reg`, `Ctx.first_atomic_pos` and
  `RegKind.RK_QUANTSUFFIX`** (docs/design/atomic_groups_design.md, R31).

  - **`A_ATOMIC` is a KIND, not a field**, on D62's OWN principle rather than
    on a precedent — the first revision of the design cited
    `assertions_design.md` §8.3 as settling it and the panel found §8.3 says
    the opposite (D62 chose the FLAG for `(?m)`). D62's test is what carries
    it: kinds encode STRUCTURE, fields encode parse-resolved MODIFIER state,
    and atomicity changes the LANGUAGE (`(?>a*)a` matches nothing where `a*a`
    matches), changes the BACKTRACKING, and brackets a body. Two further
    supports, both measured: `src/opt/revdet.c`'s `rd_node` CLEARS
    `Ast.u.rep.possessive` on the copy the emitter walks, so a field would be
    silently deleted on a revdet-approved body; and adding an `AKind` raises
    `-Wswitch` at every pass that must decide about it while adding a FIELD
    raises none.
  - **`Ast.reg` is SR-8's stamp (D67)**, spelled as a pointer to the producing
    registry ROW rather than a copy of its `engines` mask — a copied mask is a
    second home for a registry fact, and `why`'s text has to come from the row
    anyway. NULL means ANY_ENGINE, so a FORGOTTEN stamp fails in the UNSOUND
    direction ON PURPOSE (contract note 2): the generic tripwire in
    tests/registry/registry_check.c is what catches it, not a lucky default.
    A discharge's output must not inherit the discharged node's stamp
    (note 3) — the free discharge is deletion-shaped and satisfies that
    trivially.
  - **`Ctx.first_atomic_pos`** is `first_kreset_pos`'s twin, field for field
    including first-wins, and exists for the DIAGNOSTIC's offset only: the
    engine verdict WALKS the post-discharge tree, because a parse-time counter
    would keep counting nodes a rewrite deleted.
  - **`RK_QUANTSUFFIX` is the first NON-DOORWAY row kind**, and its cost is
    the thing to read before adding a sixth: a fifth `RegKind` raises NO build
    alarm at all (MEASURED, 28 files / 0 `-Wswitch` diagnostics — every RegKind
    switch in the tree carries a `default:`), so the exposure is the hardcoded
    kind ARRAYS and the enumerations-by-CALL. Twelve sites were touched;
    eleven were enumerated in the design and the TWELFTH — a
    `const RegRow *all[4]` in registry_check.c whose loop already ran to
    RK_COUNT — was found by a SEGFAULT. `check_kind_coverage` (new) reads the
    `--list-syntax` OUTPUT, which is the only formulation that can see an
    `all_kinds[]` omission at all.

  **[D65] `PcrecBuiltStatus` and `PCREC_UNBUILT_MARKER`.** A THIRD axis on
  `RegRow` beside `RegStatus`/`Roadmap` — has the owning module's producer
  landed for THIS construct — deliberately NOT a fourth `RegRow` field:
  `pcrec_construct_built_status()` (src/parse/syntax_dump.c) DERIVES it
  per row by driving the row's own `syntax` through a gate-forced-open
  doorway call, the reason ext.c's UNBUILT macro comment already gives for
  not adding "a second built column somebody would have to keep in sync
  with the ports". `PCREC_UNBUILT_MARKER` is the fixed substring both
  ext.c's UNBUILT macro (which renders it) and the classifier's
  documentation (not its logic — see syntax_dump.c's own comment for why
  classification reads `ExtResult.answered_at` instead) share, so a
  reworded refusal cannot silently drift from what it names. See
  docs/design/registry_built_status_memo.md (ratified wholesale, D65) and
  src/parse/CLAUDE.md's syntax_dump.c entry for the full derivation.

## Conventions

All dynamic allocations for AST/IR go through arena_alloc() and are freed together. StrBuf accumulates generated code; sb_* functions append. Error paths longjmp to cx.jb. internal.h is NOT installed; it is internal to src/.

Maintenance: update this file when files are added/removed or their roles change.
