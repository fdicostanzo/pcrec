# crsharv — OWASP CRS v4.30.0 pattern harvest (source 1 of [UTF-RW])

Lane `crsharv` (sonnet), 2026-11-05. Data commit: `315b6bd5f` (data only, its own commit). Rulings file was empty at every re-read (0 bytes).

## In plain words

1. The full OWASP Core Rule Set at its latest stable release (v4.30.0) is now in the tree as a table of **329 regexes (306 distinct)** from 301 rules, each with file, line, rule id, paranoia level and transforms. libpcre2 10.46 accepts **all 329**.
2. **None of the 306 distinct patterns uses any construct on the scoreboard gap list** (variable-width lookbehind, conditionals, `\X`, set ops, `\R`, `(*ACCEPT)`, `(*FAIL)`, `\C`, `\cX`, `\o{}`, `\N{U+}`, `(?#)`, `(?|)`, `[[:<:]]`). Not one lookbehind of any width. This confirms the sourcing plan's prediction: CRS tests "does the harvest look like the wild", not the gaps.
3. **pcrec compiles 285 of 306 with `--features all`; the 21 refusals are all size caps**, not missing features: 13 over the 1,000,000-byte emitted-C-source cap and 8 over the 500,000-byte emitted-code cap (big keyword alternations, up to 4.6 MB of C). No module refusal at all. That is a finding for the size/NFA-compaction side, not the capability side.
4. Home: `third_party/owasp-crs-v4.30.0/`, the existing shape, with **one deliberate deviation: the recipe is `extract.py`, not `generate.py`** (argued below). No code under `src/ cli/ lib/ memfn/src/ tests/` was touched.

## What was stored

`third_party/owasp-crs-v4.30.0/`: `patterns.tsv`, `PROVENANCE.md`, `LICENSE` (Apache-2.0, byte-identical to the CRS file), `extract.py`, `count_gaps.py`, `summary.txt`, `gap_counts.txt`. Index rows added in `third_party/README.md` and `CLAUDE.md`.

Provenance: tag `v4.30.0` (annotated tag object `0e6e598a...`, GitHub signature "verified: valid"), commit `e03a4f6dabc7a30ebd8c52c97d28a154f590a48f` ("chore: release v4.30.0"), published 2026-10-02, stable, the repo's "Latest". The commit was confirmed three ways (`git ls-remote` peeled tag, GitHub tag API, GitHub commits API) and the clone's HEAD equals it. The release page itself shows the tag, not a sha, so "verified against the published release" means: the release's tag resolves to this commit via the API and the tag is signature-verified.

Licence (stop rule checked): Apache-2.0, repo has no NOTICE file; the rule-file headers carry "Copyright (c) 2006-2020 Trustwave and contributors / 2021-2026 CRS project". PROVENANCE.md carries the LICENSE copy, those notices and the change statement (patterns verbatim, rearranged to TSV). Terms are clear; no stop.

## Counts (facts)

- Rows 329: 320 `@rx` operators (20 negated `!@rx`), 9 regex variable selectors (`TX:/^header_name_920450_/`, `ARGS_NAMES:/^[\w]+\[...\]$/` etc.). No implicit-`@rx` rows exist. 301 distinct rule ids (chain children inherit the head's id, `chain_pos` > 0 for 35 rows). Paranoia: PL1 185, PL2 98, PL3 31, PL4 7, none 8. 23 rows repeat an earlier pattern text (`dup_of`). 133 patterns start with `(?i`. All ASCII (no non-ASCII byte in any pattern). Length: mean 625, max 12,182 bytes.
- Not stored as patterns: 20 `.data` phrase-list files (5,796 non-comment lines; used by `@pmFromFile`, 20 uses), 6 `@pm` inline lists, and 179 `regex-assembly/*.ra` source fragments (the assembled result is what is in the `.conf` files). Other operators (`@lt @eq @ge @gt @streq @within ...`) carry no regex.
- Dedupe vs bench wild set (read-only, `bench/capability/patterns/wild-*.rx`, byte-equal match): 942140, 942160, 942270, 942500 equal bench's four CRS wild patterns; **942360 does not** (bench copied it from `main` earlier; CRS changed it); and bench's `wild-codegrammar-json-array-begin` is byte-equal to CRS 921220 (a trivial pattern, coincidence not provenance). So 5 of 32 bench patterns overlap; the other 27 are not from CRS.
- Gap constructs, over the 306 distinct patterns (lexical scan skipping escapes and classes; a sanity test of the scanner on a synthetic pattern found each construct): variable-width lookbehind 0 (no lookbehind at all), conditionals 0, `\X` 0, set ops 0, `\R` 0, `(*ACCEPT)` 0, `(*FAIL)` 0, `\C` 0, `\cX` 0, `\o{}` 0, `\N{U+}` 0, `(?#)` 0, `(?|)` 0, `[[:<:]]` 0. (A raw grep for `(?|` finds 14 hits; all are `\(\(?|` — an escaped paren, an optional paren and an alternation — false positives the scanner correctly skips.)
- pcrec `--features all`, serial, niced, default limits, 306 unique patterns: **285 compile, 21 refuse; refusal histogram: 13 "pattern too large: emitted C source over limit 1000000", 8 "pattern too large: emitted code over limit 500000", module refusals 0.** Run with the lane's own `build/pcrec` built from main `7ffbd4deb`.

## Method

1. Pinned shallow clone into `$PCREC_TMPDIR/scratch/crsharv/src/`; read as text only; nothing from it executed; `extract.py` lives outside it and ran with `python3 -I`.
2. `extract.py`: Apache-style logical lines (backslash-newline joins, next line's leading blanks dropped); `SecRule VARS "OPERATOR" "ACTIONS"` tokenised as quoted words (backslash-quote becomes a quote, every other backslash pair verbatim); the operator's `@rx` argument is the pattern; regex variable selectors (`NAME:/re/`, not XPath `XML:`) recorded as `var-selector:NAME`; `SecRuleUpdate*/Remove*` lines (55) skipped; rule id, phase, `paranoia-level/N` tag and `t:` transforms from the actions, inherited down `chain`.
3. Validation: ctypes into the installed `libpcre2-8.so.0` (10.46), `pcre2_compile_8` with options 0.
4. Reused from bench: its approach is "copy the SecRule's `@rx` text verbatim"; the extraction matches it byte-for-byte on 4 of its 5 rules (the fifth changed upstream).
5. `count_gaps.py` for constructs and pcrec outcomes.

## Home argument (third_party/ fit)

The shape fits (one dir per source, version in the name, PROVENANCE.md naming what derives from it). PREMISE TEST result: `make gen-tables` runs **every** `third_party/*/generate.py` with no argument (`Makefile:286`), and CLAUDE.md says each must support `--check` in `make test`. A `generate.py` here would either fail (it needs the download, which is not in the tree) or be a declared no-op. I chose neither: the recipe is `extract.py`, which gen-tables never sees, and PROVENANCE.md says so. The index text in `third_party/README.md` ("a data source compiles to generated tables") is about build inputs; this harvest is test/measurement data, so it has no `--check` or `GEN_TABLES` entry. The tests grep named sources only (no glob over `third_party/`), so no test is affected. If the manager prefers the declared no-op `generate.py`, it is a one-file rename plus a stub.

## Measured vs inferred

Measured: tag, commit and signature status (API); licence file and headers; all 329 rows and the libpcre2 verdicts; the operator census; the gap counts; the pcrec outcomes; byte-equality with bench's patterns.
Inferred: `flags` column is `s` for every row (ModSecurity compiles `@rx` dot-matches-newline; from memory of ModSecurity behaviour, NOT read from its source; libpcre2 acceptance does not depend on it); the line-continuation blank handling (from Apache's config reader behaviour, unread); paranoia taken from the rule head's `paranoia-level/N` tag. Not checked: whether Apache's quote handling would also collapse `\\` (moot: no extracted pattern contains a doubled backslash). The pcrec size-cap refusals are at default limits; whether they clear with a raised cap was not tried.

## STATE AT HANDOFF

Branch `lane/crsharv`: data commit `315b6bd5f`, plus this report's commit. Rulings file: no entries (0 bytes). Downloads and build output are in scratch / `build/` (gitignored). Nothing owed.
