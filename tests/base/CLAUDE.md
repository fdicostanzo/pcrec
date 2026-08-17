# tests/base — base-tier regex test corpus

Comprehensive test suite for base-tier PCRE features: literals, character classes, quantifiers, alternation, anchors, groups, and basic escapes. Every expectation is cross-verified against python3 re to ensure semantics match PCRE for this tier.

## Files

- **literals.rxt** — literal character and substring matching
- **dot.rxt** — dot (.) matching (any byte)
- **classes.rxt** — character class [...] syntax and behavior
- **class_brackets.rxt** — the MEMBER SETS of the class-bracket patterns FIX-2
  changed the verdict of (`[a[:b]`, `[[:alpha]`, `[.a]x.]`, `[a[.b]c]d.]`, the
  K4 rule-3 discriminators, both doorway-4a controls). They were guarded only by
  `accept` rows asserting exit 0 and a non-empty file — "did not say no" — and
  appeared nowhere in this corpus, so R9/C1-F4's one-line sabotage that DROPS
  the `:` from `[a[:b]`'s member set passed every suite in the repo and the
  differential fuzzer. Sabotage-validated: that edit fails 4 cases here
- **quantifiers.rxt** — *, +, ? quantifiers
- **bounded_repeats.rxt** — {m,n} repeat syntax
- **d27_forms.rxt / d27_bodies.rxt / d27_nesting.rxt / d27_edge.rxt /
  d27_captures.rxt / d27_large_counts.rxt** — the D27 blinded quantifier /
  bounded-repeat corpus (2026-08-16, cell `brepspec`): 81 blocks / 676 live
  case-lines written from the PCRE promise by an author denied `src/` and
  `tests/`, every expectation computed from python `re` and independently
  re-verified by a from-scratch checker. Covers every repeat spelling
  greedy+lazy, class/alternation/group/multi-char bodies, 2-3-level nesting
  with mixed preference, nullable-body edges, last-iteration-wins captures
  (incl. the branch-not-reset rule), 500-2000 counts and the 64-copy
  replication-cap boundary (`perr`). Two case-lines from the corpus live in
  `tests/known_fail/d27_nested_min_boundary.rxt` (K23) instead of here.
- **d27_k23_ambiguous_decomposition.rxt** — the D27 blinded corpus for the
  K23 ambiguous-decomposition region (2026-08-17, cell `d27k23`): 3 pattern
  blocks (`(a{1,3}){64,65,66}`) / 89 case-lines covering the 65..100 dense
  region, the 3N span cap, broken-run and offset-start composites. The
  region's python `re` oracle does not terminate, so expectations derive
  from a stated law (leftmost run of length L>=N matches [start,
  start+min(L,3N))) proven by exhaustive small-N induction and re-verified
  independently at review; verification ledger in
  docs/design/k23_impl/d27_corpus_notes.md. Lands WITH the [M4.6d] MRL fix.
- **alternation.rxt** — | alternation and precedence
- **alternation_trie.rxt** — priority hazards of M2.8 prefix-trie factoring (D9): shorter-branch-first shapes, overlapping-but-distinct classes, mixed eligible/ineligible runs. Each guard is sabotage-validated — disabling the disjointness guard fails 2 cases, disabling index-range partitioning fails 7
- **anchors.rxt** — ^ and $ anchors
- **eol_engine.rxt** — M2.7 regressions: `$` patterns on the O(n) unanchored engine
- **eol_scan_avoidance.rxt** — M2.12 regressions: prefilter/skip loops restored on the `$` path (D11). The original 13 patterns all failed the first M2.12 attempt, which bounded skips at n-1 but still evaluated the EOL view before the skip ran. R3.4 adds the other half of D11's interaction, which had no case at all: a forward skip state whose PLAIN accept flag is set, so `last` must survive a skip that crosses already-accepting positions. Both halves are sabotage-validated and need different patterns — restricting the EOL accept to the boundary fails 3 cases of `a.*|b$` / `a[^\n]*|\n$`, dropping the non-EOL post-skip `last = pos` fails 10 cases of `[a-z].*|q$` / `a.*|b` / `=.*|;`, and the original 13 catch NEITHER
- **groups.rxt** — (...) capturing and (?:...) non-capturing groups
- **escapes.rxt** — \\ \" \n \t metachar and control escapes
- **empty_matches.rxt** — patterns matching empty strings
- **precedence.rxt** — operator precedence and grouping
- **leftmost_semantics.rxt** — leftmost-first match semantics (greedy/lazy precedence)
- **review_r21.rxt** — K17's regressions (R21 finding E-1, fixed 2026-08-14): the empty-iteration exit redirect is not a one-shot. Six diverging family members needing all of a lazy nullable prefix, a nullable inner star and an outer `*`; one level deeper again (`(?:b*?(?:(?:a*)*)*)*`, which needs the redirect a third time); a witness the post-fix random sweep found on its own; and the four neighbours that were already correct, which are the over-reach controls for a fix that WIDENS when the redirect fires. Both oracles: 120/120 pairs python-vs-libpcre2 agree
- **k18_empty_exit_through_seen_eps.rxt** — K18's own 165 acceptance cases
  (docs/dev/known_issues.md K18, fixed 2026-08-15), moved here from
  `tests/known_fail/` in the commit that closed the entry: the
  empty-iteration redirect reached THROUGH an already-seen non-loop ε state,
  `(?:(?:a|b*?)?)*` on "ab" → [0,2) where both oracles give [0,1). 26 of the
  165 failed before the fix. **Read it with the three files below and do not
  treat it as the acceptance criterion for the class** — it was derived from
  the bug as found, so every diverging pattern in it carries a lazy nullable
  arm, and a candidate repair that passes all 165 was measured still wrong on
  83 patterns of the same severity
- **k18_arm_order.rxt** — the R23 S8 axis, 54 patterns / 667 cases: every K18
  diverging shape in BOTH alternation orders, greedy as well as lazy nullable
  arms, plus the empty-alternative (`(?:(?:(?:b|)|a)?)*`) and concatenation
  (`(?:(?:b?|a)(?:b?|d))*`) forms, which contain no lazy quantifier anywhere.
  The defect never needed laziness — it needs the arm whose EXIT edge lands on
  the already-seen ε state to be the PREFERRED one, and a greedy nullable arm
  gets that by being written FIRST. Two of the K18 entry's own "does NOT
  diverge" controls were live miscompiles with their arms swapped. Nine
  over-reach controls, including K17's repro and a pattern with no nullable
  loop at all (the closure's empty-context fast path)
- **k18_split_shapes.rxt** — 83 patterns / 609 cases, the `{0,2}`-bodied
  family where the conflation happens at a nested optional SPLIT rather than
  at an `N_EPS`. These are the cells that separate the landed repair from the
  cheap two-line alternative the design note rejected: python `re` agrees with
  the repair on 98 of 98 and with the alternative on 0
- **k18_deep_nesting.rxt** — 8 patterns / 24 cases guarding a RESOURCE class,
  not an answer: the nesting ladder to the parser's own 250-paren cap, where
  the path-sensitive closure's context count grows as d²/2, plus a lazy inner
  quantifier at that depth and forty nullable loops in SEQUENCE. The design's
  prototype descended once per context with a C stack frame (31,377 deep at
  250, an asan stack overflow at 210); the shipped `clo_walk` is iterative, and
  these blocks are what would notice if that regressed. The rest of the corpus
  tops out at loop-nesting depth 4. It is also the deliberate GROW-PATH test
  for the three tables the repair adds — 31,627 contexts against initial
  capacities of 64 and 256, so every doubling/rehash path runs, under asan too
- **k18_cost_gates.rxt** — 6 patterns / 28 cases whose point is COMPILE TIME
  rather than spans, riding the harness's own per-invocation pcrec budget
  (`pcrec_timeout_secs`, which K18's lane made axis-aware for exactly this).
  Two families, neither of them the obvious one: the fuzz-found witness that
  caught a 7x CONSTANT-FACTOR regression in the design's prototype on
  byte-identical work — a `perr` block, since every binary refuses it on the
  DFA state cap after doing the work — and bounded-repeat × nullable-loop
  swept in k, which is why the honest cost variable is the number of open-loop
  CONTEXTS and not the nesting depth a reader can see (it runs at depth 1 and
  was 231x on the broken prototype, invisible to any depth-based gate)
- **syntax_errors.rxt** — malformed patterns and diagnostic accuracy, including the K5/K6 brace miscompiles fixed 2026-08-10 (FIX-1). Two halves that must be read together: the `perr` blocks assert the rejections, and the literal-match blocks below them assert what must KEEP compiling (`a{`, `{}`, `{,}`, `a{65536x}`, …) — without those, the obvious over-reach of either fix passes every rejection. The seven K5 blocks carry `# pcre2-only` because python `re` accepts counts up to 4294967294 (U5); `tests/reject/` pins the DIAGNOSTIC for all of them, which `perr` cannot express
- **possess_lazy_guard.rxt** — the 20 D47.6 lazy-possessification guard cells (docs/dev/decisions.md D47 ruling 6): every quantifier `eng_brep_design.md`'s repaired possessification analysis declines under its lazy non-nullable-remainder conjunct, whose "20 false declines" turned out to be a probe defect, not a real cost — `probe_possess.py`'s subject alphabet omitted the prefix byte `z` these 20 patterns are built from, so it could not reach the subjects (`za{1,3}?` on "zaa", `(?:ab){3,}?` on "abababab", …) where all 20 GENUINELY diverge lazy-vs-possessive. The possessification pass now EXISTS (src/opt/possessify.c, merged 2026-08-16), so these cells are live-fire: 79 cases (span + capture-slot) pin the lazy behavior the shipped pass must preserve by declining, oracle-verified three ways (python3 `re`, libpcre2, pcrec's own build). Extended 2026-08-16 (nested-lazy lane follow-up) with the lazy-`$` family — a bare `$` follow makes the remainder nullable REGARDLESS of `(?m)`, so the lazy conjunct declines it even though the greedy twin possessifies under the D47.5 `$` exemption; discriminating subjects end in `\n` (`$` holds before a final newline, so a wrongly-possessified lazy loop swallows it), plus the greedy control pinning the exemption's own soundness on the same subjects

## Conventions

Format: `pattern <regex>` followed by `m "<subject>" START END` (match expected) or `n "<subject>"` (no match). Escapes in subjects (\" \\ \n etc) are encoded as literal backslash sequences for shell safety; driver.c decodes them. Run via `make test` or `bash tests/harness/run.sh tests/base/`.

Maintenance: update this file when .rxt files are added/removed or feature coverage changes.
