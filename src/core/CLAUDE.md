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

  **[SEL-1] (2026-08-28) `compile_driver` IS A BOUNDED ONE-SHOT RETRY LOOP
  NOW** (`COMPILE_MAX_ATTEMPTS = 2`, `SELECT_MAX_ROUNDS`'s own
  from-day-one-bound reasoning), not a single pass — plan row [SEL-1], K40's
  fix. The ONE `setjmp` in this file is the only recovery point the compiler
  has, so feeding a DFA build's own "over budget" result back into engine
  selection (`auto`'s do-or-die exception: the overflow is a selection
  outcome, not a refusal — `src/opt/select_engine.c`'s `forces_dfa_
  overflow` entry has the full mechanism) means rerunning the WHOLE pipeline
  once more with one more input bit set (`Ctx.dfa_disabled`) rather than
  wrapping the DFA build in a second, LOCAL recovery point — the shape the
  brief that chartered this row explicitly ruled out ("no try/catch-shaped
  clause at the ctx_fail site"). The retry is decided in the `setjmp`-catch
  branch (`cx.dfa_overflowed && defo.engine == PCREC_ENGINE_AUTO &&
  !(defo.flags & PCREC_FORCE_PREFILTER) && !dfa_disabled`), so `--engine=dfa`
  and `-fprefilter` never retry and keep today's refusal, unchanged.
  `dfa_disabled`/`dfa_overflowed`/`dfa_overflow_why` are plain `Ctx` fields
  (`internal.h`), not arena text, because the retry decision runs AFTER
  `job_cleanup`'s `arena_free` on the failed attempt — `overflow_why`
  (a local, outside the loop) is what carries the failed attempt's own
  diagnosis forward into the next `Ctx`'s seed. `attempt` and `dfa_disabled`
  are `volatile`: `-Wclobbered` (which `make strict` promotes) flags both
  without it, since the loop calls `setjmp` fresh each iteration — more than
  gcc's conservative liveness analysis can see through.

  **[LIM-2] N1 (2026-09-04) THE AUTO-ROUTE WORK BUDGET'S OWN STDERR NOTE.**
  `src/ir/dfa.c`'s `intern()` gains a SMALLER, auto-only budget
  (`PCREC_MAX_AUTO_DFA_ELEMS`) on the same `Ctx.subset_elems` counter K7
  already charges, checked before the hard `PCREC_MAX_SUBSET_ELEMS` cap and
  joining the IDENTICAL `[SEL-1]` umbrella (`dfa_overflowed`/
  `dfa_overflow_why`) a hard-cap overflow uses — see that file's own
  comment for the full mechanism and why it is scoped to `!d->optional`
  (an optional machine's overflow already never refuses) and to
  `cx->opt->engine == PCREC_ENGINE_AUTO` (an explicit `--engine=dfa` pays
  the full cap in full). `Ctx.dfa_overflow_is_budget` is the ONE new field
  this needed: it distinguishes "this retry followed the auto budget" from
  "this retry followed a hard cap" so the one-line stderr note can be
  printed on the SUCCESSFUL fallback attempt only — `volatile bool
  budget_fallback`, captured at the same point and under the same
  first-overflow-only guard `dfa_was_engine` already is, read at the
  WARN_EMIT_BYTES block's own placement (past the recovery point, on the
  attempt about to succeed, never on a discarded ladder trial). A hard-cap
  overflow's own successful fallback prints nothing new, unchanged from
  before this row.

  **[LIM-2] N1 ALSO GENERALIZES THE RAISE-ONLY OVERRIDE onto three more
  caps.** `defo.max_nfa_states`/`max_dfa_states_goto`/`max_subset_elems`
  (0 = the built-in default) read exactly like `max_emit_code_bytes`/
  `max_emit_bytes` already did — see `lib/pcrec.h`'s own comment on the
  four new fields and `cli/main.c`'s `raise_only_limits[]`, the one table
  now driving all six raise-only flags. `PCREC_MAX_DFA_STATES_GOTO`'s own
  raise (the ENG_ATTEMPT route's build call, this file) clamps a
  raised-past-`INT_MAX` value rather than truncating it, since
  `pcrec_build_dfa`'s `maxstates` parameter is a plain `int`.

  **[ENG-ABS] (2026-08-29) `build_anchored_dfa` — THE OPTIONAL THIRD MACHINE.**
  A DFA artifact's `<prefix>_match` promises a match at exactly `ctx->pos` and
  used to reach that by running the UNANCHORED search and rejecting any match
  whose start is not `ctx->pos`; `[OPT-2]` STEP 2 measured the reverse pass that
  costs at ~50 % of the DFA's time on every matching subject. This function
  builds the same subset construction over the same NFA rooted at
  `nfa.anch_start` — the forward machine WITHOUT the start-anywhere self-loop —
  and four things about its placement are load-bearing, each stated at the
  function: it is built LAST (`PCREC_MAX_SUBSET_ELEMS` is a per-COMPILE budget,
  so an optional machine built first could refuse a pattern that compiles
  today); it is built OPTIONAL (an overflow is a selection outcome, never a
  diagnostic); the engine's overflow RECORD is saved and restored around it
  (`Ctx.dfa_overflowed` means "the DFA engine cannot compile this pattern",
  which is false when only the optional machine overflowed, and leaving it set
  would make a later unrelated `ctx_fail` take `[SEL-1]`'s retry path for the
  wrong reason); and it is skipped for a VM HYBRID, whose `_match` is the VM's
  own anchored body. `docs/design/anchored_match_unwrapped.md` §2/§5.2.
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

- **cpset.c** — [M5.0 stage 1] THE CODE-POINT INTERVAL SET: the `A_CLASS`
  payload's one representation, its arena-backed builder, and the ONE function
  in this compiler that turns a class node back into a 32-byte bitmap.
  (`docs/design/utf8_design.md` §2.2, §2.1.4, §2.7.1.)

  **WHY IT IS A FILE AND NOT A HEADER OF INLINES.** Its whole value is that the
  render is in ONE place with an assertion in it. r54 E1 found that under the
  design's first pipeline `src/gen/emit_vm.c`'s `vm_cls` would have interned
  the first 32 bytes of a code-point interval array AS a membership bitmap —
  an artifact that compiles, matches something, and is invisible to every
  answer check in this project, because those all compare pcrec against an
  oracle on a pattern both understand. `pcrec_cls_bits` REFUSES a node whose
  intervals are not byte-confined, by `ctx_fail` and not `assert` (§13
  obligation 5; and K7's rule that a library must not kill its caller), so a
  lowering that did not run is a diagnosed internal error at the site that
  would have committed the miscompile.

  **THE BUILDER IS ARENA-BACKED BECAUSE OF `ctx_fail`.** Every class in this
  compiler is accumulated inside code that can refuse mid-accumulation —
  `p_class` raises "invalid range in character class" from the middle of its
  own loop — and `ctx_fail` longjmps to `compile_driver`, which frees the arena
  wholesale. A `malloc`/`realloc` builder would leak on every diagnosed
  pattern, and the leak would be found by the ASan/LSan axis rather than by
  review. Growing through `arena_alloc` abandons the smaller block (under a
  kilobyte for a class reaching 64 intervals) and cannot leak by construction.

  **THE INVARIANT IS SORTED, DISJOINT AND NON-ADJACENT**, and non-adjacency is
  the half that is easy to drop and expensive to lose: without it `[a-mn-z]`
  and `[a-z]` are two lists denoting one set, and §2.7.2's argument that the
  artifact does not depend on the pattern's SPELLING stops being true.

  **[M5.0 stage 3] `pcrec_ast_class_from_iv` (src/parse/parse.c) is the
  interval-shaped sibling of `pcrec_ast_class_from_bits`**, and it differs in
  two ways that are both about what a NAMED SET means. It INTERSECTS the set
  with the encoding's universe rather than refusing — `\p{L}` under `byte` is
  the Latin-1 letters, which is measurably what PCRE2's own 8-bit non-UTF
  build does, where `\x{100}` under `byte` REFUSES because naming an absent
  code point is a mistake and naming a set is not. And it applies NO case
  fold: MEASURED, a caseless `\p{Lu}` is `\p{L&}` and every other property
  is caseless-invariant, so the caller owns caselessness and an ASCII fold on
  top would be wrong on every non-ASCII cased letter.

  Two types, deliberately: a WRITE-ONLY `PcrecCpSet` builder and a READ-ONLY
  published `const PcrecCpRange *`, so "publish once, never mutate" is
  compiler-checked rather than a convention — which is what lets two nodes
  share one list (`revdet.c`'s copy constructor copies the pointer).
  `tests/codegen/run_cpset_structure.sh` is the standing check.

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
  **[SEL-1] adds `PCREC_DFA_OVERFLOW_WHY_LEN`** (96), sizing `Ctx.dfa_
  overflow_why` (internal.h) — a fixed array rather than an arena string,
  because it has to survive `job_cleanup`'s `arena_free` on the failed
  attempt compile.c's retry reads it after. K38-precedent margin over the
  76-byte worst-case text src/ir/dfa.c's two overflow sites emit.
  **[LIM-2] N1 adds `PCREC_MAX_AUTO_DFA_ELEMS`** (30,000,000; `limits.def`,
  home LIMITS_H, override BUILD_D + a runtime raise flag — the two-lever
  shape `PCREC_MAX_VM_EMIT_CODE_BYTES` already has, for the identical
  reason: `tests/codegen/run_n1_budget.sh`'s reference compiler needs a
  `-D`-lowered build to drive its positive control, since the natural
  population at the shipped default is zero (docs/dev/lanes/
  n1budget_report.md carries the derivation). A SMALLER budget on the SAME
  `Ctx.subset_elems` counter `PCREC_MAX_SUBSET_ELEMS` bounds, checked ONLY
  under `--engine=auto` and only against the two mandatory machines — see
  src/ir/dfa.c's own comment at the check site.
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
  `n->u.cls` (a 32-byte bitmap through [M6.6]; `{iv, n}` code-point intervals
  since [M5.0] stage 1 — see the re-derivation below),
  `n->u.rep.{rmin,rmax,greedy,possessive,revbody}`,
  `n->u.cap.no`, `n->u.anch.multiline`, `n->u.bref.{refs,nrefs,caseless}`.
  `k`, `l`, `r`, `not_repeatable` and `reg` stay COMMON.

  **[M6.6.2 wave A2] THE FIRST MEMBER ADDED UNDER THE RULE IS `u.look`**
  (`A_LOOK`: `behind`, `neg`, `atomic`, `widths`, `nbranch`, and since
  [DD-14.LB] `at`), and it is worth
  reading as the worked example the rule was written for. The design's own
  sketch (`lookaround_design.md` §3.1) proposed FIVE new TOP-LEVEL fields, one
  of them an `int look_widths[]` FLEXIBLE ARRAY MEMBER. D70 refuses both
  halves: they go in a member, and the width table is an arena `const int *`
  because a flexible array cannot live in a union, cannot be preceded by
  another member, and would make `sizeof(Ast)` a lie for the zeroing arena
  that allocates every node at one fixed size. The union member is 24 bytes
  against the then-largest member's 32, so `sizeof(Ast)` is unchanged. (Since
  [DD-14] `u.call`'s 96 bytes set the union's size, and [M5.0] stage 1's
  16-byte `u.cls` therefore moves no other member's offset.) The rule D70 makes
  operative: **no module may add a new top-level per-kind field** — a new kind
  adds a union MEMBER, and a field joins the common block only when a survey
  MEASURES it cross-kind. The union buys reading and containment, NOT
  checking: C does not police member access, so D62's discipline (parse-
  resolved state, per-field comments, per-field sabotage rows) is unchanged.

  **[DD-14.LB] `u.look` GAINED `at`, A PATTERN OFFSET ON A NODE — THE FIRST OF
  ITS KIND, AND THE RULE IT SETS IS WHERE SUCH A FIELD MAY LIVE.** `Ast`
  carries no position of any kind (PARSE-1's own note) and that is deliberate;
  `AltInfo.last_bar` exists because of it. What forced one here is a TIMING
  gap: a lookbehind whose body carries a call cannot have its width decided in
  the parse hook (the callee is not bound yet) and cannot be refused anywhere
  else without an offset. So the hook records the assertion's own offset and
  `pcrec_postresolve` refuses there. **The field is a UNION MEMBER, not a
  common one**, and that is the containment D70 buys: "this construct's parse
  hook deferred a decision and left the offset for it" is a fact about
  lookarounds, not about nodes, and the next module that needs one adds it to
  ITS member rather than growing the common block for everybody. It is written
  UNCONDITIONALLY for every `A_LOOK` rather than only when pending, because a
  conditionally-valid field is a field a later reader gets wrong.

  **AND `u.look.widths == NULL` NOW CARRIES A THIRD MEANING, chosen for its
  FAILURE MODE.** `!behind` -> NULL with `nbranch == 0` (a lookahead has no
  width rule); `behind && widths` -> resolved; `behind && !widths` -> PENDING.
  The three are disjoint and exhaustive, and the pending state reuses NULL
  rather than taking a new boolean **because `vm_look_behind` was already loud
  about NULL** — so a post-resolution pass that goes missing is an internal
  error on the first call-bearing lookbehind. A `bool pending` beside a zeroed
  width table would have made the same loss a wrong span, and on a negative
  lookbehind a false match. Sabotage S169 is that experiment.

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
  | `--emit-ir`'s listing | **no `AKind` arm exists to write.** The listing renders the `VEvent` stream the emitter records (`emit_vm.c` switches on `VEvent.k`), so a call's listing content is whatever the `RX_CALL`/`RX_RETURN` emission records as events — the same finding `u.look` reached. WAVE B+C LANDED THAT EMISSION AND THE CONTENT IS NOW MEASURED (2026-08-25, the [DD-14] close): `--features recursion -p rx --emit-ir -- '(a(?1)?b)'` renders `CALL callee L2, return L11 ; call group 1; the frame carries the return label` plus the trailed SELF-writes, and the callee's region is listed at its own labels — the listing gained a call WITHOUT an `AKind` arm being written, which is the row's claim discharged rather than merely predicted. | measured, not assumed |

  **THE RULE THE MEMBER ADDS**, beside D70's own: a generic helper must not
  merely GUARD `u.call` — it must not FOLLOW `.body`. A whole-tree walk
  already visits the callee at the callee's own lexical position, so following
  the edge is redundant, and on `(a(?1))` it is a non-terminating compile in a
  predicate asked of every pattern. A genuinely subtree-relative analysis goes
  through `src/opt/callgraph.c`'s memoised SCC fixpoint (wave B+C).
  `sizeof(Ast)` is unchanged: the member is 32 bytes on LP64, matching the
  then-largest member.

  **[DD-14 wave B+C] `u.call` GAINED TWO MORE FIELDS, AND THEIR POLARITY IS
  THE WHOLE OF THE DESIGN.** `minw` and `nonnullable` are the two derived
  facts a bare `const Ast *` walker cannot compute, cached ON THE NODE — and
  the placement is forced rather than chosen. `pcrec_minw` (src/opt/mrl.c) and
  `vm_nullable` (src/gen/emit_vm.c) have no `Ctx` parameter, so "read
  callgraph.c's memo" has exactly two spellings: change every call site's
  signature, or put the memo in a FILE-STATIC — and a file-static is a mutable
  global, which [TS-1]/[TS-3] test against directly. The node is the one place
  both walkers already have in hand and that is private to one compile.

  **EVERY ONE IS WRITTEN SO THE ARENA'S ZERO IS THE SOUND ANSWER**, because a
  walker may legitimately run BEFORE the fixpoint does (`pcrec_minw` is called
  from `src/opt/possessify.c`, inside `pcrec_select_engine`, before the graph
  exists). `minw` 0 is `pcrec_minw`'s own SAFE direction (an under-estimate
  prunes less and can never delete a live position). `nonnullable` is
  INVERTED for exactly this reason and that inversion is the field's whole
  content: `vm_nullable` answering true is what EMITS the empty-iteration
  guard, so a zero reading "nullable" keeps the guard and costs a redundant
  test, while the other polarity's zero would DROP it and hang the matcher on
  `(?&g)*` with a nullable callee.

  **[DD-14.LB] `maxw` ARRIVED, AS A PAIR, AND THE PAIR IS WHY IT WAS ABSENT.**
  Wave B+C's entry here read *"`maxw` IS DELIBERATELY ABSENT, and the asymmetry
  is the point: `pcrec_maxw`'s safe direction is the opposite one, so a zero
  would be its SILENT MISCOMPILE"* — and that half is still exactly right. A
  bare `long long maxw` whose arena zero is 0 would be an UNDER-estimated
  maximum, which lets a variable-width branch through the lookbehind rule as
  fixed, which on a NEGATIVE lookbehind is a false match. So the field ships as
  `maxw` PLUS `maxw_known`, and `pcrec_maxw`'s arm reads the first only through
  the second: false — the arena's zero — means "answer `PCREC_W_UNBOUNDED`",
  which is what the arm answered before the memo existed. That is
  `nonnullable`'s inversion trick spelled with two fields instead of one,
  because unlike nullability there is no polarity of a WIDTH that makes its
  zero safe.

  **THE OTHER HALF OF THE OLD ENTRY WAS A TIMING CLAIM AND IT WAS ANSWERED BY
  MOVING THE CONSUMER.** It said tightening the arm *"would need a writer that
  runs before the PARSE-TIME lookbehind width rule, which the call graph cannot
  be"*. True — so the rule stopped being parse-time-only: `pcrec_postresolve`
  (src/opt/postresolve.c) re-asks module `lookaround`'s own rule after
  `pcrec_callgraph_build`, and the memo is read where it exists. **The
  generalisable form: when a memo cannot be written early enough for its
  consumer, check whether the CONSUMER can be moved later before concluding the
  memo is impossible.** See `src/opt/CLAUDE.md`'s `mrl.c` and `postresolve.c`
  entries.

  **`save`/`nsave` ARE FILLED BY THE EMITTER, NOT BY `callgraph.c`**, which is
  a deviation from design §4.1(d)'s letter and not from its principle. §4.1(d)
  says they are a fixpoint over the call graph and the PARSER does not have
  the graph, which is why they are not parse-resolved state; what it did not
  anticipate is that they are SLOT INDICES, assigned by `vm_count_slots`' own
  walk over the emitter's rung decisions and existing nowhere else. Predicting
  them outside `emit_vm.c` would be the second slot census `src/gen/CLAUDE.md`
  names as the standing hazard for this family. `pcrec_emit_vm` therefore
  takes `Ast *root` rather than `const Ast *` — a dropped qualifier is
  preferred to a cast at the write site, because a cast is a claim a reader
  has to check.

  **`Ctx` GAINED ONE FIELD**, `callgraph`, opaque and arena-owned, NULL for a
  call-free pattern. **WHERE THE PASS RUNS IS LOAD-BEARING**: it is the only
  writer of `u.call.body`, and two passes above it REBUILD nodes rather than
  mutating them, so a `.body` captured at end of parse can name a subtree that
  is no longer in the tree.

  **`PendingRef` GAINED ONE FIELD**, `PendKind` — one list, one pass, two
  rules, differing in the NAME arm alone (a call takes the FIRST DECLARATION
  statically; a reference takes the whole run and picks the first SET member
  at match time). **The ZERO case is not a third difference**: `(?R)`/`(?0)`/
  `(?00)` target the AST ROOT, which always exists, so the port answers them
  itself and queues NOTHING — which is what keeps `(a)(?-2)`, a relative
  offset computing to zero, an error-115 rather than a silent `(?R)`.

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

  **[DD-14 wave B+C] THE ONE DEFERRED RE-READ, DISCHARGED.** The table's only
  open item was `vm_lifts` once `vm_nullable` became the graph fixpoint. It was
  re-read, and the answer INVERTED from "declines for an uninteresting reason"
  to "declines for the load-bearing one": `vm_nullable`'s `A_CALL` arm is now
  `return !a->u.call.nonnullable`, so `(?>(?&g)*)` for a NON-nullable `g` is
  lifted (correctly — the star can no longer spin) and for a nullable `g` is
  not. That is not a cosmetic change of reason. It is the ONLY gate standing
  between `(?&g)*+` and a possessified region, so mech row **S157** aims at
  `vm_nullable`'s arm and not at `possessify.c`: souring the arm to a constant
  `false` is what a wrong callee-nullability answer would do, and the corpus
  cell that catches it is a nullable callee under a possessive star.

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
  region's slot INDICES over whichever one it was handed. **WAVE B+C OWED ONE
  OF THREE ANSWERS**: resolve `.body` AFTER the rewriting passes, have every
  rewriting pass update it, or exempt callee subtrees from rewriting. Note
  `possessify` and `revdet` are NOT in this list — they annotate fields on the
  SAME nodes, so `.body` sees their results.

  **[DD-14 wave B+C] TOOK THE FIRST, AND MEASURING IT NARROWED THE FINDING TO
  ONE OF THE TWO PASSES.** `src/opt/callgraph.c` binds `.body` over the FINAL
  tree, after `pcrec_select_engine` and before emission. With the bind moved
  above `pcrec_altcls`, `((?:a|b))(?1)` emits TWO DIFFERENT PROGRAMS FOR ONE
  GROUP — a merged class test lexically, the un-merged alternation with its own
  `RX_PUSH` in the region — and `RX_RESUME_FRAMES` moves 2 -> 3. **The ANSWERS
  do not change**, because altcls is answer-preserving in both directions, so
  the detector is `[DD-14-RECURSION rule 3]` in tests/codegen rather than a
  corpus cell. **And `((?>a)b)(?1)` compiles BYTE-IDENTICALLY under the same
  sabotage**: `pcrec_discharge_atomic` splices by rewriting the PARENT's `->l`
  IN PLACE, so the `A_CAP` a callee is rooted at keeps its identity and sees
  the discharge. Only the pass that REBUILDS the node is a hazard, which is a
  narrowing of what wave A2 could see. Sabotage row S166.

### The D70 ownership survey

  Every read and write of every non-`k`/`l`/`r` field of `struct Ast` across
  `src/`, `cli/`, `lib/` and `tests/**/*.c`, classified by the kind(s) the
  site is reasoning about. Recorded here because D70's "Revisit when" clause
  depends on the measurement existing. `Ast` turned out to be confined to 20
  files, all under `src/` — `cli/`, `lib/` and the test C drivers never touch
  it, so the whole migration surface was 231 lines / 249 occurrences.

  | field | kind(s) the sites reason about | Ast sites | disposition |
  |---|---|---|---|
  | `cls[32]` | A_CLASS | 25 | `u.cls.bits` (widened to `u.cls.{iv,n}` at [M5.0] stage 1) |
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
  `u.cls` spanned `+40..+71` AT THE TIME — it is 16 bytes now, and the [M5.0]
  section below is where this arithmetic's CURRENT answer lives — so through
  `u.rep` the clear wrote
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

### [M5.0 stage 1] THE SURVEY RE-ASKED AGAINST THE NEW LAYOUT — and the clobber went LATENT

  **`u.cls` IS 16 BYTES NOW**, not 32: `{const PcrecCpRange *iv; int n;}`
  (`docs/design/utf8_design.md` §2.2). §2.2.3 makes re-asking the survey's own
  QUESTION — *which generic walker writes a per-kind field without switching on
  `k`* — an obligation of the same change, on the stated ground that *"a
  16-byte `u.cls` puts different fields over different bytes and the second
  finding above is explicitly a clobber waiting for its payload."* Re-asked,
  and the answer is more interesting than "the guards still hold".

  **THE NEW ARITHMETIC**, measured with `offsetof` on the built tree rather
  than reasoned from the declaration:

  | | old (32-byte bitmap) | new (16-byte interval list) |
  |---|---|---|
  | `u.cls` spans | `+40..+71` | `+40..+55` (`iv` `+40..+47`, `n` `+48..+51`, 4 bytes tail padding) |
  | `u.rep.greedy` `+48` | bitmap byte 8 | **byte 0 of `n`** |
  | `u.rep.possessive` `+49` | bitmap byte 9 (`H`-`O`) | **byte 1 of `n`** |
  | `u.rep.revbody` `+56..+63` | bitmap bytes 16-23 (`0x80`-`0xBF`) | **outside `u.cls` entirely** |
  | `sizeof(Ast)` | 136 | **136, unchanged** |

  `sizeof(Ast)` does not move because the union's size is set by `u.call` (96
  bytes), not by `u.cls` — so this re-layout moves NO other member's offset,
  which is the narrower true statement where §2.2.3 predicted "every offset in
  the `Ast` union moves".

  **THE GENERIC-WRITER SURVEY, RE-RUN over every `u.<member>.<field> =` in
  `src/`.** Exactly one generic-path writer survives — `rd_node`, still guarded
  on `n->k == A_REP` — and `mod_assertions.c`'s pin is still guarded on
  `k == A_BOL || k == A_EOL`. Every other write is inside a producer that owns
  the kind. So the guards hold and nothing new needs one.

  **BUT THE HAZARD THE GUARD DEFENDS AGAINST HAS GONE LATENT, AND THAT IS THE
  FINDING.** `rd_node` clears — it writes ZEROS. Under the new layout
  `possessive` lands on byte 1 of `n` and `revbody` lands outside the payload,
  so the unguarded clear zeroes a byte of `n` that is **provably already
  zero**: a class over `[0, 0xFF]` can hold at most 128 disjoint non-adjacent
  intervals, so `n <= 128 < 256` and its byte 1 is 0 on every artifact the
  `byte` backend can produce. The clear is a no-op.

  **MEASURED, because "provably" deserves a number.** With the `n->k == A_REP`
  guard REMOVED, all **2,845** distinct corpus patterns compile
  **byte-identically** to the guarded build, and
  `tests/rungselect/revdet_highbytes.rxt` — the file written specifically to
  detect this clobber, whose own header records that an all-lowercase corpus
  could not express it — reports **7/7 identical**.

  **SO SABOTAGE ROW S121 IS CURRENTLY UNDETECTABLE**, and it is recorded here
  rather than quietly re-aimed, because which repair it gets is a ruling and
  not an implementation detail. The row's mechanism (clobber the class bitmap's
  bytes 9 and 16-23) describes a layout that no longer exists; its detector
  corpus cannot see the new one; and the row will go on scoring while
  certifying nothing, which is precisely the S70/S155 failure `[MECH-REACH]`
  was built for.

  **THE GUARD STAYS, AND NOT ON SENTIMENT** — but the reason given here at
  stage 1 was WRONG about when, and [M5.0] stage 3 measured it. Stage 1 said:
  *"It goes LIVE again at stage 3. `\p{L}` is ~770 intervals, so `n > 255`
  becomes ordinary the moment `unicode-props` lands."* Stage 3 landed and the
  hazard is **structurally unreachable**, which is a stronger statement than
  stage 1's arithmetic one:

  * `n > 255` REQUIRES a code point above 0xFF — a byte-confined class holds
    at most 128 disjoint non-adjacent intervals over [0, 0xFF], this file's
    own invariant. And under `--encoding=byte` a property set is CLAMPED to
    the encoding's universe (`pcrec_ast_class_from_iv`, PCRE2's own 8-bit
    behaviour), so `\p{L}` there is EIGHT Latin-1 runs, not 677.
  * A class holding a code point above 0xFF **DECLINES the
    reverse-deterministic rung**, because `pcrec_cls_bits_widen` answers ALL
    BYTES for an out-of-range class — the SOUND direction for a FIRST set,
    deliberately — so disjointness can never be proven. MEASURED with a
    `\p`-FREE control, so this is a fact about wide classes and not about
    the module: `((H)|I){3}J` under `-e utf8` stamps `RX_VM_RUNGS 0x8u`
    while `((\x{100}|H)|I){3}J` stamps `0x2u`.
  * Therefore `rd_node` never copies a class with `n > 255` at any encoding
    or cap setting — `((\p{Ll})|1){3}!` stamps `0x2u` with the emit caps
    raised twentyfold.

  The guard is correct for a reason that is about `k` and never about offsets,
  which is exactly why it survives a re-layout that erased its symptom — and
  why it stays now that the symptom is provably unreachable rather than merely
  absent.

  **THE STAGE-1 REACH PROBE WOULD HAVE SAID THE ROW HAD WOKEN UP**, and that
  is the transferable lesson. It asked whether `\p{L}` COMPILES, on the
  reasoning that compiling it implies `n > 255`. Stage 3's own clamp makes
  that implication false, the probe now matches, and the runner would have
  reported `NOW REACHED` over a population that does not exist — the S70/S155
  shape one level down, in a REACH DECLARATION rather than in a check. S121's
  probe is re-aimed at the real question (does a >255-interval class reach the
  revdet rung) and fails honestly.

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


## [DD-14 wave G] the pass reorder, and three declarations

**`compile.c`: `pcrec_discharge_atomic` IS HOISTED OUT OF
`pcrec_select_engine`** and is compile.c's own line now, immediately after
`pcrec_altcls`. ONE MOVE, satisfying two constraints that are otherwise
incompatible: the CALL GRAPH must run after every pass that REBUILDS a node
(`src/opt/callgraph.c`'s header argument — `.body` is a cache of "which subtree
is that group's IN THE TREE THE EMITTER WILL WALK"), and ENGINE SELECTION must
now run AFTER the call graph, because §6.3's LINKAGE is what decides whether a
call is structurally VM-only. The order is
`altcls -> discharge -> callgraph -> select_engine -> postresolve`.

**IT ALSO FIXED A LATENT DROP.** Inside `select_engine` the discharged root was
assigned to a LOCAL, so a discharge at the very ROOT was thrown away and the
emitter walked a tree selection had not judged. Sabotage row S178 puts the drop
back; its expectation is UNDETECTED with the search recorded, because the
discharge fires exactly where `vm_lifts` LIFTS and a lifted group allocates no
mark of its own, so the two spellings emit the same program. A CALL-FREE pattern
is unaffected by the whole move: `pcrec_callgraph_build` returns at its first
scan having written nothing.

**`internal.h` gains three declarations**: `pcrec_has_linked_call` (the
narrowing that separates "this pattern is VM-only" from "this pattern has a
call"), `pcrec_has_live_capture` (the dead-group elision — a group no emitted
code can WRITE does not force the capture-recording engine), and
`pcrec_callgraph_spliced` (the per-TARGET linkage, which is what the emitter
needs to decide whether to emit a shared region at all).

**`limits.h` gains two budgets**: `PCREC_MAX_SPLICE_NODES` (512, per spliced
site, over the expansion COMPOSED across nested splices) and
`PCREC_MAX_SPLICE_TOTAL` (8192, the sum of added nodes). Both are counted in AST
nodes rather than emitted ones, because eligibility must be decided BEFORE the
emitter runs — engine selection reads the linkage — and the emitter's `Cost`
numbers do not exist yet at that point. `PCREC_MAX_VM_NODES` stays the hard
backstop; these keep ordinary patterns far away from it.
Maintenance: update this file when files are added/removed or their roles change.

## [DD-14.FB] `BufSurface`, and two emitter signatures (2026-08-25)

`internal.h` gains one type and widens two declarations for the caller-provided
frame buffer (D71 item 2, `docs/spec/match_api.md` §10):

- **`BufSurface`** — the five facts the sizing surface publishes
  (`resume_frames`, `trail_frames`, `resume_frame_size`, `trail_frame_size`,
  `align`). It is a STRUCT rather than five parameters because both consumers
  take all of them and a positional list of five integers is the shape a later
  edit silently transposes. `pcrec_bufsurface_inert()` (src/gen/emit_dfa.c) is
  the DFA artifact's shape, spelled once: four zeros and an alignment of **1**,
  never 0 — a caller rounding an arena cursor UP to a 0 alignment divides by
  zero.
- **`pcrec_emit_prologue`** and **`pcrec_emit_info`** each take a
  `const BufSurface *`. The VM emitter computes ONE and passes the same struct
  to both, so the header's macros and `rx_info`'s fields cannot disagree: they
  are one value read twice, not two computations of one fact. The DFA emitter
  passes the inert shape.

The two structs the sizes MEASURE (`<prefix>_frame`, `<prefix>_trail_entry`)
are not declared here and must not be: they are per-artifact emitted text whose
layout three axes move (`has_linked_calls`, `--trace`, and the target's own
type sizes), which is why the descriptor is opaque and the sizes are stamped
and asserted rather than exported. See `src/gen/CLAUDE.md`'s [DD-14.FB] section.

## [OPT-4.1] `compile.c`'s build gate: the collapse and its DECLINE are one expression

The gate's four conjuncts were one `bool collapse`. They are now
`pfc_wanted` (the DFA is not the engine, the axis is not denied, there is a
collapsible repeat, and either the force flag or a ladder rung asked) and
`collapse = pfc_wanted && (force_prefilter || !lang_nullable)`. The split is what lets
the `_LANG_WHY` ladder branch on WHICH of the two happened without re-walking
anything (D81): `!collapse && pfc_wanted` is the decline and stamps
`PFLW_NULLABLE`, `!collapse && !pfc_wanted` is the old `PFLW_EXACT`/
`PFLW_NO_REP` pair.

**WHAT REACHES THIS LINE NULLABLE IS ONLY `-fprefilter-collapse`.** On a
ladder RUNG the decline happens one pass earlier, in `select_engine.c`'s
`fit.prefilter` clause, where it drops the prefilter entirely — because on a
rung the alternative to the collapsed machine is not the exact one, the exact
one being what failed, so declining HERE would send the compile back through
the construction that already overflowed and cost a third attempt. What
survives to the gate is a pattern that already has a working exact prefilter
and a caller asking for a collapsed one, and the right answer there is to keep
what it has.

`-fprefilter` is the one thing that overrides the decline, and the conjunct
here is load-bearing rather than symmetric: on the SIZE rung — the only rung
that reaches this line under that flag — the only prefilter that fits under the
cap IS the collapsed one, so declining it for a caller who explicitly demanded
a prefilter would REFUSE a pattern that compiles today, which is exactly what
`docs/spec/limits.md` §3.3 promises does not happen. On the [SEL-1] rung
`-fprefilter` never gets here at all: it makes that rung ineligible in
`compile_driver`, so the compile refuses earlier and for a different reason. `src/opt/CLAUDE.md` carries the predicate's own entry;
`docs/spec/tuning.md` §2.17 is the contract.

## [DD-13b.W1.3] the composer's three fields on `Ctx`, and one internal entry

- **`Ctx.ncap_primary`** — the PRIMARY pattern's own capture count, seeded
  by `compile_driver` from `ncap` immediately before `pcrec_rxt_compose`, on
  EVERY compile. `rx_info.ngroups` emits it; `RX_NCAPS` still emits
  `ncap + 1`. On a non-composed compile the two are equal by construction,
  which is what lets `src/gen/emit_dfa.c` read it unconditionally instead of
  asking whether composition happened.
- **`Ctx.defs`** — the `.rxt` definition closure, or NULL. Non-NULL only on
  the `--source` path (`pcrec_compile_defs`), so `pcrec_rxt_compose` is one
  pointer test on every other compile.
- **`Ctx.defer_file_refs`** — DERIVED from `defs` at compile entry and never
  set independently, so "the parser defers" and "a composer will resolve"
  cannot get out of step. Read at exactly one place,
  `pcrec_bref_resolve`'s call-by-name arm. It is a flag on `Ctx` rather than
  a change to `pcrec_parse_info` because that is the ONE parse entry point —
  shared by `--count-groups`, `--explain` and the built-status probe — and
  making it composition-aware would put a FILE-level concern inside the
  parser.

**`pcrec_compile_defs` is `pcrec_compile` plus a definition set**, and the
two share `compile_driver`, so there is exactly one compile pipeline and
`--source` cannot acquire a second one. It is INTERNAL and deliberately not
a `pcrec_options` field: D20 keeps the public option surface scalar, and a
definition closure is a FILE's property that only the `.rxt` reader can
build. A library caller that wants composition gets it through [LIB].
