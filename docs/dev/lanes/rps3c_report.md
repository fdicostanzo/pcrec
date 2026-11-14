# rps3c — triage of the two stage-3 cloud reds on lane/rps3 (lane report)

Lane rps3c (opus), branch `lane/rps3` from `1479e107e` (lanes rps3, rps3b ended).
Cloud run `rps3-test` 43429576550 at `1479e107e` had two reds: shard 11
`test-resource` (`(a|b){1,30000}` over the CPU budget, twice) and shard 12
`test-cand-oracle` (`[cand-oracle-coverage] rows with no witness: untestable`).

## STATE AT HANDOFF

- STATE: delivered-with-owed. Both reds are fixed and committed; the suites,
  the two byte sweeps and the cloud dispatch are QUEUED as one chained batch
  (OWED below). No rulings file was named in the brief.
- Validated here, standalone: `make strict` clean (the minimize fix);
  `bash tests/codegen/run_cand_oracle.sh <worktree>` (the exact command
  `make test-cand-oracle` runs) 166 passed, 0 failed, and four plants on the
  new allowance each red (below); timings below.

## CHANGES

**Red 1: the CPU budget. The cause is NOT stage 3's req walk.** Measured on
this box (Zen 4), `build/pcrec -p rx --pattern '(a|b){1,N}'`:

| N | main `8459da29a` | branch `1479e107e` | branch + fix `fc01f4d68` |
|---|---|---|---|
| 3000 | 0.13 s | 0.12 s | - |
| 10000 | 1.38 s | 1.37 s | - |
| 20000 | 5.50 s | 5.66 s | - |
| 30000 | 12.3-15.5 s | 31.4-41.6 s | 13.9-14.1 s |
| 30000 `-fno-scan-edge` | 12.9 s | - | 13.5 s |

`perf` puts 99.9% of both builds in `pcrec_minimize_dfa` (`src/opt/minimize.c`,
byte-identical on both sides): K25's Moore refinement, O(n) rounds. Both builds
minimize the SAME machines (gdb at entry: two calls, n=30001, ncls=2, identical
SHA-1 of every state's transitions/views/accept) and retire the same 220e9
instructions; the branch took 171e9 cycles to main's 67e9, with 92.7M dTLB load
misses to main's 1.0M, all of them on one instruction: glibc's AVX-512
`__memcmp_evex_movbe` masked 32-byte load of the 16-byte signature key. With the
heap layout pinned (`GLIBC_TUNABLES=glibc.malloc.mmap_threshold=131072`, or
`glibc.malloc.hugetlb=1`) both builds run at ~65e9 cycles. So stage 3 changed
only WHERE an earlier allocation left the heap, and that made libc's memcmp in
the hot loop slow; the walk is linear and was not touched.

Fix (`fc01f4d68`): the key copy and compare in `pcrec_minimize_dfa` are plain int
loops instead of `memcpy`/`memcmp` (a signature is ncls+2 or +3 ints), with a
comment saying why. 218e9 instructions, 73.5e9 cycles, 0.6M dTLB misses; the
emitted C is byte-identical (diffed; only the `#include "<out>.h"` name differs,
as it does between any two `-o` names). `a{0,25000}` 13.3 s main / 14.6 s fix,
`[a-z]{0,30000}` 18.7 s / 20.5 s on this box (the fix is ~10% slower than main's
lucky layout and 2.5x faster than the unlucky one; layout no longer decides it).
The CPU budget `K7_CPU=45` is untouched. K25 itself (Moore's O(n) rounds) is not
fixed; tests/resource's header already names it as what sets the budget.

**Red 2: `untestable` has no witness, and none can exist on today's kit.** Its
premise is the kit DECLINING a stated run on the pre-check (`pres[run].verify`
0, no verified member; `docs/design/memfn/part_d.md` §9 items 2-3, on
lane/memfn-partd). Today's kit has no decline row: `req_untestable_applies` asks
with no proof, so no span is `proven`, and every run span is decided by P0, P3
or P9 (`memfn/src/finder.c`), whose links all verify. Swept to confirm (scratch
script over rps3b's census population, 7423 patterns, `build/pcrec-harness`
default, `--harness=run-pos-sets`, `--harness=alt-union-run`): 0 compiles
emit `_REQ_WHY "untestable"`. No lever or `--memfn=` deny makes the kit decline.

The check's header allowed declaring only FINISH take cells, so `146900557`
extends the same allowance file, `tests/codegen/cand_oracle_unreached.tsv`,
to ROW lines (ROUTE and HAND `-`), and lists `untestable` with the argument,
the sweep and its producer (Part D's decline row; that landing adds the
witness and deletes the line). Not weakened: every row is still witnessed or
declared, the population check counts both, and three new failure modes hold
the declaration. Plants, each run with a prebuilt trace binary
(`CAND_ORACLE_BINS`) and reverted:
A drop the declaration -> `rows with no witness: untestable` (1 fail);
B declare the witnessed row `emitted` -> "declared unreached AND has a witness
line" + "a witness compile reaches it (stale allowance)" (2 fails);
C declare `nosuchrow` -> "names no row of cand_rows[]" (1 fail);
D add an `untestable` witness line while declared -> "declared AND has a witness
line" + the line's own reach failure (2 fails). The clean run reads
`row 'untestable' declared unreached, reached by none of 7154 witness row hits`.
`tests/codegen/CLAUDE.md`'s entry for the file says so.

## OWED

- QUEUED batch `b202611130843282545155`, jobs 200-207 (owner `rps3c`, stages file `worktrees/rps3/build/STAGES.rps3c`,
  each stage waits for the one before it to go green; verdicts by
  `scripts/monread rps3c`): `make strict`; `make test-resource`;
  `make test-cand-oracle`; `make test-codegen`; `make test-rxtsource` (verdict by
  `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`); `emit_sweep.py --ref
  1479e107e` (the branch's tip before this lane, which isolates its two commits;
  expected movers NONE, file `$PCREC_TMPDIR/scratch/rps3c/sweep_base_movers.tsv`);
  then stage `cloud`: `git push origin lane/rps3` and `scripts/cloudrun --owner
  main --kind test --name rps3c --ref lane/rps3` (fires only if every stage
  before it is green, so a local red never costs a cloud run); last, `emit_sweep.py
  --ref main` (movers file `.../sweep_main_movers.tsv`): main is 27 commits ahead
  of the branch's base `f066e84ee`, so a mover there may be main's own, not the
  branch's; rps3b's job 208 already swept the branch against its base, GREEN.
- If stage `cloud`'s push fails in the queue's non-interactive shell, run the
  two commands by hand from the worktree.
- At the joint landing with lane/memfn-partd: add `untestable`'s witness to
  `tests/codegen/cand_oracle_witnesses.tsv` and delete its line from
  `cand_oracle_unreached.tsv` (the check reds on the stale allowance otherwise).
