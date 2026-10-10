# ROWCON audit: kit rows, field x row matrix, disagreements, visibility, reach

Tree: /Users/fdicostanzo/pcrec/worktrees/memfn (branch lane/memfn-g2x, 49888b63, contains K96 fix).
Read-only. Facts only. Cites are `file:line` under `memfn/src/` unless a path is given.
The prebuilt `build/pcrec` predates the K96 fix (no "miss is not its n" string in it);
all CLI witnesses below are pcrec-corpus shapes, where the fix is byte-neutral (m1bfix_report.md s4).
CLI compiles used: about 30 of 40 (`-o -`, stdout only).

Column keys: GATE = compose.c (`site_check`, `mf_define`), GEN = generic.c, OFS = ofsskip.c,
PRE = precheck.c, RUNA = runcmp.c `runcmp_arm`, RROWS = runcmp.c's own 4-row table.

---------------------------------------------------------------------------

## 1. THE ROWS

### 1.1 Selection table A: the composer's arms (compose.c)

- Table: `static const arm *const arms[]` compose.c:121-126. Order: `ofsskip_arm`, `precheck_arm`, `runcmp_arm`, `generic_arm`.
- Struct: `arm {id, miss_leaves, applies, define, use}` kit.h:96-102. No `deny`, no name/doc column, no explain column.
- Walk: `select_arm` compose.c:128-135. FIRST-MATCH. Predicate columns: `(!arm->miss_leaves || site->on_miss_leaves) && arm->applies(site, DEFINE hooks)`.
  Selection is made ONCE, at `mf_define` (compose.c:275), over the define-time hooks. `mf_use` re-dispatches through the stored `r->arm` (compose.c:304); it does not re-select.
- No deny consulted: the walk never reads `site->opts` or `art->denies` (the comment compose.c:112-120 says the arms carry no deny "because they are not byte-moving"; the first byte-moving row is to carry one, D144 item 4). `mf_opts_check` (options.c:52) is never called by `mf_define`.
- None applies: `return NULL` -> `kit_fail("mf_define: no arm applies (the generic row must)")` compose.c:276-277. Unreachable by construction: `generic_applies` returns 1 (generic.c:621-626).
  The generic row can still REFUSE at define/use for a missing hook (section 2, R cells).
- Gate before selection (`mf_define` compose.c:259-278): abi, `site_check` (vocabulary), `site.denies == art.denies`.

| # | row | file:line | form_id | applies() | needs on_miss_leaves | text it writes |
|---|---|---|---|---|---|---|
| A1 | `ofsskip_arm` | ofsskip.c:425-431, applies :387-394 (+ `ofs_fn_applies` :97-126) | "ofsskip" | FUNC, FIND, RETURN, empty MISS, end_back 0, !reverse, !guard_by_caller, pred.fn_ref!=0, def->fn_name, `miss_is_n(def)` (:382-385), `ofs_fn_applies` | no | file-scope `static inline size_t <fn>(subject,n,pos[,tables])` (memchr stream, or PAIR leapfrog when scanned run byte is a 2-member cube) + legend comment; use = its call |
| A2 | `precheck_arm` | precheck.c:242-249, applies :70-89 | "precheck" | STMT, ALL_PRESENT, ON_MISS or ASSIGN, empty MISS, end_back 0, !reverse, npred>0, preds, def; every pred is `run_part` (:63-68) or a `single_byte` with no fn_ref (:52-59, :82); a run after a set rest declines (:81); ret_pred NONE or a run_part (:88) | YES (kit.h comment; compose.c:131) | FUNC parts at file scope via `ofs_fn_define`; body: one-byte `memchr` gate, per-run call, set-rest `rq_set[]` loop |
| A3 | `runcmp_arm` (VMRUN) | runcmp.c:351-357, applies :322-328 | "runcmp" | EXPR, VERIFY, BOOL, guard_by_caller, nterm==1, `run_cmp_sat(term0)` | no | no file-scope part; an expression from `run_cmp_render` at `<s> + <lo>` |
| A4 | `generic_arm` | generic.c:684-690, applies :621-626 | "generic" | always 1 | no | byte loops; every form/handoff in the vocabulary |

K1 reference functions (`mf_ref_*`, k1_ref.c, memfn.h:421-445) are NOT selectable: not in `arms[]`, not reachable from `mf_define`; the header says pcrec never calls them and no artifact contains them. Excluded.

### 1.2 Selection table B: the run compare's rows (runcmp.c)

- Table: `static const rc_row rows[]` runcmp.c:78-103; accessor `mf_run_rows(i)` :106-109 (public, memfn.h:355-360).
- Walk: `rc_row_of(denies, run)` :163-170. FIRST-MATCH: skip a row if `row.deny & art->denies`, else take the first whose predicate holds (`rc_holds` :143-158).
- No row: `NULL` -> `kit_fail("runcmp: no run-compare row applies")` :250, :281. Unreachable while each domain keeps its undeniable fallback (`bytes` masked, `memcmp` exact; comment :74-77).
- Customers (three): `runcmp_arm` (A3), the RUN term of `ofs_fn_define`'s verify chain (so A1 and A2's FUNC parts), and `run_cmp_prepare` (helper declaration). So table B runs inside A1/A2/A3, never as a top-level arm.

| # | row | deny | predicate | text |
|---|---|---|---|---|
| B1 | `words` | MF_D_RUN_OVERLAP | masked (some mask byte != 0xFF) and len >= 2 | W-byte word loads ANDed with the mask literal, `&&` joined; `art->words++` (:217) |
| B2 | `overlap` | MF_D_RUN_OVERLAP | exact, len in {3, 5-7, 9-15} | two overlapping word loads (same `rc_emit_words`, :193-218) |
| B3 | `bytes` | none | masked | per-position `(b & K) == T` |
| B4 | `memcmp` | none | exact | `!memcmp(base, "<t>", L)` |

Row count: 8 selectable rows (A1-A4, B1-B4).

### 1.3 Form choices with NO table (hard-coded branches inside a row)

These pick text by `if`/`switch`, with no applies/deny/name, so they are invisible to any table-based mechanism:
1. ofsskip.c:250-251 vs :252-273: PAIR leapfrog vs single memchr stream (`b >= 0` from `ofs_fn_scan` :128-141).
2. ofsskip.c:183-195 `verify_chain`: per-term spelling (run compare / byte compare / table probe).
3. precheck.c:230-236: per predicate: run call (:198-216, ASSIGN form vs presence form by `i == ret_pred`), first-pred gate (:163-173), set rest (:177-194).
4. generic.c:635-656: FUNC / ADVANCE / EXPR / STMT-value / STMT-ON_CAND (6 body forms); generic.c:131-136 member hook vs kit range test.
Total untabled branches: 2 (ofs) + 3 (pre) + 7 (generic: EXPR, FUNC define+call, ASSIGN, ON_MISS, ON_CAND, ADVANCE, member-vs-range) = 12.

---------------------------------------------------------------------------

## 2. FIELD x ROW MATRIX

Legend: H honoured | D declined by applies() | R refused (kit_fail) | I ignored | N/A | g = refused by GATE before any row sees it.
`!` marks an I cell where the contract lets the field take a value that changes correct behaviour (K96-class suspect), numbered S1..S8 and explained in 2.5.
`i` marks an I cell that is benign today (a fact/hint, or no row exploits it) but is a hazard for a future row.
RROWS reads only `run`, `mask`, `run_len` of a RUN term and `art->denies`; every other field is N/A for RROWS and is omitted.

### 2.1 mf_site

| field | GATE | GEN | OFS | PRE | RUNA |
|---|---|---|---|---|---|
| abi | R :263 | - | - | - | - |
| form | R out-of-enum :181; stmt-vs-handoff :211-214 | H :635-656 | D FUNC :389 | D STMT :72 | D EXPR :325 |
| op | R vocab :208; SKIP shape :204-207 | H switch :245 | D FIND :389 | D ALL_PRESENT :72 | D VERIFY :325 |
| handoff | R vocab :208 | H :314-318, :639-652 | D RETURN :390 | D ON_MISS/ASSIGN :73 | D BOOL :326 |
| reverse | g ALL_PRESENT :200 | H FIND/SKIP :223-234, ON_CAND :493-502; I on VERIFY/ADVANCE (no direction) | D :391 | D :74 | I (VERIFY has no direction) |
| empty | R out-of-enum :182; NOP non-STMT :215; MISS on ADVANCE :217 | H MISS :256,:360,:456; NOP :357,:448; EXCLUDED = no test | D MISS only :390 | D MISS only :74 | I (guard_by_caller supersedes, same as GEN :256) |
| end_back | R >1 :185 | H :217,:257,:360,:454 | D 0 only :391 | D 0 only :74 | I (guard supersedes) |
| pred | R via `pred_kinds` :201 | H (FIND/SKIP/VERIFY) | H via ofs_fn_applies | I (ALL_PRESENT reads `preds`) | D nterm==1 + sat :327 |
| npred, preds | R preds NULL :191 | H :269 | N/A | D npred>0, preds :75 | N/A |
| ret_pred | R :194-199 | H :270,:275 | N/A | D NONE or run_part :88; H :203 | N/A |
| guard_by_caller | R unless EXPR VERIFY, offsets>=0 :219-225 | H :152,:256 | D :391 | I (GATE makes it 0 for STMT) | D must be 1 :326 |
| use | R out-of-enum :183 | i | i | i | i |
| on_miss_leaves | R :186-189 | I (order-independent text) | N/A (FUNC => 0) | D via `miss_leaves` column compose.c:131 | N/A |
| span_lo | - | i | i | i | i |
| span_hi | - | H ADVANCE only :529,:543; i elsewhere | i | i | i |
| cand_ppm_lo/hi | - | i | i | i | i |
| consumer | R out-of-enum :184 | i | i | i | i |
| policy | - (stored `art->policy` compose.c:239, never read) | i | i | i | i |
| denies | R `!= art->denies` :271 | I (generic compares inline; the undeniable fallback) | H via run_cmp_render (RROWS) | H via run_cmp_render (RROWS) | H via run_cmp_render |
| opts | - (`mf_opts_check` not called) | i | i | i | i |

### 2.2 mf_pred and mf_term

| field | GATE | GEN | OFS | PRE | RUNA |
|---|---|---|---|---|---|
| pred.nterm | R 0 or >MAX :156-157 | H | D 0/>MAX :99; `checked>0`, `runs<=1` :125 | D ==1 :54,:65 | D ==1 :327 |
| pred.need | R out-of-enum :158 | H (tests it as REQUIRED; permitted by s14.5) | H (same) | H (same) | H (same) |
| pred.plan_hint | - | i | D >= nterm (incl. NO_PRED) :100; H :115,:130 | D must be 0 for a run part :66 | i |
| pred.plan_pos | - | i | D >= run_len :118; H :119,:137 | via ofs_fn_applies; H :102 | i |
| pred.fn_ref | - | H FUNC name :568 (reads `s->pred.fn_ref`, also for ALL_PRESENT FUNC) | D must be !=0 :392 | D run part needs !=0 :65, single_byte needs ==0 :82 | i |
| term.kind | R unknown :170 | H | H | D SET-single or RUN :54,:65 | D RUN :327 |
| term.offset | R < -MAX_BACK :161; SKIP !=0 :206; guard needs >=0 :222-224 | H negatives :154-161 | D <0 :105 | D !=0 :54,:65 | H :348 (GATE keeps >=0) |
| term.need | R out-of-enum :162 | H (tests all) | H (tests all) | H (tests all) | H |
| term.set | - | H :101-124 (unless `member`) | H count/first :53-66; D empty :111 | H `only_byte` :44-49 | N/A |
| term.table_ref | - | i (uses `member`) | H; D if set>1 and (!table_ref or !def->table_name) :111 | i | N/A |
| term.run / mask / run_len | R len 0 :166, run NULL :167 | H :189-204 (unsat byte => `0`) | H via RROWS; D unsat `run_cmp_sat` :107 | same as OFS (run part) | H; D unsat :327 |
| term.ppm_lo/hi | - | i | i | i | i |

### 2.3 mf_hooks (define-time hooks decide selection; use-time hooks are re-read by `use`)

| hook | GEN | OFS | PRE | RUNA |
|---|---|---|---|---|
| s | R if NULL :339; H, parenthesised `(%s)` :305 | I at define; R at call :280; raw in arg list (safe) | R at use :224; **raw** in `%s + %s` :168,:188 -> S2 | R :341; **raw** `%s + %s` :345 -> S6 |
| n | R :339; H parenthesised | I at define; R at call :280 | R :224; **raw** in `%s <= %s`, `%s - %s` :167-171 -> S3 | I (not read; guard supersedes) |
| lo | R :339; H parenthesised | I at define; R at call :280 | R :224; **raw** :167-171,:188 -> S4 | R :341; **raw** :345 -> S7 |
| floor | H; "0" = none :79; FUNC: floor stated at USE but not DEFINE is silently dropped :602 vs :79 -> S8 | D any non-NULL (incl "0") :99; R at call :282-283 | D for run parts via ofs_fn_applies; R at call for run lines; I for byte-only preds (offset 0 >= lo >= floor, Q-G2-6: benign) | I (guard supersedes) |
| result | R ASSIGN/ON_CAND :372,:446 | N/A | R only on the ret_pred path :204 | N/A |
| result_decl | H; R with NOP :374,:449 | N/A | H :206 | N/A |
| miss | R if NULL: RETURN EXPR :646, ASSIGN :372, ON_CAND :446, FUNC call :609 | D unless NULL or text-equal to `n` :382-385,:392; R at use :420 | **I -> S1** (writes `n`, tests `>= n`, :209,:214) | N/A |
| on_miss | R ON_MISS :363; optional on ASSIGN :386; brace-wrapped :344-349 | N/A | R if NULL :224 (always); **unbraced** `if (...)\n ind on_miss` :171,:192,:209,:214 -> S5 | N/A |
| cursor, step, more, peek, count, count_start | H (ADVANCE; `cursor` unread, Q-G2-14) | N/A | N/A | N/A |
| on_cand, on_cand_reach | H :444,:466 | N/A | N/A | N/A |
| member | H :131 (else kit range test) | I (singleton => immediate byte; multi => table_name) | I | N/A |
| table_name | I | H :147; D if absent for set>1 :111 | I | N/A |
| fn_name | R FUNC without it :567 | D :392 | D run part :66; R at define :145 | N/A |
| note | I (never called) | H :410 | H :152,:229 | I |
| note_tag | I | I | H :99 | I |
| indent | H ("" if NULL) | I (file scope) | R if NULL :224 | I |
| comment_tier | I (no comments) | H legend :335 | H :98 | I |
| u | passthrough | passthrough | passthrough | passthrough |

### 2.4 mf_art_begin args and the sink

| item | where | status |
|---|---|---|
| prefix | compose.c:238 | H by GEN (names), RROWS (`<p>_w<W>` helpers runcmp.c:204,:308) |
| policy | compose.c:239 | stored, never read by any row (i; hazard: first SIMD row must gate on MF_P_PORTABLE_ONLY) |
| denies | compose.c:240, :271 | H by RROWS only (runcmp.c:166) |
| sink.puts / vprintf | R by `kit_sink_ok` (OFS, PRE, run_cmp_render) kit.h / compose.c:95-100; GEN needs `puts` only (`kit_flush` :88) | |
| sink.cmt_open / cmt_close | optional everywhere (guarded, ofsskip.c:335,:375; precheck.c:98,:127; runcmp.c:298,:303) | |
| sink.cstr | R in `run_cmp_render` for any non-`bytes` row runcmp.c:252 | |
| sink.legend_byte | optional, OFS legend ofsskip.c:352 | |
| sink.comment_byte | NEVER READ by the kit (grep: no use in memfn/src) | dead op |
| sink.stamp / stamp_int | R in `mf_stamps` compose.c:396 | |

### 2.5 The K96-class suspects (I cells that the contract lets vary)

Count: 8 cells.

- **S1 PRE x miss.** The ASSIGN text leaves `result = <ofs call>` (a miss is `n`) and tests `result >= n` (precheck.c:206-209). Generic writes the STATED `miss` and tests `result == (miss)` (generic.c:384-390). With `miss` != `n`, PRE leaves `n` in `result` when the site gives its `on_miss`. Exposure is limited to an `on_miss` that reads `result` (text opaque; on_miss_leaves says only that it transfers control). Same defect class as K96 (an arm assuming miss == n); applies() does not look at `miss` (precheck.c:70-89) and use does not refuse (precheck.c:218-240). memfn.h `miss`: "the value written when no cand exists".
- **S2/S3/S4 PRE x s, n, lo (hook text not parenthesised).** precheck.c:166-172 `if (%s <= %s || !memchr(%s + %s, %d, %s - %s))`, :186-191 (`%s + %s`, `%s - %s`), :209/:214 (`%s >= %s`). GEN parenthesises every hook (`(%s)`, generic.c:305,:356,:360); G2's hook style 2 is an UNPARENTHESISED TERNARY (memfng2_report s2.3: 326 sites) and the contract says only "side-effect-free C expressions" (memfn.h `mf_hooks` `s`/`n`/`lo` comment "side-effect-free C expressions (rule 1)"; integration.md s8.3 rule 1). G2 never reaches PRE (never sets on_miss_leaves, m1bfix_report s6), so this is untested. `n = "c ? a : b"` makes `n <= lo` parse as `c ? a : (b <= lo)`.
- **S5 PRE x on_miss text shape.** Emitted unbraced: `if (cond)\n<ind>    <on_miss>` (precheck.c:171,:192,:209,:214). GEN wraps it in `{ }` (generic.c:348). An `on_miss` of two statements ("x = 1; return 0;") renders correctly through GEN and wrongly through PRE (the second statement runs unconditionally). memfn.h calls it "pcrec's STATEMENT" (singular); whether a statement sequence is in contract is unruled.
- **S6/S7 RUNA x s, lo.** runcmp.c:345 `kb_printf(&base, "%s + %s", h->s, h->lo)` then `base + off`. Same precedence class as S2-S4. Reached by G2 about once (batch 22), so the ternary style is likely never exercised there.
- **S8 GEN x floor on a FUNC site, define vs use.** `has_floor` is read from the DEFINE hooks (generic.c:79) and fixes the parameter list (`PARAM_FL`); `func_call` passes `h->floor ? h->floor : "0"` from the USE hooks (generic.c:602). A floor stated at use but not at define is silently dropped; a floor stated at define but omitted at use is passed as "0" (no floor). OFS refuses the first case loudly (ofsskip.c:282-283). The define/use hook contract does not say the two must agree.

Not counted (benign today; hazards for new rows):
- `use`, `consumer`, `policy`, `opts`, `span_lo`, `span_hi`, ppm hints: read by no row. A future row that exploits DISCARD (integration.md s14.5: "A kit arm may exploit DISCARD") must gate on `use` or it is the next K96. Same for MF_P_PORTABLE_ONLY (a SIMD row) and `opts` (select_arm never reads it; the first byte-moving row's `--memfn=no-NAME` deny has no consumer path today).
- PRE x floor at use for byte-only preds: ignored, harmless under Q-G2-6 (floor <= lo, offset 0).
- `lo` near SIZE_MAX: OFS `pos + maxk < n` (ofsskip.c:216,:252) and `n - pos - k` wrap for lo > n by a huge margin; GEN `lo + 1 < n` (generic.c:257) wraps the same way. G2 clamps `lo` to `n` (g2_driver.c:435,:612). The contract's own empty-range formula (`lo + end_back >= n`) has the same wrap, so this is not row-specific. Not counted.
- GEN FUNC reads `s->pred.fn_ref` even for ALL_PRESENT FUNC (generic.c:568); memfn.h puts `fn_ref` on `mf_pred`. Contract placement for an ALL_PRESENT FUNC is unstated. Not counted.

---------------------------------------------------------------------------

## 3. DISAGREEMENTS between rows on the same field

| # | field | rows | what each does | contract |
|---|---|---|---|---|
| 1 | `miss` NULL | GEN vs OFS vs PRE | GEN refuses (RETURN EXPR generic.c:646, ASSIGN :372, ON_CAND :446, FUNC call :609). OFS treats NULL as `n` (ofsskip.c:384). PRE ASSIGN accepts NULL (never reads it). This is the G2-author report. | memfn.h: `miss` = "the value written when no cand exists"; integration.md s14.1 "in EXPR and FUNC forms the miss is a VALUE (`miss`)"; s15.1 table gives `miss` = `n` for the OFS site, so pcrec states it as `n`. Contract is silent on NULL. |
| 2 | `miss` != `n` | OFS vs PRE vs GEN | OFS declines/refuses (K96 fix). PRE ignores (S1). GEN honours. | as above. |
| 3 | `floor` = "0" | GEN vs OFS/PRE-run | GEN: "0" is no floor (generic.c:79). OFS/PRE: ANY non-NULL declines (ofsskip.c:99) and refuses at call (:282). | memfn.h: `floor` "0 when NULL", so "0" == NULL by contract. OFS/PRE over-decline (conservative; costs a row, not an answer). |
| 4 | `floor` define vs use (FUNC) | GEN vs OFS | GEN silent (S8); OFS refuses loudly. | silent. |
| 5 | `n` NULL | GEN vs RUNA vs OFS | GEN R (need_subject :339); RUNA accepts (needs only s, lo :341); OFS define accepts, call R (:280); PRE R. | silent on which hooks each form needs. |
| 6 | `indent` NULL | GEN vs PRE | GEN treats as "" (generic.c:356); PRE refuses (precheck.c:224). | silent. |
| 7 | `on_miss` NULL on ASSIGN | GEN vs PRE | GEN accepts (generic.c:386 `if (h->on_miss)`); PRE refuses always (:224). | memfn.h: "ON_MISS, ASSIGN, MISS-empty: pcrec's STATEMENT". |
| 8 | hook text precedence | GEN vs PRE/RUNA | GEN parenthesises; PRE/RUNA print raw in operator contexts (S2-S7). OFS prints raw only as call arguments (safe). | "side-effect-free C expressions". |
| 9 | `on_miss` statement shape | GEN vs PRE | brace-wrapped vs unbraced (S5). | "pcrec's STATEMENT". |
| 10 | one-position set membership | GEN vs OFS | GEN calls `member` (else its own range test); OFS compares an immediate byte (singleton) or probes `table_name` (multi). | integration.md s8.3 rule 6: "the kit's scalar loop arms call back for it, so a set has one scalar spelling in the artifact"; rule 7: tables stay pcrec's. OFS departs from rule 6 for singletons; allowed only because `set[32]` bits are the truth both agree with (s10.2). |
| 11 | `note` | GEN/RUNA vs OFS/PRE | GEN/RUNA never call it; OFS/PRE do. The same site renders pcrec's FACT comment or not depending on the row. | memfn.h s14.2: pcrec's FACT comment for part `part`. Text only. |
| 12 | `lo` > `n` | all | all handle: GEN loop guard; OFS `pos + maxk < n` (returns `n`); PRE gate `n <= lo` (:167) / run call returns `n`. Agree. | Q-G2-1: legal, EMPTY. |
| 13 | OPTIONAL need | all | all test OPTIONAL terms/preds. Agree. | s14.5 lets an arm test them. |

---------------------------------------------------------------------------

## 4. VISIBILITY TODAY

Question: which row rendered a site, and why did the others decline?

| channel | what it shows | which-row? | why-declined? |
|---|---|---|---|
| `mf_result.form_id` (compose.c:308) | arm id string, only when `mf_use`'s `res` is non-NULL | yes, but pcrec passes NULL at every call (src/gen/memfn_sites.c:278 `mf_use(..., NULL)`, :286 `mf_call`, :296 `mf_emit(..., NULL, NULL)`); `mf_call` has no `res` at all. The only reader is tests/memfn/arm_fixtures.c:290 (it re-renders a FUNC site's call once more through `mf_use` just to get the id, :283-288). G2 never reads it. | no |
| form_id policy | "opaque; consumers never parse it" (memfn.h:299); C4 class 7 bans pcrec comparing it (tests/memfn/arch_blind_check.py:146-149; sabotage S521) | | |
| rendered comments | OFS: legend "THE OFFSET-k CANDIDATE-START SKIP" (ofsskip.c:340). PRE: "THE NECESSARY-RUN SEARCH" (precheck.c:105,:114). RUNA: none per compare; helper comment "Word loads for the literal-run compares" (runcmp.c:299). GEN: writes no comment at all (generic.c header). All gated by `cmt_open(tier)`; pcrec uses NONESSENTIAL, so default artifacts carry none (checked: `build/pcrec` default output has no legend). | partial, and only for OFS/PRE when comments are on | no (declines are silent) |
| stamps | `RUN_WORDS` = count of B1+B2 compares (runcmp.c:216-217); `MEMFN_FORMS` constant "none" (compose.c:404); `MEMFN_LIBC` = names pcrec noted (compose.c:405). No per-arm field. docs/spec/match_api.md §6.3.10¶3, §6.3.10¶2. | no (RUN_WORDS separates words/overlap from bytes/memcmp, per artifact) | no |
| `--list-axes` | axis `run-overlap` rows 1-4 = B1-B4, read live from `mf_run_rows` (src/dump/axes_dump.c:656-666); axis `memfn-simd`; section `memfn` (options.def) is EMPTY (options.def born empty; only the header comment). A1-A4 appear nowhere. | B rows only | no |
| denies | only `MF_D_RUN_OVERLAP` (memfn.h:96; pcrec `-fno-run-overlap`, bit 43) and only B1/B2. No deny removes A1/A2/A3 (compose.c:112-120). `--memfn=no-NAME`: `mf_site.opts` is carried but `select_arm` never reads it; registry empty. pcrec's own `-fno-offset-skip`, `-fno-req-run`, `-fno-req-byte`, `-fno-run-prefilter` remove sites BEFORE the kit. | | |
| C5 arm pins | tests/memfn/arm_fixtures.c (17 fixtures), pins/arms.tsv (34 rows), run_arm_pins.sh: asserts each fixture renders through its PINNED arm and digests def/use text. ARMS_EXPECTED="ofsskip precheck runcmp" (run_arm_pins.sh:38; generic not listed); ARMS_ROW_FLOOR=34 (:37). Decline cells pinned to generic: `ofs-decline-miss`, `ofs-decline-floor`. | yes, for fixtures | indirectly: a decline fixture pins that a given input lands on generic; it does not say which field caused it |
| site census / C17 | tests/memfn/site_census.py: a traced build logs (kind, file, function) per `mf_define`/`mf_emit` call; per-compile door accounting; verdict: every `delegated` pcrec row rendered at least once. | no (counts calls per pcrec site, not arms) | no |
| site manifest | tests/memfn/site_manifest.tsv: 13 pcrec sites, pending/delegated. Delegated: PRE, OFS, SETREST, VERIFY, VMRUN. | no | no |
| PCREC_CAND_TRACE | `CANDTRACE slot route row site` stderr records (src/core/internal.h:6986-6997); compile-time knob, scratch builds only. The PRE builder emits pcrec's INPUT decisions (`req-site`, `req-gate`, `run-tests`, `req-handoff`, `set-rest`, src/gen/emit_dfa.c:1438-1446). No record exists in memfn_sites.c, memfn_stamps.c or the kit; none names a kit arm. | no | no |
| loud errors | `mf_art_error` text names the arm ("ofsskip: ...", "generic: ... needs the `miss` hook"); only for REFUSALS, not declines | on refusal | on refusal |

Net: today nothing outside the C5 fixtures can say which arm rendered a site, and nothing anywhere can say why an arm declined. A decline is a silent `return 0` in `applies()`.

---------------------------------------------------------------------------

## 5. REACHABILITY TODAY

### 5.1 From pcrec's corpus (CLI-confirmed witnesses; `-p rx -o -`)

| row | reachable from pcrec? | witness |
|---|---|---|
| A1 ofsskip, single stream | yes | `--pattern 'user:pass[0-9]'` (DFA; `rx_ofsskip` memchr at offset 4, `RX_REQ_HANDOFF "none"`); also `[a-c]x[0-9]q`, `userpass(a|b)+` |
| A1 ofsskip, PAIR leapfrog | not confirmed in the corpus within the cap | C5 `ofs-pair` only. The pair FORM is reached via A2 FUNC parts: `--engine=vm -i --pattern 'hello[0-9]'` and `(?i)userpass(a|b)+` emit `ha`/`hb` inside `rx_reqrun` |
| A2 precheck, run FUNC part, ON_MISS | yes | `--pattern '(?:foo|bar)+baz'`; `--engine=vm --pattern 'abcd[0-9]'` (`if (rx_reqrun(...) >= subject_length) return 0;`) |
| A2 precheck, gate + set rest | yes | `--features all --pattern '(x?)([a-z]+)+Z.@\1'` (`rq_set[] = { 64 }`) |
| A2 precheck, ASSIGN handoff | yes | `--pattern 'x{2,5}(?i:cat)'` (`RX_REQ_HANDOFF "5"`, `handoff_position = rx_reqrun(...)`), `(?:a|bb)?catdog`, `(?i)userpass[0-9]` |
| A2 precheck, masked whole run + rest | C5 only (`pre-masked-whole-rest`) | not confirmed in the corpus within the cap |
| A3 runcmp (VMRUN) | yes | `--engine=vm --pattern 'abcd[0-9]'` (`!memcmp(subject + scan_position, "abcd", 4)`) |
| A4 generic | NOT found | no pcrec site selected it in any compile above; identity gates (m1bfix_report s4: 156/156 artifacts byte-identical, 40 ofs, 94 pre, 101 run compares) imply pcrec's three delegated sites never reach it, since the generic text differs from pcrec's pre-migration text. This is an inference, not a measurement: nothing records the arm pcrec's sites select. |
| B1 words | yes | `--engine=vm -i --pattern 'abcd[0-9]'` (`rx_w4(...) & rx_w4("\337...")`, `RX_RUN_WORDS 1`); `x{2,5}(?i:cat)` |
| B2 overlap | yes | `--engine=vm --pattern 'abcdefg[0-9]'` (`rx_w4(subject+...)== ... && rx_w4(... + 3)`, `RX_RUN_WORDS 2`) |
| B3 bytes | yes (only under the deny) | `-fno-run-overlap --engine=vm -i --pattern 'abcd[0-9]'` (`((subject + cand)[0] & 223) == 65 && ...`) |
| B4 memcmp | yes | `--engine=vm --pattern 'abcd[0-9]'` (`!memcmp`, L 4) |

Note: B1-B4 are reached THROUGH A1/A2/A3, so the row-level witness is the run's shape, not a new arm.

### 5.2 From G2

- G2 is the only kit test that exercises GEN across the whole vocabulary. It never reads `form_id`, so nothing records which arm any G2 site used.
- From the reports (memfng2_report.md; m1bfix_report.md s1, s6; journal "late morning" entry):
  - A1: reached by exactly two sites before the K96 fix (both wrong); 0 sites after the fix.
  - A2: never reached. G2 never sets `on_miss_leaves`.
  - A3: about one site (batch 22, `memcmp` row).
  - B1 `words`: never reached. B2 `overlap`: not stated in the reports. B3 `bytes` / B4 `memcmp`: B4 by that one A3 site; B3 not stated.
  - A4 (generic): every other G2 site (4,011 rendered in the first full run, memfng2_report s2.1).
- Lane g2x (blinded, opus, worktree g2x) is extending G2 now; the next non-blinded step is a per-ARM reach census of G2's sites with literal floors (journal).
- Even once G2 reaches A1/A2 with the hook styles it uses, S2-S4 are only caught if the generator emits the ternary style on those sites.

### 5.3 What counts per-row reach today

- C5 (arm_fixtures.c / arms.tsv): existence, one fixture per shape: all 4 top arms (generic via the two decline fixtures) and all 4 B rows (run-overlap3/13 = B2, run-memcmp8 = B4, run-masked-words = B1, run-masked-deny = B3, run-exact-deny = B4). Count K35: ARMS_ROW_FLOOR 34, ARMS_EXPECTED 3 arms.
- `RUN_WORDS` stamp: per-artifact count of B1+B2 together.
- C17/site_census: calls per pcrec site, not arms.
- tests/memfn/run_handoff_reach.sh: three witness patterns for the VM hybrid handoff route (artifact-text markers); a per-route floor, not per-row.
- C12 (form_checks.py): counts search forms in pcrec's emitters, not kit rows.
- G2's census (memfng2_report s2.5): counts shapes (combos, term cells, lengths), not arms.
- Nothing counts per-arm reach over a corpus, and nothing counts per-arm reach in G2. For pcrec's own start rows the precedent is planned only: docs/design/start_table.md:1340 "C2 adds, under PCREC_CAND_TRACE, a per-row hit counter that row_census.tsv cross-checks ...; a row whose counter reads 0 ... UNPROVEN-BY-SWEEP"; tests/codegen/run_cand_rows.sh covers `dfa_pfs[]` structure.

---------------------------------------------------------------------------

## 6. FACTS a design needs

### 6.1 The row-selection idiom elsewhere in pcrec

- `DfaCand {name, deny, applies}` (src/gen/emit_dfa.c:3391-3395): every row of every candidate list begins with it. `name` = the stamp value; `deny` = a flag bit in `cx->opt->flags` that REMOVES the row; `applies(const DfaSel *)`.
- `dfa_select` (emit_dfa.c:5089-5099), written once for six axes: for each row in order, skip if `deny & flags`, skip if not `cand_routed` (a per-row `routes` mask), return the first whose `applies` holds. Macros `DFA_SELECT` (:5101) and `DFA_SELECT_ROUTED` (:5106).
- Total fallback: every list ends in a row whose applies is `cand_always` (:5113); a missing fallback crashes ("deliberately not defended against", comment :5071-5088), unlike the kit's `kit_fail`.
- Users: `dfa_pfs[]` (:6623, 6667, 6697, 7203), `req_admits` (:7039), `req_uses` (:7150), `dfa_matches` (:7460), `dfa_search_starts` (:7676), reprs (:5448).
- Rows are exposed: `AXIS_LIST(dfa_pfs)` (:7737) feeds `--list-axes`, so the deny bit, stamp name, and doc come from the same table (src/core/axes.def:214).
- Trace: `PCREC_CAND_TRACE_REC(slot, route, row, site)` (src/core/internal.h:6986-6997) prints the chosen row's NAME at the decision, `site` a string literal; designed to be diffed per pattern (docs/design/start_table.md C0/C1; C2 plans `CandRow`/`cand_select` and a hit counter).
- Kit-side precedent: runcmp.c's `rc_row {mf_run_row {name, deny, doc}, pred, form}` (:67-72) + `mf_run_rows()` accessor + `--list-axes` section: the same idiom, with name, deny bit and one-line doc, exposed. The composer's `arm` struct (kit.h:96-102) lacks name/deny/doc and has no accessor. `miss_leaves` is a lone predicate column.
- Style rule: memory `pcrec-decisions-as-first-match-tables` (ordered predicate-row table, first passing non-denied row executes).

### 6.2 Existing deny/explain machinery the kit could reuse

- `mf_option` registry (options.def / options.c:11-26; `mf_options()`, `mf_opts_check()`): the `--memfn=no-NAME` namespace and its refusal text are built; `mf_site.opts` already carries the string to `mf_define`; nothing consumes it (select_arm). Section `memfn` of `--list-axes` is born empty.
- `MF_D_*` denies (memfn.h:96) + `site.denies == art.denies` assert (compose.c:271) + pcrec's one map table (`pcrec_memfn_denies` / `pcrec_memfn_deny_flags`, src/gen/memfn_sites.h): the in-emitter deny channel.
- `mf_run_rows` + axes_dump.c:656-666: a kit table printed live by pcrec.
- `mf_result.form_id` (48 bytes) and `mf_art_error` text: existing, unused-by-pcrec outputs.
- `kit_fail` is sticky and first-error-wins (compose.c:72-81): a refusal channel; no non-fatal "note" channel exists.
- Stamps: `mf_stamps` writes three lines; `MEMFN_FORMS` is a constant placeholder for "the forms used" (Q55, R4f).
- Explain-shaped code elsewhere: `pcrec_syntax_explain` / `pcrec_probe_ask` (src/core/internal.h:6944-6965) answer syntax questions; nothing explains a selection. `src/dump/facts_dump.c` dumps facts, not decisions.
- Decisions constraint (journal, ROWCON entry): the explain/decision record is to be kit-owned, one record shape that pcrec's start-decision trace can migrate into at M5.

---------------------------------------------------------------------------

## Summary numbers

- Selectable rows: 8 (4 composer arms, 4 run-compare rows); 12 further untabled form branches (1.3).
- K96-class suspect cells: 8 (S1 PRE x miss; S2-S4 PRE x s, n, lo; S5 PRE x on_miss shape; S6-S7 RUNA x s, lo; S8 GEN x floor define/use). Three further families listed as benign hazards (2.5).
- Disagreement rows: 13.
