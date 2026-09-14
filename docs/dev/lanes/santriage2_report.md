# santriage2 report — san-stage battery, 2026-09-13/14

Battery: `scripts/battery.sh` on merge commit `0b7f4d62`. `san` stage killed
by the manager after 5h with 1 of 35 scripts complete (registry). Read-only
triage; no repo files touched. Scratch artifacts under
`build/battery_20260913_183914/triage/` (gitignored, not committed).

## Headline finding (root cause, applies to all three questions below)

**`ASAN_OPTIONS="detect_leaks=1"` — set unconditionally by the Makefile's
`SAN_ENV` (and identically by the pre-existing `ASAN_ENV` for `make asan`
alone) — makes `build-san/pcrec`, and every GENCFLAGS-sanitized generated
matcher, hang at process exit on this box (Homebrew gcc-16 16.2.0, Darwin
arm64/M1), burning near-100% CPU the whole time it is alive, until an
external timeout/watchdog kills it.** This is a Darwin+gcc-16 toolchain
calibration defect (LeakSanitizer's Darwin support in GCC's libsanitizer),
not a regression introduced by merge `0b7f4d62`, and it is orthogonal to the
merge's own territory (rxt/schema/dispatch). It is also NOT specific to the
new combined `san` target — `make asan`'s own `ASAN_ENV` carries the exact
same `ASAN_OPTIONS="detect_leaks=1"`, so this bug has been latent and would
fire on `make asan` too, any time it is actually run on this box.

Reproduction (isolated, no battery running, `build/battery_20260913_183914/triage/`):

| call | env | result |
|---|---|---|
| `build-san/pcrec -p rx -o f.c -- '.'` | none | 0.075s, rc=0 |
| `build-san/pcrec -p rx -o f.c -- '.'` | `ASAN_OPTIONS=detect_leaks=1` | rc=124 at every timeout tried (10s, 15s, 30s, 180s, 240s) — **never completes on its own**; `user+sys ≈ wall` (e.g. 240s wall / 2m21s user / 1m37s sys) — actively spinning, not blocked |
| `build-san/pcrec --list-schema` | `ASAN_OPTIONS=detect_leaks=1` | same hang |
| `build-san/pcrec --probe-ask verdict -- '\g<01>'` | `ASAN_OPTIONS=detect_leaks=1` | same hang (3/3 trials, 20.04s each) |
| `LSAN_OPTIONS=""` alone (no ASAN_OPTIONS) | | 0.071s, rc=0 — **fine** |
| `ASAN_OPTIONS=detect_leaks=0` | | 0.071s, rc=0 — **fine** |
| a GENCFLAGS-sanitized generated matcher, run directly (`t '.'`) | none | prints `match 0 1`, 0.449s, rc=0 |
| same matcher binary | `ASAN_OPTIONS=detect_leaks=1` | prints `match 0 1` (correct answer computed and printed fine), then hangs at exit — 15s wall, rc=124, `user+sys≈wall` |

So the effect is isolated to exactly one knob (`detect_leaks=1`), it affects
BOTH axes the san battery instruments (the pcrec compiler binary itself and
every GENCFLAGS-compiled generated matcher when run), and the hung process
has already computed and printed its correct answer before the hang — the
hang is purely in the sanitizer's exit-time leak scan, not in pcrec's own
logic. In back-to-back trials in my (idle, non-contended) triage session the
hang was highly reproducible for both heavyweight (full compile) and
lightweight (`--probe-ask`) invocations alike — i.e., it did not look
allocation-volume-gated. I could not further characterize *why* GCC's LSan
implementation behaves this way on Darwin/arm64 (likely candidate: LSan's
stop-the-world thread/heap enumeration relies on OS facilities GCC's
libsanitizer fork implements for Linux only — Apple's own clang refuses
`-fsanitize=leak` outright on Darwin with a diagnostic; GCC does not gate it
at compile time, so it silently produces a binary whose leak-check hangs at
runtime instead) — that root-causing is beyond this triage's scope and
doesn't change the actionable finding.

## Q1 — the reject-stage red (614 FAILs, "irreplaceable checks are gone")

**Verdict: darwin/gcc-16 toolchain-calibration artifact. NOT a regression
from the merge.**

`tests/reject/run_reject_tests.sh` wraps every one of its ~800 cases in
`"$TIMEOUT_BIN" 60 "$PCREC" -p rx -o "$WORKDIR/..." -- "$pat"` — a single,
uniform invocation shape, never touching the merge's territory
(`src/parse/rxt_source.c`, `rxt_schema.def`, `schema_dump.c`,
`--list-schema`) differently per case. All 614 FAIL lines in `2.out` are
`exit 124 (crash or timeout)` / `exit 124 — timed out or was killed` — every
single failure is the SAME failure mode, uniformly, across both `accept` and
`reject` cases, trivial and complex patterns alike (`.` and `a|b` fail
exactly like `\p{Script=Latin}` and `(*LIMIT_MATCH=4294967290)`). That
uniformity is the tell: this is not a construct-specific regression, it's
every invocation of `build-san/pcrec` under this script's environment hitting
the same 60s wall.

Direct reproduction: `timeout 60 build-san/pcrec -p rx -o f.c -- '.'` (the
EXACT shape of case "accept '.': exit 124") — with the san stage's
`ASAN_OPTIONS="detect_leaks=1"` exported (as `make san` does for the whole
stage), this hangs and is killed at 60s, rc=124, reproducing the exact
failure line verbatim. Without that one env var, the identical command
returns in 0.075s. This is a complete, deterministic reproduction of the
row's failure mode using nothing from the merge's changed files.

The "irreplaceable checks are gone" message is downstream bookkeeping: the
census that certifies which hand-written rows exist reads its population
from the run's PASS/FAIL results, and a row whose invocation timed out never
produced a result row, so the irreplaceability census correctly reports it
as missing. The census mechanism is doing its job correctly; its input
(614/614 timeouts) is the actual defect.

**Nothing in this failure touches rxt/schema/dump surfaces specifically** —
`--list-schema` alone (no pattern, no rxt_source.c dispatch path at all)
reproduces the identical hang, so there is no reason to suspect the merge's
`rxt_source.c` dispatch rewrite, `rxt_schema.def`, or `schema_dump.c`.

## Q2 — the CLI watchdog kill (1.out line 772, and the `\g<01>` case at 810)

**Verdict: same root cause. Not pattern-dependent in kind, though the
OBSERVED hit rate in this run was partial (not 100%), unlike reject's.**

Line 772's watchdog line reads:
`watchdog: run_cli_tests.sh:772: CPU limit exceeded (limit 60s of CPU time) (TERM->KILL), peak rss 16480 kB`
immediately following `FAIL: case10: --probe-ask verdict runs / expected: 0 /
actual: 124`. K37 (`tests/lib/gen_timeout.sh` / `tests/lib/CLAUDE.md`) routes
call-bearing patterns (the `\g<01>` family) through `scripts/watchdog` with
its own **CPU-time** cap (60s) rather than the plain `TIMEOUT_BIN` wall wrap —
so a spinning/CPU-burning hang like this one is exactly the shape that trips
a CPU-time watchdog, and does so reliably: my reproduction of
`build-san/pcrec --probe-ask verdict -- '\g<01>'` under
`ASAN_OPTIONS=detect_leaks=1` burned ~11.8s user + 8.2s sys of every 20s wall
budget tried (3/3 trials) — i.e., real CPU consumption, not an idle block,
consistent with a CPU-limit watchdog firing at 60s of accumulated CPU exactly
as the log shows.

Cost comparison, `build/pcrec` (unsanitized) vs `build-san/pcrec` (sanitized)
on the SAME invocation:

| invocation | env | result |
|---|---|---|
| `build/pcrec --probe-ask verdict -- '\g<01>'`-equivalent full compiles (unsanitized) | none | sub-second, well inside the plain-axis 20s pcrec_timeout_secs budget (per `gen_timeout.sh`'s own measured baseline: 0.38s plain worst case in the whole corpus) |
| `build-san/pcrec --probe-ask verdict -- '\g<01>'` | `ASAN_OPTIONS=detect_leaks=1` | never completes; killed at every budget tried (10s/15s/20s), ~59% CPU-to-wall ratio the whole time |

I could not derive a clean "multiplier" (Nx slower) for this row because in
my reproduction the sanitized call did not complete at all within any budget
I tried (up to 240s on a different case) — the honest statement is "infinite
relative to the plain baseline," not "N times slower." That said, the ACTUAL
battery log (`1.out`, 201 buffered lines, a partial capture since cli was
still running at kill time) shows a MIXED outcome, not a uniform hang: 62
`PASS` lines against 39 `FAIL` lines (all FAIL lines attributable to
124/watchdog-kill) in the visible sample — roughly 39% observed failure rate
in that slice, not the 100% reject stage showed. My own isolated
reproduction, run repeatedly outside the battery (idle box, no other san
scripts concurrently active), hit the hang on every trial I tried, including
supposedly-lightweight `--probe-ask` calls that in the real log sometimes
passed. I cannot fully explain this mismatch from triage alone — it is
consistent with either (a) some nondeterminism/raciness in whatever GCC's
LSan does on Darwin at exit (sometimes it resolves fast, sometimes it
spins), or (b) ambient conditions during the real 4-concurrent-script run
differing from my quiet single-process reproduction in a way that changes
the odds. Either way, the FAILURE MECHANISM itself (a CPU-burning hang under
`detect_leaks=1`, unrelated to pattern content) is the same, cleanly
reproduced fact in both places; only the hit RATE differs and is unexplained.

## Q3 — the harness pace (0.out, 0 bytes after 5h)

**Verdict: fully explained by the same root cause; the estimated true wall
cost of a full san-axis harness run under this bug is on the order of DAYS,
not the documented 110-minute historical baseline — so 5h making no visible
progress is expected, not merely "slow."**

Two measured facts combine:

1. **Both halves of every harness case pay the hang.** Per case,
   `tests/harness/run.sh` does (at minimum) one `pcrec` compile invocation
   (`pcrec_run`/`pcrec_timeout_secs()`, SAN axis = 60s budget) AND, for each
   `m`/`n`/`ms`/`ns` line, one execution of the resulting GENCFLAGS-sanitized
   matcher (`gen_run`/`gen_run_secs`, SAN axis = 60s budget per
   `tests/lib/CLAUDE.md`). I directly reproduced the hang on BOTH steps for
   the same trivial pattern (`\.`): the pcrec compile step hangs to its
   budget, and — separately — running the resulting matcher binary ALSO
   hangs to its budget after printing the correct `match 0 1` line first.
   So a case that would normally be sub-second-times-two now costs up to
   ~120s (60+60) if both halves hang, or 60s if only one does.

2. **Scale**: excluding `tests/known_fail/` (deliberately excluded from
   `run.sh`'s default run), the corpus is **209 `.rxt` files, 3,933
   `pattern` blocks, 24,227 `m`/`n`/`ms`/`ns` lines** (counted directly:
   `find tests -name '*.rxt' ! -path 'tests/known_fail/*'`, then
   `grep -c '^pattern'` / `grep -cE '^(m|n|ms|ns) '` summed over that list).

Even using the LOWER of the two observed hang rates in this triage (reject's
compile-only calls: 100%; cli's mixed sample: ~39% failed/124, though my own
reproduction of similar-shaped calls hung 100% of the time in isolation) as
a floor, and taking pcrec's own compile step as reliably hanging (matches
reject's measured 100% on the identical invocation shape) while assuming
only ~40% of matcher-run invocations hang (cli's observed rate, generously
optimistic given my own isolated reproduction hung on every trial):

    3,933 compiles  x 100% x 60s  = 235,980s  (~65.6 CPU-hours)
    24,227 runs     x  40% x 60s  = 581,448s  (~161.5 CPU-hours)
    total serial cost            ≈ 817,428s  (~227 CPU-hours, ~9.5 CPU-days)

`tests/harness/run.sh` dispatches PROCS workers one-per-FILE (San's
`run_san_group.sh` sets `PROCS=3` for harness specifically, per the shape
line in `san.log`: "35 scripts, up to 4 concurrent, PROCS=3 per script").
Dividing the serial estimate by 3 concurrent file-workers:
**≈227/3 ≈ 76 wall-hours ≈ 3.2 wall-days** for the harness stage alone to
clear the corpus under this bug — before even reaching the 34 other san
scripts (many of which, like `tests/reject/`, are 100%-hang cases per their
own measured rate, and would push the true total materially higher than
this floor). This dwarfs `run_san_group.sh`'s own documented ~110-minute
full-battery baseline by roughly two orders of magnitude, and is fully
consistent with the observed state: `tests/base/escapes.rxt` (a modest
28-pattern, ~35-`m`/`n`-line file — small even by this corpus's standards)
still in flight after 5 hours, with the harness's own `0.out` at 0 bytes
because `run.sh`'s PROCS>1 path only prints a file's tally once that WHOLE
file's worker finishes (no per-case progress line) — consistent with the
worker genuinely still grinding through that one file's cases, each paying
up to ~120s, not with the harness being stuck/deadlocked.

## Q4 — verdict per artifact

| artifact | verdict | evidence |
|---|---|---|
| **san stage overall (killed at 5h, 1/35 done)** | darwin/gcc-16 calibration artifact | root-cause reproduction above: `ASAN_OPTIONS=detect_leaks=1` hangs `build-san/pcrec` and every sanitized generated matcher at exit on this box, independent of pattern or the merge's changed files |
| **reject stage (614/614 FAIL, "irreplaceable checks are gone")** | darwin/gcc-16 calibration artifact | 100% of failures are uniform exit-124, reproduced verbatim on trivial `accept '.'`/`reject` cases outside the merge's territory; `--list-schema` alone (no rxt dispatch path) reproduces the identical hang |
| **cli stage (watchdog CPU-limit kill at :772, mixed PASS/FAIL)** | darwin/gcc-16 calibration artifact, same mechanism, un-explained partial hit rate | CPU-burning hang reproduced on the identical `--probe-ask`/`\g<01>` invocation shape; real log's ~39% observed failure rate in the visible sample is lower than my 100%-in-isolation reproduction rate — mechanism confirmed, exact hit-rate driver not determined in this triage |
| **harness stage (0 bytes after 5h, stuck on escapes.rxt)** | darwin/gcc-16 calibration artifact | structural estimate (209 files / 3,933 patterns / 24,227 match lines, both compile- and run-side hangs measured directly) puts a full clearance at ~3+ wall-days under PROCS=3, two orders of magnitude past the ~110-minute historical baseline — "no progress in 5h" is the expected shape of this bug, not evidence of anything merge-specific |
| **registry stage (3.out: 225/0, complete text, no `.rc` file)** | UNRESOLVED, flagged for the manager | registry's own scripts (`compliance_section.py`, `axes_registry_check.sh`, `limits_check.sh`) do invoke `$PCREC`, and I reproduced the identical `detect_leaks=1` hang on `build-san/pcrec --list-schema` (registry's own kind of call) in isolation — so registry's calls SHOULD be vulnerable to the same bug, yet its buffered output shows a clean, complete 225/0 summary. I could not reconcile this within the triage's scope: either registry's actual `$PCREC` calls are fewer/shaped differently than I assumed (not independently verified against its full script text beyond the four invocation lines I grepped), or the same hit-rate non-determinism noted in Q2 happened to favor it every time in this run. The missing `.rc` file is `run_san_group.sh`'s own artifact: it writes `<dir>/<k>.rc` only once its measurement of that script's `$?` completes and is captured by the harness's `wait`/dispatch bookkeeping (`tests/lib/run_san_group.sh:100`) — a script whose OWN process had exited with a captured status but whose `.rc` write raced against the manager's kill-time copy-out (or whose registry script, despite printing "== Summary ==", was still inside a LATER shell step after that print — e.g. its own trailing `axes_registry_check.sh`/`limits_check.sh` calls, which run AFTER the printed compliance-section summary per the file's line order at :392/:554 — and got killed before writing its own final exit status) is the more likely reading than "the script cleanly finished and the harness merely forgot to record it." Recommend the manager re-run registry stage alone with `detect_leaks=0` to see whether the discrepancy is this timing race or something registry-specific.

## Recommendations (not decisions — the manager/Frank rule these)

1. **Immediate unblock for any darwin san/asan run**: override
   `ASAN_OPTIONS` to `detect_leaks=0` (or simply unset it) for this box until
   the underlying GCC/Darwin LSan issue is understood or a working
   combination is found. Confirmed fix in isolation: identical calls that
   hang under `detect_leaks=1` return in <0.1s under `detect_leaks=0` or
   unset, with the rest of ASan/UBSan instrumentation presumably still
   active (not verified in this triage — worth a positive-control check that
   real ASan/UBSan findings still fire with leak detection off).
   D26/D45-style: this is a budget-model input (the SAN axis's calibration
   assumed sanitizer overhead is a multiplier on plain cost, per
   `gen_timeout.sh`'s own header — "-O1 -fsanitize=address,undefined,leak
   (2.2s plain)... 1.15x the budget" — a measurement almost certainly taken
   on Linux; that assumption is false on this Darwin/gcc-16 combination and
   the budgets built on it (`PCRECTIMEOUT_SAN=60`, `GENCPU_SAN=200`,
   `GENTIMEOUT_SAN=180`) cannot be reached by raising them further, since
   the hang does not resolve on its own even at 240s.
2. Once unblocked, a targeted re-run of just `tests/reject/` and a handful of
   `tests/base/*.rxt` files under `SAN_ENV` with `ASAN_OPTIONS=detect_leaks=0`
   would give a clean read on whether ASan+UBSan alone (without LSan) behaves
   at the ~1-4x overhead `gen_timeout.sh`'s existing budgets assume, which is
   the number that should drive any budget re-calibration.
3. The registry-stage discrepancy (Q4's UNRESOLVED row) is worth a direct,
   short re-run in isolation before trusting its "225/0" as a real green —
   if the `.rc`-write race reading is right, a re-run under the SAME
   (buggy) env might not reproduce a clean pass at all.

## Files

- Report: `/Users/fdicostanzo/pcrec/build/battery_20260913_183914/triage/santriage2_report.md` (this file)
- Reproduction scratch (not committed): `/Users/fdicostanzo/pcrec/build/battery_20260913_183914/triage/` — `genA.c`..`genG.c`, `matcher.c`/`matcher`, `s1..s5.c`, `c1..c12.c`/`.log`, `conc_times.log`
- Source logs read: `build/battery_20260913_183914/{trailer.log,san.log,san_buffer/{0,1,2,3}.out,san_buffer/2.rc}`
- Key source files cited: `Makefile:1225-1320` (`ASAN_ENV`/`SAN_ENV`/`asan:`/`san:` targets), `tests/lib/gen_timeout.sh` (budget model + its own calibration citations), `tests/lib/run_san_group.sh` (PROCS=3 shape, 110-min historical baseline comment), `tests/reject/run_reject_tests.sh:258` (the reproduced invocation shape), `tests/cli/run_cli_tests.sh` (case10 probe-ask/count-groups block), `tests/registry/run_registry_tests.sh:148-162,392,554`
