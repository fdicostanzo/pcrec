# pinmsg report ([PIN-MSG-DEPTH])

## Summary
S1760 and S1761 read UNREACHED at a deep scratch path because their REACH probe's expected phrase sits after a fixture path in `pcrec_error.msg`, cut at 256 bytes. Fixed test-side only; both now read REACHED at any depth and DETECTED in full. STATE:done, row moved to plan_completed.md.

## Fix
`tests/mech/sabotages/S1760_pin_compare_skipped.sh` and `S1761_pin_last_link_only.sh`: SAB_REACH makes `S=$(mktemp -d "${PCREC_TMPDIR:-/var/tmp/pcrec-$(id -un)}/r.XXXXXX")`, copies `$TREE/tests/code/frag` to `$S/f`, uses `$S` for every path (include line, output, entry), preserves the probe's exit code and removes `$S`. The message path is now about 40 bytes regardless of scratch depth. No src/ or message change; the sha256 pins are unaffected (byte copy).

## Validation
- Before (main 9d796f4ec, deep TMPDIR 94-char leaf): REACH_ONLY, both rows reach:MISSING, rc=1 (reproduced).
- (a) after, same deep TMPDIR: `mech-reach-only: DONE rc=0 rows=2 reached=2 unreached=0`.
- (b) after, default scratch: reached=2 unreached=0, rc=0.
- (c) full rows S1760 S1761: both DETECTED; `mech run COMPLETE: 2 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0)`. Log: $PCREC_TMPDIR/scratch/pinmsg/c.log. Note: run (c) was launched without TMPDIR set, so mech used /tmp for its work tree (cleaned by mech); a lane slip, not a defect of the fix.
- `make -s strict` clean; `make -s test-plan-lint` PASS.
All runs under `scripts/boxlock run --label pinmsg`.

## STATE AT HANDOFF
OWED: none
Complete. Rulings file empty (no entries applied). Branch lane/pinmsg committed.
