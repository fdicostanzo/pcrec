# [DD-13b.W23.1] — the SCHEMA TABLE and its surface (lane w231)

Branch `lane/w231`, from `3127cf62`. Step brief:
`docs/design/dd13_format/w23_impl.md` REVISION 1.1 §6.1; design of record
`format_design.md` 3.4.2.

Everything §6.1's build order names is built. What follows is what the
build MEASURED, what it found that the note did not anticipate, and the
four places the note contradicts itself or the tree — each stated with
the resolution taken, because the brief's standing line is to report a
disagreement rather than improvise past it, and improvising past it
silently is the failure mode that line exists to stop.

---

## 1. What landed

| # | build order item | landed as |
|---|---|---|
| 1 | the schema table + the Makefile prerequisite | `src/parse/rxt_schema.def` (66 rows), `Makefile:150`'s prerequisite list |
| 2 | the reader, the three parameter queries, the exhaustive switch | `src/parse/rxt_schema.c` |
| 3 | leg A's dispatch as a table WALK — S0-S3 and parameter 3 | `src/parse/rxt_source.c` |
| 4 | the diagnostic CLASS tag | `rxt_fail` + 62 call sites |
| 5 | `--list-schema`, including the `surface` section | `src/parse/schema_dump.c`, `cli/main.c` |
| 6 | W23-S3, S241, S244, the structure-layer fixtures | `tests/rxtsource/` (six arms, ten fixtures), `tests/mech/sabotages/` |
| 7 | SW2, SW16, SW17, SW13 — and SW21, which §4.1 also assigns here | `docs/spec/{rxt_format,cli,table_contract,registry}.md` |

Plus §4.3's withdrawal (`testee`/`option`), which §4.3 assigns to this
step's parser and census.

## 2. Acceptance, MEASURED

| acceptance | measured |
|---|---|
| corpus census `210 / 3,936 / 28,943` unmoved | **unmoved**, the suite's own summary line |
| `--list-source` unchanged over the corpus | **210 files, 0 differing, 0 refusals either side**, against a scratch build of `3127cf62` |
| `make strict` clean | **clean** (`-Werror -Wshadow`, whole tree) |
| `--list-schema` emits a row per dispatched (scope, kind), verified behaviourally | W23-S3's six arms, all green |
| the three parameters are each ONE query | `opens_group: true` → **2 rows**; the `value`+`children` PAIR → **6 rows / 5 kinds**; `children: tree` → **2 rows / 1 kind** |
| the narrowings' fixtures RED before, GREEN after | `config_tab_body` and `config_mixed_indent` both **rc 0 at the branch point, rc 1 now** |
| S241 and S244 each turn their named check red | **both measured under the plant** (§5) |
| `tests/rxtsource` green | **145 passed / 1 recorded / 0 failed** |
| `make test` green | **OWED** — launched as this lane's last act, log path in the handback |

`tests/codegen` (109/0, including the K37 bare-call guard at 711 sites and
SABANCHOR over 248 rows, both new anchors resolving) and `tests/cli`
(0 failed) were run directly and are green.

## 3. THE FOUR CONTRADICTIONS, and what was done about each

### 3.1 §2.2 and §6.1 disagree about whether W23 ROWS exist at W23.1

§2.2: *"It may not add `tag` or `ext` arms — only their ROWS, marked with
their `wave`, so SW13's refusal list is derived and correct at the
intermediate pin."* §6.1's acceptance: *"`opens_group: true` returns
exactly `pattern` (one row at this step)"* and *"`children: tree` returns
**zero** rows at this step … because `ext` has not landed."*

Those cannot both hold. **Resolved in §2.2's favour**, on the ground that
§2.3 is a contract the step SIGNS — *"`refuse_wave` … W23.1 re-bases it on
the schema's `wave` column so the list is derived"* — and a derived list
needs rows. Without them `vocabulary` reads *"not a file-level
directive"*, which is the K14 gap §2.3 measured and assigned to this step
to close.

So the measured answers are 2 / 6 / 2 rather than 1 / 5 / 0. The property
§6.1's bullet is actually about — *"a parameter whose row set is
legitimately empty must be distinguishable from a parameter that is not
implemented"* — is delivered and is checkable: all three are plain column
filters over one TSV returning a possibly-empty set, never an error.

### 3.2 "five rows" is five KINDS; the (scope, kind) model gives six

`format_design.md` §1.2.1's parameter table says the prose set is *"today:
`description`, `license-note`, `adaptation`, `attribution`, `note` — five
rows"*. Those are five KINDS, and `description` exists at file scope AND
block scope, so a table whose key is (scope, kind) holds **six rows**.
`children: tree` is the same shape one row smaller: `ext` is ONE kind at
TWO scopes, so **two rows**.

Not a defect in either document, but a number a check could be written
against, so it is stated here in the form a check can use: **kinds and
rows are different populations and the design's counts are kinds.**

### 3.3 §6.1 says eleven structure-layer fixtures; §3.2's table has ten

Counting §3.2's rows marked W23.1: `prose_hash`, `prose_ragged`,
`prose_dedent`, `config_tab_body`, `config_mixed_indent`,
`comment_in_config_body`, `comment_in_prose_region`,
`prose_paragraph_break`, `ws_only_line_positions`, and
`block_scalar_in_body` (re-aimed rather than added) = **ten**. Ten landed.
An eleventh — `version_reserved.rxtin` — was added by this lane for a
reason §3.4 explains, so the delivered count is eleven by coincidence and
not by agreement.

### 3.4 SW13 promises `version` is RESERVED, and nothing implemented it

§1.3: *"Still refused after W23, BY NAME: `version` (RESERVED …)"*, and
SW13 is W23.1's. A keyword with no schema row refuses as an unknown token
in its scope — which is the **truth about a withdrawn production and a lie
about a reserved one**. The two are different facts and a reader acts on
them differently: one hunts a typo, the other waits for a wave that is
never coming.

So `version` has a row whose `wave` is a RESERVED sentinel
(`PCREC_RXT_WAVE_RESERVED`), the same derivation produces it, and
`refuse_wave` gains one branch and a third sentence. Writing the spec
claim without the row would have been a promise with no producer, which is
exactly what §4.1's own SW20 finding is about one row over.

## 4. WHAT THE BUILD FOUND THAT THE NOTE DID NOT

**`RxtScope` was already taken.** `src/parse/rxt_compose.c:112` has a
file-local `typedef … RxtScope` — the composer's SAVED PARSE SCOPE — so
the schema's scope enum is `RxtSchemaScope`. Two unrelated notions of
"scope" in one subsystem, and the collision surfaced as five
`request for member … in something not a structure` errors in a file this
step does not touch.

**The `wave` values in the old hand table were STALE, and the schema is
where it showed.** `head_vocab`/`block_vocab` marked `include`, `tag`,
`freq` as wave 2 and `use`, `oracle`, `variant` as wave 3. F-Q1 collapsed
W2 and W3 into ONE W23 delivery, so every one of those numbers had been
wrong since the ruling; the fixtures greped `'NOT IN THIS BUILD'` and
never the number, so nothing saw it. The rows read 23 now and
`unknown_kind.rxtin`/`wave2_keyword.rxtin` moved from "wave-2" to
"wave-23" in their diagnostics.

**Bash's `read` collapsed the dump's empty TAB fields, and the arm
reported 0 of 0 — a GREEN VACUITY rather than a failure.** W23-S3's wave
arm was first written as `while IFS=$'\t' read -r …` over the dump. Most
schema rows have an empty `constraints` cell, `read` collapses
TAB-delimited empty fields even under a single-character `IFS` (the defect
`tt4m3_report.md` records), every later column shifted left, and the
`wave` field the arm tested was somebody else's. It read **0 rows out of a
population of 7** and printed `0 of 0`, which the check's own condition
then had to be taught to fail on: *a population of zero is also a failure
here.* Rebuilt on `awk`. **The transferable half is not the bash trap —
it is that an arm which derives its population from the data it is
checking must fail on an EMPTY population, or the first thing that breaks
its extraction turns it green.**

**W23-S3's cardinality arm had to be rewritten before S241 had a
detector.** As first written it hardcoded `name` (at-most-one, refuse) and
`m` (repeat, accept). S241's plant mislabels one row's cardinality in the
DUMP — and the plant moves `name` OUT of the at-most-one set, so an arm
checking only "at-most-one rows refuse a second" passes under it
completely. The arm is dump-driven and two-directional now, over **16
block rows** with a probe-line table whose own coverage is asserted (a
kind with no probe FAILS rather than being skipped, since a skipped row is
the population nobody counts). Measured under the plant: `1 of 16 block
rows disagree`.

**The prose PAIR's second plant was measured, not argued.** S244 ships
plant (b) — `children` flipped from `prose` to `none`, `value` untouched —
and under it `prose_hash.rxtin` refuses with *"indented line continues
nothing ('description' takes no continuation)"*. That is the plant which,
if the structure layer read `value` alone, would change nothing observable
anywhere; the fixtures assert a region's DECODED VALUE, which is what
makes it visible.

**The attachment stack needed no limit, and that is a finding about
`limits.def` rather than about the stack.** The first draft was going to
add a depth cap row, which would have moved `limits_check.sh`'s 57-row
manifest and `limits.md` §3.5. It is unnecessary: each attachment level
costs at least one more leading SPACE, so the depth is bounded by the line
it is reached on. An arena-backed growing stack adds no number to the
tree at all — and §1.2.1's own argument ("one bit per open frame, and the
frames existed before") is the same observation from the other side.

## 5. The sabotage rows, validated

| row | plant | measured under the plant |
|---|---|---|
| **S241** | `schema_dump.c` hand-writes the block `name` row's cardinality as `repeat` while the parser refuses a second one | `FAIL: W23-S3 arm 5: 1 of 16 block rows disagree with the dump's own cardinality column` |
| **S244** | `rxt_schema.def`'s file `description` row: `children` `prose` → `none` | `prose_hash.rxt:11: [structure-attachment] indented line continues nothing ('description' takes no continuation)` |

Highest id on main re-checked before numbering: **S238**. Both anchors
resolve under `make test-codegen`'s SABANCHOR check (248 rows).

**S241 deviates from §3.5's spelling and says so.** The note's plant
disagrees on `provenance.fidelity`'s `closed` set — a W23.3 production,
which W23.1 declares but does not ENFORCE, so that plant would turn
nothing red at this pin and the row's own stated rule ("a row must fail on
the tree it is planted into") forbids it. The plant moved to a column that
is live at W23.1. The constraint kinds' ENFORCEMENT arrives with their
productions; at this pin the column is declared, rendered and parsed
through the exhaustive switch, and nothing enforces it, which the
`.def`'s own header says rather than implying otherwise.

## 6. What this step deliberately did NOT do

- **`unique-by` is not declared on the three duplicate-name refusals.**
  `config`, `target` and block `name` collisions are enforced in code with
  three different wordings. §2.25.3 names `unique-by`'s customers as
  `under`'s key tuple and a `vocabulary` key — neither of these — so
  declaring it here would have added a SECOND parser-code exception to a
  schema that claims exactly one, which §5.2a item 4 calls the dangerous
  outcome. The absence is consistent with the design's own customer list.
- **`flags`/`engine` value sets are not declared `closed`.** Same reason:
  `closed`'s named customers are `fidelity`, `kind`, `convention` and
  `vocabulary`-declared keys.
- **Legs B and C are untouched**, so two fixtures assert leg A alone where
  §3.2's table says three legs. `block_scalar_in_body` in particular is a
  refusal that changed DIRECTION: leg A accepts a block `description |`
  now and legs B and C still refuse every indented line until W23.2's
  attachment arm. The three-leg form of both assertions belongs to that
  step, and making them three-leg here would assert a claim about two
  parsers nothing has taught.
- **K57 is not fixed** (ruling R4), and `prose_dedent.rxtin` pins the
  wrong value with K57 named, so the fix breaks the pin.
- **No `abi` bump**, and no file under `src/gen/`, `src/ir/`, `src/opt/`
  or `lib/pcrec.h` was opened — §1.9's claim, checkable by `git diff
  --stat` rather than by this sentence.

## 7. §4.3's three arms, measured at this pin

- **(a) the DATA arm** — no `.rxt`/`.rxtin` file has a line whose first
  token is `configs`, `testee`, `option`, `provides` or `capable`:
  **0 of 272 files**, unchanged.
- **(b) the PARSER arm** — the note measured **1** before this step
  (`rxt_source.c:149`'s two `config_vocab` rows). It reads **0** now: the
  keyword tables do not exist, and a withdrawn production has no schema
  row. The arm's whole value is that it read 1 before and 0 after; an
  arm whose baseline is zero proves nothing about the change made.
- **(c) the SPEC arm is a READ and not a grep.** `rxt_format.md`'s
  later-wave keyword paragraph named `testee` and `option` and now does
  not; it gained the sentence that the list is DERIVED, so the next
  withdrawal costs no edit here at all. `rxt_format.md:130`'s *"configs
  are three artifacts"* is legitimate English and was read rather than
  matched, exactly as §4.3 requires.

Census re-pinned in the same change: `CENSUS_WORDS_32` → `CENSUS_WORDS_30`
with its length pin and both messages, and the failure message now says
what the two ways OUT of the list are (withdrawal, graduation) rather than
pointing at a section that no longer carries the list.

## 8. Owed

**`make test`.** Launched as this lane's last act per BOILERPLATE's
DO-THEN-FINISH; the handback names the log path and the completion line.
Everything else in §2 is measured.
