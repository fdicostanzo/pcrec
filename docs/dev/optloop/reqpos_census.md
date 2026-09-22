# `[OPT-REQPOS]` — the positioned necessary-byte census (the D77 trigger)

**[OPTLOOP.2] cycle-2 preparation, lane `c2prep`, 2026-09-22.** Census only:
nothing under `src/`, `lib/` or `cli/` changed, no mechanism is built, and no
clock was read anywhere. Every number is a COUNT.

The row (`docs/dev/plan.md` `[OPT-REQPOS]`, filed by Frank on
`[OPT-REQBYTE]`'s landing) names its own D77 trigger: *"a compile-side CENSUS
before any build"* of how many patterns carry a required byte at finite
`dmax`, how many carry two necessary bytes at a fixed separation and how rare
the pair is against the single byte, and which bench cells have the byte
PRESENT rather than absent. This is that census.

Instruments and data: `c2/reqpos_probe.c`, `c2/reqpos_census.py`,
`c2/reqpos_census.tsv`, `c2/reqpos_crosscheck.txt`, `c2/reqpos_tiers.txt`,
`c2/run_selectivity.txt` (directory `CLAUDE.md` describes each).

---

## 0. The headline

* **Tier 2 — the bounded-`dmax` skip loop the row is really about — has a
  population of TWO among cycle 1's 34 losing cells**, and 6.0% of the shipped
  corpus. It is the smallest of the four tiers on every population measured.
* **All five of `[OPT-REQBYTE]`'s own target rows are TIER 3**, confirming the
  row's own written prediction verbatim — and all five have the byte ABSENT
  from the bench subject, which is exactly where batch 1 already answers the
  whole call in one pass and where no positional refinement can add anything.
* **Tier 2b — the pair / word compare — is the large and useful tier**: 27.3%
  of the bench population and 18.6% of the corpus carry a necessary literal
  run of 2 bytes or more. On the `capability` set, **5 patterns have the
  single byte PRESENT in the subject and the RUN ABSENT**, so a word-grain
  pre-check answers their whole call in one pass exactly where the byte-grain
  one cannot.
* **A finding the row did not ask for**: 14 of the 36 `capability` patterns
  with a necessary byte have a RARER necessary byte than the one
  `[OPT-REQBYTE]` picks, and for **three of them the rarer byte is ABSENT
  while the picked byte is PRESENT** (§5). PCRE2's rightmost-byte rule, which
  batch 1 copied deliberately, is leaving three whole-call answers on the
  table on this subject.

**Recommendation, stated once**: tier 2 does not clear D77 on this evidence
and should not be built. Tier 2b should be the row, and the cheapest thing in
front of both is the pick rule (§5), which needs no new emitted mechanism at
all.

---

## 1. Method, and how it is checked

`c2/reqpos_probe.c` is a throwaway analyzer that links `libpcrec.a` and drives
the REAL parser, `pcrec_altcls`, `pcrec_discharge_atomic` and
`pcrec_lower_enc`, so the tree it walks is the tree the emitters walk: after
the lowering every `A_CLASS` is a BYTE class and a singleton is exactly one
`memchr` argument. It carries `src/opt/reqbyte.c`'s own set and pick rules
verbatim beside new position and run tracking.

**Why not `--emit-ir`.** It refuses on every DFA-winning pattern
(`w2x_report.md` §5), so an IR-driven census would have silently measured a
biased half of the corpus and read green.

**The check that makes the numbers citable.** The probe's `req_byte` column
must equal batch 1's landed `RX_REQ_BYTE` stamp on every pattern, read off an
artifact emitted by `worktrees/optimpl1/build/pcrec`:

```
checked  63     agree 63     disagree 0     skipped 1 (batch 1 refuses the pattern)
```

**And it did not agree on the first run, which is the more useful result.** On
`/user|/users` the stamp read `r` and the probe read `s`, because
`pcrec_altcls` FACTORS that alternation to `/user(?:s)?` before anything
downstream sees it (`RX_ALTCLS_FACTORED 1` on the artifact) and the optional
tail then contributes no necessary byte. The probe's pipeline prefix was parse
+ lower; it is now altcls + discharge + lower. The general form is worth more
than the cell: **an analysis's answer is a property of the tree at its own
call site, so a census that reconstructs the pipeline must reconstruct every
REWRITING pass above that site** — and the only reason this was found is that
the census was built with a cross-check against the shipped stamp rather than
against its own reasoning.

**The three facts, and the tiers they decide.**

| fact | meaning |
|---|---|
| `req_byte` | the necessary byte, `reqbyte.c`'s own pick |
| `dmin`/`dmax` | the tightest interval of offsets FROM THE MATCH START at which a guaranteed occurrence sits; `dmax = -1` is unbounded |
| run | the longest necessary literal RUN, with its own offset interval |

| tier | predicate | what it would be |
|---|---|---|
| 1 | `dmin == dmax` | a FIXED offset — `src/opt/prefix_k.c`'s territory, built for the DFA route today |
| 2 | `dmax` finite | a BOUNDED range: a failed attempt at `s` with the next occurrence at `q` may jump to `q − dmax` |
| 2b | run ≥ 2 | the PAIR: `memchr` one member, one unaligned word compare at the known delta |
| 3 | `dmax` unbounded | reverse-inner, `[ENG-ISL]` territory |

Tier 2b is **orthogonal** to 1/2/3: a run is a statement about two bytes'
relative positions and says nothing about either one's offset from the start.

**Known false negatives, stated because a census that does not name them
over-claims its own zeroes.** At an `A_ALT` the run analysis keeps only the
branches' common prefix and suffix, so `(?:xabcy|zabcw)` reports no run where
`abc` is one; runs are not merged across iterations of a repeat; and a class
with more than one member contributes no byte, which is every caselessly
folded literal (D23 folds `(?i)a` to `[aA]` at parse time), so every `(?i)`
pattern's run figure is a floor. All three under-report. `dmin` may
under-estimate and `dmax` over-estimate, both of which only weaken a bound.

---

## 2. Tier counts, by population

`bench` is every `bench/*/patterns/*.rx` export across the six sets; `corpus`
is every `pattern`/`pattern-esc` line of every shipped `.rxt`, decoded out of
`--list-source`'s field escaping.

| | bench (249) | corpus (3,944) | corpus `-e utf8` (3,944) |
|---|---|---|---|
| no necessary byte | 105 — 42.2% | 1,296 — 32.9% | 1,291 — 32.7% |
| **tier 1** fixed offset | 75 — 30.1% | 1,566 — 39.7% | 1,598 — 40.5% |
| **tier 2** bounded `dmax` | **21 — 8.4%** | **238 — 6.0%** | **255 — 6.5%** |
| **tier 3** unbounded | 35 — 14.1% | 432 — 11.0% | 432 — 11.0% |
| refused (module gate) | 13 — 5.2% | 412 — 10.4% | 368 — 9.3% |
| **tier 2b** run ≥ 2 | 68 — 27.3% | 734 — 18.6% | 799 — 20.3% |
| run ≥ 4 | 29 — 11.6% | 90 — 2.3% | 100 — 2.5% |
| run ≥ 8 | 6 — 2.4% | 25 — 0.6% | 26 — 0.7% |

Per bench set:

| set | N | none | t1 | t2 | t3 | run ≥ 2 |
|---|---|---|---|---|---|---|
| `altwide` | 33 | 24 | 6 | 3 | 0 | 5 |
| `bounded` | 43 | 36 | 1 | 6 | 0 | 0 |
| `capability` | 64 | 27 | 17 | 4 | 15 | 14 |
| `email` | 3 | 0 | 1 | 0 | 2 | 0 |
| `loglines` | 11 | 2 | 3 | 4 | 2 | 3 |
| `syntax` | 95 | 16 | 47 | 4 | 16 | 46 |

**Tier 2 is the smallest live tier everywhere.** Its largest single home is
`bounded`, 6 of 43, which is the set built out of counted repeats — the one
population where a finite `dmax` is structurally likely. Read against tier
2b's 734 corpus rows and tier 1's 1,566, a bounded-range skip loop is the
least-reachable of the three mechanisms the row bundles.

---

## 3. Where the tiers land on cycle 1's losing rows

Joining `cycle1_rows.tsv`'s 34 losing (pattern, regime) cells against the
census:

| tier of the pattern's required byte | losing cells |
|---|---|
| 3 — unbounded | 11 |
| 1 — fixed offset | 11 |
| none | 10 |
| **2 — bounded `dmax`** | **2** |

The 25 distinct losing patterns, by best rank:

| pattern | tier | rank | score | run | `dmax` | byte hits in `t-1m` |
|---|---|---|---|---|---|---|
| `bracket-array-define` | none | 1 | 1.9587 | 0 | — | — |
| `tag-depth3-bound` | **3** | 2 | 0.9492 | 2 | ∞ | **0** |
| `dup-param-detect` | **3** | 3 | 0.9171 | 1 | ∞ | **0** |
| `wild-semdiv-dollar-trailing-newline-pcre2` | 1 | 4 | 0.8710 | 3 | 2 | 22,334 |
| `tag-pair-match` | **3** | 5 | 0.7640 | 2 | ∞ | **0** |
| `wild-secrets-username-password-pair` | **3** | 6 | 0.7232 | 1 | ∞ | **0** |
| `wild-secrets-aws-access-key-id` | 1 | 7 | 0.6112 | 1 | 0 | 1,754 |
| `wild-logparse-winpath-grok` | **3** | 8 | 0.3611 | 1 | ∞ | **0** |
| `nested-comment-rec` | 1 | 9 | 0.2972 | 2 | 0 | 30,000 |
| `wild-codegrammar-json-constant` | none | 10 | 0.2788 | 0 | — | — |
| `wild-waf-crs-942360-concat-sqli` | none | 11 | 0.2435 | 0 | — | — |
| `router-prefix-order` | 1 | 12 | 0.2258 | 5 | 4 | 54,781 |
| `file-ext-order` | 1 | 13 | 0.2213 | 4 | 3 | 54,781 |
| `wild-semdiv-altorder-foo-foobar-rustregex` | 1 | 14 | 0.1931 | 3 | 1 | 38,684 |
| `wild-waf-crs-942270-union-select` | none | 15 | 0.1831 | 0 | — | — |
| `wild-secrets-github-pat` | 1 | 16 | 0.1763 | **11** | 6 | 6,061 |
| `wild-waf-crs-942160-sleep-benchmark` | **3** | 17 | 0.1708 | 1 | ∞ | 6,061 |
| `quoted-delim-match` | none | 19 | 0.1348 | 0 | — | — |
| `balanced-parens-rec` | **3** | 21 | 0.1145 | 1 | ∞ | 6,061 |
| `wild-waf-crs-942140-dbnames` | none | 24 | 0.0866 | 0 | — | — |

**The five `[OPT-REQBYTE]` target rows are the five bolded tier-3 entries with
a zero byte count**, which is the row's own prediction (*"the five M1 target
rows put their byte after an unbounded repeat, so they are likely tier 3"*)
confirmed rather than assumed. And their byte count of zero is why nothing
positional can help them: batch 1's whole-window `memchr` already answers the
entire find-all call in one pass on exactly those rows, and a tier-2 skip loop
or a tier-3 reverse walk has no work left to do.

**The complement is where tier 2/2b/3 would have to pay**: of the 36
`capability` patterns with a necessary byte, **11 have it ABSENT from `t-1m`
and 25 have it PRESENT**. The 25 are the population, and they are dominated by
tier 1 (already served on the DFA route) and tier 2b.

---

## 4. Tier 2b: how rare the run is against the byte

`c2/run_selectivity.py` counts each necessary run as a literal in the bench's
`t-1m` subject and divides by the count of its rarest member byte. That ratio
IS the pair filter's selectivity gain. Scoped to `capability`, whose regime
uses this subject — the `syntax` and `altwide` rows in the raw file are
measured against a text that is not theirs and are not read here.

| pattern | run | len | rarest-byte hits | run hits | gain |
|---|---|---|---|---|---|
| `router-prefix-order` | `/user` | 5 | 29,144 | 245 | **119.0×** |
| `keyword-prefix-order` | `in` | 2 | 30,683 | 7,243 | 4.2× |
| `logparse-atomic` | `: ` | 2 | 9,070 | 9,070 | 1.0× |
| `logparse-atomic-removed` | `: ` | 2 | 9,070 | 9,070 | 1.0× |
| `file-ext-order` | `.tar` | 4 | 14,826 | **0** | ∞ |
| `wild-secrets-github-pat` | `github_pat_` | **11** | 4,973 | **0** | ∞ |
| `wild-secrets-slack-webhook-url` | `://` | 3 | 9,070 | **0** | ∞ |
| `wild-semdiv-altorder-foo-foobar-rustregex` | `foo` | 3 | 18,853 | **0** | ∞ |
| `wild-semdiv-dollar-trailing-newline-pcre2` | `abc` | 3 | 4,973 | **0** | ∞ |
| `nested-comment-rec` | `*/` | 2 | 0 | 0 | (byte already absent) |
| `tag-depth3-bound`, `tag-pair-match` | `</` | 2 | 0 | 0 | (byte already absent) |
| `winpath-near-miss` | `:\` | 2 | 0 | 0 | (byte already absent) |
| `wild-waf-crs-942500-comment-obfuscation` | `*/` | 2 | 0 | 0 | (byte already absent) |

**Five `capability` patterns have the byte PRESENT and the run ABSENT.** On
those, a byte-grain whole-window pre-check cannot fire at all and a word-grain
one answers the entire call in one pass — the same 0.0168 ns/byte floor
`cycle1_analysis.md` §2.2 shows three engines share and pcrec already reaches.
Four of the five are cycle-1 losing rows (`file-ext-order`,
`wild-secrets-github-pat`, `wild-semdiv-altorder-foo-foobar-rustregex`,
`wild-semdiv-dollar-trailing-newline-pcre2`) — four losing cells carrying
**1.4617 of weighted score**, against the whole losing matrix's 10.284.

Over the whole bench population: **68 patterns carry a run of 2 or more; on 60
of them the run never occurs in `t-1m` at all**, and the 8 finite gains run
from 1.00× to 118.96× with a median of 4.24×. The 1.00× rows are the honest
counter-example and they have a shape: `logparse-atomic`'s run is `": "`,
where the space always follows the colon in this text, so the second byte
carries no information. **A pair filter's gain is not a property of the run's
length**, and a findings-informed choice of WHICH pair (D83's `freq`, the same
value `firstset_design.md` §5 names) is what separates `/user` from `": "`.

`wild-secrets-github-pat`'s 11-byte run at a fixed offset of 6 is the row's
own worked example arriving unprompted: one 8-byte unaligned compare covers
`ithub_pa`, and the run may overlap the `memchr` byte exactly as Frank's
`https://` example describes.

---

## 5. The finding the row did not ask for: the pick rule

`[OPT-REQBYTE]` emits **the rightmost** necessary byte, matching PCRE2's own
`LASTCODEUNIT` choice, deliberately, so that a later multi-byte form is a
widening and not a different mechanism. The census reports the whole necessary
SET, and joining it against the subject census shows what the rightmost rule
costs on this text:

* **14 of the 36** `capability` patterns with a necessary byte have a RARER
  necessary byte than the one picked;
* **3 of those have the rarer byte ABSENT while the picked byte is PRESENT**:

| pattern | picked (rightmost) | hits | rarest necessary | hits |
|---|---|---|---|---|
| `nested-comment-rec` | `/` | 30,000 | `*` | **0** |
| `wild-validator-email-owasp` | `.` | 14,826 | `@` | **0** |
| `wild-waf-crs-942500-comment-obfuscation` | `/` | 30,000 | `*` | **0** |

On those three, batch 1's shipped pre-check cannot fire and a
frequency-informed pick answers the whole find-all call in one pass.
`nested-comment-rec` is a cycle-1 losing row at rank 9.

**This is the cheapest item in this document.** It emits no new mechanism, no
new stamp and no new emitted line: `reqbyte.c` already carries the whole set
internally (`RbSet.bits`) and chooses one member from it at the end. The
change is which member — and the fact that decides it is exactly the `freq`
value `firstset_design.md` §5 specifies, whose format already ships
(`src/parse/rxt_schema.def:146`).

The rightmost rule is not wrong; it is a **profile-less default**, and the
row's own reason for it (a later multi-byte form is a widening) is untouched
by changing which member a findings-informed build selects.

---

## 6. UTF-8

The `-e utf8` arm moves the tier counts slightly and in the expected
direction: tier 1 rises (1,566 → 1,598) and tier 2 rises (238 → 255), because
a multi-byte character lowers to a fixed-width `A_CAT` of byte classes, which
adds fixed offsets. Tier 3 is unchanged at 432. Runs rise (734 → 799). Nothing
here changes any recommendation; it is recorded because the row's populations
were asked for under both encodings.

---

## 7. What is owed, and to whom

* **No timing.** Every claim above is a count. What a tier-2b word compare
  costs per candidate, and whether the five byte-present/run-absent rows reach
  the §2.2 floor, is a Linux measurement in `[OPT-5]` STEP 0's shape and is
  owed before anything is built. The block belongs in the implementation
  row's own step 0, not here.
* **The `bounded` set's six tier-2 rows are the only place tier 2 has a
  population worth a second look**, and they are counted-repeat shapes whose
  regime this census did not examine. If tier 2 is to be reconsidered, that is
  the subbench to take it into (D119's 2026-09-22 addendum makes the subbench
  follow the question).
* **`syntax` and `altwide` run selectivity** is unmeasured: their runs were
  counted against `capability`'s subject in the raw output and those rows are
  excluded from §4 for that reason. Each set has its own subjects.
