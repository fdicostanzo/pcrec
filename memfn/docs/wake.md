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
- IN FLIGHT: code critic round crit-k382a (opus coordinator, draft to /var/tmp/pcrec-pcrec/scratch/crit-k382a/). On hand-back:
  commit it as docs/dev/reviews/2026-11-10-r2-k382a.md on lane/memfn-k382a, rule the dispositions, run a fix lane if needed.
- THEN: gates 540-549 (kit-k382a-*, /var/tmp/pcrec-pcrec/scratch/memfn/k382a/jobs/, all dry-runs pass) - re-key if a fix lane
  moves the tip after a cancel (key chains collapse); queue; watch with `scripts/monread kit --wait`; done line; main merges.
- Main's full suite holds the box Wed 11-11 01:00 to ~14:00 on a frozen main: no kit jobs or merges to main in that window.
- After K38-2a: 3.0b (main's go given: "3.0b stays after it"), then K38-2 (the seam event, L), K38-3.
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
