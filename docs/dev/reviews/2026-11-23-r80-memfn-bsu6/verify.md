# verify.md: r80 memfn-bsu6 (inline, by the coordinator; every CONFIRMED item is a quote claim or a one-call repro)

## RULE-1: HOLDS
- Call: `kit/cards.sh rule c6decide rule/scratch/drills/hb_void_loss.tsv` -> "C6 on: LOSS; readable 21 of 21 ... A/A: 0 standing non-TIE of 20 readable", rc 0.
- Quote: c6_rule.md CPU-QUIET CONTROL "an arm still short of LAUNCHES valid launches makes both of its cell's comparisons INCONCLUSIVE-NOISE"; cards.py `c6_cell` computes the reading and the A/A pairwise (c6_cmp -> NOISE only for the pair holding the None arm). kit/ref (coordinator's DRY) shows the denominator effect: "readable 28 of 32 ... A/A of 32 readable" with 4 V-void NOISE cells.
## FIDELITY-1: HOLDS
- Call: `python3 -I fidelity/scratch/tools/lay.py <SUBJECT cards.py> fidelity/scratch/orig c6_dig32 on` (compiles guarded off) -> V first vs re-time shared (p64,p32,rel) 2, H64 0, H64.b 2; H64.b rt0 (prelude mod 64, align) pairs = H64 rt0's (0/0, 32/5, 16/0, 48/5).
## FIDELITY-2 / CHECKS-3: HOLDS (two independent plants: fidelity's retime=1->0 at the re-time call; checks' X9 and T7). Reason by reading: DryProbe.measure checks only os.path.exists(exe); row `variants` records an index 0..3 with no pool identity.
## FIDELITY-4: HOLDS by reading: `class GateFail(RuntimeError)` (cards.py:669); time_cells' launch loop `except Exception as e: out[c] = row_line(c, "void", ...)` (cards.py:1184-1185); c6_read collects gatefail only from status `gatefail`.
## CHECKS-1, -2, -4, -6, -7: HOLD as mutant-survival claims (checks' mutant table, 62 mutants, copies under checks/scratch/mut/); not re-run (each is a "no check catches X" claim whose proof is the mutant's green run).
## CHECKS-5: HOLDS by reading: dry_guard's `guarded` tests argv[0] == taskset or `kw.get("env")` holding CARD_TIME; `_exec` passes env=None for gate/reach/proof execs (inherits os.environ); the DRIVER's timed path is `if (!getenv("CARD_TIME")) {... return 0;}` (cards.py:654).
## RULE-3: HOLDS by reading the diff: `probe_t0 = time.time()` after steps 1-3; `--deadline +S` = probe_t0 + S; `t_start` unused for the window; no deadline -> `stop = None`.
## RULE-2, RULE-4: HOLD by reading (`c6_report` prints only notes containing "not repeated"; `c6_decide` prefixes TRUNCATED on first-pass NOT-RUN only, `cmd_c6decide` returns 4 on retime_notrun too).
## G1-1: HOLDS by reading (g1_span_vector.py `if d is None or n is None or d == n: continue`; the meta line counts inputs).
## G1-7: HOLDS: `git diff --stat 9d796f4ec 715a17a58 -- src memfn/src memfn/include lib cli` empty (critic's call; coordinator's diffstat at freeze showed only cards.py, g1_span_vector.py and two .md files).
## Not verified: FIDELITY-5 (SUSPECTED; needs a real run's quiet sample), CHECKS-8 (SUSPECTED), RULE-5 (an algebraic argument; read, sound on its face).
VERIFY COMPLETE
