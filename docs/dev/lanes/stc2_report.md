# stc2 — [START-TABLE] C2: implement the one start table

Lane stc2, 2026-10-07, opus. Branch `lane/stc2` off main `9a66d8bb` (main
has since gained docs only). Design: `docs/design/start_table.md` rev 2.1,
§1, §2.2-§2.3, §3.2 C2, §3.3 items 6-7, §3.4; D151 addenda 1-3, D152;
input: `stc1_report.md` §2 (the edit set, re-derived here on the tip).

**Status:** built and committed. Default build byte-for-byte unchanged by
construction (no reader switched) and by the checks in §5; the both-walks
oracle is clean on the 42 named witnesses in both orders and on two corpus
samples; its failing direction is measured (S594-S599 all DETECTED). The
full-corpus runs, `make test-codegen` and the Mac `make test` are OWED, in
one detached chain (§6).

## 1. What landed

- **`CandRow`, `cand_rows[]`, `cand_select`, `cand_route_of`**
  (`src/gen/emit_dfa.c`, the section after `dfa_search_is_pinned`), and in
  `src/core/internal.h` the `CandSlot` enum (§1.2's eight slots),
  `CandVmFacts` (the five `Vm` values rows read: `root_minw`, `mrl_win`,
  `nclamp`, `has_push`, the class's reseed gap) and `CandRoute`, moved there
  from `emit_dfa.c` and given its third value `CAND_ROUTE_ATTEMPT` (DFA = 0
  and VM = 1 unchanged).
- **`CandSel`** is `DfaSel` renamed, with one new field `vm`
  (`const CandVmFacts *`); `typedef CandSel DfaSel` keeps every existing
  spelling. Every existing initializer is designated, so `vm` is NULL there.
- **The row** carries: `c` (identity, deny, predicate — `DfaCand`, so the
  predicates are today's functions by pointer), `slot`, `routes` (written on
  every row), `tok` (today's spelling, §4 item 1), `map` (§1.4), `giveup`
  (§1.5), `hands` (§1.6, a `CT_*` set), `list[route]` (§1.1's per-route
  `{axis, order, listed name}`), and `was` — the ORACLE's link to the old
  table row it restates, deleted with the old tables at C3-C5.
- **`cand_nodes[]`** holds `accepts` per slot and for the three non-slot
  successors (VERIFIER, LOOP, CALLER), the routes each slot is asked on
  (§2.3's route-class table), and each slot's successors (§1.6's edges).
- **Nine new predicate functions** for the inline decisions (§2.3 item 1):
  W1 `cand_window_applies`, H1 `cand_ceiling_applies`, N12
  `cand_pred_memchr_applies` (calls `attempt_cand`), R1-R4 (the four
  `vm_reseed_holds` tag arms), B1-B4. Every other row's predicate is the old
  row's function.
- **No reader switched.** `cand_select`, `cand_route_of` and `cand_nodes[]`
  carry `__attribute__((unused))` until C3; nothing in the default build
  calls them, and `call_graph.py` confirms it (§5).

### 1.1 The both-walks oracle (trace build only)

At every old start decision, `-DPCREC_CAND_TRACE` also asks `cand_select`
for the same (slot, route) and aborts (`CANDORACLE` line, `abort()`) unless
it chose the same row: by POINTER to the old table row where the decision is
a walk (`was`), and by today's spelling (`tok`) always. Thirteen sites: the
eight walks (`dfa_pf_of`, `vm_start_row`, `pcrec_dfa_scan_state_written`,
`dfa_form_derive`, `req_admit`, `req_use`, `dfa_search_start_of`,
`vm_plan_reseed`) and the five inline decisions (end-window, `attempt_cand`,
`emit_attempt`'s bound, the VM entry's root-minw and `attempt_max`). WINDOW,
whose site prints route `-`, is checked on every route the slot is asked on.
A fourteenth hook holds `cand_route_of` to the body dispatch
(`pcrec_emit_dfa_engine`).

- **Both orders** (§3.3 item 6): the default trace build asks the old
  decision first; `-DPCREC_CAND_NEW_FIRST` asks `cand_select` first, so a
  predicate's first-ask side effects land on the new walk.
- **Quiet.** The oracle's walk runs with a trace-build-only thread-local
  depth (`pcrec_cand_trace_quiet`, `src/core/internal.h`) raised, so a
  predicate that itself walks (F1 asks PRESENCE, P3 and R4 ask NEXT, N12 is
  `attempt_cand`) prints no extra record and is not re-checked. The
  `CANDTRACE` stream stays C1's record for record.
- **Self-check.** Every checked decision also runs `cand_rows_selfcheck`:
  slot order (one block per slot), unique identities, every row routed only
  where its slot is asked, totality per asked (slot, route) (§1.3), `hands`
  within the slot's successors' `accepts` (§1.6), unique (axis, order)
  listings. This is §3.5's planned structural checks, in C rather than in
  `cand_rows_check.py`, while the table has no reader.
- **The hit counter** (§3.4): each checked decision prints
  `CANDROW <slot> <route> <identity> <site>` to stderr. Trace tooling reads
  `CANDTRACE` lines only, so it ignores these.
- **Witness script:** `tests/codegen/run_cand_oracle.sh` builds both trace
  compilers from a tree and compiles `tests/codegen/cand_oracle_witnesses.tsv`
  (42 lines: every row identity, plus the deny landings) with each. A line
  passes when both builds compile with no abort and both print a `CANDROW`
  for its row. Coverage is K35-checked against the table's own source.
  `make test-cand-oracle` (in `TEST_SECTIONS`, its own section for
  `test-premul-table`'s smoke reason, ~50 s); mech arm `candoracle`.

## 2. The 37 rows and today's sites

Identity = `c.name` (unique); tok = today's spelling where it differs.

| # | identity (tok) | slot | routes | today's site | predicate |
|---|---|---|---|---|---|
| W1 | `window` | WINDOW | D A V | `pcrec_emit_end_window_clamp` `w < 0` | `cand_window_applies` (new) |
| W2 | `window-none` (`none`) | WINDOW | D A V | same | `cand_always` |
| P1 | `presence-none` (`none`) | PRESENCE | D A V | `req_admits[0]` via `req_admit` | `req_none_applies` |
| P2 | `one-attempt` | PRESENCE | D A V | `req_admits[1]` | `req_one_attempt_applies` |
| P3 | `dominated` | PRESENCE | D A V | `req_admits[2]` | `req_dominated_applies` |
| P4 | `set-leads` | PRESENCE | D A V | `req_admits[3]` (deny 45) | `req_set_leads_applies` |
| P5 | `emitted` | PRESENCE | D A V | `req_admits[4]` | `cand_always` |
| H1 | `ceiling` | WIDTH | V | VM entry's `root_minw` test | `cand_ceiling_applies` (new) |
| H2 | `width-none` (`none`) | WIDTH | V | same | `cand_always` |
| F1 | `handoff` | FIRST | D A V | `req_uses[0]` via `req_use` (deny 46) | `req_handoff_applies` |
| F2 | `scan-from-startpos` | FIRST | D A V | `req_uses[1]` | `cand_always` |
| N1-N11 | the eleven `dfa_pfs[0..10]` names | NEXT | D (N7: V) | `dfa_pfs[]` via its four walks | the `pf_*_applies` functions |
| N12 | `pred-memchr` | NEXT | A | `attempt_cand` | `cand_pred_memchr_applies` (new) |
| N13 | `next-none` (`none`) | NEXT | D A V | `dfa_pfs[11]` / `attempt_cand` false | `cand_always` |
| R1 | `exact` | RETRY | V | `pcrec_reseed_rows[0]` via `vm_plan_reseed` | `cand_rs_exact_applies` (new) |
| R2 | `clamped` | RETRY | V | `[1]` | `cand_rs_clamped_applies` (new) |
| R3 | `retry-anchored` (`anchored`) | RETRY | V | `[2]` | `cand_rs_anchored_applies` (new) |
| R4 | `adaptive-dense` | RETRY | V | `[3]` (deny 37) | `cand_rs_dense_applies` (new) |
| R5 | `adaptive` | RETRY | V | `[4]` (deny 37) | `cand_always` |
| R6 | `fixed` | RETRY | V | `[5]` | `cand_always` |
| B1 | `bot` | BOUND | A | `emit_attempt`'s `anchored` | `cand_bound_bot_applies` (new) |
| B2 | `attempt-gstart` (`gstart`) | BOUND | A | `emit_attempt`'s `a_bot` | `cand_bound_gstart_attempt_applies` (new) |
| B3 | `vm-anchored` (`anchored`) | BOUND | V | VM entry, `start_anchor == BOT` | `cand_bound_anchored_vm_applies` (new) |
| B4 | `vm-gstart` (`gstart`) | BOUND | V | VM entry, `== GSTART` | `cand_bound_gstart_vm_applies` (new) |
| B5 | `all` | BOUND | A V | both, fallback | `cand_always` |
| S1 | `pinned` | RECOVER | D | `dfa_search_starts[0]` (deny 22) | `start_pinned_applies` |
| S2 | `reverse-pass` | RECOVER | D A | `dfa_search_starts[1]` | `cand_always` |

N1-N11 keep `dfa_pfs[]`'s names, deny bits and order (N1/N2 deny 16|32,
N3/N4 16, N5-N7 47). Listings: W/P/F/N/S on the DFA route, N7, R and B3-B5
on the VM route, N12 and H none.

## 3. Oracle evidence (in hand)

| run | population | result |
|---|---|---|
| `run_cand_oracle.sh`, both orders | 42 witness lines, 37 rows | 88 / 0 (89 / 0 with the build step); every row reached on both builds |
| corpus sample, old-first (`worktrees/stc2-scratch/hits.py`, every 20th distinct pattern) | 182 patterns × 5 arms (auto/vm × byte/utf8, `-fno-hyb-reseed`) | 0 aborts, 0 rc or byte differences vs the default build; 32 rows hit |
| corpus sample, new-first | 182 × 4 arms | 0 |
| after the route oracle, both orders | every 40th, 91 × 3 arms | 0 / 0 |
| hit counter vs stamps (`xcheck.py`, every 40th, 3 arms) | REQ_WHY, DFA_START, VM_START, VM_START_SCAN, VM_RESEED | 31 relations, 0 differing |

The stamp side of the cross-check is read from the DEFAULT build's artifact
bytes, so it shares nothing with `cand_rows[]` or the trace.

**The failing-direction control** (mech, `PROCS=2`, all `DETECTED`, tree
`0db889a4`; log `worktrees/stc2-scratch/` copy of `mech_s594.log`):

| row | plant | candoracle |
|---|---|---|
| S594 | N9 `memchr` reads the memchr-bounded predicate (the brief's planted predicate difference) | 26 fail / 63 pass |
| S595 | N12 routed on DFA instead of ATTEMPT (route mis-key) | 2 / 87 |
| S596 | P4's deny bit dropped | 2 / 87 |
| S597 | B3 tests GSTART (an inline restatement wrong) | 14 / 75 |
| S598 | RETRY's fallback made deniable (totality) | 84 / 5 |
| S599 | H1 hands CAND (handoff type) | 84 / 5 |

## 4. What the design got wrong, or left open

1. **`c.name` "unique across `cand_rows[]`" (§1.1) vs §2.2's names.** §2.2
   names four rows `none`, two `anchored`, two `gstart`. Built: identities
   are unique (`window-none`, `presence-none`, `width-none`, `next-none`,
   `retry-anchored`, `vm-anchored`, `attempt-gstart`, `vm-gstart`) and a
   `tok` column keeps today's spelling, which the trace and the oracle use.
   N12's `tok` is its identity `pred-memchr` (C1's record spelling); its
   STAMP projection is still `"memchr"` (D-1), which C3/C5's `stamp` column
   must carry separately.
2. **§1.2's `accepts` do not type-check §1.6's own edges.** FIRST accepts
   only HIT, but E2 hands it LOWER and F2 scans from it: built as
   HIT | LOWER. VERDICT has no accepting successor: the CALLER accepts it
   (NOMATCH is returned there). RECOVER accepts LOWER (the END is not a
   handoff type). The check is "every handed type is accepted by some
   successor", not per-edge, because P1-P3 hand no HIT to FIRST.
3. **"NEXT hands CAND (+ WINDOW from a hybrid's prefilter)"** is a property
   of the route CLASS (E6), not of any row; N rows hand CAND.
4. **§1.3's `cand_select(slot, route, s, flags)`** carries the route twice.
   Built as `cand_select(slot, s, flags)` with `s->route`. §3.5's planned
   check "every CandSel initializer names `.slot`" then has nothing to
   check: `slot` is the walk's argument, not `CandSel`'s field.
5. **"inventory_check against a fresh call_graph (the family changes only by
   the edit set's definitions: C2's new ones in)"**: the family is
   reach-from-the-emitters, and C2's definitions have no reader. So
   `call_graph.py` gained `TABLE_ROOTS = ["cand_select"]`: the table, the
   walk, the nine new predicates and the row types join at C2 (127 -> 141,
   all dispositioned). `cand_route_of` reads `job->engine`, no seed, so it
   is not a member; the edit set's `def cand_route_of C2` is its only line.
   `call_graph.py` also skips the trace-only code (`#ifdef PCREC_CAND_TRACE`
   to its `#else`/`#endif`) and the oracle hooks (`CAND_ORACLE_*`,
   `VM_CAND_*`), as C1 taught it to skip records: sites 156 -> 162, the six
   new ones all inside `cand_select` and the new predicates.
6. **The payload `u` is not in C2.** Each of C3-C5 moves its old table's
   fields into `u` when it deletes the table; holding copies now would be a
   second home for the same data until then. `was` is the C2-only link.
7. **N12's site has no `Ctx`** (`attempt_cand(const Dfa *, CandSet *)`): the
   oracle walks there with no deny bits, exact because neither N12 nor N13
   carries one.
8. **Route-free listings** (W, P, F) sit on `list[CAND_ROUTE_DFA]`; C6's
   projection rule must read "the first route the slot is asked on".
9. **S594-S599 are detected only while the old decisions exist.** As C3-C5
   delete a slot's old walk, its oracle hook goes with it; each commit must
   re-home or retire the rows on its slot. `sabotage_anchors.py` classes them
   RE-RUN `after-C5b` because the edit set predates them; the C3 author
   re-derives.
10. **`refactor_edit_set.tsv` names no line for C2's two edits to existing
    text**: `typedef struct DfaSel {` / `} DfaSel;` (now `CandSel`) and the
    `CandRoute` enum's move. Neither is a sabotage anchor (grep, 0), and all
    42 `line`/`token` entries resolve at identical counts on main and the tip.
11. **One anchor collision, avoided.** `cand_rows[]`'s N2 line first read
    `PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER, pf_run`, a third match
    of S283's anchor (`SAB_COUNT=2`); the line is broken after the deny so
    S283 keeps its count until C3 re-aims it.

## 5. Validation run

| check | result |
|---|---|
| `make strict`, default build | clean |
| `make strict CFLAGS="-O2 -g -DPCREC_CAND_TRACE"` | clean |
| same plus `-DPCREC_CAND_NEW_FIRST` | clean |
| `scripts/m6read_check_sab_anchors.py` | all anchors resolve (491 rows, 509 sites) |
| edit-set `line`/`token`, main vs tip | 42 / 42 identical counts |
| `call_graph.py` + `inventory_check.py` | 141 / 141, rc 0; sites 162 (156 + 6 new, §4 item 5) |
| `sabotage_anchors.py` | 491 files, 509 sites, family 113, re-aim 15, re-run 98, count mismatch 0, unresolved 0, OTHER rows naming the family 0 |
| `reconcile.py` | clean (stamp keys 10/10, 5,192 hidden movers over 5 members) |
| `run_cand_oracle.sh` | 89 / 0 |
| mech S594-S599 | 6 / 6 DETECTED |

## 6. OWED — the detached chain

Chain: `worktrees/stc2-scratch/chain.sh`, log `chain.log`, completion lines
`A_RC=`, `O1_RC=`, `O2_RC=`, `H_RC=`, `X_RC=`, `CODEGEN_RC=`,
`MAKETEST_RC=`. It takes `worktrees/.mac-suite.lock` for each heavy step.
All binaries are built from the committed tip (`git archive`), never from the
worktree's `build/`.

- **Run A** (`runA.log`) — THE BAR: `emit_sweep --ref main --bin <C2
  default> --arms start`, all six streams and 32 arms × 2. Must read 0
  movers.
- **Run O1** (`runO1.log`) — old-first oracle build as the working binary
  against the C2 default build, `--arms start`, plus `--trace` against
  main's C1 trace build: no abort anywhere (an abort is an asymmetric row),
  0 movers, trace SET gate clean, records floor and 25/25 site keys.
- **Run O2** (`runO2.log`) — the same with the new-first build.
- **Run H** (`hitsH.tsv`, `hitsH.log`) — the hit counter over every distinct
  corpus pattern, 12 arms (auto/vm × byte/utf8 and eight deny arms), plus
  default-vs-oracle identity; **X** (`xcheck.log`) its stamp cross-check.
  Rows with zero hits in every arm are UNPROVEN-BY-SWEEP and have a witness
  in `cand_oracle_witnesses.tsv`.
- **`make test-codegen`** (`codegen.log`) then **`make test`**
  (`maketest.log`), under the lock. Read the verdict from make's
  `*** [test-X] Error` lines; the darwin reds named in BOILERPLATE (PC-3's
  U13) are expected.

Fill §3 and §5 from these logs; the start_table.md C2 outcome paragraph
names the same paths.

## 7. Merge notes

`src/gen/emit_dfa.c` gained one section (after `dfa_search_is_pinned`), a
forward block (after `dfa_search_is_pinned`'s forward declaration) and one
line before/after each of the thirteen decisions; `emit_vm.c` gained the
`VM_CAND_*` block before `VmReseed` and three hook pairs. The kit's M1b
touches `emit_dfa.c` only at a helper flush (~:9955 on main); no overlap
expected. On a main merge: merge alone, `make strict` in all three builds,
re-run `run_cand_oracle.sh`, `call_graph.py` + `inventory_check.py`, the
anchor tripwire, then the chain.
