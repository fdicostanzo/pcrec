# et1twin — [ENG-TACTICS] stage 1's D77 trigger: K12 recount under G2 + reverse-inner hand twins

**Lane `et1twin`, 2026-10-10, opus. MEASUREMENT ONLY: nothing under `src/` changes.**
Pin: main `c87d20af` (abi 74), Linux dev box (Ryzen 7700X, gcc 15.2, libpcre2-8 10.46).
pcrec-bench at `f68448a6`, read only (subjects regenerated in a `git archive` copy,
throughput hashes checked against its manifests). Instruments and raw outputs:
`docs/dev/optloop/et1twin/` (own `CLAUDE.md`). **Every number is SCRATCH TIER.**

Charter: D151 addendum 4 — stage 1 = rev-inner's DFA hat, triggered by a hand twin on
the top K12 cells, counted after G2.

## 0. Answers first

@@ANSWERS@@

## 1. Step A — the recount

### 1.1 Method

- **Population.** `studies/walk_survey/k12_census.py` re-run at the pin over every
  bench pattern export: still **24 patterns** flagged K12. Two moved off the list's
  substance since the survey: `capability/tail-ext-lower-txt` and
  `tail-dotstar-txt` now compile `RX_DFA_SCAN "rev-end"` ([OPT-REVEND] 7388f1c0);
  the survey already excluded their cells as K1-owned, so the total does not move.
  `syntax/rec-define`, `loglines/uuid` and `wild-validator-uuid-grok` read
  `RX_DFA_START "end-minus-width"`.
- **Measure.** walk_survey's own instrument (`wsdrv5.c`, `m_gap` = forward-machine bytes
  stepped before each call's match start) re-run over the K12 patterns' bench cells at
  the pin (`run_pop.py`, config `default`), then `analyze.py` with the survey's own
  weights (`bench_times.tsv`): `est = bench median × m_gap / T`, K1-owned cells excluded.
  **Every surviving cell's `m_gap` is byte-identical to the survey's**: neither
  [OPT-REVEND] nor [START-LANDING] (b8337c33) touched a K12 cell's forward walk — the
  K12 cells still read `reverse-pass` (or `attempt-start`/`end-minus-width`) and the
  total re-measures at 15.786 ms (survey: 15.8).
- **The gates.** No `inner_split` fact exists yet, so G1/G2 are read by hand off each
  pattern's text, one row per pattern in `recount.py`'s table (the table IS the reading;
  it names the `P · L` split each verdict was read on). G2 is applied as
  `where_to_start.md` §2.4 states it: `fixed_width(P) ∨ ¬(bytes(L) ⊆ alphabet(P))`.
  A second column applies the FACTOR-FREE refinement this lane found necessary to
  read altwide (§1.3); it is reported, not counted as G2.

### 1.2 The recount table (`docs/dev/optloop/et1twin/recount.txt`)

@@RECOUNT@@

### 1.3 Reading

- **Under G2 as stated, the stage-1 population is 5.84 ms of the 15.8 ms (37%)**, and
  it is essentially ONE pattern: `loglines/ipv6` carries 5.83 ms of it (throughput
  5.69 + search_short 0.14). The other survivors are crumbs: `kv-quoted` 8.5 µs (it
  already has the K82 handoff at `c − 32`), the uuid pair ~1 µs (start already exact,
  `end-minus-width`), `csv5` 7 ns.
- **altwide/sfx-\* (5.82 ms) FAIL G2's formula** — the stems span all 26 letters, so
  `{i,n,g} ⊆ alphabet(P)`, and their widths are 3-9, not fixed — **but the split is
  NOT ambiguous.** G2's literal arm is rust's sufficient condition for "no occurrence of
  `L` lies inside a string `P` matches"; the exact condition (§2.2 step 2's own
  argument) is that no string of `P` CONTAINS `L` as a factor (the `j + |L| ≤ j'`
  case), plus no crossing occurrence (`j < j' < j + |L|`, which needs `L` to have a
  border; `ing` has none). No stem of sfx-64/256/512 contains `ing` (checked over all
  64/256/512). This FACTOR-FREE arm is decidable on `P`'s DFA (a product with the
  `L`-occurrence automaton) and strictly weaker than the alphabet arm. It is NOT
  rust's third (disjoint-separator) arm, which D151 item 3 ruled NO on; it is a new
  question (§5 Q1).
- **`\S+@\S+` and email/\* fail every arm.** `'@'` is a factor of `\S+`; the quoted local
  part of the email patterns admits `'@'` (`\x23-\x5b`), a genuinely ambiguous split.
  (`\S+@\S+` happens to be monotone for a different reason — `P` is one class-plus that
  contains `L` — but no arm on file or proposed here admits it, and its 1.41 ms is
  K7-shaped: the presence `memchr('@')` then the DFA re-steps the gap.)
- **Off the stage-1 route:** the two VM hybrids (syslogbase: lookahead in `P`; winpath-
  grok: an atomic group in `P` — G1 fails on both) and eight `^`-anchored patterns (one
  attempt; the tactic declines, `where_to_start.md` §2.5).
- **Recounted estimate: 5.84 ms under G2 as written; 11.66 ms if the factor-free arm is
  admitted.** Both are walk_survey's upper-estimate weights (old-pin bench medians on the
  Ryzen 1600, uniform per-byte cost), so the TWINS (§2) are the price, not these.

## 2. Step B — the hand twins

### 2.1 Cells chosen

The formal-G2 survivors ranked by estimate are ipv6 (5.83 ms), kv-quoted (8.5 µs), then
crumbs; D151 add. 4 names ipv6 and altwide/sfx-64. Twinned: **`loglines/ipv6`** (the
population), **`altwide/sfx-64`** (named by the ruling; admitted only under the
factor-free arm), and **`loglines/kv-quoted`** (the second formal survivor, and the
one cell where today's artifact already scans the landmark: it isolates what EXACT
buys over the K82 handoff's `c − K` WINDOW).

### 2.2 The twin (`twin.c`)

One generic file around each cell's UNMODIFIED artifacts, so no emitted line is
hand-edited:

- `rx.c` — today's artifact for `R`: supplies the landmark scan where it already emits
  one (`rx_reqrun`: kv-quoted's `="`, sfx-64's `ing`) and the ANCHORED forward finish
  `rx_match_caps` (the anchored DFA, `start_table.md` §4.1's DFA hat).
- `rxpl.c` — pcrec's own artifact for `(?:P·L)\z`, which [OPT-REVEND] compiles to a
  pure reverse walk from the subject end (`build.sh` asserts `RXPL_DFA_SCAN
  "rev-end"`). Called with length `j + |L|` it is exactly the reverse DFA over `P·L`
  seeded at the landmark occurrence `j`, floored at `search_from`, recording the
  smallest accepting start `s*(j)` — the walk `where_to_start.md` §2.1 defines, and
  the PREFIX reverse machine `start_table.md` §4.1 says the build needs, here borrowed
  from REVEND's emitter (`locate_finish.md` §7.2's "rev-end as rev-inner with
  landmark = end", read the other way round).
- `tw_search`: for each occurrence `j ≥ pos` of `L` in order — `s*(j)` by the reverse
  walk; if non-empty, `rx_match_caps` anchored at `s*(j)`; a match is the answer, else
  `pos = j + 1`. ipv6's landmark is a plain `memchr(':')` (its artifact emits only a
  presence pre-check).
- Donors: ipv6 `[0-9a-f]{1,4}:\z` (P = the alternation's common head, `L = ':'`);
  kv-quoted `\b[a-z_][a-z0-9_]{0,31}="\z`; sfx-64 the pattern itself `+ \z` (`S` empty).

### 2.3 Answer identity (`ident.txt`)

@@IDENT@@

### 2.4 Timing (`times.tsv`, `times_summary.txt`)

@@TIMING@@

## 3. TRIGGER VERDICT

@@VERDICT@@

## 4. What stage 1's build is if it fires

@@BUILD@@

## 5. Questions (with recommendations) and bench-only questions for relay

@@QUESTIONS@@

## 6. Reproduction

```
make -j16
B=/home/pcrec/projects/pcrec-bench; W=build/et1; mkdir -p $W/bc
git -C $B archive HEAD bench pcrecbench | tar -x -C $W/bc
(cd $W/bc/bench/<set> && python3 -I gen_subjects.py && python3 -I gen_throughput_subjects.py)   # altwide loglines (+ the K12 sets for Step A)
# Step A: studies/walk_survey/{pop_bench.py,run_pop.py (WSDRV=wsdrv5.c CONFIGS=default),analyze.py,k12_census.py}
python3 docs/dev/optloop/et1twin/recount.py docs/dev/optloop/et1twin/k12_cells_now.tsv
# Step B
PCREC=$PWD/build/pcrec BENCH=$B OUT=$PWD/build/et1twin docs/dev/optloop/et1twin/build.sh
OUT=$PWD/build/et1twin BENCHCOPY=$PWD/$W/bc BENCH=$B docs/dev/optloop/et1twin/ident.sh
OUT=$PWD/build/et1twin BENCHCOPY=$PWD/$W/bc docs/dev/optloop/et1twin/time.sh > times.tsv
python3 docs/dev/optloop/et1twin/summarize.py times.tsv
```
