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
  contradiction over one field.
- **Caller-owned, fixed-size, compile-time-sized** (C7): a caller declares
  `ptrdiff_t caps[RX_NCAPS][2];` on the stack; nothing in the generated
  contract allocates.

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

---

## 7. Entry-point naming (OS-0) for every new symbol

[OS-0] (`docs/dev/plan.md`) is the named-entry-point convention: per-prefix
symbols, resolved once at generation time, so a statically-known caller pays
no runtime dispatch. This freeze introduces symbols in BOTH of §0's
namespaces; the table separates them because they follow different rules.

| symbol | namespace | scoped by `--prefix`? | status |
|---|---|---|---|
| `<prefix>_search` | 1 (per-artifact) | yes | unchanged name, changed signature (§1) |
| `<prefix>_span` | 1 | yes | unchanged name, changed representation (§1) |
| the match-here entry | 1 | **PROPOSED-here (§12.6): yes — `<prefix>_match`** | new; see below |
| `<PREFIX>_NCAPS`, `<PREFIX>_UNSET` | 1 | yes (uppercased) | already spelled this way in the subst note's example |
| `<prefix>_group_entry`, `<prefix>_groups[]`, `<PREFIX>_NGROUPS` | 1 | yes | PROPOSED-here (§5, §12.3) |
| `rx_ctx`, `rx_matchfn`, `rx_callout_ref` | **neither — fixed literal** | **no (open question, §12.7)** | as spelled throughout `design_callout_abi.md` |
| `rx_callout_<name>` | fixed literal `rx_callout_` prefix + the callout's own name | no | RULED (D38) shape |
| `pcrec_err_input`, `PCREC_ERR_INPUT_*` | 2 (library-fixed) | no | PROPOSED-here (§6) |

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
   for capture-bearing patterns. **PROPOSED-here (§12.8), flagged as an ASK
   (§13):** what does a DFA-compiled pattern that HAS capturing groups (no
   backreferences, so not yet forced to the VM by SR-8) report through
   `caps[1..ngroups]` via the retrofitted match-here entry, given the DFA
   engine has never tracked per-group offsets (only the whole-match span)?
   Neither D38 nor D39 nor [M4.4]'s plan-row text says. This document does
   not resolve it — per-pattern engine selection is M4.2/M4.6 territory —
   but flags it because [M4.4] will hit the question mechanically the moment
   it retrofits F1/F8 onto a DFA matcher for a pattern with groups.

---

## 12. Everything this document introduces beyond the rulings (for the manager / M4.3 panel)

Collected from the PROPOSED-here marks above, in one place per the brief's
house-style requirement:

1. **§1**: the concrete post-break spelling of `<prefix>_span` —
   `typedef ptrdiff_t <prefix>_span[2];`, keeping the existing name and
   `<prefix>_search` signature shape, changing only element type and
   struct-vs-array representation.
2. **§3**: the scope note that F2's `__builtin_trap()` call-site enforcement
   has no call sites to attach to yet at [M4.4] time (no callout/composition
   code exists), so [M4.4] emits the entry but not the trap-guarded call.
3. **§5**: the group-index C identifier spellings (`<prefix>_group_entry`,
   `<prefix>_groups[]`, `<PREFIX>_NGROUPS`) and the claim that the index's
   CONTENT (not just its `ref` column) is empty (count 0) until module
   `named-groups` lands.
4. **§5** (same item, restated): that unnamed capturing groups never appear
   in the index at all (only named groups get an entry), since an entry
   needs a name to be a lookup key.
5. **§6**: the concrete `pcrec_err_input` enum and field spelling for the
   which-input tag.
6. **§7**: that the match-here entry is `<prefix>_match` (prefix-scoped),
   by analogy with `<prefix>_search`'s existing collision-avoidance role.
7. **§7 / §12.7 together**: the claim that `rx_ctx`/`rx_matchfn`/
   `rx_callout_ref` are DELIBERATELY fixed literal names, not scoped by
   `--prefix`, because per-pattern scoping would defeat the ABI's
   composability goal — and the C-typedef-scoping argument for why that is
   safe across separately-compiled generated files. This is the single
   highest-leverage PROPOSED-here item in this document: if wrong, it
   changes every code sample in `design_callout_abi.md` and this document
   both.
8. **§11 item 7**: the open question of what a group-bearing, non-backref
   DFA-compiled pattern's `caps[1..]` should read via the retrofitted
   match-here entry before the VM/engine-selection exists — recorded as a
   question for [M4.4]/[M4.2], not answered here.

---

## 13. ASKs for the manager / Frank

1. **Confirm or correct §12.7**: should `rx_ctx`, `rx_matchfn`,
   `rx_callout_ref` be literal, fixed names shared by every generated matcher
   regardless of its own `--prefix` (this document's reading of
   `design_callout_abi.md`'s consistent literal spelling), or should they be
   `<prefix>_ctx`-scoped like `<prefix>_search`? The composability property
   (R-a, F5/F6) only holds under the first reading; the source docs never
   state which was intended.
2. **Confirm §12.6**: is `<prefix>_match` an acceptable spelling for the
   unconditional match-here entry, or does OS-0 (or Frank) want a different
   name? No ruling picks one.
3. **Confirm §5/§12.3-4**: is the group index scoped to NAMED groups only
   (count 0 until `named-groups` lands), or should it include an entry per
   capturing group (named or not) with `name = NULL` for unnamed ones? The
   bsearch-by-name framing in D39 suggests named-only, but this is inference,
   not a ruling.
4. **§11 item 7 / §12.8**: what should a DFA-compiled, group-bearing,
   non-backreference pattern's `caps[1..ngroups]` contain via the retrofitted
   match-here entry, given the DFA engine has never tracked sub-group
   offsets? Candidates: (a) leave `caps[1..]` at `RX_UNSET` always until the
   pattern is routed to the VM (M4.6's engine selection), effectively
   under-promising C6 for this interim population of patterns; (b) force
   ANY capturing group (not just backrefs) onto the VM starting at M4.5,
   simplifying the DFA's contract to always be 0-group; (c) something else.
   This is genuinely M4.2/M4.6 territory, not M4.1's, but the freeze
   document surfaces it because [M4.4] will hit it mechanically.
5. **§6**: is `pcrec_err_input` / `PCREC_ERR_INPUT_PATTERN` /
   `PCREC_ERR_INPUT_TEMPLATE` an acceptable spelling, or does Frank want a
   different field name than `input` (e.g. `which`, `source`)?

No genuine contradiction between D38 and D39 was found — every tension
encountered (ncap-as-watermark vs. C6's no-watermark rule, §2.1; the group
index's "(empty-ref)" phrasing vs. this document's stronger "(empty,
period)" reading, §5) resolved on inspection rather than blocking. The five
items above are gaps the rulings left unfilled, not disagreements between them.
