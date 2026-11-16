---
name: pcrec-critic
description: Run an adversarial critic round on a pcrec (or memfn kit) DESIGN document, CODE change, or both. The manager launches one opus COORDINATOR agent that freezes the subject, picks lenses from the declared lens table, briefs and launches blinded read-only critics, verifies their findings, drafts docs/dev/reviews/YYYY-MM-DD-rN-<topic>.md with PROPOSED dispositions, and meta-monitors the round itself; the manager then rules the dispositions and launches the fixes. Use before a build go (design) or before landing (code). Args: design|code|both, the subject (doc path, branch or commit), a topic name.
---

# pcrec critic round

A critic round reviews a DESIGN document, a CODE change, or both, against the
living guide `docs/dev/guide/` (coding, architecture, style, critics, addenda).
The guide holds the rules critics review against; this skill holds the
procedure. When the two disagree, the guide wins and you fix the skill.

Lenses are chosen per subject from the table in section 4. No lens set is
standard because an earlier round used it (Frank, 2026-10-23).

## 1. Roles

| role | who | does | never |
|---|---|---|---|
| **launcher** | the manager | names subject, mode and topic; launches the coordinator; rules every disposition; launches fix lanes; accepts or declines proposed skill/guide changes | tells the coordinator any known finding (it must stay blind) |
| **coordinator** | ONE opus agent, background | sections 2-7: freeze, profile, lenses, briefs, launch, monitor, verify, draft, meta-monitor | rules dispositions; edits code; commits; merges |
| **critics** | 2-5 agents launched BY the coordinator | one narrow question each, read-only, findings to a file | run `make` or suites; edit either repo |
| **verifier** | one agent launched by the coordinator | re-runs every CONFIRMED finding that would change code or a design | trusts a critic's consequence claim |

Why a coordinator (Frank, 2026-10-23): every critic report woke the manager's
large context (about a dozen turns per round), and the manager knew results it
had to keep out of the briefs. A fresh coordinator is cheaper per turn and is
blind by construction. Subagents can launch subagents (tested 2026-10-23), but
a nested agent's final reply may NOT reach its parent: everything that matters
travels as FILES, and a missing file gets one SendMessage asking for it.

## 2. Launch (manager)

Topic names are unique per DAY across main and the kit (prefix the kit's with `memfn-`; 2026-11-12 the kit's crit-s1 collided with main's). Launch one agent: `model: opus`, background, name `crit-<topic>`, prompt =
"COORDINATOR critic round <topic> (<mode>). Read
/home/pcrec/projects/pcrec/.claude/skills/pcrec-critic/SKILL.md sections 3-8
and follow them as the coordinator." plus: mode, subject, topic, the scope
mandate (only the pcrec and pcrec-bench repos; scratch only under
`$PCREC_TMPDIR/scratch/crit-<topic>/`; no edits to either repo except creating and
removing the review worktree), and the denylist paths the coordinator cannot
know (lane report names, earlier reviews of this subject). Say NOTHING about
known results. Then go about other work; the coordinator hands back one
message when the draft is ready.

## 3. Freeze and profile (coordinator)

1. Subject:
   - code: `git rev-parse` the branch yourself (never a hash from prose); record
     `SUBJECT` and `BASE=$(git merge-base main SUBJECT)`.
   - design: the document path AND the commit that holds it (`git log -1
     --format=%H -- <doc>` on its branch); critics read that version. ALSO record the commit a
     BUILD would land on (normally main HEAD), build the review tree THERE and tell critics both;
     any cited code that moved between them is a finding (2026-10-29 r4 p48).
   The subject stays frozen until the round compiles (learnings §6, R30).
   When the subject has CLIENT design docs (designs it serves or is served by), check each client's ancestry
   against the subject commit and brief critics on the client version IN FORCE at the freeze (2026-11-05 r5 arev:
   the subject predated its client's rev 1).
   Freeze the RULINGS too: record main's decisions.md/plan.md commit at the freeze, diff them against main at
   hand-back, and report any change as FREEZE DRIFT in the draft (2026-11-02 r2 spanpick2: the owner amended
   D186 add. 1 mid-round; caught by chance).
   Locate each in-force ruling's RECORD (file:line at the freeze); a ruling relied on with no record is a FREEZE NOTE in the
   draft (2026-11-06 r5: DEFAULTS (B) was ruled by message only).
   RE-DIFF the rulings at EACH critic return, not only at hand-back; a ruling whose Home is the subject that lands
   mid-round gets a FRESH critic on its section (2026-11-06 r4 span-cards: D188, homed in rev 1, was seen only at hand-back).
   A mid-round ruling NOT yet homed in the subject gets a HAND MAPPING under FREEZE DRIFT (what it settles, what it reopens, per finding) instead of a fresh critic (2026-11-15 r10 predspec9: two owner entries settled half of CENSUS-2 and reopened the anchors).
2. Code mode: make a clean review tree, `git worktree add --detach
   worktrees/crit-<topic> SUBJECT`, and build it ONCE yourself, UNLOCKED:
   `nice make -j2` (critics run `build/pcrec` and `gcc -S` on single
   patterns, never `make`). NEVER under `scripts/boxlock`: a waiter yields to
   every ready queue job, often the subject's own validation, and a build of
   seconds waited 3h50m (round 2026-10-27 r1 ic2). Launch the probe lenses
   only once `build/pcrec` exists; a critic without a binary waits for it
   (poll every 10 min, up to 4 h) rather than ending source-only. When the promise includes trace records, build BASE and SUBJECT
   `-DPCREC_KS_TRACE` binaries ONCE into the round dir as part of the round's build
   (r5 sp1g: saved three per-critic builds). When a touched trace sits behind a guard (`PCREC_KS_TRACE`, `PCREC_CAND_TRACE`, whatever the `#if` names), grep the guard and build BASE and SUBJECT trace binaries for it before briefing (r11 covs1f: a COMMON named a trace switch that never printed). For MFTRACE REACH equality, build the BASE and SUBJECT MF_TRACE pairs via
   `tests/memfn/mk_mftrace_lib.sh` + one gcc link; a BASE tree may be a `git archive` export in the
   round dir (r1 sp1b). When the subject adds or moves sabotage rows, also prebuild ONE planted compiler per moved
   row into the round dir (`plants/<ID>/`, from the row's own BEFORE/AFTER), so critics test each row's witness
   without running make (r9 covs1: 9 plants took about 10 minutes). Build each plant with `build/pcrec build/pcrec-harness` (a REACH-using row needs the harness; r18 covs2a: REACH-FAILED on every plant built with the compiler alone).
3. Denylist (D27 applied to review): the lane's reports
   (`docs/dev/lanes/<lane>*`), review files on this subject, `git log` bodies
   beyond the subject lines, job logs, other worktrees, the box queue, plus the
   launcher's list. Put it in every brief. To deny a plan.md row, locate it by `grep -n '^- \[TAG\]'` only; never print its
   neighbours (a `sed -n` around the tag line leaked the denied rulings, 2026-10-26 inline-c). State denied files as PATHS EXCLUDED
   from EVERY git diff and grep in COMMON (for PLAIN grep, `--exclude=` per denied file: plain `grep -r` ignores git pathspecs; r2 sp1c) (`':!memfn/docs/journal.md'`), not only in one
   example command (r5 sp1g: a per-directory diff showed a denied journal hunk).
   When a ruling the critics need has its ONLY record in a denied ledger (a journal, a responses file), COMMON QUOTES it
   verbatim and gives a ready plain-grep exclude string for that file (2026-11-07 r12 planframe1: a plain grep leaked one
   denied journal line while a critic looked for the ruling).
4. Profile: what does the subject touch? Several can apply:
   - design: a new mechanism or table; a measured quantity, check or data file;
     a caller-facing contract; a build proposal (cost, scope); rulings it rests on
   - code: emitted C; a decision table/selector/row; a caller-facing contract;
     a performance claim, floor or re-pin; checks/pins/sabotage rows; plain C
     structure; rulings relied on

## 4. Pick lenses (coordinator)

First match per profile item, union the results; 2-5 critics; never a lens
with nothing in scope. Each lens is ONE question (narrow briefs beat wide ones,
measured twice). Subject column: D = design document, C = code diff.

| subject | profile item | lens | its one question | model |
|---|---|---|---|---|
| D C | always | **goals** (fold into another lens if needed) | Does the design state ranked, checkable goals (architecture.md)? Does the subject serve them in that order? No goals = a DOC finding; review against the goals the design implies, saying so. | strong |
| D | the owner has stated benefit criteria for this subject | **owner criteria** | Grade the subject on the owner's stated criteria in force at the FREEZE, in his order: does each claim serve them, or argue something he ranked as a constraint? | strong |
| D | a new mechanism or table | **premise** | Name every assumption the design rests on and test each (grep, measure, read the data): is it true? ("do we really need this?", "is this really constant?" are this lens; so is every sentence of the form "the existing X already does Y": find X by file:line.) A replay against a part map reads type/enum/table hunks in full, never classifying by hunk-header function names (2026-11-01 r3 stream3: a hand-schema change was filed under the planner because it sat beside a planner function). Every "today the tree does X" number re-runs from the command the design must cite beside it (a number with no command is a finding), and for each function the design KEEPS, ask whether the new text requires a property it lacks (2026-11-15 covcap-r2: a false "lists 24" and a kept helper missing cross-depth identity). For each new LIMIT, find the existing limits on the same object (grep `limits.def` for its producer: construction budget, state ceiling) and run the limit's witness through the build tree: does the object it limits exist at that size? (2026-11-15 covcap-r3: a new span limit sat behind the machine's own 4096-state ceiling and could never bind) | strong |
| D C | a trust boundary (opt-in, gate, untrusted input becomes code or a file read) | **adversary** | As the author of an untrusted input, find every path from your bytes to code, a file read or a terminal escape that bypasses the gate, including the test harness and tooling as entry points; and what an ADMITTED input can do to the rest of the output | strong |
| D | a table, rule or selection | **simulate** | Run the proposed rule over the real corpus or data: does it pick what the design claims, and where does it mispick? Where the output is a verdict table over measured outcomes, drill it first-match on CONSTRUCTED outcomes, the design's own predicted outcome first, then adversarial ones (2026-10-31 bakeoff: the predicted tie read INCONCLUSIVE). Where the design ships its own drill script, implement the rule from the design TEXT before reading the script, then diff the two (bakeoff2: nine text/script divergences); and recompute every outcome the design QUOTES from its OWN formula: a number borrowed from an evidence study's different arithmetic is a finding (2026-11-02 spanpick: smp20's 8.6 % was R-33's doubled hits); and run two standing drills: ADD A NEVER-PICKED CANDIDATE (a normaliser over the candidate set, such as a ratio-to-best, must not flip the pick) and RE-SWEEP every quoted region boundary finer than the study's grid (a boundary on a grid point is unproven) (2026-11-03 spanpick4); a rewrite run to a fixpoint and called a NORMAL FORM gets a confluence drill: every merge order over small exhaustive grids plus the real widest inputs (2026-11-05 alt-nf SIM-2: 23% of grids, \\p{Lu} 76 vs 66); apply each ACCEPTANCE CASE AND every worked table the revision adds in the program's REAL MODE, searched vs whole value, on every re-check (2026-11-15 r10 SIM-6: a searched case expected an anchored answer since rev 7; 2026-11-16 r29 SIMULATE-1/6: two new tables stated whole-value answers that move when searched); on a re-check that FOLDS a ruling, re-apply EVERY SAME look-alike row under each ruling folded in that revision, not only the rows the revision's own re-check question names (2026-11-15 r12 SIMULATE-1: four SAME rows contradicted the anchoring ruling folded in the same revision); on a ruling stated by POSITION ("the filter side of X"), test its trigger against the operator's symmetry and against nesting (the position inside a hole, inside another filter) (2026-11-15 r14 predspec12 F1/F2); for a diagnostic whose message makes a semantic claim ('adds nothing', 'never matches'), plant a counter-case for the CLAIM in each place it fires (a non-edge anchor), not only the evidence's own population (2026-11-15 r16 predspec14 SIMULATE-1); an evidence row that shows a refusal or an error names the MECHANISM that refuses; an emulator's own `raise` is not evidence (2026-11-15 r17 predspec17 F6); for a design whose values are SETS, two spellings of the same set (the empty set above all) must give the same answer in every mode (2026-11-16 r26 jointcond ZERO-EMPTY: found by three lenses); DOMAIN drill: for any existential "some value" reading, run it against a complement set, a dead branch, and a lookbehind-restricted group in two spellings of the same pattern (2026-11-16 r28 absfold MARK-DOMAIN: three lenses reached the domain from different sides, one drill reaches all), and an equal-behaviour pair built by a CONDITION (`rx & (cond)` vs the narrowed rx) or a second `&` operand (2026-11-16 r29 FIXIND-7, AND-DEAD) | sonnet+ |
| D | a grammar or notation | **census** | For each mark and key word, classify every occurrence's meaning over every code span; report any with two (2026-11-15 r8 predspec6: found the most items, quantified the comma claim 200/200) | opus |
| D | a claim of answer identity BY PROOF (a rewrite, an elision, a dropped record) | **soundness** | Build the base tree and APPLY the documented rule, as written, to the emitter's real output for crafted witnesses (and to every seam where two documents' rules compose): does any answer move? (2026-10-29 r3 vmtrail: produced every answer-level repro). When the design reads a RECORD of the program (an event stream, a listing), also enumerate every statement the emitter prints inside a matcher and check each is recorded or a declared no-effect form (r6 vmcons: 4 of 5 answer holes were unrecorded statements); and build one MIS-TYPED record per kind class (a conditional fail typed FAIL, a guarded write typed SET) and check the design's checks catch each (r8 vmcons2: a token-list signature passed a mis-typed fail); and list every post-render rewrite of the text and each check's domain, and ask whether each analysed operand prints (r9 vmcons3: a respell after rendering and non-printing operands broke rendered-from-the-record); and when a design REMOVES a frame push, list every path that frame's pop reaches (later branches, the next row), not only the removed piece's own retries (2026-11-06 r1 arev2: a dropped push lost every later branch on `(?<*`); and for each sabotage witness the design proposes, compute whether its fact clears every floor and domain test in BOTH the correct and the sabotaged build: a witness under the floor in both cannot fail (2026-11-05 alt-nf: S-c out of domain, S-f under the floor, S-d named none) ; and when the design ships PSEUDO-CODE over the machine's real primitives (frames, slots), hand-execute it LITERALLY over multi-branch witnesses: what does each saved frame restore? (2026-11-05 r3 vlookbehind: a 570M-case simulation of the rule's intent was 0-diff while the sketch's retry frame restarted the next branch from the wrong place); and compile every emitted-shape claim at default flags, at `-march=native` and under the second supported compiler (2026-11-07 r1 xarch: only non-default consumer flags exposed the build failures) | opus |
| D | a RE-CHECK of a revised design | **fix-induced** | For each claimed fix: does it add a read, a hand, a row or a check? Trace each addition in today's code (read cycles, new take cells, checks that now fire). (2026-10-29 r5 landwalk2: rev 1's D3 fix closed a LOCATE->NEXT read cycle) When a fix adds or changes a field, list the SIBLING fields it leaves unstated and trace every reader of them (r7 landwalk3: a new LOCATE row stated no RECOVER; its readers dereferenced NULL) For every PAIR of fixes touching one check or one directory, recompute that check's population at the build tree (2026-11-06 r5 CHECKC: two sound fixes left a check over zero keys). Trace every NEW slot write, trail entry and frame to the pass that SIZES its storage (`vm_cost_*`): a literal interpreter without capacity misses it (2026-11-05 r6 vlb2: `(?<=a{1,2})x` would return PCREC_ERR_FRAMES).. Quote the DEFINITION, and trace every reader, of any existing record a fix names as a fact's home (2026-11-01 r2 stream2: `Nfa.erased` gaining `\K`/`\G` flipped exact windows). When a revision RESTRUCTURES a walk into numbered per-depth rules, map every conjunct it absorbs to the depth range it reads today (0..k, k, 0) and check each at the boundary depth `k` (2026-11-15 covcap-r4: an inclusive `j <= k` loop became a rule run only below `k`, an answer move; a kept guard ahead of an existing conjunct also duplicated it: grep each guard's test against the conjunct table). A claim that witnesses 'move with X by construction' is drilled per row KIND (verdict, facts, answer, mech REACH) at X's extreme admissible values (2026-11-15 r15 covs2e FIND-2). When a revision RESTATES an earlier revision's decision, diff the two sentences; a dropped exclusion is a finding (2026-11-15 r16 predspec14 FIXIND-8: rev 13's 'not inside a hole' lost in rev 14). When a revision moves a fact's PRODUCER from library text to the author's input (labels, fields, separators), re-run every derived form using `!` over author inputs with an OPTIONAL, a REPEATED and a NON-CONFORMING field: a negation turns 'false on unset' into 'true on unset' (2026-11-15 r17 predspec17 F1) | opus |
| D | the LAST re-check before a build go | **readiness** | Per build unit: do its cites hold at the build tree, can its witness fail, is it separable, is it complete (every reader of what it changes listed)? Run the build tree's LOADER refusal paths over every new data-row shape the design writes, and list every check that compares an embed or copy with its source (2026-11-06 r6 span-cards: a measured row's `inputs` shape the loader refuses; a cell-less embed reddening three STORE checks). A new record is traced through BOTH the check's own feed and the production collector the census reads (kit partd3, 2026-11-12). A per-unit verdict, and the round's overall verdict "ready / ready with listed text fixes / not ready" (2026-11-03 r2 spanpick5: the most productive lens of the round); staff ONE readiness critic PER BUILD UNIT (2026-11-07 r13 planframe2: two 11-minute critics gave clean per-unit verdicts); for each new legal range coupled to an existing BUILD_D/FLAG_D row, grep every `-D<row>=` reference build in tests/ and check the range's default stays legal there (2026-11-15 r13 covs2d F14); re-run the design's own reader-finding greps and diff their output against the design's hit lists (2026-11-15 r15 covs2e: the subject's own greps printed S526, S3223 and three span writers its lists dropped); when the check plan spans units, give the sabotage/witness rows to ONE readiness critic and the code items to the per-unit critics (r13: 4 of 19 readiness findings duplicated) | opus |
| D | a change table against a client design doc (a fold) | **change-table completeness** | Re-derive the client's site list by grep over every term the folded rulings touch; every hit in a site no row covers is AFFECTED or UNAFFECTED with a reason; every row's cite lands on its WHOLE item (2026-11-16 r26 jointcond: a sonnet critic found 10 gaps, about 45 draft lines, in 3.3 min) | sonnet |
| D C | a table / slot / mechanism | **slot tracing** | Trace every slot to the table or mechanism the design names for it: is anything duplicated, narrowed or unreachable ("one table per slot")? Is it the third member of a family? | strong |
| D C | rulings relied on | **ruling check** | For each ruling, does it agree with the design and the guide, and what are its CONSEQUENCES? Fold into slot tracing when that runs. A wording the record hands to the round ("the wording is the manager's, to be checked") is diffed verbatim against every quoted copy (2026-11-16 r26 jointcond RULING-1: an inserted clause created the contradiction the round was asked to check). Sub-part: READINGS WRITTEN AFTER THE SUBJECT'S COMMIT (the manager's later readings in the record) get a HAND MAPPING per reading onto the subject's sentences, and each is attacked (2026-11-16 r28 absfold: 7 of 9 RULING findings). When a revision WITHDRAWS a reading, re-check every KEPT reading whose stated equivalence rested on it (2026-11-16 r29 predspec20 V4: 14:50 (b) 'same as satisfied' held only under (c) 'any text', withdrawn in the same revision). | strong |
| D | a measured quantity, check or data file | **measurement** | The docs/design/CLAUDE.md standing questions: the regime, the independent control, what moves when the data is regenerated. A named ESTIMATOR or gate is drilled like a selection rule, on constructed outcomes: clean, one outlier launch, bimodal, A/A above spread, an equal-effect sweep (2026-11-06 r4 span-cards: these drills found every gate defect, MEAS-2/4/7/8/10) | sonnet+ |
| D | a build proposal | **cost and overlap** | What does it cost, what does it buy, what measurement triggers it (D77), and does it overlap an in-flight refactor (D153)? Costlier must prove more. | sonnet+ |
| C | emitted C | **emitted vs replaced** | Generate C and asm of the new path AND the path it replaces, and diff every PRE-EXISTING entry BASE vs SUBJECT: what does the new code do worse or differently? For a deletion of fields no kit `.c` reads (grep), cap identity probes at a few hundred and spend the budget on the check lens's plants (r5 sp1g). When a row moves between tables, compare the gate INPUT each walk hands gate_check; plant the contract's opposite and require a refusal. For a zero-mover unit, cap this lens's probes at ~800 compiles and spend the rest READING the equivalence argument (2026-11-05 sp1e: F1 was found by reading). | strong |
| D C | a caller-facing contract | **contract** | Does the code (or the design) do exactly what the spec says for every admitted input class; do names describe behaviour (D174, D80)? Code mode probes edges with the built compiler. | strong |
| C | a performance claim / re-pin | **trade audit** | Every pin, floor or count moved: what speed, size or coverage did it give up, and who judged that trade? | sonnet+ |
| C | checks / pins / sabotage / flags | **check adequacy** | Per new or changed check: what input makes it fail, who chose it, does a witness reach the site, is the population counted (learnings §3)? For an INVARIANCE check ("the kit never reads X"), plant the reader where the containing object is CONSUMED, not only where the design's plant sits, and demand a reach control: the varied render differs from the absent-object render on at least one site (2026-11-03 r5 sp1g). Code mode: when the subject deletes or respells kit or src text, this lens runs `python3 -I scripts/m6read_check_sab_anchors.py` against the review tree (a plant may quote a body, not a name; 2026-11-04 r1 sp1b). Classify every plant compare as SAME, SILENT-MOVE (rc 0, bytes differ) or LOUD (rc != 0), deleting old outputs before each compare: a LOUD plant is caught by every corpus compile (r2 sp1c). For a census or backstop, plant a BYPASS whose text contains none of the conforming call's tokens; for an invariance harness demand a per-row reach table (each covered row, dropped, moves some reply or is declared unreached) (2026-11-05 sp1d). For a declared map or list read by a check, plant a DELETED line and an INVENTED line; both must go red (2026-11-05 sp1e). Name which site fields a generator family holds constant, and which kit rows that hides (2026-11-11 K38-2 review: F1 hid behind G2's on_miss_leaves=1 everywhere). | sonnet+ |
| D C | a planner / kit / back-end seam | **seam round trip** (manifesto principle 9) | Could what crosses this seam be written to text and read back by another process? Name every pointer, callback, shared state or target-language assumption that crosses. For a trace or record added for the seam, construct two inputs with EQUAL records and DIFFERENT picks (2026-11-05 sp1d). Any NEW state a seam change introduces is traced into trace shadows and emitted comments too, not only the seam fields (kit partd2, 2026-11-12). For a key the subject declares, check every member is printed in the record (2026-11-05 sp1e). Plant a wrong value in EVERY neighbouring field of the struct a witness record describes, not only the field the design names (2026-11-06 r8 s2a: a noise digest that skipped the handed value passed a value+1 fill). | strong |
| D C | a measurement harness (timed loops, cells, a run record) | **harness fidelity** | Is the thing TIMED the thing GATED, KEYED and RECORDED? Trace one cell end to end: the entry the timer calls vs the entry the answer gate calls, the population each counts, the key and hash the cell carries vs the code that ran, and whether the verdict reads the record or a live recomputation. Plant: halve the timed loop only; swap an arm's key; give two identical records different cells (2026-11-06 r9 s2c: all four answer-level findings were this shape) | opus |
| C | plain C structure | **house rules** | coding.md + style.md: duplication (name the shared abstraction), altitude, tables used as if-chains, side effects in predicates. | sonnet |

Always add the two standing questions to one lens (say which): **sibling of a
family** and **general form + unlocks** (with triggers).

Staffing: a "strong" lens gets opus; with both in scope, at least one strong
critic on behaviour (emitted code or simulation) and one on design. A subject that moves more than ~5 sabotage rows gets an opus check-adequacy critic, one row per sabotage (2026-11-11 K38-2 review: the sonnet critic was thin).

A D27 spec-first test author (tests written from the promise, denied src/ and
tests/, in a `scripts/mk_d27_cell.sh` cell) is not a critic: for a design with
a contract, RECOMMEND one in the draft; the launcher decides.

## 5. Brief and launch the critics (coordinator)

First check the round dir `$PCREC_TMPDIR/scratch/crit-<topic>/` is EMPTY or absent; if not, stop and ask the launcher for a new topic (2026-11-12 collision). In code mode, write ONE shared run kit into the round dir BEFORE briefing (a driver that builds/runs a pattern on BASE and SUBJECT side by side, and a libpcre2 oracle call) and name it in COMMON: every critic of round r2-reqpast finished in 3-10 min with no time spent building tools (2026-11-12). Under a box hold, check-adequacy plants become mutations of the EMITTED C, not rebuilds. In design mode, when the subject changes a walk over a built machine, the run kit also holds a script that applies the subject's UNBUILT rule to the emitted machine at any bound, and a trace compiler whose decision record the critics read (2026-11-15 covcap-r3: three lenses found the unreachable limit in minutes with `machine.py` and the KITPROOF record). On a re-check where `src/` is unchanged since the previous round's review tree, REUSE that round's kit and trace compiler: repoint them to the new round dir and sanity-run one known row before briefing (2026-11-15 covcap-r4: no build time spent); if its review worktree was pruned (§6.4 prunes it), reuse the kit scripts and rebuild the tree once: 3 minutes at -j2 (2026-11-15 r15 covs2e). When the subject is a timing harness or writes measurement sets: the fidelity lens compiles the timed file as the harness does and checks the timed site has ONE caller (a gate in the same file changed the timed code), the readiness lens LOADS every set the subject writes with the tree's loader, and a guard comparing two tables is planted with the CONSISTENT edit of both, not one (2026-11-15 kit round memfn-mfindcomb). In design mode, copy the frozen subject and its rulings record READ-ONLY into the round dir (`R/subject/`) and point the critics at those copies (2026-11-15 r12 predspec10: no grep-leak or denylist exposure, no repo access needed).

For a STAGED subject, COMMON quotes every interim wrongness the design accepts for this stage (e.g. "wrong there until B") beside the no-abi/no-stamp rulings (r18 covs2a: the contract critic spent its top finding rediscovering one). When the subject's evidence includes a sweep with committed or scratch RAW data, copy it read-only into the round dir and name it in COMMON as the population (2026-11-02 spanpick: three lenses counted populations the report alone would not show). COMMON has critics read every ruling file (decisions.md, plan.md) via `git show <freeze>:path`, never the live tree (2026-11-03 r2: a ruling landed mid-round). For a rate-sensitive subject COMMON names each rate regime and how to reach it (default prior; `-e utf8` = NONE; `-I tests/findings/adversarial --analysis=uniform` = all-tie, run from the review tree; `-I DIR --analysis NAME` = a real bundle), and in code mode tells critics to compare BASE/SUBJECT emitted C under the SAME basename in two dirs (the C names its basename; r1 sp1b). Check every regime spelling with one compile before briefing (2026-11-05 r1 sp1d: the documented spelling was refused); a BASE/SUBJECT compare pair counts as 2 compiles in the budget. A brief that sets a probe matrix states the PRODUCT next to the cap (e.g. `25 patterns x 9 arm sets x 2 encodings x 2 trees = 900 compiles; cap 600`) (2026-11-15 r4 fixposts2c: a critic miscounted its matrix and ran 900+ compiles against a ~600 cap). Write one COMMON brief file under `$PCREC_TMPDIR/scratch/crit-<topic>/` (scope
When the subject's evidence includes a sweep with committed or scratch RAW data, copy it read-only into the round dir and name it in COMMON as the population (2026-11-02 spanpick: three lenses counted populations the report alone would not show). COMMON has critics read every ruling file (decisions.md, plan.md) via `git show <freeze>:path`, never the live tree (2026-11-03 r2: a ruling landed mid-round). COMMON names which ONE lens verifies the owner's quotes word for word against the record; the others cite them without re-checking (2026-11-16 r26 jointcond: two lenses re-checked the same ~19 quotes, both 0 drift). A lens is briefed from the SUBJECT's text, never from the record's paraphrase of what the subject should say (2026-11-16 r29 predspec20: a wrong list in the simulate brief, caught by the critic). For a rate-sensitive subject COMMON names each rate regime and how to reach it (default prior; `-e utf8` = NONE; `-I tests/findings/adversarial --analysis=uniform` = all-tie, run from the review tree; `-I DIR --analysis NAME` = a real bundle), and in code mode tells critics to compare BASE/SUBJECT emitted C under the SAME basename in two dirs (the C names its basename; r1 sp1b). Check every regime spelling with one compile before briefing (2026-11-05 r1 sp1d: the documented spelling was refused); a BASE/SUBJECT compare pair counts as 2 compiles in the budget. A brief that sets a probe matrix states the PRODUCT next to the cap (e.g. `25 patterns x 9 arm sets x 2 encodings x 2 trees = 900 compiles; cap 600`) (2026-11-15 r4 fixposts2c: a critic miscounted its matrix and ran 900+ compiles against a ~600 cap). Write one COMMON brief file under `$PCREC_TMPDIR/scratch/crit-<topic>/` (scope
mandate, read-only rules, subject and paths, the guide files, design docs and
spec sections the subject cites, the denylist, the output format), then one
short per-lens prompt: title `CRITIC <lens> (<model>): <topic>`, "read COMMON
first", the one question, the output file path.

COMMON tells critics to pass patterns in single quotes or via a file and to check the `Pattern:` header of every emitted file they cite before reporting a byte-identity or route claim (2026-11-15 r13 covs2d MEASURE-4: shell quoting ate a `\b`, a refuted finding). A brief carries ONE question with at most two sub-parts and itself requires "append each finding to your file the moment you have it, one append per finding"; a critic still without findings 20 min after its one resend is replaced by a fresh, narrower critic at once (2026-11-07 r1 xarch: two wide opus briefs wrote nothing in 45 min, their narrow replacements delivered in 7-9 min).

Output format (in COMMON): the critic CREATES its file (say it does not exist
yet: critics took a named file for an input), with its headings, as its FIRST action (2026-11-05 r7: a critic that wrote last wrote nothing) and writes it INCREMENTALLY;
each finding has an id `<LENS>-n`, CONFIRMED (with a repro: input, command,
observed vs expected) or SUSPECTED (what would confirm it), severity (answer /
speed / size / maintenance / doc / design), effort, blast radius, file:line or
§; a finding against a ruled D-row cites it and argues, or drops; the file
ends with PROBED-AND-HELD (with case counts). Final reply at most 150 words. A critic whose findings-file Write is REFUSED SendMessages its findings to the coordinator AT ONCE, marked relayed (2026-11-06 r2 vlb3: 38 minutes of results were invisible). If a harness rule REFUSES the critic's findings-file Write, it does not route around the refusal: it returns the findings as its final text (that reaches the launcher, who relays it to the coordinator) and the draft marks that critic 'relayed' (2026-11-05 r4 altnf2).

Each critic gets a DELIVER file beside its output (`report=` its findings file, `sections:` the
findings + PROBED-AND-HELD, `nonempty: Findings; PROBED-AND-HELD` (r3 vlb4: lanecheck passed an empty template), `commit: no`) and ends only after `scripts/lanecheck --dir $PCREC_TMPDIR/scratch/crit-<topic> --deliver FILE NAME` (without `--dir` its pass record lands in the repo root, 2026-11-03 sp1a)
prints DONE; the coordinator runs `scripts/lanewatch --dir $PCREC_TMPDIR/scratch/crit-<topic> NAME...`
instead of waiting for replies (nested replies are often lost).

Coordinator-only notes (process.md, planted checks, suspicions) live in a
`.coord/` subdirectory of the round dir, and COMMON's denylist names `.coord/`
(2026-10-31 pricing-split: a critic read the coordinator's planted-check note).
Each critic writes its scratch ONLY under its own `<round>/<lens>/` subdirectory, and nobody copies a revision a lens is denied into the shared round dir (2026-11-15 covcap-r2: three denied revisions sat in the round dir beside every lens's files).
Before briefing, check where every evidence script the critics will run writes,
and redirect writes out of denied dirs and out of the main tree (set
`PCREC_TMPDIR` to the critic's own dir; set `LANEWATCH_LOG` under `.coord/`)
or forbid the mode (2026-10-31 bakeoff3).

In design mode the coordinator ALWAYS PRE-CREATES each critic's findings file (cheap; it also matters when the round may straddle a box script deadline, no lanecheck/lanewatch after it), with its headings, and names a `CRITIC COMPLETE` line the critic writes last as the completion marker (2026-11-16 r19 predspec19: both fix-induced critics produced no file, and a missing file cannot be told from a critic still working; 2026-11-16 r28 absfold: made unconditional, every critic wrote into it cleanly).

Launch all critics in one message, background, UNNAMED (a teammate cannot name agents). No addenda to a running
critic; a missed input goes to a fresh critic.

## 6. Monitor, verify, draft (coordinator)

1. Critics may return in the launch turn even when backgrounded; then read the files at once.
   Read each critic's FILE when it idles; a critic without its file gets ONE
   SendMessage asking for it. A critic idle on its own background probes gets
   one nudge to resume. Stop each critic (TaskStop) once its file is complete.
2. Launch ONE verifier (sonnet unless a finding needs opus judgment) over all
   CONFIRMED findings that would change code or a design: answers against the
   oracle (libpcre2 / python `re`), speed with `perf stat -e instructions:u`
   pinned `taskset -c 7` and repeats, size with `size`, structural claims by
   quoting the cited lines, design claims by the simulation or grep they name.
   Give it a DELIVER block like a critic's (its file `verify.md`, one section per finding id, a closing
   `VERIFY COMPLETE` line; 2026-10-29 landwalk: without one the verifier improvised its own shape).
   Per plant claim the verifier records the plant compiler's exit code beside the byte verdict (r2 sp1c). A REFUTED verdict quotes the exact call it ran; the coordinator re-runs every REFUTED that rests on a crafted input before drafting (2026-11-03 sp1f: a verifier refuted with a malformed key). The coordinator may instead verify inline, recording the calls, when every CONFIRMED finding is a quote claim or a one-call oracle repro (2026-11-15 r14 predspec12: a verifier agent would have cost more than the checks). Two critic findings that CONTRADICT each other go to the verifier as ONE item (kit round partd2, 2026-11-12). It writes `verify.md` INCREMENTALLY, one finding at a time (a nested agent's final reply is often
   lost: 2026-10-26 ic1b-code): HOLDS / REFUTED / PARTLY / not verified (why).
   Use an opus verifier when the CONFIRMED findings are interlocking semantic claims, and group same-root findings as ONE item (2026-11-16 r29 predspec20: 16 items, 5 PARTLY corrections, one unification).
3. Draft `$PCREC_TMPDIR/scratch/crit-<topic>/review.md` in the
   `docs/dev/reviews/` shape: subject; lenses as run (lens, model, question,
   why chosen); which lens caught what; findings by id with a PROPOSED
   disposition (FIX-NOW | PLAN | DOC | REJECTED | NOTED) and a one-line reason;
   PROBED-AND-HELD; by-id completeness; lessons for the guide. Consolidate
   overlapping findings (name every lens that found it). Copy critic texts and
   `verify.md` beside it in `review/`.
4. Remove the review worktree (`scripts/wtprune --apply --force --quiet-min 1 crit-<topic>`: the default 120-minute quiet gate keeps a freshly built tree)
   and stop the verifier.

## 7. Meta-monitor the round (coordinator)

Keep `$PCREC_TMPDIR/scratch/crit-<topic>/.coord/process.md` AS YOU GO: per agent, launch
and end time, model, final state (file complete / resent / nudged / stalled);
brief confusions; delivery failures; blinding leaks you noticed; per lens,
findings raised / verified / severity / overlaps; time to draft. At the end
add:
- **Process observations:** what slowed or confused the round, what the
  lens table missed or over-staffed.
- **Proposed changes:** concrete text for this skill, `docs/dev/guide/critics.md`
  or the COMMON template, each with the observation that motivates it.
- **Framework notes:** what this round says about the coordinator pattern
  itself (a manager launches one coordinator that runs a fan-out, verifies and
  drafts for a ruling), and where else it might fit, with the evidence.

## 8. Hand back (coordinator)

One SendMessage to the launcher, at most 15 lines: the draft path, the
answer-level and speed-level findings, proposed FIX-NOW ids, and the top
proposed process change. Then END.

## 9. Rule and close (manager)

1. Read the draft and `process.md`; rule each disposition (overrule with a
   reason); commit the review as `docs/dev/reviews/YYYY-MM-DD-rN-<topic>.md`
   (+ sibling dir of critic texts), indexed in `docs/dev/reviews/CLAUDE.md`. Before that commit, `grep -rnE 'plan\.md:[0-9]' <review>.md <review dir>` must find nothing:
   plan_lint PL14 rejects line-numbered plan.md cites (they rot), and one blocked main's push of 2026-11-04 r1;
   cite a row by its tag instead. A review must not cite a spec by LINE either (the pre-commit hook rejects it): cite the section (2026-11-15 r13/r14).
2. FIX-NOW items go to fix lanes on the subject branch (fresh agents, the
   review as brief source); the round closes when every finding has a
   disposition and every FIX-NOW is landed or ruled.
3. Accept or decline each proposed process change: accepted ones go into this
   skill, `docs/dev/guide/critics.md` "Lessons from review rounds", in the same
   commit as the review. Framework notes go to
   `docs/dev/meta/coordinator_framework.md` (append, dated, with evidence).
4. Report to the owner in plain words: what was reviewed, which lenses ran and
   why, what each found, what is being fixed, whether the subject may proceed.
