# rpland report (STOPPED, sonnet): merge main into lane/rpfix is not mechanical

## STATE AT HANDOFF
`git merge main` (main a07f76d6c) into lane/rpfix (5dd83294d) was run alone, produced 12 conflicted files, and
was ABORTED (`git merge --abort`); the branch is unchanged at 5dd83294d apart from this report. Nothing pushed.
Steps 2-4 (abi reconciliation, validation, push) NOT done. Stop rule applied: the conflicts are semantic, not stale pins.

Conflicted files: docs/dev/history/abi_changelog.md, docs/dev/history/claude_md/docs__dev__lanes.md,
docs/dev/plan.md, docs/spec/facts_listing.md, docs/spec/match_api.md, docs/spec/tuning.md,
src/gen/emit_dfa.c, tests/codegen/run_codegen_tests.sh, tests/codegen/run_recursion_identity.sh,
tests/mech/sabotages/S463_handoff_k_minus_one.sh, S693_abi_not_bumped.sh, tests/rxtsource/run_rxtsource_tests.sh.

## CHANGES
None to the tree. Why the merge is not mechanical:
- main's K38-2 (abi 104) RETIRED `req_run` / `req_run_maxoff` and the cut run window: callers read
  `pcrec_fact_req_whole_run(cx)->whole_len`, K is the whole run's position-0 offset, the search returns a
  least CANDIDATE, and the handoff position is emitted via `pcrec_emit_start_zero` with a `round` StrBuf.
  rpfix (REQ-PAST-LAST) is written against `pcrec_fact_req_run(cx)->len`, moved the `round` buffer into the
  bounded branch, adds the `unbounded` branch/re-ask and `handoff-attempts-unbounded`, and rewrote
  the same spec sentences (match_api.md REQ_HANDOFF paragraph, facts_listing 4.1.2 p8/p8a/p8b, tuning 2.41 p8b).
  emit_dfa.c has three overlapping hunks (ABI define, the k/whole/run + round block, the [K82] vs
  [REQ-PAST-LAST] comment); S463's SAB_BEFORE/AFTER anchors conflict on the same lines.
- The unbounded re-ask must be re-expressed in K38-2's whole-run / candidate vocabulary, and the spec
  paragraphs and the abi 105 changelog rewritten over main's 104 entry. That needs design judgment (and
  likely a kit-seam check, the kit's MF_SITE_ABI moved in K38-2), not a union merge.
- Mechanical parts once the code is resolved: ABI 105 readers (emit_dfa.c define, ABI_EXPECT in
  run_codegen_tests.sh, match_api.md x4 sites, abi_changelog.md, S693, recidentity pins), rxtsource census
  (main 7034/98216/22982/25395 plus rpfix's +2 blocks/+36 lines; recount with the check), plan.md
  (main's REQ-PAST-LAST row vs rpfix's deletion: keep rpfix's), lanes index union.

Remaining for landing: a fresh opus lane to port REQ-PAST-LAST onto K38-2 (resolve the 12 files), then
`make strict`, the six named sections, and a full make test or cloud test on the merged tip.
