# studies/cls_tree_study — the [CLS-TREE] prototype-before-commit study

Backs `docs/dev/cls_tree_study.md`. Read the memo for the findings; this file
is the reproduction recipe and the things a future reader needs in order not
to re-learn them.

Nothing here is built by pcrec's `make`, linked into pcrec, or run by
`make test`. It reads two things out of the tree — `src/parse/uprops_tables.inc`
(the generated property sets) and `tests/**/*.rxt` (corpus patterns, compiled
by `build/pcrec`) — and writes only under this directory.

## Reproduce

    make discover            # the C sectioning DP
    make populations         # print the three study populations
    make k53                 # the 12 K53 sets, every policy: size + verify
    make baseline            # what pcrec emits TODAY for the same 312 sets
    make uprops              # the 312 property sets, 3 policies
    make byteclasses         # extract the corpus byte-class population
    make crosscheck          # C DP vs Python DP over a population
    make proptest            # deliverable (4): the composition property test
    make bench               # ns/char — REFUSES unless load1 < 0.5

`make all-sweeps` runs the sizing/verification arms in the order the memo
reports them. `CC` defaults to `gcc-16` (this box's real gcc; bare `cc`/`gcc`
is Apple clang, and `size -m` parsing assumes Mach-O either way).

**The Makefile spells that default `ifeq ($(origin CC),default)`, not
`CC ?= gcc-16`.** `?=` cannot work here: make defines `CC` itself, so the
assignment never fires and every target silently builds with Apple clang.
This was caught when `make discover` produced a clang binary *after* every
measurement in the memo had been taken with `gcc-16` invoked directly — the
same defect `docs/dev/lanes/santriage_report.md` records for
`scripts/battery.sh`'s `san`/`lint` stages, reappearing in a new file. A
study whose numbers come from one compiler and whose `make` uses another is
not reproducible, however green it looks.

## What the pieces are

| file | role |
|---|---|
| `clsets.py` | the three POPULATIONS, parsed out of the tree's own generated data |
| `kit.py` | the per-section representation KIT + the exact two-level minimizer |
| `section.py` | the sectioning DP (Python) and the shell-out to the C one |
| `discover.c` | the SAME DP in C — deliverable (3)'s compile-time instrument |
| `emit.py` | composes one bespoke straight-line matcher from a sectioning |
| `sweep.py` | build + EXHAUSTIVELY VERIFY + size, one row per (set, policy) |
| `baseline.py` | what `build/pcrec` emits today for the same sets |
| `crosscheck.py` | the two DP implementations compared over a population |
| `proptest.py` | the provenance-blindness composition property test |
| `bench.py` | ns/char, house protocol (interleaved, load-gated, checksummed) |
| `extract_byteclasses.py` | byte classes parsed off EMITTED artifacts |

## Five things not to simplify away

**1. The populations are read from the tree's own generated tables, never
re-derived from the UCD.** `studies/form_char_twins` set this rule for a
reason: a set re-derived from source data can disagree with the set the
compiler actually builds, and then the study is measuring its own parser
instead of pcrec. `clsets.uprops()` parses `src/parse/uprops_tables.inc`;
`extract_byteclasses.py` parses emitted artifacts.

**2. `baseline.py` must pass `-e utf8`.** Under `byte` every property set is
clamped to Latin-1 and tiny, and a baseline taken that way understates
today's cost by two orders of magnitude. This is not hypothetical: it is
exactly the trap [K53-SELRETRY] §4 recorded, where a codegen census compiled
`\p` corpus lines with no encoding and concluded the `\p` family was not the
population it was looking for.

**3. The baseline is compared as OBJECT bytes, not emitted-source bytes.**
The kit is measured as `.text + .rodata` of its own `.o`, so the baseline is
compiled and sized the same way. Comparing the kit's object against pcrec's
772 KB of emitted *source* for `\p{L}` would flatter the kit by whatever the
comments weigh; the honest number is 227,409 object bytes, and it is still a
50x story.

**4. Verification is exhaustive, not sampled.** Every cell compares the kit
matcher against an independently constructed reference on all 1,114,112 code
points. The reference is deliberately the dumbest correct thing (a flat
binary search over the whole interval list) so that a disagreement can never
be both sides making the same mistake.

**5. `bench.py` REFUSES on a loaded box.** It does not caveat. The sizing and
verification arms are static properties and run any time; ns/char is not.

## The bug this study's own cross-check found

`section.py` prices `PAGE64` in O(k) *without materializing the table* — that
is what keeps discovery cheap enough to answer deliverable (3). The first
version of that price double-counted a 64-wide page shared by two consecutive
intervals, which suppressed the all-empty leaf and under-priced the form by 8
bytes on one section of `\p{L}`.

It was found by comparing the price the DP paid against the table the emitter
actually wrote, and it is worth stating as a rule rather than as a bug: **a
cost model that prices a form without building it is only safe if something
independently builds it and checks.** `make k53` does that on every cell.

The same pairing caught the `BSEARCH` op-count divergence between the C and
Python DPs (an integer floor `log2` against `math.log2`), which moved `\p{L}`
at the middle policy from 28 sections to 27. Both implementations were
self-consistent; only the comparison could see it.

## Box context (D35 spirit)

Every number in the memo was measured on the Mac dev box (M1, darwin 25.6.0),
`gcc-16`, `-O2 -std=gnu11`. `size -m` (Mach-O) is parsed for section bytes;
`sweep.obj_sizes` carries an ELF `size -A` arm for the Linux side but that
arm is UNEXERCISED — re-measure before citing any of this on `ubuntubudu`.
