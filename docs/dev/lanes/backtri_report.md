# [BACKLOG-TRIAGE] (2026-09-22, lane backtri, sonnet)

Delivers `docs/dev/backlog_triage_2026-09-22.md`: a 93-row inventory (81
`STATE:not-started` rows + 12 dormant `STATE:started` rows), each placed
into a D86 column (feature/optimization/admin-structural) with its D77
trigger and dependencies, three ranked column lists, a close/fold
candidate list, and one top proposal per column. Read-only against
`src/`/`tests/`/`cli/`/`lib/` — nothing under those touched; this lane
only reads and writes `docs/dev/`.

## What the count check found

The brief and [BACKLOG-TRIAGE]'s own plan.md row text both cite "100" /
"102" not-started rows, both from an **unanchored**
`grep -n "STATE:not-started" docs/dev/plan.md`. That grep over-counts:
rows now `STATE:started` or `STATE:completed` often carry the phrase
"formerly STATE:not-started" in their own history prose (the exact same
prose-vs-tag confusion class the codebase's `[MECH-REACH]`/K35 lineage
already warns about for checks, one level up — here it bit a plan-row
census instead of a sabotage census). An anchored count
(`grep -cE "^[[:space:]]*- \[[^]]*\] STATE:not-started" docs/dev/plan.md`)
reads **81**. Full anchored tally for the file: not-started 81, started
19, completed 69, completed-in-place 2, closed-not-started 2, deferred 4
(blocked 0) = 177 real rows; the observed 100/102 also swallowed the
format-template line at `plan.md:9` and, in the brief's case, its own
citation of the grep recipe. The triage document's §0 records this and
recommends re-pinning plan.md's own row text plus a `learnings.md` §3
addition on the anchoring lesson.

Verifying the STATE:started side the same way (19 rows) surfaced a
second issue the same mechanism caused: `[OPT-5]`, `[OPT-VMFL]`, `[DD-11]`
etc. all contain "STATE:not-started" as prose too — every one was
individually re-checked with the anchored pattern and by reading enough
of the row's own text to classify it as genuinely in-flight, genuinely
dormant, or a false hit.

## Findings the honesty check surfaced (not asked for, found while dispositioning triggers)

- **[DD-1] is delivered, not open.** Its remaining charter after the
  OS-1/D23 ASCII closure ("multi-byte fold pairs, one-to-many foldings
  and the fold-before-negate rule") is verbatim what
  `docs/dev/lanes/CLAUDE.md`'s own `utf8s4_report.md` entry describes as
  shipped under the heading "[M5.0] STAGE 4, DD-1's FOLD CLOSURE." DD-1's
  plan.md text (line 1288) was never updated with a closure note.
- **[DD-12]** is a one-line unfinished stub ("— the UTF ARCHITECTURE
  sketch (Frank,", plan.md:1289) that predates the real UTF-8 design
  actually built across [M5.0]'s five stages. Flagged for close or
  rewrite-as-pointer.
- **[DD-7]**'s own text already dispositions both of its halves (one
  answered by `engine_m4.md` §7.1, the other re-homed to [ENG-ABS]); a
  grep for "M4.3" (the one open dependency it names) found no other hit
  in `plan.md`/`decisions.md` — flagged for the manager to check
  `dev_journal.md` before closing.
- **A cluster of four rows** (DD-2, M4-CALLOUTS, M4-SUBST, DD-6) name
  "M4" or "the assertions module" (M6) as their trigger; M4/M5 are
  recorded shipped (`rel1a_report.md`) and M6.0 is
  `STATE:completed` (`plan_completed.md:3762`). None shows a post-landing
  revisit. Flagged as a systemic gap, not four one-offs — the triage doc
  proposes a standing rule (grep plan.md for a milestone's ID whenever it
  completes).
- **[CC-CLANG]**'s row still reads "awaiting merge review" from
  2026-09-01, but `git merge-base --is-ancestor origin/lane/cc HEAD`
  confirms it merged, and three later commits build on its mechanism.
  Only STEP 3 (behind "Frank's perf hold") is genuinely open.
- **[DD-11]**'s stated gate, M6.6, completed 2026-08-24
  (`plan_completed.md:3658`) — the follow-on [DD-11.5]/[DD-11.6] appears
  to have been actionable for nearly a month without being reopened.
- **[BENCH-1]** — its own most recent text already reads "Bench-owned;
  pcrec owes the registry seed and the answers," which D78 (the bench
  repo split) and D119 (the OPTLOOP cause-taxonomy loop, which names
  `[OPTLOOP.1.analysis]` as its own worklist generator) have made
  structurally true. Recommended to fold into D119's model.
- **[OPT-4.2]** is a closed Frank ruling ("WAIT FOR A WITNESS — no row,
  no hunt") sitting in a still-open plan row; recommended to convert to a
  `known_issues.md`/`decisions.md` note and close the row.
- **[TT-14]** looks, by content alone, like a likely duplicate of
  [TT-4M]/[TT-4M-TIME]'s already-delivered batching work — flagged, not
  acted on (would have needed a full read outside this lane's scope).

None of these were re-diagnosed or re-measured; each claim above is
either a direct grep/git check or a citation to an already-committed
report. See the triage document's "Open questions" section for the full
list with exact evidence.

## Scope discipline

Per the brief: this lane did not rank the optimization column against
bench data (no bench access, no measurement run) — it ranked by trigger
state and Frank's own recorded sequencing only, and the triage document's
§2b says explicitly that this ranking is to be merged with lane
`optrev`'s [OPTLOOP.1.analysis] cause-ranked output by the manager.
`plan.md` itself was not modified (read-only per the brief).

## Deliverables

- `docs/dev/backlog_triage_2026-09-22.md` (committed, this lane's main
  deliverable)
- `docs/dev/lanes/backtri_report.md` (this file)
- `docs/dev/lanes/CLAUDE.md` +1 line
- `docs/dev/CLAUDE.md` +1 line (points at the triage doc)

## Validation

Docs-only lane; no `make`/`make test`/`make strict` run (nothing under
`src/`/`cli/`/`lib/`/`tests/` touched, and the brief specifies a WRITER
worktree with no build step). All facts checked against the live tree
via `grep`/`sed`/`git log`/`git merge-base` — commands and outputs are
reproducible from this report's own citations.

## Handback

Complete. Nothing owed. Committed on `lane/backtri`, not merged.
