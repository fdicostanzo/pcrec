# l1ttri report: triage of the red make test on the L1 landing branch (b44c334b8)

STATE: partial (2 of 3 sections fixed; test-memfn-arch stopped by the allowlist rule)

## Summary
Red job 202 (perfrun at b44c334b8, contaminated=YES) had three sections. All three
reproduced ALONE and quiet, so none is LOAD. Two are fixed on lane/l1ttri (commit 2e9e86126);
the third needs a manager ruling (STOP rule: two prior allowlist rows for the same cause).

## Failing sections
- test-codegen (tests/codegen/run_dfa_stamps.sh): `[agreement] the empty-engine bucket differs from its named manifest`.
- test-stackdepth (tests/thread/run_stackdepth_tests.sh): `[DD-10] look nested 250 deep` and
  `lookbehind nested 250 deep` KILLED pcrec_compile (exit 139) on the 442368-byte thread.
- test-memfn-arch (tests/memfn/run_arch_blind.sh, C4): NEW architecture vocabulary in
  tests/lookaround/d27_l1/l1d27_listing.tsv (1 hit) and l1d27_witnesses.rxt (5 hits), class 1 isa-name.

## Cause per failure
- codegen: STALE EXPECTATION, explained mover. Ten patterns (`(?:(?=z)a){3}`, `(?<=a)(?<=b)c`,
  `(?=[ab])[cd]x`, `(?=\x{e9})e.`, two `(?i)(?=k)(?-i)...z`, `[a-p](?<=q)`, `\d(?<=[a-z])`,
  `x(?=[^\x00-\xff])y`, `x[^\x00-\xff]y`) are now proven never-match by the L1 feature and take the
  empty engine. Each is a never-match by inspection (a lookaround whose set is disjoint from the adjacent
  step, or empty in the byte universe). Bucket 270 to 280; no lost member.
- stackdepth: REAL REGRESSION. Control (821f23545): look@250 hw=204552 rc=0. Branch: killed at 442368.
  Cause: `rb_zero_item_into` (src/facts/req.c) held the item's `RbRuns u` and `rr_cat`'s temporaries
  (-fstack-usage: 6800 B frame) in the SAME frame that makes the body's recursive `rb_walk`, so a nested
  lookaround cost about 6.8 KB per level more (rb_walk itself is 320 B). Not a limit issue.
- memfn-arch: needs a ruling. The D27 L1 corpus has the subject string "adx" (`(?:(?=ab)ac|(?=ad)ad)x`
  against "adx acx adxadx"), which the C4 isa-name class reads as the ADX extension. Same cause as two
  allowlist commits in the last 14 days (d7aaa3bc1 2026-11-06, 403aa54c8 2026-11-07; rows now at
  tests/memfn/c4_allowlist.tsv lines 50-55). Per the brief that is STOP: no row added. The files are
  D27-blinded and not edited.

## Fixes
- 2e9e86126, src/facts/req.c: the body descent is split from the item: `rb_zero_item_into` (pointers only,
  does `ahead++ / rb_walk / ahead--`) then `rb_zero_item_fin` (PCREC_OWN_FRAME, the `RbRuns u` work);
  `rb_look_item` no longer walks and is PCREC_OWN_FRAME. Behaviour identical; no emitted byte.
- 2e9e86126, tests/codegen/run_dfa_stamps.sh: EMPTY_MANIFEST plus the 10 patterns, with a [LOOK-L1] comment.
- NOT fixed: memfn-arch. Options: (a) allowlist rows for the two d27_l1 files (class 1, counts 1 and 5),
  the cheap path; (b) a subject that is not an ISA name, which the blinded author owns.

## Validation
- `make -j4` clean (no warnings) on lane/l1ttri.
- `bash tests/codegen/run_dfa_stamps.sh` standalone: checks passed 41, failed 0, empty bucket 280 EXACT.
- `make test-stackdepth`: both scripts green (5 and 39 checks, 0 failed); look@250 and lookbehind@250
  hw=204552, identical to the control 821f23545 (detached worktree worktrees/l1ttri-ctl).
- The other 20 test-codegen run_group scripts passed in the red job; not re-run here.
- `make test-memfn-arch`: NOT re-run after the fix (still red by the two adx hits).
- Full make test: NOT queued, it would end red on memfn-arch until the ruling.

## STATE AT HANDOFF
Branch lane/l1ttri at 2e9e86126 plus this report. Rulings file: absent, nothing applied.
Owed: none queued; one make test is owed after the memfn-arch ruling (start after 07:00 on 11-20 if it
would run past 20:00). Control worktree worktrees/l1ttri-ctl left in place (my one wtprune attempt was
refused by the classifier as too broad): prune it with `scripts/wtprune --apply --force l1ttri-ctl`.
