# verify of round "iter" (SUBJECT 588714855, BASE 02f357b39); scratch /tmp/claude-1001/crit-iter/verify/
CONTRACT-1 HOLDS: libpcre2 G vs rx_next I, dfa engine, vm all OK. ` *|^x+` on "  x": G 0,2 2,2 3,3 / I adds 2,3. `|^x` on "  x" and "xx": I adds 2,3 / 1,2. `|(?:^a|b)` on "aab": I adds 1,2.
CONTRACT-2 HOLDS: -e utf8 -futf-check -fstartpos-guard=align 'a|', 61c3a980ff61, at=2: rc=-9 lo=2 while __bind_checks writes *pos only after success (art.c:318-322), aligned start was 4.
CONTRACT-3,4,5,6: not verified: doc.
EMIT-1 HOLDS: 3 repeats, deterministic (+-3 ins). `(a|b)*?\1?` L 10.286M->11.486M (+11.7%), M +14.1%, C +12.2%; `(?:(a)|b)*` L +10.1%, M +11.3%, C +10.6%; counts/sums equal.
EMIT-2 PARTLY: cost direction holds (L/N/K64 per match: `a*` 65.0/94.5/74.9; `(a*)` 75.0/100.0/66.9; `^`-free). But "even K64 stays 22-28% behind on VM rows" is false for `(a*)` (K64 66.9 < L 75.0); only tiered rows lag. Predicate/unlock part was SUSPECTED, unprobed.
EMIT-3 HOLDS: `^a|b` bxb L 78.0 N 100.0 K1 131.0 K4 99.5 K64 89.7 (identical to critic).
EMIT-4 HOLDS (small): `(a|ab)(c|bcd)(d*)` unit "abcd" (no trailing space): L 454.1 N 475.1 K4 471.8 K64 459.9 (+4.6% / +1.3%).
EMIT-5 HOLDS: K1-N = +32 (`a*`), +31 (`^a|b`), +23 (`(a*)`).
EMIT-6 HOLDS: .text totals `\w+` 2719->4623, `a*` 1435->4059, `(a+)(b+)` 4848->10296, `(a*)` 1705->5673; `\w+` one_local 468 (0x1d4), _next 524, _next_n 601 exactly.
EMIT-7 HOLDS: `(a|ab)(c|bcd)(d*)` L loop +120,084 ins / 40,000 searches = +3.0 per _search; M/C flat (+23 total). rx_search listing 19->23 insns.
EMIT-8: not verified (not in assigned list).
SLOT-1 HOLDS: emit_iter.c emit_step_own switch(t->own) with OWN_TIERED/_TIER_NOTE/run_state_bind(storage.frames...) text; selector `en->fwd_entries ? PCREC_FWD_EMPTY : pl->tiered ? OWN_TIERED : OWN` at emit_vm.c:13795 and :13935.
SLOT-2 HOLDS: vm_emit_retry order start_zero, run_state_init, notempty=1, then vars_resolve (emit_vm.c:13908-13913) vs _match_caps_run vars_resolve before start_zero ("K129: as _match", :13705).
SLOT-3 HOLDS: compile.c:353 gate `chosen!=DFA||part||!reports_empty`; emit_dfa.c:15730 `entry_emitted(NEXT)` + retry_ok; stamp :15006 own ternary; emit_vm.c:13930 `retry=reports_empty`; vm notempty field/guard keyed on reports_empty only.
SLOT-4: unprobed (>50-compile census).
SLOT-5 HOLDS: entries.c:194 pr_next_vm lists SEARCH_RUN; emitted vm2.subj.c: rx_search_run only called from _search rungs (467,477), rx__step calls rx__find (558).
SLOT-6,7,8,9,10: not verified: not assigned (SLOT-10 = doc/D174).
HOUSE-1: not verified (not assigned). HOUSE-2 HOLDS (same sites as SLOT-1). HOUSE-3 HOLDS: diff of dfa_dir_anchored (emit_dfa.c:9137) vs dfa_dir_retry (:13936) differs only in name strings, banner, one prose line.
HOUSE-7 PARTLY: `ent == PCREC_ENTRY_FIND` at emit_dfa.c:1894,1921,1954 and `d->n > 0 && ent != FIND` at :14178; find_body_shared forward-declared :1886, defined :1963. The "two derivations diverge" part is SUSPECTED, unprobed.
HOUSE-8 HOLDS: emit_iter.c:125-146 renders guard into StrBuf g, tests `g.len > 0 || g.cmt_dropped > 0`.
HOUSE-12: HOLDS as fact (stamp values "dfa-root"/"vm-guard", spec lists _ITER_RETRY as caller-visible stamp row, the branch spec's stamp table); the D174 ruling itself is the manager's.
HOUSE-13 REFUTED as a live bug: `--engine=dfa` on `${v}x` is refused ("requires the VM engine, which --engine=dfa excludes"), so the DFA site never sees vars; latent only.
HOUSE-4,5,6,9,10,11,14: not verified (not assigned).
CHK-1 HOLDS: iter_drv.c:491 `if (g < 0) v = "SKIP";` first; fail[] only consulted in later arms; printed as FAIL= on a SKIP line; run_iter_diff.sh:150 greps only ^(DIFF|REFUSED|CCFAIL|RUNFAIL|STAMPBAD).
CHK-2 HOLDS: run_iter_diff.sh:140,156 counts nskip and prints it; the floors are groups and retry cells only; `exit 0` at :102/:108 (missing-oracle path).
CHK-3 HOLDS: run_iter_diff.sh:153 `awk '$4 !~ /-futf-check|--step-budget/'` is per group flags; iter_drv.c:493 GIVEUP arm does not test utf8_ok.
CHK-4 HOLDS: iter_drv.c:472 `strcat(reach," n0fresh")` and :485 `" n0ended"` unconditional (n0bound at :481 is conditional on mI>=2).
CHK-5: unprobed (needs the sabotage matrix, not run). CHK-6..10: not verified (not assigned).
