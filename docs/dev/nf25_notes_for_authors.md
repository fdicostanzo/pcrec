# Notes toward a response to the authors of [NF25] — kept as we go

Frank, 2026-09-04 15:3x: "if we successfully use this paper to build an
algorithm, when you're done i'd like you to generate a doc in response —
what worked, what didn't, modifications, etc that might be of interest to
the authors. for now, keep notes." This file is the notebook. Every lane
that builds on, measures against, or departs from [NF25] (Nicol & Frohme,
"Deconstructing Subset Construction: Reducing While Determinizing",
arXiv:2505.10319, TACAS 2026 — full entry in /REFERENCES.md) APPENDS a
dated bullet here in the same change. The response document is written
from these notes when (if) the algorithm ships; nothing here is sent
anywhere until Frank rules it.

Ground rules for a bullet: what we tried, what the paper predicted, what we
measured (with the study/report/commit that holds the number), and whether
the difference is our setting (regex position automata, counted repeats,
priorities, views) or something general.

## Seed — from the reading, before any code (M5, lane m5paper, 2026-09-04;
docs/dev/dfa_online_minimization_study.md §6)

- **Setting difference the evaluation does not cover.** The paper's
  benchmarks are 52 Walnut systems and 300 random modular NFAs; no regular
  expression and no counted repetition appears. pcrec's motivating shapes
  are nested counted repeats (`((?:[^a]{1,2}|.{0,2}?)+){0,8}...`), where
  raw subset construction is ~27-33× the minimized machine
  (studies/lim2_census/: 27,575 raw → 1,010 states on
  tests/base/k18_cost_gates.rxt:66). Whether the registry's lookup answers
  for those never-created metastates on this family is the first thing we
  would measure; it is exactly the population where their construction
  would earn the most or nothing.
- **A reading that matters for size-bounding users.** §3.1's "a final
  minimization is necessary" is easy to miss from the abstract; our study
  first ranked the construction on the assumption that the on-the-fly
  result could BE the artifact (raw = emitted). It cannot, and no
  intermediate count is a lower bound on the final size either. If the
  authors have a bound on the reduced-but-not-minimal machine's size
  relative to the minimal one, that is the number a compiler with an
  emit-size cap needs.
- **Their Table 1 is a 2×2 of the shapes we had already enumerated
  independently** (SC-S = pruning each subset by a dominance preorder;
  OTF = periodic partial minimization + a generalizing registry). That the
  two decompositions coincide is a small confirmation worth telling them.
- **Registry cost.** No complexity analysis in the paper; GET is worst-case
  quadratic in lattices × minimal elements. On position automata with
  priorities (a regex engine's NFA), keys carry more structure than a plain
  NFA's; whether the similarity preorder still normalizes well is open.
- **The reference implementation's input model** (plain NFAs: no epsilon,
  no priorities, no views) means it cannot serve as an isomorphism oracle
  for a regex compiler's DFA; a port that accepts a position automaton
  with priority would be the reusable artifact.
- **Their partition rule for unexplored states** (pinned as singleton
  blocks in the intermediate Hopcroft pass) is the rule our M1 measurement
  now tests; our first draft had assumed only the closed subgraph could
  merge, which is more pessimistic than their rule.

## Notes from building (none yet)
