# docs/design/memfn/probes/r17/upa/ — uses per activation of the set-FIND sites

Lane r17upa (2026-10-12), for the memfn kit manager: how many USES (calls of
"the next candidate at or after lo") one ACTIVATION of a set-FIND site gets on
pcrec-bench's own subjects. That decides whether a stateful form's carried
state pays (setfind.md rev 2.3 §9.2's (P); the bench request's Q3). Counts
only, no timing. Reading: `../reading_upa.md`. Report:
`docs/dev/lanes/r17upa_report.md`. Nothing here is built by pcrec's make, and
nothing reaches the default build. This is the filed `mfk-upa` counter's
question, answered by a probe script, not by a kit trace rendering.

- `upa.py` — the instrument. It compiles each bench pattern as the bench's
  pcrec testee does (`-p rx -fcomments --features all`, plus `--no-captures`
  for nocaps and `-e utf8` on the utf8 set). It finds every 256-entry table
  walk (census.py's `WALK_RE`) and writes an instrumented COPY: `upa_act` at
  the holding function's entry, and `upa_use(F, hit, pos)` after each walk. It
  builds the plain and instrumented artifacts into `upa_driver.c`, runs both
  over the set's subjects through the bench's own loader, and writes
  `counts.tsv`/`sites.tsv`/`controls.tsv`. Controls:
  - answer identity, plain vs copy;
  - answers against the bench's libpcre2 expectations;
  - hit positions strictly rising within an activation;
  - hits ≤ S-bytes × activations;
  - calls ≤ activations ≤ 2 × calls (the deep tier).

  `--plant` makes the copy skip every candidate, and the controls must fire.
  It needs the bench's tree regenerated into scratch (`--bench-src`, a
  `git archive` copy with its generators run; never the bench clone itself).
- `upa_driver.c` — the driver: search-short = one `rx_search(s, n, 0)` per
  short subject; find-all = match_api.md §3.1's loop (utf8 advance with
  `--utf8`). It mirrors pcrec-bench `testees/pcrec/timed.c` at 1cb906f6 and
  prints ANS/MONO/LVL lines per subject at the levels `fn:<id>` (one call of
  the holding function = the state lifetime), `call` and `pass`.
- `summarize_upa.py` — rolls `out/` into the reading's tables (`--compact`,
  `--rollup`, `--corner PPM`, `--hybrid`, `--members 30-39`, `--dense`,
  `--cells`); bands BELOW/IN-BRACKET/ABOVE against B_EVEN in (1, 4); a set's
  term count is an upper bound (ranges, complement ranges, census.py's cube
  cover).
- `cells_r17.txt` — the R-17 named cells (setfind_bench_request.md §2 item 1),
  bench name and kit name.
- `out/` — the run: `counts.tsv.gz` (one row per cell × config × regime ×
  subject × level, with the histogram), `sites.tsv`, `controls.tsv`,
  `planted_controls.tsv`, `tables.md` (every generated table) and
  `provenance.txt` (pins, box, commands, completion lines).

Re-run (light, about 3 minutes on 4 cores; pin it, e.g. `taskset -c 12-15`):
`git -C <bench> archive HEAD bench pcrecbench schema testees | tar -x -C
build/upa/benchsrc`, run each set's `gen_subjects.py` and
`gen_throughput_subjects.py` there and check the manifests reproduce, then
`upa.py --pcrec build/pcrec --bench-src build/upa/benchsrc --out build/upa/all`.

Maintenance: update this file when files are added/removed or change roles.
