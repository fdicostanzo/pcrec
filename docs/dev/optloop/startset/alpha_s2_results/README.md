# START-SET stage 2 (VM hat) — Linux alpha, raw results

Driver: `docs/dev/optloop/startset/alpha_s2.sh` (D144 item 1 / add. 1 / add. 3;
`docs/design/startset.md` §7). Read in `docs/dev/lanes/alphas2_report.md`.

- **Pin**: BASE `f3c726d7` (abi 61, main before the VM hat), NEW `57db5152`
  (abi 62, the VM hat), DENY = NEW + `-fno-start-set` (bit 47). Both revs built
  from `git archive` of the box repo; the driver was taken from main `eacde3dc`.
- **Box**: ubuntubudu (AMD Ryzen 5 1600), Ubuntu gcc 15.2.0, glibc 2.43
  (`ldd`: 2.43-2ubuntu2.4), `taskset -c 2`, governor schedutil, boost=1, scalar
  layer only (no `-fmemfn-simd` axis at this pin). `CC=gcc -O2`.
- **Protocol**: 5 launches round-robin base/new/deny x 5 timed passes (>= 50 ms
  loops); a cell = median of per-launch medians; per-cell wait for load1 < 0.5.
- **When**: run 1 = `all` (build + check + time), started 2026-10-06 14:46 UTC,
  header load1=0.90 (the gate then waited per cell). Run 2 = `time` only, same
  built artifacts, started 15:01:37 UTC, header load1=0.15. Run 2 is a
  reproducibility pass added by the lane; the manager's queued command is run 1.
- **Check step**: `check: rc=0` (every subject SHA OK; W cells differ from BASE
  and DENY == BASE under the normalization; C cells identical; base/new/deny
  answer identically on every subject).

Files: `alpha_s2_run1.log` / `alpha_s2_run2.log` (verbatim driver output);
`alpha_s2_run1.tsv` / `alpha_s2_run2.tsv` (the result table rows only, TAB
separated: cell, subject, unit, base, new, deny, new-base, floor, verdict).
No other result TSVs exist: the driver prints its table to stdout.

Caveat: ~10 minutes into run 1 a second `time` instance was launched by mistake
(the lane misread run 1's progress) and killed by `scripts/safekill` within ~40 s,
before its first load-gate-passed launch could be observed; it overlapped only run 1's
`union-srch` control cells. Those cells were re-read in run 2 and agree.
