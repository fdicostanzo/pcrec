# kvcensus — the [KIT-VERIFY] proof census (D161 addendum 16)

Lane `kvcensus`, 2026-10-18. MEASUREMENT ONLY: compile-side and libpcre2-side, single
process, `nice -n 19`; no subject was timed, gcc never ran on an artifact, nothing under
`src/` changed. pcrec at main `2523cfe4b` (built once in the worktree); pcrec-bench read
only at `34174712` (clean); libpcre2-8 10.46 (the dev box's reference oracle). The run is
`docs/dev/kvcensus/` at lane tip (`census.log`: 5,183/5,183 rows, 553 s); every table
below is `summarize.py`'s output on it (`docs/dev/kvcensus/tables.md` holds the full set).

The census D161 add. 16 gates [KIT-VERIFY]'s build on (review r2 kitverify-proof §8, P3):
per kit search site, the origin, what is sent and proven today, the EXACT prefix,
`consumable_len` per consumer kind, whole-cover, and context spans before/after the
origin, with a savings bound.

## 0. Answers first

| question | answer (native configuration unless named) |
|---|---|
| population | 5,183 rows (367 bench + 4,816 corpus), each native and again under `-e utf8` where byte: 9,772 compiles, **9,004 compiled, 768 refused**, 0 errors; **7,620 search sites** (3,981 native) |
| what the kit proves today | offset 0 only (`proven0`) on every FIND site, offset −1 (`proven_prev`) on the 65 MLINE sites, nothing past offset 0 anywhere (by construction: no other proof field exists). `proven0` equals the forward machine's escape set on **all 4,707** view-free sites checked |
| origin | 2,770 native sites start at the match start; **288 (9% of PF/OFS) are SCAN-RESTART** sites (span 0 is where the forward scan leaves its start row: a context byte before the match, or a later byte the reverse pass walks back from); 656 presence, 234 landmark (K82 handoff), 33 after-newline |
| exact prefix (2,617 start-origin sites with a language) | exact 1 on **55%**, 2 on 23%, 3-4 on 14%, ≥5 on 8%; MIXED (exact, then superset inside the span) on 12% (310); **65 patterns (12 bench) are exact in byte and mixed only under utf8** (`.{8,64}` 8 → 1, slack-webhook 32 → 5) |
| (a) DFA consumable_len | median **1** (= what `proven0` already proves), p90 4; **742 of 2,318** measured DFA sites (32%) have consumable bytes past offset 0 (bench 105/208); on scan-restart sites it stays **1** (the engaged sets fork on restart bytes) |
| (b) VM literal prefix | strict (no capture write skipped): ≥1 on 4% of VM_ATTEMPT and 10% of the hybrids' VMs, ≥2 on one site; relaxed (a capture open at the attempt start allowed): ≥1 on 27% / 20%, ≥2 on 5-7% / 2-4% |
| (c) whole-cover | **87 bench patterns, 1,060 corpus**; per search site **1,027** native (77 bench). Bench whole-cover cells are literal and fixed-class cells (litrun, syntax, utf8 literals, bounded/dig-exact, year4, the floors) and literal alternations (file-ext-order, keyword/router-prefix-order, foo\|foobar) — §6 lists them by cell |
| context | 40 bench / 471 corpus context-shaped rows; 14 / 151 have every item expressible as per-position sets; they add **10 bench / 107 corpus whole-cover** patterns and make the seeded entry a compile-time constant on **14/14 and 50/50** real machines checked |
| does pcrec already rewrite `\b` by position? | **No.** `\b` lowers to `A_CTX(W, prev XOR next)` everywhere (`src/parse/mod_assertions.c:131-134`); the VM tests both sides (`src/gen/emit_vm.c:8355`, `assert \b word boundary` in `--emit-ir`); the DFA gets the positional effect only implicitly, from its seed table. The rewrite is an equivalence: PCRE2 agrees on **6,510/6,510** cells |
| savings bound | DFA prefix entry: mean **0.38 ns/candidate** at the skip walk's 0.19 ns/B (p90 0.75 ns; p90 6.35 ns if every skipped byte is an in-match step at ~1.6 ns/B) — against K88's ~4.6 ns re-entry. Whole-cover saves per MATCH the engine walk plus the start recovery |

**What this says for the build** (§8): build whole-cover (U1, report without an engine) first;
it is the only class with a per-match payoff and a real bench population. The DFA prefix
entry (U2) pays well under a nanosecond per candidate at the median and should wait.
The VM literal entry (U3) has almost no population. `consumable_len` as one number is
supported: a uniform position after a non-uniform one occurs on 25 of 3,673 measured sites.
It has to be STATED per site by pcrec, not derived from the language: the scan-restart
9% shows why. R-25 is live on 524 OFS sites today.

## 1. Population, and who counts each (K35)

| population | counted by | native | utf8 |
|---|---|---:|---:|
| rows | the [ARTREV] enumerator, IMPORTED (`docs/dev/optloop/artrev/gen/census.py` `bench_pop`/`corpus_pop`: every bench `patterns/*.rx`, every distinct (pattern, encoding, icase) `.rxt` block, `--features all`) | 5,183 | 4,589 (the byte rows; bench `utf8` and utf8 corpus blocks are native utf8) |
| compiled / refused | pcrec's exit status on the probe compile | 4,784 / 399 | 4,220 / 369 |
| search sites | `kvprobe.c` at pcrec's own two doors (`pcrec_memfn_define`/`_emit`), the last size-ladder attempt only | 3,981 | 3,639 |
| non-search kit sites (not censused) | the same probe | EDGE 3,702, VMSPAN 2,522, N7 836, VMRUN 529, STAY 283, VMSTRIDE 151 (instances, both configs) | |
| language read off pcrec's machine | `kvdfa.py`: the artifact's own anchored machine (N), else `--engine=dfa --no-captures` (D), else the anchor-stripped body of an attempt-engine pattern, else nullable | 3,095 | 2,601 |
| language read from PCRE2 alone | `kvpcre.lang` (byte only; 123 of these capped: a lower bound) | 1,574 | 0 |
| no language | — | 115 | 1,619 |

Refusals are the corpus's refuse-expected rows (quantifier errors, variable-length
lookbehind, `\K` placement, …) and 25 bench rows: 8 `too large`, 12 unbuilt-module rows
(`misc`, `conditionals`, `callouts`, …), 2 UCP, one invalid UTF-8, one variable-length
lookbehind, one `(*SKIP)`. The full reason table is in `tables.md` §1. The utf8 column
has no PCRE2-only reading: a byte-level enumeration under UTF must complete every truncated
character (up to 64³ match calls per string), measured too slow for the lane's window.
Its 1,557 corpus rows without a machine are counted, not read, and every utf8 number below
covers machine-read patterns only. `-fno-scan-edge` (needed to read whole tables) moved the
engine on 0 rows.

## 2. Method, per column

**Sites.** `kvprobe.c` is linked into a copy of the CLI with `--wrap` (nothing under `src/`
changes). For every site it records op, form, handoff, consumer kind, span-0 terms (offset,
need, byte set or run) and `preds`/presence spans. It also asks the kit's pure define-time
query `mf_ask` for the same site and hooks, which gives `proven0` and `proven_prev`. The
search sites are OFS (offset-skip FUNC), PF (FIND), MLINE (FIND, context −1) and PRE
(ALL_PRESENT presence and the landmark handoff).

**Origin.** PRE is `presence`, or `landmark` when it ASSIGNs with `head_max` > 0; MLINE is
`after-nl`. A PF/OFS site is `start` unless its span-0 set fails to contain the language's
first-byte set S_0. Then it is `scan-restart`: the forward scan restarts where its start row
stops self-looping, and the reverse pass recovers the start. `/ctx` marks a pattern with
leading context items, where span 0 is the context byte (`(?<=\$)\d+` scans for `$`).
Prefix columns are computed for `start` (and `after-nl`) sites only.

**The language and the exact prefix** (`kvdfa.lang`). The census walks the anchored
(match-here) machine from its entry rows over SUBSETS of rows, so a seeded machine reads the
union over every predecessor class. A position d exists while no reached subset can accept
(no match ends before it). It is exact while every reached subset allows the same next-byte
set: the cross product S_0..S_d then equals the length-(d+1) prefixes, the brief's
definition. When exactness ends, the walk records a counterexample pair (a string in the
product that is a prefix, and one that is not). `span` is capped at 32 (`MF_MAX_SPAN_POS`'s
derivation). The PCRE2 reading (`kvpcre.lang`) enumerates the prefixes explicitly and is
used only where pcrec has no machine.

**(a) consumable_len, plain DFA** (`kvdfa.uniform`). This uses the artifact's own FORWARD
machine and the language's S_j. `delta_uniform[j]` holds when every string of S_0..S_j drives
the start path to ONE row. `a_best` is the largest N ≤ exact with one entry row after N
bytes, no dead row on the way, and no accept before the entry. The review's witnesses read
as stated: `ac\d|bc` false at 0, `abc\d{3,7}` true at all six. Scan-restart sites use the
forward path's engaged sets (`kvdfa.forward_path`). A seeded machine (DFA hat, `\b`, `(?m)^`)
declines, as window_contract §4.3 requires, and item 4 re-asks it under a context.

**(b) VM literal prefix** (`kvvm.py`, the `--emit-ir` program from L0). It counts
straight-line `consume`/`compare` tests and stops at any choice, `assert`, meter `note`,
`accept` and, in the strict reading, any capture `set`. The relaxed reading lets
`set slot <- scan_position` pass (a capture open whose value is the attempt start plus the
bytes so far).

**(c) whole-cover** (`kvdfa.whole`). The exact prefix equals the span, every subset at the
span accepts unconditionally with no live successor, and there is no seed, view or
class-indexed accept left to decide. Per site this needs origin `start`: the stream is
ascending and complete, so its first full-span candidate is the leftmost match. A
`whole_end` reading also strips a trailing `$`/`\z`/`\Z`, which becomes pcrec's length
compare.

**Context** (`kvctx.py`, item 4). A pattern with no top-level `|` that opens with
`\b`/`\B`/`(?<=X)`/`(?<!X)` or ends with `\b`/`\B`/`(?=X)`/`(?!X)` is a context row. Its
items are stripped and the BODY is compiled. An item is expressible as follows:
- a positive fixed-byte-width product X, where an absent byte fails it;
- a negative width-1 X (its complement set), where an absent byte satisfies it;
- `\b`/`\B` next to a body position whose set lies inside or outside `\w`: `\b` before `\w`
  is `(?<!\w)`, before a non-word byte `(?<=\w)`.

The real seeded machine's entry rows are then re-read under the context set (plus the absent
byte where it satisfies), and the PCRE2 check compares the pattern with its positional
rewrite.

## 3. Origins, what is sent, what is proven today (native)

| site | consumer kind | origin | sites |
|---|---|---|---:|
| PF | DFA_SCAN | start / scan-restart (/ctx) | 1,101 / 125 (19) |
| OFS | DFA_SCAN | start / scan-restart | 645 / 5 |
| PF | HYB_PF | start / scan-restart (/ctx) | 680 / 134 (4) |
| PF | DFA_HAT | start / scan-restart | 88 / 1 |
| PF | VM_ATTEMPT | start | 256 |
| MLINE | DFA_ATTEMPT | after-nl | 33 |
| PRE | DFA_SCAN / HYB_PF / VM_ATTEMPT / DFA_ATTEMPT | presence | 253 / 134 / 257 / 12 |
| PRE | DFA_SCAN / HYB_PF / DFA_ATTEMPT | landmark | 117 / 101 / 16 |

- **Offsets and need.** Every PF site sends ONE REQUIRED term at offset 0 (4,374 of 4,374,
  both configurations). OFS sends the offset-k set, most often `0O,1O` (1,019 sites). Its
  terms are OPTIONAL in 2,314 of 2,472. MLINE sends `-1R`.
- **`proven0` vs S_0 at a start origin**: equal on 1,924 PF and 625 OFS sites, wider on 39.
  It is never narrower: a site whose set was narrower is a scan-restart site by definition,
  and its own control is the next point.
- **`proven0` vs the forward escape set**, read independently off the emitted table: equal
  on all 4,707 view-free sites. The 12 non-equal sites all sit on machines with a `$`/`\z`
  view, the `-bounded` family whose end positions pcrec decides itself.
- **R-25's exposure, counted.** `kit_class` intersects every offset-0 term into `proven0`
  regardless of `need`. **524 of 650 native OFS sites (56 bench) send OPTIONAL offset-0
  terms today.** That is correct only because the generic arm tests every term. It is the
  population that would over-claim the day a kit row declines an OPTIONAL term.

## 4. The exact prefix (start-origin sites)

| cfg | length | sites | 1 | 2 | 3-4 | 5-8 | 9-16 | 17-31 | 32 (cap) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| native | exact | 2,617 | 1,445 | 591 | 370 | 108 | 49 | 9 | 45 |
| native | span | 2,617 | 1,278 | 579 | 467 | 152 | 71 | 21 | 49 |
| utf8 | exact | 1,481 | 727 | 329 | 268 | 97 | 33 | 7 | 20 |
| utf8 | span | 1,481 | 634 | 295 | 334 | 119 | 55 | 20 | 24 |

**Mixed** (exact for a prefix, superset after it inside the span): 310 native / 201 utf8
sites. **utf8-born mixing** (exact over the whole span in byte, mixed under `-e utf8`): 65
patterns, 12 of them bench. Examples: `bounded/pw-8-64` 8 → 1, `line-80` 32 → 1, `csv5`
4 → 1, `tail-dotstar-txt` 4 → 1, `wild-secrets-slack-webhook-url` 32 → 5,
`wild-waf-crs-942270-union-select` 15 → 6, `syntax/cls-dot` 3 → 2. In every one, a `.` or a
negated class becomes multi-byte, so `exact_len` is a per-encoding fact (kvp-contract S1).

## 5. consumable_len per consumer kind

**(a) plain unseeded DFA** (`a_best`; DFA_SCAN includes the offset-skip FUNC):

| cfg | kind | origin | sites | measured | 0 | 1 | 2 | 3-4 | 5-8 | 9-16 | 17-31 | 32 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| native | DFA_SCAN | start | 1,746 | 1,677 | 342 | 676 | 259 | 251 | 84 | 31 | 9 | 25 |
| native | DFA_SCAN | scan-restart | 149 | 94 | 3 | 91 | 0 | 0 | 0 | 0 | 0 | 0 |
| native | HYB_PF | start | 680 | 641 | 123 | 435 | 57 | 16 | 1 | 4 | 0 | 5 |
| native | HYB_PF | scan-restart | 138 | 119 | 1 | 118 | 0 | 0 | 0 | 0 | 0 | 0 |
| utf8 | DFA_SCAN | start | 1,381 | 1,160 | 191 | 452 | 189 | 201 | 77 | 27 | 7 | 16 |
| utf8 | HYB_PF | start | 695 | 195 | 29 | 128 | 24 | 9 | 1 | 4 | 0 | 0 |

Not measured: 60 seeded DFA_SCAN start sites and 89 DFA_HAT sites (the seeded entry, item 4),
and the no-language sites (utf8 HYB_PF 495: no PCRE2 reading under utf8). `a_best` = 0 on
342 + 123 sites: position 0 itself forks the forward machine (the `ac\d|bc` shape). A uniform
position after a non-uniform one occurs on 25 of 3,673 measured sites. **A consumer reads a
prefix, so one `consumable_len` loses almost nothing.** Bytes past offset 0 that a DFA
consumer could skip if the kit proved them: 742 native sites (bench 105 of 208), 2,839 bytes
in total.

**(b) VM literal prefix:**

| cfg | kind | reading | sites | 0 | 1 | 2 | 3-4 | 5-8 | 9-16 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| native | VM_ATTEMPT | strict literal / +class | 256 | 246 / 243 | 10 / 13 | 0 | 0 | 0 | 0 |
| native | VM_ATTEMPT | relaxed literal / +class | 256 | 186 / 156 | 57 / 81 | 10 / 14 | 0 / 2 | 1 | 2 |
| native | HYB_PF (its VM) | strict literal / +class | 680 | 613 | 66 | 0 | 1 | 0 | 0 |
| native | HYB_PF (its VM) | relaxed literal / +class | 680 | 544 / 522 | 122 / 130 | 5 / 9 | 9 / 15 | 0 | 0 / 4 |

VM programs open with a capture write, a dispatch or an assertion. Strict entry past
literals has almost no population. Relaxed, the median is still 0 and ≥2 occurs on 2-7%.

**(c) whole-cover:**

| pop | cfg | with language | whole-cover | carry captures | widths 1 / 2 / 3-4 / 5-8 / 9-16 / 17-31 |
|---|---|---:|---:|---:|---|
| bench | native | 337 | **87** | 8 | 12 / 11 / 44 / 8 / 11 / 1 |
| bench | utf8 | 207 | 58 | 8 | 10 / 4 / 29 / 7 / 7 / 1 |
| corpus | native | 4,323 | **1,060** | 256 | 584 / 184 / 196 / 64 / 25 / 7 |
| corpus | utf8 | 2,385 | 582 | 147 | 251 / 104 / 138 / 62 / 22 / 5 |

- **Per search site** (origin start): 1,027 native (77 bench). By kind: DFA_SCAN 388 PF +
  363 OFS, HYB_PF 231, VM_ATTEMPT 39, DFA_HAT 6.
- **Without any kit search site** (anchored attempt / match-here only): 3 bench, 52 corpus.
- **Whole-cover once a trailing `$`/`\z`/`\Z` is pcrec's length compare**: 10 bench, 172
  corpus more (validators such as `^\d{5}$`-shaped cells; `us-zip` is not one, it is
  variable width).

## 6. Context spans, and the savings bound

| pop | cfg | context rows | body machine | all items expressible | (a) ≥1 | (a) ≥2 | whole-cover with context | real seeded entry constant |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| bench | native | 40 | 27 | 14 | 12 | 8 | **10** | 14 of 14 |
| corpus | native | 471 | 353 | 151 | 122 | 36 | **107** | 50 of 50 |
| bench | utf8 | 34 | 21 | 9 | 8 | 7 | 6 | 11 of 11 |
| corpus | utf8 | 431 | 313 | 128 | 101 | 35 | 88 | 47 of 47 |

- **Shapes** (native): trailing `\b` 123, leading positive lookbehind 97, leading negative
  lookbehind 45, trailing `\B` 45, `\b…\b` 40, leading `\b` 35, trailing positive / negative
  lookahead 32 / 27, …
- **Declined**: 50 unparsed (`\Q`), 14 extended mode, 11 top-level `|`, 18 empty bodies.
- **Bench patterns that become whole-cover once their context joins the span**:
  capability/hex8-bounded (`\b…\b`, width 8), capability/utf8-lead-no-cont (`(?!…)`, 1),
  syntax/asr-wb and asr-nwb (3), syntax/lka-pos and lkb-pos (4), utf8/asr-b-ascii (3),
  utf8/asr-b-cyr (12), utf8/asr-lb-class and asr-lb-fixed (1).

**Today's implicit context spans.** On the 23 `scan-restart/ctx` sites (native) pcrec's FIND
already sends the CONTEXT byte as span 0 (`(?<=\$)\d+` scans for `$`): the forward scan
consumes the predecessor. Addendum 16's "context as a span before the origin" exists today
for width-1 lookbehinds, spelled as a shifted origin.

**Savings bound** (no timing). The constants are from `docs/dev/lanes/armread_report.md`:
§1/§4 the DFA skip walk c_byte 0.1884-0.1885 ns/B on Zen 4 7700X; §2 an in-match DFA state
step ~1.4 ns/B above c_byte, DERIVED.

| cfg | DFA sites | Σ a_best (B/candidate) | median | p90 | mean ns/cand @0.19 | p90 @0.19 | p90 @0.19+1.4 | bytes past offset 0 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| native | 2,318 | 4,692 | 1 | 4 | 0.38 | 0.75 | 6.35 | 2,839 |
| utf8 | 1,355 | 3,193 | 1 | 4 | 0.44 | 0.75 | 6.35 | 2,058 |

The median site's whole bound is offset 0, which `proven0` already covers. Past offset 0 the
bound is about 1.2 B per site. That is under 0.25 ns per candidate at the skip rate and about
2 ns at the in-match rate, before subtracting the kit's own per-position test. It is smaller
than K88's ~4.6 ns per re-entry, as kvp-unlock M4 predicted. Whole-cover saves per MATCH,
not per candidate: the engine's k steps and its start recovery (the reverse pass, or
end-minus-width). armread puts that at C_match 3.2-7.5 ns (DFA, m = 8192) plus k × ~1.6 ns.

Whole-cover bench cells (native; every regime the set declares is match, search_short,
throughput unless noted):

| set | patterns (width) |
|---|---|
| litrun | lit-l2 (2), l3, l4, l7, l8, l10, l16, l31, floor (1) |
| bounded | dig-exact-2/8/16, year4 (4), floor |
| capability (search_short, throughput) | file-ext-order (4), keyword-prefix-order (2), router-prefix-order (5), wild-semdiv-altorder-foo-foobar-rustregex (3), wild-codegrammar-json-array-begin / -object-begin (1), floor-byte |
| sentinel (search_short) | file-ext-order, keyword-prefix-order, router-prefix-order, floor-byte |
| syntax | lit-cat, anc-a-uc, anc-caret, anc-g-uc, anc-m-caret (4), cls-dot, cls-fold-pair, cls-i-class, cls-mixed-case, cls-n-uc, cls-negset, cls-pair-ctl, esc-cr/hex/hex-braced/nl/octal-0/quote/tab, mod-i/n/r/reset/s/unset/x, grp-cap/named/named-quote (VM, 1 capture), grp-atomic-alt, qnt-poss-quest, lka-nonatomic, lkb-neg (VM), rec-back/fwd/g-angle/py (VM, 1 capture), rec-define, floor |
| utf8 (search_short, throughput) | lit-1ch-2b/3b/4b, lit-cyr-run (12), lit-nearmiss-run (9), lit-nfc-pair, lit-offset-at-head/tail, lit-run-3 (9), lit-sharp-s (7), alt-shared-lead, asr-caret-ml, ci-ascii-control, ci-e-acute, ci-turkish-i, ci-ucp-invariance, cls-d-ascii, cls-s-nbsp, qnt-lazy-2b, floor |
| altwide, email, loglines | floor (1) |

## 7. Controls (each against a source the instrument does not share)

| control | instrument checked | checks | failures |
|---|---|---:|---:|
| C1 exact-prefix samples are PCRE2 prefixes (every context class) | kvdfa.lang | 38,880 | 144 in **18 patterns** (excluded, below) |
| C2 inexact counterexample pairs: one a prefix, one not | kvdfa.lang | 608 | 0 |
| C3 whole-cover samples match at width k under a random tail; one-position mutants do not | kvdfa.whole | 17,721 | 0 |
| C4 leading `\b`/`\B` equals its positional rewrite (7 contexts × 6 bodies per row) | kvctx.expressible | 6,510 | 0 |
| C5 `proven0` vs the forward escape set off the emitted table | kvprobe/mf_ask vs kvdfa | 4,719 | 0 view-free (12 view-bounded, explained in §3) |
| C6 machine reading vs PCRE2-only reading (sampled 15% of byte rows, uncapped) | kvdfa vs kvpcre | 262 | span 5, exact 5, whole 6 disagree |
| C7 VM prefix longer than the exact prefix | kvvm vs the language | 1,867 | 12, all never-matching (`z(?!)`, `z(?<=abc)`) |

- **C1's 18 failing patterns.** Each is a degenerate corpus test with an end assertion
  mid-pattern (`\zx`, `\Zx`, `(?:\z|-)[a-z]{2,4}`, `[ab]*\z\W`). These languages are empty or
  end-gated. The reader treats a view-reached row as live when only the subject end can
  follow it. They are EXCLUDED from every language-derived table and listed in `tables.md` §7.
- **C6's disagreements** are all context-dependent shapes (`ab(?!c)`-style trailing context,
  `\bat [a-z]`, `(?<![a-c])\d`, `(?:a|A)*\b`). In them the two readings range over different
  predecessor sets: PCRE2 uses one representative per width-1 class, the machine every class.
- **Failing-direction controls** (`selftest.py`, 57 PASS lines, transcript `selftest.txt`).
  Each instrument meets a known witness and a PLANT that must change its answer:
  - an edited machine whose product breaks at 1;
  - a non-uniform digit at offset 3, which reads contig 3;
  - a diverging engaged byte, which gives forward_path 1;
  - a live edge after the end, which breaks whole-cover;
  - a superset position claimed exact, which PCRE2 rejects;
  - a straddling `\b`, which is not expressible;
  - the wrong rewrite of `\b-x`, which differs;
  - a trailing `(?!c)`, which is not whole-cover;
  - a non-nullable start row.
- **Not controlled**: `a_best` itself is machine-internal (no PCRE2 analogue). Its controls
  are the witnesses and plants above plus C5's agreement on the entry row.

## 8. What this says for the build

1. **Whole-cover first (U1).** It has a payoff per MATCH (the engine walk plus start
   recovery, armread 3.2-7.5 ns plus k steps) and a measured bench population: 87 bench
   patterns, 77 bench search sites, plus 10 with context and 10 with an end anchor. The
   population is concentrated in literal and fixed-class cells and literal alternations.
   "Wild" bench patterns rarely qualify (file-ext/keyword/router-prefix-order and the
   foo|foobar semdiv cell are the exceptions). Its consumption condition is origin
   `start`, so the 9% scan-restart sites must be told apart, which pcrec knows.
2. **Do not build the DFA prefix entry (U2) yet.** The median consumable prefix is offset 0,
   which is already proven. Past it, ~1.2 B per site is worth well under 1 ns per candidate
   at the skip rate, below the ~4.6 ns re-entry it competes with. Its trigger stays a timed
   class-led cell (kvp-contract U2).
3. **The VM literal entry (U3) has no population** worth a design: strict ≥1 on 4-10%,
   ≥2 on one site of 936.
4. **`consumable_len` is one number, stated by pcrec per site.** Prefix consumers lose
   nothing measurable (25 / 3,673 sites have a later uniform position). On scan-restart
   sites the language would claim more than the consumer can take, so the number must come
   from the consumer, as ruled.
5. **Context spans:** the `\b` positional rewrite is an equivalence (C4: 0 / 6,510). It
   makes every checked seeded entry a constant (64 of 64 real machines), and it adds a modest
   whole-cover population (10 bench, 107 corpus). Fold it into U1 for `\bword\b`-shaped
   sub-problems, not as a separate build. Width-1 lookbehind context is already sent today
   as a shifted origin (23 sites).
6. **R-25 before any kit row may decline an OPTIONAL term:** 524 native OFS sites carry
   OPTIONAL offset-0 terms.
7. **`exact_len` is per encoding:** 65 patterns change only under utf8. A `.` or a negated
   class is the whole mechanism.

## 9. Measurement regime, limitations, reproduction

- **Regime.** Compile-side only. The savings bound is a derivation from armread constants,
  not a measurement on these sites. An official verdict on any build is the bench's on the
  targeted hardware (D144 add. 4).
- **Limitations, counted where they bite.**
  - utf8 rows have no PCRE2-only reading (1,619 utf8 rows without a language).
  - 123 PCRE2-only readings are capped (`maxprod`/`budget`), so their exact length is a
    lower bound; 27 hit PCRE2's match limit and are counted as no language.
  - Lookbehinds wider than one byte are read over width-1 contexts only.
  - PRE presence/landmark sites get no prefix analysis (their origin is not the match start).
  - The context parser reads text and declines `\Q`, extended mode and top-level
    alternation.
  - The tables are read under `-fno-scan-edge`, which moved no engine.
- **Reproduce.**
  - Build the probe once:
    `gcc -O2 -std=gnu11 -Ilib -Isrc -o build/kv/pcrec-kv cli/main.c docs/dev/kvcensus/kvprobe.c build/libpcrec.a -Wl,--wrap=pcrec_memfn_define -Wl,--wrap=pcrec_memfn_emit`.
  - Run the census:
    `PCREC=build/pcrec PROBE=build/kv/pcrec-kv BENCH=/home/pcrec/projects/pcrec-bench OUT=build/kv/run nice -n 19 python3 docs/dev/kvcensus/census.py`
    (~10 min, one process).
  - Fold it: `OUT=build/kv/run python3 docs/dev/kvcensus/summarize.py`.
  - Check the instruments: `python3 docs/dev/kvcensus/selftest.py`.
  - Instruments and data: `docs/dev/kvcensus/` (own CLAUDE.md).
