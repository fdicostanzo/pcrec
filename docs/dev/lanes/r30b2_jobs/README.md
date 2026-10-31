# r30b2_jobs — the R-30 re-run on the merged tip, one stage per job

Lane r30bfix (2026-10-31). STAGED, NOT QUEUED: the kit manager queues these after agreeing the
slot with main. The plan is `docs/dev/lanes/r30btri_report.md` "Re-run plan" (rows 1-10, mech
split in two); the fixes they validate are `docs/dev/lanes/r30bfix_report.md`.

- Tree: `worktrees/r30b` (branch `lane/memfn-r30b`), abi 94 (provisional) over main 5c60e118c.
- Shared settings and helpers: `common.sh` (sourced by absolute path; boxqueue runs a copy of each
  job). Output: `worktrees/r30b/build/r30b2/<step>.log`.
- Job 1 records the tip it built in `build/r30b2/TIP`; every later job refuses to run on a
  different tip. Commit nothing to the branch while the chain runs. If the tip has to move,
  retry job 1 first (`boxqueue retry kit-r30b2-build`), then the rest.
- Each job's `--ready` is `scripts/boxqueue after KEY` on the jobs it needs. A KEY not in the
  queue reads "not ready", which queuewatch's PENDING-STUCK reports, so queue every job.
- Every `--dry-run` passed on the delivered tip (r30bfix_report.md "Staged jobs").

## Order

| # | file | KEY | after | stage | cap s | expected wall |
|---|---|---|---|---|---|---|
| 1 | `01-build.sh` | kit-r30b2-build | - | make -j16, make strict, mechval (77 ids); records the tip | 900 | ~2 min |
| 2 | `02-census.sh` | kit-r30b2-census | 1 | refbuild of main 5c60e118c + `r30b_evidence/census.py` | 1800 | ~5 min |
| 3 | `03-codegen.sh` | kit-r30b2-codegen | 1 | make test-codegen | 1200 | ~5 min |
| 4 | `04-memfn.sh` | kit-r30b2-memfn | 1 | the 15 memfn sections | 1800 | ~10 min |
| 5 | `05-compound.sh` | kit-r30b2-compound | 1 | make test-compound | 1800 | ~10 min |
| 6 | `06-regrx.sh` | kit-r30b2-regrx | 1 | make test-registry, make test-rxtsource | 900 | ~3 min |
| 7 | `07-axes.sh` | kit-r30b2-axes | 1 | `AXES=--harness=pres-window tests/axes/run_axes.sh` | 2400 | ~12 min |
| 8 | `08-test.sh` | kit-r30b2-test | 1, 3, 4, 5, 6 | full make test via `scripts/perfrun --label r30b2` | 3600 | ~25 min |
| 9 | `09-mech-a.sh` | kit-r30b2-mech-a | 8 | mech, 38 rows (the six new plants, S278, S693, S449, S678 first) | 3600 | ~45 min |
| 10 | `10-mech-b.sh` | kit-r30b2-mech-b | 9 | mech, the other 39 rows | 3600 | ~45 min |
| 11 | `11-reach.sh` | kit-r30b2-reach | 1 | `REACH_ONLY=1` matrix, MECH_SCRATCH kept in `build/r30b2/reach_scratch` | 1200 | ~5 min |

Walls are job 697's own timestamps (r30btri_report.md); compound's is an inference. Total
about 2.8 h of box time. Priority numbers below are placeholders in the order above, shortest
first. Renumber them freely: the KEY, which `after` reads, does not change with the number.

## Queue commands (run from the main tree)

    Q=/home/pcrec/projects/pcrec/scripts/boxqueue
    J=/home/pcrec/projects/pcrec/worktrees/r30b/docs/dev/lanes/r30b2_jobs
    $Q add --name 770-kit-r30b2-build    $J/01-build.sh
    $Q add --name 771-kit-r30b2-regrx    $J/06-regrx.sh
    $Q add --name 772-kit-r30b2-reach    $J/11-reach.sh
    $Q add --name 773-kit-r30b2-census   $J/02-census.sh
    $Q add --name 774-kit-r30b2-codegen  $J/03-codegen.sh
    $Q add --name 775-kit-r30b2-memfn    $J/04-memfn.sh
    $Q add --name 776-kit-r30b2-compound $J/05-compound.sh
    $Q add --name 777-kit-r30b2-axes     $J/07-axes.sh
    $Q add --name 778-kit-r30b2-test     $J/08-test.sh
    $Q add --name 779-kit-r30b2-mech-a   $J/09-mech-a.sh
    $Q add --name 780-kit-r30b2-mech-b   $J/10-mech-b.sh
    $Q --dry-run

## Reading the verdicts

Each job's `job.log` shows `== r30b2 step NAME rc=N` lines and each step's verdict lines. The
full logs are in `build/r30b2/`. For job 8, read `build/r30b2/test.make.log.perfrun` first, then
the `test-red:` lines. Job 11's per-row `reach.log` files stay under
`build/r30b2/reach_scratch/`, so an S1760/S1761 miss can be explained if it happens again.
