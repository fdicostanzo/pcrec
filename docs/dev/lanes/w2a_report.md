# [REVW.2] WAVE 2, SLICE A — EP2's steps 1 through 9

Lane `w2a` (opus, 2026-09-18), branch `lane/w2a` off `main` at `f6474777`.
Charter: `docs/dev/reviews/lens_reports/emitvm_second_pass.md` §5's sequence
table, steps 1-9, one commit per step, every step byte-neutral. NOT in
scope and NOT touched: step 10 (X8), step 11 (stage 3 / `sb_fragf`), steps
12-15, DD-8, `[EMIT-VERB]`, `src/gen/emit_dfa.c`.

**Nine steps landed, nine commits, every one byte-neutral on three
independent artifact streams.** No step is an `abi` event: not one emitted
byte moved, so no bump, no identity re-pin and no `docs/spec/` hunk is owed
(D76/D94 apply to emitted-text changes; there are none here).

---

## 1. The steps

| # | step | commit | what it did | buffers retired | anchors re-aimed |
|---|---|---|---|---:|---:|
| 1 | **E1** `vm_slot_ref` | `1c0d3418` | collapsed the four hand-rolled slot-ref copies in `vm_call`/`vm_splice` onto a helper built ON `vm_slot_expr` | **8** | 0 |
| 2 | **E2** `vm_emit_span_scan` | `570495e7` | one writer for `vm_cursor_rep`'s two span scans (possessive + greedy) | 0 | 0 |
| 3 | **E3** `vm_bounds_text` | `c6de6802` | `{m,}` / `{m,n}` in one spelling instead of three, across four sites | **3** | 0 |
| 4 | **P1** `vm_resolve_nonnull` | `1f79bc32` | the call-target nullability fixpoint out of `pcrec_emit_vm` | 0 | 0 |
| 5 | **P2** `vm_plan_regions` | `170ff1e3` | region linkage flags + transitive group set + `spl_nw` | 0 | 0 |
| 6 | **E0** `vm_walk_caps` + `vm_walk_calls` | `a7081656` | four spine walkers → two walkers + four callbacks | 0 | **1** (S149) |
| 7 | **P4** `vm_memo_region_costs` | `a5150ffc` | the region cost fixpoint | 0 | 0 |
| 8 | **P3** `vm_build_region_saves` | `edb39ab8` | the `W` save-set build, snapshots as parameters | 0 | **6** |
| 9 | **`vm_plan_capacities`** | `60e78828` | the capacity/budget policy block | 0 | **0** (EP2 said 2 — see §4) |

**Totals.** 11 of EP2 category (a)'s 40 literal-sized buffers retired
(measured: literal-sized `char NAME[<int>];` declarators in `emit_vm.c`
went **35 → 24**; all `char NAME[…]` declarators **56 → 46**, the one
addition being `vm_slot_ref`'s `char ex[PCREC_MAX_EMIT_NAME_LEN]`, which is
derived per coding_guide §2.2, not literal). `pcrec_emit_vm` went **2,387 →
2,071 lines**. The file grew 11,659 → 11,824 lines, which is what extracting
into documented headers costs and is the trade EP2 asked for.

---

## 2. Byte-neutrality: the instrument, and its reach

Three artifact streams, all compared against a **pinned branch-point
binary** built from `git archive HEAD` at `f6474777` — a reference that does
not move as the lane edits, so a step's green is a fact about that step.

**(a) The corpus argv sweep.** Every `pattern`/`pattern-esc` block in
`tests/**/*.rxt` — 3,938 rows, the same population and `--list-source`
methodology as `docs/dev/w1stage0_evidence/longprefix_sweep.py` — compiled
three ways per row and hashed:

| stream | what it is | OK rows |
|---|---|---:|
| `.c` at default engine | `-p rx --features all --emit-main -o -` | 3,731 |
| `.c` at `--engine=vm` | forces the VM route on every pattern that can take it | 3,732 |
| `--emit-ir` listing | `vm_render_listing` → `job->irsb` | 3,732 |

`--features all` is what makes the recursion corpus reachable at all: 398
`tests/recursion/` rows, **360 of them compiling through the VM route**,
which is this slice's own reach into `vm_call`/`vm_splice`/`vm_region`.
The sweep was run twice on one unchanged binary first and returned an
identical TSV, so a green means "no byte moved", not "the instrument is
noisy". **Every one of the nine steps: BYTE-IDENTICAL, all three streams.**

**(b) The composition-route sweep — and why the argv sweep is not enough.**
`vm_splice`'s DELIVER block (one of E1's four sites) is gated on
`a->u.call.deliver_n`, which is written **only** by
`src/parse/rxt_compose.c`. No pattern passed through `argv` can reach it,
and **no `tests/**/*.rxt` corpus file declares an `export`** — the
delivering fixtures are `tests/rxtsource/fixtures/*.rxtin`, which the
corpus sweep does not see. So a second sweep compiles all 304 `.rxt`/
`.rxtin` files through `pcrec --features all --source F -o <dir>` and hashes
every artifact produced (74 artifacts). **Every step: BYTE-IDENTICAL.**

**MEASURED REACH, not assumed** (learnings §3 item 3, `[MECH-REACH]`). A
marker was planted in the DELIVER block and both sweeps re-run:

| sweep | rows that changed |
|---|---|
| composition route (304 files) | **2** — `compose_delivers.rxtin`, `deliver_forms.rxtin` |
| argv corpus (3,938 patterns) | **0** |

The marker was then removed and both sweeps returned to identical. Without
arm (b) this lane would have had **no witness at all** for one of E1's four
sites, and the corpus green would have said nothing about it.

**(c) The `irsb` arm.** `tests/codegen/run_ir_listing.sh` — **93 passed / 0
failed** on every step, including its 11 BYTE-NEUTRALITY rows. Its measured
reach is 27 of 41 `vm_rolef` sites with no lookbehind, subroutine-call or
counter-rung reach (`w1stage0.md` §2-3), which is exactly why sweep (a)'s
`--emit-ir` column exists: it puts 3,732 listings against that arm's 11.

**(d) The four `.c` identity gates.** `make test-codegen`: **8 of 9 scripts
pass on every step, and the failing set is byte-identical to the
branch-point baseline run** — one row, `run_inline_capability.sh`'s `nm
could not read arm_a.o (no rx_search symbol)`, a darwin `nm` red measured on
`f6474777` itself before the first edit. Not this lane's.

`make strict`: clean on all nine steps.

---

## 3. Anchors

**The instrument.** `replace.py`'s own gate, run over every row without
building a mech tree: source each `tests/mech/sabotages/S*.sh`, count its
`SAB_BEFORE`/`SAB_BEFORE2` in the current tree by the same whole-file
`content.count()` the applier uses, and compare to `SAB_COUNT`. **282 anchor
records across 266 rows**; 0 mismatches at the branch point.

**FLOORS BY GREP ON THIS TREE** (`grep -rl <id> tests/mech/sabotages/`),
never cited from EP2:

| identifier | rows | | identifier | rows |
|---|---:|---|---|---:|
| `vm_count_slots` | 8 | | `vm_cursor_rep` | 1 |
| `vm_w_range` | 4 | | `vm_rep` | 1 |
| `vm_splice` | 3 | | `vm_grp_set` | 1 |
| `vm_region` | 3 | | `vm_w_caps` | 1 |
| `vm_cost` | 3 | | `vm_slot_expr` / `vm_slot_name` / `vm_revdet_rep` / `vm_counter_rep` / `vm_publish_nonnull` / `vm_publish_saves` / `vm_ceiling` | 0 |
| `vm_call` | 1 | | | |

**`emit_vm.c` holds 95 anchor RECORDS on this tree (99 located occurrences),
against EP2's 94 at `7d444f9e`.** EP2's own rule — counts are FLOORS — met
from inside, as `w1kit_report.md` §8 item 6 predicted it would be.

**Seven re-aims, all measured in both directions.** For each, the anchor set
was counted before the edit (to see exactly which broke) and after (to see
that nothing else did):

| step | rows re-aimed | before | after |
|---|---|---|---|
| E0 | S149 | **1** of 282 broken, and only S149 | 0 of 282 |
| P3 | S148, S150, S151, S152 (both sites), S153 | **6** of 282 broken, exactly EP2's predicted set | 0 of 282 |

Each break has one cause and the re-aim applies exactly that transform:
E0's is the eight-space dedent of `vm_w_caps`'s `A_CAP` arm into
`vm_w_cap_slots`'s body plus the closure spelling (`w`/`nstate` →
`c->w`/`c->nstate`); P3's is the four-space dedent plus
`snap_before`/`snap_after` → `before`/`after`. Every row carries a dated
`RE-AIMED` note saying which step moved it and that the plant and intent are
unchanged.

**RE-DRIVEN SOLO, not assumed.**

All seven were re-driven solo (`run_sabotage_matrix.sh <id>`, one invocation
per row — the driver's selector takes one id), **every one at the final tree
SHA `8c142b9a`**, with `unexpected: 0` and `anomalies: 0` on every run:

| row | `SAB_EXPECT` | verdict | cells |
|---|---|---|---|
| S148-w-includes-slot0 | (DETECTED) | **DETECTED** | `corpus:18fail/2pass, recdiff:169fail/7pass` |
| S149-w-drops-pending | (DETECTED) | **DETECTED** | `corpus:5fail/42pass, recdiff:4fail/9pass` |
| S150-w-drops-cutmark | UNDETECTED | **UNDETECTED (EXPECTED)** | `corpus:0fail/47pass, recdiff:0fail/10pass` |
| S151-w-drops-emptyguard | UNDETECTED | **UNDETECTED (EXPECTED)** | `corpus:0fail/1690pass, recdiff:0fail/10pass` |
| S152-w-drops-rungs | UNDETECTED | **UNDETECTED (EXPECTED)** | `corpus:0fail/1690pass, recdiff:0fail/10pass` |
| S153-w-drops-look | UNDETECTED | **UNDETECTED (EXPECTED)** | `corpus:0fail/50pass, recdiff:0fail/10pass` |

**Read these against `SAB_EXPECT`, not against "DETECTED".** Four of the six
P3 rows are argued-not-measured rows sitting on the ratchet with
`SAB_EXPECT=UNDETECTED`, so the criterion is the driver's own `unexpected:
0` — an UNDETECTED there is the row behaving as recorded, and a sudden
DETECTED would be the surprise. S149 was driven at `a7081656` (its own
commit, since the runner archives HEAD) and again in this final set.

One honest caveat about the cells: the PASS counts have grown since these
rows' `SAB_DOC_FIGURE` text was written (S152 records `corpus 0fail/346pass`
against the 1,690 measured now), because the corpus has grown. The VERDICTS
match the recorded ones exactly; the pass denominators do not, and should
not be read as reproducing the historical figure.

Logs: `…/scratchpad/w2a/mech_S1{48,49,50,51,52,53}.log`, collected verdicts
in `…/scratchpad/w2a/mech6.verdicts`.

---

## 4. What EP2 got wrong about the tree

The `w1kit_report.md` §8 shape: short, so a later lane carries it.

1. **`vm_plan_capacities` carries ZERO anchors, not two.** EP2 §3.4's table
   reads *"P4 + `vm_plan_capacities` `:9189-9405` — 2 anchors: S41, S184"*.
   Measured here: extracting the capacity policy broke nothing.
   `S41_ir_label_drift` anchors on `vm_lbl(&v, acc, …)` and
   `S184_frame_size_from_wrong_struct` on the `vm_layout` frame-size pair —
   both in the EMISSION block that FOLLOWS the policy, and neither quotes a
   capacity local. EP2's row bundles P4 and the capacities into one span and
   inherits the emission block's anchors. **The slice's true anchor cost is
   7 re-aims, not 9.**
2. **The anchor population is 95 records in `emit_vm.c`, not 94** (282
   tree-wide across 266 rows, against EP2's 261 rows / 277 records and
   `w1kit`'s 266 rows). Floors, as everyone keeps saying and keeps being
   right about.
3. **E1's four sites are all in `vm_call`/`vm_splice`.** EP2's §4 layer table
   lists L10's nine category-(a) buffers as *"`vm_call` ×2, `vm_splice` ×6,
   `vm_region` ×1, of which E1 retires 8"*. The eight E1 retires are two in
   `vm_call` and six in `vm_splice`; `vm_region` is untouched. The prose in
   §2.3 saying "four sites in `vm_call`/`vm_splice`" is the accurate half.
4. **`vm_plan_capacities` cannot be a clean value-returning extract without
   dropping two fields.** `Cost cost` and `fits` have NO reader outside the
   policy block — the compiler said so (`-Wunused-variable` on both when
   they were carried out in the struct). Any brief that lists "eight values"
   to return is listing six plus two intermediates.
5. **Three extractions forced a verbatim relocation of a small helper**
   (`vm_w_range` for P3, `vm_ceiling` for step 9) because the extracted
   function now precedes the helper's old definition. Free — a verbatim
   same-file move costs zero re-aims (EP2 §3.5's own finding) — but a brief
   that budgets "one function per step" will meet it at compile time.
6. **The argv corpus is NOT a witness for the DELIVER block** (§2b). EP2's
   byte-neutrality obligation names the four identity gates, the full-corpus
   emit-diff and the `irsb` arm; none of the three reaches
   `deliver_n > 0`. Measured: 0 of 3,938 argv rows, 2 of 304 source files.

**HELD:** EP2's step ORDER (including its three corrections to lens 11 —
X8 last, P2 exists, P4 before P3), its abi verdict for every step (not an
event, confirmed by measurement on three streams rather than assumed), its
zero-anchor predictions for E1/E2/E3/P1/P2/P4, its 1-anchor prediction for
E0 and its 6-anchor prediction for P3 (both exact), its correction to lens
11's `vm_build_region_saves` signature (the snapshots really are
unexpressible as anything but parameters), and its ruling that the
non-emitting passes stay in `emit_vm.c` rather than moving to `src/opt/`.

---

## 5. Design notes a reviewer should check

- **D108 boundary.** Nothing added here is a kit primitive. `vm_slot_ref`,
  `vm_emit_span_scan` and `vm_bounds_text` take `Vm *` because they read
  `v->p`/`v->up`/the slot layout and write `v->b` — they are the emitter's
  own helpers, in the same class as the `vm_set`/`vm_rolef` family they sit
  beside, not `sb_*`-tier text primitives. The five P-steps are WALK-side
  passes over the `Vm`, which D108's rule about primitives never reaching
  into `Ctx`/`Job`/`Vm` does not govern. The walk → `VEvent` → render
  boundary is untouched: no new writer of `v->ev` and no new reader of it.
- **The two walkers stayed two** (E0), and `vm_grp_set_cap` /
  `vm_w_cap_slots` stayed two callbacks. `src/opt/atomic.c`'s warning
  against merging verdicts is the governing rule and the file's own comment
  at the old site explains why the same walk answers in two index spaces.
- **Three `ctx_fail` assertions travelled with their passes and their
  comments**: the nullability fixpoint's settle-round assertion (P1 — EP2
  warned that an early return would delete it silently; it did not),
  the `spl_nw` agreement check with its "this is a SAME-SOURCE check and
  must not be read as anything more" comment (P3), and the cost memo's
  did-not-settle failure (P4).
- **One comment was corrected rather than moved intact**: the `-Wshadow`
  note on `wg` in P3's body said *"`GenNames g` is in scope here"*, which
  stopped being true the moment the loop left `pcrec_emit_vm`. It now
  records that as history. A verbatim move would have shipped a false
  statement.
- **`vm_plan_capacities`'s call site unpacks into the names the emission
  already uses** rather than renaming ~60 downstream references to
  `caps.x`. coding_guide §1.7 and §4's editing principle: the rename buys a
  reader nothing and rewrites text sabotage rows sit on.

---

## 6. Validation, and what is owed

COMPLETE at handback — all of it:

- Per step (all nine): corpus argv sweep 3,938 × 3 streams BYTE-IDENTICAL;
  composition sweep 304 files / 74 artifacts BYTE-IDENTICAL; anchor
  integrity 0 mismatches of 282; `make strict` clean;
  `run_ir_listing.sh` 93/0; `make test-codegen` 8/9 with the FAIL set
  identical to the branch-point baseline.
- `[MECH-REACH]` probe for the DELIVER block: measured, both directions.
- Sabotage **S149: DETECTED** after its re-aim, re-driven solo.

- All seven re-aimed sabotage rows re-driven solo at the final SHA
  `8c142b9a`: `unexpected: 0`, `anomalies: 0`, `unreached: 0` on every run.
  §3's table has the per-row verdicts and cells.
- `bash tests/rxtsource/run_rxtsource_tests.sh`: **212 passed / 0 failed**,
  including `INV-COMPAT holds over 211 files / 3,938 blocks / 28,949
  expectation lines`.
- `bash tests/vm/run_vm_tests.sh`: **48 passed / 0 failed**.

NOTHING IS OWED. The full battery is the manager's at merge, as always.

**Rollback.** Nine independent commits, each mergeable on its own in EP2's
order. Reverting step 8 (P3) requires reverting its six anchor re-aims with
it; reverting step 6 (E0) requires reverting S149's.

**Next step for wave 2, slice B:** EP2 sequence **step 10 (X8, the stamp
pair, 52 sites)** — the only item in the sequence with an `abi` question
attached, which EP2 places AFTER stage 3 delivers `sb_name`/`sb_upper`. So
the genuinely next unblocked item is **step 11, lens 10 STAGE 3
(`sb_fragf` over the remaining buffers)**, whose population this slice just
reduced from 40 to 29 category-(a) statements.
