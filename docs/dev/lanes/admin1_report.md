# admin1 — MACPORT-XARGS + LIM-OVR bundle (2026-09-22, sonnet)

Two plan rows, two commits, each independently revertable. Branch
`lane/admin1` from main `69172a00`.

## Part 1 — [MACPORT-XARGS]: already fixed, not by this lane

**Finding, not a fix.** The row's whole charter — `tests/rxtsource/
run_rxtsource_tests.sh` legs B/C using GNU-only `xargs -a`, never running
on darwin — was already closed by Frank directly on 2026-09-10, commit
`fb1b9c5e` ("tests/rxtsource/run_rxtsource_tests.sh: fix xargs -a and wc -l
padding"), four days after this row was chartered (2026-09-06) and never
re-flagged in plan.md. That commit's own message records the exact
population the row named ("xargs -a's failure cascaded into 11 of the 14
test-rxtsource FAILs") and fixed all six remaining sites via the portable
`xargs CMD < "$FILES"` form.

**Live-verified on this box** at branch point `69172a00`:
`bash tests/rxtsource/run_rxtsource_tests.sh` reads **212 passed / 0 failed
/ 1 recorded**. The one RECORD line ("C3: population pins are python
3.14's numbers; this python (3.9)'s deltas...") is the pre-existing,
already-documented darwin python-version note (`btriage_20260917_
report.md`), not a failure and unrelated to xargs.

A tree-wide grep for `xargs -a`, `-d`, `--arg-file`, `--max-lines` and
other GNU-only spellings found none outside historical prose comments
explaining why those sites were avoided — every remaining `xargs` call in
the tree (`tests/mrl/run_mrl_tests.sh`, every `tests/codegen/run_*_
identity.sh`, `tests/registry/limits_check.sh`, etc.) already uses the
portable `xargs CMD < FILE` or `... | xargs -0 CMD` form. `docs/testing.md`
carries no darwin-known-reds text citing a 14-failure xargs class either,
so no re-pin was owed there.

**No code change made.** Delivered as a plan-tracking correction: the row
archived to `plan_completed.md` with the fix commit cited and the darwin
re-verification recorded (commit on this branch).

**Linux verification command for the executor** (unchanged in shape by
this finding, since nothing here touched behavior):

    bash tests/rxtsource/run_rxtsource_tests.sh

Expect the identical PASS population to darwin's 212/0/1 (the RECORD
line's exact wording may cite the Linux box's own python3 minor version
instead of 3.9 — expected version-sensitivity per the existing C3 note,
not a divergence).

**Process finding, not this lane's to fix**: `docs/dev/backlog_
triage_2026-09-22.md`'s own MACPORT-XARGS row (delivered by lane `backtri`
hours earlier the same session) cites the same now-stale "14 pre-existing
failures, A/B'd" figure as evidence the row was ready to schedule, rather
than as a citation of an already-fixed defect. Flagged to the manager
rather than self-edited, since that inventory is another lane's delivered
artifact and out of this lane's chartered scope.

## Part 2 — [LIM-OVR]: the FLAG_D token + the override-honesty check

**The audit found four rows, not one.** The charter named
`PCREC_MAX_AUTO_DFA_ELEMS` and said "audit the other five BUILD_D rows."
Of `src/core/limits.def`'s six `BUILD_D` rows, checking each against
`cli/main.c`'s `raise_only_limits[]` table found:

| row | real caller lever? | how |
|---|---|---|
| `PCREC_MAX_AUTO_DFA_ELEMS` | yes | `--max-auto-dfa-elems` (table, raise-only) |
| `PCREC_MAX_VM_EMIT_CODE_BYTES` | yes | `--max-emit-code-bytes` (table, raise-only) |
| `PCREC_MAX_EMIT_BYTES` | yes | `--max-emit-bytes` (table, raise-only) |
| `PCREC_DEFAULT_WARN_EMIT_BYTES` | yes | `--warn-emit-bytes=` (bespoke, NOT raise-only — settable to any value) |
| `PCREC_ANCHORED_MAX_STATES` | no | no cli/main.c reference at all |
| `PCREC_SIZE_TERM_THRESHOLD` | no | no cli/main.c reference at all |

The fourth row, `PCREC_DEFAULT_WARN_EMIT_BYTES`, is not in
`raise_only_limits[]` at all — its flag is wired through a separate
`else if` block in `cli_parse` because it is settable to any value, not
raise-only (docs/spec/limits.md's own "the one size option that is not
raise-only" section). It would have been missed by an audit that only
grepped the table; it was found by reading the flag's actual wiring.

**The fix, exactly as the charter scoped it.** A new override token,
`FLAG_D`, carrying `BUILD_D`'s identical `-D`-movable-default generation
machinery:

- `src/core/limits.h`: one more dispatch macro,
  `PCREC_LIMIT_LIMITS_H_FLAG_D`, body identical to `_BUILD_D`'s (both read
  `default_name`). The `#ifndef`/`#define`/`#endif` wiring blocks below are
  UNCHANGED — they are keyed on the row's NAME, never on which override
  token named it, so a caller-facing flag existing changes nothing about
  how the built-in default itself is moved at pcrec's own build time.
- `src/dump/limits_dump.c`: `override_name()` gains `FLAG_D` -> `"flag+-D"`.
  `BUILD_D`'s own rendering, `"-D"`, is UNCHANGED and still accurate for
  its two remaining rows.
- `src/core/limits.def`: the four rows' override token moved `BUILD_D` ->
  `FLAG_D`, each with a one-line note citing [LIM-OVR] and why. The other
  two rows are untouched.
- `docs/spec/limits.md` §3.4a: the override vocabulary gained the fourth
  spelling (D80 — this is caller-observable, `--list-limits` is public
  surface per `lib/pcrec.h`'s `pcrec_limits_tsv` declaration). No other
  spec section states an override-column value for any of the four moved
  rows, so no further spec hunk was owed.
- **NOT an abi event**: `--list-limits` is compiler-side registry surface,
  not emitted-artifact scaffolding. D76/D94's bump ritual is about what a
  generated MATCHER carries; this changes nothing any artifact emits.

**The owed check, built.** `tests/registry/limits_check.sh` gains part 4
(the file's own header now says "FOUR PARTS", was three). It reads
`cli/main.c`'s `raise_only_limits[]` table BY GREP — independent of
`limits.def`'s own override token, the same K35 "a control must not share
a source with what it controls" discipline part 3 already follows — plus
one named, live-verified bespoke-flag site (`grep -q '"--warn-emit-
bytes='`), and cross-checks BOTH directions against every dump row whose
rendered override is `-D` or `flag+-D`: a row with a real lever whose
override does not say so (the exact [LIM-OVR] shape), or a row claiming
one it does not have. Deliberately scoped to the six `BUILD_D`/`FLAG_D`
rows rather than to every row rendering plain `flag` (eleven total) —
the other five FLAG rows have no `-D` machinery at all and are a
different, unchartered question.

Live output after the fix:

    PASS: [override-src] cli/main.c's raise_only_limits[] table names exactly the 6 expected limits.def rows
    PASS: [override-src] cli/main.c still carries the bespoke --warn-emit-bytes= flag (PCREC_DEFAULT_WARN_EMIT_BYTES's caller lever)
    PASS: [override-honesty] all 6 '-D'/'flag+-D' rows agree with cli/main.c's actual flag surface, both directions (4 render 'flag+-D' with a real lever each, 2 render plain '-D' with none)

**Sabotage-validated live** (scratch, reverted before commit): reverted
`PCREC_MAX_EMIT_BYTES`'s token from `FLAG_D` back to `BUILD_D`, rebuilt,
re-ran the check — part 4 fails naming the row and the exact [LIM-OVR]
shape ("has a REAL caller-facing flag in cli/main.c but its dump override
is '-D'"), 26/1. Reverted, rebuilt clean, back to 27/0.

**S208 re-aimed.** `tests/mech/sabotages/S208_limits_row_value_drifts_
from_doc.sh`'s `SAB_BEFORE`/`SAB_AFTER` anchors quote `PCREC_MAX_VM_EMIT_
CODE_BYTES`'s full row text verbatim, which moved from `BUILD_D` to
`FLAG_D` plus the new derivation note. Re-anchored to the current text
(verified byte-for-byte against the live `limits.def` line via a python
round-trip before committing — the same `SAB_BEFORE = git show HEAD:<path>`
discipline BOILERPLATE names). NOT re-run through `make mech` (a full
sabotage-matrix build is well beyond this lane's scope and the box's
one-heavy-suite-at-a-time rule); the manager or the next mech run should
solo-verify with `bash tests/mech/run_sabotage_matrix.sh S208` and expect
`limits:1fail/Npass` naming the value drift, matching the row's own
`SAB_DOC_FIGURE` shape.

**Every live reader found by grep and updated** (root CLAUDE.md's D94
discipline, applied here to a registry-dump change rather than an abi
bump): `src/core/limits.def`'s own header vocabulary and mechanism
comment (the worked example there was literally
`PCREC_MAX_VM_EMIT_CODE_BYTES`, one of the four moving rows — its citation
of `PCREC_LIMIT_LIMITS_H_BUILD_D` became `_FLAG_D`), `src/core/limits.h`'s
dispatch-macro block comment, `src/core/CLAUDE.md` and `src/ir/CLAUDE.md`
(both cited `BUILD_D` by name for `PCREC_MAX_AUTO_DFA_ELEMS`),
`tests/codegen/run_n1_budget.sh` and `tests/codegen/CLAUDE.md` (same row,
same citation, since that row's reference-compiler technique is the
worked example for why the `-D` lever exists at all), and
`tests/registry/CLAUDE.md`'s `limits_check.sh` entry (part count + a new
paragraph). A tree-wide grep for `BUILD_D` outside historical lane
reports/reviews/journal/plan_completed.md found only `BUILD_DIR` (the
unrelated Makefile variable) false positives beyond the files above.

**Deliberately NOT touched**: the charter's own last sentence names a
D26-tier unit-harmonization residual ("elements" vs "state-set elements")
and says "harmonize opportunistically at a future abi event, never
alone" — left exactly as instructed.

## Validation

| command | result |
|---|---|
| `make -j4 CC=gcc-16` | clean |
| `make strict CC=gcc-16` | clean ("strict: whole tree compiles clean with -Werror -Wshadow") |
| `bash tests/registry/limits_check.sh` | 27/0 (was 21/21 at [LIM-1]'s own landing count; +3 PASS lines for part 4) |
| `bash tests/rxtsource/run_rxtsource_tests.sh` | 212/0/1 recorded (Part 1's own evidence) |
| `make test-codegen CC=gcc-16` | **9/10 scripts passed**; `checks passed: 65 / checks failed: 0` before the one red. The sole failure is `run_inline_capability.sh`'s `FAIL: nm could not read arm_a.o (no rx_search symbol)` — the STANDING darwin `nm`-on-Mach-O red documented in 29 separate `docs/dev/lanes/*.md` reports since the two-machine split (`mtriage_report.md`, `w5_report.md`, `evtriage3_report.md` among them), unrelated to `limits.def`/`xargs` by construction — `run_inline_capability.sh` probes VM entry-shape capability via an `nm` symbol read, nothing this lane touched. `run_n1_budget.sh` (the direct exerciser of `PCREC_MAX_AUTO_DFA_ELEMS`'s reference-compiler technique, one of the four rows this lane moved to FLAG_D) is inside the SAME `run_group` batch and its own PASS lines are in the log, unaffected. |

`make test` in full is the manager's, per the brief.

## Handback

Sent to `main` via SendMessage before this report's final commit, per
BOILERPLATE — see that message for the numbers as they stood at hand-off,
and for `make test-codegen`'s result if it completed before the handback
was sent.
