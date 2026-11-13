# VERIFY: s1 design re-check

## Verdicts

### READY-B-2
**HOLDS in substance, with one correction (PARTLY on the run_finder half's wording).**
- G2 half HOLDS. `memfn/tests/run_g2.sh` :1036-1038 (BT) runs the window family as
  `TMPDIR="$work" LIB="$plainlib" "$TO" 3000 bash "$here/run_g2_win.sh"`, `plainlib="$lib"` set at :288 BEFORE
  `[ "$rows" = 1 ] && lib=".../libpcrec_mftrace.a"` (:289); `run_g2_win.sh` :294 `one_run plain "$LIB"`, its plant
  path `kit_objs` (:209-216) compiles memfn/src with no `-DMF_TRACE`. `grep -c 'mf_wspan\|mf_walt\|nalt'
  memfn/tests/g2/g2_gen.c` = 0 (the rows half on libpcrec_mftrace.a states no window facts; :66-67 says so).
  So no G2 process defines a window-family site on a traced kit.
- run_finder half: `tests/memfn/run_finder.sh` :159/:169 run `--purity`/`--purity-control` on the PLAIN `$WORK/fx`;
  `run_purity_reach.sh` is handed `$WORK/fx` (:206). The traced `fxt` reaches finder_check.py's modes only
  (`--fd-site` FD_SITES + set10-* + RATE_SITES; `DIR --only fd-P*`; `DIR --query`).
- Correction (the "any fxt mode" question): I built a traced fxt in my dir (18 kit sources `gcc -std=gnu11 -O1
  -DMF_TRACE -c`, all rc 0; arm_fixtures.c + a `--wrap=pcrec_mf_wf_prepare,--wrap=pcrec_mf_wf_parts_prepare` probe,
  rc 0) and ran every mode finder_check uses. Results:
  - `fxt DIR --query` (whole fixture set): 0 `table=wf` records, 0 WPATH, 0 wf_prepare calls.
  - `fxt --fd-site S` for set10 set2r byte1 run3 pre-req pre-opt byte1t byte1vm hat1 mline set10-nobody set10-param
    set10-bodyoor pre-noproof pre-omin: no window-family call.
  - `fxt --fd-site pre-lead` / `pre-lead-run` (check_seam's RATE_SITES, traced arm) and `fxt DIR --only fd-P4` /
    `fd-P4-den` (check_pres_routing): `wf_parts_prepare rc=0`, and the trace prints
    `MFTRACE ROW table=wfE art=1 site=1 phase=define row=E-func verdict=CHOSEN gate=PASS` (one per run).
  So fxt DOES define E-func sites, but only pre-check PARTS (wf_parts_prepare -> wf_prepare, E-func's legacy
  translation); none of them prints `MFTRACE WPATH`/`FDROUTE` (grep count 0), i.e. none is a whole window site with
  the define_sel window record (`compose.c` :1186-1200) the 3.0b agreement sits beside. No fxt mode defines an
  E-find, E-generic or E-stmt site.
- Judgment: E and E2 have no traced whole-site population in G2 or run_finder at BT; whether the part E-func
  decisions (4 runs) carry the agreement depends on 3.0b placing the check on parts too, which the design does not
  say. B-2's fix (name a traced pass) stands; its text should not say fxt defines NO window site.

### READY-B-3
**HOLDS (arity, the jobs); runtime effect PARTLY (reasoned, not run).**
- `docs/dev/lanes/r33_sim/probe.c` :36-40 (BT): `mf_art *__wrap_pcrec_mf_art_begin(mf_arena *ar, const char *prefix,
  uint32_t policy, uint64_t denies, const mf_measures *ms, const mf_analysis *an)` and
  `__real_pcrec_mf_art_begin(ar, prefix, policy, denies, ms, an)`: SIX args. `memfn/include/memfn.h` :1425-1426 (BT):
  `mf_art *mf_art_begin(mf_arena *a, const char *prefix, uint64_t denies, const mf_measures *ms, const mf_analysis *an);`
  FIVE args (`#define mf_art_begin MF_NS(art_begin)` :1393).
- `nice -n 19 gcc -std=gnu11 -Wall -Wextra -I.../memfn/include -I.../lib -c docs/dev/lanes/r33_sim/probe.c` -> rc 0,
  no diagnostics (the `__real_`/`__wrap_` prototypes are the probe's own; nothing checks them against memfn.h).
- Jobs that build it, in tree: `docs/dev/lanes/r33_sim/240-kit-r33-sweep.sh` :28 and `241-kit-r33-rp.sh` :28
  (`bash "$SIM/build.sh" "$TREE" "$S/tb"`, `TREE=/home/pcrec/projects/pcrec/worktrees/r33` :7); `build.sh` :12-14 links
  `cli/main.c probe.c libpcrec.a -Wl,--wrap=pcrec_mf_define,--wrap=pcrec_mf_emit,--wrap=pcrec_mf_art_begin`.
  `docs/design/memfn/span_pick/CLAUDE.md` :40 ("re-made by its job 240") and :47 ("job 488 re-makes the sweep");
  440/488 are queue job files, not in the tree (not opened: queue is denylisted).
- Runtime (SysV x86-64, reasoned from the two signatures; NOT run: building the traced lib needs `make`): pcrec's
  5-arg call puts denies in rdx, ms in rcx, an in r8. The wrapper reads policy=edx, denies=rcx (the ms pointer),
  ms=r8 (the an pointer), an=r9 (unset), and forwards rdx=policy, rcx, r8 to the real 5-arg function, which then
  sees denies = the LOW 32 BITS of the caller's denies (zero-extended from `uint32_t policy`), ms and an intact.
  So the critic's "forwards ms/an correctly; the probe's own `an` is garbage" holds, and in addition deny bits
  32-63 are dropped on the way through (any deny whose bit is >= 32 would be lost in a census run). "It broke
  silently at U2" holds.

### READY-B-5 and FIX-1
**Facts HOLD. B-5's judgment HOLDS (emit_sweep would catch a refused ASK-6 under 3.0b). FIX-1's row-1 scenario is
REAL as a coverage gap (HOLDS), with one wording correction (there are two literal `@` checkers, both deny the
cover route).**
- `src/gen/emit_dfa.c` (BT) `req_run_at` :16050; the cover branch :16068-16079:
  `mf_site *cs = pcrec_cover_site(cx, cv, NULL, NULL, &h, &u);` then
  `if (!mf_wdecide(pcrec_memfn_art(cx), cs, &w) && w.has_stop) at = req_run_in_cover(...); goto done;`
  -- a refusal leaves `at = -1` (:16061) with no diagnostic. Contrast `window_reply_ask` :7608-7618:
  `if (mf_wdecide(...)) pcrec_ctx_fail(cx, 0, "internal error: the memfn kit refused the window family's phase-1 ask ...")`.
- `emit_cover` :14249-14251: `const char *stem = dfa_fragf(cx, "%s_cover", fn); mf_site *s = pcrec_cover_site(cx, cv,
  stem, NULL, &h, &u); uint32_t handle = pcrec_memfn_define(cx, DELEG_COVER, s, &h, c);` -- pcrec defines the site.
  `src/gen/known.c` :484-509 `pcrec_cover_site` builds it (STMT/FIND/ASSIGN, `site_kind = MF_SK_REPORT`,
  `decl_point = stem != NULL`, `pred.fn_ref = stem != NULL`, hooks `h`), so the ask's copy (stem NULL) differs from
  the define's in decl_point/fn_ref, as FIX-1 says.
- `tests/codegen/reqcube_check.py` :97 `COVER_DENY = "--memfn=no-window-search"`, used by `emit()` :102, the facts
  call :113, and the C4 lever path :401. Also `tests/codegen/run_prechecks.sh` :88/:102 (its [3.1r] REQ_RUN literal
  check, :448-454) compiles under the same COVER_DENY, and `tests/codegen/run_encoding_checks.sh` :687/:1513
  normalizes the `@` away (`REQRUN_STAMP_RE ... (?:@\d+)?` -> `@K`). So no checker I found compares a cover-route `@`.
- Population (4 pcrec compiles, all rc 0): `build/pcrec -p rx --features all --pattern P`:
  `foo[0-9]{4}bar` -> `RX_REQ_RUN "626172@0"`, `RX_DFA_SCAN "cover"`; `abcdef` -> `"616263646566@1"`, cover;
  `a{6}b` -> `"61616161616162@6"`, cover. With `--memfn=no-window-search`: `foo[0-9]{4}bar` -> `"626172@0"`,
  `"unanchored"` (the deny re-routes, so the deny-only checkers never see the cover `@`).
- Judgment B-5: 3.0b is byte-neutral, and `scripts/emit_sweep.py` stream 1 compares whole `.c` artifacts at the
  default engine under `--features all` over the corpus; a refused ASK-6 drops the `@` on every cover-route artifact
  (all three probes above carry one), so emit_sweep would red. B-5 is right that the check exists and is unnamed.
- Judgment FIX-1: after 3.0b, a row that moves bytes on purpose (row 1) no longer has emit_sweep identity as a
  guard; a frame-dependent row declining NONE asks would make `w.has_stop` 0 on the cover ask and drop `@` silently
  (no error, see above), and the only literal `@` checkers deny the cover route. The scenario is real; whether it
  fires depends on row 1 choosing §6's "declines on NONE asks" option.

### READY-K-1 and READY-K-8
**K-1 HOLDS. K-8: its facts HOLD; its consequence (a text-census cell cannot see an arm stop being entered) holds
by construction (reasoned, not planted).**
- `memfn/tests/g2/g2_pres_run.c` (BT) `lay_a` :561-585 (inside `#ifdef G2P_ASAN` :555): `static const unsigned
  ws[] = { 16, 32 }; ... for (unsigned off = 1; off < ws[wi]; off++) { size_t n = x->run_len + rnd(24);` and
  `rnd(n)` = `(g_rng >> 33) % n` (:99-103), so layout A's n <= run_len + 23. Layout L (`uses`, :517):
  `size_t n = rnd(x->run_len + 48);` so n <= run_len + 47.
- Render (own dir): `nice -n 19 gcc -std=gnu11 -O1 -Wall -Wextra -Werror -I memfn/include -I memfn/tests/g2
  memfn/tests/g2/g2_pres_gen.c build/libpcrec.a -o verify/g2p/gen` -> rc 0;
  `verify/g2p/gen 20261110 400 verify/g2p/out x86-64-v3 0` (run_g2_pres.sh's one_pass argv, :265, its
  default SEED/NSITES :61-62) -> rc 0, `G2PGEN x86-64-v3.default ... simd16=22 simd32=22 ...`,
  `g2_pres_gen failures: 0`.
- Each `__w32` helper's entry test, joined to the site's `run_len` from the `g2p_sites[]` initializer (field 8,
  `g2_pres.h` :49-56), by a python read of `g2p_sites.c`:
  all 22 `__w32` helpers read `if (pos >= n || n - pos < T32) return ..__w16(...)` with T32 = run_len + 31
  (site 41: run_len 8, T32 39, T16 23; site 335: run_len 20, T32 51, T16 35; ... ), and T16 = run_len + 15.
  Layout A's largest n is run_len + 23 < T32 on every site: "w32 helpers 22 reachable in A 0". w16 (T16 =
  run_len + 15 <= run_len + 23) is reachable in A. Layout L's n reaches run_len + 47 >= T32, so w32 is entered in L
  on a fraction of calls only (n - pos >= run_len + 31), as K-8 says.
- So no w32 arm can run in layout A at BT (any seed: the bound is structural, n <= run_len + 23 < run_len + 31), and
  a w32 layout-A cell counted as placements is nonzero while reaching no w32 arm.

### READY-K-2
**HOLDS (by grep; no plant was run: run_g2_pres.sh is out of bounds, so no compiler exit code to record).**
- `memfn/tests/run_g2_pres.sh` (BT) :361-365: `if [ "${1:-}" = "--plant" ] || [ "${1:-}" = "--plants" ]; then ...
  export G2P_NOASAN=1`. `one_pass` builds and runs the ASan binary only under `if [ -z "${G2P_NOASAN:-}" ]` (:279-284,
  `-DG2P_ASAN`); the same guard at :469, :521, :561.
- `tests/mech/run_sabotage_matrix.sh` :3489-3494, the `g2pres` arm: comment "no ASan build (no row plants a read)",
  then `LIB=... CC=... TMPDIR=... G2P_NOASAN=1 bash "$tree/memfn/tests/run_g2_pres.sh"`; vocabulary line :558 says the same.
- Layout A exists only under `#ifdef G2P_ASAN` (`g2_pres_run.c` :555, its calls :712-713, :752-753, print :774-775).
- So neither plant runner (`--plant`/`--plants`, the g2pres mech arm) ever runs layout A; a W-K4b plant whose only
  detector is "an ASan report in layout A" cannot red in them. (Combined with K-1: at w32 not even an ASan run
  would reach the arm.)

### READY-K-5
**HOLDS (re-run on a scratch copy).**
- `tests/memfn/finder_check.py` (BT) `check_store` :549-570 is called from main (:930); for every
  `measure_store/*/*/set.tsv` whose method is `kit-grid@V` it compares `sorted(secc) == sorted(mine)`, `mine` = every
  `memfn/data/cards/kit-grid.tsv` row of ver V, else `bad("store %s: its cards section is not %s.tsv's ver %s")`.
  `measure_store/zen4-grid3/1/set.tsv` :13 `method kit-grid@3`. Run by `tests/memfn/run_finder.sh` (Makefile :1606-1609).
- Repro (own dir only): copied BT's kit-grid.tsv to `verify/k5/cards/`, appended
  `kit enter_back 3 kind;entry;back walkbytes artifact die1 g256 delta 1048576 7 7 twin-per-arm - - -` (tab-separated,
  the `kit enter 3` row's shape, :68), and ran check_store's comparison by importing BT's finder_check.py
  (`python3 -I verify/k5/cmp.py .../finder_check.py .../measure_store/zen4-grid3/1/set.tsv CARDS`):
  BT copy: `method kit-grid@3 ... ver-3 cards 4 section 4 equal True`;
  with the row: `method kit-grid@3 ... ver-3 cards 5 section 4 equal False` -> check_store would print
  "store zen4-grid3@1: its cards section is not kit-grid.tsv's ver 3" and red run_finder's section.

### READY-K-6
**HOLDS.**
- Scratch trees (own dir) `verify/k6/{bt,row}` holding BT's `docs/design/memfn/span_pick/census0.out` and
  `memfn/data/policy.tsv`, plus kit-grid.tsv as at BT (bt) or with K-5's `enter_back` ver-3 row (row).
  `SLOT_TREE=verify/k6/$t python3 -I -B docs/design/memfn/span_cards/slot/plan.py report` (BT's plan.py, `-B` so no
  bytecode is written): `bt rc=0 lines=85 enter_back=0`, `row rc=0 lines=85 enter_back=0`, `cmp` -> BYTE-IDENTICAL
  (`== slot plan: 38 rows, 30 floor lines over 18 clauses`). The new card loads silently and plans nothing.
- The refusal: importing BT's plan.py under SLOT_TREE=row, `"enter_back" in CARD` -> True; `key_arm_mismatch` on a
  synthetic Arm `name="kit.enter_back.1.NONE.8"` -> `SystemExit: plan: card dim back (key kit.enter_back.1.NONE.8) has
  no DIM_FIELD line` (plan.py :210-216). Its only caller is `link.py` :233 inside `render(fx, a)` (per Arm, link
  time), not `build()`/`report`. So "plan.py refuses a card dim with no planner line" fires only for a planned Arm at
  link time; the dry run as worded neither lists nor refuses the new cell.

### FIX-4
**HOLDS.**
- `tests/compound/run_lever_fence.sh` (BT) :61 `ALLOW='^(cli/main\.c|...|tests/codegen/reqcube_check\.py|...|tests/memfn/run_arm_reach\.sh|tests/memfn/site_census\.py|...)'`
  (no `tests/memfn/reach_equal\.py`; under `scripts/` only `scripts/emit_sweep\.py`); `mentions()` :62-65 greps
  `-e '--harness=' -e "$PFX"` over `docs/spec docs/guide README.md examples lib tests scripts cli` and drops ALLOW;
  check (c) :76-78 fails on any remainder. Today `grep -c -e '--harness=' tests/memfn/reach_equal.py` -> 0.
- Replay on a scratch copy (`verify/fix4/tests/memfn/reach_equal.py` = BT's + one appended line naming
  `"--harness=run-tie-left"`), the fence's own pipeline with its own ALLOW (read out of the script by sed):
  `(cd verify/fix4 && grep -rnI -e '--harness=' tests) | grep -Ev "$ALLOW"` printed
  `tests/memfn/reach_equal.py:309:# planted: arms include "--harness=run-tie-left"` (rc 0) -> (c) would FAIL.
- The binary: `build/pcrec --harness=run-tie-left --features all -p rx -o .. --pattern 'a.*zqxzqx'` -> rc 1,
  "pcrec: unknown option '--harness=run-tie-left'"; `build/pcrec-harness` same argv -> rc 0 (`cli/main.c` :1538).
  So an arm pointed at plain (MF_TRACE) pcrec fails every compile, on both sides, as FIX-4 says.

### FIX-6
**HOLDS (shard table); the id half is PARTLY (the K38-3 sentence is ambiguous, not contradictory).**
- `tests/ci/cloud_mech_shards.tsv` (BT) line 1-2: "the cloud mech kinds' shard table ([CLOUD-SUITE] C), GENERATED by
  tests/ci/cloud_units_plan.py mech". `grep -c 'S30[0-9][0-9]'` -> 34 lines; ids S3000-S3012, S3015, S3020, S3030-S3035,
  S3042-S3048, S3060-S3064 (K38-2's among them). `cloud_units_plan.py` :193-195 `plan_mech` takes its ids from
  `os.listdir("tests/mech/sabotages")`, so every new mech row joins only when the table is regenerated;
  `tests/ci/CLAUDE.md` :64-68 says how it is made. 3.0b (19 rows) and K38-3 (its plants) both add rows under
  tests/mech/sabotages, so each lander regenerates the one file (or its rows are absent from the cloud shards); the
  second lander re-runs the generator. I found no check that forces the regeneration (a gap, not a red).
- Ids: SUBJ span_runs_sheet.md :568 (K38-3 row): "Ids from the free range at build (S3078 and up are 3.0b's
  expectation; take K38-3's after the manager's ledger)"; plan_frame.md SUBJ :1030 "expected as **S3078-S3096**";
  Order paragraph :580-584 "recommended K38-3 FIRST ... or the two in parallel lanes. Neither re-baselines the other."
  If K38-3 lands first and takes the lowest free ids, 3.0b's "expected" range shifts; the sentence can also be read
  as "after 3.0b's reservation". Harmless (ids are re-taken at build), as FIX-6 says; a one-clause text fix.

### FIX-7
**Facts HOLD; the SUSPECTED population gap is CONFIRMED: no purity site reaches a PAIR pick or a refused framed
(wf_plan_site) ask at BT.**
- `memfn/src/window.c` (BT): `wf_plan_site` :2322-2335 calls `decide`, `plan_of`, then
  `if (wf_find_decide(art, d, w, def, 1, fx)) { *why = "out of memory"; return -1; }` before Table E's `kit_walk`.
  `wf_find_decide` :2245-2248: `if (fx->pick == FF_PAIR && !fx->fn) { fx->fn = art->a->alloc(art->a->u, sizeof *fx->fn); ...`
  `why_room` :2303-2308: `char *buf = art->a->alloc(art->a->u, WF_WHY_MAX);`, called at :2340, :2374, :2383 (the
  refusal paths). Both allocate from `art->a` directly, as FIX-7 says.
- Population: I ran the purity harness on my TRACED fxt (built for B-2: same arm_fixtures.c, kit `-DMF_TRACE`):
  `verify/fxt --purity` -> rc 0, `checks passed: 1157`, `checks failed: 0`. Its trace:
  - every `table=fd` REACH line reads `chosen=0 asked=0` (D-hors D1 D1c D1w PAIR R7w P0 P2 P3 P4 P9): T-FIND is never
    asked on a purity site, so no PAIR pick, so `wf_find_decide`'s alloc is never reached;
  - `table=wfE`: 89 SEL, 89 END, all 89 `chosen=E-` (81 E-func, 8 E-generic); `grep -vc 'chosen=E-'` on the END lines
    -> 0: no wf_plan_site refusal, so `why_room` is never reached. The one refused case,
    `pur_refused()` (`arm_fixtures.c` :2218-2226, a two-NONE site, :2341-2342), produces no wfE selection (it is
    refused before Table E).
- So a 3.0b build that threads the allocator into `wf_plan_site` but leaves (1) or (2) on `art->a` would pass the
  purity/counting-arena population as it stands at BT. (Side fact for B-2: this traced `--purity` run carries 89
  whole-site window defines with WPATH records; run_finder runs `--purity` only on the plain fx.)

### READY-A-2 / FIX-3 (enclosing functions of window.c :664, :938, :1563)
**HOLDS for the three functions; one correction to FIX-3's "neither decide nor the plan function".**
- `grep -n kit_run_opts_of memfn/src/window.c` (BT) -> :115 (a string), :664, :938, :1563. Enclosing function by an
  awk over the headers, then checked by hand (no column-0 `}` between header and line):
  :664 -> `static void a_mass_choose(wf_x *x)` (:651), Table A's `mass` row (:764), walked by `decide` (:1206, its
  `kit_walk(&wf_atable, ...)`); :938 -> `static void run_member(wf_dec *d)` (:925), the `C-member` row (:1117), reached
  by `decide` through `c_plan(d)` (:1153, called :1242); :1563 -> `static void translate(const wf_dec *d, const struct
  wf_plan *w, unsigned eb, wf_legacy *L)` (:1476).
- `mf_wdecide` (:1279-1295) at BT calls only `wf_check`, `decide`, `reply_of`: it reaches :664 and :938, not :1563.
  So A-2 holds as written (the design's "inside `decide` (:938, :1563)" misnames :1563 and omits :664).
- Correction to FIX-3: `translate`'s callers are `wf_prepare` :2430, the B row :1913, AND `e_legacy_holds` :1628
  (`translate(e->d, e->w, eb, e->L); return kit_legacy_serves(...)`), which is Table E's E-func/E-stmt `holds`
  (`wf_erows[]`), walked by `wf_plan_site`'s `kit_walk(&wf_etable, ...)` (:2333). So :1563 IS inside the plan
  function 3.0b shares with a framed `mf_wdecide`; it is outside `decide` only. The cite fix stands (name :664 and
  :938 as decide's reads); :1563 should be labelled "the plan function's Table E walk (and the define)", not
  "define-only".

### Summary
- HOLDS: B-2 (substance; fxt defines E-func pre-check PARTS only, no whole window site), B-3, B-5, FIX-1, K-1, K-2,
  K-5, K-6, FIX-4, FIX-7 (gap confirmed: purity reaches no PAIR pick, no wf_plan_site refusal), A-2.
- PARTLY: FIX-6 (shard table holds; id sentence ambiguous), FIX-3 (:1563 is reached by wf_plan_site via
  e_legacy_holds, not define-only), K-8 (facts hold; consequence by construction).
- REFUTED: none.
- Extra facts found: probe.c's arity drift also drops deny bits 32-63 (B-3); a traced `fxt --purity` (not run by
  run_finder today) carries 89 whole-site window defines (81 E-func, 8 E-generic), the population B-2's fix names.
- Budget used: 18 kit `-c` compiles + 1 traced fxt link + 1 probe.c `-c` + 1 g2_pres_gen build = 21 gcc; 6 pcrec
  compiles (build/pcrec x5, pcrec-harness x1); 0 make, 0 suites, 0 boxqueue; writes only under verify/.

VERIFY COMPLETE
