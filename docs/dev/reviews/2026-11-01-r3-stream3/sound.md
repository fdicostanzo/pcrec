# SOUND lens: crit-stream3 (approach.md REVISION 3, §6.0, §6.1, Forced to B, composition, §4.1 typing)

Oracles: libpcre2 10.46 via p2m.py (the oracle, D26; every "truth" below is its output), python `re`
not used where it lacks the syntax. Today's compiler: the review tree's build/pcrec (main 3f777330e),
driven by sound/run.sh + sound/drv.c (prints every slot). Compiles: 11 run-and-match + 6 `--emit-ir`
(sound/compiles.log), well under the ~40 cap. "Row computes" = the answer the row yields when every
conjunct, read literally, holds and the row's kind renders S as §6.1/§6.2 say.

## Findings

### SOUND-1: §6.0's empty-iteration rule is off by one iteration; it contradicts its own witness, the note, and today's code (K128)
- CONFIRMED (libpcre2 + today's pcrec + the note + code). Severity ANSWER (text; rows 14/15 are HELD,
  no code reads the sentence). Effort trivial (one phrase in §6.0 and row 14). Blast radius rows 14,
  15 and any AUTO that implements the rule from the text. Hits §6.0 "empty-iteration rule", §6.1
  row 14. NEW in rev 3 (the rule's wording is rev 3's, written from the A2/A13 note).
- Text: "X{m,} runs its first m iterations unconditionally; BEYOND THE MINIMUM, an iteration that
  ends where it started ends the loop". Row 14: "copies 1 to m always run; BEYOND THEM an iteration
  that ends where it started ... never loops back". Read literally, an empty m-th iteration does NOT
  end the loop, so iteration m+1 is tried. The note (§"Short answer" 1) says the opposite: "The empty
  test lives only at the repeating close of copy m, and it only decides whether iteration m+1 is
  attempted", i.e. an EMPTY m-th iteration ends the loop. Today's code says the same:
  `src/gen/emit_vm.c:6552-6570` ([K128] "THE LAST MANDATORY ITERATION IS THE LOOP'S FIRST ... if it
  consumed nothing the loop runs no iteration at all").
- Witness (the table's own): `(?:()|a)+?b` on "ab": truth (0,2), g1 UNSET. Rule as written: copy 1
  takes `()` (g1=(0,0)); lazy tries `b`, fails; iteration 2 (beyond the minimum) is tried, its `a`
  arm consumes, `b` matches: g1=(0,0). Variant with a visible second slot: `(?:()|(a))+?b` on "ab":
  truth g1 unset, g2=(0,1); rule as written g1=(0,0), g2=(0,1). Today's pcrec: `0:(0,2) 1:(-1,-1)
  2:(0,1)` (agrees with libpcre2; run.sh c1).
- Second gap in the same bullet: it covers only X{m,}. Bounded optional copies have NO empty test
  (the note's "Not checked" guess, now confirmed): `(?:()|a){1,2}?b` "ab" g1=(0,0) and
  `(?:()|a){0,2}?b` "ab" g1=(0,0), where an X{m,}-style test would give unset. Row 14's "bounded
  repeats fully unrolled" is right; §6.0 should say it.
- Fix: "iterations 1 to m always run; from iteration m on, an iteration that ends where it started
  ends the loop on that path (the test at copy m's close decides m+1); X{m,n} with n finite has no
  empty test (`(?:()|a){1,2}?b` "ab" g1=(0,0))." Same edit in row 14.

### SOUND-2: §6.0's over-approximating polarity widens a gate to ε under the DISJOINTNESS question, which is unsound for row 1's FIRST ∩ FOLLOW
- CONFIRMED (libpcre2; possessify.c contradicts the text). Severity ANSWER (text: §6.0 is "the
  definitions every row uses"; row 1 is by reference, so today's code is safe). Effort small. Blast
  radius row 1's summary, any future disjointness conjunct (row 11's one-pass is a CAN-happen test
  and is safe). Hits §6.0 Polarity bullet 1, §6.1 row 1. INDUCED by A1 (polarity per question).
- Text: a conjunct that tests "that two sets are DISJOINT (... row 1's FIRST ∩ FOLLOW ...)
  OVER-approximates: each zero-width item, non-consuming callout and backref it reaches is widened
  to its superset (ε FOR A GATE; the backref superset below)". ε is the gate's LANGUAGE superset,
  right for row G's necessity. For FOLLOW it is the wrong widening: a gate reads the bytes BEFORE the
  position (Q's own bytes), so treating it as ε makes FOLLOW pass through to the pattern end, the
  follow becomes vacuous, and the greedy arm possessifies. possessify.c:42-47: an assertion in the
  follow "widens FOLLOW to all bytes, i.e. declines"; only `$`/`\z` are transparent (D47.5).
- Witnesses (row 1's own, each confirming that ε-for-a-gate commits wrongly): `[ab]{0,4}\b` "abc"
  truth (0,0), possessive `[ab]{0,4}+\b` (3,3); `a*(?=a)` "aa" (0,1) vs `a*+(?=a)` no match;
  `\w*\B` "ab" (0,1) vs no match; `a*(?<!a)` "aa" (0,0) vs no match. A non-consuming callout widened
  to ε does the same with a vetoing callee (`(\d+)(?C"even")`, not runnable through p2m).
- Fix: in bullet 1 split the two questions: for a CAN-happen test (G, row 11) a gate is ε; for a
  FOLLOW disjointness test a gate or callout reached in the follow widens FOLLOW to ALL bytes
  (declines), except the upward-closed end anchors (D47.5) and the [ART-POSS-ARMS] arms.

### SOUND-3: row 3's infallible-K exclusion list misses CALL (and VAR, and a slot-test condition): a nullable K that reaches a gate through a call commits wrongly
- CONFIRMED (libpcre2 + today's pcrec). Severity ANSWER (text; row 3 in context is NEW). Effort
  trivial. Blast radius row 3 in context and §6.0's UNDER-approximating bullet. Hits §6.0 Polarity
  bullet 2, §6.1 row 3. NEW (r2's suggested wording, adopted, had the same three-item list).
- Text: "K is ACCEPT, or K is nullable at an unanchored pattern end and holds NO zero-width item,
  callout or backref". A subroutine call is none of the three, and K's nullability is the callee's.
- Witness: `(?:x((?=a)))?a*(?1)` on "aa": S = `a*`, K = `(?1)` (callee `(?=a)`, nullable, K holds a
  CALL only), S's record empty, S writes no slot: row 3 admits, commits e=2, `(?=a)` fails at 2, at
  every later start likewise: NO MATCH. Truth (0,1); today's pcrec (0,1) (run.sh c2). Lazy:
  `(?:x($))?a*?(?1)` "aa": row computes (2,2), truth (0,2).
- Same shape, not buildable today (conditionals unimplemented): `(x)?a*(?(1)a|)` "xaa": K is
  nullable through its `|` arm but fails when g1 is set; truth (0,3) g1=(0,1); a row 3 that does
  not count the condition as "may fail" commits a*=2, K fails, backtracking into `(x)?` skips the
  `x`, and the answer is (0,0) (SUSPECTED until the conditionals module exists: whether a condition
  is a "zero-width item" is undefined). A_VAR (kindrow.def:74, width ANY) has the same status as CALL.
- Fix: the under-approximating list = "a zero-width item, callout, backref, CALL/recursion, variable
  or condition" (the Ambiguous bullet's default list already names backref, call, recursion,
  variable; reuse it).

### SOUND-4: the regularity rule tests only `Nfa.erased`, which (by §4.1's own statement) does not carry backrefs, calls or variables today; rows 2, 3, 7, 8, 9 then admit a backref-bearing S
- CONFIRMED (code + libpcre2 + today's pcrec). Severity ANSWER (text, for the interval before G's
  BREF arm lands; row 7 is BUILT and its text is looser than its code). Effort small. Blast radius
  every AUTO-rendered row and row 7. Hits §6.0 regularity rule, §6.1 rows 2, 3, 7, 8, 9, §4.1.
  NOT FIXED (crit-stream2 SOUND-5 / A4, whose fix option 2 "name fit.prefilter's declines as the
  second input" was not taken into the rows).
- §4.1: "Today the backref, variable and call declines live in the prefilter's admission
  (`fit.prefilter`), not in the word"; the bits come "when it is built". kindrow.def:70, :73, :74:
  A_BREF, A_CALL, A_VAR all ERASE 0. The regularity rule's only test is "S's language-superset record
  EMPTY", so a backref in S passes it. Row 7's conjunct is "the language record over the pattern is
  empty"; today's code is `fit.prefilter && !cx->job->nfa.erased` (emit_vm.c:3774-3777): the
  `fit.prefilter` half appears only in a parenthetical, not as a conjunct.
- Witnesses: `(a|b)(?:\1)*` "abb": truth (0,1) g1=(0,1); pcrec (0,1) (c6). Row 3 (K = ACCEPT, S =
  `(?:\1)*` writes no slot, record empty) admits; an AUTO can render `\1` only by its superset {a,b}
  (§6.0), first outcome e=3: (0,3). Row 8 (one greedy quantifier over a fixed-stride deterministic
  body `\1`, width 1): `(a|b)(?:\1)*c` "abbac" truth (3,5) g1=(3,4) (pcrec agrees, c7); ENUM over the
  superset from start 0 yields ends 4,3,2,1 and `c` at 4 matches: (0,5).
- Fix: the regularity rule reads "record empty AND S holds no backref, call, recursion or variable
  (today: `fit.prefilter`'s declines), until their bits land"; row 7's first conjunct names both
  halves of `pcrec_vm_prefilter_window`.

### SOUND-5: no AUTO row names the report shift; today's DFA refuses `\K`, the row 3 text (BUILT) admits it
- CONFIRMED (today's compiler) that the text is looser than the code; the answer move is SUSPECTED
  (it depends on whether the card's `demands` check fires for an AUTO-internal shift). Severity
  ANSWER-if-unguarded / DESIGN. Effort trivial. Blast radius rows 2, 3, 8, 9 (AUTO), 4. Hits §6.0
  "two superset facts", §6.1 rows 2, 3, 8, 9, §4.1 fact 2. INDUCED by B1 (moving `\K` out of the
  record removed the only conjunct that declined it for the AUTO rows).
- `a\Kb` --engine=dfa: "pcrec: \K requires the VM engine, which --engine=dfa excludes" (c4). Row 3's
  status says "BUILT for whole capture-free patterns (the DFA engine)" and its conjuncts (K =
  ACCEPT, record empty, no capture) all hold for `a\Kb*`; an AUTO COMMIT that does not apply the
  shift reports (1,3) on "xab" where truth is (2,3). §4.1 places the shift on the CONSUMER's card
  ("a consumer that does not apply it declines"), but a shift INSIDE an AUTO-rendered S has no
  downstream consumer that sees it: the AUTO is the producer of the reported start. `\G` is fine
  (today's DFA takes `\Gab`, c10, rc 0 on "xab", right).
- Fix: add "no report shift inside S" to the regularity rule (or "the AUTO kind applies the shift"
  as a kind-row fact), as row 5's `g1` already does.

### SOUND-6: row 8's cited witness pins nothing; the every-iteration clause needs a subject whose LAST iteration skips the slot
- CONFIRMED (libpcre2). Severity DOC (witness quality; D27 authors will copy it). Effort trivial.
  Hits §6.1 row 8 witness column. NEW (r2 kept it as "held"; the brief's pin test is new).
- `(?:(a)|b)*c` "bac": the last iteration is `a`, so a cursor that derives g1 from the LAST
  iteration (no every-iteration clause) also reports g1=(1,2): it is right without the clause.
  The pinning subject is "abc": truth g1=(0,1) (kept from iteration 1; today's pcrec agrees, c11);
  last-iteration derivation gives (1,2) or unset.

### SOUND-7: two lists in §6.0 omit rows they bind (regularity omits row 4; the empty-iteration rule says only 14 and 15 use it)
- CONFIRMED (text + libpcre2). Severity DOC. Effort trivial. Hits §6.0. NEW.
- The regularity rule enumerates "rows 2, 3, 8, 9 and 12's body" as the AUTO rows; §6.2 renders row 4
  as `AUTO COMMIT`, and row 4's own "B regular" is not tied to the record. Witness: `(?>a*(?=a))` "aa"
  truth (0,1); an erased body's first success gives (0,2).
- "Rows 14 and 15 use it": every AUTO that computes a FIRST outcome over a nullable-body loop (rows
  3, 4, 8) must follow it too. Today's DFA does (`(?:|a)+` "a" --engine=dfa (0,0), c8, = truth);
  row 4 (NEW, possessive): `(?:|a)++b` "ab" truth (1,2), an RE2-style priority machine (ε-cycle
  pruned) gives first body success end 1 and (0,2).

### SOUND-8: "Only row G hands a superset" contradicts rows 6, 13 and 15′
- CONFIRMED (text). Severity DOC. Effort trivial. Hits §6.0 regularity rule's last sentences, §6.1
  rows 6, 13. NEW.
- Row 6: "the walk hands LOWER/CAND (the typing rule)"; row 13: "a stretch over it hands a
  superset"; row 15′ "is sound by row G". Say "only a gate-typed hand (G, and rows 6/13 through the
  typing rule) carries a superset".

### SOUND-9: row 8's "fixed-stride" admits stride 0, which today's code declines
- CONFIRMED (code). Severity MAINTENANCE (looser than code; would be ANSWER if built from the text).
  Effort trivial. Hits §6.1 row 8. NEW.
- `vm_cursor_fits` (emit_vm.c:2042-2047) declines `len <= 0`. A stride-0 body, `()*b` "b": truth
  g1=(0,0) (one empty iteration, kept, by the empty-iteration rule); an ENUM with "ends strictly
  descending" over stride 0 has one end and zero iterations, so a cursor-derived slot is unset.
  Fix: "positive fixed stride".

## PROBED-AND-HELD

- Cited witnesses vs libpcre2: all 35 cited pattern/subject pairs re-run; every cited answer holds
  (row 1's KELVIN/LONG S confirmed with real U+212A/U+017F subjects: `\x{212a}*(?i:k)` (0,6), its
  possessive no match; `\x{17f}*(?i:s)` (0,4)).
- Pins (which conjunct each witness pins, against a row WITHOUT that conjunct): G's two backref
  witnesses pin the referent's fold and the backref's fold closure (an under-stated {a} hands
  NOMATCH); `a(?=b)|c` pins no-UPPER. Row 1: `a{1,3}?` pins the lazy conjunct; the four gate
  witnesses pin the follow widening (each possessive form confirmed wrong); `(a)A*(?i:\1)` pins the
  CLOSURE (`(a)A*+(?i:\1)` "aAA" no match), but a row that widened a backref to all bytes also gets
  it right, so it pins nothing against the conservative alternative; KELVIN/LONG S pin the fold.
  Row 2: all four pin (`(?:a|bc?)c` also on "bcc" (0,3)). Row 3: both polarity witnesses pin; the
  capture witness pins "no tagless AUTO". Row 4: `(?>a+)a` pins nothing (sanity); the outer-pin
  witness pins (`(?:(?:a|ab)(c)|ab(c)?)` without the atomic gives g1=(2,3), with it g2=(2,3)). Row 7:
  its atomic witness pins nothing TODAY (conjunct 1 declines it, as E2 says); `a\Kb`/`\Ga(x)` pin the
  two-fact split. Rows 9, 10 (both trail orders), 11, 14 (`(a*)*` "aa" g1=(2,2)), 16, 17: pin as
  stated. Row 8: see SOUND-6.
- Round-2 holes re-tried with variants: SOUND-1 (polarity) closed for gates, callouts, backrefs in K
  (open for CALL: SOUND-3). SOUND-2 (row 2 per branch) closed: `(?:ab|a..)d`, `(?:a|bc?)c` "bc"/"bcc".
  SOUND-3 (σ under the caller) closed: `(?:(a)|(a))\2` "aa" truth g2=(0,1) is declined by row 2's
  slot clause and Forced to B. SOUND-4 (regularity) closed for lookaround/atomic/callout bits, open
  for backref/call/var (SOUND-4 here). SOUND-5 split closed for windows (`a\Kb`, `\Ga(x)` exact),
  induces SOUND-5 here. SOUND-6 (CALL captures) closed: `(a)(?1)` "aa" g1=(0,1), `(?:(a)|b)(?1)`
  "ba" g1 unset, and every CALL target is a capturing group, so the stopgap forces every CALL
  (conservative). SOUND-7..10 closed by text (E1, E2, row 10's "every resume frame", "at SOME
  entry" + defaults + Σ*). FIXIND-12 closed, variants: UTF `(?i:(k))\1` on two KELVIN SIGNs (0,6);
  `(k)(?i:\1)` "kK" and UTF "k"+KELVIN (0,4) (the backref's Unicode fold); `(?ir:...)` restrict
  declines both directions (no match), which "the fold in force, with caseless-restrict" covers;
  `(?|(a)|(b))\1` "bb" and the `(?J)` duplicate-name union "bb" hold.
- Empty-iteration facts other than SOUND-1: `(a|)*b`, `(a?){3,}b`, `(?:()|a)+b` g1=(1,1),
  `(?:()|a){2,}?b` g1=(0,0), possessive `(?:()|a)++b` (1,2) g1=(1,1) (the note's "worth confirming"
  case, confirmed), `(a|)+?b` "b" g1=(0,0), `()*b`/`()+b` g1=(0,0): 12 cases, all as the note says.
- Composition by hand: row 3 · row 3 (`a*b*`), row 3 inside row 4 (inner K = the atomic's end acts as
  ACCEPT), row 3 inside a loop body (K infallible, so S is never revisited), row 1 inside a row-7 pin
  (an end pin is upward-closed like `\z`), row 10 under FIND (`(?:(a)b|c)` "ac") and ENUM
  (`(?:(a)|ab)c` "abc"), G feeding 5/6/7 (G hands only LOWER/CAND/NOMATCH, each a valid input to a
  FIND): no break found beyond SOUND-3/4/5.
- §6.0 vs §4.1 typing: consistent on `UPPER` (cand_project, emit_dfa.c:13647-13651) and on the
  two-fact split; the gap is SOUND-5 (a shift inside an AUTO has no consumer) and SOUND-8 (wording).
- Cites checked in the review tree: emit_vm.c:3774-3777 (exact), :13021-13025 (the ORDERING RULE
  comment, within 2 lines), emit_dfa.c:8010-8026 (comment + `pf_vm_start_applies` at 8026),
  :8013-8019 ("A CALLOUT IS NOT A CONJUNCT"), :13647-13651, nfa.c:643-648, possessify.c:10-47: all
  hold. Today's code agrees with rows 1 (`(a*)$` possessify 1/1; `[ab]{0,4}\b` not possessified), 8
  (vm_det_seq + per-offset caps), 3 whole-pattern (`(?:|a)+` DFA (0,0)).

## Summary

Rev 3 closes round 2's holes in their original shapes, but §6.0 still has two wrong definitions. The
empty-iteration rule is off by one: an empty m-th iteration ends the loop (note, K128 at
emit_vm.c:6552), and the table's own `(?:()|a)+?b` witness refutes the text (SOUND-1). The polarity
bullet widens gates to ε for row 1's FOLLOW, which row 1's own witnesses refute (SOUND-2). Row 3's
K list misses CALL (SOUND-3). The regularity rule tests a record that has no backref/call/var bits
yet (SOUND-4, NOT FIXED SOUND-5), and nothing declines `\K` in an AUTO (SOUND-5, INDUCED by B1).
