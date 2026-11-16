# raisefix — R28-1 witness for the raise's term rule; the raise re-cut as one commit

Lane raisefix (opus), 2026-11-16, for the kit manager. Review: r28
(`/var/tmp/pcrec-pcrec/scratch/crit-memfn-span4kfix/review.md`, RULED section).
Branch `lane/memfn-span4k-raise`, re-cut as ONE commit whose parent is plan B's
tip `60c2958ae`.

## Summary

- **R28-1 is fixed.** The raise's READ-1 has two declining rules in
  `run_part_terms` (memfn/src/window.c): the stretch rule and the term rule.
  The term rule now has an in-tree witness and a plant row.
  - Witness: `pur_long_run_fixtures` (tests/memfn/arm_fixtures.c) gains a
    second pair. `pur_long_run` takes a new argument `M`: positions from `M` on
    carry many bytes, so they are unspelled.
    - At `M = 0` the part is L SET terms and no RUN term. Its scan stretch is
      empty, so only the term rule can refuse it.
    - Control: `MF_MAX_TERM` (32) unspelled positions DEFINE.
    - Witness: `MF_MAX_TERM + 8` (40, the critic's L=40 shape) unspelled
      positions must be refused, and the error must name "more than
      MF_MAX_TERM terms".
  - Plant row **S3258** (`tests/mech/sabotages/S3258_run_part_terms_past_max_term.sh`)
    removes the term rule. It goes RED. S3259 is unused.
  - The purity pin moves 13270 -> **13272** (tests/memfn/run_finder.sh). Its
    comment now carries the 13268 decomposition from the review's question (2).
  - The cloud mech shard table is regenerated for S3258.
- **R28-4 (DOC): `WF_LEGACY_POS` is ADDED by the raise, not retired.** The raise
  defines `#define WF_LEGACY_POS MF_MAX_TERM` in window.c. That keeps
  `wf_legacy`'s per-term arrays at 32 positions while `MF_WSPAN_POS` goes to
  4095. The old commit message said "retired"; the re-cut message says "added".
- **R28-5 (DOC): the width-4095 RCDIFF is a LOST compile.** It goes from rc 0 to
  rc 1. `[0-9a-f]{4095}` compiled on the unraised merge (engine route). On the
  raised tree it fails: "pattern too large: 612696 bytes of emitted code (limit
  500000)". That is r27 READ-3, main's code-bytes cap, a PLAN row for main's
  stage 2. It is not a run "now admitted". The 22 DIFFs at width 4095 are the
  admitted runs, and the review found them answer-identical.
  - span4kfix_report.md (on the delivered plan-B branch) still carries the old
    wording for both R28-4 and R28-5. This lane did not edit it, because that
    branch is delivered. The ruling names the commit message and the lane report,
    and both now say it right.
- Everything else the raise commit did is unchanged: `MF_WSPAN_POS` 32 -> 4095,
  `MF_MAX_SPAN_POS` and `MF_MAX_AHEAD` retired, the D-hors shift capped at 255,
  d27_frame KPOS, S526 re-aimed, READ-1's two rules, S3254.

## Fixes by id

| id | what | where |
|---|---|---|
| R28-1 | the term rule's witness: a 32-unspelled control that defines, a 40-unspelled case refused naming the term count; plant row S3258; purity pin 13272 | tests/memfn/arm_fixtures.c `pur_long_run`, `pur_long_run_fixtures`; tests/mech/sabotages/S3258_run_part_terms_past_max_term.sh; tests/memfn/run_finder.sh; tests/ci/cloud_mech_shards.tsv |
| R28-4 | `WF_LEGACY_POS` is added, not retired | raise commit message; this report |
| R28-5 | the width-4095 RCDIFF is a lost compile, 0 -> 1, = READ-3 (main's code-bytes cap) | raise commit message; this report |

R28-2, R28-3 (FIX SOON) and R28-6, R28-7 (notes) are not in scope here. The
ruling owes R28-2 and R28-3 to the next kit touch of the seam.

## Validation

Box: dev box, gcc 15.2, `nice`, -j4, `gnutimeout` on each command. No `make
test`, no box jobs, no timing, no cloud. Scratch:
`/var/tmp/pcrec-pcrec/scratch/memfn/raisefix/`.

**The combined approximation tree** (`worktrees/raisefix-comb`, detached, now
removed):
- Base: `7d8043861`, the critic's unraised merge. It is `60c2958ae` merged with
  `lane/covs2afix` at `7983d4798`, which is still that branch's tip. Its
  conflicts were resolved as the review records.
- On top: the raise `ad3f60711` and this lane's fix commit, both cherry-picked
  clean. Tip `1ede3dfde`.

Results on that tree:
- `make` builds clean. `make strict`: clean ("whole tree compiles clean with
  -Werror -Wshadow"). `make test-codegen`: exit 0, 21/21 scripts.
- `make test-memfn-finder` (tests/memfn/run_finder.sh): exit 0, no make error
  line; the purity pin 13272 holds there.
- `fx --purity` (arm_fixtures.c against build/libpcrec.a), no plant: **13272
  passed, 0 failed**.
- **S3258 planted** (the term rule removed, the row's BEFORE->AFTER applied by
  hand, lib rebuilt): **13271 passed, 1 failed**, RED. First FAIL: "long run: a
  part of MF_MAX_TERM + 8 unspelled positions answered rc -1, not run_part_terms'
  term refusal (READ-1, R28-1): mf_define: outside the vocabulary (the window
  family's plan, translated): nterm > MF_MAX_TERM". The later vocabulary check
  refuses, but only after the write; the fixture tells the two apart by the text.
- **S3254 planted** (re-checked on the same tree): 13271 / 1 failed, RED, first
  FAIL the stretch fixture ("rank_n > MF_RANK_MAX").
- **ASan + UBSan**: arm_fixtures.c built against every memfn/src/*.c with
  `-fsanitize=address,undefined -fno-sanitize-recover=undefined`,
  `ASAN_OPTIONS=detect_leaks=0`:
  - with the rule: `--purity` 13272 passed, 0 failed, rc 0, **no sanitizer
    report**;
  - with the term rule planted out: rc 1, `window.c:3158:30: runtime error:
    index 33 out of bounds for type 'mf_term [32]'`. That is the overrun the
    rule prevents, now reached by the in-tree fixture.
  - With leak detection on, the run reports only the fixture harness's own
    arena leaks at exit (`pur_alloc`). Those are not a memory-safety finding.
- **Movers**, unraised merge `7d8043861` vs the raised tip `1ede3dfde`, both
  built here, over the review's 280-pattern list (`pats.txt`, the critic's
  movers.sh):
  - `--window-search-width=32`: 277 SAME, 3 BOTHFAIL, **0 movers**.
  - default width: 277 SAME, 3 BOTHFAIL, **0 movers**.
- `tests/ci/cloud_mech_check.sh tests/ci/cloud_mech_shards.tsv` (in this
  worktree): PASS, 90 shards hold the 1313 sabotage ids exactly once.
  Regenerated by `cloud_units_plan.py mech --measured tests/ci/measured_mech.tsv
  --slots 30 --waves 3 --write`.
- Not run: a mech matrix run of S3258 (`bash tests/mech/run_sabotage_matrix.sh
  S3258`). The plant was shown red by hand, as above.

## STATE AT HANDOFF

- The raise: `lane/memfn-span4k-raise` is ONE commit whose parent is
  `60c2958ae`. It is the commit that carries this report. Its sha is in the
  handback message to the kit manager.
- In that commit: the raise's earlier content, the R28-1 fix, the regenerated
  shard table, this report, `raisefix_deliver.txt` and the history index line.
  `raisefix_rulings.md` is gitignored (`docs/dev/lanes/*_rulings.md`), so it is
  not committed. It was empty at every read.
- Rulings applied: none (the rulings file was empty).
- The scratch worktree `worktrees/raisefix-comb` was removed with `scripts/wtprune
  --apply --force raisefix-comb`.
- OWED: none
