# docs/dev/lanes/predspec291_evidence/ — rev 29.1 of predicates_draft.md (review r54's fixes), its evidence

Lane predspec291 (2026-11-19), DESIGN EVIDENCE for review r54's P29-1..P29-16 as the predicate manager ruled them,
the manager's readings 1-4 of the brief, and the owner's padded-lazy-sparse ruling (rulings file R1). Rules nothing.
Historical after merge; never edited after. The model is rev 29's `../predspec29_evidence/predspec29_model.py`
extended (that directory stays as committed).

## Files

- `predspec291_model.py` — STANDALONE. Rev 29's PARTS PO, FF, CO, NE, DD, SC, TA, TB, PL, AC, each kept, plus the r54
  checks (marked `[29.1]` in the output): PO (the CONDITION on dense and sparse lazy arguments, fill in priority and
  shortest-first order), TX (the inserted literal PARSED ALONE; drills; every rev 29 flags triple re-derived), FA (`r`,
  `aD` under UTF+UCP), SQ (sequence-operand flags), CO (`\d + (1|9)`, `enumerate(/\d/) + 1`), DD (a program parser:
  the warned form, a 13-program drill, the hint by place, the value-hole witness), SC (optional/looped `$h`), TA
  (hole-export), PL (one warning trigger), AC (a negated filter operand). Header names sabotages t1-t35. Controls:
  libpcre2-8 10.46 via `../rxmodel_evidence/pcre2h.py` (run, never read: D181), python `re`.
- `predspec291_model.out` — forward run: CHECKS 41 of 41 OK.
- `predspec291_sabotage.out` — each of t1-t35 alone: every one CAUGHT, no traceback.

## Run (one process; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/predspec291 && timeout 900 python3 -I -B \
        <worktree>/docs/dev/lanes/predspec291_evidence/predspec291_model.py > fwd.out)

A few minutes. `PREDSPEC291_SABOTAGE=t1` (one at a time).

## RULE-AS-CODE (consistency checks, never independent controls)

| predicate | draft sentence (rev 29.1) |
|---|---|
| `body(rx, n, ..)` | padded-order RULED (any-length first); `exact_first` the DROPPED rival, for the check that can fail |
| `alone(outer, inner, ..)` | the inserted literal PARSED ALONE (P29-1): own comment/`\Q` end, renamed/renumbered groups, own `(?R)`, `(?-U:(?^ims-subset:..))`; a MODEL |
| `Prs`, `dollar_sites(prog)`, `warns(prog)` | the dollar form on the PARSE (P29-11); hint only at an `&` operand (P29-12) |
| `warns_arith` | ONE trigger: a result known nothing, whatever the cause; a list only when every member's is (P29-7) |
| `sc_prog(loop, reading)` | R.1.7 (3) "a reset is a mention" vs the rival "last set" (P29-5) |
| `exports_year(kind)` | THE DRAFT'S READING of export-rule (3) for a hole vs a SEQ part (P29-13) |
| rev 29's predicates | as in `../predspec29_evidence/CLAUDE.md` |

LIMITS: the dense `\d+?` fill reference runs at length <= 5 (at 6 it is too large a PCRE pattern); fill is printed
in both orders because review r54's reference was shortest-first, not `enumerate`'s priority order; the program
parser covers only the drill's grammar (`&`, `+ -`, parens, conditions, regex with holes, strings, reads, numbers).
