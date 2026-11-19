# docs/dev/lanes/predspec281_evidence/ — rev 28.1 of predicates_draft.md (review r52's fixes), its evidence

Lane predspec281 (2026-11-18), DESIGN EVIDENCE for the fixes review r52 asked and the predicate manager ruled
(`docs/dev/reviews/2026-11-18-r52-predspec28.md`), and for the manager's readings of that round. Rules nothing.
Historical after merge; never edited after. `../predspec28_evidence/` stays as committed (helpers here are copies).

## Files

- `predspec281_model.py` — STANDALONE. PARTS PR, CO, PO, FF, NW (with NE), SN, DD, RC, TT, UN, PW (the header names
  the review item of each and the sabotages t1-t21). Controls: libpcre2-8 10.46 through `../rxmodel_evidence/pcre2h.py`
  (run, never read: D181), python `re`, direct semantic functions.
- `predspec281_model.out` — forward run: CHECKS 27 of 27 OK (6 are the helper's selfchecks).
- `predspec281_sabotage.out` — each of t1-t21 alone (every one CAUGHT), then all at once (6 of 27: the selfchecks).

## Run (one process; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/predspec281 && timeout 900 python3 -I -B \
        <worktree>/docs/dev/lanes/predspec281_evidence/predspec281_model.py > fwd.out)

Seconds. `PREDSPEC281_SABOTAGE=1` or `t1,..`.

## RULE-AS-CODE (consistency checks, never independent controls)

| predicate | draft sentence (rev 28.1) |
|---|---|
| `enum(rx)` | §5.5 `enumerate` (PCRE priority order; class members codepoint, the LEAN). Its ORDER is checked against libpcre2 itself (PART PR); its SETS against python `re` |
| `arith(y, op, k)` | R.1.16 THE NUMBER DOMAIN (RULED canonical; `% 0` and a negative result THE DRAFT'S READING, number-edges) |
| `per_member`, `zfill_min` | padded-width (RULED minimum); padded-order (THE DRAFT'S READING: the argument's order) |
| `lang(lit)` | same-name-twice (RULED): where the error fires |
| `fires(...)` | dollar-diagnostic (the manager's call 4: a read stands for its group's rx) |
| `CLAUSES`, `status` | T8/T9's ordered clause list (the manager's call 1); `EXPECT` is written by hand |

LIMITS: the two-case body's `&`s are reduced BY HAND for the arguments used (their SETS are checked against the
definition); an infinite argument is truncated to the subject's length (members longer than the subject cannot
match); an `&` inside a hole is spelt as a capture plus a callout that judges the stretch whole; §5.5 gives no
budget NUMBER (`BUDGET` is the model's) and states only EDGE assertions (an interior lookaround and a backreference are
refused by the model, marked NOT STATED in the output).
