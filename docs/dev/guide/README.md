# docs/dev/guide/ — the living coding, architecture and style guide

One guide for two readers: coding agents WRITE to it (lane briefs point here)
and code critics REVIEW against it. It changes often, so it lives in the repo,
outside any skill; skills and `docs/dev/lanes/BOILERPLATE.md` reference it.

## Read before your first code edit

`coding.md` (C under `src/`, `cli/`, `lib/`, and checks), then the files below
that match your area. Critics read `critics.md` as well.

## Files

- `coding.md` — house disciplines, taught primitives, emitted-text rules, the
  altitude rubric, writing a check, the do-nots. Cited elsewhere as `coding_guide §N`.
- `architecture.md` — design rules: tables for decisions, general mechanisms,
  facts across the kit boundary, build under measurement.
- `style.md` — naming, comments, spec-in-same-change.
- `critics.md` — how a code critic uses the guide (first version).
- `addenda/` — per-area additions (see `addenda/README.md`).

## How to amend

A rule enters with its WHY and a SOURCE: a D-number in `docs/dev/decisions.md`,
a review file under `docs/dev/reviews/`, or "Frank YYYY-MM-DD". Rules, not
findings; an incident is one line, never a paragraph. A rule re-learned the hard
way gets its incident line. Verify a D-number exists before citing it. Rules
that change when a refactor lands say so; never tell a reader to use a
primitive that does not exist yet.

## Addenda

An area's additions live in `addenda/<area>.md`; they add to the base and never
contradict it. A conflict goes to the manager, not to a quiet override.
