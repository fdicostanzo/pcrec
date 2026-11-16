# checks — memfn-mcfix

## Findings


### CHECKS-A1 (CONFIRMED, maintenance, trivial effort, blast: one assert) memfn/src/window.c wf_wsearch _Static_assert is tautological
`wf_wsearch[FF_MFIND + 1]` and `_Static_assert(sizeof wf_wsearch/sizeof wf_wsearch[0] == FF_MFIND + 1)` both key to FF_MFIND: always true. Plant: copy kit.h with `FF_ZZZ` appended after FF_MFIND, `gcc -std=gnu11 -fsyntax-only window.c` -> rc 0, no diagnostic (checks/sa/). wsearch_of(FF_ZZZ) silently answers NONE via the bounds test: the exact failure the comment says it prevents. SILENT-MOVE. Only a sentinel (FF__COUNT) or last-member-independent bound can fail it. finder.c's ff_name assert (line 72) has the same shape (pre-existing; ff_name is initializer-sized so it does catch a missing name BEFORE FF_MFIND, but planted finder.c with FF_ZZZ also compiled rc 0).

### CHECKS-A2 (CONFIRMED, maintenance, trivial) rows_check `instrument:<unit>` accepts any non-empty unit
Plant (copy of tests/memfn under checks/rc, run via rows_check.py --root copy): `instrument:bogus-unit` on fn/mfind-w32 -> GREEN (264 passed, 0 failed). Unit is read by nothing (no link to LEVER_ARMS/the `mfind` lever); SAME for an invented unit. Other plants LOUD: deleted row (kit has row..., row_floors names...), invented row (3 FAIL), empty `instrument:`, misspelt tag, duplicate row, pcrec row relabelled instrument (needs fixture witness), all red. Also nothing checks an instrument row is truly UNPICKED (no pcrec-pattern witness reaching it): same gap as pending-site.

### CHECKS-A3 (CONFIRMED, measurement-weak, trivial) run_g2_mfind.py floor scaling is 0 at --sites<=40
scale=max(0,(sites-40)/40): at --sites 40 every population floor incl. 'sites' is 0 (vacuous); head-derived pops (a00..afe, k0, d0) are constant across sites yet scale down below 80 (lax, safe). At the defaults 80/160 min(scale,1)=1: unchanged, so no regression; floors at 160 are still the 80-site floors (pre-existing).

### CHECKS-A4 (CONFIRMED, hidden-by-generator note) g2_mfind_gen holds constant: use=POSITION, ret_pred, span_hi UNBOUNDED, cand_ppm_hi/ppm_hi FULL, body ONESHOT, form FUNC (STMT only for SH_PRE), op FIND (ALL_PRESENT for PRE), handoff RETURN, empty MISS, need REQUIRED, span_class BOUNDED, hk.miss MF_MISS_N, hooks names subject/n/pos, indent "", policy only INLOOP/SIZE. Any mfind_applies/reach branch keyed on another use/body/handoff/empty/span/policy value is untested by G2 (answers) and only visible to the simdguarded lever witnesses (2 patterns).

## PROBED-AND-HELD
- S3198: SAB_BEFORE `    return ofs_fn_fits(x, d);` occurs exactly 1x in memfn/src/vrun.c (line 683) = SAB_COUNT 1. Lever witnesses (harness --harness=mfind, run on review-tree build): 'a.*\x7f[acegikmoqsuwy]{12}' at x86-64 and x86-64-v3 -> MEMFN_FORMS "none", SWAR body present (memcpy(&w, subject x2) => 'lever-capped' counted; 'foo.*bar' renders mfind@w16 / mfind@w32+w16. Plain pcrec (no lever) has 0 memcpy(&w, subject => the new CHECKS-3 gate cannot count a non-lever artifact. Under the sabotage (not built; make forbidden) the long witnesses would render helpers: stamp over bound sum (2335/4089 vs 1400+700 at x86-64) and lever-capped 0<4 floor: LOUD by reading; unbuilt.
- selector check (g2_mfind_gen.c): strings match emitted selector shape (`return NAME__w32(` in last fn of site); w16 helper falls through to body, w32 to w16, so a skipped rung cannot satisfy the top-rung string. Not run (needs kit build).
- scripts/m6read_check_sab_anchors.py from review tree: "sabotages checked: 1301 (1355 anchor sites) / all anchors resolve"; tree stayed clean.
- rows_check plants: 7 (delete, invent, duplicate, empty, misspelt, relabel, bogus unit): 6 red, 1 green (A2).
