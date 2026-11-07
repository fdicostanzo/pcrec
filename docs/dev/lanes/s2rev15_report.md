# s2rev15 — span_cards rev 1.5: the fused-compare bound, the estimator commit, r_max measured (lane report)

Branch `lane/memfn-s2c` (worktree `worktrees/s2c`), on ca4ca26b1. The kit manager's rulings R15-1..R15-3 on the
second S2d window (run s2d-20261107a, FROZEN 1e4999d1c, REFUSED on `verify.rc-memcmp.l1` and
`verify.settest.c1`). Scope: this worktree, `/var/tmp/pcrec-pcrec/scratch/memfn/s2rev15/`, and gate job 474 in
`/var/tmp/pcrec-pcrec/scratch/memfn/s2c/jobs/`. The main tree, pcrec-bench and the run dirs under
`scratch/memfn/s2d/` were read only (both windows' dirs were copied before anything ran over them). Nothing was
queued and nothing was timed.

## Summary

- **R15-1, the fused-compare bound.** est.py reads a FACT off the timed code of every `verify_cmp` row. It reads
  every launch executable `J4/L<l>/J4.L<l>`, arm and twin. The fact: every instruction of `<stem>_time` that
  reads the subject (a base+index memory operand) is a `cmp`/`test $imm` on that memory, and there is at least
  one. Two readings must agree:
  - `fused_text`, over objdump's mnemonics, derives the fact.
  - `fused_bytes`, est's own prefix/REX/opcode/ModRM/SIB decode of the instruction bytes, checks it.
  A disagreement refuses (`FUSED-FACT MISMATCH`). So does a fact that differs between launches or between arm
  and twin (`FUSED-FACT UNSTABLE`). A row WITH the fact, whatever its sign, is `measured`: value 0, noise
  `max(r_max, |med(x_l)|)`, tag `fused-load-op`, and a source that names the evidence. A row without it keeps
  REV14-1 (`null` when all six trimmed launches are negative).
- **The fact holds for exactly l1 and c1** in window 2 (and in window 1's older loop too). w1, w2, w3, c2, cn
  and every null base load the subject into a register first.
- **R15-2.** The draft writes `# note est_commit: <sha>`. It is refused from an est with uncommitted `slot/`
  changes, and refused when any `TIMED_PATHS` file differs between the record's `code_commit` and the est
  commit. `rows` prints an `est commit` line.
- **R15-3.** `r_max_e6` is now 56070, MEASURED over both windows (window 1 6447..53751, window 2 15597..56070,
  max w1.p50). The UNMEASURED DEFAULT label is dropped and both windows are cited. Window 2 is still scored at its
  pinned 53751; the new value applies from the next window.
- **Window 2, re-scored: FULL.** The four l1/c1 rows are bound. Every other row is byte-identical to
  `s2d2/est_rows.txt`.
- **No timed binary changes** (see "Timed-code impact").
- **No set-format, noise-state or seam change.** The draft loads in pcrec's C loader, and its digest equals
  ks_ref.py's.

## Rev 1.5 text

- `docs/design/memfn/span_cards.md`:
  - The title and status are rev 1.5.
  - New §R1.5: the rulings table; R15-1's fact, check, bound and recompute reading; R15-1's sabotage and
    self-test; R15-2; R15-3; window 2's re-score.
  - `[rev1.5 R15-1]` hunks in the §2.3 `verify_cmp` row, §3.5 delta rows, and §11 item 2 (the independent
    control).
  - `[rev1.5 R15-2]` hunks in §3.8 steps 1 and 3.
  - `[rev1.5 R15-3]` in §R1.4's r_max paragraph.
  - A STATE AT HANDOFF entry.
- `docs/spec/measures.md`:
  - §3.5¶3 is amended: a bound row is priced by ¶3b.
  - §3.5¶3b is new, "Bound delta rows". The rule is generic: a producer's fact about the timed code, derived
    from object code and never from the sign, checked by a second reading, and stated in `tags`. The row is
    value 0, noise `max(r_max_e6, |med(x_l)|)`. The recompute applies it to tagged rows and takes the fact as
    stated, because the set carries no object code.
  - §3.5¶8a is amended: the rules are those of ONE estimator commit, named by PROVENANCE.md and the draft. A
    later est may score a record only over unchanged timed code.
  - §3.5¶11 is amended: bound rows are priced.
- `memfn/data/policy.tsv` and its CLAUDE.md: r_max_e6 is 56070, measured, both windows cited, with a re-derive
  trigger.
- The CLAUDE.md lines are updated: `docs/design/memfn/`, `span_cards/`, `s2d2/` and `slot/`.

## Code

All of it is in the slot harness's python and a design drill. None of it is under `src/`, `cli/`, `lib/` or
`memfn/src/`.

- `slot/est.py`:
  - `FUSED_TAG`, `FUSED_EVIDENCE`, `TIMED_PATHS`.
  - `fused_text` (the derivation) and `fused_bytes` (the check). `FUSED_DERIVE` lets the self-test plant a
    derivation.
  - `disasm`: objdump at `--insn-width=16`, so no line wraps.
  - `arm_syms`: the `{name: aK}` map from `obj/tab.c`.
  - `fused_facts`: every launch, arm and twin.
  - `est_commit` and `timed_moved` (R15-2).
  - In `compute`, the bound branch runs before the NULL/sub-resolution logic, for rows with the fact only.
  - Bound rows are excluded from the bimodal note: their value is 0, so the ratio test would always fire.
  - The draft's bound row is `measured`, value `0`, with the `fused-load-op` tag and the evidence source. The
    draft also writes the `# note est_commit` line and refuses on a dirty est or moved timed code.
  - Self-test:
    - `_synth` now builds REAL timed code for J4 with `_synth_code`: gcc -O2 `-fno-ipa-icf`, link.py's
      pointer-bump loop. l1 and c1 compare the byte against an immediate (fused). The other classes mask the
      byte first. The bases load it into a register.
    - `VK` moved from settest.c1 to settest.c2, because c1 is fused now. `FK` is l1.p0.
    - Six new cases: (1) the bound at a negative median, with no bimodal note; (2) the bound at a positive
      median; (3) a non-fused class negative on all six launches stays null; (4) the fused class compiled
      un-fused stays null; (5) a fact unstable across launches is refused; (6) a non-fused class wearing the
      fact is refused.
    - The plant-applied test also hashes the J4 launch executables.
- `slot/sabotage.sh`:
  - New rows x1 S2950, x2 S2951, x3 S2952 are in the header, the default row list and the case table.
  - b1 S2945 is re-anchored. Its old anchor text gained `and not r.get("fused")`, so the first full run
    reported PLANT FAILED. The fix keeps the same plant, at the new anchor.
- `rmax_drill.py`: the two windows' inputs are `W1` and `W2`, and `WINDOWS` selects one by run id. RUNDIR
  re-takes the inputs of the window its record names. The drill prints each window's range and the max over
  both.

## Timed-code impact

The intent was NO; the result is NO for every file. Files changed since the second window's frozen code
(ca4ca26b1, which is 1e4999d1c plus the s2d2 evidence docs):

| file | reaches a timed binary? |
|---|---|
| `docs/design/memfn/span_cards/slot/est.py` | no: it reads cells and the run directory's executables after the run; link.py, run.py and drv never import it for rendering or timing |
| `docs/design/memfn/span_cards/slot/sabotage.sh` | no: it plants into scratch copies only |
| `docs/design/memfn/span_cards/rmax_drill.py` | no: a design drill over est's `compute` |
| `memfn/data/policy.tsv` | no: plan.py reads it only as the cards' `gate` (`gate_default_e6`) and est reads `r_max_e6`. Neither reaches a TU: link.py, drv.c, gen.c, slot.h, art.py and run.py do not read the policy (grep). A next window's frozen plan text and record pin the new value |
| `memfn/data/CLAUDE.md`, the four `CLAUDE.md` files, `span_cards.md`, `measures.md`, `s2d2/rev15_rows.txt`, `docs/dev/lanes/s2rev14_deliver.txt`, this report | no: text |

est's own R15-2 check agrees: `git diff --name-only 1e4999d1c <est commit> -- TIMED_PATHS` is empty. The draft
was written, which it would not be otherwise. libpcrec, the kit and `tests/memfn/arm_fixtures.c` are untouched.

## Score of window 2

The fixed est was run over a COPY of `/var/tmp/pcrec-pcrec/scratch/memfn/s2d/s2d-20261107a/`, at
`scratch/memfn/s2rev15/w2`. est was at commit 1e862ff9a, clean; its code is unchanged at the tip. The rows are
committed in `docs/design/memfn/span_cards/s2d2/rev15_rows.txt`.

- `est.py rows`: **`== s2 OUTCOME FULL exit 0`**. `policy r_max_e6 53751 pinned by the run record`;
  `est commit 1e862ff9aeb0f696855024f8135a456e4ba06d3d`.
- `est.py draft` to `scratch/memfn/s2rev15/draft.tsv`: 38 rows, 826 cells, digest 2d2b3c0861443bec, outcome
  FULL, rc 0. The file's sha-256 is 689e4c74a3379f8ad5a7062444f34acde4ef80430d713910c2dbcf326ece80ba.
  `build/pcrec --list-measurements=draft.tsv` loads it (rc 0), and `ks_ref.py digest` gives 2d2b3c0861443bec.
  Nothing was written into `measure_store/`.

Every row's status:

| row | status | value | noise |
|---|---|---|---|
| kit.enter.1.NONE / .3 / .4 / .5 / .6 | ungated (priced) | 1097315234 / 41460754 / 43675666 / 5057971 / 38926996 | 6657931 / 1356342 / 1957837 / 187677 / 1263116 |
| kit.find_byte.libc / pair / walk | gate pass | 38049 / 73843 / 1000000 | 609 / 1277 / 1076 |
| kit.find_hit.libc.{periodic,random}.one.{1024,256} | ungated | 16247767, 19207980, 55815981, 54632973 | 556954, 345413, 658297, 501385 |
| kit.find_hit.pair.{periodic,random}.{alt,one}.{1024,256} (8) | ungated | 83154198, 39437556, 83985086, 38333593, 141147653, 95657352, 130362238, 88893809 | 5514347, 841618, 5239119, 827446, 2546493, 1001560, 2483595, 1329406 |
| kit.find_hit.walk.{periodic,random}.one.{1024,256} | ungated | 30591248, 29134980, 50541639, 43531860 | 1230854, 1772381, 26273532, 18149325 |
| **kit.verify_cmp.rc-memcmp.l1.p0** | **fused-compare bound** (was null) | 0 | 116015 |
| **kit.verify_cmp.rc-memcmp.l1.p50** | **fused-compare bound** (was null) | 0 | 105615 |
| kit.verify_cmp.rc-words.w1.p0 | sub-resolution, r 53751 | 20652 | 54465 |
| kit.verify_cmp.rc-words.w1.p50 | ungated (priced) | 38837 | 41753 |
| kit.verify_cmp.rc-words.w2.p0 / p50 | ungated | 7865977 / 8229814 | 73121 / 87189 |
| kit.verify_cmp.rc-words.w3.p0 / p50 | ungated | 13654226 / 11695981 | 245430 / 693187 |
| **kit.verify_cmp.settest.c1.p0** | **fused-compare bound** (was null) | 0 | 119301 |
| **kit.verify_cmp.settest.c1.p50** | **fused-compare bound** (was null) | 0 | 107405 |
| kit.verify_cmp.settest.c2.p0 | sub-resolution, r 53751 | 25519 | 86477 |
| kit.verify_cmp.settest.c2.p50 | sub-resolution, r 47541 | 0 | 47541 |
| kit.verify_cmp.settest.cn.p0 / p50 | ungated | 6610053 / 15963793 | 572429 / 179674 |

Drift is kept on every job (J2 0, J2p 8357, J3 14111, J4 280, J5 17637). `diff` against `s2d2/est_rows.txt`
shows only the four bound rows and the outcome line.

The draft's header and note lines:

```
# pcrec measurement set (spec: docs/spec/measures.md)
# note note_box_state: a launch-level fast/slow split in the control of J2 1.51 %, J2p 0.65 %, J3 1.47 %, J4 0.93 %, J5 1.78 % (a gap over 5000 ppm between two clusters of >= 2 launches): the box changed state within those jobs
# note note_bimodal: bimodal delta rows (a gap over 100000 ppm of the value between two clusters of >= 2 launches; priced with their spread as noise): kit.find_hit.walk.random.one.1024, kit.find_hit.walk.random.one.256, kit.verify_cmp.rc-words.w1.p50
# note r_max_e6: 53751, pinned by the run record
# note est_commit: 1e862ff9aeb0f696855024f8135a456e4ba06d3d, the estimator that scored the record (code_commit 1e4999d1c3e88b98bff91d4a973c4a18ec3b4fdf; the timed code unchanged between them)
format 2 / id zen4-grid3 / rev 1 / class x86_64/zen4 / isa x86-64-v4 avx512f avx2 sse4.2 popcnt bmi2 / tier scratch
composite 0 / members (empty) / unit_key kit.find_byte.walk / method kit-grid@3
run s2d-20261107a record:d2c9fb97fb433d50b892731b8f28d315a6dccf70ff3b978ea78345721f15263b
box AMD Ryzen 7 7700X 8-Core Processor, CPU 7 / compiler gcc 15.2.0 -O2 -march=x86-64 -mtune=generic / libc glibc 2.43
code_commit 1e4999d1c3e88b98bff91d4a973c4a18ec3b4fdf / counters skipped:not-taken / partial 0 / rows 38 / values_digest 2d2b3c0861443bec
```

A bound row as drafted:
`kit.verify_cmp.rc-memcmp.l1.p0 walkbytes 0 -22355 116015 49 measured - - kit:form.rc-memcmp=8821e9cc925d59c2 fused-load-op slot J4 fused-compare bound r_max 53751; evidence: windows s2d-20261106 and s2d-20261107a, two null bases, both negative; the arms-only fused/unfused step +0.14 wb (span_cards s2d2/analysis.md)`.

A side reading, not asked: est at rev 1.5 over a copy of window 1 (s2d-20261106) bounds l1/c1 there too, and
that window stays REFUSED on `floor:byte.libc` alone.

## Sabotage

Slot-local rows (`slot/sabotage.sh`), ids S2950-S2952. They are free on main, in the worktrees' sabotage
scripts and in the kit's reserved ranges.

| row | plant | detector | result |
|---|---|---|---|
| x1 S2950 | `fused_text` returns `bool(subj)`: every class that reads the subject wears the fact | the bytes' reading refuses: self-test `complete` is `refused (FUSED-FACT MISMATCH ...)` | DETECTED (`selftest complete WRONG refused (FUSED-FACT MISMATCH kit.verify_cmp.rc-words.w1.p0 launch 1 ...`) |
| x2 S2951 | the check's comparison is `if False:` (removed) | self-test "a non-fused class wearing the fact" (expects refused) goes WRONG | DETECTED (`... a non-fused class wearing the fact WRONG ok (FULL exit 0)`) |
| x3 S2952 | the bound branch is keyed on `key.startswith("kit.verify_cmp.")` (no fact) | self-test "a class NOT fused negative on all six: null (REV14-1 holds)" goes WRONG | DETECTED (`... a class NOT fused negative on all six: null (REV14-1 holds) WRONG`) |

Each row goes red when planted. Reverted, it is the control copy: the J2 dry run and the est self-test are
green.

## Validation

All light: nice -n 19, -j4. The box queue held another lane's make test / mech / reach the whole time, and
there was no timing job. The chain is `scratch/memfn/s2rev15/val.sh`; its logs are `val.log` and `val.<step>.log`.

- `make` (nice, -j4): rc 0.
- `make strict`: rc 0 ("whole tree compiles clean with -Werror -Wshadow").
- `make test-memfn-finder`: checks 3272 passed, 0 failed; proof checks 0 failed.
- `tests/registry/limits_check.sh`: 39 passed, 0 failed.
- `tests/memfn/run_arch_blind.sh`: 17 passed, 0 failed.
- `make test-plan-lint`: 2 passed, 0 failed.
- `make test-spec-history`: 11 passed, 0 failed. A first commit of measures.md was refused by the pre-commit
  spec-history hook, because "corrected" is a walkback marker. The phrase was reworded.
- `slot/est.py selftest`: **28 cases, 0 wrong** (6 new for R15-1; the r10 cases now target c2, a non-fused class).
- `slot/sabotage.sh`, all 24 rows from a fresh scratch dir (`sabfinal`, `val.sabotage.log`): control green (J2
  dry run and est self-test), **24 DETECTED, 0 MISSED**. The first full run (`sab.log`) had b1 at PLANT FAILED (its
  anchor moved). It was re-anchored and then DETECTED alone (`sab2.log`) and in the full run.
- `rmax_drill.py` over copies of both windows: the inputs equal each run's; r_max_e6 = 56070.
- `docs/dev/artifact_size_log.tsv` was not touched in this worktree.

## Gate jobs

- `474-kit-s2c-slotsab`:
  - `expect rows=21` became `rows=24`.
  - The row regex gained `x1|x2|x3`.
  - The would-run row list and the header comment now name n3, s3-s5 (missing before) and x1-x3.
  - `--dry-run` prints `boxqueue: expect rows=24 ...`.
  - The previous copy is `scratch/memfn/s2rev15/474.before`.
- 470-473 carry no count this change moves: strict's rc, the sections count, make test's step and mech rows.
- Nothing queued. `s2d/window.vars` was not touched.

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| R15-1 bound: value 0, noise max(r_max, \|med\|), evidence source | est.py bound branch and draft row; §R1.5; measures.md §3.5¶3b |
| R15-1 scope by a class fact derived from the timed arm's object code, never the sign; REV14-1 holds without it | `fused_facts` over every launch executable, two readings; self-test cases 3 and 4 |
| R15-1 sabotage (1) a non-fused class wearing the fact refused, (2) the check removed, (3) the branch without the fact; red planted / green reverted | x1 S2950, x2 S2951, x3 S2952 (see Sabotage) |
| R15-1 no set-format, noise-state or seam change | none: `tags` and `source` are existing provenance columns; the C loader and ks_ref accept the draft |
| R15-2 the draft and PROVENANCE name the est commit; a recompute uses it; a later est over unchanged timed code is allowed; in design and spec | `# note est_commit`; `est_commit`/`timed_moved` refusals; §R1.5, §3.8 steps 1 and 3; measures.md §3.5¶8a |
| R15-3 r_max re-derived from window 2 by rmax_drill.py; policy.tsv updated, label dropped, both windows cited; window 2 at its pinned 53751, new value from the next window | rmax_drill.py (W1, W2); policy.tsv 56070; §R1.5, §R1.4 hunk; the draft's note `53751, pinned` |
| design marked `[rev1.5 <id>]` with an §R1.5 table; spec cited by section | done |
| score window 2 over a copy: rows, draft to scratch; outcome, every row, the draft's header/notes; no measure_store write | Score of window 2: FULL |
| timed-code impact section, every file | done: NO for every file |
| validation list | Validation |
| gate job 474's expected row count | 21 -> 24 |
| commit s2rev14_deliver.txt as-is, by name | 89bc49b8a |
| artifact_size_log.tsv not committed | not touched (checked by `git status`) |

## STATE AT HANDOFF

Complete; OWED none. No rulings file was named. Next: S2e (the set into `measure_store/`, PROVENANCE naming est
commit 1e862ff9a and the bound rows' evidence, and the recompute's ¶3b rule over the `fused-load-op` tag).
Open for the kit manager: `TIMED_PATHS` is a hand list (§R1.5 says so). A path it misses weakens only the R15-2
refusal; it cannot change the frozen cells.
