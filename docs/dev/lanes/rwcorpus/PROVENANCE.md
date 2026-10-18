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

## Data caveats (facts about the bytes; rwfix, 2026-10-18)

**Line endings.** Every Project Gutenberg file (`prose/` x12, `nonenglish/`
x28) is CRLF on every line (`audit.py` prints `crlf=N/N`). Left as published:
CRLF is real-world data, and `$`, `.` and `\s*$` behave differently on it.
Other classes keep their upstream endings.

**Head bias.** A prefix of these files does not represent the file:
- cut at 40 MiB on a line boundary (the tail is NOT in the subject):
  `logs/openstack.log` (sorted `*.log` concatenation), `logs/hadoop.log`
  (sorted `*.log` concatenation), `logs/bgl.log` (head of the zip member),
  `markup/python_docs.html` (sorted `*.html`), `structured/govinfo_bills.xml`
  (sorted `*.xml`);
- sorted by path then concatenated, whole (not cut): `code/{c,go,java,
  javascript,python,rust}.src`, so a head sample is whichever directory sorts
  first;
- a sorted upstream file, taken whole: `structured/census_gazetteer_places.tsv` (Census gazetteer, sorted by
  state: `^TX` is 0 in the first 4 MiB, 1,863 in the file).
Counts from any prefix of these files are not representative.

## Non-English audit (2026-10-18)
`audit.py CLASSDIR` prints per file: strict UTF-8 validity, mojibake-sequence
count, script mix, CRLF count, and the Gutenberg header's `Language:`. All 28
original files decode as strict UTF-8 with 0 mojibake-sequence hits; four were
still wrong and were replaced (same class, same license basis; new bytes
fetched 2026-10-18):

| dropped | defect | replacement | language / script |
|---|---|---|---|
| pg8186 Actes et Paroles 1 | labelled French, but accents stripped to ASCII (52 non-ASCII chars in 922 KB) | pg798 Stendhal, Le rouge et le noir | French, accents intact |
| pg8453 Actes et Paroles 2 | same | pg2650 Proust, Du cote de chez Swann | French, accents intact |
| pg20175 Chatzopoulos, Fthinoporo | labelled Greek, but Greek stored as Windows-1253 bytes read as Latin-1 (91% Latin letters, 0 Greek): mojibake that is valid UTF-8 | pg27073 Chrestomanos, I Kerenia koukla | Modern Greek, 92% Greek letters |
| pg9000 Sri Vishnu Sahasranaamam | labelled Sanskrit, but ASCII transliteration (`varuNo vaaruNo`): no non-Latin script | pg27081 Mickiewicz, Sonety | Polish: Latin-extended (a-ogonek, l-stroke), the class's weakest script |

Language coverage kept: Chinese, Japanese, Cyrillic (Russian, Bulgarian,
Serbian), Greek, Hebrew, German, French. The Sanskrit slot became Polish;
Devanagari/Arabic could not be sourced (Project Gutenberg has ~1 text each,
none usable). Known and kept: pg4572, pg4573 and pg4580 are the same work
(Fen Zhuang Lou, parts 1-10, 11-20 and complete), so the Chinese text is
partly duplicated.
