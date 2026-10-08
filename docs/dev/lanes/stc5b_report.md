# stc5b — [START-TABLE] C5b: the four BOUND restatements become BOUND READERS

Lane stc5b, 2026-10-08, opus. Branch `lane/stc5b` off main `37462a8e` (C5 and
the kit's N4/g2floor merged). Design: `docs/design/start_table.md` rev 2.1
§3.2 C5b, §1.3, §1.6, §2.3 item 4, §3.5. Model: `stc5_report.md` (shape),
`stc3_report.md`/`stc4_report.md` §4 (rulings). The edit set and the anchor
derivation were re-derived on current main before any edit (§2).

**Status:** built and committed. On the light gates (§3): ZERO MOVERS, no abi
event, and the C1 trace identical record for record apart from the records
the design allows C5b to add (the four BOUND readers' own site keys, declared
in `docs/design/start_table/trace_declared_C5b.txt`). The heavy chain is
**OWED**: armed detached, waiting for `worktrees/stc5b/.lift` (§6).

## 1. What landed

Commits on top of `37462a8e`: `1d760c6c` (the readers), `568ea178` (re-aims,
S606), `039a6682` (instruments, the trace check's own function),
`afb63540` (the declared multiplicity), `d6a4ad24` (the strcmp check), plus
this report's commit (docs, plan, CLAUDE.md files).

- **The four restatements read BOUND through the walk.** Each asks BOUND's
  row on ITS OWN route and tests `u.bound.one != CAND_ONE_NONE`:
  - **P2** `one-attempt` (`req_route_one_attempt`): the VM arm on
    CAND_ROUTE_VM (B3/B4, the `start_anchor` fact); the DFA arm on
    `cand_route_of(cx)`, and only where that is CAND_ROUTE_ATTEMPT (B1/B2,
    `dfa_interior_dead`). That was the fifteenth `job->engine` test, the one
    C3 left for C5b; it now reads `cand_route_of` like the other fourteen.
    D-2b's split is kept exactly, since each arm reads its own route.
  - **N7** `first-class` (`pf_vm_start_applies`): the anchoring conjunct
    reads BOUND on the hat's own CandSel (route VM).
  - **R3** `anchored` (`cand_rs_anchored_applies`): BOUND on the RETRY
    selection's route (VM).
  - **N12** `pred-memchr` (`attempt_cand`): its own `anchored` loop is gone.
    `attempt_cand` now takes N12's `CandSel` (it took the `Dfa`) and reads
    BOUND on it (route ATTEMPT). The `d->n == 0` test still comes first, so
    an empty machine asks nothing (B1 would read `s1g`).
- **One selection read, not four.** `cand_read(reader, slot, sel, site)`
  (macro `CAND_READ`, the site a string literal as the trace's) is
  `cand_select(slot, sel, flags)` for a predicate of slot `reader`.
  `CAND_BOUND_ONE(reader, sel, site)` is its BOUND projection, through the
  existing `pcrec_cand_bound` accessor (the CandRow type is incomplete where
  `attempt_cand` sits). Forward-declared beside `cand_select`; defined after
  the hit counter.
- **The slot graph lists the reads.** `CandNode` gains `reads[CAND_NSLOTS]`,
  a `CAND_ON(route)` mask per read slot (§1.3's selection DAG as data):
  PRESENCE->BOUND (ATTEMPT, VM), NEXT->BOUND (ATTEMPT, VM), RETRY->BOUND (VM).
- **Every re-entry is a checked edge** (trace build only, so the default
  build compiles none of it):
  - `cand_read_hit` aborts with `CANDORACLE undeclared-read <reader> <slot>`
    on a read the graph does not declare on the read's route (new S606).
    Then it prints the read's own `CANDTRACE` record and counts its hit
    (`CANDROW`).
  - `cand_rows_selfcheck` also aborts on a read of a (slot, route) the slot
    is never asked on (`table-read-unasked`), and on a cycle in the reads
    (`table-read-cycle`), via a transitive closure over 8 slots.
  - Failing direction shown on scratch copies: drop NEXT's VM read ->
    `CANDORACLE undeclared-read NEXT BOUND first-class-bound` on `--engine=vm
    I`; add BOUND->RETRY -> `CANDORACLE table-read-cycle RETRY`.
- **Checks.** `tests/codegen/cand_rows_check.py` `[cand-no-name-strcmp]`'s
  receiver half covers `cand_read`/`CAND_READ`. On a scratch copy,
  `strcmp(CAND_READ(...)->tok, ss->name_probe)` (no literal) FAILs with the
  new check and passed with the old one. `run_cand_rows.sh` 3/0 on the tree.
- **Instruments re-derived** (`docs/design/start_table/`):
  - `call_graph.py`: two fixes, both byte-neutral on main `37462a8e` (the
    output there is identical, checked):
    1. a function-like macro's `#define` line is body past its parameter
       list. `CAND_READ` is one line, and without this the read had no edge
       to the walk: the four readers' "names" columns read EMPTY and
       `cand_read` was not a family member;
    2. "reaches a seed" is a fixpoint over the graph, not a memoized DFS. A
       predicate that reads another slot through the walk makes the graph
       cyclic through `cand_rows[]` (cand_select -> cand_rows -> predicate
       -> CAND_BOUND_ONE -> CAND_READ -> cand_read -> cand_select), and a DFS
       that answers false for a node on its own stack caches the false.
  - `call_graph.txt` regenerated: family 129 -> 132 (`cand_read`,
    `CAND_READ`, `CAND_BOUND_ONE`).
  - `inventory.tsv` 147/147 (the three in as WALK; the four readers' notes
    say they read BOUND).
  - `refactor_edit_set.tsv` amended with C5b's own `def`s (`cand_read`,
    `CandNode`, `cand_nodes`, `cand_rows_selfcheck`, `attempt_cand`), the
    stc5 §4 item 5 rule (name the text that changes).
  - `sabotage_anchors.{tsv,total}` post-C5b; `assert_reach.tsv` regenerated
    (it had last been written at revision 2.1).
- **Structural grep (§3.3 item 5).** Every C2-C5b `token`/`line` of the edit
  set reads 0 in `src/**/*.c|h`. The only hits are history sentences in
  `src/gen/CLAUDE.md` (`VRS_*`, `DfaSel`).
- **No spec hunk.** Nothing a caller can observe moved: no artifact byte, no
  stamp, no listing line (`--list-axes`/`-syntax`/`-limits`/`-schema`
  byte-identical, §3), no deny bit. `-fno-vm-anchor-bound` still empties the
  fact under P2's VM arm, N7 and R3, now through B3/B4 (start_table.md
  §3.5's "the reach is identical").

## 2. Sabotage rows

**Derivation on main `37462a8e`, before any edit** (`sabotage_anchors.py`,
output identical to the committed `.tsv`/`.total`): 509 row files, 527
sites, 115 family rows; re-aim C5b = **S269, S274, S276, S441, S492**
(the design's list; S441 is the row C5 already moved once); `rerun_at` C5b =
S491, S493, S496, S497. One unresolved site, pre-existing (S571,
`memfn_sites.c:35`).

**`--step C5b=37462a8e..HEAD`** (the commit's actual diff, PRE tree = a
`git archive` of main): 7 definitions edited, 13 reached, 1 pure-rename hunk
ignored; `rerun_at` C5b = S491, S493, S496, S497 (all `C5b:hunk`), the edit
set's own four. No reach-derived row beyond them.

**After C5b** (post tree): 510 row files / 528 sites, 116 family rows, all
anchors resolve (`m6read_check_sab_anchors.py`: 510 rows / 528 sites), 0
count mismatches. Re-aim C5b leaves exactly one: S606, the new row, which
sits in the C5b `def` `cand_nodes` by construction (S372's shape at C5).

| row | class | what changed | intent re-verified (plant on a scratch copy, probe) |
|---|---|---|---|
| S269 | re-aim | `req_route_one_attempt`'s new body; plant unchanged (always `false`) | `^abc$`: `RX_REQ_WHY` `one-attempt` -> `emitted` |
| S274 | re-aim | the VM arm's return now opens with `CAND_BOUND_ONE(...)`; plant drops K64's linearity conjunct alone | `--engine=vm ^([a-zA-Z0-9._%+-]+)+@`: `emitted` -> `one-attempt` |
| S276 | re-aim | whole function; the plant's VM arm is `return true`, its DFA arm the new text | `--engine=vm ([a-zA-Z0-9._%+-]+)+@`: `emitted` -> `one-attempt` |
| S441 | re-aim (C5, C5b) | `{ return 0 && CAND_BOUND_ONE(CAND_SLOT_RETRY, ...); }` | `^(?>a|ab): (.*)$`: `RX_VM_RESEED` `anchored` -> `adaptive-dense` |
| S492 | re-aim | the anchoring conjunct is the `CAND_BOUND_ONE` line; plant drops it | `^(ab)\1`: `RX_VM_START_SCAN` `none` -> `first-class` |
| S606 | NEW (`candoracle`) | NEXT's `reads` loses the VM route | trace build, `--engine=vm I`: `CANDORACLE undeclared-read NEXT BOUND first-class-bound`; clean trace build 0 |
| S491, S493, S496, S497 | re-run (derived, `C5b:hunk`) | `pf_vm_start_applies`' body changed around their anchors | — |
| S594-S600, S605 | re-run by judgment | the trace build's self-check and hit path gained the read; S597 is B3's predicate, now reached by four more readers | — |
| S81, S263, S270, S295 | re-run by judgment | S81: `attempt_cand`'s candidate set; S263: the VM bound text B3/B4 carry; S270: G1 reaches N12 through `attempt_next_of`; S295: the `vm-anchor-bound` flags leak | — |

S606 takes the next free id: S605 was the highest on main and every `lane/*`
branch. A concurrent lane taking S606 would be a merge renumber.

**Mech verdicts: OWED** (the chain's `MECH` lines, §6), ids WITHOUT suffix,
FATAL grepped per log. Every row's `SAB_EXPECT` is DETECTED except where the
row declares otherwise on main (S269's harness arm is expected green by its
own text; its prechecks arm is the detector).

**The after-C5b family sweep is NOT in the chain.** §3.5 re-runs the other
family rows (106 sites at main, 115 post-C5b) "once, as one mech sweep after
C5b". That is a long run (mech ~6 h for the whole matrix on Linux); it is the
manager's call to schedule (§4 item 4).

## 3. Identity gate

All builds are default builds against main `37462a8e` built from
`git archive` (`build/c5b/main`, `mainbuild_default`, `mainbuild_trace`); the
tip is `git archive HEAD` (`build/c5b/tip`, `tipbuild_default`,
`tipbuild_trace`). Scratch scripts `build/c5b/{quick,irq,quickdeny,trq}.py`
(stc5's, adapted: `JOBS`, and trq's declared filter). The box carried the
memfn session's heavy run throughout (load 40-68); the gates ran at 6 jobs.

| run | population | result |
|---|---|---|
| byte sweep, full distinct corpus | 4,378 patterns x 4 arms (auto/vm x byte/utf8), `.c`+`.h` at one `-o` basename, `--emit-facts=byte,utf8`, the four `--list-*` dumps | 16,026 compiled cells, **0 movers** (53 s) |
| `--emit-ir` (`--engine=vm`), full corpus + the three ceiling witnesses | 4,381 x byte/utf8 | 8,020 listings, **0 movers** (15 s) |
| deny arms, every 10th pattern | 438 x 14 flags (the start-family bits, `-fprefilter-collapse`, `-fno-length-prune`) x 4 arms | 22,288 compiled cells, **0 movers** (52 s) |
| C1 trace vs main's trace build, full corpus | 4,378 x 12 arms (the 4 base arms, `-fno-hyb-reseed`, `-fno-vm-anchor-bound`, vm `-fno-vm-anchor-bound`, `-fno-end-window`, `-fno-length-prune`, `-fprefilter-collapse`, utf8 `-fno-hyb-reseed`, `-fno-req-byte`) | 2,496,990 working records, 158,511 of them at the four declared site keys (one-attempt-bound 83,133, first-class-bound 53,724, pred-memchr-bound 17,056, retry-anchored-bound 4,598); after filtering them, **0 problems**: multiset AND ordered sequence identical, the reference side carries no declared key, bytes identical, 0 aborts (150 s) |
| `run_cand_oracle.sh` (tip trace build) | 42 witnesses | 46 / 0 |
| `run_cand_rows.sh` | | 3 / 0 (tip and worktree) |
| `inventory_check.py` | | 147 / 147 |
| `m6read_check_sab_anchors.py` | 510 rows / 528 sites | all resolve |
| `make` / `make strict` / trace build with `-Werror` | | clean |

**The trace's declared difference.** C5b adds one record per BOUND read, at
the reader's own site key: `one-attempt-bound` (P2, both arms; the record's
route field says which), `first-class-bound` (N7), `retry-anchored-bound`
(R3), `pred-memchr-bound` (N12), each `BOUND <route> <row> <site>`. After
filtering exactly those four keys, every pattern-arm's ORDERED sequence is
identical to main's, the reference side carries none of them, and all four
are observed (a stale declaration would fail). Records inside a quiet walk
(`cand_hit_every`'s cross-route check re-evaluates P2) print nothing, as
every record does. The ask set grows only by BOUND's own predicates
(`dfa_interior_dead` on ATTEMPT, the `start_anchor` fact on VM, which P2, N7
and R3 already asked), and `assert_reach.tsv` shows no BOUND predicate
reaching an assertion: (b) of §1.3 holds by the population.

## 4. What the design got wrong or left open (questions with recommendations)

1. **§1.3's other reads are not in `reads[]` yet.** The DAG table lists G1
   (PRESENCE reads NEXT), F1 (FIRST reads PRESENCE) and R4 (RETRY reads
   NEXT's scanned set). Those reads predate the selection read and go
   through their own functions (`dfa_cand_scan`, `req_admit`,
   `pcrec_dfa_cand_ppm`). Declaring them in `reads[]` without routing them
   through `cand_read` would be a declared edge nothing checks (a
   population nobody counts). **Recommendation:** route them through
   `cand_read` in C6 (or the commit that next touches each), declaring the
   edge in the same change; until then `cand_nodes`' comment says the graph
   lists the BOUND reads only.
2. **The call graph could not see the read** (§1, instruments). Both fixes
   are byte-neutral on main, and both are general (any one-line macro; any
   cycle). **Recommendation:** accept. A later commit that adds a read
   through the walk gets correct family/seed reach with no instrument edit.
3. **`attempt_cand` changed its signature** (`const CandSel *` for the
   `Dfa`). The edit set named only its loop line. Its one caller is N12's
   predicate, so nothing else moved. **Recommendation:** accept; amended in
   the edit set with the reason.
4. **The after-C5b family mech sweep** (§3.5: the other rows "re-run once,
   as one mech sweep after C5b") is a full-matrix-sized run. It is not in
   this lane's chain. **Recommendation:** schedule it as its own heavy slot
   after C5b merges, or fold it into the next full mech battery; the 22
   rows in the chain are the ones C5b's diff and walk changes reach.
5. **The trace record format is spelled twice.** `cand_read_hit` writes the
   `CANDTRACE` line with `fprintf` because its site is a parameter, and
   `PCREC_CAND_TRACE_REC` requires a literal. `cand_hit` already does the
   same for `CANDROW`. **Recommendation:** accept; the literal rule is kept
   at the call site (`CAND_READ`'s `"" site`).

## 5. Spec hunks

None. Nothing caller-observable moved (§1, last bullet; §3's dumps).

## 6. The detached chain (OWED)

`build/land/chain.sh`, armed by a `nohup setsid` waiter that polls
`worktrees/stc5b/.lift` every 30 s and then runs the chain. Everything logs
under `build/land/`; the completion lines go to `build/land/verdict.txt`:

- `SWEEP_RC=`: `emit_sweep.py --arms start` over the full corpus, tip vs
  main default (`sweepA.log`). Must read 0 movers.
- `TRACE_RC=`: `emit_sweep.py --trace` (streams c-default/c-vm) with
  `--trace-declared tip/docs/design/start_table/trace_declared_C5b.txt`
  (`sweepT.log`): the SET gate, the ordered diagnostic, the records floor and
  the 25 declared C1 site keys reached.
- `CODEGEN_RC=` (`codegen.log`).
- `MAKETEST_RC= wall=` and `MAKETEST_VERDICT_LINES n` (`mt.log`); the verdict
  is `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`, 0 lines = green.
  `docs/dev/artifact_size_log.tsv` is restored after.
- `MECH <id> rc= <trailer>` for the 22 rows of §2 (`mech_<id>.log`), a
  `MECH_FATAL <id>` line if the log has FATAL, then `MECH_DONE` and
  `CHAIN_DONE`; `build/land/DONE` is touched.

The tip is `git archive HEAD` at lift time. A fresh agent fills §2's mech
verdicts and §3's heavy rows from `verdict.txt` and the per-step logs, and
justifies any UNDETECTED/UNREACHED row against its own `SAB_EXPECT`.

## OWED

- The heavy chain above, all of it.
- §4 items 1 and 4 are for a ruling; the rest are recommendations to accept.

## STATE AT HANDOFF

- Branch `lane/stc5b`; code, checks, instruments and docs committed; this
  report's commit is the tip.
- Light gates COMPLETE and green (§3): zero movers, trace identical apart
  from the declared four site keys, no abi event.
- Heavy chain ARMED, NOT RUN: waiter PID 3904935, SID 3904935 (`nohup setsid bash -c 'until [ -f WT/.lift ]; ...; bash WT/build/land/chain.sh'`, confirmed with `ps -o pid,sid,args`); waits for
  `worktrees/stc5b/.lift`, then `build/land/chain.sh`; ends with
  `CHAIN_DONE` in `build/land/verdict.txt`.
