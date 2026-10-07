# stc1 — [START-TABLE] C1: the selection trace

Lane stc1, 2026-10-07, opus. Branch `lane/stc1` off main `6d0177f8`, main
merged in once (`6f3266d7`, admin1007's S169 → S556 rename; no `.c` change).
Design: `docs/design/start_table.md` rev 2.1, §3.2 C1, §3.3 item 5, §6 Q3;
input lists: D151 addenda 1-3, `stc0_report.md` (§4 the two C1 conditions,
§6 the every-flag movers), and the kit's B1-B20
(`git show 4f2b401f:docs/dev/lanes/r4ccore_report.md` §3).

**Status:** the hook, the instruments' re-derivation and the edit-set table
are done and committed. The validation status is in §5, with what is
complete and what is OWED.

## 1. What landed

- **`PCREC_CAND_TRACE_REC(slot, route, row, site)`** and
  **`PCREC_CAND_TRACE_RECF(slot, route, site, fmt, ...)`**, in
  `src/core/internal.h` (end of file). Each prints one stderr line,
  `CANDTRACE <slot> <route> <row> <site>`, only under `-DPCREC_CAND_TRACE`.
  In the default build a record expands to `((void)sizeof("" site))`: no
  code, and its arguments are not evaluated.
- **Frank's condition 1 is enforced by the compiler, not by review.** `site`
  is pasted as `"" site`, so anything but a string literal fails to compile
  in BOTH builds. It caught one at once: the first draft's
  `d == &cx->job->dfa ? "form-fwd" : "form-other"` did not compile and became
  two literal records. There is no `__func__` field (the prototype's
  brittleness-only column is gone), so a record is 4 fields.
- **Frank's condition 2:** `scripts/emit_sweep.py --trace` now GATES on the
  SET compare (`trace_diff.compare(unordered=True)`). It prints the ordered
  compare after it as a non-gating DIAGNOSTIC. `--trace-ordered` swaps the
  two, and replaces `--trace-unordered`, which had no other caller.
  `trace_diff.py` itself is unchanged (its `--unordered` mode and the
  S552-S555 rows stand).
- **The records print only values the decision already computed** (or pure
  reads of the `Job`). This is the rule that keeps the trace build's emitted
  bytes equal to the default build's. An accessor asked for the first time
  inside a record would mark a fact `used` and move the facts listing.
  Stream 6 of the trace-vs-default sweep is the check (§5).
  - Two records re-ask something:
    - `pcrec_artifact_has_dfa_scan`, which reads `fit` and nothing else;
    - `pcrec_fact_start_anchor`, at `vm-bound`, the line before the
      decision's own ask of the same fact.
- **No existing anchor text and no `refactor_edit_set.tsv` `line` moved.**
  - `m6read_check_sab_anchors.py`: all 481 rows resolve (499 sites).
  - Every edit-set `line`/`token` resolves at the same count on main and at
    the tip. The first draft rewrote `dfa_engine_is_empty`'s
    `if (cx->job->engine == PCREC_ENG_ATTEMPT) return cx->job->dfa.n == 0;`,
    an edit-set line. This check caught it, and the record now sits beside
    the line instead.
  - Lines the default build changes, all behaviour-identical:
    - six walk `return` expressions are now a local, a record, and
      `return` the local (the C0 prototype's shape);
    - `attempt_cand`'s two returns;
    - `req_site_define`'s two early returns now have braces.
- **The records floor is re-pinned and a site-reach check is added.**
  `TRACE_RECORDS_FLOOR` was 89,135 / 38,523 (the C0 prototype's lower
  bounds). It is now **256,608 / 62,962**, the C1 hook's own count over the
  4,612 corpus rows (`runF.log`: a mirrored run of the trace build over
  streams 1-2, 131 s).

  New `TRACE_SITES`: on a full-population run every one of the 25 declared
  site keys must print at least once on the working side. A site whose
  record stopped printing would otherwise hide inside an arm's total (K35).
  All 25 are reached.

  Failing direction, replayed over `runF`'s streams: dropping `ofs-need`'s
  records reads NOT REACHED. It also trips the floor on both arms (255,615 <
  256,608; 62,297 < 62,962) and gives 1,447 SET movers.

  Records per site, c-default:

  | site | records |
  |---|---|
  | `prefix-k` | 82,648 |
  | `engine-empty` | 63,349 |
  | `search-start` | 26,567 |
  | `pf-of` | 18,373 |
  | `req-admit` | 14,533 |
  | … | … |
  | `scan-state` | 620 |
  | `attempt-bound` | 499 |

  c-vm reaches 13 keys; the other 12 are DFA-body sites, which a forced VM
  never asks.
- **`docs/design/start_table/call_graph.py`** skips `PCREC_CAND_TRACE_REC*`
  invocations, including multi-line ones, when it finds decision SITES. A
  record prints a decision and makes none. Without the filter the census
  grew from 155 to 168 sites, all of them the records' own ternaries. With
  it the tip reads 155, the same site set as main, and six lines are spelled
  differently (the walk returns above).

## 2. THE EDIT SET — C2's input (site keys, at tip `6f3266d7`)

Every row below prints ONE record per ask: `slot`, `route`, then the chosen
`row`, at `site`. The record line is the `PCREC_CAND_TRACE_REC` call; the
decision line is what C2-C5 rewrite.

Class column:
- **W** — a walk over a table (inventory WALK);
- **I** — an inline decision with no table;
- **R** — a route dispatch;
- **P** — a route-keyed payload (K65/K66);
- **L** — a landmark admission;
- **K** — the kit's boundary list.

The commit column is `refactor_edit_set.tsv`'s; **"—"** means the edit set
names no commit for that decision line (§3).

| site key | slot | rows printed | record (file:line) | decision read (file:line) | class | B-id | commit |
|---|---|---|---|---|---|---|---|
| `pf-of` | NEXT | `dfa_pfs[]` row name, route `dfa` | emit_dfa.c:6662 | `dfa_pf_of` 6658 (`dfa_pfs[]` 6617) | W | B10 | C3 |
| `vm-start` | NEXT | `dfa_pfs[]` row, route `vm` | emit_dfa.c:6692 | `vm_start_row` 6688 | W | B10 | C3 |
| `scan-state` | NEXT | `dfa_pfs[]` row | emit_dfa.c:7198 | `pcrec_dfa_scan_state_written` 7187 | W | — | C3 |
| `form-fwd` / `form-other` | NEXT | `dfa_pfs[]` row, forward / other machine | emit_dfa.c:8147, :8149 | `dfa_form_derive` 8146 | W | B10 | C3 |
| `search-start` | RECOVER | `dfa_search_starts[]` row | emit_dfa.c:7672 | `dfa_search_start_of` 7668 (table 7658) | W | — | C3 |
| `req-admit` | PRESENCE | `req_admits[]` row (`none`/`one-attempt`/`dominated`/`set-leads`/`emitted`) | emit_dfa.c:7034 | `req_admit` 7029 (table 7007) | W | B2 | C4 |
| `req-use` | FIRST | `req_uses[]` row (`handoff`/`scan-from-startpos`) | emit_dfa.c:7145 | `req_use` 7140 (table 7124) | W | B5 | C4 |
| `reseed` | RETRY | `pcrec_reseed_rows[]` name, route `vm` | emit_vm.c:11117 | `vm_plan_reseed` 11107 | W | — | C5 |
| `end-window` | WINDOW | `window` / `none` | emit_dfa.c:940 | `w < 0` emit_dfa.c:941 | I | — | C5 |
| `attempt-cand` | NEXT | `pred-memchr` / `none`, route `attempt` | emit_dfa.c:4023, :4045 | `attempt_cand` 4016 (`anchored` loop 4021, return 4044) | I | — | C3 (readers), C5b (loop) |
| `attempt-bound` | BOUND | `bot` / `gstart` / `all`, route `attempt` | emit_dfa.c:9159 | `a_bot`/`a_gst`/`anchored` emit_dfa.c:9125-9132 | I | — | C5 |
| `vm-bound` | BOUND | `anchored` / `gstart` / `all`, route `vm` | emit_vm.c:13474 | `start_anchor != NONE` emit_vm.c:13478 | I | — | C5 |
| `root-minw` | WIDTH | `ceiling` / `none`, route `vm` | emit_vm.c:13192 | `v->root_minw >= PCREC_MINW_MAX` emit_vm.c:13237 (stamp :11420, listing :9492) | I | — | C5 |
| `dfa-engine` | ROUTE | `dfa` / `attempt` (`job->engine`) | emit_dfa.c:10051 | `pcrec_emit_dfa_engine` 10049 | R | — | C3 (`cand_route_of`) |
| `entry-gate` | ROUTE | `entry` / `inlined` (`fit.chosen == ENGM_DFA`), route `dfa` or `attempt` | emit_dfa.c:8626, :8926 | emit_dfa.c:8625/8641 (`emit_unanchored`), 8925/8940 (`emit_attempt`); VM entry unconditional (emit_vm.c:13119, :13171, :13190) | R | B13 | — |
| `engine-empty` | ROUTE | `empty` / `live`, route `dfa` or `attempt` | emit_dfa.c:4272, :4277 | `dfa_engine_is_empty` 4269 | R | — | C3 |
| `run-tests` | PRESENCE | `none` / `window` / `whole-run`, route `dfa-scan` or `no-dfa-scan` | emit_dfa.c:1451 | K66: emit_dfa.c:1044 (`req_run_tests` 1030; B6's admission restatement :1040) | P | B6, B7 | — |
| `set-rest` | PRESENCE | `set-rest` / `none`, route class | emit_dfa.c:1455 | K65: emit_dfa.c:1312 (`req_set_rest_members` 1305; membership 1318-1328) | P | B7, B8 | — |
| `prefix-k` | NEXT | `nsel=N` | emit_dfa.c:4236 | `pcrec_prefix_ksets` (src/opt/prefix_k.c:179-326) called at emit_dfa.c:4235 | L | B11, B18 | outside (§2.5) |
| `req-site` | PRESENCE | `nothing` / `declined` / `byte` / `run` | emit_dfa.c:1432, :1436, :1447 | `req_site_define` 1424: :1431 (B1), :1435 (B2), :1439 (B3) | K | B1, B2, B3 | — |
| `req-gate` | PRESENCE | `none` / `byte` / `lead-optional` / `lead-required` | emit_dfa.c:1448 | :1440-1442 (`req_lead_byte`, its need by route) | K | B4 | — |
| `req-handoff` | FIRST | `assign` / `on-miss` | emit_dfa.c:1453 | :1445 (`req_use(cx) == REQ_USE_HANDOFF`) | K | B5 | — |
| `req-from` | FIRST | `handoff` / `scan-from-startpos` | emit_dfa.c:1557 | `pcrec_emit_req_byte_check` 1536: :1554 (B19), :1556 (B5′) | K | B5′, B19 | — |
| `ofs-need` | PRESENCE | per-term need signature (`r`/`s` + `R`/`O`, `*` on the plan's term) | emit_dfa.c:1085 (`ofs_pred_trace`, called :1134) | `ofs_pred_of` 1092-1131 | K | B20 | — |

Kit boundary entries with NO record, and why:
- **B9** (`emit_req_handoff_rest` 1176) — payload text. FIRST's `handoff`
  row decides whether it runs: `req-use`/`req-handoff`.
- **B12** — the kit's own form choice.
- **B14** (emit_dfa.c:8651) — a reader of FIRST's selection, which `req-use`
  prints.
- **B15** (emit_dfa.c:9784-9785, written :10016) — a reader of PRESENCE,
  printed by `req-admit`.
- **B16, B17** — stamps (PROJ): they project rows already printed.

`pf_scan_set_of` (emit_dfa.c:6670) is not a walk: it reads the row a walk
chose.

Every site is a DECISION read. None is in the kit's emitted search text
(D146/D147); `ofs_pred_trace` reads the `mf_pred` pcrec built, before it is
handed to the kit.

## 3. The instruments, re-derived on post-R4c main

- **`call_graph.py` → `call_graph.txt`**: 1,937 definitions, family 112, 155
  sites (main: 155; `def-*` line ranges moved with R4c).
- **`inventory.tsv`**: on post-R4c main `inventory_check.py` FAILED.
  - Five members were undispositioned: `emit_req_handoff_rest`,
    `req_note_run`, `req_set_rest_members`, `req_site_define`,
    `req_site_note`.
  - Three were in the inventory but no longer in the graph:
    `emit_req_handoff`, `emit_req_run_check`, `emit_req_set_rest`.
  - The R4c kit migration replaced the three pre-check emitters with these
    five. Re-dispositioned:

    | member | class | role |
    |---|---|---|
    | `req_site_define` | READER | PRESENCE then FIRST: the pre-check's decision reader, B1-B5 and B8 |
    | `req_set_rest_members` | EMIT | K65 |
    | `emit_req_handoff_rest` | EMIT | FIRST F1's payload |
    | `req_note_run` | EMIT | the kit's note hook, decides nothing |
    | `req_site_note` | EMIT | the kit's note hook, decides nothing |
    | `pcrec_emit_req_byte_check` | READER | re-noted: it is now only the use point, reading FIRST (B5′/B19) |

  - Now **127/127**, rc 0.
- **`sabotage_anchors.py`**: 481 row files, 499 sites, FAMILY 106, RE-AIM 15
  (C3 4, C4 2, C5 5, C5b 5), RE-RUN 91.
  - **Exit 2 on ONE unresolved site, and it is pre-existing on main**
    (verified on a `git archive 6d0177f8` tree): S526's second anchor, the
    file-scope `_Static_assert(MF_MAX_TERM >= …)` at emit_dfa.c:1089 (main
    :1070). The owner-resolution rules have no case for a file-scope
    `_Static_assert`. This is an instrument gap: S526 is OTHER either way
    (it guards the kit's C14 width), and nothing in C1 depends on it.
  - S169's start-family row is S556 since admin1007 (the RE-AIM line for
    `if (v->root_minw >= PCREC_MINW_MAX)`, C5).
- **`reader_grep.sh` → `reader_grep.txt`**: regenerated; two new lines, both
  in `memfn/docs/requests.md`.
- **`reconcile.py`**: unchanged: stamp keys 10/10 mapped, 5,192 hidden
  movers over 5 members, 0 OTHER rows naming the family.

### 3.1 Proposed edit-set additions (NOT written into `refactor_edit_set.tsv`; the C2 author or the manager decides)

The design says PRESENCE's payload absorbs K65/K66 as `u.admit.noscan`
(§2.2), but `refactor_edit_set.tsv` names no `line` for either decision. So
`sabotage_anchors.py` classes their rows RE-RUN when they will need RE-AIM:
- S277/S316: K65's `if (pcrec_artifact_has_dfa_scan(cx)) return;`;
- S278: K66's `if (pcrec_artifact_has_dfa_scan(cx) || r->whole_len <= r->len) return 1;`.

Proposed:

| kind | value | commit | why |
|---|---|---|---|
| line | `if (pcrec_artifact_has_dfa_scan(cx)) return;` | C4 | K65 reads PRESENCE's `u.admit.noscan` |
| line | `if (pcrec_artifact_has_dfa_scan(cx) \|\| r->whole_len <= r->len) return 1;` | C4 | K66 reads `u.admit.noscan` |
| line | `if (b < 0 && pcrec_fact_req_run(cx)->len < 2) {` | C4 | B1 RESTATES P1 `none`'s predicate (`req_none_applies`, emit_dfa.c:6951) inline. Deleting it ADDS a `req_admit` ask where nothing is necessary, so it is a declared ask-set change |
| line | `if (r->len < 2 \|\| !req_admit_emits(req_admit(cx)))` | C4 | B6, the same restatement inside `req_run_tests` |

The entry gate `fit.chosen == ENGM_DFA` (B13) is named by §0a as one of the
two route dispatches, but no commit's edit set touches it. The design keeps
it ("untouched" in the kit's B13). The record prints it so a C3 route change
that moved it would show.

## 4. What the design got wrong, or left stale

1. **"Every decision site `inventory.tsv` classes WALK or INLINE"** under-names
   C1's sites. The inventory has 6 WALK and ONE INLINE
   (`pcrec_emit_end_window_clamp`). The other inline decisions in §0a's own
   list are filed under other classes:
   - `attempt_cand` is PRED;
   - `start_max` and `attempt_max` sit inside BODY members;
   - the root-minw test sits in a BODY.

   C1 printed §0a's seven inline sites, the three inventory ROUTE members
   (plus `fit.chosen`), K65/K66, `nsel`, and the kit's B-list. Section 2's
   table is the list.
2. **The K65/K66 line citations** (`:1267`, `:1041`) and the
   `pcrec_emit_req_byte_check`/`emit_req_*` names are pre-R4c. They are now
   :1312 and :1044 in `req_set_rest_members`/`req_run_tests`, read by
   `req_site_define`.
3. **The inventory was stale after R4c** (§3). The design said the
   instruments re-derive it after R4c; on post-R4c main
   `inventory_check.py` exited 1, and nobody had re-run it.
4. **The edit set lacks K65/K66** (§3.1).
5. **§3.3 item 5's "printed at the walk's return"** holds at the walks. A
   multi-ask site multiplies records:
   - `prefix-k` prints on every `unanch_start` call, 21-38 times per compile
     in the samples;
   - `engine-empty` and `pf-of` likewise.

   The SET gate collapses these. The ORDERED diagnostic will be noisy for
   C3+, which change ask counts, so read it per site.

## 5. Validation

| check | result |
|---|---|
| `make strict`, default build | clean (before and after the main merge) |
| `make strict CFLAGS="-O2 -g -DPCREC_CAND_TRACE"` | clean |
| `scripts/m6read_check_sab_anchors.py` | all 481 rows / 499 anchor sites resolve |
| edit-set `line`/`token` resolution, main vs tip | identical counts, none lost |
| `inventory_check.py` (fresh `call_graph.txt`) | 127/127, rc 0 |
| `scripts/tests/emit_sweep.py.test` | 7/7 pass |
| `scripts/tests/trace_diff.py.test` | 17/17 pass |
| every-flag movers seen by the trace (below) | 20/20 arm cells: visible-but-not-traced = 0 |
| trace build vs default build, ALL six streams + `--arms start` | OWED (see 5.2) |
| default build vs main, `--arms start` + trace family | OWED (5.2) |
| records floor | re-pinned 256,608 / 62,962, all 25 site keys reached (`runF.log`); its gate run in A is OWED |
| failing-direction controls | OWED (5.2) |
| `make test-codegen`, `make test` (Mac, async, suite lock) | OWED (5.2) |

### 5.1 The every-flag movers (stc0_report §6)

Method: for each of the 3,598 distinct corpus patterns, compile with the
TRACE build at base and base+flag, in four arms. A stamp mover is
`es.start_keys_moved`, the gate's own definition. A trace mover is a changed
record SET. The script was scratch (`worktrees/stc1-scratch/movers_trace.py`,
log `movers_trace.log`).

Cells read `visible / traced`:

| flag | auto/byte | vm/byte | auto/utf8 | vm/utf8 | sites the trace moved |
|---|---|---|---|---|---|
| `-fno-possessify` | 6 / 6 | 9 / 9 | 6 / 6 | 9 / 9 | `req-admit`, `req-site`, `run-tests`, `req-gate`, `req-handoff`, `req-from`, `set-rest` |
| `-fno-altcls-merge` | 2 / 2 | 8 / 9 | 2 / 2 | 8 / 9 | as above, plus `req-use`, `ofs-need` |
| `-fno-altcls-factor` | 0 / 0 | 1 / 1 | 0 / 0 | 1 / 1 | as above |
| `-fno-premul-table` | 0 / 0 | 0 / 0 | 2 / 2 | 0 / 0 | `vm-start`, `set-rest`, `run-tests` |
| `-fno-cls-kit` | 0 / 0 | 0 / 0 | 3 / 3 | 1 / 1 | `reseed`, `vm-start`, `set-rest`, `run-tests` / the req family |

Readings:
- Every visible count equals stc0b's Linux sweep (6/9, 2/8, 0/1, 2 at utf8,
  3/1).
- **Every visible mover is a trace mover.** The trace sees the
  `REQ_WHY`/admission movement at `req-admit`, which is where C2's
  `cand_select` must read the VM frame verdict (`vm_frameless`,
  `req_route_one_attempt` emit_dfa.c:6893) through the same accessor.
- `-fno-altcls-merge`'s one extra traced pattern per vm arm is a mover with
  no start stamp. Its records move at `ofs-need`/`run-tests`: a pre-check
  term changed shape with no stamp naming it. It is exactly the class §3.3
  item 5 says the trace sees and stamps do not.

### 5.2 OWED (the long runs; chain in `worktrees/stc1-scratch/`)

Fill in the floor re-pin, the start_table.md C1 row and the numbers from
these logs. The completion lines are `B_RC=` / `A_RC=` in `chain1.log` and
`P_RC=` / `H_RC=` in `chain2.log`.
- **Run B** (`runB.log`): `emit_sweep --ref-bin <trace build> --bin
  <default build> --arms start`, all six streams and 32 arms × 2. This is the
  trace moving NO emitted byte, including the facts listing, which would see
  an extra fact ask.
- **Run A** (`runA.log`): `--ref 6d0177f8 --tree-rev 17dd805b --arms start
  --trace` with the trace build as both trace bins.
  - Default main vs default lane: 0 movers, no abi event.
  - The trace's stdout is compared with both sides' default builds.
  - The records-per-arm floor: TRACE_RECORDS_FLOOR's re-pin source.
  - `17dd805b` and the merged tip `6f3266d7` have identical `.c`/`.h`
    (`git diff --stat 17dd805b 6f3266d7 -- src lib cli memfn`: CLAUDE.md
    only), so these runs speak for the tip.
- **Run P** (`runP.log`), the failing-direction control: a planted
  bytes-identical row change (C0's D4c: `pcrec_dfa_scan_state_written`
  built with `.forward = false`) as the working trace bin. The SET gate must
  read FAIL. C0 measured 176 trace movers against 15 byte movers.
- **Run H** (`runH.log`), the hookless control: main's default build as both
  trace bins. The records floor must FAIL (0 < floor), and the site check
  must read 0/25.
- **Chain 3** (`chain3.log`) waits for chain 2 and then takes
  `worktrees/.mac-suite.lock` (a directory plus an owner file, released on
  exit). It runs `make test-codegen` (`codegen.log`, `CODEGEN_RC=`) and then
  `make test` (`maketest.log`, `MAKETEST_RC=`). Read the verdict from make's
  `*** [test-X] Error` lines. The standing darwin `nm arm_a.o` red and
  PC-3's U13 are expected.

Every path above is under `/Users/fdicostanzo/pcrec/worktrees/stc1-scratch/`.
All four chains are detached with `nohup` and `caffeinate`.

**Merge note:** R4c′ had not merged when the lane ended. When it does,
merge main into `lane/stc1` ALONE, resolve, run `make strict`, and re-run
Run B. My records in `pcrec_emit_req_byte_check`, `req-from` at :1557, sit
below R4c′'s :1505 insertion.
