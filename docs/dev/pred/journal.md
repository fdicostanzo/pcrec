# Predicate-language manager: journal (append-only, newest at bottom)

## 2026-11-18 — the session is chartered (written by main, session 140)

- Frank, to main: "Please create a new manager skill: /pcrec-predicate-manager. Used to design and develop the
  predicate language. Managed by the pcrec manager like the kit manager is. an interface for me discuss predicate
  work." Skill `.claude/skills/pcrec-predicate-manager/`; this directory; the first wake.md written by main from
  sessions 134-140. Until today the pcrec manager ran the predicate work itself (journal: docs/dev/dev_journal.md,
  the 2026-11-14 .. 11-18 entries; the lanes predspec .. predspec271).

## 2026-11-18 evening — first predicate-manager session up

- Registered role pred; worktree `worktrees/pred` on `lane/pred-rev28` cut from main f9ee6814e. Read wake.md,
  M-1, the record from backref-label to read-is-constant, the draft's R.1.15 (11), R.1.16 ANSWERS CHANGED, R.8's
  hole-reads-capture row. No lane, no critic round alive.
- Grep of the record before asking hole-reads-capture: the 2026-11-17 ruling "what an unqualified `$x` reads"
  says "`$x` and `x:` never disagree" and predates holes holding values; so it is put to him as a confirm with
  that ruling quoted, not as a fresh question. The capture side of the example re-run under python `re`
  (`3-3;-3;` WHOLE holds; FIND-ALL on `3-3;-3; 7-7;` = [`3-3;-3;`@0, ``@7, `7-7;`@8, ``@12]), equal to the draft's row.
- owner.md written. Waiting on Frank's answer to hole-reads-capture.
- Main ACKed the hand-over (cross-session message): review number r52 is RESERVED for the rev 28 critic round;
  main's session is closing, the next one reads to_main.md at wake.
- Frank RULED hole-reads-capture: the label ("what i want is that $y works like label. however, there is a way to
  get the pcre capture value"). On the way: his discussion (label and capture separate; a labelled group need not be
  returned) and his recollection of the label-only group, CONFIRMED in POSTFACT.md 2026-11-09 (not in the predicate
  record until now); `(?<:x>foo)` and `(?':x'foo)` rejected by libpcre2 (error 162), run by ctypes; his typed
  `(<:x>foo)` a slip, corrected by him. Four record entries; predicates_future item 32. A reading of mine withdrawn
  the same hour ("the record lacks a per-group form").
- LESSON (case): his "I proposed" was true but lived in ANOTHER row body (POSTFACT.md). The record grep before
  answering covers docs/design/plan_row_bodies/, not COND-FAMILY.md alone.
- Next asked: number-domain (the record's 2026-11-15 confirmation, "numeric ranges are string sets; padding is an
  explicit transform", answers the comparison half; the arithmetic half is what is asked).
- Frank RULED number-domain: canonical. On the way: his suggestion "cant we wrap padded($y + 1)" and his idea
  `padded($y + 1, 4)` / `padded($y + 1, length = 4, pad = "0")` (both recorded, not ruled). Runs: scratch models
  `$PCREC_TMPDIR/scratch/pred/padwrap.py`, `padwidth.py` (to be re-made as evidence by the rev 28 lane; padwrap's
  `& /\d{n}/` uses a lookahead approximation, exact only for the subjects printed). numeral-width read as moot (m1).
- Next asked: padded-width (exact or minimum). Rulings gathered for rev 28 so far: hole-reads-capture,
  number-domain.
- Frank RULED padded-width: minimum (after three remarks recorded as clarification / observations; my leaning
  moved from exact to minimum on the two-case macro body, 36,119 python checks, 0 differences). Rulings gathered
  for rev 28: hole-reads-capture, number-domain, padded-width.
- Next asked: hole-flags. Pre-check run with libpcre2 (ctypes): a subroutine call to a group defined caseful
  stays caseful under a later `(?i)` (`a-A` fails), a backreference takes the options in force (`a-A` holds): PCRE's
  own two analogues agree with the draft's "as ruled for each"; what is asked is the string constant in a hole.
- Frank RULED hole-flags (a hole takes the flags in force at the hole; each regex literal has its own flags) and,
  on his own question, flags-propagate: yes (propagation with override; the draft's NO INHERITED FLAGS reversed).
  His argument (under one type `"blah"` is a regex, so without propagation the hole's flags reach nothing) refuted
  my "plain text vs pattern text" split: withdrawn in the record. Rulings gathered for rev 28: hole-reads-capture,
  number-domain, padded-width, hole-flags, flags-propagate.
- Next asked: unset-in-hole (ALGEBRA against the EMPTY readings; ALGEBRA equals PCRE on every run of rev 27.1's
  PART B).
- Frank RULED unset-in-hole: no string (I took his slug answer "i meant what you describe "no string" as. its a
  regex that matches nothing" as the ruling and told him so). His idea: a provided constant for the never-matching
  regex (sibling of "anything"; naming trap: the record's `when` ruling uses "matches nothing" for the EMPTY
  string). Rulings gathered for rev 28: hole-reads-capture, number-domain, padded-width, hole-flags,
  flags-propagate, unset-in-hole. Next asked: construction-line, part (a).
- Frank RULED construction-line: enumerate (after his clarification that "under construction" was not about
  arrays, and his two options; the enumerate line was my candidate, §5.5 "Enumerate go."). lift-order read as
  answered by consequence; under-construction-class closed as an answer-free manager's call (own class).
  Rulings gathered for rev 28 (seven): hole-reads-capture, number-domain, padded-width, hole-flags,
  flags-propagate, unset-in-hole, construction-line. Ideas recorded, not ruled: the label-only group
  `(?<:x>...)`, `padded(rx, length =, pad =)` names, the never-matching constant.
- Frank RULED value-test (the `if` was illustrative; `when` applies to `$y`; no special case: my reading of his
  slug answer, told to him). dollar-warning closed as an answer-free manager's call (the warning stays). Eight
  rulings for rev 28. Next asked: same-name-twice (libpcre2 by ctypes: without `(?J)` error 143; with it `\k<h>`
  reads the first group: `12-1` holds, `12-2` fails).
- Frank RULED same-name-twice ("i agree with your lean": error at the backreference unless `(?J)`). On his
  question the dollar-warning call was WITHDRAWN. NINE rulings.
- LAUNCHED lane predspec28 (opus; worktree worktrees/predspec28, branch lane/predspec28 from c32e93bc6): the rev
  28 fold. Deliver + empty rulings file written first; `lanewatch --follow predspec28` armed. Brief: nine rulings
  quoted; NOT RULED list; every (m) reading of the folded entries to test; premise test = predspec271 evidence
  re-runs byte-identical; not the full restructuring. wake.md rewritten in flight.
- Frank asked for a proposal on `${@y}` (given: value only for declared-then-used; models arrayhole.py,
  csvhead.py in scratch), asked about a CSV header (answered: keeping names = the array form, run time; a
  header-named column check = a compile-time per-position alternation, run), then RULED: "${@y} stays as a future
  direction item and is not built or defined now". TEN rulings. Sent to the running lane as R1 in
  worktrees/predspec28/docs/dev/lanes/predspec28_rulings.md (VERIFY in its STATE AT HANDOFF). Future item 33.
- predspec28 DELIVERED (tip 15af8217e; lanewatch DONE; R1 applied per STATE AT HANDOFF) and MERGED (e51e9a965;
  plan-lint clean). Draft is rev 28 (9,755 lines). Readings NOT SUPPORTED recorded as a MANAGER CORRECTION entry:
  numeral-width is NOT moot (subtraction: 10, 100, 1000) -- I had told Frank it fell away, corrected to him;
  the general diagnostics do not fire on `$x & <5` (gap: dollar-diagnostic); `${@y}` is a plain not-defined
  error, not under construction. New question slugs: numeral-width (narrowed), dollar-diagnostic, any-case-body,
  domain-components, same-name-count. Next: critic round r52 on rev 28.
- predspec28 TaskStopped (told: `${@y}` = a plain "not defined" error). LAUNCHED critic round r52 on rev 28:
  coordinator `crit-predspec28` (opus, background), design mode, round dir
  `$PCREC_TMPDIR/scratch/crit-predspec28/`; standing lenses named (ruling; ruled examples through the status
  tables in every mode; general form + unlocks); denylist given; no known result told. On hand-back: read
  review.md + .coord/process.md, rule dispositions, a FIX lane (rev 28.1, files the review as
  docs/dev/reviews/2026-11-18-r52-predspec28.md), merge, `done:` to main.
- Review r52 handed back (five opus lenses, 56 raw findings, 22 items, none refuted). I RULED every disposition
  (record entry "MANAGER — review r52 of rev 28"): A FIX-NOW (padded's body reorders a search: my two-case macro
  reading withdrawn as an "equals"; padded-order queued for Frank); B-K FIX-NOW/PLAN as proposed, with calls:
  ordered clauses in T8/T9, `${@y}` not-defined, product-order closed by consequence, dollar-warning re-ruled (a
  read stands for its group's rx in emptiness diagnostics: a reading, to confirm), "the never-matching rx",
  `strlen` placeholder. The r52 attack also corrected my correction entry (numeral-width is a full question for
  `%`; domain-components is not a gap; the outside-domain clause is ruled). Coordinator TaskStopped.
- LAUNCHED fix lane predspec281 (opus): rev 28.1 + filing the review. Deliver/rulings files written first;
  lanewatch armed. owner.md and wake.md refreshed.
- Frank asked whether `padded()` fixes the `10-09` case (answered with a four-row model table), then RULED
  numeral-width: canonical. ELEVEN rulings tonight. Sent to the running fix lane as R1 in
  worktrees/predspec281/docs/dev/lanes/predspec281_rulings.md (it changes disposition F: VERIFY in its STATE AT
  HANDOFF).
- predspec281 DELIVERED (lanewatch DONE; R1 applied per STATE AT HANDOFF), MERGED (7f175758f; plan-lint clean),
  TaskStopped. Draft = rev 28.1 (9,973 lines); review r52 filed with my ruled dispositions. Its one NOT SUPPORTED
  (my dollar-diagnostic reading against §5.2's wording) recorded; the question row prints the wording change.
- DELIVERED to main: P-2 in to_main.md (done line, [COND-FAMILY] status line, the coordinator's four process
  changes and two proposed edits of my own skill). /q asked padded-order; he asked what the exact-width part is.

## 2026-11-19 (just after midnight) — padded-order ruled
Frank: "putting the length in front would help order" / "i meant, putting any length" (observation; run padfront.py),
then "i agree with your lean" = RULING: plain macro, any-length branch first. Two readings for the rev 29 lane
(length-ordered arguments equal fill; unbounded lazy). Next question in the queue: flags-in-filter. Nothing running.

## 2026-11-19 (early) — flags and class-order
Frank: flags-propagate meant "rx inherits the flags of the surrounding rx" (flags-in-filter closed as "reach" by
consequence, my reading); a binding in a hole inherits (lean, matches the draft); flags-scope RULED (inherit i, m, s;
not U, x, xx, n; J with same-name-count; "only i" an observation); class-order RULED: longest first, class positions
only (his idea; run classlong.py). Fourteen rulings wait for rev 29. Next question: dollar-diagnostic. Nothing running.

## 2026-11-19 (early, later) — three more rulings
dollar-diagnostic (the form `$x & ..` just gets a warning; my withdrawal reversed, the general-diagnostic proposal
dropped), number-edges (nothing), same-name-count (scoped). Seventeen rulings wait for rev 29. any-case-body held
until the rev 29 lane runs it under the flags rulings. New queue item: inner-label-read. Nothing running.

## 2026-11-19 (early) — session closed (/close)
After same-name-count: his scope question (backreferences only; my `$h` extension withdrawn), his recollection on
private labels (export-rule already rules binding scope; inner-label-read not asked), his direction "use labels as
they are defined and see if there is a problem" (isodate example to the rev 29 lane). wake.md rewritten with the
rev 29 fold brief's contents; owner.md refreshed; P-3 in to_main.md. Nothing running. Main had not merged P-2.

## 2026-11-19 (midday) — second session up; rev 29 fold lane launched
Registered (session_role pred). Main MERGED lane/pred-rev28 (P-2, P-3 done; its e99273ff3 moved the r52 index line to
reviews/NOTES.md); main merged back into my branch (plan-lint clean). Review number for the rev 29 round: r54 (r53
taken). LAUNCHED lane predspec29 (opus, worktree worktrees/predspec29, branch lane/predspec29): folds the six
2026-11-19 rulings, tests 16 manager's readings, works the isodate / private-label / any-case-body tasks; deliver and
rulings files written first; lanewatch armed. On DONE: read the report, merge, then critic round r54 (design, topic
predspec29). Meanwhile asking Frank plus-operands: the record (number-domain "nothing" outside the domain; the
sequence operator ruled 2026-11-17; number-edges "no compile error of its own") appears to answer it; asked as a
confirmation with a run (scratch/pred/plusops.py).

## 2026-11-19 (midday) — his idea on parameter restrictions, in answer to plus-operands
Asked plus-operands (as a confirmation). Frank answered with an IDEA, not the slug: a macro parameter restricted by
`&` in the head (`example(g & /\d+/)`), "some value in the intersection for the macro to match", and the same logic to
limit / overload arithmetic. Recorded verbatim with the 2026-11-13 typed-parameter entries it meets (intersection as
the meaning; his "type must equal" lean the other way); ideas file item 34. plus-operands stays OPEN; my reading is
that his idea is the "nothing" answer. Lane predspec29 still running.

## 2026-11-19 (afternoon) — plus-operands RULED
After two discussion turns (his ideas: a parameter restricted by `&`; a class as the number base; numbers as strings
over an ordered symbol set: ideas file items 34, 35), Frank RULED plus-operands: for now arithmetic is digits only,
anything else is nothing, a warning if known; `+` never joins; a literal mismatch becomes an error once types exist
(direction). Sent to the running lane predspec29 as R1 in its rulings file (verify in STATE AT HANDOFF). Next
question: other-holes.

## 2026-11-19 (afternoon) — rev 29 delivered and merged; critic round r54 launched
predspec29 DELIVERED (lanewatch DONE; R1 applied per STATE AT HANDOFF), MERGED (80c912aa5; plan-lint clean),
TaskStopped. Draft = rev 29 (10,160 lines). Readings 1, 14, 17 not supported (record entry "after lane predspec29");
new owner questions class-positions, class-index; T-a's two surprises and T-c to tell him. other-holes is ASKED in
chat (three places, runs in scratch/pred/otherholes.py). LAUNCHED coordinator crit-predspec29 (opus, background),
design mode, review r54. On hand-back: rule dispositions, FIX lane predspec291 (rev 29.1 + files the review), merge,
`done:` to main.

## 2026-11-19 (afternoon) — other-holes RULED
Frank: class member and range end = an alternation of the class, one per value (collapses to one class; range
errors removed from the alternation); option hole with several values = error. Place 2 differs from my leaning.
Recorded with runs and seven readings; a negated class is not covered (`[^x]|[^y]` vs `[^xy]` part): asked as
negated-class-hole. NOT in rev 29 (round r54 frozen on it): goes to the fix lane (rev 29.1) with r54's dispositions.

## 2026-11-19 (afternoon) — option-hole details and negated-class-hole RULED
Frank: an empty option value adds no options; values from the legal set or an error; nothing there is an error;
his count remark read as the count value 0 (`{0}`), my zero-values reading stands untested. negated-class-hole:
"[^${join(c)}]" = the user joins; the alternation rule is unchanged (my one-class leaning not taken). All for rev
29.1. Next asked: anything-text. Round r54 still running.

## 2026-11-19 (late afternoon) — anything-text and zero-in-sequence RULED
anything := [\s\S]* (his spelling, run under every flag); standing instruction "be suspicious of my regex and confirm
contemporaneously" (memory + proposed skill edit, to_main P-4). zero-in-sequence: "the condition is always sees the
regex composed at the point it is used. so the 0: is the match so far" (not my leaning, the error). I had glossed
the slug wrongly in chat (as the never-matching rx) and corrected it in the question. Both for rev 29.1. Next:
group-truth / pass-table. Round r54 still running.

## 2026-11-19 (evening) — review r54 ruled; fix lane predspec291 launched
Round r54 handed back (16 items, none finds a printed RULED answer wrong). I RULED the dispositions (record entry
"review r54 of rev 29"): all FIX-NOW; calls on P29-6 (the padded condition was checked on a witness that could not
fail: back to Frank as the confirm padded-lazy-sparse), P29-7 (one warning trigger: any known-nothing arithmetic
result), P29-11/12 (the dollar form on the parse; the hint only where it is a drop-in); owner questions added
(r/a flags, sequence-operand flags, class-first, class-index reworded, hole-export). Coordinator TaskStopped.
LAUNCHED lane predspec291 (opus): rev 29.1 + files the review; deliver/rulings files first; lanewatch armed.
The rulings made during the round (other-holes, option hole, negated-class-hole, anything-text, zero-in-sequence,
bare condition in a hole) are REV 30's fold. Frank also discussed a condition without parentheses: checked, the
draft makes `A & 0: digit` an error (a lean); my call: parentheses stay required for now.

## 2026-11-19 (evening) — padded-lazy-sparse RULED; limited(); a direction on macros
Frank: "padded-lazy-sparse: stated behavior"; padded's default is `0*`, the width argument suspect; a `limited(rx, n)`
macro (ideas item 36); DIRECTION: no deep dives into one macro unless it raises a language point (memory saved).
Validated his examples on request: with digits := \d+ padding is a no-op as a set; "00000 through 99999" (exact)
vs "limited" (at most) not settled. Sent to the running fix lane as R1 (the confirm question becomes a ruling).

## 2026-11-19 (evening) — documentation organization: requested, delegated, format proposed
Frank asked for an organization of the predicate documents (base + details files, path tags with status, lint;
modelled on the plan split), then delegated the form ("keep, modify, or reject these instructions as you reason it
better"; design it from how I use the files; rejected-and-why; analogy search by subagents). Census agent predcensus
(sonnet, read-only; facts in scratch/predcensus/facts.md; stopped): 155 ruling entries, ~100 slugs, 72 candidate
names, 17 principles, 36 parked items; what [DOC-INDEX] rejected. WROTE docs/dev/pred/doc_format.md (PROPOSED):
three base/details pairs (core with a principles section, library, parked); the record stays one log with `tags:`
lines; a `rejected:` block and `by:` principle links per piece; lint L1-L11 asked of main (to_main P-5). The
library-document request is absorbed (no separate lane). NEXT: pilot after rev 29.1 (skeleton + core/holes).

## 2026-11-19 (evening) — lint lane launched at main's instruction
Main answered P-5: "write it yourself in a lane on your branch ... I'll review it, run a code critic round sized to
it, and land it with your branch after rev 29.1." LAUNCHED lane predlint (sonnet; worktrees/predlint): scripts/
pred_doc_lint.py (L1-L11, planted-fault selftest, a minimal reader --show/--list); the scripts/entry profile only if
declaration-only. Two lanes running: predspec291 (rev 29.1 + files r54), predlint. Watchers armed on both.

## 2026-11-19 (evening) — lint lane merged; fix lane found idle and woken
predlint DELIVERED twice (first cut; then R1: L8 exempts parked / under-construction / principles pieces), lanewatch
DONE, selftest re-run by me (22 runs, 11 of 11 rules, 0 failures), MERGED into lane/pred-rev28 (plan-lint clean),
TaskStopped. Not built: a scripts/entry profile (needs new accessor code: main decides) and a make target; the lint's
own --show/--list reader covers the need. doc_format.md corrected (tag depth, `shared:` line, L8 exemptions).
predspec291: its watcher exited QUIET (25 min, rc 10): the lane had idled "waiting" on its own background sabotage
run, which had finished 20 min earlier. Woken by message; watcher re-armed. LESSON (already a rule for critic
coordinators, r53): a lane brief must say "no background jobs: run checks in the foreground under timeout".

## 2026-11-19 (evening) — rev 29.1 delivered to main
predspec291 DELIVERED (lanewatch DONE after the wake message; R1 applied), MERGED (plan-lint clean), TaskStopped.
Draft = REVISION 29.1 (10,275 lines), review r54 filed. Record entry "after lane predspec291" (the fill-reference
fact on padded-lazy-sparse). Ideas items 37, 38 (the round's two general forms). to_main P-6 (done lines, status
line, proposed skill edits); main messaged. NEXT: the pilot lane of the reorganized documents.

## 2026-11-19 (evening) — pilot lane launched; main's code round on the lint is r56
LAUNCHED lane preddoc1 (opus; worktrees/preddoc1): the skeleton of the three base/details pairs, core/principles and
core/holes in full (with the rulings made since rev 29's fold), twelve readings to test, a completeness control from
the census, FORMAT PROBLEMS as a report section; no background jobs (brief says so); lanewatch armed. Main: got P-6;
the lint's code round is r56 (running); it merges lane/pred-rev28 (draft + lint) when r56's fixes are in, at
whichever tip I name; decides the entry profile / make target and answers the skill edits at that merge.

## 2026-11-19 (evening) — main's review r56 of the lint ruled; fix lane predlint2 launched
Main ruled r56 (code round on scripts/pred_doc_lint.py): the FIX-NOW list, the mutation harness as acceptance gate,
ONE reader = a scripts/entry profile calling the lint's parser, the review to be filed on my branch. MY rulings
(form, delegated): CONTRACT-10(d) "every rulings item cites an existing title"; the DOC hunks written into
doc_format.md (record-title shape, L6 word list with code spans exempt, pilot mode, L8 exemptions, one reader).
LAUNCHED lane predlint2 (sonnet; worktrees/predlint2); lanewatch armed. RETURNED to main: the critic-skill process
changes (I do not edit files under .claude/skills at a peer's request). The pilot preddoc1 found the lint's L4
two-line-opener bug (ruled R1 in its rulings file: cite true titles, accept those failures only); it is in
predlint2's fix list. Two lanes running: preddoc1 (pilot), predlint2.

## 2026-11-19 (evening) — lint fixes merged (r56 gate passed)
predlint2 DELIVERED (lanewatch DONE; R1 applied), gate RE-RUN by me (176 mutants, 160 killed, 16 equivalent, 0
survived; .test PASS; entry selftest 75/0), MERGED, plan-lint clean, TaskStopped. Reader = scripts/entry profile
`predicates`. to_main P-7. The pilot's two lint questions were ruled R1/R2 in its rulings file (cite true titles;
both L4 classes are now fixed in the lint, so the pilot's remaining L4 failures should vanish after it merges this).
One lane running: preddoc1.

## 2026-11-19 (evening) — the pilot landed on my branch
preddoc1 DELIVERED (lanewatch DONE; R1, R2 applied), MERGED (plan-lint clean), TaskStopped. With predlint2's fixed
lint the merged tree lints CLEAN (1,828 checks, 0 failures). Core: 94 pieces (ruled 61, ? 24, reading 5, open 4),
34 KB base, largest piece 15 lines; holes 20 pieces (15 ruled, 3 reading, 2 open); principles 22; library 27
(skeleton), parked 36. Completeness: 124 of 124 slugs homed; two 2026-11-15 hole rulings the draft's R section had
not carried were found and folded (anchored-in-hole, and-in-hole). My readings 1-9, 11, 12 SUPPORTED; reading 10
parts (an answer against a compile error): NEW owner question bare-condition-labels. FORMAT rulings after the pilot
(doc_format.md): a `principle` status; `skeleton: yes`; one piece one status (split zero-values); the `?` date.
to_main P-8 names the tip. NEXT: show Frank the holes section; on his look, the conversion of the remaining sections
(lanes per section group) with the two lint additions; then the completeness critic round.

## 2026-11-19 (evening) — main merged the pilot; the lint is in make test
Main merged the pilot (main fceff8f98) and wired the lint into make test (section test-doc-lint, 76024ee9e): a
document change that breaks the lint turns make test red, so RUN THE LINT BEFORE NAMING A TIP. Main merged back
into my branch (plan-lint and document lint clean). My two later lint additions get their own small code round from
main. Waiting on Frank: doc-shape (his look at the pilot). Nothing running.

## 2026-11-19 (afternoon) — the owner answered doc-shape; lane preddoc2 launched

Frank read the pilot: macros that have a body go to the library (core = primitives; `peek` "a useful transform");
a default-imported set with `peek`; an aside to discuss importing symbols (`(left,right) := import("blah",
/left|right/)`); a standard move/rename with previous tags in the history; the files under
`docs/design/predicates/`. Recorded verbatim; doc-shape read as answered (this shape with these changes).
doc_format.md gained "Changes after the owner read the pilot" (`see:`, `was:`, `formerly:`, `module:`,
`default: yes`, the directory). Lane preddoc2 (opus) launched for: lint and reader changes, the move, the
post-pilot format changes, macros to the library with a model run per moved body. Watcher armed. P-9 to main (asks
the code-round number). New owner questions queued: import-symbols, default-set. WAITING on: preddoc2.

## 2026-11-19 (late afternoon) — preddoc2 merged; import-symbols ruled; code round r57 running

Lane preddoc2 delivered and merged (tip cd5ddeb70): the six files are `docs/design/predicates/*.md`; lint 2,168
checks, 0 failed (new L12 module/default); mutation 212 / 196 killed / 16 equivalent / 0 survived; peek, when,
when-test and repeat moved to the library, each body run against every ruled example (25 checks, 17 sabotages);
the consuming-test warning stays core; `scripts/entry core/conditional/peek` resolves to `lib/control/peek`.
My readings 1-4 SUPPORTED (2 except the warning). Confirmed by me: no-absence and exact-wording take status
`principle`. Lane stopped. Critic coordinator crit-preddoc2 launched for r57 (small code round, main's number).
Owner, same hours: import-symbols RULED in steps (named binding list, `=x` shorthand also in a macro call, any map,
`(=)` first for all public names, later entries override, `_ = left` leaves a member out, a conflict between two
modules in one import is a compile error). OPEN: import-several (his `import("pcrec"|"numbers")` meets the
2026-11-14 "exactly one file" ruling). WAITING on: crit-preddoc2; his answer on import-several.

## 2026-11-19 (evening) — review r57 drafted and ruled; fix lane predlint3 launched; import-several ruled

r57 (small code round on preddoc2's lint changes): 16 items, 8 where the lint passes a forbidden document (worst:
a `was:`/`formerly:` line closes the open details field so later rulings items go unchecked, a regression; a
retired tag can be reused once its `was:` line is deleted; a principle item without its class passes). Dispositions
ruled as proposed: FIX NOW F1-F7, F9-F11, F13-F15; DOC F16 and the fold of doc_format.md's three late sub-sections
into its upper half; PLAN F8, F12, G1-G3. Coordinator stopped; draft committed (ebeeaf3d3). Lane predlint3
(sonnet, worktrees/predlint3) applies and files it; watcher armed. NOTE for main: an older file
2026-09-12-r57-w23-format.md already carries the number r57. Owner: import-several RULED (several files; one name
= the combined map; reverses 2026-11-14 "exactly one file"). WAITING on: predlint3.

## 2026-11-19 (evening, later) — predlint3 merged; delivered to main (P-10); conversion lanes 3a/3b/3c launched

predlint3 merged (lint 2,278 / 0; mutation 316 / 301 / 15 / 0; r57 filed RULED; doc_format.md folded, each rule
once). Accepted its calls: F2 "at least one principle item names its class"; the record `tags:` check accepts a
live piece, a section or a previous tag. Delivered tip 3c0042d1c to main (P-10, message sent). Decided: import is
RULED, so it is a CORE section (`core/modules`), not parked; the parked `?` piece is retired by `was:`.
Launched, opus, watchers armed, disjoint: preddoc3a (core model, patterns, labels, conditions, filters),
preddoc3b (core values, arrays, operators, diagnostics, spellings + new core/modules with today's import
rulings), preddoc3c (library in full with proved bodies, `capture`, the 72 census names; parked against the 38
ideas-file items; deletes parked/import-symbols). None edits the ratchet: I lower it after the merges. A known
transient: 3b and 3c each may show ONE lint failure on the retired parked tag until both are merged.
AFTER THEM: merge 3a, 3b, 3c (each ALONE), lower the ratchet, lint; ask main for a review number; a critic round
with a COMPLETENESS lens (census lists: 155 ruling entries, slugs, 72 names each land on a tag); retire
predicates_future.md; send main the skill text for the new layout. WAITING on: the three lanes; main's merge.

## 2026-11-19 (night) — the conversion is merged: no unconverted piece left; asked main for the review number

Main merged P-10 (main 892553b58). Lanes preddoc3a, 3b, 3c delivered, merged (index conflicts: both sides kept)
and stopped. State: core 113 pieces, library 38, parked 39; no `?`, no skeleton; ratchet set to zero; lint 4,056
checks, 0 failed; three soft-cap warnings (core.md 93.7 KB against 64; library 28.2 against 24; parked 17.7
against 16: the caps were my guesses; decide after the review whether to raise them or split core).
MY ERROR, found by 3b: statement 7 of import-symbols ("positional `(a, b) := X` left undefined") was wrong against
"2026-11-16 OWNER CONFIRMATION — a tuple on the left of a binding takes it apart"; withdrawn in the record, told to
Frank, core/modules/positional rewritten by hand as ruled. LESSON (again): grep the record before giving him a
list of "implications".
By hand: the eight record `tags: parked/import-symbols` lines repointed to core/modules (tags lines are my
metadata, not his words); parked head paragraph.
OPEN CALLS OF MINE for the fix lane after the review: (1) his words put PRIMITIVE names in the core, the library
lane left the primitive provided names in the library (any_case, occurs, param, file_text, ...): move them to a
core section, or amend the format with a reason; (2) the census has 61 names, not 72: 11 unaccounted; (3)
nullable-meaning sits on a core piece and belongs to lib/search/occurrences; (4) condition-group (open) sits on a
ruled piece; (5) bold openers glued to a paragraph cannot be cited; (6) some/count/none/same/all have no core
piece; (7) retire predicates_future.md (all 38 items now have parked pieces).
Owner questions now open in the documents: any-case-body, bare-condition-labels, caller-ambiguous, class-index,
class-positions, default-set, group-truth, hole-export, not-test, number-in-loop; named by lanes, not pieces:
condition-group, export-choice, limited (at most / exactly), between's body, list_of, param, within, upperStart.
WAITING on: main's review number; then one opus critic coordinator (design mode, completeness lens).

## 2026-11-19 (late night) — review r59: NOT ready; my tuple statement wrong a second time; fix lane preddoc4 launched

r59 (main's number; five critics; draft committed c331717a6): examples 92 run, 0 differ, but: rulings 144
expected / 27 missing; slugs 188 / 49 unhomed + 10 misplaced; provided names 98 / 27 missing; rejected candidates
100 / 25 missing; core primitives with no piece (comparisons, some/every/count, tuples, computed labels, .index /
.label, assert); three definitions of `0`; negation undefined in places; 11 primitive pieces in the library;
core.md does not read front to back. Verdict: not ready as the wake base. ALL proposed dispositions accepted.
MY ERRORS: (1) my withdrawal of statement 7 stopped one record entry short: his "Yes" on taking a tuple apart was
REOPENED eight minutes later ("Nothing is set in stone"); the question is the draft's open tuple-parts. Record
corrected again, piece rewritten `open tuple-parts`, to be told to him. (2) the padded width body I wrote and he
agreed to has `n` outside a hole (`{n,}` is literal text); corrected to count holes in the record; answers
unchanged. LESSONS: read the SAME-DAY entries after any entry cited as confirmed; an evidence model must build the
regex from the body's TEXT, not its intent (three rounds missed the padded slip that way).
PLAN: lane preddoc4 (opus, launched, watcher armed): the design-bearing findings (sections C, D, RULING-n;
primitives move to a new core/builtins; missing primitives added; READ-18 stage 1). THEN lane preddoc5: the
mechanical lists from the critics' appendices (citations, slugs, rejected, names). THEN a re-check round (ask main
for a number), file r59, deliver. Not delivered to main since P-10. WAITING on: preddoc4.

## 2026-11-19 (near midnight) — preddoc4 merged; the owner refined "primitive"; preddoc5 launched

Owner: "all macros "x()" should be in the library document ... marked as to whether they are defined in the
language or not"; "my 'primitive' designation doesn't work"; library = "provides the symbols"; then "I agree with
your take" (split by what a thing is; `import` the call in the library, the binding list in the core). Recorded;
sent to the running lane as R-1, which it applied (verified in the merge: no core/builtins; 46 library pieces all
with `defined:`, 15 native; enumerate and import in lib/builtin).
preddoc4 merged and stopped: lint 4,575 / 0; core 119 pieces, library 46; padded body with count holes built
mechanically from its text; ZERO, NEGATION, the missing primitives (comparisons, tuples, computed labels,
metadata, some/count, assert, pattern, eval), condition-group as an open sub-piece. Soft caps: core.md 100.6 KB,
library 38.2 KB (grew with the new pieces; READ-18 stage 2, generated indexes, is PLAN).
preddoc5 (opus, launched, watcher armed): the appendices' four lists row by row (27 rulings, 49 + 10 slugs, 27
names, 25 rejected), parked rulings items, `defined:` into doc_format.md, files r59 as RULED.
THEN: merge, ask main for a re-check review number, re-check round (same five lenses), deliver (P-11).
Owner questions named by preddoc4: zero-in-loop, caller-ambiguous (a) vs (e), every-pass-spelling,
condition-group, flags-in-filter, operators-as-bodies, macro-warning. WAITING on: preddoc5.

## 2026-11-19 (midnight) — preddoc5 merged; r59 filed; re-check round r60 running

preddoc5 merged and stopped (tip d8634250a after merge; lint 4,850 / 0): rulings 33 rows (20 homed, 8
superseded, 5 already), slugs 59 (50 homed, 9 already), names 36 (24 homed, 9 already, 3 not names), rejected 25
(24 homed, 1 not); no status rose to ruled; no contradiction met; r59 filed RULED and indexed; doc_format.md has
`defined:`. Main gave r60 and reminded: evening hold, light work only (told to the coordinator). Coordinator
crit-preddoc5 (opus) launched: fix-verification per r59 finding, list re-count from the appendices, ruling lens
on the added text with the same-day-later-entry check, a cold read-whole, new-damage. Verdict asked: READY /
READY WITH NAMED RESIDUALS / NOT READY.
THEN: rule its dispositions; if a fix lane is needed, run it; deliver to main as P-11 (documents converted,
reviews r59 + r60); retire predicates_future.md (my call, pending: all 38 items are parked pieces); send main the
skill text for the new layout (sections 0, 1, 3, 4, 5 name the draft as the working document). At pause:
REWRITE wake.md from scratch (it still describes the first session). WAITING on: crit-preddoc5.

## 2026-11-20 (after midnight) — r60: NOT READY by a short batch; fix lane preddoc6 launched

r60 (draft committed 3e520c47c): of 38 applied r59 findings 31 FIXED, 6 PARTLY, 1 FIXED WRONGLY
(condition-group), 0 not fixed; re-counts: rulings 1 of 144 missing (looped-compare), slugs 5 of 188, names 1 of
98 (+ the `@` effects), rejected 0 of 100 (5 partial). Worst: positional piece still used the withdrawn wording
for the map case; `@export`/`@warn`/`@options` have no piece; a citation of words superseded the same night
(SOURCE-ROW); an OWNER-RULED warning (looped-compare, moved by joint-loops part 3) that a manager's withdrawal had
dropped from the documents; duplicate bodies in the base. All proposals accepted; my calls: the `@` effects are
three native library pieces; the looped warning is stated as he last ruled it, with an open sub-piece
looped-warning for him. Lane preddoc6 (opus) launched, watcher armed; it also files r60. The coordinator says no
further full round is needed after this batch: I verify by its three readings and the lint, then deliver (P-11).
New owner question queued: looped-warning. WAITING on: preddoc6.

## 2026-11-20 — preddoc6 merged; r60 filed; DELIVERED to main (P-11); wake.md rewritten

preddoc6 merged and stopped: lint 5,014 / 0; r60 filed RULED, verdict READY WITH NAMED RESIDUALS; re-counts
rulings 0 missing of 144, slugs 0 language slugs missing of 188, names 0 of 98, rejected 0 of 100; `@warn`,
`@export`, `@options` are library pieces; looped-compare restored as he ruled it with the open sub-piece
looped-warning; new open piece call-forms (repeat / padded several call-form bodies against the macro rule).
Main merged in (two index conflicts, both sides kept). predicates_future.md marked retired; pred CLAUDE.md for the
new layout; wake.md rewritten from scratch; owner.md refreshed; P-11 written and main told (tip 9958a6e1a).
Core 122 pieces, library 54, parked 39. NOTHING running. WAITING on: main's merge; Frank's next question
(bare-condition-labels first).

## 2026-11-20 — /close of the second predicate-manager session

Main merged P-11 (main f1792840b; lint there 5,014 / 0) and applied the skill edits; Frank then asked this session
to make the skill's wake-up read the three primary files (core, library, parked) at their new paths: done on my
branch, P-12, merged by main. /close with nothing in flight: wake.md brought to the close state, owner.md current,
P-13 written, main told. Next session: /q, bare-condition-labels first, then looped-warning.

## 2026-11-19 (box date) — third predicate-manager session: wake-up

Registered (session_role pred); read wake, from_main (nothing after M-1), core/library/parked whole, the record from
doc-shape to the end, r60's PLAN rows. Branch fast-forwarded to main 50f56b1cd; main told. Before asking
bare-condition-labels I grepped the record: hit-carry (2026-11-18, asked as a ruling with the witness
`occurrences(/${c}(?<h>\d)/, min = 2)`, c a condition in a hole reading the surrounding literal's h) and
pass-start-read's witness `/(?:${c}(?<h>\d);)*/` already have a condition in a hole reading the surrounding labels;
his words there: "a condition ... before the label ... carries". So the question goes to him as a CONFIRMATION that
the record answers it, not as a fresh question. preddoc1 PART R10 re-run: same answers (the PART LT difference is
the moved files, historical). WAITING on: Frank (bare-condition-labels).

## 2026-11-19 (evening) — bare-condition-labels RULED and folded

Five record entries (his statement "the same condition just after the rx literal", checked: true for a hole last
only; "it's not the same"; his guess; the ruling with its correction). Folded by me in one commit: the core piece
is ruled, details carry three rulings and three rejected candidates; lint 5,033 / 0. One reading of mine listed
for a lane: outside a loop a hole before its group is the never-pass warning. NEXT: looped-warning. WAITING on:
Frank.

## 2026-11-19 (evening) — looped-warning RULED: the warning is removed

"looped-warning: I agree remove warning." Folded by me: the piece core/diagnostics/looped-compare restated (no
warning; last pass after the loop, every pass on the item), its question sub-piece merged in by a `was:` line,
the warnings table's row gone; lint 5,020 / 0. He also asked for the intended in-loop form and whether the joint
`(h, m):` form is better: answered in the session with runs. NEXT in the queue: hole-export. WAITING on: Frank.

## 2026-11-19 (evening) — hole-export RULED (both pass through); his array-under-composition question

Folded: core/labels/export statement 3 revised (outside = inside less private), the question piece merged by
`was:`; lint 5,014 / 0. Told him two checks against his message: across `|` a flat label is not ambiguous (ruled
alternation example); the record has his own "The array takes all h including the one outside the group" and
"a compose and a literal rx have the same label behavior", so the array is by NAME in the composed rx. Readings
of mine listed in the record entry (bare `v` outside `date` now the last mention). WAITING on: Frank (the array
discussion; then class-positions).

## 2026-11-19 (night) — array-scope RULED and folded; class-positions RULED, fold lane predloop launched

array-scope: "by the scope of the entire rx", a part label limits it (`x.@a`); folded by me (5a655e436).
class-positions: after my lean (written order, then classes by result length) he proposed the nested loop over
enumerate "as though this was against fn()", classes in descending value order; shown `10 - \d` on `10` (`1`, not
`10`), he ruled "class-positions: nested loops, classes descending". Record tip 18ca97f7e. It replaces
class-order: longest and answers class-index, so it moves several pieces and needs runs: lane predloop (opus,
worktrees/predloop, branch lane/predloop off 18ca97f7e), deliver + empty rulings file written before launch,
lanewatch --follow armed. Left open by his answer: class-value (non-digit classes). While it runs I do NOT edit
core/arrays, core/values/arithmetic|functions, lib/builtin/enumerate, lib/structural/sort on my branch.
WAITING on: predloop; Frank's next question (flags-in-filter).

## 2026-11-19 (night) — predloop merged; one of my answers to him withdrawn; quantified-order asked

predloop DONE (lanecheck rc 0), merged (tip after the record entry b47e798cf), stopped: lint 5,062 / 0, plan-lint
clean, its model re-run on my branch 20 / 0. class-positions and class-index merged into lift / class-order /
enumerate; new open class-value. My reading (c) half failed: I told him lazy + greedy gives `123` on `x123` from a
hand model that enumerated count by count; enumerate's recorded priority order is depth first and gives `12`.
Withdrawn in the record; asked him quantified-order. LESSON (again): a hand model is the model's INTENT; the
lane's mechanical one found it. Critic round on the session's batch is owed before delivery to main (ask main
for the number first). WAITING on: Frank (quantified-order).

## 2026-11-19 (night) — quantified-order RULED; classes turn to lowest to highest; lane predasc launched

"quantified-order: keep pcre priority order and classes change to lowest to highest unless pcre priority order
disagrees ... Only solution is sorting output when needed. Need a terser sort function for common use." Record tip
5a299d40d. Shown him: `\d + 1` is then `1|..|9|10`, SEARCHED `x10 10` `1`@1 bare, `10`@4 between `\b`s (his
boundary remark, run). Lane predasc (opus, worktrees/predasc off 5a299d40d): deliver + empty rulings file written
first, lanewatch --follow armed. Owed by me: a name proposal for the terse sort; the critic round on the batch
(number from main first). While it runs I do not edit the class-order / lift / enumerate / sort pieces.
WAITING on: predasc; Frank's next question (flags-in-filter).

## 2026-11-19 (late) — predasc merged; corrections owed to him told; sort shorthand noted

predasc DONE (lanecheck rc 0; hand-back verified against the report), merged, to be stopped: lint 5,094 / 0 after
my sort bullet, plan-lint clean, its model re-run on my branch 24 / 0. Classes ascending: `\d + 1` is
`1|..|10`; `10 - \d` now `10|9|..|1`; bounded lazy + lazy `1`@1, lazy + greedy `123`@1 again (both told to him).
His sort remark recorded (lean + request); `longest_first(X)` proposed and noted on lib/structural/sort.
OPEN from tonight: class-value. NEXT: ask main for a review number, critic round on the batch (bare-condition-
labels, looped-warning, hole-export, array-scope, class-positions + quantified-order), then deliver.
WAITING on: Frank (flags-in-filter next; his word on the critic round timing is not needed).

## 2026-11-19 (22:25) — critic round r61 (predfold1119) launched

Main gave r61 and a box deadline: nothing running after 00:30 (the kit's timing night at 01:00). Coordinator
crit-predfold1119 (opus, background, design mode) on the diff 50f56b1cd..tip over docs/design/predicates/ with the
record from the first bare-condition-labels entry to the end; lenses required: ruling, run-every-example in three
modes, general form + unlocks; told to hand back by ~00:15. Round dir $PCREC_TMPDIR/scratch/crit-predfold1119/.
THEN: rule dispositions, a fix lane if needed (it files the review), deliver to main (P-14).
WAITING on: crit-predfold1119; Frank (flags-in-filter).

## 2026-11-19 (22:50) — flags-in-filter RULED and folded (after r61's freeze)

"flags-in-filter: both sides inherit." Folded by me (piece ruled, details, lint 5,098 / 0). His follow-up (a bound
`&` put in a hole against one written there): answered as a reading: no difference; the same binding with no
surrounding rx reads under its own flags (run). NOT covered by r61 (frozen before it): name it in the delivery.
WAITING on: crit-predfold1119; Frank (next: class-value or group-truth).

## 2026-11-19 (22:45) — r61 handed back: NOT READY by one fix pass; dispositions ruled; fix lane predfix61 launched

r61 (5 critics, ~20 min): all 16 printed run lines held; answer-level: export statement 3 against 6/7 (a `_` part
leaks), "can never pass" wrong for NOT/default tests (four lenses), "whole surrounding rx" reaches private labels,
array of settings against passes, a class-member hole's order under a lift. Ruling-level: statement 3's "inside
view" is MY reading stated as ruled; his "ambiguous and therefore an error" unanswered. Every proposal accepted
(record entry, tip 1fa811754). New owner questions: flat-read-outside, bare-nested-scope, array-vs-passes,
class-hole-order. Lane predfix61 (opus, worktrees/predfix61 off 1fa811754; deliver + rulings files first;
lanewatch armed; told the 00:30 deadline) applies FIX-NOW and files the review. Coordinator stopped.
Process changes the coordinator proposed (for main, the skill is main's): name other lenses' root concepts in
each brief; drill a scope-WIDENING fold against every privacy/closing rule; name the two-valued pair when a fold
states a rule at one polarity; run every cited evidence script at the fold's tip.
LESSON (mine): three of my hand folds widened a scope in my own words ("whole surrounding rx", "inside view")
beyond his; quote, do not widen. WAITING on: predfix61; Frank (class-value / the four new questions).

## 2026-11-19 (23:00) — predfix61 merged; r61 filed; DELIVERED to main (P-14)

predfix61 DONE (lanecheck rc 0; hand-back checked against the report), merged, stopped: lint 5,242 / 0, plan-lint
clean, predfix61 model 15 / 0 and predasc model 24 / 0 re-run on my branch; no printed answer changed. r61 filed
RULED (docs/dev/reviews/2026-11-19-r61-predfold1119.md + directory; index line in reviews/NOTES.md, as r60's).
Four new open pieces: flat-read-outside, bare-nested-scope, array-vs-passes, class-hole-order (lift-order tag).
Not applied (mine to weigh): does label.unset also fire on an always-unset read; a note in predloop's superseded
model. His follow-up on flags (inherit before or after the intersection) recorded as a question, flags-before-and,
unanswered; the ruling stands as folded (before). P-14 written; main told.
WAITING on: main's merge; Frank (flags-before-and, class-value, the four new questions, then group-truth...).

## 2026-11-19 (23:15) — main merged P-14; his resolve-then-wrap proposal on flags recorded

Main merged 74f70152e (lints clean there); it applies the status line, r61's skill changes and my skill edit in
the morning, and prunes the lane worktrees then. Frank (discussion): an expression in a hole is resolved on its
own, then the result is inserted wrapped by the context options ("after"); it would reverse "both sides inherit"
as I folded it. Checked and told him: same answers as "before" except where the sides' case demands conflict (his
`[a-z]x & [A-Z]x`); bound-and-inserted equals inserted-whole under both; it collides with the ruled "a flag it
writes for itself wins" (`A & A` against `A` with `(?-i)`). Record tip 9d763c435. Nothing folded.
WAITING on: Frank (flags-before-and).

## 2026-11-19 (23:30) — flags-in-filter confirmed (before); a warning proposed to him

"I agree with the ruling that the environment of the hole sets the default options for the expression inside."
Folded by me (ruling item, his own proposal rejected by him, the `[a-z]x & [A-Z]x` line; lint 5,255 / 0). He
asked for a warning; proposed flags-warning (fire when the sides-first result differs from the expression alone
with the flag on its result; brute-force run on six examples, two WARN, four quiet). Not delivered yet (after
P-14). WAITING on: Frank (flags-warning).

## 2026-11-19 (23:40) — flags-warning RULED and folded

"flags-warning: yes when it works. You can't do it if the expression refers to $x a label in the literal". Row
`pcrec.flags.filter` (my placeholder) in the warnings table, a bullet on core/holes/flags/in-filter, rulings on
both; lint 5,267 / 0; tip after this entry. Not yet delivered (two folds since P-14: flags-before-and,
flags-warning): deliver with the next batch or at close; they were hand folds, so the next critic round covers
them with flags-in-filter. WAITING on: Frank (class-value next).

## 2026-11-19 (23:50) — /close of the third predicate-manager session

Nothing in flight at /close. wake.md rewritten from scratch; owner.md current; P-15 written; main told. On main:
everything through P-14. On my branch only: flags-in-filter with its confirmation and flags-warning (hand folds,
no critic round yet). Next session: /q, class-value first, then the four r61 questions; a critic round on the
three post-P-14 folds before the next delivery.

## 2026-11-21 (16:30) — fourth predicate-manager session: wake-up

Registered (role pred). Read wake.md, from_main (M-2 new), the three base files whole, the record from
bare-condition-labels to the end, the journal tail. Merged main into `lane/pred-rev28` (clean; lint 5,267 / 0,
plan-lint clean). Main had not merged P-15's three hand folds: branch is ahead of main by them. M-2 (Frank's
remark to main on rx / graph manipulation for intersection and subtraction, a LEAN) recorded verbatim in the
record; nothing folded. P-16 written (M-2 acknowledged). Nothing running. NEXT: /q with class-value first
(run: `$PCREC_TMPDIR/scratch/pred/classvalue.py`); a critic round on the three post-P-14 hand folds before the
next delivery (number from main first).
WAITING on: Frank (class-value).

## 2026-11-21 (16:50) — class-value RULED and folded

"ascending codepoints everywhere makes sesne." Folded by me (one ruling): record entry, lib/builtin/enumerate/
class-value to ruled (candidate (b) rejected as enumerate's order; class-base stays parked), pointers in
enumerate, core/arrays/class-order and its details; lint 5,279 / 0. Two readings of mine listed for the next lane
(a caseless single character; byte mode). On my branch only now: four hand folds since P-14. 14 open pieces.
WAITING on: Frank (flat-read-outside next).

## 2026-11-21 (17:10) — flat-read-outside RULED (a) and folded

His question back ("so the read is based on match not group?") answered and recorded; then "flat-read-outside: a".
Folded by me: the piece to ruled with both run lines (predfix61 FB), statement 3's clause, details ((b) and (c)
rejected), the parked user-doc trap. Lint 5,289 / 0. 13 open pieces. Five hand folds on my branch since P-14.
WAITING on: Frank (bare-nested-scope next).

## 2026-11-21 (18:00) — bare-nested-scope in discussion; the construction exercise run

He set my question's frame aside ("literals are not the way to think about it"; construction; fill order;
descending and horizontal; hole kinds). My leaning (a) as put withdrawn; a frame proposed (meaning on the finished
rx; shaping and matching holes; open or closed at a BINDING boundary). He asked for an exercise: build four rx from
macros only. Done (`$PCREC_TMPDIR/scratch/pred/construct.py`, 0 differing on all four); recorded with findings: his
bottom-up prediction supported; outer values reach a lower piece as READS PASSED AS ARGUMENTS; the closed rule
never pinched; the dollar-form warning, label hygiene and `[=year]` did. Nothing folded.
WAITING on: Frank (bare-nested-scope, his reaction to the exercise).

## 2026-11-21 (19:10) — pure-label RULED (a); three examples on scope; NOT yet folded

The bare-nested-scope thread: his three questions answered (my `inner($h)` rewrite corrected: it consumes; the
faithful closed form passes the condition); then his correction "a label is not a capture"; pure-label asked and
RULED: "captures are explicitly written either in literal form or using a macro like capture()"; a label-to-capture
add-on is needed (after the fact, for library labels; spelling open); `_` labels never export as captures; three
examples (C sees d through B(A); B's body may not name d; B may label its parameter). All recorded. NOT FOLDED:
pure-label moves export statement 5, core/labels/paths, labels-vs-captures, lib/structural/capture: a fold LANE
once the scope thread settles (with the readings listed in the record entry). On the branch: five hand folds since
P-14 plus this unfolded ruling; a critic round (number from main) after the lane.
WAITING on: Frank (the condition-as-argument edge of bare-nested-scope).

## 2026-11-21 (19:40) — zero-in-definition RULED (a); fold lane predscope launched

condition-argument withdrawn (his `B(A & (d: <100))` is equivalent, 0 of 19,530 differ; `when`'s ruled condition
test already answers it). "zero-in-definition: a" recorded. Lane predscope (opus; worktree `worktrees/predscope`,
branch `lane/predscope` from 36a74948f; deliver + empty rulings file written before launch; lanewatch armed) folds
pure-label, the `_` statement, zero-in-definition and his three examples, and tests the readings of today's
entries. NOT for the lane: the capture add-on's form (under construction), my frame (proposals).
WAITING on: lane predscope (delivery by lanewatch DONE + report); Frank (array-vs-passes next; it touches
core/labels/labels-vs-captures, which the lane edits: a ruling there goes to the rulings file or a follow-up fold).

## 2026-11-21 (20:30) — array-vs-passes (a) and joint-in-some RULED; lane predscope merged

Rulings recorded, NOT folded: array-vs-passes "option a" (the group questions and `h[k]` read the array of
settings; revises lib/counting's pass wording, group-truth, outermost-view's bullet); joint-in-some (a joint entry
inside a group question refused for now; same item written on the item; "no one would know to write it").
class-hole-order asked, not answered yet. Lane predscope DELIVERED (lanewatch DONE; tip e86e2ce0c), merged (lint
5,446 / 0; plan-lint clean), stopped. Its finding: my rule over his three examples is not supported as stated
(bound conditions and computed labels are outside it; his examples cover a parameter's labels only), so
bare-nested-scope stays open, narrowed to a label the USER of a definition sets. Three new owner questions queued
(zero-condition-binding, bare-nested-scope narrowed, capture-loop-value).
NEXT: a follow-up fold lane (predarr) for array-vs-passes + joint-in-some once class-hole-order is answered (it can
ride along); then a critic round over all of today's folds and the three of 2026-11-19 (number from main).
WAITING on: Frank (class-hole-order).

## 2026-11-21 (21:10) — class-hole-order RULED (a), folded by me; lane predarr launched

His correction first: the piece's example `/${[${c}] + 1}/` was not legal predicate language (it is `/${/[${c}]/ +
1}/`); corrected in the piece, recorded. Then "class-hole-order: a": folded (one piece; lint 5,459 / 0). Lane
predarr (opus; `worktrees/predarr`, branch `lane/predarr` from 96f25d7a0; deliver + empty rulings written first;
lanewatch armed) folds array-vs-passes (a) and joint-in-some and tests the readings of those two entries.
WAITING on: lane predarr; Frank (bare-nested-scope narrowed, next).

## 2026-11-21 (22:20) — bare-nested-scope RULED in two cases and folded by me

Case 1: "compile error at inner" (a piece may not name a label it does not hold). His label-variable question
answered (the parked label parameter; pass the condition or the set today). Case 2: "no, c" (letter unclear; his
loop reason checked: same under both, the loop resets), then, shown the witness pair against compose-equals-
literal, "lol. i meant b": own value only. Folded by me: core/holes/bare-condition/nested-scope to ruled (the
composed lines to rejected), bare-condition/labels' "Composed" line flipped to never matching with the
one-definition line beside it, reads' value-hole clause, a bullet on core/labels/flow for the exception; details.
Lint 5,487 / 0. Five readings of mine listed (the piece = a binding or macro body; user's loop; two uses).
Lane predarr still running. WAITING on: lane predarr; Frank (zero-condition-binding next).

## 2026-11-21 (23:00) — lane predarr merged; his "do you see an issue" answered

Frank asked for issues with bare-nested-scope as ruled: three told him (extracting a definition changes an answer,
with the never-pass warning at the definition; flags flow in, label values do not; what one piece is for a
twice-used argument or a user's loop). bound-condition asked, not answered. Lane predarr DELIVERED (lanewatch
DONE; tip 5133528c6), merged (lint 5,546 / 0; plan-lint clean), stopped. On the branch since P-14: the three folds
of 2026-11-19 and today's class-value, flat-read-outside, pure-label + zero-in-definition (predscope),
class-hole-order, bare-nested-scope (hand), array-vs-passes + joint-in-some (predarr). Review number asked of main.
NEXT: the critic round over all of it; then deliver (P-17).
WAITING on: main (review number); Frank (bound-condition).

## 2026-11-21 (23:20) — critic round r77 predfold1121 launched

Main gave r77. One opus coordinator `crit-predfold1121` (design mode; background) over the documents at
lane/pred-rev28 882bcf330 against main's 74f70152e: the three folds of 2026-11-19 and all of today's. Round dir
`$PCREC_TMPDIR/scratch/crit-predfold1121/`; standing lenses required (RULING; printed ruled examples re-derived in
every mode + legal programs; general form and unlocks); lane reports, earlier reviews and my journal/wake denied.
The subject stays FROZEN until the draft: rulings Frank gives meanwhile are RECORDED only, folded after the round.
WAITING on: the coordinator's hand-back (read the round dir at each wake); Frank (bound-condition).

## 2026-11-21 (19:20 EST) — close of the fourth predicate-manager session, at the owner's word

bound-condition asked twice; his two examples of `0` (a bare condition reads the rx it sits in; in `${A & (0:
S)}` only A) confirmed as ruled after my argument ("that settles it. my two examples are correct"); the named-
condition case still open. His "issue definition" recorded ("bindings define scope"; the `i`-only lean; the
list_of_stuff sketch, worked by me with a set-making macro). A misread run in the record corrected by an appended
entry. Then: "lets close the session now" and "don't cancel the subagents. let them finish".
IN FLIGHT, NOT CANCELLED: critic round r77 predfold1121 (critics and verifier done, the coordinator drafting;
round dir `$PCREC_TMPDIR/scratch/crit-predfold1121/`). Nothing else running; no cron. wake.md rewritten from
scratch; owner.md current; P-17 written; main told. On the branch only: the three folds of 2026-11-19 and all of
today's rulings. NEXT SESSION: rule r77's dispositions, one fix lane (it files the review), deliver (P-18), then
/q with bound-condition first.

## 2026-11-21 (19:45 EST) — r77 drafted (NOT READY); not ruled; session closed

The coordinator handed back after the close paperwork: draft at `$PCREC_TMPDIR/scratch/crit-predfold1121/review.md`,
verdict NOT READY; its first finding is an owner question (array-scope against own-value-only inside a used
piece); the rest FIX-NOW text and example fixes, several on my hand fold of bare-nested-scope and on the
bound-condition carve-out. wake.md's State and question queue updated; owner.md too. Dispositions NOT ruled
(session closing at his word): first act of the next session.

## 2026-11-22 (about 12:30 EST) — fifth predicate-manager session: wake-up; r77 ruled

Registered (`session_role pred`); main merged into `lane/pred-rev28` (one conflict, the lanes history index: both
sides kept); lint 5,569 / 0, plan-lint clean. Read core, library, parked whole; the record from zero-in-definition
to the end; r77's draft and process notes. RULED r77's dispositions (record entry of today): A1+A2 the owner
question array-in-piece (documents mark the collision meanwhile); A3-A5, A7-A9, A12 and D1-D12 FIX-NOW; A6 to be
verified by the lane, then PLAN; A10, D13 and the de-duplication PLAN; a new owner question helper-captures queued.
Witness for array-in-piece re-run by a hand-built simulation (`$PCREC_TMPDIR/scratch/pred/array_in_piece.py`).
P-18 written. NEXT: launch lane predfix77 (opus; files the review), ask him array-in-piece, then bound-condition.

## 2026-11-22 (afternoon) — array-in-piece and bound-condition ruled; predfix77 merged; P-19 delivered

RULED by him: array-in-piece (b) ("because B is bound first, its internal references refer only to what can be
seen at that point"; both in-place forms, `&` and SEQ, see A's h); bound-condition (b) ("mostly confirmed": `A :=
(x: blah)` and `A := /x/ & (y: blah)` are compile errors, computed labels bound alone with them; macro variables
and macro types under construction; `c := (0: 5)` left open by him). My leaning (a) and the "laid where it is
used" reading WITHDRAWN. Lane predfix77 (R-1, R-2, R-3 applied) delivered and merged: r77 filed and applied; lint
5,771 / 0. P-19 written. IN THE RECORD, NOT IN THE DOCUMENTS: bound-condition (documents carry it open with his
position). WAITING on him: count-in-set (he asked where `ch` is defined; answered). NEXT: his answer, then ONE
opus follow-up lane folding bound-condition (+ count-in-set), a critic round on that fold (number from main), P-20.

Main (2026-11-22): review number **r82** is ours for the bound-condition fold's critic round; main merges 399ef98f4 after reading P-19.

## 2026-11-22 (later) — five more rulings; predbound merged; predref running

RULED by him today after array-in-piece and bound-condition: count-in-set (b: a value left of `:`), binding-prefix
(1 yes: a group question through a binding's prefix reads every use; 2 a: a plain read with several uses is a
compile error), label-reference (required; the plain idiom included; his unqualified-after-definition idea parked
by him), helper-captures (the library's helpers set labels, not captures; `(?<:x>...)` his proposal). Values
allowed in the joint form (my reading withdrawn at his question). record-in-some CLOSED by me on his words of the
21st (told to him; no objection yet). Lane predbound (R-1..R-3) delivered and MERGED (915b47e64; lint 6,088 / 0;
its model 21 / 0). Lane predref (opus; worktree `worktrees/predref`) RUNNING: the label-reference sweep, the
"read flat" statements, helper-captures. NEXT: accept and merge predref; critic round r82 (number from main) over
today's folds (predbound + predref; subject = diff from 399ef98f4); rule it; fix lane; P-20. Question queue:
call-prefix, zero-condition-binding, count-several, capture-loop-value, zero-in-loop with the occurrences-argument
reading, macro variables / macro types (with declared labels), group-truth, every-pass-spelling, the older ones.

2026-11-22, his direction after closed-argument (not confirmed as a ruling: his lean (a) stands recorded): "do your followups and we can continue this conversation later". Lane predref delivered and MERGED (lint 6,205 / 0; its model 8 / 0; no answer changed by the sweep). Launching lane predcall (opus): call-prefix case 1, the A.d / c.d lines, his second hits example, closed-argument as an open piece with his lean, c.A. Then r82.

## 2026-11-22 (evening) — closed-argument ruled; predcall merged; critic round r82 launched

RULED: closed-argument (a) (and with it call-prefix case 2: `A.d` legal exactly where `d` is visible through the
call). Lane predcall delivered (R-1 applied) and MERGED: tip 6f1fe4e84, lint 6,289 / 0, its model 14 / 0. One
model defect it reported: the evidence models keep `_x` part-label groups visible (against export statement 6):
for the r82 fix lane. LAUNCHED: coordinator `crit-predfold1122` (opus, background), review r82, design mode,
subject = diff 399ef98f4..6f1fe4e84 of docs/design/predicates/, round dir
`$PCREC_TMPDIR/scratch/crit-predfold1122/`. The subject stays FROZEN until the draft: anything he rules meanwhile
is RECORDED only. WAITING on: the coordinator's hand-back (read the round dir at each wake). Frank: "do your
followups and we can continue this conversation later".

## 2026-11-22 (night) — r82 drafted and RULED; fix lane predfix82 running

r82 (five opus lenses + verifier): every printed example HOLDS (35 of 35), quotes 107 of 107; 44 findings, none
rejected. Answer-level: a name with two sources (ANS-1: OWNER QUESTION two-sources); the one-use plain read `A.h`
folded as ruled on what was a lean, and my Class sentence misdescribed his 2026-11-17 point 4 (CORRECTED by a
record entry; OWNER QUESTION idiom-confirm, with the isodate idiom taken on his silence); value entry inside a
group question; the tier of a path to an invisible label; nested paths; the index through a prefix across `&`
(the last four: my readings, ruled in the dispositions entry). Evidence: FOUR old models red or crashing at the
freeze, undeclared; two models exit 0 while red; the engine exports through `_x` part labels and double-lowers a
later `&` operand. RULED (record entry "2026-11-22 MANAGER — review r82"). Coordinator stopped. Lane predfix82
(opus; `worktrees/predfix82`, cut at 0f6a556bc) RUNNING: applies the fixes, one model with the engine fixes and a
successor check per old model, files the review as docs/dev/reviews/2026-11-22-r82-predfold1122.md. NEXT: accept,
merge, lint, P-20 (done line + [COND-FAMILY] status + the three process lessons as proposed skill edits +
worktrees to prune: predbound, predref, predcall, predfix82), SendMessage main. Questions for him, in order:
two-sources; idiom-confirm; then the queue in wake.md.

## 2026-11-22 (late) — predfix82 merged; P-20 delivered; nothing in flight

Lane predfix82 delivered (rulings file empty; all nine of my r82 readings supported; no printed line's answer
moved: 220 lines under the old and the fixed engine) and MERGED: lint 6,428 / 0, its model 22 / 0. Review r82
filed. P-20 written (done line, status line, seven worktrees to prune, four proposed skill edits). wake.md's State
rewritten. Owner questions next: two-sources, idiom-confirm.

## 2026-11-22 (late night) — default-export RULED protected; fold lane preddef running

After P-20: his C++ analogy (three of four matched; the default, A alone, was PUBLIC by hole-export); his example
`B := A & A`, `C := B & (B.a: 9)` ("B.a is always an error"); then RULED "default-export: protected": a part used
alone is available inside the binding and NOT exported. Reverses hole-export (2026-11-19) and export statement 3
for an unlabelled part. Lane preddef (opus; `worktrees/preddef`, cut at 0050e019a) RUNNING: rule pieces restated,
every printed program swept (explicit part labels to export), his analogy as a table, a model implementing the
protected default with a SUCCESSOR check over all older models. Two NEW owner questions, neither applied:
argument-default (the caller's own `A.d` for an argument through a bare `${rx}`: his example 1 of the 21st and
closed-argument against the new default); capture-export (does a capture in rx text deep inside bare-used parts
still reach the caller). Asked main for a review number (REPLY pending). NEXT: accept and merge preddef; critic
round with main's number (subject = diff from 30ca2520d); rule; fix lane; P-21.

Main (2026-11-22): review number **r83** is ours for the default-export fold; P-20 (30ca2520d) is merged and pushed on main.

## 2026-11-22 (night, later) — export-list ruled; preddef merged; critic round r83 launched

RULED after default-export: export-list ("Export list: yes": `[(=year) = isodate]`, the named binding list on a
part label; one form, two targets; his caveat "bindings used to scope labels (A.a: 8)"). AGREED framing (not a
ruling): two base kinds of name, LABEL and BINDING, with properties; "captures can have no label" (his note: the
label and capture properties are independent, four cells). His observation: label-reference solves a used
binding's label hiding a binding. Lane preddef (R-1, R-2 applied) delivered and MERGED: tip 3e58abe9e, lint
6,645 / 0, its model 22 / 0, 229 printed lines with no answer moved; 5 programs now compile errors, 10 kept
"(awaits argument-default)". Its own reading, for the round: a labelled part still passes `pub.h` by name.
LAUNCHED: coordinator `crit-preddef1122` (opus, background), review r83, subject = diff 30ca2520d..3e58abe9e,
round dir `$PCREC_TMPDIR/scratch/crit-preddef1122/`, with a NAMES lens (the name-resolution table). The subject
stays FROZEN until the draft. FOR THE r83 FIX LANE (beyond the round's findings): the name table as one piece
(two kinds, the four-cell label/capture table, his agreement quoted); the hide-label warning's trigger and
parked/ideas/label-hygiene restated (his observation). Owner questions: argument-default, capture-export,
two-sources, idiom-confirm.

## 2026-11-22 (night, later still) — program-options and hole-flags RULED (recorded only; subject frozen for r83)

RULED: program-options (yes: a statement sets flags for the literals written after it in the same file; `m`,
`s`, `n`, `x` first; never across an import; a literal's own flags win) and hole-flags (yes to all: `i` has a
weak per-file value that does not propagate; at a hole only an EXPLICIT `i` / `-i` is inherited; `m` and `s` no
longer inherited: reverses the 2026-11-19 list). His reason: consistent with the other program-level settings.
NOT FOLDED: the documents are frozen for round r83. PLAN: after r83's fix lane merges, ONE opus fold lane
(predflags) for these two rulings (core/patterns/flags, core/holes/flags and in-filter, lib/builtin/options, the
warnings row, any_case, the examples resting on an inherited `m`/`s` or a non-explicit `i`), then its own critic
round (ask main for the number), then delivery.

## 2026-11-22 (very late) — r83 drafted and RULED; fix lane predfix83 running

r83 (five opus lenses incl. the NAMES grid, + verifier): every printed line agrees; no undeclared evidence red.
Answer-level findings all sat in grid cells no printed line reaches: the evidence engine accepts what the text
refuses (the `&` ambiguity from outside / through a part label / through an export list; an export list through
a call; bare `$h`, `h[2]` across `&`); argument-default's question misstated its consequence (FIXED before he is
asked); two cases decided twice. RULED (record entry "2026-11-22 MANAGER — review r83"): my readings on A4 (an
outside read sees exported settings only), A5 (a binding's name reaches its unlabelled uses only), D4, D8, the
cross case; CORRECTION: default-export also narrows label-flow (b) and bare-nested-scope case 2 for the user;
idiom-confirm CLOSED on default-export (the statement put to him was "available locally as `A.h`"). Coordinator
stopped. Lane predfix83 (opus; `worktrees/predfix83`, cut at 8619d21f1) RUNNING: the fixes, a successor model
with the NAME-GRID check, the name table piece, the hide-label / label-hygiene restatement, the review filed as
docs/dev/reviews/2026-11-22-r83-preddef1122.md. It does NOT fold the flag rulings. NEXT: accept, merge, lint,
P-21 (done + status + worktrees preddef, predfix83 + the round's skill edits P1-P5), SendMessage main. THEN the
flags fold (lane predflags + its own round; ask main for the number). Owner questions, in order:
argument-default (with its library face), capture-export, two-sources; tell him: idiom-confirm closed, the
correction, and the S1 view (textual ownership as a principle) if he wants it.

## 2026-11-22 (very late, 2) — argument-default, wrapper-export, transform-export RULED (record only)

RULED while predfix83 runs (NOT folded; the documents carry argument-default as open): argument-default: an
error, with his PRINCIPLE "The label is not to the regex abstractly, it's to the spot in the pattern where the
regex is being inserted" (an argument is a template); wrapper-export (a) (`peek`, `atomic`, `when`, `list_of`,
the gap bodies write `[(=) = A]` on the spot); transform-export: yes (the convention for every provided body
that places its argument); his pair `hide(x) := /${x}/`, `identity(x) := /${[(=) = x]}/` (examples; not ruled
as provided names). My reading told to him: a label written ON an argument at a call (`B([a = A])`) is a
compile error; a group inside an in-place argument is not the caller's to read (answers two-sources' first
shape). THE NEXT FOLD LANE (after predfix83 merges and P-21) carries FIVE rulings: argument-default,
wrapper-export, transform-export, program-options, hole-flags; then its own critic round (ask main for the
number). A principle piece for "a label is to the spot" (core/principles; his words; the name mine).

## 2026-11-22 (very late, 3) — predfix83 merged; P-21 delivered; fold lane predspot running; r84 assigned

Lane predfix83 delivered (rulings file empty; NAME-GRID 96 cells: 89 agree, 0 disagree, 7 undecided, all
argument-default's; one answer changed by my A5 reading: `[a = A] SEQ A & (A.h: <5)` now reads the unlabelled
use) and MERGED: lint 6,830 / 0, its model 25 / 0. Review r83 filed. P-21 written and sent to main (tip
75d2318bd); main merges after the kit's U4 lands. Main gave review number **r84** for the next fold's round.
Lane **predspot** (opus; `worktrees/predspot`, cut at 75d2318bd) RUNNING: the five rulings in two groups
(labels: argument-default, wrapper-export, transform-export, the principle piece "a label names a spot"; flags:
program-options, hole-flags), a model with the NAME-GRID decided and a FLAG-GRID. NEXT: accept, merge, lint;
critic round r84 (design mode; subject = diff 75d2318bd..tip; lenses RULING, EXAMPLES, GENERAL, NAMES grid, a
FLAGS grid lens, fix-induced); rule; fix lane; P-22.

FOR THE r84 FIX LANE (spelling side; no meaning moves): his reading of `[a = A]` (the brackets are the array / grouping; `a = A` the label set of the expression language; `[a = A | b = B]`); my four precedence points (label set looser than SEQ and `&`, tighter than `|`; written only inside `[ ]` or directly in a hole, so `${=rx}`; never bare in `( )`): my syntax reading, not ruled; `[ab = B | A]` (six places in core.md) becomes `[ab = (B | A)]`; the comma form `[a, b, c]` kept for now as `a | b | c`; the precedence table row 9 restated. Also: `A(rx) := /${=rx}/`, `A.rx`, `A.rx.g` as the third small form beside hide / identity.

2026-11-22 (latest): RULED capture-export in two parts (a named group in a part of a composed program is NOT a capture by default; the program-level `capture(path)` asks for one; explicit captures returned from the artifact against implicit ones the language needs). RECORD ONLY: predspot is running and r84 follows; this fold (export statement 5, labels-vs-captures, lib/structural/capture and its add-on, caller-ambiguous, the name table four cells) goes to the lane AFTER r84 with its own round, together with the label-set spelling notes if the r84 fix lane has not taken them.

2026-11-22 (latest, 2): RULED zero-condition-binding: an error, to be reconsidered later (his reasons recorded). RECORD ONLY; a single-piece fold (core/holes/bare-condition zero-binding piece, the two candidate lines to rejected): by hand or with the capture-export lane after r84.

## 2026-11-22 (night's end) — predspot merged; critic round r84 launched

Lane predspot (nudged once after 25 quiet minutes on its background plant run) delivered and MERGED: tip
e6e95a2c5, lint 7,034 / 0, its model 27 / 0 (29 plants caught), NAME-GRID 144 cells all agree, FLAG-GRID 128
cells (78 agree, 0 disagree, 50 n/a). Folded: argument-default (an error), wrapper-export, transform-export, the
principle piece, program-options, hole-flags. One answer changed in group 1 (the two-use body now reads the
labelled spot); none of the printed flag lines (all four had an explicit `(?i)`). LAUNCHED: coordinator
`crit-predspot1122` (opus, background), review r84, subject = diff 75d2318bd..e6e95a2c5, round dir
`$PCREC_TMPDIR/scratch/crit-predspot1122/`, lenses RULING, EXAMPLES, NAMES grid, FLAGS grid, fix-induced +
general. Subject FROZEN until the draft. NEXT: rule r84; ONE opus fix lane (files the review; ALSO the spelling
notes: label set, `${=rx}`, `[ab = (B | A)]`, the comma form, the third small form `A(rx) := /${=rx}/`); merge;
P-22. THEN a fold lane for capture-export and zero-condition-binding with its own round (ask main for a number).

## 2026-11-22 (close) — /close at the owner's word: "Let's discuss these pain points next time."

After the predspot merge and the r84 launch: RULED capture-export (two parts) and zero-condition-binding (an
error for now), both RECORD ONLY; his reading of `[a = A]` and of arrays (spelling notes); his question
`A(rx) := /${=rx}/` (legal: a label on the spot); and the JSONL EXERCISE he asked for (library updated, a search
built, values returned for fields not searched on, run on a hand-lowered model; seven findings; record entry
"2026-11-22 MANAGER — the JSONL capture exercise he asked for"). He closes with: discuss the pain points next
time. wake.md REWRITTEN from scratch (the pain points first). IN FLIGHT AT THIS ENTRY: critic round r84
(coordinator `crit-predspot1122`), NOT interrupted; the next line of this journal says whether its draft had
arrived when the session closed.

## 2026-11-22 (close, last line) — r84 DRAFTED, NOT RULED; coordinator stopped; session closed

The coordinator handed back after the close paperwork: draft `$PCREC_TMPDIR/scratch/crit-predspot1122/review.md`
(critic texts + verify.md in `review/`, process in `.coord/process.md`); freeze e6e95a2c5 (the branch moved to
2a67e7f63 mid-round by record / journal entries only, mapped under its FREEZE NOTES). Its hand-back: evidence
re-run green (predspot 27 / 0) but SWEEP passes over 9 printed lines the model answers wrongly (B7; the documents
are right in those rows); answer-level in the documents: A1 (reading (e) false when `@options` comes mid-file), A2
(a bound `&` in a hole under file options), A3 (the program option `x` revises a 2026-11-14 ruling without naming
it; "No implicit extended mode" now false), A4 (reading (a) reverses his 2026-11-17 "yes" to
`rx.repeat([a = rx.digit])`), A5 (`prefix_in` exempted though it places S), A6/A7 (neither root has ONE deciding
statement; undecided cells listed); in the evidence: B1 (an answer flips when a binding is named like the macro's
parameter), B2, B3 (label-reference bypassed inside an argument), B5 (grid arms that cannot fail). Proposed
FIX-NOW: A1-A8, B1-B5, B7, C1-C8, D1-D7; four owner questions proposed (repeat-label, spot-read-name,
option-hole-explicit / options-reach-constants, options-position). NOT RULED: first act of the next session, as
wake.md says (read the draft WHOLE first; A4 is a ruled-words finding: read his 2026-11-17 entry before ruling).

## 2026-11-23 — sixth session: wake

- Registered (`session_role pred`); wake.md, the channel (nothing after M-2), core.md (first half whole, second half by
  heading and statement), the record's last entries read. main merged into `lane/pred-rev28` cleanly (155 commits);
  lint 7,049 / 0; `make -s test-plan-lint` green; P-21's tip 75d2318bd is on main. Main told (no reply asked).
- r84 (`$PCREC_TMPDIR/scratch/crit-predspot1122/review.md`, 270 lines): still to rule; not read yet this session.
- First question put to the owner: label-name-hole, with the run `$PCREC_TMPDIR/scratch/pred/label_name_hole.py`
  (a path model of `[r = kv("ts", /\d+/)] & (r.ts: <5)`). Waiting on his answer.

## 2026-11-23 — the label parameter (JSONL pain point 1) discussed; two rulings

- label-name-hole as first put: withdrawn in half (his correction: no hole at the expression level); the k
  restrictions proposed; his point that a hole-named label is not "textually defined" (true of the ruled name hole
  too; my hole-named-label proposal set aside by his two approaches).
- WORKING DIRECTION (tentative, his): a macro takes a LABEL (`A(l:) := /(?<:${l}>\d+)/`, `A(x:) & (x: 5)`;
  `row(dt:, "date", isodate) & (dt.year: 2000)`). Same label twice: the standard rules (run).
- RULED: label-parameter-omitted (`_` is the unspecified label; no argument omitted under the current call rules;
  label args not special by position or requirement); label-parameter-default (yes, a label may be an optional
  parameter; spelling lean `l = ts:`). IDEA to park: the empty position `row(,"level", ..)`.
- NOT FOLDED: all of it (record only). Fold lane's list grows: capture-export, zero-condition-binding, the label
  parameter (label-variables piece, the name hole taking a label, the JSONL sketch), the parked empty position.
- Asked next: capture-place. r84 still to rule.

## 2026-11-23 — captures and labels in arguments: seven more rulings (record only)

- capture-place: his LEAN (a), an `&` operand taking a label reference; early capture "no crime".
- RULED: capture-twice (a); label-kinds (one mark = the setting kind; references native-only); capture-name (a);
  array-capture (yes: `capture(x)` the label, `capture(@x)` the array, unbuilt; capture-as-pcre dropped;
  capture-loop-value closed as the label; plan rows [CAPTURE-ARRAY] / [ARRAY-CAPTURE] found; P-23 notice to main);
  argument-export (yes, by his "this aligns with my understanding": told to him as the reading taken);
  label-in-argument (a sent label is ok, passes `_`: "an accepted backdoor"); argument-label (yes: my readings (a),
  (b) of argument-default withdrawn).
- MY CORRECTION: "ts.year is a compile error as the rules stand" was over-claimed; withdrawn the same turn he asked.
- OPEN with him: what he meant by threading the label to `string`; the optional-member idiom; duplicate keys; what
  is left of ambiguity-per-name; a label pre-defined as a symbol; the empty argument position (to park).
- NOT DONE: r84 dispositions; nothing of 2026-11-22 (late) or 2026-11-23 is folded. The fold is now a LANE (many
  pieces: label-variables, name hole, argument-default, two-sources, closed-argument, capture, capture/add-on,
  capture-export, caller-ambiguous, labels-vs-captures, zero-binding, lib/json sketch, parked empty position).

## 2026-11-23 — the capture shape moved to the set side; optional-label ruled

- His proposal `(isodate.year: capture("year"))`; capture-absent; his `capture("h")?`; his `(h?: capture("h"))`.
- RULED: optional-label (`(h?: S)` holds when h is absent or in S). The capture shape is now set-side
  (`capture("name")` = `anything` with a request); it REPLACES the morning's `capture(path)` operand (his lean) and
  the `name =` keyword of capture-name (a). capture-twice (a) and array-capture carry over.
- FLAG filed at his word: optional-label-general (special form or general; `(h+: blah)`).
- MY ERROR: one run line and a note were written into the record before the run was read; corrected by an appended
  correction entry the same turn; the owner was shown the run's output only. Rule: paste run output, never pre-write it.

## 2026-11-23 — close (/close)

- Nothing in flight. wake.md rewritten; owner.md current; the record holds every word of the day. r84 NOT ruled;
  nothing of 2026-11-22 late or 2026-11-23 folded. P-24 posted; main told.

## 2026-11-23 — seventh session: wake; r84 ruled; lane predfix84 launched

- Registered; wake.md, the channel (nothing after M-2), core.md / library.md / parked.md WHOLE (in parts), the record
  from "label-name-hole as first put" to the end, r84's draft whole. main merged cleanly; lint 7,185 / 0; plan-lint green.
- r84 RULED (record entry "2026-11-23 MANAGER — review r84 (predspot1122)"): the flags group and the evidence fixes
  to FIX lane predfix84; A4, A7, C3, C4, C5, D2 OVERTAKEN by argument-label and handed to the fold lane; repeat-label
  not asked (the record answers it); four owner questions queued (options-position, option-hole-explicit,
  options-reach-constants, spot-read-name).
- LAUNCHED: lane predfix84 (opus, worktree `worktrees/predfix84`, cut at 2d6270c10; deliver + empty rulings file
  written first; `lanewatch --follow` armed). Main told; review number r86 reserved for the fold (predfold1123).
- Found while preparing the first question: an optional mark on the label (`m?`) existed on 2026-11-16 and was
  DROPPED by him the same day ("drop-mark: YES"); its meaning then was "some value the label could have had" (not a
  test of one row). The mark ruled on 2026-11-23 is a one-row test (absent or in S). Parked pieces that say "there
  is no optional mark" (default-set, empty-value, macro-warning) move at the fold. To tell him.
- ASKED: optional-label-general, with the run `$PCREC_TMPDIR/scratch/pred/optional_general.py`. Waiting on him;
  predfix84 in flight.

## 2026-11-23 — seventh session: the entry operator `?:`; label-forward ruled

- optional-label-general: his lean "a special case"; optional-place answered "Before the colon" (my reading: the
  place is ruled); his PROPOSAL / lean: a second entry operator `?:` beside `:` (so `?` has one meaning). I write it
  that way in the fold unless he objects; `h+` / `h*` and `(a?, b)` then do not arise. Ideas recorded, not ruled:
  `?` for optional macro parameters without defaults (meets call-forms (b)); a value left of `:` with no label
  (`("Frank": S)`: legal by the sentence as written, my reading).
- string-label: his intent recorded (the row's label on the data, sent through to `string`).
- RULED: label-forward: yes. Answered with runs: a filter over two rows at the line; several keys in one row.
- ASKED: capture-negated. predfix84 still in flight.
- Scratch models of the day: optional_general, optional_place, label_forward, line_combined, capture_negated
  (`$PCREC_TMPDIR/scratch/pred/`): hand-lowered; the fold lane rebuilds them mechanically.

## 2026-11-23 — predfix84 delivered and merged; P-25 done: to main

- Lane predfix84 (nudged once: it idled on a sabotage run that had finished) delivered: lanecheck DONE, tip
  97549667e; MERGED into `lane/pred-rev28`; lint 0 failed; plan-lint green; model 37 / 0, 43 plants caught, 0 answers
  moved over 216 printed lines. Review r84 FILED. Lane stopped. P-25 `done:` posted; main told.
- Since the last entry: capture-negated RULED, broadened by him (no effect macro under a negation); two-sources'
  second shape CLOSED on label-reference at his question; zero-in-loop ASKED (waiting).
- NEXT: the FOLD lane (r86, predfold1123) for 2026-11-22 late + 2026-11-23, with the six overtaken r84 findings and
  the lane report's LEFT FOR THE FOLD LANE list; brief after his zero-in-loop answer or at the next pause.

## 2026-11-23 — zero-in-loop and binding-fixed ruled; fold lane predfold1123 launched

- RULED: zero-in-loop (b); binding-fixed: yes (a new principle; confirms "two uses of one piece are two pieces").
  Main merged P-25 (014ebc42f).
- LAUNCHED: lane predfold1123 (opus; worktree `worktrees/predfold1123`, cut at e420369c5; deliver + empty rulings
  file written first; `lanewatch --follow` armed): the fold of the record from "a question on transform-export:
  `A(rx) := /${=rx}/`" through "binding-fixed: yes", with r84's six handed-over findings. Its review is r86
  (coordinator to launch at its delivery). Later rulings of this session go to its rulings file as R-n.
- To do without asking him: options-position's first half is in his own words ("in future bindings"; the ruled
  statement "literals written after the statement"): close it as "from the statement on" (an R-n for the lane);
  repeat / turning a flag off stay unstated.

## 2026-11-23 — zero-open ruled; the call-forms play-out written at his request

- RULED: zero-open, all four (R1 in predfold1123's rulings file). Discussion recorded: his count-prefixed list
  example, "length(0:)", `0` as the one open name.
- call-forms: his lean (b) ("i like your suggestion"), `repeat(X, _, 5)` "is 0 up to 5", and a request to play it
  out (nine questions, two levels). WRITTEN as the record entry "2026-11-23 MANAGER — the play-out he asked for"
  (a proposal throughout): a head is a binding list and a call binds it against the argument record; omitted /
  unspecified `_` / open kept apart; array = lift, tuple = positions, map = names; a user macro taking a macro,
  with its termination cost. Runs: `$PCREC_TMPDIR/scratch/pred/call_forms.py`. He "will be back later to go over".
- IN FLIGHT: lane predfold1123 (R1 pending in its file). r86 round to launch at its delivery.

## 2026-11-23 — predfold1123 delivered and merged; critic round r86 launched

- Lane predfold1123 delivered (lanecheck DONE; R1 zero-open applied): MERGED (026090af8); lint 7,902 / 0;
  plan-lint green; model 18 / 0, 24 plants caught. Folded: every ruling from 2026-11-22 late through zero-open.
  Answers changed are listed in its report (two-sources' line; five programs legal again under argument-label;
  `c := (0: 5)` an error; the two-argument capture wrapper to rejected). Lane stopped.
- Its note for after the review: zero-open's two record entries were not in its worktree, so four pieces cite them
  in history lines only (match-so-far, reads, warnings, capture) and core/values/reads keeps its 2026-11-22 date:
  the r86 fix lane turns them into rulings items.
- Owner questions the lane left, by slug: label-set-precedence (`[a = A | b = B]`), question-request,
  effect-in-guard, array-request-spelling, label-parameter-dollar (optional-label-general is closed by his `?:`
  lean: check how the lane wrote it).
- LAUNCHED: coordinator `crit-predfold1123` (opus, background), review r86, subject frozen at 026090af8, scope
  014ebc42f..026090af8, round dir `$PCREC_TMPDIR/scratch/crit-predfold1123/`. NOT a delivery to main until r86 is
  ruled and its fix lane lands.
- WAITING ON HIM: the call-forms play-out (he said he would be back to go over it).

## 2026-11-23 — r86 drafted and ruled; fix lane predfix86 launched; call-forms discussion continues

- r86 (coordinator `crit-predfold1123`, 5 opus lenses + verifier; 46 items, 0 refuted; draft
  `$PCREC_TMPDIR/scratch/crit-predfold1123/review.md`): RULED (record entry "2026-11-23 MANAGER — review r86").
  Three findings were errors of MY fold brief: the joint and value `?:` lines printed legal against the asked
  statement's conservative edges (A1); optional-label-general closed on my thought (A1); his call spelling
  `l = ts:` taken as a head default (A8). Coordinator stopped.
- LAUNCHED: lane predfix86 (opus; worktree `worktrees/predfix86`, cut at a05795469; deliver + empty rulings file
  first; lanewatch armed). It also folds label-hole-full (ruled mid-round) beside A15 and files the review.
- With the owner since the fold: label-hole-full RULED (by kind of group); count-unspecified RULED (an unspecified
  count bound by meaning); DISCUSSION: `repeat(A)` as `A*`, unset against the underscore, his conditional repeat
  head (same table as head (i) but for a written 0), the `? :` / `?:` spelling collision, "meet me half way".
  ASKED: unspecified-rule; WAITING: repeat-head. None of the call-forms material is folded (a later fold).
- LESSON (his): a lone underscore VANISHES in his chat UI: fenced code blocks or the word (memory saved).
- Queue additions from r86: closing-own-label, capture-in-set, optional-entry-edges.

## 2026-11-23 — predfix86 delivered and merged; P-26 done: to main; six more rulings for the next fold

- Lane predfix86 (one STOP on A2, answered as R2; R1 = closing-own-label) delivered: MERGED; lint 8,163 / 0;
  plan-lint green; model 29 / 0, 36 plants caught. Review r86 FILED. P-26 `done:` posted, main told (asked for
  the next review number, topic predfold1123b). Lane stopped; nothing in flight.
- RULED since the fold's cut (record only; the NEXT FOLD): count-unspecified; unspecified-rule ("yes and
  elegant"); call-forms (one head per name, four lines); repeat-head (head (i)); closing-own-label (folded by
  predfix86 as R1; its `rulings:` items owed); binding-as-label (his four conditions; REVERSES argument-default's
  error and the labelled-spot legal lines; answers spot-read-name). Also label-hole-full (folded by predfix86).
- For the next fold's brief (r86 A1/A8 lesson): QUOTE each ruling's asked statement with its edges; do not
  summarise. Pieces: call-forms, bindings (positional / named, defaults), lib/rx/repeat (one head), lib/modifiers/
  padded (the width form renamed), core/holes/count (unspecified bounds), a piece for the unspecified mark,
  binding-prefix / argument-default / closed-argument / call-prefix / arguments (the shorthand's four conditions
  and the table), export statement 7's rulings item, the parked compile-time conditional, G1's ownership table if
  label-doors is ruled.
- ASKED, waiting: label-doors (the four-line general rule). Queue: capture-in-set; optional-entry-edges (stays as
  ruled unless he wants it); the three flags questions; a map written in place; a user macro taking a macro.

## 2026-11-23 — label-doors ruled; fold lane predfold1123b launched (review r88 to follow)

- RULED: label-doors, five lines (owned by the text that writes it; a path is a chain of labels; a binding's name
  as a skipped label under his four conditions; each part decides its doors, closing one closes only that one;
  stacked labels are equal names of one spot). Before it: his two-label body (agreed, run); my reading (a) of
  label-parameter-omitted WITHDRAWN (an unspecified label on a part is the part with no label, not the blank mark).
- Main merged P-26 (7b61fd62a); r88 reserved for this fold's review.
- LAUNCHED: lane predfold1123b (opus; worktree `worktrees/predfold1123b`, cut at 89d26b6b3; deliver + empty
  rulings file first; lanewatch armed). Scope: every ruling after zero-open: count-unspecified, unspecified-rule,
  call-forms, repeat-head, binding-as-label (reverses argument-default's error), label-doors with ONE ownership
  table; rulings items for closing-own-label and label-hole-full; parked pieces for the play-out's level 2 and the
  compile-time conditional. The brief makes each ruling's ASKED statement the source (the r86 lesson).
- NEXT: at its delivery: merge, lints, coordinator `crit-predfold1123b` for r88 (design mode; the standing lenses
  plus the EXPANSION drill and a grid over the ownership table), rule, fix lane, P-27.
- Queue with the owner: capture-in-set; optional-entry-edges; the three flags questions; a map written in place; a
  user macro taking a macro; the older list; the spellings review.

## 2026-11-23 — close (/close): predfold1123b delivered and merged; r88 NOT launched

- Lane predfold1123b delivered (lanecheck DONE; rulings file empty throughout; nudged once to poll its sabotage
  run): MERGED (3c6462b24); lint 8,502 / 0; plan-lint green; model 18 / 0, 25 plants caught (its first plant run
  missed 3: fixed and re-run). Lane stopped. It refuted two lines of my spot-read-name working (pre-condition-4);
  neither was written.
- NOT a delivery: the fold is unreviewed. r88 (reserved by main) is the FIRST act of the next session, before any
  question to the owner; a parallelism lens on the evidence model joins it (the owner's item, via main).
- Main, the same hour: P-17..P-26's skill edits merged (24 items); the polling exception for predicate lanes
  granted; the [COND-FAMILY] row's next line updated.
- wake.md REWRITTEN from scratch; owner.md current; P-27 (pausing) posted; main told. Nothing in flight; no cron.

## 2026-11-23 — eighth session: wake

- Registered (session_role pred); main merged into `lane/pred-rev28` (one routine conflict in the lanes history
  index, both sides kept): tip d3ca4a5ef; lint 8,502 / 0; plan-lint green. Main told.
- LAUNCHED review r88: coordinator `crit-predfold1123b` (opus, background), subject frozen at d3ca4a5ef, scope
  `git diff 7b61fd62a..d3ca4a5ef -- docs/design/predicates/`, six lenses (ruling, examples + expansion drill,
  fix-induced + general form, names grid over the ownership table, check adequacy, parallelism of the model).
- Read whole: core.md, library.md, parked.md; the record from closing-own-label to the end.
- ASKED the owner: list-is-label (run: the list body in three modes; the parting case of two arguments holding
  one name, `W.h` the last mention against `A.h` A's own spot). Waiting on his answer and on r88's hand-back.

## 2026-11-23 — review r88 ruled; fix lane predfix88 launched

- r88 draft (28 items, A1-A18 / B1-B10; none refuted, none rejected): RULED in the record ("MANAGER — review r88
  (predfold1123b): the dispositions"). Main evidence finding B1: the fold's SUCCESSOR check ran no predecessor
  (13 models dead at load, declared superseded); my "over ten minutes" premise was wrong (6 s).
- LAUNCHED lane predfix88 (opus; worktree `worktrees/predfix88`, cut at b63928b48; deliver + empty rulings file
  first; lanewatch armed): documents A1-A18 (G4 table only), evidence B1-B9, files the review. PLAN: G3, NAMES-5,
  B10 (re-measure after B1).
- New owner questions queued: exact-count-unspecified, stacked-chain, nested-made.
- Coordinator crit-predfold1123b stopped. Waiting: the owner's answer on list-is-label (if it arrives while the
  lane runs: R-1 in its rulings file); the lane's delivery.
- For main at P-28: three lessons + three proposed critic-skill changes from r88's process.md.

## 2026-11-23 — shorthand-is-callers RULED (reverses my reading (a) of binding-as-label)

- His question on list-is-label exposed that "made by anyone, the body included" was MY addition to his fourth
  condition. RULED: the shorthand is the caller's own label, `B(A)` + `A.d` = `B([A = A])`, whatever the body
  does, the closing body included. Dissolved: list-is-label, both-uses, pair-twice-alone, nested-made, r88 A4.
- predfix88 (running) got R-1, a notice: do not fold it, skip nested-made, list what will be reversed.
- NEXT: at predfix88's delivery: merge, lints, then fold lane predfold1124 (the ownership table's argument row,
  argument-default, closed-argument, call-prefix, label-reference, the six library reads, the lines "Both uses");
  it needs a review number from main before its critic round.
- ASKED the owner: capture-in-set.
- LESSON: a reading of mine attached to HIS condition and carried inside the statement he says yes to is still
  mine; a table derived through it must say which rows rest on the reading (he ruled the table, not the intent).

## 2026-11-23 — predfix88 delivered and merged; P-28 posted; label-tree asked

- Lane predfix88 delivered (lanecheck DONE; R-1 applied; delivery pins for the predecessors ACCEPTED): MERGED;
  lint 8,650 / 0; plan-lint green; model 25 / 0, 39 plants caught; full run 62 s (B10's trigger not met). Review
  r88 filed. Lane stopped. P-28 `done:` posted, main told, a review number asked for predfold1124.
- RULED by the owner since: capture-in-set: error; exact-count-unspecified: error (his count-0 proposal not taken
  by his own answer). His discussion on the shared operators recorded; a parked piece is owed (a form of its own
  for effects; a condition operator).
- My closure of stacked-chain WITHDRAWN at his objection; his framing (flat inside a binding, the tree from
  outside; `[_t = A]` is `[_ = [t = A]]`) put back to him as the ruling label-tree, with the by-name read from
  outside as the edge. ASKED; also waiting: options-reach-constants (asked before his framing arrived).
- NEXT: fold lane predfold1124 once label-tree is answered (scope: shorthand-is-callers, capture-in-set,
  exact-count-unspecified, label-tree, the three closures that stand (options-position's position half, the
  argument half of options-reach-constants), the parked effects piece).

## 2026-11-23 — main merged P-28; r90 reserved

- Main: P-28 (0dda97065) merged on main (push follows CI). Review number r90 is reserved for predfold1124's round.
- Last REVIEWED tip is now 0dda97065. Waiting on the owner: label-tree, then options-reach-constants.

## 2026-11-23 — path-rules RULED; fold lane predfold1124 launched (review r90 to follow)

- His four path rules (a start and a target in the label DAG; no underscore label on the path unless it is the
  start; any label of the binding may start; a middle label may be skipped where unambiguous) + my two readings +
  rules 5 and 6 across bindings: RULED ("path-rules: yes"). It replaces label-tree and my readings (b), (c) of
  label-doors; stacked-chain answered (the chain is legal); two printed lines become compile errors.
- LAUNCHED lane predfold1124 (opus; worktree `worktrees/predfold1124`, cut at 172930848; deliver + empty rulings
  first; lanewatch armed). Scope: shorthand-is-callers, capture-in-set, exact-count-unspecified, path-rules, two
  standing closures (options mid-file; an argument literal takes the caller's file's options), the parked
  effects piece. Not ruled, kept open: the constant half of options-reach-constants (ASKED).
- NEXT: at its delivery: merge, lints, coordinator `crit-predfold1124` for r90 (design; ruling lens on the ASKED
  statements, examples + expansion drill, fix-induced + general form, names grid over the path rules, check
  adequacy incl. the header-mutation drill), rule, fix lane, P-29.
- LESSON (third time this session a closure or extension of mine was overturned by his next message: by anyone
  the body included; never chain; X.m.h an error): when I "apply his sentence literally" I keep extending it
  past the case it was asked on. Before closing a queued question on the record, check WHICH CASE his sentence
  was asked about and say so; a closure outside that case is asked, in one line, not closed.

## 2026-11-23 — close (/close): predfold1124 delivered and merged; r90 NOT launched

- RULED by the owner before the close: options-reach-constants: yes; option-hole-explicit: explicit (both sent to
  the running lane as R-1, R-2 and folded). ASKED, not answered: not-test.
- Lane predfold1124 delivered (lanecheck DONE; R-2 the last ruling applied): MERGED; lint 8,811 / 0 after I added
  the two `rulings:` items it could not cite; plan-lint green; model 20 / 0, 20 plants caught, 15 predecessors
  re-run, 50 reds declared verbatim; full run 66 s. Lane stopped.
- NOT a delivery: the fold is unreviewed. r90 (reserved by main) is the FIRST act of the next session.
- wake.md REWRITTEN from scratch; owner.md current; P-29 (pausing) posted; main told. Nothing in flight; no cron.

## 2026-11-25 — ninth session: wake; r90 launched

- Registered (session_role pred). Main merged into `lane/pred-rev28` (clean; tip 07a46f018); lint 8,811 / 0;
  plan-lint green. M-3 read ([PRED-MUT-CHECK]: the 282 hand-copied mutants of scripts/tests/pred_doc/mut.py; the
  class fix is mine, nothing asked now).
- LAUNCHED coordinator `crit-predfold1124` (opus, background): review r90, design mode, subject the branch frozen at
  its tip, scope `git diff 0dda97065..tip -- docs/design/predicates/`, record range from after "review r88
  (predfold1123b): the dispositions" to the end; lenses asked: ruling (which case each sentence was asked on),
  examples / mode closure + expansion drill, fix-induced + general form, name grid over the path rules, check
  adequacy; denylist given; no known result told. Main told (no reply needed).
- Read whole: core.md, library.md, parked.md; the record's eighth-session entries.
- NEXT: re-ask not-test; on r90's hand-back: rule, one opus fix lane (files the review), merge, lints, P-30.

## 2026-11-25 — drop-not in discussion; the all-DFA goal; r90 ruled; fix lane predfix90 launched

- Owner (8 record entries, all classed; none a ruling): not-test re-asked -> "is not ... a logical statement?" ->
  "Couldn't ! Handle it?" (record check: NOT on a condition was MY proposal, spelled `!` then) -> drop-not ASKED
  (NOT leaves; `!` on a pattern, set or condition; the negative peek a body over `(?!...)`) -> the peek family ->
  his spelling lean `peeknot` -> "a complement on a lookahead is not meaningful" (yes; run) -> his IDEA `peek(!A)`
  (the peek detects a complement, as a hole's position decides) -> my general form: `!B` is "no path of B in the
  place's text and mode" (place table), so `peek(!A)` is `(?!A)` by definition; the wider in-place rule would make
  `when(!x, z)` work and reverse lone-complement-match: put to him, NOT answered.
- GOAL he stated, amended: "goal is all dfa unless specified by user. I don't want "when" to force vm". Recorded;
  P-30 notice to main (lookaround over a regular body in the automaton, product, complement: M-2's layer).
- r90 hand-back (coordinator stopped): 12 A items, 9 B, 9 C, 1 rejected; no ruled answer changes. RULED (record
  entry "review r90 (predfold1124): the dispositions"): all FIX-NOW but A12's unified statement and A11's group
  node (PLAN) and the full mutant gate (PLAN); four owner questions queued: sent-label-wall, skip-past-wall,
  equivalence-inside, shorthand-outside; open line alone-as-middle.
- LAUNCHED lane predfix90 (opus; worktree `worktrees/predfix90`, cut at 33abd6926; deliver + empty rulings first;
  lanewatch armed): applies r90, adds the path GRID against a separate rule evaluator, files the review.
- NEXT: his answer on drop-not; at predfix90's delivery: merge, lints, P-31 `done:`, tell main.

## 2026-11-25 — drop-not RULED; array-argument asked; predfix90 merged; P-31 done:

- RULED by the owner: drop-not ("I agree with our conclusions: peek(!A)"): `NOT` leaves; `!` on a pattern, set or
  condition; the negative peek is `peek(!A)`; `!peek(A)` and the bare `when(!x, z)` stay errors; not-test closed.
  NOT folded (its own lane, after the budget question).
- His standing request: each feature discussed carries its DFA category (yes / never / maybe + weight); memory
  `pcrec-pred-dfa-category`; the peek and `when` forms classed for him.
- /q: group-truth asked -> his idea: the group questions take the ARRAY form (`@d`) -> array-argument ASKED (four
  lines; group-truth closes inside it) -> he asked to discuss the "against" (a condition as a ready-made argument):
  census of printed calls told (every running call is one entry in place). NOT answered.
- Lane predfix90 DELIVERED (lanecheck DONE), MERGED; lint 9,106 / 0; plan-lint green; the model re-run at the merged
  tip 26 / 0. C3 ruled on the lane's flag (a crash is its own declared class). Lane and coordinator stopped.
- P-31 `done:` posted; main told. SLOW-BURN WEEK (memory, seen late): no other lane or round this week unless the
  owner says so; the drop-not (+ array-argument, if ruled) fold waits.
- NEXT: his answer on array-argument; then the r90 questions one at a time (sent-label-wall, skip-past-wall,
  equivalence-inside, shorthand-outside, alone-as-middle); the fold lane when he says go or the week resets.

## 2026-11-25 — array-argument and brace-counts RULED; main merged P-31; maps: lane predmap launched

- Main: `lane/pred-rev28` 16625c1f7 MERGED into main (r90's fold); P-30 journaled for [COND-FAMILY]; P-31's skill
  edits join main's owed doc lane; predfold1124 and predfix90 to be pruned by main.
- RULED by the owner: array-argument "yes including every" (the group questions take `@d` and a set; `every`
  back, over the array; group-truth and every-pass-spelling closed; record-in-some dissolved, my reading);
  brace-counts "I rule we should do this" (`x{a,b}` postfix, lazy and possessive forms; `rx.repeat` stays).
  With drop-not: THREE rulings in the record, not in the documents; one fold lane owed (waits for his go or the
  weekly reset).
- His ideas parked (pieces owed at the fold): one name for two of a library's labels by the export list; a
  selection of an array's settings by position.
- MAPS (his order: maps, then strings): his proposal of a map creator recorded; map-creator ASKED (five lines);
  he LEANS yes and asked for a lane on the accessor's uses: lane predmap LAUNCHED (sonnet, a study; worktree
  `worktrees/predmap`, cut at 956869507; deliver + empty rulings first; lanewatch armed; no subagents). My own
  thought on his "sequence map" told to him: one map, the joining chosen by the name applied (`join`, `any_order`).
- NEXT: predmap's report -> put map-creator back to him with its findings; then strings; then the r90 questions.

## 2026-11-25 — close: map-creator and string-literals RULED; predmap merged; nothing folded

- Lane predmap DELIVERED (lanecheck DONE; `predmap_runs: 54 cases, 0 failed`), MERGED; stopped. A study, no
  document change.
- RULED by the owner: map-creator "Yes to all seven" (after: no deduplication, "a search which might be empty",
  "F.z must exist or error", the key's order, his `.index` example); string-literals "Yes all five" (the triple
  quote reserved, parked).
- MY ERROR, recorded: I withdrew the key's-order answer on meaning-not-spelling without running it; he asked
  "why otherwise"; the two spellings enumerate alike; withdrawal withdrawn.
- FIVE rulings and his all-DFA goal are in the record, NOT in the documents. The fold lane (predfold1125) waits
  for his go or the weekly reset (slow-burn week).
- wake.md REWRITTEN from scratch; owner.md current; P-32 (pausing) posted; main told. Nothing in flight; no cron.

## 2026-11-27 — tenth session: the owner reopens `!`; bang-split asked, not answered; review r109 launched

- Wake: session registered; main merged into the branch (history index conflict, both sides kept); lints green;
  main told. The whole-file read of core.md was NOT done (the owner opened with `!` at once; pieces read by tag).
- The owner's discussion of `!` (twelve record entries, each with runs): his idea (no `!B` object; `!` on
  conditions; an `&!` operator; something for `when`); entry operators for "outside" (`:!`, `?:!` after his `!`,
  `?!`); `when` over conditions only (his `(0: A)` form validates only if the test means "A matches from here";
  `0` is the match so far); `C &! A` as the guard REFUTED by run; his peek operators `^A`, `^!A`, then `~A`, `~!A`
  and "keep ! out of the language"; his question whether prefix `!A` as `(?!A)` is a mistake.
- bang-split ASKED (six lines). NOT answered: he dislikes `^!(cond)` ("looks like abuse"), leans to `!(cond)` as
  the one bare form, and asked for a critic round with a suggestion on `!`.
- My corrections, recorded: "same characters, same meaning" for `(h: !<5)` / `:!` holds for single atoms only
  (99 of 1000 differ on a compound set); "drop the prefix `!`" withdrawn, then re-derived when the premise
  changed; "`!` is never an operator by itself" withdrawn and restored with its ground.
- Review r109 (predbang, design, sized small; number from main): coordinator crit-predbang launched (opus);
  subject `docs/dev/pred/bang_candidate.md`, evidence `docs/dev/lanes/predbang_evidence/`. Round dir
  `$PCREC_TMPDIR/scratch/crit-predbang/`.
- Still owed: the fold of the five rulings of 2026-11-25 (waits; it will fold with whatever he rules on `!`).
- NEXT: the round's draft -> rule dispositions -> put its answers and suggestion to him -> bang-split re-asked.

### 2026-11-27 — tenth session: r109 handed back and ruled; bang-split RULED
- Review r109 (predbang) handed back, dispositions ruled by the manager, filed
  (`docs/dev/reviews/2026-11-27-r109-predbang.md`); coordinator stopped. Reported to the owner with a re-asked
  bang-split (the round's V-C).
- The owner replaced it with his own form: `!` the logical not of a test, `~` the complement (today's ruled
  complement respelled), no `:!`/`?:!`/`&!`. Validated by run (`predbang_evidence/tilde.py`), re-asked, and RULED:
  "bang-split: yes". His question on binding a complement is answered by complement-place (2026-11-18).
- r109's F1, F4, F6 (`&!`, `:!` in a record) have no subject under the ruling; F5, F7, F13 go to the fold brief.
- Waiting: his go for the fold lane (six rulings now). Nothing running.
- and-not RULED ("agree drop &!"); his "Budget is fine" read as the fold's go. Review number r111 from main.
  LAUNCHED lane predfold1125 (opus; worktree worktrees/predfold1125 cut at 212e234e6; deliver + empty rulings
  written first; lanewatch --follow armed). Seven rulings in its brief. Waiting on the lane's delivery.
- Asked and RULED while the lane ran (each sent to it as R-1..R-6): sent-label-wall (error), label-needs-mark
  (yes), skip-past-wall (legal paths only), equivalence-inside (no label `t`), alone-as-middle ("yes to the
  gate": a part used alone may be named as a step, never skipped; the manager's first lean withdrawn on his
  point), shorthand-outside (error). group-node framed and ASKED (runs: predbang_evidence/groupnode.py).
- Lane predfold1125 DELIVERED (lanewatch DONE; lint 9770/0; model 15/0; 15 plants caught), merged at ddad6c680
  (lint 9795/0, plan-lint green), stopped. Owed by me at the fix: a rulings item per R-1..R-6 citing the record.
- LAUNCHED critic round r111 (crit-predfold1125, opus coordinator, three critics, design mode, freeze ddad6c680).
  Waiting on its draft and on the owner's group-node answer.
- group-node RULED (a group is a step; an underscore group walls), his backreference recollection checked;
  peek-name RULED keep (reviewable). Review r111 handed back (26 findings), dispositions ruled, coordinator
  stopped. LAUNCHED fix lane predfix111 (opus; worktree cut at cec257072; applies r111, folds group-node and
  peek-name, files the review; lanewatch armed). Owner questions from the round: gate-beside-label,
  gate-twice-scope (answers go to the lane's rulings file as R-n).
- Lane predfix111 DELIVERED (lanewatch DONE; lint 9998/0; model 14/0; 14 plants caught; 67 successor reds
  declared), merged at aa3f2c296, stopped. Review r111 filed by it. P-34 done line written; main told. Open with the
  owner: gate-beside-label (asked; the lane printed (ii) as a marked reading; `g.h` over `/(?<g>${A})x/` is the
  same cell), gate-twice-scope (next). Marked readings told to him at the r111 report.
- Main merged lane/pred-rev28 at dd873d4b4 into main and pushed (17468e317); it prunes predfold1125 and
  predfix111. Waiting on the owner: gate-beside-label, then gate-twice-scope.
- gate-beside-label RULED (error). His proposal of a one-path rule for skipping, a census run (onepath.py), then
  one-path RULED ("yes all five"; it answers gate-twice-scope; the array form exempt). Merged main back (637a5e79c).
  LAUNCHED fold lane predfold1127 (opus; the two rulings; lanewatch armed). Review number r112 from main for its
  small critic round. One question the lane will bring back: the array form over a part used alone.
- Lane predfold1127 DELIVERED (lanewatch DONE; lint 10099/0; model 13/0; 15 plants caught), merged at 860331f12,
  stopped. Eight printed reads moved to compile errors (three more than the census four). LAUNCHED critic round
  r112 (crit-predfold1127, opus coordinator, two critics). Owner questions from the lane: array-gate (asked),
  body-own-name (next). A stray predfold1125.out my census driver left in the worktree root was moved to scratch.
- array-gate RULED (error). Review r112 handed back (F1 to F8, COORD-1), dispositions ruled, coordinator stopped;
  it corrected my telling of one-path's cost (seven reads move, not four; five have no full path): told to the
  owner, who did not reopen one-path. body-own-name RULED ("agree": a path that skips nothing is always legal).
  LAUNCHED fix lane predfix112 (opus; worktree cut at 2d7718d4e; applies r112, folds array-gate and
  body-own-name, files the review; lanewatch armed). Waiting on its delivery.
- His lean: a path never goes through an argument's place, with the manager's carve-out for labels a body passes
  on by an export list ("a strong lean yes"; not ruled); and a lean that `[(=foo) = rx]` with an argument lacking
  `foo` is an error at the use. He asked for other unanticipated problems: LAUNCHED study lane predarg (opus,
  read-only on the documents, worktree cut at 88cda0d38; lanewatch armed) beside the running fix lane predfix112.
- Lane predfix112 DELIVERED (lanewatch DONE; lint 10121/0; model 11/0; 12 plants caught), merged at af340ff45, stopped.
  Review r112 filed by it. P-35 done line; main told. One cell for the owner: gate-beside-direct. Study lane
  predarg still running.
- Main merged P-35 (b35175102). Study lane predarg DELIVERED (lanewatch DONE), merged (the routine history-index
  conflict, both sides kept), stopped: 111 reads classed, 9 printed lines move, 11 problems, 7 questions. My
  carve-out wording was ambiguous (door vs own labels). Open with the owner: gate-beside-direct; then the seven,
  carve-out-reading first.
