# docs/dev/lanes/preddoc4_evidence/ — the r59 design fixes' runs

Lane preddoc4 (2026-11-19), DESIGN EVIDENCE for the pieces of `docs/design/predicates/` that lane added or changed
while applying review r59's design-bearing findings and the manager's ruling R-1: every example line added or
changed is run in WHOLE, SEARCHED and FIND-ALL; the corrected `padded` body is built MECHANICALLY from its printed
text; the manager's readings 1 and 2 are tested over the base files. Rules nothing. Historical after merge.

## Files

- `preddoc4_model.py` — STANDALONE, python `re` only; the path engine of lane preddoc3c copied unchanged, plus a
  body builder that parses a body's text from library.md and substitutes `${p}` holes (a bare parameter stays
  literal text). PARTS PD (padded, built from its text), AT (atomic), KI (kinds example with `!`), CM
  (comparisons), TU (tuples), NE (negation), ZL (`0` in a loop, both candidates), SO (some), CO (count), ME
  (`.index`), CL (computed label), PT (pattern), RP (rx.repeat's copies), R1 (reading 1 under R-1: no core piece
  is a call-form name, every library piece has `defined:`; prints the native list), R2 (reading 2: every name
  called in a base file has a library piece; exceptions listed in the script), DOC (each example line verbatim in
  core.md or library.md). Header lists sabotages s1-s16.
- `preddoc4_model.out` — forward run: 16 checks, 0 failed, rc 0.
- `preddoc4_sabotage.out` — each of s1-s16 alone: 16 of 16 CAUGHT.

## Run (no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/preddoc4 && timeout 600 python3 -I -B \
        <worktree>/docs/dev/lanes/preddoc4_evidence/preddoc4_model.py)

`PREDDOC4_SABOTAGE=s3` (one plant at a time); `PREDDOC4_LINES=1` prints the example lines.

## Limits

- Conditions and group questions are lowered by hand per example (a python predicate over the path's captures):
  exact for these examples only.
- Python has no branch reset `(?|`: PART RP runs the copies as `(?:...)` (no group inside, so the answers are equal).
- Reading 2's name scan is lexical (code spans, `name(` not after `$`, `@`, `/`, `.`); it does not see bare names
  used without a call (`digit`).
