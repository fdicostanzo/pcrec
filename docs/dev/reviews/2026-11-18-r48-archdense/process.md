# process log: critic round archdense (ARCHITECTURE mode, first real use), coordinator

## Freeze (17:15)
- SUBJECT: docs/design/dense_hit_arch.md @ 5dcc98dfc (lane/archdense tip, rev-parsed 5dcc98dfcae2).
- TREE T (note header): 57fcb5737dff (= main~1; main HEAD eb92cd5b5 = T + one journal commit).
- Site drift T..main over src cli lib memfn tests scripts docs/spec docs/dev/guide docs/design/stream: EMPTY (git diff --stat). No moved site.
- Rulings at freeze: decisions.md last touched d648a285f (ancestor of T), plan.md last touched at T. Re-diff at each critic return and at hand-back.
- Denylist: docs/dev/lanes/archdense* (report exists only on the lane commit, not at T), journal/wake/owner, worktrees/, .coord/.
- Round dir was absent; created. R/subject/: the note, the plan row (plan.md@T lines 285-295), architecture.md@T, pcrec-architect SKILL.md@T, all chmod a-w.

## Lenses (5)
- AGGREGATION opus: table row + standing questions (sibling, general form + unlocks) vs the note's section.
- SITEMAP sonnet: re-derive first from requirements, then diff.
- REGISTER sonnet: table row.
- FIRSTUNIT opus: U1 (one unit listed) + seam round trip on U1's seam (folded, sub-part b).
- RULING opus: ruling check (architect's reading of NOTES 1-3, D146/D157/D195, ¶7a; owner quotes verbatim: ONLY this lens) + goals lens folded (tier-1 CHECK lines; does the note decide design-owned things).
Rationale: profile = site map + register + one remodel unit (U1) + a kit seam + rulings relied on. Goals folded into RULING rather than AGGREGATION to keep aggregation's brief to one question + the standing pair.

## Agents
- 17:17 launched 5 critics in one message (background, unnamed). ALL FIVE returned in the launch turn (tool results came back synchronously, each "ended without delivering a report through SubagentHandback": expected; files are the delivery).
  - AGGREGATION opus: 4.9 min, 36 tool uses, 5 findings (all CONFIRMED; AGG-3 part SUSPECTED), lanecheck DONE.
  - SITEMAP sonnet: 3.2 min, 20 tools, 8 findings (7 CONFIRMED, 1 SUSPECTED), DONE. Did the derive-first step (my_sites.md) and found 13/13 note sites independently.
  - REGISTER sonnet: 4.0 min, 27 tools, 5 items (2 CONFIRMED, 2 SUSPECTED, 1 NOTED), DONE.
  - FIRSTUNIT opus: 5.7 min, 41 tools, 6 findings (all CONFIRMED), DONE.
  - RULING opus: 7.8 min, 52 tools, 10 findings (9 CONFIRMED, RULING-10 part SUSPECTED), 21 quotes verified, DONE.
- No resend, no nudge, no stall. Nothing to TaskStop (all ended).
- 17:26 rulings re-diff at first return: see below.
- FREEZE DRIFT at first return (17:26): main moved eb92cd5b5 -> 2843924a1 (predspec27 merge; plan.md [REQ-LOOKAROUND] row only). decisions.md, guide, src, memfn, docs/spec, roadmap: unchanged. No ruling this subject relies on moved. NOTE: crit-archlook is a parallel arch round today; review-number collision possible (r48).
- 17:28 launching ONE opus verifier over 10 grouped items (interlocking semantic claims: site classes, seam phases, rulings): skill §6.2 "opus verifier when CONFIRMED findings are interlocking".
- 17:28 verifier (opus) launched; returned in the launch turn, 6.7 min, 51 tools, V1-V10 all filled, VERIFY COMPLETE, lanecheck DONE. 0 full refutations; 2 sub-claims refuted/reversed; 1 count corrected (41 -> 42); 1 NEW adjacent site found (VM hybrid prefilter's landmark_position declaration, emit_dfa.c:14012).
- No REFUTED verdict rests on a crafted input, so no coordinator re-run was needed (skill §6.2).
- 17:33 rulings re-diff at hand-back: main still 2843924a1; no change to decisions/plan/guide/src/memfn since the first return.
- 17:40 draft review.md + review/ (5 critic files, verify.md, COMMON, SITEMAP step-1 list). No review worktree to remove (arch mode builds none).

## Per lens: raised / verified / severity / overlaps
| lens | raised | verified HOLDS / PARTLY / sub-refuted | severities | overlaps |
|---|---|---|---|---|
| AGGREGATION | 5 | 3 / 2 / 0 | design 4, maintenance 1 | A (SITEMAP-7), B (SITEMAP-6, RULING-6), C (FIRSTUNIT-1/2) |
| SITEMAP | 8 | 6 / 2 / 1 reversed (SITEMAP-3 hazard) | design 5, maintenance 1, doc 2 | A, B, D (FIRSTUNIT-3/4) |
| REGISTER | 4 + 1 NOTED | 2 / 2 / 1 sub-claim | doc 1, design 3 | I with RULING-3 |
| FIRSTUNIT | 6 | 4 / 2 / 0 | design 4, maintenance 1, doc 1 | C, D, E (RULING-1/4/7/8) |
| RULING | 10 | 10 / 0 / 0 (RULING-10 part SUSPECTED) | design 5, doc 5 | E, I, J (unique), K (unique) |
Time from launch to draft: ~23 min (17:17 launch -> 17:40 draft).

## Process observations
1. Fast and clean: all five critics and the verifier finished in 3-8 min each, returned IN the launch turn (synchronous tool results despite run_in_background), wrote incrementally into pre-created files, and passed lanecheck. No resend, nudge, stall, leak or delivery failure. The pre-created-file rule (design mode) transferred to arch mode unchanged.
2. The derive-first site-map brief worked as designed: the sonnet critic found 13/13 note sites before opening the map, then 5 the note lacks. Cheapest lens per finding (3.2 min, 8 findings).
3. The ruling lens was the most productive (10 findings; groups J and K unique to it) although the skill's arch-mode "usual staffing" does not list it. The note carried five owner questions, a proposed kit request and an "architect's reading" of three owner NOTES: that is a rulings-heavy profile. Four of five owner questions turned out to be settled by the record.
4. Overlap was high and useful (groups A-E each reached by 2-3 lenses from different sides: code, class, record); the verifier merged them without contradiction. The skill's "assign each named drill topic to ONE lens" was not at risk here because no drill topics were named.
5. The verifier earned its opus: it reconciled four candidate U1 homes into one constraint, corrected a count, reversed a hazard direction, and found an adjacent site no critic had.
6. The arch-mode skill text has no step for the request text a note proposes (U1's R-n draft). It was reviewed only because first-unit's brief added "is the request facts-only?". It produced the most consequential design finding (E).

## Where the skill's arch-mode procedure or docs/dev/guide/ was unclear, wrong or missing (pilot record)
P-1. Review NUMBERING: the launcher said "N by the skill's numbering rule"; the skill has none (sections 1-9), and docs/dev/reviews/CLAUDE.md states only the file pattern. Today two rounds (archdense, archlook) run in parallel; N collides unless one rule assigns it. MISSING.
P-2. §3.1 arch: "critics read code with git grep <T> ... no review tree is built" but §6.4 always says "Remove the review worktree"; arch mode has none. UNCLEAR (harmless).
P-3. §4 arch-mode usual staffing omits the ruling lens and the seam lens, although the profile line (§3.4) lists "a planner / kit / back-end seam; rulings relied on" for arch. Both were needed. WRONG for a note with owner questions or a kit request.
P-4. The "goals" lens row (A part) is "fold into another lens if needed" but names no default host in arch mode; I folded it into ruling. UNCLEAR.
P-5. No lens owns the note's PROPOSED KIT REQUEST TEXT or its OWNER QUESTIONS list. MISSING (see proposed change C-2).
P-6. first-unit identity lists gates as "byte-identity sweep, abi or kit event"; the architect skill's unit GATE vocabulary (SKILL @T line ~92) is "no-mover with byte identity / abi event / kit seam event, D146": no "kit ROW event", which is what U1's pcrec-owns branch is (FIRSTUNIT-2). MISSING in the architect skill (and so in the lens).
P-7. The architect skill's WIDEN rule ("every GENERIC writer or copier of the shape ... each is a hazard when the shape changes") assumes a strengthening. For a WEAKENED contract the hazards are the checks asserting the stronger contract and the serves declarations (V4). WRONG direction for weakenings.
P-8. architecture.md register "HOW TO USE IT" step (1) says grep for files, functions and the plan tag, but the roadmap areas are "rows by reference" (row 12) and their "Ride-along triggers" vs "Prerequisites" lines are easy to confuse (the note answered A-PLAN's prerequisite, not its trigger) and easy to skip (5 areas missed). UNCLEAR.
P-9. architecture.md "Notice siblings" says "count the CALL SITES that ask the same question"; the note counted SLOTS (tables) and treated a built site as planned on the plan tag's word. The guide does not say "built" is read from code at T. MISSING.
P-10. The architect skill has no "stop rule" by that name, yet the note invokes one (RULING-2): either the skill's §3.2 wording or the architect's habit drifted. UNCLEAR naming.

## Proposed changes (concrete text; manager accepts or declines; I edited nothing)
C-1 (skill §2, numbering; P-1): add after "Topic names are unique per DAY": "The review number N is the next integer after the highest rN already used on that date in docs/dev/reviews/ OR claimed by a running round's coordinator (the launcher assigns N in the launch prompt when two rounds run the same day)."
C-2 (skill §4 arch-mode staffing; P-3, P-5): replace "Usual staffing: aggregation, site-map completeness, register (always), plus first-unit identity when the note lists remodels; 3-5 critics." with "Usual staffing: aggregation, site-map completeness, register (always); first-unit identity when the note lists remodels (it also reads any kit REQUEST TEXT the note proposes, for facts-only and pre-answered questions); the ruling lens when the note carries owner questions, a reading of owner NOTES, or a proposed request (it checks every owner question against the record: a question the record answers is a finding; the goals lens folds here); 3-5 critics. (2026-11-18 archdense: the ruling lens gave 10 findings, 4 of 5 owner questions were settled by the record.)"
C-3 (lens table, site-map completeness row; P-9): append "For every plan row the note calls PLANNED or not built, grep its row names, emitters and site ids in code at T: a STATE tag is not evidence (2026-11-18 archdense: [LANDWALK] built at T, tagged not-started); and for every emitted local the feature changes, grep EVERY declaration (archdense: three declarations of landmark_position, one found only by the verifier)."
C-4 (lens table, register row; P-8): append "For each roadmap area (row 12 by reference) quote the area's 'Ride-along triggers.' line and dispose against IT, not the Prerequisites line; a trigger that names the plan tag is a match, declined only with a reason that addresses the tag (archdense: A-PLAN, A-SEAM; 5 areas undisposed)." Also: "check each PROPOSED row's event can fire for the shapes the note itself foresees (archdense P1)."
C-5 (pcrec-architect skill, unit GATE vocabulary; P-6): "its GATE (no-mover with byte identity / abi event / kit seam event (a contract or vocabulary meaning moves) / kit ROW event (rows newly serve a class the contract already admits), D146)"; and WIDEN: "when the widening WEAKENS a reply contract, the hazards are the checks asserting the stronger contract and the per-row serves declarations, not the renderers (archdense V4)."
C-6 (pcrec-architect skill, owner questions; P-5): "Each owner question cites every record that bears on it (the plan row's NOTES, D-rows, spec). Where the record already answers it, state the record's reading as a confirm, not a question. Quote owner words only as the record quotes them; text a record attributes to the manager is the manager's."
C-7 (skill §6.4; P-2): "Remove the review worktree (code and design modes; arch mode builds none)".
Guide lessons (critics.md "Lessons from review rounds"): the five in review.md's last section.

## Framework notes
- The coordinator pattern fit arch mode with no adaptation beyond copying the subject and its requirements into R/subject: 6 agents, ~23 min, zero manager turns between launch and hand-back. A rulings-heavy note made the ruling lens the decisive one, which the arch staffing line did not predict: the profile step (§3.4) is the right place to catch that, so the coordinator should staff from the profile, not from "usual staffing".
- Synchronous returns: every nested agent returned in the launch turn even though backgrounded, so lanewatch was unnecessary; the files plus lanecheck were sufficient as the delivery channel.
- Where else it might fit: a pre-briefing triage of owner-question lists (one ruling-lens agent over owner.md's questions against the record) would have the same blind-by-construction value; evidence: J here.
