# [AUTOMATON-KIT] row body

## 2026-11-22 — Frank: the loop-in-loop rewrite belongs to the graph rewrite layer (DIRECTION)

His words: "We'd discussed a graph rewrite code piece. We'd also discussed depth rewrite where a loop in a loop can become a
single loop. If the loop rewrite is t in the graph rewrite it should be" (read as "isn't ... it should be"; phone autocorrect).

- The rewrite: a loop directly inside a loop collapses to one loop where the language allows it. Run 2026-11-21 (python `re`,
  depths 2/4/6, 3000 random subjects each, 0 span differences): the growth sweep's `(?:(?:c|b)+|b)+` nests match exactly the spans
  of `[bc]+` for the non-capturing, case-insensitive, atomic and capturing kinds; captures differ for capturing kinds (a group's
  last iteration), so those need the capture-preserving form or are excluded.
- It moves here from [SPELLING-INV], whose text lists nested quantifiers (`(a*)*`) as an example of a missed normalization;
  [SPELLING-INV] keeps the respelling CENSUS, this row owns the rewrite.
- Manager note (hand-worked, for the design step): the rewrite must act BEFORE the NFA build, because today `X+` copies its body
  once per level (2^(d+2)-2 states at depth d, lane plusprof); a rewrite on the built automaton would pay the doubling first. Two
  places the layer could act: on the pattern tree before construction (the fold), or in construction itself (a `+` built as a
  back edge rather than a body copy, which would remove the doubling for every nested `+`, reducible or not; why the body is copied
  today is for the design step to find).
