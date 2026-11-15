# CHECKS findings

## Findings

### CHECKS-1 CONFIRMED: G2's one-member family counts SUBJECT populations, never which FORM ran; a selector that skips the w32 rung stays fully green
- Severity: maintenance (coverage blind spot; a dropped rung = w32 untested + the instrument measures the wrong form). Effort: small. Blast radius: run_g2_mfind.py / g2_mfind_driver.c only.
- Where: memfn/tests/g2/g2_mfind_driver.c census() (L239-273) and run_g2_mfind.py DRV_FLOOR_80 (L103-110); g2_mfind_gen.c check_site (L371-377: helper NAME present/absent only, "not an exact count").
- The driver's census (hits, stream1/2, trap, late, beyond) is computed from the subject and the reference alone: the counts are IDENTICAL across all 7 builds incl. the lever-0 fn-memchr controls (run48.log: every build `checks 7903392 ... beyond=1547666`). Nothing counts that a w32 block, a w32 final block, a w32 rejected lane etc. ever executed.
- Repro: generated the 160-site x86-64-v3 file (gen 20261114 160 DIR x86-64-v3 1), rewrote each selector `return g2m_N__w32(` -> `return g2m_N__w16(` (145 sites; checks/plant-sel.c), built with the runner's flags `-O2 -march=x86-64-v3 -Wall -Wextra -Werror` (unused static inline w32 helpers: no warning), ran the driver stride 4: `checks 6586160 failures 0`, rc 0. Expected: red (the w32 form no longer reached). Classification: SAME (green) where a reach check should be red. The generator's structural check passes too (the helper's definition and fall-through name keep `__w32(` in the text); MFTRACE REACH counts COMPILE-time row choice, unchanged. Only a text pin (tests/memfn/pins/arms.tsv fixture ofs-mfind-w32) would move, a control that shares the kit as source.
- Reach itself HOLDS today (see PROBED-AND-HELD: per-form path counters). Fix shape: a path census build (counters per helper kind x {entry, block, final, final-mask-cut, handed, rejected}, as checks/bin/instr.py does) with floors per target, or at least a selector-calls-top-rung structural check per target.

### CHECKS-2 CONFIRMED (from code): run_g2_mfind.py's own declared lists carry no identity pin; a DELETED plant, build or population key is green
- Severity: maintenance. Effort: small (a literal id list per list, as run_rows.sh ROW_MAP_PIN does). Blast radius: run_g2_mfind.py.
- Where: run_g2_mfind.py PLANTS (L151-194), BUILDS (L78-90), POP_FLOOR (L115-133), DRV_FLOOR_80 (L103-110); the plant loop (L475-490) and summary (L520-531) iterate whatever is declared; nothing counts plants, plant runs, builds or floor keys against a literal.
- Deleted-line plants (argued from code, the loops are plain iterations): delete the S3173 row -> no `PLANT S3173` line, `plants: N runs` drops by 6, rc 0 (run_g2.sh only greps PLANT lines for display); delete one KIND of a plant (e.g. S3173's 'w32') -> green; delete the 'asan-x86-64-v3' BUILDS row -> green; delete the 'beyond' DRV key (the r2 F10 population) or 'k0' POP key (the only population through which S3152 can fault, see PROBED) -> green.
- Invented-line plants: an invented POP/DRV key is RED (pop/cnt default 0/-1 under the floor); an invented PLANT with an anchor the text lacks is RED (`the edit does not apply`). So the lists are one-sided: invention red, deletion green.
- Same shape in tests/memfn/simd_guarded_check.py LEVER_ARMS / LEVER_NAMED (argued from code, L129-137 + FLOORS `simd-form-lever` 2, `lever-capped` 4, both `>=`): a DELETED arm or witness is red (a floor falls short), an INVENTED one is GREEN (counts only rise). rows.tsv, row_floors.tsv, simd_bounds.tsv and finder_check FORM_IDS are two-sided (see PROBED-AND-HELD).

### CHECKS-3 CONFIRMED: simd_guarded_check's `lever-capped` floor counts "no SIMD form", not "the fit test declined"; S3170's plant RAISES it
- Severity: maintenance (a floor whose name claims a cause it does not observe). Effort: small. Blast radius: tests/memfn/simd_guarded_check.py L344-345, FLOORS['lever-capped'].
- `if lever and not sites: counts lever-capped`: any lever witness whose MEMFN_FORMS is `none` counts, whatever the reason.
- Repro (S3170's shape, the arm without `--harness=mfind`): `build/pcrec-harness --features all -p rx -fmemfn-simd={x86-64,x86-64-v3} -o - --pattern P` for P in foo.*bar and the two long witnesses: all six print `RX_MEMFN_FORMS "none"`, so under S3170 lever-capped = 6 >= floor 4 (green on that floor); S3170 is still DETECTED, but only by the unread-rows gate and simd-form-lever. Equally, a change that stops the lever reaching the long witnesses at all (fn-mfind not taken) keeps lever-capped green.
- What holds today: with the lever the long witnesses DO reach the body (`memcpy(&w, subject` x2 in the SWAR body at both targets) and the w16/w32 helpers are absent, i.e. the cap really declines them (PROBED). Fix shape: count lever-capped only where the body row is fn-mfind (its `memcpy(&w` text or the trace's chosen row) and the level helpers are absent.

### CHECKS-4 SUSPECTED (argued from code + target listing): the axes `--harness=mfind` x SIMD arm pins x86-64-v3 whatever the host, has no skip protocol, and counts no reach
- Severity: maintenance (an arm64 or non-AVX2 host's test-axes goes red for a reason that is not an answer; and a green arm proves nothing if no corpus artifact took mfind-w*). Effort: small. Blast radius: tests/axes/run_axes.sh L1813-1827 (+ memfn_top_target L1293-1298).
- memfn_top_target picks "the family with more than one target" from `--list-cpu-targets`; on this build that is amd64 on EVERY host (armv8-a is alone in arm64), so on the Mac (arm64) the arm compiles artifacts carrying the amd64 family guard `#error "this file was generated for another CPU family"` -> every job compile fails (red); on an x86 host without AVX2 the v3 region code can SIGILL. The existing `-fmemfn-simd` axis uses the host family's default target, and G2's family has `SKIPPED ARM <level>` for exactly this; this arm has neither.
- Reach: the arm is answer identity vs the default (the r2 F12 fix says it is the rows' only answer check on pcrec's own sites) but nothing counts how many corpus artifacts carry `MEMFN_FORMS "mfind@w32+w16"` / `mfind@w16`; if the lever stopped reaching the SIMD rows the arm stays green (MECH-REACH). Confirm: run the arm on an arm64 host, or count `mfind@` tokens over its artifacts.
- Shard table (tests/ci/cloud_axes_shards.tsv): one unit `--harness=mfind` at the 387 s median ESTIMATE, but the AXES word selects TWO jobs (the INTERNAL_ARMS one and the SIMD one, both matched by `*" --harness=mfind "*`), so its weight is under-stated ~2x (ESTIMATE either way; low).

### CHECKS-5 CONFIRMED: the r2 F1 cap (ofs_fn_fits via mfind_applies) has no sabotage row, and G2's one-member space never reaches it
- Severity: maintenance. Effort: small (one mech row). Blast radius: memfn/src/vrun.c mfind_applies L681-684; tests/mech/sabotages.
- G2's space renders at most 1,375 guarded bytes per site (gen 160 sites: w16 1289/1355, w32 1375), under the 1,400/1,500 caps, so no G2 site is declined and the G2 bound comparison (`mx <= bd`) cannot go red by construction (the bound IS the kit's cap, pinned equal by simd_guarded_check's declaration pin: a control sharing its source, by design).
- Plant (built by hand, read-only on the tree): copy of vrun.c with `return ofs_fn_fits(x, d);` -> `return 1;`, one object, relinked pcrec-harness (checks/capoff/). Stamps under `--harness=mfind`: x86-64 long-tbl 0xff9 = 4089 and long-run 0x91f = 2335 > mfind-w16 1400 + target-text 700; x86-64-v3 7831 / 4323 > 1400+1500+700. So simd_guarded_check's `plain stamp exceeds the sum of its rows' bounds` and the lever-capped floor (0 < 4) WOULD fire (argued: its witness build needs make). The detector exists; no mech row (only S3170, which drops the lever) registers it. Add the row: SAB_BEFORE `    return ofs_fn_fits(x, d);` in memfn/src/vrun.c, suite simdguarded.

### CHECKS-6 (design, informational): the fields G2's one-member generator holds constant, and the kit branches that hides
- Severity: design/maintenance. Effort: medium if wanted. Blast radius: memfn/tests/g2/g2_mfind_gen.c draw()/main() L430-500.
- HELD CONSTANT on every site: `span_hi` MF_SPAN_UNBOUNDED; `cand_ppm_hi` and every term's `ppm_hi` MF_PPM_FULL; every term `need` REQUIRED; `body` ONESHOT; `empty` MISS; `use` POSITION (DISCARD on pre); op FIND / form FUNC / handoff RETURN (ALL_PRESENT/STMT/ON_MISS only on the `pre` shape); `plan_hint`/`plan_pos` always stated; hooks `subject`/`n`/`pos`, `hk.miss` MF_MISS_N; no rank facts, no window facts, no `denies`, no `opts` (no `--memfn=` deny), reverse/end_back unset; offsets 0..16 (never negative), <= 4 terms, RUN <= 12 bytes; the scanned position always ONE exact byte (never caseless, never a two-member cube); the lever set {mfind} only; three targets. The call text is rendered into a null sink and never compiled (the generator writes its own wrappers).
- HIDDEN kit branches: (a) prefix_holds' REACH decline (`span_hi < 16/32 + vrun_t(p)`, ofsskip.c L486-487): never taken in G2 (span unbounded); (b) the cap decline (ofs_fn_fits): never taken (CHECKS-5), so G2 never answer-checks a SIMD-target site whose selector calls `__body` directly under the lever; (c) first-match precedence fn-every-pos / fn-pair over fn-mfind: no generated site is a cube or scan-less, so G2 never shows the lever leaves fn-pair's sites alone (S686 and the arm pins hold the order instead); (d) mfind_text's refusal `mfind: the scan is not one byte at an offset the guard covers` (k < 0 or D < 0): unreachable from the space (offsets >= 0); (e) `denies` RUN_OVERLAP, served by mfind's contract (VRUN_SERVES), never stated; (f) the mf_use/call side under the lever (the generator discards it). (a), (b), (f) are where a regression could land unseen by THIS family; none is an answer risk today (reads stay inside [pos, n) by the body's own bound).

### CHECKS-7 CONFIRMED (low): POP_FLOOR scales linearly below 80 sites although the fixed head is 40 of them; `--sites 48` gives 6 false reds
- Severity: maintenance (only the documented `--sites` knob; the tier runs 80/160). Effort: trivial. Where: run_g2_mfind.py L415-420 (`int(floor * min(scale, 1.0))`; the comment at L111-114 says they do not scale UP, true, but scaling DOWN linearly is wrong when 40 sites are a fixed head).
- Repro: `python3 -I memfn/tests/run_g2_mfind.py --root REVIEWTREE --sites 48 --quick --keep` (checks/run48.log): every answer and plant green, then `FAIL: population multi 45 < floor 48`, caseless 12<15, nterm3 12<19, nterm4 3<11, inloop 3<7, size 3<7; `checks failed: 6`. Either refuse `--sites` < 80 or scale on (sites - 40).

## PROBED-AND-HELD

### Per-sabotage rows (one per plant: reaches its site? caught by the check that should?)
Observed: `run_g2_mfind.py --sites 48 --quick` on the review tree (checks/run48.log), 57 plant runs, every PLANT in its expected class.
| plant | reaches | caught by the right check | note |
|---|---|---|---|
| S3150 final-late | yes, w16/w32/body | FAULT (runner's signal class) | a RUNAWAY witness as its comment says: `i += VW` past e wraps; proves the exit test, not a 1-byte bound |
| S3151 loop-past | yes | FAULT | runaway, same |
| S3152 entry-short | yes, w16/w32 | FAULT | faults ONLY through k == 0 sites in layout L (f = pos - 1); at k > 0 f >= pos is a legal read and the mask hides the lane; held by the `k0` floor (36), which CHECKS-2 shows is unpinned |
| S3153 no-final-mask | yes | SAME (expected) | a text pin / specificity control, rightly SAME: lanes in [f, i) were all rejected already and the check is pure |
| S3154 swar-classic | yes, body at all 3 files | LOUD | needs the trap subjects (trap population floored) |
| S3155 high-lane | yes | LOUD | |
| S3156 stream-drop | yes | LOUD | needs stream1 (floored) |
| S3157 body-short | yes | FAULT | k == 0 / layout L, as S3152 |
| S3158 lane-shift | yes | LOUD (may FAULT, accepted) | |
| S3159 endian | yes, 2 sites per body | LOUD | |
| S3173 top-one-byte | yes | FAULT | D == 0 sites read s[n] (layout U); D > 0 through the verify chain |
| S3174 top-one-byte-dpos | yes (per = -1: D > 0 helpers only) | FAULT | through the driver's `beyond` subjects (floored) |
| S3170 (mech) lever arm drops lever | yes (anchor resolves: m6read_check_sab_anchors.py, 1300 rows, all resolve) | DETECTED by simd_guarded's unread-rows gate and simd-form-lever (0 < 2); NOT by lever-capped, which rises to 6 (CHECKS-3) |
| S2930 (mech, re-aimed) | yes: only the new 15th `lever` column (NULL) appended; plant unchanged | finder_check check B, as before | |
| S686 (mech, re-aimed) | yes: hand-built planted ofsskip.o + pcrec (checks/s686/): `(?i)select --memfn=no-window-search` on "select" -> `nomatch` (base: match 0 6); default artifact moves silently (answers same) | the answers (reqcube.rxt) as designed | the plant now DUPLICATES the fn-memchr row (ahead of pair, and its own later row); the kit accepts a duplicate row name (no refusal), so detection is by answers, the intended detector |

### Declared lists, DELETED and INVENTED line
| list | deleted | invented | how known |
|---|---|---|---|
| tests/memfn/rows.tsv | RED: `the kit has row fn/mfind-w32 and rows.tsv does not` | RED: `rows.tsv names ... the kit has no such row` | code, rows_check.py L725-737 (not run: builds the traced pcrec + plants) |
| tests/memfn/row_floors.tsv | RED: `rows.tsv names X and row_floors.tsv has no line` | RED: `row_floors.tsv names X and rows.tsv does not` | code, rows_check.py check D |
| tests/memfn/simd_bounds.tsv | RED: declaration pin `guarded_max 1500 != simd_bounds.tsv None` + UNDECLARED on the v3 lever artifacts | RED: `rows no artifact read`; `names no vrun.c declaration` if mfind-/vrun- prefixed | code, simd_guarded_check.py L251-269, L426-429 (needs the witness build: not run) |
| LEVER_ARMS / LEVER_NAMED | RED (simd-form-lever or lever-capped short) | GREEN (floors are >=) | code: CHECKS-2 |
| finder_check FORM_IDS | RED: `the entry table holds mfind-w32 -, which the design does not name` | RED: `mf_form_hash(X) does not resolve` | code, finder_check.py L328-364 |
| tests/memfn/pins/arms.tsv | RED: `rendered with no pin` | RED: fixture `renders through 'nothing'` | code, run_arm_pins.sh L36-56 |
| run_g2_mfind PLANTS/BUILDS/POP/DRV | GREEN | RED (POP/DRV), RED (unapplicable plant) | code: CHECKS-2 |

### Held (probed)
- REACH at every form (CHECKS-1's census, run by hand, NOT by the check): instrumented the 160-site files (checks/bin/instr.py; counters per helper kind) and ran the driver per target. x86-64-v3: w32 entries 7.94M, full blocks 8.05M, final blocks 3.96M, final-mask cuts 1.95M, lanes handed 13.9M / rejected 9.1M (2.75M handed in the final block); w16 (fall-through) entries 5.71M, rejected 5.99M; body 6.66M entries, byte loop 2.36M. x86-64: w16 13.6M entries, rejected 15.1M, w32 0. generic: body 20.3M entries, 48.3M blocks, rejected 19.3M. 26,344,640 checks per file, 0 failures. Verify chain both accepting and rejecting at every form: yes. Thin spot: a second full w32 block only ~117k times (n <= 73 with maxk up to 28).
- Unplanted mutants all killed (driver stride 4, v3 file, all kinds): drop `i = f;` (SEGV), drop the helper entry's `pos + maxk >= n ||` (SEGV), drop the body's `pos + maxk >= n` return (SEGV), verify chain always true (FAIL got 0 want 2), drop `if (i == e) return n;` (10 s alarm), wrong SWAR XOR byte (FAIL got 9 want 7). 6 of 6.
- Oracle independence: the driver's ref_find reads the predicate as drawn, never kit output; the lever-0 builds (fn-memchr, the shipped row) agree with it over the identical space (7,903,392 checks each at 48 sites), so the reference models the shipped contract; the scan choice only steers the planter. Shared source is limited to the generator's struct, which both the mf_term translation and the table come from (a translation bug shows as a red, not a hide).
- Guard layouts U (s + n), L (below s + pos), A (alignments 0..31), every n 0..73, both lever states and all 7 builds: rc 0, populations printed per build.
- The long lever witnesses reach fn-mfind (SWAR body present) and the cap declines their helpers at both targets; foo.*bar renders mfind@w16 (1502 B) / mfind@w32+w16 (2657 B).
- Cap removal plant: stamps 4089/2335 (x86-64), 7831/4323 (v3) exceed bounds: simd_guarded's arithmetic would fire (CHECKS-5).
- run_lever_fence ALLOW adds tests/mech/sabotages/S3170_ and simd_guarded_check.py: both exist (the brief's "tests/compound/sabotages" path is the diffstat's abbreviation; the files live in tests/mech/sabotages/).
- rows: run_g2.sh FLOOR_ROWS 36 with check (b) n >= 1 per row: under --rows the three mfind rows must be chosen at least once (compile-time reach, the runner's --reach-err joins it); row_floors' g2 cells stay PLACEHOLDER (printed UNREACHED), by policy.

### Sibling of a family
run_g2_mfind.py is the third author-written kernel family beside run_g2_simd.py (vrun rows) and run_g2_any.py (find-any kernel): the same gen + driver + runner, per-target files, build list, SKIPPED ARM protocol, plant list with FAULT/LOUD/SAME classes, literal floors. The siblings share CHECKS-1 and CHECKS-2's shapes as far as I read run_g2_any (driver-side subject populations, plant lists iterated without a pin); not verified here beyond the CLAUDE.md descriptions.

### General form + unlocks (with triggers)
- General form: ONE declared table per kernel family (targets x builds x plants{id, kind, edit, class} x populations), a shared plant/build runner, and a PATH CENSUS compiled in by a single `-DG2_PATH` hook in the rendered text (per helper kind: entry, block, final, final-mask cut, handed, rejected) floored per target; each list pinned by a literal id string (ROW_MAP_PIN's pattern) so a deleted line is red. Unlocks: CHECKS-1 and CHECKS-2 closed for all three families at once; the census doubles as the slot harness's `reject` dim witness (counts rejected lanes per block, the stream the fused row is measured on). Trigger: the next kernel family (D197's ruled split shape: the T-FIND row's search renderer + S-mask stream row, built only on a fused WIN) or the next change to any of the three runners, whichever comes first.
- Lever x SIMD axes arm generalized: every test-only lever whose rows have SIMD levels gets its SIMD-layer arm from one table (lever, target rule = the HOST family's top target, skip if the host cannot run it, a reach count of the lever's MEMFN_FORMS tokens). Trigger: a second test-only lever with SIMD rows, or the first non-amd64 test-axes run.
