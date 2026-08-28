# tests/offsetskip — [OPT-K]'s OFFSET-k candidate-start skip, as answers

One `.rxt` file, `offset_skip.rxt`, picked up by `make test-corpus` like every
other corpus directory (`tests/harness/run.sh` sweeps every `*.rxt` under
`tests/`). There is no runner script here and there should not be: what this
directory owns is ANSWERS, and the mechanism's structural facts live in
`tests/codegen/run_offset_skip.sh`.

## What it checks, and what it deliberately does not

The offset-k skip is ANSWER-IDENTITY-PRESERVING BY CONSTRUCTION — every test
it adds to a candidate start is a NECESSARY condition of a match beginning
there (`docs/design/offset_k_skip.md` §3.2) — so its correctness ARGUMENT is a
proof and its correctness GATE is `make test-axes` under `-fno-offset-skip`,
which compares the whole corpus case by case across the axis. This file is
neither of those, and a reader who takes it for either will over-trust it.

What it is is the ARITHMETIC of the emitted skip, exercised where arithmetic
can be wrong: the `cand = hit - k*` mapping at the subject START, the
`cand + maxk >= n` guard at the subject END, overlapping candidates and the
resume, restarts (`ms <P>`, which is one iteration of a find-all loop), the
RESEED, and a block of negative examples the selection declines.

## THE TWO FILES NAME THE SAME PATTERNS ON PURPOSE

Every §1-§6 block here uses a pattern `tests/codegen/run_offset_skip.sh` §2
independently requires to SELECT the form. Without that pairing this file
would pass exactly as well on a compiler that had stopped emitting the skip
altogether — which is [MECH-REACH]'s failure and this project's most-recorded
check defect (a corpus that silently stopped exercising its mechanism).
Sabotage row S187 is that failure made real: the selection never fires, this
file stays 80/80 GREEN, and only the population check goes red.

## THE ONE ROW THAT EARNED ITS PLACE BY MEASUREMENT

§4's `[-a]{3}-b` block is the only thing here that turns the RESUME's
off-by-one (`pos = cand + 1 + k*` instead of `pos = cand + 1`) into a wrong
answer, and it exists because the first draft of this file claimed four other
patterns did and MEASURED FALSE — the plant left the whole file 75/75 green.

The reason is structural and worth carrying: the plant loses a match only when
a real start `p` lies in `(cand, cand + k*]`, which puts the failed
candidate's own scan byte at match offset `h - p < k*` — so the pattern must
ALLOW its scan byte somewhere BEFORE the offset it is scanned at. `uuid` and
`iso-ts` have hex and digits before their `-`; `stack-frame` has `a` before
its `t`; `needleXYZW` has `needle` before its `X`. None can express it.
`[-a]{3}-b` scans `-` at offset 3 and permits `-` at 0-2, so it can.

The generalisable lesson is the one this tree keeps re-learning: a row that
EXERCISES a line is not a row that DETECTS a change to it, and the difference
is only ever visible by planting the change.

## Oracle

python3 `re` (CLAUDE.md's base tier), through `tests/harness/verify_rxt.py`.
Every expectation was produced by running that oracle rather than by reading
the emitter, and it refuted three of the first draft's rows — two `\b` cells
whose author forgot the assertion reads the byte to the LEFT, and a `n` row
whose subject contained a second, later match the author was not thinking
about. No `\Z` appears here, so `tests/assertions/absolute.rxt`'s oracle
carve-out does not apply, and no block is `# pcre2-only`.

## Maintenance

Update this file when the corpus gains a section or a pattern whose selection
is asserted elsewhere. If a pattern here stops selecting the offset-k form,
`tests/codegen/run_offset_skip.sh` §2 fails first and names it — fix the pair,
never one side.
