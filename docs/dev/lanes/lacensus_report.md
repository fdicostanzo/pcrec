# lacensus — [UCP] Q2/Q3 lookaround SHAPE census

Lane `lacensus` (sonnet), branch `lane/lacensus`, worktree
`worktrees/lacensus`, on `main` at `9399d927`. MEASUREMENT lane: nothing
under `src/`, `tests/` or `docs/spec/`. One commit, `e0b4da4a`.

## Deliverable

`docs/dev/lookaround_census.md` (the memo) +
`docs/dev/lookaround_census/` (scripts, own CLAUDE.md, classified census
TSV + report transcript, both pinned `_9399d927`). Notes added to
`docs/dev/CLAUDE.md` and the `[UCP]` row in `docs/dev/plan.md`.

## Answer

Of the **493** corpus+bench patterns that compile to the VM today with
lookaround as their ONLY DFA-excluding construct (corrected from
`ucp_study.md`'s 492 — see below):

| | n | ALL-(a) | ALL-(a)-or-(b,k≤2) |
|---|---:|---:|---:|
| all | 493 | 172 (34.9%) | 280 (56.8%) |
| corpus, excl. one adversarial test-matrix file | 187 | 92 (49.2%) | 126 (67.4%) |
| bench (the less test-biased population) | 18 | 8 (44.4%) | 10 (55.6%) |

A bounded-context DFA predicate view limited to single-character-class
lookarounds already covers a third to a half of the population; widening
to fixed-width bodies ≤2 characters covers the majority (56-67%, depending
on how one adversarial test file is weighted). Full breakdown, per-
occurrence totals, the shape-(b) k distribution, and the 10-pattern-per-
class hand-verified sample are in the memo §§0, 3, 5.

## Method notes (see memo §1 for the full account)

- **No recompile, no boxlock needed.** Reused `studies/ucp_study/
  census_13b7c202.tsv`/`census_nocap_13b7c202.tsv` (already-compiled
  engine stamps at commit `13b7c202`, 18 commits behind this lane's pin).
  Verified the gap is safe: `git diff --stat 13b7c202..9399d927 --
  tests/ examples/` touches only `tests/findings/` and one codegen check
  script ([FINDINGS] B6 / [FIND-TIE]), nothing under `tests/lookaround/`
  or `tests/utf8/`. `--list-source` calls (to re-gather full pattern text)
  are light metadata reads, not compiles.
- **Classified from RAW, untruncated pattern text**, gathered fresh by ID
  via the same population walk `studies/ucp_study/census.py` uses —
  deliberately never the census TSV's own 200-char-truncated,
  backslash-rendered `pattern` column, which is exactly the escaping/
  truncation trap `optrev_report.md` already names one instance of. This
  sidestepping is WHY the reproduction found +1 over `ucp_study.md`'s 492
  (memo §2): a 1,948-byte bench pattern whose only lookarounds sit past
  byte 200 read as an EMPTY family set under the original truncated scan
  and were silently dropped from that count.
- `shape_classify.py` is a from-scratch recursive-descent parser over the
  pattern text (not derived from pcrec's AST or `--emit-ir`'s VM listing —
  memo §4 explains why: the listing states lookbehind width directly but
  not lookahead's). Verified by a 10-pattern-per-shape hand sample (memo
  §5), all confirmed correct by inspection, plus two bugs the build itself
  caught and fixed: the FAM `capture` family regex and the shape parser's
  own group dispatch both initially mis-handled PCRE2's `(*pla:...)`-style
  alpha-verb lookaround spellings as ordinary capturing groups, falsely
  excluding/misclassifying `tests/lookaround/alpha_spellings.rxt`'s ten
  fixtures.
- **DO item 1** ("with captures / --no-captures, since captures force the
  VM on their own") is answered as a SET RELATION, not two independent
  counts: the default (captures-on) population (378) is an exact subset of
  the no-captures population (493) — the 115-pattern gap is precisely the
  patterns whose text ALSO carries a real capturing group, verified by
  reading each one's WHY string rather than assumed. The naive count from
  trusting `RX_ENGINE_WHY` alone under DEFAULT is only 12 (three orders of
  magnitude off), because under DEFAULT most VM routing is captures
  (949/1,647) and WHY names only the first excluding construct it finds.
- The corpus population is dominated by one systematically-enumerated
  adversarial D27 boundary-case file (`tests/lookaround/d27/matrix.rxt`,
  288 of 493 = 58.4%), whose own shape mix reads materially LOWER on
  shape (a) (25.0%) than the bench or the rest of the corpus (44-49%) —
  the memo reports both the blended and the file-excluded numbers rather
  than picking one, mirroring `ucp_study.md`'s own "the bench is the less
  biased number" reading.

## Validation

No `make`/suite runs applicable (nothing under `src/`/`tests/`). The
census script itself is its own validation instrument: reproduced
`ucp_study.md`'s 492 to within +1 (explained), the shape classifier's
output was hand-verified against 10 samples per class (all correct), and
both found bugs were caught by comparing the script's own output against
expectation (an unexpectedly small `default_sel`, an unexpectedly nonzero
"FAM false-positive: no real lookaround found" bucket) rather than by
inspection alone.

## Owed / open

Nothing owed. Not built or measured here (out of scope, named in the memo
§6): whether a shape-(a) occurrence's own CLASS is affordable on the DFA
today (that is [CLS-TREE]'s dependency), and throughput (open question 7
in `ucp_study.md`). Both stay open for the design pass.
