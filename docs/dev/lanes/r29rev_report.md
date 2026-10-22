# r29rev — pre-merge review of the kit's R-29 delivery (D172 S2)

Lane r29rev (opus), 2026-10-22, read-only review. Input: `lane/memfn-ws` @ 25ec6f665
(validated code tip a2d4d9738 plus one `[responses]` commit). Main: bf33d2dab.
No `make`, no box job. Every claim below was checked against an artifact, not the kit's words.

**OVERALL VERDICT: MERGE.** No point is FIX-FIRST or BLOCK. There are four follow-up nits (§9), none of them a
merge condition.

| # | point | verdict |
|---|---|---|
| 1 | job 586 ran at a2d4d9738 vs bf33d2dab, green | MERGE |
| 2 | compose.c merge resolution keeps R-28's fixes | MERGE |
| 3 | wsframe aba15302e (4 KB frame bar) | MERGE (nit N1) |
| 4 | wsc8 masked-note fix 5fed19321 | MERGE |
| 5 | no pcrec abi event; MF_SITE_ABI readers | MERGE |
| 6 | D80 spec hunks | MERGE |
| 7 | files outside memfn/, src/ for main's eye | MERGE (nits N2, N3) |
| 8 | facts DECLARED MOVES 3451 | MERGE |
| 9 | trial merge | MERGE (clean, tree equals the branch's) |

## 1. Job 586 — MERGE

- Log: `worktrees/.boxqueue/done/20261022T171338.062136463-586-kit-wsmain-heavy/job.log`.
- `scripts/verdict` on it: `VERDICT GREEN: 16 completion signal(s), no red line`. `result`: `outcome=green rc=0 wall=2089s
  verdict=GREEN`, `population: sweeps ran=5 declared=5 OK`.
- The tip and base, job.log line 1: `== wsmain heavy tip a2d4d9738f79a5a509de38ab9f74b668af883d0c vs bf33d2dab`. The make-test
  log's own stamp (`worktrees/wsmain/build/wsmain/heavy/test.make.log`) says
  `RUN-STAMP: tree=a2d4d9738f79... (clean) sections=76/76 duration=1298s`.
- `grep -cE '\*\*\* \[(Makefile:[0-9]+: )?test-'` gives 0 on test.make.log. job.log prints no `test-red:` line. perfrun says
  `DONE rc=0 ... section-errors=0 class=green contaminated=no`.
- Steps: build rc=0, strict rc=0 (`whole tree compiles clean`), the five sweeps rc=0 with every stream at `movers=0 asymmetric=0`,
  codegen at 0 failed in every block, and memfn_link at 11/0 with `largest frame: 3600 pcrec_mf_form_hash`.
- 25ec6f665's parent is a2d4d9738. `git diff a2d4d9738 25ec6f665` touches only `memfn/docs/responses.md` (+32). The job therefore
  validates the code being merged.
- Note: `lane/memfn-ws` now points at 7dba9e28e. That is one more commit after 25ec6f665, `memfn journal: R-29 delivered (586
  green)`. It is a journal change only. Merging the branch name instead of the sha brings it in too. That is harmless, but main
  should know it.

## 2. compose.c merge resolution (1d83e8430) — MERGE

- `git diff 573207f76 1d83e8430 -- memfn/src/compose.c` (the kit side vs the merge) contains EXACTLY R-28 600feffc4's compose.c
  hunks, and nothing else:
  - `term_prove` gains `long base` and writes `pv[d - base]` (compose.c:338, :354).
  - `kit_class` passes `MF_PROOF_LO` (:376).
  - `kit_report_exact` holds one offset's row, `uint8_t req[1][32]`, compares per offset and returns early (:396-406). This replaces
    the 41-row table.
- D172's side of the same functions is kept: the `ctx`/`nctx` loops and `pred_proves` clipping are gone. That is the R1 retirement
  (wsc6 6-k5; memfn.h:168 records `ctx/nctx ... DELETED`). R-28's `report_exact` change was therefore applied to the D172 shape,
  which has span-0 terms only. It is correct, since `term_prove(.., d, d, req, d)` writes row 0.
- R-28's other sites survive at the tip:
  - `terms.c` is byte-identical to 600feffc4.
  - kit.h:497 (`-1 (the scratch allocation was refused`) is there.
  - memfn/src/CLAUDE.md:19 (the STACK rule) is there.
  - `run_link_checks.sh` has 8 R-28 mentions.
  - The only formhash.c delta vs main is the 3 retired-field assignments; the arena is untouched.

## 3. wsframe aba15302e — MERGE (nit N1)

- `mf_wdecide` (window.c:1050-1054): `wf_dec *d = calloc(1, sizeof *d); if (!d) return -1; decide; reply_of; free(d)`.
  - `decide` and `reply_of` are void, so there is no early return between the calloc and the free, and no leak.
  - The heap is right here: the ask is documented PURE, so the art's arena would be wrong.
- `wf_legacy`: `e_legacy_holds` no longer has a 5 KB local. `wf_prepare` allocates `L` from the art's arena beside d/w/pid
  (window.c:1393), under the existing refusal `if (!d || !w || !pid || !L) { *why = "out of memory"; return -1; }` (:1394).
  - It reaches the predicate through `wf_ex.L`.
  - `wf_ex` is built at one site only (:1403), so no initializer lacks `L`.
  - `translate` begins with `memset(L, 0, sizeof *L)` (:1218), so reusing the buffer from the E-walk for the final translation
    cannot leak state.
  - Before the change, `kit_legacy_serves` saw a stack local that died on return. It therefore cannot have relied on `L` outliving
    the call, and the reuse is safe.
  - Cost: `L` is now allocated even on the paths that never translate, about 5 KB of arena per window site per art. This is
    acceptable.
- Evidence: memfn_link in job 586 reports `PASS: [R-28] no kit function has a stack frame over 4096 B`, with the largest frame
  3600 B (`pcrec_mf_form_hash`, which is R-28's own). The wsframe report says 76/76 compiles are byte-identical. The five sweeps at
  0 movers cover that at corpus scale.
- **N1 (doc):** memfn.h:1455-1457 still says `mf_wdecide` "Returns 0, or -1 where the site is not one the family describes". -1
  now also means a refused allocation. pcrec's two callers, emit_dfa.c:1143 and :7411, would then print "internal error: the memfn
  kit refused / names no member". That is a misleading wording on OOM only; it is not a miscompile.

## 4. wsc8 5fed19321 — MERGE

- `req_note_run` (emit_dfa.c:1289) now derives `masked` from the fact (:1293). It uses `run_mask_or_null(r->mask, r->len)` for
  test 0 (the window) and `run_mask_or_null(r->whole_mask, r->whole_len)` for test 1 ([K66] whole run).
  - The old derivation read `p->term[0].mask`, which has been NULL since FUNC parts became `fn_ref`-only (wsc5 32f9b1781).
  - The new one mirrors main's constructors: on main, `ofs_test_run` uses `run_mask_or_null(mask, n)` and `req_pres_spans` uses
    `run_mask_or_null(run->whole_mask, run->whole_len)`.
- It is comment text only (`PCREC_CMT_NONESSENTIAL`).
- Witness: in job 586's arms sweep (`worktrees/wsmain/build/wsmain/heavy/sweep_arms.log`:78/93/126/141), the `-fcomments` arm
  reads `differ=4326/4326`, `4360/4360`, `4327/4327` and `4362/4362`. Those are identical counts on the ref and new sides, so 583's
  red no longer reproduces.

## 5. abi claims — MERGE

- **No pcrec abi event.**
  - Every artifact stream in all five sweeps is at 0 movers: c-default, c-vm, emit-ir-vm, emit-ir-auto x4, stderr and composition.
  - The arms family covers 46 arms x 2 streams with matching differ counts.
  - test-codegen (the identity gate) is green.
  - No emitted byte moves against bf33d2dab, so leaving abi at 83 is correct.
- **MF_SITE_ABI 20.**
  - `#define MF_SITE_ABI 20` is at memfn.h:39.
  - Every live reader, found by grep, cites 20: memfn/include/CLAUDE.md:4, memfn.h:261/400/635, kit.h:194/216,
    g2_gen.c:2030, tests/memfn/arm_fixtures.c:59, proof_check.c:2 and run_proof.sh:5.
  - The remaining 19s are in historical lane reports, the journal and responses entries, which are records.
  - Nothing in docs/spec names MF_SITE_ABI.

## 6. D80 — MERGE

The caller-observable moves and their hunks:

- **Stamps.** The values are unchanged, but their source moved to the kit.
  - Hunks: match_api.md §6.3.1¶5a, tuning.md §2.14¶2, §2.14¶3 and §2.30¶2, findings.md §4 (two rows).
- **`--list-limits` PCREC_OFSK_MAX_SET description.** The `src/opt/prefix_k.c:` prefix was dropped from limits.def.
  - It is a declared dumps row (`--dumps-declared-rows=--list-limits:PCREC_OFSK_MAX_SET`, which is judged both ways).
  - The description is free text, so no spec sentence quotes it. Checked by grep.
- **`--emit-facts` `used` column.** See §8.
  - It is covered by facts_listing.md §4.1¶1's general rule ("rows read `used no`" where no pass asked).
  - §4.1.2¶7c does not name a consumer, so no hunk is owed.
- Nothing in docs/spec still names `prefix_k.c`, `exact_len`, `prefix_stated`, `window_stated`, `read_floor` or `consumable`
  (grep: empty).

## 7. Outside memfn/ and src/ — MERGE (for main's eye; nits N2, N3)

- **src/ (pcrec-owned):**
  - emit_dfa.c (+/-719): the NEXT/OfsTest/OFFSETS readers read the phase-1 reply. `req_run_member` is the single resolver of the
    run member.
  - memfn_sites.c: window sites state R-29's facts only.
  - known.c: the cover shadow uses `pcrec_fact_span_stated` unless kit-proof is routed.
  - facts.c/.h: `_stated` reads and the two member stamp helpers.
  - findings.c/.h: `pcrec_find_run_rank` is deleted.
  - internal.h: `PrefixKSets` and `pcrec_prefix_ksets` are deleted.
  - limits.def: the description changes.
  - emit_vm.c: `consumer` is dropped.
  - `src/opt/prefix_k.c` is DELETED.
- **Behaviour note.** `req_run_member` (emit_dfa.c:1143-1151) turns any disagreement between the kit's member and pcrec's own
  `r->idx` into `pcrec_ctx_fail` ("internal error"), which REFUSES the compile instead of falling back.
  - It held on the whole corpus: 0 refusal movers and stderr tags equal on every sweep.
  - It is an assert-shaped invariant, in house style. Main should know that a future kit tie-rule change shows up as a refused
    compile, not as a mover.
- **Other files:**
  - Makefile: `plan_cost.def` was added to KITHDRS, and known.o to the memfn.h dependency list (the wsc3 stale-header incremental
    bug), with comments for both.
  - The `test-memfn-rank` comment was inverted.
  - scripts/emit_sweep.py (+130) gained `--facts-declared-moves` and `--dumps-declared-rows`, with self-tests in
    `scripts/tests/emit_sweep.py.test`.
  - tests/registry/limits_check.sh changed.
  - tests/memfn/* and tests/mech/sabotages: S187, S188, S281, S289, S293, S731-S737, S849, S1222, S1223 and S1226 were retired,
    and S1415-S1421 added.
  - docs/design/memfn/window_site.md is new; there are lane reports and the review file.
- **N2 (doc):** stale comment pointers to the deleted `src/opt/prefix_k.c`:
  - src/facts/facts.h:415 ("The offset-k selection (src/opt/prefix_k.c) reads it"), which is now false;
  - src/core/internal.h:2140;
  - src/facts/kset.c:5 (historical, OK);
  - src/findings/CLAUDE.md:16/20;
  - memfn/src/plan_cost.def:3/36 and window.c:3 cite it as a transcription source at 7050f8652, which is fine.
- **N3 (doc):** docs/design/compare_stack.md (and its ctx_span call-graph snapshots) cite `prefix_k.c:NNN`. These are design
  records, not normative; leave them.

## 8. facts DECLARED MOVES 3451 — MERGE

- What moves: in the `--emit-facts` listing, `span_facts`' `used` cell goes `yes` -> `no`, on 3451 patterns (6828 rows,
  byte+utf8). The wsc8 count was 3356 before main's added corpus.
- Why:
  - On main, the only pass reader of `pcrec_fact_span` besides the cover was memfn_sites.c:525, which computed the site's
    `exact_len` prefix fact.
  - R1 (wsc6 6-k5) retired the prefix facts, so that ask is gone.
  - known.c:259 now asks the non-pass `pcrec_fact_span_stated` unless `pcrec_kit_proof_routed` is set.
  - The listing's force loop still lists the value (§4.1¶1), so only the `used` cell moves.
- Declared and judged both ways: emit_sweep's `--facts-declared-moves` requires every REF row holding `yes` to move to `no`, and
  nothing else in the listing to move, before it reports `movers=0`. All five sweeps print
  `DECLARED MOVES ... patterns=3451 rows=6828`, together with `facts ... movers=0 asymmetric=0`
  (sweep_plain.log:28, the same on the other four). The dumps stream's one declared row, `patterns=1 rows=1`, is the
  PCREC_OFSK_MAX_SET description from §6.
- Expected: yes. A fact that no pass consumes must read `used no`; that is the column's contract.

## 9. Trial merge — MERGE

- `git merge-tree --write-tree bf33d2dab 25ec6f665` returns rc=0 with tree 7b8974979, which is IDENTICAL to `25ec6f665^{tree}`.
  The branch already contains main, so the merge's content is exactly the validated tree.
- `main` is still bf33d2dab. Main's checkout was not touched.

## Follow-up nits (file, none blocks)

- **N1:** memfn.h `mf_wdecide` comment: name the allocation refusal as a -1 cause. This is the kit's file.
- **N2:** src/facts/facts.h:415 and src/core/internal.h:2140 cite the deleted `src/opt/prefix_k.c` as the selection. They should
  name the kit's window family. src/findings/CLAUDE.md:16/20 too.
- **N3:** memfn/CLAUDE.md's peak line (define_sel 3,408 B vs 3,456 B), which the kit already owes.
- **N4:** `req_run_member`'s hard failure on a kit/pcrec member disagreement (§7). Keep it, but name it in the S3 brief so that a
  kit tie-rule change is reviewed as a refusal risk.

## Disclosure

During the read I created and immediately deleted one scratch file, `worktrees/.r29w.c` (gitignored). That was a mis-aimed
redirect. Nothing else was written outside this worktree.
