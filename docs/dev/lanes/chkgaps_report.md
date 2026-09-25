# chkgaps — closing four check-design gaps (2026-09-25, lane chkgaps, sonnet)

Branch `lane/chkgaps` from main `1a2504e1`. Brief: close four check-design
gaps found 2026-09-25, each with a sabotage row proving the check can go
red, plus a trivial comment fix in `src/parse/definitions.c`.

## Gap 4 — the VM class-fold shape had no agreement check against fold.c

`src/gen/emit_vm.c`'s `vm_cls_shape`/`vm_cls_test` (~1633/~1655) recognize
and emit the ASCII-fold class compare with a hardcoded condition that has
no tie to `pcrec_ascii_fold` (`src/core/fold.c`), the table this project
otherwise treats as ground truth (`tests/backrefs/fold_agreement_check.c`).
S228 already proves the recognizer's conjuncts matter but reaches only 2 of
26 real pairs by hand and never the EMITTED COMPARE line independent of the
recognizer.

Added `tests/codegen/fold_pairs_dump.c` (derives the real 26 fold pairs and
6 near-miss punctuation pairs straight from `pcrec_ascii_fold`, never
hand-typed) and `tests/codegen/run_cls_fold_agreement.sh` (compiles, links
and RUNS a real `--emit-main` artifact per pair, reading exit codes).
Floors are half the measured population (13/3), never the number itself.
163 checks, wired into `make test-codegen`'s group and into `tests/mech` as
a new `clsfold` arm.

**Sabotage S275** shifts the emitted compare's own constant (`hi` -> `lo`)
— the direction S228 cannot reach, since S228 only ever touches the
recognizer. MEASURED DETECTED: `clsfold:78fail/85pass`.

## Gap 3 — mech's `encoding` arm had no clean-tree baseline

`run_encoding_checks.sh` is opt-in and rides no `TEST_SECTIONS` entry, so
it went standing-red on main for two weeks (D118 to enctriage's fix) with
nothing to notice, and the mech `encoding` arm scored each row's ABSOLUTE
`checks failed` count — so S229/S-U8 read DETECTED whatever their own
plant did for the whole window (`docs/dev/lanes/enctriage_report.md`
finding 4).

`ENCODING_BASELINE_FAIL` is now computed once per matrix run (same lazy,
SHA-cached shape `CLEAN_TREE` already uses) and subtracted from each row's
own count before `score_arm` sees it — a sabotage is DETECTED on this arm
only if it adds a failure the clean tree does not already have. An
unscrapeable baseline is a hard FATAL for the whole run.

**Re-validated S229** end to end: `encoding baseline: 0 failure(s) measured
on the clean tree` (the tree is currently green, so this run reproduces the
pre-existing DETECTED verdict without regression) — `reach:ok(1/1)`,
`corpus:1fail/69pass,encoding:1fail/9pass`, verdict DETECTED, 0
unexpected/undetected/anomalies.

## Gap 2 — run_axes.sh: a one-sided give-up was folded into "never a failure"

`dump_diff.awk`'s `BUDGET` bucket folded together two shapes: a budget
BOUNDARY moving while both sides still give up (licensed by `tuning.md`
§2.5) and an answer<->give-up TRANSITION where exactly one side gives
up/times out. The second was never a failure — exactly K64's own shape,
and `docs/dev/learnings.md` §3's filed candidate ("count give-up
TRANSITIONS as their own population").

Split the bucket: `BUDGET` stays "both sides give up"; a new `GIVEUP1`
bucket is "exactly one side does". `run_axes.sh` treats every `GIVEUP1`
case as a FAILURE unless the axis names the exact `(flags, file:line)` pair
in a new `GIVEUP1_ALLOWANCE` manifest — derived, never a blanket count (K35:
a count ceiling disarms itself the moment a different case moves under it).
The manifest is EMPTY today: no legitimate one-sided give-up has ever been
measured separately from the two-sided bucket.

`run_ksweep.sh` (`dump_diff.awk`'s other consumer) is updated to keep
excluding BOTH buckets — its own §6.1 measurement already documents
K-dependent one-sided flips as a real, expected phenomenon — including its
§3.3a declared-capacity-floor rule, which previously scanned only `BUDGET`
rows and would otherwise have silently stopped seeing exactly the
one-sided case that rule cares about most.

**Smoke-validated** on small corpus slices for both scripts (`giveup1=0`
throughout, no regressions, `run_axes.sh tests/base/literals.rxt` and
`run_ksweep.sh tests/base/literals.rxt` both green).

**OWED**: the full `make test-axes` (opt-in, multi-hour) — this is a policy
change to what that battery scores (a case that used to pass silently as
"budget-bound" can now fail), and the real corpus's `GIVEUP1` population is
unmeasured. Ask the manager for the heavy slot before running it; the first
run's own `GIVEUP1_ALLOWANCE` entries (if any legitimate cases surface)
are a follow-up commit, not a blocker to merging this mechanism.

## Gap 1 — answerdiff (and everything else) missed K64 by running AUTO-route only

Two parts, since K64's real fix is not merged and the check-design fix must
not depend on it landing.

**Part 1 — standing population reach.** `admitimpl_answerdiff.py` (the
`[OPT-PRECHECK-ADMIT]` REF-vs-TIP differential) ran AUTO-route arms only,
and it is a one-shot lane instrument nothing re-runs (k64fix's own report).
Added `tests/known_fail/k64_precheck_forced_vm.rxt`: PCRE2's real
expectations (NOMATCH) on 4 subjects lacking the necessary byte, under a
forced `--engine=vm` + tiny compiled `--step-budget=10000` build. The
current (unfixed) compiler gives up instead (`PCREC_ERR_STEPS`), so the
file's own cells FAIL under `tests/harness/run.sh` — exactly the
known-fail ratchet's "still failing, expected" state (verified: 2
passed/4 failed, ratchet reports "still failing", rc 0). This is the
first standing, always-run reach into the forced-VM admission population.
Re-pinned `tests/rxtsource/run_rxtsource_tests.sh`'s corpus census
(217/3996/29119; RUNSH_* unchanged since the file is under
`tests/known_fail/`) — verified live, 214/0 checks pass, denominators
reconcile.

**Part 2 — a real, sabotage-provable answer check independent of K64's own
fix.** Added `tests/codegen/run_prechecks.sh` §5.6: an UNANCHORED VM-route
witness (`([a-zA-Z0-9._%+-]+)+@`, no `^`) that G2 correctly admits with the
pre-check EMITTED today (`req_route_one_attempt`'s own `start_anchor`
conjunct already excludes it) — compiled with `--emit-main` and RUN, not
merely stamp-checked. This is deliberately NOT K64's own population (an
anchored route); it is the same defect class one conjunct further up, so
it needs no dependency on K64's fix.

**Sabotage S276** drops the `start_anchor` conjunct entirely (every VM
route admitted, anchored or not) — the generalized form of K64's own
missing-linearity check. MEASURED DETECTED: `prechecks:8fail/244pass`,
§5.6's own witness flipping `RX_REQ_WHY` from `"emitted"` to `"one-attempt"`
and its no-`@` subject from a fast NOMATCH (exit 1) to a step give-up.

## Trivial fix

`src/parse/definitions.c`'s comment on `pcrec_def_text_cx` cited
`src/parse/mod_backrefs.c`'s "identical `toupper((unsigned char)c)` idiom"
as precedent; that idiom no longer exists there. Re-cited
`src/core/sb.c`'s `pcrec_sb_upper` (same idiom, same kind of host-side,
non-emitted byte). Comment-only, confirmed not in emitted text.

## Validation

- `make -j4 CC=gcc-16 && make strict CC=gcc-16`: clean, throughout.
- `tests/codegen/run_cls_fold_agreement.sh`: 163/0 standalone.
- `tests/codegen/run_prechecks.sh`: 254/0 standalone (was 250/0).
- `tests/known_fail/run_known_fail.sh`: 1 still-failing (expected), 0 now
  passing, rc 0.
- `tests/rxtsource/run_rxtsource_tests.sh`: 214 passed / 0 failed / 1
  recorded (darwin's own pre-existing non-native-pin note), census
  reconciles at 217/3996/29119.
- `tests/axes/run_axes.sh` / `tests/axes/run_ksweep.sh`: smoke-validated on
  small slices (`tests/base/literals.rxt`), `giveup1=0` throughout, no
  regressions. **Full corpus run OWED** (see gap 2 above).
- Sabotage rows, each run solo via `bash tests/mech/run_sabotage_matrix.sh
  S<id>` on a fresh scratch tree from committed HEAD:
  - S275 (gap 4): DETECTED, `clsfold:78fail/85pass`.
  - S276 (gap 1): DETECTED, `prechecks:8fail/244pass`.
  - S229 (gap 3, pre-existing row, re-validated against the new baseline
    mechanism): DETECTED, `corpus:1fail/69pass,encoding:1fail/9pass`, 0
    unexpected/undetected/anomalies.
- `make test-codegen CC=gcc-16`: OWED — a run was in flight at hand-off;
  see the manager's own re-run or this lane's follow-up message for the
  result. (The one pre-existing standing red on this box across every
  prior lane's report is `run_inline_capability.sh`'s darwin
  `nm arm_a.o` issue, unrelated to any of the four gaps.)
- `make test`, `make mech` (full): NOT run — heavy, multi-hour, owed to
  the manager's next battery slot per BOILERPLATE's one-heavy-suite rule.

## Check gaps NOT closed (recorded rather than guessed at)

- The `GIVEUP1_ALLOWANCE` manifest is empty. The first full `make
  test-axes` run may surface real, legitimate one-sided give-ups (an axis
  denial genuinely making a search more expensive without being wrong);
  populating the manifest from that run is real work, not a rubber stamp.
- Gap 1's general mechanism (§5.6/S276) covers the "wrong conjunct on the
  VM arm" shape; it does not cover a hypothetical DFA-route or G1
  (dominance) analogue of the same class, which nothing in this delivery
  measured a population for.

## Rulings received

None — no mid-flight ruling messages arrived during this lane's run.
