# edge1 — [OPT-EDGE] STEP 1 (shared-sentinel edge dispatch) + K43 (b)

Lane B of the 2026-09-03 evening wave. Branch `lane/edge1`, based on main
9d8401a (abi 17). Written under the bench's box hold: TONIGHT is
write-only, no `make test` / `make test-axes` / `make test-codegen` /
batteries / timing loops. Every acceptance number that needs a suite is
marked **OWED**.

---

## 1. E1 — THE PREDICTION TABLE (written BEFORE any build or measurement)

Written 2026-09-03 ~17:15 EDT, after reading the mechanism
(`emit_scan_loop`/`emit_scan_edge`, `src/opt/scanedge.c`, the two
`DfaRepr` token blocks) and BEFORE editing a single line or measuring a
single artifact other than the one `pcrec -p rx iso-ts` run used to read
today's emitted loop.

### 1.1 The design I predict from

Today the loop body is, in order

```
A  accept probe            (acc->emit_top)
B  candidate-start prefilter (pf->emit)       — fires only at s0
C  stay skips              (dir->emit_skip)   — never fires at a scan head
D  the scan edges          — nscan × `if (state == HEAD && more && class_test)`
E  position-view select    (view->emit)
F  viewed accept probe     (acc->emit_after_view)
G  bound break + the step  (acc->emit_tail)
H  `if (<p>_<m>_is_dead(state)) break;`
```

D is the cost: one compare per edge, per iteration, on the generic path.

The change, in four parts.

1. **Renumbering** (`src/opt/scanedge.c`, folded into the compaction the
   pass already does): the surviving states are permuted so the scan-edge
   HEADS occupy the TOP `nheads` rows, in their existing relative order.
   Interior members are still dropped. Everything downstream reads state
   numbers out of the same `Dfa`, so the permutation is invisible to it.

2. **The stop predicate** (`emit_dfa.c`, the two `emit_token` bodies): a
   machine that carries at least one edge additionally emits

   ```c
   static inline int <p>_<m>_is_stop(<p>_<m>_state s) { return (unsigned)s >= FLOOR; }
   ```

   with `FLOOR = cell_of(n - nheads)`. Dead is ABOVE the head range under
   both representations without moving it: premultiplied dead is 65535 and
   the largest live cell is `(n-1)*ncls < 65535` by `PREMUL_MAX_ENTRIES`;
   indexed dead is `-1`, whose unsigned reading is `UINT_MAX`. So the ONE
   unsigned compare tests dead ∪ head, `is_dead` keeps its name, its body
   and its exact meaning, and NO TABLE BASE BIAS IS NEEDED — the heads stay
   real rows because they were moved to the TOP of the row space rather
   than below zero. (The brief's "bias the table base so negative offsets
   index" is the negative-sentinel variant of the same ruling; the
   top-of-space variant discharges the requirement "edge heads must remain
   VALID TABLE ROWS" with a bias of zero.)

3. **The loop** becomes

   ```
   for (;;) {
       A; B; C;
     <p>_<m>_scan_views:
       E; F; G;
       if (<p>_<m>_is_stop(state)) {          /* was: is_dead */
           if (<p>_<m>_is_dead(state)) break;
         <p>_<m>_scan_edge:                    /* rare: a scan-edge head */
           A;                                  /* the head's own accept probe */
           B;                                  /* ONLY when s0 is itself a head */
           D;                                  /* today's if-chain, TEXT UNCHANGED */
           goto <p>_<m>_scan_views;
       }
   }
   ```

   with, before the loop, a one-per-CALL entry test that sends a seed state
   that is already a head into the cold block (folded away entirely when the
   seed is the `constant` form and s0 is not a head — the common case).

   C is NOT replayed in the cold block: `pick_skip_states` declines any
   state carrying a scan edge, so `f->skip` and `f->scan` are disjoint by
   construction and a skip can never fire at a head. I predict I will add a
   `ctx_fail` assertion of that disjointness rather than leave it a comment.

4. **K43 (b)**, independent of the above: `<prefix>_run_state_init`'s slot
   loop becomes a designated-range initializer.

### 1.2 What moves, and by how much — PREDICTED

Byte formula, per MACHINE that carries at least one edge:

| term | predicted bytes | why |
|---|---|---|
| `is_stop` accessor | +95 | one emitted line + no comment of its own |
| two labels + the `if (is_dead) break;` + `goto` + braces | +150 | scaffolding |
| A replayed | +100 | one `if (…accepts(…)) recv = pos;` line |
| B replayed | +330, and ONLY when s0 is a scan head | the prefilter block |
| C replayed | 0 | not replayed (disjointness) |
| D | 0 | moved, not copied |

Per artifact, summed over its machines. `rx_search` carries the forward and
reverse machines; `rx_match`'s anchored machine is a third. Only the
forward machine can have a prefilter.

| artifact | edges (f/r/a) | s0 a head? | predicted Δ source bytes | predicted Δ generic-path instructions, forward loop |
|---|---|---|---|---|
| iso-ts | 4 / 4 / 4 | forward: yes | **+1,020** (345+345+330) | **−8** (4 edges × `cmp`+`jne`) |
| http-5xx | measured at E4 | TBD | +345 per edge-carrying machine, +330 if s0 is a head | −2 per edge removed from the generic path |
| cls-upto-4 (`[a-z]{0,4}`) | 1 / ? / 1 | forward: expect yes | +345 per machine, +330 if s0 is a head | −2 |
| no-edge control | 0 | — | **0 — byte-identical to main** | 0 |

Two predictions I will be judged on rather than these arithmetic ones:

- **P1 (the structural acceptance).** After the change, the forward scan
  loop's generic path in `objdump -d` has the SAME INSTRUCTION COUNT as the
  same pattern compiled with `-fno-scan-edge`, and the same count as today
  MINUS `2 × nscan`. The dead test's encoding changes from `cmp $0xffff` /
  `jne` to `cmp $FLOOR` / `jb` (premultiplied) — one instruction either way,
  both macro-fusing.
- **P2 (the no-edge control).** Every artifact with zero scan edges, and
  EVERY artifact compiled with `-fno-scan-edge`, is byte-identical to
  main's. The `is_stop` accessor, the labels and the cold block are emitted
  only for a machine with `nscan > 0`, and the renumbering only happens when
  the pass accepts at least one chain.
- **P3.** The answer is identical on every corpus cell and every axis.
  OWED — needs `make test` / `make test-axes` (tomorrow).
- **P4.** `-fanalyzer` is clean on K43's three named artifact shapes after
  the designated-range initializer, and the initializer's object code is the
  same instruction sequence as the loop's (gcc lowers both to the same
  `rep stos` / unrolled stores).

### 1.3 What I predict will NOT move

- The stamps. `RX_DFA_SCAN_EDGE` names the axis-I run-extension body
  (`range`/`bitmap`); `RX_DFA_TABLE` names the representation
  (`premultiplied`/`indexed`). Neither names a state number, a layout or a
  sentinel, so neither is made to lie by the renumbering. No stamp change,
  no IFF change. (If E4 contradicts this, the stamp is fixed with its IFF.)
- `docs/spec/tuning.md`'s `-fno-scan-edge` entry: the flag still removes the
  whole transform, and P2 says its artifact is unchanged.
- The compile-time bound D45 and `PCREC_MAX_SCAN_EDGES` (4). The floor above
  2 is [OPT-EDGE]'s NEXT rung and is measured on the new loop, not here.

### 1.4 The prediction table, scored

Filled in at E4. Every row gets HIT or MISS with the measured number.

---

*(Sections 2+ are written as the work lands.)*
