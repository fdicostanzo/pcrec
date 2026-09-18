# Triage: `battery_20260918_051433`'s `test`-stage red (lane btriage2)

Note on the filename: this brief also named the lane `btriage2`, and an
earlier `btriage2` lane (2026-09-10) is on record, so this report is
date-qualified rather than risking a collision with that lane's own
`docs/dev/lanes/btriage2_report.md` (which does not exist in this tree, but
the brief's own caution is followed anyway) — matching the precedent
`btriage_20260917_report.md` set for the plain `btriage` name.

## Verdict

**The 272bf970 pin HOLDS.** The `test`-stage's entire red is ONE failure
(`grep -c '^FAIL'` on the battery's `test.log` returns exactly `1`; the
battery's own `checks failed: 1` line is `tests/resource/run_resource_tests.sh`'s
own per-file summary, not a second failure), and it is a STALE TEST-SIDE
WITNESS with an insufficient CPU-budget margin, not a defect in anything the
fix-now pile or wave U shipped. Fixed and re-validated locally in this
worktree; a fresh `make test` on ubuntubudu would need to confirm the fix
holds there too, though the fix's own margin (see below) should not leave
that in doubt.

## The failure

```
== [OPT-3] §3 the corpus sweep: stamp vs emitted tables, every artifact ==
FAIL: '(?:[a-z][0-9]){1,13000}' exited 123, expected the size-cap refusal:
watchdog: sizecap (?:[a-z][0-9]){1,13000}: CPU limit exceeded (limit 45s of
CPU time) (TERM->KILL), peak rss 22636 kB
```

**The section header printed just above this line is misleading — the FAIL
is NOT from `run_premul_table.sh`.** `run_premul_table.sh` contains no
`watchdog`/`sizecap` calls and no such message anywhere in its source; the
message's exact text and `-l "sizecap $pat"` label trace uniquely to
`tests/resource/run_resource_tests.sh`'s Section 1b (`size_moved` loop,
line ~304). The two scripts run back to back in the battery
(`run_resource_tests.sh` at test.log:2972, `run_premul_table.sh` at
test.log:3103) and the log shows `run_resource_tests.sh`'s own printed
summary (`checks passed: 11 / checks failed: 0`, at test.log:3011) with NO
`size_moved` output visible in between — the loop's own PASS/FAIL lines are
flushed late relative to the next script's `==` headers, a buffering
artifact of that box's `make test` output capture, not a section boundary.
(This cost real time to pin down; flagged so the next triage does not
re-derive it — the exact code paths are quoted below so it does not need
re-deriving either.)

## Classification: stale test-side pin (insufficient CPU margin), not a regression

**The witness itself is correct — refuse `(?:[a-z][0-9]){1,13000}` at the
total emitted-size cap.** What is wrong is the CPU budget it runs under.
Section 1b's `size_moved` loop shares Section 1's `K7_CPU` (default 45s),
whose own header comment calibrates that default as "~3x" a MEASURED 15.4s
compile (`a{0,25000}`, on the dev box). Row 1's witness measures **25.17s
user CPU on this same dev box** (Apple M1 Max, `gcc-16 -O2`,
`/usr/bin/time -l build/pcrec -p rx -o /tmp/o.c '(?:[a-z][0-9]){1,13000}'`)
— under 1.8x margin against K7_CPU's own 45s, well short of the ~3x
convention that set the budget in the first place.

**Why row 1 costs so much more than an ordinary compile: it does the work
TWICE.** The same pattern with `--max-emit-bytes=9000000` (which never
trips the cap, so [K59-PREMUL]'s drop ladder never retries) measures only
**12.58s** — essentially half. The row's own header comment already
documents the mechanism (`[K59RUNG]`, 2026-09-17): a cap hit on a
premultiplied DFA artifact retries once with `-fno-premul-table` before
refusing again, so the refusal path pays for two minimizations where a
plain compile pays for one.

**ubuntubudu (the Linux reference box) is a materially slower single core
than the Mac dev box that calibrated K7_CPU.** `lscpu` there reports an AMD
Ryzen 5 1600 (2017, 6c/12t desktop part); this dev box is an Apple M1 Max.
Published single-core benchmarks put the M1 Max at roughly 2.3-2.6x the
Ryzen 5 1600. 25.17s x ~2.3-2.6 lands at roughly 58-65s — comfortably past
K7_CPU's 45s ceiling, which is exactly the exit-123 CPU-limit kill the
battery recorded.

**This is not box contention.** The battery's own trailer records
`load at start: 05:14:33 ... load average: 0.52, 0.15, 0.05` on a 12-thread
box — effectively idle. `run_resource_tests.sh` already has a load-guard
mechanism (`tests/lib/load_guard.sh`, `[TT-10]`) that reclassifies a
123/124 kill as INCONCLUSIVE under real contention, but it is wired into
Section 1's loop only (lines ~247/252) — Section 1b's loop has no such
check and would not have used it here regardless, since the box was not
contended.

**Ruled out as a cause: the three commits the fix-now pile added since
`cf0962e3`** (`git log --oneline cf0962e3..272bf970 -- src/opt/minimize.c
src/ir/dfa.c src/core/compile.c src/core/limits.h`):

- `66363dcd` [REVW.FIX] L4-C1+C2 — adds function-header COMMENTS to 43
  functions. No code change.
- `5886e315` [REVW.FIX] L3-F3 — replaces open-coded FNV-1a arithmetic at 9
  sites (`dfa.c`'s `dhash`, `minimize.c`'s signature hash) with two
  `static inline` helpers, same arithmetic and evaluation order, the
  commit's own validation confirms byte-identical emit-diffs. `static
  inline` at `-O2` should compile to identical code; this is a mechanical
  refactor with no plausible performance delta, and row 2's witness
  (`(a|b){5,30000}`, exercises the SAME `dhash` code path, measured
  11.27s here) shows no comparable slowdown.
- `23eb3d34` [REVW.FIX] L8-F1 — attaches a `Ctx` back-pointer on two
  `StrBuf`s in `compile_driver`'s attachment block. Unrelated to
  minimization.

None of these three touch the DFA minimization algorithm's asymptotic or
constant-factor cost. The margin gap traces entirely to the witness's own
CPU cost (25.17s, nearly double the case that calibrated K7_CPU) meeting a
reference box measurably slower than the one the budget was calibrated on
— a gap that predates this battery and was simply never exercised on
Linux before now (btriage's own 2026-09-17 report, which re-derived this
exact witness, measured and validated it on the Mac worktree only and said
so explicitly: "a fresh `make test` on the Linux box would need to confirm…").

Row 2 (`(a|b){5,30000}`, the loop's other cell) is unaffected — measured
11.27s here, comfortably under budget on either box, and the battery's log
confirms it PASSED immediately after row 1's FAIL.

## The fix

Scoped to Section 1b only, via a new `SIZECAP_CPU` (default 90s) watchdog
CPU budget used in place of `K7_CPU` for both of that loop's `watchdog`
calls (the refusal check and the `--max-emit-bytes` re-acceptance check).
Section 1's own `K7_CPU` is untouched — that section's whole claim is the
K7 CPU/wall/RSS ceiling itself, so loosening it for everyone would weaken
what it asserts; Section 1b's claim is the SIZE cap, and its watchdog
budget only needs enough margin for a legitimately expensive (not runaway)
compile on the slowest box this suite runs on. 90s gives row 1's own
25.17s Mac measurement ~3.6x margin (back in line with K7_CPU's own ~3x
convention) and, by the same ~2.3-2.6x cross-platform ratio used above,
projects to roughly 58-65s needed on ubuntubudu — comfortable headroom
under 90s.

Files changed:
- `tests/resource/run_resource_tests.sh` — `SIZECAP_CPU` env var (default
  90), the two `watchdog -c` calls in the `size_moved` loop switched from
  `$K7_CPU` to `$SIZECAP_CPU`, header comment tracing the measurement, and
  the `Env:` usage-comment block updated.
- `tests/resource/CLAUDE.md` — documented Section 1b (missing from the
  file's own "now FIVE sections" list before this change — a separate,
  pre-existing staleness fixed in passing since I was already editing the
  section it describes) and the new `SIZECAP_CPU` env var; also
  de-hardcoded the `Env` paragraph's stale `K7_SECS`/`K7_CPU` numeric
  defaults (60/20), which no longer match the script's actual defaults
  (120/45) and were not part of this triage's own claim, so I pointed
  readers at the script's header rather than re-copying a second stale
  pair of numbers.

## Validation

Built clean in this worktree (`make -j4 CC=gcc-16`, no `src/`/`cli/`
changes — only `tests/`). `make strict CC=gcc-16`: **clean, rc=0**
("strict: whole tree compiles clean with -Werror -Wshadow" — expected,
since nothing under the warnings-as-errors scope changed, but run per the
delivery bar).

Direct reproduction of the failure BEFORE the fix, on this worktree's own
build: `(?:[a-z][0-9]){1,13000}` measured 25.17s user / 25.57s real CPU,
correctly refusing at 1,034,778 bytes (the `was` field in the loop's
success message is informational only — not compared against the actual
byte count — so the 1-byte difference from btriage's originally-recorded
1,034,779 is not a pin problem).

Targeted section run AFTER the fix,
`bash tests/resource/run_resource_tests.sh` (no env overrides, so
`SIZECAP_CPU` used its new 90s default):

```
== Summary ==
checks passed: 27
checks failed: 0
checks inconclusive: 0
sections skipped: 1
RESOURCE_RC=0
```

(Section 2 is the one expected skip — `[MACPORT]`'s darwin `ulimit -v`
limitation, unrelated to this fix.) The two `size_moved` rows both read
PASS, including the previously-failing one:

```
PASS: '(?:[a-z][0-9]){1,13000}' refused by the total emitted-size cap (was 1034779 bytes before [ART-SIZE]): pcrec: pattern too large: 1034778 bytes of emitted C source (limit 1000000, ~171 KB .o). L
PASS: '(?:[a-z][0-9]){1,13000}' is re-accepted with --max-emit-bytes raised (the override works end to end)
```

This is 2 more than btriage's own prior local count (25 pass at the
2026-09-17 landing), which predates wave U's L8-F6 additions (Section 0's
census check and Section 2b's allocation-injector check) — both new
sections this run exercises that btriage's did not, accounting for the
delta.

Not re-run: a full `make test` (box-concurrency rule — the remote battery
was still mid-run on ubuntubudu at hand-off, running only the touched
suite plus `make -j4`/`make strict` locally per this brief's own
validation bar). `make test-codegen` was not run either: no emitted
scaffolding, ABI, or `src/`/`cli/` byte changed — only a test script's own
watchdog budget — so D76/D94's re-pin obligation does not apply.

## Commits

Branch `lane/btriage2`, off main `272bf970`:

1. `9255307b` — widen the `size_moved` loop's own CPU budget
   (`SIZECAP_CPU=90`), with the measurement traced in the script's own
   header comment.
2. (this report, plus the `tests/resource/CLAUDE.md` documentation update)

Not merged to main; not pushed. PARKED per the brief — the remote battery
was still in flight (axes/san/lint/mech stages) at hand-off, and nothing
merges to main until its own trailer completes.
