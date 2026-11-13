# CRITIC ready30bcites: s1

## Findings

### READY-A-1 — §2.1-§2.3's cites (3.0b's Content, the D27 author's source) were not re-based; §2.1's caller prose contradicts the block
CONFIRMED. Severity doc. Effort S (about 20 line numbers). Blast radius: the build lane and the D27 spec-first author, who writes from §2.2-§2.3 alone. Blocks 3.0b: TEXT fix.
The re-base block says "Every cite in 3.0b's text was re-read at 35bee4da9; a cite that moved is rewritten in place". 3.0b's Content is "§2.2-§2.3", but only §3/§4 are in its table, and §2.1-§2.3 still carry a678d0a4e line numbers:
- §2.1 prose: "Today two pcrec callers make the phase-1 ask (`grep -rn mf_wdecide src`: `emit_dfa.c` :1068, :7610)". At BT the callers are :7614 and :16077. The block itself says this, so the doc contradicts itself.
- §2.1 row 1: `window_reply_ask` :7604-7616 asked at :4792 (BT: :7608-7620, asked at :4743); `next_keys` :7298-7306 (BT :7277, read :7297-7299); the offset rows :10471-10500 (BT :10537-10563); `ofs_test_of` :7402-7412 (BT :7381); `pf_site_of` :7131-7146 (BT :7109); `find_site` :6922 (BT :6878); `cand_ask` :8352 (BT :8344); `known.c` :488 (BT :484).
- §2.2 contract line 3: "today's first statement of `mf_wdecide`, `window.c` :1224" (BT :1281; a678's :1224 IS the memset, BT's :1224 is not); `compose.c` :170-171 (BT :171, close enough).
- §2.3: `mf_wreply` at `memfn.h` :1467-1482 (BT :1583-1598, which the block gives only in its layout bullet); `frame_row` ids `window.c` :1616-1621 (BT `wf_erows`/names at :1671-1672, :2189-2190); `compose.c` :1316 `mf_result.row` (BT :1296/:1357); `finder.c` :586-592 `fd_scope` (BT :593).
Repro: `git show a678d0a4e:memfn/src/window.c | sed -n 1224p` prints `memset(out, 0, sizeof *out);`, and BT `window.c` :1281 prints the same line. Fix: add a §2.1-§2.3 row group to the re-base table, or narrow the block's claim to "§3/§4", and correct §2.1's caller sentence.

### READY-A-2 — "the lever is read inside `decide` (`window.c` :938, :1563)": :1563 is in `translate` (phase 2), and decide's other read, :664, is not named
CONFIRMED. Severity doc. Effort XS. Blocks 3.0b: TEXT fix. The conclusion (`mf_wdecide` is pure on a given art) holds.
At BT, `kit_run_opts_of(..art..)` is read at three sites. :664 is in `a_mass_choose`, Table A's choose, which `decide` reaches. :938 is in `run_member`, the C-member row, which `decide` reaches through `c_plan`. :1563 is in `translate`, which `mf_wdecide` does not reach. `translate` is called from `wf_prepare` :2430 after `wf_plan_site` and from the B rows :1628/:1913, so it is define-side only.
Repro: `awk` the enclosing function per line: 664 -> `a_mass_choose`, 938 -> `run_member`, 1563 -> `translate`.
Why it matters: the purity harness's restated wording ("the facts and the art's lever set") and the agreement argument cite these lines as the decision's lever reads. A builder adding the open-question `--harness=run-tie-left` arm needs the right population: decide's A-row (:664) and C-member (:938). Fix: cite :664 and :938 as decide's reads, and :1563 as `translate`'s (the define's rendering, read by both agreement halves through the same art).

### READY-A-3 — ASK-2 survives unmarked in §2.2's contract line 2, which the D27 author reads alone
CONFIRMED. Severity doc. Effort XS. Blocks 3.0b: TEXT fix.
plan_frame §2.2 contract line 2 (SUBJ line 220) reads: "Under NONE `def` is not read and may hold any value (pcrec's ASK-2 passes NULL)". ASK-2 is VOID, and NONE's pcrec user is now ASK-6 (`req_run_at`, `emit_dfa.c` :16077). The contract lines are "what a D27 author tests from this section alone", so this is the one stale ASK-2 mention a blinded author will act on. It is not `[s1d]`-marked.
Two lesser related ones. §1 Non-goals (:161) and §4.2 "Not asked" (:862) still name "a frame for pre-check parts (§7 Q1)", while the block says §7 Q1 "has no subject left". The non-goal stays true (member pre-check parts are still kit-framed through `wf_parts_prepare`/`wf_part_site` :2595/:2470), but Q1's text names `req_run_member` only. Q1 should be restated or marked rather than left subjectless while two sections cite it.
Repro: `git show SUBJ:docs/design/memfn/plan_frame.md | grep -n "ASK-2 passes"` -> :220.

### READY-A-4 — three imprecise `[s1d]` cites (range edges, a reader's field list)
CONFIRMED. Severity doc. Effort XS. Blocks 3.0b: TEXT fix (optional; a builder would find each by eye).
- `struct wf_plan` "`window.c` :1299-1331": the struct runs :1299-1341 (`};` at :1341). The members it names, `srch`/`fused`/`strm`/`chk`, are at :1326-1329, which is inside the cited range.
- "Readers that copy the reply ... `g2_win_gen.c` :947-948": the field-by-field copy of `mf_wreply` into `g2w_reply` is :942-949 (alt..path). :947-948 are only its run-field lines, and the frame part's copy is appended after :949.
- `req_run_at`'s second reader "`us.wr.run_stated`/`run_member`, :16089-16092" also reads `us.wr_stated` and `us.wr.pinned` (:16089). The conclusion (ASK-1's decision group, untouched) holds.

## PROBED-AND-HELD

Checked at BT 35bee4da9, in worktrees/crit-s1 (HEAD verified) and by `git show`/`git grep`. 0 compiles, about 45 greps/reads.

**(a) The cites and factual claims that held** (about 60 cites, every one in the re-base block and its table):
- ASK-2's subject is gone: no `req_run_member` anywhere in src/.
- `req_run_at` is at `emit_dfa.c` :16050, with `mf_wdecide` at :16077 on `pcrec_cover_site`. It reads `has_stop` and `stop` only (into `req_run_in_cover`). Commit 2c3b2097e's subject matches.
- `window_reply_ask`'s call is at :7614 and its refusal at :7614-7617. The comment is at :7602-7607 and `ofs_site_define` at :7626-7646. `cand_asked_hold` is at :7044-7063, the `wr` comment at :4582-4588, and `ofs_test_of`'s `run_lo`/`run_len` at :7400-7401.
- `mf_wreply` is at `memfn.h` :1583-1598, `path` last, and its layout is unmoved. `MF_SITE_ABI` is 27 (:39) and the entries run to :243 (MF_VOCAB at :244). `MF_CLASS_V` is 9 (:1155). The comments are at :605-607, :1551-1557 and :1599-1602.
- `memfn/include/CLAUDE.md` :4 is stale (25/8), as the design says.
- `window.c`: `wf_plan_site` :2321; `wf_prepare` :2403 (call :2420, stores :2424-2427); `wf_parts_prepare` :2573 with its `wf_prepare` call at :2595; `derive_run_part` :2543; `wf_floor_uses` :3409-3417; MF_CLASS_V :3352; comments :51 and :1282.
- `kit.h`: `fd_ren` :266, inside :242-273.
- `compose.c`: `select_arm` :264, comment :255-261; `kit_legacy_serves` :310-316; the rule-2 re-ask through `ask_sel` :1221-1227; MF_CLASS_V :367 and :1054.
- `finder.c` `fd_opt` :521-523. `gate.c` MF_MISS_N :673-678.
- `arm_fixtures` `pur_diff` :2246 and control print :2370-2378. `run_finder.sh` PURITY_FLOOR=1157 at :158 (read :164, header :147). `tests/memfn/CLAUDE.md` :45.
- ASK-4's suites: `run_cand_oracle.sh` :90 and `run_fallback_table.sh` :143, both unchanged.
- `known.c` `pcrec_cover_site` :484.

**(b) Completeness held.**
- `mf_wdecide` callers by grep over the whole tree (non-md) number exactly 10: `emit_dfa.c` :7614 and :16077; `arm_fixtures.c` :2313, :2320, :2347, :2365; `g2_win_gen.c` :817, :877, :941; `run_decide_check.c` :207. The block lists all 10, plus `r33_sim/probe.c` :94 (successor probe per Q15). The census jobs `240-kit-r33-sweep.sh`/`241-kit-r33-rp.sh` build it.
- No `docs/design` C/py calls it. pcrec-bench (4ac9832b) has 0 callers or readers (only a historical inbox number).
- `mf_wreply` readers and copies are all in the block or in §3/§4.2: `emit_dfa.c` :4590/:7383/:16073, g2_win_gen, g2_win_run.c :99-103, g2_win.h :44-53, arm_fixtures, run_decide_check, probe.c/collect.py.
- MF_SITE_ABI symbolic readers by grep equal the table's list exactly (memfn_sites :459, compose :1036/:1093-1095, window :1283/:1483, presence :271, formhash :383, g2_gen x9, g2_simd :340, g2_win x4, g2_pres_gen :338, arm_fixtures :247, mass :267, policy :59, proof :164, proven :63, run_decide :109).
- The historical count is 345 lines in 78 files with journals/requests/responses excluded, against the design's 354/79: same order, ledger definition loose, held.
- No literal pins. `docs/spec`/`docs/guide` name neither `mf_wdecide` nor `mf_wreply`, so there is no spec hunk.
- No mech sabotage anchors on a line 3.0b edits. S3042 anchors above :16077 in `req_run_at`, not on the ask.
- The highest file-named sabotage id on any local branch is S3077, so S3078+ holds.

**Goals lens:** the re-based 3.0b still serves §1 in order. Goal 1: ASK-6 is NONE, so `stop` is unchanged by R27's decision-prefix equality, and no byte moves. Goals 2-3: the agreement and purity are unchanged; the lever read is per-art, so both halves agree. Goals 4-5 are untouched. Nothing in the re-base reorders the goals.

## VERDICT (3.0b cites/completeness): READY WITH LISTED TEXT FIXES (READY-A-1 required; A-2, A-3 small; A-4 optional). No design fix: every caller and reader the build would break is named.
