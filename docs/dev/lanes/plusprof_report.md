# plusprof report

## Summary
Premise holds: nested `+` compile CPU grows about x4.5 per level (d=12 1.04 s, d=13 4.74 s) on a quiet box. The step is the `width` fact's frontier walk, `pcrec_width_walk` (src/facts/kset.c:385): 83% wdrain + 10% wclose + 7% walk. Filed as K159 and plan row [K159-PLUS-SUPERLINEAR]. Nothing fixed.

## Scaling
Pattern as in the brief; `build/pcrec -p rx -o OUT.c --pattern P`, main 715b90b5f, load1 1.5.
| d | cpu s | RSS KB | NFA states | C bytes |
|---|---|---|---|---|
| 9 | 0.01 | 8272 | 2046 | 15884 |
| 10 | 0.05 | 8184 | 4094 | 15900 |
| 11 | 0.22 | 10748 | 8190 | 15915 |
| 12 | 1.04 | 16588 | 16382 | 15930 |
| 13 | 4.74 | 28324 | 32766 | 15945 |
| 14 | 20.16 | 51340 | n/a | 15960 |
States double per level; time x4.5 per level, so about states^2.2. Emitted C is constant (about 16 KB), and gcc -O2 takes 0.03 s on d=12 and d=13 output. The 41 MB at d=15 was not reproduced with this pattern in the default configuration (likely the sweep's lifted-limits cell); not investigated.

## Profile
perf record -g, d=13, 19,008 samples: wdrain 83.3%, wclose 9.7%, pcrec_width_walk 6.6%, refine_by 0.15%, make_state 0.10%, DFA build 0.03%. One stage: the facts pass (PF_WIDTH, src/facts/facts.c:404).

## Cause
`pcrec_width_walk` advances the closed frontier one byte per step (`wadvance` kset.c:187), each step re-closing the whole frontier (`wclose` kset.c:166, `wdrain` kset.c:112). For an unbounded pattern the frontier never empties; the only exit is `j > nfa->n` (kset.c:408). So n+1 steps, each costing the closure size, which grows with the copied bodies. No fixpoint test exists on a repeated frontier.

## Filing
docs/dev/known_issues.md K159; docs/dev/plan.md [K159-PLUS-SUPERLINEAR]; `make -s test-plan-lint` passes.

## STATE AT HANDOFF
Committed on lane/plusprof. Last ruling applied: none (rulings file empty, R-0). No make test run (doc-only). Scratch: /var/tmp/pcrec-pcrec/scratch/plusprof.
OWED: none
