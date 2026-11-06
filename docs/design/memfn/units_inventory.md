# The kit's basic-units inventory under D186 (TRIAL)

**Status: INVENTORY under D186 (TRIAL, owner 2026-11-02). Not a design, not a build go.** It
lists what exists today in D186's two kinds (UNIT implementations, CHOICE rows) and what fits
neither. Lane unitinv, 2026-11-02, on lane/memfn-unitinv (main 34c8ed620 merged with the kit
branch). Source: `docs/dev/lanes/kitunits_report.md` (the survey, U1-U14). Every citation was
re-read against the code in this worktree: **[F]** read and verified here; **[I]** inference;
**[U]** could not be verified. Line numbers that moved since the survey are listed in §6.
Context: `docs/dev/lanes/t588tri_report.md`, `bar588_report.md` (job 588),
`docs/design/stream/roadmap.md` §0a and A-PLAN (the choice table is the kit's planning face).

## Goals

Priority order; a lower goal gives way to a higher one.

1. **D186 can classify every change.** Benefits: the owner and the kit manager, who judge each
   optimization against its kind's bar. Measure: every mechanism in memfn/src that decides or
   renders search text appears here as a unit implementation, a row, or a §3 item; zero
   unclassified mechanisms (a reviewer's grep of `kit_walk` tables, `*_choose` and `*_holds`
   finds none missing).
2. **The duplicates are named before the next choice change.** Benefits: whoever writes the next
   row (first: the 588 stop row). Measure: every question answered in more than one place carries
   a ⚑ in §2 and a §4 line with one proposed home.
3. **Per-row evidence is visible.** Benefits: the D186 bar ("no regime loses beyond noise") needs
   to know which rows have regime evidence. Measure: every row in §2 states MEASURED / DERIVED /
   ARGUED / PROVISIONAL / UNMEASURED and, where measured, the box.
4. **Citations are current.** Benefits: the next lane, which starts from this file. Measure:
   every file:line here resolves at this branch's tip; moved ones are listed in §6.

**Non-goals:** no design of the unified table, no pricing model, no code change, no
re-measurement, no ruling on 588 (its options are in t588tri §c).

**Standing questions** (docs/design/CLAUDE.md): (1) measurement regime: NOT RELEVANT as a new
measurement (none is made); the evidence column records each existing constant's box and basis.
(2) independent control: NOT RELEVANT (no check or selection is built). (3) regeneration: NOT
RELEVANT (no table or data file is added).

## 1. Units and their implementations

A UNIT answers one question; an IMPLEMENTATION is a rendering that answers it for a stated case.
"Pure" = renders what it is told; "hides a choice" = picks among forms inside itself (that
choice is then also listed in §2). All memfn/src/ unless a path says otherwise. [F] throughout
except where marked.

| Unit (question) | Implementation | Rendered at | Case handled | Kind |
|---|---|---|---|---|
| **FIND** the next member of S at offset d | memchr forward | pffind.c `pf_memchr_arm` :547, `pf_memchr_bounded_arm` :552; window.c B-memchr; ofsskip.c `memchr_body` (fn-memchr) | \|S\| = 1, offset >= 0 | pure |
| | memchr back | pffind.c `pf_memchr_back_arm` :562; window.c B-memchr (LIBC_BACK) | one context byte below the origin (MLINE) | pure |
| | two memchr streams | ofsskip.c `ofs_pair_text` :279, called by fn-pair's body and window.c :2473 (B-pair) | \|S\| = 2, any two bytes, offset >= 0 | pure |
| | table walk | pffind.c `pf_walk_arm` :557, `pf_walk_bounded_arm` :567; window.c B-walk (C-table or C-own test) | any S | pure |
| | precheck's own memchr | precheck.c :303 (part 0), :324 (later bytes' table loop of memchr) | a pre-check's one-byte parts | pure text, but outside every FIND table (§3 N9) |
| | V1 / W64 / A3 | **none**: finder.c rows R8/R2/R3b pick them, `fd_route` maps them to no arm (:898) | — | no renderer [F]; whether any compile reaches those rows [U] |
| | SIMD: vrun w32 / w16 | vrun.c (`vrun_w16_decl` :437, `vrun_w32_decl` :444), guarded rungs over fn-pair's scalar text | the scanned cube KA plus KB = `rank_pos[1]` (w32); KA only (w16) | **hides a choice** (KB position, §3 N10) |
| | SIMD: find any of 2-3 bytes | vany.c (stand-alone `mf_kernel_find_any`) | K = 2..3 bytes | pure; **no row reaches it** (§3 N12) |
| **SKIP** after a miss (resume) | `c + 1` | window.c `resume_next` (formerly `wf_d_text`'s D-one; no row of its own since span_pick 1e) | always | pure |
| | Horspool shift | window.c `wf_b_render` B-hors (`d_hors_head`/`_next`/`_define`), T-FIND's D-hors row (finder.c; formerly `wf_d_text`) | dense stop over the window's tested sets | pure (its admission is §2 Q7) |
| **SET-MEMBERSHIP** test of one byte | range chain | generic.c `kit_set_test` :106 (ranges OR-ed, `==`, `<=`, `>=`) | any set; shared with window.c `wf_member_of` :2060 | pure |
| | offered table `T[b]` | generic.c `member_test` :133 (pcrec's hook if offered, else `kit_set_test`); window.c C-table/C-own | a set pcrec offers a table for | **hides a choice** (hook first) |
| | ofsskip's verify chain | ofsskip.c `verify_chain` :184 | the offset-skip function's verify | pure [I] |
| **RUN COMPARE** of a literal stretch | words / overlap / bytes / memcmp | runcmp.c rows :108-131, picked by `rc_row_of` :214 | masked >= 2; exact len 3,5-7,9-15; masked fallback; exact fallback | **hides a choice** (a declared row table) |
| | per-byte compare | generic.c :190-209 | the generic row's run terms | pure; **bypasses runcmp** (§4 U8) |
| **VERIFY** the plan's other positions | window `wf_test_to` | window.c :2148 (C-run stretches through runcmp) | E-find's candidate loop | pure (plan from Table C) |
| | offset-skip verify | ofsskip.c `verify_chain` :184 | the E-func/E-stmt legacy text | pure |
| | generic predicate | generic.c (terms joined by `&&`) | the floor | pure |
| **PRESENCE** check of required members | precheck renderers | precheck.c `precheck_arm` :524, `precheck_assign_arm` :541, `precheck_assign_byte_arm` :558 | by handoff and `ret_pred` | **hides a choice** (3 arms by frame + own memchr) |
| **MASS** of a set (frequency) | `kit_set_mass` / `kit_set_sum` | presence.c :81 / :89 | a set over the byte-rate | pure |
| | `cube_mass`, `window_mass` | presence.c :66, :101 | a run cube; a window term | pure (variants, §4 U4) |
| | pcrec's `pcrec_find_set_mass`, `pcrec_find_pick` | src/core/findings.c :661, :643 | pcrec's own readers | pure (pcrec side, D157) |
| **SET COVER** (OR of lane-testable terms) | `mf_set_terms` | terms.c :389 (own costs EQ 6 / CUBE 7 / ARC 9) | S, K, budget | pure; **no caller** in memfn/, src/, tests/ (only the link check) [F] |
| **MISMATCH** (in-place fold) | `mismatch_inplace_arm` | mismatch.c :282 | the in-place fold; other folds go to the generic row | pure [I] |
| **FRAME** (the text's shape) | E-func / E-stmt (legacy translate, then compose's arm walk); E-find; E-generic | window.c `wf_erows` :1449; compose.c `select_arm` :263 | FUNC/RETURN; STMT/ASSIGN/ON_MISS; window plan; floor | **hides a choice** (E-func/E-stmt re-enter the method walk, §3 N5) |

Pure units: FIND's memchr/back/pair/walk texts, D-one, D-hors text, `kit_set_test`, the mass
primitives, `mf_set_terms`, vany. Units hiding a choice: vrun (KB), `member_test` (hook vs own),
runcmp (`rc_row_of`, already a declared table), precheck (arm + own memchr), the frame rows.

## 2. Choices and their rows

Rows are first-match unless stated. Evidence: the row's own basis string or the constant's
provenance in plan_cost.def. ⚑ = this question is also answered elsewhere by a different rule.

**Q1 Which stop (position and set)?** ⚑ (5 table rows + 5 other answers)

| Row | Where | Facts read | Evidence |
|---|---|---|---|
| A-empty | window.c `wf_arows` :638 | an empty meet inside a core | structural |
| A-parked | :640 (`a_parked_holds` :407, `_choose` :413, price :420) | k0 verify-YES core; prices k0 as C_MEMCHR if 1 member else C_BITMAP | C_MEMCHR/C_BITMAP MEASURED on ubuntubudu Zen 1, not the dev box |
| A-model (RESEED) | :642 (`a_model_holds` :451, `a_model_choose` :466, `scan_ok` :446-449) | walked one-member core spans; C_MEMCHR + mass x verify, greedy plan | domain MEASURED (offset_k_skip.md §7.3); C_VERIFY, MAX_SET UNMEASURED DEFAULT |
| A-mass (NOENTRY: REPORT, parts) | :644 (`a_mass_holds` :535, `a_mass_choose` :543, `mass_domain` :529) | least `kit_set_sum` over any non-full core position; **no method price** | 580/581 (REPORT) |
| A-floor | :646 | no core position | structural |
| other answers | `run_member` window.c :763 (TIE_HIGHER over `kit_set_sum`); translate's run rank :1320; presence.c P3 `run_scan` :173 (cube_mass, rightmost tie); pcrec `pcrec_find_run_scan_index` findings.c:745; pcrec `pcrec_run_pin` src/facts/kset.c:294 (exact positions) | | cross-checked, not shared (§4 U2) |

**Q2 Which alternative, PARKED or RESEED?** Table M, window.c `wf_mrows` :708: M-one (one
alternative), MARGIN (`m_margin_holds` :673: RESEED wins at cost x 2 < PARKED x 1, needs both
priced and the RESEED by A-model), M-parked. Evidence: MATERIAL_NUM/DEN ARGUED (offset_k_skip.md
§4.5). Single place.

**Q3 Which find method for S at d?** ⚑ (four deciders)

| Rows | Where | Facts read | Evidence |
|---|---|---|---|
| R8, R3a, R3b, R4, R1, R2 | finder.c `fd_rows` :248-281 | measure keys (`kit.lstar`, `kit.h3a`, `kit.gstar`, `kit.xover`, `kit.block.W64`), call length, history | DERIVED / MEASURED / PROVISIONAL (R3a/b); keys exist in measure_store/zen4-grid1; reach at any compile [U] |
| D1 | :282 | span 0, one member, not a VM attempt seek | UNMEASURED DEFAULT |
| D1c | :287 | context stop (MLINE) | UNMEASURED DEFAULT |
| D1w | :293 | span 0, one member, anywhere else | UNMEASURED DEFAULT |
| PAIR | :306 | two members, **and `SF_WINDOW_STOP`** (set only by `fd_find` :938) | UNMEASURED DEFAULT; "no PAIR cost constant" |
| R7w | :322 | span 0 (the default) | MEASURED (walk ruling, D169 add.) |
| asked by | `fd_route` :863 (PF sites; never PAIR), `fd_find` :922 (E-find; PAIR possible) | | |
| compose arm walk | compose.c `arms[]` :134 via `select_arm` :263, when `fd_route` names no row | each arm's contract | per-arm |
| fn-pair, fn-memchr | ofsskip.c `fn_rows` BODY :415-416 (`pair_holds` :377: a two-member cube in a RUN term, `ofs_fn_applies` :106) | the scanned position's cube | none stated |
| B-fn, B-pair, B-memchr, B-walk | window.c `wf_brows` :1699 (`b_fn_holds` :1672) | the FIND pick + whether fn_rows agrees | renderer rows |

**Q4 SIMD rung or not?** ofsskip.c `fn_rows` PREFIX :419-420 (vrun-w32, vrun-w16;
`prefix_holds` :402: brackets, REACH, OVER fn-pair, APPLIES), OFF unless `-fmemfn-simd`.
Evidence: MEASURED-UNOFFICIAL (kitunits §4; official verdict pending, vrun_bench_request.md).
⚑ for the positions it filters (Q1/Q5, see §3 N10).

**Q5 Which verify plan?** ⚑ Table C, window.c `wf_crows` :942-968 (12 rows by step: C-meet,
C-floor, C-yes, C-bound, C-model, C-none, C-pin, C-stop, C-run, C-table, C-own, C-asc).
C-model reuses A-model's greedy pick (C_VERIFY, MAX_SET UNMEASURED DEFAULT); the others are
structural. Also answered by the PRES slot for pre-check parts (Q9) and by ofsskip's legacy text.

**Q6 Which compare form?** runcmp.c rows :108-131 (words, overlap, bytes, memcmp; `rc_row_of`
:214); overlap's lengths derived from gcc's memcmp decomposition, words/bytes unstated. ⚑
generic.c :190-209 compares per byte without asking.

**Q7 Which resume?** Table D, window.c `wf_drows` :1635: D-hors (`d_hors_holds` :1592,
stop mass >= HORS_MIN), D-one (floor). Evidence: HORS_MIN 145822 PROVISIONAL, one winning cell
(job 581, dev box). D176 Q2 already rules it a priced method in Table A (not built).

**Q8 Which frame?** Table E, window.c `wf_erows` :1449 (E-func, E-stmt, E-find, E-generic;
order stated as "legacy first so today's bytes stay"); non-window sites: compose.c
`select_arm` :263 (REPORT refused there). Evidence: structural (frame facts).

**Q9 Which presence link per span?** finder.c PRES slot :330-349 (P0, P2, P3, P4, P9) over
presence.c `kit_pres_picks` :149; `fd_pres` :984. ⚑ pcrec's req side computes the same picks
(§5).

**Q10 Landmark admission?** ⚑ pcrec `req_landmark_admits` src/gen/emit_dfa.c:9064 over
`pcrec_landmark_margin` :9057; lmwalk.c `lc_rarity` :231 (K = walk + `LMWALK_K_HIT_UNMEASURED`
:35); kit shadow presence.c :222-245 (evidence only). Evidence: margin DERIVED from the
mass model; k_hit UNMEASURED.

**Q11 Which set-test form?** generic.c `member_test` :133 (offered table, else `kit_set_test`);
window.c C-table / C-own. No per-regime evidence; 588's smp04 (`[a[:b]`, 4.475x random) is the
compare chain losing to DEF's 256-entry table: a UNIT-change candidate (t588tri §a).

Totals: 11 questions; 59 table rows (A 5, M 3, FIND 11, pf arms 5, fn BODY 2, B 4, PREFIX 2,
C 12, runcmp 4, D 2, E 4, PRES 5) plus 7 untabled answers (Q1's 5, Q10's 2 live functions).

## 3. Fits neither kind (D186's revisit triggers)

| # | Mechanism | Why neither | What would make it fit |
|---|---|---|---|
| N1 | `a_model_choose` window.c :466 | enumerates a whole greedy verify plan per scan candidate and prices stop+plan with the method hard-wired (C_MEMCHR): a whole-solution search, not a row | Q1 as one row over (position x method) with a verify price per position (D176 Q1); the plan then Table C's |
| N2 | Table M MARGIN :673 | compares two whole alternatives' totals by an ARGUED 2x factor | a row with per-regime evidence for the margin, or the alternative folded into Q1's priced choice |
| N3 | terms.c `mf_set_terms` :389 | exhaustive cover search with its own costs; no caller | a FIND implementation whose rendering a row picks, or retire |
| N4 | `SF_WINDOW_STOP` gating PAIR finder.c :306/:938 | renderer availability stated as a fact: the same stop gets PAIR via `fd_find`, never via `fd_route` | method rows read only stop facts; availability per frame becomes the renderer's contract |
| N5 | B-fn window.c :1672 | exists only to reconcile the FIND pick with fn_rows' BODY pick | one method decider (§4 U3); B rows key on the pick alone |
| N6 | sequencing A -> D -> B, `wf_find_decide` :1719-1755 | stop fixed (Table A) before the resume (:1738) and method (`fd_find` :1747) that would price it; unpriced fixed order | the joint priced choice of D176 Q1/Q2 |
| N7 | HORS_MIN plan_cost.def | threshold from one in-sample cell, never priced against the find it replaces | D176 Q2 (Horspool priced as a method) or per-regime evidence for the threshold |
| N8 | A-parked's price window.c :420 | prices a two-member k0 as C_BITMAP whatever renders it (walk via E-func, PAIR via E-find); Table A reads no frame | method priced by the method actually rendered (U3 unified) |
| N9 | precheck's own memchr :303/:324 | a find method chosen inside a renderer, outside every FIND table | its byte parts asked through the FIND slot |
| N10 | vrun KA/KB vrun.c :28-60 | a second "which positions" answer: KB = `rank_pos[1]` by ranking order, w16 KA only (588's SIMD-on 5.27x) | KA/KB from the plan's stop and first verify position (the window reply) |
| N11 | E-row order window.c :1440-1443 | "legacy rows first so today's bytes stay": byte preservation, not facts or evidence | each frame row conditioned on facts with evidence; legacy retires (A-PLAN split) |
| N12 | vany.c | a unit implementation no row can reach | a FIND row (Q3) with its card, or stays stand-alone product only |
| N13 | plan_cost.def C_MEMCHR/C_BITMAP/C_ENTER | measured on ubuntubudu Zen 1, used on the zen4 dev box: evidence from another regime | [MEASURE-SET] zen4 revision (D176 Q3) |
| N14 | finder rows R8/R2/R3b | pick V1/W64/A3, which `fd_route` cannot render (:898): would refuse if reached | drop, or give each pick a renderer and a card (reach [U]) |

## 4. Duplicates to unify (proposed single home, one line each)

- **U1 smp20, A-model vs A-mass (Q1).** One Table A stop row priced over (position x method) for
  every entry kind, so OFS and COVER pick the same stop for `(?i)x/1234` (D176 Q1).
- **U2 run scan member (Q1, five spellings).** window.c `run_member`, asked by every reader
  (pcrec's `req_run_member` emit_dfa.c:1058 already asks and fails loudly on disagreement).
- **U3 find method (Q3, four deciders + precheck).** The finder's FIND slot asked once per stop on
  stop facts only; compose's arm walk, fn_rows BODY and B-fn become renderers keyed by its pick.
- **U4 mass variants (kit side).** One presence.c mass primitive with a named capped/uncapped
  argument; pcrec's findings.c copy stays (D157 boundary).
- **U5 tie rules (three tables).** window.c `wf_ties` :85; presence.c `tie_over` :128 and pcrec's
  PICK read its rows.
- **U6 landmark admission (Q10).** pcrec's `req_landmark_admits` (the landmark origin is pcrec's,
  D167); the kit's copy stays evidence-only, lmwalk already shares the margin.
- **U7 SIMD filter positions (Q4 vs Q1/Q5).** The window reply's stop and plan.
- **U8 run compare (Q6).** runcmp's `rc_row_of`; generic.c's per-byte test becomes its caller.
- **U9 MAX_SET.** src/core/limits.def `PCREC_OFSK_MAX_SET` :393; plan_cost.def's copy reads it.
- **U10 verify plan (Q5).** Table C for every site; the PRES slot's pre-check part ordering and
  ofsskip's legacy plan read it.

## 5. pcrec-side findings (findings only; main files)

- **Run pin / scan index.** `pcrec_find_run_scan_index` src/core/findings.c:745 (rightmost tie,
  O-60's UTF-8 reason) and `pcrec_find_run_window_start` :780, read in src/facts/req.c:779-781;
  `pcrec_run_pin` src/facts/kset.c:294 (exact positions, rightmost). Agreement with the kit's
  `run_member` is held by `req_run_member` src/gen/emit_dfa.c:1058-1076 (loud) and the KW-8
  census, not by sharing. [F]
- **Landmark admission.** `req_landmark_admits` emit_dfa.c:9064 and `lc_rarity`
  src/gen/lmwalk.c:231 both read `pcrec_find_set_mass` and share `pcrec_landmark_margin` :9057;
  lmwalk adds its own walk-length model with `LMWALK_K_HIT_UNMEASURED` 10 (:35). [F]
- **Set-leads.** `req_set_leads_own` emit_dfa.c:11043 sits under `#ifdef PCREC_CAND_TRACE`: the
  live row reads the kit's P4 (`req_set_leads_applies`), so this copy is a trace-build shadow
  expectation, not a live second decider (the survey listed it as a duplicate). [F]
- **lmwalk.** Its rarity slot is a pcrec-side admission row with an UNMEASURED constant; the kit
  never sees the route choice. [F]
- **Route choice.** `next_keys` emit_dfa.c:7299 (FIRST/NEXT CandSel) chooses handoff, scan or
  landmark walk partly from the kit's reply (`wr_entry`, `wr.reseed` :7319-7320). [F]
- **OFS window statement.** `ofs_window_of` emit_dfa.c:7592 states the walked offsets; pcrec
  decides which offsets exist, the kit picks among them. [F for the function; I for the split]
- **PF span 0.** pcrec states the start set as span 0; no kit row picks another stop for PF
  sites. [I, from `fd_route`'s span-0 rows]

## 6. Citations that moved since the survey (dc6a40dfb -> this tip)

| Survey cite | Now | Survey cite | Now |
|---|---|---|---|
| window.c A-parked :413 | holds :407, choose :413, row :640 | emit_dfa.c `ofs_window_of` ~6820 | :7592 |
| window.c A-mass :544-562 | `a_mass_choose` :543-561 | emit_dfa.c `next_keys` :7296 | :7299 |
| window.c Table M MARGIN :673 | `m_margin_holds` :673, rows :708 | emit_dfa.c `pcrec_landmark_margin` :9056 | :9057 |
| window.c `wf_ties` :80 | enum :79, table :85 | emit_dfa.c `req_landmark_admits` :9067 | :9064 |
| window.c B-fn :1673 | :1672 | emit_dfa.c `req_set_leads_own` :11044 | :11043 |
| ofsskip `ofs_fn_applies` :125-131 | function :106, rule :124-131 | lmwalk.c `lc_rarity` :232 | :231 |
| precheck memchr :284-330 | :303, :324 | "src/gen" req.c:766-781 | src/facts/req.c:779-781 |
| compose.c `arms[]` :134 | :134 (unchanged) | findings.c :643/:661/:745/:780 | unchanged |

Unverified: whether any compile reaches finder rows R8/R1/R2/R3a/R3b/R4 (their keys exist in
measure_store/zen4-grid1; a reach count needs a run, out of scope here); pffind.c:158-206
"applies" ranges were not re-read line by line.

## STATE AT HANDOFF

OWED none. Document lane: no make, no runs, no code edits. Counts: 10 units (FIND, SKIP,
SET-MEMBERSHIP, RUN COMPARE, VERIFY, PRESENCE, MASS, SET COVER, MISMATCH, FRAME) with 25
implementations; 11 choice questions; 59 table rows plus 7 untabled answers; 10 duplicates;
14 neither-kind items.
