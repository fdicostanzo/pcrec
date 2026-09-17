# studies/lim2_m2/ — [LIM-2]/dfamin M2, the dominance-prize measurement

Measurement instrument, not product code (never built or run by pcrec's
top-level `make`/`make test` — `studies/CLAUDE.md`'s standing rule). See
`docs/dev/dfamin_m1m2.md` §3/§4 for the full methodology, the approximation
this instrument DELIBERATELY takes (the study's own "illegitimate stand-in"
for candidate B's general simulation preorder), and the results.

**This directory's own harness LINKS a probe committed separately in
`src/core/internal.h`/`src/ir/nfa.c`/`src/ir/dfa.c` (the `[PROBE-M2]`
commit), gated on `getenv("PCREC_PROBE_M2")` and a no-op by default (see
`dfamin_m1m2.md` §5/§6 for the disposition and the byte-identity check).
That commit is measurement-only and does not land** — a future reader who
finds `pcrec_probe_m2_dropped`/`pcrec_probe_m2_total` undefined at link
time is looking at a tree where the manager has already dropped it per
that disposition; this directory's binary is then unbuildable until either
the probe commit is re-applied or this directory is retired with it.

## Files

- `lim2_m2.c` — the instrument. Links `../../build/libpcrec.a`; reads the
  probe's counters as `extern`.
- `Makefile` — `make CC=gcc-16` / `make clean`.
- `run_m2.sh` — the sweep driver: runs the binary TWICE (`PCREC_PROBE_M2`
  unset, then `=1`) over the shipped corpus plus three force files
  (`tests/base/k18_cost_gates.rxt`, `tests/counterk/counterk.rxt`,
  `docs/dev/dfamin_m1m2_evidence/k25_chain_ladder.rxt`).
- `m2_baseline.tsv` / `m2_baseline.summary.txt` — committed baseline
  output (probe disabled).
- `m2_pruned.tsv` / `m2_pruned.summary.txt` — committed pruned output
  (probe enabled); note one row fewer than baseline — the K18 census
  witness REFUSES under the stand-in (`dfamin_m1m2.md` §4b).

Maintenance: update this file when files are added/removed or their roles
change (matching every other `studies/*/CLAUDE.md` in this tree).
