# s3build report — [CLS-TREE] S3, the A_WCLASS node (2026-09-29, lane s3build, opus)

Branch `lane/s3build` from `aab32f9b` (main S1 + U2). A BYTE-IDENTICAL
refactor: no abi bump, no `docs/spec/` hunk, nothing caller-observable.
Inputs: `docs/dev/cls_s3_reader_inventory.md` (rulings D-1..D-8, §10),
`docs/design/cls_tree_design.md` §2.1/§6, `docs/dev/lanes/clsid_report.md`.

## 1. What landed, by commit group

| commit | content |
|---|---|
| c1 `f4c11164` | `A_WCLASS` (appended to `AKind`, so no enum value moves), `u.wcls`, `pcrec_wcls_set` (kind-checked), `pcrec_wcls_misplaced` (the one D-1 loud answer), `pcrec_ast_seethru` (the one see-through, inline in `internal.h`), the kind guard in `pcrec_cls_bits`/`_widen`/`_single`, `pcrec_cls_has` deleted, an arm in all 50 `AKind` switches, the five `default:` switches fully enumerated (D-6) |
| c2 `aeb98163` | the producer: `lower_class_utf8` returns `wclass_of(lc, a, res)` for every non-empty multi-unit class; the empty-set case stays a byte-confined `A_CLASS` |
| c3 `27b115c5` | `tests/codegen/run_wclass_census.sh` + `wclass_census.py` (in `make test-cpset-structure`), mech arm `wclass`, sabotage rows S365/S366, docs |
| `353f0cc2` | S-U8 and S303 re-anchored onto the lowering's new `return wclass_of(...)` |
| final | report, plan.md, gate numbers |

**Guards need a `Ctx *`.** `_widen` and `_single` had none, so a loud refusal
meant threading one: `pcrec_cls_bits_widen(cx, …)`, `pcrec_cls_single(cx, …)`,
`pcrec_lit_run(cx, …)`, `pcrec_revdet_first(cx, …)`, `rd_alt_disjoint(cx, …)`,
`first_of(cx, …)`, `rb_walk(cx, …)`/`pcrec_req_walk(cx, …)`,
`vm_isl_single(v, …)`, `Gk.cx` (set by `pcrec_uniq_scratch`, now also the
allocator `pcrec_possessify`/`pcrec_poss_survey` use), and
`tests/registry/definitions_oracle_gen.c`'s `textfn_byte`. S50 re-anchored for
`rd_alt_disjoint(R->cx, rev)`.

**D-4 as built.** `vm_emit` = `vm_charge` + `vm_emit_node` (the old switch);
`A_WCLASS`'s arm calls `vm_emit_node` on the child, so the wrapper's charge
stands in for the child's and the node count is unchanged. `vm_cost` and
`vm_count_slots` return/walk the child's (`under_atomic` passed through).

**D-3 as built.** `pcrec_ast_seethru` is applied at every P3 spine descent
that flattens or counts: `vm_cat_flatten`, `vm_alt_flatten`,
`vm_count_slots`' ALT spine, `vm_isl_words`' two flatteners, the island node
counter; `nfa.c`'s `ast_bare` now calls it (so the NFA sees exactly the old
tree). The `for(;;)`/`continue` walkers (`rb_walk`, `ew_walk`, `sa_walk`, the
four `mrl.c` widths) needed no see-through: a transparent `a = a->l; continue;`
arm continues the same accumulation the old tree did.

## 2. Findings

1. **The inventory's rows 5/6 are W, not U — the D-1 ruling on them would
   have broken the gate.** `vm_det_seq`/`vm_cap_offsets` serve the CURSOR rung
   on any quantifier body (`vm_cursor_fits`), not only revdet bodies. With
   them declining: `(é)+` (also by default engine), `é{3}`, `(?:é)+x`,
   `x(?:é)*y` all MOVE (vm); with them loud those patterns would REFUSE.
   Built as child-walkers; W2 is the witness. Recorded in the inventory §11.
2. **"u.cls reads as the empty class" (inventory §4) is false for a union** —
   every member is at offset 0, so `u.cls` on an `A_WCLASS` reads its set.
   The kind guard is what makes a set-reading mistake loud. Measured the
   other way: S365's plant (shared `A_CLASS` arm in `vm_emit_node`) with
   `cls_kind_guard` also deleted compiles `x[é]y` and answers nomatch on
   `x\xc3\xa9y` where the clean artifact answers (0,4) — a silent
   miscompile. With the guard: "internal error: pcrec_cls_bits was handed a
   wide class".
3. **At a spine HEAD the wrapper never reaches `vm_emit`** (the see-through
   hands the flattener the child), so `[é]x` does not exercise the forward
   arm at all; `x[é]y` (spine item) does. A witness choice worth knowing for
   S4.
4. **The seethru is load-bearing, measured**: removed from `vm_cat_flatten`
   only, `éabc --engine=vm` moves (the 5-byte `"\303\251abc"` run compare
   splits). `vm_isl_words`' arm declining moves `café|naïve|résumé` (vm).
5. **`pcrec_wcls_set` has no caller at S3** — every reader walks the child,
   by design. It ships as the one spelling S4's readers will use; flagged in
   case the manager prefers it deferred (it is the shape that got
   `pcrec_cls_has` deleted, except that it is kind-checked).
6. The first census draft would have shared the leaf label lists; the rule
   "no label run holds both `A_CLASS` and `A_WCLASS`" was kept strict, so L
   rows got the kind in a DESCENT group (walk the child) or a separate arm.

## 3. Validation

GATE_RESULTS

- `make strict CC=gcc-16`: clean (after c3 and after the re-anchors).
- `bash tests/codegen/run_wclass_census.sh`: 10/0 (and W1-W4 10/0 against
  the aab32f9b reference binary, so the witnesses are identity facts).
- `bash tests/codegen/run_cpset_structure.sh`: 28/0 (its [2c] window widened
  -A6 -> -A8 for the guard line; FAM/[2b] prose drop `pcrec_cls_has`).
- `scripts/m6read_check_sab_anchors.py`: 351 rows / 367 sites, all resolve.
- Sabotage rows, planted by hand into a copy of the tree (the `mech` runner's
  own solo run is OWED): S365 → `wclass` 2 fail ([5b], [W4]); S366 → 3 fail
  ([5a], [5c], [W3]). Re-anchored S303 → the compile refuses with the E1/E2
  nullability error (its facts detector); S-U8 → the `RX_PRUNE_CLAMP_SPAN(…,
  1, 2)` stride disappears (its encoding-checks detector).
- Targeted differential: 18 patterns × {default, --engine=vm} under
  `-e utf8 --features all` against the aab32f9b binary, same basename: all
  identical (`\p{L}+ --engine=vm` refused by both).

**OWED** (the manager's): full `make test`; `make mech` solo rows S365, S366,
S50, S-U8, S303 (`bash tests/mech/run_sabotage_matrix.sh S365` etc.). Mech
anchors S58/S-U4/S66/S121/S166/S302/S305 re-verified by the anchor script
(only S50/S58/S-U8/S303 moved; S58 was avoided by placing `pcrec_minw`'s arm
after its `A_CAP` arm).

## 4. Docs touched

`src/core/internal.h` (kind + member comments; the multiline note's
"five default: sites" now records they are enumerated), `src/core/CLAUDE.md`,
`src/opt/CLAUDE.md`, `tests/codegen/CLAUDE.md`,
`tests/mech/run_sabotage_matrix.sh` vocabulary, `Makefile` (test-cpset-structure),
`docs/design/patfacts/design.md` §3 and `src/facts/kinds.c` (the fifth kind in
the invariance proof), `docs/dev/cls_s3_reader_inventory.md` §11, plan.md.
