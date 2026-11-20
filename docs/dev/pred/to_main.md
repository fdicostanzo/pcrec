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
