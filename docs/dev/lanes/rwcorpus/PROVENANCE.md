# rwcorpus provenance (2026-10-13)

Every file's URL, license, retrieval date and sha256 is a row in `manifest.tsv`.
Licensing basis per source family (checked at retrieval, not assumed):

| family | license basis |
|---|---|
| Project Gutenberg texts (prose, nonenglish) | public domain in the US; gutenberg.org/policy/license.html (trademark terms only on the header/footer, left in place) |
| Loghub (Apache error, Linux syslog, OpenStack, Hadoop, Zookeeper, BGL) | Zenodo record 8196385 metadata: `cc-by-4.0` (zenodo.org/api/records/8196385). Attribution: Zhu et al., "Loghub: A Large Collection of System Log Datasets for AI-driven Log Analytics". NB the GitHub README says "freely available for research or academic work"; we rely on the Zenodo CC-BY-4.0 record |
| elastic/examples apache_logs | Apache-2.0 (repo LICENSE, GitHub API `license`) |
| Source code | per-tarball: Lua MIT; Redis 7.2.4 BSD-3 (deps/ excluded); jQuery MIT; ripgrep MIT/Unlicense; Django BSD-3; cobra Apache-2.0; Guava Apache-2.0 |
| Python docs HTML | PSF License / 0BSD |
| USGS, Census, GPO govinfo | US Government works, public domain |
| Natural Earth | public domain (naturalearthdata.com/about/terms-of-use) |
| libpng | PNG Reference Library License v2 (permissive) |

## PII handling
Loghub is "NOT sanitized" upstream. prep.py scrubs, deterministically: IPv4
addresses -> `10.a.b.c` (sha1-derived), any e-mail address ->
`user@example.invalid`, `rhost=`/`user=` values, ftpd reverse-DNS hostnames.
System account names (root, news, cyrus, test) remain in syslog lines; no
real person's e-mail or credential was found in the scrubbed outputs (greps
recorded in the report). Code/doc archives and the binary-class tars keep
upstream AUTHORS/credit names (public attributions under the stated licenses).
Prose/nonenglish are untouched. Scrubbing changes byte counts slightly; the
manifest pins the post-scrub bytes.

## Volatile rows
The two USGS FDSN queries carry an `updated` timestamp per event that USGS
revises; a re-fetch may differ (manifest.py warns, does not fail).

## Skipped (license or PII not established)
See `../rwcorpus_report.md` "Skipped".
