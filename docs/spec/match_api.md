# The match API — generated-artifact and library contract

This is the **spec**, not the design record: what pcrec's compiled library
(`lib/pcrec.h`) and every generated matcher actually promise, as shipped.
Per `docs/spec/CLAUDE.md`'s charter, this document states the contract; it
is actively maintained and carries no build history. Where it references
`docs/design/match_api_m4.md` or `docs/design/engine_m4.md`, that is
informational — the reasoning and panel record behind a rule, never a
second source of authority. On any disagreement between this document and
those, THIS document is what pcrec promises.

Every rule below was checked against the shipped surface: `lib/pcrec.h`
itself, artifacts actually emitted by `build/pcrec` for representative
patterns (a `--no-captures` DFA build, a captures-default VM build, a
custom `-p` prefix, budget-limited builds), and the test cases cited
inline. Two places where the shipped surface does not match
`match_api_m4.md`'s design text are called out explicitly (§3.5, §7)
rather than silently reconciled.

**Verification ledger.** The document was authored at commit `c113890`
and re-verified end to end after the R29 adversarial panel
(2026-08-18, `[M4.7g]`). Every claim was re-checked against artifacts
emitted freshly for that pass, and this revision adds these measurements:
the find-all protocol of §3.1 run against `python3 re.finditer` on twelve
(pattern, subject) pairs plus three that expose its documented lossiness;
the §8.0 example compiled `-Wall -Wextra -Werror`, run, and its output
compiled in turn; the subject-side contract of §3.1 measured under
AddressSanitizer on exact-size heap buffers with a firing positive
control; §5.3's concurrency promise checked against the shipped,
sabotage-validated TS-1/TS-2/TS-3 guards rather than a one-off probe;
§3.4/§6.1's section placement measured with `readelf`; §6.3's macro
inventory measured by listing every `#define` in a build of each engine;
§8.1's D56 guarantees measured at the refusal boundary. Two errors the
panel found in the previous revision are recorded where they happened
rather than quietly repaired: §3.5 (a contradiction described as an
omission, and §2 quoting a corrected comment as if it were shipped) and
§6.3 (a mirror claimed to be total that is partial). The corresponding
shipped comments — the emitted `rx_matchfn` ABI block and
`lib/pcrec.h`'s generated-searcher comment — were fixed in the same
pass, so §2's quotation is now the real text.

**[M5-SEAM] revision (2026-08-18, D58 — the encoding seam prelude).** The
document gains §3.1.1, the `<prefix>_next_pos` encoding residual, and §3.1's
find-all loop now advances through it. What this pass re-measured, all
against artifacts emitted by the build at this commit: §3.1's loop compiled
against real artifacts and run on 26 (pattern, subject) pairs x 2 engine
arms = 52 runs against `python3 re.finditer`, with the lossy class checked
as a strict SUBSET in both directions (the measurement is now
`tests/encseam/`, a suite in `make test`, rather than a one-off transcript);
§3.1.1's two code blocks quoted verbatim from a fresh `-p rx` build of
`'a(b|c)+d'`, no elisions; §8.0's example recompiled `-Wall -Wextra -Werror`
against `lib/pcrec.h` and `libpcrec.a`, run, and its `matcher.c` compiled in
turn, plus every field of a `pcrec_default_options()` struct printed to
re-check item 1's claim; §8.1's D56 refusal re-measured at the `a{9795}` /
`a{9796}` boundary (its wording changed — the old text promised a milestone
that had already shipped) together with the escape it now names; §8.2's
encoding paragraphs measured at the refusal boundary for `utf8` and for an
out-of-range value. Two SURFACE changes ride this revision and are recorded
where they happen rather than folded in silently: `PCREC_ENC_ASCII` is
renamed `PCREC_ENC_BYTE` (§8.2), and §3.1's byte-vs-character caveat is
RESOLVED rather than deleted — §3.1.1 keeps the old caveat's text and says
what discharged it. A same-day manager follow-up (from a live
consumer-question thread) adds two ADVISORY clarifications: the §3
entry-picker's discriminator sentence and §3.2's failing-match cost note —
prose only, no emitted text quoted, nothing re-measured.

**[M6.3] revision (2026-08-18, module `named-groups`).** §6's own
recorded open question — "the `groups` array is described as sorted and
`bsearch`-able, but no document states the sort KEY" — is DISCHARGED
rather than reworded around: the key is `strcmp` on the name, matching
libpcre2's own `PCRE2_INFO_NAMETABLE` order (measured directly,
tests/probes/probe_named_groups.c), and docs/dev/decisions.md's D59
records the evidence. Re-measured for this pass: §6's `groups`/`nnames`
field comments and its worked example, quoted verbatim from a fresh `-p
rx --features named-groups` build of `'a(?<b>b|c)+d'` (both the
captures-default and `--no-captures` forms, to check the `slot: -1`
claim in both directions).

**D61 revision (2026-08-18, same session — Frank design thread).** Two
ADVISORY forward-promise clarifications, prose only, no emitted text
quoted, nothing re-measured: §3.3's slot-latitude note is narrowed
(primary groups' `slot == number` is permanent on captures-on builds;
the different-slot latitude applies to future ref-bearing rows only)
and §6 gains the `ngroups` PERMANENT-PREFIX promise (slots
`1..ngroups` are this pattern's own groups forever; insertion
mechanisms append, never interleave). docs/dev/decisions.md D61.

**[ABI-NS] revision (2026-08-18, same session — D60 + addendum).** Every
emitted macro whose VALUE is a property of pcrec's CONTRACT rather than of
one artifact moves from a per-`<PREFIX>` spelling to one canonical,
unprefixed `PCREC_*` spelling in the shared `PCREC_RX_ABI_H` block (§2):
the give-up code space (`<PREFIX>_ERR_STEPS`/`_FRAMES`/`_WORK`/`_FLOOR` →
`PCREC_ERR_STEPS`/`_FRAMES`/`_WORK`/`_FLOOR`; **[DD-14 wave A, D71 item 1,
2026-08-24]: `PCREC_ERR_RECURSE` joins it and `PCREC_ERR_FLOOR` moves
−4 → −5, and `PCREC_ERR_INTERNAL` — below the floor, NOT a give-up —
joins the same shared block for the same "one contract fact, one spelling"
reason — see §4's own revision notes**), the caps-array unset
sentinel (`<PREFIX>_UNSET` → `PCREC_UNSET`), and the nine D46 stamp BIT
constants (`<PREFIX>_VM_RUNG_CURSOR`/etc., `<PREFIX>_VM_STRAT_POSSESSIVE`/
`_BACKTRACKING`, `<PREFIX>_VM_PRUNE_CLAMPED`/`_UNCLAMPED` →
`PCREC_VM_RUNG_*`/`PCREC_VM_STRAT_*`/`PCREC_VM_PRUNE_*`). The per-prefix
spellings are DELETED, not aliased (house precedent: `PCREC_ENC_BYTE`,
D44.2's `<prefix>_span` retirement). NEW in the same block:
`PCREC_ENGINE_DFA`/`PCREC_ENGINE_VM`, naming `rx_info.engine`'s
formerly number-only contract (§6 used to say "no such constant is
#defined anywhere" — this revision discharges that). What STAYS
per-prefix is exactly the set whose VALUE genuinely varies per artifact:
`<PREFIX>_NCAPS`, the budget/capacity macros, the D46 stamp MASKS
(`<PREFIX>_VM_RUNGS`/`_STRATS`/`_PRUNES`), `<PREFIX>_VM_PREFILTER`/
`_VM_PRUNE_CEILING`. §1, §2, §4, §5, and §6's engine paragraph are
re-quoted this pass, verbatim from a fresh `-p rx` build of `'a(b|c)+d'`
(both a `--no-captures` DFA artifact and a captures-default VM one) —
docs/dev/decisions.md D60 and its addendum.

**[DD-14.FB] revision (2026-08-24, D71 item 2) — the first revision that
stated a contract BEFORE it existed, and the marking mattered.** Every
revision before it recorded what shipped. That one added **§10, the
caller-provided frame buffer**, as SPECIFIED AND NOT YET BUILT. It was
here rather than in the design note alone because D71 item 2 rules the
shape "decided at docs/spec/match_api.md under D40", and because the three
existing entries' compatibility story is a fact about THIS document's
contract.

**[DD-14.FB] code half (2026-08-25) — §10 IS NOW BUILT, and this document
is once again a record of what ships.** Every artifact pcrec emits exports
`<prefix>_search_in`, `<prefix>_match_in` and `<prefix>_match_caps_in`,
declares `<prefix>_buffers`, and carries the five sizing macros and
`rx_info`'s four new fields at `abi` 3 — on BOTH engines, inert on a DFA
artifact. The forward pointers in §3, §4, §5.3 and §6 have lost their
"not yet built" wording; nothing else in §1-§9 changed. MEASURED on the
shipped emitter and re-quoted in §10: `<prefix>_search`'s stack frame is
131,216 B on a call-bearing artifact where `<prefix>_search_in`'s is 144 B,
the give-up boundary is unmoved (a 684-byte subject matches, 686 does
not), and the `MAP_NORESERVE` worked example matches 800 KB in 0.057 s
touching 90 MB. The design record, with the alternatives
and their measured costs, is `docs/design/frame_buffer_design.md`
(informational, per docs/spec/CLAUDE.md's charter). Measured for this pass
and quoted in §10: the run-struct and per-entry stack sizes, the
depth-vs-capacity table, and the `MAP_NORESERVE` worked example, all
against artifacts emitted by the build at this commit.

**[SPEC-1.4] revision (2026-08-26, docs/spec/ consolidation pass, D80) —
five small patches, no shipped behaviour changed.** (1) §4 gains one
sentence pointing at `docs/spec/limits.md` for the give-up codes' numeric
trigger defaults, rather than leaving a reader to find them scattered
across three decision entries — the numbers already live in `limits.md`
(`[SPEC-1.1]`) and this document was the one place that never pointed
there. (2) §6.3's DFA-stamp-gap caveat — the survey's C2 — is VERIFIED
CURRENT, nothing changed: `[DD-13]`/`[DD-13c]` (2026-08-25) already
discharged the gap ("a consumer MAY now `#if` on `RX_ENGINE`"), re-checked
against a freshly built DFA artifact and a VM hybrid for this pass
(`grep RX_ define` on `--no-captures '(?:foo|bar)\z'`: `RX_ENGINE "dfa"`,
`RX_DFA_SCAN "unanchored"`, `RX_DFA_PREFILTER "byte-class-bounded"`,
present and correct) and no stale wording of the old caveat survives
anywhere in this file. (3) §6 gains a caller-facing `abi` paragraph
restating D76 in contract terms: what a bump means, what is fixed within
one number, and pre-v1's "the stamp is the whole of the announcement"
posture (D40 regime 1) — the existing prose narrated four individual bump
events but never stated the general rule; `rx_info.abi` is confirmed `6`.
(4) §8.2 gains a lead sentence stating plainly, before the field table,
that `byte` is the only implemented encoding — matching `lib/pcrec.h`'s
own enum comment and `cli/main.c --help`'s wording verbatim, rather than
requiring a reader to find the fact three paragraphs down. (5) New §3.6,
"whole-subject / end-anchored matching" (survey's F9): the `(?:P)\z`
idiom, why it exists (no native end-anchored entry; `$` is the wrong
anchor — verified live, `(?:foo)$` matches `"foo\n"` at `[0,3)` while
`(?:foo)\z` on the same subject reports no match), the `a|ab` counter-
example showing a naive `_match_caps(...) == n` test is
sufficient-not-necessary (verified live: `a|ab` on `"ab"` reports
`[0,1)`, while `(?:a|ab)\z` on the same subject reports `[0,2)` via the
alternative branch the naive test never tries), that the idiom is
RULED-permanent (D77, plan row `[OS-4]`, 2026-08-25 — not a stopgap
awaiting a future generation axis), and the whole-subject artifact's own
DFA stamps (verified live on `--no-captures '(?:foo|bar)\z'` and
`'(?:foo)\z'`: `RX_DFA_SCAN "unanchored"`, `RX_DFA_PREFILTER
"byte-class-bounded"`/`"memchr-bounded"` — the `-bounded` forms §6.3
already documents for a `\z` view).

---

## 1. Two namespaces plus one closed, fixed-literal family

Every symbol a pattern compile can produce falls into one of three
groups, with one stated boundary case (the two artifact-stamp macros
noted under group 2, which are `PCREC_*`-named yet per-artifact):

1. **Per-artifact symbols**, scoped by the caller's `pcrec_options.prefix`
   (default `"rx"`): `<prefix>_search`, `<prefix>_match`,
   `<prefix>_match_caps`, `<prefix>_info`, `<prefix>_next_pos` (§3.1.1),
   and the `<PREFIX>_*` macro
   family (`RX_NCAPS`, the D46 observability
   macros in §6.3). A pattern compiled with `-p foo` gets
   `foo_search`, `FOO_NCAPS`, etc. — verified by compiling the same
   pattern under `-p foo` and reading the emitted header. (The CLI spells
   this option `-p` and only `-p`; there is no `--prefix` long form —
   `pcrec --prefix foo ...` is an unknown-option error.)
   **[ABI-NS], 2026-08-18 (D60):** `RX_UNSET` and `RX_ERR_*` used to be
   in this family and are NOT any more — they moved to the fixed,
   unprefixed `PCREC_*` spelling in group 3's ABI block below, and the
   `<PREFIX>_*` spelling was DELETED, no alias. A caller reading old
   documentation (or an artifact emitted before this date) that names
   `RX_UNSET`/`RX_ERR_STEPS`/etc. is reading the pre-[ABI-NS] contract.
2. **pcrec's own fixed library surface**: the `PCREC_*` enum/bit
   constants and the `pcrec_options`/`pcrec_output`/`pcrec_error`/
   `pcrec_err_input` types declared in `lib/pcrec.h`. Never scoped by a
   generated pattern's prefix.

   **The `PCREC_*` spelling is not by itself a promise that a name lives
   in `lib/pcrec.h`**: two macros break that reading, and a consumer
   grepping for the namespace will find them. Every emitted artifact
   carries `PCREC_FEATURE_SET` and `PCREC_FEATURE_MODULES` (the D37
   artifact stamp — e.g. `#define PCREC_FEATURE_SET "std1"`,
   `#define PCREC_FEATURE_MODULES "classes,modifiers"`), which are
   `PCREC_*`-named, PER-ARTIFACT, and declared nowhere in `lib/pcrec.h`.
   They are the one exception to §8's own naming rule, and they are
   deliberate: an artifact must not be ambiguous about what it was built
   with. Everything else `PCREC_*` follows the rule as stated.
3. **Fixed-literal ABI types**, scoped by *neither* of the above, in the
   order the artifact declares them: `rx_ctx`, `rx_matchfn`,
   `rx_callout_ref`, `rx_renderfn`, `rx_group_entry`,
   `struct rx_info`. These are always spelled `rx_*`
   regardless of `--prefix`, on purpose: they are what let two
   differently-prefixed generated matchers compose in one translation
   unit (a compiled matcher links directly as another's callout, with no
   adapter) — verified in the emitted header: the six types live inside
   their own `#ifndef PCREC_RX_ABI_H` guard, separate from the
   per-prefix `PCREC_GEN_<PREFIX>_H` guard wrapping the rest of the file,
   so two artifacts compiled with different prefixes and `#include`d into
   one TU declare these types identically and do not collide (confirmed:
   `-p rx` and `-p foo` builds of the same pattern emit byte-identical
   `#ifndef PCREC_RX_ABI_H` blocks).

   **[ABI-NS], 2026-08-18 (D60 + addendum).** The same guarded block also
   carries every emitted MACRO whose value is a pcrec-contract fact
   rather than an artifact-specific one, unprefixed and emitted
   unconditionally on every artifact (DFA-only included, the same
   "reserved but unreachable" shape §4 already had): the give-up code
   space `PCREC_ERR_STEPS`/`PCREC_ERR_FRAMES`/`PCREC_ERR_WORK`/
   `PCREC_ERR_RECURSE`/`PCREC_ERR_FLOOR` (§4 — `_RECURSE` joined and
   `_FLOOR` moved −4 → −5 at [DD-14] wave A, D71 item 1), the
   below-the-floor `PCREC_ERR_INTERNAL` (§4 — NOT a give-up, same wave,
   commit 2), the caps-array
   unset sentinel `PCREC_UNSET`
   (§5), the two engine constants `PCREC_ENGINE_DFA`/`PCREC_ENGINE_VM`
   (§6), and the nine D46 stamp bit constants `PCREC_VM_RUNG_CURSOR`/
   `_FRAMES_BOUNDED`/`_FRAMES_UNBOUNDED`/`_REVDET`/`_COUNTER`,
   `PCREC_VM_STRAT_POSSESSIVE`/`_BACKTRACKING`,
   `PCREC_VM_PRUNE_CLAMPED`/`_UNCLAMPED` (§6.3). These moved out of the
   per-`<PREFIX>` macro family of group 1 above; the old `<PREFIX>_*`
   spellings were DELETED, not aliased. What stays per-prefix, because
   its VALUE genuinely varies per artifact, is exactly `<PREFIX>_NCAPS`
   plus the D46 stamp MASKS and budget/capacity macros of §6.3.

A generated artifact is either self-contained (`options.header_name ==
NULL`, everything below in the `.c`) or split into a paired `.h`/`.c`
(`options.header_name` set) — both forms carry the identical declarations
below. Two things beyond the file split differ, and a consumer writing
against the header namespace should know both: the self-contained form
omits the `PCREC_GEN_<PREFIX>_H` include guard entirely (measured with
`header_name == NULL`: zero occurrences, against three in the split
form's `.h`), since there is no header to guard; and the D46
observability macros of §6.3 are emitted into the `.c` only, never into
the `.h` (§6.3 states this where it matters).

---

## 2. Fixed ABI types

```c
typedef struct rx_ctx {
    const unsigned char *subject;   /* whole subject, not a slice */
    size_t                len;      /* subject length */
    size_t                pos;      /* where to match, anchored */
    size_t                ncap;     /* capture slots known so far (watermark
                                        mid-match; ncaps on completion) */
    const ptrdiff_t     (*caps)[2]; /* [start,end); {-1,-1} = unset */
    void                 *user;     /* per-binding user data */
} rx_ctx;

/* returns matched length >= 0 (anchored at ctx->pos), -1 (fail), or a
 * typed give-up code in [PCREC_ERR_FLOOR, -2] -- one per way the
 * engine can give up (PCREC_ERR_STEPS/_FRAMES/_WORK/_RECURSE). D49: those
 * codes PROPAGATE, they are not collapsed to -1, and a caller doing
 * an exact `== -1` test sees them as distinct values. Values
 * strictly BELOW PCREC_ERR_FLOOR stay RESERVED for a future abort
 * semantic; PCREC_ERR_INTERNAL ([DD-14] wave A commit 2, D71 item 1) is
 * its first producer, and a
 * generated call site that invokes an rx_matchfn traps on one.
 * Self-contained: must accept ctx->ncap == 0, ctx->caps == NULL. */
typedef ptrdiff_t rx_matchfn(const rx_ctx *ctx);

#define PCREC_ERR_STEPS    (-2)
#define PCREC_ERR_FRAMES   (-3)
#define PCREC_ERR_WORK     (-4)
#define PCREC_ERR_RECURSE  (-5)  /* [DD-14] reserved: no producer yet (D71 item 1) */
#define PCREC_ERR_FLOOR    (-5)  /* give-ups: [FLOOR,-2]; below: reserved (D49) */
#define PCREC_ERR_INTERNAL (-6)  /* [DD-14] below PCREC_ERR_FLOOR: NOT a give-up, D71 item 1 */

#define PCREC_UNSET ((ptrdiff_t)-1)

typedef struct rx_callout_ref {
    rx_matchfn *fn;
    void       *user;
} rx_callout_ref;

/* Emitted ONLY when a substitution template names it. Renders one
 * template segment from the same rx_ctx a callout receives. Writes at
 * most outcap bytes to out; returns the number of bytes produced, or
 * -1 to fail. Called with out == NULL and outcap == 0, it returns the
 * length it WOULD produce, writing nothing. */
typedef ptrdiff_t rx_renderfn(const rx_ctx *ctx,
                              unsigned char *out, size_t outcap);

typedef struct {
    const char *name;
    int         number;
    int         slot;   /* caps[] index this entry delivers, or -1 if
                           this build delivers no slot for it */
    const char *ref;    /* NULL/empty for the primary's own groups */
} rx_group_entry;

struct rx_info {
    /* ... elided here; §6 quotes the full field list ... */
};

#define PCREC_ENGINE_DFA 1
#define PCREC_ENGINE_VM  2

#define PCREC_VM_RUNG_CURSOR           0x1u
#define PCREC_VM_RUNG_FRAMES_BOUNDED   0x2u
#define PCREC_VM_RUNG_FRAMES_UNBOUNDED 0x4u
#define PCREC_VM_RUNG_REVDET           0x8u
#define PCREC_VM_RUNG_COUNTER          0x10u
#define PCREC_VM_STRAT_POSSESSIVE      0x1u
#define PCREC_VM_STRAT_BACKTRACKING    0x2u
#define PCREC_VM_PRUNE_CLAMPED         0x1u
#define PCREC_VM_PRUNE_UNCLAMPED       0x2u

extern const struct rx_info <prefix>_info;   /* not inside the ABI block */
```

The block above is the emitted text verbatim (re-quoted from a freshly
emitted artifact for this revision), with two marked exceptions: the
`struct rx_info` body is elided to §6, and `extern const struct rx_info
<prefix>_info;` is per-prefix and so lives *outside* the
`PCREC_RX_ABI_H` guard, not in this block. Four things the comments
state that a reader should not have to infer:

- **`rx_renderfn` carries a sizing protocol**, and it is shipped ABI
  text, not a design intention: called with `out == NULL` and
  `outcap == 0` it writes nothing and returns the length it *would*
  produce. That is how a caller sizes a buffer before rendering.
- **`rx_group_entry.ref`** is documented in the artifact only as
  "NULL/empty for the primary's own groups". Its non-empty form is a
  labeled insertion path that nothing in pcrec can produce today.
- **[ABI-NS], 2026-08-18 (D60 + addendum): every macro in this block is
  UNPREFIXED and byte-identical across every `--prefix`.** Before this
  date the give-up codes and the unset sentinel were spelled
  `<PREFIX>_ERR_*`/`<PREFIX>_UNSET`, with a `<PREFIX>` placeholder in the
  `rx_matchfn` comment naming "this artifact's own uppercased --prefix";
  that placeholder is gone because the macros it pointed at no longer
  vary per artifact. The nine D46 stamp bit constants
  (`PCREC_VM_RUNG_*`/`PCREC_VM_STRAT_*`/`PCREC_VM_PRUNE_*`) and the two
  engine constants (`PCREC_ENGINE_DFA`/`PCREC_ENGINE_VM`, new — see §6)
  join them for the identical reason and are emitted unconditionally,
  even on a DFA-only artifact that never produces a VM stamp value or a
  give-up code — the "reserved but unreachable" shape §4 already had.
- **`<PREFIX>` still appears elsewhere in this artifact, just not in this
  block.** `struct rx_info`'s own `ncaps` field comment (§6) still reads
  "this artifact's own `<PREFIX>_NCAPS`" — `<PREFIX>_NCAPS` is a
  per-artifact VALUE (§1) and stays per-prefix on purpose, unlike the
  macros above.

**`rx_info` is a struct TAG, not a typedef, and every reference to it
spells `struct rx_info`** — verified directly (`grep`-visible in every
emitted header: `struct rx_info { ... };` and
`extern const struct rx_info <prefix>_info;`, no bare `rx_info` typedef
anywhere). This is an as-built departure from `match_api_m4.md` §5's
sketch, which showed a bare `typedef struct { ... } rx_info;`. The reason
is forced, not stylistic: under the default prefix `"rx"`, the per-artifact
instance `<prefix>_info` *is* the literal identifier `rx_info` — byte-
identical to the type's own name — and a typedef name and a variable name
cannot coexist in one C scope. Struct tags live in a separate C namespace
from ordinary identifiers, so `struct rx_info` (the type) and `rx_info`
(the default-prefix instance) coexist without conflict. **This is the
contract as shipped: an embedder writing code against a generated header
declares `const struct rx_info *`, never a bare `rx_info`.**

**This spelling is RULED, not provisional (D57, 2026-08-18).** The
question of renaming the per-artifact instance to buy a bare typedef
back is closed: the struct-tag form is blessed as the contract, and the
design sketch's typedef form is dead. A consumer that wants a typedef'd
name ships `typedef struct rx_info rx_info_t;` in its own header, which
touches nothing pcrec emits.

---

## 3. Entry points

Every generated artifact exports, unconditionally, five `<prefix>`-scoped
symbols: the four below, plus the encoding residual `<prefix>_next_pos`
that §3.1.1 specifies (a fifth entry since [M5-SEAM], and the one place an
artifact's byte-vs-character distinction lives).

**[DD-14.FB] (D71 item 2): three more entries ship** —
`<prefix>_search_in`, `<prefix>_match_in` and `<prefix>_match_caps_in`,
each its un-suffixed sibling plus one argument naming where the working
storage lives. **Eight is what an artifact exports today.** §10 is their
contract, and it includes the promise that the three below are unchanged —
signature, return space and behaviour — for a caller that never calls an
`_in` entry.

**[OPT-1], 2026-08-25: THE THREE UN-SUFFIXED ENTRIES HAVE A COST MODEL, and
it is the one thing about them a caller may now want to know.** On an
artifact whose stamped default storage does not fit inside one 4 KB page,
each of them **runs the match on a page-sized buffer and escalates to the
stamped default only on a `PCREC_ERR_FRAMES` give-up**, by calling a
non-inlined internal function that owns the full storage and re-runs the
match from scratch. Everything in this section and in §3.1–§3.3 — the
signatures, the return spaces, the anchoring, the `caps` disciplines, every
answer and every capture span — is **unchanged**, and §10.9 is why that is a
theorem rather than a hope. What changes is the price of a call.

**MEASURED on the RFC 5322 email specimen** (`--engine=vm`, 16-byte matching
subject, N=100k, median of 5, `taskset`, six repetitions): **213–268 → 45.6–48.8
ns/call**, against 44.2–47.2 for `<prefix>_search_in`; and that artifact's own
entry frame, `gcc -fstack-usage`, **98,512 → 3,168 B**. (The `^(a(?1)?b)$`
recursion specimen is a DIFFERENT artifact with different numbers — 131,216 →
3,184 B; §5.3 and `limits.md` §5 use that one. Do not pair one specimen's
timing with another's frame.)

**IT IS A BET, AND IT LOSES ON SOME PATTERNS. THE COST WHEN IT LOSES:**

- **The wasted fast attempt is bounded by the STEP and WORK budgets, not by
  the frame count.** Sixty frames of DEPTH can absorb an unbounded amount of
  backtracking, so "the fast tier is small" does not bound the work it does
  before giving up.
- **There is a DISCONTINUITY at the boundary, not a ramp.** MEASURED on
  `((a)|(aa))+b` (tiered vs `-fno-tiered-entry`, N=20k, median of 5): 18.5 vs
  207.1 ns at n=1 — 11× FASTER — rising to 186.4 vs 365.3 at n=23, then
  **568.9 vs 372.9 at n=24**, a 3.05× jump across one byte and 1.53× SLOWER
  than the single-tier entry. Above the boundary it stays 1.24–1.53× slower.
- **"Deep" can mean a very short subject.** That boundary is a **25-byte**
  subject (24 `a`s and a `b`). Depth is a property of the backtracking, not of the input length.
- **An escalating call can do up to twice the STEP budget of real work** —
  §10.9 resets both budgets for the deep attempt, so the fast attempt's spend
  is additional. §4 states the consequence for the give-up codes.

**A caller that needs depth on the FAST path uses `_in`.** A caller who knows
its subjects are deep, or who is on a stack too small for the deep tier (§5.3,
K33), supplies its own storage through §10's `_in` entries and never meets the
tier at all. `-fno-tiered-entry` (`docs/spec/tuning.md` §2.12) restores the
single-tier shape without changing call sites, and is the right answer for a
workload measured to sit above the boundary.

### 3.1 `<prefix>_search` — the search-loop entry

```c
int <prefix>_search(const unsigned char *s, size_t n, size_t startpos,
                     ptrdiff_t (*caps)[2]);
```

Searches `s[startpos..n)` for the leftmost match and returns:

| return | meaning |
|---|---|
| `1` | match found; if `caps != NULL`, `<PREFIX>_NCAPS` pairs are written, `caps[0]` the whole-match span (no second name for it) |
| `0` | no match; `caps` (if non-NULL) is left **untouched** — the `int` return alone communicates match/no-match |
| `<PREFIX>_ERR_STEPS` / `_FRAMES` / `_WORK` / `_RECURSE` | engine gave up (§4); `caps` also left **untouched**. `_RECURSE` is reserved with no producer yet ([DD-14] wave A, D71 item 1) |
| `PCREC_ERR_INTERNAL` | NOT a give-up (§4) — the artifact detected its own analysis/emission inconsistency (module `lookaround`'s negative-polarity end-check is the one producer today); `caps` left **untouched** like every other negative return ([DD-14] wave A commit 2, D71 item 1) |

Note that `0` here means **no match**, not a zero-length match. A
zero-length match is a success: it returns `1` with
`caps[0][0] == caps[0][1]`. (The anchored entries of §3.2/§3.3 use the
other convention, because their return value carries a length: there `0`
IS a zero-length match, and no-match is `-1`.)

`caps` may be `NULL` (existence-only search — every caller before M4.5
did exactly this, and the signature costs them nothing new).
`startpos > n` returns `0`. `^` anchors to absolute offset `0` regardless
of `startpos`. `s` may be `NULL` only when `n == 0`.

**Every offset written to `caps` is an ABSOLUTE offset into `s`, never
relative to `startpos`** — measured, and the property a find-all loop
depends on: searching `"xabcabcx"` for `abc` from `startpos = 0` reports
`[1,4)`, and the next search from `4` reports `[4,7)`, not `[0,3)`.

**`caps[0][0]` IS WHERE REPORTING BEGINS, WHICH IS NOT ALWAYS WHERE MATCHING
BEGAN** ([M6.2] wave E; `docs/design/assertions_design.md` §6). Without `\K`
the two coincide and nothing in this document had to distinguish them. `\K`
resets the reported start to wherever the winning path last crossed it, so on
`a\Kb` over `"ab"` the search consumes two bytes from offset 0 and reports
`[1,2)`. Three consequences a caller can see, all of them PCRE2's too:

- **`caps[0][0]` can be greater than the offset the match began at**, so it is
  not a bound on where the engine looked. Nothing in the find-all loop above
  depends on it being one — the loop advances off `caps[0][1]`, the match END,
  which `\K` does not touch.
- **`caps[0][0] == caps[0][1]` no longer implies nothing was consumed.**
  `ab\K` over `"ab"` reports `[2,2)` after consuming two bytes. The loop above
  is still correct — an empty REPORTED span at `p` advances by
  `<prefix>_next_pos`, and the next search starts past it — but a caller that
  measured work done by the reported width would measure zero.
- **The anchored entries of §3.2/§3.3 return the CONSUMED length**, which is
  the number that differs. On `ab\K` at `pos = 0` they return `2` while the
  span they report (§3.3) is `[2,2)`. That is deliberate and is what makes the
  §5 callout protocol's advance terminate; see those sections.

A pattern with no `\K` is unaffected in every respect: the construct is
module-gated (`assertions`) and, when present, forces the VM engine.

**The subject side of the contract.** `s` is `n` bytes and nothing more:
a `0x00` byte inside `s` is an ORDINARY byte with no special meaning (it
is only the *pattern* side, §7, that is NUL-terminated), and **the
matcher never reads `s[n]`** — there is no sentinel, so `s` need not be
NUL-terminated and need not have a readable byte after its end.
Measured on both engines with the subject in an exact-size heap
allocation under AddressSanitizer: `a.b` and `a(.)b` both match the
3 bytes `{'a', 0x00, 'b'}` (span `[0,3)`, group 1 `[1,2)`), and matching,
non-matching and `n == 0` searches over exact-size buffers are all clean.
The check is non-vacuous: the same probe compiled to read one byte past
the end (`n` overstated by one) fires a heap-buffer-overflow at the
matcher's own `memchr` prefilter.

#### Finding every match

This entry is ONE-SHOT: it finds the *first* match at or after
`startpos`. There is no batch find-all primitive and none is planned for
v1, so a caller wanting every match writes the loop — and the loop is
not simply "restart at the previous match's end", which spins forever
the first time a pattern matches empty (`a*` on `"bbb"` returns `[0,0)`
from `startpos = 0` for ever). The rule that terminates and is correct:

```c
size_t p = 0;
while (p <= n) {
    int r = <prefix>_search(s, n, p, caps);
    if (r != 1) break;                       /* 0 = done; < 0 = gave up (§4) */
    report(caps[0][0], caps[0][1]);
    p = (caps[0][1] > caps[0][0])            /* non-empty: resume at its end */
          ? (size_t)caps[0][1]
          : <prefix>_next_pos(s, n, (size_t)caps[0][0]);   /* EMPTY: next char */
}
```

**The empty-match advance rule**: a zero-length match is reported like
any other, and then the next search starts at the next CHARACTER boundary
past its start. Note that the advance is off the match's own START
(`caps[0][0]`), not off the loop variable — an empty match can be found at
a position later than the one searched from. The loop terminates because
`p` moves strictly forward every iteration (§3.1.1's contract makes
`<prefix>_next_pos` return a position strictly greater than the one it was
given) and `p > n` ends it.

That loop, coded exactly as written above, was compiled against real
artifacts and run against `python3 re.finditer` on twenty-six
(pattern, subject) pairs, on BOTH engines — each pattern compiled twice,
captures-on and `--no-captures`, for 52 runs. Twenty-two agree with
`re.finditer` span for span, including the three that motivate the rule:
`a*` over `"bbb"` → `(0,0) (1,1) (2,2) (3,3)`; `x?y` over `"yy"` →
`(0,1) (1,2)`; and alternations mixing empty and non-empty branches —
`a|` over `"bab"` → `(0,0) (1,2) (2,2) (3,3)` and `a|b*` over `"cbbac"` →
`(0,0) (1,3) (3,4) (4,4) (5,5)`. It also agrees on `a*`/`"aaa"`,
`a?`/`"aba"`, `b*`/`"abbbab"`, `(a|)`/`"xax"`, `a(b|)c`/`"acabc"`,
`(ab)*`/`"ababx"`, `a{0,2}`/`"aaaa"`, `[a-c]*`/`"xabcx"`, and on the ten
pairs added with this revision: `[0-9]+`/`"a12b345"`, `a{2,}`/`"aaaa"`,
`(?:ab|a)`/`"aab"`, `(a*)*`/`"aab"`, `.`/`"abc"`, `ab$`/`"xabab"`,
`^a`/`"aa"`, `c*` and `x` over the EMPTY subject, and `a`/`"a"`. The whole
set is `tests/encseam/findall_cases.txt` and it runs in `make test`, so
this measurement is a check now rather than a transcript.

**Where this loop is LOSSY, stated honestly.** It reports fewer matches
than PCRE2 and python `re` do for a pattern that *prefers* the empty
match at a position where a non-empty match also starts. Those engines,
on finding an empty match at `p`, RETRY at `p` with an
"empty match not permitted here" constraint (PCRE2 spells it
`PCRE2_NOTEMPTY_ATSTART`) and report the non-empty match too, before
moving on. **pcrec's entry points cannot express that retry** — there is
no "must not match empty here" mode on any of them — so the advance rule
above is the whole of what a pcrec consumer can do. Measured
divergences, all of this one class, and all of them OMISSIONS — the
protocol's spans are always a strict SUBSET of `re.finditer`'s, which the
suite checks rather than accepting any difference at all: `|a` over
`"aaa"` — this loop reports 4 spans `(0,0) (1,1) (2,2) (3,3)` where
`re.finditer` reports 7, adding `(0,1) (1,2) (2,3)`; likewise `a*?` over
`"aaa"` (4 vs 7), `a??` over `"aba"` (4 vs 6) and `b*?` over `"abba"`
(5 vs 7). Where the pattern's own preference picks a non-empty match
wherever one starts — all twenty-two agreeing cases above, including
every greedy quantifier among them — there is no divergence.

**This loop is what gives `\G` its meaning** ([M6.2] wave D;
`docs/design/assertions_design.md` §4.3). `\G` asserts that the current
position equals the `startpos` the call was given, so under the loop above
— which passes its resume position as `startpos` — it means **"contiguous
with the previous match"**, and that is exactly PCRE2's global-iteration
semantics, where each `pcre2_match` call advances `start_offset`. The two
agree with no work on either side, because this entry already takes the
parameter PCRE2 threads. `\G\w+` under this loop is therefore a
TOKENIZER — it reports `(0,2)` on `"ab ab ab"` and stops at the first gap
— where the `\G`-free `\w+` is a scanner and reports all three. Measured
by `tests/assertions/run_gstart_diff.sh` §1, against libpcre2 driven
through this same loop rather than against a hand-written span list.

**`\K` under this loop is safe and is worth one sentence, because the reason
is not the obvious one** ([M6.2] wave E). The loop advances off `caps[0][1]`
and `\K` moves only `caps[0][0]`, so termination and progress are untouched —
but a `\K` pattern CAN report an empty span after consuming bytes (`ab\K`
gives `[2,2)`), which takes the loop's EMPTY arm and advances by one character
from the REPORTED START rather than from the match end. MEASURED against
libpcre2 driven through this same loop rather than argued: `ab\K` over
`"ababab"` reports `2,2 6,6` from both — note what the empty arm costs, which
is that the match at offset 2..4 is not reported again at 4 — and `a\Kb` over
`"ababab"` reports `1,2 3,4 5,6` from both.
`tests/assertions/run_kreset_diff.sh` §5 is that comparison, run every
suite. It is also why the empty arm is written against `caps[0][0]` rather
than against the loop variable: the note above says an empty match can be
found at a different offset from the one asked for, and `\K` is the construct
that makes that routine rather than exotic.

Verified against the shipped emitter (`src/gen/emit_dfa.c`) and a fresh
artifact: the DFA matcher writes `caps[0][0]`/`caps[0][1]` only under
`if (caps)`, guarded exactly as documented, in the unanchored search
body. The `--emit-main` `main()` carries no such guard and needs none —
it passes a real array, never `NULL`.

#### 3.1.1 `<prefix>_next_pos` — the encoding residual

The loop's advance is not `+ 1`. It goes through a fifth exported entry,
which every artifact carries:

```c
size_t <prefix>_next_pos(const unsigned char *s, size_t n, size_t pos);
```

**This entry is the one place an artifact's byte-vs-character distinction
lives** ([M5-SEAM], `docs/dev/decisions.md` D58; the architecture is
`docs/dev/plan.md`'s `[DD-12]` row). An artifact embeds exactly one
encoding's residual block, chosen per compile call by
`pcrec_options.encoding` (§8.2) — never process- or file-globally, so two
differently-prefixed artifacts compiled for different encodings compose in
one translation unit exactly as §1 says they do.

The contract, quoted verbatim from a freshly emitted artifact (the
declaration and its own comment in a `-p rx` build of `'a(b|c)+d'`, no
elisions):

```c
/* rx_next_pos -- the ENCODING RESIDUAL entry (pcrec DD-12/D58).
 *
 * Returns the smallest position STRICTLY GREATER than pos that is a
 * CHARACTER BOUNDARY of this artifact's encoding, counting every position
 * >= n as a boundary. So the result is in (pos, n] whenever pos < n, and is
 * pos + 1 whenever pos >= n -- which is what lets a find-all loop advance
 * past a zero-length match and still terminate (see pcrec's
 * docs/spec/match_api.md S3.1, which writes that loop out).
 *
 * This entry is the ONE place an artifact's byte-vs-character distinction
 * lives. It reads s only at offsets in [pos, n), so the (s == NULL, n == 0)
 * subject rx_search accepts is legal here too, and it is never called from
 * this artifact's own engine: it is caller-facing residue, not hot-path
 * code.
 *
 * THIS artifact was compiled for the `byte` encoding, where one byte is one
 * character. An artifact compiled for another encoding exports this same
 * entry with that encoding's body and no caller loop changes. */
size_t rx_next_pos(const unsigned char *s, size_t n, size_t pos);
```

Four consequences a caller can rely on:

- **It is an ordinary extern function**, declared in the emitted header
  (or, in a self-contained artifact, in the `.c` beside the other four
  entries' declarations) and defined in the `.c`. Not a macro, not
  `static inline`: it is a caller-facing entry point, and it is declared
  where the other entry points are declared.
- **It never reads outside `[pos, n)`**, so the `(s == NULL, n == 0)`
  subject §3.1 already admits is legal here too. Under the byte encoding
  it does not read `s` at all.
- **`pos > n` is not an error** — the result is simply `pos + 1`. That is
  what lets the loop above terminate with no special case.
- **The result is always strictly greater than `pos`.**

**Under the byte encoding — the only one implemented today — the body IS
`pos + 1`**, and this is measurement, not intention. The whole definition,
verbatim from the same artifact:

```c
/* byte encoding: one byte is one character, so the next boundary after pos
 * is pos + 1 and the subject is never read. */
size_t rx_next_pos(const unsigned char *s, size_t n, size_t pos)
{
    (void)s; (void)n;
    return pos + 1;
}
```

**This resolves a caveat this section carried until [M5-SEAM], and the
history is worth keeping rather than deleting.** The loop's advance used
to be a literal `+ 1`, and this section warned that "`+ 1` advances one
BYTE … when module `utf8` lands at M5 this becomes the wrong advance for a
multi-byte character, and M5 owns sharpening it; a consumer writing
UTF-8-aware find-all today must advance to the next character boundary
itself." That obligation is discharged, and discharged in the direction
that costs the caller nothing: **the loop above is already final.** M5's
UTF-8 backend supplies a boundary-aware body for this same entry under
this same signature, and no caller's find-all loop changes a character —
which is the entire point of the residual seam. What a consumer must NOT
do is inline the `+ 1` back: that is the one edit that would make a
byte-compiled caller wrong against a UTF-8-compiled artifact. (The
caveat's other half — "the ASCII encoding, `PCREC_ENC_ASCII`" — is also
gone by rename: the constant is `PCREC_ENC_BYTE` and the CLI value is
`byte`, since the semantics were always "every byte is a character",
which is not what ASCII says. §8.2 records the rename.)

The complementary half of the seam is a NEGATIVE promise, and it is
enforced rather than asserted: **a residual entry is never called from the
artifact's own engine.** DD-12 (7) forbids the hot path depending on the
encoding; `tests/codegen/run_codegen_tests.sh` reads every emitted engine
body for a residual reference across six emission shapes in both artifact
forms; and the check is sabotage-validated
(`tests/mech/sabotages/S68_residual_in_hot_loop.sh` makes the emitted
bitmap prefilter's skip loop advance through `<prefix>_next_pos` — the
whole `.rxt` corpus stays green, because under this backend the two are
the same value, and only the structural check sees it).

### 3.2 `<prefix>_match` — the unconditional, anchored match-here entry

```c
ptrdiff_t rx_matchfn(const rx_ctx *ctx);   /* the shared type, §2 */
ptrdiff_t <prefix>_match(const rx_ctx *ctx);
```

**Matches at exactly `ctx->pos`: a match starting anywhere else is not
reported.** That is the semantic promise, and it is what a caller can
rely on; it is deliberately not a claim about how the artifact is built.
The two engines implement it differently — the VM emitter genuinely has
no search loop here, while the DFA emitter reaches the same answer by
running its ordinary search and rejecting any match whose start is not
`ctx->pos`. Both were measured to give the same answers; only the
promise above is contractual. One COST consequence of the DFA shape is
worth a caller's attention: on a FAILING match-here, the underlying
unanchored search does not know the question is anchored — it may skim
the remainder of the subject hunting a later match the filter will then
discard (the state-0 `memchr` skip keeps this a skim rather than a
per-byte walk), where the VM's anchored body fails at the first
divergent byte. A caller issuing many expected-to-fail `<prefix>_match`
probes against long subjects on a DFA artifact is in this entry's worst
case; the filed improvement (an emitted anchored automaton,
docs/dev/plan.md [ENG-ABS]) is evidence-gated and not scheduled.

Returns the matched
length (`>= 0`), `0` for a zero-length match at `ctx->pos`, `-1` on no
match, or a typed give-up code (§4). Delivers
**no captures** — `ctx->caps` is an *input* (§5), not an output channel,
and there is no parameter for `<prefix>_match` to write group offsets
into. Self-contained per its type's contract: a top-level caller passes
`ctx->ncap = 0, ctx->caps = NULL`.

### 3.3 `<prefix>_match_caps` — the anchored, capture-delivering entry

```c
ptrdiff_t <prefix>_match_caps(const rx_ctx *ctx, ptrdiff_t (*caps_out)[2]);
```

Same anchoring promise as `<prefix>_match`, plus a
capture-delivering output. On success, `caps_out[0..<PREFIX>_NCAPS-1]` are
all written (the same completed-match discipline as `<prefix>_search`),
`caps_out[0]` is `[ctx->pos, ctx->pos + length)`, and **`caps_out[k]` is
capturing group `k`** for `k >= 1`, in the pattern's own left-to-right
numbering, on any captures-on build. (`rx_group_entry.slot` exists for a
future in which a build delivers a *different* slot for a group; on
today's builds no such indirection is in play and the identity above is
what the examples in §5.1 rely on. **D61, 2026-08-18, narrows that
latitude: for the PRIMARY pattern's own groups on a captures-on build,
`slot == number` is PERMANENT — the different-slot latitude applies only
to future ref-bearing rows (§6), whose delivered slots APPEND after the
primary prefix and never displace slots `1..ngroups`.**)

**On failure, `caps_out` is untouched — and a give-up is a failure for
this rule.** Every negative return leaves the caller's array exactly as
it was; the generated source says so outright ("caps_out is UNTOUCHED on
every negative return, give-up included"). The same holds for
`<prefix>_search`'s `caps`.

`ctx->caps`/`ctx->ncap` are read as ordinary `rx_ctx` input
(unrelated to `caps_out`) — a top-level call passes `ncap=0, caps=NULL`
exactly like `<prefix>_match`.

Which entry a caller reaches for: no start position known and/or no
captures wanted → `<prefix>_search`; start position known, captures
wanted, no search loop wanted → `<prefix>_match_caps`; neither offsets
nor a loop wanted → `<prefix>_match`. The discriminator is whether the
start position is KNOWN, never whether captures are wanted:
`<prefix>_search` delivers full captures too when handed a `caps`
buffer (§3.1's table), so "first match plus its groups" is one
`<prefix>_search` call — `<prefix>_match_caps` is only for the anchored
case, and reaching for it because "captures" appears in its name is the
misreading this sentence exists to prevent.

**One caveat on that ergonomic framing**, because it invites reading the
three entries as interchangeable views of one answer: they are not, on
the give-up axis. §4's uniformity is about the CODE SPACE — which values
mean what — not about which entry gives up on a given input. Whether a
budget is exhausted is a property of the entry point, because the
entries do different amounts of work — and it goes BOTH ways. Measured,
`(a|aa)+b` built `--step-budget=3`: over `"aaaaaaaaaaaaaaaaaaaaX"`,
`<prefix>_search`
returns `0` (its DFA prefilter resolves the question definitively
without ever entering the VM) while `<prefix>_match` and
`<prefix>_match_caps` both return `-2`. And on the same artifact family
built `--backtrack-frames=1`, the reverse: over `"xxaaaaab"`,
`<prefix>_search` returns `-3` while both anchored entries return a
clean `-1`, because anchoring at position 0 fails immediately and never
spends a frame. A caller must therefore handle give-ups on whichever
entry it actually calls, and must not infer from one entry's clean
answer that another would give one.

### 3.4 `<prefix>_info` — the reflection structure

```c
extern const struct rx_info <prefix>_info;
```

One instance per artifact, link-time constant, no runtime cost to build
it. Full field list: §6.

**It is not, strictly, `.rodata`, and the difference is the one an
embedder targeting ROM or flash cares about.** `struct rx_info` holds
two pointers — `pattern` and `engine_why` — so the object needs
load-time relocation and the toolchain places it accordingly. Measured
with `readelf` on a default build of `'a(b|c)+d'`: `rx_info` is a
104-byte object in section `.data.rel.ro.local` (writable-then-read-only,
not `.rodata`), and that section carries exactly two `R_X86_64_64`
relocations, one per embedded string pointer. The strings themselves are
in `.rodata`. There is no run-time initializer and no constructor; the
cost is two relocations at load, not zero.

### 3.5 A design-vs-shipped note: give-up codes are uniform, not collapsed

`match_api_m4.md` §3 as originally written required `<prefix>_match` to
**collapse** every give-up code to a bare `-1` (D42.3's reservation on
the `rx_matchfn` type). **That collapse does not exist in the shipped
artifact**, on either engine. Both bodies, quoted from freshly emitted
artifacts:

```c
/* DFA artifact (--no-captures 'a(b|c)+d'), with its full comment: */
/* D49: the give-up codes PROPAGATE rather than collapsing to -1.
 * Unreachable on this engine — a DFA artifact has no counter to
 * exhaust — but written uniformly on purpose: the contract of
 * rx_matchfn is one contract, and a wrapper that discards codes it
 * merely happens never to see is the shape that goes wrong when a
 * later engine shares this emitter. */
ptrdiff_t rx_match(const rx_ctx *ctx)
{
    /* Initialized: gcc -O1 false maybe-uninitialized (pcrec K28). */
    ptrdiff_t caps[RX_NCAPS][2] = {{0}};
    int found = rx_search(ctx->subject, ctx->len, ctx->pos, caps);
    if (found < 0) return (ptrdiff_t)found;
    if (found != 1 || (size_t)caps[0][0] != ctx->pos) return -1;
    return caps[0][1] - caps[0][0];
}
```

```c
/* VM artifact ('a(b|c)+d' under -p r22a), where the codes are LIVE: */
ptrdiff_t r22a_match(const rx_ctx *ctx)
{
    r22a_work w;
    ptrdiff_t r;
    if (ctx->pos > ctx->len) return -1;
    r22a_work_init(&w);
    r = r22a_match_impl(ctx, &w, ctx->len);
    /* No translation and no clamp: the impl's return space IS this
     * contract's -- >= 0, -1, or one of the three R_ sentinels, which
     * are the ERR_ codes. A defensive floor test here would be dead
     * code pretending to be a safeguard. */
    return r;
}
```

**Both quotations matter, and quoting only the first would be a broken
check.** The DFA body's own comment says the propagation branch is
*unreachable on that engine* — a DFA artifact has no counter to exhaust
— so it is evidence that the emitter WRITES the propagation, not that
propagation ever happens. The live evidence is the VM: measured,
`(a|aa)+b` built `--step-budget=3` returns `-2` from `<prefix>_match`
and `<prefix>_match_caps`, and the same pattern built
`--backtrack-frames=1` returns `-3` from all three entries — including
`<prefix>_search` — on the subject `"ab"`. (The DFA body's second line,
`if (found != 1 || caps[0][0] != ctx->pos) return -1;`, is also the only
thing making that engine honor §3.2's anchoring promise — worth seeing
rather than eliding.)

**The initializer on `caps` is not padding, and it is quoted here because
it is in the artifact.** Added 2026-08-19 ([M6.2] repair slice, closing
`docs/dev/known_issues.md` K28): when the pattern's DFA is a single dead
state, `rx_search` always returns 0, gcc `-O1` inlines it, and then
reports this array as maybe-uninitialized even though the `found != 1`
short-circuit makes the read unreachable. The read really is unreachable
and the initializer really is never observed — it changes no answer — but
the artifact is source someone else compiles, and a consumer building with
`-Werror` sees a build failure. The same declaration and the same
initializer appear in `<prefix>_match_caps` and in the standalone
`main()`. Restructuring the test instead was measured NOT to silence the
report.

This is the shipped, correct state: `docs/dev/decisions.md` D49
supersedes D42.3 and rules the uniform-codes contract these artifacts
implement — `match_api_m4.md`'s own §3 carries the D49 amendment in
place. A caller that only tests `r < 0` for "did it match" is unaffected
either way; a caller doing an exact `== -1` comparison sees give-up
codes as distinct values, not folded into `-1`.

**An artifact generated before 2026-08-18 carries a comment that
contradicts all of the above, and a reader holding one needs to know
that.** Until that date, the emitted `rx_matchfn` ABI comment read
"Return values < -1 are RESERVED for a future abort semantic; no
pcrec-emitted matcher produces one today" — an affirmative false
statement about the artifact it sits in, which the measurements above
refute. **Where an old artifact's comment and this document disagree,
this document is the contract; the artifact's behavior always matched
this document, not its own comment.** This section as first written
(`[M4.7f]`) described that comment as merely *omitting* the give-up
codes, which was too generous by a wide margin, and §2 of this document
quoted a *corrected* version of that comment as though it were the
shipped text. Both were found by the R29 panel and fixed in the same
pass (`[M4.7g]`, 2026-08-18): the emitted comment now states the give-up
space (§2 quotes it verbatim), and `lib/pcrec.h`'s generated-searcher
comment, which had the same defect in its own words, now names the
negative return space too.

### 3.6 Whole-subject / end-anchored matching: the `(?:P)\z` idiom

**There is no native end-anchored entry — no `<prefix>_search`-style
call that means "match, and require the match to reach the subject's
own end".** §3.1–§3.3's three entries all answer "does a match exist
starting here", never "does a match exist covering here to `n`". A
caller that wants PCRE2's `PCRE2_ANCHORED|PCRE2_ENDANCHORED` regime — a
match that starts AND ends where asked — gets there by folding the
requirement into the PATTERN rather than by a fourth entry point:
compile `(?:P)\z` (the original pattern `P`, wrapped in a non-capturing
group, followed by `\z`) and call any of §3.1–§3.3 as usual.

**`\z`, not `$`.** `$` admits a trailing newline at the default options
(`(?m)` off), which is not "the subject's end" — verified live:
`(?:foo)$` compiled `--no-captures` matches `"foo\n"` at `[0,3)`, while
`(?:foo)\z` on the identical subject reports no match. `\z` is module
`assertions`' unconditional end-of-subject assertion (`docs/spec/
pcre2_compliance.md` and `tests/assertions/`) and admits nothing after
it; it is the only anchor of the three (`$`, `\Z`, `\z`) with that
property at default options.

**Why the naive alternative — run the ordinary anchored entry and test
`length == n` — does not work.** It is SUFFICIENT (a match that happens
to reach `n` really is end-anchored) but not NECESSARY (a match that
does not reach `n` does not prove no end-anchored match exists), because
leftmost-first preference picks the FIRST alternative that matches,
never the one that reaches farthest. Verified live: `a|ab` compiled
`--no-captures`, run anchored over `"ab"`, reports `[0,1)` — branch `a`
wins by leftmost-first preference and the naive test (`1 == 2`?) answers
NO. But `(?:a|ab)\z` over the same subject `"ab"` reports `[0,2)`: `\z`
forces backtracking past the `a` branch's failure (position 1 is not the
subject's end) into the `ab` branch, which does reach it. The naive test
would have wrongly concluded no end-anchored match exists; the idiom
does not, because it is the ENGINE doing the searching, not a caller
re-deriving what the engine already decided.

**This is a ruled-permanent idiom, not a stopgap awaiting a dedicated
generation axis.** `docs/dev/plan.md` row `[OS-4]` and
`docs/dev/decisions.md` D77 (2026-08-25): a whole-subject/end-anchored
generation axis (a single artifact answering both the ordinary and the
end-anchored question, or an emitted skip loop that can stop one byte
short for `\z`) is explicitly NOT being built now, on D77's own general
rule — *"no artificial timelines; when we would be better served
building something later under measurement, wait and see, and focus on
builds we will not have to rebuild or roll back."* The two-artifact cost
(one compile for the ordinary question, a second `(?:P)\z` compile for
the end-anchored one) and the final-byte DFA skip gap the idiom leaves
on the table are recorded as a general-optimization candidate should a
measurement ever justify it (`docs/dev/plan.md` `[DD-13]`) — this is not
scoped to any one caller, `(?:P)\z` benefits from it identically to
every other `\z`-bearing pattern.

**What the whole-subject artifact's own DFA stamps say (§6.3), verified
live.** The `\z` wrapper changes the emitted candidate-start filter, not
just the trailing assertion: on `(?:foo|bar)\z` (`--no-captures`),
`RX_DFA_SCAN` reads `"unanchored"` (the idiom does not anchor the
START, only the end) and `RX_DFA_PREFILTER` reads `"byte-class-bounded"`
— the bounded form §6.3 already documents for a `$`/`\Z`/`\z` view,
where a skip may not pass the position whose accept has not yet been
evaluated. `(?:foo)\z` (a single literal, no alternation) stamps the
matching single-candidate form, `"memchr-bounded"`. Neither idiom use
produces `RX_DFA_SCAN "attempt"` by itself — that shape is what a
LEADING `^`/`\A` selects (§6.3), an orthogonal axis the idiom does not
touch.

---

## 4. The give-up code space (D49)

**This section states the CODES; the numeric TRIGGER DEFAULTS — the step
and work budgets, the frame/trail capacities — are `docs/spec/limits.md`'s
own subject and are not restated here.** That document also carries the
compile-time state-count ceilings (a different "limit"), the two-tier
entry's cost model in numeric form, and the K33/K34 documented-divergence
detail; this section stays about which VALUE means what, at every entry,
uniformly.

`<prefix>_search`, `rx_matchfn` (hence `<prefix>_match` and any callout),
and `<prefix>_match_caps` all report engine give-up in the same CODE
SPACE: a negative return strictly below `-1`, with the same value
meaning the same thing at every entry. That uniformity is about the
codes, not about when a give-up happens — which entry gives up on a
given input is a property of that entry (§3.3's caveat, measured in both
directions).

**[OPT-1], 2026-08-25: THE STEP AND WORK BUDGETS BOUND ONE ATTEMPT, AND AN
UN-SUFFIXED ENTRY MAY MAKE TWO.** §10.9's tiered entry re-runs the match on
the stamped default after a `PCREC_ERR_FRAMES` give-up on its fast tier, with
both budgets **refilled** — which is what makes the answer identical to a
single-tier artifact's, and is stated there. The consequence belongs here: a
single call to `<prefix>_search`/`_match`/`_match_caps` can therefore spend up
to **twice** the step budget and twice the work budget before it returns. The
CODES are unaffected (a returned `PCREC_ERR_STEPS` still means the deep
attempt exhausted a full budget), and the `_in` entries, which have no tier,
are bounded by one budget as they always were. A caller that needs a hard
bound on the work ONE call may do uses `_in` or `-fno-tiered-entry`
(`tuning.md` §2.12).

```c
#define PCREC_ERR_STEPS    (-2)
#define PCREC_ERR_FRAMES   (-3)
#define PCREC_ERR_WORK     (-4)
#define PCREC_ERR_RECURSE  (-5)  /* [DD-14] reserved: no producer yet (D71 item 1) */
#define PCREC_ERR_FLOOR    (-5)  /* give-ups: [FLOOR,-2]; below: reserved (D49) */
#define PCREC_ERR_INTERNAL (-6)  /* [DD-14] below PCREC_ERR_FLOOR: NOT a give-up, D71 item 1 */
```

**[ABI-NS], 2026-08-18 (D60).** These four were spelled `<PREFIX>_ERR_STEPS`/
`_FRAMES`/`_WORK`/`_FLOOR` before this date, one set per artifact even
though every artifact emitted identical values. D60 ruled the values a
pcrec-CONTRACT fact, not a per-artifact one, and moved them unprefixed
into the shared `PCREC_RX_ABI_H` block (§2) — the per-`<PREFIX>` spelling
is DELETED, not aliased. The block above is quoted verbatim from a fresh
`-p rx --no-captures` build of `'a(b|c)+d'`; a `-p foo` build of the same
pattern emits the byte-identical lines (§1/§2's cross-prefix
identity property, now covering these constants too).

**[DD-14] wave A, 2026-08-24 (D71 item 1).** `PCREC_ERR_RECURSE` joins the
block and `PCREC_ERR_FLOOR` moves −4 → −5 — D49's own re-open clause
("getting the partition wrong pre-release costs a renumber and nothing
else"), exercised. The CODE is reserved now; the recursion-depth COUNTER
that would produce it is NOT in the default artifact (D71 item 1 — a
future `[V-H]` diagnostic-generation axis, a separate emitted variant, not
a runtime flag). No arm in any emitter returns `PCREC_ERR_RECURSE` today —
it is exactly as unreachable on every artifact as `PCREC_ERR_STEPS` etc.
are on a DFA-only one, the same "reserved but unreachable" shape.

**[DD-14] wave A commit 2, 2026-08-24 (D71 item 1). `PCREC_ERR_INTERNAL`
is BELOW the floor and is NOT a give-up.** D49 reserves everything
strictly below `PCREC_ERR_FLOOR` for "a future abort semantic"; this is
that semantic's first producer. It means the artifact detected its OWN
inconsistency — a compile-time width analysis (`pcrec_maxw`) disagreeing
with what the emitter actually walked — never a runtime resource
give-up. Its one producer today is module `lookaround`'s negative-polarity
lookbehind END-CHECK (`(?<!X)`): on that polarity a declined branch is the
assertion SUCCEEDING, so a width disagreement would be a FALSE MATCH, and
the hard return is what prevents it (never observed on a correctly
analyzed pattern — the check is provably redundant for the width class
this module ships and is emitted as a self-consistency guard anyway).
A TOP-LEVEL entry (`<prefix>_search`, `<prefix>_match`,
`<prefix>_match_caps`) still PROPAGATES `PCREC_ERR_INTERNAL` to its own
caller exactly like a give-up — it is not such an entry's job to trap on
its own return. "Composed call sites must trap below the floor", below,
is where the trap belongs.

Verified against both a DFA-only artifact (`--no-captures`, no counter
exists, these codes are reserved-but-unreachable) and a captures-default
VM artifact (`RX_STEP_BUDGET`/`RX_WORK_BUDGET`/`RX_BT_FRAMES`/
`RX_TRAIL_FRAMES` macros present, the counters live). A DFA-compiled
artifact never RETURNS one of these codes — it has no counter to
exhaust — but it does EMIT them: the constants are defined in every
artifact, and a DFA artifact built `--emit-main` even emits the full
three-way handler text for them (measured: `if (rc == PCREC_ERR_STEPS)`,
`PCREC_ERR_FRAMES`, `PCREC_ERR_WORK` all present in a `--no-captures
--emit-main` build). That is deliberate, and it is what lets a caller's
`switch` written today survive a later compile of the same pattern
selecting the VM.

**Composed call sites must trap below the floor.** Every generated call
site that invokes an `rx_matchfn` (a callout, a composed submatcher) must
enforce `if (ret < PCREC_ERR_FLOOR) __builtin_trap();` — this binds
call sites that call *into* another `rx_matchfn`, not an exported entry's
own internal `return`. No such call sites are emitted by pcrec today
(callout code generation has no producer yet); the obligation is recorded
here for whichever future work (callouts, composition) first emits one.
`PCREC_ERR_INTERNAL` now gives that future trap a real value it would
actually fire on — trapping on it there IS the design, not a gap.

**`PCREC_ERR_FRAMES` names a RESOURCE, not an array and not an owner.**
Two distinct capacities can exhaust and both report this one code: the
resume stack (`<PREFIX>_RESUME_FRAMES`) and its sibling undo trail
(`<PREFIX>_TRAIL_FRAMES`). Which one ran out is not reported, and a caller
must not assume it was the one whose macro is named "frames" — MEASURED on
`^(a(?1)?b)$`, the artifact gives up with the trail full and TWO THIRDS of
its resume stack still unused (`docs/design/frame_buffer_design.md` §4). The same
code, with the same meaning, covers a caller-supplied buffer
([DD-14.FB], §10.3) — and there too it does not say whose buffer it was.

**Today's `1`/`0` contract for `<prefix>_search` is unchanged** — this
reservation adds give-up outcomes, it does not renumber match/no-match.
It does mean the return is not two-valued, so `if (<prefix>_search(...))`
reads a give-up as a match: test `== 1` for "matched" (§3.1).

---

## 5. Capture-slot semantics

```c
const ptrdiff_t (*caps)[2];         /* rx_ctx field; half-open [start, end) pairs */
#define <PREFIX>_NCAPS <n>          /* per-artifact, compile-time constant */
#define PCREC_UNSET ((ptrdiff_t)-1) /* pcrec-contract, unprefixed (§2); D60 */
```

**[ABI-NS], 2026-08-18 (D60).** `PCREC_UNSET` was spelled `<PREFIX>_UNSET`
before this date — one identical value emitted once per artifact, moved
unprefixed into the shared `PCREC_RX_ABI_H` block (§2) since it is a
pcrec-contract fact, not a per-artifact one. The per-`<PREFIX>` spelling
is DELETED, not aliased. `<PREFIX>_NCAPS` is unaffected: its VALUE
genuinely varies per artifact (below), so it stays per-prefix.

- **Unset representation:** `{-1, -1}` in **both** slots of a pair.
  `caps[k][0] < 0` is a sufficient unset test.
- **Index 0 is always the whole match.** `<PREFIX>_NCAPS >= 1` always.
- **`<PREFIX>_NCAPS` is a property of the compiled ARTIFACT, not of the
  pattern text.** A DFA-compiled artifact — capture-bearing pattern or
  not — always emits `<PREFIX>_NCAPS 1`; `<PREFIX>_NCAPS > 1` implies the
  VM engine was selected. Verified: `'a(b|c)+d'` compiled `--no-captures`
  emits `RX_NCAPS 1` with `rx_info.ngroups == 1` (the pattern *has* a
  group; the artifact delivers no slot for it); the same pattern compiled
  with captures on (the default since M4.5) emits `RX_NCAPS 2`.
  `rx_info.ncaps == <PREFIX>_NCAPS` always (a structural invariant of the
  build).
- **Every pair `0..<PREFIX>_NCAPS-1` is written on a completed match** —
  no watermark needed at read time once a match succeeds.
- **On a failed match, the caller's array is left untouched — and an
  engine GIVE-UP is a failure for this rule.** Every negative return
  from an anchored entry, and a `0` or a give-up code from
  `<prefix>_search`, leaves the array exactly as the caller left it. No
  attempt is made to write `{-1,-1}` into it; the `int`/`ptrdiff_t`
  return value alone communicates failure. The generated source states
  the give-up half outright ("caps_out is UNTOUCHED on every negative
  return, give-up included").
- **Caller-owned, fixed-size, compile-time-sized**: a caller declares
  `ptrdiff_t caps[<PREFIX>_NCAPS][2];` on the stack. Nothing in the
  generated contract allocates.
- **`ctx->caps`, handed to a callout mid-match, is valid for the
  duration of that one call only.** The engine rewrites the same storage
  afterward (trail-based undo); a callout that retains the pointer past
  its own call and reads it later is the embedder's bug, not a pcrec
  contract violation.
- **A completed match's `caps` are stable until the next match call
  reusing the same buffer** — the matcher may overwrite the buffer
  between separate calls, but never mid-splice.

### 5.1 What a written slot's value actually means (the R22 rules)

C6 above says every slot `0..ncaps-1` is written on a completed match; it
does not by itself say *which* value a group inside a repeated construct
ends up holding when that group did not run in every iteration. Two rules
govern this, measured three-way unanimous (python `re`, libpcre2, and
pcrec agree) and now part of the shipped contract, not an addendum to it:

1. **Cross-iteration retention.** A group inside a quantifier whose
   subexpression did not run in the *final* iteration retains its value
   from the last iteration in which it *did* run. `((a)|(b))*` matched
   against `"ab"` reports group 2 as `[0,1)` — not unset — because group
   2 ran on the first iteration even though the second iteration took the
   other alternative. Unset means "never participated in the whole
   match", not "didn't participate in the match's last iteration".
2. **An empty final iteration still overwrites.** `(a*)*` and `(a?)*`
   matched against `"aaa"` both report group 1 as `[3,3)` — an empty
   iteration's write is a write, even though it contributes no bytes.

A caller reading `caps[k]` after a successful match therefore never needs
to reason about *which* iteration produced the value; both rules above
are already applied by the time the match completes, and the slot either
holds the group's last-executed span or is genuinely unset (the group
never ran at all, in any iteration, anywhere in the match).

### 5.2 Explicit non-requirements

The following are deliberately **not** part of this contract. Every item
here is scoped to the MATCH path — the generated matcher and its
caps buffers. The pcrec LIBRARY's own compile path does allocate and
does have a lifecycle to manage; that is §8's `pcrec_output` /
`pcrec_output_free`, and nothing here excuses skipping it.

- No ovector sizing negotiation — the group count is a compile-time fact.
- No match-data object, no allocation, no lifecycle to manage.
- No run-time "does group N exist" query (a compile-time check, if
  needed, is the caller's own business).
- No run-time name lookup for template resolution (a future substitution
  compiler resolves `${name}` at pcrec-compile time).
- No partial-match or streaming window state.
- No callout/callback context beyond what `rx_ctx` itself carries — a
  callout binding's `user` data lives entirely in the `rx_callout_ref`
  the binding declares; nothing about *which* callout is firing is
  visible to `rx_matchfn`'s own signature.

### 5.3 Concurrency: a generated matcher is reentrant and thread-safe

**A generated matcher holds no mutable state of its own.** Every entry
point's working state lives in its own stack frame and in the caller's
`caps` buffer; the tables, bitmaps and the `rx_info` instance are
`const`. Therefore:

- Any number of threads may call the same artifact's entry points
  concurrently, **provided each call has its own `caps`/`caps_out`
  buffer** (which the caller owns and declares, per the rule above).
  Sharing one buffer between concurrent calls is a data race in the
  CALLER's code, not something the matcher serializes for it.
- The same holds for one thread re-entering a matcher (from a callout,
  say), subject to the same distinct-buffer rule.
- `<prefix>_info` is read-only and may be read from anywhere at any time.

**This is a CONTRACT, binding on future emitters, not merely an
observation about today's output.** It is what makes a generated matcher
usable from a thread pool at all, and an engine that wanted a mutable
scratch buffer would have to change this document first.

**One thing this section promises that a THREAD-STACK-SIZED caller cannot
currently collect, stated because a reader will otherwise discover it as a
crash.** "Any number of threads may call the same artifact's entry points"
says nothing about how much STACK each such call needs, and for one
artifact class the answer is large: an artifact whose frame requirement is
not statically bounded declares its whole run state as a local of the entry
it was called through. MEASURED on a `-p rx --features all` build of
`^(a(?1)?b)$` — `<prefix>_search`'s stack frame was **131,216 bytes**, which
does not fit a musl-default 128 KB thread stack, and calling it from such a
thread faulted on any subject, a 2-byte one included. A statically-bounded
pattern pays nothing (`a(b|c)+d`'s entry is 208 bytes) and a glibc-default
8 MB main thread is unaffected.

**[OPT-1], 2026-08-25: THAT MEASUREMENT NOW READS DIFFERENTLY, and the
limitation NARROWS rather than closing.** §10.9's tiered entry moves the
stamped default storage off the entry's own frame and onto a
non-inlined internal function only a `PCREC_ERR_FRAMES` give-up reaches. Re-MEASURED on the same
build: `<prefix>_search`'s frame is **3,184 bytes** and the internal
function's is 131,216. So on a musl-default 128 KB thread that artifact now
**matches every subject the fast tier holds** — the "faults on any subject,
a 2-byte one included" sentence is no longer true — and faults only on one
deep enough to escalate. **The remedy is still `_in`**, and it is still the
only way to get a guarantee: which subjects escalate is a property of the
pattern and the subject, not something a caller can bound in advance.
`docs/dev/known_issues.md` K33 carries the narrowed statement, and
`tests/thread/run_stackdepth_tests.sh` pins both halves — the small entry
frame, and the deep tier still dying.

**The remedy SHIPS: it is §10's `_in` entries** ([DD-14.FB], D71 item 2),
whose own frame MEASURES **144 bytes at -O2** — 312 including the two
statics they call through, and 224 at -O3, where gcc inlines the statics into
both entries (the 131 KB of default storage still never reaches the `_in`
entry, which is the property that matters). A caller on a small thread stack supplies its own
storage and the arrays are not on that stack at all; a caller who cannot
must still size the thread for the artifact or compile with a smaller
`--backtrack-frames`. **The default path is unchanged and still does not
fit**, deliberately: D73 keeps the stamped 2048/3072 on the reasoning that
the caller buffer is the way around it, so this remains a live limitation
for a caller who calls the un-suffixed entry from a small-stack thread —
`docs/dev/known_issues.md` K33. `docs/design/frame_buffer_design.md` §3
carries the design's measurements and
`tests/thread/run_stackdepth_tests.sh` reproduces both halves on every
run: the default entry dying on a 128 KB thread, and `_search_in`
matching the same subject on the same thread.

It is also GUARDED rather than asserted, by two shipped checks that run
in `make test`:

- **TS-1** (D19) is static: it scans every emitted file across nine
  emission shapes and fails on any non-const static object, or any
  reference to a non-reentrant or allocating libc symbol.
- **TS-2** is dynamic and runs under ThreadSanitizer: eight threads
  share ONE compiled matcher and search DIFFERENT subjects
  concurrently, across five patterns chosen to hit five differently
  *shaped* emitted engines, and every threaded result must equal a
  single-threaded baseline recorded before any thread was spawned.
  **Its sabotage arm proves the detector is watching** — a planted race
  in a scratch copy of the driver must be caught, or the check fails
  itself.

The library side has the same treatment: **TS-3** runs eight threads
each compiling its own pattern through `pcrec_compile()` concurrently,
byte-matching a single-threaded baseline, also TSan-instrumented and
also sabotage-validated. So `pcrec_compile()` is safe to call
concurrently too, which §8 assumes and this is the evidence for.

---

## 6. `rx_info` — the reflection structure

```c
struct rx_info {
    unsigned      abi;             /* layout version; bump-on-change */
    uint64_t      flags;           /* PCREC_* option bits, exactly as compiled */
    int           encoding;        /* PCREC_ENC_* */
    int           ncaps;           /* == <PREFIX>_NCAPS: this artifact's
                                       caps[] slot count, all-in */
    int           ngroups;         /* capturing groups in the PATTERN
                                       TEXT — a lexical fact, independent
                                       of --no-captures and of engine
                                       selection */
    int           nnames;          /* entries in groups[]: NAMED groups
                                       only. 0 until module 'named-groups'
                                       lands (still true as of this
                                       writing — verified: '(?<g>a)' still
                                       refuses "requires module
                                       'named-groups'") */
    unsigned      engine;          /* PCREC_ENGINE_DFA=1 /
                                       PCREC_ENGINE_VM=2 */
    int64_t       step_budget;     /* -1 = none */
    int64_t       work_budget;     /* -1 = none; the THIRD bound (D47
                                       SECOND ADDENDUM): forward work the
                                       fail label never sees, counted
                                       separately from step_budget */
    int64_t       frame_capacity;  /* -1 = unbounded. NOTE the sentinel
                                       is NOT the one the same-named
                                       pcrec_options field uses — see
                                       the asymmetry note below */
    int64_t       subject_ceiling; /* 0 = unset/not applicable; else the
                                       stamped honest ceiling for a
                                       residually-unbounded capture body */
    int64_t       resume_frames;   /* [DD-14.FB] the stamped DEFAULT
                                       resume capacity, in frames;
                                       0 = this artifact has no resume
                                       stack (every DFA artifact) */
    int64_t       trail_frames;    /* ditto, in trail entries */
    int32_t       resume_frame_size; /* bytes per resume frame, THIS
                                       artifact; 0 on a DFA artifact */
    int32_t       trail_frame_size;  /* bytes per trail entry */
    const char           *pattern;      /* source pattern text, as given
                                            to pcrec_compile() */
    size_t                pattern_len;  /* companion length — see §7 */
    const rx_group_entry *groups;       /* NULL until the pattern text
                                            declares at least one named
                                            group; sorted by NAME (strcmp)
                                            when non-NULL — see below */
    const char           *engine_why;   /* forcing construct/reason, or
                                            NULL; also carries a prefilter
                                            note on hybrid-eligible
                                            artifacts */
    const char           *scan;         /* [DD-13c] the DFA scan this
                                            artifact CONTAINS: "unanchored"
                                            / "attempt" / "empty", mirroring
                                            <PREFIX>_DFA_SCAN. NULL when it
                                            contains none */
    const char           *prefilter;    /* [DD-13c] this artifact's
                                            candidate-start mechanism, in
                                            whichever engine's vocabulary
                                            applies. Never NULL */
};
```

**[DD-13c], 2026-08-25 (D40 addendum) — `scan` and `prefilter`: THE SELECTION
FACTS GET RUNTIME MIRRORS.** §6.3's two DFA-scan macros are preprocessor-only,
and the consumer least able to read a preprocessor macro is exactly the one
most likely to want these facts: a `dlopen`ing host, an FFI or `ctypes`
binding, a tool walking several `<prefix>_info` symbols in one linked image.
Those consumers already read `engine` and `engine_why` here; they can now read
the scan facts the same way. **The two fields are APPENDED AT THE END of the
struct**, after the three pointers, so no existing member's offset moves —
`abi` still bumps (5 → 6), because the struct GREW, but this is a smaller kind
of event than abi 2's inserted `work_budget` or abi 3's inserted sizing block,
both of which moved every following offset.

**THE RULE, exactly** (`tests/codegen/run_dfa_stamps.sh` asserts every line of
it over the whole corpus, on both engines):

| artifact | `scan` | `prefilter` |
|---|---|---|
| DFA artifact | `"unanchored"` / `"attempt"` / `"empty"` — the value of `<PREFIX>_DFA_SCAN` | the value of `<PREFIX>_DFA_PREFILTER`: one of the five in §6.3 |
| VM artifact, HYBRID | the same three values, describing the DFA scan the artifact INLINES | the same five values, describing that inlined scan's own filter |
| VM artifact, non-hybrid | `NULL` — there is no DFA scan in this artifact | `"none"` — the VM's own vocabulary (`<PREFIX>_VM_PREFILTER`'s value on exactly these artifacts) |

Three consequences a consumer can rely on, and they are the reason the rule is
worth stating rather than inferring:

1. **`prefilter` is never `NULL`.** Every artifact has an answer to "what
   candidate-start mechanism do you carry", including "none".
2. **`scan != NULL` on a VM artifact IS "this is a hybrid".** That is the
   runtime reading of `<PREFIX>_VM_PREFILTER "hybrid"`, which had no `rx_info`
   mirror at all before this date.
3. **The string `"hybrid"` never appears in `prefilter`.** It is in the VM's
   vocabulary, but an artifact that would say it reports its inlined scan's
   ACTUAL mechanism instead — strictly more information, and consequence 2 is
   how the coarser fact is still readable. A consumer that wants the coarse
   answer tests `scan != NULL`, not `strcmp(prefilter, "hybrid")`.

**ONE DERIVATION, TWO SPELLINGS.** The field and the macro are written from the
same pair of emitter functions and from nowhere else, so they cannot report
different answers unless the emitter is wrong about both — which is what makes
"field == macro" a check of the compiler rather than of arithmetic, and it is
asserted on every compiled artifact of both engines.

**[ABI-NS], 2026-08-18 (D60 addendum): `engine`'s number-only contract now
has names.** Until this date, this field's comment read "1 = DFA, 2 = VM.
The artifact spells these ENGM_DFA/ENGM_VM in a COMMENT only — no such
constant is #defined anywhere, so compare against the numbers" — a
COMMENT-only convention naming the internal `select_engine.c` enum
spelling (`ENGM_DFA`/`ENGM_VM`), never an emitted symbol. D60's addendum
ruled this the same class of pcrec-contract fact as the give-up code
space (§4) and `PCREC_UNSET` (§5): a universal, artifact-independent
value with no emitted name, which its membership rule closes. `PCREC_ENGINE_DFA`

(1) and `PCREC_ENGINE_VM` (2) are now real `#define`s in the shared
`PCREC_RX_ABI_H` block (§2), pinned to the numbers the field already
stamped — this NAMES the existing contract, it does not renumber it. The
internal `ENGM_*` enum stays internal and is never exported; the emitted
`.engine` comment now reads `PCREC_ENGINE_DFA=1 / PCREC_ENGINE_VM=2` as
quoted above, verbatim from a fresh build.

`ngroups`, `ncaps`, and `nnames` are three genuinely different counts and
do not, in general, coincide: `ngroups` is a fact about the pattern's own
text; `ncaps` is a fact about what *this build* delivers (pinned to `1`
on any DFA-compiled or `--no-captures` build regardless of how many
groups the text has); `nnames` is the length of the (currently always
empty) named-group index. Verified: the `--no-captures 'a(b|c)+d'` build
above has `ngroups=1, ncaps=1`; the captures-default build of the same
pattern has `ngroups=1, ncaps=2`.

**`ngroups` is additionally a PERMANENT PREFIX-LENGTH promise (D61,
2026-08-18; advisory forward promise — no emitted text changes with
it).** On any captures-on build, slots `1..ngroups` of the caps array
are THIS pattern's own groups in its own left-to-right numbering, so
`ngroups <= ncaps - 1` with equality on every build pcrec emits today.
Slots above `ngroups` are reserved for future insertion/composition
mechanisms: a ref-bearing producer (§2's "labeled insertion path")
APPENDS its delivered slots and never interleaves with or renumbers the
primary prefix. A caller indexing `caps` by the pattern's own group
numbers is therefore safe against every future insertion feature. The
promise pins the caps LAYOUT, not group NUMBERING —
`rx_group_entry.slot` remains the number-to-slot indirection for
whatever numbering a future insertion design chooses (§3.3's narrowed
latitude note).

`pattern` is embedded unconditionally as an escaped C string literal
(`"`, `\`, and control bytes are escaped — an unescaped pattern
containing `"` would otherwise emit a syntactically broken `.c` file;
verified the emitter carries a dedicated string-literal escaper distinct
from the `/* ... */`-comment escaper used elsewhere in the file).

`groups`/`nnames` stay `NULL`/`0` for a pattern with no named group, and
for every pattern until module `named-groups` is enabled (`--features
named-groups` or a named set that includes it) — verified live:
`'(?<g>a)'` still refuses with `requires module 'named-groups'` against
the bare default. **[M6.3], 2026-08-18 — the sort key, previously left
open, is fixed FOR EVERY ROW THIS MODULE CAN PRODUCE TODAY: `strcmp` on
the NAME, byte-exact and CASE-SENSITIVE** (measured, both oracles:
`(?<name>a)(?<NAME>b)` is two distinct groups under libpcre2 10.46 and
python3 `re` alike, unchanged under `(?i)`/`PCRE2_CASELESS` — caseless
folds MATCHING, never name identity, and this key applies no fold
either). This matches libpcre2's own `PCRE2_INFO_NAMETABLE`, which is
sorted the identical way — measured directly
(tests/probes/probe_named_groups.c: a pattern declaring
`zeta`/`alpha`/`mu` by opening-paren order reports its table back in
`alpha`/`mu`/`zeta` order), the evidence behind this choice
(docs/dev/decisions.md D59) rather than an invented pcrec-only
convention.
**[M6.5.2], 2026-08-22 — superseded for duplicated names: the key is now (name asc, number asc); see §6.0.**

**This does not fix the key for `ref`-bearing rows, and that is
deliberate.** Every row this module produces has `ref` NULL/empty (§2's
"the primary's own groups"); a future producer of NON-empty `ref` (§2's
still-unproduced "labeled insertion path") makes the table's effective
key the COMPOUND `(ref, name)`, and where such a row sorts relative to
the primary's own is left OPEN by this revision, exactly as `ref`
itself was left open until a producer needed it — a name-only
invariant stated unconditionally here would silently foreclose that
future producer's own design question. Quoted verbatim from a freshly
emitted `-p rx --features named-groups` build of `'a(?<b>b|c)+d'`:

```c
static const rx_group_entry rx_group_names[] = {
    { "b", 1, 1, NULL },
};
```

and the `rx_info` instance's own two fields, from the same artifact:

```c
    .ngroups = 1,
    .nnames = 1,
    ...
    .groups = rx_group_names,
```

The array's own C identifier (`rx_group_names` above, under the default
`--prefix rx`) is `<prefix>`-scoped like every other per-artifact symbol
(§1) — it is not one of the six fixed-literal ABI types, only the ENTRY
type (`rx_group_entry`) is. Each entry's `slot` field is the group's
capture-slot index when this build actually delivers one (a
captures-wanted build; a named group's presence already forces the VM
through the pre-existing generic capture-forcing engine-selection rule,
so this is never observably a DFA artifact with a live slot) and `-1`
otherwise — verified: the same pattern compiled `--no-captures` stamps
`{ "b", 1, -1, NULL }` and selects the DFA engine (`.engine = 1`).

**Two more reflection facts are weaker than they look**, and the
difference from a shipped guarantee matters to anyone writing code
against them:

- **`rx_ctx.ncap`'s "watermark mid-match" reading has no producer.**
  (It is an `rx_ctx` field rather than an `rx_info` one, but it belongs
  with these.) Every call site in every emitted artifact sets
  `ctx.ncap = 0`; nothing ever advances it, so no caller can observe a
  watermark. It is reserved for a future mid-match view, exactly as
  `nnames`/`groups` are reserved for `named-groups`.
- **`rx_info.abi` is `6` on every artifact today ([DD-13c] bumped it from 5,
  which was [OPT-1]'s two-tier entries), and is not yet a
  compatibility promise.** Being pre-v1 (§9), it is a layout version and
  nothing more: do not build version negotiation on it until v1 declares
  what a bump means. It moved `2` → `3` at [DD-14.FB] (§10.4), which
  inserted the four sizing fields after `subject_ceiling` and therefore
  moved every following offset — which is exactly what this member exists
  to announce. It moved `3` → `4` at [DD-13] (§6.3), which added the DFA
  artifact's three selection stamps. **THAT SECOND BUMP MOVED NO STRUCT
  OFFSET**, and the number still had to move: D76 rules `abi` the version
  of the EMITTED SCAFFOLDING as a whole, not of `struct rx_info` alone,
  because the thing it protects is
  `tests/codegen/run_recursion_identity.sh`'s whole-file comparison (B) —
  which a new `#define` line breaks exactly as a moved offset would. A
  bump is therefore always paired with a re-pin of that comparison to the
  change's last `src`-touching commit, in the same change.

  It moved `4` → `5` at [OPT-1], the two-tier default entries — the first
  bump at which NO DFA artifact's bytes moved at all, since the tier is
  emitted only by the VM path. And it moved `5` → `6` at [DD-13c], which is
  the first bump that is BOTH kinds of event at once: emitted scaffolding
  (the `"empty"` scan value, and the two `_DFA_*` lines every VM hybrid
  gained) AND a real struct change — `scan` and `prefilter`, appended at the
  END so that, unlike [DD-14.FB]'s insertion, **no existing member's offset
  moves**. It is also the mirror image of [OPT-1]'s: that bump reached VM
  artifacts only, this one reaches both kinds.

**What a caller may assume, stated once in caller terms rather than left
to accumulate from six bump-event paragraphs (D76, D40 regime 1).** The
paragraph above narrates each bump's OWN cause; this is the general rule
those events are instances of. **What changes at a bump:** `abi`
(`rx_info.abi`, mirrored nowhere else) is the version of the emitted
SCAFFOLDING AS A WHOLE — every declaration, comment and macro in the
artifact, not merely `struct rx_info`'s own layout — so a change to any
of it, whether or not a struct offset moves, IS an `abi` bump; [DD-13c]'s
`3` → `4` (§6.3's two new stamp lines, no struct offset) and [DD-13c]'s
own `5` → `6` (both a struct append AND new stamp lines) are the two
ends of that range, and neither is a smaller event than the other by
this document's own promise. **What is fixed within one `abi` number:**
the emitted output is byte-exact WHOLE-FILE for a given pattern, prefix
and option set — comments included — which is what `abi` exists to let
a caller detect the boundary of; a caller diffing two artifacts compiled
at the same `abi` and finding them to differ has found a pcrec bug, not
an expected drift. **What a bump does NOT carry, pre-v1:** no
compatibility story and no announcement beyond the stamp itself — D40
regime 1 rules pre-v1 breaks unconstrained in substance, and for an
`abi` bump specifically the bumped NUMBER already discharges D37's
announced-boundary requirement; there is no separate deprecation cycle,
migration note, or advance notice to expect. A caller that wants
version-negotiation semantics from `abi` is building on a promise this
document does not make until a future v1 declaration says otherwise (§9).

**`frame_capacity`'s sentinel asymmetry.** The field name appears on
both sides of the API with different sentinels, and neither side is
wrong — they answer different questions. On the INPUT side,
`pcrec_options.frame_capacity == 0` means "let the compiler size it"
(and a positive value is a request). On the OUTPUT side,
`rx_info.frame_capacity == -1` means "no bound at all" — which is what a
DFA artifact stamps, having no resume stack to bound (measured:
`.frame_capacity = -1` alongside `.step_budget = -1` and
`.work_budget = -1` on a `--no-captures` build). `0` is not a legal
output value and `-1` is not a legal input value. §8 restates this at
the options side.

### 6.0 Duplicate-name runs — the sort key and the caller's algorithm ([M6.5.2], 2026-08-22)

**The sort key is (name asc, number asc).** [M6.3] fixed it as `strcmp` on the
NAME "for every row this module can produce today" — a name-only key, written
when duplicate names were impossible. Module `backrefs` ships `(?J)`, so a name
may now label a RUN of rows; within a run the rows are ordered by ASCENDING
group number, and that tiebreak is a CORRECTNESS requirement, not a
reproducibility nicety: `mod_named_groups.c` PREPENDS declarations and the
emitter walks from the head, so a name-only comparator on a stable sort yields
DESCENDING numbers within a run and the algorithm below would select the
wrong member. The emitted comparator is `src/gen/emit_dfa.c`'s `ng_cmp_name`;
`tests/codegen/run_codegen_tests.sh`'s `[M6.5-DUPNAMES]` check reads the rows
off the artifact and asserts them STRICTLY increasing in (name, number) — the
strictness is the comparator-totality half. Sabotage S120 removes the tiebreak.

**The caller's algorithm for a name that may be duplicated.** `bsearch` by
name returns SOME row of the run; walk BACK to the run's first row (the
previous row with a different name, plus one), then FORWARD to the first row
whose slot PARTICIPATED in the match (both offsets set). That row is the
group a by-name reference resolved to — PCRE2's documented "first of the set
that is set" rule, measured (backrefs design §8.3: first of the name-run by
ascending number that is SET, where "set" includes set-to-empty) — and it is
the SAME algorithm the emitted `\k<name>` resolution uses, so the caller and
the matcher cannot disagree about which member a name meant. A run none of
whose members participated is an unset name.

### 6.1 `rx_info` is link-time, not runtime, data

It is **not** part of `rx_ctx` or any callback parameter — a caller
reads `<prefix>_info` by symbol, once, at whatever point it wants the
artifact's own facts about itself (option flags, which engine, the
budgets it was built with, its own source pattern text). Its section
placement is `.data.rel.ro.local` rather than `.rodata`, for the reason
§3.4 measures.

### 6.2 Second-count example, worked

`'a(b|c)+d'` compiled `--no-captures`: `ncaps=1, ngroups=1` — the pattern
*has* a group, the artifact delivers no slot for it, and a reader who
only checked `ncaps` would wrongly conclude the pattern has no groups at
all. The two facts coincide only when `ncaps - 1 == ngroups`, i.e. a
VM-compiled, captures-on artifact — the common case since M4.5, not a
rule `rx_info` restates for every build.

### 6.3 The compile-time mirror: observability macros

An artifact also carries compile-time macros, for a caller that wants to
`#if` on a fact rather than read a struct field at run time — D46's
"every strategy selection point must be observable" requirement. Two
scoping facts first, because both are easy to get wrong and neither is
guessable:

**The mirror is PARTIAL — on a VM artifact six of `rx_info`'s fifteen
fields have a macro, and nine do not.** The six that mirror are `ncaps`
(`<PREFIX>_NCAPS`), `engine` (`<PREFIX>_ENGINE`, as the string `"vm"`),
`engine_why` (`<PREFIX>_ENGINE_WHY`), `step_budget`
(`<PREFIX>_STEP_BUDGET`), `work_budget` (`<PREFIX>_WORK_BUDGET`) and
`frame_capacity` (`<PREFIX>_BT_FRAMES`). The nine with no macro at all
are `abi`, `flags`, `encoding`, `ngroups`, `nnames`, `subject_ceiling`,
`pattern`, `pattern_len` and `groups` — including `ngroups`, which is
exactly the count §6.2 works hardest to distinguish from `ncaps`, and
which is therefore reachable only by reading `<prefix>_info` at run
time.

**[DD-13], 2026-08-25: THE D46 FAMILY SPLITS IN TWO, and only one half is
engine-scoped.**

- **(a) SELECTION FACTS are UNCONDITIONAL.** Which engine an artifact is,
  and which CANDIDATE-START mechanism it took (the M2.1 self-loop skip is
  scan avoidance too and is not yet stamped — [DD-13]'s next candidate),
  are present on EVERY
  artifact pcrec emits, with an engine-appropriate value.
  `<PREFIX>_ENGINE` is the family's first member and is now stamped on
  both kinds (`"vm"` / `"dfa"`, from one emitter —
  `pcrec_emit_engine_stamp`, so the two spellings cannot drift). The
  prefilter axis keeps ENGINE-SPECIFIC NAMES because its VALUE SETS are
  different vocabularies, not one vocabulary with two readings:
  `<PREFIX>_VM_PREFILTER` is the VM's, `<PREFIX>_DFA_PREFILTER` and
  `<PREFIX>_DFA_SCAN` are the DFA scan's.

  **[DD-13c], 2026-08-25 — "UNCONDITIONAL" IS TWO RULES, NOT ONE, AND THIS
  PARAGRAPH USED TO CONFLATE THEM.** The unit that owns a stamp is the
  MECHANISM the stamp names, not the artifact kind that usually carries it:

  - `<PREFIX>_ENGINE` is on **every artifact pcrec emits**, full stop.
  - `<PREFIX>_DFA_SCAN` and `<PREFIX>_DFA_PREFILTER` are on **every artifact
    that CONTAINS a DFA scan** — which is every DFA artifact AND every VM
    HYBRID. A hybrid (`<PREFIX>_VM_PREFILTER "hybrid"`) inlines the DFA
    emitter's own forward+reverse or attempt scan as a `static` function,
    with its own tables, its own D11 bound and its own candidate-start
    filter; it is the artifact kind that carries the mechanism this pair
    exists to report, and until [DD-13c] it was the one kind that could not
    say so. A NON-hybrid VM artifact contains no DFA scan and carries
    neither macro. **The rule is an IFF and is checkable as one:** a VM
    artifact carries the two `_DFA_*` macros if and only if
    `<PREFIX>_VM_PREFILTER` is `"hybrid"`
    (`tests/codegen/run_dfa_stamps.sh` asserts it in both directions, with
    the emitted `static <prefix>_prefilter` body — not either macro — as the
    independent third term).
  - The two prefilter macros are **two different selections**, not two
    spellings of one. `_VM_PREFILTER` says whether the VM runs a
    capture-erased DFA ahead of its program at all; `_DFA_PREFILTER` says
    what candidate-start filter that scan itself carries. A hybrid answers
    both, and the answers are independent.

  All four values come from ONE derivation per engine (`unanch_start`,
  `attempt_cand` in `src/gen/emit_dfa.c`) read by every site that needs
  them — the emitted loop, the DFA artifact's stamp, the hybrid's stamp —
  so a stamp cannot disagree with the loop it describes unless the
  derivation itself is wrong, in which case the loop is wrong too.
- **(b) CAPACITY and ACTIVITY macros stay VM-only**, exactly as this
  section already said: `<PREFIX>_VM_RUNGS`, `_VM_STRATS`, `_VM_PRUNES`,
  `_VM_PRUNE_CEILING`, `_VM_CALL_SPLICED`/`_LINKED`, `_VM_ROOT_MINW`, the
  budget macros and the frame/trail sizes. They report what the VM DID —
  per quantifier, per call site, per frame — and a DFA artifact has no
  such activity to report. This is the half the old rule was right about.

**[OPT-1], 2026-08-25: two more (b) macros —
`<PREFIX>_FAST_FRAMES` and `<PREFIX>_FAST_TRAIL`.** They report the
capacities the un-suffixed entries' FAST TIER runs on (§3, §10.9), and they
are on **every VM artifact**, single-tier ones included:

```c
#define RX_FAST_FRAMES  47   /* tiered: below the stamped default */
#define RX_FAST_TRAIL   71
```

**`<PREFIX>_FAST_FRAMES == <PREFIX>_RESUME_FRAMES` IS the statement "this
artifact has one tier"**, and it is the only spelling of it. Four things
produce it — the stamped default already fits a page, the slot array alone
does not, the scaled fast tier would be too small to be worth two runs, or
`-fno-tiered-entry` — and a consumer that needs to distinguish those reads
`rx_info.flags` and the pattern, not a missing macro. The macros are never
absent on a VM artifact, deliberately: a fact readable by a macro's ABSENCE
is the discriminator [DD-13] had to go back and remove from two checks.

They are **(b) and not §10.4**, and the line is worth drawing because
§10.4's five macros are the exception that goes on both engines. Those five
are arithmetic a caller must do **in order to call** an `_in` entry. These
two are not: no entry takes a fast capacity, no caller sizes anything from
one, and a DFA artifact has no tier to report. They are `.c`-private like
the budget macros beside them, so a consumer reading only the header does
not see them — which is the right answer to "should my code branch on the
tier boundary?" (it should not).

**On a DFA artifact the mirror is still thinner on the (b) macros: no
budgets, no `_VM_RUNGS`/`_STRATS`/`_PRUNES` MASK.**
A `--no-captures` build defines `RX_NCAPS` and the two `RX_ALTCLS_*`
stamps below, plus — **[ABI-NS], 2026-08-18 (D60): unconditionally, on
every artifact regardless of engine** — the give-up code space, the
unset sentinel, `PCREC_ENGINE_DFA`/`PCREC_ENGINE_VM`, and the nine D46
stamp bit constants (`PCREC_VM_RUNG_*`/`PCREC_VM_STRAT_*`/
`PCREC_VM_PRUNE_*`), the same "reserved but unreachable" shape the
give-up codes already had before this date. What a DFA artifact does NOT
carry is the (b) macros: the budget macros and the three OR'd MASKS
`RX_VM_RUNGS`/`RX_VM_STRATS`/`RX_VM_PRUNES` — those stay VM-artifacts-only,
because a DFA artifact has no per-quantifier rung/strategy/clamp decision
to summarize. `RX_ENGINE_WHY` stays VM-only too, and for a reason that is
about the FACT rather than about the engine: it names the construct that
FORCED the VM, and a DFA artifact was not forced — its `rx_info.engine_why`
is `NULL` for the same reason, so the macro's absence mirrors the struct.

**A consumer MAY now `#if` on `RX_ENGINE`.** This paragraph used to close
with the opposite warning — "a consumer that `#if`s on `RX_ENGINE` is
writing code that does not compile against half the artifacts pcrec
produces" — and [DD-13] answered it rather than restating it: the failure
that warning describes is caused by a CONDITIONAL stamp, and the only fix
for it is an UNCONDITIONAL one. The warning still holds, verbatim, for
every (b) macro: `#if`ing on `RX_VM_RUNGS` or a budget macro is writing
code that does not compile against a DFA artifact. (Measured by listing
every `#define` in a fresh build of each kind.)

**The per-artifact SUMMARY macros live in the `.c`, not the `.h`; the
universal `PCREC_*` constants live in the `.h`.** In the split form the
CLI produces by default, a consumer `#include`s the `.h` — which
carries the whole unprefixed universal set from the shared
`PCREC_RX_ABI_H` block (§2: the four give-up codes, `PCREC_UNSET`, the
two engine constants, the nine D46 stamp bit constants) plus
`<PREFIX>_NCAPS`, on EVERY artifact including a DFA-only one (measured
on one VM build and one DFA build: nineteen `#define`s in each `.h`,
identical except `RX_NCAPS`'s value; twenty-six in the VM `.c`). Before
[ABI-NS] this was eight `#define`s in the `.h` and thirty-five in the
`.c` — the difference is exactly the eleven macros that moved
(`PCREC_ENGINE_DFA`/`_VM`, new, plus the nine D46 bit constants that
used to be per-prefix and `.c`-only). So **the `#if` use case above,
for the universal constants, no longer needs a self-contained build —
they reach a consumer's TU through the ordinary `#include "<name>.h"`
now.** It remains true for the per-artifact SUMMARY macros below
(`RX_ENGINE`, the masks, the budgets): those are still emitted into the
`.c` only, so reading THEM still requires either a self-contained
artifact (`header_name == NULL`) or being the generated `.c` itself.
Whether the summary macros should also be emitted into the header is an
open design question, not settled here.

With that scoping, the observability macros on a captures-default build
of `'a(b|c)+d'` (the `#define` lines are the artifact's; the `/* ... */`
annotations below are this document's, not emitted text):

```c
#define RX_ENGINE          "vm"                    /* mirrors rx_info.engine */
#define RX_ENGINE_WHY       "capture group at pattern offset 1"
#define RX_VM_PREFILTER      "hybrid"               /* or "none" */
#define RX_VM_RUNGS           0x1u   /* bitmask: which per-quantifier rungs
                                         this artifact actually uses —
                                         CURSOR/FRAMES_BOUNDED/
                                         FRAMES_UNBOUNDED/REVDET/COUNTER */
#define RX_VM_STRATS           0x1u  /* bitmask: POSSESSIVE/BACKTRACKING */
#define RX_VM_PRUNES            0x1u /* bitmask: CLAMPED/UNCLAMPED (MRL) */
#define RX_VM_PRUNE_CEILING      "prefilter-window"
```

And on a DFA artifact — measured on `'(?:[a-z]+)@(?:[a-z]+)'`, the email
specimen's shape:

```c
#define RX_ENGINE        "dfa"          /* mirrors rx_info.engine; UNCONDITIONAL */
#define RX_DFA_SCAN      "unanchored"   /* or "attempt" */
#define RX_DFA_PREFILTER "byte-class"   /* see the value set below */
```

And on a VM HYBRID — measured on `'a(b|c)+d'`, the block at the top of this
section, which carries all of these at once:

```c
#define RX_ENGINE        "vm"           /* the artifact's own engine */
#define RX_ENGINE_WHY    "capture group at pattern offset 1"
#define RX_VM_PREFILTER  "hybrid"       /* the VM runs a DFA ahead of its program */
#define RX_DFA_SCAN      "unanchored"   /* [DD-13c] ...and THIS is that DFA */
#define RX_DFA_PREFILTER "memchr"       /* ...and this is ITS candidate-start filter */
```

`RX_DFA_SCAN` names WHICH DFA SCAN the artifact CONTAINS. The three shapes
are `"unanchored"` (the O(n) forward+reverse table pair, D7), `"attempt"`
(the per-start-position computed-goto loop a `^`/`\A`-bearing pattern
takes) and `"empty"`; the first two are different loops with different cost
curves, and nothing else a consumer can read distinguishes them — both stamp
`RX_ENGINE "dfa"` and both set `rx_info.engine` to `PCREC_ENGINE_DFA`.

**`"empty"` is [DD-13c], 2026-08-25, and it is a THIRD SHAPE rather than a
special case of the other two.** A pattern the start analysis proves can
match nothing — `\B\b`, `\b\B`, `\d\b\w`, `a\bb`, and their `^`-anchored
spellings — compiles to a search body that is one `return 0`: no table, no
loop, no skip, on EITHER engine. Those artifacts used to stamp the name of
the loop the emitter WOULD have written (`"unanchored"`, or `"attempt"` when
anchored), which is a statement about which emitter ran and not about what it
wrote. `RX_DFA_PREFILTER` reads `"none"` on all of them, for the reason the
value set below gives: there is no scan for a filter to be part of.

`RX_DFA_PREFILTER` names the CANDIDATE-START mechanism the artifact
carries, and its five values are the whole set:

| value | mechanism |
|---|---|
| `"none"` | no candidate-start filter: the start state ACCEPTS (`start_acc` — no skip is sound; the largest cause, e.g. `a*`, `.*`, `\bx*`), every position is a candidate, or the artifact provably matches nothing |
| `"memchr"` | ONE candidate byte value; a `memchr()` replaces the steps |
| `"byte-class"` | several; a 256-entry `<prefix>_can_begin_match` bitmap walk |
| `"memchr-bounded"` | the `memchr` form under a `$`/`\Z`/`\z` view or a word context: bounded at `n - 1` and WITHOUT the early `return 0` |
| `"byte-class-bounded"` | the bitmap form under the same, bounded at `n - 1` |

**The two `-bounded` values are a REAL difference in what the mechanism
buys, not a spelling.** Under a view, a skip may not pass the position
whose accept has not been evaluated yet, so every skip stops one byte
short and the `memchr` arm loses its early-out (`docs/dev/plan.md`
`[DD-13]` (b) measured the `(?:P)\z` spelling's loop as strictly weaker
than the plain form's on the same candidate table). A consumer that could
not tell them apart would attribute that difference to the pattern.

These are scalar macros for a per-artifact-wide verdict
(`RX_ENGINE`, `RX_VM_PREFILTER`, `RX_DFA_SCAN`, `RX_DFA_PREFILTER`,
`RX_VM_PRUNE_CEILING`) or a bitmask
when the axis is decided per-quantifier and a single scalar would
misreport a mixed pattern (`RX_VM_RUNGS`, `RX_VM_STRATS`,
`RX_VM_PRUNES`). Of the VM block above, everything but `RX_ENGINE` is
VM-artifacts-only; the DFA block's `RX_DFA_SCAN`/`RX_DFA_PREFILTER` are
the DFA SCAN's own selection facts ([DD-13]'s (a)/(b) split, above) and
since [DD-13c] appear on every artifact that CONTAINS such a scan — DFA
artifacts AND VM hybrids, the iff stated in (a). **[ABI-NS],
2026-08-18 (D60): the NAMED bit constants each mask is built from
(`PCREC_VM_RUNG_CURSOR`/etc., `PCREC_VM_STRAT_POSSESSIVE`/`_BACKTRACKING`,
`PCREC_VM_PRUNE_CLAMPED`/`_UNCLAMPED`) are not emitted here any more —
they moved to the shared, unprefixed `PCREC_RX_ABI_H` block (§2),
emitted once and unconditionally on every artifact including a DFA-only
one. Only the three OR'd MASKS above stay per-prefix and VM-only, since
their VALUE is the one genuinely per-artifact fact.** Two more D46
stamps are NOT VM-only, and a DFA-only artifact carries them too:

```c
#define RX_ALTCLS_MERGES   1   /* alternation runs merged into one class */
#define RX_ALTCLS_FACTORED 0   /* alternation runs prefix-factored */
```

They are emitted before either engine is built, so they appear on a
capture-free pattern's DFA artifact as well (measured on a
`--no-captures` build).

**`rx_info.flags` and these macros answer different questions, and the
masking rule applies to only one of them.** `flags` records the REQUEST
— the `PCREC_*` option bits exactly as compiled — with the
testing/tuning denials masked OUT, because an axis that changes no
answer must not make two identically-behaving artifacts differ in their
reflection surface. The macros record what the emitter DID, and they
visibly move when a denial is exercised: measured on
`'(x)(?:a|bc)+d'`, building `-fno-possessify` moves `RX_VM_STRATS` from
`0x1u` (POSSESSIVE) to `0x2u` (BACKTRACKING) while the emitted
`rx_info.flags` value is unchanged — the whole `rx_info` initializer is
identical between the two builds except `frame_capacity`, which moves
because denying possessification really does cost a frame. So: to see
what was ASKED FOR, you cannot use `flags` for a masked axis at all; to
see what HAPPENED, read the macro.

The set of bits that get masked, and the per-flag reasoning, live in
`lib/pcrec.h`'s own comments (`lib/CLAUDE.md` indexes them) — that is
where to look, from here and from §8, to see which bits legitimately
vanish from `rx_info.flags` on a round trip. This document does not
duplicate that catalogue.

---

## 7. The compile-entry contract: patterns are NUL-terminated

`pcrec_compile()` takes a NUL-terminated `const char *pattern` and no
length parameter:

```c
int pcrec_compile(const char *pattern, const pcrec_options *opt,
                   pcrec_output *out, pcrec_error *err);
```

**A raw `0x00` byte inside the intended pattern silently truncates the
compile.** A 3-byte pattern `"a\0b"` compiles as the 1-byte pattern `"a"`
and `pcrec_compile()` reports **success** — for a different, shorter
pattern than the one the caller passed. This is not a defect pcrec
intends to fix in this API shape; it is the documented, checkable
behavior of a NUL-terminated entry point, and it is symmetric with a
comparison engine measured independently for this document:

**PCRE2's own `PCRE2_ZERO_TERMINATED` compile mode truncates
identically.** Measured directly against libpcre2 10.46 on this box
(dlopen'd via `tests/fuzz/pcre2_abi.h`, the project's existing
no-dev-package ABI shim — not read from documentation): compiling the
3-byte buffer `{'a', 0, 'b'}` with `PCRE2_ZERO_TERMINATED` produces a
pattern that matches only `"a"` (a 1-byte match at the start of the
3-byte subject `"a\0b"`), while compiling the same buffer with an
explicit `length=3` produces the real 3-byte pattern, matching the full
subject with span `[0,3)`. Both engines have exactly one honest way to
avoid this: the caller must pass the pattern's true length, which
PCRE2's API accepts and pcrec's `pcrec_compile()` today does not. This is
therefore an **API-surface gap relative to PCRE2's own length-taking
mode**, not a semantics divergence between the two engines' NUL handling
— PCRE2's sentinel mode has the identical failure mode pcrec's only mode
has.

**`rx_info.pattern_len` is the detectability instrument for this gap,
and reaching it costs more than reading a field.** It reports the
*actual* byte count `pcrec_compile()` saw and compiled — the truncated
count, not the caller's intended count. But `rx_info` lives in the
GENERATED ARTIFACT, and `pcrec_compile()` hands its caller C source
text, not a struct: at compile time the only way to read `pattern_len`
is to string-search `out.c_src` for the emitted `.pattern_len = N,`
line, and the only way to read it as a value is to compile and link the
artifact first. Neither is a check a caller will write by accident.

**The one-line pre-flight is cheaper and is what a caller should
actually do.** If you know the pattern's true length independently —
and a caller handling untrusted or NUL-bearing pattern text does — test
it before compiling:

```c
if (strlen(pattern) != known_length) { /* the pattern contains a NUL:
                                          refuse it yourself */ }
```

That catches the truncation before it happens, using only the standard
library. `pattern_len` remains the after-the-fact instrument for an
artifact you already have. Verified: compiling the byte-built 3-byte
`"a\0b"` buffer through the real `pcrec_compile()` (not the CLI, which
cannot carry a NUL through `argv` at all) produces `out.c_src` containing
`.pattern_len = 1,` — the artifact honestly reports what it actually
compiled. This exact probe is pinned as `tests/cli/run_cli_tests.sh`
case16, and the general "`pattern_len` is the source byte count, not the
matched-byte count" property (distinguishing `pattern_len` from a count
of bytes the matcher actually walks — e.g. `'a\nb'`, 4 source bytes,
`pattern_len = 4`) is pinned structurally in
`tests/codegen/run_codegen_tests.sh`.

**Full length-taking compile support — a `(pattern, length)` overload or
equivalent that lets `pcrec_compile()` refuse a pattern whose declared
extent it cannot verify, rather than silently truncating and succeeding —
is not part of this contract.** It is scheduled with `DD-3` (generated-API
versioning/compatibility policy), tracked as `docs/dev/known_issues.md`
K9, and is the natural trigger for customer `V-A`'s `(pattern, length)`
compatibility shim. Until then, a caller with an untrusted or
NUL-containing pattern source must run the `strlen` pre-flight above
itself; nothing in `pcrec_compile()`'s signature enforces that.

---

## 8. The library entry: `pcrec_options`, `pcrec_output`, `pcrec_error`

### 8.0 A complete compile, start to finish

This is the whole calling sequence, and it compiles and runs exactly as
written (verified: built with `gcc -Wall -Wextra -Werror` against
`lib/pcrec.h` and `libpcrec.a`, run, and its `matcher.c`/`matcher.h`
output compiled in turn):

```c
#include <stdio.h>
#include "pcrec.h"

int main(void)
{
    pcrec_options opt;
    pcrec_output  out;
    pcrec_error   err;

    /* MANDATORY first step: a zero-initialized pcrec_options has
       prefix == NULL and every compile fails with "invalid symbol prefix". */
    pcrec_default_options(&opt);
    opt.header_name = "matcher.h";   /* NULL (the default) = self-contained .c */

    if (pcrec_compile("a(b|c)+d", &opt, &out, &err) != 0) {
        fprintf(stderr, "pcrec: %s (at byte %zu of the %s)\n", err.msg, err.pos,
                err.input == PCREC_ERR_INPUT_PATTERN ? "pattern" : "template");
        return 1;
    }

    /* out.c_src and out.h_src are malloc'd, NUL-terminated C source and are
       the CALLER's to free from here on. h_src is non-NULL exactly when
       opt.header_name was set. */
    FILE *c = fopen("matcher.c", "w");
    if (c) { fputs(out.c_src, c); fclose(c); }
    if (out.h_src) {
        FILE *h = fopen("matcher.h", "w");
        if (h) { fputs(out.h_src, h); fclose(h); }
    }

    pcrec_output_free(&out);   /* frees both buffers, NULLs both fields */
    return 0;
}
```

Four things in it are contract, not style:

1. **`pcrec_default_options()` is mandatory, and skipping it fails every
   compile.** It is not a convenience that fills in tasteful defaults
   over a working zero state: a zeroed `pcrec_options` has
   `prefix == NULL`, and pcrec refuses a NULL prefix. Measured — a
   `memset`-zeroed options struct returns `-1` with
   `err.msg == "invalid symbol prefix (must be a C identifier, <= 60
   chars)"` for a pattern that compiles fine after
   `pcrec_default_options()`. It sets `prefix = "rx"`,
   `encoding = PCREC_ENC_BYTE` and `header_name = NULL`, and zeroes
   everything else; override fields after calling it, never instead.
   (Re-measured for this revision by printing every field of a
   default-initialized struct: `prefix=rx`, `encoding=0` — which is
   `PCREC_ENC_BYTE` — `header_name=NULL`, `flags=0`, `engine=0`.)
2. **`pcrec_output` owns two heap buffers and the caller frees them.**

   ```c
   typedef struct {
       char *c_src;   /* malloc'd; free with pcrec_output_free */
       char *h_src;   /* malloc'd, or NULL when options.header_name == NULL */
   } pcrec_output;
   ```

   `pcrec_output_free()` frees both and NULLs both fields (measured
   before and after), so it is safe to call twice and safe on a struct
   whose `h_src` was never produced. There is no other way to release
   them. §5.2's "no allocation, no lifecycle to manage" is a statement
   about the MATCH path only; the compile path allocates and this is its
   lifecycle.
3. **`h_src` is non-NULL exactly when `header_name` was set** (measured
   both ways). Do not test `header_name` and assume; test `h_src`.
4. **Check the return value, not the error struct.** `pcrec_compile()`
   returns `0` on success and `-1` on failure, and fills `err` only on
   failure.

### 8.1 What `pcrec_compile()` guarantees its caller (D56)

pcrec is a library, and two of its promises exist because a library
cannot behave like a program:

- **It never `abort()`s the caller on the compile path.** Every
  allocation site routes failure through the internal `ctx_nomem()` and
  comes back as a normal `-1`-with-diagnostic return, so a caller that
  sets a memory limit precisely in order to survive a hostile pattern
  does survive it. Two `abort()`s remain in the code deliberately and
  neither is an allocation failure: a "cannot happen" DFA structural
  invariant, and the syntax-dump path's detached string buffers, which
  run outside a compile and have no `pcrec_error` to report through.
- **A pattern can be REFUSED for compile-side RESOURCE reasons, and
  that is a distinct failure class from a syntax error.** It arrives
  through the same `-1` and the same `pcrec_error`, so a caller
  distinguishes them by reading `err.msg`, not by the return value.
  Measured at the D56 boundary (re-measured for this revision): `a{9795}`
  compiles, `a{9796}` returns `-1` with `err.msg == "pattern too complex
  for the DFA engine (subset construction exceeds 48000000 state-set
  elements; try --engine=vm)"`. The pattern is perfectly legal PCRE; what
  failed is that compiling it would cost more than pcrec is willing to
  spend. A caller that reports every `-1` as "bad regex syntax" to its
  user will be wrong here. **The escape the diagnostic names is real and
  was measured, not assumed**: the same `a{9796}` compiles cleanly under
  `--engine=vm`, because that mode never builds the DFA whose cap this
  is. (Until [M5-SEAM] this message ended "VM engine arrives in M4" — a
  promise about a milestone that had already shipped, which sent a reader
  looking for a future release instead of at a flag they already have.)

### 8.2 The option and error structures

**`byte` is the only encoding pcrec implements today.** `utf8` is a
recognised NAME with no backend — refused until milestone M5 — stated
here first because the fact otherwise sits three paragraphs down, behind
the field table below: this is `lib/pcrec.h`'s own enum comment
("not yet implemented (arrives with milestone M5)") and `cli/main.c
--help`'s own wording ("utf8 ... is refused until milestone M5") said
once, up front, rather than left for a reader to find in either.

```c
typedef struct {
    const char *prefix;      /* C identifier prefix; default "rx" */
    int         encoding;    /* PCREC_ENC_* ; PER-COMPILE-CALL, see below */
    uint64_t    flags;       /* PCREC_CASELESS | PCREC_EMIT_MAIN |
                                 PCREC_NO_CAPTURES | ... (see lib/pcrec.h
                                 for the full, growing bit catalogue) */
    const char *header_name; /* NULL = self-contained .c */
    int         engine;      /* PCREC_ENGINE_AUTO / _DFA / _VM */
    int64_t     step_budget; /* PCREC_STEP_BUDGET_DEFAULT / _NONE, or a count */
    int64_t     work_budget; /* PCREC_WORK_BUDGET_DEFAULT / _NONE, or a count */
    int         unroll_k;    /* PCREC_UNROLL_K_DEFAULT (0) = built-in default */
    int         frame_capacity; /* 0 = let the compiler size it. NOT the
                                    same sentinel as rx_info's field of the
                                    same name, which uses -1 for unbounded */
} pcrec_options;
```

**`encoding` is a PER-COMPILE-CALL scalar** ([M5-SEAM], D58): one encoding
per `pcrec_compile()` call, carried in this field and nowhere else. There is
no process-global, no file-global and no environment variable, so mixing
encodings inside one compilation unit or one binary is supported by
construction — each artifact is self-contained, carries its own prefix, and
embeds exactly one encoding's residual block (§3.1.1). The CLI spells it
`-e NAME` or `--encoding=NAME`.

`PCREC_ENC_BYTE` (0, the default) is the only encoding implemented; the
value is what `rx_info.encoding` reports (§6). `PCREC_ENC_UTF8` (1) is a
recognised NAME with no backend: `pcrec_compile()` refuses it with
`err.msg == "encoding 'utf8' arrives with milestone M5 (an engine axis, not
a module: no --features name enables it)"`, and any other value is refused
with `"unknown encoding (want byte, utf8)"`. Both refusals are ordinary
`-1`-with-diagnostic returns and write no C.

**`PCREC_ENC_BYTE` was spelled `PCREC_ENC_ASCII` before [M5-SEAM]**, and
`-e ascii` was the CLI value. It is a RENAME, not an alias — `-e ascii` is
now an unknown encoding — taken under §9's pre-v1 posture as one announced
boundary. The reason is that the old name asserted something false about
the semantics: this encoding treats every byte as a character, `0x80`-and-up
included, with no case and no meaning attached, which is precisely what
"ASCII" does not say. D58's own ruling text names the encoding `byte`.

Every boolean option (`PCREC_CASELESS`, `PCREC_EMIT_MAIN`,
`PCREC_NO_CAPTURES`, and the strategy-denial/force flags in `lib/
pcrec.h`) is one representation end-to-end: the same bit set by a CLI
flag, carried in `pcrec_options.flags`, and reflected verbatim (where not
deliberately masked, §6.3) in the compiled artifact's `rx_info.flags`.
`PCREC_NO_CAPTURES` recovers the pre-captures-default pure-DFA artifact
(`<PREFIX>_NCAPS 1`); captures are on by default since M4.5.

**A caller that round-trips its own flags through `rx_info.flags` will
find some bits missing, legitimately.** The masked ones are the
testing/tuning axes that change no answer (§6.3); which bits those are,
and why each is masked, is documented per-flag in `lib/pcrec.h`'s own
comments, which is the place to look — this document does not duplicate
that catalogue.

`pcrec_error` carries which input a diagnostic's `pos` indexes into:

```c
typedef enum {
    PCREC_ERR_INPUT_PATTERN  = 0,
    PCREC_ERR_INPUT_TEMPLATE = 1
} pcrec_err_input;

typedef struct {
    char            msg[256];
    size_t          pos;
    pcrec_err_input input;
} pcrec_error;
```

`pcrec_compile()` always sets `input = PCREC_ERR_INPUT_PATTERN` today (it
has no other input yet — a future substitution-template compiler is the
first producer of `PCREC_ERR_INPUT_TEMPLATE`). `pcrec_compile()` returns
`0` on success (`out` filled) or `-1` on failure (`err` filled if
non-NULL) — verified directly: an unterminated group `"a(b"` returns
`-1` with `err.pos == 1, err.input == PCREC_ERR_INPUT_PATTERN`.

`PCREC_*` names only pcrec's own enum/bit-valued constants — never a
struct field name, never a bare CLI flag spelling — with the one stated
exception §1 records: the per-artifact `PCREC_FEATURE_SET` /
`PCREC_FEATURE_MODULES` stamps, which carry the `PCREC_*` spelling
without living in `lib/pcrec.h`. `PCRE2_*` spellings
are reserved for a future PCRE2-compatibility layer and are never native.

---

## 9. Provenance and status

This document graduates `docs/design/match_api_m4.md` (the M4 match-API
freeze design record) and `docs/design/engine_m4.md` into a spec per
`docs/dev/decisions.md` D40's addendum: design records what pcrec wants
to build and the process that got there; this spec records what shipped
and is pcrec's contract with an embedder, going forward. Consult those
documents for *why* a rule is what it is (ruling citations, panel
findings, refuted alternatives); consult this document for *what the
rule is*.

**Pre-v1 posture (D40):** this contract carries no backwards-compatibility
weight yet. Breaking changes are unconstrained in substance and governed
only in form — one announced-boundary commit per break, populations
conserved and accounted, never silent drift. At a future v1 declaration,
this document (or its direct successor) becomes the compatibility-bound
enumeration; until then, "frozen" here means "the M4 working baseline",
not "permanent".

---

## 10. The caller-provided frame buffer — **[DD-14.FB]**

> **STATUS: BUILT (2026-08-25).** Every artifact pcrec emits exports
> `<prefix>_search_in`, `<prefix>_match_in` and `<prefix>_match_caps_in`,
> declares the `<prefix>_buffers` descriptor, carries the five sizing
> macros in its header and the four sizing fields on `rx_info` at `abi`
> 3 — on both engines, present and inert on a DFA artifact. This section
> was written one revision earlier as SPECIFIED-NOT-YET-BUILT, because
> D71 item 2 rules the shape "decided at docs/spec/match_api.md under
> D40"; every number in it has since been re-measured against the shipped
> emitter, and the two that moved are noted where they appear. The design
> record — the alternatives, why each was rejected, and the measurements
> behind the numbers — is `docs/design/frame_buffer_design.md`,
> informational per docs/spec/CLAUDE.md's charter.
>
> **What checks it.** `tests/recursion/framebuffer.rxt` (behaviour, in
> `make test`), `tests/codegen/run_codegen_tests.sh`'s `[DD-14.FB]` block
> (the six entry declarations byte-exact, the sizing surface on both
> engines, no capacity guard reading a stamped constant, the delegation
> direction), `tests/thread/run_stackdepth_tests.sh` (the 128 KB thread,
> in `make test`), and `make test-frame-buffer` on demand (the
> NULL-equivalence spread and §10.6's reservation, re-measured).

### 10.1 What the ruling is for

A generated matcher never allocates (§5.2), so the two arrays a
backtracking match needs — the resume stack and its undo trail — are
sized at compile time and live in the entry point's own stack frame. That
makes the artifact's depth ceiling a compile-time constant, which is the
right default and the wrong limit: **no fixed number is right for a
data-dependent depth, and the caller is the one who knows.** D71 item 2
rules that a caller may supply the storage instead, keeping pcrec's
never-allocates property while lifting the ceiling as far as the caller
is willing to reserve.

Two measured facts frame what this buys, and the release note states both:

- **The depth ceiling is small, and it is a SUBJECT SIZE, not a number.**
  MEASURED on a default `-p rx --features all` build of `^(a(?1)?b)$` (a
  pattern whose recursion depth grows with the subject): it matches up to
  a **684-byte** subject and returns `PCREC_ERR_FRAMES` at a 686-byte one.
  libpcre2 10.46 matches 800 KB of the same shape — that half is not
  measured here but cited from `docs/design/subroutines_design.md` §5.6.
- **The refusal is CONSTANT-TIME, which is the half PCRE2 does not have.**
  MEASURED on the same build, the left-recursive runaway `^(a|(?1)a)$`
  over aⁿb returns `PCREC_ERR_FRAMES` in **0.0006 s at every n from 100 to
  100,000** — flat across a 1,000× range. libpcre2 pays a cost growing as
  the square of the subject there (2.6–5.6 s at n = 20,000, cited from the
  same section, which measures the exponent at 2.04). Refusing a legitimate
  deep match is the price of refusing a runaway in constant time; §10.6 is
  how a caller who wants the depth buys it back.

### 10.2 The three new entries, and the descriptor

```c
typedef struct {
    void   *frames;    /* storage for resume frames */
    size_t  nframes;   /* CAPACITY IN FRAMES — not bytes */
    void   *trail;     /* storage for trail entries */
    size_t  ntrail;    /* capacity in ENTRIES — not bytes */
} <prefix>_buffers;

int       <prefix>_search_in    (const unsigned char *s, size_t n, size_t startpos,
                                 ptrdiff_t (*caps)[2], const <prefix>_buffers *buf);
ptrdiff_t <prefix>_match_in     (const rx_ctx *ctx, const <prefix>_buffers *buf);
ptrdiff_t <prefix>_match_caps_in(const rx_ctx *ctx, ptrdiff_t (*caps_out)[2],
                                 const <prefix>_buffers *buf);
```

Each `_in` entry is its un-suffixed sibling in every respect —
same anchoring promise, same return space, same `caps`/`caps_out`
discipline, same give-up codes — plus one argument naming where the
working storage lives. §3.1, §3.2, §3.3, §4 and §5 apply to them
unchanged and are not restated here.

**Three properties of the descriptor are contract, not convenience:**

- **`<prefix>_buffers` is PER-ARTIFACT, scoped by `--prefix`** — it is
  *not* one of §1's fixed-literal `rx_*` ABI types, and the difference is
  deliberate rather than an oversight. Those six types are literal so that
  differently-prefixed matchers compose; a buffer is the opposite case,
  because a resume frame's SIZE differs between artifacts (MEASURED: 24
  bytes on an artifact with no LINKED call, 40 on one with a linked call —
  `RX_VM_CALL_LINKED > 0`; a call that wave G SPLICED, `RX_VM_CALL_SPLICED`,
  is inlined and adds nothing to the frame, so the email specimen's factored
  form under `--engine=vm` stamps 24 with ten spliced calls — read the
  stamp, never infer it from the pattern text). A fixed-literal
  spelling would advertise an interchangeability that does not exist.
- **The counts are CAPACITIES, not byte sizes.** `nframes` is how many
  frames the storage holds, `ntrail` how many trail entries. §10.4 is how a
  caller converts bytes to counts.
- **`frames` and `trail` are two separate regions and BOTH are required**
  when `buf` is non-NULL. Supplying one and not the other is not
  expressible: the trail is not an implementation detail of the frames, and
  MEASURED on `^(a(?1)?b)$`, the trail is the array that binds first at the
  stamped defaults — a caller who could raise only `nframes` would see no
  change at all (`docs/design/frame_buffer_design.md` §4).

### 10.3 `buf == NULL`, and what a give-up means

**`buf == NULL` is defined to be exactly a call to the un-suffixed entry
with the same other arguments.** Not "similar to", not "equivalent in
observable behaviour" — the same call, and an artifact is free to
implement it as one. This is the whole compatibility story for a caller
that wants one call site and a runtime choice.

**A give-up means "the buffer in use ran out", and the code does not say
whose buffer it was.** `PCREC_ERR_FRAMES` is returned for a caller-supplied
buffer exactly as for the stamped default, and §4's rule that the code
names a RESOURCE rather than an array or an owner holds here too. **The
count that WOULD have sufficed is NOT reported.** That is deliberate and
matches D71 item 1's treatment of the recursion counter: the number is a
diagnostic fact, the default artifact does not carry the machinery to
produce it, and "rebuild with the diagnostic axis" is the documented story.

**A give-up is RETRYABLE, and this is a promise a caller can build on.**
Calling the same entry again, same subject, same `startpos`, with a larger
buffer, is defined: the matcher holds no state between calls (§5.3), the
caller's `caps` array is untouched on every negative return (§3.3, §5), and
the buffers are pure scratch. So "give up, double the buffer, retry" is a
correct algorithm and the obvious one to write.

**The buffer's contents after any call are UNSPECIFIED.** A caller must not
read them and need not re-initialise them before the next call. Nothing in
the buffer is meaningful to anyone but the matcher, and nothing survives
the call that produced it.

**Alignment.** Both regions must be suitably aligned for the artifact's own
frame and trail types; `<PREFIX>_BUFFER_ALIGN` (§10.4) states the
requirement. Storage from `malloc`, `mmap`, or a declaration of any
ordinary object type satisfies it on every target pcrec supports; the macro
exists for the caller doing pointer arithmetic inside a larger arena.

### 10.4 Sizing a buffer: the reflection surface

The frame and trail layouts are private to the artifact — this document
does not publish them, and a caller must not assume them. What it publishes
instead is the arithmetic. Five macros in the emitted header:

```c
#define <PREFIX>_RESUME_FRAMES      2048  /* the stamped DEFAULT capacity */
#define <PREFIX>_TRAIL_FRAMES       3072
#define <PREFIX>_RESUME_FRAME_SIZE    40  /* bytes per frame, THIS artifact */
#define <PREFIX>_TRAIL_FRAME_SIZE     16
#define <PREFIX>_BUFFER_ALIGN          8
```

**Those numbers are STAMPED FOR THE TARGET, not constants of pcrec, and a
reader must not take `40` as one.** A resume frame's size depends on the
artifact — MEASURED: **24** bytes on a call-free artifact, **40** on a
call-bearing one, **32** and **48** on the `--trace` versions of the same two —
and on the target's own type sizes. pcrec computes each number at compile time
from the SAME member list that emits the struct, so the two cannot drift; and
because a stamped literal is a number that can be wrong where a `sizeof` cannot
(the frame and trail types are private to the artifact, so the header has no
type to apply `sizeof` to), **the artifact ASSERTS each stamped macro against
the real `sizeof`/`_Alignof` at its own build**. A number computed for a
different target model is therefore a loud compile error naming the macro, not
a silent under-allocation in the caller who divided by it. Read the macros;
never hardcode their values.

(the two capacity macros existed before this revision but lived in the
generated `.c`; they moved into the `.h`, where a caller can read them), and
four of the same facts as fields on `rx_info`, for a consumer with no C header —
an FFI or `dlopen` binding, which is exactly the consumer most likely to
want a large reservation:

```c
    int64_t  resume_frames;      /* the stamped default capacity */
    int64_t  trail_frames;
    int32_t  resume_frame_size;  /* bytes per frame / per trail entry */
    int32_t  trail_frame_size;
```

**`rx_info.abi` moves `2` → `3`** with this addition (§6's own rule:
"layout version; bump-on-change"). `resume_frames` duplicates the existing
`frame_capacity` field's information for the bounded case and is not
redundant with it: `frame_capacity` reports `-1` for "no bound at all" on a
DFA artifact and answers a different question (§6's sentinel-asymmetry
note).

**A STAMPED SIZE OF `0` MEANS "THIS ENGINE TAKES NO BUFFERS" — CHECK BEFORE
YOU DIVIDE.** The byte-to-capacity arithmetic above (`bytes /
<PREFIX>_RESUME_FRAME_SIZE`) is a division by zero on any artifact whose
engine has no resume stack, which is every DFA artifact. That is not a defect
in the `0`: it is `rx_info`'s honest signal, and the alternative — a fake
non-zero size for storage that is never read — would be worse. But it means
the one-call-site-against-both-engines property this section promises has one
obligation on the caller's side: **test the size before dividing by it, and
pass `NULL` when it is `0`.** Nothing is lost by doing so — an `_in` entry on
such an artifact accepts a descriptor and ignores it, so `NULL` and a
correctly-sized buffer are the same call there.

**On a DFA artifact the whole surface is present and inert**, which is §4's
"reserved but unreachable" shape applied again and is what lets a caller
write one call site against both engines. The three `_in` entries, the
`<prefix>_buffers` type and all five macros are emitted on EVERY artifact;
the four sizing macros and the four `rx_info` fields read `0`, because that
engine has no resume stack to size; and an `_in` entry on such an artifact
accepts a descriptor and ignores it, answering exactly as its un-suffixed
sibling does. This is a deliberate departure from §6.3's rule that the
per-artifact budget/capacity macros are VM-artifacts-only: those macros
report what an artifact DID, where these five are what a caller needs in
order to CALL it, and a consumer whose code stops compiling when the same
pattern selects the other engine is the failure §6.3 warns about.

### 10.5 Concurrency and reentrancy: §5.3, extended by exactly one clause

§5.3's rule — "any number of threads may call the same artifact's entry
points concurrently, provided each call has its own `caps`/`caps_out`
buffer" — gains one conjunct and nothing else:

> **…and its own frame and trail buffers.** Two concurrent calls sharing
> one `<prefix>_buffers` region is a data race in the CALLER's code,
> exactly as a shared `caps` array is, and the matcher does not serialize
> it. The same applies to one thread re-entering a matcher from a callout:
> the inner call needs its own storage.

**There is deliberately no way to set a buffer once, per artifact or per
thread**, and this is the reason: any such mechanism is either mutable
state in the emitted file — which §5.3 forbids and which the TS-1 check
would reject — or a thread-local, which survives the concurrency test and
fails the reentrancy one. The buffer travels with the call because that is
the only place it can travel and keep §5.3 true.

### 10.6 A worked example: an mmap'd, lazily-committed reservation

This is what D71 item 2 means by "PCRE2-depth recursion with pcrec still
never allocating". The caller reserves address space it does not commit,
and the operating system materialises only the pages the match actually
touches.

```c
#include <sys/mman.h>
#include "matcher.h"                  /* the generated header */

size_t bytes = (size_t)64 << 20;      /* 64 MB of address space, per region */
void  *f = mmap(NULL, bytes, PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_NORESERVE, -1, 0);
void  *t = mmap(NULL, bytes, PROT_READ|PROT_WRITE,
                MAP_PRIVATE|MAP_ANONYMOUS|MAP_NORESERVE, -1, 0);

rx_buffers buf = { f, bytes / RX_RESUME_FRAME_SIZE,
                   t, bytes / RX_TRAIL_FRAME_SIZE };

int r = rx_search_in(subject, n, 0, caps, &buf);   /* pcrec allocates nothing */
```

**MEASURED on `^(a(?1)?b)$` with exactly those two reservations** (the
arithmetic is `RX_RESUME_FRAME_SIZE == 40` and `RX_TRAIL_FRAME_SIZE == 16`,
so 1,677,721 frames and 4,194,304 trail entries):

| subject | result | time | process RSS after |
|---|---|---|---|
| 684 B | match | 0.0001 s | 2.0 MB |
| 200 KB | match | 0.0135 s | 24 MB |
| **800 KB** | **match** | **0.056 s** | **88 MB** |
| 932 KB | match | 0.065 s | 102 MB |
| 940 KB | `PCREC_ERR_FRAMES` | 0.069 s | 103 MB |

**RE-MEASURED on the shipped emitter (2026-08-25) and the table holds** —
1,677,721 frames and 4,194,304 trail entries derived from the same two
reservations, 1.8 MB resident before the first match, the 800 KB row
matching in 0.057 s having touched 90 MB, and the ceiling still between
n = 466,000 and n = 470,000. `tests/recursion/run_frame_buffer.sh` is that
re-measurement, and it asserts each of those rather than printing them.

**CORRECTION, same pass.** The sentence that stood here said the same
artifact returns `PCREC_ERR_FRAMES` "on every one of those subjects"
through `rx_search`. That is true of the **four larger rows only**: 684 B
is exactly the largest subject §10.1 says the un-suffixed entry MATCHES,
so the first row's control returns `1`, and the two sentences could not
both be true. MEASURED, and corrected here rather than left standing;
`docs/design/frame_buffer_design.md` §8 carries the same overstatement and
is left alone as the historical record. Three things a caller should take
from it:
**128 MB reserved costs 1.7 MB of resident memory until touched**; the
800 KB row is the depth libpcre2 10.46 was measured reaching from its
heap, so the ruling's goal is met with room to spare; and **the ceiling is
predictable from the emitted numbers** — the trail binds, at
`ntrail / (trail entries per level)`, which for this pattern is 4,194,304 /
8.98 ≈ 467,000 levels, and the measured boundary sits between 466,000 and
470,000.

**The buffer does not have to be `mmap`'d.** Any storage works — a heap
allocation, a static array in the caller's own translation unit, an arena
slice. `MAP_NORESERVE` is the example because it is the one that makes a
generous ceiling nearly free, and because it is the shape D71 item 2 names.

### 10.7 The freestanding and embedded profile

A caller with no `mmap` has two routes and needs neither `mmap` nor a heap:

- **Pass `NULL`** and get the stamped default — exactly today's behaviour,
  unchanged, with the artifact's own storage on the stack.
- **Point the descriptor at the caller's own static storage.** This does
  not violate §5.3's no-mutable-state rule, and the distinction is worth
  stating because it looks like it should: that rule binds what pcrec
  EMITS. Storage the embedder declares in its own translation unit is the
  embedder's, and the embedder is the party who knows whether its matcher
  calls are concurrent. A single-context embedded caller puts the buffer
  in `.bss`, keeps its stack small, and pays nothing.

### 10.8 What does NOT change

Stated explicitly because it is the compatibility promise, and because the
implementation lane owes a check that asserts each line:

- **`<prefix>_search`, `<prefix>_match` and `<prefix>_match_caps` keep
  their exact signatures, return spaces, anchoring promises and
  `caps`/`caps_out` disciplines.** A consumer that never calls an `_in`
  entry needs no source change, and its call sites are binary-compatible.
- **`<prefix>_next_pos` is untouched**, as is the find-all protocol of §3.1
  that goes through it.
- **The give-up code space of §4 gains no member.** `PCREC_ERR_FRAMES`
  covers the caller-buffer case; nothing new is minted.
- **No allocation is added anywhere** (§5.2 stands, and §5.2's scoping to
  the match path is unchanged: the compile path's `pcrec_output` lifecycle
  is §8's and is unaffected).
- **The pre-v1 posture of §9 governs the two things that DO break** —
  `rx_info`'s layout (§10.4, `abi` 2 → 3) and the emitted run-struct text,
  which was never contractual. Per D40 regime 1 these are unconstrained in
  substance and governed only in form: one announced-boundary commit,
  populations conserved and accounted. [DD-3], which would otherwise supply
  the versioning-event policy, has no policy yet (plan.md, `STATE:not-started`).

### 10.9 The tiered default entry, and what a FRAMES escalation restarts — **[OPT-1]**

**The rule.** On an artifact whose stamped default storage does not fit
inside one 4 KB page, each un-suffixed entry runs the match on a
page-budgeted buffer of `<PREFIX>_FAST_FRAMES`/`<PREFIX>_FAST_TRAIL` (§6.3)
and, **on `PCREC_ERR_FRAMES` and on no other outcome**, re-runs the same
match from scratch on the full stamped default. The second run's result is
what the caller gets. Every other outcome — a match, a no-match,
`PCREC_ERR_STEPS`, `_WORK`, `_RECURSE`, `PCREC_ERR_INTERNAL` — is returned
from the first run directly.

**A FRAMES ESCALATION RESTARTS THE STEP AND WORK BUDGETS.** They are per
CALL, not per tier, and the second run begins with both full — the same
state §4's budgets are in at the top of any call. This is not a
concession; it is what makes the rest of this section true, and the
alternative (carrying the remainder forward) would be observably wrong: a
deep run started with a depleted step budget would report `PCREC_ERR_STEPS`
where a single-tier artifact matches. **Its consequence — one call may spend
up to twice each budget — is stated in §4**, and the wasted fast attempt is
bounded by those budgets rather than by the fast frame count, since sixty
frames of depth can absorb an unbounded amount of backtracking.

**No answer changes, and that is a consequence rather than a hope.** The
deep run is a bit-for-bit replay of what a single-tier entry does, from
scratch: the same capacities, both budgets refilled, the same start-position
loop over the same prefilter, one deterministic engine. Nothing the fast
attempt did can carry into it, because §5.3 leaves nothing that could — the
run state is a local of the tier that declared it, there is no allocation,
no thread-local and no mutable static. So for every artifact, every subject
and every entry, the value returned and the capture spans written are the
ones the entry produced before the tier existed.

One behaviour genuinely differs and is not observable: the fast attempt may
reach `PCREC_ERR_FRAMES` where a single-tier run would have reached
`PCREC_ERR_STEPS`, having hit its smaller capacity earlier in the same
trace. That value is never returned — it is the escalation trigger — and
the replay then reports the `PCREC_ERR_STEPS`.

**What a caller may rely on:**

- Every promise in §3, §3.1–§3.3, §4 and §5 stands unchanged.
- `PCREC_ERR_FRAMES` from an un-suffixed entry still means what §4 says: the
  **stamped default** ran out. It never reports the fast tier's exhaustion.
- The depth an artifact can reach is unchanged (D73 keeps the stamped
  2048/3072); only the cost of *not* reaching it moved.
- **A call that DOES escalate is SLOWER than it was** — measured 1.24–1.53×
  on `((a)|(aa))+b`, with a 3.05× discontinuity across the boundary itself
  (§3 carries the figures). The tier is a bet that real calls hold on the
  fast tier; where a workload is measured not to, `_in` or
  `-fno-tiered-entry` is the answer.
- The **`_in` entries are untouched** — contract, signature and cost. They
  never had a tier and do not gain one: the caller owns the storage, so
  there is nothing to escalate from. `buf == NULL` remains §10.3's "the same
  call" as the un-suffixed entry, and therefore now gets the tiering.

**What a caller must NOT rely on:** which tier answered. There is no
supported observable for it — `<PREFIX>_FAST_FRAMES` says where the boundary
is, not which side a given call landed on. A caller who needs a depth
guarantee on the fast path, or who is on a stack too small for the deep
tier, uses `_in` (§10.2); `-fno-tiered-entry` (`tuning.md` §2.12) removes
the tier for a whole artifact.

**`rx_info.abi` moves `4` → `5`** with this change (§6's bump-on-change
rule). No struct offset moves — the two new stamps are `#define`s — and no
DFA artifact's bytes move at all, the first `abi` bump of which that is
true; the number versions the artifact FORMAT, not the VM, so it moves on
both engines regardless.
