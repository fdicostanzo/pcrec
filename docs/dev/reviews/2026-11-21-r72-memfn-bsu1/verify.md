# VERIFY — r72 memfn-bsu1

## Findings

### SLOT-2 — HOLDS
`plan_ix(w, w->hl)` at window.c:4087 (`d_hors_head`, `int ih = plan_ix(w, w->hl);`) and at window.c:4106 (`hors_skip`, same expression). `grep -n plan_ix` shows only the definition (3956) and those two uses.

### SLOT-3 — HOLDS (a-e all)
(a) block_span.md (SUBJECT 4a098e1e4) line 437 "six `gate_contract`s, one per row" and §14 U1 row (line 1380) "its six contracts"; window.c has four `WF_CT_S` (ct_s_deny/force/lever/head, lines 1920-1923) and four rows (S_DENY..S_HEAD).
(b) design line 438 `use_s_none = { MF_ANY, MF_ANY, MF_PH_DEFINE, 0, GATE_ALWAYS }`; window.c:1917 uses `NU(use_nothing)` (shared with A-empty/A-floor, line 792). Note the code contract is not that array only: WF_CT_S also sets the WF_SERVES fields, still all-wildcard.
(c) design lines 458/469 store `{i, k, form, j}`; code line 1970 stores `(struct wf_stretch){ i, k, wf_spanrows[r].h(&x) }`, i.e. `{i, k, h}`.
(d) window.c:1891 "The rows read plan facts, not site fields" vs 1899-1900 `s_deny_holds`/`s_force_holds` reading `x->d->s->opts` (the site's options) and 1901-1906 `s_lever_holds`/`s_lever_h` reading `x->d->art->levers`/`->span_head` (art, not plan).
(e) window.c file header (lines ~47-49): "Every table is a `kit_table` on the one walk (kit_walk; Tables A, M, E, and T-FIND's fd_rows)" - no wfS (wfS is named only at 1471 and from 1880).

### SLOT-4 / HOUSE-2 — HOLDS (a and b)
(a) window.c:1901-1904 `s_lever_holds` returns `x->d->art && (...)`, but `wf_stretches` (1952-1960) executes `const mf_art *art = d->art;` then `art->nsites + 1` in the `gate_tctx` initializer before any walk: art is dereferenced first, so the NULL test is dead.
(b) window.c:1969 `if (r >= WF_NSROWS) return -1;  /* T-head always holds: unreachable */`; callers: 2583 `if (wf_stretches(...)) return -1;` (no why text, E-find prepare) and 2696-2699 `*why = "out of memory"; return -1;`; the header comment of wf_stretches says "-1 out of memory". The unreachable case would be reported as out of memory at the floor caller.

### SLOT-5 — HOLDS
`wf_tables_check` (window.c:2488-2507) checks `wf_erows[i].holds/.ct`, `wf_spanrows[i].holds/.h/.ct`, `ren_search[i].k.holds` for E_FIND and the fused key; no check of `ren_search[].skip` or `.head` for NULL. `wf_find_prepare` calls `w->skip = w->srch->skip(w);` unconditionally (window.c:2582). Rows: all four E-find search rows set `stop_skip`/`hors_skip` (2262-2274 region); the E-stmt rows (arm != NULL) carry a skip slot too, not called by this path. Latent only (no current row NULL).

### HOUSE-3 — HOLDS
`wf_spanrows[]` initializers (window.c:1932-1935) all end `NULL }` in the `opt` slot; `s_opt` (1941) returns it; it is the walk's opt column, never non-NULL today (design U2's V rows would be the first).

### HOUSE-4 — HOLDS
tests/mech/sabotages line 3 (SUBJECT tree): S3278 "wf_span_head (memfn/src/window.c) drops the `--memfn=span-loop` arm"; S3279 "wf_span_head (memfn/src/window.c) drops the lever"; S3281 "wf_span_head (memfn/src/window.c) drops the `--memfn=no-span-loop` arm"; S3282 "wf_span_head (memfn/src/window.c) honours the lever ... takes every N as 0". All present tense; `wf_span_head` no longer exists in the subject (the diff touched 7 lines in each of these four files, S3280 5 lines).

### HOUSE-5 — HOLDS (three lines over 100 columns)
From `git diff 367cbdedb 4a098e1e4 -- memfn/src/window.c`, added lines wider than 100: 
- window.c:1472 width 130 (" * block_span.md §3) and stored once in the plan's stretch list. A periodic segment, such as `(ab){500}`, is NOT built (r45_reply...")
- window.c:3605 width 114 (" * FORMS) under inline head `head`: the number of entries from `i` on that one loop tests, at least 2 (the minimum...")
- window.c:2262 width 101 (`"fn-pair's two memchr streams (ofs_pair_text) at the stop's offset", stop_skip },`)
Next widest added line is 97.

### CORPUS-1 — HOLDS
span_seed.rxt:46 `pattern \b[0-9a-f]{32}\b`, :86 `mc "3a18f6d4b2907e5c3a18f6d4b2907e5ca18f6d4b2907e5c3a18f6d4b2907e5c318f6d4b2907e5c3a18f6d4b2907e5c3g" 0`. `kit/pcre2_oracle` on that pattern and subject prints `nomatch` (the 96 hex digits have no word boundary inside), so the 0 is correct. `grep '^mc ' | awk '{print $NF}' | sort | uniq -c`: 40 x `2`, 1 x `0`. So it is the only non-2 of 41 (the 0 is right; the fact is as stated, not an error).

### CORPUS-2 — HOLDS
block_span.md §10.1 (lines ~1010-1011): "X a byte outside it (`\n` for `[^\n]`, `a` for `[\x80-\xbf]`, `g` or `!` otherwise". gen_span_seed.py:65 `OUTSIDE = b"g!\na-~"` and `outside(cls)` (122-126) returns the first of OUTSIDE not in the class: for `[\x80-\xbf]` that is `g`, not `a`. Spec and generator disagree (generator is the data; doc wording stale).

### CORPUS-3 — PARTLY (2 of the 5 checked; the count 5 not independently established; the gate claim holds)
`kit/emit.sh trace:subject` (grep -c 'table=wfS' err.txt, counts of MFTRACE lines): `[0-9a-f]{1001}` default width: 0; with `--window-search-width=4095`: 6. `[0-9a-f]{20}[g-z]{20}` default: 0; at 4095: 12 (two selections). Control patterns at default: `[0-9a-f]{16}`, `{17}`, `[A-Z]{17}`, `{32}`, `\b..{32}\b`, `ab[0-9]{26}`, `[0-9]{24}`: 6 each. Gate: `git diff 367cbdedb 4a098e1e4 -- . (minus denied, design docs, span_seed.rxt)` contains no `4095` string at all; only block_span.md (design) §10.2/G-4 describes compiling the .rxt's 41 patterns at 4095, and no file in the diff implements it (the population pins in run_rxtsource_tests.sh/manifest do not mention it). I did not enumerate the other three patterns (compile cap).

### CORPUS-4 — HOLDS
tests/memfn/CLAUDE.md (SUBJECT): the new heading `### SPAN-SEED (R-47 U1, lane bsu1; ...)` with its bullet is inserted (diff @@ -67) directly after the rq2 section's bullet and before `- **run_d3floor.sh**, **d3_floor.py** ...` which previously followed rq2's heading as a bare bullet; that pre-existing D3-floor bullet now sits under the SPAN-SEED heading. (The same diff also moves a worked example out of the rule-4 bullet into NOTES.md.)

### EQUIV-2 / SLOT-7(c) — HOLDS
`kit/emit.sh trace:subject` on `[0-9a-f]{20}[g-z]{20}` with `--window-search-width=4095` (output dir verify/o13w): two lines
`MFTRACE END table=wfS art=1 site=1 phase=define chosen=T-head would_decline=0 fields=-`, byte-identical (lines 65 and 71 of err.txt; the SEL lines 60 and 66 are likewise identical). Nothing in the record names the stretch (i, k).

## PROBED-AND-HELD
Compiles used: 15 of 30 (all trace:subject, single pattern each). Witness lengths: patterns reached 20+20 = 40 positions (min, plus `{16}`=16) to `{1001}` = 1001 positions (max).

VERIFY COMPLETE
