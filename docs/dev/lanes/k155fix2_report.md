# k155fix2 report: review r96's FIX-NOW items on lane/k155fix

Lane k155fix2 (opus), 2026-11-24. Worktree worktrees/k155fix, branch lane/k155fix, from d26893e40. Brief: apply the manager's rulings on code review r96 (`docs/dev/reviews/2026-11-24-r96-k155code.md`, its RULED section, copied verbatim). R-1..R-3 of k155fix_rulings.md still bind: no Job-owned buffer, no new mechanism, the three whole-artifact rewrites stay [ARENA-SCOPES] clients.

## Summary

- COST-1 is fixed. Each `${...}` expansion's intern key is now rendered ONCE and kept beside it (`Ctx.var_exp_keys`). The intern loop compares against the stored keys, and the two emitter sites that re-rendered an expansion read the stored key too. On the r96 witness, peak RSS is now BELOW BASE at every size (x0.23 at n=3200, where the pre-fix subject was x13.6), because BASE's own quadratic render is gone as well. Emitted bytes are identical to BASE at every n.
- The class survey of all 23 scratch-builder sites found no other site whose retention grows faster than the text it produces. One more linear-per-reference site (the VM's caller-variable label, a render per reference) was moved onto the stored key. No site needs a scoped arena. The table is under "Retention census".
- GENFORM-1/CHECK-5: alloc_check has a W6 compound witness. Its by-design fallback absorptions are pinned exactly (982 single-shot, 0 sustained). A pinned count now prints a NOTE; before, it printed a FAIL. New row S3580 drops `pcrec_arena_own`, and only W6 sees that (verified locally).
- GENFORM-2: the measures FILE reader allocates its buffer from a stat() size BEFORE it opens the file, so no FILE is live across an arena allocation. No new mechanism was needed.
- CHECK-1: the scanner now classifies EVERY declarator. It has three new fixtures, and S3584 is the tree plant.
- CHECK-4: the stale-row rule, the three floors and a new layer census each have their own control plant, which runs before the scan. S3581-S3583 plant the script itself. I ran 9 mutants and all were caught.
- CHECK-6: the injected free and realloc lower the live balance only for a block the injector counted.
- GENFORM-3: the minimize.c allowlist row cites [ARENA-SCOPES].
- GENFORM-4: the caller-owns rule is written in src/core/CLAUDE.md and coding.md 1.6. The scanner header sentence about src/dump is corrected.
- The PLAN item (GENFORM-5/8/9, COST-2 into [ARENA-SCOPES]'s refs) is NOT applied on this branch. That plan row was filed on main after the branch point, so lane/k155fix has no such row to append to. It is owed at merge; the text is in STATE AT HANDOFF.

## Fixes

| item | where | what |
|---|---|---|
| COST-1 | src/core/internal.h (`Ctx.var_exp_keys`), src/parse/mod_vars.c `vars_intern_exp` | the key is rendered once per expansion and stored beside `var_exps[i]` (same doubling growth); the lookup compares stored keys |
| COST-1 class | src/gen/emit_vm.c (resolver comment loop; `vm_var` label) | both read `var_exp_keys[...]` instead of re-rendering (the label site was one render per REFERENCE) |
| GENFORM-1/CHECK-5 | tests/core/alloc_check.c | W6 `^abc\|x+$` row: floor 504, absorbed 982/0 with its reason; `report()` treats an absorption count EQUAL to a stated pin as a NOTE (any other count still FAILs either way); header lists W6 |
| sabotage | tests/mech/sabotages/S3580_compound_part_text_not_owned.sh | resource arm; local check: W6's profiling pass FAILs ("left heap live"), W1-W5 unaffected |
| GENFORM-2 | src/core/ks_measures.c `pcrec_ks_meas_read_file` | stat, then allocate, then fopen/read/close. Only a regular file is read. A length change since the stat reads as "cannot read". A DIRECTORY passed as `--measures=DIR` used to report a bogus "out of memory" (ftell's size went to the arena, stranding the FILE); it now reports "cannot read". Diagnostic wording tier only (D26; the spec pins no text). A real FILE emits identical bytes to BASE |
| CHECK-1 | tests/core/scratch_builder_check.py `strbuf_declarators` | splits each declaration at depth-0 commas up to its `;`; a parameter list yields its first declarator only; an initializer still open at the line's end is taken as written (this also catches CHECK-2's `StrBuf b = {` + newline shape). Fixtures: `u = {0}, all = {0}` now needs `all`, `nb = {..}, leak = {..}` needs `leak`, `a = scratch, b = {0}` needs `b` |
| CHECK-1 plant | S3584_scratch_builder_second_declarator.sh | `StrBuf nb = {..}, leak = {..};` in target_headers_render (core arm). The critics' v4/v5 bypass trees now FAIL (v2/v3 too) |
| CHECK-4 | scratch_builder_check.py `self_test_controls`, `layer_census`, `stale_rows`, `floor_failures`, `EXCLUDED` | a sentinel row that must come back stale; an empty population that must trip all three floors; a census listing with a new and a missing layer; the real tree's src/ subdirectories must each be a LAYER or EXCLUDED with a reason (dump, findings) |
| CHECK-4 plants | S3581 (stale rule deleted), S3582 (file floor deleted), S3583 (facts dropped from LAYERS) | all core arm. Mutants run locally against the tree, all rc != 0: stale rule, each of the 3 floors, LAYERS minus facts / minus enc, census new / missing, second-declarator. 9 of 9 caught |
| CHECK-6 | alloc_check.c `live_tracked` | free subtracts, and realloc subtracts and re-notes, only for a block the injector counted |
| CHECK-2/3, CHECK-5 doc | scanner header "WHAT IT DOES NOT SEE" | names the single-line limits, headers, the unlisted heap spellings, non-memory resources, a StrBuf inside a local struct type, and the two SINGLE-CONTROL rows (S3570 round, S3572 lines) that no dynamic witness reaches |
| GENFORM-3 | scratch_builder_check.py minimize.c row | cites [ARENA-SCOPES]. The other two mentions of the dangling slug are history (the k155fix report, the r96 review) |
| GENFORM-4 | src/core/CLAUDE.md, docs/dev/guide/coding.md 1.6, scanner header | the caller-owns rule; coding.md also gains review r96 lesson 1 (state a looped scratch builder's call count) |
| docs | docs/testing.md (K155 passage), tests/core/CLAUDE.md row, the review's RULED section | |

S-ids used: S3580-S3584 from the brief's S3580-S3586 (S3585, S3586 unused).

## Retention census

The shape to look for: a scratch builder grown or re-created per item of a population whose size the user controls, so that its abandoned blocks (at least 256 B per call: sb_grow's first cap) pile up in the job arena. "Bound" is calls per compile attempt.

| site | in a loop / called per item? | calls per attempt | retention | action |
|---|---|---|---|---|
| core/varexp.c:312 render | per call site: intern (1 per new expansion), resolver comment, VM ref label | was E(E+1)/2 + E + R; now E | was QUADRATIC (COST-1) | FIXED: rendered once per expansion; resolver and label read the stored key |
| gen/emit_vm.c:12751 lit | per expansion with an operator word | <= E | linear, ~ the word | none (linear, bounded by the emitted word text) |
| gen/emit_dfa.c:5376 scan_set_text | per DFA state with a scan edge (2 listing + 2 comment callers) | <= 2 per scan state | linear in S; text <= ~5*ncls B | none (same order as the emitted text it feeds; measured at noise) |
| gen/emit_dfa.c:13248 scan_test | per scan edge (`emit_scan_edge` loop) | one per scan edge | linear | none (measured at noise) |
| gen/emit_dfa.c:1168 round | per req-byte handoff site (3 callers, once per emitter) | constant | constant | none |
| gen/emit_dfa.c:8059 round | per landmark move (form handoff + VM reentry) | constant | constant | none |
| gen/emit_dfa.c:3675 loop | in a loop over the ENCODING's entry table | <= entries of one encoding (fixed) | constant | none |
| gen/memfn_sites.c:1026 fb | per residual site (from 3675) | constant | constant | none |
| gen/memfn_stamps.c:313 line | in a loop over `ks_marks[]` (fixed table) | constant | constant | none |
| gen/memfn_stamps.c:343 lines, :406 lines | once per attempt | 1 | small | none |
| gen/part_layout.c:547 stamp_value, :679 rows | once per attempt / per listing | 1 | small | none |
| gen/known.c:723 cover cells | once per listing | 1 | small | none |
| facts/facts.c:740 pf_hex | per stamp / listing row | constant (<= 3) | <= PCREC_MAX_REQ_RUN_SCAN items | none |
| facts/facts.c:791..912 (6 renders) | per fact row in the facts listing / a stamp | constant (fact table) | <= ~1.3 KB each | none |
| core/sb.c:692 stampv v | per stamp under a compound shell | stamps (fixed set per artifact) | linear in stamps | none |
| parse/mod_callouts.c:67 co_echo | refusal path only | 1 | small | none |

Growth-in-loop sites with SUPER-LINEAR retention: 1 (COST-1, fixed). Linear-per-item sites: 4 (5376, 13248, 12751, and the label site, which is now fixed). No site needs a scoped arena. The STOP rule (more than ~6) did not fire.

THE MEASURED GUARD. Peak RSS (KB, /usr/bin/time %M) of the one-pattern compile. BASE = 01171dfee's build (the critics' copy); FIXED = this branch; `--max-emit-code-bytes`/`--max-emit-bytes` raised to 1e9 so every size runs to completion. Emitted rx.c is byte-identical BASE vs FIXED in every row (sha column in `$PCREC_TMPDIR/scratch/k155fix2/rss_table.tsv`).

| family | n | BASE | FIXED | FIXED/BASE |
|---|---|---|---|---|
| r96 witness `${v0}..${vN-1}` | 400 | 7,504 | 6,776 | 0.90 |
| | 800 | 13,628 | 9,040 | 0.66 |
| | 1600 | 33,240 | 13,448 | 0.40 |
| | 3200 | 102,008 | 23,036 | 0.23 |
| many references, 10 expansions `${v(i%10)}` | 400 | 6,212 | 6,388 | 1.03 |
| | 800 | 8,212 | 8,496 | 1.03 |
| | 1600 | 12,448..12,492 | 12,644..12,904 | 1.01-1.04 |
| DFA scan `a[^a]*b[^b]*..` (critic COST's) | 100 | 14,500..14,864 | 14,304..15,004 | 0.99-1.01 |
| compound-admitted (cs) | 200 | 7,648 | 7,568 | 0.99 |
| non-compound alternation (cmp) | 400 | 13,840..13,912 | 13,712..13,904 | 0.99-1.00 |

Pre-fix subject for comparison (r96's own numbers): x3.4 (400), x7.0 (800), x10.8 (1600), x13.6 (3200). Noise, from repeated runs of the same binary: about +-2.5% (BASE scan100 ranged 14,500-14,864). Before the label fix, the references family read 1.04/1.06/1.07 and was rising with n; after it, 1.03 flat. Every family is within x1.0-x1.1. No cheap TEST guard was added: an RSS ratio needs a BASE binary, and an absolute RSS bound would be an unmeasured tuning constant. The fix also takes the quadratic render COUNT out of the code, so a regression has to re-add a render inside a loop, which a reviewer can see.

## Validation

- `make -s strict`: rc 0 ("whole tree compiles clean with -Werror -Wshadow").
- `python3 scripts/m6read_check_sab_anchors.py`: 1412 sabotages, 1471 anchor sites, all resolve.
- `bash tests/core/run_core_tests.sh` (the file test-core runs): 9 passed, 0 failed. The scanner prints PASS (91 files, 23 scratch, 24 allowlisted, 6 Job buffers).
- alloc_check `--both`, against an injected build of this tree (build-alloc/, `$PCREC_TMPDIR/scratch/k155fix2/ac_both.out`): rc 0, 13 passed, 0 failed. W6 shows NOTE 982/1008 pinned fallback, sustained clean, and 1 filed stranding (target_headers_render) in each mode. Both known_stranded rows are reached.
- S3580 checked locally (planted compound.o in a copy of the injected lib): W6 "profiling pass did not succeed cleanly", rc 1. Nothing else fails.
- S3581-S3584 are covered by the matching local mutants (CHECK-4 row above). The critics' bypass trees v4/v5 now fail the scan.
- COST-1 peak-RSS guard: the table above.
- Measures FILE: identical rx.c/rx.h BASE vs FIXED with `--measures=measure_store/zen4-grid1/1/set.tsv`. A missing file still says "cannot open".
- OWED (queued as the last act, refuse-after 19:30): `k155fix2-sweep` (emit_sweep.py --ref 01171dfee, 0 movers expected), `k155fix2-test` (make test via perfrun; log `$PCREC_TMPDIR/scratch/k155fix2/maketest.log`, verdict = make's `*** [...test-X] Error` lines), `k155fix2-mech` (S3580-S3584; `== mech run COMPLETE: 5 rows (... undetected: 0 ...)`), `k155fix2-asan` (make asan, rc).

## STATE AT HANDOFF

- STATE: delivered, validation OWED (four queue jobs above). Last ruling applied: none in k155fix2_rulings.md (empty at every re-read); the brief's RULED list in full, except the PLAN item below.
- OWED AT MERGE (the manager or the landing lane): [ARENA-SCOPES] is on main and not on this branch. Append to its `refs:` line: `review r96 GENFORM-5/8/9, COST-2 (design inputs: one sb.c storage-transplant primitive by .ar for the memfn_stamps/part_layout swaps; adoption into a Job buffer is a copy or a registry hand-off; one Ctx registry with scope marks and a RELEASE operation)`.
- The W6 absorption pin (982) is exact, as D110 requires, so an allocation-shape change on the compound path re-pins it.
- K155 stays OPEN (R-3); nothing here touches the three whole-artifact rewrites.
- Commits fd5e5ed94..HEAD on lane/k155fix; job scripts in `$PCREC_TMPDIR/scratch/k155fix2/jobs/`.
