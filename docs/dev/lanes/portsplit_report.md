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

## 5. Validation (Mac, PROCS=4) — OWED, RUNNING DETACHED
Box: load ~9-11 the whole time (land3's mech chain); wall times are contended
and the p1/p4 pairs run back to back, so read RATIOS, not absolutes.
Chain (nohup+caffeinate, started 00:48): `/tmp/portsplit/chain.sh`, then
`/tmp/portsplit/chain2.sh` (waits for `CHAIN_DONE`, then S189 solo).
- Summary: `/tmp/portsplit/summary.txt`; completion lines `CHAIN_DONE` (six codegen
  scripts at PROCS=4 then PROCS=1, then run_anchored_diff at PROCS=4) and
  `CHAIN2_DONE` (S189 solo, PROCS=1 so INNER_PROCS = ncpu).
- Per-script logs `/tmp/portsplit/<name>_p4.log` / `_p1.log`, `anchored_diff_p4.log`,
  `s189.log`. Each summary row: rc, wall, load, `checks passed/failed`, and the
  `shard_split: wrote N shards` line (confirms N actually ran).
- Pass criterion: p4 and p1 rows show identical passed/failed counts; p4 rows say
  `wrote 4 shards`; p4 wall < p1 wall. PROCS=1 IS the old behaviour (old fallback =
  one shard), so p1 is the "before" leg.
- Rows landed so far when this report was written:
  - dfa_stamps p4: rc=0, 51 s, 33 passed / 0 failed, `wrote 4 shards (3493 lines)`.
- GNU semantics: the helper uses only awk + wc + ls, no split at all, so there is
  no GNU/BSD divergence to test; the one behavioural difference from `split -n l/N`
  is chunk boundaries (GNU splits by bytes-aware line chunks), which no script
  depends on (each shard is an independent pattern list; verdict tokens are summed).
  `gsplit` was not needed.

## 6. S189: 2fail/5pass (recorded) vs 1fail/6pass (s189tri) — OWED, hypothesis only
Both are 7 checks; one check that was red at 312612b is green now. Not caused by
shard count: sharding only partitions the same pattern list and the tallies are sums.
What changed in the file since 312612b: only ucpu3's reporter split (23263eb2,
per-kind detail tags, no change to which counts trip a `bad`), so the difference
is in the compiler/corpus, not the script's own logic. Candidates for the second
red then: the `n_infra`/`n_cc` checks or a §2 capture witness. The sabotage's
current failing check is named by `FAIL:` lines in `/tmp/portsplit/s189.log`
(KEEP=1, the row's `anchdiff.log` is under the printed scratch dir).
Next step for whoever finishes: read which single check is red now; then answer
"was the other one red at 312612b" by building 312612b + the S189 plant in a
scratch tree (or `git log 312612b..HEAD -- src/core/compile.c`, 68 commits) and
re-record `SAB_DOC_FIGURE` by MECHANISM (the answer-level divergence check is the
detector; the second red, if any, is incidental) rather than by count.
