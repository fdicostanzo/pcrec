# docs/design/memfn/r17b_prime/fdb1/ — lane fdb1's B1 instruments

R17-b′ step B1 (lane fdb1, 2026-10-16; `../../r17b_prime.md` rev 3 §1.6
[rev3 B6], §4.5 rule 6). Compile-only; never built or run by pcrec's make.

- `shadow_census.py` — two censuses over emit_sweep's population.
  `reader` compiles every distinct corpus pattern at four arms with a
  `-DPCREC_CAND_TRACE` compiler and `PCREC_MF_ASK_TRACE=1` and tallies the
  reader shadow's `MFASK` records and every `CANDORACLE` abort (the gate is
  zero aborts). `manifest` compiles the byte and byte-vm arms with a traced
  harness under `--harness=measures=SET` and writes every slot-FIND shadow
  decision of a set site of two or more members.
- `mk_trace_harness.sh TREE OUT` — builds that traced harness
  (`cli/main.c -DPCREC_HARNESS` linked against `build/libpcrec_mftrace.a`).
- `predicted_movers_B4.tsv` — the COMMITTED PREDICTED-MOVER MANIFEST: the
  manifest run under `memfn/data/sets/kit-interim-grid1.tsv`. B4's movers
  by ID were held to it. Regenerate with `shadow_census.py manifest` (the
  command is in its header); the counts are in `docs/dev/lanes/fdb1_report.md`.
  SUPERSEDED for B4 by `../fdb2/predicted_movers_B4.tsv` (B2's floor-token
  correction, rev 3 [C4]); this file stays as B1 wrote it, B1's record.
