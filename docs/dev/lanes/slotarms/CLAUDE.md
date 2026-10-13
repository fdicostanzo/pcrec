# slotarms/ -- pcrec's engine arms for the joint timing slot

Prepared (NOT timed) by lane `slotarms`, 2026-10-13; report: `../slotarms_report.md`.
The memfn kit session owns and runs the slot; this directory only supplies the arms.

- `arms.tsv` -- the 7 cells (pattern, pcrec flags, subject family, expected engine stamps).
- `gen_subj.py` -- deterministic subject generator (empty, no-match 8/64/1Ki/64Ki, one match every 8/64/1Ki bytes).
- `build.sh` -- pcrec -> `$OUT/bin/<cell>/V0/{art.c,art.h,run}` (kit harness layout) + `$OUT/subj/`; -j2, pinned.
- `drv.c` -- the kit's vdrv.c driver (no KEEP) plus a `check` mode; `run SUBJECT [first|all] [check]`.
- `verify.sh` -- engine/no-kit-form stamps per cell, and every (cell, subject, mode) answer vs python3 `re`.
- `time.sh` -- the kit's timing method over these arms (absolute ns, A/A floor); `--estimate` times nothing.

`OUT` defaults to `<worktree>/build/slotarms` (gitignored). Run `make` first for `build/pcrec`.
