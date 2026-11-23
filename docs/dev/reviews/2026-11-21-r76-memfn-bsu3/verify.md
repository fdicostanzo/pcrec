# VERIFY: r76 memfn-bsu3


## Verdicts

### CHECKS-2: HOLDS
- Subject simd_floor_check.py C9 loop (review tree, lines 466-475): `inl = always_inline_sel(ton)`; `if r and r.returncode == 0: rec['issues'] += o0_inline_issues(...)`; `for fn, vw in sorted(sel.items()): if fn in inl: continue` then the "is not defined in the -O0 object" issue. BASE (base tree lines 375-382) has no `inl` skip: a failed -O0 compile left `defined` empty so every selector got the "not defined" issue.
- Repro re-run: fakepcrec.py read first: it runs the REAL build/pcrec, then (only for `[A-Z]{32}` at -fmemfn-simd=x86-64-v3) rewrites one `bm` line in the emitted artifact and corrects SIMD_GUARDED_BYTES; it touches no tree. Output `-p rx --features all -fmemfn-simd=x86-64-v3 --pattern '[A-Z]{32}'`: `gcc -O2 -Wall -Wextra -Werror -c` rc 0; `gcc -O0 -c` error "the last argument must be an 8-bit immediate" (m.c:80). Real script (critic's mut/tree copy = review-tree script + one NAMED row `vtest`; diff confirmed that is the only difference) with `--every 100000`: "x86-64-v3: named witness vtest is a mover" PASS, and the log carries zero `C9` issues (only the K35 floors 55 and the x86-64 not-a-mover line fail; rc 1). So the -O0 build break is silent. 

### CONTRACT-1: see below (appended after check)

### CONTRACT-1: HOLDS (the "see below" stub above is superseded by this entry)
`build/pcrec --list-axes` (review tree) line 229: `span-vector ... (no vector body is built yet); denied, ...`. `build/pcrec -p rx --features all -fmemfn-simd=x86-64-v3 --pattern '[0-9a-f]{17}' -o x.c` (first line `Pattern: [0-9a-f]{17}`, abi 112): 5 occurrences of `vs0__w32` in the artifact. The help string is false at the subject.

### SLOT-1: HOLDS
window.c:1927-1932: comment "The window row's lower bound 16 is ALSO the safety floor ... a re-measure may raise it, never lower it", `enum { WF_VWIN_LO = 16, WF_VWIN_HI = 1000, WF_VSCAN_LO = 24, WF_VSCAN_HI = 64 }`. vs_w32_block :4373 `if (k < WF_VWIN_LO) return kit_fail(... "(16 at least)", k);` :4375 `const unsigned b = k >= 32 ? 32 : 16;`. T-vscan holds (:1950-1954): `fd_brow_is(brow, FD_NAMED_R7W) && x->k >= WF_VSCAN_LO && x->k <= WF_VSCAN_HI && s_v_ok(x)` - it reads WF_VSCAN_LO, not WF_VWIN_LO. Model: with WF_VWIN_LO = 32 a T-vscan stretch k 24..31 still holds (24 <= k <= 64), selects the V row, whose define path (:4443) calls vs_w32_block (only call site, grep), and the assert k < 32 fails -> kit_fail (hard failure, message still says "16 at least"). Also literal 16 appears in message and `: 16`. Today (16 vs 24) latent only.

### SLOT-2: HOLDS
plan.md at fb258a000 line 323-327: `[BSPAN-VANY-RIDE] STATE:not-started -- block span: vany joins the lifted selector writer`; status "U2 lifts ofsskip's two writers into one shared kit helper (r68 ruling R-4)"; trigger "vany's next touch (... block_span.md section 5, \"One writer\")". block_span.md at ec578d053 :850: "when vany is next touched, the two-function block and vany's level block are ..." (the lift) and :1728-1729 §14 item (5): "vany's ride-along: the two-function level block and vany's level block lifted into one writer at vany's next touch (§5)". The row names only the selector lift.

### SLOT-3: HOLDS
window.c:1944 `s_v_ok: !x->w->table[x->i] && !x->nv`; :2024 `unsigned nv = 0; /* V stretches so far */`; :2045 `unsigned j = wf_spanrows[r].define ? nv++ : 0;` (nv counted on `define`; the nv comment says "V stretches" but the key is the define column). wf_tables_check :2572-2576 checks only `!holds || !h || !render || !ct`; no line pairs `render == wf_span_v` with `define != NULL`. Latent (no non-V define row today).

### SLOT-4: HOLDS (members exist; line numbers slightly off but real)
window.c:4439 `if (art->levels >> LV_X86_W32 & 1 && out->simd_open && out->simd_close)`; LV_X86_W32 at :4392, :4393, :4439, :4440, :4445, :4448 (six, critic said five incl. :4439 listed separately: all present). vrun.c:774-802 `vrun_w16_ct`/`vrun_w32_ct`/`mfind_w16_ct`/`mfind_w32_ct` with `[FLD_target] = MF_ANY & ~CM_NO_LEVEL(LV_...)` (:779 shown for w16) and `vrun_uses` :770; ofsskip.c:596 fn_rungs exists.

### SLOT-5: HOLDS (members exist)
(a) ofsskip.c:726-733 fn_level_name (`%s__%s`), :816 `body_fn` oom line (the `__body` build is at the nearby body_fn), vany.c:161 and :240-242 (`snprintf(suffix/fall ... "__%s"/"%s__body")`), window.c:4306-4317 vs_name. (b) ofsskip.c:808 `o->simd_open && o->simd_close` into fn_in, read at :486 `if (!x->brackets) return 0;`; window.c:4439 inline; vany.c:211 `if (levels && (!o->simd_open || !o->simd_close)) return vany_refuse(...)`. (c) ofsskip.c:777-782 fn_note_form; window.c:4446-4448 token write. (d) vany.c:189 vany_selector, ofsskip.c:643 kit_selector, :743 fn_level_block, vany.c:155 vany_level: all exist as described.

### CHECKS-3: HOLDS (as a weakness in the check's shape; the miss itself is a modelled future, not run)
Code (review tree tests/memfn/simd_guarded_check.py): :365-367 `if sites: ... rec['counts'].append('simd-form'); if rec['key'].startswith('named:'): rec['counts'].append('simd-form-named')` (kind-blind: any form token, any arm); :169 `'simd-form-named': 9`; :445-451 floor test is `n >= floor` (total only); :439-441 "rows no artifact read" uses `rows_read |= rec['rows']` from EVERY artifact (corpus sample included). No per-row expectation for the named `vspan` key.
Count (subject compiler, `-p rx --features all -fmemfn-simd=<t> --pattern ...`, the 9 NAMED patterns x x86-64 / x86-64-v3 / armv8-a, 27 emits, RX_MEMFN_FORMS read from each): cells with a form = 9 exactly: vrun, vrun-fixed, vrun-gap, vrun-long each `vrun@w16` at x86-64 and `vrun@w32+w16` at x86-64-v3 (8), `vspan` `span-vector@w32` at x86-64-v3 (1); all other cells "none" (armv8-a none for all, vspan none at x86-64). So a V loss reads 8 < 9: red today (HELD), and compensation by any other named gaining a form is arithmetically open (>=).

### CHECKS-1: HOLDS
Method: copied tests/memfn/simd_floor_check.py from the review tree twice (HERE pinned to the review tree's tests/memfn so the imports and corpus resolve), built the levels dumper as run_simd_floor.sh does (`gcc -O2 -I memfn/include simd_levels.c build/libpcrec.a`, rc 0), and ran each copy with `--pcrec <plants/S3515 compiler> --every 25 --jobs 2` under nice (2 x 100 compiles). Plant compiler: rc 0 on `[A-Z]{32}` at x86-64-v3 (emission silent-moves: the diff against the subject's artifact is the `__w32` head line and the stamp; first line carries `Pattern: [A-Z]{32}`); the suite then fails.
- Copy A (`o0_inline_issues` returns [] -- the -O0 rule a no-op): rc 1, "checks failed: 6": the 3 V movers `[A-Z]{32}`, `[\x80-\xbf]{25}`, `\w{32}` each FAIL "V head: rx_mf1_vs0__w32 is `unused int`, expected `__attribute__((always_inline)) int`" (text leg); 0 `-O0:` lines; plus the pre-existing K35 floors (55, at every 25) x2 and "no clean vector span mover to plant the V controls on". So S3515 stays DETECTED with the -O0 rule deleted.
- Copy B (the V-head loop disabled, `for m in []`): rc 1, "checks failed: 45"; 42 of them `C9 <cell> -O0: rx_mf1_vs0 is always_inline, yet its family defines rx_mf1_vs0__w32` and `... rx_search, which calls rx_mf1_vs0, holds no pshufb` (3 V movers x 7 C9 cells x 2), 0 V-head lines. So the -O0 rule alone also catches S3515.
Verdict: two independent legs reject the plant; the mech row (suite-level SAB_SUITES) cannot tell which leg fired, so the -O0 rule's rule-leg is not isolated by S3515 as the row header claims ("the -O0 rule is the leg that sees it"). (Whether the mech harness has any per-leg field was not re-checked by me; the critic's statement that it has none is not verified.)
VERIFY COMPLETE
