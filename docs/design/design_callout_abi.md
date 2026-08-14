# Callout-ABI ↔ match-here alignment — proposal for the M4 match-API freeze

STATUS: PROPOSAL (manager-drafted, eighteenth session, 2026-08-14;
direction confirmed by Frank in-session: *"align the regex parse function
with the callout callback function so the interface was the same and you
could use the regex parse function as a callout"*). Remaining syntax and
semantic choices are FRANK'S (the [M4-CALLOUTS] 2026-08-13 amendment).
GATE: decided BEFORE M4's match-API design freezes (same gate as [PC-5]).
Sources: plan row [M4-CALLOUTS] (docs/dev/plan.md), D36 (decisions.md),
the [M4-SUBST] row's reuse of the static-extern primitive. No panel yet; a
D6 panel reviews this alongside the M4 match-API design when that design
exists.

## 1. The ruled direction

ONE signature serves both roles:

    typedef ptrdiff_t rx_matchfn(const char *subject, size_t len, size_t pos);
    /* returns matched length >= 0 (anchored at pos), or -1 for no match */

- Every generated matcher EXPORTS an anchored match-here entry of this
  shape (OS-0's named entry points are the natural vehicle).
- Every callout site BINDS an extern of this same shape
  (`extern ptrdiff_t rx_callout_n(const char *, size_t, size_t);`),
  compile-time bound, zero cost when absent (D36's static-extern
  primitive, signature updated to the aligned shape).

Because the two are IDENTICAL, a compiled matcher is a valid callout by
plain linking — link-level regex composition, no adapter, no shim. This
is the alignment being ruled on.

## 2. The semantic split the one signature carries (state it honestly)

A PCRE2-style callout and a composed submatcher are different operations
sharing the shape:

- OBSERVER use (`(?C...)`): zero-width. The function inspects and
  returns 0 (continue; zero bytes consumed) or −1 (fail this path). It
  is the degenerate consumer.
- COMPOSITION use: the callee CONSUMES input — its returned length
  advances the outer position. It is OPAQUE to the automaton: atomic
  (the outer engine takes the callee's one priority-first answer and
  never backtracks into it for alternatives) and un-fusable,
  partitioning the outer pattern into [M4.0]'s DFA islands around call
  points.

PCRE2's <0 abort has no slot in the aligned shape. Proposal: abort stays
a PCRE2-compat-layer concept (§3); a native callout/submatcher can only
match (length) or fail (−1). If Frank wants native abort, reserve −2 —
default proposal is NOT to (§5 Q3).

## 3. Where the pcre2_callout_block mirror lives now

D36's field-for-field `pcre2_callout_block` mirror is NOT lost — it moves
to where D36 already put the PCRE2-shaped surface: the COMPAT LAYER, and
because pcrec is AOT, that layer is a GENERATION-TIME BINDING, not a
runtime wrapper:

- Native mode (default): call sites invoke the aligned-signature extern
  directly. No block is built; patterns without callouts pay nothing,
  patterns with them pay one direct call.
- PCRE2-compat mode (V-A, or an emit flag when V-A lands): the GENERATOR
  emits block assembly at the call site — it has every field's value in
  scope there (capture-so-far vector, callout number/string, pattern
  offset) — and calls a block-shaped extern with D36's 0/>0/<0 return
  contract, D26-exact. `pcre2_set_callout` trampolines on top of that,
  exactly as D36 rules.

This dissolves the tension the plan row flagged: a runtime trampoline
above a narrow primitive could never reconstruct state it was not
passed, but an AOT generator emitting the block AT the call site has all
of it. The block mirror is a compat-mode code-generation choice; the
aligned signature is the one primitive.

## 4. What this imposes on the M4 match-API freeze

Freeze-time obligations if accepted; they cost nothing at M4 even if
callout behavior ([M4-CALLOUTS] step 2) lands much later:

- **F1**: every generated matcher exports the anchored match-here entry —
  name (OS-0 convention, e.g. `<prefix>_match_here`), the §1 signature,
  and the length-or-−1 return convention frozen. Signed `ptrdiff_t` so
  fail (−1) and empty match (0) stay distinct.
- **F2**: the entry is self-contained and reentrant (no hidden globals),
  consistent with the emitted code's existing no-runtime-dependency
  property.
- **F3**: callout externs use the same signature; the block-shaped
  variant exists only in PCRE2-compat generation mode (§3) and its block
  mirrors pcre2_callout_block field for field (D26-exact there, and only
  there).
- **F4**: composed submatchers cannot abort the outer match — match or
  fail only (pending §5 Q3).
- **F5**: capture OPACITY across the composition boundary — the outer
  pattern does not see the inner matcher's captures in v1. Cross-unit
  capture visibility belongs to [V-E]'s manifest design, not here.
- **F6**: [M4-SUBST]'s callback template segments reuse this same
  aligned extern primitive verbatim (its row already says so); the
  subst design note should consume the §1 typedef rather than invent a
  sibling.

## 5. Open questions for Frank (numbered, rulings requested)

1. Confirm the §1 signature spelling: `ptrdiff_t (const char *subject,
   size_t len, size_t pos)` — argument order, `char*` vs `uint8_t*`, and
   length-before-pos are freeze-frozen once M4's API freezes.
2. Does the exported match-here entry exist UNCONDITIONALLY on every
   generated matcher, or under an emit flag? (Recommendation:
   unconditional — small, and D37's stamping precedent favours artifacts
   carrying their full contract.)
3. Native abort: match-or-fail only (recommended), or reserve −2 for
   abort-the-outer-match?
4. Confirm capture opacity (F5) for v1 composition.
5. Pattern syntax for composition segments (which spelling binds a named
   extern as a submatcher) — deliberately unproposed here; it interacts
   with [V-E]'s named-definitions question and is recorded there as
   Q2/K4-tier (measured, not read).

## 6. Explicitly out of scope

- Callout BEHAVIOR itself ([M4-CALLOUTS] step 2, M4-hosted, VM-only per
  D36 — the compiled DFA erases fire positions).
- Fire-point discipline (ruled engine-relative in D36,
  PCRE2_NO_START_OPTIMIZE precedent).
- [V-E] manifest/named-definition composition (source-level inlining vs
  this link-level ABI — that comparison is V-E's own open question).
