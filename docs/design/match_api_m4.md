# M4 match-API freeze — the collected contract

**STATUS: PROPOSED.** This document does not itself rule anything; it
collects rulings that already exist (`docs/dev/decisions.md` D38, D39, and
D38's PC-5 disposition of `docs/pcre2_options.md`) into one place, precisely
enough that [M4.4] can apply the break mechanically and [M4.3]'s panel can
attack a single surface instead of three overlapping documents. **The freeze
does not take effect until AFTER [M4.3]'s panel closes.** Until then this is
a draft of the contract, not the contract.

## How to read this document

Every substantive claim below carries one of three marks:

| mark | meaning |
|---|---|
| **RULED (Dnn)** | Frank has ruled this; cited to the decision. Not open, but the panel may still attack the *consequence* drawn from it. |
| **PROPOSED-here** | this document's own synthesis — either a concrete spelling the rulings implied but did not state, or a reconciliation of a tension between two ruled inputs. NOT a ruling. Collected in §12 for the manager. |
| **BELIEVED** | consistent with the rulings and the existing shipped contract as read, but not independently re-derived here; flagged so the panel knows where to spend attacker time. |

Two documents carry the applied rulings today and are the ones this freeze
reconciles: `docs/design/design_callout_abi.md` (the callout/match ABI, F1–F8)
and `docs/design/subst_template_design.md` (the capture-offset contract,
C1–C11, §9's fourteen rulings). On any conflict between this document and
`docs/dev/decisions.md` D38/D39, **the decision log wins** — this document is
a restatement, not a new source of authority.

---

## 0. Scope note: two different "prefix" namespaces

Two unrelated naming surfaces are both discussed below and must not be
conflated, because §8's PCREC_*/PCRE2_* ruling governs only one of them:

1. **Per-artifact emitted symbols**, scoped by the caller's `pcrec_options.prefix`
   (default `"rx"`) — `<prefix>_search`, `<prefix>_span` today; `RX_NCAPS`,
   `RX_UNSET` in the design docs' examples are this family, spelled with the
   *default* prefix uppercased. A caller compiling with `--prefix foo` gets
   `FOO_NCAPS`, `foo_search`, etc. This is [OS-0]'s territory.
2. **pcrec's own library-level compile-option namespace** (`PCREC_ENC_ASCII`
   today in `lib/pcrec.h`; future flag constants from the PC-5 survey) — fixed,
   never scoped by the caller's prefix, because these are pcrec's own API
   surface, not generated per pattern. D38's addenda (§8 below) govern *this*
   namespace only.

`pcrec_error`'s new which-input tag (§6) belongs to namespace 2. `RX_NCAPS`/
`RX_UNSET`/the group-index symbols (§2, §5) belong to namespace 1 and are
untouched by the PCREC_*/PCRE2_* ruling.

---

## 1. The `rx_span` → `ptrdiff_t[2]` pair break

**RULED (D38 Q12):** *"`rx_span` BREAKS AT THE M4 FREEZE — becomes the
`ptrdiff_t` pair type in one announced break (Frank: `ptrdiff_t` 'clearer in
a utf environment'); no permanent conversion seam."*

**Today's emitted contract** (`src/gen/emit_dfa.c:104-119`, `lib/pcrec.h`):

```c
typedef struct { size_t start, end; } <prefix>_span;
int <prefix>_search(const unsigned char *s, size_t n, size_t startpos,
                     <prefix>_span *m);
```

`tests/harness/driver.c` consumes this shape today; it is the only public
generated artifact that changes representation at the freeze.

**What it becomes.** `design_callout_abi.md` F3 requires *one* capture
representation, not a conversion between two: `rx_ctx.caps` is
`const ptrdiff_t (*)[2]`, `{-1,-1}` = unset (§2 below). "No permanent
conversion seam" (D38 Q12) rules out keeping `<prefix>_span` as a
`size_t`-typed struct alongside a new `ptrdiff_t`-typed `caps` array forever —
the two must become the same representation. Concretely, the whole-match span
**is** `caps[0]`: a half-open `[start, end)` pair, `ptrdiff_t` elements,
`{-1,-1}` on no match rather than the caller-facing `int` return already
doing that job.

**PROPOSED-here (§12.1)** the concrete spelling M4.4 emits, since neither
D38 nor the two carrying docs pick one:

```c
typedef ptrdiff_t <prefix>_span[2];   /* [start, end); {-1,-1} on no match */
int <prefix>_search(const unsigned char *s, size_t n, size_t startpos,
                     <prefix>_span *m);
```

i.e. `<prefix>_span` stays the name `emit_span_typedef` already emits and
`<prefix>_search` keeps its existing signature shape — only the element type
and struct-vs-array representation change, to `ptrdiff_t[2]`, so that a
`<prefix>_span` and a `caps[k]` pair are byte-for-byte, type-for-type
identical (F3's "one representation" read literally: not merely
same-field-types, but the *same type*). This is what makes `caps[0]` and the
top-level `<prefix>_search` output interchangeable without a cast or a
conversion function anywhere in generated or embedder code.

**Exactly which artifacts change**, so [M4.4] is a checklist rather than a
rediscovery:

- `src/gen/emit_dfa.c`: `emit_span_typedef` (the `size_t start, end` struct
  literal at line 106) and every `%s_span *m` declaration site.
- `lib/pcrec.h`: the doc comment describing `<prefix>_search`'s contract
  ("byte offsets, end exclusive" — update the type, not the semantics).
- `tests/harness/driver.c` and any other consumer of `.start`/`.end` field
  names — the array form above has no field names, so these become `m[0][0]`/
  `m[0][1]` or an equivalent macro; **PROPOSED-here**, this is exactly the
  kind of consumer-side churn D37's "one announced break commit" shape exists
  to bound: it lands in the SAME commit as the emitter change, not staged.
- Anywhere the corpus or codegen structural checks grep for `_span` or
  `size_t start, end` (`tests/codegen/run_codegen_tests.sh`, per its own
  CLAUDE.md note about symbol-pattern greps degrading silently when the
  underlying shape changes — the same hazard OS-0b already fixed once for a
  different reason).

**This is a [DD-3] generated-API-versioning event**, scheduled to land WITH
the M4 freeze rather than after it (D38 Q12's own framing, subst note §9 Q12).
No deprecation period, no compat shim in the base contract — one break, one
commit, D37's "announced-boundary" shape (a version-line boundary, not a
silent drift).

**RULED (D41.5, 2026-08-14) — the search entry's POSTURE.** One-shot
`<prefix>_search` (find the leftmost match from `startpos`, return, caller
restarts at the previous end) is the v1 primitive, as a CHOSEN posture, not
a default: Frank raised the find-all / continued-search alternative
(motivated by SIMD block scanning — a first-match return discards the
block's remaining candidate work). Under PCRE2's sequential-match semantics
"find all" is the same result set, so the question is redone work only.
Ruled remedies: EMITTED LOOPS own dense-match iteration (the PC-5
EMITTED-LOOP disposition — global subst today, V-C grep later; the
generator owns the loop, so block context carries in locals); a
cursor/iterator entry (`<prefix>_iter` over a caller-declared,
per-pattern-sized carry struct) is the DESIGNATED ADDITIVE EXTENSION when
an embedder customer appears — deliberately not designed now; batch
find-all is REJECTED as a primitive (data-dependent output size,
capacity negotiation reinvents the cursor). See D41 for the full record.

**RULED (D42.3, 2026-08-14) — `<prefix>_search`'s negative-return space.**
Handed across from engine_m4.md §4.4/§4.5: `<prefix>_search` keeps returning
`int`, and its NEGATIVE values are RESERVED for engine-give-up conditions —
the search entry, unlike `rx_matchfn`, has room for a third outcome beyond
match/no-match, because D38.4's `< -1` reservation binds only the ABI type
`rx_matchfn`, not this per-artifact entry (engine §4.4's "`rx_search` is not
an `rx_matchfn`" observation). Two names are fixed now, cheap because the
space is empty today (STRUCTURAL: `<prefix>_search` returns exactly `1` or
`0`):

```c
/* <prefix>_search returns:
 *   1              match found, *m (and, once M4.5 lands, caps) written
 *   0              no match
 *   RX_ERR_STEPS   step budget (DD-2, engine §4.2) exhausted
 *   RX_ERR_FRAMES  backtrack-frame/trail capacity (engine §4.5) exhausted
 */
```

**Today's `1`/`0` contract KEEPS its meanings** — this reservation adds new
negative outcomes, it does not renumber the existing two. A DFA-only
artifact (pre-M4.5, or any `--no-captures` build, D42.1) never emits a step
or frame counter and so never returns either code; they become live only
once the counters exist on the VM path (engine §4.6). The concrete integer
values are [M4.4]'s emitter's to assign, not fixed by this ruling.

---

## 2. The caps array surface: `rx_ctx.caps`, `RX_NCAPS`, `RX_UNSET`, and the C1–C11 conformance table

**RULED (D38, applying subst note §10):** *"Adopt §2's C1–C11 as requirements
on M4's match API... together with §2.2's explicit non-requirements. C4 and C5
are now stated in the callout ABI's `rx_ctx.caps` representation, per F3."*

### 2.1 The frozen shape

```c
const ptrdiff_t (*caps)[2];   /* rx_ctx field; [start, end) pairs */
#define RX_NCAPS <ngroups + 1>          /* caller-facing macro, per pattern */
#define RX_UNSET ((ptrdiff_t)-1)        /* both slots of an unset pair */
```

(`RX_` here is the *default* prefix uppercased per §0 — a pattern compiled
with a different `--prefix` emits `<PREFIX>_NCAPS`/`<PREFIX>_UNSET`.)

- **Unset representation:** `{-1, -1}` in **both** slots of a pair (C5,
  AMENDED from PCRE2's `~(PCRE2_SIZE)0`-in-both-slots convention to the
  signed equivalent — `caps[k][0] < 0` is a single signed comparison).
- **Every pair `0..ngroups` is written on a completed match** (C6); no
  watermark, no guard needed at read time for a completed match.
- **`ncap` is a mid-match watermark at callout sites and is PINNED to
  `ngroups + 1` on a completed match**, with every pair written
  (design_callout_abi.md §1, subst §2.4(d)) — this is the reconciliation of
  C6 ("no watermarks") against the callout direction's genuine need for a
  watermark (captures-so-far, R-b): the tension resolves because they are
  properties of two different MOMENTS (mid-match vs. completed), not a
  contradiction over one field. **Lifetime of the pointer handed to a
  callout at that mid-match moment is a separate freeze line — §4's D42.5
  addition.**
- **Caller-owned, fixed-size, compile-time-sized** (C7): a caller declares
  `ptrdiff_t caps[RX_NCAPS][2];` on the stack; nothing in the generated
  contract allocates.

**RULED (D42.2, 2026-08-14) — `RX_NCAPS` states what the ARTIFACT delivers,
not what the pattern text contains.** Confirming engine_m4.md §5.7 (which
answered §13 ASK 4): capture-slot count is a property of the compiled
artifact, chosen at the SAME point the engine is chosen. A DFA-compiled
artifact emits `RX_NCAPS 1` always; `RX_NCAPS > 1` implies the VM engine,
enforced by a `tests/codegen/` structural check live from [M4.4]. C6 never
bends — for a DFA artifact `RX_NCAPS - 1 == 0`, so "every pair `0..ngroups`
written" is trivially `caps[0]` only, never an under-populated promise.

**RULED (D42.1, 2026-08-14) — captures are ON BY DEFAULT.** After [M4.5],
`pcrec 'a(b|c)+d'` emits a capture-tracking (VM) matcher, matching PCRE2's
own default and the principle of least surprise; `--no-captures` is the
GENERATION AXIS that recovers today's pure-DFA artifact (`RX_NCAPS 1`) for
callers who do not want group offsets. Before [M4.5] lands, and for any
`--no-captures` build after it, `RX_NCAPS` is 1 for every pattern — there is
no window in which a caller can ask for something nothing can deliver
(engine §5.7.3). The `RX_NCAPS` 1 → >1 change for group-bearing patterns
lands on the SAME announced D37 boundary as the `rx_span` break (§1; engine
§9.2(3), §5.7.3).

### 2.2 C1–C11 conformance table

| req | what it demands | how the frozen surface satisfies it |
|---|---|---|
| C1 | group count is a compile-time constant | `RX_NCAPS` is a `#define`, emitted per pattern; already backed today by `--count-groups` at compile time |
| C2 | O(1) indexed access by number, flat sequence | `caps` is `const ptrdiff_t (*)[2]` — a flat array, no iteration/search/cursor needed |
| C3 | index 0 is the whole match, exists at 0 groups | `caps[0]` is the whole-match span (§1); `RX_NCAPS >= 1` always (`ngroups + 1`, minimum 1) |
| C4 | byte offsets, half-open `[start, end)`, two-element pair | `ptrdiff_t[2]` per pair, AMENDED element type per D38 Q12 |
| C5 | distinguished unset value in BOTH slots, named constant | `{-1, -1}`; `RX_UNSET` macro so a caller never hard-codes either spelling |
| C6 | every pair `0..ngroups` written on every successful match | stated explicitly above; `ncap == ngroups + 1` is the completed-match contract |
| C7 | caller-owned, fixed-size, compile-time-constant count | `RX_NCAPS` macro; no allocation anywhere in generated code |
| C8 | spans stable for the duration of one splice | RULED (D38): the matcher MAY overwrite the caps buffer between separate match calls; a completed match's caps are stable until the NEXT match call reusing the same buffer — a documented consequence, not an accident |
| C9 | PCRE2 numbering: left-to-right by opening paren, non-capturing groups don't consume a number | unaffected by M4 — already the parser's shipped, measured behaviour (`--count-groups`) |
| C10 | name→number is compile-time, no runtime lookup REQUIRED for `${name}` resolution | the template compiler resolves `${name}` at pcrec-compile time and emits no names; **AMENDED by D39** — F8's group index (§5) is exported anyway, but for a DIFFERENT customer (embedders, V-A), not to satisfy C10 |
| C11 | success/failure is a return value, not an error object | `rx_matchfn`/the match-here entry returns `ptrdiff_t` (length, or `-1`); no error struct on the match path |

### 2.3 Explicit non-requirements (§2.2 of the subst note), carried forward as NOT promised

- No ovector sizing negotiation (pcrec knows the group count at compile time).
- No match-data object, no allocation, no lifecycle.
- No run-time "does group N exist" query (a compile-time check owns that).
- No run-time name lookup for **template resolution** — C10 stands for that
  purpose specifically. (F8's index is a separate obligation, not a
  contradiction of this — see §5.)
- No partial-match or streaming window state (M3's business if ever anyone's).
- No callout/callback context threading beyond what `rx_ctx` itself carries.

---

## 3. The unconditional match-here export (F1, F2)

**RULED (D38):** *"the match-here entry is exported UNCONDITIONALLY on every
generated matcher"* (§6 Q2 of design_callout_abi.md), *"self-contained...
must accept `ncap = 0, caps = NULL`"* (F2), with the reserved-return-space
enforcement folded into F2 as one property, not a separate freeze item.

```c
typedef ptrdiff_t rx_matchfn(const rx_ctx *ctx);
/* returns matched length >= 0 (anchored at ctx->pos), or -1 (fail).
 * Self-contained: must accept ctx->ncap == 0, ctx->caps == NULL. */
```

- **F1**: name per OS-0 (§7 below — PROPOSED-here since neither ruling picks
  a literal symbol); the `rx_matchfn` type; `ptrdiff_t` return, matched
  length or `-1`. Signed so fail (`-1`) is distinct from an empty match (`0`).
- **F2**: self-contained and reentrant — a top-level caller invokes it with
  `ncap = 0, caps = NULL`; the matcher never REQUIRES inbound capture state.
  **F2 additionally requires every generated CALL SITE that invokes an
  `rx_matchfn` to enforce**:

      if (ret < -1) __builtin_trap();

  This binds call sites that *call into* another `rx_matchfn` — callout
  invocations and composed-submatcher calls — not the exported entry's own
  internal `return`. **PROPOSED-here (§12.2), scope note for [M4.4]:** no
  such call sites exist yet — callout behaviour (M4-CALLOUTS step 2) is a
  boonies row explicitly NOT an M4 substep (per [M4.7]'s framing: "the VM
  design must merely not preclude its call sites"). So [M4.4] emits the
  match-here entry itself but does not yet need to emit any
  trap-enforcing call site; the obligation lands with whichever future work
  (callouts, V-E composition) first emits a call to an `rx_matchfn`.
- **Reserved value space**: return values `< -1` are RESERVED for a future
  abort semantic and are not produced by any pcrec-emitted matcher today.
  `abort()` (needs libc) and `longjmp` (setjmp cost on the warm path,
  `volatile`-local hazard at `-O2`) were both rejected in favour of
  `__builtin_trap()`, which is freestanding-safe.
- **F4** (confirmed, no longer pending): match-or-fail only in v1. Composed
  submatchers/callouts cannot abort the outer match.

### 3.1 `<prefix>_match_caps` — the anchored capture-delivering entry

**RULED (D41.4, 2026-08-14):** an anchored capture-DELIVERING entry JOINS the
freeze surface, closing the gap both design docs converged on independently
(this document's §13 ASK 4 / engine_m4.md §11.2: `rx_matchfn`'s `caps` is an
INPUT and its return is a length only, so a caller who knows the start
position and wants group offsets — D41.4's "tokenizer class of caller" — has
no entry to call). Exact signature left to the amendment round; this is that
signature.

**PROPOSED-here (§12.9):**

```c
ptrdiff_t <prefix>_match_caps(const rx_ctx *ctx, ptrdiff_t (*caps_out)[2]);
/* Anchored at ctx->pos (no search loop, unlike <prefix>_search).
 * Returns matched length >= 0 (the same value <prefix>_match(ctx) would
 * return for this ctx) or -1 on failure.
 *
 * On success: caps_out[0..RX_NCAPS-1] are ALL written (C6, same
 * copy-on-success discipline as <prefix>_search, engine_m4.md §3.4);
 * caps_out[0] is the whole match, [ctx->pos, ctx->pos + length).
 * On failure: caps_out is untouched.
 *
 * Self-contained per F2: ctx->ncap/ctx->caps are read as ordinary
 * rx_ctx INPUT (a top-level call passes ncap=0, caps=NULL, same as
 * <prefix>_match) and are NOT this entry's own output channel — that is
 * what caps_out is for. rx_ctx.caps stays frozen as an input (D38/F3,
 * engine §11.2); this entry does not reinterpret it. Caller-owned,
 * RX_NCAPS entries, allocation-free (C7). A thin wrapper over the same
 * internal rx_match_impl(ctx, w) that engine_m4.md §4.4's three layers
 * build for <prefix>_match and <prefix>_search. */
```

**Which entries deliver captures.** `<prefix>_search` and
`<prefix>_match_caps` do; `<prefix>_match` structurally cannot — its
`caps` is an input, its return is a length only, and there is no output
channel for its own captures anywhere in `rx_matchfn`'s signature (engine
§11.2). A capture-consuming caller who does not want the search loop uses
`<prefix>_match_caps`; one who does not know the start position uses
`<prefix>_search`; one who wants neither offsets nor a loop uses
`<prefix>_match`.

**Rationale.** `const rx_ctx *ctx` as the first parameter — rather than the
scalar `(subject, len, pos)` triple `<prefix>_search` takes — keeps
`<prefix>_match_caps` sharing its FIRST parameter's exact type with
`<prefix>_match`: a caller that already built a `ctx` (to call `_match`, or
because it sits inside composed matching) reuses it verbatim to also get
captures, with no repackaging. It is also the thinnest wrapper structurally:
`rx_match_impl` already takes `(const rx_ctx *, rx_work *)` (engine §4.4),
so `<prefix>_match_caps` is `rx_match_impl(ctx, &w)` plus one
copy-on-success loop into `caps_out` — no local `rx_ctx` needs constructing
first, unlike a scalar signature would require. The separate `caps_out`
parameter (rather than writing through `ctx->caps`) has direct precedent:
`rx_renderfn` (subst Q13) is already `ctx` plus a separate output
parameter, for the same underlying reason — `rx_ctx.caps` is frozen as an
INPUT (D38/F3), so an entry that DELIVERS captures needs a channel `rx_ctx`
does not provide, exactly as the renderer needed one for its rendered
bytes.

**Rejected alternative:** the scalar signature, `(subject, len, pos,
ptrdiff_t caps_out[RX_NCAPS][2])`, mirroring `<prefix>_search`'s own
parameter style instead of `<prefix>_match`'s. Rejected because it buys
nothing a `ctx`-based signature doesn't already have — a caller with only
scalars builds a one-line compound literal exactly once, while a caller
that already holds a `ctx` (the composition-adjacent case this entry
primarily exists for, per D41.4) is forced to re-unpack it into scalars for
no benefit — and it would group `<prefix>_match_caps` with
`<prefix>_search` (the LOOPING entry) in a reader's mental model rather
than with `<prefix>_match` (the ANCHORED entry it is actually a
capture-delivering sibling of), the wrong grouping for §7's table.

---

## 4. `rx_ctx` layout and the `rx_callout_ref` binding unit

**RULED (D38):** the field set below, confirmed with `void *user` added via
the binding-unit struct rather than a bare extra field.

```c
typedef struct rx_ctx {
    const unsigned char *subject;   /* whole subject, not a slice */
    size_t                len;      /* subject length */
    size_t                pos;      /* where to match, anchored */
    size_t                ncap;     /* capture slots known so far (watermark
                                        mid-match; ngroups+1 on completion) */
    const ptrdiff_t     (*caps)[2]; /* [start,end); {-1,-1} = unset */
    void                 *user;     /* per-binding user data, RULED (D38) */
} rx_ctx;

typedef struct rx_callout_ref {
    rx_matchfn *fn;
    void       *user;
} rx_callout_ref;

extern const rx_callout_ref rx_callout_<name>;   /* one per callout binding */
```

- **RULED (D42.5, 2026-08-14) — `rx_ctx.caps` LIFETIME, joining the F-list.**
  The `caps` pointer handed to a callout is valid for the DURATION OF THE
  CALL ONLY. The engine rewrites the same storage afterwards (trail-based
  undo, §2.4 of engine_m4.md — the slots a callout reads are not a private
  copy). A callout that retains the pointer past its own call and reads it
  later is the EMBEDDER'S BUG, not a pcrec contract violation; nothing in
  the generated code detects or guards against it. This line did not exist
  in F1–F8 (engine_m4.md §12 ASK-3 raised the gap) and is now part of the
  frozen contract alongside them.
- **`const unsigned char *subject`**, not `const char *`: char signedness is
  implementation-defined, and the emitter already indexes 256-entry class
  tables with subject bytes (`rx_ftr[st * 5 + rx_fcls[s[pos++]]]`) — a signed
  `char` makes that a negative index on any byte >= `0x80`. `PCREC_ENC_ASCII`
  is documented "byte semantics, 8-bit clean," so such bytes are ordinary
  subjects, not an edge case. RULED as subst note Q14 / design_callout_abi.md
  §1's already-applied form.
- **The BINDING UNIT is the struct, not the bare function pointer.** The
  engine reads `ref->user` into `ctx->user`, then calls `ref->fn(ctx)`. State
  is per-binding; per-thread state is the callout's own `_Thread_local`
  business (an `&tls_var` static initializer does not compile, so this cannot
  be routed through `user` at binding time).
  **Rejected**: a single process-global `user` (defeats per-binding state);
  a per-call `user` parameter threaded through `rx_matchfn` itself
  (Frank: "ouch" — changes the signature for every caller to serve a
  minority need).

  **Re-examined 2026-08-14 (Frank's question, post-D38; asked, not
  directed — ruling unchanged):** would `(*fn)(const rx_ctx *, void
  *data)` be better, keeping `user` out of `rx_ctx` so the struct stays
  pure match state? Answer recorded so the panel need not re-derive it:
  `rx_ctx` is a TRANSIENT, PER-CALL view whose instance the engine owns —
  `pos` and the `ncap` watermark are already written between callout
  sites, so `user` adds one store to a struct that is engine-local and
  mutated per site regardless, and the callee's `const` view means no
  aliasing is observable. The two-arg form's separation is conceptual
  only, while its cost is concrete: composition requires the match-here
  entry to share the type, so every non-callout embedder would carry a
  `NULL` second argument (the same signature tax D38's rejection
  recorded), and the Q13 renderer signature would grow to four
  parameters. `rx_ctx` purity is also not durable either way — the v2
  declared-capture-export path is already a DD-3 struct revision. Frank
  confirmed KEEP same day, adding that pre-v1 he is unconcerned with
  backwards compatibility — so struct-stability arguments carry no
  weight against this choice today.
- **Composition is a one-line const wrap**: `const rx_callout_ref
  rx_callout_x = { inner_match_here, NULL };` — because the two struct
  shapes are identical, a compiled matcher links directly as a callout with
  no adapter.
- **F3, stated as a freeze property**: `rx_ctx.caps`'s representation *IS*
  the match API's capture-offset contract — the same `ptrdiff_t[2]` pairs as
  §1's `<prefix>_span` and §2's caps array. One representation, not a
  conversion, anywhere a capture offset crosses an API boundary in the
  generated contract.
- **Captures are OPAQUE across the composition boundary in v1**: a callout
  sees the outer captures-so-far; a composed matcher's own inner captures are
  invisible to the outer pattern (F5). The v2 path — declared-in-syntax
  export, `(?Cc<n>"fn")` direction, a non-const ctx + capacity field — is
  RECORDED, not scheduled; it is a DD-3 struct revision when it comes.

---

## 5. The exported group index (F8, D39 + addendum)

**RULED (D39 + addendum):** every generated pattern exports a static const
name→number index, born WITH a `ref` column at this freeze (not added later
as a second break):

```c
typedef struct {
    const char *name;
    int         number;
    const char *ref;     /* NULL/empty for the primary's own groups;
                             carries the labeled insertion path once
                             V-E's rx references exist */
} <prefix>_group_entry;

extern const <prefix>_group_entry <prefix>_groups[];
#define <PREFIX>_NGROUPS <count>
```

(**PROPOSED-here**, §12.3: the struct/array/count symbol names above —
D39 fixes the FIELD set `{name, number, ref}` and its properties, not the
C identifier spelling. Following §1's `RX_NCAPS`-style convention for the
count keeps the naming scheme uniform across every new symbol this freeze
introduces; see §7's table.)

- **Sorted, bsearch-able, `.rodata` only, zero runtime cost** — a static
  table, not a runtime structure.
- **Does NOT travel in `rx_ctx` or any callback parameter**: it is a
  link-time constant per pattern (queried by symbol, not passed at a call
  site), unlike everything else in §2 and §4.
- **`ref` is NULL/empty for the primary pattern's own groups today** — V-E's
  labeled-reference numbering (a path like `"c:a"` for nested insertions) is
  the only future consumer of a non-empty `ref`; nothing produces one yet.
  This is why F8's index is "born with the ref column" rather than needing a
  second break when V-E lands: V-E extends DATA, not ABI.
- **Second customer**: `V-A`'s `pcre2_substring_number_from_name`.
- **PROPOSED-here (§12.4), what the index CONTAINS today**: the array is
  indexed over NAMED groups only — an entry with no name has nothing to
  `bsearch` by, so unnamed capturing groups do not appear. Module
  `named-groups` does not exist yet (subst C10's measured gate:
  `pcrec --count-groups '(?<g>a)(b)'` currently fails with "requires module
  'named-groups'"), so **every pattern's index has count 0 until that module
  lands** — the export mechanism (the array + count symbols) is present
  unconditionally per F8; its CONTENT is trivially empty pre-`named-groups`.
  This is a narrower reading of the plan row's "(empty-ref) group index
  retrofitted onto the EXISTING DFA matchers" than "ref column empty, but
  entries already exist for something" — flagged for the panel because it is
  new synthesis, not literally in D39.

---

## 6. `pcrec_error` gains the which-input tag (subst Q8)

**RULED (D38, subst note §9 Q8):** *"`pcrec_error` gains a WHICH-INPUT
tag (an enum: pattern vs. template) beside `pos`; a `lib/pcrec.h` change to
land at the M4 freeze."*

Today (`lib/pcrec.h:34-37`):

```c
typedef struct {
    char   msg[256];
    size_t pos;
} pcrec_error;
```

**PROPOSED-here (§12.5)**, since the ruling fixes the requirement (an enum
beside `pos`) but not field/type names:

```c
typedef enum {
    PCREC_ERR_INPUT_PATTERN  = 0,
    PCREC_ERR_INPUT_TEMPLATE = 1
} pcrec_err_input;

typedef struct {
    char            msg[256];
    size_t          pos;
    pcrec_err_input input;   /* which input string `pos` indexes into */
} pcrec_error;
```

This belongs to §0's namespace 2 (`pcrec`'s own fixed API surface), so the
enum constants are `PCREC_*` per §8's naming scheme — a case where the two
freeze obligations reinforce each other. `pcrec_compile()` always sets
`input = PCREC_ERR_INPUT_PATTERN` (the only input it has today); the
substitution-compiler entry point (`[M4-SUBST]`, not yet built) is the first
producer of `PCREC_ERR_INPUT_TEMPLATE`.

**RULED (D42.4, 2026-08-14) — spelling ACCEPTED, with a compat obligation
recorded.** `pcrec_err_input` / `input` / `PCREC_ERR_INPUT_PATTERN` /
`PCREC_ERR_INPUT_TEMPLATE` are accepted exactly as proposed above — no
rename. Recorded alongside: the PCRE2-compat surface (V-A direction, D38's
addenda) will ALSO alias these names PCRE2-style with approximately the
same error meaning ("samish" — D26's tiering governs: the MEANING matches,
the WORDING need not). This lands now (nothing native ever uses a PCRE2_
spelling, unchanged) or at V-A's own design time, whichever comes first;
it is not owed by [M4.4].

---

## 7. Entry-point naming (OS-0) for every new symbol

[OS-0] (`docs/dev/plan.md`) is the named-entry-point convention: per-prefix
symbols, resolved once at generation time, so a statically-known caller pays
no runtime dispatch. This freeze introduces symbols in BOTH of §0's
namespaces; the table separates them because they follow different rules.

| symbol | namespace | scoped by `--prefix`? | status |
|---|---|---|---|
| `<prefix>_search` | 1 (per-artifact) | yes | unchanged name, changed signature (§1); negative space RULED (D42.3, §1) |
| `<prefix>_span` | 1 | yes | unchanged name, changed representation (§1) |
| the match-here entry | 1 | yes — `<prefix>_match`, RULED (D41.2, §12.6's proposal confirmed) | new; see §3 |
| `<prefix>_match_caps` | 1 | yes | new (D41.4); PROPOSED-here (§3.1, §12.9) |
| `<PREFIX>_NCAPS`, `<PREFIX>_UNSET` | 1 | yes (uppercased) | already spelled this way in the subst note's example; `RX_NCAPS`'s artifact-property rule RULED (D42.2, §2.1) |
| `<prefix>_group_entry`, `<prefix>_groups[]`, `<PREFIX>_NGROUPS` | 1 | yes | RULED (D41.3): mechanism ships at [M4.4], NAMED-groups-only content, count 0 until module `named-groups` lands (§5, §12.3) |
| `rx_ctx`, `rx_matchfn`, `rx_callout_ref` | **neither — fixed literal** | **no, RULED (D41.1, confirming §12.7)** | as spelled throughout `design_callout_abi.md` |
| `rx_callout_<name>` | fixed literal `rx_callout_` prefix + the callout's own name | no | RULED (D38) shape |
| `pcrec_err_input`, `PCREC_ERR_INPUT_*` | 2 (library-fixed) | no | RULED (D42.4): spelling accepted; V-A compat alias obligation recorded (§6) |

**PROPOSED-here (§12.6), the match-here entry's name.** Neither ruling picks
a literal spelling. Following the SAME collision-avoidance reasoning that
gives `<prefix>_search` its prefix (two generated files linked into one
program must not collide), the match-here entry should be `<prefix>_match` —
prefixed like every other per-pattern entry point, distinct from the ABI
TYPES below it, which must NOT be prefixed for a different reason.

**PROPOSED-here (§12.7), and flagged as a genuine ASK (§13):**
`design_callout_abi.md` spells `rx_ctx`/`rx_matchfn`/`rx_callout_ref`
literally as `rx_` throughout, never `<prefix>_ctx`. This document reads that
as INTENTIONAL rather than a stand-in for the default prefix, because the
ABI's entire point is composability: "a compiled matcher links directly as a
callout... link-level regex composition with no adapter" only works if EVERY
generated matcher, regardless of its own `--prefix`, shares one `rx_matchfn`
type and one `rx_ctx` layout. Prefixing these per-pattern would break exactly
the property F1–F6 exist to provide — a pattern compiled with `--prefix foo`
could not bind as a callout for one compiled with the default `rx` prefix
without a cast through incompatible types.

This is safe under C's per-translation-unit typedef scoping: `typedef struct
rx_ctx {...} rx_ctx;` appearing identically in two separately-compiled `.c`
files produces no link-time symbol and no ODR-style conflict — each TU's
typedef is local to it, and as long as the FROZEN shape (§4) never diverges
between them, the types remain structurally and nominally compatible
wherever they are used together (e.g. a callout `extern` declared in a
different TU). This document is not aware of this reasoning being written
down anywhere in the ruled material; §13 asks Frank to confirm it explicitly,
since it is the one naming choice that is load-bearing for the entire ABI's
central selling point (R-a's "align... so you could use the regex parse
function as a callout") rather than a cosmetic pick.

---

## 8. The PCREC_* native constants surface

**RULED (D38 addenda):** *"the layering question closes immediately —
`PCRE2_*` IS FOR COMPATIBILITY, full stop. The native surface is uniformly
`PCREC_*` for every flag... One canonical namespace (PCREC_*), one compat
aliasing surface (PCRE2_*, the V-A direction); no flag is ever native under
the PCRE2_ prefix."* Restated in `docs/pcre2_options.md`'s "Naming scheme
(D38 addenda)" section.

This governs §0's namespace 2 only (pcrec's own library-level API surface —
`PCREC_ENC_ASCII` today; future flag constants as PC-5 rows land; the new
`pcrec_err_input` enum, §6). **It does NOT touch namespace 1** — `RX_NCAPS`,
`<prefix>_match`, etc. are per-artifact emitted symbols scoped by the CALLER's
chosen prefix, not by this scheme.

**What the freeze fixes today**: the SCHEME, not any concrete flag. Per
`docs/pcre2_options.md`: "nothing below emits either name yet — this note
applies only once a row's own work actually lands." No PC-5 row lands as part
of [M4.1]/[M4.4]; this section exists so that when one does (independently),
its constant is `PCREC_*`-native by construction rather than by a
case-by-case re-litigation.

**Manager-confirmed today (2026-08-14) — what this ruling governs, stated so
a panel critic does not have to re-derive it.** Frank asked whether
`--no-captures`/`-i` map to `PCREC_*` options under the hood; the answer is
recorded here rather than left to be rediscovered:

- **The native option SURFACE is the `pcrec_options` STRUCT**
  (`lib/pcrec.h`), not a bitmask — named fields (`prefix`, `encoding`,
  `caseless`, `emit_main`, `header_name` today). M4-era additions land the
  same way: the captures default's `--no-captures` becomes a field
  (`int captures;` direction, or equivalent), not a `PCREC_*` bit.
- **CLI flags are a thin veneer over the struct**: `-i` sets
  `opt.caseless = 1`; `--no-captures` (once M4.5 lands) sets its field the
  same way. No CLI flag is itself a `PCREC_*` constant.
- **§8's `PCREC_*` ruling names the ENUM-VALUED constants** — `PCREC_ENC_ASCII`
  today (the value a struct field like `encoding` HOLDS), and any future
  flag-shaped constant of the same kind — not the struct's field names and
  not the CLI flags that set them.
- **V-A's compat layer is where bits reappear**: it translates PCRE2
  bitmask spellings (`PCRE2_CASELESS`, etc.) onto the native struct's
  fields AT THE BOUNDARY. Bits at the compat boundary, fields natively —
  the same "PCRE2_* compat, PCREC_* native" split §8 states for constants
  applies to the OPTION-SETTING mechanism too, one level up.
- **No bitmask surface is being added natively.** If that changes, it is a
  Frank ruling recorded here or in `docs/dev/decisions.md`, not a drift a
  later reader should infer from an implementation detail.

---

## 9. Callout-pattern entry points thread nothing extra

Stated as its own freeze property because it is easy to assume otherwise: a
callout binding's `user` data lives ENTIRELY in the `rx_callout_ref` the
binding declares (§4) — no additional parameter, no additional field, no
per-call argument. The engine's obligation at a callout call site is exactly:
copy `ref->user` into `ctx->user`, then call `ref->fn(ctx)`. Nothing about
*which* callout is firing, or what pattern position it fires at, is visible
to `rx_matchfn`'s signature — that information lives in which `extern` was
bound at that call site, a compile-time fact, not a run-time one. This is
D36's static-extern primitive, restated at the ABI's final signature: zero
cost when a callout is absent, and no `rx_matchfn` implementation can be
written that requires knowing it is being called AS a callout versus being
called as a top-level entry (F2's self-containedness).

---

## 10. Deliberately open — not blocking the freeze

These stay open by explicit ruling or by the two carrying docs' own
framing. The freeze proceeds without them.

- **Callout binding syntax spelling** (design_callout_abi.md §6 Q5, R-d):
  near-PCRE2 `(?C...)` family favored, nothing chosen. Any spelling that
  reinterprets a currently-valid pattern must be module-gated (the collision
  rule holds regardless of which spelling is picked).
- **Embedded-code restrictions** (§6 Q6): distant future, unscheduled, no
  syntax proposed beyond Frank's `\{ strlen($1) == 5 }` sketch.
- **The group-vs-non-group callout form** (R-c: "two forms or a switch"):
  spelling deliberately unproposed.
- **V-E-time items** (D39 addendum, "still open"): the reference-path
  spelling (order/separator of `"c:a"`), whether an insertion's label is
  mandatory or optional-with-default for single insertions, and lookup-key
  semantics (name-alone when unambiguous vs. `ref+name`).
- **The captures-opaque v1 / declared-in-syntax v2 path**
  (design_callout_abi.md F5, §6 Q4): recorded, not scheduled; a DD-3 struct
  revision when it lands.
- **The native-abort reservation** (F2, F4): `< -1` is reserved and trapped,
  but no return value is assigned a meaning yet. Revisit if a real customer
  for native abort appears (D38's own revisit-when).
- **`\G`/global-mode shared state** (subst §6.2), **`^`-under-global-iteration**
  and **newline-convention interaction with global substitution** (DD-11) —
  cited by the subst note, not this document's business.

---

## 11. What [M4.4] must do mechanically

Translating §1–§9 into an implementation checklist, so the freeze is
executable rather than merely descriptive:

1. **Break `<prefix>_span`** (§1): `emit_span_typedef` in `src/gen/emit_dfa.c`
   emits the `ptrdiff_t[2]` form instead of the `size_t start,end` struct;
   every `%s_span *m` declaration/definition site updates in the same commit;
   `lib/pcrec.h`'s doc comment updates; `tests/harness/driver.c` and any
   `_span`-pattern grep in `tests/codegen/` update in the same commit — one
   announced break, not a staged migration.
2. **Emit `rx_ctx`, `rx_matchfn`, `rx_callout_ref`** (§4, §7) as file-scope
   types, once per file — the same "ONCE PER FILE, shared by every engine in
   it" shape `emit_span_typedef` already uses, since these three types are
   fixed (not `<prefix>`-scoped, §12.7) and would collide if emitted more
   than once identically (harmlessly, but redundantly) or divergently
   (a build error, same class as today's duplicate-`rx_span` hazard).
3. **Emit the match-here entry unconditionally** (§3) — `<prefix>_match`,
   `rx_matchfn`-typed, accepting `ncap=0, caps=NULL` — retrofitted onto the
   EXISTING DFA matchers (per [M4.4]'s own plan-row text), alongside
   `<prefix>_search`, not replacing it. No trap-check call sites are needed
   yet (§3's scope note — no callers of `rx_matchfn` exist before callouts or
   V-E composition land).
4. **Emit F8's group index unconditionally, empty today** (§5): the
   `<prefix>_group_entry` array, `<prefix>_groups[]`, `<PREFIX>_NGROUPS`
   symbols land with count 0 for every pattern (module `named-groups`
   doesn't exist), `ref` column present but never populated (V-E doesn't
   exist). The MECHANISM is what this freeze requires landed now; the
   CONTENT arrives with those later modules.
5. **Change `lib/pcrec.h`**: add `pcrec_err_input` and the `input` field to
   `pcrec_error` (§6); `pcrec_compile()`'s error path sets
   `PCREC_ERR_INPUT_PATTERN` always (it has no other input yet).
6. **Coverage conservation** per the STD1 re-baseline shape (`docs/dev/plan.md`
   / `docs/testing.md`): every corpus/harness site that reads `.start`/`.end`
   field names or assumes `size_t` capture offsets is inventoried and updated
   in the SAME commit as item 1, not discovered by a later test failure —
   this is the "suite populations conserved and accounted" clause in
   [M4.4]'s own plan row.
7. **Nothing above requires the VM.** All of it targets the existing DFA
   emitter; M4.5 (VM emitter core) is where `caps` actually gets populated
   for capture-bearing patterns. **RESOLVED by D42.2 / engine §5.7 (was
   this document's own §13 ASK 4 / §12.8):** a DFA-compiled pattern —
   capture-bearing or not — emits
   `RX_NCAPS 1` at [M4.4] time, full stop; there is no interim `caps[1..]`
   population to define because the artifact never promises those slots.
   `RX_NCAPS > 1 ⇒ VM` is the structural check [M4.4] adds.
8. **Emit `<prefix>_match_caps`** (§3.1, D41.4): the anchored
   capture-delivering sibling of `<prefix>_match`, thin-wrapped over the
   same `rx_match_impl`. Lands whenever `<prefix>_match` does for a given
   engine — at [M4.4] it exists but is only ever called on a `RX_NCAPS 1`
   artifact (so `caps_out[0]` is the only slot ever written); it becomes
   useful for capture-bearing patterns once [M4.5]'s VM lands.
9. **`<prefix>_search`'s negative-return space** (D42.3, §1): reserve and
   name `RX_ERR_STEPS`/`RX_ERR_FRAMES` in the emitted header at [M4.4],
   even though no engine produces either value until [M4.6] wires the
   budget/frame counters — the space must be reserved before any counter
   exists, not after, so a caller's `switch` written against [M4.4]'s
   output does not need revisiting later.

---

## 12. Everything this document introduces beyond the rulings (for the manager / M4.3 panel)

Collected from the PROPOSED-here marks above, in one place per the brief's
house-style requirement. Items 3–8 were RULED by D41/D42 in the amendment
round (still listed — they are what the panel should check the ruling was
APPLIED to, not just that it exists); items 1, 2, and the new item 9 remain
open PROPOSED-here synthesis for the panel to attack:

1. **§1**: the concrete post-break spelling of `<prefix>_span` —
   `typedef ptrdiff_t <prefix>_span[2];`, keeping the existing name and
   `<prefix>_search` signature shape, changing only element type and
   struct-vs-array representation. **Still open** — no ruling picked this
   concrete spelling.
2. **§3**: the scope note that F2's `__builtin_trap()` call-site enforcement
   has no call sites to attach to yet at [M4.4] time (no callout/composition
   code exists), so [M4.4] emits the entry but not the trap-guarded call.
   **Still open.**
3. **§5**: the group-index C identifier spellings (`<prefix>_group_entry`,
   `<prefix>_groups[]`, `<PREFIX>_NGROUPS`) and the claim that the index's
   CONTENT (not just its `ref` column) is empty (count 0) until module
   `named-groups` lands. **RULED (D41.3).**
4. **§5** (same item, restated): that unnamed capturing groups never appear
   in the index at all (only named groups get an entry), since an entry
   needs a name to be a lookup key. **RULED (D41.3), same ruling as item 3.**
5. **§6**: the concrete `pcrec_err_input` enum and field spelling for the
   which-input tag. **RULED (D42.4)**, plus the V-A compat-alias obligation
   recorded alongside it.
6. **§7**: that the match-here entry is `<prefix>_match` (prefix-scoped),
   by analogy with `<prefix>_search`'s existing collision-avoidance role.
   **RULED (D41.2).**
7. **§7 / §12.7 together**: the claim that `rx_ctx`/`rx_matchfn`/
   `rx_callout_ref` are DELIBERATELY fixed literal names, not scoped by
   `--prefix`, because per-pattern scoping would defeat the ABI's
   composability goal — and the C-typedef-scoping argument for why that is
   safe across separately-compiled generated files. This was the single
   highest-leverage PROPOSED-here item in this document. **RULED (D41.1)** —
   confirmed exactly as proposed, including the C-typedef-scoping safety
   argument (D41.1's own text cites "safe under C's per-TU typedef
   scoping").
8. **§11 item 7**: the open question of what a group-bearing, non-backref
   DFA-compiled pattern's `caps[1..]` should read via the retrofitted
   match-here entry before the VM/engine-selection exists. **RULED
   (D42.2, confirming engine §5.7's answer, ASK-12):** the question
   dissolves — a DFA-compiled artifact never promises `caps[1..]` at all
   (`RX_NCAPS 1` always); see §2.1 and §11 item 7's revision.
9. **§3.1** (new this round): the concrete `<prefix>_match_caps` signature
   — `ptrdiff_t <prefix>_match_caps(const rx_ctx *ctx, ptrdiff_t
   (*caps_out)[2])`, `ctx` for the anchor position (matching
   `<prefix>_match`'s first parameter, not `<prefix>_search`'s scalar
   triple) plus a separate output array (matching the renderer's `rx_ctx` +
   output-parameter shape, subst Q13), rejecting a scalar-triple
   alternative. D41.4 ruled that this entry EXISTS; this signature is
   PROPOSED-here, for [M4.3] to review.

---

## 13. ASKs for the manager / Frank

1. **RULED (D41.1, 2026-08-14):** FIXED literal names, confirming §12.7's
   reading — `rx_ctx`, `rx_matchfn`, `rx_callout_ref` are shared by every
   generated matcher regardless of `--prefix`. Composability is the point;
   safe under C's per-TU typedef scoping.
2. **RULED (D41.2, 2026-08-14):** `<prefix>_match`, as proposed (§12.6).
3. **RULED (D41.3, 2026-08-14):** NAMED-groups-only, as recommended —
   count 0 until module `named-groups` lands; unnamed groups are reachable
   by number via `caps[]`. The mechanism ships at [M4.4] regardless.
4. **ANSWERED by engine_m4.md §5.7 (2026-08-14), with a sharpening this
   document must absorb in the amendment round:** the match-here entry has
   NO `caps` output for ANY engine (`rx_ctx.caps` is an input; the return
   is a length — engine doc §11.2), so the question binds the
   capture-DELIVERING entries instead. The answer: the capture-slot count
   is a property of the ARTIFACT — a DFA-compiled artifact emits
   `RX_NCAPS 1`, C6 never bends, and `RX_NCAPS > 1` implies the VM (one
   structural check, live from [M4.4]). Candidate (a) is rejected there
   (permanently ambiguous `RX_UNSET`; silent empty renders under D38's
   subst-Q3). Frank's confirmation of the §5.7 rule rides engine ASK-12,
   still pending. **RULED alongside it (D41.4): an anchored
   capture-delivering entry (`<prefix>_match_caps` direction) JOINS the
   freeze surface** — exact signature proposed by the amendment round,
   reviewed at M4.3. **ASK-12 itself now RULED (D42.2, 2026-08-14):** the
   §5.7 rule is CONFIRMED as stated — folded into §2.1 and §11 item 7 in
   this amendment round. The `<prefix>_match_caps` signature it names is
   §3.1.
5. **§6**: is `pcrec_err_input` / `PCREC_ERR_INPUT_PATTERN` /
   `PCREC_ERR_INPUT_TEMPLATE` an acceptable spelling, or does Frank want a
   different field name than `input` (e.g. `which`, `source`)? **RULED
   (D42.4, 2026-08-14):** accepted as proposed, `input` unchanged, plus the
   V-A compat-alias obligation — see §6.

No genuine contradiction between D38 and D39 was found — every tension
encountered (ncap-as-watermark vs. C6's no-watermark rule, §2.1; the group
index's "(empty-ref)" phrasing vs. this document's stronger "(empty,
period)" reading, §5) resolved on inspection rather than blocking. The five
items above are gaps the rulings left unfilled, not disagreements between them.

---

## 14. AMENDMENTS APPLIED (D41/D42, 2026-08-14)

The amendment round owed after D41 and engine_m4.md's merge is DISCHARGED —
every item below is integrated in place (not merely annotated) at the
section cited; this list is now the record of what changed, not a
checklist of what remains.

1. **`<prefix>_match_caps`** (D41.4): exact signature proposed and
   integrated at §3.1, with a naming-table row at §7, an [M4.4] emission
   item at §11.8, and its rationale/rejected-alternative recorded there and
   at §12.9. Anchored at `ctx->pos`, fills a caller-provided `caps_out`
   array, returns length or −1; a thin wrapper over the same internal
   `rx_match_impl` as `<prefix>_match` and `<prefix>_search` (engine doc
   §4.4's layering).
2. **Search-entry negative returns** (engine doc §4.4/§4.5 handback):
   integrated at §1 (RULED D42.3) and §11.9 — `<prefix>_search` reserves
   negative returns for engine-give-up, naming `RX_ERR_STEPS` and
   `RX_ERR_FRAMES`; today's `1`/`0` contract keeps its meanings unchanged.
3. **§13.4's sharpening absorbed**: §3.1 states which entries deliver
   captures (`<prefix>_search`, `<prefix>_match_caps`) and that
   `<prefix>_match` structurally cannot; engine §5.7's
   `RX_NCAPS`-is-an-artifact-property rule is folded into §2.1 (RULED
   D42.2, confirming ASK-12) and §11 item 7 is rewritten to match rather
   than to flag an open question.
4. **`rx_ctx.caps` lifetime line** — RULED (D42.5): integrated into §4
   ("valid for the duration of the call; the engine rewrites the storage
   afterwards; retaining the pointer is the embedder's bug"), with a
   forward reference from §2.1 where the mid-match watermark is discussed.
5. **`pcrec_err_input` compat note** — RULED (D42.4): integrated into §6
   and the §7 table row — spelling accepted as originally proposed; the
   V-A compat surface will also alias these names PCRE2-style with
   approximately the same error meaning (D26 tiering governs the wording).
6. **Captures-default consequence** — RULED (D42.1): integrated into §2.1
   — captures ON by default post-[M4.5] (`--no-captures` recovers today's
   artifact); `RX_NCAPS` reflects the ARTIFACT per the confirmed engine
   §5.7 rule (D42.2); the search entry's negative space carries
   `RX_ERR_STEPS`/`RX_ERR_FRAMES` per D42.3/§1.

**What did NOT resist integration.** No conflict was found between any
D41/D42 ruling and the existing text of this document — every ruling
either confirmed a PROPOSED-here item verbatim (D41.1/D41.2/D41.3/D42.4)
or filled a gap this document had already flagged as an ASK (D41.4/D42.2's
answer to ASK 4; D42.5 to §12 ASK-3's engine-side twin; D42.3 to the
search-entry gap engine §4.4 raised). The one place worth flagging for the
panel as a JUDGMENT CALL rather than a mechanical fold: `§3.1`'s
`<prefix>_match_caps` signature took `const rx_ctx *ctx` plus a separate
output array over a scalar `(subject, len, pos)` triple — D41.4 ruled the
entry must exist and be reviewed at [M4.3], not which shape it takes, so
this is new PROPOSED-here synthesis for the panel to attack, not a ruled
fact. §12 collects it alongside the two items (1, 2) still open from the
prior round.
