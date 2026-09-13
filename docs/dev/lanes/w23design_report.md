# w23design report — [DD-13b.W23] STEP 1: format_design.md REVISION 3

Lane w23design (opus), 2026-09-12, branch `lane/w23design` from main
b9572c66. DESIGN ONLY: every commit touches `docs/design/dd13_format/`
and `docs/dev/lanes/` only — nothing under `src/`, `tests/` or
`docs/spec/`. The D6 panel reviews the delivery; implementation is NOT
cleared by it.

## What was delivered

`docs/design/dd13_format/format_design.md` is REVISION 3 (2,517 →
~3,500 lines): the [B42] capability-set needs note absorbed into the
design of record under Frank's F-Q1 (Tier 1 + Tier 2 as ONE W23
delivery) and F-Q2 (multi-line patterns MUST). The brief's six
deliverables and where each lives:

1. **The productions** — §1.2 (the body SUB-BLOCK mechanism), §1.3
   (grammar: `pattern-esc`, `provenance`, `vocabulary`, `configs`,
   `capable`, `under`, `tag-prose`, `@file: as/sha256`, `oracle`
   engine-ref, `variant` reshaped), §2.14-§2.24 (semantics, one section
   per production). §1.4 is the restructured wave table: W1 BUILT, ONE
   W23 delivery, an explicit remains-after list, and **no abi event
   anywhere in W23**. §4.5 item 4 is REPLACED (regime repair), §6.2 is
   REPAIRED (the worked bench file now survives D93 by construction).
   §0.6 is the revision record keyed to N-nn.
2. **P-Q dispositions** — §8, all nine.
3. **Spec-delta plan** — §3.4's SW1-SW15 table (D80), including SW12's
   three-reader name-grammar note (the derived-identifier binding
   touches NO reader's grammar — only the composer's lookup).
4. **Acceptance-checklist mapping** — §9, all 41 checks; G3 comes out
   M1/M5/M10 change, everything else's FACTS unchanged, with one named
   precision (appended header columns; see "refuted/precisioned").
5. **Frank queue** — §7.3 (W23-F1, W23-F2, W23-F3).
6. This report.

## The two leanings, worked to answers

**P-Q1 (the biggest shape decision): CONFIRMED as the general body
sub-block mechanism** (§1.2). Two genuine customers — `provenance`, and
`variant`, whose revision-2 body ALREADY carried a one-off un-indented
`groups` continuation line the general form retires (the house rule
applied to this note's own earlier special case). The narrow rules that
keep N-2's refusal loud: indentation-test-precedes-dispatch in all
three body readers (without it an indented `pattern` line would start a
block in one reader and continue a sub-block in another — the one
defect the mechanism could introduce, closed by ordering, and why
`variant` carries `text` rather than `pattern`); a bare indented line
stays a hard error with today's diagnostic; blank line terminates (the
head's r46sem-10 rule reused). The flat prov-* fallback was declined:
it answers provenance only and leaves `variant`'s hack standing.

**P-Q5 (the regime mechanism): option 3 CONFIRMED — and regime grouping
does NOT ride the sub-block mechanism** (§2.22). The derived-identifier
call binding lives at the composer's definition-set lookup
(`rxt_compose.c:169/:176`, consumed by the re-resolution at
`:690/:788` — verified in the shipped code), through
`pcrec_rxt_prefix_from_name` (`rxt_source.c:337` — the mapping's ONE
home), with the target-prefix collision refusal reproduced at the call
site: exact spelling does NOT win (it is the identity case of the same
map), the refusal names both definitions. The three name-grammar
readers (`rxt_source.c:298 defname_ok`, `run.sh:2015`,
`verify_rxt.py:331`) are untouched — the call's spelling stays PCRE2's,
the definition's stays wide, only leg A's single-implementation lookup
learns the map. §4.5 item 4 is then usable AS DESIGNED with its two
surviving caveats restated (capture-column trigger; composed blocks are
`oracle pcre2`). A `regime` sub-block was worked and declined: it is a
case scope by another name (Frank ruled none exists), it would put case
lines under indentation in the most load-bearing arms of all three
readers, and it buys nothing the shipped composer doesn't deliver.

## Pre-rulings: verified, one deviated from on evidence

**(a) mc counting rule — DEVIATED, with the measurement** (§0.6, §2.21;
this is the item to read first). The brief's rule
(`pos = max(end, pos+1)`) was run head-to-head against the shipped
find-all protocol (`match_api.md` §3.1) and `re.finditer`:

- The bench's literal formula **DOUBLE-COUNTS an empty match found
  beyond the scan position** — `(?=a)` on `"xax"`: it reports
  `(1,1) (1,1)` (its `max` returns the match's own position when the
  match lies ahead of `pos`, so the same empty match is found again);
  the §3.1 protocol and `finditer` both report one.
- BOTH non-retry rules are a strict subset of `finditer` on
  empty-preferring patterns (`a*?`/"aaa": 4 vs 7) — the NOTEMPTY class
  §3.1 already documents, which **pcrec's entry points cannot express**.

So the spec paragraph states the §3.1 protocol BY REFERENCE (non-empty
→ resume at end; empty → one character past the REPORTED start; no
retry): already shipped, already suite-checked
(`tests/encseam/findall_cases.txt`), the one rule every pcrec artifact
implements — and the bench's own note pre-authorized exactly this
answer ("the harness's rule, whatever it is — say that"). The bench
owes one adapter edit; flagged as §7.3 W23-F3 because a pre-ruling was
deviated from.

**(b)-(h) verified and applied as ruled**: `as`/`sha256` (§2.18, with
the functional-binding rule the repeated-per-case-line spelling forces);
oracle engine-ref (§2.9); tag-prose (§1.3); vocabulary (§2.15 — grammar,
head continuation, `capable`/`under`/`kind` enforcement points settled);
variant kind (§2.23, as a sub-block — the inline spelling was unsafe
against rest-of-line pattern text, e.g. a replacement text could itself
begin `kind …`); sections for --list-source (§2.24 — unconditional when
non-empty, with a `cases` section because under Option A the
expectations must be readable at the seam; conditional or flagged
emission declined as a K35 trap); STEP 0 designed-against (§0.6).

**Ratification items (iii)/(iv)** are §2.20 (`configs describe` —
resolution 1 designed: descriptive configs compose into nothing,
`target … with` refused, `use` inert-and-counted, entry-file scope,
plus N-43's permanence sentence) and §2.16 (`capable` IN the format,
fail-closed, `requires` reserved by one spec sentence) — both
presented ready-to-ratify at §7.3.

## Refuted / precisioned, beyond (a)

- **G3's "everything else UNCHANGED" cannot be byte-literal**: appended
  header columns (table_contract's own compatible evolution) move every
  successful dump's header, and case-bearing fixtures gain `#section
  cases` rows. The FACTS M2-M4/M6-M9/M11-M13 are unchanged; §9's G3/D5
  rows carry the precision (name-resolved comparison, or one re-baseline
  at delivery with the cited reason).
- **B5 is PARTIAL by design**: `pattern-esc` round-trips `\n` and a
  trailing `\r`; **`\x00` is refused by name, naming K9** — the compile
  entry takes no pattern length, so a NUL pattern would silently
  compile as its prefix, the exact trap STEP 0 closes for raw lines.
  Lifts on `rx_info.pattern_len`'s API half; §2.19.
- The `vocabulary` keyword today is refused as UNKNOWN, not with the
  later-wave sentence (MEASURED, §0.6) — SW13 grows the
  recognised-refusal list so a partial build cannot regress the
  "never as unknown" promise.

## Rulings received

F-Q1, F-Q2 and the manager's pre-rulings (a)-(h) plus leanings
(i)-(iv), all from the launch brief; no mid-flight rulings arrived.

## Validation

Design-only delivery; nothing under `src/`/`tests/`/`docs/spec/`
changed (verified: `git diff --stat main...` touches
`docs/design/dd13_format/` and `docs/dev/lanes/` only). VALIDATION
COMPLETE for this lane's scope: the measured probes above (the
three-rule find-all comparison, the 17-token first-position census at
0, the unknown-vs-later-wave refusal probes against `build/pcrec` at
b9572c66) are reproduced in §0.6 with method; a grep sweep for
stale revision-2 phrasings the W23 changes contradict was run and five
touch-ups applied (T-2/OD-2/§4.5-item-1 variant spellings, the W1.1
block-scalar correction's scope, one typo). No `make` run and none
owed — no buildable surface moved; the full battery is the manager's
at merge as ever.

## For the panel (where to attack)

1. §2.22's claim that the derived lookup needs no reader change — the
   sharpest counter would be a `verify_rxt.py` path that resolves a
   call (I found none; its composed-block handling is a structural
   skip).
2. §2.24's unconditional `cases` section — the size/compat trade was
   argued from the K35 lesson; a critic may find a consumer that
   byte-pins the dump beyond the `tests/rxtsource` fixtures named.
3. §1.2's indentation-precedes-dispatch rule as stated against
   `run.sh`'s ACTUAL arm order (I verified the refusal exists in all
   three readers, not the dispatch order of every arm).
4. §2.21's protocol choice: whether any bench regime NEEDS finditer
   counts (their throughput patterns are non-nullable today; a nullable
   member pattern would surface the divergence class).
