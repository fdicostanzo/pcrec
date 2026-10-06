# studies/artrev/ -- the [ARTREV] harness (S0)

Lane `artharness` (2026-10-05, sonnet). Backs `docs/dev/optloop/artrev/charter.md`
(S0, §3.1) and D150. Never built or run by pcrec's make; reads a GIVEN `pcrec`
binary and writes only `build-artrev/` (gitignored). Nothing under `src/`,
`cli/`, `lib/`, `tests/` is touched (tests/ is only READ, for the corpus cases).
Python 3.9-clean. See README.md for the recipe and the bound/lock table.

## Files
- `artrev.py`    the CLI: `gen` (artifact + `-S` asm + the generation/compile
                 lines, pin/abi/gcc recorded), `twin` (apply/seal a patch;
                 REJECTS SIMD/target flags and any `artifact.h` change),
                 `identity`, `time`, `ledger`, internal `_rawtime`.
- `common.py`    paths, meta, THE fixed compile line (`BASE_FLAGS`), the
                 rejection regex table, the `iterations.tsv` ledger and its
                 bounds (6 leads / 4 revisions / 3 timing runs), the gates.
- `identity.py`  answer identity: every exported call shape (the `_in` ones
                 too: the compile line now carries -DARTREV_HAVE_IN=1) on supplied
                 subjects + corpus `.rxt` cases + a generated battery (a regex
                 SAMPLER seeds real matches), libpcre2 sample, `--san`, PLUS by
                 default (charter S1-S3, 2026-10-06): the SHRUNKEN-RESOURCE phase
                 (0/1 frames x 0/1 trail, shrunk step/work budgets, THE GIVE-UP
                 RULE with its libpcre2 oracle), the WINDOW-START differential
                 (artifacts with an internal `rx_prefilter`), and the livelock
                 bound on the twin's driver run.  `--strict-giveup`,
                 `--skip-shrunk`/`--skip-window` (the latter log PASS-PARTIAL,
                 which `time` refuses).
- `timing.py`    interleaved rounds, load gate, locks, watchdog, verdict rule,
                 the `--remote ubuntubudu` wrapper (day-only, dry-run), the LAYOUT
                 control (`--pads`/`--pad-arms`: arms rebuilt at code-offset pads,
                 verdict folds in the spread across pads), `--cell` (the CELL row).
- `variants.py` `driver_spans.c`  `artrev.py variants`: a DENSE and a SPARSE variant
                 of a cell subject, built from the original's own match spans.
- `driver_pf.c`  the window-start driver (internal prefilter, orig vs twin).
- `reverify.sh`  re-run the hardened identity over a directory of sealed patches in a
                 scratch root and print a verdict table (used by lane artcollect).
- `fixtures/`    pinned A09 artifact for the self-test's real-twin checks (its CLAUDE.md).
- `shim.c` `artrev_abi.h` `driver_id.c` `bench_t.c` `pcre2_ref.c`  the C side:
                 one shim TU per arm (the bench's shim shape), the identity
                 transcript driver, the timed find-all unit, the libpcre2 oracle.
- `gen_selection.py`  generate selection.tsv rows at one pin.
- `selftest.sh` `selftest_twins.py` `selftest.log`  the self-test INCLUDING the
                 failing direction, and its committed transcript.

## Rules this directory lives by
- The ledger is the bound: never edit `iterations.tsv` by hand; `time` refuses
  a twin whose `artifact.c` is not its last logged revision.
- `--gate-override` / `--hour-override` / `ARTREV_SUITE_LOCK_PATH` work only
  under `ARTREV_SELFTEST=1` (set by selftest.sh alone) and are logged loudly.
- A new check here must ship its failing-direction control in selftest.sh.

- `confirm_collect.py` — S4 helper (lane artconf): joins a pass-1 and pass-2 `summary.txt` plus the identity logs into the per-artifact `confirmed.tsv`. Reads files only.
