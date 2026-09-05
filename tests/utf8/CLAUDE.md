# tests/utf8 — the [M5.0] utf8-encoding corpus (D27 blinded, promoted)

Thirteen `.rxt` files, 523 blocks, authored BLIND (D27: denied `src/`,
`tests/`, everything beyond `docs/design/utf8_d27_extract.md`) against the
PRE-stage-2 tree by cell `utf8corpus`, then PROMOTED against the merged
[M5.0] stage 2 tree by lane `utfprom` (2026-09-05). No `.rxt` directive
exists for this corpus's own oracle rule beyond what `tests/harness/run.sh`
already reads — it rides `test-corpus` exactly like every other per-module
directory (`tests/classes/`, `tests/modifiers/`, `tests/named_groups/`): no
dedicated `make test-utf8` target, because none of these files carries a
structural/differential check today (unlike `tests/lookaround/` or
`tests/recursion/`, which pair their `.rxt` corpus with a `run_*_diff.sh`).
A byte-mirror libpcre2/pcrec-under-utf8 differential (the natural next
instrument, on the shape `tests/atomic_groups/run_atomic_diff.sh`
established) is a real gap this corpus's own author flagged (REPORT.md
§7 item 1) and this promotion did not build — filed as open work, not
invented as harness syntax that doesn't exist.

## Provenance

- **Author**: D27-blinded cell `utf8corpus` (`worktrees/utf8corpus-cell/`),
  2026-09-05. `d27/REPORT.md` there is the full authoring record: sizing
  vs. the extract's own table, the byte-decomposition finding, the oracle
  drift (libpcre2 10.37 on this cell, not the project's 10.46 reference —
  re-verification against 10.46 owed on the Linux slot, per the manager's
  brief), and the independent checker (`d27_scratch/check_rxt.py`, 5/5
  planted corruptions caught).
- **Promoter**: lane `utfprom`, NOT blinded, against `05b2fe8a` (stage 2 +
  the ascii-fold form merged). `docs/dev/lanes/utfprom_report.md` is the
  promotion record: per-axis promoted/still-perr/divergent counts, the one
  genuine divergence (moved to `tests/known_fail/`, below), the corpus-bug
  fix applied at promotion (a missing `encoding utf8` line on 8 of
  `axis02_class_boundary.rxt`'s blocks), and the `# pcre2-only` marking
  pass this directory needed that no other per-module directory has
  needed yet.
- **10.46 re-verification**: still owed (memory `pcrec-cross-platform-
  verification`: this Mac box's libpcre2 is 10.37; 10.46 verification
  happens on the Linux slot). Every oracle-driven expectation in this
  corpus traces to 10.37 through the author's own drift-validation sweep
  (REPORT.md §3), not to 10.46 directly.

## Oracle rule — the SECOND directory in the tree with its own

`tests/assertions/` is the one other directory whose oracle rule differs
from the project default (python3 `re`), for a measured reason stated in
its own CLAUDE.md. This directory is the second, for a DIFFERENT measured
reason: **`tests/harness/verify_rxt.py`'s subject decoder
(`decode_subject`) is byte-oriented, not UTF-8-aware** — every `\xHH`
escape becomes one python `str` character one-for-one, while the PATTERN
text is read as real UTF-8 and compiled as a true Unicode string. Under
`encoding utf8` (and, it turns out, under `encoding byte` too, whenever a
LITERAL multi-byte character sits in the pattern source) a multi-byte
UTF-8 sequence in either the pattern or a subject therefore compiles or
matches as the WRONG NUMBER of "characters" under python — not because the
construct is unsupported (the usual `# pcre2-only` reason elsewhere in the
tree) but because the shared harness's own default oracle has no notion of
character boundaries at all. MEASURED at promotion: 211 spurious FAILUREs
under the default python sweep, on cells the LIVE harness
(`tests/harness/run.sh`, the real oracle) answers correctly. Every
affected block carries `# pcre2-only`, and `python3 tests/harness/
verify_rxt.py tests/utf8` is 100% PASS on what's left (376 pass / 0 fail /
959 skip) — see `docs/dev/upstream_issues.md` for the citable record.
`tests/harness/run.sh` (the LIVE oracle, pcrec's actual compiled behaviour
against each block's recorded expectation) is unaffected by any of this
and is what every promoted block's real correctness rests on.

## Files

Each `axis<NN>_*.rxt` corresponds one-to-one to a section of
`docs/design/utf8_d27_extract.md` cited in the file's own header; the
`_byte.rxt` siblings (axes 1-3 only) are the `encoding byte` MIRROR arm —
see axis 1's own header for why a byte-mirror exists and what it measures
(a literal multi-byte sequence matches identically to a byte-literal
reading; a class/quantifier/range/alternation wrapping one is
BYTE-DECOMPOSED, matching any of its individual bytes independently — the
whole reason the utf8 encoding module needs to exist).

| file | blocks | perr | real | notes |
|---|---:|---:|---:|---|
| axis01_encoded_length.rxt | 64 | 0 | 64 | promoted clean |
| axis01_encoded_length_byte.rxt | 64 | 12 | 52 | 4 newly promoted (`\x{}`<=U+00FF); 12 still refuse, now a RANGE error not a module error |
| axis02_class_boundary.rxt | 24 | 2 | 22 | promoted; corpus bug fixed (8 blocks were missing `encoding utf8`) |
| axis02_class_boundary_byte.rxt | 24 | 6 | 18 | 4 newly promoted; 4 still refuse (range), 2 still refuse (`\p`, unaffected) |
| axis03_invalid_utf8.rxt | 27 | 0 | 27 | promoted clean |
| axis03_invalid_utf8_byte.rxt | 27 | 0 | 27 | untouched (already fully real as authored) |
| axis04_p_categories.rxt | 148 | 148 | 0 | untouched (`\p`/`\P`, module `unicode-props`, stage 3) |
| axis05_p_refusals.rxt | 34 | 34 | 0 | untouched (permanent PCRE2 error-147 refusals) |
| axis06_caseless_fold.rxt | 48 | 4 | 44 | PINNED TO TODAY'S BEHAVIOUR, not promoted to the oracle — see below |
| axis07_caseless_1ton.rxt | 11 | 0 | 11 | pinned to today's behaviour; agrees with the oracle on every cell |
| axis08_lookbehind_varwidth.rxt | 24 | 3 | 21 | promoted; `features` line added per block (missing as authored) |
| axis09_nextpos_findall.rxt | 19 | 0 | 19 | promoted; 1 block (of the original 20) moved to `known_fail` — see below |
| axis10_surrogate_witness.rxt | 9 | 3 | 6 | promoted clean |

**523 blocks here** (524 authored minus the 1 moved to `known_fail`), 311
real / 212 `perr`. Full per-axis reasoning, including every `features`/
`encoding` line added at promotion and why, is each file's own header
comment plus `docs/dev/lanes/utfprom_report.md`.

## The one genuine divergence: K49

`axis09_nextpos_findall.rxt`'s "midstart-row3-boundary" block
(`(?<!.)` at startpos=2 over a subject whose byte 2 is a real character
boundary) disagreed with its ARGUED expectation: pcrec answers a match at
`(3,3)`, an illegal mid-character byte offset, where the design position
says no match. Filed as `docs/dev/known_issues.md` K49 and moved to
`tests/known_fail/k49_utf8_lookbehind_retry.rxt` per
`docs/spec/rxt_format.md`'s own rule ("a cell whose correct answer is
DISPUTED, not merely unbuilt, is not a `perr` case... move it to
`tests/known_fail/`") — this is a possible stage-2 bug the blinded corpus
found, not a construct that's merely unbuilt, and moving it keeps `make
test` green while keeping the finding loud (the ratchet fires the moment
it's fixed). A pointer comment sits at the block's former position.

## The known, pre-identified gap: axis06/axis07 (non-ASCII caseless folding)

Per the manager's explicit instruction at promotion time: `axis06_
caseless_fold.rxt` and `axis07_caseless_1ton.rxt` are PINNED TO TODAY'S
REAL BEHAVIOUR, not promoted to the PCRE2_UTF|PCRE2_CASELESS oracle their
own future-case comments (left in place, unchanged, for provenance)
record. `(?i)`/`flags i` under `-e utf8` does ASCII-only fold today
(stage 4, non-ASCII caseless folding, has not landed) — 20 of axis06's 44
live blocks (29 cells) disagree with the recorded oracle for exactly that
reason, and are NOT filed as findings: landing stage 4 is "restore the
oracle values from the comments above, drop the ASCII-fold values,
re-run," the same mechanical shape `tests/recursion/`'s `wave=` argument
uses for an unbuilt module. axis07 (11 blocks, the "1:n non-matching"
design) happens to agree with the oracle on every cell already, for its
own checked reason — see that file's header.

## Maintenance

Landing module `unicode-props` (stage 3): axis04, axis05, and the 6
still-perr `\p{...}`-bodied blocks scattered through axis02/axis08/axis10
promote the same way this lane promoted everything else — re-derive
compile status, replace `perr` with the block's own future-case comment,
re-run `bash tests/harness/run.sh tests/utf8`, watch for divergences.

Landing stage 4 (non-ASCII caseless folding): axis06/axis07 promote by
restoring the PCRE2_UTF|PCRE2_CASELESS comment values in place of the
ASCII-fold-pinned ones currently live; re-run and expect 0 divergences
per the file headers' own reasoning, or a fifth finding if that
expectation is wrong.

Building the byte-mirror libpcre2 differential (REPORT.md's own open
item 1, axes 6/7/9/10 currently have no mirror file at all): follow
`tests/atomic_groups/run_atomic_diff.sh`'s shape, not a new one.
