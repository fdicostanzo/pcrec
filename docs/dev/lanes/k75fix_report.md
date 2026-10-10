# k75fix — K75 FIXED, ruling M1 (2026-09-30, lane k75fix, sonnet)

Branch `lane/k75fix` from main `64298135`. D132 item 1: after a NON-EMPTY match
the spec find-all loop resumes at `<prefix>_next_pos(s, n, end - 1)` instead of
`end`. **Protocol and contract only: nothing under `src/`, `cli/` or `lib/`
changed, no emitted byte moves, no abi event.** Not pushed, not merged.

## Sites changed (found by grep, not from the measurement doc's list alone)

Spec / docs (D80):
- `docs/spec/match_api.md` §3.1 (§3.1.3; boundary rule is §9.2) — the loop's non-empty arm; a paragraph stating
  the alignment is a no-op on a well-formed subject and why the subtraction
  cannot underflow; the three-sentence boundary rule (a caller's `startpos`
  must be a boundary and is refused otherwise; positions the loop computes are
  always boundaries; a continuation byte is never a match start); the
  empty-arm paragraph gains the non-empty companion clause; the startpos
  bullet on `<prefix>_next_pos` now says both arms; the "coded exactly as
  written" verification sentence says what the byte-encoded pairs do and do not
  cover and points at the ill-formed witnesses.
- `docs/spec/rxt_format.md` `mc` — the counting rule cites the aligned resume,
  and a `[K75]` paragraph states the skip and the three witness counts.
- `docs/spec/CLAUDE.md`, `docs/guide/using-the-matcher-from-c.md` (one
  sentence; the guide points, it does not restate).

Find-all loops (every transcription of §3.1 under `tests/`; `studies/` and
`docs/dev/**` loops are historical/unbuilt and were left alone):
`tests/harness/driver.c` (the `mc` C leg), `tests/harness/verify_rxt.py`
`_findall_protocol` (the `mc` python leg), `tests/encseam/findall_driver.c`
(+ a comment in `findall_oracle.py`, unchanged in behaviour: byte encoding),
`tests/assertions/gstart_findall.c`, `tests/codegen/entry_shape_driver.c`,
`tests/backrefs/run_backref_diff.sh` §6. The last four are byte-encoded, where
`next_pos(end - 1) == end`, so they are answer-identical by construction and
are aligned only so no transcription lags the spec.

Witnesses: six new cells in `tests/rxtsource/fixtures/mc_illformed_utf8.rxtin`
(pin in `run_rxtsource_tests.sh`: run.sh `cases passed: 2 -> 8`, verify_rxt.py
`PASS=2 -> 8`). This fixture is the one place both `mc` legs are scored against
independently derived counts.

Sabotage: **S407** (C leg: `driver.c` arm back to the raw end) and **S408**
(python leg: the skip dropped), both on the `rxtsource` arm, both with a
`SAB_REACH_POP` floor on the fixture's stray-byte cells; described in
`tests/mech/CLAUDE.md`. Highest S-id on main was S406.

`docs/dev/known_issues.md` K75 -> FIXED; `docs/dev/lanes/CLAUDE.md` index.
plan.md has no row naming K75 (grepped), so no plan edit.

## Oracle evidence

libpcre2 **10.48** (Homebrew; CI's 10.46 was not re-run for this lane, and the
measurement doc already notes the offset-0 cells agree across the two).
`PCRE2_UTF|PCRE2_MATCH_INVALID_UTF`, find-all loop = the pr3 loop the
measurement used (non-empty: `p = end`, the library advances; empty:
`p = start + 1` then skip `0x80-0xBF`). Scratch program in
`/tmp/claude-k75fix/or.c` (not committed; ~20 lines, the measurement's `ff.c`
with a hex-subject argv). Counts (subject in hex):

| pattern | subject | count | spans |
|---|---|---|---|
| `a` | `61 80 61` | 2 | (0,1)(2,3) |
| `a` | `61 80 80 61` | 2 | (0,1)(3,4) |
| `a` | `61 c3 a9 80 61` | 2 | (0,1)(4,5) |
| `.` | `61 80 61` | 2 | (0,1)(2,3) |
| `a|` | `61 80 61` | 3 | (0,1)(2,3)(3,3) |
| `a|` | `61 80` | 2 | (0,1)(2,2) |
| `x?` | `61 80 80 80` | 2 | (0,0)(4,4) (pre-existing cell) |

Pre-change loop on the same fixture: `run.sh` **3 passed / 5 failed** (the C
loop hands K50 a stray and gives up), post-change 8/0.

Re-verification of the measurement's differential with the shipped-binary
build of this branch (19,608 subjects over `61 62 80 c3 a9 e3 ff`, lengths
0..5, libpcre2 10.48 as reference; scratch copy of `k75m_evidence/fall.py`
pointed at this worktree's `build/pcrec`; `cur` = unaligned loop, `m1` = the
aligned loop now specified):

```
pattern         n cur!=pcre2  m1!=pcre2
a           19608        572          0
.           19608       2408          0
a|          19608       2980          0
x*          19608          0          0
(?<!a)b     19608        492          0
(?<=a)b     19608          2          0
```

The `\B`, `\b`, `(?<=.)x*` residuals of the measurement are K74's family (the
empty match PCRE2 reports at the end of a valid chunk) and are unchanged by
this fix, as the ruling says.

## Findings

- Leg C (python) cannot be the second reader for multi-byte characters: subjects
  are decoded one character per byte, so `.` would count `c3 a9` twice. The
  fixture's subjects are therefore ASCII + stray continuation bytes, with one
  multi-byte cell for `a` only (where `a` cannot see the difference). This is a
  pre-existing property of the leg, not new.
- The python plant (S408) does NOT move the `a` cells (python's `re` steps over
  a non-`a` stray with no help), only `.` and `a|`; the C plant (S407) moves the
  `a` cells too (K50 refusal, count lost). So the two rows are not redundant.
- `make test-spec` fails here for an environmental reason unrelated to this
  change: `tests/fuzz/pcre2_abi.h` cannot find `pcre2.h` in that target's
  compile (13 of 14 checks). It is not part of `make test` (Makefile comment).
  Not investigated further.

## Validation (Mac, gcc-16; logs in `/tmp/claude-k75fix/`, verdict = make's `*** [test-X] Error` lines)

No `*** [test-X] Error` line in any of the following except `test-spec`
(below). All run against this branch's tip with `CC=gcc-16`; chain script and
logs in the scratchpad (`/tmp/claude-k75fix/chain.log`, `<name>.log`).

| stage | command | verdict |
|---|---|---|
| strict | `make strict CC=gcc-16` | rc 0, "whole tree compiles clean with -Werror -Wshadow" |
| encseam | `make test-encseam` | rc 0 (`findall_driver.c` aligned arm, byte encoding, identical answers) |
| rxtsource | `make test-rxtsource` | rc 0, `checks failed: 0`; the mc/ill-formed-utf8 block PASSes on all eight cells (run.sh `cases passed: 8`, verify_rxt.py `PASS=8 FAIL=0`) |
| registry | `make test-registry` | rc 0, every `checks failed: 0` |
| backrefs | `make test-backrefs` | rc 0 (§6 find-all runs against libpcre2 with the aligned arm) |
| assertions | `make test-assertions` | rc 0 (incl. `gstart_findall.c`) |
| entry shape | `bash tests/codegen/run_entry_shape_identity.sh` | rc 0 |
| S407 | `tests/mech/run_sabotage_matrix.sh S407` solo | **DETECTED**, `rxtsource:1fail/270pass`, reach floor 7 (want >= 6) |
| S408 | `tests/mech/run_sabotage_matrix.sh S408` solo | **DETECTED**, `rxtsource:1fail/270pass`, reach floor 7 |
| test-spec | `make test-spec` | rc 2, 13 of 14 checks fail to COMPILE: `tests/fuzz/pcre2_abi.h: pcre2.h: No such file` (environmental, off `make test`; not attributable to this change, not A/B-ed against the branch point) |

NOT run (per the brief): the full `make test`, `make test-codegen`'s abi-scaffolding readers
(nothing emitted moved; the loop drivers under `tests/codegen/` that read the
spec text were exercised only via `run_entry_shape_identity.sh`), the
`test-axes` sweep, the Linux/10.46 confirmation. `make test-corpus` was not
run: no corpus file changed. The Linux full `make test` is the manager's to
schedule; the census pins that move with a fixture line (rxtsource C1-C3) did
not move because the fixture is a `.rxtin` under `tests/rxtsource/fixtures/`,
outside the corpus census (`test-rxtsource` above is green).

## Drafted bench I-note (NOT sent; the manager relays)

> **I-note for pcrec-bench — find-all alignment under `-e utf8` (K75, D132).**
> pcrec's spec find-all loop (match_api.md §3.1) now resumes after a
> NON-EMPTY match at `<prefix>_next_pos(s, n, end - 1)`, i.e. `pos = end`
> followed by "while `pos < n` and `s[pos]` is in `0x80..0xBF`: `pos += 1`".
> Your formula `pos = max(end, pos + 1)` needs the same alignment for any
> `-e utf8` cell whose SUBJECT MAY BE ILL-FORMED: without it, a match that
> ends immediately before a stray continuation byte leaves the next search on
> a byte pcrec's entries refuse (`PCREC_ERR_STARTPOS`, K50), and the count
> stops short (libpcre2 with `PCRE2_MATCH_INVALID_UTF` reports 2 for `a` over
> `61 80 61`; the unaligned loop reported 1). On a well-formed subject the
> alignment is a no-op (a match end is a boundary), so no existing
> well-formed count moves. The EMPTY-match arm is unchanged
> (`pos = start + 1`, then the same skip); separately, `max(end, pos + 1)`
> double-counts an empty match found beyond the scan position
> (`w23design_report.md`: `(?=a)` on `"xax"` is 1, not 2), which this note does
> not touch. Positions a CALLER passes to an entry must still be boundaries;
> only the loop's own computed positions are aligned. Evidence: pcrec
> `docs/dev/k75_measurement.md`, `docs/dev/lanes/k75fix_report.md`.
