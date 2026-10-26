# scansetfix report — triage of the RED job 500-scanset-test ([SCANEDGE-SET])

Lane scansetfix (sonnet), 2026-10-26, branch `lane/scanset` from a81c5cbc6. Job 20261026T125546 verdict RED
(`section-errors=4`; strict, axes, mech S213 green). No wrong answer in any failure: STOP RULE not triggered.
Rulings file: none appended (last entry applied: none).

| # | failure | cause | class | fix | evidence |
|---|---|---|---|---|---|
| 1 | test-codegen: `skip states: forward skip loop`, `OS-0b ... no skip table`, `[M6.2-WORDB rule 2]` | the three fixtures (`.*=.*`, `.*\b.*`) are about `pick_skip_states`; `.` is classes {0,2}, so the new set rule makes the stay states scan edges (`rx_forward_scan1`) and the stay tables the fixtures grep for are gone. Equal-speed replacement, not a lost optimization | stale fixture | fixtures pass `-fno-scan-edge` (the edge form has its own census, sections 7/8) | `run_codegen_tests.sh` 331 pass / 0 fail; `.*\b.*` edge vs `-fno-scan-edge` answers equal on 11 subjects |
| 2 | test-rxtsource: census/RUNSH/C3 pins MOVED, W23-S7 control | the new `tests/classes/scan_set.rxt`: +1 file, +11 blocks, +74 case lines | stale population pin | re-pinned 297/6174/74395 -> 298/6185/74469 (RUNSH 273 -> 274), C3 PASS +50, SKIP +24 (all pcre2-only), verifiable +50; +74 reconciles to the file's 74 cases | `run_rxtsource_tests.sh` 298 pass / 0 fail |
| 3 | test-startset `[vm-movers]` (8 unlisted) | the 8 forced-VM movers of scan_set.rxt were never in `manifest_s2_vm_forced.tsv` (corpus-adding lane runs test-startset: this one had not) | stale manifest | +8 rows, computed from the build's own `RX_VM_START_SCAN != none` under `--engine=vm`; no existing row moved | `run_vmhat_checks.sh` 22/0 |
| 4 | test-startset `[dfa-deny]` (3 blocks: clspack_atoms:53, composition_d27:9936/10135) | not a miscompile: with a start-set hat the conditional re-seed makes the head a seed target and scanedge.c precondition (8) refuses it, so the hat arm lacks a (now set-shaped) edge the deny arm has. `DFA_SCAN_EDGE` stamp names the kind (`bitmap` both arms), so `classify()` saw no cross-row class | check blind spot (pre-existing interplay, newly reachable) | `classify()` also counts edge tables (`rx_*_scanN[256]`), so the scan-edge class is named and re-compared with `-fno-scan-edge` on both arms (the existing class mechanism, no special case) | `run_dfahat_checks.sh` 35/0 |
| 5 | test-endmark G3 (9 artifacts: `\s+$` family, rev_end.rxt, composition) | G3 prices STATES; a set edge adds a 256-B table + loop per head, so the tagged (default) arm carries more of them than the model counts (e.g. 25454 vs 22582+905) | stale model (edge tables outside the state model) | G3's two size reads use `-fno-scan-edge` on both arms; G1/G2/G4 untouched | `run_b3_checks.sh` 46/0, g3 population 42 (floor 42) |

## STATE AT HANDOFF
Commits on `lane/scanset` (see git log). Targeted re-runs of the five failing sections green. OWED: full re-validation job
(`scanset_job` re-queued as the lane's last act; key/log recorded below).
