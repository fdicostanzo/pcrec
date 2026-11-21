# docs/dev/lanes/predspec243_evidence/ — rev 24.3 of predicates_draft.md, its evidence engine

Lane predspec243 (2026-11-17), DESIGN EVIDENCE: every answer revision 24.3 of `docs/design/predicates_draft.md`
states (§R) is a line of `predspec243_model.out`. Rules nothing. Historical after merge; never edited after.

## Files

- `predspec243_model.py` — the engine. It EXECUTES lane predspec242b's engine (`../predspec242b_evidence/`, never
  edited; it executes predspec241's, which loads lastpass's, pathimpact's path enumerator and rxmodel's libpcre2
  harness) in memory with textual patches, each asserted to hit once, acting under the NOW rule only (rev 24.3's;
  rev 24.1's carry and rev 23.2's rules run as before): FIX-A1 a loop iteration that matches the empty string past
  the minimum is KEPT as the last pass (pathimpact's `Rx._rep`, predspec241's `Rep` and `OccS`); FIX-A2 the pass
  forms over a label inside a literal read the OUTERMOST enclosing loop's passes, each at the outermost view
  (predspec242b's `_row_of_outer`); FIX-A4 FIND-ALL is PCRE2's global loop (after an empty match, retry at the same
  place with NOTEMPTY_ATSTART | ANCHORED, then advance), in the engine and in every libpcre2 model (the harness's
  `Pcre.findall`, predspec241's `SM`, predspec242b's `OwnRx`). PARTS: predspec242b's whole output first (its PARTS
  0-Q, unchanged in form); 0 every line of `predspec242b_model.out` that moved, WAS / NOW (none); X1 the empty pass
  (libpcre2 facts, nullable bodies vs model U, the three loop kinds agree, `occurrences` with a nullable argument);
  X2 the pass forms two loops deep (literal vs holes vs an independent direct evaluator, before and after); X3 joints
  across depths and sibling loops; X4 FIND-ALL vs PCRE2's loop (before and after); U the STRUCTURAL-UNROLLING model
  (review r42's model U: `B*` written `(?:B'*B)?`, only the last pass's copy naming the group, plain callouts), 15
  rows, and the helper-group model's two lookaround witnesses; K which constructs a filter operand's "contextual rx"
  ruling covers (`\b`, `\B`, lookbehind, lookahead, `\G`, `\K`), covered (REJECTED) vs not (the stretch), with the
  excluded subject reading; Y the "probably a mistake" error candidates, meaning vs ERROR; Z lines the text quotes
  (§2.6's `abb` example, zero-place's 738 vs 660, duplicate names and `\k<x>`); CHECKS; SUMMARY.
- `predspec243_model.out` — the forward run (committed).

## Run (one engine process at a time; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/predspec243 && timeout 1800 python3 -I -B \
        <worktree>/docs/dev/lanes/predspec243_evidence/predspec243_model.py > fwd.out)

About 2.5 minutes. `PREDSPEC243_SABOTAGE=1` switches FIX-A1, FIX-A2 and FIX-A4 off in the engine (the libpcre2
models keep PCRE2's behaviour).

Verdicts (2026-11-17): forward PART 0 0 changed lines, checks 37 of 37 OK, model U 15 of 15; sabotage checks 27 of
37 OK (FAILED: X1 NL and NL2 under NOT, the six X2 checks, X4 lazy NOT, U NL), model U 14 of 15: caught.

REACH (stated): the `occurrences` part of FIX-A1 is not reached by its checks (its nullable rows equal model U with
the fix off as on), and no line of PARTS 0-Q can move by FIX-A1 (every pool's loop body consumes a character).

LIMITS: model U assumes the unrolled pattern's path order equals the loop's (it can differ when a body has two live
choices; every row here agrees with the engine); PART K's subject model puts `\G` at the stretch's start, not
PCRE2's search start; the engine has no DEFINE or backreference node (PART Z's `\k<x>` line is libpcre2 only).
