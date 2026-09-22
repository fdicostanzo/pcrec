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

---

## 3. The five target MECHANISMS

Ranked by the sum of the class-weighted scores of the rows each explains.
They are mechanisms, not patterns (memory `pcrec-general-mechanisms-not-special-cases`):
each is stated in its general form, names the existing primitive it extends,
and carries the Linux measurement that must confirm the diagnosis **before**
any implementation (D77).

| rank | mechanism | score covered | rows | size | architecture fit |
|---|---|---|---|---|---|
| M1 | **[OPT-REQBYTE]** required-byte whole-window pre-check | 3.714 | 5 | S–M | extends the prefilter, both engines |
| M2 | **[OPT-ANCHOR-VM]** the VM's attempt-loop start bound | 2.112 (+ §1.1's three default cells) | 2 (+3) | S | moves an existing DFA primitive to the VM |
| M3 | **[OPT-FIRSTSET]** candidate-start set derived from the AST, not the start state | 1.002 | 4 | M | replaces one derivation inside the existing prefilter |
| M4 | **[OPT-ENDWIN]** end-anchor start-window bound | 0.871 | 1 | M | D77's own named `\z` fold |
| M5 | **[OPT-ATTEMPT-SPLIT]** `^` on some branches stops costing the whole DFA toolkit | 0.306 | 2 | M–L | reuses both existing DFA shapes |

Their union covers 8.005 of the losing rows' 10.284 weighted score. The
remainder is §2.3(f)'s backtracking bucket (1.004, no mechanism named yet —
M6 below is the measurement that would name one) and §2.3(j)'s SIMD
deferrals (1.275).

**The natural first implementation batch (D119 caps it at three) is
M1 + M2 + M3**: they are one analysis and two consumers, they share their
validation population, and they carry 6.828 of the 8.005.

### The shared profile setup (run once on ubuntubudu)

`perf` is unavailable there (`perf_event_paranoid=4`,
`opt5_step0_profile.md` §1) — so this follows the [OPT-5] step-0 method:
a real driver, a calibrated clock, and static disassembly. Every command is
verbatim. Nothing is written inside `/home/duxevents/pcrec-bench`.

```sh
# 0.1  a scratch root OUTSIDE both repos
export OPT1=/tmp/optloop1 && mkdir -p "$OPT1" && cd "$OPT1"

# 0.2  the pin under test: pcrec at the analysis commit
git -C /home/duxevents/pcrec worktree add "$OPT1/pcrec" lane/optrev
cd "$OPT1/pcrec" && make -j4 && cd "$OPT1"

# 0.3  the three throughput subjects, regenerated into the scratch root.
#      This WRITES NOTHING in pcrec-bench (the repo's own generator would
#      rewrite a committed manifest; this snippet does not call it).
mkdir -p "$OPT1/subj"
python3 - <<'PY'
import sys, os, hashlib
sys.path.insert(0, "/home/duxevents/pcrec-bench/bench/capability")
import captext as ct
for sid, n, seed in (("t-64k",65536,0xC0FFEE1),("t-256k",262144,0xC0FFEE2),("t-1m",1048576,0xC0FFEE3)):
    b = ct.text(n, seed)
    open(os.path.join(os.environ["OPT1"], "subj", sid + ".bin"), "wb").write(b)
    print(sid, len(b), hashlib.sha256(b).hexdigest())
PY
# EXPECT, byte for byte against bench/capability/manifest_throughput.tsv:
#   t-64k  65536   d2e4f134473cc40a9a4e7df7a30e0efa11f566d96ee990c62cd663a2439c8524
#   t-256k 262144  3cf7b248873da164518b74e039cc2380f39e233b2899716c82c8eb4b7b49b5a7
#   t-1m   1048576 ccbdf7eb97f15776a68b8bbb9d6387870cd01d4796207fb20032958caf9754ee
# A mismatch means the subject changed and every number below is off-pin: STOP.

# 0.4  the clock calibration (opt5_step0_profile.md §1's dependent add-chain,
#      with the volatile barrier that stops gcc folding it to a closed form)
cat > "$OPT1/clock.c" <<'EOF'
#include <stdio.h>
#include <time.h>
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
  return t.tv_sec + 1e-9*t.tv_nsec;}
int main(void){volatile long v=0; long N=2000000000L; double t0=now();
  for(long i=0;i<N;i++){ v=v+1; __asm__ volatile("":"+r"(v)); }
  double dt=now()-t0; printf("%.4f GHz (N=%ld, %.3f s)\n", N/dt/1e9, N, dt); return 0;}
EOF
gcc -O2 -o "$OPT1/clock" "$OPT1/clock.c" && for i in 1 2 3 4 5; do "$OPT1/clock"; done
uptime   # load1 must be < 0.5 before any timed phase; discard above 2.0

# 0.5  the shared find-all driver: the bench's own loop shape
#      (testees/pcrec/driver.c:714-740), reproduced so a hand-twin can be
#      timed against the shipped artifact with one variable moved.
cat > "$OPT1/findall.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "art.h"
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
  return t.tv_sec + 1e-9*t.tv_nsec;}
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"rb"); fseek(f,0,SEEK_END); long n=ftell(f); rewind(f);
  unsigned char*b=malloc(n); if(fread(b,1,n,f)!=(size_t)n) return 2; fclose(f);
  long iters = argc>2 ? atol(argv[2]) : 5;
  ptrdiff_t caps[RX_NCAPS][2];
  double best=1e30; long count=0;
  for(long it=0; it<iters; it++){
    double t0=now(); size_t pos=0; count=0;
    for(;;){ int r=rx_search(b,(size_t)n,pos,caps); if(r==0) break;
             if(r<0){ printf("giveup %d\n", r); break; }
             size_t s=(size_t)caps[0][0], e=(size_t)caps[0][1];
             count++; pos = (e>s)?e:s+1; if(pos>(size_t)n) break; }
    double dt=now()-t0; if(dt<best) best=dt; }
  printf("%-24s n=%ld matches=%ld best=%.9f s  %.4f ns/byte\n",
         argv[1], n, count, best, best*1e9/(double)n);
  return 0; }
EOF
```

---

### M1 — `[OPT-REQBYTE]`: the required-byte whole-window pre-check

**Rows explained** (all `large-subject-throughput`): `tag-depth3-bound`
(rank 2, 193.19×), `dup-param-detect` (3, 576.38×), `tag-pair-match`
(5, 199.50×), `wild-secrets-username-password-pair` (6, 55.16×),
`wild-logparse-winpath-grok` (8, 149.20×). Weighted score **3.714**, the
largest of any mechanism in the matrix.

**Diagnosis.** Per call, on a 1 MiB subject with no match:
`pcre2-interp` does **one** `memchr`-class pass (0.0169 ns/byte, the §2.2
floor rate three independent engines share) and returns NOMATCH for the
whole subject. pcrec runs a full VM attempt at every one of the 1,048,576
start positions (2.52–9.74 ns/byte). The deciding fact is not the first
byte — for `dup-param-detect` and `winpath-grok` the first-byte set is 63
and 53 bytes wide and useless — it is that **every match of these patterns
must contain a literal byte that occurs zero times in the subject**
(`'>'`, `'='`, `'\'`, §2.1's census; `PCRE2_INFO_LASTCODEUNIT` per pattern,
§2.3(c)'s table, measured here with `docs/dev/optloop/p2info.c`). pcrec
computes no such fact at any point in the pipeline: `--list-axes` has no
axis for it and no stamp reports one.

**The mechanism, in general form.** Compute, at compile time from the AST, a
**necessary literal byte**: a byte `c` such that every string in the
pattern's language contains `c` at some position past its start. The
derivation is the obvious one — walk the AST bottom-up returning a set of
necessary bytes (`concat` unions its children's sets; `alternation`
intersects; a quantifier with minimum 0 returns the empty set; a class
returns a singleton only when it is one byte; a backreference or a linked
call returns the empty set, which is always sound because the empty set
disables the check). Emit one byte (the rightmost, matching PCRE2's own
choice, so a later multi-byte form is a widening and not a different
mechanism) into the artifact and test it **once per `<prefix>_search`
call**, before the attempt loop, with the `memchr` the prefilter path
already emits:

```c
    if (!memchr(subject + search_from, RX_REQ_BYTE, subject_length - search_from))
        return 0;
```

This EXTENDS the existing prefilter primitive rather than paralleling it:
`RX_DFA_PREFILTER "memchr"` already emits a `memchr` over the same window
for a *candidate start*; this is the same instrument keyed on a *necessary
byte* and hoisted one level out, so it also serves the VM, where the hybrid
prefilter is declined outright for backreferences and linked calls
(`src/opt/select_engine.c:604,651`). Three of the five rows are exactly
those declines.

**Architecture fit.** Inside the architecture: one compile-time analysis,
one emitted constant, one `memchr` in a function that already contains one
on the DFA route. No new engine, no new pass ordering constraint.

**Size expectation.** Two emitted lines and one `#define` per artifact where
the byte exists; zero where it does not. Under 100 bytes of emitted C.
Nothing in the tables moves.

**The axis.** `-fno-req-byte` / `PCREC_NO_REQ_BYTE`, stamp
`<PREFIX>_REQ_BYTE` (the byte, or `none`), one row in `src/core/axes.def`.
Sabotage direction: invert the `memchr` test's sense (`if (memchr(...)) return 0;`)
— a plant that must turn matching subjects into NOMATCH on the five rows'
own hit subjects; the reach witness is any pattern whose stamp is not
`none`. `make test-axes` must read answer-identical denied and forced over
the whole corpus.

**Owed Linux measurement** (confirms the diagnosis and sizes the landing bar
before anything is built):

```sh
cd "$OPT1"
# M1.a  baseline: the shipped artifacts, the bench's own flags and subjects
for P in tag-depth3-bound dup-param-detect tag-pair-match \
         wild-secrets-username-password-pair wild-logparse-winpath-grok; do
  "$OPT1/pcrec/build/pcrec" --features all -p rx -o "$OPT1/$P.c" \
      "/home/duxevents/pcrec-bench/bench/capability/patterns/$P.rx" 2>/dev/null \
    || "$OPT1/pcrec/build/pcrec" --features all -p rx -o "$OPT1/$P.c" \
         --pattern "$(cat /home/duxevents/pcrec-bench/bench/capability/patterns/$P.rx)"
  cp "$OPT1/$P.h" "$OPT1/art.h"; cp "$OPT1/$P.c" "$OPT1/art.c"
  gcc -O2 -I"$OPT1" -o "$OPT1/base_$P" "$OPT1/findall.c" "$OPT1/art.c"
  for S in t-64k t-256k t-1m; do "$OPT1/base_$P" "$OPT1/subj/$S.bin" 5; done
done
# EXPECT (Ryzen 1600, the bench's own figures): matches=0 everywhere, and
# ns/byte flat across the three sizes at
#   tag-depth3-bound 3.26 | dup-param-detect 9.74 | tag-pair-match 3.37
#   username-password-pair 0.93 | winpath-grok 2.52
# A non-flat ns/byte is a finding in its own right (the set's own rule R6).

# M1.b  the HAND-TWIN: the same artifact with the pre-check inserted by hand.
#       REQ is the byte PCRE2 records; this lane measured it per pattern.
#       tag-depth3-bound '>' | dup-param-detect '=' | tag-pair-match '>'
#       username-password-pair '=' | winpath-grok '\\'
#       Insert immediately after `if (search_from > subject_length) return 0;`
#       in <prefix>_search (DFA) / rx_search_run (VM):
#           if (!memchr(subject + search_from, REQ, subject_length - search_from))
#               return 0;
#       and add #include <string.h>.
#       Then rebuild exactly as in M1.a and re-run the same three subjects.
# EXPECT: ns/byte collapses to the §2.2 floor (~0.017) on all five, i.e.
#   192x / 576x / 199x / 55x / 149x, reproducing the matrix's own ratios.
#   ANY twin that does NOT reach ~0.017 ns/byte refutes the diagnosis.

# M1.c  the CARVE-OUT: the pre-check must cost nothing where it cannot fire.
#       Same twin, run on a subject that DOES contain the byte, so the
#       memchr succeeds immediately and the attempt loop runs as before.
printf 'x%.0s' $(seq 1 1000000) > "$OPT1/subj/hit.bin"; printf '>' >> "$OPT1/subj/hit.bin"
"$OPT1/base_tag-pair-match" "$OPT1/subj/hit.bin" 5
"$OPT1/twin_tag-pair-match" "$OPT1/subj/hit.bin" 5
# EXPECT: within noise of each other (the memchr finds the byte at offset
#   1,000,000 and is one pass; the attempt loop is unchanged). A twin more
#   than ~2% slower here is the landing bar's carve-out failing.
```

---

### M2 — `[OPT-ANCHOR-VM]`: the start-position bound in the VM's attempt loop

**Rows explained.** `bracket-array-define` thr (rank 1, **52,122.95×**) and
srch (rank 18, 2.34×); weighted score **2.112**. Plus, at the shipped
default config only (§1.1), `evil-alt-nested` thr (49,016× vs the
algorithmic target) and `trim-nested-star` thr (39,447×), which score zero
in the ranking because `--no-captures` rescues them.

**Diagnosis.** `bracket-array-define` is `PCRE2_ANCHORED` (measured here).
`oniguruma` answers it in **31 ns at every subject size** — one attempt at
position 0, first byte is not `[`, done. pcrec runs 1,048,576 attempts
(3.54 ns/byte, perfectly linear, x15.9 for x16 subject). The bound already
exists in this tree, in the other emitter: `src/gen/emit_dfa.c:6802-6812`
derives `bool anchored = dfa_interior_dead(d->s1u) && dfa_interior_dead(d->s1g)`
and writes `const size_t start_max = 0 /* fully ^-anchored */;`. The VM's
`rx_search_run` writes `for (;;) { ... attempt_position++; }` with no bound
at all. The DFA control is direct: `ipv4-near-miss` and
`wild-validator-ipv4-owasp` are equally anchored, take the DFA route, and
read a flat 6.2 ns at 64 KiB and at 1 MiB.

**The mechanism, in general form.** Give the VM's search loop the *same
three-valued bound the DFA already has*, derived from the same kind of fact
one layer up (the AST/NFA rather than the DFA's start-state interior,
because a VM-routed pattern has no DFA to ask): `start_max = search_from`
when every alternative of the whole pattern begins with `\A`/`^` outside
multiline or with `\G`; `subject_length` otherwise. This is
**implement-then-replace**, not a parallel mechanism: the derived fact
should become one predicate both emitters read, so the DFA's
`dfa_interior_dead` pair becomes a *confirmation* of an AST-level answer
rather than a second source of truth. Fourteen of the 64 patterns are
`PCRE2_ANCHORED` **and** VM-routed at `auto-caps`; three of those carry
`RX_VM_PREFILTER "none"` and are the ones with no rescue at all
(`bracket-array-define`, `evil-alt-nested`, `trim-nested-star`).

**Architecture fit.** Inside the architecture, and the smallest of the five:
one predicate, one emitted bound, one loop condition. No new engine.

**Size expectation.** Net **negative** on an anchored VM artifact (the
`attempt_position++` path becomes dead and gcc deletes it); under 50 bytes
elsewhere.

**The axis.** `-fno-vm-anchor-bound` / `PCREC_NO_VM_ANCHOR_BOUND`, stamp
`<PREFIX>_VM_START` (`anchored` / `gstart` / `unanchored`, so it reads
against the DFA's own `RX_DFA_SCAN`). Sabotage direction: emit
`subject_length` where the predicate says `search_from` — undetectable by
any answer check (it is a pure cost regression), so the row's detector must
be the **stamp**, and the reach witness is `bracket-array-define` itself.
That asymmetry is worth stating in the row: *a bound that only removes
provably-failing attempts has no answer-level detector, so its sabotage row
is a stamp row.*

**Owed Linux measurement:**

```sh
cd "$OPT1"
# M2.a  baseline + the anchored-DFA control, same artifact family
for P in bracket-array-define evil-alt-nested trim-nested-star ipv4-near-miss; do
  "$OPT1/pcrec/build/pcrec" --features all -p rx -o "$OPT1/$P.c" \
      --pattern "$(cat /home/duxevents/pcrec-bench/bench/capability/patterns/$P.rx)"
  grep -E '^#define RX_(ENGINE|VM_PREFILTER|DFA_SCAN) ' "$OPT1/$P.c"
  cp "$OPT1/$P.h" "$OPT1/art.h"
  gcc -O2 -I"$OPT1" -o "$OPT1/base_$P" "$OPT1/findall.c" "$OPT1/$P.c"
  for S in t-64k t-1m; do "$OPT1/base_$P" "$OPT1/subj/$S.bin" 5; done
done
# EXPECT: bracket-array-define / evil-alt-nested / trim-nested-star read
#   ~3.5 / ~4.1 / ~3.1 ns/byte and IDENTICAL at both sizes;
#   ipv4-near-miss (DFA, start_max = 0) reads ~6 ns TOTAL at both sizes.
#   The last line is the control that says the bound, not the engine, is
#   what separates them.

# M2.b  the HAND-TWIN: in each VM artifact's rx_search_run, replace
#           if (attempt_position >= subject_length) return 0;
#           attempt_position++;
#       with
#           return 0;
#       (the bound start_max == search_from, spelled by hand). Rebuild and
#       re-run the same two subjects.
# EXPECT: all three collapse to a constant ~30-120 ns at BOTH sizes, i.e.
#   the O(1) shape oniguruma and pcre2-interp already read. Answer identity
#   must be checked first: the twin must print matches=0 on both subjects,
#   as the baseline does.

# M2.c  the CARVE-OUT: an UNANCHORED VM artifact must not move.
"$OPT1/base_nested-comment-rec" "$OPT1/subj/t-1m.bin" 5   # built as in M2.a
# EXPECT: unchanged by the twin (the predicate is false there, so no line
#   of its emitted text differs) -- confirm by `cmp` of the two .c files.
```

---

### M3 — `[OPT-FIRSTSET]`: the candidate-start set, derived from the AST

**Rows explained.** `wild-secrets-aws-access-key-id` thr (rank 7, 29.65×
vs rust, **18.93× vs the best scalar engine**) and srch (rank 29),
`wild-codegrammar-json-constant` thr (rank 10, 14.96× / 1.88× scalar),
`wild-waf-crs-942140-dbnames` thr (rank 24, 1.82×). Weighted score
**1.002**.

**Diagnosis.** pcrec derives `rx_can_begin_match[256]` from the bytes that
leave the DFA's start state. A leading `\b` makes that state track word
context, so every word byte leaves it and the set becomes the 63-byte word
class — 77.21% of the throughput text, i.e. the skip loop can never skip.
The minimal witness, built in this worktree, is one construct wide:
`A[A-Z0-9]{16}` stamps `RX_DFA_PREFILTER "memchr"` with a 1-byte set;
`\bA[A-Z0-9]{16}` stamps `byte-class-bounded` with a 63-byte set. PCRE2
records `FIRSTCODEUNIT = 'A'` for both. This is the named cause of
[OPT-3]'s own measured symptom (`opt3_dfa_scan_measurement.md`: the skip
loop *"is entered 190,651 times and skips ZERO bytes"*).

**The mechanism, in general form.** Compute the candidate-start set from the
**bytes that can begin a match** — an AST-level first-byte analysis that
looks *through* leading zero-width assertions (`\b`, `\B`, `^`, `\A`,
lookahead, lookbehind) to the first byte-consuming element — rather than
from the automaton start state's live transitions. Intersect with the
current derivation (never widen it: the start-state set is sound, so the
new set must be a subset or the analysis is wrong, which is a free
compile-time assertion and the natural identity check). Two consumers, one
analysis: (i) the DFA route's existing `rx_can_begin_match` skip loop, whose
representation, sizes and stamps do not change at all — only the set's
contents; (ii) the VM route, where it gives a candidate-start skip to the
eleven `RX_VM_PREFILTER "none"` artifacts that have no prefilter today,
soundly, because a first-byte set is a necessary condition on the match's
own first byte and a backreference or linked call in leading position simply
yields "unknown" and disables it. `nested-comment-rec` is the case that
shows (ii) matters on its own: first byte `/`, 2.86% of the subject, so 35×
fewer attempts than today's every-position walk.

**Architecture fit.** Inside the architecture; it replaces one derivation
inside an existing pass and adds one consumer. It shares its analysis with
M1 (the same bottom-up AST walk returns the first-byte set and the necessary
byte), which is why M1+M2+M3 is the natural batch.

**Size expectation.** Zero on the DFA route (same tables, different
contents; a narrower set can flip `byte-class` to `memchr`, which is
*smaller*). On the VM route it adds one 256-byte table or one `memchr` per
prefilter-less artifact — bounded by `PCREC_MAX_*`, and the `-fno-` flag is
the recourse.

**The axis.** `-fno-first-set` / `PCREC_NO_FIRST_SET` (deny → fall back to
today's start-state derivation, which is exactly what makes this change
bisectable), plus `PCREC_FORCE_FIRST_SET`. Stamp: the existing
`RX_DFA_PREFILTER` value moves on the reached population, which IS the
observable; add `<PREFIX>_VM_PREFILTER` value `first-byte` for consumer
(ii). Sabotage direction: widen the derived set by one byte that cannot
begin a match — invisible to every answer check (it only costs time), so
again a **stamp/count** detector, with the corpus census of
`|can_begin_match|` as the pinned population. `make test-axes` denied/forced
answer-identity over the corpus is the correctness bar.

**Owed Linux measurement:**

```sh
cd "$OPT1"
# M3.a  the minimal witness pair -- the whole claim in two artifacts
for PAT in 'A[A-Z0-9]{16}' '\bA[A-Z0-9]{16}'; do
  "$OPT1/pcrec/build/pcrec" --features all --no-captures -p rx \
      -o "$OPT1/w.c" --pattern "$PAT"
  echo "== $PAT"; grep -E '^#define RX_DFA_PREFILTER ' "$OPT1/w.c"
  cp "$OPT1/w.h" "$OPT1/art.h"
  gcc -O2 -I"$OPT1" -o "$OPT1/w" "$OPT1/findall.c" "$OPT1/w.c"
  "$OPT1/w" "$OPT1/subj/t-1m.bin" 5
done
# EXPECT: memchr / byte-class-bounded, and a ns/byte ratio of roughly the
#   candidate-density ratio (0.17% vs 77.21%). This is the number the
#   mechanism is worth on this shape; if the two artifacts time the SAME,
#   the skip loop is not where the cost is and M3 is refuted.

# M3.b  the three real rows, baseline
for P in wild-secrets-aws-access-key-id wild-codegrammar-json-constant \
         wild-waf-crs-942140-dbnames; do
  "$OPT1/pcrec/build/pcrec" --features all --no-captures -p rx -o "$OPT1/$P.c" \
      --pattern "$(cat /home/duxevents/pcrec-bench/bench/capability/patterns/$P.rx)"
  cp "$OPT1/$P.h" "$OPT1/art.h"
  gcc -O2 -I"$OPT1" -o "$OPT1/base_$P" "$OPT1/findall.c" "$OPT1/$P.c"
  "$OPT1/base_$P" "$OPT1/subj/t-1m.bin" 5
done
# EXPECT 3.83 / 3.05 / 2.97 ns/byte (the matrix's own figures).

# M3.c  the HAND-TWIN: in each artifact, overwrite rx_can_begin_match[256]
#       with the set PCRE2 records -- aws: {'A'} only; json-constant:
#       {'t','f','n'}; dbnames: the 14-bit bitmap (print it with
#       docs/dev/optloop/p2info.c, extended to dump FIRSTBITMAP). Rebuild,
#       re-run t-1m, and CHECK matches= is unchanged from the baseline.
# EXPECT aws-access-key-id to approach pcre2-dfa's 0.20 ns/byte (the 18.93x
#   scalar gap); json-constant and dbnames to approach re2's 1.62 ns/byte.
#   A twin that is answer-identical but NOT faster refutes M3 for that row.

# M3.d  the disassembly read (static, no timer): confirm the skip loop is
#       the thing that changed, not the transition loop.
objdump -d --no-show-raw-insn "$OPT1/base_wild-secrets-aws-access-key-id" \
  | sed -n '/<rx_search>:/,/^$/p' > "$OPT1/aws_base.s"
objdump -d --no-show-raw-insn "$OPT1/twin_wild-secrets-aws-access-key-id" \
  | sed -n '/<rx_search>:/,/^$/p' > "$OPT1/aws_twin.s"
diff "$OPT1/aws_base.s" "$OPT1/aws_twin.s" | head -40
# EXPECT: the only instruction-level difference is inside the
#   `while (... && !rx_can_begin_match[subject[scan_position]]) scan_position++;`
#   block (a different table CONTENT, possibly a different table SIZE if gcc
#   folds a 1-element set to a compare). Any difference in the transition
#   loop means the twin changed more than the candidate set: redo it.
```

---

### M4 — `[OPT-ENDWIN]`: the end-anchor start-window bound

**Row explained.** `wild-semdiv-dollar-trailing-newline-pcre2` thr (rank 4,
**1,401.23×** vs rust, **725.16×** vs the best scalar engine, oniguruma).
Weighted score **0.871**. The pattern is `abc$`.

**Diagnosis.** `rust` reads **25.7 ns at 64 KiB and 25.7 ns at 1 MiB**; re2
99 ns flat; oniguruma 151 ns flat. pcrec reads 3,521 / 16,746 / 89,433 ns —
linear, 0.085 ns/byte. pcrec is already fast *per byte* (its
`RX_DFA_PREFILTER "offset-set-bounded"` skip is working); it is scanning a
megabyte that cannot contain a match at all. Every match of `abc$` must
**end** at the subject end (or just before a final newline), and the
pattern's maximum width is 4, so only start positions in `[n-4, n]` can
match. The three O(1) engines are exploiting that; pcrec is not. This is
exactly the general optimization **D77 named and deferred** — *"the gap is a
FOLD ON THE IDIOM (the skip loop reasoning about `\z`), a general
optimization for every `\z` user, already a [DD-13] candidate for the bench
loop"* — now with the measured number D77 said to wait for.

**The mechanism, in general form.** When every alternative of the pattern
ends in `$`/`\Z`/`\z` (outside multiline) **and** `pcrec_maxw(root)` is
finite, the scan's start window is `[subject_length - maxw - ε,
subject_length]` rather than `[search_from, subject_length]`, where `ε` is
the `$`-before-final-newline allowance (1 byte under the shipped newline
convention). Where `maxw` is unbounded the mechanism declines, which is the
common case and costs nothing. It extends the existing **position view**
axis (`--list-axes`: `view` = `end+eol`/`end`/`eol`/`none`), which already
*recognises* a `\z`/`$` view and uses it to choose the `-bounded` prefilter
candidates — this mechanism gives that same recognised view its second, much
larger consumer: the scan's start bound, not just its accept test.

**Architecture fit.** Inside the architecture: `pcrec_maxw` exists, the view
axis exists, and the bound is one clamp on the loop the DFA already writes.
The VM gets the same clamp through M2's `start_max` if that lands first,
which is another reason to sequence M2 early.

**Size expectation.** Under 100 bytes of emitted C.

**The axis.** `-fno-end-window` / `PCREC_NO_END_WINDOW`, stamp
`<PREFIX>_END_WINDOW` (the `maxw` bound, or `none`). Sabotage direction:
widen the window by one byte too FEW (clamp to `n - maxw + 1`) — this one
**does** have an answer-level detector, because it drops a legal match, and
the reach witness is any `$`-terminated corpus pattern with finite `maxw`.

**Owed Linux measurement:**

```sh
cd "$OPT1"
# M4.a  baseline, and the scaling shape that is the whole claim
"$OPT1/pcrec/build/pcrec" --features all --no-captures -p rx -o "$OPT1/dol.c" --pattern 'abc$'
grep -E '^#define RX_DFA_(PREFILTER|SCAN|START) ' "$OPT1/dol.c"
cp "$OPT1/dol.h" "$OPT1/art.h"
gcc -O2 -I"$OPT1" -o "$OPT1/base_dol" "$OPT1/findall.c" "$OPT1/dol.c"
for S in t-64k t-256k t-1m; do "$OPT1/base_dol" "$OPT1/subj/$S.bin" 5; done
# EXPECT ~3,500 / ~16,700 / ~89,400 ns, matches=0, i.e. LINEAR in n.

# M4.b  the HAND-TWIN: in <prefix>_search, before the scan loop, insert
#           if (subject_length > 5 && search_from < subject_length - 5)
#               search_from = subject_length - 5;   /* maxw(abc$) = 4, +1 for $\n */
#       and re-run. (5 is hand-computed here; the landed mechanism derives
#       it from pcrec_maxw.)
# EXPECT: ~25-150 ns, IDENTICAL at all three sizes -- the O(1) shape.
#   Answer identity: matches=0 on all three, as the baseline reports.

# M4.c  the correctness carve-out the twin must survive, on a MATCHING
#       subject and on one where the match is NOT at the end.
printf 'abc' > "$OPT1/subj/e1.bin"                    # matches at 0
printf 'abc\n' > "$OPT1/subj/e2.bin"                  # $ before final newline
python3 -c "import sys; sys.stdout.buffer.write(b'x'*100000+b'abc')" > "$OPT1/subj/e3.bin"
python3 -c "import sys; sys.stdout.buffer.write(b'abc'+b'x'*100000)" > "$OPT1/subj/e4.bin"
for S in e1 e2 e3 e4; do "$OPT1/base_dol" "$OPT1/subj/$S.bin" 1; \
                          "$OPT1/twin_dol" "$OPT1/subj/$S.bin" 1; done
# EXPECT: matches= agrees base-vs-twin on all four (1,1,1,0). e2 is the
#   trailing-newline case the +1 exists for; e4 is the one a window that is
#   one byte too wide would still get right and a wrong VIEW test would not.
```

---

### M5 — `[OPT-ATTEMPT-SPLIT]`: `^` on some branches costs the whole DFA toolkit

**Rows explained.** `wild-waf-crs-942360-concat-sqli` thr (rank 11, 5.41×
vs `re2-longest`) and srch (rank 27, 1.53×). Weighted score **0.306**.

**Diagnosis.** The pattern carries `^(?:json\.)?...` in one branch of a
1,460-byte top-level alternation. `src/gen/emit_dfa.c:13-17` routes any
pattern containing `^` to `ENG_ATTEMPT`, the per-start-position
computed-goto shape, and says in its own comment that *"fully-anchored
patterns get the start_max=0 fast path, so the slow shape is `^` on only
SOME branches."* This artifact is the slow shape: `start_max = subject_length`,
and its stamps read `RX_DFA_PREFILTER "none"`, `RX_DFA_TABLE "none"`,
`RX_DFA_SCAN_EDGE "none"` — **no prefilter, no premultiplied table, no
[OPT-5] scan edge**, because `ENG_ATTEMPT` has none of that machinery. It
reads 8.83 ns/byte, the highest per-byte cost of any DFA artifact in the
set, against `re2-longest`'s 1.62. One `^` in one branch of a 2,000-state
pattern costs the entire optimization toolkit.

**The mechanism, in general form.** Split a pattern whose top-level
alternation mixes `^`-anchored and unanchored branches into **one attempt of
the original machine at `search_from`**, followed by the ordinary
`ENG_UNANCH` engine — with its prefilter, its premultiplied table and its
scan edge — built from the pattern with the anchored branches removed, for
positions past `search_from`. Leftmost-first is preserved by construction:
at `search_from` the original machine decides (so branch order is the
original's), and no anchored branch can match anywhere later. This is not a
new engine: both halves are engines the tree already emits, and the
"optional contributor" shape is the one `[K53-SELRETRY]`'s drop ladder
already established.

**Architecture fit.** Inside the architecture, but it is the largest of the
five: it builds two machines where one is built today, and the emitted entry
has to sequence them. A real risk the design pass must price is that a
two-machine artifact doubles the table budget on exactly the patterns whose
tables are already largest.

**Size expectation.** Up to **2×** the table bytes on a reached artifact.
That is the axis's whole argument, and it is why this one may belong at a
`--tune` position rather than at the default (D119 item 4's second axis).

**The axis.** `-fno-attempt-split` / `PCREC_NO_ATTEMPT_SPLIT`, stamp
`<PREFIX>_DFA_SCAN` gains the value `attempt+unanchored`. Sabotage
direction: drop the anchored half (answer-detectable: a subject matching
only through the `^` branch answers NOMATCH) and, separately, drop the
`search_from` attempt of the original (also answer-detectable). Reach
witness: `wild-waf-crs-942360-concat-sqli` itself, plus the shipped corpus's
own `attempt`-scan-with-`start_max = subject_length` population, which must
be counted before the row is sized.

**Owed Linux measurement:**

```sh
cd "$OPT1"
P=wild-waf-crs-942360-concat-sqli
"$OPT1/pcrec/build/pcrec" --features all -p rx -o "$OPT1/$P.c" \
    --pattern "$(cat /home/duxevents/pcrec-bench/bench/capability/patterns/$P.rx)"
grep -E '^#define RX_(ENGINE|DFA_SCAN|DFA_PREFILTER|DFA_TABLE|DFA_SCAN_EDGE) ' "$OPT1/$P.c"
grep -m1 'const size_t start_max' "$OPT1/$P.c"
cp "$OPT1/$P.h" "$OPT1/art.h"
gcc -O2 -I"$OPT1" -o "$OPT1/base_$P" "$OPT1/findall.c" "$OPT1/$P.c"
for S in t-64k t-1m; do "$OPT1/base_$P" "$OPT1/subj/$S.bin" 5; done
# EXPECT 8.83 ns/byte at both sizes, start_max = subject_length.

# M5.b  the UPPER BOUND the mechanism is chasing, measured without building
#       it: compile the SAME pattern with its one ^-bearing alternative
#       deleted by hand (it is the `^(?:json\.)?...` arm) and time that.
#       That artifact takes ENG_UNANCH and gets prefilter+table+scan edge.
#       Write the edited pattern to "$OPT1/split.rx" first.
"$OPT1/pcrec/build/pcrec" --features all -p rx -o "$OPT1/split.c" \
    --pattern "$(cat "$OPT1/split.rx")"
grep -E '^#define RX_(DFA_SCAN|DFA_PREFILTER|DFA_TABLE|DFA_SCAN_EDGE) ' "$OPT1/split.c"
cp "$OPT1/split.h" "$OPT1/art.h"
gcc -O2 -I"$OPT1" -o "$OPT1/split" "$OPT1/findall.c" "$OPT1/split.c"
"$OPT1/split" "$OPT1/subj/t-1m.bin" 5
wc -c "$OPT1/$P.c" "$OPT1/split.c"
# EXPECT: ns/byte at or below re2-longest's 1.62, and a SIZE figure that is
#   the other half of the decision -- the landed mechanism emits BOTH
#   machines, so the size to price is the sum. If the split artifact is not
#   materially faster, ENG_ATTEMPT is not the cost and M5 is refuted.
```

---

### M6 — the measurement that would name a sixth mechanism (no mechanism yet)

§2.3(f)'s eleven rows (weighted 1.004) are VM rows where pcrec and the
winner are both linear and pcrec costs 1.05–5.2× per byte. Nothing in the
emitted C names a mechanism: `rx_reset_for_next_attempt` is O(trail depth),
i.e. proportional to work already done. **A mechanism must not be proposed
before the profile says what the per-byte cost is.** The measurement:

```sh
cd "$OPT1"
for P in nested-comment-rec quoted-delim-match balanced-parens-rec; do
  "$OPT1/pcrec/build/pcrec" --features all -p rx -o "$OPT1/$P.c" \
      --pattern "$(cat /home/duxevents/pcrec-bench/bench/capability/patterns/$P.rx)"
  cp "$OPT1/$P.h" "$OPT1/art.h"
  gcc -O2 -I"$OPT1" -o "$OPT1/base_$P" "$OPT1/findall.c" "$OPT1/$P.c"
  "$OPT1/base_$P" "$OPT1/subj/t-1m.bin" 5
  objdump -d --no-show-raw-insn "$OPT1/base_$P" \
    | sed -n '/<rx_match_anchored>:/,/^$/p' | wc -l
done
# Then: instrument a COPY of each artifact with a counter incremented once
# per rx_match_anchored call and once per VM dispatch step, run it on t-1m,
# and divide the measured wall time by each count. That gives ns/attempt
# and ns/step separately -- which is the fact that decides whether the
# bucket is an attempt-COUNT problem (M2/M3 territory) or a per-STEP
# problem (an emitted-code problem), and no proposal should precede it.
```

---

### 3.1 The three PARKED rows, placed in the same ranking

D119's sequencing note says the parked rows compete with fresh findings for
the same lane. Scored by the same rule — the weighted score of the
`capability@0.1` rows each would move — all three score **zero**, and the
matrix does not support any of them. Said plainly, because that is the
result:

**[ENG-ISL]** (the VM alternation island, STEP 1 shipped at `cee7c741`).
**Score 0 on this subbench.** The island already fires here: four patterns
carry `RX_VM_ALT_ISLANDS ≥ 1` (`logparse-atomic` 2, `logparse-atomic-removed` 2,
`wild-secrets-aws-access-key-id` 1, `wild-secrets-username-password-pair` 2),
and none of the four is a losing row *because of* its alternation. The
remaining [ENG-ISL] work is STEP 2's shapes (the `ab[cd]|abx` tail form, the
class-member expansion) and there is **no pattern in `capability@0.1` whose
losing row those shapes would move**. Its measured customer is still
`bench/altwide` (the ×8.87/×20.1 order effect at w-256/w-512, the VM refusal
wall), which this cycle did not analyse. The honest statement is *not in
this matrix*, not *refuted*.

**[CLS-TREE]** (the class-matcher kit). **Score 0 on this subbench, and
structurally so.** Every testee here compiles for byte semantics and **no
pattern in the set uses `\p{...}`** — the code-point-class population the
study measured (312 script sets, K53's six, `\P{Unknown}`) has no member
here. The one candidate that looked adjacent is
`wild-datetime-datefinder-alternation`'s size-cap refusal, and it is not a
class problem: its diagnostic is *"A repeat's body is replicated and counts
MULTIPLY through nesting"*, `--no-captures` compiles it at 20,432 bytes of
code against 670,153 with captures, and neither `--unroll=1` (675,615) nor
`--tune=min-size` (670,109) moves it. That is VM lowering size, §4.
[CLS-TREE]'s own D77 trigger (K53/K55) is unchanged and is elsewhere.

**[DD-13]** (the `.rxt` format half). **Not an optimization row at all.** It
moves no cell in any matrix by construction; it is ranked here only because
the brief asked, and the answer is that it does not belong in this ranking.

---

## 4. Fundamental / deferral dispositions

One line each, for every losing or non-numeric cell no mechanism above
covers. A recorded deferral is a result (D119 item 3).

| cell | disposition | reason |
|---|---|---|
| `negation-scope-lookbehind-var` thr + srch | **MODULE GAP, not a performance gap** | Variable-length lookbehind is not implemented; `onig`, `re2`, `re2-longest`, `rust`, `tre` and `vectorscan` all declare it unsupported too, and `pcre2-dfa` gives up. Only the PCRE2 interpreter and JIT answer. Nothing to optimize; it is a feature row. |
| `wild-datetime-datefinder-alternation` thr + srch (captures on) | **SIZE, own row, not cycle 1** | 670,153 bytes of emitted VM code against the 500,000 limit; `--no-captures` takes the DFA at 20,432 bytes of code. The VM's lowering of a ~2,200-branch alternation carrying ~100 capture groups is linear in (total literal bytes × capture slots) where the DFA's is not. Neither `--unroll=1` nor `--tune=min-size` rescues it. A VM-lowering size row, adjacent to [ENG-ISL] STEP 2, not to [CLS-TREE]. |
| `evil-alt-nested` srch | **NO RANKING GROUP** | Every roster engine is excluded (§1.2). The two "wrong" subjects are the two the PCRE2 oracle itself gave up on at derivation time and `NOTES.md` records as dropped from `expectations.tsv`; the label needs a bench-side read before it is called a divergence. Not a timing target under any reading. |
| `trim-nested-star` srch, default config (8.97 ms vs `auto-nocaps`'s 419 ns) | **BACKTRACKING, FUNDAMENTAL for this engine** | `^(\s+)*$` on a ≤75-byte subject with whitespace runs is ambiguous decomposition; the VM explores it, the DFA does not. M2's start bound does not help (the subject is short, the cost is inside one attempt). pcrec's own `--no-captures` DFA answers it 21,411× faster, so the *engine* is not missing anything — the **capture-forced VM selection** is. Candidate for a later cycle: a partial-capture route (`f2_rescue_split.md` §"design-event candidates" already names two). Not cycle 1. |
| `balanced-parens-rec`, `nested-comment-rec`, `quoted-delim-match`, `currency-lookbehind-fixed`, `dup-param-detect` srch, `tag-pair-match` srch, `tag-depth3-bound` srch, `bracket-array-define` srch | **DEFERRED PENDING M6's PROFILE** | 1.05–5.2× against `onig`/`pcre2-interp`, both engines linear, no mechanism visible from the emitted C. §3 M6 is the measurement that would name one; proposing a mechanism first would be building ahead of measurement (D77, memory `pcrec-build-under-measurement`). |
| `wild-secrets-github-pat`, `keyword-prefix-order`, `wild-waf-crs-942160-sleep-benchmark`, `router-prefix-order`, `uuid-near-miss` thr, `wild-validator-ipv4-owasp` thr, `ipv4-near-miss` thr, `wild-secrets-aws-access-key-id` srch, `wild-waf-crs-942360-concat-sqli` srch | **SIMD-PHASE DEFERRAL** | pcrec already beats **every scalar engine** on these nine rows (0.21×–0.98×); only `rust` is ahead, with a vectorized multi-literal prefilter. D119 defers SIMD to the end of the loop. Recording them here means the SIMD phase starts with a named population instead of a survey. |
| `wild-waf-crs-942270-union-select` (2.28× scalar), `wild-semdiv-altorder-foo-foobar-rustregex` (1.26×), `file-ext-order` (1.17×) | **RESIDUAL MULTI-LITERAL GAP, not sized for cycle 1** | After the SIMD subtraction these keep a real but small scalar gap against `re2`/`re2-longest`. The mechanism would be a scalar multi-literal (Aho-Corasick-shaped) prefilter — a genuinely new primitive, not an extension of one, so it is the largest architecture bet on this page for the smallest measured return. Revisit when M1–M4 have landed and the matrix is re-run. |
| `wild-codegrammar-json-constant` (1.88× scalar), `wild-waf-crs-942140-dbnames` (1.82×) | **COVERED BY M3, partially** | Both carry the 63-byte `can_begin_match` of §2.3(d). M3's hand-twin (M3.c) is what says how much of the 1.88×/1.82× the first-byte fix recovers and how much is residual multi-literal. |

**Two non-findings worth recording so nobody re-derives them.**
D119's **engine-selection** bucket (VM where the DFA could serve) is
**empty** here: every VM-routed losing row is VM-routed for a construct the
DFA cannot express. D119's **per-call-overhead** bucket is empty *in pcrec's
disfavour*: pcrec holds the best floor in the roster (665 ns against
`rust`'s 1,228 and `pcre2-interp`'s 2,583) and wins 53 of 62 short-regime
rows.

---

## 5. Proposed plan rows, for Frank to ratify

`docs/dev/plan.md` is **not edited by this lane**. These are the rows as
they would be written, in `plan.md`'s own format. Each names its D119
landing-bar cells: the exact `(pattern, regime)` cells whose median must
improve by more than their IQR, and the carve-out cells that must not
regress by more than theirs. Sizes are S/M/L in the house sense (S = one
predicate and one emitted line; M = a pass-level analysis with two
consumers; L = a second machine).

**A note on the bar's feasibility.** At the analysis pin the per-cell
spreads are tiny against the gaps — `bracket-array-define` thr `auto-caps`
carries a median of 4,880,764 ns against a `stddev_ns` of 1,303 (0.027%),
`tag-depth3-bound` thr 4,512,599 against 11,175 (0.25%), `floor-byte` thr
23,115 against 40 (0.17%). The bar will not be the hard part on the target
cells; the carve-outs are where it bites, which is why every row below names
`floor-byte` in both regimes.

```
- [OPT-REQBYTE] STATE:not-started (SIZE S-M) (PROPOSED 2026-09-22 by
  [OPTLOOP.1.analysis], docs/dev/optloop/cycle1_analysis.md M1 — the
  largest single weighted gap in capability@0.1, 3.714 of the losing
  rows' 10.284) — THE REQUIRED-BYTE WHOLE-WINDOW PRE-CHECK. Compute at
  compile time, from the AST, a byte every match must contain past its
  start (PCRE2's PCRE2_INFO_LASTCODETYPE/LASTCODEUNIT, `man pcre2api`);
  emit it and test it ONCE per <prefix>_search call, before the attempt
  loop, with the memchr the prefilter path already emits. Extends the
  prefilter primitive (RX_DFA_PREFILTER "memchr" is the same instrument
  keyed on a candidate START); serves BOTH engines, which is the point,
  since the VM's hybrid prefilter is declined outright for backrefs and
  linked calls (src/opt/select_engine.c:604,651) and three of the five
  target cells are exactly those declines. Axis -fno-req-byte /
  PCREC_NO_REQ_BYTE, stamp <PREFIX>_REQ_BYTE, one src/core/axes.def row;
  sabotage inverts the memchr sense (answer-detectable). PROFILE FIRST
  (D77): cycle1_analysis.md M1.a/M1.b/M1.c, exact commands for the Linux
  executor. LANDING BAR — improve: (tag-depth3-bound, thr),
  (dup-param-detect, thr), (tag-pair-match, thr),
  (wild-secrets-username-password-pair, thr),
  (wild-logparse-winpath-grok, thr). Do not regress: (floor-byte, thr),
  (floor-byte, srch), (wild-secrets-github-pat, thr),
  (router-prefix-order, thr), (email-nested-plus, thr) — every one a cell
  where the required byte is PRESENT, so the memchr is pure added cost.
```

```
- [OPT-ANCHOR-VM] STATE:not-started (SIZE S) (PROPOSED 2026-09-22 by
  [OPTLOOP.1.analysis], cycle1_analysis.md M2 — the single largest RATIO
  in the matrix, 52,122.95x, and the three worst DEFAULT-CONFIG cells in
  the set) — THE START-POSITION BOUND IN THE VM'S ATTEMPT LOOP. The DFA
  emitter already derives a three-valued start_max (0 for ^, search_from
  for \G, subject_length otherwise; src/gen/emit_dfa.c:6802-6812); the VM
  emitter writes `for (;;)` with no bound. Derive the same fact one layer
  up (AST/NFA, since a VM-routed pattern has no DFA to ask) and have both
  emitters read ONE predicate — implement-then-replace, not a parallel
  mechanism. Population: 14 of capability@0.1's 64 patterns are
  PCRE2_ANCHORED and VM-routed at auto-caps; 3 carry
  RX_VM_PREFILTER "none" and have no rescue at all. Axis
  -fno-vm-anchor-bound / PCREC_NO_VM_ANCHOR_BOUND, stamp
  <PREFIX>_VM_START (anchored/gstart/unanchored). NOTE FOR THE SABOTAGE
  ROW: a bound that only removes provably-failing attempts has NO
  answer-level detector, so the row is a STAMP row with
  bracket-array-define as its reach witness. PROFILE FIRST:
  cycle1_analysis.md M2.a/M2.b/M2.c. LANDING BAR — improve:
  (bracket-array-define, thr), (bracket-array-define, srch), and at the
  auto-caps ARM specifically (evil-alt-nested, thr) and
  (trim-nested-star, thr), which the best-variant ranking hides.
  Do not regress: (floor-byte, thr), (floor-byte, srch),
  (nested-comment-rec, thr), (codegrammar-flat, thr) — unanchored VM
  artifacts whose emitted text must be byte-identical.
```

```
- [OPT-FIRSTSET] STATE:not-started (SIZE M) (PROPOSED 2026-09-22 by
  [OPTLOOP.1.analysis], cycle1_analysis.md M3; NAMES THE CAUSE of
  [OPT-3]'s own measured symptom, docs/dev/opt3_dfa_scan_measurement.md
  "the skip loop is entered 190,651 times and skips ZERO bytes") — THE
  CANDIDATE-START SET, DERIVED FROM THE AST RATHER THAN FROM THE DFA'S
  START STATE. A leading \b makes the start state track word context, so
  rx_can_begin_match[256] becomes the 63-byte word class: MEASURED
  minimal witness, `A[A-Z0-9]{16}` stamps memchr with a 1-byte set and
  `\bA[A-Z0-9]{16}` stamps byte-class-bounded with a 63-byte one, while
  PCRE2 records FIRSTCODEUNIT='A' for both. Compute the first-byte set
  from the bytes that can BEGIN A MATCH, looking through leading
  zero-width assertions; intersect with today's derivation, never widen
  (a free compile-time assertion and the natural identity check). TWO
  CONSUMERS, ONE ANALYSIS: the DFA's existing skip loop (contents change,
  representation does not) and the VM's eleven RX_VM_PREFILTER "none"
  artifacts, which gain a candidate-start skip they have none of today
  (nested-comment-rec: first byte '/', 2.86% of the bench text, 35x fewer
  attempts). Shares its AST walk with [OPT-REQBYTE]. Axis -fno-first-set
  / PCREC_NO_FIRST_SET + PCREC_FORCE_FIRST_SET; the sabotage widens the
  set by one impossible byte and is therefore a STAMP/COUNT row, pinned
  against a corpus census of |can_begin_match|. PROFILE FIRST:
  cycle1_analysis.md M3.a-M3.d. LANDING BAR — improve:
  (wild-secrets-aws-access-key-id, thr),
  (wild-codegrammar-json-constant, thr),
  (wild-waf-crs-942140-dbnames, thr), (nested-comment-rec, thr).
  Do not regress: (floor-byte, thr), (floor-byte, srch),
  (wild-logparse-quotedstring-grok, thr), (high-byte-run, thr),
  (uuid-near-miss, srch) — cells whose prefilter is already narrow, where
  the new derivation must produce the identical set.
```

```
- [OPT-ENDWIN] STATE:not-started (SIZE M) (PROPOSED 2026-09-22 by
  [OPTLOOP.1.analysis], cycle1_analysis.md M4 — D77's OWN NAMED
  CANDIDATE, "a FOLD ON THE IDIOM (the skip loop reasoning about \z), a
  general optimization for every \z user", now with the measured number
  D77 said to wait for: 1,401x against rust and 725x against the best
  scalar engine on `abc$`) — THE END-ANCHOR START-WINDOW BOUND. When
  every alternative ends in $/\Z/\z outside multiline AND pcrec_maxw is
  finite, the scan's start window is [n - maxw - eps, n], not
  [search_from, n]; eps is the $-before-final-newline allowance. Extends
  the EXISTING position-view axis (--list-axes `view` already recognises
  the \z/$ view and uses it to pick the -bounded prefilter candidates):
  this gives that recognised view its second and much larger consumer,
  the scan's start bound rather than only its accept test. Declines where
  maxw is unbounded, which costs nothing. Axis -fno-end-window /
  PCREC_NO_END_WINDOW, stamp <PREFIX>_END_WINDOW; the sabotage clamps one
  byte too FEW and IS answer-detectable (it drops a legal match).
  PROFILE FIRST: cycle1_analysis.md M4.a/M4.b/M4.c, including the four
  correctness carve-out subjects (match at 0 / trailing newline / match
  at the end of 100 KB / match at the start of 100 KB). LANDING BAR —
  improve: (wild-semdiv-dollar-trailing-newline-pcre2, thr).
  Do not regress: (floor-byte, thr), (floor-byte, srch),
  (wild-validator-email-owasp, thr), (uuid-near-miss, thr),
  (ipv4-near-miss, thr) — anchored-at-both-ends cells already at O(1),
  where a second bound must be free.
```

```
- [OPT-ATTEMPT-SPLIT] STATE:not-started (SIZE M-L) (PROPOSED 2026-09-22
  by [OPTLOOP.1.analysis], cycle1_analysis.md M5; the emitter's own
  comment already names the shape, src/gen/emit_dfa.c:13-17 "the slow
  shape is ^ on only SOME branches") — `^` IN ONE BRANCH STOPS COSTING
  THE WHOLE DFA TOOLKIT. A pattern containing ^ routes to ENG_ATTEMPT,
  which has no prefilter, no premultiplied table and no [OPT-5] scan
  edge; when it is FULLY anchored start_max=0 makes that free, and when
  it is not it pays for everything (wild-waf-crs-942360-concat-sqli:
  RX_DFA_PREFILTER/TABLE/SCAN_EDGE all "none", start_max =
  subject_length, 8.83 ns/byte, the highest per-byte cost of any DFA
  artifact in the set, against re2-longest's 1.62). Split into ONE
  attempt of the original machine at search_from, then the ordinary
  ENG_UNANCH engine built from the pattern with the anchored branches
  removed; leftmost-first holds by construction. Both halves are engines
  the tree already emits; the "optional contributor" shape is
  [K53-SELRETRY]'s. SIZE IS THE ARGUMENT AGAINST IT: up to 2x the table
  bytes on exactly the patterns whose tables are already largest, so this
  may belong at a --tune position rather than at the default (D119 item
  4's second axis). PRECONDITION: count the shipped corpus's own
  ENG_ATTEMPT-with-start_max=subject_length population before sizing the
  row (D81's 2026-08-25 census recorded 180 of 995 DFA artifacts on the
  attempt scan and did NOT split them by start_max). Axis
  -fno-attempt-split / PCREC_NO_ATTEMPT_SPLIT, stamp value
  RX_DFA_SCAN "attempt+unanchored"; both sabotage directions are
  answer-detectable. PROFILE FIRST: cycle1_analysis.md M5.a/M5.b.
  LANDING BAR — improve: (wild-waf-crs-942360-concat-sqli, thr),
  (wild-waf-crs-942360-concat-sqli, srch). Do not regress:
  (ipv4-near-miss, thr), (uuid-near-miss, thr), (base10num-near-miss,
  thr), (winpath-near-miss, thr), (wild-validator-email-owasp, thr) —
  the five FULLY anchored attempt-scan artifacts, whose emitted text must
  be byte-identical because the predicate is false for them.
```

```
- [OPTLOOP.1.M6] STATE:not-started (SIZE S, MEASUREMENT ONLY) (PROPOSED
  2026-09-22 by [OPTLOOP.1.analysis], cycle1_analysis.md M6) — WHAT THE
  VM COSTS PER ATTEMPT AND PER STEP. Eleven losing rows (weighted 1.004)
  are VM rows where pcrec and the winner are both linear and pcrec costs
  1.05-5.2x per byte, and NOTHING in the emitted C names a mechanism
  (rx_reset_for_next_attempt is O(trail depth), i.e. proportional to work
  already done). Instrument a COPY of nested-comment-rec /
  quoted-delim-match / balanced-parens-rec with a per-call and a
  per-dispatch-step counter, run on t-1m, and divide: ns/attempt and
  ns/step SEPARATELY. That number decides whether the bucket is an
  attempt-COUNT problem ([OPT-ANCHOR-VM]/[OPT-FIRSTSET] territory) or a
  per-STEP problem (an emitted-code problem), and NO mechanism should be
  proposed before it (D77; memory pcrec-build-under-measurement).
  Nothing under src/. LANDING BAR: n/a, the deliverable is the number.
```

**Sequencing recommendation.** D119 caps an implementation batch at three
mechanisms. **Batch 1 = [OPT-REQBYTE] + [OPT-ANCHOR-VM] + [OPT-FIRSTSET]**:
they carry 6.828 of the 8.005 weighted score the five cover, the first and
third share one AST walk, and all three are extensions of primitives that
already exist rather than new machinery. `[OPT-ENDWIN]` and
`[OPT-ATTEMPT-SPLIT]` are batch 2, and `[OPTLOOP.1.M6]` can run as a
measurement lane beside either, since it touches nothing.

**Run [OPTLOOP.1.M6] and every `PROFILE FIRST` block before any
implementation lane opens.** They are all one Linux executor session on
ubuntubudu and they share the setup in §3; several of them are capable of
refuting their own mechanism, which is what they are for.

---

## 6. What this analysis does NOT establish

- **No timing was taken on this box.** Every pcrec-vs-engine number is the
  bench's Ryzen 1600 measurement at pin `25b1984f`; every pcrec structural
  fact is from `ab341bfe`'s own compiler. The two pins differ by
  [REL-1.4]'s version/`abi` stamp, which this lane confirmed accounts for
  the 39–46-byte size difference on the one artifact where it is visible
  (`wild-datetime-datefinder-alternation`'s refusal byte count) and for
  nothing else it looked at.
- **The `pcre2_pattern_info` facts were measured against libpcre2 10.48
  (Homebrew)**, not the 10.46 reference. They are structural pattern
  properties, so drift is unlikely, but the executor should re-run
  `docs/dev/optloop/p2info.c` against 10.46 on ubuntubudu if any of them
  becomes load-bearing for a landed change.
- **The 0.0169 ns/byte floor rate is an observation, not an identification.**
  Three independent engines share it and pcrec is the fastest of them, which
  is what licenses calling it "one `memchr`-class pass". No disassembly of
  libpcre2 was done and none is needed for the mechanism, whose own witness
  is pcrec's `floor-byte` row.
- **The `evil-alt-nested` short-regime "wrong" labels are unresolved.** §1.2
  gives the reason to suspect a dropped-expectation artifact rather than a
  pcrec divergence; confirming it is a bench-side read this lane could not
  make.
- **Nothing here re-ranks the other five sub-benches.** `bench/altwide`,
  `bench/bounded`, `bench/loglines`, `bench/syntax` and
  `bench/email-specimen` were not analysed, which is why [ENG-ISL]'s
  zero in §3.1 is "not in this matrix" and not "refuted".
