# [OPTLOOP.1-CAPSVIEW] — the captures-vs-captures re-ranking of cycle 1

Lane `capsview`, 2026-09-22, branch `lane/capsview` from `69172a00`.
Docs only: nothing under `src/`, `cli/`, `lib/` or `tests/`; nothing written
in `/Users/fdicostanzo/pcrec-bench` (read-only reference).

**The ask.** Frank, 2026-09-22, on `cycle1_analysis.md`'s own ranking (lane
`optrev`, [OPTLOOP.1.analysis]/[BENCH-REVIEW]): *"we do have the fastest
times but sometimes they are fastest because we consider a version without
capture. We need to consider capture vs capture engines for those. Apples vs
apples."* This memo answers that: it takes pcrec's SHIPPED DEFAULT
(`auto-caps`, `--features all`, captures on, engine auto) and ranks it
against the capture-bearing competitor engines only, instead of taking
pcrec's best-of-four-variants figure §1 used.

**Sources.** `cycle1_analysis.md` §0 (the algorithmic-advantage criterion and
the class weighting, reused unchanged, not re-derived here), §1/§1.1 (the
best-variant ranking and its own default-config caveat), §2.3 (the D81
stamp buckets). The bench report
`/Users/fdicostanzo/pcrec-bench/reports/2026-09-20-capability-0.1-budu-ryzen1600-fullroster-25b1984f.{tsv,matrix.tsv}`
— the SAME data `cycle1_analysis.md` was written against. This lane's brief
names a newer 2026-09-22 `wrapfix` group
(`2026-09-22-capability-0.1-budu-ryzen1600-wrapfix-25b1984f.*`) as the latest
sample for seven testees, with rank order unchanged from `fullroster`; this
memo does not independently re-verify that claim and ranks on the SAME
`fullroster` pin `cycle1_analysis.md` used throughout, per the brief's own
instruction ("cite it, rank on the same data the analysis used"). No timing
was taken on this box; every number is the bench's Ryzen 1600 measurement or
a `pcrec --list-*`/emitted-C stamp already on file from `cycle1_analysis.md`'s
own compile pass.

**Reproduction.** `docs/dev/optloop/capsview.py` reads the SAME reproduction
artifacts `cycle1_analysis.md`'s own scripts wrote to the shared scratchpad
(`rank.json`'s per-testee nanosecond dict for every one of the 125 ranked
cells; `stamps.json`'s `RX_*` stamps from the `auto-caps`/`auto-nocaps`
compiles) — nothing recompiled, nothing re-measured. Its output,
`docs/dev/optloop/capsview_data.json`, is the single source every table
below is rendered from; every ratio in this document is one row of that
file divided by another cell of the SAME row (never across rows, patterns
or regimes, per §0's own rule, carried forward unchanged).

---

## 1. The CAPS table — pcrec `auto-caps` against capture engines only

All 125 of §1's ranked cells, minus the two where `auto-caps` itself does
not compile (listed at the table's foot, not scored). Competitor set:
`pcre2-interp`, `oniguruma`, `re2`, `re2-longest`, `rust`, `tre` — `pcre2-jit`
excluded as a target (§0 rule 1: JIT codegen is not algorithmic), `pcre2-dfa`
and `vectorscan` excluded (§0 rule 2/this brief: they are NOCAPS testees,
not a captures comparison). The **best scalar-caps** column repeats §0 rule
4's carve-out inside the captures-only set: the best of the same six minus
`rust` (rust's SIMD prefilter is a deferred phase, not a cycle-1 target).
Same weight-per-family and `score = weight × log2(ratio)` (clamped at 0)
formula as §0, using the SAME per-family weights §0 computed over the whole
125-row population — not recomputed over this narrower 123-row scorable set,
so a family that loses a row here to a compile failure does not have its
remaining rows' weight inflated to compensate. Ranked descending by score.
The **orig §1 variant/ratio** columns are `cycle1_analysis.md`'s own
best-of-four-variants figure for the same cell, carried alongside for direct
comparison — never re-derived, read straight from `rank.json`.

| # | score | family | pattern | regime | auto-caps ns | best capture engine | best-cap ns | ratio | best scalar-caps engine | scalar-caps ratio | orig §1 variant | orig §1 ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.9588 | cap-recursion | `bracket-array-define` | thr | 4,880,764 | onig | 93.600 | **52144.92x** | onig | 52144.92x | vm-in | 52122.953 |
| 2 | 1.2984 | redos-nested | `evil-alt-nested` | thr | 4,305,649 | rust | 87.841 | **49016.29x** | re2-longest | 13860.53x | auto-nocaps | 0.311 |
| 3 | 1.2723 | redos-nested | `trim-nested-star` | thr | 3,248,263 | rust | 82.346 | **39446.71x** | re2 | 11363.55x | auto-nocaps | 0.185 |
| 4 | 1.0113 | redos-nested | `trim-nested-star` | srch | 8,970,875 | rust | 1993.0 | **4501.17x** | re2 | 952.11x | auto-nocaps | 0.215 |
| 5 | 0.9502 | cap-recursion | `tag-depth3-bound` | thr | 4,512,599 | pcre2-interp | 23238.0 | **194.19x** | pcre2-interp | 194.19x | vm-in | 193.188 |
| 6 | 0.9178 | cap-backref | `dup-param-detect` | thr | 13,461,123 | pcre2-interp | 23240.8 | **579.20x** | pcre2-interp | 579.20x | auto-nocaps | 576.383 |
| 7 | 0.8710 | semantics-divergence | `wild-semdiv-dollar-trailing-newline-pcre2` | thr | 109,716 | rust | 78.300 | **1401.23x** | onig | 725.16x | auto-caps | 1401.225 |
| 8 | 0.7647 | cap-backref | `tag-pair-match` | thr | 4,657,317 | pcre2-interp | 23229.8 | **200.49x** | pcre2-interp | 200.49x | auto-nocaps | 199.497 |
| 9 | 0.7232 | wild-secrets | `wild-secrets-username-password-pair` | thr | 1,283,961 | pcre2-interp | 23276.3 | **55.16x** | pcre2-interp | 55.16x | auto-caps | 55.162 |
| 10 | 0.6112 | wild-secrets | `wild-secrets-aws-access-key-id` | thr | 4,010,040 | rust | 135,250 | **29.65x** | pcre2-interp | 18.40x | auto-caps | 29.649 |
| 11 | 0.3611 | wild-logparse | `wild-logparse-winpath-grok` | thr | 3,470,269 | pcre2-interp | 23249.3 | **149.26x** | pcre2-interp | 149.26x | auto-nocaps | 149.201 |
| 12 | 0.2976 | cap-recursion | `nested-comment-rec` | thr | 7,807,113 | onig | 1,498,678 | **5.21x** | onig | 5.21x | vm-in | 5.198 |
| 13 | 0.2788 | wild-codegrammar | `wild-codegrammar-json-constant` | thr | 4,198,570 | rust | 280,589 | **14.96x** | re2 | 1.88x | auto-caps | 14.963 |
| 14 | 0.2435 | wild-waf | `wild-waf-crs-942360-concat-sqli` | thr | 12,149,169 | re2-longest | 2,246,279 | **5.41x** | re2-longest | 5.41x | auto-caps | 5.409 |
| 15 | 0.2258 | semantics-divergence | `router-prefix-order` | thr | 393,594 | rust | 60176.5 | **6.54x** | re2 | 0.98x | auto-caps | 6.541 |
| 16 | 0.2213 | semantics-divergence | `file-ext-order` | thr | 292,750 | rust | 46454.2 | **6.30x** | re2-longest | 1.17x | auto-nocaps | 6.299 |
| 17 | 0.1931 | semantics-divergence | `wild-semdiv-altorder-foo-foobar-rustregex` | thr | 409,792 | rust | 82230.5 | **4.98x** | re2 | 1.26x | auto-caps | 4.983 |
| 18 | 0.1833 | wild-waf | `wild-waf-crs-942270-union-select` | thr | 999,731 | rust | 280,701 | **3.56x** | re2-longest | 2.28x | auto-nocaps | 3.558 |
| 19 | 0.1765 | wild-secrets | `wild-secrets-github-pat` | thr | 124,480 | rust | 46777.4 | **2.66x** | onig | 0.30x | auto-nocaps | 2.659 |
| 20 | 0.1708 | wild-waf | `wild-waf-crs-942160-sleep-benchmark` | thr | 1,269,889 | rust | 388,639 | **3.27x** | re2 | 0.57x | auto-caps | 3.268 |
| 21 | 0.1536 | cap-recursion | `bracket-array-define` | srch | 6834.4 | onig | 2915.5 | **2.34x** | onig | 2.34x | vm-caps | 2.339 |
| 22 | 0.1397 | cap-backref | `quoted-delim-match` | thr | 10,105,663 | onig | 3,837,825 | **2.63x** | onig | 2.63x | auto-nocaps | 2.546 |
| 23 | 0.1328 | cap-recursion | `nested-comment-rec` | srch | 9319.5 | onig | 4461.8 | **2.09x** | onig | 2.09x | vm-caps | 2.081 |
| 24 | 0.1147 | cap-recursion | `balanced-parens-rec` | thr | 5,485,432 | pcre2-interp | 2,903,815 | **1.89x** | pcre2-interp | 1.89x | vm-caps | 1.887 |
| 25 | 0.0976 | cap-recursion | `balanced-parens-rec` | srch | 6643.5 | pcre2-interp | 3866.6 | **1.72x** | pcre2-interp | 1.72x | auto-nocaps | 1.680 |
| 26 | 0.0906 | cap-backref | `dup-param-detect` | srch | 10874.1 | pcre2-interp | 5805.1 | **1.87x** | pcre2-interp | 1.87x | auto-nocaps | 1.867 |
| 27 | 0.0866 | wild-waf | `wild-waf-crs-942140-dbnames` | thr | 4,085,020 | re2 | 2,241,475 | **1.82x** | re2 | 1.82x | auto-caps | 1.822 |
| 28 | 0.0832 | semantics-divergence | `keyword-prefix-order` | thr | 731,141 | rust | 365,976 | **2.00x** | re2 | 0.30x | auto-nocaps | 1.997 |
| 29 | 0.0698 | wild-validator | `wild-validator-ipv4-owasp` | thr | 31.987 | rust | 17.900 | **1.79x** | pcre2-interp | 0.33x | auto-nocaps | 1.043 |
| 30 | 0.0679 | cap-backref | `quoted-delim-match` | srch | 11359.6 | onig | 7095.2 | **1.60x** | onig | 1.60x | auto-nocaps | 1.573 |
| 31 | 0.0617 | wild-validator | `wild-validator-us-zip-owasp` | thr | 30.205 | rust | 18.084 | **1.67x** | pcre2-interp | 0.32x | auto-nocaps | 0.984 |
| 32 | 0.0617 | wild-waf | `wild-waf-crs-942360-concat-sqli` | srch | 7378.9 | rust | 4812.2 | **1.53x** | re2 | 0.77x | auto-caps | 1.533 |
| 33 | 0.0472 | cap-backref | `tag-pair-match` | srch | 6023.9 | pcre2-interp | 4343.7 | **1.39x** | pcre2-interp | 1.39x | auto-caps | 1.387 |
| 34 | 0.0437 | wild-secrets | `wild-secrets-aws-access-key-id` | srch | 2731.4 | rust | 2143.1 | **1.27x** | pcre2-interp | 0.60x | auto-nocaps | 1.152 |
| 35 | 0.0220 | cap-lookaround | `currency-lookbehind-fixed` | thr | 11,179,317 | onig | 9,600,379 | **1.16x** | onig | 1.16x | vm-in | 1.158 |
| 36 | 0.0156 | cap-recursion | `tag-depth3-bound` | srch | 7142.9 | onig | 6552.3 | **1.09x** | onig | 1.09x | vm-in | 1.053 |
| 37 | 0.0116 | wild-validator | `uuid-near-miss` | thr | 19.929 | rust | 18.100 | **1.10x** | onig | 0.21x | auto-caps | 1.101 |
| 38 | 0.0040 | wild-validator | `ipv4-near-miss` | thr | 18.716 | rust | 18.100 | **1.03x** | pcre2-interp | 0.20x | auto-nocaps | 1.033 |
| 39 | 0.0019 | wild-secrets | `wild-secrets-github-pat` | srch | 1701.6 | rust | 1683.6 | **1.01x** | onig | 0.58x | auto-nocaps | 0.815 |
| 40 | 0.0000 | wild-logparse | `base10num-near-miss` | thr | 16.914 | rust | 90.113 | **0.19x** | pcre2-interp | 0.18x | auto-nocaps | 0.209 |
| 41 | 0.0000 | wild-logparse | `base10num-near-miss` | srch | 555.0 | rust | 2222.5 | **0.25x** | re2 | 0.14x | auto-nocaps | 0.248 |
| 42 | 0.0000 | wild-codegrammar | `codegrammar-flat` | thr | 608,610 | pcre2-interp | 2,116,041 | **0.29x** | pcre2-interp | 0.29x | auto-caps | 0.288 |
| 43 | 0.0000 | wild-codegrammar | `codegrammar-flat` | srch | 931.1 | rust | 2496.0 | **0.37x** | pcre2-interp | 0.34x | auto-nocaps | 0.295 |
| 44 | 0.0000 | wild-codegrammar | `codegrammar-xflag` | thr | 604,191 | pcre2-interp | 2,121,187 | **0.28x** | pcre2-interp | 0.28x | auto-caps | 0.285 |
| 45 | 0.0000 | wild-codegrammar | `codegrammar-xflag` | srch | 932.2 | rust | 2485.9 | **0.37x** | pcre2-interp | 0.34x | auto-nocaps | 0.293 |
| 46 | 0.0000 | cap-lookaround | `currency-lookbehind-fixed` | srch | 5149.0 | pcre2-interp | 15949.0 | **0.32x** | pcre2-interp | 0.32x | auto-caps | 0.336 |
| 47 | 0.0000 | redos-nested | `date-nested-plus` | thr | 30.625 | rust | 81.748 | **0.37x** | onig | 0.32x | auto-nocaps | 0.197 |
| 48 | 0.0000 | redos-nested | `date-nested-plus` | srch | 869.7 | rust | 1762.3 | **0.49x** | pcre2-interp | 0.20x | auto-nocaps | 0.279 |
| 49 | 0.0000 | cap-backref | `doubled-word` | thr | 25,478,964 | onig | 80,036,134 | **0.32x** | onig | 0.32x | auto-nocaps | 0.317 |
| 50 | 0.0000 | cap-backref | `doubled-word` | srch | 20883.1 | pcre2-interp | 83264.2 | **0.25x** | pcre2-interp | 0.25x | auto-nocaps | 0.250 |
| 51 | 0.0000 | cap-lookaround | `email-local-nodup` | thr | 978.7 | onig | 1381.0 | **0.71x** | onig | 0.71x | auto-caps | 0.709 |
| 52 | 0.0000 | cap-lookaround | `email-local-nodup` | srch | 10638.3 | onig | 18596.6 | **0.57x** | onig | 0.57x | auto-nocaps | 0.570 |
| 53 | 0.0000 | redos-nested | `email-nested-plus` | thr | 48.279 | rust | 107.5 | **0.45x** | re2 | 0.14x | auto-nocaps | 0.304 |
| 54 | 0.0000 | redos-nested | `email-nested-plus` | srch | 1429.6 | pcre2-interp | 3172.2 | **0.45x** | pcre2-interp | 0.45x | auto-nocaps | 0.308 |
| 55 | 0.0000 | semantics-divergence | `file-ext-order` | srch | 852.6 | rust | 1424.6 | **0.60x** | onig | 0.27x | auto-nocaps | 0.582 |
| 56 | 0.0000 | cap-lookaround | `float-literal-bound` | thr | 1,789,283 | onig | 13,300,527 | **0.13x** | onig | 0.13x | auto-nocaps | 0.135 |
| 57 | 0.0000 | cap-lookaround | `float-literal-bound` | srch | 2487.2 | pcre2-interp | 5490.3 | **0.45x** | pcre2-interp | 0.45x | auto-nocaps | 0.452 |
| 58 | 0.0000 | floor | `floor-byte` | thr | 23114.5 | tre | 23231.6 | **0.99x** | tre | 0.99x | auto-caps | 0.995 |
| 59 | 0.0000 | floor | `floor-byte` | srch | 667.2 | rust | 1228.3 | **0.54x** | tre | 0.32x | auto-nocaps | 0.542 |
| 60 | 0.0000 | binary-nonutf8 | `high-byte-run` | thr | 482,988 | pcre2-interp | 1,017,809 | **0.47x** | pcre2-interp | 0.47x | auto-caps | 0.477 |
| 61 | 0.0000 | binary-nonutf8 | `high-byte-run` | srch | 1119.7 | pcre2-interp | 3529.0 | **0.32x** | pcre2-interp | 0.32x | auto-nocaps | 0.338 |
| 62 | 0.0000 | wild-validator | `ipv4-near-miss` | srch | 493.0 | rust | 1435.2 | **0.34x** | pcre2-interp | 0.17x | auto-caps | 0.344 |
| 63 | 0.0000 | semantics-divergence | `keyword-prefix-order` | srch | 774.2 | rust | 1619.6 | **0.48x** | pcre2-interp | 0.19x | auto-caps | 0.478 |
| 64 | 0.0000 | wild-logparse | `logparse-atomic` | thr | 30.200 | onig | 97.798 | **0.31x** | onig | 0.31x | auto-caps | 0.309 |
| 65 | 0.0000 | wild-logparse | `logparse-atomic` | srch | 844.3 | pcre2-interp | 4959.1 | **0.17x** | pcre2-interp | 0.17x | auto-nocaps | 0.169 |
| 66 | 0.0000 | wild-logparse | `logparse-atomic-removed` | thr | 30.259 | rust | 86.313 | **0.35x** | onig | 0.31x | auto-nocaps | 0.217 |
| 67 | 0.0000 | wild-logparse | `logparse-atomic-removed` | srch | 811.4 | rust | 1562.5 | **0.52x** | pcre2-interp | 0.17x | auto-nocaps | 0.315 |
| 68 | 0.0000 | binary-nonutf8 | `mojibake-curly-quote` | thr | 23138.5 | pcre2-interp | 23237.6 | **1.00x** | pcre2-interp | 1.00x | auto-nocaps | 0.995 |
| 69 | 0.0000 | binary-nonutf8 | `mojibake-curly-quote` | srch | 682.6 | pcre2-interp | 2824.6 | **0.24x** | pcre2-interp | 0.24x | auto-caps | 0.242 |
| 70 | 0.0000 | redos-nested | `numeric-id-nested-plus` | thr | 27.798 | rust | 86.584 | **0.32x** | pcre2-interp | 0.30x | auto-nocaps | 0.189 |
| 71 | 0.0000 | redos-nested | `numeric-id-nested-plus` | srch | 834.5 | rust | 2674.0 | **0.31x** | re2-longest | 0.09x | auto-nocaps | 0.176 |
| 72 | 0.0000 | redos-nested | `phone-list-nested-plus` | thr | 28.464 | rust | 86.569 | **0.33x** | pcre2-interp | 0.30x | auto-nocaps | 0.188 |
| 73 | 0.0000 | redos-nested | `phone-list-nested-plus` | srch | 902.4 | rust | 2969.7 | **0.30x** | re2 | 0.09x | auto-nocaps | 0.162 |
| 74 | 0.0000 | cap-backref | `phone-palindrome-6` | thr | 7,152,600 | onig | 14,477,787 | **0.49x** | onig | 0.49x | vm-caps | 0.492 |
| 75 | 0.0000 | cap-backref | `phone-palindrome-6` | srch | 7225.4 | pcre2-interp | 17534.1 | **0.41x** | pcre2-interp | 0.41x | vm-caps | 0.411 |
| 76 | 0.0000 | cap-lookaround | `pwd-strength-chain` | thr | 225.0 | onig | 4048.7 | **0.06x** | onig | 0.06x | auto-nocaps | 0.055 |
| 77 | 0.0000 | cap-lookaround | `pwd-strength-chain` | srch | 12402.4 | onig | 36028.0 | **0.34x** | onig | 0.34x | auto-caps | 0.344 |
| 78 | 0.0000 | semantics-divergence | `router-prefix-order` | srch | 786.2 | rust | 1313.2 | **0.60x** | onig | 0.28x | auto-nocaps | 0.591 |
| 79 | 0.0000 | binary-nonutf8 | `utf8-lead-no-cont` | thr | 481,116 | pcre2-interp | 1,017,026 | **0.47x** | pcre2-interp | 0.47x | auto-nocaps | 0.473 |
| 80 | 0.0000 | binary-nonutf8 | `utf8-lead-no-cont` | srch | 1252.2 | pcre2-interp | 3459.5 | **0.36x** | pcre2-interp | 0.36x | auto-caps | 0.401 |
| 81 | 0.0000 | wild-validator | `uuid-near-miss` | srch | 564.0 | rust | 698.3 | **0.81x** | onig | 0.20x | auto-nocaps | 0.807 |
| 82 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-array-begin` | thr | 263,768 | rust | 307,114 | **0.86x** | tre | 0.38x | auto-caps | 0.859 |
| 83 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-array-begin` | srch | 687.8 | rust | 1330.6 | **0.52x** | tre | 0.31x | auto-caps | 0.517 |
| 84 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-constant` | srch | 2455.1 | rust | 3048.9 | **0.81x** | pcre2-interp | 0.32x | auto-nocaps | 0.803 |
| 85 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-number-extended` | thr | 2,447,718 | rust | 10,611,469 | **0.23x** | pcre2-interp | 0.13x | auto-caps | 0.231 |
| 86 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-number-extended` | srch | 1410.3 | pcre2-interp | 9943.9 | **0.14x** | pcre2-interp | 0.14x | auto-caps | 0.142 |
| 87 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-object-begin` | thr | 23153.6 | pcre2-interp | 23229.7 | **1.00x** | pcre2-interp | 1.00x | auto-nocaps | 0.994 |
| 88 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-object-begin` | srch | 687.7 | rust | 1226.8 | **0.56x** | tre | 0.33x | auto-nocaps | 0.543 |
| 89 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-stringcontent-escape` | thr | 23123.6 | pcre2-interp | 23214.3 | **1.00x** | pcre2-interp | 1.00x | auto-caps | 0.996 |
| 90 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-stringcontent-escape` | srch | 747.1 | rust | 2946.6 | **0.25x** | pcre2-interp | 0.24x | auto-nocaps | 0.261 |
| 91 | 0.0000 | wild-datetime | `wild-datetime-moment-iso8601` | thr | 32.997 | pcre2-interp | 97.644 | **0.34x** | pcre2-interp | 0.34x | auto-nocaps | 0.201 |
| 92 | 0.0000 | wild-datetime | `wild-datetime-moment-iso8601` | srch | 982.2 | rust | 2043.0 | **0.48x** | pcre2-interp | 0.28x | auto-nocaps | 0.289 |
| 93 | 0.0000 | wild-logparse | `wild-logparse-base10num-grok` | thr | 4,024,235 | pcre2-interp | 19,807,036 | **0.20x** | pcre2-interp | 0.20x | auto-nocaps | 0.203 |
| 94 | 0.0000 | wild-logparse | `wild-logparse-base10num-grok` | srch | 2506.9 | pcre2-interp | 11930.5 | **0.21x** | pcre2-interp | 0.21x | auto-caps | 0.210 |
| 95 | 0.0000 | wild-logparse | `wild-logparse-base10num-noatomic` | thr | 3,983,605 | pcre2-interp | 20,669,190 | **0.19x** | pcre2-interp | 0.19x | auto-nocaps | 0.193 |
| 96 | 0.0000 | wild-logparse | `wild-logparse-base10num-noatomic` | srch | 2499.1 | pcre2-interp | 12206.0 | **0.20x** | pcre2-interp | 0.20x | auto-nocaps | 0.203 |
| 97 | 0.0000 | wild-logparse | `wild-logparse-quotedstring-grok` | thr | 1,008,829 | pcre2-interp | 2,071,041 | **0.49x** | pcre2-interp | 0.49x | auto-caps | 0.487 |
| 98 | 0.0000 | wild-logparse | `wild-logparse-quotedstring-grok` | srch | 1963.3 | pcre2-interp | 4938.3 | **0.40x** | pcre2-interp | 0.40x | auto-nocaps | 0.397 |
| 99 | 0.0000 | wild-logparse | `wild-logparse-quotedstring-noatomic` | thr | 930,344 | pcre2-interp | 2,111,987 | **0.44x** | pcre2-interp | 0.44x | auto-nocaps | 0.440 |
| 100 | 0.0000 | wild-logparse | `wild-logparse-quotedstring-noatomic` | srch | 1857.6 | onig | 290,738 | **0.01x** | onig | 0.01x | auto-nocaps | 0.124 |
| 101 | 0.0000 | wild-logparse | `wild-logparse-syslogbase-expanded` | thr | 3,992,451 | onig | 69,561,406 | **0.06x** | onig | 0.06x | auto-nocaps | 0.132 |
| 102 | 0.0000 | wild-logparse | `wild-logparse-syslogbase-expanded` | srch | 3769.0 | pcre2-interp | 9134.1 | **0.41x** | pcre2-interp | 0.41x | auto-nocaps | 0.502 |
| 103 | 0.0000 | wild-logparse | `wild-logparse-winpath-grok` | srch | 2644.9 | pcre2-interp | 3989.4 | **0.66x** | pcre2-interp | 0.66x | auto-nocaps | 0.663 |
| 104 | 0.0000 | wild-secrets | `wild-secrets-slack-webhook-url` | thr | 341,200 | re2-longest | 439,089 | **0.78x** | re2-longest | 0.78x | auto-nocaps | 0.770 |
| 105 | 0.0000 | wild-secrets | `wild-secrets-slack-webhook-url` | srch | 1305.8 | rust | 2558.6 | **0.51x** | onig | 0.39x | auto-nocaps | 0.363 |
| 106 | 0.0000 | wild-secrets | `wild-secrets-username-password-pair` | srch | 1863.3 | rust | 2478.7 | **0.75x** | pcre2-interp | 0.38x | auto-nocaps | 0.555 |
| 107 | 0.0000 | semantics-divergence | `wild-semdiv-altorder-foo-foobar-rustregex` | srch | 715.3 | rust | 1343.0 | **0.53x** | onig | 0.24x | auto-caps | 0.533 |
| 108 | 0.0000 | semantics-divergence | `wild-semdiv-dollar-trailing-newline-pcre2` | srch | 1189.4 | rust | 1594.0 | **0.75x** | onig | 0.34x | auto-nocaps | 0.746 |
| 109 | 0.0000 | semantics-divergence | `wild-semdiv-empty-alt-repeat-pcre2` | thr | 7,018,277 | rust | 13,152,404 | **0.53x** | pcre2-interp | 0.15x | auto-nocaps | 0.290 |
| 110 | 0.0000 | semantics-divergence | `wild-semdiv-empty-alt-repeat-pcre2` | srch | 2901.3 | rust | 13254.3 | **0.22x** | onig | 0.17x | auto-nocaps | 0.093 |
| 111 | 0.0000 | wild-validator | `wild-validator-email-owasp` | thr | 40.350 | rust | 107.8 | **0.37x** | re2 | 0.11x | auto-nocaps | 0.367 |
| 112 | 0.0000 | wild-validator | `wild-validator-email-owasp` | srch | 1072.0 | rust | 2580.3 | **0.42x** | onig | 0.21x | auto-nocaps | 0.412 |
| 113 | 0.0000 | wild-validator | `wild-validator-ipv4-owasp` | srch | 870.5 | rust | 1254.0 | **0.69x** | pcre2-interp | 0.27x | auto-nocaps | 0.397 |
| 114 | 0.0000 | wild-validator | `wild-validator-us-zip-owasp` | srch | 808.1 | rust | 1669.7 | **0.48x** | re2 | 0.40x | auto-nocaps | 0.290 |
| 115 | 0.0000 | wild-validator | `wild-validator-uuid-grok` | thr | 82561.3 | rust | 210,621 | **0.39x** | re2-longest | 0.04x | auto-nocaps | 0.392 |
| 116 | 0.0000 | wild-validator | `wild-validator-uuid-grok` | srch | 716.2 | rust | 1240.8 | **0.58x** | pcre2-interp | 0.24x | auto-caps | 0.577 |
| 117 | 0.0000 | wild-waf | `wild-waf-crs-942140-dbnames` | srch | 2713.5 | rust | 4408.0 | **0.62x** | re2 | 0.28x | auto-nocaps | 0.614 |
| 118 | 0.0000 | wild-waf | `wild-waf-crs-942160-sleep-benchmark` | srch | 1305.4 | rust | 3205.0 | **0.41x** | pcre2-interp | 0.36x | auto-nocaps | 0.409 |
| 119 | 0.0000 | wild-waf | `wild-waf-crs-942270-union-select` | srch | 1150.5 | rust | 2127.7 | **0.54x** | pcre2-interp | 0.22x | auto-nocaps | 0.540 |
| 120 | 0.0000 | wild-waf | `wild-waf-crs-942500-comment-obfuscation` | thr | 23121.0 | rust | 41251.6 | **0.56x** | re2 | 0.05x | auto-caps | 0.560 |
| 121 | 0.0000 | wild-waf | `wild-waf-crs-942500-comment-obfuscation` | srch | 736.3 | rust | 2422.4 | **0.30x** | pcre2-interp | 0.22x | auto-caps | 0.304 |
| 122 | 0.0000 | wild-logparse | `winpath-near-miss` | thr | 20.100 | onig | 94.067 | **0.21x** | onig | 0.21x | auto-caps | 0.214 |
| 123 | 0.0000 | wild-logparse | `winpath-near-miss` | srch | 500.7 | rust | 1796.4 | **0.28x** | onig | 0.17x | auto-nocaps | 0.278 |
| - | - | wild-datetime | `wild-datetime-datefinder-alternation` | thr | **no data — auto-caps does not compile** ([OPTLOOP.1.analysis] §1.2: 670,153/665,144 bytes > the 500,000-byte code cap; only `auto-nocaps` compiles) | - | - | - | - | - | - | - |
| - | - | wild-datetime | `wild-datetime-datefinder-alternation` | srch | **no data — auto-caps does not compile** ([OPTLOOP.1.analysis] §1.2: 670,153/665,144 bytes > the 500,000-byte code cap; only `auto-nocaps` compiles) | - | - | - | - | - | - | - |

Two cells carry no number at all: `auto-caps` refuses to compile
`wild-datetime-datefinder-alternation` on EITHER regime (`cycle1_analysis.md`
§1.2: 670,153/665,144 emitted bytes against the 500,000-byte code cap; only
`--no-captures` compiles, at 20,432 bytes). This is the sharpest possible
form of "apples to apples" hiding a problem: the best-variant ranking
reports this pattern as a routine 0.30×/0.02× WIN (rows 88/125 in §1) because
`auto-nocaps` answers it, but the shipped default cannot produce an artifact
for this pattern at all.

---

## 2. The NOCAPS table — pcrec `auto-nocaps` against no-capture engines

Smaller, and mostly for completeness, per the brief. Competitor set:
`pcre2-dfa` only — `vectorscan` is excluded as a target per §0 rule 2 (a
SIMD-first, multi-pattern streaming automaton reporting `nosom`/`nocaps`,
no scalar mechanism to mine), which leaves `pcre2-dfa` as the ONLY
algorithmic nocaps-vs-nocaps target in the whole roster. 15 of the 125 cells
carry no `pcre2-dfa` number at all (below the table); the bench's own `st`
status per cell (`rank.json`) accounts for all 15 — 10 are `unsup`
(`cap-backref`/`cap-recursion` rows: PCRE2's DFA algorithm does not
implement backreferences or recursion, declared up front) and 4 are
`wrong`/`gave-up` on `short-subject-search` cells in unrelated families
(`file-ext-order`, `keyword-prefix-order`, `router-prefix-order`,
`wild-logparse-quotedstring-grok` — `wrong`; `tag-depth3-bound` —
`gave-up`), a different exclusion reason this memo does not investigate
further.

| # | score | family | pattern | regime | auto-nocaps ns | pcre2-dfa ns | ratio |
|---|---|---|---|---|---|---|---|
| 1 | 1.7422 | cap-recursion | `bracket-array-define` | thr | 4,879,528 | 311.0 | **15691.17x** |
| 2 | 0.9569 | cap-recursion | `tag-depth3-bound` | thr | 4,687,862 | 23252.4 | **201.61x** |
| 3 | 0.7233 | wild-secrets | `wild-secrets-username-password-pair` | thr | 1,287,800 | 23326.7 | **55.21x** |
| 4 | 0.5387 | wild-secrets | `wild-secrets-aws-access-key-id` | thr | 4,201,043 | 211,882 | **19.83x** |
| 5 | 0.3608 | wild-logparse | `wild-logparse-winpath-grok` | thr | 3,468,811 | 23338.3 | **148.63x** |
| 6 | 0.2364 | cap-recursion | `nested-comment-rec` | thr | 7,809,448 | 2,105,601 | **3.71x** |
| 7 | 0.0628 | cap-recursion | `balanced-parens-rec` | srch | 6494.1 | 4585.5 | **1.42x** |
| 8 | 0.0530 | cap-recursion | `nested-comment-rec` | srch | 9306.4 | 6937.2 | **1.34x** |
| 9 | 0.0275 | cap-recursion | `balanced-parens-rec` | thr | 5,481,441 | 4,705,333 | **1.16x** |
| 10 | 0.0051 | cap-lookaround | `currency-lookbehind-fixed` | thr | 11,205,442 | 10,819,261 | **1.04x** |
| 11 | 0.0000 | wild-logparse | `base10num-near-miss` | thr | 16.900 | 80.872 | **0.21x** |
| 12 | 0.0000 | wild-logparse | `base10num-near-miss` | srch | 552.0 | 4930.3 | **0.11x** |
| 13 | 0.0000 | cap-recursion | `bracket-array-define` | srch | 6882.2 | 8881.9 | **0.77x** |
| 14 | 0.0000 | wild-codegrammar | `codegrammar-flat` | thr | 629,144 | 15,415,828 | **0.04x** |
| 15 | 0.0000 | wild-codegrammar | `codegrammar-flat` | srch | 723.9 | 2456.6 | **0.29x** |
| 16 | 0.0000 | wild-codegrammar | `codegrammar-xflag` | thr | 646,060 | 14,814,923 | **0.04x** |
| 17 | 0.0000 | wild-codegrammar | `codegrammar-xflag` | srch | 724.9 | 2477.8 | **0.29x** |
| 18 | 0.0000 | cap-lookaround | `currency-lookbehind-fixed` | srch | 5162.3 | 15324.1 | **0.34x** |
| 19 | 0.0000 | redos-nested | `date-nested-plus` | thr | 16.100 | 103.2 | **0.16x** |
| 20 | 0.0000 | redos-nested | `date-nested-plus` | srch | 490.9 | 4237.3 | **0.12x** |
| 21 | 0.0000 | cap-lookaround | `email-local-nodup` | thr | 980.9 | 3885.4 | **0.25x** |
| 22 | 0.0000 | cap-lookaround | `email-local-nodup` | srch | 10607.1 | 42500.9 | **0.25x** |
| 23 | 0.0000 | redos-nested | `email-nested-plus` | thr | 32.700 | 2525.9 | **0.01x** |
| 24 | 0.0000 | redos-nested | `email-nested-plus` | srch | 975.5 | 8804.8 | **0.11x** |
| 25 | 0.0000 | redos-nested | `evil-alt-nested` | thr | 27.300 | 1581.5 | **0.02x** |
| 26 | 0.0000 | semantics-divergence | `file-ext-order` | thr | 292,629 | 1,134,876 | **0.26x** |
| 27 | 0.0000 | cap-lookaround | `float-literal-bound` | thr | 1,788,993 | 18,611,392 | **0.10x** |
| 28 | 0.0000 | cap-lookaround | `float-literal-bound` | srch | 2483.2 | 5858.8 | **0.42x** |
| 29 | 0.0000 | floor | `floor-byte` | thr | 23139.2 | 23242.8 | **1.00x** |
| 30 | 0.0000 | floor | `floor-byte` | srch | 665.2 | 2277.4 | **0.29x** |
| 31 | 0.0000 | binary-nonutf8 | `high-byte-run` | thr | 483,136 | 1,012,634 | **0.48x** |
| 32 | 0.0000 | binary-nonutf8 | `high-byte-run` | srch | 1105.3 | 3272.3 | **0.34x** |
| 33 | 0.0000 | wild-validator | `ipv4-near-miss` | thr | 18.692 | 81.597 | **0.23x** |
| 34 | 0.0000 | wild-validator | `ipv4-near-miss` | srch | 494.1 | 2742.2 | **0.18x** |
| 35 | 0.0000 | semantics-divergence | `keyword-prefix-order` | thr | 730,992 | 3,142,701 | **0.23x** |
| 36 | 0.0000 | wild-logparse | `logparse-atomic` | thr | 31.421 | 245.6 | **0.13x** |
| 37 | 0.0000 | wild-logparse | `logparse-atomic` | srch | 837.3 | 5240.1 | **0.16x** |
| 38 | 0.0000 | wild-logparse | `logparse-atomic-removed` | thr | 18.700 | 193.7 | **0.10x** |
| 39 | 0.0000 | wild-logparse | `logparse-atomic-removed` | srch | 492.7 | 4582.1 | **0.11x** |
| 40 | 0.0000 | binary-nonutf8 | `mojibake-curly-quote` | thr | 23119.1 | 23264.9 | **0.99x** |
| 41 | 0.0000 | binary-nonutf8 | `mojibake-curly-quote` | srch | 683.2 | 2857.4 | **0.24x** |
| 42 | 0.0000 | redos-nested | `numeric-id-nested-plus` | thr | 15.200 | 80.311 | **0.19x** |
| 43 | 0.0000 | redos-nested | `numeric-id-nested-plus` | srch | 470.7 | 13240.3 | **0.04x** |
| 44 | 0.0000 | redos-nested | `phone-list-nested-plus` | thr | 15.200 | 80.795 | **0.19x** |
| 45 | 0.0000 | redos-nested | `phone-list-nested-plus` | srch | 480.6 | 15202.5 | **0.03x** |
| 46 | 0.0000 | cap-lookaround | `pwd-strength-chain` | thr | 222.2 | 12107.0 | **0.02x** |
| 47 | 0.0000 | cap-lookaround | `pwd-strength-chain` | srch | 12651.4 | 95501.1 | **0.13x** |
| 48 | 0.0000 | semantics-divergence | `router-prefix-order` | thr | 393,773 | 2,182,506 | **0.18x** |
| 49 | 0.0000 | redos-nested | `trim-nested-star` | thr | 15.200 | 252.9 | **0.06x** |
| 50 | 0.0000 | redos-nested | `trim-nested-star` | srch | 427.7 | 13637.6 | **0.03x** |
| 51 | 0.0000 | binary-nonutf8 | `utf8-lead-no-cont` | thr | 481,068 | 1,017,211 | **0.47x** |
| 52 | 0.0000 | binary-nonutf8 | `utf8-lead-no-cont` | srch | 1253.5 | 3120.4 | **0.40x** |
| 53 | 0.0000 | wild-validator | `uuid-near-miss` | thr | 19.988 | 168.0 | **0.12x** |
| 54 | 0.0000 | wild-validator | `uuid-near-miss` | srch | 563.2 | 3168.7 | **0.18x** |
| 55 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-array-begin` | thr | 263,785 | 770,479 | **0.34x** |
| 56 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-array-begin` | srch | 709.5 | 2396.8 | **0.30x** |
| 57 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-constant` | thr | 4,199,248 | 6,207,306 | **0.68x** |
| 58 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-constant` | srch | 2449.5 | 7078.2 | **0.35x** |
| 59 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-number-extended` | thr | 2,448,299 | 21,848,582 | **0.11x** |
| 60 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-number-extended` | srch | 1417.6 | 12446.2 | **0.11x** |
| 61 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-object-begin` | thr | 23090.6 | 23287.6 | **0.99x** |
| 62 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-object-begin` | srch | 665.9 | 2290.1 | **0.29x** |
| 63 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-stringcontent-escape` | thr | 23131.3 | 23343.9 | **0.99x** |
| 64 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-stringcontent-escape` | srch | 741.8 | 2838.8 | **0.26x** |
| 65 | 0.0000 | wild-datetime | `wild-datetime-datefinder-alternation` | thr | 10,423,601 | 10,045,930,900 | **0.00x** |
| 66 | 0.0000 | wild-datetime | `wild-datetime-datefinder-alternation` | srch | 2010.0 | 3,958,473 | **0.00x** |
| 67 | 0.0000 | wild-datetime | `wild-datetime-moment-iso8601` | thr | 19.600 | 116.4 | **0.17x** |
| 68 | 0.0000 | wild-datetime | `wild-datetime-moment-iso8601` | srch | 589.8 | 3794.8 | **0.16x** |
| 69 | 0.0000 | wild-logparse | `wild-logparse-base10num-grok` | thr | 4,024,030 | 27,306,141 | **0.15x** |
| 70 | 0.0000 | wild-logparse | `wild-logparse-base10num-grok` | srch | 2515.7 | 16435.1 | **0.15x** |
| 71 | 0.0000 | wild-logparse | `wild-logparse-base10num-noatomic` | thr | 3,983,530 | 22,242,282 | **0.18x** |
| 72 | 0.0000 | wild-logparse | `wild-logparse-base10num-noatomic` | srch | 2474.9 | 13874.2 | **0.18x** |
| 73 | 0.0000 | wild-logparse | `wild-logparse-quotedstring-grok` | thr | 1,008,867 | 3,853,301 | **0.26x** |
| 74 | 0.0000 | wild-logparse | `wild-logparse-quotedstring-noatomic` | thr | 929,843 | 8,795,923 | **0.11x** |
| 75 | 0.0000 | wild-logparse | `wild-logparse-quotedstring-noatomic` | srch | 1855.0 | 14951.9 | **0.12x** |
| 76 | 0.0000 | wild-logparse | `wild-logparse-syslogbase-expanded` | thr | 3,988,287 | 30,190,617 | **0.13x** |
| 77 | 0.0000 | wild-logparse | `wild-logparse-syslogbase-expanded` | srch | 3583.6 | 7132.2 | **0.50x** |
| 78 | 0.0000 | wild-logparse | `wild-logparse-winpath-grok` | srch | 2643.9 | 5810.3 | **0.46x** |
| 79 | 0.0000 | wild-secrets | `wild-secrets-aws-access-key-id` | srch | 2468.3 | 4262.8 | **0.58x** |
| 80 | 0.0000 | wild-secrets | `wild-secrets-github-pat` | thr | 124,369 | 1,043,730 | **0.12x** |
| 81 | 0.0000 | wild-secrets | `wild-secrets-github-pat` | srch | 1371.5 | 3377.1 | **0.41x** |
| 82 | 0.0000 | wild-secrets | `wild-secrets-slack-webhook-url` | thr | 338,263 | 1,846,587 | **0.18x** |
| 83 | 0.0000 | wild-secrets | `wild-secrets-slack-webhook-url` | srch | 927.9 | 3956.5 | **0.23x** |
| 84 | 0.0000 | wild-secrets | `wild-secrets-username-password-pair` | srch | 1376.1 | 3835.9 | **0.36x** |
| 85 | 0.0000 | semantics-divergence | `wild-semdiv-altorder-foo-foobar-rustregex` | thr | 410,777 | 1,586,699 | **0.26x** |
| 86 | 0.0000 | semantics-divergence | `wild-semdiv-altorder-foo-foobar-rustregex` | srch | 716.2 | 3072.3 | **0.23x** |
| 87 | 0.0000 | semantics-divergence | `wild-semdiv-dollar-trailing-newline-pcre2` | thr | 109,785 | 2,608,091 | **0.04x** |
| 88 | 0.0000 | semantics-divergence | `wild-semdiv-dollar-trailing-newline-pcre2` | srch | 1188.7 | 3546.2 | **0.34x** |
| 89 | 0.0000 | semantics-divergence | `wild-semdiv-empty-alt-repeat-pcre2` | thr | 3,812,624 | 28,157,478 | **0.14x** |
| 90 | 0.0000 | semantics-divergence | `wild-semdiv-empty-alt-repeat-pcre2` | srch | 1238.2 | 119,947 | **0.01x** |
| 91 | 0.0000 | wild-validator | `wild-validator-email-owasp` | thr | 39.600 | 695.0 | **0.06x** |
| 92 | 0.0000 | wild-validator | `wild-validator-email-owasp` | srch | 1063.7 | 7240.4 | **0.15x** |
| 93 | 0.0000 | wild-validator | `wild-validator-ipv4-owasp` | thr | 18.678 | 82.036 | **0.23x** |
| 94 | 0.0000 | wild-validator | `wild-validator-ipv4-owasp` | srch | 497.9 | 2706.1 | **0.18x** |
| 95 | 0.0000 | wild-validator | `wild-validator-us-zip-owasp` | thr | 17.800 | 80.592 | **0.22x** |
| 96 | 0.0000 | wild-validator | `wild-validator-us-zip-owasp` | srch | 485.0 | 3353.7 | **0.14x** |
| 97 | 0.0000 | wild-validator | `wild-validator-uuid-grok` | thr | 82557.9 | 28,647,235 | **0.00x** |
| 98 | 0.0000 | wild-validator | `wild-validator-uuid-grok` | srch | 717.9 | 3409.4 | **0.21x** |
| 99 | 0.0000 | wild-waf | `wild-waf-crs-942140-dbnames` | thr | 4,099,501 | 23,532,098 | **0.17x** |
| 100 | 0.0000 | wild-waf | `wild-waf-crs-942140-dbnames` | srch | 2707.4 | 16470.1 | **0.16x** |
| 101 | 0.0000 | wild-waf | `wild-waf-crs-942160-sleep-benchmark` | thr | 1,272,714 | 5,570,650 | **0.23x** |
| 102 | 0.0000 | wild-waf | `wild-waf-crs-942160-sleep-benchmark` | srch | 1301.1 | 3182.7 | **0.41x** |
| 103 | 0.0000 | wild-waf | `wild-waf-crs-942270-union-select` | thr | 998,851 | 2,440,750 | **0.41x** |
| 104 | 0.0000 | wild-waf | `wild-waf-crs-942270-union-select` | srch | 1148.8 | 4769.3 | **0.24x** |
| 105 | 0.0000 | wild-waf | `wild-waf-crs-942360-concat-sqli` | thr | 12,239,877 | 227,773,602 | **0.05x** |
| 106 | 0.0000 | wild-waf | `wild-waf-crs-942360-concat-sqli` | srch | 7417.0 | 182,782 | **0.04x** |
| 107 | 0.0000 | wild-waf | `wild-waf-crs-942500-comment-obfuscation` | thr | 23179.7 | 1,949,360 | **0.01x** |
| 108 | 0.0000 | wild-waf | `wild-waf-crs-942500-comment-obfuscation` | srch | 750.1 | 3237.2 | **0.23x** |
| 109 | 0.0000 | wild-logparse | `winpath-near-miss` | thr | 20.209 | 264.6 | **0.08x** |
| 110 | 0.0000 | wild-logparse | `winpath-near-miss` | srch | 499.9 | 5444.9 | **0.09x** |

**Cells with no `pcre2-dfa` target (15):**

| pattern | regime | family | `pcre2-dfa` status |
|---|---|---|---|
| `doubled-word` | thr | cap-backref | `unsup` |
| `doubled-word` | srch | cap-backref | `unsup` |
| `dup-param-detect` | thr | cap-backref | `unsup` |
| `dup-param-detect` | srch | cap-backref | `unsup` |
| `file-ext-order` | srch | semantics-divergence | `wrong` |
| `keyword-prefix-order` | srch | semantics-divergence | `wrong` |
| `phone-palindrome-6` | thr | cap-backref | `unsup` |
| `phone-palindrome-6` | srch | cap-backref | `unsup` |
| `quoted-delim-match` | thr | cap-backref | `unsup` |
| `quoted-delim-match` | srch | cap-backref | `unsup` |
| `router-prefix-order` | srch | semantics-divergence | `wrong` |
| `tag-depth3-bound` | srch | cap-recursion | `gave-up` |
| `tag-pair-match` | thr | cap-backref | `unsup` |
| `tag-pair-match` | srch | cap-backref | `unsup` |
| `wild-logparse-quotedstring-grok` | srch | wild-logparse | `wrong` |

---

## 3. The DELTA table — rows §1 called a WIN that the caps view calls a LOSS

Every row where `cycle1_analysis.md`'s own best-of-four ranking scored ZERO
(`auto-nocaps` won the row outright, ratio ≤ 1, §1's "pcrec wins" bucket)
but where forcing the SHIPPED default (`auto-caps`) loses to a capture
engine (this memo's §1 ratio > 1). **5 rows**, not 3: §1.1 already named the
three sharpest ({evil-alt-nested thr, trim-nested-star thr, trim-nested-star
srch}, its own "sharpest default-config cells in the whole matrix"
paragraph) but did not attempt an exhaustive sweep of the boundary
`ratio > 1.0` case — two more cross it, both by a narrow margin
(`wild-validator-us-zip-owasp` thr at 1.67×, `wild-secrets-github-pat` srch
at 1.01×, i.e. right at the line). `RX_ENGINE`/`RX_ENGINE_SEL`/`RX_ENGINE_WHY`
are the `auto-caps` artifact's own stamps, read from `stamps.json` (no
recompile — the stamp was already on file for all five).

| family | pattern | regime | auto-caps ns | auto-nocaps ns | best capture engine | best-cap ns | ratio (auto-caps / best-cap) | `RX_ENGINE` | `RX_ENGINE_SEL` | `RX_ENGINE_WHY` |
|---|---|---|---|---|---|---|---|---|---|---|
| redos-nested | `evil-alt-nested` | thr | 4,305,649 | 27.300 | rust | 87.841 | **49016.29x** | `vm` | `declined-nullable-default` | `capture group at pattern offset 1` |
| redos-nested | `trim-nested-star` | thr | 3,248,263 | 15.200 | rust | 82.346 | **39446.71x** | `vm` | `declined-nullable-default` | `capture group at pattern offset 1` |
| redos-nested | `trim-nested-star` | srch | 8,970,875 | 427.7 | rust | 1993.0 | **4501.17x** | `vm` | `declined-nullable-default` | `capture group at pattern offset 1` |
| wild-validator | `wild-validator-us-zip-owasp` | thr | 30.205 | 17.800 | rust | 18.084 | **1.67x** | `vm` | `selected` | `capture group at pattern offset 6` |
| wild-secrets | `wild-secrets-github-pat` | srch | 1701.6 | 1371.5 | rust | 1683.6 | **1.01x** | `vm` | `selected` | `capture group at pattern offset 2` |

`declined-nullable-default` on the two `redos-nested` rows is
`f2_rescue_split.md`'s own finding, cited here rather than re-derived: the
`^`-anchored nullable-quantifier prefilter rescue is unreachable once
captures route the pattern to the VM, for reasons unrelated to WHERE the
capture sits in the pattern. The other three read `selected`/`forced` — an
ordinary engine-selection outcome, not a decline.

---

## 4. The five mechanisms, re-scored under the caps view

Each of §3's five mechanisms (`M1`–`M5`) is restated here using the SAME
named rows, but with each row's pcrec side pinned to `auto-caps` (never the
best-of-four figure) and its competitor restricted to this memo's §1 set
(capture engines only — relevant only where a row's original target was
`pcre2-dfa`, which none of these 14 rows' targets are). This is the
apples-to-apples question the mechanisms themselves must survive: were they
mined from a comparison that only looked fast because a no-captures variant
was doing the running?

| mechanism | §3 score (best-variant) | caps-view score | delta | rows |
|---|---|---|---|---|
| M1 [OPT-REQBYTE] | 3.714 | 3.7170 | +0.0030 | 5 |
| M2 [OPT-ANCHOR-VM] | 2.112 | 2.1124 | +0.0004 | 2 |
| M3 [OPT-FIRSTSET] | 1.002 | 1.0204 | +0.0184 | 4 |
| M4 [OPT-ENDWIN] | 0.871 | 0.8710 | +0.0000 | 1 |
| M5 [OPT-ATTEMPT-SPLIT] | 0.306 | 0.3052 | -0.0008 | 2 |
| **sum** | **8.005** | **8.0260** | **+0.0210** | 14 |

**Verdict: robust.** All five mechanisms move by under 2% of their own
score (`M3` moves the most, +1.8%, because three of its four rows —
`wild-secrets-aws-access-key-id` thr, `wild-codegrammar-json-constant` thr,
`wild-waf-crs-942140-dbnames` thr — already ran `auto-caps` in §1, and the
scalar-caps restriction to capture-only engines does not change which
engine is fastest on any of the four). None of
M1–M5 was an artifact of comparing a no-captures pcrec build against
capture-bearing competitors — restated in their OWN §3 form (a required-byte
pre-check, a VM start bound, a first-byte set derived from the AST, an
end-anchor window, and the `^`-on-some-branches DFA toolkit loss), each
mechanism is exactly as large under `auto-caps` alone as it was under the
best-of-four figure.

### The new population — caps losses no §3 mechanism explains

25 of the caps table's 39 losing rows are not one of M1–M5's 14 named rows.
Total weighted score **6.0106**, against **8.0260** for the five named
mechanisms and **14.0366** for the whole caps-losing population — so the
caps view's total losing score (14.04) is bigger than §1's original 10.284
(the captures-only competitor restriction removes some rows' access to a
`pcre2-dfa` target that was carrying them, and several `auto-nocaps`-best
rows now score for the first time), and 43% of it (6.01 of 14.04) is
un-mined. Bucketed by the `auto-caps` artifact's own `RX_ENGINE_WHY` stamp:


**`RX_ENGINE_WHY` = "capture group"** — 14 rows, weighted score 4.6833

| pattern | regime | caps-vs-best-cap-engine ratio | score | caps ÷ nocaps (the cost of captures) | best capture engine |
|---|---|---|---|---|---|
| `evil-alt-nested` | thr | 49016.29x | 1.2984 | 157716.09x | rust |
| `trim-nested-star` | thr | 39446.71x | 1.2723 | 213701.49x | rust |
| `trim-nested-star` | srch | 4501.17x | 1.0113 | 20974.69x | rust |
| `nested-comment-rec` | thr | 5.21x | 0.2976 | 1.00x | onig |
| `wild-secrets-github-pat` | thr | 2.66x | 0.1765 | 1.00x | rust |
| `quoted-delim-match` | thr | 2.63x | 0.1397 | 1.03x | onig |
| `nested-comment-rec` | srch | 2.09x | 0.1328 | 1.00x | onig |
| `dup-param-detect` | srch | 1.87x | 0.0906 | 1.00x | pcre2-interp |
| `wild-validator-ipv4-owasp` | thr | 1.79x | 0.0698 | 1.71x | rust |
| `wild-validator-us-zip-owasp` | thr | 1.67x | 0.0617 | 1.70x | rust |
| `quoted-delim-match` | srch | 1.60x | 0.0679 | 1.02x | onig |
| `tag-pair-match` | srch | 1.39x | 0.0472 | 0.98x | pcre2-interp |
| `tag-depth3-bound` | srch | 1.09x | 0.0156 | 1.02x | onig |
| `wild-secrets-github-pat` | srch | 1.01x | 0.0019 | 1.24x | rust |

**`RX_ENGINE_WHY` = "engine=dfa, no WHY stamp (not VM-forced by a construct)"** — 8 rows, weighted score 1.0931

| pattern | regime | caps-vs-best-cap-engine ratio | score | caps ÷ nocaps (the cost of captures) | best capture engine |
|---|---|---|---|---|---|
| `router-prefix-order` | thr | 6.54x | 0.2258 | 1.00x | rust |
| `file-ext-order` | thr | 6.30x | 0.2213 | 1.00x | rust |
| `wild-semdiv-altorder-foo-foobar-rustregex` | thr | 4.98x | 0.1931 | 1.00x | rust |
| `wild-waf-crs-942270-union-select` | thr | 3.56x | 0.1833 | 1.00x | rust |
| `wild-waf-crs-942160-sleep-benchmark` | thr | 3.27x | 0.1708 | 1.00x | rust |
| `keyword-prefix-order` | thr | 2.00x | 0.0832 | 1.00x | rust |
| `uuid-near-miss` | thr | 1.10x | 0.0116 | 1.00x | rust |
| `ipv4-near-miss` | thr | 1.03x | 0.0040 | 1.00x | rust |

**`RX_ENGINE_WHY` = "(\?R)"** — 2 rows, weighted score 0.2123

| pattern | regime | caps-vs-best-cap-engine ratio | score | caps ÷ nocaps (the cost of captures) | best capture engine |
|---|---|---|---|---|---|
| `balanced-parens-rec` | thr | 1.89x | 0.1147 | 1.00x | pcre2-interp |
| `balanced-parens-rec` | srch | 1.72x | 0.0976 | 1.02x | pcre2-interp |

**`RX_ENGINE_WHY` = "(\?<=...)"** — 1 row, weighted score 0.0220

| pattern | regime | caps-vs-best-cap-engine ratio | score | caps ÷ nocaps (the cost of captures) | best capture engine |
|---|---|---|---|---|---|
| `currency-lookbehind-fixed` | thr | 1.16x | 0.0220 | 1.00x | onig |

**The `capture group` bucket is the dominant one**, as expected: 14 rows,
weighted score 4.6833 (78% of the new population's total, 33% of the WHOLE
caps-losing population). This is the population the manager's separate
captures-mechanism survey should measure against. Two things inside it are
worth separating before that survey starts, both readable straight off the
`caps ÷ nocaps` column above (never diagnosed further here, per this memo's
own no-new-mechanisms rule):

- **Three rows carry almost the entire population's weight and a
  caps-vs-nocaps factor over 20,000×** (`evil-alt-nested` thr 157,716×,
  `trim-nested-star` thr 213,701×, `trim-nested-star` srch 20,975×) — these
  are exactly §1.1's own three default-config cells, restated here with
  their actual captures-on/captures-off ratio rather than the "default ÷
  best" framing §1.1 used.
- **Eleven rows carry a caps-vs-nocaps factor of 0.98×–1.71×** — captures
  cost little to nothing on these. `RX_ENGINE_WHY` names "capture group" as
  the reason for all eleven, but `rank.json`'s own `requires` field splits
  them: five (`dup-param-detect` srch, `tag-pair-match` srch,
  `tag-depth3-bound` srch — `backrefs`; `nested-comment-rec` both regimes —
  `lookaround`) declare a SECOND module need the stamp does not name as
  primary, so the VM route was very likely unavoidable on these regardless
  of captures; `quoted-delim-match` (both regimes, `lookaround`) is the same
  shape. The other three — `wild-secrets-github-pat` (both regimes),
  `wild-validator-ipv4-owasp` thr, `wild-validator-us-zip-owasp` thr —
  declare NO second module (`requires` is empty): "capture group" is the
  WHOLE reason on these, yet captures still cost near-nothing
  (0.98×–1.71×), which is itself worth a line in the captures survey.
  Separating "costs 20,000×" from "costs ~1×" (whether or not a second
  module masks the reason) is exactly the distinction a captures-cost
  mechanism population needs and exactly what this memo does NOT resolve
  further (no diagnosis beyond the stamp).

**The `engine=dfa` bucket (8 rows, score 1.0931) is NOT a captures-cost
population at all** — every row in it reads `caps ÷ nocaps ≈ 1.00×`, meaning
`auto-caps` and `auto-nocaps` pick the identical DFA artifact and captures
cost nothing. This bucket is `cycle1_analysis.md` §2.3(j)'s own
SIMD-deferral population (pcrec's scalar DFA already beats every non-`rust`
capture engine; only `rust`'s vectorized prefilter is ahead) reappearing
here because it happens to also lose against the narrower capture-only
competitor set — not a new finding, and explicitly NOT part of the captures
survey's population.

**The two remaining buckets** (`(?R)`, 2 rows, `balanced-parens-rec`;
`(?<=...)`, 1 row, `currency-lookbehind-fixed`) also read `caps ÷ nocaps
≈ 1.00–1.02×` — recursion and lookbehind force the VM regardless of
captures, so these are not captures-cost rows either, despite losing in
this captures-only view.

---

## 5. Totals

| view | scorable cells | pcrec wins/ties | pcrec loses | no-data cells |
|---|---|---|---|---|
| §1 CAPS (`auto-caps` vs. capture engines) | 123 | 84 | 39 | 2 |
| §2 NOCAPS (`auto-nocaps` vs. `pcre2-dfa`) | 110 | 100 | 10 | 15 |

Against `cycle1_analysis.md` §1's headline (best-of-four pcrec: fastest or
tied on 91 of 125 ranked cells, 72.8%): the shipped default alone wins or
ties **84 of 123** scorable captures-on
cells (68.3%) against capture-bearing competitors, and **100
of 110** scorable captures-off cells (90.9%) against the one
algorithmic nocaps competitor that exists. Five rows (§3) flip from WIN to
LOSS outright, and the `capture group` population (§4, 14 rows, score
4.6833) is the largest single chunk of losing score in the whole matrix that
no named mechanism yet explains.

**What the best-variant ranking hid, honestly stated.** §1's ranking answers
"can pcrec do this pattern at all, at its best" — a fair question, and
`cycle1_analysis.md` §1.1 already flagged that it is not the shipped
default's number for three cells. This memo shows the gap is wider than
three cells, though most of it does not flip the verdict: `auto-nocaps` was
the variant carrying **65 of the 91** win/tie rows in §1's own headline
number — the majority of it — and of those 65, **58 still win or tie**
when the comparison is forced onto `auto-caps` against capture engines only
(§1 above). The other **5 flip from WIN to LOSS outright** (§3's delta
table), and **1 more pattern** (`wild-datetime-datefinder-alternation`)
was never a genuine win at all — the shipped default cannot produce an
artifact for it. So the best-variant framing was not systematically
misleading on the win/lose VERDICT, but it was silent on MAGNITUDE and on
one compile failure, and it structurally could not surface the `capture
group` population (§4, 14 rows, score 4.6833) — the largest un-mined chunk
of losing score in the whole matrix — because every one of those rows
already had a captures-off number to report instead, so none of them was
ever counted as a loss anywhere in §1. §3's five mechanisms are unaffected:
they are equally real, to within 2%, under `auto-caps` alone (§4's table).
