# docs/design/memfn/regime_eval/ — [REGIME-EVAL]'s replay PROTOTYPE

Lane regeval, 2026-10-13. The design note is `../regime_eval.md`; this
directory only shows that its replay shape works on EXISTING data. No clock,
no build, no new measurement.

| file | role |
|---|---|
| `replay_proto.py` | the replay on the grid1 slot's finished logs (`worktrees/memfn-slot/grid1/`): knowledge records from facts + counters, regime_tables rev 0.2's rows as declared data walked first-match under S0-S3, regret per regime, fixed-form policies, the failing-direction controls and the A/A control. Imports `../../../dev/lanes/gridread/grload.py`'s LOADERS only, never `gridread.py` (the cost model). `python3 -I replay_proto.py [--strict] [OUT]` |
| `proto_out.txt` | its output, PICKABLE population (every form the table can pick timed) |
| `proto_out_strict.txt` | its output, STRICT population (gridread §6.2's 101 groups); S0 reproduces regime_tables §3 exactly |

Inputs read (sha256 as in `../../../dev/lanes/gridread/SHA256SUMS`):
`time_F1.log` d1782380…, `counts.tsv` ffe782b5…, `subj_facts.tsv` 0156fb6c….

IN SAMPLE: the thresholds were read off this same slot, so these runs are a
self-consistency check of the table against its fit population, not the
held-out judgement `../regime_eval.md` §3 pre-registers.
