# Predicate manager -> main (ONE writer: the predicate manager; `[pred]` commits on its branch)

Entries are `P-n`, dated, never deleted. `done:` lines name the branch tip and the report path.

## P-1 (2026-11-18, predicate manager) — up

- Acknowledges M-1. The predicate manager session is up: branch `lane/pred-rev28` (worktree `worktrees/pred`),
  cut from main f9ee6814e. From now the draft, COND-FAMILY.md and predicates_future.md are written here only.
- First with Frank: the hole-reads-capture confirm, then the R.8 queue. No lane and no critic round running;
  I will ask for a review number before the rev 28 round.

## P-2 (2026-11-18 night, predicate manager) — done: rev 28.1 of the predicate draft, review r52 filed

- done: branch `lane/pred-rev28`, tip at this commit's parent chain (merge it at its head); reports
  `docs/dev/lanes/predspec28_report.md` (the fold) and `docs/dev/lanes/predspec281_report.md` (the fixes);
  review `docs/dev/reviews/2026-11-18-r52-predspec28.md` (+ its directory; dispositions ruled by me; indexed).
- What lands: `docs/design/predicates_draft.md` REVISION 28.1 (NOT STABLE); `COND-FAMILY.md` with the owner's
  ELEVEN rulings of 2026-11-18 evening (hole-reads-capture, number-domain, padded-width, hole-flags,
  flags-propagate, unset-in-hole, construction-line, value-test, same-name-twice, array-in-hole = future
  direction, numeral-width); `predicates_future.md` items 32-33; evidence dirs `predspec28_evidence/`,
  `predspec281_evidence/`; `docs/dev/pred/` (journal, wake, this file). Lane branches `lane/predspec28`,
  `lane/predspec281` are merged into mine; their worktrees are yours to prune (wtprune).
- [COND-FAMILY] plan-row status line I ask you to record: "2026-11-18: draft rev 28.1 (NOT STABLE; review r52
  filed); the owner ruled eleven questions on holes, numbers, flags and the construction line; open with him:
  padded-order, flags-in-filter, flags-scope, class-order, dollar-diagnostic, number-edges, any-case-body,
  same-name-count; design only, no build go."
- PROPOSED EDITS to files you own (accepted by me from the r52 coordinator; verbatim text in
  `docs/dev/lanes/predspec281_report.md`, STATE AT HANDOFF, items 1-4): pcrec-critic skill section 3 (a FREEZE
  NOTE when the fold range ends past the record at the subject commit) and three lens drills (set-equal bodies
  drilled in SEARCHED/FIND-ALL with a prefix pair; a flag rule run with every PCRE inline flag, `#` under x and
  an `&` inside the place; an evidence enumerator's order checked against PCRE priority order).
- PROPOSED EDIT to the pcrec-predicate-manager skill (a lesson that is a rule): section 2, "Before asking
  anything, grep the record": add "and, for a recollection of his ('I proposed'), every file under
  docs/design/plan_row_bodies/ and docs/design/ (the label-only group was in POSTFACT.md, 2026-11-09)"; and:
  "a body or macro offered to him as EQUAL to a meaning is run in SEARCHED and FIND-ALL before it is said, not
  only WHOLE (padded, r52 item A)".
- Note: `docs/dev/reviews/CLAUDE.md` is near its 12 KB limit (the r52 index line is short).

## P-3 (2026-11-19 early) — pausing; the owner ruled six more

- notice: the first predicate-manager session is CLOSED (/close). Nothing running; no lane, no round, no cron.
  Branch `lane/pred-rev28`, tip = this commit. P-2 above is still the delivery to merge (rev 28.1 + review r52);
  commits after it are record, journal, wake and this file only (no draft change).
- Since P-2 Frank ruled SIX more (record only, to be folded as rev 29 by the next session): padded-order (a plain
  macro, any-length branch first), flags-scope (inherit `i`, `m`, `s`; not `U`, `x`, `xx`, `n`), class-order (longest
  first, class positions only), dollar-diagnostic (the form `$x & ..` just gets a warning), number-edges (nothing),
  same-name-count (scoped, backreferences only).
- [COND-FAMILY] plan-row status line, replacing P-2's: "2026-11-19: draft rev 28.1 (NOT STABLE; review r52 filed);
  the owner has ruled seventeen questions since rev 27.1 (eleven folded, six waiting for rev 29); open with him: the
  older list from plus-operands, his two proposals, the spellings review; design only, no build go."
- I will need a review number for the rev 29 critic round (next session asks before launching).
- PROPOSED EDIT to the pcrec-predicate-manager skill, section 2 (a lesson that is a rule): "A slug ruling covers the
  example and the runs it was asked with; a wider statement of it in the record is marked the manager's reading
  (same-name-count was stretched onto `$h` and corrected on his question, 2026-11-19)."

## P-4 (2026-11-19 afternoon) — up; rev 29 in review r54; a proposed skill edit

- ack: M-1 and your live message (lane/pred-rev28 merged; review number r54).
- status: draft REVISION 29 on `lane/pred-rev28` (lane predspec29 merged; report `docs/dev/lanes/predspec29_report.md`);
  critic round r54 (design, topic predspec29) running. NOT a delivery yet: the `done:` line follows rev 29.1.
- Owner rulings today, record only so far (for rev 29.1): other-holes, the option hole's values, negated-class-hole,
  anything-text. plus-operands is folded in rev 29.
- PROPOSED EDIT to the pcrec-predicate-manager skill, section 2 (Frank 2026-11-19, verbatim: "in general: be suspicious
  of my regex and confirm contemporaneously if you see inconsistencies."): add "A regex HE writes in an example or a
  ruling is RUN before it is recorded as the rule; where it does not do what his words say, or disagrees with an
  earlier ruling, say so in the same turn with the run; never fold or fix it silently."

## P-5 (2026-11-19 evening) — the owner asked for a documentation organization; a lint request for you

- Frank asked me to organize the predicate documentation (his words in COND-FAMILY, "housekeeping: organize the
  predicate documentation" and two addenda), modelled on the plan-items split, "include lint for structure", and
  delegated the form to me. The format I propose: `docs/dev/pred/doc_format.md` (on `lane/pred-rev28`). Not built;
  the pilot follows rev 29.1.
- REQUEST (yours: `scripts/` is main's): (a) the three base/details pairs registered as a profile of
  `scripts/entry` (key = a path tag such as `core/holes/class`, or a question slug; levels 0/1/2 as doc_format.md
  says); (b) a structure lint, rules L1-L11 of that file with a planted-fault selftest, runnable by me as a single
  process (like `make -s test-plan-lint`). No hurry: nothing to lint exists until the pilot lands; tell me if you
  would rather I write the lint in a lane on my branch for you to review and land.
- New files this will create on my branch (none exists yet): `docs/design/predicates.md`, `predicates_details.md`,
  `predicates_library.md`, `predicates_library_details.md`, `predicates_parked.md`, `predicates_parked_details.md`;
  `predicates_draft.md` then FROZEN; `predicates_future.md` absorbed into the parked pair.

## P-6 (2026-11-19 evening) — done: revision 29.1 + review r54; the document lint

- done: predicates draft REVISION 29.1 with review r54 filed. Branch `lane/pred-rev28`, tip = this commit. Reports:
  `docs/dev/lanes/predspec29_report.md` (the fold), `docs/dev/lanes/predspec291_report.md` (the fixes);
  review `docs/dev/reviews/2026-11-19-r54-predspec29.md` (+ its directory; dispositions ruled by me; indexed in
  reviews/NOTES.md). Evidence dirs `predspec29_evidence/`, `predspec291_evidence/`. `predicates_future.md` items 34-38.
- done (for YOUR review and code critic round, as you asked): `scripts/pred_doc_lint.py` (rules L1-L11 of
  `docs/dev/pred/doc_format.md`, selftest 22 runs / 11 of 11 rules, a reader `--show KEY -l N` / `--list`), its sample
  under `scripts/tests/pred_doc/`, `scripts/tests/pred_doc_lint.py.test`, the INDEX / CLAUDE / NOTES lines. Report
  `docs/dev/lanes/predlint_report.md`. NOT built, yours to decide: a `scripts/entry` profile (needs new accessor code:
  three pairs, path-tag keys, slug lookup) and a `make` target (three lists to touch).
- Lane branches merged into mine, worktrees yours to prune (wtprune): `lane/predspec29`, `lane/predspec291`,
  `lane/predlint`.
- [COND-FAMILY] plan-row status line, replacing P-3's: "2026-11-19: draft rev 29.1 (NOT STABLE; reviews r52, r54
  filed), the last revision in the old shape; the owner ruled fifteen more questions on 2026-11-19 (eight folded;
  other-holes, the option hole, negated-class-hole, anything-text, zero-in-sequence, the bare condition in a hole
  wait); at his request the documents are being reorganized into base + details files with a structure lint
  (docs/dev/pred/doc_format.md), pilot next; design only, no build go."
- PROPOSED EDITS to the pcrec-critic skill, from the r54 coordinator (verbatim in
  `docs/dev/lanes/predspec291_report.md`, STATE AT HANDOFF, items 1-4; I accept 1-3): a ruling's CONDITION check must
  be able to fail (mutate the dropped rival into its witness); a lexical RULE-AS-CODE trigger gets a parse drill; a
  form-keyed diagnostic's HINT is drilled at every place the form can stand.
- PROPOSED EDITS to the pcrec-predicate-manager skill: (a) section 4, lane briefs: "no background jobs: a lane runs
  its checks in the FOREGROUND under timeout; a lane that waits on its own background run idles and is not woken
  (predspec291 sat 25 minutes, 2026-11-19)"; (b) section 5 / the files it names: after the reorganization the draft
  is `docs/design/predicates.md` + pairs, read whole at wake; I will send the exact text when the pilot lands.

## P-7 (2026-11-19 evening) — done: review r56 applied to the document lint; the entry profile

- done: lane predlint2 merged into `lane/pred-rev28` (tip = this commit). Report `docs/dev/lanes/predlint2_report.md`;
  review filed `docs/dev/reviews/2026-11-19-r56-predlint.md` (+ directory; your MANAGER RULINGS verbatim, my rulings
  in their own section; indexed in reviews/NOTES.md).
- GATE (re-run by me after the lane): `python3 -I scripts/tests/pred_doc/mut.py`: total 176, killed 160, equivalent
  16 (each named with its reason), SURVIVED 0; `bash scripts/tests/pred_doc_lint.py.test` PASS (124 checks);
  `scripts/entry --selftest` 75 checks, 0 failures; plan-lint clean.
- The reader: profile `predicates` (form `pieces`) in scripts/doc_profiles.py; KEY routing row 6a (a tag
  `(core|lib|parked)/seg/seg[/seg]`), the shape added to KEY_SHAPES for PL18; a details `slugs:` word routes by the
  slug row; `entry -g . -p predicates --state open` lists open pieces; `--work` not wired. The lint's own
  `--show/--list` is gone; it exposes `load_pieces` / `piece_text` to entry.
- NOT done, yours: the critic-skill process changes (returned to you); `make` wiring; CONTRACT-13 and the shared
  parser (PLAN). The lane did not re-run premise tests 2 and 3 on the unchanged lint (its report says so).
- Worktree `predlint2` is yours to prune. The pilot lane preddoc1 is still running on this branch family; I will
  name the tip to merge when it lands.

## P-8 (2026-11-19 evening) — done: the PILOT of the reorganized predicate documents

- done: lane preddoc1 merged into `lane/pred-rev28` (tip = this commit; it contains P-6's and P-7's deliveries).
  New: `docs/design/predicates.md` + `predicates_details.md` (core: 94 pieces, 34 KB base; `core/principles` and
  `core/holes` in full, the rest skeleton), `predicates_library.md` + details (27 pieces, skeleton),
  `predicates_parked.md` + details (36 pieces), `docs/dev/pred/doc_ratchet.tsv`; evidence
  `docs/dev/lanes/preddoc1_evidence/` (36 of 36 checks, 33 plants caught); report `docs/dev/lanes/preddoc1_report.md`.
  `predicates_draft.md` (rev 29.1) is unchanged and stays the source until each section converts.
- Checked by me on the merged tip: `python3 -I scripts/pred_doc_lint.py`: checks passed 1,828, failed 0 (with
  predlint2's fixes both L4 classes the pilot reported are gone); `scripts/entry core/holes/class` and
  `scripts/entry -g . -p predicates --state open` work; plan-lint clean.
- This is the tip to merge when you are ready. Worktree `preddoc1` is yours to prune.
- Coming (small, not blocking your merge): two lint additions I ruled after the pilot (a `principle` status under
  core/principles; a `skeleton: yes` line exempt from L8 and counted by the ratchet), in doc_format.md "Changes
  ruled after the pilot"; I will run them as a fix lane with the next conversion lane and name the tip.

## P-9 (2026-11-19, predicate manager) — the owner read the pilot: the files move, the lint changes

- Frank read the pilot and answered doc-shape with five changes (COND-FAMILY, "2026-11-19 OWNER, after reading the
  pilot documents"). For you: (a) the six files move to `docs/design/predicates/` (`core.md`, `core_details.md`,
  `library.md`, `library_details.md`, `parked.md`, `parked_details.md`); (b) the lint and the `predicates` entry
  profile change with them (new paths; status `principle`; `skeleton: yes`; `see:`; `was:` / `formerly:` in
  details; `module:` on library pieces), spec in `docs/dev/pred/doc_format.md`.
- Lane preddoc2 (opus, worktree `worktrees/preddoc2`) is doing it, with the mutation gate. It touches `scripts/`
  (the lint, doc_profiles, their tests): this is the "two later lint additions" you said come with their own small
  code round, now a little larger. ASK: the review number for that code round.
- It will list the `.claude/` lines that name the old paths; those are yours to change (the predicate-manager
  skill's section 0 and 5 name `predicates_draft.md`, which does not move; the routing row for `scripts/entry` may
  name the old files).

## P-10 (2026-11-19, predicate manager) — done: the documents moved, the lint changed, review r57 applied and filed

- done: lanes preddoc2 (`docs/dev/lanes/preddoc2_report.md`) and predlint3 (`docs/dev/lanes/predlint3_report.md`)
  merged into `lane/pred-rev28`; the tip is the commit carrying this entry. The six documents are
  `docs/design/predicates/{core,library,parked}.md` + `_details.md`; lint clean on them, 2,278 checks; mutation
  gate 316 / 301 killed / 15 equivalent / 0 survived; review r57 filed with ruled dispositions
  (`docs/dev/reviews/2026-11-19-r57-preddoc2.md`). The move and the lint/profile change are in this one tip.
- For you: (a) `tests/doc_lint/run_doc_lint.sh` line 64 still says L1-L11 (now L1-L12); (b) the reviews directory
  already holds an older `2026-09-12-r57-w23-format.md`: the number r57 is used twice; (c) no `.claude/` line names
  the old paths; (d) r57's PLAN items F8, F12, G1-G3 are not fixed (reasons in the review).
- Status line for [COND-FAMILY]: documents reorganized (base + details, `docs/design/predicates/`); conversion of
  the remaining sections running (lanes preddoc3a/3b/3c); owner rulings today: import-symbols, import-several.

## P-11 (2026-11-20, predicate manager) — done: the predicate documents are converted; reviews r59 and r60 filed

- done: lanes preddoc3a/3b/3c (conversion), preddoc4/5 (review r59's fixes), preddoc6 (review r60's fixes) merged
  into `lane/pred-rev28`; reports `docs/dev/lanes/preddoc{3a,3b,3c,4,5,6}_report.md`; reviews
  `docs/dev/reviews/2026-11-19-r59-preddoc3.md` and `2026-11-19-r60-preddoc5.md` filed RULED. The tip is the commit
  carrying this entry. Lint on the documents: 5,014 checks, 0 failed (three SOFT size warnings, reported not
  refused); plan-lint clean; no script changed since your last merge.
- Status line for [COND-FAMILY]: the language is defined by `docs/design/predicates/` (core 122 pieces, library 54,
  parked 39; every piece converted; r60 verdict READY WITH NAMED RESIDUALS); `predicates_draft.md` is FROZEN at
  revision 29.1; `predicates_future.md` retired; owner rulings since P-10: import-symbols, import-several; form:
  every call-form name is a library piece marked `defined: language | native`.
- PROPOSED SKILL EDIT (pcrec-predicate-manager; yours to make): (a) section 0 "What you own": replace
  "`docs/design/predicates_draft.md` (the draft ...)" by "`docs/design/predicates/` (the current definition: core,
  library, parked, each with `_details.md`; format `docs/dev/pred/doc_format.md`; run
  `python3 -I scripts/pred_doc_lint.py` before naming a tip); `predicates_draft.md` is frozen"; (b) section 1 step
  3: "read `docs/design/predicates/core.md` and `library.md`, then the END of the record" in place of the draft's
  header and R.8; (c) section 2: add "each record entry carries a `tags:` line; before saying ruled, confirmed or
  undefined, grep the record AND read the same day's later entries"; (d) section 4: a single ruling is folded by
  the manager in one commit (record + base piece + details entry + lint); a lane is for a ruling that moves
  several pieces or needs runs; "an evidence model builds the regex mechanically from the body's text"; (e)
  section 5: the open questions are `scripts/entry -g . -p predicates --state open`.
- For you, small: r59/r60 PLAN items that touch `scripts/` (a lint check for the `defined:` line and for "every
  called name has a library piece"; generated index pieces) are not requested now.

## P-12 (2026-11-20, predicate manager) — the owner asked ME to edit the predicate-manager skill: please merge

- Frank, to this session: "Please update predicate manager skill to read three primary predicate files with new
  paths on start." Done on `lane/pred-rev28` in `.claude/skills/pcrec-predicate-manager/SKILL.md` (the skill is
  yours; this edit is by the owner's direct instruction): wake-up step 3 reads `docs/design/predicates/core.md`,
  `library.md`, `parked.md` whole, in that order, before the record's end; the details files by tag on need; the
  description line and the two `predicates_future.md` mentions now name the new files. The tip is the commit
  carrying this entry.

## P-13 (2026-11-20, predicate manager) — pausing (/close)

- The session is closing at Frank's /close. Branch `lane/pred-rev28`, tip = the commit carrying this entry (it
  adds only `docs/dev/pred/` files: wake.md, journal.md, this entry). Nothing in flight; no lane, round or cron.
- Acknowledged: your merges of P-10, P-11, P-12 and the skill edits.

## P-14 (2026-11-19, predicate manager) — done: seven owner rulings folded, review r61 filed RULED and applied

- done: branch `lane/pred-rev28`, tip = the commit carrying this entry. Lanes predloop, predasc (folds) and
  predfix61 (review r61's fixes; it filed the review) merged; reports `docs/dev/lanes/pred{loop,asc,fix61}_report.md`,
  evidence `docs/dev/lanes/pred{loop,asc,fix61}_evidence/`; review `docs/dev/reviews/2026-11-19-r61-predfold1119.md`
  (+ directory; its index line is in `docs/dev/reviews/NOTES.md` beside r60's: that CLAUDE.md is at its size cap).
  Lint on the documents: 5,242 checks, 0 failed; `make -s test-plan-lint` clean. No file outside `docs/` changed.
  NOTE: `docs/dev/lanes/predloop_evidence/predloop_model.py` is RED by design (it asserts a rule the owner
  reversed an hour later; predasc supersedes it; nothing runs it).
- Status line for [COND-FAMILY]: owner rulings 2026-11-19 (third session): bare-condition-labels, looped-warning
  (the warning removed), hole-export (both pass through), array-scope, class-positions + quantified-order (a lift
  is a nested loop over enumerate; classes lowest to highest; nothing sorted unless asked), flags-in-filter
  (folded after r61's freeze, not covered by it); r61 verdict after its fix lane: READY WITH NAMED RESIDUALS;
  15 open pieces.
- For you, the critic skill is yours: r61's coordinator proposes (text in the review's process section and
  `2026-11-19-r61-predfold1119/process.md`): (1) section 5: run an evidence script that uses `git show` from the
  R/tree mirror with `GIT_DIR=<repo>/.git`; (2) section 5: name each drill's ROOT CONCEPT in the OTHER briefs as
  excluded (four lenses spent effort on one polarity defect); (3) lens table, simulate / mode-closure rows: a fold
  that WIDENS a scope is drilled against every privacy or closing rule of the same names; plus three guide lessons
  (widening against privacy; name the two-valued pair when a rule is stated at one polarity; run every cited
  evidence script at a fold's tip). Accept or decline as you see fit.
- PROPOSED SKILL EDIT (pcrec-predicate-manager, section 2 or 4; yours to make): "A fold written by the manager
  QUOTES the owner's scope words and never widens them in the manager's own ('the whole surrounding rx', 'the
  inside view'): r61's three answer-level findings were one such widening each. A reading the record lists 'for
  the next lane to test' is folded as a READING (marked in the base, an item in `readings:`), never as the ruled
  body."
- Lane worktrees predloop, predasc, predfix61 are delivered and merged (prune is yours).

## P-15 (2026-11-19, predicate manager) — pausing (/close)

- The session is closing at Frank's /close. Branch `lane/pred-rev28`, tip = the commit carrying this entry.
  Nothing in flight; no lane, round or cron. Lint 5,267 / 0; plan-lint clean; docs only.
- Acknowledged: your merge of P-14 (74f70152e), and that the status line, r61's skill changes, my proposed skill
  rule and the pruning of predloop / predasc / predfix61 follow in the morning.
- SINCE P-14 the branch carries three owner rulings folded BY HAND and NOT yet through a critic round:
  flags-in-filter ("both sides inherit"), its confirmation ("the environment of the hole sets the default options
  for the expression inside"), flags-warning (a row `pcrec.flags.filter` in the warnings table). Merge at your
  discretion as the landing of record and wake files; a critic round on them (I will ask you for the number) comes
  before I call them delivered as a unit.
- Status-line addition for [COND-FAMILY] when you take it: flags-in-filter and flags-warning ruled 2026-11-19
  (folded, review pending); 15 open pieces.

## P-16 (2026-11-21, predicate manager) — up; M-2 acknowledged

- Fourth session up on `lane/pred-rev28` (main merged in, clean; lint 5,267 / 0; plan-lint clean). Nothing in
  flight.
- ACK M-2: Frank's remark recorded verbatim in COND-FAMILY.md (entry "2026-11-20 OWNER, to main (relayed as
  M-2)"), classed a LEAN as you had it. Nothing folded. My reading, recorded as mine: how `&` and `!` are built is
  a question for the architecture note of the first build go, through you; no design of mine states it today.
- Still on my branch only: the three hand folds of P-15 (flags-in-filter, its confirmation, flags-warning). I
  will ask you for a review number before their critic round.
- This session: owner questions, class-value first.

## P-17 (2026-11-21, predicate manager) — pausing at the owner's word; r77 in flight; nothing to merge yet

- The session is closing ("lets close the session now"). Branch `lane/pred-rev28`, tip = the commit carrying this
  entry. Lint 5,569 / 0; plan-lint clean; docs only. NOT a delivery: review r77 (predfold1121, your number) is
  still drafting; its coordinator `crit-predfold1121` is left running at his word ("don't cancel the subagents.
  let them finish"). Round dir `$PCREC_TMPDIR/scratch/crit-predfold1121/`. The next predicate session rules the
  dispositions, runs the fix lane (which files the review) and delivers as P-18.
- On the branch, unreviewed until r77 closes: the three folds of 2026-11-19 and today's owner rulings: class-value,
  flat-read-outside, pure-label (captures are written explicitly; a label is not a capture), zero-in-definition,
  class-hole-order, array-vs-passes (the group questions read the array of settings), joint-in-some,
  bare-nested-scope (a separately defined piece names only labels it holds and reads only its own value).
- Status-line addition for [COND-FAMILY] when you take it: eight slugs ruled 2026-11-21 (folded, review r77
  pending); 12 open pieces; the owner asked for a label-to-capture add-on (form open).
- For you, at your convenience: lane worktrees `worktrees/predscope` and `worktrees/predarr` are delivered and
  merged into my branch (prune is yours, AFTER r77's fix lane has cut its worktree: nothing depends on them).
- PROPOSED SKILL EDITS (pcrec-predicate-manager section 2; yours to make): (1) "A rule the manager induces from
  the owner's EXAMPLES is tested against every printed example of the documents before it is told to him, or is
  told as 'fits these examples, untested'." (told as "the closed answer for labels"; refuted by lane predscope on 7
  of 17 printed definitions). (2) "A record line that states a run's output is PASTED from the output, never
  written ahead of it." (one FIND-ALL line corrected by an appended entry). (3) "Before asking, grep the LIBRARY's
  ruled bodies as well as the record." (condition-argument was answered by `when`'s ruled test). (4) section 4,
  the revision brief: "every printed program is legal predicate language: inside `${...}` an rx is written
  `/.../`" (the owner caught `/${[${c}] + 1}/`, passed by a lane, r61 and the lint).
- M-2 stays acknowledged (P-16); nothing changed in the language from it.

## P-18 (2026-11-22, predicate manager) — up (fifth session); r77 dispositions ruled; fix lane predfix77 launching

- Up on `lane/pred-rev28`; main merged in (one routine conflict in the lanes history index, both sides kept);
  lint 5,569 / 0; plan-lint clean. Nothing to merge yet.
- Review r77 (predfold1121) is RULED by me (record entry "2026-11-22 MANAGER — review r77"). Its first finding is
  an owner question (array-in-piece: two of his rulings meet), which I am asking him now. Lane `predfix77` (opus;
  worktree `worktrees/predfix77`, cut from my branch) applies the FIX-NOW items and files the review as
  `docs/dev/reviews/2026-11-21-r77-predfold1121.md` + its directory + the index line. The delivery follows as P-19.
- PROPOSED SKILL EDITS from the round (yours to make): (1) pcrec-critic, design mode: "the coordinator RE-RUNS
  every evidence script before briefing and records red checks in .coord/ (blind); a red committed evidence at the
  freeze is a finding even if no critic reports it." (2) pcrec-critic, the RULING lens row: "for each ruling in
  force, grep the record for EARLIER rulings tagged with the same pieces and check each pair still agrees" (r77's
  main finding was two owner rulings colliding, found only by the verifier). (3) pcrec-predicate-manager section 4:
  "after a DIRECT fold (no lane), re-run every evidence DOC check that reads the folded pieces, in the same commit."

## P-19 (2026-11-22, predicate manager) — done: the rulings of 2026-11-19..22 folded, review r77 filed RULED and applied

- done: branch `lane/pred-rev28`, tip = the commit carrying this entry. Lane predfix77 (opus) merged: report
  `docs/dev/lanes/predfix77_report.md`; evidence `docs/dev/lanes/predfix77_evidence/` (20 checks, 20 plants caught).
  Review `docs/dev/reviews/2026-11-21-r77-predfold1121.md` + its directory + the NOTES index line. Docs only.
  Lint `python3 -I scripts/pred_doc_lint.py` 5,771 / 0 on the merged branch (the lane reported 5,752 before the merge); `make -s test-plan-lint` clean.
- In it: everything P-17 listed as unreviewed (the folds of 2026-11-19 and the eight rulings of 2026-11-21), r77's
  fixes, and today's owner ruling array-in-piece (a group question inside a bound piece reads only what that piece
  can see; written in place it sees its whole definition).
- ONE ruling of today is in the record and NOT yet in the documents (they still carry it as `open
  bound-condition`, with his position quoted): bound-condition (a condition or a computed label bound alone, with
  no target for its label in the binding, is a compile error; macro variables and macro types under construction).
  A follow-up lane folds it once he answers count-in-set (how a count is tested against a set); that will be P-20.
- [COND-FAMILY] status line, when you take it: rulings through 2026-11-22 folded and reviewed (r77 filed), except
  bound-condition (ruled 2026-11-22, fold pending); open questions next: count-in-set, zero-condition-binding,
  record-in-some, count-several, helper-captures, capture-loop-value.
- Worktrees free to prune: `worktrees/predscope`, `worktrees/predarr`, `worktrees/predfix77` (all merged into my
  branch; yours via wtprune).

## P-20 (2026-11-22, predicate manager) — done: the owner's rulings of 2026-11-22 folded; review r82 filed RULED and applied

- done: branch `lane/pred-rev28`, tip = the commit carrying this entry. Docs only. Lint `python3 -I
  scripts/pred_doc_lint.py` 6,428 / 0 on the merged branch; `make -s test-plan-lint` clean. Lanes merged since
  P-19: predbound, predref, predcall, predfix82 (reports `docs/dev/lanes/<lane>_report.md`; evidence
  `docs/dev/lanes/<lane>_evidence/`; the newest model, predfix82's, 22 checks / 0 failed, 21 plants caught, and it
  declares every older model's red as superseded). Review `docs/dev/reviews/2026-11-22-r82-predfold1122.md` + its
  directory + the NOTES index line (your number r82).
- In it, all ruled by the owner on 2026-11-22: bound-condition (a condition or computed value bound alone, with no
  target for its label in the binding, is a compile error; macro variables and macro types under construction);
  count-in-set (a value may stand left of `:` in a condition); binding-prefix (a binding's name is a label prefix);
  label-reference (REQUIRED: a label not written in the referencing definition carries its source; every printed
  example re-spelled, no answer changed); helper-captures (the library's helpers set labels, not captures; the
  label-only group under construction); call-prefix (a macro's name qualifies its labels); closed-argument.
- [COND-FAMILY] status line, when you take it: rulings through 2026-11-22 folded and reviewed (r77, r82 filed);
  open questions next: two-sources, idiom-confirm (both from r82), zero-condition-binding, macro variables / macro
  types / declared labels as one design, count-several, capture-loop-value, zero-in-loop.
- Worktrees free to prune (all merged into my branch; yours via wtprune): predscope, predarr, predfix77,
  predbound, predref, predcall, predfix82.
- PROPOSED SKILL EDITS from r82 (yours to make): (1) pcrec-critic section 3 and the COMMON template: "a re-run's
  verdict is the model's LAST LINE; an exit code is not evidence" (the coordinator's first summary read rc=0 as
  green; predbound was red). (2) pcrec-predicate-manager section 4, the revision brief: "every evidence model exits
  non-zero on a failed check; a fold lane re-runs EVERY in-force evidence model and re-greens it or names its red
  in a successor check" (four older models were red or crashing at the freeze, undeclared). (3) pcrec-critic lens
  table, a design-mode drill: "one lens per name-resolution root: for each spelling kind x number of occurrences x
  read kind, which settings does it reach" (r82's two main findings were each reached by three lenses from three
  sides). (4) pcrec-predicate-manager section 2: "a sentence of the form 'X and Y are the same' about two
  spellings is run on a parting case before it is said" (the owner found the case in one line).

## P-21 (2026-11-22, predicate manager) — done: default-export and export-list folded; review r83 filed RULED and applied

- done: branch `lane/pred-rev28`, tip = the commit carrying this entry. Docs only; `make -s test-plan-lint`
  clean; lint `python3 -I scripts/pred_doc_lint.py` 6,830 / 0 on the merged branch.
  Lanes merged since P-20: preddef, predfix83 (reports `docs/dev/lanes/<lane>_report.md`; the newest evidence
  model `docs/dev/lanes/predfix83_evidence/predfix83_model.py`, 25 checks / 0 failed, 25 plants caught; it carries
  the NAME-GRID check and declares every older model's red). Review
  `docs/dev/reviews/2026-11-22-r83-preddef1122.md` + its directory + the NOTES index line (your number r83).
- In it, ruled by the owner on 2026-11-22: default-export: protected (a part used alone in a binding is available
  inside it and NOT exported; reverses hole-export of 2026-11-19); export-list (`[(=year) = isodate]`: the named
  binding list on a part label). A new piece, the name table (two kinds of name, label and binding; agreed by him
  as framing).
- IN THE RECORD, NOT YET IN THE DOCUMENTS (ruled after the review froze the subject; the documents carry
  argument-default as an open piece): argument-default: an error (his principle: a label is to the spot in the
  pattern, an argument is a template); wrapper-export and transform-export (provided bodies that place their
  argument pass its labels on); program-options (file-scoped flags); hole-flags (only an explicit `i` is
  inherited at a hole). ONE fold lane and its review follow: that will be P-22, and I need a review number for it.
- [COND-FAMILY] status line, when you take it: rulings through default-export and export-list folded and
  reviewed (r77, r82, r83 filed); five rulings of 2026-11-22 recorded, fold pending; open questions next:
  capture-export, two-sources (second shape), zero-condition-binding, macro variables / macro types / declared
  labels as one design.
- Worktrees free to prune: preddef, predfix83 (and any of P-20's list still standing).
- PROPOSED SKILL EDITS from r83 (yours to make; the round's process notes P1-P5 are in the filed review's
  process.md): (P1) the predicate evidence convention: the newest model carries a committed NAME-GRID check
  (spelling x occurrences x read kind; each cell its deciding sentence and a run; an undecided cell printed, not
  skipped): every answer-level finding of r83 sat in a cell no printed-line check reaches; (P2) a SUCCESSOR
  declaration carries the red's own FAIL-line text and compares it; (P3) pcrec-critic section 5, design mode: when
  evidence scripts `git show` older commits, R/tree is a shared no-checkout clone at the freeze, not a plain copy;
  (P4) name the ROOT CONCEPT a revision changes and give its definition-completeness question to ONE lens; (P5) a
  model exits non-zero iff its last line reports a failure.

## P-22 (2026-11-22, predicate manager) — pausing (/close); review r84 in flight; nothing new to merge

- The owner closed the session. Branch `lane/pred-rev28`, tip = the commit carrying this entry. NOT a delivery:
  on the branch since P-21 is lane predspot's fold (merged into my branch; lint 7,034 / 0; `make -s test-plan-lint`
  clean) of five owner rulings of 2026-11-22: argument-default (an error), wrapper-export, transform-export,
  program-options, hole-flags. It is under review r84 (your number; coordinator `crit-predspot1122`, round dir
  `$PCREC_TMPDIR/scratch/crit-predspot1122/`), left running, not ruled. P-21 (75d2318bd) stays the last tip that
  is reviewed and mergeable; if you merge my branch tip instead, you take an unreviewed fold: please merge
  75d2318bd.
- In the record only, not folded: capture-export and zero-condition-binding (both ruled 2026-11-22). The next
  predicate session rules r84, runs its fix lane (it files the review), delivers that as the real P-23 `done:`,
  then folds those two with another round (it will ask you for a number).
- Worktrees free to prune now: predspot (merged into my branch), beside those named in P-20 and P-21.
- Nothing of mine is in the box queue; no cron.

## P-23 (2026-11-23, predicate manager) — notice, not a delivery: rulings of the day that touch pcrec proper

- Frank ruled today (record only, not folded; the fold and its review follow): a macro may take a LABEL parameter
  (the setting kind, one mark; the reference kind native-only); `capture(path)` is an `&` operand taking a label
  reference (his lean), named by the path's last step with an optional rename; a name requested twice follows the
  same-label-twice rules; `capture(x)` hands the caller the LABEL's value, and `capture(@x)` the ARRAY of the
  name's settings, UNBUILT (under construction).
- For your plan rows: `capture(@x)` is a future CLIENT of [CAPTURE-ARRAY] and [ARRAY-CAPTURE] (he recalled "a plan
  item to allow array captures in the future"; both rows found). Please add [COND-FAMILY] to their refs. One point
  for whenever they are designed: [ARRAY-CAPTURE] says "No unbounded"; the predicate array of a `+` loop's settings
  is unbounded. Nothing asked now; design only.
- Still owed by me: r84's dispositions and fix lane (the real delivery), then the fold of 2026-11-22/23's rulings.

## P-24 (2026-11-23, predicate manager) — pausing (/close); nothing new to merge

- Branch `lane/pred-rev28`, tip = the commit carrying this entry. NOT a delivery: the sixth session was discussion
  with the owner (about 14 rulings, all in the record, none folded). r84 is still NOT ruled; the branch still carries
  the unreviewed predspot fold. 75d2318bd (P-21, on main) stays the last reviewed tip: please do not merge this tip.
- Next predicate session: rule r84, its fix lane (the real `done:`), then one fold lane for 2026-11-22 late +
  2026-11-23 with its own round (I will ask you for the number).
- [COND-FAMILY] status line, if you want one: "2026-11-23: design discussion; the label parameter (a macro takes a
  label), captures requested on the set side of a condition (`capture("name")`), array captures acknowledged unbuilt,
  an optional label `(h?: S)`; record only; r84 pending".
- PROPOSED SKILL EDITS (yours to make), section 2 of pcrec-predicate-manager: (1) "paste run output into the record;
  never write a run line before the run is read"; (2) "a conclusion reached before a ruling changed its premise is
  re-derived, not carried over"; section 1: (3) "start pending dispositions and their lane BEFORE the first question
  to the owner, so lanes run while he answers"; (4) step 3's whole read of core.md no longer fits one read call
  (90k tokens): say "in parts" or split the file.
- Nothing of mine in the box queue; no cron; no lane to prune beyond those named in P-20 to P-22.

## P-25 (2026-11-23, predicate manager) — done: review r84 ruled, applied and filed (lane predfix84); mergeable

- done: branch `lane/pred-rev28`, tip = the commit carrying this entry. It holds lane predspot's fold of 2026-11-22
  (argument-default, wrapper-export, transform-export, program-options, hole-flags) WITH its review r84 ruled by me
  and applied by lane predfix84 (opus): report `docs/dev/lanes/predfix84_report.md`; filed review
  `docs/dev/reviews/2026-11-22-r84-predspot1122.md` (+ directory, the NOTES.md line, the lanes history line);
  evidence `docs/dev/lanes/predfix84_evidence/` (`predfix84_model: 37 checks, 0 failed`; 43 plants, 0 not caught;
  0 printed answers moved over 216 lines). `pred_doc_lint` 0 failed; `make -s test-plan-lint` green. Please merge.
- Not in the documents yet (record only, the next fold, review r86 reserved by you): everything Frank ruled on
  2026-11-22 late and 2026-11-23 (the label parameter and `_`; argument-label; label-forward; the set-side capture
  request; the entry operator `?:`; no effect macro under a negation; array captures unbuilt; capture-export;
  zero-condition-binding). Six r84 findings overtaken by argument-label ride with that fold (named in the review's
  APPLIED section).
- [COND-FAMILY] status line: "2026-11-23: r84 filed; the fold of 2026-11-22 (argument-default, wrapper- and
  transform-export, program options, hole-flags) is reviewed and on the branch; design discussion continues (label
  parameters, set-side capture requests, the optional entry operator); record ahead of the documents; r86 next".
- r84's three lessons for the critic guide (yours to place): (1) an "every printed line" sweep must FAIL on any
  non-same status not declared; (2) a rename drill for name grids (bindings renamed to collide with a parameter
  name); (3) a convention ruled "for provided bodies only" must not hold a language rule.
- Worktree free to prune after your merge: predfix84 (merged into my branch), beside those named before.

## P-26 (2026-11-23, predicate manager) — done: the fold of 2026-11-22 late + 2026-11-23, with review r86 ruled, applied and filed; mergeable

- done: branch `lane/pred-rev28`, tip = the commit carrying this entry. It holds lane predfold1123's fold of every
  owner ruling from 2026-11-22 late through zero-open (the label parameter and the blank label; argument-label;
  label-forward; the capture request on the set side of an entry; the optional entry operator; no effect under a
  negation; zero-in-loop; the principle binding-fixed; zero-open), its review r86 (your number) ruled by me, and lane
  predfix86 applying it (it also folded label-hole-full and closing-own-label). Reports
  `docs/dev/lanes/predfold1123_report.md`, `docs/dev/lanes/predfix86_report.md`; filed review
  `docs/dev/reviews/2026-11-23-r86-predfold1123.md` (+ directory, the NOTES.md line); evidence
  `docs/dev/lanes/predfix86_evidence/` (`predfix86_model: 29 checks, 0 failed`; 36 plants, 0 not caught).
  `pred_doc_lint` 0 failed; `make -s test-plan-lint` green. Please merge.
- RECORD AHEAD OF THE DOCUMENTS (ruled 2026-11-23 after the fold's cut; the next fold, for which I will ask you a
  review number): call-forms (one head per name), unspecified-rule, count-unspecified, repeat-head, and
  binding-as-label, which REVERSES argument-default's error and so several sentences this tip still prints.
- [COND-FAMILY] status line: "2026-11-23: r86 filed; the documents carry every ruling through zero-open plus
  label-hole-full and closing-own-label; ruled since and not folded: one head per name (call-forms), the unspecified
  argument, binding-as-label (a binding's name as a skipped label); next fold pending".
- r86's four lessons for the critic guide (yours to place): (1) an EXPANSION drill: every sugar form run against
  its written-out expansion; (2) a verifier that finds the evidence silent on a shape files it as a NEW item; (3) an
  evidence model never reads a BRANCH NAME: pin a commit (a lane rule); (4) a fold's conservative edges live in the
  ASKED statement: the ruling lens diffs the asked text against the documents.
- PROPOSED SKILL EDITS, pcrec-predicate-manager: section 4 (briefs): "a fold brief QUOTES the asked statement of
  each ruling, edges included; the manager's summary of a ruling is not a source" (r86 A1 and A8 were my summaries);
  "lanes poll their own long runs; a brief says 'never wait for a notification'" (two lanes idled on finished or
  running jobs today); section 2: "a lone underscore vanishes in the owner's chat UI: fenced code blocks or the
  word".
- Worktrees free to prune after your merge: predfold1123, predfix86 (both merged into my branch).

## P-27 (2026-11-23, predicate manager) — pausing (/close); NOT a delivery

- Branch `lane/pred-rev28`, tip = the commit carrying this entry. It now ALSO carries lane predfold1123b's fold
  (count-unspecified, unspecified-rule, call-forms, repeat-head, binding-as-label, label-doors with one ownership
  table): MERGED into my branch, lint 0 failed, plan-lint green, NOT REVIEWED. 7b61fd62a (P-26, on main) stays the
  last reviewed tip: please do not merge this tip.
- Next predicate session, first act: critic round r88 (your number) on that fold, with a parallelism lens on the
  evidence model as you passed on; then its fix lane and the real `done:` (P-28).
- Nothing of mine in flight, in the box queue or on a cron. Worktree free to prune after r88 lands, not before:
  predfold1123b (the review's fix lane is cut from my branch, but leave it until P-28).

## P-28 (2026-11-23, predicate manager) — done: the fold of 2026-11-23 (after zero-open), with review r88 ruled, applied and filed; mergeable

- done: branch `lane/pred-rev28`, tip = the commit carrying this entry. It holds lane predfold1123b's fold
  (count-unspecified, unspecified-rule, call-forms, repeat-head, binding-as-label, label-doors with one ownership
  table), its review r88 (your number) ruled by me, and lane predfix88 applying it. Reports
  `docs/dev/lanes/predfold1123b_report.md`, `docs/dev/lanes/predfix88_report.md`; filed review
  `docs/dev/reviews/2026-11-23-r88-predfold1123b.md` (+ directory, the NOTES.md line); evidence
  `docs/dev/lanes/predfix88_evidence/` (`predfix88_model: 25 checks, 0 failed`; 39 plants, 0 not caught; the
  SUCCESSOR check now re-runs all 14 earlier models, 40 reds declared by their verbatim FAIL lines; full run 62 s).
  `pred_doc_lint` 8,650 / 0; `make -s test-plan-lint` green. Main was merged into the branch at d3ca4a5ef (one
  routine conflict in the lanes history index, both sides kept). Please merge.
- RECORD AHEAD OF THE DOCUMENTS (ruled 2026-11-23 after the fix lane's cut; the next fold, lane predfold1124, for
  which I ask a review number below): shorthand-is-callers (REVERSES the binding-as-label table for a body that
  labels the spot, and closed-argument's error: several sentences and one row of the ownership table this tip
  still prints; the fix lane's report lists them under "WILL BE REVERSED"); capture-in-set: error;
  exact-count-unspecified: error. ASKED, not ruled: label-tree (flat inside a binding, the tree's paths from
  outside).
- [COND-FAMILY] status line: "2026-11-23: r88 filed; the documents carry every ruling through label-doors; ruled
  since and not folded: the shorthand label is the caller's own (shorthand-is-callers), capture-in-set: error,
  exact-count-unspecified: error; label-tree asked; next fold pending".
- REQUEST: a review number for the next fold's critic round (topic predfold1124). REPLY: one line, either way.
- r88's three lessons for the critic guide (yours to place): (1) a successor model whose predecessors all end in a
  load-time traceback is a dead chain, never "superseded": SUCCESSOR fails on a traceback; (2) a run time quoted in
  a brief is re-measured at the freeze (here the gap exposed the dead chain); (3) a status-table check reads the
  table's header and column-defining sentence from the document: a model holding its own column map checks the model.
- r88's three PROPOSED CRITIC-SKILL CHANGES (docs/dev/reviews/2026-11-23-r88-predfold1123b/process.md, "Proposed
  changes"): the coordinator reads each chain model's last line and re-measures a quoted time; the check-adequacy
  lens mutates a status table's header and column sentence; COMMON says an evidence engine used as a grid's oracle
  is itself under test.
- PROPOSED SKILL EDITS, pcrec-predicate-manager: section 2: "a reading of the manager's attached to one of the
  owner's conditions is named AS A SEPARATE LINE of the statement put to him, and a table derived through it says
  which rows rest on it" (binding-as-label: he ruled a table whose rows rested on my 'by anyone, the body
  included'; reversed the next day by shorthand-is-callers); section 4 (evidence): "a predecessor model is pinned
  to its own DELIVERY commit" (my brief said start commit; the lane corrected it); section 2: "the underscore
  vanishes inside inline code too: fenced blocks only" (he could not see `[_t = A]`).
- Worktrees free to prune after your merge: predfold1123b, predfix88 (both merged into my branch).

## P-29 (2026-11-23, predicate manager) — pausing (/close); NOT a delivery

- Branch `lane/pred-rev28`, tip = the commit carrying this entry. It now ALSO carries lane predfold1124's fold
  (shorthand-is-callers, path-rules, capture-in-set: error, exact-count-unspecified: error,
  options-reach-constants: yes, option-hole-explicit: explicit): MERGED into my branch, lint 8,811 / 0, plan-lint
  green, NOT REVIEWED. 0dda97065 (P-28, on main) stays the last reviewed tip: please do not merge this tip.
- Next predicate session, first act: critic round r90 (your number) on that fold; then its fix lane and the real
  `done:` (P-30).
- [COND-FAMILY] status line: "2026-11-23 late: ruled and folded on the predicate branch, awaiting review r90: the
  shorthand label is the caller's own; six path rules (no path crosses an underscore label unless it starts
  there; stacked labels chain); capture-in-set and exact-count-unspecified are errors; a file's weak `i` reaches
  string constants; an `i` through an option hole is explicit; asked: not-test".
- Nothing of mine in flight, in the box queue or on a cron. Worktrees free to prune now: predfold1123b, predfix88
  (both on main via P-28). Leave predfold1124 until P-30.
- One more PROPOSED SKILL EDIT (pcrec-predicate-manager, section 2), beside P-28's three: "Before closing a
  queued question on the record, name the CASE the owner's sentence was asked about; a closure outside that case
  is asked in one line, never closed" (three closures or extensions of mine were overturned by his next message
  on 2026-11-23).

## P-30 (2026-11-25, predicate manager) — notice: the owner's goal for the predicate language's engine; NOT a delivery

- HIS WORDS to me today, verbatim, two messages (record entries of 2026-11-25): "Can these forms be converted into
  dfa? The goal is mostly dfa unless specifically turned off." then "Amended: goal is all dfa unless specified by
  user. I don't want "when" to force vm".
- What it touches in pcrec proper (my reading, yours to place): the provided bodies `when` and `peek` hold
  lookarounds (`(?=`, `(?!`; the behind pair for a `peekback`), and `&` / `!` are a product and a complement of
  automata. Every lookaround form is VM today (APPROACH.md's module table). So a predicate build at the default
  level needs lookaround-over-a-regular-body in the automaton engine, beside the product and the complement: the
  rx and graph manipulation layer of M-2. [REQ-LOOKAROUND]'s ref "lookahead removal + lookahead to DFA" is the
  nearest existing row I found.
- Nothing asked of you now (design only; no build go). It belongs in the [COND-FAMILY] row's requirements when you
  next touch it. The `done:` for review r90's fold will be P-31.

## P-31 (2026-11-25, predicate manager) — done: review r90 (predfold1124) ruled, applied, filed; the fold is deliverable

- done: branch `lane/pred-rev28`, tip = the commit carrying this entry. It carries lane predfold1124's fold (the
  six rulings of 2026-11-23 late: shorthand-is-callers, path-rules, capture-in-set, exact-count-unspecified,
  options-reach-constants, option-hole-explicit), review r90 on it, and lane predfix90's fixes. Reports:
  docs/dev/lanes/predfold1124_report.md, docs/dev/lanes/predfix90_report.md. Review:
  docs/dev/reviews/2026-11-25-r90-predfold1124.md (+ its directory; INDEX line added).
- Checks at the tip: `python3 -I scripts/pred_doc_lint.py` 9,106 / 0; `make -s test-plan-lint` green;
  `predfix90_model: 26 checks, 0 failed` (re-run by me after the merge).
- Also on the branch, RECORD ONLY (not in the documents yet): the owner's ruling drop-not (`NOT` leaves the
  language; the negative peek is `peek(!A)`; not-test closed), his all-DFA goal (P-30), and the discussion of
  array-argument (asked, not answered). Their fold is a later unit.
- [COND-FAMILY] status line: "2026-11-25: r90 filed; the documents carry every ruling through
  option-hole-explicit (2026-11-23); ruled since and not folded: drop-not (`NOT` leaves, `peek(!A)`); the owner's
  stated goal: all DFA unless specified by the user, `when` must not force the VM; asked: array-argument; five
  owner questions queued from r90 (sent-label-wall, skip-past-wall, equivalence-inside, shorthand-outside,
  alone-as-middle)".
- Worktrees free to prune after your merge: predfold1124, predfix90 (both merged into my branch). worktrees/predref
  is not mine to judge: I did not create it this session.
- r90's lessons for the critic guide (yours to place; docs/dev/reviews/2026-11-25-r90-predfold1124/process.md):
  (1) a path-rule fold needs a GRID GENERATOR run against the rules written as a separate small evaluator (every
  answer-level finding was a cell no printed line reached; the name-grid lens gets a one-program probe and is told
  to cover depth 3, two binding levels and a wall below every start kind); (2) a declaration keyed on a verbatim
  FAIL line that carries document LINE NUMBERS goes red on any later one-line edit: normalise them out, and the
  committed .out is the delivered tip's run; (3) a reading phrased "whatever X does" is drilled on the inverse
  position too.
- PROPOSED SKILL EDITS, pcrec-predicate-manager: section 2: "each question put to the owner carries its DFA
  category: yes / never / maybe with a weight, and what the maybe depends on" (his words 2026-11-25, record);
  section 1: "read the memory index's TAIL too: a note cut off from the loaded index (the slow-burn week) was
  missed and a full-size critic round was launched"; section 4: "after merging a lane, the manager re-runs its
  model at the MERGED tip before the done: line (record entries land while a lane runs)".
- REPLY: one line, either way (merged, or what blocks).

## P-32 (2026-11-25, predicate manager) — pausing (the owner's close); NOT a delivery

- Branch `lane/pred-rev28`, tip = the commit carrying this entry. Beyond your merge of 16625c1f7 it carries NO
  predicate document change: record entries (the whole session), my journal and wake, this file, and lane
  predmap's study (docs/dev/lanes/predmap_report.md + predmap_evidence/, its history line). Lint 9,182+ / 0;
  plan-lint green. Safe to merge if you want the record on main; nothing needs it.
- RULED by the owner today, in the record, NOT yet in the documents (one fold lane owed, waiting for his go
  because of the slow-burn week): drop-not; array-argument (with `every`); brace-counts; map-creator (seven
  lines); string-literals (five lines). His stated goal: P-30.
- [COND-FAMILY] status line: "2026-11-25 late: r90's fold on main; ruled and not folded: drop-not (`NOT` leaves,
  the negative peek is `peek(!A)`), array-argument (group questions take the array form; `every` over the array),
  brace-counts (`x{a,b}` a postfix operator), map-creator (a labelled array with an enforcing literal; `m[key]` a
  search; `.index`), string-literals (no operators, either quote, five escapes, one line; the triple quote
  reserved); the owner's goal: all DFA unless specified by the user; queued: five questions from r90 and the
  map's open edges".
- REQUEST, when the fold's critic round comes (not now): a review number. I will ask again before launching.
- Worktree free to prune after your next merge of my branch: predmap.
- PROPOSED SKILL EDITS, pcrec-predicate-manager: section 2: "before withdrawing an answer already told to the
  owner on a principle's ground, RUN the principle on the case (the two spellings through the rule)" (I withdrew
  the key's-order answer and had to restore it the next turn); section 2: "when the owner asks 'couldn't X
  handle it' or 'should these take Y', grep the record for where the current form came from before defending
  it" (three times today it was the manager's, not his); section 1, for a slow-burn week: "the wake reads
  core.md's principles and the pieces the queue touches, not the whole file" (the whole read is about 90k
  tokens): yours and the owner's to decide.
- Nothing of mine in flight, in the box queue or on a cron. No reply needed.

P-33 (2026-11-27): review r109 (predbang) filed on lane/pred-rev28 with dispositions ruled; nothing to merge
urgently. NEW OWNER RULING in the record: bang-split (`!` = logical not of a test; `~` = the complement,
filter-only; `^A` lookahead, `!^A`; no lookbehind operator for now). Not folded; it joins the five rulings of
2026-11-25 in one fold lane awaiting his go. Proposed pcrec-critic skill edits from the round: in a multi-variant
subject give "operand kinds of each new operator" to ONE lens in COMMON; a per-variant ruling table as standard.
