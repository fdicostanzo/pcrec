# memfn kit — wake-up brief

Rewritten 2026-11-10 06:20 by the kit session (pcrec-memfn). Committed docs win on any conflict.

## Who you are
The kit manager (`/pcrec-memfn-manager`). Main is the pcrec manager session `pcrec-main`. Frank rules, mostly via main.
Kit worktree: worktrees/memfn on branch lane/memfn-k1108 (ledger/journal commits; tip 0e2d3d157 + journal).

## Read in order
1. This file. 2. memfn/docs/journal.md tail (11-09 onward). 3. requests.md / responses.md open items.
4. docs/design/memfn/span_runs_sheet.md rev 1.2 (on lane/memfn-r38s @ 7e7d89a6c), the R-38 design of record.
5. D190 (3.0a plan triple), D191 (span-arms build go), [REVIEW-GATE] (code critic round or written waiver before a major landing).

## CURRENT STATE
- U2+U3 LANDED on main (cf578177e). R-37 done.
- R-35 3.0a: all gates GREEN (500, 501/502/093 identity, 094 reach, 095 make test, 096 plants, 097-099 mech) on
  lane/memfn-s30a @ f5c2f416a vs cf578177e. done posted (0e2d3d157). Main ruled MERGE; landing lane kitland3 is merging.
  WAITING (waiting_on.kit): kitland3's landing commit on main.
- NEXT: K38-1 (R-38 unit 1, size M) on a fresh branch cut from main AFTER the 3.0a landing, carrying the sheet
  (cherry-pick/merge lane/memfn-r38s 7e7d89a6c). Then K38-2a, K38-2, K38-3 (one abi event for parts A+B).
  A major code landing needs a code critic round ([REVIEW-GATE]).
- 3.0b waits for main's go, which comes after the 3.0a landing.

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
