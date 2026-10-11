# 2026-10-11 r2 — D6 panel on [LOSS-REVIEW] phase 2 (`docs/dev/optloop/lossreview/fixes.md`)

Three read-only critics, session 108, desk reads at 112b60e9 (no make, no timing): **cause** (opus,
causal attribution), **family** (opus, sibling-of-a-family + general form + unlocks), **rank**
(sonnet, arithmetic + weighting). Full texts: `2026-10-11-r2-lossreview-fixes/`.

**Verdict:** no blocker. The four-family frame and the 94.3 ms total reproduce. Not ready to rank
for Frank: three candidates' mechanisms do not follow from their evidence (1, 3, 6), one candidate
re-proposes a filed and measured mechanism (6 = [OPT-3-RUNEND](a)), the pricing crosses D146's line,
and the ranking claim "1, 3, 5 rank high on every ordering" is false. Every finding ACCEPTED;
revision lane `lrrev` applies them to fixes.md (revision 2) and runs the no-clock instruments.

## Dispositions

| id | sev | finding | disposition |
|---|---|---|---|
| C1 | MAJOR | Cand 1: 3.94M seam calls (not 4.7M) → 7.9-15.8 ms; 11 cells not 10; the 2% refute bar contradicts the 5.7-11.4% modj prediction; specialization gain exists only on 1-char-capture cells (bak-2, phone: 7.26 ms), elsewhere call overhead only; modj also pays an out-of-line `rx_match_anchored` per attempt + 1.34M VM-hat seeks, so "if null then trail" does not follow; Q3's premise is wrong (three fold_agreement checks call `rx_span_match_caseless`). | ACCEPTED. Per-cell % bands; refute = below the band's low end; add a `static noinline` arm on bak-2 (PLT vs specialization); drop the trail inference; Q3 becomes manager's: keep a wrapper or re-home the three checks in the same change. UNLOCK filed in fixes.md: a call-site census of every per-attempt call boundary. |
| C2 | MAJOR | DENSE-SKIP: (iii) is ruled out as the GAP (re2 pays the same chain at 1.62-1.67 ns/B); (i) vs (ii) inseparable on set totals (collinear; 2-param fit, no entry term); json-constant evidence goes AGAINST (i). | ACCEPTED. Per-subject five-arm design (base / plainloop / -fno-start-set / stay / boundary-pair) before cand 5(a)/6 claim the 13.2 ms. The boundary-pair skip `!(T[s[p]] & NW[s[p-1]])` filed as the general form (R4d's pair generalized to classes); its no-clock trigger count runs first. [POS-PARALLEL] loses this 13.2 ms as a customer. |
| C3 | MAJOR | R4d's extrapolation: R-1's baseline is a two-stream masked pair on sparse text; the HIT-RESTART cells are one-stream exact runs on dense text; "50-80% memchr" is circular. | ACCEPTED (also rank 2.3/2.4). Gain UNKNOWN for HIT-RESTART + C3; K101 cells kept; one per-cell twin (R-1's swar in lit-cat's fn-memchr body) owed before the BODY row claims them. Near-noise DENSE cells (x1.26-1.29) named as such. |
| C4 | MAJOR | Cand 6 = [OPT-3-RUNEND](a), priced a net loss on non-periodic text, timed as noise by ARTREV I13; a mass threshold would DECLINE dbnames' shipped stays; the gcov counts cited are total steps. | ACCEPTED. Fold cand 6 into [OPT-3-RUNEND]; reach cut to C5's 0.26 ms + whatever the stay twins show; mover set includes shipped stays; `vm/stayprobe.py` on the three cells (no clock). Family F7 (`stay_len` = 1/(1-mass)) predicts the same break-even. |
| C5 | MINOR | 5(a)'s reach omits mod-j-uc + the bak-1 family; their +3-4% is inside the null band. | ACCEPTED. Add to reach; bak-2's +17.5% is the only D77 witness. |
| C6 | MINOR | Cand 7's gain is ~25 ms, not ~20. | ACCEPTED, labelled derived (M5.b at an older pin). |
| F1 | MAJOR | "Price the form" in pcrec is D146's rejected price market. | ACCEPTED. pcrec prices its CONSUMER side and states density as a FACT; the kit picks the per-hit form. Rewords §1 F1, 5(a), §3 step 6. |
| F2 | MAJOR | The primitive exists: `prefix_k.c` `model_cost`; R4 is not the only density-priced start decision; it lacks a per-stop restart term; `C_MEMCHR`/`C_BITMAP` are kit-form costs left in pcrec. | ACCEPTED. [PRIOR-COST-UNIFY] GENERALIZES `model_cost`. The two kit-form constants (and G1's `memchr_form` density clause) are an open item for that row's design (leaning: move into the kit's choice under D146). |
| F3 | MAJOR | The density channel exists and is empty: `mf_site.cand_ppm`, `mf_term.ppm`; pcrec writes unknown; the kit reads neither. | ACCEPTED. Filling them is the pcrec half of cands 3/5(b): facts only, no movers, no abi. Scheduled AFTER the L1 merge (memfn_sites.c overlap). |
| F4 | MAJOR | FIND rows are already one table (pffind via `PcrecFind`); integration is per site (D63 holds); fixes.md puts SWAR in three tables; "pair" conflates SET pair and POSITION pair. | ACCEPTED. ONE SWAR set/cube FIND row in pffind; OFS BODY/PRE compose it. The kit request is written that way. |
| F5 | MINOR | F1 has eight more members (run_window_start, run_pin, req_pick/req_byte, vm_reseed_cal, prefix_k's singleton gate, `pass < 4`, MIN_SCAN_CHAIN, FIND_FLOOR_PPM; deferpre K=64 unlabelled); G2 is misfiled. | ACCEPTED. Into the [PRIOR-COST-UNIFY] row; prefix_k's singleton gate filed as an UNLOCK (cube FIND row; trigger ci-moskva). |
| F6 | MAJOR | Two families: ADAPTIVE-ARM (RETRY, K105, 5(a)'s dense decline: a compile-time decline repeats hcolon_in's x1.5); SIZE-KNEE/MATERIALITY. | ACCEPTED. 5(a) reshaped as an adaptive arm whose initial state the primitive sets; [ADAPTIVE-ARM] and [SIZE-KNEE] FILED, not scheduled. |
| F7 | MINOR | Cand 6's value is the stay RUN length. | ACCEPTED, merged into C4. |
| F8 | MINOR | The independence model must be labelled. | ACCEPTED. |
| R1 | MAJOR+minor | Arithmetic: 4.7M→3.94M; "90%"→100% by construction (and the DENSE-SKIP overlap note contradicts the table); 10→11 cells; 7 of 88 not 91; cand 5 with/without C1c; median-ratio top-3 sentence; step numbering. | ACCEPTED, all corrected. |
| R2 | MAJOR | Ranking flips with the metric (cand 7 first on ns, cand 2 last; 1 and 3 low on ratio). | ACCEPTED. fixes.md states all three orderings. The weighting rule is a question for Frank (see below). |
| R3 | MAJOR | Unstated overlaps (PAIR-SKIP, ci-moskva, RUN-PICK, qnt-poss-quest, the C1 frameless pool's 26.5 > 17.74 ms); mod-j-uc's 6.5-8 ms has no candidate; remodel overlap with [PRIOR-COST-UNIFY], L1's abi event and the kit's in-flight rows. | ACCEPTED. Overlap table + a "remodel overlap" column (D153). |
| R4 | MAJOR | §5's questions: Q1 is already ruled (D122 add. 3, D147 add. 6); Q2 is unblocked by a compile-only census the manager can run; Q3 and Q5 are the manager's; Q4 must split (DFA-hat half unsupported); the weighting rule is missing. | ACCEPTED. Q1 dropped; attemptcensus run by lane lrrev; Q3/Q5 decided by the manager; Q4 split; weighting question added. |

## For Frank (after revision 2 lands)

- The round's WEIGHTING rule: the manager's lean is owner-actionable and certain first (a cheap
  confirmed step gate), then total ns, with cell count and worst ratio as tie-breaks.
- Q4 (VM-hat half only) and Q6 (round order).
