# crit-arev, lens OWNER-CRITERIA (opus), subject arev.md rev 0 + roadmap.md A-REV, frozen at dd89fa9bb

Read: R/subject_arev.md, R/subject_roadmap.md (A-REV row, ### A-REV, A-VERDICT, H-FLAGS, §5 R03/R10, §6),
manifesto.md, vlookbehind.md rev 1 at f15f30f25 (§0, §3, §4, §5.4, §5.6, §6, §13), plan rows [STREAM]
[VLOOKBEHIND] [LB-EXIST] [GIVEUP-DIFF] [REVBLOCK-VIEW] [VMREC] [LANDWALK-VM] [LANDWALK-ALLACC] and D77/D153/D185/D186
at f15f30f25; review tree worktrees/crit-arev (emit_dfa.c `struct DfaDir`, `dfa_dir_reverse`; `build/pcrec --help`).

## Findings

### OWNER-1 — the operand record carries C text: an F2 failure written into the end state
CONFIRMED. Severity design. Effort S (text: restate three operands as facts). Blast radius: S1, S3, every
future back end (F2). arev §2.1, §3.3 (a).
- The manifesto (§2): "A record says WHAT happens ..., never how it is spelled in C." F2's failure form:
  "a record still carries target text after the first target has paid for removing it." Principle 9: no
  assumptions about the other side's language cross a seam.
- arev §2.1's `RevWalk` keeps C text as operands: `seed` = "the position expression ... (`DfaDir.seed_cond`/
  `seed_byte` today)"; `dead` = "`continue;`" for W2, "NULL" for W1; `names` = "state, position and result
  variable names, table names"; §3.3 (a): "its state variable, indentation and table comment become operands".
- The code confirms these are C fragments: worktrees/crit-arev/src/gen/emit_dfa.c:5787-5830 (`struct DfaDir`:
  `statev`, `posv`, `recv`, `ind`, `bind`, `seed_cond`, `seed_byte`, `at_bound`, `peek`, `consume`,
  `advance`, all `const char *`) and :9360-9374 (`dfa_dir_reverse` = `"rewind_position <= search_from"`,
  `"subject[--rewind_position]"`, `"        "`). S1 as written MOVES those strings from a frozen constant into the
  record; it does not remove target text, it relocates it into the seam document.
- Expected under the owner's order (F2 over F3, principle 9): `seed`/`floor` as typed position roles
  (forward-accept, n, n-1, hit+1, VM cursor; floor = search-from | subject-start | cursor-minus-W), `dead` as a
  hand type (NOMATCH, next-seed, fail), `names` as an instance id from which the C back end derives spellings.
  §2.3 reason 1 (the function boundary is the naming scope) already shows names need not be an operand.
- The §2.1 claim "The record is the seam document of principle 9" is therefore false as written.

### OWNER-2 — §0's goals are not the owner's goals: F1-F3 absent, F4 promoted to a goal, the gate promoted to goals
CONFIRMED (text). Severity design. Effort S (rewrite §0). Blast radius: every step's justification. arev §0.
- Manifesto §1 / D185: goals F1 > F2 > F3; F4 a CONSTRAINT; "no answer moves and nothing gets slower" a GATE,
  not a goal; "speed is not the case".
- arev §0 ranks G1 answers (the gate), G2 one mechanism (the ratchet, principle 3/6), G3 cross-engine pieces
  (the owner's 2026-11-05 payoff), G4 no blindness = F4 (ranked as a goal, below G3), G5 speed (the gate again).
  None of F1 FOCUS, F2 FLEXIBILITY, F3 DIVISION OF LABOUR is named, measured, or used to order a step.
- Consequences found by this lens: F2 fails unnoticed (OWNER-1); no per-part check for F3 (OWNER-3); the step
  order is derived from arev's own G2 > G3 rather than an owner ranking (OWNER-5).
- Checkable form the owner's criteria give (manifesto §5): F1 = a new reverse-walk client touches only the
  planner + declared append shapes (the record, the machine table); F2 = a second back end leaves `RevWalk`
  and the exit rows unchanged; F3 = the kind's renderer has an oracle it runs alone; F4 = a constraint each
  step must meet, with the backward facts (Nfa.erased, the realized machine, the overflow decline) listed.

### OWNER-3 — G4 is unmeasurable for three of four walks, and the kind has no per-part check (F3)
CONFIRMED. Severity design. Effort S-M. Blast radius: S1, S2, S4 acceptance. arev §0 G4, §3.2/§3.3 witnesses.
- G4's measurable: "every instance prints its operands in `--emit-ir` / the trace". `build/pcrec --help`
  (review tree): `--emit-ir` prints "the VM PROGRAM LISTING ... a DEBUG listing, VM-only"; `--trace` prints
  "every resume-frame push/pop and capture write". W1-W3 are inline walks in DFA artifacts: neither channel
  reaches them. G4 as written can pass only for W4 and L.
- F3's failure form is "a part's only check runs end to end through another part's code". Every witness in
  §3.1-§3.3 is a whole-matcher answer cell (S1825, S50-S52, WD1-WD7). Roadmap §0a names the per-seam check
  ("a plan in, the C out, golden-file tests: the owner's 'contract + tests per seam'"). arev names no
  record-in / text-out test for `RevWalk` or `VK_AUTO`, and no oracle the kind's owner runs alone; it
  should, or say it has none (manifesto §5 F3).

### OWNER-4 — the owner's worked example (reverse DFA, then a forward VM run for captures) is built by no non-HELD step
CONFIRMED (text). Severity design. Effort M (re-stage). Blast radius: S3, S5, G3, the client document. arev §0 G3,
§2.3 finisher contract, §3.1, §4.1 S3/S5; vlookbehind rev 1 §5.4.
- Owner, 2026-11-05: the payoff is "a reverse DFA inside a VM lookbehind, then a forward VM run for captures".
  arev G3's own measurable says "its result handed to a VM forward run".
- S3 builds `exist` (no VM run at all) and `gate` (the passed hand is a yes/no; §3.1 row 2's finisher is "the
  `range` row's loop, unchanged", which re-starts at the cursor's farthest length and ignores the DFA's
  accept position). The step that hands a DFA position to a forward VM run is row 3 `commit` = S5, HELD.
- So S3 delivers a cross-engine GATE, not the owner's example; G3 is marked met by a step that does not meet it.
- It also changes the client: vlookbehind rev 1 §5.4 (in force at the build commit) has ONE `reverse-dfa`
  row with exits "EXISTENCE" or "candidates farthest first, each confirmed by §5.1's step", and its evidence
  requirement (a)-(d) prices THAT row. arev's `gate` row does not exist in rev 1 and rev 1's candidate exit is
  arev's HELD S5. arev was written without rev 1 (COMMON note) and neither document reconciles this.
- Ask (plain words, for the owner): is the first cross-engine piece a gate in front of today's loop (cheapest,
  what S3 builds), or the DFA handing its start positions to the forward VM run (the example he gave)?

### OWNER-5 — "lookbehind first" re-read as "first in design"; the build order and two prerequisites disagree with vlookbehind rev 1
CONFIRMED (text). Severity design. Effort S (an owner question + a rev-1/arev reconciliation). Blast radius: the
A-REV step order. arev §4.1 closing paragraph; roadmap ### A-REV Steps; vlookbehind rev 1 §4 "Why not now", §5.4.
- arev §4.1: "The owner's order (lookbehind first) is the order of DESIGN ... S3 is the first step built for a
  client rather than a migration." Built order: S1, S2 (migrations, ride-alongs) before S3. That is a reading
  of an owner direction, asserted rather than asked; the ranking that justifies it (G2 one mechanism over G3
  cross-engine) is arev's own (OWNER-2).
- The two client documents disagree on where S3 sits: vlookbehind rev 1 §4 "Why not now" says building D
  "ahead of A-REV's P-d step would add a third hand-written reverse walk" and §5.4 lists [LANDWALK-VM] (G5)
  among D's prerequisites; arev puts S3 BEFORE S4 (= P-d, which waits on P-b, which waits on P-c) and lists
  neither P-d nor [LANDWALK-VM]. arev's argument (S3 is an instance via `VK_AUTO`, ratchet 0) may well be
  right and would make lookbehind genuinely buildable earlier than rev 1 says, but it supersedes rev 1's
  staging without saying so. One document must be revised, and the owner told which order holds.
- Buildability of "lookbehind first" (the S3 chain, at f15f30f25): S1 (not built, ride-along); vlookbehind
  stage 1 (rev 1 PROPOSED; [VLOOKBEHIND] next = a re-check round, then owner Q1 (re-asked) and Q2, then a build
  go); [GIVEUP-DIFF] (not started; trigger is a VM-finisher LOCATE row); the bench lifting
  `lookbehind-variable` (an inbox entry after stage 1); then the D77 trigger (OWNER-6). Lookbehind is the
  LAST client buildable under this plan, behind S1 and plausibly S2 and S4 as ride-alongs. The design should
  say so in plain words.

### OWNER-6 — the owner's named payoff waits on a speed trigger the client document predicts will not fire
CONFIRMED (text). Severity design. Effort S (an owner question). Blast radius: whether G3 is ever built. arev §4.2;
vlookbehind rev 1 §3 speed rows, §5.4.
- arev §4.2 makes S3's trigger a SPEED measurement (pcrec slower than libpcre2 on
  `negation-scope-lookbehind-var` with the lookbehind as cause, or a regime-(c) cell in a real workload).
- vlookbehind rev 1 §3: short bodies (every population row but the cap pin) "No expected win (INFERRED)"; the
  bench pattern "INFERRED small difference, since the lookbehind is evaluated only where `\bavailable\b` can
  follow". And the manifesto: "Speed is not the case for this work"; the stream's proofs (P-b..P-d) are
  ordered by the proof table, not by a speed trigger.
- So under this plan the owner's 2026-11-05 payoff has no reachable trigger: the D77 rule (build under measured
  need) and the owner's direction (cross-engine pieces are THE payoff, lookbehind first) pull opposite ways,
  and arev resolves it silently in D77's favour.
- That may be right (D77 is a standing rule), but it is the owner's call: either the cross-engine piece is a
  stream PROOF (scheduled like P-c/P-b, judged on F1-F4, speed only as the gate), or it waits for a speed
  number that may never come. arev should put the question, with a leaning.

### OWNER-7 — S3 adds a VM record kind while [VMREC] is in flight (D153), and S2 rides inside it
SUSPECTED (sequencing; confirm with the manager's reading of D153's scope over [VMREC]). Severity design.
Effort S. Blast radius: [VMREC] (b)/(c), S2, S3. arev §4.1 S2/S3 rows, §2.3 reason 3.
- [VMREC] at f15f30f25: STATE:started; (a) done 3bc599c92; (b) the analysis-free R stage and (c) the analysis
  build NOT started. D153: "A round-3 row that touches a site under remodel sequences" behind it; why: "Building
  a row on a site mid-remodel moves the edit set the refactor's instruments re-derive".
- S3 adds `VK_AUTO` to `VmKind` (the remodel's central enum) and its prerequisite reads "[VMREC] (a) DONE,
  `VK_AUTO`'s effects written to (c)'s declared-effects rule" — a RULING of r9, not (c)'s built analysis. (c)'s
  lexer/analysis would then have to model a kind it was not designed with. S3 is a choice row (an
  optimization by D186), so D153 binds it; arev does not list (b)/(c) as prerequisites nor argue the exception.
- S2's trigger is "a change opening `vm_revdet_rep` ([VMREC] (b) or (c), ...)": a migration added INTO the
  in-flight refactor's change. Ride-along says the migration goes with it or just before; D153's "remodel
  overlap" column should name it so the [VMREC] lane's identity instrument is not surprised.
- Expected: S3 prerequisites name [VMREC] (c) landed (or an argued exception for the owner); S2 named in
  [VMREC]'s row as a ride-along it may carry.

### OWNER-8 — the ratchet credit for S1 and S2 is counted by recipes the same note wrote; R03 falls by a rename
CONFIRMED (text). Severity design (check design, learnings §3). Effort S. Blast radius: G2's measurable, the §5
log. arev §0 G2, §4.3, §3.2.
- R03 restated: "`} Rev;` ... present: 1, else 0". S2 = "`Rev` becomes the shared `RevWalk` ... `vm_rev_emit`
  becomes the kind's structural renderer, unchanged in its text". The recipe reads 0 after a struct rename while
  the second renderer (the parallel walk body) stays — the recipe counts a spelling, not a mechanism. arev
  concedes it ("Whether that counts R03 to 0 is owner question 2").
- R28 is a member arev itself adds (+1) and S1 deletes (-1): S1's only ratchet movement is a row the same note
  created. Legitimate under roadmap §8 item 2, but G2's "R28, R03, R10 fall to 0" then reads as three
  mechanisms removed where, by the manifesto's measure (two mechanisms doing one job), S1+S2 remove one
  frozen-string copy and one struct.
- The control shares a source with what it controls. Expected: recipes counted by an independent author (the
  manager restating §5, as roadmap §5 says), and R03's recipe counting renderers of reverse walks (table +
  structural = one representation axis, if the owner rules structural is a representation and not a parallel
  mechanism).
- Dangling references: arev cites "owner question 2" (§3.2, §4.1 S2, §6) and "open question 3" (§8), but the
  note has no questions section; the questions apparently live in the lane report (denylisted for this round).
  The design note itself must carry the owner's questions in plain words (docs/design/CLAUDE.md, memory
  plain-words).

### OWNER-9 — no per-step cost line; "cost nothing on the box" is not true of S1/S2
CONFIRMED (text). Severity doc. Effort S. arev §4.1.
- The steps table has prerequisites, gate, trigger and ratchet, but no COST column (lines moved, lane size, box
  time) beside the BUY (ratchet units, the operand it frees). The roadmap row gives only "S per step (S3: M)".
- §4.1: "S1 and S2 ... cost nothing on the box". Their gates are `emit_sweep.py` identity over the corpus,
  `make test`, `make test-codegen` and sabotage re-aims (S1825/S1827/S74/S759/S760; S50-S52/S94/S160): heavy,
  box-locked runs. The owner weighs cost/benefit at GO (memory cost/benefit pushback); state it.
- What each step buys, read under the owner's criteria: S1 buys G2-G3 of vlookbehind §4 (floor, seed, names
  as operands: an F1 gain if OWNER-1 is fixed, a relocation of C text if not) and S3's precondition; S2 buys a
  shared record description (small F1 gain, no F2 gain while the structural renderer stays); S3 buys the first
  cross-engine gate (OWNER-4); S4 buys R10 and P-d's falsifier (the largest F1/F4 gain, the asserts becoming
  seam type checks).

### OWNER-10 — stale at the build commit: [LB-EXIST] IS filed
CONFIRMED. Severity doc. Effort trivial. arev §5 first bullet.
- arev §5: "The HELD row is NOT yet filed (checked on lane/vlbrev1 at 2056360d7 ...)". At f15f30f25,
  plan.md has `- [LB-EXIST] STATE:not-started — lookbehind existence filter ...` (HELD; refs vlookbehind §5.4,
  [ENG-LOOK]). The ask ("it should name this note's `exist`/`gate` rows as the reverse form") must now be checked
  against the filed text: it names "reverse-dfa's existence exit", not `gate`.

## PROBED-AND-HELD

- The open "VM base" frame is NOT leaned on as ruled. Checked every step's prerequisite, gate and trigger
  (S0-S5, 6 rows), the §3.1 soundness argument, the §2.3 finisher contract and §0 non-goals: none cites the
  frame; §6 is headed "NOT a rule" and §0 lists choosing it as a non-goal. §3.1's soundness rests on the
  recorded exactness fact (`Nfa.erased`), which holds under either reading. The roadmap A-REV section does not
  cite it either. Held.
- The record keeps `host` as an operand so VM-only facts (charge, frames) do not leak into inline walks (§6
  "Where it could hurt"): consistent with F1; held.
- Selections are declared first-match row tables, not if-chains: §3.1 exit rows (3), §2.2 exit/behaviour table
  (5 rows), §2.1 operand table. Held against the owner's table rule.
- Facts both ways (F4 as a constraint): the realized `Nfa.erased`, the overflow-as-decline and the build request
  travel with the machine-table entry (§2.4). Held (but see OWNER-3 on observing them).
- Prerequisite statuses as stated in §4.1 checked at f15f30f25: [VMREC] (a) DONE 3bc599c92 (matches);
  [GIVEUP-DIFF] not started (matches); [VLOOKBEHIND] rev 1 PROPOSED, not built (matches "rev 1 in progress, not
  built"); [REVBLOCK-VIEW] filed, not scheduled, and itself byte-moving (S1 rides before it, consistent).
  4 of 4 held.
- `scripts/emit_sweep.py` exists in the review tree (G1's comparator): held.
- No-reverse-VM non-goal matches the owner's quoted words in vlookbehind rev 1 §0: held.
- D186 kind: S3's rows are CHOICE rows with per-regime evidence and the narrowing rule (§3.1, §4.2 reuses rev 1
  §5.4's (a)-(d)): held. Flag-follows-caller-effect (test-only lever unless a regime can be slower): held.
