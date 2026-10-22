# wsframe report: D172's window.c frames under the R-28 bar

Lane wsframe (in worktree `worktrees/wsmain`, branch `lane/memfn-wsmain`, from tip 4c3f06470). Serves R-29: the D172 branch with main merged in must pass R-28's existing gate (no kit stack frame over 4096 B, `tests/memfn/run_link_checks.sh`).

## Change (code commit aba15302e, `memfn/src/window.c` only)

| function | before | after | mechanism |
|---|---|---|---|
| `pcrec_mf_wdecide` | 10,720 B | 64 B | `wf_dec` on the heap: `calloc`/`free`, -1 on a refused allocation (R-28's `mf_set_terms` shape, terms.c) |
| `e_legacy_holds` | 5,088 B | 48 B | `wf_legacy` allocated once by `wf_prepare` from the art's arena beside `d`/`w`/`pid` (its existing "out of memory" refusal), passed in `wf_ex`, reused by the final translation |

Why two mechanisms: `mf_wdecide` is documented PURE ("no art state", memfn.h), so it does not grow the art's arena; both its callers (emit_dfa.c `req_run_member`, `window_reply_ask`) already turn -1 into a loud `pcrec_ctx_fail`. `e_legacy_holds` is a Table E predicate and cannot refuse (a 0 would silently pick E-generic and move bytes), so its storage comes from `wf_prepare`, which already allocated the final `wf_legacy` from the art's arena and refuses loudly; the allocation moves before the walk and that later allocation is removed (one fewer arena block on the legacy path, one more on the E-generic path).

Init / lifetime / reentrancy:
- `decide()` begins `memset(d, 0, sizeof *d)` and `translate()` begins `memset(L, 0, sizeof *L)`, so the old uninitialised locals and the new heap/arena storage hold the same contents (`calloc` zeroing is redundant).
- `mf_wdecide`: one `calloc`, no early return between it and the `free`; the refusal paths before it allocate nothing.
- `L` is arena-owned (the art's lifetime, as the old final `L` was); every refusal in `wf_prepare` returns before any use; the walk's E-func and E-stmt calls and the final translation each rewrite it whole.
- No statics: each `mf_wdecide` call and each `wf_prepare` call (pre-check parts included) owns its own storage, so nesting or recursion through `kit_legacy_serves` cannot share scratch.

## Validation

- Frames (`gcc 15.2 -O2 -std=gnu11 -fstack-usage`, run_link_checks.sh's recipe), top 6 after: 3,600 `pcrec_mf_form_hash`; 3,456 `define_sel`; 3,376 `pcrec_mf_wf_parts_prepare`; 3,184 `pcrec_mf_kit_report_exact`; 3,024 `pcrec_mf_wf_parts_check`; 2,448 `pair_facts`. All under 4,096. `tests/memfn/run_link_checks.sh`: 11 passed, 0 failed (R-28: 306 functions measured, largest 3,600).
- Byte identity: 19 patterns (the brief's 7: `((?i:abc))`, `\b[0-9a-f]{8}\b`, `foo|bar`, `(?m)done$`, `\w(?=\d)\w`, `\d{4}`, `\bcat\b`; and 12 of run_wreply.sh's 13 witnesses: the UUID, `in|instanceof`, `\Bfoo\B`, `\b\.[0-9]{4}Z`, `abc`, `(?i)x/1234`, `xy.*xy(?i:z)`, `\babcd\b`, `foo\b`, `a(b|c)+d`, `\bx`, `x[ab]cdefg`) x `-e byte`/`-e utf8` x default/`--engine=vm`, `-p rx -fcomments --features all --emit-main`: 76 outputs, 76 identical, exit codes identical (all 0). REACH (gdb hit counts on the built CLI): `e_legacy_holds` hit in 76/76 compiles, `pcrec_mf_wdecide` in 60/76.
- `make -j16` clean; `make strict` clean.
- `memfn/tests/run_g2_win.sh`: 6,032 passed, 0 failed (ASan+UBSan driver 3000/0; W1 ref-defects 2-5 red as they must be). `tests/memfn/run_wreply.sh`: see the handback (log `build/wsframe/wreply.log` in the worktree; it waits on the box lock).
- Job `docs/dev/lanes/wsmain_job_586-kit-wsmain-heavy --dry-run`: resolves unchanged (cap 10800, expect sweeps=5); it builds the tip, so it needs no edit.

Not touched: `memfn/CLAUDE.md`'s peak statement still holds (largest 3,600 B); its "next `define_sel` 3,408 B" reads 3,456 B at this tip (from merged main, not this change).
