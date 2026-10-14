# rwquest report — blinded user questions over the real-world corpus

Lane `rwquest` (2026-10-14, sonnet). Facts only: 177 questions (about 25 per
class), one table, one check script. No timing, no engine run, no design.
Deliverables: `rwquest/questions.src` (input), `rwquest/check.py`,
`rwquest/questions.tsv` (generated), `rwquest/CLAUDE.md`.

## Disclosure (what reached me beyond the data)

The brief asked me not to read the project. At spawn I nevertheless received
injected context, which I did not choose and could not unread:

- the root `CLAUDE.md` (the maintainers' working agreement: pcrec is a
  PCRE-to-C ahead-of-time compiler, with its build/test targets and a long
  situation index);
- `docs/CLAUDE.md`, `docs/dev/CLAUDE.md` and `docs/dev/lanes/CLAUDE.md`, which
  together are a very long digest of internal work: engines (DFA, VM, hybrid),
  prefilters, required-byte and required-run pre-checks, start sets, `memchr`
  kernels, reverse-end walks, SIMD plans, the bench, and per-lane findings;
- `docs/dev/lanes/rwcorpus/CLAUDE.md`, and the manager's memory index.

I also read what the brief allowed: `BOILERPLATE.md`, `manifest.tsv`,
`rwcorpus_report.md`. I did not open anything under `src/`, `tests/`, `cli/`,
`lib/`, `analyze/`, `memfn/`, `docs/design/`, `docs/spec/`, or the bench, and I
did not look at any existing pattern corpus.

Did it influence me? Probably slightly, and I cannot rule it out. The patterns
were written after sampling each file and are ordinary grep/log/code idioms. But
I had read that rare literals, required bytes, doubled words, end anchors and
many-keyword alternations matter, and the brief itself asked for rare vs
very-common and `\b`/lookaround/backreference cases; I included all of those,
and cannot separate "the user would ask" from "I was primed". The guessed
frequencies were written from the file samples, not from the digest.

## What was produced

| class | questions | notes |
|---|---|---|
| logs (7 files) | 28 | everyday greps, IPs, UUIDs, timestamps, key=value, negative lookahead per line |
| code (6 langs) | 27 | definitions, includes, #define, TODO, literals, annotations, long lines |
| prose (12 books) | 27 | words, names, quotes, doubled words, lookbehind/lookahead, headings |
| structured | 24 | TSV rows, CSV fields, GeoJSON keys and coordinates, XML tags and attributes |
| markup | 24 | HTML tags/attrs/ids/entities, rst directives and roles, markdown links |
| nonenglish | 25 | Han/Kana/Cyrillic/Greek/Hebrew runs, ruby text, lookarounds on `\p{L}`, caseless Cyrillic |
| binary | 22 | tar/zip/gzip/bz2/png/gettext magics, NUL runs, printable strings |

Modes: 122 find-all, 44 count, 6 line (grep-style), 5 first-match. Flag
sets: 103 none, 27 multiline, 21 utf, 15 caseless, 5 dotall, 5 with ucp
(utf, utf+ucp, utf+ucp+caseless, utf+multiline are separate sets).

## Check results

`check.py` compiles with python 3.14 `re` and counts on a 4 MiB head sample and
on the whole file (up to 64 MiB; every file fits). Total runtime under 10 s.

- 160 questions compile and run in python (`ok`).
- 17 are `py-unsupported` (all nonenglish: `\p{Han}`, `\p{Hiragana}`, `\p{Lu}`,
  `\x{..}` and similar); each has a hand-written equivalent (explicit ranges)
  and its counts come from that equivalent. They are marked
  "py-unsupported ... (equiv)".
- No timeout, no catastrophic backtracking in python on any question.
- Guess vs measured frequency (own thresholds: rare <10 matches/MiB, some <500,
  many <10000, everywhere beyond; 172 non-`first` questions): exact bucket 103,
  within one bucket 165. Seven misses of two buckets or more: C16, P19, P27,
  B14 (guessed some, found none), P21 (many -> rare, see CRLF), N11 (many ->
  none, see non-English), N23 (some -> everywhere).

Per class, exact / within-one agreement (`first`-mode questions excluded):
logs 14/26 of 26, code 22/26 of 27, prose 16/22 of 25, structured 13/24 of 24,
markup 14/24 of 24, nonenglish 13/23 of 25, binary 11/20 of 21.

## Per-class summaries

**Logs.** Lines are short and regular; the interesting questions are
severity words (L01, L13), timestamps and IDs (L04, L11, L12 UUIDs, L17 node
ids), and a few structured extractions (L07, L14). Match density spans six
orders of magnitude: 3 per file for 5xx responses (L06) and 0 for
`kernel panic` (L25) to 14,871 per MiB for BlueGene node ids (L17). The
hadoop and openstack files are concatenations of many per-service logs, so
density drifts down the file (L01: 6 ERROR lines in the first 4 MiB, 539 in the
whole 40 MiB).

**Code.** Definition extractors (C02, C06, C13, C14) and include/import lines
are the bulk; they are line-anchored with `(?m)`. Densities are modest
(tens to thousands per MiB) except string literals (C05, 5,800/MiB). Several
natural questions return little or nothing in these sources: Guava has no
trailing whitespace (C16, 0), doubled small words in Java comments are rare
(C19: 0 in the head, 30 in the file).

**Prose.** Word and name searches (P01, P11, P20) are dense; structure searches
(headings P09/P10, the START marker P16) are rare. The curly-quote speech
question (P03) works because these particular books use U+201C/U+201D. Moby
Dick numbers its chapters `CHAPTER 1.`, Pride and Prejudice uses roman
numerals, Monte Cristo uses `Chapter 1.` with mixed case; my first P09 guessed
roman numerals on Moby Dick and matched nothing, which is exactly the kind of
miss a user has, so the corrected pattern is the shipped one.

**Structured.** Three very different shapes: the gazetteer is a fixed-width
TSV (see surprises), the USGS CSV has quoted fields with embedded commas, and
the GeoJSON files are either 5,800 long uniform lines or ONE 13 MB line (S14-S17
exercise single-line find-all; S16 counts 547,672 coordinate pairs in it).
The XML (govinfo) has a 7 MB line as well. Key-value extraction (S12) is the
densest question in the set (42,000 matches/MiB in the sample).

**Markup.** HTML questions are dominated by tags (M02, M22: 44,700 per MiB,
essentially every other byte region), attributes (M01, M03, M06), and entities
(M07). The rst and markdown files are small, line-oriented, and anchor-heavy
(M10, M11, M14, M16).

**Non-English.** Unicode-property questions (`\p{Han}`, `\p{Cyrillic}`,
`\p{Greek}`, `\p{Hebrew}`) match at 40,000-100,000 per MiB because the scripts
are the text. The ruby-annotated Japanese (pg31617) gives bracket pairs
`《…》` (N04/N05, 37,000/MiB). Caseless Cyrillic with `(?i)` plus `\w`
boundaries (N25) is the one question that genuinely needs UCP.

**Binary.** Magic-number searches are rare (B03, B08, B19, B21: 0-14 total),
structural fields in the tar are regular and frequent (B05 `ustar\x0000` 10,005
in the 50 MB tar, one per member), and printable-string or high-byte runs are
the dense end (B10: 1.5 M in the 48 MB zip). Compressed streams give small
random counts for short patterns (B03 `\x1f\x8b\x08`: 2 hits in 1.5 MB, i.e.
chance).

## Surprising things about the data

1. **Every prose and non-English file is CRLF.** All 12 Gutenberg books and all
   29 non-English texts have a `\r` before every `\n` (checked with
   `grep -c $'\r$'`; counts equal line counts). The shape report does not say
   so. Consequence for PCRE2 at its default LF newline: `$` does not match
   before the `\r`, so `^$` finds 1 blank line in pg98 (P21) where `^\s*$`
   finds 3,388 (P26); `\w-$` finds nothing in Moby Dick (P19, and P27 with
   `\r?`), and `^CHAPTER [IVXLC]+\.$` would have missed all 57 headings
   (P10 uses `\s*$` for that reason). Any line-anchored question on these
   files needs `\r?$`, `\s*$` or `(*ANYCRLF)`, and `.` matches the `\r`.
2. **The gazetteer rows are fixed-width, space-padded to 200 bytes** (p50 =
   p90 = p99 = 200 in the shape table), so every row ends in a run of spaces
   after the longitude, and the water-area columns read `0.` not `0.000`
   (my first S04 matched nothing). Anchored-end questions again need `\s*$`.
3. **Head samples mislead on sorted or concatenated files.** Seven questions
   find 0 in the first 4 MiB and something in the file (C19, S02, M21, B15,
   B16, B19, B20); 13 more have 20x or more matches in the file than the
   sample suggests. `^TX\t` (S02) is 0 in the first 4 MiB and 1,863 in the file
   because the gazetteer is sorted by state; L01 `ERROR` is 6 vs 539. Counts
   from any prefix of these files are not representative.
4. **Two non-English files are not what their names suggest.** pg8186 and
   pg8453 (French) are 99.98% ASCII with the accents stripped, so a French
   accented-letter question (N11) matches nothing. pg20175 (Greek) is
   mojibake: Greek text stored as Latin-1-looking letters (`ìéëéÜ`, `ðñé`), so
   `\p{Greek}` finds nothing there and runs of U+00C0-U+00FF are everywhere
   (N20, 53,000/MiB).
5. **Tar members do not start a line.** The shebangs in the Django tar (9 of
   them, e.g. at byte offset 5,832,192 = 512 x 11,391) follow the previous
   member's NUL padding, so `(?m)^#!.*python` finds nothing (B14); text-style
   line anchors inside a tar mostly hit only inside member bodies.
6. **Python `re` and PCRE2 diverge on these inputs only where expected**: all
   17 py-unsupported questions are Unicode properties or `\x{..}`. Python 3.14
   handled lookbehind, backreferences, `(?=...)`, possessive-free patterns and
   the `\r` cases without error. The check is python's answer, not an oracle.
7. **The govinfo XML and the Natural Earth GeoJSON have single lines of 7 MB
   and 13 MB**, so a line-mode (`grep`) question on them returns the whole file
   as one hit and a find-all is the only sensible mode; I used find-all/count.
8. The sample preference of `first` questions: L21 (`Exception` in hadoop)
   first hits at byte 180,040; P16/P25 hit within the first kilobyte; L25 and
   B18 never hit.

## Limits of this deliverable

- Counts cover the first file listed per question; multi-file intents
  (a pattern run across the whole class) are not separately counted.
- Frequency buckets are this lane's own; they are not engine ratios.
- No question uses `\K`, `\R`, `\h`, branch-reset, atomic groups, recursion or
  callouts; they are not things these users would plausibly type for these
  files, and the brief did not require them.
- Possessive quantifiers and atomic groups are not used either, for the same
  reason; python 3.14 would have accepted them.
