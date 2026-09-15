# [DD-13b.W23.2] — legs B and C, and the STEP 0 parity fix (lane w232)

Branch `lane/w232`, from `fcfdd944`. Step brief: `docs/design/dd13_format/
w23_impl.md` REVISION 1.1 §6.2; design of record `format_design.md`
3.4.2. Commit: `6e952586`.

All seven build-order items land: `record_fail_class`/`_fail` (the
diagnostic class tag in both legs, at every per-line refusal site — not
only the sites this step's own fixtures exercise), the attachment arm
(S1), the STEP 0 parity fix (`nul_byte`/`dup_description` move to
`check_refusal_all3`), the two attachment fixtures plus
`nul_in_comment.rxtin`, S239, and the arm-hash re-pin.

## 1. What landed

| # | build order item | landed as |
|---|---|---|
| 1 | rewrite `check_refusal_all3` to compare CLASS; give its seven existing call sites their classes | `tests/rxtsource/run_rxtsource_tests.sh`'s `extract_class` + rewritten `check_refusal_all3`; `bad_flags`/`bad_engine`/`desc_pipe_trailing_space`/`directive_before_pattern`/`bad_name_ident`/`bad_encoding_ident`/`dup_block_name` all carry a class argument now |
| 2 | the diagnostic CLASS tag in both legs, at the rule that fired | `record_fail_class` (run.sh), `_fail` (verify_rxt.py) — every per-line refusal in both legs, including each catch-all |
| 3 | the STEP 0 parity fix | `nul_byte`/`dup_description` → `check_refusal_all3`; `tests/rxtsource/CLAUDE.md`'s scope note narrowed |
| 4 | the ATTACHMENT arm | the new indent-dispatch block ahead of first-token dispatch in both legs (S1, format_design §1.2.1) |
| 5 | child consumption, mechanism only | built generically; no live population at this pin (see §5 below) |
| 6 | W23-S1, W23-S2; S-R1 (S239); the three fixtures | `check_refusal_all3`'s rewrite IS W23-S2; `indent_pre_body.rxtin`, `indent_under_m.rxtin`, `nul_in_comment.rxtin`; `tests/mech/sabotages/S239_m_children_config.sh` |
| 7 | the SW rows this step makes true | none — see §4 |

## 2. Acceptance, MEASURED

| acceptance | measured |
|---|---|
| C1 three-way census, byte-identical trees, unmoved | **210 / 3,936 / 28,943**, the suite's own summary line, unmoved |
| C2 (run.sh's own population) | **209 / 3,933 / 28,932**, reconciled against the census minus `known_fail`'s 1/3/11 |
| W23-S2 green on every refusal fixture in §3.2 that exists at this pin | all green — see the full pass list below |
| `indent_pre_body.rxtin` refuses in all three legs at the PRE-BODY position | class **structure-attachment**, all three |
| `check_refusal_all3` compares CLASS at all seven existing call sites and every new one | **12 sites total** (7 existing + `nul_byte`, `dup_description`, `indent_pre_body`, `indent_under_m`, `nul_in_comment`), no call site left on a verdict-only signature |
| `nul_byte.rxtin`/`dup_description.rxtin` move to `check_refusal_all3` and pass; `dup_head_description.rxtin` does NOT move | confirmed — see §3.2 |
| `tests/rxtsource/CLAUDE.md`'s leg-A-only scope section narrowed in the same commit | done — the NUL and duplicate-description halves close, the head-description half stays with the seam-ruling reason |
| `nul_in_comment.rxtin` refuses in all three legs | class **value-shape**, all three |
| S239 turns a class comparison red and leg A's own verdict green | see §3.3 — the exact shape moved, argued below |
| `make strict` clean; `bash tests/rxtsource/run_rxtsource_tests.sh` green | **160 passed / 0 failed / 1 recorded** (the pre-existing box-sensitivity RECORD, not gating) |

`make -j4 CC=gcc-16` also clean. `make test` is **OWED to the manager**,
per the box constraint (a battery is in flight; this lane's own
validation set explicitly excludes it).

## 3. Findings, ruled and recorded

### 3.1 The reserved-`version` class question (ruled, accepted)

**Decision: keep `[unknown-token-in-scope]`.** `format_design.md`
§2.25.5's own class definition reads: *"the kind has no schema row in
this scope, **or has one whose wave is above this build's**."*
`PCREC_RXT_WAVE_RESERVED` (999, `src/core/internal.h:4418`) is the
maximal instance of that exact test — permanently above, not merely
not-yet — and `refuse_wave`'s own gating condition at both call sites
(`rxt_source.c:1211`, `:1253`) is literally `row->wave >
PCREC_RXT_WAVE_BUILT`, which RESERVED satisfies by construction, same
as any ordinary future-wave row. The class captures this correctly as
written; no fifth class, no `docs/spec/cli.md` hunk. Ruled and accepted
by the manager mid-flight.

### 3.2 `indent_under_m.rxtin`'s class: structure-attachment, not schema-constraint (ruled, accepted — note correction owed to manager)

**MEASURED against the shipped W23.1 binary**, before writing any
leg-B/C code: `src/parse/rxt_source.c`'s S1 attachment block files
EVERY *"indented line continues nothing"* refusal under `RXTD_STRUCTURE`
(class `structure-attachment`), regardless of WHY there is nowhere to
attach — no parent open at all (`:1173`), or a parent whose `children`
column reads NONE (`:1169`), or the post-attachment indent-mismatch arm
(`:1184`). `w23_impl.md` §3.2's fixture table says `indent_under_m`
should be `schema-constraint`; the delivered code disagrees with its
own design note.

Per this step's own boundary (*"must not touch: `rxt_source.c`'s
grammar. If the step finds itself there, the boundary is wrong"*), legs
B and C are made to **match leg A** rather than the note — both now read
`structure-attachment` for an indented line under a childless kind,
verified three ways:

```
leg A: pcrec: [structure-attachment] ...: indented line continues nothing ('m' takes no continuation)
leg B: ...: [structure-attachment] indented line continues nothing ('m' takes no continuation, declared on line N)
leg C: ValueError: [structure-attachment] ...: indented line continues nothing ('m' takes no continuation, declared on line N)
```

The discrepancy is recorded in `indent_under_m.rxtin`'s own header, in
`tests/rxtsource/CLAUDE.md`'s new W23.2 section, and here. **Per the
manager's ruling this note does NOT edit `w23_impl.md` itself** — the
manager applies the one-line correction at merge (the w231
ratified-corrections-ride-the-merge precedent). The three citations for
that edit: `rxt_source.c:1169`, `:1173`, `:1184`.

### 3.3 S239's detector, restated against the corrected class

The build-order item's own wording (*"S239 turns C1 red and leg A alone
green"*) predates this lane's §3.2 finding. What actually happens under
the plant (`rxt_schema.def`'s block `m` row, `children: none →
config`), measured on a scratch build and reverted:

```
leg A (sabotaged): pcrec: [unknown-token-in-scope] ...: 'n' is not a config-block directive
leg B (unchanged):      ...: [structure-attachment] indented line continues nothing ('m' takes no continuation, ...)
leg C (unchanged): ValueError: [structure-attachment] ...
```

Leg A's own VERDICT is unchanged (still refuses — the *"leg A alone
green"* half, read as "leg A's own behaviour still looks fine in
isolation"), and its CLASS moved from `structure-attachment` to
`unknown-token-in-scope`. That is exactly the shape *"a row that only
proves 'something went red' does not prove it went red for its
reason"* is about: a verdict-only comparison (including the corpus-wide
C1 byte-identical-tree differential, which does not reach the fixtures
directory at all) sees nothing; `check_refusal_all3`'s own class
comparison on `indent-under-m` is the ONE instrument that does — leg
A's own needle check (`[structure-attachment]`, folded into
`check_refusal`'s needle list) fails under the plant. Field-validated
(`VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S239` →
`FIELDS OK`); the real DETECTED run through the matrix is owed (outside
this lane's allowed validation set — `make mech` is a heavy suite and a
battery is in flight on this box).

### 3.4 A regression found and fixed inside this lane

`parse_rxt`'s refactor to byte-mode reading (needed for the whole-file
NUL pre-scan) first used `str.splitlines()`, which treats VT (0x0b),
FF (0x0c) and several other Unicode line-break characters as
separators, not only `\n`. `ctrl_bytes.rxtin` (sem1, the r46 panel's
own BLOCKER control) carries a literal VT and FF inside its `pattern`
line, and `.splitlines()` silently re-chopped that one line into three
— leg C started refusing a file it must accept. Caught by this lane's
own full `run_rxtsource_tests.sh` run before landing (159/1/1 →
160/0/1 after the fix), not by a panel. Fixed to `.split('\n')`,
matching the original `readlines()` behaviour exactly.

## 4. SW rows / spec hunks: NONE, explicitly

**No `docs/spec/` hunk lands in this commit.** SW21
(`docs/spec/cli.md`'s "The diagnostic CLASS tag" section, four-row
table) already covers pcrec's own `.rxt`-source diagnostics as of
W23.1 — the class tag's position and closed set are stated there as
the CLI's output contract. Legs B and C (`tests/harness/run.sh`,
`tests/harness/verify_rxt.py`) are test-harness internals: nothing a
caller of `pcrec` itself observes moved. Stated explicitly per the
manager's ruling that "no hunk" and "forgot the hunk" must never look
identical in a diff.

## 5. What this step deliberately did NOT do

- **No live "child consumption" population is exercised.** At this pin
  no BLOCK-scope schema row admits children (`provenance`/`variant`/`ext`
  arrive at W23.3), so the attachment arm's else-branch — "the parent's
  `children` column names a real scope" — has no corpus or fixture to
  drive it yet. The mechanism (computing the parent's kind and line,
  ready for a future scope-aware dispatch) is in place; W23.3 is where
  it gets a customer.
- **`block_scalar_in_body.rxtin` stays leg-A-only.** The authoritative
  build order (`w23_impl.md` §3.2's own table) assigns it to W23.1 and
  does not list it for W23.2's acceptance; a `w231_report.md` passage
  suggesting otherwise is imprecise relative to the actual fixture
  table this lane built against.
- **The `Must not touch` boundary held**: `git diff --stat` against the
  merge base touches only `tests/harness/{run.sh,verify_rxt.py}`,
  `tests/rxtsource/{CLAUDE.md,run_rxtsource_tests.sh,fixtures/*}`,
  `tests/mech/sabotages/S239_*.sh`. Zero files under `src/`.
- **S239's real DETECTED run through `make mech`** — field-validated
  only, per the box constraint. Owed to the manager.
- **`make test`** — owed to the manager (this lane's validation set
  deliberately excludes it; a battery is in flight on this box).

## 6. What a fresh agent needs to know

- The attachment mechanism is entirely in `tests/harness/run.sh` (the
  new block right after the two blank/comment `continue`s, before the
  `BEGIN PINNED ARM REGION` marker — outside the pin by construction)
  and `tests/harness/verify_rxt.py`'s `parse_rxt` (the block right
  before the `if not seen_pattern:` check — it must run FIRST, or an
  indented pre-body line reaches the wrong branch and gets the wrong
  class, which is exactly the ordering defect `indent_pre_body.rxtin`
  exists to pin).
- `extract_class` (`run_rxtsource_tests.sh`) reads the LAST bracketed
  `[a-z-]+` tag in a leg's output, not the first — load-bearing because
  leg C's `--dump` path has no top-level try/except (pre-existing) and
  a refusal there is a full python traceback; the class tag is on its
  own final line.
- The ARM_PIN hash (`run_rxtsource_tests.sh:1120`) is
  `b5a00e6142d024f2978bce13bd8debd9733818df3ab4023ce7e4075d62036356`,
  recomputed from the committed `run.sh`; any further edit inside the
  `BEGIN`/`END PINNED ARM REGION` markers must re-pin it in the same
  commit.
- W23.3's productions (`ext`, `provenance`, `variant`) are the first
  real customers of the attachment arm's child-consumption branch; that
  step's own brief should re-verify the branch against a real schema
  row with a named `children` scope before assuming it works untested.
