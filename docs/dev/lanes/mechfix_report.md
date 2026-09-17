# lane mechfix — the mech arm's missing-log default (2026-09-17)

Branch `lane/mechfix`, base `cf0962e3`. Two commits: `81c2a6f0` (the fix),
`4b97abc9` (docs). PARKED, not merged.

## The defect (pre-existing, flagged by lane dialimpl)

Every suite arm in `tests/mech/run_sabotage_matrix.sh` scraped `p`/`f`
out of its own suite log and scored with

    [ "${f:-1}" -gt 0 ] 2>/dev/null && any_fail=1

so a MISSING suite log — or one the scrape pulled no number from —
DEFAULTED the failure count to 1 and the row scored **DETECTED**: a suite
that never ran was credited with catching the plant. The distinguishing
evidence (the `ERRfail/?pass`-shaped results cell) was printed on every
such row and nothing read it. The incident: S249's first run, where the
tunedial suite script was uncommitted, `git archive HEAD` produced a tree
without it, and the row read `tunedial:ERRfail/?pass DETECTED`
(dialimpl_report.md; superseded reading recorded in S249's own
`SAB_DOC_FIGURE`).

## Site count

**52 sites**, enumerated mechanically (every `${f:-1}` occurrence in the
driver): 50 uniform three-line sites (`suite_bits+=` / the defaulting
test / `any_ran=1`) and 2 structured variants — the `framebuffer` arm's
totals-first/exit-second ladder and the `registry` arm's compliance
interleave. The report's "ALL arms" claim confirmed.

## The fix — one general site

`score_arm LOGFILE FCOUNT CELL` in `run_sabotage_matrix.sh` (defined
above `run_one`, called inside its subshell) is now the single place a
scraped count becomes a verdict bit. All 50 uniform sites were rewritten
to one call each (the rewrite was scripted, not hand-copied; each call
passes the arm's pre-rendered cell so NO arm's cell format moved on the
healthy path). The two variants keep their shapes with only the
missing-count path routed through the helper:

- **missing/EMPTY log** → cell `NAME:NO-LOG(<file>)`, `any_unmeasured`;
- **log present, no scrapeable count** (the S249 incident's exact shape —
  bash's no-such-file error is the whole log) → the documented
  `ERRfail/?pass` cell, `any_unmeasured`;
- **numeric count** → byte-identical behaviour to the old code.

`any_unmeasured` is Frank's S155 vocabulary, deliberately reused rather
than minted: the verdict block renders it ANOMALY, and a real `any_fail`
from another arm still outranks it. A count is synthesized in NEITHER
direction — scoring the absence as f=0 would be the UNDETECTED lie
instead ([ABI-NS]: a detection helper that defaults on missing input
fails in the silent direction).

One addition to the verdict block: when EVERY assigned arm is unmeasured,
a new branch names the arms and their logs
(`ANOMALY (no assigned arm produced a measurement:
tunedial:no-count-scraped:tunedial.log)`) instead of falling through to
the bare `ANOMALY (no suite ran)`.

`framebuffer`'s first branch also changed from `[ "${f:-1}" -gt 0 ]` to
`[ "$f" -gt 0 ]`: under the old spelling a missing count not only scored
DETECTED, it MASKED the arm's own `UNMEASURED-no-asan` branch (rc=3 was
never consulted because the defaulted 1 took the first branch).

## Validation — the failing direction FIRST

All runs solo through the real driver; temp commits used for the repro
were dropped (`git reset` to base) before the fix was committed.

| step | tree | driver | reading |
|---|---|---|---|
| repro | base + `git rm run_tune_dial.sh` (temp) | PRE-fix | `reach:ok(4/4), tunedial:ERRfail/?pass` — **DETECTED, anomalies: 0** (the false-DETECTED, reproduced exactly) |
| fix, same tree | same temp HEAD | post-fix | `tunedial:ERRfail/?pass` — **ANOMALY (no assigned arm produced a measurement: tunedial:no-count-scraped:tunedial.log), anomalies: 1** |
| NO-LOG variant | base + silent `exit 0` stub suite (temp) | post-fix | `tunedial:NO-LOG(tunedial.log)` — same ANOMALY shape, `no-log` token |
| real S249 | `81c2a6f0` | post-fix | `reach:ok(4/4), tunedial:11fail/9pass` — **DETECTED**, unexpected 0 |
| real S249 A/B | `81c2a6f0` | PRE-fix (checked out to the path, then restored) | `reach:ok(4/4), tunedial:11fail/9pass` — byte-identical counts |
| real S204 | `81c2a6f0` | post-fix | `pop:…unknown_kind.rxtin:/^no-such-kind /=1(want>=1), rxtsource:1fail/211pass` — **DETECTED**, unexpected 0 |
| field validation | `81c2a6f0` | post-fix | `VALIDATE_ONLY=1`: **261 definition(s) valid** |
| `bash -n` | — | post-fix | clean |

## Finding: S249's recorded count has drifted, and it is not this lane's

S249's `SAB_DOC_FIGURE` records `tunedial:8fail/9pass` at its own pin
(tree `5f2d757d`, pre-merge). Today's HEAD reads `11fail/9pass` — through
the PRE-fix driver as well (the A/B row above), so the +3 is the
k59rung/dialimpl merge's suite growth (the clean suite still totals 17/0;
under the plant K59's ladder machinery emits three additional failing
sub-checks), not a scoring change. For numeric `f` the two drivers are
semantically identical by construction and measured identical here. The
row's figure update is left to the row's owner/manager rather than
drive-by edited by this lane; flagged in the handback.

## Docs

- Driver header: the missing-log ANOMALY rule added beside the
  SAB_REQUIRE/ANOMALY paragraph it generalizes.
- `tests/mech/CLAUDE.md`: a paragraph under the `run_sabotage_matrix.sh`
  entry (the defect, the incident, the mechanism, the validation shape).

## Not done, deliberately

- No full `make mech` (owed to the nightly checkpoint per the brief; the
  fix's blast surface on green rows is the healthy path, shown
  byte-identical by A/B).
- No edit to S249's `SAB_DOC_FIGURE` (another lane's row; see the
  finding above).
- The pfcollapse arm's inline "`ERRfail/?pass` here is a scrape
  mismatch" comment still reads correctly under the new scoring (such a
  row now reads ANOMALY rather than DETECTED) and was not reworded.
