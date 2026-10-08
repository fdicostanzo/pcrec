# stc5 — [START-TABLE] C5: RETRY + BOUND + WINDOW + WIDTH read the start table

Lane stc5, 2026-10-07, opus. Branch `lane/stc5` off main `8cada7b9` (C3 and
C4 merged). Design: `docs/design/start_table.md` rev 2.1 §3.2 C5, §2.2, §3.5,
§3.6. Models: `stc3_report.md` and `stc4_report.md` (their §4 rulings, chains
and instruments). The edit set and the anchor derivation were re-derived on
current main before any edit (§2).

**Status:** built and committed. On the light gates (§3), ZERO MOVERS, no abi
event, and the C1 trace is unchanged record for record. No trace difference
is declared. The heavy chain is **OWED**: it is armed detached and waits for
`worktrees/stc5/.lift` (§6).

## 1. What landed

Three commits on top of `8cada7b9`: `1f284904` (C5 proper), `19229768`
(checks, re-aims, re-derived instruments, spec hunks, CLAUDE.md files) and
`b367be5a` (plan, design note, Makefile comment). This report is a fourth.

- **The last old table is deleted.** `pcrec_reseed_rows[]` (emit_vm.c), its
  `VRS_P_*`/`VRS_A_*`/`VRS_S_*` tag enums and `vm_reseed_holds` are deleted
  into the RETRY rows of `cand_rows[]`.
  - Each row's action, start column, armed bit and listing text are the
    payload `CandReseed` (`u.reseed`). Its action and start enums are
    `CAND_RS_A_*`/`CAND_RS_S_*`, as the edit set named them.
  - The row reasons that sat above the old table now sit on the RETRY block
    of `cand_rows[]`, verbatim.
  - `vm_plan_reseed` asks `pcrec_cand_select_vm(RETRY)`.
  - `VmReseed.row` is a `const CandRow *`, read through `pcrec_cand_tok`
    (the `<PREFIX>_VM_RESEED` stamp and the trace) and `pcrec_cand_reseed`.
- **The inline decisions read their slot's row.**
  - **WINDOW.** The end-window clamp asks `cand_window_clamps` (WINDOW on
    CAND_ROUTE_DFA, C4's entry rule) and returns early unless
    `u.window.clamp` holds. The window VALUE is still the `end_window`
    fact's.
  - **WIDTH.** The VM entry's root-minw test reads `vm_width_row`
    (`u.width.check`).
  - **BOUND on the ATTEMPT route.** `emit_attempt` asks BOUND on
    CAND_ROUTE_ATTEMPT: `a_bot`/`anchored` are the row's `u.bound.one`, and
    `start_max`'s text is `u.bound.start_max`. The one-way assertions stay in
    the body.
  - **BOUND on the VM route.** The VM's `attempt_max` reads `vm_bound_row`.
    Its declaration line is `u.bound.attempt_max`, one text that B3 and B4
    share (`CAND_VM_BOUND_ONE`). The comment still names the fact's value.
- **The stamp and listing readers project the same rows.**
  - `<PREFIX>_END_WINDOW`: the fact's window where the WINDOW row clamps,
    and the row's listed name (`none`) where it does not.
  - `<PREFIX>_VM_START`: the BOUND row's listed name on the VM route
    (`anchored`/`gstart`/`unanchored`, the stamp's own vocabulary).
  - `<PREFIX>_VM_ROOT_MINW` and `--emit-ir`'s `root-minw` row: emitted
    where the WIDTH row checks, with the value still from `root_minw`.
- **`dfa_select` STAYS** (the C3 ruling). C4 had already removed the start
  tables' last `DFA_SELECT` callers, so C5 deletes none. The edit set's
  `def DFA_SELECT C5` row is annotated with the ruling.
- **The VM emitter's view of the table** (`core/internal.h`).
  - `CandRow` is opaque outside emit_dfa.c.
  - The three payloads the VM reads (`CandReseed`, `CandBound`,
    `CandWidth`) are defined in the header.
  - The walk is `pcrec_cand_select_vm(cx, slot, vm)`, and five one-line
    accessors read the chosen row.
  - `CandWindow` stays in emit_dfa.c, since only emit_dfa.c reads it.
  - §4 item 2 says why the design takes this shape.
- **The listing projection.** `pcrec_reseed_row(i, &desc)` projects the
  RETRY rows for `--list-axes` (axis `hyb-reseed`), in C4's shape: a bool
  accessor, false past the last row. `pcrec_reseed_nrows` and
  `PcrecReseedRow` are gone, and `axes_dump.c` loops on the return. Stream
  5 is byte-identical.
- **The C2 both-walks oracle is retired.** Nothing is left to compare, so
  these are deleted: `cand_oracle_pre/post`, the `_in` pair, the
  `CAND_ORACLE_*` macros, `pcrec_cand_oracle_vm_pre/post`,
  `VM_CAND_PRE/POST`, `CandRow.was` and `-DPCREC_CAND_NEW_FIRST`'s branch.
  Every reader now runs the hit counter:
  - `cand_hit` on the DFA side;
  - `VM_CAND_HIT` → `pcrec_cand_hit_vm` on the VM side;
  - WINDOW `cand_hit_every`, which keeps the C2 oracle's `every`
    cross-route check as the entry-slot rule.

  `tests/codegen/run_cand_oracle.sh` builds one trace compiler, and
  `CAND_ORACLE_BINS` takes one binary (a second word is ignored).
- **Checks.** `tests/codegen/cand_rows_check.py` `[cand-no-name-strcmp]`
  now covers EVERY slot.
  - The WINDOW/WIDTH/RETRY/BOUND rows' 17 names are ordinary words (`all`,
    `exact`, `anchored`, ...). For them the literal half fires only where
    the same call also reads a row-name expression: §3.5's rule.
  - The receiver half adds the C5 selection functions and the VM name
    accessors.
  - Failing direction shown on a scratch copy:
    `strcmp(pcrec_cand_tok(rs->row), "exact")` and
    `strcmp(vm_bound_row(v)->tok, "anchored")` both FAIL, and a
    literal-only `strcmp(v->cx->opt->name, "exact")` stays green.
  - New sabotage row **S605** (§2).
- **Spec hunks (D80).** `docs/spec/registry.md` BOUNDARY (the `hyb-reseed`
  rows are `cand_rows[]`'s RETRY rows since C5) and `docs/spec/tuning.md`
  §2.35 (the same, parenthetical). No artifact or listing text moved.
- **Readers outside `src/`** (`reader_grep.sh` over the C5 `def`s, plus a
  grep for the retired names). Updated: `src/core/axes.def`'s
  `-fno-hyb-reseed` comment, `tests/registry/axes_registry_check.sh`'s
  `RX_VM_RESEED` comment, the `Makefile`'s `test-cand-oracle` comment,
  `tests/mech/run_sabotage_matrix.sh`'s `candoracle` arm description, and
  `src/gen/CLAUDE.md` (a C5 entry; the re-seed section),
  `tests/codegen/CLAUDE.md` and `tests/mech/CLAUDE.md`.
- **Instruments re-derived:**
  - `call_graph.txt`; `call_graph.py`'s hook comment.
  - `inventory.tsv` is 144/144:
    - out: `pcrec_reseed_rows`, `pcrec_reseed_nrows`, `PcrecReseedRow`,
      `vm_reseed_holds`;
    - in: the four payload types, `cand_window_of`, `cand_window_clamps`,
      `pcrec_cand_select_vm`, `vm_width_row`, `vm_bound_row`, and
      `vm_cand_facts`, which is no longer trace-only.
  - `refactor_edit_set.tsv`, amended (§4 item 5).
  - `sabotage_anchors.{tsv,total}`, post-C5.

The §3.3 item 5 structural grep: every C2-C5 `token`/`line` of the amended
edit set reads 0 under `src/`. `def`s survive by name where the plan keeps
the function (C3's precedent). `make` and `make strict` are clean.

## 2. Sabotage rows

**Derivation on main `8cada7b9`, before any edit** (`sabotage_anchors.py`):
- Totals: 498 row files, 516 sites, 115 family rows.
- One unresolved site, pre-existing (S571, `memfn_sites.c:35`, already in
  main's `.total`).
- **Re-aim at C5:** S263, S371, S372, S441, S556. This is the design's list,
  with S556 being the renumbered H1 row the design calls S169.
- **`rerun_at` C5:** 22 sites in 21 rows: S36, S63, S82, S85, S88,
  S141 (two sites), S144, S168, S181, S224, S225, S226, S235, S264, S370,
  S400, S422, S430, S469, S511, S572.
  - Against the design's list, S511 (`emit_attempt`) and S572
    (`pcrec_emit_prologue`, the `END_WINDOW` stamp's owner) are new.
  - S82/S235 are as listed.

**After C5** (on the post-C5 tree): 498/516, all anchors resolve
(`m6read_check_sab_anchors.py`), 0 count mismatches. The C5 re-aims now sit
outside any C5 edit. S372 still classes RE-AIM, because its owner
`vm_plan_reseed` is a C5 `def`; its anchor survived.

| row | class at C5 | what changed | intent re-verified (plant on a scratch copy, probe) |
|---|---|---|---|
| S263 | re-aim | anchor `#define CAND_VM_BOUND_ONE "    const size_t attempt_max = search_from;\n"` (emit_dfa.c, B3/B4's bound text); same edit | `^(a)b` `--engine=vm`: stamp `anchored`, body `attempt_max = subject_length` |
| S371 | re-aim | `if (rs->row && pcrec_cand_reseed(rs->row)->action != CAND_RS_A_FIXED) {`; same edit | `(?<=é)x` utf8: stamps `adaptive`, 0 `reseed_steps--` (1 unplanted) |
| S372 | re-aim (anchor unchanged) | `rs->cal = vm_reseed_cal[v->has_push];` | `(?<=é)x` utf8: frameless start budget 64 → 2 |
| S441 | re-aim (C5; C5b again) | `cand_rs_anchored_applies`' body in emit_dfa.c (the old switch arm); same edit | `^(?>a|ab): (.*)$`: `anchored` → `adaptive-dense` |
| S556 | re-aim | `* [START-TABLE] C5 the condition is the WIDTH row ...` / `if (pcrec_cand_width(width)->check)`; same edit (the site removed) | `^((?1)a)$`: guard 1 → 0, stamp kept |
| S605 | NEW (`candrows`) | `vm_plan_reseed` reads the armed state by `strcmp(pcrec_cand_tok(rs->row), "adaptive-dense")` | artifact byte-identical (md5 equal on `[a-z](?=the)`); `[cand-no-name-strcmp]` FAILs |
| the 21 `rerun_at` C5 rows above | re-run (derived) | their owner's body changed around the anchor | — |
| S594, S595, S596, S597, S598, S599, S600 | re-run by judgment | the trace-build code around them changed (oracle → hit counter). S597's plant now MOVES the VM bound (B3 decides) | — |
| S495, S283, S284, S462, S473 | re-run by judgment | S495's `pcrec_dfa_cand_ppm` is reached through RETRY R4's walk now; S283/S284/S462/S473 sit in `cand_rows`, whose block C5 edited (payloads), although the edit set names `cand_rows` only at C2 (§4 item 6) | — |

S605 takes the next free id: S604 was the highest across main and every
`lane/*` branch (possbuild's). A concurrent lane taking S605 would be a merge
renumber.

**Mech verdicts: OWED** (the chain's `MECH` lines, §6). Ids are passed
WITHOUT a suffix. The chain greps each log for `FATAL` and prints each row's
`== mech run COMPLETE` trailer. Every row's `SAB_EXPECT` is DETECTED except
where the row declares otherwise on main.

## 3. Identity gate

**The light gates.** All builds are default builds of the working tree,
against main `8cada7b9` built from `git archive` into `build/c5/main`. The
scratch scripts are `build/c5/quick.py`, `quickdeny.py`, `irq.py` and
`trq.py`, adapted from stc4's.

| run | population | result |
|---|---|---|
| byte sweep, full distinct corpus | 4,292 patterns × 4 arms (auto/vm × byte/utf8), `.c`+`.h` at one `-o` basename, `--emit-facts=byte,utf8`, `--list-axes`/`-syntax`/`-limits`/`-schema` | 15,690 compiled cells, **0 movers** |
| `--emit-ir` listing (`--engine=vm`), full corpus + the three ceiling witnesses | 4,295 × byte/utf8 | 7,852 listings, **0 movers** (`root-minw` row reached) |
| deny arms, every 10th pattern | 430 × 14 flags (the 12 start-family bits, `-fprefilter-collapse`, `-fno-length-prune`) × 4 arms | 22,372 compiled cells, **0 movers** |
| C1 trace vs main's old-first trace build, full corpus | 4,292 × 12 arms (the 4 base arms, `-fno-hyb-reseed`, `-fno-vm-anchor-bound`, vm `-fno-vm-anchor-bound`, `-fno-end-window`, `-fno-length-prune`, `-fprefilter-collapse`, utf8 `-fno-hyb-reseed`, `-fno-req-byte`) | 2,301,454 records, **0 problems**. The multiset AND the ordered sequence are identical, the trace build's `.c` is identical, and there are 0 aborts. NO declared difference |
| `run_cand_oracle.sh` | 42 witnesses | 46 / 0 (47 / 0 with its own build) |
| `run_cand_rows.sh` | 23 + 17 row names, 243 comparison calls | 3 / 0 |
| `inventory_check.py` | | 144 / 144 |
| `m6read_check_sab_anchors.py` | 498 rows / 516 sites | all resolve |

The heavy chain is §6, OWED. It covers: the six emit_sweep streams plus
`--arms start` (64 DIFFER cells); the full trace against both of main's
trace builds; the `--trace` stream; the oracle; `cand_rows`;
`test-codegen`; `make test`; and the 39 mech rows.

## 4. What the design got wrong or left open (questions with recommendations)

1. **"One selection" (§3.6) and "no eager plan" (§1.3) meet in the VM's
   phase order.**
   - **The conflict.** `pcrec_emit_vm` writes the stamps BEFORE the
     search body. A stamp can therefore read the body's selection only if
     that selection is made earlier, in a planning step. That is an eager
     ask, and it reorders the C1 trace: the WIDTH and BOUND records would
     move ahead of the prologue's.
   - **What was built.** Each stamp and listing reader RE-ASKS the same
     one-function derivation (`vm_width_row`, `vm_bound_row`,
     `cand_window_of`) without a record. Only the body's ask prints its
     trace record and hit.
   - **Why it is sound.** The re-ask's predicates are pure reads, and
     their asks were already made by the reader it replaces: `root_minw`;
     the `start_anchor` and `end_window` facts, which the old stamps read
     through `pcrec_fact_stamp`.
   - **Precedent.** This is RECOVER's shape since C3 (`dfa_search_start_of`,
     "one derivation, five readers").
   - **Recommendation:** accept. The alternative (decide in
     `vm_plan_reseed`'s planning step, store the rows, and print each record
     at its body site from the stored row) is equally byte-neutral and
     closer to the VM file's "the stamps decide nothing" header. It changes
     where the trace record is printed, so it is a ruling, not a lane
     choice.
2. **How emit_vm.c reads the table.** The rows live in emit_dfa.c, and
   their type embeds emit_dfa.c-private types (`CandPf`, `CandSel`).
   - **What was built.** `CandRow` is opaque in `core/internal.h`. The VM
     reads it through `pcrec_cand_select_vm` and five one-line accessors
     (`pcrec_cand_tok`, `_listed`, `_reseed`, `_bound`, `_width`). The
     three payload types it reads are in the header.
   - **The alternative.** Moving `CandRow` and its whole payload union into
     the header would drag `CandSel`/`CandPf`/`PfScan`/`DfaForm` with it,
     with anchors on their fields.
   - **Recommendation:** accept. C6/C7, or the kit's general table engine
     if a table adopts it (Q-ROW-4), can revisit it.
3. **WINDOW and WIDTH needed payloads the design did not list.**
   - **Why.** §1.1's `u` list has none for them. But a reader may not
     branch on `map` (§1.4), nor compare row identity
     (`dfa_search_is_pinned`'s [r2 sound-m2] rule).
   - **What was built.** `u.window.clamp` and `u.width.check`, one bool
     each.
   - **`u.bound`'s shape.** It is `one` (none / offset 0 / startpos) plus
     each route's text. `all`, routed on both routes, carries
     `start_max = "subject_length"` and no `attempt_max`.
   - **Recommendation:** accept, and add both to §1.1's table at C6.
4. **`<PREFIX>_VM_START` projects the row's LISTED name, not the fact's
   renderer.**
   - **The two spellings.** The design's parenthetical ("the value still
     from its landmark") fits `END_WINDOW` and `VM_ROOT_MINW`, whose values
     are numbers, and those still come from their landmarks. `VM_START`'s
     value IS which row fired: `anchored`/`gstart`/`unanchored` is both the
     fact's spelling and B3/B4/B5's `vm-anchor-bound` listed names.
   - **Why the listed name.** Reading the listed name makes the stamp, the
     body and the listing one selection. Reading the fact would keep a
     second path the stamp could drift down.
   - **Bytes.** Identical (§3).
   - **Recommendation:** accept.
5. **The edit set named text that C5 keeps; amended, each with its reason
   in the file.**
   - **Kept text.**
     - `long long w = pcrec_fact_end_window(cx);` is now the clamp's VALUE
       read after the row decides. The decision was the next line, which
       is gone.
     - The two stamp CALL lines (`END_WINDOW`, `VM_START`) still write
       their stamps; their VALUE lines are the ones that changed.
   - **Re-pointed entries.**
     - Token `rs->row` → `rs->row->`: the field keeps its name and its
       type changes.
     - `def DFA_SELECT C5` is annotated STAYS.
     - R3's C5b `line` is re-pointed to its text's new home,
       `cand_rs_anchored_applies` in emit_dfa.c, so C5b's derivation finds
       S441's anchor.
   - **Recommendation:** accept. An edit-set `line` should name the text
     that CHANGES, which a re-derivation on the commit's own diff would
     give.
6. **The `rerun_at` gap again (stc4 §4 item 3).** It shows in two shapes:
   - rows reached through a NEW walk: S495, via R4's `pcrec_dfa_cand_ppm`;
     and S597, whose B3 predicate now decides the bound;
   - rows sitting in a definition the commit edits that the edit set
     names only at an earlier commit: `cand_rows`, whose block C5 extends
     with payloads (S283, S284, S462, S473, S594-S600).

   All twelve re-run by judgment in the chain. **Recommendation:** as
   stc4's. `sabotage_anchors.py` should compute `rerun_at` from each
   commit's actual diff (owner bodies touched) plus the walk-reach
   change, rather than from the edit set's `def` column alone.
7. **"Both orders" after C5.** The order mattered only while an old
   decision ran beside `cand_select`; with none left, `-DPCREC_CAND_NEW_FIRST`
   selects nothing. The chain therefore compares the tip's one trace build
   against BOTH of main's trace builds (old-first and new-first), which is
   the strongest form left. **Recommendation:** accept; the macro can be
   dropped from the docs at C7.
8. **`pcrec_reseed_rows`/`nrows` "accessor kept to C7"** (§3.5) became C4's
   bool projection now. The only readers outside `src/` were comments, and
   they are updated. **Recommendation:** accept; C6's general projection
   absorbs it.
9. **A scratch slip, reported.** One light run of `run_cand_oracle.sh`
   (its self-build check) ran without `TMPDIR` set, so its `mktemp -d`
   landed in `/tmp`. Its exit trap removed the directory, and nothing
   remains (checked). The chain exports `TMPDIR` into the worktree's
   `build/tmp`.

## 5. Spec hunks

- `docs/spec/registry.md`, the BOUNDARY paragraph: the `hyb-reseed` rows
  are `cand_rows[]`'s RETRY rows since C5.
- `docs/spec/tuning.md` §2.35: the same, as a parenthetical.

No artifact or listing text moved, so there is no abi event and no other
hunk.

## 6. The detached chain (OWED)

`build/c5/waitrun.sh` is armed with `nohup … & disown`, logging to
`build/c5/chain.log`. It waits for `worktrees/stc5/.lift`, then runs
`build/c5/chain.sh`.
- Every step logs under `build/c5/`.
- The tip's binaries are built by `git archive` from the HEAD at lift time
  (`tipbuild_default`, `tipbuild_trace`).
- Main's builds come from `8cada7b9`: `build/c5/mainbuild_default` and
  `mainbuild_old`, plus `mainbuild_new`, which the chain builds if absent.

Completion lines, in order:

- `SWEEP_RC=`: Run A, THE BAR. `emit_sweep.py` runs the six streams plus
  `--arms start` (64 DIFFER cells) over the full corpus (`sweepA.log`). It
  must read 0 movers.
- `TRACEQ_RC=a/b`: `trq.py` over every distinct pattern × 12 arms, against
  main's old-first and then its new-first trace build (`traceq_old.log`,
  `traceq_new.log`). It must report `problems 0`. C5 declares NO trace
  difference.
- `TRACE_RC=`: `emit_sweep --trace` (`sweepT.log`): floors and site reach,
  with nothing declared.
- `ORACLE_RC=`, `CANDROWS_RC=`, `CODEGEN_RC=`.
- `MAKETEST_RC= wall=` and `MAKETEST_VERDICT_LINES n` (`maketest.log`). The
  verdict is `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`, and 0 lines
  means green. `docs/dev/artifact_size_log.tsv` is restored after.
- `MECH <id> rc= <trailer>` for the 39 rows of §2 (`mech_<id>.log`). A
  `MECH_FATAL <id>` line follows if the log has FATAL. Then `MECH_DONE`;
  then `build/SLOT_DONE` is touched and the chain prints `CHAIN_DONE`.

A fresh agent completes the delivery from these lines. It fills §3's heavy
rows and §2's verdicts, and justifies any UNDETECTED (EXPECTED) row.

## OWED

- The heavy chain above (all of it), including the 39 mech rows and the
  full `make test` wall and verdict.
- §4 items 1, 2 and 6 are open for a ruling; the rest are recommendations to
  accept.

## STATE AT HANDOFF

- Branch `lane/stc5`. The code, the light checks and the docs are committed;
  this report's own commit is the tip.
- The light gates are COMPLETE and green (§3): zero movers, the trace is
  identical, there is no abi event, and no trace difference is declared.
- The heavy chain is ARMED and has NOT run:
  - the waiter is `nohup setsid bash build/c5/waitrun.sh`, PID 3024498,
    started 2026-10-07T20:41:53;
  - it waits for `worktrees/stc5/.lift`, then runs `build/c5/chain.sh`;
  - it logs to `build/c5/chain.log`, with the completion lines in §6;
  - it ends with `build/SLOT_DONE` and `CHAIN_DONE`.
- The chain takes the tip by `git archive HEAD` at lift time. A fresh agent
  fills §2's mech verdicts and §3's heavy rows from `chain.log` and the
  per-step logs under `build/c5/`, and justifies any UNDETECTED (EXPECTED)
  row.
- Open for a ruling: §4 items 1, 2 and 6.
