# growfile: filing the growth-sweep survey's crashes and runaways

Lane growfile (sonnet), 2026-11-20. Records only; no source or spec edit. Base: main 6134c8e8a.

## Summary

Five survey findings (KR-A..KR-E) were re-checked on main's build and on lane/k146land's build. The K146 branch fixes ONE (KR-C, the no-quantifier `vm_emit_node` chain, as a side effect of the `PCREC_OWN_FRAME` marks). The other four are filed as K148-K151 (K149 is KR-B, K147's second shape), with plan rows, plus the [GROWTH-SWEEP] umbrella and a corrected [LM-SPINE-DEPTH]. `make -s test-plan-lint` is green. K147 was not edited (its text exists only on lane/k146land); see "Known issues filed".

## Known issues filed

| K | survey id | what | function |
|---|---|---|---|
| K148 | KR-A | long zero-width run (`\b` x 30,000, `(?=a)` x 12,000) kills compile; limits.md §3.10¶1 is false (fix lane owns the spec hunk) | `lm_maxw`/`lm_flatten`, src/gen/lmwalk.c |
| K149 | KR-B | `(abc\|abd(...abe))*` x 200 kills compile with no backreference: K147's second shape | `first_of`/`text_first`, src/opt/possessify.c |
| K150 | KR-D | `(?:a\|b)` x N quadratic memory (3.46 GB at 5,000), no refusal | `lm_cat`, lmwalk.c:70 |
| K151 | KR-E | call-target chain N=200+ passes 2 GB before any refusal | `vm_build_region_saves`, emit_vm.c |

Every entry carries the repro, N, the signal or memory, the function and "the fix joins the general depth/size mechanism". K numbers start at K148 (main's highest is K146, k146land's K147). K149 is filed as its own entry instead of being folded into K147: K147's text exists only on lane/k146land, and editing it here would conflict at the landing. The landing should append K149's witness to K147 as a third shape. Merge note: known_issues.md and plan.md hunks sit at the file top and near [LM-SPINE-DEPTH] respectively; the K147 insert on k146land is adjacent, so expect a trivial keep-both conflict in known_issues.md.

## Plan rows

- [GROWTH-SWEEP] not-started: the owner's words quoted, waits on K147's landing, pairs with [LINT-FRAME], absorbs DEPTH_FAMILIES, refs the survey.
- [K149-FIRSTOF-NOBREF], [K150-LMCAT-QUADRATIC], [K151-CALLCHAIN-MEM]: one row per new K.
- [LM-SPINE-DEPTH]: "unreachable today" replaced by "REACHABLE on main", pointing at K148.
- Not filed: KR-C (fixed on the K146 branch). The survey's DEPTH-row suggestion for it (`e_lit4` shape, no quantifier) belongs to the [GROWTH-SWEEP] runner.

## Re-checks against the K146 branch

Binaries: main = worktree build of 6134c8e8a; K146 = `git archive lane/k146land` built in scratch. Stack `ulimit -s 432` (the compile thread is 442,368 B); memory cap 2g unless noted (rc 122 = watchdog memory kill). Generators: growsurv_evidence/gen.py.

| cell | main | lane/k146land |
|---|---|---|
| z_b 30,000 (KR-A) | 139 | 139 |
| cat_look 14,000 / 12,000 / 16,384 | 139 | 139 (14,000); 9,000 and 6,000 compile on main |
| e_lit3 250, 225, 200 (KR-B) | 139 | 139 (250); 150 and 100 pass |
| e_lit4 240, 220, 210, 200 (KR-C) | 139 | 0 (fixed) |
| cat_ncgrp 3,000 / 5,000 (KR-D) | 0 / 0 at 6g | 0 (3,000); no refusal either way |
| calls_chain 160 / 200 / 250 / 320 (KR-E) | 1 (refuse) / 122 / 122 / 122 | 122 (320) |
| e_ref 250 (K147) | 139 | 139 (K147 not fixed on the branch) |
| e_star 250 (K146 family) | 139 | 0 (fixed) |

Not done: KR-D's peak RSS was not re-measured (an unwatched run was declined); the K entry cites the survey's figures. Raw output: /var/tmp/pcrec-pcrec/scratch/growfile/recheck.txt.

## STATE AT HANDOFF

Committed on lane/growfile; rulings file empty; nothing owed.
OWED: none
