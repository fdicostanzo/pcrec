# docs/dev/lanes/predbang_evidence/ — the runs behind the `!` candidate (2026-11-27)

Evidence for `docs/dev/pred/bang_candidate.md` (the candidate rule set for `!`, [COND-FAMILY]; nothing ruled). Each
script is a python3 -I `re` run the predicate manager made while discussing with the owner; the record
(`docs/design/plan_row_bodies/COND-FAMILY.md`, entries of 2026-11-27) pastes their lines. They PRINT; they assert
nothing and cannot fail: runs, not checks.

- `bang_forms.py` — `A & !B & !C` against `A &! (B | C)`; `A & (C | !B)` against `A &! (B &! C)`; a control pair.
- `bang_entry.py` — the four entry cells on `/(?<h>\d)?x/` (present / absent-allowed by in / outside).
- `bang_record.py` — a negated record and a negated joint entry against entry-by-entry rewrites.
- `when_cond.py`, `when_peek.py` — a conditions-only `when` through a label on a (possessive) optional.
- `when_zero2.py` — `when((0: A), A SEQ B, C)` under two readings of `0`.
- `when_diff.py` — `(A SEQ B) | (C &! A)` against today's `when` body.
- `caret.py` — `when(^A, B, C)` and `when(^!A, B, C)` under the body `T SEQ B | ^!T SEQ C`.
- `*.out` — each script's committed output.

Design evidence only; no check under `make` reads it.
