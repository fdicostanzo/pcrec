# tests/axes — [CHK-2] piece 2: the answer-identity sweep

Sweeps the WHOLE `.rxt` corpus over every optimization-axis deny/force flag
(`docs/spec/tuning.md` §2, bits 4-31 of `pcrec_options.flags`) plus the
coarse `--engine=vm`/`--engine=dfa` axis (§2.11), comparing per-case ANSWERS
(match/nomatch/span/captures/give-up code) against the default build's —
never pass/fail COUNTS, which can agree while the underlying cases that
passed disagree. See `run_axes.sh`'s own header for the full design
rationale, the derived-registry mechanism, and the detect demonstration's
recorded transcript.

**THE BIT RANGE IS `4..31` AND THE UPPER END IS NOT A FACT ABOUT THE FAMILY.**
It read `4..15` — the family's extent on the day this was written — and
[OPT-K]'s bit 16 was therefore DERIVED AWAY SILENTLY: a new axis absent from
the sweep with no failure, which is the exact "an axis shipped without its
five things" gap this row exists to close, arriving through this row's own
instrument. Only the LOW bound does real work (bits below 4 are unrelated
`1u << N` constants in the same header). The section anchor for the doc
cross-check does not spell the axis count in English either, for the same
reason: it read `/^## 2\. The thirteen axes/`, [OPT-K] correctly renamed that
heading, and the range then matched nothing and the check compared against an
EMPTY documented column. Anchor on numbers a human does not maintain.

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
  every case AGREE / REFUSED / BUDGET / LOST / MISMATCH / GAINED — see
  "The classification rule" below.

## The classification rule (manager's ruling, 2026-08-26, from the first
full-corpus sweep's own findings)

The first full-corpus `make test-axes` run FAILED four axes with **zero
genuine answer disagreement** — every failure was the comparator having
only two buckets (AGREE / everything-else) where the axis family's own
documented behaviour needs several. `dump_diff.awk` now classifies each
BASE key in this order:

1. **AGREE** — `trc` and `out` identical on both sides.
2. **REFUSED** — the axis side is a compile-time refusal
   (`tests/harness/run.sh`'s `RXTDUMP` `REFUSED` producer: pcrec itself
   declined the pattern under this axis's flag, `trc=REFUSED`, `out` =
   pcrec's own diagnostic text). `dump_diff.awk` does not know whether an
   axis's OWN documented limit produced it — that is `run_axes.sh`'s job
   (below), via `REFUSAL_PATTERN`/`REFUSAL_FLOOR`.
3. **BUDGET** — neither side is REFUSED, the two disagree, and EITHER
   side's `trc` is `3` (a give-up — `driver.c` exits 3 uniformly for
   steps/frames/work) or `124` (a per-case harness timeout). `tuning.md`
   §2.5's "identity holds modulo which budget binds" is the spec sentence
   this extends to the harness's own per-case wall timeout: a budget
   boundary moving under a denied optimization is not an answer
   disagreement.
4. **LOST** — the axis produced NO record for this key at all (not even a
   REFUSED one) — a structural gap beyond a documented refusal: a PROCS
   worker vanishing, a whole file failing to parse. Always a failure.
5. **MISMATCH** — neither REFUSED nor budget-bound, and the two disagree: a
   genuine answer difference. Always a failure.
6. **GAINED** — a key the axis produced that the baseline never had. Never
   documented as possible for any axis; always a failure.

**`run_axes.sh` does the axis-specific half of step 2**: `REFUSAL_PATTERN`
is a per-flag lookup of the SUBSTRING that axis's own documented limit's
diagnostic contains (verified live against the shipped `ctx_fail` text,
never guessed) — `"would replicate its body"` for `-fno-counter`'s
replication cap, `"-fprefilter requires the VM engine"` for `-fprefilter`'s
force-refusal, `"requires the VM engine"` (the shared phrasing every
`select_engine.c` do-or-die refusal under `--engine=dfa` uses) for the
coarse engine axis. A REFUSED case whose text matches is
**REFUSED-DOCUMENTED**: counted as a population, floored (K35,
`REFUSAL_FLOOR`) so a change that quietly stops the mechanism firing is
caught, never a failure. **A REFUSED case whose text does NOT match — or
whose axis has NO `REFUSAL_PATTERN` entry at all — is promoted to a real
failure**, printed loudly as an UNDOCUMENTED refusal. This is deliberately
NOT a blanket per-axis exemption: `tuning.md` documents every bit-flag axis
except the force-prefilter pair as NEVER refusing under the default (auto)
engine this sweep uses, so an axis with no entry treats ANY refusal as
worth investigating rather than silently absorbing it.

Per-axis output line: `agree=N budget-bound=N refused-documented=N
(floor F) lost-other=N mismatches=N gained=N` — every bucket printed
beside the verdict, never only a pass/fail count.

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
