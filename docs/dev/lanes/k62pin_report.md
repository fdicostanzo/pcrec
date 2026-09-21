# k62pin — re-pin tests/rxtsource census after K62 corpus addition

Lane `k62pin` (sonnet), RE-PIN lane. Worktree `worktrees/k62pin`, branch
`lane/k62pin`, from local main `dbc4865a`.

## Situation

lane `adm0921` added ONE new corpus file, `tests/quoting/k62_class_range_e.rxt`
(5 blocks, 16 cells — a K62 regression pin, oracle-verified against this
box's local libpcre2 10.48-Homebrew), without re-pinning
`tests/rxtsource/run_rxtsource_tests.sh`'s census. The darwin `make test`
gate at `4c2b06d2` was RED on every census-derived assertion in that one
script: the census pin itself, the file-list pin, C1 legs A/B/C's
block-row counts, the case-row derivation, C3's file-count and
reconciliation, and the W23-S7 corpus control. The other red in that log
(`nm could not read arm_a.o`) is the standing darwin probe, not this
lane's.

## Grep sweep — every reader found, with disposition

```
grep -rn "28955\|3939\b\|\b212\b" tests/ scripts/ docs/spec docs/testing.md tests/*/CLAUDE.md
```

| hit | disposition |
|---|---|
| `tests/rxtsource/run_rxtsource_tests.sh:222-224` (`CENSUS_FILES=212` / `CENSUS_BLOCKS=3939` / `CENSUS_LINES=28955`) | **the pin — re-pinned** |
| `tests/bench/compare/floors.tsv:109`, `results-ubuntubudu-*.md` (`...389.212`, `...1344.212`, `...25189.212`) | unrelated — decimal fractions ending in `.212`, not the file/block count |
| `tests/utf8/CLAUDE.md:138` (`317 real / 212 perr`) | unrelated — a different, independently-derived count (utf8 `perr` blocks at a stage-5 milestone), not this census |

A second, broader sweep for the two more distinctive numbers
(`\b28955\b\|\b3939\b`, all file types, whole tree minus `worktrees/`/`build/`)
found only two more hits, both historical:

| hit | disposition |
|---|---|
| `docs/dev/lanes/w5r_report.md:83`, `docs/dev/lanes/tour4_report.md:186-188` (`3939` reach counts) | unrelated — a `scripts/emit_sweep.py`-family REACH figure from an earlier lane's own corpus-argv sweep, not the rxtsource census. Both files are historical, per `docs/dev/lanes/CLAUDE.md`'s own rule ("historical once merged; never edited afterwards") — out of scope even if they had matched |

`tests/rxtsource/CLAUDE.md`, `tests/quoting/CLAUDE.md`, `docs/spec/rxt_format.md`
and `docs/testing.md` carry no numeric census citation to move.
`tests/quoting/CLAUDE.md` already documents the new file (adm0921's own
commit); no update owed there.

**Conclusion: `tests/rxtsource/run_rxtsource_tests.sh` is the ONLY live
manifest for these numbers.**

## Re-pinned values

```
CENSUS_FILES  212 -> 213
CENSUS_BLOCKS 3939 -> 3944
CENSUS_LINES  28955 -> 28971

RUNSH_FILES   211 -> 212
RUNSH_BLOCKS  3936 -> 3941
RUNSH_LINES   28944 -> 28960
```

`tests/quoting/k62_class_range_e.rxt` is not under `tests/known_fail/`,
so `RUNSH_*` moves by the identical `+1/+5/+16` delta — same shape as
every prior non-known_fail corpus addition this file's own history
records (cmtfix, adm71, etc).

### The two derivations — components, not totals

**Case-row derivation** (`kind_cases`/`kind_perr`/`kind_group` at
`run_rxtsource_tests.sh:750-756`): these are **not** manifest constants.
They are computed LIVE, every run, by an `awk` scan of the real corpus
against three line-kind patterns, then compared against `CENSUS_LINES`.
There is nothing to re-pin here beyond `CENSUS_LINES` itself — the log's
own FAIL line (`24288 + 456 + 4227 = 28971, but census is 28955`) already
shows the live-computed values agreeing with the new total; only the
manifest constant they were compared against was stale.

Attribution, confirmed by isolating the new file's contribution
(`(24288-15) + (456-1) + (4227-0) = 28955`, the pre-addition value): the
file's 15 `m`/`n` case lines land in `kind_cases` (24273 -> 24288), its 1
`perr` line lands in `kind_perr` (455 -> 456), and `kind_group` is
untouched (4227 -> 4227, consistent — the file declares no `g`/`gp`
capture-slot lines).

**C3 derivation** (`c3_pass + c3_info + c3_skip + C3_TIMEOUT_FILE_LINES`
at `:1221`): same shape — `c3_pass`/`c3_info`/`c3_skip` are live
`verify_rxt.py` output, not manifest constants, compared against
`CENSUS_LINES`. What IS a manifest constant here is the separate
**Linux-reference breakdown** (`C3_PASS`/`C3_SKIP`/`C3_SKIP_*`/etc,
`:1136-1147`), asserted as a hard `fail` on non-Darwin and only
`record`ed as a box-sensitivity delta on Darwin. Re-pinned by isolating
the new file:

```
$ python3 tests/harness/verify_rxt.py --file-timeout 10 \
    tests/quoting/k62_class_range_e.rxt
  k62_class_range_e.rxt: 15 case(s) skipped, not python-verifiable
    (pcre2-only 0, give-up 0, composed 0, no-python-expression 15,
     perr-python-accepts 0, own-oracle 0, under-convention 0)
  ...
  TOTAL: m=9 n=6 ms=0 ns=0 perr=1 g=0 gp=0 cases=16
  PASS=1 FAIL=0
  SKIP=15 (... no-python-expression=15 ...)
```

The file's one `perr` block is the `+1 PASS` (a `perr` is verified the
same way any `perr` is — D26 provenance-only, not a python-`re` question),
and every one of its four accepting blocks' 15 `m`/`n` lines classifies as
`no-python-expression`: python's `re` has no translation for the
class-range `\E`/`\Q\E` dissolution these blocks pin (this is a
structural "no python spelling exists" classification the tool makes per
pattern shape, not a python-version-sensitive divergence — the same
reasoning the file's own prior re-pins use for `pcre2-only`, so it
transfers across boxes the same way).

```
C3_PASS          13720 -> 13721   (+1)
C3_SKIP          15146 -> 15161   (+15)
C3_SKIP_NOPYTHON  1875 -> 1890    (+15)
```

All other `C3_SKIP_*` reasons, `C3_INFO`, `C3_STOREUNCOVERED`, `C3_TIMEOUT`
and `C3_TIMEOUT_FILE_LINES` untouched — the file is not composed, not
pcre2-only, not a giveup, not a perr-python-accept, not own-oracle, not
under-convention, and times out nothing.

Reconciliation: `13721 + 15161 + 89 = 28971 = CENSUS_LINES` (matches).

## Solo-run validation

### `tests/rxtsource` section

```
$ make CC=gcc-16 test-rxtsource
```

Full green: `checks passed: 212`, `checks recorded: 1` (the expected
darwin box-sensitivity `RECORD:` line — pins are Linux-reference numbers,
this box diverges on `PASS`/`SKIP`/`no-python-expression`/
`perr-python-accepts` counts as documented, the reconciliation check
stays hard and passes), `checks failed: 0`. Every previously-red line now
reads PASS, including the W23-S7 corpus control:

```
PASS: census: 213 files / 3944 blocks / 28971 expectation lines (matches the pin)
PASS: file list: 213 files (the population every leg below reads)
PASS: denominators reconcile: census 213/3944/28971 minus known_fail's 1/3/11 = run.sh's 212/3941/28960
PASS: C1: leg A emitted 3944 block rows (matches the census)
PASS: C1 leg A == leg B: pcrec --list-source and run.sh --dump agree byte for byte on 3944 blocks
PASS: case-row derivation reconciles: 24288 subject-bearing + 456 perr + 4227 g/gp = 28971 expectation lines
PASS: C1: leg B emitted 24288 case rows ...
PASS: C1: leg C emitted 24288 case rows ...
PASS: C3: verify_rxt.py discovered 213 files (its own discovery, floored at the census)
PASS: C3: verify_rxt.py verified 12742 expectation(s) with 16133 skip(s) and 7 info ..., 0 failures
RECORD: C3: population pins are Linux-reference numbers; this box's deltas ...:
    PASS: got 12742, pinned 13721
    SKIP: got 16133, pinned 15161
    INFO: got 7, pinned 0
    no-python-expression: got 2866, pinned 1890
    perr-python-accepts: got 10, pinned 14
PASS: C3 reconciles: 12742 verified + 7 info + 16133 skipped + 89 in the timed-out file = 28971
PASS: W23-S7 corpus control: entry files: 213 (== CENSUS_FILES), fragments spliced: 0 — the shipped corpus has no include lines

== Summary ==
checks passed: 212
checks recorded: 1
checks failed: 0
PASS: rxtsource: INV-COMPAT holds over 213 files / 3944 blocks / 28971 expectation lines
```

Full log: `/tmp/k62pin_rxtsource.log` (session scratch, not committed).

### `make test-codegen` and the rxtsource section's home under it

`make test-codegen` was launched (`/tmp/k62pin_codegen.log`) — result and
completion line appended below once it finished (see "Validation numbers"
below; this section is the RXTSOURCE-specific run, which is the direct
hit for this lane's change and is what the census pins above are verified
against).

### `scripts/m6read_check_sab_anchors.py` sanity check

```
$ python3 scripts/m6read_check_sab_anchors.py
sabotages checked: 270 (286 anchor sites)
all anchors resolve
```

All 286 anchor sites resolve — the re-pin touched no sabotage anchor
(all edits are pure numeric-constant/comment changes inside the
CENSUS_*/RUNSH_*/C3_* blocks, none of them an anchor target).

## Validation numbers — status

- `bash tests/rxtsource/run_rxtsource_tests.sh` (solo): **COMPLETE**,
  212/0/1-recorded, see above.
- `scripts/m6read_check_sab_anchors.py`: **COMPLETE**, 286/286 anchor
  sites resolve.
- `make test-codegen`: **[fill at hand-off — see log path above]**

## Plan note

Appended to `[ADMIN-0921]`'s plan row: "re-pin landed by k62pin: census
212/3939/28955 -> 213/3944/28971 (RUNSH_* +1/+5/+16 matching), C3
Linux-reference PASS +1/SKIP +15 (all no-python-expression); rxtsource
solo 212/0/1-recorded, sab-anchors 286/286."

## Branch

`lane/k62pin`, tip `e7fddbad` (commit `[k62pin] re-pin tests/rxtsource
census after K62 corpus addition`) + this report's own commit. Not
merged.
