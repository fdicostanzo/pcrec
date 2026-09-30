# portsplit report (2026-09-30) — silent-serial `split -n` sites

Lane `portsplit` (sonnet), branch `lane/portsplit` from `lane/land3` (d1e2cdc7).
Brief: replace every GNU-only `split -n` with `tests/lib/shard_split.sh`, make a
short-shard outcome LOUD, add the missing `PROCS="$INNER_PROCS"` on mech arms,
validate at PROCS=4 on the Mac, explain S189's 2fail/5pass vs 1fail/6pass.

## 1. Sites found (grep `split .*-n|NSHARD=1|cp .*pats.*p00` over tests/, scripts/, Makefile)
Exactly the six s189tri named; no others (the only other `split` hits are awk
`split()` calls and prose). All six carried the identical two-line
`split -n "l/$NSHARD" -d ... || { cp ... p00; NSHARD=1; }`:
`tests/codegen/run_dfa_uniform_fold.sh`, `run_dfa_stamps.sh`, `run_form_census.sh`,
`run_anchored_match.sh`, `run_vm_frameless.sh`, `run_search_pinned.sh`.
Each now sources `tests/lib/shard_split.sh`, calls `shard_split "$NSHARD" pats sh/p || exit 1`
and sets `NSHARD="$SHARD_COUNT"`. The last line matters: `run_vm_frameless.sh:250`
and `run_search_pinned.sh:491` iterate `seq 0 $((NSHARD-1))` over `sh/pNN`, and
`run_form_census.sh:253` throttles on `$NSHARD`, so NSHARD must be the count of
files actually written. `run_anchored_diff.sh` got the same two lines.

## 2. Helper changes (tests/lib/shard_split.sh)
- Distribution changed from ceil(lines/N)-sized chunks to balanced
  `int((NR-1)*N/lines)`, clamped: exactly min(N, lines) contiguous shards
  (ceil chunking could write fewer than N for lines >= N, e.g. 9 lines / N=4 -> 3).
  Checked on a 10-line file for N = 1, 4, 10, 12: concatenation of shards is
  byte-identical to the input, sizes 3/2/3/2, and N=12 -> 10 shards + NOTE.
- LOUD: sets `SHARD_COUNT`; fewer shards than asked -> stderr
  `shard_split: NOTE: asked for N shards, wrote M`; empty input, awk failure or zero
  files -> `shard_split: FATAL` and return 1 (callers `|| exit 1`). This is the
  learnings.md §3 "population nobody counts" repair: the old fallback made the
  loss of parallelism indistinguishable from slowness.
- `SHARD_SPLIT_VERBOSE=1` prints the count on every call (used by the validation).

## 3. Mech matrix (tests/mech/run_sabotage_matrix.sh)
Listed every script under tests/ that reads `PROCS` and checked each matrix
invocation for `PROCS=` on its command line. Four arms lacked it and now carry
`PROCS="$INNER_PROCS"`: `anchdiff` (run_anchored_diff.sh), `anchoredmatch`,
`searchpinned`, `vmframeless`. The reject/harness/clskit/expansion arms already
had it. The other readers (dfa_stamps, dfa_uniform_fold, form_census,
tiered_entry, lookaround_identity, axes, ksweep, size_log) are not invoked by any
matrix arm. tests/mech/CLAUDE.md gains a paragraph under the [TT-8] section.

## 4. Docs
tests/lib/CLAUDE.md (helper entry rewritten), tests/mech/CLAUDE.md, docs/testing.md
(one stale `split -n l/N` phrase), plus comments at the six sites.

## 5. Validation (Mac, PROCS=4) - DONE (filled by psfinish, 2026-09-30)
Chains `/tmp/portsplit/chain.sh` and `chain2.sh` both completed (`CHAIN_DONE`,
`CHAIN2_DONE` in `/tmp/portsplit/summary.txt`). PROCS=1 is the old behaviour (old
fallback = one shard), so p1 is the "before" leg and p4 the "after". Every row rc=0.
Box load was ~6-25 the whole time (land3's mech chain) and the pairs ran back to
back, so read the RATIOS; the load column is the 1-min load at start of each leg.

| script | p4 pass/fail | p1 pass/fail | shards p4 | shards p1 | wall p4 | wall p1 | p1/p4 | load p4 / p1 |
|---|---|---|---|---|---|---|---|---|
| `run_dfa_stamps.sh` | 33/0 | 33/0 | 4 | 1 | 51 s | 117 s | 2.3x | 8.45 / 8.33 |
| `run_dfa_uniform_fold.sh` | 6/0 | 6/0 | 4 | 1 | 77 s | 169 s | 2.2x | 16.00 / 6.15 |
| `run_form_census.sh` | 1/0 | 1/0 | 4 | 1 | 148 s | 359 s | 2.4x | 13.24 / 6.81 |
| `run_anchored_match.sh` | 20/0 | 20/0 | 4 | 1 | 77 s | 146 s | 1.9x | 7.31 / 7.28 |
| `run_vm_frameless.sh` | 6/0 | 6/0 | 4 | 1 | 66 s | 166 s | 2.5x | 24.67 / 8.12 |
| `run_search_pinned.sh` | 17/0 | 17/0 | 4 | 1 | 156 s | 216 s | 1.4x | 7.56 / 7.17 |
| `run_anchored_diff.sh` | 7/0 | (no p1 leg) | 4 | - | 1207 s | - | - | 12.88 |

Result: p4 and p1 pass/fail counts are identical on all six paired scripts; every
p4 leg says `wrote 4 shards (asked 4, 3493 lines)` and every p1 leg `wrote 1`; p4 is
faster on all six (1.4x-2.5x; the vm_frameless p4 leg ran at load 24.7 and
search_pinned is dominated by a serial tail, so neither ratio is a clean scaling
figure). No count mismatch, so no finding to diagnose. `run_anchored_diff.sh`
unplanted at p4: 7 passed / 0 failed (the baseline S189 is scored against).
GNU semantics: the helper uses only awk + wc + ls, no `split`, so there is no
GNU/BSD divergence to test; the one behavioural difference from `split -n l/N` is
chunk boundaries, which no script depends on (each shard is an independent pattern
list; verdict tokens are summed).

## 6. S189: 2fail/5pass (recorded) vs 1fail/6pass (s189tri) - PARTLY DONE, ONE RUN OWED
Today's run (`/tmp/portsplit/s189.log`, rc=0, DETECTED, KEEP=1 scratch
`.../pcrec-mech-sabotage.CkOhse/S189-anchored-machine-unpruned/anchdiff.log`):
7 checks, 6 pass, 1 red. The single red check is
`FAIL: 185 patterns DIVERGE between the unwrapped form and the search-and-filter
form` (the answer-level divergence detector, the row's point). Green today: RAN
to a verdict, built under -O1 -Werror, deny flag refuses nothing, population 1642
(floor 1150), section 2 capture arrays over 976 cells, section 2 all 8 witnesses.
Which check was the SECOND red at 312612b is not yet known (candidates: the
population-floor check or a section 2 check, both of which have been re-derived
since). OWED: a scratch worktree `worktrees/psfinish-312` (312612b, planted by
`adfa, true, false` -> `false, false` at src/core/compile.c:143, build.log
`/tmp/portsplit/b312_build.log`) runs `tests/anchored/run_anchored_diff.sh` at
PROCS=2 detached; log `/tmp/portsplit/b312_anchdiff.log`, completion line
`B312_DONE`. Read its `FAIL:` lines: two FAILs, one of them not the divergence one,
names the second red. Then re-record `SAB_DOC_FIGURE` in
tests/mech/sabotages/S189_anchored_machine_unpruned.sh by MECHANISM: the divergence
FAIL is the detector; the count (now 1fail/6pass) is incidental. Delete the scratch
worktree afterwards (`git worktree remove --force worktrees/psfinish-312`).
