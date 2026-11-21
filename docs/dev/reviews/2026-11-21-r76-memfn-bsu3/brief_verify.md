# VERIFIER (sonnet): r76 memfn-bsu3

Read /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3/COMMON.md first (scope mandate, denylist, kit, plants).
EXCEPTION to COMMON's denylist for you: you MAY read the five critic files in the round dir
(sound.md, fidelity.md, checks.md, contract.md, slot.md) and the critics' lens dirs (checks/, slot/,
contract/) to re-run their repros. Still denied: `.coord/`, and everything else COMMON denies.
Your lens dir: .../crit-memfn-bsu3/verify/ (export TMPDIR=.../crit-memfn-bsu3/verify/tmp).
Output: .../crit-memfn-bsu3/verify.md (pre-created; APPEND only, one section per finding id, written
the moment each verdict is in). Deliver file: .../verify_deliver.txt (it wants a `## Verdicts` heading:
append `## Verdicts` first). Last line: `VERIFY COMPLETE`. Then run
`/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3 --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3/verify_deliver.txt verify`
until DONE, then end.

Do NOT trust any critic's consequence claim: re-run or re-read each one yourself. Verdict per item:
HOLDS / REFUTED / PARTLY (say which part) / not verified (why). A REFUTED quotes the exact call you ran.
For a plant claim record the plant compiler's exit code beside the byte verdict.

Items (ids as the critics wrote them):
1. CHECKS-1 (checks.md): S3515 is caught by the V-head TEXT leg as well as the -O0 rule, so the -O0
   rule has no control of its own. Verify: copy tests/memfn/simd_floor_check.py from the review tree
   into your dir, make the -O0 rule a no-op in the COPY (e.g. `o0_inline_issues` returns []), and run the
   copy against the S3515 plant compiler over the same sample the critic used (read
   tests/memfn/run_simd_floor.sh for the exact invocation; `--every 25`, `--jobs 2`, `nice`; build the
   levels dumper as that script does, into your dir). Does the run still fail on the V movers (by which
   leg)? Also the converse: with the V-head leg disabled instead, does the -O0 rule alone catch S3515?
2. CHECKS-2: a failed -O0 compile records no issue for an always_inline (V) selector. Verify by reading
   the C9 loop in the review tree's simd_floor_check.py (quote the lines) AND by re-running the critic's
   repro (checks/mut/bin/fakepcrec.py, FAKE_MODE=o0fail; read it first and confirm it only rewrites an
   artifact). Compare with BASE's script (`/var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu3/base/tests/memfn/simd_floor_check.py`).
3. CHECKS-3: `simd-form-named` is a kind-blind total, so a V loss can be compensated. Verify by reading
   simd_guarded_check.py's FLOORS and counting code (quote it) and by counting, with the subject
   compiler, which NAMED witnesses render a form at each family target.
4. CONTRACT-1: memfn/src/options.def's `span-vector` help says "no vector body is built yet". Verify
   with `build/pcrec --list-axes` and one x86-64-v3 emit of `[0-9a-f]{17}`.
5. SLOT-1: the K >= 16 safety assert reads WF_VWIN_LO (T-vwin's measured row bound) while T-vscan's
   bound is WF_VSCAN_LO. Verify by quoting window.c's enum, its comment, the assert and the B choice;
   and by a model: if WF_VWIN_LO were 32 (do NOT rebuild; reason from the code), would a T-vscan stretch
   with k 24..31 reach vs_w32_block and fail? Quote the T-vscan holds predicate.
6. SLOT-2: plan.md's [BSPAN-VANY-RIDE] row (read via `git -C /home/pcrec/projects/pcrec show
   fb258a000:docs/dev/plan.md`, locate it by `grep -n '^- \[BSPAN-VANY-RIDE\]'` and read only that row)
   names the selector lift but not the level-block lift that block_span.md §5 and §14 item (5) promise.
   Quote both.
7. SLOT-3: `nv`/`j` now key on the `define` column, which also gates s_v_ok's once-per-site rule;
   wf_tables_check does not pair `render == wf_span_v` with `define != NULL`. Quote the lines.
8. SLOT-4 and SLOT-5 (design/maintenance readings): quote the cited lines and say whether each
   described member exists as described (file:line). No consequence testing needed.

Compile cap: 300 compiles in total (each suite-script run at --every 25 counts 100). End all probing
by 00:30.
