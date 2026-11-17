# docs/dev/lanes/predspec242b_evidence/ — rev 24.2 of predicates_draft.md, its evidence engine

Lane predspec242b (2026-11-17), DESIGN EVIDENCE: every answer revision 24.2 of `docs/design/predicates_draft.md`
states (§R) is a line of `predspec242b_model.out`. Rules nothing. Historical after merge; never edited after.

## Files

- `predspec242b_model.py` — the engine. It EXECUTES lane predspec241's engine (`../predspec241_evidence/`, never
  edited) in memory with textual patches, each asserted to hit once: P1 the pass-own candidate becomes the default
  (a loop pass has its own labels; after the pattern a looped label reads the last pass's own value); P2 that
  candidate's context restores the default; P3-P5 the switches act under rev 24's rules only; P6 THE OUTERMOST VIEW
  (nested-pass, ruled the same evening: a label two loops deep is unset by every enclosing loop's pass); P7 the
  per-test override defers to the row. PARTS: 0 the switch back and the premise (predspec241's run, patches' guards
  only, must equal its committed .out byte for byte; the pass-own candidate's 17 of 68 and V7's 8 / 33 / 33) and the
  whole of rev 24.1's evidence re-run under the rule, every changed line printed as `0 WAS` / `0 NOW` (a line of
  predspec241_model.out not listed there is printed identically under rev 24.2); S the tables the owner was shown
  (STOP RULE lines); T a run against the hits (rulings R3: the loop of conditioned times vs find-all on them); A the
  catalogue lines that move (before / after); B §R.4's old meanings, W1c's optional item restored; C rev 24.1's 38
  libpcre2 models (plain PCRE2 = the CAPTURE's reading) and C2 the HELPER-GROUP callout models of the rule (a group
  `(?<ps>)` at each pass start; a label is the pass's own when its capture starts at or after it), with the ORDER
  CHECK; L a label is not a capture (libpcre2 `\k<m>`); R the constructs rev 24.1's ramifications listed; J
  joint-last-pass dissolves; N nested-pass (the outermost view, inner views by nesting, the innermost reading as a
  record number); P the owner's black-box principle, the manager's readings (a)-(d) tested as claims; Q what the rule
  leaves undetermined and rev 24.1's other questions re-run.
- `predspec242b_model.out` — the forward run (committed).

## Run (one engine process at a time; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/predspec242b && timeout 1800 python3 -I -B \
        <worktree>/docs/dev/lanes/predspec242b_evidence/predspec242b_model.py > fwd.out)

Switches (environment): `PREDSPEC242B_SABOTAGE=1` (after the loop a label reads the FIRST pass's own value: PART S
and the helper-group checks must fail); `PREDSPEC242B_RULES=24.1` (NOW is rev 24.1's draft reading, PCRE's carry:
PART A MOVED 0; PART S prints STOP lines, the carry answers he was not shown). About 3 to 4 minutes a run. PART N
and PART T run their rule explicitly (rev 24's context), so their checks pass under the switch too; PART T's labels
are set in every pass that reads them, so the carry and the rule agree there by construction.

Verdicts (2026-11-17): forward checks 18 of 18 OK, switch BYTE-IDENTICAL; sabotage 4 of 12 OK (run before PART T was
added; PART S 0 of 5, helper-group models 6 of 16); switch: MOVED 0, shown tables 0 of 5 (each a STOP line).

LIMITS (stated): the engine has no backreference node (PART L is libpcre2 only); a label set before a loop and again
inside it (duplicate names) is run by rev 24.1's direct evaluator and a libpcre2 model with the outside group renamed.
