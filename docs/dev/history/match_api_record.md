# match_api.md — the removed history (record, NOT normative)

This file holds the build history that `docs/spec/match_api.md` carried until
its facts-only rewrite (lane specclean, 2026-10-09, plan row `[SPEC-CLEAN]`):
revision notes, the verification ledger, rulings, walkbacks, superseded
wordings and dated row notes, in the order they stood. It is a RECORD: nothing
here is a promise. The contract is `docs/spec/match_api.md`; where a passage
below disagrees with it, the spec is right and the passage is history.

**How it was cut.** Every paragraph of the old document that the history check
(`tests/spec_history/spec_history.py`'s markers: dates, ADDENDUM, walkback
phrases, panel/ruling/lane narrative, row-tag-opened paragraphs) flags, plus
four whole blocks (the header's revision notes, old §3.5, old §9, old §10's
status box), copied VERBATIM, each tagged with the old section and line range
it came from. Mixed paragraphs are copied whole, so a current fact may appear
here beside its history; the spec states it without the history. The `abi`
change log (old §6, lines 2309-3553) is not here: it continues as
`docs/dev/history/abi_changelog.md`. The complete pre-rewrite text is
`git show aee1a570:docs/spec/match_api.md`, and
`studies/specclean/claims.tsv` maps every normative claim of that text to
its new location.

---

### [old header, lines 3-10]

This is the **spec**, not the design record: what pcrec's compiled library
(`lib/pcrec.h`) and every generated matcher actually promise, as shipped.
Per `docs/spec/CLAUDE.md`'s charter, this document states the contract; it
is actively maintained and carries no build history. Where it references
`docs/design/match_api_m4.md` or `docs/design/engine_m4.md`, that is
informational — the reasoning and panel record behind a rule, never a
second source of authority. On any disagreement between this document and
those, THIS document is what pcrec promises.

### [old header, lines 12-18]

Every rule below was checked against the shipped surface: `lib/pcrec.h`
itself, artifacts actually emitted by `build/pcrec` for representative
patterns (a `--no-captures` DFA build, a captures-default VM build, a
custom `-p` prefix, budget-limited builds), and the test cases cited
inline. Two places where the shipped surface does not match
`match_api_m4.md`'s design text are called out explicitly (§3.5, §7)
rather than silently reconciled.

### [old header, lines 20-40]

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

### [old header, lines 42-65]

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

### [old header, lines 67-77]

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

### [old header, lines 79-86]

**D61 revision (2026-08-18, same session — Frank design thread).** Two
ADVISORY forward-promise clarifications, prose only, no emitted text
quoted, nothing re-measured: §3.3's slot-latitude note is narrowed
(primary groups' `slot == number` is permanent on captures-on builds;
the different-slot latitude applies to future ref-bearing rows only)
and §6 gains the `ngroups` PERMANENT-PREFIX promise (slots
`1..ngroups` are this pattern's own groups forever; insertion
mechanisms append, never interleave). docs/dev/decisions.md D61.

### [old header, lines 88-113]

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

### [old header, lines 115-122]

**[DD-14.FB] revision (2026-08-24, D71 item 2) — the first revision that
stated a contract BEFORE it existed, and the marking mattered.** Every
revision before it recorded what shipped. That one added **§10, the
caller-provided frame buffer**, as SPECIFIED AND NOT YET BUILT. It was
here rather than in the design note alone because D71 item 2 rules the
shape "decided at docs/spec/match_api.md under D40", and because the three
existing entries' compatibility story is a fact about THIS document's
contract.

### [old header, lines 124-140]

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

### [old header, lines 142-227]

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
events but never stated the general rule; `rx_info.abi` is `27`
([EMIT-VERB], THE EMITTED-COMMENT AXIS — see §6's bump list; before it,
[OPT-DIAL], THE SPEED-VS-SIZE DIAL — every artifact of both engines gains
exactly one line in the shared prologue, `#define <PREFIX>_TUNE
"<token>"`, a closed five-token selection stamp (23-28 bytes by token);
nothing else moves at the default position `balanced`, which is
STRUCTURAL rather than measured because every cell of that row in
`src/core/tune.c` is the em-dash sentinel and its deny mask is empty; a
non-default position may move far more, which is the dial's point, but no
struct offset moves, no `rx_info` member is added or changed, and no
answer moves at any position, which is the dial's own acceptance
criterion; `25` was
[PORTFIX], A CLANG-COMPATIBILITY LABEL FIX — every scan-edge-bearing DFA
machine (or VM-hybrid inlined prefilter) gains a trailing `;` on its
`scan_views` and `scan_edge` labels, closing a label-immediately-followed-
by-a-declaration shape that gcc accepts as a `-std=gnu11` extension and
clang 21 rejects as `-Wc23-extensions` under `-Werror`; no answer moves and
the VM program region is unmoved on every axis, for the same structural
reason [OPT-EDGE] STEP 1's own bump below states; `24` was
[K50], CANDIDATE MATCH STARTS ARE CHARACTER BOUNDARIES — every artifact
gains `#define PCREC_ERR_STARTPOS (-7)` in the shared ABI block, and under a
multi-byte encoding the unanchored machine, `ENG_ATTEMPT`'s start loop and
the entries' new boundary guard all move; see §3.1's startpos paragraph,
§4's below-the-floor block and `docs/spec/tuning.md` §2.23; `23` was
[FORM-CHAR] STEP 1, the VM's ASCII-FOLD class test — see §6.3's
`_VM_CLS_FOLDS` entry and `docs/spec/tuning.md` §2.22; `22` was
[CC-DIFF] STEP 2, the VM ENTRY SHAPE: every VM artifact gains the
`<PREFIX>_VM_ENTRY_SHAPE` and `<PREFIX>_VM_PROGRAM_BYTES` stamps, and at rungs
`shared`/`forward` the entry chain's own shape moves — the three `_in` entries
carry the body, the un-suffixed entries forward to them, and a static empty
descriptor is new emitted text; the VM program region is unmoved. Before it,
21 = [OPT-EDGE] STEP 1.1, the scan-edge ENTRY DISPATCH: the entry-seed dispatch is
generalised to `is_stop && !is_dead` and precondition (8) admits an edge only
where the seed AND the prefilter reseeds — the entry block's shape moved on
every edge-bearing artifact and nothing else; before it, 20 = [DD-13b.W1.3],
COMPOSITION: on a composed artifact `groups[]` gains the
definitions' delivered rows under a leading SCOPE sort key, so `nentries`
exceeds `nnames` for the first time; invisible on a non-composed compile — atop
[OPT-EDGE] STEP 1's `19`, the shared-sentinel scan-edge dispatch, atop
[ENG-ISL] STEP 1's `18` — the VM's alternation island: a flat alternation whose
language is a finite literal set is emitted as a trie dispatch rather than
`vm_alt`'s serial resume chain, with its `<PREFIX>_VM_ALT_ISLANDS` count —
the FIRST bump to move the VM PROGRAM region itself, atop
[CC-DIFF] STEP 1's `17`, the two emitted-code spellings: `always_inline` on a
frameless VM artifact's entry-chain helpers, and the uniform-table fold with
its `<PREFIX>_DFA_UNIFORM_FOLDS` stamp, atop
[OPT-5] STEP 2's `16` — the start-pinned search: `rx_info.search_form` +
`<PREFIX>_DFA_START` — [DD-13b.W1.2]'s `15` and [CC-CLANG]'s `14`; it read
`6` when this note was written, `7` after [OPT-3], `8` after [ENG-FORM], `9`
after [OPT-K], `10` after [ENG-ABS], `11` after [ART-SIZE] and `12` after
[OPT-4]).
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

### [old header, lines 229-241]

**[DD-13b.W23.3] revision (2026-09-15) — one rule, stated where it was
missing.** §3.1.1 gains the `utf8` advance as NORMATIVE text: *from
`pos + 1`, past every byte in `0x80`-`0xBF`*, which defines the entry on
ILL-FORMED input where "the next character boundary" had no single
reading. The rule is not new behaviour — it is what [M5.0] stage 2's body
already does — and the block is quoted verbatim from a fresh `-e utf8`
build of `'a(b|c)+d'`. It is written down because a foreign consumer
comparing find-all counts against a pcrec artifact — the `mc` production
in `docs/spec/rxt_format.md` — cannot derive it from prose otherwise.
One stale clause was corrected in the same paragraph: §3.1.1 called
`byte` "the only one implemented today" three lines above its own
statement that [M5.0] stage 2 landed the `utf8` body. No entry point,
signature or return value changed, and W23 carries no `abi` event.

### [old §1, lines 251-270]

1. **Per-artifact symbols**, scoped by the caller's `pcrec_options.prefix`
   (default `"rx"`): `<prefix>_search`, `<prefix>_match`,
   `<prefix>_match_caps`, `<prefix>_info`, `<prefix>_next_pos` (§3.1.1),
   `<prefix>_valid_upto` (§3.1.2, [UTF-VALID]), and the `<PREFIX>_*` macro
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

### [old §1, lines 317-337]

   **[ABI-NS], 2026-08-18 (D60 + addendum).** The same guarded block also
   carries every emitted MACRO whose value is a pcrec-contract fact
   rather than an artifact-specific one, unprefixed and emitted
   unconditionally on every artifact (DFA-only included, the same
   "reserved but unreachable" shape §4 already had): the give-up code
   space `PCREC_ERR_STEPS`/`PCREC_ERR_FRAMES`/`PCREC_ERR_WORK`/
   `PCREC_ERR_RECURSE`/`PCREC_ERR_FLOOR` (§4 — `_RECURSE` joined and
   `_FLOOR` moved −4 → −5 at [DD-14] wave A, D71 item 1), the
   below-the-floor `PCREC_ERR_INTERNAL` (§4 — NOT a give-up, same wave,
   commit 2) and its three caller-refusal siblings `PCREC_ERR_STARTPOS`,
   `PCREC_ERR_UNSET_VAR` and `PCREC_ERR_UTF` (§4), the caps-array
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

### [old §2, lines 430-435]

The block above is the emitted text verbatim (re-quoted from a freshly
emitted artifact for this revision), with two marked exceptions: the
`struct rx_info` body is elided to §6, and `extern const struct rx_info
<prefix>_info;` is per-prefix and so lives *outside* the
`PCREC_RX_ABI_H` guard, not in this block. Four things the comments
state that a reader should not have to infer:

### [old §2, lines 437-463]

- **`rx_renderfn` carries a sizing protocol**, and it is shipped ABI
  text, not a design intention: called with `out == NULL` and
  `outcap == 0` it writes nothing and returns the length it *would*
  produce. That is how a caller sizes a buffer before rendering.
- **`rx_group_entry.ref`** is documented in the artifact only as
  "NULL/empty for the primary's own groups". **[DD-13b.W1.3] it has a
  producer now**: on a composed artifact (`pcrec --source`, see
  `docs/spec/rxt_format.md`) a row whose `ref` is non-NULL names the
  DEFINITION that declared the group, and that row is a library's group
  seen by the caller. See §6's composition subsection.
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

### [old §2, lines 480-485]

**This spelling is RULED, not provisional (D57, 2026-08-18).** The
question of renaming the per-artifact instance to buy a bare typedef
back is closed: the struct-tag form is blessed as the contract, and the
design sketch's typedef form is dead. A consumer that wants a typedef'd
name ships `typedef struct rx_info rx_info_t;` in its own header, which
touches nothing pcrec emits.

### [old §3, lines 491-494]

Every generated artifact exports, unconditionally, five `<prefix>`-scoped
symbols: the four below, plus the encoding residual `<prefix>_next_pos`
that §3.1.1 specifies (a fifth entry since [M5-SEAM], and the one place an
artifact's byte-vs-character distinction lives).

### [old §3, lines 496-502]

**[DD-14.FB] (D71 item 2): three more entries ship** —
`<prefix>_search_in`, `<prefix>_match_in` and `<prefix>_match_caps_in`,
each its un-suffixed sibling plus one argument naming where the working
storage lives. **Eight is what an artifact exports today.** §10 is their
contract, and it includes the promise that the three below are unchanged —
signature, return space and behaviour — for a caller that never calls an
`_in` entry.

### [old §3, lines 504-513]

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

### [old §3.1, lines 614-683]

- **This is what libpcre2 does, and the shape was chosen after measuring it.**
  Under `PCRE2_UTF` every mid-character `startoffset` returns
  `PCRE2_ERROR_BADUTFOFFSET`, uniformly — measured over ten patterns at both
  mid-character offsets of a two-character subject, 20 of 20 refused, with
  the same ten patterns answering normally at all three boundary offsets
  (`docs/design/utf8_measurements/out/startbnd.txt` §2, libpcre2 10.46).
  Under D26 pcrec owes the refusal, not the number.
- **The order against `startpos > n` is the one stated above**: a `startpos`
  past the end of the subject still returns `0`, as it always has. Every
  position at or beyond `n` counts as a character boundary. (libpcre2 answers
  `PCRE2_ERROR_BADOFFSET` there instead; pcrec does not change its own
  long-standing answer to match, and this is a deliberate divergence rather
  than an oversight.)
- **The anchored entries of §3.2/§3.3 carry the same guard** against
  `ctx->pos`, so a caller cannot reach the permissive behaviour by choosing a
  different entry; §10's `_in` entries inherit it from the bodies they share.
- **`<prefix>_next_pos` (§3.1.1) is the supported way to produce a valid
  `startpos`**, and the find-all loop above uses it on BOTH arms — which is why
  that loop is unaffected by this rule in either direction, ill-formed
  subjects included ([K75]).
- **`-fno-startpos-guard` selects the other semantics**, and it is a real
  alternative rather than a way to switch a check off: the artifact then
  answers at whatever position the caller named, with the automaton's own
  answer. For a leading NEGATIVE assertion that answer differs from both of
  PCRE2's UTF modes in the SUCCEEDING direction — `(?<!.)` at offset 1 of the
  four bytes `CE B1 CE B2` reports `(1,1)` — because a truncated leading
  character has no path and a negative assertion succeeds exactly where its
  body has none. **Neither of those two arms ROUNDS a caller's `startpos >
  0`**: silently advancing to the next boundary is not something a caller
  gets without asking, because a caller handed an answer for a position it
  did not ask about cannot tell that from an answer for the one it did.
- **`-fstartpos-guard=align` is the axis's THIRD value, and it is that
  rounding, asked for by name** ([UTF-VALID], D132 item 2, ruled D133;
  `docs/spec/tuning.md` §2.23). It is for a caller holding a MISALIGNED
  POINTER into valid text — one that split a buffer on arbitrary bytes. A
  `startpos > 0` inside a character is moved FORWARD over continuation bytes
  to the next character start (or `n`), ONCE, at entry, and the search runs
  exactly as if that position had been passed: `caps` offsets, `\G` and a
  lookbehind's context are all read from it. Offset 0 is never moved (it is
  never refused either). The anchored entries (§3.2/§3.3) answer `-1` at a
  misaligned `ctx->pos`, because no match begins inside a character. It is
  refused together with `-fno-startpos-guard`, and inert under `byte`. It is
  not a way to accept invalid UTF-8: under `-futf-check` (below) the check
  then runs from the ALIGNED position, stepping back behind it as for any
  `startpos`, so the bytes of the character the pointer landed inside are
  checked as the caller's real text.
- **OFFSET 0 IS NEVER REFUSED, AND ON AN ILL-FORMED SUBJECT IT IS NOT WHERE A
  MATCH IS ATTEMPTED** ([K73], Frank's 2026-09-29 ruling (a)). No character
  precedes offset 0, so a caller naming it cannot have pointed inside one; but
  a subject may BEGIN with continuation bytes (`0x80`-`0xBF`), and then offset
  0 is not a character start either. The search then begins at the first
  non-continuation byte (or at `n`), exactly as `PCRE2_MATCH_INVALID_UTF`
  advances its start offset, and every answer is the answer from there:
  `''`, `\B`, `x*` and `(?=)` report `(1,1)` on `\x80` and `(2,2)` on
  `\x80\x80`; `^`, `\A` and `\G` are FALSE at the moved start, so `^` finds
  nothing on `\x80` and `\G|b` reports `(2,3)` on `\x80\x80b` (libpcre2 10.46,
  `docs/dev/lanes/k73utf_evidence/k73_witness_10.46.txt`). An ill-formed
  LEAD byte (`0xFF`, a truncated `0xE3`) is a valid start and is attempted,
  as before. The rule has NO FLAG — it is the same under
  `-fno-startpos-guard`, which governs only a `startpos > 0` — and it is the
  one place pcrec now does what `PCRE2_MATCH_INVALID_UTF` does at a start
  offset; an explicit mid-character `startpos > 0` keeps the refusal above,
  a deliberate, stated divergence from that mode.
- **The anchored entries (§3.2/§3.3) answer `-1` at `ctx->pos == 0` on such
  a subject**, because they report only a match beginning exactly at
  `ctx->pos` and none begins at a position that is not a character start.
  libpcre2 under `PCRE2_ANCHORED` advances there too and reports the match at
  the moved start (`(1,1)` for `x*` on `\x80`); pcrec's anchored contract has
  no way to report a start other than `ctx->pos`, so this is a second stated
  divergence, and both entry shapes agree on it.

### [old §3.1, lines 749-756]

**WHAT THE ARTIFACT PROMISES ABOUT ITS OWN POSITIONS IS NOT PART OF THIS
AXIS.** Every position the ENGINE generates — an unanchored search's candidate
match starts, a failed attempt's retry, and since [K73] the first attempt of a
search at offset 0 — is a character start of the encoding, unconditionally and
under either setting of the flag. That is K49's
and K50's fix, and it has no knob: a reported match span never begins inside a
character on any subject, whichever arm the artifact carries. The flag governs
only where a CALLER may point the entry.

### [old §3.1, lines 770-782]

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

### [old Finding every match, lines 895-913]

That loop, coded exactly as written above (its aligned non-empty arm is
[K75]'s later, well-formed-subject no-op change; the twenty-six pairs below
are `byte`-encoded and read the same under it, and the ill-formed-subject
witnesses are `tests/rxtsource/fixtures/mc_illformed_utf8.rxtin`), was
compiled against real artifacts and run against `python3 re.finditer` on twenty-six
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

### [old §3.1.1, lines 1079-1099]

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
byte-compiled caller wrong against a UTF-8-compiled artifact. **[M5.0]
stage 2 landed that UTF-8 body** — `$_next_pos` under `utf8` skips forward
over continuation bytes to the next character boundary — so the seam's
prediction is now a shipped fact rather than a plan, and the loop above
compiles unchanged against a `-e utf8` artifact. (The caveat's other half —
"the ASCII encoding, `PCREC_ENC_ASCII`" — is also
gone by rename: the constant is `PCREC_ENC_BYTE` and the CLI value is
`byte`, since the semantics were always "every byte is a character",
which is not what ASCII says. §8.2 records the rename.)

### [old §3.1.2, lines 1112-1112]

#### 3.1.2 `<prefix>_valid_upto` — the subject validator ([UTF-VALID])

### [old §3.2, lines 1180-1189]

**`"unwrapped"` — the anchored automaton ([ENG-ABS], 2026-08-29).** The
artifact carries a THIRD machine: the same tables its forward scan is
built from, WITHOUT the start-anywhere self-loop, run forward from
`ctx->pos`. There is no later start to reject and no backwards pass to
recover a start with, so a failing probe stops at the first byte that
cannot continue a match beginning here, and a succeeding one costs one
forward scan rather than a forward and a reverse.
`docs/design/anchored_match_unwrapped.md` is the note; §3 there is the
argument that this reports the same length the other form reports, on
every input.

### [old §3.2, lines 1191-1214]

**`"search-filter"` — the original shape, and still the form on some
artifacts.** The entry runs the artifact's ordinary UNANCHORED search
and rejects any match whose start is not `ctx->pos`. One COST
consequence is worth a caller's attention: on a FAILING match-here, the
underlying search does not know the question is anchored — it may skim
the remainder of the subject hunting a later match the filter will then
discard (the state-0 `memchr` skip keeps this a skim rather than a
per-byte walk), where an anchored body fails at the first divergent
byte. **A caller issuing many expected-to-fail `<prefix>_match` probes
against long subjects is in this form's worst case, and can read off the
artifact whether it is in it.** Five populations still take this form:
an artifact whose engine is the per-start attempt loop
(`<PREFIX>_DFA_SCAN "attempt"`, i.e. a `^`- or `\G`-bearing pattern), an
artifact that matches nothing (`"empty"`), one whose anchored machine
exceeded a DFA cap — a SELECTION OUTCOME, never a refusal — any
build under `-fno-anchored-dfa` (`docs/spec/tuning.md` §2.15), and — since
[K53-SELRETRY], 2026-09-10 — an artifact whose anchored machine pcrec
DROPPED so the artifact would fit under an emitted-size cap
(`docs/spec/limits.md` §8, "The optional-contributor drop"). **That last
one is the population this cost note is most relevant to**, because it is
the only one where a caller could have had the faster form and lost it to a
size limit rather than to the pattern's own shape: it is identifiable by
`<PREFIX>_ENGINE_SEL "size-cap-retry"`, and raising `--max-emit-bytes` is
what gets the anchored machine back.

### [old §3.3, lines 1236-1251]

Same anchoring promise as `<prefix>_match`, and the same two forms
(§3.2) — under `"unwrapped"` this entry delegates to `<prefix>_match` and
fills the spans itself, so `caps_out[0]` is `[ctx->pos, ctx->pos +
length)` by construction rather than by a filter that proved it. Plus a
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

### [old §3.5, lines 1312-1312]

### 3.5 A design-vs-shipped note: give-up codes are uniform, not collapsed

### [old §3.5, lines 1314-1318]

`match_api_m4.md` §3 as originally written required `<prefix>_match` to
**collapse** every give-up code to a bare `-1` (D42.3's reservation on
the `rx_matchfn` type). **That collapse does not exist in the shipped
artifact**, on either engine. Both bodies, quoted from freshly emitted
artifacts:

### [old §3.5, lines 1320-1337]

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

### [old §3.5, lines 1339-1354]

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

### [old §3.5, lines 1356-1367]

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

### [old §3.5, lines 1369-1380]

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

### [old §3.5, lines 1382-1387]

This is the shipped, correct state: `docs/dev/decisions.md` D49
supersedes D42.3 and rules the uniform-codes contract these artifacts
implement — `match_api_m4.md`'s own §3 carries the D49 amendment in
place. A caller that only tests `r < 0` for "did it match" is unaffected
either way; a caller doing an exact `== -1` comparison sees give-up
codes as distinct values, not folded into `-1`.

### [old §3.5, lines 1389-1405]

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

### [old §3.6, lines 1443-1457]

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
measurement ever justify it (`docs/dev/plan.md` `[OS-4]`) — this is not
scoped to any one caller, `(?:P)\z` benefits from it identically to
every other `\z`-bearing pattern.

### [old §3.6, lines 1459-1467]

**The ANCHORED-DFA cost this sentence used to defer to `[OPT-2]`/`[ENG-ABS]`
IS BUILT** (2026-08-29): a `\z`-bearing pattern still selects the DFA, and its
`<prefix>_match` now runs the artifact's own anchored machine from `ctx->pos`
rather than the unanchored search with a start filter (§3.2's `"unwrapped"`
form). Measured on this exact idiom over the comparative bench's 85 compliance
subjects: the matching split goes from 2.074× behind the backtracking VM to
**1.031×**, and short valid emails from 1.223× behind to **0.482×** — ahead of
it. Nothing about the idiom itself changed; it is the entry that got cheaper.
`docs/design/anchored_match_unwrapped.md` §7.1 has the numbers and the method.

### [old §4, lines 1502-1513]

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

### [old §4, lines 1527-1535]

**[ABI-NS], 2026-08-18 (D60).** These four were spelled `<PREFIX>_ERR_STEPS`/
`_FRAMES`/`_WORK`/`_FLOOR` before this date, one set per artifact even
though every artifact emitted identical values. D60 ruled the values a
pcrec-CONTRACT fact, not a per-artifact one, and moved them unprefixed
into the shared `PCREC_RX_ABI_H` block (§2) — the per-`<PREFIX>` spelling
is DELETED, not aliased. The block above is quoted verbatim from a fresh
`-p rx --no-captures` build of `'a(b|c)+d'`; a `-p foo` build of the same
pattern emits the byte-identical lines (§1/§2's cross-prefix
identity property, now covering these constants too).

### [old §4, lines 1537-1545]

**[DD-14] wave A, 2026-08-24 (D71 item 1).** `PCREC_ERR_RECURSE` joins the
block and `PCREC_ERR_FLOOR` moves −4 → −5 — D49's own re-open clause
("getting the partition wrong pre-release costs a renumber and nothing
else"), exercised. The CODE is reserved now; the recursion-depth COUNTER
that would produce it is NOT in the default artifact (D71 item 1 — a
future `[V-H]` diagnostic-generation axis, a separate emitted variant, not
a runtime flag). No arm in any emitter returns `PCREC_ERR_RECURSE` today —
it is exactly as unreachable on every artifact as `PCREC_ERR_STEPS` etc.
are on a DFA-only one, the same "reserved but unreachable" shape.

### [old §4, lines 1547-1563]

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

### [old §4, lines 1588-1595]

**[K50], 2026-09-06. `PCREC_ERR_STARTPOS` IS THE SECOND BELOW-THE-FLOOR CODE,
AND IT IS A REFUSAL OF THE CALL RATHER THAN A REPORT ABOUT THE ENGINE.** Every
value in `[PCREC_ERR_FLOOR, -2]` says the engine ran and exhausted something.
`PCREC_ERR_INTERNAL` says the artifact caught its own inconsistency. This one
says the CALLER named a `startpos` (or a `ctx->pos`) that is not a character
boundary of the artifact's encoding, so no attempt was made and no budget was
touched — §3.1 states the rule and `docs/spec/tuning.md` §2.23 states the axis
that selects the other semantics.

### [old §4, lines 1613-1620]

**[UTF-VALID], 2026-09-30 (D133). `PCREC_ERR_UTF` (−9) IS THE THIRD CALLER
REFUSAL, AND THE FIRST BELOW-THE-FLOOR CODE A COMPOSED CALL SITE PROPAGATES.**
It means an artifact compiled with `-futf-check` found an ill-formed sequence
beginning in the checked range `[startpos − LB, n)` (§3.1), so the call was
refused before any attempt; `caps` is untouched, and
`<prefix>_valid_upto(s, n, startpos)` (§3.1.2) is the offset. It is one code
for every kind of ill-formedness (D26: pcrec owes the refusal and the offset,
not PCRE2's twenty `PCRE2_ERROR_UTF8_*` values).

### [old §5, lines 1662-1667]

**[ABI-NS], 2026-08-18 (D60).** `PCREC_UNSET` was spelled `<PREFIX>_UNSET`
before this date — one identical value emitted once per artifact, moved
unprefixed into the shared `PCREC_RX_ABI_H` block (§2) since it is a
pcrec-contract fact, not a per-artifact one. The per-`<PREFIX>` spelling
is DELETED, not aliased. `<PREFIX>_NCAPS` is unaffected: its VALUE
genuinely varies per artifact (below), so it stays per-prefix.

### [old §5.1, lines 1705-1709]

C6 above says every slot `0..ncaps-1` is written on a completed match; it
does not by itself say *which* value a group inside a repeated construct
ends up holding when that group did not run in every iteration. Two rules
govern this, measured three-way unanimous (python `re`, libpcre2, and
pcrec agree) and now part of the shipped contract, not an addendum to it:

### [old §5.3, lines 1782-1801]

**[OPT-1], 2026-08-25: THAT MEASUREMENT NOW READS DIFFERENTLY, and the
limitation NARROWS rather than closing.** §10.9's tiered entry moves the
stamped default storage off the entry's own frame and onto a
non-inlined internal function only a `PCREC_ERR_FRAMES` give-up reaches. Re-MEASURED on the same
build: `<prefix>_search`'s frame is **3,184 bytes** and the internal
function's is 131,216. **The fit criterion is free STACK HEADROOM AT THE
CALL SITE (entry + deep, 134,400 bytes for this artifact class), not
thread-stack size as such** — a call's frame lands wherever the stack
pointer already sits, so a thread's nominal size only equals the headroom
available to it when the call happens at depth ~0 (`docs/spec/limits.md`
§5 states the general rule). At depth ~0 on a musl-default **128 KB**
thread — the measured, worked example — that artifact now
**matches every subject the fast tier holds** — the "faults on any subject,
a 2-byte one included" sentence is no longer true — and faults only on one
deep enough to escalate. **The remedy is still `_in`**, and it is still the
only way to get a guarantee: which subjects escalate is a property of the
pattern and the subject, not something a caller can bound in advance.
`docs/dev/known_issues.md` K33 carries the narrowed statement, and
`tests/thread/run_stackdepth_tests.sh` pins both halves — the small entry
frame, and the deep tier still dying.

### [old §6, lines 1961-1967]

**[FINDINGS] B1, 2026-09-27 — `findings`.** Appended after `nvars` on
[DD-13c]'s terms: no existing member's offset moves, and `abi` bumps 39 → 40
with the `<PREFIX>_FINDINGS` stamp it mirrors (§6.3). D43 makes `rx_info` the
canonical machine-readable record, so the macro alone would be invisible to a
linked binary. The value names the analysis a byte-rate came from **in plain
text**, so a shipped binary discloses the analysis name it was built under
(`docs/spec/findings.md` §5 states it; name bundles neutrally).

### [old §6, lines 1969-1972]

**[DD-13b.W1.2], 2026-08-31 — `name` and `nentries`.** Appended after
`match_form` on [DD-13c]'s terms: no existing member's offset moves, and
`abi` bumps 13 → 14 because the emitted scaffolding grew (D76 — the rule
is about the scaffolding as a whole, not about this struct alone).

### [old Composition — what a caller sees of a li, lines 2004-2008]

**[DD-13b.W1.3], 2026-09-03.** `pcrec --source FILE` composes: the target
pattern's `(?&…)` calls bind DEFINITIONS declared in that file or in a file
it `lib`s (`docs/spec/rxt_format.md`). What follows is the whole of what
composition changes about this struct; a caller of a single-pattern artifact
is unaffected in every particular.

### [old Composition — what a caller sees of a li, lines 2090-2097]

**[DD-13b.W1], 2026-08-30 — `nnames`'s comment was STALE, and the way it
was stale is worth one paragraph.** It read *"0 until module
'named-groups' lands (still true as of this writing — verified:
`'(?<g>a)'` still refuses "requires module 'named-groups'")"*. Module
`named-groups` shipped 2026-08-18 (`src/parse/mod_named_groups.c`,
D79's five ruled modules), so the CLAIM has been false for twelve days —
but **the quoted verification still reproduces its quoted output**, because
the module is GATED and not enabled by default. MEASURED 2026-08-30:

### [old Composition — what a caller sees of a li, lines 2109-2118]

So a reader who did the honest thing — re-ran the command the comment
offers — would have been told the stale sentence was current. That is
the failure mode `docs/dev/learnings.md` §3 names one level up from
where it usually bites: not a check that shares a source with its
subject, but a CITED MEASUREMENT that outlived the fact it was cited for
while still reproducing. A verification command pins an OUTPUT; it does
not pin the REASON for that output, and this comment's reason changed
from "the module does not exist" to "the module is not on by default"
with no visible effect. Corrected in the struct above by naming both
reasons separately.

### [old Composition — what a caller sees of a li, lines 2120-2126]

**[ENG-ABS], 2026-08-29 — `match_form`.** Appended after `prefilter` on
[DD-13c]'s own terms and for its own reason (a consumer with no
preprocessor). Its NULL rule is NOT `scan`'s: `scan` is non-NULL on a
hybrid, because a hybrid contains a DFA scan; `match_form` is NULL there,
because a hybrid's `<prefix>_match` is the VM's anchored body and this
field's value set does not describe it. `abi` bumps 9 → 10; no existing
member's offset moves.

### [old Composition — what a caller sees of a li, lines 2128-2138]

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

### [old Composition — what a caller sees of a li, lines 2152-2161]

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

### [old Composition — what a caller sees of a li, lines 2169-2177]

**[ABI-NS], 2026-08-18 (D60 addendum): `engine`'s number-only contract now
has names.** Until this date, this field's comment read "1 = DFA, 2 = VM.
The artifact spells these ENGM_DFA/ENGM_VM in a COMMENT only — no such
constant is #defined anywhere, so compare against the numbers" — a
COMMENT-only convention naming the internal `select_engine.c` enum
spelling (`ENGM_DFA`/`ENGM_VM`), never an emitted symbol. D60's addendum
ruled this the same class of pcrec-contract fact as the give-up code
space (§4) and `PCREC_UNSET` (§5): a universal, artifact-independent
value with no emitted name, which its membership rule closes. `PCREC_ENGINE_DFA`

### [old Composition — what a caller sees of a li, lines 2179-2184]

(1) and `PCREC_ENGINE_VM` (2) are now real `#define`s in the shared
`PCREC_RX_ABI_H` block (§2), pinned to the numbers the field already
stamped — this NAMES the existing contract, it does not renumber it. The
internal `ENGM_*` enum stays internal and is never exported; the emitted
`.engine` comment now reads `PCREC_ENGINE_DFA=1 / PCREC_ENGINE_VM=2` as
quoted above, verbatim from a fresh build.

### [old Composition — what a caller sees of a li, lines 2195-2210]

**`ngroups` is additionally a PERMANENT PREFIX-LENGTH promise (D61,
2026-08-18; advisory forward promise — no emitted text changes with
it).** On any captures-on build, slots `1..ngroups` of the caps array
are THIS pattern's own groups in its own left-to-right numbering, so
`ngroups <= ncaps - 1` with equality on every build from a single
pattern. Slots above `ngroups` are reserved for insertion/composition
mechanisms: a ref-bearing producer (§2's "labeled insertion path")
APPENDS its delivered slots and never interleaves with or renumbers the
primary prefix. **[DD-13b.W1.3] that producer exists**: a composed
artifact has `ngroups < ncaps - 1`, and every slot in between belongs to
a bound definition. A caller indexing `caps` by the pattern's own group
numbers is therefore safe against every future insertion feature. The
promise pins the caps LAYOUT, not group NUMBERING —
`rx_group_entry.slot` remains the number-to-slot indirection for
whatever numbering a future insertion design chooses (§3.3's narrowed
latitude note).

### [old Composition — what a caller sees of a li, lines 2218-2235]

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

### [old Composition — what a caller sees of a li, lines 2237-2246]

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

### [old Composition — what a caller sees of a li, lines 2278-2316]

- **`rx_ctx.ncap`'s "watermark mid-match" reading has no producer.**
  (It is an `rx_ctx` field rather than an `rx_info` one, but it belongs
  with these.) Every call site in every emitted artifact sets
  `ctx.ncap = 0`; nothing ever advances it, so no caller can observe a
  watermark. It is reserved for a future mid-match view, exactly as
  `nnames`/`groups` are reserved for `named-groups`.
- **WHAT A DEFAULT ARTIFACT CARRIES BY WAY OF COMMENTS, since
  [EMIT-VERB]** (D112; `docs/spec/tuning.md` §2.24). Exactly two things,
  and both are emitted under every setting: (1) the **provenance line**,
  `/* Generated by pcrec VERSION (abi N). Pattern: <pattern> */` — VERSION
  is `PCREC_VERSION` (`lib/pcrec.h`, D115, [REL-1.4]) and N is the same
  digit `rx_info.abi` carries below; the abi digit was added by a same-day
  rider (D112 item 2) and the version by [REL-1.4]'s own rider, each
  riding the abi bump its own change already opened rather than taking a
  second one (D76/D94's addendum shape), so the line names pcrec, its
  version AND the abi as the ruling always specified (the version moved
  `0.1.0-beta` -> `0.2.0-beta` at [REL-0.2], 2026-10-03: the string alone
  changed, not an abi event, same byte length) —
  on the `.c` and on the
  paired `.h`; and (2) the **shared `PCREC_RX_ABI_H` type block's
  doc-comments** — `rx_ctx`'s field notes, `rx_matchfn`'s return-space
  paragraph, the give-up and below-the-floor code notes, `rx_renderfn`,
  `rx_group_entry` and every `rx_info` member's note. That block is the
  one §2 calls the shipped doc-comment an embedder actually reads, and it
  is why it is essential. Everything else the emitter can say — the
  orientation block, the table and state legends, the per-label role
  lines, the entry-point paragraphs, the encoding residuals' own
  doc-comments and the feature-set line — is emitted only under
  `-fcomments`. Note the last of those: `PCREC_FEATURE_SET` and
  `PCREC_FEATURE_MODULES` (§6.3) still carry the feature set on the `.c`,
  but the paired `.h` records it in NO form in a default build.
**THIS PARAGRAPH IS THE `abi` CHANGE LOG, and it is the only one** (D76
addendum, [REVW.A1], 2026-09-19). Every bump's own D76/D94 ritual carries a
`docs/spec/` hunk, so the ritual maintains this narrative by construction —
which is why it is gap-free from `2` to `42` while the three narrative copies
that lived in `src/gen/emit_dfa.c`, `src/gen/CLAUDE.md` and the codegen
suite's failure message had each drifted. Those are now a pointer, a pointer,
and a check's message copied FROM here. **A bump updates this paragraph, in
the bump's own commit.**

### [old Composition — what a caller sees of a li, lines 3554-3586]

**What a caller may assume, stated once in caller terms rather than left
to accumulate from six bump-event paragraphs (D76, D40 regime 1).** The
paragraph above narrates each bump's OWN cause; this is the general rule
those events are instances of. **What changes at a bump:** `abi`
(`rx_info.abi`, mirrored nowhere else) is the version of the emitted
SCAFFOLDING AS A WHOLE — every declaration, comment and macro in the
artifact, not merely `struct rx_info`'s own layout — so a change to any
of it, whether or not a struct offset moves, IS an `abi` bump; [DD-13]'s
`3` → `4` (§6.3's two new stamp lines, no struct offset), [DD-13c]'s
own `5` → `6` (both a struct append AND new stamp lines), [OPT-3]'s
`6` → `7` (the first that moves emitted PROGRAM bytes — the DFA scan's
tables and loop lines — with NO struct offset moving at all) and
[ENG-FORM]'s `7` → `8` (the largest emitted-text event so far, and still no
struct offset moved) span the
range this rule covers, and not one of them is a smaller event than the
others by this document's own promise. **What is fixed within one `abi` number:**
the emitted output is byte-exact WHOLE-FILE for a given pattern, prefix
and option set — comments included — which is what `abi` exists to let
a caller detect the boundary of; **"option set" does real work in that
sentence since [EMIT-VERB]** (`tuning.md` §2.24), because `-fcomments` and
`-fno-comments` are two option sets and their artifacts differ by design —
in comment TEXT and in nothing else, so the object file, the
comment-excluded size and every emitted `#define` are identical between
them; a caller diffing two artifacts compiled
at the same `abi` and finding them to differ has found a pcrec bug, not
an expected drift. **What a bump does NOT carry, pre-v1:** no
compatibility story and no announcement beyond the stamp itself — D40
regime 1 rules pre-v1 breaks unconstrained in substance, and for an
`abi` bump specifically the bumped NUMBER already discharges D37's
announced-boundary requirement; there is no separate deprecation cycle,
migration note, or advance notice to expect. A caller that wants
version-negotiation semantics from `abi` is building on a promise this
document does not make until a future v1 declaration says otherwise (§9).

### [old §6.0, lines 3600-3600]

### 6.0 Duplicate-name runs — the sort key and the caller's algorithm ([M6.5.2], 2026-08-22)

### [old §6.0, lines 3615-3624]

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

### [old §6.3, lines 3664-3665]

**[DD-13], 2026-08-25: THE D46 FAMILY SPLITS IN TWO, and only one half is
engine-scoped.**

### [old §6.3, lines 3680-3682]

  **[DD-13c], 2026-08-25 — "UNCONDITIONAL" IS TWO RULES, NOT ONE, AND THIS
  PARAGRAPH USED TO CONFLATE THEM.** The unit that owns a stamp is the
  MECHANISM the stamp names, not the artifact kind that usually carries it:

### [old §6.3, lines 3684-3703]

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

### [old §6.3, lines 3705-3710]

  **[OPT-4], 2026-08-29: a FOURTH selection on the same neighbourhood,
  `<PREFIX>_VM_PREFILTER_LANG`** — and it is a THIRD independent question,
  not a refinement of either macro above. `_VM_PREFILTER` says whether the
  VM runs a DFA ahead of its program; `_DFA_PREFILTER` says what
  candidate-start filter that DFA's own scan carries; this says WHICH
  LANGUAGE the DFA recognises. Two values:

### [old §6.3, lines 3748-3752]

  **[OPT-HYB-RESEED], 2026-09-29 (abi 49): `<PREFIX>_VM_RESEED`, what the
  hybrid's RETRY does after a failed attempt** (`tuning.md` §2.35). Same
  IFF as `_VM_PREFILTER_LANG` — every artifact whose `_VM_PREFILTER` reads
  `"hybrid"`, and no other. The value is the name of the first-match row
  that fired (`pcrec --list-axes` prints the table, axis `hyb-reseed`):

### [old §6.3, lines 3769-3773]

  **[K50] / [UTF-VALID], 2026-09-30 (abi 50): `<PREFIX>_STARTPOS_GUARD`,
  what the entries do with a caller's mid-character position** (`tuning.md`
  §2.23). UNCONDITIONAL, on every artifact of both engines — a family (a)
  selection fact riding the shared prologue, because the axis belongs to
  the ENTRIES rather than to either engine:

### [old §6.3, lines 3781-3783]

  **[UTF-VALID], 2026-09-30 (abi 50): `<PREFIX>_UTF_CHECK`, whether the
  entries refuse an ill-formed subject** (`tuning.md` §2.36). UNCONDITIONAL,
  beside `_STARTPOS_GUARD`, for the same reason:

### [old §6.3, lines 3795-3799]

  **[OPT-3], 2026-08-26: a THIRD `_DFA_*` macro, `<PREFIX>_DFA_TABLE`**, on
  exactly the same footing and under exactly the same IFF — every artifact
  that CONTAINS a DFA scan, which is every DFA artifact and every VM hybrid,
  and no other. It names the ENCODING of that scan's transition table
  (`docs/design/premultiplied_dfa_table.md`, `docs/spec/tuning.md` §3):

### [old §6.3, lines 3811-3820]

  **[CC-DIFF] STEP 1, 2026-09-03: the encoding this stamp names is the
  selection that was MADE, and after the uniform fold an artifact can carry
  that selection without carrying a table.** `<PREFIX>_DFA_UNIFORM_FOLDS`
  (below) is where a consumer reads how many tables are actually there. The
  stamp does NOT fall to `"none"` when everything folds: the representation
  was still chosen, and it still fixes the folded constant's value (`65535`
  under `"premultiplied"`, `-1` under `"indexed"`), so reporting `"none"`
  would erase a live fact rather than correct a stale one. `"none"` keeps its
  existing meaning, a scan with no numeric transition table by CONSTRUCTION —
  `_DFA_SCAN "attempt"` or `"empty"`.

### [old §6.3, lines 3822-3832]

  **It has no `rx_info` mirror, deliberately** —
  unlike `scan` and `prefilter`, whose mirrors §3.2 of `tuning.md` records.
  §6.3's (a)/(b) split is a rule about MACROS and makes the macro owed; the
  two struct fields were a separate D40-addendum layout decision at [DD-13c],
  justified by a header-less consumer (`dlopen`, FFI, a tool walking several
  `<prefix>_info` symbols), and measured 2026-08-26 no such consumer exists
  yet — the abi-6 fields are still unread. An unread mirror for THIS stamp
  would be built ahead of a measured need (D77). **The trigger, so it need not
  be re-derived: the first consumer that reads `rx_info.scan` or
  `rx_info.prefilter` at run time makes `table` owed too**, and it is an
  append at the end of the struct at that point, moving no existing offset.

### [old §6.3, lines 3846-3855]

  All four values come from ONE derivation per engine (`unanch_start`,
  `attempt_cand` in `src/gen/emit_dfa.c`) read by every site that needs
  them — the emitted loop, the DFA artifact's stamp, the hybrid's stamp —
  so a stamp cannot disagree with the loop it describes unless the
  derivation itself is wrong, in which case the loop is wrong too.
  **[CC-DIFF] STEP 1, 2026-09-03: a FOURTH `_DFA_*` macro,
  `<PREFIX>_DFA_UNIFORM_FOLDS`** — on exactly the same footing and under
  exactly the same IFF as `_DFA_TABLE`: every artifact that CONTAINS a DFA
  scan, which is every DFA artifact and every VM hybrid, and no other. It is
  an INTEGER, not a string:

### [old §6.3, lines 3897-3899]

  **[OPT-ENDWIN], 2026-09-22: `<PREFIX>_END_WINDOW` — HOW FAR FROM THE
  SUBJECT'S END A MATCH MAY BEGIN.** Family (a): on EVERY artifact pcrec
  emits, both engines, because the analysis is neither engine's.

### [old §6.3, lines 3924-3925]

  **[OPT-REQBYTE], 2026-09-22: `<PREFIX>_REQ_BYTE` — A BYTE EVERY MATCH MUST
  CONTAIN.** Family (a): on EVERY artifact pcrec emits, both engines.

### [old §6.3, lines 3955-3957]

  **[OPT-REQPOS] tier 2b, 2026-09-22: `<PREFIX>_REQ_RUN` — A LITERAL RUN
  EVERY MATCH MUST CONTAIN.** Family (a): on EVERY artifact pcrec emits, both
  engines.

### [old §6.3, lines 3969-3980]

  The run's bytes as lowercase hex, then `@`, then the index within them of
  the member the emitted `memchr` scans for; or `"none"` at a length below 2,
  which is `<PREFIX>_REQ_BYTE`'s own case. Hex because a run is arbitrary
  bytes inside a `#define`'s string body; the index because it is the one fact
  about the emitted check a reader cannot derive from the bytes, and because
  `<PREFIX>_REQ_BYTE` is exactly `bytes[idx]` wherever position `idx` is an
  exact byte — which is what makes the two stamps checkable against each
  other. **Since `abi` 59** a run whose positions are not all exact bytes
  carries `/` and each position's mask `K` in hex: `T` (the bytes) is each
  position's lower member and `(x & K) == T` its membership test; an exact
  run's text is unchanged. `tuning.md` §2.28 carries the derivation. No
  `rx_info` mirror, its sibling's reason.

### [old §6.3, lines 3982-3984]

  **[OPT-PRECHECK-ADMIT], 2026-09-23: `<PREFIX>_REQ_WHY` — WHETHER THE
  ARTIFACT ACTED ON EITHER FACT, AND WHY NOT.** A closed four-token
  selection stamp, family (a): on EVERY artifact pcrec emits, both engines.

### [old §6.3, lines 3990-3995]

  | value | what it says |
  |---|---|
  | `"emitted"` | the artifact emits a pre-check, on the byte or run its two siblings name — since `abi` 60 possibly LED by a rarer necessary-set byte's one-byte check (`tuning.md` §2.40; the stamp says whether, not in which shape), and since `abi` 61 possibly HANDED OFF (`<PREFIX>_REQ_HANDOFF`, below) |
  | `"none"` | nothing is necessary — no byte and no run (the analysis found neither, or `-fno-req-byte` denied them) |
  | `"one-attempt"` | declined: the search route tries ONE start position, so a whole-window pass in front of it can only add work |
  | `"dominated"` | declined: the artifact's own candidate-start `memchr` already scans a byte at least as rare |

### [old §6.3, lines 3997-4004]

  `"none"` here holds **if and only if** `<PREFIX>_REQ_BYTE` AND
  `<PREFIX>_REQ_RUN` are both `"none"` (since `abi` 59; before it the byte
  alone decided, every run byte being a set member). Any other value asserts
  that a byte or a run WAS derived, and only `"emitted"` asserts that the
  artifact tests it — so a consumer asking "does this artifact reject
  a subject in one pass" reads THIS stamp and then its siblings for the value,
  never the siblings alone. `tuning.md` §2.29 carries both rules and their
  measured populations. No `rx_info` mirror, its siblings' reason.

### [old §6.3, lines 4006-4009]

  **[K82] (B), `abi` 61: `<PREFIX>_REQ_HANDOFF` — WHERE THE SEARCH BODY'S
  SCAN BEGINS.** Family (a): on EVERY artifact pcrec emits, both engines
  (Frank's ruling, 2026-10-05: a stamp varies by engine family, never by
  presence within one; "does not apply" is a value).

### [old §6.3, lines 4036-4038]

  **[START-SET] stage 2, `abi` 62: `<PREFIX>_VM_START_SCAN` — WHERE A VM
  ATTEMPT CAN START.** Family (a): on EVERY artifact pcrec emits, both
  engines, beside `<PREFIX>_REQ_HANDOFF` and for its ruling.

### [old §6.3, lines 4060-4061]

  **[FINDINGS] B1, 2026-09-27: `<PREFIX>_FINDINGS` — WHICH FINDINGS THIS
  ARTIFACT WAS BUILT FROM.** Family (a): on EVERY artifact, both engines.

### [old §6.3, lines 4082-4091]

  **[OPT-LITSCAN] S4 C1, 2026-10-03 (`abi` 58): `<PREFIX>_RUN_WORDS` — HOW
  MANY RUN COMPARES THE OVERLAP ROW WROTE.** On EVERY artifact, both engines.
  An ACTIVITY count, which (b) below keeps VM-only, and it is here instead
  because the mechanism it counts is both engines': the run compare
  (`docs/spec/tuning.md` §2.38) writes the DFA scan's run term and run
  pre-check as well as the VM's literal runs and island chains. Since
  [MEMFN] M1b (2026-10-07, no `abi` event: not a byte moved) the run compare
  is pcrec-memory-functions' (`memfn/src/runcmp.c`), and the kit writes this
  line too, as the first of its three lines (the two below follow it); its
  value is still an unquoted integer.

### [old §6.3, lines 4097-4107]

  **The IFF: it is the number of literal-run compares this artifact writes as
  word compares** (the `overlap` row: an exact run of length 3, 5-7 or 9-15;
  and since `abi` 59 the `words` row: a masked run, `tuning.md` §2.39),
  counting each compare once whatever engine wrote it; any other exact run
  compare is a `memcmp` and is not counted. `0` on every
  artifact that writes none and under `-fno-run-overlap`. It is written after
  the engine body — beside the `rx_info` definition, `<PREFIX>_FINDINGS`'
  placement — because a DFA artifact's compares sit in file-scope blocks
  emitted after the prologue. A COUNT, `_VM_LIT_RUNS`' reason. What a
  consumer may NOT conclude: anything about the answers, which are identical
  either way. No `rx_info` mirror (D77).

### [old §6.3, lines 4109-4113]

  **[MEMFN] R4a′, `abi` 63, 2026-10-05 (the stamps' own `abi` event): `<PREFIX>_MEMFN_FORMS`
  and `<PREFIX>_MEMFN_LIBC` — WHAT THE SEARCH-CODE KIT RENDERED, AND WHICH
  LIBC FUNCTIONS THE ARTIFACT CALLS.** On EVERY artifact, both engines; the
  pair is written by pcrec-memory-functions (`memfn/`, D146/D147) and sits
  directly after `<PREFIX>_RUN_WORDS`.

### [old §6.3, lines 4157-4160]

  **[MEMFN] RQ-3, `abi` 71, 2026-10-09 (D155 addendum 2):
  `<PREFIX>_SIMD_GUARDED_BYTES` — HOW MANY BYTES OF THE ARTIFACT SIT UNDER A
  CPU-LEVEL GUARD.** On EVERY artifact, both engines, written by pcrec
  directly after `<PREFIX>_MEMFN_LIBC`; an unsigned integer.

### [old §6.3, lines 4204-4206]

  **[OPT-ANCHOR-VM], 2026-09-22: `<PREFIX>_VM_START` — WHERE AN ATTEMPT MAY
  BEGIN.** A closed three-token selection stamp, on EVERY VM artifact,
  hybrids included, and never defined on a pure-DFA artifact:

### [old §6.3, lines 4233-4237]

  **[OPT-VMFL], 2026-09-02: `<PREFIX>_VM_FRAMELESS`, and it is (b) for
  `_VM_CALL_SPLICED`'s reason rather than a new one.** It is not a decision
  the compiler MADE before emitting — there is no frameless mode anywhere
  upstream — it is what the emitted program turned out to CONTAIN,
  discovered by emitting.

### [old §6.3, lines 4261-4271]

  **[CC-DIFF] STEP 1, 2026-09-03: THIS MACRO NOW REPORTS A SECOND FACT ABOUT
  THE SAME ARTIFACT, and it is deliberately the SAME macro rather than a new
  one.** `1` additionally means that the artifact's eight VM entry-chain
  statics carry `static inline __attribute__((always_inline))` (the abi-17
  entry above lists them); `0` means none of them does. A second stamp —
  `<PREFIX>_VM_INLINE_CHAIN`, say — was considered and REJECTED: it would
  carry the same value as this one BY CONSTRUCTION, since the emitter derives
  both from the one `has_push` bool, and a second spelling of one fact is the
  shape this project has had to unpick twice ([CC-CLANG]'s `strstr` for a
  push needle; the `_FAST_FRAMES` discriminator). A consumer that wants to
  know whether the entry chain is inlined reads this macro.

### [old §6.3, lines 4273-4284]

  **[CC-DIFF] STEP 2, 2026-09-04: THAT SECOND FACT IS NOW A NECESSARY AND NO
  LONGER A SUFFICIENT CONDITION, and `<PREFIX>_VM_ENTRY_SHAPE` carries the
  rest of it.** The inline attribute stopped being a boolean when STEP 2 made
  the entry chain a four-rung ordinal (`docs/spec/tuning.md` §2.21): a
  frameless artifact may carry the attribute on all eight statics (`inline`,
  `forward`), on seven with the matcher `noinline` instead (`shared`), or on
  none at all (`plain`, which AUTO selects above the size term where the
  forward rungs are illegal). So this macro's `1` now means the artifact IS
  ELIGIBLE for the attribute, and the SHAPE stamp says what was actually
  emitted. `0` still means none of them carries it, exactly as before — a
  framed artifact is `plain` by construction and there is no second route to
  `0`.

### [old §6.3, lines 4286-4290]

**[CC-DIFF] STEP 2, 2026-09-04: `<PREFIX>_VM_ENTRY_SHAPE` and
`<PREFIX>_VM_PROGRAM_BYTES`, and they are (b) for `_VM_FRAMELESS`'s reason.**
There is no entry-shape MODE upstream of the emitter either: the rung is
chosen where the program has just been emitted, from the program's own size
and from what it turned out to contain.

### [old §6.3, lines 4311-4317]

**Since `abi` 54 (K79) the size is measured at the CANONICAL prefix length,
two bytes**: the program is emitted under a two-byte placeholder prefix and
the caller's `-p` spelling is written onto the finished text afterwards
(`limits.md` "Size limits and the prefix"). So the number is the program's
length as it reads at `-p rx`, the same under every prefix, and the rung it
chose is too. Before 54 it counted the prefix's own bytes, and a long enough
prefix pushed an artifact across the knee.

### [old §6.3, lines 4332-4335]

**[ENG-ISL] STEP 1, 2026-09-03: `<PREFIX>_VM_ALT_ISLANDS`, and it is (b) for
`RX_ALTCLS_FACTORED`'s reason.** There is no island MODE anywhere upstream of
the emitter; it is what the emitted program turned out to CONTAIN, decided
alternation by alternation while `src/gen/emit_vm.c` was standing on the node.

### [old §6.3, lines 4372-4379]

**[FORM-CHAR] STEP 1, 2026-09-05: `<PREFIX>_VM_CLS_FOLDS`, and it is (b) for
`_VM_ALT_ISLANDS`' reason.** There is no fold MODE anywhere upstream of the
emitter; it is what the emitted program turned out to CONTAIN, decided pool
class by pool class by the fold rows of `src/gen/clskit.c`'s class-form
table (`byte-fold`, `byte-fold-default`; `vm_cls_shape` before `abi` 51)
while `src/gen/emit_vm.c` had the set in hand. It counts a VM program's
folds only; a DFA scan edge's fold (`abi` 53, `--tune=-2`/`-1`) is reported
by `<PREFIX>_DFA_SCAN_EDGE "fold"`.

### [old §6.3, lines 4411-4412]

**[OPT-LITSCAN] S2a, 2026-09-27 (`abi` 41): `<PREFIX>_VM_LIT_RUNS`, (b)
for `_VM_CLS_FOLDS`' reason.**

### [old §6.3, lines 4418-4430]

**The IFF: it is the number of literal-run compares this artifact's VM
program writes** — a run of three or more one-byte literals in a
concatenation ([OPT-LITSCAN] F5, `abi` 43, D127, narrowed from two: a
two-byte run reads cheaper as its own two-node byte chain, `tuning.md`
§2.31), and an alternation island's single-child trie chain (unaffected by
F5's floor, its own mechanism), each compared as one bounds check and one
run compare (`docs/spec/tuning.md` §2.31, §2.38: since `abi` 58 a
constant-length `memcmp` or, at the lengths gcc decomposes, two overlapping
word compares). UNCONDITIONAL on
every VM artifact, hybrids included, never defined on a pure-DFA artifact,
`0` under `-fno-lit-run`. A COUNT for the two entries above' reason. What a
consumer may NOT conclude: anything about the answers, which are identical
either way.

### [old §6.3, lines 4432-4433]

**[CLS-TREE] S4, 2026-09-29 (`abi` 48): `<PREFIX>_VM_CLS_KIT`, (b) for
`_VM_CLS_FOLDS`' reason.**

### [old §6.3, lines 4439-4452]

**The IFF: it is the number of distinct class-matcher functions
(`<prefix>_wcls<N>` and, since `abi` 51, `<prefix>_class_kit<N>`) this
artifact's VM program calls.** A `wcls` matcher is a wide class tested as one
decode and one matcher; a `class_kit` matcher is a byte class tested by the
kit's `K` form at `--tune=-2`/`-1`, where the kit is smaller than the class's
table (`docs/spec/tuning.md` §2.33). A DFA scan edge's kit matcher
(`<prefix>_<machine>_scankit<N>`) is not counted here; it is reported by
`<PREFIX>_DFA_SCAN_EDGE "kit"`. It is
emitted on every VM artifact, hybrids included, and never on a pure-DFA
artifact. It reads `0` under `-fno-cls-kit`, and under `-e byte` at
`0`/`+1`/`+2`. It is a COUNT, for the entries above' reason. A consumer may
NOT conclude anything about the answers, which are identical either way.
Nor may it conclude which form a matcher took: that is `--emit-ir`'s
`consume` row, and the matcher's own text.

### [old §6.3, lines 4454-4455]

**[OPT-CLSPACK], 2026-09-30 (`abi` 48): `<PREFIX>_VM_CLS_ATOMS`, (b) for
`_VM_CLS_FOLDS`' reason.**

### [old §6.3, lines 4470-4473]

**[OPT-1], 2026-08-25: two more (b) macros —
`<PREFIX>_FAST_FRAMES` and `<PREFIX>_FAST_TRAIL`.** They report the
capacities the un-suffixed entries' FAST TIER runs on (§3, §10.9), and they
are on **every VM artifact**, single-tier ones included:

### [old §6.3, lines 4498-4513]

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

### [old §6.3, lines 4515-4525]

**[OPT-4] (2026-08-29) `<PREFIX>_ENGINE_SEL` — the same decision as a TOKEN,
and it is a different macro from `_ENGINE_WHY` on purpose.** `_ENGINE_WHY` is
PROSE, written for a person and allowed to name an offset, a construct or a
build outcome. A CONSUMER cannot bucket on it: telling "auto picked the VM"
from "auto FELL BACK to the VM" means substring-matching English, which is what
the comparative benchmark project was reduced to. `_ENGINE_SEL` is the same
decision with a CLOSED value set, and — like `_ENGINE` and unlike `_ENGINE_WHY`
— it is **UNCONDITIONAL on every artifact, both engines** (D81: a fact stamped
only when it is interesting is a hint, and `"selected"` is a fact). Both are
written from one derivation at `src/opt/select_engine.c`'s single fit site;
neither is parsed to produce the other.

### [old §6.3, lines 4527-4536]

| value | meaning |
|---|---|
| `"selected"` | `auto` chose on the AST and nothing overflowed. The common case, on both engines |
| `"forced"` | the caller named `--engine=vm` or `--engine=dfa`, so `auto` selected nothing |
| `"declined-nullable-default"` | [OPT-4.2] (2026-08-31) `auto`, NOTHING overflowed, and the ORDINARY hybrid's own EXACT prefilter language is NULLABLE — it matches the empty string, so the forward+reverse DFA pair would admit a zero-length match at every position and could never dismiss one. Since `abi` 68 ([NULLABLE-ANCH]) "nullable" is the `empty_admits` fact: a pattern whose every empty match crosses a non-multiline start AND end anchor (`^(\s+)*$`) is not declined and reads `"selected"`. Since `abi` 69 ([DEC-VAR-ATTRIB]) a `${...}` pattern is never declined here either: its variable turns the prefilter off before any nullability is asked, and it reads `"selected"` (it read this value when nullable, a decline that decided nothing). `-fprefilter` overrides the decline, and an explicit `--engine=vm` reads `"forced"` (F-B2). No rung is involved and no prefilter survives. The general form of `"declined-nullable"` below, off the rung it is scoped to (`tuning.md` §2.17) |
| `"overflowed-dfa"` | `auto`, the DFA was to be the ENGINE, its build overflowed a cap, and no prefilter survived the fallback ([SEL-1]) |
| `"overflowed-prefilter"` | `auto`, the VM was already chosen for another reason, and only its auto-selected PREFILTER's DFA overflowed, so the prefilter was dropped |
| `"collapsed-prefilter"` | `auto`, a DFA build overflowed a STATE cap, and the [SEL-1] retry KEPT a prefilter by rebuilding it from the count-collapsed language (`tuning.md` §2.5, §2.17) |
| `"declined-nullable"` | `auto`, a [SEL-1] OR [OPT-4] retry OFFERED the count-collapsed prefilter and it was DECLINED because the collapsed language is NULLABLE — it matches the empty string, so the filter could never dismiss a position. No prefilter survives, and the artifact is the one this compile produced before that retry existed (`tuning.md` §2.17, [OPT-4.1]) |
| `"size-cap-retry"` | an emitted-SIZE cap (not a DFA state cap) REFUSED the exact artifact and a retry rebuilt a smaller one that SHIPPED. The rungs that reach it are the size-cap ladder's (`limits.md` §8), and the artifact's own axis stamps say which: on a **VM hybrid** it is [LIM-1]/[OPT-4]'s rung and the count-collapsed prefilter survived (`tuning.md` §2.17, legible as `<PREFIX>_DFA_PREFILTER` with `<PREFIX>_PREFILTER_LANG_WHY "count-collapsed"`), or — [PF-DROP], D135 — the ladder's last rung and the prefilter was DROPPED (legible as `<PREFIX>_VM_PREFILTER "none"` with `<PREFIX>_VM_PREFILTER_WHY "size cap retry, hybrid N > CAP"`, the refused artifact's bytes and the cap it exceeded — the only `"none"` that stamp is written beside); on a **DFA artifact** it is [K53-SELRETRY]'s optional-contributor drop and the anchored match-here machine was dropped (`tuning.md` §2.15, legible as `<PREFIX>_DFA_MATCH "search-filter"`), or [K59-PREMUL]'s premultiplied-table drop (`<PREFIX>_DFA_TABLE` off `"premultiplied"`). Distinct from `"collapsed-prefilter"`, which is the [SEL-1] DFA-state-cap rung's own success — the rungs are offered under different conditions in `compile_driver`'s retry loop |

### [old §6.3, lines 4556-4566]

**`"declined-nullable-default"` AND `"declined-nullable"` ARE THE SAME
POLICY ON TWO DIFFERENT POPULATIONS, KEPT AS TWO VALUES ([OPT-4.2],
2026-08-31) rather than folded into one.** Both say "this pattern's own
language admits a zero-length match at every position, so no prefilter for
it can ever dismiss one" — but `"declined-nullable"` says a ladder RUNG
offered a rescue and it was refused, while `"declined-nullable-default"` says
there was never a rung: the ORDINARY hybrid's own exact prefilter was the
thing declined. A consumer that folded the two together could not tell
"this compile hit a cap and recovered smaller-but-useless" from "this
compile never hit anything at all", which is exactly the distinction the
five fallback values above exist to keep visible.

### [old §6.3, lines 4568-4581]

**`"size-cap-retry"` CLOSES A GAP THIS DOCUMENT ITSELF USED TO NAME WITHOUT
FIXING** ([LIM-1], D90, 2026-08-30). Before this value existed, a [OPT-4] size
rung whose retry SUCCEEDED (the collapsed prefilter survived) stamped
`"selected"` — indistinguishable from a compile that never touched any cap at
all, because `dfa_disabled` (the flag that routes to the DFA-overflow arms
above) is never set on this rung: the DFA build itself succeeded, it was the
WHOLE ARTIFACT that an emitted-size cap refused. `docs/spec/limits.md` §3.3's
own [OPT-4] section had recorded "the SIZE rung's own decline is not this
value... the route stays `selected`" as a statement about the DECLINE only,
and it was being silently read as true of the rung's SUCCESS too — the exact
closed-value-set-losing-a-member shape K35 exists to name. A rescue that was
refused (nullable) now reads `"declined-nullable"`; one that shipped now reads
`"size-cap-retry"`; only a genuinely unremarkable compile still reads
`"selected"`.

### [old §6.3, lines 4583-4597]

**[K53-SELRETRY] (2026-09-10) A SECOND RUNG JOINED THAT VALUE RATHER THAN
MINTING A THIRD.** The size-cap retry ladder gained a rung for DFA artifacts:
an artifact carrying the OPTIONAL anchored match-here machine
(`<PREFIX>_DFA_MATCH "unwrapped"`) that a size cap refuses is re-emitted
without it (`docs/spec/limits.md` §8, "The optional-contributor drop"). It
reads `"size-cap-retry"` because that is what the value means — an emitted-size
cap forced a retry and the retry shipped — and the gap the paragraph above
describes is the SAME gap: without it, `\p{L}` under `-e utf8` would stamp
`"selected"` and nothing would say the artifact is slower than an
unconstrained build's. **Which contributor a retry dropped is read off the
artifact's own axis stamps, not off a second value here**, and the two rungs
cannot both fire on one compile (the first requires a VM hybrid, the second a
DFA artifact), so the pair is exact. Minting a second value would have put
"a size cap forced a retry" in two homes, which is the drift this section's
own history is about.

### [old §6.3, lines 4623-4640]

**[SEL-1] (2026-08-28) `RX_ENGINE_WHY` CAN ALSO NAME A BUILD OUTCOME, NOT
ONLY A CONSTRUCT.** Under `--engine=auto`, a DFA build that overflows a cap
(state count, table entries, the K7 element budget — `docs/spec/tuning.md`
§2.11) is a selection outcome rather than a refusal, and the artifact that
falls back to the VM stamps that outcome the same way every other forcing
reason is stamped, and since [OPT-4] (2026-08-29) it can appear beside a
`RX_VM_PREFILTER "hybrid"` rather than only beside `"none"` — the fallback's
first rung rebuilds the prefilter from the count-collapsed language instead of
dropping it, and `RX_VM_PREFILTER_LANG_WHY "dfa overflow retry, exact nfa N"`
is what says so (`tuning.md` §2.5, §2.17). `RX_ENGINE_WHY "dfa overflowed: >32000 states at pattern
offset 0"`. The offset is not tied to any one AST node (this reason is a
property of the whole compile, not of a construct at a position) and reads
0 by convention, the same position the underlying `pcrec_ctx_fail` reports at. If
the pattern's engine choice is ALSO forced by a real construct (a capture
request, a `VM_ONLY` registry row), that reason wins the stamp on the
ordinary first-wins rule above — the overflow's own effect on the PREFILTER
(dropped, `RX_VM_PREFILTER "none"`) still applies independently in that
case, through a fact `RX_ENGINE_WHY` does not carry.

### [old §6.3, lines 4642-4650]

**A consumer MAY now `#if` on `RX_ENGINE`.** This paragraph used to close
with the opposite warning — "a consumer that `#if`s on `RX_ENGINE` is
writing code that does not compile against half the artifacts pcrec
produces" — and [DD-13] answered it rather than restating it: the failure
that warning describes is caused by a CONDITIONAL stamp, and the only fix
for it is an UNCONDITIONAL one. The warning still holds, verbatim, for
every (b) macro: `#if`ing on `RX_VM_RUNGS` or a budget macro is writing
code that does not compile against a DFA artifact. (Measured by listing
every `#define` in a fresh build of each kind.)

### [old §6.3, lines 4652-4672]

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

### [old §6.3, lines 4738-4746]

**`"empty"` is [DD-13c], 2026-08-25, and it is a THIRD SHAPE rather than a
special case of the other two.** A pattern the start analysis proves can
match nothing — `\B\b`, `\b\B`, `\d\b\w`, `a\bb`, and their `^`-anchored
spellings — compiles to a search body that is one `return 0`: no table, no
loop, no skip, on EITHER engine. Those artifacts used to stamp the name of
the loop the emitter WOULD have written (`"unanchored"`, or `"attempt"` when
anchored), which is a statement about which emitter ran and not about what it
wrote. `RX_DFA_PREFILTER` reads `"none"` on all of them, for the reason the
value set below gives: there is no scan for a filter to be part of.

### [old §6.3, lines 4798-4801]

| value | mechanism |
|---|---|
| `"unwrapped"` | the artifact carries a THIRD machine — the forward tables WITHOUT the start-anywhere self-loop — and runs it from `ctx->pos`: no later start to reject, no backwards pass, and a failing probe stops at the first byte that cannot continue a match beginning here |
| `"search-filter"` | the entry runs `<prefix>_search` and rejects any match whose start is not `ctx->pos`. FIVE populations: `_DFA_SCAN "attempt"`, `_DFA_SCAN "empty"`, an anchored machine that exceeded a DFA cap (a SELECTION OUTCOME, never a refusal), any build under `-fno-anchored-dfa`, and — [K53-SELRETRY], 2026-09-10 — an artifact whose anchored machine was DROPPED to fit under an emitted-size cap, which is the one population of the five that `<PREFIX>_ENGINE_SEL` distinguishes (it reads `"size-cap-retry"`; the other four read whatever their engine selection was, ordinarily `"selected"`) |

### [old §6.3, lines 4820-4827]

| value | mechanism |
|---|---|
| `"none"` | the artifact carries no scan edge. Four causes and none of them a failure: no machine has a collapsible run; `_DFA_SCAN "attempt"`, whose states are code labels and whose step is a computed `goto`, so there is no loop-carried table load to shorten; `_DFA_SCAN "empty"`, whose body is one `return 0`; and any build under `-fno-scan-edge` |
| `"range"` | every edge in the artifact tests a CONTIGUOUS byte range (the class table's `byte-range` row), emitted inline against immediates — `b == c`, `b <= hi` from 0, otherwise `(unsigned)(b - lo) <= span u`, the VM's own spelling since `abi` 53 — so the loop touches no memory but the subject |
| `"fold"` | (`abi` 53) at `--tune=-2`/`-1` only: every edge's class is an ASCII case pair on the `byte-fold` row, tested inline as `(b \| 0x20) == x`. At `0`/`+1`/`+2` a scan edge's fold pair is a `"bitmap"` (D138 Q1: the default fold is held for both sites until its measurement rules). Never under `-fno-cls-fold` |
| `"bitmap"` | at least one edge's class is on the `byte-table` row, and the table selection's `scan-table` row gives it a 256-byte membership table read. The loop-carried register is still the cursor, which is the property the transform is for; the memory reference is the price |
| `"kit"` | ([CLS-TREE] S2, `abi` 52) at `--tune=-2`/`-1` only: every edge's class is on the class-form table's `byte-kit` row — its kit matcher, written at the edge's two test sites, is smaller than its 256-byte table (`abi` 53, D139 item 1) — so its test calls a `static inline` kit matcher `<prefix>_<machine>_scankit<N>` in place of the table (`docs/spec/tuning.md` §2.33). Never at `0`/`+1`/`+2`, and never under `-fno-cls-kit` |
| `"mixed"` | an ARTIFACT-LEVEL composition, `RX_DFA_TABLE`'s own shape: this artifact's machines took more than one form. The choice is per EDGE, and a machine may carry up to four |

### [old §6.3, lines 4880-4914]

These are scalar macros for a per-artifact-wide verdict
(`RX_ENGINE`, `RX_VM_PREFILTER`, `RX_DFA_SCAN`, `RX_DFA_PREFILTER`,
`RX_VM_PRUNE_CEILING`) or a bitmask
when the axis is decided per-quantifier and a single scalar would
misreport a mixed pattern (`RX_VM_RUNGS`, `RX_VM_STRATS`,
`RX_VM_PRUNES`). **`RX_VM_POSS_ARMS`** ([ART-POSS-ARMS], abi 66) is the
per-ARM half of `RX_VM_STRATS`' POSSESSIVE bit: bit `0x1` (A0, a
lookahead-born gate in the follow valued with nothing known on its left),
`0x2` (A1, a gate valued by the loop's own LAST characters' polarity) and
`0x4` (B, a backreference's first character read from its groups) are set
when that arm was NEEDED for some positive possessify verdict — for A1,
the verdict was decided by A1 alone; for A0 and B, the same compile with
that arm denied counts fewer positive verdicts. `0x0u` where no arm was
needed, which includes every artifact built with both arms denied: a denied
arm's bit is 0 by construction (`tuning.md` §2.44/§2.45). Emitted on every
VM artifact, never on a DFA-only one. The bit values are this paragraph's;
they are not named constants in the `PCREC_RX_ABI_H` block. Of the VM block above, everything but `RX_ENGINE` is
VM-artifacts-only; the DFA block's `RX_DFA_SCAN`/`RX_DFA_PREFILTER`/
`RX_DFA_PREFILTER_OFFSETS`/`RX_DFA_TABLE`/`RX_DFA_SCAN_EDGE`/`RX_DFA_START` are
the DFA SCAN's own selection facts ([DD-13]'s (a)/(b) split, above) and
since [DD-13c] appear on every artifact that CONTAINS such a scan — DFA
artifacts AND VM hybrids, the iff stated in (a). `RX_DFA_TABLE` is
[OPT-3]'s, `RX_DFA_SCAN_EDGE` [OPT-5] STEP 1's and `RX_DFA_START` [OPT-5]
STEP 2's; all three join that iff unchanged.
`RX_DFA_MATCH` is [ENG-ABS]'s and
does NOT: it is a fact about an ENTRY rather than about a scan, so its
iff is `RX_ENGINE "dfa"` — see its own paragraph above. **[ABI-NS],
2026-08-18 (D60): the NAMED bit constants each mask is built from
(`PCREC_VM_RUNG_CURSOR`/etc., `PCREC_VM_STRAT_POSSESSIVE`/`_BACKTRACKING`,
`PCREC_VM_PRUNE_CLAMPED`/`_UNCLAMPED`) are not emitted here any more —
they moved to the shared, unprefixed `PCREC_RX_ABI_H` block (§2),
emitted once and unconditionally on every artifact including a DFA-only
one. Only the three OR'd MASKS above stay per-prefix and VM-only, since
their VALUE is the one genuinely per-artifact fact.** Two more D46
stamps are NOT VM-only, and a DFA-only artifact carries them too:

### [old §8.0, lines 5037-5046]

**Link with `-Wl,-dead_strip` (ld64) or `-Wl,--gc-sections` (GNU ld).**
`libpcrec.a` is a static archive with `.rxt`-source-file support (the
`--source` composer) statically reachable from the ordinary compile path;
a consumer that never calls `pcrec_compile_defs`/`pcrec_rxt_source_parse`
pulls those object files in anyway unless the linker is told to drop
unreachable sections. MEASURED (2026-09-17 code review, L6 §1.3): this one
flag, with no source change anywhere, recovers 43,968 of the 44,448 bytes
those objects add to a minimal consumer's `__text` — leaving 480 bytes and
two symbols the composer's own early-return path still reaches. Omitting
it is not wrong, only larger than it needs to be:

### [old §8.0, lines 5086-5099]

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

### [old §8.1, lines 5125-5138]

- **It never `abort()`s the caller on the compile path.** Every
  allocation site routes failure through the internal `pcrec_ctx_nomem()` and
  comes back as a normal `-1`-with-diagnostic return, so a caller that
  sets a memory limit precisely in order to survive a hostile pattern
  does survive it. One `abort()` remains in the code deliberately, and
  it is not on the compile path: the syntax-dump path's detached string
  buffers, which run outside a compile and have no `pcrec_error` to report
  through. The DFA structural invariants that used to be the OTHER
  exception now refuse through `pcrec_ctx_fail` like every other
  "cannot happen" site in the compiler (K61, `docs/dev/known_issues.md`).
  **2026-09-18: this promise had TWO real exceptions before today, and
  both are now closed — it has none.** They were independent mechanisms
  with nothing in common but their symptom, which is why each needed its
  own fix.

### [old §8.1, lines 5151-5182]

  *The state legend (K60, D105).* A second, narrower mechanism: the
  emitted DFA state legend's scratch buffers were raw, unrouted
  allocations that never called `pcrec_ctx_nomem` at all, so on failure they
  dropped the legend and let the compile SUCCEED. A caller under memory
  pressure could receive `0` and an artifact whose comment bytes
  differed from the same pattern's compiled anywhere else, with nothing
  in the artifact saying so. Because that path never reached the
  recovery point, D109's fix could not reach it either — it was closed
  separately, and by DELETION rather than by diagnosis: the unbounded
  buffer became a fixed local and the rest moved to the compile's
  arena, so a failure there is now an ordinary refusal (measured:
  `make alloc`'s W1 and W3 witnesses, 15 and 25 absorbed before the
  fix, 0 after). **A compile that would previously have emitted a
  legend-less artifact under OOM now returns `-1` with a diagnostic.**
  The emitted bytes of a compile that does not run out of memory are
  unchanged, which is why D105 is not an `abi` event.
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

### [old §8.2, lines 5251-5259]

**`features` is [REL-1.11]'s library promotion of the CLI's `--features`
lever** (2026-09-21, docs/dev/decisions.md D20's own "promote a library
channel later"), applied PER `pcrec_compile()` CALL: a comma-separated
module-name list exactly as `pcrec --list-syntax`'s `module` column spells
them, the frozen named set `"std1"` (D37), `"all"`, or `"none"`. An unknown
name is refused by name — the same `--flavour` rule the CLI's own
`--features` follows — surfaced through `pcrec_error` exactly like any
other compile-time refusal, with the identical wording the CLI's own
`--features: <text>` stderr line quotes (minus that prefix).

### [old §8.2, lines 5299-5305]

**`PCREC_ENC_BYTE` was spelled `PCREC_ENC_ASCII` before [M5-SEAM]**, and
`-e ascii` was the CLI value. It is a RENAME, not an alias — `-e ascii` is
now an unknown encoding — taken under §9's pre-v1 posture as one announced
boundary. The reason is that the old name asserted something false about
the semantics: this encoding treats every byte as a character, `0x80`-and-up
included, with no case and no meaning attached, which is precisely what
"ASCII" does not say. D58's own ruling text names the encoding `byte`.

### [old §9, lines 5371-5371]

## 9. Provenance and status

### [old §9, lines 5373-5380]

This document graduates `docs/design/match_api_m4.md` (the M4 match-API
freeze design record) and `docs/design/engine_m4.md` into a spec per
`docs/dev/decisions.md` D40's addendum: design records what pcrec wants
to build and the process that got there; this spec records what shipped
and is pcrec's contract with an embedder, going forward. Consult those
documents for *why* a rule is what it is (ruling citations, panel
findings, refuted alternatives); consult this document for *what the
rule is*.

### [old §9, lines 5382-5388]

**Pre-v1 posture (D40):** this contract carries no backwards-compatibility
weight yet. Breaking changes are unconstrained in substance and governed
only in form — one announced-boundary commit per break, populations
conserved and accounted, never silent drift. At a future v1 declaration,
this document (or its direct successor) becomes the compatibility-bound
enumeration; until then, "frozen" here means "the M4 working baseline",
not "permanent".

### [old §10, lines 5392-5392]

## 10. The caller-provided frame buffer — **[DD-14.FB]**

### [old §10, lines 5394-5413]

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

### [old §10.1, lines 5415-5415]

### 10.1 What the ruling is for

### [old §10.4, lines 5553-5557]

(the two capacity macros existed before this revision but lived in the
generated `.c`; they moved into the `.h`, where a caller can read them), and
four of the same facts as fields on `rx_info`, for a consumer with no C header —
an FFI or `dlopen` binding, which is exactly the consumer most likely to
want a large reservation:

### [old §10.6, lines 5652-5657]

**RE-MEASURED on the shipped emitter (2026-08-25) and the table holds** —
1,677,721 frames and 4,194,304 trail entries derived from the same two
reservations, 1.8 MB resident before the first match, the 800 KB row
matching in 0.057 s having touched 90 MB, and the ceiling still between
n = 466,000 and n = 470,000. `tests/recursion/run_frame_buffer.sh` is that
re-measurement, and it asserts each of those rather than printing them.

### [old §10.6, lines 5659-5674]

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

### [old §10.8, lines 5697-5698]

Stated explicitly because it is the compatibility promise, and because the
implementation lane owes a check that asserts each line:

### [old §10.9, lines 5718-5718]

### 10.9 The tiered default entry, and what a FRAMES escalation restarts — **[OPT-1]**

### [old §10.9, lines 5786-5789]

**[ART-SIZE] the size term's four macros**, on the `<PREFIX>_DFA_SCAN`
precedent (a selection fact stamped whether or not it fired, D81) and
VM-artifact-scoped for the first two, because a DFA artifact has no counter
rung to have chosen a `K` for:


---

## docs/spec/CLAUDE.md's `match_api.md` entry, as it stood at aee1a570

The directory index's entry carried the document's revision notes too; it was
replaced by a description of the rewritten document, and its text is kept
here verbatim.

- `match_api.md` — **[M4.7f], 2026-08-18: the FIRST spec document.** The
  as-built match-API contract: the generated artifact's entry points
  (`<prefix>_search`/`_match`/`_match_caps`/`_info`), the six fixed-literal
  ABI types (`rx_ctx`, `rx_matchfn`, `rx_callout_ref`, `rx_group_entry`,
  `struct rx_info`, `rx_renderfn`), capture-slot semantics (the C1–C11
  requirements restated as contract prose, with the R22 cross-iteration-
  retention/empty-final-iteration-overwrite rules folded in as first-class
  text, not an addendum), the D49 give-up code space
  (`RX_ERR_STEPS`/`_FRAMES`/`_WORK`/`_RECURSE` since [DD-14] wave A, the
  `RX_ERR_FLOOR` partition) and the below-the-floor `RX_ERR_INTERNAL`
  (NOT a give-up, [DD-14] wave A commit 2), the
  `rx_info` reflection structure and its D46 compile-time observability
  macro mirror, the compile-entry NUL-termination contract (with an
  independently measured libpcre2 10.46 comparison — `PCRE2_ZERO_TERMINATED`
  truncates identically), and `pcrec_options`/`pcrec_error`. Every claim
  is verified against the shipped surface (`lib/pcrec.h`, artifacts
  actually emitted by `build/pcrec`, cited tests) rather than copied from
  `docs/design/match_api_m4.md`, which had drifted from what shipped in
  one place (§3.5: the give-up-code collapse `match_api_m4.md` still
  describes was superseded by D49 before this graduation and the shipped
  artifact already implements the superseding rule) and carries one
  as-built deviation of its own (§2: `rx_info` ships as a struct TAG, not
  the bare typedef the design sketch showed — forced by a name collision
  with the default-prefix `<prefix>_info` instance; **RULED D57,
  2026-08-18: the struct-tag spelling is blessed as the contract and the
  typedef form is dead**, so §2 states it as settled rather than open).
  References `docs/design/match_api_m4.md`/`engine_m4.md` informationally
  for the ruling history; this document alone states what pcrec promises.

  **[M6.2] waves D and E each added a sentence to §3.1, and wave E's is the
  larger one.** Wave D's says what `\G` means under the find-all loop
  ("contiguous with the previous match", PCRE2's global-iteration semantics,
  for free because the entry already takes the parameter PCRE2 threads). Wave
  E's says that **`caps[0][0]` is where REPORTING begins, which is not always
  where matching began** — `\K` moves it — with three consequences a caller
  can see: `caps[0][0]` can exceed the offset the match began at and is
  therefore not a bound on where the engine looked; `caps[0][0] ==
  caps[0][1]` no longer implies nothing was consumed (`ab\K` reports `[2,2)`
  after two bytes); and the anchored entries of §3.2/§3.3 return the CONSUMED
  length, which is what makes the §5 callout advance terminate. The find-all
  loop is unaffected because it advances off `caps[0][1]`, and that is
  MEASURED against libpcre2 driven through the same loop
  (`tests/assertions/run_kreset_diff.sh` §5) rather than argued.

  **[K75] (D132, 2026-09-30) — §3.1's find-all loop resumes after a
  non-empty match at `<prefix>_next_pos(s, n, end - 1)`, not `end`.** A
  protocol change only (no emitted byte, no abi event): a no-op on a
  well-formed subject, and under `-e utf8` it steps over a stray continuation
  byte instead of handing the engine a `startpos` K50 refuses. §3.1 also now
  states the boundary rule outright (a caller's `startpos` must be a
  boundary; positions the loop computes always are; a continuation byte is
  never a match start); `rxt_format.md`'s `mc` paragraph carries the same
  advance.

  **[M4.7g], 2026-08-18 — the R29 fix pass** (`docs/dev/reviews/
  2026-08-18-r29-match-api-spec.md`) is the document's first revision,
  and its shape is worth knowing before editing this file again: the
  MATCHING SEMANTICS survived the panel untouched, and every landed fix
  was in the surrounding surface — the library calling sequence (§8 now
  carries one worked example that was compiled and run before it went in,
  plus §8.1's D56 guarantees), the find-all protocol (§3.1, verified
  against `re.finditer` and honest about where it is lossy against
  PCRE2's NOTEMPTY retry, which pcrec cannot express), the reflection
  surface's over-claims (§6.3's macro mirror is partial, and thinner
  still on DFA artifacts), and the two shipped doc-comments an embedder
  actually reads, which BOTH denied the give-up-code space §4 promises
  (fixed in `src/gen/emit_dfa.c` and `lib/pcrec.h` in the same pass).
  The document's header now carries a VERIFICATION LEDGER recording what
  each pass re-measured; keep it current, and keep §3.5's record of the
  two errors the panel found — an idealized quotation in a document whose
  authority is "checked against the shipped surface" is the failure mode
  the document exists to prevent, and old artifacts still carry the
  comment it describes.

  **[M5-SEAM], 2026-08-18 — the second revision** (D58, the encoding seam
  prelude). Smaller in shape than R29's and worth knowing for one reason:
  it is the first revision where a recorded CAVEAT was DISCHARGED rather
  than a claim corrected. §3.1's find-all loop advanced by a literal `+ 1`
  and carried a byte-vs-character caveat saying M5 would have to sharpen
  it; the loop now advances through `<prefix>_next_pos`, the first encoding
  residual, and the new §3.1.1 states that entry's contract. The caveat's
  own text is QUOTED in §3.1.1 rather than deleted, with what discharged it
  said next to it — the same discipline §3.5 follows for the two errors R29
  found. Also in this pass: §1 and §3 count five per-artifact entry points
  instead of four; §8.2 gains the per-compile-call encoding rule and
  records the `PCREC_ENC_ASCII` -> `PCREC_ENC_BYTE` rename as an announced
  pre-v1 boundary; §8.1's D56 quotation was re-measured (its wording had
  gone stale — it promised a milestone that had already shipped). The
  find-all measurement behind §3.1 is now a SUITE (`tests/encseam/`, in
  `make test`) rather than a transcript, which is the direction to keep
  taking this document's numbers.

  **[M6.3], 2026-08-18 — the third revision** (module `named-groups`).
  The second DISCHARGE this document has recorded (the [M5-SEAM] shape,
  not a correction): §6's own open question — the `groups` array's sort
  key — is fixed (`strcmp` on the name, matching libpcre2's own
  `PCRE2_INFO_NAMETABLE` order, measured; docs/dev/decisions.md D59
  carries the evidence and the reasoning) and §6's worked example is
  re-quoted verbatim from a fresh build carrying the module, in both the
  captures-default and `--no-captures` forms.

  **[ABI-NS], 2026-08-18 — the fourth revision** (D60 + addendum, the
  emitted universal-constant namespace unification). The give-up code
  space (§4), the caps-array unset sentinel (§5), and the nine D46 stamp
  bit constants (§6.3) move from per-`<PREFIX>` spellings to one
  canonical, unprefixed `PCREC_*` spelling in the shared `PCREC_RX_ABI_H`
  block (§2); the old `<PREFIX>_*` spellings are DELETED, no alias.
  `rx_info.engine`'s formerly number-only contract (§6 used to say "no
  such constant is #defined anywhere") gains names, `PCREC_ENGINE_DFA`/
  `PCREC_ENGINE_VM`, in the same block. §1, §2, §4, §5, §6 and §6.3 are
  re-quoted this pass, verbatim from fresh builds (both a `--no-captures`
  DFA artifact and a captures-default VM one). A THIRD-PARTY collision
  was found and fixed in the same lane, outside this document's own
  scope but load-bearing for it: `lib/pcrec.h` already declared
  `PCREC_ENGINE_DFA`/`PCREC_ENGINE_VM` as `enum` members for
  `pcrec_options.engine` (the compile-time engine REQUEST), and an
  artifact's own `#define` of the identical name, included before that
  header, rewrote the enum declaration into invalid syntax — fixed by
  converting `lib/pcrec.h`'s two members to plain `#define`s
  byte-identical to the artifact's emission (`lib/CLAUDE.md` carries the
  detail).

  **[DD-14.FB], 2026-08-24 — the fifth revision, and the first that states
  a contract BEFORE it exists** (D71 item 2, the caller-provided frame
  buffer). Every earlier revision recorded what shipped; this one adds
  **§10, marked "SPECIFIED, NOT YET BUILT" in its own first line**, because
  D71 item 2 rules the buffer's shape "decided at docs/spec/match_api.md
  under D40" and the three existing entries' compatibility story is a fact
  about this document's contract. **The marking is the point, and an
  editor of this file must keep it**: this document's authority is that
  every claim was checked against the shipped surface, so a forward-looking
  section is only safe while it says loudly that it is one — §1-§9 are what
  pcrec promises today, §3/§4/§5.3/§6 carry one-line forward pointers that
  each name the pending status, and nothing in §1-§9 changed in substance.
  When the implementation lands, §10's status block comes off and its
  content merges into §3/§5/§6 where it belongs; that merge is the
  revision, not a re-write. Specified: three `_in` entries taking a
  per-artifact `<prefix>_buffers` descriptor (deliberately NOT one of §1's
  fixed-literal `rx_*` types — a frame's SIZE differs per artifact, so a
  literal spelling would advertise an interchangeability that does not
  exist), `buf == NULL` DEFINED as a call to the un-suffixed entry,
  `PCREC_ERR_FRAMES` unchanged and retry defined, a sizing surface with
  `abi` 2 → 3, and §5.3 extended by exactly one conjunct (own buffers per
  concurrent call). The design record — alternatives, costs, and the
  ASK — is `docs/design/frame_buffer_design.md`.
  **One shipped-behaviour note rides this revision and is NOT
  forward-looking**: §5.3 gains a MEASURED paragraph saying the concurrency
  promise is collectable only on a large-enough thread stack.
  `<prefix>_search`'s stack frame is 131,296 bytes on a call-bearing
  artifact whose frame requirement is not statically bounded, which does
  not fit a musl-default 128 KB thread and faults on a 2-byte subject. That
  is a live gap between §5.3's contract and the shipped artifact, filed as
  the design note's FINDING-1.

  **[SPEC-1.4], 2026-08-26 — the docs/spec/ consolidation pass's own patch
  set (D80), five small additions, no shipped behaviour changed.** §4 now
  points at `docs/spec/limits.md` for the give-up codes' numeric trigger
  defaults rather than leaving them unfound; §6.3's DFA-stamp-gap caveat
  (survey row C2) was re-verified against a fresh DFA/hybrid build and
  found already discharged by `[DD-13c]` — no wording changed there; §6
  gained a caller-facing `abi` paragraph stating D76's rule in contract
  terms (what a bump means, what stays fixed within one number, and that
  pre-v1 the bump IS the whole of the announcement, D40 regime 1); §8.2
  now leads with "`byte` is the only encoding implemented today" rather
  than requiring a reader to find it three paragraphs down; and a new §3.6
  states the `(?:P)\z` whole-subject/end-anchored idiom (survey row F9) —
  why `\z` and not `$` (verified live: `(?:foo)$` matches `"foo\n"`,
  `(?:foo)\z` does not), the `a|ab` counter-example showing a naive
  `length == n` test is insufficient (verified live: `a|ab` on `"ab"`
  reports `[0,1)`, `(?:a|ab)\z` on the same subject reports `[0,2)`), its
  ruled-permanent status (`docs/dev/decisions.md` D77, plan row `[OS-4]`),
  and the idiom's own DFA stamps (verified live: `RX_DFA_SCAN
  "unanchored"`, `RX_DFA_PREFILTER "byte-class-bounded"`/
  `"memchr-bounded"`).


  **[DD-13b.W1.2], 2026-08-31 — the sixth revision, `rx_info.name` and
  `rx_info.nentries`.** Two members APPENDED to §6's struct (no existing
  offset moves) and `abi` 13 -> 14. `name` is the artifact's own name —
  never NULL, stamping the `<prefix>` when a build supplies none — and it
  answers a different question from `prefix`: one definition built under
  three configs is three artifacts, three prefixes and ONE name.
  `nentries` is the length of the whole `groups[]` array where `nnames`
  counts the primary pattern's own rows, which stay a genuine PREFIX of
  it; **they are EQUAL on every artifact pcrec emits today** and the
  section says so in those words rather than implying a distinction that
  has no producer yet. The field ships now because it rides this bump
  rather than costing a second one.

  **2026-09-10 (Frank's ruling, lane rpkg, wording only, same pass as
  `limits.md` above):** §5.3's K33 paragraph restates the fit criterion as
  free stack HEADROOM AT THE CALL SITE rather than thread-stack SIZE —
  the musl-128KB and glibc-8MB numbers now read as worked examples of
  headroom at call depth ~0, not as the rule. No shipped-behaviour claim
  changed.

  **`[OPTLOOP.1]` batch 1, 2026-09-22 (D119) — `abi` 28 -> 29, THE THREE
  WHOLE-WINDOW PRE-CHECKS.** §6's `abi` change log gains its next entry:
  every artifact of both engines gains the `<PREFIX>_END_WINDOW` and
  `<PREFIX>_REQ_BYTE` stamps, every VM artifact gains `<PREFIX>_VM_START`,
  and the three analyses' own populations gain the emitted bound, clamp and
  `memchr` those stamps name. ONE bump for three mechanisms — one landing,
  one emitted-scaffolding event. No struct offset moves, no `rx_info` member
  is added or changed, no answer moves; §2.25-§2.27 of `tuning.md` carry the
  axes and `end_window.rxt` the one mechanism that has an answer-level net.

  **[REL-1.4], 2026-09-21 (D115) — `abi` 27 -> 28, THE VERSION STAMP.** §6's
  `abi` change log gains its next entry: the essential generated-by line
  now also names `PCREC_VERSION` (`lib/pcrec.h`) beside the abi digit —
  `/* Generated by pcrec 0.1.0-beta (abi 28). Pattern: ... */`, on every
  artifact of both engines regardless of `-fcomments`. No struct offset
  moves, no `rx_info` member is added or changed, and no answer moves; the
  comment TEXT is the only thing that changed. `PCREC_VERSION` itself is
  independent of `abi` (versions the tool, not the emitted scaffolding).

