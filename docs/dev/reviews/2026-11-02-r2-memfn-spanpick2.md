# Review 2026-11-02 rN: memfn-spanpick2 (design RE-CHECK): span_pick.md rev 2

DRAFT by the coordinator (crit-memfn-spanpick2). Every disposition below is PROPOSED; the launcher rules.
(The round number N is the launcher's to assign.)

## Subject

- `docs/design/memfn/span_pick.md` REVISION 2 (PROPOSED) on lane/memfn-spanpick2, frozen at the doc's
  last commit 5b3bc376a (= branch head; adds rev 2, the census dir `span_pick/`, one index line). Copy in
  `$PCREC_TMPDIR/scratch/crit-memfn-spanpick2/subject/` (sha256 1f8235978e45b76c…, re-checked OK after the
  round; branch head unchanged), with rev 1 beside it for diffing.
- Build-landing commit: main HEAD 959c08124 at the freeze (= the branch's merge base). Rev 2 cites code at
  884996ef6; 884996ef6..959c08124 changed docs only, so every code cite was checked in the review tree
  `worktrees/crit-memfn-spanpick2` (built once, `nice make -j2`, unlocked, rc 0) plus a scratch MF_TRACE
  build in the round dir (`tracebuild/`, kept in scratch; the worktree is removed).
- RE-CHECK inputs: the ruled review 2026-11-02-r1-memfn-spanpick (+ dir) and D186 addendum 1 as at
  959c08124. R-33's raw sweep (5,492 lines, sha 20ebd035…) copied read-only into the round dir as the
  population.
- Evening hold: no make by critics, no timing, no queue. Compiles: FIX 13, MEAS 5, SIM 14, SLOT 3,
  OWNER 0, verifier 10 (all single, `timeout 60`).

### FREEZE DRIFT: the owner corrected A2 DURING the round (read this first)

main moved 959c08124 -> 3e3060012 while critics ran (docs only). Two commits rewrite **D186 addendum 1
A2** (c721d115c, 5b19cbb3e): "NO special rule for `(?i)x/1234`, interim or hand-written ... no hand row is
written for its class. The loss is resolved by DATA through the general mechanism: the first PRICED
departure once stage 2's cards are measured ... Consequence: stage 2 follows stage 1 directly ... smp20's
pick is a WATCHED WITNESS at every stage." Critics graded A2 as at the freeze (the hand row ONE-STREAM
as stage 3's row 1). Consequences for this draft, applied in the dispositions below:
- Rev 2's **ONE-STREAM row (§Staging row 1) is now contrary to A2** and goes; the R-group findings about
  it are SUPERSEDED except where they carry over to any T-PICK row (noted per item).
- **Open question 2 is answered** by the correction (stage 2 follows stage 1 directly); O1 is moot.
- The **pricing findings (C-group) move from "later" to the critical path**: smp20 is now fixed only by
  a priced departure, and C1 (the undefined `streams` factor) DECIDES whether the formula can ever
  depart for smp20 under P (reading B: '/' wins under P at either hit value; reading A: it turns on
  `hit(PAIR)`). With F already favouring '/', the P side is the whole question.

## Lenses as run

| lens | model | its one question | why chosen |
|---|---|---|---|
| FIX (fix-induced, structural) | opus | For B1-B5, C3, C8, C9, E1-E3, A6: does each fix hold in today's code, and what read/hand/row/check does it add (read cycles, sibling fields, the definition and readers of every record a fix names as a home)? Per stage-1 unit: byte-identical on every arm? | a re-check (fix-induced is mandatory); the fix list was 27 ids, so the lens was split in two halves |
| MEAS (fix-induced, pricing + measurement standing questions) | opus | For A1, A3, C1, C2, C4-C7, D1-D5: does each fix hold against the cited docs/code, and what does it introduce? Then docs/design/CLAUDE.md's regime / control / regeneration questions | the other half of the fix list; measured quantities and a data file |
| SIM (simulate) | opus | Implement ONE-STREAM from the TEXT first, run it over the raw sweep, diff against rev 2's scripts, recompute every quoted number from rev 2's own formula, drill constructed cases, check the arms | a new selection rule with a census; round 1's lesson (borrowed numbers) |
| SLOT (slot tracing) + the two STANDING questions | opus | Trace every kit decider to rev 2's claimed true inventory; ratchet rows; is Goal 3's census implementable and can it fail? Sibling of a family; general form + unlocks | a table inventory is the subject's Goal 3 |
| OWNER (owner criteria + ruling check, folded) | opus | Grade rev 2 on D186 + add. 1 (A1/A2/A6) at the freeze, then each relied-on ruling's agreement and consequences; are the open questions the right owner questions; is the disposition table faithful | owner criteria in force; round 1 proposed folding the ruling check here (adopted) |
| verifier | opus | 22 groups over every CONFIRMED finding that would change the design, each tagged stage-1-blocking or later | code-reading and arithmetic judgment |

Not run: adversary (no trust boundary), soundness (no answer-identity-by-proof beyond stage 1's byte
identity, which FIX covered unit by unit), cost and overlap (D153 overlap is OWNER-7). D27 spec-first
author: still NOT recommended (the plan reply is kit-internal); revisit at the first priced row, which now
moves smp20 and carries a deny and a stamp.

## Which lens caught what

| item | FIX | MEAS | SIM | SLOT | OWNER | verifier |
|---|---|---|---|---|---|---|
| P1 plan/frame/method order (T-FRAME "at plan time", SF_WINDOW_STOP, Horspool) | 2, 3, 8 | | | 8 | | V1, V2, V3 HOLD |
| P2 B-fn vs B-pair: emit key is not (method, frame row) | 7 | | | 1 | | V4 HOLDS |
| P3 unit 1a orphans two caller-visible denies | 1 (+add.) | | | 7 | | V5 HOLDS |
| P4 Goal 3's census cannot pass / cannot fail | 6 | | | 2, 6 | | V6 HOLDS |
| S1 inline tie / run-member spellings survive | 5 | | | 3 | | V7 HOLDS |
| S2 mass primitive input shape (multiset) | 4 | | | | | V8 HOLDS |
| S3 PRES ordering double-booked; C-bound; two grouping rules | | | | 4, 5 | | V9 HOLDS |
| C1 `streams x byte(method)` undefined | | 1 | 5 | | | V10 HOLDS |
| C2 formula gaps: hit(hors), verify.cmp mispredict, exact-once rounding | | 2, 3, 5 | | | | V11 HOLD |
| C3 bands: qualifiers ranked inside band; comparison band; model error 0 | | 6, 7 | | | 3 | V11 HOLD |
| C4 noise decides but the digest excludes it | | 8 | | | | V12 HOLDS |
| C5 "zen4-grid1 rev 2" vs new run = new id | | 9 | | | | V13 PARTLY |
| C6 DEFAULTS flip and M2 envelope unstated | | 10 | | | | V14 HOLDS |
| C7 key count is the kit's self-report; `consulted` never set | | 11 | | | | V15 HOLDS |
| C8 drop-F plant sits in the C5-gated class | | 12 | | | | (text; not re-run) |
| C9 SIMD layer: cards with no reader; rule 6 vs the 11-02 "each layer its own winner" | | 13 | | | 2 | V16 HOLDS / PARTLY |
| C10 `enter` keyed by kind x entry bakes a fixture's survival | | 14 (SUSP.) | | | | not verified |
| C11 regime section omits non-card numbers the pick reads | | 15 | | | | (text) |
| C12 quoted numbers: 153,477, "2:1", "plan_cost.def hit 20" | | 4 | 6 | | | V21 HOLDS |
| R1 row 1's census is default-arm only (vm: 2 non-COVER sites; held-out empty) | | | 1 | | | V17 HOLDS |
| R2 the bound admits P-losing stops for k >= 13 | | | 2 | | | V18 HOLDS |
| R3 row 1 tie order: text vs script | | | 3 | | | V19 HOLDS |
| R4 counts pool the DEF deny arm; PF statement wrong | | | 4 | | | V20 HOLDS |
| R5 row 1 on pre-check parts moves a kit stop pcrec does not scan | | | 7 (SUSP.) | | | V17 side note |
| R6 hand rows "need only 1d" vs A2's finished refactor | | | | | 1 | V22 PARTLY |
| R7 A-model + ONE-STREAM: the first unification target stays two rules | | | | | 4 | V22 HOLDS |
| R8 smp20 has two bars, no outcome if they split | | | | | 8 | V22 HOLDS |
| R9 D144 batch gate vs D186 narrowing | | | | | 9 | V22 HOLDS |
| O1 Q2's leaning re-opens A1 / defers D176 Q3; two triggers | | | | | 5 | V22 HOLDS |
| O2 the pilot baseline pricing must beat is absent | | | | | 6 | V22 HOLDS |
| O3 held fixes (smp04, PAIR look-ahead) vs the goal order | | | | | 7 | V22 PARTLY |
| O4 Q1 amends the agreed A-PLAN step without saying so | | | | | 10 | V22 HOLDS |
| O5 Q3 "does not depend on the frequencies" overstated | | | | | 11 | V22 HOLDS |
| O6 D157 "never a position" mis-states the ruling; D167 A11 exception | | | | | 12 | V22 HOLDS |
| O7 stage-3 ratchet delta unstated | | | | | 13 (SUSP.) | not verified |
| F standing questions | | | | (a), (b) | | — |

## Findings, by consolidated id, with PROPOSED dispositions

No finding is answer-level. Nothing was REFUTED outright; one sub-claim was (OWNER-1's "a stop change
cannot reach the renderers before 1e": today's reply already carries the stop).

### Stage-1 blockers (the build go cannot pass these as written; all are TEXT fixes)

**P1 — the plan/frame/method order is a cycle in today's code** (FIX-2, FIX-3, FIX-8, SLOT-8; V1-V3 HOLD).
Re-checks B2: FAILS / INTRODUCES-NEW. (a) T-FIND's answer today depends on WHO asks: `fd_find` sets
`SF_WINDOW_STOP` (finder.c:938), PAIR requires it (:306), `fd_route` inside Table E's legacy rows never
sets it; witness `[a-z]+[%&][a-z]+` takes E-stmt + R7w walk, while smp20's REPORT site takes PAIR. 1e
deletes the bit "as a stop fact", which moves bytes. (b) Table E reads `def`, hooks and `gphases` (different
for `mf_define` vs `mf_emit`, compose.c:255-258), while the plan call `mf_wdecide` takes no hooks and pcrec's
`window_reply_ask` relies on "the decision reads no frame fact" (emit_dfa.c:7600-7602); rev 2's step 1 lists
form/handoff/site_kind (frame fields by window_site's definition) beside "no frame fact here". (c) D-hors
pre-empts `fd_find` (window.c:1743-1746) and reads T-VERIFY's tested sets; it is in no T-FIND row.
PROPOSED: **FIX-NOW** (design decision, then text). The cheapest byte-identical shape is that the frame and
its legacy rows stay a TEXT-time (phase-2) answer and the reply grows only what is frame-independent; or
the plan call takes frame + hooks + phase set and pcrec's phase-1 askers are listed as changed. Either way:
keep `SF_WINDOW_STOP` through stage 1 (renamed for what it is: "the asker renders PAIR"), put the Horspool
row first in T-FIND's list, after the frame, and drop the claim "T-FIND validity reads T-FRAME's
contracts". Blocks 1e only.

**P2 — B-fn vs B-pair: same method and frame row, two texts** (FIX-7, SLOT-1; V4 HOLDS). `b_fn_holds`
re-walks `fn_rows` BODY (window.c:1673-1683); smp05 renders an `ofsskip__body` function, pr09 an inline
two-stream loop, both PAIR on E-find. Rev 2's 1e deletes "B-fn's reconciliation" while BODY stays a decider.
PROPOSED: **FIX-NOW**: 1e keeps the reconciliation (and `b_fn_holds` leaves the ratchet's delete list), or
the reply carries a renderer field / T-FRAME splits E-find. Blocks 1e only.

**P3 — unit 1a retires two caller-visible denies** (FIX-1 + addendum, SLOT-7; V5 HOLDS). R8 carries
`fd-r8`, R1/R2 carry `fd-ndisp` (options.def:61-67); both are `registry.md` §6¶8a rows, §6¶8b's floor 14
counts them, `emit_sweep.py` ASSERT_ZERO arms use them; R1/R2 are the only `pay` rows behind the public
`mf_finder_pay`. The witness "byte-identical on EVERY arm" cannot hold if they retire (R0/R5 precedent:
unknown options); if they stay they deny nothing. PROPOSED: **FIX-NOW**: shrink 1a to N3 + R3a/R3b/R4 (no
deny, no caller effect), and move R8/R1/R2 + their denies + the pay machinery to a separate step with its
registry hunk (D80), `--list-axes` re-pin and test edits. That keeps 1a a true no-mover.

**P4 — Goal 3's census can neither pass nor fail as written** (FIX-6, SLOT-2, SLOT-6; V6 HOLDS). Rev 2
itself keeps byte-identical second deciders after stage 1 (generic.c's RUN chain, `fn_rows` BODY,
`scan_ok`, the inline ties of S1), so "a second decider that stays byte-identical fails it" is red at every
unit HEAD; "four pick-side tables" counts T-PICK, absent until stage 3 (three after stage 1); `fn_rows`
PREFIX and compose's `arms[]` (frame selector of every non-plan site) are uncounted. And `kit_walk` reach
sees no decider that is a plain loop (`c_plan`, Table B, TIE, `run_member`, translate's rank). PROPOSED:
**FIX-NOW**: a corrected count; a named exception list, each with its retiring trigger; an implementable
census = a committed `decider -> table` map + an argmin-shape grep whose hits must all be mapped + one
sabotage row (a byte-identical copy of `run_member`'s loop must go red).

### Stage-1 hazards (byte identity holds only if one sentence is added)

**S1 — tie and run-member spellings survive** (FIX-5, SLOT-3; V7 HOLDS): translate's run rank (window.c:
1320-1343, ties HIGHER inline), presence's run window (presence.c:183-188, LEFTMOST inline, while
`wf_ties[T_WINDOW]` says "no kit reader"); the presence-member row needs a second comparator shape and an
UNKNOWN-order value. PROPOSED: **FIX-NOW** (add both to 1b/1c reading `wf_ties`, or list them kept).

**S2 — U4's primitive must take a position multiset** (FIX-4; V8 HOLDS, constructed `zzzzzzz~J` moves
`run_window` under a set-shaped primitive). PROPOSED: **FIX-NOW** (one sentence in 1b).

**S3 — PRES ordering double-booked; C-bound unnamed; two grouping rules** (SLOT-4, SLOT-5; V9 HOLDS).
PROPOSED: **FIX-NOW** for SLOT-4 (move "PRES part ordering" to T-PRES with the chain order and
`implied_by`; U10 = Table C + ofsskip's legacy plan); **DOC** for SLOT-5.

### Pricing (now the critical path for smp20, see FREEZE DRIFT)

**C1 — `streams x byte(method)` is undefined and decides smp20 under P** (MEAS-1, SIM-5; V10 HOLDS).
`find.byte` is carded per method (PAIR its own row), C1's own principle puts PAIR's second stream inside
its card, yet the formula multiplies by an undefined `streams`. Reading B (PAIR card = its per-byte cost):
P PAIR 264,694 vs '/' 153,477, '/' wins under P at either hit value; reading A (the script's): turns on
`hit(PAIR)`. PROPOSED: **FIX-NOW** (drop `streams`; `find.byte(m)` = the method's cost per subject byte,
all streams), and recompute §Robustness's table, which under the corrected A2 is the forecast of whether
smp20 is ever fixed.

**C2 — formula gaps** (MEAS-2 `hit(hors)` in no card/prerequisite list; MEAS-5 `verify.cmp`'s 0.5 regime
has no term, today's `verify_cost` carries C_MISPRED; MEAS-3 "exact, once" is not int128 fixed point for
192 of 5,329 alternatives; V11 HOLD). PROPOSED: **FIX-NOW** (name `hit(hors)`; `cmp(form, pass)`; declare
the fixed-point scale and §1.7's rounding name).

**C3 — bands** (MEAS-6 + OWNER-3: qualifiers ordered by worst-case ratio inside the band, against D176 Q5
and guide addenda/kit.md; MEAS-7: comparison band of two prices sharing cards undefined; first priced row's
model error is an unmeasured 0; V11 HOLD). Re-checks A3: PARTLY. PROPOSED: **FIX-NOW** ("qualifiers within
band of the best go to TIE"; band of a comparison = quadrature of coefficient-difference x noise; the
first priced row's model error UNMEASURED, guarded by its own run).

**C4 — noise decides but `values_digest`/no-shadowing exclude it** (MEAS-8; V12 HOLDS). PROPOSED: **DOC**
(stage 2's owed list adds: digest coverage of noise or a refusal of FILE sets sharing a committed id, with
`measures.md` §3.3¶1/§5¶4 and measure_sets §4.1/§1.6 hunks; "§4" corrected to the channel's homes).

**C5 — "zen4-grid1 rev 2" vs spec §8¶1 "a new run as a new id"** (MEAS-9; V13 PARTLY: rev 2 follows D176
Q3's wording and names the fallback). PROPOSED: **DOC**: default to a new id and surface "D176 Q3 /
[MEASURE-SET] vs measures.md §8¶1" to main as the real question.

**C6 — DEFAULTS flip and M2's envelope** (MEAS-10; V14 HOLDS). A bare compile prices nothing until DEFAULTS
names the new set (a default change with census); at M2 the envelope excludes every per-byte cost row,
so priced rows go dark on bare compiles. Under the corrected A2 this decides whether smp20 is fixed for
bare compiles at all. PROPOSED: **FIX-NOW** (one paragraph in §What moves; the M2 interaction as a stated
dependency to main).

**C7 — the key count is the kit's self-report; `consulted` is never set** (MEAS-11; V15 HOLDS). PROPOSED:
**FIX-NOW** (name an independent pcrec-side count, e.g. a python re-price from the stamped set's rows;
"T-PICK sets `consulted`" listed in the first priced row's change).

**C8 — drop-F plant has no reaching witness before the C5-gated class** (MEAS-12). PROPOSED: **DOC**
(per priced row, its own witness or a declared UNREACHED).

**C9 — the SIMD layer** (MEAS-13 HOLDS; OWNER-2 PARTLY). Rule 6 (scalar plans only) has D147 behind it but
contradicts roadmap §0a's owner-agreed "the scalar build and the SIMD build each choose their own
winner"; SIMD-form cards then have no T-PICK reader, and N12's "live when carded" is a priced choice
outside T-PICK. The O-117 consequence is overstated (a route choice). PROPOSED: **owner question** (plain
words: "should a SIMD build be allowed to pick a different search position than the plain build, when its
own measured costs say so?"; leaning: yes, by its own row with SIMD-on evidence, scalar remains the bar);
until answered, **FIX-NOW** drop SIMD-form cards from stage 2 (D77).

**C10 — `enter` survival** (MEAS-14, SUSPECTED). PROPOSED: **PLAN** (stage 2 card design question).
**C11 — regime section** (MEAS-15). PROPOSED: **DOC**.
**C12 — quoted numbers** (MEAS-4, SIM-6; V21 HOLDS: 153,476 not 153,477; "at least 2:1"; the 20 c hit is
R-33's assumption, not plan_cost.def). PROPOSED: **DOC** (round 1's lesson 1 not fully applied).

### Row 1 ONE-STREAM (SUPERSEDED by the corrected A2; carry-overs noted)

**R1** (SIM-1; V17 HOLDS): R-33's sweep covers the default arm + the DEF deny only; on `--engine=vm` smp20
has two NONE non-COVER sites where any smp20 departure lands, and pr09/c04989 do not move. Carry-over:
**FIX-NOW** in general form: every T-PICK row's movers census is computed per arm (vm, both layers,
denies), never from the default-arm sweep alone; smp20's watched-witness reading names its arms.
**R2** (SIM-2; V18 HOLDS): the mass bound admits P-losing stops for k >= 13. **SUPERSEDED** (the bound goes
with the row; a priced departure compares walk vs stream by cards). NOTED as the reason a count-only
bound is unsafe.
**R3** (SIM-3; V19): tie order text vs script. **SUPERSEDED**; carry-over **DOC**: onestream.py is
retired or relabelled with the row.
**R4** (SIM-4; V20 HOLDS): counts pool the 43-pattern DEF deny recompile (1,767 = 1,742 + 25 etc.); "PF
states span 0 on its PARKED alternative" false on 291 sites; "several core positions" false on 740 of
1,454. PROPOSED: **DOC** (RTE-only counts, or "units incl. DEF"; correct the PF sentence).
**R5** (SIM-7, SUSPECTED; V17 side note: smp20 vm's pre-check states '/' while the kit's reqrun body scans
{X,x}): a pick on a pre-check part moves a kit stop pcrec does not scan (`req_run_member` reads
`run_member`). Carry-over: **PLAN** — any T-PICK row states whether it applies on pre-check parts.
**R6** (OWNER-1; V22 PARTLY), **R8** (OWNER-8), **O5** (OWNER-11): **SUPERSEDED** (no hand row; smp20 is a
watched witness; Goal 5 should be rewritten to the corrected A2: watched at every stage, options only at
the last planned step).
**R7** (OWNER-4; V22 HOLDS): D186's first unification target (S3's two stop rules) stays two KEY rows.
Under the corrected A2 its home is the priced row, so: **DOC** — name A-model's one-member preference and
the first priced departure as the meeting point, and say the KEY rows retire there.
**R9** (OWNER-9; V22 HOLDS): D144 item 3 (batch-gate regressions become issue rows) vs D186 (a losing
regime narrows the row). PROPOSED: **DOC** + a one-line ruling for main (D186 governs choice rows).

### Owner and rulings

**O1** (OWNER-5): Q2 re-opened A1 / deferred D176 Q3. **SUPERSEDED** by the corrected A2 ("stage 2 follows
stage 1 directly"); FIX-NOW: delete Q2, state stage 2's trigger once (= stage 1 done).
**O2** (OWNER-6; V22 HOLDS): "the pilot is the baseline any pricing must beat" ([PRICE-BAKEOFF],
pricing_requirements.md) is absent. PROPOSED: **FIX-NOW** (the first priced row's acceptance includes the
pilot comparison; name when the drift gauge is re-read and its cost).
**O3** (OWNER-7; V22 PARTLY): holding smp04's unit change and [PAIR-LOOKAHEAD-TIME] for all of stage 1
under D153 vs Goal 2 > Goal 3. PROPOSED: **owner question** (plain words: "the small fix for the `[a[:b]`
slowdown and the look-ahead measurement: wait for the clean-up, or go first?"; leaning: wait, D153, smp04
is inside the allowance).
**O4** (OWNER-10): Q1 should say it amends the agreed A-PLAN step ("candidates and cards out"); stage 1
lists the roadmap edit. **DOC**.
**O6** (OWNER-12): "never a CHOSEN position" (D157 has pcrec send candidate positions); landmark admission
carries D167 add. 1 A11's exception status. **DOC**.
**O7** (OWNER-13, SUSPECTED): stage-3 ratchet delta for T-PICK. **DOC**.

### F — standing questions (SLOT)

Sibling family: lmwalk, landmark admission, PRES's P2/P4 picks, `precheck-assign-byte` in `arms[]`,
[PRICE-BAKEOFF]. PROPOSED: **PLAN**: move [PICK-IDIOM]'s trigger to the first T-PICK row's landing (now
the first priced row), so the row format is chosen once. Unlocks (with triggers): registered deciders
(stage 1 go; = P4's fix); PRES on the plan call ([MEMFN-UNBOUNDED-SPANS]); non-plan sites as a reduced
vector (next kit request adding an arm); per-target plans (a second class's set); lmwalk priced by the
kit's cards (stage 2's first set). **NOTED**.

## Overall assessment (proposed)

- No answer-level finding. The disposition table is faithful to round 1's rulings (OWNER, every id), and
  most structural fixes hold as text; but the fix-induced lens found that B2's "T-FRAME at plan time"
  and two deletions in 1e close cycles or drop guards in today's code.
- **Stage-1 build go: NOT YET.** Four blockers (P1, P2 in unit 1e; P3 in 1a; P4 the Goal-3 check) and three
  one-sentence hazards (S1-S3), all text fixes, no measurement. Units 1b-1d are buildable once S1-S3 and
  P4 are written; 1a once shrunk (P3); 1e needs the P1 design decision first (recommend: frame stays at
  text time through stage 1).
- **The owner's A2 correction (mid-round) removes row 1** and makes stage 2 the next step after stage 1.
  The pricing section therefore needs C1-C3, C6, C7 before stage 2 is chartered, and C1 is the one
  finding that predicts whether the data path can ever fix smp20 under P.
- A rev 3 is warranted; a further re-check can be narrow (FIX + MEAS lenses on the changed sections).

## PROBED-AND-HELD (by lens; detail in review/)

- FIX: B1's cites (window.c :251-254, :877-878) verbatim; A-floor 1,420 = exact condition; U4 NONE total
  62,500; zero reach of the six inert rows; B4 rows exist; B5 "no pcrec abi event" by readers; C3 KEY/M
  integers and truncation order; C9; E1-E3; A6 quotes. 13 compiles.
- MEAS: onestream.out reproduces byte-identically; `mf_measure` has no noise field; 68 kit rows all
  noise '-'; stamp "" on 4 sampled artifacts; ONE-STREAM read no card; finder_check D/F as described;
  DEFAULTS = `idk zen4-grid1@1`; A1, C5, D5 hold.
- SIM: row 1 from text alone reproduces 1,637/1,056/577/4 units/3 patterns exactly; 381/381 OFS UNSTATED;
  1,420/1,835 from facts; A-empty zero over 3,494 alternatives; 62,500 vs 62,496; E row a function of
  (form, handoff, site_kind, floor) on the default arm; job-588 ratios match; core-position clause
  load-bearing (excludes two `(?m)` non-core '\n' stops).
- SLOT: every U/N id placed once (24); 1a "7 members"; 1b "2-3 variants"; candidate builder carries
  A-model's input (470/470 merged sets equal); T-FRAME = Table E moved; KEY's five rows reproduced
  (1,857/1,432/415/1,420); run member before Table C; Table D walked only on E-find (1,021/1,021).
- OWNER: D186 kinds (4 checks), A1 (4), A2 as at freeze (3), A6 (3); D176 Q1/Q2/Q4/Q5/Q6, D153, D157,
  D147 add. 9, D77, D80, D174, D149, D167 add. 2, D76/D94 agree; every disposition id faithful.

## By-id completeness

FIX 1-8 (+1 addendum) -> P1, P2, P3, P4, S1, S2; MEAS 1-15 -> C1-C12, P-none; SIM 1-7 -> R1-R5, C1, C12;
SLOT 1-8 + (a)(b) -> P1, P2, P3, P4, S1, S3, F; OWNER 1-13 -> R6-R9, O1-O7, C3, C9. Every critic id is in
one consolidated item; 51 raw findings -> 36 items + F.

## Lessons for the guide (proposed)

1. **Fix-induced, phase moves**: when a fix moves a decision to another call or phase (plan time vs text
   time), list that call's INPUTS and check every read the decision makes is among them (FIX-3: Table E
   reads hooks and a phase set the plan call does not take). Add to the fix-induced lens row.
2. **Deleting a row is not "zero reach" alone**: grep the row's deny/option NAMES and the spec rows that
   list them (FIX-1/SLOT-7: two inert rows carried caller-visible denies). Add to the premise or
   fix-induced row.
3. **Population by arm**: COMMON states which arms the copied raw data covers, and critics split every
   count by arm (SIM-1: no vm/SIMD arm; SIM-4: deny recompiles pooled into "sites").
4. **Splitting fix-induced in two** (structure / measurement) for a fix list over ~20 ids worked: both
   halves found INTRODUCES-NEW items with no overlap except at the B2/frame seam.

## Meta (summary; full record in .coord/process.md)

Five opus critics + one opus verifier, all delivered by file (every final reply lost again), no resend or
nudge; critics 21:54-22:05, verifier 22:07-22:18, draft 22:30. The owner's A2 correction landed on main
during the round; the coordinator noticed it only at the post-round freeze re-check (main HEAD moved).

## RULINGS (kit manager, 2026-11-02)

- All PROPOSED dispositions ACCEPTED. The ONE-STREAM findings are superseded by the owner's A2 correction (D186 add. 1 amended: smp20 has no hand row; data resolves it as the first priced departure after stage 2's cards). Rev 3 drops the row.
- Rev 3 also carries the owner's later direction (via main, 2026-11-02 22:30):
  - smp20 is a WATCHED witness read two ways at every stage: blind, as the least-bad pick across subject kinds; and with a text-like --analysis bundle, where it must switch to '/'.
  - No real-text rate dataset now; options are evaluated only at the last planned step.
  - The [BENCH-WITHDATA] bar is a property of the pick: a with-data compile matches or beats blind beyond noise on cells whose subject kind the bundle describes (that scope is PENDING the owner's confirmation).
- C9 and O3 go to the owner (plain words). Until C9 is answered, SIMD-form cards are dropped from stage 2.
- Process change ACCEPTED: freeze the rulings as well as the subject, and report FREEZE DRIFT at hand-back (skill §3 step 1).
