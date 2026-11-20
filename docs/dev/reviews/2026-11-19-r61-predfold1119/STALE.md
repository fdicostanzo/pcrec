# STALE findings — r61 predfold1119

## Findings


### STALE-1  CONFIRMED  severity: doc  effort: S
where: core_details.md § core/diagnostics/looped-compare, readings: 2nd item (R/subject/core_details.md line 1828); also rulings item 3 (line ~1822)
claim: the readings item still says "the warning stands as joint-loops (3) left it; whether it is still wanted is core/diagnostics/looped-compare/still-wanted (the predicate manager's ruling ...)". That piece was MERGED away (the `was:` line 1817 says so; no such tag in core.md or core_details headings) and the question was answered "remove the warning" (rulings item 1). The item asserts the withdrawn rule (warning stands) and points at a removed tag. Rulings item 3 calls joint-loops (3) "The owner's LAST word on the warning; it MOVES the 00:09 warning, it does not retire it", which the entry's own item 1 reverses (2026-11-19 later than 2026-11-17).
repro: grep -n 'still-wanted' R/subject/core_details.md -> 729, 735, 1817(was:), 1828; tag list built from `### ... [tag]` headings of core/library/parked.md (212 tags) lacks core/diagnostics/looped-compare/still-wanted.
blast radius: readers of the entry for what the warning's status is; pass-start-read entry (STALE-2).
proposed fix: rewrite 1828 as history ("at the time ... open; answered by looped-warning: remove") and qualify item 3 with "(until looped-warning, 2026-11-19)".

### STALE-2  CONFIRMED  severity: doc  effort: S
where: core_details.md § core/conditions/pass-start-read, rejected: last item (line 729) and history items (lines 733-735)
claim: rejected line says of the manager's looped-warning "the question is open (core/diagnostics/looped-compare/still-wanted)": a pointer to a removed (merged) tag, and "open" is false now (ruled: remove the warning). History line 735 (undated-status wording "whether it is still wanted is open ... The slugs looped-compare and looped-warning moved to those two pieces") likewise names two pieces where one remains; line 734 says the draft "withdrew compare.looped" with looped-warning, "rejected above", while the owner's later ruling is what actually removes it. Line 735 is dated history so lower weight; line 729 is a current-state rejected: item.
repro: sed -n 729p / 733,735p R/subject/core_details.md
blast radius: pass-start-read's own readers; the slug looped-warning now homed in looped-compare.
proposed fix: line 729 -> "... withdrawn by the manager, then ruled removed by the owner (core/diagnostics/looped-compare)"; add "(merged since)" to 735.

### STALE-3  CONFIRMED  severity: doc  effort: S
where: library_details.md § lib/builtin/enumerate evidence: (line 25) and § lib/builtin/enumerate/class-value evidence: (line 44); core_details.md § core/arrays/class-order evidence (line 1075, labelled "earlier")
claim: predloop_model.py at the freeze encodes the WITHDRAWN descending rule. Run: ( cd R/tree && python3 -I docs/dev/lanes/predloop_evidence/predloop_model.py ) -> "20 checks, 9 failed: EXclassorder EXsub EXtwo EXlazy EXfirst EXnest EXbounded EXenumclass EXpos" (rc=1). Entries cite these as current support: library_details:25 "predloop EXenum, EXenumclass, EXpos" (EXenumclass, EXpos FAIL; the model prints enumerate(/\d/) = ['9',..,'0'], enumerate(/[abc]/) = ['c','b','a']); library_details:44 "predloop EXpos, EXwplus" (EXpos FAILS; EXwplus passes only because it prints the descending list `(?:10|9|..|1)`); core_details:1075 lists predloop EXclassorder..EXbounded under "earlier" (7 of those fail) but the word "earlier" is the only flag, and 25:/44: carry no such flag. predasc at the freeze: "24 checks, 0 failed" (rc=0) and covers the same names ascending.
repro: as above; also cited-but-passing-for-the-wrong-reason: predloop EXwplus (core_details 991/994, library_details 43/44), RB (core_details 1041) compare the descending loop against longest-first.
blast radius: any reader treating an evidence: line as "re-runnable support"; the lint is green so nothing guards it.
proposed fix: drop predloop from evidence: of the current-state entries (25, 44, 994, 1041) or mark "superseded by predasc"; or retire/refresh predloop_model.py so it is green.

### STALE-4  CONFIRMED  severity: maintenance  effort: S
where: predloop sabotage claims ("predloop sabotage sN caught") in core_details 991/1080/1086, library_details 17/33
claim: with predloop at 9 baseline failures, a plant whose target check is one of those 9 cannot be told from baseline. Plant list vs baseline (R run, PREDLOOP_SABOTAGE=sN): s1 (target EXclassorder), s2 (EXsub), s3 (EXfirst), s4 (EXlazy), s5 (EXnest), s11 (EXenumclass), s12 (EXpos), s13 (EXbounded), s20 (EXtwo) each end with its target already in the 9; the other-check changes they cause are incidental (s1 adds EXmul RB; s5 adds NOTHING: "9 failed: EXclassorder EXsub EXtwo EXlazy EXfirst EXnest EXbounded EXenumclass EXpos" identical to baseline; s12 likewise adds nothing). So core_details:1086 "predloop EXnest ... sabotage s5 caught" and library_details:33 "predloop ... EXpos ... sabotage s12 caught" are not true at the freeze: s5 and s12 are NOT caught (same 9-failure line as no plant). s4, s14, s3 differ only via other checks.
repro: for s in s5 s12; PREDLOOP_SABOTAGE=$s python3 -I predloop_model.py | tail -1 -> identical to the unsabotaged tail line.
proposed fix: remove those caught-claims or cite predasc's s26/s12 instead.

### STALE-4a  CONFIRMED  severity: maintenance  effort: S
where: refinement of STALE-4
claim: of the predloop "sabotage caught" claims, those at core_details 1080/1081/1085/1086/1088 and library_details 33 are in history items quoting the earlier text verbatim (so labelled as past); the two that are not true at the freeze are s5 (core_details:1086, plant changes nothing: same 9-check failure line as no plant) and s12 (library_details:33; likewise identical to baseline). Live (non-history) predloop claims that DO hold: core_details:1040 s8 (adds EXlift, EXplus, ..), library_details:17 s10 (adds EXenum), core_details 991 s7 (history).
repro: PREDLOOP_SABOTAGE=s5 / s12 predloop_model.py | tail -1 == unsabotaged tail -1.
proposed fix: as STALE-4.

### STALE-5  CONFIRMED  severity: maintenance  effort: S
where: predasc sabotage s6 (core_details:1072 "predasc EXeq, sabotage s6 caught")
claim: the plant is caught (EXeq EXmul fail among "4 failed: EXtwo EXnest EXeq EXmul") but the run takes 2m02s (user 1m59s), over the 120 s bound COMMON/the lane's own convention gives a reviewer; under `timeout 100` it is killed (rc=124) with no verdict line, so a reviewer using the stated bound sees "no output", not "caught".
repro: PREDASC_SABOTAGE=s6 timeout 100 python3 -I predasc_model.py -> rc=124; with timeout 280: rc=1, 122 s.
proposed fix: note the runtime in the details entry or make the unsorted-duplicates plant cheaper.

## PROBED-AND-HELD
- Withdrawn-rule terms grepped over all six files (core, library, parked, three details): descend (core/library/parked 0 hits; details: all ~25 hits are verbatim "Statement before"/rejected/history or quoted owner words, each labelled replaced); longest first / longer is tried (core 252 is the parser "read longest first"; library 636-648 sort pieces are the user-sorts rule; details hits all history/rejected/readings-of-candidates); "no order" (core 735 is the ruled "no PCRE order, nothing disagrees"); "over the product of the operands" (1 hit, history 997); "its own literals" (1 hit, rejected 525); pcrec.compare.looped / looped (core 1293 heading only; 0 in warnings table); class-positions, class-index, hole-export, still-wanted, looped-warning as tags (0 in core/library/parked bodies; details hits all `was:`/history except STALE-1/2).
- Pointers: 212 tags in core/library/parked headings, 212 details entries, 0 missing, 0 orphan; every needs:/see:/by: line in the three base files resolves (0 BADREF). Non-resolving tag-like tokens in details: only the four still-wanted lines (STALE-1/2) are live; the rest are group prefixes (core/arrays, lib/builtin...) or `was:`/history of merged tags (class-index, class-positions, hole-export, core/arrays/enumerate).
- Heading status/date vs details: all 6 changed pieces (labels-vs-captures, export, lift, class-order, bare-condition/labels, looped-compare) ruled 2026-11-19 with a ruling item or history of that date; enumerate/class-value dates consistent with details.
- predasc at freeze: 24 checks, 0 failed (rc=0). All 26 plants run: each target check fails (s1 s2 s3 s4 s5 s7-s26 within 1-15 failures; s6 caught after 122 s). Single-check catches: s12 (EXpos), s14-15, s17-18, s21-25.
- predloop at freeze: 20 checks, 9 failed (STALE-3). Of its 20 plants, those not hidden by baseline failures are caught: s6 s7 s8 s9 s10 s14 s15-s19(partly) ; s5 and s12 are not distinguishable (STALE-4).
- Counts: 19 core/library details entries read for evidence lines (~33 predloop mentions, 4 classed as current-support citing failing checks); 0 differing runs needed (no match claims made).

CRITIC COMPLETE
