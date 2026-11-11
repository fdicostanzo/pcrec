# closeb — close [REGIME], park the five quiet optimization rows, owner-waits view (2026-11-10)

## STATE AT HANDOFF

STATE: delivered (branch lane/closeb, built on lane/closea). Validation COMPLETE, no runs owed. Green in the worktree: `make test-plan-lint` (339 rows, 0 violations; selftest 45 plants, 18/18 rules, 4 new `waits: owner` plants under PL10), `make test-doc-lint` (7 checks), `bash tests/doc_lint/run_doc_index.sh` (DONE rc=0), `make strict`, `scripts/entry --selftest` (69 checks, 0 failures). `scripts/entry --work | head` prints `## waiting on the owner` first.

### Owner-waits view (tooling)
- Field: `waits: owner — <the question in plain words>` (any row). `scripts/plan_lint.py` PL10 checks the shape (`owner — ` then at least 10 characters); plants: no question, no dash, empty question, question too short. `scripts/entry --work` lists these rows first, in their own section, and not again under their state. Selftest fixture row FF-6 plus an order check. Policy paragraph "Owner waits" in plan.md, doc_format.md, doc_profiles.py work text and tests/plan_lint/CLAUDE.md updated.

### [REGIME] verification: CLOSED as superseded (plan_completed.md "Completed 2026-11-10", after the closea rows)
Verdict: superseded, not still the plan. Evidence: the table it was to replay held forms V1/A1/A3 chosen by hand-fitted thresholds. The kit's B4' withdrew V1/R5/R0 on 2026-10-21 (the walk is every set FIND's default, closed in walk_vs_v1_record.md; [MEMFN-REGIME] holds the way back). D186 (2026-11-02) replaced "fit a table, judge by replay" with "every choice row carries per-regime evidence from job 588 style runs", priced picks come from [MEASURE-SET] sets (span_pick stages 1-2, zen4-grid3@1 692ec83b7), D188 prices the SIMD levels. span_pick.md never cites the replay evaluator.

| chartered piece | where it lives now |
|---|---|
| (1) [REGIME-CORPUS] subjects + questions | DONE, closed by closea (b39a69c2e) |
| (2) [REGIME-EVAL] replay evaluator | SUPERSEDED, closed here (design only, rev 2.4, never built); the replay-judge idea survives as [TABLE-JUDGE] (status line updated); J1 population = the corpus |
| (3) [REGIME-TWIN] dispatch timed | SUPERSEDED, closed here: span_pick stage 3 times each row (588-style run on every arm); the grid harness became [MEASURE-SET]'s method |
| (4) D6 rounds on designs/results | rides each row's own review; no separate piece |
| (5) prerequisites: [FINDALL-NEXT] (D165), [MEASURE-SET], kit R17-b' | each its own live row; R17-b' B1-B3b landed (0ec28bddd, d18cee085), later B-steps are the kit's own ledger |
| (5) [REGIME-LANDINGS] | NO other home: filed Deferred with a trigger ([MEMFN-REGIME]'s landing regime, or a priced span_pick row reading E; requests.md R-19 site_kind gate) |
| (6) R17-b'' with F4/F7 + D165 parity gate | kit-owned (kit ledger, build go 2026-10-21); the iterator side is [FINDALL-NEXT] I2/I3 |
| (7) official verdict (Zen 1 + bench run) | [OPT-SIMD]'s review line (D144 add. 4) |
Not verified by running anything (rows and docs read only); the call that EVAL/TWIN are not worth keeping alive rests on the above, and either can be re-filed from plan_completed.md.

### Parked (moved to Deferred, STATE:deferred, new status + trigger; landed parts kept in the status)
| row | landed (kept) | NOT started | trigger |
|---|---|---|---|
| MATCH-SPLIT | STEP-0 survey, COMPOUND-client design (compound.md rev 2.2, cb1b9e68f) | the client build | a bench cell or census of multi-pin-class patterns at rank, or OPT-REVEND anc-tail fires |
| ENTRY-TABLE | E0, E0c, E1 (7c0a90479, abi 80), ATTR-TABLE | E1-prime | a measured size/time difference for a preset cell, or first VM-bodied/find subject |
| PRIOR-COST-UNIFY (was blocked) | design rev 2 (bf460fa33), input-formula report | the primitive | a fifth member of the prior-reading admission family, or the kit's window unit re-scopes it |
| ARTREV | S0 harness, pilot (15/22 WIN, gate MET) | the FULL RUN | OPTLOOP selection short of measured candidates, or Frank's go |
| ENG-TACTICS | charter + evidence | tactic census | freeze lifts and Frank's go (rev-inner's trigger fired 2026-10-27, held) |
[COMPOUND] became `ongoing` (why/review given; its two clients are parked); [OPTLOOP] unchanged (its charter does not name these as children).

### Owner-waits list with verdicts
Marked `waits: owner` (really waiting on Frank): [VLOOKBEHIND] (STALE part fixed: §13 Q1/Q2 were already ANSWERED 2026-11-06; what remains is the stage 2 build go, after a re-check critic round), [CONDITIONALS] (design-lane go, four questions in condinv_report.md), [TRAIL-CKPT-PRUNE] (is +1.6 to +4 % above his ~3 % bar), [CLI-OUTKEEP] (build go), [FINDINGS.B4] (trigger fired, dated status line added, build go).
Not marked, verdict:
- [RUN-POS-SET]: waits on the kit's R-38 Part D first; the go comes after, so it is not yet an owner question. Left.
- [INLINE-C] "gate is Frank's word": already given; stage text. Left.
- [LANDWALK] trigger "manager's check of rev 2, then Frank's build go": STALE (stage 1 merged dc6a40dfb, abi 95); needs a status restatement, outside this brief; children LANDWALK-CARD/CENSUS triggers say "stage 1 opens" and are stale too. Flag for the manager.
- The ~100 Backlog/Boonies/Candidates rows saying "starts on Frank's word" ([PCRE2-GAPS-TBD], [DELTA-JUDGE-UNIFY], [DEBUG-CHECKS], [DECISION-LOG], [STREAM], [ENG-TDFA], [ENG-LOOK], [DFAREC] "or Frank's go", ...): standing wording of those tiers per the Policy, not a pending question; marking them would drown the section. Left.
- The ARTREV "suggestions await Frank" text is gone with the rewrite (stale since the pilot).
