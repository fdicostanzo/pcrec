# revfloor — [OPT-REVEND] form-census floor re-derivation (2026-10-10, sonnet)

Branch `lane/revfloor`, from `lane/revtri` (cabb7840). One commit plus this report.

## The trigger

`lane/revbuild`'s `make test-axes` failed one check, `tests/codegen/run_form_census.sh`:
`population floor crossed: 'D:RX_DFA_PREFILTER=run-pinned-bounded' has 9 witnesses, floor is 12`.
On main a15fb77b the same census reads 20.

## Method

The census's own population (`grep -rhE '^pattern ' tests | LC_ALL=C sort -u`, 4,643 patterns),
each compiled at the default engine with `--features all -p rx` by two builds:
this worktree (lane/revtri tip) and `worktrees/revtri-main` (main a15fb77b, read-only, its
existing build used unmodified). Compared RX_DFA_SCAN, RX_DFA_PREFILTER, RX_ENGINE and
RX_DFA_MATCH per pattern. Old build: 20 run-pinned-bounded; new: 9 (matches the census).
Instrument: `build/rf/w.sh` in the worktree (gitignored `build/`), not committed.

## The 11 that left run-pinned-bounded

| pattern | engine | before | after (SCAN, PREFILTER) |
|---|---|---|---|
| `abc$` | dfa | unanchored, run-pinned-bounded | rev-end, none |
| `abc\z` | dfa | same | rev-end, none |
| `abc\Z` | dfa | same | rev-end, none |
| `log$` | dfa | same | rev-end, none |
| `/user$` | dfa | same | rev-end, none |
| `/user\z` | dfa | same | rev-end, none |
| `foo\b\z` | dfa | same | rev-end, none |
| `(abc)$` | vm (exact hybrid) | same | rev-end, none |
| `(ab)(c)$` | vm | same | rev-end, none |
| `(foo\|foobar)$` | vm | same | rev-end, none |
| `(log\|login\|logout)$` | vm | same | rev-end, none |

## Classification

All 11 EXPECTED: each is end-pinned (`$`, `\z`, `\Z`) and takes the rev-end locator
(RX_DFA_SCAN "rev-end", forward prefilter "none", per tuning.md §2.46 ¶4). Nothing else
moves into or out of run-pinned-bounded: the 9 that stay are lookaround/`\b` shapes
(`(?!x)abc`, `(?=a)(?=ab)abc`, `(?m)abc$` (multiline, not end-pinned), `(foo\B)`, `(foo\b)`,
`a(?*b)bc`, `a(?=b)bc`, `foo\B`, `foo\b`), none end-pinned. No finding.

Whole-population movers by (scan, prefilter) class, for context (new value `rev-end` takes
235 patterns in total): byte-class-bounded -> rev-end 52 dfa + 34 vm (+8 vm keeping the
prefilter), memchr-bounded -> rev-end 47 dfa + 33 vm (+5 vm keeping it), none -> rev-end 27+1,
offset-set-bounded -> rev-end 8+6, run-pinned-bounded -> rev-end 7 dfa + 4 vm,
first-memchr-bounded 2+1. Separately 67 `empty` patterns change RX_DFA_MATCH
`search-filter` -> `nomatch` (not a form-census floor; noted only).

## Floors set (tests/codegen/run_form_census.sh)

- `D:RX_DFA_PREFILTER=run-pinned-bounded` 12 -> 7. The file's convention is ~80-86% of the
  measured count, rounded down (14 -> 12; 117/113 -> 100). 9 * 0.8 = 7.2 -> 7. Comment added in
  the file's existing style (cause, measurement, convention).
- NEW `D:RX_DFA_SCAN=rev-end` 200 (measured 235; ~85%). The value reaches the corpus and had no
  floor row (K35: floored on first sight). Triples observed: 219 none/premultiplied, 8
  byte-class-bounded, 5 memchr-bounded, 3 none/mixed.
- `D:RX_DFA_SCAN=rev-end` added to KNOWN_VALUES so the completeness loop names it.
- Not touched: the other prefilter values the rev-end triples mention (byte-class-bounded,
  memchr-bounded) and `RX_DFA_SCAN=empty` still have no floor row; they are not rev-end values
  and predate this lane. Noted for the manager.

## Validation

`bash tests/codegen/run_form_census.sh` in this worktree (the file the suite runs): checks passed 1, checks failed 0; run-pinned-bounded = 9 (floor 7), RX_DFA_SCAN rev-end = 235 (floor 200). `make test-spec-history` after the report: 145 passed, 0 failed.
