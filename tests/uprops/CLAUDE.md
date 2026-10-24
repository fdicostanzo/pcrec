# tests/uprops — module `unicode-props`, the checks a `.rxt` file cannot make

[M5.0] stages 3 and 5. `make test-uprops` (the `byte` arm, part of
`make test`); `make test-uprops-utf8` (the whole code-point space, opt-in).

The module's ANSWERS live in two corpus files: `tests/utf8/
axis04_p_categories.rxt` — the D27-blinded corpus, 136 blocks / 462 cases,
promoted at stage 3 from the oracle answers its author carried in each block's
comment — and `tests/utf8/axis12_scripts.rxt`, stage 5's, whose expectations
are the 10.46 REFERENCE's own answers rather than this box's. This directory
is everything those corpora structurally cannot express.

## Files

- **run_uprops_tests.sh** — five sections, and the reason there are five is that each sees something none of the others can. §5 ([PF-DROP], D135, utf8 arm only) sweeps ...
- **uprops_oracle.c** — the libpcre2 side, through the shared binding (`tests/fuzz/pcre2_abi.h`, direct-linked since [ORACLE-LINK]/D98, 2026-09-09), so a clone without ...
- **uprops_sweep.c** — the pcrec side, compiled once per property against that property's own emitted artifact.
- **size_ladder_prefilter_drop.rxt** — [PF-DROP] (D135): the witness `(\p{Xwd})` under `-e utf8`, a VM hybrid refused at default axes before the size-cap ladder gained its ...
- **uprops_compare.py** — the comparator, and the ONE place the Unicode-version drift policy is written down.
- **uprops_ucdref.py** — [UPROP-MORE]: independent references for what libpcre2 cannot arbitrate. `names`/`ext` re-read `Blocks.txt` and `DerivedAge.txt` themselves and compare every Block/Age sweep exactly, plus structure (Age is a function and `age=NA` completes it; blocks plus `blk=NB` tile the space); `pyuni` cross-checks `Bidi_Mirrored` and `Bidi_Class` against python `unicodedata` 16.0.0 on assigned code points (SKIPS loudly on another python). Run as §6 of the script.
- **uprops_names.py** — [M5.0] stage 5: §2's PROMISE SIDE, re-derived from the vendored UCD and compared against the shipped table's rows in BOTH directions.

## What is NOT here

**Refusals.** Which module a diagnostic promises is `tests/reject/`'s, for
this tree's standing reason — a `perr` block asserts only that compilation
failed. The gate-open uprops wordings are pinned there (`reject_gated
unicode-props`, twelve rows).

**The name axis against a generated space.** That is PC-3's
(`tests/registry/pcre2_check.c`): the closed-gate shape differential, and
`check_gated_uprops_space`, which asserts pcrec never ACCEPTS a property name
libpcre2 rejects — since stage 5 by sweeping EVERY name pcrec's own table
holds (1,053 across the three namespaces) rather than a hand-written list, and
with a drift rule of its own, since Unicode ADDS scripts and an older oracle
genuinely does not have `\p{Kawi}`.

**The patterns that do not compile under `utf8` at default axes.** They are
`tests/known_fail/k53_uprops_oversize.rxt` and `docs/dev/known_issues.md` K53
— an engine issue (an OPTIONAL machine's bytes refusing patterns that compile
without it), not a `\p` one. Six at stage 3; stage 5 added four blocks and
the population is smaller than its own shape suggests — of 684 script
patterns measured at default axes, exactly two SETS refuse, and they are
`\p{Unknown}` under its four spellings.

Maintenance: update this file when a section is added or its argument changes;
re-measure the two arms' figures from a run rather than reading them here.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__uprops.md`.
