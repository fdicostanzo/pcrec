# Lane artconf -- report (2026-10-06, sonnet, branch `lane/artconf`)

[ARTREV] S4, the confirmer. Verdict tables: `docs/dev/optloop/artrev/confirm/verdicts.md` (raw TSVs beside it).

## Done
- Built pcrec at 57db5152 (detached worktree, `make CC=gcc-16`); `confirm_prep.sh` regenerated the three artifacts with it and
  all sha256 matched `pilot_pins.tsv` (A01 1588f520, A07 42a70983, A09 bc5bb11b). 26 twin arms imported.
- Extra arm `poss` for A07: `pcrec -p rx --features all --pattern '\b(\w++)\b\s++\1\b'` at the pin compiler: stamps
  `RX_VM_FRAMELESS 1`, `RX_VM_ENTRY_SHAPE "inline"`, zero `RX_PUSH` uses (only the macro definition). Its artifact.h differs
  (pattern comment, RX_RESUME_FRAMES 1 / RX_TRAIL_FRAMES 4), so it was installed by hand and ledgered as uncounted.
  Identity: PASS plain+san, 50,168 give-up repairs (oracle-checked), FAILS `--strict-giveup`.
- Hardened identity, plain and san, every arm: 52/52 PASS (`confirm/identity.tsv`); strict-giveup FAILS exactly the 10 arms with repairs.
- Timing on ubuntubudu (gcc 15.2), two passes per artifact plus an A07 re-run; verdict by the charter rule with the pad control.

## Results (CELL row, pad-controlled; full tables in verdicts.md)
- A01: L1 WIN (-72%); L2, L4 NOISE (pass 1); L3 NOISE on the cell, WIN on the dense subject only.
- A09: L1 WIN -95%, L2 WIN -76%, L6 (combo) WIN -95%; L3 and L5 NOISE (dense-only wins); L4 LOSS +23% on the cell and sparse, WIN on dense.
- A07: 12 of 13 reviewer arms WIN (-22% .. -83%), a_L6 NOISE (~2% on dense/sparse); `poss` WIN -58%.
- Scratch vs confirmed: b_L1-L4 (the only scratch-timed leads) agree 4/4 in verdict.
- Repair counts / `changes-giveup-surface`: A07 a_L2,b_L2 5,380; a_L3-L5, b_L3-L6 294,884; poss 50,168; all A01/A09 and a_L1,a_L6,b_L1 zero.

## Caveats and findings
- A07 pass 2 run `002` had `orig2` LOSS (-1.00%) on the dense generality row only; re-run as `003`, all controls NOISE everywhere;
  CELL verdicts identical across both runs. `003` is the reported run. (3 timing runs per A07 arm: bound met.)
- The plan's blanket `export ARTREV_REMOTE_CC=gcc` breaks local identity on the Mac (gcc = clang); discarded and re-ran the first
  batch of identity without it. Plan should say: export it for `time` only.
- Poor harness output: `summary.tsv` has no layout columns; `studies/artrev/confirm_collect.py` (new) joins `summary.txt`.
- The A07 stack arms' increments (tables, restart) were not isolated; only stack-vs-orig verdicts exist.
- Box wall about 21 min (7 runs). Last box run ended 10:45:04 EDT; remote lock and run dirs removed, `~/scratch_lx/artrev` is empty.
- I ran one `pkill -f` by mistake early on (denied by the permission layer, nothing killed); no process was disturbed.

## Joined
`generalize.md` section 3 `confirmed` column (15 ideas), `notebook/confirmed.md` (charter 3.2), per-artifact `A01|A09|A07a|A07b/confirmed.tsv`.
