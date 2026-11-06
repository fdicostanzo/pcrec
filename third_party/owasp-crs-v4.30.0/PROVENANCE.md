# owasp-crs-v4.30.0 — provenance

A pattern harvest (test/measurement data), not a vendored source file: every
regex in the OWASP Core Rule Set's rule files, extracted to one TSV. Lane
`crsharv`, 2026-11-05; Frank's ruling 2026-11-05 ("OWASP CRS as source 1" of
the real-world pattern harvest, plan row [UTF-RW]).

## Source

- Project: OWASP CRS (Core Rule Set), https://github.com/coreruleset/coreruleset
- Release: `v4.30.0`, GitHub release published 2026-10-02T21:19:43Z,
  https://github.com/coreruleset/coreruleset/releases/tag/v4.30.0
  (a stable, non-draft, non-prerelease release; the repository's "Latest")
- Annotated tag object `0e6e598a818c613cec4e13d3ecf16b19af6a002f`, peeling to
  commit **`e03a4f6dabc7a30ebd8c52c97d28a154f590a48f`** ("chore: release
  v4.30.0 (#4826)"). GitHub reports the tag's signature as verified/valid.
- Retrieved 2026-11-05: `git clone --depth 1 --branch v4.30.0` into the
  pcrec temp root; the checked-out HEAD equals the commit above. The commit was
  cross-checked three ways: `git ls-remote` (peeled tag), the GitHub tag API
  (`object.sha`), and the GitHub commits API for `v4.30.0`.
- Nothing from the download was executed; its files were read as text only.
  The download itself is NOT stored here (scratch only).

## Licence

Apache License 2.0 (`LICENSE` here is the CRS `LICENSE` file byte for byte,
sha256 prefix verified equal to the clone's). The CRS repository has no
`NOTICE` file. Each rule file's header carries the copyright lines, which
apply to this derived data:

    Copyright (c) 2006-2020 Trustwave and contributors. All rights reserved.
    Copyright (c) 2021-2026 CRS project. All rights reserved.
    The OWASP CRS is distributed under Apache Software License (ASL) version 2

Apache-2.0 section 4 (redistribution of a Derivative Work) is met by: this
LICENSE copy; the notices above retained; and the change statement below.
Changes: the regexes are reproduced verbatim (see extract.py for the one
unescaping step) and rearranged into a TSV with added columns; no pattern text
was edited.

## What derives from it

`patterns.tsv`, `summary.txt` and `gap_counts.txt` here, and the lane report
`docs/dev/lanes/crsharv_report.md`. Nothing under `src/`, `cli/`, `lib/` or
`tests/` derives from it, and nothing reaches a generated matcher. A future
consumer (the [UTF-RW] census, a bench set) must add its row here.

## Files

- `extract.py` — the recipe: `python3 -I extract.py CRS_CHECKOUT [--bench-dir D]`
  rewrites `patterns.tsv` and `summary.txt`. It is deliberately NOT named
  `generate.py`: `make gen-tables` runs every `third_party/*/generate.py`, and
  this recipe needs the downloaded checkout, which is not in the tree.
- `count_gaps.py` — `python3 -I count_gaps.py patterns.tsv build/pcrec`:
  construct counts + the pcrec `--features all` outcome (output: `gap_counts.txt`).
- `patterns.tsv` — columns: `id` (crs0001.., file order), `file`, `line` (first
  physical line of the rule), `rule_id` (chain children inherit the head's id),
  `chain_pos` (0 head, 1.. children), `operator` (`@rx`, `@rx(implicit)` for a
  bare pattern with no `@`, or `var-selector:VAR` for a regex selector such as
  `TX:/^foo_/`), `negated` (`!@rx`), `phase`, `paranoia` (from the
  `paranoia-level/N` tag of the rule head; empty if none), `transforms`
  (`t:` actions joined by `+`), `flags`, `pattern`, `libpcre2_ok`, `dup_of`
  (first id with identical pattern text).
- `summary.txt`, `gap_counts.txt` — counts, from the same run.

## Measured vs inferred

Measured: tag/commit identity; the 329 rows; that libpcre2 10.46 accepts every
one (compiled with options 0); the operator census; the pcrec outcomes.
Inferred: `flags` is `s` for every row — ModSecurity compiles `@rx` with the
dot matching newline; this is from the ModSecurity reference manual's behaviour
as remembered, not read from ModSecurity source, and pattern-embedded `(?i)`
etc. are left in the pattern text. Whether Apache config parsing would also
turn a doubled backslash inside the quoted operator into one (the extractor
keeps every backslash pair verbatim and only turns backslash-quote into a
quote) is NOT verified, but moot (no extracted pattern contains a doubled backslash); four of the five CRS rules bench copied verbatim (942140, 942160,
942270, 942500) equal this extraction byte for byte (942360 differs: bench
copied it from `main` before 4.30.0); libpcre2 accepts all rows either way.
Line continuations: the backslash-newline is dropped and the next line's
leading blanks are dropped (inferred from Apache's config reader).
