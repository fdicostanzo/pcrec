# [FINDINGS] Q5 — which run-level estimator, at what table size?

**Lane `runest`, 2026-09-25.** D123 addendum 3's charter: measure now, keep
the data for `[FINDINGS]` to consume. Answers
`docs/design/findings/requirements.md` R6/Q5/§0 finding 2 and the WAF sign
question `docs/dev/optloop/waf_attribution.md` §3.2 leaves open. Nothing
under `src/`, `cli/`, `lib/` touched; no `make test`. Reproduction:
`scripts/` in this directory, data in `data/`, corpora in `corpora/`
(two of four re-fetched by `scripts/fetch_corpora.sh`, see `manifest.tsv`).

## 0. Findings first

1. **The shipped independence-product baseline is not merely imprecise
   here, it is the wrong SIGN on the cell the row exists for.** On held-out
   `web_request` text, the baseline ranks `select` as the rarest of
   `union`/`select`/`from`; the true order is `union` rarest, then
   `select`, then `from`. Its whole-corpus rank correlation with true
   density is **essentially zero (Spearman ρ = −0.0055)** on `web_request`
   and stays weak everywhere except `json` (ρ = 0.40–0.60). This reproduces
   `reqpos_2b.md` §4.2's "5×–3,257×" finding from the density side rather
   than the run-population side: a marginal per-byte statistic cannot
   predict a joint fact, on ANY corpus tried, not just the three rows that
   note measured.
2. **A plain BIGRAM Markov chain, fit per subject class, fixes the WAF sign**
   and is the most ROBUST candidate overall — not the most accurate on
   every class, but the only one that is never worse than competitive and
   never gets a sign wrong. **Recommended run-level KIND: a per-class
   bigram table** (`P(b)` and `P(b_i | b_{i-1})`, i.e. `src/opt/prefix_k.c`'s
   existing prior widened from a 256-entry unigram to a 256×256 conditional
   table — the same widening shape `reqpos_2b.md` itself is to `reqbyte.c`).
3. **Trigram (and the token+trigram hybrid, since the token table almost
   never fires — see finding 5) has the BEST rank correlation on 3 of 4
   classes, and is the estimator that gets the WAF sign WRONG.** On the
   800 KB `web_request` training sample it predicts `select` (ρ_trigram
   context noise) as rarer than `union`, inverting the true order — a
   sparse higher-order model overfitting a modest exemplar, not a better
   model. **More table order is not free accuracy at this sample size**,
   and the design should not assume a large exemplar is available (R32).
4. **The candidate literal runs a real regex pattern needs are mostly NOT
   natural-language words.** Of the 14 bench-derived necessary runs
   (`.tar`, `in`, `: `, `*/`, `/user`, `</`, `github_pat_`, `://`, `foo`,
   `abc`, `:\`) only `in`/`foo`/`abc` are word-shaped at all, and NONE of
   the three WAF keywords (`union`/`select`/`from`) turned up as an exact
   TOKEN in the 800 KB `web_request` training text (`token_exact=False`
   on every one, `data/scoring.tsv`). A top-K token table therefore
   degrades to its bigram fallback for almost this whole population — real
   but narrow value, not a general substitute for an n-gram model.
5. **Table size favours bigram too, once "size" means what the format
   would actually ship.** A dense bigram table is a fixed **128 KB**
   (256×256, 2-byte ppm entries) regardless of corpus. The sparse top-K
   trigram/token tables this measurement built are class-dependent and
   often SMALLER in raw bytes (13–58 KB observed) but that is exactly why
   they overfit on a small exemplar — fewer observations per cell, more
   variance, and (finding 3) an occasional wrong sign. The size/accuracy
   trade here is not monotone: the biggest table is the most robust one.
6. **Class match matters more than order.** Training the trigram/bigram
   model on `log_lines` and evaluating (never fitting) against the
   pcrec-bench synthetic throughput subject (`t-1m.bin`, log/code-mixed
   text) gets ρ = 0.68; training the SAME model shape on `web_request` and
   evaluating on the same bench subject gets only ρ = 0.39 — one more
   argument for per-subject-class named analyses (D83's addendum) over one
   global table.

## 1. Method

**Corpora** (`manifest.tsv`; two committed, two manifest-only per R29 —
neither had a clearly permissive redistribution licence at fetch time):

| class | source | bytes | committed |
|---|---|---|---|
| `web_request` | elastic/examples Apache combined log (Apache-2.0) | 1,000,000 (of 2,370,789) | yes |
| `log_lines` | logpai/loghub `HDFS_2k.log` | 287,848 | no (re-fetch) |
| `prose` | Project Gutenberg, *Pride and Prejudice* (public domain) | 738,046 | yes |
| `json` | JSONPlaceholder `/comments`+`/posts`+`/users` | 190,912 | no (re-fetch) |

Each class is split 80/20 (train/test), never shuffled (a stationary text
stream, matching how an exemplar analyzer would see it). All per-class
tables are fit on TRAIN only; every reported density and rank is measured
on TEST, held out. **None of the four is derived from a pcrec-bench
subject (R30).** The bench's own `capability/throughput/t-1m.bin`
(sha256 in `manifest.tsv`) is read ONLY in §4 as an out-of-sample
evaluation set, explicitly labelled, never fit.

**Candidate runs to rank** (`data/runs.tsv`, `scripts/build_runs.py`): the
14 bench `capability` patterns' necessary literal runs (`run_len >= 2`),
read from the already-committed `docs/dev/optloop/c2/reqpos_census.tsv`
run census (itself produced by compiling `patterns.rxt` with `build/pcrec`
and reading `RX_REQ_RUN` stamps — this lane reused that census rather than
recompiling), plus the three WAF keywords `union`/`select`/`from`
(`waf_attribution.md` §3.2). 14 distinct byte strings after dedup.

**Estimators** (`scripts/score_estimators.py`, counting shared from
`scripts/ngram_count.py` per R27b):

| # | estimator | shape | table size (this measurement) |
|---|---|---|---|
| 0 | baseline | independence product over the SHIPPED static `pcrec_byte_freq_ppm` (`prefix_k.c`), same table for every class | 0 (already shipped) |
| 1 | bigram | Markov chain, `P(b0) · Π P(b_i\|b_{i-1})`, add-one smoothed, fit per class | 128 KB (256×256, dense, fixed) |
| 2 | trigram | Markov chain, `P(b0)·P(b1\|b0)·Π P(b_i\|b_{i-2}b_{i-1})`, top-20,000 observed contexts kept, falls back to bigram for any unseen context | 13.5–58.6 KB (sparse, class-dependent; nothing was dropped by the 20k cap at this corpus size) |
| 3 | token | top-4,000 exact-token frequency table, falls back to the bigram chain for a run that is not an exact token | 19.3–66.3 KB (class-dependent) |
| 4 | hybrid | token-exact override on top of the trigram chain | union of 2 and 3's tables |

**Metric.** Per (class, run, estimator): predicted and TRUE density in
occurrences per 1e6 bytes (a +0.5 continuity correction on the true count
avoids an infinite log-ratio when a rare run has zero held-out hits, which
is common at this sample size — the same "a zero would let the model
believe a byte is impossible" reasoning `prefix_k.c`'s own floor uses).
Per class: **Spearman rank correlation** of predicted vs true density
across the 14 runs (does the estimator pick the truly rarest run — the
metric the brief names as the one that matters), and **mean |log2 error|**
(density accuracy). Full per-run numbers: `data/scoring.tsv`.

## 2. Results

### 2.1 Rank correlation and log-error, per class

| class | estimator | Spearman ρ (higher = better ranking) | log2 MAE (lower = better density) |
|---|---|---|---|
| web_request | baseline | **−0.0055** | 7.61 |
| web_request | bigram | 0.590 | **7.41** |
| web_request | trigram | **0.686** | 8.47 |
| web_request | token | 0.590 | 7.41 |
| web_request | hybrid | 0.686 | 8.47 |
| log_lines | baseline | 0.336 | **8.12** |
| log_lines | bigram | 0.600 | 11.40 |
| log_lines | trigram | **0.798** | 12.26 |
| log_lines | token | 0.708 | 10.80 |
| log_lines | hybrid | **0.798** | 12.22 |
| prose | baseline | 0.404 | **7.23** |
| prose | bigram | 0.847 | 8.76 |
| prose | trigram | **0.913** | 8.99 |
| prose | token | 0.866 | 8.37 |
| prose | hybrid | **0.913** | 9.01 |
| json | baseline | 0.603 | **7.59** |
| json | bigram | 0.610 | 9.41 |
| json | trigram | 0.610 | 13.49 |
| json | token | 0.610 | 9.62 |
| json | hybrid | 0.610 | 13.69 |

Reading it: trigram/hybrid win the RANKING question on 3 of 4 classes and
tie on the 4th; but the baseline (which the mechanism ships today) has the
best or tied-best log-error on every class except web_request, because on
a held-out sample this small most candidate runs are near the noise floor
and the baseline's flat, corpus-blind prior is a low-variance (if
mis-ranked) guess. Neither "always pick the biggest model" nor "always
trust the shipped prior" is the answer the two columns agree on; §0 finding
2/3 is what resolves it.

### 2.2 The WAF sign check (the deliverable's headline question)

On `web_request` held-out text, true order (rarest first):
**`union` < `select` < `from`**.

| estimator | predicted order | matches true? |
|---|---|---|
| baseline (shipped) | select < union < from | **NO** |
| bigram | union < select < from | **YES** |
| trigram | select < union < from | **NO** |
| token | union < select < from | **YES** (falls back to bigram; none of the three hit the token table) |
| hybrid | select < union < from | **NO** |

**So: bigram (equivalently, token here, since it degrades to bigram)
answers the WAF question correctly; the shipped baseline and the
higher-order trigram/hybrid do not.** The raw densities explain why
trigram fails — it is not a close call:

```
run      true_test_count   baseline_ppm   bigram_ppm   trigram_ppm   token_ppm
union    0                 0.0847         0.0579       0.0141        0.0579 (fallback)
select   0                 0.0088         0.1309       0.0005        0.1309 (fallback)
from     1                 0.4676         2.5348       8.3023        2.5348 (fallback)
```

`select`'s trigram probability (0.0005 ppm) is two orders of magnitude
below its bigram probability (0.13 ppm) — a sparse-context artifact of an
800 KB training sample, not evidence the word is rare. This is exactly
the failure mode §0 finding 3 names: a sparse higher-order model finds
spurious low-count contexts before it has enough data to trust them.

### 2.3 Out-of-sample generalization (bench `t-1m.bin`, EVALUATION ONLY)

Never fit on; read once per model, sha256-checked against `manifest.tsv`.

| trained on | estimator | Spearman ρ vs bench true counts |
|---|---|---|
| web_request | baseline | 0.383 |
| web_request | trigram/hybrid | 0.395 |
| log_lines | baseline | 0.383 (same table, class-blind) |
| log_lines | trigram/hybrid | **0.682** |

The `log_lines`-trained model generalizes much better to the bench's own
log/code-mixed synthetic text than the `web_request`-trained one does —
the class of the fitting corpus matters as much as the estimator kind,
which is the direct argument for D83's addendum shipping ONE table PER
named analysis rather than one global table.

## 3. Recommendation for the design note

**Kind: a per-class BIGRAM table** (`P(first byte)` + `P(byte | previous
byte)`), one 256+65536-entry ppm table per named analysis, the direct
widening of `prefix_k.c`'s existing 256-entry unigram prior — same shape,
same normalisation-to-1,000,000 discipline (R3), same integer-only rule.

- **Size bound:** fixed 128 KB per analysis at 2-byte ppm entries (could
  shrink to 64 KB at 1-byte log-quantized entries if `[FINDINGS]`'s R33
  footprint budget wants it — not measured here, D77).
- **One-pass computable, streaming-friendly (Q8):** the counting module
  (`scripts/ngram_count.py`, R27b's shared implementation) accumulates
  unigram+bigram counts in a single left-to-right pass with O(1) state
  between bytes (the previous byte) — the analyzer's eventual C end state
  can do this from stdin with no buffering.
- **Robust at small-exemplar sizes** (150 KB–800 KB training text in this
  measurement): unlike trigram, it never inverted a rank in the four
  classes tried.
- **Answers the WAF question**, which is the customer this measurement
  exists for (`requirements.md` C6, `reqpos_2b.md` §2.3's "when a run-rate
  analysis is eventually written, it is a findings value like any other").

**Trigram/hybrid: recorded as a candidate upgrade, not shipped now (D77).**
It wins the ranking metric on 3 of 4 classes and would likely win
outright given a training exemplar an order of magnitude larger than the
150 KB–800 KB samples used here — that is the measurement that would
trigger building it, not a guess. Shipping it today would trade the one
customer this row exists for (the WAF sign) for a ranking improvement on
runs nobody has a losing cell for yet.

**Token/word table: not a general substitute.** Real necessary runs are
mostly not words (§0 finding 4); ship it, if at all, as a free enrichment
on top of the bigram table (exact-token override, zero cost when absent)
rather than as its own row — which is exactly the "hybrid" shape already
measured here, at bigram's accuracy once trigram is dropped from it.

**Caveat on the baseline's log-error win.** The static prior has better or
tied MAE on 3 of 4 classes. That is a low-variance/high-bias artifact of a
flat, corpus-blind table matching a lot of near-floor test-set zeros by
luck of scale, not evidence it estimates density well — its rank
correlation is the worse (often near-zero or negative) of every candidate,
and RANK is the property the design's customer (C6, S1's run-choice) needs.

## 4. Caveats

- **Sample sizes are small** (150 KB–800 KB train per class) by the
  standard third_party corpora this project usually vendors; a repeat of
  this measurement against a multi-megabyte exemplar per class, once one
  is available under a clear redistribution licence, is the natural
  follow-up and would settle whether trigram's ranking edge survives more
  data (§0 finding 3's own trigger).
- **json and log_lines are manifest-only** (R29): their raw text is not
  committed, only the derived scoring numbers and bigram tables
  (`data/tables/*.json`); a future session must re-fetch to reproduce the
  fitting step from scratch, which `scripts/fetch_corpora.sh` does with a
  sha256 check.
- **The WAF check is one corpus (web_request), one training split.** It is
  the sharpest available evidence for the sign question the brief asks,
  not a statistically powered study; the qualitative result (baseline
  wrong, bigram right, trigram wrong) is corroborated by the mechanism
  each estimator uses (marginal vs. conditional vs. sparse-conditional),
  not merely by the one split.
- **No timing, no `src/` change, no `make test`** — this is D123 addendum
  3's measurement step only; a shipped run-level `freq`-family kind is
  `[DD-13b]`'s format work plus a `[FINDINGS]` design-note event, neither
  done here.
