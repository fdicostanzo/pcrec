# r4ccore — [MEMFN] R-4 / R4c lane CORE: M1 migrates, implement-then-replace, zero movers

Lane r4ccore (opus), 2026-10-06, branch `lane/r4ccore` cut from the kit
branch `lane/memfn-r4c` (d836eb17 = main 691a8b7c + the R-4 ack). Charter:
the kit manager's brief (scope pass `worktrees/r4cscope-scratch/scope.md`
§6 "Lane CORE", rulings `rulings.md`), integration.md rev 4.7 §14, §15,
§16 item 4, §17, §22 R4c. Parallel lanes AXIS (the memfn-simd pair) and
CHECKS (C4/C12/C13/C14 scripts, C17 re-key, VM-hybrid witness) own the
files they own; nothing of theirs was edited here.

## 1. Summary (resume from here)

- **Commits:** `66176e35` IMPLEMENT, `7607c589` IMPLEMENT fix-up (S514
  re-aim), `917a3624` REPLACE, plus this report's commit.
- **The kit renders both M1 sites.** `memfn/src/ofsskip.c` (the offset-skip
  function: memchr arm, pair leapfrog, verify chain, offset legend, call)
  and `memfn/src/precheck.c` (the pre-check composite: one-byte gate, run
  calls, set rest, ASSIGN/ON_MISS) are scalar arms above the generic row.
  pcrec describes the sites through `src/gen/memfn_sites.{c,h,def}`; every
  start decision stays in `emit_dfa.c` (§3, the boundary list).
- **Zero movers.** `emit_sweep --ref 691a8b7c` (default arm, 5 streams):
  0 movers / 0 asymmetric at IMPLEMENT and again at REPLACE. At IMPLEMENT
  the I1 shadow comparator also ran over the corpus at `-fcomments`, both
  engines, `-e utf8` and the 8 M1-relevant denies: 0 comparator failures.
  No abi event (`PCREC_ARTIFACT_ABI` 64 unchanged).
- **Mech:** 20 rows anchored in M1 emitters; 11 re-anchored (8 kit-side,
  3 pcrec-side), 9 unchanged verbatim; S514 (adjacent, memfn_stamps.c)
  re-aimed at IMPLEMENT; [SABANCHOR] all anchors resolve (§4).
- **Q10:** no define-without-use route: `mf_art_end` (now the stamp pass's
  end of every attempt) never fired over either sweep or the 12 I1 arms.
- **Two kit-contract findings** (§6): arm selection must see the define's
  hooks (G2 found it), and the pre-check arm is only correct where `on_miss`
  LEAVES the site — CHOSEN interim fix, ruling requested.
- **Licence:** arms carry SPDX 0BSD + `pcrec 691a8b7c … (relicensed 0BSD by
  its author; ruling pending)`. The merge waits on Frank's Q1 ruling.
- **OWED** (heavy, not this lane's): full `make test`, the mech rows, the
  I2 axis/tier sweep after main's C0, the Linux verdict (§8).

## 2. What was built

### 2.1 The kit (memfn/)

- **Arm interface** (`kit.h`, `compose.c`): an arm writes STRAIGHT TO THE
  SINK in order (previously a kb flushed at the end). pcrec's comment gate is
  a write-time mute whose muted-byte count feeds the size term, so the kit's
  comment bytes must flow through pcrec's StrBuf between `cmt_open` and
  `cmt_close`, and pcrec's `note` hooks must land at the arm's point. The
  generic row still buffers and flushes once (`kit_flush`), unchanged in
  output. `applies(site, def_hooks)`: see §6 F1.
- **`ofsskip.c`** — `ofs_fn_define/ofs_fn_call/ofs_fn_scan/ofs_fn_applies`
  (shared with the pre-check's FUNC parts) and `ofsskip_arm` (FIND / FUNC /
  RETURN; `note(0)` then the legend comment then the function). maxk and
  the scan byte are re-derived from the terms.
- **`precheck.c`** — `precheck_arm` (ALL_PRESENT, STMT, ON_MISS|ASSIGN):
  define writes, per FUNC part, `note(i)`, the run-search comment (tag from
  `note_tag(i)`, "run"/"whole run" by FUNC-part ordinal), the function; use
  writes per predicate `note(i)` and its statement; the first single-byte
  predicate is the `<=`-guarded gate, later single bytes are one `rq_set`
  loop. Per-predicate function names kept on the record (`site_rec.fns`).
- `PROVENANCE.md` rows for both files; `memfn/src/CLAUDE.md` updated.

### 2.2 pcrec (src/)

- **`src/gen/memfn_sites.def`** — DELEG_SITES: `PRE` (ALL_PRESENT,
  ON_MISS|ASSIGN, SET|RUN, scan, ceiling DISCARD — it carries SETREST) and
  `OFS` (FIND, RETURN, SET|RUN, scan, ceiling POSITION).
- **`src/gen/memfn_sites.{c,h}`** — per-attempt `mf_art` (`Job.mf`, begun at
  first ask); the StrBuf sink (`cmt_open` enters a NONESSENTIAL region,
  writes `/* `, returns 1; `legend_byte` = `pcrec_emit_legend_byte`); arena
  adapter; site/pred/term constructors (`MF_P_INLOOP` only from the row
  budget, `MF_P_PORTABLE_ONLY` constant until AXIS's switch, `opts` NULL);
  define/use/call wrappers with `deleg_check` (C10 per row, at compile
  time); `pcrec_memfn_check_use` (C10 per instance); the shared hooks
  (`note` at file scope = `pcrec_runcmp_prepare` of the part's run terms;
  `run_cmp` = `pcrec_emit_run_compare`); `pcrec_memfn_art_end` (unused
  handle; kit includes ⊆ the prologue's, `Job.string_h`).
- **`emit_dfa.c`** — `ofs_pred_of` (OfsTest → one predicate; C14
  `_Static_assert(MF_MAX_TERM >= PCREC_OFSK_MAX_SET + 1)`; maxk/scan-byte
  consistency and the two unreachable shapes fail loudly), `req_site_define`
  (the builder), `pcrec_emit_req_byte_check` (the use + pcrec's handoff
  remainder `emit_req_handoff_rest` + C10), `ofs_site_define`,
  `pf_ofs_call`; pcrec's notes factored out as `req_note_byte/run/rest`,
  the set-rest decision as `req_set_rest_members` (anchored lines kept
  verbatim); `DfaPf.emit_block` takes a non-const `DfaForm` to store
  `ofs_site`; `legend_byte` exported as `pcrec_emit_legend_byte`.
- **`memfn_stamps.c`** — the stamp pass uses the attempt's art and ends it.
- **`sb.c`** — `sb_vprintf` exported as `pcrec_sb_vprintf` (the sink's
  `vprintf` op is exactly the adapter its old comment anticipated).
- **Checks:** C5 (`tests/memfn/arm_fixtures.c`, `pins/arms.tsv`,
  `run_arm_pins.sh`, `make test-memfn-arms`: 8 fixtures × 2 parts, form-id,
  digests, K35 floor 16, `--perturb` witness) and C10's static half
  (`run_deleg_sites.sh`, `make test-memfn-deleg`: budgets vs a literal D91
  list, `mf_vocab_has` probe, `MF_P_INLOOP`'s one home, no by-value
  `mf_site/mf_pred/mf_result` under `src/`, two planted controls). Both in
  TEST_SECTIONS.
- **Manifest** (REPLACE): PRE/OFS/SETREST `delegated`, emitters re-pointed
  to the builders (Q4); rule 3 now non-vacuous; memchr( in src/gen 8 → 2.

## 3. THE BOUNDARY LIST, as kept (main's start-table fold edits these)

Every start-decision read left on pcrec's half, at `917a3624`
(`src/gen/emit_dfa.c` unless named):

| # | file:line | what it reads |
|---|---|---|
| B1 | 1405 (`req_site_define`) | `pcrec_fact_req_byte`, `pcrec_fact_req_run(cx)->len < 2` — "nothing necessary" (row `none` of `req_admits[]`): no site |
| B2 | 1406 | `req_admit_emits(req_admit(cx))` — the admission (`req_admits[]` 7202, `req_admit` 7224): no site |
| B3 | 1407 | `pcrec_fact_req_run(cx)->len >= 2` — run form vs one-byte form |
| B4 | 1408-1411 | `req_lead_byte(cx)` (`set-leads`, 7231) — the gate predicate and its byte; `pcrec_artifact_has_dfa_scan` → its need (OPTIONAL on a DFA-scan route, else REQUIRED, §14.5) |
| B5 | 1413 | `req_use(cx) == REQ_USE_HANDOFF` (`req_uses[]` 7317, `req_use` 7333) — ASSIGN/`ret_pred`/`use` |
| B5′ | 1514 (`pcrec_emit_req_byte_check`) | `req_use(cx)` again — the expression the body reads (`fwd.from`/`first`); C10 per instance at 1515 |
| B6 | 1039 (`req_run_tests`) | `r->len < 2 || !req_admit_emits(req_admit(cx))` |
| B7 | 1043 (`req_run_tests`) | `pcrec_artifact_has_dfa_scan(cx) || r->whole_len <= r->len` — whole-run presence; 1290 (`req_set_rest_members`) the set rest's route |
| B8 | 1297, 1298, 1300, 1303 (`req_set_rest_members`) | set-rest membership: exact whole-run positions, `pcrec_fact_req_byte`, the lead, `pcrec_fact_req_set` |
| B9 | 1158-1164 (`emit_req_handoff_rest`) | `pcrec_fact_req_run_maxoff` (K), `pcrec_emit_start_zero(…ROUNDUP)`, the `[K82]` comment, clamp and subtraction, written after `mf_use`; 1416 asserts handoff ⇒ the window is the last predicate |
| B10 | 8804 (`emit_unanchored`), `dfa_pfs[]` 6816, `DFA_SELECT_ROUTED` 6860/6888 | the prefilter row → `pf->emit_block` (`pf_block_ofs` 6411), `pf->run_term` |
| B11 | `ofs_test_of` 6204, `ofs_test_model` 6189, called 8337 (`dfa_form_derive`) | `us->ofsk` (prefix_k: sel/scan/maxk), `us_run_pin`, `pf->run_term` — the k-set selection; `ofs_pred_of` 1073 only translates it (plan_hint = the scan) and checks maxk/scan byte (1077, 1114) |
| B12 | kit-side now | the legend's deny literal keyed by run-term presence (`ofsskip.c` `legend`) — a form choice, not a decision read |
| B13 | 8807, 8829 (`emit_unanchored`); 9105, 9120 (`emit_attempt`); `src/gen/emit_vm.c` 13118, 13189 | `fit.chosen == ENGM_DFA` define/use guards (VM: unconditional) — untouched |
| B14 | 8832 | `req_handoff_assert_body` — untouched |
| B15 | 9961, 10192 (`pcrec_emit_prologue`) | `req_admit` → `<string.h>`; `Job.string_h` recorded for the kit-includes assertion |
| B16 | 10443 | `DFA_PREFILTER_OFFSETS` stamp: `ofs_test_of`, `ofs_test_at` — untouched |
| B17 | 335, 7342 | `req_handoff_stamp`, the REQ_* stamps — untouched |
| B18 | `src/opt/prefix_k.c` | the k-set model — untouched |

Not decisions (now kit form choices): the pair-arm dispatch, the `k == 0`
spelling, verify order, the comment variants, the set-rest table loop.

## 4. Mech rows

20 rows anchor in the M1 emitters (scope §3's table, re-checked at REPLACE):

| row | was | now | how |
|---|---|---|---|
| S464 | `emit_req_handoff` decl printf | `memfn/src/precheck.c` `run_line` ASSIGN miss line | **re-anchored, kit** (plant: hand off the next occurrence) |
| S265 | `emit_req_one_byte` | `precheck.c` `gate` | **re-anchored, kit** |
| S454 | `ofs_test_emit_fn` pair dispatch | `ofsskip.c` `ofs_fn_define` (`if (0 && b >= 0)`) | **re-anchored, kit** |
| S185 | `ofs_test_emit_fn` resume | `ofsskip.c` memchr arm `pos = cand + 1` | **re-anchored, kit** |
| S447 | `ofs_test_emit_pair` second member | `ofsskip.c` `ofs_fn_scan` | **re-anchored, kit** |
| S450 | `ofs_test_emit_pair` re-search bound | `ofsskip.c` `pair_body` `lim` | **re-anchored, kit** |
| S455 | `ofs_test_emit_pair` locals | `ofsskip.c` `pair_body` | **re-anchored, kit** |
| S279 | `ofsk_emit_verify` run offset | `ofsskip.c` `verify_chain`'s `run_cmp(…, t->offset + 1, …)` | **re-anchored, kit** |
| S285 | `ofsk_emit_verify` `PcrecRun` | `src/gen/memfn_sites.c` `run_of` (Q11: pcrec-side) | **re-anchored, pcrec** |
| S460 | `pcrec_emit_req_byte_check` lead-first calls | `req_site_define`'s predicate order (runs before the gate) | **re-anchored, pcrec** |
| S511 | `emit_req_one_byte` (C17 stale PRE) | MLINE's `emit_attempt` memchr literal (PRE is delegated) | **re-aimed, pcrec**; `SAB_REACH_POP` → the MLINE row; planted: C17 rule 4 FAILs, restored: 0 |
| S463, S471, S470 | `emit_req_handoff` | `emit_req_handoff_rest`, verbatim | unchanged anchor |
| S277, S316, S452, S459 | `emit_req_set_rest` | `req_set_rest_members`, verbatim | unchanged anchor |
| S278, S449 | `req_run_tests` | same | unchanged anchor |

Count: **20 = 11 re-anchored (8 kit + 3 pcrec) + 9 unchanged.** Adjacent:
S514 (`memfn_stamps.c`, the stamp expression) re-aimed at IMPLEMENT; S472
(`pcrec_emit_start_zero`), S293/S287/S448 (`ofs_test_run`/`ofs_test_of`),
S186, S267 untouched. Changed detection paths: **S287** and **S293** now
fail the compile loudly through `ofs_pred_of`'s consistency check (planted
by hand: `internal error: an offset-k skip's memfn description disagrees
with its test`) instead of reaching the artifact — the kit derives maxk and
the scan byte itself. Each re-anchored plant was applied by hand and shown
to move the reach pattern's artifact (or, S511, to trip C17); the detector
runs are OWED (§8).

## 5. Validation

| run | result | log |
|---|---|---|
| `emit_sweep.py --ref 691a8b7c --bin <IMPLEMENT>` | 5 streams 0 movers 0 asymmetric; self-check passed; reach 4159/4160/4160/38/7 | `build/scratch/sweep1.log` (worktree scratch) |
| I1 over corpus argv (4606) × 12 arms: `-fcomments`, `-fcomments --engine=vm`, `-fcomments` × each of `-fno-offset-skip -fno-req-byte -fno-req-run -fno-run-prefilter -fno-req-run-fold -fno-req-set-lead -fno-req-handoff -fno-run-overlap`, `-e utf8`, `-fcomments -e utf8 --engine=vm` | 0 comparator/kit internal errors; ok/refuse counts equal the default sweep's | `build/scratch/i1arms.log` |
| `emit_sweep.py --ref 691a8b7c --bin <REPLACE>` | 5 streams 0 movers 0 asymmetric | `build/scratch/sweep2.log` |
| `make strict` | clean (both commits) | |
| `make test-memfn-link/-manifest/-arms/-deleg/-stamps` | 8/22→19/36/5/12 passed, 0 failed (REPLACE) | |
| `make test-memfn-g2` (quick) | 21,707,515 passed, 0 failed (after F1's fix) | |
| `make test-codegen` (IMPLEMENT) | all sections green except [SABANCHOR] (S514), fixed in 7607c589 | `build/scratch/codegen1.log` |
| `make test-codegen` (REPLACE) | CODEGEN-EXIT 0, [SABANCHOR] all anchors resolve | `build/scratch/codegen2.log` |
| `make test-registry`, `make test-rxtsource` (REPLACE) | 0 failed each | `build/scratch/test-registry.log`, `test-rxtsource.log` |

## 6. Findings for the kit manager

- **F1 (G2 found it): an arm must not apply where it needs a hook the
  caller does not offer.** The first build selected `ofsskip` for G2's FIND/
  FUNC sites with no `run_cmp`; two refused. Fix: `arm.applies(site, def)`
  sees the define's hooks; the scalar arms decline without `fn_name`,
  `run_cmp` (a RUN term), `table_name` (a multi-byte set). G2 then reads 0
  failed. Note G2 now reaches the precheck arm on none of its sites (§F2:
  G2 passes no `on_miss` at define) — coverage of that arm is I1 + C5.
- **F2 (contract gap, ruling requested): the pre-check arm is correct only
  where `on_miss` LEAVES the site.** Its predicates run in sequence after a
  miss and its set rest has no empty test (EXCLUDED in place), right for
  pcrec's `return 0;` and wrong for G2's mode-0 `missed = 1;` (on_miss
  repeated, and `memchr(s + lo, c, n - lo)` with `lo > n`). The contract
  says on_miss is a statement the kit places, not whether it leaves.
  CHOSEN interim: the define's hooks carry `on_miss` too and the arm
  applies only where its last statement begins with `return`/`goto`/
  `break`/`continue` (`miss_leaves`); the use's on_miss must agree. That
  READS a hook string, which §14.1 says the kit never does. Recommendation:
  rule that an ALL_PRESENT ON_MISS/ASSIGN site's `on_miss` leaves the site
  (pcrec's always does), or give the kit a bit; then delete `miss_leaves`.
- **F3 (CHOSEN): file-scope `note` is pcrec's text for a FUNC part**, used
  to write the run compare's word-load helpers (`pcrec_runcmp_prepare`)
  where pcrec wrote them, before each part's comment. The composite has two
  FUNC parts whose helpers may differ (a 4-byte window and a 9-byte whole
  run), so pcrec cannot write them all before `mf_define` without moving
  bytes. Dissolves at M1b (helpers become the kit's, §14.8).
- **F4 (CHOSEN): the sink's `cmt_open` always answers open** and writes the
  opener into a muted region when comments are off, so `cmt_dropped` (the
  size term's input) counts the kit's comment bytes exactly as pcrec's.
- **F5 (CHOSEN):** the offset-skip function's parameters/locals are the
  arm's own names; the define ignores `s/n/lo`. "run" vs "whole run" in the
  run-search comment is keyed by FUNC-part ordinal.

## 7. Dependencies on the parallel lanes

- **AXIS:** `memfn_policy()` (`memfn_sites.c`) returns `MF_P_PORTABLE_ONLY`
  constantly; it should read the memfn-simd bit when AXIS lands (one line).
- **CHECKS:** C12's ceiling literal 8 → 2 (memchr) belongs in CHECKS's C12
  file, which is not on this branch: lower it at merge (C17's information
  line reads 2). C17's dynamic half still keys on `mf_emit_site` (re-key to
  `mf_define`/`mf_use`/`mf_call`, Q3). The VM-hybrid witness row.
  Sabotage rows for C5/C10 (§17.6) are CHECKS's numbering.

## 8. OWED runs (heavy — the kit manager's slot)

- Full `make test` on the Mac (detached), e.g.
  `cd worktrees/r4ccore && nohup caffeinate -s make test CC=gcc-16 > build/scratch/test.log 2>&1 &`;
  completion = the test trailer; verdict = `*** [test-X] Error` lines.
- The mech rows: `bash tests/mech/run_sabotage_matrix.sh S464 S265 S454
  S185 S447 S450 S455 S279 S285 S460 S511 S514 S287 S293 S463 S470 S471
  S277 S316 S452 S459 S278 S449` (each must read DETECTED).
- I2 over every axis × both tiers after main's C0 (`--extra`), Linux via
  the executor; plus `--emit-facts` (the pre-check builder asks at the
  define point what pcrec asked at the use point; same calls, same
  conditions — unverified by a sweep stream).
- The Linux verdict through the executor.

## 9. Charter vs committed

| charter item | state |
|---|---|
| kit baseline arms, byte for byte | DONE (ofsskip.c, precheck.c) |
| builders filling mf_site, opts NULL | DONE |
| per-attempt mf_art | DONE (`Job.mf`) |
| I1 shadow comparator, fail loudly | DONE at IMPLEMENT, deleted at REPLACE |
| DELEG_SITES with `use` ceiling, per-instance req_use, C10 | DONE |
| C14 asserts | DONE (`_Static_assert` in `ofs_pred_of`); CHECKS's compile check pending |
| arms.tsv recorded | DONE (C5) |
| licence header, ruling pending | DONE |
| REPLACE: emitters write kit text, replaced code deleted | DONE |
| manifest rows → delegated, emitters re-pointed | DONE |
| mech re-points with count | DONE (20: 11 re-anchored, 9 unchanged) |
| C12 ceiling 8 → 2 | DEPENDENCY (CHECKS's file absent) |
| src/gen/CLAUDE.md "edit in memfn/" | DONE |
| zero movers | DONE (default arm + 12 I1 arms); full I2 OWED |
| boundary list, Q10 finding | §3; Q10 none |
| make, strict, test-codegen, registry, rxtsource, quick memfn, emit_sweep | DONE, all green |
