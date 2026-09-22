# Lane admin2 — plan archive sweep + learnings addendum + BOILERPLATE

Three commits on `lane/admin2` from `b3086b46`, docs-only, no build/suite run
needed for any of the three (no `src/`/`tests/` touched).

1. `0030cbaa` — plan.md ARCHIVE SWEEP
2. `9fa3697a` — learnings.md §3 addendum
3. `b67575da` — BOILERPLATE.md + CLAUDE.md

## 1. plan.md ARCHIVE SWEEP

### The count discrepancy up front

The brief's anchored baseline (not-started 81, started 17, completed 71)
was already stale by the time this lane started: `closefold` (folding
DD-1/DD-12/DD-7/BENCH-1/OPT-4.2/TT-14 into `plan_completed.md`) and the
manager's own BENCH-REVIEW/BACKLOG-TRIAGE closure both landed on main
**the same day, before `b3086b46`**. Re-measured fresh on this lane's own
branch point:

```
grep -cE "^[[:space:]]*- \[[^]]*\] STATE:not-started" docs/dev/plan.md   # 81
grep -cE "^[[:space:]]*- \[[^]]*\] STATE:started" docs/dev/plan.md       # 14
grep -cE "^[[:space:]]*- \[[^]]*\] STATE:completed[^-]" docs/dev/plan.md # 70
grep -cE "STATE:completed-in-place" docs/dev/plan.md                    # 2
```

The `71` in the brief and the `72` its own unanchored-substring caveat
implies both come from `grep -c "STATE:completed"` (no word boundary),
which also matches `STATE:completed-in-place` — a genuinely different,
deliberate state ([SPEC-1.9], [DD-4], both already self-documented as
"retained here rather than archived" and correctly untouched by this
sweep). The real population of exact `STATE:completed` rows at this
lane's branch point was **70**, not 71/72.

### What moved, grouped by parent `## ` milestone heading

62 of the 70 moved verbatim to a new dated section in `plan_completed.md`
(`## Archived 2026-09-22 (lane admin2: ...)`), grouped by the nearest
preceding `## ` heading in `plan.md`:

| group | rows moved |
|---|---|
| M5 — UTF-8 | 3 (K50-NULLGATE, ENCCHK-DD12A, K53-SELRETRY) |
| Beyond M7 — long-term vision | 36: TT-6/TT-5/TT-7/CHK-1/K38-FIX/TT-12/TT-11/TT-10/MECH-REACH/TT-9/TT-8 (11), SPEC-1.1-1.8 (8), REG-SV, SPEC-1.10, LIM-1, PLAN-AUDIT (4), REL-1 + REL-1.1-1.11 (12, one archive group), REL-META |
| The 2026-09-17 code-review refactor | 10: K60-FIX/D105-BUILD/ALLOC-PINS/REVW.2/BSWEEP/EMIT-VERB/REVW.3/REVW.4/REVW.5/REVW.A1 |
| Design-debt ledger | 3: HDR-1/HDR-2/DD-13c |
| Parser structure — the syntax construct registry | 1: TT-2 |
| Optimization waves (D21) | 9: OPT-1/OPT-2/ENG-FORM/OPT-4.1/OPT-EDGE/FORM-CHAR/OPT-DIAL/CC-DIFF/ART-SIZE |
| **total** | **62** |

Two pointers left in `plan.md` (both "parent still needs its children's
existence visible" cases, per the brief):

- Under `[SPEC-1]` (STATE:started; its own [SPEC-1.11] child is not yet
  done): `sub-rows 1.1-1.8, 1.10 archived 2026-09-22 -> plan_completed.md
  (REG-SV and LIM-1, standalone rows in this span, archived too)`.
- `[REL-1]` itself replaced by a one-line stub matching the file's own
  established convention for a fully-archived milestone (the same shape
  as the pre-existing `[K50-BNDSTART]`/`[M6.0]`/`[ABI-NS]` stubs already
  in the file): `[REL-1] archived to plan_completed.md (completed
  2026-09-22 — the 0.1.0-beta release tagged on Frank's word; sub-rows
  REL-1.1-REL-1.11 archived with it, all delivered per D113/D116)`.

### Exceptions kept resident (8 rows), each judged and reasoned

Per the brief: `[OPTLOOP.1.analysis]` explicitly, plus "any completed row
whose text a STATE:started sibling references by line proximity." Judged
against the actual file, five more rows fit that shape and one family
(DD-13's four indented children) fits it as a group:

- **[TT-4] / [TT-4.1]** (kept, lines then 308-370) — [TT-4M]
  (STATE:started) sits on the line **immediately** before [TT-4] with no
  blank line between them, and its own text says so explicitly:
  "re-opening [TT-4]'s closed levers ON DARWIN — the close note's own
  revisit condition." [TT-4.1] is [TT-4]'s own indented sub-bullet,
  directly continuing the same closure narrative; archiving [TT-4] while
  leaving [TT-4.1] orphaned (or vice versa) would have split one story.
- **[OPTLOOP.1.analysis]** (kept) — the brief's own named exception:
  in-flight cycle context under the started [OPTLOOP] parent.
- **[ENG-ISL.S0]** (kept, one line only — see the block-boundary note
  below) — the identical shape to [OPTLOOP.1.analysis]: a completed
  sub-study sitting directly under the still-parked, STATE:started
  [ENG-ISL] parent, which the brief's phrasing ("judge") invites treating
  the same way.
- **[DD-13a] / [DD-13b.W1] / [DD-13b] / [DD-13b.panel]** (kept, as a
  group) — all four are indented children of the still-STATE:started
  [DD-13] (itself PARKED, not closed), and [DD-13b.W1.3] — also
  STATE:started — sits physically WEDGED between two of them ([DD-13b.W1]
  and [DD-13b], line 1339 between 1338 and 1340), so archiving the
  completed children would break the reading order of an
  actively-tracked, unfinished format-design milestone mid-stream.
  **[DD-13c]**, despite the similar name, is a SEPARATE top-level row (no
  indentation, no interleaving with any started sibling) and archived
  normally.

### A block-boundary correction the mechanical scan got wrong once

An automated "block = bullet line through the last line before the next
bullet/heading" scan initially proposed archiving [ENG-ISL.S0] as lines
992-1011. Reading the actual content: lines 993-1011 are a stray,
unindented-by-marker continuation paragraph that is **about the parent
[ENG-ISL] row** ("this parked row", "the FIRST mechanism... stays gated
on [BENCH-1]"), not about the S0 sub-study — it happens to sit physically
after S0's own single-line bullet in the file, purely by prior editing
history, with nothing marking the seam except that line 993 restarts a
different topic without a "- [" bullet marker. [ENG-ISL.S0]'s own block
is exactly ONE line (992); the trailing prose stays untouched as [ENG-ISL]
's own continuation, which is moot anyway since [ENG-ISL] itself is kept.
Every other multi-line block among the 70 was hand-read in full before
being trusted (verified coherent, no similar seam) — see the commit's own
message for the shorter version.

### Verification (arithmetic reconciles exactly)

| | before (this lane's branch point) | after |
|---|---|---|
| plan.md `STATE:not-started` (anchored) | 81 | 81 (unchanged) |
| plan.md `STATE:started` (anchored) | 14 | 14 (unchanged) |
| plan.md `STATE:completed` (anchored, exact) | 70 | 8 (exactly the 8 kept rows, verified by name) |
| plan.md `STATE:completed-in-place` | 2 | 2 (unchanged, untouched by design) |
| plan_completed.md `STATE:completed` (`grep -c`) | 203 | 265 (+62, exact) |

Every one of the 62 moved rows appears exactly once in `plan_completed.md`
and zero times in `plan.md` (grepped by exact `[ID]` for a sample spanning
the whole list, plus the REL-1.x family in full). Two double-blank-line
artifacts the removals produced (a heading directly followed by a bullet
whose own leading/trailing blank lines became adjacent once the bullet
was deleted) were collapsed — confirmed absent from the pre-edit file
first, so the collapse could not have eaten a pre-existing intentional
gap.

## 2. learnings.md §3 addendum (`docs/dev/learnings.md`, new "### 3.y")

Three lessons from 2026-09-22, cited to source:

- A coverage-count guard living in a DIFFERENT FILE from what it counts
  (`run_registry_tests.sh:586` pinning `limits_check.sh`'s PASS count) can
  go stale even when the edited script is validated standalone and
  correctly — the guard's own "COVERAGE CHANGED" message never says
  `FAIL:`, and its own comment history names this the FOURTH instance of
  the identical failure mode (`regred_report.md`).
- "sections ran: N/M" counts launched sections, not passed ones — the
  real verdict is make's `*** [test-X] Error` lines (lane axesfix's
  finding, journal correction `b3086b46`).
- `[OPT-REQBYTE]`'s whole-window pre-check can retire a whole population
  of give-up/budget witnesses ([MECH-REACH]'s seventh instance) by
  omitting the pattern's required byte; the fix is at the check's build
  site (a deny flag, or a witness the mechanism structurally declines),
  never a per-witness `.rxt` line, since no `.rxt` block kind can deny a
  compiler axis. A mechanism that only discards provably-dead work has no
  answer-level detector, so its sabotage row is a stamp row
  (`optimpl1_report.md` §0.3 — not yet visible from this worktree at
  time of writing, cited per the brief's own text since it names the
  exact section).

## 3. BOILERPLATE.md + CLAUDE.md

Three terse additions to `docs/dev/lanes/BOILERPLATE.md` (ARM OWED RUNS
DETACHED under Process rules; DARWIN TIMEOUTS under Box facts; "RE-RAN
STANDALONE, CLEAN" MUST NAME THE FILE under Process rules) and one row
appended to the root `CLAUDE.md` situation index (reading a gate/suite
log's real verdict). `AXES="-fno-…"` was verified against
`tests/axes/run_axes.sh`'s own env-var name before being cited, rather
than guessed.

## Rulings received

None — no mid-flight questions arose; every judgment call (the kept-in-
place exceptions, the REL-1/SPEC-1 pointer shape, the DD-13c split) is
argued from the file's own content and existing conventions above.

## Handback

Docs-only lane; no `make`/suite validation applicable to any of the three
deliverables (no `src/`/`tests/`/`cli/`/`lib/` touched). All three
commits are on `lane/admin2` from `b3086b46`. Nothing owed.
