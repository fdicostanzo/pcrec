# rxtnul — [DD-13b.W23] STEP 0: two silent-loss refusals in the .rxt parser

Lane `rxtnul` (sonnet tier), branch `lane/rxtnul`, chartered at `b9572c66`.
Scope: `src/parse/rxt_source.c` only, per the brief — the two refusals
pcrec-bench's `rxt_needs_v1.md` asked for
(`docs/design/dd13_format/bench_rxt_needs_v1.md` §1.9 M1/M5, §2.7's refusal
ask, acceptance checks B3/B4/C10).

## What changed

1. **NUL refusal** (`slurp_lines`, `src/parse/rxt_source.c`). Before this
   fix the whole-file buffer was split into NUL-terminated C strings with
   no prior scan, so `pattern ab<NUL>cd` silently parsed as `ab`, exit 0,
   no diagnostic (M1). Now the buffer is scanned for an embedded NUL byte
   BEFORE the line split, and the first one found is refused by name —
   the file, the 1-based line it falls on, and that it is a NUL byte.

2. **Duplicate `description` (pattern block)**. Before this fix a second
   `description` line inside one pattern block silently overwrote the
   first (`block->description` is a single field) (M5). Now the second
   one is refused, naming the block's earlier line — the same discipline
   the existing duplicate-block-name refusal uses.

3. **Duplicate `description` (file head)** — the brief's third ask
   ("investigate the HEAD scope too... verify what the head parser does
   today and cover it"). Measured first: the head's `description` was
   NOT the same silent-overwrite shape — each occurrence pushes its own
   `RXT_DECL_DESCRIPTION` row (in file order, like every other head
   declaration), so a second head-level description never lost data, it
   just became a second row with nothing consuming it as "the" file
   description. `docs/spec/rxt_format.md` calls the field "a
   machine-readable prose FIELD" (singular), so a second one is refused
   the same way, for consistency, even though the underlying mechanism
   differs from the block case.

No `abi` bump: this is parse-time refusal only, no emitted-scaffolding
change. Verified `--list-source`'s output is unchanged on the existing
corpus (`tests/rxtsource`'s own census: 210 files / 3936 blocks / 28943
expectation lines, identical before and after).

`docs/spec/rxt_format.md` gets three hunks in the same change (D80): the
head declaration table's `description` row, the block-scoped
`description` bullet, and the `pattern <regex>` bullet.

## Exact refusal diagnostics (verbatim)

```
pcrec: <file>:<N>: embedded NUL byte in .rxt source file

pcrec: <file>:<N>: a pattern block has one 'description' (already given on line <M>)

pcrec: <file>:<N>: a file has one 'description' (already given on line <M>)
```

## Test counts before/after

`make test-rxtsource` (`tests/rxtsource/run_rxtsource_tests.sh`):

| | before | after |
|---|---|---|
| checks passed | 119 | 125 |
| checks recorded | 1 | 1 |
| checks failed | 0 | 0 |
| census (unchanged either way) | 210 files / 3936 blocks / 28943 lines | same |

The +6 are the three new refusals' `check_refusal` calls plus their three
accept-control assertions (see below).

## Suite results

- **`make strict`** (warnings-as-errors, opt-in gate): **GREEN** —
  `strict: whole tree compiles clean with -Werror -Wshadow`.
- **`make test-rxtsource`**: **GREEN**, 125/125 (see above), run directly
  (foreground, ~a few seconds — this section is deliberately cheap, no
  corpus compiles).
- **`make test`** (the full suite, the merge/close standard): **LAUNCHED
  IN BACKGROUND, RESULT OWED.** Per BOILERPLATE's DO-THEN-FINISH rule this
  run is the last thing this lane does — a full `make test` on this box
  runs well past the ~4-minute poll threshold (the Linux reference
  measured ~10:32 wall at `-j12`; this Mac's gcc is faster per-compile but
  the suite is still minutes, not seconds). Command:
  `make test CC=gcc-16`, backgrounded via `nohup ... > build/rxtnul_test.log
  2>&1 &` from the worktree root at commit `d4576c48`. **Log:**
  `/Users/fdicostanzo/pcrec/worktrees/rxtnul/build/rxtnul_test.log`.
  **Completion signature**: the trailer `tests/lib/test_trailer.sh` prints
  at the end, `sections ran: N/M` (naming any section that did not run),
  preceded by each section's own PASS/FAIL summary. A fresh agent or the
  manager should read that log's tail for the trailer line and the overall
  exit code before treating this delivery as fully validated.
  Risk assessment for why this is expected clean: the change touches only
  `src/parse/rxt_source.c`'s head/body parse (no `src/ir/`, `src/opt/`,
  `src/gen/` touched, no `abi` bump), the shipped 210-file corpus has zero
  NUL bytes and zero blocks with more than one `description` line
  (confirmed by `test-rxtsource`'s own census + the targeted rxtsource
  suite reading every corpus file through all three parsers with 0
  failures), and the two new code paths are refusal-only additions with no
  change to any accepted output.

## The two probe transcripts asked for in the brief

### NUL fixture refused / the same file NUL-free accepted

```
$ build/pcrec --list-source /tmp/nul.rxt      # pattern ab<NUL>cd
pcrec: /tmp/nul.rxt:2: embedded NUL byte in .rxt source file
(exit 1)

$ build/pcrec --list-source /tmp/ok.rxt       # pattern abcd (no NUL)
# pcrec --list-source: the .rxt SOURCE file AS WRITTEN (DD-13b W1).
...
target	1	rx	one
pattern	2	one		abcd
(exit 0)
```

This is exactly what `tests/rxtsource/fixtures/nul_byte.rxtin` (the
refusal) and its derived NUL-free twin (`tr -d '\000' < fixture`, the
accept control) assert in `run_rxtsource_tests.sh`'s new `sem22` block —
the twin is built FROM the refusing fixture at test time, so the two are
byte-identical except for the one byte under test.

### Duplicate-description fixture refused / single accepted

```
$ build/pcrec --list-source /tmp/dup_desc.rxt
pcrec: /tmp/dup_desc.rxt:5: a pattern block has one 'description' (already given on line 4)
(exit 1)

$ build/pcrec --list-source /tmp/single_desc.rxt
# ... one row, pattern block's description column = "first one"
(exit 0)
```

Same shape at the head: `dup_head_description.rxtin` refuses naming line
1 as the earlier occurrence; `head_basic.rxtin` (which already carries
exactly one head-level description and is exercised by many other checks
in this suite) is the accept control, asserted explicitly in the new
`sem25` block.

## What is NOT fixed, named rather than left to be discovered

Legs B (`tests/harness/run.sh`'s arm chain) and C
(`tests/harness/verify_rxt.py`) do **not** detect either shape today —
measured directly on headless fixtures: a NUL byte is silently DROPPED by
bash's own `read` (leg B) and silently REPLACED with a space by leg C's
decoder; a duplicate block-level `description` is silently resolved
LAST-WINS by both, the exact pre-fix pcrec behaviour. This is unlike the
existing duplicate-block-name refusal, which both legs already detect
independently — so `dup_block_name.rxtin` uses `check_refusal_all3` and
all three of this lane's new fixtures deliberately use the single-leg
`check_refusal` instead, with the asymmetry stated in both
`tests/rxtsource/run_rxtsource_tests.sh`'s comments and
`tests/rxtsource/CLAUDE.md`'s new section. Fixing legs B/C is out of this
lane's scope (`src/parse/rxt_source.c` only, per the brief) and is a
plausible follow-on if the manager wants three-way parity here too.

## Files changed

- `src/parse/rxt_source.c` — the two refusals (`slurp_lines`'s NUL scan;
  `block_desc_line`-tracked block-level duplicate; the head-level
  duplicate-row check).
- `docs/spec/rxt_format.md` — three D80 hunks (head `description` row,
  block `description` bullet, `pattern <regex>` bullet).
- `tests/rxtsource/run_rxtsource_tests.sh` — `sem22`/`sem24`/`sem25`
  blocks.
- `tests/rxtsource/fixtures/nul_byte.rxtin`,
  `dup_description.rxtin`, `single_description.rxtin`,
  `dup_head_description.rxtin` — new fixtures (kept `.rxtin` so they
  never join the corpus or move its census, per this directory's
  standing convention).
- `tests/rxtsource/CLAUDE.md` — new section documenting the lane's
  fixtures and the leg A-only scope note.

## Handback

Committed at `d4576c48` on `lane/rxtnul`. `make strict` and the targeted
`make test-rxtsource` are both green with numbers above; `make test` is
running in the background and its result is OWED — see the log path and
completion signature above. Do not merge without reading that log's
trailer line first.
