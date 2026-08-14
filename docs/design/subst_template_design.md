# Compiled substitution — the template compiler design (M4-SUBST, phase 1)

**Status: PROPOSED, §9 now fully RULED (D38, 2026-08-14).** `docs/dev/decisions.md`
D38 rules all fourteen of §9's questions (and §10's summary asks) —
outcomes appended in place below, marked **RULED (D38, 2026-08-14)**.
The design prose itself is UNCHANGED by this pass; only the rulings are
added. It is the design note the `[M4-SUBST]` row owes *before M4's
match-API freezes*, and its §2 is the half that has a deadline: the
capture-offset contract stated there is an **input** to that freeze, not a
consumer of it. Everything else can move later; §2 cannot.

Nothing here is implementation. No code was written for the template
compiler; the only code this note added is a measurement probe
(`tests/probes/probe_subst.c`).

**AMENDED 2026-08-14** against `design_callout_abi.md` (Frank's R-a/R-b/R-c
rulings, committed at `bfc07b0`), which lands after this note's first draft
and whose **F3** and **F6** bind it. The capture-offset contract adopts
`rx_ctx.caps` — `ptrdiff_t[2]` pairs, `{-1,-1}` = unset — instead of the
draft's `size_t` spans (§2.4), and the callback template segments consume
`rx_ctx` verbatim instead of the draft's bespoke signature (§7.2). Both
amendments improved the design rather than merely complying with it; §2.4
and §7.2 also carry three things the freeze should see, raised as questions
12–14. Amended text is marked **AMENDED 2026-08-14** in place; the superseded
draft is in git history, not edited away.

## How claims in this document are marked

The `[M4-SUBST]` row is a ratified scope statement with Frank's own
observations recorded in it. This note restates some of that and proposes a
great deal more, and the two must not blur together.

| mark | meaning |
|---|---|
| **[RATIFIED]** | restates the `[M4-SUBST]` plan row, or another ratified row/decision. Not open. |
| **[MEASURED]** | a fact about PCRE2 measured on this box, with the cell cited. Not an opinion, and not read from documentation. |
| **[PROPOSED]** | this note's design. Awaiting review and Frank's ruling. |
| **[OPEN]** | a question this note deliberately does not answer. Collected in §9. |

### Measurement provenance

Every **[MEASURED]** claim comes from `tests/probes/probe_subst.c`, archived
at `docs/measurements/probe_subst.txt` (D35), run against **libpcre2 10.46
2025-08-27** at repo `46862ef`. Section numbers below like *(probe §7)* index
that report.

The probe follows the method `tests/probes/CLAUDE.md` closes with: twelve
predictions (P1–P12) are stated in its header **before** the first run, and
the report shows which survived. **Three were refuted, and two of the three
changed this design** — they are called out where they land (§2.5, §3.3,
§5.4). Because this box has the libpcre2 runtime but no `pcre2.h`, the
`PCRE2_SUBSTITUTE_*` bit values are hand-written from memory of the
documentation and then **confirmed by effect** before use (probe §0), the
precedent `probe_uprops.c` set for `PCRE2_EXTRA_BAD_ESCAPE_IS_LITERAL`. All
five confirmable bits confirmed.

---

## 1. What this note is, and why it can precede M4

**[RATIFIED]** The row's scope: *the `pcre2_substitute` capability as an AOT
artifact — pattern AND replacement template compiled together into one
emitted C function (match + splice), first/global modes, caller-buffer
zero-allocation mode plus an output-sizing mode.*

**[RATIFIED]** The sequencing licence, in Frank's words: *the template
compiler is almost completely independent of the matcher... it consumes only
the capture-offset CONTRACT, so its design note can precede M4 even though
end-to-end substitution is capture-gated.*

That observation is stronger than it looks, and this note leans on it hard
enough to be worth restating precisely. A template compiler is a **pure
function of two inputs**: the template text, and the *shape* of the capture
data — how many groups exist, what their names are, how an offset pair is
represented, what an unset group looks like. It never needs a matcher. It
never needs to know what the pattern matches. It needs to know what the
pattern *captures*, which is a parse-time property.

Two facts measured in this repo make the independence concrete rather than
aspirational:

- **[MEASURED]** pcrec **already** computes the group count at compile time
  and already exposes it: `pcrec --count-groups` returns 0/1/2/1/2 for
  `abc`/`(a)`/`(a)(b)`/`(?:a)(b)`/`(a)|(b)`. The compile-time bounds check in
  §4 — the AOT win the row names — is buildable against today's parser, with
  no captures, no VM and no M4.
- **[MEASURED]** the whole-match span is *already* the generated contract:
  `rx_search` fills `rx_span {size_t start, end;}`. `$0` therefore needs
  nothing that does not exist. As §8.3 works out, this makes the entire
  global-mode splice geometry — the fiddliest part of the whole feature —
  testable **today**, on 0-group patterns.

So the capture-gated part of M4-SUBST is exactly `$1`..`$n` and `${name}`,
and nothing else.

### 1.1 Scope boundaries

Not this note's business, cited rather than solved: `\G` semantics
(**[DD-4]**), the engine choice and capture prefilter (**[DD-7]**,
**[M4.0]**), UTF (**[M5]**, **[DD-12]**), generated-API versioning
(**[DD-3]**), and the option-flag dispositions (**[PC-5]** — whose row
already routes `PCRE2_SUBSTITUTE_*` here and classifies
`NOTEMPTY`/`NOTEMPTY_ATSTART` as `EMITTED-LOOP`, "*subsumed by generated
iteration... pcrec emits the loop itself at DD-4/M4-SUBST*". §6 is that
loop).

---

## 2. The capture-offset contract — what the template side REQUIRES

**This is the section with the deadline.** It is written as requirements on
M4's match API, not as a description of one. Each is stated so that M4 can
satisfy it in whatever way suits the engine, and each says *why the template
compiler needs it* — a requirement without a consumer is a requirement to
delete.

### 2.1 The requirements

**C1 — The capturing-group COUNT is a compile-time constant.**
The template compiler must know, before emitting anything, how many
capturing groups the pattern has. Without this there is no compile-time
bounds check and the AOT win in §4 evaporates. **[MEASURED]** already
satisfied by today's parser (`--count-groups`); the requirement on M4 is only
that it not become a run-time property.

**C2 — Captures are addressable by NUMBER, as a flat indexed sequence.**
The template compiler emits, for `$k`, a read of entry `k`. It requires
random access by a compile-time-constant index and nothing else — no
iteration, no search, no cursor. Any representation with `O(1)` indexed
access satisfies this; a flat array of pairs is the obvious one.

**C3 — Index 0 is the WHOLE MATCH, and exists even when the pattern has zero
groups.** `$0` is core (§3.1), so a zero-group pattern must still expose the
overall span. **[MEASURED]** this is PCRE2's numbering (probe §3: `/b+/` with
`[$0]` yields `a[bb]c`) and it is already pcrec's shape — `rx_span` *is* pair
0. The requirement is that M4 not restructure captures into a groups-only
array indexed from 1 with the overall match kept somewhere else.

**C4 — Offsets are BYTE offsets into the original subject, half-open
`[start, end)`, as a two-element pair per group.** The splice is a copy out
of the subject buffer; it needs byte positions in that buffer. Not code-point
indices, not pointers, not lengths. This matches PCRE2, which reports byte
offsets even under UTF. **[DD-12]** already rules that code points exist only
at regex-compile time between parse and lowering, so this requirement is a
restatement of the ratified UTF architecture, not a new constraint on it.
Under **[M5]** the template compiler stays entirely encoding-blind: it copies
byte ranges the matcher identified.

**AMENDED 2026-08-14** (callout-ABI ruling, `design_callout_abi.md` F3): the
element type is **`ptrdiff_t`**, not `size_t`, and the pair is
`ptrdiff_t[2]`. §2.4 works through the adoption and what it costs.

**C5 — There is a DISTINGUISHED UNSET value, present in BOTH slots of an
unset pair, and it is a NAMED constant in the generated header.**
A group that exists but did not participate in this match is the one case the
compile-time bounds check cannot remove (§2.3), so the emitted splice must be
able to test for it at run time. **[MEASURED]** PCRE2 uses
`~(PCRE2_SIZE)0` — `18446744073709551615` here — in both slots (probe §2).

**AMENDED 2026-08-14**: the sentinel is **`{-1, -1}`** per the callout ABI,
which under `ptrdiff_t` is the same *idea* as PCRE2's all-ones and a strictly
better one to test — `caps[k][0] < 0` is one signed comparison, where the
`size_t` form needs a comparison against a named constant that a caller can
get wrong. The named constant is still required (`RX_UNSET`), because a
caller writing its own loop must not hard-code either spelling.

**C6 — EVERY pair `0..ngroups` is written on every successful match.**
The emitted splice reads pair `k` unconditionally; if pairs above some
watermark could hold stale or uninitialised data, every read would need a
guard, and the guard would need a watermark the template compiler does not
have. This is the requirement most at risk of being lost, because PCRE2's own
API does *not* obviously promise it: `pcre2_match` returns "highest set pair
+ 1", which reads like a licence to leave the rest alone. **[MEASURED]** it
nonetheless writes them: with the ovector poisoned to `0xDEAD` first,
`/(a)(b)?(c)?/` on `"a"` returns `rc=2` and pairs 2 and 3 come back
`PCRE2_UNSET`, not poison (probe §2). So this requirement is *agreement* with
PCRE2 rather than divergence — but it must be written down, because it is
agreement with PCRE2's behaviour and not with the shape of its return value.

**C7 — The span array is CALLER-OWNED, fixed-size, and its size is a
compile-time constant the generated header exposes.**
No allocation anywhere in the generated code — the positioning note's element
2 (embedded / no-library: "*no malloc/errno/locale in generated code*") and
TS-1's all-const-tables rule are not negotiable for this feature. The caller
must be able to write `ptrdiff_t caps[RX_NCAPS][2];` on the stack, which
requires the count as a macro, not as a function return.

**C8 — The spans are STABLE for the duration of one splice.**
In global mode the emitted loop alternates *match* and *splice*; the splice
for match *k* reads spans the matcher wrote. The contract must state whether
the matcher may overwrite the span array during a subsequent search (it may —
the loop simply completes each splice first) so that the loop's ordering is a
documented consequence rather than an accident. **[OPEN]** only in the sense
that M4 must *say*; either answer is implementable.
**RULED (D38, 2026-08-14):** §2's C1–C11 are accepted as requirements on
M4's match API (§10), carrying this note's stated answer forward as the
accepted contract — the matcher may overwrite the span array between
splices, and the loop completing each splice first is the documented
consequence, not an accident.

**C9 — Group NUMBERING is PCRE2's: left-to-right by opening parenthesis of a
capturing group; non-capturing groups do not consume a number.**
`$n` is resolved against this at compile time, so the template compiler and
the matcher must agree on it exactly — a divergence here is a silent
miscompile, the worst outcome in the D26 tier table (tier 1). **[MEASURED]**
`(?:a)(b)` has capture count 1 in both pcrec (`--count-groups`) and libpcre2
(`PCRE2_INFO_CAPTURECOUNT`, probe §1).

**C10 — NAME→NUMBER is a COMPILE-TIME table, not a run-time lookup surface.**
`${name}` resolves to a number during compilation and the emitted code
contains no names at all. The requirement on M4/`named-groups` is therefore
weak and cheap: expose the mapping to the compiler. It explicitly does *not*
require the generated artifact to carry a name table, a string comparison, or
a lookup function. **[MEASURED]** this is gated on module `named-groups`,
which does not exist yet — `pcrec --count-groups '(?<g>a)(b)'` fails with
*"(?<...) requires module 'named-groups'"*. So `${name}` is gated on that
module, **not** on M4, and it tiers separately for that reason (§3.1).

**C11 — Success/failure is a return value, not an error object.**
The splice needs to know only whether a match occurred. No error codes, no
match-data object, no diagnostic buffer.

### 2.2 What the template side explicitly does NOT require

Stated because a match API designed to serve substitution could easily
over-deliver, and each of these would be cost with no consumer:

- **No ovector sizing negotiation.** PCRE2 has it because a caller compiles a
  pattern it did not write; pcrec knows the group count at compile time (C1).
- **No match-data object, no allocation, no lifecycle.** (C7.)
- **No run-time "does group N exist" query.** That is §4's compile-time
  check.
- **No run-time name lookup** (C10) and no `pcre2_substring_*` family.
- **No partial-match or window states.** Streaming substitution is **[M3]**'s
  business if it ever is anyone's; this note is buffer-to-buffer.
- **No callout or callback context threading from the matcher.** §7's
  template callbacks are invoked by the *splice*, not by the matcher, and
  need nothing from the match API.

### 2.3 The one thing compile-time checking does NOT remove

Worth stating plainly because it is easy to over-claim the AOT win.
"Group 2 exists in this pattern" is decidable at compile time. "Group 2
participated in *this* match" is not — it is a property of the subject.
**[MEASURED]** the distinction is live: `/(a)(b)?/` on `"a"` leaves pair 2
`UNSET` (probe §11), and `/(a)|(b)/` on `"b"` leaves pair 1 `UNSET` (probe
§2).

So §4's check eliminates PCRE2's `-49 (unknown substring)` class entirely,
and leaves the *unset* case as a genuine run-time condition that the emitted
code must render somehow. What it renders is §9's question 3, and it is the
most consequential ruling in this note.

### 2.4 Reconciliation with the callout ABI (F3, F6) — AMENDED 2026-08-14

`docs/design/design_callout_abi.md` (manager proposal, incorporating Frank's
same-day rulings R-a/R-b/R-c) aligns the matcher and callout interfaces on
one context struct, and its **F3** couples that struct's capture field to
this section: *"the capture representation in `rx_ctx.caps` must BE the match
API's capture-offset contract (one representation, not a conversion)."*

```c
typedef struct rx_ctx {
    const char     *subject;
    size_t          len;
    size_t          pos;
    size_t          ncap;       /* capture slots known so far */
    const ptrdiff_t (*caps)[2]; /* [start,end) pairs; -1,-1 = unset */
} rx_ctx;
```

**[PROPOSED]** this note **adopts** `rx_ctx.caps` as the capture-offset
contract. F3 is right that two representations with a conversion between them
would be the worse outcome, and the fit is good: `const ptrdiff_t (*)[2]` is
precisely C2's "flat indexed sequence of pairs" and C4's half-open byte
ranges, expressed as a type rather than as a convention. C1, C2, C3, C7, C9,
C10 and C11 are unaffected.

Four consequences the freeze should see, because adoption is not free and
three of these are not visible from the callout side alone.

**(a) It changes an ALREADY-EMITTED type.** `src/gen/emit_dfa.c:106` emits
`typedef struct { size_t start, end; } <prefix>_span;` today, `rx_search`
takes a `rx_span *`, and `tests/harness/driver.c` consumes it. So "one
representation, no conversion" cannot be satisfied by adding `rx_ctx`
alongside `rx_span` — it requires that `rx_span` either become the pair type
or go away. That is a breaking change to a shipped generated contract, which
is **[DD-3]**'s territory (generated-API versioning) and should be recorded
as a cost of F3 rather than discovered at implementation time.
**[PROPOSED]** the cheapest reconciliation is that the whole-match span
becomes `caps[0]` and `rx_search` keeps a compatibility signature; but this
note does not own that call and flags it as §9 question 12.

**(b) `size_t` → `ptrdiff_t` halves the representable subject length**, from
`SIZE_MAX` to `PTRDIFF_MAX`. On any target pcrec plausibly serves this is
irrelevant (2^63−1 bytes here), and the gain — one signed test for unset, and
fail/empty distinctness for the same reason F1 gives for the return value —
is worth it. Recorded so the freeze is informed rather than surprised.

**(c) `const char *subject` should almost certainly be `const unsigned char
*`.** This is a defect report against the ABI proposal, not a substitution
question, but this note is the second consumer and so is where it surfaced.
Plain `char` has implementation-defined signedness; the entire existing
emitter uses `const unsigned char *` for subject bytes precisely because it
indexes 256-entry class tables with them (`rx_ftr[st * 5 + rx_fcls[s[pos++]]]`
in the emitted scan loop), and a signed `char` makes that a negative index on
any byte ≥ 0x80. `PCREC_ENC_ASCII` is documented as *"byte semantics, 8-bit
clean"*, so bytes ≥ 0x80 are ordinary subjects, not an edge case. The splice
copies bytes and would survive either choice; the matcher on the other side
of the same struct would not.

**(d) `ncap` is a WATERMARK, and C6 said watermarks are the thing to avoid.**
The tension is real but resolves cleanly, and the resolution is worth writing
into the freeze because each side is right about its own direction:

- *Callout direction (mid-match).* Captures genuinely are incomplete — that
  is the whole content of R-b's "captures **thus far**" — so `ncap` is
  load-bearing and correct there. A callout must not read `caps[k]` for
  `k >= ncap`, and `caps[0]`'s end is not yet meaningful at all, since the
  overall match has not finished.
- *Substitution direction (match complete).* The splice runs only after a
  match succeeds, and C6 asks that at that point **every** pair `0..ngroups`
  be written, with non-participating groups holding `{-1,-1}` rather than
  being merely "beyond the watermark". **[MEASURED]** this is what libpcre2
  does at match completion, the poison cell in §2.5 notwithstanding its
  return value.

**[PROPOSED]** therefore: `ncap` is part of the struct, and the *contract on
a completed match* is `ncap == ngroups + 1` with all pairs written. The
emitted splice then needs no watermark logic and no guard per reference,
which is what C6 was actually asking for — C6 is a statement about the
completed-match contract, not a request to delete a field the callout
direction needs.

### 2.5 Refuted prediction that changed this section

**P11 predicted** that an unset pair reads as `PCRE2_UNSET` in both slots —
confirmed. **P8's neighbour did not survive**: the note's first draft assumed
pairs above `pcre2_match`'s return value were undefined, and would have
written C6 as a *divergence from PCRE2* with a justification paragraph. The
poison cell (probe §2) refuted that, so C6 is now stated as agreement. The
requirement did not change; the honesty of its rationale did.

---

## 3. The template language, tiered under D18

**[RATIFIED]** *Tier the template language: core `$n`/`${name}`/literal
escapes first; PCRE2_SUBSTITUTE_EXTENDED forms (`\u` `\l` case forcing,
`${n:-default}`, `${n:+yes:no}`) earn their rows separately under D18's
earn-its-axis discipline.*

### 3.0 The tiering mechanism: a run-time option becomes a compile-time module

**[PROPOSED]** and this is the note's main structural idea.

In PCRE2, `PCRE2_SUBSTITUTE_EXTENDED` is a bit passed at substitute time; one
compiled pattern serves both languages, and which template dialect is in
force is a property of the *call*. Under D18 that is precisely the shape
pcrec compiles away: the template dialect is fixed when the template is
compiled, so there is no bit, no branch, and no dialect at run time.

The natural home for the tier is therefore **the existing module/feature-set
gate** (D37, `--features`), not a new option. **[PROPOSED]** three module
names, in the one namespace SR-10 requires:

| module | contents | status |
|---|---|---|
| `subst` | the core template language (§3.1) | the phase-1 build |
| `subst-extended` | PCRE2's `SUBSTITUTE_EXTENDED` forms (§3.3) | earns its own row |
| `subst-pcrec` | everything beyond PCRE2's surface (§7) | earns its own row |

Three things fall out for free, which is the argument for the choice:

1. A template using an un-enabled form fails with the project's existing
   diagnostic shape — *"requires module 'subst-extended'"* — which D26 tier 3
   says discharges the diagnostic obligation **in full**. No PCRE2 error
   wording is reproduced anywhere in this design.
2. D37's artifact stamp already records the enabled set in the emitted `.c`,
   so what dialect a generated substituter was built with is self-evident
   from the file.
3. SR-10's single-namespace rule applies to these names for free, because
   they are members of the same MODULES namespace as everything else.

### 3.1 Core tier (module `subst`)

**[PROPOSED]**, and every row is **[MEASURED]** to be core in PCRE2 (probe
§3) unless noted:

| form | meaning |
|---|---|
| `$0`, `${0}` | the whole match |
| `$n`, `${n}` | capturing group *n*, resolved and bounds-checked at compile time (§4) |
| `${name}` | named group; **gated additionally on module `named-groups`** (C10) |
| `$$` | a literal `$` |
| any other byte | literal, copied through |

Two deliberate consequences:

- **A backslash is an ordinary literal byte in the core tier.** **[MEASURED]**
  this is PCRE2's behaviour, not a simplification: without `EXTENDED`,
  `x\ny` produces the five bytes `x\ny` — backslash retained — while with
  `EXTENDED` it produces the four bytes `x`, `0x0A`, `y` (probe §4). So
  "literal escapes" in the ratified row's phrasing means `$$` and nothing
  more; `\n` belongs to §3.3. Getting this backwards would make every core
  template with a Windows path in it wrong.
- `${name}` sits in the core *language* tier but is gated on a different
  module, so the first build ships `$n` working and `${name}` refusing
  cleanly. That is the normal module shape, not an exception.

### 3.2 Measured grammar corners the core tier must reproduce (tier 1)

These are **[MEASURED]** and they are all in the D26 *tier 1* band — what a
template *produces* is core semantics, and a divergence is a bug. They are
listed because each is a plausible thing to get wrong by writing the obvious
parser (probe §3, §12):

1. **`$name` bare (no braces) is real, and it is GREEDY.** `$g` followed by
   `x` reads the name `gx`, and errors — `[$gx]` on `/(?<g>b)/` gives
   `-49 (unknown substring)`, it does not render group `g` followed by a
   literal `x`. Likewise `$g_`, `$g1`.
2. **The same greed applies to digits.** `$12` on a one-group pattern is a
   reference to group *twelve* and errors; it is not `$1` followed by `2`.
   `${1}2` is the way to write the latter, and works.
3. **A bare `$` before a name character is a reference, so its failure mode is
   "unknown substring", not "bad syntax."** `$x` gives `-49`, whereas `$` at
   end of template and `$` before a space give `-35 (invalid replacement
   string)`. Two different error classes an implementation could easily merge.
4. `$$` yields one `$`.

**[PROPOSED]** pcrec reproduces items 1–4's *semantics* exactly (tier 1) and
says nothing about PCRE2's error numbers (tier 3). §9 question 2 asks whether
the bare `$name` form should be supported at all, given that item 1 makes it
an error magnet and pcrec — unlike PCRE2 — would catch it at build time.

### 3.3 Deferred tier (module `subst-extended`)

**[MEASURED]** every form below requires `PCRE2_SUBSTITUTE_EXTENDED` and is
either literal or an error without it (probe §4, §6):

| form | measured behaviour |
|---|---|
| `\n`, `\x41`, other C-style escapes | literal (backslash retained) in core; interpreted under EXTENDED. `\q` under EXTENDED is `-57 (bad escape sequence)` |
| `\$` | a literal `$` under EXTENDED; in core the backslash is literal and `$1` still parses as a reference |
| `\u`, `\l` | one-shot case forcing of the next output character |
| `\U`, `\L`, `\E` | case-forcing runs. `\E` with no open run is a harmless no-op |
| `${n:-default}` | default when the group is unset. **In core this is `-58 (expected closing curly bracket)`** — the `:` is simply not part of the core brace grammar |
| `${n:+yes:no}` | set/unset selector; one-armed `${n:+yes}` is also valid |

**Three measured facts about case forcing that a naive design gets wrong,**
and they are why this tier genuinely earns a separate row rather than being
"a small addition" (probe §12):

- **Case forcing is a pending operator on the OUTPUT BYTE STREAM, not a
  transform applied to the next template item.** `\u$1z` where group 1 is
  unset (with `UNSET_EMPTY`) produces `Z` — the pending force skipped straight
  past the empty group and landed on the literal `z`. Any implementation that
  applies `\u` to "the next segment" is wrong on exactly this cell.
- **A one-shot force CANCELS an active run rather than nesting inside it.**
  `\U$1\l$1` on `/(bc)/` produces `BCbc`, not `BCbC`: the `\l` ended the `\U`
  run. Doubled `\u\u$1` gives `Bc` — the second replaces the first, it does
  not force two characters.
- **A run spans `$n` boundaries and literal text alike**: `\U$1-$2z` gives
  `B-CZ`.

**[MEASURED]** one option-precedence fact worth recording for **[PC-5]**:
`SUBSTITUTE_LITERAL` **beats** `SUBSTITUTE_EXTENDED` — with both set, the
template is emitted raw (`\u$0` comes out as the five bytes `\u$0`). Under
D18 `LITERAL` is not an option at all in pcrec; it is the degenerate template
compiler (a template with no `$` in it), which needs no code.

### 3.4 Why this tiering, in D18's terms

D18's rule is that a dimension is an axis only when its requested set has two
or more elements, and that a fixed choice is compiled away. A template's
dialect is fixed the moment the template is written down: no caller ever
needs one emitted function to serve both dialects, because the template is
baked in. So the dialect is a **singleton dimension by construction** — it
never becomes a generation axis, and it never appears in a signature. That is
a stronger statement than "we tier it for effort reasons": it is why the
tiering costs nothing at run time and can never grow a dispatch.

---

## 4. Compile-time resolution and the error surface

**[RATIFIED]** *`$n`/`${name}` references are resolved and BOUNDS-CHECKED AT
COMPILE TIME against the pattern's own group count — a template naming a
group that does not exist is a compile error, where PCRE2 discovers it at
substitute time.*

### 4.1 What is checked, and what PCRE2 does instead

**[MEASURED]** PCRE2's substitute-time failures for this class, which pcrec
converts into build failures (probe §5):

| template against `/(b)/` | PCRE2, at substitute time | pcrec **[PROPOSED]** |
|---|---|---|
| `[$2]` | `-49 (unknown substring)` | compile error |
| `${nosuch}` on `/(?<g>b)/` | `-49 (unknown substring)` | compile error |
| `[$2]` + `UNKNOWN_UNSET` | `-55 (requested value is not set)` | *n/a — the option has no pcrec analogue; the reference is simply invalid* |

The AOT win is exact and worth naming precisely: **the entire "unknown
substring" error class ceases to exist at run time.** Not "is less likely" —
ceases to exist, because a template that could produce it does not compile.
This deletes an error path from the generated code and a failure mode from
every deployment, which is the embedded-niche argument (positioning element
2) in miniature. **[MEASURED]** it also removes PCRE2's `UNKNOWN_UNSET`
option along with it: that option exists only to soften an error pcrec has
already made impossible.

### 4.2 The compile-time error surface

**[PROPOSED]**, in the project's existing style. Every one of these is a
`pcrec_error` with a message and a position; none reproduces a PCRE2 error
number or wording (D26 tier 3):

| condition | shape of the diagnostic |
|---|---|
| `$n` with *n* > group count | `template group $2 does not exist: pattern 'X' has 1 capturing group` |
| `${name}` not in the pattern's name table | `template group ${foo} does not exist` — **[PROPOSED]** and it should list the names that do exist, since they are all known at compile time |
| `${` never closed | `unterminated ${ in template` |
| `$` at end of template | `template ends with '$'` |
| `$` before a byte that starts no reference | `'$' must be followed by a group reference or '$'` |
| a `subst-extended` form with that module disabled | `requires module 'subst-extended'` — the existing gate diagnostic, unchanged |

Two properties this surface should have, both **[PROPOSED]**:

- **Naming what does exist.** A compile-time checker knows the group count
  and the name table; a diagnostic that says "does not exist" without saying
  what does is throwing away information the run-time checker never had. This
  is the whole reason the check is worth moving to compile time.
- **The error is attributed to the TEMPLATE, not the pattern**, and this
  collides with the existing API. `pcrec_error.pos` is documented as *"byte
  offset into the pattern, when applicable"*. With two input strings, `pos`
  becomes ambiguous, and a caller pointing a caret at the wrong string is a
  worse experience than no caret. This is **[OPEN]** — §9 question 8 — and it
  is an API question that must be answered before M4 freezes, because it
  changes `lib/pcrec.h`.
  **RULED (D38, 2026-08-14):** see §9 question 8 — `pcrec_error` gains a
  WHICH-INPUT tag (an enum: pattern vs. template) beside `pos`.

### 4.3 A tension in the ratified row, recorded

The row says a template naming a nonexistent group *is a compile error*. That
is unambiguous for `$99`. It is **not** unambiguous for the *unset* case
(§2.3), which the row does not mention and which is not decidable at compile
time. A reader could take "bounds-checked at compile time" to mean the
generated code has no unset handling at all, which is not implementable.
§9 question 3 puts the choice to Frank rather than resolving it here.

---

## 5. The emitted artifact shape

**[RATIFIED]** *pattern AND replacement template compiled together into one
emitted C function (match + splice), first/global modes, caller-buffer
zero-allocation mode plus an output-sizing mode.*

### 5.1 Style constraints inherited

From today's emitter (`src/gen/CLAUDE.md`, and the sample below) — these are
observed facts about the tree, not proposals: symbols carry the user's prefix
(default `rx`); the subject is `const unsigned char *` with a `size_t`
length; spans are `size_t` pairs, end-exclusive; the file-scope surface is
one typedef plus per-entry-point declarations, everything else
function-local `static const` (TS-1); the code must stay warning-clean under
`-Wall -Wextra -Werror`; and the emitted header is `#include <stddef.h>` and
nothing else. Today's whole public surface for a pattern is:

```c
typedef struct { size_t start, end; } rx_span;
int rx_search(const unsigned char *s, size_t n, size_t startpos, rx_span *m);
```

### 5.2 Proposed generated surface

**[PROPOSED]**, for `pcrec -p rx --replace '<$1>' -o out.c '(a+)b'`:

```c
/* Generated by pcrec. Pattern: (a+)b */
/* Replacement: <$1> */
/* Feature set: <D37 stamp, unchanged; 'subst' appears in its module list> */

/* The capture-offset contract, shared verbatim with the callout ABI (F3). */
typedef struct rx_ctx rx_ctx;         /* see design_callout_abi.md §1 */

#define RX_NCAPS 2                    /* $0..$1 — the caps[] element count */
#define RX_UNSET ((ptrdiff_t)-1)      /* C5: an unset capture, both slots */

/* Substitution outcome. Non-negative = number of substitutions performed. */
#define RX_SUBST_NOSPACE (-1)

/* Substitute into a caller-owned buffer. On entry *outlen is the capacity
 * of out; on return it is the number of bytes produced. Returns the number
 * of substitutions (0 = no match, subject copied through), or
 * RX_SUBST_NOSPACE with *outlen set to the capacity that would suffice.
 * out may be NULL, in which case nothing is written and *outlen receives
 * the required capacity (sizing mode). Allocates nothing, ever. */
int rx_subst(const unsigned char *s, size_t n,
             unsigned char *out, size_t *outlen);
```

Notes on each choice, all **[PROPOSED]**:

- **One function, both modes.** PCRE2 splits sizing off into
  `PCRE2_SUBSTITUTE_OVERFLOW_LENGTH`, an option you must remember to pass.
  **[MEASURED]** without it, an undersized buffer returns `-48` and sets the
  length to `PCRE2_UNSET` — the caller learns nothing (probe §8). Making the
  required capacity *always* reported costs one `size_t` store on a path that
  is already failing, and removes an option. `out == NULL` for a pure
  pre-flight is the second half of the same idea.
- **Count as the return value** matches PCRE2 (**[MEASURED]** `rc` is the
  substitution count; a no-match returns `0` with the subject copied through
  — probe §9) and it is what a caller actually wants to branch on.
- **No `startpos`.** `rx_search` has one because a caller drives its own
  loop; substitution's loop is emitted (§6), so exposing a start offset would
  invite callers to hand-roll the very loop this feature exists to remove.
  **[OPEN]**-adjacent: if `\G` (**[DD-4]**) or `PCRE2_SUBSTITUTE_MATCHED` ever
  need it, it is an additive parameter on a second entry point.

### 5.3 first / global as a GENERATION AXIS, not a flag

**[PROPOSED]** and this is the D18-shaped part. First-match and global are
*not* a run-time parameter. They are a requested set, exactly as D18
describes, and the emitted result is one entry point per requested element,
following **[OS-0]**'s named-entry-point rule (*"emit named per-combination
entry points... so a statically-known caller pays no dispatch at all"*):

| requested | emitted |
|---|---|
| `{first}` | `rx_subst` |
| `{global}` | `rx_subst` (the global one; the name is the singleton's) |
| `{first, global}` | `rx_subst_first` and `rx_subst_all`, plus D20's selector if a finder is ever built |

The two functions genuinely differ in code, not in a branch: the first-match
form has no loop, no carried position, and none of §6's empty-match
machinery. A run-time flag would put the entire global-mode state machine
into the first-match path and pay for it on every call — the exact trade D18
forbids.

### 5.4 The buffer contract, and a refuted prediction

**[MEASURED]**, and P8/P9 are where the probe was most useful, because
PCRE2's length contract is *asymmetric* in a way that is easy to reproduce
wrongly (probe §8):

- On **success**, `*outlengthptr` is the produced length **excluding** the
  terminating NUL (3 for `"aXY"`), and the buffer *is* NUL-terminated.
- On **overflow with `OVERFLOW_LENGTH`**, `*outlengthptr` is **4** for the
  same 3 bytes — it **includes** room for the NUL.
- A buffer of exactly the text length (3) **fails** with `-48`: the NUL must
  fit. Capacity 4 succeeds.

So the same output variable means two different things depending on the
return value. **[PROPOSED]** pcrec does not reproduce that. The proposal is
that `*outlen` means *bytes produced* on success and *capacity required* on
`RX_SUBST_NOSPACE`, with **no NUL termination and no NUL budget** — the
length is the contract, uniformly, exactly as `rx_span` is the contract for
`rx_search`. Reasons: the subject may contain NULs (pcrec is 8-bit clean by
`PCREC_ENC_ASCII`'s definition), so a NUL terminator is not a reliable
delimiter anyway; and a caller who wants one can append it, knowing the
length. This is a deliberate divergence from PCRE2 in a place D26 does not
protect — it is API shape, not "what a pattern matches" — but it *is* a
divergence and it is §9 question 4.
**RULED (D38, 2026-08-14):** see §9 question 4 — length-only, as
proposed here, with no NUL termination and no NUL budget.

### 5.5 One emitted file, several templates

**[PROPOSED]** nothing in this design ties one pattern to one template. The
splice code is per-template; the matcher is per-pattern and shared. Emitting
`rx_subst_redact` and `rx_subst_expand` over one matcher is the same
named-entry-point mechanism as §5.3 and needs no new machinery. This is the
natural hook for **[V-E]**'s manifest (a template becomes a field of a named
entry) and is noted so the design does not accidentally preclude it.

---

## 6. Global-mode semantics

The emitted loop. **[PC-5]** already classifies `PCRE2_NOTEMPTY` /
`NOTEMPTY_ATSTART` as `EMITTED-LOOP` — *"these exist because PCRE2 callers
hand-roll global-match loops around a raw single-match primitive; pcrec emits
the loop itself"* — so this section is that row's design half.

### 6.1 The measured rules

**[MEASURED]** (probe §7). The skeleton is unsurprising: copy subject text
between matches, splice at each match, copy the tail. The empty-match rule is
where implementations go wrong, and the measurement settles it:

```
a*  on "bab", global, replacement [$0]   ->  []b[a][]b[]     (4 substitutions)
a*  on "aab", global, replacement [$0]   ->  [aa][]b[]       (3 substitutions)
(empty pattern) on "abc", replacement -  ->  -a-b-c-         (4)
(?=b) on "abc", replacement -            ->  a-bc            (1)
\b  on "ab cd", replacement -            ->  -ab- -cd-       (4)
a*  on "bab", NOT global                 ->  []bab           (1)
```

The rule these are consistent with, and the one this note **refines a
prediction into** (P10 was stated too strongly):

> An empty match is suppressed **only at the position where an empty match
> was just produced** — not at the end of a non-empty match. Concretely: after
> producing a match, the next search starts at that match's end. If the
> *previous* match was empty, that search is retried "not-empty-at-start and
> anchored"; on failure, one character is copied through and the position
> advances by one.

The discriminating evidence is `"aab"` → `[aa][]b[]`: the `[]` sits at
offset 2, immediately after the non-empty `[aa]` ended at 2. A design that
suppresses empty matches at the previous match's end — the intuitive reading,
and P10's — produces `[aa]b[]` and is wrong by one substitution. Trace of
`"bab"` under the correct rule: empty at 0; retry at 0 fails; copy `b`,
advance to 1; match `a` at [1,2); search from 2 finds empty at 2 (allowed —
previous match was non-empty); retry at 2 fails; copy `b`, advance to 3;
empty at 3. Four substitutions, `[]b[a][]b[]`. ✓

### 6.2 Cited, not solved

- **`\G` (**[DD-4]**).** `\G` anchors at the end of the previous match, which
  is exactly the position this loop carries. The two features therefore share
  one piece of state, and whichever lands second must not introduce a second
  copy of it. **[DD-4]** owns the semantics; this note owns only the
  observation that the state is common, and flags **[DD-7]**'s related note
  that `nfa_wrap_unanchored` bakes in the self-loop with no toggle.
- **`^` under global iteration.** `lib/pcrec.h` documents that *"`^` anchors
  to absolute offset 0 regardless of startpos"*. A global substitution over a
  `^`-anchored pattern must therefore not simply re-enter `rx_search` with a
  larger `startpos` and expect PCRE2's behaviour. **[PROPOSED]** the emitted
  loop for an anchored pattern is the degenerate one (at most one match),
  which is correct and free — but it must be *decided* at generation time
  from the pattern's anchoring, not discovered at run time.
- **Advancement under UTF (**[M5]**).** "advance by one character" replaces
  "advance by one byte". Per **[DD-12]** the matcher stays byte-wise, so this
  is a step-width question in the emitted loop, not a representation change.
  Deferred entirely.
- **Newline conventions (**[DD-11]**).** PCRE2's global loop has a
  CRLF-specific rule when advancing past an empty match. The probe does not
  exercise it, deliberately (§7's `$` cell shows only the single match on
  `"a\nb"`): **[DD-11]** owns `NEWLINE`/`BSR`, and a second answer invented
  here would be a second description of one fact.

---

## 7. Beyond PCRE2 — the pcrec-extended tier

**[RATIFIED]**, Frank 2026-08-13: *"this might be an area where we provide
more capability than pcre2"* — richer shell-style transforms and **C function
callbacks as template segments**, reusing M4-CALLOUTS' static-extern
primitive verbatim, with everything past PCRE2's surface in pcrec's own
clearly-flagged namespace (SR-10) so the D26 compatibility story stays clean.

### 7.1 The namespace requirement, made testable

**[PROPOSED]** the rule that makes "clearly-flagged namespace" mean
something operational rather than stylistic:

> Every pcrec-only template form must be a spelling that **PCRE2 rejects**,
> in both the core and EXTENDED dialects.

The reason is D26 tier 1. If a pcrec-only form were something PCRE2 *accepts*
with a different meaning, then a valid PCRE2 template would silently change
behaviour under pcrec — a miscompile, the one outcome the compatibility story
cannot survive. Stated this way it is a **property that can be tested**, and
it can be tested the same way it was measured: hand the candidate spelling to
libpcre2 and require an error.

**[MEASURED]** all candidates surveyed are rejected by PCRE2 10.46 in both
dialects, so the namespace is available (probe §13):

| candidate | core | EXTENDED |
|---|---|---|
| `${!name:1}` | `-35` | `-35` |
| `$!{name:1}` | `-35` | `-35` |
| `${#…}`, `${@…}` | `-35` | `-35` |
| `${1!upper}`, `${1\|upper}` | — | `-58` |
| `${1:!upper}`, `${1:^}` | — | `-59` |

**[PROPOSED]** `${!...}` — it is the only shape measured as an error
*independently of the dialect*, so the flag does not depend on which tier is
enabled. Spelling is Frank's to rule (§9 question 5); the *requirement* above
is the part this note asks to be adopted regardless of spelling.

**Convergence worth recording (2026-08-14).** `design_callout_abi.md` §3
arrives at the same principle from the pattern side, and names this note as
sharing the discipline: *"a spelling that reinterprets a currently-valid
pattern must be MODULE-GATED"* — `(<x>)` is today a group matching the
literal `<x>`, `\{` an escaped literal brace. Same hazard, and the two rules
should be read together, but they are not identical and the difference is
deliberate:

- The **pattern** side gates, because the colliding spellings are already
  *valid PCRE2* and cannot be made errors; the module gate is what keeps
  today's parse standing when the module is off.
- The **template** side can demand more, because the namespace is empty:
  every candidate measured is *already an error* in PCRE2 (the table above),
  so pcrec-only template forms can be required to collide with nothing at
  all. That is strictly stronger than gating, and it costs nothing to keep
  while the property still holds.

Both are one instance of SR-10's rule that pcrec's own surface lives in a
flagged namespace; if a future template extension ever needs a spelling PCRE2
accepts, it falls back to the pattern side's module gate rather than
inventing a third answer.

### 7.2 Callback segments

**AMENDED 2026-08-14.** The first draft invented a bespoke signature taking
`(in, inlen, out, outcap, outlen)`. `design_callout_abi.md` **F6** rules that
out: *"[M4-SUBST]'s callback template segments reuse this same
`rx_matchfn`/`rx_ctx` primitive verbatim; the subst design note should consume
the §1 typedef rather than invent a sibling."* What follows is the amended
form, and it is better than what it replaces — the bespoke version passed one
pre-selected capture's text, where `rx_ctx` hands the callback *all* the
captures and lets it choose, which is exactly what Frank's
`parse_int($1) > 100` direction needs.

**[PROPOSED]**, consuming the ABI's context type verbatim:

```c
/* Emitted ONLY when the template names it; the embedding program defines it.
 * Renders one template segment. Reads its inputs from the SAME rx_ctx a
 * callout receives — ctx->caps[k] selects any group, ctx->subject is the
 * text. Writes at most outcap bytes to out; returns the number of bytes
 * produced, or -1 to fail the substitution. Called with out == NULL and
 * outcap == 0, it returns the length it WOULD produce, writing nothing. */
typedef ptrdiff_t rx_renderfn(const rx_ctx *ctx,
                              unsigned char *out, size_t outcap);

extern ptrdiff_t rx_tr_upper(const rx_ctx *, unsigned char *, size_t);
```

**How far "verbatim" reaches, stated precisely**, because F6 asks for
something only half of which is literally possible. The **`rx_ctx` half is
verbatim** — same struct, same capture representation, same field meanings,
no conversion, which is the part F3 actually cares about. The **`rx_matchfn`
half cannot be**, because the two functions have different jobs: a matcher
*consumes* subject text and reports a length; a renderer *produces* output
bytes. A renderer with `rx_matchfn`'s exact signature would have nowhere to
write. So `rx_renderfn` is `rx_matchfn` **extended by an output buffer**, and
it deliberately keeps every other convention identical:

- `ptrdiff_t` return, with `-1` = fail and `>= 0` a length — the same signed
  discipline F1 gives for `rx_matchfn`, and for the same reason (a zero-length
  render must stay distinct from a failure).
- `const rx_ctx *` as the first parameter, unchanged.
- Compile-time bound: the `extern` is declared only when a template names it,
  so a program with no callback templates gains no symbols and no link-time
  obligation — D36's static-extern primitive, zero cost when absent.

This is offered as the reading of F6 rather than a departure from it; if the
manager intends something stricter — a renderer that really is an
`rx_matchfn`, presumably writing through a field added to `rx_ctx` — that is
§9 question 13.

**One consequence that improves the design.** The `out == NULL` convention
above is the same one §5.2 proposes for `rx_subst`'s sizing mode, so the
sizing question raised below composes instead of conflicting: a
callback-bearing template can be sized exactly by calling each renderer once
with `out == NULL`. That costs a second call per segment but keeps the sizing
mode *exact*, which the first draft had given up on. It does mean a renderer
must be **pure enough to be called twice** — a documented obligation on the
embedder, not something pcrec can enforce, and the reason option (a) below
survives as the fallback for renderers that are not.

**A real consequence, stated rather than hidden:** a callback's output length
is not knowable without asking the callback, so **the sizing mode (§5.2)
cannot be exact for a callback-bearing template for free.** Three options,
and the amended signature above changes which one wins: (a) sizing mode
returns a lower bound and callers handle `RX_SUBST_NOSPACE` anyway, (b)
sizing mode calls each renderer with `out == NULL` — **exact**, at the cost
of a second call per segment and an obligation that renderers be callable
twice, (c) callback templates get a sink-based entry point instead:

```c
/* Streaming writer form: no output buffer at all. */
int rx_subst_to(const unsigned char *s, size_t n,
                int (*sink)(void *ctx, const unsigned char *p, size_t len),
                void *ctx);
```

**[PROPOSED]** (b) as the default, with (a) as the documented fallback for
renderers that cannot be called twice, and (c) offered alongside: the sink
form composes with **[M3]** later and removes the buffer-sizing question
entirely. It is also independently useful — writing substitution output
straight to a socket or a `FILE *` with no intermediate buffer is exactly the
embedded-niche story. Note that (c)'s `void *ctx` is the sink's own context,
not the renderer's; `rx_ctx` covers the renderer, which is what question 6
below now reduces to.

### 7.3 Built-in transforms

**[PROPOSED]** the callback mechanism is the general answer, and *specific*
built-in transforms (upper, lower, trim, pad, a numeric format) each earn
their own row under D18 rather than arriving as a bundle. Recording the
direction is enough for this note; building one is not phase-1 work. Note
that PCRE2's own `\U`/`\L` (§3.3) already covers the case-forcing subset, so
a pcrec built-in `${!upper:1}` would be *redundant with* `\U$1\E` and should
be justified on ergonomics or not built.

---

## 8. Testing sketch

### 8.1 A corpus format extension, in the existing shape

**[PROPOSED]** substitution needs a template and an expected output string,
neither of which `.rxt` can express. The extension follows the existing
directive grammar exactly (`docs/testing.md`, "The `.rxt` format") — a
block-scoped directive like `flags`/`features`, plus assertion lines that
parallel `m`/`n`/`perr`:

```
# repl <template>       — block-scoped, like flags/features; does not carry
# s  "<subject>" "<expected output>"    — first-match substitution
# sg "<subject>" "<expected output>"    — global substitution
# serr                                  — the TEMPLATE fails to compile

pattern (a+)b
repl <$1>
s  "xaabz" "x<aa>z"
sg "aabaab" "<aa><aa>"

pattern (b)
repl [$2]
serr
```

The `<expected output>` field reuses the existing quoted-subject escape set
(`\"`, `\\`, `\n`, `\t`, `\r`, `\f`, `\v`, `\xHH`) unchanged, which matters:
substitution outputs are exactly where an embedded NUL or newline needs
writing down, and that machinery already exists and is tested.

### 8.2 The oracle, and a measured exclusion

**[MEASURED]** python's `re.sub` is a **valid oracle for global-mode splice
geometry** — it agrees with libpcre2 byte-for-byte on every empty-match cell
measured, which is the part most worth an oracle:

| cell | libpcre2 10.46 | python 3.14 `re.sub` |
|---|---|---|
| `a*` on `"bab"` | `[]b[a][]b[]` | `[]b[a][]b[]` |
| `a*` on `"aab"` | `[aa][]b[]` | `[aa][]b[]` |
| empty pattern on `"abc"` | `-a-b-c-` | `-a-b-c-` |
| `(?=b)` on `"abc"` | `a-bc` | `a-bc` |
| `\b` on `"ab cd"` | `-ab- -cd-` | `-ab- -cd-` |
| `a*` on `"bab"`, first only | `[]bab` | `[]bab` |

Two adjustments the verifier needs, both mechanical: python spells references
`\g<n>`/`\g<name>` rather than `$n` (`re.sub` treats `$1` as literal text), and
`re.subn` supplies the substitution count.

**[MEASURED]** and this is a genuine **oracle exclusion**, in the same shape
as the exclusions `docs/testing.md` already records for `{,}` and possessive
quantifiers:

> **Unset-but-existing groups diverge.** `/(a)|(b)/` on `"b"` with `[\1]`:
> python renders `[]`; libpcre2 with the same template *errors* with `-55
> (requested value is not set)` and needs `PCRE2_SUBSTITUTE_UNSET_EMPTY` to
> render `[]`. Whichever way §9 question 3 is ruled, one of the two oracles
> disagrees with pcrec on this cell and the corpus must mark it.

This is exactly the *differential gate principle* case
(`docs/testing.md`, 2026-08-12): the two oracles disagree, so the cell is
pinned against the one that matches the ruling and annotated with why.

### 8.3 What is testable BEFORE captures land — and it is most of it

This subsection is the practical payoff of §1 and is **[PROPOSED]** as the
phase-1 test plan:

1. **The whole template compiler, with no matcher at all.** Template parsing,
   every §4.2 diagnostic, every §3.2 grammar corner, the tier gate's *"requires
   module 'subst-extended'"* refusals. A template compiler is a pure function
   of (template, group count, name table), and `--count-groups` supplies the
   group count today. This is testable against patterns with any number of
   groups, because *counting* groups needs no capturing.
2. **Every literal-only splice**, using today's `rx_search`. `pattern abc` +
   `repl X` is fully implementable now.
3. **The entire global-mode splice geometry — all of §6.1.** Every cell in
   that table uses only `$0`, and `$0` *is* `rx_span`, which `rx_search`
   already fills. `a*`, `\b`, `(?=b)` and the empty pattern are 0-group
   patterns. So the single fiddliest part of the feature, the empty-match
   advancement rule, can be built and pinned against both oracles **before M4
   exists**. (`\b` and `(?=b)` are themselves module-gated — `assertions` and
   `lookaround` — so the phase-1 subset of this table is the `a*`/empty-pattern
   rows, with the rest arriving as those modules do.)
4. **Only `$1`..`$n` and `${name}` are actually gated** — on M4 and on
   `named-groups` respectively.

**[PROPOSED]** a `tests/subst/` directory per `docs/testing.md`'s
"Adding a new component test directory", whose pre-M4 content asserts the
`perr`/`serr` refusals and items 1–3, converting to full cases as captures
land. That is the ratchet shape the project already uses.

### 8.4 The D27 angle

**[PROPOSED]** this feature is an unusually good D27 candidate. The template
language is *specified by this note* and by PCRE2's documented surface, with
essentially no implementation-derived alphabet — which is the precise
condition under which D27 measured its win. A spec-first author denied `src/`
and `tests/` could write the template corpus from §3 and §6 alone, and
`tests/probes/probe_subst.c` exists to be handed over as working oracle code
(the stated reason `tests/probes/` exists at all).

---

## 9. Open questions for Frank

Numbered for reference. Recommendations are this note's, not rulings.

1. **Is `$0` core?** **[MEASURED]** it is core in PCRE2, and it costs nothing
   because `rx_span` already carries it. *Recommend: yes, core.*
   **RULED (D38, 2026-08-14):** yes, `$0` is core.

2. **Is the bare `$name` form (no braces) supported?** **[MEASURED]** PCRE2
   supports it and it is greedy — `$gx` is the name `gx`, not group `g` then
   `x` (§3.2). Supporting it is PCRE2 fidelity; dropping it is one fewer
   footgun, and pcrec would catch the mistake at build time rather than at
   run time, which weakens the footgun argument considerably.
   *Recommend: support it (tier 1 fidelity), since the compile-time check
   defuses it.*
   **RULED (D38, 2026-08-14):** supported, per the recommendation — the
   compile-time check defuses the footgun.

3. **What does an UNSET but existing group render as?** The most consequential
   question here. **[MEASURED]** PCRE2 default: `-55`, a run-time error;
   with `SUBSTITUTE_UNSET_EMPTY`: empty. Python: empty. pcrec's options are
   (a) always empty, (b) a **generation axis** (D18) chosen when the
   substituter is emitted, (c) reproduce the run-time error. Note that (c)
   puts an error path into generated code for the embedded niche, and that
   the D18-shaped answer is (b) with a default. *Recommend: (b), defaulting
   to empty* — which also makes python the cleaner oracle (§8.2).
   **RULED (D38, 2026-08-14):** (b) — a GENERATION AXIS, default empty;
   python becomes the clean oracle (§8.2).

4. **Does the output buffer get NUL-terminated?** **[MEASURED]** PCRE2
   terminates *and* requires room for it, and reports length inclusive of it
   on overflow but exclusive on success (§5.4). §5.2 proposes length-only,
   uniformly, no NUL. This is an API-shape divergence from PCRE2, which D26
   does not protect either way. *Recommend: length-only.*
   **RULED (D38, 2026-08-14):** length-only, uniformly, no NUL termination
   and no NUL budget — 8-bit clean; embedded NULs are legal output.

5. **The extension namespace spelling.** **[MEASURED]** every candidate is
   rejected by PCRE2, so all are safe; `${!...}` is the only one that is an
   error *independently of dialect* (§7.1). Separately, and more important
   than the spelling: is §7.1's **requirement** (every pcrec-only template
   form must be a PCRE2 error, testably) adopted as a rule? It is the
   template-side sibling of `design_callout_abi.md` §3's module-gated
   collision rule — that doc names this note as sharing the discipline — and
   §7.1 argues the template side should hold the stronger form, since its
   namespace is empty where the pattern side's is not.
   **RULED (D38, 2026-08-14):** the §7.1 namespace rule is ADOPTED as
   testable (every pcrec-only template form must be a spelling PCRE2
   rejects), and `${!...}` is reserved as the extension prefix.

6. **Callback signature: is there a `void *ctx`?** *Narrowed by the
   2026-08-14 amendment.* Segment renderers now take `const rx_ctx *`
   verbatim (§7.2), so the question is no longer whether they get a context —
   it is whether `rx_ctx` itself should carry a user-data pointer, which is
   `design_callout_abi.md`'s **own question 1** and should be ruled there
   once, not twice. D19 (usable *from* threads) is the argument for yes: a
   renderer with no user data must reach for a global. What remains here is
   only the sink form's `void *ctx` (§7.2 option (c)), which is the sink's,
   not the renderer's. *Recommend: rule it on the ABI side; yes on the sink.*
   **RULED (D38, 2026-08-14):** subsumed by `design_callout_abi.md`'s
   ruling — `rx_ctx` gains `void *user` via the `rx_callout_ref` binding
   unit (§1.1 there); segment renderers consume `rx_ctx` verbatim, so
   this question does not need a separate answer here.

7. **Where does the template come from on the CLI?** `--replace TEMPLATE` is
   the obvious flag. But **[V-E]**'s manifest is the ratified home for
   "name, pattern, flags, encoding per entry", and a template is naturally a
   field of that entry. *Recommend: `--replace` now, and note the manifest
   field so V-E's design inherits it.* Related: may one file carry several
   templates over one matcher (§5.5)?
   **RULED (D38, 2026-08-14):** `--replace` now (repeatable per §5.5);
   `[V-E]`'s manifest gains a template field when that design lands.

8. **`pcrec_error.pos` with two input strings.** It is documented as an offset
   into *the pattern*. A template error needs an offset into *the template*.
   This changes `lib/pcrec.h` and so **must be answered before M4's API
   freeze** — it is the one question here with the same deadline as §2.
   Options: a discriminator field, a second position field, or a convention.
   **RULED (D38, 2026-08-14):** `pcrec_error` gains a WHICH-INPUT tag —
   an enum distinguishing pattern vs. template — beside `pos`; a
   `lib/pcrec.h` change to land at the M4 freeze.

9. **UTF deferral.** Confirm that the template compiler is encoding-blind
   (C4: byte offsets throughout, per **[DD-12]**), that global-mode step width
   is **[M5]**'s only change to §6, and that case-forcing under UTF (§3.3) is
   **[DD-1]**/**[M5]** business and not this note's.
   **RULED (D38, 2026-08-14):** confirmed as stated — byte offsets
   throughout per **[DD-12]**, UTF is **[M5]**'s.

10. **Duplicate group names (`(?J)`).** A template `${name}` with two groups
    of that name has to pick one. Deferred with `named-groups`, or ruled now?
    **RULED (D38, 2026-08-14):** deferred, to land together with module
    `named-groups`.

11. **Does the sizing mode survive §7.2?** *Improved by the amendment:* the
    `out == NULL` convention makes it exact even for callback templates, at
    the cost of calling each renderer twice. Adopt that, or accept a lower
    bound, or make the sink form the only supported shape for the extended
    tier?
    **RULED (D38, 2026-08-14):** sizing is EXACT BY CONTRACT — renderers
    must honor `out == NULL` sizing and be deterministic across the two
    passes; a renderer that violates this is the embedder's bug, not a
    pcrec obligation to guard at run time.

**Added by the 2026-08-14 callout-ABI amendment:**

12. **`rx_span` versus `rx_ctx.caps` — who gives way?** F3 requires one
    capture representation with no conversion, but `<prefix>_span`
    (`size_t start, end`) is already emitted (`src/gen/emit_dfa.c:106`),
    already in `rx_search`'s signature and already consumed by
    `tests/harness/driver.c`. Satisfying F3 means `rx_span` becomes the pair
    type or disappears — a breaking change to a shipped generated contract,
    which is **[DD-3]**'s territory. *Recommend: the whole match becomes
    `caps[0]` and `rx_search` keeps a compatibility signature*, but this is
    a match-API call, not a substitution one. See §2.4(a).
    **RULED (D38, 2026-08-14):** `rx_span` BREAKS at the M4 freeze — it
    becomes the `ptrdiff_t` pair type in one announced break, not a
    permanent conversion seam (Frank: `ptrdiff_t` is "clearer in a utf
    environment"). This is the M4 match-API's [DD-3] event, scheduled
    with the freeze per this question's own framing.

13. **How literally does F6's "verbatim" bind?** §7.2 reads it as: the
    `rx_ctx` half is verbatim, the `rx_matchfn` half is extended by an output
    buffer, because a renderer produces bytes and a matcher does not. If
    something stricter is intended — a renderer that really is an
    `rx_matchfn`, writing through a field added to `rx_ctx` — say so, since
    it changes the ABI struct rather than this note.
    **RULED (D38, 2026-08-14):** confirmed as §7.2 reads it — a renderer
    is `rx_matchfn` extended by an output buffer:
    `rx_renderfn(const rx_ctx *, unsigned char *out, size_t cap) ->
    ptrdiff_t`, same return discipline as `rx_matchfn`, sharing the
    `out == NULL` sizing convention (Q11).

14. **Is `rx_ctx.subject` really `const char *`?** §2.4(c) argues it should
    be `const unsigned char *`: `char`'s signedness is implementation-defined,
    the emitter already uses `unsigned char` because it indexes 256-entry
    class tables with subject bytes, and `PCREC_ENC_ASCII` is documented
    8-bit clean. This is a defect report against the ABI proposal, surfaced
    here because this note is its second consumer.
    **RULED (D38, 2026-08-14):** `const unsigned char *subject` — already
    applied in `design_callout_abi.md` §1.

---

## 10. Summary of what this note asks for

- **Adopt §2's C1–C11 as requirements on M4's match API** (the deadline
  item), together with §2.2's explicit non-requirements. C4 and C5 are now
  stated in the callout ABI's `rx_ctx.caps` representation, per F3.
  **ACCEPTED (D38).**
- **Rule §9's fourteen questions**, of which 3, 8 and 12 are load-bearing for
  other work. **ACCEPTED (D38)** — all fourteen ruled, see §9 above.
- **Take §2.4's four consequences of adopting `rx_ctx.caps` to the freeze**,
  three of which are not visible from the callout side alone: it breaks the
  already-emitted `<prefix>_span` type (question 12), `ncap` is a watermark
  that C6 needs pinned to `ngroups + 1` on a completed match, and
  `rx_ctx.subject` should be `const unsigned char *` (question 14).
  **ACCEPTED (D38).**
- **Accept the module-name tiering in §3.0** (`subst`, `subst-extended`,
  `subst-pcrec`) as the mechanism that turns PCRE2's run-time
  `SUBSTITUTE_EXTENDED` option into a D18 compile-time tier and inherits
  D26 tier 3's diagnostic discharge for free. **ACCEPTED (D38).**
- **Accept §7.1's namespace requirement** — every pcrec-only form must be a
  spelling PCRE2 rejects — as a testable rule, independent of the spelling
  chosen. **ACCEPTED (D38).**
