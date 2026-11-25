# Job 760-kit-u6time: the R-47 U6 C6/C6c timing record (dev box, Zen 4, 2026-11-24 01:00-01:06)

Frank cleared the window ("u6-timing-window: yes"), dev box only. The tree was b291a2f7c plus docs/dev/lanes/u6time* (eabf2edad). CPU 15, its SMT sibling 7.
- `job.log`: the job's log. Lines 1-8 are PREPARE and the no-clock rehearsal; the rehearsal's lines are the cause of the "expect stale" outcome. The timed run starts at "u6time: TIME".
- `results_c6_83fd4fd63765bed1.tsv`: the record, rule 9a2875a6bf089837, 486 rows.
- `quiet.tsv`: the slot Waiter, which went quiet after 130 s at load1 1.29.
- `quiet_sample_*.tsv`: the CPU-quiet control.

**Verdict** (c6decide):
- C6 on: NO LOSS. Readable 27 of 32, W/T/L 17/10/0, A/A rate 0.000.
- C6c off-clang: NO LOSS. Readable 11 of 12, 0/11/0.
- C6c off-os: NO LOSS. Readable 12 of 12, 0/12/0.
- NOT-RUN 0 and no TRUNCATED.

**Queue outcome** `failed rc=0 verdict=GREEN` (POPULATION-OVER, expect stale): the kit manager RULED IT GREEN. The job shape is fixed since (the rehearsal goes to its own file, c6decide's copy goes to a file, and the verdict pattern anchors on "; readable"). Replayed on this log's timed section, the fix gives done=1 and verdict=3.

**Boxes:** Zen 4 only. ubuntubudu (Zen 1) is UNAVAILABLE, an old box not planned to return. There is no Mac cell (Frank, 11-23).
