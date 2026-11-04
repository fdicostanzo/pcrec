# kitunits: survey of the memfn kit's choice mechanism (read-only, 2026-11-02)

Subject: main dc6a40dfb (abi 95), memfn/src/ and pcrec's own choosers. Trigger: t588tri_report.md on lane/memfn-k1102. **[F]** marks what I verified by reading the cited code; **[I]** marks inference. Nothing was built or run.

## 0. Short answer

The statement **mostly holds, with one qualification**:
- **What holds:** the kit does reduce to a small set of basic questions. Each is answered in several places, by rules that differ, and every scenario carries its own selection.
- **The qualification:** the remedy cannot be "independent units composed in sequence". Frank's ruling D176 Q1 (decisions.md:9912) already makes "which stop, found how" ONE *joint* priced choice over (alternative x position x method).
- **So the end state is:** shared units (candidate generation, method pricing, verify pricing, rendering) feeding one shared least-cost pick. Today each scenario has its own pick, or none.

## 1. The units

| # | Unit (question) | Inputs | Output |
|---|---|---|---|
| U1 | **Mass**: how often does set S occur? | byte-rate ppm[256] (NONE = cardinality), S | ppm |
| U2 | **Stop choice**: which position (and its set) to search for | spans, sets, core, verify, entry, masses; sometimes a method cost | offset d*, set S* |
| U3 | **Find method**: how to find the next S at offset d | \|S\|, offset sign, site kind, layer, measure keys | memchr, memchr-back, two-stream PAIR, table walk (V1/W64/A3 unbuilt) |
| U4 | **SIMD form** over a find | policy, levels, the BODY row, reach | vrun-w32/w16 rungs, or none |
| U5 | **Verify plan**: which other positions to test, in what order and grouping | the stop, spans, masses, MAX_SET | offset list plus compare grouping |
| U6 | **Compare method** for a group | run bytes, mask, length, denies | words / overlap / bytes / memcmp, with trim/pad/lead |
| U7 | **Set-membership test** | S, an offered table | `T[b]`, `b==k`, or a range chain |
| U8 | **Resume after a miss** | the stop's mass, the window's tested sets | c+1 (D-one) or a Horspool shift (D-hors) |
| U9 | **Presence**: which required members or run window to verify, in what order, or skip | pspans, proof, masses | a link per span |
| U10 | **Alternative choice** (PARKED vs RESEED) | the two alternatives' prices | the chosen alternative |
| U11 | **Landmark admission** | landmark mass, start-set mass, K | yes/no (margin) |
| U12 | **Frame** | form, handoff, whether a legacy row serves | E-func / E-stmt / E-find / E-generic; arm |
| U13 | **Set cover** (OR of lane-testable terms) | S, K, budget | terms; **no renderer consumes it** |
| U14 | **Span skip, mismatch** | the site | always the generic byte loop: no choice exists |

## 2. Where each unit is decided and rendered

| Unit | Decided at | Rendered at |
|---|---|---|
| U1 | kit: `kit_set_mass`/`kit_set_sum` presence.c:81/89, `cube_mass` :66, `window_mass` :101. pcrec: `pcrec_find_set_mass` findings.c:661, `pcrec_find_pick` :643 | n/a |
| U2 | window.c Table A: A-parked :413, A-model :466 (`scan_ok` :446), A-mass :544. Also `run_member` :763, translate's rank :1320, presence.c P3 run scan :173. pcrec: `pcrec_run_pin` kset.c:294, `pcrec_find_run_scan_index` findings.c:745 (read in req.c:779) | through U3's renderers |
| U3 | compose.c `arms[]` :134 walk (pffind.c:158-206 applies); finder `fd_route` finder.c:863 (D1 :282, D1c :287, D1w :293, R7w :322); finder `fd_find` :922 (adds PAIR :306); ofsskip `fn_rows[]` BODY :414 (`pair_holds` :377); precheck.c's own memchr text :284-330 | pffind.c; ofsskip.c (`ofs_pair_text`, fn bodies); window.c `wf_brows` :1694 (B-fn/B-pair/B-memchr/B-walk); precheck.c |
| U4 | ofsskip `fn_rows[]` PREFIX, `prefix_holds` :402 | vrun.c |
| U5 | window.c Table C (`wf_crows`; C-model reuses A-model's greedy pick); presence P3/P4 for pre-check parts | window.c `wf_test_to`; ofsskip `verify_chain`; generic.c |
| U6 | runcmp.c `rc_row_of` :214 (one table) | runcmp.c — **but generic.c:190-209 renders its own per-byte run test** |
| U7 | by table offer | `kit_set_test` (generic.c, shared with window.c `wf_member_of`); ofsskip `verify_chain`; generic `member_test` |
| U8 | window.c Table D: `d_hors_holds` :1592 (mass >= HORS_MIN), else D-one | window.c `wf_d_text` |
| U9 | finder PRES slot (P0/P2/P3/P4/P9) over presence.c `kit_pres_picks`; pcrec req.c and `req_set_leads_own` emit_dfa.c:11044 | precheck.c |
| U10 | window.c Table M (MARGIN :673) | n/a |
| U11 | pcrec `req_landmark_admits` emit_dfa.c:9067 and `pcrec_landmark_margin` :9056; lmwalk.c `lc_rarity` :232; kit shadow presence.c:222 | pcrec |
| U12 | window.c `wf_erows` :1445; compose.c `select_arm` :263 | each row's own file |
| U13 | terms.c `mf_set_terms` (its own costs EQ 6 / CUBE 7 / ARC 9) | none |

### 2a. The same question answered in several places by different rules [F]

1. **Stop choice (U2): three cost models in one table.**
   - A-model (RESEED) admits only one-member walked stops (`scan_ok` :446-449) and prices `C_MEMCHR` plus mass x verify, with a greedy verify set.
   - A-mass (NOENTRY: REPORT/cover) takes the least mass over any non-full core position (:544-562) and prices no method at all.
   - A-parked prices k0 as `C_MEMCHR` if it has one member, else `C_BITMAP` (:421).
   - For `(?i)x/1234`, the OFS site gets A-model and the COVER site gets A-mass. That is the job 588 split.
2. **A-parked's price and its renderer disagree.** A two-member k0 is priced as a bitmap walk, but the actual find depends on the frame:
   - Through E-func/E-stmt, the translated PF site goes through `fd_route`. PAIR cannot hold there: it needs `SF_WINDOW_STOP`, which only `fd_find` sets (:940). So R7w renders a walk.
   - Through E-find, `fd_find` picks PAIR (two memchr streams).
   - Table A "reads no frame fact" (window.c header), so it cannot know which one it priced.
3. **Find method (U3): four deciders.** They are compose `arms[]`, `fd_route` (D1/D1w/R7w), `fd_find` (adds PAIR) and ofsskip `fn_rows` BODY. Their two-byte rules differ:
   - PAIR takes any two bytes at offset >= 0.
   - fn-pair takes only a one-bit cube inside a RUN term (`ofs_fn_applies` :125-131).
   - `fd_route` sites never get PAIR.
   - B-fn (:1673) exists only to reconcile the finder's answer with `fn_rows`' answer.
   - precheck.c writes its own memchr text for presence bytes, outside both tables.
4. **Run scan member: five spellings of one rule.**
   - The five: `pcrec_find_run_scan_index`; `pcrec_run_pin` (exact positions only); presence.c P3 `run_scan` (:173, cube_mass, ties to the rightmost); window.c `run_member` (:763, `kit_set_sum`, TIE_HIGHER); translate's rank (:1320).
   - They are held equal by loud checks, not by sharing: `req_run_member` (emit_dfa.c:1058-1076) fails the compile on disagreement, and the KW-8 census checks the ports.
   - Each spelling restates the tie rule.
5. **Mass (U1): two parallel primitive sets.** pcrec has findings.c; the kit has presence.c with 3-4 internal variants (cube, set, window, capped/uncapped). The pcrec/kit split is deliberate (D157). The kit-internal variants are not.
6. **Resume (U8) is admitted by a mass threshold alone.** `HORS_MIN` is PROVISIONAL and is never priced against the find it replaces. D176 Q2 already rules that Horspool becomes one method in the priced choice.
7. **Landmark admission (U11): three copies.** `req_landmark_admits`, lmwalk's `lc_rarity` (which shares `pcrec_landmark_margin`), and the kit's evidence-only shadow at presence.c:222.
8. **SIMD filter positions (U4) are a second "which positions" answer.**
   - vrun takes KA from `plan_pos` (U2's answer) and KB from `rank_pos[1]`, by ranking order alone.
   - w16 reads KA only, which is why the SIMD-on 588 cell searched only {x,X}.
9. **Run compare (U6) is one table with one bypass.** generic.c renders its own run test and never asks runcmp.
10. **Orphaned units.** `vany.c` (find any of 2-3 bytes) and terms.c (set cover) have no deciding row, so no decider can pick them.

## 3. How scenarios are assembled today

| Scenario | Route | Composes shared units, or its own choice? |
|---|---|---|
| DFA prefilter OFS (pcrec `ofs_window_of`, emit_dfa.c ~6820) | window phase 1, then E-func, then ofsskip `fn_rows` | **Own joint choice.** Tables A x M are "one least-cost choice over (alternative, stop)" (window.c:19) with the method fixed in the price (C_MEMCHR); then `fn_rows` re-decides the method. pcrec's `next_keys` (:7296) routes on the reply |
| PF find (DFA body/hat, hybrid, VM hat seek) | `select_arm` and `fd_route` | Composes U3. The stop is pcrec's span 0 and is never chosen |
| MLINE | `fd_route` D1c | Composes U3 |
| VMRUN (VM literal run) | runcmp_arm | Composes U6 |
| PRE composite | PRES slot (ports) + `wf_parts_prepare` (:1935, A-mass per part) + ofsskip + precheck's own memchr | Mixed: four sources for one site |
| COVER / REPORT | E-find: Table D, then `fd_find` (Table B), then runcmp | Composes U3/U6/U8, but only **after** an unpriced A-mass stop is fixed: the 588 gap |
| LMHIT | finder | Composes U3; admission (U11) is pcrec's |
| STAY / EDGE / VMSPAN / VMSTRIDE, N7 | generic | No choice |

Where the kit enumerates complete solutions and picks one [F]:
- `a_model_choose` (:466) builds a whole greedy verify plan per scan candidate and prices stop plus plan, with the method hard-wired.
- Table M compares two whole alternatives' totals.
- terms.c runs an exhaustive cover search with its own costs.
- Everything else is first-match over one question.

Wrong sequencing [I]: the order A, then D, then B fixes the stop before the method and resume that would price it are known.

## 4. Data and costs

| Cost | Where | Basis | Stated once? |
|---|---|---|---|
| C_MEMCHR 6, C_BITMAP 116 | plan_cost.def | MEASURED on ubuntubudu Zen 1, not the dev box | once; only A-model and A-parked read them |
| C_VERIFY 250, MAX_SET 4 | plan_cost.def | UNMEASURED DEFAULT | MAX_SET is stated twice: it mirrors `PCREC_OFSK_MAX_SET` (limits.def:393) |
| C_ENTER 2000 / C_MISPRED 1500 | plan_cost.def | MEASURED x ASSUMED / DERIVED | once |
| MATERIAL 2/1 | plan_cost.def | ARGUED | once |
| HORS_MIN 145822 | plan_cost.def | PROVISIONAL (one in-sample cell) | once |
| PAIR / walk / memchr method costs | **none** ("no PAIR cost constant"); D1/D1w/PAIR are UNMEASURED DEFAULT, R7w MEASURED | | **absent** |
| tie rules | `wf_ties[]` window.c:80; presence.c `tie_over`; pcrec PICK | mixed | **three tables** |
| cover term costs | terms.c | counted operators | once; nothing consumes them |
| vrun KB count per level | vrun.c | MEASURED-UNOFFICIAL plus ruling | once |
| finder measure keys | finder.c | no deciding row reads one today | n/a |
| LMWALK_K_HIT_UNMEASURED | lmwalk.c | UNMEASURED | pcrec only |

Only scan plus verify is ever priced, and only in Table A's model rows. Method choice is unpriced and first-match by member count. Moving plan_cost.def and the method cards into the measurement set is ruled (D176 Q1/Q3) but not built (plan.md "next").

## 5. pcrec-side choosers of the same questions

- **Run member/pin:** `pcrec_run_pin`, `pcrec_find_run_scan_index` and `_window_start` (findings.c:745/780, read in req.c:766-781). The kit's `run_member` is asked back and must agree.
- **Walked offsets for RESEED:** pcrec's kset walk decides which offsets exist; the kit picks among them.
- **Set-leads:** `req_set_leads_own` (emit_dfa.c:11044) duplicates kit P4.
- **Landmark admission:** emit_dfa.c:9056-9075 and lmwalk.c:232-258 read `pcrec_find_set_mass` directly. lmwalk has its own walk-length model.
- **Route choice:** the FIRST/NEXT CandSel rows (e.g. `next_keys` :7296) choose handoff, scan or landmark walk, partly from the kit's reply. The kit never sees this choice.
- **PF span 0 (start set):** stated by pcrec. The kit never picks another stop for those sites.

## 6. Verdict

**What holds** [F]:
- The kit's work does reduce to a small unit set: U1-U14, with U1/U2/U3/U5/U6/U8 as the core.
- The units are spread out:
  - U2 has 3 kit rules plus 5 run-member spellings (2 of them pcrec's).
  - U3 has 4 deciders plus precheck's own text.
  - U1 has two primitive sets plus variants.
  - Tie rules live in 3 tables.
- Agreement is held by cross-checks and censuses, not by sharing one implementation.
- Scenarios do carry their own choices. 588 is exactly that: OFS gets A-model, COVER gets A-mass. The same pattern gets two stops from two models. Neither model prices the two-stream find that one of them then renders.

**The qualification:**
- "Build up rather than search for a complete solution" is only half right. U2 (stop), U3 (method), U5 (verify) and U8 (resume) depend on each other:
  - The best stop depends on the method's cost.
  - The method depends on the stop's set size (1 = memchr, 2 = PAIR, 3+ = walk).
  - The verify cost depends on which position the stop removed.
  - Horspool replaces the find entirely.
- Fixing each answer in sequence is what produced 588. D176 Q1/Q2 already rules the joint form. So what should be shared is each unit's answers as **priced options**, not its choice.
- Several units are already well-factored and composed: runcmp (U6, used by ofsskip, window, vrun and VMRUN), `kit_walk`, `kit_set_test`, and `fd_find` as E-find's one FIND decider. The damage is concentrated in U2/U3 and their pricing.

**Main obstacles** [I]:
1. **Joint dependence.** Composition has to be a candidate generator, per-method pricers, and one least-cost pick, not a pipeline of first-match tables.
2. **Renderer availability leaks into deciding.** PAIR is gated on `SF_WINDOW_STOP`, fn-pair has a narrower contract, and B-fn exists to reconcile them. Which methods are available depends on the frame (U12), which Table A may not read.
3. **There are no method prices.** The finder picks first-match by member count, and plan_cost.def is Zen 1 data with UNMEASURED, ARGUED and PROVISIONAL rows. The [MEASURE-SET] migration (D176 Q3) comes first.
4. **The pcrec/kit boundary duplicates rules.** Run pins, scan indices, set-leads and landmark admission are computed on both sides and cross-checked. "One set of choices" needs pcrec's readers to *ask* the kit, as `req_run_member` already does. D157 (facts only) and D167 (the landmark origin is pcrec's) limit how far U11 can move.
5. **The legacy E-func/E-stmt translation re-enters the old arm walk.** That walk re-decides U3 under `fd_route`'s rules, so two method deciders survive as long as the legacy rows render.

**Sketch of the unit boundaries** (not a design):
- One candidate generator: positions with their set and mass, across all alternatives and bounded spans (unbounded spans later).
- One mass primitive and one tie table.
- Per-method pricers that each answer "can you find S at d in this frame, and at what cost": memchr, memchr-back, PAIR, walk, Horspool, with SIMD rungs as forms of a method.
- One verify pricer over the remaining positions.
- ONE least-cost pick over (alt x position x method), using the declared tie rows.
- Then first-match renderers keyed by the winning method: Table B's renderer rows, runcmp, the set test.
- Presence (D176 Q4) uses the same generator and mass with a different price.

Files read: memfn/src/{window.c, finder.c, presence.c, ofsskip.c, compose.c, pffind.c, precheck.c, runcmp.c, vrun.c, terms.c, generic.c, mismatch.c, plan_cost.def}; src/gen/{emit_dfa.c, lmwalk.c, memfn_sites.def}; src/core/findings.c; src/facts/kset.c; docs/dev/decisions.md (D176); docs/dev/plan.md ([MEASURE-SET], [MEMFN-PAIRSTOP]); docs/design/memfn/window_site.md §1, §2.2; t588tri_report.md on lane/memfn-k1102.
