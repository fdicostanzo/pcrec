# Lane k86fix report (sonnet, writer) — K86 spelling-dependent precedence

Branch lane/k86fix; code commit 9fedfb6d. Not merged.

## Change
- `cli/main.c` `apply_target`: after a config's raw `pcrec` line is reparsed (which overwrote the CLI's options), an explicit CLI `--engine` is restored and a conflict reported (`this file's \`pcrec\` line --engine=X`), unless a typed `engine` row exists, which reports its own conflict against the restored value (one report, not two). The tune report's first word is `CLI` only when the losing value is the CLI's own; a raw-line value is labelled `this file's \`pcrec\` line`.
- `docs/spec/cli.md` §1.1: `flags`/raw `-f` bits UNION across sources (contradicting bits refuse, A1/A2); raw `--engine` follows the typed rule; tune report names its source. The engine/tune sentence no longer lists `flags` as file-wins.
- Tests: `[K86]` block in tests/rxtsource/run_rxtsource_tests.sh (7 cells: D3 typed/raw with CLI vs silent, CLI vm over raw dfa, E3 CLI-labelled and raw-labelled). Verified failing before the fix (3 FAIL: D3 raw, converse, E3 raw), all pass after (standalone extraction of the block).
- `docs/design/option_sets_measurements/out/cross_source.txt` regenerated; cases.sh rerun diff vs pre-fix: ONLY cells D3 (engine vm -> dfa, new err line) and E3 (label) changed.
- Abi: not an event; no emitted scaffolding changed. `make strict` clean.

## Same-class defects NOT changed (reported)
E2, H1, H4, G2: a config's raw `--tune=`/`--unroll=`/`--step-budget=`/`-e` beats an explicit CLI value silently (the typed spelling reports for tune, E1; budget/encoding typed rows are silent too, H3/G1). That is the R4 generalized-report ruling, stderr only, outside K86's D3/E3 scope.

## Validation
OWED: tests/cli + rxtsource sections and `make test` (background, suite lock) — see the handback message for log path and completion line.
