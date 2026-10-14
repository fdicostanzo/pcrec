# rwquest2 — second blinded user-question list (SEALED), [REGIME-CORPUS] step 2b

Lane `rwquest2` (2026-10-14, sonnet). Role-play: a USER with the rwcorpus pile,
writing the regexes they would actually run. The list is a sealed reserve (hash only,
`rwquest2/SEALED.md`); this report carries method, disclosure and data surprises, and
NO question content.

## Method
- Sampled every class from the start, middle and end (head, `sed -n`, random line draws,
  per-file byte/line facts via `python3 -I` scripts kept outside the corpus subtrees).
  Nothing from the corpus was executed.
- Wrote 165 questions (target was ~20 per class; trimmed from 179, the rest kept for mix):
  everyday literals and counts, extraction with captures, validation-shaped tokens
  (octet-range IPv4, ISO timestamps, ids), caseless, multiline and dotall, lookarounds,
  backreferences, alternations, possessive/`\K`/recursion/named-group power patterns,
  verbose mode, `\p{Script}` and UCP-aware word-boundary patterns for the non-English
  files, and bytes-mode patterns for the archive/compressed class.
- Fields per row: id, class, files, intent, PCRE2 pattern, flags (`i m s x utf ucp`; no
  `utf` = byte mode), mode (find-all 121 / count 22 / line-by-line 17 / first 5),
  match-frequency GUESS (none/rare/sparse/moderate/dense per MiB; written before any
  measurement, never edited afterwards), then python-measured columns.
- Python sanity check (`python3 -I`, `re`): compiled all rows; counted on a sample of at
  most 1.5 MiB per file (whole file if smaller; head/middle/tail 512 KiB chunks cut at
  newline boundaries otherwise), and re-scanned the full file whenever the sample read
  zero (5 rows). 159 rows `ok-sample`, 5 `ok-fullscan`, 1 `py-unsupported` (a recursion
  pattern). Where `re` lacks the construct (`\p{..}`, `\x{..}`, `\K`, `(?<name>)`),
  a hand-written python-equivalent pattern is recorded in the last column and was the
  one counted. All 165 PCRE2 patterns also compile under the box's libpcre2-8
  (ctypes, compile-only; no pcrec code or test read).
- Measured vs guessed: 76 of the 164 checked rows fall in the guessed density bucket
  (the "dense" bucket was set far too high: only 45 guessed dense; very few rows exceed
  50,000 matches per MiB). Counts are sample-based lower-bound-ish signals, not corpus truth.

## Disclosure: what reached me anyway
- Auto-injected at startup: the pcrec root `CLAUDE.md`, the manager memory index
  `MEMORY.md`, `docs/CLAUDE.md`, `docs/dev/CLAUDE.md`, `docs/dev/lanes/CLAUDE.md` and
  `docs/dev/lanes/rwcorpus/CLAUDE.md`. I did not Read any `src/`, `tests/`, `cli/`,
  `lib/`, `analyze/`, `memfn/`, `docs/design/`, `docs/spec/`, other `docs/dev/` files, nor
  pcrec-bench; I read only BOILERPLATE.md, `rwcorpus/manifest.tsv` and
  `rwcorpus_report.md`.
- Those injected files include one-line summaries of every lane report. Two relevant to
  independence: (1) the `rwquest_report.md` summary line (the FIRST list): that it has 177
  questions over the 7 classes (~25 each) with flags, run mode and guessed vs
  python-measured frequency, 160 compile in python, 17 py-unsupported, and the findings
  "every prose and non-English file is CRLF, head-sample counts mislead on sorted files,
  two non-English files are not what their name says". No question text was in it. That
  summary may have shaped my column design (guess + measured) and made me check line
  endings and file identity; I verified each fact on the corpus myself. (2) the long
  summaries of the regime/cost-model, bench and kit lanes (what the decision table is
  for); I did not use them to choose patterns.
- I did not read `docs/dev/lanes/rwquest/` or `rwquest_report.md` themselves.

## Data surprises (facts about the corpus; no question content)
- Every prose and non-English file is CRLF throughout (not just some), so anchored
  line patterns see a trailing `\r`; the hadoop and zookeeper logs also carry CR
  line endings on a share of their lines (17k / 21k CR-bearing lines in their first
  3 MB); the other logs and the code/markup/structured files have none.
- `structured/census_gazetteer_places.tsv` rows are space-padded to a fixed 200 bytes, so
  `$`-anchored field patterns need `\s*$`; the Natural Earth file is ONE 13 MB line and
  govinfo has a 7 MB line.
- Gutenberg editions here use typographic quotes and apostrophes (U+201C/U+201D/U+2019)
  in the English texts, so ASCII-quote patterns silently miss; the French files in this
  pile (pg8186, pg8453) have accents stripped to ASCII; `nonenglish/pg20175` is titled
  Greek but its body is Greek mis-decoded as Latin-1 (Latin-letter mojibake); the Hebrew
  files carry gershayim abbreviations and almost no niqqud; the German Hegel text uses
  the pre-1996 spelling.
- Python 3.12 docs HTML says "Added in version", not "New in version" (the older
  phrasing matches nothing); the syslog scrubbing replaces every `rhost=`/`user=` value
  with the same token, so "interesting host/user" questions have an empty answer here.
- BGL lines carry the node location twice per line; openstack file names are prefixed to
  every line; the compressed streams in `binary/` give a few random-looking hits for
  short magics, while tar members, NUL padding and octal fields are dense.
- Head samples mislead (sorted order again): e.g. the first lines of the apache error log
  are 2005 notices, while the file as a whole has about 38k error lines to 14k notices.

## Deviations
- 165 rows instead of ~140 (about 24 per class); one new directory
  `worktrees/.corpus/sealed/` was created for the sealed file and scripts (inside the
  gitignored worktrees tree, as instructed).
- The first (`rwquest`) list was not consulted, so overlap in intent with it is possible.
