# tests/axes — [CHK-2] piece 2: the answer-identity sweep

Sweeps the WHOLE `.rxt` corpus over every optimization-axis deny/force flag
(`docs/spec/tuning.md` §2, bits 4-31 of `pcrec_options.flags`) plus the
coarse `--engine=vm`/`--engine=dfa` axis (§2.11), comparing per-case ANSWERS
(match/nomatch/span/captures/give-up code) against the default build's —
never pass/fail COUNTS, which can agree while the underlying cases that
passed disagree. See `run_axes.sh`'s own header for the full design
rationale, the derived-registry mechanism, and the detect demonstration's
recorded transcript.

## Files

- **run_axes.sh** — the orchestrator (`make test-axes`).
- **utfcheck_arm.py** — [UTF-VALID] `-futf-check`'s OWN ARM (`docs/spec/tuning.md` §2.36).
- **memfn_arm.py** — [RUNAXES] the `--memfn=` ARM's reach (below, "The `--memfn=` arm").
- **dump_diff.awk** — the comparator: two `RXTDUMP` files keyed by `<.rxt file>:<line>` (unique — one case per source line), classifying every case AGREE / REFUSED / ...
- **startset_arm.py** — the product arm's mover count (above).

## The classification rule (manager's ruling, 2026-08-26, from the first
full-corpus sweep's own findings)

The first full-corpus `make test-axes` run FAILED four axes with **zero
genuine answer disagreement** — every failure was the comparator having
only two buckets (AGREE / everything-else) where the axis family's own
documented behaviour needs several. `dump_diff.awk` now classifies each
BASE key in this order:

(Rest of this section: see the history file.)

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
`HARNESS_BATCH=N` (forwarded, see above) batches that per-pass corpus
compile too.

Maintenance: update this file when files are added/removed or their roles
change.

(Rest of this section: see the history file.)

- Also (one-line entries for these are in the history file): `run_ksweep.sh`, `start_landing_movers.tsv`.
- `giveup1_key_check.sh`: light check (runs first in `make test-axes`) that GIVEUP1_ALLOWANCE's text-keyed entries (`file@pattern :: case`) resolve and survive a comment edit above them.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__axes.md`.
