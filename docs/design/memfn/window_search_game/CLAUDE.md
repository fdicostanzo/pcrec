# docs/design/memfn/window_search_game/ — lane wingame's and wingame2's instruments

The evidence behind `../window_search_game.md` (D161's "search for the window",
gamed out before any request). This is design-study tooling. It is never built
or run by `make` and is read by no check. COUNTS ONLY: nothing here reads a clock.

## Files

- `spans.py` — D161's SPAN LIST for one pattern, derived independently of
  pcrec. It applies a PCRE-to-Python spelling pass, walks `re._parser`'s tree in
  byte mode with ASCII classes, and flattens it to positions and gaps; a span is a
  maximal run of positions with `move_back = omax` and `overshoot = omax - omin`.
  Every information loss is a `notes` token (`alt-dropped`, `rep-right`,
  `lookaround`, `backref`, `recursion`, `kreset`, `gstart`, `verb`, ...). Run it
  as `python3 spans.py PATTERN...` to print the list.
- `game.py` — the kit POLICIES (P1 rare-pos, P2 rare-span, P3 pair,
  P4 selfprice, P5 window(consumer)) and the COUNTING simulator (`simulate`:
  stops, survivors, window bytes, window union, possible starts, by numpy over
  the subject). The constants that are not D161 inputs are named and labelled
  UNMEASURED: `CONSUMERS`, `scan_price`, `VERIFY_PER_STOP`, `SELF_DECLINE`.
  Hand witness for `simulate` (checked when it was written):
  `[a-z]{1,8}@example\.com`'s inner span over
  `zzbob@example.com and x@example.com @examplX` gives 2 stops, 2 survivors,
  37 window bytes, a 35-byte union and 16 starts.
- `gen_subjects.py BENCHCOPY OUTDIR` — regenerates capability `t-256k`, syntax
  `t-256k` and loglines `t-256k-fail`/`-hit` from a `git archive` COPY of
  pcrec-bench (`bench` + `pcrecbench`). Each subject's sha256 is held against the
  bench's `manifest_throughput.tsv`; all four matched at `d359564f`.
- `run_game.py PCREC BENCHCOPY SUBJDIR PRIOR CORPUSROOT OUTDIR [N]` — the
  population run. It compiles each pattern once with `--emit-facts` (raw bytes on
  argv, `--features all`). It writes `spans.tsv` (spans, notes, the k-set control
  `kset_agree`, the shipped stamps), `spaninfo.tsv` (every span with its rates),
  `choices.tsv` (each policy's form and SHIPPED's), `sim.tsv` (counts per policy
  and subject, plus a python `re` match count as a sanity column) and
  `spanforms.tsv` (each bounded span's best single and pair form, simulated: the
  span-vs-span data). `WINGAME_LIMIT=k` thins the population for smoke runs.
  SHIPPED is today's choice mapped onto the same form where it has one: start-set
  rows, `offset-set`/`run-pinned` offsets (kset classes), `handoff` (req run or
  req byte, K back), the VM's first-class scan, and the hybrid's inlined DFA
  prefilter. A route with no window search counts as "the consumer meets every byte".
- `[wingame2]` additions. `spans.py` keeps each span's first item index (`item0`) and
  has `rel_from_items` (a direct walk between two spans: the control for the derived
  relative distance). `game.py` has P6 `refine` (`region_of`, `Plan`, `plans_of`,
  `pol_refine`, `refine_pair`), `simulate_plan` (counts: B stops, B survivors, local
  positions, distinct A windows, plus a merged hand-over), and `simulate_gate`
  (a presence gate on the rare span, continuous or tail form). `run_game.py` adds the
  eleven `WIT2` two-span witnesses as set `wit2` (summarize.py's A-D tables ignore
  that set), `refine.tsv` (per pattern x subject x consumer: nosearch, P5, P6, local,
  local-merge, local-loose, fwd, fwd-gate, fwd-tail, nosearch-gate, nosearch-tail) and
  `relcontrol.tsv`. `WINGAME_ONLY=set` restricts the run to one set. `chain.sh` takes
  `PCREC=/path/to/pcrec` to reuse a build. `summarize.py` section E reads them.
- `summarize.py OUTDIR` — the markdown tables `window_search_game.md` §4.2 cites.
- `chain.sh WORKTREE` — the post-hold run: it builds the worktree's pcrec,
  regenerates the subjects if absent, runs `run_game.py` over the full population
  (177 bench + 150 corpus) and writes `data/` + `data/summary.md`. Its log is
  `build/wg/chain.log`, and its completion line is `== wingame chain COMPLETE`.
- `data/` — the chain's committed output for 327 patterns (177 bench + 150 corpus):
  `spans.tsv`, `spaninfo.tsv`, `choices.tsv`, `sim.tsv`, `spanforms.tsv` and
  `summary.md` (the tables the note's §4.2 reads). Regenerate with `chain.sh`
  (~30 s); the `--emit-facts` listings stay in `build/wg/full/facts/`.
