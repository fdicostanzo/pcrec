# Lane adm131 — D131 docs + exec summary: report

Lane `adm131` (sonnet, ADMIN, docs only), branch `lane/adm131` off `main`
at `fdcf3e00`, 2026-09-29. Nothing under `src/`, `cli/`, `lib/`, `tests/`
touched. Source of truth: `docs/dev/decisions.md` D131 (just committed at
branch point), D129, D130.

## Item 1 — apply clsfit's verbatim λ diff

`docs/dev/lanes/clsfit_report.md`'s diff did **NOT** `git apply --check`
cleanly against this branch point — the file has drifted since the diff
was cut against `608bd094` (line numbers moved, and the diff's own second
hunk context (`-fno-offset-skip`) does not match this tree's actual
context line at that location, `-fno-premul-table`). **Hand-applied
faithfully**, content byte-for-byte identical to the diff apart from
substituting `D131` for the `D<next>` placeholder:
- `docs/design/opt_dial_design.md` §4: the new "RE-PROPOSED AFTER
  [CLS-TREE] S0's CALIBRATION" block + the re-proposed table, inserted
  before the superseded five-constant table (kept, labelled "superseded
  pins... kept for the record").
- `docs/spec/tuning.md`'s λ row: replaced `reservation` × 5 with the
  ruled first-match policy, citing D131 and the calibration.

Verified: no stray `D<next>` left anywhere in the tree; both markdown
tables read cleanly.

## Item 2 — plan.md rows

All five, each citing D131:
- `[CLS-TREE]` (docs/dev/plan.md:1532): appended S0 COMPLETE (calibration
  in cls_tree_design.md §1.7, λ ruled), S1 CHARTERED (lane clss1), S2
  RE-SCOPED (byte forms are size-leaning only).
- `[OPT-CLSPACK]` (plan.md:1411): appended PROMOTED TO BUILD — atom table
  default from N ≈ 11, ≤ 64 atoms. Left `STATE:not-started` (no build
  lane exists yet; "promoted" reads as a ruling, not a started build) —
  **flagging this as a judgment call** in case Frank wants
  `STATE:started` instead.
- `[FINDINGS-BENCH-TIERS]`: **CLOSED**, not left open. Read the row's own
  charter (deliver the bench's four-column numbers, Frank reads them
  before any bench-config decision) against D131's own text: every
  actionable finding already has a separate owner (`[FIND-DOMAIN-CHECK]`
  filed, `[SEL-COST]` pulled forward, `[LIST-TABLES]` noted) — nothing is
  left for this row itself to still be "open" about. Moved to
  `docs/dev/plan_completed.md` under a new `## Completed 2026-09-29`
  header, `STATE:completed`, with the numbers summarized inline
  (DECLARED misleads, PROFILED never regresses, ORACLE-BEST headroom ~0
  on loglines / real on email, `--tune` moves only two positions). If
  Frank wants it left open pending the `--extended`/compile-time-axis
  follow-up, that's a one-line revert (move the row back, `STATE:started`).
- New row **`[FIND-DOMAIN-CHECK]`** (plan.md:362, filed not scheduled):
  D131 item 7, citing O-74's weblog iso-ts ×1.47/×1.84 finding.
- `[SEL-COST]` (plan.md:229): parenthetical changed from "NOT scheduled"
  to "PULLED FORWARD into the next optimization cycle's queue, D131 item
  8"; appended the email whole-subject ORACLE-BEST evidence (×0.648
  floor / ×0.856 orig).
- `[LIST-TABLES]` (plan.md:1541, now ~1550 after the insert above):
  appended O-74's open question — PROFILED moved `iso-ts`'s program
  (`program_sha256` fb085cf3 → e094fe46, as given in the brief) with no
  read stamp moving.

## Item 3 — executive summary

`docs/dev/summaries/2026-09-29-b115-findings-tiers-exec-summary.md`,
following the 2026-09-28-b108 precedent's four-section shape (findings /
surprises / impact / next steps), every number cited to the bench ledger
(`/Users/fdicostanzo/pcrec-bench/docs/dev/ledgers/2026-09-29-b115-findings-tiers-f7f5a143.md`)
or O-74. The next-steps table names WHO answers each open item (mostly
"stock-take" — there's nothing left for the bench to answer, since O-74
is fully read into D131).

**On the CLS-TREE S0 addendum**: there was no existing precedent
directory shape for "two topics, one exec summary" or "same-day second
ledger", so I added it as a clearly-headed second section within the
SAME file (both stem from D131's same ten-item status list) rather than a
separate file — flagging this choice in case Frank prefers a separate
`2026-09-29-clstree-s0-exec-summary.md`.

`docs/dev/summaries/CLAUDE.md` updated with the new file's bullet.

## Item 4 — CLAUDE.md updates

Content-only edits (no file adds/removes) in `docs/design/`/`docs/spec/`,
so no *mandatory* CLAUDE.md update — but I added short addenda anyway,
matching this project's own convention of dated append-only annotations
on design/spec CLAUDE.md entries when a ruling lands on a document those
entries describe:
- `docs/design/CLAUDE.md`'s `opt_dial_design.md` entry: notes the D131
  supersession of the five pinned frontier constants.
- `docs/design/CLAUDE.md`'s `cls_tree_design.md` entry: notes §1.7's
  addition and its D131 rulings (λ, CLSPACK promotion, D129 Q5 amendment).
- `docs/spec/CLAUDE.md`'s `tuning.md` entry: notes the λ row's first
  move off `reservation`, still design-stage since `[CLS-TREE]` is
  unbuilt.
- `docs/dev/summaries/CLAUDE.md`: new file's bullet (item 3 above).

## Unresolved / flagged for Frank

1. `[OPT-CLSPACK]`'s STATE tag left at `not-started` despite "PROMOTED TO
   BUILD" — see item 2 above.
2. `[FINDINGS-BENCH-TIERS]` closed rather than left open — see item 2
   above; easy to revert if wrong.
3. The CLS-TREE S0 addendum's placement (second section, same file vs. a
   separate file) — see item 3 above.

## Validation

Docs-only lane; no `make` run (per BOILERPLATE.md, admin/docs lanes don't
build). Checked: `git apply --check` on the clsfit diff (FAILED, hand-
applied instead, reported above); grep for stray `D<next>` (none); both
edited markdown tables read structurally intact by eye.

Branch `lane/adm131`, all work committed. Ready for merge review.
