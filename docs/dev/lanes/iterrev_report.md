# Lane `iterrev` — `findall_iter.md` revision 2 (the short revision before its D6 panel)

Lane `iterrev`, 2026-10-16, opus, from main `64e77cf9a` (abi 78). DESIGN-DOC lane: nothing
under `src/`, `cli/`, `lib/`, `tests/` changed; nothing measured; no clock read; no `make`.
Branch `lane/iterrev`.

## Deliverable

`docs/design/findall_iter.md` revision 2. Read its §R2 (ruling → section) first. Index
entries: `docs/design/CLAUDE.md` (the `findall_iter.md` entry) and this directory's
CLAUDE.md.

Inputs read: D163 add. 6-7, D165 + add. 1-2, D166 (+ add. 1-2), D167 + add. 1 in
`docs/dev/decisions.md`; `compound_entries.md` REVISION 3 from `lane/cmprev2` (not merged to
main at this lane's base; read with `git show`), especially I4 and §3.8; `compound.md` §A.2
and §B.2; `match_api.md` §10; r17b_prime.md §6 on `lane/memfn-r17` `c90d65e53`.

## What revision 2 does (summary for a resuming agent)

1. **Compound controllers.** `next` = `iterate(STATE; STEP; BATCH)`, a row of
   `entry_rows[]`. STEP = guarded `first-nonzero(R@q, SEARCH@LOWER(adv(q)))` (guard: the
   RETRY bit), else `SEARCH@lo`. This is split's controller exactly (`compound.md` §B.2,
   guard "floor can be live"), so one combinator emitter serves both. The combinator row
   gains a `meter` column (split `shared`, retry `per-operand`).
2. **Layout from the part-layout row.** Revision 1's §2.2 two-row rule is KEPT as the `0`
   cell's content (`compound_entries.md` I4); non-zero positions go through that note's
   §3.4 tables (P2 adds `noclone` to the label-table body).
3. **Internal batching** in `<prefix>_buffers` (a third region `batch`/`nbatch`, stride
   `NCAPS` pairs): a fill runs STEP up to `nbatch` times, delivery copies one entry per
   call, a code met mid-fill waits in `rc_next`. No `_in` memory = K = 1, written straight
   to `caps` (the same loop, degenerate). §3.4a argues answer/give-up identity to K = 1 by
   construction. Ships in I1 only if the parity slot's new `B64` arm beats `I` beyond the
   noise floor on cells 1/3; otherwise filed (I4). `next_n` stays optional, timed (`N64`).
4. **Binding at init.** `RX_ITER_INIT(s, n)`; `next(&it, caps)`; optional inputs are
   SETTERS on a FRESH iterator (`rx_iter_at`, `rx_iter_vars`, and a typed per-prefix header
   `<prefix>_iter_buffers`), recorded by header option bits: one rule instead of 2³ init
   macros. The per-call `(s, n)` compare is gone; the owner compare stays; an ENDED header
   state makes stickiness free on the fast path.
5. **Error contract** as ruled: 1/0 + `it.rc` (0 done, give-up or refusal code), sticky.
6. **F-1 static twins**: `__adv`, `__valid_upto`, `__var_valid` for every residual leaf; all
   internal callers (the compound controller included) call the twins; exported residuals
   forward. Folded into I1. A relocation check (no internal reloc to an own exported
   residual) and sabotage P-d.
7. **S as a derivation** (A10): S = max over paths of Σ 8 B × declared carried words. Today
   **64 B** = kit FIND row 40 (r17b_prime.md §6: base, top, mask, H, `valid_until`) + K5
   pair hits 16 (kept until a kit form is proven single-pass over its spans) + reseed hint
   8. Re-derived at I1; a later K5 retirement shrinks S to 48 B only riding another abi
   event (manager's answer-free call, leaning stated).
8. **Meter per logical search** (reading of D163 add. 6 Q1): the retry and the following
   search, and each step of a fill, get fresh meters; inside one logical search Q1 holds.
9. **Lenses**: §8.1 state family (the batch is the one caller-sized member, so it is not in
   S); §8.2 combinator family (the retry is a second row of split's combinator; `iterate` is
   the only new combinator); §8.3 the per-call overhead levers; **§8a NEW-DATASET**: every
   new item named with its home. The storage-row declarations move from revision 1's
   proposed standalone `iter_rows.def` to the STATE part's column in `entry_rows[]`
   (fallback named as debt). No new standalone table.

## Questions for Frank (discussion form, in §10)

- **Q-I1** meter unit: per logical search (leaning) vs per exported call (Q1 literal).
- **Q-I2** buffers binding: typed per-prefix header setter (leaning) vs `void *` macro.
- **Q-I3** batch region home: extend `<prefix>_buffers` (leaning; costs
  `-Wmissing-field-initializers` on positional initializers, F11) vs a separate `rx_batch`.
- **Q-I4** batch entry: full `NCAPS` pairs (leaning) vs spans-only (filed U12).

## Findings (§11; F1-F8 are revision 1's)

- F9: D165 add. 2 says `rx_buffers`; the shipped type is per-artifact `<prefix>_buffers`.
- F10: Q1 read literally would make the retry and batching move give-ups.
- F11: growing `<prefix>_buffers` warns positional initializers under `-Wextra`, incl.
  match_api.md §10.6's example.
- F12: designing the fill makes `__find`'s in-edge from `_next` R3 on every artifact once
  batching lands; `compound_entries.md` §3.8 lists it HELD (not edited here).
- F13: S today is 64 B; `compound_entries.md` and r17b_prime.md cite 48/56.

## Sabotage (PROPOSED; the manager allocates)

Revision 1's S923-S942 kept as labels (S931 retargeted to the owner compare, S935 to
`rx_iter_at`). New: P-a (pending code delivered early), P-b (one meter across a fill), P-c
(retry shares SEARCH's meter), P-d (compound calls exported `_next_pos`, structural), P-e
(batch stride one pair), P-f (setter on BOUND accepted), P-g (ENDED not set on refusal),
P-h (fill overruns `nbatch`, ASan). P-b and P-c ship constructed cells (no harvested cell
reaches them).

## Owed (not this lane's)

- The twin's re-spelling (binding at init, fused compare) and a `B64` fill arm, then the
  parity slot's pre-build run (§5.3), launched by main in a box window. The two PREDICTED
  numbers (three init stores; `sizeof(rx_iter)` = 160 B) come from that re-run.
- E0 before I0(c)/I1.

## Validation

Design text only. Checked: no stale revision-1 spellings remain (`FRESH_AT`,
`RX_ITER_INIT_AT`, `_VARS`, the per-call `(s, n)` signature, `__step` outside the history
row) by `command grep`. No suite run (none applies).
