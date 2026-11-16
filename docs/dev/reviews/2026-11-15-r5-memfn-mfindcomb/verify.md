# VERIFY findings (round memfn-mfindcomb)

## FIDELITY-1

**HOLDS** (all three legs reproduced; consequence magnitude PARTLY: real per-hit overhead, size untimed).
- TU: copied fidelity/rd_ctrl/JMH/obj/arm24.c (kit.find_hit.mfind-w32.periodic.one.32.50) to verify/f1/. Compiled with link.py's own line (link.py:36 CC + 451): `gcc -std=gnu11 -O2 -march=x86-64 -mtune=generic -c -DSYM=a24 -DCAND_STRIDE=64u -DPOOL_BYTES=16777216u -I<slot> arm24.c` -> rc=0. `nm`: `T a24_gate`, `T a24_time`, `t mf_fn__w32`; `objdump --disassemble=a24_time`: `2f5: call 0 <mf_fn__w32>` inside the loop.
- `_gate` deleted (verify/f1/nogate.c, only lines 138-149 removed; diff shown), same flags, rc=0: `nm` -> only `T a24_time`; `objdump ... | grep -c call` -> 0. Cause = the second caller (`_gate`, link.py:249) of the always_inline `step` -> static finder with two call sites stays out of line. HOLDS.
- pcrec side: `kit/lever.sh verify/lv 'xy[0-9]+z' 'aaxy12zbb' -fmemfn-simd=x86-64-v3` -> `MFIND-REACHED yes`, on/off/oracle `match 2 7`, AGREE; `gcc -O2 -c on/rx.c` rc=0: no local finder symbol (`rx_ofsskip__w32`/`rx_reqrun__w32` absent from nm), all 8 vpcmpeqb are in `rx_search`; rx_search's only call relocation is `memchr` (another site), none to a finder. HOLDS.
- Per-hit path (static count, no timing), from the hit's `cmpw $0x7978` to the next scan `vpcmpeqb`: out-of-line 27 instructions (callee `jne, vzeroupper, ret`; caller `cmp, jb, lea, add, cmp, jae, call`; callee re-entry `lea, cmp, jae, lea, mov x3, vmovd, sub, vpbroadcastd, cmp, jbe, mov, sub, cmp, jbe`) vs inlined 19 (no call/ret/vzeroupper, the 0x78 broadcast hoisted out of the loop at a24_time+0x10..0x2e). So +8 instructions incl. call+ret+vzeroupper and a vmovd->vpbroadcastd dependency feeding the next compare. Plausibly material at small gaps (gap 2-8: a hit every few bytes, the per-hit tail dominates) and negligible at gap >= 256; direction biases the fused cost UP, i.e. toward D197's "loss" branch. Magnitude NOT measured (clock forbidden).

## contract-2

**HOLDS** (upgraded SUSPECTED -> CONFIRMED by load).
- Draft produced by est's own synth + write_draft (draftsets/plants.py copied to verify/ds, slot copied fresh from the review tree): `SLOT_TREE=<review> python3 -I plants.py verify/ds/runs P0` -> `P0_control: WRITTEN`; draft.v6.tsv (zen4-grid6, 66 rows), draft.v6-v3.tsv (zen4-grid6-v3, 22 rows), draft.tsv (zen4-grid3, 11 rows incl. walk). Header of draft.v6.tsv: `unit_key	kit.find_byte.walk`; `grep -c kit.find_byte.walk draft.v6.tsv` -> 1 (the header line only).
- Loaded with the review tree's loader: `build/pcrec -p rx --measures=<draft.v6.tsv> -o o.c --pattern abc` -> rc=1, `unit_key 'kit.find_byte.walk' names no row`; same for draft.v6-v3.tsv (rc=1, same message; src/core/ks_measures.c:598-599). Control: draft.tsv passes that check and is refused later for an unrelated reason (`zen4-grid3@1 is a committed measurement set with different values; rename the set`), so the loader reaches the unit check and only the ver-6 sets fail it.
- Selftest PINS the refused shape: est.py:1440-1442 `mf_write` requires `set(sets["6"]) == six` (FORMS6 keys only, plan.py:151 has no walk) and `plan.UNIT_KEY in sets["3"]` with `not six & set(sets["3"])`; mf_split (1403-1405) the same; write_draft hard-codes `("unit_key", plan.UNIT_KEY)` for every ver (est.py:941).
- Context: BASE's est.py:882 writes the same header for the ver-4 set (record.SETS has `"4": "zen4-grid4@1"`), so the shape predates the subject; no zen4-grid4 set was ever committed (measure_store holds zen4-grid1, zen4-grid3 only). The subject adds two more sets with the defect.

## FIDELITY-2

**HOLDS.**
- Code: est.py:631 calls `fused_facts(... [k for ... if k.startswith("kit.verify_cmp.")] ...)`; `manifest_check` (est.py:353-376) has exactly one caller, est.py:408 inside fused_facts (`grep -n manifest_check est.py` -> 353 def, 402 docstring, 408 call). The mfcard window (J2 J2p JMB JMH) holds no verify_cmp row, so for it the loop body never runs: no manifest, plan or executable check, and `manifest_sha256_<job>` (record.py:238) is read by nothing on that path. manifest_check itself never reads the manifest's `cell_text` entry (run.py:171 writes it; manifest_check compares run_id, plan and the L<n> executables only). `cell_texts` (est.py:769-788) reads cell_text.tsv raw.
- Plant (my copy, draftsets/plants.py P11 in verify/ds): after the synth run, JMB/JMH cell_text.tsv `x86-64-v3` -> `generic`, and each job's manifest.tsv replaced by `run_id selftest / cell_text 000..0` (a pin that matches nothing). Command `SLOT_TREE=<review> python3 -I plants.py verify/ds/runs P11` -> `P11_celltext_edited: WRITTEN`, draft.v6.tsv `rows=88 ... forms=['fn-memchr','mfind-swar','mfind-w16','mfind-w32']` vs control P0 `draft.v6-v3.tsv rows=22 forms=['mfind-w32']`: the 22 mfind-w32 rows moved set silently. SILENT-MOVE (rc 0, sets differ).

## DRAFTSETS-1

**HOLDS** (= contract-4).
- Code quoted, est.py:917-924: `suf, cls = TARGET_SET[tgt_of[r[0]]]` / `if cls.split("/")[0] != TARGET_LEVEL[tgt_of[r[0]]]: raise ... DRAFT-ISA-LEVEL MIXED`; both dicts are literals at est.py:794-796. `cell_texts` (est.py:782-788) keeps `f[6]` (target) and drops column 8 (`target_isa`): nothing in est reads target_isa.
- Plants (verify/ds, `python3 -I plants.py verify/ds/runs P4 P5`): P4 (TARGET_SET["x86-64-v3"]=("","x86_64/zen4") AND TARGET_LEVEL["x86-64-v3"]="x86_64") -> `WRITTEN`, draft.v6.tsv class x86_64/zen4 holds 88 rows incl. mfind-w32, no -v3 set. P5 (mfind-w32 labelled `generic`, target_isa `avx,avx2`) -> `WRITTEN`, same 88-row baseline-class set. Both SILENT-MOVE vs control P0 (66 + 22 split). The guard fires only when the two literals disagree (selftest mf_mixed).

## FIDELITY-3

**HOLDS.**
- Code: est.py:949-951 `in_set(c)`: `return TARGET_SET[tgt_of[a]][1] == cls if a in tgt_of else True` (tgt_of = row keys only, est.py:787); `mine` (est.py:907-911) `return v == "3" or a == "ctl" or any(plan.base_of(r[0]) == a ...)` for non-kit arms. `mine` is unchanged from BASE (base est.py:866-870); `in_set` is new, so the cross-ISA-level half is the subject's, the cross-ver half pre-existing.
- Repro (verify/ds P0 control, cells sections counted by arm): draft.v6.tsv (zen4-grid6, class x86_64/zen4) holds `base.mfind-w32` 7 cells; draft.v6-v3.tsv (class x86_64-v3/zen4) holds `base.mfind-swar`, `base.mfind-w16`, `base.fn-memchr` 7 each; draft.tsv (zen4-grid3, ver 3) holds all four JMH bases (28 cells) plus JMB/JMH ctl (21 each). The real dry run's cell_text (fidelity/rd_ctrl/JMH/cell_text.tsv, read-only) records `base.mfind-w32	x86-64-v3	avx,avx2,bmi,bmi2`, so the baseline-class set carries cells of v3 code. Contradicts main's 2026-11-15 wording "a set never mixes code compiled for different hardware levels" for CELLS (rows are split correctly). Severity: maintenance/design (cells are evidence, no row value read from a foreign base: each row's delta uses its own base wherever filed).

## FIDELITY-5

**HOLDS; pre-existing at BASE** (the reject dim adds same-base key pairs, sharpening it).
- Command (fidelity/probe/dup.py copied to verify/f5, run on my slot copy): `SLOT_TREE=<review> python3 -I dup.py verify/ds/slot verify/f5` ->
  `control (2480315, 2520000)` / `appended 7 duplicate cell lines` / `dup-cell (7981617, 8109320)` (SILENT-MOVE: value x3.2, rc 0) / `swap-keys REFUSED ... names base ['base.mfind-w16'], the family rule's is base.mfind-w32` (LOUD, only via the base suffix) / `swap-reject 2257000 2341000` vs `control-reject 2341000 2257000` (SILENT-MOVE: reject-0 and reject-100 abs swapped, no refusal).
- Code: est.py:611-613 `c[(x["job"], x["arm"], x["length"], x["launch"])] = x` (last line wins, no duplicate check); BASE est.py:604-606 identical. `grep cells record.py` hits only `j1_cells` (record.py:8,189,195): no `cells.<job>.tsv` pin; est reads no `transcript`. Pre-existing.

## EMITTED-3

**HOLDS (as a maintenance/robustness note; no wrong reply today).**
- review tree memfn/src/window.c:2511-2519: `static const uint8_t wf_wsearch[FF_HORS + 1] = { [FF_LIBC] = ..., [FF_HORS] = MF_WSEARCH_HORS, };` and `return (unsigned)f <= FF_HORS ? wf_wsearch[f] : MF_WSEARCH_NONE;`. kit.h:668: `... FF_PAIR, FF_HORS, FF_MFIND } fd_form;` so FF_MFIND = FF_HORS + 1 is answered by the bounds branch.
- `git diff 04fe41c92 1e3d4a17b -- memfn/src/window.c | grep wsearch\|FF_HORS\|FF_MFIND`: the subject widened only the REN_PICK comment and the `_Static_assert(FF_MFIND < 31 ...)` at window.c:1904; finder.c:72 asserts `ff_name` size == FF_MFIND + 1. No static assert ties wf_wsearch's size to the enum.
- Nuance: the in-table forms that render no search (FF_W64, FF_A3, ...) also reply NONE (MF_WSEARCH_NONE = 0, memfn.h:1688, designated-init zero), so "NONE" for a non-search pick is the table's stated intent ("every other pick renders no search, NONE"); the defect is only that FF_MFIND's (and any future form's) NONE comes from the range test rather than a declared entry, and a future real search pick appended after FF_HORS would silently reply NONE. Severity maintenance, effort trivial.

## CHECKS-1

**HOLDS** (re-run independently, 80 sites rather than the critic's 160).
- `gcc -O2 -Wall -Wextra -Werror -I memfn/include -o gen memfn/tests/g2/g2_mfind_gen.c build/libpcrec.a` rc=0; `gen 20261114 80 verify/c1/t x86-64-v3 1` rc=0 (stderr `G2M guarded w16 1238`, `w32 1311`); 75 selectors `return g2m_N__w32(`.
- Plant (verify/c1/p): every selector body `return g2m_N__w32(` -> `return g2m_N__w16(` (regex over the selector function only; 75 rewritten, 0 left). Both built with the runner's flags `gcc -O2 -march=x86-64-v3 -Wall -Wextra -Werror -DG2M_SITES=... g2_mfind_driver.c`: rc=0 both (unused static inline w32 helpers raise no warning).
- `drv-t 4` and `drv-p 4`: both rc=0, `checks 3293080`, `failures 0`; full stdout identical (`diff` of everything but G2M lines -> IDENTICAL; census `hits 1569742 stream1 595682 stream2 125122 trap 821205 late 423696 beyond 937053` in both). `objdump -d | grep -c 'vpcmpeqb.*ymm'`: control 150, plant 0: the w32 form is gone from the binary and the family is green. SAME where a reach check should be red.

## CHECKS-5

**HOLDS** (the two absence claims; the cap-removal stamp arithmetic not re-run).
- `grep -rn 'ofs_fn_fits\|fn_fits\|mfind_applies' tests/ memfn/tests/ (*.py *.sh *.tsv *.c)` -> no hit except the comment at tests/memfn/simd_bounds.tsv:26. `grep -rl -i mfind tests/mech/sabotages/` -> only S3170 (drops the lever flag) and S686 (fn_rows order). No sabotage row anchors `return ofs_fn_fits(x, d);` (memfn/src/vrun.c:683).
- G2 never reaches the cap: my generator run (CHECKS-1, 80 sites, v3) prints `G2M guarded w16 1238`, `G2M guarded w32 1311`, under MFIND_W16_GUARDED_MAX 1400 / MFIND_W32_GUARDED_MAX 1500 (vrun.c:702-703); the critic's 160-site run reports 1289/1355/1375, also under. So no G2 site is declined by the fit test.
- Not verified: that simd_guarded_check would go red on the cap removal (needs a relinked harness + the witness build; the critic's hand-built checks/capoff/ was not re-run).

## CHECKS-3

**HOLDS.**
- Code: tests/memfn/simd_guarded_check.py:344-345 `if lever and not sites: rec['counts'].append('lever-capped')`; floor `'lever-capped': 4` (L165), compared `>=`.
- Run (`build/pcrec-harness [--harness=mfind] --features all -p rx -fmemfn-simd=T -o - --pattern P | grep -o 'RX_MEMFN_FORMS "[^"]*"'`, T in x86-64 / x86-64-v3, P = the three LEVER_NAMED): with the lever: foo.*bar `mfind@w16` / `mfind@w32+w16`, both long witnesses `none` at both targets -> lever-capped = 4 (floor met exactly). Without the lever (S3170's shape): all six `none` -> lever-capped = 6 >= 4: the floor RISES under S3170 (S3170 is still caught by simd-form-lever 0 < 2 and the unread-rows gate, so detection of S3170 is not lost).
- Distinguishing fact the floor ignores: `grep -c 'memcpy(&w, subject'` on the long-tbl witness: lever on 2 (SWAR body, cap declined the helper), lever off 0, at both targets. So 'lever-capped' counts "no SIMD form", not "the fit test declined". Severity maintenance.

## CHECKS-2

**HOLDS (from code; deleted/invented-line plants not run: each needs a full G2 run).**
- memfn/tests/run_g2_mfind.py iterates whatever is declared: `for key, floor in POP_FLOOR.items()` (L416), `builds = BUILDS if x86 ...` + `ex.map(answer, builds)` (L424-442), `for key, fl in DRV_FLOOR_80.items()` (L456), `for sid, pname, expect, edits in PLANTS` (L475, L520); `grep -n 'len(PLANTS)\|len(BUILDS)\|len(POP_FLOOR)\|_PIN'` -> nothing; run_g2.sh:1137 only greps `^(space|build|plants|PLANT|...)` for display. So a deleted row of any of the four lists removes its check with nothing counting it: green. An invented POP/DRV key is red (`pop[key]` 0 / `cnt.get(key, -1)` under its floor), an invented PLANT with a non-applying anchor red: one-sided, as claimed.
- simd_guarded_check.py: LEVER_ARMS/LEVER_NAMED (L129-137) feed `for n, pat in LEVER_NAMED for arm, argv in LEVER_ARMS` (L285); floors `simd-form-lever: 2`, `lever-capped: 4` (L163-165) compared with `>=`: a deleted arm/witness drops a count under a floor (red), an invented well-formed one only raises counts (green). HOLDS as argued.

## CHECKS-7

**HOLDS** (reproduced cheaply without the runner: the population step only).
- Code: run_g2_mfind.py:415-420 `scale = a.sites / 80.0` / `fl = int(floor * min(scale, 1.0))`; the comment (L111-114) says the fixed head is 40 of the sites (g2_mfind_gen.c:233-234 `heads[id / 4]`, 10 heads x 4).
- Repro: generator (verify/c1/gen) run for seed 20261114 at 48 and at 80 sites, 3 targets x lever 1/0 (verify/c7), then `run_g2_mfind.population()` over the six metas and the runner's own floor formula: `48 reds 6 [('multi', 45, 48), ('caseless', 12, 15), ('nterm3', 12, 19), ('nterm4', 3, 11), ('inloop', 3, 7), ('size', 3, 7)]`; `80 reds 0 []`. Same six as the critic's run48.log. Low (only the documented `--sites` knob below 80).

## CHECKS-4

**PARTLY** (the pin holds; it is inherited, not new; the arm64 failure is not run).
- Pin: running run_axes.sh's own `memfn_top_target` (extracted verbatim, `TIMEOUT_BIN=gnutimeout PCREC=build/pcrec`) prints `x86-64-v3`. The target list is static kit text (memfn/src/targets.def:83-95, no host `#if`), so amd64 is the only family with two targets on every host and the arm (run_axes.sh:1813-1827) is `--harness=mfind -fmemfn-simd=x86-64-v3` everywhere. The artifact carries `#if !(defined(__x86_64__) && !defined(__ILP32__))` / `#error "this file was generated for another CPU family..."` (pcrec-harness --harness=mfind -fmemfn-simd=x86-64-v3 'foo.*bar', lines 18-19), so on an arm64 host the compile would fail. `grep -n 'uname\|aarch64\|arm64' run_axes.sh` -> nothing: no skip protocol. `grep 'mfind@\|MEMFN_FORMS' run_axes.sh` -> nothing: no reach count. Those parts HOLD.
- REFUTED part: "the existing -fmemfn-simd axis uses the host family's default target". The pre-existing `--memfn=` SIMD layer (BASE run_axes.sh:1304-1311; subject 1311-1321) uses the SAME top-target rule, deliberately ("family explicit (the pins read the same on every host)", [XARCH-DEV] U3). The new arm reuses that function, so the host-insensitivity is a pre-existing property of test-axes, shared not introduced. Severity low; fix belongs to both arms.
- Shard weight (2 jobs under one AXES word): not verified.

## DRAFTSETS-3

**HOLDS.** `python3 -I plants.py verify/ds/runs P6` (mfind-w32 labelled `x86-64-v4` in cell_text) -> `P6_unknown_target: CRASH(KeyError): 'x86-64-v4'` from `TARGET_SET[tgt_of[r[0]]]` (est.py:919). LOUD but as a traceback, not an InputError naming the unknown target; no file written. Severity low (maintenance).

## DRAFTSETS-4

**HOLDS** (doc + dead selftest conjunct; the "only by construction" part HOLDS by reading).
- span_cards.md (review tree) L790-791 "The card keys carry no target dim, because a set is one target." and L797-798 "Every other target: absent (build), by the one-target rule" stand unamended above the new L803-807 paragraph, under which zen4-grid6@1 holds generic AND x86-64 rows (P0 control: draft.v6.tsv forms mfind-swar/fn-memchr (generic) + mfind-w16 (x86-64)). Contradiction HOLDS.
- est.py:1454 `base_tg = {"generic", "x86-64"}` and L1461 `... and not set(sets["6"]) & set(sets["6v3"]) and base_tg)`: a non-empty literal set, always truthy, read nowhere else (`grep -n base_tg est.py` -> 1454, 1461). Dead conjunct HOLDS.
- "Identical text shares one cell" is enforced by nothing: cell_texts keeps the last line per arm (est.py:787-788), so P8/P9-shaped duplicates collapse whatever their text (consistent with FIDELITY-5 / DRAFTSETS-2; P8/P9 not re-run by me).

## DRAFTSETS-5

**PARTLY** (the stale prose HOLDS; "none cites D197" is moot: D197 is not in the subject tree).
- Quoted at 1e3d4a17b: tests/memfn/rows.tsv:153-155 all three rows `pending-site:span_pick-row-1`; rows.tsv:29-30 defines `pending-site:<trigger>` as "built ahead of the pcrec site that will reach it", while rows.tsv:56 says "a measuring instrument only (F5, Frank ...)": the token contradicts D197 ("never a pick"). memfn/src/kit.h:674-675 "reports MF_WSEARCH_NONE, until a selection table picks the form"; memfn/src/ofsskip.c:467 "a selection that picks the form replaces this predicate"; "picks yet" at memfn/src/compose.c:1474, src/core/internal.h:204, cli/CLAUDE.md:30 item (11). kit-grid.tsv:77 "(SEARCH vs the walk, STREAM RESTART vs MASK, D190) are not built and are owed" vs D197's "a fused WIN triggers building ... under its own owner go" (conditional, not owed). HOLDS as doc/design.
- Moot part: `grep -c D197 docs/dev/decisions.md` in the review tree -> 0; D197 exists only on main at 4ccd97ca7:docs/dev/decisions.md:10219. The subject cannot cite an id it does not hold; its sites cite the same ruling as "F5, Frank 2026-11-15". The landing should add the D197 cite, not a finding against the lane.
- Note: the trigger token `span_pick-row-1` does name the decision D197 says the instrument settles, so it is half-right; the defect is the `pending-site` class, which promises a future reaching site.

## FIDELITY-4

**HOLDS (by absence)**; the libc-ifunc sub-claim not verified.
- `grep -n 'fn-memchr\|memchr\|libc' slot/est.py slot/record.py slot/j1_rule.py`: est hits are the `libc` header fact (est.py:864, 946), a selftest base-swap regex (1181) and the synth record (1418); record.py only the libc/GLIBC_TUNABLES provenance (132-140) and a window comment (42). `grep -n 'FORMS6\|mfind' est.py` (non-comment): every hit is in the selftest (1395-1476). No code compares any mfind-* row with fn-memchr or states which cells/margin decide D197.
- Cross-set by construction: P0 control (verify/ds) files mfind-w32 rows in draft.v6-v3.tsv (zen4-grid6-v3) and fn-memchr rows in draft.v6.tsv (zen4-grid6). HOLDS.
- Context: D197 is on main only (4ccd97ca7), not in the subject tree; a declared decision rule is a reasonable ask before the window, not a defect of the lane's code per se. Severity design.
- Not verified: which glibc memchr variant binds on this box (would need LD_DEBUG/gdb on a launch; out of read-only scope for the time I had).

## EMITTED-1

**HOLDS** (numbers reproduced exactly; whole-object deltas within ~15 B).
- `build/pcrec-harness [--harness=mfind] [-fmemfn-simd=x86-64-v3] --features all -p on -o X.c --pattern '(ABC)'`, `gcc -O2 -fno-inline -c`, `nm -S --size-sort` (verify/e1): off `on_ofsskip__body` 0xa5 = 165 B; lever (SIMD off) `__body` 0x1e4 = 484 B (2.93x); lever at x86-64-v3 `__body` 0x1b4 436 + `__w16` 0x10b 267 + `__w32` 0x129 297 = 1000 B (6.06x); off at x86-64-v3 unchanged 165 B. Inlined `gcc -O2` whole-object .text: off 2968, lever 3176 (+208), lever v3 3672 (+704) (critic: +223 / +695).
- Cause read in the emitted SWAR body (verify/e1/on.c): the verify chain `on_w2(subject + cand) == on_w2("AB") && on_w2(subject + cand + 1) == on_w2("BC")` is written twice (short-span byte loop and the mask stream), and the SWAR mask expression twice (full and final block). HOLDS. Severity size; lever-only text.

## contract-6

**HOLDS (read only), with one refinement each.**
- ofs_fn_fits (memfn/src/ofsskip.c:676-689): renders `fn_head` + `d->render` + `fn_call_line` into a counting sink (`fit_puts/fit_vprintf/fit_cstr/fit_cmt_open`), saves/restores only `art->words`. Mutations reachable through the render: `art->wused |=` (runcmp.c:297, 471), `art->words++` (298, restored), `art->includes |= MF_INC_STRING_H` (371, 382, 426), and `kit_fail(art, ...)` (sticky art->err: e.g. vrun.c mfind_text's `mfind: the scan is not one byte...`, runcmp.c:223/362/415/436). `art->wemitted` (runcmp.c:501) is written only by mf_flush_helpers, reached from run_cmp_prepare, which ofsskip_define calls (ofsskip.c:945) BEFORE ofs_fn_define, so the fit pass finds `need` = 0 and declares nothing into the void. So: wused/includes are OR-idempotent with the real render (prepare already set the widths; the body renders the same chain), words restored; the answer is identical today, as the critic says. The real latent hazards are (1) a kit_fail inside the fit turning a decline into a sticky error, and (2) the fit hands pcrec's hooks `h` (table_params, verify_chain) the counting sink: any pcrec-side hook state is also driven twice (not checked). Also noted: at ofs_fn_serves (ofsskip.c:577) fn_in carries `art = NULL`, so fits returns 0 there (decline) while fn_define (779) passes art: serves and define can disagree about the PREFIX rows (BODY slot only is walked at serves, so no answer effect seen). Severity maintenance.
- slot/gen.c (subject-new branch, absent at BASE): the guard is `if (L > 1 && ... && a->gap < L)` (gen.c:76) and the random-with-run planter (gen.c:97-102) rejection-samples E = len/gap marks with no other mark within L - 1. At gap == L that needs a perfect tiling: never terminates in practice. Refinement: random sequential placement jams near ~75% of the dense packing, so the hang zone is roughly gap < ~1.34 L, not only gap == L. Unreachable today: JMH plans `landing="periodic"` only (plan.py:447-450); ver-3 random arms use GAPS = (256, 1024) (plan.py:141, 345). Not run (read only, as briefed).

## Summary

HOLDS: FIDELITY-1 (finder out of line in `_time` because `_gate` is a second caller; pcrec's rx_search inlines it; +8 instructions per hit incl. call/ret/vzeroupper/re-broadcast; magnitude untimed), contract-2 (CONFIRMED by load: both ver-6 drafts refused `unit_key 'kit.find_byte.walk' names no row`; selftest pins the shape; same header shape at BASE for ver 4), FIDELITY-2, DRAFTSETS-1, FIDELITY-3, FIDELITY-5 (pre-existing), EMITTED-3, CHECKS-1, CHECKS-5, CHECKS-3, CHECKS-2 (code), CHECKS-7, DRAFTSETS-3, DRAFTSETS-4, FIDELITY-4, EMITTED-1, contract-6.
PARTLY: CHECKS-4 (pin and no skip/reach hold; "the existing axis uses the host default" REFUTED: the U3 `--memfn=` layer uses the same top-target rule, pre-existing), DRAFTSETS-5 (stale prose holds; "none cites D197" moot, D197 is not in the subject tree).
REFUTED: none.
No timing run, no make, no box-queue job. All artifacts under verify/.

VERIFY COMPLETE
