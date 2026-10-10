# rev2corp report — [OPT-REVEND] stage 2 correctness corpus

Lane `rev2corp`, 2026-10-10, branch `lane/rev2corp`. Deliverable:
`tests/revend/stage2_captures.rxt` (119 blocks, 647 m/n/ms/ns cells, 645 `g`
slots = 1,292 expectation lines), its generator `gen_stage2.py` and an
independent verifier `verify_stage2.py`. No code under `src/`, `cli/`, `lib/`
changed; the corpus describes semantics main already implements.

## Oracle method

Every expectation is libpcre2 10.46's answer (`tests/fuzz/pcre2_oracle.c`
built against the box's libpcre2-8), never pcrec's. python `re` is NOT an oracle
(its `\Z` is PCRE2's `\z`), so every block is `# pcre2-only`. The oracle
compiles at options=0, so a block's `flags i`, `flags u` and `encoding utf8`
are carried into the pattern text the oracle sees as `(?i)`, `(*UCP)`,
`(*UTF)` prefixes. `gen_stage2.py` writes the file; `verify_stage2.py` then
re-reads the WRITTEN file with its own parser and re-asks the oracle for every
span and every group slot (shares no code or table with the generator).
Sabotage control: flipping one `g` slot and flipping one `n` to `m` in a copy
were each caught (1 FAIL, exit 1).

## Case families -> locate_finish.md risk

| fam | blocks (by first-letter tag; 118 of 119, one untagged) | what it stresses | risk it covers |
|---|---|---|---|
| A | 16 | `$`/`\Z` with a final newline: n vs n-1 ends, `\z` as the n-only control, group that can/cannot take the newline, lazy vs greedy newline, `(a\|a\n)$` vs `(a\n\|a)$` | the n / n-1 seed tie of the reverse walk (§4.3 "seeds only at n/n-1", §4.4); leftmost-first choosing BETWEEN ends, not shortest/longest |
| B | 10 | `(a*)ab$`, `(a+)(a?)$`, `(.+?)(\d+)$`, `(a\|ab)(c\|bcd)$`: group placement determined by the remainder | the VM finisher must place groups over the span the locator proved (window identity, E9) |
| C | 10 | groups in loops: last iteration, alternating arms keep the earlier iteration's other group, nullable group under `*`/`+` | capture retention across iterations on a verified window |
| D | 6 | optional/unset groups (-1 -1), one-of-three arms, pin in only one arm | unset slots reported correctly; unpinned top-level alternation (`(a)\|b$`, `(a$)\|(b)`) is NOT end-pinned (control) |
| E | 7 | alternation priority inside groups: prefix arm vs longer arm | priority-end vs max(D) |
| F | 5 | nested groups, nested under a loop, nested optionals | numbering and last-iteration spans of inner groups |
| G | 8 | empty matches at the end, empty at n-1 vs n, `()$`, `(\b)$` | the empty-window `[s,s]` case; leftmost start for nullable groups |
| H | 8 | `ms`/`ns`: start offsets at, inside and past the pinned tail, `\b` at the search start | search_from / start offsets near the end (FIN4 `search-from`) |
| I | 7 | the census's unbounded shapes: `(\d+)$`, `(\w+)\z`, `([^/]+)$`, `(.*)\.txt$`, `([^.]*)\.txt$`, `(\s+)$` | the population the census names (unbounded, start-unanchored) |
| J | 7 | `\b` and (negative) lookbehind at the match start, lookbehind with an anchor alternative | context before the located start (lookbehind sees bytes before `lo`) |
| K | 11 | UTF-8: multi-byte last char, 3/4-byte tails, Unicode `\s`/`\d` under UCP, start offsets on char boundaries, mixed-length loop iterations | byte-offset arithmetic at the tail; a reverse walk must not stop mid-character |
| L | 7 | caseless tails: literal, run, class, NEGATED class, `.TXT`, Kelvin sign and U+00C9 under utf8 | case folding in the reverse tables |
| M | 6 | pin inside a group, `$` in `(?:$)`, DOTALL, possessive/atomic prefix, `(?m)` and a half-pinned alternation as non-pinned controls | the end-pin predicate's edges (multiline must not take the stage-2 route) |
| N | 10 | the design note's named witnesses: LAZY tie `(\s+?){2}$` (E3, the search-from-not-verify-at hazard), `(a\z)+` and `(a+)$` (T5 unbounded), clamped widths `(\d{2,4})$`/`(a{3})$`/`(\w{1,3})\z`, `\K` | §4.3 E3, T5, the clamped-hybrid ENDSET route, X1/`\K` views |

## Verdicts (Linux dev box, main + this branch, gcc 15.2, libpcre2 10.46)

- `python3 -I tests/revend/verify_stage2.py` (oracle vs the written file):
  647 cells agree, 645 group slots agree, 0 FAIL.
- `bash tests/harness/run.sh tests/revend/stage2_captures.rxt` (pcrec,
  default engine): 1,292 passed, 0 failed.
- Same file with `RXTFLAGS=--engine=vm`: 1,292 passed, 0 failed.
- `--engine=dfa`: not admissible as is (every pattern carries captures: "pass
  --no-captures"). With `RXTFLAGS="--engine=dfa --no-captures"`: ZERO
  whole-match (m/n) expectation mismatches; the only reds are the `g` slots
  (capture-erased by construction) and the 16 cells of the three blocks that
  need the VM (the `(?<=` lookbehind block and the two `\K` blocks, refused by
  name). That DFA-axis agreement is the window-identity property stage 2 rests
  on, observed on the whole-match column.
- `make test-rxtsource` (the section that census-pins the corpus): green after
  re-pinning CENSUS_FILES 276->277, CENSUS_BLOCKS 5431->5550, CENSUS_LINES
  52073->53365, RUNSH_FILES 252->253, RUNSH_BLOCKS/LINES likewise, C3_FILES
  179->180, C3_SKIP 34695->35987 and C3_SKIP_OWNORACLE 14908->16200 (every
  block `# pcre2-only`, so C3_PASS is unchanged).
- `make test-spec-history` run after this report: see the handback message.

## Notes for the L1/L2 build

- Under the pcrec `utf8` encoding `\w` is ASCII-only unless `flags u`, and UCP
  `\w` is refused outright under utf8 ([CLS-TREE] S4); K therefore uses ASCII
  `\w` (a multi-byte letter ENDS the run) and UCP only for `\s` and `\d`.
- A `features` line REPLACES the default module set; the generator adds
  `assertions` (`\z \Z \b \K (?m)`), `lookaround` (`(?<`), `modifiers` (`(?m)`)
  and `classes` where a pattern needs them.
- Not covered, deliberately: `\G`, callouts and recursion/subroutine calls (not
  end-pin stage-2 populations), `-i` combined with `flags u` beyond the two
  cells in L, and large subjects (this is a semantics corpus, not a timing one).
- To extend: add `add(C(...))` rows to `gen_stage2.py`, regenerate, run the
  verifier and the harness, and re-pin the rxtsource census by the printed
  deltas.
