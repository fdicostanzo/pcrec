# archhist report: the refactor history, facts only (unit A1 of [ARCH-STEP])

## STATE AT HANDOFF

Lane archhist (sonnet), branch lane/archhist. Rulings file `docs/dev/lanes/archhist_rulings.md`: empty; no R-n applied.
Deliverable complete; gaps are marked "not found" or INFERRED in place.
OWED: none

Method note: four read-only sonnet helpers gathered the leads (one per era); their hand-backs reached the manager condensed, and the manager forwarded the condensed text. Where this report quotes a sha, line or count it comes from that text or from the helper report received directly; the shas below were each re-checked with `git log -1` (pre-refactor shas verified: 30de9e3ad, eacac76f9, 74379fe00, a29f02dd6, 8eec6f874, de89af4cb, 93b066ae7, 273ba1ac6, 7e1caad08, f77ed1130, fff636eda, cb1b968d9, bf9a5bb8d, 3bc599c92). Counts not re-run by me are marked (helper). Premise test passed: journal has 53 lines matching refactor|remodel.

## HOW THE HISTORY WAS SEARCHED

- `grep -c -i "refactor\|remodel" docs/dev/dev_journal.md` -> 53; `grep -n -i "refactor\|remodel" docs/dev/dev_journal.md` and reading around each hit (journal lines 1454-27430).
- `grep -n -i "refactor\|remodel\|unif\|record-first\|parallel mechanism\|migrat" docs/dev/decisions.md` (the `scripts/entry` decisions profile is dormant, "profile decisions dormant (unit 1)", so decisions were read by grep and Read).
- `grep -i "^- \[" docs/dev/plan_completed.md | grep -i "refactor|remodel|fold|retire|table|unif"`; `scripts/entry START-TABLE -l 2`.
- docs/dev/reviews/2026-09-17-code-review.md section 3 (the wave plan); `grep -l -i "parallel mechanism\|special case\|if-chain\|dispersed" docs/dev/reviews/*.md` (41 files listed; the S3 and r6/r8/r9 reviews read).
- docs/dev/guide/architecture.md (each rule's Source line), docs/design/start_table.md, docs/design/plan_row_bodies/ARCH-STEP.md.
- Four helpers searched by era with `git log --grep=TAG`, `git diff --shortstat`, journal and decisions greps (assignments: early refactors; REVW/FLAG/DOC-INDEX; START-TABLE/DEC-FALLBACK/entry rows/PRIOR-COST/DD-11.5/ROWCON; VMREC/MEMFN/RUN-POS-SET/stream).
- Not searched: memfn/docs/journal.md in depth (only the helper's summary of kit remodels), `docs/dev/backlog_triage_2026-09-22.md`, `code_review_criteria_draft.md` (the review's own synthesis was used instead).

## THE REFACTORS

Dates are YYYY-MM-DD. "Rule" = section of docs/dev/guide/architecture.md unless stated.

### 1. One struct for every AST kind, made a union (D70, [M6.6.2] wave 0)
- AGGREGATED: per-kind fields (cls[32], rmin/rmax, capno, multiline, revbody/possessive) as top-level fields of one struct `Ast` (src/core/internal.h:1491), "union-by-convention" (decisions.md:5333); the lookaround design (docs/design/lookaround_design.md section 3.1) proposed still more look_* fields. 200+ access sites, 13 sabotage anchors.
- FOUND: the 2026-08-23 design session, owner ask 1; owner: "I'm not worried about memory but complexity and flexibility. Using a union of types is a fine way to deal with it." (journal 12375-12395).
- COST: lane d70union, one day, 10 commits 9874c3076..777c31c7f, merge a9739e191, 42 files; sizeof(Ast) 104 -> 72; four-axis identity gate 2056x4 = 8224, 0 differing against pin eacac76f9. Unanticipated: 13 stale anchors re-homed; `rd_node` (src/opt/revdet.c) cleared revbody/possessive on every kind, a live clobber of u.cls.bits[] bytes that moved zero gate bytes, fixed by kind guards, tests/rungselect/revdet_highbytes.rxt and mech S121 (journal 12468, 12568-12580) (helper).
- KNOWABLE: partly. D62 (2026-08-18, decisions.md:4985-5003) accepted "a FUTURE analysis's author must read the field comment" and set "Revisit when: a fifth AST analysis lands". Ast built in M0+M1 211140b8a (2026-08-09); no note then weighing a union (helper).
- RULE: none. DATES: built 2026-08-09; decided and done 2026-08-23.
- NOTE (INFERRED): "One node type whose per-kind fields are dead for every other kind yet writable by generic code."
- RETRO: pre pin eacac76f9; no design note beyond APPROACH.md.

### 2. Class payload from a 256-bit bitmap to code-point intervals (M5.0 utf8 stage 1, lane utf8s1)
- AGGREGATED: every class consumer reading the 32-byte bitmap `cls[32]`; APPROACH.md:165-167 "256-bit bitmaps (uint64_t cls[4])" and :178 "UTF-16/32 later = new encoding backend, no core changes". Nine consumer sites (nfa.c:542, emit_vm.c:1515/3287/4608/7055, altcls, possessify, revdet) (helper).
- FOUND: a planned design step (design gate c767ae25f, 2026-09-04, "pure refactor", utf8_design.md:168).
- COST: commits e431744a0, 817315474 (2026-09-05), merge f22b65c44; 17 files +1194/-90; new cpset.c (309 lines) and lower_enc.c (158); identity gate 14/14, four axes, 2,557 patterns, 0 differing, no abi bump (journal 21495-21504). The lane refuted a design constraint and found S121 latent. Stages 2-5 to 2026-09-09, about 18 commits (helper).
- KNOWABLE: yes; utf8_design.md:133-139 records the monotonicity premise with triggers; APPROACH.md:165-178 shows the bitmap was a stated choice.
- RULE: none. DATES: bitmap 2026-08-09; decided 2026-09-04; done 2026-09-05.
- NOTE (INFERRED): "A_CLASS stores a fixed 256-bit bitmap, so a code point above 0xFF has no place in it."
- RETRO: pre sha 30de9e3ad; design note docs/design/utf8_design.md (APPROACH.md for the original).

### 3. Per-prefix universal constants unified (D60, [ABI-NS])
- AGGREGATED: universal constants emitted as per-prefix macros though their values do not depend on the artifact (decisions.md:4880-4958). D49 had already unified the VALUES a day earlier.
- FOUND: owner 2026-08-18: "i don't see the advantage on keeping them separate" (journal 10521).
- COST: charter 55c4b3c4d, merge 5fd0c3234, same day, 31 files +563/-181; collision with lib/pcrec.h PCREC_ENGINE_DFA/VM; 8 test sites read constants from the .c (helper).
- KNOWABLE: D49 (2026-08-17) unified the values and left the names. RULE: none (nearest: "Pre-release ABI changes happen, by ritual"). DATES: decided and done 2026-08-18.
- NOTE (INFERRED): "Constants whose values do not depend on the artifact are one declaration, not one per prefix."

### 4. One negative-code contract for the match entries (D49)
- AGGREGATED: `_match` collapsed give-ups to -1 (D42.3, 2026-08-14, decisions.md:3677) while `_match_caps` had distinct codes.
- FOUND: ruled 2026-08-17 at the counter-K design (journal 9178-9200, 1a9513b7f). D42.3 said "Re-open when a composition customer appears (cheap pre-v1 per D40)": the alternative was seen and deferred.
- COST: abi 1 -> 2; ERR_FLOOR -4 -> -5 later (09b276922) (helper). RULE: none. DATES: 2026-08-14 to 2026-08-17.
- NOTE (INFERRED): "Every entry reports the same give-up reasons with the same codes."

### 5. The recursion-module ParseMods pointer change that left anchors stale (side effect, not a refactor)
- [M6.2] wave A (211c5da84, merge e609a8c53, 2026-08-19) changed Ctx.mods from struct to pointer; five of seven drifted mech anchors (S08, S09, S21, S22, S26) were the result (journal 10600); fixed by lane sabanchors, ae6e41f82, merge 926b5894c, 2026-08-21. RULE: none directly; the 2026-09-17 review's "anchors are FLOORS found by grep" method rule is related. Included for completeness, not counted in the tally.

### 6. Flag/modifier state in an AST field to context rows (D62 -> [DD-11.5] P2a-P2c, lane ctxbuild)
- AGGREGATED: the multiline flag as a node field (D62, 2026-08-18) read by analyses; superseded by the D62 addendum (2026-10-19): (?m)^ and (?m)$ become A_CTX rows of src/core/ctxfn.def. A_BOL/A_EOL into A_CTX is still open (helper).
- COST: 12 commits 25dbef7bf..cda6592f4 (2026-10-18..20), merge d06b530f7, abi 80 -> 81, 26 files +515/-434. KNOWABLE: D62 said "Revisit when: a fifth AST analysis lands". RULE: none. NOTE (INFERRED): "A modifier that changes what a node matches belongs in the node's kind or context row, not in a flag that each analysis must remember to read."

### 7. One seam entry for variable match (lane varmvp; a rejected delivery, near miss)
- 2026-09-23..25; owner ruling "ONE seam entry: bref_match generalized to pointer+length"; first delivery adab16b6 REJECTED (var_match siblings beside bref_match, would force a second abi bump); revised 89655b7e renamed span_match and span_match_caseless and deleted two sibling-only mechanisms; merge 809aab12 = abi 32; 9 commits (journal 25598-25640) (helper). The ruling preceded the build, so cost was a rejected delivery, not a post-hoc refactor. RULE: none (the general-form rule is the neighbour).

### 8. The 2026-09-17 code review and its waves ([REVW], fix-now, waves U/1-5, A1)
- AGGREGATED, by the review's own counts (docs/dev/reviews/2026-09-17-code-review.md section 0): the walk discipline re-implemented x75, prefix interpolation x652, growable array x about 28 sites (13 extractable arrays, M5), scratch-buffer sizing x58+; emitters hold 44% of sabotage anchors; fragment buffers (emit_vm.c) 94/49/48/58; 39 layering back-edges (31 invisible to the tool); cli_parse a 59-arm guard repetition; abi log in three drifting homes. Onto: emit_vm.c interior, src/enc layering, cli_parse, lib/pcrec.h.
- FOUND: a chartered review, eleven opus lenses plus a second pass (decided 2026-09-17/18).
- COST: 2026-09-17..20, 276 commits 93b066ae7..85e5e84c6, src/cli/lib 63 files +8134/-5210 (helper); owner-asked git count: net +1,243 in src/cli/lib, 60,326 -> 62,437 lines, functions 861 -> 918, tests +4,675 (journal 24361-24375). Fifteen lanes; one abi event 26 -> 27. Wave commits (helper): FIX 13, U 3, W1 8, W2 52 (emit_vm.c EP2 16 steps), W3 9, W4 16 (cli_parse table d0c8b4c22; axes.def D111), W5 25 (D104 renames, libpcrec.a exports zero symbols without pcrec_ prefix), A1.
- KNOWABLE: nothing found for the individual primitives; the review itself says the tree is "healthy where sonnet lanes have been building under panel review".
- RULE: docs/dev/guide/coding.md sections 1-6 (the wired coding guide, charter added 2026-09-17); review section 5 method findings -> learnings.md section 3. In architecture.md: none by Source line.
- NOTE (INFERRED): "Every tree walk goes through one visitor and every growable array through one helper."
- RETRO: pre = 93b066ae7^.

### 9. Raw flag-word reads behind four accessors ([FLAG-ACCESS])
- AGGREGATED: 65 raw reads of the public flags word in 15 files (plan said about 63 in 11) -> 4 accessors in src/core/internal.h (helper).
- FOUND: the owner's flag-bits concern (58 of 64 bits used; docs/dev/flag_audit_2026-11-12.md; decisions.md D195, line 10187) and the [IFACE-PUSH] trigger at <=4 free bits. COST: filed and merged 2026-10-10 (04b83ddf1, 67f59d244), 8 commits, 29 files +358/-79; gate tests/core/flag_access_check.py, S792; no abi. KNOWABLE: nothing found. RULE: coding.md section 1.10. Pre = 273ba1ac6. Related, not built: [FLAG-DEMOTE] (not-started, needs an internal deny word at compile.c about 1415-1500, tune.c:81).
- NOTE (INFERRED): "The flags word has one reader function per question; no site tests a bit directly."

### 10. Start strategies into one table (refactor A, [START-TABLE] C0-C7 + C5b, D151)
- AGGREGATED: start mechanisms built one by one as local tables and predicates (`dfa_pfs[]`, `req_admits[]`/`req_uses[]`, `dfa_search_starts[]`, reseed rows) in src/gen/emit_dfa.c, emit_vm.c, select_engine.c; docs/design/start_table.md section 1; the sibling question was D124 ("notice siblings") and docs/design/litscan_k82h.md section 2.1 records "why `req_uses[]` was born separate".
- FOUND: the owner 2026-10-06: "So are we going to reorganize around a single start strategy decision table?" -> "Agree with direction"; D151 addendum 1 (fold first, before the reverse-walk row), addendum 3 Q2 ("otherwise logic is spread around which is the opposite of what we want"). Design: where_to_start.md, decision_families_survey.md.
- COST: 2026-10-06..10-08 (design 10-06; C6+C7 merged cf3ffaacd 10-08); 32 commits, src +3460/-1219 (helper); no-mover (byte-identical) gates; 14 sabotage re-aims, 81 re-runs, 95 family rows (start_table.md section R). Pre sha 74379fe00 (abi 64).
- KNOWABLE: D124/D148 and the decision-families survey show the family at three-plus dispersed members before the build; the first member's note (litscan_k82h.md section 2.1) shows a private table chosen on purpose.
- RULE: "Decisions are declared tables, not if-chains" (Source: Frank 2026-09-28 and 2026-10-12; D122, D151) and "Notice siblings of a decision family" (Frank 2026-10-06; D124, D151); "Refactors outrank optimization on the same site" (D153).
- NOTE (INFERRED): "Every start strategy is one row of one table with one row contract; no start mechanism has its own array."

### 11. Fallback ladders into one declared form (refactor B, [DEC-FALLBACK] B0-B7, D151 addendum 2)
- AGGREGATED: engine-fallback decisions as scattered conditionals in select_engine.c (the prefilter admission ternary at select_engine.c:862, [SEL-1] overflow rungs), becoming `fit_rungs[]`; plus [DEC-VAR-ATTRIB], [DEC-COLLAPSE-WASTE], [DEC-ROUTE] (rode the fold).
- FOUND: the same 2026-10-06 ruling that opened refactor A: "two serial no-mover refactors A / B". COST: 2026-10-06..10-09, 42 commits, src +2663/-1072 (helper); B7 merged 09ce1b36 (2026-10-09). Pre sha a29f02dd6. KNOWABLE: docs/design/decision_families_survey.md; no note at the time each ladder was built (not found). RULE: as entry 10. NOTE (INFERRED): "Each fallback is one named rung of one ladder with a declared predicate."

### 12. Entry rows built before the iterator ([ENTRY-ROWS] E0, D163 addendum 7 Q4)
- E0 (the zero-mover `entry_rows[]` table) built BEFORE the iterator's I1, under remodel-first (decisions.md D163 add. 7, ~line 9661). 2026-10-16..18, src +6150/-1201 (helper); pre sha 8eec6f874. Here the rule was applied up front: a new feature (find-all iterator) found the entries a dispersed family and the table landed first. RULE: applied "Notice siblings"/"Refactors outrank optimization". Original entries' design: nothing found.

### 13. Record-first VM ([VMREC], D182)
- AGGREGATED: about 132 body print sites in emit_vm.c (14,573 -> 14,201 lines) beside a separate listing event stream; 91 statement sites, 46 unrecorded (journal 27404; decisions.md:10012); a second description of the same statement in text and in the event record.
- FOUND: reviews r6 (vmcons), r8, r9 (journal 27395/27413/27419), 2026-10-29: root-cause ruling "printing IS recording".
- COST: bf9a5bb8d (2026-10-29) to merges 3bc599c92 + cfb6c4a85 (2026-10-31), about 32 commits, new src/gen/vm_stmt.[ch]; 0 movers over 68 arms x 548 (helper). Pre sha de89af4cb.
- KNOWABLE: nothing found; original VM built 2026-08-15 (242dcf37a), design docs/design/engine_m4.md.
- RULE: coding.md section 2.7 (helper). NOTE (INFERRED): "Every VM body statement is produced from one typed record so analyses read records, not re-lexed text."

### 14. Migration of every search site to the kit ([MEMFN], D146/D147, Q42)
- A deliberate migration, not an accretion: filed 2026-10-04 (cdd129428); Q42 2026-10-05 "migrate EVERY search site ... a half-migrated tree makes everyone remember which sites are which" (decisions.md:9054). 266 commits; M1-M7 zero-mover merges 2026-10-06..10-09 (81bc13dee, 76b7eadf6, d33e1d55e, 33186bc02, 2382b26b2, 6e7fc41e5, 287133bae). Inventory of sites: compare_stack.md:101 (2026-09-25). RULE: "Across the kit boundary, send facts, not methods" (D157, D146). Pre sha 691a8b7c7 (INFERRED). Counted as other.

### 15. One window site replaces the REPORT-specific path (D172; kit remodels ROWCON and window)
- AGGREGATED: a REPORT-specific search path beside the general window search; trigger R-27 bug fix; the first design was rejected by panel M1 (helper). 1967412ff (2026-10-21), landed 2026-10-24, 74 commits. KNOWABLE: nothing found. RULE: same "One table per slot" family (and D172 S3's "two stop rules are the first unification", decisions.md ~10049). NOTE (INFERRED): "REPORT and every other window search share one site."

### 16. A private copy of a declared table: S3's find step
- AGGREGATED: S3 mapped the kit's FIND table onto a two-value enum and lost the two-stream form (29x on caseless literals). FOUND: code review 2026-10-23 (docs/dev/reviews/2026-10-23-r1-memfn-s3-code.md, C1/C3/C5). COST: fix before landing; pre sha 7e1caad08. RULE PRODUCED: "One table per slot: no private copy of a declared mechanism" (architecture.md, Source this review). KNOWABLE: the FIND table existed when S3 was designed.

### 17. Span-context slice built then deleted ([DD-11.5] span slice, [COVER-CAP] stage 1)
- The span slice (UL-0, `span_facts`) built 2026-10-21 (cb1b968d9) and deleted by COVER-CAP stage 1 on 2026-11-15 (merge fff636eda, abi 108) (helper). Cost: 25 days of existence; details of the deleted code not found. RULE: none.

### 18. Row contract that grew an engine (ROWCON / K96)
- K96 found 2026-10-07 (a row's applicability ignored fields the only caller never sent), ROWCON narrowed the same day, closed 2026-11-10 (helper). RULE PRODUCED: "A row checks its own contract" (Source: Frank 2026-10-07, K96). Memory note: ROWCON grew from K96 into an engine plus an abi event.

### 19. Alternation fold handling to one owner ([RUN-POS-SET] / [ALT-NF], D187)
- AGGREGATED: fold (case/class) handling spread over lower_enc.c, altcls.c, req.c `rr_alt` (docs/design/alt_normal_form.md rev 3). Design first (rev 0-3 on 2026-11-05); critic r2 found SND-1 (answers moved). Stages 1-2b landed f77ed1130 (2026-11-07, abi 97, src +1584/-612); stage 3 started 2026-11-13 (in flight). Pre sha f77ed1130^1. RULE: none yet. Knowable: the alternation island review (2026-09-03-r53) existed earlier (not read; not found as a statement about this).

### 20. Design redirect before build: MATCH-SPLIT pin-only -> COMPOUND (D163)
- A design, not a build: 2026-10-12 the pin-only panel found a miscompile; docs/design/match_split_pinonly.md SUPERSEDED by compound.md; COMPOUND B0-B4 built, MATCH-SPLIT parked. Cost in code: none found. RULE: none.

Avoided cases recorded in the decisions (not refactors, kept for the tally of what the record shows being prevented): D75 (the general `pcrec_has_live_capture` built first, not gated on a recursion call; journal 13790-13795; produced "Build the general form; no parallel mechanisms or special cases", 2026-08-23); [PATFACTS] D120 (D125 add. 1 ~decisions.md 8640-8660: "built first, it would be a parallel mechanism that [PATFACTS] then replaces"; 44 commits to 2026-09-30); D8/M2.7 (`$` unified, `^` deliberately deferred, [ENG-ABS-CARET] trigger unmet). In flight or not built: [RXINFO-REMODEL] (plan row, not-started), [DOC-INDEX] D192 (10 commits, 2026-11-10), [MEASURE-SET] D166 (23 commits), [FLAG-DEMOTE].

## PATTERNS ACROSS THEM

A plain tally of entries 1-4, 6, 8-20 (entry 5 is a side effect, entry 7 a rejected delivery; INFERRED classification by me, each entry has one primary class; 18 entries):
- if-chain or dispersed family became a declared table: 3 (10 START-TABLE, 11 DEC-FALLBACK, 12 entry_rows; the cli_parse table is one wave inside 8).
- second mechanism beside a first, unified or deleted: 4 (3 ABI-NS, 15 D172 window site, 16 S3 private copy, 17 span slice); entry 7 is the same shape caught at review, a near miss counted outside the 18.
- missing seam or primitive (one function or record that every site should call): 5 (1 D70 union, 6 D62 to A_CTX, 8 REVW, 9 FLAG-ACCESS, 13 VMREC).
- data shape with no room for the next feature: 2 (2 utf8 bitmap, 19 alternation fold owner).
- interface that was inconsistent or leaked a method: 2 (4 D49, 18 ROWCON/K96).
- other: 2 (14 MEMFN migration, deliberate; 20 D163 design redirect).
Sizes, commits: entries with a measured commit count: REVW 276, MEMFN 266, D172 74, START-TABLE 32 (src +3460/-1219), DEC-FALLBACK 42, VMREC about 32, entry_rows E0 (src +6150/-1201), utf8 about 18 plus stages, D70 10, FLAG-ACCESS 8, D62 to A_CTX 12.
Observations the record states (not conclusions): the table-shaped refactors were all gated "no-mover / byte-identical" with a sweep at zero movers; three of the refactors were triggered by an owner question or ruling (START-TABLE, ABI-NS, D70); three by a critic round (VMREC, S3, REVW); entries 1, 2 and 6 each name a "revisit when" or later-stage trigger in the earlier note.

## RULES THE GUIDE ALREADY HOLDS AND THEIR SOURCE

architecture.md section by section (Source line verbatim; refactor that fed it; whether a refactor in this list came AFTER the rule's source date):
1. "A design states its goals, ranked" - Frank 2026-10-23 (RX_FOREACH iterator timing, job 599); not from a refactor in this list. Refactors after it: VMREC (2026-10-29..31), RUN-POS-SET (2026-11-05..), COVER-CAP stage 1 (2026-11-15).
2. "Decisions are declared tables, not if-chains" - Frank 2026-09-28 and 2026-10-12; D122, D151: fed by START-TABLE/DEC-FALLBACK (10-06..10-09; their decisions are the rule's cited sources). Later: entry_rows E0 (10-16..18) applied it.
3. "One table per slot: no private copy" - 2026-10-23 S3 code review (entry 16). After it: D172 window site landing (10-24), VMREC, RUN-POS-SET.
4. "Build the general form; no parallel mechanisms or special cases" - Frank 2026-08-23; D75 addendum. Came BEFORE: D62 to A_CTX (2026-10-18..20), START-TABLE, DEC-FALLBACK, entry_rows, VMREC, S3 private copy (2026-10-23), D172 window site, the span slice (built 10-21, deleted 11-15). The rule did not prevent these; whether each was "a special case" under the rule's wording is not in the record (the S3 review cites it as C1/C3).
5. "Notice siblings of a decision family" - Frank 2026-10-06; D124, D151. Came before: entry_rows (applied), VMREC, RUN-POS-SET stage 3.
6. "A row checks its own contract" - 2026-10-07 (K96, entry 18). After: S3 private copy (C1/C3 narrowing), ROWCON's closing 11-10.
7. "No silent defaults" - 2026-10-07; D161, D162. Not tied to a refactor in this list.
8. "Across the kit boundary, send facts, not methods" - D157, D146 (entry 14).
9. "Build under measurement" - Frank 2026-08-25 and 2026-10-21; D77, D18. Not tied to a refactor.
10. "Tuning constants are suspect" - 2026-10-05. None.
11. "A VM capacity change is measured through both entries" - review 2026-10-29-r2 F5. None.
12. "Simplification is a benefit on its own" - Frank 2026-10-18. Applies to START-TABLE and others retrospectively; none produced it by Source.
13. "Pre-release ABI changes happen, by ritual" - 2026-08-25; D40, D76, D94. Came before D62 to A_CTX, START-TABLE (no abi), VMREC (no abi), RUN-POS-SET (abi 97).
14. "Refactors outrank optimization on the same site" - 2026-10-06; D153, D151. Came before entry_rows, VMREC, RUN-POS-SET, COVER-CAP.
15. "Product first, harness minimal" - 2026-10-21; none.
16. "Caller-facing names describe behaviour" - D174 (not a refactor).
17. "A directory of parts and one runner" - 2026-11-12; shared append-only files (history index, manifests) caused merge conflicts; no refactor in this list.
Refactors NOT producing any architecture.md rule by Source line: D70 union, utf8 intervals, ABI-NS, D49, D62 to A_CTX, REVW (feeds coding.md), FLAG-ACCESS (coding.md 1.10), VMREC (coding.md 2.7), RUN-POS-SET, DD-11.5 span slice.
Refactors that happened AFTER the rule they might be read against already existed (the rule did not prevent them; listed because they matter most): after "Build the general form" (2026-08-23): D62 to A_CTX, the span slice built 2026-10-21 and deleted 2026-11-15, the S3 private copy, D172's REPORT-specific path, VMREC (a second description of each statement; the rule is about mechanisms, whether it applies is not stated in the record). After "Notice siblings" and "Decisions are declared tables" (2026-10-06 / 2026-09-28): VMREC (not a table case), RUN-POS-SET stage 3 (fold handling over three files). After "Refactors outrank optimization" (2026-10-06): COVER-CAP stage 1 deleting the span slice. After "One table per slot" (2026-10-23): none found that is the same class; D172's window-site landing was in flight that week.

## WHAT A NOTE WOULD HAVE NEEDED TO SAY

(All INFERRED; one sentence per refactor, a fact about that code.)
1 D70: "Per-kind fields are dead for other kinds yet writable by generic code, so the node needs a variant per kind."
2 utf8: "A class is stored as a 256-bit bitmap and has no representation for a code point above 0xFF."
3 ABI-NS: "These constants do not vary by artifact, so one namespace declares them."
4 D49: "Every entry uses the same give-up codes."
6 D62: "A modifier that changes matching is a context row, not a flag each analysis must read."
8 REVW: "Every tree walk goes through one visitor; every growable array through one helper; every emitted prefix through one function."
9 FLAG-ACCESS: "One accessor per flag question; no site tests a bit."
10 START-TABLE: "Every start strategy is a row of one table with one row contract."
11 DEC-FALLBACK: "Each fallback is a named rung of one declared ladder."
12 entry_rows: "The entries are rows of one table before the iterator adds a row."
13 VMREC: "Every VM body statement is produced from one typed record."
15 D172: "REPORT and every window search share one site."
16 S3: "The find step reads the kit's FIND table; it has no enum of its own."
17 span slice: nothing found in the record about what the slice assumed; a note would have had to say what COVER-CAP's cover row subsumes (INFERRED from the deletion).
18 ROWCON: "A row declines every field it does not honour, judged against the full contract."
19 RUN-POS-SET: "Fold handling has one owner; the other files ask it."
14 MEMFN and 20 D163: not applicable (deliberate migration; design redirect).

## CANDIDATES FOR THE RETRO TEST

Chosen for an easy pre-refactor checkout and a written design of the original feature:
1. [VMREC]: pre-refactor commit de89af4cb (2026-10-30; main just before the vmrec merge 3bc599c92); original VM design docs/design/engine_m4.md (built 242dcf37a, 2026-08-15); what the refactor later did: records for every body statement (new src/gen/vm_stmt.[ch]).
2. [START-TABLE]: pre-refactor commit 74379fe00 (2026-10-06, abi 64); original designs docs/design/startset.md, offset_k_skip.md, litscan_k82h.md; what it later did: one `cand_rows[]` table (d151 addenda).
3. D70 union: pre-refactor commit eacac76f9 (2026-08-23); original written design APPROACH.md plus docs/design/lookaround_design.md section 3.1 (struct Ast built 211140b8a, 2026-08-09, no design note weighing the union); what it later did: a union of per-kind payloads, sizeof(Ast) 104 -> 72.
Alternates: utf8 stage 1, pre 30de9e3ad (design APPROACH.md:165-178, later utf8_design.md); [DEC-FALLBACK], pre a29f02dd6 (design docs/design/dec_fallback.md); FLAG-ACCESS, pre 273ba1ac6 (no original design note found).
