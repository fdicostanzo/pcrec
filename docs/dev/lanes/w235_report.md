# [DD-13b.W23.5] — fixtures, population, spec, and the acceptance pass (lane w235)

Branch `lane/w235`, from `lane/w234` tip `3b4fff45`. Step brief:
`docs/design/dd13_format/w23_impl.md` REVISION 1.1 §6.5; design of record
`format_design.md` 3.4.2. Two manager rulings (R-A, R-B) plus the step's own
build order. Two commits: `62ddb96d` (code/fixtures/spec), `5917200c`
(CLAUDE.md updates).

**STATUS: DELIVERED.** `make -j4 CC=gcc-16` clean; `make strict` clean;
`bash tests/rxtsource/run_rxtsource_tests.sh` **201 passed / 1 recorded / 0
failed** (was 191/0 at the branch point); `VALIDATE_ONLY=1` mech field
validation **256/256 valid** (including the new S248); S248 hand-verified
DETECTED on a scratch build (plant/rebuild/run/revert cycle, transcript in
§3 below). `make test`/`test-axes`/`san`/`lint`/`mech`'s real run remain
OWED to the next battery — the box constraint named in the brief held for
this lane's entire working period.

---

## 0. Rulings received

**R-A — the `pattern-esc` dump-value seam** (escalated by `w233_report.md`
§3.2 and `w234_report.md` §3): leg A's `--list-source` `pattern` column
keeps DECODED bytes; legs B and C (which cannot decode without a second copy
of the escape table) report the text AS WRITTEN. The three-leg VALUE
comparison for a `pattern-esc` row is therefore **A-vs-(B==C), EXCLUDED BY
DESIGN** — the third instance of the dup_head_description/include seam
shape. Consumed as: `pattern_esc_value_seam.rxtin` (a new fixture whose
`pattern-esc` block carries a real escape, `\n`, giving the seam a
population of one instead of zero) plus a check asserting B == C with the
exclusion of A stated in the check's own comment, plus a `docs/spec/
rxt_format.md` spec hunk (D80) stating the split normatively.

**R-B — the withdrawal-absence check's over-broad data arm** (escalated by
`w234_report.md` §2): the naive grep for `configs|testee|option|provides|
capable` cannot tell a withdrawn `config`-body DIRECTIVE from an `ext` BODY
LINE spelled the same word — `ext bench` / `testee pcre2/10.46` is
`format_design.md` §2.27's own worked example, not the withdrawn roster
returning. Consumed as: the data arm NARROWED structurally (an indent
stack tracking attachment under an `ext` opener — not a keyword list of
consumer namespaces), verified on a genuine top-level `testee` plant
(caught) and the aux-nested spelling (not caught), and `aux_identity
.rxtin`/`aux_identity_edited.rxtin` reverted from `w234_report.md`'s `ref`
workaround back to `testee` so the worked example's own spelling is
restored and exercises the narrowing.

Both rulings are recorded verbatim in the brief; nothing here reinterprets
them.

---

## 1. What is built

### 1.1 R-A

- `tests/rxtsource/fixtures/pattern_esc_value_seam.rxtin` — an ordinary
  `pattern` block first (see §2.1's finding on why), then
  `pattern-esc "a\nb"`.
- A check in `run_rxtsource_tests.sh`: leg A's dump reads `a\nb` (decoded:
  one literal byte, one real newline, one literal byte); legs B and C both
  read `"a\\nb"` (as-written, quotes and the doubled backslash both
  present). Asserts B == C; does not compare A against either.
- `docs/spec/rxt_format.md`'s `pattern-esc` production gains a new bullet
  stating the seam normatively: `--list-source` decodes, a harness reading
  the raw file (as both legs do, to avoid a second/third copy of the escape
  table) does not, and a third reader comparing the two would see the
  difference.

### 1.2 R-B

- `withdrawn_data_arm()` (a shell function in `run_rxtsource_tests.sh`): an
  AWK indent-stack walk over one file. A BLANK line or a column-1 `#`
  closes every open level (S0/S1's own rule); a dedent pops the stack to
  the matching level; a line is checked against the five withdrawn/reserved
  tokens **only when the stack is empty** (not inside an `ext` subtree);
  a line whose first token is `ext` pushes a new level. `freq` is
  deliberately NOT an opener — its body is the schema's DATA scope
  (declared rows: `question`/`reader`/`analyzer`/`row`/`provenance`), not
  TREE, so it is not an aux subtree.
- **DATA ARM**: runs `withdrawn_data_arm` over `git ls-files '*.rxt'
  '*.rxtin'`, requiring 0 hits.
- **SELF-CHECK**: two scratch files built inline (never the real corpus,
  which the arm above has already proven clean) — a top-level `testee`
  line (must be caught, 1 hit) and the same word nested under a real `ext`
  opener (must NOT be caught, 0 hits). Proves the narrowing is structural
  rather than a keyword list.
- **PARSER ARM**: greps each of the four readers' own live-keyword spelling
  — a quoted `PCREC_RXT_SCHEMA` kind in `src/parse/rxt_schema.def` (the ONE
  dispatch table since W23.1 retired `config_vocab`/`head_vocab`/
  `block_vocab`), a quoted string in `verify_rxt.py`, a `^`-anchored bash
  arm in `run.sh`, a quoted flag in `cli/main.c` — for each of the five
  withdrawn/reserved tokens. Requires 0 hits (measured 1 before the
  withdrawal, per `w23_impl.md` §4.3: `rxt_source.c:149`'s now-retired
  rows).
- **SPEC ARM** (§4.3(c)): deliberately NOT automated. `rxt_format.md:130`'s
  "configs are three artifacts…" is legitimate English no pattern
  separates from the withdrawn `configs describe`/`configs build`; stays a
  standing review step.
- `tests/rxtsource/fixtures/aux_identity.rxtin` and
  `aux_identity_edited.rxtin`: `ref` reverted to `testee`.
- `tests/mech/sabotages/S248_withdrawn_testee_returns.sh`: plants a
  `config testee` row back into `rxt_schema.def`. Confirms the PARSER ARM
  alone goes red (the DATA ARM and self-check are unaffected — three
  independent arms, three independent readings).

### 1.3 The rest of the build order

- `tests/rxtsource/fixtures/mc_illformed_utf8.rxtin` — `w23_impl.md`
  §3.2's own W23.3 row, never landed there (confirmed by grep: zero hits
  for "mc_illformed" or "illformed" anywhere in the tree before this
  commit). SW7's ill-formed-UTF-8 advance rule (`match_api.md` §3.1.1):
  `x?` (nullable) over three bare continuation bytes `\x80\x80\x80` under
  `-e utf8`. WITH the skip rule: an empty match at 0, one skip across all
  three continuation bytes, an empty match at 3 — count 2. WITHOUT it
  (naive `pos + 1` alone): count 4. Both `run.sh`'s C loop (the real
  `<prefix>_next_pos` residual) and `verify_rxt.py`'s independent python
  transcription report 2; both were confirmed to FAIL loudly against the
  naive 4 before landing (a deliberately wrong `mc ... 4` fixture, run,
  reverted).
- **W23-S5, the `all-readers` population check** (§3.3): walks
  `--list-schema`'s OWN output for every BLOCK-scope row reading
  `validated_by: all-readers` (today: `name`, `description`, `flags`,
  `encoding`, `engine`) and fails naming any row with no line in
  `$RECEIPTS`. The log is written by exactly two functions:
  `check_refusal_all3_kind KIND ...` (a thin wrapper around
  `check_refusal_all3` that appends a receipt after it runs — all thirteen
  existing call sites keep their positional needle arguments unchanged;
  five were renamed to the `_kind` form: `bad_flags`→flags, `bad_engine`→
  engine, `bad_name_ident`/`dup_block_name`→name,
  `bad_encoding_ident`→encoding, `dup_description`→description) and
  `check_accept_all3_kind KIND FIXTURE LABEL` (the accept-side sibling
  §3.3 names, built here for the first time —
  `block_kinds_accept.rxtin` carries `name`/`flags`/`encoding`/`engine`
  together; `description`'s receipt rides the pre-existing
  `single_description.rxtin` accept control). **A receipt is written only
  when all three legs actually ran and answered** — never a declared
  fixture name.
- **Item 2 of the build order (promote `pcrec` rows to `all-readers` where
  a fixture now exists): audited, NOTHING TO PROMOTE.** The five existing
  `all-readers` rows are exactly the kinds where legs B and C perform real
  VALIDATION (a closed vocabulary or identifier grammar each leg
  independently enforces), per the RECOGNISE-vs-VALIDATE split
  (`format_design.md` §2.14/§2.24). Every other `pcrec`-only kind is
  either structurally-shared machinery (the STRUCTURE-ATTACHMENT refusals
  `check_refusal_all3` already exercises for `aux_malformed_body`/
  `indent_pre_body`/`indent_under_m` are about S1's attachment stack, not
  about a specific kind's own schema constraint) or RECOGNISED-but-
  UNVALIDATED by design (`provenance`/`variant`/`ext`/`tag`/`oracle`/
  `budget`/etc. — legs B and C consume the body and pcrec alone validates
  it, per §2.24's own table). This is a finding stated rather than a
  silent skip; the two new fixtures built this step (`mc_illformed_utf8`,
  `block_kinds_accept`) do not change it — `mc`'s row is `validated_by:
  none` by design (`--list-source` performs no pattern/subject-text
  validation at all) and `block_kinds_accept` exercises kinds already at
  `all-readers`.
- **SW rows**: `w23_impl.md` §4.1's table lists no SW row for W23.5 beyond
  the §4.3 landing condition already discharged above. SW20/SW21, the two
  rows the design's own risk list (§7.1 item 2/§0.5) flagged as needing
  confirmation, were both already landed at W23.3a/W23.1 respectively
  (confirmed by grep — `SW20`'s "entry files"/"fragments spliced"/
  "RESOLUTION failure" text is in `rxt_format.md`; `SW21`'s diagnostic-
  class table is in `cli.md`). Nothing owed.

---

## 2. Findings

### 2.1 [NEW FINDING] leg C refuses a file whose FIRST block opens with `pattern-esc`

`verify_rxt.py:667`'s `first != 'pattern'` test (the gate that gives the
head-declaration words their own error before falling through to the
"unknown token" catch-all) has **no exemption for `pattern-esc`** — only
the literal token `pattern`. So a file whose first body-scope line is
`pattern-esc "..."` raises `[unknown-token-in-scope] 'pattern-esc' line
before any pattern block`, even though legs A and B both accept the
identical file (MEASURED live, both forms). This is S242's own finding
(`w234_report.md`'s account of `opener_pattern_esc_pair.rxtin`'s first
line, "the FIRST `pattern-esc` line in a file has no other route into
BLOCK scope at all") recurring **one leg over** — S242 is about leg A's
schema dispatch, this is about leg C's separate, hand-written gate — and
it means `opener_pattern_esc_pair.rxtin` (leg-A-only, S242's own fixture)
has never actually been reachable by a three-leg comparison at all, in
either direction. Not fixed here (out of this step's brief — it is a
`verify_rxt.py` code change, and this step's charter is fixtures/
population/spec); `pattern_esc_value_seam.rxtin` works around it by
ordering (a `pattern` block first).

### 2.2 [NEW FINDING] `--source`/`--target`'s config resolution silently prefers the FILE's `engine` over an explicit CLI `--engine=` flag

Found during the bench-acceptance dry run (§4, check F2). `cli/main.c:890-
891`:

```c
if (t->engine) {
    if (!strcmp(t->engine, "vm")) ts.opt.engine = PCREC_ENGINE_VM;
```

runs unconditionally whenever the resolved target's config declares
`engine vm`, with no check of whether `ts.opt.engine` was already set by
an explicit `--engine=` CLI flag. MEASURED: a target built from a `config`
declaring `engine vm`, compiled with `pcrec --source F --target T
--engine=dfa`, stamps `.engine = 2 /* PCREC_ENGINE_VM */` — the CLI's own
explicit request is silently overwritten, no diagnostic either way. This
is exactly the shape bench check F2 asks about ("the command line wins,
or the file is refused — **either is acceptable, silence is not**") and
is a genuine gap: nothing in this tree's spec or design documents states
which side should win, and the code's answer is neither documented nor
symmetric (a CLI `--engine=dfa` against a file's `engine vm` is silently
overridden; the reverse was not tested but the code path is
one-directional by construction). Not fixed here — a real behavior change
belongs to a ruling and a `cli/main.c` edit, both outside a fixtures/spec
step's charter. Flagged for the manager's queue.

---

## 3. The bench acceptance dry run (§5, §6.5 build item 4)

Scoped to the RUNNABLE subset per the brief: groups A, B, C, D, F1/F2, G,
using a scratch fixture directory
(`$SCRATCHPAD/dryrun/F`, not committed — session-temporary per the scope
mandate) and the delivered `build/pcrec` binary. Three populations, never
one number:

| check | verdict | note |
|---|---|---|
| A1 | **RUNNABLE, RED (ALREADY-KNOWN CAUSE)** | `include` at block scope refuses (`[structure-attachment] 'include' is a file-level declaration...`) — exactly `w23_impl.md` §5's own A1 finding, reproduced live. The corrected form (include at head only) is exit 0 |
| A2 | **RUNNABLE, RED (ALREADY-KNOWN CAUSE)** | `config … testee`/`option` refuse (`[unknown-token-in-scope] 'testee' is not a config-block directive`) — exactly §5's own A2 finding (D99 withdrawal) |
| A3 | RUNNABLE, GREEN | unknown keyword names its context |
| A4 | RUNNABLE, GREEN | `tag` inside a `config` body refuses naming the context |
| A5 | RUNNABLE, GREEN | `tag` accumulates, bare label + `key=value` both present |
| B1/B2 | RUNNABLE, GREEN | high-byte/tab/CR round-trip (rc 0; byte-exactness already covered by the shipped `ctrl_bytes.rxtin`/sem1 corpus check, M3/M4) |
| B3/B4 | RUNNABLE, GREEN | NUL refused by name / NUL-free file accepted — ALREADY LANDED per §5's own mapping |
| B5 | **RUNNABLE, PARTIAL (ALREADY-KNOWN CAUSE)** | `pattern-esc "a\nb\x00c\r"` refuses on the `\x00` (K9); the newline/CR-only twin round-trips — exactly §5's own B5 finding |
| B6 | RUNNABLE, GREEN (PREMISE DISSOLVED) | `pattern-esc "a"` then `pattern b` in "one block" is TWO blocks, not a refusal — exactly §5's own B6 finding |
| B7 | **RUNNABLE, GREEN — FIRST LIVE VERIFICATION** | `@file:` on a 3-byte `\x00\xff\x41` file reaches the matcher whole (`.* ` matches (0,3)) — §5 named this owed since revision 1; discharged here |
| C1-C10 | RUNNABLE, GREEN | vocabulary refusal+control, provenance required/conditional fields+control, second-provenance refusal, sha256 mismatch (via `run.sh`, leg A does not validate it)/match, second-description refusal (C10, changed by design — M5) |
| D1 | RUNNABLE, GREEN | tag/provenance/oracle/variant/mc/under/`@file:` id+hash all appear in the dump (combined with C8/C9's evidence for the `@file:` half) |
| D2 | NOT-RUN-HERE | requires code review of pcrec-bench's own loader, a sibling repo not present |
| D3 | RUNNABLE, GREEN | tab-in-pattern round-trips |
| D4 | RUNNABLE, GREEN | the VALIDATES-vs-RECOGNISES sentence exists in `rxt_format.md` |
| D5 | RUNNABLE, GREEN (by reasoning) | sections are additive-only; existing corpus files' main-table columns are unchanged (already confirmed by the corpus-census re-run across every W23 step) |
| E1-E7 | NOT-RUN-HERE | require `pcrecbench`/`make check-harness`, not present in this checkout |
| F1 | RUNNABLE, GREEN | a target-less, config-less file parses (rc 0); the spec sentence exists (W1.2's own addition) |
| F2 | **RUNNABLE, RED — NEW FINDING** | see §2.2 above: the CLI's `--engine=dfa` is silently overridden by the file's own `engine vm`, with no diagnostic either way |
| F3/F4 | NOT-RUN-HERE | pcrec-bench's own gate/review, not applicable to this repo |
| G1 | NOT-RUN-HERE (box constraint) | `make test` forbidden this session; `bash tests/rxtsource/run_rxtsource_tests.sh` (201/0) is the allowed proxy and is part of, not the whole of, `make test` |
| G2 | NOT-RUN-HERE | `make check-harness`'s `check_rxt_export`, pcrec-bench's own tool |
| G3 | PARTIAL (qualitative) | M1 (NUL refusal) confirmed already-true; M10 (W2/W3 keywords) confirmed changed by design, WITH the A1/A2 caveats above; M5 (C10) confirmed changed by design. The bench's own probe script (`docs/dev/measurements/probe_rxt_format.py`) is not in this repo, so the literal re-run is NOT-RUN-HERE |

**Summary: 25 of 41 runnable here (matches the brief's own ~25/41
estimate); 20 green, 3 red-with-already-documented-cause (A1, A2, B5 —
each traced to §5's own prior finding), 1 red-and-new (F2), 1 partial
(B6, premise-dissolved rather than red or green); 16 not-runnable
(missing tool or sibling repo: D2, E1-E7, F3, F4, G2; box-constrained:
G1; qualitative-only: G3).**

**THE CORRECTION LIST IS `format_design.md` §9's, BY REFERENCE** — per
`w23_impl.md` §5's own standing lesson, this note does NOT re-derive it.
Nothing in this dry run changes that list; F2's finding is NEW (not in
§9) and is added to the manager's queue below rather than folded into the
bench's own correction list, since it is a pcrec behavior gap, not a
bench-fixture correction.

---

## 4. Consolidated merge-time correction list for `w23_impl.md`

Gathered from all five step reports (w231, w232, w233, w233a, w234) plus
this one, per §6.5's own instruction — cited, never edited by any lane
(w232's own precedent).

1. **From `w232_report.md` §3.2`** (W23.2): §3.2's fixture table says
   `indent_under_m.rxtin`'s class is `schema-constraint`. The delivered
   code answers `structure-attachment` on all three legs (measured; legs
   B/C were matched to leg A's own S1 behavior per W23.2's own
   must-not-touch boundary — `rxt_source.c`'s S1 block files every
   "indented line continues nothing" refusal under `RXTD_STRUCTURE`
   regardless of whether there is no parent at all or the parent's
   `children` column reads NONE, three call sites `rxt_source.c:1169`,
   `:1173`, `:1184`). Correct `indent_under_m.rxtin`'s row to
   `structure-attachment`.
2. **From `w233a_report.md` §0/§2`** (W23.3a): §1.10.2's table lists "legs
   B and C" together for rules 2 (REPORT), 4 (SPLICE) and 5 (CLOSURE
   TALLY). MEASURED: leg C structurally cannot splice `include` at all
   (it is head-scoped by design, and the seam ruling's head-bearing
   refusal already raises before any body line is reached, in both plain
   and `--dump` mode). Correct those three cells to read "leg B; leg C's
   half is discovery subtraction only" — and correct §3.1's W23-S7 row
   and §6.3a's acceptance line ("the three legs' block counts are equal")
   to state the splice half is a TWO-leg (A/B) comparison, never
   `check_refusal_all3`'s three-way shape.
3. **No correction found from `w233_report.md` or `w234_report.md`**
   against `w23_impl.md` itself (both reports' own §3 items are
   disagreements with `format_design.md`, already the design note's own
   territory, or dispositions of open items between lane reports — not
   citations against `w23_impl.md`'s text).
4. **This step (w235) found no `w23_impl.md` text errors** — §2's two
   findings above (the leg-C pattern-esc gate, the CLI/config engine
   precedence gap) are gaps in the CODE and in `cli/main.c`'s behavior
   respectively, not in the design note's prose.

---

## 5. What a fresh agent needs to know

- **`check_refusal_all3`'s positional signature is UNCHANGED.** A receipt
  is opted into by calling `check_refusal_all3_kind KIND fixture label
  class [needle...]` instead — the kind is a NEW leading argument this
  wrapper strips before delegating, so no existing needle-argument
  position moved.
- **`$RECEIPTS` is a plain text log, `$WORKDIR/all3_receipts.txt`,
  written only by `check_refusal_all3_kind` and `check_accept_all3_kind`.**
  A future kind reaching `all-readers` needs a call through one of these
  two, not a manual `record_receipt` at a bespoke call site — the whole
  point is that the receipt is inseparable from the code path that does
  the three-leg work.
- **`withdrawn_data_arm()` is reusable** for any future narrowing question
  shaped like "is this line inside an `ext` subtree" — it is a general
  indent-stack walk, not a one-off.
- **§2.1's leg-C gap is real and affects `opener_pattern_esc_pair.rxtin`
  (S242) too** — anyone building a new pattern-esc-as-first-block fixture
  needs a leading ordinary `pattern` block, or will hit the same gate.
- **§2.2's engine-precedence gap needs a ruling before a fix** — the two
  candidate answers (CLI wins; refuse when both are set) are both
  reasonable and neither is documented anywhere today.
- Full battery (`make test`/`test-axes`/`san`/`lint`/`mech`'s real run) is
  OWED to the merging session, per the box constraint named in the
  brief. The mech matrix's field validation (256/256) and S248's
  hand-verified DETECTED transcript are the allowed substitute.
