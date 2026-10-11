# docs/dev/optloop/rewtwin/ — the `rev-end-width` twin (lane rewtwin, 2026-10-11)

Measurement only. The twin is a scratch emitter change on branch
`lane/rewtwin-scratch` (NOT for merge); this directory holds its patch, the
answer-identity sweep, the timing, and the data. Reading:
`../../lanes/rewtwin_report.md`.

## Files

- `twin.patch` — the scratch change to `src/gen/emit_dfa.c`'s
  `emit_rev_end`, against main 2f438878 (the two commits of
  `lane/rewtwin-scratch`). Under a fixed byte width W, on a DFA-hat entry and
  a byte-boundary encoding, the walk is replaced by AT(n-1-W) (only under
  `$`/`\Z` with a final newline) and then AT(n-W), each handed to the
  artifact's own match-here entry (FIN3 verify-at). The first one that
  matches is the leftmost match.
- `identity.py` — the answer-identity sweep. For each row it compiles today,
  the twin and `-fno-rev-end`, and links them with libpcre2-8 (10.46) in one
  driver. It then compares every artifact's search answer, including every
  capture pair, with `pcre2_match` at EVERY start position (every character
  boundary under utf8). The subjects are the bench's litrun short and
  throughput subjects (the last 200 bytes of each throughput subject), plus
  edits of each and an exhaustive sweep over a per-row alphabet.
  `identity.log` is the transcript: 70 rows, 6,072,394 cells per artifact,
  0 differences. The `identical-text`/`TWIN` label is a heuristic based on
  prefix substitution: `aws/whole` caps reads `TWIN` but is byte-identical
  apart from the prefix.
- `timing.py` + `timing_onebinary.tsv` — the FIRST timing shape: four arms
  linked into one binary. It is kept as the record of why it was replaced.
  Its second copy of today's identical text read up to x1.30 off the first,
  so at 2-5 ns it measured layout.
- `timing_pad.py` — the timing of record. Each arm is alone in its own
  binary, preceded by `.skip PAD` (8 pads, 0..112 step 16, the K87 control)
  and built with `-O2 -falign-functions=64`. Runs are pinned to CPU 3 with
  `taskset`, 3 rounds x 8 pads with the arms rotated, and each launch reports
  the median of 9 timed passes. The arms are `today`, `twin`, `norevend`
  (`-fno-rev-end`) and `twininl` (the twin with `__attribute__((flatten))` on
  `rx_search`, a hand edit that inlines the verify-at call). The regimes are
  `short` (the 27 litrun short subjects) and `long` (the 27 ~64 KiB
  throughput subjects), with one `rx_search(s, n, 0)` per subject.
- `summarize.py` — reduces a `timing_pad` TSV. For each cell it gives the
  median over launches and the layout band (min..max of the per-pad medians),
  with ratios to `today`.
- `timing_pad_run1.tsv` / `summary_run1.txt` — run 1 (three arms, no
  `twininl`), load1 0.98.
- `timing_pad_run2.tsv` / `summary_run2.txt` — run 2 (all four arms),
  load1 1.06-1.13. Its three shared arms reproduce run 1 to within about 1%.

## Re-running

    W=/home/pcrec/projects/pcrec/worktrees
    # subjects: the bench's published bench/litrun/{subjects,throughput} (read-only copy)
    python3 -I identity.py   $W/rewtwin/build/pcrec $W/rewtwin-scratch/build/pcrec SUBJ WORK
    python3 -I timing_pad.py $W/rewtwin/build/pcrec $W/rewtwin-scratch/build/pcrec SUBJ WORK OUT.tsv 3
    python3 -I summarize.py OUT.tsv

`SUBJ` must contain `subjects/` and `throughput/`, as copied from
pcrec-bench `bench/litrun/` (sha256 checked against its `manifest.tsv`).
