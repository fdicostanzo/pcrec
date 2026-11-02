# SOUND lens: crit-stream2 (approach.md REVISION 2, §6 + §6.0 + §4.1)

Oracles: python3 `re` and the review tree's build/pcrec (worktrees/crit-stream2, main 8e846f501),
driven by a printing harness (sound/drv.c, sound/run.sh; all spans printed). 34 compiles total
(under the 50 cap). Every "expected" below is the answer BOTH oracles gave (python skipped where
it lacks the syntax, noted). "Predicted" = the answer the row produces when applied as written.

## Findings

### SOUND-1 — row 3's infallible-K test is widened in the UNSOUND direction by §6.0's polarity rule
- CONFIRMED (text applied as written); severity ANSWER; effort small (one sentence in §6.0 + row 3);
  blast radius every in-context row-3 admission; hits §6.0 "Polarity", §6.1 row 3 (and the row-12
  listing). INDUCED by the rev-2 fix of round-1 A5 (SOUND-5/PREMISE-8: "widen for SUFFICIENCY rows").
- §6.0 lists row 3 as a SUFFICIENCY row and says such rows WIDEN every zero-width item, callout and
  backref "reached in K to any byte, nullable"; row 3's own conjunct repeats it ("K nullable, with
  every zero-width item, callout and backref in K widened by polarity"). Widening to "nullable" is an
  OVER-approximation of K's language: right for row 1's FOLLOW-disjointness test, but row 3 asks
  whether K SUCCEEDS from every end, which needs an UNDER-approximation (a gate may fail). Widened, any
  K made only of gates becomes "nullable", hence "infallible", and row 3 commits S's first outcome.
- Witness 1: `a*(?=a)` on "aa". Rows 1 (FOLLOW widened, declines) and 2 (S ambiguous) decline; row 3
  sees K = `(?=a)` widened to (any byte, nullable) -> admits, commits e=2, `(?=a)` fails at 2, every
  later start likewise. Predicted NO MATCH; expected (0,1) (python, pcrec). Row 3 precedes row 12, so
  row 12's own edge witness (this same pattern) never gets the stretch.
- Witness 2: `a*?$` on "aa": K = `$` widened -> nullable -> commit the lazy first outcome e=0, `$`
  fails; starts 1 likewise; predicted (2,2), expected (0,2) (python, pcrec).
- Witness 3 (callout half): `a*(?C1)` with a callee that vetoes unless at the subject end: widened
  callout "nullable" -> commit; observed answer depends on the callee, the backtracker retries
  shorter runs. (Not compiled: --emit-main cannot bind a callee; the shape is row 7's own callout
  witness.)
- Fix: polarity is per QUESTION, not per row: over-approximate (widen) where the row tests
  disjointness/possibility (row 1 FOLLOW, row 11's one-pass), UNDER-approximate (a gate, callout or
  backref = "may fail", never nullable) where the row tests that K always succeeds (row 3, and any
  "K infallible" reading). Row 3's conjunct should read: K is ACCEPT, or K contains no zero-width
  item, callout or backref and is nullable at an unanchored end. Add `a*(?=a)` "aa" and `a*?$` "aa"
  to row 3's witnesses.

### SOUND-2 — row 2's conjunct is per BRANCH, so S with two single-end branches of different width is admitted
- CONFIRMED (text applied as written); severity ANSWER; effort small; hits §6.1 row 2; INDUCED by
  the round-1 A3 disposition wording ("every branch deterministic with one end").
- Row 2: "every branch deterministic with exactly ONE end (fixed width, or a prefix-free literal
  set, and no branch itself ambiguous)". Each branch having one end does not make S unambiguous:
  `(?:ab|a..)` has branch ends 2 and 3 on "abc...". §6.0 already defines the right test ("ambiguous"
  = more than one (e,σ) from p) but row 2 does not use it.
- Witness: `(?:ab|a..)d` on "abcd". Each branch fixed-width and deterministic; row 2 admits and
  commits the first outcome e=2; `d` fails at 2 ('c'); predicted NO MATCH; expected (0,4) (python,
  pcrec).
- Fix: row 2's first conjunct = "S is not ambiguous (§6.0) at any entry", with "fixed width or a
  prefix-free literal set" as the two sufficient tests stated for S as a WHOLE (all branches one
  width). Add the witness.

### SOUND-3 — rows 2 and 9's "K reads no slot" escape ignores the CALLER as a slot reader and never says which σ survives
- CONFIRMED as a text gap, internally inconsistent; severity ANSWER (captures); effort small;
  hits §6.1 rows 2 and 9 and §6.0 "ambiguous". NEW in rev 2 (row 9's equal-σ merge; row 2's σ case).
- Row 2: "where outcomes differ in σ, K reads no slot S writes"; row 9: "equal ends merged only with
  equal σ, or where K reads no slot". The "why" column argues "K cannot tell the outcomes apart",
  but the reported capture vector is read by the caller after ACCEPT. Taken literally, at a pattern
  end K = ACCEPT reads no slot, so row 9 may merge `(?:(a)|a)`, which its own witness column says is
  "kept apart". Nothing says the merged/committed outcome carries the PREFERRED σ.
- Witnesses: `(?:(a)|a)` on "a": expected g1=(0,1) (python, pcrec); a merge keeping branch 2's σ
  reports g1 unset. `(?:(a)|(a))b` on "ab": expected g1=(0,1), g2 unset (python, pcrec); a merged
  trie leaf may report g2=(0,1).
- Fix: replace "K reads no slot" with "the kept outcome is the first in preference order among those
  with equal end, and K reads no slot S writes" (the caller is then served by the preferred σ, and K
  cannot distinguish the dropped ones). Keep `(?:(a)|a)` as the witness of the clause.

### SOUND-4 — rows 2, 3, 8, 9 never require S regular / S's erasure record empty; a gate inside an ENUM/COMMIT body erases to a superset
- CONFIRMED as a missing conjunct (the column claims "full conjunct list (all must hold)");
  severity ANSWER if a planner reads the list as complete; effort small; hits §6.1 rows 2, 3, 8, 9.
  NEW in rev 2 (the full-conjunct-list claim is rev 2's).
- Only row 4 ("B regular") and row 12 ("body regular") say it. Row 8 admits "one greedy quantifier
  over a deterministic fixed-stride body"; `(?:a(?=a))*` is deterministic, stride 1. Rendered as
  `AUTO ENUM` the lookahead lowers to ε (NFA_ERASED_LOOK, src/ir/nfa.c:759), so ENUM yields ends
  3,2,1,0 instead of 2,1,0.
- Witness: `(?:a(?=a))*$` on "aaa": predicted (0,3) (ENUM's first end 3 satisfies `$`); expected
  (3,3) (python, pcrec). With a capture: `(?:(a)(?=a)|b)*$` "aab" expected (2,3), g1 unset.
- §4.1's typing rule (an erased stretch hands end NONE) would forbid the ENDSET row 8 must hand, so a
  careful planner declines; but that is a cross-section inference, not a conjunct. Fix: add "S
  regular (S's erasure record empty)" to rows 2, 3, 8, 9 (or one sentence above the table that every
  AUTO-rendered row requires it).

### SOUND-5 — §6.0's superset owner `Nfa.erased` does NOT record `\K`, `\G`, backrefs or calls, though §6.0 says it covers them
- CONFIRMED (grep); severity DESIGN (an answer under the typing rule if the record is read as
  written); effort medium (new record bits, or a second owner, contradicting "projection, not a new
  derivation"); hits §6.0 "The superset owner", §4.1 typing rule, rows 5 and 7. NEW in rev 2.
- §6.0: "The record covers ANYTHING that makes a stretch's (start, end) differ from the reported
  (slot0.start, slot0.end): erasures, `\K` ..., `\G`, and a callout that can veto. An IR kind the
  record does not know defaults to superset." In the review tree: src/core/kindrow.def:65-66 gives
  `A_KRESET` ERASE 0 ("`\K` moves the reported start and adds nothing to the language: exact"),
  :64 `A_GSTART` 0 (nfa.c:704 lowers it to an exact `N_GSTART`), :70 `A_BREF` 0, :73 `A_CALL` 0,
  :74 `A_VAR` 0; `NFA_ERASED_*` has exactly four bits (internal.h:2428-2434). The "unknown kind
  defaults to superset" guard never fires: these kinds are KNOWN, with erase 0. Today's exactness is
  two facts (`fit.prefilter && !erased`, emit_vm.c:3776): the backref/call/var decline lives in
  `fit.prefilter`, not the record.
- Witness: `a\Kb` on "xab": expected (2,3) (pcrec). The record over the stretch is empty, so the
  typing rule allows `AT` start = 1; a row-10 `SET` of slot0 at that AT coordinate reports (1,3).
  For G's new backref-superset machine, a stretch `(a|b)\1` would likewise read "exact" off a record
  whose `A_BREF` erase is 0.
- Fix: name the bits the end state adds (REPORT_SHIFT for `\K`, BREF_SUPERSET, CALL, VAR; `\G` is
  position-exact and can be argued out), or name `fit.prefilter`'s declines as the second input.

### SOUND-6 — the capture conjunct does not define "slots S writes" across a subroutine call (PCRE2 restores captures after a call)
- CONFIRMED as a definitional gap with a pcrec-oracle witness; severity ANSWER under one reading;
  effort small; hits §6.0 "capture conjunct" and "Forced to B" (which forces only calls with an
  AMBIGUOUS body). NEW.
- Witness: `(a)(?1)` on "aa": expected g0=(0,2), g1=(0,1) (pcrec; python has no `(?1)`; PCRE2's
  documented rule that captures set during a subroutine call revert afterwards). The call's body `a`
  is unambiguous, so "Forced to B" does not apply; if a replacement row counts the callee's `A_CAP`
  as a slot S writes, it is DERIVED (S's entry/exit) and the SET reports g1=(1,2).
- Fix: "slots S writes" excludes every slot written inside a CALL's dynamic extent (they are
  restored at RETURN); say so in §6.0, or add "a stretch containing a CALL whose callee writes a
  slot" to Forced to B.

### SOUND-7 — row 1's "by reference" text does not equal possessify.c, contrary to its status cell
- CONFIRMED (code read + `--emit-ir`); severity DOC/SPEED (text is STRICTER, no answer moves; a
  stream built from the text would lose possessifications and break the §6.3 byte-identity gate);
  effort small; hits §6.1 row 1, §6.0 polarity. Residual of round-1 A5 (NOT FULLY FIXED).
- Text: "an assertion, callout or backref reached in the follow widens it, except where an
  [ART-POSS-ARMS] arm proves otherwise". Code: (a) `$` (non-multiline) is TRANSPARENT,
  `fst_empty(true)` (src/opt/possessify.c:655-665) and `\z` likewise (CTX_PIN_END arm, :692ff.),
  by D47.5's upward-closure exemption, not an [ART-POSS-ARMS] arm; observed: `(a*)$` --engine=vm
  --emit-ir prints `possessify 1/1` (the text would decline it). (b) a subroutine call and a variable
  in the follow WIDEN (`A_CALL`, `A_VAR` -> `fst_row`, :575-576, :629), which the text omits. (c)
  `\G` widens to all bytes NON-nullable (:667-690), not "any byte, nullable" (same verdict, different
  set). (d) the lazy conjunct is stated after the EITHER (both arms) while the code places it in the
  disjointness arm only and propagates "to the end of the pattern" (:19-21); equal verdicts for
  m == n, but not the same text.
- Fix: cite D47.5's `$`/`\z` exemption and the CALL/VAR widening in row 1, or drop "the row text
  now equals the code" and say "by reference; the code is authoritative".

### SOUND-8 — row 7's "only above atomic / possessive / lookaround" and "no veto-capable callout" clauses are vacuous under its own first conjunct
- CONFIRMED (grep); severity DOC/MAINTENANCE; effort trivial; hits §6.1 row 7; NEW.
- Row 7's first conjunct requires the pattern's erasure record EMPTY; an atomic group
  (NFA_ERASED_ATOMIC, nfa.c:955; possessive quantifiers parse to atomics), a lookaround
  (NFA_ERASED_LOOK, :759) and a callout (NFA_ERASED_CALLOUT, :646) each make it non-empty. So the
  witness `(?:(?>a|ab)(c)|ab(c)?)` is declined by conjunct 1 and the new clauses never fire. Not
  unsound; it reads as if row 7 admits atomics. State which conjunct is binding, or note the clause
  is for a future record relaxation.

### SOUND-9 — row 10's trail order names only ENUM resume frames; FIND (next-start) frames are unnamed
- SUSPECTED; severity ANSWER if a FIND frame does not reset slots; effort trivial; hits §6.1 row 10,
  §4.1 `reentry`. NEW.
- Row 10: "its trail entry sits above any ENUM resume frame of the stretch before it". §4.1 has three
  pushing kinds (FIND, ENUM, CHOICE). Witness `(?:(a)b|c)` on "ac": at start 0 a seam SET writes g1
  and the stretch fails; FIND resumes at 1 and matches `c`; expected (1,2), g1 unset (python, pcrec).
  If the FIND frame neither restores the trail nor clears slots, g1=(0,1) leaks. Confirm by stating
  "above every resume frame" or that FIND's row resets the slot array per start.

### SOUND-10 — "ambiguous" is per entry p; the planner's static test, and the backref-superset of a self-referencing referent, are undefined
- SUSPECTED (design precision); severity DESIGN; effort small; hits §6.0 "Ambiguous", "backref
  superset"; NEW.
- §6.0: "S is ambiguous at p iff ...". Forced to B and row 2 use "an AMBIGUOUS S" without the
  quantifier over p; a planner needs "ambiguous at SOME p" and a decision procedure (decidable for a
  regular S via the self-product with tags; for an S holding a backref, call or recursion, it must
  default to ambiguous, which is not stated). Likewise the backref superset is "the referent's
  language" with no rule for a referent that contains the backref itself (`(a|b\1)+`) or a recursion
  (`(a(?1)?b)\1`): the language is circular or non-regular and the definition should say "widen to
  Σ*" there.

## PROBED-AND-HELD

- Row 4 (`(?>a+)a` "aa" no match) and its outer-pin clause (`(?:(?>a|ab)(c)|ab(c)?)` "abc": g1
  unset, g2=(2,3)): held, both oracles, 2 cases. Atomic-within-atomic K reasoning (inner row 3 with
  K = the atomic's end) held by hand on `(?>(a|ab)c?)d` "abd" (no match).
- Row 8 every-iteration clause `(?:(a)|b)*c` "bac" g1=(1,2); row 9 `(a|ab)*c` "aabc" g1=(1,3);
  row 10 `(?:(a)|ab)c` "abc" g1 unset; row 11's `(a*)a` "aa" g1=(0,1): 4 cases, both oracles agree.
- Row 12 edge clause, applied to EACH candidate end then K: `a*(?=a)aab` "aaab" (0,4) and
  `(?:a|b(?=c))*.` "abc" (0,3): held (2 cases, both oracles), PROVIDED S itself is taken by an ENUM
  row and row 12 replaces only the predicate (SOUND-1 is what lets row 3 pre-empt it).
- Backref superset caselessness both ways: `(a)(?i:\1)` "aA" (0,2); `(?i)(a)(?-i)\1` "AA" (0,2) (the
  referent's caseless language is already {a,A}; pcrec only, python lacks scoped (?-i)): 2 cases held.
  `(?:(a)|(a))\2?b` "ab" g2 unset: held.
- Composition paragraph: rows exact under a K-condition (1, 2, 3, 9, 12) checked by hand for
  S1·S2 both row 3, row 1 inside a row-7 pin (the pin is an end pin, upward-closed like `\z`), and row
  3 inside row 4: no break found once SOUND-1..4 hold. The paragraph's premise ("exact for EVERY
  entry") does not literally cover these rows (they are exact for S·K, not for S); a wording point,
  not a hole.
- Row 13's fire-set statement and "a COMMIT path that crosses a callout ENDS at the callout": consistent
  with NFA_ERASED_CALLOUT (nfa.c:646) and the typing rule; held by reading.
- Forced to B: backref after an ambiguous S taken by row 3 (`(a|ab)\1` "abab") is caught (S
  ambiguous at 0). Gaps found are SOUND-6 (call capture restore) only.
- Compiles: 34 (22 witnesses + 4 --emit-ir + 8 harness/failed-parse runs); no sweep.

## Summary

Rev 2's table still moves answers when applied as written: the A5 fix made §6.0's "widen" polarity
apply to row 3's INFALLIBLE-K test, the unsound direction (`a*(?=a)` "aa", `a*?$` "aa"); row 2's
per-branch wording admits `(?:ab|a..)d` "abcd"; rows 2/9's "K reads no slot" ignores the caller's σ.
Rows 2/3/8/9 lack "S regular" (`(?:a(?=a))*$`), and `Nfa.erased` does not record `\K`/\G/backref/call
as §6.0 claims. Row 1's text is stricter than possessify.c (`$`/`\z`, CALL), not equal.
