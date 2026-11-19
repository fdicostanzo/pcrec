# docs/dev/lanes/predspec29_evidence/ — rev 29 of predicates_draft.md (the owner's six 2026-11-19 rulings), its evidence

Lane predspec29 (2026-11-19), DESIGN EVIDENCE for the fold of padded-order, flags-scope, class-order,
dollar-diagnostic, number-edges and same-name-count, the manager's readings 1-16 of those record entries, and tasks
T-a (isodate), T-b (private labels), T-c (any_case body). Rules nothing. Historical after merge; never edited after.
Helpers are COPIES from `../predspec281_evidence/` (that directory stays as committed).

## Files

- `predspec29_model.py` — STANDALONE. PARTS PO, FF, CO, NE, DD, SC, TA, TB, AC (the header names the reading or task
  each feeds and the sabotages t1-t18). Controls: libpcre2-8 10.46 through `../rxmodel_evidence/pcre2h.py` (run, never
  read: D181), python `re`, direct semantic functions.
- `predspec29_model.out` — forward run: CHECKS 25 of 25 OK (6 are the helper's selfchecks).
- `predspec29_sabotage.out` — each of t1-t18 alone (every one CAUGHT, no traceback), then all at once (8 of 25).

## Run (one process; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/predspec29 && timeout 900 python3 -I -B \
        <worktree>/docs/dev/lanes/predspec29_evidence/predspec29_model.py > fwd.out)

Seconds. `PREDSPEC29_SABOTAGE=1` or `t1,..`.

## RULE-AS-CODE (consistency checks, never independent controls)

| predicate | draft sentence (rev 29) |
|---|---|
| `body(rx, n)` | padded-order RULED: the macro text, RUN in libpcre2 (each `&` a capture + callout judging the stretch whole) |
| `spell(outer, inner)` | flags-scope RULED: `i m s` inherited at a hole, `U x xx n` at their defaults; `(?^..)` / `(?-U:..)` mechanics checked by run |
| `amp_hole(.., reach)` | flags-in-filter: REACH (the manager's reading 3) against the operands' own flags |
| `by_len`, `two_class`, `quant` | class-order RULED (longest, per class position); readings 10's candidates C1-C3, P1-P3, Q1-Q2 |
| `warns(prog)` | dollar-diagnostic RULED: the warning keyed on the FORM `$x & S` |
| `visible(name, parts, inside)` | export-rule (1)-(4), label-flow (3), R.1.0's BINDING / PART LABEL rows |
| `exported(labels)` | export-rule (1): public unless `_` |

LIMITS: an infinite argument's fill reference is truncated to the subject's digits and length (HAND-WORKED; a member
with another digit or longer than the subject cannot match); an `&` in a hole is spelt as a capture plus a callout
judging the stretch whole by the other operand; the `any_case` primitive's SEARCHED / FIND-ALL order is the MODEL's
(S's members in S's order, each with its case variants; §2.7 defines a set).
