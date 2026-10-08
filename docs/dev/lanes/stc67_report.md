# stc67 — [START-TABLE] C6 and C7: the listing reads the table; refactor A complete

Lane stc67, 2026-10-08, opus. Branch `lane/stc67` off main `f5d3547d` (C5b
merged). Design: `docs/design/start_table.md` rev 2.1 §3.2 C6/C7, §1.1, §1.3,
§2.4 D-3, §3.5, §3.7. Models: `stc5_report.md`, `stc5b_report.md` (shape,
instruments, chain), and the §4 rulings of stc3/stc4/stc5/stc5b. Added scope,
by the manager's ruling on stc5b §4 item 1: route §1.3's reads G1, F1 and R4
through `cand_read` and declare each edge in `CandNode.reads[]` in the same
commit.

**Status.** Built and committed. C6 is zero movers. C7 is the DECLARED
listing commit: stream 5 only, and NOT an abi event. The design says so
(§3.1, "The exceptions are C7, a declared stream-5-only change"; §3.2's C7
row; §3.7, "At C7 only `kind` and one `desc` change"). The tree agrees: C7
moves no emitted byte, `--emit-ir` listing or `--emit-facts` listing, so
nothing an artifact carries moves. **Refactor A (C0-C7 with C5b) is
complete.** The light gates are green (§3). The heavy chain is **OWED**: it
is armed detached and waits for `worktrees/stc67/.lift` (§6).

## 1. What landed

| commit | what |
|---|---|
| `41c5410b` | C6, the listing reads the table |
| `7ad018d2` | C6, G1/F1/R4 read through `cand_read`, each edge declared; S607-S610 |
| `dee6f5f9` | C6 instruments: edit set, call graph, inventory, anchors |
| `103b07a4` | C7, the declared listing commit; spec hunk |
| (this report's commit) | post-C7 instruments, plan, CLAUDE.md files, design note, report |

**C6, the listing.**
- **One projection.** Every start axis's `--list-axes` rows are
  `cand_rows[]`'s rows listed under it. The seven axes are `prefilter`,
  `search-start`, `req-admit`, `req-use`, `hyb-reseed`, `vm-anchor-bound` and
  `end-window`. One accessor, `pcrec_cand_list_row(axis, i, &row)`, projects
  them in table order, and one dump emitter, `emit_cand_axis`, prints them.
  `cand_list_stamp` returns the row's SLOT's stamp on the listed route
  (NEXT is `RX_DFA_PREFILTER`, or `RX_VM_START_SCAN` on the VM route).
  `cand_list_value` returns the stamp writer's spelling:
  - PRESENCE: `req_why_name`;
  - FIRST: `""` or `none`;
  - WINDOW: `""` or the listed name;
  - every other slot: the listed name.
- **`desc` beside the row** (`CandRow.desc`, §1.1). The text moved VERBATIM
  from `axes_dump.c`'s `AXIS_DESC` start rows, from the hand-stated
  `vm-anchor-bound`/`end-window` texts, and from the PRESENCE/FIRST/RETRY
  payloads (`CandAdmit`/`CandUse`/`CandReseed` lose `desc`). D-3's stale
  text moved with it.
- **`CandList.fact_deny`.** This is the FACT deny the listing SHOWS. Bit 28
  is shown on the anchored BOUND rows and bit 29 on `window`. The walk never
  reads it (§3.7: the bit empties the landmark, not the row).
- **The self-check** (trace build) now also fails in two cases:
  - a listed row without `desc`, or an unlisted row with one
    (`table-desc-unlisted`);
  - a listed `order` that is not the row's position among its axis's rows in
    table order (`table-listing-order`). This is what lets the projection
    walk in table order and print `order` dense.
- **Deleted.** The per-axis accessors went: `pcrec_req_admit_row`,
  `pcrec_req_use_row`, `pcrec_reseed_row` and their `Pcrec*Desc` types,
  `pcrec_dfa_axis_prefilter_cands`, `pcrec_dfa_axis_searchstart_cands`,
  `cand_axis_rows` and `cand_listed_row`. So did `PcrecAxisCand.stamp`,
  whose one user was the VM hat's row. `stamp_macro_of` loses its two start
  arms.
- **A start row with no `desc`** prints `desc_of`'s placeholder. The axis
  registry check already fails that placeholder. Its message now names both
  homes of the text (`AXIS_DESC` for a machine-form axis, the row's `desc`
  for a start axis).

**C6, the reads (added scope).**
- **G1** (`dominated`, PRESENCE) and **R4** (`adaptive-dense`, RETRY) read
  NEXT through `dfa_cand_scan(cx, reader, …)`. It uses `dfa_pf_read` on the
  DFA route and `attempt_next_read` on the ATTEMPT route, both `CAND_READ`.
  `pcrec_dfa_cand_ppm`'s second NEXT selection is a RETRY read too.
- **F1** (`handoff`, FIRST) reads PRESENCE through `req_admit_read` on
  CAND_ROUTE_DFA (C4's entry-slot route). It also runs `cand_every_route`,
  which is `cand_hit_every`'s cross-route half, split out so the read's
  `cand_hit` is not doubled.
- **`cand_nodes[].reads`** declares PRESENCE→NEXT (CR_DFA, CR_ATTEMPT),
  FIRST→PRESENCE (CR_DFA) and RETRY→NEXT (CR_DFA, CR_ATTEMPT), in the same
  commit as the routing. The DAG stays acyclic (self-check).
- **The trace.** The DFA-route reads and F1's print exactly the records
  `dfa_pf_of` and `req_admit` printed before (sites `pf-of`, `req-admit`),
  so routing them moves no record. The ATTEMPT-route read is the one
  addition. `attempt_next_of` printed no record of its own, and a checked
  read prints `NEXT attempt <row> attempt-next`. That is C6's declared
  multiplicity (`docs/design/start_table/trace_declared_C6.txt`).

**C7.**
- **D-3 corrected.** The `first-memchr-bounded` desc said `T = S & E* (E*
  every seed state's escape set; T == S)`. It now says "scanned as `T = S`,
  a non-empty proper subset of the start state's escape set E", as
  `pf_dfa_start_set` does.
- **`kind=list`.** Every start axis lists as `kind=list`. `emit_cand_axis`
  takes no kind, so `req-admit`, `req-use`, `hyb-reseed`, `vm-anchor-bound`
  and `end-window` move from `predicate`.
- **Spec hunk** `docs/spec/registry.md` §6 (D80): the `kind` column
  definition and the BOUNDARY paragraph. The paragraph now says the seven
  start axes are `cand_rows[]` projections, that a start axis's `deny_macro`
  may name a fact deny, and that `applies` is the row's `desc`. The row
  count is unchanged (136 rows / 46 axes, re-derived).
- **The movers are declared and checked.**
  `docs/design/start_table/listing_declared_C7.tsv` names every changed cell:
  five `kind` declarations over the axes (`*` = every row the PARENT lists),
  expanding to 18 cells, plus D-3's `applies` cell.
  `docs/design/start_table/listing_diff.py` compares the parent's listing
  with the commit's cell by cell. It fails in four cases:
  - an undeclared change;
  - a declaration that did not happen, or happened otherwise;
  - a row, header or section difference;
  - a `*` over an empty population.

  It was run in both directions (§3).

**Instruments** (`docs/design/start_table/`).
- `refactor_edit_set.tsv` names C6's and C7's changed TEXT. A `def` is used
  only for a definition deleted, new, or rewritten throughout; a partly
  edited one is named by its changed lines or tokens (stc5 §4 item 5's
  rule). A first draft used `def cand_rows` and `def req_handoff_applies`,
  and that classed 21 rows RE-AIM whose anchors had not moved (§4 item 2).
- `call_graph.txt`: family 132 → 135 (`attempt_next_read`, `dfa_pf_read`,
  `req_admit_read`).
- `inventory.tsv`: 150/150 (the three in as WALK).
- `assert_reach.tsv`: regenerated. It shows line moves only, plus
  `dfa_pf_read` asking `start_set` as `dfa_pf_of` does. No new assertion is
  reached.
- `sabotage_anchors.{tsv,total}`: regenerated post-C7.

**No other spec hunk.** C6 moves nothing caller-observable (`--list-axes`
byte-identical). C7's only observable change is `--list-axes`, which the
registry hunk covers.

## 2. Sabotage rows

**Derivation on main `f5d3547d`, before any edit**, with the amended edit
set: 510 row files / 528 sites, 116 family rows.
- **Re-aim C6 = S606.** It sits in `cand_nodes`, which C6 edits. Its anchor
  (NEXT's `reads`) is textually identical to PRESENCE's old reads lines, so
  the def, not a line, names it.
- **Re-aim C7 = none.** No row anchors in `axes_dump.c` (grep, 0).
- **One unresolved site**, pre-existing: S571, `memfn_sites.c:35`.

**`--step` derivations** (the commit's actual diff, ROOT the PRE tree):
- `C6=f5d3547d..dee6f5f9`: 63 rows `rerun_at` C6 (hunk 20, reach 43).
- `C7=dee6f5f9..103b07a4` (ROOT the C6 tree): 11 rows (hunk). All 11 are in
  the C6 set: the `cand_rows` anchors and S610.
- A first run with the POST tree as ROOT gave 71. It adds S224-S226, S264,
  S372, S422 and S605 through `pcrec_cand_listed`/`pcrec_cand_select_vm`/
  `cand_window_clamps` callers, plus S610. The chain runs the union.

**After C7:** 514 row files / 532 sites, 120 family rows. Every anchor
resolves (`m6read_check_sab_anchors.py`: 514 rows / 532 sites), with 0 count
mismatches.

| row | class | what changed | intent verified (plant on a scratch copy, trace build + `run_cand_oracle.sh`) |
|---|---|---|---|
| S606 | re-aim C6 | `cand_nodes` gains three `reads` entries; S606's NEXT anchor unchanged | still `CANDORACLE undeclared-read NEXT BOUND first-class-bound` |
| S607 | NEW (`candoracle`) | FIRST's `reads` loses PRESENCE (F1) | `undeclared-read FIRST PRESENCE req-admit`: 41 of 46 checks fail (every witness asks FIRST) |
| S608 | NEW (`candoracle`) | PRESENCE's NEXT read loses CR_ATTEMPT only | `undeclared-read PRESENCE NEXT attempt-next` on `(?m)^ERROR`, 2 fail; a route-blind check would pass it |
| S609 | NEW (`candoracle`) | RETRY's `reads` loses NEXT (R4), keeps BOUND | `undeclared-read RETRY NEXT pf-of` on `[a-z](?=the)`, 3 fail |
| S610 | NEW (`candoracle registry`) | the `memchr` row keeps its listing, loses its `desc` | self-check `table-desc-unlisted` (42 fail); `--list-axes` prints the placeholder; axis registry check 1 FAIL (213/1) |

All four new rows leave the default build's bytes unchanged. Each reaches
its site on the clean tree (SAB_REACH, verified). S607 took the next free id:
S606 was the highest on main and on every `lane/*` branch.

**Mech verdicts: OWED** (the chain's `MECH` lines, §6). There are 77 rows,
ids WITHOUT suffix, each verdict read from its own trailer, and FATAL is
grepped per log:
- the re-aim (1) and the new rows (4);
- the derived `rerun_at` union (71);
- judgment rows (2): S282 and S571, the two rows outside the derived set
  whose reach reads `--list-axes`. S441, S462 and S473 also read it and are
  derived.

## 3. Identity gate

The reference is main `f5d3547d`, built from `git archive`
(`build/c67/mainbuild_default`, `mainbuild_trace`). The working side is the
worktree built by `build/c67/light.sh` (`wt_default`, `wt_trace`, the trace
build with `-Werror`). The scratch scripts are stc5b's `quick`/`irq`/
`quickdeny`/`trq`, with `trq` taking the declared file as a parameter. They
ran at 6 jobs.

| run | after C6 part 1 | after C6 part 2 | after C7 |
|---|---|---|---|
| byte sweep, full distinct corpus (4,378 patterns × auto/vm × byte/utf8, `.c`+`.h`, `--emit-facts`, four dumps) | 16,026 cells, **0 movers** | **0 movers** | **1 mover: the `--list-axes` dump** (declared, below) |
| `--emit-ir` (`--engine=vm`), full corpus + 3 witnesses, byte/utf8 | 8,020, **0** | **0** | **0** |
| deny arms, every 10th pattern (14 flags × 4 arms) | 22,288, **0** | **0** | only the `--list-axes` dump |
| C1 trace vs main's trace build, full corpus × 12 arms | 2,496,990 records, **0 problems** | 2,499,322 records; 2,332 `attempt-next` declared and filtered; **0 problems**, 0 aborts | same as C6 part 2 |

| check | result |
|---|---|
| `listing_diff.py` main vs C7 | 136/136 rows, 19 declared cells, **19 changed as declared** |
| `listing_diff.py`, failing direction | identical listings: FAIL (declared change absent); an undeclared `applies` edit: FAIL; one `kind` left `predicate`: FAIL |
| other dumps (`--list-syntax/-families/-definitions/-limits/-schema`) | identical at C6 and C7 |
| `run_registry_tests.sh` (C7 tree) | green; axis check 214/0 (213/1 under S610's plant) |
| `run_cand_oracle.sh` (C7 trace build) | 46/0 |
| `run_cand_rows.sh` | 3/0 |
| `inventory_check.py` | 150/150 |
| `m6read_check_sab_anchors.py` | 514 rows / 532 sites, all resolve |
| `make` / `make strict` / trace build `-Werror` | clean |

## 4. What the design got wrong or left open (with recommendations)

1. **§3.5's "At C6 the projection keeps `pcrec_reseed_rows`/
   `pcrec_reseed_nrows` as accessors until C7"** was overtaken at C5, which
   replaced both with `pcrec_reseed_row` (stc5 §4 item 8). C6 deleted every
   per-axis accessor for the one projection. **Recommendation:** accept;
   annotated in place.
2. **The edit set's grain decides the re-aim list.** C6 names `cand_rows`'s
   and `req_handoff_applies`'s changed TOKENS and LINES, not their defs. Naming
   the defs classed 21 rows RE-AIM whose anchor text had not moved: all
   resolved at their exact counts. That overstates the intent re-verification
   a commit owes and hides which rows it really moved. The design's "a
   commit that edits a line the file does not name is out of plan" still
   holds at token grain. **Recommendation:** accept, and state the rule
   ("`def` = deleted, new, or rewritten throughout") at the top of
   `refactor_edit_set.tsv` for refactor B. It is now in C6's block comment.
3. **The C6 row does not name `cand_nodes`.** The added scope (the G1/F1/R4
   reads) edits it, so C6 re-aims S606, and §3.5's "C6 re-aims none" was true
   only of the listing half. **Recommendation:** accept; annotated in §3.5.
4. **`list[route]` + `stamp` (§1.1).** The design makes `stamp` a per-row
   column. The tree shows a row's stamp is its SLOT's on the route it is
   listed on, so it is derived (`cand_list_stamp`), not stored. The one
   per-row exception before C6 was the VM hat's `RX_VM_START_SCAN` row, and
   it is exactly the NEXT slot on the VM route. **Recommendation:** accept;
   a per-row column would be a second spelling of the slot.
5. **Two of §3.7's fact denies are listing data** (`CandList.fact_deny`),
   not derived from a landmark column. Derivation would need the `landmark`
   column (§1.1), which still has no reader. Deriving the deny from it would
   also add bit 30 (`-fno-req-byte`) to every PRESENCE row, which the listing
   has never shown. That is a contract question, not a no-mover.
   **Recommendation:** keep the explicit field until the `landmark` column
   gets a reader; then decide in its own change.
6. **The added record for the ATTEMPT-route read** (`attempt-next`) is the
   one trace movement C6 makes. The alternative, a read that prints nothing,
   would break C5b's rule that every read prints its own record.
   **Recommendation:** accept, declared.

## 5. Spec hunks

`docs/spec/registry.md` §6 (C7): the `kind` column and the BOUNDARY
paragraph. Nothing else is caller-observable.

## 6. The detached chain (OWED)

`build/land/chain.sh` has stc5b's shape. A `nohup setsid` waiter polls
`worktrees/stc67/.lift` every 30 s and then runs the chain. Everything logs
under `build/land/`, and the completion lines go to `build/land/verdict.txt`:

- `SWEEP_RC=`: `emit_sweep.py --arms start --streams
  c-default,c-vm,emit-ir,composition,facts`, full corpus, tip vs main
  default (`sweepA.log`). It must read 0 movers. The dumps stream is
  excluded because C7 moves `--list-axes`.
- `LISTING_RC= <verdict>`: `listing_diff.py` main vs tip `--list-axes`
  against `listing_declared_C7.tsv` (`listing.log`). Must read EXACTLY AS
  DECLARED.
- `DUMPS_RC=`: the other six `--list-*` surfaces, `cmp` main vs tip. Must be
  0.
- `TRACE_RC=`: `emit_sweep.py --trace` (c-default/c-vm) with
  `--trace-declared tip/docs/design/start_table/trace_declared_C6.txt`
  (`sweepT.log`). It covers the SET gate, the ordered diagnostic, the
  records floor, and the 25 C1 site keys reached.
- `CODEGEN_RC=` (`codegen.log`), `MAKETEST_RC= wall=` and
  `MAKETEST_VERDICT_LINES n` (`mt.log`). The verdict grep is
  `'\*\*\* \[(Makefile:[0-9]+: )?test-'`, and 0 lines means green.
- `MECH <id> rc= <trailer>` for the 77 rows of §2 (`mech_<id>.log`),
  `MECH_FATAL <id>` on a FATAL, then `MECH_DONE`, `CHAIN_DONE` and
  `build/land/DONE`.

The tip is `git archive HEAD` at lift time. A fresh agent fills §2's mech
verdicts and §3's heavy rows from `verdict.txt` and the logs. It justifies
any UNDETECTED/UNREACHED row against its own `SAB_EXPECT`; S496/S497 are
declared UNREACHED on main (stc5b §7).

## 7. Rows gated on C7 or the fold (listed, not acted on)

Found by grepping `plan.md` for C7, "the fold", "start-table fold" and
"refactor A":
- **[START-DENSE]**: "GATED on [START-TABLE] C7".
- **[OPT-HYB-RESEED-POLICY]**: folded into [START-DENSE], "gated on C7".
- **[START-D1]**: G1 declines `EXACTPRED` rows, "its OWN row after the fold's
  C7".
- **[TIE-ALIGN]**: "its own abi event after the start-table fold's C7".
- **[DEC-FALLBACK]**: refactor B; "its STEP 0 census runs after the fold's
  C7 merges".
- **[DEC-POSDOM]**: "evaluate as its own family AFTER the start-table fold".
- **[ENG-TACTICS]** (two places): "DEPENDS ON the unified start table fold
  (C0 then C1-C7) landing first".
- **[OPTLOOP]** round 3: "RUNS BEHIND THE REMODEL — [START-TABLE] C1-C7+C5b,
  then refactor B".
- **[DEC-ROUTE]**: "rides the start-table fold's commits (C0-C7)".
  Absorbed, nothing left to do.
- **[MEMFN-ROWCON]**: "C2-C7 should keep the trace records in the
  literal-site-key form". Satisfied: C6's records are literal site keys.
- **[U8-PICK]**: "remodel overlap likely refactor A". A soft overlap note,
  not a gate.

## OWED

- The heavy chain (§6), all of it.
- §4 items are recommendations to accept. Item 5 (fact denies as listing
  data) is the one with a contract question behind it.
- Closing the [START-TABLE] row (STATE:completed, archive) is the manager's
  at merge, once the chain reads green.

## STATE AT HANDOFF

- Branch `lane/stc67`. Code, checks, instruments, spec and docs are
  committed, and this report's commit is the tip.
- The light gates are COMPLETE and green (§3). C6 has zero movers. C7's only
  movement is the declared `--list-axes` cells. The trace is identical apart
  from C6's declared `attempt-next` records. There is no abi event.
- The heavy chain is ARMED, NOT RUN. The waiter PID/SID are in the handback
  message. It waits for `worktrees/stc67/.lift`, then runs
  `build/land/chain.sh`, and ends with `CHAIN_DONE` in
  `build/land/verdict.txt`.
