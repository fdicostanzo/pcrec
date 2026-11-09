# [S30A-PLAN] body: the PLAN dispositions of code review 2026-11-09 r1 s30a (kit unit 3.0a, R-35)

Filed 2026-11-09 by the manager from docs/dev/reviews/2026-11-09-r1-s30a.md (ruled). Each item waits on its trigger; none is scheduled. All are kit-side (memfn/), built by the kit when the trigger fires.

| item | what | trigger |
|---|---|---|
| F3 unification | the gate (`wf_renders`, ctx `mf_site *`) and E-find's composition (`wf_find_decide`, ctx `wf_bx *`) look the search table up separately with different predicate context types; unify to one context type per table (§2.4 "ONE function"). A FIX-NOW guard (E-find search rows carry no predicate) holds it meanwhile. | the first E-find search row with a predicate |
| F7 | the FUNC-form floor's loop is open-coded in `wf_floor_define` beside the skeleton table, which holds one spelling | the first MASK loop-state slot (both floor shapes would need it; plan_frame Goal 4) |
| F10 | under (R), §R's refusal invariant names Table S on only 6 of 19 refused witnesses; 13 refuse through pcrec's ask path with no kit reason: pcrec surfaces the kit's why on the ask path, or §R reads the traced REFUSE record | the next change to the ask path's diagnostics, or [IFACE-PUSH] |
| F17 | `b_fn_holds` calls `translate` inside a predicate (side effect in a predicate, pre-existing, now behind the shared `ren_find`) | 3.0b, when fused rows grow |
| memfnrows mech arm | a `memfnrows` arm (run_rows.sh, ~3 s) so the §R/§S row checks become sabotage-matrix rows (today (M)'s only detector, rows_check §S, has no mech arm) | the next §R/§S row added |
