# r6 report -- [MEMFN-ROWCON] R-6: `miss = MF_MISS_N` at the three N2 cells

Lane `r6` (sonnet), branch `lane/r6` from main 13b9f2ae. Zero movers by contract.

## What changed
- `memfn/docs/requests.md`: R-6 filed, in the format of R-4/R-5.
- `src/gen/emit_dfa.c`, three hook initializers, nothing else:
  - `ofs_site_define`: `.miss = MF_MISS_N` (ofsskip FUNC/FIND/RETURN, define).
  - `pf_ofs_call`: `.miss = MF_MISS_N` (same site, use).
  - `pcrec_emit_req_byte_check`: `.miss = s->handoff == MF_H_ASSIGN ? MF_MISS_N : NULL`
    (precheck STMT/ALL_PRESENT/ASSIGN, use). The conditional keeps the ON_MISS handoff
    flavour at exactly what N2 observed (it does not use `miss`), so it states three
    cells and not four.
- The cells matched `n2_results_5fc4b0e5.md` one-to-one, so there was no stop condition.
- `emit_vm.c:vm_run_compare` also builds hooks; it is not an N2 cell (runcmp rows do not decline) and is untouched.

## Validated now (light)
- `make strict`: clean. `scripts/m6read_check_sab_anchors.py`: 497 sabotages / 515 sites, all resolve. No sabotage anchor text quotes an edited line.
- N2 would-decline, SMOKE mode (`SMOKE=1 n2_census.sh`, 3 patterns x 2 arms, traced `-DMF_TRACE` build, no lock):
  - main 13b9f2ae: `would_decline=6`, exactly the three cells (ofsskip define 2, ofsskip use 2, precheck use 2).
  - lane/r6: `would_decline=0`.
  - The full N2 sweep (958k compiles) was not run: hours, and it takes the Mac suite lock path. Smoke is a control, not the census.
  - Outputs: `build/scratch/n2_smoke_old/`, `build/scratch/n2_smoke_new/` (gitignored).

## OWED (detached chain, started automatically when `.lift` appears)
Chain script `build/r6_chain.sh`, waiter `build/r6_wait.sh`; completion file `build/chain_done` (`R6-CHAIN-DONE`), then `build/SLOT_DONE`.
1. Identity gate: `python3 scripts/emit_sweep.py --ref 13b9f2ae` -> `build/gate.log`, judged by `memfn_r4c_gate.py --zero-dumps` -> `build/gate.judge` (required `R4C-GATE PASS (--zero-dumps)`), rc in `build/gate.rc`.
2. `make -k -j16 -Otarget test` -> `build/test.log`, wall + rc in `build/test.rc`. Verdict: `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/test.log`.
3. Solo mech `S566 S529 S470 S471 S472 S460` -> `build/mech_<id>.log`; each must read DETECTED. These are the rows anchored in the edited precheck/handoff neighbourhood. About 110 rows are anchored somewhere in `emit_dfa.c`; the other rows were not run (none quotes an edited line; anchors resolve).
4. `docs/dev/artifact_size_log.tsv` restored by the chain; never commit its regeneration.
