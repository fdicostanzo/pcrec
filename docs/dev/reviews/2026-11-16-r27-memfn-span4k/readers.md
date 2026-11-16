# READ findings

## Findings

### READ-1 — CONFIRMED (on the combined approximation tree only) — answer (memory safety) — the raise lets a run presence span exceed 32 positions, and the derived run part then writes past `mf_pred.rank_pos[MF_RANK_MAX]` / `rank_ppm[]` (and, on a longer run, past the heap block)
- Where: raise 2794f4696 lifts `compose.c:684`'s check (`w->len > MF_WSPAN_POS`, the run presence span's own contract) from 32 to 4095. Nothing else bounds the run part. `window.c` `run_part_terms` (combined tree :3099-3160) then calls `run_rank(..., b - a, q)`. `run_rank` (:1580-1595) writes `p->rank_pos[k]` / `p->rank_ppm[k]` for k < n with no `MF_RANK_MAX` (32) check. The same function also writes `q->term[q->nterm]` per position outside the stretch, with no `MF_MAX_TERM` check (not exercised below).
- The design's list missed it. r45_reply rev 6 §1 "What the kit owes": the pre-check's run part only widens `mf_run_reply` and allocates `run_bytes` by length. The 32-shaped ranking and term arrays are not named. The raise's own commit adds `WF_LEGACY_POS` (translate) and the D-hors cap, but no row contract here (K96: each row checks its own contract).
- Repro: `R/readers/probe/longrun.c`. It states an ALL_PRESENT site (VM_ATTEMPT and DFA_SCAN), one REQUIRED run presence span of L one-member positions, plus the derived run part (`preds[0].fn_ref = 1`), then calls `mf_ask` and `mf_define`. It is built against the combined tree's `memfn/src/*.c` with `-fsanitize=address,undefined`. Observed:
  - L=32: clean, define rc 0;
  - L=33 and L=40: UBSan reports `window.c:1592: index 32 out of bounds for type 'uint16_t [32]'` and the same at :1593 (`uint32_t [32]`). These are silent in-struct overwrites. The define then fails late with "outside the vocabulary ...: rank_n > MF_RANK_MAX";
  - L=100 and L=4095: ASan reports `heap-buffer-overflow WRITE of size 4 in run_rank window.c:1593`.
  - Expected: a named refusal before any write. Either the run presence span contract keeps 2..32 (a `WF_LEGACY_POS`-like bound of its own), or `run_part_terms` declines a stretch longer than `MF_RANK_MAX` and more terms than `MF_MAX_TERM`.
- Reach from pcrec: none today. pcrec states the pre-check run at most `PCREC_MAX_REQ_RUN_SCAN` = 32. But the bound that ties pcrec to 32 is gone too (READ-2), so the kit's contract is the only guard, and it now says 4095.
- Effort: small (one decline line in compose.c's run-span contract or in run_part_terms, plus a witness row at L=33). Blast radius: the kit's ALL_PRESENT derived run part, any host stating a run over 32. Subject: raise 2794f4696, judged on the combined tree; SUBJECT alone refuses L > 32 at compose.c:684.

### READ-2 — CONFIRMED (by grep) — design — main's ruling other-sites-at-32 YES has no enforcing bound in any tree: the reach half is already gone at SUBJECT, and both halves go with the raise
- The ruling (r45_reply rev 6 §7; `R/subject/r45_request_and_rulings.md`): "pcrec keeps its other window sites at 32 positions and reach 64 by its own assertions: one `_Static_assert` per construction bound it owns (`PCREC_MAX_REQ_RUN_SCAN`, `PCREC_PREFIX_K_MAX`) at its own writers, not a site kind in `window_bounds_check`, which also replaces the now-loose `emit_dfa.c:1446`".
- At SUBJECT:
  - `window_bounds_check` (`src/gen/memfn_sites.c:629-630`) reads `MF_WREACH`, which is now 4096 (R1). So every non-cover site's reach is checked against 4096, not 64, and nothing in pcrec states 64.
  - The positions half still holds, only through `MF_WSPAN_POS` = 32: `emit_dfa.c:1446` `_Static_assert(PCREC_MAX_REQ_RUN_SCAN <= MF_WSPAN_POS)` plus `window_bounds_check`'s `len` clause.
- On the combined tree (with the raise): `MF_WSPAN_POS` is 4095. `emit_dfa.c:1446` is the ONLY `_Static_assert` over either construction bound (grep `_Static_assert[^;]*(PCREC_PREFIX_K_MAX|PCREC_MAX_REQ_RUN_SCAN)` over src/ at SUBJECT, at main 4e8f281cd, at lane/covs2afix 7983d4798 and on the combined tree: one hit each, that line), and it is now non-binding. No `PCREC_PREFIX_K_MAX` assert exists anywhere. So a non-cover statement of 33..4095 positions, or reach 65..4096, passes every pcrec check and reaches the kit's 4095 contract. READ-1 shows one kit path that corrupts memory there.
- Construction still keeps them small: pre-check run <= `PCREC_MAX_REQ_RUN_SCAN` 32; reseed walk <= `PCREC_PREFIX_K_MAX` 24 spans of 1; `find_window` spans of 1-2 at offset <= 0; the parked R <= 32. So this is a missing WITNESS, not a live mover (no probe found a non-cover span over 32).
- What would close it: the ruled asserts land on main's combined branch IN THE SAME LANDING as the raise, and the reach-64 bound gets its pcrec name (main's, r45read C2). Until then, the raise should not land alone.
- Severity: design (an unenforced ruling) / answer (latent, through READ-1). Effort: small (two `_Static_assert`s at `req_pres_spans`/`pf_window_of`, plus a reach constant). Blast radius: every non-cover window site. File: `src/gen/memfn_sites.c:629`, `src/gen/emit_dfa.c:1446`.

### READ-3 — CONFIRMED (on the combined approximation tree only; the cause is pcrec's stage 2, not the kit) — answer — a legal `--window-search-width=4095` turns `[0-9a-f]{4095}` from a compiled artifact into a compile FAILURE
- Repro: `combined/tree/build/pcrec -p rx --features all --window-search-width=W -o OUT/rx.c --pattern '[0-9a-f]{4095}'` (old outputs deleted first):
  - W=32: rc 0, engine route (`ENGINE_SEL "selected"`, `RX_DFA_SCAN "unanchored"`);
  - W=4095: rc 1, "pcrec: pattern too large: 612696 bytes of emitted code (limit 500000) ...". `x[0-9a-f]{4000}y` at W=4095 does the same (598,823 B).
  - W=2000 on `[0-9a-f]{2000}`: rc 0, `"cover"`, 304,313 B with a large-artifact warning.
- Expected, per the R-45 request's own FACT (cost) and cover_cap §11: a cover whose text exceeds the cap is LOST to the engine route (the size-cap ladder), never a failed compile. The code-bytes refusal here (limit 500,000) is not the ladder's `PCREC_MAX_EMIT_BYTES` path, so a caller-legal width fails the compile outright.
- Not a kit reader. It is filed because the lens's own probe found it, for routing to main's stage-2 B-list (the per-width "survives the cap" record). It rests only on the approximation tree.
- Severity: answer (availability). Effort: unknown (pcrec side). Blast radius: every fixed-width class pattern above about 2,000-3,000 positions at a width that admits it.

### READ-4 — SUSPECTED — speed (compile-time, minor) — B5's loop bound is still the CEILING (`MF_MAX_FWD`), now 4104 offsets x 256 bit tests per cover attempt at every `k`
- Where: `src/gen/known.c:650` (`for (int d = MF_PROOF_LO; d < MF_MAX_FWD; d++)` with 256 `kn_has` pairs per offset). This was 40 offsets before R1. Past `max(MF_PROOF_LO + proof_n, k + 1)` both `want` and `got` are all ones, so ~4,060 of the 4,104 iterations compare ones with ones on a short cover.
- Design §5 (b) lists `known.c:649` as a loop that "becomes bounded by the count". SUBJECT kept the ceiling bound and changed only the row read.
- What would confirm it: the coordinator's compile-cost record (`covcost2`). I took no timing number (the round forbids timing). Fix: bound the loop at `max(MF_PROOF_LO + proof_n, k + 1)`, or memcmp a row before the bit loop. Effort: trivial. Blast radius: every cover compile attempt.

### READ-5 — CONFIRMED (by grep) — doc — none of design §5 (h)'s doc readers moved at SUBJECT
- The design says these are "updated in the build or flagged in its report". I cannot see whether the report flags them: it is denylisted. At SUBJECT they still state the pre-R-45 carrier:
  - `docs/design/memfn/plan_frame.md:313`: `plan_test` is `uint8_t[MF_WPLAN_MAX]`, with "NONE past `nplan`", which SUBJECT retired;
  - `docs/design/memfn/window_site.md:133`: "`mf_class.proven[]` is fixed";
  - `window_contract.md:1351` and `docs/design/run_pos_set_stage3_readiness.md:61`: `MF_WSPAN_POS` = `MF_MAX_SPAN_POS`, `set[MF_WSPAN_POS][32]`;
  - `docs/design/kit_proof.md` §4.2 (:769-794): `MF_MAX_FWD (MF_MAX_SPAN_POS + MF_MAX_AHEAD)` and `proven[MF_MAX_FWD - MF_PROOF_LO][32]`;
  - `docs/design/span_arms.md:210`;
  - `docs/dev/kvcensus/kvdfa.py:25`: `CAP = 32  # MF_MAX_SPAN_POS's derivation`.
- `memfn/include/CLAUDE.md` and `memfn/CLAUDE.md` did move. docs/spec has no reader (grep: none).
- Severity: doc. Effort: small (a sweep of 7 files, or a report line naming them). Blast radius: design-tier readers only. If the report already flags them, drop this.

## PROBED-AND-HELD
- **The widened `mf_wspan` fields** (`len`/`core_lo`/`core_len` to uint16_t), SUBJECT. Readers grepped over src, memfn, tests and the span_pick probe for narrowing reads, `(uint8_t)` casts and `%hhu`; no narrowing read found.
  - pcrec's writers respelled to `(uint16_t)` (`memfn_sites.c` `pcrec_memfn_wspan`/`_core`).
  - The kit: `wf_check`, `kit_last_stated`, `wf_extent` and `wf_stated_offsets` read them as int64/long/unsigned.
  - `formhash.c`'s `fh_work` got its own 2-position lists, and its shapes state at most 2.
- **`set`/`table_ref` now pointers.** The only pcrec writer path is `pcrec_memfn_wspan` (arena, exactly `len` entries); every pcrec `mf_wspan` comes from `pcrec_memfn_walt_spans` plus that writer (grep `mf_wspan` in src: 4 construction sites). Arena storage of exactly `len` means a too-long statement can no longer overrun the struct before `window_bounds_check` runs.
- **`mf_run_reply` widened** (four fields to uint16_t, 8 B with no padding). 13 pcrec readers (emit_dfa.c :1155-1221, :1598, :7594, :9047, :9242, :16323) and 12 kit readers all read into int/unsigned. The by-value memcmps (`emit_dfa.c:1665`, `g2_pres_gen.c:999`) are padding-free. All 7 `presence.c` casts are respelled to uint16_t; `KIT_RUN_NONE` is an aggregate of 4.
- **`mf_wreply` nplan/plan/plan_term/plan_test/run_len.** Writers: `reply_of` (rows checked against `plan_cap`, -1 before any write) and `reply_frame` (NULL `plan_test` refused). pcrec readers: `emit_dfa.c:7495` (to `nplan`) and the trace `wreply_same` (deep, with the pointers NULLed before the memcmp). `UnanchStart.wr` copies share arena rows within one `cx->arena`.
- **`proven[]` to `proof_n`/`proof`.** No code reader of `proven[` is left (grep over src, memfn, tests, mech; the only hits are comments and `proof_meta.h`'s renamed list member).
  - B5 (`known.c:654-663`) reads `proof[row]` only under `proof_n`, with all ones outside.
  - `kit_proof_close` copies rows 0 and -1 only under `proof_n`.
  - `wf_plan_class` indexes rows only after R-out, and `end >= last_t + 1`.
  - `term_prove` is clipped to `[MF_PROOF_LO, proof_n)`.
  - `cand_class_eq` reads `proven0`/`proven_prev` by value only, and the `CandAsked` copies share arena rows; `PcrecCover` is itself in `cx->arena`, so `cv->cls.proof` cannot outlive it.
- **Whole-struct compares.** All `memcmp(&` sites over src/memfn/tests at SUBJECT (11) are either a deep compare that NULLs the pointers first (`kit_class_same`, `wreply_same`, `wr_first_diff`, the `arm_fixtures`/`d27_frame`/`g2_win_gen` helpers) or a by-value `run` compare. All `offsetof(mf_wreply, ...)` sites (12) read `framed`/`plan_test` boundaries, and NONE's NULL `plan_test` keeps the frame part zero. No pointer-by-address compare survives. The trace builds compile: `emit_dfa.c -DPCREC_CAND_TRACE -fsyntax-only` and kit `compose.c`/`window.c`/`finder.c -DMF_TRACE -fsyntax-only`, all clean.
- **`MF_WREACH`/`MF_MAX_FWD` 64 to 4096, SUBJECT.**
  - Every array sized by `MF_WSPAN_POS`, `MF_MAX_FWD - MF_PROOF_LO` or `MF_WPLAN_MAX` is `static` or heap (11 sites, all tests: `proof_check.c:275` 262 KB static, `proven_check.c` x2, `run_decide_check.c` x7, `g2_pres_gen.c` x2), and there are no stack arrays.
  - `WF_NPOS` is a clamp only (`wf_extent`). `wf_stated_offsets` uses a heap bitmap.
  - `d27_frame.c:332`'s clamp is a generator's own.
  - `gate.c:627` is a clamp, still true. `G2W_REACH 64` / `G2W_MAXPOS 32` are G2's own generator ranges.
  - `cc_fits` stays at 32 through `MF_WSPAN_POS` (READ-2 covers the reach half).
- **D94 abi number readers.** `MF_SITE_ABI` 30 and `MF_CLASS_V` 11 have no value-pinning reader outside memfn.h (grep for `==`/`!=`/`<`/`,` against a number, `SITE_ABI..29|30`, `CLASS_V..10|11`, over src, cli, lib, memfn, tests, scripts, docs/spec, docs/design/memfn, tools, analyze: comments only). `memfn/include/CLAUDE.md` is updated. `PM_NPROOF`/`G2W_NPROOF` are gone (grep: 0 hits).
- **Raise, `[MF_WSPAN_POS]` arrays on the combined tree.** Grep over src, memfn, tests and docs/design/memfn: all 4 such arrays are `static` (`g2_pres_gen.c:502-503`, `run_decide_check.c:127-182`, plus the `run_g2_win.sh:271` plant's `static wf_pos pl[]`). No stack array is sized by it.
  - `wf_legacy` is respelled to `WF_LEGACY_POS` = `MF_MAX_TERM`. Its derivation holds by reading: `legacy_ok` caps the non-full positions at 32, and `run_bytes` refuses a full position before writing past it.
  - `d27_frame` takes `KPOS` 32 with `_Static_assert(KPOS <= MF_WSPAN_POS)`.
- **D-hors cap at 255** (raise). Holds by reading: the loop exits at t = 255 only after t = 1..254 were each found safe, so a shift of 255 is a shift below the least unsafe one. It is unchanged at windows of 255 or fewer. Its cost is O(256 x min(window, 255) x n) per prepare, and it is reached only from non-cover E-find; REPORT sites are excluded, and non-cover sites are 32 or fewer by construction.
- **Retired names on the combined tree.** No code reader of `MF_MAX_SPAN_POS`/`MF_MAX_AHEAD` remains (grep: memfn.h comments and S526 comments only). The combined tree builds.
  - S526's new shape: `form_checks.py` prints "PASS: C14 stride control"; the only other `MF_MAX_TERM` `_Static_assert` is `window.c:1837` (`MF_MAX_TERM - 1 <= INT8_MAX`, holds at 31); `SAB_FILE2`'s line is present.
  - The `SAB_BEFORE` lines of S1131, S3223, S526, S1083, S1224, S1018, S1148, S3086 and S3097 are all present in their files on the combined tree (grep -F, 9 rows).
- **Spans > 32 on combined `build/pcrec`.**
  - Covers at `[0-9a-f]{100}` (w=100), `a{4095}` (w=4095), `\b[0-9a-f]{1000}\b` (w=1000), a 42-byte literal (w=40) and `[0-9a-f]{2000}` (w=2000): all rc 0, `RX_DFA_SCAN "cover"`, with the Pattern header checked. 5 compiles, plus the 2 cases in READ-3 and 2 in its control.
  - Kit probe (READ-1): L=8 and 32 are clean, on 2 site kinds each.
- **The cover ask's storage.** `pcrec_memfn_rows(..., true)` passes `MF_MAX_FWD - MF_PROOF_LO` rows (ruled cover-ask-storage). Every other ask (7 call sites) passes `mf_rows_need`'s minimum (ruled caller-storage). Each ask gets its own storage, so the trace re-ask never aliases.

CRITIC COMPLETE
