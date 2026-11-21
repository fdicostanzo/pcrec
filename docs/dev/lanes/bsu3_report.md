# Lane bsu3: R-47 unit U3, the vector span's `w32` level block

## STATE AT HANDOFF

STATE: delivered

U3 is built on branch lane/bsu3, cut from lane/memfn-k1108 at 2cdff1794 (U1, U2, U2b; abi 111; design note rev 4.2). The `w32` level block renders at `-fmemfn-simd=x86-64-v3` only; SIMD-off and `x86-64` bytes are U2's but the abi number.

Results (each with its section below):
- F2, run first: **82 of 82 routed cells MATCH** 710's timed `avx2-loop` machine code, 0 DIFFERS; 710's table, the §10.1 k source and the kit's own text each route 82 cells (F2 AND THE GUARDED BOUND).
- SIMD-off movers against the cut: **0**, no mask, every arm, both streams. SIMD-on movers: **28 (byte) / 20 (utf8) at c-default and 0 at c-vm** over the corpus, **31** for SPAN-SEED at width 4095, all at the `w32` layer, and they are exactly the V sites (IDENTITY GATE).
- C18 (`test-memfn-simdfloor`) reads U3's text green with the U3 amendment only (C18 HEAD FAMILY).
- Sabotage: new row S3515 (C18 control (1)); S730's V witness, owed since U2; S693 re-aimed. REACH_ONLY over every row (SABOTAGE AND REACH).
- The abi is 112 (rulings R-2), with every reader re-pinned (ABI EVENT).

Rulings file (docs/dev/lanes/bsu3_rulings.md): the last entry applied is R-2.
- R-1: abi 112, provisionally.
- R-2: 112 confirmed as the next number after the branch's (111 -> 112); the landing re-pins it by grep.

Commits (lane/bsu3):
- be192b04a: the U3 byte move with its abi event, the spec hunks and the check amendments.
- 33953d7c2: the pins (S3515, the S730 V witness, the C4 rows, the recursion-identity self-pin).
- 3f5d93969: the FILEPIN comment worded arch-free (C4 read red at 33953d7c2; SABOTAGE AND REACH).
- the report commit.

OWED: none of my own; no process of mine is running. The closing runs are box-queue jobs, queued as my last act (OWED RUNS): `724-kit-bsu3-test` (key kit-bsu3-test) and `725-kit-bsu3-mech` (key kit-bsu3-mech), ready after 724.

## THE JOB

Build unit U3 of docs/design/memfn/block_span.md rev 4.2, as its §14 U3 row and the sections it cites describe. The build go is D201 (Frank 2026-11-21, "build with simd layer"; add. 1, 2 (option A), 4 ("scalar-check-cut: yes") and 5 ("wrap-clang: a")); the design rounds r68, r69 and r71 cover U3.

Also mine, from review r75's PLAN items: SLOT-3 (a `define` column on wf_spanrows), SLOT-4 (one V head writer and one name function, before `__w32` adds the third head), CHECKS-8 (a committed reader of the V selector/`__body` text), and the S730 V witness owed since U2.

Not mine: U4 (G2-V, the T-table pins, the rest of C18, sabotage rows (a)-(f)), U5 (card C6), U6 (the G1 package). r75's SLOT-2 general form is not in my brief; its trigger (the next finder-row key another table reads) does not fire at U3, which adds no finder-row key.

Premise test. `grep -n 'span-vector' src/options.def` found no file: the option row lives at `memfn/src/options.def:138`, the kit's registry (memfn/CLAUDE.md, the options namespace). The brief's path is missing the `memfn/` prefix; the premise holds. `__body` is in memfn/src/window.c (the first hit is line 1914). No stop rule fired: the design matched the code and the brief, no SIMD-off byte moved, no answer moved, the §4.2 over-read argument held at both block widths, and C18 read U3 green with the U3 row's amendment alone.

## THE CHANGE

memfn/src/window.c (the kit):
- **The `w32` level block** (`vs_w32_block`, block_span.md §4.1). For a V stretch at a target admitting the 32-byte level (`art->levels` bit `LV_X86_W32`, design §3's fact), with a sink that offers the bracket, V's own writer brackets two functions with `simd_open(LV_X86_W32)` / `simd_close`:
  - `<p>_mf<h>_vs<j>__w32_b(p)`: the nibble-table test of B bytes. `lo_t` and `hi_t` are computed in C from the stretch's 32-byte set (`w->set[i]`) and written HIGHEST LANE FIRST (t[15] .. t[0], a value over 127 as its signed char), one copy at B = 16 and two at B = 32. At B = 16 the text is the xmm stream (`__m128i`, `_mm_`).
  - `<p>_mf<h>_vs<j>__w32(S, C)`: `p = S + C + LO`, then blocks of B while `i + B < K`, then the last block `p + (K - B)`.
  - B is 32 where K >= 32, else 16. **K < 16 is refused** by a `kit_fail` (a stated precondition, never a decline): §4.2 has no block width below 16.
- **The selector's replaced call.** `kit_selector` (the kit-wide writer, U2) gets the top helper `__w32` and level `LV_X86_W32`, so its one call line `    return <fn>__w32(S, C);` is bracketed; with no level it calls `__body`, as at U2.
- **The include bit on the art:** `art->includes |= kit_level(LV_X86_W32)->includes`, ofsskip's `fn_level_block` idiom; the window plan's class does not change (`MF_CLASS_V` unchanged).
- **The form token** `span-vector@w32` is appended to `art->forms` per rendered site (MEMFN_FORMS).
- **SLOT-3:** wf_spanrows gains a `define` column (`wf_span_v_define` on T-vwin/T-vscan, NULL elsewhere). The enumerator numbers a stretch `j` iff its row has a define, and `wf_find_define` calls the column. No function pointer is read as a row-kind tag any more (the two `render == wf_span_v` sites are gone).
- **SLOT-4:** one V head writer `vs_head(o, attrs, name, s, c)` (every V head: `__body`, the selector, `__w32`, and `__w32_b` with its one pointer parameter), and one name function `vs_name(rc, st, part, blk)` (the selector, `__body`, `__w32`, `__w32_b`). The level's stamp comes from `kit_level()->stamp`, levels.def's one spelling. The use (`wf_span_v`) and the define read the same name function.

Checks (each section below): C18's head family, `_b` name form and -O0 rule (tests/memfn/simd_floor_check.py); the V head lint with its planted control (CHECKS-8); `simd_bounds.tsv` row `span-vector-w32`; `simd_guarded_check.py` NAMED `vspan`, `simd-form-named` 8 -> 9; the identity gate's w32-layer shape (tests/memfn/span_vector_identity.py); mech rows S3515, S730 and S693.

Spec (D80), in the same commit as the byte move:
- `tuning.md` §2.43¶3a: what On renders gains the vector span.
- §2.43¶3b: its one switch is the `scalar` deny.
- §2.43¶3d: the "later unit, not built" parenthetical replaced.
- `registry.md` §6¶8a: the `span-vector` row, the same.
- `limits.md` §8.3¶3: the per-form bound, 1,700, in both the parts sentence and the caller's bounding list.
- §6¶8b's memfn floor is unchanged (15): U3 adds no option row.

No CLAUDE.md change: no file is added, removed or changes role (S3515 is a row in an existing directory).

## ABI EVENT

111 -> 112 in commit be192b04a, the same commit as the byte move (D76/D94, memfn/CLAUDE.md). Rulings R-1 and R-2: 112 is the next number after the branch's, and the landing re-pins it by grep to whatever is next on main.

The readers were found by `git grep -n -w 111 -- src tests docs/spec docs/testing.md memfn docs/dev/history/abi_changelog.md`, every hit reviewed by hand, unfiltered (block_span.md §9.2):
- `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`;
- `docs/spec/match_api.md` §1's K80 guard (its three lines), the §6 `abi` table row and §6¶17's sentence;
- `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT`, plus its failure message's bump history (the 111->112 clause appended);
- `tests/mech/sabotages/S693_abi_not_bumped.sh` `SAB_BEFORE` 112 / `SAB_AFTER` 111 (the cut's number), re-aimed;
- `docs/dev/history/abi_changelog.md`: the new entry, and the U2 entry turned to "was 111";
- `tests/codegen/run_recursion_identity.sh` FILEPIN, self-pinned to be192b04a, the lane's last src commit (commit 33953d7c2). ABASEPIN is unchanged.

Every other hit is not an abi reader: PCRE2 error 111, row and line numbers, timings and counts, and the memfn journal/responses/wake history. `git grep v111` finds no `_v<N>` symbol spelling (one `.rxt` subject's variable name only).

MF_SITE_ABI and MF_CLASS_V are unchanged: the site carries no new field, and the level's include bit rides the art.

## IDENTITY GATE

All runs were under `scripts/boxlock run`, gnutimeout-bounded. Logs are in $PCREC_TMPDIR/scratch/bsu3/: idA*.log, idB2.log, heavy*.log.

**(1) SIMD-off identity, raw bytes, NO mask** (`scripts/emit_sweep.py`):
- Reference: the cut 2cdff1794 (`scratch/bsu3/base`). Subject: the U3 code with the abi held at 111 (`scratch/bsu3/preabi`).
- So any byte that moves here is a code move, not the number.
- Streams c-default and c-vm, every arm, corpus population 7,274 (byte) per stream.

| arm | c-default movers | c-vm movers |
|---|---|---|
| off_byte (no flag) | **0** | **0** |
| off_utf8 (`-e utf8`) | **0** | **0** |
| x86-64 byte / utf8 (the scalar SIMD layer) | **0 / 0** | **0 / 0** |
| span-loop force / no-span-loop deny | **0 / 0** | **0 / 0** |
| x86-64-v3 + `--memfn=no-span-vector` | **0** | **0** |
| SPAN-SEED (41) at width 4095: off / x86-64 / force / deny | **0** each | **0** each |
| **x86-64-v3 byte** | **28** | 0 |
| **x86-64-v3 utf8** | **20** | 0 |
| **SPAN-SEED at width 4095, x86-64-v3** | **31** | 0 |

- SIMD-off movers are **0**.
- SIMD-on movers sit at one layer only, the 32-byte one (`-fmemfn-simd=x86-64-v3`).
- The VM stream has no window walk, so it never moves.
- The utf8 arms were re-run separately (idA2.sh), because the first loop's `eval` split `-e utf8`; those first runs printed a usage error and measured nothing.

**(2) The deny/V-site gate** (`tests/memfn/span_vector_identity.py`, §10.2 G-4, now with U3's w32-layer shape):
- Reference: its declared reference, the build BEFORE the vector span (0481a4130, abi 109; lane bsu2's merge base). Subject: `build/pcrec` at abi 112.
- **PASS**: 62,841 compiles, 0 failures.
- `deny_differs=0` in every cell: `--memfn=no-span-vector` matches the pre-V artifact after M1-M9, at the SIMD-off, x86-64 and x86-64-v3 layers.
- `mover_not_vsite=0` and `floor_fail=0`: every default mover is a V site, at 28 (byte) / 20 (utf8) / 31 (seed at 4095) per c-default cell.
- At x86-64-v3 every mover's added text is exactly what the gate admits at a level:
  - the kinds `__body`, selector, `__w32`, `__w32_b`;
  - at most one include line;
  - one `span-vector@w32` token per site in MEMFN_FORMS;
  - every selector calling `__w32`.
- A first run against the cut (idB.log) failed by construction, not by a fault: the cut already carries U2's deny. Against the cut's default the deny differs in exactly the V sites (28/20, all `mover_not_vsite`). That run is not the gate's reference.

**Answers:** the probe in F2 AND THE GUARDED BOUND (3,064 subjects, 0 differ). G2-V, the committed answer leg, is U4's. The G2 window family (`memfn/tests/run_g2_win.sh`) is green: 27,376 checks passed, 0 failed.

## F2 AND THE GUARDED BOUND

**F2 was the first check run on the built text**, before the identity gate and the rest (block_span.md §6; §14 U3 "F2 recorded before anything else"). It is a delivery check, run once and recorded here; it is not committed.
- Script: $PCREC_TMPDIR/scratch/bsu3/f2.py. Log: $PCREC_TMPDIR/scratch/bsu3/f2_record.log. It ran under `scripts/boxlock run --label bsu3-f2`.
- **Population: 710's grid**, 10 classes x 13 k = 130 cells (`confirm.py` CLASSES, KS_OLD + KS_NEW), pattern `cls{k+1}` at `--window-search-width=4095`.
- **The routed set, counted three ways:**
  - (A) 710's own table (TABLE + SITE_EXPECT): 82;
  - (B) §10.1's k source on the SHIPPED build, applied in the script: the finder row from a `-DMF_TRACE` harness's `MFTRACE FDROUTE` record (the `mk_mftrace_lib.sh` library), k from `pcrec-harness --harness=span-head=0`'s loop text (END - LO), and the predicate D-hors 16..1000 / R7w 24..64 on frame E-find: 82;
  - (C) the kit's own answer, the `__w32(` call in the shipped x86-64-v3 artifact: 82.
  - **No cell disagrees** across the three.
- **Fidelity:** for each routed cell, `gcc -std=gnu11 -O2 -c` of the shipped `-fmemfn-simd=x86-64-v3` artifact and of 710's `work/src/<cell>.avx2-loop.c` (the same gcc 15.2.0 and flags), then `objdump -d` of `rxa_search` with addresses and symbol offsets normalized. **82 MATCH, 0 DIFFERS.** So the landing rule ("any DIFFERS blocks the landing") is not triggered, and C6's population gains no cell from F2.

**The guarded bound** (block_span.md §5, §12): `tests/memfn/simd_bounds.tsv` row `span-vector-w32` **1700**, CHOSEN, UNMEASURED DEFAULT, a bound by construction.
- V renders at most once per site and has no decline path. The bracket is one site's level block plus the selector's call line, and its text is fixed per (B, set) apart from its numbers.
- So the worst case is the largest instance with every varying part at its longest: both nibble tables at 32 lanes of `-128`, a ten-digit site handle in each of the 11 names (the handle is a `uint32_t`, and the kit caps no site count), the offset ` + 4095`, and k 1000. That gives 1,605 bytes, rounded up to 1,700.
- Measured instances (the bracket's bytes, read off the emitted text): 1,315 at B = 32 (`[0-9a-f]{41}` at 4095) and 1,102 at B = 16 (`[0-9a-f]{17}`).
- The stamp counts at pcrec's two-byte placeholder prefix (limits.md §8.2¶1): `-p rx` and `-p rxa` both stamp 0x6cc on `[0-9a-f]{17}`.
- The bound has a reader that is not the every-10th sample: `simd_guarded_check.py` NAMED gains `vspan` (`[0-9a-f]{17}`), and `simd-form-named` is re-pinned 8 -> 9 (vspan renders at the 32-byte target only). `limits.md` §8.3¶3 names the bound.
- The kit states no `guarded_max` for V: it is no `mf_formdecl` row and no fit test reads it (design §5: a fixed bound, not a cap), so the kit-pin leg (vrun.c's declarations) has nothing to pin.

**The over-read argument (§4.2) at the boundaries**, checked on the emitted text:
- At K = B (k 16, `[0-9a-f]{17}`) the loop guard `i + 16 < 16` never holds, and the one block reads `p + (16 - 16)`.
- At K = 40 (B 32) one trip reads [p, p + 32), and the last block reads [p + 8, p + 40).
- No read leaves [p, p + K). K < 16 is refused by the renderer.

A sanity probe, not G2-V (which is U4's): $PCREC_TMPDIR/scratch/bsu3/probe_ans.py.
- 21 patterns (18 of them V sites at x86-64-v3, the rung edges 16/31/32/33/63/64/1000 included, plus `\w{501}`, `[aeiou]{40}` and the D1/PAIR/literal-bracketed controls) x (40 random subjects + a failing-index staircase at every position).
- ON vs OFF vs python `re`: **3,064 subjects, 0 differ**.

## C18 HEAD FAMILY

tests/memfn/simd_floor_check.py, the U3 part of the C18 amendment (block_span.md §10.2 [R71-4]). NAMED, the floors, the routing leg and controls (2)-(4) stay U4's.
- **The head family:** `SELECTOR` and `HELPER` accept `static inline`, then an optional `__attribute__((...))` naming `always_inline` and/or `unused`, then `size_t` or `int`. SELECTOR now uses named groups (`attr`, `fn`, `callee`, `vw`).
- **The name form [R-10]:** `HELPER` is `(\w+)__w(\d+)(?:_b)?\(`, so `__w32_b` IS a helper for the exclusivity lint. Drilled: both `__w32_b` and `__w32` are found on each witness.
- **The -O0 rule [R-7, R-8]** (`o0_inline_issues`): for a selector whose OWN head says `always_inline`, in the -O0 object, at every C9 cell:
  - (1) no symbol of its family (`<fn>`, `<fn>__*`) is defined (`nm`, `t` or `T`);
  - (2) every function calling it (found in the TEXT: the nearest column-0 definition line above the call) holds a `pshufb` or `vpshufb`.
  - A selector with ofsskip's head keeps today's `nm` leg.
- **Control (1)** (drop always_inline from `__w32`) is mech row S3515 (SABOTAGE AND REACH). Hand-drilled on the three §16 item 10 witnesses (`[0-9a-f]{17}`, `[0-9]{25}`, `[0-9a-f]{41}` at 4095): the clean text gives no -O0 issue; the plant gives both legs red ("its family defines rx_mf1_vs0__w32" and "rx_search ... holds no pshufb").
- **CHECKS-8** (review r75): a committed reader of the V function TEXT. A **V head lint** in text_legs reads every function named `<p>_mf<h>_vs<j>[__part]` and requires its declared head: `__attribute__((always_inline)) int`, and `(always_inline, unused)` on `__body`.
  - One planted control (`V_PLANTS`: `__body`'s always_inline dropped) runs on a target's first clean V mover, and must be rejected by `V head`.
  - `V_CONTROL_TARGETS = ('x86-64-v3',)` requires such a mover to exist there (K35).
  - Drilled: the clean text passes; the plant is rejected.
  - The rest of CHECKS-8 is U4's: the T-table pins count the selector and `__w32` CALLS, and the routing leg reads the V head family with its forwarded arguments.
- **Result:** `make test-memfn-simdfloor` **green**: 22,767 checks passed, 0 failed, with the U3 amendment alone.
  - x86-64-v3: movers 102, selectors per level w32=102.
  - The named witnesses and floors (55, 55, {'w32': 55}) hold. The floors are not re-pinned; that is U4's, at the measure.
  - The V head control is rejected by `V head`.

## SABOTAGE AND REACH

- **S3515** (new; `memfn/src/window.c`; suite `simdfloor`): `__w32`'s head written with `unused` in place of `always_inline`. This is C18 control (1).
  - REACH: `[0-9a-f]{17}` at `-fmemfn-simd=x86-64-v3`, expecting the clean `__w32` head. REACHED.
  - Its C4 rows (classes 1 and 6) are in c4_allowlist.tsv; its prose is worded arch-free.
- **S730** (re-aimed at U2): gains the V witness owed since U2, a second REACH compile expecting `    return rx_mf1_vs0__w32(rx_mf1_s, rx_mf1_c);`. REACHED 2 of 2.
- **S693**: re-aimed to 112 / 111.
- **REACH_ONLY over every row** at 33953d7c2: 1,372 rows; 666 reached, 682 no-probe, 16 declared unreached, 8 unreached.
  - **Six of the 8 were mine** (S518-S523, the C4 rows). The FILEPIN comment I added in 33953d7c2 named the SIMD target token, so C4 read red there.
  - Fixed in 3f5d93969 (reworded arch-free). Re-probed at 3f5d93969: those six reach, and `run_arch_blind.sh` reads 32 passed, 0 failed.
  - **The other two (S1760, S1761, rxt_source.c) are pre-existing**, already filed as [PIN-MSG-DEPTH]: the expected phrase follows an absolute fixture path in a fixed-size message, so deep scratch paths truncate it (memfn/docs/responses.md, memfn/docs/journal.md 11-10). U3 does not touch them.
- **DETECTION is owed**: S3515, S730, S693 plus the 11 other rows the two amended suites detect, in job 725 (OWED RUNS). The lane ran REACH only.
- All 49 window.c rows' anchors still match the source text.

## OWED RUNS

Queued as my last act, after this commit (`scripts/boxqueue add`). Both are non-timing, estimated about 40 + 50 min, and end hours before 00:45 (the 01:00-07:00 timing window is main's).

- **724-kit-bsu3-test**: `make -j16` then `make test` via `scripts/perfrun` on lane/bsu3. Log: $PCREC_TMPDIR/scratch/bsu3/maketest.log; the verdict is make's error lines.
- **725-kit-bsu3-mech**: DETECTION of S3515 S730 S693 S1852 S3170 S3198 S699 S700 S701 S702 S703 S723 S724 S728 (14 rows), ready after 724 is green.

**The deliver file's `owed:` line reads `none`.** The brief says to set it to my keys, and BOILERPLATE says a lane never edits the deliver file. I did not edit it. The keys are here and in STATE AT HANDOFF; the manager may correct the line.

Already run in-lane, all green:
- `nice make -j2`, `make strict`;
- `run_arch_blind.sh` (32/0);
- the sections test-codegen, test-registry, test-memfn-rows, -finder, -g2, -guarded, -simdfloor, -arms, -link, -targets, test-rxtsource, test-startset, test-compound, test-partlayout, test-cpset-structure, test-recursion-identity (0 make errors);
- the G2 window family;
- the identity runs;
- F2.
