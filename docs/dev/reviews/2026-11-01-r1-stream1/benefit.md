# BENEFIT lens, crit-stream1 (opus)

Subject: approach_synth.md (frozen copy). Review tree: worktrees/crit-stream1 @ f574eab2d.
Judged ONLY on the owner's F1-F4 (focus, flexibility, division of labour, no blindness);
speed only as must-not-regress. No compiles were needed; all evidence is grep / git log
subject lines / file:line in the review tree. Scratch counts: benefit/mergestat.txt, log.txt.

## Findings

### BENEFIT-1. The benefit case is never re-argued on F1-F4. CONFIRMED. Severity doc/design. Effort small (one section). Blast radius: the GO/NO-GO itself. Hits §4, §5, §8.
- Evidence: `grep -n -i -E "focus|backend|front ?end|division|blind|owner"` over approach_synth.md returns
  ZERO hits for any of them; §4's headings are 4.1 Reach, 4.2 Speed, 4.3 Simplicity,
  4.4 New capability, 4.5 Not benefits. Its grades (STRONG/MEDIUM/WEAK) are speed/reach grades.
  The owner's criteria (owner_framing_and_criteria.md, last section) explicitly SUPERSEDE speed
  as the case and arrived after round 1, so the subject, a synthesis of round-1 drafts, is
  graded against the old question.
- What an F1-F4 case would have to show: (F1) the part list, each part's contract and its own
  test boundary, and that a typical recent feature would touch one part; (F2) one new backend
  and one new front end walked through, naming the parts that change; (F3) per part, an oracle
  its owner can run WITHOUT the other parts; (F4) per seam, which facts travel each way.
- Per-criterion verdicts (argued in BENEFIT-3..7): F1 PARTLY; F2 backend PARTLY, front end
  ASSERTED-ONLY (in fact never asserted) and CONTRADICTED for a different match semantics;
  F3 PARTLY (kit DELIVERED, planner/renderers ASSERTED-ONLY); F4 PARTLY (forward facts yes,
  backward none).

### BENEFIT-2. (A, pro-end-state) Two engines cost F1/F3 forever, and the tree measures it. CONFIRMED. Severity design (supports the subject; it should cite this). Effort trivial. Hits §4.3, §5.
- Co-touch: of the 115 code-bearing first-parent merges on main since 2026-09-01
  (`git log --merges --first-parent --since=2026-09-01`, 400 merges, 115 touching src/cli/lib),
  **39 (34%) touched BOTH `src/gen/emit_dfa.c` and `src/gen/emit_vm.c`**, 44 touched one, so 72%
  of feature merges entered the emitter pair. Median feature merge: 7 src files, 39 files total
  (p90: 17 src, 108 total; max 47 src: lane/ic1b). Over all 1,390 non-merge commits since
  2026-09-01, 94 touched both emitters. Examples of both-emitter merges by subject: [INLINE-C]
  ic1b/ic2fix, iterators _next (iterland), [DD-11.5] ctxbuild, [ENTRY-TABLE] e1, [OPT-REVEND] b3tri,
  [OPT-LITSCAN] c3build. That is F1's "a change means scanning too much" in numbers.
- Unit of focus: the two emitters are 16,008 + 14,201 = 30,209 lines, about 31% of
  src/*/*.c + cli + lib (96,159 lines); each alone is larger than the next nine src files combined
  except compile.c (3,722) and possessify.c (2,203).
- Parallel plan rows (plan.md): [ENG-COUNT] l.515 "THE VM SIDE ALREADY HAS THE LOOP FORM"
  (the same capability, two forms per engine); [START-DENSE] l.647 "the retry slot's adaptive rule
  carried to the VM-only and DFA-hat routes" (a port row); l.556 cross-note "build it as an
  island shape shared by both engines, not as a DFA-only edge kind"; l.933 "V1 waits for this row on
  both engines, the VM version ... included"; l.775-777 a per-form refinement "hybrid, then
  VM-only" that breaks the fit table's once-per-row bound. Note: the subject's §4.3 phrase
  "'port this to the other engine' plan rows" is uncounted and the literal phrase occurs 0 times;
  the explicit port rows are few (~5), the real cost is in the merges, not in plan rows. Say so.
- Division-of-labour leak, forever: the engine taxonomy is in the KIT's public header,
  `memfn/include/memfn.h:414-415` (`MF_SK_DFA_SCAN, MF_SK_DFA_HAT, MF_SK_HYB_PF,
  MF_SK_VM_ATTEMPT, MF_SK_DFA_ATTEMPT`), selected by `emit_dfa.c:1415-1425` site_kinds[]. The one
  part that WAS split off (memfn, the owner's own example of a worthwhile split) must know pcrec's
  two-engine/hybrid structure to do its job. Grown-today keeps this as long as there are engines;
  the stream deletes it (X14). This is the strongest F3 argument for the end state and the subject
  lists it only as a simplicity row.
- What today can NEVER do on F1-F4: make a capability exist once (the engine is a per-pattern
  partition, so every stretch-level capability has a home per engine or a glue site X1-X14); keep
  engine context out of the kit's interface.

### BENEFIT-3. F1: the parts are implied, not defined; the planner becomes the new unit of focus. CONFIRMED (from the subject's own text). Severity design. Effort medium (a part table + test boundaries). Blast radius: every future change. Hits §2 "Who segments", §4.3.
- Implied parts: (P1) parse + IR + opt passes (unchanged); (P2) the planner with the ONE admission
  table §3; (P3) the kind table + one renderer per kind (§2: "each kind one row of one kind table
  with one renderer"); (P4) the kit (facts in); (P5) the controller ABOVE the stream (compound,
  arch variants). The seam contract (§2) is defined for RUNTIME seams between stretches; no
  contract is defined for the COMPILE-TIME seams P2->P3 (what makes a stream well-formed and
  renderable) or P3->P4 beyond today's mf_site.
- The subject concedes the decisions move, not shrink: §4.3 "The DECISIONS do not vanish; they move
  into the planner's table (C). `emit_dfa.c`'s 16k lines are mostly decisions and reasons (T)."
  So P2 absorbs select_engine.c (1,485 lines), the decision halves of both emitters, the
  cand_rows[] / LOCATE-RECOVER-FINISH rows, compound's split rows and lmwalk's admission table.
  "One admission table" is good for F4 (one place sees everything) and bad for F1/F3 unless the
  table is itself partitioned. The design HAS the mechanism (the `exact` seam field: "the
  admission row that made this seam sound, so one deny axis per row can test it") but never states
  "a row is a part: its argument, its deny axis, its D27 spec-first tests, its owner".
- Changes that still cross parts: a new instruction kind (open choices A/B: TAGGED, GUIDED, THREADS,
  MEMO) = kind row + renderer (P3) + admission row (P2) + possibly a new `pos` type (seam contract)
  + kit (P4); a new kit operation = P2 + P3 + P4. Those are contract changes and may be rare; the
  design should say they are the ONLY cross-part changes, and that a new admission row over
  existing kinds touches P2 alone.
- Verdict F1: PARTLY. Delivered for "a capability exists once" (kind table); asserted-only for
  "a change touches one part" until the planner is split into per-row parts with per-row tests.

### BENEFIT-4. F2 backend: the stream inherits D182's record LEVEL, which is C-spelling, not target-neutral. CONFIRMED. Severity design. Effort medium. Hits §2 ("built and rendered the D182 way"), §5 loss 6.
- The subject widens D182 to the whole artifact. Today's D182 records (`src/gen/vm_stmt.h`) carry C
  spelling: `VmGuardSpell` VG_BRACED / VG_INLINE / VG_INLINE_BRACED (l.100-104), a value fragment
  whose VP_TEXT piece is free C text (l.70-83; `emit_vm.c` builds 22 text fragments via
  `pcrec_vm_frag_text`/`_of`, against 92 builder calls), locals named by their C variable
  (`VmLocal`, `<p>_rv<loop>_cursor`, `revdet_group_span[j][half]`), and kinds documented by their
  rendered C (`VK_PUSH /* <P>_PUSH([n, ]&&<p>_L<n>, POS); */`, a computed-goto label address). The
  kit's contract is C text (`memfn/CLAUDE.md:3`: "the kit returns the C text for it"). Loss 6
  states the stream's render vocabulary must hold computed-goto DFA states in one function.
- Walk a new backend (a JIT, a non-GNU C without computed goto, WASM): with the §2 SEMANTIC kinds
  (CHOICE, AUTO(M,dir,exit), SKIP(set,dir,stride), SET ...) only P3's renderers and P4's emission
  target change: about 21 kinds, an enumerated job, a genuine F2 win over two 15k-line emitters.
  With D182's CURRENT level, every TEXT fragment and spelling enum is C and the backend rewrites the
  planner's output too. The subject never says which level the stream's records sit at.
- Verdict F2 backend: PARTLY. Needed: a target-neutrality rule ("no record carries target text;
  spelling is a renderer choice") and its test (BENEFIT-6's interpreter is that test).

### BENEFIT-5. F2 front end: the stream adds nothing for a dialect, and its soundness rule is defined BY backtracking. CONFIRMED (subject text). Severity design. Effort small to state, large to generalise. Hits §3.
- A dialect that lowers to today's IR (P1) gains from the IR seam, which exists today; the stream
  gets no credit there.
- A front end with DIFFERENT semantics: §3's setting is "Backtracking yields S's outcomes
  (e1,s1),(e2,s2)... in preference order"; row B "IT IS the semantics"; rows 3, 8, 9 are
  preference-order arguments. A POSIX leftmost-longest dialect makes every row's argument and the
  floor wrong. A set-of-patterns API (Hyperscan-style, N patterns with ids): §2 puts whole-artifact
  composition in a controller ABOVE the stream and FIND "at the bottom of the one choice stack",
  one per stream, so a shared FIND over N streams (the main thing such an API buys) has no place.
- Verdict F2 front end: ASSERTED-ONLY (in truth unaddressed); CONTRADICTED for a new semantics as
  written. The general form: make the reference semantics a named parameter of the table (row B =
  the dialect's reference machine; each row's argument stated against it), and let FIND be a
  stream instruction that can feed several ACCEPT ids. Trigger: a second semantics or a set API
  requested; not before (D77).

### BENEFIT-6. F3: no part except the kit has an oracle its owner can run alone. CONFIRMED (subject text). Severity design. Effort medium. Hits §5 loss 1, §8.
- Kit (P4): DELIVERED today (own G2 tests, memfn/CLAUDE.md:31) and IMPROVED by the stream (engine
  kinds deleted, BENEFIT-2).
- Planner (P2): its only stated checks are answer identity over the corpus (needs P3 + gcc), the
  dry run M8 (prints a tiling, judges nothing) and a deny axis per row (end to end). A planner
  owner cannot validate a change without the renderer owner's code: the control shares a source
  with what it controls (learnings §3), which is loss 1 restated at the part level.
- Renderers (P3): byte identity vs today during migration only; after migration no per-kind oracle.
- What would deliver F3: a STREAM INTERPRETER (executes records in-process, no C, no gcc). It is
  loss 1's own mitigation ("ONE reference tiling whose renderers are separate code"), and it gives
  (a) the planner owner an oracle: interpret the planned stream vs the all-B tiling of the same
  pattern; (b) the renderer owner a per-kind oracle: seam-in -> rendered C -> seam-out vs the
  interpreter on the same seam-in; (c) the F2 target-neutrality test of BENEFIT-4. Not in the design.
- Verdict F3: PARTLY (kit DELIVERED; planner and renderers ASSERTED-ONLY).

### BENEFIT-7. F4: every seam field flows producer->consumer; the round's own F4 example is ceded. CONFIRMED (subject text + lane/p1build plan). Severity design. Effort small (one field + rule). Hits §2 seam contract, §4.5.
- §2's seam fields pos, slots, proof, reentry, effects, exact, meters: all describe what the
  producer hands forward. None carries what the CONSUMER will test anyway or at what cost.
- [LANDWALK-PRES] (lane/p1build docs/dev/plan.md): PRESENCE declines its required-run
  pre-check as `dominated` by the walk, blind to the pre-check's run being rarer than the landmark
  (`[a-z]+@x` on acc-small: 556K vs 425K instructions, x0.77). In the stream, PRESENT and FIND are
  separate kit instructions chosen by first-match rows per stretch, and "price chooses only among
  rows that ADMIT" per stretch: the same local, blind choice, unless the planner is global.
- §4.5 files "seam proof reuse past the cut (T B7): already pursued ... as [CAND-SPAN]" under NOT
  benefits. [CAND-SPAN] (plan.md) is exactly a fact shared both ways by three sites
  (pre-check, walk hit, literal search). On F4 that IS the criterion, and the stream's typed seam
  is its natural home; the subject gave the F4 case away by grading it on speed.
- Tension the design must face: F4 by a central planner that sees everything works against F1/F3;
  F4 by seam fields that travel BOTH ways keeps parts small. Fix: a `demand` field (the consumer's
  declared checks + per-hit cost) that the producer's row reads; witness and trigger:
  the [CAND-SPAN] design lane (filed 2026-11-01).
- Verdict F4: PARTLY.

### BENEFIT-8. The design's implied goal order is soundness > byte identity > speed > reach > simplicity; no proof shows an F1-F3 property. CONFIRMED. Severity design. Effort small. Hits §4 order, §7, §8.
- §4's order and grades, §7 (M1-M6 sizing speed/reach populations, T1-T3 timing) and §8 (P-a..P-e
  byte-identical, then P-f and P-g, BOTH speed benefits) rank speed as the first benefit. The owner
  ranks F1-F4 first, speed as no-regress. Only M0/M7 (count sites, builders, deny axes deleted) are
  F1 proxies; keep them and say so.
- A proof that serves F1/F3: P-a's one `SKIP(set,dir,stride)` record shipped WITH its own per-kind
  test that runs without the emitters (seam-in, seam-out), and P-e (M8) promoted from a dry run to the
  planner's own oracle once an interpreter exists. Speed proofs then show no regression.
- Does it serve its own order? Yes for soundness and byte identity (well ordered); no for the owner's.

### BENEFIT-9. Standing question: it IS the general form of X1-X14; unlocks with triggers. CONFIRMED (§4.3 mapping covers all 14). Severity design (positive). Hits §2, §4.3.
- §4.3's table maps every one of X1-X14 to a kind (AUTO, SKIP, FIND, PRESENT, VERIFY, MISMATCH) or
  to the controller above; nothing is left as a residual special case. That is the general form.
- Unlocks (each with its trigger): (u1) the stream interpreter = reference tiling + per-part oracle
  + backend-neutrality test (trigger: loss 1's mitigation is chosen, or the first non-gcc target is
  requested); (u2) per-row ownership of the admission table, each row = argument + deny axis + D27
  tests (trigger: the second admission-row author working at the same time as the first); (u3) a
  two-way seam `demand` field (trigger: the [CAND-SPAN] design lane, now); (u4) a semantics-parameterised
  floor and a multi-ACCEPT FIND (trigger: a second dialect or a set-of-patterns API); (u5) D182
  stage (c) designed on the stream's record set (subject's timing note, trigger: stage (c) design,
  now) is also the cheapest moment to fix BENEFIT-4's record level.

## PROBED-AND-HELD
- X14 (draft_today.md): `emit_dfa.c:1415-1425` site_kinds[] holds at f574eab2d, five MF_SK_* rows; and
  the enum is public kit ABI at `memfn/include/memfn.h:414-415` (stronger than the draft says).
- coding.md §2.7 (l.240) states the D182 record rule as the subject cites; D182 at decisions.md:9994.
- [CAND-SPAN] at plan.md and commit c967685c9 exist as §4.5 cites.
- [LANDWALK-PRES] exists on lane/p1build plan.md with the measured x0.77 (F4's worked example).
- The subject's §4.3 X1-X14 table: 14 of 14 sites mapped; none left without a stream home (HELD,
  the general-form claim).
- Emitter sizes: emit_dfa.c 16,008 and emit_vm.c 14,201 lines (subject: "16k lines", HELD).
- Co-touch counts: 400 first-parent merges since 2026-09-01 scanned, 115 with code, 39 both emitters.
- Plan rows read by tag only: [ENG-COUNT], [START-DENSE], [CAND-SPAN]; plus grep lines 556, 775-777,
  933 (no neighbour rows printed).

## Summary
- The subject argues speed/reach/simplicity; it never re-argues on F1-F4 (0 hits for focus/backend/front end/division/blind).
- Pro-end-state evidence it omits: 34% of feature merges since Sept touched BOTH emitters; the engine taxonomy sits in the kit's public header.
- F1 PARTLY: decisions move into one planner table; per-row parts and tests are implied, not stated.
- F2 PARTLY (backend: D182 records are C-spelling) / front end unaddressed, contradicted for new semantics; F3 PARTLY (kit only); F4 PARTLY (seam is one-way, CAND-SPAN ceded).
- General form: yes; key unlock is a stream interpreter (loss 1's mitigation) giving every part its own oracle.
