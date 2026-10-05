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

## Revision 2 (lane `k82hrev`, opus, 2026-10-04)

Applies the light D6 panel r1 (`docs/dev/reviews/2026-10-04-r1-k82-handoff.md`
on main; 17 findings, all ACCEPTED) to `docs/design/litscan_k82h.md`, in
place, each change marked `[r1 <id>]`; the note's new §R maps every finding
to the section that answers it. Docs only: no `src/` change, no `make test`.
One new compile-only instrument, `docs/dev/optloop/s4/k82hand/
k82h_census_r2.py` (+ `.out`), run with the existing prototype binary.

### What changed in the design

1. **The gate's contract** (S-F1, new §1.1a): `rx_reqrun` returns the
   LEFTMOST masked occurrence ≥ `search_from`; written into
   `ofs_test_emit_fn`, binding the pair arm and any future [MEMFN]/S4
   search arm; sabotage S464 plants the later-occurrence gate.
2. **The give-up allowance** (S-F2, C-C8): only a count-collapsed
   prefilter can answer below `c − K`, so only there can the VM's work
   change. H10 corrected ("the VM attempts fewer" was wrong elsewhere).
   Q10 recommends declining the handoff on count-collapsed prefilters
   instead of keeping the allowance.
3. **`\G`** (S-F3): the hybrid's prefilter is a third reader; sound for the
   filter (the retries already pass `attempt_position`), and a narrow
   decline (d′) for `\G` + clamped window, population 0 (Q9).
4. **Verbs/callouts** (S-F4): conjunct (g), structurally unreachable today
   (both refused, measured), sabotage S475 declared UNREACHED.
5. **utf8 round-up** (S-F5, S-F6): uncapped `< subject_length` loop inside
   the `lo > f` branch only.
6. **Stamp** (C-C1): `REQ_HANDOFF` on movers only (Q3 reversed); §2.3a
   enumerates the abi-digit and byte-count readers by grep on main and
   `lane/k82fix`, with per-option movement; bit 46 joins
   `strategy_denials` (C-C3), so DENY == BASE modulo the abi digit alone.
7. **Checks**: §4.2a gives the fact three checks that share no source with
   `rb_walk` (hand K pins incl. `ci-strasse` K = 2; an invariant-F oracle
   over libpcre2/python `re` anchored matches; K−1 over every K > 0
   mover); §4.2b handles DD12a(i); every sabotage detector moves into
   `run_prechecks.sh` §5.12; every row has a constructed reaching witness.
   Sabotage is S463-S477, fifteen rows, with revision 1's mapping in §4.4.

### Census results (`k82h_census_r2.out`)

- Corpus, 3,663 distinct pattern/args: `auto` 160 movers (121 DFA
  unanchored / 6 attempt / 33 hybrid, reproducing §3.1); `--no-captures`
  160 (144 / 7 / 9); `--engine=vm -fprefilter` 160, all hybrid (642
  refused, do-or-die). Same K histogram in all three.
- Every hybrid mover's `RX_VM_PREFILTER_LANG` is `exact`, in every config;
  the six bench hybrid movers too (checked one by one). So the narrowed
  allowance's population is empty.
- The 35 corpus blocks with a budget or a `gu` case: all VM with no DFA
  scan, 0 movers.
- The K > 0 population is thin: 27 corpus movers, 14 bench.
- No mover carries `\G`; the constructed witness `(?:\Gab|x)(cat)dog` is a
  VM hybrid, `exact`, K = 2 (prototype).
- Of the 12 `EMITTED_BYTES` pinned patterns, 2 are movers (`\bword\b`,
  `(?i)HeLLo`); the resource suite's 762,574-byte pin is not.

### Frank questions (revised, §Q)

Q1 yes (new axis, row 1 calls `req_admit()`); Q2 keep the round-up in its
revised form; **Q3 movers-only stamp (facts-only acceptable)**; Q4/Q5/Q6/Q7
unchanged; Q8 build after k82fix, the gate contract named in the build and
[MEMFN] briefs; **Q9 (new)** keep the `\G`/clamped decline in the first
build; **Q10 (new)** decline the handoff on count-collapsed prefilters.

### Owed (unchanged in kind)

Frank's rulings on Q1-Q10; then the build lane, which owes everything in
§4 including the three independent fact checks of §4.2a and the
constructed count-collapsed witness or Q10's decline.

### Process note

The scratch files of this revision live in the worktree's own
`build/k82hand-scratch/` (gitignored), never `/tmp`.
