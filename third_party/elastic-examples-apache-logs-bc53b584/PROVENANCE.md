# PROVENANCE — elastic/examples, "Common Data Formats/apache_logs", pinned

## Source

| | |
|---|---|
| **Origin** | https://github.com/elastic/examples, path `Common Data Formats/apache_logs/apache_logs` |
| **Pinned commit** | `bc53b584c0f9f574d4373193334bf03541a54936` ("Fix a few errors in log file", 2017-11-06) — the LAST commit to touch this file's path, found via `GET /repos/elastic/examples/commits?path=...` (D123 addendum 6's "prefer a stable, versioned retrieval point ... a pinned commit"; the earlier committed sample cited only the `master` branch, which moves) |
| **Retrieved** | 2026-09-27 |
| **Retrieved by** | lane `findb5src`, `[FINDINGS]` B5 (sourcing half) |
| **Licence** | Apache License 2.0, per `GET /repos/elastic/examples/license` (`LICENSE` in this directory, fetched at the same pinned commit) |
| **Modified?** | The vendored file is a **TRIMMED PREFIX**, not the full file — see "Trim" below. Within that prefix it is byte-for-byte as retrieved. |

### File, with the checksum retrieved

| file | full-file SHA-256 (at the pinned commit) | full-file bytes | vendored file | vendored SHA-256 | vendored bytes |
|---|---|---|---|---|---|
| `Common Data Formats/apache_logs/apache_logs` | `f15c31e905f86c7b4b6ab44aee74d0a2086dce89f010187d983edea7ef0364ef` | 2,370,789 | `apache_logs.txt` | `43cfdc461a4ccecd3e93bbe0e30fd022a416e6fbe0ad2e613b1a13b85bee0e47` | 1,000,000 |

Verify the vendored file: `shasum -a 256 third_party/elastic-examples-apache-logs-bc53b584/apache_logs.txt`.
Verify it against the upstream original: fetch the pinned commit's raw file
(`https://raw.githubusercontent.com/elastic/examples/bc53b584c0f9f574d4373193334bf03541a54936/Common%20Data%20Formats/apache_logs/apache_logs`),
confirm its SHA-256 is the full-file value above, then confirm
`head -c 1000000` of it reproduces the vendored file's SHA-256.

### Trim

`apache_logs.txt` is the **first 1,000,000 bytes** of the pinned commit's
file, not the whole 2,370,789-byte file. This is not a new decision: it
reproduces the trim `docs/dev/findings_measure/manifest.tsv` and
`docs/dev/findings_measure/corpora/web_request.txt` already made for the
same source under the `master` URL (same bytes — see "Cross-check"
below) — kept here at the same size so the two committed copies of "the
`web_request`/`weblog` sample" describe the same exemplar rather than two
different ones, and because `docs/design/findings/design.md` §8.3 states
the bundle sizes (freq/cpfreq/bigram) against a 1,000,000-byte sample
already. A full-file vendor would be a defensible alternative (2.3 MB is
not large by this directory's own precedent — `ucd-16.0.0/UnicodeData.txt`
is 2.18 MB) but was not taken, to avoid two slightly different exemplars
answering to the same measured numbers in `design.md`.

**Cross-check performed at retrieval time**: the pinned commit's file's
SHA-256 (`f15c31e9...`) matches the SHA-256 the existing
`docs/dev/findings_measure/manifest.tsv` row already recorded for the
`master`-URL fetch (also `f15c31e9...`) — this file has had no commits
past `bc53b584` (2017-11-06) on the `master` branch either, so re-pinning
changed the CITATION (an immutable commit instead of a moving branch
ref), not the bytes.

## What derives from it

| derived artifact | produced by | consumed by |
|---|---|---|
| `src/findings/weblog.rxt` (the shipped `weblog` analysis, `[FINDINGS]` B5) | `generate.py` in this directory, running `build/pcrec-analyze` over `apache_logs.txt` | module `findings`' `analysis weblog` bundle: `freq` + `cpfreq` blocks (design.md §13 B5), a byte-rate exemplar for C6 (the WAF sign check / S4(a)'s run pick) |

`generate.py` writes it (lane `findb5`, 2026-09-28; the sourcing lane's
`generated_preview.rxt` scratch check is retired); `make gen-tables`
regenerates it and the store, and `make test-findings` sec. 12 runs
`generate.py --check`.

## Why this class ships (D123 addendum 7)

`web_request`/`weblog` is one of the two FIRST shipped named analyses,
because it has a measured customer: C6 (the WAF `union`/`select`/`from`
sign question, `docs/dev/optloop/waf_attribution.md` §3.2) and S4(a)'s
run pick (`docs/dev/findings_measure/estimator_report.md`). `json`/`prose`
(also in `docs/dev/findings_measure/`) stay measurement controls and are
not shipped.

## Licence note

The Apache License 2.0 permits redistribution of the Work (§4), which is
what this vendoring is. `LICENSE` in this directory is the pinned
commit's own top-level `LICENSE` file, unmodified.
