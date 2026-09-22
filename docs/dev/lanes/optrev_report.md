# lane `optrev` — [OPTLOOP.1.analysis] = [BENCH-REVIEW], cycle 1 of the optimization loop

Branch `lane/optrev` from main `ab341bfe`, 2026-09-22, opus. Analysis and
measurement only: **nothing under `src/`, `cli/`, `lib/` or `tests/`**, and
nothing written anywhere in `/Users/fdicostanzo/pcrec-bench`. Delivered
COMPLETE; nothing owed by this lane. What IS owed is the Linux profile
work the analysis itself charters as a precondition on any implementation —
see §5 below for exactly where those commands live.

## 1. Deliverables

| file | what |
|---|---|
| `docs/dev/optloop/cycle1_analysis.md` | the analysis (1,380 lines): §0 the criterion, §1 all 128 cells ranked, §2 cause bucketing off the D81 stamps, §3 the five mechanisms + M6, §3.1 the three parked rows placed, §4 deferral dispositions, §5 six proposed plan rows, §6 limits |
| `docs/dev/optloop/cycle1_rows.tsv` | the machine-readable ranked table, one row per ranked cell |
| `docs/dev/optloop/{parse_pats,stamps,rank,join,scale,table,mdtable}.py`, `p2info.c` | the reproduction pieces |
| `docs/dev/optloop/CLAUDE.md`, an entry in `docs/dev/CLAUDE.md` | the directory's charter and its index line |
| this file, and its line in `docs/dev/lanes/CLAUDE.md` | the lane record |

`docs/dev/plan.md` is deliberately **not** edited: the proposed rows are in
the analysis §5 for Frank to ratify, per the brief.

## 2. The headline a fresh agent needs

pcrec's best variant is **fastest or tied on 91 of the 125 ranked cells** of
`capability@0.1`. Of the 34 it loses, **nine are cells where pcrec already
beats every SCALAR engine** and only `rust`'s vectorized multi-literal
prefilter is ahead — recorded as SIMD-phase deferrals per D119, not as
cycle-1 targets. What remains is dominated by **four compile-time pre-checks
PCRE2 computes and pcrec computes only partly**:

1. a **required byte** (`PCRE2_INFO_LASTCODEUNIT`) — pcrec has none at all;
2. a **start anchor** bound — pcrec has it on the DFA route
   (`start_max`, `src/gen/emit_dfa.c:6808`) and **not** on the VM route;
3. a **first-byte set** — pcrec derives it from the DFA's start state, so a
   leading `\b` universalizes it to the 63-byte word class;
4. an **end-anchor window** — pcrec has none; this is D77's own named `\z`
   fold, now with a number.

The five proposed mechanisms are, in rank order:

- **[OPT-REQBYTE]** (score 3.714, 5 cells, size S–M) — one `memchr` per
  call for a byte every match must contain. Serves both engines, which
  matters because the VM's hybrid prefilter is declined outright for
  backreferences and linked calls.
- **[OPT-ANCHOR-VM]** (2.112, 2 cells + the three worst default-config
  cells in the set, size S) — the DFA's three-valued `start_max`, derived
  one layer up and read by both emitters.
- **[OPT-FIRSTSET]** (1.002, 4 cells, size M) — the candidate-start set
  computed from the AST, looking through leading zero-width assertions.
  Names the cause of [OPT-3]'s own measured "the skip loop skips ZERO
  bytes".
- **[OPT-ENDWIN]** (0.871, 1 cell, size M) — the end-anchor start-window
  bound; D77's named candidate.
- **[OPT-ATTEMPT-SPLIT]** (0.306, 2 cells, size M–L) — `^` on some branches
  currently costs the prefilter, the premultiplied table and the [OPT-5]
  scan edge all at once.

Recommended batch 1 (D119 caps it at three): the first three. They carry
6.828 of the 8.005 weighted score the five cover, and [OPT-REQBYTE] and
[OPT-FIRSTSET] share one AST walk.

## 3. The four findings worth reading before the next lane opens

**(a) The bench's own floor row is the control that makes the whole
analysis citable.** `floor-byte` (the pattern `~`, a byte absent from the
throughput text) reads 17,611 ns at 1 MiB on pcrec, 17,693 on
`libpcre2-interp`, 17,817 on `rust` — 0.0168–0.0170 ns/byte, and **pcrec is
the fastest of the three**. That rate is one `memchr`-class pass and it is a
property of the box. Every "the winner answers in one pass" claim in the
analysis is anchored to a number pcrec itself already achieves, so none of
them is a claim about a mechanism pcrec cannot have. Read the other way, the
same row is the second control: `--engine=vm` on `~` costs 815,257 ns
against `auto`'s 23,115, a 35× penalty on the simplest pattern in the set,
because a forced VM has no prefilter and walks every start position.

**(b) The ranking hides the shipped default, and on three cells that
matters enormously.** The D119 rule ranks pcrec's BEST variant, which is the
honest "can pcrec do this at all" comparison. It is not `auto-caps`. On
`evil-alt-nested` and `trim-nested-star` — both `^`-anchored `redos-nested`
members where turning captures on moves the artifact from the DFA to the VM
— `auto-caps` is 49,016× and 39,447× the algorithmic target while scoring
**zero** in the ranking, because `--no-captures` wins their row outright.
The analysis carries them in its own §1.1 table. *A best-of-variants ranking
is the right instrument for finding mechanisms and the wrong one for
describing what a caller gets.*

**(c) The minimal witness for [OPT-FIRSTSET] is one construct wide, and it
was built rather than argued.** `A[A-Z0-9]{16}` stamps
`RX_DFA_PREFILTER "memchr"` with a 1-byte candidate set;
`\bA[A-Z0-9]{16}` stamps `byte-class-bounded` with a **63-byte** one — the
word class, 77.21% of the bench text, so the skip loop can never skip. PCRE2
records `FIRSTCODEUNIT = 'A'` for both. Four patterns in the set carry that
63-byte set and three are losing rows. The cause is that pcrec derives the
set from the bytes that leave the DFA's start state, and a leading `\b`
makes that state track word context.

**(d) An extraction bug that reads as a compiler bug, recorded so the next
lane does not re-find it.** `pcrec --list-source`'s `pattern` column is
escaped in `pcrec_sb_field`'s vocabulary (`\\` `\t` `\n` `\r` `\xNN`,
`src/core/sb.c`), so a pattern taken from that column **must be decoded
before it is handed back to `--pattern`**. The first cut of `stamps.py` did
not, and the result was nine plausible-looking compiler refusals — *"range
out of order in character class"*, *"missing terminating ] for character
class"*, *"module 'branch-reset' is enabled but (?\|...) is not implemented"*
— on patterns the bench had compiled successfully at the same pin. Every one
was the extractor doubling or dropping a backslash. The cure that turned it
from "plausible" to "checked" was not re-reading the decoder: it was
**comparing all 64 decoded patterns byte-for-byte against the bench's own
derived `patterns/*.rx` exports**, which are an independent projection of
the same source, and getting 64 of 64 identical. *When one instrument reads
a pattern, a second, independently-produced copy of that pattern is the only
thing that says the reading is right.*

## 4. Method, and what makes each class of claim citable

- **No timing on this box.** Every engine-versus-engine number is the
  bench's Ryzen 1600 measurement (`pinconfirm` and `fullroster` reports of
  2026-09-20, pin `25b1984f`), read from the matrix and the subject-grain
  surfaces. Absolute medians were reconstructed as `best_ns × ratio` and the
  set-grain aggregation confirmed to be the SUM over the regime's subjects
  (`floor-byte`: 1,138 + 4,409 + 17,693 = 23,240 against the matrix's
  23,243).
- **Structural pcrec facts** come from this worktree's own
  `build/pcrec` (`ab341bfe`, `abi` 28) compiling all 64 patterns at the
  bench's three flag sets: 187 of 192 compiles succeed and the five failures
  reproduce the bench's own refusals exactly, which is the cross-pin check.
- **Structural PCRE2 facts** come from `pcre2_pattern_info` against the
  Mac's Homebrew libpcre2 10.48 — flagged in the analysis §6 as not the
  10.46 reference.
- **The subject census** that makes the throughput regime legible was
  produced by regenerating the three texts from the bench's own `captext.py`
  into the session scratchpad and checking all three SHA-256 values against
  the committed `manifest_throughput.tsv`. All three match.

## 5. What is OWED — and by whom

Nothing is owed by this lane. The analysis charters, as a **precondition on
any implementation lane**, one Linux executor session on ubuntubudu:

- the shared setup block, `docs/dev/optloop/cycle1_analysis.md` §3 "The
  shared profile setup" (scratch root, worktree, subject regeneration with
  its expected hashes, clock calibration, the shared find-all driver);
- per-mechanism command lists **M1.a–M1.c**, **M2.a–M2.c**, **M3.a–M3.d**,
  **M4.a–M4.c**, **M5.a–M5.b**, and the measurement-only **M6** — every one
  verbatim, and several of them capable of refuting their own mechanism,
  which is what they are for.

`perf` is unavailable on that box (`perf_event_paranoid=4`), so all of it
follows [OPT-5] step 0's method: a real driver, a calibrated clock, static
disassembly.

## 6. Commits on `lane/optrev`

Seven, in order: the three data-extraction scripts; the stamp join,
per-subject scaling and the `pcre2_pattern_info` probe; analysis §0–§2;
analysis §3; analysis §3.1–§6; the `[OPT-REQBYTE]` carve-out correction;
the two `CLAUDE.md` edits. `make -j4 CC=gcc-16` built clean in the worktree;
no suite was run and none is required — the lane changes no code.
