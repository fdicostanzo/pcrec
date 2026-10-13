# slotarms/ -- pcrec's engine arms for the joint timing slot

Lane `slotarms`, 2026-10-13; report `../slotarms_report.md`. The kit session owns and runs the slot; this
directory is delivered in the kit harness's ext contract (copy `arms.tsv build.sh gen_subj.py` to
`$OUT/ext/slotarms/`; `verify.sh` is ours, not part of the contract).

- `arms.tsv` -- `cell arm role subjects modes`: 6 cells (p1/p2/p3 x -first/-all), 14 arm lines, subjects `pc_*`.
- `build.sh` -- `OUT=... PCREC=.../pcrec bash build.sh`: subjects + `bin/<cell>/<arm>/{run,cnt,art.c,art.h}`. Embeds the
  arm spec (pattern, pcrec flags, expected engine stamps) and the driver (slot25c drv.c method + `check`/`cnt` modes).
- `gen_subj.py` -- `gen_subj.py OUT` writes `OUT/subj/pc_*` (empty, no-match 8/64/1Ki/64Ki, one match per 8/64/1Ki bytes).
- `verify.sh` -- `OUT=... bash verify.sh`: engine / no-kit-form stamps and answers vs python3 `re` (+ cnt twin).
Nothing here is timed by the lane.
