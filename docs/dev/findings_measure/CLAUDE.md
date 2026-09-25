# docs/dev/findings_measure/ — the [FINDINGS] run-level estimator measurement

D123 addendum 3 (Frank, 2026-09-25): the run-level estimator measurement
(`requirements.md` R6/Q5) runs NOW, as corpus arithmetic with no `src/`
change, and its data is KEPT for `[FINDINGS]`'s eventual design note to
consume. This directory is that measurement's data and reproduction
record, lane `runest`.

## Files

- `estimator_report.md` — THE DELIVERABLE: which run-level density
  estimator (independence-product baseline / bigram / trigram / word-token
  / hybrid) best predicts a literal run's rarity, at what table size, per
  subject class, and specifically whether it fixes the WAF `union` vs
  `select` vs `from` sign flip `docs/dev/optloop/waf_attribution.md` §3.2
  names. Read this first; every number in it cites a file below.
- `manifest.tsv` — corpus provenance: url, sha256, licence, retrieval
  date, whether the raw text is committed here (R29: only when the licence
  clearly permits redistribution) or manifest-only (re-fetchable).
- `corpora/` — the four training corpora (`web_request`, `log_lines`,
  `prose`, `json`), 80/20 split at measurement time (never committed
  pre-split — the split is deterministic from `scripts/score_estimators.py`
  reading the first N bytes). `web_request.txt` (Apache-2.0) and
  `prose.txt` (public domain) are committed; `log_lines.txt` and
  `json.txt` are gitignored (ambiguous redistribution licence at fetch
  time) — `scripts/fetch_corpora.sh` re-fetches both, sha256-checked
  against `manifest.tsv`.
- `scripts/`
  - `ngram_count.py` — THE SHARED COUNTING MODULE (R27b: the shipped
    generators and the analyzer/exemplar scanner must share one counting
    implementation; this is the python prototype of it, one-pass,
    streaming-friendly). Unigram, bigram, trigram, and whitespace/
    punctuation-delimited token counts over a byte string.
  - `dump_byte_freq.c` — dumps the shipped static prior
    (`src/opt/prefix_k.c`'s `pcrec_byte_freq_ppm`) to `data/byte_freq_ppm.tsv`
    by linking against `build/libpcrec.a`, so estimator (0)'s table can
    never drift from hand-transcription.
  - `build_runs.py` — builds `data/runs.tsv`, the candidate literal runs
    to rank: the bench `capability` patterns' necessary runs (read from
    the already-committed `docs/dev/optloop/c2/reqpos_census.tsv` run
    census, itself produced by compiling with `build/pcrec` and reading
    `RX_REQ_RUN` stamps) plus the three WAF keywords.
  - `fetch_corpora.sh`, `build_json_corpus.py` — re-fetch the two
    manifest-only corpora, sha256-checked.
  - `score_estimators.py` — the scorer: fits per-class bigram/trigram/
    token models on TRAIN, scores all five estimators against TRUE
    held-out density and rank on TEST, runs the WAF sign check, and reads
    (never fits on) the pcrec-bench `t-1m.bin` throughput subject as an
    out-of-sample EVALUATION set only (R30: no shipped analysis may be
    derived from a pcrec-bench subject). Writes everything under `data/`.
- `data/` — every number `estimator_report.md` cites, regenerable by
  re-running the `scripts/` above in order (`build_runs.py`,
  `dump_byte_freq.c`, `score_estimators.py`):
  - `byte_freq_ppm.tsv` — the dumped static prior (candidate 0's table).
  - `runs.tsv` — the candidate runs.
  - `scoring.tsv` — one row per (class, run, estimator): true and
    predicted density, log2 error, whether a token-table hit fired.
  - `table_sizes.json` — per-class table byte counts for bigram/trigram/
    token.
  - `bench_eval.tsv` — the out-of-sample bench-evaluation rows.
  - `tables/*.json` — the derived per-class bigram tables (unigram counts,
    sparse bigram counts, top-200 tokens) for the winning estimator, so a
    later session can inspect or reuse them without re-fetching/refitting.
  - `score_log.txt` — the scorer's own stderr transcript (rank
    correlations, log-MAE, the WAF check, the bench-eval check), archived
    verbatim as the run record `estimator_report.md`'s tables are read off.

Maintenance: update this file when files are added/removed or their roles
change (matches the project's per-directory CLAUDE.md convention).
