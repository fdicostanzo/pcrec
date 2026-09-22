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
