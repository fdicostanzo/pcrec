# decfbB7 — [DEC-FALLBACK] refactor B, step B7: the declared listing commit

Lane decfbB7 (sonnet), 2026-10-09, branch `lane/decfbB7` off main `f27ff639`.
Charter: `docs/design/dec_fallback.md` rev 2 §4.2 B7 and "B7's deliverables",
§6.2, §4.5-§4.7, §10 (F-B2), §11 Q4(b) (ruled YES); carry-ins from
`decfbB6_report.md`; precedent `stc67_report.md` (C7). B7 moves `--list-axes`
only and is NOT an abi event.

## Summary (a fresh agent resumes from here)

**Status.** Built, committed, light gates green. The heavy chain is ARMED,
NOT RUNNING (waits for `worktrees/decfbB7/.lift`). Never merged.

**What landed.**
- `engine-route` lists in the attribution order: `declined-nullable` is order
  3 and `collapsed-prefilter` order 4 (two cell numbers: T2's
  `nullable-collapsed` cell and T1's `sel1-collapse` cell). §6.2's other six
  orders are unchanged.
- `kind` is `list` on `engine-route`, `size-term`, `prefilter-lang`
  (`emit_kind_row`; `emit_pred_row` is a wrapper that keeps `predicate`).
- F-B2: `declined-nullable-default`'s desc loses "(or forced --engine=vm plus
  -fprefilter)" and says an explicit `--engine=vm` reads `forced`.
  D-3-like: `size-cap-retry`'s desc now names every producer
  (T1 `prefilter-collapse` AND the three `drop-*` rows, which stamp it).
- Q4(b): T1 listed whole as `fallback` (11 rows: order = table order, name,
  `deny`, a desc GENERATED from the row's cells: action, arrival labels,
  degrading, `--fast-or-fail` reach, attempts added, repeat, stderr note) and
  T2 as `prefilter-admit` (10 rows: verdict, the `--emit-ir` prefilter token
  and its prose). `pcrec_fit_table_row` (compile.c),
  `pcrec_pf_admit_table_row` (select_engine.c), `FbTabRow` (internal.h),
  `emit_fb_table_axis` (axes_dump.c). No stamp macro (the tokens they feed are
  the three per-value axes').
- 136 rows / 46 axes -> 157 / 48.
- Spec: `registry.md` §6 (count, axis list, `kind` column, `applies`
  provenance), `tuning.md` §2.16 and §2.17 precedence sentences.
- Pins: `tests/registry/run_registry_tests.sh` axes PASS count 210 -> 216
  (the two T1 rows with a deny bit, 3 checks each, MEASURED), plus a new
  check: `engine-route`'s literal listed order and `kind=list` on the five
  fallback axes.
- S627 re-aimed (its span contains the `collapsed-prefilter` cell, order
  3 -> 4; intent, swapping the two [SEL-1] rows, unchanged).

## The control: `listing_declared_B7.tsv` + `listing_diff.py`

`docs/design/dec_fallback/listing_declared_B7.tsv` declares 21 changed cells
(17 `kind` via `*`, 2 `order`, 2 `applies`) and 21 ADDED rows.
`docs/design/dec_fallback/listing_diff.py` is C7's instrument extended for what
B7 has and C7 had not: rows keyed by (axis, candidate) so a swap is two `order`
cells; added rows declared with `+`. It fails on an undeclared change, a
declared non-move, a removed or undeclared added row, a header/section change,
an axis reordering, and an axis whose `order` column is not 1..n in file order.
Old values are read off the parent listing; new values are written in the
manifest, not read off the listing under test.

    python3 -I docs/design/dec_fallback/listing_diff.py PARENT NEW MANIFEST
    rows 136/157; declared cells 21, changed as declared 21; declared added rows 21, as declared 21
    listing diff: EXACTLY AS DECLARED

Run against a `f27ff639` build (`git archive`, `build/b7/ref`), default and
`--features all`: both EXACTLY AS DECLARED. Failing direction, three runs:
(1) one `order` declaration deleted -> `UNDECLARED engine-route/declined-nullable
order: '4' -> '3'`; (2) a `kind` cell reverted in the new listing -> `DECLARED
NOT AS STATED`; (3) the last added row removed -> `DECLARED ADDED row
fallback/refuse is absent`; all FAIL.

**Honest limit of the added rows' `applies`.** It is GENERATED text. The
manifest pins each row's leading phrase (the action / verdict and token), not
the whole sentence; the rest (labels, flags, counts) is generated from the
same cells the walk reads, so a hand declaration of it would restate its
source (learnings §3). Everything else about an added row (axis, order, name,
kind, empty stamp, deny macro and bit, cli flag) is declared exactly.

## Zero artifact movers

Named gates, all at HEAD `c4481e90` vs `f27ff639` (both built from `git
archive`):
- `scripts/emit_sweep.py --ref f27ff639 --tree-rev HEAD --every 10 --jobs 8
  --streams c-default,c-vm,emit-ir,composition,facts,emit-ir-auto,stderr`
  (`build/b7/sweep.log`): every stream movers=0 asymmetric=0, SELF-CHECK
  PASSED at full reach (population 5431 argv + 373 composition files; four
  `emit-ir-auto` arms, `stderr`, `facts`). `--every 10`, default engine, no
  `--variant` arms: a partial population, the same scope B6 stated.
- The `dumps` stream was run by hand, the sweep's own rule (whole-file byte
  comparison): `--list-syntax --list-definitions --list-verbs --list-families
  --list-limits --list-schema` identical; `--list-axes` differs and is the
  declared diff above. (The sweep's own `dumps` stream would report that one
  mover, which is B7's whole point; it was excluded and replaced by this.)
- `tests/codegen/run_fallback_table.sh`: 135 passed / 0 failed
  (`build/b7/fbt.log`); it builds the trace builds, which compile my
  compile.c/select_engine.c edits.
- `make strict`: clean (`-Werror -Wshadow`).

## Carry-ins from decfbB6, each dispositioned

1. **`forced`/`selected` have no table row.** KEPT, by design. They are the
   attribution walk's two ENDS (before any row, after the last), not a row's
   product; their cells stay in `esel_ends[]`. Listing them on the `fallback`
   axis would invent rows. Nothing deferred.
2. **Multi-producer values sit on the first producing row.** KEPT. §6.2 states
   exactly this rule ("listing each value at its FIRST producing cell in table
   order"), and with the swap it yields the declared order. The cell's row is
   invisible in the listing (the cell carries the order); nothing to move.
   The `exact` desc "always (fallback)" on T3's `nullable` row is a wording
   point only: DEFERRED to [LIST-TABLES], which would list T3's rows whole.
3. **T3's six `LANG_WHY` tokens appear in no listing.** DEFERRED to
   [LIST-TABLES] (with T3 as a whole-table axis). Reason: Q4(b)'s ruling is
   T1 and T2 only; the six tokens are a `format` set (`size cap retry, exact
   N > cap`), not names, and listing them wants its own ruling on how a
   parameterised value is spelled in `stamp_value`.
4. **D-3-like, F-B2, §4.6 order**: FIXED (above).
5. **`count-collapsed`'s `NO_PREFILTER_COLLAPSE` is both a T3 cell field and
   T1 `prefilter-collapse`'s `deny`** (B6 finding 5). DEFERRED: deriving one
   from the other is a cleanup with no measured need (D77), and after B7 the
   bit is listed on three rows of two axes (`sel1-collapse`,
   `prefilter-collapse`, `count-collapsed`), all read by the registry check.

## Sabotage rows

`sabotage_anchors.py ../.. call_graph_fallback.txt refactor_edit_set.tsv
--final after-B6 --edit-names --step B7=f27ff639..HEAD` (`build/b7/step.out`):
"5 definitions edited, 9 reached; STEP B7: 22 rows re-run (hunk 22)":
S102 S165 S238 S272 S423 S625 S627 S628-S638 S640 S646 S647 S648. Re-aimed: S627
only (`m6read_check_sab_anchors.py` found it stale; after the edit "all
anchors resolve", 562 rows / 580 sites). None of the 22 plants a listing value
(each is scored by fbt or its own suite). The 22 are in the chain. The
unresolved-source count in that script's stderr (37) is the pre-existing one.
No new sabotage id.

## OWED (armed detached)

`build/land/waiter.sh` (nohup setsid) waits on `worktrees/decfbB7/.lift`, then
`build/land/chain.sh`: `make -j6`, `perfrun` `make test`, `make strict`,
`make testscripts`, mech `VALIDATE_ONLY=1`, the 22 mech rows solo-scored.
Trailer `build/land/trailer.log` ends `== CHAIN DONE`. Read make test's
verdict from `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/land/test.log`
(empty = green) with `test.log.perfrun`; mech rows from each
`== mech run COMPLETE`. Light, done in-lane: `make test-registry` rc 0
(`build/b7/reg2.log`, 216 PASS, the new order check printed).

## Bench inbox note (TEXT for the manager to commit; I did not write to pcrec-bench)

> [inbox] pcrec `--list-axes` change, [DEC-FALLBACK] B7 (declared listing
> commit, lane decfbB7). Parsers keyed on axis NAME need nothing; parsers keyed
> on (axis, order) or on `kind` need a look. (1) `engine-route` orders 3 and 4
> swap: `declined-nullable` is now order 3, `collapsed-prefilter` order 4 (the
> attribution walk's order; the other six keep their orders). (2) `kind` is
> `list` (was `predicate`) on `engine-route`, `size-term` and `prefilter-lang`.
> (3) Two descs changed (`declined-nullable-default`, `size-cap-retry`). (4)
> TWO NEW AXES, `kind=list`, empty `stamp_macro`/`stamp_value`: `fallback` (11
> rows; the size-cap and [SEL-1] ladder, one row per ladder row in the order
> the compiler walks them; `deny_macro` PCREC_NO_PREFILTER_COLLAPSE on
> `sel1-collapse` and `prefilter-collapse`) and `prefilter-admit` (10 rows; the
> prefilter admission rows in walk order). Their `applies` text is generated
> from the table row, not hand prose. Main table: 136 rows / 46 axes -> 157 /
> 48. No generated artifact, `--emit-ir` or `--emit-facts` byte moved. Spec:
> `docs/spec/registry.md` §6. Rows of the two new axes are descriptive, not
> stamps: do not bucket on them.

## Proposed plan-row text (do not apply; manager edits plan.md)

> `[DEC-FALLBACK] B7` — STATE:completed (pending heavy chain) 2026-10-09, lane
> decfbB7 (`lane/decfbB7`): the declared listing commit. `engine-route`
> declined-nullable/collapsed-prefilter swap, `kind` -> `list` on three axes,
> F-B2 and `size-cap-retry` descs, T1/T2 listed as `fallback`/`prefilter-admit`
> (Q4(b)); 136/46 -> 157/48; `listing_diff.py` EXACTLY AS DECLARED (21 cells, 21
> rows); sweep 0 movers, fbt 135/0, registry pin 210 -> 216, S627 re-aimed.
> Deferred to [LIST-TABLES]: T3's six `LANG_WHY` tokens.
