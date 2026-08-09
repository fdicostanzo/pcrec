# tests/bench — performance/regression benchmark suite

Plan step M2.3. Where `tests/harness/` checks *correctness* (does the
generated matcher return the right span), this suite checks *performance
regression*: does pcrec stay fast to compile, does the C compiler stay fast
on its output, and does the generated matcher stay fast (and linear) to
run. It exists specifically because checkpoint review R1
(`docs/reviews/2026-08-09-m1.md`) found the M1 computed-goto emitter had two
measured pathologies that no test caught until an adversarial critic went
looking, and both needed a standing regression guard before M2 could build
on top of the emitter:

- **A-2** (unanchored search is O(n^2)): the M1 emitted loop restarted the
  DFA from scratch at every start position with no prefilter, measured
  textbook quadratic — `a*b` over an all-`'a'` buffer took 4x longer per 2x
  input size (7.78s at 160 KB, extrapolating to hours at 10 MB).
- **A-3** (gcc compile time doesn't scale with the state cap): the 10k-state
  cap didn't bound gcc's own compile time on the emitted C. `[01]*1[01]{n}`
  needs `2^(n+1)` states (provably minimal for that family); going from 512
  to 2048 states took `gcc -O2` from 1.3s to 62.7s, and 8192 states didn't
  finish `-O2` in 120s — superlinear CFG-pass cost on one huge
  computed-goto function.

Both were triaged into the M2.0 design gate (new automaton/emitter shape)
with this bench suite as the thing that proves the fix and stays green
against future regressions.

## Measurement rigor (M2.9, decision D12)

Checkpoint review R2 found the first version of this suite could not fail:
budgets were 9x–300,000x looser than the numbers they guarded, measurements
were single samples on an unpinned `schedutil` box with turbo on, one case
measured early exit rather than throughput, and the linearity check was
computed from times below its own anti-blowup floor.

What that means in practice: a sabotage build with the memchr prefilter and
self-loop skip states disabled runs 5.4x/68x/5.6x slower on cases (a)/(b)/(c)
— and the ORIGINAL budgets of 200/50/50 MB/s passed all three.

So now:

- every timed run is pinned with `taskset -c $BENCH_CPU` (`chrt -f 50` is
  probed and used only where permitted);
- every measurement is `BENCH_TRIALS` repeats (default 5) judged on the
  **median**, with the max/min **spread** printed on the row;
- the run header records cores, pinning, trial count, governor, turbo and
  load average;
- budgets are the measured median divided by ~1.75, so a ~1.75x regression
  fails, and they are re-validated against the sabotage above whenever
  retuned;
- no measurement is allowed to be sub-millisecond — iteration counts were
  raised where they were.

Reference medians on the development box (AMD Ryzen 5 1600, 12 cores,
schedutil, turbo on, load ~0.9, `BENCH_TRIALS=7`):

| measurement | median | per-trial spread | budget |
|---|---|---|---|
| COMPILE-SPEED (20 patterns) | 0.111 s | — | < 0.4 s |
| KEYWORD-SCALE (3600 words) | 0.92 s | — | < 4 s |
| GCC-TIME, 8192 states, -O2 | 0.219 s | — | < 2 s |
| (a) `needleXYZW` 8 MB | 1918 MB/s | 1.15x | > 1200 MB/s |
| (b) `a*b` 8 MB all-'a' | 21910 MB/s | 1.21x | > 12000 MB/s |
| (c) `a(b\|c)+d` 8 MB no-match | 1794 MB/s | 1.35x | > 1000 MB/s |
| (d) `(alpha\|beta\|...)` 8 MB no-match | 429–457 MB/s | 1.03–1.08x | > 330 MB/s |
| linearity 64MB/16MB | 3.63 | 1.06–1.14x | < 6.0 (linear 4.0) |

Every value is env-overridable; retune on slower hardware by setting the env
vars, not by editing the defaults.

## Running

```
bash tests/bench/run_bench.sh
```

Needs a built `build/pcrec` (`make` at the repo root first), `gcc` (or
`$CC`), and `python3` (used to generate the throughput subject files).
Nothing here modifies the repo; all work happens in a `mktemp -d` workdir
that is deleted on exit unless `KEEP=1`.

Env vars:

| var | default | meaning |
|---|---|---|
| `PCREC` | `<repo-root>/build/pcrec` | binary under test |
| `CC` | `gcc` | C compiler for the GCC-TIME and THROUGHPUT sections |
| `SKIP_BUDGETS` | `0` | `1`: still measure and print every PASS/FAIL, but never let a budget miss set the exit code (mechanical/harness failures — a crash, a compile that should have succeeded but didn't — still fail the exit code regardless) |
| `KEEP` | `0` | `1`: keep the temp workdir (generated `.c`/`.h`, subject files, binaries) instead of deleting it, and print its path |

Every budget threshold and every hang-protection timeout is also an
overridable env var — see the header comment in `run_bench.sh` for the
full list and current defaults. This matters because the DFA engine is
being reworked as this suite is being written; the budgets below are set
for the *post-rework* table emitter, not tuned to any one box, so a slower
CI runner or a future emitter with different constant factors should
override rather than have this suite silently miscalibrated.

## What each section measures, and why the budget is what it is

### COMPILE-SPEED

Runs pcrec over ~20 varied base-tier patterns (plain literals, alternation,
character classes, bounded repeats `{m,n}`, and a realistic log-line
pattern combining all of those) and sums pcrec's own wall time. Budget: **under 0.4s total** (measured
0.111s). Originally 2s, which was ~18x looser than the measurement and could
not have failed — see "Measurement rigor" above for why every budget on this
page was re-derived in M2.9.

Implementation note: the whole loop is wrapped in a single outer `timeout`
rather than one `timeout` per pattern. On the box this suite was built and
tested on, forking `timeout` itself costs roughly 100x what pcrec takes to
compile a small pattern (~0.1s of subprocess-spawn overhead vs ~0.001s of
actual pcrec work); wrapping every invocation individually would measure
shell/`timeout` overhead, not pcrec, and blew the 2s budget on that
artifact alone during self-test. One outer timeout still bounds a hang
(`COMPILE_SPEED_TIMEOUT`, default 30s), just without per-pattern
attribution if it ever fires.

Patterns intentionally avoid `\d \w \s`, POSIX classes (`[:alpha:]` etc.),
and other not-yet-implemented constructs — see the `esc_modules` table in
`src/parse/parse.c` — since this section is about compile *speed*, not
compile *coverage* (that's `tests/harness/`'s job).

### GCC-TIME (the R1 A-3 regression guard)

Compiles two DFAs known to be large by construction — `[01]*1[01]{8}`
(512 states) and `[01]*1[01]{12}` (8192 states), both from A-3's own
measurements — with `$CC -O1 -c` and `-O2 -c` (compile only, no link; a
`main()` isn't emitted, and only the compiler's own front/middle/back-end
time is in scope here, not the linker's). Budgets: **2s each** for `-O1` and `-O2`, per pattern (measured 0.219s).
A-3 originally recommended 5s/10s after watching the old emitter blow through
both (62.7s and >120s DNF); the table emitter is so far inside that envelope
that the loose values could not fail, so M2.9 tightened them.
On the old computed-goto emitter this section is *expected* to fail — that
was the whole point of measuring it; on the new table-driven emitter it
should pass with room to spare.

The `-O2` timeout defaults to 130s (`GCC_O2_TIMEOUT`), deliberately just
above A-3's "didn't finish in 120s" observation, so a regression back to
the old emitter's shape shows up as a clean, fast "DNF, budget FAIL"
instead of the harness hanging for however long an unbounded superlinear
compile would actually take.

### THROUGHPUT (+ the R1 A-2 linearity check)

Three subjects, 8 MB each, generated with `python3`:

- **(a)** random lowercase text with `needleXYZW` planted at the 90% mark,
  pattern `needleXYZW`. Budget: **> 1200 MB/s** (measured 1918).
- **(b)** 8 MB of `'a'` repeated, pattern `a*b` — guaranteed no match. This
  is A-2's exact pathological shape (DFA state advances maximally at every
  restart position with nothing to prefilter on). Budget: **> 12000 MB/s**
  (measured 21910, at 20 iterations — a single 8 MB pass is ~0.75 ms, too
  short to time honestly).
- **(c)** random lowercase text over an alphabet with no `d` in it, so
  `a(b|c)+d` CANNOT match and the engine scans the whole buffer. Budget:
  **> 1000 MB/s** (measured 1794). This case used to plant a match 4 KB into
  8 MB, which meant a correct early-exiting engine scanned 0.05% of the buffer
  and the "throughput" figure — 5,547,850 MB/s — was really exit latency
  (R2-B4).

None of these floors is loose any more. The old 50 MB/s values were a
"did this fall off a cliff" trip-wire that a 68x regression could pass; see
"Measurement rigor" above.

**Linearity check**: `a*b` over 16 MB vs 64 MB of all-`'a'` (x20 iterations)
— the same shape as A-2's measurement, re-run at two sizes so the suite can
compute a ratio instead of relying on a single absolute-time budget. Budget:
**ratio (64 MB time / 16 MB time) under 6.0** (measured 3.63). It was 1 MB vs
4 MB at a ratio budget of 8.0, which put both sides below the script's own
anti-blowup floor — it was reading timer noise (R2-B4). A linear-time engine gives ~4.0 (4x
the data, 4x the time); A-2's measured behavior was ~4x time per *2x*
size, i.e. ~16x per 4x size — so 8.0 sits at the geometric midpoint,
comfortably rejecting anything with real quadratic character while still
tolerating constant-factor noise (cache effects, measurement jitter) in a
linear implementation.

Throughput is measured by `bdriver` (`tests/bench/bdriver.c`): it reads a
subject file fully into memory (length tracked from `fseek`/`ftell`, never
`strlen`, since subjects are 8 MB of non-NUL-terminated binary data), calls
`rx_search(buf, n, 0, &m)` in a tight loop for a given iteration count, and
times the loop with `clock_gettime(CLOCK_MONOTONIC)`. It's compiled fresh
per pattern against that pattern's `gen.c`/`gen.h` (always emitted as
`gen.c`/`gen.h` by `run_bench.sh`, regardless of pattern, so `bdriver.c`
can have a single fixed `#include "gen.h"`), under
`-Wall -Wextra -Werror -O2 -std=gnu11`.

## Hang protection

Every pcrec invocation, every `gcc`/`$CC` compile, and every `bdriver` run
is wrapped in `timeout`. If a measurement doesn't finish in time it's
reported as `DNF (exceeded Ns timeout)` and counted as a budget **FAIL**
(never as a silent hang or a script crash) — this is deliberate for the
GCC-TIME 8192-state `-O2` case (see above) and, on the *old* emitter, would
also be expected for THROUGHPUT (b)/(c) and the linearity check, since
those are exactly A-2's quadratic shape at a size where the old emitter
would run for hours.

## SKIP_BUDGETS=1

`SKIP_BUDGETS=1` runs every measurement and prints every PASS/FAIL exactly
as normal, but a budget **FAIL** no longer makes the script exit nonzero
(a **hard error** — pcrec crashing, `$CC` failing to compile code that
should compile, a subject-generation failure — still does, regardless of
`SKIP_BUDGETS`). This is for validating the suite's own mechanics
independent of whether the engine under test currently meets its
performance targets: subjects get generated, `pcrec` and `$CC` get
invoked, `bdriver` builds and runs, numbers get printed — useful when
iterating on the emitter itself, or when re-baselining budgets after a
deliberate architecture change.

### When the box is busy

Budgets tight enough to catch a 1.75x regression are also tight enough for a
loaded machine to fail them: a known-good build measured 8572 MB/s on case (b)
against its 12000 floor at 1-minute load 24.4 on 12 cores, with per-trial
spreads widening from 1.15–1.35x to 1.38–1.53x.

Rather than loosen the budgets — which is what anyone would eventually do to
stop a flaky gate — the suite refuses to judge. Above `LOAD_LIMIT` (default
`max(2.0, cores/2)`) a budget MISS is reported as `INCONCLUSIVE`, is not
counted as a failure, and the summary states that the run gated nothing. A
PASS under load is still reported as a PASS, since beating a floor on a busy
box is if anything stronger evidence.

That is reported through the EXIT CODE, not just the summary, because the
first version of this downgrade exited 0 and turned a flakiness guard into a
detection hole — a build with a 3.4x/68x/5.5x regression exited green whenever
the box was busy, which at a default limit of cores/2 was the normal case:

| exit | meaning |
|---|---|
| 0 | gated, and clean |
| 1 | gated, and a budget failed |
| 2 | **NOT gated** — one or more budgets inconclusive |

So a green `make bench` on a loaded box is not evidence of no regression, and
now says so in a way automation can read (D14).

## Case (d), and why every optimization needs a case that EXERCISES it

Case (d) exists because of the sharpest R3 finding: deleting the BITMAP half of
the start prefilter (keeping only the memchr fast path — a plausible "simplify
the special case away" edit) costs ~1.5x on multi-first-byte patterns and
passed `make test`, `make bench`, the python oracle, the differential fuzzer
AND `compare/gate.sh`. Five nets, all green, on a real regression.

The cause was coverage, not margins: cases (a)–(c) all have exactly ONE escape
byte, so every one of them took the memchr branch and the bitmap branch was
unexercised anywhere in the suite. D12's claim that the prefilter was
"sabotage-validated" was true of half of it.

Case (d)'s budget is deliberately tighter than the /1.75 used elsewhere —
healthy measures 429–457, the sabotage 296–305, so 330 sits between them with
~1.3x headroom either way. A 1.75x margin would have let exactly this through
again.
