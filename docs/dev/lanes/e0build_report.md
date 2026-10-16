# e0build — E0 of compound_entries.md rev 3: the zero-mover `entry_rows[]` with its rank column

Lane `e0build` (opus), 2026-10-16, branch `lane/e0b` from main `2288ad1cb`. Build go: Frank,
D167 (2026-10-16). Design: `docs/design/compound_entries.md` revision 3 §3.0 I2, §3.2, §3.6,
§4.1, §5.1 (E0a, E0b); panel `docs/dev/reviews/2026-10-16-r3-compound-entries.md` (LK-1, CE-1,
CE-2, F3, I4); D163 addendum 7 (Q4: E0 before I1).

## 1. What was built

**Scope: E0a and E0b. E0c is NOT built** (§5 below). No emitted byte is meant to move, and
nothing here is an abi event.

- **E0a: `entry_rows[]`** (`src/gen/entries.c`). Each entry is a CONTROLLER row:
  `{entry, when, comb, parts, nparts, mode}`, first match per entry. A part reference is
  `{part, when, rank}`. The combinator column (`EntryComb`) holds only the combinators that
  have an emitted client: `locate-then-finish`, `finish-at`, `forward`, `first-nonzero`, plus
  `leaf`/`data`/`driver` for the residuals, `info` and `main`. The mode column holds only
  `ONESHOT`.
- **The RANK column** (`PcrecEdgeRank`, `core/internal.h`: R0 rare, R1 conditional, R2
  per-call, R3 inner). It is new data, written by hand from the emitters' call sites
  [r3 LK-1]. Each rank is a shape predicate:
  - `search_run -> prefilter` is R3 where `PcrecEntryShape.prefilter_retry` is set, else R2.
    The new field is set in `emit_vm.c` from the two facts that the search body's
    `retry_win`/`retry_seed` read: `v.nclamp > 0` and the re-seed row's action. It is not a
    scan of the text (§4.1).
  - a compound's first operand is R2 under `\G` (`comp_floor_any`), else R1.
  - the `rev-end` tie's `search -> match` is R0.
  - the VM `_in` entries' two branches (NULL descriptor or not) are R1.
  - everything else is R2.
- **The compound controller as rows.** It has two operand ids, `PCREC_ENTRY_COMP_A` and
  `PCREC_ENTRY_COMP_B` (`<p>__<role>_search`), and three shape fields: `compound`, `comp_b`
  and `comp_floor_any`, set at the DFA emitter's shape site. These rows state what
  `emit_compound.c` actually calls, and that differs from B0's hand list in three ways (§4).
- **E0a's both-walks oracle** (commit `42da18f60`, deleted by E0b). It was always on in that
  commit and checked two things against `entry_edges[]`: the derived edges on every shape, and
  the closure on every request. Section 2 has the result.
- **E0b** (commit `37a4d3bfb`). Removed `entry_edges[]`, the seven predicates only it used, and
  the oracle. `pcrec_entry_shape` now derives the relation once, closes the request over it,
  and fails as an internal error when the closure reaches an entry that has no row on the
  shape. The relation is reported through a new `PcrecEmitIn.edge_rank` out slot.
- **The rank fixture** (§3.6, a precondition of E1):
  - `tests/compound/entry_ranks.tsv` is hand-written from the emitted C. It has 10 witness
    rows, and every rank R0-R3 is WITNESSED, so no row is UNWITNESSED. Each row names its call
    site in the caller's body and the exact count of that site.
  - `tests/compound/check_entry_ranks.py` checks the fixture against the drive's new `ranks`
    subcommand (`compound_drive.c`) and holds each witness to its site. It then checks the
    re-seed population: every corpus hybrid is R3 if and only if its emitted `search_run`
    holds a second `<p>_prefilter(` call site. That fact is read from the text, with K35
    floors.
  - It runs as `run_compound_unit.sh`'s new `E0` block, inside `make test-compound`.
- **Sabotage S1008** (`tests/mech/sabotages/S1008_e0-rank-r3-read-as-r2.sh`): the R3 cell is
  read as R2. Of the allocated range S999-S1008, it is the only row E0 owns. S999-S1007 plant
  rows that E1 builds (P1, T1/T2, P2, the `noclone` count, `forwardable`, `callers`, `θ_hot`,
  the layout pass), so they stay with E1.

## 2. Validation

| check | command / file | result |
|---|---|---|
| build | `make -j16` | clean |
| strict | `make strict` | clean (`-Werror -Wshadow`) |
| E0a both-walks oracle (E0a commit) | scratch sweep, every corpus block x 7 arms (default, `-e utf8 -futf-check`, `-e utf8`, `--engine=vm`, `--engine=vm -e utf8 -futf-check`, `-fprefilter`, `-fno-prefilter`), `--features all --emit-main` | 35,805 runs, 29,848 compiled, **0 disagreements**; reached 5,888 hybrid, 228 compound, 3,797 forward-rung, 20,250 VM, 9,598 DFA artifacts |
| rank fixture | `check_entry_ranks.py --every 1` | 10/10 witness rows, 0 failures; re-seed population 910 R3 / 449 R2, 0 failures |
| rank fixture, failing direction | S1008 plant applied by hand, `--every 8` | 115 FAIL lines (114 population artifacts, plus the R3 floor of 0 against 56); the fixture's two R3 rows fail too |
| `make test-compound` | `build/logs/test-compound.log` | **PASS** (§2.1) |
| ZERO MOVERS, emit_sweep against the merge-base | `build/land/chain.sh` | **OWED** (§2.2) |
| `make test` | `build/land/chain.sh`, through `scripts/perfrun` | **OWED** (§2.2) |

The corpus rank census at EVERY=1, from the drive over 4,624 distinct patterns (4,243
compile):

| edge | rank | count |
|---|---|---|
| `search_run -> prefilter` | R3 | 910 |
| `search_run -> prefilter` | R2 | 449 |
| VM `_in -> {sibling, _run}` | R1 | 2,037 each |
| compound `search -> comp_a` | R1 | 41 |
| compound `search -> comp_a` | R2 | 7 |
| compound `search -> next_pos` | R1 | 27 |
| compound `search -> comp_b` | R2 | 27 |
| `rev-end` tie `search -> match` | R0 | 1 (`(?:\s+\|x\s*?)$`) |

### 2.1 make test-compound

`make test-compound` (EVERY=8, `build/logs/test-compound.log`): **PASS**, every block green
(B0 closure exactness under three requests x three arms, E0 fixture 10/10 and re-seed
population 114 R3 / 52 R2, B1, B2, B4 incl. G1/G2/G3/G4/G7 against libpcre2).

### 2.2 The owed heavy chain

The box is shared, so the heavy runs wait for the manager's slot. `build/land/waiter.sh`
(detached) polls `worktrees/e0b/.lift` and then runs `build/land/chain.sh` once. The chain:

1. `make -j16`.
2. A reference `build/pcrec` from `git archive 2288ad1cb` (the merge-base), in
   `build/land/ref/`.
3. `scripts/emit_sweep.py --ref-bin <ref>`, five runs, each logged to
   `build/land/sweep-<name>.log`:
   - **full**: every default stream (corpus `.c` at the default engine and `--engine=vm`,
     `--emit-ir`, composition, dumps, `--emit-facts`, emit-ir-auto, stderr), self-check
     first;
   - **arms**: `--arms start` (the start-family deny arms at byte and utf8, plain `-e utf8`,
     `-i`, the null arm);
   - **comments**: `--extra=-fcomments`;
   - **simd**: `--extra=-fmemfn-simd` (SIMD on; the full run is SIMD off);
   - **utfcheck**: `--extra-base="-e utf8" --extra=-futf-check`.
4. `scripts/perfrun --label e0build -- build/land/test.log`.

Each step logs `rc=` to `build/land/chain.log`. The completion line is
`== e0build chain COMPLETE ==`. The make verdict is `grep -E '\*\*\* \[(Makefile:[0-9]+:
)?test-' build/land/test.log`, which must be empty. Any non-zero emit_sweep rc is a mover,
and a mover is an abi event that goes to the manager (brief: STOP and report).

## 3. Why zero movers holds by construction

- The default request reaches the same closure over the derived edges as it did over the hand
  list, so no `static` keyword moves.
- No emitter reads `comb`, `mode` or the rank.
- The new shape fields are read only by `entries.c`.
- A compound is compiled only under the default request (`compile.c`'s `comp_state`): any
  `req` or `part_role` sets `COMP_OFF`. So the extra compound edges cannot change a linkage.

E0a's oracle checked the closure equality on every corpus compile. The emit_sweep chain is
the independent control (§3.6: "the only control cited").

## 4. Ambiguities resolved (each in the zero-mover direction)

1. **E0 scope.** §5.1 splits E0 into E0a/E0b/E0c, and the brief names "`entry_rows[]`, with
   E0a's per-edge RANK column". I built E0a and E0b. E0c is a re-spelling of
   `emit_dfa.c`/`emit_vm.c`'s entry writers through per-combinator emitters, many sabotage
   anchors sit on those writers, and it is not needed by E1 or I1's consumption of the
   table. It is left as its own step, and the manager was told when the lane started.
2. **The part reference gets its own `when`.** §4.1's `PartRef` is `{part, rank}`, with the
   shape test only on the row. But one controller body holds a call on only some of the
   shapes its row serves: the subject check under `-futf-check`, the `rev-end` tie, the
   variables, the hybrid. Without a per-reference `when`, each such fact would multiply the
   rows. The alternative was a rank predicate that returns "absent", which would merge
   presence into rank. I added `when` to `PartRef` instead.
3. **The compound's edges are stated as emitted**, not as B0 had them:
   - `match_caps` calls the first operand, not `_match`;
   - `match_caps` runs its own prologue (`-> valid_upto` under `-futf-check`);
   - `search -> next_pos` and `search -> comp_b` exist only when Q is emitted.

   B0's `match_caps -> match` edge on a compound was spurious. It was harmless only because
   the default request exports every public entry. The E0a oracle declared exactly these
   differences for the compound shape, and nothing else.
4. **Operand ids are internal entries.** `COMP_A`/`COMP_B` are `PcrecEntry` rows, so the
   compound's parts are in the same relation the layout row will read. Their linkage bits
   are computed and never asked.
5. **The rank of the VM `_in` entries' two calls is R1** (the descriptor test selects one).
   **`main -> search` is R2** (one call). **`var_valid -> valid_upto` is R2.**
6. **`EC_FORWARD` for the VM's un-suffixed entries.** They bind storage and call their `_run`
   body, or forward to `_in`. The `_run` bodies carry the `locate-then-finish`/`finish-at`
   combinators.

## 5. Not done / for the manager

- E0c (above). No plan.md row names E0, so no STATE tag was moved; the manager owns that
  row.
- The mech row S1008 was validated by hand (§2). Its matrix figure is owed at a mech slot.
- `comb`/`mode` have no reader until E1/I1. This is stated at the table.
- Process note: at the lane's start, one scratch file was written under `~/.claude/projects/…`
  (outside the mandate). It was removed within the minute, and all later scratch went to
  `worktrees/e0b/build/scratch`.
