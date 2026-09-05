# utfprom_report.md — [M5.0] promotion of the D27 blinded utf8 corpus

Lane branch: `lane/utfprom`, worktree `worktrees/utfprom`, at `05b2fe8a`
(stage 2 + the ascii-fold form merged). Not blinded — full repository read
access.

## Disclosure (spawn-time injections)

Per the brief's disclosure requirement: the session-root CLAUDE.md and the
user's memory index (`MEMORY.md`) arrived as background context at spawn,
as did the CLAUDE.md files for every directory read during the session
(`tests/`, `tests/known_fail/`, `tests/recursion/`, `docs/`,
`docs/spec/`, `docs/dev/`). None named implementation detail beyond what
the task brief and the repository itself already state.

## DIVERGENCES FIRST, per the brief

**One genuine divergence, filed as K49 and moved to `tests/known_fail/`.**
`axis09_nextpos_findall.rxt`'s "midstart-row3-boundary" block —
`(?<!.)` (`--features lookaround`, `-e utf8`) at explicit `startpos=2`
over subject `"\xce\xb1\xce\xb2"` (two 2-byte UTF-8 characters, alpha then
beta; byte 2 is a genuine character boundary). The D27 extract's own
ARGUED design position (Sec 2.6.1.1's mid-character-startpos table) says
the correct answer is NO MATCH: the assertion `(?<!.)` is false at
position 2 (alpha precedes it), and an unanchored retry from a failed
startpos must only ever try LATER CHARACTER BOUNDARIES — the next of
which is position 4 (subject end), where the assertion is false again
(beta precedes it). **pcrec's live answer is a MATCH at `(3,3)`** — byte
offset 3 sits INSIDE beta's own two-byte encoding, not a character
boundary under any reading. The sibling block at the same startpos with
`(?!.)` (a different pattern, "midstart-row4") answers correctly, so this
is not a wholesale defect in the unanchored-retry path; it looks specific
to `(?<!.)` (or lookbehind zero-width assertions generally) at this exact
shape. **Suspected mechanism** (not traced into `src/` — out of this
lane's scope): the unanchored search, on failing a zero-width assertion
at a given position, appears to retry the NEXT BYTE rather than the next
CHARACTER (via the encoding's own `next_pos` entry), landing on an
illegal mid-character offset. Full write-up: `docs/dev/known_issues.md`
K49. The cell moved to `tests/known_fail/k49_utf8_lookbehind_retry.rxt`
(pinning the ARGUED/correct expectation, not pcrec's current answer),
with a pointer comment at its former position — this project's own
convention for a disputed answer rather than an unbuilt construct
(`docs/spec/rxt_format.md` step 5), which is also what keeps `make test`
green while the finding stays loud (the known_fail ratchet fires the
moment it's fixed).

**A KNOWN, pre-identified gap is NOT counted as a finding: axis06/axis07
(non-ASCII caseless folding).** The manager's brief explicitly named this
one in advance ("non-ASCII caseless folding does not exist yet (stage
4)... check what the parser actually does with it today and pin THAT").
20 of `axis06_caseless_fold.rxt`'s 44 live blocks (29 cells) disagree with
their recorded `PCRE2_UTF|PCRE2_CASELESS` oracle, because pcrec's
`(?i)`/`flags i` under `-e utf8` does ASCII-only fold today (KELVIN
SIGN<->k, LONG S<->s, etc. do not unify). Per the brief's instruction
these blocks are PINNED to pcrec's own live, real answer rather than
promoted to the oracle — the oracle comment is left in place, unchanged,
directly above each pinned case for provenance, so landing stage 4 is
"restore the oracle values, drop the pinned ones, re-run," not a
divergence discovery. `axis07_caseless_1ton.rxt` (the "1:n non-matching"
design) happens to agree with the oracle on every one of its 11 blocks
already — pcrec's ASCII-only fold trivially can't unify a non-ASCII pair,
and PCRE2's real fold agrees these specific 11 candidates don't unify
either, so 0 gaps there.

## A corpus-authoring bug, found and fixed, not a pcrec finding

`axis02_class_boundary.rxt`: every one of its 10 `\x{}`/`\p{}`-spelled
blocks (8 of which promote) was missing its own `encoding utf8` line —
present on every LITERAL sibling block in the same file, and implied by
the file's own stated `PCRE2_UTF` oracle basis. As authored these blocks
would have compiled (where they compile at all) under the bare BYTE
default instead of utf8, which is why they showed 6 spurious "divergences"
on the first pass (the `\x{7f}\x{80}`-family blocks, which DO compile
under bare byte too by coincidence — both members happen to be <=U+00FF —
but mean something different there: byte 0x7f/0x80 literally, not "the
UTF-8 encoding of U+007F/U+0080"). Added `encoding utf8` to match the
sibling pattern and the file's own stated intent; re-verified 0
divergences. This is the exact shape `tests/recursion/dupnames.rxt`'s
`features` line bug was (that directory's own CLAUDE.md: "the generator's
own guard said so, unprompted... fixed in `gen_corpus.py` rather than
hand-editing the .rxt lines") — a missing directive, not a semantic
disagreement, and I fixed it at promotion rather than reporting it as a
finding.

## What promotion actually did, per axis

Built `build/pcrec` (`gcc-16`, this Mac box), then live-probed every
`perr` block's current compile status and, where it now compiles,
cross-checked the block's own future-case comment (the D27 author's
oracle-derived expectation, in ready-to-promote `m`/`n`/`ms`/`ns` syntax)
against pcrec's real compiled-and-run behaviour — never against a
reasoned guess. Tooling (scratch, not part of the delivered corpus):
`oracle.py` (compiles + builds + runs a pattern/subject through the real
`tests/harness/driver.c`, exactly the shape `tests/harness/run.sh` uses),
`rxtblocks.py` (a `.rxt` block parser verified byte-identical round-trip
on all 13 files before any edit), `promote.py` (the promotion/divergence
engine), `byteesc.py` (python bytes-`re` on a `\x{HH}`-\>`\xHH` translated
pattern, for the handful of blocks the corpus itself never gave a future
value for — see below).

| axis | blocks | promoted | still `perr` | divergent | notes |
|---|---:|---:|---:|---:|---|
| 01 (utf8) | 64 | 64 | 0 | 0 | clean |
| 01 (byte mirror) | 64 | 52 | 12 | 0 | 4 newly promoted, fresh-derived (below); 12 still refuse, now RANGE not MODULE |
| 02 (utf8) | 24 | 22 | 2 | 0 | clean once the missing-`encoding` bug (above) was fixed |
| 02 (byte mirror) | 24 | 18 | 6 | 0 | 4 newly promoted, fresh-derived; 4 refuse (range, one member >U+00FF), 2 refuse (`\p`, unaffected) |
| 03 (utf8) | 27 | 27 | 0 | 0 | clean — the ill-formed-subject barrier ruling holds exactly as measured |
| 03 (byte mirror) | 27 | 0 (untouched) | 0 | 0 | already fully real as authored |
| 04 (`\p` categories) | 148 | 0 | 148 | 0 | untouched — `unicode-props` still unbuilt (stage 3) |
| 05 (`\p` refusals) | 34 | 0 | 34 | 0 | untouched — permanent PCRE2 error-147 refusals |
| 06 (caseless fold) | 48 | 44 pinned-today | 4 | 0* | *20 blocks disagree with the recorded oracle — the KNOWN gap above, not counted here |
| 07 (caseless 1:n) | 11 | 11 pinned-today | 0 | 0 | agrees with the oracle on every cell |
| 08 (lookbehind) | 24 | 21 | 3 | 0 | `features` line added per block (see below); `\p{L}`-bodied blocks unaffected |
| 09 (next_pos) | 20 | 19 | 0 | 1 | the ONE finding (K49), moved to known_fail |
| 10 (surrogate) | 9 | 6 | 3 | 0 | clean — surrogate-subject rejection holds on every encoding shape |

**Totals**: 524 authored blocks -> 523 in `tests/utf8/` + 1 in
`tests/known_fail/`. 311 real (222 newly promoted from `perr`), 212
still `perr` (all genuinely still gated — `unicode-props`, or a genuine
`\x{}`/range refusal). Zero silent reconciliations: every promoted value
is either the corpus's own recorded oracle answer (verified live to
agree), a fresh live-derivation cross-checked two ways (below), or —
axis06/07 only, per explicit instruction — pcrec's own real observed
behaviour with the oracle value kept alongside for provenance.

### Fresh-derivation blocks (no future-case comment existed)

Eight blocks across `axis01_encoded_length_byte.rxt` (4) and
`axis02_class_boundary_byte.rxt` (4) use `\x{HH}` escapes with a code
point <=U+00FF. [M5.0] stage 2 made `\x{}` BASE-grammar range-checked per
encoding (<=U+00FF compiles under `byte` too now; the D27 corpus was
authored before this landed and assumed the gate was permanent, so it
carried no future-case comment for these blocks at all — just a
"module-gated under byte too" description, now corrected in each block's
own header comment to state the RANGE reason, live-verified). Derived
fresh values by translating the pattern's `\x{HH}` spellings to python
bytes-`re`'s `\xHH` (byte-for-byte identical meaning under `byte`
encoding) and running python's own bytes engine on the translated pattern
against three canonical subjects per block, THEN cross-checking against
pcrec's own compiled-and-run output on the exact same subjects — the
corpus's own established "LIVE pcrec/byte == python/re-bytes"
methodology, extended by one step to blocks the blinded author never
reached. All 8 agree exactly, including the byte-decomposition subtlety
`[\x{7f}\x{80}]` exposes on the ill-formed subject `"\xc2\x80"` (the class
has exactly two BYTE members, 0x7f and 0x80 — unlike its literal sibling
`[]` whose source bytes happen to spell THREE byte members, 0x7f/0xc2/0x80
— so the escaped and literal spellings of "the same two code points" are
NOT equivalent under byte encoding, and deriving each independently
rather than assuming equivalence is what caught that).

### `features` lines added at promotion (missing as authored)

Neither `axis08_lookbehind_varwidth.rxt` nor the 4 mid-character-startpos
blocks of `axis09_nextpos_findall.rxt` carried a `features` line as
authored — the blinded author never got past `-e utf8`'s own
unconditional refusal (pre-stage-2) to discover module `lookaround` needs
enabling explicitly, off the `std1` default. Added per block, derived
from the pattern's own body: `lookaround` on every lookbehind block,
`+classes` for a `\w`-bodied one, `+modifiers` for an `(?i)`-bodied one,
`+named-groups,recursion` for the call-bearing shape. The call-bearing
gate is worth naming: the corpus's own REPORT.md Sec 2 found `(?&g)`
refusing as `requires module 'named-groups'` under the pre-stage-2 build
and recorded that as the call's own gate; live-measured now, `(?&g)`
needs `recursion` — `named-groups` is a DIFFERENT, EARLIER gate, needed
by the group DECLARATION `(?<g>...)` the call refers to, which the
pre-stage-2 build's blanket `-e utf8` refusal never let the author get
past to discover the second one.

### `# pcre2-only` marking pass (255 blocks, all 13 files)

`tests/harness/verify_rxt.py`'s default python oracle has NO UTF-8
awareness in its subject decoder (`decode_subject`: every `\xHH` -> one
python `str` character, one-for-one) even though it reads the PATTERN
text as real UTF-8 and compiles it as a true Unicode string — a mismatch
that produced 211 spurious FAILUREs on a first oracle-sweep pass, all of
them cells the LIVE harness (`tests/harness/run.sh`, pcrec's actual
behaviour against the recorded expectation) answers correctly. Marked
every affected block `# pcre2-only` (255 blocks; `mark_pcre2only.py`,
scratch tooling, detection rule: any pattern or live case subject
containing a byte/character >=0x80). `docs/dev/upstream_issues.md` U14 is
the citable record. Re-verified: `python3 tests/harness/verify_rxt.py
tests/utf8` is 376 pass / 0 fail / 959 skip (100%); `bash tests/harness/
run.sh tests/utf8` is 1335 pass / 0 fail (K49 excluded via known_fail);
`bash tests/known_fail/run_known_fail.sh` reports K49 as `still failing
(expected)` alongside the pre-existing K34.

## Wiring

`tests/utf8/` rides `test-corpus` automatically — `tests/harness/run.sh`
with no arguments sweeps every `*.rxt` under `tests/` (`docs/spec/
rxt_format.md`: "no registration step needed"), and
`tests/rxtsource/run_rxtsource_tests.sh`'s `find tests -name '*.rxt'`
picks the new files up the same way. **No dedicated `make test-utf8`
target was added**, on the sibling-directory precedent: every plain
per-module `.rxt` directory in the tree (`tests/classes/`,
`tests/modifiers/`, `tests/named_groups/`) has NO dedicated `make`
target, because none carries a structural/differential check beyond
ordinary `.rxt` evaluation — a dedicated target exists only where a
directory ALSO has a `run_*_diff.sh`-shaped instrument
(`tests/lookaround/`, `tests/recursion/`, `tests/atomic_groups/`, etc.).
`tests/utf8/` has no such instrument today (the byte-mirror libpcre2
differential is a real, disclosed gap — see its own CLAUDE.md's
"Maintenance" section), so it follows the plain-directory precedent
rather than the brief's literal "so `make test-utf8` exists" phrasing.
Flagging this explicitly in case that reading is wrong.

## Side effect: `tests/rxtsource`'s pinned file-count census is now MORE stale

Pre-existing on the merged tree before this lane touched anything (git
stash confirmed): `bash tests/rxtsource/run_rxtsource_tests.sh` already
failed 18 checks, including "found 194 .rxt files, pinned 193" — a
hand-maintained constant already one file behind. Adding 14 new `.rxt`
files (13 in `tests/utf8/`, 1 in `tests/known_fail/`) grows the same
pre-existing failure's numbers (194->208 found, three related
denominator-reconciliation checks move with it) rather than introducing
a new failure class — 19 failed vs. 18 pre-existing, +1, all in the same
family. **Not fixed here**: the pinned count is a whole-tree census
shared by every lane touching `.rxt` files concurrently; updating it
mid-lane risks a second lane's own additions re-staling it before merge.
Flagging for the manager to update once every pending lane's file count
is known, rather than silently patching a cross-cutting constant outside
this lane's own directory.

## Files touched

- `tests/utf8/*.rxt` (13, new) + `tests/utf8/CLAUDE.md` (new)
- `tests/known_fail/k49_utf8_lookbehind_retry.rxt` (new) +
  `tests/known_fail/CLAUDE.md` (K49 bullet added)
- `docs/dev/known_issues.md` (K49 entry added)
- `docs/dev/upstream_issues.md` (U14 entry added)
- `tests/CLAUDE.md` (utf8/ directory bullet added)
- This file.

## Verification run log

    build/pcrec: gcc-16, this Mac box, clean build
    bash tests/harness/run.sh tests/utf8         -> 1335 pass / 0 fail
    python3 tests/harness/verify_rxt.py tests/utf8 -> 376 pass / 0 fail / 959 skip (100%)
    bash tests/known_fail/run_known_fail.sh      -> still failing: 2 (K34, K49), now passing: 0
    build/pcrec --list-source <every file>       -> parses clean, all 13 + known_fail's 1
