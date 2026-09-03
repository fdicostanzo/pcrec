# [CC-DIFF] STEP 1 — lane ccdiff1

Both emitter spellings STEP 0 measured, landed as ONE abi event (16 -> 17).
Chartered by Frank 2026-09-03. Worktree `worktrees/ccdiff1`, branch
`lane/ccdiff1`, base `580f1a0`.

## 1. THE PREDICTION TABLE — written BEFORE the census

Recorded here first, per the brief, so the census can refute it.

| prediction | basis | value |
|---|---|---|
| VM-route artifacts gaining the attribute | = `RX_VM_FRAMELESS 1`; vmfl0's census (`optvmfl_step0.md`): 1,090 `frames==1 ∧ frameless` + 198 `frames>1 ∧ frameless` of 2,603 VM-compiled corpus+bench artifacts | **1,288 (49.5 %)** |
| ...of them reached under `auto` rather than `--engine=vm` | vmfl0: 385 of the 1,090 (290 as hybrids, 95 plain) | **385** |
| FRAMED artifacts whose bytes move | none: the gate is `has_push`, and the attribute is the only change on that route | **0, the abi stamp aside** |
| DFA-route artifacts folding >= 1 table | STEP 0 §2(d): 22 of 90 `auto` artifacts across bounded/loglines/altwide/email | **~24 %** |
| the folded artifact's own shape | `cls-upto-4` measured by hand before the census: 403 -> 373 source lines, 4 folds | **-30 lines, `_DFA_UNIFORM_FOLDS 4`** |
| direction of the emitted-size books | DOWN on folded DFA artifacts (a table and its legend leave), UP by a few bytes per header on frameless VM artifacts (the attribute text) | **both, opposite signs** |
| object code, frameless VM (`dig-upto-16 --engine=vm`) | STEP 0 §3-6: frame + canary + out-of-line call go | **`sub $0x98,%rsp` gone, `%fs:0x28` gone, `rx_search_run`/`rx_match_anchored` absent from `nm`** |
| object code, folded DFA (`cls-upto-4` auto) | STEP 0 §1: the table-base `lea`s and the frame go | **0 table `lea`s, 0 pushes in `rx_search`** |

## 2. WHAT LANDED

*(filled in below as the lane proceeds)*
