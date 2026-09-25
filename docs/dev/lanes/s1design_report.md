# Lane `s1design` — `[OPT-LITSCAN]` S1 design note (2026-09-25)

Branch `lane/s1design` from main `b5c1423b`. Tier: opus. DESIGN ONLY: nothing
under `src/`, `cli/`, `lib/` or `tests/` changed, and no `make test` was run.
`build/pcrec` was built in the worktree for artifact reads.

## Delivered

- `docs/design/litscan_s1.md`: the S1 design note (plus its entry in
  `docs/design/CLAUDE.md`).
- `docs/dev/optloop/s1/`: the census probe patch, `census.py`,
  `census.tsv`/`census_summary.txt`, router's twin generator, the count
  driver and `twin_counts.txt` (its own `CLAUDE.md`, plus an entry in
  `docs/dev/optloop/CLAUDE.md`).

## Validation (what was run)

**Program identity.** At `b5c1423b`, `-fno-req-byte` (keyword) and
`-fno-req-run` (router) produce artifacts whose matcher code is identical to
`25b1984f`'s build. The diff is only the header comment/include line, `.abi`,
`.flags` and `rx_info`'s `vars`/`nvars` pair. Verified with a scratch
`git archive 25b1984f` build.

**Answer check and counts.** Subjects were regenerated from pcrec-bench's
generators: 75/75 short and 3/3 throughput, all sha-matched. Every arm of
each pattern produced the same span hash:
- router arms (a), (c) and (b)-twin: 312 thr matches and 1 short match;
- keyword arms: 9,467 thr matches and 4 short matches.

The counts are in `twin_counts.txt`.

**Census.** 235 bench patterns × 2 auto configs, and 3,576 corpus rows, under
the probe. It exited 0, and 423 corpus rows and 14 bench patterns were refused
by the compiler, as expected.

**Nothing timed on darwin.** The ns figures come from the bench's Ryzen
records, reduced with `pcrecbench.reduce`.

## For a resuming agent

The note's §9 holds four questions for Frank:
1. whether to convert the floating pre-check loop to the one search block in S1;
2. class C2;
3. the VM seed as its own row;
4. a K64-sibling witness for the one-byte density clause.

§10's Linux request is written for AFTER the implementation lands. No
pre-implementation run is requested (D77). A D6 panel follows. The
implementation lane's checklist is §1 (the rows and conjunct), §3's
verification list and §7 (abi/spec/sabotage/anchors). Rebase against k64fix
(abi 33, S274) if it has merged.
