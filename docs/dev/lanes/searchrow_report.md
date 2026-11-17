# searchrow — the searched result row and the complement (lane report)

EXPLORATION, rules nothing. Deliverable: `docs/design/condition_kind.md` Part IV (Parts I-III kept as delivered; the
header names four parts). Evidence: `docs/dev/lanes/searchrow_evidence/` (`searchrow.py`, `searchrow.out`,
CLAUDE.md). No edit to `predicates_draft.md` (rev 22) or to any ruling.

## STATE AT HANDOFF

- Branch `lane/searchrow`, cut from main @ 94edfed66; the tip is the last commit on the branch.
- Delivered:
  - Part IV (IV.0-IV.8) of `docs/design/condition_kind.md` and its header line;
  - `searchrow_evidence/`;
  - this report and its history-index line in `docs/dev/history/claude_md/docs__dev__lanes.md`.

  `docs/design/CLAUDE.md` is unchanged (the note's role is unchanged).
- PREMISE TEST passed. Review r31's `0 7` reproduces (R22 HOLDS `7`, S FAILS). So does its `when` count: 5,060 of
  11,110 (S's body 6,050 vs rev 22's 11,110, first `9:45`). Both come from this lane's own evaluator.
- Rulings file `docs/dev/lanes/searchrow_rulings.md`: re-read before each commit and before this report. It is
  EMPTY (no R-n applied).
- Nothing built; `make` not run. Every run took about 6 seconds, under `timeout 300`, finished before 23:20 box
  clock. Nothing is left running.

OWED: none.

## THE CANDIDATES

Each candidate defines what a searched program's result rows are, and what `!B` removes (Part IV.2):
- R22 (rev 22): every filter, a complement too, is asked of the stretch; D196 retries ends.
- X (Part I's S2): every span is a row.
- S (**source-row** as worded): the complement is per subject.
- M (manager's, as briefed): PCRE's reported matches, then kept or dropped; nothing retried.
- M+ (lane's): D196 retry for conditions; a complement removes finished matches whose stretch B matches whole; no
  retry.
- Mr: M+ with EXCEPT on row identity. The 20:43 "same stretch whole" picks M+ over Mr (they part on
  `/\d+/ & !/0|00/`).

Rev 22 defines only the FIRST reported match (D196). The sequence of matches ("several result rows per subject")
is taken to be the non-overlapping leftmost find-all, as records items and `occurrences` hits already are. That
assumption is the lane's (STOP RULE), and the M candidates' `0 7` answer depends on it.

## THE TWO RULINGS UNDER EACH

All examples are SEARCHED. Each candidate's answer on `t2 & !q` at `9:30` (shown to the owner as FAILS) and on
`/\d+/ & !/0+/` at `0 7` (rev 22 and the 20:43 tie: HOLDS `7`):

| | R22 | X | S | M | M+ | Mr |
|---|---|---|---|---|---|---|
| `9:30` | HOLDS `9` | HOLDS | FAILS | FAILS | FAILS | FAILS |
| `0 7` | HOLDS `7` | HOLDS `7` | FAILS | HOLDS `7` | HOLDS `7` | HOLDS `7` |
| rev 22's worked searched examples (L34, L59, L13, §11 (i), §4.2 `9:15`; hand: L66, E-IPV4, `anchored(/foo/)`) | all | all | all | NONE (each FAILS or reports another span) | all | all |

So M, M+ and Mr satisfy both rulings, and M+ and Mr also keep every rev 22 example. No candidate keeps all three of:
- (a) `9:30` FAILS;
- (b) D196's retry;
- (c) adding a condition never admits.

M+ drops (c), M drops (b), and R22 drops (a).

Under M+, source-row's wording would be amended to this (Part IV.6):

> A searched statement gives several result rows per subject: the matches it reports, leftmost and not
> overlapping, each found as D196 finds a match. A complement on the right of `&` removes the matches whose
> stretch the complemented statement matches whole, with no retry. A complement with nothing on its left is per
> subject.

It still gives what he said yes to:
- `9:30` FAILS;
- 1,970 of 11,110 `t2` subjects, identical to per subject (0 differ);
- `0 7` HOLDS `7`.

It parts from "per subject" only on subjects with several matches: `9:30 1` HOLDS reporting `1`, on 286 of 600 pair
subjects.

## RUNS

Commands (from `$PCREC_TMPDIR/scratch/searchrow/`, W = the worktree):

    timeout 300 python3 -I W/docs/dev/lanes/searchrow_evidence/searchrow.py > fwd.out
    SEARCHROW_SWAP=1 timeout 300 python3 -I W/docs/dev/lanes/searchrow_evidence/searchrow.py > swap.out
    diff <(grep -v '^ORDER:' fwd.out) <(grep -v '^ORDER:' swap.out)   # empty
    SEARCHROW_SABOTAGE=1 forward vs SEARCHROW_SABOTAGE=1 SEARCHROW_SWAP=1: 4 differing lines (the swap check can fail)

Counts. All are SEARCHED unless they say WHOLE. All come from `searchrow.out` and are unchanged by the swap run.
- `when`, body vs case-when (T2, 11,110):
  - R22: 11,110 = 11,110 (vacuous);
  - S: 6,050 vs 11,110, differ 5,060;
  - M: 6,050 = 6,050, differ 0;
  - M+: 6,050 vs 11,110 as a retrying filter, but 0 differ against the case-when per REPORTED match;
  - WHOLE: 6,050 = 6,050.

  On T2PAIRS (600): S differs on 174, M on 0, M+ on 42 (retrying filter).
- Adding `(h: >20)` to q in `q & !(q & late)`, subjects admitted, T2 / T2PAIRS:
  - R22: 0 / 0;
  - S: 1,009 / 214;
  - M: 0 / 0;
  - M+: 1,009 / 126;
  - WHOLE: 0.
- Adding `(m = 0: <20)` at the top of `t2 & !/\d:\d\d/`: M+ admits 800 of 11,110 (`0:20`) and 90 of 600. Every other
  candidate admits 0.
- `/\d+/ & !/\d\d/` vs its positive spelling (DIG, 696): M+ differs on 90 (`00`); R22 and M on 0; S on 657.
- `/\d+/ & <17` vs D196 (DIG): M differs on 356 (`17`); every other candidate on 0.
- `/\d+/ & !/0+/` (DIG): S differs from rev 22 on 546 (`01`); M and M+ on 0.

Whole-value: every candidate shares one whole-value test. Part I's 1,970 and review r31's whole numbers reproduce,
and no count of Parts I-III moves.

## QUESTIONS FOR THE OWNER

Each wants a reply either way.
- **complement-per-match**: a complement removes matches, not subjects (the amended wording above). Leaning yes.
- **complement-retry**: the smallest choice. M+ (conditions retry, complements do not; adding a condition can admit
  in searched mode, 800 of 11,110), or M (nothing retries; D196 reversed), or R22 (everything retries; `9:30`
  HOLDS). Leaning M+.
- **nested-complement**: is a `contains`/`occurrences` argument a searched place, so that `contains(t2 & !q)` FAILS
  on `9:30` like the program? Or is it a hole, which HOLDS through `9`? Leaning searched place (rev 22 §2.6 calls
  its hits find-all hits).

## LEFT OPEN

- The find-all assumption (rev 22 defines only the first match).
- The "resume at the next start" variant of M+ was not run.
- What `|` reports when one side is a complement.
- `all` and "repeated" in searched mode.
- L66, E-IPV4 and the `anchored(/foo/)` row are hand derivations.
- Details: Part IV.8.
