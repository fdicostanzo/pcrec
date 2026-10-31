# vmland: landing report for lane/vmrec (VM record-first refactor, step (a))

Lane vmland (sonnet), 2026-10-31. Rulings file vmland_rulings.md: empty at the last read; the in-conversation manager ruling (no jump, queue 759, no push, no prune) applied.

## Done
- Merge: `git merge --no-ff lane/vmrec` (tip 0aed76752) alone, no conflicts: merge sha 3bc599c92.
- Follow-up commit cfb6c4a85 (named paths): D182 in decisions.md; guide entry coding.md 2.7; plan row [VMREC] (STATE:started, Active; plan_lint 0 violations); scripts/emit_sweep.py declared identity arm set (IDENT_* tables, `--list-ident-arms REFREV`, `--ident-arm NAME`); full_suite_ledger.md landing line.
- emit_sweep: the list reproduces the job's 69 rows (68 + witness) minus the dropped non-flag arm `-fstartpos-guard` (one-line comment). `nocaptures` and `axis-fno-splice-calls` are IDENT_EXEMPT rows with reason strings; a `--limit 20` run of each prints `DELIVER witness: EXEMPT for arm ... (reason); byte identity is checked on c-default,c-vm,emit-ir`, movers=0, rc=0 (ref = tree binary, so a plumbing proof, not an identity run). An exempt arm that runs the composition stream is reported as invalid and fails.
- `make strict` green on the merged tree.

## Deviations
- The two proof sweeps ran WITHOUT `boxlock run`: it yielded to queue jobs 760/762 and emit_sweep's own cap exempts `--limit` <= 50 runs. Small (20 patterns, -j4).
- The follow-up report and the lanes history index entry are NOT in cfb6c4a85 (the 759 job pins HEAD to that sha); this report is untracked and the index line is not added: the manager commits both after 759.
- The job script for the old identity gate (/var/tmp/pcrec-pcrec/scratch/vmrecm/744-vmrecm-ident.job) still carries its own axes()/arms(); switching it to `--list-ident-arms` is not done.

## OWED
- `make test-codegen`: queued job `759-vmland-codegen` (cap 1800, runs `make -j16` then `make test-codegen`; refuses unless main HEAD = cfb6c4a8567dac8cd84159bdb4f863bdca5b2bb0). Completion line it greps: `cg: DONE rc=0` in job.log.cg. Its script: /var/tmp/pcrec-pcrec/scratch/vmland/759-vmland-codegen.
- Push of main: NOT done (manager pushes after 759 green).
- Prune: NOT done. Manager runs `scripts/wtprune` (dry run, `--apply vmrec`) then `scripts/branchprune` (`--apply` lane/vmrec).

## STATE AT HANDOFF
main = cfb6c4a85 (merge 3bc599c92 under it), local only. Dirty/untracked: docs/dev/artifact_size_log.tsv (not mine), docs/dev/lanes/vmland_deliver.txt, this report. Job 759 pending behind 758-fsfix-axes. No process of mine running.
