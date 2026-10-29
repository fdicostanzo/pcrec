# docs/dev/optloop/ — the optimization loop's per-cycle analyses (D119)

One directory per project, one file set per CYCLE of [OPTLOOP]. A cycle's analysis step
([OPTLOOP.N.analysis]; cycle 1's is also [BENCH-REVIEW]) delivers `cycleN_analysis.md` here with the
machine-readable table it is written against and the scripts that produced it. These are
MEASUREMENT-AND-ANALYSIS documents (`docs/dev/`'s sense), not designs.

## Standing rules

- A lane NEVER edits `../plan.md`: plan rows a cycle proposes are written IN the analysis and ratified into
  plan.md by Frank.
- A design note for a ratified mechanism goes to `docs/design/`; an implementation's own record goes to
  `docs/dev/lanes/`.
- Everything here is read-only with respect to the pcrec-bench checkout: scripts read its reports,
  `patterns.rxt` and `captext.py` and write nothing there. Throughput subjects are regenerated into a scratch
  directory and checked against the bench's committed `manifest_throughput.tsv` hashes.
- Standing note on these scripts: the cycle-1 scripts carry the authoring session's scratchpad path in an
  `SP` constant at the top (and `stamps.py`'s `P`, the compiler path). They are archived as the reproduction
  record, not a runnable harness: re-point `SP`/`P` before re-running. A repo path must not be baked in
  (`capsview.py` cites this note). `capsurvey_census.py` instead takes paths from the environment
  (`PCREC`, `BENCH`, `OUT`) and runs as it stands.
- Read `cycle1_analysis.md` §0 first for the target criterion: `pcre2-jit` is never the target,
  `vectorscan` is excluded, `rust` counts with its SIMD component separated; class weighting applies uniformly.
- Numbers in `cycle1_caps_view.md` read off `capsview_data.json`; never re-derive by hand.
- Measurement-only readings obey D77 (build under measurement): state the rule and the measurement that would
  trigger building it; do not build.
- `gapreport.sh` copies the hand-kept `judgement_gapreport_*.md` verbatim into the report; a re-run never
  overwrites it.
- Maintenance: add a cycle's (or lane's) files and a one-line description here when its analysis lands.
  Every dir with its own `CLAUDE.md` is indexed by it.

## Files and subdirectories

Cycle 1
- `cycle1_analysis.md` — [OPTLOOP.1.analysis]: 128 cells ranked by D119, cause buckets from D81 stamps, five mechanisms, six proposed rows.
- `cycle1_rows.tsv` — machine-readable ranked table (made by `table.py`).
- `parse_pats.py`, `stamps.py`, `rank.py`, `join.py`, `scale.py`, `mdtable.py`, `table.py` — cycle-1 reproduction scripts (pattern parse, `RX_*` stamp reads, ranking, joins, scaling, table renderers).
- `p2info.c` — `pcre2_pattern_info` structural probe (built against Homebrew 10.48, not the 10.46 reference; see analysis §6).
- `cycle1_caps_view.md`, `capsview.py`, `capsview_data.json` — [OPTLOOP.1-CAPSVIEW]: shipped default re-ranked against capture-bearing engines only; script and its single data source.
- `cycle1_nocaps_view.md`, `nocapsview/` — [OPTLOOP.1-NOCAPSVIEW]: `auto-nocaps` against non-capturing configs (I-99/I-100 classification; `rust-default` is NOCAPS); §6 cross-class anomaly query (I-101). Open item: caps view not yet revised to I-100.
- `cycle1_profile.md` — [OPTLOOP.1.profile]: I-85 profile pass read against analysis §3's EXPECT lines.
- `runs/2026-09-22-i85-405668e9/` — [I-85] raw profile transcripts (own README.md).
- `cycle1_ledger_reading.md` — reading of the batch-1 after-measurement (O-45) against the D119 bar: per-mechanism verdicts, null control, G1/G2/G3 rules; §9 reconciles O-48/I-93 (G3 refuted on x86_64).
- `b1ledger/` — its instruments (subject census, artifact-identity census, cost model). Own CLAUDE.md.
- `runs/2026-09-23-i89A-8d716693/` — I-89 block (A) raw `make test-axes` transcript (own README.md).
- `axes_reconciliation_2026-09-23.md` — [AXESREC]: O-47's three oddities are one reporting offset, not a pcrec finding.
- `runs/2026-09-23-i93-8d716693/` — five discrimination blocks (I-93/O-48) raw transcripts (own README.md).
- `captures_via_dfa_survey.md` — survey/fit analysis of capturing-via-DFA (lane capsurvey); read §1 first. Not a cycle.
- `capsurvey_census.py`, `capsurvey_census.tsv` — its §1.5 compile-side census (env-path script).

Cycle 2 preparation and reading
- `c2/` — cycle-2 prep reproduction pieces. Own CLAUDE.md.
- `firstset_design.md` — [OPT-FIRSTSET] design note (§0 first; narrowing as stated in cycle1 M3 is unsound; §4.6 reconciles against real `rx_search`).
- `reqpos_census.md` — [OPT-REQPOS] D77 census (tier 2 population of two; tier 2b has the population).
- `onepass_census.md` — one-pass reach census (candidate (c) survives; M-B undecided, Linux work).
- `linux_ask_i89.md` — draft I-89 executor request bundle (blocks A-C), annotated with the AXESREC correction.
- `cycle2_batch2_reading.md` — reading of batch-2 after-measurement (O-49); asks I-102/I-103/I-104.
- `b2ledger/` — its instruments (`stampdiff.py`, `nullctl.py`, `costmodel.py`, JSON outputs). Own CLAUDE.md.
- `runs/2026-09-23-o49-b1885a83/` — archived O-49 sources and ledger.
- `runs/2026-09-23-o51-i103/` — archived O-51 ([B83]) sources (own README.md).
- `cycle2_i103_reading.md` — reading of O-51 against I-103/I-103a; §4 designs the cycle-3 ask (I-105).
- `vmlit_trigger_read.md` — [OPT-VMLIT] trigger read (gcc never fuses a compare chain; row stays not-started).
- `cycle2_admitfix_reading.md` — reading of [B84]/O-52 ([OPT-PRECHECK-ADMIT]); `admitfix/` — its instruments and transcripts.
- `wordfold_census.md` — [WORD-FOLD] D77 census; `wf/` — its instruments (`wf_run_probe.c` etc.).
- `waf_attribution.md` — compare_stack.md §6.1 S3 WAF-cell attribution; `waf/` — twin generator, answer checker.
- `s1/` — counts behind `docs/design/litscan_s1.md`. `s2a/` — `s2a_movers.py` mover biconditional. `s4/` — bench census and spelling probes behind `docs/design/litscan_s4.md` (own CLAUDE.md).
- `reqrunenc_census.md`, `reqrunenc/` — [OPT-REQRUN-ENC] D77 census and instruments.
- `b108_reading.md`, `b108/` — reading of [B108]/O-64 ([OPT-LITSCAN] S2a) and instruments (`fncmp.sh`, `offs.py`, `transcript.txt`).
- `cycle2_close.md` — [OPTLOOP.2] CYCLE 2 CLOSE (docs-only; residuals proposed, not filed).

Later rounds
- `gapreport_2026-10-03.md`, `gapreport_2026-10-05.md`, `gapreport_2026-10-11.md` — [OPT-GAPREPORT] instances 1-3 (D144 addendum 2); `gapreport/` — instruments, data and `gapreport.sh` (`--group NAME|latest --out ...`, `--check`, `--peer-group`). Own CLAUDE.md.
- `judgement_gapreport_2026-10-05.md`, `judgement_gapreport_2026-10-11.md` — hand-kept judgement files (the latter a lane draft the manager replaces or extends).
- `lossreview/`, `lossreview_charter.md` — [LOSS-REVIEW] phase-1 per-route attributions (`dfa.md`, `vm.md`, `misc.md`) and charter. Own CLAUDE.md.
- `sellit_read.md` — SEL-LIT desk read (verdict SYNTHETIC ONLY).
- `k87twin_report.md`, `k87twin.sh`, `k87twin_sum.py`, `k87twin_align.sh`, `k87twin/` — [K87] range-spelling Linux twin with alignment control.
- `revend_census.md`, `revend/` — [OPT-REVEND] census (filed, not scheduled) and instruments. Own CLAUDE.md.
- `startset/` — [START-SET] alpha blocks (round 2; `alpha_s2.sh` ...).
- `artrev/` — [ARTREV] (D150) charter, selection, pilot setup, collected reviews, `confirm/` S4 results, `report_pilot.md`, `generalize.md` + `gen/`; harness in `studies/artrev/` (identity rules in `studies/artrev/CLAUDE.md`).
- `round3_selection.md` — DRAFT round-3 slate for Frank.
- `primed_2026-10-29.md` — the PRIMED list (Frank 2026-10-29): candidates from the subst/unusual/regular readouts, each with evidence, state, design and remodel overlap; next round takes 4-6 after [INLINE-C]; one build at a time until then.
- `et1twin/` — [ENG-TACTICS] stage-1 K12 recount and reverse-inner twins (reading `../lanes/et1twin_report.md`). Own CLAUDE.md.
- `rlhtwin/`, `rlhbuild/` — [REQ-HANDOFF-L1] twins and as-built identity/timing (readings `../lanes/rlhtwin_report.md`, `rlhbuild_report.md`). Own CLAUDE.md each.
- `rewtwin/` — [OPT-REVEND] `rev-end-width` twin (reading `../lanes/rewtwin_report.md`). Own CLAUDE.md.
- `matchsplit/` — [MATCH-SPLIT] STEP 0 class-mix survey (reading `../lanes/mssurvey_report.md`). Own CLAUDE.md.
- `nullanch/` — [NULLABLE-ANCH] STEP 0 census (reading `../lanes/nullanch0_report.md`). Own CLAUDE.md.

## Pointers

`../plan.md`, `../decisions.md` (D77, D119, D144, D150, D151), `docs/design/` (design notes cited above), `../lanes/` (lane reports), pcrec-bench's `docs/dev/outbox_to_pcrec.md` / `inbox_from_pcrec.md`.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__dev__optloop.md
