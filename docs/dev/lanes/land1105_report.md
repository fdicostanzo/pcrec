# land1105 report: span_pick unit 1d landing

## Merges
- lane/memfn-sp1d (0044a0ee7) -> 39e7b20c5, clean, no conflicts.
- lane/memfn-k1102 (352ed1aef) -> 2d7f4bd8c. One conflict, memfn/docs/journal.md (both sides appended a
  `## 2026-11-04 (night)` section); resolved keeping BOTH sections whole. `make strict` green before commit.

## R21 restatement (docs/design/stream/roadmap.md §5)
Recipe cell replaced with the kit's proposal; baseline cell notes "reads 1 at daf6f002b and 0 at 1d's merge".
Ratchet script output at HEAD (`/var/tmp/pcrec-pcrec/scratch/memfn/sp1d/ratchet.sh /home/pcrec/projects/pcrec`):

    R20=3 R21=1 R22=0 R23=0 R24=0 R25=1 R26=0 R27=0 total=5
    R24-restated=0 (kit_run_member 1, rank-loop 0, p3-scan 0, run_member-own-mass 0)
    R21-restated=0 (a_model_choose 0, a_mass_choose 0, cands 1)

(The first line is the old written recipes; with R21 restated the stage-1 kit-row total is 4.)

## Plan rows filed (STATE:not-started, Backlog, before [KIT-PAYLOAD-VERSION])
- [SP1D-M-INPUTS] (F4, trigger with row 1)
- [SP1D-ARGMIN] (F9 U-1/U-2)
- [SP1D-SETLEADS] (F9 P4, next T-PRES change)
- [SP1D-KITSPLIT-SEAMS] (F10 + r2 F13, F12; kit split)
- [SP1D-AMODEL-CANDS] (Design deviation 1; a ruled change)
All cite docs/dev/reviews/2026-11-05-r1-memfn-sp1d.md, no plan line numbers.

## Ledger
1d merge added as minor (major 0, minor 1); trigger-state line updated. None for k1102 or own docs commits.

## Checks
make strict green; scripts/plan_lint.sh 0 violations; make test-registry rc=0; pre-push-light all passed.

## STATE AT HANDOFF
Pushed main 81a9c750f..3e450359b (plus this report's commit). No worktrees or branches pruned. Left alone:
artifact_size_log.tsv, *_deliver.txt, land1101.done. No rulings file existed.
