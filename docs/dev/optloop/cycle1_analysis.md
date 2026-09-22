# [OPTLOOP.1.analysis] — cycle 1 of the optimization loop (D119), on `capability@0.1`

Lane `optrev`, 2026-09-22, branch `lane/optrev` from `ab341bfe`.
Analysis only: nothing under `src/`, `cli/`, `lib/` or `tests/`; nothing
written in `/Users/fdicostanzo/pcrec-bench` (read-only reference).

**Sources.** The bench reports
`/Users/fdicostanzo/pcrec-bench/reports/2026-09-20-capability-0.1-budu-ryzen1600-{pinconfirm,fullroster}-25b1984f.*`
(matrix, subject-grain and interpretation surfaces), the set's own
`bench/capability/{NOTES.md,patterns.rxt,manifest*.tsv,gen_throughput_subjects.py,captext.py}`,
and this worktree's `build/pcrec` (`ab341bfe`, `abi` 28) compiling all 64
patterns at the bench's own three flag sets. **No timing was taken on this
box** — every number below is the bench's Ryzen 1600 measurement or a
structural fact read off emitted C, a `pcre2_pattern_info` query, or a byte
census of the subjects. Every owed measurement is named in §3 as an exact
command list for the Linux executor.

Reproduction pieces live beside this file (`CLAUDE.md` names them);
the machine-readable ranked table is `cycle1_rows.tsv`.

---

## 0. The criterion for "algorithmic", stated once

D119 rule 2 ranks a row by pcrec's ratio to the fastest engine on that row
**whose advantage is algorithmic**. The rule applied uniformly to all 128
rows:

1. **`pcre2-jit` is never itself the target.** JIT code generation is not an
   algorithmic advantage — pcrec compiles too. Where the JIT is fastest, the
   row's algorithmic target is the fastest non-JIT, non-vectorscan engine.
   This is exactly the discriminator Frank's own carve-out asks for ("a JIT
   start-up optimization such as a required-byte scan IS algorithmic"),
   because PCRE2's start-up optimizations are computed at **compile** time
   and are shared by the interpreter and the JIT: `man pcre2api`, "the
   start-up optimizations are in effect a pre-scan of the subject that takes
   place before the pattern is run", and the facts they use
   (`PCRE2_INFO_FIRSTCODEUNIT`, `PCRE2_INFO_FIRSTBITMAP`,
   `PCRE2_INFO_LASTCODETYPE`/`LASTCODEUNIT`, `PCRE2_INFO_MINLENGTH`) are
   pattern properties, not JIT properties. So whenever a start-up
   optimization is what is winning, `pcre2-interp` wins too and is named as
   the target — which is what happens on five of the top eight rows below.
2. **`vectorscan` is excluded as a target.** It is a SIMD-first,
   multi-pattern streaming automaton reporting `nosom`/`nocaps`; there is no
   scalar mechanism to mine from a vectorscan win.
3. **Every other engine counts**, subset engines included (`re2`,
   `re2-longest`, `rust`, `oniguruma`, `tre`, `pcre2-dfa`): a subset engine's
   win is a mechanism to mine.
4. **`rust` counts, with its SIMD component separated.** The rust crate's
   literal prefilters (`memchr`, Teddy) are algorithmic *mechanisms* with
   SIMD *implementations*. D119 defers SIMD to the end, so every row is also
   reported against the **best scalar engine** (the `scalar ×` column: the
   roster minus `rust`, `pcre2-jit` and `vectorscan`). A row where pcrec
   already beats every scalar engine and only `rust` is ahead is recorded as
   a SIMD-phase deferral, not as a cycle-1 target. That is nine of the
   thirty-four losing rows.

**The class weighting.** D119: weight by pattern class so one exotic row
cannot outrank a family. Each of the thirteen `tag family=` values holds one
equal budget; a row's weight is `1 / (rows of its family in this matrix)`,
so `cap-recursion` (8 rows) weights each row 0.125 and `wild-logparse`
(20 rows) weights each 0.05. The score is

    score = weight × log2(ratio),  clamped to 0 when ratio ≤ 1

The `log2` is a deliberate compression so that a single 52,000× row cannot
swamp a family; the raw ratio is carried in its own column and nothing is
hidden. Ratios compare **within a row only** — never across rows, patterns
or regimes.

**The two regimes** (`bench/capability/subbench.toml`,
`pcrecbench/harness.py:78`, `pcrecbench/subbench.py:369`):
`large-subject-throughput` is a **find-all** loop over the three generated
texts (64 KiB / 256 KiB / 1 MiB), one iteration per probe;
`short-subject-search` is a single leftmost search over the 75 short
subjects, 200 iterations. A *set-grain* median is the **sum** over that
regime's subjects (verified: `floor-byte` throughput reads
1,138 + 4,409 + 17,693 = 23,240 ns against the matrix's 23,243).

---

## 1. The ranked table — all 128 (pattern, regime) cells

125 cells rank; three do not and are in §1.2. **pcrec's best variant is
fastest or tied on 91 of the 125** and behind an algorithmic engine on 34.
Total weighted score over the losing rows: 10.284.

`pcrec variant` is the fastest of the four bench entries on that row:
`auto-caps` = `--features all`; `auto-nocaps` = `+ --no-captures`;
`vm-caps` = `+ --engine=vm`; `vm-in` = the same forced VM through the `_in`
entries with a caller frame buffer (`testees/pcrec/configs.toml`).

| # | score | family | pattern | regime | pcrec variant | pcrec ns | algorithmic target | target ns | ratio | pcrec artifact (engine/scan/prefilter) | best scalar | scalar × |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.9587 | cap-recursion | `bracket-array-define` | thr | vm-in | 4878708.4 | onig | 93.6 | **52122.95** | vm/none | onig | 52122.95 |
| 2 | 0.9492 | cap-recursion | `tag-depth3-bound` | thr | vm-in | 4489306.0 | pcre2-interp | 23238.0 | **193.19** | vm/none | pcre2-interp | 193.19 |
| 3 | 0.9171 | cap-backref | `dup-param-detect` | thr | auto-nocaps | 13395594.1 | pcre2-interp | 23240.8 | **576.38** | vm/none | pcre2-interp | 576.38 |
| 4 | 0.8710 | semantics-divergence | `wild-semdiv-dollar-trailing-newline-pcre2` | thr | auto-caps | 109715.9 | rust | 78.3 | **1401.23** | dfa/unanchored/offset-set-bounded | onig | 725.16 |
| 5 | 0.7640 | cap-backref | `tag-pair-match` | thr | auto-nocaps | 4634284.5 | pcre2-interp | 23229.8 | **199.50** | vm/none | pcre2-interp | 199.50 |
| 6 | 0.7232 | wild-secrets | `wild-secrets-username-password-pair` | thr | auto-caps | 1283961.1 | pcre2-interp | 23276.3 | **55.16** | vm/hybrid | pcre2-interp | 55.16 |
| 7 | 0.6112 | wild-secrets | `wild-secrets-aws-access-key-id` | thr | auto-caps | 4010040.3 | rust | 135249.7 | **29.65** | vm/hybrid | pcre2-dfa | 18.93 |
| 8 | 0.3611 | wild-logparse | `wild-logparse-winpath-grok` | thr | auto-nocaps | 3468811.4 | pcre2-interp | 23249.3 | **149.20** | vm/hybrid | pcre2-interp | 149.20 |
| 9 | 0.2972 | cap-recursion | `nested-comment-rec` | thr | vm-in | 7790226.6 | onig | 1498678.4 | **5.20** | vm/none | onig | 5.20 |
| 10 | 0.2788 | wild-codegrammar | `wild-codegrammar-json-constant` | thr | auto-caps | 4198569.8 | rust | 280588.5 | **14.96** | dfa/unanchored/byte-class-bounded | re2 | 1.88 |
| 11 | 0.2435 | wild-waf | `wild-waf-crs-942360-concat-sqli` | thr | auto-caps | 12149168.7 | re2-longest | 2246279.5 | **5.41** | dfa/attempt/none | re2-longest | 5.41 |
| 12 | 0.2258 | semantics-divergence | `router-prefix-order` | thr | auto-caps | 393594.1 | rust | 60176.5 | **6.54** | dfa/unanchored/memchr | re2 | 0.98 |
| 13 | 0.2213 | semantics-divergence | `file-ext-order` | thr | auto-nocaps | 292629.0 | rust | 46454.2 | **6.30** | dfa/unanchored/memchr | re2-longest | 1.17 |
| 14 | 0.1931 | semantics-divergence | `wild-semdiv-altorder-foo-foobar-rustregex` | thr | auto-caps | 409792.5 | rust | 82230.5 | **4.98** | dfa/unanchored/memchr | re2 | 1.26 |
| 15 | 0.1831 | wild-waf | `wild-waf-crs-942270-union-select` | thr | auto-nocaps | 998850.9 | rust | 280700.9 | **3.56** | dfa/unanchored/byte-class | re2-longest | 2.28 |
| 16 | 0.1763 | wild-secrets | `wild-secrets-github-pat` | thr | auto-nocaps | 124368.5 | rust | 46777.4 | **2.66** | dfa/unanchored/offset-set-bounded | onig | 0.30 |
| 17 | 0.1708 | wild-waf | `wild-waf-crs-942160-sleep-benchmark` | thr | auto-caps | 1269889.0 | rust | 388639.3 | **3.27** | dfa/unanchored/byte-class | re2 | 0.57 |
| 18 | 0.1532 | cap-recursion | `bracket-array-define` | srch | vm-caps | 6819.6 | onig | 2915.5 | **2.34** | vm/none | onig | 2.34 |
| 19 | 0.1348 | cap-backref | `quoted-delim-match` | thr | auto-nocaps | 9769774.2 | onig | 3837824.7 | **2.55** | vm/none | onig | 2.55 |
| 20 | 0.1322 | cap-recursion | `nested-comment-rec` | srch | vm-caps | 9287.2 | onig | 4461.8 | **2.08** | vm/none | onig | 2.08 |
| 21 | 0.1145 | cap-recursion | `balanced-parens-rec` | thr | vm-caps | 5478750.3 | pcre2-interp | 2903815.4 | **1.89** | vm/none | pcre2-interp | 1.89 |
| 22 | 0.0935 | cap-recursion | `balanced-parens-rec` | srch | auto-nocaps | 6494.1 | pcre2-interp | 3866.6 | **1.68** | vm/none | pcre2-interp | 1.68 |
| 23 | 0.0901 | cap-backref | `dup-param-detect` | srch | auto-nocaps | 10836.8 | pcre2-interp | 5805.1 | **1.87** | vm/none | pcre2-interp | 1.87 |
| 24 | 0.0866 | wild-waf | `wild-waf-crs-942140-dbnames` | thr | auto-caps | 4085020.0 | re2 | 2241475.0 | **1.82** | dfa/unanchored/byte-class-bounded | re2 | 1.82 |
| 25 | 0.0832 | semantics-divergence | `keyword-prefix-order` | thr | auto-nocaps | 730991.6 | rust | 365976.0 | **2.00** | dfa/unanchored/offset-set | re2 | 0.30 |
| 26 | 0.0654 | cap-backref | `quoted-delim-match` | srch | auto-nocaps | 11161.3 | onig | 7095.2 | **1.57** | vm/none | onig | 1.57 |
| 27 | 0.0617 | wild-waf | `wild-waf-crs-942360-concat-sqli` | srch | auto-caps | 7378.9 | rust | 4812.2 | **1.53** | dfa/attempt/none | re2 | 0.77 |
| 28 | 0.0472 | cap-backref | `tag-pair-match` | srch | auto-caps | 6023.9 | pcre2-interp | 4343.7 | **1.39** | vm/none | pcre2-interp | 1.39 |
| 29 | 0.0255 | wild-secrets | `wild-secrets-aws-access-key-id` | srch | auto-nocaps | 2468.3 | rust | 2143.1 | **1.15** | dfa/unanchored/byte-class-bounded | pcre2-dfa | 0.58 |
| 30 | 0.0211 | cap-lookaround | `currency-lookbehind-fixed` | thr | vm-in | 11113159.1 | onig | 9600379.2 | **1.16** | vm/none | onig | 1.16 |
| 31 | 0.0116 | wild-validator | `uuid-near-miss` | thr | auto-caps | 19.9 | rust | 18.1 | **1.10** | dfa/attempt/none | onig | 0.21 |
| 32 | 0.0093 | cap-recursion | `tag-depth3-bound` | srch | vm-in | 6897.6 | onig | 6552.3 | **1.05** | vm/none | onig | 1.05 |
| 33 | 0.0051 | wild-validator | `wild-validator-ipv4-owasp` | thr | auto-nocaps | 18.7 | rust | 17.9 | **1.04** | dfa/attempt/none | pcre2-dfa | 0.23 |
| 34 | 0.0039 | wild-validator | `ipv4-near-miss` | thr | auto-nocaps | 18.7 | rust | 18.1 | **1.03** | dfa/attempt/none | pcre2-dfa | 0.23 |
| 35 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-stringcontent-escape` | thr | auto-caps | 23123.6 | pcre2-interp | 23214.3 | 1.00 | dfa/unanchored/memchr | pcre2-interp | 1.00 |
| 36 | 0.0000 | floor | `floor-byte` | thr | auto-caps | 23114.5 | tre | 23231.6 | 0.99 | dfa/unanchored/memchr | tre | 0.99 |
| 37 | 0.0000 | binary-nonutf8 | `mojibake-curly-quote` | thr | auto-nocaps | 23119.1 | pcre2-interp | 23237.6 | 0.99 | dfa/unanchored/memchr | pcre2-interp | 0.99 |
| 38 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-object-begin` | thr | auto-nocaps | 23090.6 | pcre2-interp | 23229.7 | 0.99 | dfa/unanchored/memchr | pcre2-interp | 0.99 |
| 39 | 0.0000 | wild-validator | `wild-validator-us-zip-owasp` | thr | auto-nocaps | 17.8 | rust | 18.1 | 0.98 | dfa/attempt/none | pcre2-dfa | 0.22 |
| 40 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-array-begin` | thr | auto-caps | 263768.2 | rust | 307114.3 | 0.86 | dfa/unanchored/memchr | tre | 0.38 |
| 41 | 0.0000 | wild-secrets | `wild-secrets-github-pat` | srch | auto-nocaps | 1371.5 | rust | 1683.6 | 0.81 | dfa/unanchored/offset-set-bounded | onig | 0.47 |
| 42 | 0.0000 | wild-validator | `uuid-near-miss` | srch | auto-nocaps | 563.2 | rust | 698.3 | 0.81 | dfa/attempt/none | onig | 0.20 |
| 43 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-constant` | srch | auto-nocaps | 2449.5 | rust | 3048.9 | 0.80 | dfa/unanchored/byte-class-bounded | pcre2-dfa | 0.35 |
| 44 | 0.0000 | wild-secrets | `wild-secrets-slack-webhook-url` | thr | auto-nocaps | 338263.4 | re2-longest | 439089.4 | 0.77 | dfa/unanchored/offset-set | re2-longest | 0.77 |
| 45 | 0.0000 | semantics-divergence | `wild-semdiv-dollar-trailing-newline-pcre2` | srch | auto-nocaps | 1188.7 | rust | 1594.0 | 0.75 | dfa/unanchored/offset-set-bounded | onig | 0.34 |
| 46 | 0.0000 | cap-lookaround | `email-local-nodup` | thr | auto-caps | 978.7 | onig | 1381.0 | 0.71 | vm/hybrid | onig | 0.71 |
| 47 | 0.0000 | wild-logparse | `wild-logparse-winpath-grok` | srch | auto-nocaps | 2643.9 | pcre2-interp | 3989.4 | 0.66 | vm/hybrid | pcre2-interp | 0.66 |
| 48 | 0.0000 | wild-waf | `wild-waf-crs-942140-dbnames` | srch | auto-nocaps | 2707.4 | rust | 4408.0 | 0.61 | dfa/unanchored/byte-class-bounded | re2 | 0.28 |
| 49 | 0.0000 | semantics-divergence | `router-prefix-order` | srch | auto-nocaps | 775.5 | rust | 1313.2 | 0.59 | dfa/unanchored/memchr | onig | 0.28 |
| 50 | 0.0000 | semantics-divergence | `file-ext-order` | srch | auto-nocaps | 828.8 | rust | 1424.6 | 0.58 | dfa/unanchored/memchr | onig | 0.26 |
| 51 | 0.0000 | wild-validator | `wild-validator-uuid-grok` | srch | auto-caps | 716.2 | rust | 1240.8 | 0.58 | dfa/unanchored/offset-set | pcre2-interp | 0.24 |
| 52 | 0.0000 | cap-lookaround | `email-local-nodup` | srch | auto-nocaps | 10607.1 | onig | 18596.6 | 0.57 | vm/hybrid | onig | 0.57 |
| 53 | 0.0000 | wild-waf | `wild-waf-crs-942500-comment-obfuscation` | thr | auto-caps | 23121.0 | rust | 41251.6 | 0.56 | dfa/unanchored/offset-set | re2 | 0.05 |
| 54 | 0.0000 | wild-secrets | `wild-secrets-username-password-pair` | srch | auto-nocaps | 1376.1 | rust | 2478.7 | 0.56 | dfa/unanchored/byte-class | pcre2-dfa | 0.36 |
| 55 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-object-begin` | srch | auto-nocaps | 665.9 | rust | 1226.8 | 0.54 | dfa/unanchored/memchr | tre | 0.32 |
| 56 | 0.0000 | floor | `floor-byte` | srch | auto-nocaps | 665.2 | rust | 1228.3 | 0.54 | dfa/unanchored/memchr | tre | 0.32 |
| 57 | 0.0000 | wild-waf | `wild-waf-crs-942270-union-select` | srch | auto-nocaps | 1148.8 | rust | 2127.7 | 0.54 | dfa/unanchored/byte-class | pcre2-dfa | 0.24 |
| 58 | 0.0000 | semantics-divergence | `wild-semdiv-altorder-foo-foobar-rustregex` | srch | auto-caps | 715.3 | rust | 1343.0 | 0.53 | dfa/unanchored/memchr | onig | 0.24 |
| 59 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-array-begin` | srch | auto-caps | 687.8 | rust | 1330.6 | 0.52 | dfa/unanchored/memchr | tre | 0.31 |
| 60 | 0.0000 | wild-logparse | `wild-logparse-syslogbase-expanded` | srch | auto-nocaps | 3583.6 | pcre2-dfa | 7132.2 | 0.50 | vm/hybrid | pcre2-dfa | 0.50 |
| 61 | 0.0000 | cap-backref | `phone-palindrome-6` | thr | vm-caps | 7116848.2 | onig | 14477786.9 | 0.49 | vm/none | onig | 0.49 |
| 62 | 0.0000 | wild-logparse | `wild-logparse-quotedstring-grok` | thr | auto-caps | 1008829.4 | pcre2-interp | 2071041.0 | 0.49 | vm/hybrid | pcre2-interp | 0.49 |
| 63 | 0.0000 | semantics-divergence | `keyword-prefix-order` | srch | auto-caps | 774.2 | rust | 1619.6 | 0.48 | dfa/unanchored/offset-set | pcre2-interp | 0.19 |
| 64 | 0.0000 | binary-nonutf8 | `high-byte-run` | thr | auto-caps | 482988.0 | pcre2-dfa | 1012634.4 | 0.48 | dfa/unanchored/byte-class | pcre2-dfa | 0.48 |
| 65 | 0.0000 | binary-nonutf8 | `utf8-lead-no-cont` | thr | auto-nocaps | 481067.9 | pcre2-interp | 1017026.4 | 0.47 | vm/hybrid | pcre2-interp | 0.47 |
| 66 | 0.0000 | cap-lookaround | `float-literal-bound` | srch | auto-nocaps | 2483.2 | pcre2-interp | 5490.3 | 0.45 | vm/hybrid | pcre2-interp | 0.45 |
| 67 | 0.0000 | wild-logparse | `wild-logparse-quotedstring-noatomic` | thr | auto-nocaps | 929842.8 | pcre2-interp | 2111987.3 | 0.44 | vm/hybrid | pcre2-interp | 0.44 |
| 68 | 0.0000 | wild-validator | `wild-validator-email-owasp` | srch | auto-nocaps | 1063.7 | rust | 2580.3 | 0.41 | dfa/attempt/none | onig | 0.20 |
| 69 | 0.0000 | cap-backref | `phone-palindrome-6` | srch | vm-caps | 7212.2 | pcre2-interp | 17534.1 | 0.41 | vm/none | pcre2-interp | 0.41 |
| 70 | 0.0000 | wild-waf | `wild-waf-crs-942160-sleep-benchmark` | srch | auto-nocaps | 1301.1 | pcre2-dfa | 3182.7 | 0.41 | dfa/unanchored/byte-class | pcre2-dfa | 0.41 |
| 71 | 0.0000 | binary-nonutf8 | `utf8-lead-no-cont` | srch | auto-caps | 1252.2 | pcre2-dfa | 3120.4 | 0.40 | vm/hybrid | pcre2-dfa | 0.40 |
| 72 | 0.0000 | wild-logparse | `wild-logparse-quotedstring-grok` | srch | auto-nocaps | 1962.8 | pcre2-interp | 4938.3 | 0.40 | vm/hybrid | pcre2-interp | 0.40 |
| 73 | 0.0000 | wild-validator | `wild-validator-ipv4-owasp` | srch | auto-nocaps | 497.9 | rust | 1254.0 | 0.40 | dfa/attempt/none | pcre2-dfa | 0.18 |
| 74 | 0.0000 | wild-validator | `wild-validator-uuid-grok` | thr | auto-nocaps | 82557.9 | rust | 210621.1 | 0.39 | dfa/unanchored/offset-set | re2-longest | 0.04 |
| 75 | 0.0000 | wild-validator | `wild-validator-email-owasp` | thr | auto-nocaps | 39.6 | rust | 107.8 | 0.37 | dfa/attempt/none | re2 | 0.11 |
| 76 | 0.0000 | wild-secrets | `wild-secrets-slack-webhook-url` | srch | auto-nocaps | 927.9 | rust | 2558.6 | 0.36 | dfa/unanchored/offset-set | onig | 0.28 |
| 77 | 0.0000 | cap-lookaround | `pwd-strength-chain` | srch | auto-caps | 12402.4 | onig | 36028.0 | 0.34 | vm/hybrid | onig | 0.34 |
| 78 | 0.0000 | wild-validator | `ipv4-near-miss` | srch | auto-caps | 493.0 | rust | 1435.2 | 0.34 | dfa/attempt/none | pcre2-dfa | 0.18 |
| 79 | 0.0000 | binary-nonutf8 | `high-byte-run` | srch | auto-nocaps | 1105.3 | pcre2-dfa | 3272.3 | 0.34 | dfa/unanchored/byte-class | pcre2-dfa | 0.34 |
| 80 | 0.0000 | cap-lookaround | `currency-lookbehind-fixed` | srch | auto-caps | 5149.0 | pcre2-dfa | 15324.1 | 0.34 | vm/hybrid | pcre2-dfa | 0.34 |
| 81 | 0.0000 | cap-backref | `doubled-word` | thr | auto-nocaps | 25353511.9 | onig | 80036134.3 | 0.32 | vm/none | onig | 0.32 |
| 82 | 0.0000 | wild-logparse | `logparse-atomic-removed` | srch | auto-nocaps | 492.7 | rust | 1562.5 | 0.32 | dfa/attempt/none | pcre2-dfa | 0.11 |
| 83 | 0.0000 | redos-nested | `evil-alt-nested` | thr | auto-nocaps | 27.3 | rust | 87.8 | 0.31 | dfa/attempt/none | re2-longest | 0.09 |
| 84 | 0.0000 | wild-logparse | `logparse-atomic` | thr | auto-caps | 30.2 | onig | 97.8 | 0.31 | vm/hybrid | onig | 0.31 |
| 85 | 0.0000 | redos-nested | `email-nested-plus` | srch | auto-nocaps | 975.5 | pcre2-interp | 3172.2 | 0.31 | dfa/attempt/none | pcre2-interp | 0.31 |
| 86 | 0.0000 | redos-nested | `email-nested-plus` | thr | auto-nocaps | 32.7 | rust | 107.5 | 0.30 | dfa/attempt/none | re2 | 0.10 |
| 87 | 0.0000 | wild-waf | `wild-waf-crs-942500-comment-obfuscation` | srch | auto-caps | 736.3 | rust | 2422.4 | 0.30 | dfa/unanchored/offset-set | pcre2-dfa | 0.23 |
| 88 | 0.0000 | wild-datetime | `wild-datetime-datefinder-alternation` | thr | auto-nocaps | 10423601.4 | rust | 35096287.1 | 0.30 | dfa/unanchored/byte-class | re2-longest | 0.01 |
| 89 | 0.0000 | wild-codegrammar | `codegrammar-flat` | srch | auto-nocaps | 723.9 | pcre2-dfa | 2456.6 | 0.29 | dfa/unanchored/memchr | pcre2-dfa | 0.29 |
| 90 | 0.0000 | wild-codegrammar | `codegrammar-xflag` | srch | auto-nocaps | 724.9 | pcre2-dfa | 2477.8 | 0.29 | dfa/unanchored/memchr | pcre2-dfa | 0.29 |
| 91 | 0.0000 | wild-validator | `wild-validator-us-zip-owasp` | srch | auto-nocaps | 485.0 | rust | 1669.7 | 0.29 | dfa/attempt/none | re2 | 0.24 |
| 92 | 0.0000 | semantics-divergence | `wild-semdiv-empty-alt-repeat-pcre2` | thr | auto-nocaps | 3812623.6 | rust | 13152403.9 | 0.29 | dfa/unanchored/byte-class | pcre2-dfa | 0.14 |
| 93 | 0.0000 | wild-datetime | `wild-datetime-moment-iso8601` | srch | auto-nocaps | 589.8 | rust | 2043.0 | 0.29 | dfa/attempt/none | pcre2-interp | 0.17 |
| 94 | 0.0000 | wild-codegrammar | `codegrammar-flat` | thr | auto-caps | 608610.4 | pcre2-interp | 2116041.1 | 0.29 | vm/hybrid | pcre2-interp | 0.29 |
| 95 | 0.0000 | wild-codegrammar | `codegrammar-xflag` | thr | auto-caps | 604191.2 | pcre2-interp | 2121186.8 | 0.28 | vm/hybrid | pcre2-interp | 0.28 |
| 96 | 0.0000 | redos-nested | `date-nested-plus` | srch | auto-nocaps | 490.9 | rust | 1762.3 | 0.28 | dfa/attempt/none | pcre2-dfa | 0.12 |
| 97 | 0.0000 | wild-logparse | `winpath-near-miss` | srch | auto-nocaps | 499.9 | rust | 1796.4 | 0.28 | dfa/attempt/none | onig | 0.17 |
| 98 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-stringcontent-escape` | srch | auto-nocaps | 741.8 | pcre2-dfa | 2838.8 | 0.26 | dfa/unanchored/memchr | pcre2-dfa | 0.26 |
| 99 | 0.0000 | cap-backref | `doubled-word` | srch | auto-nocaps | 20836.9 | pcre2-interp | 83264.2 | 0.25 | vm/none | pcre2-interp | 0.25 |
| 100 | 0.0000 | wild-logparse | `base10num-near-miss` | srch | auto-nocaps | 552.0 | rust | 2222.5 | 0.25 | dfa/attempt/none | re2 | 0.14 |
| 101 | 0.0000 | binary-nonutf8 | `mojibake-curly-quote` | srch | auto-caps | 682.6 | pcre2-interp | 2824.6 | 0.24 | dfa/unanchored/memchr | pcre2-interp | 0.24 |
| 102 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-number-extended` | thr | auto-caps | 2447718.4 | rust | 10611468.7 | 0.23 | dfa/unanchored/byte-class | pcre2-interp | 0.13 |
| 103 | 0.0000 | wild-logparse | `logparse-atomic-removed` | thr | auto-nocaps | 18.7 | rust | 86.3 | 0.22 | dfa/attempt/none | onig | 0.19 |
| 104 | 0.0000 | redos-nested | `trim-nested-star` | srch | auto-nocaps | 427.7 | rust | 1993.0 | 0.21 | dfa/attempt/none | re2 | 0.05 |
| 105 | 0.0000 | wild-logparse | `winpath-near-miss` | thr | auto-caps | 20.1 | onig | 94.1 | 0.21 | dfa/attempt/none | onig | 0.21 |
| 106 | 0.0000 | wild-logparse | `wild-logparse-base10num-grok` | srch | auto-caps | 2506.9 | pcre2-interp | 11930.5 | 0.21 | vm/hybrid | pcre2-interp | 0.21 |
| 107 | 0.0000 | wild-logparse | `base10num-near-miss` | thr | auto-nocaps | 16.9 | pcre2-dfa | 80.9 | 0.21 | dfa/attempt/none | pcre2-dfa | 0.21 |
| 108 | 0.0000 | wild-logparse | `wild-logparse-base10num-grok` | thr | auto-nocaps | 4024029.9 | pcre2-interp | 19807035.7 | 0.20 | vm/hybrid | pcre2-interp | 0.20 |
| 109 | 0.0000 | wild-logparse | `wild-logparse-base10num-noatomic` | srch | auto-nocaps | 2474.9 | pcre2-interp | 12206.0 | 0.20 | vm/hybrid | pcre2-interp | 0.20 |
| 110 | 0.0000 | wild-datetime | `wild-datetime-moment-iso8601` | thr | auto-nocaps | 19.6 | pcre2-interp | 97.6 | 0.20 | dfa/attempt/none | pcre2-interp | 0.20 |
| 111 | 0.0000 | redos-nested | `date-nested-plus` | thr | auto-nocaps | 16.1 | rust | 81.7 | 0.20 | dfa/attempt/none | onig | 0.17 |
| 112 | 0.0000 | wild-logparse | `wild-logparse-base10num-noatomic` | thr | auto-nocaps | 3983529.8 | pcre2-interp | 20669189.7 | 0.19 | vm/hybrid | pcre2-interp | 0.19 |
| 113 | 0.0000 | redos-nested | `numeric-id-nested-plus` | thr | auto-nocaps | 15.2 | pcre2-dfa | 80.3 | 0.19 | dfa/attempt/none | pcre2-dfa | 0.19 |
| 114 | 0.0000 | redos-nested | `phone-list-nested-plus` | thr | auto-nocaps | 15.2 | pcre2-dfa | 80.8 | 0.19 | dfa/attempt/none | pcre2-dfa | 0.19 |
| 115 | 0.0000 | redos-nested | `trim-nested-star` | thr | auto-nocaps | 15.2 | rust | 82.3 | 0.18 | dfa/attempt/none | pcre2-dfa | 0.06 |
| 116 | 0.0000 | redos-nested | `numeric-id-nested-plus` | srch | auto-nocaps | 470.7 | rust | 2674.0 | 0.18 | dfa/attempt/none | re2-longest | 0.05 |
| 117 | 0.0000 | wild-logparse | `logparse-atomic` | srch | auto-nocaps | 837.3 | pcre2-interp | 4959.1 | 0.17 | vm/hybrid | pcre2-interp | 0.17 |
| 118 | 0.0000 | redos-nested | `phone-list-nested-plus` | srch | auto-nocaps | 480.6 | rust | 2969.7 | 0.16 | dfa/attempt/none | re2 | 0.05 |
| 119 | 0.0000 | wild-codegrammar | `wild-codegrammar-json-number-extended` | srch | auto-caps | 1410.3 | pcre2-interp | 9943.9 | 0.14 | dfa/unanchored/byte-class | pcre2-interp | 0.14 |
| 120 | 0.0000 | cap-lookaround | `float-literal-bound` | thr | auto-nocaps | 1788992.7 | onig | 13300527.4 | 0.13 | vm/hybrid | onig | 0.13 |
| 121 | 0.0000 | wild-logparse | `wild-logparse-syslogbase-expanded` | thr | auto-nocaps | 3988287.3 | pcre2-dfa | 30190617.0 | 0.13 | vm/hybrid | pcre2-dfa | 0.13 |
| 122 | 0.0000 | wild-logparse | `wild-logparse-quotedstring-noatomic` | srch | auto-nocaps | 1855.0 | pcre2-dfa | 14951.9 | 0.12 | vm/hybrid | pcre2-dfa | 0.12 |
| 123 | 0.0000 | semantics-divergence | `wild-semdiv-empty-alt-repeat-pcre2` | srch | auto-nocaps | 1238.2 | rust | 13254.3 | 0.09 | dfa/unanchored/byte-class | onig | 0.07 |
| 124 | 0.0000 | cap-lookaround | `pwd-strength-chain` | thr | auto-nocaps | 222.2 | onig | 4048.7 | 0.05 | vm/hybrid | onig | 0.05 |
| 125 | 0.0000 | wild-datetime | `wild-datetime-datefinder-alternation` | srch | auto-nocaps | 2010.0 | rust | 87852.2 | 0.02 | dfa/unanchored/byte-class | re2-longest | 0.01 |

### 1.1 The DEFAULT-CONFIG column the best-variant ranking hides

The ranking above takes pcrec's **best** of four variants, which is the
honest comparison for "can pcrec do this at all". It is not the shipped
default. `auto-caps` (`--features all`, captures on, engine auto) is what a
caller gets, and on three rows it is catastrophically worse than pcrec's own
best variant:

| pattern | regime | `auto-caps` ns | pcrec best variant ns | default ÷ best | default ÷ algorithmic target |
|---|---|---|---|---|---|
| `evil-alt-nested` | thr | 4,305,649 | 88 (`auto-nocaps`) | 48,927 | **49,016** |
| `trim-nested-star` | thr | 3,248,263 | 82 (`auto-nocaps`) | 39,613 | **39,447** |
| `trim-nested-star` | srch | 8,970,875 | 419 (`auto-nocaps`) | 21,411 | **4,501** |

All three are `^`-anchored `redos-nested` members where turning captures ON
moves the artifact from the DFA to the VM. They score **zero** in §1 because
`auto-nocaps` wins their row outright, and they are the three sharpest
default-config cells in the whole matrix. Mechanism M1 below covers the two
throughput cells; the `search` cell is backtracking cost and is
dispositioned in §4.

### 1.2 Cells that carry no number

| pattern | regime | reason (from the report's `R-STATUS-3`/`R-STATUS-4` and this lane's own compile) |
|---|---|---|
| `evil-alt-nested` | srch | **No ranking group exists.** Every roster engine is excluded: `pcre2-interp`/`jit`/`onig` and pcrec `auto-caps`/`vm`/`vm-in` give up (`-2:PCREC_ERR_STEPS×2`, `-47:match×2`, `-17:retry×2`); `pcre2-dfa`, `re2`, `re2-longest`, `rust`, `tre`, `vectorscan` and pcrec `auto-nocaps` are excluded for 10 wrong answers each. The wrong-answer population is exactly 2 subjects × 5 trials, and those two subjects (`rd-evil-alt-near-miss`, `sd-empty-alt-hit`) are the two `NOTES.md` records as **dropped from `expectations.tsv`** when the PCRE2 oracle itself gave up at derivation time. So the `wrong` label needs a bench-side read before anyone calls it a pcrec divergence; it is not a timing target either way. |
| `negation-scope-lookbehind-var` | thr, srch | `unsup` (unsupported-by-declaration) on pcrec and on `onig`/`re2`/`re2-longest`/`rust`/`tre`/`vectorscan`; `pcre2-dfa` gives up (`-42:pattern`). pcrec's own diagnostic, reproduced here: *"variable-length lookbehind is not implemented: every alternative of a lookbehind must have a fixed length (this one can match 4..51 characters)"*. A MODULE gap, not a performance gap — §4. |

Two further non-timing outcomes the matrix carries:

- **`wild-datetime-datefinder-alternation` does not compile on three of the
  four pcrec configs.** Reproduced here at `ab341bfe`: `auto-caps` 670,153,
  `vm-caps`/`vm-in` 665,144 bytes of emitted code against the 500,000 limit
  (the bench at `25b1984f` recorded 670,159 / 665,107 — the 39–46-byte
  difference is [REL-1.4]'s version/`abi` stamp, not a change in the
  blowup). `--no-captures` compiles at 20,432 bytes of **code** (889 KB of
  source, i.e. tables). Neither `--unroll=1` (675,615) nor
  `--tune=min-size` (670,109) rescues it. §4.
- **`email-nested-plus` / srch** excludes pcrec's two forced-VM entries for
  `PCREC_ERR_STEPS` give-ups on 5 subjects; `auto-caps`/`auto-nocaps` answer
  and are ranked.

---

## 2. Cause bucketing off the D81 stamps

Every one of the 64 patterns was compiled in this worktree at the bench's
own three flag sets and the stamps read off the emitted `.c`
(`docs/dev/optloop/stamps.py`; the resulting census is
`cycle1_rows.tsv`'s `engine`/`dfa_scan`/`dfa_prefilter`/`vm_prefilter`
columns). 187 of 192 (pattern, variant) compiles succeed; the five failures
are exactly the bench's own, above.

**Engine census at `auto-caps`:** 38 VM, 24 DFA, 2 refused.
**DFA prefilter census** (24): none 6, memchr 8, byte-class 4, offset-set 3,
byte-class-bounded 2, offset-set-bounded 1. **DFA scan:** unanchored 18,
attempt 6.
**VM prefilter census** (38): `hybrid` 27, `none` 11.

### 2.1 The subject census is what makes the throughput regime legible

The three throughput texts were regenerated from `captext.py` into the
session scratchpad and checked against the committed
`manifest_throughput.tsv` — all three SHA-256 values match exactly. Their
byte census (identical in shape at all three sizes) is decisive:

> `<`, `>`, `&`, `\`, `'`, `=`, `~`, `@`, `%`, `!`, `?`, `|`, `{`, `}`, `*`,
> `,`, `;`, `$` occur **zero** times. Present: `"` (0.57%), `#`, `(`, `)`,
> `+`, `-`, `.`, `/` (2.86%), `:`, `[`, `]`, `_`, digits, `A`–`W`, `a`–`y`.
> Word characters are 77.2% of the text.

So a pattern whose match must contain any of the absent bytes cannot match
anywhere in any of the three subjects, and a whole-subject pre-check answers
the entire find-all call in one pass.

### 2.2 The floor row proves what that pass costs, and that pcrec can reach it

`floor-byte` is the pattern `~`, and `~` is absent. Per-subject medians:

| testee | 64 KiB | 256 KiB | 1 MiB | ns/byte @1 MiB |
|---|---|---|---|---|
| `pcrec auto-caps` | 1,107.8 | 4,387.1 | **17,611.4** | 0.0168 |
| `libpcre2 interp` | 1,138.2 | 4,409.5 | 17,693.4 | 0.0169 |
| `rust` | 1,135.2 | 4,459.0 | 17,817.3 | 0.0170 |
| `libpcre2 jit` | 2,508.6 | 9,794.2 | 39,663.5 | 0.0378 |

Three independent engines land on the same 0.0168–0.0170 ns/byte, and
**pcrec is the fastest of them.** That rate is one `memchr`-class pass over
the subject and it is a property of the box, not of any engine. pcrec
reaches it through `RX_DFA_PREFILTER "memchr"`. Everything in §2.3 is a case
where pcrec *cannot* reach a mechanism it already owns.

The same table read the other way is the second control: `vm-caps` on
`floor-byte` throughput is **815,257 ns** against `auto-caps`'s 23,115 — a
35× penalty on the single literal `~`, because a forced VM has no prefilter
and walks every start position.

### 2.3 The buckets, in D119's taxonomy

**(a) ENGINE SELECTION — VM where the DFA could serve: EMPTY.** Every
VM-routed losing row is VM-routed for a construct the DFA cannot express —
`RX_ENGINE_WHY` reads `(?R)`, `(?&name)`, `capture group`, `(?<=...)`,
`(?!...)`, `(?>...)`. No row in this subbench is a selection mistake. That
is a result, and it means cycle 1 has nothing to mine in D119's first
bucket.

**(b) SCAN SHAPE — the VM's attempt loop has no start bound.** The DFA
emitter writes (`src/gen/emit_dfa.c:6808-6812`):

```c
    const size_t start_max = 0 /* fully ^-anchored */;
    for (start = search_from; start <= start_max; start++) {
```

a three-valued bound (`0` for `^`, `search_from` for `\G`, `subject_length`
otherwise) derived from `dfa_interior_dead(d->s1u)`/`(d->s1g)`. The VM
emitter writes no bound at all — from `bracket-array-define`'s own artifact:

```c
    for (;;) {
        ctx.pos = attempt_position;
        result = rx_match_anchored(&ctx, run, window_end);
        ...
        rx_reset_for_next_attempt(run);
        if (attempt_position >= subject_length) return 0;
        attempt_position++;
    }
```

Measured consequence on `bracket-array-define` (`^ (?&brackets) $` under
`(?x)`; `RX_ENGINE "vm"`, `RX_VM_PREFILTER "none"`):

| testee | 64 KiB | 256 KiB | 1 MiB | shape |
|---|---|---|---|---|
| `oniguruma` | 31.2 | 31.4 | 31.2 | **O(1)** |
| `libpcre2 jit` | 42.2 | 42.8 | 42.7 | O(1) |
| `libpcre2 interp` | 111.0 | 110.3 | 110.3 | O(1) |
| pcrec (all four) | ~233,700 | ~930,100 | ~3,716,000 | linear, 3.54 ns/byte |

`pcre2_pattern_info` confirms the pattern carries `PCRE2_ANCHORED`. The
direct control is that pcrec's **DFA** route has this: `ipv4-near-miss`,
`uuid-near-miss` and `wild-validator-ipv4-owasp` are equally anchored, land
on `RX_DFA_SCAN "attempt"` with `start_max = 0`, and read a flat ~6–20 ns at
every subject size.

**(c) PREFILTER MISS — the required byte.** Five throughput rows where the
winner is at the §2.2 floor and pcrec is at VM-attempt rate. `pcre2_pattern_info`
run here against libpcre2 10.48 (Homebrew; a structural query, not a timing):

| pattern | pcrec route | PCRE2 first unit | PCRE2 **required** unit | present in subject? | pcrec ns/byte | target ns/byte |
|---|---|---|---|---|---|---|
| `tag-pair-match` | vm / none | `'<'` | `'>'` | **no** | 3.37 | 0.0169 |
| `tag-depth3-bound` | vm / none | `'<'` | `'>'` | **no** | 3.26 | 0.0169 |
| `dup-param-detect` | vm / none | bitmap[63] | `'='` | **no** | 9.74 | 0.0169 |
| `wild-logparse-winpath-grok` | vm / hybrid | bitmap[53] | `'\'` | **no** | 2.52 | 0.0169 |
| `wild-secrets-username-password-pair` | vm / hybrid | `'U'` | `'='` | **no** | 0.93 | 0.0169 |

`PCRE2_INFO_LASTCODETYPE`/`LASTCODEUNIT` is documented as "the rightmost
literal code unit that must exist in any matched string, other than at its
start" (`man pcre2api`). **pcrec computes no such fact.** Note that the last
three rows are the ones a first-byte prefilter cannot rescue: their
first-byte sets are 63, 53 and 2 bytes wide, and only the required byte is
decisive. Across the whole set, PCRE2 records a required unit for **25 of
the 64 patterns**.

**(d) PREFILTER MISS — the candidate-start set, coarsened by a leading
`\b`.** pcrec derives the DFA prefilter's `rx_can_begin_match[256]` from the
bytes that leave the machine's start state. A leading `\b` makes that state
track word context, so the set becomes the whole word class. Minimal witness,
built here:

| pattern | `RX_DFA_PREFILTER` | `\|can_begin_match\|` | hit rate in the 1 MiB subject |
|---|---|---|---|
| `A[A-Z0-9]{16}` | `memchr` | 1 (`A`) | 0.17% |
| `\bA[A-Z0-9]{16}` | `byte-class-bounded` | **63** (`[0-9A-Za-z_]`) | **77.21%** |

One construct, one prefilter class, a 454× denser candidate set. PCRE2
records `FIRSTCODEUNIT = 'A'` for the `\b` form regardless. Four patterns in
the set carry a 63-byte `can_begin_match` for this reason, and three of them
are losing rows:

| pattern | pcrec set | PCRE2's set | pcrec ns/byte | best scalar ns/byte | scalar × |
|---|---|---|---|---|---|
| `wild-secrets-aws-access-key-id` | 63 (77.21%) | 1 (`'A'`, 0.17%) | 3.83 | `pcre2-dfa` 0.20 | **18.93** |
| `wild-codegrammar-json-constant` | 63 (77.21%) | bitmap[3] | 3.05 | `re2` 1.62 | 1.88 |
| `wild-waf-crs-942140-dbnames` | 63 (77.21%) | bitmap[14] | 2.97 | `re2` 1.62 | 1.82 |
| `wild-logparse-syslogbase-expanded` | 63 (77.21%) | bitmap[16] | — | — | (not losing) |

This is [OPT-3]'s already-measured symptom — *"the skip loop is entered
190,651 times and skips ZERO bytes"* (`docs/dev/opt3_dfa_scan_measurement.md`)
— with a named cause.

**(e) SCAN SHAPE — `^` on SOME branches drops the whole DFA toolkit.**
`src/gen/emit_dfa.c:13-17` says it in its own words: *"ENG_ATTEMPT (patterns
containing `^`): per-start-position computed-goto attempt loop … fully-anchored
patterns get the start_max=0 fast path, so the slow shape is `^` on only
SOME branches."* Of the six `attempt`-scan artifacts in this set, five carry
`start_max = 0` and are free; `wild-waf-crs-942360-concat-sqli` carries
`start_max = subject_length` and pays. Its stamps are
`RX_DFA_PREFILTER "none"`, `RX_DFA_TABLE "none"`, `RX_DFA_SCAN_EDGE "none"`
— no prefilter, no premultiplied table, no [OPT-5] scan edge — and it reads
**8.83 ns/byte**, the highest per-byte cost of any DFA artifact in the set,
against `re2-longest`'s 1.62.

**(f) VM BACKTRACKING COST.** Eleven rows where pcrec and the winner are
both linear and pcrec is 1.05–5.2× the winner's per-byte rate:
`nested-comment-rec` (5.20× onig thr, 2.08× srch), `quoted-delim-match`
(2.55× / 1.57×), `balanced-parens-rec` (1.89× / 1.68× interp),
`dup-param-detect` srch (1.87×), `tag-pair-match` srch (1.39×),
`currency-lookbehind-fixed` (1.16×), `tag-depth3-bound` srch (1.05×),
`bracket-array-define` srch (2.34×). No single mechanism is visible from the
emitted C: `rx_reset_for_next_attempt` is O(trail depth), i.e. proportional
to work already done, not a fixed per-attempt tax. **This bucket needs the
profile before it can name a mechanism** — §3 M5.

**(g) PER-CALL OVERHEAD UNDER FIND-ALL: pcrec is the best in the roster.**
`floor-byte` `short-subject-search` set-grain: pcrec `auto-nocaps` **665 ns**,
`auto-caps` 667, `rust` 1,228, `pcre2-dfa` 2,277, `pcre2-interp` 2,583,
`pcre2-jit` 3,032, `re2` 7,499. pcrec wins 53 of the 62 ranked short-regime
rows and no losing short row exceeds 2.34×. D119's per-call-overhead bucket
is empty in pcrec's disfavour.

**(h) UTF-8 COST: not exercised.** Every testee in this set compiles for
byte semantics; no pattern uses `\p{...}`. The bucket has no population here.

**(i) STATE BLOW-UP / SIZE CAP: one row.**
`wild-datetime-datefinder-alternation`, §1.2 and §4.

**(j) FUNDAMENTAL / SIMD-DEFERRED.** Nine of the 34 losing rows are rows
where **pcrec already beats every scalar engine** and only `rust` is ahead:
`wild-secrets-github-pat` (0.30× scalar), `keyword-prefix-order` (0.30×),
`wild-waf-crs-942160-sleep-benchmark` (0.57×), `wild-secrets-aws-access-key-id`
srch (0.58×), `wild-waf-crs-942360-concat-sqli` srch (0.77×),
`router-prefix-order` (0.98×), `uuid-near-miss` thr (0.21×),
`wild-validator-ipv4-owasp` thr (0.23×), `ipv4-near-miss` thr (0.23×). The
mechanism rust is winning with is a vectorized multi-literal prefilter
(Teddy/`memchr`); pcrec's scalar equivalent is already competitive. Per
D119 these are **SIMD-phase deferrals**, not cycle-1 targets. Four further
rust-won rows retain a real but modest scalar gap after that subtraction
(`wild-waf-crs-942270-union-select` 2.28×, `wild-codegrammar-json-constant`
1.88×, `wild-semdiv-altorder-foo-foobar-rustregex` 1.26×, `file-ext-order`
1.17×).

### 2.4 The brief's own question: which pre-check would have sufficed

Three whole-subject pre-checks explain every O(1) or floor-rate answer in
this matrix, and pcrec has exactly one of them:

| pre-check | PCRE2's name | pcrec has it? | rows it explains here |
|---|---|---|---|
| first code unit / first bitmap → `memchr` or class skip | `FIRSTCODEUNIT` / `FIRSTBITMAP` | **partly** — `RX_DFA_PREFILTER`, DFA route only, derived from the start state so a leading `\b` destroys it | `floor-byte` (pcrec wins), §2.3(d)'s four |
| required code unit anywhere in the match → one `memchr` per call | `LASTCODETYPE`/`LASTCODEUNIT` | **no** | §2.3(c)'s five |
| pattern is start-anchored → one attempt | `PCRE2_ANCHORED` | **DFA only** (`start_max`) | §2.3(b)'s three, plus §1.1's three default-config cells |
| pattern is end-anchored and bounded → scan only the tail | (rust/re2 reject `abc$` in O(1)) | **no** | `wild-semdiv-dollar-trailing-newline-pcre2` |
