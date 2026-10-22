# i2design — [FINDALL-NEXT] I2 design note (lane report)

Lane i2design (opus), 2026-10-21, branch `lane/i2design` from `lane/i1build`
`e0139d8c6` (abi 83). DESIGN ONLY: nothing under `src/`, `cli/`, `lib/` or `tests/`
changed, nothing ran on the box, and no clock was read. Rulings file
`i2design_rulings.md`: empty at every checkpoint, so no entry was applied. The file is
gitignored (`.gitignore:68`), so it exists in the worktree but cannot be committed.

## Deliverable

- `docs/design/findall_iter_i2.md`, revision 1. It is a delta note: §0's header says why
  it is not revision 4 of `findall_iter.md`.
- `docs/design/findall_iter.md`: a pointer paragraph at the end of §12 naming what I2
  withdraws.
- `docs/design/CLAUDE.md`: the index entry.

## The design in five lines

1. `size_t <prefix>_next_n(rx_iter *, caps, k)`: up to k full-capture entries, written in
   place. A return below k means the iterator has ENDED (`it.rc` says why). k = 0 is
   inert. It is k calls of `next` by construction, so the two interleave freely. NO
   `rx_iter` change; `PCREC_ITER_LAYOUT` stays 3.
2. `_next` and `_next_n` are thin controllers over ONE static `always_inline`
   `<p>__pull(it, caps, k)`. `_next` passes k = 1, and gcc is predicted to fold that to
   I1's code. That prediction is gated: "`I` unharmed", `I` at I2 against `I` at I1.
3. `RX_FOREACH(info, it, m)` lives in the shared block. It calls `info->next_n` with a
   4→64 doubling buffer inside a 4,168 B automatic struct (computed, not measured). It
   never allocates and needs only the shared block, never the artifact's `.h`. It handles
   `break`/`continue` with the two-loop idiom. It refuses with `PCREC_ERR_ITER` when
   `next_n` is NULL, when NCAPS is greater than `RX_FOREACH_PAIRS`, and (Q2) when the abi
   differs.
4. The internal batch is WITHDRAWN: `rx_iter_batch`, `rc_next`, `bhead`/`bcount`,
   `OPT_BATCH`, `__fill`, the `batch` column, `B64`, and §3.4a's conditional. B64 measured
   `off` on every dense subcell. N64 won only by removing calls, which the caller-side
   macro does.
5. One abi event (84 if nothing lands first). `rx_info` appends `next_n`. The spec hunks
   (§3.8.1/§3.8.2, §1¶2/5/6/7/8, §6 row 31) are listed in note §6.

## Difference from the design of record (brief's STOP RULE)

`findall_iter.md` rev 3 §6.9 named **I2 = the kit's `st` stage** and **I4 = `next_n`**.
Its §12 (the I1 addendum) said "I2 appends" the batch fields AND `st`. The manager's later
record (plan.md, wake.md, D171) puts `next_n` + the macro in I2. The substance is
compatible: `next_n`'s signature is rev 1's twinned one, with Q-I4's full-caps stride. The
note follows the manager's record and renames the kit stage I3 (note §7). If the manager
prefers rev 3's names, this stage is "I4" and nothing else changes.

## Facts cited (none re-measured)

- "0.58x on prose via the PLT" is c3-4k R2 `N64/L_old` = 0.5761
  (`parity_report.md`, RESULT (parread)). Against `I` it is 0.74. On c1 and c4, N64 ≈ I.
- **c6: N64 is 1.66-1.95x WORSE than `I`** (twin, attempt route). The record does not
  explain it. The note guesses a two-copy `__find` layout in the twin and puts c6 in the
  I2 timing gate.
- The twin's N64 was spans-only (`mktwin.py`). I2's entries hold full captures, written in
  place. The prediction is "no worse"; the c4 gate checks it.

## Sabotage ids

S1309-S1318 are PROPOSED (ten rows, note §5.4). They lie inside I1's range S1297-S1330 and
are unused on main and in every worktree. The kit's ledger says "next free S1331", and
S1331/S1332 exist. **The manager confirms the range**, or names another.

## Questions for Frank (plain words, each with a leaning; note §11)

1. **Patterns with very many capture groups.** The macro's buffer is a fixed 4 KiB. Past
   255 groups it cannot hold even one match. *Leaning:* stop with the iterator's error
   code. The caller raises one `#define` or uses the artifact's own entries.
2. **Checking that the record matches the header.** This is one compare per loop, so that
   a record from a different pcrec build fails cleanly instead of calling through the
   wrong offset. *Leaning:* check, once per loop. It is the only safety the
   header-less use has, and it is not a check on the caller's calls.
3. **Leaving the loop early.** Up to 63 fetched matches are never seen, and the iterator
   has moved past them. *Leaning:* say so in the spec ("finished when the loop exits");
   add no rewind code.
4. **Withdrawing the internal batch for good.** The October 14 ruling put batching inside
   the iterator. It measured slower, and the caller-side macro is what won. *Leaning:*
   withdraw it entirely (it was never built).

## What the critic panel should attack (note §12)

1. The c6 loss and the guessed cause.
2. "`_next` folds to I1's code" under `always_inline` STEP and the VM's `__step_own`.
   Also: is the fallback a second mechanism?
3. The macro's exact text: the two-loop idiom, `continue`, nesting, the comma initializer,
   `-Wall -Wextra -Wshadow -Wmaybe-uninitialized`, clang, `-O0`, and the per-match cost
   once `f->buf` escapes to the call.
4. k = 0 inertness versus "the first call binds".
5. Whether holding the new arms to `I` (not to `G` alone) is sound. Could a STEP-only plant
   be reachable only through `next_n`'s loop?
6. The drivers' oracles: `re.finditer` for encseam, and the runner-side retry loop for
   gstart.
7. Whether anything shipped on `lane/i1build` (spec §3.8, the block comment, §12) promises
   the withdrawn batch fields.
8. The sibling lens: are the rx_info entry pointers the dispersed family, and is two
   members the moment to stop?
9. The unlocks (note §10) and their triggers.

## STATE AT HANDOFF

Committed on `lane/i2design`: the rulings-file placeholder (gitignored, uncommitted),
the note, the pointer and the index entry. Then this report and the lanes-index line.
Rulings: none (the file is empty). Nothing is owed by this lane. Next: the manager's
critic panel on `docs/design/findall_iter_i2.md`, then a build lane with Frank's go
(already given for I2).
