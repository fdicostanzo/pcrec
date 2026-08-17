# Callout-ABI ↔ match-here alignment — proposal for the M4 match-API freeze

> ## PANEL OUTCOME (R21) — READ BEFORE ANY SECTION BELOW
>
> This document's FIRST panel review (R21,
> `docs/dev/reviews/2026-08-14-r21-m4-design.md`; dispositions ratified in
> `docs/dev/decisions.md` D44) reviewed it as a ruled input alongside
> `match_api_m4.md` and `engine_m4.md`. Two backports land this round,
> both FIX-NOW: **F8 is SUPERSEDED** — the group index it describes as
> freestanding symbols folded into `rx_info` at D43.1 and gained a `slot`
> column at D44.3; the customer this section named is also corrected
> (C-2/A-13, §5 below). **A new F9** records D42.5's callout caps-lifetime
> line, which this document never carried despite being the ABI's own
> home (C-3, §5 below). A POST-RULING UPDATES block at §5's end records
> that D41–D44 landed after this document's text and that
> `match_api_m4.md` carries the applied surface — this document stays the
> historical record, per house style, rather than being rewritten to
> match it.

STATUS: RULED (D38, 2026-08-14) — `docs/dev/decisions.md` D38 applies the
rulings below to §1, §2, §4, §5 and §6. Two items remain OPEN: the syntax
family (§6 Q5, per R-d) and the embedded-code restrictions (§6 Q6, distant
future); everything else in this document is settled.

STATUS (as drafted): PROPOSAL (manager-drafted, eighteenth session,
2026-08-14), incorporating THREE in-session rulings from Frank (same day):

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
        const unsigned char *subject;  /* whole subject, not a slice */
        size_t               len;      /* subject length */
        size_t               pos;      /* where to match, anchored */
        size_t               ncap;     /* capture slots known so far */
        const ptrdiff_t     (*caps)[2];/* [start,end); -1,-1 = unset */
        void                 *user;    /* RULED (D38): per-binding user data */
    } rx_ctx;

(`unsigned char *` per the subst note's §2.4 finding: char signedness is
implementation-defined and the emitter indexes 256-entry class tables
with subject bytes. `ncap` is a mid-match watermark at a callout site;
on a COMPLETED match it is pinned to ngroups + 1 with every pair written
— the subst note's C6.)

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

### 1.1 RULED (D38): the BINDING UNIT is a struct, and `rx_ctx` carries `user`

`rx_ctx` gains a `void *user` field (above); the engine fills `ctx->user`
from the binding reference before every call. The thing a callout site
actually binds is not the bare function symbol above but a small const
struct wrapping it:

    typedef struct rx_callout_ref {
        rx_matchfn *fn;
        void       *user;
    } rx_callout_ref;

    extern const rx_callout_ref rx_callout_<name>;

— one `extern const rx_callout_ref rx_callout_<name>` per callout. The
engine reads `ref->user` into `ctx->user`, then calls `ref->fn(ctx)`.
Composition (using a compiled matcher as a callout) is a one-line const
struct wrap: `const rx_callout_ref rx_callout_x = { inner_match_here,
NULL };` — no adapter code.

State is per-binding (the `user` pointer each `rx_callout_ref` carries).
Per-THREAD state is the callout's own business via its own
`_Thread_local` storage — an `&tls_var` static initializer does not
compile, so a callout wanting thread-local state manages that itself
inside `fn`, not through `user`.

**Rejected (D38):** a single process-global `user` pointer (one value
shared by every callout — defeats the point of per-binding state), and a
per-call `user` parameter threaded through every call site (Frank:
"ouch" — over-callback-friendly, and it changes `rx_matchfn`'s signature
for every caller to serve the minority that needs it).

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

**RULED (D38):** native abort is NONE in v1 — match-or-fail only, as
proposed. Return values < −1 are RESERVED for a future abort semantic
and, so the reservation is not merely a comment, ENFORCED TODAY at every
generated call site: `if (ret < -1) __builtin_trap();`
(freestanding-safe — no libc dependency, so it holds on the no-libc
line). `abort()` was rejected: it needs libc. `longjmp` was also
rejected: it costs a `setjmp` on the warm entry path even when never
taken, and it interacts badly with `volatile`-local requirements at
`-O2`. `__builtin_trap()` with −2 reserved gives the same expressiveness
on the (rare, cold) path a future real abort would take, at zero cost on
the path that matters.

**AMENDED (D49, 2026-08-17) — the trap SURVIVES; its BOUND moves from a
literal to a name, and −2 is no longer the abort reservation's to spend.**
D49 partitions the `< −1` space: `[RX_ERR_FLOOR, −2]` are TYPED GIVE-UP codes
that a matcher legitimately returns (`RX_ERR_STEPS`, `RX_ERR_FRAMES`,
`RX_ERR_WORK`), and only values strictly below the floor stay reserved for
abort. F2's obligation therefore reads:

    if (ret < RX_ERR_FLOOR) __builtin_trap();

and a call site must ALSO propagate a give-up rather than treating it as a
path failure — one line, before the trap check. That propagation is the point:
under the old collapse an inner matcher's give-up became a plain "this path
did not match", so the OUTER match could report an answer where a bound had
blown.

Two consequences worth stating for whoever writes the first call site. The
sentence above about "−2 reserved" is the one part of this ruling that did not
survive: a future native abort needs an encoding below the floor, and how much
room the give-up block gets was fixed before anyone knew how many codes it
would eventually hold. And the trap's own rationale is UNCHANGED and still
correct — freestanding-safe, zero cost on the warm path, `abort()`/`longjmp`
still rejected for the reasons above. Nothing here was cheap to change later
and expensive now; it was the reverse, which is why it changed now: VERIFIED
at ruling time that ZERO generated files contain the trap line, because this
module has no producer (`emit_vm.c`'s `VE_CALLOUT` is marked reserved), so
the codegen this amendment governs does not yet exist.

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

**RULED (D38):** confirmed as proposed. Abort in PCRE2-compat mode needs
no native abort mechanism at all — it is discharged entirely by the
generated call site: when the block-shaped extern returns < 0, the call
site jumps directly to the fail epilogue, exactly as any other failed
match would. Compat-mode "abort" is generation-time control flow, not a
runtime signal threaded back through `rx_matchfn`'s return convention.

## 5. What this imposes on the M4 match-API freeze

- **F1**: every generated matcher exports the anchored match-here entry:
  name (OS-0 convention), the §1 `rx_matchfn` type, length-or-−1 return.
  Signed `ptrdiff_t` keeps fail (−1) distinct from empty match (0).
- **F2**: the entry is self-contained and reentrant; it must accept
  `ncap = 0, caps = NULL` (no inbound capture dependence). **RULED
  (D38):** F2 additionally requires every generated call site to enforce
  the reserved-return-space rule with `if (ret < -1)
  __builtin_trap();` — the trap is part of F2, not a separate freeze
  item, because it is a property of the same call-site codegen F2
  already governs.
- **F3**: `rx_ctx`'s layout is part of the frozen ABI. The capture
  representation in `rx_ctx.caps` must BE the match API's capture-offset
  contract (one representation, not a conversion) — RECONCILED
  2026-08-14: the [M4-SUBST] note's §2.4 ADOPTS `ptrdiff_t[2]` /
  {−1,−1}-unset as the contract (its C4/C5). Consequence it returns:
  one-representation means the ALREADY-EMITTED `<prefix>_span`
  (`size_t start,end` — emit_dfa.c) must become this pair type or go —
  a breaking change to a shipped generated contract, i.e. a [DD-3]
  generated-API-versioning event to schedule WITH the M4 freeze, not
  after it (subst note Q12).
- **F4**: composed submatchers/callouts cannot abort the outer match —
  match or fail only. **RULED (D38, §6 Q3):** confirmed, no longer
  pending — v1 ships match-or-fail only, −2 reserved and trapped per F2.
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
- **F8** (D39.1 + addendum, `docs/dev/decisions.md`): every generated
  pattern EXPORTS a static const name→number group index — a sorted
  `{const char *name; int number; const char *ref;}` array plus count,
  bsearch-able. The `ref` column is BORN INTO the frozen shape (NULL for
  the primary's own groups): it carries the labeled insertion reference
  ("a:reg1" style; nested insertions compose a path, "c:a") once V-E's
  rx references exist — so V-E extends data, not ABI,
  `.rodata` only, zero runtime cost. It does NOT travel in `rx_ctx` or
  any callback parameter (it is a link-time constant per pattern, not
  per-call state); a callout wanting it links against the exported
  symbol directly. Second customer: V-A's
  `pcre2_substring_number_from_name`.

  **SUPERSEDED (D43.1/D44, ratifying R21 C-2/A-13) — kept as history, not
  the current shape.** This section still describes F8 as FREESTANDING
  symbols (`<prefix>_group_entry`/`<prefix>_groups[]`/`<PREFIX>_NGROUPS`)
  — D43.1 (2026-08-14, same session, after this document's text was
  written) folds the index into `rx_info` instead: it becomes the
  `groups`/`nnames` members of one reflection struct, `extern const
  rx_info <prefix>_info` per artifact, rather than three freestanding
  per-artifact symbols. The R21 panel found this document was the ONE
  place in the repository still specifying the superseded freestanding
  form with zero D41/D42/D43 mentions (C-2) — a staleness gap this
  backport closes. Three things changed beyond the container:
  - **The element type gained a column.** D44.3 (ratifying R21 A-4) BORN
    `rx_group_entry` with `{name, number, slot, ref}` — a `slot` field
    between `number` and `ref` that this section's `{name, number, ref}`
    triple does not have, closing a pre-V-E out-of-bounds read the panel
    found reachable (`--no-captures '(?<g>a)'` names a group with no caps
    slot to point at; `slot == -1` now says so explicitly instead of
    leaving a reader to assume `slot == number`).
  - **The customer this section names is CORRECTED.** "V-A's
    `pcre2_substring_number_from_name`" is superseded by D43's own text:
    the second customer is V-A's `pcre2_pattern_info`, which reads the
    WHOLE `rx_info` struct (flags, encoding, the three counts, the
    engine, the budget), not `rx_info.groups` in isolation the way the
    narrower `pcre2_substring_number_from_name` framing implied.
  - **The full current shape lives at `match_api_m4.md` §5**, D44.5's
    hardened layout (`abi` first member, widened `flags`/`step_budget`,
    the `ncaps`/`ngroups`/`nnames` three-count split, `engine`/
    `engine_why`, `pattern`/`pattern_len`, `frame_capacity`/
    `subject_ceiling`) — this section is not updated to match it in
    place; the pointer is deliberate, per this document's own house
    style of appending rather than rewriting.

- **F9** (NEW, D42.5, backported per R21 C-3): `rx_ctx.caps` handed to a
  callout is valid for the DURATION OF THE CALL ONLY. The engine rewrites
  the same storage afterwards (trail-based undo, `engine_m4.md` §2.4/
  §3.4 — the slots a callout reads are not a private copy). A callout
  that retains the pointer past its own call and reads it later is the
  EMBEDDER'S BUG, not a pcrec contract violation; nothing in the
  generated code detects or guards against it. **The panel found this
  line ABSENT from this document entirely** — not merely as an unnumbered
  F-item, but nowhere in its text — despite being exactly the kind of
  callout-lifetime property this document's F1–F8 exist to state, and
  despite `rx_ctx.caps` (§1's own struct) being this document's own
  field. It was raised at `engine_m4.md` §12 ASK-3 and ruled at D42.5 the
  same session; this backport is the first time it lands in the document
  that actually owns the `rx_ctx` type it constrains.

## 6. Open questions for Frank (numbered, rulings requested)

1. **RULED (D38):** confirmed — the §1 `rx_ctx` field set is settled
   with the addition of `void *user` (§1.1), carried via the
   `rx_callout_ref` binding unit rather than as a bare extra field a
   callout reaches for directly. Struct-pointer calling convention
   confirmed. Frozen at the M4 API freeze as planned.
2. **RULED (D38):** UNCONDITIONAL — the exported match-here entry exists
   on every generated matcher, no emit flag, per the recommendation.
3. **RULED (D38):** match-or-fail only; −2 (and everything below −1) is
   RESERVED for a future abort semantic and enforced today via F2's
   `__builtin_trap()` call-site check. See §2's ruling for the rejected
   alternatives (`abort()`, `longjmp`).
4. **RULED (D38):** confirmed — F5's boundary holds. Callouts see outer
   captures-so-far; a composed matcher's own inner captures stay opaque
   in v1. The v2 path (declared-in-syntax export, `(?Cc<n>"fn")`
   direction, non-const ctx + capacity field, a DD-3 struct revision) is
   recorded, not scheduled.
5. **OPEN** — stays exactly as ruled by R-d: syntax undecided. This is
   the one item this document leaves open by Frank's own explicit
   ruling, not an oversight. The callout-binding constraint ("near pcre2
   standards") and the R-c group-vs-non-group question are unchanged;
   revisit when syntax work is scheduled.
6. **OPEN** — embedded-code restrictions remain unruled; distant future,
   no scheduling asked, unchanged by D38.

## POST-RULING UPDATES (D41–D44, backported 2026-08-14)

This document's text predates D41, D42, D43 and D44 — all four landed in
the SAME session that ruled D38 above, but later in it, after this
document's prose was written. Rather than rewrite this document's body to
track every subsequent ruling (the house-style choice this project makes
throughout `docs/design/`: append, don't silently rewrite), this section
records what changed and where the CURRENT applied surface lives:

- **The ABI type family grew.** D41.1 confirms `rx_ctx`/`rx_matchfn`/
  `rx_callout_ref` (this document's own types) as fixed-literal, never
  `--prefix`-scoped — exactly as spelled throughout this document, now
  RULED rather than merely this document's own convention. D43.1 adds
  `rx_info`/`rx_group_entry` to the same family (§5's F8 backport above).
- **`rx_ctx.caps`'s representation changed shape at the freeze**, per
  `match_api_m4.md` §1.0 (D44.2): the SEARCH ENTRY that fills a caller's
  caps array now takes `ptrdiff_t (*caps)[2]` directly rather than a
  `<prefix>_span` out-parameter — `rx_ctx.caps` itself (this document's
  own `const ptrdiff_t (*caps)[2]` field, §1) is UNCHANGED by that reshape,
  since it was already the pair-array shape; only the SEARCH entry's own
  parameter, a different struct this document does not define, changed.
- **The match-here entry gained a capture-delivering sibling**
  (`<prefix>_match_caps`, D41.4) and the search entry gained reserved
  negative-return codes (D42.3) — neither is this document's business
  (they are match-API surface, `match_api_m4.md` §3.1/§1), noted here only
  so a reader of THIS document's F1/F2 does not assume `rx_matchfn` is the
  only way to get captures out of a compiled matcher.
- **`match_api_m4.md` is the applied surface.** Any conflict between a
  reading of this document and `match_api_m4.md`'s current text resolves
  in `match_api_m4.md`'s favor — this document remains authoritative for
  the callout-ABI DESIGN RATIONALE (why one context struct, why the
  binding-unit indirection, why captures are visible in/opaque out) but
  not for the exact current struct layouts, which move faster than this
  document is updated.

## 7. Explicitly out of scope

- Callout BEHAVIOR implementation ([M4-CALLOUTS] step 2, M4-hosted,
  VM-only per D36).
- Fire-point discipline (ruled engine-relative in D36,
  PCRE2_NO_START_OPTIMIZE precedent).
- [V-E] manifest/named-definition composition (source-level inlining vs
  this link-level ABI — V-E's own recorded open question).
