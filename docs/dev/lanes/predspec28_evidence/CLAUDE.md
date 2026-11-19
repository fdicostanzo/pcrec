# docs/dev/lanes/predspec28_evidence/ — rev 28 of predicates_draft.md (the owner's 2026-11-18 evening rulings), its evidence

Lane predspec28 (2026-11-18), DESIGN EVIDENCE for the fold of nine rulings (hole-reads-capture, number-domain,
padded-width, hole-flags, flags-propagate, unset-in-hole, construction-line, value-test, same-name-twice) and the
manager's readings in those record entries. Rules nothing. Historical after merge; never edited after.
`../predspec271_evidence/` stays as committed (the helpers here are copies, not imports).

## Files

- `predspec28_model.py` — STANDALONE. PARTS PW, NW, FL, AC, UN, CN, HR, SN, DW, TT (the header names the record
  entry of each and the sabotages s1-s14). Controls: libpcre2-8 10.46 through `../rxmodel_evidence/pcre2h.py` (run,
  never read: D181), python `re`, direct semantic functions.
- `predspec28_model.out` — forward run: CHECKS 19 of 19 OK (6 are the helper's selfchecks).
- `predspec28_sabotage.out` — each of s1-s14 alone (every one CAUGHT: its run fails at least one check), then all
  at once (6 of 19: only the selfchecks stay OK).

## Run (one process; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/predspec28 && timeout 900 python3 -I -B \
        <worktree>/docs/dev/lanes/predspec28_evidence/predspec28_model.py > fwd.out)

Seconds. `PREDSPEC28_SABOTAGE=1` or `s1,..`.

## RULE-AS-CODE (consistency checks, never independent controls)

| predicate | draft sentence (rev 28) |
|---|---|
| `enum(node)` | §5.5 `enumerate` (PCRE priority order; class members in codepoint order, a LEAN; refusals). Its SETS are checked against python `re` on a brute-force pool; its ORDER is the rule |
| `status(op, kind)`, `compose(...)` | R.1.16 THE TYPE TABLE, the rows rev 28 moves (T8-T10, T13) and THE COMPOSITION RULE |
| `plus(y, k)` | R.1.16 THE NUMBER DOMAIN (RULED canonical) |
| `zfill_min`, `macro` | padded-width (RULED minimum) and the two-case macro body (the manager's reading m2) |

LIMITS: the label is predspec261's marker model; an `&` inside `quoted(...)` is spelt as a whole-stretch lookahead
(PART AC, a HAND-WORKED spelling whose answers are run); the hit lists of PART UN are PCRE2's global loop with the
hole reading the previous hit's value; the manager's 36,119-check count for the macro is NOT reproduced as a count
(his six candidate texts are not in the record): this run's own candidate set gives 47,112 checks, 0 differ.
