# studies/locate_finish/ — the LOCATE × FINISH census (lane locfin, D156)

Compile-side census behind `docs/design/locate_finish.md` (§3, §4): which
locator and which finisher every corpus and bench artifact gets TODAY, and the
populations the note's new rows would reach. No subject is matched and no
clock is read. Pin: main `525dec33` (abi 71), Linux dev box, gcc 15.2;
pcrec-bench read at `76e13c1d` (read-only).

- `census.py` — builds the two populations and runs the end-pin probe by
  IMPORTING `docs/dev/optloop/revend/census.py` (`bench_pop`, `corpus_pop`,
  `run_probe`), so this census and [OPT-REVEND]'s count the same rows the
  same way; the probe is `docs/dev/optloop/revend/revend_probe.c` built from
  its committed source against this tree's `build/libpcrec.a`
  (`gcc -O1 -Ilib -Isrc docs/dev/optloop/revend/revend_probe.c build/libpcrec.a -o PROBE`).
  Per row: `pcrec --emit-facts` (the `kinds`/`start_anchor`/`end_window`
  facts and the decision stamps) and the emitted C itself (TEXT: a reverse
  machine present, an inlined prefilter present). Env and the exact command
  are in its docstring. Writes `results/rows.tsv` (committed gzipped).
- `analyze.py` — three CONTROLS first (C1 stamp vs text on the reverse
  machine; C2 stamp vs text on the inlined prefilter; C3 the borrowed probe's
  end pin vs the SHIPPED `end_window` fact); it exits 1 and prints no table if
  any disagrees. Then tables T1-T7 (today's pairs, hybrids by their
  prefilter's locator, the end-pinned population by pair, the stage-1 /
  stage-2 / relaxed-reverse populations, their bench members).
  `results/summary.txt` is its verbatim output.
- `finish_sites.sh` — the FINISH decision as spelled today: every code line
  under `src/gen/` testing `fit.chosen`, `fit.prefilter` or `prefn`.
  `results/finish_sites.txt` is its output; the note's §3.3 dispositions it.

**The instrument defect it caught in itself (recorded, not hidden).** The
first run's TEXT marker was `rx_reverse_next_state`; C1 read 146
disagreements, all artifacts whose reverse machine uses the uniform-fold
representation (`[CC-DIFF]`), which has no next-state accessor. The marker is
now any `rx_reverse_` identifier and C1 reads 0; without the control the
census would have reported 146 reverse-pass artifacts as having no reverse
machine.

Regenerating `rows.tsv.gz` (a new pin, a grown corpus) moves `summary.txt` and
every population number in `docs/design/locate_finish.md`; no check reads
these files.
