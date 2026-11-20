# k147f2 — review r64's rulings applied to the K147 fix

Lane k147f2 (sonnet), branch lane/k147f2, cut from lane/k147fix ceae6bcab. Scratch: /var/tmp/pcrec-pcrec/scratch/k147f2/.
Premise test: `git log --oneline -1` read ceae6bcab. F2's DIED reproduced (rc 139 on the 442,368-byte thread); F5's plant reproduced NOMATCH (below).

## Summary

All FIX-NOW items (F1, F3-F10) and PLAN/DOC items (F2 -> K152, F11, F12, F13) are applied; the four process changes are in the skill.
No emitted-byte mover: a 368-compile and a 1,500-compile BASE-vs-lane comparison (below) read 0 movers (`--list-limits` text aside, which is the declared F1/F6 move).
The committed identity sweep (`scripts/emit_sweep.py`) is DONE: every stream 0 movers. The new sabotage row S3440 ran through the matrix as a queue job: DETECTED (66 corpus failures, possdiff 0 fail, reach ok), no unexpected or unreached; its plant was also shown red by hand. Two pins moved and were re-pinned: the start-set VM mover manifests (+2 rows) and rxtsource's census and C3 pins (+2 blocks, +135 case lines).

## Fixes by finding

Every number below was produced by the harness driver the stack suite uses, built from this tree: `gcc -O2 -I lib -o drv tests/thread/compile_stack_driver.c build/libpcrec.a -lpthread -lm`, run as `drv STACK PATTERNFILE all 0` (VM rows: engine 2). The family rows are also printed by `bash tests/thread/run_compile_stack.sh` (RECORD lines, log /var/tmp/pcrec-pcrec/scratch/k147f2/stack.log). Musl depths: a bisection over depth 1..250 for the largest depth whose `drv 131072` run did not die.

- F1 (limits.md §3.10 ¶1-¶5, limits.def PCREC_COMPILE_STACK_BUDGET). The worst of the margin-bearing families with an element beside the nest is 344,560 B (`(?:a|b(?:a|b…c)*)*d`; also the capturing, named, atomic, `*?` and `*+` spellings), 442,368/344,560 = 1.284. The literal-branch family (K152) is 440,560 B (1.004), and K148 stays. ¶1 now names two exceptions (K148, K152); ¶2 and ¶5 say the headroom holds for every family except those; the limits.def row says 1.28x today and names both defects (the `--list-limits` text moves, as ruled). ¶3 restated entirely from the measurements in F3.
- F3. Re-measured with `d` as a trailing element AND as a leading one (same numbers either way): ncaltrep 344,560 (alone 344,176); altrep 344,560 (alone 257,552); `*?` 344,560; `*+` 344,560 (alone 293,552); `?` 312,560; atomic/named altrep 344,560; `+`/`{2}` refused after at most 314,224; brefrep/brefsrep 257,792 (alone 257,552), `\1` with `*+` 293,792; lookrep 297,776 (alone 297,536); optnest 208,504 (alone 185,936); lookarounds/atomic/named/inline 204,552 / 196,552 / 200,552 / 212,696 (as before); groups 120,552; call rows 120,552; compound 225,496 (as before); the 251 refusals at most 214,152 (as before); litrep and non-capturing literal 440,560 (alone 317,504 and 440,176); literal `+` refused after 410,224 (alone 409,840). ¶4 depths at 131,072 B with the element: 83 (ncaltrep, altrep, `*+`), 88 (lookrep; 87 alone), 115 (brefs), 149 (optnest), 145-159 (lookarounds etc.), 129 (compound), 250 (plain), 64 (litrep and non-capturing literal). DEPTH_FAMILIES gained altpos (`*+`), altpost, ncaltpost, litpost, altpospost, brefpost, optpost (tests/thread/run_compile_stack.sh); `bash tests/thread/run_compile_stack.sh`: 65 passed, 0 failed (the 7 new rows add 14 depth checks).
- F4. 16,792 -> 18,552 B (conditionals and branch resets, RECORD lines of the same run).
- F5. Two cells in tests/possessify/possessify.rxt after the B-depth cells: K=64 (arm B ends exactly at the bound: a control) and K=65 (one past it: the witness), each with every group slot, python3 `re` and libpcre2 10.46 (ctypes, `pcre2_match_8`) agreeing: K=64 match 0 66, K=65 match 0 67. Sabotage row S3440 (`src/opt/possessify.c`, first_eval's `widen:`: `v = fst_leaf(q, f->a)` -> `v = f->acc`). Plant shown red by hand: BASE-built tree + this tree's possessify.c with the plant, `bash tests/harness/run.sh` on the two cells: 66 of 135 cases fail (the K=65 match and its 65 group slots; the K=64 control stays green), the clean tree 135 of 135. The matrix row itself is OWED (Validation).
- F6. limits.def PCREC_MAX_POSS_REF_DEPTH text: bounds the arena frames and the work of one resolution, no longer the C stack; labelled UNMEASURED (a compile-cost cap kept from the C-stack days).
- F7. PCREC_OWN_FRAME dropped from `fst_leaf` with its header sentence (it is a leaf under a non-recursing fold).
- F8. gk_build's CAT and ALT loops and ss_walk's ALT loop are on PCREC_SPINE_EACH; the A_CAP/A_ATOMIC tail call is `a = a->l; goto again;`. ss_walk's union now starts as the empty union (no bytes, not nullable), equal to the old first-branch seeding because OR is commutative.
- F9. `text_first`/`cap_group` replaced by `first_eval`'s `text` reading in possessify.c comments, src/opt/NOTES.md, S604's SAB_DESC and S602's prose and figure; the who-label `"text_first"` is `"first_eval"`; first_eval's post-switch arm is `pcrec_ctx_fail` (noreturn, like FK_BREF). Anchor tripwire: `python3 scripts/m6read_check_sab_anchors.py`: 1368 rows, all anchors resolve.
- F10. [POSS-CTX-TABLE] status records the fired trigger and what remains.
- F11. docs/dev/guide/coding.md OWN_FRAME paragraph gained the third case; plan row [ARENA-REGROW] (allocation half ready, walk-stack primitive waits for a fourth member).
- F12. Note on [GROWTH-SWEEP] (`item_first` stays on C recursion, 352 B/level, ~88 KB at 250).
- F13. PLAN note on [LINT-FRAME] (gk_build CAT update order: find a witness first; the rest answer-silent, noted). No other change.
- F2 -> K152: see below.

## K152 filing

docs/dev/known_issues.md K152 (newest first, the file's form) and plan row [K152-NFA-DEPTH] STATE:not-started next to [K147-POSSESSIFY-DEPTH]; K152 is in [GROWTH-SWEEP]'s red cells and [LINT-FRAME]'s refs. Witness `^(?i:` + `(?:abc|abd` x249 + `abe` + `)*` x249 + `)|b$`: DIED rc 139 at 442,368 (reproduced here), 452,080 B on an 8 MB thread (reproduced: `drv 8388608`, rc 0 hw=452080). The cause is the review's, "unverified by gdb": I did not run gdb. No DEPTH_FAMILIES row for it: the harness has no expected-fail form (its DEPTH arm fails on a death), so the shape is listed in K152 and the plan row for the fixing lane to add with its fix.

## Process changes applied

.claude/skills/pcrec-critic/SKILL.md, each tagged "r64 k147fix": the contract lens row gained the restated-paragraph rule (re-read margin/ratio sentences and limits.def text) and the worst-POSITION rule; section 6 item 2 gained the coordinator-built plant rule for a SUSPECTED coverage claim; the COMMON plants sentence gained the exact-SAB_COUNT applier rule (the COMMON template has no separate applier paragraph, so it rides that sentence).

## Identity

No generated-code change by construction (the src edits are F7-F9: attribute, loop shape, a comment, a label string, an unreachable arm, one limits text).
- `python3 scripts/emit_sweep.py --ref ceae6bcab --ref-bin <clean ceae6bcab build in scratch> --bin build/pcrec --jobs 4 --comp-jobs 2 --out /var/tmp/pcrec-pcrec/scratch/k147f2/sweep "--dumps-declared-rows=--list-limits:PCREC_COMPILE_STACK_BUDGET,--list-limits:PCREC_MAX_POSS_REF_DEPTH"`: `emit_sweep: DONE rc=0`, 170 s, 7,233 corpus patterns: c-default, c-vm, emit-ir-vm, facts, the four emit-ir-auto arms, stderr, composition (466 files) and dumps (7) streams all `movers=0 asymmetric=0`, every tag floor held. The dumps stream's 2 declared moves are the `--list-limits` rows of F1/F6. Log: /var/tmp/pcrec-pcrec/scratch/k147f2/sweep.log. The sweep ran on the tree before the B-depth cells moved to the file's end and before the re-pins; those later commits touch tests only (`git diff 04ad1e0ca HEAD -- src` is empty).
- Interim, my own: a clean ceae6bcab build (`git archive ceae6bcab`, `make -j4`, in scratch) against this tree's build, `-p rx --features all` emitted C + stderr + rc compared byte for byte: 184 patterns (every unique pattern line of tests/possessify/possessify.rxt including the new cells, backreference chains K=60..69, three nest shapes) x 2 engines (default, vm) = 368 compiles, 0 movers; and 1,500 patterns sampled (seed 7) from tests/*/*.rxt x the default engine: 1500 compiles, 0 movers.

## Validation

Run in this worktree on the final tree (the commit tip):
- `make -j4`: clean; `make -s strict`: passes (whole tree -Werror -Wshadow).
- `make test-stackdepth` equivalent, `bash tests/thread/run_compile_stack.sh`: 65 passed, 0 failed.
- `make test-registry`: 79 passed, 0 failed. `make test-possessify`: 44 passed, 0 failed (possdiff and possessify_tests, 2/2 scripts).
- `bash tests/harness/run.sh tests/possessify/possessify.rxt`: 3788 cases passed, 0 failed (includes the two new cells).
- `make -s test-plan-lint`: 384 rows, 0 violations, selftest 45 plants. `make -s test-spec-history`: 11 passed. `python3 scripts/m6read_check_sab_anchors.py`: all anchors resolve.
- `make test-startset` was RED once on the first full run: `run_vmhat_checks.sh` found the 27 shifted manifest rows (the two cells inserted mid-file moved the line keys). Fixed by appending the cells at the END of possessify.rxt (no existing row moves) and adding the 2 new VM-hat mover rows to tests/startset/manifests/manifest_s2_vm_auto.tsv and manifest_s2_vm_forced.tsv; `bash tests/startset/run_vmhat_checks.sh`: 22 passed, 0 failed; `run_startset_checks.sh` 3/0; the dfa-hat part of `make test-startset` read 35/0 before the move and was not re-run after it (the cells are not DFA movers).
- `bash tests/rxtsource/run_rxtsource_tests.sh` (the file itself): red on the census (7233/100188 vs pinned 7231/100053) and on C3 pass/verifiable; re-pinned CENSUS_BLOCKS/LINES, RUNSH_BLOCKS/LINES, C3_PASS 24840, C3_VERIFIABLE 27259 (the two cells are python-verifiable, so their `# pcre2-only` marker was dropped); then 300 passed, 0 failed.
- `make test-possessify` 44/0 (re-run after the move), `make test-endmark` 46/0, `make test-compound` 17/0 + 16/0 + 4/0, `make test-thread` rc 0.
- `make test-spec` FAILS 13 of 14 checks (`did not compile`) on this tree AND on a clean ceae6bcab build alike (`make -C <scratch base> test-spec`: the same 13 failed): environmental and pre-existing, not from this lane; not investigated.
- Not run: `make test` and `make test-axes` (the manager dispatches the cloud run), and the size tripwire of `test-corpus` (two python-verified blocks appended to a file the size log reads).
- `bash tests/mech/run_sabotage_matrix.sh S3440` through `scripts/boxqueue add` (job 200-k147f2-mech, 138 s): DETECTED, `== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, oracle-skipped: 0)` at the tree 87e3e41d7 (src-identical to the final commit). S602 and S604 were re-worded only (text, not anchors); their rows were not re-run.

## STATE AT HANDOFF

Rulings file docs/dev/lanes/k147f2_rulings.md: empty; last R-n applied: none. Branch lane/k147f2 committed at the tip named in the handback. Every finding F1-F13 is done; the items not done by design: no gdb for K152, no DEPTH_FAMILIES row for K152 (no expected-fail form), no CLAUDE.md touched (size check not needed). No STOP was hit.

OWED: none. The S3440 matrix row ran as boxqueue job 200-k147f2-mech (the first direct launch had died waiting on the box lock): `== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, oracle-skipped: 0) at 87e3e41d7`, verdict DETECTED: reach ok (1/1), pop 1 (want >=1), corpus 66 fail / 3722 pass, possdiff 0 fail / 294 pass. Job dir /home/pcrec/projects/pcrec/worktrees/.boxqueue/done/20261120T184824.280080792-200-k147f2-mech.
