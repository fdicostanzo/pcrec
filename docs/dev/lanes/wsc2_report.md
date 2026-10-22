# wsc2 — D172 S2: the kit's rulings on commit 1, commit 2 (pcrec states spans), commit 3 (the trace shadow)

Lane wsc2 (kit lane of the memfn kit manager), 2026-10-22. Worktree
`worktrees/wsc2`, branch `lane/memfn-wsc2`, cut from `lane/memfn-wsc1` @
3cd809da1 (D172 commit 1). Build go: Frank's conditional go (critics GO,
main agreed); request R-29; design `docs/design/memfn/window_site.md` rev 3.2
§5.1. No rulings file was named.

STATE AT HANDOFF: three commits, every light check green at each commit's
tip (§3). The FULL corpus shadow ran and is reported by column (§4). The heavy
job (emit_sweep ×4 vs 3cd809da1, then make test) is QUEUED and OWED (§5).

## 1. The commits

| # | sha | scope | what |
|---|---|---|---|
| (a) | 110e1437c | KIT PATH (memfn/, tests/memfn/, the wsc1 report's id table) | Plant ids WSC1-P1..P8 renamed to S1400..S1407 and WSC1-R1 to S1408. The F-8 ruling: R is identified by its SHAPE and must be UNIQUE, so `wf_check` refuses a second R-shaped span in one alternative. Plant S1409 covers the refusal. |
| (b) | 4ad027ee9 | PCREC PATH (src/ only, plus ONE sabotage re-aim under tests/mech, §6 D-7) | D172 §5.1 commit 2: pcrec states R-29's facts beside the old fields. Zero movers by construction. |
| (c) | ae35dcad4 | KIT PATH (memfn/ only) | D172 §5.1 commit 3: the trace SHADOW (`wf_shadow`, lever `MF_WSHADOW`) and its script `memfn/tests/wshadow.py`. |

Main reviews (b) separately: it touches no file under memfn/.

## 2. Builder → fact mapping (against R-29's fact table)

Every statement is built by `pcrec_memfn_window_stated` (src/gen/memfn_sites.c), which checks pcrec's own bounds against the kit's shape bounds (MF_WMAX_ALT, MF_WMAX_SPAN, MF_WSPAN_POS, [-MF_MAX_BACK, MF_WREACH)) and fails loudly past one. The kit's `wf_check` also holds each statement on every DEFAULT art (compose.c `window_route`), so a malformed statement fails the compile. None did over the whole test suite (§3).

| R-29 site | builder | alternatives (ENTRY) | spans, core, verify | table offers | floor |
|---|---|---|---|---|---|
| PF, PF bounded, the hybrid's PF (the forward DFA prefilter) | `find_site` ← `pf_site_of` ← `pf_window_of` (emit_dfa.c), both the define (`pf_find_of`) and the readers' query (`cand_pf_site`) | PARKED; plus RESEED where `-fno-offset-skip` is not given and prefix_k's own gate holds (k0 has 1-255 members, the walk is stated) | PARKED `{0: k0}` YES, core all (bounded: `{0: k0, 1: any}`, core [0,2)), plus R ONLY under §1.1's pin fact. RESEED `{0: F0}` YES (bounded: `+{1: any}`), then EVERY walked offset k ≥ 1 as its own one-position span, verify NO, core [0], in walk-index order, then R | k0: `<p>_can_begin_match`. F0 and each walked offset with ≥ 2 members: `<p>_ofs_k<k>` | SUBJECT |
| the offset-skip block | `ofs_site_define` ← `pf_window_of` | the same as PF | the same, with NO D11 `{1: any}` (§6 D-5) | the same | SUBJECT |
| MLINE, both callers (`dfa_cand_scan`'s query and the attempt loop's emit at emit_dfa.c ~14059) | `find_site` ← `mline_find_of` → `find_window` | one, NONE | `{-1: \n}` YES, core [0,1) | none | EXPR (`floor` hook `start`) |
| the VM hat seek | `find_site` ← `vm_hat_find_of` → `find_window` | one, NONE | `{0: S}` YES, core all | `<p>_start_set` | SUBJECT |
| Z2's cover site | `pcrec_cover_site` → `cover_window` (known.c) | one, NONE | span 0 `{0..k-1: S_d}` YES, core [0,k). One span per stated context side (at -1, at k), YES, core its position where absence FAILS and empty where it SATISFIES | none | SUBJECT |
| the pre-check's FUNC parts | NOT STATED | — | — | — | — (§6 D-1) |
| frequencies | unchanged: the byte-rate on `mf_art_begin` | | | | |

**R (the run):**
- What R is: the necessary run's window (`req_run`), stated as positions (exact = one member, cube = two) at offset `o - at`, the offset its pinned stretch fixes (`run_pin`).
- Verify NO, core all.
- Never stated as a member or a stretch.
- Not stated under `PCREC_NO_OFFSET_SKIP` or `PCREC_NO_RUN_PREFILTER`, nor where the pin would place the window below the match start (`o < at`).
- In PARKED only where all of these hold: w = 0; R's position 0 is exact; the kind is DFA_PF_ONE_BYTE; k0 = {that byte}; F0 = {that byte}.

**Facts read without a pass:**
- `pcrec_fact_req_run_stated`, and the new `pcrec_fact_run_pin_stated`. They are read only where prefix_k already weighed the walk (`us->ofsk.walk`), so the byte-rate has already been asked.
- So neither the facts' `used` record (the `facts` stream) nor the `_FINDINGS` consulted population can move.

**No D157 breach:** nothing here ranks, picks, prices or plans. No rank, no `plan_hint`, no member, and no selection-dependent table list is computed for the new statement. The offers are every walked offset's table that pcrec can emit; which ones the text reads is the kit's `mf_defined.reads_table`, F-18.

## 3. Checks (Linux dev box, gcc 15.2)

| check | (a) 110e1437c | (b) 4ad027ee9 | (c) ae35dcad4 |
|---|---|---|---|
| `make strict` | clean | clean | clean (re-run after the amend) |
| `python3 -I scripts/m6read_check_sab_anchors.py` | 901 rows / 932 sites resolve | first run: 1 STALE (S1085, its anchor quoted `pf_site_of`'s old signature). Re-aimed in (b) (§6 D-7), then all resolve | all resolve |
| `bash tests/codegen/run_codegen_tests.sh` | 331 passed, 0 failed | the first run's 1 failure was the same S1085 anchor (SABANCHOR). After the re-aim: 331 / 0 | 331 / 0 |
| `make test-core` | rc 0 | rc 0 | rc 0 |
| `make test-memfn-{link,manifest,stamps,arms,deleg,arch,forms,reach,rows,finder,rank,guarded,simdfloor,g2}` | each rc 0 | each rc 0 | each rc 0 (rows re-run after the amend: rc 0) |
| G2 quick (`test-memfn-g2`) | checks passed 71,217,801, failed 0 | the same | the same |
| `bash memfn/tests/run_g2_win.sh` | GREEN 6032 / 0 (the floor `two_runs`: 86 refused, floor 77) | GREEN | GREEN |
| `run_g2_win.sh --plants` | 9 of 9 RED: S1400-S1407 as wsc1's, S1409 "two runs: an alternative stating two spans of R's shape was decided" | — | — |
| `run_proof.sh --plant S1408` | RED (READS: a fault, guard at s + n) | — | — |
| zero movers, sample (b) | — | 22 patterns × {default, `--engine=vm`, `-fno-offset-skip`} = 66 triples, `.c` + stderr + rc + `--emit-facts` against a 3cd809da1 build: 0 differ. Includes offset-set, offset-set-bounded, run-pinned and memchr artifacts | — |
| emit_sweep vs 3cd809da1, every arm | — | QUEUED (§5) | QUEUED (§5) |

The (c) column's light run went through `build/wsc2/light.sh`. Its logs are in `build/wsc2/light_{a,b,c}/`.

## 4. The trace shadow's mismatch counts by column

`memfn/tests/wshadow.py` works as follows:
- It builds a pcrec over the MF_TRACE kit.
- It compiles the emit_sweep corpus at the default engine and at `--engine=vm` under `MF_WSHADOW=1`.
- It counts the `MFTRACE WSHADOW` records whose old and family values differ, per column.
- The `group` column is compared canonically: each compare is renumbered by its first appearance.
- Every mismatch is written to `OUT/mismatch_<column>.tsv`.

**FULL reading** (`scripts/boxlock run --label wsc2-wshadow`, at the (c) tip):
- 5811 corpus patterns, 11,622 compiles, 0 timed out.
- 7087 window sites shadowed.
- Family paths: mass 4111, parked 2245, parked+pin 44, reseed 523, reseed+pin 129, empty 35.

| column | reseed | stop | plan | pin | group | arm | text |
|---|---|---|---|---|---|---|---|
| mismatches | 0 | 35 | 558 | 0 | 558 | 45 | 45 |

Two classes cover every mismatch:

1. **523 sites (plan, group; 45 of them arm and text).** The default engine's BOUNDED PF site, entry PARKED, path `parked`, old plan `-`, family plan `1`.
   - On 45 of these, the two-term translation renders `pf_walk` where today's text is `pf_memchr`.
2. **35 sites (stop, plan, group; text equal).** The VM hat on `\p{Cn}`/`\p{Co}`-shaped patterns (tests/utf8/axis04_p_categories.rxt), where the start set S is EMPTY.
   - Old: stop 0 over an empty set. Family: A-empty, no stop (`stop -999`, path `empty`).
   - Both texts hash the same. This is a representation difference in the columns, not a text move.

The sampled first reading (`--every 160`, 37 patterns, 48 sites: plan/group 3, arm/text 1) showed only class 1.

Class 1 in detail:
- The bounded PF site's D11 position `{1: any}` is a verify-YES core position.
- C-yes therefore puts offset 1 into the family's plan (old plan `-`, family `1`).
- On `((?<!a)z)` that turns a two-term translation into `pf_walk` instead of today's `pf_memchr`, so the `arm` and `text` columns differ too.
- Where the bound lives at commit 4 is the next lane's question: an all-256 core position as `end_back` in the translation, or dropped by C-yes.

The `reseed`, `stop` and `pin` columns read 0. On the sampled RESEED and pinned sites (uuid, `x[ab]cdefg`, `[ab]c+d`), the family's text hash equals today's.

Log: `worktrees/wsc2/build/wsc2/wshadow.log`. Records per column: `build/wsc2/wshadow/mismatch_<column>.tsv`. The same run's `--g2` half ended `G2 span sites (run_g2_win.sh, the reference's columns): rc 0, checks failed: 0`.

**G2's generated span sites have no old fields, so they have no old path to shadow.** Their comparator is G2's reference decision (g2_win_ref.c: prefix_k's rules transcribed from the design). Column by column (DECIDE: alt/stop/plan/grouping; PLAN; PROOF) it reads 0 mismatches: run_g2_win.sh, checks failed 0.

The shadow shares the family's MODEL with prefix_k, so it is a localizer and NOT acceptance (review "seq").

## 5. The queued heavy job

`576-kit-wsc2-heavy`:
- Kit band, `idle-ok`, cap 14400 s.
- Its `--ready` starts with main's hold line on `i2build-parity`.
- The job file is `build/wsc2/576-kit-wsc2-heavy`.

At the lane tip it runs, in order:
1. `make -j16`.
2. `emit_sweep --ref 3cd809da1` four times: plain streams `c-default,c-vm,emit-ir,composition,facts,emit-ir-auto,stderr` (dumps excluded), `--arms start`, `--extra=-fno-run-prefilter`, `--extra=-fmemfn-simd`. Each needs zero movers.
3. `scripts/perfrun --label wsc2 -- build/wsc2/heavy/maketest.make.log`.

**Completion lines:**
- Four `emit_sweep: DONE rc=0` (the declared population, `expect sweeps=4`).
- `== wsc2 heavy: 0 step(s) failed`.
- The make verdict is `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/wsc2/heavy/maketest.make.log` (empty = green). Read it with `scripts/verdict`.

**Logs:** `worktrees/wsc2/build/wsc2/heavy/{build,sweep_plain,sweep_arms,sweep_norun,sweep_simd,maketest}.log`, and the queue's job.log under `worktrees/.boxqueue/done/<ts>-576-kit-wsc2-heavy/`.

The first enqueue started at 02:37 while the tree held my uncommitted (c) amend. It was refused at START ("DRY-RUN-FAILED ... worktree dirty", `worktrees/.boxqueue/failed/20261022T023700.903115893-576-kit-wsc2-heavy`) and RE-QUEUED on the clean tip. The job's dry run needs the worktree CLEAN when it starts, so do not edit `worktrees/wsc2` until it has run.

OWED: both verdicts. A fresh agent reads them.

**Derived sabotage list (§5.4) for (b):**
- 87 rows name a file (b) touches: emit_dfa.c 79, memfn_sites.c 7, facts.c 1.
- All anchors resolve after the S1085 re-aim.
- The rows naming a function (b) edits are S1085 (re-aimed), S1138, S223, S284 and S490. Their anchors lie outside the changed hunks, so their intent is unchanged.
- `REACH_ONLY=1` over these rows is NOT run, and is owed with commit 4's NEXT change. Commit 2 moves no reach: no NEXT row reads the new facts.

## 6. Deviations and findings, with evidence

- **D-1 (the pre-check's FUNC parts are not stated).** There are two reasons:
  - The kit refuses window facts on a default-art site with no pred terms: compose.c `window_route`, "a site stating only window facts renders only on an art previewing...". The pre-check is an ALL_PRESENT site whose parts are `preds[]`, and its `pred.nterm` is 0. Stating facts there would fail every pre-check compile.
  - A pre-check has up to two FUNC parts, `<p>_reqrun` and K66's `<p>_reqrun_whole`. These are two candidate definitions, and one site-level statement holds only one. Even one alternative with "one span per part" (§1.2) would hold two R-shaped spans, which the F-8 refusal rejects.
  - Asked of the kit manager (message, 2026-10-22). The leaning: a per-part statement (window facts per `mf_pred`), a kit field, filed for commit 4.
- **D-2 (the DFA hat).** §1.2's PF row names `{0: k0}`. The DFA hat's rows (first-memchr-bounded, first-class-bounded) scan T = start_set, not k0, and re-seed where they moved.
  - Stated: PARKED `{0: k0}` everywhere on the forward DFA prefilter. This is the fact §1.2 names, and MARGIN's `base` is prefix_k's.
  - T is a fact of the NEXT row's frame. How the family renders a hat at commit 4 is open.
- **D-3 (R's offset comes from the pin).**
  - `run_pin`'s stretch is chosen by a rate pick (`pcrec_run_pin`'s selection, which retires at commit 6). Here it is read only for the window's offset `o - at`, never its member or stretch.
  - Soundness note for main: R's CUBE positions outside the pinned exact stretch are not walk-proven at that offset. The pin proves the exact stretch only. A verify-NO span claims every match satisfies it.
  - Today's `ofs_test_verifies_run` reads the window at the same offset. But nothing today TESTS those cube positions on that claim.
  - The kit reads R's positions only under C-pin, which compares the exact stretch, or under a PARKED floor plan.
- **D-4 (one offer id space).**
  - The PF site's table ids (PcrecFindTable) and the offset-skip site's (k + 1) collide. So the window offers use `WIN_OFFER_FIND + t` and `WIN_OFFER_OFS + k`, and both `table_name` hooks resolve both (`win_offer_name`).
  - Every multi-member walked offset is offered, not only today's selected ones. The tables the text reads are the kit's `reads_table` (F-18).
- **D-5 (the D11 bound per builder).** The PF site's bounded statement carries the core `{1: any}` (today's `end_back` 1). The offset-skip block's FUNC returns any candidate below n, and its caller clamps, so it states no bound. Each builder's statement mirrors its own old fields. The shadow (§4) shows the bound's position entering the family's plan.
- **D-6 (the shadow's `text` column).**
  - It is each side rendered the SAME way on a scratch art, then normalized-hashed (`mf_form_hash_text`). The rendering is one call, or define then use with the define's hooks.
  - It is not the artifact's bytes. emit_sweep at commit 5 is that witness.
  - G2's half is the reference's verdict (§4).
- **D-7 (a test file in the pcrec-path commit).** S1085's anchor quoted `pf_site_of(cx, pf, ...)`, so it was re-aimed in (b) to the new signature. The intent is the same: the readers' PF site carries E, not the row's scanned set. §5.4 puts re-aims in the step's commit. It is the only non-src file in (b).
- **D-8 (F-8's scope).** The uniqueness refusal applies to EVERY alternative (NONE entries included: REPORT, parts), not only RESEED. That way no list order decides R anywhere.
  - G2 generates such alternatives in FAM_MASS/REPORT/RANDOM. The generator counts the refusal (`two runs refused`, floor 77), then gives every extra R-shaped span a three-member position 0. The run's RNG stream is unchanged.
- **D-9.** Z2's cover is not stated where k = 0. The RESEED alternative is stated wherever the walk has offset 0 (nwalk ≥ 1), even with no walked offset.
- **F-4** (pf_walk's K96 gap) is FILED as ruled, not fixed. **F-1, F-3, F-5, F-6, F-7** are accepted as built.

## 7. Charter vs committed

| charter item | committed |
|---|---|
| (a) rename WSC1-P1..P8 → S1400..S1407, WSC1-R1 → S1408 everywhere (run_g2_win.sh, run_proof.sh, the report's table) | yes (also memfn/tests/CLAUDE.md, tests/memfn/CLAUDE.md); the kit journal's past entry is append-only, left |
| (a) F-8: R by shape, unique, loud refusal, plant S1409 | yes (§6 D-8) |
| (a) F-1/3/5/6/7 accepted, F-4 filed | yes, no change |
| (b) src/cli/lib/docs-spec only | src/ plus one sabotage re-aim (D-7); no spec hunk (nothing caller-observable moves) |
| (b) PF, PF bounded, MLINE both callers, VM hat, offset-skip block, pre-check FUNC parts, Z2 cover | all but the pre-check parts (D-1) |
| (b) zero movers by construction, old fields stated, old arms render | yes; sample 66/66 identical; full sweep queued |
| (b) exactly R-29's facts (spans, unordered alternatives with ENTRY, offers, floor; frame and frequencies as today) | yes (§2) |
| (b) R as positions, never a member; R in PARKED only under the condition; not under the two denies; walked offsets one-position in walk-index order | yes |
| (b) no NEXT-row change, no deletion, no stamp change | none |
| (c) the trace shadow: family columns beside the old path's, mismatches by column over the corpus and G2 | yes; full corpus read (§4); G2 via its reference (D-6) |
| light checks after each commit | §3 |
| heavy job 576-kit-wsc2-heavy, idle-ok, main's hold line | queued |
