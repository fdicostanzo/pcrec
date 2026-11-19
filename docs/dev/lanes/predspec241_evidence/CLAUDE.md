# docs/dev/lanes/predspec241_evidence/ — rev 24.1 of predicates_draft.md, its evidence engine

Lane predspec241 (2026-11-17), DESIGN EVIDENCE: every answer revision 24.1 of `docs/design/predicates_draft.md`
states (§R) is a line of `predspec241_model.out`. Rules nothing. Historical after merge; never edited after.

## Files

- `predspec241_model.py` — the engine: a copy of lane predspec24's (`../predspec24_evidence/`, never edited) with the
  fixes of review r40 (`docs/dev/reviews/2026-11-17-r40-predspec24.md`), each named in the file head: FIX-A1 a loop
  body or `occurrences` argument reads the labels set so far (an optional label keeps an earlier pass's value);
  FIX-A2 a loop exports every label its item sets (the last setting overall); FIX-A3 `&` and `!B` run the right
  operand WHOLE on the stretch's own text; FIX-A5 every "(labels compared)" key carries labels in WHOLE too; FIX-C1
  the order swap is replaced by PART C's ORDER CHECK (a check that can fail). Loads lane lastpass's engine in memory
  (and through it pathimpact's path enumerator and rxmodel's libpcre2-8 harness `../rxmodel_evidence/pcre2h.py`).
  PARTS: A the catalogue (68 lines, NOW = rev 24, BEFORE = rev 23.2, PRINTED CHECK); B the ways to write the old
  meanings (23 rows + controls); C callout models on libpcre2 (38: `&`/`!B` models run the operand as its own
  pattern WHOLE on the stretch a callout extracts; defaults as PCRE conditional groups V26-V29; the place-by-operator
  grid G1-G9) + the ORDER CHECK; D properties (D12-D21: the kept sentences review r40 names); E the open items; Q
  the owner questions, every candidate run: hits-text, atomic-search, joint-last-pass, hits-committed, join-order,
  polarity-rule, exception-rule (ruled after the run's text was written; its lines stay as the record),
  pass-list-read, zero-place, pass-own-labels (the context `passown`: no carry inside a loop, after the loop the last
  pass's own value; its RAMIFICATIONS re-run PARTS A-C and direct evaluators for nested loops and a label set before
  the loop), operand-context (`AndCtx`: the operand in the subject, end tied); F whole-text legality.
- `predspec241_model.out` — the forward run (committed).

## Run (one engine process at a time; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/predspec241 && timeout 1800 python3 -I -B \
        <worktree>/docs/dev/lanes/predspec241_evidence/predspec241_model.py > fwd.out)

Switches (environment): `PREDSPEC241_SABOTAGE=1` (a bare looped label reads the FIRST pass, a loop item does not
carry earlier labels, `&` runs its right operand outer: PART C and the ORDER CHECK must fail);
`PREDSPEC241_RULES=23.2` (NOW under rev 23.2's rules: MOVED 0, printed mismatches 0). About 40 seconds a run.

LIMIT (stated, not covered): a condition inside an ATOMIC part inside a loop item that reads a label an earlier pass
set (the atomic node judges its conditions before the loop fills in the carried labels).
