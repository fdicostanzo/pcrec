# tests/axes — [CHK-2] piece 2: the answer-identity sweep

Sweeps the WHOLE `.rxt` corpus over every optimization-axis deny/force flag
(`docs/spec/tuning.md` §2, bits 4-15 of `pcrec_options.flags`) plus the
coarse `--engine=vm`/`--engine=dfa` axis (§2.11), comparing per-case ANSWERS
(match/nomatch/span/captures/give-up code) against the default build's —
never pass/fail COUNTS, which can agree while the underlying cases that
passed disagree. See `run_axes.sh`'s own header for the full design
rationale, the derived-registry mechanism, and the detect demonstration's
recorded transcript.

## Files

- **run_axes.sh** — the orchestrator (`make test-axes`). Derives the
  bit-flag registry from `lib/pcrec.h`/`cli/main.c` (never hand-copied —
  docs/dev/learnings.md §3), cross-checks it against `docs/spec/tuning.md`
  §2's own `(bit N)` headings, runs a baseline `tests/harness/run.sh` pass
  and one pass per axis (via that script's `RXTFLAGS`/`RXTDUMP` hooks — the
  latter added by this row), diffs every pair with `dump_diff.awk`, and
  cross-checks one DFA-side axis (`-fno-premul-table`) against LIVE
  libpcre2 through `tests/registry/run_pc4.sh`. `AXES=` restricts to a
  subset for a quick local run; `SKIP_ORACLE=1` skips the PC-4 leg.
- **dump_diff.awk** — the comparator: two `RXTDUMP` files keyed by
  `<.rxt file>:<line>` (unique — one case per source line), classifying
  every case AGREE / MISMATCH (answer moved) / LOST (case ran under
  default, not the axis) / GAINED (the reverse, never documented as
  possible for any axis).

## Conventions

`RXTDUMP` (documented in `tests/harness/run.sh`'s own header) is the ONE
env-var hook this row added to the harness rather than a new `.rxt`
directive — the same "general knob, not a one-off" shape `RXTFLAGS` took
(`tests/harness/CLAUDE.md`'s own [DD-14 wave G] entry). Empty by default,
so a plain `tests/harness/run.sh` run is byte-for-byte unchanged.

`make test-axes` is an OPT-IN battery stage (like `make strict`/`make
ubsan`), NOT part of `make test` — ~13 full corpus passes at roughly the
runtime of one `test-corpus` pass each. `docs/testing.md`'s "Answer-identity
sweep" section has the measured runtime and how to read a failure.

Maintenance: update this file when files are added/removed or their roles
change.
