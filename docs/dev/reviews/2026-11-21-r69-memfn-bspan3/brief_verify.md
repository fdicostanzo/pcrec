VERIFIER (sonnet): memfn-bspan3 (review r69). Read /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan3/COMMON.md FIRST: its
scope mandate, trees, kit and denylist bind you (you MAY read every critic findings file of this round:
seam/emit/pop/checks/ruling.findings.md in the round dir, and their lens dirs' tools/outputs, read only). You re-check
CONFIRMED findings yourself; never trust a critic's consequence claim. Re-derive each with the cheapest independent
method: quote the cited code/record lines (file:line at the build tree /home/pcrec/projects/pcrec/worktrees/crit-memfn-bspan3
or R/subject/), re-run the stated compile/grep yourself (write only under /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan3/verify/,
export TMPDIR there), and for answer/compile claims reuse the critic's tool from its lens dir if present, running it with
outputs into YOUR dir. Caps: 120 pcrec compiles, 150 gcc compiles. No make, no suites, no timing.
Write /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan3/verify.md INCREMENTALLY (it exists: APPEND only, never Write over it),
one section per item `## Vn (<finding ids>)`: verdict HOLDS / REFUTED / PARTLY (say which part) / not verified (why), the
exact calls you ran, observed facts. A REFUTED verdict quotes the exact call. End the file with a line `VERIFY COMPLETE`.
Items:
V1 SEAM-2: plan_of cannot compute skip; skip's inputs (w->hl, w->grp, stop_alone, the pick) are written after plan_of (wf_plan_site order, b_hors_prepare, find_groups, wf_find_prepare); plan_of memsets w (unset skip = 0).
V2 SEAM-3 (confirmed part only): wf_find_define walks no plan entries; stretches exist only as iteration state in wf_test_to.
V3 SEAM-4: kit_table rows need a ct accessor (kit.h), walk_row calls t->ct(i) and applies opt only when in->s is set (compose.c); wf_tables_check exists; trace_format.md names wfA/wfM/wfE.
V4 SEAM-5: fn_level_block writes exactly one function per block (head, render, close); mf_formdecl.render typed to fn_in; ofs_fn_fits / ofs_fn_fall and their vrun.c callers.
V5 SEAM-1: `[0-9a-f]{32}` with `--memfn=no-window-skip` traces fd R7w k 31; `[0-9a-f]{31}[0-9]` traces R7w, k 31 (kit/site.py).
V6 EMIT-1 + CHECK-2 (one item): at -O0, the hand-built V text at B 16 (`[0-9a-f]{17}` or `[0-9]{25}`) shows 0 ymm in rxa_search; at B 32 (k >= 32) ymm > 0. Reuse emit/tools/build_v.py or checks/tools/mkv.py.
V7 EMIT-2 + CHECK-2 control: dropping always_inline from __w32 makes `nm` at -O0 list the __w32 symbol; correct text lists no vs0 symbol at -O0.
V8 EMIT-3 + CHECK-3: simd_open/close (src/core/sb.c) write no text (byte accounting); the ISA region is a file-wide target pragma; C18's placement lint requires every body inside the region.
V9 EMIT-4: simd_floor_check.py HELPER regex `(\w+)__w(\d+)\(` cannot match `rxa_mf1_vs0__w32_b(` (python one-liner).
V10 EMIT-5 + CHECK-10: tests/memfn/routing_shape.py HEAD and FUNC_SUFFIXES do not match the §5 V selector head.
V11 POP-1: bench rows hex32.rx / hex32-id.rx / dig-exact-32 patterns in R/population/spancensus2_bench_own.tsv.
V12 POP-2 + CHECK-6 frame part + RULING-8(b): `[0-9a-f]{20}[g-z]{20}` at width 32 traces fd R7w, frame E-stmt; with the frame column removed from the rows the cell still reads absent (k 20/19 < 24); `[0-9a-f]{33}` at width 32 traces R7w E-stmt; the pin list is 11 patterns / 16 pattern-width cells.
V13 POP-3: under -e utf8 at width 32 `[a-f]{17}` / `[aeiou]{17}` trace R7w, `[^\n]{17}` E-stmt; at width 64 `[0-9]{64}` R7w k 63 and `[0-9]{65}` E-stmt.
V14 CHECK-1: a build-tree artifact's .c carries `    .abi = 109,` (and emit_dfa.c writes it), beyond the four spellings §10.2 lists.
V15 CHECK-4: the anchors of S2995, S3001, S3002, S724 (fn_level_block), S730 (fn_selector), S690, S694 (fn_call_line), S695 (fn_define) in ofsskip.c (kit/anchors_fn.txt; re-check by reading the rows' SAB_BEFORE); §10.2's re-aim list names none of them; §14 schedules REACH_ONLY at U1 and before delivery only.
V16 CHECK-5 (by reading): run_g2_win.sh's head passes run G2's generated sites (g2_win_gen.c) and never compile a pcrec pattern.
V17 CHECK-6 main: `ab[0-9]{26}` with `--memfn=no-fd-d1` at width 32 traces fd D1w k 26; no §10.2 pin cell uses --memfn=no-fd-d1.
V18 CHECK-7: hand two-level wrapper (checks/tools/wrapoff.py + census.sh, outputs to your dir) on `\b[0-9a-f]{32}\b` at -fno-memfn-simd leaves a `nopl 0x0(%rax,%rax,1)` line after removing exactly `nop`, `xchg %ax,%ax`, `data16 ... nopw`, `cs nopw` lines; the 32 non-movers' two arms are byte-identical C.
V19 CHECK-8: MFTRACE FDROUTE record carries no k field (one traced compile).
V20 CHECK-9: tests/axes/memfn_arm.py requires every `--list-axes` memfn row in MEMFN_CLASS; the note (§9.3, §10.1, §14) names no MEMFN_CLASS row.
V21 RULING-1, -2, -3, -6, -7, -8(a), -10 (quote claims, one section): check each quoted record line in R/subject/decisions.md / memfn_requests.md and R/r68's MANAGER RULING against the critic's text and the subject.
V22 SEAM-6 (SUSPECTED; settle the premise only): does pcrec emit offered tables as function-local statics (src/gen/emit_dfa.c emit_u8_table)? and does V's §5 signature take no table parameter? Do not hunt for a witness beyond 10 compiles.
