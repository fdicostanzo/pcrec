# vlbdesign report: design note for variable-width (bounded) lookbehind

Lane vlbdesign (opus), 2026-11-05, branch `lane/vlbdesign` from main `4e35534af`. Design only:
nothing under `src/`, `cli/`, `lib/`, `memfn/src/`, `tests/` was touched. Plan row [VLOOKBEHIND].
Deliverable: `docs/design/vlookbehind.md` (PROPOSED rev 0). Evidence:
`docs/dev/lanes/vlbdesign_evidence/`. The pinned PCRE2 source copy was not opened (D181).

## For the owner, in plain words

1. **B and D are one mechanism.** Both try places where the lookbehind's text could start, farthest
   first, and at each one run the body forward and require it to end at the current position. B
   tries every place inside the width range; D asks a reverse DFA which places can work. So the
   note makes "where to try" a declared choice with two rows: the range (B) and the reverse DFA (D).
2. **D still needs B's forward run** whenever the lookbehind has captures, atomic or possessive
   parts, nested lookarounds or callouts. Measured: atomic parts shrink what the body matches
   (`(?<=(?>a|ab)b)x` is no match on `abbx`, the non-atomic form matches), so a DFA built with the
   atomicity dropped can only FILTER candidates, never answer. "DFA only" holds just for exact,
   side-effect-free bodies.
3. **D is not a second client of the landmark walk as it stands**: the walk is a search-entry
   step of the DFA artifact, with one machine per artifact, its floor at the search start (a
   lookbehind's must be the subject start) and a DFA finisher. D IS made of the walk's parts (the
   reverse NFA of a sub-pattern, the optional machine build, the reverse-scan renderer), and its
   true home is the stream plan's single reverse-walk record kind (roadmap A-REV) placed inside a
   VM body ([LANDWALK-VM]). Building it now would add a third separate reverse walk, which the
   stream ratchet forbids, for patterns where it is not expected to be faster.
4. **Recommendation:** build the range row (B) now as stage 1; the backreference width as stage 2;
   hold the reverse-DFA row (D) until A-REV gives it a home and a measurement shows the loop slow
   somewhere. Today's fixed-width lookbehinds keep their exact bytes: the general loop with one
   possible length folds to today's code by itself (no special branch).

## What the note decides

- The mechanism (§5.1): per branch, written order; candidate starts farthest first, clamped at the
  subject start (absolute); a retry frame per candidate; the end-check is load-bearing and
  backtracks into the body; atomic forms cut, non-atomic keep the frames (PCRE2's retry).
- The fixed-width fold (§5.1): natural (the retry test is a compile-time constant), applying the
  manager's 19:45 clarification; the emitted comment is the only place the one-point shape is named.
- The width rule and cap (§5.2): a range per branch; refuse unbounded and PCRE2's 255 cap on every
  branch once any varies; a new `limits.def` row.
- The negative arm (§5.3): decline for a varying branch, the `PCREC_ERR_INTERNAL` hard return kept
  for one-point branches; one predicate (`lo < hi`).
- The candidate source as a D186 choice row (§5.4): `reverse-dfa` HELD (admission conjuncts,
  evidence per regime incl. short bodies, the bench pattern, a wide body, a random-like regime;
  prerequisites A-REV, [LANDWALK-VM], [GIVEUP-DIFF]; trigger a measured slow cell), `range` the total
  fallback, shipping in stage 1.
- The second-client question (§4): answered with file:function evidence and the six
  generalizations D needs (machine per site, floor/seed as operands, names per instance, three
  exits, VM hosting, a VM finisher).
- Staging and gates (§6), ten sabotage witnesses with reach and failure reason plus six for stage 3
  (§7), S136's re-aim so the negative arm's hard return stays exercised (§7), population (§8),
  D27 recommended (§9), spec hunks (§10), the three standing questions (§11).

## Open questions for Frank (the note's §13; leanings are not rulings)

1. Today's fixed-width lookbehinds keep their exact code? Leaning yes (a natural fold, no abi event).
2. The 255 limit: default only, a setting at the interface push? Leaning yes.
3. Backreferences inside lookbehind as a second step? Leaning yes.
4. NEW: your reverse-DFA idea: build the loop now and hold D as a "where to try" choice until the
   reverse-walk unification gives it a home and a measurement asks for it? Leaning yes.

## For the critic round

Points most worth attacking: the claim that the one-point fold is byte-identical (only stage 1's
identity gate proves it); the UTF-8 clamp's spelling (left to the build lane, §5.1); the exactness
reading `Nfa.erased == 0` as sufficient for D's existence exit (callouts, `\b` views at the floor);
the S136 re-aim cells; whether stage 1 owes an abi bump (§14, read against `match_api.md` §6¶19).

## Measured vs inferred

- MEASURED (dev box, libpcre2 10.46 as a library, `oracle_probe.c` from vlbinv and `startpos.c`):
  `d_match.out`, `d_utf.out`, `w_match.out` (including the S136 re-aim cells), `startpos.out`;
  premise (`premise.txt`: `(?<=a|bc)x` compiles, `(?<=a{1,3})b` refused, `build/pcrec --features all`
  at `4e35534af`).
- MEASURED PROXY: `revdfa_sizes.tsv`, reverse-machine sizes read from pcrec artifacts of patterns
  equal to the body (`cnt.py`).
- READ from code: §4's evidence (`emit_landmark_walk`, `lmwalk_build`, `revend_build_one`,
  `emit_reverse_block`, `struct DfaDir`, `VmKind`, `Nfa.erased`, `vm_look_behind_branch`, S136).
- INFERRED: speed comparisons (no timing run), the fold's byte identity, the work bound.

## STATE AT HANDOFF

STATE: delivered. Commits on `lane/vlbdesign`: WIP evidence, the note + plan status + design
CLAUDE.md line, this report. Rulings file `vlbdesign_rulings.md`: one entry (2026-11-05 19:45,
manager clarification on question 1), applied in §5.1 and §13 q1. `plan_lint.sh`: 298 rows, 0
violations. No build beyond the one `make -j4` for the premise; no heavy run; nothing owed. No
DELIVER block existed for this lane (`docs/dev/lanes/vlbdesign_deliver.txt` absent), so
`scripts/lanecheck` was not run. No S-ids or D-ids were taken (proposed "D-next" not needed: the
note records a design, the decision entry is the manager's at ruling time).
