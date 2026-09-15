# [DD-13b.W23.4] — `--list-source`'s four `#section` blocks (lane w234)

Branch `lane/w234`, from `lane/w233a` tip `b9a49d35`. Step brief:
`docs/design/dd13_format/w23_impl.md` REVISION 1.1 §6.4; design of record
`format_design.md` 3.4.2 §2.24. Five commits: `b68a399a` (WIP: the
accumulation mechanism), `c691a5fb` (the four sections + R5/R6 repair),
`1809d305` (S242/S243/S246 + W23-S6), `ebbe671c` (spec hunks + CLAUDE.md).

**STATUS: DELIVERED.** `make -j4`/`make strict` clean;
`bash tests/rxtsource/run_rxtsource_tests.sh` **191 passed / 1 recorded /
0 failed** (up from 184 at the branch point); census **210/3936/28943
unchanged**. No `abi` event (`git diff --stat b9a49d35..HEAD -- src/gen
src/ir src/opt lib` empty). `make test`/`test-axes`/`san`/`lint`/`mech`
remain OWED to the next battery — the box constraint named in the brief
held for this lane's entire working period.

---

## 1. What is built

### 1.1 Leg A accumulates what W23.3 only validated

W23.3's leg A recognised `provenance`/`variant`/`ext`/the eight CASE
kinds and deliberately stored nothing beyond validation (§2.2's own step
boundary: "W23.3 touches no dump SHAPE"). Four new record types on
`RxtSource` (`src/core/internal.h`): `RxtProv`, `RxtVariant`, `RxtCase`,
`RxtAux` — one growable array each, in FILE ORDER, populated during the
same generic parse walk W23.1-W23.3 built:

- **PROVENANCE/VARIANT: captured at FRAME CLOSE**, inside the existing
  `RXT_CLOSE_FRAME` macro right after `frame_constraints` passes, so a
  record missing a `required` field never reaches the push. `RxtFrame`
  gained `open_line`/`open_value` — the sub-block's own opener line and
  scalar (a `provenance` line's own `line`; a `variant <testee>`'s `line`
  AND `testee`) — refreshed on every dispatched row via two new loop
  locals so a following indented line always captures its TRUE opener's
  facts. `frame_field()` reuses `cond_holds`'s own (scope, kind-name)
  lookup shape rather than inventing a second one.
- **AUX: captured PER LINE**, not at frame close — `#section aux`'s own
  normative "row order is source order" falls out for free from pushing
  one row as each line is read. The opener row (depth 0) is pushed
  unconditionally at the `ext`/`freq` dispatch arm (both FILE and BLOCK
  scope), even for an empty body — "the opener line IS the block's
  identity" has no other way to hold when nothing is ever indented under
  it. `RxtFrame` gained `depth`/`consumer` (tree-frame-only, inherited
  unchanged parent-to-child) and reuses `open_line` as the level's own
  `parent_line` (documented as "never both apply to the same frame" with
  provenance/variant's use of the same field).
- **CASE LINES: `parse_case_body`, deliberately NOT a second validator.**
  Every CASE-kind row is `validated_by: none`, and §2.2's step boundary
  reads "W23.4 adds no production and no refusal" — so the parser is a
  best-effort STRUCTURAL split of the documented grammar: a shape it
  does not recognise leaves the corresponding field NULL rather than
  raising anything. `is_case_kind` gates an `under` line's wrapped tail
  so a malformed wrapped kind cannot be misparsed into a real kind's
  fields.

### 1.2 The dump: three appended columns, four new head-row kinds, four sections

`rxt_columns[]` grows to 19 (`tags`, `oracle`, `esc` appended, position
1-16 unchanged); `RxtDeclKind` gains `RXT_DECL_VOCABULARY`/`ORACLE`/`TAG`/
`USE` (`vocabulary`/`oracle`/`tag`/`use` now push their own head row,
`lib`'s own one-row-per-line convention — they used to be recognised,
value-checked and dropped). `pcrec_rxt_source_tsv` emits the four
`#section` blocks (`provenance`/`variants`/`cases`/`aux`) unconditionally
when non-empty, always after the main table, matching
`schema_dump.c`'s own wire-format shape.

### 1.3 The format-reader survey, re-run, and R5/R6 repaired

Re-ran the survey (§6.4 item 1); its own table (§1.5) held for R1-R4/R7-R9
but **R5 and R6 were, as predicted, exactly the `NF != 15`-shaped defect**
— both read every non-`#` row of the stream as main-table, which every
`#section` data row violates. Both repaired to be SECTION-AWARE: they
track the stream's own `#section NAME`/`#kind` boundaries and use the
matching section's own expected width, hard-failing on an unrecognised
section name (never defaulting). The MANIFEST re-pinned to 19 columns;
its own lookup fixed from `tail -1` over every `#` line (which now reads
a SECTION's header on any section-bearing file) to `grep '^#kind'`
specifically. **The synthetic-stream control** (item 3b, a hand-written
stream, never real `pcrec` output) exercises both repaired arms at a
section width that differs from 16 (`#section cases` is also 16 — the
design's own reason to pick `aux`, width 8).

**W23-S4** built: no `#section` row's field 1 equals a main-table `kind`
token, and sections follow the main table — asserted on
`aux_deep_tree.rxtin`, whose whole point (colliding keys) makes it the
sharpest possible witness.

### 1.4 Six pre-existing checks made section-aware

Any fixture whose block carries a real case line now legitimately grows
a `#section cases` block, and six checks that read "every non-`#` row"
as if it were the main table needed the same repair R5/R6 got:
`sem10`'s `be_kinds`, `w23s1/ws-positions`'s twin-file diff (which also
had to blank section rows' own `line`/`block_line`, not just the main
table's `line`), `head/head_basic`'s row-order check, `W23-S3 arm 1`'s
opener probe, and `aux/deep-tree`/`aux/subtree-extent`'s "exactly N
rows" assertions — the last two were **obsolete by design, not merely
stale**: W23.3 asserted a total row count of 1 (or 2) because aux
content was structurally invisible; W23.4's whole point is making it
visible, so a nonzero `#section aux` count is now correct and the
absence claim narrows to the surfaces that must still show nothing.
**Every one of these was reproduced as a genuine regression against a
scratch build of the branch point (`b9a49d35`, 184/0/0) before being
attributed to this change** (BOILERPLATE's own rule) — a `git worktree
add` at the branch point, rebuilt, and diffed against my own tree's
result.

`aux_literal_pipe`'s central assertion, owed since W23.3
(`w233_report.md` §3.2: "the VALUE half is W23.4's"), is now built: the
`separator |` row's value is the single byte `|`, and `terminator`/`note`
below it share its `parent_line` as SIBLINGS.

### 1.5 S242, S243, S246, W23-S6

Two new fixture pairs (`opener_pattern_esc_pair`/`opener_m_not_opener`,
`aux_identity`/`aux_identity_edited`) and their checks.

- **S242** (S-R4a, `pattern-esc` loses `opens_group`): MEASURED a
  stronger symptom than the design predicts — a file whose FIRST block
  opens with `pattern-esc` refuses outright
  (`[unknown-token-in-scope]`), because the root frame's `f->base` only
  ever reaches BLOCK scope through the opener transition. The design's
  own "block_line drift on a second pattern-esc line" is real but this
  fixture's first line already fails before that shape is reached.
- **S243** (S-R4b, `m` gains `opens_group`): `pcrec_rxt_schema_opener` is
  scope-FREE and the root frame's `.base` stays `RXT_SCOPE_FILE` for its
  whole lifetime, so every `m` line ANYWHERE in the file — not only ones
  at file scope — starts closing/reopening blocks. `opener_m_not_opener
  .rxtin` (1 block, 2 cases) becomes 3 blocks / 0 cases under the plant;
  the same mechanism produced 15,513 spurious block rows on the full
  corpus during hand-verification.
- **S246**, two variants: (a) `ext`'s BLOCK-scope row loses
  `cardinality: repeat` — **the first draft targeted the FILE-scope row
  and the hand-verify caught it UNDETECTED**, since `aux_identity_edited
  .rxtin`'s two `ext` blocks are both block-scoped; fixed to the correct
  row. (b) `section_count()` — the SHARED helper every W23.4 fixture
  check routes through, not the corpus-only `a_blocks` snippet the
  design's own prose names (the corpus's zero-`ext` population could
  never arm that target) — is corrupted to fold an aux tree's own
  `ext`-opener rows into the main-table count, reachable through
  `aux_deep_tree.rxtin`'s own opener with no dedicated fixture.
- **W23-S6** (format_design §2.27.3 clause 5): edit `aux_identity`'s
  body (line count, depth, key spellings, block count all move at once)
  and require every pcrec output except `#section aux`'s rows to stay
  byte-identical. Two arms built: `--list-source` with the section
  elided, and the compiled artifact (`.c` AND `.h`, via `--source`'s
  implicit-single-unnamed-block default). **The design's third arm
  ("every diagnostic") is deliberately NOT built as a separate fixture
  pair** — `--list-source` performs no pattern-text validation at all
  (`validated_by: none` on every `pattern`/`pattern-esc` row), so a
  `pattern a(` fixture is silently ACCEPTED rather than refused, and a
  genuine format-level refusal (a malformed `provenance` field) would
  introduce unrelated content into the comparison. The diagnostic arm is
  discharged for free instead by S246 variant (a)'s own detection
  (`aux_identity_edited.rxt` starts refusing where it used to accept) —
  recorded as a deliberate narrowing, not an omission.

All six rows: FIELDS OK (`VALIDATE_ONLY=1`) and hand-verified DETECTED on
scratch builds — S200/S201/S202/S203 re-confirmed still-detected under
the repaired R5/R6 (their SAB_DESC stale counts re-derived: 19/19,
18/19, 210, replacing 15/16/14/15/179), S242/S243/S246 verified new
(S246's two variants separately and together). Highest id on `main` at
numbering time: S238; this branch's own history additionally carried
S240/S241/S244/S245/S247 from unmerged W23 lanes — S242/S243/S246 collide
with none of them. Real `make mech` `DETECTED` rides the next battery.

### 1.6 Spec hunks and CLAUDE.md

`docs/spec/rxt_format.md`: the column table gains `tags`/`oracle`/`esc`
and the four new head-row kinds; the four `#section` blocks documented
(columns, ordering, the field-1 invariant); the "W23 productions parse
and are not reported" and "Sectionless" paragraphs — both made FALSE by
this delivery — corrected in place; the `ext` production's own section
points at `#section aux` as the literal discharge of "dumps it
faithfully". `docs/spec/cli.md`'s `--list-source` entry names 19 columns
and the four sections. `docs/spec/table_contract.md`'s Scope row updated
and a new paragraph records `--list-source` as the mechanism's second
producer and the first whose main table stays anonymous while gaining
named sections after it. `src/parse/CLAUDE.md`, `tests/rxtsource/
CLAUDE.md`, `tests/mech/CLAUDE.md` carry the mechanism, the `section_
count()` helper, the six section-aware fixes, and S242/S243/S246's own
record including both corrections the hand-verify caught.

---

## 2. A finding: the withdrawal-absence check's data arm is over-broad

§8 item 6 asks every step to re-verify the withdrawals' absence check
(§4.3's three arms). Both re-verified clean at this pin (0 hits each) —
but only after a real trip. My first-draft `aux_identity` fixtures used
`ext bench` / `testee pcre2/10.46`, **`format_design.md` §2.27's own
worked example's exact spelling**, and the data arm's grep
(`^[[:space:]]*(configs|testee|option|provides|capable)([[:space:]]|$)`)
flagged both files: it cannot distinguish a withdrawn `config`-body
DIRECTIVE from an `ext` BODY line using the same word, because it has no
notion of the OPEN SUBTREE (S2's opener set is empty there; the
unknown-token rule is vacuous). `testee` as an aux key is not a hazard —
it is the format's own example — so this is the check being wrong, not
the fixture. Fixed by renaming the fixtures' aux key to `ref` rather than
narrowing the check itself, since that is a design question (should the
absence check exclude open-subtree lines structurally?) outside this
step's brief. Flagged here rather than silently worked around; the
population will only grow as `ext` sees real use.

## 3. The OPEN ITEM from `w233_report.md` §3.2 — dispositioned, not resolved

w233's own report named an open item: legs B and C cannot agree with leg
A on a `pattern-esc` row's dump VALUE (A reports decoded bytes; B and C
report as-written; B==C; population zero), asking this step to resolve
it or disposition it explicitly. **DISPOSITIONED, NOT RESOLVED.** The
`esc` column this step adds (§1.2 above) answers a DIFFERENT question —
which spelling wrote a block — and does not touch what legs B/C's own
`pattern` column CONTAINS for a `pattern-esc` block, which is still
as-written text rather than leg A's decoded bytes. Making legs B/C
decode would mean teaching bash and python a second implementation of
`pcrec_rxt_decode_escaped`'s table (`tests/harness/run.sh` already
avoids exactly that duplication for the reason its own CLAUDE.md states:
"leg B passes the still-encoded text through with `pcrec --pattern-esc`
and decodes nothing in bash"), which is a real design decision this step
did not make unilaterally. Population is ZERO (no corpus file uses
`pattern-esc`), so nothing observable changes either way at this pin.
Escalating to the manager rather than guessing: should legs B/C's
`pattern` column report AS-WRITTEN (today's behaviour, and arguably the
more honest "each leg's own view") or should leg A's dump column be
demoted to AS-WRITTEN too (giving up the byte-exact-round-trip property
§2.24 currently claims for it)? Either answer is a one-line change once
ruled; this step made neither, to avoid pre-empting a ruling on a
zero-population question.

---

## 4. What a fresh agent needs to know

- **`section_count SECTION FILE`** (`tests/rxtsource/run_rxtsource_tests
  .sh`, defined beside `pass`/`fail`) is the ONE shared helper every
  W23.4 fixture check routes through. Route any new section-aware count
  through it rather than growing a sixth hand-rolled copy.
- **`parse_case_body` never calls `rxt_fail`.** If a future step wants
  case-line VALIDATION (raising the schema row's `validated_by` above
  `none`), that is a real semantic change belonging to its own step, not
  a silent addition here.
- **The MANIFEST's own lookup is `grep '^#kind'`, not `tail -1` over
  every `#` line** — the second form reads a SECTION's header the moment
  any file in the corpus grows one.
- **`RxtFrame.open_line`/`open_value` serve TWO purposes** (provenance/
  variant's own opener facts; a tree frame's own `parent_line`) and the
  header comment states why they never collide. A third use would need a
  third field, not a third meaning layered onto these two.
- Full battery (`make test`/`test-axes`/`san`/`lint`/`mech`) is OWED to
  the merging session, per the box constraint named in the brief.
