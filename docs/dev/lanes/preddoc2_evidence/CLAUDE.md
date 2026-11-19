# docs/dev/lanes/preddoc2_evidence/ — the macros-to-the-library runs

Lane preddoc2 (2026-11-19), DESIGN EVIDENCE for moving `peek`, `when` (with its test) and `rx.repeat` from the
core predicate document to the library (`docs/design/predicates/`): each body reproduces every ruled example of
the frozen draft in WHOLE, SEARCHED and FIND-ALL; the zero-values sub-pieces' examples; the manager's readings 3
and 4; the slug census. Rules nothing. Historical after merge; never edited after.

## Files

- `preddoc2_model.py` — STANDALONE, python `re` only. The BODIES as functions from regex text to regex text (hole,
  lookahead, sequence, `|`, the count-copy rule); every example RUN, compared with the draft's PRINTED answers
  (typed in by hand: the control, run by earlier lanes on libpcre2), and with a DIRECT SEMANTIC MODEL of `when`
  written from the ruled words with its own find-all loop; each example line must occur verbatim in its document.
  PARTS PE (peek), W1 W1doc WT WTdoc WD WN WC WCnot WS WV W8 (when and its test), RX RXexact RXnone RXlift RXdoc RB
  R6 (repeat), ZVpattern ZVcount ZVclass (zero values), M3 M4 (readings 3, 4; M4 reads the pilot by
  `git show 76024ee9e:...`), SL (124 slugs). The header lists sabotages s1-s17.
- `preddoc2_model.out` — forward run: 25 checks, 0 failed.
- `preddoc2_sabotage.out` — each of s1-s17 alone: 17 of 17 CAUGHT (rc 1, the named checks failing).

## Run (no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/preddoc2 && timeout 300 python3 -I -B \
        <worktree>/docs/dev/lanes/preddoc2_evidence/preddoc2_model.py)

Under a second. `PREDDOC2_SABOTAGE=s3` (one plant at a time).

## Limits

- Conditions are lowered to lookarounds on the text the label holds (`(h: <5)` with h the digit just read is
  `(?<=[0-4])`): exact for these examples only, not a general lowering of conditions.
- The warning on a bare-pattern test is a diagnostic: not runnable here (core/diagnostics/consuming-test).
- The count-copy rule is RULE-AS-CODE (as preddoc1's); its control is the draft's printed answers and python's own
  `\d{2,4}` / `\d{2}|\d{4}` / `\d+` over 63 texts.
