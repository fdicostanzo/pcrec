# K57 fix (2026-09-15, lane k57fix, sonnet)

Fixes K57 (`docs/dev/known_issues.md`): the `|` block scalar's dedent
strip was a BYTE COUNT, so a continuation line indented LESS than the
block's own dedent depth (set by the first continuation line) had its
first N bytes deleted silently, exit 0. Per the manager's standing
pre-ruling for this lane (checked first against the design, which
deliberately left this decode case to the implementer — see
`format_design.md` §1.2.1 S3 and §1.2.5), the fix is REFUSAL BY NAME,
class `value-shape`, naming both the shallower line's own indent and
the depth the first continuation line set — never silent loss, never
silent reinterpretation.

## Where the fix lives

All three legs implement the identical byte-count dedent, and all three
were fixed:

- **Leg A** — `src/parse/rxt_source.c`'s `read_prose_region`. A new
  validation pass runs over every line in the region before any
  stripping: a CONTENT line (one with a non-whitespace byte after its
  own leading whitespace run) whose own run is shorter than the block's
  established `indent` refuses, class `value-shape`. A WHITESPACE-ONLY
  line is exempt — it is BYTES per S3 and decodes to an empty
  paragraph-break line whatever its own width (`prose_paragraph_break
  .rxtin`, unaffected).
- **Leg B** — `tests/harness/run.sh`'s `prose_take`. Carries the
  identical validation. **Needed a LATCH beyond the check itself**:
  `prose_take` is called per streaming line and `record_fail_class`
  never aborts the file the way leg A's C-level `return` does, so the
  naive fix (validate, record, clear `prose_open`) let the region's
  REMAINING lines fall through to the top-level per-line dispatch as
  ordinary directives — which raised a SECOND, unrelated
  `structure-attachment` failure ("indented line continues nothing")
  that `extract_class`'s last-bracket read then reported instead of the
  real one. Caught live on the new three-leg fixture before it shipped
  (see below), not assumed. `prose_bad`, a per-region latch reset
  alongside `prose_dedent` at all three sites that open a region, is
  the fix: once set, `prose_take` keeps silently swallowing the
  region's lines rather than handing them back to the dispatcher —
  what leg A's single-pass extent scan does for free.
- **Leg C** — `tests/harness/verify_rxt.py`'s prose-region arm inside
  `parse_rxt`. Carries the identical validation. `_fail` already raises
  immediately (a `ValueError` that propagates out of `parse_rxt`), so
  no latch was needed here — leg C's caller never sees a
  partially-refused region.

## Fixtures and the check flip

`tests/rxtsource/fixtures/prose_dedent.rxtin` is **UNCHANGED IN
CONTENT** (the original three-line repro) and its check in
`run_rxtsource_tests.sh` is **INVERTED**, per r59-R4's own prediction
recorded in the fixture's own header: it used to be an `accept_value`
pin on today's wrong decoded string; it is now a `check_refusal`. It
stays **LEG-A-ONLY** — the fixture is head-scoped (`description |`
above the first `pattern`), and the head has one parser by the seam
ruling, so legs B and C never reach it regardless of what their own
dedent code does.

**`tests/rxtsource/fixtures/prose_dedent_body.rxtin` is NEW** — the
identical shallow-continuation shape, at BLOCK scope (inside a
`pattern` block's own `description`) rather than the file's head, so
all three legs parse it. Checked with `check_refusal_all3_kind
description prose_dedent_body.rxt prose-dedent-body value-shape ...`:
all three refuse, class `value-shape` agrees across all three
(confirmed live — this is where the leg-B cascading-error bug above
was actually found), and it rides `description`'s existing
`all-readers` receipt population (W23-S5) rather than opening a new
kind.

## Docs

- `docs/dev/known_issues.md` — K57's header now reads `FIXED 2026-09-15
  (lane k57fix)`; the entry's body gains the fix mechanism, which legs
  carry it, the latch finding, and the fixture pointers. The original
  filed description (repro, mechanism-as-filed) is left verbatim per
  house convention — only new paragraphs were added.
- `docs/spec/rxt_format.md` — §"S3 — opaque regions" (D80 spec hunk,
  the same change): a new paragraph states the dedent-DECODE rule
  normatively (dedent depth set by the first line; deeper lines keep
  relative indent; a whitespace-only line is the paragraph break; a
  shallower CONTENT line refuses, class `value-shape`). The section
  previously stated only the region's EXTENT and left the decode
  entirely to `known_issues.md`'s own prose.
- `src/parse/CLAUDE.md`, `tests/harness/CLAUDE.md`, `tests/rxtsource/
  CLAUDE.md` — each gained a dated note ("[K57FIX, 2026-09-15]" /
  "[K57FIX lane, 2026-09-15]") at the relevant bullet/section, per the
  file-add/role-change maintenance convention (`prose_dedent_body
  .rxtin` is a new file; `prose_dedent.rxtin`'s own role flipped;
  `prose_take`/`read_prose_region`/leg C's prose arm all changed
  behaviour).

**Deliberately NOT edited**: `docs/design/dd13_format/format_design.md`
still describes K57 as filed/unfixed in several places (its own §0.8
history, the K57 narrowing-census entry, `w23_impl.md`'s r59-R4 record).
Per the tree's own precedent (`w232_report.md`: "a lane does not edit
the ruled design note" — corrections to that document land AT THE
MERGE, in the manager's voice), this lane leaves those mentions as the
historical record they are and flags the one-line status update as
owed to the manager at merge. Same for `docs/dev/plan.md`'s [DD-13b.W23]
narrative, which already correctly predicted "K57 stays unfixed ...
goes red at its fix" — historically accurate, no edit needed, though
the manager may want a closing note.

## Validation

- `make -j4 CC=gcc-16` — clean build, no warnings.
- `make strict` — **clean** ("whole tree compiles clean with -Werror
  -Wshadow").
- `bash tests/rxtsource/run_rxtsource_tests.sh` — **208/0**
  (`checks recorded: 1`), up from the branch point's 205 by exactly the
  +3 the new three-leg fixture check contributes (leg A's own
  `check_refusal` line + legs B/C's class-agreement lines); the
  `prose_dedent` flip is a like-for-like swap (1 check either way).
  Census unmoved: **210 files / 3936 blocks / 28943 expectation
  lines**. `prose_hash`/`prose_ragged`/`prose_paragraph_break` (the
  three AVOIDED-narrowing pins) all still pass unchanged — the fix
  does not touch the legitimate ragged/paragraph-break shapes.
- Manual repro check: the exact K57 known_issues.md transcript
  (`printf 'description |\n    line one\n  dedented-line-two\n\n
  pattern a\n' > d.rxt; build/pcrec --list-source d.rxt`) now exits 1
  with `pcrec: [value-shape] d.rxt:3: block scalar '|' continuation is
  indented 2, less than the block's own indent 4 set by line 2 --
  dedenting would delete content` instead of silently emitting the
  corrupted value.
- Manual leg B/C check on the new body-scoped fixture: all three legs
  refuse with `[value-shape]` and no cascading second error (confirmed
  before AND after the `prose_bad` latch was added, showing the
  regression it fixes).

`make test`/`mech`/`san`/`axes`/`lint` were **NOT run** — BOILERPLATE's
box rule (lane `dialsweep` is running a corpus sweep) and this lane's
own scope (rxtsource + strict only). Owed to the manager's merge
battery.

## Commits on `lane/k57fix`

- `5a81ec38` — `[K57] WIP: refuse a shallower prose-region continuation
  line in all three legs` (the three code fixes: `src/parse/
  rxt_source.c`, `tests/harness/run.sh`, `tests/harness/verify_rxt.py`)
- `81adc35c` — `[K57] docs: known_issues FIXED marker, rxt_format.md
  dedent-decode spec hunk, CLAUDE.md updates + new three-leg fixture`
  (docs, the two fixtures, the test-script check flip)

PARKED on `lane/k57fix` — the manager merges; full battery rides the
next merge event per the box rule above.
