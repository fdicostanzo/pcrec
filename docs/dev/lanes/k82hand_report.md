# Lane `k82hand` — K82 cause (B)'s HANDOFF, design only (2026-10-04, opus)

Branch `lane/k82hand`, from `lane/k82fix` `f0d0b206` (abi 60, not yet on
main). Docs only: nothing under `src/`, `cli/`, `lib/`, `tests/` or
`docs/spec/` changed, and no `make test` was run (none was owed). The one
build was `make -j4 CC=gcc-16`, for `--emit-facts`.

## Delivered

- `docs/design/litscan_k82h.md` — the design note.
  - §1: the mechanism, the proof (Claims 1-3 plus the `\G` variant), the
    byte-offset fact, and the exact predicate.
  - §2: the slotting. A new `req_uses[]` table, axis `req-use`,
    `-fno-req-handoff` bit 46, `<PREFIX>_REQ_HANDOFF`, and abi 60 → 61 with
    its spec hunks.
  - §3: the movers and the predicted timing.
  - §4: the validation plan (S463-S472 and the alpha cells).
  - §5: 12 hazards and 8 questions.
- `docs/dev/optloop/s4/k82hand/` — the instruments, with their own
  CLAUDE.md:
  - `proto_maxoff.diff`: the prototype walk annotation, never applied to
    `src/`;
  - `k82h_census.py` and its transcript `k82h_census.out`.
- `docs/design/CLAUDE.md` and `docs/dev/optloop/s4/CLAUDE.md`: entries.

## Findings that a resuming agent needs

1. **The bound is BYTES on the lowered tree.** `ci-strasse` is K = 2, not 1,
   because `(?i)s` folds with `ſ` (2 bytes). `pcrec_cwmax` counts
   characters (`A_WCLASS` = 1) and would under-count, and that error deletes
   matches. Sabotage S464 is that error.
2. **Census over the prototype** (`k82h_census.out`):
   - Program movers: bench auto 47 (49 rows), corpus auto 160 (209 rows).
     Forced-VM: 0.
   - Unbounded and handoff-unreachable: bench 8, corpus 37. `union-select`
     is among them and stays unmoved.
   - All five cause-(B) cells move: K = 0, and K = 2 for `ci-strasse`.
3. **The handoff program does a suffix of the discard program's work.** So
   no regression is expected against abi 60 beyond one compare per passing
   call. `mod-i`'s residual over DENY is the pair arm's per-call overshoot,
   which is a separate item (H11).
4. **The twin's offset was not recorded.** The note's prediction table
   reuses k82cost's Mac T3 numbers. `twin_t3.py` takes OFF as an argument,
   and the transcript does not record the OFF used per cell. If
   `ci-strasse`'s twin used 1, its timing is unaffected but the twin was
   unsound on `ſtraße`.
5. **This branch lacks two of the note's references.** `litscan_k82b.md`
   and `../dev/optloop/s4/k82cost/` are on main (`7d81a618` merged), not on
   `lane/k82fix`. The note cites them by path, and they resolve once both
   branches are on main.

## Owed

- The light D6 panel on the note (Frank: light panel first). §5 lists what
  the critics must refute.
- Frank's rulings on Q1-Q8. Each has a recommendation in the note.
- The build lane, after the panel. Owed with it:
  - the mover manifest with the deny arm (§4.1);
  - the answer differential, including ASan (§4.2, §4.3);
  - the `handoff.rxt` witnesses;
  - the sabotage rows (§4.4);
  - the Linux alpha (§4.5).
