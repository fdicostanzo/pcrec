# Re-check: cofix amendments to 711 (check-order) and 712 (ramp vs chunk), 2026-11-20

Sized re-check, one critic who is also the verifier. Read-only. Everything written is under `/var/tmp/pcrec-pcrec/scratch/crit-memfn-cofix/`.

## Freeze
`freeze.sha256` was taken at 17:47 and re-checked at 17:53: **every file hash still matches**. It covers:
- 711: spike.py, decision_rule.md, decision_rule.body
- 712: rampchunk.py, decide.py, driver.c, rc_count.h, rc_window.h, decision_rule.md, rule_sha.txt
- the jobs 710, 711, 712 and common.sh
- cpuquiet/spec.md
- the ruling file `worktrees/memfn/docs/dev/reviews/2026-11-20-memfn-blockconfirm.md` (its RULING section is at line 155)

The stamps agree with the files:
- 711: RULE_SHA 28b518b84de080aa is the first 16 hex of sha256(decision_rule.body). spike.py's constant matches, and so does line 1 of the .md.
- 712: RULE_SHA efb4f0d7d3ab0bd5 is the first 16 hex of sha256(decision_rule.md), and rule_sha.txt holds the same value.

Rulings checked against: GATES-1, GATES-3 (with GATES-4 folded in) and MEASUREMENT-1 as they apply to 711 and 712, plus spec amendment 2'.

I did not read anything on the denylist.

## Per change

### (a) GATES-3 / spec 2': cap, banner and 100 ms observation
**711: CLOSED** (drill711.py, results in drill711.out)
- The cap binds. With a faked CPU-7 sample at 30 % busy, the uncapped value is 0.60 and CPU7_MAX comes out at 0.200 with `cpu7_capped` true. A repeat at 0.25 is void; one at 0.19 is not.
- The banner `**QUIET SAMPLE BUSY: CPU7_MAX capped at 20 % (sample max 30.0 %)**` is the first line after the H1 title of decision.md. It also goes to the log.
- Sample at 0.08: CPU7_MAX is 0.160, not capped, no banner.
- Sample at exactly 0.10: CPU7_MAX is 0.200, not capped, no banner. The spec says "exceed", so this is correct.
- 100 ms observation: with the timed pass forced to return at once, the /proc/stat window measured 0.1002 s. With a 30 ms pass it was 0.1010 s, and with a 150 ms pass 0.1504 s (no padding).
- The returned `secs` stays the repeat's own length (0.0001, 0.0309, 0.1503 s), so NIVCSW scaling is unchanged, as A6 says.
- Rule text A6 says the same as the code.

**712: CLOSED** (drill712.py, results in drill712.out)
- The same three samples give the same results: capped 0.200 with the uncapped 0.600 printed, then 0.160, then 0.200 not capped.
- I ran decide.py on a copy of the run-smoke-rampfix run with a capped qc.json:
  - It opens with the banner, then the thresholds line.
  - Apart from those two lines, the verdict body is byte-identical to the same run with no qc.json, so the amendment moves no verdict.
  - A run directory with no qc.json still decides (rc 0).
- 100 ms observation, real launches of fake exes: the window was 0.1015 s for an exe that exits at once, 0.1010 s at 30 ms and 0.184 s at 150 ms.
- rampchunk.py writes qc.json right after the quiet sample, before any cell is timed.
- The GATES-2 marker was re-made after the edit: check/record.txt pins the current hashes of rampchunk.py and decide.py, and the dry run reports the marker current.

### (b) MEASUREMENT-1 in 711: near-miss WINs re-timed and counted only if they repeat
**CLOSED** (drill711.py ran write_decision, the real function, on constructed rows: pattern co_hex8, cells nm-d25/50/75)

| drill | input | result |
|---|---|---|
| D1 | 3 WINs, all repeat | CANDIDATE, 3 of 3 (positive control) |
| D2 | 3 WINs; re-time gives WIN / TIE / LOSS | WIN-NR x2, counted as TIE: 1 of 3, no CANDIDATE |
| D3 | re-time of the arm short (n=2) | WIN-UNRETIMED x3, no CANDIDATE |
| D3b | re-time of FRONT short | WIN-UNRETIMED x3, no CANDIDATE |
| D3c | re-time reading is NaN | WIN-UNRETIMED x3, no CANDIDATE |
| D4 | re-time NOT-RUN (deadline) | WIN-UNRETIMED x3, NOT-RUN banner, no CANDIDATE |
| D5 | 0 counted cells (all main cells INCONCLUSIVE-NOISE) | "NO LOSS, but no near-miss WIN majority" under the NOISY RUN banner, never CANDIDATE |
| D7 | one WIN whose re-time reads LOSS | WIN-NR (TIE), the same as LOSS-NR the other way round; 2 of 3 still CANDIDATE, which is correct |
| D8 | WIN in a non-near cell | not re-timed, not in the majority test |

- In all of these, cells that did not hold their WIN stay in the denominator.
- The re-time request list (the `out=None` path) returns the near-miss WINs, so cmd_measure re-times them together with their FRONT.
- D4b (rerows=None giving CANDIDATE from WINs that were never re-timed) cannot happen in a real run: cmd_measure passes a list, and cmd_decide passes `[]` when there is no retime.tsv.
- The "expected false-WIN count: NONE AVAILABLE" line is printed. The rule says the same (A5).
- New estimate: 5805 s, up from 4131 s.
  - That decomposes as main 3507 s plus a near-miss share of 1594 s (45 %), so the worst-case term is what the code computes.
  - The near-miss share already covers LOSSes in near-miss cells; the 10 % allowance covers LOSSes elsewhere.

### (c) GATES-1: 712 waits on kit-checkorder only
**CLOSED**

Wait graph:
- 711: no wait keys. Its `--ready` only checks the HOLD-711 file (absent) and STOP_AT.
- 712: waits on kit-checkorder.
- 710: waits on kit-checkorder and kit-rampchunk.

This is a DAG, so there is no cycle.

When a key is cancelled, failed or `none`, boxqueue's cmd_state reports something other than pending/running, so the jobs depending on it go ahead. Nothing blocks, and no 77 cascade follows. While 711 is held by its HOLD file (exit 75), it shows as `pending`, so 712 and 710 wait as intended.

The job header and rule amendment 4 say the same thing.

### STOP_AT 2026-11-21 12:00 against the new estimates
**Holds.** Both dry runs produced their estimates from the amended code:

| job | estimate | cap | latest start | refusal at that point |
|---|---|---|---|---|
| 711 | 5805 s (6405 s with the quiet wait) | 13410 s | 10:23 on 11-21 | the body refuses before and after the quiet wait; measure refuses with 77 |
| 712 | 1402 s (2002 s) | 4604 s | 11:26 on 11-21 | `--ready` gives 77; the body checks again |

Worst case, with every repeat voided three times:
- 712: about 3840 s, under its 4604 s cap.
- 711: about 2x (the void loop re-runs pass A only), about 12.1 ks, under its 13.4 ks cap but with little margin. See N-1.

### Dry runs do no real work
**Holds.** I ran both jobs' `--dry-run` (rc 0 each; output in dry711.out and dry712.out) after touching a marker file. Afterwards, `find -newer` over checkorder/, rampchunk/ and the bconf-night tree returned nothing. There is no timing, perf run or build.

### Amended rules stamped before any timing
**Holds.**
- checkorder/ has no `run-*` directory.
- rampchunk/ has only run-smoke (15:07) and run-smoke-rampfix (15:47). Both are smoke runs, made before amendment 4 (17:29).
- 711's correctness marker check.pass (17:33:54) is newer than spike.py (17:32:34), and its src_hash covers spike.py.

## New findings (none can misread a verdict)
- **N-1 (711, cap-kill gap; made a little more likely by the amendment).**
  - 711 hands measure `--deadline STOP_AT` only. 710 hands min(STOP_AT, start + cap − margin) (its GATES-9 fix).
  - results.tsv is written only after the main pass, so a boxqueue cap kill leaves no verdict at all.
  - On a busy box, spec 2' voids more repeats, and each void re-runs pass A up to twice. My arithmetic puts the all-void worst case at about 12.1 ks against the 13.4 ks cap, and EST_CELL_S is UNMEASURED on this harness.
  - The outcome would be no verdict, not a wrong one.
  - PROPOSED **NOTED**, or a cheap FIX-NOW if the manager wants it: copy 710's three deadline lines into 711's body.
- **N-2 (711, already in the rule).**
  - When the main pass is cut by the deadline, the near-miss majority counts only the cells that ran. In drill D6, 1 of 3 near-miss cells ran, its WIN repeated, and the verdict read CANDIDATE "1 WIN of 1" under the NOT-RUN banner.
  - This is what rule A3 says ("take no part in any count"); the cofix change did not introduce it. With the window as wide as it is, it is unlikely to happen.
  - PROPOSED **NOTED**, or DOC: the verdict line should say "of N planned".
- **N-3 (712, a property of the 100 ms observation from amendment 1, not of cofix).**
  - 712's cold launches last 2–11 ms (the 18 smoke launches).
  - Observed over 100 ms, a burst on CPU 7 that falls inside one launch shows up as at most about 11 % busy, below any CPU7_MAX of 5–20 % only when the burst is that short.
  - So the CPU-7 test on cold cells is effectively a check on the 100 ms around the launch; the nivcsw test still applies to each launch.
  - It affects every arm alike, A/A included, so it cannot bias a direction. PROPOSED **NOTED**.
- **N-4 (re-queue order).** The `none` and `cancelled` states do not block. If 712 or 710 is re-queued before 711, it runs first. PROPOSED **NOTED**: re-queue in the order 711, 712, 710 (one batch with 711 first).
- **N-5 (wording only).** PROPOSED **DOC**:
  - 711's decision text still says "Void repeats this run: (main pass + LOSS re-time)"; it now also covers the WIN re-time.
  - The dry-run line says "710 waits on it" but does not mention 712.
- **N-6 (711, existing behaviour).** 711's `--ready` does not check the estimate, so a start late on 11-21 shows up as a red (DONE rc=1) where 712 and 710 would give a 77. PROPOSED **NOTED**.

(Side observation: CPU 7 was about 93 % busy at 17:52, with load 15.7. The jobs' quiet wait and sample handle that, but if the box stays this loaded, expect the QUIET SAMPLE BUSY banner.)

## Verdicts
- **711: READY TO TIME.** (a) CLOSED, (b) CLOSED. N-1, N-2, N-5 and N-6 do not block.
- **712: READY TO TIME.** (a) CLOSED, (c) CLOSED. N-3 and N-5 do not block.

Re-queue in the order 711, 712, 710 (N-4).

## RULING (kit manager, 2026-11-20)
711 and 712 READY TO TIME is accepted.
- N-1 NOTED: the worst case is 12.1 ks against the 13.4 ks cap.
- N-2 NOTED, to be read with the results.
- N-3 NOTED: a cold-cell caveat for 712.
- N-4: the queue order 711, 712, 710 is kept.
- N-5 DOC.
- N-6 NOTED: queued around 21:00, 711's latest start of 10:23 is far off.
