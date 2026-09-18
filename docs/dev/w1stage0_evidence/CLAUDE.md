# docs/dev/w1stage0_evidence/ — [REVW.1] wave 1 stage 0's reproduction pieces

Evidence and committed baselines for wave 1's PRECONDITION stage
(`docs/dev/reviews/lens_reports/lens10_emission_kit_charter.md`'s STAGE 0,
plus EP2's two additions from `emitvm_second_pass.md`). See
`docs/dev/w1stage0.md` for all three deliverables' findings and
`docs/dev/lanes/w1stage0_report.md` for the lane's own delivery report.

## Files

- `longprefix_sweep.py` — the long-prefix full-corpus sweep driver
  (deliverable 1). Enumerates every `pattern`/`pattern-esc` block across
  `tests/**/*.rxt` via `--list-source` (dialtrain_byteid_evidence's own
  escape-decode shape), compiles each at `-p rx` and at a legal 60-byte
  prefix (`PCREC_MAX_PREFIX_LEN`, `src/core/limits.def:133`), and — only
  when the 60-byte pcrec compile succeeds — gcc-compiles the emitted `.c`
  under the harness's own GENCFLAGS (`-O1 -std=gnu11 -Wall -Wextra
  -Werror`). Invoked by `tests/codegen/run_longprefix_sweep.sh`, which also
  owns the row-count tripwire against `run_rxtsource_tests.sh`'s
  `CENSUS_BLOCKS` pin. Usage:
  `python3 longprefix_sweep.py <pcrec> <repo-root> <out-tsv> <cc> <gencflags...>`.
- `longprefix_baseline.tsv` — the COMMITTED baseline this sweep produced at
  this wave's branch point (272bf970): 3,938 rows (one per corpus pattern
  block), columns `idx file kind rx_ok rx_err p60_ok p60_err p60_size
  p60_gcc_ok p60_gcc_err pattern`. This is what a FUTURE wave (lens10's
  stage 3, when it lands) diffs its own re-run against to claim
  byte-neutrality reaches the 48+ literal-sized emitter buffers at the
  legal prefix boundary — see the memo for the measured result (1,499 of
  1,500 rx-compiling patterns also compile at 60 bytes; the one exception
  is a size-cap refusal, not a miscompile; zero gcc anomalies).
- `longprefix_sweep.log` — the sweep driver's own stdout from the run that
  produced the baseline above (file/pattern counts, the bucket totals, the
  tripwire's PASS line).
- `listing_reach_census.py` — the listing-reach census driver (deliverable
  3, EP2's addition). Two halves: STATIC — every `vm_rolef(v, "..."` call
  site in `src/gen/emit_vm.c`, attributed to its enclosing function by a
  backward scan for the nearest preceding column-0 function head; DYNAMIC —
  for a given population, compiles each pattern at `--emit-ir` and checks
  whether each call site's format-literal PREFIX (the text before its first
  `%` conversion) appears in the listing text. The PRIMARY census (always
  run) is `tests/codegen/run_ir_listing.sh`'s own fixed `PATTERNS` array,
  extracted from that file so there is only one place the set is typed
  (never hand-copied here). `--corpus` adds a SECONDARY, informational
  census over the whole `tests/**/*.rxt` corpus at default engine
  selection. Usage: `python3 listing_reach_census.py <pcrec> <repo-root>
  [--corpus]`.
- `listing_reach_census.log` — the census's own stdout at this wave's
  branch point: the primary census reaches 27 of 41 `vm_rolef` call sites
  (66%) — every L8 rung family that fires at all fires completely (`vm_alt`,
  `vm_cursor_rep`, `vm_rep`, `vm_rev_emit`, `vm_revdet_rep`, `vm_star`), but
  `vm_counter_phase`/`vm_counter_rep` (the counter rung), `vm_look_behind`
  (lookbehind), `vm_call`/`vm_splice`/`vm_region` (subroutine calls) and the
  two possessive-chain optional-copy helpers (`vm_opt_chain`/
  `vm_poss_chain`) are ENTIRELY UNREACHED by that population — none of its
  11 patterns contains an unbounded-count quantifier past the deterministic
  cursor's reach, a lookbehind, a subroutine call, or an optional-copy
  possessified chain. See the memo for what this means for a future stage 3
  lane's population choice for the `irsb` byte-neutrality arm specifically
  (`tests/codegen/run_ir_listing.sh`'s new BYTE-NEUTRALITY block, deliverable
  2) — it inherits this same population and therefore this same reach gap.

Not archived: the `pcrec` binary used (rebuild from this branch's HEAD) and
the per-pattern `.ir`/`.c` intermediate files the sweeps generate and delete
as they go (both scripts clean up after themselves; only the aggregate TSV/
log is kept).
