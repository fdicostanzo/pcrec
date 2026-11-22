# bspan3 report: block_span.md rev 3 (review r68 applied)

## STATE AT HANDOFF
OWED: none.

STATE: done (design text only; no code under memfn/src, src, cli, lib or tests; no suite, no timing, no queue job). Branch lane/bspan3, note `docs/design/memfn/block_span.md` rev 3 (revision line "rev 3 (2026-11-21): review r68 applied"), plus its index line in `docs/design/memfn/CLAUDE.md`. Rulings file `bspan3_rulings.md` re-read before each commit and this report; last entry applied: **R-1** (the review is renumbered r68; the note names r68 everywhere, F-ids unchanged). The owner's answer to `wrap-differs` had not landed there.

Probes run (re-derivations only): a lane build (`nice make -j2`, unlocked) and a traced pcrec (memfn/src/*.c with `-DMF_TRACE -O1`, linked the way `tests/memfn/rows_check.py` does) in `$PCREC_TMPDIR/scratch/bspan3/tr/`; one gcc -O0 `always_inline` probe (`$PCREC_TMPDIR/scratch/bspan3/ai.c`). The commands are in the note's §16 items 5, 6c and 9.

## THE JOB
Revise block_span.md from rev 2 to rev 3 by applying review r68 (filed as r67, renumbered) as the kit manager ruled it: every FIX-NOW and DOC item, and F-14 as ruled. Do not edit decisions.md (F-24 is main's). Every "today the tree does X" number carries its command. The premise test holds: `grep -n 'T-keep'` hit rev 2's row (§3) and unit text. In rev 3 T-keep is gone as a row and as a unit; the word appears only in the revision history, in the "cut" lines and in the dispositions table (7 hits, all saying it was removed).

## FINDINGS APPLIED
Every F-id maps to a section in the note's new §18 dispositions table. The main points:
- F-2 / F-3: §0.1 now gives the real population: 3 bench sites, all k 31 (HORS, HORS, R7w), and 0 corpus V sites (counterk:1919 is D1). I re-derived it from the trace's FDROUTE row. §10.1 adds SPAN-SEED, a literal list of 41 patterns at widths 32 and 4095 with printed counts. Its floors are 28 and 31 V sites, derived with the table's predicate. The identity gate's mask is declared before data (the four abi-line spellings). Its reference is the merge base, built once.
- F-14: U2b is now a machine-code census on the BUILT text, with padding normalized. It covers the real population plus a 160-pattern grid (710's ten classes x k 16..31 at width 32; 128 of them eligible). `\w{20}` is the floor witness and must be found. T-keep, §2.1 (c) and the scalar timing are dropped. The CONSTRAINT line now sits above §0. §2.2 holds the `wrap-differs` fork.
- F-4: T-vscan holds on finder row R7w. D1w is excluded on purpose, and the FREEZE NOTE says so. I re-derived `x[0-9]{26}` going to D1w under `--memfn=no-fd-d1`.
- F-1: the C18 amendment is now a unit in U4. It accepts the attribute spelling, and gets an -O0 rule for `always_inline` helpers (no symbol exists, which I probed). The rule: the compile must succeed and a ymm register must show in the caller. It also gets named witnesses (floor 2) and three control plants.
- F-10 / F-11: the table is asked at define and at use (runcmp's idiom). `skip` is lifted into the plan. The include bit goes on the art (ofsskip's idiom). One writer, lifted from ofsskip; vany joins at its next touch.
- F-5, F-6, F-7, F-8, F-9, F-12, F-13, F-15..F-19, F-21..F-23 are applied as their Fix texts say.
- F-20: the FREEZE NOTE quotes D201, add. 1 and add. 2 verbatim from the decisions.md record, and labels every reading as the managers'. **One deviation from the brief:** the brief's add. 2 quote starts "Scalar wrap: ...". The record (decisions.md D201 add. 2) has no "Scalar wrap:", and F-20 says to quote the record exactly, so the note quotes the record.
- F-24 was not applied: it is main's (decisions.md).
- SHIP-SIZE (§17): the cuts are T-keep, U2b's timing, G1's timing window and C6's four outside-bound cells, and no new levers (two are filed as PLAN rows with a trigger). The growths are the C18 amendment, the formhash shape + renderer + entry, 5 re-aims plus 1 ordering plant, SPAN-SEED (41 patterns, 2 floors) and 4 pin cells (12 pins in all). Total: 2 new table rows plus 4 reshaped, 1 deny, 1 card + 1 grid row + 1 formhash shape/entry, 2 G2 sections, 12 pin cells, SPAN-SEED, 1 identity gate, the C18 amendment, 5 new sabotage rows and 5 re-aims, 6 spec hunks, 1 abi event.

## OPEN QUESTIONS
- `wrap-differs` (owner, OPEN; the build waits on it). The wrapper changes gcc's SIMD-off machine code on `\w`-like sets (20-26 lines). It changes none of the 3 real sites. The note's §2.2 gives two outcomes:
  - (1) wrap everything;
  - (2) do not wrap the differing sets. No compile-time fact names "gcc's code differs". The nearest is a correlate, `kit_set_test`'s term count. That makes (2) either a gcc-specific proxy row plus a committed census check, with the SIMD-on win forfeited on those sets, or option B.
  The managers lean to (1).
- For main: D201 add. 2's population line (F-2) and its provenance pointer (F-24).

## OWED RUNS
none (U2b's census, F2 and C6 are build-lane steps; this lane ran no suite, sweep or timing).
