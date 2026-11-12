# memfn kit — wake-up brief

Rewritten 2026-11-10 06:20, CURRENT STATE updated 16:00, by the kit session (pcrec-memfn).

## Who you are
The kit manager (`/pcrec-memfn-manager`). Main is the pcrec manager session `pcrec-main`. Frank rules, mostly via main.
Kit worktree: worktrees/memfn on branch lane/memfn-k1108 (ledger/journal commits; tip 0e2d3d157 + journal).

## Read in order
1. This file. 2. memfn/docs/journal.md tail (11-09 onward). 3. requests.md / responses.md open items.
4. docs/design/memfn/span_runs_sheet.md rev 1.2 (on lane/memfn-r38s @ 7e7d89a6c), the R-38 design of record.
5. D190 (3.0a plan triple), D191 (span-arms build go), [REVIEW-GATE] (code critic round or written waiver before a major landing).

## CURRENT STATE (2026-11-10 16:00)
- Landed on main: U2+U3 (cf578177e), 3.0a (2d72849ed), K38-1 (7658295b3, kit_run_decide).
- K38-2a: lane/memfn-k382a @ 41ebc052b (worktrees/k382a). Build lane k382a delivered (report docs/dev/lanes/k382a_report.md):
  the in-run stop reads kit_run_decide, lever run-tie-left (+ --harness= arm), G2 presence family run_g2_pres.sh, C2 classifier,
  W-K4 layouts, S3007/S3009 RED. The D27 oracle (lane k382o, branch k382o db3f0fb8e) is MERGED in: GREEN over 50,178 records;
  S3008 (plant B) DETECTED. Seam: docs/dev/lanes/k382a_oracle_iface.md.
- Review 2026-11-10 r2 k382a ruled and fixed (committed on the branch).

- K38-2a LANDED on main d81ebd294 (11-11).
  then watch with `scripts/monread kit --wait`; done line; main merges.
- Main frozen until the full suite verdict (~08:00 Wed): a done line parks on its branch.
- FRANK 11-10: close completable items first; NO 3.0b or new feature/opt. Main GO (journal 18:15): ledger closes (scratch/memfn/ledgerclose), lane kclose (SEAM-2 + R-13 owed, jobs 560-569), group 4: KIT = PIN-MSG-DEPTH + XARCH-NEEDSOK (Frank GO 11-10) kclose2 DONE 19:05; gates 570-580 QUEUED behind 550-559 (on green: done lines; pin R-13a floor from job 580) (it will FIRST merge main >= dc1988069 for the K37 fix and re-base the gates; add a job for R-13a TRACE_VARIANT_RECORDS_FLOOR via emit_sweep --variant all --bases byte --trace), prune; responses index after [DOC-INDEX].
- R-39 (g2 shard selector, Frank GO 11-11, approved exception): r39 split CORRECT (561 green) but UNBALANCED (92/267/87/107 s; simd unit 221 s). R-39 DONE line posted 11-11 09:30 (lane/memfn-r39b @ 119e1b6f5); main merges (Frank 11-11: cloud make test first).
- K38-2 GO (Frank 11-11 "finish it now"): k382 DONE 20:40; review r1 k382 FIXED by k382fix (01:10 11-12); cloud run 1 RED on the stale base; k382m merged main (abi 101), green except c2b; lane k382c2b (ruling A) RUNNING; then queue 600-609 + re-run cloud; on green: done line, main merges (re-bump abi if needed, re-pin FILEPIN); gates 600-609 (box) + cloudrun test/axes/ubsan/asan (lines in k382_report.md); FILEPIN re-pin at landing; then K38-3. Main sequences the abi re-bump.
- CLOUD: make test/axes/ubsan/asan stages go via scripts/cloudrun --owner kit --kind K, not the box queue.
- FRANK SETS (11-11): S0 K38-2a/kclose/K38-2 -> S1 K38-3 + 3.0b (main accepted 11-11) beside S2 Part D (GO at K38-2 landing) -> S3 COVER-CAP (request from main when S3 opens); Part C/EARNED-SKIP/MATCH-KNOWN PARKED (Frank 11-11; Part C returns as a fact producer for match-known). OWED: kit-only candidate list with triggers to main at K38-2 critic round.
- Pending main: the master row over conditionals/predicates/intersection (Frank 11-10); main runs the survey and sends the
  design for kit comment. Doc-index ledger format agreed (doc_index_format.md §8.1): convert responses.md once main's kit profile exists.
- Kit ruling on record: K38-2a made the in-run stop a counted reader (done).

## Box rules
- Frank's evening hold 20:00-01:00; the kit's hold.sh (scratch/memfn/s2a/jobs/hold.sh) blocks starts 19:00-01:00
  unless the dated lift file /var/tmp/pcrec-pcrec/hold_lifted_YYYYMMDD exists (shared with main; 00:xx reads the previous day).
- Jobs only through scripts/boxqueue; prio <100 overrides row-length order (rename your own jobs only). Watch with
  `scripts/monread kit --wait`. Kill only with scripts/safekill. Never /tmp. Name each harness's parallelism cap in briefs.

## Quiet-pass todo
scripts/wtprune (dry run, then --apply) for landed lanes: k0, s2e, u30d, u2, sp1efix, s30a (after landing), r38s (after
K38-1 carries the sheet); then scripts/branchprune --kit.

## Lessons (recent)
- An identity arm for a target that writes no target text is refused as vacuous; check generic == plain directly.
- A busy lane misses mid-run rulings; verify them in the deliverable.
- A compile failure is not a catch (ANOMALY); skips must be counted, and a skip without a fact failure is a FAIL.
