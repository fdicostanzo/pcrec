# plan.md item-by-item triage — 2026-10-12 ([PLAN-LINT] step 1)

Lane `plantri`, read-only against `docs/dev/plan.md` at main `43f78acc1` (1,353 lines, 478,786 bytes, 262 `[ID]` rows + 1 template pseudo-row, 23 headings). Nothing in plan.md was edited. Evidence = commits (all cited hashes verified as ancestors of main), `docs/dev/plan_completed.md`, `decisions.md`, `docs/dev/lanes/*_report.md`, `known_issues.md`, and the tree. Row numbers are plan.md line numbers at this commit. "Wedged" = a row physically inserted inside another row or between a parent and its child.

Classes: **COMPLETED** (done; evidence cited), **SUPERSEDED** (no longer relevant; by what), **DUPLICATE** (of which row), **STALE** (row is live but its status/notes/trigger are out of date; what is stale), **JUNK** (not a row, or an archive stub), **LIVE** (keep; one line why). One class per item; where an item is two things the evidence says so.

## 1. Summary

| class | rows | row KB | free-text blocks | total | proposed action in one phrase |
|---|---:|---:|---:|---:|---|
| COMPLETED | 20 | 60 | 1 | 21 | archive to plan_completed.md |
| SUPERSEDED | 6 | 8 | 0 | 6 | delete / merge into the superseder |
| DUPLICATE | 33 | 21 | 5 | 38 | delete or merge (one id, one row) |
| STALE | 24 | 86 | 12 | 36 | rewrite status / move remainder, then keep or close |
| JUNK | 34 | 17 | 17 | 51 | delete (stubs, notes, headings) |
| LIVE | 145 | 266 | 5 | 150 | keep (reformat to canonical row) |
| **total** | **262** | **459** | **40** | **302** | |

Reading it: of 262 rows only 145 (55%) are plain LIVE; 20 are completed work still resident (7 of them with the disallowed `STATE:done`), 34 rows are archive stubs/lead-ins, 33 are duplicates (26 are the index block, which already DIVERGES from the full rows it copies), 6 are superseded, 24 are live but wrong in a stated way. Of the free-text blocks, none is a row; 29 of 40 are junk or stale. 93 rows (35%) can leave the file with no loss of a live commitment; the 24 STALE rows need a human edit; the SUPERSEDED and a few COMPLETED calls are marked for Frank to confirm in the evidence column.

## 2. Frank's named examples, answered

| example | where | verdict | recommendation |
|---|---|---|---|
| [XARCH] | 227 | STALE (step 0 COMPLETED; remainder tabled) | 3.4 KB row = delivered step 0 (xarch_step0.md, merged 2026-09-05) + a tabled remainder (clang column, iso-ts redo, pinned-10.46 jit column). The "future round for architecture specific opt" it waits for is now [OPT-SIMD] / D144 addendum 4 (verdicts per targeted hardware). Archive step 0; keep a 3-line deferred stub pointing at [OPT-SIMD]. |
| M4 and its sub-rows | 107-219, 116-173 | JUNK | six stubs ([M4.1]-[M4.5],[M4.7]) restate rows that are in plan_completed.md; M4.4 and M4.5 stubs are paragraph-sized. The two "design notes" at 184-219 are design docs (backrefs_design.md, atomic_groups_design.md). Delete the whole M4 section. |
| "Development Order" | 55-85 | STALE -> delete | STD1, M4, M5, M6 are complete; [BENCH-1] closed 2026-09-22; the OPT-wave ordering (MECH-3 first) is overtaken by D119/[OPTLOOP]. Keep one line: remaining spine = M3, then M7. |
| "Next: M4.." | 87-105 | JUNK | dated 2026-08-14 hand-off ("NEXT: [M4.4]") for a milestone that completed 2026-08-18. Delete. |
| random design notes | 184-219, 288-312, 1257-1263, 1153-1162 | JUNK | backrefs and atomic-groups notes (captured in docs/design), the 25-line POSITIONING NOTE, the "Process mechanization" anecdote and the D21 "optimization waves" motto are prose, not rows. Move positioning to APPROACH.md; delete the rest. |
| "archived to plan_completed.md" stubs | 31 rows | JUNK | the stubs: M4.1-M4.5,M4.7, K50-BNDSTART, LIM-OVR, MACPORT-XARGS, M6.0-M6.6, SPEC-M, ABI-NS, M6-READ, REL-1, OPT-HYB-RESEED-FORM, OPT-VEDGE, SAFEKILL, DD-9, DD-14, ART-POSS-ARMS, SR-11, TT-3, DOC-DRV (+ FINDINGS, DD-13, DD-11, which still carry STATE:completed). All their full rows are verified present in plan_completed.md. Delete all; the lint should forbid stubs (a row is either here or there). |
| [read-bytes] -> readability | 232, 984 | DUPLICATE (overlap) | [READ-BYTES] (2026-09-05, readable byte values) and [VM-READABLE] (2026-10-12, readable VM body) are one theme, both emitted-scaffolding abi events, both sonnet/M6-READ-shaped. VM-READABLE item (3) spells bytes as numbers (`!= 123`), which READ-BYTES would render as `'{'`. Merge into one emitted-readability row so they ride one abi event; [M6-READ] (done) is the model. |
| M3.0 | 259 | LIVE | M3 streaming is the one open spine milestone (README.md:60); design gate still the next step. Absorb [OS-3] (a pure input to it). |
| M3.1 | 260 | LIVE | blocked behind M3.0 design gate; keep as a child. |
| M7.0 | 268 | STALE | "differential fuzzing vs libpcre2" is done (tests/fuzz/, PC-3, PC-4); "freestanding" is [FREESTANDING]; only "PCRE2 testdata import" is unrepresented. Rewrite to the real residue or drop. |
| [REL-0.2] | 272 | COMPLETED | merged 98fc4c82 (2026-10-03), tag v0.2.0-beta exists. STATE:completed in a file that forbids it; archive. |
| "Beyond M7" | 281-286 (+135 rows) | STALE | a heading that claims "direction, not scheduled work" over 135 rows (51% of the file), including [OPTLOOP] and 19 of the 20 started rows. The name is wrong for its content. Dissolve into Active / Candidates / Backlog / Boonies. |
| any STATE:done | 317, 555, 1307, 1313, 1318, 1319, 1323 | COMPLETED (7 rows) | `done` is not an allowed state (header: not-started\|started\|completed\|blocked\|deferred) and these are finished: TT-MECHPAR, AXES-DENY-MASK, SIZE-CAP-FLAG, DEC-VAR-ATTRIB, DEC-FALLBACK (14 KB), DEC-COLLAPSE-WASTE, START-TABLE (8 KB). All merged (hashes in the row table). Archive. |
| "refiled" rows | 346-349, 960-961, 314 | LIVE (but the refile pattern is a smell) | seven rows REFILED 2026-09-30 by parkmeas out of CLOSED parent rows ([OPT-3-RUNEND], [OPT-5-PERIODK], [ENG-ABS-CARET], [ENG-ISL-S2], [DD-13b.W1.3.1], [DD-13b.W1.4], [TT-4M-ATTRIB]). None has had its measurement run (no opt3s3/opt5pk/attemptcensus/islcensus/tt4mattrib lane or report exists). They are legitimate parked candidates; their parents are archived, so each carries its own history paragraph. No action beyond reformatting; [ENG-ABS-CARET] should cross-link [MATCH-SPLIT]. |
| [ENG-ISL-S2] | 349 | LIVE | refiled 2026-09-30; D77 trigger unmet (needs an OPTLOOP cell that scores it); census never run; bench O-82 A4 gave a lower bound only. |
| the two [SEL-COST] items | 230 and 357 | DUPLICATE + STALE | 230 is the full row (misfiled under "M5 - UTF-8") and records the latest status: step 1 designed 2026-10-03 and NOT built, no bucket clears D119 (docs/design/sel_cost.md). 357 is an index-pointer copy that still says "NEED: the four bench questions" and that SEL-SIZE "becomes one instance" - both overtaken ([SEL-SIZE] closed as REFUTED 2026-10-03). Delete 357 (and 358, the SEL-SIZE index copy); move 230 under [OPTLOOP] candidates with its status rewritten. |

## 3. File-rule violations (the header's own rules)

Header rules: "States: not-started | started | completed | blocked | deferred" and "this file keeps zero STATE:completed rows".

**3a. Rows tagged `STATE:completed` (11 rows; the header promises zero; `grep -c STATE:completed docs/dev/plan.md` = 14 lines):**

| line | id | note |
|---:|---|---|
| 229 | [SEL-SIZE] | also misfiled under M5; duplicate at :358 |
| 272 | [REL-0.2] | requested example |
| 324 | [FLAG-ACCESS] |  |
| 351 | [REVEND-WALK-FORM] | today (2026-10-12, session 110) |
| 389 | [CAND-PATH-READS] | merged 2026-10-12 |
| 395 | [GUIDE-OPT-LEVEL] |  |
| 405 | [REQ-HANDOFF-L1] |  |
| 413 | [FINDINGS] | archive STUB that carries the tag |
| 959 | [DD-13] | archive STUB that carries the tag (+4 ids) |
| 963 | [DD-11] | archive STUB that carries the tag |
| 1296 | [CLS-TREE] | 13.3 KB; plus orphan paragraph :1298 |

Plus `STATE completed` (colon-less, index copy) at :358.

**3b. Rows tagged `STATE:done` (not an allowed state, 7 rows):** :317 TT-MECHPAR, :555 AXES-DENY-MASK, :1307 SIZE-CAP-FLAG, :1313 DEC-VAR-ATTRIB, :1318 DEC-FALLBACK, :1319 DEC-COLLAPSE-WASTE, :1323 START-TABLE.

**3c. Completed work spelled in prose instead of a state (31 stub rows):** `COMPLETED <date> — row archived in plan_completed.md` (M4.1-M4.5, M4.7, OPT-HYB-RESEED-FORM, OPT-VEDGE, DD-9, ART-POSS-ARMS), `archived to plan_completed.md (...)` (K50-BNDSTART, LIM-OVR, MACPORT-XARGS, M6.0-M6.5, SPEC-M, ABI-NS, M6-READ, REL-1, SAFEKILL, SR-11, TT-3, DOC-DRV), `ARCHIVED →` (M6.6, DD-14). The header's "completed rows are archived" is honored by moving them and then leaving a 1-3 line tombstone each, which nothing asks for.

**3d. Header recipes that no longer hold:** `grep -n "STATE:started"` matches the recipe lines themselves (:20-23) and prose as well as rows; "ANCHORED count (81 on 2026-09-22)" is a stale literal; `grep -cE "^[[:space:]]*- \[[^]]*\] STATE:not-started"` misses the 28 colon-less index rows and counts the 26 duplicated ids twice.

## 4. Row table (every `[ID]` row)

Columns: line | id | state as written (`~x` = colon-less `STATE x`) | chars | class | evidence | proposed action. Title column omitted to keep rows narrow; the id is the key.

| line | id | state | chars | class | evidence | action |
|---:|---|---|---:|---|---|---|
| 60 | [STD1] | (none) | 1035 | JUNK | `[STD1]` bullet inside the obsolete spine list; STD1 completed 2026-08-13 (plan_completed.md has the row) | delete with the section |
| 116 | [M4.1] | (none) | 272 | JUNK | archive stub; [M4.1] COMPLETED 2026-08-14 (merge 65b16c6), full row in plan_completed.md | delete |
| 120 | [M4.2] | (none) | 595 | JUNK | archive stub; [M4.2] COMPLETED 2026-08-14 (merge b726386), row in plan_completed.md | delete |
| 129 | [M4.3] | (none) | 725 | JUNK | archive stub; [M4.3] COMPLETED 2026-08-14 (R21, freeze declared), row in plan_completed.md | delete |
| 140 | [M4.4] | (none) | 1162 | JUNK | completed-row-sized status paragraph for [M4.4] (merge c18e904); row is in plan_completed.md:1693 | delete |
| 157 | [M4.5] | (none) | 1053 | JUNK | completed-row-sized status paragraph for [M4.5]; row is in plan_completed.md:1736 | delete |
| 173 | [M4.7] | (none) | 496 | JUNK | archive stub; [M4.7] COMPLETED 2026-08-18 (fix merge d523a88) | delete |
| 223 | [UTF-PAT] | not-started | 2055 | LIVE | chartered 09-05, unscheduled; no raw-UTF-8-pattern contract/corpus arm exists in tests/utf8; text still says "stage 2" although M5.0 closed 2026-09-12 | keep; update text (drop stage wording) |
| 224 | [K50-BNDSTART] | (none) | 221 | JUNK | archive stub; K50-BNDSTART completed 2026-09-06 (8e0fe77f, abi 24) | delete |
| 225 | [UTF-RW] | not-started | 3068 | STALE | its sequencing condition ("after M5.0 stages 3-5 land") is met (M5.0 closed 2026-09-12, m5close_report.md) but the row still reads as gated | keep; update trigger text to "unblocked, unscheduled" |
| 226 | [UTF-EXTENT] | not-started | 889 | LIVE | filed 2026-09-30 by uvbuild, "recorded, NOT built" (D133 Q2) | keep |
| 227 | [XARCH] | deferred | 3477 | STALE | step 0 delivered+merged 2026-09-05 (xarch_step0.md, xarch0_report.md); the row is ~3.4 KB of delivered history around a tabled remainder (clang column, iso-ts redo, pinned-10.46 jit column); the "round for architecture-specific opt" it waits for IS [OPT-SIMD] / D144 add. 4 (verdicts per targeted hardware) | archive step 0 to plan_completed.md; keep a 3-line deferred stub pointing at [OPT-SIMD] |
| 228 | [FORM-CHAR2] | not-started | 1928 | STALE | row says "RULED 2026-09-11 SUBSUMED INTO [CLS-TREE]" yet [CLS-TREE] closed 2026-10-03 with D138 Q1 "measure first - the fold default stays pending FORM-CHAR2"; the two statements contradict. Overlaps [CLS-FOLD-WAF744] (same cls-fold timing question) | update text; merge with [CLS-FOLD-WAF744] |
| 229 | [SEL-SIZE] | completed | 1035 | COMPLETED | STATE:completed in this file (rule: zero such rows); CLOSED AS REFUTED, RULED 2026-10-03 (docs/design/sel_cost.md). Also misfiled under "M5 - UTF-8"; a second copy sits at :358 | archive; delete :358 copy |
| 230 | [SEL-COST] | not-started | 2371 | STALE | row is in the wrong section (M5) and its status is behind: step 1 was designed and NOT built 2026-10-03 (docs/design/sel_cost.md, selcostdes_report.md: no bucket clears D119 as a compile-time term); the admission-rule trigger is the live part. The index copy at :357 is older still | move under [OPTLOOP] candidates; rewrite status to "designed, trigger = admission rule"; delete :357 copy |
| 231 | [LIM-OVR] | (none) | 307 | JUNK | archive stub; LIM-OVR delivered 2026-09-22 (lane admin1) | delete |
| 232 | [READ-BYTES] | not-started | 2153 | DUPLICATE | overlaps [VM-READABLE] (filed 2026-10-12): both are emitted-code readability, both an abi event; VM-READABLE item (3) even spells bytes as numbers (`!= 123`) which this row would render as `'{'` | merge into one emitted-readability row (READ-BYTES + VM-READABLE), one abi event |
| 234 | [MACPORT-XARGS] | (none) | 335 | JUNK | archive stub; MACPORT-XARGS found already fixed 2026-09-22 (fb1b9c5e) | delete |
| 238 | [M6.0] | (none) | 569 | JUNK | archive stub; M6.0 CLOSED 2026-08-25 (D79); rows live in plan_completed.md | delete |
| 239 | [M6.1] | (none) | 309 | JUNK | archive stub; M6.1 completed 2026-08-18; rows live in plan_completed.md | delete |
| 240 | [M6.2] | (none) | 223 | JUNK | archive stub; M6.2 completed 2026-08-21; rows live in plan_completed.md | delete |
| 241 | [M6.3] | (none) | 127 | JUNK | archive stub; M6.3 completed 2026-08-18; rows live in plan_completed.md | delete |
| 242 | [SPEC-M] | (none) | 130 | JUNK | archive stub; SPEC-M completed 2026-08-21; rows live in plan_completed.md | delete |
| 243 | [M6.4] | (none) | 572 | JUNK | archive stub; M6.4 completed 2026-08-22; rows live in plan_completed.md | delete |
| 244 | [M6.5] | (none) | 3412 | JUNK | archive stub; M6.5 completed 2026-08-22 (status paragraph ~3.4 KB); rows live in plan_completed.md | delete |
| 245 | [M6.6] | (none) | 285 | JUNK | archive stub; M6.6 completed 2026-08-24, already says ARCHIVED; rows live in plan_completed.md | delete |
| 246 | [ABI-NS] | (none) | 157 | JUNK | archive stub; ABI-NS completed 2026-08-18; rows live in plan_completed.md | delete |
| 256 | [M6-READ] | (none) | 335 | JUNK | archive stub; M6-READ completed 2026-08-21; rows live in plan_completed.md | delete |
| 259 | [M3.0] | not-started | 373 | LIVE | M3 streaming is the one open spine milestone (README.md:60); no design started | keep; fold [OS-3] into it |
| 260 | [M3.1] | not-started | 84 | LIVE | blocked behind M3.0 design gate | keep |
| 268 | [M7.0] | not-started | 152 | STALE | "differential fuzzing vs libpcre2" is DONE (tests/fuzz/, PC-3/PC-4 registry-vs-libpcre2, fuzz gate); freestanding is its own row [FREESTANDING]; only "PCRE2 testdata import" is unrepresented elsewhere | rewrite to the two real residues (testdata import, freestanding link) or delete if Frank drops testdata import |
| 272 | [REL-0.2] | completed | 1585 | COMPLETED | STATE:completed in this file; merged 98fc4c82 (2026-10-03), tag v0.2.0-beta exists | archive (the "next version bump" role passes to a new row only when wanted) |
| 277 | [EMIT-ENTRIES] | not-started | 1371 | DUPLICATE | overlaps [EMIT-SET] (:550): both = choose which entry points/units are emitted; B0 of [COMPOUND] already built the entry-table internals (cpb02_report.md "B0 [EMIT-ENTRIES] internal") and this row does not say so | merge [EMIT-SET] and [EMIT-ENTRIES] into one row; record B0 |
| 278 | [LANG-1] | not-started | 1546 | LIVE | chartered 2026-09-21; docs/guide/lang/README.md exists but no examples/<lang> beyond makefile | keep |
| 279 | [LANG-2] | not-started | 509 | LIVE | chartered 2026-09-21, behind [LANG-1] | keep |
| 314 | [TT-4M-ATTRIB] | not-started | 1197 | LIVE | refiled 2026-09-30 by parkmeas (D137 item 3); attribution run never launched (no tt4mattrib lane/report) | keep |
| 315 | [TT-13] | not-started | 1691 | STALE | premise changed: filed 2026-09-04 when the full battery took ~4 h on the dev box; since 2026-10-07 the Linux dev box runs `make test` in ~11 min (BOILERPLATE box facts, 678.6 s) and [TT-MECHPAR] fixed the mech serial throttle (3.3x) | ask Frank: close as superseded, or restate against the new box |
| 316 | [TT-15] | not-started | 3611 | STALE | same premise as [TT-13] ("full validation takes 4 hours on the dev box"); the new Linux box and [TT-MECHPAR]/[TT-JTUNE] answer the cost complaint | ask Frank: close as superseded |
| 317 | [TT-MECHPAR] | done | 1831 | COMPLETED | STATE:done (not an allowed state); MERGED 2026-10-09 lane/mechpar, mechpar_report.md | archive |
| 318 | [TT-JTUNE] | started | 1160 | LIVE | perfrun + rotation ledger are standing instrument (BOILERPLATE heavy-chain template); ledger readings still being appended | keep |
| 319 | [SPEC-LANG] | not-started | 1790 | LIVE | filed 2026-10-09 FOR EVALUATION | keep |
| 320 | [RXT-ONE-READER] | not-started | 1263 | LIVE | filed 2026-10-10; [RXT-READERS] (done) only re-aligned the grammar | keep |
| 321 | [ORACLE-OPTS] | not-started | 821 | LIVE | filed 2026-10-10 | keep |
| 322 | [K50-HARVEST] | not-started | 645 | DUPLICATE | same topic as [K50-DD12AI-MANIFEST] (:424): DD12a(i)/K50 manifest drift at full population, re-harvest owed | merge into [K50-DD12AI-MANIFEST] |
| 323 | [IFACE-PUSH] | not-started | 1173 | LIVE | umbrella with a hard trigger (<= 4 flag bits left of 64) | keep |
| 324 | [FLAG-ACCESS] | completed | 1505 | COMPLETED | STATE:completed in this file; MERGED 67f59d24 2026-10-10 (gate flag_access_check.py, S792) | archive; carry "RESIDUE FOR [IFACE-PUSH]" sentence into that row |
| 325 | [SPEC-ORG] | not-started | 1707 | LIVE | filed 2026-10-10, document-only, "maybe not ever" | keep |
| 326 | [SPEC-1.11] | not-started | 2019 | LIVE | boonies; 2026-08-29 | keep |
| 327 | [GUIDE-1] | not-started | 807 | SUPERSEDED | docs/guide/ exists with 8 chapters (merged 2026-09-21 as [REL-1.3], plan_completed.md:4260); the row's "starts after [SPEC-1]..." and "[REL-META]'s README pass" are both gone | archive/delete |
| 339 | [REL-1] | (none) | 183 | JUNK | archive stub; REL-1 completed 2026-09-22 (v0.1.0-beta) | delete |
| 340 | [OPTLOOP] | started | 5401 | STALE | head still carries "next cycle HELD (Frank 2026-09-26, D125)" but D144 (2026-10-03) lifted that hold and the cycle is open; head is a 5.4 KB stack of dated parentheticals | rewrite head as charter + current round; move history to a journal/summary |
| 341 | [LOSS-REVIEW] | started | 1591 | LIVE | phase 3 in progress; candidate 1 merged 2026-10-12 (4cd82e8d, abi 76) | keep; trim layered status |
| 342 | [OPT-HYB-RESEED-FORM] | (none) | 163 | JUNK | archive stub; A1 shipped a588c668, A2 dropped | delete |
| 343 | [OPT-HYB-RESEED-POLICY] | not-started | 1717 | DUPLICATE | its own text says "D153: folded into the ONE retry-slot row [START-DENSE]" | delete; keep the disarm-rule sentence in [START-DENSE] |
| 346 | [OPT-3-RUNEND] | not-started | 1637 | LIVE | refiled 2026-09-30; trigger unmet (needs a non-periodic subject measurement; O-82 A1 now supplies one subject) | keep; update with O-82 A1 subject |
| 347 | [OPT-5-PERIODK] | not-started | 2483 | LIVE | refiled 2026-09-30; D77 trigger unmet | keep |
| 348 | [ENG-ABS-CARET] | not-started | 1865 | LIVE | refiled 2026-09-30; shares its single witness with [OPT-ATTEMPT-SPLIT]/[MATCH-SPLIT] START+FREE step and [OS-4] | keep; cross-link to [MATCH-SPLIT] step 2 |
| 349 | [ENG-ISL-S2] | not-started | 1730 | LIVE | refiled 2026-09-30; STEP 2 census never run (no islcensus lane); trigger unmet | keep |
| 350 | [OPT-REVEND] | started | 5148 | LIVE | started; L1/L2 + stage 2 merged 7388f1c0; rev-end-width measured; head is a 5 KB nest of 8 parenthesised statuses (oldest innermost) | keep; rewrite head as charter + one status line |
| 351 | [REVEND-WALK-FORM] | completed | 889 | COMPLETED | STATE:completed in this file; ANSWERED 2026-10-12 by b3rev (form W) | archive; move the one-line answer to [OPT-REVEND] |
| 352 | [REVBLOCK-VIEW] | not-started | 591 | LIVE | filed 2026-10-12, trigger = B3 build lands form W | keep |
| 353 | [VM-LEN-HOIST] | not-started | 1182 | LIVE | filed 2026-10-12, measurement first | keep |
| 354 | [MATCH-KNOWN] | not-started | 1390 | LIVE | filed 2026-10-12, discuss before design | keep |
| 355 | [ARTREV] | started | 1182 | LIVE | started; pilot complete 2026-10-06, full run decided, nothing run since (no report.md in optloop/artrev) | keep (idle); mark waiting |
| 357 | [SEL-COST] | ~not-started | 651 | DUPLICATE | index-pointer copy of [SEL-COST], whose full row is at :230; the two already DIVERGE (this copy is OLDER: still says "NEED: the four bench questions" / "[SEL-SIZE] becomes one instance") | delete; keep the full row, add a generated candidates index if wanted |
| 358 | [SEL-SIZE] | ~completed | 397 | DUPLICATE | index-pointer copy of [SEL-SIZE], whose full row is at :229; the two already DIVERGE (this copy is OLDER: still says "NEED: the four bench questions" / "[SEL-SIZE] becomes one instance") | delete; keep the full row, add a generated candidates index if wanted |
| 359 | [OPT-HYB-RESEED-XCALL] | ~not-started | 1704 | DUPLICATE | index-pointer copy of [OPT-HYB-RESEED-XCALL], whose full row is at :552; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 360 | [CTX-PREFILTER] | ~not-started | 481 | DUPLICATE | index-pointer copy of [CTX-PREFILTER], whose full row is at :1304; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 361 | [OPT-ENDWIN-ENC] | ~not-started | 305 | DUPLICATE | index-pointer copy of [OPT-ENDWIN-ENC], whose full row is at :553; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 362 | [TIE-ALIGN] | ~not-started | 436 | DUPLICATE | index-pointer copy of [TIE-ALIGN], whose full row is at :1303; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 363 | [OPT-VMLIT] | ~not-started | 549 | DUPLICATE | index-pointer copy of [OPT-VMLIT], whose full row is at :1209; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 364 | [WORD-FOLD] | ~not-started | 793 | DUPLICATE | index-pointer copy of [WORD-FOLD], whose full row is at :1288; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 365 | [OPT-A] | ~not-started | 550 | DUPLICATE | index-pointer copy of [OPT-A], whose full row is at :1204; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 366 | [OPT-VEDGE] | (none) | 186 | JUNK | archive stub; OPT-VEDGE COMPLETED 2026-10-04 (a588c668) | delete |
| 367 | [OPT-NEG] | ~not-started | 385 | DUPLICATE | index-pointer copy of [OPT-NEG], whose full row is at :1205; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 368 | [OPT-ALTHASH] | ~not-started | 429 | DUPLICATE | index-pointer copy of [OPT-ALTHASH], whose full row is at :1207; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 369 | [OPT-SIMD] | ~started | 1028 | DUPLICATE | index-pointer copy of [OPT-SIMD], whose full row is at :1210; the two already DIVERGE (this copy is NEWER: it records RQ-3/RQ-2 merged 2026-10-09, the full row does not) | delete; keep the full row, add a generated candidates index if wanted |
| 370 | [MEMFN-ENTRYSINK] | ~not-started | 1360 | LIVE | FILED, NOT SCHEDULED 2026-10-08; a real row hiding inside the duplicate index block | keep; move out of the index block (under [MEMFN] / boonies) |
| 371 | [MEMFN-CI-ASCII] | ~not-started | 557 | LIVE | FILED, NOT SCHEDULED 2026-10-09; a real row hiding inside the duplicate index block | keep; move out of the index block (under [MEMFN] / boonies) |
| 372 | [MEMFN-RTDISPATCH] | ~not-started | 1249 | LIVE | FILED, NOT SCHEDULED 2026-10-08 (D155); a real row hiding inside the duplicate index block | keep; move out of the index block (under [MEMFN] / boonies) |
| 373 | [SIMD-META] | ~not-started | 139 | DUPLICATE | index-pointer copy of [SIMD-META], whose full row is at :607; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 374 | [OPT-B] | ~not-started | 395 | DUPLICATE | index-pointer copy of [OPT-B], whose full row is at :1235; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 375 | [OPT-C] | ~not-started | 382 | DUPLICATE | index-pointer copy of [OPT-C], whose full row is at :1236; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 376 | [OPT-D] | ~not-started | 391 | DUPLICATE | index-pointer copy of [OPT-D], whose full row is at :1237; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 377 | [XART-TABLES] | ~not-started | 415 | DUPLICATE | index-pointer copy of [XART-TABLES], whose full row is at :1238; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 378 | [BREF-FOLD-ONCE] | ~not-started | 458 | LIVE | boonies 2026-10-09; a real row hiding inside the duplicate index block | keep; move out of the index block (under [MEMFN] / boonies) |
| 379 | [EMIT-ALIGN] | ~not-started | 325 | DUPLICATE | index-pointer copy of [EMIT-ALIGN], whose full row is at :1281; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 380 | [ENG-TACTICS] | ~not-started | 456 | DUPLICATE | index-pointer copy of [ENG-TACTICS], whose full row is at :421; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 381 | [ENG-THIN] | ~not-started | 350 | DUPLICATE | index-pointer copy of [ENG-THIN], whose full row is at :661; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 382 | [ENG-PGO] | ~not-started | 401 | DUPLICATE | index-pointer copy of [ENG-PGO], whose full row is at :694; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 383 | [ENG-DIRECT] | ~not-started | 468 | DUPLICATE | index-pointer copy of [ENG-DIRECT], whose full row is at :737; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 384 | [ENG-COUNT] | ~not-started | 431 | DUPLICATE | index-pointer copy of [ENG-COUNT], whose full row is at :794; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 385 | [ENG-CLAMP] | ~not-started | 268 | DUPLICATE | index-pointer copy of [ENG-CLAMP], whose full row is at :795; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 386 | [ENG-LOOK] | ~not-started | 440 | DUPLICATE | index-pointer copy of [ENG-LOOK], whose full row is at :816; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 387 | [ENG-CUT] | ~not-started | 311 | DUPLICATE | index-pointer copy of [ENG-CUT], whose full row is at :859; the two already DIVERGE | delete; keep the full row, add a generated candidates index if wanted |
| 388 | [OPT-FIRSTSET] | started | 6299 | STALE | 2026-10-10 planaudit prefix itself says stages 0-3 LANDED (f3c726d7, 57db5152, 8148e034 all on main) and "owed clauses below are historical"; 6.3 KB of history around a ~2-line remainder (batch gate, K90/K91 under [START-DENSE]) | archive as completed; move the remainder to [START-DENSE] |
| 389 | [CAND-PATH-READS] | completed | 1338 | COMPLETED | STATE:completed in this file; MERGED 35c0b923 2026-10-12 | archive |
| 390 | [COMPOUND] | started | 1951 | LIVE | started; B0-B2 merged 2a54c3e71, B4 in flight (cpb4), B3 built (b3build) | keep; trim layered head |
| 391 | [MATCH-SPLIT] | started | 2268 | LIVE | started; 4a design note + rebuild-as-compound (D163) | keep |
| 392 | [OPT-ATTEMPT-SPLIT] | not-started | 2178 | SUPERSEDED | its own head: "2026-10-11: SUBSUMED as the start-pinned member of [MATCH-SPLIT]" | delete; keep the cycle1 M5 evidence as a link in [MATCH-SPLIT] |
| 393 | [CAPS-VIEW-RERENDER] | not-started | 971 | LIVE | filed 2026-09-28 (admin88), residual #4 of cycle 2 | keep |
| 394 | [CAPTURES-DFA-MB] | not-started | 1678 | LIVE | filed 2026-09-28, residual #5 | keep |
| 395 | [GUIDE-OPT-LEVEL] | completed | 1103 | COMPLETED | STATE:completed in this file; DONE 2026-10-03 (one sentence in docs/guide/getting-started.md) | archive |
| 396 | [OPT-GAPREPORT] | started | 1361 | COMPLETED | planaudit 2026-10-10: "DELIVERED ... nothing is unbuilt"; stays started only as a standing "run at round boundaries" duty (gapscript 0bb52eab, gaprep, o83read) | archive; move the duty sentence to [OPTLOOP] |
| 397 | [BENCH-ASKS-PENDING] | not-started | 1714 | JUNK | "a NOTE ROW - the relay list, nothing here is scheduled work" (2026-10-03); relays belong in pcrec-bench inbox_from_pcrec.md / wake.md, and half the items are overtaken (O-81..O-82 era) | delete; re-issue still-open asks through the inbox |
| 398 | [OPT-LITSCAN] | started | 17581 | STALE | 17.6 KB; planaudit 2026-10-10 prefix: S1 steps 1-5, step 6, S4 C0/C1/C3, K82 (A)(C)(B) all MERGED, "pending merge" below is historical; remainder = C2 held on its D77 witness | archive delivered stages; keep a short row for C2 + the witness requirement |
| 400 | [K88-HANDOFF-DENSE] | not-started | 542 | LIVE | filed 2026-10-05 (K88); D77 trigger = back-to-back-match literal bench cell | keep |
| 401 | [PRIOR-COST-UNIFY] | blocked | 2453 | LIVE | blocked/paused by D161 pending re-scope; legitimate STATE:blocked | keep; move "SHARED VOCABULARY" prose to its design note |
| 402 | [KIT-VERIFY] | not-started | 1629 | LIVE | filed 2026-10-12, not scheduled | keep |
| 403 | [ADAPTIVE-ARM] | not-started | 1025 | LIVE | filed 2026-10-11, not scheduled | keep |
| 404 | [SIZE-KNEE] | not-started | 915 | LIVE | filed 2026-10-11, not scheduled | keep |
| 405 | [REQ-HANDOFF-L1] | completed | 5433 | COMPLETED | STATE:completed in this file; MERGED 7b1f60fa 2026-10-11 (abi 74 -> 75) | archive; K105 stays in known_issues |
| 406 | [NULLABLE-ANCH] | started | 1585 | STALE | planaudit 2026-10-10: BUILD LANDED (02db3811, abi 68); "awaiting merge" text historical; remains K97 (long-match tax) + F1 (sits with DEC-FALLBACK, which is done) | archive build; file remainder as K97 pointer |
| 407 | [CAP-EARLY-STOP] | not-started | 1507 | LIVE | filed 2026-10-09 FOR EVALUATION | keep |
| 408 | [SL-COMPILE-TIME] | not-started | 826 | LIVE | boonies, filed 2026-10-11 | keep |
| 409 | [FINDALL-REENTRY] | not-started | 422 | LIVE | boonies, filed 2026-10-09 | keep |
| 410 | [U8-PICK] | started | 1776 | LIVE | started; step 0 done (u8pick0), D160 ruled authored prior; build pending | keep |
| 411 | [OPT-VMSEED] | not-started | 3048 | STALE | row flips between "not-started" and "the VM hat landed" (ssbuild2 57db5152); whether the VM hat discharged it is left as "a manager call" since 2026-10-10 | decide: close as delivered by START-SET stage 2, or restate the unbuilt remainder |
| 412 | [EDGE-STAMP] | not-started | 980 | LIVE | chartered 2026-09-20; `<PREFIX>_SCAN_EDGES` count stamp not emitted (only RX_DFA_SCAN_EDGE form exists) | keep |
| 413 | [FINDINGS] | completed | 113 | JUNK | archive stub that still carries `STATE:completed` (counts as a completed row); FINDINGS completed 2026-09-30 | delete (fix the stub shape) |
| 414 | [FINDINGS.B4] | not-started | 372 | LIVE | HELD per Frank 2026-09-28 option (c) | keep |
| 415 | [FIND-DOMAIN-CHECK] | not-started | 4090 | LIVE | filed 2026-09-29 (D131 item 7) | keep |
| 417 | [FIND-UTF8-DEFAULT] | not-started | 482 | LIVE | filed 2026-09-28; gate half met ([FIND-TIE] landed 72e3ae41) but the corpus half ([UTF-RW]) is not | keep |
| 418 | [FIND-MIX] | not-started | 1091 | LIVE | filed 2026-09-28 | keep |
| 419 | [FINDINGS-S1-REVISIT] | not-started | 672 | LIVE | boonies 2026-09-25 | keep |
| 420 | [FINDINGS-SELINC] | not-started | 774 | LIVE | boonies 2026-09-25 | keep |
| 421 | [ENG-TACTICS] | started | 6961 | LIVE | started: window-needle generalization filed 2026-10-12 (parked with rev-inner); a duplicate index copy exists at :380 | keep; trim |
| 422 | [UCP] | started | 7894 | LIVE | started; U3 chartered as capability route (D134), queued behind UTF-VALID which is now built (uvbuild 2026-09-30) | keep; update "queued behind [UTF-VALID]" |
| 423 | [VAR] | started | 8743 | LIVE | started; MVP pattern half merged (varmvp, abi 32); head is 8.7 KB; M9 replace half pending | keep; trim; absorb [FEAT-VAR] |
| 424 | [K50-DD12AI-MANIFEST] | not-started | 6148 | LIVE | 2026-09-30 "EXPLAINED MOSTLY" by silentred; manifest re-harvest still owed (K50-HARVEST says the manifest drifted again 2026-10-10) | keep; merge [K50-HARVEST] into it |
| 425 | [V-A] | not-started | 511 | LIVE | boonies 2026-08-12 | keep |
| 426 | [V-B] | not-started | 212 | LIVE | boonies | keep |
| 427 | [V-C] | not-started | 151 | LIVE | boonies | keep |
| 428 | [V-D] | not-started | 704 | LIVE | boonies 2026-08-19 | keep |
| 429 | [LIB] | not-started | 2245 | STALE | says "BLOCKS on [DD-13b]" (ruled 2026-08-28); [DD-13b] is STATE:completed (plan_completed.md:4816, merged daa6b6c 2026-08-29; the W23 implementation waves finished 2026-09-15) so the stated blocker is gone and nobody re-asked the spine question | ask Frank: unblock/schedule or leave boonies; update text |
| 430 | [CAP-STAMP-BYTES] | not-started | 981 | LIVE | filed 2026-10-09 FOR EVALUATION (belongs to the [IFACE-PUSH] stamp family) | keep |
| 431 | [FINDALL-NEXT] | not-started | 4677 | LIVE | 2026-10-11 unifying shape; part of the IFACE-PUSH/find-all family | keep |
| 432 | [STAMP-REVIEW] | not-started | 2092 | LIVE | filed 2026-10-09 FOR EVALUATION | keep |
| 433 | [EFFORT-BUDGET] | not-started | 2494 | LIVE | filed 2026-10-09; shares vocabulary with [PRIOR-COST-UNIFY], which is paused | keep |
| 434 | [RXINFO-REMODEL] | not-started | 2123 | LIVE | filed 2026-10-09 FOR EVALUATION | keep |
| 435 | [V-E] | not-started | 4386 | LIVE | recorded design input (D88); cross-artifact sharing half overlaps [XART-TABLES] | keep; cross-link |
| 436 | [ART-MGR] | not-started | 7180 | LIVE | design-only direction document, 7 KB, 2026-09-30 | keep; move body to docs/design/artifact_manager.md (it already exists) |
| 495 | [V-F] | not-started | 837 | LIVE | boonies 2026-08-12 | keep |
| 507 | [V-G] | not-started | 1126 | LIVE | boonies 2026-08-13 | keep |
| 523 | [V-H] | not-started | 1683 | STALE | still says [DD-8] "already owes --emit-ir / --emit-dot": --emit-ir shipped (DD-8 closed 2026-09-28, D106), --trace shipped (M4.5c); only the verbose-compile mode, trace enrichment and --emit-dot ([EMIT-DOT]) remain | update text |
| 549 | [SAFEKILL] | (none) | 290 | JUNK | archive stub; SAFEKILL completed 2026-08-19 | delete |
| 550 | [EMIT-SET] | not-started | 2230 | DUPLICATE | overlaps [EMIT-ENTRIES] (see :277); broader (units incl. value-add) | merge with [EMIT-ENTRIES] |
| 551 | [BENCH-UTF8] | started | 1539 | STALE | planaudit 2026-10-10: the utf8 subbench is BUILT and RUNNING; remainder = growth families (g)-(k) "not verifiable from this repo" | archive the build part; ask the bench dev for the (g)-(k) status or drop |
| 552 | [OPT-HYB-RESEED-XCALL] | not-started | 2427 | LIVE | HELD: xcalldes found XCALL reaches 1 of 14 cells; [OPT-HYB-RESEED-FORM] took the work; a duplicate index copy at :359 | keep |
| 553 | [OPT-ENDWIN-ENC] | not-started | 328 | LIVE | FILED+HELD 2026-09-27, noise-scale; duplicate index copy at :361 | keep |
| 554 | [SIZE-CMT-CLASS] | not-started | 906 | LIVE | filed 2026-09-27 | keep |
| 555 | [AXES-DENY-MASK] | done | 2219 | COMPLETED | STATE:done (not an allowed state); DONE 2026-10-06 by K92 (abi 65), closed 2026-10-07 | archive |
| 556 | [PAT-LINT] | not-started | 2060 | LIVE | parked, no queue position (2026-08-25) | keep |
| 585 | [V-I] | not-started | 1198 | LIVE | boonies 2026-08-18 | keep |
| 603 | [OPT-SETS] | not-started | 2011 | STALE | planaudit 2026-10-10 prefix: planning step done (option_sets.md merged a2b9d831), "Consider STATE:not-started (nothing active)"; the row text above and below disagree about being open | retag and trim; keep as a pointer to option_sets.md |
| 604 | [MEMFN] | started | 9384 | STALE | 9.4 KB, newest-first dated status paragraphs; the TAIL still says "NEXT: M7 (N7), M6 (N6 + VMSTRIDE), then R4j/M5" although M7 and M6 merged 2026-10-08/09 (the head says so); and [SIMD-SIZE-PARITY] was inserted between this row and its child | rewrite as charter + one status line; move history to memfn/docs/journal.md |
| 605 | [SIMD-SIZE-PARITY] | not-started | 1076 | LIVE | filed 2026-10-12, not scheduled; but physically wedged between [MEMFN] and its child [MEMFN-ROWCON] | keep; move below [MEMFN] children |
| 606 | [MEMFN-ROWCON] | started | 4386 | LIVE | started: N3/N4 built (n3_report, n4_report); rev 4 narrowed gate; remains the pcrec-side R-6 requests | keep; verify whether anything is still open |
| 607 | [SIMD-META] | not-started | 3395 | LIVE | meta-plan for studies/simd1 (2026-08-16); duplicate index copy at :373 | keep or merge into [OPT-SIMD] |
| 661 | [ENG-THIN] | not-started | 2177 | LIVE | parked [OPTLOOP] candidate (D137); full row, an index copy exists in the candidates block | keep |
| 694 | [ENG-PGO] | not-started | 6274 | LIVE | parked [OPTLOOP] candidate (D137); full row, an index copy exists in the candidates block | keep |
| 737 | [ENG-DIRECT] | not-started | 4652 | LIVE | parked [OPTLOOP] candidate (D137); full row, an index copy exists in the candidates block | keep |
| 793 | [ENG-TDFA] | not-started | 1390 | LIVE | filed 2026-10-09, "a BIG FISH", unscheduled | keep |
| 794 | [ENG-COUNT] | not-started | 2141 | LIVE | parked [OPTLOOP] candidate (D137); full row, an index copy exists in the candidates block | keep |
| 795 | [ENG-CLAMP] | not-started | 1566 | LIVE | parked [OPTLOOP] candidate (D137); full row, an index copy exists in the candidates block | keep |
| 816 | [ENG-LOOK] | not-started | 4037 | LIVE | parked [OPTLOOP] candidate (D137); full row, an index copy exists in the candidates block | keep |
| 859 | [ENG-CUT] | not-started | 2333 | LIVE | parked [OPTLOOP] candidate (D137); full row, an index copy exists in the candidates block | keep |
| 860 | [M4-CALLOUTS] | not-started | 257 | STALE | trigger "step 2 awaits M4" is met (M4 shipped 2026-08-18; backlog_triage 09-22 flagged it); AND the row is physically split in two: [MATCH-EVENTS] was inserted at :861 in the middle of its body (:862-896) | repair the split; restate trigger; ask Frank if still wanted |
| 861 | [MATCH-EVENTS] | not-started | 3840 | LIVE | filed 2026-10-12, not scheduled; wedged inside [M4-CALLOUTS] | keep; move out |
| 897 | [M4-SUBST] | not-started | 3357 | STALE | trigger "need not wait on M4" - M4 shipped; D38 design of record is docs/design/replace_design.md (variables design set, 09-23) which now names this row as its implementation target; "xmas item" text is a 2026-08-12 note | restate against replace_design.md / [VAR] M9; ask Frank if still wanted |
| 956 | [DD-2] | not-started | 688 | COMPLETED | VM step/frame budgets shipped: PCREC_ERR_STEPS/_FRAMES (match_api.md (old line cites 219 and 387)), D42.6/D45; row says "(with M4 design)" and M4 shipped | archive |
| 957 | [DD-9] | (none) | 734 | JUNK | archive stub; DD-9 decided 2026-08-14 | delete |
| 958 | [EMIT-DOT] | not-started | 755 | LIVE | filed 2026-09-28 (residual of DD-8) | keep |
| 959 | [DD-13] | completed | 213 | JUNK | archive stub with FIVE ids in one line ("[DD-13] and its completed children [DD-13a], [DD-13b.W1], ...") and `STATE:completed` (counts as a completed row); also wedges the two live children below it | delete; keep the two children under a [DD-13] heading or as top-level rows |
| 960 | [DD-13b.W1.3.1] | not-started | 988 | LIVE | refiled 2026-09-30; Frank ruling option 1, after PFX-1 step 0 (pfx0 done) | keep |
| 961 | [DD-13b.W1.4] | not-started | 1009 | LIVE | refiled 2026-09-30; format_design wave table remainder | keep |
| 962 | [DD-6] | not-started | 127 | COMPLETED | multiline ^/$ as DFA state context shipped in module assertions ([M6.2] waves; tests/codegen/run_mlinectx_identity.sh, run_endvar_identity.sh); backlog_triage 09-22 flagged "M6 shipped, unconfirmed" | archive (confirm with Frank) |
| 963 | [DD-11] | completed | 106 | JUNK | archive stub carrying `STATE:completed` (DD-11 completed 2026-09-30) | delete (fix the stub shape) |
| 964 | [DD-11.5] | not-started | 1187 | LIVE | re-chartered 2026-09-28 (admin88) | keep |
| 981 | [DD-14] | (none) | 483 | JUNK | archive stub; DD-14 completed 2026-08-25 | delete |
| 982 | [DD-3] | not-started | 112 | LIVE | R1 item "before M3"; abi policy is D76/D94 but no vendored-consumer compat statement exists; same family as the [IFACE-PUSH] umbrella | keep; link under [IFACE-PUSH] |
| 983 | [PLAN-LINT] | not-started | 1049 | LIVE | this audit's parent row (filed 2026-10-12); sits in "Design-debt ledger" section | keep; move to an Admin section |
| 984 | [VM-READABLE] | not-started | 1404 | LIVE | boonies, filed 2026-10-12; misfiled in "Design-debt ledger" | keep; merge with [READ-BYTES] |
| 985 | [FREESTANDING] | not-started | 2657 | LIVE | boonies 2026-08-28; misfiled in "Design-debt ledger" | keep |
| 986 | [DD-5] | not-started | 86 | LIVE | R1 item, title-only; overlaps [FREESTANDING] (backlog_triage pairs them) | keep; fold into [FREESTANDING] |
| 987 | [DD-10] | not-started | 512 | LIVE | R3 critic item; companion check is [TS-4] | keep; merge with [TS-4] |
| 1000 | [OS-0] | not-started | 1034 | LIVE | D20 optional module, no customer | keep |
| 1001 | [OS-2] | not-started | 451 | COMPLETED | M5 landed; encoding is a lowering pass before the emitters (`pcrec_lower_enc`, src/opt/lower_enc.c) with one DFA emitter shape - the row's predicted "folds" outcome; no separate measurement record found (backlog_triage 09-22 §OS-2 "measurement now due") | close as answered by M5 architecture, or run the one-hour desk check first |
| 1002 | [OS-3] | not-started | 304 | DUPLICATE | "Feeds M3.0's design gate; do not write streaming code before it is settled" - pure input to [M3.0] | merge into [M3.0] |
| 1003 | [OS-4] | not-started | 1969 | SUPERSEDED | the measurement it asks for was done by cycle 1 (cycle1_analysis.md M5, ATTEMPT population) and the construction choice moved into [MATCH-SPLIT]/[OPT-ATTEMPT-SPLIT]/[ENG-ABS-CARET] | merge into [MATCH-SPLIT] |
| 1019 | [SR-5] | not-started | 1002 | LIVE | title-only (R6 rewrite note); guard of the measured fast-path property | keep |
| 1032 | [SR-6] | not-started | 999 | STALE | "not a step to schedule - a rule to follow when a module is implemented"; the modules landed (src/parse/mod_*.c x11) so the rule was followed; text still says "no verb produces yet" | convert to a src/parse/CLAUDE.md convention; delete the row |
| 1046 | [SR-7] | deferred | 902 | LIVE | deferred by D18 earn-its-axis; one flavour-varying row known | keep |
| 1058 | [SR-8] | deferred | 1627 | STALE | "Blocked on M4 having a second engine": M4 shipped; D55 (2026-08-17) decided the consultation lands with the first VM_ONLY producer, `\K` (M6.2 wave E) was that producer and the tripwire fired and got a named exception (select_engine.c:31-47); row text still describes a future | close as superseded by D55/D59 or rewrite the trigger |
| 1081 | [SR-10] | not-started | 1573 | LIVE | 2026-08-12/08-23; namespace tables | keep |
| 1098 | [DOC-BM] | deferred | 4046 | STALE | contains a struck-through (~~...~~) fragment of dead history ("was STATE:blocked; RESOLVED by D32", planaudit 2026-10-10) inside a live deferred row; its constraint ("must exist before section 7.1's five escape rows land") is unverified | strip the struck-through history; verify the constraint |
| 1163 | [BENCH-CEIL] | not-started | 2763 | LIVE | boonies, Frank 2026-08-18 | keep |
| 1204 | [OPT-A] | not-started | 6358 | LIVE | parked candidate; duplicate index copy at :365 | keep |
| 1205 | [OPT-NEG] | not-started | 1672 | LIVE | parked candidate; index copy :367 | keep |
| 1206 | [FEAT-VAR] | not-started | 1667 | SUPERSEDED | [VAR] (chartered 2026-09-23) answered its four design questions (variables_roadmap.md:348: (b)(c) answered, (d) a signature change, (a) deferred to phase 5) and built the pattern half (varmvp, abi 32) | merge into [VAR]; keep "(a) DFA string-edge variant deferred" as a line there |
| 1207 | [OPT-ALTHASH] | not-started | 2118 | LIVE | parked candidate; index copy :368 | keep |
| 1208 | [PFX-1] | not-started | 3068 | LIVE | filed 2026-09-04 (D96); step 0 done (pfx0_report.md), step 1 needs its own design | keep |
| 1209 | [OPT-VMLIT] | not-started | 4694 | STALE | full row says "TRIGGER PARTIALLY MEASURED"; the index copy (:363) and litrun_report.md say "largely DELIVERED as [OPT-LITSCAN] S2a (exact run = one P4 compare, abi 41)" and recommend staying not-started; the two copies disagree | reconcile (close as delivered by S2a with the ctx/level-context bench run named as the open gate) |
| 1210 | [OPT-SIMD] | started | 6312 | LIVE | started (kit SIMD layer only); full row is the OLDER copy (misses RQ-2/RQ-3 merges that :369 records) | keep one copy |
| 1235 | [OPT-B] | not-started | 660 | LIVE | parked candidate | keep |
| 1236 | [OPT-C] | not-started | 278 | LIVE | parked candidate | keep |
| 1237 | [OPT-D] | not-started | 1894 | LIVE | parked candidate | keep |
| 1238 | [XART-TABLES] | not-started | 1560 | LIVE | parked candidate; overlaps V-E R-VE-3 | keep |
| 1239 | [UCD-RECORD] | not-started | 1750 | LIVE | filed 2026-09-28 | keep |
| 1240 | [ART-POSS-ARMS] | (none) | 230 | JUNK | archive stub; ART-POSS-ARMS completed 2026-10-10 (c9672bd2) | delete |
| 1241 | [ART-VMCTX-START] | not-started | 710 | LIVE | filed 2026-10-06/07 under [OPTLOOP] candidates, unscheduled, D77 trigger stated | keep |
| 1242 | [ART-TRAIL-ELIDE] | not-started | 950 | LIVE | filed 2026-10-06/07 under [OPTLOOP] candidates, unscheduled, D77 trigger stated | keep |
| 1243 | [POSS-CALL-COPY] | not-started | 1341 | LIVE | filed 2026-10-06/07 under [OPTLOOP] candidates, unscheduled, D77 trigger stated | keep |
| 1244 | [POSS-CTX-TABLE] | not-started | 1674 | LIVE | filed 2026-10-06/07 under [OPTLOOP] candidates, unscheduled, D77 trigger stated | keep |
| 1245 | [ART-CTX-TRIO] | ~row | 439 | LIVE | HOLD row with no STATE tag (2026-10-06): three artrev leads parked behind START-SET stage 3 (now landed) and a bench weight | keep; give it STATE:not-started; first gate (START-SET stage 3) is met, the bench-weight gate is open |
| 1255 | [TS-4] | not-started | 454 | DUPLICATE | "DD-10 is a thread-safety item" - the companion check of [DD-10] | merge into [DD-10] |
| 1265 | [SR-11] | (none) | 192 | JUNK | archive stub; SR-11 completed 2026-08-22 | delete |
| 1266 | [TT-3] | (none) | 194 | JUNK | archive stub; TT-3 completed 2026-08-22 | delete |
| 1267 | [MECH-3] | not-started | 519 | SUPERSEDED | "schedule before OPT-A opens": the OPT waves opened (D119/D144) with the bench (D78) and D144 add. 1 as the measurement vehicle; `scripts/measure.sh` (D35) and `scripts/perfrun` exist | ask Frank: close as superseded |
| 1271 | [DOC-DRV] | (none) | 243 | JUNK | archive stub; DOC-DRV completed 2026-08-22 | delete |
| 1272 | [PC-2] | not-started | 74 | LIVE | recurring maintenance (compliance-refresh skill); continuation lines are indented under a one-line head | keep (as recurring) |
| 1273 | [PCRE2-UP] | not-started | 976 | LIVE | "NOT started, no measured need yet" (2026-08-30) | keep |
| 1279 | [CLS-FOLD-WAF744] | not-started | 1032 | LIVE | boonies 2026-09-30 | keep; merge with [FORM-CHAR2] |
| 1281 | [EMIT-ALIGN] | not-started | 2416 | LIVE | boonies; text says NOT TRIGGERED (bench O-69: governor, not layout); duplicate index copy :379 | keep or close as not triggered |
| 1283 | [ENC-MODEL] | not-started | 2175 | LIVE | boonies, Frank 2026-09-06/08, unscheduled | keep |
| 1284 | [FOLD-BASE] | not-started | 2938 | LIVE | boonies, Frank 2026-09-06/08, unscheduled | keep |
| 1285 | [MULTI-PAT] | not-started | 2532 | LIVE | boonies, Frank 2026-09-06/08, unscheduled | keep |
| 1287 | [JSONL] | not-started | 1913 | LIVE | boonies, Frank 2026-09-06/08, unscheduled | keep |
| 1288 | [WORD-FOLD] | not-started | 4191 | STALE | folded into [OPT-LITSCAN] S4: C0/C1/C3 (cube, run compare, caseless necessary run) are built and merged; only C2 (VM masked run) is held; the row still reads as an open investigation | close as delivered by S4 (C2 held under [OPT-LITSCAN]) |
| 1289 | [SPAN-ISEL] | not-started | 3695 | LIVE | filed 2026-10-10/11, unscheduled, thought-before-proceeding | keep |
| 1290 | [BITSTREAM-GPU] | not-started | 755 | LIVE | filed 2026-10-10/11, unscheduled, thought-before-proceeding | keep |
| 1291 | [PIC-ARM] | not-started | 803 | LIVE | filed 2026-10-10/11, unscheduled, thought-before-proceeding | keep |
| 1292 | [SPELLING-INV] | not-started | 1444 | LIVE | filed 2026-10-10/11, unscheduled, thought-before-proceeding | keep |
| 1293 | [POS-PARALLEL] | not-started | 2239 | LIVE | filed 2026-10-10/11, unscheduled, thought-before-proceeding | keep |
| 1294 | [VM-CLSMASK] | not-started | 2603 | LIVE | filed 2026-10-10/11, unscheduled, thought-before-proceeding | keep |
| 1296 | [CLS-TREE] | completed | 13276 | COMPLETED | STATE:completed in this file (13.3 KB); CLOSED 2026-10-03, S2 Linux-confirmed | archive |
| 1301 | [TEST-DISPATCH-SIG] | not-started | 1366 | LIVE | filed 2026-09-26/28, harness column, size S | keep |
| 1302 | [RUNSH-BUNDLE-DECL] | not-started | 1795 | LIVE | filed 2026-09-26/28, harness column, size S | keep |
| 1303 | [TIE-ALIGN] | not-started | 2472 | LIVE | filed 2026-09-29; duplicate index copy :362 | keep |
| 1304 | [CTX-PREFILTER] | not-started | 3016 | LIVE | step 0 delivered 2026-09-29, joint measurement found no D77 trigger; index copy :360 | keep |
| 1305 | [LIST-CLASSES] | not-started | 2118 | LIVE | filed 2026-09-28 | keep |
| 1306 | [LIST-TABLES] | not-started | 1849 | LIVE | filed 2026-09-28 | keep |
| 1307 | [SIZE-CAP-FLAG] | done | 1012 | COMPLETED | STATE:done (not an allowed state); MERGED 5761cd03 2026-10-09 | archive |
| 1313 | [DEC-VAR-ATTRIB] | done | 951 | COMPLETED | STATE:done (not an allowed state); MERGED 32a1c91f 2026-10-09 with abi 69 | archive |
| 1318 | [DEC-FALLBACK] | done | 14344 | COMPLETED | STATE:done (not an allowed state), 14.3 KB; B7 MERGED 2026-10-09 (09ce1b36) | archive |
| 1319 | [DEC-COLLAPSE-WASTE] | done | 2595 | COMPLETED | STATE:done (not an allowed state); MERGED 32a1c91f | archive |
| 1320 | [DEC-RUNG] | not-started | 376 | LIVE | filed 2026-10-06 (decsurvey), unscheduled, D77 trigger stated | keep |
| 1321 | [DEC-KINDATTR] | not-started | 484 | LIVE | filed 2026-10-06 (decsurvey), unscheduled, D77 trigger stated | keep |
| 1322 | [DEC-LIMITS] | not-started | 263 | LIVE | filed 2026-10-06 (decsurvey), unscheduled, D77 trigger stated | keep |
| 1323 | [START-TABLE] | done | 7845 | COMPLETED | STATE:done (not an allowed state), 7.8 KB; C6+C7 MERGED 2026-10-08 cf3ffaac | archive |
| 1324 | [START-DENSE] | not-started | 905 | LIVE | gated on START-TABLE C7, which is now merged (cf3ffaac) so the gate is open; absorbs OPT-HYB-RESEED-POLICY | keep; update gate |
| 1325 | [OPT-ENDTERM] | not-started | 1371 | LIVE | filed 2026-10-06, D153; unscheduled, D77 (cross-refs K81 and the archived [OPT-VEDGE]) | keep |
| 1326 | [DEC-ROUTE] | not-started | 1096 | SUPERSEDED | "ABSORBED by the start table's route column ... Kept only as the pointer; no separate lane"; start table complete (START-TABLE done) | delete |
| 1327 | [START-D1] | not-started | 532 | LIVE | filed 2026-10-06; gated on measuring the 33 artifacts | keep |
| 1328 | [START-D2] | not-started | 416 | COMPLETED | `DFA_START "attempt-start"` shipped with L2.1 of [OPT-REVEND] (revbuild_report.md, 4863fc96; match_api.md (old line cite 1764) shows the value; 638 movers) | archive |
| 1329 | [START-D2B] | not-started | 310 | LIVE | "RULED: FILE, don't fix" 2026-10-06 | keep |
| 1330 | [DEC-POSDOM] | not-started | 1122 | LIVE | filed 2026-10-06 | keep |
| 1331 | [EST-REGISTRY] | not-started | 481 | LIVE | chartered unscheduled 2026-09-30 (D141) | keep |
| 1332 | [MECH-SAN-ARM] | not-started | 2038 | LIVE | filed 2026-09-26, checks column | keep |
| 1333 | [TEST-METRICS] | not-started | 2835 | LIVE | filed 2026-09-26, harness column; [TT-JTUNE] ledger is the partial answer | keep; link to TT-JTUNE ledger |
| 1334 | [TEST-REENTRANT] | not-started | 1887 | LIVE | filed 2026-09-26 | keep |
| 1338 | [FEAT-GLOBAL-RETIRE] | (none) | 560 | LIVE | 2026-09-21 [REL-1.11] follow-up; lives in the "Small-debt shelf" as a bullet with no STATE and no title separator | keep; promote to a real row |

Template pseudo-row :14 (`- [Mx.y] STATE:<state> — <title>`) is the format example inside the "Step-state format" section; any parser must skip it (it sits in an indented code block).

## 5. Free-text blocks and headings (everything that is not a row)

| lines | block | class | evidence | action |
|---|---|---|---|---|
| 1-3 | Title + intro | LIVE | two lines; fine | keep |
| 5-8 | CLOSE-OUT SEQUENCE IN FORCE banner (D125) | STALE | D144 (decisions.md:8937, 2026-10-03) "Lifts D125's hold on opening the next [OPTLOOP] cycle"; phases 1-3 done (ph3_reassessment_2026-09-28.md); the banner still reads as the governing rule | delete (or one line "current focus: see wake.md") |
| 10-31 | Step-state format + grep recipes | STALE | lists 5 states but the file uses 8 spellings (done, colon-less `STATE x`, COMPLETED, ARCHIVED, HOLD ...); says "81 on 2026-09-22" for a count that is now ~190; says "keeps zero STATE:completed rows" and holds 11 (14 lines) | rewrite as the canonical format (below); generate counts, never hard-code them |
| 33-43 | Queue discipline (Frank, 2026-08-12) | STALE | BOONIES-TIER rule is still valid; the "spine order re-ruled 2026-08-13: STD1 -> M4 -> M5 -> M6 -> M3 -> M7" list is history (STD1/M4/M5/M6 done); names [M4-CALLOUTS],[M4-SUBST],[V-E],[V-F],[SR-10] as the boonies examples | keep the rule in one sentence; drop the spine list |
| 45-53 | Lane structure (D86) | JUNK | process policy, not plan state; owned by D86 (decisions.md), root CLAUDE.md and the pcrec-manager skill; its last sentence "Rows still open on Frank's word" is the only plan content | delete |
| 55-85 | Development order (ratified 2026-08-13) | STALE | spine list is history: STD1, M4, M5, M6 are complete; remaining spine = M3 then M7; the sequencing notes ("[BENCH-1] builds the benchmark ... then the OPT waves open, [MECH-3] first") are overtaken: [BENCH-1] closed 2026-09-22 (folded into D119), OPT waves run as [OPTLOOP] | delete; keep one line "remaining spine: M3 streaming, then M7" |
| 87-105 | "Next: M4 (milestones start with Frank)" | JUNK | says "NEXT: [M4.4] - implementation is open" as of 2026-08-14; M4 completed 2026-08-18; whole block is a dated hand-off note | delete |
| 107-114 | M4 section heading + "Expanded 2026-08-14" intro | JUNK | M4 completed; the section now holds only 6 archive stubs | delete with the stubs |
| 181-182 | "Design notes moved here from [MOD-0.1]'s archived entry" | JUNK | lead-in to the two notes below | delete |
| 184-200 | DESIGN NOTE for `backrefs` (Frank, 2026-08-12) | JUNK | design prose, not a row; captured by docs/design/backrefs_design.md (module shipped M6.5, 2026-08-22) | delete (design doc holds it) |
| 202-219 | SAME-SESSION COMPANION NOTE for atomic-groups/possessives | JUNK | design prose; captured by docs/design/atomic_groups_design.md (module shipped M6.4, 2026-08-22) and REFERENCES.md [Ber13+] | delete |
| 221 | Heading "M5 - UTF-8" | STALE | M5 completed 2026-09-12; the section is a junk drawer: UTF-PAT/UTF-RW/UTF-EXTENT plus XARCH, FORM-CHAR2, SEL-SIZE, SEL-COST, READ-BYTES, and 3 stubs | dissolve; re-home rows by class |
| 236, 248-254 | Heading "M6" + "(2026-08-13: classes+ and modifiers halves already landed...)" paragraph | JUNK | M6 completed 2026-08-25 (D79); 10 stubs + a history paragraph | delete |
| 257, 262-264 | Heading "M3" + "(2026-08-13: moved after M6...)" note | JUNK | the note restates the deleted Development-order list | delete the note; keep M3.0/M3.1 rows |
| 270-275 | Heading "Unscheduled rows (Frank, 2026-09-21, seventy-fifth session)" + "Chartered by Frank..." line | STALE | section name is a session label; its first row is [REL-0.2] (completed) and the TT-*/SPEC-*/IFACE rows that follow are not "chartered by Frank, no trigger" in the same sense | rename section "Backlog (unscheduled)" |
| 281-286 | Heading "Beyond M7 - long-term vision (Frank, 2026-08-09)" + intro | STALE | intro says "Direction, not scheduled work ... each becomes a milestone only after the current ladder is complete" but the section holds 135 rows (51% of all rows) including [OPTLOOP] and every started row except a handful; the name is wrong for its content | dissolve into Active / Candidates / Backlog / Boonies sections |
| 288-312 | POSITIONING NOTE (Frank + manager, 2026-08-13) | JUNK | marketing/positioning paragraph (25 lines), not a row; mentions [BENCH-1] prioritizer (closed); README.md and decisions.md (memory: "fastest COMPLETE pcre") carry positioning | move to APPROACH.md or delete |
| 344 | Bullet "Candidates for the next cycle (D137, ...)" | JUNK | id-less bullet that is really the lead-in sentence of a section | make it the section intro line |
| 345 | Bullet "REFILED FROM THE CLOSED PARKED ROWS (real rows, STATE-tagged)" | JUNK | id-less sub-label | delete |
| 356 | Bullet "MOVED IN PLACE (index only; each row keeps its text...)" | JUNK | admits "STATE x here is a pointer, not a row tag": the 26-entry duplicate index block (:357-387) | delete the block (generate an index if wanted) |
| 658-659 | Lead-in "M4-hosted, boonies-queued (Frank's queue discipline places these after the spine, not before):" | JUNK | orphan lead-in above [ENG-THIN]..[ENG-CUT]; they are now [OPTLOOP] candidates | delete |
| 945-952 | Heading "The 2026-09-17 code-review refactor ..." + Authority paragraph | JUNK | section has NO rows: every [REVW.*] row is archived (plan_completed.md:3914+); "guided tour happens AFTER all refactoring" is the only open thought and has no row | delete; if the tour is wanted file [CODE-REVIEW-TOUR] |
| 954 | Heading "Design-debt ledger (from R1; resolve before the milestone that hits each)" | STALE | R1 debt framing is 2026-08-09; of its 16 rows, 3 are completed/stubs (DD-9,DD-13,DD-11,DD-14) and 4 are unrelated new rows (PLAN-LINT, VM-READABLE, FREESTANDING, EMIT-DOT) | dissolve; re-home rows |
| 989-998 | Heading + intro "Option-specialization dimensions (D18)" | LIVE | policy statement that gates OS-0..OS-4; 4 rows, one decided, one duplicate, one superseded | keep trimmed to 2 sentences, or fold into [OS-0] |
| 1005-1017 | Heading + intro "Parser structure ... THE AGREED ORDER (R6) is COMPLETE" | STALE | the intro says "Work these in sequence. Each is a checkpoint..." about an arc that "is COMPLETE"; remaining rows are SR-5..SR-10/DOC-BM, none sequenced | delete the intro; keep rows |
| 1153-1162 | Heading "Optimization waves (D21)" + Frank quote | JUNK | D21 wave order was replaced by D119 [OPTLOOP]; section is a heading over 19 rows that are all "(under [OPTLOOP] candidates per D137)"; the Frank quote about the test suite is a motto, not a plan item | delete; rows move to the Candidates section |
| 1247-1253 | Heading "Thread-safety (D19)" + audit paragraph (2026-08-09) | LIVE | one row (TS-4) under a 7-line audit note; audit date 2026-08-09, not re-checked | keep trimmed; merge TS-4 into DD-10 |
| 1257-1263 | Heading "Process mechanization (session 2026-08-09)" + paragraph | JUNK | a retrospective paragraph over one row ([MECH-3]); "four consecutive checkpoints" is a 2026-08-09 anecdote | delete; keep [MECH-3] (or close it) |
| 1269 | Heading "PCRE2 compliance tracking" | LIVE | heading over PC-2 and PCRE2-UP; PC-2 continuation lines are at indent 2 under a one-line head | keep |
| 1277 | Heading "Far-future concepts (the boonies - unscheduled, no milestone)" | LIVE | 39 rows, but includes the 13 KB completed [CLS-TREE] and active-looking candidates (SPAN-ISEL, POS-PARALLEL); name is fine, membership is not | keep; rows re-sorted |
| 1298 | Paragraph "**RE-CHARTERED (Frank AGREED 2026-09-28, admin88 ...) ... NEXT CONCRETE STEP: the design note**" | STALE | orphan paragraph after the completed [CLS-TREE] row (:1296): says the next step is a design note and a light panel; [CLS-TREE] was built and CLOSED 2026-10-03 | delete (it is part of the CLS-TREE history) |
| 1336-1340 | Heading "Small-debt shelf" + [FEAT-GLOBAL-RETIRE] bullet + "Pointers, not queue positions" | JUNK | "pointers, not new rows" list; FEAT-GLOBAL-RETIRE is a row in disguise (no STATE) | dissolve (see items below) |
| 1342-1343 | Shelf bullet K9 (public API takes no pattern length) | DUPLICATE | K9 is OPEN in known_issues.md:2342; not a plan item | delete; known_issues owns it |
| 1344 | Shelf bullet TS-4 / DD-10 | DUPLICATE | both are rows ([TS-4] :1255, [DD-10] :987) | delete |
| 1345 | Shelf bullet "DD-8 - --emit-ir / --emit-dot, useful during M4 bring-up" | COMPLETED | [DD-8] CLOSED 2026-09-28 (plan_completed.md:4764); --emit-ir shipped, --emit-dot became [EMIT-DOT] | delete |
| 1346 | Shelf bullet SR-5 | DUPLICATE | row [SR-5] :1019 | delete |
| 1347 | Shelf bullet "MECH-3 - schedule before [OPT-A] opens" | DUPLICATE | row [MECH-3] :1267; the OPT waves opened long ago | delete |
| 1348 | Shelf bullet "module-swap / row-deletion guard - owed, unruled" | STALE | no row, no owner, no date; cannot tell whether it was built | file as a row with a date or delete |
| 1349-1350 | Shelf bullet "PC-4 missing shapes - caseless-negated, \N{n,m}, MODIFIER, zero-tail (?P" | STALE | PC-4 completed (62,872 cells); the missing-shapes list has no row | file as a row or delete |
| 1351-1352 | Shelf bullet "PC-2 - re-survey" | DUPLICATE | row [PC-2] :1272 | delete |


## 6. Format inconsistencies by kind (input to the linter)

All counts are from the 262 `[ID]` rows at `43f78acc1` unless stated; method in `build/` is not committed (scratch), commands are trivial greps/awk over the row spans.

| # | kind | count | examples |
|---|---|---:|---|
| F1 | **Header shape.** `STATE:x (status blob…) — title` | 155 | :223 UTF-PAT, :388 OPT-FIRSTSET |
| | `STATE:x — title` (the documented shape) | 32 | :259 M3.0, :983 PLAN-LINT |
| | archive stub (`COMPLETED …`, `archived to plan_completed.md`, `ARCHIVED →`) | 31 | :116 M4.1, :549 SAFEKILL, :981 DD-14 |
| | colon-less `STATE x —` (index-pointer rows) | 28 | :357 SEL-COST, :369 OPT-SIMD |
| | `STATE:x **bold blob**` | 10 | :229 SEL-SIZE, :272 REL-0.2, :340 OPTLOOP |
| | other (`- **[STD1]**` bold id; mixed) | 4 | :60 |
| | `HOLD` with no STATE / no STATE at all | 2 | :1245 ART-CTX-TRIO, :1338 FEAT-GLOBAL-RETIRE |
| F2 | **State spellings.** `STATE:not-started` 158, `STATE:started` 19, `STATE:completed` 11, `STATE:done` 7, `STATE:deferred` 4, `STATE:blocked` 1; colon-less `STATE not-started` 28 / `started` 1 / `completed` 1; prose-only states `COMPLETED`, `ARCHIVED`, `archived`, `HOLD`, `completed-pending-close`; states quoted in prose (`formerly STATE:not-started`) defeat the unanchored grep the header itself documents | 8+ spellings | see §3 |
| F3 | **Title buried.** The title (text after the status blob) starts beyond column 150 | 107 of 230 STATE rows (median col 310) | :227 XARCH (col 595), :272 REL-0.2 (455), :316 TT-15 (432) |
| | no em-dash separator in the head line | 5 | :413, :959, :963, :964 DD-11.5, :1319 |
| F4 | **Row size.** median 1,113 chars; >1 KB 146 rows; >2 KB 71; >5 KB 17; max 17,581 (OPT-LITSCAN). Lines >1,000 chars: 129; >5,000: 14; longest line 16,957 | | :398 OPT-LITSCAN 17.6 KB, :1296 CLS-TREE 13.3 KB (completed), :1318 DEC-FALLBACK 14.3 KB (done) |
| F5 | **Two physical layouts.** 224 single-line rows (any length) vs 38 hard-wrapped at ~72 columns with a 2-space continuation indent (the 2026-08 rows) | 38 wrapped | :495 V-F, :507 V-G, :523 V-H, :556 PAT-LINT, :661 ENG-THIN, :1019-1098 SR-* |
| F6 | **Status layering inside one row**, three conventions: newest-first prepend (:604 MEMFN, :390 COMPOUND, :341 LOSS-REVIEW), oldest-innermost nested parentheticals (:350 OPT-REVEND, paren depth 3), appended-last (:398 OPT-LITSCAN). Old `NEXT:` lines survive in the tail after the head says they happened (:604 "NEXT: M7 (N7), M6 …" vs head "M7, M6 MERGED"). Retro-fit `**2026-10-10 AUDIT (planaudit): …**` prefixes on 7 rows that say "the text below is historical" without removing it | 7 + 10 bold | :388, :398, :406, :411, :551, :603, :396 |
| F7 | **Multiple ids per line.** One stub row carries six ids and a STATE tag; a HOLD row bundles three candidate ids that have no rows; the template pseudo-row; and the 26-entry duplicate index block (26 ids appear on 52 rows) | 1 + 1 + 1 + 26 | :959 DD-13 (+DD-13a, DD-13b.W1, DD-13b.W1.3, DD-13b, DD-13b.panel), :1245, :14, :357-387 |
| F8 | **Duplicate ids.** 26 ids on two rows each; the copies already diverge (OPT-SIMD: :369 newer; SEL-COST/SEL-SIZE: :357/:358 older; OPT-VMLIT: :363 vs :1209 disagree on delivered) | 26 | §4 DUPLICATE rows |
| F9 | **Wedged rows.** A row inserted inside another row or between parent and child, so the text of one reads as part of the other | 3 | [M4-CALLOUTS] :860 body continues at :862-896 after [MATCH-EVENTS] :861; [SIMD-SIZE-PARITY] :605 between [MEMFN] :604 and its child [MEMFN-ROWCON] :606; stub [DD-13] :959 between its live children [DD-13b.W1.3.1]/[W1.4] and their archived parents |
| F10 | **Indentation / nesting.** indent 0: 197, 2: 27, 4: 38. Hierarchy is encoded three incompatible ways: indentation, dotted ids (22 ids; only 4 indented, 18 at indent 0 whose parents are archived), and prose (`under [OPTLOOP] candidates per D137`, 30 rows, instead of structure) | | :340-387 OPTLOOP subtree mixes indent 2 and 4; :960 `DD-13b.W1.3.1` indent 2 under a stub |
| F11 | **Rows without STATE.** 31 stubs + HOLD + the shelf bullet + 3 id-less bullets (:344, :345, :356) + 8 shelf bullets with no id | ~44 lines | :1338-1352 |
| F12 | **Sections do not match contents.** 135 of 262 rows (51%) in "Beyond M7 — long-term vision" including 19 of 20 started rows; "M5 — UTF-8" holds XARCH/SEL-COST/SEL-SIZE/READ-BYTES; "Design-debt ledger" holds PLAN-LINT/VM-READABLE/FREESTANDING; "Optimization waves (D21)" holds 19 rows all marked as OPTLOOP candidates; "Far-future (boonies)" holds the completed CLS-TREE; the "code-review refactor" section (:945) has no rows at all | | §5 |
| F13 | **Dates.** ISO dates mixed with session names in words ("fifty-fifth session", 52 rows) and numerals ("session 110", 39 rows), fuzzy times ("~09:2x"); 40 STATE rows contain no ISO date at all so cannot be aged | 40 undated | :259, :268, :357-387 |
| F14 | **Citations into the file.** 112 `plan.md:<line>` citations in 35+ files (reports, design docs); live ones rot silently, e.g. `docs/design/variables_pattern.md:15` cites `plan.md:1413` for [FEAT-VAR] (now :1206). 34 `[ID]` references in plan.md resolve to no row in plan.md or plan_completed.md (`[COMPOSITE]` renamed [COMPOUND], `[OPT-OFSK]`, `[M4.0]`, `[DD-11.6]`, `[DEC-STAMPS]`, `[OPTLOOP.N.impl]` …; bench `[B…]` and `K…` ids are legitimate externals) | 112 / 34 | |
| F15 | **Parallel status stores.** The same status lives in plan.md rows, dev_journal.md, wake.md, lane reports and decisions.md, so the row accretes a copy of each (the "planaudit" prefixes are the manager re-deriving a row's status from those). Nothing separates *charter* (stable, Frank's words) from *status* (volatile) | | F4, F6 |

## 7. Proposed canonical row format

Design goals: one grep recipe works; a row is readable in 5 lines; charter and status are separated; history has a home that is not the row; hierarchy is structural; the linter can be strict.

```
## <Section>                       # fixed list: Active, Candidates ([OPTLOOP]), Backlog, Boonies, Deferred, Policy

- [ID] STATE:<not-started|started|blocked|deferred> — <title, <= 100 chars, plain text>
  filed: 2026-10-12 by Frank (session 110)         # required, ISO date; who/where
  status (2026-10-12): <ONE line, <= 300 chars, REWRITTEN in place, never appended>
  next: <next concrete step or `trigger:` D77 measurement that would start it>
  refs: design docs/design/x.md; report docs/dev/lanes/y_report.md; K97; D163; bench O-96
  <optional charter paragraph: <= 6 lines, the owner's words and the problem; no history>
  - [CHILD-ID] STATE:... — ...        # child = 2-space nested; dotted id only if its parent is a row here
```

Rules that follow from it:

1. **Completed work leaves the file.** `completed` is not a state here; finishing a row = move the whole row (verbatim, as admin2 did) to plan_completed.md in the same commit. No stubs, no tombstones; `grep -n '\[ID\]'` across both files finds it.
2. **One id, one row.** Candidate/index views are generated (`scripts/plan_index`), never hand-copied.
3. **Charter vs status.** Charter text is edited only by the owner; the `status` line is the only volatile field and is dated. History goes to dev_journal.md / lane reports and is linked from `refs:`.
4. **A row over ~12 lines is a design doc in disguise** → move the body to `docs/design/<id>.md` and keep a 3-line row. (Today: 17 rows >5 KB.)
5. **Hierarchy only by nesting** (2-space steps), and dotted ids only mirror an existing parent row. "Under [OPTLOOP] candidates" becomes `Candidates` section + nesting.
6. **No free text outside the Policy section** (headings, rows, and ≤ 15 lines of policy). Design notes, positioning, retrospectives, hand-offs live elsewhere.
7. **Cite rows by `[ID]`, never by line number.**
8. **Dates ISO only** in new text; sessions by number if at all.
9. **A `started` row must carry a `status` date ≤ 30 days old** or it is reported (the audit of 2026-10-10 found 5 mis-tagged rows by hand).

## 8. Proposed lint rules (`scripts/plan_lint.sh`, step 3)

Severity: E = fails `make test`, W = reported. Land with a **ratchet** (baseline file of existing violations per rule, K35-style floors, the count may only fall) so the linter can ship before the cleanup finishes; each cleanup commit lowers the baseline.

| id | rule | sev | catches (today's count) |
|---|---|---|---|
| P1 | every non-blank line outside fenced code is a heading, a row line, a row continuation, or inside the `Policy` section | E | 35 free-text blocks (§5) |
| P2 | row head matches `^( {2})*- \[ID\] STATE:(not-started\|started\|blocked\|deferred) — .{1,100}$` | E | F1 (≈ 230 rows) |
| P3 | `completed`, `done`, colon-less `STATE x`, `HOLD`, `COMPLETED`, `ARCHIVED`, `archived to` forbidden as row heads | E | 11 + 7 + 29 + 31 + 1 |
| P4 | ids unique across the file | E | F8 (26) |
| P5 | an id that has a completed row in plan_completed.md must not have a live row here | E | resurrected rows; stub detection |
| P6 | ID syntax `[A-Z][A-Z0-9]*(-[A-Z0-9]+)*(\.[A-Za-z0-9]+)*`; dotted id requires its parent row as the nearest enclosing row | E | F10 (18 orphan dotted) |
| P7 | nesting: indent ∈ {0,2,4}, child indent = parent + 2, and no row of a lesser indent between a parent and a child | E | F9 wedges (3) |
| P8 | head line balanced `(` `)` and `**` | E | wedges where a body was split (:860) |
| P9 | required attribute lines present: `filed:`, `status (date):`, and `next:` or `trigger:` for `not-started`/`blocked` | W→E after cleanup | all |
| P10 | `status` line ≤ 300 chars, single line, ISO date; row total ≤ 12 lines / 1,500 chars (W), ≤ 40 lines / 4,000 chars (E) | W/E | F4 (146 / 71 / 17 rows) |
| P11 | no line > 1,000 chars; no hard wrap < 100 cols mixed with long lines in one file | E | 129 lines |
| P12 | no bold blob after `STATE:` | E | 10 |
| P13 | `started` row with `status` date older than 30 days, or `not-started` row whose status says MERGED/BUILT/LANDED/DONE | W | OPT-FIRSTSET, NULLABLE-ANCH, OPT-LITSCAN, BENCH-UTF8, … (the 24 STALE rows) |
| P14 | a row mentioning `MERGED <hash>` must not be `not-started`/`started` unless an `open:` attribute lists a remainder | W | stale-status detector |
| P15 | `[ID]` references resolve to a row in plan.md / plan_completed.md / a K-entry / D-entry / bench id; unknown ids W | W | F14 (34) |
| P16 | tree-wide: no `plan.md:<digits>` citation in live docs (docs/spec, docs/design, CLAUDE.md files) | W | F14 (112 in 35 files; frozen reports exempt) |
| P17 | section membership: `deferred` only under Deferred, `started` only under Active, `Candidates` rows have `parent: OPTLOOP` | E | F12 |
| P18 | state counts printed in the header are generated (`scripts/plan_lint.sh --counts`); the header may not contain a hand-typed count | E | "81 on 2026-09-22" |
| P19 | **non-vacuity (K35):** the lint counts the rows it parsed and fails if it parsed 0 or fewer than a floor; a planted-violation self-test per rule (like tests/spec_history) must go red | E | the linter itself |

Suggested order of work for the cleanup lane (step 2), cheapest first: (1) delete the 34 JUNK rows (17 KB: stubs and lead-ins), the 26-entry duplicate index block, and ~190 lines / 14 KB of free text (Next: M4, Development order, the M4/M6 sections, the two design notes, the positioning note, the small-debt shelf, the D125 banner) — zero information loss, everything is in plan_completed.md or the named design docs; (2) archive the 20 COMPLETED rows (60 KB of the file's 459 KB of row text, dominated by DEC-FALLBACK 14 KB, CLS-TREE 13 KB, START-TABLE 8 KB); (3) merge the 33 DUPLICATE/6 SUPERSEDED rows; (4) repair the 3 wedges; (5) the 24 STALE rows one by one with the owner (list in §4; the Frank-decision ones are TT-13, TT-15, MECH-3, LIB, M4-CALLOUTS, M4-SUBST, OS-2, DD-6, DD-2); (6) split the 17 rows >5 KB into row + design doc; (7) re-section by the §7 section list; (8) switch the linter from ratchet to hard.

Open questions for Frank (the manager can relay): confirm the SUPERSEDED/COMPLETED calls marked "(confirm with Frank)" or "ask Frank" in §4: [DD-6], [OS-2], [TT-13], [TT-15], [MECH-3], [LIB], [M4-CALLOUTS], [M4-SUBST], [OPT-VMSEED], [M7.0] residue, and whether the "guided tour" of the 2026-09-17 code review still wants a row.

