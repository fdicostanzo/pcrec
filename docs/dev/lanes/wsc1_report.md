# wsc1 — D172 S2 commit 1: the kit's window family (lane report)

Lane wsc1 (kit lane of the memfn kit manager), 2026-10-22. Worktree
`worktrees/wsc1`, branch `lane/memfn-wsc1`, cut from the kit branch
`lane/memfn-ws` @ 7050f8652. Build go: Frank 2026-10-21, conditional on the
critics and main agreeing; both held (main filed R-29, agrees with rev 3.2).
Design of record: `docs/design/memfn/window_site.md` rev 3.2. Scope: §5.1
COMMIT 1 ONLY, the kit side. No pcrec builder edit, no `MF_SITE_ABI` number
change, no D-hors.

STATE AT HANDOFF: every light check run and green (§2, "Validation at the
tip"); the heavy run (emit_sweep plain vs 7050f8652 with the dumps stream,
then `make test`) is QUEUED as `575-kit-wsc1-heavy` and OWED (§4). No
rulings file was named.

## 1. What was built, mapped to the design

Everything below is reachable ONLY on an art previewing `"window-family"`
(`mf_preview`). No default path decides anything from the new facts.

| design | built | where |
|---|---|---|
| §1 the facts: spans (start, sets, core, verify), alternatives with ENTRY, table offers, floor, frame | `mf_wspan`, `mf_walt`, `mf_verify`, `mf_core`, `mf_entry` (UNSTATED / NONE / PARKED / RESEED), `mf_wfloor`; `mf_site.nalt`/`alts`/`wfloor` appended LAST; bounds `MF_WSPAN_POS`, `MF_WMAX_SPAN`, `MF_WMAX_ALT`, `MF_WREACH`, `MF_WPLAN_MAX`. The frame is today's fields (form/op/handoff/empty/use/body/decl_point/site_kind/hooks, `pred.fn_ref`); EXPR's F is the `floor` hook | `memfn/include/memfn.h` |
| §1 as `fields.def` rows with contract classification, appended last | classes PARKED, RESEED, NOENTRY, CORED, NOCORE, W_SUBJECT, W_EXPR; fields `alts`, `entry`, `span_start`, `core`, `verify`, `toffer`, `wfloor`. They classify ONLY through `gate_in.wf` (the family's walk facts) and read UNSTATED in every other walk, so no older row is declined by a site stating them beside its old fields | `memfn/src/fields.def`, `gate.c`, `kit.h` |
| the statement's rules | `wf_check`: every fact stated (an UNSTATED zero refused, the empty core a value), bounds, `wfloor` refused UNSTATED where a span reaches below the candidate, two alternatives = one PARKED + one RESEED, NOP's empty range agreed by both; the frame rules on the preview's own route. On a default art the facts are checked as statements and a spans-only site is refused naming the lever | `window.c`, `compose.c` `window_route` |
| §0 the two-phase ask, phase 1 | `mf_wdecide(art, site, mf_wreply *)`: pure, no text; the chosen alternative, stop (offset and set), plan offsets AND their compares (`plan_term`), pinned, the run's member and stretch, the RE-SEED bit, the path. Refused without the lever; reads no frame fact | `memfn.h`, `window.c` |
| §2.1 Table A | `wf_arows[]`, a `kit_table` on `kit_walk` (table `wfA`): A-empty (C-meet's empty meet inside a core, the floor), A-parked, A-model, A-mass, A-floor; keyed by contract on `entry` and `core` | `window.c` |
| §2.1 MARGIN | `wf_mrows[]` (table `wfM`): M-one, MARGIN (`best * NUM < base * DEN`), M-parked | `window.c` |
| §2.1 the TIE table | `wf_ties[]`: every tie row of §2.1 (A-mass stretch HIGHER, A-mass set LOWER, A-model LOWER, C-model EXCHANGE, MARGIN PARKED, the truncation window LEFTMOST as pcrec's); every comparison that can tie reads it (`tie_takes`) | `window.c` |
| §3.2 prefix_k as rows | `verify_cost`, `model_cost`, the scan loop over walked one-member spans, the exchange sort, the greedy `continue`, the MAX_SET cap, `base`, verbatim | `window.c` `a_model_choose`, `a_parked_choose` |
| §3.3 `plan_cost.def` | `MF_COST(name, value, unit, provenance, box, basis)`: C_MEMCHR 6, C_BITMAP 116 (MEASURED, ubuntubudu), C_VERIFY 250 (UNMEASURED DEFAULT), C_ENTER 2000 (MEASURED x ASSUMED), C_MISPRED 1500 (DERIVED), MATERIAL 2/1 (ARGUED), MAX_SET 4 (UNMEASURED DEFAULT); HORS_MIN left out (D-hors, S3) | `memfn/src/plan_cost.def` |
| §2.3 Table C | `wf_crows[]` in step order: C-meet, C-floor / C-yes, C-model / C-none, C-pin, C-stop, C-run (W2's separation, the pinned stretch exactly one compare), C-table / C-own, C-asc | `window.c` |
| §2.3 C-pin, the reply owns member and stretch | `run_member` (exact positions, TIE HIGHER), `c_pin` (the stop IS the member, the plan does not test all of R) | `window.c` |
| §3.5 the RE-SEED bit | set on a RESEED choice, on PARKED + C-pin, and on a PARKED floor plan that reads a verify-NO span | `window.c` |
| §2.5 Table D | `wf_drows[]`: D-one only (`c + 1`), read by the floor's loop. D-hors NOT built (S3) | `window.c` |
| §2.6 Table E | `wf_erows[]` (table `wfE`): E-func (FUNC/RETURN, no expression floor), E-stmt (STMT/ASSIGN or ON_MISS), E-generic (the floor). E-func/E-stmt render the plan TRANSLATED into today's row's site, selected by the composer's walk as ever (the finder's routed pick included), so their text is today's rows'; they hold only where the translation has the plan's semantics and today's rows serve the frame (asked quietly, `kit_legacy_serves`) | `window.c`, `compose.c` |
| §2 the generic floor; §1.3 the three-way edge guard | `wf_floor_arm` (form id `wf-floor`): a byte loop over the plan's positions (the stop's included), ONE hoisted core bound per candidate (the loop condition `c + chi < n`, the first conjunct `c >= [F +] |clo|`), the THREE-WAY guard on every non-core position (off the subject passes, inside [0, F) is pcrec's edge, else membership), C-table / C-own; FUNC, STMT/ASSIGN, STMT/ON_MISS, every empty outcome; its class from the plan (R-25) | `window.c` |
| §2.7 path ids | `mf_wreply.path` (phase 1) and, in a trace build, `MFTRACE WPATH art= site= path= arm= fd=` per rendered site | `window.c`, `compose.c`, `memfn/docs/trace_format.md` |
| the masses (pcrec_find_set_ppm = set_mass, PROBED-AND-HELD) | `kit_set_mass` (capped, A-model) and `kit_set_sum` (PICK's uncapped cube mass, A-mass and the member), `kit_byte_rate`, one definition shared with presence.c | `presence.c`, `kit.h` |

## 2. Checks

| check | command | verdict |
|---|---|---|
| build | `make -j16` | clean, no warning |
| strict | `make strict` | **clean** ("whole tree compiles clean with -Werror -Wshadow") |
| sabotage anchors | `python3 -I scripts/m6read_check_sab_anchors.py` | **all anchors resolve** (901 sabotages, 932 anchor sites) |
| codegen | `bash tests/codegen/run_codegen_tests.sh` | **331 passed, 0 failed** (a first run read 330/1 on `[DD-14-RECURSION rule 3]` "pcrec failed to compile the fixture": I had rebuilt `build/pcrec` while it ran; the fixture compiles rc 0 alone, and the re-run on the stable build is green) |
| test-core | `make test-core` | **rc 0** |
| every test-memfn-* | `make test-memfn-{link,manifest,stamps,arms,deleg,arch,forms,reach,rows,finder,rank,guarded,simdfloor}` | **each rc 0** (finder: finder_check 958/0, proven 31/0, arm_reach 16/0, pr11 5/0, presence 24/0, proof 1288/0 with proof_run's new read-limit layouts: 550 sites, 21,479,052 layout calls) |
| G2 quick | `make test-memfn-g2` (run_g2.sh --quick, with section 4w) | **rc 0, checks passed 71,217,801, failed 0**; section 4w "PASS: window family (checks passed: 6031)" |
| G2 window family | `bash memfn/tests/run_g2_win.sh` (TMPDIR the scratchpad) | **GREEN: checks passed 6031, failed 0** (1500 sites rendered, 3,745,812 answer calls in four layouts, 622,264 hits; ASan+UBSan driver passed 3000 failed 0; W1 ref-defects 2-5 each red) |
| plants | `bash memfn/tests/run_g2_win.sh --plants` | **8 of 8 RED** (§3) |
| emit_sweep plain vs 7050f8652 | queued (§4): the box lock was held by 571-kit-r28-heavy | OWED |
| make test | queued (§4) | OWED |

### 2.1 Notes on the light checks

- Every light check ran on this box while the queue's `571-kit-r28-heavy`
  held the box lock (a correctness run, not a timing window): no quiet gate
  was in force. `emit_sweep` takes the box lock itself, so it is in the
  queued heavy job instead of run by hand (§4).
- `proof_run`'s new READS check has its own planted witness, `WSC1-R1` in
  `tests/memfn/run_proof.sh` (the generic row's read bound one byte loose):
  RED, "READS: a fault (guard at s + n)".
- The final window-family numbers at the tip are in "Validation at the
  tip" below.

## Validation at the tip

Final runs on the tip's build (scratchpad logs; seed 20261022, 1500 sites):

- `bash memfn/tests/run_g2_win.sh`: **checks passed 6031, failed 0, rc 0.**
  1500 of 1500 sites rendered, 26 lever controls and NOP refusals refused
  as they must be, 1500 queries agreeing with a same-phase define;
  3,745,812 answer calls (each in layouts U, L, S-in, S-out), 622,264 hits;
  paths empty 197, parked 317, reseed 117, mass 745, floor 124, pinned 39,
  RE-SEED set 257; MARGIN chose RESEED 117, PARKED 151; ties decided: mass
  255, model 63 (a MARGIN tie never arose: no floor holds it); cells:
  edge rejections 24,575, core positions off the subject 1,788,589,
  non-core 544,594, reads below the candidate 1,029,683, NOP empties
  147,501; forms wf-floor 821, generic 398, pf_memchr 235 (pf_memchr_back
  among them), ofsskip 29, pf_walk 17. ASan+UBSan driver 3000/0. W1
  ref-defects 2-5 each red.
- `bash memfn/tests/run_g2_win.sh --plants`: **8 of 8 RED** (table §3).
- `bash tests/memfn/run_proof.sh --plant WSC1-R1`: **RED** (READS: a fault,
  guard at s + n).

## 3. The plants

`memfn/tests/run_g2_win.sh --plant ID` copies `memfn/src`, replaces one
string, rebuilds the kit objects, regenerates and re-runs; it must go red.
Placeholder ids WSC1-P1..P8 until the kit manager assigns S1400-S1429 ones
(asked 2026-10-22).

| id | the defect | verdict (first red) |
|---|---|---|
| WSC1-P1 | an edge guard dropped (the floor's `c >= F + |d|` clause) | RED: READS, a fault in layout L (guard at s + F) |
| WSC1-P2 | C-run merging singletons (positions one-position spans cover grouped) | RED: DECIDE, the compare at plan[3] (3 sites) |
| WSC1-P3 | a margin direction flipped | RED: DECIDE, alt (225 sites) |
| WSC1-P4 | a tie flipped (A-mass at a set position to the HIGHER offset) | RED: DECIDE, stop (44 sites) |
| WSC1-P5 | a core position read as outside the core (the plan's last tested position) | RED: PLAN (664 sites) |
| WSC1-P6 | an empty meet not sent to the floor (§5.2's list) | RED: 314 sites (DECIDE; first printed: the query's class differs from the define's) |
| WSC1-P7 | C-pin splitting the stretch (§5.2's list) | RED: DECIDE grouping (39) |
| WSC1-P8 | an untested offset claimed (§5.2's list: the class proves one past each tested position) | RED: PROOF (356) |

P5 as first written (a core position's own test spelled three-way) went
GREEN: it is EQUIVALENT, since the hoisted bound already holds every core
position of [clo, chi] inside the subject. The plant was retargeted to the
bound itself (§2.6 F-15 below), which is where reading a core position as
outside the core can change an answer.

## 4. The queued heavy run

Job `575-kit-wsc1-heavy` (kit band, `idle-ok`, cap 14400 s, a correctness
run with no quiet gate; `--ready` exits 0). At the lane tip it runs:
`make -j16`; `python3 scripts/emit_sweep.py --ref 7050f8652 --bin build/pcrec
--tree worktrees/wsc1 --no-self-check --streams c-default,c-vm,emit-ir,
composition,facts,emit-ir-auto,stderr,dumps` (zero movers required: the
family is unreachable without the lever, so every stream must read
`movers=0`); then `scripts/perfrun --label wsc1 -- build/wsc1/heavy/
maketest.make.log` (`make test`).

- Logs: `worktrees/wsc1/build/wsc1/heavy/{build,sweep_plain,maketest}.log`,
  the make output `build/wsc1/heavy/maketest.make.log` (+ `.perfrun`), the
  sweep's own `build/wsc1/heavy/sw_plain/`; the queue's job.log under
  `worktrees/.boxqueue/done/<ts>-575-kit-wsc1-heavy/`.
- Completion lines: `emit_sweep: DONE rc=0` (the declared population,
  `expect sweeps=1`), `== wsc1 heavy: 0 step(s) failed`; the make verdict
  is `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' maketest.make.log`
  (empty = green). Read it with `scripts/verdict`.
- OWED: both verdicts. A fresh agent reads them.

## 5. Where the design was wrong, silent or unbuildable as written

Each with its code evidence. None changes a commit-1 byte; each is a
reading the build had to make, recorded so commit 2-6's lanes and the next
revision of window_site.md can rule on it.

- **F-1 (a soundness gap in C-meet on a PARKED alternative).** §2.3 step 1
  merges every span at an offset into ONE position. On a PARKED alternative
  the pinned run R (verify NO) is sound only under a re-seed (§1.1). A
  verify-YES position C-meet merged with R (k0 at 0 with R's exact byte, the
  bounded `{1: any}` with R's next byte) would then TEST R's set without the
  re-seed: e.g. a bounded PARKED site whose R covers offset 1 would filter
  parked candidates by R's byte at 1, which a non-re-seeding PF row must not
  do (today's `pf_memchr_bounded` does not). Built: the plan READS a PARKED
  alternative's verify-NO spans (sets and cores) only where the plan sets
  RE-SEED (C-pin, or the floor row testing every span); `rd_set`/`rd_core`
  in window.c, and the reference's `yes_only` in g2_win_ref.c. A-empty still
  reads the full meet (the alternative's logical candidate set).
- **F-2 (A-model's domain must be core).** B finds the next byte of
  set(d*) INSIDE the subject, so a stop at a non-core position would lose
  the candidates whose stop lies off it. §1.2 states every walked offset
  core ("walked all"), so pcrec's statements are unaffected; the kit's
  A-model only scans walked one-member spans that state their core
  (`scan_ok`). A-parked and A-mass were already core-only.
- **F-3 (Table B is not one table at commit 1).** §2.2 says "Table B IS the
  finder's FIND slot (`fd_rows`)" with PAIR a FIND-slot row. Built without a
  parallel table: B is reached through the row E hands the translated plan
  to: `fd_rows` (D1/D1c/D1w/R7w via the composer's `fd_route`) on a STMT
  frame, and the offset-skip function's own BODY/PREFIX slots (`fn-memchr`,
  `fn-pair` = PAIR, `vrun-*` = SIMD) on a FUNC frame. Folding PAIR into
  `fd_rows` is a restructure of finder.c and ofsskip.c that commit 1's
  zero-mover scope does not need; it is commit 4/6's to do with the reply.
- **F-4 (a legacy row's K96 gap the family can reach).** `pf_walk` admits a
  NOP site stating an `on_miss` at selection and REFUSES it at use
  (pffind.c `pf_walk_use`: "an on_miss is run only where the empty range
  runs the miss"). Today's PF builders never state that shape, but E-stmt
  hands the family's frames to the composer's walk, which picks `pf_walk`
  and then refuses. G2's in-place frame states no on_miss under NOP; filed
  for the kit (a one-line applicability clause in `pf_walk_applies`, zero
  movers, not done here: out of commit 1's scope).
- **F-5 (the empty range, unstated).** The frame drops `end_back` (it is a
  core fact now) but `empty` NOP / EXCLUDED still need "empty". Read: the
  range is empty iff `lo + hy >= n`, `hy` the largest offset >= 0 of a
  verify-YES core position of the chosen alternative (`lo > n` where there
  is none): no candidate can then hold. Two alternatives disagreeing on it
  under NOP are REFUSED (the outcome would be a choice). This reproduces
  today's PF text exactly (`lo + end_back >= n`, the bounded span's `{1:
  any}` being hy 1); window_site.md should state it.
- **F-6 (E-func/E-stmt render through today's rows).** §2.6 says "today's
  `static inline size_t`" and "today's PF block". Built literally: the plan
  is translated into the site today's builders state (one term per compare,
  the stop's term the scanned one, ascending, every term REQUIRED, span 0's
  class and window facts as today, `end_back` from the core, the run's
  ranking as `pcrec_find_run_rank`) and the composer selects as ever. Where
  the translation would not have the plan's semantics (a non-core tested
  position, a full-set position other than the bounded end, a NOP/EXCLUDED
  empty range that would differ) or today's rows do not serve the frame,
  the floor renders. REPORT routes to the floor until S3 (its row RPT
  decides only on an R-26.6 preview). The translation's `consumer` is
  derived from `site_kind` (consumer retires, §4).
- **F-7 (the MARGIN's pairing).** §2.1 says "two alternatives stated". Read:
  only {PARKED, RESEED} is described (any other pair is refused); MARGIN
  holds only where PARKED took A-parked (its `base`) and RESEED took A-model
  (its `best`); otherwise M-parked (the TIE table's PARKED).
- **F-8 (which span is R).** The facts carry no R label. Read: R is the
  first span of two or more positions each one member or a cube (verify is
  not the test: a pre-check run part states YES and §3.4 reads its member
  too). A REPORT stating several such spans (S3) has only the first as R.
- **F-9 (two masses).** A-model uses MASS (capped at 1e6,
  `pcrec_find_set_ppm`); A-mass and the member use PICK's uncapped cube mass
  (`pcrec_find_pick`, `pcrec_find_run_rank`). They differ only when a set's
  rates sum past 1e6.
- **F-10 (mixed A-mass ties).** The TIE table names a stretch row (HIGHER)
  and a set row (LOWER) but not a tie between the two. Composed: walking
  ascending, an equal-mass STRETCH position takes the tie from any earlier
  one, a SET position never does.
- **F-11 (phase 1 reads no frame, so it checks none).** `mf_wdecide` holds
  only the window facts; the frame rules are phase 2's (`wf_check(s, 1)`).
- **F-12 (C-model's ties need the listing order).** prefix_k's exchange sort
  runs over walk-index order; the kit reproduces it over the LISTED order,
  so §1.1's ascending listing obligation is load-bearing (G2 states it).
- **F-13 (the floor row's RE-SEED).** A PARKED floor plan tests every span,
  R included, so it sets RE-SEED where a verify-NO span is stated (§3.5's
  "any plan reading R").
- **F-14 (Table D's reader).** D-one is the floor's resume; a legacy row's
  text resumes at `c + 1` by its own text, as today.
- **F-15 (the hoisted bound subsumes the core test).** "Core positions get
  ONE hoisted bound per candidate" makes a core position's per-position
  off-subject case dead code; the bound is the core rule's whole carrier.
- **F-16 (`mf_ask` vs `mf_emit`).** mf_ask answers mf_define's selection
  (define phases); mf_emit reads the use hooks too, so E-func/E-stmt may
  hold at the query and not at the one-call entry (a use-phase field today's
  row does not serve). G2 compares the query with a same-phase define.
- **F-18 (a table offer is an id).** Appendix A says a table offer names
  pcrec's table; built as today's `table_ref` id per position, rendered
  through the `table_name` hook (rule 7), so `mf_defined.reads_table` says
  whether pcrec emits it.
- **F-17 (`proof_run` had no read-limit layout).** Review S2's
  sentinel-padded exact-size buffers did not exist: `tests/memfn/proof_run.c`
  called every site on a fixed 8-byte stack array. Added: each call repeated
  with the subject at a guard page after n, at one before 0, and between
  SENTINEL pads (twice); each must answer as the plain call. The window
  family's driver carries the same three layouts plus a guard at s + F.

## 6. Charter vs committed

| charter item | committed |
|---|---|
| new site facts in the kit's site description, fields.def rows, appended last, nothing in pcrec states them, no default path reads them | yes (§1) |
| PHASE-1 decision ask, no text; alternative, stop, plan, run member/stretch, RE-SEED | yes (`mf_wdecide`) |
| PHASE-2 text by Tables A-E as declared first-match tables | yes (A, M, E as `kit_table`s; C, D, TIE declared row lists); B via the existing tables (F-3) |
| `plan_cost.def` verbatim with provenance, box, basis; C_VERIFY UNMEASURED DEFAULT | yes |
| TIE table, margin row, C-pin, C-run with W2, three-way edge guard | yes |
| the generic floor | yes (`wf_floor_arm`) |
| D-hors NOT in this commit | not built |
| G2 generates span sites; candidates and completeness against the scalar loop | yes (`run_g2_win.sh`; section 4w of run_g2.sh) |
| proof_run sentinel-padded exact-size buffers | added (F-17) |
| planted defects, each caught | 5 asked + 3 of §5.2's: 8 of 8 red |
| zero movers | nothing reaches the family without the lever; owed: emit_sweep (§4) |
| no pcrec builder edits, no MF_SITE_ABI number change | none, none |
