# `tt4m_time.md` — [TT-4M-TIME] the clean post-fix `HARNESS_BATCH` timing

2026-09-11, lane tt4mtime, measurement only (nothing under `src/`/`tests/`
changed). Answers the row's own charter: a QUIET-BOX, normal-conditions
full `make test` at `HARNESS_BATCH` unset vs `=64 PROCS=8` on the tree
AFTER the 2-character-prefix fix (`a2c89c06`, lane axbatch), since the
prior `docs/dev/tt4m_2d_evidence/` runs (README below) are both
upper-bound-understated (measured under concurrent load) and predate that
fix — no clean suite-level number existed before this memo. The default-on
flip decision reads THIS number, not 2d's.

## 1. The timing pair

Both runs on this Mac (`hw.ncpu` 10, GNU Make 3.81 — this box's bundled
`make` predates `-Otarget`/`--output-sync`, so `test:`'s ten prerequisite
sections run in the Makefile's own listed order both times, exactly as
`docs/testing.md`'s "plain `make test` (no `-j`)" note describes; no `-j`
flag on either run, matching the shape `docs/dev/lanes/tt4m3_report.md`'s
own OWED commands specify). Worktree `worktrees/tt4mtime`, branch
`lane/tt4mtime`, built at `818a8711` (main HEAD at lane start) with
`make -j4 CC=gcc-16`. Wall/CPU captured by `/usr/bin/time -l` wrapping the
whole `make test` invocation (one process tree, no second compile).

| run | command | load1 before | wall | user CPU | sys CPU | pass/fail counts |
|---|---|---|---|---|---|---|
| 1 (unbatched) | `make test` | OWED | OWED | OWED | OWED | OWED |
| 2 (batched) | `HARNESS_BATCH=64 PROCS=8 make test` | OWED | OWED | OWED | OWED | OWED |

Speedup: OWED (wall), OWED (CPU).

Count parity (unbatched vs batched pass/fail/pattern-compile-failure/
size-log-row totals, per section): OWED.

Expected baseline per BOILERPLATE.md/the brief: green except the chartered
darwin `inline_capability` failure ([CC-DIFF] — not a regression), counted
identically in both runs. OWED whether that held.

Raw logs: `tt4mtime_run1.log` / `tt4mtime_run2.log` (session scratchpad,
paths in the handback message) — archived summary lines quoted in §1a once
both runs land.

### 1a. Anomalies

OWED.

## 2. The customer enumeration (re-verified, not rewritten)

`docs/dev/tt4m_batch_customers.md` (lane rpkg, 2026-09-10, snapshotted at
commit `2d0471a3`) already delivered the full enumeration: every
`tests/harness/run.sh` re-invoker (Category 1, 8/8b rows) and every
per-pattern-compile-outside-`run.sh` site (Category 2), plus the
found-but-not-a-customer sites (Category 3). Read that memo for the design
argument; this row only re-verifies it is still current at `818a8711` and
cites it, per the brief — it does not restate or rewrite the table.

Re-verification method: `grep -rn 'harness/run\.sh'` and `grep -rn
'HARNESS_BATCH'` over the whole tree (excluding `worktrees/`/`.git/`) at
this lane's branch point, the same method the memo itself documents.
Result: every site the memo names is still present at its cited line (or
the file has grown and the site shifted a few lines but the same call
survives — checked by grep, not by diff):

- Category 1 rows 1 (`tests/size/run_size_log.sh`), 2 (`tests/lib/
  san_scripts.txt` + `run_san_group.sh`), 3 (`tests/axes/run_axes.sh`,
  now **batched** — landed 2026-09-10 by lane axbatch, after the
  enumeration memo was written; the memo's own row already recorded this),
  4 (`tests/axes/run_ksweep.sh`), 5 (`tests/known_fail/run_known_fail.sh`),
  6 (`tests/mech/run_sabotage_matrix.sh:1952`), 7 (`S205`'s reach probe),
  8/8b (`tests/rxtsource/run_rxtsource_tests.sh`, 13 call sites) — all
  confirmed present.
- Category 2 rows 9 (`tests/bench/run_bench.sh`, declined by design) and
  10 (`tests/fuzz/fuzz.py`, python, unreachable by this bash-only axis) —
  both confirmed present, dispositions unchanged.
- Category 3 (the six single-process differential drivers, `run_cli_tests
  .sh`/`run_codegen_tests.sh`'s fixed-scenario compiles, `run.sh` itself)
  — confirmed still the mechanism, not a customer, by the same reasoning.

No new customer appeared and no listed customer disappeared between
`2d0471a3` and `818a8711`. The one change in that interval — row 3 going
from NO to YES — was already reflected in the memo's own text (it records
the axbatch landing inline), so this re-verification finds the memo
CURRENT, not stale.

## 3. The san-arm feasibility note (owed to the Linux executor)

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

## 4. Limitations

- **Single sample pair.** One run at `HARNESS_BATCH` unset, one at `=64
  PROCS=8`, both once. No repeat runs, no variance estimate — the darwin
  load-gate escalation recorded in `docs/dev/cls_tree_study.md`'s D77
  verdict section applies here too: this desktop Mac's ambient load1
  rarely sits near zero (background apps, editor, Tailscale — none of it
  a competing heavy suite, confirmed by `ps` before each run), so a
  "quiet box" here means "nothing else CPU-heavy running," not a near-idle
  machine, and a single pair under that definition is a point estimate,
  not a distribution.
- **What would change the number**: a third+ run at each setting (to
  separate real speedup from this box's own run-to-run jitter — memory
  `pcrec-nfa-compaction-paper`-adjacent studies on this project have seen
  single-digit-percent jitter between otherwise-identical runs); a repeat
  at `PROCS` values other than 8 (the P=8 recommendation is
  `tt4m_step2a_parallel_sizing.md`'s own finding, itself a single-box,
  single-sweep result); and, separately, this same pair run on the Linux
  reference box, since every number here is Mac-specific by
  `docs/testing.md`'s "The boxes" convention (cross-box timings are never
  compared) and the Linux executor's acceptance run (owed per
  `tt4m3_report.md`) is still the number that governs the LINUX battery's
  own default.
- **This memo does not re-argue `HARNESS_BATCH`'s correctness** — answer
  identity (byte-for-byte case counts) is what §1's count-parity column
  checks; the mechanism's own construction/smoke validation is
  `tt4m3_report.md`'s and `axbatch_report.md`'s territory, not
  re-litigated here.

## 5. Sources

- `docs/dev/tt4m_batch_customers.md` — the enumeration this row cites and
  re-verifies (§2).
- `docs/dev/lanes/tt4m3_report.md` — the implementation report and its
  OWED acceptance-command list (§1's invocation shape follows it).
- `docs/dev/lanes/axbatch_report.md` — the 2-character-prefix fix
  (`a2c89c06`) this row's charter requires the timing to postdate.
- `docs/dev/tt4m_2d_evidence/README.md` — the PRIOR (stale, concurrent-load,
  pre-fix) timing evidence this row supersedes; not reused.
- `docs/dev/known_issues.md` K54 — darwin san infrastructure status, §3's
  premise.
- `docs/design/tt4m_harness_batching.md` §4 — the GENCFLAGS/axis
  compatibility argument §3 checks against the shipped code.
