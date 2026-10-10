# K75 measurement — what PCRE2 does at a continuation-byte start offset

Lane k75m (2026-09-30, measurement only, nothing under `src/`/`tests/`/
`docs/spec/`). Oracle: libpcre2 **10.48** (Homebrew), the local one. pcrec:
`lane/k73utf` (`bd1be543`, K73's fix, abi 47), built in `worktrees/k75m`.
Evidence and drivers: `docs/dev/lanes/k75m_evidence/`. Every PCRE2 cell was
run with `PCRE2_UTF` alone ("U") and with `PCRE2_UTF|PCRE2_MATCH_INVALID_UTF`
("I"), each unanchored and with `PCRE2_ANCHORED` ("UA", "IA"). pcrec cells are
`<prefix>_search` and `<prefix>_match` (`-e utf8 --features all`).

## Population

9 patterns: `a` (non-empty), `.`, `x*` (empty-matchable), `\B`, `(?<!a)`,
and four lookbehinds (`(?<=a)x*`, `(?<=a).`, `(?<=é)x*`, `(?<=.)x*`). 16
subjects, every startoffset 0..n, 3,942 cells. Each continuation-byte offset
is classified from the subject alone:

- **A**: inside a WELL-FORMED sequence (`c3 a9 78` at 1; `e2 82 ac 78` at 1, 2;
  `f0 9f 98 80 78` at 1..3; `c3 a9 80 61` at 1). 10 positions.
- **B**: a STRAY, claimed by no lead: `80` alone; after ASCII (`61 80`,
  `61 80 61`); after a complete sequence (`c3 a9 80 61`, `e2 82 ac 80 80 61`);
  runs (`61 80 80 80 62`); after a truncated lead and an ASCII byte (`e3 61 80`);
  the surplus continuation after an over-long claim (`e3 80 61 80`); after an
  invalid lead (`ff 80 61`, `c0 80 61`). 13 positions.
- **T**: a continuation claimed by a TRUNCATED lead (`e3 80 61` at 1; `f0 9f 98 61`
  at 1, 2; `e3 80 61 80` at 1). 4 positions.

## The table (all nine patterns unless a pattern is named)

| kind | PCRE2 U / UA | PCRE2 I / IA | pcrec `_search` / `_match` (lane/k73utf) |
|---|---|---|---|
| A, 10 cells | `PCRE2_ERROR_BADUTFOFFSET` (-36), 10/10 | start advanced to the next non-continuation byte, then the pattern runs from there: `.` `x*` `(?<!a)` 10/10 answer at the moved start; `a` 4 match later / 6 nomatch; `\B` 10/10 nomatch | `PCREC_ERR_STARTPOS`, 10/10, both entries |
| B, 13 cells | -36 (12), -22 (1: offset 0 of `80`, the byte is illegal as a first byte) | advanced exactly as for A: `x*` 13/13 answer at the moved start; `.` 9 moved / 4 nomatch (end of subject); `a` 6 / 7 | `PCREC_ERR_STARTPOS` 12/13; the 13th is offset 0 (K73: `_search` moves, `_match` answers nomatch) |
| T, 4 cells | -36, 4/4 | advanced exactly as for A and B, 4/4 (`x*` `.` `a` `(?<!a)`) | `PCREC_ERR_STARTPOS`, 4/4 |

Anchored ("IA") advances too: `a` on `61 80 61` from 1 answers (2,3) with
`PCRE2_ANCHORED`. pcrec's anchored contract reports only a match beginning at
`ctx->pos`, so its `_match` refuses at these offsets (a stated divergence,
match_api.md §9.2, `#startpos`).

Representative rows (PCRE2 I / pcrec search), the full grid is `raw.tsv`:

| pattern | subject (hex) | from | kind | PCRE2 I | pcrec |
|---|---|---|---|---|---|
| `x*` | `c3 a9 78` | 1 | A | (2,3): the match at the moved start 2 takes the `x` | REFUSED |
| `x*` | `61 80` | 1 | B | (2,2) | REFUSED |
| `a` | `61 80 61` | 1 | B | (2,3) | REFUSED |
| `a` | `e2 82 ac 80 80 61` | 3 | B | (5,6) | REFUSED |
| `a` | `e3 80 61` | 1 | T | (2,3) | REFUSED |
| `.` | `c3 a9 78` | 1 | A | (2,3) | REFUSED |
| `\B` | `61 80` | 1 | B | (2,2) | REFUSED |
| `(?<=.)x*` | `c3 a9 78` | 1 | A | (3,3), NOT (2,2) | REFUSED |

The last row is a second, independent fact: under `MATCH_INVALID_UTF` the
moved start is a CHUNK boundary, and a lookbehind cannot see behind it, on a
well-formed subject as much as an ill-formed one (`(?<=.)x*` finds nothing at
the moved offset 2 although `é` precedes it; IA answers nomatch). pcrec, whose
lookbehind reads the real bytes, would answer (2,2) if it moved. It does not
matter to K75 (the find-all differential below shows lookbehind patterns
agreeing), but it means "match PCRE2 at a moved start" is not free of
lookbehind semantics.

## The rule PCRE2 follows, in one sentence

**PCRE2 decides on the BYTE, not on the sequence: any startoffset whose byte is
`10xxxxxx` is `BADUTFOFFSET` without `MATCH_INVALID_UTF` and is advanced to the
next non-continuation byte with it, identically for a true mid-character
position (A), a stray (B) and a truncated sequence's continuation (T) — so
PCRE2 draws no A/B line, and the "principled line" K75 asks about is pcrec's to
invent, not PCRE2's to confirm.**

K50's refusal of kind A is a pcrec choice for which PCRE2 itself offers the
typed error only in the mode without `MATCH_INVALID_UTF` (the mode
`pcrec_startpos_guard_text`'s comment cites); under the mode K73 follows at
offset 0, PCRE2 advances at A too.

## Where K75 actually comes from

The explicit-startpos question is not where the lost match is. The lost match
is the spec find-all loop (match_api.md §3.1) handing the engine a stray
because the previous non-empty match ended on one. The alignment PCRE2 does
inside `pcre2_match` (advance the offset) can be done by the CALLER for free:
`<prefix>_next_pos(s, n, end - 1)` is exactly "skip from `end` over continuation
bytes" and equals `end` whenever `end` is a boundary (every match end on a
well-formed subject).

Differential, 19,608 subjects (every string of length 0..5 over
`61 62 80 c3 a9 e3 ff`) x 11 patterns, libpcre2 10.48 find-all with
`MATCH_INVALID_UTF` (pr3's loop) as the reference; "cur" = the loop as
specified today, "m1" = the same loop with `p = next_pos(s, n, end - 1)` after
a non-empty match:

| pattern | cur != PCRE2 | m1 != PCRE2 |
|---|---|---|
| `a` | 572 | 0 |
| `.` | 2,408 | 0 |
| `a|` | 2,980 | 0 |
| `(?<=a)b` | 2 | 0 |
| `(?<!a)b` | 492 | 0 |
| `x*`, `^a`, `b$` | 0 | 0 |
| `\B` | 9,260 | 9,260 |
| `\b` | 1,296 | 1,296 |
| `(?<=.)x*` | 5,008 | 5,008 |

m1 never turns an agreeing subject into a disagreeing one (0 cells with
cur == PCRE2, m1 != PCRE2), and it repairs every subject in five patterns.
The three residual patterns diverge identically under cur and m1 (m1 == cur on
every one of their divergent cells): they are the ill-formed-position family,
not K75 — pcrec's engine never attempts a match at a stray offset, so the
empty match PCRE2 reports at the end of a valid chunk (`\B`/`\b` on `61 80`,
`(?<=.)x*` on `61 80`) is not found (K74, the [UTF-VALID] design).

## The minimal pcrec change

**M1, protocol only (recommended).** Change the §3.1 loop's non-empty arm from
`p = caps[0][1]` to `p = <prefix>_next_pos(s, n, caps[0][1] - 1)`. No emitted
byte changes: no `abi` event, no identity re-pin. K50's refusal of an explicit
continuation-byte `startpos` is untouched for A and B and T alike (a caller
handing the engine a stray still gets `PCREC_ERR_STARTPOS`); the reason the
refusal can stay is that the loop no longer manufactures such a position. It
is a no-op on a well-formed subject (a match end is a boundary, so
`next_pos(end-1) == end`), so it cannot move any existing well-formed `mc`
count. Sites: `docs/spec/match_api.md` §3.1 (the loop and the empty-arm
sentence), `docs/spec/rxt_format.md` `mc` (line ~761), the driver behind
`tests/encseam/findall_cases.txt`, `mc_illformed_utf8.rxtin`'s expectations
(oracle: the same pr3 loop), and the bench's find-all formula (external:
`pos = max(end, pos+1)` must gain the same alignment; relay through the
manager). It is a spec/contract change, so D80 applies.

**M2, engine-side (only if an explicit stray startpos must be ANSWERED).**
Refuse only a continuation byte inside a well-formed sequence, advance for a
stray. This IS separable from K50's kind-A refusal, but not cheaply: the
current guard is one byte test (`(S[P] & 0xC0) != 0x80`), whereas "inside a
well-formed sequence" needs a backward scan of up to three bytes with the full
well-formedness rules (lead range, E0/ED/F0/F4 second-byte limits, sequence
fits before `n`), emitted in the four guard sites (`pcrec_startpos_guard_text`
callers in `emit_dfa.c` and `emit_vm.c`) plus a SEEK action at each; that is an
emitted-scaffolding change, an `abi` bump, an identity re-pin, and a fresh
decision for T (truncated-sequence continuations: A or B?) which PCRE2 gives no
guidance on. Because PCRE2 has no A/B line, M2's line would be pcrec-only and
its lookbehind semantics at the moved start would still differ (chunk blindness
above).

## Caveats

- Local libpcre2 is 10.48, not the 10.46 reference; the K73 evidence
  (`k73_witness_10.46.txt`) already agrees with these offset-0 cells, and the
  find-all reference loop here is the same one `k73_mc_findall_10.46.txt` used.
  The kind A/B/T table was NOT re-run on the 10.46 box (light probes only, and
  the result is a single uniform rule); worth one confirmation there before a
  spec sentence cites it.
- `-22` vs `-36` in the U arm on kind B is which error PCRE2 reports first;
  both are typed errors, not answers.
