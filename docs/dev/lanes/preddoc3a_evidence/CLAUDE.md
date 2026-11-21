# docs/dev/lanes/preddoc3a_evidence/ — the core part A conversion runs

Lane preddoc3a (2026-11-19), DESIGN EVIDENCE for converting the core sections `core/model`, `core/patterns`,
`core/labels`, `core/conditions`, `core/filters` of `docs/design/predicates/core.md`: every example line of those
sections RUN in WHOLE, SEARCHED and FIND-ALL; the manager's readings 1-3; the slug census. Rules nothing.
Historical after merge; never edited after.

## Files

- `preddoc3a_model.py` — STANDALONE, python `re` only. A small backtracking PATH MODEL written from the ruled
  words (a condition is a piece of the pattern; branchings reset the labels inside them; `&` keeps P's paths whose
  stretch Q matches whole, P outer; complement, lookahead, atomic, backreference by PCRE's capture), with PCRE2's
  find-all loop. Each example is compared with a plain-regex LOWERING (python `re`, exact for that example only)
  where one exists, and with the frozen draft's PRINTED answers (typed in by hand from the named PART); its line
  must occur verbatim in core.md. Checks: one per example, plus CAPT2, PATH2, NUML2, TV2, PSR2, AND2, AND3, LOOK2;
  R1 (every ruled piece's rulings titles found in the record, every quote verbatim), R2 (no `needs:` into a later
  section), DONE (no `?`, no skeleton left), SL (the 124 slugs homed). The header lists sabotages s1-s21.
- `preddoc3a_model.out` — forward run: 40 checks, 0 failed.
- `preddoc3a_sabotage.out` — each of s1-s21 alone: 21 of 21 CAUGHT (the named checks failing).

## Run (no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/preddoc3a && timeout 300 python3 -I -B \
        <worktree>/docs/dev/lanes/preddoc3a_evidence/preddoc3a_model.py)

Under a second. `PREDDOC3A_SABOTAGE=s3` (one plant at a time).

## Limits

- The path model is RULE-AS-CODE; its controls are the lowerings and the printed answers, neither built from it.
- The lowerings are exact for their examples only, never a general lowering of conditions.
- Diagnostics (warnings, compile errors) are not runnable here.
