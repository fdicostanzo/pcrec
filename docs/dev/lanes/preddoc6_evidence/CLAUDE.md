# docs/dev/lanes/preddoc6_evidence/ — the r60 fixes' runs

Lane preddoc6 (2026-11-19), DESIGN EVIDENCE for the example lines of `docs/design/predicates/` that lane added or
changed while applying review r60's FIX-NOW batch, and for the manager's three readings. Rules nothing. Historical
after merge.

## Files

- `preddoc6_model.py` — STANDALONE, python `re` only; lane preddoc4's path engine and body builder copied
  unchanged, plus a path expander. PARTS TV (core/conditions/two-valued's table, both columns, every path of P),
  CF (call-forms: `rx.repeat(rx.digit, 3)` by each body, built from lib/rx/repeat's text), CP (capture's body
  built from its text), MN (month_numbered, the twelve names read from the body), EX (core/labels/export's
  program), DG (`/\d${(0: rx.digit)}x/`), CG (condition-group's candidate (b) and the unquantified control), EV
  (count's even-count pattern), R3 (reading 3: every called name has a library piece; no bare `digit` in a code
  span), DOC (each printed line verbatim in core.md or library.md). Header lists sabotages s1-s9.
- `preddoc6_model.out` — forward run: 10 checks, 0 failed, rc 0. `preddoc6_sabotage.out` — s1-s9 each alone: 9 of 9 CAUGHT.
- `preddoc6_defs.py` / `.out` — reading 2: names defined twice with different bodies in the base files.
- `preddoc6_recount.out` — reading 1: review r60's four list re-counts re-run on this lane's tree (the critic's
  scripts, `$PCREC_TMPDIR/scratch/crit-preddoc5/recount/`, copied to the lane's scratch with only the tree path
  changed; they read r59's population files under `$PCREC_TMPDIR/scratch/crit-preddoc3/`, not committed).

## Run (no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/preddoc6 && timeout 600 python3 -I -B \
        <worktree>/docs/dev/lanes/preddoc6_evidence/preddoc6_model.py)

`PREDDOC6_SABOTAGE=s3` (one plant at a time); `PREDDOC6_LINES=1` prints the example lines.

## Limits

- Conditions are lowered by hand per example; exact for these examples only. The control for an example line is
  the document's own printed line (PART DOC), written before the run.
- The examples moved by COLD-10 (contains/endsWith candidate runs, now `readings:` in library_details.md) moved
  word for word and are not re-run here; their runs are lane preddoc3c's and preddoc4's.
- Reading 3's scan is lexical (as preddoc4's R2) plus a bare-`digit` search in code spans.
