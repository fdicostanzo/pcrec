# crit-stream1, lens SOUND: the §3 admission table applied AS WRITTEN

Method: each row of approach_synth.md §3 (G, 1-17, B), Pick 2 (typing rule) and Pick 3
(maximality) read literally, as a planner author (or a D27 spec-first author, hole 3) would.
Witnesses worked by hand; expected answers from python `re` 3.14 (base tier) AND today's
review-tree build (`worktrees/crit-stream1/build/pcrec --features all`, own capture-printing
driver `soundness/drv.c`, helper `soundness/run.sh`, outputs `soundness/w/`). 37 compiles,
sampled, no sweep. pcrec and python agreed on every witness except w23, where pcrec follows
its own PCRE2 rule (match_api.md §5.1¶3a) and python differs, as that paragraph says.
Notation: `pat` on "subj" -> g0..gn spans; "commit form" = the row's deterministic form
delivering one outcome.

## Findings

### SOUND-1 Rows 7 and 15 are UNSOUND with an atomic group inside S (CONFIRMED)
- Witness w11: `(?:(?>a|ab)(c)|ab(c)?)` on "abc". Expected (python = pcrec): g0=(0,3)
  g1=unset g2=(2,3). The capture-erased pattern `(?:(?>a|ab)c|abc?)` has the same span
  [0,3), so row 7 admits a pinned finish.
- Row 7 as written: "with an END pin, outcomes that cannot reach e are dead". Inside the
  atomic the body outcome `a` cannot reach e=3 (c at 1 is `b`). Killing it and moving on to
  `ab` gives branch 1 a path ending at 3: g1=(2,3), g2=unset. WRONG. The backtracker never
  tries `ab`: once `a` succeeds the atomic commits, and a failure after it kills the WHOLE
  atomic, never the next body outcome.
- Row 15 (GUIDED: "take the first branch whose successor is viable") gives the same wrong
  answer: `a`'s successor is not viable, `ab`'s is.
- Fix: rows 7, 15 (and 15') must either exclude atomic groups / possessive quantifiers /
  lookarounds with ambiguous bodies inside S, or say that the pin and viability apply only
  ABOVE an atomic (an atomic body's choice is its first body success, judged with K = the
  atomic's end, never with the pin). That turns row 15's UNVERIFIED into UNSOUND-as-written,
  and gives row 7 a conjunct it lacks.
- Severity answer; effort small (one conjunct each, plus this witness in the D27 author's
  set); blast radius every pinned finisher and the GUIDED mechanism (open choice B); §3 rows
  7, 15, §6 #3 #4.

### SOUND-2 Row 15 (GUIDED) is UNSOUND under PCRE's empty-iteration rule (CONFIRMED expected answer; mismatch worked by hand)
- Witness w23: `(?:()|a)+?b` on "ab". pcrec (match_api.md §5.1¶3a, the PCRE2 rule):
  g0=(0,2) g1=UNSET. python: g1=(0,0), which is what a plain-NFA lexicographic-first path gives.
- Hand work: from 0 the guided walk takes `()` first, because its successor is viable through
  "iterate again, then `a`, then `b`". Then exit is not viable at 0 and iterate is. It either
  produces python's (0,0) or gets stuck at an ε-revisit. PCRE's path: after an empty
  iteration no further iteration runs, `b` fails, backtrack into iteration 1, take `a`, so
  g1 stays unset.
- "The lexicographically-first accepting path" is only right over an automaton whose state
  carries "this iteration consumed nothing" (finite, so regularity holds), and the viability
  pass must be computed over that SAME automaton. The row does not say so. w24
  `(?:()|a)+b` "ab" -> g1=(1,1) (both oracles) is the greedy control.
- Severity answer; effort small in text, real in the mechanism; §3 row 15, §2 open choice B.
- pcre2-reader question (to pin PCRE2, not pcrec): "After an iteration of an unbounded
  repeated group that matched the empty string, does PCRE2's interpreter ever start a
  further iteration (including when it is the m-th mandatory iteration of X{m,}), and are
  captures set inside that empty iteration kept in the reported match?"

### SOUND-3 Row 2 ("unique end") admits stretches with more than one outcome (CONFIRMED)
- (a) "a first-byte-disjoint alternation" does not imply one end when a branch is itself
  ambiguous. w06: `(?:a|bc?)c` on "bc" -> g0=(0,2) (python = pcrec, today's DFA engine). The
  commit form takes `bc`, `c` fails, and nothing at 1 or 2 matches: NO MATCH. w31
  `(?:a|bc?)(c)` -> g1=(1,2), the same with a capture.
- (b) "fixed width" does not give one outcome once σ differs and K reads a slot. w17:
  `(?:(a)b|a(b))\2` on "abb" -> g0=(0,3) g1=unset g2=(1,2) (python = pcrec). Committing to
  the first outcome (g1 set, g2 unset) fails `\2`: NO MATCH. With conditionals (not built in
  pcrec, python only): `(?:a(b)|ab)(?(1)x|y)` "aby" -> (0,3) g1 unset, and
  `(?:(a)|a)(?(1)b|c)` "ac" -> (0,2) g1 unset.
- The "Forced to B" sentence ("a backreference ... reading a group set inside an AMBIGUOUS
  S") does not catch (b): row 2's own claim is that S is NOT ambiguous ("there is only one
  outcome"), and first match puts row 2 ahead of B. "Ambiguous" is never defined.
- Fix: row 2 = "every branch deterministic with one end (T R1(d)), and where outcomes
  differ in σ, K reads no slot S writes". Define "ambiguous" as "more than one (e, σ)
  outcome".
- Severity answer; effort small; §3 row 2 and "Forced to B".

### SOUND-4 Row G's "backref -> referent" is not a necessary condition (CONFIRMED)
- w33: `(a)(?i:\1)` on "aA" -> g0=(0,2) g1=(0,1), and on "xaA" -> (1,3) (python = pcrec).
- A gate that demands the referent's language {a} at the backref position rejects the real
  match "aA". The subject finds exactly this defect under row 17 ("Row 17 checked") but
  leaves row G, an AGREE row, stating the same substitution as sound ("it only removes
  positions that cannot match"). The typing rule's erasure list (Pick 2) also names
  "a backref replaced by its referent" as a SUPERSET, which it is not under caselessness
  (nor under MATCH_UNSET_BACKREF, where ε is needed).
- Today's code declines here (listing: `prefilter no-backreference ... neither a sound
  superset nor the true span`), so this is a regression the table would introduce.
- Fix: one definition of the backref's superset (its own caselessness, ε when unset is
  allowed, the union over duplicate names / `(?|`), used by G, row 1's first(K) (see
  SOUND-5), the typing rule and row 17 alike.
- Severity answer; effort small (text) plus a pcre2-reader note (the subject already asks
  for one under row 17; extend its question to G); §3 row G, Pick 2, row 17.

### SOUND-5 Row 1 as written is weaker than the possessify rule it cites (CONFIRMED)
Row 1 reads "`C{m,n}` and first(K) ∩ C = ∅", justified by "a shorter run leaves a byte of
C next, which K cannot start with". possessify's own header (`src/opt/possessify.c:10-47`)
records that this exact simplification is MEASURED UNSOUND, and its code carries conjuncts
the row lacks. Each one below is a witness against the row text. Today's build answers each
correctly, because possessify has the conjunct:
- LAZY: w29 `a{1,3}?` on "aaaa" -> (0,1). K = ACCEPT, so first(K) is ∅ and the row admits
  the repeat; the commit form gives (0,3). possessify.c:33-38 adds the lazy-only conjunct.
- A zero-width item in K that can succeed at a retreat and fail at the maximal exit:
  w30 `[ab]{0,4}\b` "abc" -> (0,0) (possessify.c:43-47 is this exact witness);
  w03 `\w*\B` "ab" -> (0,1); w04 `a*(?<!a)` "aa" -> (0,0); w05 `a*(?=a)` "aa" -> (0,1).
  Under the natural reading "first(K) = the bytes K can consume first", each is admitted, and
  the commit form answers no match (w30: (3,3)).
- Callouts: §1's AGREE row "callouts: ε to the analysis if non-consuming", plus G's
  "non-consuming callout -> ε", applied to row 1's first(K). The spec's own measured case
  (match_api.md §11.6¶2: `(\d+)(?C"even")` over `1234`, pcrec answers [0,3)) becomes
  PCRE2's default "no match", the auto-possess divergence pcrec's contract rejects.
- Case: w16 `(a)A*(?i:\1)` "aAA" -> (0,3). If first(\1) is taken from the referent {a}
  without the backref's caselessness, the row admits `A*` and the commit form fails.
- Root cause: the table uses "ε to the analysis" (right for NECESSARY conditions: G, 13)
  without saying that every SUFFICIENCY row (1, 2, 3-in-context, 8) must widen a zero-width
  item, callout or backref to "any byte, nullable" (possessify.c:544-590) unless an arm
  proves otherwise.
- Fix: replace row 1's text with possessify's rule by reference (U1/U2, non-nullable body,
  disjointness or exact count, the lazy conjunct, the widening arms), and state the
  ε-vs-widen polarity once, for the whole table.
- Severity answer (if built from the table text; doc as it stands, since the code is right);
  effort small; §3 row 1, rows G/13, §1 callouts row.

### SOUND-6 Rows 3/4 carry no capture conjunct, and Pick 3 makes the capture split optional (CONFIRMED by text and hand work)
- Row 3 ("K is ACCEPT ... D3's pruned machine computes exactly e₁") and row 4 deliver an END.
  The soundness rule they serve requires (e₁, σ₁). Draft T's R1 had the conjunct ("Captures
  inside a COMMIT segment are allowed where derived (§1.3). Elsewhere the region splits at
  the capture", draft_today.md §2.2). The merged table dropped it.
- Pick 3 then says that a region takes "the largest enclosing node that admits a
  deterministic row", and that any split "to put a SET inside" is a departure that must carry
  a measured price. Read together for `(a|ab)(c|bcd)(d*)` (whole pattern, K = ACCEPT):
  row 3 admits the whole pattern, maximality takes it, and the unpriced default emits one
  AUTO COMMIT with no tags. g0=(0,4) is right; g1=(0,1) g2=(1,4) g3=(4,4) (t1, python =
  pcrec) are produced by nothing. The same holds for `((a)|a)b?`: e₁ cannot say which
  branch ran, but σ₁ has g2 set.
- Fix: rows 3, 4 (and 2, 5 wherever they hand AT/SPAN) admit S only if every slot S writes
  is DERIVED (an offset of entry or exit) or produced by row 11's or open choice A's
  mechanism. Otherwise the split at the capture is FORCED (a soundness split, never a
  priced departure). Pick 3's maximality ranges over rows that admit WITH their captures,
  and over replacement rows only (G and 15' are not replacements).
- Severity answer; effort small in text; blast radius every capture pattern (hole 1's
  population); §3 rows 3/4, §2 Pick 3.

### SOUND-7 Row 16 (MEMO) is UNSOUND under subroutine calls; counters and empty-iteration guards are state too (CONFIRMED / SUSPECTED)
- CONFIRMED, w20: `^(?:(a+)x|(?1)y)$` on "aay" -> pcrec g0=(0,3) g1=unset (PCRE2-only
  syntax, no python oracle; that a subroutine call matches here is not in doubt). Branch 1
  reaches the points inside group 1's `a+` at positions 1 and 2, and they fail (no `x`).
  Branch 2's `(?1)` arrives at the SAME (point, pos) pairs with a different continuation
  (return, then `y`). A (point, pos) failure memo answers "fails again": NO MATCH. Row 16's
  exclusions (backref to a rewritten group, slot-reading callout) do not exclude CALL/RETURN.
- SUSPECTED: today's VM state beyond (point, pos). `--emit-ir` for `(?:a|ab){2,40}(c)` shows
  `counter rung, {2,40}, K=8, greedy (mandatory replicated, optional counted)`. The slots
  section names `guard` slots for nullable unbounded quantifiers. A memo keyed on
  (point, pos) without the counter value or the guard slot conflates arrivals with
  different remaining counts or different empty-iteration states. To confirm: a witness
  where the same (loop-head, pos) is reached first with a count that fails and then with
  one that succeeds, run under a prototype memo. BitState's argument holds over an UNROLLED
  program, which pcrec's counter rung is not.
- Fix: the key is (point, pos, the frame state K reads: call stack top, live counters,
  guard slots), or row 16 excludes CALL and counted rungs.
- Severity answer; effort medium; §3 row 16, §6 #4.

### SOUND-8 The typing rule's erasure list omits `\K` and the callout, yet claims to replace lmwalk g1 (CONFIRMED by text + w19)
- Pick 2's rule restricts only SUPERSET segments ("any erasure: atomic, lookaround, count,
  backref"). draft_today.md:61 records that lmwalk's g1 conjunct covers "erasure, `\G`,
  `\K`", and Pick 2 says that it replaces g1.
- `\K` erases nothing. w19 `a\Kb` on "ab" -> g0=(1,2), "xab" -> (2,3). The segment's
  language {ab} is exact, so as worded the rule lets a walk or a reverse pass emit `AT 0` /
  `SPAN(0,2)` as the match. That is wrong wherever the hand is reported rather than
  re-finished.
- A non-consuming callout treated as ε (row 13, §1) makes the segment a superset when the
  callee can veto, but the rule does not name it as an erasure. Example:
  `(?:a(?C1)b|a)` with a callee that vetoes. The pure-callee answer (§11.6¶1) is [0,1). A
  callout-ε segment hands SPAN(0,2), and a pinned finisher (row 7) then finds no outcome
  ending at 2: no match.
- `\G`, when it is not treated as an erasure, is the third member.
- Fix: the rule covers anything that makes the segment's (start, end) not the reported
  (slot0.start, slot0.end): erasures, `\K` (report shift), `\G` (offset anchor), and
  callouts that can veto. Better: list the erasure set by IR kind and default
  unknown kinds to superset ("undeclared = superset", the D182 (c) ruling-1 polarity).
- Severity answer; effort small; §2 Pick 2, §3 rows 5/6/13.

### SOUND-9 Row 8's "slots a function of the end" is ambiguous, and the useful reading is false for a conditional capture in the body (CONFIRMED)
- w09: `(?:(a)|b)*c` on "abc" -> g1=(0,1), and on "bac" -> g1=(1,2). w25 `((a)|(b))*c` "abc"
  -> g2=(0,1). Both oracles agree, and match_api.md §5.1¶2 says the same. The body is
  deterministic with fixed stride 1, so row 8 admits it. g1 is the LAST iteration in which
  the group RAN, not an offset of e.
- For a fixed subject everything is trivially "a function of the end". If the row means
  "derived as an offset of the end" (the cursor-rung reading), it must exclude captures not
  written on every iteration.
- Fix: row 8 = "every slot written in the body is written on every iteration, at a fixed
  offset". Otherwise split, or use open choice A.
- Severity answer; effort small; §3 row 8.

### SOUND-10 Row 11 (one-pass) does not say one-pass OVER WHAT (CONFIRMED)
- w10: `(a*)a` on "aa" -> g1=(0,1). S = `(a*)` by itself has one live thread per position,
  but committing it gives g1=(0,2) and then the trailing `a` fails. RE2/Go test one-pass over
  the WHOLE program. As a per-stretch row, the test must be over S·K up to the segment's
  exit commit point (or S must also pass row 1 or row 3).
- Severity answer; effort small; §3 row 11, open choice A.

### SOUND-11 Row 12 admits mid-segment folding that hole 5 says must stay a seam (CONFIRMED)
- w05: `a*(?=a)` on "aa" -> (0,1). The row's "folding it as context or a guard is the same
  test" is true only when the guard is applied to EACH candidate end in preference order.
  Applying it to the committed end gives no match. Hole 5 says so, but the row's admission
  column carries no "at a segment edge, or one-pass" conjunct, and a table-driven planner
  reads the row, not the hole.
- Severity answer; effort small; §3 row 12, §6 #5.

### SOUND-12 Row 10's "pure store" holds only for an AT-typed position and a trailed, stack-ordered SET (UNDERSPECIFIED; held by hand)
- w32: `(?:(a)|ab)c` on "abc" -> g1=UNSET. After branch 1 (g1 set) fails at `c`, ENUM
  re-entry takes `ab` without writing g1, so the SET must have been undone. That is sound
  because the contract trails slots AND the SET's trail entry sits above the ENUM resume
  frame, so it is popped before ENUM-next. w22 `(a|ab)*c` "aabc" -> g1=(1,3) holds the same
  way inside a loop.
- The row also needs `pos` to be `AT`. A SET of a group start at a seam typed `LOWER`/`CAND`
  (after a walk under row 6, or after a superset segment) has no defined value.
- With hole 10 (ENUM generator state per frame, not per segment), the SET question is
  answered: SOUND under those two conditions. Both should be written into the row.
- Severity doc; effort trivial; §3 row 10.

### SOUND-13 Rows 1/2 do not name the fold that disjointness is computed under (UNDERSPECIFIED; held today)
- w18 `\x{212a}*(?i:k)` (-e utf8) on KELVIN SIGN x2 -> g0=(0,6) bytes (python (0,2) chars),
  and w35 `\x{17f}*(?i:s)` on LONG S x2 -> (0,4) (python (0,2)). With the ASCII fold, {K, k}
  is disjoint from {U+212A} and the repeat would be committed. Under the Unicode simple fold
  it is not. Today's build is right on both.
- Fix: "disjoint on code points, under the encoding's fold at that position (`-i`, `(?i)`
  scope, --ucp Latin-1 pairs)". Hole 11 names the code-point half only.
- Severity doc; effort trivial; §3 rows 1, 2, §6 #11.

### SOUND-14 Row 14 (THREADS) and the empty-iteration rule: held by hand, but the row does not name its mechanism (UNDERSPECIFIED)
- By hand, a Pike thread list whose ε-closure drops a second arrival at the same pc and
  position gives the PCRE answers on w12 `(a*)*` "aa" -> g1=(2,2), "b" -> (0,0);
  w13 `(a|)*b` "aab" -> (2,2); w14 `(|a)*` "aa" -> (0,0); w15 `(a*)+` "aa" -> (2,2);
  w23 `(?:()|a)+?b` "ab" -> g1 UNSET (python differs). The reason: the empty iteration's
  re-entry to the loop head is exactly the dropped duplicate.
- Bounded copies are distinct pcs, so they are not deduplicated, which matches §5.1¶3a's
  "every copy of a bounded X{m,n} is not covered". The row's soundness therefore rests on
  that ε-closure rule plus a fully unrolled bounded repeat. The text says neither, and a
  counted rung (SOUND-7) breaks the second.
- Severity doc; effort small; §3 row 14. pcre2-reader question: the same as SOUND-2.

## PROBED-AND-HELD
- Row 1, single-class with today's possessify conjuncts: 11 witnesses, all answers right
  (w01 `(\w+\.)+com` x4 subjects incl. last-iteration g1, w02 `(\w+(?:-\w+)*)@(\w+)` x4,
  w03, w04, w16, w18, w29, w30, w35). The row TEXT fails (SOUND-5); the cited code holds.
- Hole-1 witnesses with captures in segments and repeats: `(\w+\.)+com`,
  `(a|ab)(c|bcd)(d*)`, `(\w+(?:-\w+)*)@(\w+)`. A tiling of row-1 islands plus seam SETs
  (row 10) inside a B loop gives the right last-iteration captures on all 9 subject cases,
  worked by hand against the oracle answers. Unset-on-later-iteration does not exist in
  PCRE (§5.1¶2, w09/w25), so no row has to clear slots.
- Row 4 (source atomic, regular body): w27 `(?>a+)a` "aa" -> nomatch (both). It holds, apart
  from captures (SOUND-6).
- Row 8: `(?:aa|a)*` is correctly not admitted (not fixed stride). The lazy order
  (w21 `(?:(a)|b)*?c`) holds for ends. Captures fail (SOUND-9).
- Row 9: `(a|ab)` and `(c|bcd)` in t1 (g1=(0,1) g2=(1,4) g3=(4,4)) and w22 hold. Equal ends
  with unequal σ (`(?:(a)|a)`) are kept apart by the row's own merge rule, but row 2 takes
  them first (SOUND-3).
- Row 10 under ENUM re-entry with trailed slots: w32, w22 (SOUND-12's conditions hold today).
- Row 17: the subject's own refutation is reproduced (w33 `(a)(?i:\1)`), and today's
  `no-backreference` decline is confirmed on 3 patterns.
- Composition across one seam, by hand. Row 1 into a row-7 pinned finisher: the pin only
  shrinks K's language, so disjointness survives. Row 3-in-context inside a pinned finisher:
  the true path goes through e₁, so the pin cannot kill it. Row 9 ENUM followed by a row-1
  commit (`(a|ab)b*c` "abbc"). General argument: a replacement that is exact for EVERY
  entry (p, σ_in) leaves the continuation function of every enclosing stretch unchanged, so
  admissions compose. The rows that are exact only under a hand (6, 7, 15) compose only if
  the hand is valid, which is the typing rule's job (SOUND-8).
- Not probed: rows 5 and 6 beyond their cited tables (the lmwalk admission and the floor,
  §6 #7 already open), and verbs (`(*ACCEPT)` etc. are not built: `requires module 'verbs'`).
  When they land they are erasures that are NOT supersets, a case the typing rule's framing
  has no slot for.

## Summary
Applied as written, 6 rows admit wrong answers: 2 (ambiguous branch; σ under a slot reader),
G (caseless backref), 7 and 15 (atomic inside S), 15 (empty iteration), 16 (subroutine
calls). Row 1 is weaker than the possessify code it cites (lazy, zero-width/callout K, case).
Rows 3/4 have no capture conjunct, and Pick 3 makes the capture split an optional priced
departure. The typing rule omits `\K` and callouts. Rows 8, 11, 12 need one conjunct each.
Rows 1 (as coded), 4, 9, 10 and composition across one seam held on 37 compiles.
