# closefold — applying Frank's ruling on [BACKLOG-TRIAGE]'s close/fold candidates

2026-09-22, lane closefold, sonnet, docs-only (nothing under `src/`/`tests/`).
Branch `lane/closefold` from main `69172a00`. Source of truth:
`docs/dev/backlog_triage_2026-09-22.md` §3 and Frank's ruling "Agree with
close items" (2026-09-22).

## What was done

Six rows moved from `docs/dev/plan.md` to `docs/dev/plan_completed.md`,
each flipped to `STATE:completed` with a one-sentence closure note citing
"Frank 2026-09-22, backlog_triage_2026-09-22.md §3", body text preserved
verbatim, archived under a new `## Completed 2026-09-22 (lane closefold...)`
heading:

1. **[DD-1]** — closed: delivered under [M5.0] stage 4 (DD-1's fold
   closure, `utf8s4_report.md`).
2. **[DD-12]** — closed: superseded by `docs/design/utf8_design.md` and
   [M5.0].
3. **[DD-7]** — closed: both halves dispositioned (capture prefilter
   answered by `engine_m4.md` §7.1; `^`/`$` absorption re-homed to
   [ENG-ABS]); the M4.3 panel DID happen — confirmed directly in
   `plan_completed.md`'s own "Completed 2026-08-14" section, whose
   `[M4.3]` entry reads "COMPLETED 2026-08-14 (R21; row archived in
   plan_completed.md) — the D6 panel ran (3 critics, 36 findings, 11
   tier-1)..." at `docs/dev/plan.md:121` (pre-edit line number, in the M4
   milestone's historical prose). This corroborates the manager's own
   verification named in the brief.
4. **[BENCH-1]** — closed: FOLDED into D119's [OPTLOOP] (the bench repo
   D78 + the cause-ranked analysis are its two jobs).
5. **[OPT-4.2]** — closed: Frank's ruling "WAIT FOR A WITNESS — no row,
   no hunt" stands as a closed disposition; the impact-bounded finding
   recorded. Cross-referenced in `docs/dev/known_issues.md`'s K41 entry
   (no prior cross-reference existed in either `known_issues.md` or
   `decisions.md` — checked by grep for `OPT-4.2`, `WAIT FOR A WITNESS`,
   `witness gap`, `witness-gap`, `ESEL_DECLINED_NULLABLE` before adding).
   K41 was chosen as the "appropriate section" because it is the entry
   that documents the exact `compile_driver` size-cap retry rung
   `ESEL_DECLINED_NULLABLE` belongs to — not a fresh K-number, since
   `known_issues.md`'s own charter is "confirmed correctness bugs" and
   OPT-4.2's own text says the unwitnessed path is "performance-only,"
   i.e. not a bug.
6. **[TT-14]** — closed: FOLDED into [TT-4M]/[TT-4M-TIME] (the same
   charter, built there); [TT-15] stays distinct.

**[BENCH-1] dependency re-pointing.** Grepped the whole tree for every
row naming `[BENCH-1]` as a dependency, gate, or proving-ground reference
(not counting prose in "Development order"/"Beyond M7" narrative sections,
which cite no STATE tag and are not rows, and not counting two
STATE:completed historical notes — `[M4.2]`'s and `[DD-9]`'s own archived
text — which describe what already happened rather than a live gate).
Seven live rows qualified and each got ONE bracketed addendum
(`(gate re-pointed 2026-09-22: [BENCH-1] folded into [OPTLOOP]; ...)`)
pointing at `[OPTLOOP]`'s cycle analyses (`docs/dev/optloop/
cycle1_analysis.md` as the running example) instead of BENCH-1's
now-closed worklist/prioritizer:

- **[BENCH-CEIL]** (`docs/dev/plan.md`, "cross-links: [BENCH-1] (home
  instrument)" / "alongside [BENCH-1]'s build-out")
- **[ENG-ABS]** (the FIRST mechanism, `^`-absorption, "stays gated on
  [BENCH-1]'s `^`-on-some-branches case") — used the brief's own example
  addendum verbatim, since cycle 1's analysis names this exact witness
  under `[OPT-ATTEMPT-SPLIT]`, `docs/dev/optloop/cycle1_analysis.md` M5
  (confirmed by grep: `[OPT-ATTEMPT-SPLIT]` `^` on some branches, priority
  score 0.306, size M-L, PROPOSED 2026-09-22).
- **[ENG-CUT]** ("build when a [BENCH-1]/[ENG-PGO]-class customer
  exists")
- **[ENG-ISL]** ("waits for evidence that capture-free VM-FALLBACK
  FRAGMENTS ... are hot: [BENCH-1] floors or [ENG-PGO] profiles showing
  it") — noted that cycle 1's analysis already scores this parked row at
  0 on the capability subbench ("not in this matrix", not refuted).
- **[ENG-PGO]** ("implementation AFTER the M4 spine closes and WITH
  [BENCH-1] ... BENCH-1's prioritizer is also this row's proving ground")
- **[SIMD-META]** ("reconcile with DD-9/[BENCH-1]'s case-(f) worklist
  row")
- **[OPT-SIMD]** ("adoption measured under BENCH-1's instruments")

None of these seven rows' `STATE` tags were changed — only the dependency
text, per the brief.

**Root CLAUDE.md.** Added one row to the situation-index table:

    | complete a milestone or close a row | grep plan.md for rows naming
    it as a TRIGGER or gate (DD-2/M4-CALLOUTS/M4-SUBST/DD-6/DD-11 sat
    months behind shipped M4/M6/M6.6 — backlog_triage_2026-09-22.md) |

**[BACKLOG-TRIAGE]'s own row** updated with "closes applied 2026-09-22
(lane closefold): DD-1/DD-12/DD-7/BENCH-1/OPT-4.2/TT-14 archived to
plan_completed.md, [BENCH-1]'s dependency text re-pointed at [OPTLOOP] in
7 rows".

## Verification

Anchored counts (`grep -cE "^[[:space:]]*- \[[^]]*\] STATE:not-started"` /
`STATE:started` on `docs/dev/plan.md`, `grep -c "STATE:completed"` on
`docs/dev/plan_completed.md`), before vs. after — the plan.md header's
own recorded starting figure (81) and a fresh grep of `main` for the
started count:

| metric | before | after | delta |
|---|---|---|---|
| plan.md anchored `not-started` | 81 | 77 | -4 (DD-1, DD-12, DD-7, TT-14) |
| plan.md anchored `started` | 19 | 17 | -2 (BENCH-1, OPT-4.2) |
| plan_completed.md `STATE:completed` (grep -c, all occurrences incl. sub-rows) | 193 | 199 | +6 |

Arithmetic reconciles exactly with the six moves (all six were verified
individually as `not-started`/`started` at plan.md's own text before
moving them — DD-1/DD-12/DD-7/TT-14 were `STATE:not-started`; BENCH-1/
OPT-4.2 were `STATE:started`, matching the brief's prediction).

Every moved row was confirmed to appear **exactly once**, verbatim plus
its closure note, in `plan_completed.md`
(`grep -c "^- \[ID\] STATE:completed"` = 1 for each of the six), and
**zero times** in `plan.md` (`grep -c "^- \[ID\] STATE:"` = 0 for each).

`git diff --stat` on the branch: `CLAUDE.md` +1, `docs/dev/known_issues.md`
+8, `docs/dev/plan.md` 110 changed (81 deletions, 29 insertions — the six
row bodies removed net of the seven small addenda and the one BACKLOG-
TRIAGE edit), `docs/dev/plan_completed.md` +83. The full diff was read
line-by-line (not just diffstat) to confirm the six removals and seven
addenda are the only content changes, plus the one apparent adjacent
"K38-FIX" context line in the diff output, which is unmodified — a diff
hunk-header artifact from the neighboring TT-14 deletion, not a change to
that row (checked: identical text before and after, present in the
`plan_completed.md` diff nowhere and in `plan.md`'s "after" content
unchanged).

No `make`/`make test`/`make strict` run — docs-only lane, nothing under
`src/`/`cli/`/`lib/`/`tests/` touched, per BOILERPLATE's read-only critic
carve-out for a writer whose whole diff is documentation (still worked in
a worktree per the writer ritual, since the brief calls this lane a
"Docs-only WRITER").

## Not done / left for the manager

- [DD-9]'s and [M4.2]'s own historical `COMPLETED`-not-`STATE:completed`
  text (lines in the M4/DD narrative, predating the `STATE:` tag format)
  still mention `[BENCH-1]` descriptively — these are historical record,
  not live gates, and were deliberately left untouched (the brief's
  re-pointing scope is "every row that names [BENCH-1] as a dependency
  or gate", and these are neither rows in the current format nor gates —
  they narrate what already happened).
- [PLAN-AUDIT] and [REL-1] are both `STATE:completed` rows still resident
  in `plan.md` (not `STATE:not-started`/`started`, so outside this
  lane's six-row scope) — the brief names [REL-1] explicitly as an
  exception the manager will handle separately; [PLAN-AUDIT] was not
  named and was left alone rather than guessed at.
