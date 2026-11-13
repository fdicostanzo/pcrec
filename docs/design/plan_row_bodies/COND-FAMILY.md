# [COND-FAMILY] plan row body

Long-form notes moved out of plan.md (PL11 charter cap).

## 2026-11-12

- NOTE (2026-11-12, Frank): DFA captures are CHAINED to this family as one body of work: after the current sets (S1 rest, S2, S3 cover cap, S4, [FLAG-DEMOTE]) the manager writes ONE plan covering lookaround/predicates/intersection AND captures in the DFA ([ENG-TDFA]); Frank: "That would be cutting edge stuff." Evidence: docs/design/dfa_captures_research.md; studies/dfacap_spike/ (lane capspike).

- NOTE (2026-11-12, Frank: a formal evolving spec + a way to test X & Y, then predicates via callouts; chain PCRE2+callout oracle -> VM with callouts -> DFA vs VM AND oracle): spike studies/andspike (lane andspike) WORKS: PCRE2 with a callout enumerates X's ends in preference order; X&Y two ways agree; 64,200 regular-subset enumerations 0 disagreements; laws hold; predicates 12,400/12,400. Needs NO_AUTO_POSSESS; (?R) needs a guard; COMMIT/SKIP diverge; cost exponential (cap = inconclusive). Report F7: 8 semantics recommendations for the spec (X&Y reported match is NOT commutative under the leaning rule: 10.2% differ, a ruling for Frank); F9: production oracle ~100 lines in co_oracle.c; F10: callout corpus ideas. Second foundation section of the combined plan, beside [FACT-READS].

- NOTE (2026-11-12, D196 add. 2): mechanism first, syntax untethered: Boolean IR operators (intersection variants for exact span / lookahead prefix / lookbehind backward; difference; XOR) whose first clients are lookaround lowering and a `--compare X Y` equivalence tool; surface syntax is a separate optional unit.

- NOTE (2026-11-12, Frank: "a good series of plan items ... consider dependencies ... make each piece individually useful when possible"): the combined plan's FIRST deliverable is a dependency graph of plan rows, each stating waits: (checked: targets exist, no cycles), its standalone value if work stopped after it, its check/oracle, its first client; branches that can run in parallel named (Boolean mechanism vs DFA captures); a readiness critic round with a dependency lens before any build go. Sketch in the 2026-11-12 journal entry: foundation ([FACT-READS], span oracle, spec + rule coverage), mechanism (intersection node, --compare, lookahead lowering, lookbehind via reverse DFA, difference), captures (TDFA stage 1, then with lowered lookaround), predicates (VM callouts, then regular ones to DFA), optional syntax last.
