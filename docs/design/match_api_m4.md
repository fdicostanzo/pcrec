# M4 match-API freeze — the collected contract

> ## GRADUATED ([M4.7f], 2026-08-18) — THE CONTRACT NOW LIVES IN docs/spec/
>
> This document's design reasoning and ruling history stay here and remain
> the reference for *why* the contract is what it is. The CONTRACT ITSELF —
> what pcrec promises an embedder, actively maintained — is now
> `docs/spec/match_api.md`. On any disagreement between the two, the spec
> wins; two were found and corrected at graduation rather than silently
> reconciled: the give-up-code collapse this document's §3 still describes
> was superseded by D49 before graduation (the shipped `<prefix>_match`
> propagates give-up codes uniformly, not `-1`-collapsed — see the spec's
> §3.5), and `rx_info` ships as a struct TAG (`struct rx_info`), not the
> bare typedef §5's layout sketch shows (see the spec's §2; still an open
> Frank ruling, `docs/dev/plan.md`'s history). The R22 §2.2 addendum below
> (cross-iteration retention, empty-final-iteration overwrite) is folded
> into the spec's §5.1 as first-class contract prose, not carried as an
> addendum there.

> ## PANEL OUTCOME (R21) — READ BEFORE ANY SECTION BELOW
>
> A three-critic panel (R21, `docs/dev/reviews/2026-08-14-r21-m4-design.md`)
> reviewed this document together with `engine_m4.md` and the two ruled
> inputs. Dispositions ratified in `docs/dev/decisions.md` D44. This fix
> round applies every FIX-NOW and every D44 RULE outcome that touches this
> document, in place, marked **RULED (D44)**/**(R21)**: the search-entry
> signature reshapes to a caps-array-only form at [M4.4] (§1, A-1); the
> `<prefix>_span` typedef RETIRES rather than surviving as a compatibility
> alias (§1); the ncaps vocabulary is restated end-to-end so `ngroups` never
> again means two things (§2, A-5); `rx_group_entry` is BORN with a `slot`
> column (§5, A-4); `rx_info` is hardened — `unsigned abi` first member,
> widened `flags`, `int64_t step_budget`, `engine`/`engine_why` split,
> `pattern_len`, the invariant `rx_info.ncaps == RX_NCAPS` (§5, A-3/A-10/
> A-11/A-12/A-15/A-16); the ABI-type include guard is prefix-independent
> (§11, A-2); the M4.5-mechanism/M4.6-calibration counter correction lands
> (§11, C-1); `--no-captures` × a `$n`-referencing `--replace` is a
> compile-time error (§11, A-9); `PCREC_CASELESS` is the ruled spelling
> (§8, D44.8). Superseded text is struck/annotated in place per this
> document's own house style, not silently rewritten.

**STATUS: FROZEN — the M4 WORKING BASELINE, declared at [M4.3]'s close
(2026-08-14, R21 dispositions applied and sanitizer-green K17 fix
merged).** The freeze's WEIGHT is calibrated by D44's addendum: this is
the settled surface [M4.4]–[M4.7] build against without mid-build drift —
NOT a v1 contract. The post-run review at [M4.7]'s close is EXPECTED to
revise it with the running engine's measurements in hand, under D40
regime 1's announced-break form; build-time disagreements resolve toward
running code and are recorded for that review (miscompile-shaped findings
always stop the line). The as-built contract graduates to docs/spec/ at
[M4.7] (D40 addendum).

*(Original status, kept for history:)* PROPOSED — this document does not
itself rule anything; it collects rulings that already exist
(`docs/dev/decisions.md` D38, D39, and D38's PC-5 disposition of
`docs/pcre2_options.md`) into one place, precisely enough that [M4.4] can
apply the break mechanically and [M4.3]'s panel can attack a single
surface instead of three overlapping documents.

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
`RX_UNSET` (§2) belong to namespace 1 and are untouched by the
PCREC_*/PCRE2_* ruling.

**A third family, present since §4 and grown by D43: fixed-literal ABI
TYPES**, scoped by NEITHER namespace — `rx_ctx`, `rx_matchfn`,
`rx_callout_ref` (§4), and now `rx_info`/`rx_group_entry` (§5, D43.1). Their
TYPE names never carry `--prefix`; their per-artifact INSTANCE symbols do
(`<prefix>_info`, like `<prefix>_match`). §7's table marks this family
"neither." The group index (D39/F8) used to sit in namespace 1 as
freestanding `<prefix>_group_entry`/`<prefix>_groups[]`/`<PREFIX>_NGROUPS`
symbols; D43 moves it into this third family as `rx_info` members — see
§5's own note on why folding it into a genuinely shared `rx_info` forces
its element type fixed-literal too.

---

## 1. The `rx_span` → `ptrdiff_t[2]` pair break, RESHAPED (D44.2) into the caps-array search signature

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

**SUPERSEDED (D44.2, R21 A-1) — the `<prefix>_span[2]`-array-typedef spelling
below is history, kept per house style, not the shape [M4.4] emits.** The
R21 panel MEASURED a live hazard in it: an unchanged [M4.4]-era caller,
recompiled against the bigger M4.5-era artifact with no source change,
silently stack-smashes at run time with zero diagnostic, because the array
typedef and a hypothetical wider one are both just `ptrdiff_t[N]` — nothing
in the type system catches the size change. A struct or, as ruled, a
caps-array PARAMETER catches it as a hard compile error instead. The
post-M4.5 `_search` signature this section originally left unstated is the
actual root cause the panel names (A-1's finding): declare the final shape
now, at [M4.4], so there is no interim shape to grow out from under a
caller.

**What it becomes, as originally read (superseded reasoning, kept for the
record).** `design_callout_abi.md` F3 requires *one* capture
representation, not a conversion between two: `rx_ctx.caps` is
`const ptrdiff_t (*)[2]`, `{-1,-1}` = unset (§2 below). "No permanent
conversion seam" (D38 Q12) rules out keeping `<prefix>_span` as a
`size_t`-typed struct alongside a new `ptrdiff_t`-typed `caps` array forever —
the two must become the same representation. Concretely, the whole-match span
**is** `caps[0]`: a half-open `[start, end)` pair, `ptrdiff_t` elements.

~~**PROPOSED-here (§12.1)** the concrete spelling M4.4 emits, since neither
D38 nor the two carrying docs pick one:~~

```c
/* SUPERSEDED (D44.2) — this typedef never lands. Kept as history only. */
typedef ptrdiff_t <prefix>_span[2];   /* [start, end); {-1,-1} on no match */
int <prefix>_search(const unsigned char *s, size_t n, size_t startpos,
                     <prefix>_span *m);
```

~~i.e. `<prefix>_span` stays the name `emit_span_typedef` already emits and
`<prefix>_search` keeps its existing signature shape — only the element type
and struct-vs-array representation change, to `ptrdiff_t[2]`, so that a
`<prefix>_span` and a `caps[k]` pair are byte-for-byte, type-for-type
identical (F3's "one representation" read literally: not merely
same-field-types, but the *same type*). This is what makes `caps[0]` and the
top-level `<prefix>_search` output interchangeable without a cast or a
conversion function anywhere in generated or embedder code.~~

### 1.0 RULED (D44.2, 2026-08-14) — the search entry's FINAL shape, effective [M4.4]

> `int <prefix>_search(const unsigned char *s, size_t n, size_t startpos,
> ptrdiff_t (*caps)[2]);`

- **`caps[0]` IS the whole-match span** (F3's "one representation" taken
  literally — not merely same-field-types, the *same type* and the *same
  array*, with no second name for element 0).
- **`RX_NCAPS` pairs are written on match** — the full caps array the
  artifact promises (§2.1's D42.2 artifact-property rule; `RX_NCAPS` is 1
  on a DFA-compiled artifact today, growing only once [M4.5]'s VM exists).
- **`caps` MAY be `NULL`.** A caller who wants existence-only search (today's
  entire caller population) passes `NULL` and gets exactly today's `1`/`0`
  contract with no array to declare — this is what makes the reshape free
  for every existing caller rather than a tax that forces a `caps[RX_NCAPS][2]`
  declaration on someone who never wanted one.
- **`<prefix>_span` RETIRES.** It does not survive as a typedef, a
  compatibility alias, or a second name for `caps[0]` — one break, no second
  one staged for [M4.5]: `RX_NCAPS` simply grows from 1 upward and the same
  `caps` parameter accommodates it with no further signature change. This is
  what "no permanent conversion seam" (D38 Q12) means taken to its conclusion
  — not two representations kept in sync, but one parameter that is already
  the final shape.
- **Negative returns are D42.3's reserved space, unchanged by the reshape**
  (§1.1 below) — the reshape is additive to the return-value ruling, not a
  revision of it.

**Exactly which artifacts change**, so [M4.4] is a checklist rather than a
rediscovery. **RULED (D44's ratification of A-7): the list gained three
sites the original grep-based inventory missed**, because they read a
member (`m->start`/`m->end`), which no `_span`/`start.*end` grep catches —
the same "symbol-pattern greps degrade silently when the underlying shape
changes" hazard this list already names for `tests/codegen/`, now caught by
the panel on its own inventory:

- `src/gen/emit_dfa.c`: `emit_span_typedef` (the `size_t start, end` struct
  literal at line 106, RETIRED per §1.0 — the function is deleted, not
  changed to emit a new typedef) and every `%s_span *m` declaration/
  definition site (`emit_search_decl`, `emit_search_head`, both change to
  the `ptrdiff_t (*caps)[2]` parameter of §1.0).
- **`src/gen/emit_dfa.c:468`** (`emit_unanchored`'s search body):
  `if (m) { m->start = sfound; m->end = end; }` — becomes a write into
  `caps[0][0]`/`caps[0][1]` (and, once RX_NCAPS > 1, the rest of the array),
  guarded on `caps != NULL` per §1.0's NULL-allowed rule (A-7).
- **`src/gen/emit_dfa.c:564`** (`emit_attempt`'s per-start loop):
  `if (m) { m->start = start; m->end = last; }` — same conversion, same
  guard (A-7).
- **`src/gen/emit_dfa.c:610`** (the `--emit-main` generated `main()`):
  `m.start`/`m.end` field access and the `printf("match %zu %zu\n", ...)`
  format both change — the field access becomes `caps[0][0]`/`caps[0][1]`
  indexing, and **the `%zu` format specifiers become `%td`** (`ptrdiff_t`'s
  conversion specifier; `%zu` is `size_t`'s and is a format-string type
  mismatch, UB under `-Wformat`, once the field type changes) (A-7).
- `lib/pcrec.h`: the doc comment describing `<prefix>_search`'s contract
  ("byte offsets, end exclusive" — update the type AND the parameter shape,
  not merely the type as the superseded draft above assumed).
- `tests/harness/driver.c` and any other consumer of `.start`/`.end` field
  names — the array form has no field names, so these become `caps[0][0]`/
  `caps[0][1]` or an equivalent macro; **PROPOSED-here**, this is exactly the
  kind of consumer-side churn D37's "one announced break commit" shape exists
  to bound: it lands in the SAME commit as the emitter change, not staged.
- Anywhere the corpus or codegen structural checks grep for `_span` or
  `size_t start, end` (`tests/codegen/run_codegen_tests.sh`, per its own
  CLAUDE.md note about symbol-pattern greps degrading silently when the
  underlying shape changes — the same hazard OS-0b already fixed once for a
  different reason, and the same hazard A-7 just found a second instance
  of, in this very checklist).

**RULED (D44, A-8) — the failure-path contradiction is resolved: UNTOUCHED
wins everywhere.** ~~A prior draft of this section stated `{-1,-1}` is
written to `*m`/`caps` on no match.~~ That sentence is DELETED, not merely
annotated, because it directly contradicted §3.1 and engine_m4.md §3.4's
"on a failed match the caller's array is UNTOUCHED (nothing was copied)" —
one property, stated once, correctly, at §3.4 below; this section no longer
restates it in a form that could drift out of sync. The `int` return value
alone communicates match/no-match; a failed `<prefix>_search` call leaves
`caps` (if non-NULL) exactly as the caller left it.

**This is a [DD-3] generated-API-versioning event**, scheduled to land WITH
the M4 freeze rather than after it (D38 Q12's own framing, subst note §9 Q12).
No deprecation period, no compat shim in the base contract — one break, one
commit, D37's "announced-boundary" shape (a version-line boundary, not a
silent drift). **D44.2 does not add a second break**: the reshape lands in
the SAME [M4.4] commit as the originally-planned `rx_span` break, not as a
follow-on event — the panel's finding is about what shape that one commit
emits, not about adding a second commit.

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
 *   1              match found; if caps != NULL, RX_NCAPS pairs written,
 *                  caps[0] the whole-match span (§1.0, D44.2)
 *   0              no match; caps untouched (A-8)
 *   RX_ERR_STEPS   step budget (DD-2, engine §4.2) exhausted
 *   RX_ERR_FRAMES  backtrack-frame/trail capacity (engine §4.5) exhausted
 *   RX_ERR_WORK    work bound exhausted -- ADDED by the D47 SECOND ADDENDUM
 */
```

**AMENDED (D47 SECOND ADDENDUM + D49, 2026-08-17) — a THIRD code, and the
partition of the space below it.** Settlement 4 gives the frameless forward
work its own bound, so `RX_ERR_WORK` joins the two above on the same
reservation basis (`counterk_design.md` §7.4/§7.5). The step budget is
UNCHANGED — same meaning, same unit, same default — which is the property
that settlement chose over the alternatives.

D49 then partitions the negative space rather than leaving it open-ended:

```c
/* RX_ERR_FLOOR  the give-up block's floor. Codes in [RX_ERR_FLOOR, -2] are
 *               TYPED GIVE-UPS a caller may read and propagate; anything
 *               strictly BELOW the floor stays RESERVED for the future abort
 *               semantic that design_callout_abi.md F2 traps on.
 */
```

The floor is emitted as a NAME beside the codes (per-prefix, with its three
siblings — see `src/gen/emit_dfa.c`'s `emit_ncaps_macros` for why that
placement was chosen over the shared ABI block, and when to revisit it)
precisely so F2's call-site check stops transcribing a literal that the next
give-up code silently invalidates.

**Today's `1`/`0` contract KEEPS its meanings** — this reservation adds new
negative outcomes, it does not renumber the existing two. A DFA-only
artifact (pre-M4.5, or any `--no-captures` build, D42.1) never emits a step
or frame counter and so never returns either code; they become live only
once the counter MECHANISM exists on the VM path. **CORRECTED (D44,
ratifying R21 C-1) — the counter's landing is two substeps, not one**:
[M4.5] wires the mechanism itself (a bring-up placeholder budget, per
engine_m4.md §4.6 — "provisional placeholder for bring-up only:
1,000,000"), and [M4.6] calibrates the shipped default from measurement
(D12's "budgets are set from measured medians, not vibes" discipline).
Both codes are therefore reachable starting at [M4.5], not [M4.6] — a
prior draft of this sentence said "[M4.6]" for both landing points, which
conflated wiring with calibration; `docs/dev/plan.md`'s own [M4.5]/[M4.6]
rows already carry this split correctly (§11 item 9 restates it). The
concrete integer values are [M4.4]'s emitter's to assign, not fixed by
this ruling.

---

## 2. The caps array surface: `rx_ctx.caps`, `RX_NCAPS`, `RX_UNSET`, and the C1–C11 conformance table

**RULED (D38, applying subst note §10):** *"Adopt §2's C1–C11 as requirements
on M4's match API... together with §2.2's explicit non-requirements. C4 and C5
are now stated in the callout ABI's `rx_ctx.caps` representation, per F3."*

**RULED (D44, ratifying R21 A-5) — VOCABULARY RESTATEMENT, not a
re-ruling.** D43 addendum 2 already gives `rx_info` three distinctly-named
counts (§5 below): `ncaps` (the artifact's `caps[]` geometry, all-in),
`ngroups` (the pattern text's lexical capturing-group count, independent of
engine/`--no-captures`), and `nnames` (the named-index length). This
section, written before that addendum landed, still phrased C3/C6 and
D38.6's watermark rule as "`ncap = ngroups + 1`" — a leftover from when
those were believed to be the same number. **They are not, in general**
(D43 addendum 2's whole point): a `--no-captures` build has `ngroups > 0`
but `ncaps == 1`. Below, every occurrence of "`ngroups + 1`" describing
`RX_NCAPS`/`ncap`'s completed-match value is restated as "`ncaps`
(`RX_NCAPS`)" — the ARTIFACT fact, not the pattern-text fact. This changes
no requirement C1–C11 imposes; C6 always meant "every slot this artifact
actually delivers," and `ncaps` is now the name for that count everywhere
in this document, matching `rx_info`'s own field name (§5).

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
- **Every pair `0..ncaps-1` is written on a completed match** (C6,
  RESTATED in `ncaps` vocabulary per D44/A-5 above — `ncaps` here is
  `RX_NCAPS`, the artifact's delivered slot count, not `ngroups`, the
  pattern text's lexical group count); no watermark, no guard needed at
  read time for a completed match.
- **`ncap` is a mid-match watermark at callout sites and is PINNED to
  `ncaps` (`RX_NCAPS`) on a completed match**, with every pair written
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
| C2 | O(1) indexed access by number, flat sequence | **RESTATED (D44.3) — O(1) BY SLOT**: `caps` is `const ptrdiff_t (*)[2]`, a flat array indexed directly by SLOT (§5's `rx_group_entry.slot`, not by group NUMBER unconditionally — a group's number and its slot coincide only when every group up to it delivers a slot, e.g. no `--no-captures` and no unnamed-group-skips-a-slot composition case; the O(1) property itself is untouched, only which index a reader uses to get it) |
| C3 | index 0 is the whole match, exists at 0 groups | `caps[0]` is the whole-match span (§1); `RX_NCAPS >= 1` always (`ncaps >= 1`, minimum 1 — D44/A-5 vocabulary) |
| C4 | byte offsets, half-open `[start, end)`, two-element pair | `ptrdiff_t[2]` per pair, AMENDED element type per D38 Q12 |
| C5 | distinguished unset value in BOTH slots, named constant | `{-1, -1}`; `RX_UNSET` macro so a caller never hard-codes either spelling |
| C6 | every pair `0..ncaps-1` written on every successful match | stated explicitly above; `ncap == ncaps` (`RX_NCAPS`) is the completed-match contract (D44/A-5 vocabulary — was "`ngroups + 1`") |
| C7 | caller-owned, fixed-size, compile-time-constant count | `RX_NCAPS` macro; no allocation anywhere in generated code |
| C8 | spans stable for the duration of one splice | RULED (D38): the matcher MAY overwrite the caps buffer between separate match calls; a completed match's caps are stable until the NEXT match call reusing the same buffer — a documented consequence, not an accident |
| C9 | PCRE2 numbering: left-to-right by opening paren, non-capturing groups don't consume a number | unaffected by M4 — already the parser's shipped, measured behaviour (`--count-groups`) |
| C10 | name→number is compile-time, no runtime lookup REQUIRED for `${name}` resolution | the template compiler resolves `${name}` at pcrec-compile time and emits no names; **AMENDED by D39** — F8's group index (§5) is exported anyway, but for a DIFFERENT customer (embedders, V-A), not to satisfy C10 |
| C11 | success/failure is a return value, not an error object | `rx_matchfn`/the match-here entry returns `ptrdiff_t` (length, or `-1`); no error struct on the match path |

**[M4.5d] AS-BUILT ADDENDUM (2026-08-15, R22 — WHAT VALUE a written slot
carries; C6 says every slot is written, not what with):** two rules the
D27-blinded capture author found stated nowhere, MEASURED three-way
unanimous (python `re`, libpcre2 10.46 via probe, pcrec — R22 findings
1–2, review file 2026-08-15-r22-m45d-capture-author.md):
1. **Cross-iteration RETENTION**: a group inside a quantifier whose
   subexpression did not run in the FINAL iteration retains its value
   from the last iteration in which it DID run — `((a)|(b))*` on "ab"
   reports g2 = [0,1), not unset. Unset means "never participated in
   the whole match", not "didn't participate in the last iteration".
2. **Empty final iteration OVERWRITES**: `(a*)*` / `(a?)*` on "aaa"
   report g1 = [3,3) — an empty final iteration's write is a write.
Wording pass owed at M4.7's post-run review; recorded here so the
contract text stops under-specifying what the three engines already
agree on.

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
/* returns matched length >= 0 (anchored at ctx->pos), -1 (fail), or a typed
 * give-up code in [RX_ERR_FLOOR, -2] (D49, superseding D42.3's collapse).
 * Self-contained: must accept ctx->ncap == 0, ctx->caps == NULL. */
```

**AMENDED (D49, 2026-08-17): the bare `<prefix>_match` CARRIES the give-up
codes.** D42.3 had collapsed every give-up to `-1` here — the sole deliberate
exception to the distinct-codes contract, forced only by the reservation this
type's own `< -1` space was under. D49 supersedes it on three grounds, none
of which is D42.3's own stated re-open trigger (a composition customer, which
still has not appeared): pcrec is pre-release, so a "final" label reads as
"stable absent a reason" (D47 SECOND ADDENDUM's rider); the typedef is
BIDIRECTIONAL, so under the collapse an embedder-WRITTEN callout had no legal
spelling for "I gave up" at all, its only option being a value that traps the
process; and the collapse let an inner give-up read as a plain path failure,
so an outer match could report an ANSWER where a bound had actually blown —
a wrong answer, not merely a lost diagnostic. A caller that only asks "did it
match" still writes `r < 0` and is unaffected; only an exact `== -1` test
moves.

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

  **SUPERSEDED IN PART (D49, 2026-08-17) — the space is PARTITIONED, and the
  trap's bound is a NAME.** `< -1` is no longer reserved WHOLE for abort. It
  splits: `[RX_ERR_FLOOR, -2]` are typed give-up codes that a matcher DOES
  produce (`RX_ERR_STEPS`, `RX_ERR_FRAMES`, `RX_ERR_WORK` — §1), and only
  values strictly below the floor remain reserved for abort. F2's obligation
  therefore respells, and every call site must use the name rather than the
  literal:

      if (ret < RX_ERR_FLOOR) __builtin_trap();

  What this cost, stated because the ruling accepted it with eyes open: a
  future abort semantic loses `-2` as its cheapest encoding and must live
  below a give-up block whose size is fixed before anyone knows how many
  give-up codes there will eventually be. Getting the partition wrong
  pre-release costs a renumber and nothing else, which is the whole reason it
  was affordable to take now — VERIFIED at the time of ruling: ZERO generated
  files contain the trap line, because module `callouts` has no producer
  (`src/gen/emit_vm.c`'s `VE_CALLOUT` is marked reserved), so the call-site
  codegen that must change does not exist yet.
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

**PROPOSED-here — give-up behavior (manager addition at review,
2026-08-14).** `<prefix>_match_caps` is NOT an `rx_matchfn` (two
parameters, a different function type), so D38.4's `< -1` reservation and
F2's trap rule do NOT bind it — its negative return space below `-1` is
pcrec's own, by exactly the "`rx_search` is not an `rx_matchfn`"
observation (engine_m4.md §4.4) one entry over. Proposal: on a
budget/frame-carrying artifact it MAY return `RX_ERR_STEPS`/
`RX_ERR_FRAMES` (D42.3's search precedent) rather than collapsing give-up
into `-1` as `<prefix>_match` must — a tokenizer looping on this entry
wants to distinguish "no token here" from "the engine gave up". Rejected
alternative: `-1`-only for symmetry with `<prefix>_match` — rejected
because the symmetry is with the wrong sibling: `<prefix>_match`'s
collapse is FORCED by its frozen ABI type, and copying a forced limitation
into an entry that has room for honesty inverts the reason the limitation
was accepted (D42.3, §11.1 of engine_m4.md). Like the search codes, both
values are reserved at [M4.4] and become live only when the counters exist.

**AMENDED (D49, 2026-08-17) — the asymmetry this paragraph reasons about is
GONE, and the paragraph is kept because its reasoning is what removed it.**
Both entries now carry the same distinct codes (three of them: `RX_ERR_WORK`
joined at the D47 SECOND ADDENDUM). So "rather than collapsing give-up into
`-1` as `<prefix>_match` must" no longer describes anything — `<prefix>_match`
must not, because D49 unfroze the reservation that forced it.

The rejected alternative above was rejected for the right reason and the
argument survives intact: the symmetry WAS with the wrong sibling, because
`<prefix>_match`'s collapse was forced rather than chosen. D49 simply removed
the force instead of continuing to work around it — which is what the
paragraph's own sentence, "copying a forced limitation into an entry that has
room for honesty inverts the reason the limitation was accepted", implies once
the limitation itself becomes movable.

**RULED (D44, R21 panel review) — both properties above CONFIRMED, no
change.** The panel reviewed this signature (§13 ASK 4/D41.4's own
reference) and raised nothing against it: `caps_out` untouched on failure
stands (the same A-8 "untouched wins" rule §1 states for `<prefix>_search`
— one property, two entries, no divergence), and the `RX_ERR_STEPS`/
`RX_ERR_FRAMES` give-up-code proposal stands as this section's own answer,
reserved and inert until [M4.5] wires the counter mechanism (bring-up
placeholder) and [M4.6] calibrates it (D44/C-1's M4.5-mechanism/
M4.6-calibration correction, §1.1), exactly as written above.

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

## 5. The `rx_info` reflection structure (D43, HARDENED by D44/R21) — F8's group index folds in

**RULED (D43.1, 2026-08-14):** every generated artifact exports a static
REFLECTION structure — a fixed ABI type `rx_info` (fixed-literal name per
D41.1's family — see §7's table, and §0's third naming family below), one
`extern const rx_info <prefix>_info` per artifact, `.rodata` only, zero
runtime cost. This SUPERSEDES engine_m4.md §5.5's comment/macro-only
stamping direction as the CANONICAL machine-readable record — comments
stay for humans; macros stay where compile-time-useful (engine §5.5
carries the applied amendment).

**RULED (D44.5, 2026-08-14, ratifying R21 A-3/A-10/A-11/A-12/A-15/A-16 —
the layout below is FINAL, replacing the §5 layout D43 left to this
amendment round.** The panel measured or reasoned six independent defects
in the prior sketch (a genuinely-ambiguous `ncaps` reading, no
layout-version member, `long` width instability, a NUL-terminated pattern
string with no escaper for it, `engine` as a string beside `encoding` as
an int, and a struct that had already grown once mid-round with no
mechanism to say so) — the layout below closes all six in place:

**[M4.4] AS-BUILT DEVIATION (2026-08-14, recorded for M4.7's post-run
review; needs a ruling):** `rx_info` is emitted as a struct **TAG ONLY**
(`struct rx_info { ... };`, no typedef alias), and every reference spells
it `struct rx_info` — NOT the bare-typedef spelling the snippet below
shows. Found miscompile-shaped at implementation: `<prefix>_info` under
the DEFAULT prefix `rx` is the literal identifier `rx_info`, byte-identical
to this type's own name, and a typedef name and a variable name cannot
coexist in one C scope (gcc: "redeclared as different kind of symbol") —
every default-prefix build failed to compile. Struct tags live in a
separate C namespace, so the tag and the instance coexist. This is the one
of the six ABI types where the collision is reachable ("info" is the only
per-artifact suffix that is verbatim a whole ABI type name). OPEN for
Frank: bless `struct rx_info` as the ABI's real C spelling, or rename the
per-artifact instance and restore the typedef. Emitter record:
src/gen/emit_dfa.c (emit_rx_abi_types / emit_info_decl comments), landed
with the [M4.4] break commit.

```c
typedef struct {
    const char *name;
    int         number;
    int         slot;     /* RULED (D44.3, ratifying A-4): caps[] index
                              this entry delivers, or -1 if this build
                              delivers no slot for it (e.g. a
                              --no-captures primary referencing a named
                              group before V-E lands, or any named group
                              on a --no-captures artifact) — see the note
                              below C2's O(1)-BY-SLOT restatement (§2.2) */
    const char *ref;      /* NULL/empty for the primary's own groups;
                              carries the labeled insertion path once
                              V-E's rx references exist */
} rx_group_entry;

typedef struct {
    unsigned      abi;            /* RULED (D44.5, A-10): layout VERSION,
                                      FIRST member unconditionally — this
                                      struct already grew once (D43
                                      addendum 2) with no way for a reader
                                      to detect the shape it links against;
                                      bumped whenever a member is added,
                                      removed, or reordered below */
    /* --- scalars grouped for layout (D44.5, A-17) --- */
    uint64_t      flags;          /* RULED (D44.5, A-12): PCREC_* option
                                      bits, exactly as compiled (§8) —
                                      widened from `unsigned int` to a
                                      fixed-width 64-bit type; a 32-bit
                                      field against a ~74-row PCRE2 option
                                      survey (docs/pcre2_options.md) plus
                                      pcrec's own bits was a foreseeable
                                      DD-3 event this round pre-spends */
    int           encoding;       /* PCREC_ENC_* */
    int           ncaps;          /* RULED (D44.5, A-3): = RX_NCAPS,
                                      the ELEMENT COUNT — ALL-IN by
                                      definition (whatever slots THIS
                                      build actually delivers, including
                                      V-E's referenced-pattern
                                      contributions once they exist).
                                      STRUCTURAL invariant, checkable from
                                      [M4.4]: rx_info.ncaps == RX_NCAPS.
                                      (Prior sketch read "= RX_NCAPS - 1",
                                      an off-by-one against its own
                                      sizing use — A-3's finding.) */
    int           ngroups;        /* capturing groups in THIS PATTERN's
                                      own TEXT — a lexical fact,
                                      independent of --no-captures and of
                                      references (D43 addendum 2); NOT
                                      always == ncaps, see the note below */
    int           nnames;         /* RULED (D44/D43-addendum-2, spelling
                                      per addendum 2): entries in
                                      `groups`, named groups only
                                      (D41.3); <= ngroups; 0 until module
                                      `named-groups` lands. Spelling
                                      `nnames` REPLACES `ngroups_named`
                                      everywhere in this document per the
                                      addendum's own naming */
    unsigned      engine;         /* RULED (D44.5, A-15): ENGM_* — the
                                      SAME enum vocabulary
                                      engine_m4.md §5.1's EngineFit and
                                      the registry's `engines` column
                                      already use (ENGM_DFA/ENGM_VM),
                                      not a second ad hoc representation
                                      of the same fact as a string */
    int64_t       step_budget;    /* RULED (D44.5, A-16): widened from
                                      `long` (platform-width-unstable —
                                      LP64 vs LLP64) to a fixed-width
                                      64-bit type; -1 = none
                                      (--fno-step-budget), so a
                                      legitimately-configured ZERO budget
                                      is representable (the prior
                                      "<= 0 means none" reading could not
                                      distinguish "no budget" from
                                      "budget of zero") */
    int64_t       frame_capacity; /* RULED (D44.5, closing the "open,
                                      not resolved" item below): the
                                      SECOND DD-2 bound (D42.6,
                                      engine_m4.md §4.5) — backtrack-frame
                                      /trail capacity, joining
                                      step_budget rather than staying
                                      comment/macro-only. -1 = unbounded
                                      is not a real state (the arrays are
                                      always some compile-time constant);
                                      the field is simply that constant */
    int64_t       subject_ceiling; /* RULED (D44.1/D42.6, for the
                                      RESIDUAL unbounded class only —
                                      §4.5/§2.5 of engine_m4.md, D44.1's
                                      frame-ceiling design): the stamped
                                      honest ceiling on subject bytes a
                                      residually-unbounded capture-bearing
                                      body can safely process before
                                      frame/trail exhaustion is possible.
                                      0/unset for a pattern whose bodies
                                      are all deterministic-cursor (no
                                      residual class) or DFA-compiled */
    /* --- pointers --- */
    const char           *pattern;     /* RULED (D44.5, A-11): source
                                           pattern text, as given to
                                           pcrec_compile() */
    size_t                pattern_len; /* RULED (D44.5, A-11): companion
                                           length, K9-proof (K9:
                                           pcrec_compile() takes no
                                           pattern length today, so a
                                           pattern containing a NUL
                                           compiles as its prefix) — a
                                           NUL-terminated-only `pattern`
                                           would silently re-truncate at
                                           the exact byte K9 already
                                           flags as dangerous. See the
                                           escaping obligation below */
    const rx_group_entry *groups;      /* sorted, bsearch-able; NAMED
                                           groups only (D41.3) */
    const char           *engine_why;  /* RULED (D44.5, A-15): the
                                           forcing construct/reason,
                                           split OUT of `engine` into its
                                           own free-text field — mirrors
                                           engine_m4.md §5.5's
                                           RX_ENGINE_WHY macro, and keeps
                                           `engine` itself a clean enum
                                           comparison rather than a
                                           strcmp target. Reflects the
                                           prefilter bit too (A-15): a
                                           non-empty suffix on
                                           hybrid-eligible artifacts,
                                           e.g. "capture group at offset
                                           0; DFA prefilter available" */
} rx_info;

extern const rx_info <prefix>_info;
```

- **Sorted, bsearch-able, `.rodata` only, zero runtime cost** — same
  properties the freestanding index had; nothing about the DATA changes,
  only its container.
- **Does NOT travel in `rx_ctx` or any callback parameter**: like the
  freestanding index before it, `rx_info` is a link-time constant per
  pattern (queried by symbol), unlike everything in §2 and §4.
- **The pattern string is embedded UNCONDITIONALLY** (D43.3): artifacts
  carry their contract (D37 spirit). An omission axis (size/secrecy) may
  earn itself later if a real objector appears (D18); none exists today.
- **RULED (D44.5, A-11) — the escaped-C-literal emission obligation is
  STATED, not discharged: no escaper for it exists in the codebase
  today.** `rx_info.pattern` is emitted as a C string literal
  (`"..."` — not the comment text `emit_pattern_comment` writes at
  `src/gen/emit_dfa.c:28-41`, which is the ONLY escaper this codebase has
  today and is NOT a string-literal escaper: it avoids `*/` and emits
  `\xNN` for non-printables so the text is safe inside a `/* ... */`
  comment, but it does nothing about `"` or `\`, both of which are legal
  and unescaped inside a PCRE pattern and both of which would terminate
  or corrupt a C string literal if copied through verbatim (a pattern
  containing `"` — e.g. `[^"]*"` — would emit a syntactically broken
  `.c` file). [M4.4] must write a STRING-LITERAL escaper (`"`, `\`,
  control bytes, at minimum) before `rx_info.pattern` can be emitted;
  `emit_pattern_comment` is cited here precisely so nobody mistakes it
  for one when implementing this member.
- **`ref` is NULL/empty for the primary pattern's own groups today** — V-E's
  labeled-reference numbering is the only future consumer of a non-empty
  `ref`; nothing produces one yet.
- **Named-only content, unchanged from D41.3**: `pcrec --count-groups
  '(?<g>a)(b)'` still fails with "requires module 'named-groups'" today, so
  `groups`/`nnames` are `NULL`/`0` on every pattern until that module
  lands. `ngroups` (the total) is INDEPENDENT of that gate — see the note
  below.
- **Second customer**: `V-A`'s `pcre2_pattern_info` (D43's own text; this
  supersedes this document's earlier framing of `V-A`'s
  `pcre2_substring_number_from_name` as the second customer — that reads
  `rx_info.groups` specifically, `pcre2_pattern_info` reads the whole
  struct). **Queued customers**: V-G (regex testing), V-H (debug/trace),
  and F7's per-pattern selection reporting (engine_m4.md §5.5).

**RULED (D44.3, ratifying R21 A-4) — `rx_group_entry` is BORN with `slot`,
not added later.** The panel found this reachable pre-V-E, not merely a
future edge case: `--no-captures '(?<g>a)'` on the D43.1-era shape (no
`slot` column) puts a named-group index entry into `groups[]` with
`number == 1` but a `--no-captures` artifact's `caps[]` has exactly one
element (`RX_NCAPS 1`, D42.2) — a consumer that assumed `slot == number`
(a reasonable reading of the OLD shape, since nothing said otherwise) reads
`caps[1]`, one element past the end of a one-element array. The `slot`
column makes the answer explicit and in-band: `-1` means "this build
delivers no slot for this group," full stop, no inference required. C2's
O(1) property is unaffected (§2.2's restatement above) — a reader now
indexes `caps[]` by `slot`, not by `number`, which is the D39-addendum
`ref`-column precedent applied a second time (a column exists so a reader
never has to infer what an absence means).

**RULED (D44, ratifying A-2) — `rx_group_entry` is a FIXED-LITERAL ABI
type, not `<prefix>_group_entry`.** Confirmed exactly as this document's
own prior synthesis argued (below, kept as the record of the reasoning):
D43.1 says `rx_info` is one fixed type shared by every artifact (per
D41.1's family, same reasoning as `rx_ctx` composability, §12.7). If
`rx_info.groups` pointed at a `<prefix>_group_entry`, the pointee type
would differ PER PREFIX, and `rx_info`'s own shape would then diverge
across differently-prefixed TUs — exactly the divergence §7/§12.7's
C-typedef-scoping safety argument requires NOT to happen. Folding F8 into
a genuinely uniform `rx_info` forces its constituent pointee type to go
fixed-literal too — the answer to "why does V-A need a single generic
type" is D43's own "further customers queued" framing: V-G/V-H are
plausibly MULTI-artifact tools, where a uniform type is the whole point.

**RULED (D43 addendum 2, 2026-08-14, confirmed and integrated in the
layout above): rx_info carries ALL THREE counts.** The third-count
question this round briefly opened is closed — Frank: "the more the
merrier, its essentially free." The struct carries `ncaps` (the
ARTIFACT's caps[] geometry — ALL-IN by definition, so V-E's
referenced-pattern contributions never make it wrong), `ngroups`
(capturing groups in THIS pattern's own TEXT, a lexical fact independent
of `--no-captures` and references), and `nnames` (the index length,
spelling per the addendum, replacing `ngroups_named` everywhere in this
document — D44/A-5's vocabulary restatement, §2 above). Ruled with it, a
V-E DIRECTION refining D39's addendum: a referenced regex's groups
contribute caps slots ONLY IF NAMED — named ones get slots and index
entries (ref-labeled); unnamed ones contribute nothing. Frank's motivating
scenario: a `--no-captures` primary referencing a captures-on pattern
with names reads as ngroups = primary text total, the NO_CAPTURES flag
bit (primary contributed zero), ncaps = just the referenced names'
contribution — no count carries two facts.

**Why `ngroups` is a genuinely new fact, not a restatement of `ncaps`.**
`ncaps` (`RX_NCAPS`, §2.1, D42.2) states what the ARTIFACT can DELIVER —
it is pinned to `1` on a DFA-compiled or `--no-captures` build regardless
of how many groups the PATTERN has. `rx_info.ngroups` states what the
pattern TEXT has, independent of engine selection or the captures-default
axis — useful precisely in the cases where `ncaps` alone under-informs: a
caller can ask "does this pattern have groups at all" on a pure-DFA
artifact where `ncaps` says only `1`. The two facts coincide only when
`ncaps - 1 == ngroups`, i.e. a VM-compiled, captures-on artifact — the
common case at [M4.5], but not a rule `rx_info` should be read as
restating.

**RESOLVED (D44.5, was "open, not resolved here"):** D43.1 named the step
budget as an `rx_info` member but not the backtrack-frame/trail capacity
(§4.5's SECOND DD-2 bound, engine_m4.md §4.5, D42.6's "DD-2's row names
two bounds" ruling); engine §5.5's ORIGINAL stamp comment showed both
bounds together (`/* Step budget: ...; backtrack frames: ... */`). D44.5
closes the asymmetry: `frame_capacity` joins `step_budget` above, and,
where E-3's residual-ceiling design applies (engine_m4.md §2.5/§4.5,
D44.1), `subject_ceiling` joins them both.

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
| `<prefix>_search` | 1 (per-artifact) | yes | unchanged name, RESHAPED signature — caps-array parameter, not a `*m` out-struct (§1.0, RULED D44.2); negative space RULED (D42.3, §1) |
| ~~`<prefix>_span`~~ | — | — | **RETIRED (D44.2, §1.0).** Does not land at [M4.4] and gains no compatibility alias — `caps[0]` is the whole-match span, one name, no second one. Row kept struck-through so a reader of this table's history sees the retirement rather than a silent row deletion. |
| the match-here entry | 1 | yes — `<prefix>_match`, RULED (D41.2, §12.6's proposal confirmed) | new; see §3 |
| `<prefix>_match_caps` | 1 | yes | new (D41.4); PROPOSED-here (§3.1, §12.9); give-up codes and untouched-on-failure CONFIRMED (D44, §3.1) |
| `<PREFIX>_NCAPS`, `<PREFIX>_UNSET` | 1 | yes (uppercased) | already spelled this way in the subst note's example; `RX_NCAPS`'s artifact-property rule RULED (D42.2, §2.1); vocabulary restated as `ncaps` throughout (D44/A-5, §2) |
| ~~`<prefix>_group_entry`, `<prefix>_groups[]`, `<PREFIX>_NGROUPS`~~ | — | — | **SUPERSEDED (D43.1, §5):** folded into `rx_info` — see the `rx_group_entry` and `rx_info`/`<prefix>_info` rows below. No freestanding index symbols land at [M4.4]. |
| `rx_ctx`, `rx_matchfn`, `rx_callout_ref` | **neither — fixed literal** | **no, RULED (D41.1, confirming §12.7)** | as spelled throughout `design_callout_abi.md`; RULED (D44/A-2, §11 item 2) — include guard is `PCREC_RX_ABI_H`, prefix-independent, so two differently-prefixed generated headers compile together in one TU |
| `rx_group_entry` | **neither — fixed literal** | **no, RULED (D44/A-2)** | FINAL shape `{name, number, slot, ref}` (D44.3, §5) — `slot` column added, fixed-literal status confirmed, not merely proposed |
| `rx_info` | **neither — fixed literal** | **no, RULED (D44/A-2)** | FINAL layout (D44.5, §5) — `abi` first member, widened `flags`/`step_budget`, `ncaps`/`ngroups`/`nnames` three-count split, `engine`+`engine_why` split, `pattern`+`pattern_len`, `frame_capacity`+`subject_ceiling` |
| `rx_renderfn` | **neither — fixed literal** | **no, RULED (D44, ratifying A-14)** | REGISTERED here as a fixed-literal ABI type — subst_template_design.md §7.2's renderer signature (`rx_matchfn` extended by an output buffer) was previously absent from this table and from §11's emission checklist, both corrected (item 2 below); inherits the same `PCREC_RX_ABI_H`-family guard obligation A-2 raises for the rest of this row-group |
| `<prefix>_info` | 1 (per-artifact) | yes | new (D43.1): `extern const rx_info <prefix>_info` |
| `rx_callout_<name>` | fixed literal `rx_callout_` prefix + the callout's own name | no | RULED (D38) shape |
| `pcrec_err_input`, `PCREC_ERR_INPUT_*` | 2 (library-fixed) | no | RULED (D42.4): spelling accepted; V-A compat alias obligation recorded (§6) |
| `PCREC_CASELESS`, `PCREC_EMIT_MAIN`, `PCREC_NO_CAPTURES` | 2 (library-fixed) | no | RULED (D44.8): `PCREC_CASELESS` — see §8 |
| `RX_ERR_*` on `rx_subst`'s return space | 2-adjacent (per-artifact error codes) | yes (uppercased prefix) | RULED (D44, ratifying A-14): `rx_subst` (subst_template_design.md §5.2) MISSED the D42.3 negative-space sweep when that ruling landed — its return space gains `RX_ERR_*` codes on the same reservation basis as `<prefix>_search`'s (§1.1), so a budget/frame-carrying substituter can report engine give-up rather than collapsing it into "no substitutions" |

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
applies only once a row's own work actually lands." No PC-5 row lands as
part of [M4.1]/[M4.4] — **this sentence is about `docs/pcre2_options.md`'s
own PCRE2-option-survey rows specifically, and stays true of them**; it is
NOT about `pcrec_options`' own pre-existing boolean fields, which D43.2
(below) DOES fund with concrete `PCREC_*` constants at [M4.4]. The two are
different populations: PC-5 rows are PCRE2-semantic options not yet
adopted; `caseless`/`emit_main`/the coming `no-captures` are pcrec's OWN
struct fields, already real, now getting a consistent bit-constant
representation.

**Manager-confirmed 2026-08-14 — what this ruling governs, stated so a
panel critic does not have to re-derive it.** Frank asked whether
`--no-captures`/`-i` map to `PCREC_*` options under the hood; the answer as
first recorded, then SUPERSEDED the same day by D43 (see the block below —
kept here rather than deleted, per this document's house style of
appending outcomes rather than erasing prior text):

- ~~The native option SURFACE is the `pcrec_options` STRUCT, not a
  bitmask — named fields (`prefix`, `encoding`, `caseless`, `emit_main`,
  `header_name` today). M4-era additions land the same way: the captures
  default's `--no-captures` becomes a field, not a `PCREC_*` bit.~~
- ~~No bitmask surface is being added natively.~~

**SUPERSEDED (D43.2, 2026-08-14).** Frank himself raised the options
funnel in the same session and ruled the opposite direction for BOOLEAN
fields specifically: CLI flag → `PCREC_*` bit constant → `pcrec_options.flags`
→ reflected verbatim in `rx_info.flags` (§5) is now the consistent,
end-to-end representation, adopted with all three of the amendment's
recommendations. What stands, corrected:

- **Boolean options become `PCREC_*` bits in ONE `flags` word.** `caseless`,
  `emit_main`, and the coming `no-captures` (D42.1) move from separate `int`
  fields to bits of a single `unsigned int flags` field. **Non-boolean
  options stay named fields** — `prefix`, `encoding`, `header_name`, and the
  M4-era step budget are UNCHANGED in shape, still typed struct members, not
  bits.
- **CLI flags are still a thin veneer**, now over the flags word instead of
  separate `int`s: `-i` becomes `opt.flags |= PCREC_CASELESS` (naming below);
  `--no-captures` sets its bit the same way. No CLI flag is itself the
  `PCREC_*` constant — the constant is what the flag SETS.
- **The `pcrec_options` struct BREAK lands on the [M4.4] announced
  boundary** (free pre-v1 per D40, one boundary per D37) — the same commit
  that carries the `rx_span` break and `rx_info`'s introduction, not a
  separate event.
- **ONE representation of the options fact end-to-end** (F3's
  one-representation rule, previously scoped to capture offsets, now
  EXTENDED to options by D43.2): the same boolean is the SAME bit from CLI
  parse through `pcrec_options.flags` through `rx_info.flags`, never
  translated to a different representation partway. The alternative — keep
  `int` fields internally and translate to bits only at emission time —
  was REJECTED (D43.2) as two representations of one fact, the same
  objection that shapes `rx_ctx.caps`/`<prefix>_span` sharing one
  `ptrdiff_t[2]` type (§1) rather than a conversion seam.
- **`PCREC_*` still names only the enum/bit-valued constants** — the
  distinction this section drew before stands, just with a bigger
  denomination: it now covers BOTH `PCREC_ENC_ASCII`-style enum values AND
  the new boolean bits, but still never the struct's field NAMES
  (`flags`, `encoding`) and never a bare CLI flag spelling.
- **V-A's compat layer is still where PCRE2 bits reappear**, unchanged:
  it translates `PCRE2_CASELESS` etc. onto the native `flags` word's bits
  at the boundary. Bits at the compat boundary, bits natively too now for
  booleans specifically — the compat/native split §8 draws for CONSTANT
  NAMES (`PCRE2_*` vs `PCREC_*`) is untouched; only the native SIDE's
  internal representation (struct field vs. flags-word bit) changed.

**RULED (D44.8, 2026-08-14) — the bit names, `PCREC_CASELESS` chosen:**

```c
enum {
    PCREC_CASELESS    = 1u << 0,  /* RULED (D44.8): was pcrec_options.caseless.
                                      NOT PCREC_CASE_INSENSITIVE — Frank's
                                      own sketch spelling, presented below
                                      as the rejected alternative */
    PCREC_EMIT_MAIN   = 1u << 1,  /* was pcrec_options.emit_main */
    PCREC_NO_CAPTURES = 1u << 2,  /* new, M4.5-era: --no-captures (D42.1) */
};
```

**RULED (D44.8): `PCREC_CASELESS`, not `PCREC_CASE_INSENSITIVE`** — this
document's own recommendation, ratified as written. Reasoning kept in
full: the D38-addendum PARALLEL-NAMING rule this same section states above
(§8's own RULED text: every PCRE2 option pcrec adopts gets a parallel
pcrec-native name) — `PCRE2_CASELESS` is the real PCRE2 constant this
option parallels, and a caller porting from PCRE2 (V-A's whole audience)
recognizes `PCREC_CASELESS` on sight where `PCREC_CASE_INSENSITIVE`
requires a name-mapping lookup despite meaning the same thing.
`PCREC_EMIT_MAIN` and `PCREC_NO_CAPTURES` have no PCRE2 equivalent to
parallel (both are pcrec-only knobs — a generated `main()`, and this
project's own captures-default axis), so no naming tension existed for
them and neither was reopened.

**The corrected `pcrec_options` struct, PROPOSED-here, `flags` widened to
match `rx_info.flags`'s D44.5 fixed-width type** (§5's one-representation
rule, F3/D43.2, requires the SAME bit end-to-end from CLI parse through
`pcrec_options.flags` through `rx_info.flags` — widening one without the
other would reintroduce exactly the two-representations defect D43.2
rejected, so this struct's `flags` widens alongside `rx_info.flags`):

```c
typedef struct {
    const char *prefix;       /* unchanged */
    int         encoding;     /* unchanged, PCREC_ENC_* */
    uint64_t    flags;        /* WIDENED (D44.5, matching rx_info.flags) —
                                  PCREC_CASELESS | PCREC_EMIT_MAIN |
                                  PCREC_NO_CAPTURES | ... */
    const char *header_name;  /* unchanged */
} pcrec_options;
```

`pcrec_default_options()` (`lib/pcrec.h`) initializes `flags = 0` (today's
`caseless = 0, emit_main = 0` defaults; `PCREC_NO_CAPTURES` unset means
captures ON, matching D42.1's default).

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

1. **RESHAPED (D44.2, §1.0) — RETIRE `<prefix>_span`, emit the caps-array
   search signature.** `emit_span_typedef` in `src/gen/emit_dfa.c` is
   DELETED, not changed to emit a new typedef; `emit_search_decl`/
   `emit_search_head` emit `ptrdiff_t (*caps)[2]` as the fourth parameter
   directly. Every `%s_span *m` site updates in the same commit, INCLUDING
   the three the original inventory missed (RULED D44/A-7, §1's own
   checklist): `emit_dfa.c:468` and `:564`'s `if (m) { m->start = ...;
   m->end = ...; }` member-access sites, and `emit_dfa.c:610`'s
   `--emit-main` `main()` — both its `m.start`/`m.end` field reads and its
   `printf("match %zu %zu\n", ...)` format, which becomes `%td` for
   `ptrdiff_t`. `lib/pcrec.h`'s doc comment updates; `tests/harness/driver.c`
   and any `_span`-pattern grep in `tests/codegen/` update in the same
   commit — one announced break, not a staged migration.
2. **Emit `rx_ctx`, `rx_matchfn`, `rx_callout_ref`, `rx_group_entry`,
   `rx_info`** (§4, §5, §7) as file-scope types, once per file — the same
   "ONCE PER FILE, shared by every engine in it" shape `emit_span_typedef`
   used before it was retired — since all five types are fixed (not
   `<prefix>`-scoped, §12.7/§5's D43 extension) and would collide if
   emitted more than once identically (harmlessly, but redundantly) or
   divergently (a build error, same class as today's duplicate-`rx_span`
   hazard). `rx_group_entry` and `rx_info` are new to this item this round
   (D43.1). **RULED (D44, ratifying A-2) — the guard is
   `PCREC_RX_ABI_H`, PREFIX-INDEPENDENT.** The panel MEASURED that the
   fixed-literal ABI types fail to compile in the exact composition case
   they exist for: two differently-prefixed generated headers in one TU
   each emit an include guard derived from their OWN prefix
   (`<PREFIX>_H`-style), so the guards are DIFFERENT and BOTH bodies
   re-define `rx_ctx`/`rx_matchfn`/etc. — the identical "conflicting
   types" class emit_dfa.c:92-96 already documents for what happens when
   `emit_span_typedef` runs more than once ("each occurrence declares a
   fresh anonymous struct type, so gcc rejects the file"), now reachable
   a second way — a hard redefinition error, not a harmless no-op. The
   fix: the
   block containing these five fixed-literal types is wrapped in its own
   guard, spelled identically regardless of the artifact's `--prefix`
   (`#ifndef PCREC_RX_ABI_H` / `#define PCREC_RX_ABI_H`), separate from
   whatever per-prefix guard wraps the rest of the header. **Also
   registered here (RULED D44, ratifying A-14): `rx_renderfn`
   (subst_template_design.md §7.2) joins this emission group and inherits
   the same guard** — it was previously present in the subst design note
   but absent from this checklist and from §7's naming table (both
   corrected this round), so a build emitting a callback-bearing
   substituter alongside another generated matcher in one TU was exposed
   to the identical redefinition hazard A-2 measured for the other four
   types.
3. **Emit the match-here entry unconditionally** (§3) — `<prefix>_match`,
   `rx_matchfn`-typed, accepting `ncap=0, caps=NULL` — retrofitted onto the
   EXISTING DFA matchers (per [M4.4]'s own plan-row text), alongside
   `<prefix>_search`, not replacing it. No trap-check call sites are needed
   yet (§3's scope note — no callers of `rx_matchfn` exist before callouts or
   V-E composition land).
4. **SUPERSEDED (D43.1) — no freestanding group-index symbols land.** The
   prior version of this item emitted `<prefix>_group_entry`/
   `<prefix>_groups[]`/`<PREFIX>_NGROUPS` directly. D43 folds F8 into
   `rx_info` instead (§5) — see item 10 below, which is what [M4.4] emits
   in this item's place. The group data itself (empty today, `ref` column
   present but unpopulated, content arrives with `named-groups`/V-E) is
   UNCHANGED; only its container changed.
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
   even though no engine produces either value until [M4.5] wires the
   counter MECHANISM (a bring-up placeholder budget) and [M4.6]
   CALIBRATES it from measurement (**CORRECTED, D44/C-1**: was "[M4.6]
   wires" — the plan's own [M4.5]/[M4.6] rows and engine_m4.md §4.6
   already draw this two-substep line; this checklist item now matches
   them) — the space must be reserved before any counter exists, not
   after, so a caller's `switch` written against [M4.4]'s output does not
   need revisiting later.
10. **Emit `<prefix>_info` unconditionally** (§5, D44.5's FINAL layout):
    one `extern const rx_info <prefix>_info` per artifact, `.rodata`,
    populated with `abi` (a fixed layout-version constant, D44.5), `flags`
    (from the compiled `pcrec_options.flags`, both now `uint64_t`),
    `encoding`, `ncaps` (`= RX_NCAPS`, ALWAYS — the [M4.4] structural
    check `rx_info.ncaps == RX_NCAPS` is live from this commit, trivially
    green until [M4.5] since `RX_NCAPS` is 1 everywhere pre-VM), `ngroups`
    (the parser's existing `Ctx.ncap` count — already computed for
    `--count-groups`, §1.2's inventory in engine_m4.md), `nnames`
    (NULL-backed `groups`/`0` until `named-groups`, same content as the
    old freestanding index, item 4 — spelling per D43 addendum 2,
    REPLACES `ngroups_named`), `groups`, `engine` (`ENGM_DFA` for every
    [M4.4]-era artifact — no VM exists yet — NOT the string `"dfa"` a
    prior draft of this item named; D44.5 splits the free-text reason
    into `engine_why`, empty/NULL at [M4.4]), `step_budget` (`-1`/none
    until [M4.5] wires the mechanism), `frame_capacity` (`-1`/unbounded
    until the same substep), `subject_ceiling` (unset until [M4.5]'s
    cursor-extension design, engine_m4.md §2.5/D44.1, has a residual
    class to stamp), and `pattern`/`pattern_len` (embedded
    unconditionally, D43.3, gated on [M4.4] first landing a
    string-literal escaper for pattern text — §5's A-11 obligation; no
    such escaper exists in the codebase today, `emit_pattern_comment`
    is NOT it). Every FIELD lands at [M4.4]; several are trivially
    empty/default until later substeps populate them, the same shape item
    4's group index already had before D43 folded it in.
11. **Break `pcrec_options`** (§8, D43.2/D44.8): `caseless`/`emit_main`
    become bits of a new `flags` field, widened to `uint64_t` (D44.5,
    matching `rx_info.flags`) — `PCREC_CASELESS` (RULED D44.8, not
    `PCREC_CASE_INSENSITIVE`) / `PCREC_EMIT_MAIN`; `pcrec_default_options()`
    initializes `flags = 0`; every CLI flag site (`cli/main.c`) that sets
    `opt.caseless`/`opt.emit_main` updates to `opt.flags |=` the bit; every
    consumer that reads the old `int` fields (`src/core/compile.c` and
    anywhere else `pcrec_options.caseless`/`.emit_main` is read) updates in
    the SAME commit — this is a `lib/pcrec.h` embedder-facing break, so it
    joins item 6's coverage-conservation inventory rather than being a
    separate, later-discovered failure.
12. **NEW (RULED D44.7, ratifying A-9) — `--no-captures` × a `$n`-referencing
    `--replace` template is a COMPILE-TIME ERROR.** This is a match-API-side
    obligation because the combination is reachable purely from ruled
    ground: a `--no-captures` build emits `RX_NCAPS 1` (D42.2), so
    `caps[1]` does not exist, and a template referencing `$1` against such
    a build would render the exact silent-`<>`-empty failure §5.7 of
    subst_template_design.md already rejected as candidate (a) when it
    considered leaving unset slots at `RX_UNSET` — the difference here is
    the slot does not exist AT ALL, which is worse, not better, than the
    rejected candidate. [M4.4] does not itself implement the check (no
    `--replace`/`[M4-SUBST]` code exists yet), but this item records the
    obligation so [M4.4]'s own `--no-captures` flag and [M4-SUBST]'s
    later template compiler both inherit it from the same freeze line
    rather than one of them discovering it unguarded.

---

## 12. Everything this document introduces beyond the rulings (for the manager / M4.3 panel)

Collected from the PROPOSED-here marks above, in one place per the brief's
house-style requirement. Items 3–8 were RULED by D41/D42 in the amendment
round (still listed — they are what the panel should check the ruling was
APPLIED to, not just that it exists); item 9 was reviewed by the R21 panel
and CONFIRMED (D44, §3.1); items 10–13 are RULED this round (D44.5/D44.3/
D44.8) — the panel reviewed the concrete layout/naming D43 had left open
and the layout above (§5) is now final, not merely proposed. Item 1 is
OVERTAKEN (D44.2): the search-signature reshape (§1.0) replaces the
question this item asked rather than answering it — there is no longer a
`<prefix>_span` concrete spelling to pick, because the typedef retires.
Item 2 is the one item in this list still genuinely open:

1. **§1 — OVERTAKEN (D44.2, R21 A-1).** ~~The concrete post-break spelling
   of `<prefix>_span` — `typedef ptrdiff_t <prefix>_span[2];`, keeping the
   existing name and `<prefix>_search` signature shape, changing only
   element type and struct-vs-array representation.~~ This question does
   not survive to be answered: the panel MEASURED a stack-smash hazard in
   the array-typedef shape itself (§1's own SUPERSEDED block), and D44.2
   replaces the whole approach with a caps-array SEARCH PARAMETER (§1.0)
   — `<prefix>_span` does not land in any form, so there is no spelling
   left to pick. Kept here, struck, so a reader of this item's history
   sees it was overtaken rather than silently dropped.
2. **§3**: the scope note that F2's `__builtin_trap()` call-site enforcement
   has no call sites to attach to yet at [M4.4] time (no callout/composition
   code exists), so [M4.4] emits the entry but not the trap-guarded call.
   **Still open** — genuinely so; the R21 panel raised nothing against it
   and it is not touched by any D44 disposition.
3. **§5**: the group-index C identifier spellings (`<prefix>_group_entry`,
   `<prefix>_groups[]`, `<PREFIX>_NGROUPS`) and the claim that the index's
   CONTENT (not just its `ref` column) is empty (count 0) until module
   `named-groups` lands. **RULED (D41.3).** **The SPELLING half is
   SUPERSEDED (D43.1, 2026-08-14):** these freestanding symbols no longer
   land at all — the index folds into `rx_info` (items 10–11 below). The
   CONTENT claim (D41.3, empty until `named-groups`) is UNCHANGED and now
   lives at §5 as `ngroups_named`.
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
10. **§5 — RULED (D44.5, 2026-08-14).** The concrete `rx_info` struct
    layout is now FINAL, not merely proposed: `abi` first member, scalars
    grouped, `flags`/`step_budget` widened to fixed-width 64-bit types,
    the three-count `ncaps`/`ngroups`/`nnames` split (D43 addendum 2),
    `engine` as `unsigned` (`ENGM_*`) with `engine_why` split out as its
    own free-text field, `pattern`/`pattern_len` as a pair (not a bare
    NUL-terminated pointer), and `frame_capacity`/`subject_ceiling`
    joining `step_budget`. The panel's measured/reasoned findings against
    the PRIOR sketch (A-3/A-10/A-11/A-12/A-15/A-16, six independent
    defects) are what the layout above closes — see §5's own account of
    each.
11. **§5 — RULED (D44, ratifying A-2).** `rx_group_entry` IS a
    fixed-literal ABI type (not `<prefix>_group_entry`), confirmed exactly
    as this document's own inference argued — see §5's "RULED (D44,
    ratifying A-2)" paragraph for the reasoning kept in full.
12. **§5 — RULED (D43 addendum 2, confirmed/integrated D44.5).** The
    `ngroups`/`nnames` split (renamed from `ngroups_named` per the
    addendum's own spelling) stands as this document proposed, now with a
    THIRD count (`ncaps`) alongside it rather than two — D43 addendum 2
    settled that the split should be three-way, not two-way, closing this
    item more completely than it originally asked.
13. **§8 — RULED (D44.8, 2026-08-14).** `PCREC_CASELESS`, not
    `PCREC_CASE_INSENSITIVE` — this document's recommendation, ratified as
    written. `PCREC_EMIT_MAIN`/`PCREC_NO_CAPTURES` were never in tension
    and are unchanged. The corrected `pcrec_options` struct shape
    (`flags` replacing `caseless`/`emit_main`) stands, with `flags` ALSO
    widened to `uint64_t` per item 10's `rx_info.flags` widening (§8's own
    one-representation cross-reference).

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
6. **RULED (D44.8, 2026-08-14) — the `PCREC_*` boolean bit names.**
   `PCREC_CASELESS`, not `PCREC_CASE_INSENSITIVE` — this document's
   recommendation (§8), ratified as written. `PCREC_EMIT_MAIN`/
   `PCREC_NO_CAPTURES` were never in naming tension and are unchanged.
7. **RULED (D44.5, 2026-08-14) — the `rx_group_entry`/`rx_info` layout in
   §5 is ACCEPTABLE, WITH ADDITIONS the panel's own findings required.**
   Confirmed: the `ngroups`/`nnames` split (§12 item 12) and
   `rx_group_entry` going fixed-literal (§12 item 11), both exactly as
   this document proposed. Beyond confirming what was asked, the panel's
   measurements forced six further hardening changes not anticipated by
   this ASK — `abi` versioning, widened `flags`/`step_budget`, the
   `pattern`/`pattern_len` pair with its escaper obligation, `engine`/
   `engine_why` split, and `rx_group_entry`'s new `slot` column (A-3/
   A-4/A-10/A-11/A-12/A-15/A-16) — all integrated at §5, none of them
   things this ASK originally raised.
8. **RULED (D44.5, 2026-08-14) — `rx_info` GAINS a
   backtrack-frame-capacity member.** `frame_capacity` joins
   `step_budget` (§5), closing the asymmetry this ASK flagged; a further
   member, `subject_ceiling`, joins alongside it for the residual
   unbounded-body class D44.1's frame-ceiling design (engine_m4.md
   §2.5/§4.5) introduces — a second widening this ASK did not anticipate
   but which the same D42.6 two-bounds reasoning covers once the
   residual class exists.

No genuine contradiction between D38 and D39 was found — every tension
encountered (ncap-as-watermark vs. C6's no-watermark rule, §2.1; the group
index's "(empty-ref)" phrasing vs. this document's stronger "(empty,
period)" reading, §5) resolved on inspection rather than blocking. Items
1–5 above are gaps D38/D39 left unfilled, not disagreements between them;
items 6–8 were new questions D43 opened and deferred, now RULED (D44) as
recorded against each.

---

## 14. AMENDMENTS APPLIED (D41/D42/D43, 2026-08-14)

The amendment round owed after D41 and engine_m4.md's merge is DISCHARGED —
every item below is integrated in place (not merely annotated) at the
section cited; this list is now the record of what changed, not a
checklist of what remains. Items 1–6 are the D41/D42 round; item 7 is a
second wave, D43, folded into the same round because it arrived before
[M4.3] closed (same reasoning D37 gives for one announced boundary rather
than staged amendments).

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
7. **The `rx_info` reflection structure and options funnel** — RULED
   (D43.1/D43.2/D43.3): §5 is REWORKED (not merely annotated) from "the
   exported group index" into "the `rx_info` reflection structure —
   F8's group index folds in", carrying the full struct layout, the
   unconditional pattern embed, the customer list (V-A's
   `pcre2_pattern_info` corrected as the second customer, superseding
   this document's earlier `pcre2_substring_number_from_name` framing),
   and two flagged structural additions this document had to derive
   (`rx_group_entry` going fixed-literal; the `ngroups`/`ngroups_named`
   split). §0 gains a third naming family (fixed-literal ABI types,
   previously implicit in §7's table only). §7's table drops the
   freestanding index row and adds `rx_group_entry`/`rx_info`/
   `<prefix>_info`/the three bit constants. §8 is CORRECTED in place —
   the prior "no bitmask surface is being added natively" line from the
   §8-clarification task is struck through and marked SUPERSEDED rather
   than silently rewritten, with the funnel's corrected shape (flags
   word, one-representation rationale, both candidate bit-name spellings)
   written in below it. §11 gains two mechanical items (`rx_info`
   emission, the `pcrec_options` flags-word break) and item 4 is marked
   SUPERSEDED rather than deleted. §12 gains four new items (10–13);
   §13 gains three new ASKs (6–8) for what D43 itself left open.

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

**D43's round did surface one genuine correction** (distinct from the
D41/D42 round, where nothing this document had written turned out wrong):
the §8-clarification task's "no bitmask surface is being added natively"
line was accurate when written and became WRONG the same day when Frank
ruled D43.2 in a later part of the same session. It is struck through and
marked SUPERSEDED in place (§8) rather than removed, so a reader comparing
this document against its own commit history sees the correction rather
than a silent edit. The two D43-round structural additions this document
had to derive on its own — `rx_group_entry` going fixed-literal, and the
`ngroups`/`ngroups_named` split — are flagged as JUDGMENT CALLS at §12
items 11–12 and §13 ASK 7, the same treatment `<prefix>_match_caps`'s
signature got in the prior round.

---

## 15. R21 FIX ROUND APPLIED (D44, 2026-08-14)

A third wave, distinct from D41/D42/D43 above: the [M4.3] D6 panel (R21,
`docs/dev/reviews/2026-08-14-r21-m4-design.md`) reviewed this document
alongside `engine_m4.md` and the two ruled inputs, and every disposition
touching this document is ratified in `docs/dev/decisions.md` D44 and
integrated in place at the section cited, not merely annotated:

1. **The search-entry signature RESHAPES** (A-1, D44.2): `<prefix>_span`
   RETIRES rather than becoming a `ptrdiff_t[2]` typedef; `<prefix>_search`
   takes a `ptrdiff_t (*caps)[2]` parameter directly, `caps[0]` the span,
   `NULL` allowed. §1 is rewritten with the prior typedef design kept as
   SUPERSEDED history, per house style. §11 item 1 gains the three missed
   emit sites (A-7: `emit_dfa.c:468`/`:564`/`:610`, including `%zu`→`%td`).
2. **A-8 — the failure-path contradiction is resolved by DELETION.** §1's
   "`{-1,-1}` written on no match" sentence is removed outright (not
   annotated) because it directly contradicted §3.1/engine §3.4's
   untouched-on-failure rule; one property now stated once.
3. **The ncaps vocabulary is restated end-to-end** (A-5, D44/§2's own
   vocabulary-restatement note): every "`ngroups + 1`" phrasing describing
   `RX_NCAPS`/`ncap`'s completed-match value becomes "`ncaps` (`RX_NCAPS`)"
   — a restatement per D43 addendum 2's three-count split, not a
   re-ruling. C2 is restated as O(1) BY SLOT (D44.3).
4. **`rx_info` is HARDENED to its final layout** (D44.5, closing A-3/
   A-10/A-11/A-12/A-15/A-16 in one pass): `abi` first member, scalars
   grouped, `flags`/`step_budget` widened to fixed-width 64-bit types,
   `engine` split into an enum plus `engine_why`, `pattern`/`pattern_len`
   as a pair with the escaped-C-literal emission obligation STATED (no
   escaper exists today; `emit_pattern_comment`, cited by file and line,
   is not one), and `frame_capacity`/`subject_ceiling` joining
   `step_budget`. `rx_group_entry` is BORN with `slot` (D44.3, A-4),
   closing the pre-V-E OOB read the panel found reachable through
   `--no-captures '(?<g>a)'`.
5. **The ABI-type include guard is made prefix-independent** (A-2,
   `PCREC_RX_ABI_H`, §11 item 2) — the panel MEASURED the composition
   failure the prior guard shape was exposed to; `rx_renderfn` is
   registered into the same fixed-literal family and the same guard
   obligation (A-14), having been present in subst_template_design.md but
   absent from this document's own naming table and emission checklist.
6. **The counter-landing correction lands** (C-1): "[M4.5] wires the
   mechanism, [M4.6] calibrates" replaces every "[M4.6] wires" phrasing in
   this document (§1.1, §3.1, §11 item 9).
7. **A-9 — a new inherited obligation**: `--no-captures` × a
   `$n`-referencing `--replace` template is a compile-time error, recorded
   at §11 item 12 for both [M4.4] and [M4-SUBST] to inherit from one
   freeze line.
8. **`PCREC_CASELESS` is RULED** (D44.8), closing §8/§12 item 13/§13
   ASK 6 in one disposition.
9. **§12/§13 are re-marked**: item 1 of §12 is OVERTAKEN (not answered —
   the question it asked no longer applies under the reshape); items
   10–13 move from open-D43-synthesis to RULED (D44.5/D44.3/D44.8); §13
   items 6–8 move from open ASKs to RULED, each citing its D44 sub-item.

**What resisted clean application:** nothing in this document's own prior
text was found WRONG by the panel (unlike D43's round, which caught one
line the document itself had superseded same-day) — every R21 finding
against this document was either an addition (rx_info hardening, the
`slot` column, the guard fix) or a correction to a SIBLING document's
history-preserving record (the `<prefix>_span` supersession, done via
strikethrough per house style rather than deletion, except A-8's single
sentence, which the disposition explicitly calls for deleting because it
was a live self-contradiction, not a historical claim worth preserving).
