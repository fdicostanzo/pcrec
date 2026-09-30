# k76fix — K76: a `.rxt` file whose first block is `pattern-esc` read as head-bearing

Lane k76fix (sonnet, 2026-09-30), branch `lane/k76fix`.

## Repro and what the misread does

`/tmp`-scratch witness = `tests/rxtsource/fixtures/opener_pattern_esc_pair.rxtin` (first token `pattern-esc`).
With a `--list-source` counting wrapper as PCREC (`--dump`):

| reader | unfixed | fixed |
|---|---|---|
| run.sh (leg B) `--list-source` calls | 1 | 0 |
| verify_rxt.py (leg C) `--list-source` calls | 1 | 0 |
| rxtsource census awk (`$1 != "pattern"`) | head-bearing | not head-bearing (awk widened) |

Consequence, measured: the file takes the head-bearing path, so pcrec's `--list-source` runs over the
WHOLE file. A refusal in any later block becomes a whole-file `HARNESS FAILURE`, and the earlier blocks'
passing cases are lost (`pattern-esc "a"` + a passing case, then a malformed `pattern-esc` block: unfixed
`0 passed / 2 failed`, one line naming a head; fixed `1 passed / 1 failed`, naming the bad block). No
wrong answer was found certified; the harm is a misattributed/lost block and a census that counts a
headless file as head-bearing (C0a/C1 populations off by one, as k73utf saw: 25 vs 24).

## Fix (format's own rule: the head ends at the first BLOCK OPENER; `rxt_schema.def` `opens_group` = `pattern`, `pattern-esc`)

- `tests/harness/run.sh`: `rxt_is_opener`, the one bash home; used at the 4 head tests (include discovery, closure walk, the per-file loop, ...).
- `tests/harness/verify_rxt.py`: `_RXT_BLOCK_OPENERS`, used by the entry-set walk's head probe and by the attachment check that already had the pair spelled inline.
- `tests/rxtsource/run_rxtsource_tests.sh`: census awk widened, held in `HEAD_CENSUS_AWK`.
- Other readers grepped (`scripts/`, `tests/lib`, `tests/mech`, `src/parse/rxt_source.c`): the C parser already treats both as openers; `scripts/emit_sweep.py`/`cls_identity.py` already accept both. The two `$2 != "pattern"` awks in the rxtsource script read `--list-source`'s KIND column, where a `pattern-esc` block is reported as `pattern` (checked), so they are correct.
- Two readers share a rule only by mirrored definition (bash / python / awk cannot share code); each names the others in its comment.

## Regression witness and failing direction

`K76` check in `run_rxtsource_tests.sh` (after the S242 three-legged check): wrapper-counted
`--list-source` calls from legs B and C, the census awk itself, and a control that the pre-fix rule
(`$1 != "pattern"`) reads the witness head-bearing, so the witness must discriminate. Failing direction
shown by restoring HEAD's run.sh and verify_rxt.py in place: B=1 C=1; fixed: B=0 C=0.

## Workaround removed

`tests/utf8/k73_startskip.rxt` first block `pattern (?:)` -> `pattern-esc ""`; harness 86 passed / 0 failed
before and after, verify_rxt.py ALL CHECKS PASSED (86 skips, pcre2-only), census counts unmoved (both
openers counted).

## Other edits

S203 re-aimed (its anchor line changed; `scripts/m6read_check_sab_anchors.py`: 351 sabotages, all resolve).
`docs/spec/rxt_format.md` head-boundary sentence names both openers. `docs/dev/known_issues.md` K76 FIXED.
`tests/harness/CLAUDE.md` phrase updated.

## Validation

See the handback; the rxtsource log is `/tmp/k76r/rxtsource.log` (session scratch).
