# process log: crit-archlook (2026-11-18), ARCHITECTURE mode, coordinator opus

Freeze 17:19: S (note commit) 0abc1e961 on lane/archlook (branch head e7c814fcf adds only the denied lane report);
T 57fcb5737 (note header); main HEAD b22285a36. diff T..main over src memfn lib cli sabotages spec guide
decisions plan span_arms: EMPTY (no moved sites; no ruling drift at freeze). decisions.md last changed d648a285f
(2026-11-17), plan.md last changed at T itself.
Round dir created fresh (absent before). R/subject: note, span_arms@T, architecture.md@T, ARCH-STEP.md, decisions,
plan, plan row text, POSTFACT, cover_cap, architect SKILL copy.

Blinding: while checking the sibling round's review number I listed the file NAMES in scratch/crit-archdense (its lens
names: AGGREGATION, FIRSTUNIT, REGISTER, RULING, SITEMAP) and grepped it for a review-number string; no content read.
Note for the skill: there is no rule for how two same-day rounds reserve their rN numbers.

Lenses (5): AGGREGATION opus (+ sibling-of-family, general form + unlocks), SITEMAP sonnet, REGISTER sonnet,
FIRSTUNIT opus, RULING opus (record claims + goals CHECK lines; sole owner-quote verifier).
Seam round trip: NOT staffed separately (the note adds no kit field; the kit-contract claim sits in RULING).
Probe claims of D-15 (span_arms "today" columns re-measured): coordinator verifies inline.

17:21 launched 5 critics (one message, background, unnamed). All returned IN the launch turn (final replies undelivered,
as expected); files complete with CRITIC COMPLETE and lanecheck .done for all five by 17:31. Durations: sitemap 5.9 min,
register 5.1 min, firstunit 7.1 min, aggregation 7.3 min, ruling 9.6 min. No resends, no nudges.
Raised: AGGREGATION 7, SITEMAP 6 (1 suspected), REGISTER 5 (+F-4..F-6 checks), FIRSTUNIT 9 (1 suspected), RULING 9.
FREEZE DRIFT found at 17:32: main moved b22285a36 -> 2843924a1 (17:18:59, "plan: REQ-LOOKAROUND brought current and
moved to Active"), a plan.md-only change, landed seconds before/while I froze. My `git log -1 main -- plan.md` ran before
it; my R/subject/plan_row_REQ-LOOKAROUND.txt came from the LIVE tree (scripts/entry reads the working tree), so it is the
POST-freeze row while COMMON called it "at T". RULING noticed the mismatch itself and reported it. Process lesson:
copy plan rows with `git show <freeze>:docs/dev/plan.md | grep -A`, never `scripts/entry` (it reads the live tree).

17:34 verifier (opus) launched; returned in its launch turn, verify.md complete (VERIFY COMPLETE, lanecheck DONE) in
6.0 min; 14 items, all HOLD except: RULING-3 / REGISTER-2 PARTLY (decided between them), FIRSTUNIT-2 PARTLY (:9085 is the
whole-run K), RULING-8(f) PARTLY (D70 names D62's discipline), SITEMAP-2 PARTLY (S1925's reach REFUTED: SAB_REACH runs on
the clean tree). No REFUTED rests on a crafted input except SITEMAP-2's, which quotes the matrix header and a probe:
coordinator accepts it (re-read: tests/mech/run_sabotage_matrix.sh:44 cited verbatim).
17:35 coordinator inline: the 4 D-15 probes (all HOLD).
17:36 review-number coordination: told crit-archdense and crit-predspec27 "archlook takes r50". MISTAKE: crit-archdense
had already ENDED; SendMessage RESUMED it as an in-process teammate (107 prior messages) just to read a number question.
Cost: one wasted turn of a large context. Lesson below.
17:40 draft review.md written; critic texts, verify.md, COMMON and FIRSTUNIT's anchors.py copied to review/.
Per lens: AGGREGATION 7 raised / 7 verified (2 with remedy suspected); SITEMAP 6 / 4 hold, 1 partly, 1 unverified;
REGISTER 5 / 4 hold, 1 partly; FIRSTUNIT 9 / 7 hold, 1 partly, 1 suspected; RULING 9 / 7 hold, 2 partly. Overlaps: the
K-state undercount found by 4 lenses (AGG-2/7, FU-2, SM-5; plus RULING and REGISTER out-of-lens notes); the ReqRun
generic writer by 2 (FU-9, REG-3); the RM-3 copy differences by 2 (FU-7 + REGISTER out-of-lens); the context-producer
question by 3 (RUL-4, AGG-4, REG-1). Answer- and speed-level findings: 0. Time to draft: 21 min from launch.
Review files: review.md is free of `plan.md:NNN` cites; the copied critic texts in review/ hold 16 such cites and one
spec-by-line cite (SITEMAP S25): scrub before filing (skill §9.1).

## Process observations

- The arch-mode staffing (aggregation, site map, register, first unit) plus a RULING lens worked; RULING was the most
  productive lens (9 findings, 7 design-relevant) and is NOT in §4's "usual staffing" for A. Here it was there only
  because the launcher named the record claims.
- FIRSTUNIT's own tool (anchors.py: every sabotage's SAB_BEFORE located in the moved line ranges) beat the note's
  identifier greps C31/C32 on every unit. The architect skill tells the architect to find binding checks by grep of
  identifiers; that is the floor coding.md §3.5 warns about.
- AGGREGATION found three families (never, offset bound, per-offset head) by reading the code for the QUESTION, not the
  requirement's vocabulary; the site-map lens, briefed from the requirements' vocabulary, could not have found them.
  The two lenses are complementary as designed.
- All critics finished in 5-10 min with one question each and read-only copies; no resends, no nudges; all six final
  replies undelivered (expected; files were the delivery).
- Freeze: I froze plan.md by `git log -1 main -- plan.md` a minute before the manager's plan commit landed, and copied
  the plan row with `scripts/entry`, which reads the LIVE working tree. COMMON then called it "at T". RULING caught the
  mismatch. §3 says freeze rulings by commit; it does not say scripts/entry reads the live tree.
- Unclear in the skill (arch mode): §3 arch says no review tree and "diff the note's cited sites between T and main
  HEAD" (clear); §5 "In design mode, copy the frozen subject ... R/subject/" applies to A only by §4's "In design-mode
  setup terms" sentence; a coordinator reading §5 alone would miss it. §5's pre-create rule names design mode only.
- Unclear in the guide/architect skill: the class AS-IS for a site whose line the feature deletes (SITEMAP-3); whether a
  "TRADED AGAINST" line in Goals served needs a noted-deviation row or a declaration cite (A3); the architect template
  has no slot for "rulings the note crosses" (A6, A8: two ruled shapes crossed without citation).
- Review numbering: no rule for same-day rounds reserving rN; and SendMessage to an ENDED coordinator resumes it.

## Proposed changes

1. pcrec-critic §4, ARCHITECTURE MODE "Usual staffing": add "ruling check (opus; goals folded into it) whenever the
   note cites rulings, revisions or deliveries" — observation: RULING found A1, A5, A6, A8 (stale kit ABI, a go'd unit's
   text, two ruled shapes crossed), none reachable by the four standing A lenses.
2. pcrec-critic §4, first-unit identity row, append: "find each unit's binding checks by anchor LOCATION: map every
   sabotage's SAB_BEFORE into the moved line ranges at T (r50 archlook's anchors.py); an identifier grep is a floor"
   — observation: every unit's list missed anchors (S453, S467, S813, S814, S901, S1701, S1711, S1957).
   Same sentence for pcrec-architect §4 (the architect's own binding-check step).
3. pcrec-critic §3.1 freeze, append: "Copy plan rows and ruling text with `git show <freeze>:path`, never
   `scripts/entry` (it reads the live working tree); re-check main HEAD once more at the end of setup and record any
   commit that landed during it" — observation: the manager's plan commit landed at 17:18:59, during my freeze.
4. pcrec-critic §2 (launch): "the launcher assigns the review number N in the launch prompt when another round runs the
   same day" — observation: no rule; I reserved by messaging two coordinators, one of which had ended and was RESUMED
   by the message. Add to §8 or COMMON: "never SendMessage an ended agent for a non-essential question: it resumes it".
5. pcrec-architect template: (a) a "Rulings this note crosses" line in "Requirements read" (each ruled form the note
   changes, cited and argued, or handed to the manager); (b) for each new mechanism, "family grep by the question's
   synonyms" in "The general form and its siblings"; (c) every population sentence ("three readers") carries its C-n;
   (d) a site whose line the feature deletes or rewrites is never AS-IS; (e) a goal TRADED in "Goals served" has a
   noted-deviation row or the cite of the declaration that makes it none.
6. pcrec-critic §5: make the R/subject copy and the findings-file pre-create explicit for A mode ("design or arch").

## Framework notes

- The coordinator pattern ran an arch round end to end in 21 min to draft (5 critics 5-10 min each, one opus verifier 6
  min), the coordinator's context staying small (critic files read once, no code dumps). The manager was not woken.
- Arch mode is a good fit for the pattern because every claim is a grep or a quote: the verifier could re-run all 36
  findings by command; inline verification would have cost the coordinator more context than the verifier did.
- A same-day multi-round situation (three coordinators) needs a shared allocation (review numbers) owned by the launcher,
  not negotiated between coordinators.
17:45 numbers confirmed: r48 predspec27 (prov.), r49 archdense, r50 archlook; REGISTER's relayed summary matched its file.
