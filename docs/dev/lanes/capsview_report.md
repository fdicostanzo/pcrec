# [OPTLOOP.1-CAPSVIEW] — the captures-vs-captures re-ranking (lane `capsview`)

2026-09-22, docs-only, branch `lane/capsview` from `main` `69172a00`. Nothing
under `src/`/`cli/`/`lib/`/`tests/`; nothing written in
`/Users/fdicostanzo/pcrec-bench` (read-only reference). No build was needed
or run.

## The ask

Frank's ruling on `cycle1_analysis.md`'s (lane `optrev`) ranking: "we do
have the fastest times but sometimes they are fastest because we consider a
version without capture. We need to consider capture vs capture engines for
those. Apples vs apples."

## What was delivered

- `docs/dev/optloop/cycle1_caps_view.md` — the memo, five sections matching
  the brief's five deliverables (CAPS table, NOCAPS table, DELTA table,
  mechanisms re-scored + new population, totals).
- `docs/dev/optloop/capsview.py` — the analysis script. Reads the SAME
  reproduction artifacts `cycle1_analysis.md`'s own scripts (`rank.py`,
  `stamps.py`) wrote to the shared scratchpad (this session's scratchpad
  UUID happens to match the authoring lane's, so `rank.json` and
  `stamps.json` were already on disk — no recompile, no re-measurement was
  needed or performed).
- `docs/dev/optloop/capsview_data.json` — the script's structured output;
  every table in the memo is rendered from this file.
- `docs/dev/optloop/CLAUDE.md` — one entry each for the three files above.

## Method

Reused `cycle1_analysis.md` §0's engine-exclusion rules (pcre2-jit never a
target; vectorscan excluded; rust reported with a scalar-only column
alongside) and its per-family weight/score formula
(`score = weight × log2(ratio)`, clamped at 0, weights fixed at §0's own
per-family values over the full 125-row population), applied to two new
comparisons instead of the best-of-four-pcrec-variants one §1 used:

- **CAPS**: pcrec's shipped default (`auto-caps`) against capture-bearing
  engines only (`pcre2-interp`, `oniguruma`, `re2`, `re2-longest`, `rust`,
  `tre`), with a best-scalar-caps column (same set minus `rust`).
- **NOCAPS**: `auto-nocaps` against `pcre2-dfa` — the only algorithmic
  nocaps-vs-nocaps target once vectorscan is excluded per §0.

## Findings (numbers inline, all traceable to `capsview_data.json`)

| | scorable cells | pcrec wins/ties | pcrec loses | no-data |
|---|---|---|---|---|
| CAPS (`auto-caps` vs. capture engines) | 123 | 84 | 39 | 2 |
| NOCAPS (`auto-nocaps` vs. `pcre2-dfa`) | 110 | 100 | 10 | 15 |

- **65 of §1's 91 win/tie rows were carried by `auto-nocaps`**, not the
  shipped default — the majority of §1's own headline number. Of those 65,
  **58 still win or tie** under the caps-only comparison; **5 flip from WIN
  to LOSS** (the DELTA table) — two more than `cycle1_analysis.md` §1.1
  named (`wild-validator-us-zip-owasp` thr at 1.67×, `wild-secrets-github-pat`
  srch right at 1.01×, both missed by §1.1's "three sharpest" framing which
  did not sweep the whole `ratio > 1.0` boundary).
- **Two cells have no `auto-caps` data at all**:
  `wild-datetime-datefinder-alternation` (both regimes) — the shipped
  default cannot even produce an artifact (§1.2's 500,000-byte code cap),
  yet §1's best-of-four ranking reports this pattern as an ordinary WIN.
- **The five §3 mechanisms are ROBUST**: re-scored using `auto-caps` alone
  against the capture-only competitor set, all five move by under 2% of
  their original score (sum 8.005 → 8.0260). None of M1–M5 was an artifact
  of the no-captures comparison.
- **The caps-losing population's unexplained remainder is 25 rows, score
  6.0106** (43% of the whole caps-losing total, 14.0366), bucketed by the
  `auto-caps` artifact's own `RX_ENGINE_WHY` stamp:
  - **`capture group`, 14 rows, score 4.6833 (dominant, as the brief
    expected)** — the population named for the manager's separate
    captures-mechanism survey. Three rows carry a captures-on/off factor
    over 20,000× (the same three §1.1 already flagged); the other eleven
    carry a factor of 0.98×–1.71× — captures cost near nothing on these,
    and four of them (`wild-secrets-github-pat`, `wild-validator-ipv4-owasp`,
    `wild-validator-us-zip-owasp`) have NO second module requirement, so
    "capture group" is the whole reason yet the cost is negligible — worth
    a line in the survey's own scoping.
  - **`engine=dfa, no WHY stamp`, 8 rows, score 1.0931** — NOT a
    captures-cost population (caps÷nocaps ≈ 1.00× on every row): this is
    `cycle1_analysis.md` §2.3(j)'s already-named SIMD-deferral population
    reappearing because it also loses to the narrower capture-only
    competitor set.
  - **`(?R)`, 2 rows** and **`(?<=...)`, 1 row** — recursion/lookbehind
    forcing VM selection regardless of captures (caps÷nocaps ≈ 1.00–1.02×).

## Corrections made during drafting (recorded for anyone re-deriving these numbers)

Two numeric claims were caught wrong before commit and are worth naming so a
future re-derivation doesn't repeat them: (1) the nocaps-carried-win count
is 65 of 91, not an earlier guess of ~32 — checked directly against
`rank.json`; (2) the 15 `pcre2-dfa` no-data cells are NOT all
`cap-backref`/`cap-recursion` `unsup` rows — 10 are `unsup`, but 4 are
`wrong` and 1 is `gave-up`, all five in unrelated families
(`semantics-divergence`, `wild-logparse`) on the `short-subject-search`
regime — checked against the bench's own `st` status field per cell rather
than assumed from the family name. Also corrected an over-broad claim about
the 11 low-cost "capture group" rows sharing a `backrefs`/`recursion`
`requires` field — four of the eleven have no second module requirement at
all (`rank.json`'s `requires` is empty), rewritten to state the actual
per-pattern split rather than a uniform claim.

## Validation

Docs-only lane; no `make`/`make test`/`make strict` run (nothing under
`src/`/`cli/`/`lib/`/`tests/` touched). The one check performed was
re-deriving every headline number in this report directly from
`capsview_data.json` after each correction above, by re-running the exact
python snippets shown in the memo's own reproduction section — not a suite
run, but every number in both the memo and this report was independently
recomputed at least once after the corrections, not just asserted.

## Handback

Complete. Committed to `lane/capsview` (commit `84136aea`). Nothing owed.
The `capture group` population (14 rows) is handed to the manager's
separate captures-mechanism survey as this memo names it — no new mechanism
proposed here, per the brief's own scope limit.
