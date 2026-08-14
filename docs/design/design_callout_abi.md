# Callout-ABI ↔ match-here alignment — proposal for the M4 match-API freeze

STATUS: PROPOSAL (manager-drafted, eighteenth session, 2026-08-14),
incorporating THREE in-session rulings from Frank (same day):

- R-a: *"align the regex parse function with the callout callback function
  so the interface was the same and you could use the regex parse function
  as a callout."*
- R-b: *"they should receive a structure that includes group captures thus
  far. perhaps this forces nfa. i like the idea of using it to do
  something like: `(\d+)(<fn_gt_100>)`"* — and, distant future, embedded
  code with restrictions: `(\d+)(<parse_int($1) > 100>)`.
- R-c: *"it may be that there are two forms or a switch for group vs not
  group."*
- R-d: *"syntax undecided. and the callout should probably use near
  pcre2 standards but the embedded code might be different like
  `\{ strlen($1) == 5 }` or something. tbd"* (supersedes the `(<name>)`
  sketch — see §3).

Remaining syntax and semantic choices are FRANK'S ([M4-CALLOUTS] 2026-08-13
amendment). GATE: decided BEFORE M4's match-API design freezes (same gate
as [PC-5]). Sources: plan row [M4-CALLOUTS], D36, [M4-SUBST]'s reuse of
the static-extern primitive. No panel yet; a D6 panel reviews this
alongside the M4 match-API design when that design exists.

## 1. The aligned shape: one context-struct signature on both sides

R-a wants matcher and callout to share ONE interface; R-b wants the
callout to see captures-so-far. Three bare scalars `(subject, len, pos)`
cannot carry captures, so the alignment moves to a CONTEXT STRUCT that
both sides take:

    typedef struct rx_ctx {
        const char     *subject;   /* whole subject, not a slice */
        size_t          len;       /* subject length */
        size_t          pos;       /* where to match, anchored */
        size_t          ncap;      /* capture slots known so far */
        const ptrdiff_t (*caps)[2];/* [start,end) pairs; -1,-1 = unset */
    } rx_ctx;

    typedef ptrdiff_t rx_matchfn(const rx_ctx *ctx);
    /* returns matched length >= 0 (anchored at ctx->pos), or -1 */

- Every generated matcher EXPORTS an anchored match-here entry of type
  `rx_matchfn` (OS-0's named entry points are the vehicle). A top-level
  caller invokes it with `ncap = 0, caps = NULL`; the matcher never
  requires inbound capture state.
- Every callout site BINDS an extern of the same type
  (`extern ptrdiff_t rx_callout_fn_gt_100(const rx_ctx *);`),
  compile-time bound, zero cost when absent (D36's static-extern
  primitive, signature updated to this shape).
- At a callout site the ENGINE fills `ncap`/`caps` with the captures
  completed so far — Frank's `(\d+)(<fn_gt_100>)` case: the callout reads
  `caps[1]`, parses the digits, and returns 0 (accept, zero-width) or −1
  (fail this path).

Because the two types are IDENTICAL, a compiled matcher links directly as
a callout (it simply ignores `ncap`/`caps`) — link-level regex
composition with no adapter. R-a and R-b are both satisfied by the same
struct.

## 2. Engine forcing — Frank's "perhaps this forces nfa," confirmed

Yes, and it was already ruled: D36 marks callouts ENGINE-FORCING (the
compiled DFA erases the pattern positions a callout fires at), and
captures-so-far additionally requires the engine that tracks captures —
both point at M4's VM (NFA-simulation) engine. A pattern containing a
callout compiles to the VM engine only. The DFA-islands picture from
[M4.0] still applies AROUND call points: the callee is OPAQUE — atomic
(the outer engine takes its one priority-first answer, never backtracks
into it) and un-fusable.

Semantic split the one signature carries (stated honestly):

- OBSERVER/PREDICATE use (`(?C...)`, and shapes like `(<fn_gt_100>)`):
  returns 0 (continue, zero bytes consumed) or −1 (fail this path) —
  the degenerate consumer.
- COMPOSITION use: the callee CONSUMES input; its returned length
  advances the outer position.
- PCRE2's <0 abort has no slot: native callouts match-or-fail only;
  abort stays a PCRE2-compat-layer concept (§4). If Frank wants native
  abort, reserve −2 — default proposal is NOT to (§6 Q3).

## 3. Syntax family — UNDECIDED (Frank, 2026-08-14 second ruling: *"syntax
undecided. and the callout should probably use near pcre2 standards but
the embedded code might be different like `\{ strlen($1) == 5 }` or
something. tbd"*)

What IS directional, superseding this doc's earlier `(<name>)` sketch
(recorded here so the earlier sketch is not mistaken for a leaning):

- CALLOUT BINDING: probably NEAR-PCRE2 — the `(?C...)` family PCRE2
  already owns. PCRE2's string form `(?C"text")` is the natural carrier
  for a function name (`(?C"fn_gt_100")` binding the extern), which
  keeps the callouts module's pattern layer D26-close and rides the
  `(?C` doorway [M4-CALLOUTS] step 1 is flipping to PLANNED anyway.
  Nothing here is ruled; "near pcre2 standards" is the constraint.
- EMBEDDED CODE (distant future): possibly a DIFFERENT spelling from the
  callout family — Frank's sketch: `\{ strlen($1) == 5 }`. A restricted
  expression language over `$n` compiled INTO the generated C (AOT: the
  pattern author is the developer, the expression lands as
  compile-time-visible C — trusted input per D22, but "with
  restrictions": no statements, no side effects; restriction set TBD).
  The extern form remains the primitive; embedded code subsumes its
  common cases without linking. Shares namespace discipline with
  [M4-SUBST]'s template callbacks (SR-10).
- R-c: possibly TWO FORMS or a switch — a GROUP form (the callee's
  consumed span is itself a capture group, numbered like any `(...)`)
  and a NON-GROUP form (zero-width predicate / non-capturing consumer).
  Spellings deliberately unproposed; recorded as §6 Q5.
- COLLISION RULE (holds for ANY spelling chosen): a spelling that
  reinterprets a currently-valid pattern must be MODULE-GATED. This
  bites both sketches to date: `(<x>)` is today a group matching literal
  `<x>`, and `\{` is today an escaped literal `{` — so with module
  `callouts` (or the future embedded-code module) disabled, today's
  parse stands; enabled, the new doorway opens. D37's set-graduation
  mechanics govern if either ever reaches a bare default. The
  near-PCRE2 `(?C...)` family is the one candidate with NO collision —
  `(?C` is already a rejected doorway, which is a point in its favor.

## 4. Where the pcre2_callout_block mirror lives

D36's field-for-field `pcre2_callout_block` mirror is NOT lost — it moves
to the PCRE2-compat surface, and because pcrec is AOT that layer is a
GENERATION-TIME BINDING, not a runtime wrapper:

- Native mode (default): call sites build the lean `rx_ctx` (cheap: the
  engine already owns every field) and call the extern directly.
- PCRE2-compat mode (V-A, or an emit flag when V-A lands): the generator
  instead emits pcre2_callout_block assembly at the call site — it has
  every field in scope there, including the capture vector `rx_ctx`
  already carries — and calls a block-shaped extern with D36's 0/>0/<0
  return contract, D26-exact. `pcre2_set_callout` trampolines on top,
  exactly as D36 rules.

The old tension (a runtime trampoline cannot reconstruct state it was
never passed) is dissolved twice over: generation-time assembly, and an
rx_ctx that now carries captures anyway.

## 5. What this imposes on the M4 match-API freeze

- **F1**: every generated matcher exports the anchored match-here entry:
  name (OS-0 convention), the §1 `rx_matchfn` type, length-or-−1 return.
  Signed `ptrdiff_t` keeps fail (−1) distinct from empty match (0).
- **F2**: the entry is self-contained and reentrant; it must accept
  `ncap = 0, caps = NULL` (no inbound capture dependence).
- **F3**: `rx_ctx`'s layout is part of the frozen ABI. The capture
  representation in `rx_ctx.caps` must BE the match API's capture-offset
  contract (one representation, not a conversion) — this couples to the
  [M4-SUBST] design note's capture-offset contract; the two must land on
  the same pair shape. Unset = {−1,−1}.
- **F4**: composed submatchers/callouts cannot abort the outer match —
  match or fail only (pending §6 Q3).
- **F5**: capture VISIBILITY IN, opacity OUT: a callout SEES the outer
  captures-so-far (R-b), but the outer pattern does not see an inner
  matcher's own captures in v1. Cross-unit capture export belongs to
  [V-E]'s manifest design. (R-c's GROUP form captures the callee's
  consumed SPAN — that is the outer engine's own capture of [pos,
  pos+ret), not an export of inner state, so it stays inside F5.)
- **F6**: [M4-SUBST]'s callback template segments reuse this same
  `rx_matchfn`/`rx_ctx` primitive verbatim; the subst design note should
  consume the §1 typedef rather than invent a sibling.
- **F7**: callout patterns force the VM engine; the registry/engine
  selection must be able to say so per-pattern (same per-pattern engine
  answer shape as the backrefs/atomic design notes under M4).

## 6. Open questions for Frank (numbered, rulings requested)

1. Confirm the §1 `rx_ctx` field set (anything else a callout should
   see — e.g. a user-data pointer, the callout's own site index?) and
   the struct-pointer calling convention. Frozen once M4's API freezes.
2. Does the exported match-here entry exist UNCONDITIONALLY on every
   generated matcher, or under an emit flag? (Recommendation:
   unconditional.)
3. Native abort: match-or-fail only (recommended), or reserve −2?
4. Confirm F5's boundary: callouts see outer captures-so-far; inner
   captures of a composed matcher stay opaque in v1.
5. The syntax family — open by explicit ruling ("syntax undecided"),
   under the "near pcre2 standards" constraint for the callout binding:
   is `(?C"name")` the extern-binding spelling? Plus the R-c
   group-vs-non-group pair (two forms? a switch?), and the
   embedded-code spelling (`\{ ... }` or other) whenever that distant
   work is scheduled. Interacts with [V-E]'s named-definitions question.
6. Embedded-code restrictions (distant future; no scheduling asked):
   expression-only over `$n` as sketched, or a broader-but-bounded set?

## 7. Explicitly out of scope

- Callout BEHAVIOR implementation ([M4-CALLOUTS] step 2, M4-hosted,
  VM-only per D36).
- Fire-point discipline (ruled engine-relative in D36,
  PCRE2_NO_START_OPTIMIZE precedent).
- [V-E] manifest/named-definition composition (source-level inlining vs
  this link-level ABI — V-E's own recorded open question).
