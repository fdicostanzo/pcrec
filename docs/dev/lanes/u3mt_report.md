# u3mt report: three red sections of `make test` on the joint U2+U3 landing

## Summary
Job main-u3lint-maketest (lane/u3d27 7fa8469e9) went red in test-resource, test-cpset-structure
and test-memfn-arch. Two were one cause (+34 bytes on every artifact), one a code-shape hit. No
regression found; no other FAIL line inside a passed section (the only `FAIL` hits in the full log
are `(*FAIL)` pattern text and the three sections above).

## Failures
1. test-resource: `'a{5,25000}' -fno-scan-edge -fno-start-pinned` rescued at 766218, pinned 766184 (+34).
2. test-cpset-structure CHECK 3: manifest drift. Moved stamps: EMITTED_BYTES on all 12 sample rows,
   each +34 exactly (a 26096->26130, abc 26419->26453, a(b|c)+d 40669->40703, (a)(b)(c) 37650->37684,
   [a-z]+@[a-z]+ 43368->43402, ^foo$ 26440->26474, \bword\b 27842->27876, (?i)HeLLo 29962->29996,
   cat|dog|cow|calf|camel 35984->36018, (\w+)\s+\1 36943->36977, (?<=foo)bar 38342->38376,
   (a(?1)?b) 43357->43391). No other stamp moved.
3. test-memfn-arch class 8 (reads-kit-output): `pcrec_memfn_stamps_render` holds an `mf_sink` and
   its `strlen(PCREC_HELD_HEADER_MARK)` counted as a string search.

## Fixes
- Cause of the +34 (items 1, 2), explained exactly: built the abi 97 merge-base (550e23364) and this
  tree; on `a` and `a(b|c)+d` the whole diff is the abi number (97->98, same width), the header
  name, and one new line `#define RX_TARGETS "none:generic"` = 7+1+10+1+14+1 = 34 bytes. Expected
  (U3 scaffolding, abi 98); not a regression. Re-pinned 766184 -> 766218
  (tests/resource/run_resource_tests.sh) and re-recorded the manifest (+34 on the 12 EMITTED_BYTES
  rows; tests/codegen/manifests/m5_stage1_stamps.tsv), both with dated comments.
- Item 3: reworded, no allowlist row: the held-mark byte count moved into a new static helper
  `held_marks_bytes` in src/gen/memfn_stamps.c, so the function holding the sink reads no text.
  Emitted text unchanged.

## Checks
test-resource 42/0, test-cpset-structure 29/0, test-memfn-arch 17/0 (each alone, nice);
`make strict` clean. Full `make test` re-queued (below).

## STATE AT HANDOFF
OWED: main-u3mt-maketest (prio 480, job /var/tmp/pcrec-pcrec/scratch/u3mt/jobs/maketest, TREE
worktrees/u3mech, log /var/tmp/pcrec-pcrec/scratch/u3mt/runs/maketest.log). Verdict: grep -E
'\*\*\* \[(Makefile:[0-9]+: )?test-' on the log. Tree not edited after queueing. No rulings file.
