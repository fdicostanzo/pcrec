# crit-memfn-sp1e — SLOT lens (slot tracing + ruling check)

Subject 9de5b5638 (lane/memfn-sp1e) vs base 20fb73159. Rulings read at b04160586.
No denied file was opened.

## FINDINGS

### SLOT-1 — the asker is told apart by `st == NULL`, not by the asker fact; PAIR and HORS are gated differently (SUSPECTED latent refusal)
- Severity: design / maintenance. Effort: S. Blast radius: finder.c `fd_find`, compose.c `select_arm`; no byte today.
- Where: finder.c :646-686 (`fd_find`), kit.h :531-548 (`fd_stop.renders_pair`), window.c :1844 (the one stop-stating caller), compose.c :313-321.
- What: there is ONE walk (`fd_decide` called once; R20 reads 2). But `fd_find` has two fact front-ends chosen by the pointer. With `st` NULL it runs the scope check, `find_facts` (which handles the RUN term), the UNSTATED-need refusal and the need mapping. With `st` set it runs `set_facts`, `seek_facts` and `hors_facts`, sets need REQUIRED, and sets SF_ASKER_PAIR from `renders_pair`. The only caller that states a stop always passes `renders_pair = 1`, and the other caller passes no stop. So SF_ASKER_PAIR is the same as `st != NULL`. The design calls the asker fact the walk's discriminator (§The tables T-FIND; named exceptions, "the asker fact"), but in the code the pointer is the discriminator.
- Consequence: PAIR is gated by the asker fact, so an asker that cannot render PAIR walks past it. D-hors (pick FF_HORS) is gated only by the window facts (SF_HORS_WINDOW | SF_HORS_DENSE). Compose's renderer rows name no HORS, and a pick with no renderer is REFUSED with no fall-back (compose.c :299-304, :315-321). Today only window.c states a stop, so D-hors never holds for the composer: x+y traces `row=D-hors verdict=PRED_FALSE` and its bytes are SAME. But the first stop-stating asker with `renders_pair = 0` (for example the composer stating its span 0 as an `fd_stop`, the obvious simplification) would get D-hors chosen and then refuse, where PAIR would have been skipped.
- Fix (S): gate HORS the way PAIR is gated (an asker fact for HORS, or the general form in SLOT-3). Then let the composer state an `fd_stop` from its one term, so `fd_find` has one front-end (the RUN term and the need mapping stay the composer's stated facts).

### SLOT-2 — the renderer row is not one declared row: three parallel arrays plus id branches
- Severity: maintenance. Effort: S. Blast radius: window.c E-find text only; no byte.
- Where: window.c :1799-1823 `wf_brows` (holds, libc, path, prepare); :2580-2583 `wf_b_find` (find); :2701-2711 `wf_b_text` (head, next, define); plus id branches outside the tables: :1872 `if (fx->bren == B_FN)` (prepare), :2727 `if (w->bren == B_FN)` (expr), :2735 `if (w->bren == B_PAIR)` (pair declaration), :2764 `if (w->bren == B_FN)` (define).
- What: 1e's stated content is "renderers keyed by (frame row, method row, renderer row)". The key is real: the frame is E-find, the method is T-FIND's pick (`b_*_holds` read the pick, as units_inventory N5 asks), and the renderer is `bren`. 1e also folded Table D's per-row text into the renderer row, which is good. But one row's actions are now spread over three arrays indexed by the same enum, held together by two `_Static_assert`s on size. B-fn and B-pair still render through branches on their ids. The branches pre-date 1e; the third array (`wf_b_find`, split out of the old `wf_b_text`) is 1e's.
- Fix (S): one row struct carrying {holds, libc, path, prepare, decl, head, find, next, define, expr-or-NULL}, with B-fn's function path as its `expr` and B-pair's declaration as its `decl`. That removes the four id branches.

### SLOT-3 — SIBLING OF A FAMILY: renderer selection keyed on the T-FIND pick now has three or more hand-written members (GENERAL FORM + UNLOCKS)
- Severity: design. Effort: M (a later unit, not a 1e fix). Blast radius: compose.c, window.c, ofsskip.c.
- The members:
  - compose.c `fd_renderers`/`fd_renderer` (new in 1e: pick + `end_back` -> arm, then `kit_ask` on `arms[]`).
  - window.c `wf_brows` (pick + plan -> B row; 1e added B-hors).
  - ofsskip.c `fn_rows` BODY/PREFIX (a named exception that reconciles with B-fn through `b_fn_holds`).
  - Near it: precheck's own memchr (N9).
  The decider census lists the first two under T-FRAME separately (decider_census.tsv :29 `fd_renderer`, `wf_find_decide`). That is the third member of a "pick -> text" family (the forest-for-trees lens: propose unification at three).
- General form: ONE renderer table keyed by (frame row: the composer's PF frame / E-find / OFS fn; the method's pick; the layer) -> text or arm. A frame has a renderer for a pick if and only if such a row exists.
- Unlocks:
  - (a) SF_ASKER_PAIR and the implicit HORS gate of SLOT-1 become one DERIVED fact: "this asker's frame has a renderer row for the row's pick". No new asker bit is needed per method (D176's growth rule: a new method adds a T-FIND row and its renderers, nothing in the asker). Trigger: the next FIND form only some frames render (W64/V1 at B6, a SIMD rung in E-find only).
  - (b) Unit 3.0's reply triple (frame row, method row, renderer row) becomes a lookup in one table, and the asker fact retires by construction. Trigger: unit 3.0.
  - (c) `fn_rows` BODY's named exception can retire into the same table when OFS states a kind. Trigger: the existing one ("pcrec states a kind on OFS sites").

### SLOT-4 — design and data docs still describe Table D; the design's own MF_CLASS_V lists omit 1e
- Severity: doc. Effort: XS. Blast radius: readers of the design docs.
- Where:
  - window_site.md §2.5 ("A `kit_table` on `kit_walk` (window.c `wf_dtable`)", :329-331).
  - window_site.md §2.6's E-find row ("Table D resumes it by D-hors or Table B decides its find", :359).
  - window_site.md :15 header line.
  - plan_cost.def :22-23 ("HORS_MIN ... is D-hors's (window.c Table D)"; it is read in finder.c `hors_facts` now).
  - span_pick.md Goal 2 cell (:18, "1a/1f MF_CLASS_V events") and §The designer/emitter split "What moves across" (:76-77, "1a and 1f ... MF_CLASS_V events"). 1e's conditional event has now happened and is recorded only in memfn.h, memfn/include/CLAUDE.md and finder_history.md.
  - trace_format.md `WPATH fd=` reads "the finder row whose pick decided its find", but D-hors's pick finds no stop: since 1e, `fd=D-hors` names the row that decided the skip.
- Fix: one revision line each. No stage-1 rule forbids editing window_site.md; only the roadmap is fenced.

### SLOT-5 — HORS_MIN is read through a second expansion of plan_cost.def
- Severity: maintenance. Effort: XS. Where: finder.c :625-631 (`FD_COST_##name` enum); window.c :76 (`COST()` over `WC_##name`).
- What: there is still one cost table, but now two private enum spellings of its reader in two files. A third reader would copy the X-macro again. Fix: one kit.h enum (or `kit_cost()` accessor) both files read. This also fits Goal 4's "every cost a priced row reads is a declared row".

### SLOT-6 — D-hors gained a REACH line but no floor, and no tracked owner for the floor (SUSPECTED)
- Severity: test-coverage. Effort: XS. Where: row_floors.tsv (`fd D-hors PLACEHOLDER PLACEHOLDER`), comment :80-83 "until the next N2 census and a G2 rows run measure it".
- What: this is not a regression. Before 1e, D-hors (`wfD`) printed no REACH line at all; now it is a counted `fd` row with both floors PLACEHOLDER (rows_check D accepts that and lists it UNREACHED). The trigger, "the next N2 census", is not tied to a plan row I could see from the diff. To confirm: grep plan.md after landing for a row owning the D-hors floor; if none, file one.

### SLOT-7 — (outside 1e; for 1d's owner) two window G2 plants have no anchor at base or subject
- Severity: test. Effort: XS. CONFIRMED by count.
- Where: memfn/tests/run_g2_win.sh :106 (S1405 `if (m->p[k].present && m->p[k].core && !count(m->p[k].set)) return 1;`) and :161 (S1410 `if (m->p[k].present && m->p[k].yes && !full(m->p[k].yset))`).
- What: after unescaping `\&` and `\n`, both anchors occur 0 times in window.c at BOTH base 20fb73159 and subject. The lines now read `if (m->p[k].present) plan_add(...)` / `if (m->p[k].present && m->p[k].yes) plan_add(...)` (window.c :926/:934). `git log -S` puts the change at 1d's acfb19c8f. The plant applier exits with "plant text found 0 times" (run_g2_win.sh :230-231). Every other run_g2_win.sh plant and every tests/mech sabotage on memfn/src matches its SAB_COUNT at the subject, including the re-aimed S1542 (finder.c) and S1079.

## PROBED-AND-HELD

**Slot-by-slot answer.**

**(1) T-FRAME = Table E at text time, legacy rows first, order kept.** HELD. `wf_erows` is unchanged: E_FUNC, E_STMT, E_FIND, E_GENERIC (window.c :1613-1626); `wf_prepare` walks it at define/use. Comments only.
- T-FIND (the quiet setup) runs before Table E's walk, because E-find's predicate reads it. Its answer is used only when the legacy rows decline.
- Per E-find define, T-FIND is walked twice: once quietly in setup (:1915) and once recorded (:1940). This is unchanged from base, where Tables D and B were each walked twice.

**(2) T-FIND as one first-match walk.** HELD.
- `fd_rows` order at subject, from a listing driver (one gcc line against each libpcrec.a): D-hors, D1, D1c, D1w, PAIR, R7w, P0, P2, P3, P4, P9. At base: D1 .. R7w, P0 .. P9.
- D-hors's holds are kept: `hors_facts` is `d_hors_holds` moved, with the same predicate, the same mass call on the same rate (`d->rate`) and set, and the same HORS_MIN.
- The deny `window-skip` travels with the row: `fd_opt`; `--list-axes` is byte-identical base vs subject.
- Admission reads the plan's stop set and the `hors_window` core. The shift (`hors_table`) reads the plan's tested `w->set`/`w->off`, as before.
- Resume: D-one `c + 1` (`d_one_next`) on B-pair/B-memchr/B-walk; D-shift on B-hors.
- The gate is the same for D-hors. The old wfD contract served every field. The new `ct_d_hors` serves the DEFINE-phase fields (core CORED as before); the hook fields it no longer lists are all MF_PH_USE/RUN (fields.def), and the fd walk gates at DEFINE only. Both walks pass denies 0 (`kit_walk(..., 0, ...)`).
- The window fields that are now stated in the fd walk's `gate_in` (alts .. wfloor) are served MF_ANY by every fd row.
- `fd_route` is gone. R20 by roadmap §5's own recipe, counted in the trees: base fd_route 1 + fd_find 1 + select_arm 1 + BODY 1, minus 1 = 3; subject 0+1+1+1-1 = 2. `select_arm` and BODY are the named exceptions.
- Stage-1 ratchet total at subject: R20 2 + R25 1 + R22 0 + R23 0 (R21/R24/R26/R27 0 as stated) = 3, inside "3 or 4".
- `fd_find`'s two callers: compose.c :313, window.c :1846. `fd_table` has one `kit_walk` (finder.c :532).
- Nothing in T-FIND is walked twice. D-hors is reachable only from E-find (by facts), and PAIR only from E-find (by the asker fact). See SLOT-1 for the asymmetry.

**(3) Renderer row.** HELD with SLOT-2.
- B-fn's reconciliation `b_fn_holds` is unchanged (window.c :1778-1789).
- B-hors was added. `wf_plan_brow` now names D-hors (trace only: compose.c :1138 under MF_TRACE).
- The runtime reach counter is keyed on the composer's `rid` only (compose.c :1119), so it is unchanged.
- The composer's switch became the declared `fd_renderers` table: same mapping, LIBC_BACK a wildcard on `end_back` as before.

**(4) U3/N4/N5/N11.** HELD as stated.
- U3 less OFS: the composer's arms and E-find's text are now renderers keyed on the pick; `fn_rows` BODY is a named exception; OFS sites never reach `fd_find` (`fd_scope`).
- N4: SF_WINDOW_STOP was renamed SF_ASKER_PAIR, bit 15 unchanged, and it is not on OFS.
- N5: B-fn is KEPT as the design says.
- N11: order kept.

**(5) MF_CLASS_V 7 -> 8.** WARRANTED. The listing driver shows `pres_row`'s index space moving: P0 6->7 .. P9 10->11, n 10->11.
- `pres_row`/`pres_led` writer: finder.c :798-799 (`d.terminal + 1`).
- Readers, by grep of the subject tree:
  - pcrec's `pcrec_memfn_pres_routed` (src/gen/memfn_sites.c :733-743) resolves the index through the runtime `mf_finder_rows` listing, so it moves with it.
  - arm_fixtures.c :383 and proof_check.c :408 compare against the macro.
  - compose.c :387/:1016 and window.c :2794 write the macro.
  - Every other hit is a history comment or design text. No docs/spec hit. No hit in pcrec-bench (`git grep` at 712f8c08; binary trend snapshots only).
- MF_SITE_ABI is 23 on both sides (driver).
- `git diff BASE SUBJECT -- src cli lib docs/spec` is empty, so the pcrec abi is unchanged.
- MF_FINDER_MAX 32 still holds 11 rows.

**(6) Rulings.**
- D186: a unit change with zero movers in every probe.
- D186 add. 2 purity: T-FIND reads only stated inputs (`st->rate` is the art's handed rates).
- D187: the stop crosses as a 256-bit set in `fd_stop.set`; no cube is carried beside it.
- R9: order kept.
- R11: the declared row map exists, with its readers: rows.tsv, row_floors.tsv, rows_check M, the trace names, `reach_equal --map`.
- R13: landed after 1d (base includes 1d).
- C7: R20 -1.

**Goals lens.** span_pick.md states ranked goals 1-5, and 1e serves them in order:
- G1 and G2: SAME everywhere probed; no abi change; MF_SITE_ABI unchanged.
- G3: Table D's walk is gone, R20 3->2, the decider census is green (`decider_census.py --root SUBJECT`: 67 passed, 0 failed, HITS 36, plants red).
- G3's residue: SLOT-1, SLOT-2, SLOT-5.

**Probes (all at rc 0 unless stated).**
- BYTE compare, BASE vs SUBJECT build/pcrec, the c-default form, stderr compared too: 6 patterns ([0-9a-f]{8}, (?i)cat, x[Q%]y, [a-z]{5}q, \d{4}-\d{2}-\d{2}, [A-Za-z0-9_]{6}@x) x 4 arms ("", -e utf8, --memfn=no-window-skip, -fmemfn-simd) = 24/24 SAME. Then --engine=vm 3/3 SAME, --analysis weblog 3/3 SAME, all-tie (-I tests/findings/adversarial --analysis=uniform, run from the subject root) 2/2 SAME.
- Control: subject hex8 default vs --memfn=no-window-skip differ (the `sh[` table is present / absent), so the deny is reached.
- MF_TRACE pairs:
  - hex8: wfD's SEL/ROW/END became fd's, plus a new `FDROUTE row=D-hors arm=E-find`; `WPATH fd=-` became `fd=D-hors`; a new `REACH fd D-hors chosen=1`.
  - x+y (composer): only `ROW fd D-hors PRED_FALSE` and its REACH line were added.
  - [a-zA-Z0-9]{8} x 4 arms: SAME bytes; D-hors chosen under the NONE regime (-e utf8, the 62-member set over HORS_MIN), the default and SIMD; vm takes R7w on both sides.
  - hex8 under the deny: base wfD D-one became the fd D-hors DENIED record, with the rest identical.
- reach_equal.py --map smoke (--no-corpus, 5 patterns, arms "" and -e utf8, --jobs 2): LIMITED rc=0, differ 0. Mapped wfD/D-hors -> fd/D-hors chosen BASE 1 HEAD 1. Dissolved D-one printed (3 / 4); its selections are checked implicitly through the fd rows' per-pattern equality.
- Anchors: every tests/mech sabotage with SAB_FILE under memfn/src matches its count at the subject; run_g2_win.sh plants all match except SLOT-7's two (stale at base too).
- Stale names: a grep of memfn, tests, src, scripts, docs/spec for SF_WINDOW_STOP|fd_route|wfD|wf_drows|d_hors_holds finds only history comments, the row map and its readers, run_sabotage_matrix.sh :513 (history), and the design docs of SLOT-4.

**Compile count: 102** pcrec compiles (a BASE/SUBJECT pair counted 2; the reach_equal smoke counted 20). Plus 2 gcc driver builds. No make, no box lock.
