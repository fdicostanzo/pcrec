# tests/uprops/d27 — the D27 blinded `\p` corpus (module `unicode-props`)

Sixteen `.rxt` files, 520 blocks, 12,935 case lines, riding `make test-corpus`
like every per-module corpus, plus `d27_check.py`, the two oracles that
re-derive its expectations without pcrec (`make test-uprops` §8).

## Authorship

- **Author**: D27-blinded cell `upropd27` (`worktrees/upropd27-cell/`),
  sonnet, 2026-11-11, denied `src/` and `tests/`. Inputs: the cell's
  `docs/design/uprop_more.md`, `docs/spec/{cli,pattern_language,rxt_format}.md`,
  the `build/pcrec` binary, its own knowledge of the UCD, and python
  `unicodedata` for Bidi claims. Its record: `docs/dev/lanes/upropd27_report.md`
  (and the report of lane `upropprom`, the promotion).
- **Promoter**: lane `upropprom` (not blinded). Changes to the author's files:
  one `# pcre2-only` line before every `pattern` (python `re` has no `\p`),
  nothing else; the expectations are the author's.

## Files

- **age.rxt block.rxt bidiclass.rxt** — the Age and Block extensions and `Bidi_Class` (values, `bc=`, `Block=`/`blk=`, `NB`, refusals).
- **emoji case invisible ident cjk punct misc grapheme .rxt** — the binary properties by family; **alias.rxt** one block per `PropertyAliases.txt` short alias; **unsure_names.rxt** the names the author doubted.
- **byte.rxt spelling.rxt context.rxt** — the Latin-1 clamp, loose spellings and refusals, runs/anchors/captures/`-i` contrasts.
- **d27_check.py** — `ucd` arm: single-code-point `\p{X}` blocks vs the vendored `third_party/ucd-16.0.0/` files (PropList, DerivedCoreProperties, emoji-data, DerivedAge, Blocks, DerivedBidiClass with its `@missing` defaults, UnicodeData for Bidi_Mirrored); `pcre2` arm: every block through libpcre2 (`tests/lib/p2probe.c`). Neither runs pcrec or reads its tables.

Verified counts and findings: `docs/dev/lanes/upropprom_report.md`.
