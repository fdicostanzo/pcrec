# docs/dev/lanes/predspec271_evidence/ — rev 27.1 of predicates_draft.md (review r48's fixes), its evidence

Lane predspec271 (2026-11-18), DESIGN EVIDENCE for the fixes of review r48 as the manager ruled them: the unset read
re-cut into four candidates, R.1.15 (5) under the draft's own reading, path order for a finite label, T1's written
order, the narrowed control inside an `occurrences` argument, hole-flags, the one number domain, the finite-lifting
fact, and the TYPE TABLE as rule-as-code over EVERY stated cell. Rules nothing. Historical after merge; never edited
after. `../predspec27_evidence/` stays as committed (the helpers here are copies, not imports).

## Files

- `predspec271_model.py` — STANDALONE. PARTS B, C, D, K, J, H, A, CL, I, TT (the header names the review finding of
  each). Controls: libpcre2-8 10.46 through `../rxmodel_evidence/pcre2h.py` (run, never read: D181), python `re`
  (PART J), direct semantic functions.
- `predspec271_model.out` — forward run: CHECKS 16 of 16 OK.
- `predspec271_sabotage.out` — all 9 sabotages at once: 8 of 16. `predspec271_sabotage_each.out` — each alone;
  every one fails exactly one check.

## Run (one process; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/predspec271 && timeout 900 python3 -I -B \
        <worktree>/docs/dev/lanes/predspec271_evidence/predspec271_model.py > fwd.out)

Seconds. `PREDSPEC271_SABOTAGE=1` or `s1,..`; the list is the script's header.

## RULE-AS-CODE (consistency checks, never independent controls)

| predicate | draft sentence (rev 27.1) |
|---|---|
| `status(op, kind)`, `compose(...)` | R.1.16 THE TYPE TABLE (every stated cell; an unstated cell is NOT-MODELLED) and its COMPOSITION RULE |
| `plus1(y)` | R.1.16 THE NUMBER DOMAIN (THE DRAFT'S READING) |

LIMITS: the label is predspec261's marker model; the image `[1-9]\d*` of PART I is a HAND-WORKED spelling whose
answers are run; the hit lists of PART B are PCRE2's global loop with the hole reading the previous hit's value.
