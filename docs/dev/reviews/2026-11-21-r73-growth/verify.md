# r73 growth — coordinator inline verification (section 6.2 inline form: every CONFIRMED finding is a quote claim or a one-call repro)

### DEPTH-1 — HOLDS
bash -c 'fail=0; gp=66; gf=""; case "$gp$gf" in ""|*[!0-9]*) echo RED;; *) fail=$((fail+gf)); [ "$gf" -eq 0 ] && echo PASSLINE;; esac; echo fail=$fail'
-> "[: : integer expected", fail=0 (no RED, no fail): a missing `runs failed:` line is green. growth_rc is printed only.
### DEPTH-2 / VERDICT-7 — HOLDS (reading): run_growth.py filters by --only with no emptiness check; the parse accepts gp=0.
### DEPTH-3 — HOLDS (quote): depth_families.tsv header still says "checked ... below".
### VERDICT-1 — HOLDS (quote + census as the critic printed); the depth@250 part is asked for by the [GROWTH-SWEEP] row's own `next:` ("at depth 250 and 251").
### VERDICT-2 — HOLDS: run_growth.py:218-219 `return kind in ("compiled", "refused")`; `refused` = any driver rc != 0 line (:204-206), rc=-9 "could not start" included.
### VERDICT-3 — HOLDS: run_growth.py:149 `"compile,refuse:"`; :213 `alt[7:] in text` with alt[7:] == "" is always true.
### VERDICT-4 — HOLDS: scripts/watchdog header: 123 = CPU-time kill; run_growth.py tests only 124 (:195) and 122 (:197).
### VERDICT-5 — HOLDS (quote): red branch counts every non-pass as KNOWN-RED regardless of kind.
### VERDICT-6 — HOLDS: run_growth.py:324 `if ok.returncode != 0 or nok.returncode == 0`.
### VERDICT-8 — HOLDS (quote): :231 one untagged `$PCREC_TMPDIR/growth-walls.tsv`; :282 progress log beside it.
### HOUSE-1 — HOLDS (critic's quote); coordinator adds: the CONTROL arm runs BASE's compile_stack_driver, the depth cells now run growth_driver.
### HOUSE-3 — HOLDS (quote) for the dead `if good:` block and the open `else` on the stack column.
### HOUSE-4 vs VERDICT's held note (contradiction, one item) — PARTLY
src/core/sb.c:441 `strdup("")` exists (HOUSE right, VERDICT's "no libc strdup in the compile path" wrong). But NO negative drift reproduced: an instrumented copy of growth_driver.c (.coord/v/drv.c: one printf of heap_live per cell), plain build -DGROWTH_HEAPCAP + the four --wrap flags, a 20-line series (grp@250, grp@251, longwrap@250, compound@250, z_b_past@400000; 3 uncapped + 1 at 32 MB each) -> heap_live 0 after every uncapped cell; the drift mechanism is real in principle but this population never reaches it. Side observation: longwrap@250 refused at 32 MB leaves heap_live = 32,776 (stays to the end) = K155's 32 KB buffer, visible without ASan.
### HOUSE-5 / VERDICT-9 — HOLDS: `grep -c K155 tests/growth/cells.tsv` = 0; tests/thread/CLAUDE.md not in the diff and names no tests/growth.
### HOUSE-6(5) — HOLDS: growth_driver.c:156 `setrlimit(RLIMIT_DATA, &r);` return value unchecked (and getrlimit at :153).
VERIFY COMPLETE
