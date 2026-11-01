# OWNER lens (owner criteria F1-F4, GOALS folded in): crit-stream2 re-check of approach.md rev 2

Review tree: worktrees/crit-stream2 at 8e846f501. Scratch evidence in this dir: cotouch.txt
(per first-parent commit: sha, code files, emit_dfa.c?, emit_vm.c?), merges.txt.

## Findings

### OWNER-1: the F1 check fails on all three real row-adding merges I tested, and it cannot be run as written
CONFIRMED. Severity: design. Effort: medium (a file→part map plus a fuller cross-part list in §2). Blast
radius: §0 F1 row, §2 "The F1 claim, made checkable", §9.2 F1 row. Status: INDUCED by the B3 fix (the
check is what B3's fix added, and it is incomplete).
- Check (a) says `git diff --stat` touches no file of P3, P4 or P5. Nothing maps files to parts. The
  part table names mechanisms, not files. Today the files straddle parts: emit_dfa.c holds the
  planner tables (`cand_rows[]`, the req-use rows), renderers AND the abi constant
  (`#define PCREC_ARTIFACT_ABI 93`, src/gen/emit_dfa.c:55). compile.c holds the fit ladder and the
  driver. As written, (a) has nothing to run against.
- The real cases, read from diffs:
  1. 02229045e [REQRUN-VM] added two decision rows (`handoff-attempts`, `-entry`) to the req-use
     table over existing hands, which is exactly the doc's "new admission row over existing kinds".
     Its change set also had (i) a new size-ladder rung `drop-handoff` in src/core/compile.c
     (`fit_rungs[]`, FIT_DROP_HANDOFF, fit_seq_legal rows); (ii) an emitter→driver flag
     `Job.req_handoff_vm` (internal.h, set at emit_dfa.c:1182, :7737); (iii) an abi bump 90→91 at
     emit_dfa.c:55; (iv) a VM renderer insertion point (emit_vm.c `pcrec_emit_req_attempt_reentry`);
     (v) four spec hunks.
  2. 00c97769e [REQ-HANDOFF-L1] added a req-use row. It needed two NEW IR facts
     (`PF_FACT(REQ_SET_MAXOFF…)`, `REQ_LANDMARK_MAXOFF` in src/facts/facts.def, plus facts.h and
     req.c), which is P1 + P2.
  3. lane/p1build (the doc's own row 5 / pattern 2): the lever `PCREC_NO_LANDMARK_WALK` (bit 57) in
     lib/pcrec.h:1210 + src/core/axes.def:184 + tuning.md; a ladder rung `drop-landmark-walk`
     (compile.c:1403); a new kit-site row `DELEG_SITE(LMHIT, MF_OP_FIND, …)` in
     src/gen/memfn_sites.def (each site stays countable, Q-R10-6); the abi bump.
- §2 says the ONLY cross-part changes are a new kind/exit/hand type and a new kit operation. Missing
  from that list: a new IR fact (P1+P2), a new public lever (lib/pcrec.h, axes.def, cli; no part owns
  them), a new ladder rung (no part owns compile.c's ladder), a new kit-site id (memfn_sites.def,
  which sits on the P3/P4 seam), and the abi bump, which D76/D94 requires whenever bytes move, and
  every new row moves the bytes of the patterns it admits. Each of the three cases would fail check
  (a) under the stated rule.
- The control case held: 002810cac [SCANEDGE-SET] (a byte-set SKIP operand) is correctly a contract
  event by §2's rule.
- Needed: a declared file→part map (or the end state's file layout), owners for the lever, the abi
  constant, the ladder and the DELEG table, and the cross-part list extended with "new IR fact" and
  "new kit-site id". Otherwise the F1 claim needs restating as "P2 plus the row's lever/stamp/fact
  satellites", with those satellites named.

### OWNER-2: F4 misses a backward channel, so its measurable form passes against an incomplete list
CONFIRMED. Severity: design. Effort: small to medium. Blast radius: §0 F4 row, §2 part table, §4.2.
Status: NEW in rev 2 (round 1's B7 list had the same gap).
- The size-cap fit ladder (src/core/compile.c:1268 `fit_rungs[]`, 14 rows; [DEC-FALLBACK]/[PF-DROP])
  is a plan-time BACKWARD fact running from the rendered artifact to the selection. The emitter
  writes `Job` fields while it renders (`req_handoff_vm` "Written by the emitter at the text it
  writes"; also `anchored_ok`, `revend_form`, `engine`, `mf_*`; grep `cx->job->X =` in src/gen/*.c,
  18 fields). The driver reads them, measures the size, and RETRIES the compile with a row denied.
- §4.2 claims "every field below" covers what today's tree carries (seven channels). §0 F4 fails "if
  any is dropped". This channel is in neither list. It has no part in §2, and it is a loop
  (render → measure → re-plan), not a declared acyclic card read (rule 2). The F4 check therefore
  passes vacuously for it.
- Needed: name the ladder's home (P2's planner? P5?), and a card field on the renderer side (a
  rendered-size fact) or a declared re-plan rule. Without one, the size-driven row drops stay the
  blindness F4 forbids.

### OWNER-3: F3's named oracles run end to end through other parts, so round-1 B6 is fixed only in name
CONFIRMED (by reading §2's oracle column). Severity: design. Effort: small (restate) to large (the
interpreter). Blast radius: §0 F3 row, §2, §9.2 F3 row. Status: round-1 B6 NOT FIXED in substance.
B6's ruling was "name per-part oracles" FIX-NOW, interpreter PLAN.
- P1: "libpcre2 (PC-3) on answers through the reference tiling (all-B)". That runs through P2's
  all-B tiling AND P3's renderers AND gcc. The "IR listing pins" are regression goldens that P1's own
  owner writes, not an oracle.
- P2.r: the witnesses' answers "against the reference tiling" go through P3.
- P2 "now": through P3, as the doc admits (loss 1).
- P3: "byte identity against a frozen baseline". The baseline is produced by P1+P2+P3 together, and
  it cannot tell a correct renderer change from a wrong one, so it is a regression pin, not an
  oracle.
- P5: libpcre2 through the .rxt corpus, which means through every part.
- So by §0's own failure form ("only check is end to end through another part"), P1, P2, P2.r, P3 and
  P5 fail today and under the design as scheduled. Only P4 passes, the same as today ("Today only the
  kit passes"). §3 gives the interpreter's trigger as "a non-gcc target, or loss 1's mitigation
  chosen", not F3 itself. §9.2's "each part against its own oracle" therefore overclaims.
- Not re-litigating the ruling: PLAN under D77 can stand. Then the F3 row and §9.2 should state that
  F3 is NOT met until the interpreter lands, and name F3 as a trigger for it. Also needed for P1: an
  oracle that does not render (an IR-level executor is the interpreter's natural sibling), or an
  honest "P1 has none".

### OWNER-4: F2's "renderer set plus a kit target, every record unchanged" is false by the doc's own §3, and the kit seam is C text in both directions
CONFIRMED. Severity: design. Effort: small (restate). Blast radius: §0 F2 row, §2 P4 row, §3, §9.2 F2
row. Status: NEW (B4 fixed for records, not for the kit seam).
- §3 lists the C-level content of today's records (VP_TEXT vm_stmt.h:70-83, VG_* :100-104, VK_PUSH
  :48, C local names). It calls their removal "a renderer-side move when its trigger fires (a second
  target…)". So the first new target IS the change that rewrites the records (P6) and their writers.
  "With the planner and every record unchanged" cannot hold for the first new target, which is the
  case F2 is about.
- §2's P4 contract reads "IN: facts (`mf_site`)", and §3 calls the facts interface target-neutral.
  But the P3→P4 call also passes `mf_hooks` (memfn/include/memfn.h:873-1022). Its fields are C
  expressions (`s`, `n`, `lo`, `floor`, `result`, `cursor`, `peek`), C statements (`on_miss`,
  `step` "`pos++;`", `more`), a callback that writes pcrec's C verify text into the kit's output
  (`on_cand`, ending in the `MF_TOK_ACCEPT`/`REJECT` tokens, :1036), `indent`, and a declaration
  prefix ("size_t "). A new target therefore changes memfn.h's interface, a P3+P4 contract event, not
  just "a kit target".
- Needed: the F2 row should say "a new target = migrate the records (§3), restate the kit's hook
  interface for the target, then a renderer set and a kit back end". Either way, P2 unchanged is the
  checkable part.

### OWNER-5: §0.1's counts reproduce, but the counting rule is under-stated, and the baseline measures a different quantity from the F1 check
CONFIRMED. Severity: doc. Effort: small. Blast radius: §0 F1 row, §0.1. Status: NEW wording (the B2
numbers themselves hold).
- Reproduced at 8e846f501: `git log --first-parent --merges --since=2026-09-01` gives 698 merges (697
  plus the scensus merge 9bc9da507, which touches no code); 207 touch src/|cli/|lib/; 66 touch both
  emitters, 79 one; (66+79)/207 = 70%. All hold.
- Under-stated: the word "merges" is load-bearing. Over all first-parent commits the same rule gives
  2,412 commits, 260 code-bearing, 72 both (28%), 90 one, 62% the pair. The diff base (first parent)
  and the date field are also unstated.
- The line counts: 30,209 holds (16,008 + 14,201). 96,159 equals `src/*/*.c` + `cli/*.c` only (lib/
  has no .c). The written rule "`src/*/*.c` + `cli/` + `lib/`" gives 98,089 (it counts cli/CLAUDE.md,
  lib/CLAUDE.md and pcrec.h). Headers are excluded (src .c + .h = 106,348).
- The 32%/70% counts ANY code merge touching the emitters. The F1 check is about admission-row
  changes. No today-number exists for the check itself. A baseline of "row-adding merges touching
  more than their table" (OWNER-1's three cases: 3 of 3) would measure the claim.

### OWNER-6: residual reach and speed argument, and §9.2's census citation measures a different predicate
CONFIRMED. Severity: doc. Effort: small. Blast radius: §1.1 row 3, §9.2 "what today can NEVER do", §10
reading. Status: round-1 B1 residue.
- §9.2 says today can never reach "a regular region below an irregular node at any depth (census
  below)". The census's M5a is a regular consuming leaf AFTER the first nested irregular node's
  subtree, "outside any irregular ancestor" (docs/dev/lanes/scensus_evidence/census.py:333-341). That
  is the opposite of "below", so the 12/490 does not size the claim.
- Both that row and "a callout inside a deterministic scan" are REACH arguments. §1.1 row 3 ("today
  reads the match three times, the stream reads it once") is a speed argument. The owner made speed
  (and benefits like it) not the case. These should be labelled as G0-neutral observations or moved
  out of the F1-F4 head-to-head.

### OWNER-7: the goals' priority order is the doc's inference, not the owner's
SUSPECTED (what would confirm it: an owner statement ranking F1-F3). Severity: doc. Effort: trivial.
Blast radius: §0. Status: NEW.
- The owner numbered 1-3 and listed F4 without ranking them (round1/COMMON.md, last section).
  "F1 over F2 over F3; F4 a constraint" is a reasonable reading, but it should be marked as the
  manager's ranking for the owner to confirm (architecture.md:11 requires a priority order; it does
  not require inventing one).
- F1's measurable form also drops two of the owner's own F1 symptoms: "test errors can come from
  anywhere" and "new code is generated instead of updating existing". Only F3's oracle row touches
  the first one, and OWNER-3 shows that row fails.

## PROBED-AND-HELD

- §0.1 co-touch: 207 / 66 / 79 / 70% reproduced exactly (698 merges at HEAD = 697 + 1 code-free).
  Emitter lines 16,008 + 14,201 = 30,209; 31.4% of 96,159 (under the .c-only reading).
- §10 census: all 16 cells (8 rows x bench/corpus) match scensus/run/summary.txt. Those are:
  captures-only 24/629, zero-width-only 12/459, no-backreference 12/453, no-callout 6/55, cap-in-repeat
  VM 10/438, M5a VM 12/490, M5b VM 14/409, landmark-exists 19/456. Also the header "VM 86 of 335" /
  "2,226 of 4,794", and §5.2's "bench 10, plus 8 frames-unbounded".
- Cited lines hold in the review tree: memfn.h:414-415 (MF_SK_* enum), emit_dfa.c:1415-1426
  (`site_kinds[]`), callsite_rows.c:1-14.
- GOALS shape (architecture.md:7-14): a Goals section exists, with who-benefits and a fails-when form
  per goal, a priority order, non-goals, and speed demoted to a G0 gate (B1 fixed in shape). §11's T
  rows are gates, not benefits (held).
- §2's cross-part rule classifies [SCANEDGE-SET] (002810cac, a new SKIP operand) correctly as a
  contract event (1 case).
- F4's two worked examples ([LANDWALK-PRES], [CAND-SPAN]) are stated as card reads with soundness
  kept separate (read, not re-proved; another lens owns soundness).

## Summary

The counts in §0.1 and §10 reproduce exactly. The weakness is the checkable forms.
F1: on three real row-adding merges, the change set also hit the fit ladder, a public lever, IR facts,
a kit-site row and the abi constant, and no file→part map exists (OWNER-1).
F4 omits the size-ladder re-plan loop (OWNER-2).
F3's oracles are end to end for P1, P2, P3 and P5, so B6 is fixed only in name (OWNER-3).
F2 is false for the first target by §3's own text, and the kit seam carries C text (OWNER-4).
Minor issues: the counting rule's wording, residual reach claims, an unstated priority order.
