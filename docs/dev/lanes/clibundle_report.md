# Lane clibundle report ([SIZE-CAP-FLAG] + [MEMFN] RQ-1)

Branch `lane/clibundle` off 3b43b33d; two commits (059998e4 size-cap, ce466a15
memfn) plus this report. Sonnet. Never merged.

## 1. [SIZE-CAP-FLAG] (059998e4)
- `--fast-or-fail` -> `--size-cap=refuse|degrade` (default `degrade`; a later
  `--size-cap=` wins; other values refused). Old spelling RETIRED, NO alias
  (unknown option). `PCREC_FAST_OR_FAIL` -> `PCREC_SIZE_CAP_REFUSE` (bit 41,
  masked out of `rx_info.flags`, unchanged). `fof` column name kept (internal).
- Every live reader renamed by grep (cli, lib, compile.c, emit_dfa.c, tests,
  sabotage anchors S421/S423/S631 text only; sabotage FILE names and S-ids kept
  so the anchors TSVs stay keyed), spec hunks cli.md (section, revision
  history), limits.md, tuning.md, registry.md, CHANGELOG [Unreleased]. Historical
  records (journal, reports, decisions, plan_completed, reviews) untouched.
  docs/guide had no mention.
- Listing: 11 `fallback` rows' `applies` text. Declared in
  `docs/design/dec_fallback/listing_declared_clibundle.tsv`; `listing_diff.py`
  parent(3b43b33d, built from git archive) vs new: "EXACTLY AS DECLARED" (11
  cells). `make test-registry` green with no re-pin needed (no pin reads the text).
- No artifact byte moved: not an abi event.

## 2. RQ-1 `--memfn=` (ce466a15)
- `pcrec_options.memfn` (`const char *`, appended last), CLI `--memfn=OPTS`,
  a config's raw `pcrec --memfn=` line (same parser). Config directive = the raw
  line; no typed `memfn` row was added (the brief said "directive"; say if a typed
  row is wanted: it touches rxt_format.md/schema).
- Validated once per compile (`attempt == 0`) by `pcrec_memfn_opts_check`
  (memfn_sites.c) -> kit `mf_opts_check`; refusal text is the kit's, with the
  compile's usual `pcrec: ` lead and ` (pattern offset 0)` suffix from
  `pcrec_ctx_fail` (not the kit's text alone; D26 says do not gold-plate).
  `pcrec_memfn_site` copies `cx->opt->memfn` into every site's `opts`.
- Composition: silent file-wins (config value overwrites the CLI's), verified.
  Bug found and fixed: the raw line's tokens are freed after the parse, so the
  pointer dangled; `cli_keep_string` keeps a copy (reachable via a static, so
  LSan stays quiet).
- Spec: cli.md (new section + history), registry.md §6 ("How a row is reached",
  inert at `-fno-memfn-simd`), option_sets.md table row; lib/pcrec.h hunk.
- Tests: 7 cases in `tests/cli/run_cli_tests.sh` (size-cap identity, bad
  value, retired spelling; memfn empty identity, kit refusal text, config wins).
- Kit side: the registry (`options.def`) is EMPTY, so no non-empty string is
  accepted today; the SUCCESS path of a real row and the SIMD-layer inertness
  at `-fno-memfn-simd` cannot be exercised from pcrec yet (the spec states them;
  the kit's G2 tests cover `mf_site.opts`). Nothing missing that needs a request
  now; the first row (R4d) should add a pcrec cli case with a real `no-NAME`.

## Validation
- Zero movers: `scripts/emit_sweep.py --ref 3b43b33d --tree-rev HEAD --every 10
  --jobs 8 --streams c-default,c-vm,emit-ir,composition,facts,emit-ir-auto,stderr`
  (`build/clibundle/sweep.log`): every stream movers=0 asymmetric=0, SELF-CHECK
  PASSED (argv 5431, composition 373). Partial population (`--every 10`), no
  variant arms; dumps by listing_diff above.
- `make strict` clean; `make test-registry`, `test-cli`, `test-codegen` rc 0
  (build/clibundle/*.log); all pinned to CPUs 0-7.
- OWED (armed detached, waits on `worktrees/clibundle/.lift`): `build/land/chain.sh`:
  make, perfrun `make test`, strict, testscripts, mech VALIDATE_ONLY, mech rows
  S421 S423 S631 (renamed anchors) and S313 S236 S571 (anchors in files this
  touched; derived by grepping SAB_FILE; the fallback anchor tool is B-specific).
  Trailer `build/land/trailer.log` ends `== CHAIN DONE`; verdict from
  `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/land/test.log` with
  `test.log.perfrun`; each mech row from its `== mech run COMPLETE`.

## Proposed plan-row text
[SIZE-CAP-FLAG] STATE:done (lane clibundle 059998e4: `--size-cap=refuse|degrade`,
`PCREC_SIZE_CAP_REFUSE`, no alias, 11 declared `applies` cells, 0 movers).
[MEMFN] RQ-1 STATE:done (ce466a15: `--memfn=` / config raw line / `pcrec_options.memfn`,
kit-validated once per compile, copied to every site's `opts`, silent file-wins;
0 movers). Both: pending heavy chain.

## Bench inbox note TEXT
> [inbox] pcrec CLI change (lane clibundle). `--fast-or-fail` is RETIRED (no
> alias, an unknown option now); the spelling is `--size-cap=refuse` (and
> `--size-cap=degrade`, the default). Library: `PCREC_FAST_OR_FAIL` ->
> `PCREC_SIZE_CAP_REFUSE`. Your adapter does not pass the flag (only
> testees/pcrec/CLAUDE.md:1001 and old inbox text name it); update that line.
> `--list-axes`: 11 `fallback` rows' `applies` text now reads `--size-cap=refuse`
> instead of `--fast-or-fail`; no row/axis/column moved. New: `--memfn=OPTS`
> (opaque kit string, inert/empty today). No artifact byte moved.
