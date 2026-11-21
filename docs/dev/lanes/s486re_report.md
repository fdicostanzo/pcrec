# s486re report: re-aim S486, reach sweep after rule (1)

## STATE AT HANDOFF

- Branch lane/s486re (fresh from main 75d365a0b). Rulings file read at start: empty, no entry applied.
- Done and committed: S486's reach probe re-aimed (tests/mech/sabotages/S486_dfahat_t_widened.sh).
- OWED (verdicts to be read by a fresh agent, not waited on):
  - Box job `650-s486re-reach` (boxqueue; `docs/dev/lanes/s486re_reach_job`): `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` over every row (about 1300 files). Holds itself out of 20:00-01:00 via `--ready` (exit 75). Done line: `mech-reach-only: DONE rc=0`; any UNREACHED row is listed under "NOT declared UNREACHED" in its log. Stop rule (more than 5 other UNREACHED rows = scope question to the manager) is therefore NOT yet evaluated.
  - Cloud run `scripts/cloudrun --owner main --kind mechrows --rows S486 --name s486re-rows`: proves the plant is DETECTED with the new witness (the local plant build was not run here).
- Premise test: done. On the worktree build, the old witness compiles to `RX_DFA_PREFILTER "handoff"`.

## CAUSE

Rule (1) alt_union (13f46ea50, abi 107) moved `\b((?:A3T[A-Z0-9]|AKIA|AGPA)[A-Z0-9]{16})\b` from the DFA hat (`first-memchr-bounded`) to the re-entered handoff row, which ranks above the two hat rows. The old S486 probe compiled with default options and grepped for `first-memchr-bounded`, so it read UNREACHED. Evidence: /var/tmp/pcrec-pcrec/scratch/audnight/ (s486_106.c, s486_107.c).

Before/after stamps of the AWS-key pattern (route change, speed UNMEASURED; for the manager, not fixed here):

| stamp | abi 106 | abi 107 |
|---|---|---|
| RX_DFA_PREFILTER | first-memchr-bounded | handoff |
| RX_REQ_WHY | dominated | emitted |
| RX_REQ_HANDOFF | none | 0 |
| RX_REQ_RUN | `[33474b][495054]...` (starts after the A) | `41[33474b][495054]...` (the A is now part of the run) |
| RX_MEMFN_LIBC | memchr | memchr,memcmp |

No answer changed.

## RE-AIM

The site is still reachable: with `-fno-req-handoff` the same pattern compiles to `first-memchr-bounded` on today's build (checked). That is exactly the arm tests/startset/dfahat_checks.py already uses for every witness (`NO_HANDOFF`, its REQ-HANDOFF-L1 note), so the detector (`dfahatstruct`) never saw the move: its aws witness and `[dfa-table]` pass on today's build (`DFAHAT_PART=struct`: 32 passed, 0 failed).

Change: `SAB_REACH` gained `-fno-req-handoff`; pattern, grep and plant unchanged, probe not weakened. The expectation (`first-memchr-bounded`) is the detector's own table entry, independent of the probe's source. Not yet shown: the plant is DETECTED with the new witness, which is the owed cloud mechrows run. Commit 3e58cf0de.

## FAMILY CHECK

Rows whose probe names `RX_DFA_PREFILTER`, `RX_REQ_WHY` or a first-memchr/class form: about 40 (grep of `SAB_REACH`; list in the sweep log). Six carry `first-*-bounded` without `-fno-req-handoff`: S481, S482, S483, S484, S485, S504. S482 and S484 (and the other hat rows) use `\B(?<!a)d` with `--memfn=no-window-search`; I checked that pattern by hand on today's build: `first-memchr-bounded` (reached, with that flag). The rest are decided by the reach sweep (OWED above), not by this grep.

## REACH SWEEP

OWED: queue key `650-s486re-reach`, see STATE AT HANDOFF. No result yet; no UNREACHED row is reported here because none has been measured.

## OWED

- `650-s486re-reach` (box queue, reach sweep, all rows).
- cloud `mechrows` run `s486re-rows` for S486 (owner main).
- If the sweep reports other UNREACHED rows: re-aim each the same way (find the arm the row's own detector uses), and report a count over 5 to the manager.
