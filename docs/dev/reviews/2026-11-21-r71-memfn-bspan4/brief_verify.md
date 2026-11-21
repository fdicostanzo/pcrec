VERIFIER (sonnet): memfn-bspan4 (r71). Read /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan4/COMMON.md FIRST and obey it
(scope, denylist, trees, kit). You are NOT a critic: you verify the ONE critic's CONFIRMED findings, independently, by
re-running or re-reading what each names. Findings: /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan4/ready.findings.md
(READY-1..READY-7). You may READ the critic's scripts and outputs under .../crit-memfn-bspan4/ready/ but re-derive the
verdict with your own call where you can (quote the exact call you ran). For each id give HOLDS / REFUTED / PARTLY / not
verified (why), with the evidence:
- READY-1: read the build tree's tests/memfn/simd_floor_check.py: does the NAMED leg check every named witness on every
  target in FLOORS (x86-64 included)? Does rev 4 (R/subject/block_span_rev4.md §10.1, §10.2, §11) say the x86-64 target
  renders no V mover? Is "two" vs "three" witnesses as quoted?
- READY-2: quote the five rev 4 sentences; read tests/axes/memfn_arm.py: is a MEMFN_CLASS corpus floor a count over every
  .rxt in the tree (so a U1-committed .rxt counts at U2)? Is the VM engine claim (`[0-9a-f]{17} --engine=vm` has no window
  walk) true (1-2 compiles)?
- READY-3: quote window.c's floor path (c_floor_test -> wf_test -> wf_test_to -> wf_loop_len reading w->head) and the
  rev 4 "T-head at width 32 renders none" sentence; check the reach-registry capacity claim (REACH_ROWS and the count of
  registered tables/rows: recount the 36 + 12 + 6 = 54 against the source; say how you counted).
- READY-4: is test-memfn-simdfloor in make test's TEST_SECTIONS? Does rev 4 put the C18 regex amendment in U4 and the
  level block in U3 (quote §14)? Re-run the critic's ready/legs.py with and without --amend on one witness and report.
- READY-5: quote simd_guarded_check.py's unread-row failure and its sample rule (EVERY=10 in run_simd_guarded.sh); does
  rev 4 list this reader anywhere (grep R/subject/block_span_rev4.md for simd_guarded)?
- READY-6: quote rev 4's pin-cell "present" definition; count `rxa_mf1_vs0(` and `__w32(` in the critic's ready/w/hx17/on.c
  (check its Pattern: header).
- READY-7: (a) re-run ready/u2b_diff.py (or your own diff) on `\w{20}` and report counts; quote rev 4's 42/46;
  (b) is S2931's anchor in memfn/data/cards/kit-grid.tsv; (c) quote §5's "inside the region"; (d) quote wf_find_prepare's
  signature at the build tree and whether gphases is in scope there.
Budget: 20 pcrec compiles, 40 gcc compiles. Write /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan4/verify.md (pre-created,
one section per id): APPEND/Edit section by section the moment each is done, never a whole-file Write. Your scratch dir:
/var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan4/verify/ (export TMPDIR there). End the file with a line `VERIFY COMPLETE`,
then run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan4 --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan4/verify/deliver.txt verify`
until it prints DONE. Final reply at most 100 words; a lost final reply is expected.
