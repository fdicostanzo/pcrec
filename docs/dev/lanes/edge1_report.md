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

### 1.4 The prediction table, scored — §4 below.

---

## 2. WHAT EXISTS ON THE BRANCH

Branch `lane/edge1`, five commits on top of main 9d8401a.

| commit | what |
|---|---|
| `41ab243` | §1's prediction table, committed before any edit |
| `69aa522` | the shared-sentinel dispatch: `src/opt/scanedge.c` + `src/gen/emit_dfa.c` + one `limits.def` description |
| `bd333f5` | K43 (b), and the two `-Werror` defects the sweep found in the edge path |
| `54f454f` | `docs/spec/tuning.md` §2.18, `src/opt/CLAUDE.md`, `src/gen/CLAUDE.md` |
| `1af0b74` | `tests/codegen/run_scan_edge_dispatch.sh` — a DRAFT check, delivered RED and saying so |

`make -j2` and `make strict` are clean. No abi bump: §6 lists the sites and
the number is the manager's.

### 2.1 The mechanism, as built

Frank's ruling was "dead ∪ edge-head form ONE reserved sentinel range of
NON-STATES tested by the loop's EXISTING dead check". That is what is built,
in four pieces.

**(1) The renumbering** rides the compaction `src/opt/scanedge.c` already did:
the surviving states are permuted so the edge HEADS are the machine's TOP
rows, in their existing relative order. Precondition (7) — a chain whose
fall-through is another chain's head must have the smaller index — survives
because it compares two HEADS and their relative order is preserved. The
permutation is NOT monotone, unlike minimize.c's compaction, so it goes
through a scratch array; writing in place would clobber a state a head is
moving over.

**(2) The stop predicate.** A machine carrying at least one edge emits one
more accessor:

```c
static inline int rx_forward_is_stop(rx_forward_state s) { return (unsigned)s >= 192u; }
```

**NO TABLE BASE BIAS IS NEEDED, and that is the one place I departed from the
brief's letter to keep its substance.** The brief says to bias the table base
so sentinel-range ids still index their rows. That is the NEGATIVE-sentinel
variant. Putting the heads at the TOP of the row space satisfies the same
requirement — "edge heads must remain VALID TABLE ROWS for the fall-through
step" — with a bias of exactly zero, because the dead value already sits above
every live cell under BOTH representations: premultiplied dead is 65535 and
`PREMUL_MAX_ENTRIES` keeps the largest cell `(n-1)*ncls` below it; the indexed
form's dead is `-1`, whose UNSIGNED reading is `UINT_MAX`. So one unsigned
compare tests dead-or-head in both, `is_dead` keeps its name, its body and its
exact meaning, no table cell moves, and no `DfaRepr` field changes.

**(3) The loop.** The generic path is accept probe, prefilter, stay skips,
view select, viewed probe, bound, step, ONE stop test. The edge blocks moved
VERBATIM onto a path reached only from that test and from the loop's entry.
The prefilter MOVES there rather than being copied where `s0` is itself a head
(it fires at `s0` and nowhere else, so where `s0` is a head the generic path
can never hold it); the stay skips are not replayed at all (`pick_skip_states`
declines every state carrying an edge); the accept probe is the one statement
genuinely replayed.

**(4) A NEW PRECONDITION (8), and it is a soundness requirement rather than
tidying.** The deletion argument rests on "when the ordinary step runs, the
state variable never holds a chain head together with a byte of that head's
scan class". Under the old loop that held because the edge chain was evaluated
at every state. Under the new one the loop learns "this is a head" from THE
STEP'S RESULT, so anything else that WRITES the state variable mid-body
installs a head the edge block never sees. Exactly one thing does:
`pf_emit_ofs_reseed`, the offset-set prefilter's RESEED, which writes
`s1u[upc(s[cand-1])]` after skipping. Precondition (8) refuses a head that any
seed family names, which is exact, costs nothing on a machine with no seed,
and is this pass's standing posture (every precondition declines rather than
stretching).

### 2.2 K43 (b)

`<prefix>_run_state_init`'s loop became

```c
static const ptrdiff_t fa_unset_slots[FA_NSLOTS] =
    { [0 ... FA_NSLOTS - 1] = PCREC_UNSET };
__builtin_memcpy(run->slot_values, fa_unset_slots, sizeof fa_unset_slots);
```

`__builtin_memcpy` rather than `memcpy` so no artifact acquires a
`<string.h>` dependency it did not have; the artifact is gcc-dialect by design
and already uses `__builtin_expect`.

---

## 3. WHAT WAS MEASURED (all of it on single artifacts; no suite ran)

### 3.1 The structural acceptance

`objdump -d` of `rx_search`'s forward scan loop, gcc 15.2.0 `-O2`, this box.
The number is the GENERIC PATH: the instructions on the cycle a byte that
takes no edge, no prefilter and no skip walks.

| iso-ts forward loop | instructions on the generic path |
|---|---|
| main 9d8401a (4 forward edges) | 29 |
| this branch | 15 |
| `-fno-scan-edge` control | 19 |

The four per-edge compares are gone, and the loop is FOUR INSTRUCTIONS
SHORTER than the no-edge control as well — because `s0` is itself a head on
this pattern, so the candidate-start prefilter's own guard left the generic
path with them. `-fno-scan-edge`'s 19 is the pre-[OPT-5] loop.

**THE WIN SCALES WITH THE EDGE COUNT AND IS NIL AT ONE EDGE, which is worth
the manager's attention.** On `http-5xx`, whose forward machine carries ONE
edge, the generic path is 16 instructions before and 16 after: gcc lowers
`!is_stop` back into two equality tests (one against the head cell, one
against dead), which is exactly what the old loop paid. That is the mechanism
behaving as designed — it is O(1) in the edge count where the old one was
O(N) — and N = 1 is the degenerate case. `cls-upto-4` is even flatter: its
whole loop IS the edge, so `rx_search` disassembles identically before and
after.

### 3.2 Answers

| comparison | cells | disagreements |
|---|---|---|
| this branch vs main 9d8401a vs `-fno-scan-edge`, 8 edge-bearing patterns x 13 subjects | 104 x 3 arms | 0 |
| the same widened: 22 patterns x 21 subjects | 462 x 3 arms | 0 |
| this branch vs python3 `re` | 462 | 0 |
| this branch under TEN axes vs main 9d8401a (default, `-fno-start-pinned`, `-fno-premul-table`, `-fno-anchored-dfa`, `-fno-scan-edge`, `-fprefilter`, `--engine=vm`, `-fno-possessify`, `-fno-counter`, `-fno-revdet`) | 3,024 | 0 |
| VM HYBRIDS carrying edges (`-fprefilter`, 4 patterns x 7 subjects), where the loop is emitted inside `static rx_prefilter` | 28 | 0 |

The hybrid row is separate because it is the one population where the two
labels and the entry `goto` land inside a function that is not
`<prefix>_search`: `pcrec_emit_dfa_engine` is the same call, so the hybrid
gets the new loop by construction, and 3 of the 4 witnesses carry between one
and four edges.

Compilation: 149 artifacts across SIX axes (default, `--trace`,
`--engine=vm`, `-fno-scan-edge`, `-fprefilter`, `--engine=dfa`) built
`-Wall -Wextra -Werror`, 0 failures — after the two defects in F1 were fixed.

### 3.3 Byte identity where the transform is absent

17 patterns compiled `-fno-scan-edge` on both compilers with the SAME output
basename: 17 identical, 0 differing. At the default, the 9 patterns with no
scan edge are identical and the 8 edge-bearing ones differ. `uuid` and `ipv4`
are byte-identical artifacts.

### 3.4 Emitted bytes

| artifact | before | after | delta | edges | machines carrying an edge |
|---|---|---|---|---|---|
| iso-ts | 44,580 | 46,416 | +1,836 | 12 | 3 |
| http-5xx | 68,141 | 68,869 | +728 | 2 | 2 |
| cls-upto-4 | 18,468 | 19,554 | +1,086 | 2 | 2 |
| two-chain `[a-z]{2}[0-9]{2}` | 26,067 | 27,254 | +1,187 | 4 | 2 |
| ipv6 | 32,027 | 32,510 | +483 | 1 | 1 |
| uuid | 40,961 | 40,961 | 0 | 0 | 0 |
| ipv4 | 30,710 | 30,710 | 0 | 0 | 0 |

364 to 612 emitted bytes per machine that carries an edge, and zero for every
machine that does not.

### 3.6 The precondition-(8) census — PARTIAL, and the loglines half is closed

Ruling item 6 (manager, 2026-09-03 17:5x) asks how many artifacts LOSE an
edge to precondition (8). The corpus-wide half is tomorrow's, after
`make test` has built everything. The bench's `loglines` family is closed
tonight, from eleven single-artifact compiles inside the hold's allowance —
edges counted from each artifact's own `[OPT-5] SCAN EDGE` markers, main
`9d8401a` against this branch:

| artifact | main | branch | seed tables |
|---|---|---|---|
| iso-ts | 12 | 12 | 0 |
| http-5xx | 2 | 2 | 2 |
| ipv6 | 1 | 1 | 0 |
| uuid | 0 | 0 | 8 |
| ipv4 | 0 | 0 | 0 |
| kv-quoted | 0 | 0 | 4 |
| level-context | 0 | 0 | 4 |
| stack-frame | 0 | 0 | 6 |
| hex32-id | 0 | 0 | 6 |
| bignum | 0 | 0 | 6 |
| floor | 0 | 0 | 0 |

Nothing moved. SIX of the eleven carry seed tables, so precondition (8) was
LIVE on them and cost none of them an edge; iso-ts and ipv6 carry no seed at
all, so (8) structurally cannot reach them. The row's own acceptance cell
(iso-ts) and the two artifacts beside it in the family are therefore
unaffected, which is the constraint the ruling set.

**THE INSTRUMENT IS THE MARKER COUNT, NOT THE STAMP, and the ruling was
corrected on that.** There is no `RX_SCAN_EDGES` macro. `RX_DFA_SCAN_EDGE`
is axis I's BODY form (`"range"` / `"bitmap"` / `"none"`), so reading it
detects only an artifact dropping to ZERO edges — a machine going from four
to three keeps the value `"range"` and reads identical. Tomorrow's sweep
counts markers, and reports a stamp that went `"none"` separately as a total
loss.

**AND THE POPULATION IS BOUNDED, which the sweep asserts rather than
discovers.** (8) refuses a head that a SEED family names, and `dfa_needs_seed`
is true only where the interior start states differ by context class — the
`\b`, `(?m)` and `\G` shapes. An artifact with no seed table cannot lose an
edge to (8); one that appears in the moved set without a seed means (8) is
NOT the cause and something else moved.

### 3.5 K43

`gcc -fanalyzer -Wall -Wextra -Werror`, gcc 15.2.0, on every shape K43 names,
one at a time:

| shape | before | after |
|---|---|---|
| `(a*)*` + `tests/encseam/findall_driver.c`, `-O1` | CWE-457 at `FA_SET`'s trail save | clean |
| the same at `-O2` | — | clean |
| `--trace` artifact (`(a|b)+c`) | — | clean |
| `((a)|bc){0,40}d`, `(a{1,3}){65}`, `(\w+)\s+\1`, `^(a(?1)?b)$`, `(?>a*)b`, `(?<=foo)bar` | — | clean, all six |

**THE RUNTIME COST IS NOT LITERALLY ZERO AND I AM NOT GOING TO CLAIM IT IS.**
The object code of the initialization, `-O2`, on `(a*)*` (6 slots):

| | before | after |
|---|---|---|
| the constant | `pcmpeqd %xmm0,%xmm0` (all-ones in a register) | `movdqa 0x0(%rip),%xmm0` (a 16-byte load from `.rodata`) |
| the stores | 3 x `movups %xmm0,(%r8)` at 0, 0x10, 0x20 | identical, same three offsets |

Three 16-byte stores either way; the delta is ONE instruction per inlined
copy, a register-generated constant replaced by an L1-resident load, plus 48
bytes of `.rodata` per artifact. `__builtin_memset(run->slot_values, 0xFF, …)`
would recover the `pcmpeqd` exactly, and I did not use it: it hard-codes the
BYTE PATTERN of `PCREC_UNSET` and would break silently the day that value
stopped being a repeated byte, which is the coupling this tree records
failures about.

---

## 4. THE PREDICTION TABLE, SCORED

| prediction | outcome |
|---|---|
| **P1** the generic path's instruction count equals the `-fno-scan-edge` build's and is today's minus `2 x nscan` | **HIT, and better than predicted on both halves.** iso-ts 29 -> 15 (predicted 29 -> 21) against the control's 19. The extra saving is the prefilter guard leaving the generic path with the edges. |
| **P2** every zero-edge and every `-fno-scan-edge` artifact is byte-identical to main | **HIT.** 17/17 on the flag axis, 9/9 at the default. |
| **P3** answers identical on every corpus cell and axis | **OWED** — needs `make test` and `make test-axes`. 3,486 single-artifact cells over ten axes and the python oracle are 0-disagreement. |
| **P4** `-fanalyzer` clean on K43's shapes, and the initializer's object code is the loop's | **HALF HIT.** Analyzer clean on all eight shapes. The object code is NOT identical: same three stores, one `pcmpeqd` replaced by one `movdqa` load. §3.5. |
| the byte formula: +95 accessor, +150 scaffolding, +100 A, +330 B ONLY where `s0` is a head, 0 for C, 0 for D | **MISS, low by 20-70%.** Measured 364-612 per edge-bearing machine against a predicted 345 (+330 conditional). Two errors in opposite directions: the prefilter turned out to MOVE rather than be replayed, so its +330 never applies — and the scaffolding (two labels, `if/goto`, the entry jump, the accessor's comment) is bigger than +150. |
| iso-ts +1,020 source bytes | **MISS**, +1,836. |
| iso-ts -8 generic-path instructions | **HIT and then some**, -14. |
| http-5xx and cls-upto-4 -2 per edge removed | **MISS.** Both are 0. At ONE forward edge gcc already paid one compare and still pays one; on cls-upto-4 `rx_search` disassembles identically. §3.1. |
| the stamps do not move | **HIT.** `RX_DFA_SCAN_EDGE` names axis I's body form and `RX_DFA_TABLE` the representation; neither names a state number, a layout or a sentinel. No stamp value moved on any artifact measured. |
| `-fno-scan-edge`'s tuning text does not change | **MISS**, deliberately: §2.18 gained the new loop shape, precondition (8) and the three caller-visible consequences. The FLAG's meaning did not change. |

---

## 5. FINDINGS

**F1 — Two `-Werror` defects in tonight's own edge path, both found by a
sweep and neither visible to any answer check.** Generated C is compiled
`-Wall -Wextra -Werror` by the harness and by callers, so both were hard
failures on real corpus shapes.

  1. The `scan_edge` label is reached by FALL-THROUGH from the stop test, so
     on any artifact whose start state is not a head, nothing `goto`s it:
     `-Werror=unused-label`. It is now emitted only where the loop's entry
     jumps to it. Found by the `--trace` axis, which was simply the first
     `-Werror` compile of an edge-bearing artifact I ran.
  2. A machine ALL of whose states are heads has `FLOOR == 0`, and
     `(unsigned)s >= 0u` is `-Werror=type-limits`. `[a-z]*`'s forward machine
     is exactly that: one state, and it is the head. `is_stop` folds to the
     constant there, the way [CC-DIFF] folds a uniform table.

  Both are the reason the final sweep is 149 artifacts x six axes rather than
  a handful.

**F2 — THE BRIEF'S "1/2/8-EDGE LADDER" CANNOT BE BUILT ON ONE MACHINE.**
`PCREC_MAX_SCAN_EDGES` is 4, so a machine carries at most four edges; iso-ts's
"8 edges in `rx_search`" is 4 forward plus 4 reverse, in two different loops.
Tomorrow's ladder is therefore 1/2/3/4 per machine (§6).

**F3 — The mechanism is O(1) where the old one was O(N), so at N = 1 it is a
wash.** §3.1. `http-5xx` and `cls-upto-4` are unmoved in instructions and
larger in bytes. If the manager wants a number for those artifacts, the lever
is the emitted-bytes term, not this row.

**F4 — `PCREC_MAX_SCAN_EDGES` HAS CHANGED MEANING and has not been
re-measured.** Its own comment said "each one is a compare against the state
variable on the loop's generic path, so this is the same kind of budget
`pick_skip_states` spends four of". That is now false: the generic path
carries none. What remains is an emitted-bytes budget and a bound on the edge
path's own `if` chain. Both `src/opt/scanedge.c` and `src/core/limits.def` now
say so, and neither re-chooses the number (D77).

**F5 — A PRE-EXISTING HAZARD I LOOKED FOR AND COULD NOT WITNESS.** A chain
whose fall-through is DEAD makes the emitted edge block assign the dead
sentinel, after which the loop's tail runs the bound check and THE STEP before
the dead test — indexing the transition table with the dead value. This is
unchanged by tonight's work (the same order held before it), and I could not
construct a witness: eight candidate shapes produced no edge block assigning
the sentinel. Recording it, not hunting it — Frank's own ruling of this
morning on the o42 witness gap ("WAIT FOR A WITNESS: no row, no hunt").

**F6 — The draft check is red on two of four witnesses and the file says so.**
`tests/codegen/run_scan_edge_dispatch.sh` measures the generic path as a
shortest cycle in `rx_search`'s CFG. gcc hoists the byte-class table's address
load out of the loop on two of the four witnesses, so the anchor is not on any
cycle. Three repairs were tried and MEASURED (follow the register; the same
restricted to dereferences; `-fno-move-loop-invariants`) and all three are
recorded in the file's §6 with the wrong numbers they produced, so nobody
re-tries them blind. It is wired into no make target.

---

## 6. TOMORROW'S MEASUREMENT PROTOCOL (E6, written tonight, not run)

Sequencing is the row's own: the pair, then the ladder, then the floor.

**M0 — THE ACCEPTANCE PAIR.** Two ratios on the bench's `loglines` set at the
pinned tier, iso-ts the headline cell:
  - `pcrec-auto` (this branch) against `pcrec-auto-noedge` (this branch,
    `-fno-scan-edge`) — the row's BEFORE was **x1.089** at this exact
    comparison, and the acceptance is that it moves toward 1.000.
  - `pcrec-auto` (this branch) against `pcrec-auto` (main 9d8401a) — the
    direct before/after, which is the number the row's charter asks for and
    which the counterfactual above cannot give.
  `http-5xx` and `ipv6` beside it as the family, and `uuid`/`ipv4` as the
  byte-identical controls (they must read 1.000 to within noise, and a control
  that does not is an instrument fault, not a finding).

**M1 — THE LADDER, which splits the fixed-per-artifact cost from the
per-edge cost.** Four patterns whose FORWARD machine carries 1, 2, 3 and 4
edges over the same class, each verified by counting `[OPT-5] SCAN EDGE`
markers in the artifact before it is timed (F2: four is the ceiling):

| k | pattern | note |
|---|---|---|
| 1 | `\d{2}x` | |
| 2 | `\d{2}x\d{2}` | |
| 3 | `\d{2}x\d{2}x\d{2}` | |
| 4 | `\d{4}-\d{2}-\d{2}[T ]\d{2}` | iso-ts's own prefix |

Two subject families per k, because they measure different things: a
NON-MATCHING subject of 1 MB where the machine sits in ordinary states and no
edge ever fires (this is the ENTRY cost, which is what the row is about), and
the bench's loglines subject where they do. Fit `t(k) = a + b*k` on each
family for BOTH builds. The claim is `b_new ~ 0` while `b_old > 0`, with `a`
unchanged; a `b_new` indistinguishable from `b_old` means the dispatch is not
reaching the population.

**M2 — THE FLOOR LADDER, and it is measured on the NEW loop, never on the
old one** (the row's SEQUENCING ruling). Chains of `m` = 2, 3, 4, 6, 8, 12, 16
(`[a-z]{0,m}` and `[0-9]{m}` families), each timed default against
`-fno-scan-edge`, on a subject whose runs are drawn to straddle `m`. The
output is the `m` at which the edge starts paying under the new entry cost —
which is `PCREC_MAX_SCAN_EDGES`' sibling question and the input to a
`limits.def` row. NOTHING IS BUILT FROM THIS TOMORROW; it is the measurement
that would trigger the build.

**Method, for all three.** Interleaved paired rounds, 11 of them, medians
reported WITH the per-round range — [CC-DIFF] STEP 1's own lesson, where the
medians agreed with the scratch numbers and the per-round ranges crossed 1.0
on a quiet box, so a median alone would have overclaimed. `taskset` pinned,
box load below 0.5 before a round starts and checked between rounds, one
heavy thing at a time. M0's citable number comes from the BENCH, not from my
own harness; M1 and M2 are model measurements and are mine.

**Also owed tomorrow, before any of it:** `make test` (background, poll the
log), `make test-codegen`, `make test-axes` (~48 min), and `make test
LINTGEN=1` — K43's acceptance.

---

## 7. THE abi SITE LIST (D94), found by grep, NOT bumped

`rx_info.abi` is 17 on main. This branch is one abi event ([OPT-EDGE] STEP 1
and K43 (b) together — both are emitter changes on one landing, [CC-DIFF]
STEP 1's own precedent). The bump is a separate final commit tomorrow once the
manager gives the number. Every reader of 17, found by grepping the tree:

| site | what it is |
|---|---|
| `src/gen/emit_dfa.c:1603` | `".abi = 17,\n"` — the emitted value, and the only producer |
| `tests/codegen/run_codegen_tests.sh:2758` | `ABI_EXPECT=17` |
| `tests/codegen/run_codegen_tests.sh:2760` | the failure message's bump history, which gains a `17->18` clause naming BOTH halves |
| `tests/codegen/run_recursion_identity.sh` | `FILEPIN="${RECURSION_IDENTITY_FILEPIN:-a3f40b1}"` — gate (B)'s pin, re-pinned to the MERGE commit, plus its own comment block |
| `docs/spec/match_api.md:159` | "`rx_info.abi` is `17`" in the §6 abi paragraph |
| `docs/spec/match_api.md:1694` | "**`rx_info.abi` is `17` on every artifact today**", the per-bump narrative |
| `docs/spec/match_api.md:2148` | "the abi-17 entry above" — a cross-reference to the entry that documented [CC-DIFF]'s spelling (a). It names a HISTORICAL entry and most likely does NOT move; it is listed because D94's lesson is that the hand-enumerated list missed a fifth reader in this exact file. |

**What comparison (A) of `run_recursion_identity.sh` should do.** (A) extracts
`goto <p>_L0;` through `<p>_accept:` — the VM's own program. Nothing on this
branch is emitted inside that span: `emit_scan_loop` runs inside
`pcrec_emit_dfa_engine`, which for a hybrid is called from emit_vm.c's
prefilter block ABOVE the program marker, and a non-hybrid DFA artifact has no
`goto <p>_L0;` at all. K43's initializer is in `<prefix>_run_state_init`, also
above the marker. So (A) should be byte-identical and (B) re-pins. That is a
PREDICTION, not a measurement — the gate has not been run.

---

## 8. WHAT IS UNVERIFIED, AND WHAT NEEDS A RULING

**Unverified (the box hold; all of it is tomorrow's):** `make test`,
`make test-codegen`, `make test-axes`, `make test LINTGEN=1`, every timing
number, comparison (A) of the identity gate, and the corpus-wide byte-identity
claim for zero-edge artifacts (measured on 9 patterns, not on 2,700).

**Needs a ruling.**

1. **The abi number**, and whether K43 rides this event. I have assumed it
   does (the brief says so).
2. **`tests/codegen/run_scan_edge_dispatch.sh` — keep, fix, or drop.** As it
   stands it is red on half its witnesses. Its §6 item 1 says what a working
   version needs. My own view: the property is worth a gate and the anchor is
   the wrong instrument; identifying the loop structurally, or measuring the
   emitted C's basic blocks before gcc sees them, is the direction.
3. **`PCREC_MAX_SCAN_EDGES` (4) is now a different budget** (F4) and has not
   been re-measured. It is the ladder's ceiling in M1, so tomorrow's
   measurement bears on it directly.
4. **The `>=` in §3.1's acceptance.** The subject arm is SHORTER than the
   `-fno-scan-edge` control on iso-ts, not equal, because the prefilter left
   the generic path too. The draft check asserts `<=`; whether it should also
   bound how much shorter is open.
5. **F5's dead-fall-through hazard** — recorded with no witness, per this
   morning's ruling. If the manager wants it hunted, it is a separate row.
