## variant `plain` — 4792 cases, 4350 compiled, 442 refused

### (ENGINE, ENGINE_SEL, UNROLL_K_WHY, VM_PREFILTER, VM_PREFILTER_WHY, VM_PREFILTER_LANG_WHY), compiled cases

| tuple | n |
|---|---:|
| dfa / selected / - / - / - / - | 2247 |
| vm / selected / default / hybrid / - / no counted repeat | 1008 |
| vm / selected / default / none / - / - | 497 |
| vm / selected / default / hybrid / - / exact | 243 |
| vm / forced / default / none / - / - | 220 |
| vm / declined-nullable-default / default / none / - / - | 114 |
| dfa / size-cap-retry / - / - / - / - | 15 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 1899 | 1 |
| vm / declined-nullable / default / none / - / - | 1 |
| vm / declined-nullable-default / size-model / none / - / - | 1 |
| vm / forced / size-model / none / - / - | 1 |
| vm / overflowed-dfa / default / none / - / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 1028352 > 1000000 / - | 1 |

### ENGINE_SEL alone

| (ENGINE, ENGINE_SEL) | n |
|---|---:|
| ('dfa', 'selected') | 2247 |
| ('vm', 'selected') | 1748 |
| ('vm', 'forced') | 221 |
| ('vm', 'declined-nullable-default') | 115 |
| ('dfa', 'size-cap-retry') | 15 |
| ('vm', 'collapsed-prefilter') | 1 |
| ('vm', 'declined-nullable') | 1 |
| ('vm', 'overflowed-dfa') | 1 |
| ('vm', 'size-cap-retry') | 1 |

### attempts per compile (all cases; 'refused' includes parse errors)

| (status, attempts) | n |
|---|---:|
| ('ok', 1) | 4329 |
| ('refused', 1) | 442 |
| ('ok', 2) | 17 |
| ('ok', 3) | 2 |
| ('ok', 7) | 2 |

### attempt-creating transitions, multi-attempt compiles (signature -> final ENGINE_SEL / status)

| transitions / status / final ENGINE_SEL | n |
|---|---:|
| ('drop-anchored', 'ok', 'size-cap-retry') | 15 |
| ('prefilter-collapse > drop-prefilter', 'ok', 'size-cap-retry') | 1 |
| ('sel1:collapse > sel1:drop', 'ok', 'overflowed-dfa') | 1 |
| ('sel1:collapse', 'ok', 'collapsed-prefilter') | 1 |
| ('sel1:collapse', 'ok', 'declined-nullable') | 1 |
| ('size-term-trial-or-other-fail > size-term-trial-or-other-fail > size-term-trial-or-other-fail', 'ok', 'forced') | 1 |

### size-cap collapse rung: fate of the attempt it bought (§4.1)

| fate / compile status | n |
|---|---:|
| ('next-refused:pcoll=0', 'ok') | 1 |

### [SEL-1] collapse retry: fate of the attempt it bought

| fate | n |
|---|---:|
| next-failed:ovf=1 scr=0 pcoll=0 pf=1 chosen=2 | 1 |
| next-ok:collapsed-prefilter | 1 |
| next-ok:declined-nullable | 1 |

total attempts 4825 over 4792 compiles; attempts beyond the first: 33

## variant `lowsize` — 4792 cases, 4266 compiled, 526 refused

### (ENGINE, ENGINE_SEL, UNROLL_K_WHY, VM_PREFILTER, VM_PREFILTER_WHY, VM_PREFILTER_LANG_WHY), compiled cases

| tuple | n |
|---|---:|
| dfa / selected / - / - / - / - | 2164 |
| vm / selected / default / hybrid / - / no counted repeat | 966 |
| vm / selected / default / none / - / - | 485 |
| vm / forced / default / none / - / - | 214 |
| vm / selected / default / hybrid / - / exact | 163 |
| vm / declined-nullable-default / default / none / - / - | 110 |
| dfa / size-cap-retry / - / - / - / - | 51 |
| vm / selected / cap-rescue / hybrid / - / exact | 14 |
| vm / selected / size-model / hybrid / - / exact | 12 |
| vm / selected / size-model-declined / hybrid / - / exact | 2 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30486 > 30000 / - | 2 |
| vm / collapsed-prefilter / size-model / hybrid / - / dfa overflow retry, exact nfa 1899 | 1 |
| vm / declined-nullable / default / none / - / - | 1 |
| vm / forced / size-model / none / - / - | 1 |
| vm / overflowed-dfa / default / none / - / - | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 30501 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 30614 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 30828 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 30842 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 31108 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 31110 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 31358 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 31549 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 31551 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 469076 > 60000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 60825 > 60000 | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 1028349 > 60000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30043 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30045 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30051 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30052 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30058 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30106 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30142 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30176 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30177 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30203 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30240 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30251 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30252 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30270 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30272 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30299 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30326 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30357 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30364 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30378 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30417 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30433 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30440 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30441 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30448 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30490 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30556 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30580 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30626 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30678 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30746 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30753 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30761 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30782 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30798 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30802 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31054 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31069 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31080 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31243 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31429 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31431 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31464 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31624 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31735 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31745 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31756 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31769 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31771 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31796 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31816 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31819 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31870 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31903 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31930 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 32078 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 32189 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 32335 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 32642 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 32714 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 32977 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 33719 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 34013 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 34218 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 778057 > 60000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 778923 > 60000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 782935 > 60000 / - | 1 |

### ENGINE_SEL alone

| (ENGINE, ENGINE_SEL) | n |
|---|---:|
| ('dfa', 'selected') | 2164 |
| ('vm', 'selected') | 1642 |
| ('vm', 'forced') | 215 |
| ('vm', 'declined-nullable-default') | 110 |
| ('vm', 'size-cap-retry') | 81 |
| ('dfa', 'size-cap-retry') | 51 |
| ('vm', 'collapsed-prefilter') | 1 |
| ('vm', 'declined-nullable') | 1 |
| ('vm', 'overflowed-dfa') | 1 |

### attempts per compile (all cases; 'refused' includes parse errors)

| (status, attempts) | n |
|---|---:|
| ('ok', 1) | 4102 |
| ('refused', 1) | 463 |
| ('ok', 3) | 96 |
| ('refused', 3) | 49 |
| ('ok', 2) | 38 |
| ('ok', 7) | 29 |
| ('refused', 9) | 11 |
| ('refused', 7) | 2 |
| ('ok', 8) | 1 |
| ('refused', 2) | 1 |

### attempt-creating transitions, multi-attempt compiles (signature -> final ENGINE_SEL / status)

| transitions / status / final ENGINE_SEL | n |
|---|---:|
| ('prefilter-collapse > drop-prefilter', 'ok', 'size-cap-retry') | 70 |
| ('drop-anchored > drop-premul', 'refused', '-') | 46 |
| ('drop-anchored', 'ok', 'size-cap-retry') | 26 |
| ('drop-anchored > drop-premul', 'ok', 'size-cap-retry') | 25 |
| ('prefilter-collapse > drop-prefilter', 'refused', '-') | 11 |
| ('prefilter-collapse', 'ok', 'size-cap-retry') | 11 |
| ('size-term-trial-or-other-fail > size-term-trial-or-other-fail > size-term-trial-or-other-fail > size-term-trial-or-other-fail > size-term-trial-or-other-fail > prefilter-collapse > drop-prefilter', 'refused', '-') | 3 |
| ('drop-premul', 'refused', '-') | 1 |
| ('sel1:collapse > sel1:drop', 'ok', 'overflowed-dfa') | 1 |
| ('sel1:collapse', 'ok', 'collapsed-prefilter') | 1 |
| ('sel1:collapse', 'ok', 'declined-nullable') | 1 |
| ('size-term-trial-or-other-fail > size-term-trial-or-other-fail > size-term-trial-or-other-fail > size-term-trial-or-other-fail', 'ok', 'forced') | 1 |
| ('size-term-trial-or-other-fail > size-term-trial-or-other-fail', 'refused', '-') | 1 |

### size-cap collapse rung: fate of the attempt it bought (§4.1)

| fate / compile status | n |
|---|---:|
| ('next-refused:pcoll=0', 'ok') | 43 |
| ('next-refused:pcoll=1', 'ok') | 27 |
| ('next-refused:pcoll=1', 'refused') | 14 |
| ('next-ok:count-collapsed', 'ok') | 11 |

### [SEL-1] collapse retry: fate of the attempt it bought

| fate | n |
|---|---:|
| next-failed:ovf=1 scr=0 pcoll=0 pf=1 chosen=2 | 1 |
| next-ok:collapsed-prefilter | 1 |
| next-ok:declined-nullable | 1 |

total attempts 5402 over 4792 compiles; attempts beyond the first: 610

## variant `lowdfa` — 4792 cases, 4350 compiled, 442 refused

### (ENGINE, ENGINE_SEL, UNROLL_K_WHY, VM_PREFILTER, VM_PREFILTER_WHY, VM_PREFILTER_LANG_WHY), compiled cases

| tuple | n |
|---|---:|
| dfa / selected / - / - / - / - | 2197 |
| vm / selected / default / hybrid / - / no counted repeat | 1005 |
| vm / selected / default / none / - / - | 497 |
| vm / selected / default / hybrid / - / exact | 227 |
| vm / forced / default / none / - / - | 220 |
| vm / declined-nullable-default / default / none / - / - | 114 |
| vm / overflowed-dfa / default / none / - / - | 60 |
| vm / overflowed-prefilter / default / none / - / - | 4 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 802 | 2 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 1002 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 10238 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 1592 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 16003 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 1899 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 20003 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 2051 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 24003 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 2503 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 315 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 386 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 387 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 392 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 398 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 4001 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 502 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 503 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 511 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 54 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 55 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 602 | 1 |
| vm / declined-nullable / default / none / - / - | 1 |
| vm / declined-nullable-default / size-model / none / - / - | 1 |
| vm / forced / size-model / none / - / - | 1 |

### ENGINE_SEL alone

| (ENGINE, ENGINE_SEL) | n |
|---|---:|
| ('dfa', 'selected') | 2197 |
| ('vm', 'selected') | 1729 |
| ('vm', 'forced') | 221 |
| ('vm', 'declined-nullable-default') | 115 |
| ('vm', 'overflowed-dfa') | 60 |
| ('vm', 'collapsed-prefilter') | 23 |
| ('vm', 'overflowed-prefilter') | 4 |
| ('vm', 'declined-nullable') | 1 |

### attempts per compile (all cases; 'refused' includes parse errors)

| (status, attempts) | n |
|---|---:|
| ('ok', 1) | 4260 |
| ('refused', 1) | 442 |
| ('ok', 3) | 64 |
| ('ok', 2) | 24 |
| ('ok', 7) | 2 |

### attempt-creating transitions, multi-attempt compiles (signature -> final ENGINE_SEL / status)

| transitions / status / final ENGINE_SEL | n |
|---|---:|
| ('sel1:collapse > sel1:drop', 'ok', 'overflowed-dfa') | 60 |
| ('sel1:collapse', 'ok', 'collapsed-prefilter') | 23 |
| ('sel1:collapse > sel1:drop', 'ok', 'overflowed-prefilter') | 4 |
| ('sel1:collapse', 'ok', 'declined-nullable') | 1 |
| ('size-term-trial-or-other-fail > size-term-trial-or-other-fail > size-term-trial-or-other-fail', 'ok', 'forced') | 1 |

### size-cap collapse rung: fate of the attempt it bought (§4.1)

(rung never taken)

### [SEL-1] collapse retry: fate of the attempt it bought

| fate | n |
|---|---:|
| next-failed:ovf=1 scr=0 pcoll=0 pf=1 chosen=2 | 60 |
| next-ok:collapsed-prefilter | 23 |
| next-failed:ovf=1 scr=0 pcoll=1 pf=1 chosen=2 | 4 |
| next-ok:declined-nullable | 1 |

total attempts 4956 over 4792 compiles; attempts beyond the first: 164

## variant `lowboth` — 4792 cases, 4313 compiled, 479 refused

### (ENGINE, ENGINE_SEL, UNROLL_K_WHY, VM_PREFILTER, VM_PREFILTER_WHY, VM_PREFILTER_LANG_WHY), compiled cases

| tuple | n |
|---|---:|
| dfa / selected / - / - / - / - | 2158 |
| vm / selected / default / hybrid / - / no counted repeat | 966 |
| vm / selected / default / none / - / - | 485 |
| vm / forced / default / none / - / - | 214 |
| vm / selected / default / hybrid / - / exact | 162 |
| vm / declined-nullable-default / default / none / - / - | 110 |
| vm / overflowed-dfa / default / none / - / - | 56 |
| dfa / size-cap-retry / - / - / - / - | 35 |
| vm / selected / cap-rescue / hybrid / - / exact | 12 |
| vm / selected / size-model / hybrid / - / exact | 11 |
| vm / overflowed-prefilter / default / none / - / - | 4 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 802 | 2 |
| vm / selected / size-model-declined / hybrid / - / exact | 2 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30486 > 30000 / - | 2 |
| vm / collapsed-prefilter / cap-rescue / hybrid / - / dfa overflow retry, exact nfa 16003 | 1 |
| vm / collapsed-prefilter / cap-rescue / hybrid / - / dfa overflow retry, exact nfa 20003 | 1 |
| vm / collapsed-prefilter / cap-rescue / hybrid / - / dfa overflow retry, exact nfa 315 | 1 |
| vm / collapsed-prefilter / cap-rescue / hybrid / - / dfa overflow retry, exact nfa 386 | 1 |
| vm / collapsed-prefilter / cap-rescue / hybrid / - / dfa overflow retry, exact nfa 392 | 1 |
| vm / collapsed-prefilter / cap-rescue / hybrid / - / dfa overflow retry, exact nfa 398 | 1 |
| vm / collapsed-prefilter / cap-rescue / hybrid / - / dfa overflow retry, exact nfa 511 | 1 |
| vm / collapsed-prefilter / cap-rescue / hybrid / - / dfa overflow retry, exact nfa 54 | 1 |
| vm / collapsed-prefilter / cap-rescue / hybrid / - / dfa overflow retry, exact nfa 55 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 1002 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 24003 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 387 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 4001 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 502 | 1 |
| vm / collapsed-prefilter / default / hybrid / - / dfa overflow retry, exact nfa 602 | 1 |
| vm / collapsed-prefilter / size-model / hybrid / - / dfa overflow retry, exact nfa 10238 | 1 |
| vm / collapsed-prefilter / size-model / hybrid / - / dfa overflow retry, exact nfa 1899 | 1 |
| vm / collapsed-prefilter / size-model / hybrid / - / dfa overflow retry, exact nfa 2503 | 1 |
| vm / collapsed-prefilter / size-model / hybrid / - / dfa overflow retry, exact nfa 503 | 1 |
| vm / declined-nullable / default / none / - / - | 1 |
| vm / forced / size-model / none / - / - | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 30501 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 30614 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 30828 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 30842 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 31108 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 31110 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 31358 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 31549 > 30000 | 1 |
| vm / size-cap-retry / default / hybrid / - / size cap retry, exact 31551 > 30000 | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30043 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30045 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30051 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30052 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30058 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30106 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30142 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30176 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30177 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30203 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30240 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30251 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30252 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30270 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30272 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30299 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30326 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30357 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30364 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30378 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30417 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30433 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30440 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30441 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30448 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30490 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30556 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30580 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30626 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30678 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30746 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30753 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30761 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30782 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30798 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 30802 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31054 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31069 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31080 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31243 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31429 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31431 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31464 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31624 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31735 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31745 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31756 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31769 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31771 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31796 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31816 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31819 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31870 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31903 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 31930 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 32078 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 32189 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 32335 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 32642 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 32714 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 32977 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 33719 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 34013 > 30000 / - | 1 |
| vm / size-cap-retry / default / none / size cap retry, hybrid 34218 > 30000 / - | 1 |

### ENGINE_SEL alone

| (ENGINE, ENGINE_SEL) | n |
|---|---:|
| ('dfa', 'selected') | 2158 |
| ('vm', 'selected') | 1638 |
| ('vm', 'forced') | 215 |
| ('vm', 'declined-nullable-default') | 110 |
| ('vm', 'size-cap-retry') | 75 |
| ('vm', 'overflowed-dfa') | 56 |
| ('dfa', 'size-cap-retry') | 35 |
| ('vm', 'collapsed-prefilter') | 21 |
| ('vm', 'overflowed-prefilter') | 4 |
| ('vm', 'declined-nullable') | 1 |

### attempts per compile (all cases; 'refused' includes parse errors)

| (status, attempts) | n |
|---|---:|
| ('ok', 1) | 4095 |
| ('refused', 1) | 463 |
| ('ok', 3) | 135 |
| ('ok', 2) | 44 |
| ('ok', 7) | 26 |
| ('ok', 8) | 13 |
| ('refused', 3) | 10 |
| ('refused', 7) | 2 |
| ('refused', 8) | 2 |
| ('refused', 2) | 1 |
| ('refused', 9) | 1 |

### attempt-creating transitions, multi-attempt compiles (signature -> final ENGINE_SEL / status)

| transitions / status / final ENGINE_SEL | n |
|---|---:|
| ('prefilter-collapse > drop-prefilter', 'ok', 'size-cap-retry') | 66 |
| ('sel1:collapse > sel1:drop', 'ok', 'overflowed-dfa') | 56 |
| ('drop-anchored', 'ok', 'size-cap-retry') | 26 |
| ('sel1:collapse', 'ok', 'collapsed-prefilter') | 21 |
| ('drop-anchored > drop-premul', 'ok', 'size-cap-retry') | 9 |
| ('prefilter-collapse', 'ok', 'size-cap-retry') | 9 |
| ('prefilter-collapse > drop-prefilter', 'refused', '-') | 4 |
| ('sel1:collapse > sel1:drop', 'ok', 'overflowed-prefilter') | 4 |
| ('sel1:collapse > sel1:drop', 'refused', '-') | 4 |
| ('drop-anchored > drop-premul', 'refused', '-') | 3 |
| ('sel1:collapse', 'refused', '-') | 2 |
| ('drop-premul', 'refused', '-') | 1 |
| ('sel1:collapse', 'ok', 'declined-nullable') | 1 |
| ('size-term-trial-or-other-fail > size-term-trial-or-other-fail > size-term-trial-or-other-fail > size-term-trial-or-other-fail', 'ok', 'forced') | 1 |
| ('size-term-trial-or-other-fail > size-term-trial-or-other-fail', 'refused', '-') | 1 |

### size-cap collapse rung: fate of the attempt it bought (§4.1)

| fate / compile status | n |
|---|---:|
| ('next-refused:pcoll=0', 'ok') | 39 |
| ('next-refused:pcoll=1', 'ok') | 27 |
| ('next-ok:count-collapsed', 'ok') | 9 |
| ('next-refused:pcoll=1', 'refused') | 4 |

### [SEL-1] collapse retry: fate of the attempt it bought

| fate | n |
|---|---:|
| next-failed:ovf=1 scr=0 pcoll=0 pf=1 chosen=2 | 60 |
| next-ok:collapsed-prefilter | 21 |
| next-failed:ovf=1 scr=0 pcoll=1 pf=1 chosen=2 | 4 |
| next-failed:ovf=0 scr=1 pcoll=1 pf=1 chosen=2 | 2 |
| next-ok:declined-nullable | 1 |

total attempts 5408 over 4792 compiles; attempts beyond the first: 616

