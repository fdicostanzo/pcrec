# Row reach (prototype, `reach/`), per table row and cell

Counts are ATTEMPTS (T1: arrivals; T2/T3: admissions/gates; T4: compiles) at the `base` arm per variant; `all arms` sums every variant x arm; `arms` lists the arms that reach the cell. One witness each.

## T1

| row | cell | plain | lowsize | lowdfa | lowboth | lowthr | all arms | arms | witness |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| forcing | - | 0 | 0 | 0 | 0 | 0 | **0** | - | - |
| nomem | - | 0 | 0 | 0 | 0 | 0 | **0** | - | - |
| unroll-rescue | - | 0 | 0 | 0 | 0 | 0 | **0** | - | - |
| size-term-trial | other | 3 | 21 | 3 | 6 | 3 | 256 | base,fof,minsize,no-anch,no-pf,no-pfc,no-premul,pf,pfc,vm | `((?:(?:(?:[^a]{1,2}\|[^a]??\|.{0,2}?)+){0,8}(){2,3}){1,2}){2`  (lowboth/base) |
| sel1-collapse | overflow | 4 | 4 | 95 | 95 | 4 | 1704 | base,fof,minsize,no-anch,no-pf,no-premul,no-st,pfc,unroll4 | `(a{1,3}){65}`  (lowboth/base) |
| sel1-drop | overflow | 2 | 2 | 69 | 69 | 2 | 1340 | base,fof,minsize,no-anch,no-pfc,no-premul,no-st,pfc,unroll4 | `(?:[a-z0-9!#$%&'*+/=?^_`{\|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{`  (lowboth/base) |
| prefilter-collapse | size | 3 | 104 | 0 | 84 | 3 | 1591 | base,minsize,no-anch,no-premul,no-st,pf,pfc,unroll4 | `(\\bcat\\b)+`  (lowboth/base) |
| drop-anchored | size | 15 | 98 | 0 | 38 | 15 | 1303 | base,dfa,minsize,no-pf,no-pfc,no-premul,no-st,pfc,unroll4 | `(*UCP)(?i)\\d` -e utf8  (lowboth/base) |
| drop-premul | size | 0 | 74 | 0 | 13 | 0 | 765 | base,dfa,no-anch,no-pf,no-pfc,no-st,pfc,unroll4 | `(*UCP)(?i)[\\dk]` -e utf8  (lowboth/base) |
| drop-prefilter | size | 3 | 92 | 0 | 75 | 3 | 1489 | base,minsize,no-anch,no-pfc,no-premul,no-st,pfc,unroll4 | `(\\bcat\\b)+`  (lowboth/base) |
| refuse | other | 442 | 442 | 442 | 442 | 442 | 44108 | base,dfa,fof,minsize,no-anch,no-pf,no-pfc,no-premul,no-st,pf,pfc,unroll4,vm | `\\A*`  (lowboth/base) |
| refuse | overflow | 0 | 0 | 0 | 0 | 0 | 68 | dfa,pf | `(?:ab){0,16000}`  (lowboth/dfa) |
| refuse | size | 0 | 86 | 0 | 37 | 0 | 2025 | base,dfa,fof,minsize,no-anch,no-pf,no-pfc,no-premul,no-st,pf,pfc,unroll4,vm | `(?:aa\|a){8,12}+ab`  (lowboth/base) |

## T2

| row | cell | plain | lowsize | lowdfa | lowboth | lowthr | all arms | arms | witness |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| backref | NONE | 453 | 453 | 453 | 453 | 453 | 21744 | base,fof,minsize,no-anch,no-pf,no-pfc,no-premul,no-st,pfc,unroll4,vm | `^(a)(?i:\\1)$`  (lowboth/base) |
| linked-call | NONE | 106 | 112 | 106 | 112 | 112 | 5196 | base,fof,minsize,no-anch,no-pf,no-pfc,no-premul,no-st,pfc,unroll4,vm | `(a\|b(?1)c)+`  (lowboth/base) |
| var-nullable | NONE | 12 | 12 | 12 | 12 | 12 | 516 | base,fof,minsize,no-anch,no-pf,no-pfc,no-premul,no-st,pfc,unroll4 | `^${v}{2}$`  (lowboth/base) |
| nullable-exact | NONE | 109 | 109 | 109 | 109 | 109 | 4627 | base,fof,minsize,no-anch,no-pf,no-pfc,no-premul,no-st,pfc,unroll4 | `(\\z)*`  (lowboth/base) |
| nullable-collapsed | SEL1 | 1 | 1 | 1 | 1 | 1 | 39 | base,fof,minsize,no-anch,no-pf,no-premul,no-st,pfc,unroll4 | `(?:ab){0,16000}`  (lowboth/base) |
| overflow-drop | NONE | 2 | 2 | 69 | 69 | 2 | 1436 | base,fof,minsize,no-anch,no-pfc,no-premul,no-st,pfc,unroll4 | `(?:[a-z0-9!#$%&'*+/=?^_`{\|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{`  (lowboth/base) |
| overflow-drop | SEL1 | 0 | 0 | 0 | 0 | 0 | 148 | no-pf | `a{500}`  (lowboth/no-pf) |
| forced-on | NONE | 0 | 0 | 0 | 0 | 0 | 6514 | pf | `a(b\|c)+d`  (lowboth/pf) |
| forced-on | SIZECAP | 0 | 0 | 0 | 0 | 0 | 233 | pf | `(\\bcat\\b)+`  (lowboth/pf) |
| forced-off | NONE | 0 | 0 | 0 | 0 | 0 | 15813 | no-pf,no-pfc,pfc | `a(b\|c)+d`  (lowboth/no-pf) |
| forced-off | SIZECAP | 3 | 92 | 0 | 75 | 3 | 1230 | base,minsize,no-anch,no-premul,no-st,pfc,unroll4 | `(\\bcat\\b)+`  (lowboth/base) |
| var | NONE | 11 | 11 | 11 | 11 | 11 | 544 | base,fof,minsize,no-anch,no-pfc,no-premul,no-st,pfc,unroll4,vm | `^${prefix}-[0-9]+$`  (lowboth/base) |
| default-on | NONE | 1268 | 1502 | 1268 | 1424 | 1509 | 52389 | base,fof,minsize,no-anch,no-pfc,no-premul,no-st,pfc,unroll4 | `a(b\|c)+d`  (lowboth/base) |
| default-on | SEL1 | 3 | 9 | 94 | 184 | 9 | 2003 | base,fof,minsize,no-anch,no-premul,no-st,pfc,unroll4 | `(a{1,3}){65}`  (lowboth/base) |
| default-on | SIZECAP | 3 | 104 | 0 | 84 | 3 | 1358 | base,minsize,no-anch,no-premul,no-st,pfc,unroll4 | `(\\bcat\\b)+`  (lowboth/base) |
| default-off | NONE | 2445 | 2602 | 2430 | 2481 | 2445 | 125856 | base,dfa,fof,minsize,no-anch,no-pfc,no-premul,no-st,pfc,unroll4,vm | `b\|c`  (lowboth/base) |

## T3

| row | cell | plain | lowsize | lowdfa | lowboth | lowthr | all arms | arms | witness |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| rung-sizecap | - | 0 | 54 | 0 | 41 | 0 | 786 | base,minsize,no-anch,no-premul,no-st,pf,unroll4 | `(?:a\\K){2,}b`  (lowboth/base) |
| rung-sel1 | - | 1 | 7 | 29 | 119 | 7 | 925 | base,fof,minsize,no-anch,no-premul,no-st,pfc,unroll4 | `(a{1,3}){65}`  (lowboth/base) |
| forced | - | 0 | 0 | 0 | 0 | 0 | 1460 | pfc | `(x)?a{0,4}\\Gb`  (lowboth/pfc) |
| nullable | - | 2 | 3 | 2 | 3 | 2 | 94 | base,fof,minsize,no-anch,no-premul,no-st,pfc,unroll4 | `^(a{2,4})?$`  (lowboth/pfc) |
| exact | - | 673 | 917 | 673 | 829 | 914 | 32757 | base,dfa,fof,minsize,no-anch,no-pf,no-pfc,no-premul,no-st,pf,pfc,unroll4 | `[^c]{1,3}\\z`  (lowboth/base) |
| no-rep | - | 2876 | 3069 | 2921 | 3014 | 2876 | 135344 | base,dfa,fof,minsize,no-anch,no-pf,no-pfc,no-premul,no-st,pf,pfc,unroll4 | `a(b\|c)+d`  (lowboth/base) |

## T4

| row | cell | plain | lowsize | lowdfa | lowboth | lowthr | all arms | arms | witness |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| option | - | 0 | 0 | 0 | 0 | 0 | 10570 | unroll4 | `a(b\|c)+d`  (lowboth/unroll4) |
| denied | - | 0 | 0 | 0 | 0 | 0 | 10521 | no-st | `a(b\|c)+d`  (lowboth/no-st) |
| default | - | 2102 | 2037 | 2169 | 2099 | 2061 | 96520 | base,fof,minsize,no-anch,no-pf,no-pfc,no-premul,pf,pfc,vm | `a(b\|c)+d`  (lowboth/base) |
| cap-rescue | - | 0 | 14 | 0 | 21 | 0 | 245 | base,no-anch,no-pf,no-pfc,no-premul,pf,pfc,vm | `(?:a\\K){0,10}ab`  (lowboth/base) |
| size-model | - | 2 | 14 | 2 | 16 | 16 | 465 | base,fof,minsize,no-anch,no-pf,no-pfc,no-premul,pf,pfc,vm | `(1{0,30}?[^]abc][^abc]){28,30}0+\|a`  (lowboth/base) |
| capacity-declined | - | 0 | 0 | 0 | 0 | 1 | 2 | base,vm | `(((?:a{0,2}b)+c){0,20}d){0,20}e` witness:capw (lowthr/base) |
| size-model-declined | - | 0 | 2 | 0 | 2 | 27 | 81 | base,fof,no-anch,no-pf,no-pfc,no-premul,pf,pfc,vm | `(?:a\\K){0,10}b`  (lowboth/base) |

