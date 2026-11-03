# t588tri — triage of job 588's BAR FAIL (2026-11-02)

Read-only triage (lane t588tri, opus), written up by the kit manager from the lane's final message (the harness refused the lane's own report file). Run: jobs 210-216 kit-t588-* on main 53aaef4f1+ (abi 94); verdict `== s3t BAR FAIL` in worktrees/t588/build/t588/table.log. Recompute scripts: /var/tmp/pcrec-pcrec/scratch/memfn/t588tri/{recompute,rel}.py. The FAIL holds under every reading of the allowance; the allowance defect HIDES more fails, it does not cause one.

## (a) smp20 `(?i)x/1234` (WALK/one/run; RTE/DEF 4.03x random, 2.79x none, 1.66x real; SIMD-on 5.27x none)

- DEF (no-window-search,no-window-skip): offset-skip, memchr on '/' (one member, run-pinned at offset 1), then verifies "/1234".
- RTE (cover, S3 E-find): picks position 0, set {X,x}, BY MASS ALONE (memfn/src/window.c phase-1 A rows; the one-member admission scan_ok, window.c:446-449, is what makes the skip's A-model pick '/'), found by the two-stream bounded look-ahead (two memchr streams, 128-byte doubling windows). '/' is never searched.
- Candidates per subject: real x 2338 vs / 1026; none x 1388 vs / 0; random x+X 21788 vs / 10856. The cover stop has more candidates on every class AND pays two streams where DEF pays one glibc memchr.
- SIMD-on without -march runs the SSE2 w16 vrun: it compares position 0 only (the w32 arm that also checks '/' is compiled out without __AVX2__): 5.27x on none vs glibc memchr; random 0.85.
- Class: the stop-pricing gap ([MEMFN-PAIRSTOP] / D176 Q1), a sibling of EMIT-4 on the PAIR renderer. NOT the listed Known gap (that names only the 3+-member set walk).

## (a) smp04 `[a[:b]` (WALK/one/norun; 4.475x random, passed only by the allowance; real 0.80x)

- Both arms walk byte by byte: DEF through a 256-entry table, the kit through a compare chain (gcc: sub/cmp/ja/bt). Inference (not perf-counted): branch mispredicts on random bytes (~16 % of bytes land in [58,98]). Renderer FORM, not pricing.

## (b) The allowance

- read_588.py counts throughput calls as hits+1; the 24,498.593 ns/call figure comes from year4/none with calls=1, i.e. a whole-pass delta (5.85 % of a 1 MB scan), then applied to cells with thousands of calls: throughput is effectively uncapped.
- Alternatives: exclude calls==1 -> 3.994 ns/call; or a relative allowance 0.0585.
- Floor-only flips to FAIL: smp02, smp04 (4.475), smp05, smp08, smp12, smp17, smp20 real/none; pr02, pr03, pr04, pr05, pr07, pr09 (real/dense/mixed). Stratum COVER-PAIR flips PASS -> FAIL (gmean 1.068 > 1.028), so the two-stream term fails too.
- Relative 0.0585: smp02/05/12/17 and pr03 pass; the rest still fail. The main §6 table is unaffected.
- Side flags: search_short's 14.766 comes from a 22 % layout swing (word-digit/real DV3); the reader computes the allowance PER REGIME where the design says one number over the run; the driver's DV flags (32/64/64+loops32) differ from the design's 16/32/64.

## (c) Options (not decided)

1. Kit fixes, each an abi event: smp20 — EMIT-4's minimum repair extended to the pair (M), or the full priced choice (L, deferred with pricing); smp04 — a table-form walk test (S).
2. Name smp20 a D176 Known gap (smp04 does not qualify).
3. Fix the bar: Goal 2 wording + the reader + a table-stage re-read (no box time). This makes the bar redder.
