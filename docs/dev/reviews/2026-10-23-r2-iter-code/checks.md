# CHECKS lens: check adequacy + trade audit (BASE 02f357b39 .. SUBJECT 58871485)

Read-only. Nothing built or run; every CONFIRMED below is by reading the SUBJECT tree
(worktrees/crit-iter). The matrix and the suites were not run.

## (a) Check adequacy

### CHK-1  SKIP verdict masks the state-machine arms (CONFIRMED by reading; answer/coverage; small; findall + gstart + entry-shape)
tests/findall/iter_drv.c:491-496: the verdict chain tests `g < 0` ("SKIP") BEFORE `fail[]` is
consulted. `fail` already holds sticky / endset / nullcaps / poison / dirty / info / at1 / N* / X / G1 / GN / N0
failures by then; they are printed as `FAIL=` on a line whose verdict is SKIP.
run_iter_diff.sh:150-151 fails only on `^(DIFF|REFUSED|CCFAIL|RUNFAIL|STAMPBAD)`; run_gstart_diff.sh
(`OK*|SKIP*) ;;`) and run_entry_shape_identity.sh (`^(OK|SKIP)`) accept SKIP outright.
g < 0 happens when libpcre2 refuses the pattern (`re == NULL`) or any `pcre2_match` returns < 0 mid-loop
(loop_G returns -1: match limit, depth, bad option). Those are exactly the hostile cells, and the arms
that need no oracle (sticky, endset, poison, dirty, info, at1, nullcaps, N0) are the ones lost.
Who chose the input: nobody; the masking is by construction. Fix: evaluate `fail[]` first (`DIFF` wins
over SKIP), or print arm failures as a separate verdict.

### CHK-2  SKIP is counted, never bounded; a missing oracle prints PASS (CONFIRMED by reading; coverage; small)
run_iter_diff.sh prints `skip=$nskip` and floors only groups and retry cells. A cells.tsv pattern that
libpcre2 refuses (typo, or pcrec-only syntax under `--features all`) turns its whole group into SKIP rows and the run is green.
Separately: no libpcre2 -> run_iter_diff.sh `exit 0` after a stderr SKIP; run_findall_tests.sh ignores the
status and prints `PASS: test-findall` / `checks passed: 1`. The matrix arm catches the SKIP text
(`any_skip`), `make test` does not. Same for the ASan half (`SKIP: ... ASan cells did not run`, then PASS).
tests/CLAUDE.md-level convention for PC-3 is "SKIPS loudly"; here the trailer says passed.
Fix: a SKIP ceiling (fraction of cells), and `checks passed: 0` plus a SKIP trailer line on a missing oracle.

### CHK-3  GIVEUP is excused per GROUP, not per subject (CONFIRMED by reading; answer; small)
run_iter_diff.sh:141 `awk '$4 !~ /-futf-check|--step-budget/'` excuses every GIVEUP in any group whose flags
carry either flag. iter_drv.c:493 classes GIVEUP as `rc < 0 && prefix_of(oI, oG)` without asking whether the
subject is ill-formed (ILLFORMED is tested only afterwards). So a give-up on a WELL-FORMED subject inside a
`-futf-check` utf8 group (the 252 utf8 cells) passes. Count of such cells is printed (giveup=) but has no ceiling.
Fix: GIVEUP under -futf-check only when `!utf8_ok(s,n)`; under --step-budget only on the named cells.

### CHK-4  two reach tokens fire unconditionally (CONFIRMED by reading; maintenance; trivial)
iter_drv.c:~457 `strcat(reach," n0fresh")` and `" n0ended"` are appended on every subject regardless of
what the cell did. REACH_NEED lists both, so the "met on >= 1 cell" test for S1313's FRESH/ENDED witness is a
liveness argument, not a value argument. (`n0bound` is conditioned on mI >= 2, which is right.)

### CHK-5  22 new sabotage rows: anchors good, detection unrecorded, reach left to the suite (SUSPECTED; coverage; medium)
Checked: for all 20 rows S1297-S1314, S1319, S1321 `SAB_BEFORE` occurs exactly once in `SAB_FILE` at SUBJECT
(count 1 = SAB_COUNT 1 each). Not shown by the diff: a verdict. Every new row's `SAB_DOC_FIGURE` is
"Owed: the lane queued this row ... Exact re-run command"; only S1300's header cites a run (the 621 run, which
read UNDETECTED until its witness cells were added, a good sign the author runs these). None declares
`SAB_REACH`/`SAB_REACH_POP`, so the matrix's UNREACHED verdict is unavailable; reach lives in iter_drv `R=`
tokens and exists only for S1309-S1314/S1319/S1321 (n3m4, split, gumid, done63, vmcaps2, g1, g2, gn5, n0*).
S1297-S1308 and S1300 have no reach token: their witness is "some cell in cells.tsv"; S1300's own history shows
the failure mode (no cell put a stray byte after a non-empty match). Confirm by `bash tests/mech/run_sabotage_matrix.sh S1297 ... S1321`
(ledger of verdicts) before landing; the figure must be recorded.

### CHK-6  residual-twins check: single-arch reading, one plant, one sabotage row (SUSPECTED; coverage; low)
run_residual_twins.sh reads `R_X86_64_PLT32|PC32` from `objdump -dr`; on another arch/format the awk emits
nothing, so the only loud failure is the plant (good control, but it plants `rx__valid_upto` only; the
`next_pos`/`var_valid` twin spellings rest on the same awk). Sabotage S1304 covers only the -futf-check prologue's
valid_upto call. MIN_PAIRS=8 over 7 cases is a "did someone delete a lot" floor. tests/memfn/c4_allowlist.tsv
gained a row naming the R_X86_64_* tokens as an arch exemption: the check is x86-only by admission.

### CHK-7  residual-call counter now exempts the iterator step (SUSPECTED; maintenance; low)
run_codegen_tests.sh `caller(f)` treats `rx__step` like `main`: residual calls inside the iterator step are not
counted ("the documented find-all protocol run inside the artifact"). That is a population nobody counts; a
future extra `next_pos`/`valid_upto` call in the step is invisible to the exact-count table. The exact table
values were hand-raised (`residutfdfa valid_upto 2->3`, `residutfvm 3->4`) for the bind check: exact, so fine.

### CHK-8  global.rxt expected values share a source with the iter differential (CONFIRMED by reading; coverage; low)
gen_global.py writes `mg` counts from iter_drv's `G=` field: the same libpcre2 loop the differential holds `_next` to. The
independent control is python `re.finditer` (verify_rxt), which covers C3 PASS +1188 of 1404 lines; 216 lines
(15%, `C3_SKIP_PCRE2ONLY`) are blocks demoted whole to `# pcre2-only` when python cannot compile OR DISAGREES on ANY ONE subject.
So a python disagreement is absorbed into a label rather than reported (which subject, why). Also dropped silently
at generation: subjects with `G == "-"` and groups pcrec refuses (`continue`). The mg line compares a COUNT only;
span errors with the right count are caught by run_iter_diff alone. The C3_* / CENSUS_* pins are "re-measured from this
check's own output" (the independent awk reconciliation in rxtsource still stands).
Positive: iter_diff's `L` control and the S1300 stray-byte cells; encseam's `nlossy_iter == 2*nlossy` is an exact counted population.

### CHK-9  mover census: not wired, any dfa-root size move is "explained" (CONFIRMED by reading; maintenance; low)
tests/findall/mover_census.py is not invoked by make test-findall (needs OLD and NEW binaries). Its verdict
`moved-retry-root` accepts a counted-size change of ANY magnitude when the new artifact stamps dfa-root, and it
compares only the "(M of code)" counted size, so the +8 KB total growth (see T1) is outside what it measures.

### CHK-10  encoding-identity excision widened (SUSPECTED; coverage; low)
run_encoding_checks.sh adds excised classes `forwarder` and `bind_checks` and widens K73_ZERO_RE (`ctx.pos`) and
VARVALID_CALL_RE (`rx__?var_valid`). Each widening removes text from the byte-compare. The new keys are printed as
`EXCISED k=n`; I did not see where the counts are pinned. Confirm: grep run_codegen_tests.sh for an expected `forwarder=`/`bind_checks=` value.

### Retired rows
No sabotage row deleted. Re-anchored with "same plant, same detector": S02, S05, S504, S701, S891, S902,
S1126, S1151 (S1118 comment only). One fixture retired: partlayout `held-compound` (compound class
`/held` under P2/P3) replaced by `compound-inline`; see T4.

## (b) Trade audit (old -> new; moved by; gives up)

| # | pin | old -> new | moved by | gives up | judged in the diff? |
|---|---|---|---|---|---|
| T1 | tests/codegen/manifests/m5_stage1_stamps.tsv EMITTED_BYTES, all 12 rows | e.g. `a` 21,348 -> 29,294; `(a(?1)?b)` 33,058 -> 42,247; +7,934..+9,189 (+26%..+41%) | iterator scaffold on every artifact whether or not the caller iterates; sequence in run_cpset_structure.sh: I1 +6,429, -145, I4 +3,645, itertri +703..826, nomacro -2,686 | SIZE (emitted bytes, and gcc compile input; compile time not measured in the diff) | NO. D171 accepts the ~2 ns fixed TIME cost only; it does not mention bytes. The pin comments record what moved, never that +8 KB per artifact was accepted. Excluding the scaffold from the code cap (learnings: cap reads CODE bytes) is a design choice that hides it from the caps, not a price judgement. |
| T2 | tests/resource/run_resource_tests.sh `a{5,25000}` rescue bytes | 762,954 -> 766,980 (+4,026) in three re-pins | I1 +2,662, I4 +691, itertri +673 | size (0.5%, same scaffold constant) | Recorded per re-pin, no acceptance statement; consistent with T1. |
| T3 | tests/codegen/run_n1_budget.sh auto-route mandatory-machine spend | trips at 3,500-4,000 -> 5,999 (+50%); raised test budget 5,000 -> 8,000 | a THIRD mandatory machine (the notempty retry DFA) charged against `PCREC_MAX_AUTO_DFA_ELEMS` | COVERAGE OF THE DFA ROUTE: a nullable pattern near the 30M auto budget now falls back to the VM earlier, up to ~1.5x sooner by this witness; speed (VM) for those patterns | Stated in limits.md §3.3.4 (spec hunk present) and re-bisected, but no decision row prices it. Judge: is a retry machine that is paid for by every nullable pattern, whether or not the caller iterates, worth charging against the auto budget? |
| T4 | tests/partlayout/fixtures.tsv `held-compound` -> `compound-inline` | expectation `compound=inline/held` (P2/P3) -> `compound=inline` (P5) | a compound part's label table moved to its own noinline `__find`, so `_next` is a second caller and the single-caller constraint rows stop applying to compound | COVERAGE: no CLI input reaches a compound-class constraint row (fixture comment admits it); `/held` is witnessed by `constraint-*` rows only. Also a layout change (parts copy, `__find` always_inline into the shell) whose size effect is not measured here | Documented in the fixture header; no price. |
| T5 | tests/codegen run_n1 / residual counts `residutfdfa` 2->3, `residutfvm` 3->4 | +1 residual `valid_upto` call each | iterator bind check | size (one call site) | Recorded in a comment, exact count kept. |
| T6 | tests/ci/shards.tsv | new `test-findall 1 40` | ESTIMATED (20 s dev box, not runner-measured) | CI time (~40 s) | Marked ESTIMATED. |
| T7 | tests/findall/run_findall_tests.sh ASan half | MIN_GROUPS 20 -> 10, MIN_RETRY 25 -> 10 (env override), ARMS `auto vm` | subset run under ASan | coverage: no explicit --engine=dfa arm under ASan | Subset by design; the full arm set runs un-instrumented. |
| T8 | startset manifest_s2_vm_forced.tsv | +13 rows | new global.rxt blocks | none (additive) | "no existing row moved" stated. |
| T9 | rxtsource CENSUS/RUNSH/C3 pins | files 292->293, blocks 5,976->6,038, lines 72,572->73,976, C3_PASS 20,744->21,932, C3_SKIP_PCRE2ONLY 19,157->19,373 | global.rxt | none (additive); but 216 lines are pcre2-only (CHK-8) | Re-measured; reconciliation intact. |
| T10 | abi pins S693 83->84, recursion_identity FILEPIN 813f43ec8 -> 24d2888f5 (ancestor of SUBJECT, verified) | an abi event | the iterator | none | By ritual (D76/D94). |

No floor was lowered outright; the trades are SIZE (T1, T2), DFA-route reach (T3) and one retired
fixture's coverage (T4). T1 is the one that needs a judgement someone has not visibly made.

## PROBED-AND-HELD
- 20 of 20 new sabotage rows with a SAB_BEFORE: exactly one occurrence in SAB_FILE at SUBJECT.
- iter_diff oracle (libpcre2 pcre2demo loop) is independent of pcrec; the `L` loop control is labelled a regression control that shares the engine, and is used so.
- ITER_RETRY stamp check is against the emitted text (two emission sites), with both forms required reached (dfa-root >= 1, vm-guard >= 1).
- encseam iterator arm: exact population equality (nlossy_iter == 2 * nlossy), oracle python.
- twins check has a positive control (plant) read by the same `misses` function.
- FILEPIN commit is an ancestor of SUBJECT; no sabotage row was deleted.
- cells.tsv: 1,383 cells, 92 groups (1,131 byte, 252 utf8); global.rxt 62 blocks pinned exactly by the census.
