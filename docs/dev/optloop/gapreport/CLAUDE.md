# docs/dev/optloop/gapreport/ — [OPT-GAPREPORT]'s instruments and data

These are the reproduction pieces behind `../gapreport_2026-10-03.md`, the
first instance of D144 addendum 2's repeatable gap report. The pipeline has
four steps:

1. `extract.py` reads the bench's published report `.tsv` (the `rank`
   section only) into `cells.json`.
2. `stamps.py` compiles every bench pattern into `stamps_<label>.json`.
3. `gap.py` builds the per-cell gap table, `gap_rows.json`.
4. `rank.py` combines that with `causes.tsv` into the per-group
   `rank.json`.

`nmatch.py` supplies the ns/B and ns/match denominators.

The pipeline writes nothing in pcrec-bench and reads no clock. It reads
only:

- the report `.tsv` files, fetched from the Linux box (ssh + tar);
- each bench set's `manifest_throughput.tsv`, `expectations.tsv` and
  `patterns/*.rx`, from the read-only `/Users/fdicostanzo/pcrec-bench`
  checkout.

To re-run it for the next instance, point the inputs at the new pin's
report group. Then re-judge `causes.tsv` before you trust `rank.json`,
because the cause assignment is the human layer.

## Usage: one command

    docs/dev/optloop/gapreport/gapreport.sh --group b120b121-fc719ca4 \
        --out docs/dev/optloop/gapreport_2026-10-04.md
    docs/dev/optloop/gapreport/gapreport.sh --group latest --out ...
    docs/dev/optloop/gapreport/gapreport.sh --check

What `--group NAME|latest` does, in order:

1. Fetches that report group's `.tsv` files (the group is the name after
   `budu-<machine>-` in the bench's report filenames; `latest` is the group
   with the newest date) and the seven bench sets' `manifest_throughput.tsv`,
   `expectations.tsv` and `patterns/` read-only from the Linux box, by
   `ssh -o BatchMode=yes` + `tar` (`gapconfig.REMOTE`; tailnet address) into
   a scratch dir (`--scratch`, default a fresh `mkdtemp`; `--no-fetch` reuses
   one).
2. Runs extract, stamps, nmatch, gap and rank with `build/pcrec` (`--pcrec`).
   Stamps compiles every bench pattern SERIALLY (`STAMPS_JOBS`, default 1),
   bounded by `--stamps-timeout` (3600 s). It is the slow step: run it on a
   quiet box.
3. Renders the report: summary, ranked cause groups with their cells, where
   pcrec leads, what could not be judged, stamp moves since the baseline
   census (`--baseline`, default `stamps_main.json`; `--save-stamps FILE` keeps
   the fresh census as the next baseline), and unassigned cells.
4. Copies `judgement_<stem>.md` (`--judgement`; `<stem>` is the `--out` name
   minus `gapreport_`) verbatim into a marked MANAGER JUDGEMENT section. That
   file is hand-kept, so a re-run never overwrites judgement; if it is
   missing the report says so and the script prints its expected path.

A losing cell with no `causes.tsv` row is UNASSIGNED: the script prints a
loud stderr banner naming each one, the report lists them in section 6 and
the summary, and `--fail-unassigned` makes it exit 3. Add `set<TAB>pattern<TAB>group`
rows (and a `#group<TAB>ID<TAB>text` line for a new group id) and re-run;
the judgement of a NEW group's cause is still the manager's.

The criteria are one set of first-match tables in `gapconfig.py` (scale tiers
and null bands, comparator roles, realism weights, group merges, the ranking
key). `gap.py`, `rank.py`, `stamps.py` and `gapreport.py` carry no literal
criterion of their own.

The mechanical ranking is: algorithmic evidence first (a scalar engine also
beats auto), then combined realism-weighted score, then breadth. It differs
from a hand-ordered slate (the first instance ranked CI below U8-PICK because
round 1 owns CI); put reordering reasoning in the judgement file.

`--check` runs the whole pipeline on `fixture/` (two sets, 15 cells, a fake
compiler, a baseline census with one moved stamp, one unassigned cell, one
tier-C cell, one refusal) and diffs the rendered report against
`fixture/expected.md`, exit 1 with the diff on any mismatch. After an
intended change to the renderer or the criteria, `--check --bless` rewrites
`expected.md`; read the diff in git before committing it.

## Files

- `extract.py` — reads the report `.tsv` (the `rank` section) into
  `cells.json`: per (set, pattern, regime, form, fact), each testee's
  median/min/max and status. `cells.json` is not committed; it regenerates
  from the bench's committed reports.
- `stamps.py` — compiles each `bench/<set>/patterns/*.rx` with the bench's
  `pcrec-auto` flags (`--features all`, plus `-e utf8` on utf8) and reads
  every scalar `RX_*` stamp. It takes `PCREC`, `BENCH` and `OUT` from the
  environment. Its `code_sha` is a text hash. Between `fc719ca4` and main it
  moved on almost every artifact (CLS-TREE S2's spelling changes and K78-K80
  scaffolding), so it is **not** an identity measure. Machine-code identity
  is the bench's `tools/program_identity.py`.
- `stamps_main.json` — that census at main `d986874b` (abi 55), all 331 bench
  patterns, including the 24 refusals with their first diagnostic line.
- `stamp_diff.txt` — the selection-stamp diff between the bench pin
  `fc719ca4` (abi 50) and main. One pattern differs, and only in a refusal's
  byte count.
- `gap.py` — D144 addendum 2's metric, cell by cell:
  - the pcrec side, `auto` and class-matched;
  - MEASURED-only sides;
  - the scale tiers A/B/C with the cross-window null bands from
    `cycle2_batch2_reading.md` §1;
  - the semantic flag for each comparator.

  Its output, `gap_rows.json`, is not committed.
- `nmatch.py` → `nmatch.json` — the throughput regime's total subject bytes
  and oracle match count per (set, pattern), from the bench's own manifests
  and expectations.
- `causes.tsv` — **the judgement layer**: each losing (set, pattern) gets
  one cause group. The groups are defined in `../gapreport_2026-10-03.md`
  §2. `rank.py` reports any losing cell without a group as `unassigned`,
  and this instance has 0.
- `rank.py` → `rank.json` — per group:
  - the peer cells and the ceiling cells;
  - the realism-weighted log2 scores (tier A/B only);
  - breadth;
  - the D119 algorithmic-evidence column (`scalar_wins`, `rust_only`).

  It also carries the per-set lead/null/behind census.
- `u8pick_probe.txt` — the compile-side probe behind the U8-PICK finding.
  Seven literals, each in byte mode and under `-e utf8`, with their
  `RX_DFA_PREFILTER*` and `RX_REQ_*` stamps.
- `gapreport.sh` / `gapreport.py` — the one-command driver (see Usage):
  fetch, the four steps, render, `--check`. Stdlib only.
- `gapconfig.py` — the declared first-match criteria tables.
- `fixture/` — `--check`'s committed inputs: `reports/` (two report `.tsv`),
  `inputs/` (bench-set manifests, expectations and patterns whose text is the
  fake compiler's stamp source), `fakepcrec.py`, `causes.tsv`,
  `baseline_stamps.json`, `judgement.md`, and `expected.md` (the rendered
  report the check diffs against).
