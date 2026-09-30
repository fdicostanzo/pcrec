# s189tri report (2026-09-30) — S189 "timeout" triage

## Verdict
S189 was SLOW, not stuck, and not a plant/anchor problem. Nothing to re-aim.

- Running instance (PIDs 2248/3496/3499) was alive: `run_anchored_diff.sh` worker
  was walking `pats` (3493 lines, position read off the watchdog label vs the
  pattern file: line ~1700 -> 2165 -> 2977 -> 3225 over ~20 min). Left running.
- Cause: `tests/anchored/run_anchored_diff.sh` sharded with GNU-only
  `split -n l/N -d`; BSD split on darwin rejects it and the script's
  `|| { cp pats sh/p00; NSHARD=1; }` fallback silently ran ONE shard (`sh/`
  held only `p00`, despite PROCS=4). ~1 s/pattern under load 11-14 => ~60 min.
  k67's solo re-drive `rc=124` was its wrapper timeout on the same serial sweep,
  not a hang; k67's "expected DETECTED" was luck, not a read.
- The plant itself is fine: it compiles quickly (memo keys on `prune`), and
  the answer-level differential goes red (328+ BAD_DIVERGE observed live).

## Results (darwin, at 8b6db305, build/land3_mech.log)
- S189: DETECTED, `anchdiff:1fail/6pass,corpus:0fail/26pass`, 59 min.
  (Recorded canonical figure was 2fail/5pass; one check fewer red / one more
  green — the fail is still the differential. Not chased.)
- S259: DETECTED, `resource:1fail/28pass`.
- S262: OWED — running in the land3 chain (`build/land3_mech.log`, last line
  `LAND3_MECH_DONE`; harness arm ~25 min). Read its row for DETECTED.

## Changes (lane/land3)
- `tests/lib/shard_split.sh` (new): portable awk line-chunk splitter.
- `tests/anchored/run_anchored_diff.sh`: uses it (was GNU `split -n`). Helper
  unit-checked on a 10-line file (4 shards, concatenation identical).
  End-to-end run of the new script is OWED (a clean-tree `bash
  tests/anchored/run_anchored_diff.sh` should now show several `sh/pNN`
  and finish in ~10 min).
- `tests/mech/sabotages/S189_*.sh`: comment recording the re-drive.
- `tests/lib/CLAUDE.md`: shard_split.sh entry.

## Findings for main
1. SIX more sites carry the same silent-serial `split -n` fallback:
   `tests/codegen/run_dfa_uniform_fold.sh:253`, `run_dfa_stamps.sh:550`,
   `run_form_census.sh:125`, `run_anchored_match.sh:627`, `run_vm_frameless.sh:197`,
   `run_search_pinned.sh:378`. Same one-line swap; not done here (would change
   darwin parallelism of suites mid-chain; wants its own validation).
2. `tests/mech/run_sabotage_matrix.sh` `anchdiff` arm (~line 1492) does not
   pass `PROCS="$INNER_PROCS"` like the reject/harness arms (TT-8 FIX); it
   inherits the caller's PROCS. Not edited: the running chain reads that file.
   After the chain ends, add `PROCS="$INNER_PROCS"` to that invocation.
