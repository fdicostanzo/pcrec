# K24 bisect findings

Diagnosis only (per the brief) — no fix lands from this lane. Bisected in
`worktrees/k24bisect` (branch `lane/k24bisect`, off `main` at `b726a25`).

## Result

**First bad commit: `1dbb6ce9f29f1f9b86d62cbac8f18162915512f1`**
("`[M4.4] API BREAK: caps-array search signature, fixed ABI types,
match/match_caps/info entries, PCREC_* flags word`", 2026-08-14 22:48:22 UTC).

**K18 is exonerated.** The brief's prime suspect (K18's path-sensitive
closure rewrite of `src/ir/dfa.c`, landing 2026-08-15) does not touch the
code path this regression lives in — see "Why K18 is clear" below. The
regression is fully present a full day before K18 lands, at the very next
commit after `4c26989` (2026-08-14 18:37:33 UTC, last-good), which is also
the point where `docs/dev/known_issues.md`'s window boundary assumptions
about `--no-captures` and `rx_info` turned out not to hold (see "Brief
corrections" below).

**The mechanism is not an algorithmic regression in the DFA scan.** The
emitted scan tables (`rx_fcls`/`rx_ftr`/…) and the hot-loop machine code are
byte-identical before and after 1dbb6ce, and stay byte-identical all the way
to the current tip (`b726a25`) — K18, possessify, revdet, and everything
else in the window never touch this pattern's emitted matcher at all (see
"HEAD vs culprit" below). What changed at 1dbb6ce is that `rx_search` picked
up two new same-translation-unit callers (`rx_match`, `rx_match_caps`, added
for the API break). That alone is enough to make gcc -O2's partial-inlining
pass split `rx_search` into a thin trampoline plus a separately-placed
`rx_search.part.0` holding the actual loop — and it is *that split*, not
anything about the pattern or the DFA, that the throughput regression tracks.
Confirmed causally with a compiler-flag control experiment (below): turning
partial inlining off at the culprit commit, with nothing else changed,
recovers the full historical floor.

## Per-point table (final run, CPU-pinned, quiet box)

All ten points below are the actual points needed to bracket the window —
the automated `git bisect run` walk (unpinned first draft, see the
"methodology correction" section) visited 8 of them and inferred the boundary
by elimination against the two pre-established endpoints; this table is a
clean, deliberately re-measured re-run of all ten, WITH pinning, done after
the mechanism was understood, so the reported numbers are trustworthy on
their own rather than inherited from the noisier first pass.

| commit | date (UTC) | load 1m/5m | result | median MB/s | trials |
|---|---|---|---|---|---|
| `b6adda5` | 2026-08-11 23:48:49 | 0.51/0.39 | good | 391.095 | 391.238, 389.402, 391.095 |
| `f943060` | 2026-08-13 03:30:30 | 0.55/0.40 | good | 390.337 | 390.337, 389.629, 390.446 |
| `84e5956` | 2026-08-14 15:10:50 | 0.55/0.40 | good | 389.871 | 390.655, 389.871, 386.249 |
| `308a65d` | 2026-08-14 16:49:52 | 0.50/0.39 | good | 390.423 | 390.345, 391.776, 390.423 |
| `8476717` | 2026-08-14 17:55:17 | 0.50/0.39 | good | 388.503 | 389.698, 388.503, 386.370 |
| `5e1fbf0` | 2026-08-14 18:10:04 | 0.54/0.40 | good | 390.062 | 390.062, 390.199, 387.416 |
| `3e2ec2f` | 2026-08-14 18:18:15 | 0.54/0.40 | good | 389.885 | 389.885, 388.834, 390.609 |
| `9119f21` | 2026-08-14 18:35:34 | 0.58/0.41 | good | 387.090 | 386.640, 387.090, 390.793 |
| `4c26989` | 2026-08-14 18:37:33 | 0.58/0.41 | **good (last-good)** | 390.141 | 390.141, 391.578, 389.006 |
| `1dbb6ce` | 2026-08-14 22:48:22 | 0.58/0.41 | **bad (first-bad)** | 293.437 | 293.437, 289.199, 296.475 |

Nine points hold a tight 386-392 MB/s band across three days of unrelated
history; the very next commit drops to ~293. `1dbb6ce` and `4c26989`
(its parent) were additionally each re-measured 2-3 more times independently
during the investigation (10 pinned repeats each in the mechanism section
below) — consistently ~290 and ~390 respectively. Box was quiet throughout
(load 1-min never exceeded 0.6; the LOAD_MAX=2.0 gate in the probe never
fired).

## Why K18 is clear

Generated `(alpha|beta|gamma|delta|epsilon)` with `--no-captures` at
`1dbb6ce` and at the current tip `b726a25`, diffed the two `gen.c` files: the
`rx_fcls`/`rx_ftr` DFA tables and the `rx_search` body are **identical**. The
only diff between 1dbb6ce's and HEAD's output is in code this pattern's
measurement never exercises — the `rx_match`/`rx_match_caps` wrappers gaining
a `work_budget` give-up propagation line each (D49, ENG-BREP, unreachable on
a DFA artifact) and `rx_info`'s `.abi`/`.flags`/`.work_budget` fields. K18
(2026-08-15), possessify/revdet/counter-K, and every other commit in the
window after 1dbb6ce never touch this pattern's emitted scan code at all.

## The mechanism, in detail

Compared the emitted `gen.c` for `(alpha|beta|gamma|delta|epsilon)` at
`1dbb6ce^` (`4c26989`, last-good) vs `1dbb6ce` (first-bad), no
`--no-captures` at either (see "Brief corrections" — the flag doesn't exist
yet at either commit). The diff is small and entirely explained by the API
break itself:

- `rx_search`'s signature changes (`rx_span *m` → `ptrdiff_t (*caps)[2]`) —
  a pointer either way, no algorithmic difference.
- The one line that fires only on a **successful match** gains a cast
  (`m->start = sfound` → `caps[0][0] = (ptrdiff_t)sfound`). The bisect's
  subject (`c_alt_absent.bin`, built by `purge_words()` to guarantee zero
  occurrences of all five branch words) never matches, so this line never
  executes during the measurement either way.
- Three things are newly **appended after** `rx_search` in the same file:
  `rx_match()`, `rx_match_caps()` (both one-line wrappers that call
  `rx_search()`), and the new `const struct rx_info` static data.

Compiling both at `-O2` and comparing assembly: `1dbb6ce^`'s `rx_search` is
one self-contained function containing the full scan loop inline (146 lines
of `.s`). `1dbb6ce`'s `rx_search` is a 15-line stub —
`cmpq %rdx, %rsi; jb .L38; jmp rx_search.part.0` — gcc's partial-inlining
pass has outlined the real loop into a separate symbol,
`rx_search.part.0`, called via `call` from the two new wrappers and via
`jmp` from the external entry point. Diffing `1dbb6ce^`'s inline loop body
against `1dbb6ce`'s `rx_search.part.0` body (mnemonic-for-mnemonic): they
match except for one `cmpq`/`xorl`/`jb` triplet that moved into the new
trampoline stub — i.e. **the executed instructions are the same program**,
just split across two symbols instead of one.

**Controlled causal test** (pinned to core 2, `taskset -c 2`, 10 back-to-back
trials, same binary both times, only the compiler flag changed):

| build | median MB/s (10 trials) |
|---|---|
| `1dbb6ce`'s `gen.c` + driver, plain `-O2` (the split exists) | 288.6 – 293.8, all ~290 |
| same source, `-O2 -fno-partial-inlining` (split suppressed) | 389.6 – 391.8, all ~390 |

Turning off exactly the one compiler pass responsible for the split — with
literally nothing else different, same commit, same `gen.c`, same driver,
same subject — takes the culprit commit from the regressed floor back to the
historical floor. `nm` on the two builds confirms: `rx_search.part.0` is
gone with `-fno-partial-inlining` and `rx_search` is a normal 336-byte
function again.

Why the split costs ~25-26%: the loop body's own instructions are unchanged,
but every call must now go through the trampoline's extra `jmp` into a
separately-placed function, and that function's *placement* (its byte offset
relative to whatever else got linked into the same binary — the built-in
driver's own code, in this pattern's case) is no longer something the
compiler treats as tied to the loop's own alignment directives. This is a
textbook code-layout sensitivity (Mytkowicz et al.'s "measurement bias from
environment"), not a change in what the DFA does. It is a genuine, structural
side effect of 1dbb6ce's refactor (the new in-TU callers are what trigger the
split at all — see the mnemonic-identical loop body above), not noise: with
CPU pinning, the split's cost reproduces at ~290 MB/s to within a few percent
every time, and the unsplit control reproduces at ~390 every time.

## Methodology correction (read before trusting an unpinned rerun of this)

The brief pointed at `compare.sh`'s pinning convention (`taskset -c
$BENCH_CPU`, R2-B1/B3) as the model to replicate for "commensurable" numbers,
and the first draft of `probe.sh` **missed porting it** — every trial in the
first draft ran unpinned. This was not caught by the bisect's own dead-zone
guard, and — worse — the automated `git bisect run` walk never re-measured
the two endpoints at all: `1dbb6ce` was supplied as the `bad` boundary from a
single manual pre-bisect run, and the walk only needed to find `good` all the
way up to its parent, which it did cleanly 8/8. Chasing down why a
from-scratch reproduction of that one manual "bad" reading kept disagreeing
with hand-built control binaries (392-395 MB/s, consistently) is what
surfaced the real mechanism above: unpinned, the SAME compiled binary
measured anywhere from 287 to 397 MB/s across 20 back-to-back runs once the
partial-inlining split was present (never that variable before the split, or
after `-fno-partial-inlining`) — process/core migration and per-core
frequency ramp compound with the split's placement-sensitivity in a way a
monolithic function never exposed. `probe.sh` now pins every timed
invocation (`taskset -c 2`, ported from `compare.sh`'s own PIN construction);
re-verified both endpoints AND the full 10-point table above under pinning,
all fully reproducible with tight (<1%) trial-to-trial spread.

**Practical upshot:** this box needs `taskset` for any single-binary
throughput comparison to be trustworthy after 1dbb6ce, because the split
function is layout-sensitive in a way the pre-split code never was — an
unpinned run can land anywhere in a ~290-397 MB/s range for the *identical*
binary depending on incidental scheduling. `compare.sh`'s own numbers
(294-304 MB/s, K24's filed range) are pinned and therefore reproducible
*for that specific harness's binary layout* — but that reproducibility is a
property of `compare.sh`'s own fixed link, not evidence that ~294-304 is
the built matcher's "true" rate independent of layout; the hand-built
control above shows the identical instructions landing at ~390 under a
different link (a different driver `main()`, or `-fno-partial-inlining`).

## Brief corrections (docs win per the task's own instruction)

Two assumptions in the brief did not hold once checked against history, and
the probe was built to route around both rather than assume them:

1. **`--no-captures` does not predate the window.** It was introduced in
   `242dcf3` (2026-08-15 00:15:50, the VM emitter commit), not before
   2026-08-11 as stated. Before `1dbb6ce`, there is only one engine (no
   `want_caps`/VM concept exists at all — `grep` for `want_caps` in history
   finds exactly one introducing commit, `242dcf3`), so nothing needs
   pinning; the pattern is DFA-only by construction. `probe.sh` detects
   flag availability via `pcrec --help` and only passes `--no-captures` when
   offered.
2. **There is a `rx_search` ABI break inside the window** (`1dbb6ce` itself,
   coincidentally the same commit that turns out to be the culprit): before
   it, the generated header is `int rx_search(const unsigned char *s, size_t
   n, size_t startpos, rx_span *m)` (matches `tests/bench/bdriver.c`'s
   shape, no `RX_NCAPS`/`rx_info`); from it onward, the modern `ptrdiff_t
   (*caps)[2]` signature with `rx_info`/`ENGM_DFA` stamp is already present,
   a full ~1.5h before the VM engine (`242dcf3`) that the stamp exists to
   distinguish. `probe.sh` detects the era via `RX_NCAPS` presence in the
   emitted `gen.h` and builds the matching driver variant, and only asserts
   the `ENGM_DFA` stamp when the stamp mechanism exists at all.

Neither correction changes the bisect's validity — both eras compile and run
this pattern correctly, `probe.sh` just has to speak both dialects to keep
one continuous probe across the whole window as asked.

## Files here

- `probe.sh` — the standalone bisect probe (CPU-pinned; lives here for
  provenance/audit, but `git bisect run` itself invoked a copy from the
  session scratchpad, since historical commits in the bisect range predate
  this file — see the header comment).
- `gen_subject.py` — regenerates `compare.sh`'s case-(c) subject
  (`(alpha|beta|gamma|delta|epsilon)`, absent, 8 MB) bit-for-bit, by
  replaying the same seeded RNG draw order compare.sh's embedded generator
  uses for cases (a)/(b)/(c) in sequence.

## Not done here (by design)

No fix. The obvious next question — is a source-level change (e.g.
`__attribute__((noinline))` pragma-free ways to keep `rx_search` monolithic,
or simply not adding same-TU wrapper callers, or accepting the split but
forcing consistent hot/cold linker ordering) the right lever, versus treating
this as one more entry in a broader "check what gcc's own heuristics do to
every emitted engine" audit — is a design call for the manager, not a bisect
deliverable.
