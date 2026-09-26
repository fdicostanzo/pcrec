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
  `census_summary.txt` (the tallies §6 quotes; C1/C2/C0 and B's sub-split
  are computed from the TSV, `class_c_split.py` below, not by `classify()`
  itself). **`classify()`'s B branch was CORRECTED by S1 review C2
  (2026-09-25, lane `s1rev`)**: it now folds litscan_s1.md §1.1 clause 3's
  second disjunct in full (`clause3b`: `pin + idx == 0`, `pf == "memchr"`
  exactly, and the memchr byte equal to `run[idx]`) instead of the loose
  `not sel and pf != "none"` the first cut shipped with. The committed
  `census.tsv`/`census_summary.txt` are this corrected run's output
  (re-run against `b5c1423b`'s own corpus, byte-identical to a run against
  the current tree's corpus — the two commits' `tests/` content is
  unchanged for this population). The rebuilt corpus count is **513**
  program-changing artifacts, not the note's original hand-adjusted 523 —
  see litscan_s1.md §6 for the reconciliation (8 rows excluded, not 3; 5 of
  the 8 are a form the note's own hand count missed, `pf == "memchr-bounded"`
  under a view, not the plain `memchr` clause 3(b) names).
- `class_c_split.py` — S1 review C2's downstream split of `census.tsv`'s
  single `C` tag into C1 (sel non-empty, the starred scan offset equals the
  pick's offset `pin + idx`) / C2 (sel non-empty, it does not) / C0 (sel
  empty — clause 3(b) also failed; a B-shaped residual neither C1 nor C2's
  own definition covers, since both assume a k-set exists). Also prints
  each population's `program changes = A + B + C1 + E`. Reads `census.tsv`
  directly (the raw `sel` string still carries the starred offset;
  `classify()`'s own parsed `sel` list does not).
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

- `probe_b_patch.py` — lane `s1b`'s option-B probe (litscan_s1.md
  revision 2, §6.1): the SAME `S1\t...` line and keys as `probe_patch.py`
  (so `census.py`'s `classify()` reads it unchanged), plus `kind`, `cbyte`,
  `views`, `seeded`, `se` (today's `pcrec_dfa_scan_state_written`), `implm`
  (the MODEL's selection verifies the run, read off `sel` rather than off
  the selected row's name) and `rowb` (the run row predicate as option B
  writes it, clauses 0-4, evaluated on EVERY artifact regardless of
  REQ_WHY). Same anchor, same SCRATCH-ONLY rule.
- `census_b.py` — option B's census: re-uses `census.py`'s `probe` and
  `classify`, splits C → C1/C2/C0 by `class_c_split.py`'s rule and A →
  A/A2 by G1's identity conjunct (scan byte == pick, off the probe's own
  walk), cross-tabulates `rowb` against the classes, and computes the
  program-change total itself (A + E + rowb) — no hand arithmetic.
  Outputs `census_b.tsv` / `census_b_summary.txt` (at `b5c1423b`, the
  panelled base, corpus from that tree) and `census_b_main.tsv` /
  `census_b_main_summary.txt` (at `4976f385`, revision 2's branch point).

## The build lane's instruments (lane `s1build`, 2026-09-25, base `27a63314`)

- `census.py` was CORRECTED by this lane: `probe()` passed the pattern as a
  latin-1-decoded `str`, which `subprocess` re-encodes UTF-8 into argv, so
  every non-ASCII pattern was probed as MOJIBAKE. It now passes the bytes.
  The 8 corpus class-`B` rows that were artefacts of it (all under
  `tests/utf8/`) drop out: the corpus program-change count is **505**, not
  513. `census_b_27a63314.tsv` / `_summary.txt` are the corrected census at
  the build's base.
- `s1_identity.py` — the per-commit identity gate (distinct-pattern
  populations, auto + `--engine=vm`), with the abi-digit normalization.
- `s1_movers.py` — the mechanism's movers BY ID against `census_b.tsv`, over
  census_b.py's own populations; `EXPECT` names the classes predicted to
  move, `EXTRA`/`BOTH` add a deny flag to one or both sides.
- `s1build_movers.txt` — both tools' transcripts for every step: steps 1-4
  zero movers; 5a exactly A+E; 5b exactly A+E+rowb (505 corpus, 110 bench);
  `-fno-run-prefilter` exactly A+E; `-fno-offset-skip` on both sides zero.
- `rowj_reach.py` / `rowj_reach_output.txt` — sabotage row (j)'s
  reachability RUN (litscan_s1.md R3-11): the plant built for real, both
  populations swept, 0 artifacts moved (S284's derivation).

## Step 6's instrument (lane `s1step6`, 2026-09-26, base `54bb1159`)

- `s1step6_movers.py` — the Q1 conversion's movers BY ID and its RESIDUE:
  bench (caps/nocaps, each also `--engine=vm`) and corpus (auto,
  `--engine=vm`, `-e utf8`) from BASE and NEW; predicted = BASE stamps
  `REQ_WHY "emitted"` with a `REQ_RUN`. Per artifact: changed iff predicted,
  stamps identical, the texts byte-identical once BASE's `rp_pos` loop(s)
  and NEW's `rx_reqrun*` block(s)/call(s) are removed, and one block per old
  loop with the same run and scan byte. `LIST=` writes the changed ids (the
  bench pin's mover list). `s1step6_movers.txt` is its recorded run and
  `s1step6_movers_list.tsv` the ids.

## Reproduce

    SCR=<scratch>; git -C <repo> archive b5c1423b | tar -x -C $SCR/probe
    python3 probe_patch.py $SCR/probe && make -C $SCR/probe CC=gcc-16 build/pcrec
    PROBE=$SCR/probe/build/pcrec PCREC=$SCR/probe/build/pcrec \
      BENCH=/Users/fdicostanzo/pcrec-bench CORPUS=<repo> OUT=. python3 census.py
