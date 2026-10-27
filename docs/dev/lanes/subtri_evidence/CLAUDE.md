# subtri_evidence/ — instruments behind docs/dev/lanes/subtri_report.md

Lane subtri (2026-10-27), evidence only; nothing builds or runs these.

- `drv.c` — find-all vs substitution driver, instructions:u/cycles:u around the call; `HASH=1` hashes every capture span.
- `drv_attr.c`, `pmc.h`, `attr_print.h` — the rdpmc per-stage attribution driver.
- `instr_*.diff`, `attr_*.diff` — the counter / attribution edits to each generated `rx.c` (main bdc2cb2e5).
- `proto_*.diff` — the span-identical what-if prototypes (5b, 2a, 2b, 7a-7d), NOT pcrec code.
- `*.tmpl` — the three templates in the pcrec dialect; `table.txt` — the consolidated instr/cycle table.
