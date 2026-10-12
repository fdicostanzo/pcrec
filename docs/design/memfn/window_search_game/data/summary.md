
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
