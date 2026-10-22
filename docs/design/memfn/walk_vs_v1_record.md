# Set-FIND search form: walk vs V1 and its relatives — the closed record (2026-10-21)

**Status: CLOSED.** Frank, 2026-10-21: "the choice, which i agree with, is to use the walk when
the subject is not known." This file records why, so the question is not re-opened without
NEW evidence (see "Re-open only if" at the end). It reverses D169's default (V1 when landing
predictability is unknown); the D169 addendum is proposed in memfn/docs/responses.md for main to
file.

## 1. The question

A set-FIND site (pcrec's DFA skip loop looking for the next byte of a multi-member set) can
search with:
- **the walk**: one byte at a time through a 256-entry table, inline in pcrec's DFA loop;
- **V1** (R17-b's `pf_terms_mask`): 8 bytes at a time with a SWAR test of the set's 1-2 cover
  terms, the mask kept between calls, `ctz` per stop, called through `<stem>__next_candidate`.

Both forms stop at EXACTLY the same bytes (the walk's table equals V1's member set on every
pattern checked). Only the cost between stops differs. Verification after a stop is identical:
the DFA runs from the stop and asks for the next candidate only when back at its start state.

## 2. What was believed, and what the measurements showed

| date | belief | evidence | outcome |
|---|---|---|---|
| grid1/grid2 (synthetic) | V1 beats the walk at every N ≥ 8; landing predictability, not gap, decides | grid2read §3.5 (M9, M15) | the walk pays ~4-5 ns per unpredictable landing; on regular landings V1 loses +15..+46% |
| 2026-10-20 (D169) | when predictability is unknown, presume large irregular gaps → default V1 | Frank's reasoning on absolute time | became B4's default |
| 2026-10-21 rev 4.1 | route by cover term count: V1 at ≤ 2 terms | grid2's nine shapes | B4's rule (`kit.terms.V1max` = 2) |
| 2026-10-21 E8 (real text) | — | 19 real users' patterns × 94 cells, files ≥ 1 MiB (e8min, two windows) | V1 WINS 46 cells (−3..−55%), LOSES 35 (+2..+41%), NULL 13. Losses are UNLISTED → B4 refuted |
| 2026-10-21 e8why | — | counts only | losses = DENSE + PREDICTABLE stops (≤ 40% empty 8-byte blocks AND low mispredicts per stop): English logs, code, prose. Wins = rare or irregular stops: non-English text, compressed binaries |
| 2026-10-21 flat | Frank: flatten the mask into a position list, no ambiguous branch | timed twin | flattening COSTS more (F8 L10 +34%, F64 +68%): the DFA's run after a stop steps past later candidates, and draining stale positions brings the unpredictable branch back |
| 2026-10-21 flat | wider stretch (64 bytes) | M64: 64-byte mask, ctz/blsr | best single form: −7.1% total vs walk; sparse wins grow (non-English −60%); dense losers stay (+19..+20%) |
| 2026-10-21 adasim | per-64-byte adaptive walk ↔ M64 | count-only simulation | predicted −13.2%, IF the observation is cheap and walk mode costs what the walk costs |
| 2026-10-21 adatwin | — | timed twin + object size | adaptive −2.2% (carried across calls +13.5%): walk mode INSIDE the producer is not the walk (+28% on a file it walked 91% of); the per-stretch reading costs 5-7 ns |

## 3. The mechanism, in one paragraph

On dense, predictable text (structured English: log fields, code tokens, capitals at line
starts) the walk's one branch per byte is almost always predicted, so a stop costs it nearly
nothing. V1 rarely gets its 8-byte skip there (most blocks contain a stop) and pays per-stop
bookkeeping: the in-block check, the mask test, `ctz`, and often a fresh unaligned block after
the DFA has run past the cached one. On rare or irregular stops the picture inverts: V1 skips
empty blocks 8 or 64 bytes at a time and the walk mispredicts at irregular stops. The kind of
text decides, and it is a property of the subject, unknown at compile time.

## 4. Size (gcc -O2, .text per artifact, adatwin)

| form | .text | producer alone | speed vs walk |
|---|---|---|---|
| walk | 1.30 KB | — | 0% |
| V1 | 1.94 KB | 0.57 KB | −3.9% |
| M64 | 2.71 KB | 1.30 KB | −7.1% |
| adaptive | 3.30 KB (+256 B .rodata) | 1.79 KB | −2.2% |

Gain per added KB: M64 over V1 +4.3%/KB; adaptive over V1 negative. Frank's test: "10%
improvement is decent, but less so at double the code size." M64 is ~7% for 2.1x the walk's
text, with regressions on dense English. That fails it.

## 5. The ruling and its effects

- **Default:** a set-FIND site uses the WALK when the subject is not known.
- **V1 / M64** only where a MEASURED or caller-stated regime says the stops are sparse or
  irregular (R5's MEASURED path, or a future subject analysis).
- **B4** is re-scoped. Its V1 movers disappear, and no default byte move is expected.
- **Not a dial choice.** The losses follow the kind of text, not size versus speed, so a
  speed-leaning `--tune` position would still regress English logs.
- **Filed for later:**
  - [MEMFN-SKIPSWITCH]: a walk ↔ wide-mask switch inside pcrec's DFA skip loop itself, the
    only place a "walk mode" is really the walk. **Moved to BOONIES** (Frank, 2026-10-21,
    main 388353af7: "adaptive methods haven't proved their worth"; a near-duplicate of adatwin).
  - [MEMFN-POSCOST]: position pricing, superset hulls, verify order. Its counts stand, but they
    matter only once a non-walk default exists.
- **Sibling, not this question:** R-27 (the REPORT row is slow on sparse text). It needs the
  skip the default build already has, not a new form.

## 6. Do not retry without new evidence

- V1 (or any 8-byte SWAR) as the default for unknown subjects: refuted on real text.
- Flattening the mask into a position list (8- or 64-byte): costs more on dense text.
- An adaptive switch INSIDE the kit's candidate producer: its walk mode is not the walk.
- Carrying a mode across calls without a subject reset rule: strands random-dense data.
- Choosing the form from the cover's term count alone: shape does not separate the losers.

## 7. Re-open only if

- bench (pcrec-bench, the official tier) or a real user shows a workload where a wide form
  wins without the dense-English losses; or
- ~~[MEMFN-SKIPSWITCH] is built as a switch in pcrec's DFA loop and a timed twin shows it
  beats the walk on dense text and keeps the sparse wins; or~~ (in Boonies: Frank,
  2026-10-21, "adaptive methods haven't proved their worth"; not a re-open path);
- a subject analysis or caller hint becomes available at the call (then the measured path
  applies, not a new default).

## 8. Sources

- E8: `docs/design/memfn/r17b_prime/e8min/` (plan, prereg, verdict), `docs/dev/lanes/e8min_report.md`,
  `docs/dev/lanes/e8why_report.md`.
- Twins: `docs/dev/lanes/flat_report.md`, `docs/dev/lanes/adasim_report.md`,
  `docs/dev/lanes/adatwin_report.md`.
- Branches: `lane/memfn-e8min`, `lane/memfn-flat`, `lane/memfn-adatwin`.
- Decisions: D169 (+ the proposed reversal addendum), D170 (the minimal E8 bar).
- Earlier synthetic work: `docs/dev/lanes/grid2read_report.md`.
