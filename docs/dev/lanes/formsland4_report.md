# formsland4 — merge of the r38 fix lanes into lane/memfn-forms

## Summary

Merged lane/memfn-formsfixg and lane/memfn-formsfixh into lane/memfn-forms (base 5d2a98710), applied the three J9 doc
lines, added the three missing mech shard rows, validated. One doc conflict (history index), no code conflict.

## Merges

- formsfixg: clean fast merge (6334d8f93).
- formsfixh: one conflict, `docs/dev/history/claude_md/docs__dev__lanes.md` (each side appended its report line);
  kept both lines (764bf58ad). No code conflict.
- J9 doc lines (f5442b498), comment/doc text only: `memfn/tests/g2/g2_win_gen.c` lever_controls comment (rows are
  `tests/compound/run_shell_checks.sh` section (4)); `tests/compound/CLAUDE.md` (4) clause (the bullet is wrapped
  differently from the report's quote, so the new clause was written against the current wrapped lines);
  `tests/compound/run_shell_checks.sh` header (4) block. formsfixh had not changed any of these lines.
- FINDING fixed (bc4693c6d): formsfixh added sabotages S3310-S3312 but no rows in `tests/ci/cloud_mech_shards.tsv`;
  `cloud_mech_check.sh` was red (DROPPED S3310-S3312). Added the three rows after S3304 (shard 45, ESTIMATE, same shape as
  formsfixf's S3300-S3304 rows). The shard-table header's estimate line was not regenerated.

## Validation

All run locally at nice, -j4, bounded.
- make strict rc=0; test-codegen, test-registry, test-rxtsource, test-memfn-finder, test-memfn-link, test-resource,
  test-cli, test-compound, test-memfn-g2: all rc=0 (logs in scratch/memfn/formsland4/).
- tests/compound/run_lever_fence.sh: PASS (3 checks, 4 controls).
- memfn/tests/run_g2_win.sh: checks passed 27349, failed 0.
- cards.py selftest: 182 checks, 0 failed. cards.py dry (WIDTH_FLAG=none): cells 1374, built and gated 1374, failures 0.
- tests/ci/cloud_mech_check.sh on the table (after the fix; red before it) and its --selftest: PASS, 90 shards, 1333 ids.
- scripts/m6read_check_sab_anchors.py: 1333 sabotages, all anchors resolve.
- emit_sweep vs 5d2a98710: movers=0, asymmetric=0 on every stream; DONE rc=0.
- Not run (as briefed): full make test, queue jobs, timing, cloud.

## STATE AT HANDOFF

- STATE: delivered; tip is the commit carrying this report on lane/memfn-forms.
- Rulings: formsland4_rulings.md read, no entries beyond the template.
- OWED: none
