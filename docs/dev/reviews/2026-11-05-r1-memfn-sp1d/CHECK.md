# CHECK lens — crit-memfn-sp1d (subject e9e5f035e)

Method: copies of memfn/src planted under CHECK/<plant>/, fixture built one gcc line per file as run_finder.sh does,
`--purity` and `--purity-control` run (control compared with the unplanted copy CHECK/base). Scripts: CHECK/plant.sh,
build.sh, sab.sh, cmp.sh, wit.py. run_finder.sh was run ONCE from the review tree: rc 0, `checks passed: 2266 / failed: 0`,
`purity: 287 >= floor 287`, `purity plant: RED (80 checks failed)`, `purity control: the plant is reached`.
`python3 -I scripts/m6read_check_sab_anchors.py` (review tree's copy): "sabotages checked: 1102 (1143 anchor sites) / all anchors resolve".

## FINDINGS

### CHECK-1  decider_census backstop does not see a twin argmin written against kit_pick (the shape it was re-aimed for) — CONFIRMED
- severity: maintenance (a K35 hole in a failing-direction check); effort XS-S; blast: tests/memfn/decider_census.py only.
- BACKSTOP shapes `< bm`, `< lo`, `< b.mass`, `< after->mass`, `< wl`, `< inc` match **0 lines** in the subject
  (`grep -F` over memfn/src/*.{c,h,def}); `< best` matches only a comment and `i < best_n`. The only live argmin
  shape is `pick_takes(` (8 lines, all kit_pick_takes' own definition, prototype and callers) plus `kit_walk(`, `tie_takes`, `TIE_`.
  The sp1c review's F9 ("dead backstops ... replace with live shapes", FIX-NOW) was NOT re-done at 1d: 1d replaced the
  compares with a call and ADDED `pick_takes(`, but left six dead shapes in the list (the header/tsv still count them as guards).
- Repro (census run with `--src` a copy of memfn/src plus one UNLISTED function appended to window.c holding
  `kit_pick b = KIT_PICK_NONE; for (...) { <LINE> }`), `python3 -I tests/memfn/decider_census.py --root <review tree> --src <copy> --no-plants`:
  - `if (b.pos < 0 || v[j] <= b.v) b = ...`  (the `<=` twin the brief names)           -> checks failed: 0   SILENT (green)
  - `if (b.pos < 0 || v[j] < b.v) b = ...`                                               -> checks failed: 0   green
  - `... || (v[j] == b.v && j > b.key)` (own tie)                                        -> checks failed: 0   green
  - `unsigned long long mass = v[j]; if (b.pos < 0 || mass < b.v)`                       -> checks failed: 0   green
  - same loop spelled `v[j] < best.v` / `bm = b.v; v[j] < bm` / a `/* TIE_ */` comment   -> RED (spelling matched a dead-but-still-listed shape by accident)
  So a re-spelling to `.v` compares (kit_pick's own field names, the very spelling S1095's SABOTAGE line uses:
  `b.pos < 0 || c.v < b.v`) is invisible. Observed vs expected: expected RED "decider shape outside every census member".
- The three PLANTS (window.c `kit_pick_takes(&best, p->mass`, presence.c `kit_pick_takes(&bw, wm`, window.c `kit_pick_takes(&b, c.v`)
  are byte-identical copies of loops that ASK kit_pick_takes: the backstop fires on them because their text contains the
  backstop shape `pick_takes(`, i.e. the plant shares its source with the thing it controls (learnings §3). They show that
  a *conforming* twin is flagged as unlisted; they say nothing about a twin that bypasses the one relation, which is the
  hazard 1d's text names ("every argmin asks the one before-relation"). The plants' own re-aim comment says the call "stands in the backstop for the compares it replaced"; it does not stand in for the bypass.
- HIT_FLOOR stays 30 against 37 live hits (7 of slack, vs MEMBER_COUNT's exact 52): 7 hit lines can vanish unnoticed. The tsv/py comment says "so 30 holds".
- Suggest: replace the dead shapes by live ones that a bypass would have to use (`.v <`/`< b.v`/`<= b.v`/`->v <`/`b.pos < 0`), keep one plant per
  shape that does NOT contain `pick_takes(` (a `<=` twin), set HIT_FLOOR to the exact live count.

### CHECK-2  Purity harness: four decision rows have no reply that depends on them (a plant on them is invisible) — CONFIRMED
- severity: answer (harness coverage); effort S (add sites); blast: tests/memfn/arm_fixtures.c.
- The header says the sites "reach every Table A row but A-empty and A-floor's floor-only path (A-mass, A-parked, A-model, MARGIN's two
  alternatives) and the run member (a verify-YES run R)". Plants keyed on `art->nsites` (hold iff nsites == 0), and — to show reach — the same rows
  DROPPED UNCONDITIONALLY (no art read), each run through `--purity` and `--purity-control` vs base:
  | row (window.c)                              | nsites plant | unconditional change | verdict |
  |---|---|---|---|
  | C-model (`c_model_holds`; greedy picks)      | GREEN, control same | GREEN, control same | no site ever has a non-empty pick: both replies "plan=0/0" for sites 2,3 in both rate regimes |
  | run_member `exact` (verify-NO run, `int exact = r->verify == MF_VERIFY_NO`) | GREEN | GREEN | no site states a verify-NO run (declared in the header, but the 1d witness text says "the run member", not "a verify-YES run member") |
  | C-floor (`c_floor_holds`, no-stop path)      | GREEN | GREEN | declared unreached (A-floor) |
  | M-parked (`m_parked_holds`, MARGIN fails)    | GREEN, control same | n/a | the header claims "MARGIN's two alternatives": only the RESEED-wins branch (site 3) is exercised; no two-alternative site where PARKED wins |
  A KEY/M/T-VERIFY row of these four keyed on nsites (or any art state) passes every purity check. Of the 3 unreached rows, M-parked and C-model are
  ordinary shipped behaviour (the common 'parked baseline wins' and the prefix_k picks), not exotic. Repro: CHECK/p_mparked, p_cmodel, p_cfloor,
  p_runmem, u_cmodel_off, u_exact0, u_cfloor_off (`build.sh NAME` output: "purity rc=0 ... CONTROL: same (not reached)").
- Clause of rev 5.2's 1d witness not honoured here: "its plant ... CONTROL: the plant moves a reply on the unharnessed fixture" is honoured for the one in-tree plant, but the
  population of rows a plant COULD be placed on and reach is not counted (K35): only the A-mass row is planted; there is no per-row reach floor.

### CHECK-3  In-tree plant is an A-table `holds` edit, not "a KEY or M row"; only one row is planted — SUSPECTED/minor (doc)
- run_finder.sh plants `any_stop && !x->d->art->nsites` in `a_mass_holds` (Table A). rev 5.2 1d: "a KEY or M row that changes an answer with nsites". Table A
  rows ARE the KEY rows of this family in the doc's vocabulary only if KEY = Table A; M is never planted in the tree.
  I verified the harness catches an M plant (p_margin: 40 failed, site 3, control moves) and the others below, so this is about what is *kept* green, not a current hole.
- Mild: the control compares the printed replies of the plant vs base (`! cmp -s`) after an empty-log guard on the base only; a plant fixture that crashed
  before printing would read "control moves". Cheap guard: require the plant log non-empty too (XS).

### CHECK-4  S1096 is not reproduced as caught by emitted bytes; its named witness does not reach the site — SUSPECTED
- severity: maintenance/check-adequacy; effort S to resolve (needs the candoracle trace build I may not run).
- Plant = S1096's own SAB_BEFORE/SAB_AFTER applied (tests/mech via python exact-once replace, count 1 each) to a copy of presence.c; object swapped into a copy of build/libpcrec.a; cli/main.c relinked (CHECK/S1096/pcrec; gcc rc 0).
  Compares vs build/pcrec, emitted C under the same basename x.c in two dirs, `--features all`:
  - the named witness `(?i:x)abcdefg(?i:y)` default / `-e utf8`: SAME (and an instrumented presence.c shows the window loop (`for w`) is entered **0 times** for it: run length 9 yields no
    `n > MF_PRES_WINDOW` candidates; WCAND count 0). `--analysis uniform` is refused by the base compiler (rb=1), so no probe there.
  - all 87 lines of tests/codegen/cand_oracle_witnesses.tsv (the suite SAB_SUITES=candoracle runs): **87 SAME, 0 LOUD, 0 SILENT-MOVE**; the 28 lines with pattern length >= 9 reach the window loop 0 times (instrumented build).
  - a pattern that does tie-reach the loop (`x(?i:eeeeeeeeeeeqeeeeeeeeeee)y`, default prior, 63-301 tied windows): plant -> LOUD (rc 1, "the memfn kit refused a site: mf_define: the pre-check's parts are not its pr...", pcrec's own cross-check), `-e utf8`: SAME; `(?i:x)eeeeeeeeeeeqeeeeeeeeeee(?i:y)`: SAME default, LOUD on --engine=vm; `x(?i:...)yzz`: SAME.
  So the plant is LOUD where reached (good: a silent move would be worse) but the row's declared catcher `candoracle` (SAB_DOC_FIGURE "5fail/177pass DETECTED", hand-measured on a git archive of 9eb7d7837, which is not the subject commit)
  cannot be confirmed from emitted bytes, and no witness in its suite reaches the loop by my instrumentation. If the 5 fails come from the cand trace (not bytes), the named witness comment ("caught by the (?i:x)abcdefg(?i:y) tie witness") is still stale: that pattern never ties. Confirm by running run_cand_oracle.sh against the plant (box-queue job) and by naming a tie-reaching witness.

### CHECK-5  S1095 re-anchor: holds, LOUD not SILENT — HELD (recorded as a finding only for the witness pointer)
- Plant = S1095's text on kit_run_member's pick line (window.c, count 1). Compares vs base over the 87 cand_oracle witnesses: 81 SAME, **6 LOUD** (rc 1: "the window family's run member N is not the run window's own index" / "the run ranking lost position ..." — emit_dfa req_run_member and window.c's own cross-checks), 0 SILENT-MOVE.
  Named witness `-e utf8 abcd`: base rc 0, plant rc 1 LOUD "the window family's run member 0 is not the run window's own index 3". Default regime `abcd`: SAME. `-e utf8 abcabcabc`: LOUD. `--engine=vm`, `-fmemfn-simd` variants of tie patterns: SAME. 
  Note it is LOUD because the other argmin readers (translate's ranking, pcrec's req_run_member) still apply the true relation: a planted bypass of kit_pick_takes in ONE reader is caught by the disagreement, never by the census (see CHECK-1).

## PLANTS ON THE PURITY HARNESS (art state read where the art is consumed)
All "nsites"-style plants hold iff the art has defined nothing / has a given state; `--purity` result; CONTROL = plant vs base `--purity-control`.
| plant (copy of memfn/src) | where | --purity | control |
|---|---|---|---|
| p_anystop `any_stop && !art->nsites` (the in-tree plant) | a_mass_holds (Table A) | RED, 80 failed (sites 0,4) | moves |
| p_parked | a_parked_holds | RED 80 (sites 1,3) | moves |
| p_model | a_model_holds | RED 80 (sites 2,3) | moves |
| p_margin | m_margin_holds (M) | RED 40 (site 3) | moves |
| p_mparked | m_parked_holds (M) | GREEN 287 | same: UNREACHED |
| p_rate: kit_byte_rate returns NULL when nsites | presence.c (consumer of art->an) | RED 20 (rated only) | moves |
| p_candrate: cands() gets NULL rate when nsites | candidate builder | RED 20 | moves |
| p_cpin: c_stop_holds && !nsites | T-VERIFY C-pin/C-stop/C-yes | RED 200 | moves |
| p_cmember: run_member off when nsites | T-VERIFY step 0 | RED 120 | moves |
| p_cmodel | T-VERIFY C-model | GREEN | same: UNREACHED (CHECK-2) |
| p_cbound (holds only with a stop) / p_cfloor | T-VERIFY C-bound/C-floor, no-stop path | GREEN | same: UNREACHED |
| p_runmem: `exact = ... && !nsites` | run_member verify-NO | GREEN | same: UNREACHED |
| a_includes / a_nlibc (art->includes, ->nlibc) | A-mass holds | RED 80 | moves (caught: the defines change them) |
| a_words / a_wused / a_wemitted | A-mass holds | RED 64 | moves (caught, though C3 says the emitting face is out of scope; stricter than the doc) |
| a_simd_inc, a_consulted, a_nreach, a_trace_id | A-mass holds | GREEN | same: the fixture never moves these (FUNC/RETURN sites, no SIMD, no reach stem, no finder routing; `consulted` has no writer today = breaker (d)) |
| a_policy (`policy != PORTABLE_ONLY`), a_denies, levers | A-mass holds | GREEN | policy: moves vs base (constant across the harness's arts; a legitimate per-art input, rev 5.2 axes) |
| g_static: window.c static call counter read by A-mass | breaker (c) shape | RED 35 | same (first 40 calls unaffected) |
| e_nonsticky: `art->err[0]` removed from mf_wdecide | breaker (a) | RED 5 (the sticky-err asserts) | n/a |
Reading: nsites/err/includes/nlibc/words readers are caught wherever the replies depend on the row; the misses are all rows no fixture reply depends on (CHECK-2) and art fields the fixture never moves (simd_inc, consulted, nreach; consulted/simd_inc are documented: breaker (d) future, C3 emitting-face). KEY tie rows (kit_pick_takes/kit_tie_takes) take no art by signature, so a KEY-row plant on them cannot read art; a process-global reader there is caught (g_static).

## Witness-text clauses (rev 5.2 1d) vs the harness
Honoured: N=5 window sites; fresh art vs after k defines k=0..N (in order, reversed, repeated), plan calls interleaved before each define and after the last; field-by-field (all 14 mf_wreply fields + `plan` up to nplan, `plan_term`, `stop_set` memcmp; checked against memfn.h); plant (one line, diff-counted =1, built); control (plant vs base printed replies after ONE define); sticky-err: two-NONE refused define then -1 on all 5 sites asserted as breaker (a) FENCED. Count check: 2 regimes x (5 + 35 + 35 + 65 checks) + 7 = 287 = PURITY_FLOOR exactly (floor is exact, no slack).
Not honoured / not exercised: M-parked, C-model picks, verify-NO run member, C-floor/A-floor, A-empty (last two declared); the plant is on an A row, not an M row; `--purity` is run only on the untraced fixture (breaker (b)/(c) trace labels and reach counters live under MF_TRACE and are not exercised by it — fenced by gate.c quiet, as rev 5.2 says; no harness evidence); one policy/denies/levers value only (legit inputs).

## PROBED-AND-HELD
- Purity harness: 38 fixture builds (base + 36 plants/unconditional variants + control), all compiled with the run_finder.sh gcc line; the harness is RED for 14 distinct art-reading plants and the sticky-err case, as listed; count and floor exact (287).
- run_finder.sh run once: all green incl. purity plant RED (80) and control.
- m6read_check_sab_anchors.py: all anchors resolve (1102 sabotages / 1143 anchor sites).
- S1095/S1096 plant text applies exactly once to the subject sources (count 1 each); both bypass plants are never SILENT-MOVE on 87 witnesses + ~30 probes.
- decider_census: run on the review tree: 59 passed / 0 failed, 37 hits, 0 stray, plants 1/1/2 stray hits, prototype plant 1 error; MEMBER_COUNT 52 matches rows; mass_domain gone, cands/kit_pick_takes listed.
- pcrec compiles: about 450 (56+48 sabotage compare probes, 261 witness compares, ~60 instrumented-binary reach probes, ~25 tie probes) plus 2 sabotage libs+links and 1 instrumented lib+link; budget 500.
