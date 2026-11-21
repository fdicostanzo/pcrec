# CRITIC house: growth2 (r74)

## Findings


### HOUSE-1  (a) `--sample` and `sample_matrix()` are dead, future-proofing
CONFIRMED (grep). severity: maintenance/size; effort: delete 20 lines + CLAUDE.md clause; blast: none.
run_growth.py:269-281 (`sample_matrix`, a prime-stride sampler with a second `+` stride) and :532/:555 (`--sample`) are called by nothing: not run_growth.sh, not the Makefile, not run_compile_stack.sh, not docs/testing.md; only tests/growth/CLAUDE.md:30 names it. The matrix is 1,472 cells of a generated product; a sample was the lane's own probing aid. Owner rule "least that gives a trustworthy verdict, no future-proofing": delete (the matrix `+` branch it special-cases is also the one place the sampler knows about plus_edges' 4-cell groups).

### HOUSE-2  (a) failure-kind set is open-ended beyond use; `--pairs` / UNPAIRED prints 106 lines that are by design
CONFIRMED. severity: maintenance; effort: small.
(i) run_growth.py:173 accepts red kinds CRASH TIMEOUT RUNAWAY ERROR refused BUILD MATCHER compiled; cells.tsv uses only CRASH, RUNAWAY, compiled (K148/K150/K151/K156). TIMEOUT, ERROR, refused, BUILD, MATCHER have no user: the closed set is declared (good) but 5 of 8 members are speculative. Low cost; mention only.
(ii) The end-of-run report prints `UNPAIRED:` for every selected unpaired cell: 106 = 92 matrix `+`@251 (the depth limit has no limit half for `+`, by design) + 10 memory + 4 spine. A report whose normal state is 106 lines hides the 14 that matter (memory/spine); a declared reason column (or `pair=-` with a named reason, like norun=NAME) would make a NEW unpaired cell visible. As built it is noise and gives no verdict.

### HOUSE-3  (a) cost: the depth arm in `make test`
CONFIRMED (timed). severity: speed (small); effort: none needed, decision.
`judge_cell.py subject depth/grp@250` = 2.02 s wall; `--harness base` same cell = 1.16 s; the @251 stability twin = 1.29 s. So the matcher build+run adds ~0.85 s per depth limit cell (gcc -O0 of ~HW 120 KB-stack-sized C + 3 runs). x 33 limit cells = ~28 s serial extra, divided by the runner's jobs (cpu/2) = a few seconds wall in `make test`. It buys exactly what ruling limit-cell-matcher-cost/limit-test-criteria asks (limit cell compiles AND its matcher runs). Verdict: cost acceptable, keep. (Peak: cheap cells; the matrix-@250 cells are not in make test.)

### HOUSE-4  (a) 92 plus_edges rows: needed, but the "same 25 MB" justification is wrong for 2 of 3 probed cells
CONFIRMED (probe). severity: doc; effort: edit one string (NORUN_EXCEPTIONS text, CLAUDE.md, testing.md).
Emitted C at raise 1 (growth_driver one ... CSRC_OUT): group.plus.sole.lit@15 = 30.5 MB (21 s, 1.4 GB RSS to emit), named.plus.second.litalt@14 = 22.8 MB, group.plus.sole.bref@15 = 118.8 MB. run_growth.py:85-87 says "same 25 MB of C". The conclusion holds (gcc -O0 on the smallest, litalt@14 22.8 MB, hit the 90 s wall in my probe, peak RSS 650 MB at kill), but the number is not the measured one. Also: all 92 limit cells are compile-only, so the 92 rows buy "refused at E+1 by the named limit" and "compiles at E", i.e. a bisected edge pair per cell; one table row per cell is justified by the header (edge varies 12..15, 4/12/47/29 rows at E=12/13/14/15). The edge VALUES are the verdict; keep. But 92 is 4 values only: a (kind,core)->E map would be 28 rows if edge were per kind x core, header says position matters too; not proven here, not claimed.

### HOUSE-5  (b) cells.tsv header: "lm_cat, lm_cls, lm_alt2: 8 cells" is 4
CONFIRMED. severity: doc. cells.tsv:27 says "(lm_cat, lm_cls, lm_alt2: 8 cells)"; `run_growth.py --list | grep lm_` shows 4 (lm_cat_past, lm_cls_past, lm_alt2_past @8000 and lm_alt2_k150@4000). Also the header's "K150's runaway starts near N=4,770" vs three cells sized 8000 that are refused (not runaway) by the emit cap: the cells pass only because the emit cap refuses before the runaway; the claim "no just-before cell exists" is fine but its cause sentence mixes two ordering facts.

### HOUSE-6  (b) cnt_past: an NFA-limit stability family with no limit twin and no stated reason
CONFIRMED (bisect). severity: design/doc.
spine/cnt_past (`(?:ab){2,5}`, raise 1): edge = 9362 compiles, 9363 refuses (NFA exceeds); cells sit at 16384 and 100000 (1.75x and 10.7x past), UNPAIRED. No header line says why there is no limit cell at 9362 (owner ruling limit-test-criteria: each limit has a just-before cell). Likely the matcher-cost exception would apply (norun) but the table is silent. Either add the pair (norun=limit-cell-matcher-cost if it fits; check emitted size at 9362) or state the omission in the header like the K148/K150 ones. Same for memory/cnt_nest, calls_*, lm_* (the latter is explained).

### HOUSE-7  (b) Makefile comment "about 1,500 cells x 5 runs"
CONFIRMED, severity: doc (trivial). Population is 1,594; and limit cells' run count is not 5 (uncapped + up to 4 ladder rungs, rungs below 2x pattern size skipped, and a limit cell's uncapped run adds gcc+3 runs). Same "about 1,500" in docs/testing.md.

### HOUSE-8  (b) docs/testing.md "a stability twin one unit past it"
CONFIRMED. severity: doc. testing.md says the shipped-cap limit cells each have a twin "one unit past it"; actual twins: alt_lit 70773 (limit 70657, 116 units; header explains the main() delta), alt_cap_emit 802 vs edge 799 (probe: 800 already refused), cat_grp_emit 1009 (1008 already refused), named_emit 993 (991 refused). Only lit_ship/anchors_ship twins are n+1. The cells.tsv header states the real pairs; testing.md's sentence is wrong. Not a verdict defect: every twin is refused by the SAME limit (verified, "emitted code" / "NFA exceeds").

## PROBED-AND-HELD
About 45 cell runs. Edges n (compiles, with main for limit cells) and n+1 (refused by the SAME named limit) held for: depth grp, altnest, callouter (250/251); spine alt_lit 70657/70658 (twin 70773 refused, 70772 compiles as stability, so the twin gap is explained by main()); alt_cap_emit 799/800; cat_grp_emit 1007/1008; named_emit 990/991; lit_ship 131069/131070; anchors_ship 131070/131071; raise-1 z_cls 131069/131070; lit twin 131070; matrix `+` group.plus.sole.lit 15/16/250, sole.bref 15/16, named.plus.second.litalt 14/15 (limit text matches plus_edges.tsv). Counts held: 1,594 cells (696 limit/898 stability), 696 pairs, 106 unpaired (92+10+4), 105 exceptions (13+92), 33 depth families, 92 plus rows. gcc -O0 on the smallest plus edge C (22.8 MB) exceeded a 90 s wall (supports norun). Largest witness: z_cls 131069 (524,276-byte pattern); plus edge C of 118.8 MB.

CRITIC COMPLETE
