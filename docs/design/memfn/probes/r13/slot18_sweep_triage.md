# slot18 emit_sweep triage (read-only; ref 9024449f vs r13 tip 2a44386a)

## Verdicts
- plain:    EXPECTED. rc=1 comes only from the `dumps` stream's `--list-axes` mover.
- start:    EXPECTED / pre-existing-on-main. rc=1 = the same list-axes mover plus 5 DIFFER_PINS floor lines that are identical on both sides.
- variants: EXPECTED. `VARIANTS: FAILED` = the same list-axes mover in each of the 5 cells (plain, lowsize, lowdfa, lowboth, lowthr).
- simd:     EXPECTED. 87 c-stream movers (44 default + 43 vm) are all vrun text; they reconcile with simd_floor's 44. rc=1 is again list-axes.
No R-13-CAUSED SIMD-off movers anywhere.

## Q1. plain / start / variants
- In every run (and every variant cell) exactly one stream has movers: `dumps`, population 7, movers=1 (`--list-axes`).
- The hunk adds 3 rows after `#name kind budget layer spelling doc` at line 194, all `memfn` axis rows with layer `simd`. The log's first-5 printout shows `vrun-w32` and `vrun-w16`. The task text says three rows, so I did not see the third in the log and did not check it.
- c-default, c-vm, emit-ir-vm, facts, emit-ir-auto (+ the -fno-prefilter / -fprefilter / -fno-prefilter-collapse variants), stderr and composition: movers=0 asymmetric=0 in all of the 7 runs (plain, start, plus the 5 variant cells).
- Tag floors are "all held" everywhere except simd (below).
- Self-checks PASSED. Variant plumbing witnesses are OK.
- `emit_sweep.py` returns rc=1 / `VARIANTS: FAILED` on any mover, so the list-axes mover alone explains every rc=1.

## Q2. start-sweep floor lines (DIFFER_PINS, scripts/emit_sweep.py:407)
Side a = ref (main 9024449f), side b = tree. The two sides are identical on every flagged arm, so none of these is caused by R-13.

| arm (base, flag, stream) | measured a/b | pin (differ, stamp) | flagged |
|---|---|---|---|
| byte -fno-run-prefilter, c-default | differ 127/127, stamp 127/127 | 132, 132 | DIFFER and STAMP floor, both sides |
| byte -fno-end-window, c-default | differ 272/272, stamp 272/272 | 288, 288 | DIFFER and STAMP floor, both sides; also `MANIFEST b'$' did not differ` (both sides False) |
| byte -fno-req-run, c-default | differ 553/553, stamp 296/296 | 530, 301 | STAMP floor only, 296 < 301, both sides |
| utf8 -fno-req-handoff, c-default | differ 275/275, stamp 275/275 | 280, 280 | DIFFER and STAMP floor, both sides |
| utf8 -fno-req-run, c-default | differ 608/608, stamp 294/294 | 572, 299 | STAMP floor only, 294 < 299, both sides |

- The brief named byte -fno-req-handoff. It is NOT flagged: 163/163 against a pin of 163. The flagged req-handoff arm is utf8.
- Last pin: all five pins were written in 26d2069f (stc0, 2026-10-06) and not touched since (`git log -S` for each tuple). The header says they were measured at main 4743ebb5 and in the ubuntubudu 2026-10-06 arms.tsv.
- Re-pin check: main's REVEND landing (7388f1c0 / 8416419f, 2026-10-10) re-derived the form-census floors, not DIFFER_PINS. `git log` shows no commit touching these pins after 26d2069f. Later commits to emit_sweep.py (the `be4b8dd2` and `0c5bb267` merges, `0cec4a15`, `736d4050`) touched trace floors, VARIANT_PINS and form-other, not DIFFER_PINS.
- Conclusion: the pins went stale on main (differ/stamp counts fell below, or rose above, them as emission changed since 10-06). The two sides being identical shows R-13 did not cause it. I did not bisect which main commit moved each count, and I found no earlier start-sweep log in memfn-slot to show when it first went red. A re-pin lane would need to measure these.
- Other arms: all remaining pins held, including the utf8 -fno-end-window ASSERT_ZERO 0/0 and the null arms 0/0.

## Q3. simd sweep (`--extra=-fmemfn-simd --no-differ-floor`)
Method: a driver (scratch s18tri/drv.py + an.py) imported emit_sweep's own `enumerate_corpus` and `compile_stream_c`. It re-ran the c-default and c-vm compiles over the 5616 rows with the slot's existing src_ref and src_tree binaries (no rebuild, no sweep re-run), for four combinations: ref and tree, each with and without `-fmemfn-simd`.
- Ref (main) accepts `-fmemfn-simd` as inert, so the ref ON text equals the ref OFF text for all 87 movers (0 exceptions). Tree OFF equals ref OFF for all 87. A sweep mover is therefore exactly "tree ON differs from tree OFF", which is simd_floor_check's definition.
- Result: 87 movers = 44 default + 43 vm, matching the log (the driver did not apply the sweep's both_ok filter; counts and ids agree). The id list is in s18tri/ids.txt (`engine<TAB>file<TAB>pattern`) and the raw artifacts are in s18tri/movers.pkl.
- Confinement, checked on all 87:
  - Deleted non-stamp lines: 0. The only deleted lines are the `_MEMFN_FORMS` and `_SIMD_GUARDED_BYTES` stamps.
  - `MEMFN_FORMS` goes from "none" to a string containing vrun; the observed token delta is exactly {vrun, w16, w32} in all 87. Example: `"vrun@w32+w16"`.
  - Inserted non-stamp bytes equal the new `SIMD_GUARDED_BYTES` exactly in all 87 (0 mismatches).
  - Inserted lines are the `#if defined(__x86_64__)... #include <emmintrin.h>/<immintrin.h>` blocks, the `<fn>__w16` and `<fn>__w32` functions, and the dispatcher `#if AVX2 -> __w32 / #elif SSE2 -> __w16 / #else` around the existing body return. I found no unclassified inserted line.
  - Every mover's pattern reaches a vrun site (FORMS names vrun).
  - Sampled diff: tests/assertions/d27/word_boundary.rxt `(?i)\bcat\b`, a `rx_reqrun` vrun pair.
- Reconciliation 44 + 43 against simd_floor's 44:
  - The sweep counts corpus ROWS (5616). Patterns repeat across .rxt files, mainly tests/litscan/reqcube.rxt (50 of the 87 mover rows) and handoff.rxt (20).
  - The 87 rows are only 21 distinct patterns: 20 movers at the default engine + 19 at vm = 39 distinct (pattern, engine) cells. `(?i)cat` alone is 6 rows per engine.
  - simd_floor_check dedupes patterns (`sorted({p...})`) and adds 5 NAMED witness cells: 39 + 5 = 44, which matches its `movers: 44 (pattern, engine) cells, 44 SIMD FUNCs` in make_test.log (line 5634; PASS at 5640 against floor 39).
  - So the log's "c-default movers == the simdfloor set" is true at the level of distinct (pattern, engine) cells but not as raw counts: 44 + 43 raw rows against 44 cells.
  - The coincidence 44 = 44 is just arithmetic: the 44 in the c-default stream is rows, whereas simd_floor's 44 is 39 distinct cells + 5 named. They are not the same set, and a reviewer reading "44 == 44" literally would be wrong.
- The `-fmemfn-simd ... MOVERS 20 / 19` arm lines (family `arms`, population 4527 distinct patterns, byte base only):
  - They are the arm "ref differ count / tree differ count versus the base arm". `differ=0/20` in c-default and `0/19` in c-vm: the flag moves 0 patterns on main (inert) and 20 (default) or 19 (vm) distinct patterns on the tree.
  - 20 and 19 match my distinct-pattern split exactly.
  - The `<-- MOVERS` marker is just the arm table flagging a nonzero tree-side count. There is no pin, because of `--no-differ-floor` ("an unpinned arm was WAIVED, not checked", the loud waiver in the log).
- `tag floors: NOT APPLIED (no VARIANT_PINS cell for this run)` appears five times in the simd log. This is the `--extra` run's expected waiver, not a failure.

## Q4. Other FAILED / floor / asymmetric lines
- None. asymmetric=0 on every stream of every run. The only "FAILED" text is `VARIANTS: FAILED` (list-axes) and the 5 start floor lines above. The simd run's NOT APPLIED / WAIVED lines are the documented waivers.
- Slot context (run.log, not part of the sweeps): build, strict, sabanchor, make test (NO_RED_LINES), N2 (floor_placeholder=2), G2 (0 failed) and mech (33 rows complete, 0 unexpected) are all clean.

## Files
- /home/pcrec/.claude/jobs/e99da2a5/tmp/s18tri/ids.txt (87 mover ids)
- /home/pcrec/.claude/jobs/e99da2a5/tmp/s18tri/drv.py, an.py, an2.py (drivers), movers.pkl
