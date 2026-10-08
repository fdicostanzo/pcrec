# decfbB0a report — W5, the force loop's arm (B0 deliverable 10)

Branch `lane/decfbB0a` (off `lane/decfbB0`). Changes: `tests/core/alloc_check.c`
(W5 + trace support in the injector), `tests/core/CLAUDE.md`. Nothing under
`src/`, `cli/`, `lib/` (`git diff lane/decfbB0 -- src cli lib` empty).

## The witness
`w5_run()` in alloc_check.c, single-shot only, NOT a `Witness` row (its property
differs: rc 0 + exactly one `decline:force-failed` row). Pattern `(?:a?){700}`,
default options, `pcrec_emit_facts`. Property: a trial whose failing allocation
is inside the force loop returns non-NULL text carrying exactly one
`decline:force-failed` row; never NULL, never a signal.

## How N was chosen (probed, not guessed)
- Forced derivations allocate only via `pcrec_kset_walk`'s four arena requests
  (kset.c:183-186), and the arena reaches malloc only when its block is full.
  Most patterns' force loops allocate nothing (kset_walk is already memoized by
  prefix_k, so only NULLABLE patterns, whose kset_walk is not asked by the
  compile, derive it in the loop). Of ~100 probed shapes only nullable
  large-NFA ones hit: `(?:a?){N}` hits at N=700,800,1100,1200,...; N=700 is the
  cheapest (K=220 allocations, ms per trial).
- Measured: loop = 1 allocation, call #209
  (`arena.c:19`, malloc of a new arena block); emit_facts total K=220.

## How in-loop is told from out-of-loop (control independent of the listing)
Site traces (`__FILE__:__LINE__` per call, injector `trace_on`) of two
in-process profiling passes of `pcrec_compile_driver`: hook-less (loop skipped,
`if (facts_hook)`) and hooked (no-op recording hook). They agree until the
first force-loop allocation (index d=209); loop length L = hook-entry count
minus hook-less K (=1; the render-prefix allocation after the loop is in both
traces, which is why bare totals cannot place the loop). A third pass
(`pcrec_emit_facts`) is cross-checked to reproduce the hooked trace through the
loop. No listing text is read to decide "in loop".

Trial classes: in-loop N must give code 20 (text, exactly one force-failed
row); 6 pre-loop margin calls must be DIAGNOSED (NULL+msg); post-loop calls
(render prefix + listing row rendering) are NOT asserted, reported in a NOTE,
but none may show a force-failed row. Floors (K35): loop length >= 1
(measured 1, so floor = measured, not half: below 1 nothing is left to assert);
total allocations >= 100 (measured 220).

## Measured populations (green tree)
emit_facts K=220; hook-less compile K=209 (includes the final render alloc);
loop: calls 209..209 (1 trial, site arena.c:19) -> force-failed row;
6 margin trials (203..208) diagnosed; 11 post-loop trials (210..220):
2 diagnosed, 9 killed by SIGABRT.

## FINDING (not fixed; outside B0 scope): pcrec_emit_facts aborts on OOM in the listing-render phase
9 of 11 post-loop trials die with SIGABRT: the listing's row buffers
(`FactsRows` in src/dump/facts_dump.c, `pcrec_sb_row`/`pcrec_sb_puts` on detached
StrBufs, `sb.c:29-ish sb_grow`: `abort()` when `sb->cx == NULL`) have no error
channel. Same class as K7 / lens-5 F1, on the `--emit-facts` path that no
witness covered. W5 reports the count as a `NOTE:` and does not assert it (an
assertion would make `make test` red on a pre-existing defect). Recommend the
manager file a K-entry; once fixed, W5's NOTE population can be promoted to an
asserted "diagnosed" class. (The prefix-render allocation, call #210, is
already diagnosed.)

## Both directions
Green (today's tree):
```
PASS: W5 (force loop, --emit-facts): of 1 in-loop forced allocation failure(s) (calls 209..209 of 220, pattern '(?:a?){700}'), every one answered rc 0 with exactly one `decline:force-failed` row; 6 pre-loop margin trials diagnosed
NOTE: W5 (force loop, --emit-facts): the 11 post-loop (render-prefix + listing-rendering) trials: 2 diagnosed, 9 killed by a signal, 0 other -- not asserted by W5
checks passed: 5 / checks failed: 0
```
RED, plant A (uncommitted, reverted): compile.c `if (cx.job && cx.job->pf.forcing) {`
-> `if (0 && cx.job && cx.job->pf.forcing) {`:
```
FAIL: W5 (force loop, --emit-facts): N=209 is IN the force loop (failing site arena.c:19) and the listing was REFUSED (NULL + message: the forcing arm did not absorb, or sits below the nomem arm) -- expected rc 0 with exactly one `decline:force-failed` row (code 22)
checks passed: 4 / checks failed: 1   (W1-W4 PASS unchanged), rc=1
```
RED, plant B (S-F0: the 5-line `pf.forcing` arm cut and pasted to just AFTER the
`if (cx.failed_nomem) {...return -1;}` block): identical FAIL line, rc=1
(an arena failure in the loop sets failed_nomem, which then wins).
RED, plant C (floor; scratch copy of the C with the pattern `a(b|c)+d`):
```
FAIL: W5 ...: the force loop allocates 0 time(s) for 'a(b|c)+d', floor 1 -- this witness stopped reaching the arm (K35): re-probe a pattern whose forced derivation opens an arena block
```
All plants reverted; `git diff -- src cli lib` empty.

## Commands run / pass counts
- `make BUILD_DIR=build-alloc CFLAGS="-O1 -g -include .../alloc_inject.h" build-alloc/libpcrec.a`
  then `unit_build` of alloc_check.c and run (probe/plants), scratch under build/scratch.
- `make alloc` (--both): all PASS; table W1 67, W2 15, W3 255, W4 209 (0 absorbed
  both modes); `PASS` lines 9 (W1-4 x2 + W5); "checks passed: 9, failed: 0";
  `alloc: every forced allocation failure was diagnosed, not aborted`.
- run_resource_tests.sh §2b leg, replicated exactly (same unit_build of the
  edited file against a freshly built injected lib, argument-free run, same two
  greps): rc=0, 0 lines matching `KILLED THE PROCESS BY SIGNAL|SUCCEEDED THROUGH`
  (W5's NOTE wording was chosen not to match the §2b grep), 5 PASS.
  The whole run_resource_tests.sh was also launched (log build/scratch/res.log,
  not committed); see the handback for its status.
- No `make test` run (manager's at merge). No script change was needed:
  §2b and run_alloc_tests.sh build alloc_check.c with the existing unit_build.
