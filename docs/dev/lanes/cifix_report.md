# Lane cifix report — CI run 2 triage (35675372280, main 6a54b0ac)

Branch `lane/cifix`, 3 commits on top of main, all built and validated
in this worktree. `docs/dev/plan.md`/`dev_journal.md` intentionally NOT
touched (brief instruction).

## Triage verdicts

| # | class | verdict | fix |
|---|---|---|---|
| 1 | PC-3, 60 failures | CI-ENVIRONMENT | version floor + CI builds pinned 10.46 |
| 2 | CHECK 1R pin does not resolve | CI-ENVIRONMENT | `fetch-depth: 0` |
| 3 | DD-13b.W1.1 C3 population pins moved | CI-ENVIRONMENT | re-key RECORD exception on python version |
| 4 | "CHECK 4 ... checks failed: 1" | **not a separate defect** | same failure as #2 (see below) |
| 5 | RUN-STAMP printed `(dirty)` | CI-ENVIRONMENT (real bug, always fires) | compute dirty before the run |

### (1) PC-3 — 60 failures, log line 1935

CI's `libpcre2-dev` apt install resolved Ubuntu 22.04's package, 10.42 —
four minor releases behind the `(?a)`/`(?r)` group modifiers, the
CASELESS_RESTRICT/TURKISH_CASING/scs/scan_substring verbs, and the
149804/187872 probe-count pins `tests/registry/pcre2_check.c` is
written against (D98). Every failure is that gap restated once per row,
not a real divergence.

Fix, two parts:
- `tests/registry/pcre2_check.c` gains `PCREC_PCRE2_FLOOR_{MAJOR,MINOR}`
  (10.46) and a floor check in `main()`, right after the version parses:
  a resolved libpcre2 older than the floor prints the same `SKIP:`
  banner shape absence already uses (naming the floor and the resolved
  version) and returns 0 before any check runs — a stranger's older
  distro package gets a clean SKIP, matching run_registry_tests.sh's
  own `grep -q "^SKIP:"` coverage-guard gate, verified live (forced the
  floor above 10.48 in a scratch edit, confirmed the SKIP banner prints
  and the rest of `make test-registry` completes clean, reverted).
- `.github/workflows/ci.yml` no longer installs `libpcre2-dev`. It
  downloads and builds the pinned `pcre2-10.46.tar.bz2` release tarball
  from source (cached by version via `actions/cache@v4`), points
  `PKG_CONFIG_PATH`/`LD_LIBRARY_PATH` at it, and a dedicated step fails
  the job if the resolved version isn't exactly `10.46`.

Two build shapes were tried locally (darwin) before settling: a
`--disable-shared` (static-only) build broke `pool_from_library`'s
anti-circularity design — with no separate `.so`, `pcre2_abi_path()`
resolves to the pcre2_check TEST BINARY itself, so its ASCII-run scan
picks up pcrec's own strings too, moving the probe-count pin from
149804 to 234580 (measured). The default (shared+static) build resolves
the real separate object, matching the pin's own shape; needs
`LD_LIBRARY_PATH` alongside `PKG_CONFIG_PATH` for the dynamic loader.

**Residual, flagged rather than guessed at**: the 149804 pin was
measured on ubuntubudu's own gcc. A Linux/gcc build of the identical
10.46 source SHOULD reproduce it closely, but this could only be
confirmed on the real runner — my own attempt from darwin (Apple clang,
Mach-O) measured 155742, a different-enough binary format that the
mismatch says nothing about what CI will see. **If the next run's PC-3
count is not exactly 209 passing**, that's this residual firing, not a
new regression — the fix is a re-measurement/re-pin, not another
workflow change.

### (2) CHECK 1R / cb546b3a doesn't resolve, log line ~4172

Shallow clone (`actions/checkout@v4`'s default). Grepped every
`git archive`/`rev-parse --verify` pin under `tests/`: four more exist
(`run_lookaround_identity.sh` eacac76, `run_recursion_identity.sh`
ac4917d/a70982c9, `run_atomic_identity.sh` e2f81d5,
`run_backref_identity.sh` 5286265) but **none of them are in
`Makefile`'s `TEST_SECTIONS`** — each is its own opt-in
`make test-*-identity` target, so none ran in CI at all; nothing there
"passed by luck." `make mech`'s sabotage matrix `git archive`s HEAD
itself (no ancestor pin) and isn't part of `make test` either. Fix:
`fetch-depth: 0` on the checkout. Verified: `make test-cpset-structure`
reads 28/28 in this full-history worktree (27 + the now-resolving 1R
pin).

### (3) DD-13b.W1.1 C3 population pins moved, log line 3944

`PASS 13705` vs pinned `13721` (-16), `no-python-expression 1906` vs
`1890` (+16) — exactly the shape `run_rxtsource_tests.sh`'s own "BOX
SENSITIVITY" comment already documents: 16 corpus cells are
python-3.14-expressible (the reference box, ubuntubudu) and not
expressible on an older python. The RECORD-not-assert exception for
this was keyed on `uname -s = Darwin` — a proxy for "this box's python
isn't 3.14" that was never wrong until now: CI's ubuntu-latest is
`uname -s = Linux`, so it hit the ASSERT branch against pins that were
never its python's. Re-keyed on the actually-measured cause: resolved
`python3 -c 'sys.version_info'` major.minor compared to the pinned
reference (3.14), on any box. Verified locally (darwin, python 3.9):
still records identically to before (`RECORD: C3: population pins are
python 3.14's numbers; this python (3.9)'s deltas...`).
`tests/rxtsource/CLAUDE.md`'s `record()` paragraph updated to match.

### (4) "CHECK 4 ... checks failed: 1", log lines 4243/4247

**Not a separate defect.** `CHECK 4` (`cpset model check: PASS (400
trials...)`) itself PASSED — line 4243 is just the section header
printed a few lines before the run's final tally line, "checks failed:
1", which belongs to `run_cpset_structure.sh`'s overall summary and is
caused by CHECK 1R (issue #2), not CHECK 4. Confirmed by grepping every
`checks failed:` occurrence in the log and reading each one's own
section: this is the SAME failure as #2, counted once. Fixed by #2's
fix; verified together (28/28 above already reflects this).

### (5) RUN-STAMP printed `(dirty)`, always

Real bug, not a triage question: `test:`'s recipe read
`RUN_STAMP_DIRTY` via `git diff` AFTER `$(MAKE) -k $(TEST_SECTIONS)`
ran, and `test-corpus`'s own `run_size_log.sh` writes
`docs/dev/artifact_size_log.tsv` mid-run — so the tree the dirty check
saw was never the tree that was tested. Fixed: capture `stamp_sha`/
`stamp_dirty` into shell variables before the section run (same
recipe), pass those to the trailer call. `docs/testing.md`'s RUN-STAMP
paragraph updated.

## Files changed

- `tests/registry/pcre2_check.c` — version floor
- `.github/workflows/ci.yml` — full-history checkout, build+cache
  pinned pcre2 10.46, PKG_CONFIG_PATH/LD_LIBRARY_PATH, a version
  verification step
- `tests/rxtsource/run_rxtsource_tests.sh` + `CLAUDE.md` — C3 RECORD
  re-keyed on python version
- `Makefile` — RUN-STAMP dirty-before-run
- `docs/spec/registry.md`, `docs/testing.md` — spec/process hunks for
  the caller-observable changes (D80)

## Validation done here (darwin, this worktree)

- `make -j4 CC=gcc-16` — clean
- `make strict CC=gcc-16` — clean (`whole tree compiles clean with
  -Werror -Wshadow`)
- `make test-registry CC=gcc-16` — 209/0 (PC-3), 225/0, 108/0, 24/0,
  54/0 across the section's sub-checks; forced-SKIP path verified
  separately (floor bumped above resolved 10.48, SKIP banner printed,
  reverted)
- `make test-cpset-structure CC=gcc-16` — 28/28
- `make test-rxtsource CC=gcc-16` — 212 passed / 1 recorded / 0 failed
- End-to-end pcre2-10.46-from-source rehearsal in the scratchpad
  (download, `./configure`/`make install`, `resolve_pcre2.sh` resolves
  10.46 via pkg-config, `make test-registry` links and runs against it)
- YAML validated (`ruby -ryaml`, no PyYAML on this box)

## Expected next CI run

- Checkout: full history (no timing claim beyond "small repo, cheap").
- New steps: pkg-config install, pcre2-10.46 cache miss on the FIRST
  run after this merges (a full build, a few minutes), cache hit on
  every run after; a version-verification step that fails loudly if
  anything resolves to other than `10.46`.
- `make test`: all 41 sections green, assuming the residual above
  doesn't fire. Specifically expect to SEE:
  - PC-3 (`registry vs libpcre2`) reading exactly `209` passing, `0`
    failing, `libpcre2 version: 10.46 ...` — **not** a SKIP banner
    (SKIP would mean the pinned build wasn't actually resolved —
    investigate PKG_CONFIG_PATH ordering if so).
  - `CHECK 1R` in `run_cpset_structure.sh` passing (pin `cb546b3a`
    resolves); `test-cpset-structure` at 28/28.
  - `rxtsource`'s C3 line reading "all eleven population pins hold" —
    **not** a RECORD line — if and only if CI's `python3` resolves to
    3.14; if it resolves to something else, expect a RECORD line
    (still a PASS section) naming that version instead of "Darwin".
  - RUN-STAMP printing `(clean)` (a fresh checkout, no prior artifact
    writes) rather than `(dirty)`.
  - No SKIP banners for absence anywhere PC-3/PC-4/definitions-oracle/
    uprops run — the CI-built 10.46 satisfies all of them.
- If PC-3's own passing count differs from 209 (see residual above):
  that's the toolchain-sensitivity risk flagged in docs/testing.md, not
  this lane's fix failing — re-measure and re-pin rather than re-open
  this report.
