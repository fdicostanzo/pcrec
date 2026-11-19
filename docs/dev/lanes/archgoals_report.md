# archgoals report: the live architecture goals document (unit A3 of [ARCH-STEP])

## STATE AT HANDOFF

Lane archgoals (opus), branch lane/archgoals, base fed0b4886. Documents only: no code, skill, test or template.
Rulings file `docs/dev/lanes/archgoals_rulings.md`: empty at every read (start, before the WIP commit, before
this report); no R-n applied.
Premise test passed: both reports present on the branch; `grep -c "^## " docs/dev/guide/architecture.md` printed 17
before the change (25 after: 17 kept + 8 NEW).
Checks: `timeout 300 make -s test-plan-lint` PASS (2 passed, 0 failed); `timeout 120 scripts/check_claudemd_size.sh
--all` 381 files within limits; `make -s test-spec-history` 11 passed, 0 failed. No test or script reads
docs/dev/guide/architecture.md (`grep -rn "guide/architecture" tests scripts Makefile` printed nothing).
File length: 378 lines, under the 400-line split point, so the register stays in the one file.
History index entry added (docs/dev/history/claude_md/docs__dev__lanes.md).
OWED: none

## WHAT CHANGED IN THE GUIDE

docs/dev/guide/architecture.md (supplemented, nothing deleted or weakened):
- Top note: what the document is for, who updates it when; what A1, A2 and "the architecture note" mean.
- PART 1 GOALS (DRAFT): five ranked goals, each with a CHECK and SOURCES; the gate above them (no answer moves,
  nothing slower); priority 1 > 2 > 3 > 4, goal 5 decides when not what; non-goals.
  1. One home per question. 2. A new choice is a new row, acted on through the row. 3. Seams declared, facts both
  ways. 4. A data shape covers the inputs the plan already names. 5. Remodels ride along with the feature that
  needs them.
- PART 2: the 17 rules verbatim, each with a HISTORY line and a BEFORE DESIGN question. One fix: the "house idiom"
  sentence named `dfa_pfs[]` + `DFA_SELECT`; `dfa_pfs[]` is gone (`grep -rn "dfa_pfs\[\]" src` finds only comments),
  `DFA_SELECT` survives over `dfa_reprs[]` (emit_dfa.c:6034, :6361). New text names `cand_rows[]`/`cand_select` and
  `fit_rungs[]`, with a dated correction note.
- Eight NEW 2026-11-17 DRAFT rules in house form: one question, one primitive, from the second caller; act through
  the row, never re-ask its answer; refusals are a decision family; layering holds at the call level; a decision is
  read from its record, never from the emitted text; a stage-to-stage field names its one writer and its readers; a
  new AST kind states its cost, a pass reads the kind table where it can; a shape states the inputs it covers.
- PART 3 RIDE-ALONG REGISTER: 22 rows (A2 options 1-8 with 5/6/7 split as asked, the stream roadmap by reference,
  [VMREC], [RUN-POS-SET], [FLAG-DEMOTE]'s deny word, [DD-11.5] part (a), [ENG-ABS-CARET], [RXINFO-REMODEL], and
  smaller A2 items: signed start offsets, the reference grammar, first-row walkers, the Ctx/longjmp wrapper);
  HOW TO USE IT (five steps); "considered, not adopted" (A2 options 9-11, plus option 4 wholesale and option 8
  standalone).
- README.md (guide index line) and docs/dev/guide/CLAUDE.md (file line) describe the new role.

Overlaps between rules, reported rather than merged (as briefed):
- NEW "One question, one primitive" overlaps "Build the general form" (mechanisms) and "One table per slot"
  (tables); the new one is about QUESTIONS and names the second caller as the trigger.
- NEW "Act through the row" and "Refusals are a decision family" both extend "Decisions are declared tables"
  (its "action" and "observable" clauses already imply them; the tree shows they were not read that way).
- NEW "A new AST kind states its cost" overlaps "One question, one primitive" for the kind-table half.
- A2's "the sibling trigger should count call sites" went into the BEFORE DESIGN line of "Notice siblings", not a
  new rule (it sharpens that rule's count).

Discrepancies between A2 and the tree (checked, the register uses the tree):
- The `case CRA_*` switch A2 placed in `emit_unanchored` is in `unanch_scan` (emit_dfa.c:13775, cases :13814-13894).
- The seven `act == CRA_*` tests A2 placed in `emit_attempt` (:15015-15049) are in `emit_landmark_walk` (:14985);
  `emit_attempt` (:15410) has none.
- compound.c's `strcmp(..., "all")` is on line 210 (A2: 211).
- A1 and A2 did not contradict each other on any fact used.

## WHERE EACH LINE CAME FROM

Goals: sources are cited inline in part 1 (manifesto §1; ARCH-STEP.md owner words; D124; D151 addendum 3; D153;
D77; D70; roadmap §7; A1 entries; A2 sections). The tally "9 / 3 / 2 / 2 of 18" is A1's own "Patterns across
them" (missing seam 5 + second mechanism 4 = 9; tables 3; data shape 2; interface 2), re-added, not re-classified.
Rule HISTORY lines: A1 "Rules the guide already holds" and "Refactors that happened AFTER"; A2 chains/seams.
New rules: A1 "Patterns across them" (the missing-seam shape) and A2 "What the guide does not say".

Register WHERE, each checked at fed0b4886 with these commands (run from the worktree):
- `grep -n "cand_rows\[\] *=" src/gen/emit_dfa.c` -> 10517; `grep -n "case CRA_" src/gen/emit_dfa.c` -> 13814,
  13844, 13860, 13894; `grep -n "== CRA_\|!= CRA_" src/gen/emit_dfa.c` -> 13711, 13945-13959, 14835-14838,
  15015-15049, 16115-16153; `grep -c "CRA_" src/gen/emit_dfa.c` -> 36;
  `grep -c "cand_finish_of(cx) *[!=]= *CAND_ROUTE_VM" src/gen/emit_dfa.c` -> 26.
- function definitions: `grep -rnE "^(static )?[a-z].*\b(emit_unanchored|emit_attempt|emit_rev_end|emit_scan_loop|pcrec_emit_prologue|prefilter_decision|cli_parse|cli_dispatch|lm_maxw|pcrec_minw|cwmax_walk|pcrec_sat_mul|pcrec_vm_fmul|fd_decisions|pcrec_vm_stmt_respell|vm_emit_anchored_attempt|vm_emit_search_body|compile_driver|pcrec_select_engine|pflw_walk|st_why_walk|pf_admit_walk)\(" src cli`
  -> emit_rev_end 14816, emit_unanchored 13917, emit_attempt 15410, emit_scan_loop 13524, pcrec_emit_prologue
  16357, prefilter_decision select_engine.c:940, pf_admit_walk :859, pcrec_select_engine :1425, cli_parse
  main.c:1278, cli_dispatch :2904, lm_maxw lmwalk.c:80, pcrec_sat_mul mrl.c:134, pcrec_minw :151, cwmax_walk :545,
  pcrec_vm_fmul emit_vm.c:3874, vm_emit_search_body :13133, vm_emit_anchored_attempt :14011, fd_decisions
  facts_dump.c:129, pcrec_vm_stmt_respell vm_stmt.c:1085, compile_driver compile.c:2046, pflw_walk :1622,
  st_why_walk :1697.
- `grep -n "pcrec_nullable(\|pcrec_cwmax(" src/opt/mrl.c` -> 315, 685; `grep -rnE "^(static )?[a-z].*\b(cc_width|vm_general_min_width)\(" src` -> known.c:315, emit_vm.c:11436; `grep -n "rep.rmax" src/gen/lmwalk.c` -> 93, 95.
- `grep -n 'strcmp(pcrec_cand_plain_selection' src/core/compound.c` -> 210;
  `grep -c "cand_route_of\|pcrec_cand_body_route\|fit.chosen == ENGM_" src/gen/emit_dfa.c src/gen/emit_iter.c src/core/compound.c` -> 64, 2, 2.
- `grep -n "force_on" src/opt/select_engine.c` -> arms at 1079, 1084, 1091, 1107.
- `grep -rlE "case A_[A-Z_]+:" src | wc -l` -> 27; `grep -cE "case A_[A-Z_]+:" src/opt/atomic.c` -> 115;
  `grep -n "TEXT\|ZERO" src/core/kindrow.def` (header lines 8-23).
- `grep -n "^struct Ctx\|^} Job;" src/core/internal.h` -> 3970, 3818.
- `grep -n "PCREC_TARGET_HEADERS_MARK\|PCREC_HELD_HEADER_MARK" src/gen/memfn_stamps.c` -> 334-341;
  `grep -n strstr src/gen/vm_stmt.c` -> 1095, 1165.
- `grep -rn "struct CandRow {" src` -> emit_dfa.c:5752.
- `grep -nE "^(static )?[a-z].*\b(br_name_ref|rc_name_call)\(" -r src/parse` -> mod_backrefs.c:281,
  mod_recursion.c:293; `grep -rln "_strndup(" src/parse` -> six files.
- `grep -nE "pcrec_compile(_in)?\(" src/core/compile.c` -> 3762, 3791; `sed -n 43p src/core/compile_defs.c`.
- `grep -rn "pcrec_opt_has\|pcrec_flags_has" src | wc -l` -> 80; `grep -n xdeny docs/design/flag_demote_map.md`.
- `grep -n "facts/facts.h" src/core/internal.h` -> 3429; `grep -n "include.*enc" src/core/findings.c` -> 52;
  `grep -n "What the include graph cannot see" src/CLAUDE.md` -> 34; `ls src/core/ctxfn.def`.
Register events: `scripts/entry TAG -l 1` for [FLAG-DEMOTE], [IFACE-PUSH], [VLOOKBEHIND], [RXINFO-REMODEL],
[ENG-ABS-CARET], [DD-11.5], [VMREC], [RUN-POS-SET], [STREAM], [LOOK-LOCATE]; roadmap §1-2 and §7.
Decisions read by grep and sed in docs/dev/decisions.md (the `scripts/entry` decisions profile is dormant):
D75, D77, D119, D124, D146, D147, D151 (addenda 1-3), D153, D157, D182.

Nearest to their trigger (my reading): row 4 (measure library) at [VLOOKBEHIND] stage 2, build go 2026-11-10;
row 3 (refusal table) with row 15 at [FLAG-DEMOTE], GO given, opens after S1 and kit K38-2; row 1 (rows carry
their action) at roadmap A-REV, the stream chain [STREAM] says runs next after lookbehind stage 1 and alternation.

## QUESTIONS FOR THE OWNER

1. **goals ranking**: is "one home per question" above "a new choice is a new row"? I ranked it first because A1's
   most common shape (9 of 18) is a missing shared home, while your ARCH-STEP words lead with tables. Leaning: keep
   as drafted; tables are the commonest FORM a home takes. Reply either way.
2. **shape goal**: goal 4 ("a data shape covers the inputs the plan already names") rests on only two A1 entries
   (utf8 bitmap, alternation folds) and risks reading as "build ahead", which D77 forbids. Keep it, demote it to a
   rule only, or drop it? Leaning: keep, its check only asks about inputs a plan row already names.
3. **eight new rules**: eight is a lot at once. Adopt all, or adopt the four with the most evidence (one primitive;
   act through the row; read from the record; writer and readers) and hold the rest as drafts? Leaning: all eight,
   each is short and cites a live site.
4. **register keeper**: the brief has the manager update the register at each landing; should a feature's
   architecture note be REQUIRED to cite the rows it looked up (that is unit A5's wiring, so only a yes/no now)?
5. **speed as gate**: part 1 treats speed and answers as a gate above the goals, not as a goal, following the
   manifesto. Is that right for all product code, or only for the stream work it was written for?
