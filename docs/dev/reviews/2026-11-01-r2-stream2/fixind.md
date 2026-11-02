# FIXIND: fix-induced lens, crit-stream2 (rev 2 re-check)

## Findings

All file:line cites below are in the review tree /home/pcrec/projects/pcrec/worktrees/crit-stream2
(main 8e846f501) unless marked lane/p1build (read by `git show`).

### FIXIND-1: A8's fix puts `\K` and `\G` into `Nfa.erased`, which today's tree rules EXACT. Applied, it moves today's VM hybrid windows
- CONFIRMED. INDUCED by A8 (§6.0 "The superset owner"). Severity: design/speed (bytes and a stamp move). Effort: a paragraph. Blast radius: §6.0, row 7's BUILT status, row 5, P-c's byte-identity pass criterion.
- §6.0 says `Nfa.erased` is "the ONE source" and that "the record covers ANYTHING that makes a stretch's (start, end) differ from the reported (slot0...): erasures, `\K`..., `\G`". Today the record carries LANGUAGE widening only. `src/core/kindrow.def:65-66` reads "`\K` moves the reported start and adds nothing to the language: exact", with `A_KRESET` and `A_GSTART` erase 0. `src/core/internal.h:2427-2435` lists exactly four bits (LOOK, ATOMIC, COUNT, CALLOUT). lmwalk's own `g1` keeps the report shift SEPARATE from the record: lane/p1build `src/gen/lmwalk.c:181-183` tests `A_GSTART` and `A_KRESET` and only then `erased == 0`.
- Repro: `build/pcrec -p rx --features all --pattern 'a\Kb'` gives `RX_VM_PREFILTER "hybrid"` and `RX_VM_PREFILTER_LANG "exact"`. `'\Ga(x)'` gives the same with `RX_VM_START "gstart"`. That is correct: the window is the PRE-shift span and the VM applies `\K` itself. If `\K`/`\G` set bits in `Nfa.erased`, then `pcrec_vm_prefilter_window` (`emit_vm.c:3774-3777`, `prefilter && !erased`) and `cand_project` (`emit_dfa.c:13647-13651`) flip for these patterns. The window drops to LOWER, emitted bytes move (P-c's byte identity fails), and the caller-visible `_PREFILTER_LANG` stamp changes (a D80 event nobody lists). Row 7 ("BUILT as today's hybrid exact window") stops being today's.
- Fix shape: the report shift is a fact about the hand's CONSUMER (does the finisher recompute slot0?), not a language superset. State it as its own seam or card fact next to `Nfa.erased` (today it is lmwalk g1's two extra tests). Keep `Nfa.erased` language-only, as `internal.h:2413-2420` defines it.

### FIXIND-2: A12/C8's per-coordinate `pos` vocabulary drops three of today's hand types, which the card's `accepts` (= `take`) still reads
- CONFIRMED (grep). INDUCED by A12/C8 (§4.1 `pos`; §4.2 `accepts`). Severity: design. Effort: a table row. Blast radius: §4.1, §4.2, P-b and P-c byte identity.
- Today's hands are `emit_dfa.c:9800-9814`: AT, NOMATCH, SPAN, ENDSET, LOWER, WINDOW ("a speculative end with no claim that a match exists") and EXISTS ("an end some match has", not necessarily the reported one), plus the type bits `CT_HIT` ("the gate landmark's leftmost occurrence", FIRST hands `CT_HIT | CT_LOWER`, `:9969`) and `CT_VERDICT`'s "or the accepted bound unchanged" (`:9792`).
- §4.1's `pos` has start ∈ {AT, LOWER, UPPER, CAND, NONE} and end ∈ {AT, ENDSET, NONE}. It has no spelling for a speculative end (WINDOW), for an end of SOME match (EXISTS), or for a landmark hit (HIT). RECOVER takes WINDOW and EXISTS (`emit_dfa.c:5689-5695` "the composite asks with `EXISTS`, the `rev-end` walk with `WINDOW`"), and RECOVER is in P-b's `reverse-pass`. The new `accepts` field therefore reads values the run-time half cannot express.
- Sibling unstated: §4.1 names "`CAND_HAND_*` / `CT_*`" as its precursor without mapping each one.

### FIXIND-3: B7/SEAM-9's soundness/profitability split misfiles row 5's conjuncts
- CONFIRMED. INDUCED by B7 (§4.2 rule 4; §6.1 row 5 vs §6.2 row 5). Severity: answer-risk under a later pricing edit. Effort: re-sort one row. Blast radius: row 5, the [LANDWALK-PRES] "one row edit in P2" claim.
- `finisher-dfa` is listed under PROFITABILITY (§6.2 row 5), yet its reason is soundness. lane/p1build `lmwalk.c:124-127`: "the FINISHER's route is CR_DFA, so a VM hybrid's erased prefilter body (whose language is a superset) never reaches the walk". `anchored-A` is the AT hand's taker, which is structural. By rule 4, profitability may be re-priced freely, so a pricing change that drops `finisher-dfa` admits an unsound walk.
- Siblings unstated: of lmwalk's ten rows (`lmwalk.c:276-287`), `branches`, `split` and `machine` (POST) appear in neither column.

### FIXIND-4: B7's card rule 2 ("the graph has no cycle") is stricter than the check it cites. Today's own start table fails it
- CONFIRMED (source). INDUCED by B7 (§4.2 rule 2). Severity: design. Effort: one sentence. Blast radius: §4.2, P-c ("the card half is needed here anyway").
- `table-read-cycle` (`emit_dfa.c:11244-11265`, `cand_read_cycle`) is acyclic per (slot, deny-bit) STATE. It explicitly allows slot cycles that are acyclic in rows (`:9868-9876` "let one cycle in the slot graph be acyclic in the rows"). Today's table has `NEXT` reading `NEXT` (`:9974-9984`) and, on the DFA route, PRESENCE→NEXT→FIRST→PRESENCE (`:9943-9983`). Both are legal only through `under`/`by`. As worded, rule 2 rejects them.
- The `reads` card field already names "which counterfactual WORLD". Rule 2 should say acyclic over (part, world) states.

### FIXIND-5: C7's one stamp rule plus C8's kind-row meters contradict "this rule keeps today's values" twice
- CONFIRMED. INDUCED by C7+C8 (§5.3, §5.1, §1 table). Severity: design/doc (a D80 contract). Effort: two clauses. Blast radius: §5.3, §1.1 rows 1/7/10 ("stamp dfa"), the maximality gate.
- (a) `ACCEPT` is a choice-family kind (§1 family table; §5.1 row `CHOICE, GOTO, FAIL, CUT, ACCEPT`). Every stream ends in `ACCEPT` (§1.1 row 1 `FIND lit "abc" → ACCEPT`, "stamp dfa"). So "`dfa` iff no choice-family or barrier record is statically reachable" never yields "dfa". Rev 1's three candidate rules all excluded the start loop or named M; rev 2's single rule lost that exclusion.
- (b) "budget stamps emitted iff a reachable kind row charges that budget". No kind's meters cell names the WORK budget (steps, frames, trail, "the kit's own"). Today every budgeted VM artifact stamps both. Repro: `--pattern '(a)(b)'` gives `RX_VM_FRAMELESS 1`, `RX_STEP_BUDGET 500000000LL`, `RX_WORK_BUDGET 1000000000LL`, and `(\w+)@(\w+)\.com` gives the same. WORK is charged "at each cut, at each frameless scan completion" (`emit_vm.c:8107-8110` comment), i.e. by `CUT` and `SKIP`, whose rows do not say so. Also `has_budget` is one gate for both counters (`emit_vm.c:8096-8105`, D49), which is not a per-kind fact.

### FIXIND-6: B7/SEAM-9's new profitability columns give rows 7 and G a rarity decline that today's code does not have, and that §11.3 forbids
- CONFIRMED (source). INDUCED by B7/SEAM-9 (§6.2 rows 7, G). Rev 1 row 7 had no rarity. Severity: speed/give-up (D158). Effort: one cell each. Blast radius: §6.2, §11.3 "Pricing", P-c byte identity.
- Row 7's "the window's rarity against the VM's unwindowed scan" contradicts today's hybrid window, which is "an ORDERING RULE (4.7), not a tuning knob: a pattern whose prefilter can answer must never reach the step budget" (`emit_vm.c:13013-13025`; bench case (e) 25.4 GB/subject). A rarity decline turns answers into give-ups, which D158 forbids. Row G's rarity contradicts the first-class seek: "`|S| < 256` as the ONLY narrowness gate ... no density admission is applied" (`emit_dfa.c:8021-8025`, D149). The census's prefilter reasons (scensus summary.txt M2) include no rarity reason.
- Both conflict with §11.3 "any planner pricing waits for lane/rulepilot's verdict" (D6). Rows 5 and 8 do price today, so "any" is also too broad: say "no NEW pricing".

### FIXIND-7: C11's give-up vocabulary keeps a value D158 forbids and adds one today's tree lacks
- CONFIRMED. INDUCED by C11 (§4.2 give-up contract; §6.2). Severity: doc/design. Effort: a sentence.
- Today's values are `CG_ANY` and `CG_FIXED` only (`emit_dfa.c:9829-9831`; §4.2 cites `:5682`, the field). ONE_WAY is new. D158 makes ONE_WAY a property of EVERY optimization ("a violator is a defect"), so ANY is no legal value for any row. Yet row 5's "as lane/p1build declares" IS `CG_ANY` (p1build's `landmark-walk` row sets no `.contract`). Row 13's "FIXED for the fire set's caller-visible rules" puts a fire-set rule into the give-up column, which is a category mix.

### FIXIND-8: C4's homes for X15 and X16 name things no part or card field holds
- CONFIRMED (text). INDUCED by C4 (§7.1 X15/X16; §4.1). Severity: design (F3/F4). Effort: a field and an owner.
- X15: "P5's iterate rule reads the stream's card (a not-empty start constraint)". §4.2's seven card fields have no such field. Today's demand is for a BUILT not-empty machine or a guarded matcher (`emit_iter.c:48-52`, `PCREC_ITER_NEEDS_NEDFA` / `_GUARDED`), and no card field says which part offers it.
- X16: the position-domain rule (code, three spellings today) is "owned by P6". P6's oracle is "n/a (a contract, not code)", so §0 F3's measurable form ("every part names an oracle") fails for it.

### FIXIND-9: B8's re-key inventory misses kind-keyed sets
- CONFIRMED (grep). INDUCED by B8 (§8). Severity: maintenance/doc. Effort: a list.
- Beyond the `measures_table.inc` (64), `synthetic-all-walk.tsv` and `kit-interim-grid1.tsv` (64) that §8 lists, the kinds key `memfn/data/sets/synthetic-every-key.tsv` (272 lines), `synthetic-all-v1.tsv` (12), `synthetic-all-wide.tsv` (12) and `measure_store/zen4-grid1/1/set.tsv` (64). The bijection argument still holds, but the re-key's site list must be found by grep (the D94 lesson).

### FIXIND-10: B7's card has `accepts` but not its dual, the hands a part offers
- CONFIRMED (source). INDUCED by B7 (§4.2). Severity: design (low). Effort: one row.
- Today each row declares what it HANDS (`CandRow.hands`, `emit_dfa.c:5683`; lmwalk's `.gives` on lane/p1build), and `take` is matched against it. P2's contract check "every hand typed (§4.1)" and the `cand_project` projection need the producer's declared set. The card does not list it.

### FIXIND-11: doc slips around the fixes
- CONFIRMED. Severity: doc. Effort: minutes.
- §5.2 GUIDED cites "bench 10, plus 8 frames-unbounded; §10", but §10's table has no M6 row (the numbers are scensus M6, which hold).
- §0.1's "96,159 lines of `src/*/*.c` + `cli/` + `lib/`" is `src/*/*.c` + `cli/*.c` exactly. lib/ is not in it.
- §7.1's "28 non-comment lines" of `fit.chosen`: my filter finds 24 code lines in the same 7 files. Not material.
- The header says "§12 maps" where §14 maps.

### FIXIND-12: A4's one backref superset, as worded, UNDER-states a caseful backref to a caseless group, so row G would lose matches
- CONFIRMED (oracle + build). INDUCED by A4 (§6.0 "The backref superset", used by G, row 1's FOLLOW, the typing rule). Severity: ANSWER (in text; no code reads it yet). Effort: one clause. Blast radius: row G, row 1 (FOLLOW), the struck row 17.
- §6.0 defines it as "the referent's language under the BACKREF's own caselessness". For `(?i:(a))\1` that reading gives {a}. But the group can capture "A", and a caseful `\1` then matches "A" exactly. Repro: python `re.search(r'(?i:(a))\1','AA')` gives (0,2) and `'xAA'` with `x(?i:(a))\1` gives (0,3). The review-tree build's `--emit-main` gives `match 0 2` on "AA" and `nomatch` on "aA". A NECESSARY row reading {a} would hand NOMATCH on "AA". The pcre2-reader note `/var/tmp/pcrec-pcrec/scratch/pcre2notes/backref-referent-choice.md` §4 confirms the backref's own scope decides only the COMPARISON ("((?i)rah)\s+\1 matches "RAH RAH"").
- Fix: the superset is the referent's language under the REFERENT's caselessness (what it can capture), closed under the backref's fold when the backref is caseless (plus the ε and duplicate-name/`(?|` unions). The same note §2-3 holds the union-over-duplicates and the "ε only when all are unset" halves, so §13's A4 ask is answered: the union stays a valid superset.

## Per-id verdicts on §14 (does the cited section carry the ruled fix; what it induced)

| id | cited section carries it? | induced / note |
|---|---|---|
| A1 | YES: row 7's atomic clause, row 15, row 4's outer-pin clause | row 7's atomic and callout clauses are unreachable while its first conjunct (empty record) holds; harmless |
| A2 | YES: row 15 UNSOUND AS STATED, §13 ask (note now present) | none |
| A3 | YES: §6.0 definition, row 2, Forced to B | row 2's σ clause is subsumed by the capture conjunct (A6) for replacement rows; dead text, not wrong |
| A4 | PARTLY: one definition, but worded wrong | FIXIND-12 (answer) |
| A5 | YES: row 1 = possessify.c:10-47 (checked), polarity, arms at :544-590 | none |
| A6 | YES: §6.0 capture conjunct, rows 3/4, §6.3 maximality "WITH its captures" | none |
| A7 | YES: row 16 (CALL half; counter half recorded as NOTED) | none |
| A8 | PARTLY: carries the coverage, but places it in `Nfa.erased` | FIXIND-1 (bytes, stamp) |
| A9, A10, A11 | YES: rows 8, 11, 12 | none |
| A12 | YES: typing per coordinate, no UPPER (cand_project :13647-13651 checked) | FIXIND-2 (missing WINDOW/EXISTS/HIT) |
| A13 | YES (DOC): rows 10, 14, the fold | none |
| B1 | YES: §0, G0 gate, §11 T rows as gates | none |
| B2 | YES: §0.1 (30,209 lines re-counted; 96,159 = src/*/*.c + cli/*.c) | FIXIND-11 (the "lib/" slip) |
| B3 | YES: §2 part table, F1 check | FIXIND-8 (P6 holds code but has no oracle) |
| B4 | YES: §3 (vm_stmt.h:48, :70-83, :100-104 checked) | none |
| B5 | YES (DOC): §9.1 | none |
| B6 | YES: §2 oracle column; interpreter PLAN | P6 "n/a" vs F3 (FIXIND-8) |
| B7 | YES in shape: §4.2 card, §4.3 | FIXIND-3, -4, -6, -10 |
| B8 | YES: §8 keeps and re-expresses the kind; REPORT now listed | FIXIND-9 (inventory); §0.1 still lists 5 of 6 kinds, but REPORT is not engine-named, so that is fine |
| B9 | NOTED: §7.1 | none |
| C1 | YES: §7.1 verdicts, §5.1 four ids (memfn_sites.h:308-316, .def:15-18 checked), §11.3 one body | none |
| C2 | YES: §7.2, §1.1 row 5 | none |
| C3 | YES: §4.1 `reentry`, §7.2, :14554 "SITE 2 OF THE THREE" checked | §1's family table still says choice is "the only frames" while ENUM and FIND push frames; that text is in rev 1 too, so it is not induced |
| C4 | YES: X15-X17 and 28 readers in §7.1 | FIXIND-8 (X15's card field, X16's owner) |
| C5 | YES: §7.2, §9.2 | none |
| C6 | YES: row 5 status, §5.2 | none |
| C7 | PARTLY: one rule and its spec readers (§6.3.3, tuning §3.1¶2, cli §1.11¶1 all resolve) | FIXIND-5 (ACCEPT, WORK) |
| C8 | YES: `exact` → `row`, meters → kinds, `Nfa.erased` owner | FIXIND-1, FIXIND-5(b) |
| C9 | YES: §2, one home P5, callsite_rows.c:1-14 checked | none |
| C10 | YES: TAGGED (dfa.c:1555-1557 checked), §5.2 HELD | none |
| C11 | YES: column in §6.2, D158 cited | FIXIND-7 |
| C12 | YES (DOC): §7.2, §11.3 | none |
| C13 | YES (PLAN): §4.2 demands, §4.3 unlock | none |
| C14 | YES (DOC): row 5, §7.2 | none |
| D1 | YES: §11.3 header, §11.2 baseline | none |
| D2 | YES: P-a folded into P-d after [VMREC] (b) | none |
| D3 | YES (PLAN): §11.2; emit_sweep.py IDENT_* arms exist (:2994-3010) | none |
| D4 | YES: §11.3 "Declined" | none |
| D5 | YES: §11.1 | none |
| D6 | YES: P-f consumer of CAND-SPAN, ENG-ISL cite, rulepilot gate | §11.3's "any planner pricing" collides with §6.2's priced cells (FIXIND-6) |
| D7 | YES: §11.3 order P-c, P-b, P-d | none |
| SEAM-8 | REJECTED; §6.3 keeps declared cut rows | none |

## PROBED-AND-HELD

- **Citations.** I sampled 58 file:line cites in the review tree. 56 hold as cited. Two hold with an offset or a path difference: `emit_dfa.c:8026` is `pf_vm_start_applies`, the comment block is at 8010-8025; `compound.c` is `src/core/compound.c`. These held: memfn.h:385-415/:414-415/:767-770; finder.c:398-404; emit_dfa.c:1415-1426, 5682, 5689-5695, 7060, 8283, 8316, 8714, 8013-8019, ~9790, 9870-9893, 9930, ~9944, 11280-11287, 13647-13650, 14554; emit_vm.c:3774-3777, 13005-13033, 10366-10441, 13259; nfa.c:643-648, 646, 759, 848, 955; possessify.c:10-47, 544-590; vm_stmt.h:48, 70-83, 100-104; memfn_sites.h:308-316; memfn_sites.def:15-18; callsite_rows.c:1-14; dfa.c:1555-1557; compound.c:248-265 (ONE row `split`); emit_iter.c:48-52; lane/p1build lmwalk.c:276-287; measures_table.inc 64 kind lines; the kit sets in §8; the spec anchors §3.2¶3, §5.1¶3a, §6.3.3, §11.6¶1-2, tuning §3.1¶2, cli §1.11¶1; captures_via_dfa_survey.md and emit_backends_notes.md exist.
- **Census numbers** (§10, §5.2): all 16 bench/corpus figures match scensus summary.txt (VM 86/2226, 24/629, 12/459, 12/453, 6/55, 10/438, 12/490, 14/409, 19/456, M6 10 + 8).
- **Read cycles the fixes add.** [LANDWALK-PRES]'s new read (PRESENCE reads the walk's rarity) walks over p1build's graph as PRESENCE→LOCATE(mask 0)→NEXT(walk bit)→FIRST→PRESENCE(walk)→LOCATE(walk: the walk row is transparent). It is acyclic in (slot, bits) states, so no new edge closes a cycle. B8's consumer-class derivation adds no read edge (it reads kind-row meters, which are plan constants). X17 `codes`: one table, already shared (held).
- **Compiles: 9**, under timeout 60, outputs in my lens dir: `a\Kb`, `(x)a\Kb`, `xa\Kb+c`, `\Ga(x)` (all hybrid "exact"), `(x)ab`, `(a)(b)`, `(\w+)@(\w+)\.com` (both budgets stamped), and `(?i:(a))\1` built and run on 3 subjects. Python `re` agrees on 4 witnesses.
- **Held fixes:** A5's row 1 text matches possessify's stated rule (U1/U2, non-nullable, lazy remainder conjunct on the disjointness arm, widening arms A/B). A6's maximality rule ("WITH its captures") plans `(a|ab)(c|bcd)(d*)` as split. D158's K102 exception is cited correctly. B8's six-kind table matches memfn.h's enum (REPORT included). The backref note's duplicate-name and unset answers fit A4's union-plus-ε, which is a valid superset.
- **Not a finding (suspected only, dropped):** whether the new TEST-ONLY levers (rows 2, 4, 6, 12, P-f) would each take a public flag bit. Main uses 56 distinct `PCREC_BIT`s and p1build adds 57. I found no spec for test-only levers, so there is no evidence either way.

## Summary

All 44 ruled ids are addressed in the cited sections. 3 are only PARTLY right (A4, A8, C7), and the fixes induce 12 findings.
Answer level: A4's backref superset is worded so that `(?i:(a))\1` "AA" would be lost by row G (FIXIND-12).
Bytes and stamps: A8 puts `\K`/`\G` into `Nfa.erased`, flipping today's exact hybrid window for `a\Kb` (FIXIND-1). C7's stamp rule counts ACCEPT, so nothing stamps "dfa", and no kind charges WORK (FIXIND-5). The new profitability cells decline windows by rarity where today's rule is an ordering, not a price (FIXIND-6).
Seam: `pos` lacks WINDOW/EXISTS/HIT (-2), row 5's split misfiles `finisher-dfa` (-3), card rule 2 rejects today's own start table (-4), and the give-up, X15/X16 and re-key gaps are -7..-10.
Of the 58 cites sampled, 56 hold exactly and 2 hold with an offset or path difference. All census figures match.
