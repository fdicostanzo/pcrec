| cell | reg | tier | ns lost (vs, ratio) | route: scan / prefilter / start / REQ_WHY | measured bucket (per subject byte; find-all calls) | cause |
|---|---|---|---|---|---|---|
| capability/wild-waf-crs-942360-concat-sqli | thr | A | 28,869,442 (re2 x4.8) | attempt / none / attempt-start / none | loads 3.145 (fwd 3.145, skip 0.000, pre 0.000, rev 0.000); calls 11, memchr 0 | ATTEMPT-SHAPE |
| capability/wild-validator-email-owasp | thr | B | 39,731 (jit x7.22) | attempt / none / attempt-start / one-attempt | loads 0.017 (fwd 0.017, skip 0.000, pre 0.000, rev 0.000); calls 11, memchr 0 | ATTEMPT-STEP |
| capability/hex8-bounded | thr | A | 7,294,385 (re2 x1.94) | unanchored / first-class-bounded / end-minus-width / none | loads 1.243 (fwd 0.843, skip 0.400, pre 0.000, rev 0.000); calls 932, memchr 0 | DENSE-SKIP |
| capability/wild-waf-crs-942140-dbnames | thr | A | 4,905,636 (re2:longest x1.65) | unanchored / first-class-bounded / reverse-pass / none | loads 1.160 (fwd 0.613, skip 0.547, pre 0.000, rev 0.000); calls 11, memchr 0 | DENSE-SKIP |
| capability/wild-codegrammar-json-constant | thr | A | 1,032,127 (re2 x1.14) | unanchored / first-class-bounded / reverse-pass / none | loads 1.127 (fwd 0.371, skip 0.756, pre 0.000, rev 0.000); calls 11, memchr 0 | DENSE-SKIP |
| capability/keyword-prefix-order | thr | A | 848,258 (jit x1.59) | unanchored / offset-set / reverse-pass / dominated | loads 1.061 (fwd 0.016, skip 1.030, pre 0.000, rev 0.016); calls 24541, memchr 164806 | HIT-RESTART |
| loglines/stack-frame | thr | A | 832,488 (jit x2.75) | unanchored / offset-set-bounded / reverse-pass / emitted | loads 1.098 (fwd 0.015, skip 0.000, pre 1.068, rev 0.014); calls 906, memchr 90225 | HIT-RESTART |
| syntax/asr-nwb | thr | A | 551,101 (jit x2.5) | unanchored / offset-set-bounded / end-minus-width / emitted | loads 1.089 (fwd 0.051, skip 0.745, pre 0.293, rev 0.000); calls 2054, memchr 79737 | HIT-RESTART |
| syntax/asr-wb | thr | A | 532,978 (jit x2.36) | unanchored / offset-set-bounded / end-minus-width / emitted | loads 1.088 (fwd 0.059, skip 0.772, pre 0.257, rev 0.000); calls 1862, memchr 81011 | HIT-RESTART |
| syntax/cls-fold-pair | thr | A | 299,109 (jit x1.68) | unanchored / memchr / end-minus-width / emitted | loads 1.094 (fwd 0.022, skip 0.006, pre 1.066, rev 0.000); calls 7631, memchr 50291 | HIT-RESTART |
| syntax/cls-dot | thr | A | 285,717 (jit x1.64) | unanchored / memchr / end-minus-width / dominated | loads 1.037 (fwd 0.098, skip 0.938, pre 0.000, rev 0.000); calls 7631, memchr 42663 | HIT-RESTART |
| syntax/mod-reset | thr | A | 214,210 (jit x1.29) | unanchored / run-pinned / end-minus-width / dominated | loads 1.096 (fwd 0.023, skip 1.073, pre 0.000, rev 0.000); calls 8065, memchr 93897 | HIT-RESTART |
| syntax/mod-unset | thr | A | 210,837 (jit x1.28) | unanchored / run-pinned / end-minus-width / dominated | loads 1.096 (fwd 0.023, skip 1.073, pre 0.000, rev 0.000); calls 8065, memchr 93897 | HIT-RESTART |
| syntax/mod-x | thr | A | 149,995 (jit x1.29) | unanchored / run-pinned / end-minus-width / dominated | loads 1.089 (fwd 0.022, skip 1.066, pre 0.000, rev 0.000); calls 7631, memchr 42663 | HIT-RESTART |
| syntax/esc-hex | thr | A | 149,514 (jit x1.29) | unanchored / run-pinned / end-minus-width / dominated | loads 1.089 (fwd 0.022, skip 1.066, pre 0.000, rev 0.000); calls 7631, memchr 42663 | HIT-RESTART |
| syntax/lit-cat | thr | A | 148,349 (jit x1.29) | unanchored / run-pinned / end-minus-width / dominated | loads 1.089 (fwd 0.022, skip 1.066, pre 0.000, rev 0.000); calls 7631, memchr 42663 | HIT-RESTART |
| syntax/mod-n | thr | A | 141,216 (jit x1.27) | unanchored / run-pinned / end-minus-width / dominated | loads 1.089 (fwd 0.022, skip 1.066, pre 0.000, rev 0.000); calls 7631, memchr 42663 | HIT-RESTART |
| syntax/grp-noncap | thr | A | 42,544 (jit x1.26) | unanchored / offset-set / reverse-pass / dominated | loads 1.015 (fwd 0.004, skip 1.006, pre 0.000, rev 0.004); calls 1983, memchr 10924 | HIT-RESTART |
| loglines/stack-frame | srch | B | 15,823 (jit x1.9) | unanchored / offset-set-bounded / reverse-pass / emitted |  | HIT-RESTART |
| syntax/mod-i | thr | A | 459,074 (jit x1.81) | unanchored / byte-class / end-minus-width / emitted | loads 5.149 (fwd 0.023, skip 0.006, pre 5.120, rev 0.000); calls 8065, memchr 53301 | K101 |
| syntax/mod-r | thr | A | 457,293 (jit x1.81) | unanchored / byte-class / end-minus-width / emitted | loads 5.149 (fwd 0.023, skip 0.006, pre 5.120, rev 0.000); calls 8065, memchr 53301 | K101 |
| syntax/alt-nested | thr | A | 756,021 (jit x1.63) | unanchored / byte-class / end-minus-width / none | loads 1.076 (fwd 0.171, skip 0.906, pre 0.000, rev 0.000); calls 11395, memchr 0 | PAIR-SKIP |
| syntax/alt-two | thr | A | 606,753 (jit x1.52) | unanchored / byte-class / end-minus-width / none | loads 1.078 (fwd 0.161, skip 0.917, pre 0.000, rev 0.000); calls 11395, memchr 0 | PAIR-SKIP |
| capability/high-byte-run | thr | A | 257,378 (jit x1.19) | unanchored / byte-class / reverse-pass / none | loads 1.000 (fwd 0.000, skip 1.000, pre 0.000, rev 0.000); calls 11, memchr 0 | RANGE-SKIP |
| capability/utf8-lead-no-cont | thr | A | 185,627 (jit x1.13) | unanchored / byte-class-bounded / end-minus-width / none | loads 1.000 (fwd 0.000, skip 1.000, pre 0.000, rev 0.000); calls 11, memchr 0 | RANGE-SKIP |
| bounded/pw-8-64 | thr | A | 62,985 (jit x1.49) | unanchored / byte-class / reverse-pass / none | loads 2.031 (fwd 1.016, skip 0.016, pre 0.000, rev 1.000); calls 1669, memchr 0 | REV-PASS |
| bounded/line-80 | thr | A | 43,221 (jit x2.34) | unanchored / byte-class / reverse-pass / none | loads 2.000 (fwd 1.000, skip 0.000, pre 0.000, rev 1.000); calls 10, memchr 0 | REV-PASS |
| bounded/cls-atleast-4096 | thr | A | 28,046 (jit x1.47) | unanchored / byte-class / reverse-pass / none | loads 1.808 (fwd 0.808, skip 0.192, pre 0.000, rev 0.808); calls 8, memchr 0 | REV-PASS |
| capability/wild-waf-crs-942270-union-select | thr | A | 1,758,450 (jit x9.49) | unanchored / byte-class / reverse-pass / emitted | loads 2.115 (fwd 0.000, skip 0.000, pre 2.115, rev 0.000); calls 11, memchr 134706 | RUN-PICK |
| loglines/hex32-id | thr | A | 3,586,946 (rust(SIMD-only) x1.48) | unanchored / first-class-bounded / end-minus-width / none | loads 1.246 (fwd 0.847, skip 0.400, pre 0.000, rev 0.000); calls 268, memchr 0 | LIST-RUST |
| syntax/cls-i-class | thr | A | 371,049 (rust(SIMD-only) x1.4) | unanchored / byte-class / end-minus-width / none | loads 1.039 (fwd 0.090, skip 0.948, pre 0.000, rev 0.000); calls 8065, memchr 0 | LIST-RUST |
| syntax/cls-pair-ctl | thr | A | 87,850 (rust(SIMD-only) x1.14) | unanchored / memchr / end-minus-width / emitted | loads 1.094 (fwd 0.022, skip 0.006, pre 1.066, rev 0.000); calls 7631, memchr 50291 | LIST-RUST |
| syntax/esc-tab | thr | A | 8,682 (rust(SIMD-only) x1.15) | unanchored / run-pinned / end-minus-width / dominated | loads 1.004 (fwd 0.000, skip 1.004, pre 0.000, rev 0.000); calls 28, memchr 3565 | LIST-RUST |
| capability/wild-waf-crs-942360-concat-sqli | srch | C | 2,654 (rust(SIMD-only) x1.55) | attempt / none / attempt-start / none |  | LIST-RUST |
| bounded/cls-atleast-4096 | srch | C | 2,083 (rust(SIMD-only) x9.05) | unanchored / byte-class / reverse-pass / none |  | LIST-RUST |
| bounded/cls-atleast-4096 | match | C | 1,840 (rust(SIMD-only) x7.67) | unanchored / byte-class / reverse-pass / none |  | LIST-RUST |
| bounded/floor | match | C | 139 (rust(SIMD-only) x1.47) | unanchored / memchr / end-minus-width / dominated |  | LIST-RUST |
| syntax/floor | match | C | 133 (rust(SIMD-only) x1.56) | unanchored / memchr / end-minus-width / dominated |  | LIST-RUST |
| loglines/ipv6 | thr | A | 3,139,263 (rust(SIMD-only) x1.42) | unanchored / byte-class / reverse-pass / emitted | loads 1.194 (fwd 0.647, skip 0.543, pre 0.001, rev 0.002); calls 268, memchr 268 | LIST-SCAN-SIMD |
| capability/wild-semdiv-altorder-foo-foobar-rustregex | thr | A | 953,185 (jit x4.04) | unanchored / run-pinned / reverse-pass / dominated | loads 1.042 (fwd 0.000, skip 1.042, pre 0.000, rev 0.000); calls 15, memchr 94788 | LIST-SCAN-SIMD |
| capability/file-ext-order | thr | A | 530,904 (jit x3.0) | unanchored / run-pinned / reverse-pass / dominated | loads 1.031 (fwd 0.000, skip 1.031, pre 0.000, rev 0.000); calls 11, memchr 71506 | LIST-SCAN-SIMD |
| syntax/cls-s-lc | thr | A | 434,462 (jit x2.52) | unanchored / memchr / reverse-pass / emitted | loads 1.044 (fwd 0.076, skip 0.954, pre 0.013, rev 0.000); calls 16, memchr 42888 | LIST-SCAN-SIMD |
| syntax/anc-m-dollar | thr | A | 298,876 (jit x2.36) | unanchored / offset-set-bounded / end-minus-width / emitted | loads 1.036 (fwd 0.014, skip 0.961, pre 0.062, rev 0.000); calls 195, memchr 42040 | LIST-SCAN-SIMD |
| syntax/cls-n-uc | thr | A | 286,001 (jit x1.95) | unanchored / offset-set / end-minus-width / emitted | loads 1.185 (fwd 0.013, skip 0.352, pre 0.820, rev 0.000); calls 3596, memchr 43816 | LIST-SCAN-SIMD |
| syntax/mod-s | thr | A | 276,290 (jit x2.63) | unanchored / offset-set / end-minus-width / emitted | loads 1.027 (fwd 0.016, skip 0.994, pre 0.017, rev 0.000); calls 41, memchr 30444 | LIST-SCAN-SIMD |
| syntax/cls-v | thr | A | 269,729 (jit x2.58) | unanchored / offset-set / reverse-pass / emitted | loads 1.026 (fwd 0.013, skip 1.011, pre 0.001, rev 0.000); calls 5, memchr 30295 | LIST-SCAN-SIMD |
| syntax/esc-octal-0 | thr | A | 235,206 (jit x2.4) | unanchored / run-pinned / end-minus-width / dominated | loads 1.034 (fwd 0.000, skip 1.034, pre 0.000, rev 0.000); calls 39, memchr 30413 | LIST-SCAN-SIMD |
| syntax/anc-m-caret | thr | A | 199,498 (jit x2.05) | attempt / memchr / attempt-start / emitted | loads 1.040 (fwd 0.038, skip 0.000, pre 0.984, rev 0.000); calls 344, memchr 28020 | LIST-SCAN-SIMD |
| loglines/iso-ts | thr | A | 190,474 (jit x1.2) | unanchored / offset-set / reverse-pass / dominated | loads 1.025 (fwd 0.014, skip 1.010, pre 0.000, rev 0.002); calls 268, memchr 73531 | LIST-SCAN-SIMD |
| syntax/esc-nl | thr | A | 164,630 (jit x1.99) | unanchored / run-pinned / end-minus-width / dominated | loads 1.021 (fwd 0.000, skip 1.021, pre 0.000, rev 0.000); calls 5, memchr 27666 | LIST-SCAN-SIMD |
| syntax/qnt-quest | thr | A | 151,933 (jit x1.34) | unanchored / offset-set / reverse-pass / emitted | loads 1.099 (fwd 0.015, skip 0.004, pre 1.064, rev 0.015); calls 3032, memchr 45692 | LIST-SCAN-SIMD |
| syntax/cls-h | thr | A | 128,445 (jit x1.97) | unanchored / memchr / reverse-pass / emitted | loads 1.090 (fwd 0.023, skip 0.985, pre 0.080, rev 0.001); calls 154, memchr 11615 | LIST-SCAN-SIMD |
| capability/router-prefix-order | thr | A | 120,077 (jit x1.43) | unanchored / run-pinned / reverse-pass / dominated | loads 1.034 (fwd 0.000, skip 1.033, pre 0.000, rev 0.000); calls 323, memchr 39130 | LIST-SCAN-SIMD |
| syntax/esc-quote | thr | A | 37,272 (jit x1.35) | unanchored / offset-set / end-minus-width / emitted | loads 1.010 (fwd 0.000, skip 0.000, pre 1.009, rev 0.000); calls 75, memchr 12462 | LIST-SCAN-SIMD |
| syntax/qnt-quest | match | C | 115 (rust(SIMD-only) x1.42) | unanchored / offset-set / reverse-pass / emitted |  | LIST-SCAN-SIMD |
