# docs/dev/optloop/rlhtwin/ — [REQ-HANDOFF-L1] measurement (lane rlhtwin, 2026-10-11)

The ONE-BYTE K82 handoff twins on `loglines/ipv6` and `loglines/ipv4`
against today's artifact and the reverse-inner twin (et1twin's method,
re-used). The reading is `docs/dev/lanes/rlhtwin_report.md`. MEASUREMENT
ONLY: nothing under `src/` on this branch changes. The twin's emitter is a
SCRATCH src change on branch `lane/rlhtwin-scratch` (NOT FOR MERGE), built
into `build/rlh/pcrec_scratch`. Every number here is SCRATCH TIER.

Re-uses `../et1twin/etdrv.c` (identity + timing driver), `../et1twin/p2drv.c`
(libpcre2-8 10.46 side) and `../et1twin/twin.c` (the reverse-inner twin) by
path; nothing is copied.

## Files

- `build.sh` — per cell, the variants `o` (today), `h1` (the scratch
  emitter's one-byte handoff, unmodified), `h1m` (h1 with the gate as libc
  memchr), `h2` (h1m with the handoff re-entered at the scan's restart
  point), `r` (et1twin's reverse-inner twin; ipv4's donor built here the
  same way), `p2` (libpcre2-8).
- `mktwin.py` — the hand rewrites of the scratch artifact (h1m, h2, and the
  planted bound for `plant.sh`); each rewrite asserts it matched once.
- `gen_adv.py` — 400 adversarial subjects per cell (the c - K boundary,
  landmark-dense runs, start-set runs longer than K, many dead landmarks).
- `ident.sh` — o against h1/h1m/h2/r/p2 over the loglines short +
  throughput + adversarial subjects, find-all and every startpos;
  `ident.txt` its output.
- `plant.sh` — the failing-direction control (planted bounds K-1, 1, 0);
  `plant.txt` its output.
- `census.sh` — compile-only: every bench pattern through today's pcrec and
  the scratch emitter, the patterns whose `RX_REQ_HANDOFF` moves;
  `census.tsv` its output.
- `extra.sh` — the RE-ENTERED handoff (`mktwin.py reenter-run`) on the two cells whose
  run handoff already ships (kv-quoted K = 32, sfx-64 K = 9): build / ident / time;
  `extra_times.tsv` and `extra_summary.txt` are its timing.
- `time.sh` — pinned-core interleaved timing, both regimes; `times.tsv` raw;
  `summarize.py` / `times_summary.txt` the per-cell reading, including
  each handoff variant's CAPTURE of the reverse-inner saving.

Bench subjects are regenerated in a `git archive` COPY of pcrec-bench
(`build/rlh/bc`; manifests compared equal); pcrec-bench itself is read only.
