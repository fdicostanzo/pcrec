# s2c15fix — review r11's rulings on span_cards rev 1.5 (lane report)

Branch `lane/memfn-s2c15fix` (worktree `worktrees/s2c15fix`), cut from d57f99ee4. The rulings are in
`docs/dev/reviews/2026-11-07-r11-memfn-s2rev15.md`, REV15-1..REV15-10. Every row is fixed. REV15-4's dead-code
residual is ACCEPTED and stated in §R1.5.

Scope: this worktree, `/var/tmp/pcrec-pcrec/scratch/memfn/s2c15fix/`, and gate job 474's source copy in
`scratch/memfn/s2c/jobs/` (its count and regex only). Read only: the main tree, `worktrees/s2c`, pcrec-bench,
`scratch/memfn/s2d/` (window 2's run directory was copied before anything ran over it) and the critic's scratch
(its P1-P6 were copied before est read them). Nothing was queued and nothing was timed.

## Summary

- **The fact now reads only the code that was timed (REV15-1).** est.py checks every launch executable against its
  job's `manifest.tsv` (the run id, the plan's sha and each launch's sha) and refuses a mismatch. The arm stems come
  from the pinned `plan.tsv`'s arm order. `obj/tab.c` is not pinned, so it only has to agree. `record.py finalize`
  pins each ran job's manifest sha (`manifest_sha256_<job>`) from the next window on. Window 2 predates the pin, so
  est checks it against its manifest as it stands and says so on a new `manifest` line in `rows`.
- **The fact itself (REV15-2, -3, -4).** A class is fused when exactly ONE instruction reads the subject and that
  instruction is a compare form:
  - the forms are 38-3B, 80/81/83 /7 and F6/F7 /0, not VEX/EVEX;
  - a subject read is any memory operand whose base or index holds `%rdi` or a register made from it register to
    register (a fixed point; a call and a string op count as reads too);
  - only the symbol's own range is decoded (`nm -S`);
  - the bytes' reading decodes VEX/EVEX, and the text reading parses base-less SIB.
  The two readings share only objdump's boundaries and the one-line rule `fact_of`.
- **Base check (REV15-10).** est refuses a null base whose own code is fused (`FUSED-FACT BASE`).
- **The bound's value (REV15-5).** It is `max(0, med(x_l))`; the noise stays `max(r_max, |med|)`.
- **The est commit (REV15-6, -7).** A draft names a commit only when est.py, the modules it loads from its own
  directory, ks_ref.py and policy.tsv are all blobs at HEAD. "Timed" is now an exclusion list, `NON_TIMED`: a path
  no row names is timed.
- **Sabotage (REV15-8).** Rows y1-y11 (S2953-S2963) cover both R15-2 refusals, the manifest check, the
  ignored-copy bypass and the new rules.
- **drill.py ¶3b (REV15-9).** drill.py implements ¶3b and computes window 2's four bound rows. They agree with est.
- **The tags grammar (REV15-10).** measures.md §3.5¶3b now states it.
- **Window 2 re-scored by the fixed est: FULL.** Every row, drift, note and policy line equals rev 1.5's, and so does
  the outcome. The draft digest is unchanged (2d2b3c0861443bec). `s2d2/r11_rows.txt` holds the rows.
- **No timed binary changes** (see "Timed-code impact").
- **Every CONFIRMED repro is now refused or corrected** (see "Fixes by id").

## Fixes by id

| id | fix | where | the critic's repro, after the fix |
|---|---|---|---|
| REV15-1 | `manifest_check`: the manifest's run id, its plan sha and every launch's sha against the run dir; the record's `manifest_sha256_<job>` pin when present. `plan_stems`: the stems from the pinned `plan.tsv` (null bases by class, then each row and its twin), checked against the plan's arm count; `obj/tab.c` must agree (STEM MISMATCH). `rows` prints a `manifest` line. `record.py finalize` writes the pin | `est.py`, `record.py` | P1, P2, P3, P4, P5: `MANIFEST MISMATCH job J4: launch 1's executable is not the one the manifest pins` (exit 2). P6: `STEM MISMATCH job J4: obj/tab.c's stems differ from the pinned plan's arm order (kit.verify_cmp.rc-memcmp.l1.p0, ...)` (exit 2) |
| REV15-2 | `fact_of(reads)`: exactly one subject read, and it is the compare | `est.py` | `plant/two.o`: a7 (6-byte memcmp, `cmpl` + `cmpw`) and a8 (three `cmpb`) read False/False (were True) |
| REV15-3 | compare forms 38/39/3A/3B, 80/81/83 /7, F6/F7 /0; a subject read is any operand through a subject-derived register (base or index) | `est.py` `fused_text`, `_text_insn`, `fused_bytes`, `_byte_insn` | `plant/l8.o`: a1/a2 (`cmp %r8,(%rdi,%rcx,1)`, opcode 39) True/True, a3 (`cmpw $imm,(...)`) True/True (a1/a2 read False before) |
| REV15-4 | `disasm` keeps only instructions inside `nm -S`'s range; the bytes decode VEX (C4/C5) and EVEX (62); the text parses every operand form, base-less SIB included. Dead code: an ACCEPTED residual (§R1.5) | `est.py` | `plant/v.o` has no `.size`, so est now refuses it (`no symbol size`). Assembled with `.size`, the self-test's reading cases cover v.s's shapes: VEX beside a fused compare, EVEX, base-less SIB with the subject as index and as a non-subject table, padding past `.size`. Text and bytes agree on each. P4 (the dead-code plant) still binds c2.p0 under the readings alone: the residual. Its executables are not the manifest's, so est refuses it |
| REV15-5 | bound value `max(r["value"], 0)`, noise `max(R_MAX, |med|)` | `est.py` `compute`; draft row value | the "priced positive" self-test case is re-aimed: value = med, noise max(r_max, med) |
| REV15-6 | `est_inputs()` (est.py, modules from its own directory, ks_ref.py, plan.POLICY); `est_commit` compares `git hash-object` with `git ls-tree HEAD` per file; `draft_gate` | `est.py` | in a `--shared` clone of this branch: the slot copied to the ignored `worktrees/evil/` gives `REFUSED ... worktrees/evil/est.py is not tracked at HEAD 6159382ac540 (an untracked or ignored copy)` (exit 2); an uncommitted edit to `memfn/data/policy.tsv` gives `REFUSED ... memfn/data/policy.tsv differs from its blob at HEAD` (exit 2); the clean clone drafts (FULL, the same digest) |
| REV15-7 | `NON_TIMED` (first match, reasons in place) and `timed()`; `timed_moved` filters `git diff --name-only` through it | `est.py` | in the clone, a committed `cli/main.c` edit gives `REFUSED ... the timed code moved between the record's code_commit 1e4999d1c3e8 and the est commit 19fb04caf294 (cli/main.c)` (exit 2). `timed()` reads `cli/`, `shared/`, `third_party/`, `measure_store/` and the Makefile as timed |
| REV15-8 | sabotage rows y1 S2953 (moved-code refusal), y2 S2954 (uncommitted est), y3 S2955 (manifest sha), y4 S2956 (ignored copy), plus y5-y11 for the new rules; each detector is a self-test case | `sabotage.sh`, `est.py` self-test | see Sabotage |
| REV15-9 | drill.py: `bound(x)` from ¶3b's text, over window 2's four bound rows' x_l (rmax_drill.py's W2, re-taken from the run dir), and one constructed positive row | `drill.py` | all four rows AGREE with est (0/116015, 0/105615, 0/119301, 0/107405); the positive row gives value 1000 |
| REV15-10 | measures.md §3.5¶3b: tags is `-` or `;`-separated tokens, matched exactly. est computes each verify row's null base's fact and refuses a fused base | `measures.md`, `est.py` `fused_facts` | self-test "a null base compiled fused": `FUSED-FACT BASE base.null.l1` |

Spec: `measures.md` §3.5¶3b and §3.5¶8a are amended (cited by number only). ¶3b now says:
- the fact is read from the executables the manifests pin, and the record pins the manifests (a record that
  predates the pin is checked as it stands and says so);
- the bound assumes an un-fused base;
- the value is `max(0, med(x_l))`;
- the tags grammar.
¶8a now says: the est commit names its rules only when every rules file is a tracked, identical blob, and the
timed code is an exclusion list.

Design: `span_cards.md` §R1.5 gains "The r11 table" (each id: ruling and where it is answered) and four
paragraphs: the fact as ruled by r11, the residual, the bound's value, the est commit. It also gains window 2 under
r11. There are `[rev1.5 r11-<id>]` hunks in the status line, §R1.5's R15-1 and R15-2 paragraphs, the §2.3
`verify_cmp` row, the §3.5 delta-row text, §3.8 step 1, §11 item 2 and STATE AT HANDOFF.

The CLAUDE.md lines are updated in `docs/design/memfn/`, `span_cards/`, `span_cards/slot/` and `span_cards/s2d2/`.

## Timed-code impact

The intent was NO; the result is NO for every file. Files changed on this branch since d57f99ee4:

| file | changes a timed binary? |
|---|---|
| `docs/design/memfn/span_cards/slot/est.py` | no. It reads the run directory after the timing. link.py, run.py, drv.c and gen.c never import it. `NON_TIMED` declares it non-timed |
| `docs/design/memfn/span_cards/slot/record.py` | no. `finalize` adds one `run` key per ran job (a manifest's sha) after the jobs ran. It writes only the record, and no TU reads the record |
| `docs/design/memfn/span_cards/slot/sabotage.sh` | no. It plants into scratch copies |
| `docs/design/memfn/span_cards/drill.py` | no. A design drill |
| `docs/spec/measures.md`, `docs/design/memfn/span_cards.md`, the four `CLAUDE.md` files, `s2d2/r11_rows.txt`, this report, `docs/dev/lanes/s2c15fix_deliver.txt`, the history index line | no. Text |
| (`docs/dev/reviews/2026-11-07-r11-memfn-s2rev15.md`, `docs/dev/reviews/CLAUDE.md`) | no. Text. These are the kit manager's commit a74b122de, below this branch's cut |

est's own check agrees. Every path that differs between window 2's `code_commit` 1e4999d1c and the est commit
8c193722d reads `timed() == False`, so `draft_gate` passed and wrote the draft. The same check refuses a `cli/` move
(REV15-7's repro). libpcrec, the kit, cli/, shared/, link.py, plan.py, drv.c, gen.c, slot.h, art.py, run.py and
`tests/memfn/arm_fixtures.c` are untouched.

## Window 2 re-score

est at 8c193722d (clean; every est input a blob at HEAD) over a COPY of
`/var/tmp/pcrec-pcrec/scratch/memfn/s2d/s2d-20261107a/`, at `scratch/memfn/s2c15fix/w2`. Before any run,
`diff -rq` showed the copy equal to the original. Committed as `docs/design/memfn/span_cards/s2d2/r11_rows.txt`.

- `est.py rows`: **`== s2 OUTCOME FULL exit 0`**. `policy r_max_e6 53751 pinned by the run record`;
  `est commit 8c193722dd4497dff704b3e8bbfdcdf529661b15`; `manifest J4 b2a6af13...a98800 NOT pinned by the run record
  (finalized before the pin): checked as it stands`.
- **The rows are IDENTICAL to rev 1.5's.** `diff` of the `row`, `drift`, `note`, `policy` and outcome lines between
  `s2d2/rev15_rows.txt` and `r11_rows.txt` is empty. The whole-file diff shows only the title comment, the `est
  commit` line, the new `manifest` line, the draft's sha comment and the draft's `# note est_commit` line. All four
  fused medians are negative (−116015, −105615, −119301, −107405), so REV15-5 leaves them at 0, as the ruling
  expected. Nothing moved, so there was no stop.
- `est.py draft` to `scratch/memfn/s2c15fix/draft.tsv`: 38 rows, 826 cells, digest **2d2b3c0861443bec**, outcome
  FULL, rc 0, sha-256 fe97a66181c34e858d87a7fb93da6afd62338bbb233e77e635cc899f87b4e1f8. Against rev 1.5's draft
  (`scratch/memfn/s2rev15/draft.tsv`), `diff` shows one line, the `# note est_commit` sha.
  `build/pcrec --list-measurements=draft.tsv` loads it (rc 0), and `ks_ref.py digest` gives 2d2b3c0861443bec.
  Nothing was written into `measure_store/`.
- The fact over window 2 under the r11 rule: l1 and c1 are fused (p0, p50, arm and twin, all 7 launches).
  w1/w2/w3/c2/cn and all 7 null bases are not fused. That is the same set as rev 1.5's.

## Sabotage

Slot-local rows in `slot/sabotage.sh`, ids S2953-S2963. They are free on main, in every worktree's `tests/mech`
and in the kit's reserved ranges (`memfn/docs/requests.md`). x1 S2950 is re-anchored: its old anchor
(`fused_text`'s last line) is gone, and it now plants `return bool(reads)` in `fused_text`, the same intent.

| row | plant | detector (self-test case goes WRONG) | result |
|---|---|---|---|
| y1 S2953 | `if moved:` → `if False:` in `draft_gate` | gate "timed code (src/) moved since code_commit" | DETECTED |
| y2 S2954 | the blob comparison never refuses | gate "est.py edited, uncommitted" | DETECTED |
| y3 S2955 | the launch-executable sha check removed | "a launch executable not the manifest's (P3)" (refused later as UNSTABLE, not by the manifest) | DETECTED |
| y4 S2956 | a path not tracked at HEAD skipped (`continue`) | gate "an est.py copy under an ignored path" | DETECTED |
| y5 S2957 | `fact_of`: any number of reads, all fused | "c1 compiled as two fused compares: not fused, null" | DETECTED |
| y6 S2958 | the fused-base refusal removed | "a null base compiled fused" | DETECTED |
| y7 S2959 | bound value 0 whatever the sign | "a fused class priced positive" | DETECTED |
| y8 S2960 | stems taken from `obj/tab.c` | "obj/tab.c's stems swapped (P6)" | DETECTED |
| y9 S2961 | the symbol range ignored | reading "a load past the symbol's size (padding)" | DETECTED |
| y10 S2962 | bytes do not recognise VEX/EVEX | reading "a fused compare beside a VEX load" | DETECTED |
| y11 S2963 | `timed()` default False (an inclusion list again) | gate "timed code (src/) moved since code_commit" | DETECTED |

The full run is in `scratch/memfn/s2c15fix/sab.log`, from a fresh scratch dir `sab/` over the final est (8c193722d).
- Control: the J2 dry run and the est self-test, both green.
- **`== slot sabotage: 35 DETECTED, 0 MISSED of 35 rows`**: the 24 earlier rows (j ... x3) and y1-y11.
- Each detector is a self-test case that goes WRONG when its row is planted. Cases that expect a refusal now name the
  check that must refuse (`refused:TEXT`), so a refusal by an earlier check does not count:
  - y3 (the manifest check removed) is still refused, as UNSTABLE, and goes WRONG;
  - y8 (stems from tab.c) likewise;
  - x2 (the bytes' check removed) is refused as FUSED-FACT BASE instead of MISMATCH, and goes WRONG.
- Reverted, each row is the control copy, which is green.
- A first full run was stopped by `scripts/safekill` and re-run. Its first ten rows were DETECTED. It had started
  before est_inputs' sitecustomize fix (below), which no row's plant or detector touches. The re-run is the one
  reported.

## Validation

All light: nice -n 19, -j4. The box queue held another lane's `495-mttri-axes2` (test-axes) the whole time. No kit-s2c
job and no timing job ran. The chain is `scratch/memfn/s2c15fix/val.sh`; its logs are `val.log` and `val.<step>.log`.

- `make` (nice, -j4): rc 0.
- `make strict`: rc 0 ("whole tree compiles clean with -Werror -Wshadow").
- `make test-memfn-finder`: checks 3272 passed, 0 failed; proof checks 882 passed, 0 failed.
- `tests/registry/limits_check.sh`: 39 passed, 0 failed.
- `tests/memfn/run_arch_blind.sh`: 17 passed, 0 failed.
- `make test-plan-lint`: 2 passed, 0 failed.
- `make test-spec-history`: 11 passed, 0 failed.
- `slot/est.py selftest` (`val.selftest.log`): **52 cases, 0 wrong**. The 52 are:
  - the main cases, with 10 new for r11: 4 manifest/stem cases, the two-compare class, l8, the computed pointer, the
    fused base;
  - 3 re-aimed: the positive median, and UNSTABLE and MISMATCH now named;
  - 10 reading cases, over assembled functions;
  - 6 gate cases, over a scratch git tree.
- `slot/sabotage.sh`, all 35 rows: control green, 35 DETECTED, 0 MISSED (see Sabotage).
- `rmax_drill.py` over the window-2 copy: its inputs equal the run's, and r_max_e6 = 56070 (unchanged).
- `drill.py`: rc 0; the four bound rows AGREE with est.
- Found on the way: the first `est.py draft` from the committed est REFUSED. est_inputs counted Debian's
  `/etc/python3.14/sitecustomize.py`, which lies outside the tree, as an imported module. est_inputs now takes the
  modules loaded from est's own directory (sys.path[0]); under `-I` every other entry belongs to the Python install.
  Commit 8c193722d.
- `docs/dev/artifact_size_log.tsv` was not touched in this worktree.

## Gate jobs

- `474-kit-s2c-slotsab` (the source copy in `scratch/memfn/s2c/jobs/`; the previous copy is
  `scratch/memfn/s2c15fix/474.before`): `expect rows=24` became `rows=35`, and the row regex gained
  `y1|..|y11`. `--dry-run` prints `boxqueue: expect rows=35 ...`. As the brief allows, only the count and the regex
  changed. The would-run line and the header comment still list the rows only up to x3.
- The job runs over `TREE=worktrees/s2c` (common.sh). That tree's sabotage.sh still has 24 rows, so the edited
  source copy holds only once this branch is merged into s2c. The QUEUED copy (`worktrees/.boxqueue/pending/
  474-kit-s2c-slotsab`) was not touched. It still expects 24 rows and matches `worktrees/s2c` as it stands.
- The full 35-row run took about 190 s (control.out to y11.out 173 s, plus the control's own run) here (under the axes job's load), against the job's `cap 2400`, `est 900`.
- 470-473 carry no count this change moves. Nothing was queued.

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| apply every ruling of r11 (FIX-NOW / bounded FIX) | Fixes by id: REV15-1..REV15-10 |
| REV15-4's dead-code residual ACCEPTED, in the text | §R1.5 "The residual (REV15-4, ACCEPTED)" |
| every CONFIRMED repro refused or corrected after the fix, shown | Fixes by id, the last column (P1-P6, two.o, l8.o, v.s's shapes, the ignored copy, the policy edit, the cli/ move) |
| design text in span_cards.md marked `[rev1.5 r11-<id>]`, an r11 table in §R1.5 | done |
| spec hunks in measures.md, cited by section number | §3.5¶3b, §3.5¶8a |
| new sabotage rows from S2953 | y1-y11 S2953-S2963 |
| window 2 re-scored on a COPY with the fixed est (`rows`, `draft` to scratch); rows IDENTICAL to rev 1.5's; FULL; stop if anything moves | identical, FULL; nothing moved |
| commit the fixed-est rows as `s2d2/r11_rows.txt` | 6159382ac |
| TIMED-CODE IMPACT, every file, intent NO | Timed-code impact: NO for every file |
| validation list (make, strict, finder, limits_check, arch_blind, plan-lint, spec_history, est selftest, sabotage) | Validation |
| gate job 474: expected row count and regex only | 24 → 35, regex + y1..y11 |
| deliver file committed by name in the first commit | 6a072a754 |
| artifact_size_log.tsv not committed | not touched in this worktree |
| queue nothing, no timing | nothing queued, nothing timed |

## STATE AT HANDOFF

Complete; OWED none. No rulings file was named. Next, the kit manager's:
1. merge this branch into s2c, so the gate job's 35 rows hold;
2. S2e (the set into `measure_store/`, PROVENANCE naming the est commit that scores it, and the recompute's ¶3b
   rule over the `fused-load-op` token).
The next window's record will pin its manifests (`record.py finalize`), so est checks them against the pin.
