# partd3 report

## Summary
Lane partd3 renumbered Part D's three D3 sabotage rows on lane/memfn-partd from S3120, S3121, S3122 to S3125, S3126, S3127 (in order, content unchanged), because lane/memfn-d27fix adds its own S3120-S3124 and lands on main first. No id 3120-3124 remains in tests/mech/sabotages on this branch (the dir now holds S3125, S3126, S3127 and the unrelated S312_findings_residue_ties_high.sh).

## Renumbering
- Row files git-mv'd: tests/mech/sabotages/S3125_run_part_record_skips_scanless.sh, S3126_run_part_record_on_quiet_path.sh, S3127_census_parser_skips_set_terms.sh (SAB_ID, header and SABOTAGE marker text changed inside).
- Other readers changed (word-bounded, found by git grep over the tree): memfn/tests/run_g2_pres.sh (plant cases, plant labels, PLANTS list), memfn/tests/CLAUDE.md, tests/ci/cloud_mech_shards.tsv (3 ids), docs/dev/lanes/partd2_report.md (ranges S3119-S3122 became "S3119, S3125-S3127").
- Left as written: memfn/docs/journal.md and docs/dev/history/ text. part_d.md names none of the ids.
- The queued gate job was copied from scratch/memfn/partd2/jobs/gate.sh to /var/tmp/pcrec-pcrec/scratch/memfn/partd3/jobs/gate.sh with the new ids, its OUT/S scratch moved to partd3.

## Checks
All run in the background with logs under /var/tmp/pcrec-pcrec/scratch/memfn/partd3/:
- make strict: clean (strict.log).
- python3 -I scripts/m6read_check_sab_anchors.py: 1289 sabotages, all anchors resolve (anchors.log).
- make test-memfn-arch: passed 17, failed 0 (arch.log).
- make test-memfn-rows: passed 100, failed 0 (rows.log).
- run_g2_pres.sh --plant S3125 / S3126 / S3127: RED / RED / RED, rc 0, each by its own detector (D3 EVERY-POS, D3 RECORDS, D3 UNSPELLED; plant.S312x.log).

## Owed runs
OWED: kit-partd3-gate (queued, 597-kit-partd3-gate, script scratch/memfn/partd3/jobs/gate.sh) and partd2's mechrows list with the new ids: S3106 S3107 S3108 S3109 S3110 S3111 S3112 S3113 S3114 S3115 S3119 S3125 S3126 S3127.
