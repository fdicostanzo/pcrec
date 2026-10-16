# sweeparm report (2026-10-16)

Code commit a6b933692 on lane/sweeparm (base lane/memfn-fd 39f13e397 = main
063b4a4b4 + docs; `git diff 063b4a4b4 39f13e397 -- src cli lib` is empty).

## Floors (condition 1) - measured, not estimated
Command (one binary on both sides, so a measurement; pinned, detached):

    taskset -c 12-15 python3 scripts/emit_sweep.py --ref-bin build/pcrec --bin build/pcrec \
      --no-self-check --streams c-default,c-vm [--extra-base='-e utf8'] --extra=-fmemfn-simd \
      --no-differ-floor --jobs 4          # likewise --extra=-fcomments

4,624 distinct patterns (5,790 argv rows). DIFFER counts (both sides equal):

| base | flag | c-default | c-vm |
|---|---|---|---|
| byte | -fmemfn-simd | 20 | 19 |
| byte | -fcomments | 4243 | 4244 |
| utf8 | -fmemfn-simd | 15 | 15 |
| utf8 | -fcomments | 4255 | 4257 |

Stamp floors 0 (neither flag moves a start stamp). The four floored cells re-ran
green (`<--` count 0 in all four logs, floors == measured, manifests hit).
`-fcomments` moves nearly every pattern by nature, so its floor alone is weak;
the manifest is the proof the flag arrived.

## Witnesses (condition 2)
`(?i)cat` under `-fmemfn-simd` (byte): 91 diff lines, first hunk
`+#if defined(__x86_64__) ... +static inline size_t rx_reqrun__w16(...)`.
`a` under `-fcomments`: 249 diff lines; first hunks add
`/* Feature set: std1 (modules: classes,modifiers) */` and the
`/* [DD-14.FB] The caller-provided working storage (spec section 10). ...` block.
`a` is not a SIMD mover (cmp identical), so the two witnesses are not shared.

## Plants (condition 3)
`bash tests/mech/run_sabotage_matrix.sh S981` / `S982` (TMPDIR in scratch), at 1adc371b9
(WIP form of the same commit): both `DETECTED`, `emitsweep:1fail/43pass`.
S982's failing line: `arms start rc=1: byte -fcomments c-default differ=0/0 ...
floor=4243/0 <-- MANIFEST b'a' did not differ (sides [False, False])`.
Unplanted `scripts/tests/emit_sweep.py.test`: 14 pass / 0 fail (arms start clean on
the manifest population, 56 arms differing on both sides; the test's floor was >= 40).

## Named arms in the full sweep (decision)
Adding the cells to DIFFER_PINS already puts them in `--arms start` (every DIFFER_PINS
arm). They are NOT added to the default run: the default run has no arms family, and
making it one would add ~8 compile passes per pattern to every run. Run the arm with
`--extra=-fmemfn-simd` / `--extra=-fcomments` (about 1 minute each) or `--arms start`.
The full-corpus `--arms start` was not re-run end to end (35+ arms, ~25 min); each new
cell was run floored via `--extra` instead.

## Charter checklist
1. floors measured at the base, commit + counts in the commit message: a6b933692, table above.
2. witnesses differ in that run: `(?i)cat`, `a`, diffs above; manifests hit on both sides.
3. plants S981/S982 red, unplanted green: tests/mech/sabotages/S981_*, S982_*; matrix above.
4. docs: emit_sweep.py header (`--arms start`), scripts/CLAUDE.md, tests/mech/CLAUDE.md.
