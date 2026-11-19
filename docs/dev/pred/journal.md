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
