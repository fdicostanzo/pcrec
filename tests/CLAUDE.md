# tests — test framework and corpus

Houses the .rxt test format, test runner, and per-feature test cases. Each feature module gets its own subdirectory (e.g., base/ for base-tier regexes). The harness compiles each pattern, builds a driver, and diffs actual output against expectations.

## Files

- **harness/** — test runner (run.sh), driver template (driver.c), python-re oracle (verify_rxt.py)
- **base/** — base-tier test corpus (.rxt files); every expectation cross-verified against python3 re (blocks marked `# pcre2-only` excepted — see docs/testing.md)
- **cli/** — CLI-surface and library-API tests (run_cli_tests.sh), part of `make test`
- **reject/** — the "unsupported constructs fail cleanly, never miscompile" mandate, asserted per construct (93 hand-written rejections + 66 reached by iterating `pcrec --list-syntax`, + 19 accept-controls; the two layers catch different things and neither replaces the other — see its CLAUDE.md). Cannot live in .rxt: a `perr` block requires the PYTHON oracle to fail too, and python compiles `\d`, `\b`, `(?i)` and most of the rest
- **registry/** — the SR-1 syntax construct table checked against the parser in both directions, including a 255-byte sweep of each of the four doorways that catches a construct added to parse.c with no registry row (D24), plus compliance_section.py, which holds docs/pcre2_compliance.md to the dump (SR-4)
- **bench/** — throughput + compile-time budget regression suite (`make bench`), guards R1 A-2/A-3
- **known_fail/** — regressions asserting CORRECT behavior for confirmed-but-deferred bugs (docs/known_issues.md); excluded from `make test` so the suite stays honest. Currently empty (all known bugs fixed at R2)
- **codegen/** — structural assertions that behavior-preserving optimizations are actually PRESENT in emitted code (R2-PR3: three could be disabled with zero test signal), plus a differential check that the M2.8 trie is output-preserving against a `-DPCREC_NO_TRIE` reference build (R3.3)
- **fuzz/** — PCRE2-oracle differential fuzzer (`make fuzz`), run manually and at checkpoints

## Conventions

.rxt format: comments (#), pattern blocks (pattern <regex>), and match/nomatch assertions (m/n with subject and expected span). See docs/testing.md for the full format spec. Run tests via `make test` or `bash tests/harness/run.sh [files...]`. Env vars: PCREC, CC, GENCFLAGS, KEEP=1 (preserve temp dir), VERBOSE=1 (per-test output).

Maintenance: update this file when subdirectories/test modules are added or removed.
