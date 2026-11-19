# VERIFY

## Findings

### READ-1 — HOLDS
- Ran: `gcc -g -fsanitize=address,undefined -I$T/memfn/include -I$T/memfn/src verify/longrun.c $T/memfn/src/*.c -o verify/longrun` (T=R/combined/tree; compile exit 0), then `./longrun L` for L=32,33,100.
- L=32: ask rc 0, define rc 0 (only LSan leak report: driver does not free; ASAN_OPTIONS=detect_leaks=0 clean). L=33: UBSan `window.c:1592:20 index 32 out of bounds for type 'uint16_t [32]'` and `:1593 ... 'uint32_t [32]'`; define rc -1 "rank_n > MF_RANK_MAX". L=100: same UBSan then ASan `heap-buffer-overflow WRITE of size 4 in run_rank window.c:1593`.
- Write lines (combined window.c:1592-1593): `p->rank_pos[k] = (uint16_t)r.scan;` / `p->rank_ppm[k] = kit_mass(...)`, loop `for (unsigned k = 0; k < n; k++)` with no MF_RANK_MAX check.
- SUBJECT alone: compose.c:684 `if (w->len < 2 || w->len > MF_WSPAN_POS)` refuses ("the run presence span is 2..MF_WSPAN_POS positions"); SUBJECT memfn.h:674 `#define MF_WSPAN_POS MF_MAX_SPAN_POS` (32); combined memfn.h:661 is 4095. Only the combined (raise) tree is affected.

### MEM-1 — HOLDS
- Quoted at SUBJECT memfn/src/window.c: :227 `uint8_t        *pterm;`, :1144 `uint8_t term = 0;`, :1169 `d->pterm[i] = term++;`, :1290 `d->pterm = al->alloc(al->u, d->pcap ? d->pcap : 1);` (bytes); :1349 `rows->plan_term[i] = d->pterm[i];` into memfn.h:1801 `const uint16_t *plan_term`.
- Re-ran verify/drv2 (copy of memsafe/drv2.c + drv.c; `gcc -g -fsanitize=address,undefined ... memfn/src/*.c`, compile exit 0): plan_term runs 0..255 then wraps to 0 ("265:0"); output `shared term 0 at plan[0]=1 and plan[256]=265 ... shared non-adjacent: 45`. Consequence limited to the reply contract as the critic says (not re-judged for readers).

### SEAM-1 = MEM-2 (a) — HOLDS
- window.c (wdecide_framed, SUBJECT :2799-2802): `!reply_of(d, out, rows) && !reply_frame(fp, out, rows)` -> reply_of writes `rows->plan[i]`/`rows->plan_term[i]` (:1348-1349) BEFORE reply_frame's `if (out->nplan && !rows->plan_test) return -1;` (:2701); on failure only `memset(out, 0, sizeof *out)` (rows not restored).
- Re-ran verify/drv4 (compile exit 0): `DEFINE plan_test NULL: rc=-1 reply_zero=1 plan_untouched=0 plan_term_untouched=0 plan[0]=1`; control `NONE plan_test NULL: rc=0 nplan=3` (the NONE frame needs no plan_test, so only the framed case refuses).
### MEM-2 (b)/(c) — PARTLY
- (b) compose.c:1192-1197 (ask_sel non-window): `kit_class(row, s, out, stp)` fills rows->proof before the `fd_pres(...) || pres_layout_check(...)` refusal; `memset(out,0)` only, rows not restored. Code-true; reachability not driven.
- (c) compose.c:1181-1186: `out->v = MF_CLASS_V; memset(out->proven0,0xFF,...); ... return fd_pres(art, art->nsites + 1, s, FD_PRES_QUIET, out, &why) ? -1 : 0;` — a -1 leaves *out NON-zero. mf_ask (compose.c:1218) just returns ask_sel's rc, no re-zero. Reachable only via an fd_pres -1 (finder.c:786+): `npspan > MF_MAX_PRES` and `need UNSTATED` are pre-refused by site_check (compose.c:717, 563/670) so unreachable; remaining whys (finder.c:808 set_pick > 254; "no routed PRES row decides" ~:848) I did not drive -> reachability NOT VERIFIED. Real defect in the code, latent, no OOB write.

### MEM-3 — HOLDS
- Path quoted: window.c wf_prepare allocates wf_dec/wf_plan/L/fx from `art->a` (:2525-2542 per critic; decide :1281-1291 `wf_pos[extent]`, `pterm = al->alloc(...)` at :1290). Contrast: wdecide_framed uses a private `wd_blk` heap and `wd_free(blks)` (:2780-2808).
- Re-ran verify/drv5 (compile exit 0): ask adds to art arena 7,758 B (span 0), 19,760 (100), 92,660 (1000), 335,660 (4000), 340,844 (4064) B, 2nd ask identical (kept, not reused); define +45,870 .. +516,836 B. Matches the critic.

### EMIT-1 = READ-4 — HOLDS (cost is real; magnitude is a quote-level claim, not timed)
- known.c:650 `for (int d = MF_PROOF_LO; d < MF_MAX_FWD; d++) {` with the inner `for (int b = 0; b < 256; b++)` (:665). MF_PROOF_LO = -MF_MAX_BACK = -8 (memfn.h:308,332), MF_MAX_FWD = MF_WREACH = 4096 (:333, :695) -> 4104 offsets x 256 = ~1.05M bit-test pairs per call; past max(proof_n, k+1) both sides are all-ones (want memset 0xff / got `ones`). Not timed.
- Cover ask storage: memfn_sites.c:189 `if (ceiling) proof_cap = MF_MAX_FWD - MF_PROOF_LO;` and :193 `pcrec_arena_alloc(&cx->arena, (size_t)proof_cap * 32)` = 4104*32 = 131,328 B. src/core/arena.c:6 `#define ABLOCK_MIN (64 * 1024)`; :17-18 `if (... b->cap - b->used < sz) { size_t cap = sz > ABLOCK_MIN ? sz : ABLOCK_MIN; b = malloc(...)` -> it gets its own ~131 KB block (2x ABLOCK_MIN), never freed until the arena goes. Caller: known.c:419 (cc_served, ceiling=true).

### SEAM-2 — HOLDS
- memfn_sites.c:183-199 pcrec_memfn_rows: after `mf_rows_need(s, &proof_cap, &plan_cap)` allocates `r->proof` (proof_cap*32) if proof_cap and `r->plan`, `r->plan_term`, `r->plan_test` (plan_cap entries each) if plan_cap, all from `cx->arena`; no ask-kind parameter (only `ceiling`), so every one of the 8 callers (known.c:419, emit_dfa.c:7162, 7720, 7779, 8512, 8926, 11601, 16348) gets both parts as sized by the site. Qualification: each part is allocated only when mf_rows_need returns nonzero for it (proof_cap nonzero only for nalt/FIND sites, compose.c mf_rows_need), so "both for every ask" holds for window sites with alts/FIND, not for all sites; caller never states which parts it reads.

### READ-2 — HOLDS
- `grep -rn _Static_assert src | grep -E 'PCREC_MAX_REQ_RUN_SCAN|PCREC_PREFIX_K_MAX'` at SUBJECT worktree: one hit, src/gen/emit_dfa.c:1446 `_Static_assert(PCREC_MAX_REQ_RUN_SCAN <= MF_WSPAN_POS,`; in R/combined/tree: the same single hit (now binds against 4095, so non-binding in practice). No PCREC_PREFIX_K_MAX assert in either.
- memfn_sites.c:629-631 window_bounds_check: `w->len < 1 || w->len > MF_WSPAN_POS || w->start < -MF_MAX_BACK || w->start + w->len > MF_WREACH` -> reads MF_WREACH = 4096 (memfn.h:695), so non-cover reach is checked against 4096, not 64.
### READ-3 — HOLDS (on the combined approximation tree only)
- Ran `R/combined/tree/build/pcrec -p rx --features all --window-search-width=W -o verify/o8/rx.c --pattern '[0-9a-f]{4095}'`: W=32 rc=0; W=4095 rc=1 `pcrec: pattern too large: 612696 bytes of emitted code (limit 500000), which gcc cannot compile in reasonable time ...`.
- Refusing limit: src/core/compile.c:3448-3450 `cap_code = defo.max_emit_code_bytes ? ... : (unsigned long long)PCREC_MAX_VM_EMIT_CODE_BYTES;` and the throw at :3594 `if (emit_code > cap_code) pcrec_ctx_fail(...)` (message at :3594-3600). It is the CODE-bytes cap (PCREC_MAX_VM_EMIT_CODE_BYTES, default 500000, raisable by --max-emit-code-bytes), NOT PCREC_MAX_EMIT_BYTES (limits.h:759, the total-source cap `cap_tot`, a separate branch just below at :3602).
### CHECK-2 — HOLDS (plant)
- tests/memfn/arm_fixtures.c:2419-2426 `pur_vals` copies the reply and sets `x.plan = x.plan_term = x.plan_test = NULL`; :2640 `mf_wreply rv = pur_vals(&r);    /* plan_test NULL on NONE: zero too */` then :2641 `pur_ok(!memcmp((const char *)&rv + offsetof(mf_wreply, framed), zero + ..., sizeof r - offsetof(...)), m)` -> a NONE reply with non-NULL plan_test passes by construction.
- Re-ran plant P1 (copy of checks/kp/P1/src; diff vs SUBJECT is the single added line at window.c:2841 `if (!rc && rows && rows->plan_test && out->nplan) { memset(rows->plan_test, 1, out->nplan); out->plan_test = rows->plan_test; }`): build exit 0; `fx --purity`: passed 7874 / failed 0, rc 0 (plant not caught by the S3086 purity row). d27 side not re-run.
### CHECK-3 — HOLDS (plant P2 rerun; pointer shortcuts quoted)
- arm_fixtures.c:2448 `if (a->nplan && la != lb &&` (equal pointers skip the memcmp); d27_frame.c:596 `if (a == b) return 1;`.
- Plant P2 (diff: reply_of writes function-static `sp_plan`/`sp_term` and points the reply at them, not `rows`): build exit 0; `fx --purity` 7874 / 0, rc 0 — identical to the clean control. d27/G2 identical-to-clean claims not re-run.

### HOUSE-4 — PARTLY (ordering is as stated; no corruption path shown)
- memfn_sites.c:568-577 pcrec_memfn_wspan: `size_t n = len > 0 ? (size_t)len : 1;` sizes `set`/`table` from the full int, then `w->len = (uint16_t)len;` (:573) and `w->core_len = (uint16_t)len;` (:577); window_bounds_check (:629) reads the already-truncated `w->len`. So len 65536+k is seen as k (or 0 -> refused as <1). The wrapped len is never larger than the allocation, so no overflow; the defect is only that a too-large len can pass the bounds check when len mod 65536 is in 1..MF_WSPAN_POS. No caller passes such a len (not driven).

### SEAM-3 / READ-5 — HOLDS (stale sentences exist at SUBJECT; the diff touches only docs/design/memfn/span_pick/probe/probe.c under docs/design)
- docs/design/memfn/window_site.md:133 `(`mf_class.proven[]` is fixed)`; :184, :290 also `proven[]`.
- docs/design/memfn/plan_frame.md:216-217 `int mf_wdecide(const mf_art *, const mf_site *site, const mf_hooks *def, uint8_t call, mf_wreply *out);` (no `rows`); :313 `plan_test` row: `uint8_t[MF_WPLAN_MAX]` ... `NONE past nplan`.
- docs/design/kit_proof.md (note: path is docs/design/, not docs/design/memfn/): :205 `mf_class.proven[d]`, :769 `proven[d - MF_PROOF_LO]`, :781 `#define MF_MAX_FWD  (MF_MAX_SPAN_POS + MF_MAX_AHEAD)`.
- Whether the lane report flags them is unverified (denylisted).

## PROBED-AND-HELD
- All 11 items were re-grepped/re-run; no critic claim REFUTED. Qualifiers: MEM-2(c) reachability unproven, HOUSE-4 benign, READ-1/READ-3 only on the combined approximation tree, CHECK-2/3 d27/G2 legs not re-run.

VERIFY COMPLETE
