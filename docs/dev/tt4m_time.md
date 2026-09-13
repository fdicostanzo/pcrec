# `tt4m_time.md` — [TT-4M-TIME] the clean post-fix `HARNESS_BATCH` timing

2026-09-12/13, lane tt4mtime, measurement only (nothing under
`src/`/`tests/` changed). Answers the row's own charter: a QUIET-BOX,
normal-conditions full `make test` at `HARNESS_BATCH` unset vs `=64
PROCS=8` on the tree AFTER the 2-character-prefix fix (`a2c89c06`, lane
axbatch), since the prior `docs/dev/tt4m_2d_evidence/` runs (README below)
are both upper-bound-understated (measured under concurrent load) and
predate that fix — no clean suite-level number existed before this memo.
The default-on flip decision reads THIS number, not 2d's.

**Headline, up front**: full-suite wall time drops ~9.5% (5124.29s ->
4638.17s), CPU time ~8-10%. That is real and reproducible (both runs'
per-section pass/fail counts are byte-identical — §1), but it is an ORDER
OF MAGNITUDE below [TT-4M]'s own isolated-corpus prototype ratios (4.28x
serial, 18.65x with parallel dispatch). §2 explains the gap: batching can
only touch 2-3 of the suite's 38 sections; the other ~35 pay their full
unbatched cost in both runs regardless. **Also found, not chartered
before this memo**: the suite is NOT green-except-one-red on this tree —
a second, non-batching-related FAIL reproduces identically in both runs
(§1a).

## 1. The timing pair

Both runs on this Mac (`hw.ncpu` 10, GNU Make 3.81 — this box's bundled
`make` predates `-Otarget`/`--output-sync`, so `test:`'s section list runs
in the Makefile's own listed order both times, exactly as
`docs/testing.md`'s "plain `make test` (no `-j`)" note describes; no `-j`
flag on either run, matching the shape `docs/dev/lanes/tt4m3_report.md`'s
own OWED commands specify). Worktree `worktrees/tt4mtime`, branch
`lane/tt4mtime`. The WIP skeleton this memo completes was written at
`818a8711` (main HEAD when the lane started); **the pair itself was run
at `99d2b6fe`** (this branch merged up to main's tree the next day, per
the brief) — §3's re-verification is redone at that pin, not reused from
the skeleton's `818a8711` snapshot. Wall/CPU captured by `/usr/bin/time
-l` wrapping the whole `make test` invocation (one process tree, no
second compile), sequentially, 2026-09-12 23:02 -> 2026-09-13 01:46.

| run | command | load1 before | wall | user CPU | sys CPU | max RSS |
|---|---|---|---|---|---|---|
| 1 (serial) | `make test` | 1.33 | 5124.29s | 3992.98s | 2789.07s | 325,566,464 |
| 2 (batched) | `HARNESS_BATCH=64 PROCS=8 make test` | 1.62 | 4638.17s | 3592.58s | 2639.52s | 325,582,848 |

(load1 figures as captured by the runs' own operator before each launch —
not independently re-derived here, since neither log records it inline.)

Speedup: wall -9.49% (-486.12s, -8.10 min), user CPU -10.03%, sys CPU
-5.36%, combined user+sys CPU -8.11%. Max RSS is IDENTICAL to five
significant figures (+16,384 bytes, noise) — batching does not trade
memory for time here. Two secondary `/usr/bin/time -l` counters
corroborate the mechanism independently of the confound §1a.2 names: page
reclaims drop 792,600,462 -> 762,043,627 (-3.9%), page faults drop
6,401,885 -> 5,576,114 (-12.9%), and involuntary context switches drop
9,036,179 -> 8,167,952 (-9.6%) — all consistent with fewer total OS-level
process/exec operations under batching, independent of whichever way the
PROCS confound (§1a.2) cuts. (The same report's `cycles elapsed` figure
rises 21,649,632 -> 31,297,760 while `instructions retired` barely moves
(+1.1%) — an internally inconsistent pair for a "did more work" story, so
this one counter is treated as unreliable on this platform for a
multi-process tree rather than analyzed further.)

**Count identity, run-to-run**: every one of the 51 `checks passed:`
lines and 49 `checks failed:` lines in the two full logs
(`build/tt4m_run1_serial.log`, `build/tt4m_run2_batch.log`) matches
exactly — summed, `checks passed: 2162` / `checks failed: 1` in BOTH
logs, at the identical line position in each. The corpus-level counters
also match exactly: `cases passed: 28932` / `cases failed: 0` /
`pattern-compile failures (distinct): 0` (test-corpus, both runs) and
`size-log rows: 3478` (both runs, `run_size_log.sh`'s own trailer). The
completion trailer reads `sections ran: 38/38` / `trailer: every section
in TEST_SECTIONS was launched` in both logs — no section silently
dropped under `-k` in either run. This is full count parity: nothing
about batching changed WHAT ran or WHAT it found, only how long it took.

**The chartered baseline does NOT hold as stated**: per BOILERPLATE.md/
the brief, the expected shape was green except the one chartered darwin
`inline_capability` FAIL. Both logs DO carry that FAIL, identically
(`tests/codegen/run_inline_capability.sh`, `run_group[4]` inside
test-codegen: `FAIL: nm could not read arm_a.o (no rx_search symbol) — no
verdict is evidence here`, `make[1]: *** [test-codegen] Error 1`) — but
it is not the ONLY red. See §1a.1.

Raw logs: `build/tt4m_run1_serial.log` (full `make test` output, 4012
lines) / `build/tt4m_run2_batch.log` (3963 lines), each paired with its
`/usr/bin/time -l` trailer in `build/tt4m_run1_time.log` /
`build/tt4m_run2_time.log` — all four in this worktree, uncommitted
(disposition: §7).

### 1a. Anomalies

**1a.1 — A second FAIL, not chartered, identical in both runs.**
Grepping both full logs for `FAIL:`/`Error 1`/`exited [1-9]` turns up
exactly two genuine failures in each, and only two — `test-codegen`
(`inline_capability`, chartered, above) and **`test-anchored-match`**:

```
run_group[1]: bash tests/anchored/run_anchored_diff.sh
...
FAIL: 26 pattern(s) produced emitted C that does not compile under
  -O1 -std=gnu11 -Wall -Wextra -Werror — the anchored body is source
  somebody else compiles
BAD: could not build the two-artifact driver for: (?m)ERROR$
BAD: could not build the two-artifact driver for: ([^c]{1,3})$
BAD: could not build the two-artifact driver for: (a+)$
BAD: could not build the two-artifact driver for: (a{0,4}c$)
BAD: could not build the two-artifact driver for: (a{1,3}?$)
BAD: could not build the two-artifact driver for: ERROR$
...
checks passed: 6
checks failed: 1
run_group: 1/2 scripts passed
```
`make[1]: *** [test-anchored-match] Error 1`. This block is
**byte-for-byte identical** between `tt4m_run1_serial.log:3584-3604` and
`tt4m_run2_batch.log:3535-3555` (same population counts, same six named
patterns, same 26-count) — so it is not batching-flavor-dependent and not
flaky; it is a standing property of the tree at `99d2b6fe`. It is **not
named in `docs/dev/wake.md`**, whose "make test darwin: GREEN except
inline_capability" line was written from a run that was KILLED at 3600s
before reaching `test-thread`/`test-anchored-match` in the section list
(the wake note's own words: "today's kill at exactly 3600s ... all green
to that point"). This is the first FULL, uninterrupted `make test` this
tree has had, and it surfaces a second red the partial run could not have
seen. Diagnosing or fixing the 26-pattern compile failure is out of this
memo's scope (measurement only, per the brief) — it is flagged here as a
FINDING for the manager/Frank to charter, not folded into a footnote.

(Separately, `test-thread` prints a `SKIP: gcc-16 does not support
-fsanitize=thread on this box` message with a raw `ld` error trailing it,
in both logs — this is a documented, graceful skip (`run_thread_tests.sh`
exits 0 on it; no `make[1]: *** [test-thread] Error` line follows either
log), not a third red.)

**1a.2 — `PROCS` was NOT held constant, only `HARNESS_BATCH` was
supposed to be.** Run 1 (`make test`, no `PROCS` set) resolved
`test-corpus`'s file-worker count to the box's `nproc` default: the log
line reads `parallel: 209 of 209 file workers reported (PROCS=10)`. Run 2
(`HARNESS_BATCH=64 PROCS=8 make test`) read `(PROCS=8)` for the same 209
files. So two variables moved between the runs, not one: `HARNESS_BATCH`
0->64 (the thing being measured) AND `test-corpus`'s file-level
parallelism 10->8 workers (an artifact of the brief's literal invocation
string, not a deliberate control). The same `PROCS` value also reaches
every `run_group.sh`-based section via `GROUP_PROCS=${PROCS:-nproc}`, but
`run_group.sh`'s own design note treats any value above 1 as "fully
parallel" for its own (2-8 script) groups, so 8 vs 10 is inconsequential
there — `test-corpus`'s 209-file sweep is the one place the confound could
plausibly bite. Fewer file-level workers should, all else equal, make run
2 SLOWER on the parallelism axis alone — yet run 2 was still faster
overall. That makes the confound a bias AGAINST the batching effect, the
same direction as the load1 residual (§1, table note): if anything, this
memo's ~9.5%/~486s number UNDERSTATES `HARNESS_BATCH`'s isolated
contribution, it does not inflate it.

## 2. The headline, section attribution

The ~486s / ~9.5% wall saving looks small against [TT-4M]'s own
isolated-corpus prototype ratios (4.28x serial, 18.65x with parallel
dispatch; `docs/dev/tt4m_darwin_validation.md`,
`docs/dev/tt4m_step2a_parallel_sizing.md`). Those ratios were measured on
a SINGLE corpus-compiling section in isolation; a full `make test` is 38
sections, and `HARNESS_BATCH` is an env var read by exactly one file
(`tests/harness/run.sh`) — every section that never calls that file pays
its full unbatched cost in BOTH runs, batched or not.

**Which sections can move, by construction**: `docs/dev/tt4m_batch_customers.md`
(re-verified current at `99d2b6fe` in §3) enumerates every real
`tests/harness/run.sh` re-invocation. Setting `HARNESS_BATCH=64` as an
ambient environment variable for the WHOLE `make test` invocation (as run
2 does) reaches every child process transparently — `run.sh` reads it
directly (`HARNESS_BATCH="${HARNESS_BATCH:-0}"`, `tests/harness/run.sh:241`)
with no wrapper script setting or clearing it first (checked: `grep -n
HARNESS_BATCH` on `tests/size/run_size_log.sh`,
`tests/known_fail/run_known_fail.sh`, `tests/rxtsource/run_rxtsource_tests.sh`
— zero hits in all three, so the ambient value passes through unmodified).
Of the 38 `TEST_SECTIONS`, only three route real corpus-scale compiles
through `run.sh` and are therefore live customers for a plain `make test`
run:

- **`test-corpus`** (row 1, `tests/size/run_size_log.sh`) — the WHOLE
  `.rxt` corpus, confirmed identical population both runs
  (`size-log rows: 3478`, `wrote 3478 rows`, both logs) — the largest
  customer by population.
- **`test-rxtsource`** (rows 8/8b, `tests/rxtsource/run_rxtsource_tests.sh`)
  — one `run.sh --dump` per file over the whole corpus plus several
  fixed small-fixture calls — a real but smaller customer.
- **`test-known-fail`** (row 5) — near-empty population by project
  convention (`tests/known_fail/CLAUDE.md`); negligible either way.

`test-axes`/`test-ksweep` (rows 3/4) are opt-in targets, not among the 38
`TEST_SECTIONS` `make test` runs at all, so they are irrelevant to this
pair regardless of their own batching status. `make san`/`ubsan`/`asan`
(row 2) and `make mech` (row 6) are separate opt-in targets, likewise not
part of either of these two runs. `tests/bench/run_bench.sh` (row 9,
timing IS its measurement, batching would corrupt it — by design, never a
candidate) and `tests/fuzz/fuzz.py` (row 10, python, `HARNESS_BATCH` is a
bash-only env var it never reads) are structurally unreachable. Every
other one of the ~35 remaining `TEST_SECTIONS` — the single-process
differential drivers (`assertions`, `rungselect`, `counterk`, `backrefs`,
`mrl`, `altcls`, `anchored-match`, `lookaround`, `recursion`, …), the
fixed-scenario CLI/codegen compiles, and `test-capturediff`'s python fuzz
slice — never call `tests/harness/run.sh` at all (Category 3 of the
customers memo) and should show NO wall-time change from this axis by
construction.

**What the logs can and cannot show directly**: neither log carries
per-section timestamps — `make -k` runs the section list sequentially
with no date-stamped boundary between targets, and the one artifact that
WOULD have given launch-order timestamps (`test_trailer.sh`'s per-section
marker files, touched at each recipe's first line) lives in a `mktemp -d`
directory the `test:` recipe deletes (`rm -rf "$dir"`) at its own end, so
it is gone before either log could be inspected for it. This memo's
section attribution is therefore **structural** (which sections CAN be
touched by the mechanism, established above) rather than a measured
per-section time breakdown. The one incidental exception: `tests/fuzz/
run_capturediff_gate.sh` (inside `test-capturediff`, a Category-2 python
site `HARNESS_BATCH` cannot reach) self-reports its own elapsed time —
`elapsed=28.9s` (run 1) vs `elapsed=29.2s` (run 2), noise-level identical
— which is at least consistent with a section outside the three
customers above being untouched, though one data point does not
generalize.

**Net read**: the whole ~486s/~9.5% saving is attributable to at most
three of 38 sections, over a ~3,200-3,500-pattern corpus. TT-4M's own
per-corpus ratios being real (4.28x-18.65x on an isolated section) is not
in tension with a modest whole-suite number — roughly 35 of 38 sections
pay their full, unbatched cost in both runs regardless of the axis, so a
large win concentrated in 2-3 sections nets a double-digit-percent
whole-suite result rather than anything close to the isolated ratio.

## 3. The customer enumeration (re-verified at `99d2b6fe`, not rewritten)

`docs/dev/tt4m_batch_customers.md` (lane rpkg, 2026-09-10, snapshotted at
commit `2d0471a3`) already delivered the full enumeration: every
`tests/harness/run.sh` re-invoker (Category 1, 8/8b rows) and every
per-pattern-compile-outside-`run.sh` site (Category 2), plus the
found-but-not-a-customer sites (Category 3). Read that memo for the design
argument; this row only re-verifies it is still current — now at
`99d2b6fe`, the pin the timing pair actually ran at, not the skeleton's
`818a8711` — and cites it, per the brief. It does not restate or rewrite
the table.

Re-verification method: `grep -rn 'harness/run\.sh'` and `grep -rn
'HARNESS_BATCH'` over the whole tree (excluding `worktrees/`/`.git/`) at
`99d2b6fe`, the same method the memo itself documents, EACH new hit since
the `2d0471a3`/`818a8711` snapshots read individually to separate a real
invocation from a comment/doc-prose mention (the memo's own row 8/8b
caution).

- Category 1 rows 1 (`tests/size/run_size_log.sh`), 2 (`tests/lib/
  san_scripts.txt` + `run_san_group.sh`), 3 (`tests/axes/run_axes.sh`,
  **batched** since 2026-09-10, lane axbatch — already reflected in the
  memo's own text), 4 (`tests/axes/run_ksweep.sh`), 5 (`tests/known_fail/
  run_known_fail.sh`), 6 (`tests/mech/run_sabotage_matrix.sh:1952`), 7
  (`S205`'s reach probe), 8/8b (`tests/rxtsource/run_rxtsource_tests.sh`)
  — all confirmed still present at their cited (or trivially shifted)
  lines.
- Category 2 rows 9 (`tests/bench/run_bench.sh`, declined by design) and
  10 (`tests/fuzz/fuzz.py`, python, unreachable by this bash-only axis) —
  both confirmed present, dispositions unchanged.
- Category 3 (the six single-process differential drivers, `run_cli_tests
  .sh`/`run_codegen_tests.sh`'s fixed-scenario compiles, `run.sh` itself)
  — confirmed still the mechanism, not a customer, by the same reasoning.

**New hits since the last snapshot, all read and dispositioned as
comment-only, not new customers**: the `tests/mech/sabotages/` subtree has
grown a number of individually-numbered scripts since `2d0471a3`
(`S108`, `S157`, `S159`, `S173`, `S194`, `S196`, `S198`, `S199`, `S203`,
`S213`, `S214`) — every one either mentions `tests/harness/run.sh` in
prose (a `SAB_DOC_FIGURE`/design-rationale string quoting a hand-run
command, or a comment citing K35) or sets `SAB_FILE="tests/harness/
run.sh"` (the file the sabotage PATCHES, not a re-invocation) — all of
this is row 6's existing mechanism (`run_sabotage_matrix.sh:1952` is the
one real re-invocation site for the whole `mech` subtree), not a new
customer. Likewise new hits in `tests/lookaround/run_expansion_diff.sh`,
`tests/recursion/run_recursion_diff.sh`, `tests/registry/
axes_registry_check.sh`, `tests/registry/limits_check.sh`, `tests/lib/
timeout_bin.sh`, `tests/lib/assoc.sh`, `tests/lib/run_gen_timeout_tests.sh`
(one real hit, a string-comparison self-check unrelated to invoking it),
`tests/lib/loadavg.sh` and `tests/definitions/run_definitions_tests.sh`
are all comment/doc-prose mentions of the file by name, not calls.
`tests/lib/size_count.sh` and `docs/design/oracle_interface.md` newly
mention `HARNESS_BATCH` itself, both in prose (the former a comment about
future per-member prefix behavior, the latter design prose citing the axis
as a precedent) — neither is a new site that reads or forwards the
variable.

No new customer appeared and no listed customer disappeared between
`2d0471a3` and `99d2b6fe`. This re-verification finds the memo CURRENT,
not stale, at the pin this timing pair actually measured.

## 4. The san-arm feasibility note (owed to the Linux executor)

San is Linux-only today (K54, `docs/dev/known_issues.md`): the sanitized
`pcrec` CLI itself runs pathologically slowly under `gcc-16`'s `libasan`
on arm64-darwin (trivial inputs took 100+ seconds; a full `make san`
attempt on the Mac projected DAYS and was killed). That is a COMPILER-axis
problem (the `pcrec` binary built under sanitizers), separate from the
question this row asks, which is a COMPILEE-axis question: does
`GENCFLAGS`'s `-fsanitize=...` still apply correctly to a
`HARNESS_BATCH`-compiled generated matcher — i.e. does the sanitizer
instrumentation and runtime linkage ride the batched compile+link shape
the way `docs/design/tt4m_harness_batching.md` §4 (lines 257-291) argues
it does. Nothing here attempts to run it — K54 alone makes that
infeasible on this box even for a small slice (a single sanitized
`pcrec`-compiled artifact already costs 30-150s here); this section states
exactly what the Linux run must check.

**What the design note claims** (`docs/design/tt4m_harness_batching.md`
§4): gcc's one-shot compile-and-link mode already applies every flag on
`$GENCFLAGS` (which carries `-fsanitize=...` under the san/ubsan/asan
`*_ENV` blocks, `Makefile:1178-1300`) to both the per-TU compile and the
final link — true of today's unbatched single `gen_cc` call and, the note
argues, equally true once that one call becomes N members' `-c`
sub-compiles plus a `dispatch.c` `-c` sub-compile plus one link, AS LONG
AS `-fsanitize=...` rides every one of those three compile/link
invocations, not just the final link (a split-then-link shape that drops
it from the intermediate `-c` steps would build uninstrumented object code
that still links against the sanitizer runtime — silently losing coverage
on every batch member, not a build failure).

**Code-level confirmation (this lane, static read only, no run)**:
`tests/harness/run.sh` threads `$GENCFLAGS` through all three sites the
design note's argument depends on —

- `:933` `batch_member_compile()`: `gen_cc "${bm_pattern[$mi]}" "$CC"
  $GENCFLAGS -I"$batch_bdir" -c -o "$mo" "$mc"` (per-member `-c`)
- `:1057` `flush_batch()`: `gen_cc "batch dispatch ($cur_file)" "$CC"
  $GENCFLAGS -I"$batch_bdir" -c -o "$dobj" "$dc"` (dispatch.c `-c`)
- `:1073` `flush_batch()`: `gen_cc "batch link ($cur_file)" "$CC"
  $GENCFLAGS -o "$exe" "$dobj" "${surv_objs[@]}"` (the one link)

So the design's own precondition holds in the shipped code, matching its
`[TT-3]` ccache-shape precedent it cites as the pattern to copy. This is
NOT the same as verifying the sanitizer actually catches what it should
under the batched shape — that is a behavioral question a grep cannot
answer.

**What the Linux run must check (owed, not built here)**:

1. **Builds and links clean.** On a small slice (a handful of `.rxt`
   files, NOT the whole corpus — san is the slowest compile axis and this
   is a feasibility probe, not the acceptance run):
   ```
   GENCFLAGS="-O1 -std=gnu11 -Wall -Wextra -Werror -fsanitize=address,undefined,leak -g" \
   HARNESS_BATCH=4 PROCS=1 \
   bash tests/harness/run.sh tests/base/quantifiers.rxt tests/base/literals.rxt
   ```
   proves nothing more than "it links" if it exits 0 — expected, since
   `HARNESS_BATCH` is not wired into `run_san_group.sh`/`SAN_ENV` today
   (enumeration memo Category 1 row 2), so this is a hand-built probe, not
   yet a suite path.
2. **Detection survives the batched multi-TU link.** Repeat step 1 with
   one of the scratch sanitizer bugs `docs/dev/tt7_combined_axis.md`
   planted for `[TT-7]`'s own diagnosis-distinctness check (three scratch
   sabotages into a copy of `tests/harness/driver.c` against a real
   generated matcher, each caught by its own tool) placed in ONE batch
   member's position, run at `HARNESS_BATCH>=2` so the planted bug is NOT
   the only member in its batch. Pass criterion: the sanitizer report
   still names the correct member's pattern/line (per-member `-c`
   compilation means each TU keeps its own debug info regardless of which
   TUs share its link, so attribution SHOULD be unaffected — this is the
   structural argument, not yet a measurement) — a report that instead
   names `dispatch.c` or a wrong member would mean the batching shape
   itself degrades diagnosis quality even though it still "catches"
   something.
3. **Compares the batched to the unbatched detection on the same planted
   bug**, same shape as step 2 but with `HARNESS_BATCH` unset — confirms
   the batched and unbatched reports are the SAME finding (tool, file
   attribution reachable back to the right pattern, same category of
   report), not merely that both exit nonzero.

None of this is a timing question — san's own timing under batching is a
separate, later measurement once K54 is resolved or the Linux battery
absorbs the cost regardless (san already runs there today, unbatched, at
~68 minutes per `docs/testing.md`'s "[TT-7] combined axis" section).

## 5. What the flip decision reads

The measured trade for turning `HARNESS_BATCH=64 PROCS=8` on by default for
`make test` on THIS box: **~486s / ~8.1 minutes of wall per full suite run**
(~9.5%), ~8-10% less CPU, no memory cost. Named residuals and caveats a
flip decision should carry forward, not re-derive:

- **The saving is concentrated in 2-3 of 38 sections** (§2) — a smaller
  corpus, or a tree where `test-corpus`/`test-rxtsource` shrink relative to
  the differential-driver sections, would see a smaller percentage; a
  larger corpus, more.
- **`SIZELOG`'s batch-mode caveat** (`docs/testing.md`'s `HARNESS_BATCH`
  section): under batching, a size-log row's own CPU/wall reading is the
  per-member `-c` sub-compile ALONE, not compile+link as the unbatched path
  always measured — a real, documented, non-batching-specific shape change
  in what that column means, not a compiler speed regression/improvement.
  Anyone reading `docs/dev/artifact_size_log.tsv` movement across this
  axis needs that caveat in hand (relevant here since run 2 regenerated
  that file — disposition below, §7).
- **`make mech`'s harness suite arm does not set `HARNESS_BATCH` at all**
  (`docs/dev/lanes/tt4m3_report.md` finding F4): `run_sabotage_matrix.sh`'s
  `harness)` suite arm invokes `tests/harness/run.sh` with `PCREC`/`CC`/
  `PROCS` but never `HARNESS_BATCH`, so flipping `make test`'s own default
  does NOT speed up `make mech` (row 6 of the customers memo, its highest-
  value unclaimed customer by population) — that needs its own,
  separately-ruled suite-wiring change, per F4.
- **Not measured here**: the Linux reference box (every number in this
  memo is Mac-specific, per `docs/testing.md`'s "The boxes" convention —
  cross-box timings are never compared; the Linux executor's own
  acceptance run, owed per `tt4m3_report.md`, is what governs the Linux
  battery's default) and `make mech` itself (F4, above — untouched by this
  pair regardless of the flip).

No recommendation beyond these numbers and residuals is made here — the
default-on flip is Frank's/the manager's call.

## 6. Limitations

- **Single sample pair.** One run at `HARNESS_BATCH` unset, one at `=64
  PROCS=8`, both once. No repeat runs, no variance estimate — the darwin
  load-gate escalation recorded in `docs/dev/cls_tree_study.md`'s D77
  verdict section applies here too: this desktop Mac's ambient load1
  rarely sits near zero (background apps, editor, Tailscale — none of it
  a competing heavy suite, confirmed by `ps` before each run), so a
  "quiet box" here means "nothing else CPU-heavy running," not a near-idle
  machine, and a single pair under that definition is a point estimate,
  not a distribution. Run 2's load1 (1.62) was measurably HIGHER than run
  1's (1.33) — a residual from run 1's own tail, not a separate load
  source — which biases AGAINST run 2 (a more loaded box should read
  slower, all else equal), the same direction as the `PROCS` confound
  below; both point the same way, toward this memo's number
  UNDERSTATING rather than overstating the batching benefit.
- **`PROCS` moved alongside `HARNESS_BATCH` (§1a.2), not held constant.**
  Run 1 defaulted to `nproc` (10 file-workers in `test-corpus`); run 2's
  literal invocation string set `PROCS=8`. This is not a clean single-
  variable comparison — the ~486s figure is the combined effect of
  enabling batching AND reducing `test-corpus`'s own file-level
  parallelism by two workers, not batching in isolation. Reasoned
  direction (§1a.2): fewer workers should cost time, not save it, so this
  is a bias against the measured saving, not a confound that could be
  inflating it — but it is a bias, and a repeat at matched `PROCS` values
  is the fix, not assumed away.
- **What would change the number**: a third+ run at each setting (to
  separate real speedup from this box's own run-to-run jitter — memory
  `pcrec-nfa-compaction-paper`-adjacent studies on this project have seen
  single-digit-percent jitter between otherwise-identical runs); a repeat
  at a MATCHED `PROCS` value on both sides (isolating the confound just
  named); a repeat at `PROCS` values other than 8 (the P=8 recommendation
  is `tt4m_step2a_parallel_sizing.md`'s own finding, itself a single-box,
  single-sweep result); and, separately, this same pair run on the Linux
  reference box, since every number here is Mac-specific by
  `docs/testing.md`'s "The boxes" convention (cross-box timings are never
  compared) and the Linux executor's acceptance run (owed per
  `tt4m3_report.md`) is still the number that governs the LINUX battery's
  own default.
- **This memo does not re-argue `HARNESS_BATCH`'s correctness** — answer
  identity (byte-for-byte case counts) is what §1's count-identity
  paragraph checks; the mechanism's own construction/smoke validation is
  `tt4m3_report.md`'s and `axbatch_report.md`'s territory, not
  re-litigated here.
- **The second FAIL (§1a.1) is not diagnosed here.** This memo's charter is
  measurement, not repair — `tests/anchored/run_anchored_diff.sh`'s
  26-pattern compile failure is reported as a finding for the manager/Frank
  to charter or assign, not investigated further in this document.

## 7. Disposition of `docs/dev/artifact_size_log.tsv`

Both runs regenerated this file (`test-corpus`'s own `run_size_log.sh`
writes it at the end of every full corpus compile) — the working tree
shows it modified, 3,479 lines changed each way (every row rewritten, not
appended). This reflects run 2 (batched, `PROCS=8`, last to run) plus
whatever the killed 2026-09-11 attempt referenced in `docs/dev/wake.md`
left behind before this pair started. **Not committed by this memo**: a
batched run's SIZELOG numbers carry the documented `-c`-only CPU/wall
caveat (§5) and this box was warm, not idle, for both runs (§6) — this
file is disposed of (discarded) when `worktrees/tt4mtime` is removed, not
merged into the committed log.

## 8. Sources

- `docs/dev/tt4m_batch_customers.md` — the enumeration this row cites and
  re-verifies (§3).
- `docs/dev/lanes/tt4m3_report.md` — the implementation report, its OWED
  acceptance-command list (§1's invocation shape follows it), and finding
  F4 (mech's harness arm does not set `HARNESS_BATCH`, §5).
- `docs/dev/lanes/axbatch_report.md` — the 2-character-prefix fix
  (`a2c89c06`) this row's charter requires the timing to postdate.
- `docs/dev/tt4m_2d_evidence/README.md` — the PRIOR (stale, concurrent-load,
  pre-fix) timing evidence this row supersedes; not reused.
- `docs/dev/known_issues.md` K54 — darwin san infrastructure status, §4's
  premise.
- `docs/design/tt4m_harness_batching.md` §4 — the GENCFLAGS/axis
  compatibility argument §4 checks against the shipped code.
- `docs/testing.md` "`HARNESS_BATCH` — batched compilation+dispatch"
  section — the SIZELOG caveat and 2-character-prefix mechanics cited in
  §2/§5/§7.
- `docs/dev/tt4m_darwin_validation.md`, `docs/dev/tt4m_step2a_parallel_sizing.md`
  — [TT-4M]'s isolated-corpus prototype ratios (4.28x serial, 18.65x
  parallel) §2 compares this memo's whole-suite number against.
- `docs/dev/wake.md` — records the killed 2026-09-11 attempt and the
  partial (3600s-killed) prior run whose "green except inline_capability"
  reading §1a.1 corrects.
