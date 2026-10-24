# critic_checks.md -- lens: check adequacy + trade audit (memfn-s3-final), SUBJECT cc4f54eb2, BASE 0d3765c87
Read-only; no suite run. Scratch: /tmp/claude-1001/crit-memfn-s3-final/checks/. Only single compiles + small python.

### CHECK-1  cover_pick reader cannot read the B-fn (offset-skip helper) shape of a cover find
- status: SUSPECTED (confirm: run run_encoding_checks.sh's DD12a section on a corpus line `(?i)foobar`; or read below)
- severity: maintenance      - effort: S      - blast radius: DD12a byte-vs-utf8 identity over every caseless fixed-width cover pair
- where: tests/codegen/run_encoding_checks.sh:1057 (`cover_pick`), :1543-1560
- detail: cover_pick normalizes only three shapes of a `scan_position = ({ ... })` line (memchr, B-pair loop, class loop). The default build's find for a caseless fixed run is B-fn: the line is `rx_mf1_ofsskip(...)` and the pick (K, the two memchr bytes, `while (pos + 5 < n)`) lives in the file-scope helper `rx_mf1_ofsskip__body`, which no regex touches. I ran the extracted cover_pick on `(?i)foobar`: byte stamps `@3 {B,b}`, utf8 stamps `@5 {R,r}` (DIFFER) -> picks `[]` (0 clauses). Byte and utf8 artifacts differ by ~5 helper lines (diff in checks/fb.c vs fu.c). So for any corpus pair of this shape the check is either red ("carries 0 search clause(s)", if the corpus has one) or silently does not hold B-fn's pick to its stamp (if not). Either way the new reader's stated population ("cover find, each side held to its own stamp") omits the form S3 made the default for caseless runs. No count of "cover pairs with stamps differing and picks read" is printed (only the aggregate `cover_pick` EXCISED count, whose non-vacuity needs just 1).
- who chose the input: the three regex shapes were written from job-600 artifacts (memchr/class), PAIR-loop added at r2; B-fn arrived at r1 C1 and the reader did not follow.

### CHECK-2  D-hors `whi < 0` guard: no plant, no census cell
- status: SUSPECTED (confirm: drop `|| dx->whi < 0` in d_hors_holds, run run_g2_win.sh; I expect green unless a site reaches it)
- severity: maintenance (a miss would be an `answer`/over-read)      - effort: S      - blast radius: REPORT sites whose stop sits in a negative-offset verify-YES core item
- where: memfn/src/window.c:1597; memfn/tests/run_g2_win.sh plants/EFIND_FLOORS
- detail: plants S1423/S1425 aim D-hors's bound and shift value; nothing aims the `whi >= 0` condition, and EFIND_FLOORS has `hors:110` and `below:95` as separate counts, never their intersection (D-hors with the window wholly below the candidate). The generator's dense stream puts span 0 at start 0 (whi >= 0 always); a negative whi needs the stop in an item span (rand_span, not dense sets), so HORS_MIN mass is rare there. Nothing counts that population (K35).

### CHECK-3  new axis classes `wf-find` / `wf-hors` carry no floors
- status: CONFIRMED (read)
- severity: maintenance      - effort: S      - blast radius: make test-axes
- where: tests/axes/memfn_arm.py:116-128 (comment: "FLOORS OWED ... pinned here by the agent that reads it")
- detail: both denies are `DIFFER, {}`: only the witnesses must differ (I checked: `\b[0-9a-f]{8}\b` byte differs 5 lines under no-wf-hors, utf8 does not, `\bcat\b` differs 135 under no-wf-find, so the witnesses reach). The "neither differs on the VM engine" claim and the corpus-wide counts are unasserted; a deny that stops moving most artifacts still passes while one witness moves. Deferral recorded in a comment, but no plan row/owner shown in the diff.

### CHECK-4  "the OFF arm is the build before S3" is load-bearing for ~50 re-aimed checks and no check pins it
- status: SUSPECTED (claim itself HELD in my probe: 36/36 artifacts, 18 patterns x byte/utf8, SUBJECT `--memfn=no-wf-find` == BASE modulo abi digits 84/85 and file name; `--emit-facts` also equal)
- severity: design      - effort: M      - blast radius: ~14 codegen suites, ~35 sabotage rows (S1121, S227, S267...S787), run_rows.tsv (pf_*_bounded, fn-pair, vrun-w16/w32), K27, cand_oracle, simd_floor_check, cli tests
- where: tests/codegen/*.sh, tests/mech/sabotages/S2xx-S7xx, tests/memfn/rows.tsv, run_wreply.sh ("build before S3, on which these rows and keys were written")
- detail: every pre-S3 mechanism check now compiles with `--memfn=no-wf-find`. If the deny arm ever drifts from the old default (a later window.c/E-generic change reaching it), all of those keep passing on the drifted arm and none compares to the old artifacts. Only K27 and run_dfa_stamps assert the deny arm "no longer renders cover". Likewise tests/kitproof compiles via `build/pcrec-harness` whose lever "since S3 renders the default build's text" (CLAUDE.md) -- an unpinned equality; the shipped `build/pcrec` is not the compiler under test there. run_cand_oracle's shipped-declines check now prints UNREACHED (population 0) instead of scoring, so it cannot turn red if the lever is later re-used. A one-time sweep (mine) is the only evidence.

### CHECK-5  PAIR's widened scope: rows/row_floors witness the cube, not the widening; g2 reach counts are substring heuristics
- status: CONFIRMED (read)
- severity: maintenance      - effort: S
- where: tests/memfn/rows.tsv (fd PAIR witness `(?i)foobar`), row_floors.tsv (`fd PAIR PLACEHOLDER PLACEHOLDER`), memfn/tests/g2/g2_win_gen.c ef_* counters, run_g2_win.sh EFIND_FLOORS
- detail: (a) fd PAIR's witness is a one-bit cube, which the pre-widening PAIR also decided; the control is its deny. The widening is covered only by g2's `pair:316` floor (measured 352; walk 217->114 moved), i.e. a count, via S1428/S1429/S1540 for stream-swap defects only. No plant narrows PAIR back to cubes, which would turn only a floor red (acceptable per K35 but unrecorded as the detector). (b) fd PAIR row has no pcrec_floor/g2_floor (PLACEHOLDER), so run_rows reach for the new row is unfloored. (c) ef_walk=`while (`, ef_libc=`memchr(`, ef_pair=`_ha < ` are strstr over rendered text; D-hors's probe also contains `memchr(`/loops, so "walk:103" and "libc:320" can be satisfied by non-B text. Floors are pinned AT or ~10% under measure, fine, but a render-shape rename zeroes the counter and fails (loud), while a text rename that keeps the substring passes.

### CHECK-6  proof_check.c lost REPORT proven[] == REQUIRED-sets equality; "held by G2 and C14" is only half true
- status: SUSPECTED
- severity: maintenance      - effort: M
- where: tests/memfn/proof_check.c (deleted `report_expect`, RPT exactness), family_c comment; memfn/tests/g2/g2_win_run.c:23,187
- detail: the deleted check compared `proven[d]` to the REQUIRED terms' sets both ways (docs/design/kit_proof.md m1: "C14 is EQUALITY ... `subset` alone admitted an over-filter"). G2's PROOF clause (g2_win_run.c:187) tests soundness only (a proven byte must hold at the yielded candidate in the subject), and `form_checks.py`'s C14 is a different C14 (shape bounds). tests/kitproof (answers, verdicts, facts) is the only remaining home for the exact-language side; I found no direct proven[]-vs-terms equality on the window family's class. An under-proving class is a speed loss that nothing now observes; a deliberate trade? None recorded in the diff beyond "held by G2's window family and pcrec's C14".

### CHECK-7  trade audit: floors/pins the diff moves (judge named?)
- status: CONFIRMED (read); items below marked J=judgment recorded, NJ=none located in the diff
- severity: doc      - effort: S
- detail:
  * cpset EMITTED_BYTES, 4 rows (-2404/-2912/-4454/-3103) and RX_DFA_PREFILTER "none": size GAIN; J (comment: "that ruling", job 600/606 re-records; +741 for `(?i)HeLLo` at r1/r2 with the diff-verified 30 helper lines). OK.
  * emit_sweep DIFFER_PINS: byte -fno-offset-skip 513->328, -fno-req-handoff 339->226, -fno-run-prefilter 127->54, utf8 604->376 etc.; coverage given up: every start-family deny now moves ~40% fewer default artifacts (fixed-width windows left). J: "S3 RE-PIN (lane s3fix600) ... none joined", but the judge is the lane; the ruling is the cover-by-default route. Pins are "AT the measure" (exact counts disarm themselves, learnings s3).
  * run_start_landing FLOOR_EMW 1124->510, FLOOR_PROD 1290->705: J (comment, measured job 600). Coverage of end-minus-width and the product arm halved on the default build.
  * simd_floor_check MOVERS/SIMD_FUNC 39 -> 33 (S3) -> 46; simd-form 5 -> 3 -> 6; -fmemfn-simd DIFFER cell 20 -> 9 -> 22: the comment itself calls the interim 33 "a trade never judged" (r1 C2), fixed by C1 restoring SIMD rows; final cells are above main. J at memfn_arm/emit_sweep: "a JUDGED trade, SIMD off by default and a SIMD-on loss the SIMD thread's finding (window_site.md s6)" -- judged by the lane (s3pair), citing the design doc, not a recorded owner ruling.
  * run_g2_win floors: wf-floor 740->486 (pinned AT, S2 sites moved to E-find), walk pinned 103 ("a JUDGED trade, not a lowered bar", r2 R2-1). J in comment.
  * registry floor 12->14: +2 denies, no loss. fd RPT floor row removed with RPT (J, "RETIRED at D172 S3").
  * S283 FLIPPED to UNDETECTED (run-rows mask bit now unobservable because `pf_window_of` states no run under -fno-offset-skip): a guarantee lost, J in the row (measured on c3ea619c3 AND S3 tree: unchanged, "defence in depth"). S284 flipped UNDETECTED->DETECTED (gain).
  * FLOORS OWED (memfn_arm wf-find/wf-hors): NJ beyond "owed".
  * kit_proof row m1 / CHECK-6 above: NJ.

### CHECK-8  deleted checks S1251-S1256, S922, ZK6/ZK7: guarantee gone with its mechanism
- status: CONFIRMED (held; informational)
- severity: doc
- detail: S1251/S1252/S1253/S1254 guarded `mf_preview` (after-first-define, twice, unnamed step, a `--memfn=` spelling); S1255/S1256 the REPORT row RPT's exactness comparison/fact; S922/ZK6/ZK7 "a held row decides before its step" (the preview hold in fd_row_decides). grep of SUBJECT's memfn/src, memfn/include, src, lib finds no `mf_preview` body, `kit_report_exact`, `SF_PROOF_EXACT` (finder.c:109 comment "retired"), `fd_row_decides` or "RPT" row: the mechanisms are gone, so those guarantees went with them. S1255/S1256 were already declared UNDETECTED/equivalent since S2. The only surviving cousin guarantee ("a REPORT site stated in terms is refused on every art") is held by proof_check.c family A/C/D (100-site floor) and G2 control 3. The generic property "no finder row decides before its step" has no successor (stated in run_sabotage_matrix.sh: "no row is held for a step"); acceptable since the LOCKDOWN has no held row, but a future held row has no guard.
- S1079/S1105 re-anchored to fd_route/fd_pres declines (HELD by reading; their SAB_BEFORE anchors exist per matrix header, I did not run them).

### CHECK-9  checked and found adequate: new site -> witness reach map
- E-find renderer row: S1422 (deny ignored) + controls 1-5 (render / refuse / floor); HELD.
- B-fn: ef_fn floor 48 + S1429/S1540; B-pair: ef_pair 316 + S1428/S1540; B-walk: S1427; C-run: S1426 (+ `run` floor); D-hors: S1423/S1425 + control 6/7 (`_sh[` present/absent) + hors floor 110; `wf-find` deny: S1422; `cover` LOCATE row: cand_oracle `cover - foobar/\bcat\b`, tests/kitproof (rows S1130-S1149, floors 24/6/55). The `cover` row's facts-listing contract (`used` not set by admission, facts_listing.md 4.1p2): no check; I observed `used` flips yes->no on cover artifacts vs BASE (`end_window`, `run_pin`, `width` for `abc`) and equals BASE under the deny; consistent with the spec sentence but unasserted (low).

## PROBED-AND-HELD
- Subject vs base, `--memfn=no-wf-find` vs BASE: 36 artifacts (18 patterns x byte,utf8), 0 differences after masking abi 84/85 and file stem. `--emit-facts` (abc): deny arm == BASE, 0 differences.
- NULL-subject (`search(NULL,0,0)`) under -fsanitize=undefined for 6 default cover artifacts ((?i)select, abc, x[abc]{3}y, \b[0-9a-f]{8}\b, (?i)h[a-z]llo(?=q), [ab]x[cd]{2}z): 0 faults (K27's default arm covers only `abc`).
- cover_pick regexes on 14 (pattern, encoding) artifacts: memchr/class shapes parsed and agreed with stamps (6 non-empty picks, all consistent); B-fn: 4 artifacts parse to 0 clauses (CHECK-1).
- wf-find/wf-hors witnesses differ from the deny arm (4 compiles); wf-hors does not reach utf8 as the comment claims.
- Plant anchors re-aimed in run_g2_win.sh read against window.c text (S1400, S1423, S1425-S1429, S1540) -- text-reading only, not executed.
- Denylist: no denied file opened.
