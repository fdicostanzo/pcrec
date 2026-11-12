# kclose3 report

## Summary
R-13a trace floor re-pinned in scripts/emit_sweep.py to job 580's measured counts; job 580's compare regex fixed and the declared list-axes mover argument added. The re-run is the kit manager's to queue.

## VARIANTS FAILED cause
Only the declared --list-axes memfn-simd row 2 wording change (R-13b), checked in job 580's sweep.log: every one of the 5 variants has exactly one dumps mover (population=7, movers=1), the `--list-axes:` memfn-simd@2 hunk; every other stream reads movers=0 asymmetric=0, all 5 trace verdicts CLEAN, trace-vs-default stdout diffs 0. Nothing else moved. The job now passes `--dumps-declared-rows=--list-axes:memfn-simd@2` to emit_sweep, after the same exact OLD/NEW text check ident.sh does against declared_movers.txt (REF binary vs build/pcrec).

## Floor re-pin
Verified each against job.log's sweep.log (`records per arm`) and pins.py. The floor header says measured, no margin, so exact values pasted (c-default/c-vm): plain 716435/359366, lowsize 908058/385834, lowdfa 717799/359366, lowthr 799133/385580, lowboth 878139/385834. One comment names job 580, 2026-11-12, branch tip against dc1988069.

## Job fix
The compare regex is now `^TRACE_VARIANT_RECORDS_FLOOR = (\{.*?\})\n` with re.S | re.M: line-start anchored, so the fh.write writer string (starts with `fh.write("}\n...`, a quote before the name) cannot match. A pure quote-excluding character class cannot work (the dict itself is quoted), so the anchor does the exclusion. Tested: it evals to the new floor. `bash <job> --dry-run` rc=0.

## Checks
make strict clean; `python3 -I -m py_compile scripts/emit_sweep.py` ok; scripts/tests/emit_sweep.py.test: checks failed: 0 (rc=0).

## Charter-vs-committed checklist
1 VARIANTS cause shown, declared mover wired: done (job script in scratch/kclose2/jobs, not committed). 2 re-pin: committed. 3 regex: done. 4 checks: done.

## STATE AT HANDOFF
Committed on lane/memfn-kclose: the floor re-pin and this report. Job script edits (declared-mover argument and text check, regex fix) are in /var/tmp/pcrec-pcrec/scratch/memfn/kclose2/jobs/580-kit-kclose2-r13a. Nothing owed from this lane; the 580 re-run is the kit manager's. Untracked kclose2.done is kclose2's, not touched.
OWED: none (the 580 re-run is the kit manager's to queue; expect all ten cells ok)
