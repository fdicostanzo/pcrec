# covs2land report

## STATE AT HANDOFF
Rulings file: empty (no R-n applied).
OWED: none.
Merged tip: see CLOUD RUNS DISPATCHED for the exact sha the cloud runs test (the merge commit is c774d15c05585e0665373377cb19ec83907c4dc2; the report commit a88871a19 on top of it is the tip the cloud runs test).
Premise test: lane/memfn-forms = 105bf8ef412d92bcae7ce3567f41ef107a1767b8; merge-base with lane/covs2b = 60c2958ae, an ancestor of main (yes to both).

## MERGE AND CONFLICTS
`git merge lane/memfn-forms` (alone): exactly the six expected conflicts, none in src/, cli/, lib/, memfn/src/; no unlisted conflict.
- tests/ci/cloud_axes_shards.tsv, cloud_mech_shards.tsv: took our side, then REGENERATED with the kinds table's reweigh commands, from the worktree: `python3 -I tests/ci/cloud_units_plan.py axes --measured tests/ci/measured_axes.tsv --setup 70 --slots 20 --write` and `... mech --measured tests/ci/measured_mech.tsv --setup 35 --slots 30 --waves 3 --write` (needs build/pcrec). One hand edit, the same one lane covs2g made on covs2b: the generator emits the axes unit word `--window-search-width=4095`, which no AXES= selects (cloud_axes_check named it DROPPED); the row reads `--window-search-width` as on covs2b (weight 387 estimate, shard 9). After it `cloud_axes_check.sh` PASS (20 shards, 123 jobs, 32 passes once each), cloud_mech_check PASS (90 shards, 1345 ids once each), `make cloud-check` 16 passed 0 failed.
- docs/spec/tuning.md 2.43 para 3d: hand merge, the kit's text (the span forms sentences) with covs2b's clause "the widest fixed width the window search reports is §2.56's;" inserted; both statements kept.
- docs/dev/reviews/CLAUDE.md: our side; the kit's r44 and r45 index lines were already present from the auto-merge (one each, no duplicates). The pre-commit hook then refused the file at 12930 bytes (limit 12288): moved the three oldest dated index lines (r2-reqpast, r5-covcap-r2, r6-covcap-r3) verbatim to docs/dev/history/claude_md/docs__dev__reviews.md (file now 12009 bytes). Judgement call outside the brief; text-only move.
- docs/dev/reviews/NOTES.md and docs/dev/history/claude_md/docs__dev__lanes.md: both sides kept, markers deleted; a covs2land index line added to the lanes history.
Counts recounted: axes shard rows 100 unit rows after regeneration, mech 1345 ids (`grep -v '^#' tests/ci/cloud_mech_shards.tsv | tail -n +2 | wc -l`, and cloud_mech_check against tests/mech/sabotages); no duplicates (`cut -f1 | sort | uniq -d` empty on both). The mech unmeasured count moved 83 -> 107 (new kit rows take the mean).

## READERS CHECKED
- abi: `.abi` stamp is `#define PCREC_ARTIFACT_ABI 109` (src/gen/emit_dfa.c): found. match_api.md RX_ABI_H guard, error text and define: all 109, found. tests/codegen/run_codegen_tests.sh ABI_EXPECT=109 found. S693 sabotage AFTER is 108 on purpose (the main-side number, covs2b's re-aim). The recursion-identity pin: FILEPIN/ABASEPIN b2d73b6b1 (covs2b self-pin), unchanged. No stale 108 reader (`grep -rIn '\b108\b'` on those files: only S693's comments/AFTER, and a comment in tests/memfn/simd_guarded_check.py).
- MF_SITE_ABI 30: memfn/include/memfn.h:39, known.c:344, memfn_sites.h:54,211: found. MF_CLASS_V 11: defined in memfn.h, cited in known.c:704 and 7 other src sites: found.
- registry: span-loop row in docs/spec/registry.md (6¶8a table) found; `memfn` section floor: 14 (registry.md 6¶8b) found; test-registry green with it.
- tuning.md 2.43 para 3d: single anchor, widest-width clause and SPAN FORMS text both present.

## LOCAL CHECKS
Box idle (boxqueue/boxlock status free) before running. Merge commit pre-commit staged checks: 70 passed, 0 failed.
- `make strict`: PASS (whole tree clean with -Werror -Wshadow, kit target table passes).
- `make -s test-plan-lint`: PASS (2 checks, 0 failed).
- `scripts/check_claudemd_size.sh --all`: 370 files within limits.
- `make test-codegen`, `make test-registry`, `make test-rxtsource` (one `scripts/boxlock run --label covs2land-checks` chain, log $PCREC_TMPDIR/scratch/covs2land/checks.log): all three rc=0; grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' prints nothing.
No make test, mech or battery run locally.

## CLOUD RUNS DISPATCHED
All four from lane/covs2land at a88871a1924400c858c433ab6981618eec034cf7 (the report commit; the next commit only fills this section; merge commit c774d15c0 is its parent), owner main, not waited on. The four kinds are those covs2fix_report.md dispatched for the previous tip (test, axes, asan, mechrows over its 24 rows) plus nothing else it named. Proof, `git ls-remote origin 'refs/heads/cloud/main/*/covs2land*'`:

    a88871a1924400c858c433ab6981618eec034cf7	refs/heads/cloud/main/asan/covs2land-asan
    a88871a1924400c858c433ab6981618eec034cf7	refs/heads/cloud/main/axes/covs2land-axes
    a88871a1924400c858c433ab6981618eec034cf7	refs/heads/cloud/main/mechrows/covs2land-rows.rows.S1130_S1131_S1132_S1133_S1134_S1136_S1137_S1139_S1140_S1141_S1148_S3220_S3221_S3222_S3223_S3224_S3225_S3226_S3234_S3260_S3263_S3264_S3265_S3266
    a88871a1924400c858c433ab6981618eec034cf7	refs/heads/cloud/main/test/covs2land-test

OWED: none.
