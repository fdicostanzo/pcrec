# N2 census -- [MEMFN-ROWCON] would-decline verdicts on pcrec sites

- results dir: build/scratch/n2_main_5fc4b0e5
- arm files merged: 107
- corpus rows: 5321
- distinct patterns: 4292
- composition files: 372
- arms in table: 107
- arms run: 107
- bin: /Users/fdicostanzo/pcrec/worktrees/memfn/build/scratch/n2_main_5fc4b0e5/tb/pcrec

## 1. Population

| quantity | count |
|---|---|
| arms | 107 |
| compiles attempted | 958292 |
| compiled | 858435 |
| refused (rc != 0) | 99857 |
| timeouts | 0 |
| sites traced (END with a chosen row) | 1072494 |
| selections with no row (kit refused the site) | 0 |
| would-decline selections | 129937 |

Sites traced by table, phase and chosen row:

| table | phase | chosen row | selections |
|---|---|---|---|
| arms | define | ofsskip | 56104 |
| arms | define | precheck | 299232 |
| arms | define | runcmp | 62908 |
| arms | use | ofsskip | 56104 |
| arms | use | precheck | 299232 |
| arms | use | runcmp | 62908 |
| runcmp | run | bytes | 360 |
| runcmp | run | memcmp | 97522 |
| runcmp | run | overlap | 121004 |
| runcmp | run | words | 17120 |

## 2. Would-decline verdicts, one line per (row, phase, site shape, failing fields)

| table | row | phase | site shape | failing fields (name:rule:class) | count | arms seen | witnesses [arm] stream src: pattern |
|---|---|---|---|---|---|---|---|
| arms | ofsskip | define | form=FUNC op=FIND handoff=RETURN | miss:R1:UNSTATED | 56104 | 102/107 | [--engine=dfa] c-default corpus: `b'(?!x)abc'`; [--engine=dfa] c-default corpus: `b'(?(DEFINE)(?<g>\\bab))(?&g)'`; [--engine=dfa] c-default corpus: `b'(?:(?<w>x)){0}a(?&w)b'` |
| arms | ofsskip | use | form=FUNC op=FIND handoff=RETURN | miss:R1:UNSTATED | 56104 | 102/107 | [--engine=dfa] c-default corpus: `b'(?!x)abc'`; [--engine=dfa] c-default corpus: `b'(?(DEFINE)(?<g>\\bab))(?&g)'`; [--engine=dfa] c-default corpus: `b'(?:(?<w>x)){0}a(?&w)b'` |
| arms | precheck | use | form=STMT op=ALL_PRESENT handoff=ASSIGN | miss:R1:UNSTATED | 17729 | 96/107 | [--engine=dfa] c-default corpus: `b'(?:(?i:ab)S\|(?i:abs))'`; [--engine=dfa] c-default corpus: `b'(?:(?i:abs)\|(?i:ab)S)'`; [--engine=dfa] c-default corpus: `b'(?:(?i:sab)\|S(?i:ab))'` |

## 3. R-6 table: per pcrec site kind, the field to state and the class it needs

Rule 1 (R1): the row uses the field and the site left it unstated -> state it.
Rule 2 (R2): the field is stated with a class the row does not serve.

| table | row | site shape | field | rule | observed class | phases | count | R-6 obligation |
|---|---|---|---|---|---|---|---|---|
| arms | ofsskip | form=FUNC op=FIND handoff=RETURN | miss | R1 | UNSTATED | define/use | 112208 | state `miss` |
| arms | precheck | form=STMT op=ALL_PRESENT handoff=ASSIGN | miss | R1 | UNSTATED | use | 17729 | state `miss` |

## 4. Reach: selections per chosen row (define + run phases)

| table | row | chosen |
|---|---|---|
| arms | generic | 0 |
| arms | ofsskip | 56104 |
| arms | precheck | 299232 |
| arms | runcmp | 62908 |
| runcmp | bytes | 360 |
| runcmp | memcmp | 97522 |
| runcmp | overlap | 121004 |
| runcmp | words | 17120 |

## 5. Reach: per row x field x class (nonzero cells)

| table | row | field | class | n |
|---|---|---|---|---|
| arms | ofsskip | fn_name | OTHER | 56104 |
| arms | ofsskip | lo | IDENT | 56104 |
| arms | ofsskip | miss | UNSTATED | 112208 |
| arms | ofsskip | n | IDENT | 56104 |
| arms | ofsskip | s | IDENT | 56104 |
| arms | precheck | indent | OTHER | 299232 |
| arms | precheck | lo | IDENT | 299232 |
| arms | precheck | miss | UNSTATED | 17729 |
| arms | precheck | n | IDENT | 299232 |
| arms | precheck | on_miss | JUMP | 299232 |
| arms | precheck | result | OTHER | 17729 |
| arms | precheck | s | IDENT | 299232 |
| arms | runcmp | lo | IDENT | 62908 |
| arms | runcmp | s | IDENT | 62908 |
| runcmp | bytes | run | MASKED | 360 |
| runcmp | bytes | run_len | MANY | 360 |
| runcmp | memcmp | run | EXACT | 97522 |
| runcmp | memcmp | run_len | MANY | 97522 |
| runcmp | overlap | run | EXACT | 121004 |
| runcmp | overlap | run_len | MANY | 121004 |
| runcmp | words | run | MASKED | 17120 |
| runcmp | words | run_len | MANY | 17120 |

## 6. Per-arm compile counts

| arm | attempted | ok | refused | timeout |
|---|---|---|---|---|
| --engine=dfa | 8956 | 4452 | 4504 | 0 |
| --engine=dfa+comments | 8956 | 4452 | 4504 | 0 |
| --engine=vm | 8956 | 8150 | 806 | 0 |
| --engine=vm+comments | 8956 | 8150 | 806 | 0 |
| --tune=max-speed | 8956 | 8149 | 807 | 0 |
| --tune=max-speed+comments | 8956 | 8149 | 807 | 0 |
| --tune=min-size | 8956 | 8149 | 807 | 0 |
| --tune=min-size+comments | 8956 | 8149 | 807 | 0 |
| --tune=size | 8956 | 8149 | 807 | 0 |
| --tune=size+comments | 8956 | 8149 | 807 | 0 |
| --tune=speed | 8956 | 8149 | 807 | 0 |
| --tune=speed+comments | 8956 | 8149 | 807 | 0 |
| -fmemfn-simd | 8956 | 8149 | 807 | 0 |
| -fmemfn-simd+comments | 8956 | 8149 | 807 | 0 |
| -fno-alt-island | 8956 | 8149 | 807 | 0 |
| -fno-alt-island+comments | 8956 | 8149 | 807 | 0 |
| -fno-altcls-factor | 8956 | 8149 | 807 | 0 |
| -fno-altcls-factor+comments | 8956 | 8149 | 807 | 0 |
| -fno-altcls-merge | 8956 | 8148 | 808 | 0 |
| -fno-altcls-merge+comments | 8956 | 8148 | 808 | 0 |
| -fno-anchored-dfa | 8956 | 8149 | 807 | 0 |
| -fno-anchored-dfa+comments | 8956 | 8149 | 807 | 0 |
| -fno-atomic-discharge | 8956 | 8149 | 807 | 0 |
| -fno-atomic-discharge+comments | 8956 | 8149 | 807 | 0 |
| -fno-cls-fold | 8956 | 8149 | 807 | 0 |
| -fno-cls-fold+comments | 8956 | 8149 | 807 | 0 |
| -fno-cls-kit | 8956 | 8148 | 808 | 0 |
| -fno-cls-kit+comments | 8956 | 8148 | 808 | 0 |
| -fno-cls-pack | 8956 | 8149 | 807 | 0 |
| -fno-cls-pack+comments | 8956 | 8149 | 807 | 0 |
| -fno-counter | 8956 | 8134 | 822 | 0 |
| -fno-counter+comments | 8956 | 8134 | 822 | 0 |
| -fno-ctx-node | 8956 | 8149 | 807 | 0 |
| -fno-ctx-node+comments | 8956 | 8149 | 807 | 0 |
| -fno-end-window | 8956 | 8149 | 807 | 0 |
| -fno-end-window+comments | 8956 | 8149 | 807 | 0 |
| -fno-hyb-reseed | 8956 | 8149 | 807 | 0 |
| -fno-hyb-reseed+comments | 8956 | 8149 | 807 | 0 |
| -fno-length-prune | 8956 | 8149 | 807 | 0 |
| -fno-length-prune+comments | 8956 | 8149 | 807 | 0 |
| -fno-lit-run | 8956 | 8149 | 807 | 0 |
| -fno-lit-run+comments | 8956 | 8149 | 807 | 0 |
| -fno-lit-run@utf8 | 8956 | 8165 | 791 | 0 |
| -fno-memfn-simd | 8956 | 8149 | 807 | 0 |
| -fno-memfn-simd+comments | 8956 | 8149 | 807 | 0 |
| -fno-offset-skip | 8956 | 8149 | 807 | 0 |
| -fno-offset-skip+comments | 8956 | 8149 | 807 | 0 |
| -fno-offset-skip@utf8 | 8956 | 8165 | 791 | 0 |
| -fno-possessify | 8956 | 8149 | 807 | 0 |
| -fno-possessify+comments | 8956 | 8149 | 807 | 0 |
| -fno-prefilter | 8956 | 8149 | 807 | 0 |
| -fno-prefilter+comments | 8956 | 8149 | 807 | 0 |
| -fno-prefilter-collapse | 8956 | 8149 | 807 | 0 |
| -fno-prefilter-collapse+comments | 8956 | 8149 | 807 | 0 |
| -fno-premul-table | 8956 | 8149 | 807 | 0 |
| -fno-premul-table+comments | 8956 | 8149 | 807 | 0 |
| -fno-req-byte | 8956 | 8149 | 807 | 0 |
| -fno-req-byte+comments | 8956 | 8149 | 807 | 0 |
| -fno-req-byte@utf8 | 8956 | 8165 | 791 | 0 |
| -fno-req-handoff | 8956 | 8149 | 807 | 0 |
| -fno-req-handoff+comments | 8956 | 8149 | 807 | 0 |
| -fno-req-handoff@utf8 | 8956 | 8165 | 791 | 0 |
| -fno-req-run | 8956 | 8149 | 807 | 0 |
| -fno-req-run+comments | 8956 | 8149 | 807 | 0 |
| -fno-req-run-fold | 8956 | 8149 | 807 | 0 |
| -fno-req-run-fold+comments | 8956 | 8149 | 807 | 0 |
| -fno-req-run-fold@utf8 | 8956 | 8165 | 791 | 0 |
| -fno-req-run@utf8 | 8956 | 8165 | 791 | 0 |
| -fno-req-set-lead | 8956 | 8149 | 807 | 0 |
| -fno-req-set-lead+comments | 8956 | 8149 | 807 | 0 |
| -fno-req-set-lead@utf8 | 8956 | 8165 | 791 | 0 |
| -fno-revdet | 8956 | 8149 | 807 | 0 |
| -fno-revdet+comments | 8956 | 8149 | 807 | 0 |
| -fno-run-overlap | 8956 | 8149 | 807 | 0 |
| -fno-run-overlap+comments | 8956 | 8149 | 807 | 0 |
| -fno-run-prefilter | 8956 | 8149 | 807 | 0 |
| -fno-run-prefilter+comments | 8956 | 8149 | 807 | 0 |
| -fno-run-prefilter@utf8 | 8956 | 8165 | 791 | 0 |
| -fno-scan-edge | 8956 | 8149 | 807 | 0 |
| -fno-scan-edge+comments | 8956 | 8149 | 807 | 0 |
| -fno-size-term | 8956 | 8148 | 808 | 0 |
| -fno-size-term+comments | 8956 | 8148 | 808 | 0 |
| -fno-splice-calls | 8956 | 8147 | 809 | 0 |
| -fno-splice-calls+comments | 8956 | 8147 | 809 | 0 |
| -fno-start-pinned | 8956 | 8149 | 807 | 0 |
| -fno-start-pinned+comments | 8956 | 8149 | 807 | 0 |
| -fno-start-set | 8956 | 8149 | 807 | 0 |
| -fno-start-set+comments | 8956 | 8149 | 807 | 0 |
| -fno-startpos-guard | 8956 | 8149 | 807 | 0 |
| -fno-startpos-guard+comments | 8956 | 8149 | 807 | 0 |
| -fno-tiered-entry | 8956 | 8149 | 807 | 0 |
| -fno-tiered-entry+comments | 8956 | 8149 | 807 | 0 |
| -fno-view-edge | 8956 | 8149 | 807 | 0 |
| -fno-view-edge+comments | 8956 | 8149 | 807 | 0 |
| -fno-vm-anchor-bound | 8956 | 8149 | 807 | 0 |
| -fno-vm-anchor-bound+comments | 8956 | 8149 | 807 | 0 |
| -fprefilter | 8956 | 5039 | 3917 | 0 |
| -fprefilter+comments | 8956 | 5039 | 3917 | 0 |
| -fprefilter-collapse | 8956 | 8149 | 807 | 0 |
| -fprefilter-collapse+comments | 8956 | 8149 | 807 | 0 |
| -fstartpos-guard=align | 8956 | 8149 | 807 | 0 |
| -fstartpos-guard=align+comments | 8956 | 8149 | 807 | 0 |
| -futf-check | 8956 | 8149 | 807 | 0 |
| -futf-check+comments | 8956 | 8149 | 807 | 0 |
| null | 8956 | 8149 | 807 | 0 |
| null+comments | 8956 | 8149 | 807 | 0 |
| null@utf8 | 8956 | 8165 | 791 | 0 |
