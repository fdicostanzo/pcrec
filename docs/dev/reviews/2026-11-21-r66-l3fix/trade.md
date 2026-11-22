# CRITIC TRADE: l3fix (review r66)

## Findings


### TRADE-1 (CONFIRMED, doc, small): run_cpset_structure.sh states a move the built tree does not make
tests/codegen/run_cpset_structure.sh:1130-1136 (added in the delta) records "`(?<=foo)bar` EMITTED_BYTES 38505 -> 39608 (+1103) ... RX_REQ_RUN "626172@0" -> "666f6f626172@3", RX_REQ_WHY "dominated" -> "emitted", RX_REQ_HANDOFF "none" -> "-3", RX_RUN_WORDS 3 -> 4". Repro: `kit/pc subject --features all -p rx -o - --pattern '(?<=foo)bar'`: RX_REQ_RUN "626172@0", WHY "dominated", HANDOFF "none", RX_RUN_WORDS 3, 38505 bytes (script's `$(..)` count; base and subject both 38506 by wc -c, identical). The manifest m5_stage1_stamps.tsv stays 38505 (35d352129 restored it), so the comment contradicts the pin it annotates. Those -3 figures hold only under --engine=vm. Fix: delete or restate the hunk (BASE value kept; abi digits only). Blast: none (comment).

### TRADE-2 (CONFIRMED, doc): "owner's 2026-11-20 lean" has no committed record
span_arms.md:2157 and plan.md ([L3-CONS-REENTRY], line 311 at the freeze) (+ [L3-CONS-REENTRY] refs) cite "the owner's 2026-11-20 lean that graph-based re-entry waits for a general rx/graph manipulation layer (docs/design/plan_row_bodies/REQ-LOOKAROUND.md)". `git grep -i 'rx/graph|graph-based re-entry|manipulation'` at SUBJECT finds only the two citing sentences; REQ-LOOKAROUND.md (73 lines, unchanged vs BASE) has no 2026-11-20 text. The cited record does not contain the quote. Fix: land the owner's words (verbatim) in that file or cite the real home.

### TRADE-3 (CONFIRMED, doc, small): "D191 addendum 1(b)" is cited for a rule it does not state
span_arms.md ~2133: "THE PICK RULE (D191 addendum 1(b): an unpredicted performance mover is fixed before landing)". decisions.md D191 item 5, Addendum 1(b) (owner, 2026-11-18) reads: "After the build, a result that differs from the census's expectation is a reason to reassess, not to push on." "Fixed before landing" is the manager's gloss, not 1(b)'s text (and 1(b) is the manager's RECORD line, not the owner's words). Fix: quote 1(b) or say "reassess".

### TRADE-4 (CONFIRMED, design/record): the speed/coverage given up by the pick rule has no ruling of record
What the delta gives up vs BASE-with-L3: on the default route L3's lookbehind-bytes-in-the-search (BACK run) is NOT used wherever a bounded consumed run exists (`(?<=foo)bar`, `(?<=qz)ab`, `(?<=foo)bar(\w)\1`...): reproduced `(?<=foo)bar` default stays "626172@0", K 0; BACK only under --engine=vm/-fno-req-handoff, `(?<=foo)` and `(?<=xyz)a+xyz` (reproduced: req_whole_run 78797a61, K -3). Against BASE: nothing lost (reproduced byte-identical but abi digits for `(?<=qz)x?a:`, `(?<=x)qzjv[a-z]*\d`, `(?<=a)\Kb`; 3 cmp pairs). The trade (L3 feature narrowed to avoid a x10.3 loss) is attributed to "review r65 rulings (manager, 2026-11-20 19:25)" (span_arms:2125); the only quoted rulings, R-1/R-2 (span_arms ~2169-2171), concern the DECLINE and the measurement question, not the pick rule; decisions.md at SUBJECT has no entry. Judge = manager, record = a sentence in span_arms only, no file:line ruling. R-1/R-2 verbatim check: record denied (l3feat rulings file), not checked. Fix: one decisions.md line (or owner.md question) stating the narrowing and its un-done trigger ([L3-CONS-REENTRY]).

## PROBED-AND-HELD
- Pick-rule code vs facts_listing §4.1.2¶8 vs tuning §2.41¶1/7a/8b vs match_api: rb_top_back_displaces (`!fwd_reentry || best->n==0 || (lo<hi && best->off>=UNBOUNDED)`) matches the ¶8 sentence; fwd_reentry = engine!=VM && !NO_REQ_HANDOFF matches; facts listing examples reproduced on 4 spellings (`(?<=foo)bar` default 626172/0, --engine=vm and -fno-req-handoff 666f6f626172/-3, `(?<=foo)` 666f6f/-3, `(?<=xyz)a+xyz` 78797a61/-3); match_api RX_REQ_HANDOFF "-3" under --engine=vm reproduced.
- Pins: cpset manifest 38505 reproduces; d3_floor deltas (+1/+22/+1/+23, pop +16) consistent with the recorded census claim (census not re-run); FILEPIN f487fbd0f is an ancestor and the last src commit (no src after it); five plan rows each name a trigger.
- Emitted comment "after the start of its": abi is 110 at SUBJECT (109 at BASE); the delta changes emitted text on top of the abi the branch already bumped, unlanded, so one bump (109->110) covers branch vs BASE; FILEPIN (B) pins to abi 110 and no src moved after it. Held.
- Not reproduced: span_arms instruction-count table (perf counts not run; do not time).
- Cases: 4 cmp pairs + 5 facts/emit probes. Compiles: 16 of 200. Longest witness `(?<=x)qzjv[a-z]*\d`.

CRITIC COMPLETE
