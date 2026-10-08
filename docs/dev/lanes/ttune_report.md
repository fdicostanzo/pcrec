# ttune2 report — [TT-JTUNE] (2026-10-08, sonnet, admin)

## Summary (a fresh agent resumes from here)
Delivered `scripts/perfrun`: a chain calls `scripts/perfrun --label NAME --
LOG [vars]` instead of its raw `make -k -jN -Otarget test`. It picks a shape
from `scripts/perfrun.shapes` (16x16, 16x1, 8x2, 4x4, 4x3, 2x8, 6x16; least
uncontaminated samples first; `--shape J,P` overrides), runs `gnutimeout 2700
make --debug=j ...` with PROCS=P, writes LOG byte-identically (the
`--debug=j` lines are diverted by `sectiontimes stamp SIDE`), samples CPU with
`scripts/cpusample.sh`, appends one row, writes `LOG.perfrun` with a verdict
class (green / K44-ONLY / LOAD-SUSPECT / WALL-TIMEOUT / RED-REAL), and exits
with make's rc. Data goes to the MAIN tree's gitignored `build/perf/ttune/`
(per-run files, no merge conflicts); `scripts/perfrun --fold` (in main) appends
them to `docs/dev/ttune_ledger.tsv` and copies samples/sections to
`docs/dev/ttune_ledger.d/`. Evidence, triage rule, decision rule and default
options: `docs/dev/ttune_measurement.md`. BOILERPLATE.md and memfn/CLAUDE.md
now route make test through perfrun. Plan row [TT-JTUNE] STATE:started.

Profile #0 headline (decfbB0, `-j6`, PROCS=16, 13m32s, rc 0): only the last
6.5 min were sampled (sampler started late); mean busy 82.9%, load1 up to 84
with 148 running (oversubscription: crosscheck.py 35 + run_g2 18 + harness 10
under -j6), but busy stayed 88-99% there, so it costs K44 exposure, not wall.
One serial stretch (~45 s at 53-59% busy) and a ~25 s tail (run_g2/startset).
No Makefile reorder proposed: no per-section times exist for that run;
perfrun's sections.tsv will supply them (D77).

## Validation (light only; no make test run)
- Selftests through the wrapper on `test-reject test-parse` (and a deliberately
  missing target): rc passthrough (0 and 2), log free of debug lines
  (grep child|token = 0), row/samples/sections written, cpu_s non-zero,
  contamination detected (decfbB0 chain running), RED-REAL classification,
  `--fold` idempotent in a throwaway clone, `--next` = 16,16 on an empty ledger.
  Selftest rows were deleted from build/perf/ttune afterwards.
- NOT validated: a full-length run, the K44-ONLY classification on a real K44
  red (heuristic: log greps of `counterk.rxt:1807` + FAIL-ish text and `CPU
  limit exceeded`; check the first real red against it), the sampler over 40+
  min.

## Open for the manager
- Chains must be edited to call perfrun (BOILERPLATE.md has the template);
  existing armed chains (decfbB0's chain.sh) are untouched.
- `scripts/perfrun --fold` in main after each batch, then commit the ledger.
- Concurrent chains that start together pick the same "least-sampled" shape.
- scripts/sectiontimes was the predecessor's file; kept and extended
  (side-file split mode).
