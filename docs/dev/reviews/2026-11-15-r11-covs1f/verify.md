# verify

## CHECKS-2
HOLDS. Copies in verify/ciroot (tests/mech symlinked), all-ESTIMATE table verify/allest.tsv. Plants and rc:
- unmodified measured_mech.tsv + all-ESTIMATE table: UNWEIGHTED ... S221 etc, rc 1 (loud).
- col 6 `measured` -> `apportioned` everywhere: PASS 90 shards, rc 0.
- measured file with only `#` header lines (no rows): PASS, rc 0.
- measured file missing: `awk: cannot open ...` on stderr, then PASS, rc 0.
Callers: grep of tests/ scripts/ Makefile .github finds only cloud_kinds.tsv:32 (`bash tests/ci/cloud_mech_check.sh {selector}`, no --selftest) and CLAUDE.md prose. --selftest is not run by the gate.
## CHECKS-3
HOLDS. emit_sweep prints (scripts/emit_sweep.py): :2236 `TAG FLOOR side a|b: tag n < floor` (sets ok=False; the `tag floors: N pinned, all held` line at :2243 is printed only `if ok`, so a failing tally prints NO `tag floors:` line); :2200 `REACH FLOOR VIOLATION: ...`; :3921 `DELIVER WITNESS FAILURE: fixture(s) did not produce: ...`; :4073 `emit_sweep: DONE rc=1 (uncaught exception, traceback follows)`.
job_sweep header (lines 7-9): "every tag floor held, ... Anything else (a mover in c-vm, ...; a failed floor; no DONE line) is red here."
sweep_verdict.py greps only `tag floors:` lines lacking "all held", "emit_sweep: DONE" (substring, matches the uncaught line), `DELIVER witness: OK`, streams and movers; it ignores SWEEP_RC.
My own reports (verify/sv/*.txt: 11 streams movers=0 asymmetric=0, SELF-CHECK PASSED, REAL RUN, DELIVER witness: OK, DONE line, header-only movers file), run with SWEEP_RC=1:
- clean: rc 0 (right)
- + `  TAG FLOOR side a: yes 5 < 9`: rc 0 (wrong)
- + `  REACH FLOOR VIOLATION: 5 < floor 90`: rc 0 (wrong)
- DONE line replaced by the uncaught-exception line + traceback: rc 0 (wrong)
- + `DELIVER WITNESS FAILURE: fixture(s) did not produce: ['f1']` beside `DELIVER witness: OK`: rc 0 (wrong)
## CHECKS-4
HOLDS. predict.py:45 lists `"run_pin", "finisher-dfa"` in ROUTE_ROWS. `build/pcrec --features all --emit-facts=byte,utf8 --pattern P` over abc, a+b, (a)\1, foo$, x[0-9]+Qz: grep -c finisher-dfa = 0; the distinct column-2 row names (cover, end_window, run_pin, RX_DFA_*, ...) contain no finisher-dfa. In src/ it is spelled only at src/gen/known.c:449 (`{ "C1", "finisher-dfa", "route", cc_finisher }`, a conjunct table) and src/gen/lmwalk.c:124,277 (conjunct name). Dead allowlist entry.
## FIXIND-1
HOLDS (as a tension; the abi clause is advisory-worded). docs/spec/facts_listing.md:27 [1¶1]: "It is not part of the generated artifact, so it has no `abi` number." Line 144 [4.5¶2]: "...the names are advisory, like a reason's: diagnostic words of this debug listing, not caller-facing names, and they may change with the abi (`match_api.md` §6¶17)". match_api.md:1809 [6¶17]: "`abi` is the version of the emitted SCAFFOLDING as a whole (D76) ... It is `108` on every artifact pcrec emits today". So [4.5¶2] ties listing ids to an abi that [1¶1] says the listing lacks; §6¶17 defines the artifact's abi, not the listing's.
## FIXIND-2
HOLDS for producers-disagree, PARTLY for C3-C14. docs/design/kit_proof.md carries unmarked (no superseded/rewritten tag) mentions after the C8 row (line 232) was rewritten to "its `exact/producers-disagree` detail are gone": line 101 (review table m2: "C8's `why` splits into `exact/machine-inexact` and `exact/producers-disagree`. The trace build asserts 0 of the latter"); line 966 ("C8 would then read `exact/producers-disagree` on every such body, which the trace build asserts never happens"); lines 1292-1293 ("`exact/producers-disagree` (the two producers' `S_d` differ, which the trace build asserts is 0)"); line 1141 (S1149 sabotage row, "C8 `exact/producers-disagree`"). `grep -rn producers-disagree src/` finds nothing: the detail does not exist in the build. C3-C14: line 221 ("the other notes still cite C3-C14 correctly") and line 114 ("C1-C14 order") are id-stability / review-history statements, still true (ids stable; C15 added); not stale in substance.

VERIFY COMPLETE
