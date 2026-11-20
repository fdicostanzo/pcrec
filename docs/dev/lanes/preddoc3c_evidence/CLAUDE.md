# docs/dev/lanes/preddoc3c_evidence/ — the library conversion's runs

Lane preddoc3c (2026-11-19), DESIGN EVIDENCE for converting every `?` and skeleton piece of
`docs/design/predicates/library.md`: each body written there reproduces every ruled example of its name printed in
the frozen draft or the record, in WHOLE, SEARCHED and FIND-ALL, and every example line in library.md is this
script's own output, verbatim. Rules nothing. Historical after merge; never edited after.

## Files

- `preddoc3c_model.py` — STANDALONE, python `re` only. The BODIES as nodes (regex text, `&`, `|`, sequence, hole,
  value hole, atomic, loop) yielding ends in PCRE's priority order; examples RUN in three modes and compared with
  the PRINTED answers (typed in by hand: the control). PARTS PA PW (padded), AN (anything), AC (anchored), SW SWocc
  (startsWith / endsWith / contains), OC (occurrences), HI HIline (hits), BE (between), QU (quoted), LE (length),
  MN (month_numbered), PI (prefix_in), JO (join), LF (left), SL (strlen), LO (list_of), CP (capture), RC (rx
  classes), CA CAneg (any_case candidate body), DOC (each example line verbatim in library.md). Header lists
  sabotages s1-s21.
- `preddoc3c_model.out` — forward run: 23 checks, 0 failed, rc 0.
- `preddoc3c_sabotage.out` — each of s1-s21 alone: 21 of 21 CAUGHT (rc 1, the named checks failing).

## Run (no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/preddoc3c && timeout 600 python3 -I -B \
        <worktree>/docs/dev/lanes/preddoc3c_evidence/preddoc3c_model.py)

`PREDDOC3C_SABOTAGE=s3` (one plant at a time); `PREDDOC3C_LINES=1` prints the example lines.

## Limits

- Conditions are lowered by hand per example (a python predicate on a label's text): exact for these examples
  only, not a general lowering of conditions.
- hit-carry's witness (a condition before its group) is not run: it needs the label engine (the draft ran it on
  libpcre2).
- `records`, `file_text`, `param`, `occurs`, `each` have no subject example (`modes: n/a`); nothing here runs them.
