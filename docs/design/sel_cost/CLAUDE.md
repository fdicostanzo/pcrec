# docs/design/sel_cost/ — evidence behind docs/design/sel_cost.md

Scratch-tier evidence for the [SEL-COST] step 1 design (lane selcostdes,
2026-10-03). Nothing here is built or run by `make`.

- `census.py` — the [SEL-SIZE] compile-only census: every corpus block as
  written (auto engine only) plus every pcrec-bench pattern raw and as
  `(?:P)\z`, at byte and utf8, compiled under `--engine=auto`; for each
  auto-DFA artifact of 100 KB or more, and for each artifact that the
  [LIM-2] N1 budget routed to the VM, also the forced-VM (and forced-DFA)
  compile. Population comes from `scripts/cls_identity.py`'s
  `corpus_blocks`. Usage: `REPO=<tree> PCREC=<bin> python3 census.py
  out.json` (about 5 min on the Mac at 4 threads).
- `census_large.tsv` — the derived rows from the 2026-10-03 run (c231ffc1):
  every auto-DFA artifact of 100 KB or more, plus every N1-routed one.
- `percall.c` — the whole-subject timing driver (`rx_search` from 0 in a
  calibrated loop; ns/call). Link it with one `-p rx` artifact.
- `timing_mac.md` — the Mac scratch timings the design cites (T1-T3).
