# vmrecm report: merge main into lane/vmrec, re-queue the validation (2026-10-31, sonnet)

## Merge

`git merge main` (main d30f5bb78) into lane/vmrec, merge commit c63cb05e9. Two conflicts, no record-writer
decision needed (the stop rule did not fire):

- `tests/mech/sabotages/S146_call_return_cuts.sh`: main fixed the plant (the added `%s` needs a matching
  argument; the matrix's S146 ANOMALY). vmrec had moved the target to `src/gen/vm_stmt.c`. Resolution: main's
  comment and plant text, vmrec's SAB_FILE and re-aim note, and the plant's printf arguments spelled with the
  renderer's names (`sb->p`, `sb->up`, as vm_r_return writes them). `scripts/m6read_check_sab_anchors.py`: 1086
  sabotages, 1120 anchor sites, all resolve (0 stale; the merge itself had left S146 stale until the names were
  re-aimed).
- `docs/dev/history/claude_md/docs__dev__lanes.md`: both lanes appended an index line at the end; kept both.

Everything else auto-merged (emit_sweep.py's arm pins, S1047/S1048, fsfix2's files taken from main by git).
abi: no change from main's number (vmrec is byte-identical). `make -j16` and `make strict`: clean on the merged tree.

## The two red arms of job 740 (and five more)

Job 740 actually had SEVEN failed arms of 69, all with movers=0 and asymmetric=0 (byte identity held everywhere).
None was a change in emitted text; all were witness or floor pins of the sweep itself:

| arm | cause | resolution |
|---|---|---|
| utf8 | composition artifacts floor 88 < 98: the pre-merge emit_sweep.py still carried the pre-F7 floor | main's job-695 re-pin (utf8 37/86) is in the merged script; measured 38/88 clears it |
| axis-fcomments, axis-fmemfn-simd | same (floor 106 vs measured 88) | re-pinned 38/88 in the merged script |
| nocaptures | no COMPOSITION_EXTRA_PINS entry (floors not applied) and the DELIVER witness cannot be met: with `--no-captures` the cross-group SET-pair shape does not appear. Not a tree property; ref and working both lack it | job 744 runs this arm on c-default,c-vm,emit-ir (no composition stream); the composition stream and its witness stay on every other arm. The witness itself is untouched |
| axis-fno-splice-calls | same: the flag removes the DELIVER composition artifacts | same: no composition stream |
| axis-fprefilter | requires the VM engine: c-default refuses 4463 of 6263 patterns, reach 1800 < the plain arm's floor 4920; and no composition artifacts | job 744 runs it on c-vm,emit-ir |
| axis-fstartpos-guard | NOT A FLAG: the job's axes() scraped `-fstartpos-guard` out of description text; the compiler says `unknown option`, so every pattern was refused on both sides (a vacuous arm with 0 reach) | axes() now keeps only flags the compiler accepts (68 arms, was 69) |

I did not re-run the arms ad hoc: emit_sweep has no per-arm selector (arms are the job's loop; `--arms` takes only
`start`), and the box was held by another queue job, so the evidence is job 740's logs (arm tables, floors, witness
lines) read against the merged script's pins. Job 744 is the confirmation.

## Queued (all dry-run clean at `scripts/boxqueue add`)

The 19:00-00:00 gate is dropped from every job (none is a timing run). Reference for 744 is main d30f5bb78 built
in `scratch/vmrecm/ref/` (the merged tree differs from main only by vmrec's byte-identical refactor).

| key | what | cap |
|---|---|---|
| 744-vmrecm-ident | emit_sweep, 68 arms, `$ref` = main d30f5bb78 | 7200 (LONG-JOB: ~80 min measured in 740) |
| 745-vmrecm-test | build, strict, recursion identity gate, perfrun make test (81 sections); after vmrecm-ident | 3600 |
| 746-vmrecm-mech | S1840-S1849 (10 rows); after vmrecm-test | 3600 |
| 747-vmrecm-mechre | the 29 re-aimed rows; after vmrecm-mech | 18000 (LONG-JOB: per-row time unmeasured) |

The job scripts are in `/var/tmp/pcrec-pcrec/scratch/vmrecm/74[4-7]-*.job`.

## STATE AT HANDOFF

Merge committed, S146 re-aimed, strict and the anchor check clean. Validation OWED: jobs 744-747 queued, not run.
Verdict reads: 744 `job.log.ident` ("ident: arms failed 0", every arm movers=0), 745 `job.log.make` via
`scripts/verdict`, 746/747 `== mech run COMPLETE`. If 744 shows any arm red, read the arm's own log under
`scratch/vmrecm/e1.*.log` first (a floor or witness line vs a mover). Last rulings entry applied: none
(vmrecm_rulings.md had no entries).
