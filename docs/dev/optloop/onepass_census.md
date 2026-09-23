# The ONE-PASS REACH CENSUS — `captures_via_dfa_survey.md` §3.6, measurement M-A

**[OPTLOOP.2] cycle-2 preparation, lane `c2prep`, 2026-09-22.** Census only:
nothing under `src/`, `lib/` or `cli/` changed, no mechanism is built, and no
clock was read anywhere. Every number is a COUNT.

`captures_via_dfa_survey.md` ranks the **one-pass DFA** first among three
candidates for assigning captures from a deterministic machine, and gates it
on a single number: *"if fewer than ~10% of capture-bearing corpus patterns
are one-pass, (c) is a special case for a handful of patterns and fails
`pcrec-general-mechanisms-not-special-cases`; the row closes with the
number."* A one-pass predicate does not exist in the tree, so the census
needed a throwaway analyzer. This is it.

Instruments and data: `c2/onepass_probe.c`, `c2/onepass_census.py`,
`c2/onepass_census.tsv`, `c2/onepass_summary.json`.

---

## 0. The answer

**Capture-bearing one-pass reach is 31.46% on the shipped corpus and 29.41%
on the 17 capture-forced hybrid `capability` rows. The kill threshold is
~10%. Candidate (c) SURVIVES M-A, by a factor of three.**

| population | probed | one-pass (all) | capture-bearing | **capture-bearing one-pass** |
|---|---|---|---|---|
| the 17 capture-forced `hybrid` rows | 17 | 5 — 29.41% | 17 | **5 — 29.41%** |
| corpus, `--features all`, byte | 3,944 | 1,921 — 54.39% | 1,173 | **369 — 31.46%** |
| corpus, `--features all`, `-e utf8` | 3,944 | 1,748 — 48.88% | 1,175 | **369 — 31.40%** |

Two things in that table are worth more than the headline.

* **The UTF-8 narrowing the survey expected does not land on the population
  it matters for.** `[RAonepass]`'s overlapping-encoding caveat is real and
  visible — whole-corpus reach falls 54.39% → 48.88%, 211 patterns lose the
  property — but capture-bearing reach moves by **0.06 points**, 369 rows
  either way. §3 says why.
* **The three precedents' own caps cost essentially nothing.** Applying RE2's
  ≤5-capture-pair and Go's ≤1,000-instruction limits takes 31.46% → 31.20%
  (369 → 366 rows), so the figure is comparable to the published
  implementations without a separate discussion.

---

## 1. The predicate, exactly

A pattern is one-pass when, during an **anchored** match, at most one
alternative can proceed at each input byte. Over pcrec's lowered AST, with
`FIRST(a)` the bytes that can begin a match of `a` and `F` the bytes that can
follow `a`:

| node | rule |
|---|---|
| `A_ALT` | every pair of branches has DISJOINT `FIRST`; at most one branch is nullable; and if a branch is nullable, every other branch's `FIRST` is disjoint from `F` too — without that clause "take the empty branch" and "enter a branch" are decided by the same byte |
| `A_REP` where `rmax != rmin` | the body is not nullable and `FIRST(body)` is disjoint from `F`, so "go round again" versus "leave" is decided by the next byte alone |
| `A_LOOK`, `A_BREF`, `A_CALL` | **not one-pass.** All three production implementations bail on a lookaround, a backreference and a subroutine call, and pcrec has no reason to be braver than RE2 |
| `^ $ \b \B \A \z \G \K` | allowed — deterministic empty-width tests that Go's `onepass` admits explicitly, consuming no byte and so unable to create a two-alternative step |

**Clause (iii) of §3.6** — *"the pattern is anchored or is being compiled for
the anchored entry"* — is satisfied by construction for the population the
survey cares about: §3.3's fit argument is that a one-pass DFA replaces
`rx_match_anchored`, which the hybrid already calls anchored on a window. The
census therefore does not require a leading anchor, and reports the
leading-anchored subset separately (23 of the 369 corpus rows, 1 of the 5
hybrid rows) so the stricter reading is readable off the same data.

**Known false negatives** (the predicate under-reports; every one is safe):

* `FIRST` is computed over BYTES after `pcrec_lower_enc`, so under `-e utf8`
  two classes whose UTF-8 encodings share a LEAD byte read as overlapping.
  That IS `[RAonepass]`'s narrowing, so here it is the measurement rather
  than an artefact.
* Disjointness is required pairwise over an `A_ALT` spine rather than via a
  determinizing construction.
* `A_ATOMIC` is transparent. An atomic cut REMOVES alternatives, so a pattern
  reported one-pass is still one-pass; one whose ambiguity the cut removes is
  missed.

**There are no known false POSITIVES**, which is the direction a reach gate
depends on.

Validated on thirteen hand-written cases with known answers, including the
survey's own three named non-one-pass patterns: `(.*) (.*)` and `x*x` both
read `ambiguous`, `(?=a)(b)` and `(a)\1` read `kind`, and `[0-9]+-[a-z]+`,
`(ab|cd)`, `(a|)b` and `^(\d{4})-(\d{2})` read one-pass.

---

## 2. A finding: pcrec's own factoring pass changes the answer

The survey names `(xy|xz)` — from RE2's own front end — as a pattern that is
NOT one-pass, because its branches share a first byte. **On pcrec's tree it
IS one-pass**, because `pcrec_altcls` factors it to `x(?:y|z)` before any
downstream pass sees it (`RX_ALTCLS_FACTORED 1` on its artifact).

That is not a probe defect; it is a real difference in what the two compilers
hand their analyses, and it is worth a number. The probe grew a `-no-factor`
switch that denies both altcls axes, so both readings come off one
instrument:

| corpus, byte | whole-population reach | capture-bearing reach |
|---|---|---|
| as shipped (altcls on) | 54.39% | **31.46%** |
| `-no-factor` (the precedents' criterion) | 52.21% | **28.30%** |

**`pcrec_altcls` is worth +3.16 points of capture-bearing one-pass reach.**
The consequence for anyone comparing this figure to a published one: pcrec's
reach is measured on pcrec's trees and is not comparable byte for byte with a
number derived from RE2's, Go's or rust's criterion applied to raw pattern
text. Both numbers clear the 10% threshold, so the ranking does not turn on
it.

---

## 3. Why UTF-8 barely moves the capture-bearing figure

The capture-bearing corpus population fails one-pass for two very different
reasons, and only one of them is an encoding question:

| | corpus, byte | share of the 1,173 |
|---|---|---|
| one-pass | 369 | 31.5% |
| **not one-pass: `kind`** (lookaround / backreference / call) | **543** | **46.3%** |
| not one-pass: `ambiguous` | 261 | 22.3% |

**Nearly half the capture-bearing population is excluded by a node KIND before
any first-set question is asked**, and a node kind does not change with the
encoding. The UTF-8 lead-byte overlap can only act on the `ambiguous`
boundary, and on this corpus the patterns it pushes across that boundary are
overwhelmingly capture-FREE: whole-population `ambiguous` rises 708 → 919
(+211) while the capture-bearing one-pass count does not move at all.

This is a real result and it refutes a stated expectation. The survey calls
the UTF-8 narrowing *"a real narrowing for pcrec's byte-wise UTF-8
automata"*, and for the population the mechanism would serve it is not one.

---

## 4. The 17 capture-forced hybrid rows, individually

These are the only rows where a one-pass DFA would replace a VM pass that is
doing capture work (`capsurvey_census.tsv`: `RX_VM_PREFILTER "hybrid"` and
`RX_ENGINE_WHY` naming a capture group).

| pattern | `ncap` | one-pass |
|---|---|---|
| `codegrammar-flat` | 1 | **yes** |
| `codegrammar-xflag` | 1 | **yes** |
| `wild-secrets-github-pat` | 1 | **yes** |
| `wild-secrets-slack-webhook-url` | 1 | **yes** |
| `wild-validator-us-zip-owasp` | 1 | **yes** |
| `date-nested-plus` | 2 | no — ambiguous |
| `email-nested-plus` | 1 | no — ambiguous |
| `logparse-atomic` | 1 | no — ambiguous |
| `logparse-atomic-removed` | 1 | no — ambiguous |
| `numeric-id-nested-plus` | 1 | no — ambiguous |
| `phone-list-nested-plus` | 1 | no — ambiguous |
| `wild-datetime-moment-iso8601` | 4 | no — ambiguous |
| `wild-logparse-syslogbase-expanded` | 82 | no — ambiguous |
| `wild-secrets-aws-access-key-id` | 1 | no — ambiguous |
| `wild-secrets-username-password-pair` | 2 | no — ambiguous |
| `wild-semdiv-empty-alt-repeat-pcre2` | 1 | no — ambiguous |
| `wild-validator-ipv4-owasp` | 4 | no — ambiguous |

**Not one of the seventeen is excluded by KIND** — every failure is a genuine
ambiguity, which is what a hybrid-exact population should look like (a
backreference or a linked call declines the prefilter outright, so those
patterns are not on the hybrid to begin with). Every one of the five that pass
carries exactly one capture group, and all five clear the RE2/Go caps.

Two of the five are also the two rows `reqpos_census.md` finds at TIER 1 with
a long necessary literal run — `wild-secrets-github-pat` (`github_pat_`, 11
bytes at a fixed offset of 6) and `wild-secrets-slack-webhook-url` (`://`, 3
bytes at offset 6) — which is not a coincidence: a pattern built from a rigid
literal skeleton is both easy to pre-filter and easy to make one-pass. The
other three are not: `codegrammar-flat` and `codegrammar-xflag` are tier 3
with a one-byte run, and `wild-validator-us-zip-owasp` has no necessary byte
at all. **So the two properties overlap and neither implies the other**, which
is worth stating because a reader could otherwise take the five one-pass rows
for the five easy rows.

---

## 5. What this census does NOT settle

* **M-B, and it is the measurement that actually decides the row.** §3.6's
  second measurement asks what share of a hybrid-exact artifact's time the VM
  pass is (arm 1 `--features all` minus arm 2 `--no-captures`, over the
  bench's own subjects), with the decision rule stated there: under ~10% on
  throughput and ~25% on match, the second pass is not the cost and (c) buys
  little even at full reach. **M-A survives; M-B is untouched and is Linux
  work.** Nothing in this document licenses building anything.
* **Any throughput claim.** No clock was read.
* **Whether the 31.46% is the right denominator.** The survey asks for reach
  among capture-bearing patterns, and that is what is reported. Whether a
  corpus written to exercise a compiler is representative of the patterns a
  one-pass rung would meet in production is a question no census of this
  corpus can answer, and the 17-row hybrid figure (29.41%) is the closest
  thing here to an independent check — it agrees.
* **Where the rung would sit in the selection ladder**, what it would cost in
  emitted bytes, and what its `limits.def` rows would be. §3.3 sketches all
  three; none is measured here.

---

## M-B — measured (2026-09-23, [B76] O-46, lane mbread)

§3.6's second measurement, reduced from pcrec-bench lane `b76optloop`'s
raw arm1/arm2 `ns/byte` lines (`docs/dev/lanes/b76optloop_report.md`
block (C), pcrec-bench commit `efec5366aae1268936595ccbd79e1a5689e5bae4`).
**Quoted verbatim, §3.6:** *"Decision rule. (c) is worth building only
where arm 1 − arm 2 is a material share. If the VM pass is under ~10% of
total time on the throughput regime and under ~25% on the match regime,
the second pass is not the cost and (c) buys little even at full reach;
if it is over half on the match regime, (c) has a target and the reach
figure from M-A says how big."*

### Units

The bench report's table is already reduced to `ns/byte` (best wall time
over 5 or 200 repetitions of the find-all loop, divided by the subject's
byte count — `linux_ask_i89.md` §0.4's `findall.c`, `best*1e9/n`). Arm 1
and arm 2 are timed on the *same* subject (same `n`), so
`(arm1_ns_byte − arm2_ns_byte) / arm1_ns_byte` is algebraically identical
to `(arm1_time − arm2_time) / arm1_time` — no further conversion needed.
Throughput subjects are the three pinned sizes (`t-64k`=65,536 B,
`t-256k`=262,144 B, `t-1m`=1,048,576 B); each pattern's `own` subject is
its `search_short`/`match` regime subject from
`bench/capability/expectations.tsv`, and these are **tiny hand-authored
literals** (`bench/capability/gen_subjects.py`: `v-us-zip` is 5 bytes,
`sec-github-pat` is 93 bytes) — see the caveat in §"Verdict" below.

### Cross-check (by hand, one row)

`wild-secrets-aws-access-key-id`, subject `t-1m`: arm1 = 3.6277 ns/byte,
arm2 = 3.1684 ns/byte. `(3.6277 − 3.1684) / 3.6277 = 0.4593 / 3.6277 =
0.12660…` → 12.66%, matching the reducer's `0.1266` exactly (see
`c2/onepass_mb.tsv`, `cell` rows for this pattern).

### Per pattern × subject share, and per-pattern median (all subjects pooled)

`share = (arm1 − arm2) / arm1`; a cell reading `NA` means arm1 rounded to
0.0000 ns/byte at the report's 4-decimal precision — no share is
resolvable there (0/0, not 0%).

| pattern | own-subject | t-64k share | t-256k share | t-1m share | own share | pattern median (all 4) |
|---|---|---|---|---|---|---|
| codegrammar-flat | cg-key-colon | 0.00% | −0.74% | 4.42% | 18.66% | **2.21%** |
| codegrammar-xflag | cg-key-colon | 0.30% | 33.93% | −0.10% | 25.15% | **12.73%** |
| date-nested-plus | MISSING | −20.00% | 0.00% | NA | n/a | **−10.00%** (noise floor: cells are 0.0005/0.0006/0.0001/0.0001/0.0000/0.0000 ns/byte — below display precision, not a real signal) |
| email-nested-plus | v-email | 0.00% | 0.50% | −0.50% | 31.90% | **0.25%** |
| logparse-atomic | lp-atomic-hit | 0.00% | 0.00% | 0.00% | 8.35% | **0.00%** |
| logparse-atomic-removed | lp-atomic-hit | 14.29% | 0.00% | 0.00% | 43.41% | **7.14%** |
| numeric-id-nested-plus | v-us-zip | 0.00% | 0.00% | NA | 50.00% | **0.00%** |
| phone-list-nested-plus | v-us-zip | 0.00% | 50.00% | NA | 43.33% | **43.33%** (t-256k cell is 0.0002/0.0001 ns/byte — noise-limited) |
| wild-datetime-moment-iso8601 | dt-iso8601 | 14.29% | 0.00% | 0.00% | 62.06% | **7.14%** |
| wild-logparse-syslogbase-expanded | lp-syslog | 0.90% | −0.15% | 13.12% | 19.63% | **7.01%** |
| wild-secrets-aws-access-key-id | sec-aws-key | 1.47% | 1.76% | 12.66% | 27.54% | **7.21%** |
| wild-secrets-github-pat | sec-github-pat | 1.26% | 0.46% | −0.16% | 22.92% | **0.86%** |
| wild-secrets-slack-webhook-url | sec-slack-webhook | −1.56% | −150.04%¹ | −0.18% | 20.20% | **−0.87%** |
| wild-secrets-username-password-pair | sec-userpass | 0.66% | −0.22% | 0.23% | 38.35% | **0.44%** |
| wild-semdiv-empty-alt-repeat-pcre2 | v-ipv4 | 41.46% | −20.50% | 42.84% | 50.00% | **42.15%** |
| wild-validator-ipv4-owasp | v-ipv4 | 0.00% | 0.00% | 0.00% | 65.59% | **0.00%** |
| wild-validator-us-zip-owasp | v-us-zip | 16.67% | 50.00% | NA | 33.59% | **33.59%** |

¹ `wild-secrets-slack-webhook-url`'s `t-256k` cell (0.2432/0.6081 ns/byte)
is a measurement anomaly — arm2 running 2.5x *slower* than arm1 on a
0/0-match subject — coinciding with the bench report's own note of a
`large artifact` compiler warning on this pattern's successor build. Not
excluded from the median (the reducer takes it as reported) but flagged;
the pattern's own-subject cell (20.20%) is unaffected and is the more
reliable number for this pattern.

**Population** (n=17 per-pattern medians, all resolvable):
**median 2.21%**, IQR **[0.00%, 7.21%]**. Count ≥10% threshold: **4**
(codegrammar-xflag, phone-list-nested-plus, wild-semdiv-empty-alt-repeat-pcre2,
wild-validator-us-zip-owasp). Count <10%: **13**.

### Regime split (the rule §3.6 actually applies)

The pooled-median-of-4-cells number above mixes two regimes the rule
scores with *different* thresholds. Split by regime instead (per-pattern
median of the 3 throughput cells; the single `own`/match cell):

| regime | n patterns | median share | IQR |
|---|---|---|---|
| throughput (t-64k/t-256k/t-1m) | 17 | **0.00%** | [0.00%, 0.90%] |
| match (own subject) | 16 (date-nested-plus has none) | **32.75%** | [22.24%, 45.06%] |

Patterns with match-regime share > 50% (the "has a target" bar): **2 of
16** — `wild-datetime-moment-iso8601` (62.06%) and
`wild-validator-ipv4-owasp` (65.59%); a third, `wild-semdiv-empty-alt-repeat-pcre2`,
sits exactly at 50.00% and its throughput share (41.46%) is already well
above the 10% throughput threshold on its own.

### Verdict: **SPLIT**

Applying §3.6's rule regime by regime:

* **Throughput regime clears the "not the cost" bar cleanly**: population
  median 0.00%, IQR entirely under 1% — no pattern's throughput share
  reaches even half the 10% threshold except three (`phone-list-nested-plus`
  25%, `wild-validator-us-zip-owasp` 33.33%, `wild-semdiv-empty-alt-repeat-pcre2`
  41.46%). By the throughput half of the rule alone, (c) is not the cost
  for the great majority of the population.
* **Match regime does NOT clear the same bar**: population median 32.75%
  is above the ~25% "not the cost" threshold but below the 50% "has a
  target" threshold — landing in the gap the rule's own two named
  outcomes do not cover.
* **Per-pattern (16 with own-subject data, both regimes tested)**:
  - **NOT THE COST** (throughput <10% AND match <25%), 5 of 16:
    `codegrammar-flat`, `logparse-atomic`, `wild-logparse-syslogbase-expanded`,
    `wild-secrets-github-pat`, `wild-secrets-slack-webhook-url`.
  - **HAS A TARGET** (match >50%, or match at 50% with throughput already
    >10%), 3 of 16: `wild-datetime-moment-iso8601`, `wild-validator-ipv4-owasp`,
    `wild-semdiv-empty-alt-repeat-pcre2`.
  - **AMBIGUOUS** (falls in neither named bucket), 8 of 16:
    `codegrammar-xflag`, `email-nested-plus`, `logparse-atomic-removed`,
    `numeric-id-nested-plus`, `phone-list-nested-plus`,
    `wild-secrets-aws-access-key-id`, `wild-secrets-username-password-pair`,
    `wild-validator-us-zip-owasp`.
  - `date-nested-plus`: no own-subject data (MISSING); throughput share is
    below the report's display precision on every subject — unresolved,
    counted in neither bucket.

**A likely confound, not resolved by this reduction**: every `own`/match
subject is a tiny hand-authored literal (`bench/capability/gen_subjects.py`
— `v-us-zip` is 5 bytes, `sec-github-pat` is 93 bytes, none over ~90
bytes). At that scale a single find-all call's wall time is dominated by
fixed per-call/per-attempt overhead (VM entry, frame setup, the attempt
loop's own bookkeeping), which arm 1 pays and arm 2 does not — so the
elevated match-regime shares may be measuring call overhead rather than
work that scales with genuine capture-assignment cost. This is exactly
the shape that would produce a population sitting in the gap between the
two named thresholds instead of clearing one cleanly.

**Next measurement if split**: re-run M-B's match arm on a LARGER subject
that still forces a real match with real capture groups to assign — e.g.
each pattern's own-subject literal embedded many times in a longer
buffer, or the same literal repeated at 2-3 sizes — and see whether the
share converges downward as the fixed per-call cost amortizes over more
work. If it does, the match-regime numbers here overstate (c)'s target
and the real decision rests on the throughput regime alone (which already
reads "not the cost" for all but three patterns). If the share holds
roughly flat across subject sizes, the 32.75% median is real and (c) has
a genuine, if not universal, target among capture-forced hybrid patterns.

**Reproduction**: `docs/dev/optloop/c2/onepass_mb.py` (re-runnable;
hardcodes the bench report's table since it is markdown, not TSV — a
maintainer re-running this against a new bench report edits `RAW_TABLE`)
and its output `docs/dev/optloop/c2/onepass_mb.tsv`.
