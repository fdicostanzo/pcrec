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

---

# ADDENDUM — [DD-13b.W23] STEP 1.1: REVISION 3.1 (2026-09-12, lane w23recon, opus)

Same branch `lane/w23design`, continuing from `b39eb23e` after merging
main (clean, three docs-only commits). DESIGN ONLY, same terms: every
commit touches `docs/design/dd13_format/` and `docs/dev/lanes/` only —
nothing under `src/`, `tests/` or `docs/spec/`; the only tree access was
read-only probing of `build/pcrec`, `tests/harness/verify_rxt.py` and
the corpus.

## Why there is an addendum

Two Frank rulings were issued MID-FLIGHT on 2026-09-12 and never reached
the authoring lane — its §"Rulings received" above honestly records that
none arrived. Both are now durable in
`docs/design/dd13_format/frank_inputs.md`'s 2026-09-12 section: the
**internal-consistency ruling** (five numbered consequences: no
per-keyword structural exceptions; a `version` header is on the table; a
declared schema with validation; sub-blocks get explicit syntax; the
format must be structurally parseable without context) and the
**ownership framing** (the bench's sketches are capability requirements,
the syntax is pcrec's, and long-term viability of the format outranks
bench convenience and minimal-diff). Revision 3.1 works both through the
delivered text.

**The ruling supersedes revision 3's P-Q1 answer by name.** It says the
manager's leaning — relax the head/body asymmetry for a named set of
sub-block keywords — is wrong *"because that answer requires a keyword
table to find structure, which is exactly the context-dependence ruled
out here"*, and revision 3's §1.2 was that answer.

## What moved

**1. §1.2 is rewritten as TWO LAYERS, and the head/body asymmetry is
DELETED rather than narrowed.** A STRUCTURE layer of three rules (S0
line classes; S1 indentation attaches a line to the line above it; S2 a
declared two-member BLOCK-OPENER set groups siblings) recovers blocks,
sub-blocks and line membership with no keyword table. Everything else —
scopes, value shapes, cardinality, required/conditional, closed sets —
is SCHEMA (§2.25). Three revision-3 rules stop existing: head-means-
continuation/body-means-not, "the head ends at the first `pattern` line"
as a structural rule (it survives as a scope rule, AR-4 unchanged), and
"an indented line not under a sub-block keyword is a hard error" (an
indented line always attaches; whether its parent admits children is
schema). The bench's M8 loud refusal survives in both arms. Cost:
exactly one diagnostic tier and nothing else.

**2. §1.6: the version break is PRICED and DECLINED, the keyword
RESERVED.** The re-factoring is additive — no file parses differently
(0 indented lines, and S1 reproduces head continuation exactly), no
refused file is accepted except one deliberate widening, every new token
measures 0. So "if needed" is answered NO. What *would* need it is named
and priced: making block grouping structural, which means indenting
28,943 case lines across 210 files, forking every `.rxt` producer, and
running two grammars in three readers permanently — declined. `version`
is reserved (0 occurrences, absence = version 1, position fixed at the
file's first content line) as one-line insurance; `schema` was
considered and NOT reserved, because a file-declared grammar is not the
design.

**3. §2.25 designs the SCHEMA**: one `.def` table on `limits.def`'s
shape, the parser as its reader through one exhaustive `default:`-less
switch (`definitions.c`'s `pcrec_def_tag_applies` precedent), and
`--list-schema` as the sixth registry dump. Five constraint kinds
(`required`, `required-if`, `exactly-one-of`, `closed`, `unique-by`),
each with a named W23 customer under a membership rule copied from
§2.10's data-block family. `vocabulary` is nested as the FILE-declared
rows (a `source` column), which is Frank's consequence 3 read literally.
§2.24's VALIDATES-vs-RECOGNISES statement is upgraded from prose to a
`validated_by` column the spec table is RENDERED from. Four D77
deferrals with triggers; §2.25.5 states the honest limit (the schema is
leg A's; legs B and C stay independent ON PURPOSE, because a generated
leg B would share a source with what it controls).

**4. §2.26 is the ownership audit** — all thirteen W23 spellings swept,
nine confirmed with one line each, four moved.

## What stayed, and why

- **Every need's disposition, every P-Q answer, every refusal rule and
  the whole wave table are revision 3's.** An ownership ruling about
  syntax is not a licence to reopen settled semantics.
- **Revision 3.1 adds NO production**, carries no abi event, and asks
  Frank nothing new.
- **Bare indentation beats a visible marker** (§1.2.4), designed both
  ways: a marker makes structure depend on two signals that can
  disagree, duplicates a schema fact per occurrence, and would need
  either a second mechanism beside the shipped head or a break. The
  consequence-4 obligation is met by the unified rule plus a printable
  schema. The `|` block scalar and `tag-prose`'s `"` are named as what
  they are — **value-form discriminators**, not structure markers.

## The four spellings that moved (§2.26)

| moved | why |
|---|---|
| `capable` → **`provides`** | the pattern side is `tag requires=…`; `requires`/`provides` is one relation read from both ends, the pairing every neighbouring ecosystem uses. `requires`/`capable` pairs a verb with an adjective. 0 occurrences anywhere |
| `licence`/`licence-note` → **`license`/`license-note`** | the value is an SPDX identifier and SPDX's own key is `License` — a gratuitous translation step on the one field that crosses an ecosystem boundary |
| the `freq` block's `exemplar`/`date`/`bytes`/`sha256` → **the shared `provenance` record** | **the audit's biggest finding: revision 3 shipped TWO provenance vocabularies for one idea**, with `exemplar`≡`source` and `date`≡`retrieved` naming the same facts twice. Unified into one record at two parents, required subset declared per parent by the schema. `analyzer` deliberately stays on the data block — it names the TOOL, not the origin |
| a pattern block's `description` → **`prose-value`** | the one SHIPPED refusal this revision changes, in the widening direction. The W1.1 correction rested on the head/body asymmetry (now deleted) and on `run.sh` having no continuation mechanism (W23 gives all three legs child-consumption for `provenance` anyway). `block_scalar_in_body.rxtin` is RE-AIMED, not deleted — inverted to a three-way agreement on the decoded value, which catches more than a three-way agreement on a rejection |

## Findings — measured, not argued

**F1 (the sharpest). Revision 3's own load-bearing parser rule is FALSE
in two of the three readers it is asserted of.** §1.2 rule 1 said *"the
indentation test PRECEDES token dispatch"*, binding on all three body
readers. Measured on three fixtures:

- **Leg A** (`src/parse/rxt_source.c:992`) — true, the check sits above
  the `pattern` dispatch.
- **Leg B** (`tests/harness/run.sh`) — **no indentation test exists at
  all.** All 24 dispatch arms are anchored `^<keyword>` (the one
  leading-whitespace-tolerant regex is the blank-line skip), so an
  indented line reaches the catch-all *"unparseable .rxt line (hard
  error)"* by FALL-THROUGH, not by a rule.
- **Leg C** (`tests/harness/verify_rxt.py:407-419`) — **false on the
  pre-body path.** It splits the line (which strips leading whitespace)
  and raises the head-word or no-open-block diagnostic BEFORE reaching
  its indentation check at `:424`. An indented `m` line before the first
  `pattern` reports *"'m' line before any pattern block"*.

Nothing is mis-parsed today — every arm is a hard error — so this is a
diagnostic-tier divergence in D26's terms. What is false is the claim
that a RULE holds in three places. It matters for W23 because that rule
was the thing closing P-Q1's one parser hazard, so the hazard was closed
by a rule that mostly did not exist. Under §1.2.1 the hazard is
structurally impossible instead (an opener applies among siblings; a
child is not a sibling), and H12 is re-stated as a rule to BUILD in two
legs rather than to extend in three. §9's A-group owes the fixture.

**F2. The corpus census the note is written against is stale, and the
way it went stale is the durable part.** §1.1 pins 179 files / 3,265
blocks / 26,691 expectation lines; re-measured by the same method at
the merge base it is **210 / 3,936 / 28,943** ([M5.0]'s `tests/utf8/`
corpora landed after r44). Nothing in the design depends on the values —
INV-COMPAT is a relation between two parses — but a denominator
assertion written against a constant a growing corpus outruns stops
meaning what it was written to mean, which is one step from the vacuity
it exists to prevent. §1.1 now states the RULE instead: derive the
denominator at check time, assert EQUALITY against the other parser's
count, and pin a separately re-pinned FLOOR.

**F3. Blank lines are not a block separator, which closes the one
alternative to the keyword.** Only **1,016 of 3,936 `pattern` lines
(26%)** are immediately preceded by a blank line. So §1.2.3's admission
— block grouping needs S2's two-member opener set — is not a design
choice with a cheaper option sitting beside it.

**F4. The ruling's literal reading is not fully achievable and the note
says so rather than softening it.** Structure recovery needs exactly one
keyword fact: which tokens open a block. §1.2.3 states it, §1.6.2 prices
removing it, and §2.25 makes it a declared, printable column rather than
parser knowledge — which is the strongest available form of "the schema
never decides where structure begins" short of the break.

**F5 (in the design's favour). The unification found a place the general
mechanism was already earning its keep.** Because a data block admits
children and `provenance` itself admits children, the unified record is
two levels of S1 with no new mechanism — and `provenance` is now a
kind used at TWO parents, which is what makes §1.2.6 a general form
rather than a special case with two instances.

## Frank queue (§7.3)

- **W23-F1** (`configs describe`, D93 territory) — **UNCHANGED**,
  ready to ratify as designed.
- **W23-F2** (the capability declaration lives IN the format) —
  **UNCHANGED in substance**; the line is now spelled `provides`, which
  is a manager call under the 14:5x syntax delegation and does not touch
  the in-format-vs-bench-side question Frank is being asked.
- **W23-F3** (the `mc` deviation) — **RESOLVED, off the queue.** The
  manager has ACCEPTED the deviation; it stays listed only because the
  outbox message owes the bench their one adapter edit.
- **Revision 3.1 adds nothing to the queue**, deliberately: both rulings
  delegate syntax to the manager, so §2.26's moves and §1.6's declined
  break are defended here and the panel is the check on them.

## For the manager, at delivery

The outbox message to pcrec-bench (D78, `inbox_from_pcrec.md`) owes
**one correction list**, collected in §9's head so it is not discovered
check by check: `capable` → `provides`; `licence`/`licence-note` →
`license`/`license-note`; the `freq` block's provenance fields become a
`provenance` child; a pattern block's `description` accepts a block
scalar. Every affected check is behavioural and still passes — what
moves is the literal token some of them type. Plus the `mc` adapter edit
(empty-match advance from the reported START, not `max`) that revision 3
already owed them, and one offered addition: `--list-schema` lets their
D4 probe compare the rendered spec table against the dump instead of
against prose.

## Validation

Design-only; **VALIDATION COMPLETE for this lane's scope** and nothing
owed. Verified `git diff --stat main...HEAD` touches
`docs/design/dd13_format/` and `docs/dev/lanes/` only. No `make` was
run and none is owed — no buildable surface moved; the full battery is
the manager's at merge, as ever. Every measurement above was re-run in
this worktree at the merge base against `build/pcrec`,
`tests/harness/verify_rxt.py` and the corpus, read-only, with the
fixtures written to the session scratchpad and never committed.

## For the panel (§5.2a carries this in the note itself)

The four shortest paths to breaking revision 3.1: §1.6's additivity
claim (attack it from the HEAD, not the body — S1 is asserted to
reproduce `parse_prose`/`parse_config` exactly); §1.2.3's "block
grouping is the only place" (candidates for a second: `under`'s
qualified line, `@file:`'s suffixes); §2.26 item 10's unification (find
a fact one parent needs that the other's record has no field for, and
it is a union pretending to be a unification); and §2.25's scope (a
constraint kind with a speculative customer, or a W23 refusal none of
the five kinds can express — which would make the schema a partial
declaration presenting itself as a complete one).
