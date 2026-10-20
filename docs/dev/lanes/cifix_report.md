# cifix report (lane/cifix, from main 8b89477df)

## CI red list (run 39484223605, sha 39457a796)
Only job test (3/3) was red (shards 1/3, 2/3 green). In its log
(`gh api repos/fdicostanzo/pcrec/actions/jobs/118840341237/logs`) the ONLY
`*** [Makefile:1104: test-lookaround] Error 1`; the shard trailer says
27/27 sections ran. No other red section. In test-lookaround every answer
check passed (checks passed 7, failed 13: 10 section-1 population pins +
3 policy pattern counts).

## Cause and arithmetic
The pin population is `tests/assertions/` alone (run_expansion_diff.sh).
Commit 2619ced1b added 3 blocks to tests/assertions/multiline.rxt
(`(?m)(\n^)`, `(?m)(a\n^)`, `(?m)(^)$`). Proof: the PARENT corpus
(`git archive 2619ced1b^ tests/assertions`) run through
tests/lookaround/expand_corpus.py reproduces DELTA 4's literals exactly
(545/13120/92/337/11249/38/444/253/308); HEAD gives the CI numbers.
- tot_blocks 545 -> 548: 3 blocks, all qualify (qual_blocks 337 -> 340).
- tot_beh +24: 8 + 8 + 8 m/n cells; tot_g/qual_g +12: 5 + 3 + 4 g cells
  (92 -> 104, 38 -> 50); qual_beh 11249 -> 11273.
- P1 one pattern per block: 337 -> 340 (p1_lookaround 253 -> 256; NONE
  337 -> 340).
- P2 one per substitutable occurrence: 1 + 1 + 2 = +4, 444 -> 448
  (p2_lookaround 308 -> 312).
- Q1-Q7 and both identity counts UNCHANGED (all added rows carry a lookaround).

## Re-pin
tests/lookaround/run_expansion_diff.sh: DELTA 5 comment (named cause, the
table above), exp_pop literals, the section-1 ok message, and the
report_policy arguments (P1 340 76 256, P2 448 106 312, NONE 340 340 0).
Other population pins on the same corpus: grep of tests/, scripts/, Makefile
for the literals/tot_blocks finds only expand_corpus.py (generator, no pin)
and this script. The rxtsource/startset pins were already re-pinned by
2619ced1b and shards 1/3 and 2/3 were green.

## emit_sweep -I
scripts/emit_sweep.py: `sys.path.insert(0, SCRIPT_DIR)` at module level (the
cls_identity.py / compile_time_census.py house pattern), and under `--trace`
`import trace_diff` is now resolved right after parse_args, so a missing
module fails BEFORE any table prints. (The traceback already exited 1; the
bug was the movers=0 tables standing printed above it.) Checked: a copy of
the script in a dir without trace_diff under `python3 -I --trace` dies at
once with rc=1 and no tables; the real script imports under -I.

## Verdicts
- `scripts/boxlock run --label cifix -- make -C worktrees/cifix test-lookaround`:
  checks passed 11, failed 0 (log worktrees/cifix/build/look.log; no
  `*** [` lines). scripts/verdict printed INCOMPLETE for it because a direct
  section run has no make completion trailer; the log's own tally is read.
- `make strict` rc=0; `tests/plan_lint/run_plan_lint.sh` rc=0 (2/0).
- Not run: full make test (manager's); a trace/variant emit_sweep corpus run
  (cap).

## STATE AT HANDOFF
Committed on lane/cifix, nothing owed, no src/ change.
