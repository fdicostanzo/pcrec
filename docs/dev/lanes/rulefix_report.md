# rulefix — Frank's two rulings of 2026-09-15

Both arose from lane w235's bench-acceptance dry run (`docs/dev/lanes/
w235_report.md` §2). Branch `lane/rulefix` off `main` at `7d128adf`.
Two commits, one per ruling: `21c958b5` (ruling 1), `2104ba5d` (ruling
2). PARKED per the brief — not merged; a full battery
(`build/battery_20260915_072130`) was in flight for this lane's whole
working period, so `make test` rides the next one.

## Rulings received, verbatim

**Ruling 1** (w235 finding 2, `cli/main.c:890-891`): "an EXPLICIT CLI
`--engine` value WINS over a target config's `engine` row, and a
conflict emits a DIAGNOSTIC naming both sources and both values (stderr,
non-fatal — the compile proceeds with the CLI's value)."

**Ruling 2** (w235 finding 1, `verify_rxt.py:667`): "fix the verify_rxt.py
first-block pattern-esc refusal" — Frank ruled FIX, not a documented
seam.

## Ruling 1 — CLI/config engine precedence

`cli/main.c`'s `apply_target` unconditionally overwrote `ts.opt.engine`
whenever a target's `engine vm` row was present, regardless of whether
the actual command line had asked for a different engine explicitly.

**Precedence rule implemented, checked first per the brief:** `--engine`'s
default is `auto` (`PCREC_ENGINE_AUTO = 0`, the field's zero value), and
it is the ONLY `enum` member — `PCREC_ENGINE_DFA`/`_VM` are `#define`s
(D60's ABI-namespace reason, unrelated). The field has exactly two
writers in the whole tree: the `--engine=` flag itself (identical whether
parsed from the real argv or from a `config` block's `pcrec <raw>` line,
reparsed through the SAME `cli_parse`) and the `engine` row. So checking
`ts.opt.engine != PCREC_ENGINE_AUTO` at the point `apply_target` reaches
the row is exactly "was `--engine=dfa` or `--engine=vm` typed" — no
separate tracking field needed for THAT distinction.

The one genuine ambiguity is `--engine=auto` typed explicitly: it is
byte-identical to no flag at all (same zero value). Per the ruling's own
wording ("the ruling's substance is that an explicit non-default CLI
choice is never silently overridden") this is stated as a boundary in
`docs/spec/cli.md` and in `cli/CLAUDE.md` rather than solved with
invented machinery — both cases want the same outcome (the file's row
applies, silently), so there is nothing to distinguish them FOR.

**Fix**: `apply_target`'s `engine` block now compares the current
`ts.opt.engine` against the row's requested value before overwriting.
Equal or AUTO → apply silently (unchanged behaviour). Non-AUTO and
different → keep the CLI's value, print a diagnostic naming the target,
both sources' spellings and both values, exit 0 (non-fatal).
`engine_name()` is a three-line helper added purely to render the enum
back to text for the message.

**D80 spec hunk**: `docs/spec/cli.md`'s "HOW A TARGET'S OPTIONS ARE
COMPOSED" section stated the old rule unconditionally ("the file wins...
there is no axis where naming a target silently discards an option you
gave"). Gained a new subsection naming `--engine` as the one exception,
with the diagnostic's exact shape and the `auto`-is-indistinguishable-
from-unset boundary stated explicitly. Checked `docs/spec/rxt_format.md`
for the same claim per the brief — its own `engine` mentions are either
about the FILE's own block-scoped `engine vm` directive (a different,
harness-only mechanism, `tests/harness/run.sh`'s own interpretation) or
point at `cli.md` §1 for the CLI contract rather than restating it, so no
edit was needed there.

**Behavioural checks, both directions** (`tests/rxtsource/
run_rxtsource_tests.sh`, W1.2 section — the existing target-`engine`-row
tests there are `--list-source`-only i.e. never actually compile; this is
the first place a real `--source` compile is checked against the file's
`engine` row, so it's the natural site): new fixture
`engine_cli_precedence.rxtin` (one unnamed block, block-scoped `engine
vm`, the implicit `target rx` default). Three checks: CLI silent → file's
row applies, empty stderr; CLI `--engine=dfa` conflicting → RX_ENGINE
"dfa" emitted, stderr names both `--engine=dfa` and `engine vm`, exit 0;
CLI `--engine=vm` agreeing → applies silently, no diagnostic. All three
hand-verified against a scratch build before being written into the
suite.

**CLAUDE.md**: `cli/CLAUDE.md` gained a dated section explaining the
mechanism and why no tracking field exists for the `auto` case.

## Ruling 2 — verify_rxt.py first-block pattern-esc refusal

`tests/harness/verify_rxt.py`'s attachment check (`first != 'pattern'`,
guarding the file's first non-comment line before any block has opened)
had no `pattern-esc` exemption, so leg C refused any file whose first
block opened with `pattern-esc` — `[unknown-token-in-scope] '...':
'pattern-esc' line before any pattern block` — even though legs A
(`pcrec --list-source`) and B (`run.sh --dump`) both accepted the
identical file (hand-verified against the pre-fix binary/script). This
is consistent with the delivered W23.3 schema: `pattern-esc` is S2's
second block opener (`format_design.md` §2.19, the schema table's
`opens_group` column), so wherever `pattern` may open a file's first
block, `pattern-esc` must too.

**Fix**: the test is now `first not in ('pattern', 'pattern-esc')`. Ruled
scope: only the OPENER recognition changed. The W23.5 R-A seam — leg C
reports a `pattern-esc` block's VALUE as written, never decoded, because
decoding would need a second copy of the eight-escape table in bash and a
third in python — is untouched; `pattern_esc_value_seam.rxtin`'s check
(A-vs-(B==C)) still passes unchanged, still asserting that exclusion.

**Consequence measured, per the brief**: `opener_pattern_esc_pair.rxtin`
(S242's own detector fixture, first block `pattern-esc "a"`) was never
reachable by a three-leg comparison before this fix — S242's own check in
`run_rxtsource_tests.sh` runs leg A (`--list-source`) only. Verified by
hand on a scratch build: before the fix, `python3 verify_rxt.py --dump
opener_pattern_esc_pair.rxt` raised `ValueError` at exactly the refused
line; after the fix it prints two blocks at lines 8 and 10, matching leg
A. `run.sh --dump` already accepted the file both before and after (only
leg C had the defect). S242's check gained a three-legged extension
(same file, right after the existing leg-A check) confirming legs B and
C both now report the two blocks at their own lines — this is the "fires
three-legged" re-verification the brief asked for, landed as a permanent
regression check rather than only a hand-verify.

`pattern_esc_value_seam.rxtin`'s leading `pattern` block (the "ordering
workaround" w233/w235 used, since its own value-seam claim doesn't need
`pattern-esc` to be first) is no longer load-bearing but was deliberately
left as originally written: restructuring it to drop the leading block
would exercise the SAME thing `opener_pattern_esc_pair.rxtin` now proves
directly, at the cost of re-deriving its `n==2`-indexed awk extraction for
no new coverage. Both `tests/harness/CLAUDE.md` (the `verify_rxt.py`
entry) and `tests/rxtsource/CLAUDE.md` (the R-A section) carry a dated
addendum recording the fix and this disposition, so a future reader
following either file's own "recorded rather than fixed" language is not
misled.

**Census / count deltas traced**: zero. The fix widens WHICH files leg C
accepts; it does not change how any already-accepted file is parsed, and
the shipped corpus has zero patterns whose first line is `pattern-esc`
(210/210 files unchanged — the corpus-control line in
`run_rxtsource_tests.sh` still reads `210` after this change).
`tests/rxtsource/run_rxtsource_tests.sh`'s own "checks passed" count rose
by exactly 1 (the new three-legged S242 assertion) on top of ruling 1's
+3, both accounted for below.

## Validation run (allowed set only — a full battery was in flight)

- `make -j4 CC=gcc-16`: clean build, no warnings.
- `make strict CC=gcc-16`: "strict: whole tree compiles clean with
  -Werror -Wshadow".
- `PCREC=$(pwd)/build/pcrec bash tests/rxtsource/run_rxtsource_tests.sh`:
  **205 passed / 0 failed / 1 recorded** (branch point was 201/0/1 per
  the brief; +3 ruling-1 checks, +1 ruling-2 three-legged check).
  `PCREC` must be an absolute path for this script — a relative one
  breaks its `cd`-then-invoke sites (`aux_identity` build check); this is
  a pre-existing script property, not something this lane changed, noted
  here because it cost one confusing red run before I passed an absolute
  path.
- `PCREC=$(pwd)/build/pcrec bash tests/cli/run_cli_tests.sh`: **284
  passed / 0 failed**.
- Hand-verified (not part of any suite, scratch build, both directions
  for each ruling): the four `--source`/`--engine=` combinations for
  ruling 1 (silent/conflict/agree/explicit-auto), and leg C's
  before/after behaviour on `opener_pattern_esc_pair.rxt` for ruling 2.

**Owed to the manager**: full `make test` (the battery in flight covers
it; not re-run here per the box constraint), `make mech`/`san`/`lint`/
`test-axes` (also owed, box-gated, same reason). Not an abi event — no
emitted-artifact scaffolding, struct layout, or `rx_info` field changed;
both fixes are CLI-argument-parsing and test-oracle-parsing changes only.
If the manager believes otherwise on review, that is a STOP-and-escalate
per the brief, but nothing in either diff touches `src/gen/`,
`lib/pcrec.h`, or any emitted artifact's text.

## Files touched

- `cli/main.c` — `apply_target`'s `engine` block, `engine_name()` helper.
- `cli/CLAUDE.md` — dated section on the mechanism.
- `docs/spec/cli.md` — the D80 hunk (the `--engine` exception to the
  file-wins rule).
- `tests/rxtsource/fixtures/engine_cli_precedence.rxtin` — new fixture.
- `tests/rxtsource/run_rxtsource_tests.sh` — ruling 1's three checks;
  ruling 2's three-legged S242 extension and R-A comment update (both
  rulings' test-script edits landed in the ruling-1 commit since they
  share one file — see commit `21c958b5`'s body).
- `tests/harness/verify_rxt.py` — the one-line opener-check fix.
- `tests/harness/CLAUDE.md`, `tests/rxtsource/CLAUDE.md` — dated
  addenda recording the fix.

## Handback

Both rulings implemented, both D80 hunks landed, both directions checked
for ruling 1, S242's reachability consequence measured and dispositioned
for ruling 2, rxtsource (205/0) and cli (284/0) green under the allowed
set. `make strict` clean. CLAUDE.md updated in every touched directory.
PARKED on `lane/rulefix` — not merged. Full `make test`/battery validation
is OWED to the manager, riding the battery already in flight.
