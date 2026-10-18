### 1. Population (K35)

| pop | cfg | rows | compiled | refused | error | lang: own machine | lang: --engine=dfa | lang: anchor-stripped body | lang: nullable | lang: PCRE2 only | lang: none | VM artifacts | search sites |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bench | native | 367 | 342 | 25 | 0 | 227 | 16 | 32 | 3 | 59 | 5 | 75 | 354 |
| bench | utf8 | 291 | 269 | 22 | 0 | 161 | 15 | 28 | 3 | 0 | 62 | 72 | 306 |
| corpus | native | 4816 | 4442 | 374 | 0 | 1952 | 607 | 249 | 9 | 1515 | 110 | 2088 | 3627 |
| corpus | utf8 | 4298 | 3951 | 347 | 0 | 1569 | 583 | 234 | 8 | 0 | 1557 | 2023 | 3333 |

Cross-check (sampled 15% of byte rows read off their own machine, re-read by PCRE2 alone, uncapped): 262 rows; span agrees 257, exact agrees 257, whole-cover agrees 256.

- xc disagreement tests/assertions/d27/anchors_abs.rxt:63 native `\zabc`
- xc disagreement tests/assertions/rev_end.rxt:210 native `\d+$(?=\n)`
- xc disagreement tests/lookaround/alpha_spellings.rxt:356 native `(*negative_lookbehind:a)(?:a\|b)`
- xc disagreement tests/offsetskip/offset_skip.rxt:68 native `\bat [a-z]`
- xc disagreement tests/possessify/composition_d27.rxt:518 native `\d{1,2}(?:(?<!\w)\|)\B`
- xc disagreement tests/possessify/composition_d27.rxt:1883 native `[a-c]{1,2}\B\w`
- xc disagreement tests/possessify/composition_d27.rxt:2003 native `-{0,}?(?<!\W)-`
- xc disagreement tests/possessify/composition_d27.rxt:3668 native `a*(?:a\|\b)`
- xc disagreement tests/possessify/composition_d27.rxt:10055 native `(?:a\|A)*\b`
- xc disagreement tests/recursion/d27/sr_interactions.rxt:378 native `(?(DEFINE)(?<g>\bab))(?&g)`
- xc disagreement tests/ucp/ctxnode.rxt:162 native `(?<![a-c])\d`

Refusal reasons (first words of pcrec's diagnostic):

| pop | cfg | reason | rows |
|---|---:|---:|---:|
| corpus | native | quantifier does not follow | 69 |
| corpus | utf8 | quantifier does not follow | 68 |
| corpus | native | variable-length lookbehind is not | 39 |
| corpus | utf8 | variable-length lookbehind is not | 39 |
| corpus | native | UCP/utf8 | 28 |
| corpus | utf8 | UCP/utf8 | 25 |
| corpus | native | module 'unicode-props' is enabled | 22 |
| corpus | native | \p{...}: not a one-letter | 19 |
| corpus | utf8 | \p{...}: not a one-letter | 19 |
| corpus | native | too large | 17 |
| corpus | native | invalid | 16 |
| corpus | utf8 | invalid | 16 |
| corpus | native | \K is not allowed | 15 |
| corpus | utf8 | \K is not allowed | 15 |
| corpus | utf8 | module 'unicode-props' is enabled | 15 |
| corpus | native | a relative reference of | 14 |
| corpus | utf8 | a relative reference of | 14 |
| corpus | native | two named subpatterns have | 13 |
| corpus | utf8 | two named subpatterns have | 13 |
| corpus | native | missing closing ) for | 12 |
| corpus | utf8 | missing closing ) for | 12 |
| corpus | native | number too big in | 10 |
| corpus | utf8 | number too big in | 10 |
| corpus | native | multiple quantifiers on the | 9 |
| corpus | utf8 | multiple quantifiers on the | 9 |

No language machine (anchored DFA absent under `--engine=dfa --no-captures -fno-scan-edge`):

| pop | cfg | why | rows |
|---|---:|---:|---:|
| corpus | utf8 | no-anchored | 260 |
| corpus | utf8 | pcrec: \1 requires the VM engine, w | 220 |
| corpus | utf8 | pcrec: (?>...) requires the VM engi | 167 |
| corpus | utf8 | pcrec: (?=...) requires the VM engi | 144 |
| corpus | utf8 | pcrec: (?<=...) requires the VM eng | 132 |
| corpus | utf8 | pcrec: possessive quantifier requir | 81 |
| corpus | utf8 | pcrec: (?!...) requires the VM engi | 78 |
| corpus | utf8 | pcrec: \K requires the VM engine, w | 77 |
| corpus | utf8 | pcrec: (?<!...) requires the VM eng | 59 |
| corpus | utf8 | pcrec: \k<name> requires the VM eng | 57 |
| corpus | utf8 | pcrec: (?*a) requires the VM engine | 48 |
| corpus | utf8 | pcrec: (?<*a) requires the VM engin | 43 |
| corpus | utf8 | pcrec: (?1) requires the VM engine, | 38 |
| corpus | utf8 | pcrec: \g{-1} requires the VM engin | 37 |
| corpus | native | no-anchored | 31 |

Other (non-search) kit sites seen, per artifact:

| site | instances |
|---|---:|
| EDGE | 3702 |
| VMSPAN | 2522 |
| N7 | 836 |
| VMRUN | 529 |
| STAY | 283 |
| VMSTRIDE | 151 |

### 2. The search sites: origin, what is sent, what the kit proves today

| cfg | site | consumer kind | origin | sites |
|---|---:|---:|---:|---:|
| native | MLINE | DFA_ATTEMPT | after-nl | 33 |
| native | OFS | DFA_SCAN | scan-restart | 5 |
| native | OFS | DFA_SCAN | start | 645 |
| native | PF | DFA_HAT | scan-restart | 1 |
| native | PF | DFA_HAT | start | 88 |
| native | PF | DFA_SCAN | scan-restart | 125 |
| native | PF | DFA_SCAN | scan-restart/ctx | 19 |
| native | PF | DFA_SCAN | start | 1101 |
| native | PF | HYB_PF | scan-restart | 134 |
| native | PF | HYB_PF | scan-restart/ctx | 4 |
| native | PF | HYB_PF | start | 680 |
| native | PF | VM_ATTEMPT | start | 256 |
| native | PRE | DFA_ATTEMPT | landmark | 16 |
| native | PRE | DFA_ATTEMPT | presence | 12 |
| native | PRE | DFA_SCAN | landmark | 117 |
| native | PRE | DFA_SCAN | presence | 253 |
| native | PRE | HYB_PF | landmark | 101 |
| native | PRE | HYB_PF | presence | 134 |
| native | PRE | VM_ATTEMPT | presence | 257 |
| utf8 | MLINE | DFA_ATTEMPT | after-nl | 32 |
| utf8 | OFS | DFA_SCAN | start | 649 |
| utf8 | PF | DFA_HAT | start | 79 |
| utf8 | PF | DFA_SCAN | scan-restart | 119 |
| utf8 | PF | DFA_SCAN | scan-restart/ctx | 21 |
| utf8 | PF | DFA_SCAN | start | 732 |
| utf8 | PF | HYB_PF | scan-restart | 82 |
| utf8 | PF | HYB_PF | scan-restart/ctx | 2 |
| utf8 | PF | HYB_PF | start | 695 |
| utf8 | PF | VM_ATTEMPT | start | 236 |
| utf8 | PRE | DFA_ATTEMPT | landmark | 17 |
| utf8 | PRE | DFA_ATTEMPT | presence | 16 |
| utf8 | PRE | DFA_SCAN | landmark | 143 |
| utf8 | PRE | DFA_SCAN | presence | 286 |
| utf8 | PRE | HYB_PF | landmark | 113 |
| utf8 | PRE | HYB_PF | presence | 177 |
| utf8 | PRE | VM_ATTEMPT | presence | 240 |

Offsets sent (span 0 / `preds` of a presence site; `R`/`O` = REQUIRED/OPTIONAL, `+k` a run):

| site | sent | sites |
|---|---:|---:|
| PF | 0R | 4374 |
| OFS | 0O,1O | 1019 |
| OFS | 0+2R | 73 |
| MLINE | -1R | 65 |
| OFS | 0O,2O | 57 |
| OFS | 0O,3O | 30 |
| OFS | 0+3R | 18 |
| OFS | 0O,1+1R | 15 |
| OFS | 0+1R | 13 |
| OFS | 0+4R | 10 |
| OFS | 0O,4O | 9 |
| OFS | 0O,5O | 8 |
| OFS | 0+7R | 7 |
| OFS | 0+6R | 6 |
| OFS | 0O,6O | 5 |
| OFS | 0O,8O | 4 |
| OFS | 0O,1+7R | 3 |
| OFS | 0O,1+2R | 3 |
| OFS | 0O,1+4R | 3 |
| OFS | 0O,7O | 2 |

| site | term need | terms |
|---|---:|---:|
| MLINE | R | 65 |
| OFS | O | 2314 |
| OFS | R | 158 |
| PF | R | 4374 |

`proven0` against the language's first-byte set S_0 at a START origin (`exact` = equal; `superset` = proves less than S_0 allows; a site whose span-0 set is strictly NARROWER than S_0 is reclassified `scan-restart`: the forward scan restarts where its start row stops self-looping and the reverse pass recovers the start):

| cfg | site | proven0 vs S_0 | sites |
|---|---:|---:|---:|
| native | MLINE | n/a | 4 |
| native | MLINE | none | 29 |
| native | OFS | exact | 625 |
| native | OFS | n/a | 25 |
| native | PF | exact | 1924 |
| native | PF | n/a | 445 |
| native | PF | superset | 39 |
| native | PRE | n/a | 890 |
| utf8 | MLINE | n/a | 14 |
| utf8 | MLINE | none | 18 |
| utf8 | OFS | exact | 505 |
| utf8 | OFS | n/a | 144 |
| utf8 | PF | exact | 950 |
| utf8 | PF | n/a | 1008 |
| utf8 | PF | superset | 8 |
| utf8 | PRE | n/a | 992 |

`proven0` against the forward machine's ESCAPE set E (the bytes that move its start row; read off the emitted table): `eq`; `wider` = proves less than E; `UNDER-esc` = narrower than E (a dropped restart):

| cfg | kind | proven0 vs E | sites |
|---|---:|---:|---:|
| native | DFA_HAT | n/a | 89 |
| native | DFA_SCAN | UNDER-esc-view | 4 |
| native | DFA_SCAN | differ-view | 3 |
| native | DFA_SCAN | eq | 1770 |
| native | DFA_SCAN | n/a | 118 |
| native | HYB_PF | eq | 790 |
| native | HYB_PF | n/a | 28 |
| native | VM_ATTEMPT | n/a | 256 |
| utf8 | DFA_HAT | n/a | 79 |
| utf8 | DFA_SCAN | UNDER-esc-view | 3 |
| utf8 | DFA_SCAN | differ-view | 2 |
| utf8 | DFA_SCAN | eq | 1397 |
| utf8 | DFA_SCAN | n/a | 119 |
| utf8 | HYB_PF | eq | 750 |
| utf8 | HYB_PF | n/a | 29 |
| utf8 | VM_ATTEMPT | n/a | 236 |

| site | proven_prev states something | sites |
|---|---:|---:|
| MLINE | True | 65 |
| OFS | False | 1299 |
| PF | False | 4374 |
| PRE | False | 1882 |

### 3. The exact prefix from the origin

| cfg | length | sites | 0 | 1 | 2 | 3-4 | 5-8 | 9-16 | 17-31 | 32 (cap) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| native | exact | 2617 | 0 | 1445 | 591 | 370 | 108 | 49 | 9 | 45 |
| native | span | 2617 | 0 | 1278 | 579 | 467 | 152 | 71 | 21 | 49 |
| utf8 | exact | 1481 | 0 | 727 | 329 | 268 | 97 | 33 | 7 | 20 |
| utf8 | span | 1481 | 0 | 634 | 295 | 334 | 119 | 55 | 20 | 24 |

MIXED (exact for a prefix, SUPERSET after it inside the span): sites with exact < span:

| cfg | mixed | sites |
|---|---:|---:|
| native | 0 | 2307 |
| native | 1 | 310 |
| utf8 | 0 | 1280 |
| utf8 | 1 | 201 |

utf8-born mixing (`abc[α-ω]`-shaped): rows exact over the whole span in byte, mixed under `-e utf8`: **65** patterns (12 of them bench). Examples:

- `(?:[^,\n]{0,32},){4}[^,\n]{0,32}` bounded/csv5: byte exact 4/4, utf8 exact 1/4
- `.{80,}` bounded/line-80: byte exact 32/32, utf8 exact 1/32
- `.{8,64}` bounded/pw-8-64: byte exact 8/8, utf8 exact 1/8
- `.*\.txt$` capability/tail-dotstar-txt: byte exact 4/4, utf8 exact 1/4
- `(?i)https://hooks.slack.com/services/(T[a-z0-9_]{8}/B[a-z0-9` capability/wild-secrets-slack-webhook-url: byte exact 32/32, utf8 exact 5/32
- `(?i)union.*?select.*?from` capability/wild-waf-crs-942270-union-select: byte exact 15/15, utf8 exact 6/15
- `c.t` syntax/cls-dot: byte exact 3/3, utf8 exact 2/3
- `it\Nm` syntax/cls-n-uc: byte exact 4/4, utf8 exact 3/4

### 4. consumable_len per consumer kind

(a) plain unseeded DFA (DFA_SCAN incl. offset-skip FUNC, and the hybrid's inner DFA HYB_PF): `a_best` = the largest N <= exact with one entry row after every string of S_0..S_N-1:

| cfg | kind | origin | sites | measured | 0 | 1 | 2 | 3-4 | 5-8 | 9-16 | 17-31 | 32 (cap) | not measured |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| native | DFA_SCAN | start | 1746 | 1677 | 342 | 676 | 259 | 251 | 84 | 31 | 9 | 25 | no-forward 2, no-language 7, seeded 60 |
| native | DFA_SCAN | scan-restart | 149 | 94 | 3 | 91 | 0 | 0 | 0 | 0 | 0 | 0 | control-excluded 2, no-language 53 |
| native | HYB_PF | start | 680 | 641 | 123 | 435 | 57 | 16 | 1 | 4 | 0 | 5 | no-language 32, seeded 7 |
| native | HYB_PF | scan-restart | 138 | 119 | 1 | 118 | 0 | 0 | 0 | 0 | 0 | 0 | no-language 19 |
| utf8 | DFA_SCAN | start | 1381 | 1160 | 191 | 452 | 189 | 201 | 77 | 27 | 7 | 16 | no-language 169, seeded 52 |
| utf8 | DFA_SCAN | scan-restart | 140 | 92 | 7 | 85 | 0 | 0 | 0 | 0 | 0 | 0 | control-excluded 2, no-language 46 |
| utf8 | HYB_PF | start | 695 | 195 | 29 | 128 | 24 | 9 | 1 | 4 | 0 | 0 | no-language 495, seeded 5 |
| utf8 | HYB_PF | scan-restart | 84 | 74 | 0 | 74 | 0 | 0 | 0 | 0 | 0 | 0 | no-language 10 |

Contiguous `delta_uniform` vs best entry: 25 sites differ (a uniform position after a non-uniform one); position 0 uniform on 2988 of 3673 measured sites.

Which DFA_SCAN sites already prove what (a) could consume: today the kit proves offset 0 only (`proven0`); sites with a_best >= 2 have consumable bytes past offset 0: **742** (native) / **555** (utf8).

(b) VM literal prefix (VM_ATTEMPT, and the VM behind HYB_PF): strict = stops at a capture write; relaxed = a capture open whose value is the attempt start plus the bytes so far does not stop it:

| cfg | kind | column | sites | 0 | 1 | 2 | 3-4 | 5-8 | 9-16 | 17-31 | 32 (cap) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| native | VM_ATTEMPT | b_lit | 256 | 246 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| native | VM_ATTEMPT | b_cls | 256 | 243 | 13 | 0 | 0 | 0 | 0 | 0 | 0 |
| native | VM_ATTEMPT | b_rlit | 256 | 186 | 57 | 10 | 0 | 1 | 2 | 0 | 0 |
| native | VM_ATTEMPT | b_rcls | 256 | 156 | 81 | 14 | 2 | 1 | 2 | 0 | 0 |
| native | HYB_PF | b_lit | 680 | 613 | 66 | 0 | 1 | 0 | 0 | 0 | 0 |
| native | HYB_PF | b_cls | 680 | 613 | 66 | 0 | 1 | 0 | 0 | 0 | 0 |
| native | HYB_PF | b_rlit | 680 | 544 | 122 | 5 | 9 | 0 | 0 | 0 | 0 |
| native | HYB_PF | b_rcls | 680 | 522 | 130 | 9 | 15 | 0 | 4 | 0 | 0 |
| utf8 | VM_ATTEMPT | b_lit | 236 | 227 | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| utf8 | VM_ATTEMPT | b_cls | 236 | 224 | 12 | 0 | 0 | 0 | 0 | 0 | 0 |
| utf8 | VM_ATTEMPT | b_rlit | 236 | 172 | 53 | 8 | 0 | 1 | 2 | 0 | 0 |
| utf8 | VM_ATTEMPT | b_rcls | 236 | 148 | 72 | 11 | 2 | 1 | 2 | 0 | 0 |
| utf8 | HYB_PF | b_lit | 695 | 646 | 49 | 0 | 0 | 0 | 0 | 0 | 0 |
| utf8 | HYB_PF | b_cls | 695 | 646 | 49 | 0 | 0 | 0 | 0 | 0 | 0 |
| utf8 | HYB_PF | b_rlit | 695 | 581 | 102 | 4 | 8 | 0 | 0 | 0 | 0 |
| utf8 | HYB_PF | b_rcls | 695 | 559 | 111 | 8 | 13 | 0 | 4 | 0 | 0 |

(c) WHOLE-COVER (the exact prefix is the whole fixed-width sub-problem; no seed, view or class-indexed accept left): patterns, by population (a pattern with several sites counts once):

| pop | cfg | with language | whole-cover | of which carry captures | width histogram 1..cap |
|---|---:|---:|---:|---:|---:|
| bench | native | 337 | 87 | 8 | [12, 11, 44, 8, 11, 1, 0] |
| bench | utf8 | 207 | 58 | 8 | [10, 4, 29, 7, 7, 1, 0] |
| corpus | native | 4323 | 1060 | 256 | [584, 184, 196, 64, 25, 7, 0] |
| corpus | utf8 | 2385 | 582 | 147 | [251, 104, 138, 62, 22, 5, 0] |

Whole-cover per SEARCH SITE (origin = the match start; the stream's first full-span candidate is the leftmost match):

| cfg | site | kind | sites |
|---|---:|---:|---:|
| native | OFS | DFA_SCAN | 363 |
| native | PF | DFA_HAT | 6 |
| native | PF | DFA_SCAN | 388 |
| native | PF | HYB_PF | 231 |
| native | PF | VM_ATTEMPT | 39 |
| utf8 | OFS | DFA_SCAN | 308 |
| utf8 | PF | DFA_SCAN | 235 |
| utf8 | PF | HYB_PF | 61 |

Whole-cover patterns with NO kit search site (anchored attempt / match-here only): {('bench', 'native'): 3, ('bench', 'utf8'): 3, ('corpus', 'native'): 52, ('corpus', 'utf8'): 19}

Whole-cover once a trailing END anchor (`$`/`\z`/`\Z`) is taken as pcrec's length compare: {('bench', 'native'): 10, ('bench', 'utf8'): 7, ('corpus', 'native'): 172, ('corpus', 'utf8'): 161}

### 5. Context spans before / after the origin

| pop | cfg | context parse | rows |
|---|---:|---:|---:|
| bench | native | empty-body | 1 |
| bench | native | extended | 5 |
| bench | native | ok | 40 |
| bench | native | toplevel-alt | 2 |
| bench | native | unparsed | 1 |
| bench | utf8 | extended | 5 |
| bench | utf8 | ok | 34 |
| bench | utf8 | toplevel-alt | 2 |
| bench | utf8 | unparsed | 1 |
| corpus | native | empty-body | 18 |
| corpus | native | extended | 14 |
| corpus | native | ok | 471 |
| corpus | native | toplevel-alt | 11 |
| corpus | native | unparsed | 50 |
| corpus | utf8 | empty-body | 13 |
| corpus | utf8 | extended | 14 |
| corpus | utf8 | ok | 431 |
| corpus | utf8 | toplevel-alt | 10 |
| corpus | utf8 | unparsed | 50 |

| cfg | leading | trailing | rows |
|---|---:|---:|---:|
| native | - | [b] | 123 |
| utf8 | - | [b] | 116 |
| native | [lb+] | - | 97 |
| utf8 | [lb+] | - | 83 |
| native | [lb-] | - | 45 |
| native | - | [B] | 45 |
| utf8 | - | [B] | 43 |
| native | [b] | [b] | 40 |
| utf8 | [b] | [b] | 36 |
| native | [b] | - | 35 |
| utf8 | [lb-] | - | 35 |
| utf8 | [b] | - | 33 |
| native | - | [la+] | 32 |
| utf8 | - | [la+] | 31 |
| native | - | [la-] | 27 |
| utf8 | - | [la-] | 26 |
| native | [B] | - | 12 |
| utf8 | [B] | - | 11 |
| native | [B] | [B] | 10 |
| utf8 | [B] | [B] | 10 |

| pop | cfg | context rows | body has a machine | all items expressible | (a) consumable >= 1 | (a) >= 2 | (c) whole-cover with context | real seeded entry constant | of checked | PCRE2 rewrite cells | differing |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bench | native | 40 | 27 | 14 | 12 | 8 | 10 | 14 | 14 | 588 | 0 |
| bench | utf8 | 34 | 21 | 9 | 8 | 7 | 6 | 11 | 11 | 462 | 0 |
| corpus | native | 471 | 353 | 151 | 122 | 36 | 107 | 50 | 50 | 2814 | 0 |
| corpus | utf8 | 431 | 313 | 128 | 101 | 35 | 88 | 47 | 47 | 2646 | 0 |

### 6. Savings bound (no timing; armread Zen 4 constants)

| cfg | DFA sites measured | sum a_best (B/candidate) | median | p90 | mean ns/candidate @0.19 | p90 ns/candidate @0.19 | p90 ns/candidate @0.19+1.4 | bytes past offset 0 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| native | 2318 | 4692 | 1 | 4 | 0.38 | 0.75 | 6.35 | 2839 |
| utf8 | 1355 | 3193 | 1 | 4 | 0.44 | 0.75 | 6.35 | 2058 |

Whole-cover BENCH cells (native configuration; every regime the set declares):

| bench pattern | width | engine | captures | regimes |
|---|---:|---:|---:|---:|
| altwide/floor | 1 | dfa | 0 | match,search_short,throughput |
| bounded/dig-exact-16 | 16 | dfa | 0 | match,search_short,throughput |
| bounded/dig-exact-2 | 2 | dfa | 0 | match,search_short,throughput |
| bounded/dig-exact-8 | 8 | dfa | 0 | match,search_short,throughput |
| bounded/floor | 1 | dfa | 0 | match,search_short,throughput |
| bounded/year4 | 4 | dfa | 0 | match,search_short,throughput |
| capability/file-ext-order | 4 | dfa | 0 | search_short,throughput |
| capability/floor-byte | 1 | dfa | 0 | search_short,throughput |
| capability/keyword-prefix-order | 2 | dfa | 0 | search_short,throughput |
| capability/router-prefix-order | 5 | dfa | 0 | search_short,throughput |
| capability/wild-codegrammar-json-array-begin | 1 | dfa | 0 | search_short,throughput |
| capability/wild-codegrammar-json-object-begin | 1 | dfa | 0 | search_short,throughput |
| capability/wild-semdiv-altorder-foo-foobar-rustregex | 3 | dfa | 0 | search_short,throughput |
| email/floor | 1 | dfa | 0 | match,search_short,throughput |
| litrun/floor | 1 | dfa | 0 | match,search_short,throughput |
| litrun/lit-l10 | 10 | dfa | 0 | match,search_short,throughput |
| litrun/lit-l16 | 16 | dfa | 0 | match,search_short,throughput |
| litrun/lit-l2 | 2 | dfa | 0 | match,search_short,throughput |
| litrun/lit-l3 | 3 | dfa | 0 | match,search_short,throughput |
| litrun/lit-l31 | 31 | dfa | 0 | match,search_short,throughput |
| litrun/lit-l4 | 4 | dfa | 0 | match,search_short,throughput |
| litrun/lit-l7 | 7 | dfa | 0 | match,search_short,throughput |
| litrun/lit-l8 | 8 | dfa | 0 | match,search_short,throughput |
| loglines/floor | 1 | dfa | 0 | search_short,throughput |
| sentinel/file-ext-order | 4 | dfa | 0 | search_short |
| sentinel/floor-byte | 1 | dfa | 0 | search_short |
| sentinel/keyword-prefix-order | 2 | dfa | 0 | search_short |
| sentinel/router-prefix-order | 5 | dfa | 0 | search_short |
| syntax/anc-a-uc | 4 | dfa | 0 | match,search_short,throughput |
| syntax/anc-caret | 4 | dfa | 0 | match,search_short,throughput |
| syntax/anc-g-uc | 4 | dfa | 0 | match,search_short,throughput |
| syntax/anc-m-caret | 4 | dfa | 0 | match,search_short,throughput |
| syntax/cls-dot | 3 | dfa | 0 | match,search_short,throughput |
| syntax/cls-fold-pair | 3 | dfa | 0 | match,search_short,throughput |
| syntax/cls-i-class | 3 | dfa | 0 | match,search_short,throughput |
| syntax/cls-mixed-case | 3 | dfa | 0 | match,search_short,throughput |
| syntax/cls-n-uc | 4 | dfa | 0 | match,search_short,throughput |
| syntax/cls-negset | 3 | dfa | 0 | match,search_short,throughput |
| syntax/cls-pair-ctl | 3 | dfa | 0 | match,search_short,throughput |
| syntax/esc-cr | 10 | dfa | 0 | match,search_short,throughput |
| syntax/esc-hex | 3 | dfa | 0 | match,search_short,throughput |
| syntax/esc-hex-braced | 4 | dfa | 0 | match,search_short,throughput |
| syntax/esc-nl | 9 | dfa | 0 | match,search_short,throughput |
| syntax/esc-octal-0 | 9 | dfa | 0 | match,search_short,throughput |
| syntax/esc-quote | 4 | dfa | 0 | match,search_short,throughput |
| syntax/esc-tab | 9 | dfa | 0 | match,search_short,throughput |
| syntax/floor | 1 | dfa | 0 | match,search_short,throughput |
| syntax/grp-atomic-alt | 2 | vm | 0 | match,search_short,throughput |
| syntax/grp-cap | 3 | vm | 1 | match,search_short,throughput |
| syntax/grp-named | 3 | vm | 1 | match,search_short,throughput |
| syntax/grp-named-quote | 3 | vm | 1 | match,search_short,throughput |
| syntax/lit-cat | 3 | dfa | 0 | match,search_short,throughput |
| syntax/lka-nonatomic | 4 | vm | 0 | match,search_short,throughput |
| syntax/lkb-neg | 4 | vm | 0 | match,search_short,throughput |
| syntax/mod-i | 3 | dfa | 0 | match,search_short,throughput |
| syntax/mod-n | 3 | dfa | 0 | match,search_short,throughput |
| syntax/mod-r | 3 | dfa | 0 | match,search_short,throughput |
| syntax/mod-reset | 3 | dfa | 0 | match,search_short,throughput |
| syntax/mod-s | 9 | dfa | 0 | match,search_short,throughput |
| syntax/mod-unset | 3 | dfa | 0 | match,search_short,throughput |
| syntax/mod-x | 3 | dfa | 0 | match,search_short,throughput |
| syntax/qnt-poss-quest | 2 | vm | 0 | match,search_short,throughput |
| syntax/rec-back | 4 | vm | 1 | match,search_short,throughput |
| syntax/rec-define | 5 | dfa | 1 | match,search_short,throughput |
| syntax/rec-fwd | 4 | vm | 1 | match,search_short,throughput |
| syntax/rec-g-angle | 4 | vm | 1 | match,search_short,throughput |
| syntax/rec-py | 4 | vm | 1 | match,search_short,throughput |
| utf8/alt-shared-lead | 2 | dfa | 0 | search_short,throughput |
| utf8/asr-caret-ml | 3 | dfa | 0 | search_short,throughput |
| utf8/ci-ascii-control | 3 | dfa | 0 | search_short,throughput |
| utf8/ci-e-acute | 2 | dfa | 0 | search_short,throughput |
| utf8/ci-turkish-i | 1 | dfa | 0 | search_short,throughput |
| utf8/ci-ucp-invariance | 2 | dfa | 0 | search_short,throughput |
| utf8/cls-d-ascii | 4 | dfa | 0 | search_short,throughput |
| utf8/cls-s-nbsp | 3 | dfa | 0 | search_short,throughput |
| utf8/floor | 1 | dfa | 0 | search_short,throughput |
| utf8/lit-1ch-2b | 2 | dfa | 0 | search_short,throughput |
| utf8/lit-1ch-3b | 3 | dfa | 0 | search_short,throughput |
| utf8/lit-1ch-4b | 4 | dfa | 0 | search_short,throughput |
| utf8/lit-cyr-run | 12 | dfa | 0 | search_short,throughput |
| utf8/lit-nearmiss-run | 9 | dfa | 0 | search_short,throughput |
| utf8/lit-nfc-pair | 5 | dfa | 0 | search_short,throughput |
| utf8/lit-offset-at-head | 3 | dfa | 0 | search_short,throughput |
| utf8/lit-offset-at-tail | 3 | dfa | 0 | search_short,throughput |
| utf8/lit-run-3 | 9 | dfa | 0 | search_short,throughput |
| utf8/lit-sharp-s | 7 | dfa | 0 | search_short,throughput |
| utf8/qnt-lazy-2b | 2 | dfa | 0 | search_short,throughput |

Bench patterns whole-cover ONCE their context joins the span:

| bench pattern | items | body width | regimes |
|---|---:|---:|---:|
| capability/hex8-bounded | b+ b+ | 8 | search_short,throughput |
| capability/utf8-lead-no-cont | la-+ | 1 | search_short,throughput |
| syntax/asr-nwb | B+ B+ | 3 | match,search_short,throughput |
| syntax/asr-wb | b+ b+ | 3 | match,search_short,throughput |
| syntax/lka-pos | la++ | 4 | match,search_short,throughput |
| syntax/lkb-pos | lb++ | 4 | match,search_short,throughput |
| utf8/asr-b-ascii | b+ b+ | 3 | search_short,throughput |
| utf8/asr-b-cyr | b+ b+ | 12 | search_short,throughput |
| utf8/asr-lb-class | lb++ | 1 | search_short,throughput |
| utf8/asr-lb-fixed | lb++ | 1 | search_short,throughput |

### 7. Controls (PCRE2 10.46, independent of the machine reader)

| control | checks | failures | patterns failing |
|---|---:|---:|---:|
| exact-prefix samples are prefixes | 38880 | 144 | 18 |
| inexact counterexample pairs | 608 | 0 | 0 |
| whole-cover samples match at width k / mutants do not | 17721 | 0 | 0 |
| leading \b == its positional rewrite | 6510 | 0 | 0 |
| proven0 narrower than the forward escape set (kit vs emitted table) | 4719 | 0 |  |
| VM prefix longer than the exact prefix | 1867 | 12 |  |

- tests/assertions/absolute.rxt:762 native: c1f=8 c2f=0 c3f=0 ctxf=None `\Zx` 78
- tests/assertions/absolute.rxt:762 utf8: c1f=8 c2f=0 c3f=0 ctxf=None `\Zx` 78
- tests/assertions/absolute.rxt:788 native: c1f=8 c2f=0 c3f=0 ctxf=None `\zx` 78
- tests/assertions/absolute.rxt:788 utf8: c1f=8 c2f=0 c3f=0 ctxf=None `\zx` 78
- tests/assertions/absolute.rxt:918 native: c1f=8 c2f=0 c3f=0 ctxf=None `\Aa*(?:\Zb\|\zc)` 62
- tests/assertions/absolute.rxt:918 utf8: c1f=8 c2f=0 c3f=0 ctxf=None `\Aa*(?:\Zb\|\zc)` 62
- tests/assertions/absolute.rxt:947 native: c1f=8 c2f=0 c3f=0 ctxf=None `\A(?:x*\Zy\|x*\zz)` 79
- tests/assertions/absolute.rxt:947 utf8: c1f=8 c2f=0 c3f=0 ctxf=None `\A(?:x*\Zy\|x*\zz)` 79
- tests/assertions/d27/anchors_abs.rxt:63 native: c1f=8 c2f=0 c3f=0 ctxf=None `\zabc` 616263
- tests/assertions/d27/anchors_abs.rxt:63 utf8: c1f=8 c2f=0 c3f=0 ctxf=None `\zabc` 616263
- tests/assertions/view_edge.rxt:2121 native: c1f=8 c2f=0 c3f=0 ctxf=None `(?:\z\|-)[a-z]{2,4}` 6a77
- tests/assertions/view_edge.rxt:2121 utf8: c1f=8 c2f=0 c3f=0 ctxf=None `(?:\z\|-)[a-z]{2,4}` 6761
- tests/assertions/view_edge.rxt:2607 native: c1f=8 c2f=0 c3f=0 ctxf=None `(?:[a-z]{0,3}\z\|x)[0-9]{3}` 333033
- tests/assertions/view_edge.rxt:2607 utf8: c1f=8 c2f=0 c3f=0 ctxf=None `(?:[a-z]{0,3}\z\|x)[0-9]{3}` 303239
- tests/possessify/composition_d27.rxt:2078 native: c1f=8 c2f=0 c3f=0 ctxf=None `[ab]*\z\W` 02
- tests/possessify/composition_d27.rxt:2078 utf8: c1f=8 c2f=0 c3f=0 ctxf=None `[ab]*\z\W` ec
- tests/possessify/composition_d27.rxt:2213 native: c1f=8 c2f=0 c3f=0 ctxf=None `\w{0,2}?$\W` f5
- tests/possessify/composition_d27.rxt:2213 utf8: c1f=8 c2f=0 c3f=0 ctxf=None `\w{0,2}?$\W` cc

