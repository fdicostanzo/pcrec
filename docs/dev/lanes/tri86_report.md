# tri86 — triage of land85's `make test` red (2026-09-28)

Lane land85's full `make test` on its tip 5d72b4bb (main c90e4481 +
land85's own fixes) went red in three named sections: `test-corpus`,
`test-codegen`, `test-rxtsource`. Brief: diagnose each by name, fix the
real cause(s) — general mechanism preferred over path-shaped patches,
per the lead's own hypothesis that findb6's golden fixtures were being
swept as pattern corpora — and re-validate each targeted section.

**Verdict: all three sections are GREEN now.** Every real cause traces to
one event — lane findb6 ([FINDINGS] B6, merged at c90e4481) added
`tests/findings/golden/`'s eight golden analyzer-output fixtures without
re-deriving several DERIVED-BY-MECHANISM pins and without re-running the
D94 abi-bump re-pin sweep for an unrelated concurrent landing (findtie's
abi 43→44). Nothing here is a defect in findb6's own module content; every
fix is either a stale pin or a latent mechanism defect that had zero
population until B6 gave it one.

## test-corpus: box-load false positives, not a regression

The nine `TIMED OUT (>10s)` failures in land85's own chain log (`d27_
nesting.rxt`, `dot.rxt`, `empty_matches.rxt`, `eol_engine.rxt`,
`eol_scan_avoidance.rxt`, `escapes.rxt`, `fuzz_regressions.rxt`,
`high_bytes.rxt`, `k18_arm_order.rxt`) are all trivially-fast, unrelated
patterns across unrelated files — not a plausible simultaneous hang.
Each reproduces CLEAN standalone (`bash tests/harness/run.sh tests/base/
<file>.rxt`, 0 failed on every one) once land85's own concurrent chain
(mech rows S329/S311, `census_corpus`, `run_findings_tests.sh`) had
finished — a box-load artifact against the 10s `GENRUNTIMEOUT` budget,
the same shape this house has recorded before (nltriage, btriage2). No
fix needed; no regression.

The REAL failure in this section — `tests/findings/golden/*.rxt` scored
as broken pattern-corpus files (P-C2 floor / harness-failure / schema
errors) — is the same root cause as test-rxtsource's, fixed below (golden
now joins run.sh's own `-not -path` exclusion, same shape as adversarial/
witness).

**Re-validated**: full `make test-corpus CC=gcc-16`, GREEN — 29,385 cases
passed, 0 failed, 0 pattern-compile failures, 222 entry files (matches
`RUNSH_FILES`). `docs/dev/artifact_size_log.tsv` refreshed by this run
and committed (3560 → 3596 rows, corpus growth since its last refresh,
unrelated to this triage).

## test-codegen: a stale abi pin plus a latent backtick/$ bug it exposed

`run_codegen_tests.sh`'s `ABI_EXPECT=43` was never re-pinned when
lane findtie bumped `PCREC_ARTIFACT_ABI` 43→44 (merge `72e3ae41`,
"[FIND-TIE] ... abi 43->44, S329") — that merge touched `tests/codegen/
run_prechecks.sh` but missed this file, a D94 re-pin site the ritual's
grep sweep did not find.

That stale pin only mattered because taking the mismatch branch (i.e.
calling `bad "..."`, the [DD-14.FB] abi-history diagnostic) exposed a
SECOND, independent, pre-existing defect: that diagnostic string —
30,795 bytes on one logical line, the growing abi-bump narrative every
lane since abi 2 has appended to — contains dozens of unescaped
backticks (markdown-style code formatting in prose: `` `nentries` ``,
`` `site.group` ``, `` `vars` ``, …) and four literal `$`-refs that are
prose, not real shell variables (`${name}`, `$_var_match`,
`$_var_match_caseless`, `$_var_valid`), all inside a DOUBLE-QUOTED bash
string. Bash reads an unescaped backtick pair as command substitution
and `${name}`/`$_var_match` as parameter expansion; under this script's
own `set -u`, the first unset-variable reference it reaches
(`${name}`) aborts the WHOLE SCRIPT with `name: unbound variable` —
which is exactly land85's `tests/codegen/run_codegen_tests.sh: line
2886: nentries: command not found` / `... vars: command not found` /
`... name: unbound variable` cascade. This branch had never been taken
before (every prior abi bump correctly re-pinned this same line, so the
defect had zero population until findtie's merge missed it).

Fixed both: `ABI_EXPECT` 43 → 44, and every unescaped backtick / prose
`$`-ref in the diagnostic string escaped (the three genuine variable
expansions — `$fb_abi_vm`, `$fb_abi_dfa`, `$ABI_EXPECT` — left alone).

**Re-validated**: full `make test-codegen CC=gcc-16` — `run_group:
11/12 scripts passed`; `run_codegen_tests.sh` (script 0, the one that
was red) is now clean (checks passed, 0 failed, no crash). The sole
remaining red is `run_inline_capability.sh`'s `FAIL: nm could not read
arm_a.o (no rx_search symbol)` — the ONE accepted darwin red the brief
named up front; unrelated, unchanged, confirmed pre-existing (every
other codegen script in the run was green).

## test-rxtsource: golden/'s census/harness/oracle reconciliation, four sites

The lead's hypothesis confirmed: `tests/findings/golden/`'s eight files
are ANALYSIS BUNDLES (`analysis <name>` head, `freq`/`bigram`/`cpfreq`
data blocks, zero `pattern` blocks), and `run_rxtsource_tests.sh`'s own
derived-by-mechanism pins (`CENSUS - kf - adv = RUNSH`) were never
re-derived for them. Four sites, each a real finding:

**1. `CENSUS_FILES` stale (238, live count 246).** `find tests -name
'*.rxt'` genuinely finds 246 files; golden's 8 were never added to the
pin. Re-derived by the file's own awk census run per-file over
`tests/findings/golden/`: +8 files / +0 blocks / +0 lines (each is
head-only, matching findb2's own +16/+0/+0 precedent for adversarial/
witness). `CENSUS_FILES` → 246; `CENSUS_BLOCKS`/`CENSUS_LINES` unchanged.

**2. run.sh swept golden/ as pattern-corpus files.** This is the general
mechanism fix, not just a path patch, though BOTH were needed:

- **General**: `run.sh`'s P-C2 floor ("no pattern blocks parsed from
  file") is now DECLARATION-GATED, but scoped to `--dump` mode only —
  under `--dump`, a head-bearing file whose own head (`pcrec
  --list-source`) says it carries no `pattern` row is not scored as a
  corpus file that forgot its cases (`--dump` never runs a case for any
  file, so P-C2's own reason does not apply). This is exactly the
  filed follow-up ("recognise an analysis bundle by its DECLARATION, not
  by path", findb2tri 8803ab8e) — and it required correcting my own
  FIRST draft: an unscoped exemption (P-C2 never firing regardless of
  mode) directly contradicts `tests/rxtsource/fixtures/head_only.rxtin`'s
  own deliberate test, which asserts that an ORDINARY run.sh invocation
  on a head-only file MUST still fail P-C2 ("a file that runs nothing
  must not read as a clean pass"). Caught by re-running test-rxtsource
  after the first draft and reading the new red rather than assuming
  green. The final fix preserves that assertion exactly: `--dump`
  exempts, an ordinary run does not.
- **Stopgap, still needed**: `tests/findings/golden/` joins run.sh's
  `-not -path` exclusion list beside `adversarial/`/`witness/`, because
  declaration alone cannot save five of golden's eight files — they use
  an analyzer-output dialect (`pcrec-analyze`'s own "bigram" bundle
  scan-kind; a provenance rule looser than pcrec's `--list-source`
  enforces) that `pcrec --list-source` cannot parse AT ALL today, so the
  P-C2 floor never gets a chance to run on them — something else (a real
  parse failure) fires first, correctly. Fixing the analyzer/pcrec
  dialect gap is not this triage's charter.

`RUNSH_FILES`/`BLOCKS`/`LINES` stay 222/4052/29385 (golden contributes 0
either way, matching findb2tri's own precedent one directory over); the
`adv_files`/`adv_blocks`/`adv_lines` reconciliation grep widened to
`/findings/(adversarial|witness|golden)/`.

**3. `C3_CRASHED_HEADBEARING` stale (16, should be 24).** `verify_rxt.py`
refuses ANY head-bearing file by name (the seam ruling: one head parser,
pcrec's) — golden's 8 join adversarial/witness's 16 in this pinned,
permanent, EXPECTED bucket. Re-pinned 16 → 24.

**4. Two more real, previously-zero-population mechanism defects**,
found validating (2) and (3) against golden's five genuinely-unparseable
files:

- **leg B's own tolerance** (`run.sh --dump`'s nonzero-exit cause) was
  hardcoded to "exactly the P-C2 floor, `$head_files` times" — both
  numbers wrong now that P-C2 is declaration-gated (0 occurrences) and
  five files fail a DIFFERENT, real way (a `[resolution]`-class
  entry-closure failure plus a `HARNESS FAILURE: pcrec --list-source
  failed` line, three lines each). Re-derived into three named,
  independently-asserted counts: `legb_pc2 == 0`, `legb_harness_fail ==
  HEAD_PARSE_FAIL_FILES` (new pin, 5), `legb_resolution == 2 *
  HEAD_PARSE_FAIL_FILES`, `legb_other == 0`.
- **leg A's error detection was silently dead.** `if ! cmd1 | awk ...`
  tests the PIPELINE's exit status — `awk`'s, not `pcrec`'s — and this
  script has no `set -o pipefail` anywhere. A failing `pcrec
  --list-source` call was silently skipped with no `fail` and no
  `break`, despite the code's own comment describing exactly that
  hard-stop. Zero population (nothing in the corpus made the call fail)
  until golden's five files existed to exercise it — found by measuring
  `a_head_rows` (19, not `head_files`'s 24) and by C0a's own
  `39`-calls-for-`24`-head-bearing-files mismatch. Fixed with a two-step
  capture (redirect to a temp file, test `$?` directly) tolerating
  exactly `HEAD_PARSE_FAIL_FILES` (5) failures by count — a sixth would
  now be a real, loud, unaccounted-for failure. `a_head_rows`'s own
  check corrected to `head_files - HEAD_PARSE_FAIL_FILES` (a file whose
  head does not parse emits no row at all — a third observable, distinct
  from both "no head" and "a head that parses and declares zero
  patterns").
- **Root cause of (leg A's dead detection), fixed at its source**:
  `rxt_list_source_cached` cached SUCCESS only (`RXT_LS_OUT`
  "unset/stale on failure" by its own header comment), so a genuinely
  unparseable file was re-invoked once per caller — the entry-set
  discovery walk, the closure-expansion walk, and the main per-file
  loop's own cache-miss PLUS a now-redundant second call just to fetch
  the diagnostic text for its failure message — 4 real `pcrec
  --list-source` invocations per failing file instead of 1. Fixed by
  caching the FAILURE (and its diagnostic text) the same as a success;
  the main loop's redundant retry call is now dead code and removed.
  MEASURED directly with a `CALLLOG` wrapper (the same mechanism C0a
  itself uses): 39 → 24 calls for 24 head-bearing files, exactly 1:1.

**Re-validated**: `bash tests/rxtsource/run_rxtsource_tests.sh` (standalone)
and `make test-rxtsource CC=gcc-16` — **269 passed / 0 failed / 1
recorded** (the pre-existing darwin python-version-skew `RECORD` line,
unrelated, documented elsewhere in this file's own history).

## Not fixed, flagged only (out of scope for this triage)

- `tests/mech/sabotages/S203_rxt_head_detector_fires.sh`'s `SAB_DESC`
  prose still says "179"/"210" corpus files — stale descriptive text
  (not a functional assertion; mech scores DETECTED/UNDETECTED, never
  this string). Worth a future drive-by fix, not touched here — out of
  this triage's `test-corpus`/`test-codegen`/`test-rxtsource` scope and
  `make mech` was not run by this lane.
- The underlying analyzer/pcrec dialect gap (golden's "bigram" bundle
  directive, its looser provenance rule) is real design/implementation
  work belonging to whichever lane teaches `pcrec --list-source` that
  dialect — not this triage's charter, and explicitly out of scope per
  the lead's own framing ("fixing the analyzer/pcrec gap is not this
  triage's job").

## Commits on `lane/tri86`

1. `b97caecf` — test-codegen: `ABI_EXPECT` re-pin + backtick/`$` escape fix
2. `0058b93c` — run.sh: `--dump`-scoped P-C2 declaration gate + `golden/`
   path exclusion + `rxt_list_source_cached` negative-caching fix
3. `037d2baa` — rxtsource: census/RUNSH/`C3_CRASHED_HEADBEARING` re-pins,
   leg A/leg B tolerance re-derivation
4. `9e41fa03` — `docs/dev/artifact_size_log.tsv` refresh (test-corpus
   byproduct)
5. `1b5a00bc` — `tests/harness/CLAUDE.md` dated addendum

## Validation summary (all standalone + section-target runs, this box)

| section | before | after |
|---|---|---|
| `make test-corpus` | 23 failed (9 box-load timeouts + rest golden-related) | **0 failed**, 29385/29385 |
| `make test-codegen` | `run_codegen_tests.sh` crashed the whole script | **11/12 scripts pass**; sole red is the accepted darwin `nm arm_a.o` probe |
| `make test-rxtsource` | multiple FAILs (census, leg B, C0a, leg A, C3) | **269 passed / 0 failed / 1 pre-existing RECORD** |

`make strict CC=gcc-16`: clean (no `src/`/`cli/`/`lib/` touched by this
lane — every change is under `tests/`).

Not run by this lane: `make mech`, `make san`, `make test-axes`, the full
`make test` (out of this triage's scoped three sections; land85's own
chain already validated `make test-findings` and mech rows S329/S311
green at its own tip). The manager's own merge battery is where those
belong per BOILERPLATE.
