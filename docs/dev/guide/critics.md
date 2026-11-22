# How a critic uses the guide

First version; the 2026-10-23 S3 code-review round will refine it.

The procedure for running a round (freeze, blind, pick lenses, verify, compile)
is the `pcrec-critic` skill (`.claude/skills/pcrec-critic/SKILL.md`; design, code or both, or an architecture note, run by a coordinator agent);
this page holds the rules it reviews against. Lenses are chosen per change from
the skill's lens table; no lens set is standard because an earlier round used it.

A critic reviews a diff against the guide (`coding.md`, `architecture.md`,
`style.md`, the area's `addenda/`). Critics are read-only and never run `make`
(D6). Where a finding is already known, use blinded critics (D27). Label
findings CONFIRMED (with repro) or SUSPECTED and carry a PROBED-AND-HELD list
(`docs/dev/reviews/CLAUDE.md`).

## Standing lenses
1. **Design compliance.** Does the change follow `architecture.md`? Is each
   selection a declared table, with no private copy of an existing mechanism?
2. **Emitted code vs what it replaces.** Read the generated C and asm of the
   new path AND of the path it replaces; compare, do not infer from the source.
3. **House rules.** `coding.md`, including the altitude rubric (length is a
   trigger, never a verdict; common extracts first) and `style.md`.
4. **Test and gate adequacy.** Does each new check have an independent control,
   a witness that reaches its site, and a counted population
   (`docs/dev/learnings.md` section 3)? Does it still pass when the code is wrong?
5. **Sibling of a family.** Is a new predicate or table a sibling of an
   existing decision family? Name the family.
6. **Propose the general form and unlocks.** Beyond refutation: name the general
   form of the change and what it would unlock, with triggers.
7. **Seam round trip (manifesto principle 9).** Could what crosses this seam be written
   to text and read back by another process? Name every pointer, callback, shared
   state or target-language assumption that crosses. Applies to design and code
   rounds touching planner, kit or back-end seams.

## Rules
- **A re-pinned floor or count is a TRADE to judge, never bookkeeping.** Example:
  a SIMD floor dropping 39 to 33 in a re-pin hid a 29x caseless-literal
  slowdown (2026-10-23). Ask what moved and why.
- A finding contradicting a ruled D-row, a design note's ruled section, or a
  recorded panel disposition must cite it and argue against it, or drop (A1 of
  `docs/dev/reviews/code_review_criteria_draft.md`).
- A duplication finding names the shared abstraction: signature, call sites
  replaced, what varies (A2).
- A finding cluster names the checks and anchors that bind the code it would
  move (A3), and carries severity, effort and blast radius (A4).
- Cite metric artifacts where one applies (A5, `tools/review/`).
- Review the function population length-ordered and say where you stopped (the
  draft's Addendum 2); a long function that passes the five altitude questions
  stays long, and the finding says so.

## Design rounds
A design round reviews a document before a build go. Rules a design critic
applies, beyond `architecture.md`:
- **Design panels are the cheapest reviews.** A finding in a document is a
  paragraph edit; the same finding in built code is a fix lane (learnings §5).
- **Question premises, not only errors.** "Do we really need this?" and "is this
  really constant?" each killed a mechanism several panels had accepted; every
  panel was internally sound on an unexamined premise (learnings §5).
- **Simulate against the real data before adopting.** A proposed table or rule
  is run over the real corpus; prototype rival mechanisms head to head and let
  measurement pick (learnings §5).
- **Propose the general form and its unlocks,** with triggers, not only
  refutations (Frank 2026-10-09).
- **Sibling of a family:** at about three dispersed members of a decision
  family, propose the unified table (Frank 2026-10-06, "forest for the trees").
- **BELIEVED marks are the target list:** what a design marks as believed rather
  than measured is where it breaks (learnings §5).
- **Mark the cost:** costlier proposals must prove more; raise cost as a
  challenge, not a veto (Frank 2026-10-17).

## Lessons from review rounds

Round 2026-11-15 r18, covs2a code round (`docs/dev/reviews/2026-11-15-r18-covs2a.md`); process changes ruled 2026-11-15 (manager): (1) **plants for a REACH-using row are built with `build/pcrec build/pcrec-harness`** (reach.sh read REACH-FAILED on every compiler-only plant); (2) **for a staged subject COMMON quotes every interim wrongness the design accepts for the stage** (CONTRACT-1 rediscovered 'wrong there until B').
2026-11-18, proposed by the kit after its round r44 (memfn-forms7), accepted 2026-11-18 (manager): **simulate lens: "for every grouping a pooled estimator COLLAPSES, drill with an interaction term at that grouping; a synthetic model keyed like the fit cannot fail it"**.

2026-11-18, proposed by the kit after its round r44 (memfn-forms7), accepted 2026-11-18 (manager): **perturbation lens: "name what each control holds FIXED (data sections, the driver's allocations, entry points outside the moved section) beside what it moves, and say which of those ships"**.

2026-11-18, proposed by the kit after its round r44 (memfn-forms7), accepted 2026-11-18 (manager): **"a max-over-candidates term gets the never-picked drill with a NOISY loser, not only a slow one"**.

2026-11-17 r40, predicates_draft.md rev 24 (`docs/dev/reviews/2026-11-17-r40-predspec24.md`), accepted 2026-11-17 (manager): **drill every "matches whole on the stretch" operator with an anchored, a `\b` and a lookahead operand, and treat a model built from the engine's own construction as no control** (A3: `&` matched the operand in the SUBJECT, so every anchor-free check passed and the LAW failed 1,344 of 1,365; PART C's PCRE2 models shared the construction).

2026-11-17 r40, same round (accepted 2026-11-17, manager): **a mode-closure lens adds a CAPTURE-STATE drill to every regex-model claim: an optional label inside a looped place, a label looped at two depths read from outside, a place inside a place** (A1/A2: 5/34, 300 and 693 differ; every top-level model set its labels on every path and could not see carry-over).

2026-11-17 r40, same round (accepted 2026-11-17, manager): **when evidence prints "(labels compared)", check each MODE's comparison key carries the labels; and name the evidence's ORDER/SWAP switch in COMMON and ask whether it can fail** (A5: a WHOLE key that is a bool compared holding only, 0 printed, 117 real; C1: SWAP reversed nothing that carries meaning in rev 24).

2026-11-17 r42, predicates_draft.md rev 24.2 (`docs/dev/reviews/2026-11-17-r42-predspec242.md`), accepted 2026-11-17 (manager): **COMMON states a document rule by QUOTING the subject's sentence with its line, never by the launcher's paraphrase** (B1: the brief's "unless spelled padded" sent the simulate critic to a refuted consequence; section 2.4 says "unless the literal has them"; the launcher's error).

2026-11-17 r42, same round (accepted 2026-11-17, manager): **a per-pass rule gets a NULLABLE-BODY drill (PCRE runs and keeps a final empty iteration) and its pass forms are drilled at TWO DEPTHS, literal vs hole spelling of one pattern** (A1/A2: two lenses reached the empty pass by two controls; 6 / 11 / 11 and 13 / 353 / 973 differ).

2026-11-17 r42, same round (accepted 2026-11-17, manager): **a callout model of a TEMPORAL rule is drilled with a group set by a lookaround inside a pass** (A5: a positional helper-group construction passed 16 of 16 and failed 9 / 33 / 33 on the lookaround class).

2026-11-17 r34, predicates_draft.md rev 23.1 (`docs/dev/reviews/2026-11-17-r34-predspec231.md`), accepted 2026-11-17 (manager): **on a re-check, diff every count the previous round's VERIFIER printed against the number the revision publishes, and quote the verifier's number beside the critic's in the fix-lane brief** (A1: r33's verifier printed 281 for L83 searched; rev 23.1 published the engine's 371, which read values where the draft's own section 2.2 reads canonical numerals).

2026-11-17 r34, same round (applied by file34 as plain additions to the lens rows): **a manager ruling stated as a DERIVATION is read literally everywhere its premise applies (it can reverse a kept ruling, so it was a scope rule), and find-all places are a mode of their own in the mode-closure lens** (MODECLOSURE-4, A3).

2026-11-17 r33, predicates_draft.md rev 23 (`docs/dev/reviews/2026-11-17-r33-predspec23.md`), accepted 2026-11-17 (manager): **when a revision RE-ALLOWS an operator, re-run every SAME row, warning and compile error whose stated reason assumed the operator absent** (F1, F7, F8: rev 22's "UNKNOWN and FALSE drop the same rows" silently underwrote L83, the `default.unused` (b) warning and the §5.2 error once NOT on conditions was legal again).

2026-11-17, proposed by the kit after its round r41 (a "layout twin" was a whole-text shift that kept every hot loop's 64-byte phase, so it did not stand in for another head's different body: the sixth level of the same family), accepted 2026-11-17 (manager): **simulate lens: drill a comparison kind by its PERTURBATION, what actually differs between the two objects compared (inspect with `nm` / `readelf`: which symbols moved, which loop alignments changed), not by the count of executables; a control that does not vary what the real comparison varies is not a control.**

2026-11-17, proposed by the kit after its round r39 (every noise estimator compared runs of ONE executable while the quantity judged, a head length against another, compares TWO executables: a per-binary layout offset was invisible to every estimator and to the confirm re-run), accepted 2026-11-17 (manager): **simulate lens: also drill COMPARISON KINDS: for each ratio, which physical object each side is (the same executable, two executables, two builds, two boxes), and whether the noise estimate was taken over the same kind of pair** (the apples-to-apples rule, memory pcrec-speed-compare-apples-to-apples, applied to the noise model).

2026-11-17, proposed by the kit after its review rounds through r38 on the form cards' pick rule (three rounds in a row found the defect exactly one level below the drills), accepted 2026-11-17 (manager): **simulate lens: a POOLED noise estimator is drilled with the noise confined to EACH level it pools over (one drill per level, not one for the estimator), plus a launch-order step (the same data presented in another run order).**

2026-11-17 r33, same round (applied by file33 as a plain addition to the simulate lens): **when the evidence engine and the text agree on every number, read the engine's header for the readings it implements and check each is a sentence of the subject** (F2, F4: fallthrough over filtered `|` and find-all hits were the engine's own choices).

2026-11-16 r32, [COVER-CAP] stage 2 (`docs/dev/reviews/2026-11-16-r32-covs2code.md`), accepted 2026-11-16 (manager): **a spec sentence that promises a fallback ("the compile does not fail") needs its witness at the EXTREME of the newly legal range before the hunk lands: run the range's top through every cap in limits.def's `compile budget` class, not only the cap the design names** (F1: three lenses found the refusal from three sides; the design priced one of two size caps).

2026-11-16 r31, condition_kind.md Parts I-III (`docs/dev/reviews/2026-11-16-r31-condkind.md`), accepted 2026-11-16 (manager): **a DEFINITION note (a model replacing a foundation) gets a MODE-CLOSURE drill: every operator run in every mode the language has (whole value, searched, inside a nested filter role), whatever modes the subject's evidence ran** (finding A: the evidence was whole-only by design; three lenses found the searched-mode splits by three routes).

2026-11-16 r31, same round, accepted 2026-11-16 (manager): **when the record closes with a summary ("STATE OF THE MODEL"), the ruling lens builds the next revision's RULING TABLE (every ruling and reading: stands / retired / reversed / open, by entry) instead of checking the summary alone**; that table was the round's most directly usable output.

2026-11-16 r31, same round, accepted 2026-11-16 (manager): **a "MINE, to be checked" restatement that changes answers on a locked rule's territory is an owner question, not a manager restatement: the ruling lens tests each such item against every LOCKED rule** (RULING-2: the restated `all` against absent-rule (1)).

2026-11-16 r30, predicates_draft.md rev 22 re-check (`docs/dev/reviews/2026-11-16-r30-predspec22.md`), accepted 2026-11-16 (manager): **when the evidence engine implements a rule by TRAPPING a poisoned value (a DOM "consulted"), swap the operand order inside every lambda and re-run; quote a count only after the swap leaves it unchanged** (SIMULATE-9: 30 of 355 by fn order alone).

2026-11-16 r30, same round, accepted 2026-11-16 (manager): **when a fold introduces a NESTED program (a complemented pattern, a named program under an operator), drill every "adding X never ..." claim at three insertion points: the outer chain, inside the nested program, and through a binding both share** (SIMULATE-6, FIXIND-2: two lenses, two sides).

2026-11-16 r30, same round, accepted 2026-11-16 (manager): **recompute every worked count with the DOCUMENT's own set-membership rules (literal domains, canonical numerals), never the check script's lambda** (SIMULATE-2: `int()` against the canonical-numeral rule).

2026-11-16 r30, same round, accepted 2026-11-16 (manager): **grep every "CF hh:mm" citation of an owner quote: each must resolve to a record entry** (RULING-1/-3: two remarks quoted with no entry, one quoted differently in a parked-list file). Also: build a runnable read-only copy (`R/tree/`) when lane scripts read each other by relative path, and add the ruling lens on a re-check whenever the record hands the manager's readings to the round.

2026-11-16 r29, predicates_draft.md rev 20 re-check (`docs/dev/reviews/2026-11-16-r29-predspec20.md`), ruled 2026-11-16 (manager): **a revision that WITHDRAWS a manager's reading must re-check every KEPT reading whose stated equivalence rested on it** (V4: 14:50 (b) "same as satisfied" was true only under (c) "any text", withdrawn in the same revision).

2026-11-16 r29, same round, ruled 2026-11-16 (manager): **"apply each acceptance case in its REAL MODE" extends to every NEW worked table the revision adds, not only the acceptance cases** (SIMULATE-1/6: both new tables stated whole-value answers that move when searched).

2026-11-16 r29, same round, ruled 2026-11-16 (manager): **the DOMAIN drill gains an equal-behaviour pair built by a CONDITION (`rx & (cond)` vs the narrowed rx) and by a second `&` operand** (FIXIND-7, AND-DEAD).

2026-11-16 r29, same round, ruled 2026-11-16 (manager): **verifier model: opus when the CONFIRMED findings are interlocking semantic claims; give it same-root groups as one item** (V2/V9 unified four findings and corrected three; 16 items, 5 PARTLY corrections).

2026-11-16 r28, joint_condition.md §4G absent-label rule (`docs/dev/reviews/2026-11-16-r28-absfold.md`), ruled 2026-11-16 (manager): **on a fold that lands after the manager's own later readings (here 14:50, after the note's last commit), keep "readings written after the subject's commit" as an explicit sub-part of the ruling check, with a hand mapping per reading**: it was the most productive part per minute (7 of 9 RULING findings).

2026-11-16 r28, same round, ruled 2026-11-16 (manager): **simulate lens: add a standing DOMAIN drill**: for any "some value" or existential reading, run it against a complement set, a dead branch and a lookbehind-restricted group in two spellings. Three lenses reached the domain (MARK-DOMAIN) from different sides; one drill would have reached all three.

2026-11-16 r26, joint_condition.md design note (`docs/dev/reviews/2026-11-16-r26-jointcond.md`), ruled 2026-11-16 (manager): **simulate lens, design mode: for a design whose values are SETS, two spellings of the SAME set (the empty set above all; product vs dictionary order) must give the same answer in every mode** (ZERO-EMPTY: found by three lenses; an inserted split made the answer depend on how one set was spelled).

2026-11-16 r26, same round, ruled 2026-11-16 (manager): **a design whose deliverable is a CHANGE TABLE against a client document (a fold, here §9) gets a change-table completeness lens: re-derive the client's site list by grep over every term the folded rulings touch, and check each row's cite lands on its whole item** (REV20-1..10: a sonnet critic, 3 minutes, 10 findings, about 45 draft lines the table missed).

2026-11-16 r26, same round, ruled 2026-11-16 (manager): **when a ruling's record says the WORDING is the manager's "to be checked by the critic round", the ruling lens diffs every quoted copy of that wording against the record verbatim** (RULING-1: an inserted clause created the contradiction it was asked to check). Give owner-quote verification to ONE lens; the others cite without re-checking.

2026-11-16 r19, predicates_draft rev 19 (`docs/dev/reviews/2026-11-16-r19-predspec19.md`), ruled 2026-11-16 (manager): **when a round may straddle a box script deadline, the coordinator pre-creates each critic's findings file with its headings and a `CRITIC COMPLETE` marker line the critic writes last** (both fix-induced critics ended with no findings file, and an empty file is visibly empty where a missing one is not).

2026-11-15 r17, predicates_draft revs 16-17 confirming re-check (`docs/dev/reviews/2026-11-15-r17-predspec17.md`), ruled 2026-11-15 (manager): **when a revision moves a fact's PRODUCER from library text to the author's input (labels, fields, separators), re-run every derived form using `!` over author inputs with an optional, a repeated and a non-conforming field** (F1: rev 16's always-set helper labels hid a strict-form inversion; two lenses found it in minutes).

2026-11-15 r17, same round, ruled 2026-11-15 (manager): **an evidence row that shows a refusal or an error names the mechanism that refuses; an emulator's own raise is not evidence** (F6: the wrong-length "compile error" table showed the script's own `raise`).

Round 2026-11-15 r16, predicates_draft rev 14 confirming re-check (`docs/dev/reviews/2026-11-15-r16-predspec14.md`); process changes ruled 2026-11-15 (manager): (1) **for a diagnostic whose message makes a semantic claim ('adds nothing', 'never matches'), plant a counter-case for the CLAIM in each place it fires (a non-edge anchor), not only the evidence's own population** (SIMULATE-1: the evidence table tested only edge anchors); (2) **when a revision RESTATES an earlier revision's decision, diff the two sentences; a dropped exclusion is a finding** (FIXIND-8: rev 13's 'not inside a hole' lost in rev 14).

Round 2026-11-15 r15, cover_cap rev 5.1 readiness re-check (`docs/dev/reviews/2026-11-15-r15-covs2e.md`); process changes ruled 2026-11-15 (manager): (1) **when reusing the previous round's kit and its review worktree was pruned (§6.4 prunes it), reuse the kit scripts and rebuild the tree once** (3 minutes at -j2; the reuse premise silently failed here); (2) **readiness re-runs the design's own reader-finding greps and diffs their output against the design's hit lists** (the subject's own greps printed S526, S3223 and three span writers its lists dropped: FIND-4, FIND-10); (3) **a claim that witnesses 'move with X by construction' is drilled per row KIND (verdict, facts, answer, mech REACH) at X's extreme admissible values** (FIND-2: the `@D` mechanism covered verdict rows only).

Round 2026-11-15 r13, cover_cap rev 5 §11 design (`docs/dev/reviews/2026-11-15-r13-covs2d.md`); process changes ruled 2026-11-15 (manager): (1) **COMMON tells critics to quote patterns (single quotes or a file) and to check each emitted file's `Pattern:` header before a byte-identity or route claim** (MEASURE-4: shell quoting ate a `\b`); (2) **readiness greps every `-D<row>=` reference build in tests/ for each new legal range coupled to a BUILD_D/FLAG_D row** (F14); (3) **one readiness critic owns the sabotage/witness rows, the per-unit critics the code items** (4 of 19 findings duplicated).

Round 2026-11-15 r14, predicates_draft rev 12 design re-check (`docs/dev/reviews/2026-11-15-r14-predspec12.md`); process changes ruled 2026-11-15 (manager): (1) **a ruling stated by POSITION ("the filter side of X") is tested against the operator's symmetry and against nesting** (F1/F2); (2) **the coordinator may verify inline when every CONFIRMED finding is a quote claim or a one-call oracle repro, recording the calls** (a verifier agent would have cost more than the checks).

Round 2026-11-15 r7, cover_cap rev 4 last re-check (`docs/dev/reviews/2026-11-15-r7-covcap-r4.md`); process changes ruled 2026-11-15 (manager): (1) **when `src/` is unchanged since the previous round's review tree, reuse its run kit and trace compiler** (repoint, sanity-run one known row); (2) **when a revision restructures a walk into numbered per-depth rules, the fix-induced lens maps every conjunct the walk absorbs to the depth range it reads today (0..k, k, 0) and checks each at the boundary depth `k`** (rev 4 moved C9 into a rule that never sees the rows at `k`, where today's loop is inclusive: an answer move had it been built). Also accepted from round r6 (its lesson 1): **a design that adds a LIMIT on a walk over a machine names every limit that already bounds that machine and shows the new one can bind with a witness that has a machine** (the premise lens greps `limits.def` for the object's producer).

Round 2026-11-15 r6, cover_cap rev 3 re-check (`docs/dev/reviews/2026-11-15-r6-covcap-r3.md`); process change ruled 2026-11-15 (manager): **for a design that changes a walk over a built machine, the round's run kit includes a script that applies the unbuilt rule to the emitted machine at any bound, plus the trace compiler's decision record.** With them three critics independently found that rev 3's new length limit could never bind (the machine's own state ceiling binds first).

Kit round 2026-11-15 memfn-mfindcomb (its review file is the kit's), lessons accepted by the kit manager and relayed: (1) **harness fidelity: compile the timed file as the harness does and check the timed site has ONE caller** (a second caller in the same file outlined a static inline finder); (2) **LOAD every measurement set the subject writes with the tree's loader** before the window (two sets were unloadable while the self-test pinned the refused shape); (3) **a guard comparing two tables is planted with the CONSISTENT edit of both,** not one half (a control sharing its source).

Round 2026-11-15 r5, cover_cap rev 2 (`docs/dev/reviews/2026-11-15-r5-covcap-r2.md`); process changes ruled 2026-11-15 (manager): (1) **each critic writes scratch only under its own `<round>/<lens>/` subdirectory** and never copies a denied revision into the shared round dir (the round dir held three copies of the design's earlier revisions, denied to all lenses but fix-induced); (2) **every "today the tree does X" number in a design carries the exact command that produced it**, and the premise lens re-runs each one (rev 2's "`[ab]{1000}` lists 24" and "a cliff near 511" were false on one compile, found by two critics in minutes; the design brief template carries the same rule); (3) **the premise lens asks, for each function a design KEEPS, whether the new text requires a property that function lacks** (rev 2 kept `sw_take` while needing cross-depth identity it does not have; three critics found it).
Round 2026-11-15 r4 fixposts2c (`docs/dev/reviews/2026-11-15-r4-fixposts2c.md`): a brief that sets a probe matrix states the product next to the cap (`patterns x arm sets x encodings x trees = N compiles; cap M`); the respell critic miscounted its matrix and ran 900+ compiles against a ~600 cap.

Round 2026-11-03 r1, span_pick rev 4 re-check (`docs/dev/reviews/2026-11-03-r1-memfn-spanpick4.md`): (1) a quoted region boundary from a sweep states its grid, and a boundary on a grid point is unproven; (2) a choice rule normalised over the candidate set must state whether it is independent of never-picked candidates (drill: add one); (3) every "owner rulings since rev N" row cites its durable home at the freeze, or is marked PENDING-RECORD.

Round 2026-11-02 r1, kit span_pick rev 1 (`docs/dev/reviews/2026-11-02-r1-memfn-spanpick.md`): (1) a simulate lens recomputes every outcome the design quotes with the design's OWN formula (smp20's quoted win was the evidence study's doubled-hit arithmetic; by the text's formula it loses); (2) give premise/simulate critics the evidence sweep's RAW data as the population; (3) a design's proposed sabotage witness must reach its plant by the design's own arithmetic ([MECH-REACH] applied to a design: drop-F cannot move smp20 because F already agrees there).

Round 2026-10-23 r1, kit S3 (D172's REPORT routing), four blinded critics
(`docs/dev/reviews/2026-10-23-r1-memfn-s3-code.md`, landing with lane/memfn-s3,
§4). Three of four caught a 29x caseless-literal slowdown from the code alone.
1. **Review the EMITTED artifact, both arms.** The emitted-vs-replaced lens
   caught it with loops and asm; the source-only code-quality lens missed it.
2. **Trace every slot to its named table.** The design lens caught it by
   showing a declared row (the PAIR find form) was unreachable. This is how a
   parallel mechanism shows up.
3. **A lowered performance-form floor is a trade to judge,** not a pin (the
   rule above).
4. **Blinding leaks** through report headers and git log. Give each blinded
   critic a clean worktree at the subject sha plus a denylist.
5. **The manager's rulings are review subjects too.** The defect entered
   through a ruling.
6. **Staffing:** at least one strong-model critic on emitted behaviour and one
   on design; the weaker-model lenses found real but smaller issues.

Round 2026-10-23 r2, find-all iterators (`docs/dev/reviews/2026-10-23-r2-iter-code.md`), the
first run of the `pcrec-critic` skill, five lenses picked by profile.
1. **Pick lenses by what the change touches.** The contract and slot-tracing lenses, absent from
   the earlier fixed four, found the answer bug and its cause (a private copy of the anchored body).
2. **Only the emitted-vs-replaced lens saw a regression to EXISTING entries.** Ask that lens to
   diff every pre-existing entry BASE vs SUBJECT, not only the new path.
3. **A known result re-found blind calibrates the round** (`_next_n` at k=1 slower than `_next`).

Round 2026-10-23 r2, kit S3 C1 build (`docs/dev/reviews/2026-10-23-r2-memfn-s3-c1-code.md`, lane/memfn-s3, §6), the skill's first use by the kit.
1. **The hidden-issue test passed again with the strong lenses:** both opus lenses found, blind, that two-or-more-member non-case-pair stops get a scalar walk.
2. **Verification earns its place:** it corrected a modelled magnitude (same-set windows re-read 1.1-2.5 bytes/byte on dense input, not 6-12) and showed the lane's example patterns were controls, not witnesses.
3. **Keep the check-adequacy lens whenever checks or flags change:** it alone found a broken gate (`make test-axes`'s memfn arm: MEMFN_CLASS lacked the new forms).
4. **The slot lens lists each ruling's CONSEQUENCES,** not only its agreement with the design.


Round 2026-10-24 r1, compiled substitution (`docs/dev/reviews/2026-10-24-r1-subst-code.md`, lane/substland), the coordinator skill on a 16.8k-line diff.
1. **A sabotage row can score DETECTED because its plant fails to compile** (CHK-1): with -Werror on emitted code, a plant that leaves a parameter unused scores a catch at "driver build" with no cell run. A check-adequacy lens compiles each emitted-text plant on a real artifact; the matrix asserts the plant compiles.
2. **Encoding-neutral decided from source text, not from what it denotes** (TPL-1): an all-ASCII template with `\xe9` is not neutral. A contract lens probes every escape that produces a byte.
3. **A spec sentence that pins an upstream version's behaviour can be overtaken by a later ruling** (EMIT-5 vs the D26 addendum, same day): a round checks version-pinning sentences against the current D-rows.

Round 2026-10-24, kit S3 final (memfn-s3-final):
- (2026-10-24, memfn-s3-final) **A change to the DEFAULT search gets a find-all, real-text instruction sweep per new find form.** The emitted lens runs find-all over one real text and one adversarial text per new form, BASE vs SUBJECT, by instruction count. Both large losses (a quadratic two-stream find-all, a set stop walked where BASE ran memchr) were invisible to the stated timing bar, whose sample held neither shape.
- (2026-10-24) **A new stamp VALUE or a new pre-empting row is a D94-style reader hunt.** Grep every enumeration of the stamp's values and every witness sentence for the rows it now pre-empts. Six stale spec passages came from this.
- (2026-10-24) **Critics are launched unnamed, and their results travel only as files.** A coordinator's spawns could not be named, and all six final replies were lost; the files carried everything.

Round 2026-10-27 r1, [INLINE-C] stage 2 code (`docs/dev/reviews/2026-10-27-r1-ic2-code.md`, lane/ic2).
1. **A rule that protects what a human reads is generated from the standard's property, and the lens probes the property's members** (F1, F2): a hand-typed bidi/invisible list let U+3164 make a failing-looking check pass.
2. **A keep-list by PREFIX is a control sharing its source** (F3): emitter and check both meant "public" by `<PREFIX>_`; the check's public set comes from what the caller sees (the `.h`).
3. **A comment claiming "X asserts it" is a finding target** (F5): grep for the assertion; a gate depended on one that did not exist.
4. **A card row proves it reaches the site** (F19): a prefilter rejected the whole subject before the matcher ran.

Round 2026-10-29 r1, landwalk (design) (`docs/dev/reviews/2026-10-29-r1-landwalk.md`, P1's landmark walk), rev 1 in `docs/dev/lanes/p1dsg2_report.md`.
1. **A rule stated over STATES is checked on a machine with by-class accepts.** A by-class accept and the step that continues read the same byte, so they can exclude each other; a state-level reachability rule cannot see that. Read the emitted tables of the design's own witness (PREMISE-1: the rule rejected dup-param, its headline witness).
2. **A design's sufficient syntactic forms are a second statement of its rule, and they drift.** The census counted the forms, so it measured neither the rule nor the truth (A1). A simulate lens tests the forms and the rule separately.
3. **A row that hands a NEW hand is a table walk, not a sentence.** For every hand the row produces, walk the take cells on each route and the path-closure branch it follows; the first LOCATE row to hand AT found a run-time self-cycle the static closure (each cell visited once) cannot see (A2).
4. **A speed price needs the baseline of the SELECTED path, not of the motivating case.** The motivating pattern was the only admitted row whose shipped path walked every byte; the others already started from the landmark (S2).
5. **Compile-time admission cannot pass a subject-dependent acceptance cell.** Where one pattern sits in a positive and a negative cell, the design states the loss as a bounded non-goal instead (S3).

Round 2026-10-29 r5, landwalk2 (design re-check) (`docs/dev/reviews/2026-10-29-r5-landwalk2.md`, P1 rev 1), rev 2 in `docs/dev/lanes/p1dsg3_report.md`.
1. **A fix that turns a restated predicate into a READ of another slot traces the read's cycle and its fixed points.** A row whose own selection changes the read slot's inputs makes a counterfactual read, and the fix must name it (SLOT-1: the live read had two self-consistent answers on four bench rows).
2. **"Unchanged in kind" claims about a self-check are checked by evaluating the check's condition, not its name** (SLOT-2: the inclusion cited as the PASS reason was the failure condition).
3. **A route conjunct is the FINISHER, not the body shape.** A VM hybrid's prefilter body is CR_DFA (SLOT-4; cover's C1 had already learned it).
4. **A soundness lens needs a control that can fail for every rule it calls sound** (SOUND's three controls are what make its 0-wrong count mean something).

Round 2026-10-29 r3, vmtrail (design) (`docs/dev/reviews/2026-10-29-r3-vmtrail.md`; three designs, one build sequence, consolidated in `docs/dev/lanes/vmcons_report.md`).
1. **An "answer-identical by proof" design gets a soundness lens that APPLIES the rule to emitted code.** The lens builds the base tree and hand-applies the rule, as written, to the emitter's real output for crafted witnesses. It produced every answer-level repro of the round (F1-F3, F6, F8); reading the proofs alone accepted them.
2. **Multi-document subjects: review the SEAMS.** Each document was sound against the stock program; the holes were in the composition (F4, F5, F21). Every critic tags each finding doc or seam.
3. **"Read from the event stream" is a premise to grep, not a given.** Three designs rested on a stream with no slot reads, no SET sources, missing conditional edges and a cut logged as a note. A premise lens checks every claimed input of an analysis against the producer's struct and its call sites.
4. **A cited control can stop reaching its site between design and build** (F14: R25 E5's witness now routes to revdet or the DFA). Every witness a design names gets a reach probe at the base commit.

Rounds 2026-10-31 r1-r5, pricing-split and the pricing bake-off (`docs/dev/reviews/2026-10-31-r1-pricing-split.md` .. `r5-bakeoff3.md`).
1. **Coordinator notes live where critics cannot read them.** Keep them in a `.coord/` subdirectory of the round dir that COMMON denies; a critic read the coordinator's planted-check note when process.md sat in the shared dir (r1).
2. **Drill any verdict table on CONSTRUCTED outcomes, the design's own prediction first.** The predicted tie read INCONCLUSIVE/UNRESOLVABLE (r3, SIM-5/6/7).
3. **Implement the rule from the design TEXT before reading the design's own drill script, then diff.** Nine text/script divergences, three scenarios on target only through them (r4).
4. **Check where every evidence script writes before briefing.** A design's own `--plants` mode wrote into a denied lane dir and lanewatch's default log sits in the main tree; redirect via `PCREC_TMPDIR` and `LANEWATCH_LOG` (r5).

Round 2026-11-01 r1, stream1 design (`docs/dev/reviews/2026-11-01-r1-stream1.md`), five lenses; lessons ruled 2026-11-01.
1. **A synthesis of earlier drafts is re-graded when the owner's criteria change between rounds.** The round checks the subject against the criteria in force at the FREEZE, not at writing; a subject that predates them is a DOC finding first.
2. **A merge of independently written rule tables drops conjuncts.** A synthesis that merges rule tables keeps each source row's FULL conjunct list beside the merged row, and the soundness lens diffs them.
3. **"Today's design cannot X" claims need a witness compile,** like answer claims; five premise findings were the subject claiming a benefit today's tree already has.
4. **For an F4/no-blindness question, inventory today's BACKWARD channels first** (start from `CandRow`/`CandNode`, not the subject's table).

Round 2026-11-03 r5, memfn-sp1g code (`docs/dev/reviews/2026-11-03-r5-memfn-sp1g.md`), three lenses + verifier; lessons ruled 2026-11-03.
1. **A "kit never reads X" invariance check picks its witness sites from where the kit READS the containing object, with a reach control** (the varied render differs from the absent-object render on at least one site), plus a static "kit source names no X" scan beside it. (L(4b) varied the digest on two sites that never consult the object; three real readers stayed green.)
2. **A seam-shape check is an ALLOWLIST of members on every struct of the seam,** never a denylist of retired names (provenance re-entered under a new name and on the parent struct, all green).
3. **When a deletion removes the last record column read from the built object, move one surviving column to read the object,** or the builder's remaining writes lose their only witness.
4. **A design reader list built from a grep pattern misses bare vocabulary words:** add each enumerator's bare spelling (`PRIOR_NONE` without `MF_PROV_`) and sweep design docs beyond the named sections.

Round 2026-11-04 r1, memfn-sp1b code (`docs/dev/reviews/2026-11-04-r1-memfn-sp1b.md`), four lenses + verifier; lessons ruled 2026-11-04.
1. **A code round that moves or deletes kit or src text runs the anchor checker once** (`python3 -I scripts/m6read_check_sab_anchors.py`, read-only, seconds) in the check lens. A plant can quote a function's BODY rather than its name (S1094), so a grep of the deleted names misses it.
2. **The COMMON brief of a rate-sensitive subject names how to reach each rate regime:** default (the prior), NONE (`-e utf8`), all-tie (`--analysis uniform`), and a real bundle (`-I DIR --analysis NAME`, with DIR/NAME.rxt). One critic spent 220 compiles on a misread bundle lookup.

Round 2026-11-04 r2, memfn-sp1c code (`docs/dev/reviews/2026-11-04-r2-memfn-sp1c.md`), coordinator round + verifier; lessons ruled 2026-11-04.
1. **A "MOVED" from a plant compare checks the plant's exit code first, and deletes old outputs before each compare.** Classify every compare as SAME, SILENT-MOVE (rc 0, bytes differ) or LOUD (rc != 0). A LOUD plant is caught by every corpus compile and is not a test gap; two compare scripts reported failed compiles as silent moves.
2. **Plain `grep -r` ignores git pathspecs:** a denied file inside a directory a critic greps recursively leaks. COMMON gives `--exclude=` per denied file for plain grep, or `git grep` with the pathspecs.

Round 2026-11-05 r1, memfn-sp1d code (`docs/dev/reviews/2026-11-05-r1-memfn-sp1d.md`), coordinator round + verifier; lessons ruled 2026-11-05.
1. **Check every rate-regime spelling in COMMON against the build before briefing.** `--analysis uniform` is refused; the working spelling is `-I tests/findings/adversarial --analysis=uniform`.
2. **A census backstop's shape must be one a BYPASS has to use, and its plant must not contain the conforming call's text** (F2: every plant contained `pick_takes(`, the backstop's own shape).
3. **An invariance harness needs a per-row REACH table, not one plant** (F1: four shipped rows were unreached and uncounted).
4. **A trace record added for a seam gets a sufficiency drill: two inputs with equal records must have equal picks** (F4: three constructed pairs broke it).

Round 2026-11-05 r2, alt-normal-form design (`docs/dev/reviews/2026-11-05-r2-alt-normal-form.md`), coordinator round + verifier; lessons ruled 2026-11-05.
1. **A proposed sabotage witness must be able to fail.** Compute whether its fact clears every floor and domain test in both the correct and the sabotaged build (S-c out of domain, S-f under the 16-bit floor, S-d named none).
2. **A fixpoint rewrite called a "normal form" gets a confluence drill** over every merge order (SIM-2: 23% of small grids ended in different forms; `\p{Lu}` 76 vs 66 boxes).
3. **"Not an abi event" is checked against match_api.md §6¶19 and the abi log's precedents** (two lenses reversed this round's claim independently).

- **2026-11-05 r3 vlookbehind.** (1) A simulate lens that implements a rule's INTENT validates its semantics, not its sketch: hand-execute shipped pseudo-code literally (now in the soundness row). (2) A byte-identity claim by "constant fold" is checked statement by statement against the emitted prologue: order, saved operands, charge amounts, slot allocation ("evaluates the test at compile time" hid four other differences).
Round 2026-11-05 r2, memfn-sp1e code (`docs/dev/reviews/2026-11-05-r2-memfn-sp1e.md`), coordinator round + verifier; lessons ruled 2026-11-05.
1. **When a row moves between tables, compare the gate INPUT each walk hands `gate_check`, not only the row's predicate and contract.** Plant the contract's opposite and require a refusal. F1: a clause became unable to refuse in a byte-identical move.
2. **For a declared map or list read by a check, plant a DELETED line and an INVENTED line; both must go red** (F3: both were green).
3. **For a key the subject declares, every member must be printed in the trace record**: a member missing from the record is where a bypass plant hides (F4).
4. **For a zero-mover unit, spend part of the emitted lens reading the equivalence argument rather than probing**: F1 came from reading.

Round 2026-11-06 r4, memfn-span-cards design (`docs/dev/reviews/2026-11-06-r4-memfn-span-cards.md`), coordinator round + verifier; lessons ruled 2026-11-06.
1. **Re-diff the frozen rulings at each critic return.** A ruling homed in the subject that lands mid-round gets a fresh critic on its section (D188 was seen only at hand-back).
2. **Drill a named measurement estimator like a selection rule**, on constructed outcomes (clean, outlier, bimodal, A/A above spread, equal-effect sweep): these drills found every gate defect of the round.

Round 2026-11-06 r5, memfn-span-cards re-check (`docs/dev/reviews/2026-11-06-r5-memfn-span-cards-recheck.md`); lessons ruled 2026-11-06.
1. **Locate each in-force ruling's record at the freeze**; a ruling with no record is a freeze note (DEFAULTS (B) existed only as a message).
2. **Two fixes touching one check or directory: recompute the check's population** (CHECKC: each fix held alone, together they left zero keys).
3. **"Built objects differ" is vacuous across differently named sources** (STT_FILE carries the file name); assert on linked addresses or `.text`.

Round 2026-11-06 r6, memfn-span-cards re-check 2 (`docs/dev/reviews/2026-11-06-r6-memfn-span-cards-recheck2.md`); lesson ruled 2026-11-06.
1. **Readiness runs the loader over every new data-row shape the design writes, and lists every embed-vs-source check** (READY-1: a measured row naming an arm in `inputs` is refused today; READY-3: a cell-less embed reds three STORE checks).

Round 2026-11-06 r8, memfn-s2a code (`docs/dev/reviews/2026-11-06-r8-memfn-s2a.md`); lesson ruled 2026-11-06.
1. **A witness record over a struct is planted field by field**: SEAM-1's noise digest covered the noise but not the value beside it, so a value+1 fill passed every check.

Round 2026-11-07 r1, xarch target seam design (`docs/dev/reviews/2026-11-07-r1-xarch.md`); lessons ruled 2026-11-07.
1. **A critic brief is ONE question with at most two sub-parts and requires a per-finding append; a critic still silent 20 min after its one resend is replaced by a narrower fresh critic** (two wide briefs wrote nothing in 45 min; their narrow replacements delivered in 7-9 min).
2. **Soundness compiles every emitted-shape claim at default flags, at `-march=native` and under the second supported compiler** (PROBE-1/PROBE-2: the only build failures of the round appeared under `-march=native` and clang).
Round 2026-11-06 r9, memfn-s2c code (`docs/dev/reviews/2026-11-06-r9-memfn-s2c.md`); lesson ruled 2026-11-06.
1. **A harness is reviewed for fidelity**: the answer gate ran the gate entry, not the timed one; a cell-text check read the arm, not the key; the verdict ignored the run record; a dep hashed a different instance from the one timed. Every check was green. New lens row "harness fidelity".

Round 2026-11-07 r12, memfn-planframe1 design (`docs/dev/reviews/2026-11-07-r12-memfn-planframe1.md`); lessons ruled 2026-11-07.
1. **A design that SPLITS a row table lists every per-row branch in the consuming function** (`if (w->bren == B_PAIR)`), not only the table's columns: three critics found the same uncolumned piece (F2), and the floor's different skeleton (F3).
2. **A design that re-labels what an accessor returns greps the accessor's readers** (F1, found independently by three critics, would have turned the correct build red).
3. **A ruling held only in a denied ledger is quoted verbatim in COMMON**, with a ready plain-grep exclude string (a plain grep leaked one denied journal line).

Round 2026-11-17 r43, predspec25 design re-check (`docs/dev/reviews/2026-11-17-r43-predspec25.md`); lessons ruled 2026-11-18.
1. **An evidence engine's PARSER predicates are readings too.** The engine's `starts_operand` excluded the sequence mark, a clause the draft had dropped; the evidence passed because the code restored what the text lost. Simulate lens: diff the evidence's tokenizer/parser predicates against the subject's parse-rule sentences; a predicate with no sentence is a finding.
2. **A record's RESTATEMENT of an agreed question can narrow it.** "The right side of `&`" existed only in the manager's record; the agreed question and the locked rule say an `&` operand. Ruling lens: diff each record restatement against the question the owner agreed to, list by list.
3. **Fold marks show where a lane looked.** Eight or more unmarked readers of withdrawn or changed rules were found by grepping the withdrawn rule's TERMS over the whole subject, not by the marked list. Fix-induced lens: that grep is a standing step for a re-check that withdraws rules.


Round 2026-11-18 r47, predspec26 design re-check (`docs/dev/reviews/2026-11-18-r47-predspec26.md`); lessons ruled 2026-11-18.
1. **A claim proved on ONE witness whose first item is already the special case cannot tell the claim from its rivals.** H5's `a1b` has an empty first hit; the nullable argument's meaning was false under the loop rewrite. Drill the special case in SECOND place, and at `min >= 2` (A1, three lenses).
2. **A place/position table cell about a fact written INSIDE a nested place must say where it is written.** Drill each row's `0` / label / reference cell with the row nested inside the `&`, loop and hole rows (A2, A5).
3. **For every CHECK the subject cites as "supported", mutate one arm.** If no mutation of the cited arm can move the count, the check shares its source (N3, CS3).
4. **A 0/0/0 at a short pool length is not evidence when the witness needs a longer text.** A4 needed length 7, A5 needed `min = 1`: critics state the minimum witness length they reached.

2026-11-22 r78, kit code round memfn-bsu4 (`docs/dev/reviews/2026-11-22-r78-memfn-bsu4.md`), accepted 2026-11-22 (kit manager):
1. **A harness's floors count what was DRIVEN, not only what was GENERATED.** That means per-placement runs, per-layer runs, and a self-witness for each guard page (one deliberate over-read that must fault). In r78, four mutations disabled half the promised regime and passed green while every generation floor held (G2V-1).
2. **A sabotage row cited as a guard-page witness must be benign without the guard.** Otherwise it witnesses the answer leg. When it is not benign, say so in its header and prove the guard by the harness's self-witness (PLANTSB-2).
3. **A check that holds an ORDER over a table pins every row ahead of the moved one,** not only the rows the design names. In r78, T-deny ahead of V was held by test-axes only (PLANTSA-2).
- (2026-11-22, r81 k159fix) **A stop or early-exit fix needs a BOUNDED witness beside its cost witness.** A CPU guard on an unbounded witness cannot tell a correct stop from an over-eager one (plant V1, a subset test in place of equality, moved 8 of 11 bounded widths and none of the existing table's rows).

2026-11-22 r79, kit code round memfn-bsu5 (`docs/dev/reviews/2026-11-22-r79-memfn-bsu5.md`), accepted 2026-11-22 (kit manager):
1. **A form-hash dep must cover every rendering the card times.** Enumerate the canonical instance's renderer branches against the card's cells, and plant one per branch (F1: the hash covered B = 32 only).
2. **An A/A arm is a control only if it shares the comparison's axes,** and the rule says what a failed A/A does (F2: H64.b shared H64's layout pool).
3. **"Written before data" includes the verdict clause and the unit.** Drill an all-unreadable run (F5, F6).
