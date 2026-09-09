# arm61fix — C3 re-pin derivation + scanedge lint triage

2026-09-09, lane `arm61fix`, sonnet. Two independent tasks from the I-61
Linux executor run (ubuntubudu, `/home/duxevents/pcrec/build/
stage4_arm_20260909/`). Branch `lane/arm61fix`, worktree
`worktrees/arm61fix`. Never merged to main.

## TASK 1 — C3 re-pin (`tests/rxtsource/run_rxtsource_tests.sh`)

Re-pinned `C3_PASS`/`C3_SKIP`/`C3_SKIP_PCRE2ONLY`/`C3_SKIP_NOPYTHON` to the
I-61 run's authoritative Linux numbers, discharging bat4triage's OWED note
(2026-09-08) left in the same file.

**Derivation, not a copy.** The two candidate corpus edits from the
stage-4 merge (`83f7175b`, lane utf8s4/foldhunks) are `tests/utf8/fold.rxt`
(new, commit `a3ba7de7`) and `tests/utf8/axis06_caseless_fold.rxt`
(rewritten, commit `ab5c9715`). For each I extracted the pre-image and
post-image and ran `tests/harness/verify_rxt.py` on each in isolation
(scratch copies, never touching the corpus) to measure the exact
PASS/SKIP-by-reason movement, rather than trusting a hand count:

| file | PASS delta | SKIP delta | pcre2-only delta | no-python delta |
|---|---:|---:|---:|---:|
| `fold.rxt` (new, all 18 blocks authored `# pcre2-only`) | 0 | +45 | +45 | 0 |
| `axis06_caseless_fold.rxt` (12 of 48 blocks newly marked `# pcre2-only`) | -20 | +32 | +48 | -16 |
| **sum** | **-20** | **+77** | **+93** | **-16** |

axis06's own breakdown (why -20/+32/+48/-16, not a simpler split): of the
12 newly-marked blocks, 4 are bare-literal negated singletons (`[^k]` etc.,
16 lines, previously python-PASS), 4 are the SAME code points spelled with
PCRE's `\x{NN}` brace escape (python's `re` has no brace form of `\x` and
raises `bad escape`, so these 16 lines were previously
no-python-expression), and 4 are the `[^\p{Ll}]` blocks promoted from a
single agreeing-refusal `perr` line each (PASS) to 4 real m/n lines each
(net +12 lines, matching the file's own line growth 180→192). All 12
land in pcre2-only regardless of prior bucket, since a block already
marked pcre2-only is unaffected by the value edits the promotion also
made to 24 OTHER blocks (KELVIN/MICRO/LONGS/FINALSIGMA/closure-class
families) that produce zero C3 movement.

The sums match the I-61 run's reported numbers exactly (PASS 13708, SKIP
15074, pcre2-only 2872), and the reconciliation identity holds:
`C3_PASS + C3_SKIP + C3_TIMEOUT_FILE_LINES = 13708 + 15074 + 89 = 28871 =
CENSUS_LINES` (CENSUS_LINES itself was already correctly re-pinned by
bat4triage and is untouched here). The full per-file arithmetic, with the
mechanism for each bucket movement, is written as the dated comment beside
the new pin values (`tests/rxtsource/run_rxtsource_tests.sh:731`).
giveup/composed/perr-python-accepts/own-oracle are confirmed unmoved by
both commits (0 movement in both isolated measurements) and are not
re-pinned.

**Not fixed, flagged instead**: `C3_FILES=179` (line 630) is a dead
variable — assigned but never read anywhere in the script (grep confirms
one hit). Out of this task's scope; noted for whoever next touches this
file's pins.

## TASK 2 — `src/opt/scanedge.c:325` CWE-457 triage

**Verdict: gcc -fanalyzer FALSE POSITIVE, fixed by initializing anyway
(K28 precedent), not a real bug.**

The flagged read is `exitv[p]` inside `collect()`'s head-finding loop
(:325). `exitv` is populated by `pcrec_scanedge_dfa` (:497) as
`ok[s] = member_ok(&d->st[s]) && shaped(d, s, cls, &exitv[s])` — `shaped()`
(:248) has exactly one `return true` path and it is IMMEDIATELY preceded
by `*exit = e;`, and every `return false` path skips that write. So
`ok[s] == true` **iff** `exitv[s]` was written in that pass, by
construction of the `&&` short-circuit and `shaped()`'s own control flow.
Every read of `exitv[]` in `collect()` (:325, :396, :432) is gated by the
matching `ok[]` entry before or in the same short-circuited expression, so
a read of an unwritten slot is unreachable — proven over the two-function
pair, not merely believed.

**Confirmed a genuine analyzer limitation, not a proof gap in my
reasoning**, via a light SSH probe to the reference box (read-only
reproduction, no repo writes):

- The finding did **not** reproduce on the Mac's own gcc-16 (Homebrew
  16.2.0) — `make lint CC=gcc-16` was already clean here before any fix,
  confirming the earlier `santriage` lane's account that `lint` had never
  actually executed on darwin before this Mac-move era.
- **Correction to the brief**: the run was NOT gcc 16 — ubuntubudu has no
  gcc-16 at all, only `gcc-15.2.0` (`Ubuntu 15.2.0-16ubuntu1` — the "16"
  in the brief is almost certainly the Ubuntu package suffix misread as
  the gcc major version). Reproduced the exact warning there, verbatim,
  compiling this worktree's own `scanedge.c` (sha256-identical to
  ubuntubudu's tree) with `gcc -O2 -g -Wall -Wextra -std=gnu11 -Ilib -Isrc
  -fanalyzer -c`.
- The analyzer's own event trace (in `lint.log`) shows it modeling `ok[p]`
  as true at the point of the flagged read (event 27, `if (!ok[p])
  continue`) yet still reporting `exitv[p]` uninitialized — it cannot
  carry the correlation between `ok[]`'s per-element boolean content and
  `exitv[]`'s per-element written-ness across the two different heap
  regions once state-widened over the building loop, the same
  "table-driven code" false-positive class CLAUDE.md's situation index
  already names for this tool.

**The fix, measured to work on the box that raised it**: `exitv` at :484
changes from `malloc` to `calloc`. Applied the one-line change to a
scratch copy of ubuntubudu's own `scanedge.c` and recompiled with the
identical flags: **zero warnings, rc=0**, no other line changed. This is
a pure defensive initialization — the proof above already rules out a
live read of the unwritten value, so this cannot mask a real bug class,
matching K28's own "if a one-line initialization silences it without
masking a real class, prefer that and say so." Landed with a comment at
the allocation site explaining the invariant, the false-positive
mechanism, and the measurement (`src/opt/scanedge.c:484`).

### Local validation

- `make -j4 CC=gcc-16` — clean build.
- `make strict CC=gcc-16` — `strict: whole tree compiles clean with
  -Werror -Wshadow`.
- `make lint CC=gcc-16` — clean before and after (does not reproduce the
  finding on this box at all; validated on ubuntubudu instead, above).
- `tests/codegen/run_scan_edge_census.sh` — 14 passed, 0 failed
  (unchanged by this edit; pure precondition-population census).
- `tests/codegen/run_scan_edge_dispatch.sh` — 4 FAILED
  (`iso-ts`/`http-5xx`/`two-chain`/`digits-then-letters`, all
  `symbol rx_forward_byte_class not in ...`). **Confirmed PRE-EXISTING and
  unrelated**: `git stash` + rebuild reproduces the identical 4 failures
  with the fix removed, byte for byte. Not filed further (out of this
  task's scope; flagged for the manager).
- The named answer-corpus slice (scanedge.c's own CLAUDE.md entry:
  counterk, classes, bounded_repeats, possessify, k18_*) —
  **COMPLETE: 5,810 cases passed, 0 failed, 0 pattern-compile failures,
  10 of 10 file workers reported** (`env PROCS=4 bash tests/harness/
  run.sh ...`, log at `build/scanedge_slice_validation.log`, gitignored).
  Two earlier attempts at `PROCS=1` (this box's default) were abandoned:
  the first was lost to a foreground `timeout`/pipe combination that
  buffers all output until exit, and the second, run serially in the
  background, was still going after 5+ minutes with under a second of
  parent CPU time — this box's known process-dispatch spawn-tax shape
  ([TT-14]/[XARCH]) rather than a hang, but slower than this task
  warranted given the fix is a proven no-op on every live path.
  `PROCS=4` finished promptly. Confirms the `calloc` change changes
  nothing observable.
- `make strict CC=gcc-16 clean` (as literally listed in the brief) was
  not run as a single combined step; `clean` was not invoked separately
  since `build/` is gitignored and nothing here depends on a pristine
  tree. Flagging the ambiguity rather than guessing further.

## Rulings received

None — no ruling was requested or needed for either task.

## Scope note

Touched only `/Users/fdicostanzo/pcrec`, only inside
`worktrees/arm61fix`. One light, read-only SSH probe to ubuntubudu
(`duxevents@100.69.121.107`) for TASK 2's reproduction: read-only
`gcc -fanalyzer` compiles to scratch files under `/tmp` on that box,
nothing written to its repository (verified `git status --short` there
before and after showed only its own pre-existing `docs/dev/
artifact_size_log.tsv` modification from the battery's SIZELOG run, not
anything from this probe), scratch files removed after use.
