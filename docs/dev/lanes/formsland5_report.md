# formsland5 report

## Summary
Merged the two r39 fix branches into lane/memfn-forms and applied formsfixi's "for the landing" doc lines. No conflicts, no code touched by this lane.

## Merges
- `lane/memfn-formsfixi` merged alone: clean (ort), no conflicts.
- `lane/memfn-formsfixj` merged alone: clean (ort). It regenerated `tests/ci/cloud_mech_shards.tsv`; no conflict, so no regeneration was needed. `tests/ci/cloud_mech_check.sh tests/ci/cloud_mech_shards.tsv`: PASS, 90 shards hold the 1335 sabotage ids exactly once (S3310-S3312 from fixi and S3320-S3321 from fixj included).
- Doc lines (formsfixi_report.md "For the landing", K12): S3312 added to the `run_shell_checks.sh` header (4) comment and to `tests/compound/CLAUDE.md` (4). Comment/doc text only (commit 8bb2a90df).

## Validation
Local, nice, -j4, gnutimeout; logs under /var/tmp/pcrec-pcrec/scratch/memfn/formsland5/.
- make: rc 0. make strict: rc 0 (whole tree clean with -Werror -Wshadow; kit target table passes).
- test-codegen, test-registry, test-rxtsource, test-memfn-finder, test-memfn-link, test-resource, test-cli, test-compound: all rc 0.
- tests/compound/run_lever_fence.sh: rc 0.
- memfn/tests/run_g2.sh --quick (TMPDIR set; first attempt failed only for an unset TMPDIR): checks passed 70358672, failed 0.
- memfn/tests/run_g2_win.sh: rc 0 (G2W wall total 153s).
- cards.py selftest: 197 checks, 0 failed. cards.py dry (WIDTH_FLAG=none): cells 1482, built and gated 1482, failures 0; layout twins: 38 twin exes, byte-different 38, rxa_search moved 38, answer-gated, failures 0.
- tests/ci/cloud_mech_check.sh: PASS. `python3 -I scripts/m6read_check_sab_anchors.py`: 1335 sabotages, all anchors resolve.
- emit_sweep.py --ref 1aec5d4d3: movers=0 asymmetric=0 on every stream (argv 7071, composition 465, dumps 7), DONE rc=0.
- Not run, per brief: full make test, queue jobs, timing, cloud.

## STATE AT HANDOFF
Branch lane/memfn-forms, rulings file empty at every read (no entry applied). Merge tip is the commit after 8bb2a90df (this report).
OWED: none
