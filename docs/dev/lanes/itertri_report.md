# itertri — triage of the red `make test` runs of lane/iteropt (job 597) and lane/iteropt2 (job 596)

Fixes are on lane/itertri (from lane/iteropt2 55cb89c87). No `src/` change, no regression found.
Byte pins were re-measured at the check's own `-o` (resource: `-o o.c`; cpset census: `-o -`) with this
tree's compiler and diffed against a build of lane/i2build bed4bef84 (worktree itertri-base).

| section | check | class | evidence | fix |
|---|---|---|---|---|
| test-codegen | `[SABANCHOR]` S1321 `ANCHOR NOT FOUND` (script 1 of 17; the other 16 pass) | (a) stale anchor | the STEP's `pcrec_sb_printf` call now ends `",\n p, cursor_params(cx, t), runp, runt);` on the next line, so the multi-line anchor tail moved | S1321 SAB_BEFORE/SAB_AFTER cut to the single anchored line; `m6read_check_sab_anchors.py` reads "all anchors resolve" (904 rows) |
| test-resource | `a{5,25000} -fno-scan-edge -fno-start-pinned` rescue size 766307 | (a) pin moved legitimately | 597 read 766478, 596 reads 766980 (+673 over i2build); o.c diff = 13 hunks, all inside `rx__enter`..`rx_next_n` (enter hoists its setup, step/one take s/n/&lo, new `__one_call`/`__one_local`, cursor locals in `_next_n`); rescue note unchanged | pin 766980, comment block extended |
| test-cpset-structure | `[3]` manifest drift, 12 `EMITTED_BYTES` rows | (a) manifest moved legitimately | every row +703 (DFA) .. +826 (`(a(?1)?b)`); other stamps identical; diff = the same iterator functions plus `rx_iter_begin`'s initializer (one line, the iterator constructor) | 12 rows re-recorded (values are file size - 1, as the census strips the trailing newline); history comment added |

No (b) real regression and no (c) load: the reds are deterministic byte counts and an anchor, and 596 ran at
load1 1.95. Job 597's own reds (resource, cpset) are the same two pins at iteropt's intermediate size (766478);
its test-codegen was green because S1321's anchor only broke with iteropt2's `cursor_params`.

## Validation
OWED: `make test-cpset-structure test-resource test-codegen` solo on lane/itertri, launched detached under
`scripts/boxlock run --label itertri2` (waits for job 600); logs
`worktrees/itertri/build/triage/{test-cpset-structure,test-resource,test-codegen}.log`, trailer
`ALLDONE` in `worktrees/itertri/build/triage/run2.log` with an `rc=` line per section. DONE already: the SABANCHOR
checker standalone (all anchors resolve); the byte measurements above. The S1321 mech row itself (plant still
detected) is not re-run; `bash tests/mech/run_sabotage_matrix.sh S1321` is the command if wanted.
