# land5 — [OPT-HYB-RESEED] landed on land4 (S4 + CLSPACK), abi 48 -> 49

Lane `land5` (sonnet, LANDING, 2026-09-30), branch `lane/land5` from
`lane/land4` (`25964e26`). Nothing merged to main. Two merges, both alone:

| commit | what |
|---|---|
| `7889ab1f` | `git merge lane/reseedfix` (`ade0ffbf`): 10 conflicted files, resolved below |
| `52275aec` | FILEPIN self-pin to `7889ab1f` |
| `a8f47b0a` | cpset stamp manifest re-recorded (3 rows) |
| `8d0b6524` | `git merge lane/land4` (which had gained `966c9ac8`: silentred + admin86, tests/docs only) |

`git diff 7889ab1f HEAD -- src lib cli` is EMPTY: every compiler byte is the
first merge's, so the FILEPIN and every number below stand for the tip.

## 1. What was resolved, by mechanism

| item | resolution |
|---|---|
| ABI | `PCREC_ARTIFACT_ABI` 49 (`src/gen/emit_dfa.c:51`). land4's 48 and reseed's 47 both give way. |
| ABI readers, found by grep | `run_codegen_tests.sh` `ABI_EXPECT=49` and its transition message (gained the reseed 48->49 clause); `match_api.md` §6: a new `abi is 49` entry (reseed's, rewritten from "46->47" to "48->49" with `abi-48` baselines), land4's entry turned to `was 48`, K73's stays `was 47`; §6.3's `RX_VM_RESEED` entry `abi 49` / `pre-abi-49`; `tuning.md` §2.35 (`abi 49`, `before abi 49`, `pre-abi-49`); `lib/pcrec.h` comment; `run_codegen_tests.sh` and S370/S371 comments (`pre-abi-49`); `hyb_reseed.md` "abi-49 paragraph"; `src/gen/CLAUDE.md` section title; `docs/dev/reseed/identity_sweep.py` (the normalizer now strips `abi 48 -> 49`; its base is the land4 build). |
| recursion-identity FILEPIN | `7889ab1f` (the merge commit, its last `src/` change; the k73utf convention). |
| Spec section number | reseed's tuning.md §2.33 collides with land4's `-fno-cls-kit`. Reseed becomes **§2.35** (land4 has §2.33, §2.34). Cross-references fixed by grep: `tuning.md` (heading + the flag-table row `flags bit PCREC_NO_HYB_RESEED`), `match_api.md` §6 + §6.3, `lib/pcrec.h`, `src/dump/axes_dump.c:779`, `src/gen/emit_vm.c:10908`, `src/gen/CLAUDE.md`, `tests/codegen/run_codegen_tests.sh:3356`, `tests/codegen/run_size_term.sh:186`, `docs/dev/reseed/clamped.md`, `docs/dev/reseed/answer_diff_witness.py`. Left alone on purpose: `reseed_report.md` (the lane's own voice, historical) and the r1 review files. |
| Deny bits | `PCREC_NO_HYB_RESEED` = bit 37 stands. land4 uses 36 (`CLS_KIT`) and 38 (`CLS_PACK`); 37 was free. `run_axes` derives 34 axes including 37. |
| `pcrec_emit_vm` order | `vm_cls_tables` (must follow the entry rung) then `vm_plan_reseed` (reads no program text). |
| Registry axes coverage pin | land4 147 + reseed's 8 (`-fno-hyb-reseed` on two rows x 3 lines, plus the `RX_VM_RESEED` value-set pair) = **155**. Measured: `checks passed: 155`. |
| rxtsource | no census move (reseed adds no corpus file the pin reads): 258 files / 4313 blocks / 32526 lines, rc 0. |
| cpset stamp manifest | 3 rows moved, `EMITTED_BYTES` only: `a(b|c)+d` +29, `(a)(b)(c)` +29 (the `RX_VM_RESEED "exact"` line), `(?<=foo)bar` +564 (`adaptive`: the stamp line plus the retry text). Verified by diffing each artifact against a scratch build of `lane/land4` at `-o -`: the stamp line, the two same-length abi digits and, for the third, the adaptive retry lines only. Re-recorded in `tests/codegen/manifests/m5_stage1_stamps.tsv` with a history paragraph in `run_cpset_structure.sh`. |
| Sabotage anchors | `scripts/m6read_check_sab_anchors.py`: 369 rows / 385 sites, all resolve (0 stale). The `SABANCHOR` check inside `test-codegen` agrees. |
| `run_size_term.sh` cap | NOT moved (31,500). Re-measured on the combined tree by building the reference compiler at `-DPCREC_MAX_VM_EMIT_CODE_BYTES=N`: K=4 stays chosen (`cap-rescue`) at N = 31,200, 31,300, 31,400, 32,000 and 32,100, K=8 at 36,000, `size-model-declined` at 36,300. So K=4 fits at or under 31,200 and K=3 does not fit through 32,100: the shape the cell exists for (6 and 3 do not fit, 4 does and is the largest, 2 fits) holds with margin on both sides. The cell itself reads all PASS. |
| Conflict markers | none (`grep '^<<<<<<< \|^>>>>>>> '` over the tree). `make` and `make strict CC=gcc-16` clean on the tip. |

## 2. Validation on the Mac (PROCS=2), tip `8d0b6524`

Logs: `worktrees/land5/build/land5/*.log` (gitignored).

| check | result |
|---|---|
| `make test-codegen` | rc=2, ONE `FAIL:` line: `nm could not read arm_a.o` (the standing darwin `run_inline_capability.sh` probe). `run_group: 11/12`; every other section `checks failed: 0`. |
| `make test-registry` | rc=0; axes coverage `checks passed: 155`, `checks failed: 0`. |
| `make test-rxtsource` | rc=0 (258 files / 4313 blocks / 32526 lines). |
| `make test-cpset-structure` | rc=0 after the re-record (rc=2 before it, CHECK 3 only, the three rows above). |
| `make test-recursion-identity` | rc=0, **16 passed / 0 failed**. (B) whole-file vs `7889ab1f`: `differing=0` on all four axes plus linkage. (A) vs `ac4917d`: `differing=0` on all four, `ctx-node-moved=264` on `default`. Run on the merged tree AFTER the land4 merge; the first run (before it) read the 264 as unruled, which was the silentred fix land4 had gained. |
| mech `S370`, `S371`, `S372` solo | each `unexpected 0, undetected 0, unreached 0, anomalies 0`: DETECTED. |
| reseed identity sweep (`docs/dev/reseed/identity_sweep.py`, base = scratch build of `lane/land4`, `-o -` on every side) | 6,844 rows (3,422 patterns x 2 encodings), **violations: 0**. Base equals deny on every artifact. Movers = adaptive rows only: byte 378 `adaptive` + 61 `adaptive-dense`, utf8 395 + 61 = **895** (the lane's 894 on its own corpus; the corpus is now 88 rows larger). `exact`/`clamped` artifacts identical after normalization. Code bytes gained: adaptive mean 561.7, dense mean 570.1, exact 29.0, clamped 31.0. |
| `answer_diff.py` over that mover TSV | `movers: 895`, `same: 895`, **0 DIFF**, 2,359,838 identical (subject, startpos) cells. |
| `make test-axes AXES="-fno-hyb-reseed"` | **OWED.** Running detached: `worktrees/land5/build/land5/axes.log`; status in `worktrees/land5/build/land5/chain2.log` (`=== END axes rc=N`, then `CHAIN2_DONE`). Baseline corpus run first, then the one axis; ~1 h at PROCS=2. PASS bar: 0 mismatches / 0 lost / 0 gained on the `-fno-hyb-reseed` line. Reseed's own run of this was killed by a 3,600 s baseline timeout (reseed_report §11), so this is the first live one. |

Mac `make test` in full is not run (Linux carries it).

## 3. Linux full `make test`

ubuntubudu was BUSY with land4's run (`~/pcrec/worktrees/land4-lx`, on
`966c9ac8`, 1 h+ elapsed at hand-off, no `MAKE_RC=` yet), so nothing
was launched over it. Instead a detached waiter is armed:
`~/pcrec/worktrees/land5_launch.sh` (`nohup setsid`). It polls every 60 s for
a `MAKE_RC=` line in `land4-lx/land4_test.log` AND zero `make` processes under
duxevents, then logs `df`, clones `land4-lx` to `land5-lx` (local clone), fetches
`lane/land5` from `~/pcrec/worktrees/land5-lx.bundle` (incremental over
`966c9ac8`; its head is `8d0b6524`), checks it out, and runs
`bash -c 'make -j4 > land5_build.log 2>&1 && make test > land5_test.log 2>&1; echo MAKE_RC=$? >> land5_test.log'`.

- waiter progress: `~/pcrec/worktrees/land5_wait.log`
- the run: `~/pcrec/worktrees/land5-lx/land5_test.log`, trailer `MAKE_RC=`
  (read make's `*** [test-X] Error` lines, never "sections ran")
- df at arming: 21 G free (78%).

Cleanup, when the run is read (Linux): `rm -rf ~/pcrec/worktrees/land5-lx
~/pcrec/worktrees/land5-lx.bundle ~/pcrec/worktrees/land5_launch.sh
~/pcrec/worktrees/land5_wait.log`. Mac: `git -C /Users/fdicostanzo/pcrec worktree
remove --force worktrees/land5` after the merge (`build/land5/base4` is a scratch
`git archive` of land4 inside it).

## 4. Notes

- Reseed's own manifest pins were never re-recorded on its branch (its
  branch never ran `test-cpset-structure`); the re-record is here, by mechanism.
- The recursion-identity gate is opt-in in the Makefile sense but part of
  `test-recursion-identity`; the (A) exception list (`ctx-node-moved`) came from
  the land4 merge, not from this lane.
- `awk: towc: multibyte conversion failure` / `cut: Illegal byte sequence`
  appear three times in the recursion-identity log on darwin (the `vars`
  corpus's deliberate non-UTF-8 byte); they do not move a count.
