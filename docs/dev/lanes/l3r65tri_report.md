# l3r65tri report

STATE: stopped (shard 6 fixed and verified locally; shard 13 STOPPED on a scope question)

## Summary
Cloud run 44855950624 (cloud/main/test/l3r65-test @ 0194787de) failed shards 6 and 13.
Shard 6 was a stale l3tri re-pin and is restored to BASE (one row). Shard 13 is NOT a
stale pin: two patterns moved to an encoding asymmetry that the pick rule created, and
clearing it needs a change to the DD12a(i) checker's logic (test code), not a pin edit;
that checker has already been re-aimed twice for this cause. STOPPED per the brief.
BASE = 694d91dc4 (main's merge-base). Premise test: tip bffc5d2ed. Rulings file empty, no R-n applied.

## Shard 6 cpset manifest
One moved stamp: `(?<=foo)bar EMITTED_BYTES` in tests/codegen/manifests/m5_stage1_stamps.tsv.
BASE 38505; l3tri e51c5aaaf re-pinned to 39608 for the pre-fix run; at the tip the compiler
emits 38505 again (cloud diff: recorded 39608, run 38505). Cause: review r65's pick rule
returned this pattern to BASE's run. Disposition: restored to BASE 38505 (commit on
lane/l3r65tri). Reproduced and verified locally: run_cpset_structure.sh 29 pass / 0 fail;
the other two scripts under make test-cpset-structure (run_wclass_census.sh 25/0,
run_clspack.sh 59/0) also pass. git log --since=14.days on the manifest: l3tri was the only
L3 re-pin (this one reverts it), so no repeat-cause trigger.

## Shard 13 DD12a
Reproduced locally (bash tests/codegen/run_encoding_checks.sh): the same three FAIL lines.
The 4 other FINDING patterns (`ab|abc|ad`, `(?:ab\b|ad\b)`, `\b`, `\B`) are the K50 manifest's
existing undeclared members, not new. The NEW divergences are exactly two patterns
(emitted by `pcrec --features all -e byte|utf8 -p rx`, BASE = a build of 694d91dc4, l3tri =
a build of 04b889b27):

| pattern | BASE byte / utf8 | l3tri tip byte / utf8 | this tip byte / utf8 |
|---|---|---|---|
| `(?<=a)(b)\1x` | run none, REQ_BYTE 120 / same | run 6162@1 K-1, REQ_BYTE 98 / same run | run 6162@1 K-1, REQ_BYTE 98 / run none, REQ_BYTE 120 |
| `(?i)(?<=ab)(b)\1x` | all none / all none | run 414242@2/dfdfdf K-2 / same | run 414242@2/dfdfdf K-2 / all none (REQ_WHY none) |

Which change moved it: L3 itself added the run to both sides (l3tri's pins were right for
that build); review r65's pick rule then dropped it on the utf8 side only (byte keeps it).
So the value does NOT return to BASE (BASE has no run on either side), and the l3r65 comment
"moved back to BASE's run-free form on the default route" is true for utf8 only. The checker
finds: (1) byte pre-check scans 98,120 but REQ_BYTE "98" (the 120 is the presence gate beside
the run, which l3tri's presence_stmts normalization only handles when BOTH sides state a run);
(2) REQ_WHY byte "emitted" vs utf8 "none"; (3) the two patterns are strict-bucket divergences
not on the K50 UNDECLARED list (this run diverged on 6 of the 4 listed reached).
Why STOPPED: finding (1)/(2) come from the checker's selection-coherence logic, independent of
the K50 list, so adding the two rows to tests/codegen/manifests/k50_gate_refinement.txt would
not clear them; clearing needs presence_stmts to normalize when either side states a run and
the byte-only-run / utf8-none asymmetry to be ruled a declared (REQ_RUN stamp differs) region.
That is a code edit to test logic, outside "pins, manifests and reasons only", and
tests/codegen/run_encoding_checks.sh has already been re-aimed for this cause twice
(65cbc4c97 l3tri, c29d6b716 l3r65). The K50 manifest has no L3 re-pin yet. SCOPE QUESTION for
main: (a) is the byte-keyed-run / utf8-none asymmetry the intended outcome of the pick rule
(then rule it declared and have a lane generalize the checker + add both rows), or (b) a
regression of the pick rule (utf8 should keep L3's run)? I did not judge (b): the answers
are both PCRE2-equal; this is a selection-quality question.

## Validation dispatched
None. The shard-13 section is still red at the tip, so a cloud run would only reproduce it;
shard 6 is verified locally (above). No cloud run was dispatched and no `--name l3r65tri-test`
ref exists. Local box use ended at 23:28 (nice make -j4, only the failing sections).

## STATE AT HANDOFF
- Branch lane/l3r65tri: one commit on top of bffc5d2ed (the shard-6 restore) plus this report.
- Last R-n applied: none (rulings file empty).
- Owed: shard 13 ruling (a)/(b) above, then a fix lane; then a cloud run of the result.
- Scratch: /var/tmp/pcrec-pcrec/scratch/l3r65tri/ (job logs s6.log, s13.log, enc.log, cmp/).
- Extra worktrees I made for BASE and l3tri-tip builds, still present (wtprune keeps them:
  not merged / modified recently): worktrees/l3r65tri-base, worktrees/l3r65tri-l3tri.
  Remove with scripts/wtprune --apply --force l3r65tri-base l3r65tri-l3tri.
