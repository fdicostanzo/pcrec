# tests/utf8 — the [M5.0] utf8-encoding corpus (D27 blinded, promoted)

Thirteen `.rxt` files, 524 blocks, authored BLIND (D27: denied `src/`,
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

## Files

- **landing_illformed.rxt** — the RECOVER row `landing`'s ill-formed cells (docs/design/start_landing.md §7.3 §6): four patterns that take `landing` with the ...
- **gen_landing_illformed.py** — its generator (builds a libpcre2 helper under build/gen_landing and writes the file FROM the oracle).
- **octal_wide.rxt** — K125 (lane langfix2): `\400`..`\777` are U+0100..U+01FF under utf8 (in a class, outside, the digit rule's octal reading, caseless); err 151 under byte (two `perr` controls). libpcre2 10.46 PCRE2_UTF-generated, no python arm.

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

- Also (one-line entries for these are in the history file): `axis01_encoded_length.rxt`, `axis01_encoded_length_byte.rxt`, `axis02_class_boundary_byte.rxt`, `axis03_invalid_utf8.rxt`, `axis03_invalid_utf8_byte.rxt`, `axis04_p_categories.rxt`, `axis05_p_refusals.rxt`, `axis06_caseless_fold.rxt`, `axis07_caseless_1ton.rxt`, `axis08_lookbehind_varwidth.rxt`, `axis09_nextpos_findall.rxt`, `axis10_surrogate_witness.rxt`, `axis11_startpos_boundary.rxt`, `axis12_scripts.rxt`, `axis13_ctx_illformed.rxt`, `fold.rxt`, `gen_wclass_illformed.py`, `hv_space.rxt`, `k73_startskip.rxt`, `run_startbnd_diff.sh`, `wclass_illformed.rxt`.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__utf8.md`.
