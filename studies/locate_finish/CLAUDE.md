# studies/locate_finish/ — the LOCATE × FINISH census (lane locfin, D156)

Compile-side census behind `docs/design/locate_finish.md` (§3, §4): which
locator and which finisher every corpus and bench artifact gets TODAY, and the
populations the note's new rows would reach. No subject is matched and no
clock is read. First pin: main `525dec33` (abi 71), Linux dev box, gcc 15.2;
pcrec-bench read at `76e13c1d` (read-only). RE-RUN pin (lane locfin2, panel
LF-C10): main `7efca415`, src identical to `525dec33`; pcrec-bench read at
`76e13c1d624739a069afe863297c262f4d936b4f`; 5,798 rows (5,355 compiled), 17 s
at JOBS=6. Every pre-existing `rows.tsv` cell and every T1-T8 line is
byte-identical to the first run; only the control block moved.

- `census.py` — builds the two populations and runs the end-pin probe by
  IMPORTING `docs/dev/optloop/revend/census.py` (`bench_pop`, `corpus_pop`,
  `run_probe`), so this census and [OPT-REVEND]'s count the same rows the
  same way; the probe is `docs/dev/optloop/revend/revend_probe.c` built from
  its committed source against this tree's `build/libpcrec.a`
  (`gcc -O1 -Ilib -Isrc docs/dev/optloop/revend/revend_probe.c build/libpcrec.a -o PROBE`).
  Per row: `pcrec --emit-facts` (the `kinds`/`start_anchor`/`end_window`
  facts, the end_window decline reason `f_end_window_why`, and the decision
  stamps, now including `VM_RESEED`) and the emitted C itself (TEXT: a reverse
  machine present, an inlined prefilter present). Env and the exact command
  are in its docstring. Writes `results/rows.tsv` (committed gzipped).
- `analyze.py` — four CONTROLS first (C1 stamp vs text on the reverse
  machine; C2 stamp vs text on the inlined prefilter; C3 the borrowed probe vs
  the SHIPPED `end_window` fact, TWO-SIDED; C4 the census's exact/superset
  hybrid classifier vs the independent `RX_VM_RESEED` stamp); it exits 1 and
  prints no table if any disagrees. Then tables T1-T8 (today's pairs, hybrids
  by their prefilter's locator, the end-pinned population by pair, the
  stage-1 / stage-2 / relaxed-reverse populations, their bench members, D-2's
  population). `results/summary.txt` is its verbatim output.
  - C3 forward: shipped numeric `end_window` => probe view in {`$`,`\z`}
    (400 rows, 0 disagree). C3 forward-width: shipped numeric => probe cwmax
    finite, except the DECLARED exception "pattern calls a group" (138 rows,
    all corpus): the probe never runs the call expansion, so it reads
    `^(a|b)\g<1>$` unbounded where the shipped fact says 3; classified from
    the pattern text. C3 converse: probe pinned AND probe cwmax finite =>
    shipped numeric, except the two DECLARED exceptions endwin.c's header
    names that can reach the premise: multibyte encoding (22 rows, all
    utf8, 16 distinct) and `\G` (2 rows, `\G\z`, `\G$`). They are classified
    from the row's encoding and the probe's `gstart`, never from the shipped
    answer; the shipped decline reason (`f_end_window_why`) is read only to
    confirm it matches. The other endwin.c declines (unbounded, multiline,
    not end-anchored) cannot reach the premise. A converse failure outside
    the declared exceptions exits 1.
  - C4: every compiled hybrid, classifier `F-vm-span` iff `RX_VM_RESEED` is
    `exact` (the RETRY row `exact`, first in its slot, deny mask 0, predicate
    `Vm.mrl_win`): 759/0/0/734; no structural exception; also asserts the
    stamp exists on every hybrid and on no non-hybrid, and prints the
    atomic/lookaround/lang counts as a positive control on the kind-name
    spellings. Sabotage-validated (a flipped stamp, a flipped fact, a flipped
    superset stamp each exit 1).
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
