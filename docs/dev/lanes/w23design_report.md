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

**F6. The lane's own additivity claim was WRONG once, and a probe is
what found it.** The first draft of §1.6.1 said S1 "reproduces head
continuation exactly". It does not: **S1 is DEPTH-sensitive and today's
head rule is not.** Today's parser asks only "is this line indented?",
so a `config` body whose lines sit at different depths parses as a flat
body — MEASURED on the shipped binary, a `config c` with `flags i` at
two spaces and `engine vm` at FOUR produces a `--list-source` row
byte-identical to the evenly-indented file. Under S1 the four-space
line attaches to `flags` as a child, `flags` admits none, and the file
is refused. **That is accept → reject on a construct legal today** — a
narrowing, not a re-wording, and not additive.

Taken deliberately, with the population measured in BOTH repos rather
than assumed: 0 `config` blocks in the 210-file corpus, 0 ragged bodies
among the 19 head blocks with bodies in `tests/rxtsource/fixtures/`, and
0 `.rxt`/`.rxtin` files in `pcrec-bench` at all (read-only check). It is
also FORCED rather than chosen — depth has to mean something once a
record can contain a record, which §2.10's unified `provenance` under a
data block is — and it turns a silent authoring hazard into an error.

Three things moved because of it: §1.6.1's claim 1 is corrected and
gains a claim 2a; **§1.6.4's standing rule went from two cases to
three**, because a narrowing fell between "widens acceptance" and
"makes a file mean something different" and the rule as first written
had no answer for it; and SW16 gained the spec sentence a narrowing
owes. The general lesson is the method, not the case: *the claim was
checked by running the shipped binary on a hand-made file, and reading
the code had already produced the wrong answer* — which is also the
concrete argument for §2.25's schema being DATA, since a
machine-diffable declaration is how the next one gets found without the
hand-made file.

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

---

# ADDENDUM 2 — [DD-13b.W23] STEP 1.2: REVISION 3.2, the r57 FIX ROUND (2026-09-12, lane w23fix, opus)

The r57 D6 panel (`docs/dev/reviews/2026-09-12-r57-w23-format.md`) ran
three read-only critics against revisions 3 and 3.1 and returned **3
blockers, 14 must-fixes, 12 shoulds and 4 nits, all dispositioned
FIX-NOW**. This addendum records what moved, what I pushed back on with
evidence, and the queue that goes to Frank. The note's own §0.8 is the
finding-by-finding table; this is the lane's voice on top of it.

## What moved — the five structural outcomes

1. **The block scalar was a SECOND, undeclared structural device, and
   it is now S3 OPAQUE REGIONS** (§1.2.1). Three critics arrived at it
   from three directions (G-B1, S-M1, G-B2's N1/N2), which is the panel
   working as designed. The measurement that settles it: inside a
   `description |` body an indented `#` is PROSE and ragged indentation
   is legal, both rc 0 on the shipped binary — neither recoverable from
   S0 or S1 as revision 3.1 wrote them. **The structure layer now
   states TWO schema parameters, not one** (`opens_group`, and
   `value = prose`), and the second is the open-ended one: §1.2.5's own
   "a second prose field inherits the block scalar" is a statement that
   this parameter grows, which revision 3.1 wrote without noticing it
   was describing a structure-layer input.
2. **The narrowing census is a CLOSED LIST of five, three taken**
   (§1.6.1a). Revision 3.1 said "ONE NARROWING" and wrote §1.6.4's
   standing rule from that one case — and then did not run the rule
   across its own delivery. Four more were one probe each.
3. **The constraint vocabulary is EIGHT kinds, not five** (§2.25.3),
   and the completeness claim is withdrawn. `cross-scope` was
   DEFERRED in §2.25.4 with a trigger that a production one section
   earlier already met.
4. **The `pattern`/`pattern-esc` both-in-one-block refusal is DROPPED**
   (§2.19) — empty population, because both spellings are block
   openers and a second opener starts a new block.
5. **§2.22 gained its length discipline, its real precedent and its
   callability bound** (C-M3), and the loss it creates went to Frank as
   W23-F4 rather than being absorbed here.

## MEASURED for this revision (every number re-derived, none inherited)

All read-only, `build/pcrec` built in this worktree at the merge base
(`make -j4 CC=gcc-16`, green), fixtures in the session scratchpad,
nothing committed outside `docs/`.

| what | result |
|---|---|
| corpus census | **210 files / 3,936 blocks / 28,943 expectation lines** — the floor this change re-pins |
| non-blank non-comment lines (the number §1.2.3 actually needs) | **35,961** — revision 3.1 wrote 28,943 there, which is a partition a generic reader cannot compute |
| `prose_hash` | rc 0; the indented `#` is PROSE in the decoded value |
| `prose_ragged` | rc 0; relative indentation preserved |
| `prose_dedent` | rc 0 and **CONTENT SILENTLY LOST** — `  dedented-line-two` under a 4-space block decodes as `dented-line-two`. Filed **K57** |
| `config_tab_body` | rc 0, `flags=i engine=vm` — tabs are indentation today |
| `config_mixed_indent` (2 spaces then a TAB) | rc 0, parsed FLAT — the file that has no defined tree under any depth rule |
| ragged `config` body (2 then 4 spaces) | rc 0, `--list-source` row byte-identical to the evenly-indented control (F6 reproduces exactly) |
| two adjacent `pattern` lines | **two `pattern` rows, rc 0** — S-BL2's empty population |
| `(?&x_y)` with `x-y` beside `x_y` | compiles; artifact **byte-identical** to the same file without the sibling |
| collision population, both repos | **1** (the deliberate fixture `target_prefix_collision.rxtin`, `a-b`/`a.b`) over 96 `name` lines in 26 files; C-M1's own `x_y`-beside-`x-y` shape: **0**. pcrec-bench holds **0** `.rxt`/`.rxtin` files |
| tab-indented content lines, both repos | **0** |
| fixture head bodies | **20 across 13 of 45 files**, every indented CONTENT line width 2 |
| `run.sh` dispatch arms | **22** (24 `^`-anchored `=~` hits minus two pre-loop skips), 17 inside the pinned region + 5 after |
| `capable` in the bench's §3 checklist | **0** — revision 3.1's correction-list row cited an empty population |

## Three things I pushed back on, with the evidence

**(1) G-B2's N1 and N2 are NOT narrowings to be taken — they are
narrowings AVOIDED, and taking them would be a second, worse
decision.** The review's disposition reads "Each gets the full §1.6.4
declared-narrowing package". Applied literally that would have declared
"an indented `#` inside a block scalar is now refused" and "ragged
prose is now refused" as deliberate tightenings. But G-B1's own fix —
declaring S3 — dissolves both, and the panel's convergence note says so
("One fix … discharges all"). So §1.6.1a lists all five candidates and
marks (2) and (3) AVOIDED with the mechanism that avoids them, which I
believe is what the convergence intends and is strictly more
information than either alternative. **The reason for recording the
avoidance rather than dropping the rows**: a later wave that removes or
narrows S3 would re-create both narrowings silently, and the census is
where it would have to look.

Two things make me confident rather than merely willing here. First,
N1's case is not a judgement call: `rxt_source.c:735-747` records the
grammar decision as **deliberately OPEN** ("named rather than fixed …
the grammar decision is left open"), so revision 3.1 closed an open
question by side effect in the refusing direction. Reversing that
silently in the other direction would repeat the mistake with the sign
flipped, which is why SW16 now carries both halves — prose inside a
region, refusal outside one — as spec text. Second, ragged prose is the
one population where ragged indentation is not an error: a paragraph
with an indented example in it.

**(2) K57 is FILED, not deferred to the manager, and it is filed as a
bug rather than as a narrowing.** The brief allowed either. I filed it
(`docs/dev/known_issues.md` K57, the sole non-design file this lane
touched) because the corruption is wrong under revision 3's rules,
3.1's and 3.2's alike — no design decision fixes it by arriving — and
because a silent wrong VALUE with exit 0 is the class this project
treats as worst. The entry carries the three-line repro, the mechanism
(`skip = len < indent ? len : indent` is a BYTE count applied without
checking the bytes are whitespace), both candidate fixes with their
trade-off, and the measured population (0, in both repos). §1.6.1a
records it as explicitly NOT a narrowing, so the census stays a census.

**(3) The `wave` column is KEPT, against S-S2's lean.** The finding is
right that its only named consumer has an empty population at the
delivered pin. It is kept because the consumer is real during the
ROLLOUT: W23 is one wave but five merges (H12-H16), and every
intermediate tree is a partial build where SW13's refuse-by-name list
must be honest — which is the gap §0.6 measured, not a hypothetical.
§2.25.2 states the decision AND its expiry condition, so a later reader
can drop the column without re-deriving the argument.

## Two methodology notes worth keeping

**(a) The same-basename `-o` trap, third instance.** Reproducing
C-M1's byte-identity claim first reported a DIFFERENCE, and the
difference was the `#include` line: emitting two sources to `a.c` and
`b.c` makes every artifact differ on the header it includes. That is
`opt4_impl/CLAUDE.md`'s own recorded trap and this is its **third**
recorded instance in this house. The comparison that works is equal
output basenames in separate directories. Recorded because the first
reading would have REFUTED a true finding.

**(b) I got one of my own corrections wrong and the probe caught it.**
Working C-S8 (the arm count), I wrote that revision 3.1's parenthetical
— *"its one tolerant regex is the blank-line skip"* — was itself wrong
and that the tolerant regex was the comment test. Reading
`run.sh:1692-1693` settled it the other way: `^[[:space:]]*$` IS the
blank-line skip and IS the tolerant one, `^#` is column-1-anchored like
every arm, and 3.1 was right. Corrected in place before delivery.
The shape is worth the line because it is the round's own subject one
level up: **a correction is a claim, and it needs the same probe the
thing it corrects needed.** I had the file open for the count and did
not re-read it for the adjective.

## What this revision does NOT change

No ruling is reopened. No need N-nn changes its disposition. §1.4's
wave table is untouched, W23 still carries no abi event, and §2.26's
audit still changed no semantics — the correction to its COUNT (three
moves, not four) is a framing fix, not a re-decision. The `description`
widening stays; only its attribution moves, from the ownership audit to
§1.2.5's consequence of the structure-layer re-factoring.

## Frank queue after this round (§7.3)

- **W23-F1** `configs describe` (D93) — unchanged, ready-to-ratify.
- **W23-F2** `provides` in-format — unchanged in substance; the rename
  from `capable` does not touch the question.
- **W23-F4 (NEW)** — the derived-identifier repair removes the ability
  to declare a deliberately NON-CALLABLE definition, a boundary
  `src/parse/rxt_source.c:288-291` records as a FEATURE. Written
  ready-to-ratify beside F1/F2: what is lost, the four reasons ACCEPT is
  recommended (the replacement is better than the thing lost; `export`
  already governs delivery; no current customer; reversible at a known
  price), and what ACCEPT costs stated so the ratification is informed.
- **W23-F3** stays RESOLVED, not a question.

## Validation

Design-only plus one `known_issues.md` entry. `git diff --stat
main...HEAD` touches `docs/design/dd13_format/`, `docs/dev/lanes/` and
`docs/dev/known_issues.md` only — nothing under `src/`, `tests/` or
`docs/spec/`. `build/pcrec` was built in this worktree
(`make -j4 CC=gcc-16`, rc 0) for the read-only probes above and is
gitignored; no suite was run and none is owed, since no buildable
surface moved. Every probe fixture lived in the session scratchpad.

## For the panel, if there is another round

§5.2a is re-aimed in the note itself and now has five items. The one
worth starting from is item 1's re-aim: revision 3.1's narrowing sweep
was pointed at the HEAD, and the fifth narrowing was in the composer's
name lookup with no head line involved. **Walk every §2 rule that says
"refused" and ask what it accepted yesterday** — that direction has had
one pass and found one.

---

# ADDENDUM 3 — [DD-13b.W23] STEP 1.3: REVISION 3.3, the r57 ROUND-2 FIX ROUND (2026-09-12, lane w23fix2, opus)

The r57 round-2 critic re-checked revision 3.2's three blocker fixes and
ran Addendum 2's own new attack. **S-BL1 and S-BL2 HOLD OUTRIGHT; the
S3 fix held in DIRECTION and failed end to end on its own axis.** Four
must-fixes, two shoulds, one nit. Everything below landed; the note's
§0.8 ROUND 2 block is the finding-by-finding table and this is the
lane's voice on top of it. **The Frank queue is UNCHANGED: W23-F1,
W23-F2, W23-F4.**

## What moved

Four of the seven findings are one section — §1.2.1, the structure
layer — and that concentration is the round's real shape: **every one
of them is a rule that was stated in prose and pinned by nothing.**

1. **R2-F1 — S3's trigger is PARAMETERIZED and takes the TRIMMED
   value.** 3.2 wrote *"a CONTENT line whose value is the single byte
   `|`"*, which opens a region on `pattern |` — a legal pattern
   (measured rc 0, the dump's pattern column is `|`) — and turns a
   working file into a refusal. The EBNF had the kind condition right
   all along; the normative sentence contradicted it. The trim half is
   the shipped rule verbatim (`rxt_source.c:1222-1226`, r46sem finding
   14, leg C's `v.strip() == '|'`, fixture
   `desc_pipe_trailing_space.rxtin`), not a new invention.

2. **R2-F2 — the COMMENT line terminates, and this one falsified a
   claim.** S0 declared the class; S1 and S3 never said what it does.
   Silence there is not neutral: it reads as "skip it and carry on",
   which ACCEPTS two files the shipped binary refuses. Both measured
   here, both rc 1 at line 4 with the same message: a column-1 `#` in
   the middle of a `config` body, and one in the middle of a
   `description |` region. The second is worse than a widening — under
   the transparent reading the opener ends up with TWO disjoint prose
   regions, a shape S3's single-extent rule cannot express at all. One
   sentence in S1 and one in S3 close both, and §1.6.1's claim 2 ("no
   file refused today is accepted") goes back to being true; the
   correction is recorded at claim 2 rather than tidied away, because
   the claim was shipped FALSE.

3. **R2-F3 — BLANK narrows to the EMPTY line; WHITESPACE-ONLY becomes
   its own class and is INERT.** See the pushback section: I took the
   manager's direction and changed the outside-a-region half on
   evidence.

4. **R2-F4 — the structure layer's second parameter is the
   `value`/`children` PAIR, said once.** Three sites disagreed (§1.2.1
   and §1.2.2 said `value` alone; §2.25.2 said both things in one
   subsection; §1.3's EBNF said the pair). The tiebreaker the finding
   named is S-R5's detectability and it decides cleanly: **if the
   structure layer read `value` alone, flipping a row's `children` from
   `prose` to `none` would change nothing observable anywhere** — the
   region still opens, its lines are bytes, and bytes reach no validity
   check — so a normative column would carry a corruption with no
   detector in the tree. S-R5 now names both plants.

5. **R2-B — the census carries STEP 0's two refusals, and states its
   SCOPE.** Rows (10) NUL and (11) duplicate `description`, each marked
   *"landed by STEP 0 (lane `rxtnul`, `d4576c48`), not by this
   revision"*. I took the carry rather than the scope-heading option
   the finding offered as an alternative: somebody asking "what did W23
   stop accepting" comes to this table, and a list calling itself
   CLOSED while two accept→reject changes from the same plan row sit
   outside it answers that question wrongly. §1.6.4's duty clause gains
   the general form — **the sweep is over the FORMAT, not over the
   lane's diff**.

6. **R2-C — the cardinality decision, made after measuring.** §2.25.2
   carries a per-kind table; H16 carries the choice; §1.6.1a rows (8)
   and (9) carry the compatibility package. Two deviations from the
   leaning, both forced by the measurement — see below.

7. **R2-D — "expectation line" is defined at §1.1's floor**: eight
   first-token kinds, `perr` INCLUDED, with 28,488 and 24,016 both
   named so a reader who lands on either knows which reading produced
   it.

## MEASURED for this revision (every number re-derived here, none inherited)

All against this worktree's `build/pcrec` at the lane's merge base,
plus `run.sh --dump` and `verify_rxt.py --dump` where the leg can see
the file. Fixtures lived in the session scratchpad.

| probe | result |
|---|---|
| `pattern \|` | rc 0, dump's pattern column `\|` — R2-F1's witness |
| column-1 `#` mid `config` body | **rc 1 at the line below**, *"indented line continues nothing"* |
| column-1 `#` mid `description \|` region | **rc 1 at the line below**, same message |
| whitespace-only line in a block scalar | rc 0, value `para one\n·\npara two` — it is IN the value |
| TRULY empty line in the same place | **rc 1 at the line below** (r46sem-10, working as ruled) |
| whitespace-only line in a `config` body | rc 0, body continues (`flags=i engine=vm`) |
| whitespace-only line at file start / after a blank | rc 0 in **all three legs**, both positions |
| 2nd `name` / `engine` / `encoding` / `features` / `flags` | rc 0, **last wins, no diagnostic** |
| 2nd `budget` repeating a FIELD (`steps=50`, `steps=99`) | rc 0, 99 wins |
| 2nd `budget` naming the OTHER field (`steps=50`, `frames=4096`) | rc 0, **both kept** |
| 2nd `export` | **rc 1**, *"a block has one 'export' line…"* |
| duplicate-line population, 258 files / 4,053 blocks / 19 configs | `name`/`engine`/`encoding`/`features`/`flags`/`description`/`export`: **0 each**; `budget` LINE: **1**; `budget` FIELD: **0** |
| pcrec-bench `.rxt`/`.rxtin` files | **0** (read-only `find`) |
| census awk re-run | **210 / 3,936 / 28,943**, `perr` **455**, without `perr` **28,488**, six-kind reading **24,016** |

## Two deviations from the manager's leanings, both on evidence

**(a) R2-F3: "INERT", not "attachment-relevant".** The leaning was that
a whitespace-only line become attachment-relevant — indent = its
leading whitespace, value empty, schema-inert. That dissolves the same
two narrowings, and it introduces a THIRD, because S1's own
*"attaches to nothing is a structure error"* arm then fires on two
shapes that are legal today: a whitespace-only line as a file's FIRST
line, and one immediately after a blank. Measured rc 0 in all three
legs for both. Declaring the line INERT outside a region — not CONTENT,
not BLANK, simply stepped over — dissolves the two narrowings, takes no
third, is what all three shipped legs already do at all four probed
positions, and is the shorter rule. The direction (BLANK narrows to the
empty line; whitespace-only is bytes inside a region) is the manager's
and is taken unchanged.

**(b) R2-C: `budget` is not a scalar kind, and `flags` is.** The
finding named five kinds and the leaning was "scalar kinds REFUSE
duplicates". Measuring first is what the brief required and it changed
the answer twice:

- **`budget` has a NON-ZERO population and the member is deliberate.**
  `tests/harness/giveup.rxt:19-23` writes `budget steps=50` and
  `budget frames=4096` in one block, and `parse_setting`
  (`rxt_source.c:615-620`) routes them to two separate slots.
  `cardinality: at-most-one` would have refused a corpus file
  `make test` depends on. So `budget` is **`accumulate` over the field
  set `{steps, frames}`** and the refusal lands on a repeated FIELD,
  whose population is 0. **This is the flagged non-zero population the
  brief asked me to report before taking anything**, and the report is
  that the narrowing as proposed is not taken at all — a different,
  narrower one is.
- **`flags` was not on the list and is in the identical state.**
  Measuring the shipped arms found it silently last-winning like the
  other four, population 0. It is taken with them, because leaving one
  scalar settings kind last-winning reproduces the inconsistency the
  decision exists to remove, one kind smaller — and a `cardinality`
  COLUMN whose answer is uniform where the kinds are uniform is the
  whole argument for a column over six hand-written refusals.

The general lesson, now §1.6.4 case 5: **a cardinality is a property of
the VALUE SPACE a kind writes into, not of its spelling.** Six of these
seven kinds own one slot and one owns two, and nothing in the line's
syntax says which — only the population did.

## What else moved, because a stale statement is a defect

Not in the brief's section list, and changed because the round's own
edits falsified them:

- §1.2.4's "the `children` column is not a parameter the structure
  layer reads" — false at 3.3; reworded, with the sigil's yield
  re-derived against the pair.
- §1.2.6's sub-block/region row now states the THREE terminators both
  mechanisms share.
- §5.2a item 5's "known-weak point" named `children` as unread; item 5
  is re-aimed (it scored three times in round 2) and a new item 6
  attacks the cardinality decision's counting claim, naming the one
  shape the rule deliberately excludes (a duplicate that exists only
  after `from`-composition — §2.25's cardinality is as-written, never
  resolved).
- §3.4's SW16 carries the four line classes and their effects, the
  parameterized+trimmed prose trigger, and the cardinality rules;
  the standing rule it states is now FIVE-CASE.
- §9.1's A3/A4 plan gains **four fixtures** — the comment-terminates
  pair, the paragraph break (asserting the decoded VALUE, not merely
  acceptance, since a reader that ends the region there still
  "accepts" the file and just loses the paragraph), and a four-position
  whitespace-only inertness fixture whose last three positions are
  exactly where the rejected formulation would have refused.

## The one thing I would attack next

§5.2a item 5 has now scored on three separate revisions, and the
pattern across all three hits is the same: **a line class or a value
form declared in one place and given its effect nowhere.** 3.1 declared
`|` as a value discriminator and gave it no structural effect (G-B1).
3.2 declared S3's region and gave the COMMENT class no effect inside or
outside it (R2-F2), and wrote BLANK with a parenthesis that gave
whitespace-only lines an effect nobody intended (R2-F3). The
generalisable check is mechanical and nobody has run it: **enumerate
S0's classes and S3's boundary conditions, and for each one point at
the sentence in S1/S2/S3 that says what it does.** At 3.3 all four
classes have such a sentence. That is a property a reviewer can verify
in a minute and it has been false twice.

## Validation

Design-only. `git diff --stat main...HEAD` for this round touches
`docs/design/dd13_format/format_design.md` and
`docs/dev/lanes/w23design_report.md` only — nothing under `src/`,
`tests/` or `docs/spec/`. The read-only probes used this worktree's
already-built `build/pcrec` (gitignored) plus `run.sh --dump` and
`verify_rxt.py --dump`; no suite was run and none is owed, since no
buildable surface moved. **Validation for this round is COMPLETE.**
