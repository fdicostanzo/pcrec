
### A. What the contract can express (per set)

| set | patterns | unparsed | anchored ^ | no span | no bounded span | bounded inner span | inner ov>0 | >=2 bounded spans | has unbounded span | rarest POSITION is in an unbounded span | rarest SPAN (joint) is unbounded |
|---|---|---|---|---|---|---|---|---|---|---|---|
| capability | 71 | 1 | 19 | 2 | 2 | 5 | 5 | 2 | 19 | 11 | 12 |
| loglines | 11 | 0 | 0 | 0 | 0 | 4 | 4 | 4 | 3 | 2 | 1 |
| syntax | 95 | 12 | 3 | 0 | 2 | 6 | 6 | 4 | 20 | 12 | 13 |
| corpus | 150 | 19 | 21 | 19 | 9 | 16 | 16 | 8 | 25 | 15 | 14 |

### A2. Loss notes (patterns carrying each)

| note | capability | loglines | syntax | corpus |
|---|---|---|---|---|
| alt-dropped | 27 | 7 | 6 | 24 |
| anchor-line | 0 | 0 | 1 | 0 |
| assertion | 34 | 7 | 6 | 51 |
| backref | 6 | 0 | 5 | 16 |
| conditional | 0 | 0 | 1 | 0 |
| gstart | 0 | 0 | 1 | 1 |
| kreset | 0 | 0 | 1 | 5 |
| lookaround | 13 | 0 | 4 | 13 |
| recursion | 2 | 0 | 7 | 17 |
| rep-right | 5 | 3 | 1 | 11 |
| verb | 0 | 0 | 3 | 4 |

### A3. Control: extractor prefix classes vs pcrec's k-set walk sizes

169 patterns with a fixed prefix span; 579 positions agree, 6 differ (6 patterns).
- `syntax/cls-posix` 0/1 (notes -)
- `syntax/cls-v` 4/1 (notes -)
- `corpus/c007` 0/1 (notes verb)
- `corpus/c063` 0/1 (notes verb)
- `corpus/c103` 0/1 (notes verb)
- `corpus/c128` 0/1 (notes verb)

### B. Which span each policy picks (patterns with >=1 bounded span, unanchored)

| set | patterns | P2 same span as P1 | P3 | P4 | P5-dfa | P5-vm | declines | picks an INNER span (mb>0) |
|---|---|---|---|---|---|---|---|---|
| capability | 51 | 51 | 51 | 44 | 32 | 45 | P4selfprice:7 P5dfa:19 P5vm:5 | P1:4 P2:4 P3:4 P4:4 P5:0 P5:3 |
| loglines | 11 | 11 | 11 | 9 | 8 | 11 | P4selfprice:2 P5dfa:3 | P1:2 P2:2 P3:2 P4:2 P5:2 P5:2 |
| syntax | 80 | 80 | 80 | 73 | 63 | 73 | P4selfprice:7 P5dfa:17 P5vm:7 | P1:4 P2:4 P3:4 P4:4 P5:3 P5:4 |
| corpus | 110 | 110 | 110 | 100 | 76 | 100 | P4selfprice:10 P5dfa:34 P5vm:9 | P1:14 P2:14 P3:14 P4:14 P5:12 P5:13 |

### B2. Span flips between the consumer-blind and consumer-priced policies

{'P4!=P5-dfa': 47, 'P5-dfa!=P5-vm': 52, 'P4!=P5-vm': 7}
- `capability/currency-lookbehind-fixed`: P4 `one#0{\d}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\d}@a=0,mb=0,ov=0`
- `capability/float-literal-bound`: P4 `one#0{\d}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\d}@a=0,mb=0,ov=0`
- `capability/hex8-bounded`: P4 `decline` / P5-dfa `decline` / P5-vm `one#0{[16][16][16][16][16][16][16][16]}@a=0,mb=0,ov=0`
- `capability/high-byte-run`: P4 `one#0{[128][128]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[128][128]}@a=0,mb=0,ov=0`
- `capability/phone-palindrome-6`: P4 `one#0{\d\d\d}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\d\d\d}@a=0,mb=0,ov=0`
- `capability/tail-digits-eol`: P4 `one#0{\d}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\d}@a=0,mb=0,ov=0`
- `capability/tail-space-eol`: P4 `one#0{\s}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\s}@a=0,mb=0,ov=0`
- `capability/utf8-lead-no-cont`: P4 `one#0{[30]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[30]}@a=0,mb=0,ov=0`
- `capability/wild-codegrammar-json-number-extended`: P4 `one#0{\d}@a=0,mb=1,ov=1` / P5-dfa `decline` / P5-vm `one#0{\d}@a=0,mb=1,ov=1`
- `capability/wild-logparse-base10num-grok`: P4 `one#0{[11]}@a=0,mb=1,ov=1` / P5-dfa `decline` / P5-vm `one#0{[11]}@a=0,mb=1,ov=1`
- `capability/wild-logparse-base10num-noatomic`: P4 `one#0{[11]}@a=0,mb=1,ov=1` / P5-dfa `decline` / P5-vm `one#0{[11]}@a=0,mb=1,ov=1`
- `capability/wild-logparse-syslogbase-expanded`: P4 `one#1{\x20}@a=0,mb=9,ov=7` / P5-dfa `decline` / P5-vm `one#0{[16]}@a=0,mb=0,ov=0`
- `capability/wild-waf-crs-942140-dbnames`: P4 `decline` / P5-dfa `decline` / P5-vm `one#0{[14][20][19][23]}@a=0,mb=0,ov=0`
- `capability/wild-waf-crs-942160-sleep-benchmark`: P4 `one#0{[4][4][4][4][4]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[4][4][4][4][4]}@a=0,mb=0,ov=0`
- `loglines/bignum`: P4 `one#0{\d\d\d\d\d\d\d\d\d\d}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\d\d\d\d\d\d\d\d\d\d}@a=0,mb=0,ov=0`
- `loglines/hex32-id`: P4 `decline` / P5-dfa `decline` / P5-vm `one#0{[16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16][16]}@a=0,mb=0,ov=0`
- `loglines/ipv6`: P4 `decline` / P5-dfa `decline` / P5-vm `one#0{[16]}@a=0,mb=0,ov=0`
- `syntax/cls-d`: P4 `one#0{\d}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\d}@a=0,mb=0,ov=0`
- `syntax/grp-atomic-rep`: P4 `one#0{a}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{a}@a=0,mb=0,ov=0`
- `syntax/qnt-plus-ctl`: P4 `one#0{a}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{a}@a=0,mb=0,ov=0`
- `syntax/qnt-plus`: P4 `one#0{a}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{a}@a=0,mb=0,ov=0`
- `syntax/qnt-poss-plus`: P4 `one#0{a}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{a}@a=0,mb=0,ov=0`
- `syntax/qnt-poss-quest`: P4 `one#0{a}@a=0,mb=1,ov=1` / P5-dfa `decline` / P5-vm `one#0{a}@a=0,mb=1,ov=1`
- `syntax/rec-back`: P4 `one#0{\d\d}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\d\d}@a=0,mb=0,ov=0`
- `syntax/rec-g-angle`: P4 `one#0{\d\d}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\d\d}@a=0,mb=0,ov=0`
- `syntax/rec-py`: P4 `one#0{\d\d}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\d\d}@a=0,mb=0,ov=0`
- `syntax/vrb-skip`: P4 `one#0{a}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{a}@a=0,mb=0,ov=0`
- `corpus/c007`: P4 `one#0{[11]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[11]}@a=0,mb=0,ov=0`
- `corpus/c014`: P4 `one#0{o}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{o}@a=0,mb=0,ov=0`
- `corpus/c021`: P4 `one#0{[2]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[2]}@a=0,mb=0,ov=0`
- `corpus/c023`: P4 `one#0{a}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{a}@a=0,mb=0,ov=0`
- `corpus/c031`: P4 `one#0{[2]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[2]}@a=0,mb=0,ov=0`
- `corpus/c039`: P4 `one#0{a}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{a}@a=0,mb=0,ov=0`
- `corpus/c040`: P4 `one#0{[64]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[64]}@a=0,mb=0,ov=0`
- `corpus/c043`: P4 `one#0{[2]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[2]}@a=0,mb=0,ov=0`
- `corpus/c056`: P4 `one#0{[32]}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{[32]}@a=0,mb=0,ov=0`
- `corpus/c061`: P4 `one#0{a}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{a}@a=0,mb=0,ov=0`
- `corpus/c063`: P4 `one#0{\W}@a=0,mb=0,ov=0` / P5-dfa `decline` / P5-vm `one#0{\W}@a=0,mb=0,ov=0`
- `corpus/c068`: P4 `one#0{a}@a=0,mb=4,ov=4` / P5-dfa `decline` / P5-vm `one#0{a}@a=0,mb=4,ov=4`

### C. Counted consequences on the throughput subjects (sum over the common population)

| subject | set | pop | policy | with form | stops | survivors | window bytes | VM starts | work(dfa) | work(vm) |
|---|---|---|---|---|---|---|---|---|---|---|
| capability__t-256k | capability | 46 | P1-rare-pos | 46 | 1457020 | 1220396 | 1641309 | 1537873 | 5.6e+07 | 1.71e+08 |
| capability__t-256k | capability | 46 | P2-rare-span | 46 | 1457020 | 1220396 | 1641309 | 1537873 | 5.6e+07 | 1.71e+08 |
| capability__t-256k | capability | 46 | P3-pair | 46 | 1277563 | 1220396 | 1641309 | 1537873 | 6.35e+07 | 1.79e+08 |
| capability__t-256k | capability | 46 | P4-selfprice | 46 | 2222582 | 2123282 | 2531727 | 2440759 | 2.87e+07 | 1.78e+08 |
| capability__t-256k | capability | 46 | P5-dfa | 46 | 5056753 | 4993464 | 5003764 | 4993464 | 1.33e+07 | 3.08e+08 |
| capability__t-256k | capability | 46 | P5-vm | 46 | 1868014 | 1631390 | 1776601 | 1734429 | 3.18e+07 | 1.41e+08 |
| capability__t-256k | capability | 46 | P5-dfa-subjprior | 46 | 5050594 | 4993464 | 5003764 | 4993464 | 1.33e+07 | 3.08e+08 |
| capability__t-256k | capability | 46 | SHIPPED | 46 | 2391704 | 2359644 | 2361667 | 2359644 | 4.88e+07 | 2.09e+08 |
| capability__t-256k | corpus | 80 | P1-rare-pos | 80 | 2558236 | 2435090 | 2559502 | 2536639 | 9.05e+07 | 2.89e+08 |
| capability__t-256k | corpus | 80 | P2-rare-span | 80 | 2558236 | 2435090 | 2559502 | 2536639 | 9.05e+07 | 2.89e+08 |
| capability__t-256k | corpus | 80 | P3-pair | 80 | 2438465 | 2435090 | 2559502 | 2536639 | 9.43e+07 | 2.93e+08 |
| capability__t-256k | corpus | 80 | P4-selfprice | 80 | 3071139 | 2949170 | 3073582 | 3050719 | 3.4e+07 | 2.21e+08 |
| capability__t-256k | corpus | 80 | P5-dfa | 80 | 9036018 | 8950576 | 9007739 | 8994483 | 2.22e+07 | 5.54e+08 |
| capability__t-256k | corpus | 80 | P5-vm | 80 | 2922155 | 2800186 | 2895777 | 2882521 | 3.75e+07 | 2.16e+08 |
| capability__t-256k | corpus | 80 | P5-dfa-subjprior | 80 | 6251595 | 6171034 | 6295446 | 6272583 | 2.46e+07 | 3.98e+08 |
| capability__t-256k | corpus | 80 | SHIPPED | 80 | 4100072 | 4024135 | 4033386 | 4030244 | 8.47e+07 | 3.66e+08 |
| loglines__t-256k-fail | loglines | 11 | P1-rare-pos | 11 | 340920 | 130685 | 143099 | 138931 | 8.81e+06 | 1.96e+07 |
| loglines__t-256k-fail | loglines | 11 | P2-rare-span | 11 | 340920 | 130685 | 143099 | 138931 | 8.81e+06 | 1.96e+07 |
| loglines__t-256k-fail | loglines | 11 | P3-pair | 11 | 232935 | 130685 | 143099 | 138931 | 1.13e+07 | 2.22e+07 |
| loglines__t-256k-fail | loglines | 11 | P4-selfprice | 11 | 631281 | 538030 | 550444 | 546276 | 4.32e+06 | 3.68e+07 |
| loglines__t-256k-fail | loglines | 11 | P5-dfa | 11 | 822921 | 800194 | 812563 | 808440 | 3.39e+06 | 5.14e+07 |
| loglines__t-256k-fail | loglines | 11 | P5-vm | 11 | 340920 | 130685 | 143099 | 138931 | 8.81e+06 | 1.96e+07 |
| loglines__t-256k-fail | loglines | 11 | P5-dfa-subjprior | 11 | 819094 | 800194 | 812563 | 808440 | 3.38e+06 | 5.13e+07 |
| loglines__t-256k-fail | loglines | 11 | SHIPPED | 11 | 230219 | 215054 | 274107 | 268808 | 9.62e+06 | 2.98e+07 |
| loglines__t-256k-hit | loglines | 11 | P1-rare-pos | 11 | 335019 | 128199 | 151011 | 139275 | 8.76e+06 | 1.95e+07 |
| loglines__t-256k-hit | loglines | 11 | P2-rare-span | 11 | 335019 | 128199 | 151011 | 139275 | 8.76e+06 | 1.95e+07 |
| loglines__t-256k-hit | loglines | 11 | P3-pair | 11 | 226849 | 128199 | 151011 | 139275 | 1.13e+07 | 2.21e+07 |
| loglines__t-256k-hit | loglines | 11 | P4-selfprice | 11 | 631410 | 538577 | 559901 | 549653 | 4.33e+06 | 3.7e+07 |
| loglines__t-256k-hit | loglines | 11 | P5-dfa | 11 | 826305 | 800566 | 819685 | 811642 | 3.41e+06 | 5.16e+07 |
| loglines__t-256k-hit | loglines | 11 | P5-vm | 11 | 335019 | 128199 | 151011 | 139275 | 8.76e+06 | 1.95e+07 |
| loglines__t-256k-hit | loglines | 11 | P5-dfa-subjprior | 11 | 824702 | 800566 | 819685 | 811642 | 3.4e+06 | 5.16e+07 |
| loglines__t-256k-hit | loglines | 11 | SHIPPED | 11 | 229181 | 211993 | 278161 | 269466 | 9.57e+06 | 2.97e+07 |
| syntax__t-256k | syntax | 68 | P1-rare-pos | 68 | 1901688 | 1568785 | 1868825 | 1597465 | 6.4e+07 | 1.89e+08 |
| syntax__t-256k | syntax | 68 | P2-rare-span | 68 | 1901688 | 1568785 | 1868825 | 1597465 | 6.4e+07 | 1.89e+08 |
| syntax__t-256k | syntax | 68 | P3-pair | 68 | 1580425 | 1568785 | 1868825 | 1597465 | 7.14e+07 | 1.97e+08 |
| syntax__t-256k | syntax | 68 | P4-selfprice | 68 | 2317626 | 2036688 | 2188489 | 2065368 | 2.68e+07 | 1.53e+08 |
| syntax__t-256k | syntax | 68 | P5-dfa | 68 | 4513865 | 4255985 | 4359088 | 4266288 | 2.04e+07 | 2.73e+08 |
| syntax__t-256k | syntax | 68 | P5-vm | 68 | 2317626 | 2036688 | 2188489 | 2065368 | 2.68e+07 | 1.53e+08 |
| syntax__t-256k | syntax | 68 | P5-dfa-subjprior | 68 | 4496752 | 4255985 | 4359088 | 4266288 | 2.04e+07 | 2.73e+08 |
| syntax__t-256k | syntax | 68 | SHIPPED | 68 | 2875277 | 2666120 | 2723871 | 2670284 | 7.15e+07 | 2.67e+08 |

### D. Span vs span: does the ranking flip once the window is priced?

pattern x subject cells with >=2 bounded spans: 22
| ranking compared | argmin span differs |
|---|---|
| prior-vs-measured stops | 1 |
| scan-only vs dfa-priced | 0 |
| scan-only vs vm-priced | 3 |
| dfa vs vm | 3 |

measured/predicted survivors (+1 smoothed), 329 forms: p10 0.109, p50 1.63, p90 240, max 469

### D2. Similar stop counts (<=2x), very different windows (width >=3x or overshoot gap >=4)

10 form pairs
| cell | form A (stops, survivors, window bytes) | form B | work dfa A/B | work vm A/B |
|---|---|---|---|---|
| capability/wild-logparse-syslogbase-expanded t-256k | one#0{[16]}@a=0,mb=0,ov=0 s=58874 v=58874 wb=58874 | one#1{\x20}@a=0,mb=9,ov=7 s=30634 v=30634 wb=306336 | 2402678 / 1242428 | 7053724 / 16253092 |
| capability/wild-secrets-slack-webhook-url t-256k | one#0{[2][2][2][2][2]://[2][2][2][2][2].[2][2][2][2][2].[2][2][2]/[2][2][2][2][2][2][2][2]/[2]\w\w\w\w\w\w\w\w/[2]\w\w\w\w\w\w\w\w}@a=6,mb=0,ov=0 s=7379 v=0 wb=0 | one#1{/\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w\w}@a=0,mb=56,ov=4 s=7380 v=0 wb=0 | 276902 / 276904 | 276902 / 276904 |
| loglines/ipv4 t-256k-fail | one#0{\d\x2e}@a=1,mb=2,ov=2 s=5166 v=4123 wb=16492 | one#2{\d\x2e}@a=1,mb=10,ov=6 s=5166 v=4123 wb=49476 | 371453 / 404437 | 1179561 / 2169081 |
| loglines/ipv4 t-256k-fail | pair#0{\d\x2e}@a=0,1,mb=2,ov=2 s=4123 v=4123 wb=16492 | pair#2{\d\x2e}@a=0,1,mb=10,ov=6 s=4123 v=4123 wb=49476 | 1286958 / 1319942 | 2095066 / 3084586 |
| loglines/ipv4 t-256k-hit | one#0{\d\x2e}@a=1,mb=2,ov=2 s=5863 v=4050 wb=16200 | one#2{\d\x2e}@a=1,mb=10,ov=6 s=5863 v=4050 wb=48597 | 371160 / 403557 | 1164960 / 2136960 |
| loglines/ipv4 t-256k-hit | pair#0{\d\x2e}@a=0,1,mb=2,ov=2 s=4050 v=4050 wb=16200 | pair#2{\d\x2e}@a=0,1,mb=10,ov=6 s=4050 v=4050 wb=48597 | 1285353 / 1317750 | 2079153 / 3051153 |
| corpus/c002 t-256k | one#0{a}@a=0,mb=0,ov=0 s=9607 v=9607 wb=9607 | one#1{c}@a=0,mb=2,ov=1 s=5650 v=5650 wb=16950 | 483105 / 403394 | 1242058 / 1177444 |
| corpus/c019 t-256k | one#0{[2]}@a=0,mb=0,ov=0 s=10847 v=10847 wb=10847 | one#1{c}@a=0,mb=3,ov=2 s=5650 v=5650 wb=22600 | 642697 / 409044 | 1499610 / 1516444 |
| corpus/c112 t-256k | one#0{a}@a=0,mb=0,ov=0 s=9607 v=9607 wb=9607 | one#1{a}@a=0,mb=2,ov=1 s=9607 v=9607 wb=28821 | 483105 / 502319 | 1242058 / 1818478 |
| corpus/c134 t-256k | one#0{[2]}@a=0,mb=0,ov=0 s=10323 v=10323 wb=10323 | one#1{a}@a=0,mb=3,ov=2 s=9607 v=9607 wb=38428 | 630645 / 511926 | 1446162 / 2394898 |
