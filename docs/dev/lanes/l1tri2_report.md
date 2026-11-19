# l1tri2 report: triage of the red make test on lane/l1build

## Summary
Job 202-l1fix-b202611191316002982870.test (make test at 07c840368) failed
rc=2 in three sections: test-rxtsource, test-startset, test-memfn-manifest.
No real regression. Two are stale expectations from one corpus commit
(0c42988cf, r53 F3: an 11-line pcre2-only block in tests/altcls/altnf_rules.rxt);
the third is a sampling brittleness in the site census that the same
corpus edit exposed. Fixed in 3e23df7e3; each section re-run green alone.

## Failing sections
- test-rxtsource (Makefile:680)
- test-startset (Makefile:1708), the [vm-movers] checks only
- test-memfn-manifest (Makefile:1483), rule 5 only

## Cause per failure
- test-rxtsource: STALE EXPECTATION. Census found 341/7072/98624 vs pinned
  341/7071/98618; C3 SKIP and pcre2-only each +6 (PASS and VERIFIABLE
  unchanged). Exactly 0c42988cf's block: +1 block, +6 case lines, pcre2-only.
- test-startset: STALE EXPECTATION. manifest_s2_vm_{auto,forced}.tsv key rows by
  file:line. The new block is a correct mover at altnf_rules.rxt:80 (+1 row in
  each manifest) and every later altnf_rules row moved +11 lines (same text and
  options). The log's MOVER-NOT-IN-MANIFEST / MANIFEST-NOT-MOVER pairs are
  that shift. Control: green on main at 472a53fb6 before the corpus commit.
- test-memfn-manifest: rule 5 "PF lists DFA_HAT and no corpus-pass site stated
  it". The corpus pass compiles a strided sample (every 18th of ~5500 unique
  patterns); one added unique pattern moves the alignment of everything after
  it, and the one sampled pattern that stated DFA_HAT fell out. Not a
  behaviour change: control green on main (472a53fb6), red on the branch,
  and green after the fix with the same compiler.
  Class: STALE EXPECTATION (check design), not environment, not regression.

## Fixes
3e23df7e3 on lane/l1tri2:
- tests/rxtsource/run_rxtsource_tests.sh: CENSUS_/RUNSH_BLOCKS 7072, _LINES 98624,
  C3_SKIP 75193, C3_SKIP_PCRE2ONLY 34937 (each with a provenance note).
- tests/startset/manifests/manifest_s2_vm_{forced,auto}.tsv: +1 row at :80,
  later altnf_rules rows +11, provenance comment line.
- tests/memfn/site_census.py: CORPUS_WITNESSES, a fixed pattern appended to the
  strided sample (`\b(?:true|false|null)\b`, the DFA hat's witness), so a kind
  the manifest lists no longer rides on where the stride lands. This is the
  one non-trivial item: it is a check edit, and the manifest check's other
  kinds still depend on the sample; a later brittle kind would want the same
  row (this is the first, not a second for the same cause).
No allowlist rows added.

## Validation
Run alone in worktrees/l1tri2 (build nice -j4): test-rxtsource rc=0 (341 files /
7072 blocks / 98624 lines), test-startset rc=0 (35 checks passed, 0 failed),
test-memfn-manifest rc=0 (301 patterns sampled, 558 compiled). Control
test-memfn-manifest on 472a53fb6: green. Control worktree removed with wtprune.
Full make test: OWED, key 202-l1tri2-test (cap 5400, perfrun label l1tri2),
queued, not waited on.

## STATE AT HANDOFF
Branch lane/l1tri2 at 3e23df7e3 plus this report commit; rulings file had no
entries. OWED: boxqueue key 202-l1tri2-test (full make test at the branch tip);
read its verdict with scripts/monread / the `*** [...test-X] Error` lines.
Other sections of the earlier red were green (only the three above failed).
