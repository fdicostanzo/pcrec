# msthink — [MATCH-SPLIT] thinking lane report (2026-10-11, opus)

Deliverable: `docs/design/match_split_requirements.md` (+ its docs/design/CLAUDE.md entry).
Design-only: no `src/` change, no build beyond single `build/pcrec` compiles on main
(outputs in the gitignored `worktrees/msthink/build/ms/`), no timing, no census. Nothing owed.

## Summary (a fresh agent resumes from here)

- Today: `^\s*\{|\}\s*$` → `RX_DFA_SCAN "attempt"`, `start_max = subject_length`, no
  prefilter: one attempt per position per call. Trim `^\s+|\s+$` is the same route and
  its `\s+$` arm walks each internal whitespace run from every position, O(k²). This
  is read from the emitted loop and not measured; survey §6.4(d) counts and confirms it.
- The general form: classes by PATH. Absolute anchors pin anywhere on a path; line
  anchors pin only at the edge; the free part is the machine with the pin edges
  deleted. It is ONE LOCATE combinator (a min over class locators, handing
  LOWER/point), and FINISH always runs the full machine.
- Every shipped single-class start row is a degenerate case: start_max=0, `\G`,
  MLINE, rev-end, end-window, end-minus-width/rev-end-width, unanchored.
  ATTEMPT-SPLIT is the START+FREE member; ENG-ABS-CARET is that member's absorb
  alternative only.
- Costing: the END reverse walk does not amortize under the stateless API. It
  repeats per find-all call and goes quadratic when the walk does not die and the
  free class matches densely. The admission reads [PRIOR-COST-UNIFY]'s
  `run_len`/`stay_len`.
- Questions for Frank: Q1 pin classes only (landmark classes held); Q2 END re-walk:
  admission predicate now vs a [FINDALL-NEXT] cache later; Q3 file the quadratic
  trim class as a K row; Q4 the general combinator with START+FREE first; Q5 a bench
  `anc-wrap` family vs a real-world idiom census as the no-free-arm trigger.

## Findings for the manager

- F1 the quadratic trim class (note §0 item 2, §8).
- F2 redundant `(?:^)?ab` and dead `x(?:^|y)z` anchors pay the full attempt loop
  today; the fact's flags alone would move them.
- The bench wishlist family `anc-wrap` is drafted in note §6.6 for the manager to
  add to `docs/dev/bench_wishlist.md`.
