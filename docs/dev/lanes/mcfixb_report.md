# mcfixb — review 2026-11-15 r6 memfn-mcfix FIX-NOW items (lane mcfixb, opus, 2026-11-15)

Branch lane/memfn-mcfixb, cut from ac097a76e (lane/memfn-mfind's tip). Review copied unchanged to
`docs/dev/reviews/2026-11-15-r6-memfn-mcfix.md` (+ dir) and indexed in docs/dev/reviews/CLAUDE.md.

## Summary

Every FIX-NOW and DOC item of the ruled r6 round is fixed. Each fix was shown RED first: the critic's repro or a
plant failed on the unfixed tree. Then it was fixed and shown GREEN. One more defect turned up under the STOP rule:
`--confirm` re-scored every level, not only the CONFIRM level. The kit manager ruled it (R1), and it is fixed too.

What changed in short:
- D197's rule now has guards. A record must pin the rule (both files' sha-256, taken at `window` time). The records
  must be one experiment: windows, run ids, code_commit, plan and kit fold must agree, and a confirmation must cover
  exactly the CONFIRM cells. A second run is derived from the first run's records (`--second FIRST FIRSTAVX2`), not
  from a bare flag.
- Three new verdict rows: a second run with no verdict reads NOT-WIN, a refused or absent confirmation reads
  INCONCLUSIVE (NOT-WIN on a second run), and `--confirm` re-scores only the CONFIRM levels.
- The shipped arm refuses a record with GLIBC_TUNABLES or the avx2 variant.
- est checks the cells files against pins that finalize writes.
- TIMED-SHAPE holds each form to a callee table. It refuses section-symbol branches (conditional ones included) and
  indirect call or jmp.
- CHECKS-A1 adds an `FF__COUNT` sentinel. No emitted byte moves.

What a valid record scores is unchanged, except as the review and R1 ruled (RULE-1, RULE-5, R1).

## Fixes by id

| id | state | what changed (file) | RED (unfixed) -> GREEN |
|---|---|---|---|
| RULE-1 | FIXED | verdict row `NOT-WIN second-run-without-a-verdict` is first. It covers a second run whose shipped arm has no verdict, or whose confirmation was refused or absent. (d197_rule.tsv/.py) | critic diffdrill on the unfixed tree: "shipped refused --second" -> INCONCLUSIVE x3 (red/diffdrill.unfixed.txt). Drill cases `[r6 RULE-1]` x2 -> NOT-WIN. Plant S3209 (m3) DETECTED |
| RULE-2 | FIXED | `provenance()` checks five things. (1) Every record pins the live rule. (2) Window: mfcard for the run, the first run's records and the arms; mfconfirm for a confirmation. (3) A confirming run id differs from the run's and the first run's. (4) `--second` refuses the run's own run id. (5) code_commit, plan (for a confirmation: kit keys + cards/policy sha), and the deciding forms' kit fold agree across all records. `confirm_cells_check` holds each confirming record's JMHC cells to the CONFIRM verdict's cells. A provenance failure is REFUSED (exit 2), never a row. **R1 (kit manager ruling)**: `score()` re-scores only the levels whose first-pass verdict is CONFIRM; every other level keeps its first-pass verdict | diffdrill "SAME record as confirm" -> LOSS (unfixed). Drill: 13 `[r6 provenance]` cases (1 control, 12 refusals, incl. "the SAME record passed as its own confirmation: REFUSED"), and end to end on est's synth (the run's own records as confirmation -> REFUSED). R1: the xlevel.py repro gave v3 3-loss LOSS -> CONFIRM (unfixed) / INCONCLUSIVE (pre-R1). Drill case `[r6 R1]` -> v3 LOSS stands, generic CONFIRM resolves to WIN. Plant S3208 (m2) DETECTED |
| RULE-5 | FIXED | row `INCONCLUSIVE confirmation-refused-or-absent`. Its predicate holds when a confirmation was given, there are fewer than 3 losses, and a loss has no usable confirming cell. The confirmation is never re-issued | diffdrill "cell missing" / "shipped confirm refused" -> CONFIRM again (unfixed). Drill cases `[r6 RULE-5]` x4 |
| RULE-6 | FIXED | second-ness comes from the first run's records passing provenance. CONFIRM's trigger says "the SAME arguments (a second run's --second included) plus --confirm" | covered by the provenance cases (`--second` with the run's own records, or with a confirming record as the first run: REFUSED) |
| RULE-3 + FIDELITY-3 | FIXED | record.py `window` pins `d197_rule_tsv_sha256` and `d197_rule_py_sha256` (`rule_pins`, idempotent, refuses a moved file). `rule` refuses a record whose pin differs from the files it runs with (`RULE PIN`). finalize pins `cells_sha256_<job>` (`cells_pins`), and est's read_cells refuses a differing file (`CELLS PIN`). The CELL TWICE comment is corrected: a full swap is the pin's to catch | verifier's swap plant: rc 0, priced (unfixed). est selftest `[r6 FIDELITY-3]` swap -> refused, plus its control (the same swap pinned is priced, so the pin is what refused). Plant S3207 (m1) DETECTED. Drill: rule pin wrong / missing -> REFUSED |
| FIDELITY-2 / RULE-8(b) | FIXED | arm-table row `memchr-variant-not-the-arms`: the shipped arm gets no verdict when its record carries GLIBC_TUNABLES or names the avx2 variant. The arm line prints libc's vector from the record's variant (TSV section `libc_variant`). The levels' axes no longer assert "32-byte EVEX shipped" | critic swap.py (two AVX2-tunable records) -> WIN x3 (unfixed). Drill `[r6 FIDELITY-2]` x2 -> INCONCLUSIVE |
| FIDELITY-1 | FIXED | link.py `TIMED_CALLEES` (first match by form prefix): mfind-*: none; fn-memchr, libc, pair: memchr; walk: none. Forms with no row (the s2d verify/enter forms) keep r5's rule. Every form: refuse any branch, conditional ones included, whose relocation names a section symbol, and any indirect call or jmp. `link.py shape-selftest SCRATCH`: 2 controls + plants S3210 (noinline,section), S3211 (cold), S3212 (pointer), S3213 (external definition; and fn-memchr calling strlen) | the unfixed check passed every plant (red/shape_old.txt: PASS x7). New: 7/7. Found while fixing: the `cold` plant leaves `_time` a `jne` into .text.unlikely (the loop moved to `a64_time.cold`), which a call/jmp-only regex misses. Plant S3215 (m5, section refusal dropped) DETECTED |
| RULE-7 | FIXED | the e2e drill needs `ratio N.NN` twice per level, not just the word "ratio" | plant S3214 (m4: the scan reads a missing key, ratio `-`) DETECTED. The old check would have passed it |
| CHECKS-A1 | FIXED | kit.h `fd_form` gains `FF__COUNT`. finder.c's `ff_name` assert is held to it. window.c `wf_wsearch[]` is now sized by its initializers and asserted `== FF__COUNT` (sized `[FF__COUNT]` it would be tautological again) | plant S3206 (a member after FF_MFIND): ac097a76e's window.c and finder.c compile rc 0. Fixed: both fail on their static asserts. No emitted byte moves (Validation) |
| CHECKS-A3 | FIXED | run_g2_mfind.py: `--sites < 80` -> argparse error (rc 2) | unfixed: --sites 40 parses on. Fixed: rc 2. --sites 80 parses |
| RULE-4 | DOC | TSV header defines UNPRICED (absent, drift, no x) and says why est's NULL/TEXT rows are still read. The `a=gc, b=gc` pair is now one field, `priced` | — |
| RULE-8(a) | DOC | predicates and header say loss COMPARISONS (`three-or-more-loss-comparisons`, `...-deciding-comparisons`, ...) | — |
| RULE-8(b) | DOC | w32 axes name its w16-then-SWAR fallback; w16 names its SWAR fallback | — |
| NOTED axes | DOC | d197_rule.tsv header names the axes that differ between the timed shape and production: caller loop, host function's other inlined sites, placement, fixed compile flags, EVEX 256 vs 512 | — |

Kept out of scope: RULE-9, CHECKS-A2 (PLAN), CHECKS-A4 (NOTED). No new abi, flags or D/K/R ids. Plant ids used:
S3206-S3215.

## Validation

- `make strict`: rc 0. `make test-codegen`: rc 0 (21/21 scripts).
- Emit identity vs ac097a76e's build (git archive, built in scratch): 400 corpus patterns (every other `pattern`
  line of tests/base, classes, anchored) x 3 flag sets (default, `-fmemfn-simd=x86-64-v3`, `--harness=mfind`), all
  with `-p rx --features all`. The .c, .h, stderr and rc were compared: 1200 pairs (752 compiled), 0 movers.
  scripts/emit_sweep.py was tried first; it was stopped because it waits on the box lock (it yielded to queue job
  622-kit-mfind-ident1 for over 10 minutes).
- `tests/memfn/run_arch_blind.sh`: rc 0, 17 passed, 0 failed.
- est selftest (`est.py selftest .../st2`): 66 cases, 0 wrong (64 + the swap case and its control).
- `d197_rule.py drill`: 43 cases, 0 wrong. `drill SCRATCH` (end to end): 45 cases, 0 wrong.
- `link.py shape-selftest`: 7 cases, 0 wrong.
- Dry runs with the fixed code (`run.py dry` into scratch dry1): JMB, JMH, J2, J2p rc 0, with TIMED-SHAPE green on
  every arm. Survey (survey.py): JMH 172 arms (mfind-* call nothing, fn-memchr only memchr), JMB 8, J2 libc memchr
  / walk none, J2p pair memchr x19.
- mcfixa's timing jobs 600-610 `--dry-run` with MFCARD_TREE = this worktree and FROZEN = its HEAD: 11/11 rc 0. They
  ran against a COPY of the jobs dir under a scratch PCREC_TMPDIR, so nothing was written in mcfixa's dir. No job
  needed editing: the rule's call shape (`rule R R.avx2libc [--confirm C C.avx2libc]`) is unchanged.
- The confirm plan (SLOT_CONFIRM_CELLS) keeps the same 151 kit keys as the plain plan, so provenance's plan check for
  a confirmation holds on a real confirm plan.
- `sabotage.sh` rows m1-m5, with the control on J2, est, d197, d197e2e and shape green: 5/5 DETECTED. The first pass
  had m3/m4 MISSED because the plants were malformed (an inline comment broke the planted line). The plants were
  fixed and re-run.

Not run (per brief): make test, test-axes, mech, the full sabotage table, box jobs.

Scratch: /var/tmp/pcrec-pcrec/scratch/memfn/mcfixb/ (red/, dry1/, sab*, sweep*, xlevel.py, survey.py).

## STATE AT HANDOFF

- Rulings: last entry applied R1 (kit manager, 2026-11-15 ~13:20).
- A record finalized before r6 carries no rule or cells pins, so the scorer and est now REFUSE it. No mfcard
  record exists yet. A second run would need `--second FIRST FIRSTAVX2`; no staged job runs one.
- OWED: none
