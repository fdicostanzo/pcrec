# r1tri — triage of lane/r1land's three Linux reds (2026-10-03)

Lane r1tri (opus), branch `lane/r1tri` from `lane/r1land` tip `d832fc2a`.
Input: the full Linux `make test` at `d832fc2a`, MAKE_RC=2, log
`ubuntubudu:/home/duxevents/pcrec/scratch_lx/r1_d832fc2a.log` (verdict lines
4298 / 4397 / 5520). Not merged; the manager merges r1tri into r1land.

**Verdict: all three reds are STALE PINS left by landed mechanisms (the
"readers the lanes missed" class). No real regression, no box stall.** All
three fixed in one commit, `80fafb4a`.

## Fix 1 — test-lookaround (Makefile:951): §6.3 population pin

- Section: `tests/lookaround/run_expansion_diff.sh`, 13 FAILs = §1's 10
  population counts + policy P1/P2/NONE's 3 pattern counts. The three-way
  comparisons themselves were all green (B == C on 11,045 cells, §1c
  fidelity green, 0 disagreements).
- Cause: [OPT-VEDGE]'s `tests/assertions/view_edge.rxt` (commit `e43b4cbb`),
  the only `tests/assertions/` change between merge-base `af615d01` and
  `d832fc2a`. Counted against the file: 17 `pattern` lines, 2,703 m/n/ms/ns
  lines = exactly the +17 / +2,703 deltas. All six Q1-Q6 pairs are unchanged
  in the red log (87/0, 87/754, 0/0, 31/1106, 0/0, 0/0) and tot_g/qual_g are
  unchanged, so every new block qualifies. Each block has one substitutable
  occurrence: 14 `\z` (identity rows, `\z` occurrences 49 -> 63, identity
  +14 on both policies) and 3 that insert a lookaround (`\Z` once, `$`
  twice), which gives the +3 on p1/p2_lookaround.
- Classification: stale pin. lane vedge did not re-pin it.
- Fix: re-pinned `exp_pop`, the §1 ok message, the `report_policy` literals,
  and the header prose; added a DELTA 3 note naming the corpus change:
  482->499 / 10202->12905 / 277->294 / 8342->11045 / P1 277->294 /
  P2 377->394 / id 58->72, 86->100 / look 211->214, 261->264.

## Fix 2 — test-resource (Makefile:1212): K59-PREMUL rung byte count

- Section: `tests/resource/run_resource_tests.sh`, 1 FAIL: `'a{5,25000}'
  -fno-scan-edge -fno-start-pinned rescued at 762574 bytes, pinned 762551`.
- Cause: S4 C1's `<PREFIX>_RUN_WORDS` stamp (commit `6493b1f1`). I diffed the
  artifacts from merge-base `af615d01` (abi 55) and `d832fc2a` at the same
  `-o` basename. Three lines differ: the two abi digits (same length) and one
  inserted line `#define RX_RUN_WORDS 0`, which is +23 bytes.
- Classification: stale pin. lane s4build did not re-pin it. Note: c3build
  (abi 59) adds more stamps and will likely move this number again on its
  own branch.
- Fix: 762551 -> 762574, with a RE-PINNED AGAIN note and a history entry in
  the ok message.

## Fix 3 — test-cpset-structure (Makefile:601): wclass [W1]

- Section: `tests/codegen/run_wclass_census.sh` (chained by
  test-cpset-structure), 1 FAIL: `[W1] éabc: no five-byte run`.
- Cause: S4 C1's `overlap` row now spells the five-byte run as two
  overlapping `rx_w4` words, and [W1] grepped only for the `memcmp(...,5)`
  form. I checked on r1land's own binary: the default artifact has
  `rx_w4(subject + scan_position) == rx_w4("\303\251ab") && rx_w4(subject +
  scan_position + 1) == rx_w4("\251abc")`, and `-fno-run-overlap` gives back
  the `"\303\251abc", 5)` memcmp (2 sites).
- Classification: stale reader. Same finding as lane c3build. I applied
  c3build's hunk from `1798fcc2` verbatim (only that file's diff): either
  spelling passes.

## Validation (Mac, under the suite lock, `make -k CC=gcc-16 <section>`)

- test-cpset-structure: RC 0, no `*** [` line ([W1] PASS).
- test-resource: RC 0, no `*** [` line (K59-PREMUL PASS at 762574 bytes, the same figure the Linux red printed, so the pin holds on both boxes).
- test-lookaround: RC 0, no `*** [` line. run_expansion_diff.sh 11/0: the §1 population passes at 499 / 12,905 / 294 / 11,045, and P1/P2/NONE 294/394/294 run 0 disagreements against local libpcre2.

Log: `/var/folders/sj/jbcblbpx13n6342cgcfhgbxr0000gn/T/r1tri.Hu6u/val.log` (session scratch), with `*** [` count 0. **Validation COMPLETE** for the three targeted sections. The full `make test`
was not run; the full battery is the manager's at merge.
