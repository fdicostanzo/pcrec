# Lane `ssedge` — START-SET edge cases and mutation detection (2026-10-05)

Branch `lane/ssedge` from main `e6ceeefa` (abi 61). Opus. Design, probes
and DRAFT test cells only: nothing under `src/`, `cli/`, `lib/` or `tests/`
changed. Brief: D148 addendum 1 (Frank: the set argument is not a proof;
test the EDGES and show the tests SEE each wrong variant at answer level).

**Deliverable**: `docs/design/startset.md` §6.4 (plus a pointer paragraph at
the top of the note) and `docs/design/startset/edge/` (own CLAUDE.md;
`run.sh` reproduces everything; verbatim transcripts in `out/`).

## Summary (a fresh agent resumes from here)

- **Cells**: 80 blocks, **2,070 cells**: 10 draft `.rxt` files (2,022 cells)
  plus `utfcheck_cells.tsv` (48 `-futf-check` cells). Every startpos at a
  character boundary is asked. Every answer is GENERATED from libpcre2
  (`cells.py` → `gen_rxt.py`).
- **Oracle agreement**: local 10.48 and the 10.46 reference (ubuntubudu, one
  compile + 2,070 matches in `scratch_lx/ssedge`, box idle at load 0.46)
  agree on **2,070 / 2,070**. Today's emitter (the deny arm) agrees with
  **every** cell (0 base disagreements).
- **Mutation table** (`out/mut_summary.txt`): every mutant in the brief is
  DETECTED by a draft cell at answer level, except two EQUIVALENT ones.
  - **Equivalent 1, the seek-start mutant** (`search_from` instead of
    `max(search_from, lo)`): there is no VM-hat handoff, and on the DFA hat
    the run argument applies (0 diffs on the 3 handoff movers).
  - **Equivalent 2, E\* without one seed** on 3+-seed machines: the emitted
    table is identical.
  - Both are argued in §6.4.3 items 6-7, each with the check that sees it.
- **Closure**: after four rounds of adding sweep witnesses, no block has a
  mutant that the sweep sees and no cell sees.

## Findings (startset.md §6.4.3)

1. **The unconditional re-seed loses matches on ordinary seeded movers.**
   It is not a `\G`-only hazard, so sound-F7/S485 are wrong about where it
   lives.
   - Witness: `(?:\b|xy)a` on `xya` → (0,3); the unconditional twin returns 0.
   - Counts: 6 of 84 random-family movers differ under the unconditional
     form, 0 under the conditional one. The census has 0 of 56 such movers.
   - So the conditional form is a SOUNDNESS requirement.
2. **`Tdfa` is not a sound floor.** This refutes §4.1a's "would also be
   sound" and §4.1 step 2's stated condition. The ruled `T = S` is
   unaffected.
   - Witness: `(?:\b|x)y` on `xy`. There `δ(·, x) = s0`, but
     `seed[class(x)]` is the word seed, so `x ∉ Tdfa`.
   - Corrected argument: the re-seed is exact iff every skipped byte is
     outside `S` (future-language equality of minimized states).
   - Consequence: C-SS\* cannot certify `T`; the start-byte oracle can.
3. **The DFA hat has only `-bounded` reach.** Measured 170 / 170 seeded
   artifacts (`wctx ⇒ views`), so the unbounded DFA-hat forms are
   unreachable. The bounded landing paths are answer-visible only under a
   restrictive context: `\B(?<!a)d` on `xd` (the clamp path) and on `xdz`
   (the hit path).
4. **The sound-F5(d) failing witness exists.** 36 of 97 count-collapsed
   hybrid movers lose without the re-seed, 0 with it. Witness:
   `\B(a|b){1,3}` on `xa`.
5. Re-seed removed: answer-visible on 26 of 41 movers. On the other 15 the
   stale s0 is permissive.
6. E\* without one seed: an equivalent mutant on every mover. Its guard is
   the §4.1a `T == S` build assertion.
7. The seek-start mutant is equivalent on both hats. Its guard is the
   structural check "no `_VM_START_SCAN != none` artifact has a handoff".
8. Per-member drops are seen only for members that a cell starts a match
   with. Full membership is the start-byte oracle's job.

## Sabotage rows flagged (§6.4.4)

- **S482**: unreachable. Its witness `\bab\b` is `offset-set-bounded`, not
  a mover, and the unbounded form has no seeded population.
- **S481**: plants the same row as S483. Fold or declare UNREACHED.
- **S483/S484**: need RESTRICTIVE-context witnesses, which are now measured.
- **S485**: now answer-visible. Its only reach is the `reseed.rxt` fixtures.
- **S480**: reaches only the six non-mover fixtures. The plant must carry
  r3's admission too.
- **C-SS\***: not the detector for a too-small `T`.
- **New rows proposed**: S503/S504, the no-candidate return placed before
  `rx_valid_upto` (VM / DFA). D148 addendum 1 lists this mutant and §6.3
  had no row for it.

## Validation (complete; nothing owed from this lane's runs)

- `gen_rxt.py write out/oracle_local.tsv out/oracle_ref_10.46.tsv`:
  `cells written: 2070 …; disagreements 0`.
- `pcrec --list-source` parses all 10 drafts.
- `mut.py out/mut`: `blocks 80 (hat: dfa 41, vm 13, vm-nullable 1, none 25),
  base disagreements 0`. The table is in `out/mut_summary.txt`.
- `search_uncond.py`: plain family `movers 84, cond-diffs>0 0,
  uncond-diffs>0 6, noreseed-diffs>0 75`; collapsed family `movers 97,
  cond 0, uncond 0, noreseed 36`.
- `census_reseed.py`: `rows 94, movers 56, cond>0 0, none>0 35, uncond>0 0`.

## Owed (not this lane's; named in §6.4.5)

- Trail and caller-buffer give-up cells (GU covers frames only).
- `-e utf8 --ucp` `\b` cells, once [UCP] U3/U4 builds the construct (it is
  refused today).
- The drafts' move into `tests/startset/` and `tests/utfcheck/` at each
  hat's build stage, with S503/S504 numbered after the highest S on main at
  landing.

## Process notes

- `oracle.c` was copied to the Linux box over ssh stdin, into
  `/home/duxevents/pcrec/scratch_lx/ssedge` (not the main clone). The light
  probe ran twice, the second time on the final question set.
- One process-rule slip: I used `pgrep -f` once, read-only, to check the
  search's liveness. Nothing was killed. The house rule says to poll by
  artifact, and every later poll did.
