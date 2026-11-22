# bsu2 — R-47 units U2 and U2b of docs/design/memfn/block_span.md rev 4.1 (lane bsu2, opus, 2026-11-21)

## STATE AT HANDOFF

U2 is built on branch lane/bsu2 (merge base 0481a4130, lane/memfn-k1108). U2b's census is GREEN. Nothing of U3 is in the branch: no w32 level block, no immintrin text. The V selector renders `__body` only.

The abi is **111** (109 -> 111, rulings R-1: L3 holds 110 on its branch; whichever of L3/U2 lands second re-pins to the next number at its landing, by `git grep -n -w` of the current number, unfiltered).

Green in the lane:
- `nice make -j2`, `make strict` (clean after every commit), `make test-codegen` (in the sections run).
- The identity gates, in two parts:
  - commit A (the zero-mover refactor) shows 0 movers against the merge base in all 10 arms x 2 streams, with no mask;
  - U2's deny arm shows 0 differences after the declared mask, and the default arm's movers are exactly the V sites (IDENTITY GATE).
- U2b's census: GREEN (U2B CENSUS).
- The G2 window family: 27376 passed, 0 failed.
- These 14 sections ran at make rc=0: test-codegen, test-registry, test-memfn-rows, test-memfn-finder, test-memfn-g2, test-memfn-guarded, test-memfn-simdfloor, test-memfn-arms, test-memfn-link, test-rxtsource, test-startset, test-compound, test-partlayout, test-cpset-structure.
- `make test-recursion-identity` passes 15/15 with FILEPIN self-pinned to c51fb2d36. ABASEPIN is unchanged, because (A) shows 0 differing on every axis.
- The new pins in check mode:
  - `memfn_arm.py --subset` over the six span cells: 121 passed, 0 failed;
  - `emit_sweep --extra=--memfn=no-span-vector` at byte and utf8 is rc=0 at the new floors.
- REACH_ONLY over every row (1370 rows): 671 reached, 2 unreached. The 2 are S1760 and S1761. They were red before this lane, the file they plant in is untouched here, and the cause is not established (see SABOTAGE AND REACH).

OWED: none of my own; no process of mine is running. The closing runs are box-queue jobs, queued as my last act (OWED RUNS): `717-kit-bsu2-test` (key kit-bsu2-test) and `718-kit-bsu2-mech` (key kit-bsu2-mech).

Rulings file (docs/dev/lanes/bsu2_rulings.md): the last entry applied is R-3.
- R-1: abi 111.
- R-2: the closing jobs must end before 01:00. They are queued well before it, with caps of 3600 s and 9000 s.
- R-3: no cloudrun or gh call; the box queue is used.

Commits (lane/bsu2):
- d4b25d950: WIP, zero movers.
  - SLOT-1/2/7: the stretch record stores its row, and renders from it; b_hors_prepare stores the probed index.
  - The per-stretch trace tag.
  - `kit_selector`, lifted from fn_selector.
  - `fd_brow_is`.
  - Re-aims of S689, S730 and S3280.
- c51fb2d36: the U2 byte move.
  - T-vwin and T-vscan.
  - vs<j> + `__body` + the selector.
  - The `span-vector` deny row.
  - The abi move 109 -> 111 with every reader, and the spec hunks (registry.md, tuning.md, match_api.md).
- 3b78e6a47: `tests/memfn/span_vector_identity.py`, the identity gate, with its CLAUDE.md and NOTES.md lines.
- d38be7b59: the pins.
  - MEMFN_CLASS rows for span-vector, plus span-loop re-measured.
  - emit_sweep DIFFER_PINS rows for the deny arm.
  - The recursion-identity FILEPIN self-pin.
  - The S730 REACH witness.
- The report commit.

## THE JOB

The brief: build U2 and U2b exactly as §14's rows say.
- U2:
  - T-vwin, and T-vscan keyed on R7w.
  - The wrapper at every layer, through ONE lifted selector writer, with ofsskip's bytes unchanged.
  - The deny row `span-vector`, live at both layers, with its MEMFN_CLASS row and its corpus floors measured and pinned.
  - span-loop's re-measured rows.
  - The deny arm's identity gate against the merge base, with the declared M1-M9 mask.
  - The U2 re-aims and REACH_ONLY.
  - The first abi event, in the same commit as the byte move.
  - r72's SLOT-1, SLOT-2 and SLOT-7.
- U2b: the machine-code census on the built text. No timing, and no T-keep.
- Stop if:
  - a real bench site DIFFERS;
  - `\w{20}` does not DIFFER;
  - the deny gate shows a mover outside the mask;
  - any answer changes.

Premise test: the design and the brief agree. Option A (D201 add. 2) wraps at every layer, and "scalar-check-cut: yes" (D201 add. 4) replaces the scalar timing with U2b. No stop rule fired.

## THE CHANGE

The zero-mover commit (d4b25d950) changes no artifact byte; its identity gate is below. It contains:
- **The stretch record** `wf_stretch {i, k, row, h, j}`.
  - The enumerator `wf_stretches` stores each stretch's chosen span-form row (SLOT-7), its head and its V index.
  - `wf_test_to` dispatches through `wf_spanrows[row].render`, so the walk renders from the stored k (SLOT-1).
  - `wf_loop_len` lost its head parameter: it is the enumerator's alone.
- **`b_hors_prepare` stores the probed index** in `w->hix` (SLOT-2). `d_hors_head` and `hors_skip` read it, so S3500's anchor is unchanged.
- **The per-stretch trace tag** `at=I k=K` on the wfS gate lines (gate_tctx gains `tag`), with a memfn/docs/trace_format.md hunk.
  - Adding the field means appending `, NULL` to the 12 gate_tctx initializers (gcc's -Wmissing-field-initializers).
  - S689's anchor moved with it.
- **`kit_selector`** (ofsskip.c, kit.h) is the ONE selector writer. fn_selector is a thin call of it, through head/call callbacks; ofsskip's bytes are unchanged.
- **`fd_brow_is(brow, FD_NAMED_DHORS | FD_NAMED_R7W)`** (finder.c): finder row identity by pointer. Only finder.c spells the ids (SEAM-7).

The byte move (c51fb2d36):
- **The span form table** has six rows: T-deny, T-force, T-lever, **T-vwin** (brow D-hors, 16 <= k <= 1000), **T-vscan** (brow R7w, 24 <= k <= 64), T-head.
  - Each V row requires an unbracketed stretch (`s_v_ok`) and carries opt `span-vector`, so the deny skips it in `walk_row`. Its contracts are ct_s_vwin and ct_s_vscan.
  - `wf_tables_check` also checks the new `render` column.
- **V's rendering:**
  - The walk calls `<p>_mf<h>_vs<j>(S, C)`.
  - `wf_find_define` defines each V stretch's `__body` (always_inline, unused): the T-head text the deny renders inline (`wf_span_h`).
  - Its selector (always_inline) is written by `kit_selector` with no rung, so it is `return <fn>__body(S, C);` at every layer at U2.
- **options.def** gains `span-vector` (MF_OPT_DENY, any build, scalar layer), so the deny is live at SIMD-off too.
- **Spec:** registry.md gains a span-vector row, the span-loop row is amended, and ¶8b's floor goes 14 -> 15. tuning.md §2.43 ¶3d gains a VECTOR SPAN paragraph. match_api.md is covered under ABI EVENT.

Then the pins (d38be7b59):
- **MEMFN_CLASS** (tests/axes/memfn_arm.py):
  - `span-vector` is DIFFER at both layers: 28 byte / 20 utf8 on c-default, 0 on c-vm. Its witnesses are the three bench texts, byte and utf8, on c-default.
  - The `span-loop` deny moves ASSERT_ZERO -> DIFFER 28 / 20 / 0. At a V site it is T-deny's all-inline text, while the default is the wrapper.
  - The `span-loop=force` floors rise from 14 to 50 byte / 44 utf8.
  - All were measured by `--measure` at c51fb2d36 (5700 patterns, both layers identical) and pinned at the measure.
- **emit_sweep DIFFER_PINS:**
  - The deny arm `--memfn=no-span-vector` is pinned at 28 / 20 on c-default, with manifest `[0-9]{25}`.
  - c-vm is in ASSERT_ZERO.
  - The SIMD layer's floors live in memfn_arm.py.

## ABI EVENT

The number moved 109 -> 111, per R-1. The readers were found by `git grep -n -w 109`, unfiltered, and every one was moved in c51fb2d36, the commit of the byte move:
- `src/gen/emit_dfa.c`: `PCREC_ARTIFACT_ABI 111`;
- `docs/spec/match_api.md`: the K80 guard's three lines, the §6 table row and §6 ¶17;
- `tests/codegen/run_codegen_tests.sh`: `ABI_EXPECT=111`, with its message;
- `tests/mech/sabotages/S693_abi_not_bumped.sh`: SAB_BEFORE 111 / AFTER 109, with a re-aim note;
- `docs/dev/history/abi_changelog.md`: a new 111 entry; the 109 entry now reads "was".

The other `109` hits are not abi readers: PCRE2 error 109 in parser comments, and the timings in limits.h.

The readers that never cite the number were then run: registry, codegen and rxtsource (green), and the recursion identity gate. (B) moved because the abi spellings move, so FILEPIN was self-pinned to c51fb2d36, the lane's last src commit, and the landing re-pins it to the landing merge. (A) shows 0 differing, so ABASEPIN stays b2d73b6b1.

The stamps: `MEMFN_FORMS` gains nothing at U2. Its `span-vector@w32` token, the `simd_bounds.tsv` row and the SIMD_GUARDED_BYTES rise are all U3's (§9.3), since no SIMD form renders at U2.

## IDENTITY GATE

**Commit A (the refactor), no mask:**
- Command: `scripts/emit_sweep.py --ref-bin <merge-base build> --bin <d4b25d950 build> --streams c-default,c-vm`.
- 10 arms: off, v3, force and deny at byte; off and v3 at utf8; seed4095 under off, v3, force and deny.
- Each arm shows **movers=0, asymmetric=0** on both streams:
  - corpus 7274 argv, with 6700-6801 reached per cell;
  - SPAN-SEED's 41 patterns at width 4095.
- Logs: $PCREC_TMPDIR/scratch/bsu2/idA_*.log.

**U2's deny arm, masked** (`tests/memfn/span_vector_identity.py`, committed):
- The artifact of the U2 binary under `--memfn=no-span-vector` is compared to the merge-base binary's artifact with no deny, after the nine anchored abi spellings M1-M9 and nothing else. The support_id hash is outside the mask; no population reaches it.
- Population:
  - 5683 distinct corpus patterns x {SIMD off, x86-64-v3} x {byte, utf8} x {c-default, c-vm};
  - SPAN-SEED's 41 patterns at width 4095 x both layers.
- Result: 41894 compiled, **deny_differs=0 in every cell, mover_not_vsite=0 in every cell. PASS.**
- The default arm's movers, which equal the V-call artifacts exactly:

| cell | c-default | c-vm |
|---|---|---|
| byte, both layers | 28 | 0 |
| utf8, both layers | 20 | 0 |
| seed4095, both layers | 31 | n/a |

No mover appears outside the declared mask, and no stop fired. Log: scratch/bsu2/idB.log.

The command:

    python3 -I -B tests/memfn/span_vector_identity.py --ref-bin <merge-base build>/pcrec --bin build/pcrec --jobs 8

## U2B CENSUS

The script is `$PCREC_TMPDIR/scratch/bsu2/u2b_census.py`, a delivery step that is not committed (§2.1). Its command:

    python3 -I -B u2b_census.py build/pcrec OUTDIR

Method:
- One U2 binary renders two arms per pattern: the default (wrapped) and `--memfn=no-span-vector`. Both use `-fno-memfn-simd`, `--features all` and the same `-o` basename (`<dir>/<arm>/rxa.c`).
- Each arm is compiled with `gcc -O2 -c`, then disassembled with `objdump -d --no-show-raw-insn --disassemble=rxa_search`.
- **The normalizer, declared before data:**
  - strip the address prefix;
  - replace each `<hex> <sym+off>` operand with one token;
  - collapse whitespace;
  - drop padding lines matching `^((data16|cs) +)*(nop[wlq]?( .*)?|xchg +%ax,%ax)$`.
- **Diff tool:** python3 `difflib.ndiff`. The count is the lines added plus the lines removed.

Results:
- **The real population is IDENTICAL:**

| site | width 32 | width 4095 |
|---|---|---|
| `[0-9a-f]{32}` | raw 0 / normalized 0 | raw 0 / normalized 0 |
| `\b[0-9a-f]{32}\b` | raw 3 / normalized 0 | raw 3 / normalized 0 |
| `\d{32}` | raw 0 / normalized 0 | raw 0 / normalized 0 |

- **The grid** (710's ten classes x `cls{17}`..`cls{32}` at width 32):
  - 160 compiled: 128 eligible and 32 non-movers. All 32 non-movers have byte-identical C.
  - Of the 128 eligible: **80 IDENTICAL, 48 DIFFERS**. DIFFERS list:
    - `\w{17}`..`\w{32}`: all 16, normalized 22 each;
    - `[aeiou]{17}`..`[aeiou]{32}`: all 16, normalized 38 at k 16-23 and 50 at k 24-31;
    - `[A-Za-z0-9_-]{17}`..`{32}`: all 16, normalized 2 each.
  - hex, dig, nonl, hi, af, upper and num are IDENTICAL at every k.
- **`\w{501}` @4095:** DIFFERS, normalized 2.
- **Controls:**
  - Positive control: `\b[0-9a-f]{32}\b` goes from raw 3 to normalized 0 at both widths, so the normalizer removes padding.
  - Negative control and known positives: `\w{20}` DIFFERS (22) and `\w{501}` DIFFERS.
  - The counts match §2.1: 128 eligible and 32 non-movers.
- **Verdict: GREEN.** No real site DIFFERS, and `\w{20}` does DIFFER.

Log: scratch/bsu2/u2b.log. No timing ran, and there is no T-keep (D201 add. 4).

## SABOTAGE AND REACH

The re-aims, by the anchor map over every function U2 moves (§10.2 "At U2"). The row field validation (VALIDATE_ONLY) passed for all 19 touched rows. Every row whose SAB_FILE is a file this lane edits has its anchor exactly once (331 rows). The two count-2 anchors, S283 and S284, declare `SAB_COUNT=2` and are unchanged from the base.
- **S730** is re-aimed onto `kit_selector`'s `simd_open` / call / `simd_close` lines.
  - It gains a REACH witness: `(?i)cat` at `-fmemfn-simd=x86-64-v3`, expecting `    return rx_mf1_ofsskip__w32(subject, n, pos);`. It is REACHED.
  - The design's "V witness" for S730 is NOT added at U2. The V selector shares the writer but has no rung at U2 (`__body` only, top NULL), so the plant cannot reach it until U3's `__w32`. That witness is owed to U3.
- **S689**: the anchors gained `, NULL };` (the gate_tctx field). REACHED.
- **S3280** is re-aimed onto `wf_span_h`'s `while (a < end && w->off[a] < st->h) a++;` with `<=`. REACHED.
- **S693**: abi 111 / 109. REACHED.
- **S690, S694** are unchanged (`fn_call_line`), now reached through the writer's call callback. Both REACHED.
- Unchanged and not moved, by R-4: S724, S2995, S3001, S3002, S687, S691, S692, S695 and S728.
- The window.c rows S3276-S3285, S2982, S3500 and S3501 keep their anchors.

**REACH_ONLY=1, every row:** 1370 rows: 671 reached, 2 unreached, 16 declared-unreached, 0 now-reached, 681 with no probe (log scratch/bsu2/reach.log).
- The 2 unreached rows are **S1760 and S1761** (src/parse/rxt_source.c, the include-pin chain).
- This lane does not touch that file or tests/code/.
- Run by hand in the worktree, their probes print the expected text with both the merge-base binary and the U2 binary.
- They are a known red that predates this lane: r30btri_report.md, item 5, "the S1760/S1761 cause is NOT established".

**New plants:** none. The §14 U2 row asks for the re-aims and REACH_ONLY. Of §10.2's plants, (a) and (b) need U3's vector code; (c)-(f) are caught by the T-table pins and G2-V checks, which no unit before U4 builds. The brief's ids S3505-S3519 are unused.

**Detection** of the moved and re-proved rows is owed as job `718-kit-bsu2-mech` (OWED RUNS).

## OWED RUNS

Queued as box-queue jobs, my last act. They must end before 01:00 (R-2), with caps of 3600 s and 9000 s behind main's two 1800-s nightprep jobs.
- **`717-kit-bsu2-test`** (key kit-bsu2-test): `make -j16` then `make test` via `scripts/perfrun --label bsu2`. Log: /var/tmp/pcrec-pcrec/scratch/bsu2/maketest.log; the verdict is in make's `*** [...test-X] Error` lines.
- **`718-kit-bsu2-mech`** (key kit-bsu2-mech), after kit-bsu2-test: detection of 18 rows.
  - The moved and re-proved rows: S730 S689 S3280 S693 S690 S694.
  - The window.c span rows whose path U2 changed: S3276-S3279, S3281-S3285, S2982, S3500, S3501.
  - Its expected last line: `== mech run COMPLETE: 18 rows (unexpected: 0, undetected: 0, unreached: 0, ...)`.

For the landing:
- the abi re-pin if L3 lands first (R-1);
- FILEPIN re-pinned to the landing merge;
- the S730 V witness at U3.
