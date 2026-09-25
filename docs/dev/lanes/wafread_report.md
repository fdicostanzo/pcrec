# Lane `wafread` — delivery report (S3: WAF cells attribution)

2026-09-25. Branch `lane/wafread` from main `ea51a4b3`, opus, LIGHT tier.
It built `build/pcrec` in the worktree and compiled and read artifacts. It ran
no `make test` and took no darwin timing.

## Delivered

- `docs/dev/optloop/waf_attribution.md`: the reading. Findings first: a table
  per cell, the four headline answers, the next step, the Linux request (§4)
  and two questions for Frank (§5).
- `docs/dev/optloop/waf/`: the instruments, with their own `CLAUDE.md`:
  - `mk_twin.py`: the plainloop and ciprecheck twins;
  - `check.sh` and `spans.c`: span-for-span answer identity;
  - `mk_inputs.py`: match.bin and split.rx;
  - `waf_numbers.py`/`.txt`: the bench ns/B and the subject census;
  - `stamp_join.sh`/`.txt`: all 64 patterns' stamps joined to ns/B.
- The `optloop/CLAUDE.md` entry.

## Result, for a fresh agent resuming

**Cells and causes:**

| cell | cause | mechanism | caseless |
|---|---|---|---|
| concat-sqli | `ENG_ATTEMPT` (measured ×3.51) + per-step residual | `[OPT-ATTEMPT-SPLIT]` | no |
| union-select | L3 byte-at-a-time `{u,U}` walk, ~80% of the cell; three caseless necessary runs invisible to reqbyte | **S4(a)**, predicted 0.12-0.27 ns/B vs re2's ShiftDFA 0.319 | **yes, the one S4 customer** |
| sleep-benchmark | not an algorithmic loss; pcrec beats every scalar engine | none | multi-literal only (held) |
| dbnames | 63-byte `\b` first set + per-step residual | `[OPT-FIRSTSET]`, predicted 2.09 ns/B | no |
| slack | a win at 0.77×; its memchr+verify rate is the S4(a) calibration | none | no |

**Corrections to prior documents:**

- compare_stack §6.3's "(c) multi-literal" for dbnames/concat is refuted. The
  winner is re2's plain lazy DFA at 1.63 ns/B, and rust's multi-literal
  prefilter loses to it.
- compare_stack §6.2 and wordfold_census call slack a "near-tie". It is a win.
- sleep-benchmark +7.5% drift since the pin: unattributed (Linux L4).

## Validation (answers only, darwin)

- **Twins identical to their base:** 8 of 8 (4 plainloop, 4 ciprecheck) are
  SAME on t-64k/t-256k/t-1m (0 matches) and on match.bin. The match.bin counts
  are dbnames 7, split 10, union 9, sleep 6, equal to python `re`.
- **The checker can fail:** two failing-direction controls DIFF. A wrong run
  gave 9 → 0, and a d/D/i skip gave 7 → 2.

## OWED

The §4 Linux executor block: U1-U3, L1, L2 (FIRSTSET rerun), L4. Nothing is
running. No log is pending.
