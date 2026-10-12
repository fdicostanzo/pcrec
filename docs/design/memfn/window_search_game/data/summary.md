
### A. What the contract can express (per set)

| set | patterns | unparsed | anchored ^ | no span | no bounded span | bounded inner span | inner ov>0 | >=2 bounded spans | has unbounded span | rarest POSITION is in an unbounded span | rarest SPAN (joint) is unbounded |
|---|---|---|---|---|---|---|---|---|---|---|---|
| capability | 71 | 1 | 19 | 2 | 2 | 5 | 5 | 2 | 19 | 11 | 12 |
| loglines | 11 | 0 | 0 | 0 | 0 | 4 | 4 | 4 | 3 | 2 | 1 |
| syntax | 95 | 12 | 3 | 0 | 2 | 6 | 6 | 4 | 20 | 12 | 13 |
| corpus | 150 | 23 | 20 | 19 | 9 | 16 | 16 | 8 | 25 | 15 | 14 |

### A2. Loss notes (patterns carrying each)

| note | capability | loglines | syntax | corpus |
|---|---|---|---|---|
| alt-dropped | 27 | 7 | 6 | 24 |
| anchor-line | 0 | 0 | 1 | 0 |
| assertion | 34 | 7 | 6 | 50 |
| backref | 6 | 0 | 5 | 16 |
| conditional | 0 | 0 | 1 | 0 |
| gstart | 0 | 0 | 1 | 1 |
| kreset | 0 | 0 | 1 | 5 |
| lookaround | 13 | 0 | 4 | 13 |
| recursion | 2 | 0 | 7 | 17 |
| rep-right | 5 | 3 | 1 | 11 |
| verb | 0 | 0 | 3 | 0 |

### A3. Control: extractor prefix classes vs pcrec's k-set walk sizes

166 patterns with a fixed prefix span; 582 positions agree, 0 differ (0 patterns).

### B. Which span each policy picks (patterns with >=1 bounded span, unanchored)

| set | patterns | P2 same span as P1 | P3 | P4 | P5-dfa | P5-vm | declines | picks an INNER span (mb>0) |
|---|---|---|---|---|---|---|---|---|
| capability | 51 | 51 | 51 | 46 | 38 | 45 | P4selfprice:5 P5dfa:13 P5vm:5 | P1:4 P2:4 P3:4 P4:4 P5:0 P5:3 |
| loglines | 11 | 11 | 11 | 10 | 10 | 11 | P4selfprice:1 P5dfa:1 | P1:2 P2:2 P3:2 P4:2 P5:2 P5:2 |
| syntax | 80 | 80 | 80 | 72 | 71 | 72 | P4selfprice:8 P5dfa:9 P5vm:8 | P1:4 P2:4 P3:4 P4:4 P5:4 P5:4 |
| corpus | 107 | 107 | 107 | 96 | 89 | 96 | P4selfprice:11 P5dfa:18 P5vm:10 | P1:14 P2:14 P3:14 P4:14 P5:14 P5:13 |

### B2. Span flips between the consumer-blind and consumer-priced policies

{'P4!=P5-dfa': 16, 'P5-dfa!=P5-vm': 19, 'P4!=P5-vm': 4}
- `capability/currency-lookbehind-fixed`: P4 `one#0{\d}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\d}@a=0,mb=0,ov=0`
- `capability/float-literal-bound`: P4 `one#0{\d}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\d}@a=0,mb=0,ov=0`
- `capability/tail-digits-eol`: P4 `one#0{\d}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\d}@a=0,mb=0,ov=0`
- `capability/tail-space-eol`: P4 `one#0{\s}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\s}@a=0,mb=0,ov=0`
- `capability/wild-codegrammar-json-number-extended`: P4 `one#0{\d}@a=0,mb=1,ov=1` / P5-dfa `decline` / P5-vm `one#0{\d}@a=0,mb=1,ov=1`
- `capability/wild-logparse-base10num-grok`: P4 `one#0{[11]}@a=0,mb=1,ov=1` / P5-dfa `decline` / P5-vm `one#0{[11]}@a=0,mb=1,ov=1`
- `capability/wild-logparse-base10num-noatomic`: P4 `one#0{[11]}@a=0,mb=1,ov=1` / P5-dfa `decline` / P5-vm `one#0{[11]}@a=0,mb=1,ov=1`
- `capability/wild-logparse-syslogbase-expanded`: P4 `one#1{\x20}@a=0,mb=9,ov=7` / P5-dfa `decline` / P5-vm `one#0{[16]}@a=0,mb=0,ov=0`
- `loglines/ipv6`: P4 `decline` / P5-dfa `decline` / P5-vm `one#0{[16]}@a=0,mb=0,ov=0`
- `syntax/cls-d`: P4 `one#0{\d}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\d}@a=0,mb=0,ov=0`
- `corpus/c021`: P4 `one#0{[2]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[2]}@a=0,mb=0,ov=0`
- `corpus/c031`: P4 `one#0{[2]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[2]}@a=0,mb=0,ov=0`
- `corpus/c043`: P4 `one#0{[2]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[2]}@a=0,mb=0,ov=0`
- `corpus/c094`: P4 `one#0{[3]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[3]}@a=0,mb=0,ov=0`
- `corpus/c101`: P4 `one#0{[2]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[2]}@a=0,mb=0,ov=0`
- `corpus/c129`: P4 `one#0{[3]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[3]}@a=0,mb=0,ov=0`
- `corpus/c130`: P4 `decline` / P5-dfa `decline` / P5-vm `one#0{[146]}@a=0,mb=0,ov=0`
- `corpus/c134`: P4 `one#1{a}@a=0,mb=3,ov=2` / P5-dfa `one#1{a}@a=0,mb=3,ov=2` / P5-vm `one#0{[2]}@a=0,mb=0,ov=0`
- `corpus/c148`: P4 `one#0{[2]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[2]}@a=0,mb=0,ov=0`

### C. Counted consequences on the throughput subjects (sum over the common population)

| subject | set | pop | policy | with form | stops | survivors | window bytes | VM starts | work(dfa) | work(vm) |
|---|---|---|---|---|---|---|---|---|---|---|
| capability__t-256k | capability | 46 | P1-rare-pos | 46 | 1457020 | 1220396 | 1641309 | 1537873 | 4.42e+07 | 1.59e+08 |
| capability__t-256k | capability | 46 | P2-rare-span | 46 | 1457020 | 1220396 | 1641309 | 1537873 | 4.42e+07 | 1.59e+08 |
| capability__t-256k | capability | 46 | P3-pair | 46 | 1277563 | 1220396 | 1641309 | 1537873 | 4.36e+07 | 1.59e+08 |
| capability__t-256k | capability | 46 | P4-selfprice | 46 | 1662208 | 1603150 | 2024063 | 1920627 | 1.42e+07 | 1.33e+08 |
| capability__t-256k | capability | 46 | P5-dfa | 46 | 3493516 | 3434458 | 3476630 | 3434458 | 6.34e+06 | 2.09e+08 |
| capability__t-256k | capability | 46 | P5-vm | 46 | 1690448 | 1631390 | 1776601 | 1734429 | 1.49e+07 | 1.24e+08 |
| capability__t-256k | capability | 46 | P5-dfa-subjprior | 46 | 3492777 | 3434458 | 3476630 | 3434458 | 6.34e+06 | 2.09e+08 |
| capability__t-256k | capability | 46 | SHIPPED | 46 | 2391704 | 2359644 | 2361667 | 2359644 | 3.72e+07 | 1.97e+08 |
| capability__t-256k | corpus | 77 | P1-rare-pos | 77 | 2719287 | 2600216 | 2724628 | 2701765 | 8.51e+07 | 2.96e+08 |
| capability__t-256k | corpus | 77 | P2-rare-span | 77 | 2719287 | 2600216 | 2724628 | 2701765 | 8.51e+07 | 2.96e+08 |
| capability__t-256k | corpus | 77 | P3-pair | 77 | 2603591 | 2600216 | 2724628 | 2701765 | 8.41e+07 | 2.95e+08 |
| capability__t-256k | corpus | 77 | P4-selfprice | 77 | 3135203 | 3120190 | 3244602 | 3221739 | 1.17e+07 | 2.07e+08 |
| capability__t-256k | corpus | 77 | P5-dfa | 77 | 4884934 | 4869921 | 4994333 | 4971470 | 1.08e+07 | 3.07e+08 |
| capability__t-256k | corpus | 77 | P5-vm | 77 | 2986219 | 2971206 | 3066797 | 3053541 | 1.51e+07 | 2.02e+08 |
| capability__t-256k | corpus | 77 | P5-dfa-subjprior | 77 | 3370346 | 3365837 | 3490249 | 3467386 | 1.14e+07 | 2.2e+08 |
| capability__t-256k | corpus | 77 | SHIPPED | 77 | 4095635 | 4019698 | 4028949 | 4025807 | 7.29e+07 | 3.54e+08 |
| loglines__t-256k-fail | loglines | 11 | P1-rare-pos | 11 | 340920 | 130685 | 143099 | 138931 | 6.79e+06 | 1.76e+07 |
| loglines__t-256k-fail | loglines | 11 | P2-rare-span | 11 | 340920 | 130685 | 143099 | 138931 | 6.79e+06 | 1.76e+07 |
| loglines__t-256k-fail | loglines | 11 | P3-pair | 11 | 232935 | 130685 | 143099 | 138931 | 6.13e+06 | 1.69e+07 |
| loglines__t-256k-fail | loglines | 11 | P4-selfprice | 11 | 379500 | 275861 | 288275 | 284107 | 2.23e+06 | 1.93e+07 |
| loglines__t-256k-fail | loglines | 11 | P5-dfa | 11 | 379500 | 275861 | 288275 | 284107 | 2.23e+06 | 1.93e+07 |
| loglines__t-256k-fail | loglines | 11 | P5-vm | 11 | 234324 | 130685 | 143099 | 138931 | 5.78e+06 | 1.66e+07 |
| loglines__t-256k-fail | loglines | 11 | P5-dfa-subjprior | 11 | 582059 | 538030 | 550444 | 546276 | 1.7e+06 | 3.42e+07 |
| loglines__t-256k-fail | loglines | 11 | SHIPPED | 11 | 230219 | 215054 | 274107 | 268808 | 7.32e+06 | 2.75e+07 |
| loglines__t-256k-hit | loglines | 11 | P1-rare-pos | 11 | 335019 | 128199 | 151011 | 139275 | 6.69e+06 | 1.75e+07 |
| loglines__t-256k-hit | loglines | 11 | P2-rare-span | 11 | 335019 | 128199 | 151011 | 139275 | 6.69e+06 | 1.75e+07 |
| loglines__t-256k-hit | loglines | 11 | P3-pair | 11 | 226849 | 128199 | 151011 | 139275 | 6.03e+06 | 1.68e+07 |
| loglines__t-256k-hit | loglines | 11 | P4-selfprice | 11 | 378838 | 276391 | 299203 | 287467 | 2.24e+06 | 1.95e+07 |
| loglines__t-256k-hit | loglines | 11 | P5-dfa | 11 | 378838 | 276391 | 299203 | 287467 | 2.24e+06 | 1.95e+07 |
| loglines__t-256k-hit | loglines | 11 | P5-vm | 11 | 230646 | 128199 | 151011 | 139275 | 5.7e+06 | 1.65e+07 |
| loglines__t-256k-hit | loglines | 11 | P5-dfa-subjprior | 11 | 582643 | 538577 | 559901 | 549653 | 1.73e+06 | 3.44e+07 |
| loglines__t-256k-hit | loglines | 11 | SHIPPED | 11 | 229181 | 211993 | 278161 | 269466 | 7.26e+06 | 2.74e+07 |
| syntax__t-256k | syntax | 68 | P1-rare-pos | 68 | 2089354 | 1751232 | 2051412 | 1779912 | 6.08e+07 | 2.01e+08 |
| syntax__t-256k | syntax | 68 | P2-rare-span | 68 | 2089354 | 1751232 | 2051412 | 1779912 | 6.08e+07 | 2.01e+08 |
| syntax__t-256k | syntax | 68 | P3-pair | 68 | 1762947 | 1751232 | 2051412 | 1779912 | 5.81e+07 | 1.98e+08 |
| syntax__t-256k | syntax | 68 | P4-selfprice | 68 | 2316356 | 2298867 | 2450808 | 2327547 | 1.02e+07 | 1.51e+08 |
| syntax__t-256k | syntax | 68 | P5-dfa | 68 | 2560707 | 2543218 | 2695159 | 2571898 | 9.72e+06 | 1.65e+08 |
| syntax__t-256k | syntax | 68 | P5-vm | 68 | 2316356 | 2298867 | 2450808 | 2327547 | 1.02e+07 | 1.51e+08 |
| syntax__t-256k | syntax | 68 | P5-dfa-subjprior | 68 | 3770991 | 3762053 | 3895617 | 3772356 | 8.06e+06 | 2.32e+08 |
| syntax__t-256k | syntax | 68 | SHIPPED | 68 | 2875277 | 2666120 | 2723871 | 2670284 | 6.39e+07 | 2.59e+08 |

### D. Span vs span: does the ranking flip once the window is priced?

pattern x subject cells with >=2 bounded spans: 22
| ranking compared | argmin span differs |
|---|---|
| prior-vs-measured stops | 1 |
| scan-only vs dfa-priced | 0 |
| scan-only vs vm-priced | 3 |
| dfa vs vm | 3 |

measured/predicted survivors (+1 smoothed), 329 forms: p10 0.136, p50 1.63, p90 240, max 469

### D2. Similar stop counts (<=2x), very different windows (width >=3x or overshoot gap >=4)

10 form pairs
| cell | form A (stops, survivors, window bytes) | form B | work dfa A/B | work vm A/B |
|---|---|---|---|---|
| capability/wild-logparse-syslogbase-expanded t-256k | one#0{[16]}@a=0,mb=0,ov=0 s=58874 v=58874 wb=58874 | one#1{\x20}@a=0,mb=9,ov=7 s=30634 v=30634 wb=306336 | 2008595 / 1233220 | 6659641 / 16243884 |
| capability/wild-secrets-slack-webhook-url t-256k | one#0{[2][2][2][2][2]://[2][2][2][2][2].[2][2][2][2][2].[2][2][2]/[2][2][2][2][2][2][2][2]/[2]\w\w\w\w\w\w\w\w/[2]\w\w\w\w\w\w\w\w}@a=6,mb=0,ov=0 s=7379 v=0 wb=0 | one#1{/\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w}@a=0,mb=56,ov=4 s=7380 v=0 wb=0 | 81654 / 81664 | 81654 / 81664 |
| loglines/ipv4 t-256k-fail | one#0{\d\x2e}@a=1,mb=2,ov=2 s=5166 v=4123 wb=16492 | one#2{\d\x2e}@a=1,mb=10,ov=6 s=5166 v=4123 wb=49476 | 158477 / 191461 | 966585 / 1956105 |
| loglines/ipv4 t-256k-fail | pair#0{\d\x2e}@a=0,1,mb=2,ov=2 s=4123 v=4123 wb=16492 | pair#2{\d\x2e}@a=0,1,mb=10,ov=6 s=4123 v=4123 wb=49476 | 331565 / 364549 | 1139673 / 2129193 |
| loglines/ipv4 t-256k-hit | one#0{\d\x2e}@a=1,mb=2,ov=2 s=5863 v=4050 wb=16200 | one#2{\d\x2e}@a=1,mb=10,ov=6 s=5863 v=4050 wb=48597 | 163697 / 196094 | 957497 / 1929497 |
| loglines/ipv4 t-256k-hit | pair#0{\d\x2e}@a=0,1,mb=2,ov=2 s=4050 v=4050 wb=16200 | pair#2{\d\x2e}@a=0,1,mb=10,ov=6 s=4050 v=4050 wb=48597 | 329131 / 361528 | 1122931 / 2094931 |
| corpus/c002 t-256k | one#0{a}@a=0,mb=0,ov=0 s=9607 v=9607 wb=9607 | one#1{c}@a=0,mb=2,ov=1 s=5650 v=5650 wb=16950 | 305681 / 194314 | 1064634 / 968364 |
| corpus/c019 t-256k | one#0{[2]}@a=0,mb=0,ov=0 s=10847 v=10847 wb=10847 | one#1{c}@a=0,mb=3,ov=2 s=5650 v=5650 wb=22600 | 351986 / 199964 | 1208899 / 1307364 |
| corpus/c112 t-256k | one#0{a}@a=0,mb=0,ov=0 s=9607 v=9607 wb=9607 | one#1{a}@a=0,mb=2,ov=1 s=9607 v=9607 wb=28821 | 305681 / 324895 | 1064634 / 1641054 |
| corpus/c134 t-256k | one#0{[2]}@a=0,mb=0,ov=0 s=10323 v=10323 wb=10323 | one#1{a}@a=0,mb=3,ov=2 s=9607 v=9607 wb=38428 | 335742 / 334502 | 1151259 / 2217474 |

### E0. Control: relative distance from (move-back, overshoot, length) vs a direct walk of the items

152 span pairs (earlier span bounded): 152 agree, 0 differ.

### E1. What P6 picks

| population | policy | plan (A via B) | single-span form | decline | no bounded span |
|---|---|---|---|---|---|
| 327 patterns | P6-dfa | 9 | 165 | 41 | 34 |
| 327 patterns | P6-vm | 10 | 182 | 23 | 34 |
| witnesses | P6-dfa | 5 | 2 | 4 | 0 |
| witnesses | P6-vm | 5 | 6 | 0 | 0 |

### E2. Cells where P6 chose a plan: P6 against P5 (same consumer) and SHIPPED (work; one DFA step = 1)

| pattern (spans) | subject | cons | B stops | A windows | work P6 | work P5 | P5/P6 | work SHIPPED |
|---|---|---|---|---|---|---|---|---|
| capability/wild-logparse-syslogbase-expanded `[16]@mb=0,ov=0 \x20@mb=9,ov=7 \d@mb=inf,ov=i` | cap | vm | 30634 | 42798 | 4.77e+06 | 6.66e+06 | 1.40 | 6.66e+06 |
| corpus/c002 `a@mb=0,ov=0 c@mb=2,ov=1` | cap | dfa | 5650 | 1112 | 8.81e+04 | 1.94e+05 | 2.21 | 3.06e+05 |
| corpus/c002 `a@mb=0,ov=0 c@mb=2,ov=1` | cap | vm | 5650 | 1112 | 1.76e+05 | 9.68e+05 | 5.51 | 1.06e+06 |
| corpus/c019 `[2]@mb=0,ov=0 c@mb=3,ov=2` | cap | dfa | 5650 | 1320 | 9.31e+04 | 2e+05 | 2.15 | 3.52e+05 |
| corpus/c019 `[2]@mb=0,ov=0 c@mb=3,ov=2` | cap | vm | 5650 | 1320 | 1.97e+05 | 1.31e+06 | 6.62 | 1.21e+06 |
| corpus/c109 `aa@mb=0,ov=0 bb@mb=3,ov=1` | cap | dfa | 0 | 0 | 1.57e+04 | 1.57e+04 | 1.00 | 2.18e+04 |
| corpus/c109 `aa@mb=0,ov=0 bb@mb=3,ov=1` | cap | vm | 0 | 0 | 1.57e+04 | 1.57e+04 | 1.00 | 2.69e+04 |
| corpus/c112 `a@mb=0,ov=0 a@mb=2,ov=1` | cap | dfa | 9607 | 22 | 1.05e+05 | 3.06e+05 | 2.91 | 2.62e+05 |
| corpus/c112 `a@mb=0,ov=0 a@mb=2,ov=1` | cap | vm | 9607 | 22 | 1.07e+05 | 1.06e+06 | 9.98 | 1.57e+07 |
| corpus/c125 `[2]@mb=0,ov=0 b@mb=2,ov=1` | cap | dfa | 1240 | 12 | 2.07e+04 | 4.88e+04 | 2.36 | 3.36e+05 |
| corpus/c125 `[2]@mb=0,ov=0 b@mb=2,ov=1` | cap | vm | 1240 | 12 | 2.16e+04 | 2.19e+05 | 10.12 | 1.15e+06 |
| corpus/c134 `[2]@mb=0,ov=0 a@mb=3,ov=2` | cap | dfa | 9607 | 235 | 1.11e+05 | 3.35e+05 | 3.02 | 3.36e+05 |
| corpus/c134 `[2]@mb=0,ov=0 a@mb=3,ov=2` | cap | vm | 9607 | 235 | 1.29e+05 | 1.15e+06 | 8.91 | 1.15e+06 |
| syntax/grp-atomic-alt `a@mb=0,ov=0 c@mb=2,ov=1` | syn | dfa | 8221 | 1164 | 1.15e+05 | 2.79e+05 | 2.43 | 5.78e+05 |
| syntax/grp-atomic-alt `a@mb=0,ov=0 c@mb=2,ov=1` | syn | vm | 8221 | 1164 | 2.07e+05 | 1.41e+06 | 6.79 | 2.03e+06 |
| syntax/qnt-poss-brace `a@mb=0,ov=0 b@mb=2,ov=1` | syn | dfa | 2082 | 381 | 3.68e+04 | 7.66e+04 | 2.08 | 7.66e+04 |
| syntax/qnt-poss-brace `a@mb=0,ov=0 b@mb=2,ov=1` | syn | vm | 2082 | 381 | 6.69e+04 | 3.62e+05 | 5.41 | 4.87e+05 |
| syntax/qnt-quest `colo@mb=0,ov=0 r@mb=5,ov=1` | syn | dfa | 926 | 565 | 3.97e+04 | 3.85e+04 | 0.97 | 1.38e+05 |
| syntax/qnt-quest `colo@mb=0,ov=0 r@mb=5,ov=1` | syn | vm | 926 | 565 | 1.15e+05 | 8.15e+04 | 0.71 | 2.1e+05 |
| wit2/w01-bounded-4 `\d\d\d@mb=0,ov=0 #@mb=7,ov=4` | cap | dfa | 746 | 677 | 3.35e+04 | 3.62e+04 | 1.08 | 3.62e+04 |
| wit2/w01-bounded-4 `\d\d\d@mb=0,ov=0 #@mb=7,ov=4` | cap | vm | 746 | 677 | 8.56e+04 | 2.69e+05 | 3.14 | 4.03e+05 |
| wit2/w01-bounded-4 `\d\d\d@mb=0,ov=0 #@mb=7,ov=4` | log-fail | dfa | 492 | 931 | 3.59e+04 | 2.66e+04 | 0.74 | 2.66e+04 |
| wit2/w01-bounded-4 `\d\d\d@mb=0,ov=0 #@mb=7,ov=4` | log-fail | vm | 492 | 931 | 1.08e+05 | 1.8e+05 | 1.67 | 2.69e+05 |
| wit2/w01-bounded-4 `\d\d\d@mb=0,ov=0 #@mb=7,ov=4` | log-hit | dfa | 358 | 680 | 2.83e+04 | 2.15e+04 | 0.76 | 2.15e+04 |
| wit2/w01-bounded-4 `\d\d\d@mb=0,ov=0 #@mb=7,ov=4` | log-hit | vm | 358 | 680 | 8.07e+04 | 1.33e+05 | 1.65 | 1.98e+05 |
| wit2/w01-bounded-4 `\d\d\d@mb=0,ov=0 #@mb=7,ov=4` | syn | dfa | 0 | 0 | 7.86e+03 | 7.86e+03 | 1.00 | 7.86e+03 |
| wit2/w01-bounded-4 `\d\d\d@mb=0,ov=0 #@mb=7,ov=4` | syn | vm | 0 | 0 | 7.86e+03 | 7.86e+03 | 1.00 | 7.86e+03 |
| wit2/w03-bounded-12 `\d\d@mb=0,ov=0 #@mb=16,ov=14` | cap | dfa | 746 | 1420 | 5.44e+04 | 4.29e+04 | 0.79 | 4.29e+04 |
| wit2/w03-bounded-12 `\d\d@mb=0,ov=0 #@mb=16,ov=14` | cap | vm | 746 | 1420 | 1.65e+05 | 7.17e+05 | 4.34 | 8.06e+05 |
| wit2/w03-bounded-12 `\d\d@mb=0,ov=0 #@mb=16,ov=14` | log-fail | dfa | 492 | 1934 | 6.05e+04 | 3.1e+04 | 0.51 | 3.1e+04 |
| wit2/w03-bounded-12 `\d\d@mb=0,ov=0 #@mb=16,ov=14` | log-fail | vm | 492 | 1934 | 2.11e+05 | 4.75e+05 | 2.25 | 5.34e+05 |
| wit2/w03-bounded-12 `\d\d@mb=0,ov=0 #@mb=16,ov=14` | log-hit | dfa | 358 | 1411 | 4.62e+04 | 2.47e+04 | 0.53 | 2.47e+04 |
| wit2/w03-bounded-12 `\d\d@mb=0,ov=0 #@mb=16,ov=14` | log-hit | vm | 358 | 1411 | 1.56e+05 | 3.48e+05 | 2.23 | 3.91e+05 |
| wit2/w03-bounded-12 `\d\d@mb=0,ov=0 #@mb=16,ov=14` | syn | dfa | 0 | 0 | 7.86e+03 | 7.86e+03 | 1.00 | 7.86e+03 |
| wit2/w03-bounded-12 `\d\d@mb=0,ov=0 #@mb=16,ov=14` | syn | vm | 0 | 0 | 7.86e+03 | 7.86e+03 | 1.00 | 7.86e+03 |
| wit2/w05-bounded-at `\d\d\d@mb=0,ov=0 @@mb=11,ov=8` | cap | dfa | 0 | 0 | 7.86e+03 | 7.86e+03 | 1.00 | 7.86e+03 |
| wit2/w05-bounded-at `\d\d\d@mb=0,ov=0 @@mb=11,ov=8` | cap | vm | 0 | 0 | 7.86e+03 | 7.86e+03 | 1.00 | 7.86e+03 |
| wit2/w05-bounded-at `\d\d\d@mb=0,ov=0 @@mb=11,ov=8` | log-fail | dfa | 0 | 0 | 7.86e+03 | 7.86e+03 | 1.00 | 7.86e+03 |
| wit2/w05-bounded-at `\d\d\d@mb=0,ov=0 @@mb=11,ov=8` | log-fail | vm | 0 | 0 | 7.86e+03 | 7.86e+03 | 1.00 | 7.86e+03 |
| wit2/w05-bounded-at `\d\d\d@mb=0,ov=0 @@mb=11,ov=8` | log-hit | dfa | 0 | 0 | 7.87e+03 | 7.87e+03 | 1.00 | 7.87e+03 |
| wit2/w05-bounded-at `\d\d\d@mb=0,ov=0 @@mb=11,ov=8` | log-hit | vm | 0 | 0 | 7.87e+03 | 7.87e+03 | 1.00 | 7.87e+03 |
| wit2/w05-bounded-at `\d\d\d@mb=0,ov=0 @@mb=11,ov=8` | syn | dfa | 748 | 0 | 2.01e+04 | 3.93e+04 | 1.96 | 3.93e+04 |
| wit2/w05-bounded-at `\d\d\d@mb=0,ov=0 @@mb=11,ov=8` | syn | vm | 748 | 0 | 2.01e+04 | 4.49e+05 | 22.40 | 5.84e+05 |
| wit2/w06-loose-gap `\d@mb=6,ov=6 #@mb=10,ov=9` | cap | dfa | 746 | 1489 | 5.76e+04 | 3.84e+04 | 0.67 | 3.84e+04 |
| wit2/w06-loose-gap `\d@mb=6,ov=6 #@mb=10,ov=9` | cap | vm | 746 | 1489 | 7.02e+05 | 4.93e+05 | 0.70 | 5.38e+05 |
| wit2/w06-loose-gap `\d@mb=6,ov=6 #@mb=10,ov=9` | log-fail | dfa | 492 | 1914 | 6.58e+04 | 2.8e+04 | 0.43 | 2.8e+04 |
| wit2/w06-loose-gap `\d@mb=6,ov=6 #@mb=10,ov=9` | log-fail | vm | 492 | 1914 | 8.95e+05 | 3.28e+05 | 0.37 | 3.57e+05 |
| wit2/w06-loose-gap `\d@mb=6,ov=6 #@mb=10,ov=9` | log-hit | dfa | 358 | 1395 | 5.01e+04 | 2.25e+04 | 0.45 | 2.25e+04 |
| wit2/w06-loose-gap `\d@mb=6,ov=6 #@mb=10,ov=9` | log-hit | vm | 358 | 1395 | 6.54e+05 | 2.41e+05 | 0.37 | 2.62e+05 |
| wit2/w06-loose-gap `\d@mb=6,ov=6 #@mb=10,ov=9` | syn | dfa | 0 | 0 | 7.86e+03 | 7.86e+03 | 1.00 | 7.86e+03 |
| wit2/w06-loose-gap `\d@mb=6,ov=6 #@mb=10,ov=9` | syn | vm | 0 | 0 | 7.86e+03 | 7.86e+03 | 1.00 | 7.86e+03 |
| wit2/w11-A-semirare `\d\d\d-@mb=0,ov=0 #@mb=8,ov=4` | cap | dfa | 746 | 0 | 1.54e+04 | 3.7e+04 | 2.39 | 1.5e+04 |
| wit2/w11-A-semirare `\d\d\d-@mb=0,ov=0 #@mb=8,ov=4` | cap | vm | 746 | 0 | 1.54e+04 | 1.5e+04 | 0.97 | 1.5e+04 |
| wit2/w11-A-semirare `\d\d\d-@mb=0,ov=0 #@mb=8,ov=4` | log-fail | dfa | 492 | 0 | 1.29e+04 | 2.71e+04 | 2.10 | 7.06e+04 |
| wit2/w11-A-semirare `\d\d\d-@mb=0,ov=0 #@mb=8,ov=4` | log-fail | vm | 492 | 0 | 1.29e+04 | 7.94e+04 | 6.17 | 1.2e+05 |
| wit2/w11-A-semirare `\d\d\d-@mb=0,ov=0 #@mb=8,ov=4` | log-hit | dfa | 358 | 0 | 1.15e+04 | 2.18e+04 | 1.90 | 7.82e+04 |
| wit2/w11-A-semirare `\d\d\d-@mb=0,ov=0 #@mb=8,ov=4` | log-hit | vm | 358 | 0 | 1.15e+04 | 8.38e+04 | 7.29 | 1.46e+05 |
| wit2/w11-A-semirare `\d\d\d-@mb=0,ov=0 #@mb=8,ov=4` | syn | dfa | 0 | 0 | 7.86e+03 | 7.86e+03 | 1.00 | 4.12e+04 |
| wit2/w11-A-semirare `\d\d\d-@mb=0,ov=0 #@mb=8,ov=4` | syn | vm | 0 | 0 | 7.86e+03 | 9.8e+04 | 12.46 | 9.8e+04 |

| population | consumer | plan cells | P6 better (>2%) | tie | P6 worse (>2%) | sum work P5 | sum work P6 | SHIPPED-comparable cells: P5 / P6 / SHIPPED |
|---|---|---|---|---|---|---|---|---|
| pop | dfa | 9 | 7 | 1 | 1 | 1.49e+06 | 6.25e+05 | 1.49e+06 / 6.25e+05 / 2.41e+06 |
| pop | vm | 10 | 8 | 1 | 1 | 1.32e+07 | 5.8e+06 | 1.32e+07 / 5.8e+06 / 2.97e+07 |
| wit | dfa | 20 | 5 | 7 | 8 | 4.52e+05 | 5.47e+05 | 4.52e+05 / 5.47e+05 / 5.63e+05 |
| wit | vm | 20 | 10 | 6 | 4 | 3.96e+06 | 3.17e+06 | 3.96e+06 / 3.17e+06 / 4.77e+06 |

### E3. Frank's setting, witnesses: every variant (work; one DFA step = 1)


Consumer **dfa**:

| witness | gap | region | subject | nosearch | P5 | P6 | local | local-merge | local-loose | fwd | fwd-gate | fwd-tail | nosearch-gate | nosearch-tail |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| w01-bounded-4 | bounded | 4 | cap | 2.62e+05 | 3.62e+04 | 3.35e+04 | 3.35e+04 | 3.35e+04 | 3.35e+04 | 5.98e+05 | 6.06e+05 | 5.98e+05 | 2.7e+05 | 2.62e+05 |
| w01-bounded-4 | bounded | 4 | log-fail | 2.62e+05 | 2.66e+04 | 3.59e+04 | 3.59e+04 | 2.62e+04 | 3.59e+04 | 1.01e+06 | 1.02e+06 | 1.01e+06 | 2.7e+05 | 2.62e+05 |
| w01-bounded-4 | bounded | 4 | log-hit | 2.62e+05 | 2.15e+04 | 2.83e+04 | 2.83e+04 | 2.12e+04 | 2.83e+04 | 9.79e+05 | 9.87e+05 | 9.79e+05 | 2.7e+05 | 2.62e+05 |
| w01-bounded-4 | bounded | 4 | syn | 2.62e+05 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 3.76e+05 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w03-bounded-12 | bounded | 14 | cap | 2.62e+05 | 4.29e+04 | 5.44e+04 | 5.44e+04 | 4.02e+04 | 5.44e+04 | 7.8e+05 | 7.87e+05 | 7.79e+05 | 2.7e+05 | 2.62e+05 |
| w03-bounded-12 | bounded | 14 | log-fail | 2.62e+05 | 3.1e+04 | 6.05e+04 | 6.05e+04 | 3.51e+04 | 6.05e+04 | 1.51e+06 | 1.51e+06 | 1.5e+06 | 2.7e+05 | 2.62e+05 |
| w03-bounded-12 | bounded | 14 | log-hit | 2.62e+05 | 2.47e+04 | 4.62e+04 | 4.62e+04 | 2.77e+04 | 4.62e+04 | 1.45e+06 | 1.45e+06 | 1.45e+06 | 2.7e+05 | 2.62e+05 |
| w03-bounded-12 | bounded | 14 | syn | 2.62e+05 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 5.15e+05 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w04-bounded-x | bounded | 3 | cap | 2.62e+05 | 3.41e+04 | 3.41e+04 | 1.57e+04 | 1.57e+04 | 1.57e+04 | 1.17e+06 | 1.18e+06 | 1.17e+06 | 2.7e+05 | 2.62e+05 |
| w04-bounded-x | bounded | 3 | log-fail | 2.62e+05 | 1.31e+04 | 1.31e+04 | 1.57e+04 | 1.57e+04 | 1.57e+04 | 2.37e+06 | 2.37e+06 | 2.36e+06 | 2.69e+05 | 2.62e+05 |
| w04-bounded-x | bounded | 3 | log-hit | 2.62e+05 | 1.55e+04 | 1.55e+04 | 1.57e+04 | 1.57e+04 | 1.57e+04 | 2.27e+06 | 2.27e+06 | 2.26e+06 | 2.69e+05 | 2.61e+05 |
| w04-bounded-x | bounded | 3 | syn | 2.62e+05 | 3.18e+04 | 3.18e+04 | 1.57e+04 | 1.57e+04 | 1.57e+04 | 7.35e+05 | 7.42e+05 | 7.35e+05 | 2.69e+05 | 2.62e+05 |
| w05-bounded-at | bounded | 8 | cap | 2.62e+05 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 5.98e+05 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w05-bounded-at | bounded | 8 | log-fail | 2.62e+05 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 1.01e+06 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w05-bounded-at | bounded | 8 | log-hit | 2.62e+05 | 7.87e+03 | 7.87e+03 | 7.87e+03 | 7.87e+03 | 7.87e+03 | 9.79e+05 | 7.87e+03 | 7.87e+03 | 7.87e+03 | 7.87e+03 |
| w05-bounded-at | bounded | 8 | syn | 2.62e+05 | 3.93e+04 | 2.01e+04 | 2.01e+04 | 2.01e+04 | 2.01e+04 | 3.76e+05 | 3.84e+05 | 3.76e+05 | 2.69e+05 | 2.62e+05 |
| w06-loose-gap | bounded | 3 | cap | 2.62e+05 | 3.84e+04 | 5.76e+04 | 5.76e+04 | 3.83e+04 | 8.22e+04 | 1.36e+06 | 1.37e+06 | 1.36e+06 | 2.7e+05 | 2.62e+05 |
| w06-loose-gap | bounded | 3 | log-fail | 2.62e+05 | 2.8e+04 | 6.58e+04 | 6.58e+04 | 2.89e+04 | 1.21e+05 | 2.79e+06 | 2.8e+06 | 2.79e+06 | 2.7e+05 | 2.62e+05 |
| w06-loose-gap | bounded | 3 | log-hit | 2.62e+05 | 2.25e+04 | 5.01e+04 | 5.01e+04 | 2.32e+04 | 9.07e+04 | 2.68e+06 | 2.68e+06 | 2.67e+06 | 2.7e+05 | 2.62e+05 |
| w06-loose-gap | bounded | 3 | syn | 2.62e+05 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 8.42e+05 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w07-unbounded-hash | unbounded | - | cap | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 1.17e+06 | 1.18e+06 | 1.17e+06 | 2.7e+05 | 2.62e+05 |
| w07-unbounded-hash | unbounded | - | log-fail | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 2.37e+06 | 2.37e+06 | 2.37e+06 | 2.7e+05 | 2.62e+05 |
| w07-unbounded-hash | unbounded | - | log-hit | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 2.27e+06 | 2.28e+06 | 2.27e+06 | 2.7e+05 | 2.62e+05 |
| w07-unbounded-hash | unbounded | - | syn | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 7.35e+05 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w08-unbounded-x | unbounded | - | cap | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 1.17e+06 | 1.18e+06 | 1.17e+06 | 2.7e+05 | 2.62e+05 |
| w08-unbounded-x | unbounded | - | log-fail | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 2.37e+06 | 2.37e+06 | 2.36e+06 | 2.69e+05 | 2.62e+05 |
| w08-unbounded-x | unbounded | - | log-hit | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 2.27e+06 | 2.27e+06 | 2.26e+06 | 2.69e+05 | 2.61e+05 |
| w08-unbounded-x | unbounded | - | syn | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 7.35e+05 | 7.42e+05 | 7.35e+05 | 2.69e+05 | 2.62e+05 |
| w09-unbounded-at | unbounded | - | cap | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 1.17e+06 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w09-unbounded-at | unbounded | - | log-fail | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 2.37e+06 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w09-unbounded-at | unbounded | - | log-hit | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 2.27e+06 | 7.87e+03 | 7.87e+03 | 7.87e+03 | 7.87e+03 |
| w09-unbounded-at | unbounded | - | syn | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 7.35e+05 | 7.42e+05 | 7.34e+05 | 2.69e+05 | 2.62e+05 |
| w10-unbounded-lit | unbounded | - | cap | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 1.17e+06 | 1.18e+06 | 1.17e+06 | 2.7e+05 | 2.62e+05 |
| w10-unbounded-lit | unbounded | - | log-fail | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 2.37e+06 | 2.38e+06 | 2.37e+06 | 2.7e+05 | 2.62e+05 |
| w10-unbounded-lit | unbounded | - | log-hit | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 2.27e+06 | 2.28e+06 | 2.27e+06 | 2.7e+05 | 2.62e+05 |
| w10-unbounded-lit | unbounded | - | syn | 2.62e+05 | 2.62e+05 | 2.62e+05 | - | - | - | 7.35e+05 | 7.43e+05 | 7.35e+05 | 2.7e+05 | 2.62e+05 |
| w11-A-semirare | bounded | 4 | cap | 2.62e+05 | 3.7e+04 | 1.54e+04 | 1.54e+04 | 1.54e+04 | 1.54e+04 | 1.5e+04 | 2.29e+04 | 1.5e+04 | 2.7e+05 | 2.62e+05 |
| w11-A-semirare | bounded | 4 | log-fail | 2.62e+05 | 2.71e+04 | 1.29e+04 | 1.29e+04 | 1.29e+04 | 1.29e+04 | 6.1e+04 | 6.88e+04 | 6.09e+04 | 2.7e+05 | 2.62e+05 |
| w11-A-semirare | bounded | 4 | log-hit | 2.62e+05 | 2.18e+04 | 1.15e+04 | 1.15e+04 | 1.15e+04 | 1.15e+04 | 6.33e+04 | 7.12e+04 | 6.33e+04 | 2.7e+05 | 2.62e+05 |
| w11-A-semirare | bounded | 4 | syn | 2.62e+05 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 4.12e+04 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |

Consumer **vm**:

| witness | gap | region | subject | nosearch | P5 | P6 | local | local-merge | local-loose | fwd | fwd-gate | fwd-tail | nosearch-gate | nosearch-tail |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| w01-bounded-4 | bounded | 4 | cap | 1.57e+07 | 2.69e+05 | 8.56e+04 | 8.56e+04 | 8.56e+04 | 8.56e+04 | 1.35e+06 | 1.35e+06 | 1.34e+06 | 1.57e+07 | 1.57e+07 |
| w01-bounded-4 | bounded | 4 | log-fail | 1.57e+07 | 1.8e+05 | 1.08e+05 | 1.08e+05 | 8.99e+04 | 1.08e+05 | 2.37e+06 | 2.38e+06 | 2.37e+06 | 1.57e+07 | 1.57e+07 |
| w01-bounded-4 | bounded | 4 | log-hit | 1.57e+07 | 1.33e+05 | 8.07e+04 | 8.07e+04 | 6.77e+04 | 8.07e+04 | 2.3e+06 | 2.31e+06 | 2.3e+06 | 1.57e+07 | 1.57e+07 |
| w01-bounded-4 | bounded | 4 | syn | 1.57e+07 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 6.58e+05 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w03-bounded-12 | bounded | 14 | cap | 1.57e+07 | 7.17e+05 | 1.65e+05 | 1.65e+05 | 1.38e+05 | 1.65e+05 | 2.21e+06 | 2.22e+06 | 2.21e+06 | 1.57e+07 | 1.57e+07 |
| w03-bounded-12 | bounded | 14 | log-fail | 1.57e+07 | 4.75e+05 | 2.11e+05 | 2.11e+05 | 1.54e+05 | 2.11e+05 | 4.71e+06 | 4.71e+06 | 4.7e+06 | 1.57e+07 | 1.57e+07 |
| w03-bounded-12 | bounded | 14 | log-hit | 1.57e+07 | 3.48e+05 | 1.56e+05 | 1.56e+05 | 1.14e+05 | 1.56e+05 | 4.51e+06 | 4.52e+06 | 4.51e+06 | 1.57e+07 | 1.57e+07 |
| w03-bounded-12 | bounded | 14 | syn | 1.57e+07 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 1.3e+06 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w04-bounded-x | bounded | 3 | cap | 1.57e+07 | 3.41e+04 | 3.41e+04 | 1.57e+04 | 1.57e+04 | 1.57e+04 | 3.69e+06 | 3.7e+06 | 3.69e+06 | 1.57e+07 | 1.57e+07 |
| w04-bounded-x | bounded | 3 | log-fail | 1.57e+07 | 1.31e+04 | 1.31e+04 | 1.57e+04 | 1.57e+04 | 1.57e+04 | 7.94e+06 | 7.93e+06 | 7.92e+06 | 1.57e+07 | 1.57e+07 |
| w04-bounded-x | bounded | 3 | log-hit | 1.57e+07 | 1.55e+04 | 1.55e+04 | 1.57e+04 | 1.57e+04 | 1.57e+04 | 7.59e+06 | 7.56e+06 | 7.55e+06 | 1.57e+07 | 1.57e+07 |
| w04-bounded-x | bounded | 3 | syn | 1.57e+07 | 3.18e+04 | 3.18e+04 | 1.57e+04 | 1.57e+04 | 1.57e+04 | 2.14e+06 | 2.15e+06 | 2.14e+06 | 1.57e+07 | 1.57e+07 |
| w05-bounded-at | bounded | 8 | cap | 1.57e+07 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 1.35e+06 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w05-bounded-at | bounded | 8 | log-fail | 1.57e+07 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 2.37e+06 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w05-bounded-at | bounded | 8 | log-hit | 1.57e+07 | 7.87e+03 | 7.87e+03 | 7.87e+03 | 7.87e+03 | 7.87e+03 | 2.3e+06 | 7.87e+03 | 7.87e+03 | 7.87e+03 | 7.87e+03 |
| w05-bounded-at | bounded | 8 | syn | 1.57e+07 | 4.49e+05 | 2.01e+04 | 2.01e+04 | 2.01e+04 | 2.01e+04 | 6.58e+05 | 6.65e+05 | 6.57e+05 | 1.57e+07 | 1.57e+07 |
| w06-loose-gap | bounded | 3 | cap | 1.57e+07 | 4.93e+05 | 7.02e+05 | 7.02e+05 | 6.73e+05 | 1.02e+06 | 1.52e+07 | 1.52e+07 | 1.52e+07 | 1.57e+07 | 1.57e+07 |
| w06-loose-gap | bounded | 3 | log-fail | 1.57e+07 | 3.28e+05 | 8.95e+05 | 8.95e+05 | 8.38e+05 | 1.77e+06 | 3.33e+07 | 3.33e+07 | 3.33e+07 | 1.57e+07 | 1.57e+07 |
| w06-loose-gap | bounded | 3 | log-hit | 1.57e+07 | 2.41e+05 | 6.54e+05 | 6.54e+05 | 6.13e+05 | 1.3e+06 | 3.18e+07 | 3.18e+07 | 3.18e+07 | 1.57e+07 | 1.57e+07 |
| w06-loose-gap | bounded | 3 | syn | 1.57e+07 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 8.55e+06 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w07-unbounded-hash | unbounded | - | cap | 1.57e+07 | 3.69e+06 | 3.69e+06 | - | - | - | 3.69e+06 | 3.7e+06 | 3.69e+06 | 1.57e+07 | 1.57e+07 |
| w07-unbounded-hash | unbounded | - | log-fail | 1.57e+07 | 7.94e+06 | 7.94e+06 | - | - | - | 7.94e+06 | 7.94e+06 | 7.93e+06 | 1.57e+07 | 1.57e+07 |
| w07-unbounded-hash | unbounded | - | log-hit | 1.57e+07 | 7.59e+06 | 7.59e+06 | - | - | - | 7.59e+06 | 7.6e+06 | 7.59e+06 | 1.57e+07 | 1.57e+07 |
| w07-unbounded-hash | unbounded | - | syn | 1.57e+07 | 2.14e+06 | 2.14e+06 | - | - | - | 2.14e+06 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w08-unbounded-x | unbounded | - | cap | 1.57e+07 | 3.69e+06 | 3.69e+06 | - | - | - | 3.69e+06 | 3.7e+06 | 3.69e+06 | 1.57e+07 | 1.57e+07 |
| w08-unbounded-x | unbounded | - | log-fail | 1.57e+07 | 7.94e+06 | 7.94e+06 | - | - | - | 7.94e+06 | 7.93e+06 | 7.92e+06 | 1.57e+07 | 1.57e+07 |
| w08-unbounded-x | unbounded | - | log-hit | 1.57e+07 | 7.59e+06 | 7.59e+06 | - | - | - | 7.59e+06 | 7.56e+06 | 7.55e+06 | 1.57e+07 | 1.57e+07 |
| w08-unbounded-x | unbounded | - | syn | 1.57e+07 | 2.14e+06 | 2.14e+06 | - | - | - | 2.14e+06 | 2.15e+06 | 2.14e+06 | 1.57e+07 | 1.57e+07 |
| w09-unbounded-at | unbounded | - | cap | 1.57e+07 | 3.69e+06 | 3.69e+06 | - | - | - | 3.69e+06 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w09-unbounded-at | unbounded | - | log-fail | 1.57e+07 | 7.94e+06 | 7.94e+06 | - | - | - | 7.94e+06 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |
| w09-unbounded-at | unbounded | - | log-hit | 1.57e+07 | 7.59e+06 | 7.59e+06 | - | - | - | 7.59e+06 | 7.87e+03 | 7.87e+03 | 7.87e+03 | 7.87e+03 |
| w09-unbounded-at | unbounded | - | syn | 1.57e+07 | 2.14e+06 | 2.14e+06 | - | - | - | 2.14e+06 | 2.15e+06 | 2.14e+06 | 1.57e+07 | 1.57e+07 |
| w10-unbounded-lit | unbounded | - | cap | 1.57e+07 | 3.69e+06 | 3.69e+06 | - | - | - | 3.69e+06 | 3.7e+06 | 3.69e+06 | 1.57e+07 | 1.57e+07 |
| w10-unbounded-lit | unbounded | - | log-fail | 1.57e+07 | 7.94e+06 | 7.94e+06 | - | - | - | 7.94e+06 | 7.95e+06 | 7.94e+06 | 1.57e+07 | 1.57e+07 |
| w10-unbounded-lit | unbounded | - | log-hit | 1.57e+07 | 7.59e+06 | 7.59e+06 | - | - | - | 7.59e+06 | 7.6e+06 | 7.59e+06 | 1.57e+07 | 1.57e+07 |
| w10-unbounded-lit | unbounded | - | syn | 1.57e+07 | 2.14e+06 | 2.14e+06 | - | - | - | 2.14e+06 | 2.15e+06 | 2.14e+06 | 1.57e+07 | 1.57e+07 |
| w11-A-semirare | bounded | 4 | cap | 1.57e+07 | 1.5e+04 | 1.54e+04 | 1.54e+04 | 1.54e+04 | 1.54e+04 | 1.5e+04 | 2.29e+04 | 1.5e+04 | 1.57e+07 | 1.57e+07 |
| w11-A-semirare | bounded | 4 | log-fail | 1.57e+07 | 7.94e+04 | 1.29e+04 | 1.29e+04 | 1.29e+04 | 1.29e+04 | 7.94e+04 | 8.72e+04 | 7.93e+04 | 1.57e+07 | 1.57e+07 |
| w11-A-semirare | bounded | 4 | log-hit | 1.57e+07 | 8.38e+04 | 1.15e+04 | 1.15e+04 | 1.15e+04 | 1.15e+04 | 8.38e+04 | 9.16e+04 | 8.38e+04 | 1.57e+07 | 1.57e+07 |
| w11-A-semirare | bounded | 4 | syn | 1.57e+07 | 9.8e+04 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 9.8e+04 | 7.86e+03 | 7.86e+03 | 7.86e+03 | 7.86e+03 |

### E4. Local-search counts per B stop (witnesses with a bounded gap)

| witness | subject | region (exact) | region (loose) | B stops | local positions per B stop | A windows per B stop | predicted by the table (independence) | window bytes each | starts each |
|---|---|---|---|---|---|---|---|---|---|
| w01-bounded-4 | cap | 4 | 4 | 746 | 5.00 | 0.91 | 0.00209 | 3.0 | 1.0 |
| w01-bounded-4 | log-fail | 4 | 4 | 492 | 5.00 | 1.89 | 0.00209 | 3.0 | 1.0 |
| w01-bounded-4 | log-hit | 4 | 4 | 358 | 5.00 | 1.90 | 0.00209 | 3.0 | 1.0 |
| w03-bounded-12 | cap | 14 | 14 | 746 | 15.00 | 1.90 | 0.0838 | 2.0 | 1.0 |
| w03-bounded-12 | log-fail | 14 | 14 | 492 | 15.00 | 3.93 | 0.0838 | 2.0 | 1.0 |
| w03-bounded-12 | log-hit | 14 | 14 | 358 | 15.00 | 3.94 | 0.0838 | 2.0 | 1.0 |
| w05-bounded-at | syn | 8 | 8 | 748 | 9.00 | 0.00 | 0.00376 | - | - |
| w06-loose-gap | cap | 3 | 15 | 746 | 4.00 | 2.00 | 0.299 | 7.0 | 7.0 |
| w06-loose-gap | log-fail | 3 | 15 | 492 | 4.00 | 3.89 | 0.299 | 7.0 | 7.0 |
| w06-loose-gap | log-hit | 3 | 15 | 358 | 4.00 | 3.90 | 0.299 | 7.0 | 7.0 |
| w11-A-semirare | cap | 4 | 4 | 746 | 5.00 | 0.00 | 1.04e-05 | - | - |
| w11-A-semirare | log-fail | 4 | 4 | 492 | 5.00 | 0.00 | 1.04e-05 | - | - |
| w11-A-semirare | log-hit | 4 | 4 | 358 | 5.00 | 0.00 | 1.04e-05 | - | - |

(Cells where the subject holds no B are omitted: there the plan does no local work.)

### E5. Presence gate in front of the forward search

| population | gap | consumer | cells | B absent | gate < fwd | gate > fwd | tail < fwd | tail > fwd | fwd < nosearch | nosearch-gate < nosearch | sum fwd | sum fwd-gate | sum fwd-tail |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pop | bounded | dfa | 10 | 0 | 0 | 5 | 0 | 0 | 1 | 0 | 1.69e+07 | 1.7e+07 | 1.69e+07 |
| pop | bounded | vm | 10 | 0 | 0 | 1 | 0 | 0 | 9 | 0 | 5.85e+07 | 5.85e+07 | 5.84e+07 |
| pop | unbounded | dfa | 29 | 3 | 3 | 13 | 3 | 0 | 9 | 3 | 6.97e+07 | 5.83e+07 | 5.77e+07 |
| pop | unbounded | vm | 29 | 3 | 3 | 8 | 3 | 0 | 19 | 3 | 2.41e+08 | 2e+08 | 1.99e+08 |
| wit | bounded | dfa | 24 | 7 | 7 | 3 | 7 | 0 | 4 | 7 | 2.46e+07 | 2.04e+07 | 2.02e+07 |
| wit | bounded | vm | 24 | 7 | 7 | 3 | 7 | 0 | 22 | 7 | 1.37e+08 | 1.2e+08 | 1.2e+08 |
| wit | unbounded | dfa | 16 | 4 | 4 | 0 | 4 | 0 | 0 | 4 | 2.62e+07 | 1.97e+07 | 1.97e+07 |
| wit | unbounded | vm | 16 | 4 | 4 | 0 | 4 | 0 | 16 | 4 | 8.55e+07 | 6.41e+07 | 6.4e+07 |

`B absent` = the subject holds no byte of the gate class. `gate < fwd` means the gate lowers the forward search's work by more than 2%.
