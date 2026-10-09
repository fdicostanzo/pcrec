# decfbB6 — [DEC-FALLBACK] refactor B, step B6: the listing reads the tables

Lane decfbB6 (sonnet), 2026-10-08, branch `lane/decfbB6` off main `84da351b`
(B5 merged there). Charter: `docs/design/dec_fallback.md` rev 2 §4.2 B6/B7,
§6.2, §4.6, the B7-owed list. Precedent: `stc67_report.md` (C6). B6 is a
no-mover step and NOT an abi event.

## Summary (a fresh agent resumes from here)

**Status.** B6 is built and committed; the heavy chain is ARMED, NOT RUNNING.

**What landed.**
- `FbList` (internal.h): one `--list-axes` cell — axis, order, name (which is
  also the stamp value), deny, force, lever spelling, desc. T1 `FitRung`
  (`axlist[3]`), T2 `PfAdmit`, T3 `PflwRow`, T4 `StWhy` (`axlist[1]` each)
  gain an `axlist` column; `FB_NO_LIST` says a row lists nothing.
- `pcrec_fb_list_row(axis, i)` (compile.c) returns the cell of order `i + 1`
  over T1/T3/T4 and, through `pcrec_pf_admits_list_row` (select_engine.c), T2
  and `esel_ends[]`. `axes_dump.c`'s `emit_fb_axis` projects it; the 17 hand
  `emit_pred_row` calls of `engine-route` (8), `size-term` (7) and
  `prefilter-lang` (2) are deleted. Descs, orders, names, deny/force bits and
  the `--engine=` lever text moved VERBATIM, D-3-like and F-B2 descs included
  (B7's to correct); the two comments that sat inside the `engine-route` block
  moved beside their rows. `kind` stays `predicate`.
- Trace-build self-check (`fit_tables_selfcheck`): each of the three axes is
  orders 1..n, every order carried by exactly one cell, no cell outside them.
- Re-aims S627 S640 S642 S644; family map (`call_graph_fallback.txt`,
  `sabotage_anchors.tsv`, `state_readers.txt`) regenerated; CLAUDE.md files
  (core, opt, dump, dec_fallback, lanes) and the design note's B6 outcome
  block updated.

**Validation done in-lane (light).**
| check | result |
|---|---|
| `--list-axes` vs a `84da351b` build, default | byte-identical (169 lines) |
| the same under `--features all`, `byte`, `utf8`, `recursion`, `backrefs` | byte-identical x5 |
| `make strict`: default, `-DPCREC_CAND_TRACE`, trace + `NEW_FIRST` | clean (the trace build caught a `-Wshadow` of mine, fixed) |
| `make test-registry` | rc 0, no `*** [...test-` line (`build/b6/reg.log`) |
| `tests/codegen/run_fallback_table.sh` | 135 passed / 0 failed (`build/b6/fbt.log`) |
| `scripts/emit_sweep.py --ref 84da351b --tree-rev HEAD --every 10 --jobs 8`, ALL streams incl. dumps | 0 movers, 0 asymmetric, self-check PASSED (`build/b6/sweep.log`); dumps 7/7 identical |
| `m6read_check_sab_anchors.py` | 555 rows / 573 sites, all resolve |
| `VALIDATE_ONLY=1` mech | 555 definitions valid |
| failing direction: T4's `size-model-declined` order 7 -> 6 on a `git archive` copy | listing differs, fbt 79/56 (every trace compile refuses on the self-check) |

Sweep scope note: `--every 10` (partial population; reach and DIFFER floors
not applied, identity, asserted zeros and the null arm are); the default
engine only, no `--variant` arms (the listing is static, and the `.c`
streams cannot move on a listing-only change).

**OWED, armed detached.** `build/land/waiter.sh` (nohup setsid) waits on
`worktrees/decfbB6/.lift`, then `build/land/chain.sh`: `make -j6`, `perfrun`
`make test`, `make strict`, `make testscripts`, mech VALIDATE_ONLY, and 24
mech rows solo-scored. Trailer `build/land/trailer.log` ends
`== CHAIN DONE`; logs beside it (`test.log` + `test.log.perfrun`,
`mech.log`). Read make test's verdict from
`grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/land/test.log` (empty =
green) with the perfrun note; mech rows from each `== mech run COMPLETE`.
Mech rows (24): re-aimed S627 S640 S642 S644; re-runs S102 S165 S272 S625
S238 S423 S628-S638 S646-S648. (Derivation below.)

## Findings

1. **Listed value with no table row: `forced` and `selected`.** The
   attribution walk's two ends produce no row. HANDLED: two cells in
   select_engine.c's `esel_ends[]`, beside `fit_attrib_walk`, reached by the
   same accessor. `forced` also carries the `--engine=vm / --engine=dfa`
   lever text, which has no row either.
2. **Table rows with no listed row.** All T1 rows except the three that
   carry cells (`forcing`, `nomem`, `size-term-trial`, `sel1-drop`,
   `drop-anchored`, `drop-premul`, `drop-prefilter`, `refuse`); T2's
   `backref`, `linked-call`, `nullable-exact`, `overflow-drop`, `forced-on`,
   `forced-off`, `var`, `default`; T3's `forced`, `exact`, `no-rep`. HANDLED:
   they carry `FB_NO_LIST` (a visible empty cell), because the listing names
   a VALUE and several rows produce the same one.
3. **Many rows to one listed value; a placement rule.** `declined-nullable-
   default` (T2 `var-nullable`, `nullable-exact`), `size-cap-retry` (T1
   `prefilter-collapse` plus the three drop rows), `overflowed-dfa`/
   `-prefilter` (the ROLE cell of `sel1-collapse`'s off half and `sel1-drop`),
   `count-collapsed` (T3 `rung`, `forced`), `exact` (T3 `nullable`, `exact`,
   `no-rep`). HANDLED by one mechanical rule: the cell sits on the FIRST
   row in table order whose cells produce the value. Consequences B7 should
   know: `overflowed-dfa`/`-prefilter` sit on `sel1-collapse` (not on
   `sel1-drop`, the pure-ROLE row), `exact` sits on `nullable`, though its
   desc ("always (fallback)") reads like `no-rep`. The listing orders are
   carried by the cell, so placement changes no byte.
4. **T3 has more tokens than the listing.** `prefilter-lang` lists the two
   `RX_VM_PREFILTER_LANG` values; the six `VM_PREFILTER_LANG_WHY` tokens are
   in no listing. Not touched (B7's scope question, with Q4(b)).
5. **Deny/force bits are cell fields, not derived.** `count-collapsed`'s
   `NO_PREFILTER_COLLAPSE` is also T1 `prefilter-collapse`'s `deny` cell;
   B6 keeps both spellings (verbatim, byte-identical). B7 could derive one
   from the other.
6. **`FbList` joins the call-graph family** (98 -> 99): T1's row type now
   names it. The parent under the same roots is 98, so B6 moved no other
   member. The listing accessors are outside the family (no decision reads
   them).
7. **`--step` calls S102 S165 S272 S625 RE-AIM by owner (`pf_admits`) while
   their anchors are single row-head lines B6 did not touch** (they resolve
   and their plants alter verdict/name cells only). Treated as re-runs.
8. **"Delete the hand-written arrays and accessors."** There were none: the
   three listings were straight-line `emit_pred_row` calls in
   `axes_dump.c`. Those 17 calls are the deleted text; nothing else read them
   (the readers grep below).
9. **Scope slip, reported.** Early on I redirected a probe's output and two
   scratch files to `/tmp` (`/tmp/null_unused`, `/tmp/x.tsv`, `/tmp/x.err`).
   Nothing was committed from them; I deleted all three and verified they are
   gone. Everything since is under `worktrees/decfbB6/build/`.

## Readers (grep before delivering)

Names deleted: only the 17 `emit_pred_row(...)` call sites inside
`axes_dump.c` (no named function, array or macro). Checked: sabotage anchors
(`m6read_check_sab_anchors.py` after the re-aims: all resolve; `grep` of
`tests/mech/sabotages` for `axes_dump`/`emit_pred_row`/the three axis names
finds only S627/S642/S644, re-aimed), `tests/registry` (`make test-registry`
green), `docs/spec` (`registry.md` §6 describes the listing, not its source:
no hunk owed, D80 — nothing caller-observable moved), the CLAUDE.md files
(updated).

## Re-aims and re-runs

- **Re-aimed (4), each text rebuilt from the current rows** (the rows grew an
  `axlist` initializer, so the row-swap plants' BEFORE/AFTER spans grew; the
  plants' intent, swapping two rows' evaluation order, is unchanged and the
  cells move with their rows): S627 (T1 sel1 rows), S640 (T2 forced-off/var),
  S642 (T3 rung/forced), S644 (T4 rescue/size-model). Anchors resolve;
  quoting of apostrophes in the long descs is `'\''`. Each is re-scored in
  the chain.
- **Derived** (`sabotage_anchors.py --step B6=84da351b..HEAD` against a
  parent call graph under the same roots): "10 definitions edited, 21
  reached; B6: 24 rows re-run": the four above, plus S102 S165 S272 S625
  (RE-AIM by owner, anchors untouched: re-runs, finding 7), plus S238 S423
  S628-S638 S646 S647 S648. All 24 are in the chain.
- **Plants that need to reach the listing:** none of the 24 plants a listing
  value; each is scored by its fbt/fallbacktable or its own suite (decision
  rows), and none plants a local B6 stopped reading (B4 finding 3's check:
  B6 rewrote no decision).
- No new sabotage id was taken (grep of main and `worktrees/*/tests/mech`
  not needed).

## Proposed plan-row text (do not apply; manager edits plan.md)

> `[DEC-FALLBACK] B6` — STATE:completed (pending heavy chain) 2026-10-08, lane
> decfbB6 (`lane/decfbB6`): the listing reads the tables. `axlist` columns on
> T1-T4 (`FbList` cells, today's order/name/desc verbatim), `pcrec_fb_list_row`
> / `emit_fb_axis`, `esel_ends[]` for `forced`/`selected`, trace self-check
> of the listed orders; `--list-axes` byte-identical under six `--features`
> sets, five-stream sweep 0 movers, fbt 135/0, registry green, re-aims
> S627 S640 S642 S644. Next: B7, the declared listing commit (the
> `declined-nullable`/`collapsed-prefilter` swap, `kind` -> `list`, the
> F-B2 and `size-cap-retry` descs, `tuning.md` §2.16/§2.17, `registry.md`
> §6, `listing_declared_B7.tsv`), with the placement of finding 3 to settle.
