# Lane vmcons: ONE design for the VM trail and dispatch build (R, slot-flow verdicts, C, D)

Lane vmcons (opus), 2026-10-29. Design and measurement only (no build go): nothing under
`src/`, `cli/`, `lib/` or `memfn/` changed. Worktree `worktrees/vmcons`, branch `lane/vmcons`
off main 2a565ea88. This document replaces, for the build, the three designs it consolidates:
`trailgen_report.md` (TG: R, UNDO-DEAD), `vmbc_report.md` (VB: B dead writes, C per-site call
restore) and `altd_report.md` (AD: D first-byte dispatch). It applies review
`docs/dev/reviews/2026-10-29-r3-vmtrail.md` (cited `[r3 Fn]`) and its MANAGER RULINGS, plus
this lane's rulings file (`vmcons_rulings.md`, entry R1).

Base code: lane/trailgc (D183, trail compaction at checkpoints). Probes ran on its tip
75ac19837 (`worktrees/trailgc/build/pcrec`, copied to scratch, sha256 c81eee47cf81c71a...);
the composed twins reuse vmbc's stock C emitted at 801ad1214, the commit the three designs and
the review measured, so every number below is comparable to theirs. Evidence:
`docs/dev/lanes/vmcons_evidence/` (scripts, raw tables, logs); scratch
`/var/tmp/pcrec-pcrec/scratch/vmcons/`.

## Summary

- **Premise test: reproduced.** The review's F1 witness `^(?:(?:[bB]|[cC]d)(\w))+by$` on
  `bxby`, with dead-write deletion run on the event stream as it exists: the listing records
  the write of slot 4 (the revdet loop entry) and no read of it, so the write is "dead" and is
  deleted. Stock and libpcre2 give group 1 = 1,2; the twin gives -1,-1 (also `bxcdzby`,
  `BqBqby`). The C reads slot 4 on six lines the stream never saw. `[r3 F1]`
- **One analysis input.** The build reads the emitter's event stream, EXTENDED (Stage -1):
  slot reads, SET sources, conditional jumps, both cut spellings, C locals that cross a push,
  push site kinds, backreference and backward-consuming tests, callouts, checkpoints and work
  charges become recorded events. A completeness check that is not the analysis (text vs event
  counts over the corpus) guards it. The listing header's "complete for control structure"
  becomes true. `[r3 F1, F17]`
- **One pipeline: each pass reads a REAL emission.** Walk 1 emits the stock program (C, R and
  the per-site call restore are rendering-level and present in every walk). D decides on walk
  1's events and walk 2 emits with D applied. The slot-flow verdicts decide on walk 2's events
  and walk 3 emits the final C and the listing. Every derived fact (push total and the
  resume-point cap, checkpoints and margin, framelessness and entry shape, stamps) is read from
  the final walk. Soundness then composes by transitivity: each pass is proven against the
  program it actually reads. `[r3 F7, F4, F5]`
- **One table** of statement kinds with one column per analysis (reads, writes, copies,
  MAYFRAMES, FIRST+, successors, verdict eligibility), one "unrecognised" row that refuses the
  matcher function, and one first-match verdict table decided in ordered ROUNDS: DELETE (dead,
  then copy) to a fixpoint, then UNTRAIL last. The call snapshot and C's per-site restore are
  rows of the same table. `[r3 F17, F16, F4, F2, F8]`
- **Measured together for the first time** (instructions per call, warm; 0 answer differences
  over 18,200 + 3,640 identity cells):

  | subject | stock | full stack R+B+C+U+D | D stage 1 only | C ablated | pcre2-jit |
  |---|---|---|---|---|---|
  | nest-paren-32k | 31.07 | **3.87** | 4.26 | 3.80 | 10.35 |
  | nest-brace-100k | 162.72 | **15.31** | 21.11 | 48.21 | 50.40 |
  | js-1m | 260.71 | **38.43** | 45.52 | 149.21 | 58.58 |
  | idents-1m | 191.67 | **53.78** | 54.74 | 55.03 | 82.09 |
  | splice-1m | 47.76 | **18.42** | 18.42 | 18.42 | 23.66 |
  | comment-5m | 220.97 | **101.96** | 107.46 | 105.96 | 86.50 |

  - **C stays:** without it, default depth falls to nest-brace 119 and JSON 21 (below jit's 176
    and 150), and js and nest-brace lose 3-4x.
  - **D stage 1 is the first cut:** with R, B, C and U it is already below jit in instructions
    on five of six subjects, at depths 1022 and 340. Stage 2 is filed with a trigger. `[r3 F32]`
  - **R and D overlap:** R's increment on the full stack is -10 % to +4 %, not the -8 % to -20 %
    it gives on stock. `[r3 F21, F24]`
  - **comment-5m stays above jit** (x1.18) under every stack; it is a named residual, not a goal
    this build meets.
- **Deny axes (ruled R1):**
  - D gets ONE public deny flag and a count stamp: +1 flag bit, leaving 5 free with the filed
    bit-57 candidate. That does not reach [IFACE-PUSH]'s hard trigger.
  - The slot-flow verdicts get NO public flag. They get a test-only lever on the EXISTING
    harness mechanism (`PcrecHarnessOptions` / `--harness=` / `build/pcrec-harness`,
    `run_axes.sh` INTERNAL_ARMS, the lever fence).
  - R and the per-site restore move get no flag of any kind. `[r3 F11]`
- **Two landings, two abi events.** Landing 1 is Stage -1 plus R (every VM artifact moves once,
  with no spec number moved). Landing 2 is the walks, D stage 1, C and the verdicts, with every
  depth/trail spec paragraph re-pinned ONCE. One STEP 0 job comes before landing 2's build go.
  `[r3 F34, F29]`
- **Questions for Frank:** two landings or one; D stage 2 filed; the three-walk pipeline
  against an in-memory program rewrite.

## Disposition table

One row per review finding. "Where" names this document's section that carries the fix.

| id | ruled | disposition here | where |
|---|---|---|---|
| F1 | FIX-NOW | Stage -1 extends the event stream (reads, SET sources, BRANCH, both cuts, locals, site kinds, BREF, backward tests, CALLOUT, checkpoint, work). Completeness check by text-vs-event counts. ir_listing header DOC hunk. Premise reproduced at the base. | The analysis input; Measurements |
| F2 | FIX-NOW | Table row: a CALL at site c reads W(g) ∩ live-after(R_c), in every round and stage. The witness is a test cell (W2). | The verdict table; Soundness at the seams |
| F3 | FIX-NOW | R is restated as "every cursor access in every matcher function", with a grep guard. The `abd` witness is R's sabotage (W3). | Pipeline and stages; Soundness at the seams |
| F4 | FIX-NOW | Ordered rounds: DEAD to a fixpoint, then COPY, repeated, then one recompute, then UNTRAIL last. Nothing after UNTRAIL carries a fact across a resume edge. TRAIL-EQ-LIVE is stated, and every proof citing it is checked. REACH gap recorded. | The verdict table; Soundness at the seams |
| F5 | FIX-NOW | The unrecognised row refuses the matcher function in every column. D runs on its own walk before the slot-flow verdicts, so the slot-flow reader sees D's dispatch as a declared SWITCH row with its case successors. | The verdict table; Pipeline and stages |
| F6 | DOC | D may replace a non-terminating left-recursive failure by an answer, inside pattern_language §9 paragraph 4a's latitude and limits §6. §9 paragraph 4a's own example moves and is in the re-pin list. REACH witness W6. | Soundness at the seams; Build plan |
| F7 | FIX-NOW | One pipeline. The final walk owns the push total and the resume-point cap, checkpoints and margin, FRAMELESS, ENTRY_SHAPE, the stamps and the listing. Capacities keep the AST pre-pass in this build (safe over-charge); stamp shrink is filed. `--emit-ir` renders the final walk's own events, so ir_listing §1¶4 holds. | Pipeline and stages; Deny axes and stamps |
| F8 | FIX-NOW | The callout row reads `slot_values[0 .. 2*ncap-1]` with ncap = the pattern's groups + 1 (match_api §11.3¶3), whatever `--no-captures` says. Witness W8 reproduced. | The verdict table |
| F9 | DOC + PLAN | S179, S180, `run_frame_buffer.sh`, `fb_mmap_driver.c`, framebuffer.rxt cells 2-4 and match_api §10.2¶4 join landing 2's reader census. S180 gets a designed witness (STEP 0 item). Both are re-validated with the sabotage matrix before landing. | Build plan; STEP 0 |
| F10 | FIX-NOW | A "drop-dispatch" rung on the size-cap ladder (`fit_rungs[]`): re-emit without D before refusing. No size factor constant. limits §8.4/§8.5 hunk. STEP 0 censuses D's growth. | Pipeline and stages; Build plan |
| F11 | ruled R1 | D: one public deny + count stamp. Slot-flow verdicts: a test-only harness lever, no public bit. R and the C move: none, proven at landing. +1 flag bit; trigger not reached. | Deny axes and stamps |
| F12 | FIX-NOW | The text checker is a SECOND IMPLEMENTATION, not an independent control. The independent controls are stock-vs-build answers, the oracle `.rxt` expectations and a D27 author. Gate rule: the build declines iff the checker declines, and a checker-refused optimised artifact fails. One shared test-side text-graph module. | Soundness at the seams; Build plan |
| F13 | PLAN | One sabotage table (rule row, plant, witness, expected delta). The cheap part runs on the prototypes in STEP 0, including U through VB's 9-file recursion harness and give-up-to-answer cells checked against libpcre2. | Soundness at the seams; STEP 0 |
| F14 | FIX-NOW | The counter control is re-aimed to `(?:a\|ab){300}+c` (reach-probed: `rungs counter`). `(?:a\|bc){3}+` is kept as the revdet-local witness. | Soundness at the seams; Measurements |
| F15 | DOC | FIRST+ is its own program-altitude column, not a client of kindrow's PATH column. The PATH split (EFFECT / UNSEEN) is a PLAN item under F19. | The verdict table |
| F16 | DOC | Snapshot entries are verdict sites of the one table: DELETE iff their own site's restore is deleted, else KEEP; never COPY, never UNTRAIL. | The verdict table |
| F17 | FIX-NOW | One statement-kind table with one column per analysis and one unrecognised row. | The verdict table |
| F18 | DOC/PLAN | (a) D183 addendum: walk 3's `nset` counts trailed writes only, so placement and margin follow the verdicts with no second mechanism; trail_checkpoints.py keys on a declared token list. (b) [ART-TRAIL-ELIDE] closes into this build with both obligations. (c) [ENG-ISL-S2] class-member fold is conditional on STEP 0's census. (d) One-build ruling recorded in this lane's brief; dependency is only the code-site contract. (e) One give-up-direction sentence per axis. | Build plan |
| F19 | PLAN (c FIX-NOW) | (a) PATH split filed. (b) The verdict table absorbs C; the revdet local is a listed member. (c) One test-side `tests/vm/vmgraph.py` shared by trail_checkpoints.py and the checker. | Build plan |
| F20 | PLAN | The three-walk pipeline is the minimal form of "program IR + dataflow + render". Unlocks (a)-(e) filed with triggers. | Pipeline and stages; Build plan |
| F21 | PLAN (STEP 0c) | Full-stack and ablation twins MEASURED here in instructions (identity 0 diffs). Cycles OWED to STEP 0 under the quiet gate. "Compound" withdrawn: R overlaps D. | Measurements |
| F22 | DOC | U is reframed: it removes the trail cost of capture-reading patterns, mainly backreferences. The median is 0 % over 46. U's case rests on bak-2 and phone-palindrome. | Goals and non-goals; Measurements |
| F23 | PLAN | STEP 0 re-derives engine membership by emitting at the pin, all 79 distinct texts, `-e utf8` where labelled. | STEP 0 |
| F24 | DOC | R on B+C is -0.4 % to -20.1 % (comment-5m -0.4 %), over two matchers. R's population is counted in STEP 0. | Measurements |
| F25 | DOC | Rule (iii) is not built. The "identical" claim is withdrawn: Bd vs B differ by up to 2.2 %, the twin method's layout-noise floor. TG row 6 now reads "argued, not measured". | Measurements |
| F26 | DOC + PLAN | Goals are stated in instructions. Cycles are retaken under the bench quiet gate (STEP 0 card). -O3 and default-arm R twins are in STEP 0. | Goals and non-goals; STEP 0 |
| F27 | PLAN | The two-matcher-body and callout shapes are a first-class STEP 0 category. The build's behaviour: every matcher function is analysed or refused as a whole; `__match_notempty` is a copy of the final walk's matcher. | Pipeline and stages; STEP 0 |
| F29 | DOC | Bench `program_sha256` null band and `rx_info.trail_frames` join the mover census. Two landings spend the null band twice (R once, movers once). Ask Frank. | Build plan; Questions for Frank |
| F30 | DOC | "B removes 0.4 % of entries" and "38 B-dead sites" are withdrawn (no table). Loads: instructions only. Columns here are Bd/BCd (no iii). | Measurements |
| F31 | NOTED | Sizes are calibrated on D183 (+213 source lines against +861 test/spec, two lanes, one stop). | Build plan |
| F32 | PLAN | Measured: D stage 1 first. C stays (depth 119/21 without it). D stage 2 is filed. | Measurements; Build plan |
| F33 | REJECTED | No action; `restrict` does not change the assembly. | — |
| F34 | FIX-NOW | One STEP 0 job, one pass order (D, then slot-flow, R rendering), two abi events. | STEP 0; Build plan |
| F35 | PLAN | Build row with stages, gates and a remodel-overlap column (VM-LEN-HOIST, OPT-VMLIT, VM-CLSMASK, SPAN-ISEL read; SITE-FRAMELESS, INLINE-C stage 3 adjacent). | Build plan |
| F36 | FIX-NOW | One ranked goal set with non-goals; each stage tagged with the goal it serves. | Goals and non-goals |
| F37 | DOC | One limits §7 paragraph covers D and the verdicts: one-way toward answers, and which stamp or listing row shows it. | Build plan |
| SLOTS-5 note | FIX-NOW | VE_PUSH carries an enumerated site kind; D's admission reads the enum, never role text. | The analysis input |
| Lessons 1-4 | ACCEPTED | Added to `docs/dev/guide/critics.md` (round 2026-10-29 r3). | — |

## Goals and non-goals

Ranked. Each stage serves the goals named in Build plan's stage list.

1. **G1, answers.** Identical to stock wherever stock answers, captures included; never a new
   give-up. Where stock gives up (FRAMES, WORK, STEPS), the build may answer, and the answer is
   libpcre2's (one-way toward answers; limits §1, §7). Left recursion may move from FRAMES to an
   answer inside pattern_language §9 paragraph 4a. `[r3 F36, F6]`
2. **G2, the recursive and scanner members' rate.** On the bench gap subjects (cscan's idents,
   splice, nest-paren, nest-brace, comment; JSON's js), instructions per call at or below
   pcre2-jit's. This is the design-time proxy. The landing confirms it in cycles under the
   bench quiet gate. ONE bar (x1.0), replacing VB's x2 and AD's x1. `[r3 F36, F26]`
3. **G3, flat VM patterns.** Fewer instructions per subject byte on the bench's non-recursive
   VM members. The headline is the backreference family: U removes the trail cost of
   capture-reading patterns, bak-2 -64 %, phone-palindrome -51 % in instructions. The median
   over the 46 sampled artifacts is 0 %. `[r3 F22]`
4. **G4, depth.** Default-arm depth at or above pcre2-jit's on nest-brace (176) and JSON
   (150).
5. **G5, storage.** Less working storage for one-shot callers (js-1m first touch 339 -> 64
   B/byte under B+C).

**Non-goals.**

- Default capacities, and stamped capacity shrink. The AST pre-pass keeps sizing in this build.
  Shrink is filed as its own row (trigger: a measured one-shot storage need).
- comment-5m below jit: it stays x1.18 in instructions under every stack measured here, and no
  stage of this build moves it below.
- D stage 2 (loops and optionals): filed. Its trigger is a bench cell that stage 1 leaves above
  jit in cycles at landing and stage 2 brings under.
- Packed 8-byte trail entries, narrow frames, rule (iii), runtime epochs: filed or rejected as
  in TG.
- The DFA route, the island's own rows, the kit: no change.

## The analysis input

**What the producer carries today** (grep of `src/gen/emit_vm.c` at lane/trailgc 75ac19837):

- The struct is `VEvent { VEKind k; int a, b; const char *role; }`, appended by
  `vm_ev(v, k, a, b, role)`.
- The kinds are LABEL, CLASS, PUSH, SET (a: the target slot only), GOTO, FAIL, ACCEPT, ASSERT,
  NOTE, ISLAND, CALLOUT, RUNG, STRAT, CUT (a: the mark slot), PRUNE, CALL, RETURN, LIT and
  WCLASS. VE_CALLOUT now has a producer (`vm_callout`, [INLINE-C] 1b); the enum comment still
  says "reserved", a one-line DOC fix.
- The counts are 54 `vm_ev` calls against 182 `pcrec_sb_printf` calls; 29 raw `slot_values[%`
  read formats; 32 raw `goto %s_L%d` formats against 7 `VE_GOTO` producers; `vm_jump`
  returns text and records nothing; the revdet cut is two raw printfs of
  `run->resume_depth = <rv>_frame_mark` logged as VE_NOTE. Six raw slot writes exist outside
  `vm_set`; two are the callout's slot-0 save and restore.
- `vm_slot_ref` has five callers, all SET sources. Role strings are declared decoration.

So the stream lacks slot reads, SET sources, conditional edges and the revdet cut as an edge,
exactly as `[r3 F1]` states. The premise test above shows the cost: an invisible read is not
"unrecognised", so no refuse row can catch it.

**The extension (Stage -1).** Every new or changed event is recorded by the SAME primitive call
that writes the C, as S10 already requires of labels, pushes and sets:

| event | recorded by | carries | replaces |
|---|---|---|---|
| VE_READ a=slot | `vm_slot_read(v, slot)`: returns the `slot_values[...]` text AND records the read; every raw `slot_values[%` format and `vm_slot_ref` route through it | the slot | 29 raw formats; `vm_slot_ref` |
| VE_SET a=slot, b=source slot+1 or 0 | `vm_set` (and `vm_set_copy(v, s, t)` for `s := slot[t]`) | the target, the copy source | VE_SET with no source; the listing's `<- scan_position` lie |
| VE_BRANCH a=target | `vm_jump` (every conditional `goto <p>_L`) | the target; successors are the target AND the next statement | 32 raw formats, the missing L2->L6 and L2->L5 edges of `(?:a\|bc){3}+` |
| VE_CUT a=slot or -1, b=local id | `vm_cut`, plus a local-mark form used by the revdet cut | the mark | the revdet cut's VE_NOTE |
| VE_LSET / VE_LREAD a=local id | `vm_local_set` / `vm_local_read` over a per-matcher table of declared locals that live across a push (revdet cursor, iteration and frame mark; span cursors; C's `<p>_ret_frame`) | the local | raw printfs |
| VE_PUSH b=site kind | `vm_push_at(..., kind)`; kind is an enum (alt-branch, optional greedy or lazy, loop-iteration greedy or lazy, possessive exit, rung retreat, lookaround, ...) | the structural site kind | role-text matching `[r3 SLOTS-5]` |
| VE_BREF a=group | the backreference compare | consumes unknown bytes; its reads are VE_READ | label role only |
| VE_CLASSB | the backward consuming test (lookbehind) | as VE_CLASS, direction backward | "consumed BACKWARD" role text |
| VE_SWITCH / VE_CASE a=label, b=class id | ONE switch primitive, shared by the island root and D's dispatch (AD stage 1's simplification) | each case's target and byte class; a default | the island's arms recorded as VE_GOTO |
| VE_CHECKPOINT, VE_WORK | `vm_trail_check`, `vm_work_at` | slot-neutral; the work charge's mark read is a VE_READ | VE_NOTE |
| VE_CALLOUT (exists) | `vm_callout` | the site id; its read and transient write sets come from the table row | the raw slot-0 save and restore stay raw, declared by the row |
| attempt entry | the matcher entry label is the target of the attempt reset | a graph fact, not an event | TG's extra edge, now stated once |

**The completeness check** (independent of the analysis: it counts TEXT and compares with the
LISTING, the `run_ir_listing.sh` shape that already pins labels, pushes and slots). For every
corpus artifact, inside each matcher function, outside `#define` bodies:

- the count of `slot_values[` read sites equals the count of VE_READ events (writes counted
  separately against VE_SET);
- the count of `goto <p>_L` equals the count of GOTO, BRANCH and CASE events;
- `<P>_PUSH(` equals PUSH; `<P>_CUT(` plus `resume_depth =` outside the macros equals CUT;
- every `return` site outside the prologue is a declared exit.

A planted sabotage (one raw read printf restored) must turn the check red. The ir_listing.md
header sentence "complete for control structure, lossy on operands" becomes true for control
structure and slot operands. D106's "lossy" stays for value text only. Its spec hunk appends
the ops (`read`, `branch`, `setu`, `restore`, `switch`, `case`, `lset`) to §3.4 and replaces
§3.2¶1's "Written" derivation.

**The alternative, rejected: the build reads TEXT.** An analysis over the rendered C inside the
compiler would be a parser of our own output. It is a second description of the program
(S10's failure), and it would take the text checker's role, so checker and build would share a
source. The stream extension costs one primitive per spelling and moves no artifact byte.

## The verdict table

**One statement-kind table.** Rows are the event kinds after Stage -1. Each analysis reads its
own column; nothing else decides. `s` is a slot, `L` a label, W(g) the slots region g can write
(minus 0/1), R_c the return label of call site c, ncap = the pattern's group count + 1.

| kind | successors | reads | writes | copies (must) | MAYFRAMES | FIRST+ (F, E) | verdict site |
|---|---|---|---|---|---|---|---|
| LABEL | next | — | — | meet of preds | join of preds | continue | — |
| SET s <- e | next | its VE_READs | s | kill s; gen s==t if e is slot[t] | pass | continue iff the write is non-effect (below) | yes: DEAD, COPY, UNTRAIL |
| snapshot entry j of call c | next | none | trail only | none | pass | continue | yes: row V1 |
| restore of s at R_c (C) | next | trail | s | kill s | pass | continue | yes: row V2 |
| READ (in a test or compare) | — | s | — | — | — | — | — |
| PUSH L (site kind) | next, L | live-in(L) | — | L inherits the pusher's facts | adds L; L gets the pusher's set | fork: continue and L | D: by site kind |
| CALL c (region g, return R_c) | callee entry | **W(g) ∩ live-after(R_c)** `[r3 F2]` | — | none after | pass (its frame resumes at fail, no label) | continue into the callee | — |
| RETURN (region exit) | every R_c of the region | live-in of every R_c | — | none at any R_c | pass | fork to every R_c | — |
| GOTO L | L | — | — | — | — | continue at L | — |
| BRANCH L (non-consuming test) | L, next | its VE_READs | — | — | — | fork both | — |
| CLASS / LIT / WCLASS (forward consume) | next on match; fail | — | — | — | — | F ∪= the byte class; stop | — |
| span (cursor rung) | next | its VE_READs, LREADs | its locals | — | — | F ∪= class, continue as zero iterations; stop if the reach test demands one | — |
| SWITCH + CASEs (island, D) | every case label and the default | — | — | — | — | each case contributes its class, then forks | — |
| CLASSB (backward consume) | next; fail | — | — | — | — | OPAQUE | — |
| BREF g | next; fail | 2g, 2g+1 | — | — | — | OPAQUE | — |
| CUT (slot or local mark) | next | the mark | — | unchanged | unchanged (over-approximation) | OPAQUE `[AD commit opacity]` | — |
| CHECKPOINT | next | — | trail only | — | — | continue | — |
| WORK | next | its VE_READ | — | — | — | continue | — |
| LSET x / LREAD x | next | x (LREAD) | x (LSET) | — | — | continue iff the write is non-effect (below) | never (locals are untrailed by construction) |
| CALLOUT site | next; fail | `slot_values[0 .. 2*ncap-1]` (match_api §11.3¶3, whatever `--no-captures` says) and the caller's vars `[r3 F8]` | slot 0, transiently (saved and restored around the call: net none) | kill all | pass | OPAQUE | — |
| ACCEPT | — | slots `0 .. 2*NCAPS-1` (slot 0 carries `\K`) | — | — | — | F = all, E = true | — |
| FAIL | the unwind (modelled by the PUSH edges) | — | — | — | — | nothing | — |
| attempt entry | the matcher entry | — | — | no facts | {} | — | — |
| **unrecognised** | — | — | — | — | — | — | **refuse the matcher function**: every verdict KEEP, D declines `[r3 F5]` |

**The non-effect rule (FIRST+'s write row, MEASURE-11's form).** A write before a dropped
continuation's first byte is a non-effect iff its variable is TRAILED, or the variable is dead
at every resume label its failure can reach (the next candidate's label and every label in
MAYFRAMES). Otherwise the continuation is OPAQUE. D runs on walk 1, where every slot write is
trailed (P7). So for slots this reduces to AD's row 6. The live clause is exercised only by
locals. AD's prototype treated local writes as "continue", so STEP 0 measures what the exact
rule declines.

**FIRST+ is its own column** at program altitude. It is not a reader of kindrow's PATH column:
it follows calls (PATH says OPAQUE) and treats every cut as OPAQUE (PATH says TRANSPARENT for
atomic groups). Unifying the two is F19(a)'s filed split of PATH's OPAQUE into EFFECT and
UNSEEN. `[r3 F15]`

**D's admission table** (first match per choice point; it reads VE_PUSH's site-kind enum):

| row | site kind | admit when | emit |
|---|---|---|---|
| D1 | flat alternation the island admits | the island's own rules | island trie (unchanged) |
| D2 | alternation chain, n >= 2 | some byte class drops a continuation | SWITCH to per-class chains, original order, a push only between candidates |
| D3 | optional, loop iteration (stage 2, FILED) | — | the stock chain |
| D4 | rung retreat, lookaround, possessive exit, anything else | — | the stock chain |

The size bound is a ladder rung, not a row with a factor (see Pipeline and stages).

**The slot-flow verdict table** (per SET site, first match; decided in ROUNDS, each round on
the program it rewrites):

| row | site | verdict | round | emitted |
|---|---|---|---|---|
| V0 | the matcher function holds an unrecognised statement | KEEP (every site) | — | `<P>_SET` |
| V1 | snapshot entry of s at call c | DELETE iff V2 deletes the restore of s at R_c; else KEEP. Never COPY (although `s == s`), never UNTRAIL (K36 positional storage). `[r3 F16]` | A (with its restore) | nothing / `<P>_SET` |
| V2 | restore of s at R_c | DELETE iff s ∉ K_c = W(g) ∩ live-after(R_c); else KEEP | A | nothing / the restore |
| V3 | s is dead after the site | DELETE (DEAD) | A1 | nothing |
| V4 | s == source on every path (must) | DELETE (COPY) | A2 | nothing |
| V5 | s is dead at the attempt entry and at every L in MAYFRAMES(site) | UNTRAIL | B | `<P>_SETU` (a plain store) |
| V6 | otherwise | KEEP | — | `<P>_SET` |

**The rounds (the order F4 requires).**

1. **Round A, repeated until nothing changes:**
   - A1: liveness, then every DEAD verdict (V2, V3 and V1 through V2) applied together;
   - A2: available copies on the A1 result, then every COPY verdict applied together.
2. **Round B, once:** liveness and MAYFRAMES recomputed on round A's result, then every
   UNTRAIL verdict applied together.
3. **Nothing after round B** carries a fact across a resume edge.

Why each group may be applied together, and the two kinds may not:

- **DEAD.** Deleting a dead write removes a kill of a slot dead after it and removes reads, so
  liveness only shrinks. Every other DEAD verdict stays valid.
- **COPY.** Deleting `s := slot[t]` where s == t holds leaves the facts after it unchanged, so
  every other COPY verdict stays valid.
- **DEAD with COPY is not safe.** In `s := t; s := t; read s`, the first write is dead (the
  second kills it) and the second is a copy (the first established s == t). Deleting both is
  wrong. Hence A1 and A2 alternate with re-analysis.
- **UNTRAIL.** Untrailing changes neither liveness nor MAYFRAMES, so all of them may be applied
  together. It weakens TRAIL-EQ to TRAIL-EQ-LIVE, so no must-analysis may run after it (SLOTS-3's
  counter-program). `[r3 F4]`

**C in the one table.** Liveness uses VB's stock-restore model in every round:

- every return label R_c kills all of W(g) (as if every restore were kept);
- the CALL at site c reads W(g) ∩ live-after(R_c);
- snapshot entries read nothing.

That is one monotone pass, free of VB's two traps (self-propping snapshots, growing keep sets).
K_c is read off it. The per-site restore itself (the linkage move) is a rendering change present
in every walk (Pipeline and stages), so V2 always has a per-site restore to decide.

## Pipeline and stages

**Rendering-level changes (present in every walk, no verdict, no flag).**

- **R:** every cursor access in EVERY matcher function is a local: `trail_depth`,
  `resume_depth`, `call_top`, `steps_left`, `work_left`, the bases and the caps. That covers
  macro text, primitive value text (every CUT mark write `(ptrdiff_t)run->resume_depth`,
  `CHARGE_WORK`'s `run->resume_depth - mark`), raw printfs (the revdet frame mark and cut,
  `--run->steps_left` at a callout site, the exit's positional read via `run->call_top`) and
  `<prefix>__match_notempty`. Locals are written back at every return and bracketed around the
  cold compaction call and any call that passes `run`. `[r3 F3]`
- **C-move:** the linked call's restore moves from the shared region exit to each call site's
  return label. The exit records the frame index in `<p>_ret_frame`, a declared local. On its
  own this is answer-identical (VB: idents 191.53 against 191.67). It also fixes K36 by
  construction: the positional reads run after the exit's capacity guard.

**The walks.** Each pass reads the events of a real emission, never a predicted one.

| walk | emits | read by | skipped when |
|---|---|---|---|
| 1 | the stock program (R and C-move included) | D's FIRST+ (all slot writes trailed: P7, full TRAIL-EQ) | never |
| 2 | walk 1 with D's dispatch verdicts | the slot-flow rounds | D found no site, or D is denied (walk 2 = walk 1) |
| 3 | walk 2 with the slot-flow verdicts: the FINAL C and the listing | every derived fact below | no verdict fires, or the lever is on (walk 3 = walk 2) |

- **Verdicts are keyed by site id:** the ordinal of the site's event in the walk that decided
  it. Walks run the same deterministic AST walk, so ids match. D's new chain labels are
  allocated after every walk-1 label, so walk-1 ids stay stable.
- **A codegen check pins the keying:** a walk taking an all-KEEP verdict table must emit
  byte-identical C and events to its input walk. This is also exactly what the deny flag and
  the lever produce.
- **What the final walk owns:**
  - the push-site total and the resume-point cap. D can exceed the chain's n-1:
    `[abd]x|[acd]y|[bcd]z` gives 5 sites against 2. The ir_listing `resume-points` row becomes
    the final walk's count;
  - checkpoint placement and the D183 margin. `vm_jump_closes_trail_cycle` reads the emission
    counter `nset`, and in walk 3 `vm_set` counts KEEP sites only (`vm_setu` does not count).
    So placement on trailed-write cycles and the trailed-site margin follow with NO second
    mechanism: D183 addendum `[r3 F18a]`;
  - FRAMELESS, ENTRY_SHAPE and the entry rung. `a(?:\dx|[a-z]y)c` is framed today with one
    disjoint push, and D makes it frameless. A codegen check asserts §6.3.8¶10's iff against
    the final text `[r3 F7]`;
  - the stamps, `RX_VM_PROGRAM_BYTES`, the listing and the `__match_notempty` copy.
- **What keeps the AST pre-pass in this build:** the capacities (`vm_plan_capacities`,
  `vm_cost`) and the stamped `TRAIL_FRAMES` / `RESUME_FRAMES`. Every pass only lowers use, so
  the pre-pass over-charges, which is the S87-safe direction. Stamp shrink is filed as its own
  row; its trigger is a measured one-shot storage need, and its general form is F20(a).
  `[r3 F7, COST-3, CONTRACT-7]`
- **Size (F10):** an over-cap artifact climbs a new `fit_rungs[]` rung, "drop-dispatch"
  (re-emit without D, i.e. skip walk 2), before the refusal. limits §8.4¶4's "smallest
  artifact" promise then holds structurally. No size factor exists to tune. STEP 0 censuses
  D's growth (AD measured +9 to +10 % of emitted C on cscan and JSON as an upper bound).
- **Compile time:** at most three emission walks per VM artifact. STEP 0 measures the
  emission share of compile time today. Emission is small against the gcc step, but that is
  the claim to measure.
- **The general form (F20)** is a VM program IR with a dataflow framework and a renderer. The
  walks are its minimal form: walk 1's events are the IR, the passes are the dataflow, and
  walks 2-3 are the render. Its unlocks are filed, not built (Build plan).

**Order: D first, then the slot-flow verdicts.**

- D's proof needs full TRAIL-EQ, which holds only before UNTRAIL.
- The slot-flow verdicts are facts about the program actually rendered, which has the
  dispatch in it. So no MEASURE-11 seam exists.
- B can find more dead writes after D (fewer push-edge reads).
- Measured on the prototypes: the D-first order gives the same instructions to the digit and
  the same depths as the D-last order, with 0 identity differences (Measurements). U fires on
  one more cscan site (10 against 9): "D only widens U".

## Soundness at the seams

**The composed argument.**

- **Rendering refactors.** R and the C-move are present in every walk. They are
  answer-identical by construction, and each has its own guard:
  - R: the grep check below;
  - C-move: identity, plus K36's existing witnesses.
- **Walk 1 to walk 2 (D).** AD's proof, against walk 1's complete program. Every slot write is
  trailed there, so "the unwind restores every slot" holds as stated. Locals use the
  non-effect rule.
- **Walk 2 to walk 3 (verdicts).** VB's TRAIL-EQ induction and TG's UNTRAIL argument, against
  walk 2's complete program, in the round order above.
- **Composition.** Stock ≡ walk 2 ≡ walk 3 by transitivity. Each proof's only premise about
  its input is that the input is COMPLETELY modelled. Stage -1 and its completeness check
  provide that, and the unrecognised row refuses the function otherwise.

**Seam by seam.**

- **F5, unknown statements.** An unrecognised statement refuses the WHOLE matcher function, for
  every column: liveness, both forward analyses and FIRST+. This is what the twins measured
  (whole-artifact refusal). D's dispatch is not unknown to the slot-flow reader: SWITCH/CASE is
  a declared row whose successors are the case labels. TG's ordering sentence and its
  "the second lander adds the dispatch's row" both become unnecessary, because D always runs
  first and the reader always knows SWITCH.
- **F2, the linked call's parked value.** The CALL row reads W(g) ∩ live-after(R_c) in every
  round. Before the C-move existed this would have read live-after of the shared exit's return
  labels. With the C-move in every walk, the row is always per site. The witness is W2.
- **F3, cursor reads in value text.** R's change list is "every read or write of a cursor in
  every matcher function". The guard is a codegen check: no
  `run->(resume_depth|trail_depth|call_top|steps_left|work_left)` occurs in a matcher function
  outside the write-back and reload brackets. Sabotages:
  - W3, the CUT mark: `^(?:(?>ab|a)c|abd)` on `abd`; the narrow-R twin answers nomatch where
    stock matches 0,3;
  - TG's two: `steps_left` write-back, and the reload after compaction.
- **F8, the callout read set under `--no-captures`.** The CALLOUT row reads
  `slot_values[0 .. 2*ncap-1]` with ncap = groups + 1, not NCAPS. The witness is W8.
- **F4, UNTRAIL against COPY.** Round B comes last, and nothing after it carries facts across
  a resume edge. TRAIL-EQ-LIVE ("at a resume of frame F every slot LIVE at F's resume label
  holds its push-time value") is the lemma after round B. The proofs that cite TRAIL-EQ need
  only the live form:
  - C's backtrack into a returned callee: the restored slots are the live ones;
  - D's dropped continuation: D runs before UNTRAIL;
  - D183 compaction: an untrailed old value is restored only at a frame where V5 proved it
    dead.

  No emitted producer of the counter-program's shape (a copy right after a resume label
  following an untrailable write) exists today: **a REACH gap**, recorded. Its sabotage row is
  "compute V5 on round A's input liveness". A witness is to be built when a producer appears;
  the splice park and restore pair is the likely one.
- **F6, D on left recursion.** FIRST+ is a least fixpoint, so a left-recursive arm gets F =
  its base's bytes. Stock runs the arm, recurses at one position until FRAMES at every
  capacity, and libpcre2 returns -52. D does not enter it on a byte outside F, and answers.
  This is allowed by pattern_language §9 paragraph 4a and limits §6, but §9 paragraph 4a's own example
  (`(?:a|(?R))+` on `b` gives FRAMES) moves. It is in the re-pin list. W6 is a REACH witness
  (stock FRAMES reproduced at the base).
- **D's commit opacity, lookarounds, callouts, order, nullable arms, caseless and UTF-8.**
  These are AD's arguments unchanged; their witnesses are cells W10-W17.
- **The two-matcher-body shape (F27).** `__match_notempty` is a text copy of the final walk's
  matcher plus one accept guard that reads no slot. So the verdicts, MAYFRAMES and FIRST+
  carry over (review PROBED-AND-HELD). R localises both functions (the grep check covers every
  matcher function).
- **The checker (F12).** The text-reading checker is a second implementation of the same
  table, NOT an independent control. Its rule:
  - every DELETE, UNTRAIL and dispatch the build emits must be re-derived from the text;
  - the build declines iff the checker declines;
  - a checker-refused optimised artifact fails the gate. (A refusing checker otherwise passes
    vacuously.)

  The independent controls are:
  - stock-vs-build answers: the deny flag and the lever produce the stock form in-tree;
  - the oracle-verified `.rxt` expectations;
  - libpcre2 for the give-up-to-answer cells;
  - a D27 spec-first test author: recommended for the build, written from G1's promise.

  The four text-side graph builders (trail_checkpoints.py and the three prototypes) become ONE
  test-side module, `tests/vm/vmgraph.py`, so a graph-model fix lands once (F19c).

**The witness cells** (every review witness, as a named test cell with its exact command). The
"base" column is what the base gives today (`vmcons_evidence/witness.log`, run by
`S=$PCREC_TMPDIR/scratch/vmcons bash docs/dev/lanes/vmcons_evidence/witness.sh $S/pcrec_base`).
In the build each cell becomes a sabotage row: plant the rule's failure, and the cell must
change.

| cell | rule row guarded | pattern, flags, subject | base answer (and the rule-as-written twin) | build cell |
|---|---|---|---|---|
| W1 | Stage -1 reads (F1) | `^(?:(?:[bB]\|[cC]d)(\w))+by$`, default, `bxby` / `bxcdzby` / `BqBqby` | 1:1,2 / 1:4,5 / 1:3,4 (twin: 1:-1,-1 each); libpcre2 agrees with stock | sabotage: drop VE_READ from the revdet compare; the completeness check AND the cell must catch it |
| W2 | CALL reads W ∩ live-after (F2) | `^(b)(?1)`, `--engine=vm -fno-splice-calls`, `bb` | 0:0,2 1:0,1 (twin: 1:-1,-1); libpcre2 agrees | sabotage: the call reads nothing |
| W3 | R covers value text (F3) | `^(?:(?>ab\|a)c\|abd)`, `--engine=vm`, `abd` | match 0,3 (reach: `RX_SET(RX_SLOT_CUT_MARK0, (ptrdiff_t)run->resume_depth)` present) | sabotage: leave the mark's value text unlocalised |
| W4 | round order (F4) | no producer today | REACH gap | sabotage row specified; a witness to be built with the first producer |
| W5 | unrecognised refuses the function (F5) | any artifact plus a planted unknown statement before a dispatched arm | — | sabotage: per-statement refuse; the planted-statement cell must catch it |
| W6 | D on left recursion (F6) | `(?:a\|(?R))+` on `b`, `ab`, `ba`; `^(a\|(?1)b)` on `x`, `b` | FRAMES on all (libpcre2 -52) | REACH: the cell must MOVE to an answer (a pinned expectation, re-pinned in §9 paragraph 4a) |
| W7a | FRAMELESS iff (F7) | `a(?:\dx\|[a-z]y)c`, `--engine=vm` | FRAMELESS 0, ENTRY_SHAPE plain, 1 push site | codegen check: FRAMELESS 1 and no `_PUSH(` after D |
| W7b | push-site cap from the final walk (F7) | `[abd]x\|[acd]y\|[bcd]z`, `--engine=vm` | resume-points 2, islands 0 | the final walk's count is 5; the cap reads it |
| W8 | callout ncap (F8) | `(a)(?:(b)\|c)(?C\`c: return RX_CAP_SET(2) ? RX_FAIL : RX_PASS;\`)d`, `--allow-code=c --no-captures`, `abd` / `acd` | nomatch / match (twin with the group writes deleted: match / match); `ncap = 3` | sabotage: the row reads 0..2*NCAPS-1 |
| W9 | S180 detector (F9) | to be designed in STEP 0 | — | re-validate S179/S180 in the matrix |
| W14 | U leaves a live counter trailed (F14) | `(?:a\|ab){300}+c`, `--engine=vm` | `rungs counter` (reach holds); `(?:a\|bc){3}+` is `rungs revdet` | sabotage: drop MAYFRAMES |
| W15 | U entry liveness (TG) | `a\|(b)c` on `bxa` | stock g1 -1,-1 | sabotage TG_SAB_ENTRY (detected in TG) |
| W16 | U MAYFRAMES (TG) | `(ab\|a)+ab` on `aaba` | stock g1 0,1 | sabotage TG_SAB_FRAMES (detected in TG; 610 of 1,020 subjects differ) |
| W10 | D commit opacity | `^(?(DEFINE)(?<g>a\|ab))(?>(?&g))c$` on `abc` | nomatch | sabotage: CUT not OPAQUE (the harness went red in AD) |
| W11 | D lookaround cut | `^(?!)(?<g>a\|ab)\|^(?&g)c$` on `abc`, `ac` | stock | same |
| W12 | D order | `(a\|ab)(c\|bcd)(d*)` on `abcd` | stock | sabotage: class chains reordered |
| W13 | D nullable and end arms | `(\|a)b`, `(a\|)+?$`, `(a\|$)` | stock | sabotage: E ignored |
| W17 | D callout, caseless, UTF-8 | `(?C1)a\|b` on `b`; `(?i)(k\|z)` on `K`; `(é\|e)` with `-e utf8` | stock | sabotage: CALLOUT not OPAQUE |
| W18 | VB's B/C witnesses | `^(a(?1)?b)\1$` on `aabbaabb`; `^((?>a(?1)?))a$`; `^((a)(?1)?(b))$`; `^(a\Kb)(?1)$` | stock | sabotages: PENDING read dropped; CUT mark read dropped; `\K` slot 0 in W |

## Deny axes and stamps

Written one way, as ruled (R1, Frank 2026-10-29): the flag follows what a change can DO to a
caller.

| change | can it be slower on real input? | risk | public flag | test lever | stamp |
|---|---|---|---|---|---|
| D (first-byte dispatch) | yes: a `switch` per entry where a continuation would have failed fast (AD measured +11 % on idents with an over-wide admission) | wrong answer, and speed | **ONE deny flag**, deny only. A force would be unsound: it would dispatch where FIRST+ cannot prove the drop. Working name `-fno-first-byte-dispatch`; final spelling per D174 at the build | — | **`<PREFIX>_VM_DISPATCH_SITES`**, a count beside `_VM_ALT_ISLANDS`; the listing's `switch`/`case` rows |
| slot-flow verdicts (DELETE, COPY, UNTRAIL; C's narrowing) | no: they only remove work | wrong answer | **none** | **`--harness=keep-slot-writes`**: field `slot_flow_off` in `PcrecHarnessOptions`, every verdict KEEP (walk 3 skipped) | none in the header; the listing's ops (`setu`, absent writes) and one summary row of verdict counts |
| R (cursor locals) | no (a refactor: same algorithm, same values) | wrong answer if incomplete | none | none | none; proven at landing by answer identity plus F3's grep guard |
| C-move (per-site restore) | no (a refactor) | wrong answer if positional reads move | none | none | none; proven by identity plus K36's witnesses |

**The existing test-only mechanism (R1(d)).** pcrec already has one, and this design uses it
rather than inventing another:

- `build/pcrec-harness` (`cli/main.c` with `-DPCREC_HARNESS`) parses `--harness=` options into
  `PcrecHarnessOptions` (`src/core/internal.h`), a bitfield outside `pcrec_options` and outside
  the caller contract. It is reached only through `pcrec_harness_compile`.
- It already carries `compound_off` (`--harness=no-compound`, force-declining a whole family),
  `arm_reach` and `kit_proof`.
- `tests/axes/run_axes.sh` sweeps it as `INTERNAL_ARMS`: answers must equal the default's, as
  for any axis.
- `tests/compound/run_lever_fence.sh` (G7) fences it:
  - one global under the reserved prefix `pcrec_harness_`;
  - no lib/ declaration;
  - the spelling appears nowhere outside an allowlist.

**The new lever's cost** is:

- one bitfield;
- one CLI arm in the harness build;
- one `INTERNAL_ARMS` entry;
- the fence allowlist lines for its uses (the axes arm and STEP 0's identity runs).

It spends no public flag bit, and every later refactor-class change reuses the same mechanism.

**Flag bits.**

- Today bits 0-54 and 56 are used, and bit 55 is the kit's: 57 used, 7 free (57-63).
- The filed [IFACE-PUSH] candidate takes bit 57, leaving 6. D's deny takes one: **5 remain**.
- The hard trigger ("the push opens when <= 4 flag bits remain") is NOT reached. Without the
  bit-57 candidate, 6 remain.

**D46 and the give-up surface.**

- D46's "observable and forceable": D is observable (a stamp) and deniable. It is not
  forceable, for the stated reason that a force is unsound.
- The verdicts are observable in the listing and deniable through the lever, as R1(b) rules.
- Each axis states its give-up direction once (D148 Q6 form): one-way toward answers. Steps,
  work, frames and trail use only go down. tuning gets a D section and a verdict sentence, and
  limits §7 gets one paragraph covering both. `[r3 F18e, F37]`

## Measurements

**Method.** Composed twins of vmbc's stock C (lane/trailgc 801ad1214). The order is: the
slot-flow prototype (`vmopt_tg.py`, modes `Bd`, `BCd`, `BdU`, `BCdU`); AD's `altd.py` (mode
`A` = stage 1; `ALkf` = stages 1+2 with the kind rule and FOLLOW through returns); then TG's
`variants.py R`. The D-first order (`mkd.sh`) runs `altd.py` first.

- Instructions are `instructions:u` per call, (11 - 1)/10, `_in` NF=4,194,304 NT=67,108,864,
  gcc -O2.
- Box load was 16-63 from queued correctness jobs. **Instructions only; no cycle number here.**
- pcre2-jit figures are VB's (`gap/p2 ... jg`, libpcre2 10.46).
- Builds: `vmcons_evidence/mkc.sh`, `mkd.sh`. Rates: `rate.sh`. Depth: `depth.sh` (default arm,
  bisect). Identity: `ident.py` (VB's, retargeted).

**Instructions per call, M** (`rate_instr.txt`, `rate_dfirst.txt`):

| subject | stock | B+C+U | B+C+U+R | B+C+U+D | **full: B+C+U+D+R** | full, D-first order | D stage 1 (+B+C+U+R) | C ablated (Bd+U+D+R) | D alone + R | jit |
|---|---|---|---|---|---|---|---|---|---|---|
| nest-paren-32k | 31.07 | 24.97 | 20.05 | 3.73 | **3.87** | 3.87 | 4.26 | 3.80 | 9.57 | 10.35 |
| nest-brace-100k | 162.72 | 90.42 | 72.72 | 16.71 | **15.31** | 15.31 | 21.11 | 48.21 | 65.22 | 50.40 |
| js-1m | 260.71 | 72.63 | 65.02 | 42.65 | **38.43** | 38.43 | 45.52 | 149.21 | 192.43 | 58.58 |
| idents-1m | 191.67 | 90.39 | 78.67 | 56.63 | **53.78** | 53.78 | 54.74 | 55.03 | 144.99 | 82.09 |
| splice-1m | 47.76 | 20.42 | 18.76 | 19.76 | **18.42** | 18.42 | 18.42 | 18.42 | 43.42 | 23.66 |
| comment-5m | 220.97 | 128.47 | 129.97 | 98.96 | **101.96** | 101.96 | 107.46 | 105.96 | 180.47 | 86.50 |

**Pushes per subject byte:** full stack 0 / 0 / 0.44 / 0.90 / 0.33 / 0.20 (nest-paren,
nest-brace, js, idents, splice, comment); D stage 1 1.00 / 1.00 / 1.01 / 1.10 / 0.33 / 0.30.

**Default-arm depth** (`depth_default.txt`; jit 176 / 150):

| stack | nest-brace levels | JSON `[[..1..]]` |
|---|---|---|
| B+C+U+R (no D) | 511 | 291 |
| full (B+C+U+D+R), either order | **2046** | **408** |
| D stage 1 (+B+C+U+R), either order | 1022 | 340 |
| C ablated (Bd+U+D+R), stage 1 or full D | **119** | **21** |

**Identity** (`ident.log`, `ident_dfirst.log`): every twin against stock, default arm plus the
`_in` arm at NF=200,000 with trail caps 8 to 4,000,000, rc and every capture span.

- 99 cscan and 161 JSON subjects, 12 composed twins.
- **0 differences** in 18,200 + 3,640 cells.
- The twins answer 1,586 + 1,238 and 529 + 484 cells where stock gives up, each equal to
  stock's answer at a huge buffer. A libpcre2 check of those cells is in STEP 0.
- No twin gives up where stock answered.

**Re-based claims (each replaces a claim in the three designs).**

- **R on B+C** (TG's table recomputed, F24): idents -13.2 %, nest-brace -20.1 %, splice
  -8.1 %, js -10.5 %, nest-paren -19.6 %, comment **-0.4 %**. So the range is -0.4 % to
  -20.1 %, over TWO matchers, and B+C+U+R is +1.2 % worse than B+C+U on comment. R on stock
  stays -8 % to -18 %.
- **R on the full stack** (new): nest-paren +3.8 %, nest-brace -8.4 %, js -9.9 %, idents
  -5.0 %, splice -6.8 %, comment +3.0 %. TG's "R and D compound and do not overlap" is
  WITHDRAWN: D removes the push and fail traffic R makes cheap. The +3 % cells are at the
  layout-noise floor (2.2 %, F25). R keeps its case on stock-shaped artifacts (every VM
  artifact R reaches, D or not) and is the cheapest stage. R's real population (VM artifacts
  whose matcher is a separate function) is counted in STEP 0. `[r3 F21, F24]`
- **C ablated** (new, F32): without C, js and nest-brace are 3.9x and 3.1x slower than with
  it, and depth falls below jit (119 and 21). C carries G2 on js and G4 on both members; on
  idents, splice, nest-paren and comment it changes little. **C is kept.**
- **D stage 1 as the first cut** (F32): with R+B+C+U it is at or below jit in instructions on
  five of six subjects (nest-paren x0.41, nest-brace x0.42, js x0.78, idents x0.67, splice
  x0.78), and its depths (1022, 340) exceed jit's. Stage 2 adds 0 % to -27 % and depth
  2046/408. No goal needs that. **Stage 2 is filed.** AD's js x1.06 in cycles was measured
  without R; the cycle check under the quiet gate is in STEP 0.
- **D-first order** (new, F34): same instructions to the digit and the same depths as D-last
  on all six, 0 identity differences. U fires on 10 cscan sites against 9.
- **U's framing** (F22): the flat-bench -21.7 % is a sum dominated by six backreference
  artifacts. The median over 46 is 0 %. TG's per-artifact table stands as recorded (bak-2
  -64.4 %, phone-palindrome-6 -50.6 % instructions).
- **Withdrawn numbers** (F30, F25):
  - "B removes 0.4 % of trail entries" (no table carries it);
  - "38 B-dead sites" (16 shown);
  - "(iii) identical on all six" (Bd vs B differ by up to 2.2 %, the noise floor; no BC-with-(iii)
    column was printed).

**The witness probes** (`witness.log`, base 75ac19837): W1, W2 and W8 reproduce their wrong
answers with the rule as written; W3, W6, W7a, W7b and W14 reach their sites. That is the
premise test plus lesson 4's reach probe for every review witness.

**Standing questions (docs/design/CLAUDE.md).**

1. **Measurement regime: relevant.** Warm repeated calls, resident buffers, one box (7700X),
   gcc 15.2 -O2, instructions only here. Cycles (G2's landing form) and the one-shot regime
   (G5) are STEP 0 cards under the bench quiet gate.
2. **Independent control: relevant.** Stock-vs-twin answers by running both binaries (never by
   the analysis), oracle `.rxt` expectations, libpcre2 for give-up-to-answer cells. The text
   checker is a second implementation, not a control (F12).
3. **What moves on regeneration: relevant.**
   - Landing 1: every VM artifact's matcher text (R); the bench `program_sha256` null band.
   - Landing 2: the movers' bytes, the listing, the stamps (`_VM_DISPATCH_SITES`, FRAMELESS
     and ENTRY_SHAPE where D removes the last push, `RX_VM_PROGRAM_BYTES`), checkpoint lines
     and the margin constant, and `rx_info` fields that read them.
   - Each landing is one abi event with a mover census and readers found by grep.

## STEP 0

ONE job before landing 2's build go, queued by the manager outside 19:00-00:00. It runs on the
prototypes against lane/trailgc's pin, in the D-first order (walk order), and is heavy (over 50
compiles). Exact commands follow. `$E` = `docs/dev/lanes/vmcons_evidence`, `$S` =
`$PCREC_TMPDIR/scratch/vmcons`, `$PC` = lane/trailgc's `build/pcrec`.

| # | card | command | gate / output |
|---|---|---|---|
| 0a | corpus twin identity, full stack | `scripts/boxlock run --label vmcons-step0-ident -- env CC=$S/ccwrap.sh VMCONS_CHAIN="altd:ALkf vmopt_tg:BCdU variants:R" PCREC=$PC bash tests/harness/run.sh` (every `.rxt`); again with `RXTFLAGS="-fno-splice-calls --engine=vm"`. `ccwrap.sh` is VB's, chaining the three prototypes in walk order; it uses AD's listing-free rule `all` (the soundness-maximal superset) | 0 failed; a red is a design defect: stop and report |
| 0b | census, one pass | `scripts/boxlock run --label vmcons-step0-census -- python3 -I $S/census.py $PC --rx /home/pcrec/projects/pcrec-bench/bench/*/patterns/*.rx --corpus worktrees/trailgc` (VB's, TG's and AD's census.py merged into one: one row per artifact) | engine membership by emitting at the pin, all 79 distinct bench texts, `-e utf8` where labelled (F23); per pass: movers, sites by kind, DEAD/COPY/UNTRAIL/restore-narrowed counts, D sites and declines by admission row, R population (separate matcher functions), refusals with the two-matcher and callout shapes as first-class categories (F27), D's emitted-size growth (F10), push-free and write-free regions (F20e), the [ENG-ISL-S2] class-member share (F18c) |
| 0c | gap cycles and ablations | `$E/rate.sh` without `NOCYC`, `MODES="stock BCdU_R DF_A_BCdU_R DF_ALkf_BCdU_R BdU_ALkf_R"`, inside a bench quiet-gate window; jit: AD's `jit.sh` | G2 in cycles (F26); D stage 2's trigger evaluated |
| 0d | R at -O3 and on the default arm | `EXTRA=-O3 mkv.sh` (TG's) for `R` and `stock`; `drv d` mode through `rate.sh` | F26 |
| 0e | give-up-to-answer cells against libpcre2 | `python3 -I $E/ident.py` with a libpcre2 reference arm (`p2.c` driver) for every cell where stock gave up | every twin answer equals libpcre2's (F13) |
| 0f | sabotage table on the prototypes | one flag per rule row in `vmopt_tg.py` / `altd.py` / `variants.py` (TG's `TG_SAB_*` shape), each run on its witness cell (W1-W18) | every row DETECTED; a row that does not change its cell is a REACH failure (F13) |
| 0g | U through the recursion harness | `CC=ccwrap.sh VMOPT_MODE=BCdU PCREC=$PC bash tests/harness/run.sh tests/recursion/{cscan,nocaptures,rebind,slotfamilies,whole,bothlinkage,atomicity,captures,kreset}.rxt` (VB's 9 files, about 50 compiles), plus the `RXTFLAGS` axis | 0 failed (F13) |
| 0h | locals under D's non-effect rule | `altd.py` with locals OPAQUE against locals continue, on cscan, JSON and the census | the sites the exact rule declines |
| 0i | emission share of compile time | `perf stat -e task-clock` on `$PC -p rx` over the census patterns, against `-fno-...` everything; the walks' upper bound is 3x the emission share | Pipeline's compile-time claim |
| 0j | S180 witness | probe for a pattern whose post-build trail high-water still exceeds the swapped frames region at framebuffer cell sizes (a capture live inside a possessive loop under recursion); confirm the verifier's "cell 4 becomes a detector" with `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S179 S180` on a full-stack twin build | F9 |

Missing prototype glue, written in STEP 0's lane, scratch only: `ccwrap.sh`'s chain variable,
the merged `census.py`, the sabotage flags (0f), the libpcre2 arm (0e) and the locals switch
(0h). These are prototype edits, not product code.

## Build plan

**Gate.** One optimization build at a time until [INLINE-C] closes (ruled). This design reads
only the code-site contract (the CALLOUT row's read and transient-write sets). If [INLINE-C]
stage 3 leaves that contract unchanged, the gate is the stage-2 contract, which is the
manager's call. Base: D183 (lane/trailgc) merged.

**Sizing.** Calibrated on D183: +213 source lines, +861 test and spec lines, two lanes and one
stop. `[r3 F31]`

**Landing 1 (abi event 1): Stage -1 and R.** Size M, one lane. Goal G2/G3 on stock-shaped
artifacts.

- **Stage -1:**
  - the event extension;
  - the completeness check and its sabotage;
  - the listing fixes (header sentence, set sources, §3.4 ops);
  - the VE_CALLOUT enum comment.

  No artifact byte moves; spec hunk ir_listing.md only.
- **Stage 0, R:**
  - every cursor access, in every matcher function;
  - the F3 grep guard as a codegen check;
  - sabotages W3, the steps_left write-back and the compaction reload.

  Card: TG's gap rates (stock -8 % to -18 %); 0 on inlined artifacts.
- **Landing obligations:**
  - mover census (every VM artifact);
  - limits §5 stack numbers re-measured (R moves locals onto the C stack);
  - match_api §10.9¶10 if it moves;
  - the bench null band spent once (inbox note).

**Landing 2 (abi event 2): the pipeline, D stage 1, C and the verdicts.** Size L: two to three
lanes on D183's calibration. Internal stages, each answer-gated against its predecessor before
the next:

| stage | content | goal | gate |
|---|---|---|---|
| 2a | the walk pipeline with no verdicts | — | byte-identical to landing 1 (all-KEEP equals the input walk); codegen keying check |
| 2b | D stage 1 (row D2) | G2, G4 | corpus answers equal `-fno-<dispatch>`; W6 moves; W7a/W7b; W10-W13, W17; size rung |
| 2c | C-move (rendering) | G4 (with 2e) | identity; K36 witnesses |
| 2d | round A: DEAD, COPY, C narrowing (V1-V4) | G2, G4, G5 | corpus answers equal `--harness=keep-slot-writes`; W2, W8, W18 |
| 2e | round B: UNTRAIL (V5) | G3 | as 2d; W14-W16; W4 sabotage row (REACH gap noted) |

Landing obligations (one re-pin of each paragraph set):

- **One spec pass:**
  - limits §4 (the specimen's reach), §5¶6, §6 (left recursion), §7 (one paragraph, F37),
    §8.4/§8.5 (the drop-dispatch rung, F10);
  - match_api §6.3.8¶10-12 (FRAMELESS/ENTRY_SHAPE), §10.1¶1, §10.2¶4 (its justification
    re-witnessed, F9), §10.6¶2-3;
  - tuning §2.11¶2, §2.20 and §2.21¶3 (whether SETU counts as `RX_SET` there: it does not
    touch the trail, so it does not), and a new D section with its stamp and give-up
    sentence;
  - ir_listing §3.1 `resume-points`, `trail-entries`, §3.2;
  - pattern_language §9 paragraph 4a (its example moves, F6);
  - the guide's numbers.
- **Readers found by grep, plus these named ones:**
  - S179, S180, `run_frame_buffer.sh`, `fb_mmap_driver.c`, framebuffer.rxt cells 2-4,
    `fb_exact_driver.c`, `sr_depth`, `ts4`;
  - `rx_info.trail_frames` / `subject_ceiling` (unchanged in this build: capacities keep the
    pre-pass);
  - the bench `program_sha256` null band (movers only).
- **Decision text:**
  - D183 addendum (placement and margin follow trailed sites through walk 3's `nset`;
    `trail_checkpoints.py` keys on a declared token list, `_SET(` weighted and `_SETU(` not,
    by declaration);
  - close [ART-TRAIL-ELIDE] into this row, with its two obligations: the give-up-surface spec
    hunk and the census (0b);
  - fold [ENG-ISL-S2]'s class-member half iff 0b's population rule fires;
  - record the one-build ruling and its gate.
- **Checks:**
  - `tests/vm/vmgraph.py` as the one text-graph module (trail_checkpoints.py moves onto it);
  - the second-implementation checker under F12's gate rule;
  - `REACH_ONLY=1` over the sabotage matrix for every moved witness;
  - S179/S180 re-validated;
  - a D27 spec-first author recommended.

**Filed, not built** (D77 triggers):

- D stage 2 (loops and optionals; admission row D3). Trigger: 0c shows a gap cell above jit in
  cycles that stage 2 brings under.
- Stamped capacity shrink: program-level capacities from the final walk (F20a). Trigger: a
  measured one-shot storage need, or [ART-TRAIL-ELIDE]'s "FRAMES give-up goes" asked for by a
  caller.
- AD's unlocks: (a) precise commit opacity, (b) lookbehind as a GATE, (c) FOLLOW-through-returns
  possessify (F20c; trigger JSON depth > 408 asked for), (d) skip the re-test, (e) the
  island's root as D.
- F20(b) [SITE-FRAMELESS] per path on the program table; F20(d) slot promotion to C locals,
  which would subsume the revdet local (trigger: a counting twin after landing 2 showing slot
  traffic above noise on a losing cell); F20(e) push-free regions as DFA fragments (0b's
  column).
- F19(a): split kindrow PATH OPAQUE into EFFECT and UNSEEN, and have program events carry
  their originating kind (the first-consumed-byte family: START SET, possessify `first_of`,
  the island, FIRST+).
- TG's packed entries and narrow frames, with their recorded triggers.

**Plan row and overlap** (F35). One plan row names this sequence: landings 1 and 2, the gate
above, and this remodel-overlap column.

| row | overlap |
|---|---|
| [VM-LEN-HOIST], [OPT-VMLIT], [VM-CLSMASK], [SPAN-ISEL] | they change what FIRST+'s consume rows read; none blocks |
| [SITE-FRAMELESS] | adjacent: R touches the prologue and run state it edits |
| [INLINE-C] stage 3 | adjacent: a code site that passes `run` takes R's bracket |
| [ENG-DIRECT] | its population grows |
| [DD-11.5], [POSS-CALL-COPY], [OPT-ALTHASH] | none |

## Questions for Frank

1. **Land the register fix (R) on its own first, or everything in one landing?**
   - **The problem.** R changes the text of every VM artifact and cannot change an answer by
     construction. The analysis build (dispatch, call restore, write verdicts) is the large,
     risky part.
   - **Forces.** Two landings are two version bumps, and they spend the bench's
     "same program" noise band twice (once for every VM artifact, once for the movers). One
     landing is one bump, but a single big merge, and R's win would arrive only when the
     whole analysis is ready.
   - **Leaning:** two. R plus the event extension first; it moves no spec number and lets the
     bench see R's stock-shaped win early. The analysis build then re-pins the depth and trail
     paragraphs once.
2. **Build only the alternation half of the dispatch (stage 1) now?**
   - **Measured:** with everything else in, stage 1 is already below pcre2-jit in instructions
     on five of the six gap subjects, and its depths (1022 and 340) exceed jit's (176, 150).
     Loops and optionals cut up to 27 % more and double nest-brace's depth, but no goal asks for
     that.
   - **Forces.** Stage 2 carries the one measured exception row (loop iterations) and a
     tuning risk (+11 % on idents when admitted too widely).
   - **Leaning:** stage 1 now. Stage 2 is filed, triggered by the quiet-gate cycle check in
     STEP 0.
3. **How should the build apply its decisions: re-run the emitter (up to three walks), or
   rewrite the program in memory?**
   - **The problem.** Several facts (the push count and its cap, checkpoint placement,
     framelessness, the listing) must describe the FINAL program. Each analysis must also read
     a complete program, not a prediction of one.
   - **Forces.** Re-running the emitter with a decision table keeps the house's "one call
     writes the C and the listing" rule. Every intermediate program is a real artifact (the
     deny flag and the test lever produce exactly those). The cost is compile time, up to 3x
     the emission share, measured in STEP 0. An in-memory rewrite is cheaper to run, but it
     is a second description of what the emitter would write, which is the failure the
     listing's design forbids.
   - **Leaning:** the walks, as the minimal form of the program-IR general form; revisit only
     if STEP 0 shows the compile-time cost matters.

## STATE AT HANDOFF

- STATE: complete (design and measurement, as briefed; no build).
- Rulings file `docs/dev/lanes/vmcons_rulings.md`: R1 (Frank 2026-10-29, F11 deny axes) read
  before the evidence commit and before this report; applied in Deny axes and stamps. Last
  entry applied: R1.
- OWED: none. STEP 0 (cards 0a-0j) is the build's single pre-go job, with exact commands
  above. It is not an owed lane run: it needs over 50 compiles and a quiet-gate window, and the
  brief says not to queue and wait.
- Premise test: CONFIRMED (W1, `witness.log`).
- Box use:
  - single-process probes (about 20 compiles at the base);
  - 24 composed-twin builds;
  - instruction-count rate runs;
  - two identity runs (21,840 cells);
  - depth bisects.

  The box held queue job 680-ic3-test (no timing window); load was 16-63. All runs ended by 12:50;
  nothing ran near the 19:00-00:00 window.
- Evidence: `docs/dev/lanes/vmcons_evidence/` (`mkc.sh`, `mkd.sh`, `rate.sh`, `depth.sh`,
  `ident.py`, `witness.sh`, `p2.c`, and the raw logs `rate_instr.txt`, `rate_dfirst.txt`,
  `depth_default.txt`, `ident.log`, `ident_dfirst.log`, `witness.log`). The prototypes are
  read from `vmbc_evidence/`, `trailgen_evidence/` and `altd_evidence/` (copied to scratch);
  twins are under `/var/tmp/pcrec-pcrec/scratch/vmcons/b/`.
- Also changed: `docs/dev/guide/critics.md` (lessons 1-4, ruled ACCEPTED); the lanes history
  index entry.
- A short re-review (soundness and seam lenses only) of this document is the next step, per
  the rulings.
