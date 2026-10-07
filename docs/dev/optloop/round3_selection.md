# [OPTLOOP] round 3 — SELECTED (rulings recorded 2026-10-06, D153)

**STATUS: SELECTED, runs BEHIND THE REMODEL (docs/dev/decisions.md D153).**
Frank's round-3 rulings (2026-10-06) are in "Rulings (D153)" below; the draft
text that follows is kept as written by lane round3sel, with the added
"remodel overlap" column and the questions marked RULED.

## Rulings (D153)

1. **PRINCIPLE ("don't live in a house we're remodeling"; Frank: "it's ok to
   focus on the remodel").** The in-flight REFACTORS take priority over round
   3 until complete: [START-TABLE] C1-C7 + C5b, then refactor B
   ([DEC-FALLBACK], which absorbs the prefilter admission ternary, its Q8),
   and memfn's ZERO-MOVER migration steps (R4c/M1 now; the later migration
   steps in docs/design/memfn/integration.md §22, e.g. R4g M2 PF migrate,
   R4h M3 in-loop migrate). A round-3 row that touches a site under remodel
   sequences AFTER the refactor that owns it. Remodel work has priority for
   lane slots.
2. **Remodel overlap column** added to the table below (the draft missed this
   direction), filled in by the manager.
3. **Q16 RULED.** [NULLABLE-ANCH] MAY run now (refactor B's site is not yet
   under construction; it is one predicate, B later folds the corrected
   predicate). [CTX-PREFILTER] WAITS for B. Net runnable now:
   [ART-POSS-ARMS], [ART-TRAIL-ELIDE] (after POSS-ARMS), [NULLABLE-ANCH].
4. **Procedural questions.** Q1 kanban rule YES. Q2 YES (the 2+3 batch gate
   pins on whatever is alpha-accepted; un-landed gated rows move to round 4's
   gate). Q3 YES: K90 + K91 + [OPT-HYB-RESEED-POLICY] (and K83 once sized)
   filed as ONE retry-slot row [START-DENSE], gated on C7, with one shared
   [MEMFN] request and backup B3. Q4, Q6, Q7 accepted as the draft
   recommends. Q5: keep [U8-PICK] at rank 4 but mark its remodel overlap.
5. **[OPT-ENDTERM]** is now filed in plan.md (the gap noted in section (c) 8
   below is closed).
6. **Bench relay questions** (the five at the end of this file) are OWED TO
   PCRECDEV2 and recorded there; the bench has not been contacted.

# Draft selection for Frank (lane round3sel, 2026-10-06; rulings above)

DRAFT, docs only. Frank ratifies. Rules applied: D119 and its addenda
(cause-grouped, one mechanism per row, a measured gap bar, algorithmic only,
SIMD last, engine-constrained), D125/D137, D144 (two-tier acceptance) and
addendum 3 (rounds 2 and 3 share one batch gate), D151 addenda 1-3 (fold the
start table FIRST), D146/D147 (migrated emitter text is kit work).

**Sources.** (1) Candidate rows already filed in `docs/dev/plan.md`.
(2) The bench findings as pcrec's own docs cite them: `gapreport_2026-10-05.md`
and its judgement, `summaries/2026-10-05-bench-o83-round1.md`, K81-K91 in
`known_issues.md`, and O-84/O-85 as quoted there. (3) The [ARTREV] pilot:
`artrev/report_pilot.md` §5 and `generalize.md`.

**Where round 2 left the gap table.** These readings were taken at the alpha
tier (pcrec-side Linux, pinned). The rounds-2+3 wide bench has not run yet.

- **Gap #1, START-SET**, is mostly closed (`docs/dev/lanes/alphas2_report.md`,
  `alphas3_report.md`):
  - aws: 2.89 -> 0.03 ns/B;
  - level-context: 2.41 -> 0.49 ns/B. Against the bench's jit figure (about
    0.72 ns/B) pcrec would now lead. That is a cross-instrument reading.
  - quoted-delim: 5.61 -> 0.70 ns/B;
  - balanced-parens: 3.70 -> 0.81 ns/B.
- **What is left of it:** stack-frame (x4.85 vs jit), whose bytes stage 3 does
  not change, and two regressions stage 3 introduced (K90, K91).
- **Gap #2, CTX**, is now a ceiling-only residual. Its trio stays HELD.
- **Gap #3, CI**, was cured by the K82 handoff. What remains of it is SIMD
  territory.
- **SEL-LIT** closed as SYNTHETIC ONLY (`sellit_read.md`, O-84).

**What round 3 has to work with:**

- the gaps that stay open: NULLABLE-ANCH, doubled-word, LKA, U8-PICK, CARET;
- the stack-frame row, which waits on the fold;
- round 2's own regressions.

**Round 3's window.** C1-C7 of the start-table fold have not started. They
wait for the kit's R4c, which is in its Mac `make test` now. The Linux verdict
comes by day. C1-C7 then run serially and are days out. Every new start-row
or start-mover is a one-row addition AFTER C7 (start_table.md §4: "each its own
abi event AFTER C7"). Building one before C1 would move the edit set the fold
re-derives on post-R4c main. So round 3a is built only from rows OFF the start
table. Round 3b carries the two start-table rows whose gate (C7) can plausibly
clear inside the window.

**Kanban rule (proposed, Q1).** Work top-down. When a row bails or finishes,
pull the next one. Skip a GATED row whose gate has not cleared, rather than
waiting for it. Then pull the next ungated row, then the backups in order.

## (a) The selection

| rank | row id | src | mechanism (one per row) | measured evidence (cell, number, population) | cost / risk | gate | why this rank | remodel overlap |
|---|---|---|---|---|---|---|---|---|
| **3a-1** | [NULLABLE-ANCH] | 2 | **Anchor-aware nullability in the prefilter admission.** `lang_nullable_declinable` (`select_engine.c:839-861`) declines the hybrid's exact prefilter whenever the language is nullable. That ignores `^`/`$`. An anchored pattern has only one candidate start, and the DFA verdict over that one start still rejects in linear time. | **Bench:** capability `evil-alt-nested` `^(([a-z]+)*)+$` is **x5.98 behind jit** (x37.6 vs re2-longest). `trim-nested-star` `^(\s+)*$` is **x3.00 behind jit** (x1081 vs re2). Both on the primary peer.<br>**Probe on today's main:** both are `RX_ENGINE vm`, `declined-nullable-default`, `RX_VM_PREFILTER none`. The `--no-captures` arm is already a DFA `search-filter` (`docs/dev/f2_rescue_split.md` §3).<br>**Corpus population:** not counted. That is STEP 0. | S-M / M. It is a soundness argument (what "nullable" must mean under anchors), a deny flag, an abi event and the spec hunk. Cheap compile-only census first (Mac OK). | none (engine selection is outside the fold, start_table.md §2.5). Must land before [DEC-FALLBACK]'s STEP 0, see (c). | Largest gap against the PRIMARY peer that no gate blocks. Its cause is located and confirmed on main, and it is classic ReDoS shape, so the realism holds. | **refactor B** ([DEC-FALLBACK], prefilter admission, its Q8). Edits `lang_nullable_declinable` beside the ternary B absorbs; B is not yet under construction, so it runs NOW and B later folds the corrected predicate (Q16 RULED). |
| **3a-2** | [ART-POSS-ARMS] | 3 | **Possessify analysis: two arms widened soundly.** (1) A `\b` follow after a greedy word-pure repeat. (2) A backreference's FIRST, taken as its group's FIRST. | **Bench:** capability `doubled-word` is **x1.93 behind jit** (auto 18.42 ns/B).<br>**Confirmed twin** (ubuntubudu, 7/7 pads): **-57.6%**, 17.39 -> 7.37 ns/B, with no new codegen. That projects past jit's ~9.5.<br>**Population:** 1 bench / 2 corpus (K35; not A07's headline). | S / M. Possessify has a refutation history (U1, U2, the lazy conjunct), so it gets a D6 panel and an extended `run_possdiff.sh` before build. It changes the give-up surface one way (spec sentence plus a K65-style check). | none | The cheapest confirmed win in the pool. The whole effect is a gap in an analysis. It turns a jit loss into a lead. | **none** (`src/opt/possessify.c`; not a start-table or memfn site). |
| **3a-3** | [ART-TRAIL-ELIDE] | 3 | **Untrailed `RX_SET`**, admitted where every read of the slot is dominated by a write in the same attempt and no frame is live across it (a dataflow fact). | **Confirmed only as stacks:** +6 points (b_L3 vs b_L2) and +16 points (a_L3 vs a_L2) on doubled-word. The isolated increment is NOT measured.<br>**Population:** upper bound 66 bench / 1,454 corpus with `RX_SET`; 27 / 623 frameless.<br>**Group it serves:** BACKTRACK, 14 cells at x1.17-x3.00 vs jit. | M / M. STEP 0 is the dominance-fact census plus the single-member twin; the row bails there if the increment is null. Changes the give-up surface (limits.md §3.2/§5 hunk). | **SEQUENCED after 3a-2.** Its alpha base is post-POSS-ARMS, because 3a-2 makes A07 frameless. | The only algorithmic lever on BACKTRACK's per-step cost, with the largest population in the pool. Ranked below 3a-2 because its evidence is an upper bound. | **none** (VM trail; not a migrating search site). |
| **3a-4** | [U8-PICK] | 2 | **The utf8 literal pick** (a ranking inside a row, outside the fold, start_table.md §2.5). STEP 0 is the two-artifact twin `-e byte` vs `-e utf8` of one literal. If the pick defect shows, fix the pick; if not, close. | **Bench:** 10 utf8 cells. pcrec LEADS jit on all of them but trails re2/rust by x1.2-x15.7 (`lit-sharp-s` x15.7 vs rust, auto 0.566 ns/B). | S / L. The twin is compile-plus-time only. | none | Ceiling-only (jit already behind). It ranks here because it is cheap, ungated and may be a defect, not a gap. Bail-prone by design. | **likely refactor A** (landmark pick, [TIE-ALIGN] territory); CONFIRM at its twin step. If the pick sits in a start row it sequences after C7. |
| **3b-5** | [ENG-TACTICS] reverse-inner | 1+3 | **The `rev-inner` / `handoff-rev` rows** (start_table.md §4.1). Find the rarer inner landmark, then walk back over P to the exact start (gates G1-G3). | **Bench:** loglines `stack-frame` is **x4.85 behind jit** (real text; unchanged by stage 3).<br>**[ARTREV] I1, confirmed:** **-72.2%**, 0.455 -> 0.126 ns/B.<br>**Population:** 17 bench (8 at >=8x) / 90 corpus. Soundness model 0 wrong at 10.46.<br>The dup-param-detect twin reads NULL (that cell is at the memchr floor). Frank's 2026-10-06 promotion rests on I1. | M-L / M-H. New `inner_split` fact, a prefix reverse machine (a parameter of the existing builder), a deny flag, an abi event. | **GATED: [START-TABLE] C7 merged**, plus a **[MEMFN] request**: a FIND that resumes at `hit+1`. | Biggest gap x breadth x realism in the pool. It is gated, so it heads 3b. If C7 has not merged when 3b opens, skip it and pull 7. | **A + memfn** (gated): a new `cand_rows[]` row after C7, and a FIND resuming at `hit+1` is a kit request. |
| **3b-6** | K90 + K91 + [OPT-HYB-RESEED-POLICY] | 2+1 | **The RETRY slot's adaptive rule, carried to the VM-only and DFA-hat routes** (start_table.md §4.3), plus the first-position peel as one shared seek property. RESEED-POLICY's "halve, don't reset" disarm is the same block rule's tuning. | **Our own round-2 regressions:**<br>- VM hat: quoted-delim dense +0.84 ns/B; `a(\w)\1` d33 +0.53; hit-at-0 short calls +14..+17 ns.<br>- DFA hat: ctx-* +4.0..+5.9%; syslogbase +3..6%; `\b[0-9a-f]{8}\b` +7%; per-call +3..+9 ns.<br>**RESEED-POLICY:** `a?+a` 350 re-seeds on t-64k, x1.086 (Mac scratch, directional). | M / M. No new mechanism: route bits on R4/R5 plus a conjunct. The crossover is re-measured for the seek (D149: labelled UNMEASURED until it is). | **GATED: C7.** The peel in `emit_req_handoff` is a **kit** change after R4c (the S464 half). | Repairs this cycle's own losses, with no new mechanism. The interim lever `-fno-start-set` gives the wins back, so it ranks below the new gap. | **A + memfn** (gated): the RETRY slot (R4/R5) after C7; the peel in `emit_req_handoff` is kit text after R4c. |
| **3b-7** | [CTX-PREFILTER] (the LKA group) | 1+2 | **The strongest necessary one-character condition from a positive lookaround, in the PREFILTER only.** STEP 1 is a profile and a hand twin on `lka-pos`, to see whether candidate removal converts into time. | **Bench:** syntax `lka-pos`/`lka-verb` `item(?= done)` is **x3.21 behind jit** (auto 0.380 ns/B; synthetic). `lkb-neg` is x3.47 behind jit (negative, NOT covered).<br>**Row's re-open condition:** "after RESEED lands, a lookaround cell still loses". It is met literally at O-83.<br>**Joint measurement:** 59% of live candidates removed at 1.58/KB. | S-M / L-M. A T3 row pair, exact before approximate. | none (NFA lowering into the prefilter DFA). | A primary-peer gap, but synthetic, and the row's own evidence says the loss may be per-byte, not per-candidate. Bail-prone; the profile decides it before any build. | **refactor B** (prefilter admission): WAITS for B (Q16 RULED). |
| **3b-8** | K81 | 2 | **The view-tolerant scan edge's re-entry term** on mixed-run subjects. Hypothesis only: the edge is re-entered on every run and pays its entry term each time. | **Alpha (Linux, pinned):** `base10num-grok` mix4k 6031 -> 10233 ns/call (+70%), hex4k +85%; `upto-1024` mix4k +36%.<br>**Bench:** reproduces only the entry term, `floor` +1.1..+1.6 ns per subject on four sets. The mix/hex regime has no bench subject (O-83). | S-M / L. Diagnose from the emitted text first. | none (scan edges are outside the fold). Check the [MEMFN] delegation status of the edge site first (memfn/CLAUDE.md). | Round 1's open regression. Its real-scale witness exists only on lane subjects (still a measured twin, which meets the bar). Last of the eight. | **memfn M3** (R4h: the scan edge's edge loop); check the edge site's delegation status first, and sequence after R4h if the loop has migrated. |
| B1 | [ART-VMCTX-START] | 3 | **A `ctx` column on N7** (start_table.md §4.2): the leading `\b` as a previous-byte predicate. | -22.3% / -22.9% (two reviewers); population 2 bench / 1 corpus. Unmeasured on top of 3a-2's frameless form. | S-M / L-M; abi event | **GATED: C7**, plus a **[MEMFN] request** (a two-position FIND predicate) | Small population, and its effect overlaps 3a-2's. Promote it only after 3a-2's alpha, if doubled-word still trails. | **A + memfn** (gated): an N7 column on the start table (C7) plus a two-position FIND kit request. |
| B2 | [ENG-LOOK] | 1 | **Fixed-width lookaround by product construction** (lookbehind in the forward machine). | STEP 0 census: 98 fixed-width occurrences of 2-4 characters; state growth is not the blocker. The bench lever would be `lkb-neg` x3.47. Whether that pattern's lookbehind is fixed width is unknown (bench question 4). | M-L / M; a D6 panel on the lookahead attachment point first | none | The LKA alternative if 3b-7's profile says the loss is per-byte. One mechanism at a time, so never both. | **none** (`src/ir` product construction; not a start-table or memfn site). |
| B3 | dense-gate trio: K85 + [K88-HANDOFF-DENSE] + [REQ-HANDOFF-L1] | 1+2 | **A gate that never rejects on dense text still pays its call.** | K85 `cls-n-uc` +0.023..+0.036 ns/B (>=15x its floor). K88 `mat-l31` +0.149 ns/B and `v-us-zip-plus4` +0.88 ns/call. ns-scale throughout. | S each, but the text is migrated | **GATED: C7**, and **kit work after R4c** (the PRE site and the `emit_req_handoff` split) | Small absolute deltas. It is the same family as 3b-6's peel and can ride it as one kit request. | **A + memfn** (gated): the PRE site and `emit_req_handoff` split are kit text after R4c; rides 3b-6's single request. |
| B4 | [OPT-3-RUNEND] (b) | 1 | **A two-byte transition table** for small machines (states x ncls^2 <= ~16K). | Priced only. The non-periodic subject it needed now exists (O-82 A1: email `t-d-prose-sparse-addrs`). (a) generalised read NOISE in ARTREV I13. | S twin / L | none | Pull it only if 3a and 3b drain. The twin decides it. | **none** (the DFA transition table, not a search site; M3 owns the in-loop class runs, not the transition loop). |

## (b) Considered and NOT selected

**Closed in rounds 1-2. Not repeated.**

- [OPT-HYB-RESEED-FORM]: done; A2 was dropped.
- [OPT-LITSCAN] S4 with [WORD-FOLD]: done; C3 kept.
- [OPT-VEDGE]: done; its regression is K81.
- [SEL-SIZE]: refuted.
- K82: closed as fixed.
- K87: closed, not a defect (layout).
- SEL-LIT: synthetic only.
- START-SET stages 0-3 ([OPT-FIRSTSET]/[OPT-VMSEED]): landed. Its `cand_rows[]` rename now lives inside [START-TABLE] C3.

**Not selected now.**

- [OPT-HYB-RESEED-XCALL]: HELD (xcall.md, reaches 1 of 14 cells). It sits on the RETRY slot (C7), and 3b-6 is the round's RETRY row.
- K83: clang only, and no bench cell carries clang. RETRY slot, gated on C7. The first step (clang disassembly) can be a side item.
- [SEL-COST], remaining buckets: no bench-ranked cell after SEL-LIT. Its post-build rows should land in [DEC-FALLBACK]'s table (refactor B, after C7).
- [OPT-ATTEMPT-SPLIT] / [ENG-ABS-CARET]: one witness corpus-wide (concat-sqli, a ceiling gap vs re2-longest only).
- [ENG-ISL-S2]: auto already routes class tails via the DFA (<=0.5%). No trigger.
- [OPT-REVEND]: zero bench population. It is a WINDOW-slot row, so after C7.
- [OPT-A]: on stack-frame it is subsumed by 3b-5. Its I12 residual: only 3 of 21 bench cells are predicted cheaper.
- [OPT-VMSEED] stage 4: filed, not planned. A FIRST-slot row, after C7.
- [TIE-ALIGN]: a form mover after C7, gated on D119's bench bar.
- [START-D1]/[START-D2]/[START-D2B]: after C7; D-1 is measured-gated.
- [OPT-ENDWIN-ENC]: noise-scale (D144 addendum 1), and a WINDOW slot.
- [OPT-5-PERIODK]: Frank ruled it open with no measured need; the one witness is already DFA-fast.
- CTX trio ([ART-HYB-COUNTED], I13, [ART-LAZY-FRAMELESS]): HELD until a hit-weighted cell exists. Stage 3 closed CTX's main cell (-80%).
- [ART-START-MARK]: dense-only, cell NOISE, subsumed by 3b-5.
- I9 / I10 ([OPT-B] notes): codegen-micro (D119).
- [CAPS-VIEW-RERENDER] / [CAPTURES-DFA-MB]: measurement residuals, not optimizations.
- [OPT-VMLIT], [OPT-NEG], [OPT-ALTHASH]: no measured cell. SEL-LIT closed the litrun evidence as synthetic.
- [OPT-SIMD] / [SIMD-META] / SCAN-SIMD / WIDE-ALT: SIMD last (D119, D147 addendum 7). The kit's two-byte kernels are the eventual lever.
- [ENG-COUNT], [ENG-CLAMP], [ENG-CUT], [ENG-DIRECT], [ENG-THIN], [ENG-PGO]: no current bench cell named in the gap reports.
- [OPT-C], [OPT-D], [XART-TABLES], [EMIT-ALIGN], [CLS-FOLD-WAF744]: not throughput rows, untriggered, or boonies.
- [DEC-FALLBACK], [DEC-POSDOM]: refactors and families, not optimizations. B runs after A's C7.
- BACKTRACK as a group: D119 FUNDAMENTAL. Only 3a-3 touches its per-step cost.

## (c) Cause-group conflicts (same table or site)

1. **The start table** (`dfa_pfs[]`, `req_admits[]`, `req_uses[]` and
   `pcrec_reseed_rows[]`, which fold into ONE `cand_rows[]`):
   - **The rows that wait for C7:** 3b-5, 3b-6, B1, B3, [OPT-HYB-RESEED-XCALL],
     K83, [OPT-REVEND], [OPT-A], VMSEED stage 4, [TIE-ALIGN] and START-D*.
     None of them is built before C1, and each lands as a one-row addition with
     its own abi event.
   - **3b-5 and 3b-6 are different slots** (NEXT/FIRST vs RETRY). Both can
     follow C7 in either order, but each needs its own alpha base.
2. **The RETRY slot alone.** K90 L1/L2, K91, [OPT-HYB-RESEED-POLICY] and K83
   all edit R4/R5 and their block rule. That makes them ONE mechanism and one
   row (3b-6). Never build them as separate rows (general-mechanisms rule).
3. **memfn after R4c.** The search TEXT of the offset-skip trio and of the
   composite PRE site moves behind the kit. So does the kit half of
   `emit_req_handoff` (S464). Each item below therefore needs a **[MEMFN]
   request** (`memfn/docs/requests.md`); its start DECISION reads stay with
   pcrec:
   - 3b-6's peel at F1;
   - B3 (K85's set-leads `memchr`, K88, REQ-HANDOFF-L1);
   - 3b-5's FIND resuming at `hit+1`;
   - B1's two-position FIND.

   3b-6 and B3 should be ONE request: one shared helper for the seek-peel and
   the dense gate.
4. **Prefilter admission and refactor B.** 3a-1 edits the predicate
   `lang_nullable_declinable` at `select_engine.c:839-861`, right beside the
   admission ternary at `:862` that [DEC-FALLBACK] absorbs (its Q8). Land 3a-1
   before B's STEP 0 census, which runs after C7, so B folds the new conjunct
   as an input. Its alpha also feeds [SEL-COST] §4.
5. **One cell, three rows: doubled-word.** The order is 3a-2 ([ART-POSS-ARMS]),
   then 3a-3 ([ART-TRAIL-ELIDE]), then B1 ([ART-VMCTX-START]). Each alpha is
   measured on its predecessor's output. That is the A09 L4 lesson: a stack
   hides a member that loses in its own regime.
6. **[ART-POSS-ARMS] and reverse-inner's G1.** G1 excludes possessive parts of
   P. So 3a-2 would take doubled-word-shaped patterns out of 3b-5's reach,
   unless G1 reads the PRE-possessify tree (D151 "noted interaction"). Decide
   this in 3a-2's D6 panel, before 3b-5 is designed further (Q4).
7. **LKA has two levers**, 3b-7 ([CTX-PREFILTER]) and B2 ([ENG-LOOK]). They
   are alternatives. 3b-7's profile picks one, and only one is built.
8. **The view-edge site.** K81 (3b-8) shares it with two other causes:
   [OPT-ENDTERM], the size half's second mechanism, and the `\z` reverse-pass
   cause that [SEL-SIZE] named.
   - **[OPT-ENDTERM] HAD NO PLAN ROW (now FILED, D153; cross-ref K81).** K81 (`known_issues.md:188`) and
     `plan_completed.md`'s [OPT-VEDGE] entry both call it "a separate filed
     row", but `grep -c '\[OPT-ENDTERM\]' docs/dev/plan.md` returns 0.
   - File it before K81 is designed, so that a K81 fix does not pre-empt it.
     This is a housekeeping item for the manager, the same shape as round 2's
     NULLABLE-ANCH/U8-PICK filing.

## (d) Questions for Frank

1. **The kanban rule.** **RULED YES (D153).** Work top-down. Skip (never wait on) a GATED row whose
   gate has not cleared. Pull the next ungated row, then the backups in order.
   **Recommend: yes.**
2. **The 2+3 batch gate and the fold.** **RULED YES (D153).** Pin the shared batch gate on main after
   3a plus whatever part of 3b is alpha-accepted. Any gated row not yet landed
   moves to round 4's gate instead of holding this one. **Recommend: yes.** It
   keeps the gate from waiting on C1-C7.
3. **3b-6 as ONE row.** **RULED YES (D153): row [START-DENSE].** File K90 + K91 + [OPT-HYB-RESEED-POLICY] (+ K83's
   anchored row when sized) as one RETRY-slot row, e.g. `[START-DENSE]`, with
   the peel as one kit request shared with B3. **Recommend: yes.**
   start_table.md §4.3 already designs it as one edge on two rows.
4. **The possessify / G1 interaction.** **RULED: accepted as recommended (D153).** **Recommend:** 3b-5's G1 reads the
   PRE-possessify tree (sound, because possessify only rewrites
   answer-preserving shapes). Record it in 3a-2's brief so its D6 panel checks
   it.
5. **[U8-PICK] at rank 4 **RULED: keep, remodel overlap marked (D153).**, though pcrec leads jit.** It is ceiling-only, and
   D144 addendum 2 makes jit the primary peer. **Recommend: keep it at 4.** Its
   STEP 0 costs one twin and may expose a defect. If it shows no pick defect,
   close it at once and pull 3b.
6. **[ART-TRAIL-ELIDE] against **RULED: accepted as recommended (D153).** D119's "BACKTRACK is fundamental".**
   **Recommend: admit it as algorithmic.** A dataflow fact removes trail work
   wholesale; it is not a re-spelling. The gate is its STEP 0 isolated
   increment clearing the floor on Linux.
7. **[NULLABLE-ANCH]'s scope.** **RULED: accepted as recommended (D153).** **Recommend:** the row is the anchor-aware
   nullability predicate ONLY. Re-using the `--no-captures` DFA
   `search-filter` as a match-here verdict in front of the captures VM is a
   different mechanism ([CAPTURES-DFA-MB]'s territory). File it separately if
   the census shows the prefilter alone does not close x5.98.

**Bench-only questions to relay (via pcrecdev2; no inbox entry without a ruling). OWED TO PCRECDEV2 (recorded 2026-10-06, D153; the bench has NOT been contacted):**

1. At the rounds-2+3 wide bench, re-read the stage-2/3 cells on the bench's own
   instrument: aws, quoted-delim, balanced-parens, level-context, stack-frame,
   and `lka-pos`/`lka-verb`/`lkb-neg` (did the VM hat move them?). This tells
   whether START-SET and CTX close at bench grade.
2. The subject composition of `evil-alt-nested` / `trim-nested-star`
   (near-miss vs matching, throughput vs short), so 3a-1's predicted win can be
   stated before the build.
3. Whether a real-text mixed-run `(?:P)\z` subject exists or is wanted (K81 has
   none on the bench).
4. Is `lkb-neg`'s lookbehind fixed width, and of what length (B2's reach)?
5. Is a hit-weighted `ctx-*` cell planned? That is the CTX trio's HOLD
   condition; O-85 already gives the short-call density.

**Bench answers (pcrecdev2, 2026-10-07, read from bench master 21aa69a, nothing measured):**
1. YES, at the [B124] AFTER window. The cells sit in four sets: litrun (aws, plus capability's `sec-aws-key`), capability (quoted-delim, balanced-parens), loglines (level-context, stack-frame) and syntax (lka-pos, lka-verb, lkb-neg). The bench will propose a window to Frank, once I-133 names the pin: those four sets × {auto, vm, `-fno-start-set` deny arm}. The read is cross-pin against c4c70f2c, so only the same-pin deny arm isolates the VM hat.
2. evil-alt-nested `^(([a-z]+)*)+$` and trim-nested-star `^(\s+)*$` are capability patterns, timed on search_short and throughput only. On search_short they are mostly nomatch (5/68 and 1/74), with one near-miss each, capped at ≤20 B by design (NOTES.md P5). Throughput is 3 nomatch subjects, rejected at once by `^`. 3a-1's predicted win must therefore be stated for SHORT NOMATCH. A long near-miss would be a new subject in a new set version (Frank).
3. NO real-text mixed-run `(?:P)\z` subject exists; only bounded has the match regime, over synthetic runs. One is buildable through a version bump (Frank's call) — K81's witness gap stays open until someone asks.
4. lkb-neg = `(?<!item )done`, fixed width, 5 bytes (PCRE2 max_lookbehind 5).
5. A hit-weighted ctx-* cell is NOT PLANNED. The CTX trio's HOLD condition therefore stays unmet. Releasing it means sending the bench a shape (hit share, subject length) to put to Frank as a [Bn].
