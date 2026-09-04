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

## Pairwise execution ([TT-12] STEP 1 item 1, 2026-09-03)

The job list (bit-flag axes in bit order, then `--engine=vm`, then
`--engine=dfa` — same order and same `AXES=` filtering as before) is now
run TWO AT A TIME rather than strictly serially, each at `PROCS=ceil(PROCS/2)`
(6 each at the default `PROCS=nproc=12`). `docs/dev/tt12_step0_profile.md`
§4 is why this is close to additive rather than merely contending: a single
axis's wall time is bounded by ONE `.rxt` file's case count under the
harness's per-FILE `PROCS` dispatch (`tests/assertions/multiline.rxt` at
3,065 cases, 56% more than the next-largest file), not by `PROCS` reaching
`nproc` — the box already sits roughly half-idle through most of one axis's
own run for a reason unrelated to `PROCS` width, so pairing a second axis's
own independent bottleneck onto the idle half should roughly double
throughput. **Measured** (docs/dev/lanes/tt12b_report.md has the full
table): the sequential reference is opt5i's 4205s run (`axes2.log`,
2026-09-02); see the report for the paired total.

**Answer identity is unaffected by pairing — verified, not merely argued.**
Every AGREE/REFUSED/BUDGET/LOST/MISMATCH count is computed from `diffline`,
a value captured directly from `dump_diff.awk`'s own output into a local
shell variable; nothing about the verdict is read back from a file two
concurrent axes could both be writing. What COULD have been a genuine race
under pairing, and was fixed as part of landing it: `run_one_axis` used to
write the harness's stdout/stderr and the diff-awk's own stderr to FIXED
filenames (`$WORKDIR/axis.out`/`axis.err`/`diff.err`) shared across every
axis call — harmless when only one axis ever runs at a time, a real risk
for the DIAGNOSTIC TEXT a failure prints (`---- axis.out ----` etc.) once
two axes can be mid-run at once. Every such filename is now per-axis
(slug-derived, the same shape `dump`/`rowsfile` already used).

**Implementation shape**: a subshell (`( ... ) &`) cannot mutate this
script's own `fail` variable or append to its own `axis_results` array —
subshells do not write state back to their parent. Each backgrounded axis
call writes its own `pararesult_<slug>` file (the axis_results line it
would have appended, then its own `fail` value) and `paraout_<slug>` file
(everything it would otherwise have printed live); the parent re-absorbs
both, in job-list order, after `wait`ing on the pair — so the summary table
and AXIS FAIL semantics are IDENTICAL to the sequential form, only the
moment output appears (after both of a pair finish, not streamed live)
differs. `trap - EXIT` inside the subshell is load-bearing, not decoration:
the top-level `trap cleanup EXIT` (deletes the whole `$WORKDIR` unless
`KEEP=1`) is INHERITED by a forked subshell, so without disabling it there
the first background job to finish would delete `$WORKDIR` — including the
shared `BASE_DUMP` — out from under everything else still using it.

## K45 — tests/size/size_term.rxt's tower, documented (2026-09-03)

`tests/size/size_term.rxt:34-35`'s nested-repeat tower (`engine vm`-forced,
own header: "on the default axis this pattern refuses much earlier, at NFA
construction... a pre-existing limit that has nothing to do with the size
term") was RED on five axes with `refused_undoc=2` each — not a defect,
`REFUSAL_PATTERN` simply didn't have an entry (or the right substring) for
the route each axis's own denial takes through this specific pattern:

- `-fno-counter` — the pattern trips a SECOND diagnostic shape of the same
  replication cap (`PCREC_MAX_VM_REPLICATION_PRODUCT`): "nested bounded
  repeats would replicate a body N times in total", distinct wording from
  the single-level "a bounded repeat would replicate its body" the entry
  already matched.
- `-fprefilter` and `--engine=dfa` — forcing either requires the NFA/DFA
  build the `engine vm` directive was written to skip, so both reach
  `src/ir/nfa.c`'s own construction cap ("pattern too large (NFA exceeds
  ... states)") before either axis's own do-or-die machinery gets a chance
  to fire.
- `-fno-altcls-merge` and `-fno-size-term` had NO `REFUSAL_PATTERN` entry
  at all (correct in general — neither is documented as ever refusing under
  the default engine); on this tower specifically they reach real caps
  (the VM emitted-node cap; the emitted-code-bytes cap) rather than a
  defect, so each gained a one-line entry.

No `REFUSAL_FLOOR` was added for the two newly-populated axes: a floor
asserts a MEASURED population (K35), and the only measurement behind these
two is this one file's two cells, not a corpus-wide sweep. Verified live,
2026-09-03, against the full corpus: `refused_undoc=0` on all five axes,
`refused_doc` matching the pre-fix reference run plus exactly the two new
tower cells, every other AGREE/BUDGET/REFUSED count byte-identical.

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

- **run_ksweep.sh** — [ART-SIZE]'s K-SWEEP IDENTITY GATE (`make test-ksweep`,
  opt-in, 2026-08-29). `run_axes.sh` derives its axis list from
  `lib/pcrec.h`'s `PCREC_(NO|FORCE)_* = 1u << N` constants, so it sweeps only
  PREDICATE bits — and `--unroll=K` is a VALUE axis. Until this script **no
  gate proved any K answer-identical**, which is the size term's entire
  licence. [CHK-2] item (c) folds value axes into the generic sweep; this row
  is its named trigger and this script is the gate meanwhile.
  It reuses `dump_diff.awk` rather than inventing a second comparison, so the
  give-up/capacity exclusion is that file's OWN existing `budget=` bucket —
  the one `run_axes.sh` already uses. The exclusion is STATED in the header
  with the measurements justifying it (§6.1's step-budget, frame and
  `RX_TRAIL_FRAMES` figures), because those cells are genuinely K-dependent and
  a sweep including them would fail on a TRUE property. An exclusion with
  nothing behind it is how a defect hides, so on the excluded cells it still
  asserts that where BOTH sides give up they give up with the same CODE, and it
  PRINTS the excluded population's size.
  Its **interior-optimum report** is the standing census of whether the
  ladder's interior rungs earn their cost — it names any pattern whose argmin
  is interior. On its first run it found three, which is why the ladder is
  `[8,6,4,3,2,1]` and not its endpoints.

## [CC-DIFF] STEP 2 (2026-09-04) — the sweep gains an ORDINAL axis

`--vm-entry-shape=1..4` (`docs/spec/tuning.md` §2.21) joins the job list as
FOUR jobs, appended where `--engine=vm`/`--engine=dfa` are and for the same
mechanical reason: `RXTFLAGS` takes an arbitrary extra flag, not only a `-f`
spelling. Four rather than one, because "the answers do not move" is a claim
about each rung and not about the family.

**`lost_ok` IS 0 ON ALL FOUR, AND THAT IS STRICTLY STRONGER THAN THE COARSE
AXIS'S CLAIM.** `--engine=dfa` is DO-OR-DIE and legitimately refuses, so its
LOST population is documented rather than failed. This axis NEVER refuses: a
rung an artifact cannot legally take is a SELECTION OUTCOME, and the emitter
falls to the nearest legal rung of the same body-count family. A LOST case
here therefore means a pattern stopped compiling under a flag that cannot
make that happen, and it fails.

**WHAT IT COSTS AND WHERE TO CUT IF IT IS TOO MUCH.** Four more full-corpus
runs; [TT-12] STEP 1's pairwise execution absorbs them two at a time, so the
wall cost is about two runs' worth. The honest reduction is to keep rungs 1
and 4 and drop 2 and 3 — NOT to keep one representative, because 2 and 3 are
the rungs that emit the forward entries and the static empty descriptor, i.e.
the only new emitted code the step adds.
