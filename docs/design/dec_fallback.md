# One fallback ladder — refactor B ([DEC-FALLBACK]): the row contract, the inventory, the no-mover refactor

**DESIGN NOTE, PROPOSED, REVISION 1, nothing built.** Lane `decfbdes`,
2026-10-08, from main `31a9ae4c` (abi 68). Nothing under `src/`, `cli/`,
`lib/` or `tests/` changes in this lane. The instruments and their committed
output are in `dec_fallback/` (own CLAUDE.md). Rulings are Frank's; §11 lists
the open questions, each with a recommendation.

The shape copies refactor A (`start_table.md` rev 2.1): the edit set and its
instruments, the no-mover gates, a commit plan with derived sabotage re-aims,
and the lessons of A's build (`../dev/lanes/stc5_report.md`, `stc5b_report.md`,
`stc67_report.md` §4).

**The contract, as ruled.**
- Today's tokens are kept; B is a pure no-mover (D151 addendum 2, item 1).
- B comes after A. Its STEP 0 census ran after C7 (lane decfb0).
- B absorbs `start_table.md` Q8, the prefilter admission ternary.
- The movers are later, separate rows, never folded in.

**Read before writing.**
- `decision_families_survey.md` §3.1, §4.1, §4.5, §4.6.
- `../dev/lanes/decfb0_report.md` and `decision_families/decfb0/results.md`
  (the STEP 0 census).
- `../dev/lanes/nullanch1_report.md` §1 (the `empty_admits` fact, F1).
- `sel_cost.md` §4.
- D151 and its addenda, D152, D153.
- `../spec/limits.md` §8 ("The size-cap ladder").
- The table sites in `src/core/compile.c`, `src/opt/select_engine.c`,
  `src/gen/emit_vm.c`, `src/gen/emit_dfa.c` and `src/dump/axes_dump.c` at
  this pin.

---

## R. Panel disposition

None yet. §11 Q8 recommends a light D6 panel (two critics, sound and checks),
A's shape, before the build lane starts.

---

## 0. Answers first

1. **What B builds.** Four first-match tables, plus one attribution walk that
   READS them. B adds no new decision.
   - **T1 `fit_rungs[]`**, the ONE fallback ladder. It is today's six size-cap
     rows plus four new ones: `nomem` (K60's propagation),
     `size-term-trial` ([ART-SIZE]'s "this K is out"), `sel1-collapse` and
     `sel1-drop` ([SEL-1]).
     - Rows are keyed by the ARRIVAL LABEL SET (`nomem | overflow | size |
       other`, §1.1) in an `on` column.
     - Each row carries its state writes as data (`sets`) and its tokens as
       cells.
     - The `ovf_eligible`/`retry_collapse`/`retry_drop` block
       (`compile.c:1277-1307`) and the `cx.size_cap_refused ? fit_select :
       refuse` dispatch (`:1316-1319`) become one walk.
   - **T2 `pf_admits[]`**, the prefilter admission: Q8, the 4-clause ternary
     at `select_engine.c:879-886`. It is merged with its SECOND derivation,
     the `--emit-ir` "prefilter" reason chain (`emit_vm.c:9443-9541`). The
     verdict cell is the ternary's answer and the listing cells are the
     chain's tokens. The two orders differ today (§2.2), and the merged order
     reproduces both.
   - **T3 `pflw_rows[]`**, the collapse build gate (`compile.c:1806-1873`)
     with its `VM_PREFILTER_LANG_WHY` reason, written from one row (D81's
     "decision and reason together", as a table).
   - **T4 `st_whys[]`**, the 7-arm `UNROLL_K_WHY` ternary (`compile.c:1977-1984`).
   - **The attribution walk** replaces `esel_of`'s 8-arm ternary
     (`select_engine.c:960-994`). In order:
     1. `forced`;
     2. else the admission row's ESEL cell;
     3. else the last ATTRIBUTING ladder row's cell, keyed on whether the
        final prefilter survived;
     4. else `selected`.

     `VM_PREFILTER_WHY` (`emit_vm.c:11264`) and the three drop notes
     (`compile.c:2239-2254`) read the fired row's cells.
2. **No mover: tokens, attempts and listing are all held.**
   - **Tokens.** Every value of `ENGINE_SEL`, `UNROLL_K_WHY`, `VM_PREFILTER`,
     `VM_PREFILTER_LANG`, `VM_PREFILTER_LANG_WHY` and `VM_PREFILTER_WHY`
     (`match_api.md` §6.3) is unchanged. So are the `--emit-ir` prefilter
     tokens and prose, and the stderr notes.
   - **Attempts.** The attempt COUNT and ORDER are unchanged, including every
     wasted attempt. `COMPILE_MAX_ATTEMPTS` keeps the value 25. The hand
     formula is kept and is now CHECKED against the table (§1.8).
   - **Listing.** `--list-axes` is byte-identical through B6. B7 is the one
     declared listing commit, as C7 was.
3. **F1 is PRESERVED byte for byte** (Frank's ruling).
   - Nine corpus `^${v…}$` rows stamp `declined-nullable-default` although
     `has_var` is what turns their prefilter off.
   - Today that lives in a `has_var ? nullable : empty_admits` ternary inside
     `lang_nullable_declinable` (`select_engine.c:855-857`). In B it is one
     visible ROW of T2 (`var-nullable`, §1.4), the ternary is gone, and the
     row is the F1 holder.
   - F1's fix is a separate later mover row. B makes it a one-row deletion
     plus one listing cell (§5.2).
4. **The §4.1 drift fix is NOT in B.** In B it is a one-column edit to the
   two collapse rows (§5.1). This note splits the fix in two, a split the
   survey and decfb0 did not draw:
   - the missing `pfc_rep` conjunct removes wasted attempts (a compile-time
     mover);
   - the nullable conjunct would MOVE TOKENS (`declined-nullable` →
     `overflowed-*` / `size-cap-retry`), because [OPT-4.1] DESIGNED the
     "offered and declined" outcome.

   The later row should take the first half only (§11 Q5).
5. **§4.5 and §4.6 under B** (§6).
   - §4.5 (`--emit-ir` names `-fno-prefilter` for a [PF-DROP] artifact) is
     PRESERVED. In B it is one cell: the `forced-off` admission row's listing
     cell is shared by the caller's bit and [PF-DROP]'s OR'd bit.
   - §4.6 (`engine-route` listed order ≠ evaluated order) is fixed with ZERO
     artifact movers. It does move `--list-axes`, so it is B7's declared
     listing commit: one swap of two listed orders, `kind` `predicate` →
     `list`, and two corrected descs.
6. **New findings** (§10).
   - **F-B1.** The `--emit-ir` chain has no `has_var` arm. A non-nullable
     `${…}` pattern compiled under `auto` lists
     `no-engine-vm  --engine=vm -- …`, a flag the caller never passed
     (PROBED, `a${v}b`). It is §4.5's sibling and is preserved.
   - **F-B2.** The `declined-nullable-default` listing desc ("auto (or forced
     --engine=vm plus -fprefilter)") is FALSE: that invocation stamps
     `forced` and builds a hybrid (PROBED).
   - **F-B3.** `collapsed-prefilter` is stamped whenever the [SEL-1] collapse
     retry kept ANY prefilter, collapsed or not. Its corpus population is 0;
     it closes structurally with §5.1's fix.
   - **F-B4.** Both failure labels can be set on one arrival only through the
     optional anchored machine, which restores the flag. T1's label-set walk
     reproduces today's precedence either way.
7. **Siblings** (§7). Hosted in B: the ladder, [SEL-1], K60's propagation, the
   size-term trial catch, the admission (Q8 and the listing chain), the
   collapse gate and PFLW, `UNROLL_K_WHY`, `ENGINE_SEL`, `VM_PREFILTER_WHY`,
   and the notes. Declared NOT hosted, with reasons:
   - the auto engine choice ([SEL-COST]'s `sel_auto_rows[]`, D124);
   - `forces_dfa_overflow`;
   - the do-or-die request refusals ([OPT-SETS]' constraint table);
   - `size_term_choose`'s argmin (an optimizer inside one row);
   - the `--tune` flag ORs;
   - the start table.
8. **[SEL-COST] §4 and `--fast-or-fail`** (§8).
   - [SEL-COST]'s post-build rows land as a fifth arrival label (`cost`) with
     their own T1 rows.
   - `--fast-or-fail`'s reach becomes a visible per-row column, `fof`. It is
     true on the five size rows and false on the [SEL-1] rows, today's scope
     exactly.

---

## 1. The row contract

### 1.1 The arrival label set

An arrival is one `longjmp` to `compile_driver`'s recovery point
(`compile.c:1167`'s catch branch). Today it carries three flags, read in a
fixed order (`:1203`, `:1229`, `:1277`, `:1316`). B names them once:

| label | set by | meaning |
|---|---|---|
| `nomem` | `pcrec_ctx_nomem` (`compile.c:52`) | a genuine allocation failure (K60) |
| `overflow` | `src/ir/dfa.c:203,1248,1315,1330` | a DFA state, context or work cap declined a machine |
| `size` | `compile.c:2157` | an emitted-size cap refused the artifact |
| `other` | every other `pcrec_ctx_fail` | a refusal no rung can rescue |

`label = nomem | (dfa_overflowed ? overflow : 0) | (size_cap_refused ? size :
0)`, and it is `other` when none is set.
- **Both `overflow` and `size` can only be set together through an optional
  machine.** The one optional machine, the anchored match-here DFA, saves and
  restores `dfa_overflowed` (`compile.c:360-370`), so no shipped arrival
  carries both.
- The walk is defined on the SET anyway, so its precedence is today's code
  order whatever the set (F-B4, §10).
- The `overflow` label carries one ATTRIBUTE, `dfa_overflow_is_budget` (the
  [LIM-2] N1 budget note). It is an attribute and not a row: the note prints
  for either [SEL-1] row (§1.3).

### 1.2 T1 `fit_rungs[]`: the columns

Today's columns stay: `name`, `deny`, `degrading`, `applies`, `act`. B adds:

| column | type | meaning | no silent default |
|---|---|---|---|
| `on` | label mask | the arrival labels the row is asked on | every row states it |
| `fof` | bool | `--fast-or-fail` may deny this row (when `degrading`) | stated on every row; `false` on the [SEL-1] rows is today's scope, not a default |
| `sets` | struct | the cross-attempt state the row writes: `dfa_disabled` (SET/KEEP), `collapse_reason` (a `CR_*` value/KEEP), `size_drop_rung` (an `SDR_*` value/KEEP), `flags_or` (bits), `restart_term`, `carry` (`overflow_why`, `size_cap_*`), `latch` (`dfa_was_engine`/`budget_fallback`, first overflow only) | KEEP is a named token, never 0-means-keep |
| `esel` | pair `{kept, off}` | the `ENGINE_SEL` this row attributes when the FINAL prefilter survived (`kept`) or did not (`off`); `ESEL_PASS` = attributes nothing | `ESEL_PASS` is named |
| `pflw` | `PFLW_*` / `PFLW_PASS` | the `VM_PREFILTER_LANG_WHY` value this row makes when the collapse it set builds | named |
| `pfwhy` | format / NONE | `VM_PREFILTER_WHY`'s text | named |
| `ukw` | token / PASS | `UNROLL_K_WHY` contribution (only `unroll-rescue` → `cap-rescue`) | named |
| `note` | `{what, cost}` / NONE | the stderr drop note | named |
| `retries` | 0/1 | attempts this row adds when it fires (feeds §1.8) | stated |

**Rows, in walk order:**

| # | row | on | applies (verbatim from today) | deny | degr. | fof | sets | esel {kept, off} | pflw | note |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `nomem` | nomem | always | — | no | — | PROPAGATE (refuse, keep the diagnostic) | PASS | PASS | — |
| 2 | `size-term-trial` | overflow, size, other | `st_phase == ST_LADDER` (`:1229`) | — | no | — | TERM_NEXT (`:1230-1247`) | PASS | PASS | — |
| 3 | `sel1-collapse` | overflow | `engine == AUTO && !FORCE_PREFILTER && !dfa_disabled` (`:1277-1282`) | `NO_PREFILTER_COLLAPSE` | yes | **no** | dd=SET, CR_SEL1, carry `overflow_why`, latch | {`collapsed-prefilter`, `overflowed-{role}`} | `PFLW_SEL1` | — |
| 4 | `sel1-drop` | overflow | `engine == AUTO && !FORCE_PREFILTER && (!dfa_disabled ∥ CR == CR_SEL1)` (`:1283-1284`) | — | yes | **no** | dd=SET, CR_NONE, carry, latch | {`overflowed-{role}`, `overflowed-{role}`} | PASS | — |
| 5 | `unroll-rescue` | size | NULL (chosen inside `size_term_choose`) | — | yes | yes | — | PASS | PASS | — |
| 6 | `prefilter-collapse` | size | `fit_collapse_applies` (`:683`) | `NO_PREFILTER_COLLAPSE` | yes | yes | CR_SIZECAP, carry `size_cap_*`, restart | {`size-cap-retry`, `selected`} | `PFLW_SIZECAP` | — |
| 7 | `drop-anchored` | size | `fit_anchored_applies` | — | yes | yes | SDR_NO_ANCHORED | {`size-cap-retry`, `size-cap-retry`} | PASS | anchored |
| 8 | `drop-premul` | size | `fit_premul_applies` | — | yes | yes | SDR_NO_PREMUL, `flags_or` NO_PREMUL_TABLE | same | PASS | premul |
| 9 | `drop-prefilter` | size | `fit_prefilter_applies` | — | yes | yes | SDR_NO_PREFILTER, `flags_or` NO_PREFILTER, carry, restart | same | PASS | prefilter (+ `pfwhy`) |
| 10 | `refuse` | every label | always | — | no | — | REFUSE | PASS | PASS | — |

`overflowed-{role}` is ONE cell with two spellings, keyed on the latched
`dfa_was_engine`: `overflowed-dfa` when the DFA was to be the engine,
`overflowed-prefilter` otherwise. This is `esel_of` arms 8/9 as data.

**Why each cell is today's behaviour.**
- **Rows 3-4.** The block offers collapse when it is eligible, and drop
  otherwise or after a failed collapse. `retry_collapse ? CR_SEL1 : CR_NONE`
  (`:1299`) makes row 3 win where both apply. Denying row 3
  (`-fno-prefilter-collapse`) makes it transparent and row 4 fires on the
  first overflow, which is `retry_drop`'s `!dfa_disabled` disjunct.
- **Row 4's `kept` cell is `overflowed-{role}`.** The ESEL arm order means a
  surviving prefilter after `sel1-drop` is impossible: CR_NONE plus
  `dfa_disabled` drops it, `select_engine.c:880`. So the cell's spelling is
  unobservable, and the self-check asserts the impossibility (§1.9).
- **Row 6's `off` cell is `selected`.** That is `esel_of` note (C): a
  size-cap-refused VM compile that ends with no prefilter, for a reason other
  than the nullable decline, falls to arm 6.
- **Rows 7-9 stamp `size-cap-retry` whatever the prefilter.** That is arm 5,
  which has no `fit->prefilter` conjunct (note D).

### 1.3 The walk and the state

`fit_walk(sel, labels)` walks T1 in order. A row is asked only when `on &
labels`. It is skipped when `applies` is NULL, when its `deny & flags` is set,
or when `degrading && fof && (flags & PCREC_FAST_OR_FAIL)`. The first row
whose `applies` holds fires. Row 10 always applies, so the walk is total.

The `sets` cell is applied by ONE generic action routine. Today's switch at
`:1321-1474` keeps only the cases whose action is code: PROPAGATE, TERM_NEXT,
REFUSE. The rest are data.

**The cross-attempt state is UNCHANGED in name and meaning**: `dfa_disabled`,
`collapse_reason`, `size_drop_rung`, `dfa_was_engine`, `budget_fallback`,
`size_cap_*`, `overflow_why`, `st_*`. What changes is WHO writes it: only the
row's `sets` cell does. It is still read where it is read today: every
`applies` predicate, `select_engine.c`'s admission (T2), `build_anchored_dfa`
(`:354`) and `forces_dfa_overflow` (`select_engine.c:392`).

Two records are added:
- **`fit_fired`**, a bitmask of rows fired in this compile (each fires at
  most once, §1.8). The notes read it in table order, which is today's
  `dropped_*` order. The three `dropped_*` booleans are retired.
- **`fit_last`**, the last fired row whose `esel` is not PASS. The
  attribution walk reads it (§1.7).

Neither is an artifact byte. Both are seeded into each attempt's `Ctx` as
`collapse_reason` is today (`:1062`).

**Why the state survives.** Replacing `CR_*`/`SDR_*` by row pointers would
re-aim every row and check that names them (§4.4). It would also break A's
rule that a reader reads a row's PAYLOAD, never its identity
(`dfa_search_is_pinned`, start_table.md [r2 sound-m2]). The state values ARE
the payload: a row writes `CR_SEL1`, and readers test `CR_SEL1`.

### 1.4 T2 `pf_admits[]`: the prefilter admission (Q8)

**Two derivations today.**
- The VERDICT is `select_engine.c:879-886`: the first clause (`has_bref ∥
  has_call ∥ has_var ∥ (dd && CR ≠ SEL1) ∥ dn ∥ dnd`) → off, then
  `force_on` → on, then `force_off` → off, then `would_prefilter`.
- The LISTING's reason is `emit_vm.c:9443-9541`: verdict on → `yes` /
  `yes-collapsed`; then `has_bref`, `has_call`, `dn`, `dnd`, `dd`, the
  `NO_PREFILTER` flag, else `no-engine-vm`.
- They test the same facts in DIFFERENT orders, and the listing chain has no
  `has_var` arm.

**The merged table.** Every row's verdict equals the ternary's and every row's
listing token equals the chain's, on every input (argued per row below;
checked by B2's oracle on the corpus × 4 variants):

| # | row | predicate | verdict | listing value (DD-8 token) | ESEL cell (scope) |
|---|---|---|---|---|---|
| 1 | `backref` | `has_bref` | off | `no-backreference` | — |
| 2 | `linked-call` | `has_call` | off | `no-linked-call` | — |
| 3 | `var-nullable` **[F1 holder]** | `CR == NONE && !dd && would_prefilter && has_var && nullable && !force_on` | off | `no-nullable-exact` | `declined-nullable-default` |
| 4 | `nullable-exact` | `CR == NONE && !dd && would_prefilter && empty_admits && !force_on` | off | `no-nullable-exact` | `declined-nullable-default` |
| 5 | `nullable-collapsed` | `CR ≠ NONE && empty_admits && collapsible_rep && !force_on` | off | `no-nullable-collapsed` | `declined-nullable` |
| 6 | `overflow-drop` | `dd && (CR ≠ SEL1 ∥ force_off)` | off | `no-dfa-overflow` (+ `overflow_why`) | — |
| 7 | `forced-on` | `force_on` | on | `yes` / `yes-collapsed` | — |
| 8 | `forced-off` | `force_off` | off | `no-fno-prefilter` (§4.5, preserved) | — |
| 9 | `var` | `has_var` | off | `no-engine-vm` (F-B1, preserved) | — |
| 10 | `default` | always | `would_prefilter` | `yes` / `yes-collapsed` if on, else `no-engine-vm` | — |

**Why it equals both derivations.**
- **Rows 1-2.** `lang_nullable_declinable` carries `!has_bref && !has_call`,
  so rows 3-5 exclude them, and their order against 3-5 is free.
- **Rows 3-5 are today's two flags** `prefilter_declined_nullable_default`
  (`:876-878`) and `prefilter_declined_nullable` (`:873-875`). Two facts make
  the `has_var` ternary unnecessary:
  - (a) `empty_admits ⇒ nullable` (the E1 seal asserts it, nullanch1 §1), so
    rows 3 then 4 compute exactly `(has_var ? nullable : empty_admits)`;
  - (b) the rung scope (row 5) has no `has_var` population. `has_var` makes
    `fit.prefilter` false, so no prefilter machine is built and neither
    collapse rung is ever offered. The self-check asserts `has_var ⇒ CR ==
    NONE && !dd` (§1.9).

  Rows 3-4 and row 5 are disjoint on `CR`, so their order is free. The order
  chosen (default before rung) is the one that minimises B7's listing move
  (§6.2).
- **Row 6** is the verdict's `(dd && CR ≠ SEL1)` clause. It also catches
  `dd && CR == SEL1 && force_off`: the ternary answers that off through
  `force_off`, while the listing answers `no-dfa-overflow` because the chain
  tests `dd` before the flag. One row gives both.
  - `dd && force_on` cannot arise: no retry is offered under `-fprefilter`.
  - `dd && CR == SEL1 && !would_prefilter` cannot arise: a retry is
    auto-only, and `dd` forces the VM.
- **Row 8 before row 9.** The listing chain has no `has_var` arm, so a
  `has_var` pattern lists the flag when `-fno-prefilter` is passed, else
  `no-engine-vm`. `force_on && has_var` is refused before the table
  (`select_engine.c:696`).

### 1.5 T3 `pflw_rows[]`: the collapse gate and its reason

Today (`compile.c:1806-1870`):
- `pfc_wanted = chosen ≠ DFA && !deny && pfc_rep && (force ∥ rung)`;
- `collapse = pfc_wanted && (force_prefilter ∥ !nullable)`;
- the 6-way PFLW ternary.

As rows, each writing `collapse` and `prefilter_lang_why` together (D81):

| # | row | predicate | collapse | PFLW |
|---|---|---|---|---|
| 1 | `rung` | `wanted && (fpf ∥ !nullable) && CR ≠ NONE` | yes | the T1 row that set CR: its `pflw` cell (`SIZECAP` row 6, `SEL1` row 3) |
| 2 | `forced` | `wanted && (fpf ∥ !nullable)` | yes | `PFLW_FORCED` |
| 3 | `nullable` | `wanted` | no | `PFLW_NULLABLE` |
| 4 | `exact` | `pfc_rep` | no | `PFLW_EXACT` |
| 5 | `no-rep` | always | no | `PFLW_NO_REP` |

The T1 row that set CR is found by a projection, `fit_row_setting_cr(CR)`: the
unique row whose `sets.collapse_reason` equals CR. This is A's
`fit_rung_of(act)` shape and a payload read, not identity. The self-check
asserts uniqueness. The `PFLW_*` enum values and their order are unchanged, so
`>= PFLW_FORCED` iff collapsed still holds (`internal.h:2390`).

### 1.6 T4 `st_whys[]`: `UNROLL_K_WHY`

Seven rows in today's ternary order (`compile.c:1977-1984`): `option`,
`denied`, `default`, `cap-rescue`, `size-model`, `capacity-declined`,
`size-model-declined`. `cap-rescue` is `unroll-rescue`'s `ukw` cell projected;
its predicate is `st_rescue`, set inside `size_term_choose`.
- The `size-term` listing already prints these in this order
  (`axes_dump.c:543-565`), so §4.7's precedence becomes stated rather than
  implicit.
- The precedence sentence for `tuning.md` §2.16 rides B7 (§4.2).

### 1.7 The attribution walk (`ENGINE_SEL`)

`esel_of` stays one function, at its one call site (`select_engine.c:1125`),
with its premise check kept (`:976`). Its body becomes:

```
if (engine != AUTO)                 return ESEL_FORCED;
if (admit_row->esel != ESEL_PASS)   return admit_row->esel;      /* T2 rows 3-5 */
if (fit_last)                       return fit->prefilter ? fit_last->esel.kept
                                                          : fit_last->esel.off;
return ESEL_SELECTED;
```

**Equivalence to the 9-arm table (`select_engine.c:909-919`), arm by arm.**
- **Arm 1** is line 1.
- **Arms 2-3** are the admission cells. They precede every ladder cell, as
  arms 2-3 precede arms 4-9. This matters on a `CR_SIZECAP` compile where
  `dn` holds: arm 3 must beat arm 6, and it does.
- **Arms 4-5** are rows 6-9's cells.
- **Arm 6 (`!dd → selected`)** has two routes:
  - no attributing row fired: the fallback;
  - row 6 fired and the prefilter did not survive: row 6's `off` cell.
- **Arms 7-9** are rows 3-4's cells.

**Why "last attributing row" equals the state test.** Every row sequence the
loop can take was enumerated (row order = firing order; at most one per row):
- `sel1-collapse`, then optionally `sel1-drop`;
- `prefilter-collapse`, then optionally `drop-prefilter`;
- `drop-anchored`, then optionally `drop-premul`;
- `prefilter-collapse` then `sel1-collapse` (then `sel1-drop`): the collapsed
  prefilter overflows a DFA cap.

In each, the last row's cell is what arms 4-9 compute from (CR, SDR, dd,
`dfa_was_engine`).
- After `sel1-drop` the CR is NONE and arm 8/9 decides.
- After `drop-prefilter` the SDR is set, so arm 5.
- After `prefilter-collapse` → `sel1-collapse` the CR is SEL1 and dd is set,
  so arm 7 or 8/9; `dfa_was_engine` was latched at the first overflow, on the
  VM, which is `overflowed-prefilter`.

A size row after a [SEL-1] row cannot occur:
- rows 6 and 9 need `!dd` or an uncollapsed prefilter;
- rows 7-8 need a DFA engine, and an overflow made the engine the VM.

`esel_of`'s premise check (`:976`) is today's assertion of that and stays.
The census confirms the enumeration: decfb0's attempt signatures contain only
these sequences in all four variants.

B2's both-derivations oracle (§4.3) holds the walk to the old ternary on every
compile of the corpus × the four limit variants × the flag arms.

### 1.8 `COMPILE_MAX_ATTEMPTS`

Today it is the hand formula `3 + 3·(N+1) + 1 + SDR_MAX` = 25 (N = 5,
`compile.c:479`), commented rung by rung. The table bound is:

`1 + Σ retries(r) + (1 + Σ restart(r)) · (N + 1)` = 1 + 6 + 3·6 = 25.

The terms: six retrying rows (3, 4, 6, 7, 8, 9); two restarting rows (6, 9);
`size-term-trial`'s attempts are the `(N+1)` term per run.
- B keeps the enum's value, its text and the exhaustion diagnostic
  (`:2303-2307`) byte for byte.
- It adds a self-check that the formula EQUALS the table bound. A new row
  then fails the check rather than silently truncating the search, the
  failure mode `:2294-2301` records.
- Turning the table into an X-macro `.def` so C could derive the constant is
  possible. It is not proposed: no measured need (D77).

### 1.9 The self-check (one function, trace build + a unit check)

`fit_tables_selfcheck()` asserts, by REFUSING (never `abort`, the
`esel_of:976` rule):
- each label has a total walk (row 10 applies to every label);
- every cell an action READS is stated (`ESEL_PASS`, `PFLW_PASS`,
  `SETS_KEEP` and NONE are named tokens, memory `pcrec-no-silent-defaults`);
- every row with `degrading` true has its `fof` stated;
- `COMPILE_MAX_ATTEMPTS ==` the §1.8 bound;
- each `CR_*` value other than NONE is written by exactly one T1 row (T3's
  projection);
- T2's last row always applies;
- the run-time invariants `has_var ⇒ CR == NONE && !dd` (§1.4(b)) and "row 4
  never sees a surviving prefilter" (§1.2).

The last two are checked at their read site in the trace build only, so the
default build gains no code.

---

## 2. The inventory, and how it was derived

### 2.1 The reader census (K35)

The member list is not hand-kept. `dec_fallback/state_readers.sh` greps every
CODE line under `src/` (comment lines dropped) that names one of the family's
state fields or token derivations. Its output is
`dec_fallback/state_readers.txt`: 164 lines, of which compile.c 76,
internal.h 33, select_engine.c 25, emit_vm.c 16, emit_dfa.c 8, ir/dfa.c 4.

Each line is one of:
- a member below;
- a declaration in `internal.h`;
- a WRITER of a label (`ir/dfa.c`, `compile.c:52`, `:2157`), which B does not
  change;
- a reader B keeps on purpose (`build_anchored_dfa:354`,
  `forces_dfa_overflow:392`, the `applies` bodies).

A build lane re-runs the script on its own base. Any line outside those four
classes is an undispositioned member and stops the lane.

### 2.2 The members

| site (main `31a9ae4c`) | what it decides today | in B |
|---|---|---|
| `compile.c:632-680` `FitSel`/`FitAct`/`FitRung` | the size-cap row type | gains `on`/`fof`/`sets`/token columns (B2) |
| `compile.c:683-721` the four `fit_*_applies` + `fit_always` | the rows' predicates | UNCHANGED bodies (S237/S252/S420 anchor here; §4.4) |
| `compile.c:723-730` `fit_rungs[]` | the size-cap ladder | T1; four rows added (B2) |
| `compile.c:735-758` `fit_rung_denied`/`fit_rung_of`/`fit_select` | deny + walk | the walk takes the label set; `fof` joins the deny (B2) |
| `compile.c:1199-1203` the K60 propagation | nomem first | T1 row 1 (B3) |
| `compile.c:1229-1248` the size-term trial catch | "this K is out" | T1 row 2 (B3) |
| `compile.c:1277-1307` [SEL-1] `ovf_eligible`/`retry_collapse`/`retry_drop` | the overflow ladder | T1 rows 3-4 (B3) |
| `compile.c:1308-1487` the size-cap dispatch + switch | rung actions | the walk + the `sets` routine (B3) |
| `compile.c:897-916` the `dropped_*` flags | which drops fired | `fit_fired` (B3) |
| `compile.c:2227-2254` budget note + drop notes | stderr | label attribute + the rows' `note` cells (B3) |
| `compile.c:479` `COMPILE_MAX_ATTEMPTS` | the attempt bound | value kept, checked (§1.8, B2) |
| `compile.c:1806-1870` the collapse gate + PFLW ternary | language + reason | T3 (B5) |
| `compile.c:1977-1984` `size_term_why` | `UNROLL_K_WHY` | T4 (B5) |
| `select_engine.c:855-886` `lang_nullable_declinable` + the two flags + the ternary | the prefilter admission | T2 (B4) |
| `emit_vm.c:9443-9541` the `--emit-ir` prefilter chain | the listing's reason | T2's listing cells (B4) |
| `select_engine.c:960-994` `esel_of` | `ENGINE_SEL` | the attribution walk (B5) |
| `emit_vm.c:11264-11267` `VM_PREFILTER_WHY` | its own `SDR` test | the fired row's `pfwhy` (B5) |
| `emit_vm.c:11314-11361` the PFLW stamp switch | format | UNCHANGED (it formats; it decides nothing) |
| `emit_dfa.c:447-462` `pcrec_engine_sel_name` | the one spelling | UNCHANGED |
| `axes_dump.c:542-565`, `:604-612`, `:950-997` | the three listings | projections (B6), declared move (B7) |

### 2.3 What B does NOT change, stated so a diff can be held to it

- No predicate body changes (the four `applies`, the admission's facts, the
  gate's conjuncts).
- No `CR_*`, `SDR_*`, `ESEL_*` or `PFLW_*` value is renumbered.
- No `Ctx`/`EngineFit` field is renamed: `prefilter_declined_nullable`,
  `prefilter_declined_nullable_default`, `prefilter_lang_why` and
  `size_term_why` are now written from rows. `tuning.md:1463` cites
  `prefilter_lang_why`, so no spec hunk is needed for it.
- No deny bit is added, moved or reassigned.

---

## 3. What B preserves on purpose (each a later, separate row)

| item | today | where it lives in B | the later row |
|---|---|---|---|
| F1 | `^${v…}$` stamps `declined-nullable-default` (9 corpus rows) | T2 row 3 `var-nullable` | §5.2 |
| F-B1 | `a${v}b` lists `no-engine-vm` "--engine=vm" | T2 row 9's listing cell | §5.2 (same row as F1) |
| §4.5 | a [PF-DROP] artifact lists `no-fno-prefilter` | T2 row 8's listing cell, reached by the OR'd bit | §6.1 |
| §4.1 | the collapse rows lack `pfc_rep` | T1 rows 3 and 6, column `requires` = `FIT_REQ_NONE` | §5.1 |
| F-B2 | `declined-nullable-default`'s false desc | the listing's desc, moved verbatim at B6 | B7 corrects it (a listing change, not an artifact one) |
| F-B3 | `collapsed-prefilter` without a collapse | T1 row 3's `kept` cell | closes with §5.1 |
| §4.6 | listed order ≠ evaluated | the listing's `list` column, today's order verbatim at B6 | B7 |
| D-3-like | `size-cap-retry`'s desc names only the [OPT-4] rung | the listing's desc | B7 |
| token/why separation | one token carries both | `esel` and `pfwhy`/`pflw` are already separate columns | the abi row D151 addendum 2 names |

---

## 4. The no-mover refactor plan

### 4.1 Principles (A's, restated for B)

- **Implement, then replace.**
  - T1 is EXTENDED in place, keeping its name: the brief says fold into
    `fit_rungs[]`, and a rename re-aims rows for nothing.
  - T2-T4 are built beside their ternaries, and readers switch commit by
    commit.
- **The edit set is data**: `dec_fallback/refactor_edit_set.tsv`.
  - **Grain** (`stc67_report.md` §4 item 2): `def` only for a definition
    deleted, new or rewritten throughout; otherwise the changed `token` or
    `line`.
  - A commit that edits a line the file does not name is out of plan.
  - The re-aim list is DERIVED from the file (§4.4), never prose.
- **Every commit is a no-mover with no abi event.** The exception is B7,
  which is stream-5-only and also not an abi event.
- **The build lane re-derives on its own base.** It re-runs `state_readers.sh`,
  the edit set's line check (`sabotage_anchors.py`), and
  `sabotage_anchors.py --step` per commit (admin1008b's diff-derived
  `rerun_at`). Main moves under a design note.

### 4.2 The commit sequence

| commit | what | what moves |
|---|---|---|
| B0 | **Instrument** (no `src/`): see the list after this table. | nothing in `src/` |
| B1 | **The fallback trace** under `-DPCREC_CAND_TRACE` (`#ifdef` text only), on C1's macro `PCREC_CAND_TRACE_REC(slot, route, row, site)`. ONE trace stream, no parallel mechanism: slot `fallback` (route = the label set, row = the rung taken), slot `admit` (route = scope), slot `attrib` (route = the token kind, row = the token), declared literal site keys. The trace build is byte-swept against the default build. **Cross-record**: on B1's own base, the trace's attempt signatures equal decfb0's probed-copy signatures on all four variants. Two instruments with no shared source agree, and only then is the trace the gate. | nothing (`#ifdef` only) |
| B2 | **Implement**: T1's new columns and rows 1-4 (`fit_select` asks only `on & size`, so the new rows are transparent to it); T2, T3, T4 and the attribution walk beside the old code; `fit_tables_selfcheck`. No reader switched. Under the trace build, the **both-derivations oracle** compares the old branch against the walk at every arrival, and the old ternary against the row read at every token site. It aborts on any difference and runs in both orders (A's C2 shape). | the six `fit_rungs[]` row lines; `fit_select`'s filter line; `fit_rung_denied`'s `fof` line. Re-aims S421, S423 |
| B3 | **Replace the dispatch**. The catch branch's four tests (`:1203`, `:1229`, `:1277-1307`, `:1316-1319`) become ONE `fit_walk(labels)`. The `sets` routine writes the state. `fit_fired`/`fit_last` replace `dropped_*`. The notes loop over fired rows. The self-check runs. | re-aims S253, S259 |
| B4 | **Replace the admission**. `prefilter_decision`'s `lang_nullable_declinable`, the two flags (now written from the row) and the ternary become T2's walk. The `has_var` ternary is gone and row 3 is the F1 holder. The `--emit-ir` chain reads `fit.admit`'s listing cells; the tokens and prose move verbatim. | re-aims S102, S165, S216, S272, S612 |
| B5 | **Replace the token derivations**: `esel_of` → the attribution walk; the PFLW ternary → T3; `size_term_why` → T4; `VM_PREFILTER_WHY` → the fired row's `pfwhy`. The oracle has nothing left to compare and is deleted (A's C5 precedent). | re-aims S238, S422 |
| B6 | **The listing reads the tables**: `engine-route`, `size-term` and `prefilter-lang` (`axes_dump.c`) project T1/T2/T4/T3 through a `list` column. It carries TODAY's order, name and desc verbatim, D-3-like and F-B2 descs included. `--list-axes` is byte-identical. The registry's two dump-vs-source legs retire (§4.5). | nothing (stream 5 identical) |
| B7 | **Declared listing commit**, stream 5 only, NOT an abi event: see the list after this table. | `--list-axes` text only |

**B0's deliverables:**
- `emit_sweep.py` gains `--variant NAME=CFLAGS`, which builds BOTH sides with
  the variant's `-D` set. The four variants are decfb0's `plain`, `lowsize`,
  `lowdfa` and `lowboth` (`decision_families/decfb0/build_ref.py`).
- A seventh stream, `notes`: the CLI's stderr `pcrec: note:` lines per
  compile, compared verbatim. They are caller-visible, and the six existing
  streams do not see them.
- Per-variant DIFFER floors and NAMED manifests from decfb0's tables:
  - `lowdfa`: `overflowed-prefilter` 4, `collapsed-prefilter` 23,
    `overflowed-dfa` 60;
  - `lowsize`: `size-cap-retry` 132;
  - every variant: `declined-nullable` 1.

  An arm that silently drops its `-D` set reads identical to `plain` and
  fails the floor.
- The flag arms (§4.3 item 2), each with a floor measured at B0.
- The population census over the attempt count: decfb0's attempts table is
  pinned as an exact-count manifest per variant (§4.3 item 4).
- `state_readers.sh` and the edit set re-run on B0's base.
- B0 does NOT re-home decfb0's probed-copy census. Its probes anchor on code
  B3 deletes, so it can only run on a base, which is what the B1
  cross-record needs.

**B7's deliverables:**
- `engine-route` lists in the attribution order (§6.2: two listed orders
  swap).
- `kind` changes from `predicate` to `list` on `engine-route`, `size-term` and
  `prefilter-lang`.
- F-B2's and `size-cap-retry`'s descs are corrected.
- A precedence sentence goes into `tuning.md` §2.16 (§4.7) and §2.17.
- The spec hunk is `registry.md` §6.
- The `tests/registry/` pins are re-read (§4.5).
- Optionally, the two new axes of §11 Q4.
- The movement is declared in a cells file, `listing_declared_B7.tsv`, and
  checked by C7's `listing_diff.py`.

**Not split further.** B3-B5 could be fewer, larger commits. They are split so
that each re-aimed row is verified in the commit that moves it, which is A's
reason.

### 4.3 How each commit proves 0 movers

Run against the parent (`--ref HEAD~1`, both sides built from `git archive`):

1. **`emit_sweep.py`, all seven streams, `--features all`, × the four limit
   variants.** Identity on every stream is the TOKEN IDENTITY gate.
   - The streams carry every `match_api.md` §6.3 vocabulary this family
     writes: `ENGINE_SEL` (8 values), `UNROLL_K_WHY` (7), `VM_PREFILTER`,
     `VM_PREFILTER_LANG`, `VM_PREFILTER_LANG_WHY` (6 forms) and
     `VM_PREFILTER_WHY` in streams 1-2.
   - The `--emit-ir` prefilter tokens are in stream 3, the stderr notes in
     stream 7, and the listing in stream 5.
   - Reach is held at the floors B0 pinned.
2. **The flag arms**, each with a DIFFER floor and its row(s):
   - `-fno-prefilter-collapse` (rows 3/6 transparent);
   - `-fprefilter` (the [SEL-1] rows ineligible: overflows refuse);
   - `--fast-or-fail` (rows 5-9 denied; rows 3-4 NOT, the `fof` column);
   - `-fprefilter-collapse` (T3 row 2);
   - `-fno-size-term` and `--unroll=4` (T4 `denied`/`option`);
   - `-fno-premul-table` (row 8 inapplicable);
   - `-fno-anchored-dfa` (row 7 inapplicable);
   - `--engine=vm`/`--engine=dfa` (the `forced` line; row 10 refuses a DFA
     overflow).

   Each runs at `plain` and at its variant (the [SEL-1] arms at `lowdfa`, the
   size arms at `lowsize`). `capacity-declined` has no corpus witness in any
   variant. It runs as `tests/codegen/run_size_term.sh` §7's lowered-threshold
   cell, named in the arm list.
3. **The trace** (B1's build, parent reference regenerated every commit):
   - the SET compare for every slot (A's gate);
   - plus an ORDERED compare of the `fallback` records per pattern. An
     arrival's sequence IS the attempt ORDER, so for this family order is the
     property under test, not a false-alarm source (C1's set-compare
     condition was about cross-site ask order).
   - Records floor per variant.
4. **Attempt count and order**:
   - the per-pattern sequence of `fallback` records equals the parent's;
   - the per-variant attempt histogram equals decfb0's pinned tables exactly:
     `plain` 4,825 attempts / 33 beyond the first; `lowsize` 5,402 / 610;
     `lowdfa` 4,956 / 164; `lowboth` 5,408 / 616;
   - the attempt-signature table matches line for line.

   The histogram is the independent control. It was produced by a probed
   scratch COPY that shares no code with the tables.
5. **The both-derivations oracle** (B2-B4): in both orders, under the trace
   build, at every arrival and every token site. It is a FILTER test (the old
   and new code share every predicate by pointer, A's C2 caveat). The
   attempt histogram and the bytes are the independent controls.
6. `make test-codegen` (which runs [SABANCHOR]), the registry suite,
   `fit_tables_selfcheck` as a unit check, `state_readers.sh` against the
   commit, `sabotage_anchors.py`, and mech on every re-aimed row and every
   re-run row whose `rerun_at` names the commit. The full `make test` is the
   manager's at merge.

**The controls and what they share.**
- Bytes are compared against the parent's binary (`git archive`).
- The attempt histogram comes from a probed copy of the BASE (decfb0).
- The token vocabularies are the spec's hand-written tables, read by the
  registry's docs leg.
- None of them reads T1-T4 to decide what T1-T4 should say.
- The oracle shares predicates with its subject, and this note says so (item
  5).

### 4.4 Sabotage rows (derived)

`../start_table/sabotage_anchors.py ROOT call_graph.txt
dec_fallback/refactor_edit_set.tsv` at `31a9ae4c`, output
`dec_fallback/sabotage_anchors.tsv`: 535 sites / 517 row files, COUNT_MISMATCH
0. The one UNRESOLVED_SRC site (S571 in `memfn_sites.c:35`) is pre-existing
and outside this family.

**11 rows are RE-AIMED**, each in the commit that moves its anchor's text,
with intent re-verified:

| commit | rows | why |
|---|---|---|
| B2 | S421 (`--fast-or-fail` inert), S423 (`drop-prefilter` not degrading) | `fit_rung_denied`'s line gains `fof`; the row line gains columns |
| B3 | S253 (premul drop note unstamped), S259 (K60 propagation removed) | the state writes and the nomem test become rows |
| B4 | S102, S165, S272 (prefilter on backref / call / var), S216 (the default decline neutered), S612 (`empty_admits` anchor-blind) | the ternary and `lang_nullable_declinable` become T2 rows. S612's plant ("read bare `nullable`") moves to row 4's predicate; S272's to row 9 |
| B5 | S238 (size drop unstamped), S422 (`VM_PREFILTER_WHY` unstamped) | `esel_of` rewritten; the `SDR` test becomes a row read |

**RE-RUN** (anchor text kept, owner's body or reach changed by a commit). The
script's family is the START family, so the B family's re-run set is read off
owners:
- S237, S252, S420: the three `fit_*_applies` bodies, reached by the new walk
  (B2, B3);
- S189: `build_anchored_dfa` reads `size_drop_rung` written by a row (B3);
- S191, S192: `size_term_choose`, inside row 5/row 2's action (B3);
- S193: the size-cap label at `:2157` (B3);
- S64, S176: `prefilter_decision`'s untouched lines in a rewritten function
  (B4);
- S40: `pcrec_select_engine` calls the new `esel_of` (B5);
- S224, S225, S226: `vm_emit_stamps` around the `pfwhy` site (B5).

The build lane runs `sabotage_anchors.py --step` per commit to add what the
plan cannot see (stc5 §4 item 6).

**New rows** (planned; S-id = next free on main at build, S614+ today). Each
row's detector is IN a suite mech runs ([MECH-REACH]): a new
`tests/codegen/run_fallback_table.sh` with one witness per row, plus its
lowered-limit reference builds, `run_size_term.sh`'s shape.
1. `sel1-collapse` and `sel1-drop` swapped (the `lowdfa` witness's
   `ENGINE_SEL` moves `collapsed-prefilter` → `overflowed-*`).
2. `fof` true on the [SEL-1] rows (the `--fast-or-fail` × `lowdfa` witness
   refuses where it compiled).
3. Attribution precedence inverted, ladder before admission (the `CR_SIZECAP`
   + nullable witness moves `declined-nullable` → `selected`).
4. The F1 holder row deleted (`^${v}$` moves `declined-nullable-default` →
   `selected`, one of the 9 corpus rows).
5. Row 8/row 9 swapped in T2 (`-fno-prefilter a${v}b`'s listing moves
   `no-fno-prefilter` → `no-engine-vm`).
6. `fit_tables_selfcheck`'s bound check neutered with a planted row added
   (the check must fail).
7. The trace's ordered compare weakened to a set compare on `fallback`
   records (a planted swap of two [SEL-1] records must be reported). This
   row lives on the `emitsweep` arm.

### 4.5 Structural checks that parse the source

- **`tests/registry/axes_registry_check.sh:782`** extracts `RX_UNROLL_K_WHY`'s
  values from `compile.c`'s `cx.size_term_why =` chain. B5 deletes that text.
  - The leg fails LOUD (an empty extraction is its own K35 guard; check the
    exact behaviour at build and plant it).
  - From B6, the dump PROJECTS T4. A dump-vs-T4 leg would then be a control
    sharing its source with what it controls. `RX_VM_RESEED`'s precedent
    (`:788-795`) is the answer: RETIRE the source leg, keep the docs leg, and
    let `run_fallback_table.sh`'s witnesses (each of the seven values stamped
    once) be the emitter half.
- **The same applies to `:755`'s `pcrec_engine_sel_name` leg** once B6
  projects `engine-route`. Its witnesses must cover all 8 `ENGINE_SEL` values,
  and `overflowed-prefilter` exists only under `lowdfa`. So the witness file
  needs its lowered build, or the value is declared covered by the B0 floor
  arm.
- **`run_registry_tests.sh`'s PASS-count pins** move with the retired legs.
  This is D94 addendum's second reader class, a count that cites no number of
  B's. Re-pin by measurement in the same commit.
- **`tests/registry/limits_check.sh:525-528`** lists `SDR_*` names as
  non-limit enumerators. They are unchanged in B.
- **`run_resource_tests.sh`, `run_prefilter_collapse.sh` and
  `run_tune_dial.sh`** name `ovf_eligible`/`retry_collapse`/`fit_rungs[]`/
  `CR_*` in COMMENTS only (grep at `31a9ae4c`). They move with the commit
  that retires the identifier (B3), A's `reader_grep` rule.

### 4.6 Spec hunks

Readers of the retiring identifiers outside `src/` were found by grep.
- `docs/spec/` names `fit_rungs[]` (`limits.md:801`, unchanged: the name is
  kept), `dfa_disabled` (kept) and `prefilter_lang_why` (kept). So B1-B6 owe
  NO spec hunk.
- B7 owes:
  - `registry.md` §6 (the three `kind` flips; the listing order);
  - `tuning.md` §2.16 and §2.17 (the precedence sentences);
  - `limits.md` §8, only if §11 Q4 adds the ladder as a listed axis (a
    pointer sentence).

---

## 5. After B: the movers as table edits

### 5.1 §4.1's drift: a one-column edit

**Today.**
- `fit_collapse_applies` (`compile.c:683-689`) and `retry_collapse`
  (`:1280-1282`) both omit the build gate's `pfc_rep` conjunct
  (`PF_KIND_COLLAPSIBLE_REP`, `:1807-1808`).
- So a pattern with no collapsible counted repeat is offered a collapse that
  can only rebuild the same language, and the wasted attempt fails again.
- decfb0 measured it LIVE at shipped limits:
  - `(\p{Xwd})` under `-e utf8` is one size-cap waste;
  - one more is a [SEL-1] waste;
  - under `lowsize`/`lowdfa`/`lowboth` the wastes are 43/60/99.

**In B.** T1 rows 3 and 6 carry `requires = FIT_REQ_NONE`, a named token, the
drift preserved and declared. The fix sets `requires = fit_collapse_builds` on
both rows. That is ONE column, two cells, one table, one commit, where today
it is two code paths with two different conjunct lists. `fit_collapse_builds`
reads the same E1 bit the gate reads, so the two cannot drift again.

**What the fix moves — a finding this note adds.** The real gate has a SECOND
conjunct the rows lack: `!nullable` unless `-fprefilter`.
- decfb0's recommendation includes it. It must NOT be in the fix.
- On a nullable pattern WITH a collapsible repeat, the rung is offered and
  T2's `nullable-collapsed` row declines it. That is [OPT-4.1]'s designed
  outcome, stamped `declined-nullable` (plain: 1 corpus compile).
- Adding `!nullable` to `requires` would skip the rung and move that token to
  `overflowed-*` / `size-cap-retry`, a TOKEN mover.

So:
- **Fix (a), `pfc_rep` only**, is a compile-time mover. It removes the
  wasted attempts, at most decfb0's counts. Those counts are an upper bound:
  its "wasted" definition includes nullable-with-repeat size refusals, which
  (a) leaves alone.
- **Artifact neutrality is MEASURED, not STRUCTURAL.** On decfb0's
  population, every attempt after a [SEL-1] collapse that compiled had in
  fact collapsed (23/23 `lowdfa` tuples read `PFLW_SEL1`). A no-repeat
  pattern whose retry builds a prefilter that does NOT overflow would ship
  `collapsed-prefilter` (F-B3) today and `overflowed-*` after (a). That is a
  mover with population 0 measured.
- The later row's STEP 0 re-runs decfb0's census with the fate split by PFLW
  (`no-rep` vs `nullable`). It answers both questions and gives the exact
  delta. After (a), F-B3 is structurally unreachable: row 3 then fires only
  with a repeat, and a non-nullable repeat collapses.

### 5.2 F1 and F-B1: one row deleted, one cell changed

Recommended as ONE later row (§11 Q1):
- delete T2 row 3 (`var-nullable`): the nine `^${v…}$` rows move
  `declined-nullable-default` → `selected`, the truth (`has_var` turned the
  prefilter off, `selected` is what a non-nullable var pattern reads today);
- change row 9's listing cell from `no-engine-vm` to a new DD-8 token
  `no-variable`, with a note on the `no-backreference` pattern ("erasing a
  `${…}` variable is not a superset; no flag changes this").

It is a token mover and a listing-token mover, so it carries the spec hunk:
- `match_api.md` §6.3 `declined-nullable-default` wording;
- the `--emit-ir` vocabulary in `docs/spec/`;
- the abi decision by D76/D94. A stamp VALUE moves on 9 artifacts:
  [NULLABLE-ANCH] bumped for the same shape, and `sel_cost.md` §4.6 argues a
  new value of an existing stamp is not scaffolding. The ruling is the
  manager's at that row, by grep of readers.

### 5.3 `--fast-or-fail` over the [SEL-1] rows: one column, if ever wanted

`fof` is `false` on rows 3-4. Making the policy reach them is two cells. §8
recommends against it.

### 5.4 Token/why separation (D151 addendum 2, later abi row)

The columns are already separate: `esel` is the NAME and `pfwhy`/`pflw`/`ukw`
are the WHY. Separation then changes spellings in cells, not structure.

### 5.5 [SEL-COST]'s post-build rows

See §8.1.

---

## 6. §4.5 and §4.6 under B

### 6.1 §4.5: `--emit-ir` does not know [PF-DROP]

**The mechanism.** Row 9 (`drop-prefilter`) ORs `PCREC_NO_PREFILTER` into the
retry's options (`compile.c:1467`). On the next attempt T2's `forced-off` row
fires and lists `no-fno-prefilter`, naming a flag the caller never passed.
- The stamp side is right: `VM_PREFILTER_WHY` reads the FIRED ROW (row 9's
  `pfwhy`).

**In B.** §4.5 becomes "two writers of one input bit, and a listing cell keyed
on the bit instead of on the writer". The fix (a later listing mover) is a T2
row placed before `forced-off`: `dropped-for-size` (`fit_fired` has row 9,
off), with its own listing token `no-size-cap` and the `pfwhy` text as its
note. That is one row.

**Population.** One shipped-limit witness, `(\p{Xwd})` `-e utf8`, plus the
lowered variants (decfb0 §4.5, probed on `lowsize`).
- It is a LISTING mover: `--emit-ir` stream only, no `.c` byte.
- It is not in B, so it is filed and recommended together with §5.2's row: one
  listing-vocabulary change, one spec hunk (§11 Q1).

### 6.2 §4.6: `ENGINE_SEL`'s listed order ≠ evaluated order

**Under B5 the evaluated order IS the table order.** It is the attribution
walk: `forced`, then T2 cells in T2 order, then T1 cells in T1 order, then
`selected`.

Listing each value at its FIRST producing cell gives:

| order | today's listing | B7's listing |
|---|---|---|
| 1 | forced | forced |
| 2 | declined-nullable-default | declined-nullable-default |
| 3 | collapsed-prefilter | **declined-nullable** |
| 4 | declined-nullable | **collapsed-prefilter** |
| 5 | overflowed-dfa | overflowed-dfa |
| 6 | overflowed-prefilter | overflowed-prefilter |
| 7 | size-cap-retry | size-cap-retry |
| 8 | selected ("always (fallback)") | selected (the walk's fallback, and row 6's `off` cell) |

So §4.6 is fixed with **zero artifact movers** (no `ENGINE_SEL` value moves
on any artifact; B5 already proved that). It is NOT zero LISTING movers:
- orders 3/4 swap;
- `kind` becomes `list`;
- the `size-cap-retry` and `declined-nullable-default` descs are corrected.

So it is B7, a declared listing commit like C7. B6 alone (projection with
today's order kept in the `list` column, C6's shape) is byte-identical and
does NOT fix it: it moves the disagreement from code to data, where B7 deletes
it.

**Why T2 orders `nullable-exact` before `nullable-collapsed`.** They are
disjoint on CR, so their order is free in both derivations. This order is the
one that keeps B7's move to a single swap. The alternative order moves three
listed orders.

---

## 7. Siblings of the family (forest-for-the-trees lens)

| member | question it answers | hosted in B? | why |
|---|---|---|---|
| `fit_rungs[]` size-cap ladder | which smaller form after a size refusal | **yes** (T1 rows 5-10) | the host |
| [SEL-1] overflow rungs | what after a DFA overflow | **yes** (rows 3-4) | the survey's §3.1 charter |
| K60 nomem propagation | propagate, don't absorb | **yes** (row 1) | an arrival label; its ordering was a comment (K60), now a row order |
| [ART-SIZE] trial catch | a ladder K failed | **yes** (row 2) | the same recovery point; its "any reason" rule becomes `on` |
| prefilter admission (Q8) | does the VM get a prefilter | **yes** (T2) | ruled into B (D151 add. 2) |
| `--emit-ir` prefilter chain | why no prefilter (listing) | **yes** (T2's listing cells) | the second derivation of Q8 (survey §3.1's `emit_vm.c:9387-9484` row) |
| collapse build gate + PFLW | which language, and why | **yes** (T3) | its reason reads which rung fired |
| `UNROLL_K_WHY` | the size term's verdict | **yes** (T4) | the plan row lists the token; §4.7's precedence |
| `ENGINE_SEL` (`esel_of`) | how the engine came to be | **yes** (attribution walk) | the survey's "read which row fired" |
| `VM_PREFILTER_WHY`, drop notes, budget note | why the prefilter/contributor went | **yes** (cells; the budget note is a label attribute) | readers of "which row fired" |
| auto engine choice (`pcrec_select_engine`'s `default:` arm) | DFA or VM | **no** | the engine-selection family (D124); [SEL-COST] §4.3 plans `sel_auto_rows[]` as ITS table; B consumes `fit.chosen` |
| `forces_dfa_overflow` | the retry's input to selection | **no** | the selection channel [SEL-COST] reuses; B writes `dd` (row `sets`), selection reads it |
| `-fprefilter` / `--engine=dfa` do-or-die refusals (`select_engine.c:696-725`) | refuse a request | **no** | input validation BEFORE any decision; the sibling home is [OPT-SETS]' constraint table (`option_sets.md` §2.7, refuse/inert/derive) |
| `size_term_choose`'s argmin + capacity floor | which K | **no** (inside row 5/row 2's action) | an optimizer inside a row (memory `pcrec-decisions-as-first-match-tables`), flagged |
| `--tune` positions ORing deny bits at entry | the dial | **no** | the option-set family; noted because row 8's `applies` reads the bit `--tune=-2` sets |
| `build_anchored_dfa`'s `SDR` read | build the optional machine? | **no** (a reader kept) | it reads state a row writes; no decision of its own |
| the start table's RETRY rows | re-seed or step after a failed ATTEMPT | **no** | a different question (inside one compile's matcher, at run time); refactor A's |
| [DEC-POSDOM] | which positions are legal | **no** | A's sibling, its own later row |

The family has three remaining dispersed SIBLINGS: auto engine choice, request
refusals, and the dial ORs. Each already has a planned home table
([SEL-COST], [OPT-SETS]). No fourth unification is proposed.

---

## 8. Interaction with [SEL-COST] §4 and `--fast-or-fail`

### 8.1 [SEL-COST]'s post-build rows land IN T1

`sel_cost.md` §4.3 plans each post-build decline to be reported like an N1
over-budget, "`cx->dfa_disabled` plus a reason, then `compile_driver`'s
existing one-shot retry", with a new token `"cost-declined"` (§4.6). Under B:
- the DFA build reports a fifth arrival label, `cost` (the "reason field"
  `forces_dfa_overflow` was to grow);
- T1 gains row(s) `on = cost`, after rows 3-4;
- each row carries its own `deny` (`-fno-sel-<row>`), `degrading = false`
  (`sel_cost.md` §4.4: a row exists only because it is faster) and `fof`
  stated `false`;
- it sets `dd = SET` and `esel {off: cost-declined}`;
- the attribution walk needs no edit: the row's cell IS the token.

**Amendment owed to `sel_cost.md` when that row is built** (not edited here,
D80 for designs):
- its §4.6 sentence placing `cost-declined` "in `esel_of`'s ladder between
  `ESEL_SELECTED` and the overflow range" becomes "a T1 row's cell";
- its §4.3 claim that `COMPILE_MAX_ATTEMPTS` "does not move" is true of the
  attempts actually taken (a cost row and a [SEL-1] row are exclusive: both
  set `dd`, and rows 3-4 need `!dd` or a SEL1 collapse). It is false of §1.8's
  checked bound, which grows by the row's `retries` (25 → 26). That is a safe
  over-approximation; the bound is a loop limit plus one diagnostic number,
  never an artifact byte.

### 8.2 `--fast-or-fail`

Today it denies every DEGRADING row of the size-cap ladder (`limits.md` §8).
`cli.md:414` calls it "a size POLICY". It does not touch [SEL-1], whose two
rungs also cost run time. That scope is consistent with the spec but stated
nowhere as a scope.

B makes it a column: `fof` is true on rows 5-9 and false on rows 3-4.
`--fast-or-fail`'s reach is then visible in the table, and in `--list-axes`
if §11 Q4 lists T1.

**Recommendation: keep the scope.** A caller who wants a DFA overflow refused
already has the do-or-die levers: `--engine=dfa` refuses on overflow, and
`-fprefilter` makes the [SEL-1] rungs ineligible. Widening `fof` would give
the same behaviour a third spelling. If Frank wants it, it is two cells and a
mover row with `limits.md` §8's hunk (§11 Q2).

---

## 9. Standing questions (docs/design/CLAUDE.md)

### 9.1 The measurement regime: relevant only for what B does NOT change

**B reads no timing, and every count it cites is deterministic.**
- The counts are compile outputs over the corpus: decfb0's token and attempt
  tables, the reader census and the anchor census. They are the same on any
  box with the same `gcc` and `-D` set, because selection is a compile-time
  function of the pattern and the limits.
- Their regime is "shipped limits" or one of three NAMED lowered-limit
  reference builds. The lowered values (`MAX_VM_EMIT_CODE_BYTES=30000`,
  `MAX_EMIT_BYTES=60000`, `SIZE_TERM_THRESHOLD=10000`,
  `MAX_AUTO_DFA_ELEMS=3000`) were chosen by decfb0 to give the ladders a
  population, and not bisected. A different choice changes the floors, never
  a decision B makes.

**Two inputs B keeps, measured by others in a regime that could matter.**
- The `degrading` column's cost figures (`limits.md` §8, Mac directional).
  B neither reads nor changes them.
- §5.1's later fix has an unmeasured compile-time delta. decfb0 counted
  attempts and did not time them; the row's own STEP 0 owes the timing.

### 9.2 The independent control: relevant

**For each gate.**
- **Bytes**: against the parent built from `git archive`.
- **Attempt count/order**: against decfb0's probed copy of the BASE, which
  shares no code with T1 and is cross-recorded against B1's trace once (§4.2
  B1).
- **Token vocabularies**: the spec's hand-written §6.3 tables (the registry
  docs legs). The dump-vs-source legs RETIRE at B6 exactly when they would
  start sharing a source (§4.5).
- **The both-derivations oracle** shares predicates with its subject, and is
  stated as a filter test only.

**Who counts the population (K35).**
- `state_readers.sh` counts the members.
- decfb0's tables count each token and attempt shape per variant; they are
  pinned as floors and manifests, never re-derived from T1.
- `sabotage_anchors.py` counts the rows.

**[MECH-REACH].**
- Every re-aimed row keeps its `SAB_REACH`.
- The rows whose population exists only under lowered limits get their
  detector a lowered reference build inside `run_fallback_table.sh`. These
  are `overflowed-prefilter`, the [SEL-1] collapse, and the `fof` row.
  `capacity-declined` and the `cap-rescue` cells use
  `run_size_term.sh`'s existing ones.
- A row whose detector needs a lowered build and does not get one ships
  declared UNREACHED, with the reason.

### 9.3 What moves when data is regenerated: relevant, nothing for B1-B6

B has no data file, calibration or generated table. T1-T4 are code.
- **No emitted byte moves, so there is no abi event**: identity on streams
  1-2 is B's own gate.
- **B7 moves `--list-axes`**:
  - stream 5 only;
  - the registry pins re-pinned by measurement (D94 addendum's count-reader
    class: `run_registry_tests.sh`'s PASS counts, `axes_registry_check.sh`'s
    value sets);
  - spec hunks in the same commit (§4.6, D80).
- **decfb0's `results.md` is regenerated only on a base** (its probes cannot
  patch post-B3 code). It is pinned, not regenerated per commit.

---

## 10. Findings this design adds (not in the survey or decfb0)

- **F-B1 (PROBED).** `build/pcrec --features all -p rx --emit-ir --pattern
  'a${v}b'` lists `prefilter  no-engine-vm  --engine=vm -- the VM scans from
  search_from itself (R21 E-6)` under `auto`.
  - The chain's own header (`emit_vm.c:9436-9441`) promises never to name a
    route no flag explains.
  - The `(a)${v}` case lists the same.
  - It is §4.5's sibling (a listing reason keyed on an input, not on the
    decision).
  - Preserved in B; fixed with F1 (§5.2).
- **F-B2 (PROBED).** `engine-route`'s `declined-nullable-default` desc says
  "auto (or forced --engine=vm plus -fprefilter)". `--engine=vm -fprefilter`
  on `(a*)*` stamps `forced` and `VM_PREFILTER "hybrid"`, because
  `lang_nullable_declinable` excludes `force_on` and `would_prefilter`
  excludes `--engine=vm`. It is a stale desc (D-3's class) and is corrected at
  B7.
- **F-B3 (READ, population 0).** `esel_of` arm 7 tests `CR_SEL1 &&
  fit->prefilter`, not `prefilter_collapsed`. A [SEL-1] collapse retry that
  kept an UNcollapsed prefilter (no collapsible repeat, and a rebuild that did
  not overflow again) would stamp `collapsed-prefilter` beside
  `VM_PREFILTER_LANG_WHY "no counted repeat"`. decfb0 found no such compile
  in any variant. It closes structurally with §5.1(a).
- **F-B4 (READ).** The label set is not exclusive in the CODE: `dfa_overflowed`
  can be set without a `longjmp` by an optional machine (`ir/dfa.c:203-206`).
  The one optional machine restores the flag (`compile.c:360-370`), so no
  arrival carries both labels today. T1's walk (rows 3-4 before 5-9, `on` by
  label) reproduces today's precedence for the set anyway. Precedence is
  [SEL-1] first, falling through to the size rows when neither [SEL-1] row
  applies, as the code does today at `:1308`.
- **The §4.1 split (READ + decfb0's data).** The drift is the missing
  `pfc_rep` conjunct only. The gate's `!nullable` conjunct is [OPT-4.1]'s
  DESIGNED decline, and adding it to the rows is a token mover (§5.1).
  decfb0's "WASTED" counts are therefore an upper bound on fix (a).

---

## 11. Open questions for Frank (each with a recommendation)

1. **F1 and F-B1 as one later mover row.** File one row, [DEC-VAR-ATTRIB]:
   - delete T2's `var-nullable` row, so the 9 rows move to `selected`;
   - give `${…}` patterns their own listing token `no-variable`;
   - add §6.1's [PF-DROP] listing row (`no-size-cap`) in the same change: one
     listing-vocabulary event, one spec hunk.

   **Recommend YES**, as one row after B merges. The abi ruling is by grep at
   that row (§5.2).
2. **`--fast-or-fail`'s reach.** Keep it on the size-cap rows only, with the
   new `fof` column making the scope visible? **Recommend KEEP**:
   `--engine=dfa` and `-fprefilter` are the do-or-die levers for an overflow
   (§8.2).
3. **`nomem` and the size-term trial catch as T1 rows** (rows 1-2) rather than
   two tests ahead of the table. **Recommend ROWS.** The table is then total
   over every arrival, K60's "propagate before any catch" becomes row order
   instead of a comment, and both are already ordered first today. The
   alternative leaves two decisions outside the one ladder.
4. **B7's listing scope.**
   - (a) `engine-route` order + `kind` flips for `engine-route`/`size-term`/
     `prefilter-lang` + the two desc fixes: **recommend YES** (it is §4.6's
     fix).
   - (b) ALSO list T1 and T2 as two new `kind=list` axes (`fallback`,
     `prefilter-admit`), with rows, order, deny, `degrading`, `fof` and
     `on`: **recommend YES, in B7.** [LIST-TABLES] and D152 want every table
     listed, and the cost is stream-5 rows plus registry re-pins. The
     alternative is to file it under [LIST-TABLES].
5. **§4.1's fix scope.** The later row takes the `pfc_rep` conjunct ONLY
   (compile-time mover, F-B3 closed). It does NOT take the nullable conjunct
   decfb0 recommended, which moves `declined-nullable` tokens and undoes
   [OPT-4.1]'s designed outcome. **Recommend `pfc_rep` only**, its STEP 0
   being decfb0's census re-run with the fate split by PFLW, plus a compile
   timing.
6. **Row-pointer state vs value state.** Keep `collapse_reason`/
   `size_drop_rung` as VALUE state written by rows (§1.3), not pointers to
   rows? **Recommend VALUES**: fewer re-aims, and A's "read a payload, never
   an identity" rule.
7. **Admission-table placement of the `has_var` refusal.** The `-fprefilter`
   + `has_var` refusal (`select_engine.c:696`) stays a request refusal OUTSIDE
   T2 (§7), with its future home [OPT-SETS]' constraint table. **Recommend
   OUTSIDE.**
8. **Panel.** A light D6 panel (sound + checks critics) on this note before
   the build lane, A's shape (A's panel found the re-aim undercount and the
   trace's under-specification). **Recommend YES.** Frank's standing ruling
   lets the manager launch it, so this is FYI more than a question.

---

## 12. The lenses (brief)

- **Specific vs general**: one ladder for every arrival label, one admission
  table for both of today's derivations; F1 becomes a visible row instead of
  a ternary inside a predicate.
- **Core vs derived**: the tables read E1 facts (`kinds`, `nullable`,
  `empty_admits`) and the fit; they derive no fact.
- **Applicable vs assumption-changing**: applicable; no token, attempt or
  listing byte moves through B6.
- **Fits the architecture vs refactor**: fits; it extends the existing
  `fit_rungs[]` and reuses A's trace, sweep, anchor tooling and listing
  projection.
- **Shared question / engine hat (D124)**: T1 is engine-scoped by its
  `applies` (rows 7-8 DFA, 3-4/6/9 VM), not by separate tables.
- **Forest for the trees**: §7; three siblings remain, each with a planned
  home.
