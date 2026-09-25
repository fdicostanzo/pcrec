# docs/dev/optloop/s1/ — the instruments behind docs/design/litscan_s1.md

Lane `s1design`, 2026-09-25, from main `b5c1423b`. Design-time COUNTS only:
nothing here reads a clock (darwin timing is never citable). Read-only
against `/Users/fdicostanzo/pcrec-bench` (patterns, subject generators,
`pcrecbench.reduce`); every build and subject lives in a session scratch
directory, never here.

## Files

- `probe_patch.py` — applies the census PROBE to a scratch `git archive` of
  the base (asserts its one anchor, the `REQ_WHY` stamp site in
  `src/gen/emit_dfa.c`): one `S1\t...` stderr line per compile when
  `$S1PROBE` is set, read off `req_admit`, `unanch_start`, `dfa_pf_of` and the
  offset-k walk. SCRATCH ONLY, never applied to a tracked tree.
- `census.py` — drives the probe over the bench (both auto configs) and the
  `.rxt` corpus (reusing `../c2/reqpos_census.py`'s population builders) and
  classifies every artifact into the note's §6 classes (A/B/C/D/E/V/P).
  Outputs `census.tsv` (one row per artifact-config) and
  `census_summary.txt` (the tallies §6 quotes; C1/C2 and B's sub-split are
  computed from the TSV in the note).
- `mk_twin.py` — router's S1 TWIN, hand-made from the base's `-fno-req-run`
  artifact (`--twin`), and the COUNT instrumentation (`--count`: `memchr`
  and forward-step counters) for any router arm.
- `count_driver.c` — the find-all driver the counted arms link against:
  matches, calls, `memchr` calls, DFA steps and an FNV hash of every span.
- `twin_counts.txt` — the transcript: arms (a) shipped, (c) `-fno-req-run`
  (= `25b1984f`'s program), (b) S1 for router, and shipped vs
  `-fno-req-byte` (= S1 = `25b1984f`'s program) for keyword, on the 3
  throughput + 75 short subjects (sha256 75/75, 3/3). Span hashes equal
  across every arm of a pattern.
- `router_c_identity.sh` — S1 review (lane `s1rev`, 2026-09-25) C1's
  reproducible recipe for the litscan_s1.md §10 claim "arm (c) was verified
  program-identical at `b5c1423b`": git-archives 25b1984f and a HEAD ref to
  a scratch dir, builds both with the pinned compiler, emits router
  (`/user|/users`) from each (25b1984f predates `-fno-req-run`, so its
  default artifact IS arm (c) there; HEAD compiles with `-fno-req-run`),
  and diffs. `router_c_identity_output.txt` is its recorded run.

## Reproduce

    SCR=<scratch>; git -C <repo> archive b5c1423b | tar -x -C $SCR/probe
    python3 probe_patch.py $SCR/probe && make -C $SCR/probe CC=gcc-16 build/pcrec
    PROBE=$SCR/probe/build/pcrec PCREC=$SCR/probe/build/pcrec \
      BENCH=/Users/fdicostanzo/pcrec-bench CORPUS=<repo> OUT=. python3 census.py
